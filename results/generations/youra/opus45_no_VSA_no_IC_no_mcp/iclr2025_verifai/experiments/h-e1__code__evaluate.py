from typing import Dict, List
from collections import Counter
from datasets import load_dataset
from repair_loop import repair_problem
from models import load_hf_model
from config import CONFIG

def load_benchmark_problems(benchmark: str) -> List[Dict]:
    dataset_name = CONFIG["benchmark_datasets"].get(benchmark)
    if not dataset_name:
        raise ValueError(f"Unknown benchmark: {benchmark}")

    ds = load_dataset(dataset_name, split="test")
    problems = []
    for row in ds:
        row_dict = dict(row)
        if "entry_point" not in row_dict or "test" not in row_dict:
            continue
        problems.append(row_dict)

    if not problems:
        raise RuntimeError(f"No problems loaded from {benchmark}")
    return problems

def run_benchmark(model_name: str, benchmark: str, use_structured: bool) -> Dict:
    problems = load_benchmark_problems(benchmark)
    is_openai = model_name in CONFIG["openai_models"]

    if is_openai:
        model_ref, tokenizer = None, None
    else:
        model_ref, tokenizer = load_hf_model(model_name)

    results = []
    for i, problem in enumerate(problems):
        result = repair_problem(model_ref, tokenizer, problem, use_structured, is_openai=is_openai)
        results.append(result)
        if (i + 1) % 50 == 0:
            print(f"  Progress: {i+1}/{len(problems)}")

    pass_at_1 = sum(r["passed"] for r in results) / len(results)
    had_error = [r for r in results if r["attempts_used"] > 0 or not r["passed"]]
    repair_success_rate = sum(r["passed"] for r in had_error) / len(had_error) if had_error else 0.0
    avg_attempts = sum(r["attempts_used"] for r in had_error) / len(had_error) if had_error else 0.0

    all_error_types = []
    for r in results:
        all_error_types.extend(r["error_types_seen"])
    error_breakdown = dict(Counter(all_error_types))

    return {
        "pass_at_1": pass_at_1,
        "repair_success_rate": repair_success_rate,
        "avg_attempts": avg_attempts,
        "error_breakdown": error_breakdown,
        "total_problems": len(problems),
        "problems_passed": sum(r["passed"] for r in results)
    }

def aggregate_results(all_results: Dict) -> Dict:
    return all_results
