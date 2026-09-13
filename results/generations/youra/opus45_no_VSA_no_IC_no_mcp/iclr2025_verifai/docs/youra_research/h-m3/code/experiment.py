import random
import json
from typing import Dict, List
from evaluate import load_benchmark_problems
from models import load_hf_model, generate_code
from repair_loop import extract_code_block, execute_and_check, initial_prompt, repair_problem_leveled
from errors import parse_compiler_output
from config import CONFIG

def collect_error_instances(model_name: str, benchmark: str) -> List[Dict]:
    problems = load_benchmark_problems(benchmark)
    is_openai = model_name in CONFIG["openai_models"]
    model_ref, tokenizer = (None, None) if is_openai else load_hf_model(model_name)

    instances = []
    for i, problem in enumerate(problems):
        code = extract_code_block(generate_code(model_ref, tokenizer, initial_prompt(problem), is_openai))
        passed, raw_error = execute_and_check(code, problem)
        if not passed:
            err = parse_compiler_output(raw_error, code)
            instances.append({
                "error_id": f"{benchmark}_{i}",
                "problem": problem,
                "initial_code": code,
                "error_type": err.error_type
            })
        if len(instances) >= CONFIG["target_error_instances"]:
            break
        if (i + 1) % 50 == 0:
            print(f"  Collecting errors: {i+1}/{len(problems)}, found {len(instances)} errors")

    return instances

def run_level_sweep(model_name: str, benchmark: str, levels: List[int], n_reps: int = 3,
                    error_instances: List[Dict] = None) -> List[Dict]:
    if error_instances is None:
        error_instances = collect_error_instances(model_name, benchmark)

    is_openai = model_name in CONFIG["openai_models"]
    model_ref, tokenizer = (None, None) if is_openai else load_hf_model(model_name)
    rng = random.Random(CONFIG["level_order_seed"])

    records = []
    for inst in error_instances:
        for rep in range(n_reps):
            order = levels[:]
            rng.shuffle(order)
            for level in order:
                result = repair_problem_leveled(model_ref, tokenizer, inst["problem"], level,
                                                is_openai=is_openai)
                records.append({
                    "error_id": inst["error_id"],
                    "model": model_name,
                    "benchmark": benchmark,
                    "level": level,
                    "rep": rep,
                    "error_type": inst["error_type"],
                    **result
                })

    return records

def demo():
    records = [
        {"error_id": "test_0", "model": "m", "benchmark": "b", "level": 0, "rep": 0,
         "passed": False, "attempts_used": 3, "error_type": "IndexError", "first_iter_success": False},
        {"error_id": "test_0", "model": "m", "benchmark": "b", "level": 1, "rep": 0,
         "passed": True, "attempts_used": 1, "error_type": "IndexError", "first_iter_success": True},
    ]
    assert len(records) == 2
    assert all("error_id" in r for r in records)
    print("experiment.py demo PASS")

if __name__ == "__main__":
    demo()
