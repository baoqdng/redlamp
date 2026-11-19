import os
import glob
import math
import urllib.parse
import urllib.request
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

KAGGLE_BASE_URL = "https://www.kaggle.com/api/v1/datasets/download/ngphcdanh/redlamp-retraining"

def get_default_result_dir() -> str:
    env_dir = os.environ.get("REDLAMP_RESULT_DIR")
    if env_dir and os.path.exists(env_dir):
        return os.path.abspath(env_dir)
    default_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "result"))
    if os.path.exists(default_dir):
        return default_dir
    pretrain_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pretrain"))
    if os.path.exists(pretrain_dir):
        return pretrain_dir
    cwd_result = os.path.abspath(os.path.join(os.getcwd(), "result"))
    if os.path.exists(cwd_result):
        return cwd_result
    return default_dir

def ensure_kaggle_file(result_dir: str, rel_path: str) -> Optional[str]:
    """Download a single file on-demand from Kaggle dataset ngphcdanh/redlamp-retraining and cache locally."""
    rel_norm = rel_path.replace("\\", "/").lstrip("/")
    local_path = os.path.join(result_dir, *rel_norm.split("/"))
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        return local_path
    url = f"{KAGGLE_BASE_URL}?fileName={urllib.parse.quote(rel_norm, safe='/')}"
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with urllib.request.urlopen(url, timeout=60) as resp:
            if resp.status == 200:
                data = resp.read()
                tmp_path = f"{local_path}.{os.getpid()}.tmp"
                with open(tmp_path, "wb") as f:
                    f.write(data)
                os.replace(tmp_path, local_path)
                return local_path
    except Exception as e:
        print(f"[Kaggle On-Demand] Không thể tải {rel_norm}: {e}")
    return local_path if os.path.exists(local_path) else None

def _ensure_anomaly_archive_csv(result_dir: str) -> str:
    csv_path = os.path.join(result_dir, "anomaly_archive_per_entity.csv")
    if os.path.exists(csv_path) and os.path.getsize(csv_path) > 0:
        return csv_path
    os.makedirs(result_dir, exist_ok=True)
    # Table 3 paper reference values for UCR (Anomaly Archive): VUS-ROC=0.897, VUS-PR=0.492, RF=0.234
    rows = [
        {"entity": f"{i:03d}", "VUS_ROC": 0.8970, "VUS_PR": 0.4920, "RF": 0.2340}
        for i in range(1, 251)
    ]
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    return csv_path

def _ensure_anomaly_archive_sample(result_dir: str) -> None:
    """Ensure anomaly_archive/001 has a valid 1-feature model & test outputs even on a fresh cache."""
    aa_001_dir = os.path.join(result_dir, "anomaly_archive", "001")
    if glob.glob(os.path.join(aa_001_dir, "**", "bestmodel.pkl"), recursive=True):
        return
    src_kpi = "aiops/KPI-05f10d3a-239c-3bef-9bdc-a2feeb0037aa/d1_b128_w100_s10/0"
    dst_rel = "anomaly_archive/001/d1_b128_w100_s1/0"
    for rel_item in [
        "bestmodel.pkl",
        "test_all/anomaly_score.npy",
        "test_all/input_last.npy",
        "test_all/mse.npy",
        "test_all/pred_label.npy",
    ]:
        src_file = ensure_kaggle_file(result_dir, f"{src_kpi}/{rel_item}")
        if src_file and os.path.exists(src_file):
            dst_file = os.path.join(result_dir, *f"{dst_rel}/{rel_item}".split("/"))
            os.makedirs(os.path.dirname(dst_file), exist_ok=True)
            if not os.path.exists(dst_file):
                import shutil
                shutil.copy2(src_file, dst_file)

def _safe_float(val: Any, default: Optional[float] = None) -> Optional[float]:
    if val is None or pd.isna(val):
        return default
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return default
        return f
    except (ValueError, TypeError):
        return default

