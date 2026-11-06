import os
import sys
import numpy as np
import pandas as pd
import pytest
import torch
from sklearn.preprocessing import MinMaxScaler

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import utils
from models.meta import ConvAEC
from main import anomaly_scoreing, convolve_minmax_score, mse, label_score_selected_feature

STOCK_CSV = "D:/repo/redlamp/dataset/stock/149_Stock_id_1_Finance_tr_500_1st_7.csv"
MODEL_PKL = "D:/repo/redlamp/pretrain/stock/149_Stock_id_1_Finance_tr_500_1st_7/d1_b128_w100_s1/0/bestmodel.pkl"
SAVED_TEST_DIR = "D:/repo/redlamp/pretrain/stock/149_Stock_id_1_Finance_tr_500_1st_7/d1_b128_w100_s1/0/test_all"

def test_normalization_and_slicing():
    """Verify MinMax scaling fit on the first 500 reference points."""
    assert os.path.exists(STOCK_CSV), f"Missing {STOCK_CSV}"
    df = pd.read_csv(STOCK_CSV)
    assert 'Data' in df.columns
    assert 'Label' in df.columns
    assert len(df) == 20000

    data = df['Data'].values.astype(float).reshape(-1, 1)
    train_end = 500
    scaler = MinMaxScaler()
    scaler.fit(data[:train_end])
    data_norm = scaler.transform(data)

    # Reference portion in [0, 1]
    ref_norm = data_norm[:train_end]
    assert np.all(ref_norm >= -1e-6) and np.all(ref_norm <= 1.0 + 1e-6)

def test_score_calculation_matches_ground_truth():
    """Verify anomaly_scoreing exactly reproduces saved anomaly_score.npy."""
    input_npy = f"{SAVED_TEST_DIR}/input.npy"
    pred_npy = f"{SAVED_TEST_DIR}/pred.npy"
    pred_label_npy = f"{SAVED_TEST_DIR}/pred_label.npy"
    saved_score_npy = f"{SAVED_TEST_DIR}/anomaly_score.npy"

    assert os.path.exists(saved_score_npy), "Missing saved ground truth anomaly score"
    
    test_inputs = np.load(input_npy)
    test_preds = np.load(pred_npy)
    test_pred_labels = np.load(pred_label_npy)
    saved_score = np.load(saved_score_npy)

    recomputed = anomaly_scoreing(test_inputs, test_preds, test_pred_labels, threshold=0.05)
    max_diff = np.max(np.abs(recomputed - saved_score))
    assert max_diff < 1e-12, f"Anomaly score mismatch! Max diff: {max_diff}"

def test_convaec_model_inference():
    """Verify ConvAEC outputs valid shapes, softmax sum == 1, and latent embeddings."""
    assert os.path.exists(MODEL_PKL), "Missing bestmodel.pkl"
    params = utils.AttrDict(
        name='ConvAEC',
        n_features=1,
        n_time=100,
        num_filters=[128, 128, 256, 256],
        embedding_dim=128,
        kernel_size=4,
        dropout=0.2,
        normalization='batch',
        stride=2,
        padding=2,
        anomaly_types=['normal','spike','flip','speedup','noise','cutoff','average','scale','wander','contextual','upsidedown','mixture'],
        classes=12,
        classifier_dim=32,
        c_loss_ratio=0.1,
        apply_anomaly_mask=True,
        label_smoothing=True,
        alpha=0.1,
        beta=0.01,
    )
    model = ConvAEC(params)
    state_dict = torch.load(MODEL_PKL, map_location='cpu')
    model.load_state_dict(state_dict)
    model.eval()

    dummy = torch.randn(4, 100, 1)
    with torch.no_grad():
        x_hat, x_out, x_enc = model(dummy)

    assert x_hat.shape == (4, 100, 1)
    assert x_out.shape == (4, 12)
    assert x_enc.shape == (4, 128, 1)

    # Verify softmax property (sum to 1)
    sums = torch.sum(x_out, dim=1).numpy()
    np.testing.assert_allclose(sums, np.ones(4), atol=1e-5)

def test_raw_threshold_detection():
    """Verify threshold logic using raw MSE on normal reference vs test portion."""
    input_npy = f"{SAVED_TEST_DIR}/input.npy"
    pred_npy = f"{SAVED_TEST_DIR}/pred.npy"
    test_inputs = np.load(input_npy)
    test_preds = np.load(pred_npy)

    raw_mse = mse(test_inputs.reshape(len(test_inputs), -1), test_preds.reshape(len(test_preds), -1))
    
    # Check that maximum anomaly score is significantly higher than median
    assert raw_mse.max() > 3 * np.median(raw_mse)
