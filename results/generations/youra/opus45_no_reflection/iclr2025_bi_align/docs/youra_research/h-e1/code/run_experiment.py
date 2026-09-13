"""H-E1 experiment runner: Collaboration score orthogonality test."""
import json
import os
import sys

import config
from data import load_hh_rlhf_sample
from analysis import compute_correlation
from visualize import plot_gate_bar_chart, plot_score_histogram, plot_scatter_regression, plot_boxplot

def main():
    print("=" * 60)
    print("H-E1: Collaboration Score Orthogonality Test")
    print("=" * 60)

    # Load data
    print(f"\nLoading HH-RLHF dataset (n={config.SAMPLE_SIZE}, seed={config.SEED})...")
    dataset = load_hh_rlhf_sample()
    print(f"Loaded {len(dataset)} samples")

    # Compute correlation
    print("\nComputing collaboration scores and correlation...")
    result = compute_correlation(dataset)

    # Print results
    print("\n" + "=" * 40)
    print("RESULTS")
    print("=" * 40)
    print(f"Pearson Correlation: {result['correlation']:.4f}")
    print(f"P-value: {result['p_value']:.2e}")
    print(f"Chosen Mean (std): {result['chosen_mean']:.4f} ({result['chosen_std']:.4f})")
    print(f"Rejected Mean (std): {result['rejected_mean']:.4f} ({result['rejected_std']:.4f})")
    print(f"\nGate Threshold: |r| < {config.CORRELATION_THRESHOLD}")
    print(f"Gate Passed: {result['gate_passed']}")

    # Generate figures
    print("\nGenerating figures...")
    os.makedirs(config.FIGURES_DIR, exist_ok=True)

    plot_gate_bar_chart(result['correlation'], config.CORRELATION_THRESHOLD,
                        f"{config.FIGURES_DIR}/gate_bar.png")
    print(f" - {config.FIGURES_DIR}/gate_bar.png")

    plot_score_histogram(result['chosen_scores'], result['rejected_scores'],
                         f"{config.FIGURES_DIR}/histogram.png")
    print(f" - {config.FIGURES_DIR}/histogram.png")

    all_scores = result['chosen_scores'] + result['rejected_scores']
    all_labels = [1] * len(result['chosen_scores']) + [0] * len(result['rejected_scores'])
    plot_scatter_regression(all_scores, all_labels, f"{config.FIGURES_DIR}/scatter.png")
    print(f" - {config.FIGURES_DIR}/scatter.png")

    plot_boxplot(result['chosen_scores'], result['rejected_scores'],
                 f"{config.FIGURES_DIR}/boxplot.png")
    print(f" - {config.FIGURES_DIR}/boxplot.png")

    # Save results JSON (without raw scores to keep it small)
    output = {k: v for k, v in result.items() if k not in ['chosen_scores', 'rejected_scores']}
    output['gate_passed'] = bool(output['gate_passed'])  # numpy.bool_ -> Python bool
    output['threshold'] = config.CORRELATION_THRESHOLD
    output['seed'] = config.SEED

    os.makedirs(os.path.dirname(config.RESULTS_PATH), exist_ok=True)
    with open(config.RESULTS_PATH, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {config.RESULTS_PATH}")

    print("\n" + "=" * 60)
    if result['gate_passed']:
        print("GATE: PASSED - Collaboration score is orthogonal to preference labels")
    else:
        print("GATE: FAILED - Collaboration score is NOT orthogonal (r >= 0.7)")
    print("=" * 60)

    return 0 if result['gate_passed'] else 1

if __name__ == "__main__":
    sys.exit(main())
