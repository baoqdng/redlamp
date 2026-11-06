import os
import sys
import pytest
from starlette.testclient import TestClient

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app import app

client = TestClient(app)

def test_api_models():
    res = client.get("/api/models")
    assert res.status_code == 200
    data = res.json()
    assert "models" in data
    assert len(data["models"]) > 0
    # verify Stock 149 is present
    model_ids = [m["model_id"] for m in data["models"]]
    assert any("149_Stock" in mid for mid in model_ids)

def test_api_sample_datasets():
    res = client.get("/api/sample_datasets")
    assert res.status_code == 200
    data = res.json()
    assert "samples" in data
    assert len(data["samples"]) > 0

def test_api_augmentations():
    res = client.get("/api/augmentations")
    assert res.status_code == 200
    data = res.json()
    assert "augmentations" in data
    assert len(data["augmentations"]) == 12
    assert "normal" in data["augmentations"]
    assert "spike" in data["augmentations"]
    assert "mixture" in data["augmentations"]

def test_api_predict_point():
    # Pick first model
    models_res = client.get("/api/models").json()
    model_id = models_res["models"][0]["model_id"]

    res = client.post("/api/predict_point", json={
        "model_id": model_id,
        "feature_values": [0.8, 0.1, 0.05, 0.0, 0.0]
    })
    assert res.status_code == 200
    data = res.json()
    assert "top1" in data
    assert "top3" in data
    assert len(data["pred_label"]) == 12

def test_api_analyze_sample():
    models_res = client.get("/api/models").json()
    stock_model = next(m["model_id"] for m in models_res["models"] if "149_Stock" in m["model_id"])

    res = client.post("/api/analyze", json={
        "model_id": stock_model,
        "sample_name": "149_Stock_id_1_Finance_tr_500_1st_7.csv",
        "n_train": 500,
        "threshold_type": "percentile",
        "threshold_val": 99.5,
        "ce_threshold": 0.05,
        "step": 1
    })
    assert res.status_code == 200
    data = res.json()
    assert data["conclusion"] in ["Có bất thường", "Không có bất thường"]
    assert "display" in data
    assert len(data["display"]["disp_time"]) > 0
    assert len(data["display"]["pca_x"]) > 0
    assert len(data["display"]["raw_mse"]) > 0
    assert len(data["display"]["raw_ce"]) > 0
    assert len(data["display"]["anomaly_score"]) > 0
    assert "indices_excluded" in data

def test_api_window_detail():
    # Call window_detail on the session created by previous test
    res = client.get("/api/window_detail?window_idx=100")
    assert res.status_code == 200
    data = res.json()
    assert "input_norm" in data
    assert "pred_norm" in data
    assert "squared_error" in data
    assert len(data["input_norm"]) == 100
    assert len(data["pred_norm"]) == 100

