"""Condition B and Condition C repair loops for H-Z1."""

import logging
import sys
import time
from dataclasses import dataclass, field
from typing import Optional

from openai import OpenAI

from z3_utils import extract_z3_counterexample, format_z3_ce_for_prompt

logger = logging.getLogger(__name__)


@dataclass
class RoundResult:
    round_num: int
    passed: bool
    exec_feedback: str
    mypy_feedback: str
    z3_ce: Optional[dict]


@dataclass
class ProblemResult:
    task_id: str
    condition: str
    passed: bool
    rounds_to_pass: int
    final_solution: str
    z3_ce_found_count: int
    round_history: list = field(default_factory=list)


def _get_exec_feedback(problem: dict, solution: str) -> str:
    """Run solution and capture execution error feedback."""
    from pipeline import evaluate_solution
    import traceback
    try:
        ns = {}
        exec(compile(solution, "<solution>", "exec"), ns)
        fn = ns.get(problem["entry_point"])
        if fn is None:
            return f"Error: function '{problem['entry_point']}' not defined in solution."

        # Try a quick execution with simple inputs to get error
        base_input = problem.get("base_input", [])
        if base_input:
            inputs = base_input[0] if base_input else ()
            if not isinstance(inputs, (tuple, list)):
                inputs = (inputs,)
            try:
                fn(*inputs)
                return "Execution: ran without error on sample input but failed EvalPlus tests."
            except Exception as e:
                return f"Execution error: {type(e).__name__}: {e}"
        return "Execution: failed EvalPlus test suite."
    except SyntaxError as e:
        return f"Syntax error: {e}"
    except Exception as e:
        return f"Execution error: {type(e).__name__}: {e}"


def build_repair_prompt_b(problem: dict, solution: str, exec_fb: str, mypy_fb: str) -> str:
    """Build repair prompt with execution + mypy feedback only (Condition B)."""
    return f"""Fix the following Python function:

Problem:
{problem['prompt']}

Your previous solution (incorrect):
```python
{solution}
```

Execution feedback:
{exec_fb}

Type feedback (mypy):
{mypy_fb}

Return ONLY the corrected Python function, no explanation."""


def build_repair_prompt_c(problem: dict, solution: str, exec_fb: str, mypy_fb: str,
                           z3_ce: Optional[dict]) -> str:
    """Build repair prompt with execution + mypy + Z3 CE feedback (Condition C)."""
    z3_text = format_z3_ce_for_prompt(z3_ce, problem.get("entry_point", "func"))

    return f"""Fix the following Python function:

Problem:
{problem['prompt']}

Your previous solution (incorrect):
```python
{solution}
```

Execution feedback:
{exec_fb}

Type feedback (mypy):
{mypy_fb}
{z3_text}

Return ONLY the corrected Python function, no explanation."""


def repair_loop_b(problem: dict, initial_solution: str,
                  client: OpenAI, cfg) -> ProblemResult:
    """k=5 rounds: execute → mypy → build_repair_prompt_b → LLM repair."""
    from pipeline import evaluate_solution, run_mypy, extract_code

    solution = initial_solution
    round_history = []

    for round_num in range(1, cfg.k_repair_rounds + 1):
        passed = evaluate_solution(problem["task_id"], solution, problem)
        if passed:
            return ProblemResult(
                task_id=problem["task_id"], condition="B",
                passed=True, rounds_to_pass=round_num,
                final_solution=solution, z3_ce_found_count=0,
                round_history=round_history
            )

        exec_fb = _get_exec_feedback(problem, solution)
        has_mypy_error, _, _, mypy_stdout = run_mypy(solution)
        mypy_fb = mypy_stdout if has_mypy_error else "No mypy errors detected."

        prompt = build_repair_prompt_b(problem, solution, exec_fb, mypy_fb)

        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model=cfg.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=cfg.repair_temperature,
                    max_tokens=cfg.max_tokens,
                    seed=cfg.seed,
                    timeout=60,
                )
                solution = extract_code(response.choices[0].message.content)
                break
            except Exception as e:
                logger.warning(f"Repair attempt {attempt+1} failed: {e}")
                time.sleep(2 ** attempt)

        round_history.append(RoundResult(
            round_num=round_num, passed=False,
            exec_feedback=exec_fb, mypy_feedback=mypy_fb, z3_ce=None
        ))

    # Final check after last repair
    passed = evaluate_solution(problem["task_id"], solution, problem)
    return ProblemResult(
        task_id=problem["task_id"], condition="B",
        passed=passed, rounds_to_pass=cfg.k_repair_rounds + 1,
        final_solution=solution, z3_ce_found_count=0,
        round_history=round_history
    )


def repair_loop_c(problem: dict, initial_solution: str,
                  spec_code: str, client: OpenAI, cfg) -> ProblemResult:
    """k=5 rounds: execute → mypy → Z3 CE → build_repair_prompt_c → LLM repair."""
    from pipeline import evaluate_solution, run_mypy, extract_code

    solution = initial_solution
    z3_ce_found_count = 0
    round_history = []

    for round_num in range(1, cfg.k_repair_rounds + 1):
        passed = evaluate_solution(problem["task_id"], solution, problem)
        if passed:
            return ProblemResult(
                task_id=problem["task_id"], condition="C",
                passed=True, rounds_to_pass=round_num,
                final_solution=solution, z3_ce_found_count=z3_ce_found_count,
                round_history=round_history
            )

        exec_fb = _get_exec_feedback(problem, solution)
        has_mypy_error, _, _, mypy_stdout = run_mypy(solution)
        mypy_fb = mypy_stdout if has_mypy_error else "No mypy errors detected."

        # Z3 counterexample (graceful: None on timeout/error)
        z3_ce = extract_z3_counterexample(
            spec_code, solution, problem["entry_point"], cfg.z3_timeout
        )
        if z3_ce is not None:
            z3_ce_found_count += 1
            logger.debug(f"{problem['task_id']} round {round_num}: Z3 CE found: {z3_ce['inputs']}")

        prompt = build_repair_prompt_c(problem, solution, exec_fb, mypy_fb, z3_ce)

        for attempt in range(3):
            try:
                response = client.chat.completions.create(
                    model=cfg.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=cfg.repair_temperature,
                    max_tokens=cfg.max_tokens,
                    seed=cfg.seed,
                    timeout=60,
                )
                solution = extract_code(response.choices[0].message.content)
                break
            except Exception as e:
                logger.warning(f"Repair attempt {attempt+1} failed: {e}")
                time.sleep(2 ** attempt)

        round_history.append(RoundResult(
            round_num=round_num, passed=False,
            exec_feedback=exec_fb, mypy_feedback=mypy_fb, z3_ce=z3_ce
        ))

    # Final check after last repair
    passed = evaluate_solution(problem["task_id"], solution, problem)
    return ProblemResult(
        task_id=problem["task_id"], condition="C",
        passed=passed, rounds_to_pass=cfg.k_repair_rounds + 1,
        final_solution=solution, z3_ce_found_count=z3_ce_found_count,
        round_history=round_history
    )
