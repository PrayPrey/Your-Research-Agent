"""Minimal validation - 5 problems, verify mechanism works."""
import json
import random
import os
import sys
import torch
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

from datetime import datetime
from config import CONFIG
from data import load_all_problems
from model import ExecutionFeedbackRefinement
from edit_metrics import aggregate_edit_metrics

MINIMAL_SAMPLES = 5

def run_condition(problems, refiner, feedback_type, dataset_name):
    results = []
    for idx, problem in enumerate(problems):
        print(f"  [{dataset_name}] {feedback_type} {idx+1}/{len(problems)}: {problem.get('task_id', idx)}", flush=True)
        try:
            code, passed, iterations, edit_records = refiner.generate_with_refinement(problem, feedback_type)
            results.append({
                "task_id": problem.get("task_id"),
                "feedback_type": feedback_type,
                "passed": passed,
                "iterations": iterations,
                "edit_records": edit_records,
            })
        except Exception as e:
            print(f"    Error: {e}", flush=True)
            results.append({
                "task_id": problem.get("task_id"),
                "feedback_type": feedback_type,
                "passed": False,
                "edit_records": [],
                "error": str(e)
            })
    return results

def main():
    random.seed(CONFIG.seed)
    torch.manual_seed(CONFIG.seed)

    print(f"H-M2 Minimal Test ({MINIMAL_SAMPLES} problems)", flush=True)

    print("Loading model...", flush=True)
    refiner = ExecutionFeedbackRefinement()
    print("Model loaded.", flush=True)

    all_problems = load_all_problems()
    print(f"Loaded datasets.", flush=True)

    all_results = []
    all_edit_records = []

    # Only use humaneval for minimal test
    problems = all_problems.get("humaneval", [])[:MINIMAL_SAMPLES]
    print(f"Running {len(problems)} HumanEval problems...", flush=True)

    for feedback_type in CONFIG.feedback_types:
        print(f"Condition: {feedback_type}", flush=True)
        results = run_condition(problems, refiner, feedback_type, "humaneval")
        all_results.extend(results)
        for r in results:
            all_edit_records.extend(r.get("edit_records", []))

    # Compute metrics
    detailed_pass = sum(1 for r in all_results if r["feedback_type"] == "detailed" and r["passed"])
    binary_pass = sum(1 for r in all_results if r["feedback_type"] == "binary" and r["passed"])

    print(f"\n=== RESULTS ===", flush=True)
    print(f"Detailed: {detailed_pass}/{MINIMAL_SAMPLES}", flush=True)
    print(f"Binary: {binary_pass}/{MINIMAL_SAMPLES}", flush=True)

    if all_edit_records:
        metrics = aggregate_edit_metrics(all_edit_records)
        print(f"\nEdit Metrics:", flush=True)
        print(f"  Detailed avg lines: {metrics['detailed_avg_lines_changed']:.2f}", flush=True)
        print(f"  Binary avg lines: {metrics['binary_avg_lines_changed']:.2f}", flush=True)
        print(f"  Edit scope ratio: {metrics['edit_scope_ratio']:.3f}", flush=True)

        gate_passed = metrics['edit_scope_ratio'] < 0.9
        print(f"\nGate (ratio < 0.9): {'PASS' if gate_passed else 'FAIL'}", flush=True)
    else:
        print("No edit records (all passed first try or errors)", flush=True)
        metrics = {}
        gate_passed = None

    # Save
    output = {
        "timestamp": datetime.now().isoformat(),
        "samples": MINIMAL_SAMPLES,
        "results": all_results,
        "edit_records": all_edit_records,
        "metrics": metrics,
        "gate_passed": gate_passed
    }

    with open("minimal_results.json", "w") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"\nSaved to minimal_results.json", flush=True)

if __name__ == "__main__":
    main()
