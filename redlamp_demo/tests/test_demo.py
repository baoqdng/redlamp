import os
import sys
import numpy as np
import pytest
from fastapi.testclient import TestClient

CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from server import app
from index import RedLampIndexer, get_default_result_dir
from engine import RedLampEngine

client = TestClient(app)
RESULT_DIR = get_default_result_dir()

def test_index_five_datasets_and_no_stock():
    # 0. Test /api/index HTTP endpoint directly to ensure JSON serialization succeeds without NaN errors
    resp = client.get("/api/index")
    assert resp.status_code == 200, f"/api/index failed with status {resp.status_code}"
    datasets = resp.json()

    # 1. Must contain all 5 datasets
    expected_ds = ["anomaly_archive", "iops", "smd", "smap", "msl"]
    for ds in expected_ds:
        assert ds in datasets, f"Missing dataset {ds}"
        assert len(datasets[ds]) > 0, f"Dataset {ds} is empty"

    # 2. Must NOT contain "stock" (case-insensitive)
    assert "stock" not in datasets, "Found dataset 'stock'"
    for ds_name, entities in datasets.items():
        assert "stock" not in ds_name.lower(), f"Dataset name contains stock: {ds_name}"
        for e in entities:
            assert "stock" not in e["entity"].lower(), f"Entity name contains stock: {e['entity']}"

    # 3. All datasets now use single seed (seed = 0) from Google Drive
    for ds in ["iops", "smd", "msl", "smap", "anomaly_archive"]:
        ents = datasets[ds]
        for e in ents:
            assert e["seeds"] == [0], f"Entity {e['entity']} in {ds} seeds mismatch: {e['seeds']}"
            assert e["is_multi_seed"] is False

    # 4. Anomaly archive has 250 entities (plus ALL overview entry = 251)
    aa_ents = datasets["anomaly_archive"]
    real_aa = [e for e in aa_ents if e["entity"] != "ALL"]
    assert len(real_aa) == 250, f"Anomaly archive expected 250 entities, found {len(real_aa)}"

def test_api_entity_endpoint():
    # Test SMD machine-1-1
    resp = client.get("/api/entity?dataset=smd&entity=machine-1-1&seed=0")
    assert resp.status_code == 200
    data = resp.json()
    assert data["meta"]["n_features"] == 38
    assert data["meta"]["window_size"] == 100
    assert data["meta"]["is_multi_seed"] is False
    assert "single_metrics" in data["meta"]
    assert data["meta"]["single_metrics"]["vus_roc"] > 0.8
    assert data["detail"]["default_threshold"] > 0

    # Test Anomaly archive 001
    resp_aa = client.get("/api/entity?dataset=anomaly_archive&entity=001&seed=0")
    assert resp_aa.status_code == 200
    data_aa = resp_aa.json()
    assert data_aa["meta"]["n_features"] == 1
    assert data_aa["meta"]["has_model"] is True
    assert data_aa["meta"]["single_metrics"]["vus_roc"] > 0.8

    # Verify seed-specific model_rel_path, n_params, train_mode, and FAA excluded classes
    resp_s0 = client.get("/api/entity?dataset=smd&entity=machine-1-2&seed=0").json()
    assert resp_s0["meta"]["model_rel_path"].endswith("/0/bestmodel.pkl")
    assert resp_s0["meta"]["n_params"] == 1115042
    assert resp_s0["meta"]["train_mode"] == "per_entity"

    resp_msl = client.get("/api/entity?dataset=msl&entity=C-1&seed=0").json()
    assert resp_msl["meta"]["train_mode"] == "shared"
    assert resp_msl["meta"]["n_params"] == 1125939

    resp_iops = client.get("/api/entity?dataset=iops&entity=ALL&seed=0").json()
    assert "speedup" in resp_iops["detail"]["faa_excluded_classes"]


