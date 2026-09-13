"""Integration test for full pipeline."""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from run_experiment import run_experiment


def test_full_pipeline():
    """Test end-to-end pipeline."""
    output_dir = Path(__file__).parent.parent / 'test_outputs'
    output_dir.mkdir(exist_ok=True)

    results = run_experiment('imagenet', output_dir)

    assert 'detection_success' in results
    assert 'first_decay_date' in results
    assert 'stability_cv' in results
    assert 'significance_ratio' in results
    assert isinstance(results['detection_success'], bool)


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])
