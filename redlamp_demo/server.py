import os
import sys
import numpy as np
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, Query, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from engine import RedLampEngine, ANOMALY_TYPES
from index import RedLampIndexer, get_default_result_dir, sanitize_for_json

RESULT_DIR = get_default_result_dir()

app = FastAPI(title="RedLamp Web Demo", description="Hệ thống demo phát hiện bất thường chuỗi thời gian không giám sát")

@app.middleware("http")
async def add_no_cache_headers(request, call_next):
    response = await call_next(request)
    if request.url.path.startswith("/static") or request.url.path == "/":
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

indexer = RedLampIndexer(RESULT_DIR)
engine = RedLampEngine(RESULT_DIR)

class PredictPointRequest(BaseModel):
    dataset: str
    entity: str
    seed: int = 0
    point: List[float]
    context_type: str = "normal_window" # normal_window, sample_last, custom, median
    custom_history: Optional[List[List[float]]] = None
    threshold_override: Optional[float] = None

class ExplainRequest(BaseModel):
    dataset: str
    entity: str
    seed: int = 0
    t: Optional[int] = None
    custom_window: Optional[List[List[float]]] = None
    point: Optional[List[float]] = None
    is_custom_point: bool = False

@app.get("/api/index")
def get_index():
    return sanitize_for_json(indexer.index_cache)

@app.get("/api/entity")
def get_entity(dataset: str = Query(...), entity: str = Query(...), seed: int = Query(0)):
    if "stock" in dataset.lower() or "stock" in entity.lower():
        raise HTTPException(status_code=400, detail="Stock dataset is excluded.")
    
    # Find entity in index
    ent_list = indexer.index_cache.get(dataset, [])
    target = next((e for e in ent_list if e["entity"] == entity), None)
    if not target and entity.upper() == "ALL" and ent_list:
        rep = ent_list[0]
        target = {
            **rep,
            "entity": "ALL",
            "display_name": "ALL",
            "representative_entity": rep["entity"],
            "num_entities": len(ent_list),
        }
    if not target:
        raise HTTPException(status_code=404, detail=f"Entity {entity} not found in {dataset}")

    target = dict(target)
    n_feat = int(target.get("n_features", 1))
    target.setdefault("n_params", 1090684 + 641 * n_feat)
    target.setdefault("train_mode", "shared" if dataset in ("msl", "smap") else "per_entity")

    # Check if model exists
    has_model = target["has_model"]
    extra_data = {}
    if has_model:
        try:
            d = engine.load_entity_data(dataset, entity, seed)
            seed_model_path = engine.get_model_path(dataset, entity, seed) or target.get("model_path")
            target["model_path"] = seed_model_path
            if seed_model_path:
                try:
                    rel_p = os.path.relpath(seed_model_path, RESULT_DIR).replace("\\", "/")
                except ValueError:
                    rel_p = seed_model_path.replace("\\", "/")
                target["model_rel_path"] = rel_p
                if "_s100/" in rel_p:
                    target["window_step"] = 100
                elif "_s10/" in rel_p:
                    target["window_step"] = 10
                elif "_s1/" in rel_p:
                    target["window_step"] = 1
            extra_data = {
                "length": d["length"],
                "default_threshold": d["default_threshold"],
                "threshold_3std": d["threshold_3std"],
                "threshold_995": d["threshold_995"],
                "threshold_990": d["threshold_990"],
                "threshold_950": d["threshold_950"],
                "max_anomaly_idx": d["max_anomaly_idx"],
                "normal_idx": d["normal_idx"],
                "normal_point": d["normal_point"],
                "spike_point": engine.get_spike_point(dataset, entity, seed),
                "feat_min": d["feat_min"],
                "feat_max": d["feat_max"],
                "feat_median": d["feat_median"],
                "faa_excluded_classes": [ANOMALY_TYPES[idx] for idx in d["indices"] if idx != 0],
            }
        except Exception as e:
            extra_data = {"error": str(e)}

    return sanitize_for_json({
        "meta": target,
        "selected_seed": seed,
        "detail": extra_data,
    })

@app.post("/api/predict_point")
def predict_point(req: PredictPointRequest):
    if "stock" in req.dataset.lower() or "stock" in req.entity.lower():
        raise HTTPException(status_code=400, detail="Stock dataset is excluded.")
    try:
        res = engine.predict_point(
            dataset=req.dataset,
            entity=req.entity,
            seed=req.seed,
            point=req.point,
            context_type=req.context_type,
            custom_history=req.custom_history,
            threshold_override=req.threshold_override,
        )
        return sanitize_for_json(res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/explain")
def explain(req: ExplainRequest):
    if "stock" in req.dataset.lower() or "stock" in req.entity.lower():
        raise HTTPException(status_code=400, detail="Stock dataset is excluded.")
    try:
        res = engine.explain(
            dataset=req.dataset,
            entity=req.entity,
            seed=req.seed,
            t=req.t,
            custom_window=req.custom_window,
            point=req.point,
            is_custom_point=req.is_custom_point,
        )
        return sanitize_for_json(res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/series")
def get_series(
    dataset: str = Query(...),
    entity: str = Query(...),
    seed: int = Query(0),
    feature: str = Query("0"),
    max_points: int = Query(2000),
):
    if "stock" in dataset.lower() or "stock" in entity.lower():
        raise HTTPException(status_code=400, detail="Stock dataset is excluded.")
    try:
        d = engine.load_entity_data(dataset, entity, seed)
        N = d["length"]
        anom_arr = d["anomaly_score"]
        # Peak-preserving downsampling so every anomaly spike & exact peak t is preserved on hover/click
        step = max(1, N // max_points)
        if step == 1:
            indices = list(range(N))
        else:
            idx_set = {0, N - 1, int(d["max_anomaly_idx"]), int(d["normal_idx"])}
            for b in range(0, N, step):
                bucket = anom_arr[b : min(N, b + step)]
                peak_offset = int(bucket.argmax()) if len(bucket) > 0 else 0
                idx_set.add(b + peak_offset)
            indices = sorted(i for i in idx_set if 0 <= i < N)
        inp = d["inp_last"]
        D = inp.shape[1] if inp.ndim > 1 else 1
        f_key = str(feature).strip().lower()
        if D == 1:
            feat_vals = [float(inp[i, 0]) for i in indices]
        else:
            try:
                f_idx = max(0, min(int(f_key), D - 1))
            except ValueError:
                f_idx = 0
            feat_vals = [float(inp[i, f_idx]) for i in indices]
        return sanitize_for_json({
            "indices": indices,
            "anomaly_score": [float(d["anomaly_score"][i]) for i in indices],
            "raw_score": [float(d["raw_score"][i]) for i in indices],
            "input_first_feature": feat_vals,
            "max_anomaly_idx": d["max_anomaly_idx"],
            "normal_idx": d["normal_idx"],
            "threshold": d["default_threshold"],
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static files
static_dir = os.path.join(CURRENT_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(
            index_file,
            headers={
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0",
            },
        )
    return {"message": "RedLamp Demo API running. Static index.html not found."}

if __name__ == "__main__":
    import uvicorn
    print("Khởi động RedLamp Web Demo tại http://127.0.0.1:8000")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=False)

