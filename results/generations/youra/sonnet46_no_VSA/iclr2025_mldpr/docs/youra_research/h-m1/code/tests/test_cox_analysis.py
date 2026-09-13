"""Spec-compliance tests for cox_analysis module."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from config import CoxConfig
from cox_analysis import LRTResult, run_lrt


def _make_mock_cph(ll, hr=0.87, ci_lower_log=-0.5, ci_upper_log=0.3, concordance=0.6):
    """Create a mock CoxPHFitter with the required attributes."""
    m = MagicMock()
    m.log_likelihood_ = ll
    m.concordance_index_ = concordance
    m.hazard_ratios_ = pd.Series({"log_unique_paper_count_at_intro_z": hr})
    m.confidence_intervals_ = pd.DataFrame(
        {"lower 0.95": [ci_lower_log], "upper 0.95": [ci_upper_log]},
        index=["log_unique_paper_count_at_intro_z"]
    )
    return m


def test_lrt_result_is_dataclass():
    cfg = CoxConfig()
    M0 = _make_mock_cph(-200.0)
    M1 = _make_mock_cph(-195.0)
    result = run_lrt(M0, M1, cfg)
    assert isinstance(result, LRTResult)


def test_lrt_stat_is_positive_when_m1_better():
    cfg = CoxConfig()
    M0 = _make_mock_cph(-200.0)
    M1 = _make_mock_cph(-195.0)
    result = run_lrt(M0, M1, cfg)
    assert result.lrt_stat > 0
    assert result.p_value >= 0 and result.p_value <= 1


def test_lrt_gate_pass():
    """Large LRT stat → small p, large |HR-1| → gate passes."""
    cfg = CoxConfig()
    M0 = _make_mock_cph(-200.0)
    # HR far from 1, ll much higher for M1
    M1 = _make_mock_cph(-185.0, hr=0.5, ci_lower_log=-1.5, ci_upper_log=-0.1)
    result = run_lrt(M0, M1, cfg)
    assert result.gate_passed, f"Expected gate PASS, got p={result.p_value:.4f}, |HR-1|={result.abs_effect:.4f}"


def test_lrt_gate_fail():
    """Tiny LRT stat → large p → gate fails."""
    cfg = CoxConfig()
    M0 = _make_mock_cph(-200.0)
    M1 = _make_mock_cph(-200.001, hr=0.99, ci_lower_log=-0.1, ci_upper_log=0.1)
    result = run_lrt(M0, M1, cfg)
    assert not result.gate_passed


def test_direction_h1():
    """p < 0.05, HR < 1 → H1."""
    cfg = CoxConfig()
    M0 = _make_mock_cph(-200.0)
    M1 = _make_mock_cph(-185.0, hr=0.5, ci_lower_log=-1.5, ci_upper_log=-0.1)
    result = run_lrt(M0, M1, cfg)
    assert result.direction == "H1"


def test_direction_h2():
    """p < 0.05, HR > 1 → H2."""
    cfg = CoxConfig()
    M0 = _make_mock_cph(-200.0)
    M1 = _make_mock_cph(-185.0, hr=1.5, ci_lower_log=0.1, ci_upper_log=1.5)
    result = run_lrt(M0, M1, cfg)
    assert result.direction == "H2"


def test_direction_h0():
    """p ≥ 0.05 → H0."""
    cfg = CoxConfig()
    M0 = _make_mock_cph(-200.0)
    M1 = _make_mock_cph(-200.001, hr=0.99, ci_lower_log=-0.1, ci_upper_log=0.1)
    result = run_lrt(M0, M1, cfg)
    assert result.direction == "H0"


def test_lrt_clips_negative_stat():
    """Negative lrt_stat (M1 worse under L2) clipped to 0."""
    cfg = CoxConfig()
    M0 = _make_mock_cph(-195.0)  # M0 better
    M1 = _make_mock_cph(-200.0)  # M1 worse
    # Should not raise; lrt_stat clipped to 0
    result = run_lrt(M0, M1, cfg)
    assert result.lrt_stat == 0.0


def test_non_finite_ll_raises():
    cfg = CoxConfig()
    M0 = _make_mock_cph(float("nan"))
    M1 = _make_mock_cph(-195.0)
    with pytest.raises(ValueError, match="Non-finite"):
        run_lrt(M0, M1, cfg)


def test_lrt_result_fields():
    """All required fields present in LRTResult."""
    cfg = CoxConfig()
    M0 = _make_mock_cph(-200.0)
    M1 = _make_mock_cph(-195.0)
    result = run_lrt(M0, M1, cfg)
    for field in ("lrt_stat", "p_value", "HR", "CI_lower", "CI_upper",
                  "abs_effect", "concordance", "M0_log_likelihood",
                  "M1_log_likelihood", "direction", "gate_passed"):
        assert hasattr(result, field), f"Missing field: {field}"
