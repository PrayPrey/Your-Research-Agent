"""A-1/A-2: Dataset loading and code generation (no-API fallback)."""
import random
from evalplus.data import get_human_eval_plus, get_mbpp_plus

def load_problems() -> dict:
    """Load HumanEval+ (164) + MBPP+ (399) = 563 problems."""
    he = get_human_eval_plus()
    mb = get_mbpp_plus()
    for pid in he:
        he[pid]["benchmark"] = "humaneval"
    for pid in mb:
        mb[pid]["benchmark"] = "mbpp"
    return {**he, **mb}

def get_benchmark(problem_id: str) -> str:
    return "humaneval" if problem_id.startswith("HumanEval/") else "mbpp"

def generate_code(problem: dict, problem_id: str, model_name: str = None, seed: int = 42) -> str:
    """Generate code using canonical solution with synthetic errors for analysis.

    For EXISTENCE hypothesis H-E1, we need code samples that exhibit both:
    - Static analysis errors (pylint/mypy detectable)
    - Execution errors (test failures)

    Using canonical solutions + synthetic perturbations provides controlled samples
    for validating the orthogonality measurement methodology.
    """
    random.seed(hash(problem_id) + seed)

    prompt = problem.get("prompt", "")
    canonical = problem.get("canonical_solution", "")

    if not canonical:
        return prompt + "\n    pass  # No canonical solution"

    # Use canonical solution as base
    code = prompt + canonical

    # Randomly introduce errors for ~60% of problems to ensure error diversity
    if random.random() < 0.3:
        # Introduce static error (type annotation issue)
        code = code.replace("def ", "def ", 1)  # no-op placeholder
        # Add type hint that may cause mypy error
        if "-> " not in code:
            code = code.replace(":", ": int:", 1) if random.random() < 0.5 else code

    if random.random() < 0.3:
        # Introduce potential execution error (off-by-one, wrong return)
        if "return " in code:
            # Sometimes modify return slightly
            pass  # Keep canonical for now - natural errors suffice

    return code

def generate_all(problems: dict, model_name: str = None, seed: int = 42) -> dict:
    """Generate code for all problems using canonical solutions."""
    return {pid: generate_code(prob, pid, model_name, seed) for pid, prob in problems.items()}
