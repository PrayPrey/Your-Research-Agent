"""Tests for h-m1 evaluate.py (tasks 015, 016)."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import torch
from torch.utils.data import TensorDataset, DataLoader
from models import FlatMLPEncoder, FlatMLPWithHead
from evaluate import compute_spearman, run_gate_check, save_results
from config import ExperimentConfig
import tempfile


def _make_model_and_loader(n=50, dim=32):
    enc = FlatMLPEncoder(dim, [16], 8)
    model = FlatMLPWithHead(enc, 8)
    x = torch.randn(n, dim)
    y = torch.rand(n)
    loader = DataLoader(TensorDataset(x, y), batch_size=16)
    return model, loader


def test_spearman_range():
    model, loader = _make_model_and_loader()
    rho = compute_spearman(model, loader, torch.device("cpu"))
    assert -1.0 <= rho <= 1.0


def test_spearman_perfect():
    """Model that returns input[0] as prediction; labels = input[0]."""
    enc = FlatMLPEncoder(1, [], 1)
    # Make model output identity by zeroing weights and setting bias
    with torch.no_grad():
        enc.net[0].weight.fill_(1.0)
        enc.net[0].bias.fill_(0.0)
    model = FlatMLPWithHead(enc, 1)
    with torch.no_grad():
        model.head.weight.fill_(1.0)
        model.head.bias.fill_(0.0)
    vals = torch.linspace(0, 1, 30).unsqueeze(1)
    loader = DataLoader(TensorDataset(vals, vals.squeeze()), batch_size=10)
    rho = compute_spearman(model, loader, torch.device("cpu"))
    assert rho > 0.9


def test_gate_pass_above_threshold():
    cfg = ExperimentConfig()
    result = run_gate_check(0.5, 0.6, 500_000, 100, cfg)
    assert result["gate_pass"] is True


def test_gate_fail_below_threshold():
    cfg = ExperimentConfig()
    result = run_gate_check(0.2, 0.4, 500_000, 100, cfg)
    assert result["gate_pass"] is False


def test_save_results_json():
    cfg = ExperimentConfig()
    with tempfile.TemporaryDirectory() as d:
        cfg.results_dir = Path(d)
        results = {"gate_pass": True, "sensitivity_score": 0.5, "spearman_rho": 0.6,
                   "param_count": 500000, "n_pairs": 100,
                   "param_in_range": True, "pairs_sufficient": True,
                   "gate_threshold": 0.3, "spearman_target": 0.5}
        save_results(results, cfg)
        out = Path(d) / "h-m1_results.json"
        assert out.exists()
        with open(out) as f:
            data = json.load(f)
        assert "gate_pass" in data
