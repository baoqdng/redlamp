import os
import sys
import glob
import re
import csv
import time
import argparse
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional

import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

from sklearn.ensemble import IsolationForest
import xgboost as xgb

try:
    from vus.metrics import get_metrics
except ImportError:
    get_metrics = None

import utils
import datautils

# Re-use convolution smoothing and min-max normalization from RedLamp
def convolve_minmax_score(score: np.ndarray, w: int = 50, minmax: bool = True) -> np.ndarray:
    """Convolve score with moving average kernel and normalize to [0, 1]."""
    score = np.asarray(score, dtype=float)
    if score.ndim == 1:
        score = score.reshape(-1, 1)
    
    b = np.ones((w, 1)) / max(w, 1)
    smoothed = np.apply_along_axis(lambda m: np.convolve(m, b[:, 0], mode='same'), axis=0, arr=score)
    
    if minmax:
        min_v = smoothed.min(axis=0, keepdims=True)
        max_v = smoothed.max(axis=0, keepdims=True)
        denom = max_v - min_v
        denom[denom == 0] = 1e-8
        smoothed = (smoothed - min_v) / denom
    return smoothed.squeeze()


def sliding_window_view(arr: np.ndarray, window_size: int, step: int = 1) -> np.ndarray:
    """
    Extract sliding windows from 2D array of shape (features, time).
    Returns shape: (num_windows, window_size, features).
    """
    n_features, n_time = arr.shape
    if n_time < window_size:
        pad_len = window_size - n_time
        arr = np.pad(arr, ((0, 0), (pad_len, 0)), mode='edge')
        n_time = window_size
        
    num_windows = (n_time - window_size) // step + 1
    windows = np.zeros((num_windows, window_size, n_features), dtype=np.float32)
    for i in range(num_windows):
        start = i * step
        windows[i] = arr[:, start:start + window_size].T
    return windows


# =========================================================================
# 1. Isolation Forest Detector
# =========================================================================
class IsolationForestDetector:
    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model = IsolationForest(
            n_estimators=self.n_estimators,
            contamination='auto',
            random_state=self.random_state,
            n_jobs=-1
        )

    def fit(self, X_train: np.ndarray):
        N, W, D = X_train.shape
        X_flat = X_train.reshape(N, W * D)
        if N > 10000:
            indices = np.linspace(0, N - 1, 10000, dtype=int)
            X_flat = X_flat[indices]
        self.model.fit(X_flat)
        return self

    def predict_anomaly_score(self, X_test: np.ndarray, window_size: int) -> np.ndarray:
        N, W, D = X_test.shape
        X_flat = X_test.reshape(N, W * D)
        batch_size = 10000
        scores = []
        for i in range(0, N, batch_size):
            chunk = X_flat[i:i + batch_size]
            s = -self.model.score_samples(chunk)
            scores.append(s)
        raw_score = np.concatenate(scores)
        smoothed = convolve_minmax_score(raw_score, w=int(W / 2), minmax=True)
        full_score = np.concatenate([np.zeros(W - 1), smoothed])
        return full_score


# =========================================================================
# 2. XGBoost Autoregressive Forecaster Detector
# =========================================================================
class XGBoostDetector:
    def __init__(self, n_estimators: int = 60, max_depth: int = 4, lr: float = 0.05, random_state: int = 42):
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.lr = lr
        self.random_state = random_state
        self.models = []

    def fit(self, X_train: np.ndarray):
        N, W, D = X_train.shape
        self.models = []
        for d in range(D):
            x_feat = X_train[:, :-1, d]   # Shape: (N, W-1)
            y_target = X_train[:, -1, d]  # Shape: (N,)
            model = xgb.XGBRegressor(
                n_estimators=self.n_estimators,
                max_depth=self.max_depth,
                learning_rate=self.lr,
                random_state=self.random_state,
                n_jobs=-1,
                verbosity=0
            )
            model.fit(x_feat, y_target)
            self.models.append(model)
        return self

    def predict_anomaly_score(self, X_test: np.ndarray, window_size: int) -> np.ndarray:
        N, W, D = X_test.shape
        squared_errors = np.zeros((N, D), dtype=np.float32)
        for d in range(D):
            x_feat = X_test[:, :-1, d]
            y_target = X_test[:, -1, d]
            preds = self.models[d].predict(x_feat)
            squared_errors[:, d] = (y_target - preds) ** 2
        
        raw_mse = np.mean(squared_errors, axis=1)
        smoothed = convolve_minmax_score(raw_mse, w=int(W / 2), minmax=True)
        full_score = np.concatenate([np.zeros(W - 1), smoothed])
        return full_score


