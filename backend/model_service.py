import os
import glob
import re
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA

import utils
from models.meta import ConvAEC
from main import convolve_minmax_score, mse, label_score_selected_feature

# Default 12 anomaly classes from RedLamp
ANOMALY_TYPES = [
    'normal', 'spike', 'flip', 'speedup', 'noise', 'cutoff',
    'average', 'scale', 'wander', 'contextual', 'upsidedown', 'mixture'
]

DATASET_FEATURES = {
    'stock': 1,
    'anomaly_archive': 1,
    'iops': 1,
    'smd': 38,
    'smap': 25,
    'msl': 55
}

class ModelService:
    def __init__(self, pretrain_dir="D:/repo/redlamp/pretrain"):
        self.pretrain_dir = os.path.abspath(pretrain_dir)
        self.model_cache = {}

    def list_models(self):
        """Discovers all models in pretrain_dir and extracts their configuration."""
        models = []
        pattern = os.path.join(self.pretrain_dir, "**", "bestmodel.pkl")
        for pkl_path in glob.glob(pattern, recursive=True):
            dir_path = os.path.dirname(pkl_path)
            rel_dir = os.path.relpath(dir_path, self.pretrain_dir).replace("\\", "/")
            parts = rel_dir.split("/")
            
            # parts structure: [dataset, entity, cfg_folder (d1_b128_w100_s1), seed (0)]
            dataset = parts[0] if len(parts) > 0 else "unknown"
            entity = parts[1] if len(parts) > 1 else "default"
            cfg = parts[2] if len(parts) > 2 else "d1_b128_w100_s1"
            seed = parts[3] if len(parts) > 3 else "0"

            # Parse config folder name
            m_w = re.search(r'w(\d+)', cfg)
            m_s = re.search(r's(\d+)', cfg)
            m_b = re.search(r'b(\d+)', cfg)
            m_d = re.search(r'd(\d+)', cfg)

            window_size = int(m_w.group(1)) if m_w else 100
            window_step = int(m_s.group(1)) if m_s else 1
            batch_size = int(m_b.group(1)) if m_b else 128
            downsampling = int(m_d.group(1)) if m_d else 1
            n_features = DATASET_FEATURES.get(dataset, 1)

            # Check loss files
            loss_files = [os.path.basename(f) for f in glob.glob(os.path.join(dir_path, "*loss*.txt"))]
            has_loss = len(loss_files) > 0

            model_id = rel_dir
            display_name = f"{dataset.upper()} - {entity} (W={window_size}, D={n_features})"

            models.append({
                "model_id": model_id,
                "display_name": display_name,
                "dataset": dataset,
                "entity": entity,
                "config_str": cfg,
                "seed": seed,
                "n_features": n_features,
                "window_size": window_size,
                "window_step": window_step,
                "embedding_dim": 128,
                "classifier_dim": 32,
                "classes": len(ANOMALY_TYPES),
                "anomaly_types": ANOMALY_TYPES,
                "has_loss": has_loss,
                "loss_files": loss_files,
                "pkl_size": os.path.getsize(pkl_path)
            })

        models.sort(key=lambda x: (x["dataset"], x["entity"]))
        return models

    def get_model(self, model_id):
        """Loads and caches ConvAEC model on CPU."""
        if model_id in self.model_cache:
            return self.model_cache[model_id]

        full_dir = os.path.join(self.pretrain_dir, model_id.replace("/", os.sep))
        pkl_path = os.path.join(full_dir, "bestmodel.pkl")
        if not os.path.exists(pkl_path):
            raise FileNotFoundError(f"Model file not found at: {pkl_path}")

        # Determine n_features
        dataset = model_id.split("/")[0]
        n_features = DATASET_FEATURES.get(dataset, 1)

        params = utils.AttrDict(
            name='ConvAEC',
            n_features=n_features,
            n_time=100,
            num_filters=[128, 128, 256, 256],
            embedding_dim=128,
            kernel_size=4,
            dropout=0.2,
            normalization='batch',
            stride=2,
            padding=2,
            anomaly_types=ANOMALY_TYPES,
            classes=len(ANOMALY_TYPES),
            classifier_dim=32,
            c_loss_ratio=0.1,
            apply_anomaly_mask=True,
            label_smoothing=True,
            alpha=0.1,
            beta=0.01,
        )

        model = ConvAEC(params)
        state_dict = torch.load(pkl_path, map_location='cpu')
        model.load_state_dict(state_dict)
        model.eval()

        self.model_cache[model_id] = (model, params)
        return model, params

    def get_loss_data(self, model_id):
        """Reads loss text files if present."""
        full_dir = os.path.join(self.pretrain_dir, model_id.replace("/", os.sep))
        files = {
            "train_loss": os.path.join(full_dir, "train_loss.txt"),
            "train_loss_ae": os.path.join(full_dir, "train_loss_ae.txt"),
            "train_loss_c": os.path.join(full_dir, "train_loss_c.txt"),
            "valid_loss": os.path.join(full_dir, "valid_loss.txt"),
            "valid_loss_ae": os.path.join(full_dir, "valid_loss_ae.txt"),
            "valid_loss_c": os.path.join(full_dir, "valid_loss_c.txt"),
            "time": os.path.join(full_dir, "time.txt"),
        }

        result = {}
        for k, p in files.items():
            if os.path.exists(p):
                try:
                    data = np.loadtxt(p)
                    result[k] = data.tolist() if data.ndim > 0 else [float(data)]
                except Exception:
                    result[k] = []
            else:
                result[k] = []
        return result

    def analyze_series(self, model_id, series_data, labels=None, n_train=500,
                       threshold_type="percentile", threshold_val=99.5, ce_threshold=0.05,
                       step=1):
        """
        Executes the full RedLamp evaluation pipeline on CPU.
        series_data: np.ndarray shape (T, D) or (T,)
        """
        model, params = self.get_model(model_id)
        W = params.n_time
        D = params.n_features

        # Ensure 2D (T, D)
        if series_data.ndim == 1:
            series_data = series_data.reshape(-1, 1)

        T, actual_D = series_data.shape
        if actual_D != D:
            # Handle feature mismatch gracefully (take first D or pad)
            if actual_D > D:
                series_data = series_data[:, :D]
            else:
                pad = np.zeros((T, D - actual_D))
                series_data = np.hstack([series_data, pad])

        n_train = min(max(W + 5, int(n_train)), T)

        # 1. Normalization (fit on first n_train points only)
        scaler = MinMaxScaler()
        scaler.fit(series_data[:n_train])
        series_norm = scaler.transform(series_data)

        # 2. Sliding windows
        window_step = max(1, int(step))
        windows = []
        window_indices = []  # time index t of window end point: [t - W + 1, t]
        for start_idx in range(0, T - W + 1, window_step):
            end_idx = start_idx + W
            windows.append(series_norm[start_idx:end_idx])
            window_indices.append(end_idx - 1)

        windows = np.array(windows, dtype=np.float32)  # shape (N, W, D)
        N = len(windows)
        if N == 0:
            raise ValueError(f"Series length {T} is too short for window size {W}")

        # 3. Model inference on CPU in batches
        batch_size = 128
        preds, pred_labels, pred_encs = [], [], []
        with torch.no_grad():
            for i in range(0, N, batch_size):
                b = torch.from_numpy(windows[i:i + batch_size])
                p, pl, pe = model(b)
                preds.append(p.numpy())
                pred_labels.append(pl.numpy())
                pred_encs.append(pe.squeeze(-1).numpy())

        preds = np.concatenate(preds, axis=0)          # (N, W, D)
        pred_labels = np.concatenate(pred_labels, axis=0) # (N, 12)
        pred_encs = np.concatenate(pred_encs, axis=0)     # (N, 128)

        # 4. Reconstruction MSE
        raw_mse = mse(windows.reshape(N, -1), preds.reshape(N, -1))
        mse_conv = convolve_minmax_score(raw_mse, w=int(W / 2), minmax=False)
        mse_minmax = convolve_minmax_score(raw_mse, w=int(W / 2), minmax=True)

        # 5. Classification CE score
        mean_label = np.mean(pred_labels, axis=0)
        indices = np.where(mean_label > ce_threshold)[0]
        if 0 not in indices:
            indices = np.insert(indices, 0, 0)
        indices = np.array(indices, dtype=int)

        raw_ce = label_score_selected_feature(pred_labels, axis=indices)
        ce_conv = convolve_minmax_score(raw_ce, w=int(W / 2), minmax=False)
        ce_minmax = convolve_minmax_score(raw_ce, w=int(W / 2), minmax=True)

        # 6. Combined RedLamp score (normalized across whole sequence)
        final_anomaly_score = (mse_minmax + ce_minmax) / 2.0

        # 7. Raw reference score distribution & Thresholding
        # Reference windows: windows ending within [:n_train]
        ref_window_count = max(1, sum(1 for idx in window_indices if idx < n_train))
        ref_raw_mse = raw_mse[:ref_window_count]
        ref_raw_ce = raw_ce[:ref_window_count]

        # Standardized raw combined score relative to normal reference period
        mu_mse, std_mse = float(np.mean(ref_raw_mse)), float(np.std(ref_raw_mse)) + 1e-8
        mu_ce, std_ce = float(np.mean(ref_raw_ce)), float(np.std(ref_raw_ce)) + 1e-8

        z_mse = (raw_mse - mu_mse) / std_mse
        z_ce = (raw_ce - mu_ce) / std_ce
        raw_combined_score = (z_mse + z_ce) / 2.0

        ref_combined = raw_combined_score[:ref_window_count]

        # Compute detection threshold on reference
        if threshold_type == "sigma":
            k = float(threshold_val)
            threshold = float(np.mean(ref_combined) + k * np.std(ref_combined))
            threshold_desc = f"Mean + {k}σ trên {ref_window_count} cửa sổ tham chiếu ({threshold:.3f})"
        else:  # percentile
            p = float(threshold_val)
            threshold = float(np.percentile(ref_combined, p))
            threshold_desc = f"Phân vị {p}% trên {ref_window_count} cửa sổ tham chiếu ({threshold:.3f})"

        flagged_windows = (raw_combined_score > threshold).astype(bool)

        # 8. Contiguous flagged regions and Top-3 labels
        flagged_regions = []
        in_region = False
        r_start = 0

        for i, flagged in enumerate(flagged_windows):
            if flagged and not in_region:
                in_region = True
                r_start = i
            elif not flagged and in_region:
                in_region = False
                flagged_regions.append((r_start, i - 1))
        if in_region:
            flagged_regions.append((r_start, N - 1))

        # Determine class for each region
        regions_info = []
        for s_idx, e_idx in flagged_regions:
            region_probs = np.mean(pred_labels[s_idx:e_idx + 1], axis=0)  # shape (12,)
            # Exclude eliminated indices
            masked_probs = np.copy(region_probs)
            masked_probs[indices] = 0.0

            best_class_idx = int(np.argmax(masked_probs))
            best_prob = float(masked_probs[best_class_idx])

            # Get sorted top-3 classes not in indices
            valid_classes = [c for c in range(12) if c not in indices]
            valid_classes.sort(key=lambda c: region_probs[c], reverse=True)
            top3 = [
                {"class_idx": c, "class_name": ANOMALY_TYPES[c], "prob": float(region_probs[c])}
                for c in valid_classes[:3]
            ]

            label_name = ANOMALY_TYPES[best_class_idx] if best_prob > 0.02 else "Không xác định"

            start_t = int(window_indices[s_idx])
            end_t = int(window_indices[e_idx])

            regions_info.append({
                "window_start": s_idx,
                "window_end": e_idx,
                "time_start": start_t,
                "time_end": end_t,
                "label": label_name,
                "max_prob": best_prob,
                "top3": top3
            })

        # Overall summary
        has_anomaly = len(flagged_regions) > 0
        total_flagged_windows = int(np.sum(flagged_windows))
        flagged_pct = (total_flagged_windows / N) * 100.0

        if has_anomaly:
            conclusion = "Có bất thường"
            confidence = min(99.9, max(50.0, 50.0 + (flagged_pct * 1.5) + (float(np.max(raw_combined_score) - threshold) * 5.0)))
            # Global top 3 across all flagged windows
            flagged_indices_list = np.where(flagged_windows)[0]
            avg_flagged_probs = np.mean(pred_labels[flagged_indices_list], axis=0)
            valid_classes = [c for c in range(12) if c not in indices]
            valid_classes.sort(key=lambda c: avg_flagged_probs[c], reverse=True)
            overall_top3 = [
                {"class_idx": c, "class_name": ANOMALY_TYPES[c], "prob": float(avg_flagged_probs[c])}
                for c in valid_classes[:3]
            ]
        else:
            conclusion = "Không có bất thường"
            confidence = 95.0
            overall_top3 = []

        # 9. 2D PCA projection of latent space
        # Downsample PCA input if N > 5000 for fast browser rendering
        stride_pca = max(1, N // 2000)
        pca = PCA(n_components=2)
        pca_coords = pca.fit_transform(pred_encs[::stride_pca])
        pca_indices = list(range(0, N, stride_pca))

        # Downsample series visualization points if T > 5000 to keep UI responsive
        stride_disp = max(1, T // 3000)
        disp_time = list(range(0, T, stride_disp))
        disp_series_raw = series_data[::stride_disp, 0].tolist()
        disp_series_norm = series_norm[::stride_disp, 0].tolist()
        disp_labels = labels[::stride_disp].tolist() if labels is not None else None

        stride_win = max(1, N // 2500)
        win_disp_indices = list(range(0, N, stride_win))
        disp_window_t = [int(window_indices[i]) for i in win_disp_indices]

        return {
            "model_id": model_id,
            "conclusion": conclusion,
            "confidence": round(confidence, 1),
            "has_anomaly": has_anomaly,
            "overall_top3": overall_top3,
            "threshold_desc": threshold_desc,
            "threshold": threshold,
            "threshold_type": threshold_type,
            "threshold_val": threshold_val,
            "n_train": n_train,
            "W": W,
            "D": D,
            "total_points": T,
            "total_windows": N,
            "indices_excluded": indices.tolist(),
            "indices_excluded_names": [ANOMALY_TYPES[i] for i in indices.tolist()],
            "flagged_regions": regions_info,
            "flagged_pct": round(flagged_pct, 2),
            "display": {
                "disp_time": disp_time,
                "disp_series_raw": disp_series_raw,
                "disp_series_norm": disp_series_norm,
                "disp_labels": disp_labels,
                "win_disp_indices": win_disp_indices,
                "disp_window_t": disp_window_t,
                "raw_mse": [float(raw_mse[i]) for i in win_disp_indices],
                "mse_conv": [float(mse_conv[i]) for i in win_disp_indices],
                "mse_minmax": [float(mse_minmax[i]) for i in win_disp_indices],
                "raw_ce": [float(raw_ce[i]) for i in win_disp_indices],
                "ce_conv": [float(ce_conv[i]) for i in win_disp_indices],
                "ce_minmax": [float(ce_minmax[i]) for i in win_disp_indices],
                "raw_combined_score": [float(raw_combined_score[i]) for i in win_disp_indices],
                "anomaly_score": [float(final_anomaly_score[i]) for i in win_disp_indices],
                "flagged_windows": [bool(flagged_windows[i]) for i in win_disp_indices],
                "pca_x": [float(pt[0]) for pt in pca_coords],
                "pca_y": [float(pt[1]) for pt in pca_coords],
                "pca_indices": pca_indices,
                "pred_label_sampled": [pred_labels[i].tolist() for i in win_disp_indices]
            }
        }

    def get_window_detail(self, model_id, series_data, window_idx, n_train=500):
        """Retrieves exact reconstruction, pred_label, and errors for a specific window index."""
        model, params = self.get_model(model_id)
        W = params.n_time
        D = params.n_features

        if series_data.ndim == 1:
            series_data = series_data.reshape(-1, 1)
        if series_data.shape[1] > D:
            series_data = series_data[:, :D]
        elif series_data.shape[1] < D:
            pad = np.zeros((len(series_data), D - series_data.shape[1]))
            series_data = np.hstack([series_data, pad])

        scaler = MinMaxScaler()
        scaler.fit(series_data[:n_train])
        series_norm = scaler.transform(series_data)

        window_idx = max(0, min(window_idx, len(series_norm) - W))
        win_data = series_norm[window_idx:window_idx + W] # (W, D)

        b = torch.from_numpy(win_data).unsqueeze(0).float()
        with torch.no_grad():
            p, pl, pe = model(b)

        p = p.squeeze(0).numpy() # (W, D)
        pl = pl.squeeze(0).numpy().tolist() # (12,)
        sq_err = np.mean((win_data - p) ** 2, axis=-1).tolist() # (W,)

        return {
            "window_idx": window_idx,
            "time_start": window_idx,
            "time_end": window_idx + W - 1,
            "input_norm": win_data[:, 0].tolist(),
            "pred_norm": p[:, 0].tolist(),
            "squared_error": sq_err,
            "pred_label": pl,
            "classes": ANOMALY_TYPES
        }

    def predict_custom_point(self, model_id, feature_values):
        """
        Runs model inference on a single custom point or 5-feature input.
        Constructs a stationary/synthetic context window with the user's features at the center/end.
        """
        model, params = self.get_model(model_id)
        W = params.n_time
        D = params.n_features

        # Construct a window of shape (1, W, D)
        base_window = np.zeros((1, W, D), dtype=np.float32)
        # Fill features
        for f_idx, val in enumerate(feature_values[:D]):
            base_window[0, :, f_idx] = float(val)

        b = torch.from_numpy(base_window)
        with torch.no_grad():
            p, pl, pe = model(b)

        probs = pl.squeeze(0).numpy().tolist()
        reconstruction = p.squeeze(0).numpy()[:, 0].tolist()

        # Sort classes
        sorted_classes = sorted(
            [{"name": ANOMALY_TYPES[i], "prob": float(probs[i])} for i in range(len(ANOMALY_TYPES))],
            key=lambda x: x["prob"],
            reverse=True
        )

        return {
            "reconstruction_sample": reconstruction[:20],
            "pred_label": probs,
            "sorted_classes": sorted_classes,
            "top1": sorted_classes[0],
            "top3": sorted_classes[:3]
        }

