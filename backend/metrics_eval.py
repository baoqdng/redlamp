"""
Exact VUS-ROC, VUS-PR, Range-F (RF), and Range-AUC metrics following the
paper evaluation protocol in D:/REDLAMP-danh/REDLAMP-main/evaluate.py.

Protocol ('paper'):
  * Centre score alignment: window [i*step, i*step + W) aligns to label at i*step + W // 2.
  * VUS-ROC & VUS-PR: generate_curve(label, score, slidingWindow) integrating buffer 0..W/2.
  * Range-F (RF): Tatbul et al. (2018) range-based F1 (alpha=0.2) at threshold mean(score) + 3*std(score).
  * RF (oracle): Maximum Tatbul et al. (alpha=0.2) range-based F1 across score thresholds.
  * R-AUC-ROC & R-AUC-PR: RangeAUC with buffer W/2.
"""
import json
import os
import numpy as np
from typing import Dict, Optional
from vus.metrics import generate_curve
from vus.basic_metrics import basic_metricor

# Table 3 & Table 5 paper reference metrics (KDD'25 RedLamp) from D:/REDLAMP-danh/REDLAMP-main/evaluate.py
PAPER_REFERENCE = {
    "anomaly_archive": {"VUS-ROC": 0.897, "VUS-PR": 0.492, "RF": 0.234, "R-AUC-ROC": 0.902, "R-AUC-PR": 0.517},
    "iops":            {"VUS-ROC": 0.911, "VUS-PR": 0.448, "RF": 0.179, "R-AUC-ROC": 0.940, "R-AUC-PR": 0.636},
    "smd":             {"VUS-ROC": 0.813, "VUS-PR": 0.366, "RF": 0.235, "R-AUC-ROC": 0.837, "R-AUC-PR": 0.429},
    "smap":            {"VUS-ROC": 0.642, "VUS-PR": 0.360, "RF": 0.196, "R-AUC-ROC": 0.658, "R-AUC-PR": 0.374},
    "msl":             {"VUS-ROC": 0.753, "VUS-PR": 0.482, "RF": 0.254, "R-AUC-ROC": 0.766, "R-AUC-PR": 0.507},
}


class PaperMetricor(basic_metricor):
    """Subclass handling non-binary extended labels identically to evaluate.py's Metricor."""

    def range_convers_new(self, label):
        return super().range_convers_new((np.asarray(label) > 0).astype(int))


def align_labels_centre(gt_full: np.ndarray, n_scores: int, window: int = 100, step: int = 1) -> np.ndarray:
    """
    Aligns raw timestep ground-truth labels to window scores using the 'centre' protocol
    (offset = window // 2 = 50), matching evaluate.py test_labels(alignment='centre').
    """
    gt_arr = (np.asarray(gt_full, dtype=int).ravel() > 0).astype(int)
    off = window // 2
    idx = off + np.arange(n_scores) * step
    idx = np.clip(idx, 0, len(gt_arr) - 1)
    return gt_arr[idx]


def _range_f1_at_preds(grader: PaperMetricor, label: np.ndarray, preds: np.ndarray, alpha: float = 0.2) -> float:
    if not preds.any():
        return 0.0
    r_recall, _, _ = grader.range_recall_new(label, preds, alpha=alpha)
    r_prec = grader.range_recall_new(preds, label, alpha=0.0)[0]
    if (r_prec + r_recall) <= 0:
        return 0.0
    return float(2.0 * r_recall * r_prec / (r_prec + r_recall))


def compute_rf_oracle(grader: PaperMetricor, label: np.ndarray, score: np.ndarray, n_thresh: int = 40) -> float:
    """Finds best Tatbul Range-F1 (alpha=0.2) across candidate score thresholds."""
    s_min, s_max = float(np.min(score)), float(np.max(score))
    if s_max <= s_min:
        return 0.0
    qs = np.linspace(75.0, 99.9, n_thresh)
    thresholds = np.unique(np.percentile(score, qs))
    best = 0.0
    for th in thresholds:
        preds = (score > th).astype(int)
        if not preds.any():
            continue
        rf = _range_f1_at_preds(grader, label, preds, alpha=0.2)
        if rf > best:
            best = rf
    return float(best)


def compute_paper_metrics(
    score: np.ndarray,
    label: np.ndarray,
    window: int = 100,
    step: int = 1,
    compute_oracle: bool = True,
    max_curve_len: int = 3500,
) -> Optional[Dict[str, float]]:
    """
    Computes VUS-ROC, VUS-PR, RF (mean + 3*std), RF (oracle), R-AUC-ROC, R-AUC-PR
    matching D:/REDLAMP-danh/REDLAMP-main/evaluate.py ('paper' protocol).
    Range-F1 (mean+3std and oracle) are computed on full-resolution inputs;
    VUS-ROC/VUS-PR curves use exact inputs when len <= max_curve_len and
    preserve physical buffer W/2 via proportional striding for very long series.
    """
    score = np.asarray(score, dtype=float).ravel()
    label = (np.asarray(label, dtype=int).ravel() > 0).astype(int)
    if len(score) != len(label) or label.sum() == 0:
        return None

    grader = PaperMetricor()

    # Exact Range-F1 on full resolution
    pred_3std = (score > (np.mean(score) + 3.0 * np.std(score))).astype(int)
    rf_3std = _range_f1_at_preds(grader, label, pred_3std, alpha=0.2)
    rf_oracle = compute_rf_oracle(grader, label, score) if compute_oracle else rf_3std

    # VUS & RangeAUC curve integration
    sub_stride = max(1, len(score) // max_curve_len) if len(score) > max_curve_len else 1
    if sub_stride > 1:
        # Preserve any positive anomaly within each block using max pooling for labels & scores
        trim_len = (len(score) // sub_stride) * sub_stride
        sc_c = score[:trim_len].reshape(-1, sub_stride).max(axis=1)
        lb_c = label[:trim_len].reshape(-1, sub_stride).max(axis=1)
    else:
        sc_c = score
        lb_c = label

    eff_step = step * sub_stride
    sw = max(2, int(round(window / max(1, eff_step))))

    _, _, _, _, _, _, vus_roc, vus_pr = generate_curve(lb_c, sc_c, sw)
    r_roc, r_pr, _, _, _ = grader.RangeAUC(labels=lb_c, score=sc_c, window=sw, plot_ROC=True)

    return {
        "vus_roc": float(vus_roc),
        "vus_pr": float(vus_pr),
        "rf": float(rf_3std),
        "rf_oracle": float(rf_oracle),
        "r_auc_roc": float(r_roc),
        "r_auc_pr": float(r_pr),
    }


def load_eval_cache(cache_path: str) -> Dict[str, Dict[str, float]]:
    if cache_path and os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def save_eval_cache(cache_path: str, cache_data: Dict[str, Dict[str, float]]) -> None:
    if not cache_path:
        return
    try:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache_data, f, indent=2)
    except Exception:
        pass
