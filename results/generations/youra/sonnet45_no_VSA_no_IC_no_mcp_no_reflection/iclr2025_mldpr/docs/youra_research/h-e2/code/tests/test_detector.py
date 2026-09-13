"""Tests for velocity decay detector."""

import sys
from pathlib import Path
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from detector import VelocityDecayDetector


def test_detector_basic():
    """Test basic detector functionality."""
    # Create test data with velocity decay
    dates = pd.date_range('2020-01-01', periods=200, freq='D')
    scores = [80 + 0.05 * i if i < 100 else 85 + 0.005 * (i - 100) for i in range(200)]

    df = pd.DataFrame({'date': dates, 'score': scores})

    detector = VelocityDecayDetector(window_days=180, threshold=0.1)
    first_decay, velocities = detector.detect(df)

    assert velocities is not None
    assert len(velocities) > 0
    # Decay should be detected eventually
    assert all(isinstance(v, tuple) and len(v) == 3 for v in velocities)


def test_compute_velocity():
    """Test velocity computation."""
    dates = pd.date_range('2020-01-01', periods=30, freq='D')
    scores = [80 + 0.1 * i for i in range(30)]  # Linear growth

    df = pd.DataFrame({'date': dates, 'score': scores})

    detector = VelocityDecayDetector()
    velocity, p_value = detector._compute_velocity(df)

    assert velocity > 0  # Positive growth
    assert 0 <= p_value <= 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