# =========================================================================
# 3. PyTorch LSTM-VAE Detector
# =========================================================================
class LSTMVAEModel(nn.Module):
    def __init__(self, n_features: int, window_size: int, hidden_dim: int = 64, latent_dim: int = 16):
        super().__init__()
        self.n_features = n_features
        self.window_size = window_size
        self.hidden_dim = hidden_dim
        self.latent_dim = latent_dim

        self.encoder_lstm = nn.LSTM(
            input_size=n_features,
            hidden_size=hidden_dim,
            batch_first=True
        )
        self.fc_mu = nn.Linear(hidden_dim, latent_dim)
        self.fc_logvar = nn.Linear(hidden_dim, latent_dim)

        self.decoder_fc = nn.Linear(latent_dim, hidden_dim)
        self.decoder_lstm = nn.LSTM(
            input_size=hidden_dim,
            hidden_size=hidden_dim,
            batch_first=True
        )
        self.out_linear = nn.Linear(hidden_dim, n_features)

    def encode(self, x):
        _, (h_n, _) = self.encoder_lstm(x)
        h = h_n[-1]
        mu = self.fc_mu(h)
        logvar = self.fc_logvar(h)
        return mu, logvar

    def reparameterize(self, mu, logvar):
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def decode(self, z):
        h_dec = torch.relu(self.decoder_fc(z))
        h_seq = h_dec.unsqueeze(1).repeat(1, self.window_size, 1)
        out, _ = self.decoder_lstm(h_seq)
        rec = self.out_linear(out)
        return rec

    def forward(self, x):
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        rec = self.decode(z)
        return rec, mu, logvar


class LSTMVAEDetector:
    def __init__(self, n_features: int, window_size: int, hidden_dim: int = 64, latent_dim: int = 16,
                 lr: float = 0.001, epochs: int = 20, batch_size: int = 128, device: str = 'cpu'):
        self.n_features = n_features
        self.window_size = window_size
        self.epochs = epochs
        self.batch_size = batch_size
        self.device = torch.device(device if torch.cuda.is_available() and device != 'cpu' else 'cpu')
        
        self.model = LSTMVAEModel(
            n_features=n_features,
            window_size=window_size,
            hidden_dim=hidden_dim,
            latent_dim=latent_dim
        ).to(self.device)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=lr)

    def fit(self, X_train: np.ndarray):
        self.model.train()
        N, W, D = X_train.shape
        if N > 10000:
            indices = np.linspace(0, N - 1, 10000, dtype=int)
            X_train = X_train[indices]

        tensor_x = torch.tensor(X_train, dtype=torch.float32)
        dataset = TensorDataset(tensor_x)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True, drop_last=False)

        for epoch in range(self.epochs):
            for (batch_x,) in loader:
                batch_x = batch_x.to(self.device)
                self.optimizer.zero_grad()
                rec, mu, logvar = self.model(batch_x)
                rec_loss = torch.mean((rec - batch_x) ** 2)
                kl_loss = -0.5 * torch.mean(1 + logvar - mu.pow(2) - logvar.exp())
                loss = rec_loss + 0.01 * kl_loss
                loss.backward()
                self.optimizer.step()
        return self

    def predict_anomaly_score(self, X_test: np.ndarray, window_size: int) -> np.ndarray:
        self.model.eval()
        tensor_x = torch.tensor(X_test, dtype=torch.float32)
        dataset = TensorDataset(tensor_x)
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=False)

        raw_mse_list = []
        with torch.no_grad():
            for (batch_x,) in loader:
                batch_x = batch_x.to(self.device)
                rec, _, _ = self.model(batch_x)
                mse = torch.mean((rec - batch_x) ** 2, dim=(1, 2)).cpu().numpy()
                raw_mse_list.append(mse)

        raw_mse = np.concatenate(raw_mse_list)
        smoothed = convolve_minmax_score(raw_mse, w=int(window_size / 2), minmax=True)
        full_score = np.concatenate([np.zeros(window_size - 1), smoothed])
        return full_score


