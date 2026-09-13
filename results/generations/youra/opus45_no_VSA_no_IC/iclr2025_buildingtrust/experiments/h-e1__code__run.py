"""Orchestration + Reporting for H-E1: run full analysis pipeline."""

import json
import os
import sys
from datetime import datetime

from config import FIGURES_DIR, RESULTS_DIR
from data import load_benchmark_scores
from analyze import BenchmarkCorrelationAnalyzer
from visualize import (
    plot_correlation_heatmap,
    plot_pairwise_scatter,
    plot_gate_metrics,
    plot_model_diversity,
)


def main() -> None:
    """
    Run full pipeline:
    1. Load benchmark scores
    2. Analyze correlations
    3. Save results JSON
    4. Generate all figures
    5. Print gate result
    """
    print("=" * 60)
    print("H-E1: Benchmark Correlation Analysis")
    print("=" * 60)
    print(f"Started: {datetime.now().isoformat()}")
    print()

    # Ensure output directories exist
    os.makedirs(FIGURES_DIR, exist_ok=True)
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Step 1: Load data
    print("[1/4] Loading benchmark scores...")
    try:
        scores = load_benchmark_scores()
        print(f"  Loaded {len(scores)} models")
    except Exception as e:
        print(f"ERROR: Failed to load data: {e}")
        sys.exit(1)

    # Step 2: Analyze
    print("\n[2/4] Computing correlations...")
    analyzer = BenchmarkCorrelationAnalyzer(scores)
    result = analyzer.evaluate_hypothesis()
    corr_matrix = analyzer.compute_correlation_matrix()

    print(f"  Baseline r: {result['baseline_r']:.4f}")
    print(f"  Cross-benchmark correlations:")
    for pair, r in result["correlations"].items():
        status = "✓" if result["baseline_r"] < r < result["threshold_upper"] else "✗"
        print(f"    {pair}: {r:.4f} {status}")

    # Step 3: Save results
    print("\n[3/4] Saving results...")
    result_path = os.path.join(RESULTS_DIR, "gate_result.json")
    result["timestamp"] = datetime.now().isoformat()
    result["correlation_matrix"] = corr_matrix.to_dict()

    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Saved: {result_path}")

    # Step 4: Generate figures
    print("\n[4/4] Generating figures...")
    plot_correlation_heatmap(corr_matrix, os.path.join(FIGURES_DIR, "heatmap.png"))
    plot_pairwise_scatter(scores, analyzer.benchmarks, FIGURES_DIR)
    plot_gate_metrics(result, os.path.join(FIGURES_DIR, "gate_metrics.png"))
    plot_model_diversity(scores, os.path.join(FIGURES_DIR, "diversity.png"))

    # Final result
    print()
    print("=" * 60)
    gate_status = "PASS" if result["passed"] else "FAIL"
    print(f"GATE RESULT: {gate_status}")
    print("=" * 60)
    print(f"Completed: {datetime.now().isoformat()}")

    # Return exit code based on gate
    sys.exit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
