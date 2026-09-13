#!/usr/bin/env python3
"""Run H-M1 reconstruction test PoC."""
import json
import os
import sys

from config import CONFIG
from build_pairs import load_or_build_error_pairs
from judge import JudgeLLM
from reconstruction import ReconstructionTest
from evaluate import compute_reconstruction_metrics, per_error_type_breakdown, gate_check
from visualize import plot_gate_comparison, plot_per_field_accuracy, plot_accuracy_by_error_type


def main():
    print("=" * 60)
    print("H-M1: Reconstruction Test - Information Preservation")
    print("=" * 60)

    # Setup paths relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    error_pairs_path = CONFIG["error_pairs_path"]
    results_path = CONFIG["results_path"]
    figures_dir = CONFIG["figures_dir"]

    # Create output directories
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    # Step 1: Load or build error pairs
    print(f"\n[1/5] Loading/building error pairs (target: {CONFIG['min_samples']} samples)...")
    pairs = load_or_build_error_pairs(error_pairs_path, CONFIG["min_samples"])
    print(f"  Loaded {len(pairs)} error pairs")

    # Step 2: Initialize judge LLM
    print(f"\n[2/5] Initializing JudgeLLM ({CONFIG['judge_provider']}/{CONFIG['judge_model']})...")
    judge = JudgeLLM(
        provider=CONFIG["judge_provider"],
        model=CONFIG["judge_model"],
        temperature=CONFIG["temperature"],
        max_tokens=CONFIG["max_tokens"],
    )

    # Step 3: Run reconstruction test
    print(f"\n[3/5] Running reconstruction test on {len(pairs)} samples...")
    test = ReconstructionTest(judge=judge, fields=CONFIG["fields"])
    results = test.run(pairs)

    # Step 4: Compute metrics and gate check
    print("\n[4/5] Computing metrics...")
    metrics = compute_reconstruction_metrics(results["per_sample"], CONFIG["fields"])
    breakdown = per_error_type_breakdown(pairs, results["per_sample"])

    acc_thresh = CONFIG["accuracy_threshold"]
    pass_thresh = CONFIG["pass_rate_threshold"]
    gate_pass = gate_check(metrics, acc_thresh, pass_thresh)

    print(f"\n  Results:")
    print(f"    Mean Accuracy: {metrics['mean_accuracy']:.4f} (threshold: {acc_thresh})")
    print(f"    Pass Rate:     {metrics['pass_rate']:.4f} (threshold: {pass_thresh})")
    print(f"    Std Accuracy:  {metrics['std_accuracy']:.4f}")
    print(f"    N Samples:     {metrics['n_samples']}")
    print(f"\n  Per-field accuracy:")
    for field, acc in metrics["per_field"].items():
        print(f"    {field}: {acc:.4f}")

    print(f"\n  Per error-type breakdown:")
    for et, data in breakdown.items():
        print(f"    {et}: mean={data['mean_accuracy']:.3f}, n={data['n_samples']}")

    # Step 5: Save results and generate figures
    print("\n[5/5] Saving results and generating figures...")

    full_results = {
        "metrics": metrics,
        "breakdown": breakdown,
        "gate": {
            "accuracy_threshold": acc_thresh,
            "pass_rate_threshold": pass_thresh,
            "passed": gate_pass,
        },
        "config": {k: v for k, v in CONFIG.items() if not k.endswith("_path") and not k.endswith("_dir")},
    }

    with open(results_path, "w") as f:
        json.dump(full_results, f, indent=2)
    print(f"  Saved results to {results_path}")

    plot_gate_comparison(metrics, acc_thresh, pass_thresh, os.path.join(figures_dir, "gate_comparison.png"))
    plot_per_field_accuracy(metrics, os.path.join(figures_dir, "per_field_accuracy.png"))
    plot_accuracy_by_error_type(breakdown, os.path.join(figures_dir, "accuracy_by_error_type.png"))
    print(f"  Saved figures to {figures_dir}")

    # Final verdict
    print("\n" + "=" * 60)
    if gate_pass:
        print("GATE RESULT: PASS")
        print("Information content is preserved across format transformations.")
        print(f"LLM extracted original error details with {metrics['mean_accuracy']:.1%} accuracy.")
    else:
        print("GATE RESULT: FAIL")
        print(f"Accuracy {metrics['mean_accuracy']:.3f} < {acc_thresh} or pass_rate {metrics['pass_rate']:.3f} < {pass_thresh}")
    print("=" * 60)

    sys.exit(0 if gate_pass else 1)


if __name__ == "__main__":
    main()
