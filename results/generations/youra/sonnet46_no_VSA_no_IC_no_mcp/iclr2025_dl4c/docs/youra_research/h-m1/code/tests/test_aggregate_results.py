"""Tests for aggregate_results.py"""
import json
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from aggregate_results import load_all_results, verify_signal_void_mechanism, write_signal_void_analysis


def test_verify_signal_void_pass_when_low_pass1():
    """Returns True when pass@1 = 0.35 < 0.60."""
    results = {
        "lcb": {"pass@1": 0.35},
        "loss": {
            "introductory": {"mean": 1.2, "std": 0.3, "count": 100},
            "competition": {"mean": 2.5, "std": 0.5, "count": 50},
        },
        "coverage": {"coverage_pct": 5.0, "total": 100, "solvable": 5},
    }
    success, indicators = verify_signal_void_mechanism(results)
    assert success is True
    assert indicators["signal_void_primary"] is True
    assert indicators["gate_satisfied"] is True


def test_verify_signal_void_fail_when_high_pass1():
    """Returns False when pass@1 = 0.65 >= 0.60."""
    results = {"lcb": {"pass@1": 0.65}, "loss": None, "coverage": None}
    success, indicators = verify_signal_void_mechanism(results)
    assert success is False
    assert indicators["signal_void_primary"] is False


def test_output_json_matches_schema(tmp_path):
    """Output JSON matches SIGNAL_VOID_SCHEMA."""
    results = {
        "lcb": {"pass@1": 0.20},
        "loss": {
            "introductory": {"mean": 1.1, "std": 0.2, "count": 500},
            "interview": {"mean": 1.8, "std": 0.4, "count": 500},
            "competition": {"mean": 2.7, "std": 0.6, "count": 300},
        },
        "coverage": {"coverage_pct": 7.7, "total": 600, "solvable": 46},
    }
    success, indicators = verify_signal_void_mechanism(results)
    out = str(tmp_path / "analysis.json")
    write_signal_void_analysis(indicators, out)

    with open(out) as f:
        saved = json.load(f)

    required_keys = [
        "sft_lcb_hard_pass1",
        "signal_void_primary",
        "apps_difficulty_loss",
        "loss_gradient_secondary",
        "apps_competition_coverage",
        "coverage_void_secondary",
        "gate_satisfied",
    ]
    for k in required_keys:
        assert k in saved, f"Missing key: {k}"
