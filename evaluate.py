"""
Evaluation script for RedLamp outputs and benchmark results from Google Drive / Kaggle.
Computes and summarizes VUS-ROC, VUS-PR, Range F-score (RF), and Range-AUC metrics.

Usage examples:
    # 1. Summary of all datasets from Drive results:
    python evaluate.py --summary --result_dir result

    # 2. Evaluate a specific dataset (e.g. SMD, IOPS, AnomalyArchive):
    python evaluate.py --dataset smd --result_dir result

    # 3. Recompute metrics from raw .npy test outputs:
    python evaluate.py --dataset smd --result_dir result --recompute
"""
import os
import sys
import glob
import argparse
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any

# Ensure project root in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Table 3 & Table 5 paper reference metrics (Obata et al., KDD 2025)
PAPER_BENCHMARK = {
    "anomaly_archive": {"VUS-ROC": 0.897, "VUS-PR": 0.492, "RF": 0.234, "R-AUC-ROC": 0.902, "R-AUC-PR": 0.517},
    "iops":            {"VUS-ROC": 0.911, "VUS-PR": 0.448, "RF": 0.179, "R-AUC-ROC": 0.940, "R-AUC-PR": 0.636},
    "smd":             {"VUS-ROC": 0.813, "VUS-PR": 0.366, "RF": 0.235, "R-AUC-ROC": 0.837, "R-AUC-PR": 0.429},
    "smap":            {"VUS-ROC": 0.642, "VUS-PR": 0.360, "RF": 0.196, "R-AUC-ROC": 0.658, "R-AUC-PR": 0.374},
    "msl":             {"VUS-ROC": 0.753, "VUS-PR": 0.482, "RF": 0.254, "R-AUC-ROC": 0.766, "R-AUC-PR": 0.507},
}

DATASET_DISPLAY_NAMES = {
    "anomaly_archive": "UCR Anomaly Archive",
    "iops":            "AIOps / IOPS KPI",
    "smd":             "SMD (Server Machine Dataset)",
    "smap":            "NASA SMAP",
    "msl":             "NASA MSL",
    "stock":           "TSB-AD Stock",
}

def load_summary_from_csv(result_dir: str, dataset: str) -> Optional[Dict[str, Any]]:
    """Loads existing benchmark summary CSVs from result directory or metrics directory."""
    candidates = [
        os.path.join(result_dir, f"summary_{dataset}.csv"),
        os.path.join(result_dir, f"{dataset}_summary.csv"),
        os.path.join(result_dir, f"metrics_{dataset}.csv"),
        os.path.join(result_dir, f"{dataset}.csv"),
        os.path.join(PROJECT_ROOT, "metrics", f"{dataset}_summary.csv"),
        os.path.join(PROJECT_ROOT, "metrics", f"{dataset}.csv"),
    ]
    for p in candidates:
        if os.path.exists(p) and os.path.getsize(p) > 0:
            try:
                df = pd.read_csv(p)
                if "metric" in df.columns and "ours (mean)" in df.columns:
                    # Format: summary_*.csv
                    res = {}
                    for _, r in df.iterrows():
                        m = str(r["metric"])
                        res[m] = float(r["ours (mean)"])
                    num_ent = int(df["#entities"].iloc[0]) if "#entities" in df.columns else None
                    return {"dataset": dataset, "metrics": res, "#entities": num_ent, "source": p}
                elif "V-R" in df.columns and "V-P" in df.columns and "RF" in df.columns:
                    # Format: anomaly_archive_summary.csv
                    return {
                        "dataset": dataset,
                        "metrics": {
                            "VUS-ROC": float(df["V-R"].iloc[0]),
                            "VUS-PR": float(df["V-P"].iloc[0]),
                            "RF": float(df["RF"].iloc[0]),
                        },
                        "#entities": int(df["#entities"].iloc[0]) if "#entities" in df.columns else len(df),
                        "source": p,
                    }
                elif "VUS-ROC" in df.columns or "VUS_ROC" in df.columns:
                    col_roc = "VUS-ROC" if "VUS-ROC" in df.columns else "VUS_ROC"
                    col_pr = "VUS-PR" if "VUS-PR" in df.columns else "VUS_PR"
                    col_rf = "RF" if "RF" in df.columns else None
                    if "seed" in df.columns:
                        df_s0 = df[df["seed"] == 0]
                        if not df_s0.empty:
                            df = df_s0
                    df = df.drop_duplicates(subset=["entity"] if "entity" in df.columns else None)
                    res = {
                        "VUS-ROC": float(pd.to_numeric(df[col_roc], errors="coerce").mean()),
                        "VUS-PR": float(pd.to_numeric(df[col_pr], errors="coerce").mean()),
                    }
                    if col_rf:
                        res["RF"] = float(pd.to_numeric(df[col_rf], errors="coerce").mean())
                    if "R-AUC-ROC" in df.columns:
                        res["R-AUC-ROC"] = float(pd.to_numeric(df["R-AUC-ROC"], errors="coerce").mean())
                    if "R-AUC-PR" in df.columns:
                        res["R-AUC-PR"] = float(pd.to_numeric(df["R-AUC-PR"], errors="coerce").mean())
                    return {"dataset": dataset, "metrics": res, "#entities": len(df), "source": p}
            except Exception as e:
                pass
    return None

