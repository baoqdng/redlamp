import os
import sys
import glob
import math
import numpy as np
import torch
import torch.nn as nn
from typing import Dict, Any, List, Optional, Tuple

# Add project root and REDLAMP candidates to sys.path
_CANDIDATE_PATHS = [
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")),
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "REDLAMP-main")),
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "RedLamp")),
    os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "REDLAMP-main")),
    os.path.abspath(os.path.join(os.getcwd(), "REDLAMP-main")),
    os.path.abspath(os.path.join(os.getcwd(), "RedLamp")),
    os.getcwd(),
]
REDLAMP_PATH = next((p for p in _CANDIDATE_PATHS if os.path.exists(p)), _CANDIDATE_PATHS[0])
if REDLAMP_PATH not in sys.path:
    sys.path.insert(0, REDLAMP_PATH)

from index import ensure_kaggle_file, get_default_result_dir
import utils
from models.meta import ConvAEC

ANOMALY_TYPES = [
    'normal', 'spike', 'flip', 'speedup', 'noise', 'cutoff',
    'average', 'scale', 'wander', 'contextual', 'upsidedown', 'mixture'
]

PSEUDO_ANOMALY_INFO = {
    0: {
        "name": "normal",
        "name_vi": "Normal (Bình thường)",
        "desc_vi": "Tín hiệu hoạt động ổn định, không có biến dạng Pseudo-Anomaly."
    },
    1: {
        "name": "spike",
        "name_vi": "Spike (Đột biến đỉnh nhọn)",
        "desc_vi": "Biến động tăng/giảm biên độ đột biến cục bộ tại 1–2 bước thời gian."
    },
    2: {
        "name": "flip",
        "name_vi": "Flip (Đảo chiều đoạn sóng)",
        "desc_vi": "Thứ tự thời gian của phân đoạn tín hiệu bị đảo ngược so với chuẩn."
    },
    3: {
        "name": "speedup",
        "name_vi": "Speedup (Biến đổi tần số)",
        "desc_vi": "Chu kỳ hoặc tần số dao động của chuỗi tăng/giảm đột ngột."
    },
    4: {
        "name": "noise",
        "name_vi": "Noise (Nhiễu Gaussian)",
        "desc_vi": "Biên độ bị xáo trộn bởi nhiễu trắng ngẫu nhiên cường độ lớn."
    },
    5: {
        "name": "cutoff",
        "name_vi": "Cutoff (Chặn ngưỡng biên độ)",
        "desc_vi": "Tín hiệu bị giữ phẳng ở mức cố định (Clipping / Saturation)."
    },
    6: {
        "name": "average",
        "name_vi": "Average (Moving Average)",
        "desc_vi": "Tín hiệu bị làm trơn quá mức, mất dao động chi tiết."
    },
    7: {
        "name": "scale",
        "name_vi": "Scale (Co giãn biên độ)",
        "desc_vi": "Biên độ phân đoạn bị phóng đại hoặc thu nhỏ bất thường."
    },
    8: {
        "name": "wander",
        "name_vi": "Wander (Baseline Drift)",
        "desc_vi": "Đường nền (Baseline) trôi lệch dần khỏi mức cân bằng chuẩn."
    },
    9: {
        "name": "contextual",
        "name_vi": "Contextual (Bất thường ngữ cảnh)",
        "desc_vi": "Giá trị vẫn trong dải cho phép nhưng lệch pha so với ngữ cảnh xung quanh."
    },
    10: {
        "name": "upsidedown",
        "name_vi": "Upside-down (Đảo ngược biên độ)",
        "desc_vi": "Đỉnh và đáy sóng bị lật đối xứng qua giá trị trung bình của đoạn."
    },
    11: {
        "name": "mixture",
        "name_vi": "Mixture (Ghép trộn phân đoạn)",
        "desc_vi": "Phân đoạn tín hiệu từ thời điểm khác bị chèn lệch pha vào cửa sổ hiện tại."
    }
}

