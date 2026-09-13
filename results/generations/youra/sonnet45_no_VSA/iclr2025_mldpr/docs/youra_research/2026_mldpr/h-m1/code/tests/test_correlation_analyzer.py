"""Tests for Correlation Analyzer."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from analysis.correlation_analyzer import CorrelationAnalyzer


def test_correlation_analyzer_init():
    """Test CorrelationAnalyzer initialization."""
    analyzer = CorrelationAnalyzer(random_seed=42)
    assert analyzer.random_seed == 42


def test_compute_spearman_positive_correlation():
    """Test Spearman correlation with positive correlation."""
    analyzer = CorrelationAnalyzer()

    # Perfect positive correlation
    x = pd.Series([1, 2, 3, 4, 5])
    y = pd.Series([2, 4, 6, 8, 10])

    result = analyzer.compute_spearman(x, y, one_tailed=True)

    assert result['rho'] == pytest.approx(1.0, abs=0.01)
    assert result['p_value'] < 0.05
    assert result['n'] == 5
    assert result['test_type'] == 'one_tailed'


def test_compute_spearman_no_correlation():
    """Test Spearman correlation with no correlation."""
    analyzer = CorrelationAnalyzer()

    np.random.seed(42)
    x = pd.Series(np.random.randn(100))
    y = pd.Series(np.random.randn(100))

    result = analyzer.compute_spearman(x, y, one_tailed=False)

    assert abs(result['rho']) < 0.3  # Weak or no correlation
    assert result['n'] == 100


def test_compute_partial_correlation():
    """Test partial correlation computation."""
    analyzer = CorrelationAnalyzer()

    # Create correlated data with confounding variable
    np.random.seed(42)
    n = 100
    z = np.random.randn(n)  # Confounding variable
    x = z + np.random.randn(n) * 0.5
    y = z + np.random.randn(n) * 0.5

    df = pd.DataFrame({
        'x': x,
        'y': y,
        'z': z
    })

    result = analyzer.compute_partial_correlation(df, 'x', 'y', 'z')

    assert 'rho' in result
    assert 'p_value' in result
    assert 'n' in result
    assert result['n'] == 100


def test_bootstrap_confidence_interval():
    """Test bootstrap CI computation."""
    analyzer = CorrelationAnalyzer(random_seed=42)

    x = pd.Series([1, 2, 3, 4, 5])
    y = pd.Series([2, 4, 6, 8, 10])

    ci_lower, ci_upper = analyzer.bootstrap_confidence_interval(
        x, y, n_iterations=1000, confidence_level=0.95
    )

    assert ci_lower < ci_upper
    assert ci_lower > 0.5  # Should be positive correlation
    assert ci_upper <= 1.0


def test_analyze_all_metrics():
    """Test analyze_all_metrics with synthetic data."""
    analyzer = CorrelationAnalyzer(random_seed=42)

    np.random.seed(42)
    n = 100
    df = pd.DataFrame({
        'dcs_3_score': np.random.uniform(0, 3, n),
        'commits_per_month': np.random.exponential(20, n),
        'unique_contributors': np.random.poisson(5, n),
        'median_issue_response': np.random.gamma(2, 3, n),
        'repo_age_days': np.random.randint(365, 1500, n)
    })

    results = analyzer.analyze_all_metrics(df)

    assert 'commits_per_month' in results
    assert 'unique_contributors' in results
    assert 'median_issue_response' in results

    # Check structure of results
    for metric, result in results.items():
        assert 'spearman' in result
        assert 'partial' in result
        assert 'bootstrap_ci' in result

        assert 'rho' in result['spearman']
        assert 'p_value' in result['spearman']