# =========================================================================
# Dataset Loader & Baseline Experiment Runner
# =========================================================================
def get_entities_for_dataset(dataset_name: str, stock_dir: str = './dataset/TSB-AD-U'):
    if dataset_name == 'stock':
        files = sorted(glob.glob(os.path.join(stock_dir, '*_Stock_*.csv')))
        if not files:
            files = sorted(glob.glob(os.path.join(stock_dir, '**', '*_Stock_*.csv'), recursive=True))
        return [os.path.splitext(os.path.basename(f))[0] for f in files]
    elif dataset_name == 'anomaly_archive':
        return [str(i).zfill(3) for i in range(1, 251)]
    elif dataset_name == 'iops':
        return [
            'KPI-05f10d3a-239c-3bef-9bdc-a2feeb0037aa', 'KPI-0efb375b-b902-3661-ab23-9a0bb799f4e3',
            'KPI-1c6d7a26-1f1a-3321-bb4d-7a9d969ec8f0', 'KPI-301c70d8-1630-35ac-8f96-bc1b6f4359ea',
            'KPI-42d6616d-c9c5-370a-a8ba-17ead74f3114', 'KPI-43115f2a-baeb-3b01-96f7-4ea14188343c',
            'KPI-431a8542-c468-3988-a508-3afd06a218da', 'KPI-4d2af31a-9916-3d9f-8a8e-8a268a48c095',
            'KPI-54350a12-7a9d-3ca8-b81f-f886b9d156fd', 'KPI-55f8b8b8-b659-38df-b3df-e4a5a8a54bc9',
            'KPI-57051487-3a40-3828-9084-a12f7f23ee38', 'KPI-6a757df4-95e5-3357-8406-165e2bd49360',
            'KPI-6d1114ae-be04-3c46-b5aa-be1a003a57cd', 'KPI-6efa3a07-4544-34a0-b921-a155bd1a05e8',
            'KPI-7103fa0f-cac4-314f-addc-866190247439', 'KPI-847e8ecc-f8d2-3a93-9107-f367a0aab37d',
            'KPI-8723f0fb-eaef-32e6-b372-6034c9c04b80', 'KPI-9c639a46-34c8-39bc-aaf0-9144b37adfc8',
            'KPI-a07ac296-de40-3a7c-8df3-91f642cc14d0', 'KPI-a8c06b47-cc41-3738-9110-12df0ee4c721',
            'KPI-ab216663-dcc2-3a24-b1ee-2c3e550e06c9', 'KPI-adb2fde9-8589-3f5b-a410-5fe14386c7af',
            'KPI-ba5f3328-9f3f-3ff5-a683-84437d16d554', 'KPI-c02607e8-7399-3dde-9d28-8a8da5e5d251',
            'KPI-c69a50cf-ee03-3bd7-831e-407d36c7ee91', 'KPI-da10a69f-d836-3baa-ad40-3e548ecf1fbd',
            'KPI-e0747cad-8dc8-38a9-a9ab-855b61f5551d', 'KPI-f0932edd-6400-3e63-9559-0a9860a1baa9',
            'KPI-ffb82d38-5f00-37db-abc0-5d2e4e4cb6aa'
        ]
    elif dataset_name == 'smd':
        entity_list = ["1-1","1-2","1-3","1-4","1-5","1-6","1-7","1-8","2-1","2-2","2-3","2-4","2-5","2-6","2-7","2-8","2-9","3-1","3-2","3-3","3-4","3-5","3-6","3-7","3-8","3-9","3-10","3-11"]
        return [f'machine-{e}' for e in entity_list]
    elif dataset_name == 'smap':
        return ['A-1', 'A-2', 'A-3', 'A-4', 'A-7', 'B-1', 'D-1', 'D-11', 'D-13', 'D-2', 'D-3', 'D-4', 'D-5', 'D-6', 'D-7', 'D-8', 'D-9', 'E-1', 'E-10', 'E-11', 'E-12', 'E-13', 'E-2', 'E-3', 'E-4', 'E-5', 'E-6', 'E-7', 'E-8', 'E-9', 'F-1', 'F-2', 'F-3', 'G-1', 'G-2', 'G-3', 'G-4', 'G-6', 'G-7', 'P-1', 'P-2', 'P-3', 'P-4', 'P-7', 'R-1', 'S-1', 'T-1', 'T-2', 'T-3']
    elif dataset_name == 'msl':
        return ['C-1', 'D-14', 'D-15', 'D-16', 'F-4', 'F-5', 'F-7', 'F-8', 'M-1', 'M-2', 'M-3', 'M-4', 'M-5', 'M-6', 'M-7', 'P-10', 'P-11', 'P-14', 'P-15', 'T-12', 'T-13', 'T-4', 'T-5']
    else:
        raise ValueError(f"Unknown dataset: {dataset_name}")


