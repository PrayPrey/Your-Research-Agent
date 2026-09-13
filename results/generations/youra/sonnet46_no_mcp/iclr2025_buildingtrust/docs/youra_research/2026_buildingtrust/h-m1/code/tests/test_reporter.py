import sys
import os
import json
import tempfile
from pathlib import Path
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from reporter import write_results_json, write_validation_md


@pytest.fixture
def mock_results():
    internal = {"rho": 0.72, "pval": 0.0001, "bca_ci_low": 0.45, "bca_ci_high": 0.88, "passes_threshold": True}
    primary = {"rho_partial": -0.58, "pval": 0.002, "bca_ci_low": -0.78, "bca_ci_high": -0.32,
               "ci_excludes_zero": True, "passes_threshold": True}
    confound = {"raw_rho": -0.76, "partial_rho": -0.58, "survival_fraction": 0.76,
                "confound_fraction": 0.24, "interpretation": "MMLU explains <50%"}
    discriminant = {"rho_partial": 0.08, "bca_ci_low": -0.12, "bca_ci_high": 0.28, "passes_threshold": True}
    invariance = {"rho_greedy": float("nan"), "rho_t07": float("nan"),
                  "delta_rho": float("nan"), "passes_threshold": False, "skipped": True}
    return internal, primary, confound, discriminant, invariance


def test_write_results_json_valid(tmp_path, mock_results):
    internal, primary, confound, discriminant, invariance = mock_results
    out = tmp_path / "hm1_results.json"
    write_results_json(internal, primary, confound, discriminant, invariance, True, out)
    assert out.exists()
    data = json.loads(out.read_text())
    assert "gate_pass" in data
    assert "primary_gate" in data
    assert "internal_consistency" in data


def test_write_validation_md_exists(tmp_path, mock_results):
    internal, primary, confound, discriminant, invariance = mock_results
    out = tmp_path / "04_validation.md"
    write_validation_md(internal, primary, confound, discriminant, invariance, True, out)
    assert out.exists()
    content = out.read_text()
    assert len(content) > 100


def test_gate_pass_reflected(tmp_path, mock_results):
    internal, primary, confound, discriminant, invariance = mock_results
    out = tmp_path / "hm1_results.json"
    write_results_json(internal, primary, confound, discriminant, invariance, True, out)
    data = json.loads(out.read_text())
    assert data["gate_pass"] is True


def test_gate_fail_reflected(tmp_path, mock_results):
    internal, primary, confound, discriminant, invariance = mock_results
    out = tmp_path / "hm1_results_fail.json"
    write_results_json(internal, primary, confound, discriminant, invariance, False, out)
    data = json.loads(out.read_text())
    assert data["gate_pass"] is False
