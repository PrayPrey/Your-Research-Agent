import json
import random
from config import CONFIG
from data import load_all_problems
from model import ExecutionFeedbackRefinement
from edit_scope_classify import label_edit_records

POC_SAMPLES = 50

def run_condition(problems: list[dict], refiner: ExecutionFeedbackRefinement, dataset_name: str) -> tuple[list[dict], list[dict]]:
    """Run detailed-feedback refinement. Returns (results, all_edit_records)."""
    results = []
    all_edit_records = []
    for i, problem in enumerate(problems):
        print(f"  [{i+1}/{len(problems)}] {problem['task_id']}", flush=True)
        code, passed, iteration, edit_records = refiner.generate_with_refinement(problem, "detailed")
        results.append({
            "problem_id": problem["task_id"],
            "dataset": dataset_name,
            "passed": passed,
            "iteration": iteration,
        })
        for rec in edit_records:
            rec["problem_id"] = problem["task_id"]
            rec["dataset"] = dataset_name
        all_edit_records.extend(edit_records)
    return results, all_edit_records

def main():
    random.seed(CONFIG.seed)
    all_problems = load_all_problems()

    refiner = ExecutionFeedbackRefinement()

    all_results = []
    all_edit_records = []

    for dataset_name, problems in all_problems.items():
        print(f"\nDataset: {dataset_name}")
        sampled = random.sample(problems, min(POC_SAMPLES, len(problems)))
        results, edit_records = run_condition(sampled, refiner, dataset_name)
        all_results.extend(results)
        all_edit_records.extend(edit_records)

    label_edit_records(all_edit_records)

    output = {
        "results": all_results,
        "edit_records": all_edit_records,
    }

    with open(CONFIG.results_path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nSaved {len(all_results)} results, {len(all_edit_records)} edit records to {CONFIG.results_path}")

if __name__ == "__main__":
    main()
