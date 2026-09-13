"""H-M2: Dataset loading and code generation."""
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
    """Generate code using canonical solution from evalplus.

    H-M2 reuses canonical solutions from evalplus (same as H-E1/H-M1).
    Any behavioral errors come from natural edge cases in extended test suites,
    not artificial injection.
    """
    prompt = problem.get("prompt", "")
    canonical = problem.get("canonical_solution", "")

    if not canonical:
        return prompt + "\n    pass  # No canonical solution"

    return prompt + canonical


def generate_all(problems: dict, model_name: str = None, seed: int = 42) -> dict:
    """Generate code for all problems using canonical solutions."""
    return {pid: generate_code(prob, pid, model_name, seed) for pid, prob in problems.items()}