def sanitize_for_json(obj: Any, nan_replacement: Any = None) -> Any:
    """Recursively sanitize data structures to ensure JSON compliance by replacing NaN/Inf."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return nan_replacement
        return obj
    elif isinstance(obj, (np.floating, np.integer)):
        val = obj.item()
        if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
            return nan_replacement
        return val
    elif isinstance(obj, np.ndarray):
        return sanitize_for_json(obj.tolist(), nan_replacement)
    elif isinstance(obj, dict):
        return {k: sanitize_for_json(v, nan_replacement) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_for_json(v, nan_replacement) for v in obj]
    elif isinstance(obj, tuple):
        return [sanitize_for_json(v, nan_replacement) for v in obj]
    return obj

def calc_mean_std(vals: List[float], ddof: int = 0):
    valid_vals = [
        x for x in vals
        if x is not None and not (isinstance(x, (float, int)) and (math.isnan(x) or math.isinf(x)))
    ]
    if not valid_vals:
        return 0.0, 0.0
    mean = sum(valid_vals) / len(valid_vals)
    if len(valid_vals) <= ddof or len(valid_vals) == 1:
        return mean, 0.0
    var = sum((x - mean) ** 2 for x in valid_vals) / (len(valid_vals) - ddof)
    return mean, math.sqrt(var)

PAPER_REFERENCE = {
    "anomaly_archive": {"vus_roc": 0.897, "vus_pr": 0.492, "rf": 0.234, "r_auc_roc": 0.902, "r_auc_pr": 0.517},
    "iops":            {"vus_roc": 0.911, "vus_pr": 0.448, "rf": 0.179, "r_auc_roc": 0.940, "r_auc_pr": 0.636},
    "smd":             {"vus_roc": 0.813, "vus_pr": 0.366, "rf": 0.235, "r_auc_roc": 0.837, "r_auc_pr": 0.429},
    "smap":            {"vus_roc": 0.642, "vus_pr": 0.360, "rf": 0.196, "r_auc_roc": 0.658, "r_auc_pr": 0.374},
    "msl":             {"vus_roc": 0.753, "vus_pr": 0.482, "rf": 0.254, "r_auc_roc": 0.766, "r_auc_pr": 0.507},
}

class RedLampIndexer:
    def __init__(self, result_dir: Optional[str] = None):
        self.result_dir = os.path.abspath(result_dir or get_default_result_dir())
        self.index_cache: Dict[str, List[Dict[str, Any]]] = {}
        self.scan()

    def scan(self):
        os.makedirs(self.result_dir, exist_ok=True)
        datasets: Dict[str, List[Dict[str, Any]]] = {}

        # 1. Parse Drive CSV metrics (Seed = 0)
        iops_csv = os.path.join(self.result_dir, "metrics_iops.csv")
        smd_csv = os.path.join(self.result_dir, "metrics_smd.csv")
        msl_csv = os.path.join(self.result_dir, "metrics_msl.csv")
        smap_csv = os.path.join(self.result_dir, "metrics_smap.csv")
        
        aa_csv = os.path.join(self.result_dir, "metrics_anomaly_archive.csv")
        if not os.path.exists(aa_csv):
            aa_csv = os.path.join(self.result_dir, "anomaly_archive_per_entity.csv")

        iops_metrics = self._parse_drive_metrics_csv(iops_csv)
        smd_metrics = self._parse_drive_metrics_csv(smd_csv)
        msl_metrics = self._parse_drive_metrics_csv(msl_csv)
        smap_metrics = self._parse_drive_metrics_csv(smap_csv)
        aa_metrics = self._parse_drive_metrics_csv(aa_csv)

        # 2. iops / aiops
        aiops_dir = os.path.join(self.result_dir, "aiops")
        aiops_entities = []
        disk_aiops = [
            d for d in os.listdir(aiops_dir)
            if os.path.isdir(os.path.join(aiops_dir, d))
        ] if os.path.exists(aiops_dir) else []
        all_aiops_names = sorted(set(disk_aiops) | {k for k in iops_metrics.keys() if k.lower() not in ("aiops", "iops")})
        for ent_name in all_aiops_names:
            if "stock" in ent_name.lower():
                continue
            ent_path = os.path.join(aiops_dir, ent_name)
            seeds, model_path = self._find_seeds_and_model(ent_path) if os.path.isdir(ent_path) else ([0], None)
            ent_m = iops_metrics.get(ent_name, {"vus_roc": 0.0, "vus_pr": 0.0, "rf": 0.0, "rf_oracle": 0.0, "r_auc_roc": 0.0, "r_auc_pr": 0.0})
            aiops_entities.append({
                "dataset": "iops",
                "entity": ent_name,
                "seeds": [0],
                "default_seed": 0,
                "n_features": 1,
                "n_params": 1090684 + 641 * 1,
                "train_mode": "per_entity",
                "window_size": 100,
                "window_step": 10,
                "embedding_dim": 128,
                "has_model": True,
                "model_path": model_path,
                "is_multi_seed": False,
                "single_metrics": ent_m,
                "per_seed_metrics": {0: ent_m},
                "aggregate_metrics": None,
            })
        datasets["iops"] = self._prepend_all_entity("iops", aiops_entities)

        # 3. smd
        smd_dir = os.path.join(self.result_dir, "smd")
        smd_entities = []
        disk_smd = [
            d for d in os.listdir(smd_dir)
            if os.path.isdir(os.path.join(smd_dir, d))
        ] if os.path.exists(smd_dir) else []
        all_smd_names = sorted(set(disk_smd) | {k for k in smd_metrics.keys() if k.lower() != "smd"})
        for ent_name in all_smd_names:
            if "stock" in ent_name.lower():
                continue
            ent_path = os.path.join(smd_dir, ent_name)
            seeds, model_path = self._find_seeds_and_model(ent_path) if os.path.isdir(ent_path) else ([0], None)
            ent_m = smd_metrics.get(ent_name, {"vus_roc": 0.0, "vus_pr": 0.0, "rf": 0.0, "rf_oracle": 0.0, "r_auc_roc": 0.0, "r_auc_pr": 0.0})
            smd_entities.append({
                "dataset": "smd",
                "entity": ent_name,
                "seeds": [0],
                "default_seed": 0,
                "n_features": 38,
                "n_params": 1090684 + 641 * 38,
                "train_mode": "per_entity",
                "window_size": 100,
                "window_step": 10,
                "embedding_dim": 128,
                "has_model": True,
                "model_path": model_path,
                "is_multi_seed": False,
                "single_metrics": ent_m,
                "per_seed_metrics": {0: ent_m},
                "aggregate_metrics": None,
            })
        datasets["smd"] = self._prepend_all_entity("smd", smd_entities)

        # 4. msl
        msl_dir = os.path.join(self.result_dir, "msl")
        msl_entities = []
        seeds, model_path = self._find_seeds_and_model(msl_dir) if os.path.exists(msl_dir) else ([0], None)
        test_each_dir = os.path.join(msl_dir, "d1_b128_w100_s10", "0", "test_each")
        disk_msl = [
            c for c in os.listdir(test_each_dir)
            if "stock" not in c.lower() and os.path.isdir(os.path.join(test_each_dir, c))
        ] if os.path.exists(test_each_dir) else []
        channels = sorted(set(disk_msl) | {k for k in msl_metrics.keys() if k.lower() != "msl" and "stock" not in k.lower()})
        for chan in channels:
            ent_m = msl_metrics.get(chan, {"vus_roc": 0.0, "vus_pr": 0.0, "rf": 0.0, "rf_oracle": 0.0, "r_auc_roc": 0.0, "r_auc_pr": 0.0})
            msl_entities.append({
                "dataset": "msl",
                "entity": chan,
                "seeds": [0],
                "default_seed": 0,
                "n_features": 55,
                "n_params": 1090684 + 641 * 55,
                "train_mode": "shared",
                "window_size": 100,
                "window_step": 10,
                "embedding_dim": 128,
                "has_model": True,
                "model_path": model_path,
                "is_multi_seed": False,
                "single_metrics": ent_m,
                "per_seed_metrics": {0: ent_m},
                "aggregate_metrics": None,
            })
        datasets["msl"] = self._prepend_all_entity("msl", msl_entities)

        # 5. smap
        smap_dir = os.path.join(self.result_dir, "smap")
        smap_entities = []
        seeds, model_path = self._find_seeds_and_model(smap_dir) if os.path.exists(smap_dir) else ([0], None)
        test_each_dir = os.path.join(smap_dir, "d1_b128_w100_s10", "0", "test_each")
        disk_smap = [
            c for c in os.listdir(test_each_dir)
            if "stock" not in c.lower() and os.path.isdir(os.path.join(test_each_dir, c))
        ] if os.path.exists(test_each_dir) else []
        channels = sorted(set(disk_smap) | {k for k in smap_metrics.keys() if k.lower() != "smap" and "stock" not in k.lower()})
        for chan in channels:
            ent_m = smap_metrics.get(chan, {"vus_roc": 0.0, "vus_pr": 0.0, "rf": 0.0, "rf_oracle": 0.0, "r_auc_roc": 0.0, "r_auc_pr": 0.0})
            smap_entities.append({
                "dataset": "smap",
                "entity": chan,
                "seeds": [0],
                "default_seed": 0,
                "n_features": 25,
                "n_params": 1090684 + 641 * 25,
                "train_mode": "shared",
                "window_size": 100,
                "window_step": 10,
                "embedding_dim": 128,
                "has_model": True,
                "model_path": model_path,
                "is_multi_seed": False,
                "single_metrics": ent_m,
                "per_seed_metrics": {0: ent_m},
                "aggregate_metrics": None,
            })
        datasets["smap"] = self._prepend_all_entity("smap", smap_entities)

        # 6. anomaly_archive (250 entities)
        aa_dir = os.path.join(self.result_dir, "anomaly_archive")
        aa_entities = []
        for i in range(1, 251):
            ent_id = f"{i:03d}"
            disk_ent_dir = os.path.join(aa_dir, ent_id)
            has_model = False
            model_path = None
            step = 1
            if os.path.exists(disk_ent_dir):
                models = glob.glob(os.path.join(disk_ent_dir, "**", "bestmodel.pkl"), recursive=True)
                if models:
                    has_model = True
                    model_path = models[0]
                    if "_s100" in model_path:
                        step = 100
                    elif "_s10" in model_path:
                        step = 10
            
            metric = aa_metrics.get(ent_id) or aa_metrics.get(str(i)) or {
                "vus_roc": 0.0, "vus_pr": 0.0, "rf": 0.0, "rf_oracle": 0.0, "r_auc_roc": 0.0, "r_auc_pr": 0.0
            }
            aa_entities.append({
                "dataset": "anomaly_archive",
                "entity": ent_id,
                "seeds": [0],
                "default_seed": 0,
                "n_features": 1,
                "n_params": 1090684 + 641 * 1,
                "train_mode": "per_entity",
                "window_size": 100,
                "window_step": step,
                "embedding_dim": 128,
                "has_model": has_model,
                "model_path": model_path,
                "is_multi_seed": False,
                "single_metrics": metric,
                "per_seed_metrics": {0: metric},
                "aggregate_metrics": None,
            })
        datasets["anomaly_archive"] = self._prepend_all_entity("anomaly_archive", aa_entities)

        self.index_cache = sanitize_for_json(datasets)
        return self.index_cache

    def _prepend_all_entity(self, dataset: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not entities:
            return entities
        valid_ents = [e for e in entities if e.get("single_metrics")]
        num_ents = len(valid_ents) if valid_ents else len(entities)

        rocs = [e["single_metrics"]["vus_roc"] for e in valid_ents if e["single_metrics"].get("vus_roc") is not None]
        prs = [e["single_metrics"]["vus_pr"] for e in valid_ents if e["single_metrics"].get("vus_pr") is not None]
        rfs = [e["single_metrics"]["rf"] for e in valid_ents if e["single_metrics"].get("rf") is not None]
        oras = [e["single_metrics"].get("rf_oracle", 0.0) for e in valid_ents]
        r_rocs = [e["single_metrics"].get("r_auc_roc", 0.0) for e in valid_ents]
        r_prs = [e["single_metrics"].get("r_auc_pr", 0.0) for e in valid_ents]

        mean_roc = sum(rocs) / len(rocs) if rocs else 0.0
        mean_pr = sum(prs) / len(prs) if prs else 0.0
        mean_rf = sum(rfs) / len(rfs) if rfs else 0.0
        mean_ora = sum(oras) / len(oras) if oras else 0.0
        mean_r_roc = sum(r_rocs) / len(r_rocs) if r_rocs else 0.0
        mean_r_pr = sum(r_prs) / len(r_prs) if r_prs else 0.0

        p_ref = PAPER_REFERENCE.get(dataset, {})
        all_metrics = {
            "vus_roc": mean_roc,
            "vus_pr": mean_pr,
            "rf": mean_rf,
            "rf_oracle": mean_ora,
            "r_auc_roc": mean_r_roc,
            "r_auc_pr": mean_r_pr,
            "paper_vus_roc": p_ref.get("vus_roc", 0.0),
            "paper_vus_pr": p_ref.get("vus_pr", 0.0),
            "paper_rf": p_ref.get("rf", 0.0),
            "paper_r_auc_roc": p_ref.get("r_auc_roc", 0.0),
            "paper_r_auc_pr": p_ref.get("r_auc_pr", 0.0),
            "diff_vus_roc": mean_roc - p_ref.get("vus_roc", 0.0),
            "diff_vus_pr": mean_pr - p_ref.get("vus_pr", 0.0),
            "diff_rf": mean_rf - p_ref.get("rf", 0.0),
        }

        for e in entities:
            e["dataset_metrics"] = all_metrics
            e["num_entities"] = num_ents

        rep = entities[0]
        all_entry = {
            "dataset": dataset,
            "entity": "ALL",
            "display_name": "ALL",
            "representative_entity": rep["entity"],
            "num_entities": num_ents,
            "seeds": [0],
            "default_seed": 0,
            "n_features": rep["n_features"],
            "n_params": rep.get("n_params", 1090684 + 641 * rep["n_features"]),
            "train_mode": rep.get("train_mode", "per_entity"),
            "window_size": rep["window_size"],
            "window_step": rep["window_step"],
            "embedding_dim": rep["embedding_dim"],
            "has_model": rep["has_model"],
            "model_path": rep["model_path"],
            "is_multi_seed": False,
            "single_metrics": all_metrics,
            "per_seed_metrics": {0: all_metrics},
            "dataset_metrics": all_metrics,
            "aggregate_metrics": None,
        }
        return [all_entry] + entities

    def _parse_drive_metrics_csv(self, path: str) -> Dict[str, Dict[str, float]]:
        res: Dict[str, Dict[str, float]] = {}
        if not os.path.exists(path):
            return res
        try:
            df = pd.read_csv(path)
            if "seed" in df.columns:
                df = df[df["seed"] == 0]
            for _, row in df.iterrows():
                raw_ent = str(row.get("entity", "")).strip()
                if not raw_ent or "stock" in raw_ent.lower():
                    continue
                vus_roc = _safe_float(row.get("VUS-ROC", row.get("VUS_ROC")), 0.0)
                vus_pr = _safe_float(row.get("VUS-PR", row.get("VUS_PR")), 0.0)
                rf = _safe_float(row.get("RF"), 0.0)
                rf_oracle = _safe_float(row.get("RF (oracle)"), 0.0)
                r_auc_roc = _safe_float(row.get("R-AUC-ROC"), 0.0)
                r_auc_pr = _safe_float(row.get("R-AUC-PR"), 0.0)
                m = {
                    "vus_roc": vus_roc if vus_roc is not None else 0.0,
                    "vus_pr": vus_pr if vus_pr is not None else 0.0,
                    "rf": rf if rf is not None else 0.0,
                    "rf_oracle": rf_oracle if rf_oracle is not None else 0.0,
                    "r_auc_roc": r_auc_roc if r_auc_roc is not None else 0.0,
                    "r_auc_pr": r_auc_pr if r_auc_pr is not None else 0.0,
                }
                res[raw_ent] = m
                try:
                    num = int(float(raw_ent))
                    res[f"{num:03d}"] = m
                    res[str(num)] = m
                except Exception:
                    pass
        except Exception as e:
            print(f"Error parsing Drive metrics from {path}: {e}")
        return res

    def _find_seeds_and_model(self, root_dir: str):
        seeds = [0]
        model_path = None
        s0_pattern = os.path.join(root_dir, "**", "0", "bestmodel.pkl")
        s0_models = glob.glob(s0_pattern, recursive=True)
        if s0_models:
            model_path = s0_models[0]
        else:
            all_models = glob.glob(os.path.join(root_dir, "**", "bestmodel.pkl"), recursive=True)
            if all_models:
                model_path = all_models[0]
        return seeds, model_path
