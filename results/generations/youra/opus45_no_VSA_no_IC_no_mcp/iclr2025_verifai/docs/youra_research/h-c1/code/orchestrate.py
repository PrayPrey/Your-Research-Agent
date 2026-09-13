import os
import json
from dataclasses import dataclass, asdict
from typing import List, Dict
import pandas as pd

from config import CONFIG
from repair_loop import repair_problem
from models import load_hf_model
from evaluate import load_benchmark_problems

@dataclass
class CellResult:
    model: str
    format: str
    problem_id: str
    passed: bool
    attempts_used: int

def get_cache_path(model_key: str, fmt: str) -> str:
    return os.path.join(CONFIG["cache_dir"], f"{model_key}_{fmt}.json")

def save_cell_cache(results: List[CellResult], path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump([asdict(r) for r in results], f)

def load_cell_cache(path: str) -> List[CellResult]:
    with open(path) as f:
        return [CellResult(**r) for r in json.load(f)]

def run_cell(model_name: str, use_structured: bool, problems: List[Dict]) -> List[CellResult]:
    model_key = CONFIG["model_keys"][model_name]
    is_openai = model_name in CONFIG["openai_models"]
    fmt = "structured" if use_structured else "raw"

    cache_path = get_cache_path(model_key, fmt)
    if CONFIG["cache_enabled"] and os.path.exists(cache_path):
        print(f"  Loading cached results: {model_key}/{fmt}")
        return load_cell_cache(cache_path)

    if is_openai:
        model_ref, tokenizer = None, None
    else:
        model_ref, tokenizer = load_hf_model(model_name)

    results = []
    for i, problem in enumerate(problems):
        task_id = problem.get("task_id", str(i))
        result = repair_problem(
            model_ref, tokenizer, problem, use_structured,
            max_attempts=CONFIG["max_iterations"], is_openai=is_openai
        )
        results.append(CellResult(
            model=model_key,
            format=fmt,
            problem_id=task_id,
            passed=result["passed"],
            attempts_used=result["attempts_used"]
        ))
        if (i + 1) % 50 == 0:
            print(f"  {model_key}/{fmt}: {i+1}/{len(problems)}")

    save_cell_cache(results, cache_path)
    return results

def run_all_cells(force: bool = False) -> pd.DataFrame:
    all_problems = []
    for bench in CONFIG["benchmarks"]:
        probs = load_benchmark_problems(bench)
        for p in probs:
            p["benchmark"] = bench
        all_problems.extend(probs)

    print(f"Loaded {len(all_problems)} problems (HumanEval+ + MBPP+)")

    all_results = []
    for model_name in CONFIG["models"]:
        model_key = CONFIG["model_keys"][model_name]
        for fmt in CONFIG["prompt_formats"]:
            use_structured = (fmt == "structured")
            print(f"Running cell: {model_key}/{fmt}")
            cell_results = run_cell(model_name, use_structured, all_problems)
            all_results.extend(cell_results)

    df = pd.DataFrame([asdict(r) for r in all_results])
    df["passed_int"] = df["passed"].astype(int)
    return df
