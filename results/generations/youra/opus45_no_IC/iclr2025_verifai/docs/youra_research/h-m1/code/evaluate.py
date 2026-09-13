import ast

def check_syntax(code: str) -> bool:
    if not code or not code.strip():
        return False
    try:
        ast.parse(code)
        return True
    except (SyntaxError, ValueError):
        return False

def compilation_error_rate(samples: list[str]) -> float:
    if not samples:
        return 0.0
    errors = sum(1 for s in samples if not check_syntax(s))
    return errors / len(samples)

def evaluate_condition(problem_results: dict[str, list[str]]) -> dict:
    n_errors = 0
    n_total = 0
    per_problem = {}

    for task_id, samples in problem_results.items():
        task_errors = sum(1 for s in samples if not check_syntax(s))
        task_total = len(samples)
        per_problem[task_id] = task_errors / task_total if task_total > 0 else 0.0
        n_errors += task_errors
        n_total += task_total

    return {
        "error_rate": n_errors / n_total if n_total > 0 else 0.0,
        "n_errors": n_errors,
        "n_total": n_total,
        "per_problem": per_problem
    }
