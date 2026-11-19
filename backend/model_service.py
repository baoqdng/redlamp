import os
import re
import ast
import glob
import numpy as np
import pandas as pd
import torch
from sklearn.preprocessing import MinMaxScaler
from typing import Dict, Any, List, Optional, Tuple

import utils
from models.meta import ConvAEC
from main import anomaly_scoreing
from backend.metrics_eval import (
    PAPER_REFERENCE,
    PaperMetricor,
    align_labels_centre,
    compute_paper_metrics,
    compute_rf_oracle,
    load_eval_cache,
    save_eval_cache,
)

ANOMALY_TYPES = [
    'normal', 'spike', 'flip', 'speedup', 'noise', 'cutoff',
    'average', 'scale', 'wander', 'contextual', 'upsidedown', 'mixture'
]

PSEUDO_ANOMALY_INFO = {
    0: {
        "name": "normal",
        "name_vi": "Bình thường",
        "desc_vi": "Tín hiệu hoạt động ổn định, không có biến dạng bất thường giả lập."
    },
    1: {
        "name": "spike",
        "name_vi": "Đỉnh nhọn (Spike)",
        "desc_vi": "Biến động tăng/giảm biên độ đột biến cục bộ tại 1-2 điểm."
    },
    2: {
        "name": "flip",
        "name_vi": "Đảo cực (Flip)",
        "desc_vi": "Đảo ngược dấu hoặc cực tính tín hiệu so với hình thái chuẩn."
    },
    3: {
        "name": "speedup",
        "name_vi": "Tăng tốc tần số (Speedup)",
        "desc_vi": "Chu kỳ hoặc tần số dao động của chuỗi tăng nhanh bất thường."
    },
    4: {
        "name": "noise",
        "name_vi": "Nhiễu ngẫu nhiên (Noise)",
        "desc_vi": "Biên độ bị xáo trộn bởi nhiễu trắng ngẫu nhiên cường độ lớn."
    },
    5: {
        "name": "cutoff",
        "name_vi": "Cắt cụt biên độ (Cutoff)",
        "desc_vi": "Tín hiệu bị giới hạn trần hoặc đáy (clipping/saturation)."
    },
    6: {
        "name": "average",
        "name_vi": "Trung bình hóa (Average)",
        "desc_vi": "Tín hiệu bị làm phẳng, mất đi dao động và biến thiên chi tiết."
    },
    7: {
        "name": "scale",
        "name_vi": "Co giãn biên độ (Scale)",
        "desc_vi": "Biên độ toàn bộ cửa sổ bị phóng to hoặc thu nhỏ bất thường."
    },
    8: {
        "name": "wander",
        "name_vi": "Trôi dạt xu hướng (Wander)",
        "desc_vi": "Đường baseline trôi dạt dần khỏi trục cân bằng chuẩn."
    },
    9: {
        "name": "contextual",
        "name_vi": "Bất thường ngữ cảnh (Contextual)",
        "desc_vi": "Giá trị nằm trong khoảng hợp lệ nhưng không khớp với nhịp điệu xung quanh."
    },
    10: {
        "name": "upsidedown",
        "name_vi": "Lộn ngược chuỗi (Upside-down)",
        "desc_vi": "Hình thái chuỗi bị đảo ngược chiều dọc qua trục trung vị."
    },
    11: {
        "name": "mixture",
        "name_vi": "Bất thường hỗn hợp (Mixture)",
        "desc_vi": "Sự kết hợp đồng thời của nhiều loại biến dạng giả lập khác nhau."
    }
}


