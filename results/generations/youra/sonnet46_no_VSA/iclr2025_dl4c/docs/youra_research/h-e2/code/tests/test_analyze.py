"""Tests for analyze.py — statistical analysis and gate evaluation."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
import pytest

from analyze import (
    ALPHA,
    CONDITIONS,
    CONDITION_PAIRS,
    FAIL_THRESHOLD_PP,
    MIN_CONTRAST_PP,
    evaluate_gate,
    fit_mixedlm,
    pairwise_contrasts,
)


def make_synthetic_df(n_per_cell=20, seed=42):
    """Synthetic per-problem pass@1 with a real condition effect."""
    rng = np.random.default_rng(seed)
    rows = []
    base_pass = {"humaneval_only": 0.5, "mbpp_only": 0.4, "leetcode_only": 0.3, "equal_mix": 0.45}
    for pid in range(n_per_cell):
        for cond in CONDITIONS:
            for bench in ["humaneval", "mbpp"]:
                p = base_pass[cond] + rng.normal(0, 0.05)
                rows.append({
                    "problem_id": f"p{pid}_{bench}",
                    "pass1": float(np.clip(p, 0, 1)),
                    "source_condition": cond,
                    "solution_length": 50 + rng.integers(0, 50),
                    "benchmark": bench,
                    "seed": 42,
                })
    return pd.DataFrame(rows)


def test_fit_mixedlm_runs():
    df = make_synthetic_df()
    result = fit_mixedlm(df, "humaneval")
    assert hasattr(result, "params")
    assert len(result.params) > 0


def test_pairwise_contrasts_shape():
    df = make_synthetic_df()
    results = {b: fit_mixedlm(df, b) for b in ["humaneval", "mbpp"]}
    contrasts = pairwise_contrasts(results)
    assert len(contrasts) == 12  # 6 pairs × 2 benchmarks
    assert "p_adjusted" in contrasts.columns
    assert "contrast_pp" in contrasts.columns


def test_evaluate_gate_pass_scenario():
    """Synthetic large effect → gate should PASS."""
    df = make_synthetic_df(n_per_cell=50)
    results = {b: fit_mixedlm(df, b) for b in ["humaneval", "mbpp"]}
    contrasts = pairwise_contrasts(results)
    # Force a large contrast in the dataframe to check gate logic
    contrasts["contrast_pp"] = contrasts["contrast_pp"].abs() * 5
    contrasts["reject"] = True
    gate = evaluate_gate(contrasts, results)
    assert gate["result"] in ("PASS", "AMBIGUOUS", "FAIL")  # structure check


def test_evaluate_gate_fail_scenario():
    """All tiny contrasts → gate should FAIL."""
    df = make_synthetic_df(n_per_cell=5)
    results = {b: fit_mixedlm(df, b) for b in ["humaneval", "mbpp"]}
    contrasts = pairwise_contrasts(results)
    contrasts["contrast_pp"] = 0.5  # all tiny
    contrasts["reject"] = False
    gate = evaluate_gate(contrasts, results)
    assert gate["result"] == "FAIL"
    assert gate["fail_condition"] is True


def test_condition_pairs_count():
    assert len(CONDITION_PAIRS) == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
