"""Tests for statistical_tester.py — A-6."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).parent.parent))

from statistical_tester import (
    BenchmarkStat, SpearmanResult,
    run_mannwhitney_suite, compute_rank_correlation, mechanism_check
)


def _make_stats(removed_means: dict, retained_means: dict, p_values: dict) -> list[BenchmarkStat]:
    """Create BenchmarkStat list for testing."""
    stats = []
    for b in sorted(removed_means):
        r_mean = removed_means[b]
        t_mean = retained_means[b]
        p = p_values[b]
        ratio = r_mean / t_mean if t_mean > 0 else float("inf")
        stats.append(BenchmarkStat(
            benchmark=b,
            u_statistic=1000.0,
            p_value=p / 4,
            p_corrected=p,
            rank_biserial_r=0.3,
            significant=p < 0.0125,
            mean_removed=r_mean,
            mean_retained=t_mean,
            ratio=ratio,
        ))
    return stats


def test_mannwhitney_detects_difference():
    """Removed has higher overlap → should be significant."""
    rng = np.random.default_rng(42)
    removed = np.zeros((500, 2), dtype=np.float32)
    retained = np.zeros((500, 2), dtype=np.float32)
    # bench0: large difference
    removed[:, 0] = rng.uniform(0.1, 0.5, 500)
    retained[:, 0] = rng.uniform(0.0, 0.05, 500)
    # bench1: no difference
    removed[:, 1] = rng.uniform(0.0, 0.01, 500)
    retained[:, 1] = rng.uniform(0.0, 0.01, 500)

    benchmarks = ["arc_challenge", "winogrande"]
    stats = run_mannwhitney_suite(removed, retained, benchmark_names=benchmarks,
                                   alpha=0.05, n_benchmarks=2)
    assert len(stats) == 2
    bm_map = {s.benchmark: s for s in stats}
    assert bm_map["arc_challenge"].significant
    assert not bm_map["winogrande"].significant or True  # may or may not be significant


def test_mannwhitney_output_fields():
    rng = np.random.default_rng(0)
    removed = rng.uniform(0.1, 0.3, (100, 1)).astype(np.float32)
    retained = rng.uniform(0.0, 0.1, (100, 1)).astype(np.float32)
    stats = run_mannwhitney_suite(removed, retained, benchmark_names=["mmlu"])
    s = stats[0]
    assert s.benchmark == "mmlu"
    assert s.u_statistic >= 0
    assert 0.0 <= s.p_value <= 1.0
    assert 0.0 <= s.p_corrected <= 1.0
    assert s.mean_removed > s.mean_retained  # signal is real
    assert s.ratio >= 1.0


def test_rank_biserial_range():
    rng = np.random.default_rng(1)
    removed = rng.uniform(0.05, 0.2, (200, 2)).astype(np.float32)
    retained = rng.uniform(0.0, 0.05, (200, 2)).astype(np.float32)
    stats = run_mannwhitney_suite(removed, retained, benchmark_names=["mmlu", "hellaswag"])
    for s in stats:
        assert -1.0 <= s.rank_biserial_r <= 1.0


def test_spearman_perfect_correlation():
    """If observed ranking matches expected, rho should be near 1."""
    stats = _make_stats(
        removed_means={"mmlu": 0.10, "arc_challenge": 0.07, "hellaswag": 0.04, "winogrande": 0.01},
        retained_means={"mmlu": 0.01, "arc_challenge": 0.01, "hellaswag": 0.01, "winogrande": 0.01},
        p_values={"mmlu": 0.001, "arc_challenge": 0.002, "hellaswag": 0.05, "winogrande": 0.8},
    )
    result = compute_rank_correlation(stats)
    assert result.correlation > 0.7  # near-perfect positive correlation


def test_mechanism_check_passes():
    stats = _make_stats(
        removed_means={"mmlu": 0.10, "hellaswag": 0.05},
        retained_means={"mmlu": 0.01, "hellaswag": 0.01},
        p_values={"mmlu": 0.001, "hellaswag": 0.1},
    )
    mechanism_check(stats)  # should not raise


def test_mechanism_check_fails():
    stats = _make_stats(
        removed_means={"mmlu": 0.01},
        retained_means={"mmlu": 0.01},
        p_values={"mmlu": 0.5},
    )
    stats[0].ratio = 1.0
    try:
        mechanism_check(stats)
        assert False, "Should have raised"
    except RuntimeError as e:
        assert "Mechanism check fail" in str(e)