class ModelService:
    """
    Service indexing ALL entities across all 5 datasets strictly from
    D:/repo/redlamp/dataset, pre-trained models inside D:/repo/redlamp/pretrain,
    and metrics inside D:/repo/redlamp/metrics.
    """

    def __init__(
        self,
        pretrain_dir: Optional[str] = None,
        dataset_dir: Optional[str] = None,
        metrics_dir: Optional[str] = None,
    ):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.base_dir = base_dir
        self.pretrain_dir = os.path.abspath(pretrain_dir or os.path.join(base_dir, "pretrain"))
        self.dataset_dir = os.path.abspath(dataset_dir or os.path.join(base_dir, "dataset"))
        self.metrics_dir = os.path.abspath(metrics_dir or os.path.join(base_dir, "metrics"))

        self.model_cache: Dict[str, Tuple[ConvAEC, utils.AttrDict]] = {}
        self.data_cache: Dict[Tuple[str, str], Dict[str, Any]] = {}
        self.nasa_meta_df: Optional[pd.DataFrame] = None
        self.stock_metrics: Dict[str, Dict[str, float]] = {}
        self.eval_cache_path = os.path.join(self.metrics_dir, "paper_eval_cache.json")
        self.eval_cache = load_eval_cache(self.eval_cache_path)
        self.index_cache: Dict[str, List[Dict[str, Any]]] = {}
        self.scan_index()

    def _parse_stock_csv(self, path: str) -> Dict[str, Dict[str, float]]:
        res: Dict[str, Dict[str, float]] = {}
        if not path or not os.path.exists(path):
            return res
        try:
            df = pd.read_csv(path)
            for _, row in df.iterrows():
                ent = str(row.get("entity", "")).strip()
                if not ent:
                    continue
                res[ent] = {
                    "vus_roc": float(row.get("VUS_ROC", row.get("VUS-ROC", 0.0))),
                    "vus_pr": float(row.get("VUS_PR", row.get("VUS-PR", 0.0))),
                    "rf": float(row.get("RF", 0.0)),
                }
        except Exception as e:
            print(f"[ModelService] Warning parsing stock metrics {path}: {e}")
        return res

    def _find_bestmodel(self, root_dir: str) -> Optional[str]:
        if not root_dir or not os.path.isdir(root_dir):
            return None
        pkls = sorted(glob.glob(os.path.join(root_dir, "**", "bestmodel.pkl"), recursive=True))
        if not pkls:
            return None
        for p in pkls:
            if os.path.basename(os.path.dirname(p)) == "0":
                return p
        return pkls[0]

    def _load_nasa_meta(self) -> pd.DataFrame:
        if self.nasa_meta_df is None:
            csv_path = os.path.join(self.dataset_dir, "NASA", "labeled_anomalies.csv")
            if os.path.exists(csv_path):
                self.nasa_meta_df = pd.read_csv(csv_path)
            else:
                self.nasa_meta_df = pd.DataFrame(columns=["chan_id", "spacecraft", "anomaly_sequences"])
        return self.nasa_meta_df

    def scan_index(self) -> Dict[str, List[Dict[str, Any]]]:
        """Indexes every entity from D:/repo/redlamp/dataset backed by pretrain/ checkpoints."""
        datasets: Dict[str, List[Dict[str, Any]]] = {}
        self.stock_metrics = self._parse_stock_csv(os.path.join(self.metrics_dir, "stock_per_entity.csv"))
        nasa_meta = self._load_nasa_meta()

        # 1. SMD (All 28 machines from dataset/ServerMachineDataset/test/*.txt + pretrain/smd)
        smd_test_dir = os.path.join(self.dataset_dir, "ServerMachineDataset", "test")
        smd_disk_ents = set()
        if os.path.isdir(smd_test_dir):
            for f in os.listdir(smd_test_dir):
                if f.endswith(".txt"):
                    smd_disk_ents.add(os.path.splitext(f)[0])
        smd_pre_root = os.path.join(self.pretrain_dir, "smd")
        smd_default_model = self._find_bestmodel(smd_pre_root)
        if os.path.isdir(smd_pre_root):
            for d in os.listdir(smd_pre_root):
                if os.path.isdir(os.path.join(smd_pre_root, d)):
                    smd_disk_ents.add(d)

        smd_entities = []
        for ent_name in sorted(smd_disk_ents):
            own_model = self._find_bestmodel(os.path.join(smd_pre_root, ent_name))
            model_path = own_model or smd_default_model
            smd_entities.append({
                "dataset": "smd",
                "entity": ent_name,
                "seeds": [0],
                "default_seed": 0,
                "n_features": 38,
                "window_size": 100,
                "window_step": 10,
                "embedding_dim": 128,
                "has_model": model_path is not None,
                "model_path": model_path,
                "has_own_checkpoint": own_model is not None,
                "is_multi_seed": False,
                "per_seed_metrics": {},
                "aggregate_metrics": None,
                "single_metrics": None,
            })
        datasets["smd"] = smd_entities

        # 2. IOPS / AIOPS (All 29 KPIs from dataset/IOPS/*.test.out + pretrain/iops)
        iops_dir = os.path.join(self.dataset_dir, "IOPS")
        iops_disk_ents = set()
        if os.path.isdir(iops_dir):
            for f in os.listdir(iops_dir):
                if f.endswith(".test.out"):
                    iops_disk_ents.add(f[:-9])
        iops_pre_root = os.path.join(self.pretrain_dir, "iops")
        iops_default_model = self._find_bestmodel(iops_pre_root)
        if os.path.isdir(iops_pre_root):
            for d in os.listdir(iops_pre_root):
                if os.path.isdir(os.path.join(iops_pre_root, d)):
                    iops_disk_ents.add(d)

        iops_entities = []
        for ent_name in sorted(iops_disk_ents):
            own_model = self._find_bestmodel(os.path.join(iops_pre_root, ent_name))
            model_path = own_model or iops_default_model
            iops_entities.append({
                "dataset": "iops",
                "entity": ent_name,
                "seeds": [0],
                "default_seed": 0,
                "n_features": 1,
                "window_size": 100,
                "window_step": 10,
                "embedding_dim": 128,
                "has_model": model_path is not None,
                "model_path": model_path,
                "has_own_checkpoint": own_model is not None,
                "is_multi_seed": False,
                "per_seed_metrics": {},
                "aggregate_metrics": None,
                "single_metrics": None,
            })
        datasets["iops"] = iops_entities

        # 3 & 4. MSL (27 channels) & SMAP (55 channels) from dataset/NASA
        for ds_name, n_feat, sc_code in [("msl", 55, "MSL"), ("smap", 25, "SMAP")]:
            ds_root = os.path.join(self.pretrain_dir, ds_name)
            model_path = self._find_bestmodel(ds_root)
            ds_entities = []
            if model_path:
                chans = sorted(
                    nasa_meta.loc[nasa_meta["spacecraft"] == sc_code, "chan_id"].tolist()
                ) if not nasa_meta.empty else [ds_name]
                local_chans = [
                    c for c in chans
                    if os.path.exists(os.path.join(self.dataset_dir, "NASA", "test", f"{c}.npy"))
                ]
                if not local_chans:
                    local_chans = [ds_name]
                for chan in local_chans:
                    ds_entities.append({
                        "dataset": ds_name,
                        "entity": chan,
                        "seeds": [0],
                        "default_seed": 0,
                        "n_features": n_feat,
                        "window_size": 100,
                        "window_step": 10,
                        "embedding_dim": 128,
                        "has_model": True,
                        "model_path": model_path,
                        "has_own_checkpoint": True,
                        "is_multi_seed": False,
                        "per_seed_metrics": {},
                        "aggregate_metrics": None,
                        "single_metrics": None,
                    })
            datasets[ds_name] = ds_entities

        # 5. Stock (All 20 entities from dataset/stock/*.csv + pretrain/stock)
        stock_dir = os.path.join(self.dataset_dir, "stock")
        stock_disk_ents = set()
        if os.path.isdir(stock_dir):
            for f in os.listdir(stock_dir):
                if f.endswith(".csv"):
                    stock_disk_ents.add(os.path.splitext(f)[0])
        stock_pre_root = os.path.join(self.pretrain_dir, "stock")
        stock_default_model = self._find_bestmodel(stock_pre_root)
        if os.path.isdir(stock_pre_root):
            for d in os.listdir(stock_pre_root):
                if os.path.isdir(os.path.join(stock_pre_root, d)):
                    stock_disk_ents.add(d)

        stock_entities = []
        for ent_name in sorted(stock_disk_ents):
            own_model = self._find_bestmodel(os.path.join(stock_pre_root, ent_name))
            model_path = own_model or stock_default_model
            stock_entities.append({
                "dataset": "stock",
                "entity": ent_name,
                "seeds": [0],
                "default_seed": 0,
                "n_features": 1,
                "window_size": 100,
                "window_step": 1 if own_model else 10,
                "embedding_dim": 128,
                "has_model": model_path is not None,
                "model_path": model_path,
                "has_own_checkpoint": own_model is not None,
                "is_multi_seed": False,
                "per_seed_metrics": {},
                "aggregate_metrics": None,
                "single_metrics": self.stock_metrics.get(ent_name),
            })
        datasets["stock"] = stock_entities

        self.index_cache = datasets
        return datasets

    def get_model_path(self, dataset: str, entity: str, seed: int = 0) -> Optional[str]:
        """Resolves own entity bestmodel.pkl or dataset representative bestmodel.pkl inside pretrain/."""
        if dataset in ("msl", "smap"):
            return self._find_bestmodel(os.path.join(self.pretrain_dir, dataset))
        own = self._find_bestmodel(os.path.join(self.pretrain_dir, dataset, entity))
        if own:
            return own
        return self._find_bestmodel(os.path.join(self.pretrain_dir, dataset))

    def get_test_dir(self, dataset: str, entity: str, seed: int = 0) -> Optional[str]:
        """Returns entity's own test_all/*.npy directory if it exists inside pretrain/."""
        if dataset in ("msl", "smap"):
            return None
        own = self._find_bestmodel(os.path.join(self.pretrain_dir, dataset, entity))
        if not own:
            return None
        test_all = os.path.join(os.path.dirname(own), "test_all")
        if os.path.isdir(test_all) and os.path.exists(os.path.join(test_all, "anomaly_score.npy")):
            return test_all
        return None

    def load_model(self, dataset: str, entity: str, seed: int = 0) -> Tuple[ConvAEC, utils.AttrDict]:
        """Loads and caches ConvAEC checkpoint on CPU keyed by resolved file path."""
        model_path = self.get_model_path(dataset, entity, 0)
        if not model_path or not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found in pretrain/ for {dataset}/{entity}")

        if model_path in self.model_cache:
            return self.model_cache[model_path]

        n_features = 1
        if dataset == "smd":
            n_features = 38
        elif dataset == "smap":
            n_features = 25
        elif dataset == "msl":
            n_features = 55

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
            classes=12,
            classifier_dim=32,
            c_loss_ratio=0.1,
            apply_anomaly_mask=True,
            label_smoothing=True,
            alpha=0.1,
            beta=0.01,
            fix_double_softmax=False,
            epoch=100,
            lr=0.001,
        )

        model = ConvAEC(params)
        state_dict = torch.load(model_path, map_location='cpu', weights_only=False)
        model.load_state_dict(state_dict)
        model.eval()

        self.model_cache[model_path] = (model, params)
        return model, params

    def _run_batched_inference(self, model: ConvAEC, windows: np.ndarray, batch_size: int = 512) -> Tuple[np.ndarray, np.ndarray]:
        """Executes batched CPU inference over sliding windows to prevent memory spikes."""
        hats, outs = [], []
        with torch.no_grad():
            for i in range(0, len(windows), batch_size):
                batch_t = torch.from_numpy(windows[i : i + batch_size])
                x_hat, x_out, _ = model(batch_t)
                hats.append(x_hat.cpu().numpy())
                outs.append(x_out.cpu().numpy())
        return np.concatenate(hats, axis=0), np.concatenate(outs, axis=0)

    def _resolve_paper_metrics(
        self,
        dataset: str,
        entity: str,
        scores: np.ndarray,
        gt_aligned: Optional[np.ndarray],
        window: int,
        step: int,
    ) -> Optional[Dict[str, float]]:
        """
        Returns VUS-ROC, VUS-PR, Range-F (mean+3std), RF (oracle), and R-AUC
        under D:/REDLAMP-danh/REDLAMP-main/evaluate.py ('paper' protocol),
        cached to metrics/paper_eval_cache.json for instant repeat loads.
        """
        cache_key = f"{dataset}:{entity}:paper"
        if cache_key in self.eval_cache:
            return self.eval_cache[cache_key]

        res: Optional[Dict[str, float]] = None
        if dataset == "stock" and entity in self.stock_metrics:
            base_m = dict(self.stock_metrics[entity])
            rf_oracle = base_m["rf"]
            if gt_aligned is not None and len(gt_aligned) == len(scores) and np.sum(gt_aligned) > 0:
                grader = PaperMetricor()
                rf_oracle = compute_rf_oracle(grader, (gt_aligned > 0).astype(int), scores, n_thresh=15)
            res = {
                "vus_roc": float(base_m["vus_roc"]),
                "vus_pr": float(base_m["vus_pr"]),
                "rf": float(base_m["rf"]),
                "rf_oracle": float(rf_oracle),
            }
        elif gt_aligned is not None and len(gt_aligned) == len(scores) and np.sum(gt_aligned) > 0:
            res = compute_paper_metrics(scores, gt_aligned, window=window, step=step, compute_oracle=True)

        if res is not None:
            self.eval_cache[cache_key] = res
            save_eval_cache(self.eval_cache_path, self.eval_cache)
        return res

    def load_entity_data(self, dataset: str, entity: str, seed: int = 0) -> Dict[str, Any]:
        """
        Loads entity test_all/*.npy when available, or evaluates live on CPU using
        the entity's real dataset series inside D:/repo/redlamp/dataset.
        """
        key = (dataset, entity)
        if key in self.data_cache:
            return self.data_cache[key]

        model, params = self.load_model(dataset, entity, 0)
        W = params.n_time
        D = params.n_features
        test_dir = self.get_test_dir(dataset, entity, 0)

        gt_labels = None
        eval_step = 1

        if test_dir is not None:
            anomaly_score = np.load(os.path.join(test_dir, "anomaly_score.npy"))
            inp_last = None
            input_3d = None
            if os.path.exists(os.path.join(test_dir, "input_last.npy")):
                inp_last = np.load(os.path.join(test_dir, "input_last.npy"))
            if os.path.exists(os.path.join(test_dir, "input.npy")):
                input_3d = np.load(os.path.join(test_dir, "input.npy"))
                if inp_last is None:
                    inp_last = input_3d[:, -1, :]

            if os.path.exists(os.path.join(test_dir, "mse.npy")):
                mse = np.load(os.path.join(test_dir, "mse.npy"))
            elif input_3d is not None and os.path.exists(os.path.join(test_dir, "pred.npy")):
                pred_3d = np.load(os.path.join(test_dir, "pred.npy"))
                mse = np.mean((input_3d - pred_3d) ** 2, axis=(1, 2))
            else:
                mse = anomaly_score.copy()

            pred_label = np.load(os.path.join(test_dir, "pred_label.npy"))
            label = np.load(os.path.join(test_dir, "label.npy")) if os.path.exists(os.path.join(test_dir, "label.npy")) else None

            if dataset == "iops":
                iops_file = os.path.join(self.dataset_dir, "IOPS", f"{entity}.test.out")
                if os.path.exists(iops_file):
                    df_i = pd.read_csv(iops_file, header=None, names=["Value", "Label"])
                    gt_raw = df_i["Label"].values[-(len(anomaly_score) + W - 1):]
                    gt_labels = align_labels_centre(gt_raw, len(anomaly_score), window=W, step=1)
            elif dataset == "stock":
                stock_file = os.path.join(self.dataset_dir, "stock", f"{entity}.csv")
                if os.path.exists(stock_file):
                    df_s = pd.read_csv(stock_file)
                    if "Label" in df_s.columns:
                        gt_raw = df_s["Label"].values[-(len(anomaly_score) + W - 1):]
                        gt_labels = align_labels_centre(gt_raw, len(anomaly_score), window=W, step=1)
        else:
            # Evaluate live from dataset/
            gt_full = None
            if dataset == "smd":
                te_path = os.path.join(self.dataset_dir, "ServerMachineDataset", "test", f"{entity}.txt")
                lbl_path = os.path.join(self.dataset_dir, "ServerMachineDataset", "test_label", f"{entity}.txt")
                if os.path.exists(te_path):
                    series_norm = np.loadtxt(te_path, delimiter=",", dtype=np.float32)
                    if os.path.exists(lbl_path):
                        gt_full = np.loadtxt(lbl_path, delimiter=",", dtype=int)
                else:
                    sample_csv = os.path.join(self.dataset_dir, "samples", "sample_smd_machine_1_1.csv")
                    df_smd = pd.read_csv(sample_csv)
                    feat_cols = [c for c in df_smd.columns if c.lower() != "label"][:D]
                    series_norm = df_smd[feat_cols].values.astype(np.float32)
                    gt_full = df_smd["Label"].values.astype(int) if "Label" in df_smd.columns else None

            elif dataset == "iops":
                tr_file = os.path.join(self.dataset_dir, "IOPS", f"{entity}.train.out")
                te_file = os.path.join(self.dataset_dir, "IOPS", f"{entity}.test.out")
                if not os.path.exists(te_file):
                    raise FileNotFoundError(f"IOPS test file not found for {entity}")
                df_te = pd.read_csv(te_file, header=None, names=["Value", "Label"])
                te_vals = df_te["Value"].values.astype(np.float32).reshape(-1, 1)
                if os.path.exists(tr_file):
                    df_tr = pd.read_csv(tr_file, header=None, names=["Value", "Label"])
                    scaler = MinMaxScaler().fit(df_tr["Value"].values.astype(np.float32).reshape(-1, 1))
                else:
                    scaler = MinMaxScaler().fit(te_vals[:500])
                series_norm = scaler.transform(te_vals).astype(np.float32)
                gt_full = df_te["Label"].values.astype(int)

            elif dataset in ("msl", "smap"):
                tr_path = os.path.join(self.dataset_dir, "NASA", "train", f"{entity}.npy")
                te_path = os.path.join(self.dataset_dir, "NASA", "test", f"{entity}.npy")
                if not os.path.exists(te_path):
                    raise FileNotFoundError(f"NASA data not found for channel {entity}")
                te_raw = np.load(te_path).astype(np.float32)
                if os.path.exists(tr_path):
                    tr_raw = np.load(tr_path).astype(np.float32)
                    scaler = MinMaxScaler().fit(tr_raw)
                    series_norm = scaler.transform(te_raw).astype(np.float32)
                else:
                    series_norm = MinMaxScaler().fit_transform(te_raw).astype(np.float32)

                nasa_meta = self._load_nasa_meta()
                row = nasa_meta[nasa_meta["chan_id"] == entity]
                gt_full = np.zeros(len(series_norm), dtype=int)
                if not row.empty:
                    seqs = ast.literal_eval(row["anomaly_sequences"].values[0])
                    for s, e in seqs:
                        gt_full[max(0, s):min(len(gt_full), e + 1)] = 1

            elif dataset == "stock":
                stock_file = os.path.join(self.dataset_dir, "stock", f"{entity}.csv")
                if not os.path.exists(stock_file):
                    raise FileNotFoundError(f"Stock file not found for {entity}")
                df_s = pd.read_csv(stock_file)
                m_tr = re.search(r"_tr_(\d+)_", entity)
                train_end = int(m_tr.group(1)) if m_tr else 500
                all_vals = df_s["Data"].values.astype(np.float32).reshape(-1, 1)
                scaler = MinMaxScaler().fit(all_vals[:train_end])
                series_norm = scaler.transform(all_vals[train_end:]).astype(np.float32)
                gt_full = df_s["Label"].values[train_end:].astype(int) if "Label" in df_s.columns else None

            else:
                raise FileNotFoundError(f"Unsupported dataset: {dataset}")

            step = 10
            eval_step = step
            if len(series_norm) < W:
                pad_n = W - len(series_norm)
                series_norm = np.vstack([np.tile(series_norm[0:1], (pad_n, 1)), series_norm])
                if gt_full is not None:
                    gt_full = np.concatenate([np.zeros(pad_n, dtype=int), gt_full])

            input_3d = np.lib.stride_tricks.sliding_window_view(series_norm, (W, D)).squeeze(1)[::step].copy()
            inp_last = input_3d[:, -1, :]
            if gt_full is not None:
                gt_labels = align_labels_centre(gt_full, len(input_3d), window=W, step=step)

            pred_3d, pred_label = self._run_batched_inference(model, input_3d)
            mse = np.mean((input_3d - pred_3d) ** 2, axis=(1, 2))
            anomaly_score = anomaly_scoreing(input_3d, pred_3d, pred_label, threshold=0.05)
            label = None

        mean_label = np.mean(pred_label, axis=0)
        indices = np.where(mean_label > 0.05)[0]
        if 0 not in indices:
            indices = np.insert(indices, 0, 0)

        l_copy = np.copy(pred_label)
        l_copy[:, indices] = 0
        ce_score = np.sum(l_copy, axis=1)
        raw_score = (mse + ce_score) / 2.0

        th_995 = float(np.percentile(raw_score, 99.5))
        th_990 = float(np.percentile(raw_score, 99.0))
        th_950 = float(np.percentile(raw_score, 95.0))

        max_idx = int(np.argmax(anomaly_score))
        low_score_indices = np.where(anomaly_score < np.percentile(anomaly_score, 10))[0]
        normal_idx = int(low_score_indices[len(low_score_indices) // 2]) if len(low_score_indices) > 0 else 0

        feat_min = np.min(inp_last, axis=0).tolist()
        feat_max = np.max(inp_last, axis=0).tolist()
        feat_median = np.median(inp_last, axis=0).tolist()

        computed_metrics = self._resolve_paper_metrics(
            dataset=dataset,
            entity=entity,
            scores=anomaly_score,
            gt_aligned=gt_labels,
            window=W,
            step=eval_step,
        )

        data_dict = {
            "test_dir": test_dir or "live_dataset_eval",
            "length": len(anomaly_score),
            "anomaly_score": anomaly_score,
            "mse": mse,
            "pred_label": pred_label,
            "inp_last": inp_last,
            "input_3d": input_3d,
            "label": label,
            "indices": indices.tolist(),
            "mean_label": mean_label.tolist(),
            "raw_score": raw_score,
            "threshold_995": th_995,
            "threshold_990": th_990,
            "threshold_950": th_950,
            "default_threshold": th_995,
            "max_anomaly_idx": max_idx,
            "normal_idx": normal_idx,
            "feat_min": feat_min,
            "feat_max": feat_max,
            "feat_median": feat_median,
            "computed_metrics": computed_metrics,
            "paper_ref": PAPER_REFERENCE.get(dataset),
            "metrics_is_vus": True,
        }
        self.data_cache[key] = data_dict
        return data_dict

    def get_window(self, data_dict: Dict[str, Any], t: int) -> np.ndarray:
        if data_dict["input_3d"] is not None:
            t_clamped = max(0, min(t, len(data_dict["input_3d"]) - 1))
            return data_dict["input_3d"][t_clamped]

        inp_last = data_dict["inp_last"]
        N, _ = inp_last.shape
        t_clamped = max(0, min(t, N - 1))
        start = t_clamped - 99
        if start >= 0:
            return inp_last[start : t_clamped + 1]
        pad_count = -start
        pad = np.tile(inp_last[0:1], (pad_count, 1))
        actual = inp_last[0 : t_clamped + 1]
        return np.vstack([pad, actual])

    def predict_point(
        self,
        dataset: str,
        entity: str,
        seed: int,
        point: List[float],
        context_type: str = "sample_last",
        custom_history: Optional[List[List[float]]] = None,
        threshold_override: Optional[float] = None,
    ) -> Dict[str, Any]:
        model, params = self.load_model(dataset, entity, 0)
        data_dict = self.load_entity_data(dataset, entity, 0)

        D = params.n_features
        pt = np.array(point[:D] if len(point) >= D else point + [0.0] * (D - len(point)), dtype=np.float32).reshape(1, D)

        if context_type == "sample_last":
            if data_dict["input_3d"] is not None:
                context = data_dict["input_3d"][-1, 1:, :]
            else:
                context = data_dict["inp_last"][-99:, :]
                if len(context) < 99:
                    pad = np.tile(context[0:1], (99 - len(context), 1))
                    context = np.vstack([pad, context])
        elif context_type == "median":
            median = np.array(data_dict["feat_median"], dtype=np.float32).reshape(1, D)
            context = np.tile(median, (99, 1))
        elif context_type == "custom" and custom_history:
            c_arr = np.array(custom_history, dtype=np.float32)
            if c_arr.ndim == 1:
                c_arr = c_arr.reshape(-1, D)
            if len(c_arr) >= 99:
                context = c_arr[-99:, :D]
            else:
                pad = np.tile(c_arr[0:1, :D], (99 - len(c_arr), 1))
                context = np.vstack([pad, c_arr[:, :D]])
        else:
            median = np.array(data_dict["feat_median"], dtype=np.float32).reshape(1, D)
            context = np.tile(median, (99, 1))

        window = np.vstack([context, pt])
        window_tensor = torch.tensor(window, dtype=torch.float32).unsqueeze(0)

        with torch.no_grad():
            x_hat, x_out, _ = model(window_tensor)

        reconstructed = x_hat.squeeze(0).cpu().numpy()
        pred_probs = x_out.squeeze(0).cpu().numpy()

        raw_mse = float(np.mean((window - reconstructed) ** 2))
        indices = set(data_dict["indices"])
        raw_ce = float(sum(pred_probs[j] for j in range(12) if j not in indices))
        raw_combined = float((raw_mse + raw_ce) / 2.0)

        th = threshold_override if threshold_override is not None else data_dict["default_threshold"]
        is_anomaly = raw_combined > th

        allowed_classes = [
            {"index": j, "label": ANOMALY_TYPES[j], "name_vi": PSEUDO_ANOMALY_INFO[j]["name_vi"], "prob": float(pred_probs[j])}
            for j in range(12) if j not in indices
        ]
        allowed_classes.sort(key=lambda x: x["prob"], reverse=True)
        top3 = allowed_classes[:3]

        if is_anomaly:
            winner_idx = allowed_classes[0]["index"] if allowed_classes else int(np.argmax(pred_probs))
        else:
            winner_idx = 0
        winner_meta = PSEUDO_ANOMALY_INFO[winner_idx]
        predicted_group = {
            "index": winner_idx,
            "name": winner_meta["name"],
            "name_vi": winner_meta["name_vi"],
            "desc_vi": winner_meta["desc_vi"],
            "prob": float(pred_probs[winner_idx]),
            "is_anomaly": is_anomaly,
            "reason": (
                f"Đạt xác suất cao nhất ({pred_probs[winner_idx]*100:.1f}%) trong các lớp bất thường hợp lệ"
                if is_anomaly else "Điểm kết hợp thô nằm dưới ngưỡng phân vị 99,5%, tín hiệu ổn định."
            ),
        }

        all_classes = []
        for j in range(12):
            meta = PSEUDO_ANOMALY_INFO[j]
            is_ex = j in indices
            r_str = ""
            if is_ex:
                r_str = "Lớp bình thường (luôn loại trừ)" if j == 0 else f"Xác suất trung bình toàn chuỗi ({data_dict['mean_label'][j]:.3f}) > ngưỡng 0,05"
            all_classes.append({
                "index": j,
                "name": meta["name"],
                "name_vi": meta["name_vi"],
                "desc_vi": meta["desc_vi"],
                "prob": float(pred_probs[j]),
                "excluded": is_ex,
                "reason": r_str,
                "is_winner": (j == winner_idx),
            })

        excluded_info = []
        for idx in sorted(list(indices)):
            label_name = ANOMALY_TYPES[idx]
            reason = (
                "Lớp bình thường (luôn loại trừ)"
                if idx == 0 else f"Xác suất trung bình toàn chuỗi ({data_dict['mean_label'][idx]:.3f}) > ngưỡng 0,05"
            )
            excluded_info.append({
                "index": idx,
                "label": label_name,
                "prob": float(pred_probs[idx]),
                "reason": reason,
            })

        return {
            "raw_mse": raw_mse,
            "raw_ce": raw_ce,
            "raw_combined": raw_combined,
            "threshold": th,
            "is_anomaly": is_anomaly,
            "conclusion": "BẤT THƯỜNG" if is_anomaly else "BÌNH THƯỜNG",
            "predicted_group": predicted_group,
            "all_classes": all_classes,
            "top3": top3,
            "excluded_classes": excluded_info,
            "window_input": window.tolist(),
            "custom_window": window.tolist(),
            "reconstructed": reconstructed.tolist(),
            "new_point": point,
            "explanation": f"MSE đạt {raw_mse:.4f}, điểm phân loại {raw_ce:.4f}, ngưỡng {th:.4f} (phân vị 99,5).",
        }

    def explain(
        self,
        dataset: str,
        entity: str,
        seed: int,
        t: Optional[int] = None,
        custom_window: Optional[List[List[float]]] = None,
        point: Optional[List[float]] = None,
        is_custom_point: bool = False,
    ) -> Dict[str, Any]:
        model, params = self.load_model(dataset, entity, 0)
        data_dict = self.load_entity_data(dataset, entity, 0)
        indices = set(data_dict["indices"])

        normal_t = data_dict["normal_idx"]
        win_normal = self.get_window(data_dict, normal_t)

        if is_custom_point and custom_window is not None:
            win_target = np.array(custom_window, dtype=np.float32)
            t = 99
        else:
            if t is None:
                t = data_dict["max_anomaly_idx"]
            t = max(0, min(t, data_dict["length"] - 1))
            win_target = self.get_window(data_dict, t)

        activations_target: Dict[str, np.ndarray] = {}
        hook_shapes: List[Tuple[str, List[int]]] = []
        hooks = []
        for i, blk in enumerate(model.encoder.network):
            def make_hook(idx, name):
                def hook(m, inp, outp):
                    activations_target[name] = outp.detach().cpu().numpy()
                    hook_shapes.append((f"ConvBlock {idx} (stride 2)", list(outp.shape)))
                return hook
            hooks.append(blk.register_forward_hook(make_hook(i, f"conv_{i}")))

        win_t_tensor = torch.tensor(win_target, dtype=torch.float32).unsqueeze(0)
        win_n_tensor = torch.tensor(win_normal, dtype=torch.float32).unsqueeze(0)

        with torch.no_grad():
            x_hat_t, x_out_t, x_enc_t = model(win_t_tensor)

        for h in hooks:
            h.remove()

        with torch.no_grad():
            x_hat_n, x_out_n, _ = model(win_n_tensor)

        rec_target = x_hat_t.squeeze(0).cpu().numpy()
        rec_normal = x_hat_n.squeeze(0).cpu().numpy()
        probs_target = x_out_t.squeeze(0).cpu().numpy()
        probs_normal = x_out_n.squeeze(0).cpu().numpy()
        embedding_target = x_enc_t.squeeze().cpu().numpy().tolist()

        conv_shapes = [{"layer": "Cửa sổ đầu vào", "shape": f"[1, {params.n_time}, {params.n_features}]"}]
        for lname, shp in hook_shapes:
            conv_shapes.append({"layer": lname, "shape": str(shp)})
        if hook_shapes:
            last_ch = hook_shapes[-1][1][1]
            conv_shapes.append({"layer": "MaxPool1D (to length 1)", "shape": f"[1, {last_ch}, 1]"})
        conv_shapes.append({"layer": "Conv1x1 -> Embedding", "shape": str(list(x_enc_t.shape))})

        conv_heatmap_summary = {}
        for k, v in activations_target.items():
            conv_heatmap_summary[k] = np.mean(np.abs(v[0]), axis=1).tolist()[:32]

        err_sq_target = np.mean((win_target - rec_target) ** 2, axis=1).tolist()
        err_sq_normal = np.mean((win_normal - rec_normal) ** 2, axis=1).tolist()
        mse_target = float(np.mean(err_sq_target))
        mse_normal = float(np.mean(err_sq_normal))

        raw_mse_val = mse_target
        raw_ce_val = float(sum(probs_target[j] for j in range(12) if j not in indices))
        raw_comb_val = float((raw_mse_val + raw_ce_val) / 2.0)
        th = data_dict["default_threshold"]
        is_anomaly = raw_comb_val > th

        if is_anomaly:
            allowed_cand = [j for j in range(12) if j not in indices]
            winner_idx = max(allowed_cand, key=lambda j: probs_target[j]) if allowed_cand else int(np.argmax(probs_target))
        else:
            winner_idx = 0
        winner_meta = PSEUDO_ANOMALY_INFO[winner_idx]

        classes_target = []
        classes_normal = []
        for j in range(12):
            is_ex = j in indices
            r_str = ""
            if is_ex:
                r_str = "Lớp bình thường" if j == 0 else f"Trung bình chuỗi ({data_dict['mean_label'][j]:.3f}) > 0.05"
            classes_target.append({
                "label": ANOMALY_TYPES[j],
                "name_vi": PSEUDO_ANOMALY_INFO[j]["name_vi"],
                "desc_vi": PSEUDO_ANOMALY_INFO[j]["desc_vi"],
                "prob": float(probs_target[j]),
                "excluded": is_ex,
                "reason": r_str,
                "is_winner": (j == winner_idx),
            })
            classes_normal.append({
                "label": ANOMALY_TYPES[j],
                "name_vi": PSEUDO_ANOMALY_INFO[j]["name_vi"],
                "desc_vi": PSEUDO_ANOMALY_INFO[j]["desc_vi"],
                "prob": float(probs_normal[j]),
                "excluded": is_ex,
                "reason": r_str,
                "is_winner": (j == 0),
            })

        if is_custom_point:
            time_axis = list(range(100))
            input_slice = win_target[:, 0].tolist()
            history_len = min(50, len(data_dict["raw_score"]))
            score_slice_rec = data_dict["mse"][-history_len:].tolist() + [raw_mse_val]
            l_sub = np.copy(data_dict["pred_label"][-history_len:])
            l_sub[:, list(indices)] = 0
            score_slice_ce = np.sum(l_sub, axis=1).tolist() + [raw_ce_val]
            raw_slice_combined = data_dict["raw_score"][-history_len:].tolist() + [raw_comb_val]
            score_slice_final = data_dict["anomaly_score"][-history_len:].tolist() + [min(1.0, raw_comb_val / max(1e-5, th * 1.5))]
            final_rel_val = score_slice_final[-1]

            explanations = [
                "Cửa sổ 100 điểm với điểm nạp mới tại vị trí t=99 được đưa vào phân tích.",
                "Embedding 128 chiều nén đặc trưng không gian của cửa sổ điểm nạp qua các tầng tích chập.",
                f"Sai số tái tạo tại điểm nạp MSE = {mse_target:.4f} (cửa sổ chuẩn đối chứng là {mse_normal:.4f}).",
                f"Điểm nạp được phân loại vào nhóm bất thường giả '{winner_meta['name_vi']}' đạt xác suất {probs_target[winner_idx]*100:.1f}%.",
                f"Điểm kết hợp {raw_comb_val:.3f} ({'vượt ngưỡng ' + f'{th:.3f} (bất thường)' if is_anomaly else 'dưới ngưỡng ' + f'{th:.3f} (chuẩn)'}), phân loại giả lập tham khảo."
            ]
        else:
            slice_start = max(0, t - 150)
            slice_end = min(data_dict["length"], t + 150)
            time_axis = list(range(slice_start, slice_end))
            input_slice = data_dict["inp_last"][slice_start:slice_end, 0].tolist()

            score_slice_rec = data_dict["mse"][slice_start:slice_end].tolist()
            l_sub = np.copy(data_dict["pred_label"][slice_start:slice_end])
            l_sub[:, list(indices)] = 0
            score_slice_ce = np.sum(l_sub, axis=1).tolist()
            score_slice_final = data_dict["anomaly_score"][slice_start:slice_end].tolist()
            raw_slice_combined = data_dict["raw_score"][slice_start:slice_end].tolist()
            final_rel_val = float(data_dict["anomaly_score"][t])

            explanations = [
                f"Cửa sổ 100 điểm tại vị trí t={t} được tô sáng trên chuỗi dữ liệu gốc.",
                "Embedding 128 chiều biểu diễn đặc trưng nén của cửa sổ sau 4 tầng tích chập.",
                f"Sai số tái tạo MSE = {mse_target:.4f} ở cửa sổ khảo sát (so với {mse_normal:.4f} ở cửa sổ chuẩn).",
                "Phân loại xác suất 12 lớp bất thường giả định, loại bỏ lớp bình thường và lớp nhiễu.",
                f"Điểm cuối = ({raw_mse_val:.3f} + {raw_ce_val:.3f})/2 = {raw_comb_val:.3f}, đối chiếu ngưỡng phân vị 99,5 ({th:.3f})."
            ]

        return {
            "t": t,
            "normal_t": normal_t,
            "is_custom_point": is_custom_point,
            "new_point": point,
            "winner_group": {
                "index": winner_idx,
                "name": winner_meta["name"],
                "name_vi": winner_meta["name_vi"],
                "desc_vi": winner_meta["desc_vi"],
                "prob": float(probs_target[winner_idx]),
                "is_anomaly": is_anomaly,
            },
            "window_size": params.n_time,
            "n_features": params.n_features,
            "time_slice": time_axis,
            "input_slice": input_slice,
            "win_target": win_target[:, 0].tolist(),
            "win_normal": win_normal[:, 0].tolist(),
            "rec_target": rec_target[:, 0].tolist(),
            "rec_normal": rec_normal[:, 0].tolist(),
            "err_sq_target": err_sq_target,
            "err_sq_normal": err_sq_normal,
            "mse_target": mse_target,
            "mse_normal": mse_normal,
            "conv_shapes": conv_shapes,
            "conv_heatmap": conv_heatmap_summary,
            "embedding": embedding_target,
            "classes_target": classes_target,
            "classes_normal": classes_normal,
            "score_rec_slice": score_slice_rec,
            "score_ce_slice": score_slice_ce,
            "score_final_slice": score_slice_final,
            "raw_comb_slice": raw_slice_combined,
            "threshold": th,
            "raw_mse": float(raw_mse_val),
            "raw_ce": raw_ce_val,
            "raw_combined": raw_comb_val,
            "final_relative": final_rel_val,
            "explanations": explanations,
        }
