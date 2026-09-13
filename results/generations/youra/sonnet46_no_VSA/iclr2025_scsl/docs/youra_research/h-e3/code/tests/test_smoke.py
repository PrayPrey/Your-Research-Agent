"""Smoke test: imports, shapes, and a mini Hutchinson trace on CPU."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import torch
import pytest


def test_config_imports():
    import config
    assert config.N_EPOCHS == 50
    assert 0 in config.CHECKPOINT_EPOCHS


def test_build_model():
    from train_erm import build_model
    import config
    model = build_model()
    from compute_traces import verify_architecture
    verify_architecture(model)


def test_backbone_forward():
    from train_erm import build_model
    from compute_traces import model_backbone_forward
    model = build_model()
    x = torch.randn(2, 3, 224, 224)
    feats = model_backbone_forward(model, x)
    assert feats.shape == (2, 2048)


def test_hutchinson_mini():
    """Mini Hutchinson trace on a tiny synthetic batch (CPU)."""
    from train_erm import build_model
    from compute_traces import compute_per_sample_fc_trace
    from torch.utils.data import DataLoader, TensorDataset

    model = build_model().eval()

    # Synthetic DataLoader: 8 samples
    imgs = torch.randn(8, 3, 224, 224)
    labels = torch.randint(0, 2, (8,))
    groups = torch.zeros(8, dtype=torch.long)
    ds = TensorDataset(imgs, labels, groups)
    loader = DataLoader(ds, batch_size=4, shuffle=False)

    traces = compute_per_sample_fc_trace(model, loader, K=3, device="cpu")
    assert traces.shape == (8,), f"Expected (8,), got {traces.shape}"
    assert torch.isfinite(traces).all(), "Traces contain NaN/Inf"


def test_auroc_and_R():
    from evaluate_trajectory import compute_auroc, compute_R
    traces = torch.tensor([0.1, 0.5, 0.9, 0.3, 0.8])
    minority_mask = torch.tensor([False, True, True, False, True])
    auroc = compute_auroc(traces, minority_mask)
    assert 0.0 <= auroc <= 1.0
    R = compute_R(traces, minority_mask)
    assert R > 0


def test_spearman():
    from evaluate_trajectory import compute_spearman
    rho, p = compute_spearman([0, 1, 5, 10], [0.55, 0.60, 0.72, 0.80])
    assert -1 <= rho <= 1
