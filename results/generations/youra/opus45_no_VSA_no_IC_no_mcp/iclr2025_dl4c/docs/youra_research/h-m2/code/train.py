import json
import random
import torch
from datetime import datetime
from config import CONFIG
from data import load_all_problems
from model import ExecutionFeedbackRefinement

def run_condition(problems: list[dict], refiner, feedback_type: str, dataset_name: str) -> list[dict]:
    """Run all problems with a given feedback type, collect results and edit records."""
    results = []
    for idx, problem in enumerate(problems):
        print(f"  [{dataset_name}] {feedback_type} problem {idx+1}/{len(problems)}: {problem.get('task_id', idx)}")
        try:
            code, passed, iterations, edit_records = refiner.generate_with_refinement(problem, feedback_type)
            results.append({
                "task_id": problem.get("task_id", f"{dataset_name}_{idx}"),
                "dataset": dataset_name,
                "feedback_type": feedback_type,
                "passed": passed,
                "iterations": iterations,
                "edit_records": edit_records,
                "final_code": code
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

    print(f"H-M2 Experiment: Feedback Granularity Ablation")
    print(f"Datasets: {CONFIG.datasets}")
    print(f"Feedback types: {CONFIG.feedback_types}")
    print(f"Max iterations: {CONFIG.max_iterations}")
    print()

    # Load model once
    print("Loading model...")
    refiner = ExecutionFeedbackRefinement()
    print("Model loaded.\n")

    # Load datasets
    all_problems = load_all_problems()
    print(f"Loaded {sum(len(p) for p in all_problems.values())} problems total.\n")

    all_results = []
    all_edit_records = []

    for dataset_name in CONFIG.datasets:
        problems = all_problems.get(dataset_name, [])
        print(f"Running {dataset_name} ({len(problems)} problems)...")
        for feedback_type in CONFIG.feedback_types:
            print(f"  Condition: {feedback_type}")
            results = run_condition(problems, refiner, feedback_type, dataset_name)
            all_results.extend(results)
            for r in results:
                all_edit_records.extend(r.get("edit_records", []))

    # Save results
    output = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "seed": CONFIG.seed,
            "model_id": CONFIG.model_id,
            "max_iterations": CONFIG.max_iterations,
            "datasets": CONFIG.datasets,
            "feedback_types": CONFIG.feedback_types
        },
        "results": all_results,
        "edit_records": all_edit_records
    }

    with open(CONFIG.results_path, "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to {CONFIG.results_path}")

if __name__ == "__main__":
    main()
