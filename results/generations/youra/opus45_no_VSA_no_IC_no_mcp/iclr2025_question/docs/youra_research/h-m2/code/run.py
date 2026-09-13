"""Main pipeline for H-M2: N-sample consistency mechanism analysis."""

import json
import os
import sys

from config import CONFIG
from analysis import load_scores, partition_by_label, analyze_stability_link
from plots import plot_distribution_comparison, plot_histogram_overlay


def main() -> int:
    """
    Load h-e1/outputs/scores.csv -> partition by label ->
    analyze_stability_link -> save metrics.json ->
    plot_distribution_comparison + plot_histogram_overlay ->
    gate check (direction correct AND cohens_d > threshold)
    """
    os.makedirs(CONFIG["OUTPUT_DIR"], exist_ok=True)
    os.makedirs(CONFIG["FIGURES_DIR"], exist_ok=True)

    print("=" * 60)
    print("H-M2: N-Sample Consistency Mechanism Analysis")
    print("=" * 60)

    # Load h-e1 scores
    csv_path = CONFIG["H_E1_SCORES_CSV"]
    print(f"\nLoading scores from: {csv_path}")
    df = load_scores(csv_path)
    print(f"Loaded {len(df)} samples")

    # Partition by label
    correct, incorrect = partition_by_label(df)
    print(f"Correct: {len(correct)}, Incorrect: {len(incorrect)}")

    # Analyze stability link
    print("\nAnalyzing consistency-correctness relationship...")
    result = analyze_stability_link(df, alpha=CONFIG["ALPHA"])

    # Save metrics
    with open(CONFIG["METRICS_JSON"], "w") as f:
        json.dump(result, f, indent=2)
    print(f"Metrics saved to: {CONFIG['METRICS_JSON']}")

    # Generate plots
    print("\nGenerating plots...")
    plot_distribution_comparison(correct, incorrect, CONFIG["DIST_PLOT_PNG"])
    print(f"  Distribution plot: {CONFIG['DIST_PLOT_PNG']}")

    plot_histogram_overlay(correct, incorrect, CONFIG["HIST_PLOT_PNG"])
    print(f"  Histogram overlay: {CONFIG['HIST_PLOT_PNG']}")

    # Report results
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Mean consistency (correct):   {result['mean_correct']:.4f} ± {result['std_correct']:.4f}")
    print(f"Mean consistency (incorrect): {result['mean_incorrect']:.4f} ± {result['std_incorrect']:.4f}")
    print(f"Cohen's d:                    {result['cohens_d']:.4f} (95% CI: [{result['cohens_d_ci'][0]:.4f}, {result['cohens_d_ci'][1]:.4f}])")
    print(f"t-statistic:                  {result['t_stat']:.4f}")
    print(f"p-value:                      {result['p_value']:.6f}")
    print(f"Significant (α=0.05):         {result['significant']}")
    print(f"Direction correct:            {result['direction_correct']} (correct > incorrect)")

    # Gate check
    print("\n" + "=" * 60)
    print("GATE CHECK")
    print("=" * 60)
    threshold = CONFIG["COHENS_D_THRESHOLD"]
    gate_pass = result["direction_correct"] and result["cohens_d"] > threshold

    if gate_pass:
        print(f"✓ PASS: Cohen's d ({result['cohens_d']:.4f}) > threshold ({threshold})")
        print(f"✓ PASS: Direction correct (correct > incorrect)")
        print("\n>>> GATE VERDICT: PASS <<<")
        print("N-sample consistency captures generation stability:")
        print("Low consistency correlates with factual incorrectness.")
        return 0
    else:
        print(f"✗ Cohen's d: {result['cohens_d']:.4f} (threshold: {threshold})")
        print(f"✗ Direction: {'correct > incorrect' if result['direction_correct'] else 'REVERSED'}")
        print("\n>>> GATE VERDICT: PIVOT <<<")
        print("Hypothesis not supported - consider alternative mechanisms.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
