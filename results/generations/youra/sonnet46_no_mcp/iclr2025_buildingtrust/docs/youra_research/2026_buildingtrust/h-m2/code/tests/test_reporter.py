import pytest
import json
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import reporter
import config
import numpy as np


@pytest.fixture
def sample_results():
    partial = {
        "rho_partial_advglue": -0.65,
        "bca_ci_low": -0.85,
        "bca_ci_high": -0.35,
        "ci_excludes_zero": True,
        "passes_threshold": True,
        "rho_partial_anli": -0.50,
        "anli_bca_ci_low": -0.75,
        "anli_bca_ci_high": -0.15,
    }
    composite = {
        "auc": 0.78,
        "y_proba": np.array([0.3, 0.7, 0.4, 0.9, 0.6, 0.2, 0.8, 0.5, 0.35, 0.65]),
        "y_true": np.array([0, 1, 0, 1, 1, 0, 1, 0, 0, 1]),
        "feature_cols": config.COMPOSITE_COLS,
    }
    baseline = {
        "auc": 0.62,
        "y_proba": np.array([0.4, 0.5, 0.45, 0.7, 0.55, 0.3, 0.6, 0.5, 0.4, 0.6]),
        "y_true": np.array([0, 1, 0, 1, 1, 0, 1, 0, 0, 1]),
        "feature_cols": config.BASELINE_COLS,
    }
    delta = {
        "auc_composite": 0.78,
        "auc_baseline": 0.62,
        "delta_auc": 0.16,
        "delta_auc_ci": [0.05, 0.27],
        "ci_excludes_zero": True,
        "passes_delta_threshold": True,
        "passes_auc_threshold": True,
    }
    return partial, composite, baseline, delta


def test_write_results_json_creates_file(sample_results, results_dir):
    partial, composite, baseline, delta = sample_results
    path = results_dir / "hm2_results.json"
    reporter.write_results_json(partial, composite, baseline, delta, True, path)
    assert path.exists()
    data = json.loads(path.read_text())
    assert "gate_pass" in data
    assert data["gate_pass"] is True
    assert "partial_rho" in data
    assert "delta_bootstrap" in data


def test_write_results_json_valid_json(sample_results, results_dir):
    partial, composite, baseline, delta = sample_results
    path = results_dir / "hm2_results.json"
    reporter.write_results_json(partial, composite, baseline, delta, True, path)
    # Must be valid JSON with all gate metric keys
    data = json.loads(path.read_text())
    assert "composite_auc" in data
    assert "baseline_auc" in data


def test_write_validation_md_creates_file(sample_results, results_dir):
    partial, composite, baseline, delta = sample_results
    path = results_dir / "04_validation.md"
    reporter.write_validation_md(partial, composite, baseline, delta, True, path)
    assert path.exists()
    content = path.read_text()
    assert "PASS" in content or "PARTIAL" in content or "EXPLORE" in content
    assert "H-M2" in content


def test_write_validation_md_gate_result_explicit(sample_results, results_dir):
    partial, composite, baseline, delta = sample_results
    path = results_dir / "04_validation.md"
    reporter.write_validation_md(partial, composite, baseline, delta, True, path)
    content = path.read_text()
    # Gate result must be explicit
    assert any(label in content for label in ["PASS", "PARTIAL", "EXPLORE"])
    # Metric values must be reported
    assert "0.78" in content or "0.7800" in content
