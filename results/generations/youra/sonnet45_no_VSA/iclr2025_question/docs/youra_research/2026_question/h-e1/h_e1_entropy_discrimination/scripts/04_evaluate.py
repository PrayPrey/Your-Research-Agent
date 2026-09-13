"""Evaluation script for H-E1 experiment.

Computes AUROC, statistical tests, and generates visualizations.
"""

import sys
import argparse
from pathlib import Path
import json
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from evaluation import evaluate_full_pipeline, determine_gate_decision
from visualization import generate_all_visualizations


def main():
    """Execute evaluation pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--entropies',
        type=str,
        default='./outputs/entropies.npy',
        help='Path to entropies array'
    )
    parser.add_argument(
        '--labels',
        type=str,
        default='./outputs/labels.npy',
        help='Path to labels array'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='./outputs',
        help='Output directory for results and plots'
    )
    args = parser.parse_args()

    print("=" * 80)
    print("H-E1: Evaluation & Visualization")
    print("=" * 80)

    # Load entropy and label data
    print(f"Loading entropies from {args.entropies}")
    entropies = np.load(args.entropies)

    print(f"Loading labels from {args.labels}")
    labels = np.load(args.labels)

    print(f"Loaded {len(entropies)} tokens")
    print(f"Label distribution: {np.bincount(labels)}")

    # Run evaluation
    print("\n" + "=" * 80)
    print("Running evaluation pipeline...")
    print("=" * 80)
    results = evaluate_full_pipeline(entropies, labels)

    # Determine gate decision
    print("\n" + "=" * 80)
    print("Determining gate decision...")
    print("=" * 80)
    gate_decision = determine_gate_decision(results)

    # Combine results
    full_results = {
        'hypothesis_id': 'h-e1',
        **results,
        'gate_decision': gate_decision
    }

    # Save results
    results_file = Path(args.output_dir) / 'results.json'
    with open(results_file, 'w') as f:
        json.dump(full_results, f, indent=2)
    print(f"\nSaved results to {results_file}")

    # Generate visualizations
    print("\n" + "=" * 80)
    print("Generating visualizations...")
    print("=" * 80)
    generate_all_visualizations(entropies, labels, results, args.output_dir)

    # Print summary
    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    print(f"AUROC: {results['auroc']['auroc']:.4f} (95% CI: [{results['auroc']['ci_lower']:.4f}, {results['auroc']['ci_upper']:.4f}])")
    print(f"p-value: {results['statistical_tests']['t_test']['p_value']:.4e}")
    print(f"Cohen's d: {results['statistical_tests']['cohens_d']:.4f} ({results['statistical_tests']['effect_size_interpretation']})")
    print(f"Calibration (Spearman ρ): {results['calibration']['spearman_rho']:.4f}")
    print(f"\nGate Decision: {gate_decision['decision']}")
    print(f"Interpretation: {gate_decision['interpretation']}")

    print("\n" + "=" * 80)
    print("Evaluation complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
