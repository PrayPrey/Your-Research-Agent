"""H-M3 repair loops: extends h-m2 with token logging and multi-seed support."""

import logging
import pathlib
import subprocess
import sys
import tempfile
import time

from openai import OpenAI

_h_e1_path = str(pathlib.Path(__file__).parent.parent.parent / "h-e1/code")
if _h_e1_path not in sys.path:
    sys.path.insert(0, _h_e1_path)

from pipeline import (
    extract_code,
    generate_solution,
    evaluate_solution,
    load_problems,
)

logger = logging.getLogger(__name__)

_MYPY_FLAGS = ["--ignore-missing-imports", "--no-strict-optional", "--no-error-summary"]
_MYPY_TIMEOUT = 10


def run_mypy(code: str, flags: list = None, timeout: int = _MYPY_TIMEOUT) -> tuple:
    """Return (error_count, mypy_stdout)."""
    if flags is None:
        flags = _MYPY_FLAGS
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code)
            tmp = f.name
        result = subprocess.run(
            ["mypy", *flags, tmp],
            capture_output=True, text=True, timeout=timeout,
        )
        error_lines = [l for l in result.stdout.splitlines() if "error:" in l]
        return (len(error_lines), result.stdout)
    except subprocess.TimeoutExpired:
        logger.warning("mypy timeout — counting as 0 errors")
        return (0, "")
    finally:
        if tmp:
            pathlib.Path(tmp).unlink(missing_ok=True)


def _count_tokens(prompt: str) -> int:
    # ponytail: approx token count, swap tiktoken if exact billing needed
    return len(prompt.split()) * 4 // 3


def _build_prompt_a(problem: dict, prev_solution: str, exec_feedback: str) -> str:
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


def _llm_repair(client: OpenAI, prompt: str, max_tokens: int = 2048,
                max_retries: int = 3, base_delay: float = 1.0) -> tuple:
    """Return (repaired_code, prompt_token_count)."""
    token_count = _count_tokens(prompt)
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=max_tokens,
            )
            return (extract_code(response.choices[0].message.content), token_count)
        except Exception as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"LLM repair failed: {e}")
            time.sleep(base_delay * (2 ** attempt))


def run_condition_a_h3(client: OpenAI, task_id: str, problem: dict,
                       seed: int = 42, k_max: int = 5) -> dict:
    """Execution-only repair loop with token logging."""
    solution = generate_solution(client, problem, seed)
    if not solution:
        return {"task_id": task_id, "condition": "A", "seed": seed,
                "rounds": [], "initial_mypy_errors": 0, "final_passed": False}

    initial_mypy_errors, _ = run_mypy(solution)

    rounds = []
    for k in range(1, k_max + 1):
        exec_passed = evaluate_solution(task_id, solution, problem)
        if exec_passed:
            rounds.append({"round": k, "exec_passed": True, "prompt_tokens": 0})
            break
        if k < k_max:
            fb = "Execution failed: test cases did not pass."
            prompt = _build_prompt_a(problem, solution, fb)
            try:
                solution, tokens = _llm_repair(client, prompt)
            except RuntimeError as e:
                logger.error(f"[CondA] Repair failed at k={k} for {task_id}: {e}")
                rounds.append({"round": k, "exec_passed": False, "prompt_tokens": 0})
                break
            rounds.append({"round": k, "exec_passed": False, "prompt_tokens": tokens})
        else:
            rounds.append({"round": k, "exec_passed": False, "prompt_tokens": 0})

    final_passed = any(r["exec_passed"] for r in rounds)
    return {"task_id": task_id, "condition": "A", "seed": seed,
            "rounds": rounds, "initial_mypy_errors": initial_mypy_errors,
            "final_passed": final_passed}


def run_condition_b_h3(client: OpenAI, task_id: str, problem: dict,
                       seed: int = 42, k_max: int = 5) -> dict:
    """Execution+mypy repair loop with token logging."""
    solution = generate_solution(client, problem, seed)
    if not solution:
        return {"task_id": task_id, "condition": "B", "seed": seed,
                "rounds": [], "initial_mypy_errors": 0, "final_passed": False}

    initial_mypy_errors, _ = run_mypy(solution)

    rounds = []
    for k in range(1, k_max + 1):
        mypy_count, mypy_stdout = run_mypy(solution)
        exec_passed = evaluate_solution(task_id, solution, problem)
        if exec_passed:
            rounds.append({"round": k, "exec_passed": True,
                           "mypy_error_count": mypy_count, "prompt_tokens": 0})
            break
        if k < k_max:
            if mypy_count > 0:
                logger.info(f"MYPY_FEEDBACK_ADDED: {mypy_count} errors for {task_id} round {k}")
            fb = "Execution failed: test cases did not pass."
            prompt = _build_prompt_b(problem, solution, fb, mypy_stdout)
            try:
                solution, tokens = _llm_repair(client, prompt)
            except RuntimeError as e:
                logger.error(f"[CondB] Repair failed at k={k} for {task_id}: {e}")
                rounds.append({"round": k, "exec_passed": False,
                               "mypy_error_count": mypy_count, "prompt_tokens": 0})
                break
            rounds.append({"round": k, "exec_passed": False,
                           "mypy_error_count": mypy_count, "prompt_tokens": tokens})
        else:
            rounds.append({"round": k, "exec_passed": False,
                           "mypy_error_count": mypy_count, "prompt_tokens": 0})

    final_passed = any(r["exec_passed"] for r in rounds)
    return {"task_id": task_id, "condition": "B", "seed": seed,
            "rounds": rounds, "initial_mypy_errors": initial_mypy_errors,
            "final_passed": final_passed}


def _make_key(dataset: str, seed: int, condition: str, task_id: str) -> str:
    return f"{dataset}__{seed}__{condition}__{task_id}"
