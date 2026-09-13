"""Dataset loading for HumanEval+ and MBPP+ benchmarks."""

from typing import Dict, List
from evalplus.data import get_human_eval_plus, get_mbpp_plus


def load_humaneval_plus() -> Dict[str, dict]:
    """Load 164 HumanEval+ problems.

    Returns:
        Dict mapping task_id to problem dict with keys: prompt, test, entry_point
    """
    return get_human_eval_plus()


def load_mbpp_plus() -> Dict[str, dict]:
    """Load 378 MBPP+ problems.

    Returns:
        Dict mapping task_id to problem dict with keys: prompt, test, entry_point
    """
    return get_mbpp_plus()


def load_combined_dataset() -> List[dict]:
    """Merge HumanEval+ (164) + MBPP+ (378) = 542 problems.

    Returns:
        List of problem dicts with keys: task_id, prompt, test, entry_point, source
        source: "humaneval" | "mbpp"
    """
    problems = []

    # Load HumanEval+
    humaneval = load_humaneval_plus()
    for task_id, problem in humaneval.items():
        problems.append({
            "task_id": task_id,
            "prompt": problem["prompt"],
            "test": problem.get("test", ""),
            "entry_point": problem["entry_point"],
            "source": "humaneval"
        })

    # Load MBPP+
    mbpp = load_mbpp_plus()
    for task_id, problem in mbpp.items():
        problems.append({
            "task_id": task_id,
            "prompt": problem["prompt"],
            "test": problem.get("test", ""),
            "entry_point": problem["entry_point"],
            "source": "mbpp"
        })

    print(f"Loaded {len(problems)} problems: {len(humaneval)} HumanEval+ + {len(mbpp)} MBPP+")
    return problems
