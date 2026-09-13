#!/usr/bin/env python3
"""Main entry point for H-M1 experiment: sweep + convergence analysis + figures."""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sweep import run_sweep
from analysis.convergence import analyze_convergence
from analysis.figures import generate_all_figures


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    results_dir = os.path.join(base_dir, "results")
    figures_dir = os.path.join(base_dir, "figures")

    print("=" * 60)
    print("H-M1: Noise-Dilution Mechanism Experiment")
    print("=" * 60)

    print("\n[Phase 1] Running sweep over 7 configurations...")
    all_results = run_sweep(base_dir=base_dir)

    print("\n[Phase 2] Computing convergence metrics...")
    convergence_metrics = analyze_convergence(all_results)
    convergence_path = os.path.join(results_dir, "convergence_metrics.json")
    with open(convergence_path, "w") as f:
        json.dump(convergence_metrics, f, indent=2)
    print(f"Saved convergence metrics to {convergence_path}")

    print("\n[Phase 3] Generating figures...")
    generate_all_figures(results_dir, figures_dir)

    print("\n[Phase 4] Summary")
    print("-" * 40)

    p50_vs_p0 = convergence_metrics.get("p50_vs_p0", {})
    print(f"p50 vs p0 comparison:")
    print(f"  Cohen's d: {p50_vs_p0.get('cohens_d', 'N/A')}")
    print(f"  p-value: {p50_vs_p0.get('p_value', 'N/A')}")
    print(f"  mean_diff: {p50_vs_p0.get('mean_diff', 'N/A')}")

    print("\nPer-config convergence metrics:")
    for cfg in sorted(k for k in convergence_metrics.keys() if k.startswith("M1-")):
        m = convergence_metrics[cfg]
        print(f"  {cfg}: steps_to_thresh={m['steps_to_threshold']}, "
              f"final_loss={m['final_loss']:.4f}, auc={m['convergence_auc']:.2e}")

    print("\n" + "=" * 60)
    print("H-M1 experiment complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
