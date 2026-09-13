"""Ground truth data loading and generation for H-M1."""
import random
from typing import Dict


def load_humaneval_problems(n_problems: int = 164, seed: int = 42) -> Dict[str, Dict]:
    """
    Generate synthetic HumanEval+ problem set.
    In production: use evalplus.data.get_human_eval_plus()
    """
    random.seed(seed)
    problems = {}
    for i in range(n_problems):
        task_id = f"HumanEval/{i}"
        problems[task_id] = {
            "task_id": task_id,
            "prompt": f"def solution_{i}(x): # Problem {i} specification",
            "canonical_solution": f"    return x * {i+1}",
            "entry_point": f"solution_{i}",
        }
    return problems


def generate_ground_truth(problems: Dict[str, Dict], seed: int = 42) -> Dict[str, int]:
    """
    Generate ground truth pass/fail for each problem.
    Simulates execution results: ~70% pass rate typical for code benchmarks.
    """
    random.seed(seed)
    ground_truth = {}
    for task_id in problems:
        ground_truth[task_id] = 1 if random.random() < 0.70 else 0
    return ground_truth


def load_ground_truth(dataset: str = "humaneval", n_problems: int = 164, seed: int = 42):
    """Load problems and generate ground truth."""
    problems = load_humaneval_problems(n_problems, seed)
    gt = generate_ground_truth(problems, seed)
    return problems, gt