class RedLampEngine:
    def __init__(self, result_dir: Optional[str] = None):
        self.result_dir = os.path.abspath(result_dir or get_default_result_dir())
        self.model_cache: Dict[Tuple[str, str, int], Any] = {}
        self.data_cache: Dict[Tuple[str, str, int], Dict[str, Any]] = {}
        self.spike_cache: Dict[Tuple[str, str, int], List[float]] = {}

    def _resolve_entity(self, dataset: str, entity: str) -> str:
        if entity and entity.upper() != "ALL":
            return entity
        defaults = {
            "smd": "machine-1-1",
            "iops": "KPI-05f10d3a-239c-3bef-9bdc-a2feeb0037aa",
            "aiops": "KPI-05f10d3a-239c-3bef-9bdc-a2feeb0037aa",
            "msl": "C-1",
            "smap": "A-1",
            "anomaly_archive": "001",
        }
        return defaults.get(dataset, entity)

    def get_model_path(self, dataset: str, entity: str, seed: int) -> Optional[str]:
        entity = self._resolve_entity(dataset, entity)
        # 1. Search in result_dir
        if dataset in ["msl", "smap"]:
            rel = f"{dataset}/d1_b128_w100_s10/{seed}/bestmodel.pkl"
            p = ensure_kaggle_file(self.result_dir, rel)
            if p and os.path.exists(p):
                return p
        elif dataset in ["iops", "aiops"]:
            rel = f"aiops/{entity}/d1_b128_w100_s10/{seed}/bestmodel.pkl"
            p = ensure_kaggle_file(self.result_dir, rel)
            if p and os.path.exists(p):
                return p
        elif dataset == "smd":
            rel = f"smd/{entity}/d1_b128_w100_s10/{seed}/bestmodel.pkl"
            p = ensure_kaggle_file(self.result_dir, rel)
            if p and os.path.exists(p):
                return p
        elif dataset == "anomaly_archive":
            pattern = os.path.join(self.result_dir, "anomaly_archive", entity, "**", "bestmodel.pkl")
            matches = glob.glob(pattern, recursive=True)
            if matches:
                return matches[0]

        # 2. Fallback search in pretrain folders
        base_parent = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
        pretrain_dirs = [
            os.path.join(base_parent, "pretrain"),
            os.path.join(self.result_dir, "pretrain"),
            os.path.join(os.getcwd(), "pretrain"),
        ]
        for pre_dir in pretrain_dirs:
            if not os.path.exists(pre_dir):
                continue
            candidates = [
                os.path.join(pre_dir, dataset, entity, "d1_b128_w100_s10", str(seed), "bestmodel.pkl"),
                os.path.join(pre_dir, dataset, entity, "d1_b128_w100_s1", str(seed), "bestmodel.pkl"),
                os.path.join(pre_dir, dataset, dataset, "d1_b128_w100_s10", str(seed), "bestmodel.pkl"),
                os.path.join(pre_dir, "aiops" if dataset == "iops" else "iops", entity, "d1_b128_w100_s10", str(seed), "bestmodel.pkl"),
            ]
            for c in candidates:
                if os.path.exists(c):
                    return c
            m = glob.glob(os.path.join(pre_dir, dataset, entity, "**", "bestmodel.pkl"), recursive=True)
            if m:
                return m[0]
            m_ds = glob.glob(os.path.join(pre_dir, dataset, "**", "bestmodel.pkl"), recursive=True)
            if m_ds:
                return m_ds[0]

        return None

    def _ensure_test_files(self, rel_dir: str) -> Optional[str]:
        local_dir = os.path.join(self.result_dir, *rel_dir.split("/"))
        if os.path.exists(os.path.join(local_dir, "anomaly_score.npy")):
            return local_dir
        required_files = ["anomaly_score.npy", "pred_label.npy"]
        for fname in required_files:
            fpath = os.path.join(local_dir, fname)
            if not os.path.exists(fpath) or os.path.getsize(fpath) == 0:
                ensure_kaggle_file(self.result_dir, f"{rel_dir}/{fname}")
        if not os.path.exists(os.path.join(local_dir, "input_last.npy")) and not os.path.exists(os.path.join(local_dir, "input.npy")):
            ensure_kaggle_file(self.result_dir, f"{rel_dir}/input_last.npy")
        if os.path.exists(os.path.join(local_dir, "anomaly_score.npy")):
            return local_dir
        return None

    def get_test_dir(self, dataset: str, entity: str, seed: int) -> Optional[str]:
        entity = self._resolve_entity(dataset, entity)
        # 1. Search in result_dir
        if dataset in ["msl", "smap"]:
            rel_dir = f"{dataset}/d1_b128_w100_s10/{seed}/test_each/{entity}/test_all"
            d = self._ensure_test_files(rel_dir)
            if d and os.path.exists(d):
                return d
            d_all = os.path.join(self.result_dir, dataset, "d1_b128_w100_s10", str(seed), "test_all")
            if os.path.exists(d_all):
                return d_all
        elif dataset in ["iops", "aiops"]:
            rel_dir = f"aiops/{entity}/d1_b128_w100_s10/{seed}/test_all"
            d = self._ensure_test_files(rel_dir)
            if d and os.path.exists(d):
                return d
        elif dataset == "smd":
            rel_dir = f"smd/{entity}/d1_b128_w100_s10/{seed}/test_all"
            d = self._ensure_test_files(rel_dir)
            if d and os.path.exists(d):
                return d
        elif dataset == "anomaly_archive":
            pattern = os.path.join(self.result_dir, "anomaly_archive", entity, "**", "test_all")
            matches = glob.glob(pattern, recursive=True)
            if matches:
                return matches[0]

        # 2. Fallback search in pretrain folders
        base_parent = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
        pretrain_dirs = [
            os.path.join(base_parent, "pretrain"),
            os.path.join(self.result_dir, "pretrain"),
            os.path.join(os.getcwd(), "pretrain"),
        ]
        for pre_dir in pretrain_dirs:
            if not os.path.exists(pre_dir):
                continue
            candidates = [
                os.path.join(pre_dir, dataset, entity, "d1_b128_w100_s10", str(seed), "test_all"),
                os.path.join(pre_dir, dataset, entity, "d1_b128_w100_s1", str(seed), "test_all"),
                os.path.join(pre_dir, dataset, dataset, "d1_b128_w100_s10", str(seed), "test_all"),
                os.path.join(pre_dir, "aiops" if dataset == "iops" else "iops", entity, "d1_b128_w100_s10", str(seed), "test_all"),
            ]
            for c in candidates:
                if os.path.exists(c):
                    return c
            m = glob.glob(os.path.join(pre_dir, dataset, entity, "**", "test_all"), recursive=True)
            if m:
                return m[0]
            m_ds = glob.glob(os.path.join(pre_dir, dataset, "**", "test_all"), recursive=True)
            if m_ds:
                return m_ds[0]

        return None

    def load_model(self, dataset: str, entity: str, seed: int) -> Tuple[ConvAEC, utils.AttrDict]:
        entity = self._resolve_entity(dataset, entity)
        key = (dataset, entity, seed)
        if key in self.model_cache:
            return self.model_cache[key]

        model_path = self.get_model_path(dataset, entity, seed)
        if not model_path or not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found for {dataset}/{entity}/seed {seed}")

        # Determine n_features & step
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

        self.model_cache[key] = (model, params)
        return model, params

    def load_entity_data(self, dataset: str, entity: str, seed: int) -> Dict[str, Any]:
        entity = self._resolve_entity(dataset, entity)
        key = (dataset, entity, seed)
        if key in self.data_cache:
            return self.data_cache[key]

        test_dir = self.get_test_dir(dataset, entity, seed)
        if not test_dir or not os.path.exists(test_dir):
            raise FileNotFoundError(f"Test directory not found for {dataset}/{entity}/seed {seed}")

        # Load arrays
        anomaly_score = np.load(os.path.join(test_dir, "anomaly_score.npy"))
        
        # input_last or input
        inp_last = None
        input_3d = None
        if os.path.exists(os.path.join(test_dir, "input_last.npy")):
            inp_last = np.load(os.path.join(test_dir, "input_last.npy"))
        if os.path.exists(os.path.join(test_dir, "input.npy")):
            input_3d = np.load(os.path.join(test_dir, "input.npy"))
            if inp_last is None:
                inp_last = input_3d[:, -1, :]
        if inp_last is None:
            inp_last = np.expand_dims(anomaly_score, axis=-1)

        # mse
        if os.path.exists(os.path.join(test_dir, "mse.npy")):
            mse = np.load(os.path.join(test_dir, "mse.npy"))
        elif input_3d is not None and os.path.exists(os.path.join(test_dir, "pred.npy")):
            pred_3d = np.load(os.path.join(test_dir, "pred.npy"))
            mse = np.mean((input_3d - pred_3d) ** 2, axis=(1, 2))
        else:
            mse = anomaly_score.copy()

        # pred_label
        if os.path.exists(os.path.join(test_dir, "pred_label.npy")):
            pred_label = np.load(os.path.join(test_dir, "pred_label.npy"))
            mean_label = np.mean(pred_label, axis=0)
            indices = np.where(mean_label > 0.05)[0]
            if 0 not in indices:
                indices = np.insert(indices, 0, 0)
            l_copy = np.copy(pred_label)
            l_copy[:, indices] = 0
            ce_score = np.sum(l_copy, axis=1)
            raw_score = (mse + ce_score) / 2.0
        else:
            pred_label = np.zeros((len(anomaly_score), 12))
            mean_label = np.zeros(12)
            indices = np.array([0])
            ce_score = np.zeros_like(anomaly_score)
            raw_score = anomaly_score.copy()

        # Ground truth label if present
        label = None
        if os.path.exists(os.path.join(test_dir, "label.npy")):
            label = np.load(os.path.join(test_dir, "label.npy"))

        # Statistical threshold (mean + 3*std as in REDLAMP paper evaluate.py) + percentiles
        th_3std = float(np.mean(raw_score) + 3.0 * np.std(raw_score))
        th_995 = float(np.percentile(raw_score, 99.5))
        th_990 = float(np.percentile(raw_score, 99.0))
        th_950 = float(np.percentile(raw_score, 95.0))

        # Find peak anomaly window and normal window
        max_idx = int(np.argmax(anomaly_score))
        # Find a clean normal window (middle of lowest-score region)
        low_score_indices = np.where(anomaly_score < np.percentile(anomaly_score, 10))[0]
        normal_idx = int(low_score_indices[len(low_score_indices) // 2]) if len(low_score_indices) > 0 else 0

        # Statistics of features & clean normal reference point
        feat_min = np.min(inp_last, axis=0).tolist()
        feat_max = np.max(inp_last, axis=0).tolist()
        feat_median = np.median(inp_last, axis=0).tolist()
        if input_3d is not None:
            normal_point = input_3d[normal_idx, -1, :].tolist()
        else:
            normal_point = inp_last[normal_idx].tolist()

        data_dict = {
            "test_dir": test_dir,
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
            "threshold_3std": th_3std,
            "threshold_995": th_995,
            "threshold_990": th_990,
            "threshold_950": th_950,
            "default_threshold": th_3std,
            "max_anomaly_idx": max_idx,
            "normal_idx": normal_idx,
            "normal_point": normal_point,
            "feat_min": feat_min,
            "feat_max": feat_max,
            "feat_median": feat_median,
        }
        self.data_cache[key] = data_dict
        return data_dict

    def get_window(self, data_dict: Dict[str, Any], t: int) -> np.ndarray:
        """Returns window of shape (100, n_features) at time index t."""
        if data_dict["input_3d"] is not None:
            t_clamped = max(0, min(t, len(data_dict["input_3d"]) - 1))
            return data_dict["input_3d"][t_clamped]
        
        inp_last = data_dict["inp_last"]
        N, D = inp_last.shape
        t_clamped = max(0, min(t, N - 1))
        start = t_clamped - 99
        if start >= 0:
            return inp_last[start : t_clamped + 1]
        else:
            pad_count = -start
            pad = np.tile(inp_last[0:1], (pad_count, 1))
            actual = inp_last[0 : t_clamped + 1]
            return np.vstack([pad, actual])

    def get_spike_point(self, dataset: str, entity: str, seed: int = 0) -> List[float]:
        """Computes and caches a calibrated anomalous point at t=100 for Tab 3 'Mẫu đột biến'."""
        resolved = self._resolve_entity(dataset, entity)
        key = (dataset, resolved, seed)
        if key in self.spike_cache:
            return self.spike_cache[key]

        try:
            model, params = self.load_model(dataset, resolved, seed)
            d = self.load_entity_data(dataset, resolved, seed)
        except Exception:
            try:
                d = self.load_entity_data(dataset, resolved, seed)
                spike = [round(float(v) + 3.0, 4) for v in d["normal_point"]]
                self.spike_cache[key] = spike
                return spike
            except Exception:
                return [1.0]
        D = params.n_features
        digits = 4 if D == 1 else 3
        base = np.array([round(float(v), digits) for v in d["normal_point"]], dtype=np.float32)
        win_norm = self.get_window(d, d["normal_idx"])
        hist_std = np.std(win_norm[:-1, :], axis=0)
        th = float(d["default_threshold"])
        indices = set(d["indices"])
        allowed = [j for j in range(12) if j not in indices]

        def flip01(v: float) -> float:
            return 0.0 if v >= 0.5 else 1.0

        tier1: List[np.ndarray] = []
        # 1. Classic top-channel [0, 1] presets
        for k in ([min(5, D), min(3, D), min(2, D)] if D > 1 else [1]):
            p = base.copy()
            for i in range(k):
                p[i] = flip01(p[i])
            tier1.append(p)

        # 2. Active oscillating channel subsets
        active_cols = [i for i in range(D) if hist_std[i] > 1e-3]
        for k in [2, 3, 4]:
            if len(active_cols) >= k:
                p = base.copy()
                for i in active_cols[:k]:
                    p[i] = flip01(p[i])
                tier1.append(p)

        # 3. Single-channel [0, 1] flips across all features
        for i in range(D):
            p = base.copy()
            p[i] = flip01(p[i])
            tier1.append(p)
            if D == 1:
                p_alt = base.copy()
                p_alt[0] = 1.0 if p[0] == 0.0 else 0.0
                tier1.append(p_alt)

        # 4. Adjacent 2-channel [0, 1] flips
        for i in range(min(25, D - 1)):
            p = base.copy()
            p[i] = flip01(p[i])
            p[i + 1] = flip01(p[i + 1])
            tier1.append(p)

        # 5. Actual peak test point if within [0, 1]
        peak_raw = np.array(
            [round(float(v), digits) for v in d["inp_last"][d["max_anomaly_idx"]]],
            dtype=np.float32,
        )
        if np.all((peak_raw >= 0.0) & (peak_raw <= 1.0)):
            tier1.append(peak_raw)

        # Tier 2: progressive spike amplitudes + guaranteed threshold-crossing scale
        tier2: List[np.ndarray] = []
        if not np.all((peak_raw >= 0.0) & (peak_raw <= 1.0)):
            tier2.append(peak_raw)

        top_active = active_cols[: min(5, len(active_cols))] if active_cols else list(range(min(5, D)))
        first_k = list(range(min(5, D)))
        dyn_amp = float(math.ceil(math.sqrt(max(1.0, 2.8 * th) * 200.0 * D / max(1, len(first_k)))))
        amp_list = [1.5, 2.0, -1.0, 3.0, -2.0, 5.0, 8.0, 12.0, -5.0, 20.0]
        if dyn_amp > 20.0:
            amp_list.append(dyn_amp)

        for amp in amp_list:
            c0 = top_active[0] if top_active else 0
            p1 = base.copy()
            p1[c0] = round(float(base[c0] + amp if amp > 20.0 else amp), digits)
            tier2.append(p1)
            if D > 1:
                pa = base.copy()
                for c in top_active:
                    pa[c] = round(float(base[c] + amp if amp > 20.0 else amp), digits)
                tier2.append(pa)
                pf = base.copy()
                for c in first_k:
                    pf[c] = round(float(base[c] + amp if amp > 20.0 else amp), digits)
                tier2.append(pf)

        all_cands = tier1 + tier2
        n_t1 = len(tier1)
        batch = np.repeat(win_norm[None, :, :], len(all_cands), axis=0)
        for idx_c, p in enumerate(all_cands):
            batch[idx_c, -1, :] = p

        with torch.no_grad():
            wt = torch.tensor(batch, dtype=torch.float32)
            x_hat, x_out, _ = model(wt)
            mse_arr = torch.mean((wt - x_hat) ** 2, dim=(1, 2)).numpy()
            probs = x_out.numpy()

        ce_arr = np.sum(probs[:, allowed], axis=1) if allowed else np.zeros(len(all_cands))
        comb_arr = (mse_arr + ce_arr) / 2.0

        t1_valid = [k for k in range(n_t1) if comb_arr[k] > th * 1.03 + 0.005]
        if not t1_valid:
            t1_valid = [k for k in range(n_t1) if comb_arr[k] > th + 1e-4]

        if t1_valid:
            def rank_t1(k: int):
                p = all_cands[k]
                mod_cols = [i for i in range(D) if abs(float(p[i]) - float(base[i])) > 1.5e-3]
                has_active = any(hist_std[i] > 1e-3 for i in mod_cols) if D > 1 else True
                in_top10 = all(i < 10 for i in mod_cols)
                win_j = max(allowed, key=lambda j: probs[k, j]) if allowed else 0
                is_spike_cls = (win_j == 1 and probs[k, 1] > 0.7)
                return (
                    1 if is_spike_cls else 0,
                    1 if has_active else 0,
                    1 if in_top10 else 0,
                    float(comb_arr[k]),
                )

            best_k = max(t1_valid, key=rank_t1)
        else:
            t2_valid = [k for k in range(n_t1, len(all_cands)) if comb_arr[k] > th * 1.05 + 0.005]
            if not t2_valid:
                t2_valid = [k for k in range(n_t1, len(all_cands)) if comb_arr[k] > th + 1e-4]
            best_k = t2_valid[0] if t2_valid else int(np.argmax(comb_arr))

        chosen = [round(float(v), digits) for v in all_cands[best_k].tolist()]
        self.spike_cache[key] = chosen
        return chosen

    def predict_point(
        self,
        dataset: str,
        entity: str,
        seed: int,
        point: List[float],
        context_type: str = "normal_window",
        custom_history: Optional[List[List[float]]] = None,
        threshold_override: Optional[float] = None,
    ) -> Dict[str, Any]:
        model, params = self.load_model(dataset, entity, seed)
        data_dict = self.load_entity_data(dataset, entity, seed)

        D = params.n_features
        pt = np.array(point, dtype=np.float32).reshape(1, D)

        if context_type == "normal_window":
            win_norm = self.get_window(data_dict, data_dict["normal_idx"])
            context = win_norm[:-1, :]
        elif context_type == "sample_last":
            # Last 99 points from entity
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
        elif context_type == "custom" and custom_history is not None:
            c_arr = np.array(custom_history, dtype=np.float32)
            if len(c_arr) >= 99:
                context = c_arr[-99:]
            else:
                pad = np.tile(c_arr[0:1], (99 - len(c_arr), 1))
                context = np.vstack([pad, c_arr])
        else:
            win_norm = self.get_window(data_dict, data_dict["normal_idx"])
            context = win_norm[:-1, :]

        window = np.vstack([context, pt]) # (100, D)
        window_tensor = torch.tensor(window, dtype=torch.float32).unsqueeze(0)

        with torch.no_grad():
            x_hat, x_out, _ = model(window_tensor)

        reconstructed = x_hat.squeeze(0).cpu().numpy()
        pred_probs = x_out.squeeze(0).cpu().numpy()

        # Raw MSE
        raw_mse = float(np.mean((window - reconstructed) ** 2))

        # Raw CE (exclude classes in indices)
        indices = set(data_dict["indices"])
        raw_ce = float(sum(pred_probs[j] for j in range(12) if j not in indices))
        raw_combined = float((raw_mse + raw_ce) / 2.0)

        # Threshold
        th = threshold_override if threshold_override is not None else data_dict["default_threshold"]
        is_anomaly = raw_combined > th

        # Top-3 labels from allowed classes (excluding indices)
        allowed_classes = [
            {"index": j, "label": ANOMALY_TYPES[j], "name_vi": PSEUDO_ANOMALY_INFO[j]["name_vi"], "prob": float(pred_probs[j])}
            for j in range(12) if j not in indices
        ]
        allowed_classes.sort(key=lambda x: x["prob"], reverse=True)
        top3 = allowed_classes[:3]

        # Determine winner pseudo anomaly group (truthful argmax when below threshold)
        if is_anomaly:
            winner_idx = allowed_classes[0]["index"] if allowed_classes else int(np.argmax(pred_probs))
            reason_text = f"Đạt xác suất cao nhất ({pred_probs[winner_idx]*100:.1f}%) trong các lớp bất thường hợp lệ"
        else:
            winner_idx = int(np.argmax(pred_probs))
            reason_text = (
                "Tín hiệu bám sát quy luật vận hành ổn định của thực thể."
                if winner_idx == 0
                else f"Biến động cục bộ nghiêng về {PSEUDO_ANOMALY_INFO[winner_idx]['name']} ({pred_probs[winner_idx]*100:.1f}%), nhưng tổng điểm chưa vượt ngưỡng μ + 3σ."
            )
        winner_meta = PSEUDO_ANOMALY_INFO[winner_idx]
        predicted_group = {
            "index": winner_idx,
            "name": winner_meta["name"],
            "name_vi": winner_meta["name_vi"],
            "desc_vi": winner_meta["desc_vi"],
            "prob": float(pred_probs[winner_idx]),
            "is_anomaly": is_anomaly,
            "reason": reason_text,
        }

        # All 12 classes summary
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

        # Excluded classes explanation
        excluded_info = []
        for idx in sorted(list(indices)):
            label_name = ANOMALY_TYPES[idx]
            if idx == 0:
                reason = "Lớp bình thường (luôn loại trừ)"
            else:
                m_val = data_dict["mean_label"][idx]
                reason = f"Xác suất trung bình toàn chuỗi ({m_val:.3f}) > ngưỡng 0,05"
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
            "explanation": f"MSE đạt {raw_mse:.4f}, điểm phân loại {raw_ce:.4f}, ngưỡng μ+3σ = {th:.4f}.",
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
        model, params = self.load_model(dataset, entity, seed)
        data_dict = self.load_entity_data(dataset, entity, seed)
        indices = set(data_dict["indices"])

        # Comparison normal window
        normal_t = data_dict["normal_idx"]
        win_normal = self.get_window(data_dict, normal_t)

        if is_custom_point and custom_window is not None:
            win_target = np.array(custom_window, dtype=np.float32)
            t = 100
        else:
            if t is None:
                t = data_dict["max_anomaly_idx"]
            t = max(0, min(t, data_dict["length"] - 1))
            win_target = self.get_window(data_dict, t)

        # Forward hooks for intermediate activations (separate target vs normal)
        activations_target = {}
        activations_normal = {}
        hook_target_dict = [activations_target]
        hooks = []
        for i, blk in enumerate(model.encoder.network):
            def make_hook(name):
                def hook(m, inp, outp):
                    hook_target_dict[0][name] = outp.detach().cpu().numpy()
                return hook
            hooks.append(blk.register_forward_hook(make_hook(f"conv_{i}")))

        win_t_tensor = torch.tensor(win_target, dtype=torch.float32).unsqueeze(0)
        win_n_tensor = torch.tensor(win_normal, dtype=torch.float32).unsqueeze(0)

        with torch.no_grad():
            hook_target_dict[0] = activations_target
            x_hat_t, x_out_t, x_enc_t = model(win_t_tensor)
            hook_target_dict[0] = activations_normal
            x_hat_n, x_out_n, x_enc_n = model(win_n_tensor)

        for h in hooks:
            h.remove()

        rec_target = x_hat_t.squeeze(0).cpu().numpy()
        rec_normal = x_hat_n.squeeze(0).cpu().numpy()
        probs_target = x_out_t.squeeze(0).cpu().numpy()
        probs_normal = x_out_n.squeeze(0).cpu().numpy()
        emb_t_np = x_enc_t.squeeze().cpu().numpy()
        emb_n_np = x_enc_n.squeeze().cpu().numpy()
        embedding_target = emb_t_np.tolist()
        embedding_normal = emb_n_np.tolist()
        emb_l2_dist = float(np.linalg.norm(emb_t_np - emb_n_np))
        emb_denom = float(np.linalg.norm(emb_t_np) * np.linalg.norm(emb_n_np))
        emb_cosine = float(np.dot(emb_t_np, emb_n_np) / emb_denom) if emb_denom > 1e-8 else 1.0

        conv_energies_target = [
            float(np.mean(np.abs(activations_target.get(f"conv_{i}", np.zeros(1)))))
            for i in range(4)
        ]
        conv_energies_normal = [
            float(np.mean(np.abs(activations_normal.get(f"conv_{i}", np.zeros(1)))))
            for i in range(4)
        ]

        # Step 2: Conv shapes & Embedding
        conv_shapes = [
            {
                "layer": "Input Window",
                "sub": f"{params.n_features} channels × {params.n_time} steps",
                "shape": f"[1, {params.n_features}, {params.n_time}]",
                "raw_shape": f"[1, {params.n_time}, {params.n_features}]",
                "channels": params.n_features,
                "time_len": params.n_time,
                "role": "input",
            },
            {
                "layer": "ConvBlock 0 (k=4, s=2)",
                "sub": "128 channels × 51 steps",
                "shape": "[1, 128, 51]",
                "channels": 128,
                "time_len": 51,
                "role": "conv",
                "energy": round(conv_energies_target[0], 4),
                "energy_normal": round(conv_energies_normal[0], 4),
            },
            {
                "layer": "ConvBlock 1 (k=4, s=2)",
                "sub": "128 channels × 26 steps",
                "shape": "[1, 128, 26]",
                "channels": 128,
                "time_len": 26,
                "role": "conv",
                "energy": round(conv_energies_target[1], 4),
                "energy_normal": round(conv_energies_normal[1], 4),
            },
            {
                "layer": "ConvBlock 2 (k=4, s=2)",
                "sub": "256 channels × 14 steps",
                "shape": "[1, 256, 14]",
                "channels": 256,
                "time_len": 14,
                "role": "conv",
                "energy": round(conv_energies_target[2], 4),
                "energy_normal": round(conv_energies_normal[2], 4),
            },
            {
                "layer": "ConvBlock 3 (k=4, s=2)",
                "sub": "256 channels × 8 steps",
                "shape": "[1, 256, 8]",
                "channels": 256,
                "time_len": 8,
                "role": "conv",
                "energy": round(conv_energies_target[3], 4),
                "energy_normal": round(conv_energies_normal[3], 4),
            },
            {
                "layer": "MaxPool1D (8 → 1)",
                "sub": "Global Max Pooling",
                "shape": "[1, 256, 1]",
                "channels": 256,
                "time_len": 1,
                "role": "pool",
            },
            {
                "layer": "Conv1x1 → Embedding z",
                "sub": "Bottleneck → Decoder & Classifier",
                "shape": "[1, 128, 1]",
                "channels": 128,
                "time_len": 1,
                "role": "bottleneck",
            },
        ]
        conv_heatmap_summary = {}
        for k, v in activations_target.items():
            conv_heatmap_summary[k] = np.mean(np.abs(v[0]), axis=1).tolist()[:32]

        # Step 3: Decoder error per point & Binary Anomaly Mask (meta.py: inputs*anomaly_mask, predicted*anomaly_mask)
        sq_target_mat = (win_target - rec_target) ** 2
        sq_normal_mat = (win_normal - rec_normal) ** 2
        err_sq_target = np.mean(sq_target_mat, axis=1).tolist()
        err_sq_normal = np.mean(sq_normal_mat, axis=1).tolist()
        mse_target = float(np.mean(sq_target_mat))
        mse_normal = float(np.mean(sq_normal_mat))

        # Binary keep-mask (1 = normal cell kept in MSE, 0 = anomalous cell masked out in Eq. 2)
        cell_th = np.maximum(np.max(sq_normal_mat, axis=0, keepdims=True) * 1.25, 0.01)
        keep_mask_target = (sq_target_mat <= cell_th).astype(np.float32)
        keep_mask_normal = (sq_normal_mat <= cell_th).astype(np.float32)
        err_sq_target_masked = np.mean(sq_target_mat * keep_mask_target, axis=1).tolist()
        err_sq_normal_masked = np.mean(sq_normal_mat * keep_mask_normal, axis=1).tolist()
        mse_target_masked = float(np.mean(sq_target_mat * keep_mask_target))
        mse_normal_masked = float(np.mean(sq_normal_mat * keep_mask_normal))

        # Raw scores for target
        raw_mse_val = mse_target
        raw_ce_val = float(sum(probs_target[j] for j in range(12) if j not in indices))
        raw_comb_val = float((raw_mse_val + raw_ce_val) / 2.0)
        th = data_dict["default_threshold"]
        is_anomaly = raw_comb_val > th

        # Determine winner pseudo anomaly class
        if is_anomaly:
            allowed_cand = [j for j in range(12) if j not in indices]
            winner_idx = max(allowed_cand, key=lambda j: probs_target[j]) if allowed_cand else int(np.argmax(probs_target))
        else:
            winner_idx = int(np.argmax(probs_target))
        winner_meta = PSEUDO_ANOMALY_INFO[winner_idx]

        # Step 4: Classifier
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

        plot_feat_idx = 0
        if is_custom_point and params.n_features > 1:
            last_sq_err = (win_target[-1] - rec_target[-1]) ** 2
            jump = np.abs(win_target[-1] - win_target[-2]) if len(win_target) >= 2 else np.zeros(params.n_features)
            hist_std = np.std(win_target[:-1], axis=0) if len(win_target) >= 2 else np.zeros(params.n_features)
            if float(np.max(jump)) > 1e-2:
                cand = np.where(jump >= 0.5 * float(np.max(jump)))[0]
                active_cand = cand[hist_std[cand] > 1e-3]
                if len(active_cand) > 0:
                    plot_feat_idx = int(active_cand[np.argmax(hist_std[active_cand])])
                else:
                    plot_feat_idx = int(cand[np.argmax(last_sq_err[cand])])
            else:
                top_k = min(5, params.n_features)
                if float(np.max(hist_std[:top_k])) > 1e-3:
                    plot_feat_idx = int(np.argmax(hist_std[:top_k]))
                else:
                    plot_feat_idx = int(np.argmax(hist_std))
        elif not is_custom_point and params.n_features > 1:
            ch_mse = np.mean(sq_target_mat, axis=0)
            if float(ch_mse[0]) < 0.01 and float(np.max(ch_mse)) > float(ch_mse[0]) * 3.0:
                plot_feat_idx = int(np.argmax(ch_mse))

        total_cells = int(keep_mask_target.size)
        masked_cells_target = int(np.sum(keep_mask_target == 0))
        kept_cells_target = total_cells - masked_cells_target
        masked_cells_normal = int(np.sum(keep_mask_normal == 0))
        mask_info = {
            "total_cells": total_cells,
            "masked_cells_target": masked_cells_target,
            "kept_cells_target": kept_cells_target,
            "masked_cells_normal": masked_cells_normal,
            "mask_step_target": keep_mask_target[:, plot_feat_idx].astype(int).tolist(),
            "mask_step_normal": keep_mask_normal[:, plot_feat_idx].astype(int).tolist(),
            "masked_ch_count_target": np.sum(keep_mask_target == 0, axis=1).astype(int).tolist(),
            "masked_ch_count_normal": np.sum(keep_mask_normal == 0, axis=1).astype(int).tolist(),
            "err_sq_target_masked": err_sq_target_masked,
            "err_sq_normal_masked": err_sq_normal_masked,
            "mse_target_masked": mse_target_masked,
            "mse_normal_masked": mse_normal_masked,
        }

        if is_custom_point:
            # Custom point mode: 100 points (1..100)
            time_axis = list(range(1, 101))
            input_slice = win_target[:, plot_feat_idx].tolist()
            # Step 5 slice: 50 clean reference steps around normal_t + custom point
            hist_end = max(1, min(len(data_dict["raw_score"]), normal_t))
            hist_start = max(0, hist_end - 50)
            score_slice_rec = data_dict["mse"][hist_start:hist_end].tolist() + [raw_mse_val]
            l_sub = np.copy(data_dict["pred_label"][hist_start:hist_end])
            l_sub[:, list(indices)] = 0
            score_slice_ce = np.sum(l_sub, axis=1).tolist() + [raw_ce_val]
            raw_slice_combined = data_dict["raw_score"][hist_start:hist_end].tolist() + [raw_comb_val]
            score_slice_final = data_dict["anomaly_score"][hist_start:hist_end].tolist() + [min(1.0, raw_comb_val / max(1e-5, th * 1.5))]
            final_rel_val = score_slice_final[-1]

            explanations = [
                f"Input Window 100 bước với điểm mới tại t=100 được đưa vào phân tích.",
                f"Encoder nén cửa sổ 100 bước qua 4 khối 1D-CNN thành Bottleneck Embedding z (128 chiều).",
                f"Sai số tái tạo Decoder tại điểm nạp MSE = {mse_target:.4f} (chuẩn đối chứng: {mse_normal:.4f}).",
                f"Classifier phân loại điểm nạp vào lớp '{winner_meta['name_vi']}' với xác suất {probs_target[winner_idx]*100:.1f}%.",
                f"Combined Score = {raw_comb_val:.3f} ({'vượt ngưỡng μ+3σ ' + f'{th:.3f} -> Bất thường' if is_anomaly else 'dưới ngưỡng μ+3σ ' + f'{th:.3f} -> Bình thường'})."
            ]
        else:
            # Entity series mode
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
                f"Input Window 100 bước tại vị trí t={t} được tô sáng trên chuỗi dữ liệu gốc.",
                f"Encoder nén cửa sổ tại t={t} thành Bottleneck Embedding z (128 chiều), đối chiếu chuẩn t={normal_t}.",
                f"Sai số tái tạo Decoder MSE = {mse_target:.4f} ở cửa sổ khảo sát (cửa sổ chuẩn: {mse_normal:.4f}).",
                f"Classifier dự đoán xác suất 12 lớp Pseudo-Anomaly, lọc bỏ lớp Normal và FAA (> 0.05).",
                f"Combined Score = ({raw_mse_val:.3f} + {raw_ce_val:.3f})/2 = {raw_comb_val:.3f}, {'vượt' if is_anomaly else 'dưới'} ngưỡng μ+3σ ({th:.3f})."
            ]

        return {
            "t": t,
            "normal_t": normal_t,
            "is_custom_point": is_custom_point,
            "plot_feature_idx": plot_feat_idx,
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
            "win_target": win_target[:, plot_feat_idx].tolist(),
            "win_normal": win_normal[:, plot_feat_idx].tolist(),
            "rec_target": rec_target[:, plot_feat_idx].tolist(),
            "rec_normal": rec_normal[:, plot_feat_idx].tolist(),
            "err_sq_target": err_sq_target,
            "err_sq_normal": err_sq_normal,
            "mse_target": mse_target,
            "mse_normal": mse_normal,
            "mask_info": mask_info,
            "conv_shapes": conv_shapes,
            "conv_heatmap": conv_heatmap_summary,
            "embedding": embedding_target,
            "embedding_normal": embedding_normal,
            "embedding_l2_dist": emb_l2_dist,
            "embedding_cosine": emb_cosine,
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
