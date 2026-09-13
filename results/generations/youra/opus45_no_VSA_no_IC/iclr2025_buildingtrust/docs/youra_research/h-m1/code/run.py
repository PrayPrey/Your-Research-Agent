#!/usr/bin/env python3
"""H-M1 Experiment Runner - TruthfulQA vs MMLU distinctness analysis."""
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config
from data import load_full_population
from analyze import CorrelationAnalyzer
from visualize import plot_gate_comparison, plot_scatter_divergent, plot_correlation_heatmap

def main() -> dict:
    """Run H-M1 experiment: load -> analyze -> visualize -> write results."""
    print("=" * 60)
    print("H-M1: TruthfulQA vs MMLU Distinctness Analysis")
    print("=" * 60)

    print("\n[1/4] Loading model population...")
    population = load_full_population()

    print(f"\n[2/4] Running correlation analysis...")
    analyzer = CorrelationAnalyzer(population)
    results = analyzer.evaluate_hypothesis()

    print(f"\nResults:")
    print(f"  r(TruthfulQA, MMLU): {results['r_tqa_mmlu']:.4f}")
    print(f"  r(MMLU internal mean): {results['r_mmlu_internal_mean']:.4f}")
    print(f"  Condition 1 (r_tqa < r_internal): {results['condition_1_pass']}")
    print(f"  Divergent models: {results['divergent_count']}")
    print(f"  Condition 2 (divergent >= 1): {results['condition_2_pass']}")
    print(f"  GATE PASS: {results['gate_pass']}")

    print(f"\n[3/4] Generating visualizations...")
    gate_fig_path = os.path.join(config.FIGURES_DIR, "gate_comparison.png")
    plot_gate_comparison(
        results["r_tqa_mmlu"],
        results["r_mmlu_internal_mean"],
        gate_fig_path,
        results["gate_pass"]
    )

    divergent_df = analyzer.find_divergent_models()
    scatter_path = os.path.join(config.FIGURES_DIR, "scatter_divergent.png")
    plot_scatter_divergent(population, divergent_df, scatter_path)

    heatmap_path = os.path.join(config.FIGURES_DIR, "correlation_heatmap.png")
    plot_correlation_heatmap(population, heatmap_path)

    print(f"\n[4/4] Writing results...")
    results["timestamp"] = datetime.now().isoformat()
    results["figures"] = {
        "gate_comparison": gate_fig_path,
        "scatter_divergent": scatter_path,
        "correlation_heatmap": heatmap_path,
    }

    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    results_path = os.path.join(config.RESULTS_DIR, "h_m1_results.json")
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"Results saved: {results_path}")

    print("\n" + "=" * 60)
    status = "PASS" if results["gate_pass"] else "FAIL"
    print(f"H-M1 GATE: {status}")
    print("=" * 60)

    return results

if __name__ == "__main__":
    results = main()
    sys.exit(0 if results.get("gate_pass", False) else 1)
