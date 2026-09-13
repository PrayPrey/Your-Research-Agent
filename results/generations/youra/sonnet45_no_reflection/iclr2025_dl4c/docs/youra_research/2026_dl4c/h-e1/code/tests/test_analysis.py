"""Tests for spectral analysis core."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
import pytest
from analysis import (
    ConfoundRegressor,
    SpectralAnalyzer,
    PermutationTest,
    DirectionalStability,
    StatisticalValidator
)

def test_confound_regressor():
    """Test confound removal."""
    Y = np.random.randn(100, 4)
    X = np.random.randn(100, 3)

    regressor = ConfoundRegressor()
    Y_residual = regressor.fit(Y, X)

    assert Y_residual.shape == Y.shape
    assert np.abs(np.mean(Y_residual)) < 0.5  # Close to zero mean

def test_spectral_analyzer():
    """Test eigendecomposition."""
    # Create known covariance matrix
    Sigma = np.array([
        [4.0, 0.5, 0.3, 0.2],
        [0.5, 3.0, 0.4, 0.1],
        [0.3, 0.4, 2.5, 0.3],
        [0.2, 0.1, 0.3, 1.5]
    ])

    analyzer = SpectralAnalyzer()
    eigenvalues, eigenvectors = analyzer.eigendecomposition(Sigma)

    assert eigenvalues.shape == (4,)
    assert eigenvectors.shape == (4, 4)
    assert eigenvalues[0] >= eigenvalues[-1]  # Sorted descending

def test_spectral_gap():
    """Test spectral gap computation."""
    eigenvalues = np.array([5.0, 3.0, 2.0, 0.5])

    analyzer = SpectralAnalyzer()
    gap = analyzer.spectral_gap(eigenvalues)

    assert gap > 0
    assert isinstance(gap, float)

def test_permutation_test():
    """Test permutation test."""
    Y_residual = np.random.randn(200, 4)
    aspect_labels = np.repeat(['a', 'b', 'c', 'd'], 50)

    perm_test = PermutationTest()
    results = perm_test.run(Y_residual, aspect_labels, observed_gap=0.5, n_permutations=100)

    assert 'p_value' in results
    assert 0 <= results['p_value'] <= 1
    assert 'null_gaps' in results
    assert len(results['null_gaps']) == 100

def test_statistical_validator():
    """Test integrated validation."""
    Y_residual = np.random.randn(500, 4)
    aspect_labels = np.repeat(['a', 'b', 'c', 'd'], 125)
    repo_ids = np.random.randint(0, 10, 500)

    validator = StatisticalValidator()
    results = validator.run_full_validation(Y_residual, aspect_labels, repo_ids)

    assert 'spectral_analysis' in results
    assert 'permutation_test' in results
    assert 'gate_evaluation' in results
    assert 'overall_pass' in results['gate_evaluation']
