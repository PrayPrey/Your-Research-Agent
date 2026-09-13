"""Main orchestration pipeline for H-E1 experiment."""

import os
import json
import argparse
import pandas as pd
from datetime import datetime
from tqdm import tqdm

from config import MODELS, OUTPUT_DIR, SOLUTIONS_PER_PROBLEM
from data import load_problems, get_solutions
from execute import run_evalplus
from judge import LLMJudgeEvaluator
from analyze import build_contingency, chi_square_test, verify_mechanism_active, compute_error_rates
from evaluate import generate_all_figures, ensure_output_dir


def run_experiment(skip_execution: bool = False, skip_70b: bool = False) -> dict:
    """Run full experiment pipeline."""
    ensure_output_dir()
    print(f"[{datetime.now().isoformat()}] Starting H-E1 experiment")

    # Load problems
    print("Loading HumanEval+ problems...")
    problems = load_problems()
    print(f"Loaded {len(problems)} problems")

    # Generate solution variants
    print("Generating solution variants...")
    all_pairs = []
    for problem in tqdm(problems, desc="Generating solutions"):
        solutions = get_solutions(problem, SOLUTIONS_PER_PROBLEM)
        for sol in solutions:
            all_pairs.append({
                "task_id": problem["task_id"],
                "problem": problem,
                "solution_id": sol["solution_id"],
                "code": sol["code"],
                "variant": sol["variant"],
            })
    print(f"Generated {len(all_pairs)} (problem, solution) pairs")

    # Execute for ground truth
    if skip_execution:
        print("Skipping execution, assigning synthetic ground truth...")
        for pair in all_pairs:
            pair["ground_truth"] = pair["variant"] == "canonical"
    else:
        print("Executing solutions for ground truth...")
        for pair in tqdm(all_pairs, desc="Executing"):
            pair["ground_truth"] = run_evalplus(
                pair["task_id"],
                pair["problem"],
                pair["code"]
            )

    passing = sum(1 for p in all_pairs if p["ground_truth"])
    print(f"Ground truth: {passing}/{len(all_pairs)} passing")

    # Judge inference across scales
    print("Running judge inference...")
    evaluator = LLMJudgeEvaluator()
    results = []

    scales_to_run = [s for s in MODELS.keys() if not (skip_70b and s == "70B")]

    for scale in scales_to_run:
        print(f"  Judging with {scale} model...")
        for pair in tqdm(all_pairs, desc=f"Judge {scale}"):
            judgment = evaluator.judge_code(pair["problem"], pair["code"], scale)
            error_type = LLMJudgeEvaluator.classify_error(
                judgment["verdict"],
                pair["ground_truth"]
            )
            results.append({
                "task_id": pair["task_id"],
                "solution_id": pair["solution_id"],
                "variant": pair["variant"],
                "scale": scale,
                "verdict": judgment["verdict"],
                "ground_truth": pair["ground_truth"],
                "error_type": error_type,
            })

    results_df = pd.DataFrame(results)
    results_df.to_csv(f"{OUTPUT_DIR}/results.csv", index=False)
    print(f"Saved {len(results_df)} results")

    # Statistical analysis
    print("Running statistical analysis...")
    verification = verify_mechanism_active(results_df)
    contingency = verification["contingency"]
    contingency.to_csv(f"{OUTPUT_DIR}/contingency.csv")

    # Compute metrics
    metrics = compute_error_rates(results_df)
    metrics.to_csv(f"{OUTPUT_DIR}/metrics.csv", index=False)

    # Generate figures
    print("Generating figures...")
    figures = generate_all_figures(
        results_df,
        contingency,
        metrics,
        verification["p_value"]
    )

    # Summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "sample_size": int(verification["sample_size"]),
        "sample_size_ok": bool(verification["sample_size_ok"]),
        "chi2_statistic": float(verification["chi2_statistic"]),
        "p_value": float(verification["p_value"]),
        "p_value_ok": bool(verification["p_value_ok"]),
        "dof": int(verification["dof"]),
        "gate_passed": bool(verification["gate_passed"]),
        "scales_tested": scales_to_run,
        "figures": figures,
        "metrics": metrics.to_dict(orient='records'),
    }

    with open(f"{OUTPUT_DIR}/summary.json", 'w') as f:
        json.dump(summary, f, indent=2)

    print("\n" + "="*60)
    print("H-E1 EXPERIMENT RESULTS")
    print("="*60)
    print(f"Sample size: {verification['sample_size']} (required: 500)")
    print(f"Chi-square statistic: {verification['chi2_statistic']:.4f}")
    print(f"P-value: {verification['p_value']:.6f} (threshold: 0.05)")
    print(f"Degrees of freedom: {verification['dof']}")
    print(f"\nGATE: {'PASS' if verification['gate_passed'] else 'FAIL'}")
    print("="*60)

    return summary


def main():
    parser = argparse.ArgumentParser(description="H-E1 Experiment")
    parser.add_argument("--skip-execution", action="store_true", help="Use synthetic ground truth")
    parser.add_argument("--skip-70b", action="store_true", help="Skip 70B model (requires 4xA100)")
    args = parser.parse_args()

    summary = run_experiment(
        skip_execution=args.skip_execution,
        skip_70b=args.skip_70b,
    )

    print("\nEXPERIMENT COMPLETE")
    return 0 if summary["gate_passed"] else 1


if __name__ == "__main__":
    exit(main())