def run_baseline_on_entity(dataset_name: str, entity: str, model_type: str, window_size: int = 100,
                           stock_dir: str = './dataset/TSB-AD-U', device: str = 'cuda', seed: int = 42):
    stock_path = None
    stock_tr = None
    if dataset_name == 'stock':
        files = glob.glob(os.path.join(stock_dir, '**', f'{entity}.csv'), recursive=True)
        if not files:
            raise FileNotFoundError(f"Cannot find {entity}.csv under {stock_dir}")
        stock_path = files[0]
        m = re.search(r'_tr_(\d+)_', entity)
        stock_tr = int(m.group(1)) if m else 500

    dataparams = utils.AttrDict(
        dataset=dataset_name,
        entities=entity,
        downsampling=1,
        batch_size=128,
        window_size=window_size,
        window_step=1,
        anomaly_types=['normal'],
        min_range=1,
        min_features=1,
        max_features=1,
        **({'data_path': stock_path, 'train_end': stock_tr} if dataset_name == 'stock' else {})
    )

    # Load normalized train and test splits
    train_ds = datautils._load(dataparams, group='train', validation=False)
    test_ds = datautils._load(dataparams, group='test', validation=False)

    train_Y = train_ds.entities[0].Y  # Shape: (features, time_train)
    test_Y = test_ds.entities[0].Y    # Shape: (features, time_test)
    test_labels = test_ds.entities[0].labels  # Shape: (1, time_test) or (time_test,)
    if test_labels.ndim == 2:
        test_labels = test_labels[0]
    gt = test_labels.astype(int)

    n_features, time_train = train_Y.shape
    _, time_test = test_Y.shape

    # Determine training window step to balance speed and coverage
    train_step = 1
    if dataset_name in ('iops', 'smd', 'smap', 'msl'):
        train_step = 10
    elif dataset_name == 'anomaly_archive':
        train_step = 1 if time_train < 10000 else (10 if time_train < 100000 else 100)

    train_windows = sliding_window_view(train_Y, window_size=window_size, step=train_step)
    test_windows = sliding_window_view(test_Y, window_size=window_size, step=1)

    # Fit and predict baseline
    if model_type == 'iforest':
        detector = IsolationForestDetector(n_estimators=100, random_state=seed)
        detector.fit(train_windows)
        score = detector.predict_anomaly_score(test_windows, window_size=window_size)
    elif model_type == 'xgboost':
        detector = XGBoostDetector(n_estimators=50, max_depth=4, lr=0.05, random_state=seed)
        detector.fit(train_windows)
        score = detector.predict_anomaly_score(test_windows, window_size=window_size)
    elif model_type == 'lstm_vae':
        detector = LSTMVAEDetector(
            n_features=n_features,
            window_size=window_size,
            hidden_dim=64,
            latent_dim=16,
            lr=0.001,
            epochs=20,
            batch_size=128,
            device=device
        )
        detector.fit(train_windows)
        score = detector.predict_anomaly_score(test_windows, window_size=window_size)
    else:
        raise ValueError(f"Unknown baseline model: {model_type}")

    # Crop to matching lengths
    n_pts = min(len(gt), len(score))
    gt_cropped = gt[:n_pts]
    score_cropped = score[:n_pts]

    # Compute VUS metrics
    metrics = {'entity': entity, 'model': model_type, 'VUS_ROC': np.nan, 'VUS_PR': np.nan, 'RF': np.nan}
    if get_metrics is not None and gt_cropped.sum() > 0:
        try:
            res = get_metrics(score_cropped, gt_cropped, metric='all', slidingWindow=window_size)
            metrics['VUS_ROC'] = float(res.get('VUS_ROC', np.nan))
            metrics['VUS_PR'] = float(res.get('VUS_PR', np.nan))
            metrics['RF'] = float(res.get('RF', np.nan))
        except Exception as e:
            print(f"Metrics error for {entity} with {model_type}: {e}")
    else:
        print(f"Skipping VUS metrics for {entity} (no anomalies or vus library missing)")

    return metrics


