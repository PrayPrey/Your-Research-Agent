import ast
import sys
import tempfile
import os
from typing import Optional


def run_evalplus_tests(task_id: str, completion: str) -> dict:
    """Execute completion against evalplus test suite.
    Returns: {passed: bool, error_type: Optional[str]}
    error_type in {None, 'syntax', 'runtime', 'logic'}
    """
    # Check syntax first
    try:
        ast.parse(completion)
    except SyntaxError:
        return {"passed": False, "error_type": "syntax"}

    # Use evalplus Python API
    try:
        from evalplus.data import get_human_eval_plus, get_mbpp_plus
        from evalplus.eval import check_correctness

        # Determine dataset from task_id prefix
        if task_id.startswith("HumanEval/") or task_id.startswith("humaneval"):
            problems = get_human_eval_plus()
        elif task_id.startswith("Mbpp/") or task_id.startswith("mbpp"):
            problems = get_mbpp_plus()
        else:
            problems = get_human_eval_plus()

        if task_id not in problems:
            # task_id not found — treat as runtime error
            return {"passed": False, "error_type": "runtime"}

        problem = problems[task_id]
        result = check_correctness(
            dataset="humaneval" if "HumanEval" in task_id else "mbpp",
            completion_id=0,
            problem=problem,
            solution=completion,
            expected_output=problem.get("expected_output", None),
            fast_check=True,
            identifier=task_id,
            min_time_limit=1.0,
            gt_time_limit_factor=4.0,
        )
        passed = result.get("passed", False)
        if passed:
            return {"passed": True, "error_type": None}
        else:
            # Distinguish logic vs runtime from result
            err = str(result.get("result", ""))
            if "Timeout" in err or "timeout" in err:
                return {"passed": False, "error_type": "runtime"}
            return {"passed": False, "error_type": "logic"}

    except ImportError:
        pass
    except Exception as e:
        err_str = str(e)
        if "syntax" in err_str.lower():
            return {"passed": False, "error_type": "syntax"}
        return {"passed": False, "error_type": "runtime"}

    # Fallback: simple execution check
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(completion)
            tmp_path = f.name
        result = os.popen(f"{sys.executable} {tmp_path} 2>&1").read()
        os.unlink(tmp_path)
        if "Error" in result or "Traceback" in result:
            return {"passed": False, "error_type": "runtime"}
        return {"passed": True, "error_type": None}
    except Exception:
        return {"passed": False, "error_type": "runtime"}


REWARD_MAP = {
    None: 1.0,       # passed
    "logic": 0.2,    # runs but fails tests
    "runtime": -0.2, # runtime error
    "syntax": -0.5,  # syntax error
}


def execution_reward_binary(
    completions: list,
    prompts: list,
    task_ids: list = None,
    **kwargs,
) -> list:
    """Binary reward: +1.0 if all tests pass, 0.0 otherwise."""
    if task_ids is None:
        task_ids = kwargs.get("task_ids", [None] * len(completions))
    rewards = []
    for completion, task_id in zip(completions, task_ids):
        if task_id is None:
            # No task_id — check syntax only
            try:
                ast.parse(completion)
                rewards.append(1.0)
            except SyntaxError:
                rewards.append(0.0)
        else:
            result = run_evalplus_tests(task_id, completion)
            rewards.append(1.0 if result["passed"] else 0.0)
    return rewards


def execution_reward_error_type(
    completions: list,
    prompts: list,
    task_ids: list = None,
    **kwargs,
) -> list:
    """Graded reward by error type."""
    if task_ids is None:
        task_ids = kwargs.get("task_ids", [None] * len(completions))
    rewards = []
    for completion, task_id in zip(completions, task_ids):
        if task_id is None:
            try:
                ast.parse(completion)
                rewards.append(REWARD_MAP[None])
            except SyntaxError:
                rewards.append(REWARD_MAP["syntax"])
        else:
            result = run_evalplus_tests(task_id, completion)
            rewards.append(REWARD_MAP[result["error_type"]])
    return rewards
