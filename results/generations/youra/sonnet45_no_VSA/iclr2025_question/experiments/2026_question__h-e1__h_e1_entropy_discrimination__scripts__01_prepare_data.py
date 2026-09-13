"""Data preparation script for H-E1 experiment.

Downloads and preprocesses HaluEval QA dataset.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from data_loader import HaluEvalDataLoader


def main():
    """Execute data preparation pipeline."""
    print("=" * 80)
    print("H-E1: Data Preparation")
    print("=" * 80)

    # Initialize loader
    loader = HaluEvalDataLoader(
        cache_dir="./data/halueval",
        seed=42
    )

    # Run preparation pipeline
    summary = loader.prepare_dataset()

    print("\n" + "=" * 80)
    print("Data preparation complete!")
    print("=" * 80)
    print(f"Calibration file: {summary['calibration_file']}")
    print(f"Test file: {summary['test_file']}")
    print(f"Statistics file: {summary['stats_file']}")
    print("\nStatistics:")
    print(f"  Calibration: {summary['statistics']['calibration']['total_samples']} samples")
    print(f"  Test: {summary['statistics']['test']['total_samples']} samples")


if __name__ == "__main__":
    main()
