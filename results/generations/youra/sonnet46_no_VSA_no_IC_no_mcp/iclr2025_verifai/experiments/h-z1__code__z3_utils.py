"""Z3 spec generation, validation, and counterexample extraction for H-Z1."""

import concurrent.futures
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from openai import OpenAI

logger = logging.getLogger(__name__)

# Arithmetic keywords for curation
ARITHMETIC_KEYWORDS = [
    "sum", "product", "factorial", "fibonacci", "gcd", "lcm",
    "prime", "digit", "mod", "divisor", "arithmetic", "sequence",
    "multiply", "divide", "power", "sqrt", "median", "average",
    "count", "maximum", "minimum", "greatest", "smallest", "largest",
    "number", "integer", "numeric", "calculate", "compute", "total",
]

SPEC_SYSTEM_PROMPT = """You are a formal verification expert. Given a Python function specification, generate a Z3 Python spec.

Your spec MUST define a function: def check_spec(candidate_fn, *inputs) -> bool
This function:
1. Calls candidate_fn(*inputs) to get the actual output
2. Checks if the output satisfies the formal specification
3. Returns True if correct, False if incorrect

Rules:
- Import from z3 if needed, but prefer concrete checking over symbolic Z3
- Keep it simple: just check candidate_fn(*inputs) == expected_output(*inputs)
- Handle exceptions: return False if candidate_fn raises
- The check_spec function must be self-contained

Return ONLY the Python code, no explanation."""


@dataclass
class Z3SpecResult:
    task_id: str
    spec_code: str
    valid: bool
    reject_reason: Optional[str]


def curate_arithmetic_subset(problems: dict) -> dict:
    """Filter HumanEval+ to arithmetic-heavy problems per 5-criteria filter."""
    accepted = {}
    rejected_counts = {"no_keyword": 0, "string_heavy": 0, "side_effects": 0}

    string_ops = ["split", "join", "strip", "replace", "upper", "lower",
                  "startswith", "endswith", "format", "encode", "char", "ord", "chr"]

    side_effects = ["open(", "print(", "global ", "import os", "import sys"]

    for task_id, problem in problems.items():
        prompt_lower = problem["prompt"].lower()
        canon = problem.get("canonical_solution", "")

        # Keyword check
        has_keyword = any(kw in prompt_lower for kw in ARITHMETIC_KEYWORDS)
        if not has_keyword:
            rejected_counts["no_keyword"] += 1
            continue

        # String-primary check
        string_heavy = sum(1 for op in string_ops if op in prompt_lower)
        if string_heavy >= 3:
            rejected_counts["string_heavy"] += 1
            continue

        # Side effect check
        if any(se in canon for se in side_effects):
            rejected_counts["side_effects"] += 1
            continue

        accepted[task_id] = problem
        logger.debug(f"Accepted {task_id}: arithmetic problem")

    logger.info(f"Curation: {len(accepted)} accepted, rejected={rejected_counts}")
    if len(accepted) < 30:
        logger.warning(f"Only {len(accepted)} curated problems — below minimum 30")
    return accepted


def generate_z3_spec(problem: dict, client: OpenAI,
                     model: str = "gpt-4o-mini",
                     temperature: float = 0.0,
                     max_tokens: int = 1024) -> str:
    """Call LLM to generate Z3 spec code for problem."""
    # Import extract_code from h-e1 pipeline
    from pipeline import extract_code

    # canonical_solution is just the body; build complete function for reference
    full_canonical = problem["prompt"] + problem["canonical_solution"]

    user_msg = f"""Function specification:
{problem['prompt']}

Complete canonical solution (for reference):
```python
{full_canonical}
```

Entry point: {problem['entry_point']}

Generate the check_spec(candidate_fn, *inputs) function that verifies a candidate solution against this specification.
The check_spec function should call candidate_fn(*inputs) and compare the result against the expected output."""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SPEC_SYSTEM_PROMPT},
            {"role": "user", "content": user_msg}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    spec_code = extract_code(response.choices[0].message.content)
    return spec_code


