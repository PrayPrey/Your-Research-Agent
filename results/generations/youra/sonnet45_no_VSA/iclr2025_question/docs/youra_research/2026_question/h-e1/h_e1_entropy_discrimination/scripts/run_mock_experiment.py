"""Mock experiment for H-E1 validation.

Generates synthetic data to test the full pipeline without requiring actual model inference.
This allows for rapid validation of the evaluation logic and gate decision system.
"""

import sys
import os
from pathlib import Path
import numpy as np
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from evaluation import evaluate_full_pipeline, determine_gate_decision
from visualization import generate_all_visualizations


def generate_mock_data(
    n_samples: int = 5000,
    auroc_target: float = 0.85,
    seed: int = 42
) -> tuple:
    """Generate synthetic entropy and label data with controlled AUROC.

    Parameters
    ----------
    n_samples : int
        Number of tokens to generate
    auroc_target : float
        Target AUROC value (controls separation between distributions)
    seed : int
        Random seed

    Returns
    -------
    tuple
        (entropies, labels) arrays
    """
    rng = np.random.RandomState(seed)

    # Generate labels (20% hallucinated)
    labels = rng.binomial(1, 0.2, n_samples).astype(np.int8)

    # Generate entropies with controlled separation
    # Higher target AUROC -> larger mean difference
    mean_correct = 2.0
    mean_hallucinated = 2.0 + (auroc_target - 0.5) * 3.0  # Scale by deviation from random

    entropies = np.zeros(n_samples, dtype=np.float32)

    # Correct tokens: lower entropy
    correct_mask = labels == 0
    entropies[correct_mask] = rng.normal(
        mean_correct,
        0.5,
        np.sum(correct_mask)
    )

    # Hallucinated tokens: higher entropy
    hallucinated_mask = labels == 1
    entropies[hallucinated_mask] = rng.normal(
        mean_hallucinated,
        0.6,
        np.sum(hallucinated_mask)
    )

    # Clip to valid range [0, log(32000)]
    max_entropy = np.log(32000)
    entropies = np.clip(entropies, 0, max_entropy)

    return entropies, labels


def run_mock_experiment(auroc_target: float = 0.85):
    """Run mock experiment with synthetic data.

    Parameters
    ----------
    auroc_target : float
        Target AUROC value for synthetic data
    """
    print("=" * 80)
    print(f"H-E1: Mock Experiment (Target AUROC={auroc_target:.2f})")
    print("=" * 80)

    # Create output directory
    output_dir = Path("./outputs")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate synthetic data
    print("\nGenerating synthetic data...")
    entropies, labels = generate_mock_data(n_samples=5000, auroc_target=auroc_target)

    print(f"Generated {len(entropies)} tokens")
    print(f"Label distribution: {np.bincount(labels)}")
    print(f"Entropy range: [{entropies.min():.4f}, {entropies.max():.4f}]")

    # Save data
    np.save(output_dir / 'entropies.npy', entropies)
    np.save(output_dir / 'labels.npy', labels)
    print(f"Saved data to {output_dir}")

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
        'experiment_type': 'mock',
        'target_auroc': auroc_target,
        **results,
        'gate_decision': gate_decision
    }

    # Save results
    results_file = output_dir / 'results.json'
    with open(results_file, 'w') as f:
        json.dump(full_results, f, indent=2)
    print(f"\nSaved results to {results_file}")

    # Generate visualizations
    print("\n" + "=" * 80)
    print("Generating visualizations...")
    print("=" * 80)
    generate_all_visualizations(entropies, labels, results, str(output_dir))

    # Print summary
    print("\n" + "=" * 80)
    print("EXPERIMENT SUMMARY")
    print("=" * 80)
    print(f"Target AUROC: {auroc_target:.4f}")
    print(f"Actual AUROC: {results['auroc']['auroc']:.4f} (95% CI: [{results['auroc']['ci_lower']:.4f}, {results['auroc']['ci_upper']:.4f}])")
    print(f"p-value: {results['statistical_tests']['t_test']['p_value']:.4e}")
    print(f"Cohen's d: {results['statistical_tests']['cohens_d']:.4f} ({results['statistical_tests']['effect_size_interpretation']})")
    print(f"Calibration (Spearman ρ): {results['calibration']['spearman_rho']:.4f}")
    print(f"\nGate Decision: {gate_decision['decision']}")
    print(f"Interpretation: {gate_decision['interpretation']}")

    print("\nSuccess Criteria:")
    for criterion, check in gate_decision['success_criteria'].items():
        status = "✓" if check['met'] else "✗"
        print(f"  {status} {criterion}: {check['actual']:.4f} (threshold: {check['threshold']:.4f})")

    print("\n" + "=" * 80)
    print("Mock experiment complete!")
    print("=" * 80)

    return full_results


def main():
    """Run mock experiments with different AUROC targets."""
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--target-auroc',
        type=float,
        default=0.85,
        help='Target AUROC for synthetic data (0.0-1.0)'
    )
    args = parser.parse_args()

    # Change to experiment directory
    exp_dir = Path(__file__).parent.parent
    os.chdir(exp_dir)

    # Run mock experiment
    results = run_mock_experiment(auroc_target=args.target_auroc)

    # Return exit code based on gate decision
    if results['gate_decision']['decision'] == 'PASS':
        return 0
    elif results['gate_decision']['decision'] == 'PARTIAL':
        return 1
    else:
        return 2


if __name__ == "__main__":
    sys.exit(main())
