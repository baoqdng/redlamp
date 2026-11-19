import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add redlamp_demo to sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DEMO_DIR = os.path.join(BASE_DIR, "redlamp_demo")
if DEMO_DIR not in sys.path:
    sys.path.insert(0, DEMO_DIR)

from server import app

client = TestClient(app)

def test_api_serve_index():
    """Verify index HTML endpoint loads correctly."""
    res = client.get("/")
    assert res.status_code == 200

def test_api_index():
    """Verify /api/index lists datasets and available models/metrics."""
    res = client.get("/api/index")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, dict)
    expected_ds = ["anomaly_archive", "iops", "smd", "smap", "msl"]
    for ds in expected_ds:
        assert ds in data, f"Missing dataset {ds}"
        assert len(data[ds]) > 0

def test_api_entity():
    """Verify /api/entity loads entity metadata and threshold stats."""
    res = client.get("/api/entity?dataset=smd&entity=machine-1-1&seed=0")
    assert res.status_code == 200
    ent_data = res.json()
    assert "meta" in ent_data
    assert "detail" in ent_data
    assert ent_data["meta"]["entity"] == "machine-1-1"
    assert ent_data["detail"]["default_threshold"] > 0

def test_api_series():
    """Verify /api/series returns downsampled series and anomaly scores."""
    res = client.get("/api/series?dataset=smd&entity=machine-1-1&seed=0&max_points=500")
    assert res.status_code == 200
    series_data = res.json()
    assert "indices" in series_data
    assert "anomaly_score" in series_data
    assert "threshold" in series_data
    assert len(series_data["indices"]) > 0
    assert len(series_data["indices"]) == len(series_data["anomaly_score"])

def test_api_predict_point():
    """Verify /api/predict_point executes real-time inference on an incoming sample point."""
    payload = {
        "dataset": "smd",
        "entity": "machine-1-1",
        "seed": 0,
        "point": [0.0] * 38,
        "context_type": "normal_window"
    }
    res = client.post("/api/predict_point", json=payload)
    assert res.status_code == 200
    pred = res.json()
    assert "is_anomaly" in pred
    assert "conclusion" in pred
    assert "raw_mse" in pred
    assert "raw_ce" in pred
    assert "threshold" in pred
    assert "top3" in pred

def test_api_explain():
    """Verify /api/explain produces Explainable AI feature maps and layer activations."""
    payload = {
        "dataset": "smd",
        "entity": "machine-1-1",
        "seed": 0,
        "t": 100,
        "is_custom_point": False
    }
    res = client.post("/api/explain", json=payload)
    assert res.status_code == 200
    exp = res.json()
    assert "t" in exp
    assert "win_target" in exp
    assert "rec_target" in exp
    assert "mse_target" in exp
    assert "conv_heatmap" in exp
    assert "explanations" in exp
