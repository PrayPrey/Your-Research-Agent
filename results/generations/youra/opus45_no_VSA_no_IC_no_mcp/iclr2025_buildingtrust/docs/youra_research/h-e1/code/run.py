#!/usr/bin/env python
"""Main orchestration script for h-e1 experiment."""

import json
import os
import sys
from pathlib import Path

from config import MODELS, RESULTS_DIR, SCORES_CSV, FIGURES_DIR


def main():
    print("=" * 60)
    print("h-e1 EXISTENCE Hypothesis Experiment")
    print("=" * 60)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(FIGURES_DIR, exist_ok=True)

    print("\n[1/4] Evaluating models...")
    from evaluate import evaluate_all
    evaluate_all()

    print("\n[2/4] Aggregating scores...")
    from aggregate import collect_scores, save_scores
    df = collect_scores()
    save_scores(df, SCORES_CSV)
    print(f"Models with results: {len(df)}")

    if len(df) < 5:
        print(f"ERROR: Only {len(df)} models evaluated. Need at least 5.")
        sys.exit(1)

    print("\n[3/4] Running analysis...")
    from analysis import run_analysis
    result = run_analysis(df)

    print(f"\nResults:")
    print(f" r = {result['r']:.4f}")
    print(f" p = {result['p']:.6f}")
    print(f" 95% CI = [{result['ci_lower']:.4f}, {result['ci_upper']:.4f}]")
    print(f" N models = {result['n_models']}")

    print("\n[4/4] Generating figures...")
    from visualize import generate_all_figures
    generate_all_figures(df, result)

    print("\n" + "=" * 60)
    print("GATE CHECK")
    print("=" * 60)
    print(f" r > 0.3: {result['r']:.4f} > 0.3 = {result['r'] > 0.3}")
    print(f" p < 0.05: {result['p']:.6f} < 0.05 = {result['p'] < 0.05}")
    print(f" CI_lower > 0: {result['ci_lower']:.4f} > 0 = {result['ci_lower'] > 0}")
    print("-" * 60)

    if result["gate_passed"]:
        print("GATE: PASSED")
        exit_code = 0
    else:
        print("GATE: FAILED")
        exit_code = 1

    results_path = "experiment_results.json"
    with open(results_path, "w") as f:
        result_export = {k: v for k, v in result.items() if k != "bootstrap_rs"}
        result_export["bootstrap_rs_summary"] = {
            "mean": float(sum(result["bootstrap_rs"]) / len(result["bootstrap_rs"])),
            "std": float((sum((x - sum(result["bootstrap_rs"]) / len(result["bootstrap_rs"]))**2 for x in result["bootstrap_rs"]) / len(result["bootstrap_rs"]))**0.5),
        }
        json.dump(result_export, f, indent=2)
    print(f"\nResults saved to {results_path}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
