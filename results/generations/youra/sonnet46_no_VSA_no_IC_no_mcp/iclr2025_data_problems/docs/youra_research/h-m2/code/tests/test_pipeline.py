"""Tests for pipeline gate evaluation and mechanism verification."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from statistical_tester import BenchmarkStat
from pipeline import evaluate_gate, verify_mechanism_activated


def make_stat(bench, size, pile_mean, dedup_mean, p_corrected):
    diff = pile_mean - dedup_mean
    sig = p_corrected < 0.0125
    return BenchmarkStat(
        benchmark=bench, model_size=size,
        mean_pile=pile_mean, mean_deduped=dedup_mean,
        differential=diff, t_statistic=2.0 if diff > 0 else -2.0,
        p_value=p_corrected / 4, p_corrected=p_corrected,
        wilcoxon_p=p_corrected, cohens_d=0.5 if diff > 0 else -0.5,
        significant=sig,
    )


def test_evaluate_gate_pass_2_significant():
    """≥2 significant → PASS with satisfied=True."""
    stats = [
        make_stat("mmlu", "1b", -2.0, -2.5, 0.005),
        make_stat("hellaswag", "1b", -2.0, -2.4, 0.008),
        make_stat("arc_challenge", "1b", -2.0, -2.1, 0.1),
        make_stat("winogrande", "1b", -2.0, -2.0, 0.5),
    ]
    gate = evaluate_gate(stats)
    assert gate["result"] == "PASS"
    assert gate["satisfied"]
    assert gate["n_significant"] == 2


def test_evaluate_gate_pass_1_significant():
    """SHOULD_WORK: ≥1 significant → PASS."""
    stats = [
        make_stat("mmlu", "1b", -2.0, -2.5, 0.005),
        make_stat("hellaswag", "1b", -2.0, -2.0, 0.5),
    ]
    gate = evaluate_gate(stats)
    assert gate["result"] == "PASS"
    assert gate["satisfied"]


def test_evaluate_gate_partial():
    """Direction right but not significant → PARTIAL."""
    stats = [
        make_stat("mmlu", "1b", -2.0, -2.1, 0.15),
        make_stat("hellaswag", "1b", -2.0, -2.1, 0.2),
        make_stat("arc_challenge", "1b", -2.0, -2.1, 0.18),
    ]
    gate = evaluate_gate(stats)
    assert gate["result"] == "PARTIAL"
    assert not gate["satisfied"]


def test_evaluate_gate_fail():
    """Dedup higher on all → FAIL."""
    stats = [
        make_stat("mmlu", "1b", -2.5, -2.0, 0.9),
        make_stat("hellaswag", "1b", -2.5, -2.0, 0.95),
    ]
    gate = evaluate_gate(stats)
    assert gate["result"] == "FAIL"
    assert not gate["satisfied"]


def test_verify_mechanism_all_good():
    """Mechanism activated when all conditions met."""
    from mink_scorer import MinKScore
    scores = {
        "pile_1b": {"mmlu": [-2.0] * 600, "hellaswag": [-2.1] * 600,
                    "arc_challenge": [-2.2] * 600, "winogrande": [-2.3] * 600},
        "deduped_1b": {"mmlu": [-2.5] * 600, "hellaswag": [-2.5] * 600,
                       "arc_challenge": [-2.5] * 600, "winogrande": [-2.5] * 600},
        "pile_6.9b": {}, "deduped_6.9b": {},
    }
    stats = [make_stat("mmlu", "1b", -2.0, -2.5, 0.001)]
    results = {"scores": scores, "stats": stats}
    activated, indicators = verify_mechanism_activated(results)
    assert indicators["checkpoints_loaded"]
    assert indicators["scores_computed"]
    assert indicators["pile_higher_on_any"]


def test_verify_mechanism_not_enough_scores():
    """< 500 items → scores_computed = False."""
    scores = {
        "pile_1b": {"mmlu": [-2.0] * 100},
        "deduped_1b": {"mmlu": [-2.5] * 100},
        "pile_6.9b": {}, "deduped_6.9b": {},
    }
    results = {"scores": scores, "stats": []}
    _, indicators = verify_mechanism_activated(results)
    assert not indicators["scores_computed"]