def test_api_series_peak_preserving_indices():
    resp = client.get("/api/series?dataset=smd&entity=machine-1-1&seed=0&feature=0")
    assert resp.status_code == 200
    s = resp.json()
    assert "indices" in s and len(s["indices"]) > 0
    assert len(s["indices"]) == len(s["anomaly_score"]) == len(s["raw_score"]) == len(s["input_first_feature"])
    # Peak-preserving decimation must retain exact max_anomaly_idx and normal_idx for hover/click
    assert s["max_anomaly_idx"] in s["indices"]
    assert s["normal_idx"] in s["indices"]
    # Indices must be strictly increasing real timesteps
    assert all(s["indices"][i] < s["indices"][i + 1] for i in range(len(s["indices"]) - 1))

    # Individual feature selection (e.g. D38 -> feature=37) must return matching length
    resp_ch = client.get("/api/series?dataset=smd&entity=machine-1-1&seed=0&feature=37")
    assert resp_ch.status_code == 200
    sch = resp_ch.json()
    assert len(sch["input_first_feature"]) == len(sch["indices"])

def test_predict_point_stability():
    # Test manual point prediction on SMD
    pt = [0.1] * 38
    resp1 = client.post("/api/predict_point", json={
        "dataset": "smd",
        "entity": "machine-1-1",
        "seed": 0,
        "point": pt,
        "context_type": "sample_last"
    })
    assert resp1.status_code == 200
    r1 = resp1.json()
    assert "conclusion" in r1
    assert "raw_mse" in r1
    assert "top3" in r1
    assert len(r1["top3"]) == 3
    assert "predicted_group" in r1
    assert "name_vi" in r1["predicted_group"]
    assert "desc_vi" in r1["predicted_group"]
    assert "prob" in r1["predicted_group"]
    assert "custom_window" in r1
    assert len(r1["custom_window"]) == 100
    assert "all_classes" in r1
    assert len(r1["all_classes"]) == 12

    # Repeat with identical input to verify stability
    resp2 = client.post("/api/predict_point", json={
        "dataset": "smd",
        "entity": "machine-1-1",
        "seed": 0,
        "point": pt,
        "context_type": "sample_last"
    })
    assert resp2.status_code == 200
    r2 = resp2.json()
    assert abs(r1["raw_mse"] - r2["raw_mse"]) < 1e-7
    assert r1["conclusion"] == r2["conclusion"]
    assert r1["predicted_group"]["index"] == r2["predicted_group"]["index"]

