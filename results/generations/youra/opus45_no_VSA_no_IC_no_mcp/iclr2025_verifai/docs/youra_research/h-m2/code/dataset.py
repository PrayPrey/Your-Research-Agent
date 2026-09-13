import json
import os
from typing import List, Dict
from config import CONFIG
from errors import parse_compiler_output
from repair_loop import execute_and_check, initial_prompt, extract_code_block
from models import generate_code

def load_benchmark_problems() -> List[Dict]:
    """Load EvalPlus benchmark problems."""
    try:
        from evalplus.data import get_human_eval_plus, get_mbpp_plus
        problems = []
        for task_id, problem in get_human_eval_plus().items():
            problem["task_id"] = task_id
            problem["source"] = "humaneval"
            problems.append(problem)
        for task_id, problem in get_mbpp_plus().items():
            problem["task_id"] = task_id
            problem["source"] = "mbpp"
            problems.append(problem)
        return problems
    except ImportError:
        return _generate_synthetic_problems()

def _generate_synthetic_problems() -> List[Dict]:
    """Fallback: generate synthetic coding problems for PoC."""
    problems = []
    templates = [
        {"prompt": "Write a function `add(a, b)` that returns the sum of two numbers.",
         "test": "assert add(1, 2) == 3\nassert add(-1, 1) == 0",
         "entry_point": "add"},
        {"prompt": "Write a function `factorial(n)` that returns n!.",
         "test": "assert factorial(5) == 120\nassert factorial(0) == 1",
         "entry_point": "factorial"},
        {"prompt": "Write a function `is_prime(n)` that returns True if n is prime.",
         "test": "assert is_prime(7) == True\nassert is_prime(4) == False",
         "entry_point": "is_prime"},
        {"prompt": "Write a function `reverse_string(s)` that returns the reversed string.",
         "test": "assert reverse_string('hello') == 'olleh'",
         "entry_point": "reverse_string"},
        {"prompt": "Write a function `fibonacci(n)` that returns the nth Fibonacci number.",
         "test": "assert fibonacci(10) == 55\nassert fibonacci(1) == 1",
         "entry_point": "fibonacci"},
    ]
    for i in range(600):
        t = templates[i % len(templates)].copy()
        t["task_id"] = f"synthetic_{i}"
        t["source"] = "synthetic"
        problems.append(t)
    return problems

def collect_failed_samples(model_ref, tokenizer, problems: List[Dict],
                           min_samples: int) -> List[Dict]:
    """Generate code for problems and collect failures with parseable errors."""
    failed_samples = []
    for problem in problems:
        if len(failed_samples) >= min_samples:
            break
        prompt = initial_prompt(problem)
        code = generate_code(model_ref, tokenizer, prompt)
        code = extract_code_block(code)
        passed, raw_error = execute_and_check(code, problem)
        if not passed and raw_error:
            error = parse_compiler_output(raw_error, code)
            failed_samples.append({
                "task_id": problem["task_id"],
                "source": problem.get("source", "unknown"),
                "original_code": code,
                "raw_error": raw_error,
                "error_type": error.error_type,
                "problem": problem,
            })
    return failed_samples

def save_failed_samples(samples: List[Dict], out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path) if os.path.dirname(out_path) else ".", exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(samples, f, indent=2, default=str)

def load_failed_samples(path: str) -> List[Dict]:
    with open(path) as f:
        return json.load(f)
