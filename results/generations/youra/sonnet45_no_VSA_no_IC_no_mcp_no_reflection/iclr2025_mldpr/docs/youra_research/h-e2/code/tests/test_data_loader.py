"""Tests for data loading module."""

import sys
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_loader import load_pwc_benchmark, preprocess_leaderboard


def test_load_pwc_benchmark():
    """Test loading benchmark data."""
    df = load_pwc_benchmark('imagenet')

    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert 'date' in df.columns
    assert 'score' in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df['date'])


def test_preprocess_leaderboard():
    """Test preprocessing."""
    # Create test data
    df = pd.DataFrame({
        'date': pd.to_datetime(['2020-01-01', '2020-01-01', '2020-01-02']),
        'score': [85.0, 86.0, 87.0],
        'model': ['A', 'B', 'C'],
        'paper': ['P1', 'P2', 'P3']
    })

    result = preprocess_leaderboard(df)

    assert len(result) == 2  # Deduplication should remove one entry
    assert list(result.columns) == ['date', 'score']
    assert result['score'].iloc[0] == 86.0  # Highest score for 2020-01-01


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