def test_explain_endpoint_and_sentences():
    # Test standard explain mode
    resp = client.post("/api/explain", json={
        "dataset": "smd",
        "entity": "machine-1-1",
        "seed": 0,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["explanations"]) == 5
    for i, exp_str in enumerate(data["explanations"]):
        words = exp_str.split()
        assert len(words) <= 20, f"Step {i+1} explanation exceeds 20 words: '{exp_str}' (words: {len(words)})"
    assert "mse_target" in data
    assert "mask_info" in data
    m_info = data["mask_info"]
    assert m_info["total_cells"] == 38 * 100
    assert m_info["masked_cells_target"] > 0
    assert m_info["masked_cells_normal"] == 0
    assert m_info["mse_target_masked"] < data["mse_target"]
    assert set(m_info["mask_step_target"]).issubset({0, 1})
    assert len(m_info["mask_step_target"]) == 100
    assert "conv_shapes" in data
    assert len(data["embedding"]) == 128
    assert len(data["classes_target"]) == 12

    # Test sync explain mode with custom injected point
    pt = [3.0] * 38 # clear anomaly spike/wander
    p_resp = client.post("/api/predict_point", json={
        "dataset": "smd",
        "entity": "machine-1-1",
        "seed": 0,
        "point": pt,
        "context_type": "sample_last"
    })
    p_data = p_resp.json()
    assert p_data["conclusion"] == "BẤT THƯỜNG"

    exp_custom_resp = client.post("/api/explain", json={
        "dataset": "smd",
        "entity": "machine-1-1",
        "seed": 0,
        "custom_window": p_data["custom_window"],
        "point": pt,
        "is_custom_point": True,
    })
    assert exp_custom_resp.status_code == 200
    c_data = exp_custom_resp.json()
    assert c_data["is_custom_point"] is True
    assert len(c_data["explanations"]) == 5
    for i, exp_str in enumerate(c_data["explanations"]):
        words = exp_str.split()
        assert len(words) <= 20, f"Custom Step {i+1} explanation exceeds 20 words: '{exp_str}' (words: {len(words)})"
    assert "winner_group" in c_data
    assert c_data["winner_group"]["index"] == p_data["predicted_group"]["index"]

def test_numerical_accuracy_against_saved_test_output():
    """Verify numerical precision of model inference against saved outputs on 1 entity per dataset."""
    eng = RedLampEngine(RESULT_DIR)

    test_cases = [
        ("smd", "machine-1-1", 0),
        ("iops", "KPI-05f10d3a-239c-3bef-9bdc-a2feeb0037aa", 0),
        ("msl", "C-1", 0),
        ("smap", "A-1", 0),
        ("anomaly_archive", "001", 0),
    ]

    for ds, ent, seed in test_cases:
        model, _ = eng.load_model(ds, ent, seed)
        data = eng.load_entity_data(ds, ent, seed)
        
        # Take window at t = 200
        t = 200
        win = eng.get_window(data, t)
        import torch
        win_t = torch.tensor(win, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            x_hat, x_out, _ = model(win_t)
        
        calc_mse = float(torch.nn.functional.mse_loss(win_t, x_hat).item())
        saved_mse = float(data["mse"][t])

        # Saved MSE vs calculated MSE must be within small tolerance (< 1e-4)
        diff = abs(calc_mse - saved_mse)
        assert diff < 1e-4, f"Dataset {ds} entity {ent} MSE mismatch at t={t}: calc={calc_mse}, saved={saved_mse}, diff={diff}"


def test_clean_tab3_normal_and_unit_spike_across_five_datasets():
    """Verify Tab 3 baseline (Mẫu chuẩn) is normal and calibrated spike_point (Mẫu đột biến) is anomalous across all 5 datasets."""
    cases = [
        ("smd", "ALL", 0),
        ("smd", "machine-1-1", 0),
        ("smd", "machine-2-8", 0),
        ("smd", "machine-2-2", 0),
        ("smd", "machine-3-6", 0),
        ("iops", "KPI-05f10d3a-239c-3bef-9bdc-a2feeb0037aa", 0),
        ("msl", "C-1", 0),
        ("msl", "P-14", 0),
        ("smap", "A-1", 0),
        ("smap", "D-5", 0),
        ("anomaly_archive", "001", 0),
    ]
    for ds, ent, seed in cases:
        ent_resp = client.get(f"/api/entity?dataset={ds}&entity={ent}&seed={seed}").json()
        detail = ent_resp["detail"]
        n_feat = ent_resp["meta"]["n_features"]
        assert abs(detail["default_threshold"] - detail["threshold_3std"]) < 1e-7
        normal_pt = detail["normal_point"]
        spike_pt = detail["spike_point"]
        assert len(normal_pt) == n_feat
        assert len(spike_pt) == n_feat

        # 1. Baseline normal_point must be BÌNH THƯỜNG and never show 0.0% prob
        res_norm = client.post("/api/predict_point", json={
            "dataset": ds,
            "entity": ent,
            "seed": seed,
            "point": normal_pt,
            "context_type": "normal_window",
        }).json()
        assert res_norm["is_anomaly"] is False, f"{ds}/{ent} normal_point should be normal, got {res_norm['raw_combined']} vs {res_norm['threshold']}"
        assert res_norm["conclusion"] == "BÌNH THƯỜNG"
        assert res_norm["predicted_group"]["prob"] > 0.90

        # 2. Calibrated spike_point (Mẫu đột biến) must always be BẤT THƯỜNG
        res_spike = client.post("/api/predict_point", json={
            "dataset": ds,
            "entity": ent,
            "seed": seed,
            "point": spike_pt,
            "context_type": "normal_window",
        }).json()
        assert res_spike["is_anomaly"] is True, f"{ds}/{ent} spike_point should be anomaly, got {res_spike['raw_combined']} vs {res_spike['threshold']}"
        assert res_spike["conclusion"] == "BẤT THƯỜNG"
        if (ds, ent) in (("smd", "machine-1-1"), ("smd", "machine-2-8")):
            assert res_spike["predicted_group"]["name"].lower() == "spike"
            assert res_spike["predicted_group"]["prob"] > 0.95