def run_experiment(dataset_name: str, model_type: str, window_size: int = 100,
                   stock_dir: str = './dataset/TSB-AD-U', device: str = 'cuda',
                   seed: int = 42, max_hours: float = 11.0):
    os.makedirs('./metrics', exist_ok=True)
    done_file = f'./metrics/done_{dataset_name}_{model_type}.txt'
    metrics_file = f'./metrics/{dataset_name}_{model_type}.csv'

    done_entities = set()
    if os.path.exists(done_file):
        with open(done_file, 'r') as f:
            done_entities = set(f.read().split())
    print(f"[{dataset_name} | {model_type}] Already completed: {len(done_entities)} entities")

    entities = get_entities_for_dataset(dataset_name, stock_dir=stock_dir)
    print(f"[{dataset_name} | {model_type}] Total entities: {len(entities)}")

    start_time = time.time()
    for idx, entity in enumerate(entities):
        if entity in done_entities:
            print(f"Skip {entity} (already done)")
            continue

        elapsed_hours = (time.time() - start_time) / 3600.0
        if max_hours > 0 and elapsed_hours > max_hours:
            print(f"Time limit of {max_hours} hours reached. Stopping at entity {entity}.")
            break

        print(f"[{idx+1}/{len(entities)}] Running {model_type} on {dataset_name} -> {entity}...")
        try:
            row = run_baseline_on_entity(
                dataset_name=dataset_name,
                entity=entity,
                model_type=model_type,
                window_size=window_size,
                stock_dir=stock_dir,
                device=device,
                seed=seed
            )
            print(f"Result {entity}: V-R={row['VUS_ROC']:.4f}, V-P={row['VUS_PR']:.4f}, RF={row['RF']:.4f}")

            is_new = not os.path.exists(metrics_file)
            with open(metrics_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['entity', 'model', 'VUS_ROC', 'VUS_PR', 'RF'])
                if is_new:
                    writer.writeheader()
                writer.writerow(row)

            with open(done_file, 'a') as f:
                f.write(entity + '\n')
            
            upload_cmd = os.environ.get('UPLOAD_CMD', '')
            if upload_cmd:
                os.system(upload_cmd)

        except Exception as e:
            print(f"Error processing {entity}: {e}")
            import traceback
            traceback.print_exc()

    print(f"Finished baseline {model_type} on {dataset_name}!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='stock',
                        choices=['stock', 'anomaly_archive', 'iops', 'smd', 'smap', 'msl', 'all'])
    parser.add_argument('--model', type=str, default='iforest',
                        choices=['iforest', 'xgboost', 'lstm_vae', 'all'])
    parser.add_argument('--window-size', type=int, default=100)
    parser.add_argument('--stock-dir', type=str, default=os.environ.get('STOCK_DIR', './dataset/TSB-AD-U'))
    parser.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu')
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--max-hours', type=float, default=11.0)
    args = parser.parse_args()

    datasets = [args.dataset] if args.dataset != 'all' else ['stock', 'anomaly_archive', 'iops', 'smd', 'smap', 'msl']
    models = [args.model] if args.model != 'all' else ['iforest', 'xgboost', 'lstm_vae']

    for d in datasets:
        for m in models:
            print(f"\n==========================================")
            print(f"Running Experiment: Dataset={d}, Model={m}")
            print(f"==========================================")
            run_experiment(
                dataset_name=d,
                model_type=m,
                window_size=args.window_size,
                stock_dir=args.stock_dir,
                device=args.device,
                seed=args.seed,
                max_hours=args.max_hours
            )
