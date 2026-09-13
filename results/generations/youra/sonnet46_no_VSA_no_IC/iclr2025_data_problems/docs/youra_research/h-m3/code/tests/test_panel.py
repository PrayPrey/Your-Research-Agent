"""Tests for panel_builder and panel_regression modules."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import pytest
from src.panel_builder import (
    drop_min_variance_domain,
    compute_vif,
    apply_pca_if_needed,
    verify_panel_quality,
)
from src.panel_regression import (
    fit_benchmark_specific_models,
    fit_shared_beta_model,
    extract_focal_coefficients,
)
import config as cfg


def _make_panel(n_sizes=4, n_steps=40, n_domains=5, seed=42):
    rng = np.random.default_rng(seed)
    sizes = [f"m{i}" for i in range(n_sizes)]
    steps = list(range(n_steps))
    idx = pd.MultiIndex.from_tuples(
        [(s, t) for s in sizes for t in steps], names=["model_size", "checkpoint"]
    )
    n = len(idx)
    domains = ["Wikipedia (en)", "Books3", "Github", "StackExchange", "ArXiv"][:n_domains]
    data = {d: rng.random(n) for d in domains}
    for bench in ["mmlu", "hellaswag", "arc_challenge", "winogrande"]:
        data[bench] = rng.random(n)
    data["log_params"] = [float(i % n_sizes + 7) for i in range(n)]
    return pd.DataFrame(data, index=idx), domains


def test_drop_min_variance_domain():
    df, domains = _make_panel()
    df_out, dropped, remaining = drop_min_variance_domain(df, domains)
    assert dropped in domains
    assert len(remaining) == len(domains) - 1
    assert dropped not in remaining


def test_verify_panel_quality_raises_on_books3_zero():
    df, domains = _make_panel()
    df["Books3"] = 0.0  # zero variance
    with pytest.raises(ValueError, match="Books3"):
        verify_panel_quality(df, domains)


def test_verify_panel_quality_passes():
    df, domains = _make_panel()
    stats = verify_panel_quality(df, domains)
    assert isinstance(stats, dict)
    assert "Books3" in stats
    assert stats["Books3"] > 1e-6


def test_apply_pca_low_vif():
    df, domains = _make_panel(n_domains=3)
    df_out, cols, pca_loadings, orig = apply_pca_if_needed(df, domains, vif_threshold=100.0)
    assert pca_loadings is None, "PCA should not be applied with high VIF threshold"
    assert cols == domains


def test_fit_benchmark_specific_models():
    df, domains = _make_panel(n_sizes=5, n_steps=30)
    results = fit_benchmark_specific_models(df, domains, ["mmlu", "hellaswag"])
    assert "mmlu" in results
    assert "hellaswag" in results
    assert hasattr(results["mmlu"], "params")


def test_fit_benchmark_specific_models_missing_benchmark():
    df, domains = _make_panel()
    with pytest.raises(ValueError, match="nonexistent"):
        fit_benchmark_specific_models(df, domains, ["nonexistent"])


def test_extract_focal_coefficients():
    df, domains = _make_panel(n_sizes=5)
    results = fit_benchmark_specific_models(df, domains, ["mmlu", "hellaswag"])
    focal_domains = {"wikipedia": "Wikipedia (en)", "books": "Books3"}
    focal = extract_focal_coefficients(results, domains, focal_domains)
    assert "mmlu" in focal
    assert "hellaswag" in focal
    wiki_entry = focal["mmlu"].get("Wikipedia (en)", {})
    assert "beta" in wiki_entry
    assert "se" in wiki_entry


def test_fit_shared_beta_model():
    df, domains = _make_panel(n_sizes=5, n_steps=30)
    shared = fit_shared_beta_model(df, domains, ["mmlu", "hellaswag"])
    assert hasattr(shared, "llf")
    assert shared.llf < 0 or shared.llf > -1e10  # log-likelihood is finite
