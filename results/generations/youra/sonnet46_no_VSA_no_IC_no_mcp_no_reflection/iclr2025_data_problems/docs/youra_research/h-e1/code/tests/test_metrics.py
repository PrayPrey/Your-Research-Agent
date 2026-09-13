"""Tests for metrics.py — spec compliance."""
import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import numpy as np
import pytest
from metrics import compute_ratio, compute_arc_delta, bootstrap_ratio_diff, cohens_d, evaluate_hypothesis


def _make_results(mmlu_acc: float, hellaswag_acc: float, arc_easy: float, arc_challenge_norm: float) -> dict:
    """Build a minimal lm-eval-style results dict with 57 MMLU subjects."""
    r = {}
    subjects = [f"mmlu_subject_{i:02d}" for i in range(57)]
    for s in subjects:
        r[s] = {"acc,none": mmlu_acc, "acc_stderr,none": 0.01}
    r["hellaswag"] = {"acc,none": hellaswag_acc, "acc_norm,none": hellaswag_acc + 0.05}
    r["arc_easy"] = {"acc,none": arc_easy, "acc_norm,none": arc_easy + 0.02}
    r["arc_challenge"] = {"acc,none": arc_challenge_norm - 0.02, "acc_norm,none": arc_challenge_norm}
    return r


PYTHIA = _make_results(mmlu_acc=0.40, hellaswag_acc=0.60, arc_easy=0.70, arc_challenge_norm=0.40)
OLMO   = _make_results(mmlu_acc=0.45, hellaswag_acc=0.62, arc_easy=0.72, arc_challenge_norm=0.44)


def test_compute_ratio_basic():
    ratio = compute_ratio(PYTHIA)
    assert abs(ratio - 0.40 / 0.60) < 1e-6


def test_compute_ratio_zero_hellaswag():
    bad = dict(PYTHIA)
    bad["hellaswag"] = {"acc,none": 0.0}
    with pytest.raises(ZeroDivisionError):
        compute_ratio(bad)


def test_compute_ratio_no_mmlu():
    bad = {k: v for k, v in PYTHIA.items() if not k.startswith("mmlu_")}
    with pytest.raises(ValueError):
        compute_ratio(bad)


def test_compute_arc_delta():
    delta = compute_arc_delta(PYTHIA)
    expected = 0.40 - 0.70
    assert abs(delta - expected) < 1e-6


def test_bootstrap_ratio_diff_shape():
    result = bootstrap_ratio_diff(PYTHIA, OLMO, n=100, seed=0)
    assert "mean_diff" in result
    assert "ci_95" in result
    assert len(result["ci_95"]) == 2
    assert len(result["bootstrap_diffs"]) == 100


def test_bootstrap_ratio_diff_direction():
    result = bootstrap_ratio_diff(PYTHIA, OLMO, n=200, seed=42)
    # OLMo has higher ratio; mean_diff should be positive
    assert result["mean_diff"] > 0


def test_cohens_d_identical():
    # All identical floats → std≈0 → very large or inf d
    diffs = [0.05] * 100
    d = cohens_d(diffs)
    assert d > 1e10 or d == float("inf")


def test_cohens_d_normal():
    rng = np.random.default_rng(0)
    diffs = list(rng.normal(0.05, 0.01, 1000))
    d = cohens_d(diffs)
    assert d > 0  # mean > 0, std > 0 → positive d


def test_evaluate_hypothesis_keys():
    metrics = evaluate_hypothesis(PYTHIA, OLMO)
    required = {"pythia_ratio", "olmo_ratio", "ratio_diff", "arc_delta_pythia",
                "arc_delta_olmo", "bootstrap", "cohens_d", "primary_pass",
                "secondary_pass", "verdict", "evidence"}
    assert required.issubset(set(metrics.keys()))


def test_evaluate_hypothesis_verdict_type():
    metrics = evaluate_hypothesis(PYTHIA, OLMO)
    assert metrics["verdict"] in ("CONFIRMED", "FAILED")


def test_evaluate_hypothesis_secondary_pass():
    metrics = evaluate_hypothesis(PYTHIA, OLMO)
    # OLMo arc_delta (0.44-0.72=-0.28) vs Pythia (0.40-0.70=-0.30) → OLMo higher → secondary PASS
    assert metrics["secondary_pass"] is True
