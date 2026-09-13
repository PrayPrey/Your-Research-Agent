"""Quick self-tests for H-E1 core logic. Runs without GPU or network."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import torch
import numpy as np


def test_compute_erank():
    from erank import compute_erank
    # Identity matrix -> all singular values equal -> max entropy -> erank = n
    W = torch.eye(4)
    r = compute_erank(W)
    assert abs(r - 4.0) < 0.01, f"erank(I_4) should be ~4, got {r}"

    # Rank-1 matrix -> erank = 1
    W2 = torch.zeros(4, 4)
    W2[0, 0] = 1.0
    r2 = compute_erank(W2)
    assert abs(r2 - 1.0) < 0.01, f"erank(rank-1) should be ~1, got {r2}"
    print("  test_compute_erank PASSED")


def test_pearson_one_tailed():
    from analyze import pearson_one_tailed
    x = list(range(10))
    y = list(range(10))
    r, p = pearson_one_tailed(x, y)
    assert abs(r - 1.0) < 1e-6, f"perfect correlation r should be 1, got {r}"
    assert p < 0.05, f"p should be <0.05 for perfect correlation, got {p}"
    print("  test_pearson_one_tailed PASSED")


def test_bootstrap_ci():
    from analyze import bootstrap_ci
    x = list(range(20))
    y = [xi + 0.1 * i for i, xi in enumerate(x)]
    ci_low, ci_high = bootstrap_ci(x, y, n_resamples=200, seed=0)
    assert ci_low < ci_high, "CI low should be < CI high"
    assert ci_low > 0.5, f"CI low should be >0.5 for near-perfect corr, got {ci_low}"
    print("  test_bootstrap_ci PASSED")


def test_check_global_success():
    from analyze import check_global_success
    results = {
        "bert": {"pass": True},
        "deberta": {"pass": True},
        "vit": {"pass": False},
    }
    assert check_global_success(results) is True
    results2 = {
        "bert": {"pass": False},
        "deberta": {"pass": False},
        "vit": {"pass": True},
    }
    assert check_global_success(results2) is False
    print("  test_check_global_success PASSED")


def test_layer_to_safe():
    from oracle import layer_to_safe, build_oracle_state_key
    assert layer_to_safe("encoder.layer.0.attention.self.query") == "encoder__layer__0__attention__self__query"
    key = build_oracle_state_key("bert-base-uncased", "encoder__layer__0__attention__self__query", 8, 42)
    assert "r8" in key and "s42" in key
    print("  test_layer_to_safe PASSED")


def test_config_from_model():
    from config import ExperimentConfig
    cfg = ExperimentConfig.from_model("bert-base-uncased", Path("/tmp/test_output"))
    assert cfg.model_name == "bert-base-uncased"
    assert cfg.epochs_nlp == 3
    assert cfg.baseline_rank == 8
    assert 4 in cfg.oracle_ranks
    print("  test_config_from_model PASSED")


def test_participation_ratio():
    from analyze import participation_ratio
    W = torch.eye(4)
    pr = participation_ratio(W)
    assert abs(pr - 4.0) < 0.01, f"PR(I_4) should be 4, got {pr}"
    print("  test_participation_ratio PASSED")


if __name__ == "__main__":
    print("Running H-E1 self-tests...")
    test_compute_erank()
    test_pearson_one_tailed()
    test_bootstrap_ci()
    test_check_global_success()
    test_layer_to_safe()
    test_config_from_model()
    test_participation_ratio()
    print("\nAll tests PASSED")
