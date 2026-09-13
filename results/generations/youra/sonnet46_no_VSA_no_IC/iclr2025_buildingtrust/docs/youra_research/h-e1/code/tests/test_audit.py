"""Spec compliance tests for audit.py."""
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from code.audit import check_protocol_consistency, run_h_e1_audit
from code.config import REQUIRED_COLS


def _make_matrix(n_models: int, n_complete: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Create matrix with n_complete rows having all 7 cols, rest partially filled."""
    models = [f"Model-{i}" for i in range(n_models)]
    data = {}
    for col in REQUIRED_COLS:
        vals = [0.6 + i * 0.01 for i in range(n_models)]
        # Make non-complete rows have NaN in MMLU
        for i in range(n_complete, n_models):
            if col == "MMLU":
                vals[i] = float("nan")
        data[col] = vals
    df = pd.DataFrame(data, index=models)
    attr = pd.DataFrame(
        {col: ["TrustLLM"] * n_models for col in REQUIRED_COLS}, index=models
    )
    return df, attr


def test_run_h_e1_audit_gate_pass():
    df, attr = _make_matrix(15, 12)
    result = run_h_e1_audit(df, attr, {})
    assert result["N_common"] == 12
    assert result["gate_passed"] is True


def test_run_h_e1_audit_gate_fail():
    df, attr = _make_matrix(12, 5)
    result = run_h_e1_audit(df, attr, {})
    assert result["N_common"] == 5
    assert result["gate_passed"] is False


def test_run_h_e1_audit_pair_counts():
    df, attr = _make_matrix(10, 10)
    result = run_h_e1_audit(df, attr, {})
    assert result["pair_counts"]["BBQ-Disambig/BBQ-Ambig"] == 10
    assert result["pair_counts"]["ANLI-R1/ANLI-R3"] == 10


def test_run_h_e1_audit_mmlu_coverage():
    df, attr = _make_matrix(10, 10)
    result = run_h_e1_audit(df, attr, {})
    assert result["mmlu_coverage"] == pytest.approx(1.0)


def test_check_protocol_consistency_all_within():
    score_dicts = {
        "TrustLLM": {"ModelA": {"BBQ-Disambig": 0.80}},
        "DecodingTrust": {"ModelA": {"BBQ-Disambig": 0.82}},  # delta = 2pp
    }
    warnings, fraction = check_protocol_consistency(score_dicts, threshold_pp=5.0)
    assert len(warnings) == 0
    assert fraction == pytest.approx(1.0)


def test_check_protocol_consistency_flagged():
    score_dicts = {
        "TrustLLM": {"ModelA": {"BBQ-Disambig": 0.80}},
        "DecodingTrust": {"ModelA": {"BBQ-Disambig": 0.68}},  # delta = 12pp
    }
    warnings, fraction = check_protocol_consistency(score_dicts, threshold_pp=5.0)
    assert len(warnings) == 1
    assert warnings[0]["delta_pp"] == pytest.approx(12.0, abs=0.1)
    assert fraction == pytest.approx(0.0)


def test_run_h_e1_audit_returns_complete_matrix():
    df, attr = _make_matrix(15, 11)
    result = run_h_e1_audit(df, attr, {})
    assert len(result["complete_matrix"]) == 11
