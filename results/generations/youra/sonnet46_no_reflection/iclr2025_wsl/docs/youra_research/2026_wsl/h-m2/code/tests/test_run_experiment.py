"""Tests for run_experiment.py — task-009."""
import pytest
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from run_experiment import setup_paths, generate_validation_report
from config import ExperimentConfig


def test_setup_paths_creates_dirs(tmp_path):
    cfg = ExperimentConfig()
    cfg.figures_dir = str(tmp_path / "figures")
    cfg.results_dir = str(tmp_path / "results")
    cfg.h_m1_code_path = str(tmp_path / "nonexistent")
    setup_paths(cfg)
    assert Path(cfg.figures_dir).exists()
    assert Path(cfg.results_dir).exists()


def make_results(gate_pass=True):
    return {
        "hypothesis_id": "h-m2",
        "completed_at": "2026-05-21T12:00:00",
        "var_ratio_mean": 0.72 if gate_pass else 0.45,
        "var_ratio_std": 0.05,
        "n_models": 250,
        "ratio_cifar10": 0.72 if gate_pass else 0.45,
        "ratio_svhn": 0.69 if gate_pass else 0.43,
        "stability_gap": 0.03,
        "gate_pass": gate_pass,
        "orbit_basis_dim": 64,
        "mechanism_verified": True,
        "mechanism_indicators": {
            "n_trajectories_gt_100": True,
            "orbit_basis_dim_gt_0": True,
            "var_ratio_in_range": True,
            "var_perm_positive": True,
            "var_gl_positive": True,
        },
        "gate": {
            "all_pass": gate_pass,
            "primary_pass": gate_pass,
            "n_models_pass": True,
            "non_degenerate_pass": True,
            "stability_pass": True,
            "ratio_mean": 0.72 if gate_pass else 0.45,
            "ratio_std": 0.05,
            "n_models": 250,
            "stability_gap": 0.03,
        },
    }


def test_generate_validation_report_pass(tmp_path):
    results = make_results(gate_pass=True)
    out = str(tmp_path / "04_validation.md")
    generate_validation_report(results, out)
    assert Path(out).exists()
    content = Path(out).read_text()
    assert "PASS" in content
    assert "0.7200" in content


def test_generate_validation_report_fail_with_pivot(tmp_path):
    results = make_results(gate_pass=False)
    out = str(tmp_path / "04_validation.md")
    generate_validation_report(results, out)
    content = Path(out).read_text()
    assert "FAIL" in content
    assert "PIVOT" in content


def test_generate_validation_report_has_required_sections(tmp_path):
    results = make_results()
    out = str(tmp_path / "04_validation.md")
    generate_validation_report(results, out)
    content = Path(out).read_text()
    required_sections = [
        "## Summary",
        "## Gate Decision",
        "## Key Findings",
        "## Mechanism Activation Indicators",
        "## Files Generated",
    ]
    for section in required_sections:
        assert section in content, f"Missing section: {section}"
