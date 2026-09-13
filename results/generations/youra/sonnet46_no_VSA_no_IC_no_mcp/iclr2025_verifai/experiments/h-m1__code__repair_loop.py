"""H-M1 repair loop: Condition B (execution + mypy feedback)."""

import logging
import pathlib
import subprocess
import sys
import tempfile
import time

from openai import OpenAI

# H-E1 pipeline on path (run.py sets this up, or set here as fallback)
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

_MYPY_TIMEOUT = 10  # reduced from H-E1's 30s for throughput at k=5 rounds


def run_mypy_with_output(code: str, timeout: int = _MYPY_TIMEOUT) -> tuple:
    """Run mypy; return (has_error, error_count, mypy_stdout)."""
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code)
            tmp = f.name

        result = subprocess.run(
            ["mypy", *MYPY_FLAGS, tmp],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        error_lines = [line for line in result.stdout.splitlines() if "error:" in line]
        error_count = len(error_lines)
        has_error = result.returncode != 0
        return (has_error, error_count, result.stdout)

    except FileNotFoundError:
        raise

    except subprocess.TimeoutExpired:
        logger.warning(f"mypy timeout ({timeout}s) — counting as 0 errors")
        return (False, 0, "")

    finally:
        if tmp:
            pathlib.Path(tmp).unlink(missing_ok=True)


def _build_repair_prompt(
    problem: dict,
    prev_solution: str,
    exec_feedback: str,
    mypy_stdout: str,
) -> str:
    """Condition B repair prompt with both feedback signals."""
    problem_prompt = problem.get("prompt", problem.get("text", ""))
    parts = [
        f"Problem: {problem_prompt}",
        "",
        "Previous solution:",
        f"{prev_solution}",
        "",
        "Execution feedback:",
        f"{exec_feedback if exec_feedback else '(no execution output)'}",
        "",
        "Type checker (mypy) feedback:",
        f"{mypy_stdout if mypy_stdout else '(no mypy errors)'}",
        "",
        "Please fix the above errors and provide a corrected solution.",
        "Return ONLY the complete Python function implementation, no explanation.",
    ]
    return "\n".join(parts)


def _generate_repair(
    client: OpenAI,
    prompt: str,
    max_tokens: int = 2048,
    max_retries: int = 3,
    base_delay: float = 1.0,
) -> str:
    """GPT-4o-mini at temperature=0.0 with exponential backoff."""
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.0,
                max_tokens=max_tokens,
            )
            raw = response.choices[0].message.content
            return extract_code(raw)
        except Exception as e:
            if attempt == max_retries - 1:
                raise RuntimeError(f"LLM repair failed after {max_retries} attempts: {e}")
            delay = base_delay * (2 ** attempt)
            logger.warning(f"LLM error (attempt {attempt + 1}): {e}. Retrying in {delay}s")
            time.sleep(delay)


def repair_loop_condition_b(
    client: OpenAI,
    task_id: str,
    problem: dict,
    benchmark: str,
    seed: int = 42,
    k_max: int = 5,
) -> list:
    """Run k=1..5 repair rounds with execution+mypy feedback.

    Returns list of per-round dicts. Early-exits if exec_passed=True.
    """
    records = []
    benchmark_short = benchmark.replace("+", "")

    solution = generate_solution(client, problem, seed)
    if not solution:
        logger.warning(f"Empty initial generation for {task_id}, skipping")
        return records

    for k in range(1, k_max + 1):
        _, mypy_count, mypy_stdout = run_mypy_with_output(solution)
        logger.info(f"mypy_errors_round_{k}: {mypy_count} [{task_id}]")  # activation indicator

        exec_passed = evaluate_solution(task_id, solution, problem)
        exec_feedback = "" if exec_passed else "Execution failed: test cases did not pass."

        record = {
            "task_id": task_id,
            "benchmark": benchmark_short,
            "round": k,
            "mypy_error_count": mypy_count,
            "mypy_stdout": mypy_stdout,
            "exec_passed": exec_passed,
            "repaired": k > 1,
            "solution": solution,
        }
        records.append(record)

        if exec_passed:
            break

        if k < k_max:
            repair_prompt = _build_repair_prompt(problem, solution, exec_feedback, mypy_stdout)
            try:
                solution = _generate_repair(client, repair_prompt)
            except RuntimeError as e:
                logger.error(f"Repair failed at round {k} for {task_id}: {e}")
                break

    return records


def run_all_benchmarks(
    client: OpenAI,
    benchmarks: list,
    seed: int = 42,
    k_max: int = 5,
) -> list:
    """Run repair loop across all benchmarks; return flat record list."""
    all_records = []
    for benchmark in benchmarks:
        problems = load_problems(benchmark)
        total = len(problems)
        logger.info(f"Starting {benchmark} ({total} problems)")
        for i, (task_id, problem) in enumerate(problems.items()):
            if i % 20 == 0:
                logger.info(f"[{benchmark}] {i}/{total}")
            try:
                records = repair_loop_condition_b(
                    client, task_id, problem, benchmark, seed, k_max
                )
                all_records.extend(records)
            except Exception as e:
                logger.error(f"Skipping {task_id}: {e}")
    return all_records