def compute_metrics_for_dataset(result_dir: str, dataset: str, window: int = 100) -> Optional[pd.DataFrame]:
    """Recomputes VUS-ROC, VUS-PR, and Range F-score on raw .npy files."""
    try:
        from backend.metrics_eval import compute_paper_metrics
    except ImportError:
        print("[Error] Cannot import compute_paper_metrics from backend.metrics_eval")
        return None

    # Search for test_all folders
    ds_folder = os.path.join(result_dir, "aiops" if dataset in ("iops", "aiops") else dataset)
    if not os.path.exists(ds_folder):
        ds_folder = os.path.join(result_dir, dataset)
    if not os.path.exists(ds_folder):
        print(f"[Warning] Result folder for {dataset} not found in {result_dir}")
        return None

    pattern = os.path.join(ds_folder, "**", "test_all")
    test_dirs = glob.glob(pattern, recursive=True)
    if not test_dirs:
        print(f"[Warning] No test_all folders found under {ds_folder}")
        return None

    rows = []
    print(f"--> Recomputing metrics for {dataset} ({len(test_dirs)} runs found)...")
    for t_dir in sorted(test_dirs):
        score_p = os.path.join(t_dir, "anomaly_score.npy")
        label_p = os.path.join(t_dir, "label.npy")
        if not (os.path.exists(score_p) and os.path.exists(label_p)):
            continue
        try:
            score = np.load(score_p)
            label = np.load(label_p)
            # Binary ground-truth
            if label.ndim > 1 and label.shape[1] == 12:
                # One-hot pseudo anomaly: non-zero is anomaly
                bin_label = (label[:, 1:].sum(axis=1) > 0).astype(int)
            else:
                bin_label = (label.ravel() > 0).astype(int)

            if len(score) != len(bin_label) or bin_label.sum() == 0:
                continue

            m = compute_paper_metrics(score, bin_label, window=window)
            if m:
                # Parse entity and seed from path
                parts = os.path.normpath(t_dir).split(os.sep)
                seed = parts[-2] if len(parts) >= 2 else "0"
                entity = parts[-4] if len(parts) >= 4 else "unknown"
                rows.append({
                    "dataset": dataset,
                    "entity": entity,
                    "seed": seed,
                    "VUS-ROC": m["vus_roc"],
                    "VUS-PR": m["vus_pr"],
                    "RF": m["rf"],
                    "RF (oracle)": m["rf_oracle"],
                    "R-AUC-ROC": m["r_auc_roc"],
                    "R-AUC-PR": m["r_auc_pr"],
                })
        except Exception as e:
            continue

    if not rows:
        return None
    return pd.DataFrame(rows)

