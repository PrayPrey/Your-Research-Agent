import json
import random
import torch
from tqdm import tqdm
from config import CONFIG
from data import load_all_problems
from model import ExecutionFeedbackRefinement

def run_condition(
    problems: list[dict],
    refiner: ExecutionFeedbackRefinement,
    feedback_type: str,
    dataset_name: str,
) -> list[dict]:
    results = []
    for problem in tqdm(problems, desc=f"{dataset_name}/{feedback_type}"):
        code, passed, iterations, feedback_log = refiner.generate_with_refinement(problem, feedback_type)
        results.append({
            "task_id": problem["task_id"],
            "dataset": dataset_name,
            "feedback_type": feedback_type,
            "passed": passed,
            "iterations_used": iterations,
            "code": code,
            "feedback_log": feedback_log,
        })
    return results

def main():
    random.seed(CONFIG.seed)
    torch.manual_seed(CONFIG.seed)

    print("Loading datasets...")
    all_problems = load_all_problems()

    print("Loading model...")
    refiner = ExecutionFeedbackRefinement()

    all_results = []
    for dataset_name in CONFIG.datasets:
        problems = all_problems[dataset_name]
        print(f"\nRunning {dataset_name} ({len(problems)} problems)")

        for feedback_type in CONFIG.feedback_types:
            print(f"  Condition: {feedback_type}")
            results = run_condition(problems, refiner, feedback_type, dataset_name)
            all_results.extend(results)

    with open(CONFIG.results_path, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nResults saved to {CONFIG.results_path}")

if __name__ == "__main__":
    main()
