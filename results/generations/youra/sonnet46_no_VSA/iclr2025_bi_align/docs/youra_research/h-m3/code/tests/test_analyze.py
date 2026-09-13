"""Tests for H-M3 analyze.py — scenario classification and mechanism verification."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from config import ExperimentConfig
from analyze import assign_scenario, verify_mechanism_activated, tier3_analysis, ablation_boundary
import numpy as np


@pytest.fixture
def cfg():
    return ExperimentConfig()


class TestAssignScenario:
    def test_scenario_b_high_positive(self, cfg):
        r = assign_scenario(0.50, 0.42, 0.58, cfg)
        assert r["scenario"] == "b"
        assert not r["is_ambiguous"]

    def test_scenario_c_negative(self, cfg):
        r = assign_scenario(-0.35, -0.50, -0.22, cfg)
        assert r["scenario"] == "c"
        assert not r["is_ambiguous"]

    def test_scenario_a_near_zero(self, cfg):
        r = assign_scenario(0.05, -0.05, 0.15, cfg)
        assert r["scenario"] == "ambiguous"  # grey zone: -0.20 < 0.05 < 0.40

    def test_scenario_a_true_independent(self, cfg):
        # |rho| < 0.20 AND NOT in grey zone would be -0.20 < rho < +0.20
        # But grey zone is -0.20 < rho < +0.40, so scenario a is unreachable directly
        # Test that grey zone supercedes scenario a
        r = assign_scenario(0.10, 0.05, 0.15, cfg)
        assert r["scenario"] == "ambiguous"

    def test_ambiguous_grey_zone(self, cfg):
        r = assign_scenario(0.343, 0.180, 0.492, cfg)
        assert r["scenario"] == "ambiguous"
        assert r["is_ambiguous"]

    def test_ambiguous_ci_spans_boundaries(self, cfg):
        # CI spans 0 and 0.40: ci_lo < 0 and ci_hi > 0.40
        r = assign_scenario(0.20, -0.10, 0.55, cfg)
        assert r["scenario"] == "ambiguous"
        assert r["is_ambiguous"]

    def test_narrative_generated(self, cfg):
        r = assign_scenario(0.50, 0.42, 0.58, cfg)
        assert isinstance(r["narrative"], str) and len(r["narrative"]) > 10

    def test_invalid_ci_order(self, cfg):
        with pytest.raises(ValueError, match="ci_lo"):
            assign_scenario(0.50, 0.60, 0.40, cfg)

    def test_invalid_rho_range(self, cfg):
        with pytest.raises(ValueError, match="partial_rho"):
            assign_scenario(1.5, 0.40, 0.60, cfg)


class TestVerifyMechanismActivated:
    def test_all_pass(self, cfg):
        results = {
            "partial_rho": 0.343,
            "ci_partial": [0.18, 0.49],
            "scenario": "ambiguous",
            "narrative": "This is a valid narrative string for testing.",
        }
        ok, indicators = verify_mechanism_activated(results)
        assert ok
        assert all(indicators.values())

    def test_missing_scenario(self, cfg):
        results = {
            "partial_rho": 0.343,
            "ci_partial": [0.18, 0.49],
            "narrative": "test narrative string here",
        }
        ok, indicators = verify_mechanism_activated(results)
        assert not ok
        assert not indicators["scenario_assigned"]

    def test_invalid_ci(self, cfg):
        results = {
            "partial_rho": 0.343,
            "ci_partial": [0.49, 0.18],  # reversed
            "scenario": "ambiguous",
            "narrative": "test narrative string here",
        }
        ok, indicators = verify_mechanism_activated(results)
        assert not ok
        assert not indicators["ci_bounds_valid"]


class TestTier3Analysis:
    def test_basic_output_keys(self):
        delta = np.array([0.01, -0.02, 0.03, 0.04, -0.01] * 40)
        result = tier3_analysis(delta)
        for k in ["k_positive", "n", "p_value", "direction"]:
            assert k in result

    def test_positive_dominant(self):
        delta = np.abs(np.random.default_rng(42).normal(0.05, 0.01, 200))
        result = tier3_analysis(delta)
        assert result["k_positive"] > result["n"] / 2


class TestAblationBoundary:
    def test_tight_wide_keys(self, cfg):
        r = ablation_boundary(0.50, 0.42, 0.58, cfg)
        assert "tight" in r and "wide" in r
        assert "scenario" in r["tight"]
        assert "scenario" in r["wide"]

    def test_scenario_b_in_all_variants(self, cfg):
        # 0.50 > 0.45 (wide_b) → scenario b in all variants
        r = ablation_boundary(0.50, 0.42, 0.58, cfg)
        assert r["tight"]["scenario"] == "b"
        assert r["wide"]["scenario"] == "b"