def _run_with_timeout(fn, args, timeout: int):
    """Run fn(*args) with timeout; raises TimeoutError if exceeded."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(fn, *args)
        return future.result(timeout=timeout)


def _get_test_inputs(problem: dict) -> list:
    """Extract test inputs from problem dict for validation."""
    # Try EvalPlus base_input
    base_input = problem.get("base_input", [])
    if base_input:
        return base_input[:3]

    # Fallback: try simple integer inputs based on entry_point
    entry = problem.get("entry_point", "")
    prompt = problem.get("prompt", "")

    # Count parameters from prompt signature
    import re
    sig_match = re.search(r"def\s+" + re.escape(entry) + r"\s*\(([^)]*)\)", prompt)
    if sig_match:
        params = [p.strip() for p in sig_match.group(1).split(",") if p.strip()]
        n_params = len(params)
        if n_params == 0:
            return [()]
        # Return small concrete inputs
        return [
            tuple([1] * n_params),
            tuple([2] * n_params),
            tuple([0] * n_params),
        ]

    return [(1,), (2,), (3,)]


def validate_z3_spec(spec_code: str, problem: dict, timeout: int = 10) -> Z3SpecResult:
    """Validate spec against canonical solution. Reject if false negative on canonical."""
    task_id = problem["task_id"]

    # Step 1: Compile spec_code
    try:
        spec_namespace = {}
        exec(compile(spec_code, "<spec>", "exec"), spec_namespace)
        check_spec_fn = spec_namespace.get("check_spec")
        if check_spec_fn is None:
            return Z3SpecResult(task_id, spec_code, False,
                                "spec code missing check_spec() function")
    except Exception as e:
        return Z3SpecResult(task_id, spec_code, False, f"spec compile error: {e}")

    # Step 2: Run canonical solution
    # canonical_solution is just the body (indented); prepend prompt to get full function
    try:
        full_canon = problem["prompt"] + problem["canonical_solution"]
        canon_namespace = {}
        exec(compile(full_canon, "<canon>", "exec"), canon_namespace)
        canon_fn = canon_namespace.get(problem["entry_point"])
        if canon_fn is None:
            return Z3SpecResult(task_id, spec_code, False,
                                f"canonical solution missing {problem['entry_point']}")
    except Exception as e:
        return Z3SpecResult(task_id, spec_code, False, f"canonical exec error: {e}")

    # Step 3: Get test inputs
    test_inputs = _get_test_inputs(problem)

    # Step 4: Validate spec does NOT false-negative on canonical solution
    for inputs in test_inputs[:3]:
        try:
            if not isinstance(inputs, (tuple, list)):
                inputs = (inputs,)
            result = _run_with_timeout(check_spec_fn, (canon_fn, *inputs), timeout)
            if result is False:
                return Z3SpecResult(task_id, spec_code, False,
                                    f"false negative on canonical: inputs={inputs}")
        except concurrent.futures.TimeoutError:
            return Z3SpecResult(task_id, spec_code, False, "spec timeout on canonical")
        except Exception as e:
            return Z3SpecResult(task_id, spec_code, False, f"spec runtime error: {e}")

    return Z3SpecResult(task_id, spec_code, True, None)


def _run_check_once(spec_code: str, candidate_code: str, entry_point: str, vals: tuple):
    """Run check_spec once in a fresh namespace. Called in subprocess-safe way."""
    spec_ns = {}
    exec(compile(spec_code, "<spec>", "exec"), spec_ns)
    check_spec_fn = spec_ns.get("check_spec")
    if check_spec_fn is None:
        return None

    cand_ns = {}
    exec(compile(candidate_code, "<cand>", "exec"), cand_ns)
    candidate_fn = cand_ns.get(entry_point)
    if candidate_fn is None:
        return None

    result = check_spec_fn(candidate_fn, *vals)
    if result is False:
        try:
            actual = candidate_fn(*vals)
        except Exception as e:
            actual = f"<error: {e}>"
        return {"inputs": vals, "actual_output": actual, "status": "counterexample_found"}
    return None  # no CE on this input


def extract_z3_counterexample(spec_code: str,
                               candidate_code: str,
                               entry_point: str,
                               timeout: int = 10) -> Optional[dict]:
    """Find concrete input where candidate violates spec via bounded search.
    Hard per-check timeout of 0.5s to prevent hangs."""
    import itertools

    # Use small range to keep search fast
    SEARCH_RANGE = range(-3, 8)
    MAX_TRIES = 30  # total check limit across all arities

    tries = 0
    for n_args in [1, 2, 3]:
        for vals in itertools.product(SEARCH_RANGE, repeat=n_args):
            if tries >= MAX_TRIES:
                return None
            tries += 1
            try:
                ex = concurrent.futures.ThreadPoolExecutor(max_workers=1)
                try:
                    future = ex.submit(_run_check_once, spec_code, candidate_code, entry_point, vals)
                    result = future.result(timeout=0.5)
                    if result is not None:
                        ex.shutdown(wait=False)
                        return result
                except (concurrent.futures.TimeoutError, Exception):
                    pass
                finally:
                    ex.shutdown(wait=False)
            except Exception:
                pass

    return None


def format_z3_ce_for_prompt(ce: Optional[dict], entry_point: str,
                              candidate_output: Optional[str] = None) -> str:
    """Format CE dict as human-readable string for LLM repair prompt."""
    if ce is None or ce.get("status") != "counterexample_found":
        return ""

    inputs = ce["inputs"]
    actual = ce.get("actual_output", "unknown")

    lines = [
        "\nZ3 Formal Counterexample:",
        f"  Input: {entry_point}({', '.join(repr(x) for x in inputs)})",
        f"  Your output: {actual}",
        f"  Expected: correct output per formal specification",
        "  Fix your solution to handle this input correctly.",
    ]
    return "\n".join(lines)
