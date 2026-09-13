"""Dataset loading for H-C1 experiment."""
import json
from pathlib import Path
from typing import Any

from evalplus.data import get_human_eval_plus, get_mbpp_plus

from config import Config


def load_humaneval_plus(cfg: Config) -> dict[str, Any]:
    """Load HumanEval+ dataset (164 problems)."""
    cache_file = cfg.cache_dir / "humaneval_plus.json"
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)

    problems = get_human_eval_plus()
    with open(cache_file, "w") as f:
        json.dump(problems, f)
    return problems


def load_mbpp_plus(cfg: Config) -> dict[str, Any]:
    """Load MBPP+ dataset (378 problems)."""
    cache_file = cfg.cache_dir / "mbpp_plus.json"
    if cache_file.exists():
        with open(cache_file) as f:
            return json.load(f)

    problems = get_mbpp_plus()
    with open(cache_file, "w") as f:
        json.dump(problems, f)
    return problems


def get_training_data(problems: dict[str, Any]) -> list[dict]:
    """Convert problems to training format."""
    data = []
    for task_id, problem in problems.items():
        data.append({
            "task_id": task_id,
            "prompt": problem["prompt"],
            "entry_point": problem["entry_point"],
            "canonical_solution": problem.get("canonical_solution", ""),
            "test": problem.get("test", ""),
            "base_input": problem.get("base_input", []),
        })
    return data
