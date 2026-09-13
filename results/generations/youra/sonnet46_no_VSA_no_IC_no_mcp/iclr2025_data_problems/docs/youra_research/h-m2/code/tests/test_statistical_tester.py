"""Tests for statistical tester — BenchmarkStat correctness."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pytest

from statistical_tester import run_benchmark_stat, BenchmarkStat, cohens_d


def test_cohens_d_significant():
    """Cohen's d is positive when a > b."""
    a = np.array([-2.0, -2.1, -1.9, -2.05, -1.95])
    b = np.array([-3.0, -3.1, -2.9, -3.05, -2.95])
    d = cohens_d(a, b)
    assert d > 0


def test_cohens_d_zero_std():
    """All-same arrays: d is nan (pooled_std = 0)."""
    a = np.array([1.0, 1.0, 1.0])
    b = np.array([2.0, 2.0, 2.0])
    d = cohens_d(a, b)
    assert np.isnan(d)


def test_benchmark_stat_pile_higher():
    """When Pile scores are higher, differential is positive."""
    pile = [-2.0 + np.random.normal(0, 0.1) for _ in range(100)]
    dedup = [-2.5 + np.random.normal(0, 0.1) for _ in range(100)]
    stat = run_benchmark_stat(pile, dedup, "mmlu", "1b")
    assert stat.differential > 0
    assert stat.mean_pile > stat.mean_deduped


def test_benchmark_stat_significant():
    """Large effect should be significant after Bonferroni."""
    np.random.seed(42)
    pile = list(np.random.normal(-2.0, 0.1, 1000))
    dedup = list(np.random.normal(-3.0, 0.1, 1000))
    stat = run_benchmark_stat(pile, dedup, "mmlu", "1b",
                               n_benchmarks=4, corrected_alpha=0.0125)
    assert stat.significant
    assert stat.p_corrected < 0.0125


def test_benchmark_stat_not_significant():
    """No effect → not significant."""
    np.random.seed(0)
    scores = list(np.random.normal(-3.0, 0.5, 100))
    stat = run_benchmark_stat(scores, scores, "winogrande", "6.9b")
    assert not stat.significant


def test_benchmark_stat_fields():
    """BenchmarkStat has all required fields."""
    pile = [-3.0] * 50
    dedup = [-3.1] * 50
    stat = run_benchmark_stat(pile, dedup, "hellaswag", "1b")
    assert isinstance(stat, BenchmarkStat)
    assert stat.benchmark == "hellaswag"
    assert stat.model_size == "1b"
    assert hasattr(stat, "p_corrected")
    assert hasattr(stat, "cohens_d")
    assert hasattr(stat, "wilcoxon_p")


def test_benchmark_stat_too_few_items():
    """Single item → graceful fallback, not significant."""
    stat = run_benchmark_stat([1.0], [2.0], "arc_challenge", "1b")
    assert not stat.significant
    assert stat.p_corrected == 1.0
