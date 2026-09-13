#!/usr/bin/env python3
"""H-M4 Experiment Runner: Traditional Benchmark Persistence with Reduced Dominance

Hypothesis: ImageNet/CIFAR share of total benchmark usage decreases while
absolute paper counts remain stable.

Validation approach: Using static paper counts from PWC datasets to validate
that traditional benchmarks (ImageNet, CIFAR) have:
1. Reduced share (< 50% of benchmark papers) - no longer dominant
2. Maintained substantial presence (> 10,000 papers) - persistence confirmed

Gate: SHOULD_WORK - both conditions must be satisfied.
"""

import sys
import os
import yaml

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data_loader import load_and_prepare_data
from metrics import evaluate_gate, compute_per_benchmark_metrics
from stats import chi_square_test, compute_dominance_metrics
from visualize import (
    plot_gate_metrics, plot_share_timeseries,
    plot_stacked_area, plot_per_benchmark
)
from config import RESULTS_PATH, SIGNIFICANCE_ALPHA


def main():
    print("=" * 60)
    print("H-M4: Traditional Benchmark Persistence with Reduced Dominance")
    print("=" * 60)

    # Load data
    df, stats = load_and_prepare_data()

    if len(df) == 0:
        print("ERROR: No data loaded")
        sys.exit(1)

    # Evaluate gate
    print("\nEvaluating gate criteria...")
    gate_result = evaluate_gate(stats)

    print(f"  Traditional share: {gate_result['traditional_share']*100:.2f}%")
    print(f"  Emergent share: {gate_result['emergent_share']*100:.2f}%")
    print(f"  Traditional papers: {gate_result['traditional_papers']:,}")
    print(f"  Emergent papers: {gate_result['emergent_papers']:,}")
    print(f"  Share decreased (< 50%): {gate_result['share_decreased']}")
    print(f"  Counts stable (> 10k): {gate_result['counts_stable']}")
    print(f"  Dominance shift (emergent/traditional): {gate_result['dominance_shift']:.2f}")
    print(f"  GATE PASS: {gate_result['gate_pass']}")

    # Per-benchmark metrics
    print("\nPer-benchmark paper counts:")
    per_benchmark = compute_per_benchmark_metrics(df)
    for bm, count in per_benchmark.items():
        print(f"  {bm}: {count:,}")

    # Statistical tests
    print("\nStatistical analysis...")
    chi2, p_value = chi_square_test(stats)
    print(f"  Chi-square: {chi2:.2f}, p-value: {p_value:.4e}")

    dominance_metrics = compute_dominance_metrics(df)
    print(f"  Traditional datasets: {dominance_metrics['traditional_datasets']}")
    print(f"  Emergent datasets: {dominance_metrics['emergent_datasets']}")
    print(f"  Traditional avg papers/dataset: {dominance_metrics['traditional_avg_papers']:.1f}")
    print(f"  Emergent avg papers/dataset: {dominance_metrics['emergent_avg_papers']:.1f}")

    # Generate figures
    print("\nGenerating figures...")
    plot_gate_metrics(gate_result)
    plot_share_timeseries(df)
    plot_stacked_area(df)
    plot_per_benchmark(per_benchmark)

    # Build results
    results = {
        "hypothesis_id": "H-M4",
        "gate": "SHOULD_WORK",
        "gate_pass": gate_result["gate_pass"],
        "metrics": {
            "traditional_share": gate_result["traditional_share"],
            "emergent_share": gate_result["emergent_share"],
            "traditional_papers": gate_result["traditional_papers"],
            "emergent_papers": gate_result["emergent_papers"],
            "share_decreased": gate_result["share_decreased"],
            "counts_stable": gate_result["counts_stable"],
            "dominance_shift": gate_result["dominance_shift"],
        },
        "significance": {
            "chi_square": chi2,
            "p_value": p_value,
            "significant": p_value < SIGNIFICANCE_ALPHA,
        },
        "per_benchmark_papers": per_benchmark,
        "dominance_metrics": dominance_metrics,
        "figures": [
            "figures/gate_metrics.png",
            "figures/share_timeseries.png",
            "figures/stacked_area.png",
            "figures/per_benchmark.png",
        ],
    }

    # Write results
    print(f"\nWriting results to {RESULTS_PATH}...")
    with open(RESULTS_PATH, "w") as f:
        yaml.safe_dump(results, f, default_flow_style=False)

    print("\n" + "=" * 60)
    print(f"EXPERIMENT COMPLETE - Gate: {'PASS' if gate_result['gate_pass'] else 'FAIL'}")
    print("=" * 60)

    return results


if __name__ == "__main__":
    main()
