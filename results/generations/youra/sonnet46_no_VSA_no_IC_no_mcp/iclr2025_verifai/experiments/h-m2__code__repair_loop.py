"""H-M2 repair loops: Condition A (exec-only) and Condition B (exec+mypy)."""

import logging
import pathlib
import subprocess
import sys
import tempfile
import time

from openai import OpenAI

# H-E1 pipeline on path for shared utilities
_h_e1_path = str(pathlib.Path(__file__).parent.parent.parent / "h-e1/code")
if _h_e1_path not in sys.path:
    sys.path.insert(0, _h_e1_path)

from pipeline import (
    extract_code,
    generate_solution,
    evaluate_solution,
    load_problems,
    MYPY_FLAGS,
)

logger = logging.getLogger(__name__)

_MYPY_TIMEOUT = 10


def run_mypy(code: str, timeout: int = _MYPY_TIMEOUT) -> tuple:
    """Run mypy; return (error_count, mypy_stdout)."""
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code)
            tmp = f.name
        result = subprocess.run(
            ["mypy", *MYPY_FLAGS, tmp],
            capture_output=True, text=True, timeout=timeout,
        )
        error_lines = [l for l in result.stdout.splitlines() if "error:" in l]
        return (len(error_lines), result.stdout)
    except subprocess.TimeoutExpired:
        logger.warning(f"mypy timeout — counting as 0 errors")
        return (0, "")
    finally:
        if tmp:
            pathlib.Path(tmp).unlink(missing_ok=True)


def _llm_repair(client: OpenAI, prompt: str, max_tokens: int = 2048,
                 max_retries: int = 3, base_delay: float = 1.0) -> str:
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=max_tokens,
            )
            return extract_code(response.choices[0].message.content)
        except Exception as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"LLM repair failed: {e}")
            time.sleep(base_delay * (2 ** attempt))


def _build_prompt_a(problem: dict, prev_solution: str, exec_feedback: str) -> str:
    """Condition A: execution feedback only."""
    prob_text = problem.get("prompt", problem.get("text", ""))
    return "\n".join([
        f"Problem: {prob_text}",
        "",
        "Previous solution:",
        prev_solution,
        "",
        "Execution feedback:",
        exec_feedback or "(no execution output)",
        "",
        "Please fix the errors and provide a corrected solution.",
        "Return ONLY the complete Python function implementation, no explanation.",
    ])


def _build_prompt_b(problem: dict, prev_solution: str,
                    exec_feedback: str, mypy_stdout: str) -> str:
    """Condition B: execution + mypy feedback."""
    prob_text = problem.get("prompt", problem.get("text", ""))
    return "\n".join([
        f"Problem: {prob_text}",
        "",
        "Previous solution:",
        prev_solution,
        "",
        "Execution feedback:",
        exec_feedback or "(no execution output)",
        "",
        "Type checker (mypy) feedback:",
        mypy_stdout or "(no mypy errors)",
        "",
        "Please fix the errors and provide a corrected solution.",
        "Return ONLY the complete Python function implementation, no explanation.",
    ])


def run_condition_a(client: OpenAI, task_id: str, problem: dict,
                    seed: int = 42, k_max: int = 5) -> dict:
    """Execution-only repair loop. Returns {task_id, rounds, initial_mypy_errors, final_passed}."""
    solution = generate_solution(client, problem, seed)
    if not solution:
        return {"task_id": task_id, "rounds": [], "initial_mypy_errors": 0,
                "final_passed": False, "condition": "A"}

    # Get initial mypy errors (for category labeling — same as round 0 CondB)
    initial_mypy_errors, _ = run_mypy(solution)

    rounds = []
    for k in range(1, k_max + 1):
        exec_passed = evaluate_solution(task_id, solution, problem)
        rounds.append({"round": k, "exec_passed": exec_passed})
        if exec_passed:
            break
        if k < k_max:
            fb = "Execution failed: test cases did not pass."
            prompt = _build_prompt_a(problem, solution, fb)
            try:
                solution = _llm_repair(client, prompt)
            except RuntimeError as e:
                logger.error(f"[CondA] Repair failed at k={k} for {task_id}: {e}")
                break

    final_passed = any(r["exec_passed"] for r in rounds)
    return {"task_id": task_id, "rounds": rounds,
            "initial_mypy_errors": initial_mypy_errors,
            "final_passed": final_passed, "condition": "A"}


def run_condition_b(client: OpenAI, task_id: str, problem: dict,
                    seed: int = 42, k_max: int = 5) -> dict:
    """Execution+mypy repair loop. Returns same schema as run_condition_a."""
    solution = generate_solution(client, problem, seed)
    if not solution:
        return {"task_id": task_id, "rounds": [], "initial_mypy_errors": 0,
                "final_passed": False, "condition": "B"}

    initial_mypy_errors, _ = run_mypy(solution)

    rounds = []
    for k in range(1, k_max + 1):
        mypy_count, mypy_stdout = run_mypy(solution)
        exec_passed = evaluate_solution(task_id, solution, problem)
        rounds.append({"round": k, "exec_passed": exec_passed,
                       "mypy_error_count": mypy_count})
        if exec_passed:
            break
        if k < k_max:
            fb = "Execution failed: test cases did not pass."
            prompt = _build_prompt_b(problem, solution, fb, mypy_stdout)
            try:
                solution = _llm_repair(client, prompt)
            except RuntimeError as e:
                logger.error(f"[CondB] Repair failed at k={k} for {task_id}: {e}")
                break

    final_passed = any(r["exec_passed"] for r in rounds)
    return {"task_id": task_id, "rounds": rounds,
            "initial_mypy_errors": initial_mypy_errors,
            "final_passed": final_passed, "condition": "B"}