def display_summary_table(results: List[Dict[str, Any]]):
    """Formats and prints a comprehensive comparison table between Paper and Ours."""
    print("\n" + "=" * 90)
    print("           BẢNG ĐỐI CHIẾU KẾT QUẢ BENCHMARK: REDLAMP PAPER vs. THỰC NGHIỆM TỰ CHẠY")
    print("=" * 90)
    header = f"{'Tập dữ liệu':<28} | {'#Ent':<5} | {'VUS-ROC (P / Ours / Diff)':<25} | {'VUS-PR (P / Ours / Diff)':<25} | {'RF (Paper / Ours)'}"
    print(header)
    print("-" * 90)

    for item in results:
        ds = item["dataset"]
        name = DATASET_DISPLAY_NAMES.get(ds, ds)
        n_ent = item.get("#entities", "-")
        m = item["metrics"]

        p_ref = PAPER_BENCHMARK.get(ds, {})
        p_roc = p_ref.get("VUS-ROC")
        p_pr = p_ref.get("VUS-PR")
        p_rf = p_ref.get("RF")

        o_roc = m.get("VUS-ROC", np.nan)
        o_pr = m.get("VUS-PR", np.nan)
        o_rf = m.get("RF", np.nan)

        d_roc = f"({o_roc - p_roc:+.3f})" if p_roc is not None and not np.isnan(o_roc) else ""
        d_pr = f"({o_pr - p_pr:+.3f})" if p_pr is not None and not np.isnan(o_pr) else ""

        roc_str = f"{p_roc or '-':<5} / {o_roc:.3f} {d_roc}" if not np.isnan(o_roc) else f"{p_roc or '-':<5} / -"
        pr_str = f"{p_pr or '-':<5} / {o_pr:.3f} {d_pr}" if not np.isnan(o_pr) else f"{p_pr or '-':<5} / -"
        rf_str = f"{p_rf or '-':<5} / {o_rf:.3f}" if not np.isnan(o_rf) else f"{p_rf or '-':<5} / -"

        print(f"{name:<28} | {str(n_ent):<5} | {roc_str:<25} | {pr_str:<25} | {rf_str}")

    print("=" * 90 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Evaluate RedLamp results from Google Drive / Kaggle.")
    parser.add_argument("--dataset", default="all", choices=["all", "anomaly_archive", "iops", "smd", "smap", "msl", "stock"],
                        help="Dataset to evaluate (default: all)")
    parser.add_argument("--result_dir", default="result", help="Directory containing result or metrics from Drive (default: result)")
    parser.add_argument("--summary", action="store_true", help="Quick summary mode using precomputed CSVs")
    parser.add_argument("--recompute", action="store_true", help="Force recomputing metrics on raw .npy files")
    parser.add_argument("--save", action="store_true", default=True, help="Save evaluation outputs to CSV")
    args = parser.parse_args()

    result_dir = os.path.abspath(args.result_dir)
    if not os.path.exists(result_dir):
        # Fallback to current working directory or pretrain
        if os.path.exists("pretrain"):
            result_dir = os.path.abspath("pretrain")
        else:
            result_dir = os.getcwd()

    datasets = ["anomaly_archive", "iops", "smd", "smap", "msl", "stock"] if args.dataset == "all" else [args.dataset]
    summary_items = []

    for ds in datasets:
        item = None
        if not args.recompute:
            item = load_summary_from_csv(result_dir, ds)

        if item is None and (args.recompute or not args.summary):
            df_recomputed = compute_metrics_for_dataset(result_dir, ds)
            if df_recomputed is not None and not df_recomputed.empty:
                if args.save:
                    out_csv = os.path.join(result_dir, f"metrics_{ds}.csv")
                    df_recomputed.to_csv(out_csv, index=False)
                    print(f"Saved recomputed metrics to: {out_csv}")
                # Average per seed 0
                df_s0 = df_recomputed[df_recomputed["seed"].astype(str) == "0"]
                if df_s0.empty:
                    df_s0 = df_recomputed
                m_avg = {
                    "VUS-ROC": float(df_s0["VUS-ROC"].mean()),
                    "VUS-PR": float(df_s0["VUS-PR"].mean()),
                    "RF": float(df_s0["RF"].mean()),
                }
                item = {"dataset": ds, "metrics": m_avg, "#entities": df_s0["entity"].nunique()}

        if item:
            summary_items.append(item)

    if summary_items:
        display_summary_table(summary_items)
    else:
        print(f"[Notice] No evaluation results found in '{result_dir}'.")
        print("Please ensure results downloaded from Google Drive are located in 'result/' or specify --result_dir <path>.")

if __name__ == "__main__":
    main()
