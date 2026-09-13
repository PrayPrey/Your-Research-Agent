"""Entropy computation script for H-E1 experiment.

Computes Shannon entropy from generated outputs.
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from model_engine import load_generated_outputs
from entropy_module import process_generated_outputs, save_entropy_data, compute_entropy_statistics
import json


def main():
    """Execute entropy computation pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--generated-outputs',
        type=str,
        default='./data/halueval/generated_outputs.pkl',
        help='Path to generated outputs pickle file'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./outputs',
        help='Output directory for entropy data'
    )
    args = parser.parse_args()

    print("=" * 80)
    print("H-E1: Entropy Computation")
    print("=" * 80)

    # Load generated outputs
    generated_outputs = load_generated_outputs(args.generated_outputs)

    # Compute entropies
    print("\nComputing entropy for all tokens...")
    entropies, labels = process_generated_outputs(generated_outputs)

    # Compute statistics
    print("\nComputing entropy statistics...")
    stats = compute_entropy_statistics(entropies, labels)
    print(json.dumps(stats, indent=2))

    # Save entropy data
    save_entropy_data(entropies, labels, args.output_dir)

    # Save statistics
    stats_file = Path(args.output_dir) / 'entropy_stats.json'
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"Saved statistics to {stats_file}")

    print("\n" + "=" * 80)
    print("Entropy computation complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
