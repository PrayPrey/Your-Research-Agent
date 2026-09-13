"""
Tests for BenchmarkValidator module.
"""

import pytest
import pandas as pd
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from validation.validator import BenchmarkValidator


def test_validator_initialization():
    """Test validator initialization."""
    validator = BenchmarkValidator(min_count=100, min_results=5)
    assert validator.min_count == 100
    assert validator.min_results == 5


def test_filter_by_criteria():
    """Test filtering logic."""
    validator = BenchmarkValidator(min_count=100, min_results=5)

    # Create test data
    df = pd.DataFrame({
        'benchmark_id': ['b1', 'b2', 'b3', 'b4', 'b5'],
        'name': ['Benchmark 1', 'Benchmark 2', 'Benchmark 3', 'Benchmark 4', 'Benchmark 5'],
        'result_count': [10, 3, 7, 15, 4]
    })

    filtered = validator.filter_by_criteria(df)

    # Should keep only benchmarks with result_count >= 5
    assert len(filtered) == 3
    assert all(filtered['result_count'] >= 5)


def test_check_primary_gate():
    """Test gate checking."""
    validator = BenchmarkValidator(min_count=100, min_results=5)

    assert validator.check_primary_gate(150) == True
    assert validator.check_primary_gate(100) == True
    assert validator.check_primary_gate(99) == False


def test_validate_hypothesis():
    """Test hypothesis validation."""
    validator = BenchmarkValidator(min_count=100, min_results=5)

    # Create test data with 120 benchmarks
    df = pd.DataFrame({
        'benchmark_id': [f'b{i}' for i in range(120)],
        'result_count': [10] * 120
    })

    result = validator.validate_hypothesis(df)

    assert result['total_benchmarks'] == 120
    assert result['threshold'] == 100
    assert result['passes'] == True
    assert result['status'] == 'PASS'
