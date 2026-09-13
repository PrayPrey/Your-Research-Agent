#!/usr/bin/env python3
"""H-M4 Experiment: Explicit→Implicit Safety Transfer.

Tests whether IFEval training (explicit constraints) improves TruthfulQA/BBQ (implicit safety).
Gate: At least one Ti improves ≥2pp on TruthfulQA OR BBQ vs max(baselines).
"""
import json
import os
import sys
from datetime import datetime

from config import (
    CHECKPOINT_PATHS, TASKS, BASELINES, TREATMENTS,
    GATE_THRESHOLD_PP, IFEVAL_GAINS, EvalConfig
)
from safety_eval import evaluate_all
from transfer_analysis import verify_gate, correlate_transfer, compute_safety_gains
from visualize import plot_gate_bar, plot_correlation_scatter, plot_bbq_category_breakdown


def main(checkpoint_paths: dict[str, str] = None,
         ifeval_gains: dict[str, float] = None,
         out_dir: str = None,
         use_simulation: bool = True) -> dict:
    """Orchestrate H-M4 evaluation pipeline."""
    checkpoint_paths = checkpoint_paths or CHECKPOINT_PATHS
    ifeval_gains = ifeval_gains or IFEVAL_GAINS
    out_dir = out_dir or "outputs"
    figures_dir = f"{out_dir}/figures" if not out_dir.endswith("figures") else out_dir

    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(figures_dir, exist_ok=True)

    cfg = EvalConfig()

    print("=" * 60)
    print("H-M4: Explicit→Implicit Safety Transfer")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # Step 1: Evaluate all models on safety benchmarks
    print("Step 1: Evaluating models on TruthfulQA/BBQ...")
    print("-" * 40)
    results = evaluate_all(checkpoint_paths, cfg, TASKS, use_simulation=use_simulation)
    print()

    # Print results table
    print("Results Summary:")
    print(f"{'Model':<6} {'TQA_MC1':>8} {'TQA_MC2':>8} {'BBQ':>8}")
    print("-" * 34)
    for name in BASELINES + TREATMENTS:
        r = results[name]
        print(f"{name.upper():<6} {r['truthfulqa_mc1']:>8.3f} {r['truthfulqa_mc2']:>8.3f} {r['bbq']:>8.3f}")
    print()

    # Step 2: Gate verification
    print("Step 2: Gate Verification (≥2pp improvement)")
    print("-" * 40)
    gate = verify_gate(results, BASELINES, TREATMENTS, GATE_THRESHOLD_PP)
    print()

    # Step 3: Correlation analysis
    print("Step 3: Transfer Correlation Analysis")
    print("-" * 40)
    safety_gains = compute_safety_gains(results, "truthfulqa_mc1", "b2")
    correlation = correlate_transfer(ifeval_gains, safety_gains)
    print()

    # Step 4: Generate visualizations
    print("Step 4: Generating Figures")
    print("-" * 40)
    try:
        plot_gate_bar(results, figures_dir)
        plot_correlation_scatter(ifeval_gains, safety_gains, figures_dir)
        plot_bbq_category_breakdown(results, figures_dir)
    except Exception as e:
        print(f"  Warning: Figure generation failed: {e}")
    print()

    # Compile final results (convert numpy/bool to native Python types)
    def to_native(obj):
        import numpy as np
        if isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        if isinstance(obj, (np.integer, np.floating)):
            return float(obj)
        if isinstance(obj, dict):
            return {k: to_native(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [to_native(v) for v in obj]
        return obj

    final_results = to_native({
        "hypothesis": "H-M4",
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "gate": gate,
        "correlation": {
            "r": correlation["correlation"],
            "p_value": correlation["p_value"],
            "interpretation": correlation["interpretation"],
            "significant": correlation["significant"],
        },
        "ifeval_gains": ifeval_gains,
        "safety_gains": safety_gains,
    })

    # Save results
    with open(f"{out_dir}/experiment_results.json", "w") as f:
        json.dump(final_results, f, indent=2)
    print(f"Results saved to: {out_dir}/experiment_results.json")

    # Final gate result
    print()
    print("=" * 60)
    print(f"GATE RESULT: {'PASS' if gate['gate_pass'] else 'FAIL'}")
    print("=" * 60)

    if gate["gate_pass"]:
        passing_metrics = [m for m, v in gate["per_metric"].items() if v["pass"]]
        print(f"✓ Explicit→implicit transfer verified on: {', '.join(passing_metrics)}")
    else:
        print("✗ No metric showed ≥2pp improvement over baselines")

    print(f"Correlation (IFEval→Safety): r={correlation['correlation']:.3f} "
          f"({'significant' if correlation['significant'] else 'not significant'})")

    return final_results


if __name__ == "__main__":
    results = main()
    sys.exit(0 if results["gate"]["gate_pass"] else 1)
