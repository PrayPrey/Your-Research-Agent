"""Data loading for HumanEval+ benchmark."""

import random
from typing import Any

from evalplus.data import get_human_eval_plus

from config import SEED, NUM_PROBLEMS


def load_problems() -> list[dict[str, Any]]:
    """Load HumanEval+ problems via evalplus."""
    problems = get_human_eval_plus()
    result = []
    for task_id, data in problems.items():
        result.append({
            "task_id": task_id,
            "prompt": data["prompt"],
            "canonical_solution": data["canonical_solution"],
            "entry_point": data["entry_point"],
            "test": data.get("test", ""),
            "base_input": data.get("base_input", []),
            "plus_input": data.get("plus_input", []),
        })
    return result[:NUM_PROBLEMS]


def get_solutions(problem: dict[str, Any], num_solutions: int = 5) -> list[dict[str, Any]]:
    """Generate solution variants for testing."""
    random.seed(SEED)
    solutions = []
    canonical = problem["canonical_solution"]
    solutions.append({
        "solution_id": 0,
        "code": canonical,
        "variant": "canonical",
    })
    buggy_variants = [
        ("off_by_one", _introduce_off_by_one),
        ("wrong_operator", _introduce_wrong_operator),
        ("missing_edge", _introduce_missing_edge),
        ("type_error", _introduce_type_error),
    ]
    for i, (variant_name, mutator) in enumerate(buggy_variants[:num_solutions - 1], start=1):
        mutated = mutator(canonical)
        solutions.append({
            "solution_id": i,
            "code": mutated,
            "variant": variant_name,
        })
    return solutions


def _introduce_off_by_one(code: str) -> str:
    """Introduce off-by-one error."""
    replacements = [
        ("< ", "<= "),
        ("> ", ">= "),
        ("range(0,", "range(1,"),
        ("- 1]", "]"),
    ]
    for old, new in replacements:
        if old in code:
            return code.replace(old, new, 1)
    return code + "\n# buggy: no mutation found"


def _introduce_wrong_operator(code: str) -> str:
    """Swap arithmetic operator."""
    replacements = [
        (" + ", " - "),
        (" * ", " / "),
        (" and ", " or "),
    ]
    for old, new in replacements:
        if old in code:
            return code.replace(old, new, 1)
    return code


def _introduce_missing_edge(code: str) -> str:
    """Remove an edge case check."""
    lines = code.split("\n")
    for i, line in enumerate(lines):
        if "if " in line and ("== 0" in line or "== []" in line or "is None" in line):
            lines[i] = "# " + line
            break
    return "\n".join(lines)


def _introduce_type_error(code: str) -> str:
    """Introduce type conversion error."""
    if "int(" in code:
        return code.replace("int(", "str(", 1)
    if "str(" in code:
        return code.replace("str(", "int(", 1)
    return code
