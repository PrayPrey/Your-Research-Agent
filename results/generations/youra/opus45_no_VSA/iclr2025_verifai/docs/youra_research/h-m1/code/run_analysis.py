#!/usr/bin/env python3
import json
import os
import sys

from config import AnalysisConfig
from data_loader import load_logs, validate_logs
from trajectory import compare_conditions, compute_cumulative_trajectory
from stats import mcnemar_test
from visualize import plot_delta_comparison, plot_iteration_trajectory

def main():
    cfg = AnalysisConfig()
    os.makedirs(cfg.results_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)

    print(f"Loading logs from {cfg.logs_path}")
    try:
        logs = load_logs(cfg.logs_path)
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {cfg.logs_path}")
        sys.exit(1)

    print(f"Loaded {len(logs)} records")

    try:
        validate_logs(logs, cfg)
    except AssertionError as e:
        print(f"VALIDATION ERROR: {e}")
        sys.exit(1)

    print("Computing trajectory comparison...")
    comparison = compare_conditions(logs, cfg)

    static_newly = comparison["static_first"]["newly_solved_iter_2"]
    exec_newly = comparison["exec_first"]["newly_solved_iter_2"]
    all_problems = {log["problem_id"] for log in logs}

    print("Running McNemar's test...")
    mcnemar = mcnemar_test(static_newly, exec_newly, all_problems)

    results = {
        "hypothesis": "h-m1",
        "static_first": {
            "delta_pass_12": float(comparison["static_first"]["delta_pass_12"]),
            "pass_at_iter_1": float(comparison["static_first"]["pass_at_iter_1"]),
            "pass_at_iter_2": float(comparison["static_first"]["pass_at_iter_2"]),
            "n_problems": int(comparison["static_first"]["n_problems"]),
            "newly_solved_count": len(static_newly)
        },
        "exec_first": {
            "delta_pass_12": float(comparison["exec_first"]["delta_pass_12"]),
            "pass_at_iter_1": float(comparison["exec_first"]["pass_at_iter_1"]),
            "pass_at_iter_2": float(comparison["exec_first"]["pass_at_iter_2"]),
            "n_problems": int(comparison["exec_first"]["n_problems"]),
            "newly_solved_count": len(exec_newly)
        },
        "delta_diff": float(comparison["delta_diff"]),
        "hypothesis_supported": bool(comparison["hypothesis_supported"]),
        "mcnemar": {k: float(v) if isinstance(v, (int, float)) else v for k, v in mcnemar.items()},
        "success_criteria": {
            "delta_positive": bool(comparison["delta_diff"] > 0),
            "p_significant": bool(mcnemar["p_value"] < cfg.alpha)
        }
    }

    out_path = os.path.join(cfg.results_dir, "h-m1_analysis.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results written to {out_path}")

    print("Generating figures...")
    plot_delta_comparison(comparison, os.path.join(cfg.figures_dir, "delta_pass_12_comparison.png"))

    traj_static = compute_cumulative_trajectory(logs, cfg.conditions[0])
    traj_exec = compute_cumulative_trajectory(logs, cfg.conditions[1])
    plot_iteration_trajectory(traj_static, traj_exec, os.path.join(cfg.figures_dir, "iteration_trajectory.png"))

    print("\n" + "="*60)
    print("SUCCESS CRITERIA EVALUATION")
    print("="*60)
    print(f"ΔPass₁₂(static-first): {comparison['static_first']['delta_pass_12']:.4f}")
    print(f"ΔPass₁₂(exec-first):   {comparison['exec_first']['delta_pass_12']:.4f}")
    print(f"Difference (A - B):    {comparison['delta_diff']:.4f}")
    print(f"McNemar p-value:       {mcnemar['p_value']:.6f} ({mcnemar['method']})")
    print()

    gate_pass = results["success_criteria"]["delta_positive"] and results["success_criteria"]["p_significant"]

    if gate_pass:
        print("✓ HYPOTHESIS SUPPORTED: Static-first has larger early gains (p<0.05)")
    else:
        reasons = []
        if not results["success_criteria"]["delta_positive"]:
            reasons.append("delta ≤ 0")
        if not results["success_criteria"]["p_significant"]:
            reasons.append(f"p={mcnemar['p_value']:.4f} ≥ 0.05")
        print(f"✗ HYPOTHESIS NOT SUPPORTED: {', '.join(reasons)}")

    print("EXPERIMENT COMPLETE")
    return results

if __name__ == "__main__":
    main()
