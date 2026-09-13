"""PoC validation run - subset for Phase 4 mechanism verification."""
import json
import random
import os
import torch
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

from datetime import datetime
from config import CONFIG
from data import load_all_problems
from model import ExecutionFeedbackRefinement
from edit_metrics import aggregate_edit_metrics

POC_SAMPLES = 50  # Per dataset, statistically meaningful but tractable

def run_condition(problems: list[dict], refiner, feedback_type: str, dataset_name: str) -> list[dict]:
    results = []
    for idx, problem in enumerate(problems):
        print(f"  [{dataset_name}] {feedback_type} {idx+1}/{len(problems)}: {problem.get('task_id', idx)}")
        try:
            code, passed, iterations, edit_records = refiner.generate_with_refinement(problem, feedback_type)
            results.append({
                "task_id": problem.get("task_id", f"{dataset_name}_{idx}"),
                "dataset": dataset_name,
                "feedback_type": feedback_type,
                "passed": passed,
                "iterations": iterations,
                "edit_records": edit_records,
            })
        except Exception as e:
            print(f"    Error: {e}")
            results.append({
                "task_id": problem.get("task_id", f"{dataset_name}_{idx}"),
                "dataset": dataset_name,
                "feedback_type": feedback_type,
                "passed": False,
                "iterations": 0,
                "edit_records": [],
                "error": str(e)
            })
    return results

def main():
    random.seed(CONFIG.seed)
    torch.manual_seed(CONFIG.seed)

    print(f"H-M2 PoC Experiment (subset: {POC_SAMPLES} per dataset)")
    print(f"Feedback types: {CONFIG.feedback_types}")

    print("Loading model...")
    refiner = ExecutionFeedbackRefinement()
    print("Model loaded.\n")

    all_problems = load_all_problems()

    all_results = []
    all_edit_records = []

    for dataset_name in CONFIG.datasets:
        problems = all_problems.get(dataset_name, [])
        subset = random.sample(problems, min(POC_SAMPLES, len(problems)))
        print(f"Running {dataset_name} ({len(subset)} problems)...")

        for feedback_type in CONFIG.feedback_types:
            print(f"  Condition: {feedback_type}")
            results = run_condition(subset, refiner, feedback_type, dataset_name)
            all_results.extend(results)
            for r in results:
                all_edit_records.extend(r.get("edit_records", []))

    # Compute basic metrics
    detailed_pass = sum(1 for r in all_results if r["feedback_type"] == "detailed" and r["passed"])
    binary_pass = sum(1 for r in all_results if r["feedback_type"] == "binary" and r["passed"])
    detailed_total = sum(1 for r in all_results if r["feedback_type"] == "detailed")
    binary_total = sum(1 for r in all_results if r["feedback_type"] == "binary")

    print(f"\n=== RESULTS ===")
    print(f"Detailed: {detailed_pass}/{detailed_total} = {detailed_pass/max(detailed_total,1):.3f}")
    print(f"Binary: {binary_pass}/{binary_total} = {binary_pass/max(binary_total,1):.3f}")

    # Edit metrics
    metrics = aggregate_edit_metrics(all_edit_records)
    print(f"\nEdit Metrics:")
    print(f"  Detailed avg lines: {metrics['detailed_avg_lines_changed']:.2f}")
    print(f"  Binary avg lines: {metrics['binary_avg_lines_changed']:.2f}")
    print(f"  Edit scope ratio: {metrics['edit_scope_ratio']:.3f}")
    print(f"  p-value: {metrics['p_value']:.4f}")

    # Gate check
    gate_passed = metrics['edit_scope_ratio'] < 0.9
    mechanism_verified = gate_passed and metrics['detailed_global_rewrite_rate'] < metrics['binary_global_rewrite_rate']
    print(f"\nGate (edit_scope_ratio < 0.9): {'PASS' if gate_passed else 'FAIL'}")
    print(f"Mechanism verified: {'YES' if mechanism_verified else 'NO'}")

    # Save
    output = {
        "timestamp": datetime.now().isoformat(),
        "poc_samples": POC_SAMPLES,
        "results": all_results,
        "edit_records": all_edit_records,
        "metrics": {
            "detailed_pass_rate": detailed_pass/max(detailed_total,1),
            "binary_pass_rate": binary_pass/max(binary_total,1),
            **metrics
        },
        "gate_passed": gate_passed,
        "mechanism_verified": mechanism_verified
    }

    with open(CONFIG.results_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {CONFIG.results_path}")

if __name__ == "__main__":
    main()
