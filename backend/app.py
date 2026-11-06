import os
import sys
import io
import pandas as pd
import numpy as np
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import List, Optional

# Ensure project root in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from backend.model_service import ModelService
from backend.augmentations import generate_augmentation_samples

app = FastAPI(title="RedLamp Time Series Anomaly Detection Demo")

# CORS middleware for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

service = ModelService(pretrain_dir=os.path.join(BASE_DIR, "pretrain"))

# In-memory storage for current active series to support fast window queries
active_session = {
    "model_id": None,
    "series": None,
    "labels": None,
    "n_train": 500
}

@app.get("/api/models")
def get_models():
    """Returns list of available pre-trained models with their metadata."""
    models = service.list_models()
    return {"models": models}

@app.get("/api/model_loss/{model_id:path}")
def get_model_loss(model_id: str):
    """Returns train/validation loss history from text files."""
    try:
        loss_data = service.get_loss_data(model_id)
        return {"model_id": model_id, "loss": loss_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/sample_datasets")
def get_sample_datasets():
    """Lists pre-packaged sample datasets from dataset directory."""
    stock_dir = os.path.join(BASE_DIR, "dataset", "stock")
    samples = []
    if os.path.exists(stock_dir):
        for f in sorted(os.listdir(stock_dir)):
            if f.endswith(".csv"):
                # Parse sample info
                parts = f.replace(".csv", "").split("_")
                tr_val = 500
                if "tr" in parts:
                    try:
                        tr_idx = parts.index("tr")
                        tr_val = int(parts[tr_idx + 1])
                    except Exception:
                        pass
                samples.append({
                    "id": f,
                    "filename": f,
                    "dataset": "stock",
                    "n_train": tr_val,
                    "n_features": 1,
                    "description": f"Stock finance time series with ground-truth anomalies (tr={tr_val})"
                })
    return {"samples": samples}

@app.get("/api/sample_data/{sample_name}")
def load_sample_data(sample_name: str):
    """Loads a sample dataset CSV and returns initial data stats."""
    path = os.path.join(BASE_DIR, "dataset", "stock", sample_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Sample dataset not found")

    df = pd.read_csv(path)
    data_col = 'Data' if 'Data' in df.columns else df.columns[0]
    series = df[data_col].values.astype(float)
    labels = df['Label'].values.astype(int) if 'Label' in df.columns else None

    tr_val = 500
    if "_tr_" in sample_name:
        try:
            m = re.search(r'_tr_(\d+)_', sample_name)
            if m: tr_val = int(m.group(1))
        except Exception:
            pass

    return {
        "filename": sample_name,
        "total_points": len(series),
        "n_train": tr_val,
        "has_label": labels is not None,
        "sample_points": series[:10].tolist()
    }

class AnalyzeRequest(BaseModel):
    model_id: str
    sample_name: Optional[str] = None
    csv_text: Optional[str] = None
    n_train: int = 500
    threshold_type: str = "percentile"  # "percentile" or "sigma"
    threshold_val: float = 99.5
    ce_threshold: float = 0.05
    step: int = 1

@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    """Main analysis endpoint executing RedLamp detection."""
    try:
        # Load series
        if req.sample_name:
            path = os.path.join(BASE_DIR, "dataset", "stock", req.sample_name)
            if not os.path.exists(path):
                raise HTTPException(status_code=404, detail=f"File {req.sample_name} not found")
            df = pd.read_csv(path)
        elif req.csv_text:
            df = pd.read_csv(io.StringIO(req.csv_text))
        else:
            raise HTTPException(status_code=400, detail="Must provide sample_name or csv_text")

        # Extract features and optional label
        data_col = 'Data' if 'Data' in df.columns else df.columns[0]
        labels = df['Label'].values.astype(int) if 'Label' in df.columns else None

        # Numeric columns (excluding Label)
        num_cols = [c for c in df.columns if c.lower() != 'label' and pd.api.types.is_numeric_dtype(df[c])]
        if not num_cols:
            num_cols = [data_col]

        series_data = df[num_cols].values.astype(float)

        # Store in active session for window detail queries
        active_session["model_id"] = req.model_id
        active_session["series"] = series_data
        active_session["labels"] = labels
        active_session["n_train"] = req.n_train

        # Run analysis
        result = service.analyze_series(
            model_id=req.model_id,
            series_data=series_data,
            labels=labels,
            n_train=req.n_train,
            threshold_type=req.threshold_type,
            threshold_val=req.threshold_val,
            ce_threshold=req.ce_threshold,
            step=req.step
        )
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload_csv")
async def upload_csv(file: UploadFile = File(...)):
    """Receives uploaded CSV and returns preview and column names."""
    try:
        contents = await file.read()
        text = contents.decode("utf-8")
        df = pd.read_csv(io.StringIO(text))
        
        has_label = 'Label' in df.columns or 'label' in df.columns
        num_cols = [c for c in df.columns if c.lower() != 'label']

        return {
            "filename": file.filename,
            "total_rows": len(df),
            "columns": df.columns.tolist(),
            "feature_columns": num_cols,
            "has_label": has_label,
            "csv_text": text
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {str(e)}")

@app.get("/api/window_detail")
def window_detail(window_idx: int):
    """Returns detailed reconstruction and classification for a chosen window."""
    if active_session["series"] is None or active_session["model_id"] is None:
        raise HTTPException(status_code=400, detail="No active analysis session")

    detail = service.get_window_detail(
        model_id=active_session["model_id"],
        series_data=active_session["series"],
        window_idx=window_idx,
        n_train=active_session["n_train"]
    )
    return detail

class CustomPointRequest(BaseModel):
    model_id: str
    feature_values: List[float]

@app.post("/api/predict_point")
def predict_point(req: CustomPointRequest):
    """Immediate inference for custom single point / 5-feature input."""
    try:
        res = service.predict_custom_point(req.model_id, req.feature_values)
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/augmentations")
def get_augmentations():
    """Returns the 12 synthetic augmentations from loader_aug.py for interactive gallery."""
    samples = generate_augmentation_samples()
    return {"augmentations": samples}

# Mount static frontend files
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)

