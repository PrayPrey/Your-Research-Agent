---
hypothesis_id: H-Z1
hypothesis_type: EXISTENCE
phase: 3
base_hypothesis: H-E1
date: 2026-08-26
author: yoon303@ust.ac.kr
---

# Logic: H-Z1 — Z3 Formal Counterexample Feedback for LLM Code Repair

Applied: CEGIS (Counterexample-Guided Inductive Synthesis) loop pattern — Z3 generates concrete failing witness, fed to LLM repair prompt (arXiv 2508.00419, ExVerus arXiv 2603.25810)

> **Note**: Tensor shapes not applicable — API-based inference experiment with no neural components.

---

## Codebase Analysis (Serena)

**Project Type**: incremental (base: H-E1)
**Status**: Patterns found from base code (Read + Bash tools used)
**Analyzed Path**: `docs/youra_research/h-e1/code/pipeline.py`
**Relevant Symbols Found**:

| Symbol | File | Reuse in H-Z1 |
|--------|------|----------------|
| `load_problems(benchmark)` | pipeline.py:52 | ✅ REUSED — loads HumanEval+ |
| `build_prompt(problem)` | pipeline.py:63 | ✅ REUSED — initial generation prompt |
| `extract_code(response_text)` | pipeline.py:73 | ✅ REUSED — strips markdown fences |
| `generate_solution(client, problem, seed)` | pipeline.py:82 | ✅ REUSED — initial gen (temp=0.8) |
| `evaluate_solution(task_id, code, problem)` | pipeline.py:103 | ✅ REUSED — EvalPlus correctness |
| `run_mypy(code)` | pipeline.py:149 | ✅ REUSED — mypy static analysis |
| `extract_error_categories(mypy_stdout)` | pipeline.py:137 | ✅ REUSED — error type parsing |
| `aggregate(results)` | pipeline.py:224 | PARTIAL — h-z1 has different aggregation |

**New modules for H-Z1**: `z3_utils.py`, `repair_loop.py`

---

## External Dependencies API

Verified from `h-e1/code/pipeline.py` (actual code):

```python
# ── h-e1/code/pipeline.py ──────────────────────────────────────────────────

def load_problems(benchmark: str) -> dict:
    """Load HumanEval+ or MBPP+ problems. benchmark: 'humaneval' | 'mbpp'"""
    # Returns: dict[task_id, problem_dict]

def build_prompt(problem: dict) -> str:
    """Build LLM completion prompt from problem['prompt']."""

def extract_code(response_text: str) -> str:
    """Strip markdown fences; return raw Python code string."""

def generate_solution(client: OpenAI, problem: dict, seed: int,
                      max_retries: int = 3) -> str:
    """Generate solution via GPT-4o-mini (temperature from config). Returns code str."""

def evaluate_solution(task_id: str, code: str, problem: dict) -> bool:
    """Run EvalPlus check_correctness. Returns True=PASS."""

def run_mypy(code: str) -> tuple:
    """Returns (has_error: bool, error_count: int, categories: dict, stdout: str).
    Timeout -> (False, 0, {}, ''). Callers must unpack all 4 values."""

def extract_error_categories(mypy_stdout: str) -> dict:
    """Returns {category: count} from mypy stdout."""
```

**Import pattern** (since h-z1 is not a package):
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "h-e1" / "code"))
from pipeline import (load_problems, build_prompt, extract_code,
                      generate_solution, evaluate_solution, run_mypy,
                      extract_error_categories)
```

---

## E3: Z3 Spec Generation & Validation [Complexity: 14, Budget: 2 subtasks]

### API Signatures

```python
# z3_utils.py

from dataclasses import dataclass
from typing import Optional
from openai import OpenAI

@dataclass
class Z3SpecResult:
    task_id: str
    spec_code: str           # Python code string using z3-solver
    valid: bool
    reject_reason: Optional[str]  # None if valid

def generate_z3_spec(problem: dict, client: OpenAI,
                     model: str = "gpt-4o-mini",
                     temperature: float = 0.0,
                     max_tokens: int = 1024) -> str:
    """
    Call LLM to generate Z3 spec code for problem.
    Returns: Python code string (z3-solver) encoding arithmetic constraints.
    """

def validate_z3_spec(spec_code: str, problem: dict,
                     timeout: int = 10) -> Z3SpecResult:
    """
    Validate spec against canonical solution.
    Reject if: spec says UNSAT on canonical solution (false negative).
    Accept if: spec runs without error and correctly identifies violations.
    Returns: Z3SpecResult with valid=True/False.
    """

def curate_arithmetic_subset(problems: dict) -> dict:
    """
    Filter HumanEval+ to arithmetic-heavy problems.
    Returns: filtered dict[task_id, problem] meeting all 5 criteria.
    """
```

---

## L-3-1: generate_z3_spec() [Subtask 1/2 for E3]

### Pseudo-code

```
SPEC_SYSTEM_PROMPT = """
You are a formal verification expert. Given a Python function specification,
generate a Z3 Python spec that:
1. Imports: from z3 import *
2. Creates Z3 Int/Bool/Real variables matching the function's input types
3. Creates a Solver() and adds arithmetic constraints encoding the EXPECTED output
4. The spec is a function: def check_spec(candidate_fn, *inputs) -> bool
   that returns True if candidate_fn(*inputs) satisfies the formal spec, else False
5. Use only z3 integer arithmetic (Int, Bool, If, And, Or, Not)
6. Do NOT use array constraints or bitvectors unless absolutely necessary
Return ONLY the Python code, no explanation.
"""

def generate_z3_spec(problem, client, model, temperature, max_tokens):
    user_msg = f"""Function specification:
{problem['prompt']}

Canonical solution (for reference):
{problem['canonical_solution']}

Entry point: {problem['entry_point']}

Generate the Z3 spec code."""

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
```

**Input**: `problem: dict` with keys `prompt`, `canonical_solution`, `entry_point`
**Output**: `str` — Python code using z3-solver

---

## L-3-2: validate_z3_spec() [Subtask 2/2 for E3]

### Pseudo-code

```
def validate_z3_spec(spec_code, problem, timeout=10):
    task_id = problem["task_id"]

    # Step 1: Compile spec_code safely
    try:
        spec_namespace = {}
        exec(spec_code, spec_namespace)
        check_spec_fn = spec_namespace.get("check_spec")
        if check_spec_fn is None:
            return Z3SpecResult(task_id, spec_code, False,
                                "spec code missing check_spec() function")
    except Exception as e:
        return Z3SpecResult(task_id, spec_code, False, f"spec compile error: {e}")

    # Step 2: Run canonical solution
    try:
        canon_namespace = {}
        exec(problem["canonical_solution"], canon_namespace)
        canon_fn = canon_namespace[problem["entry_point"]]
    except Exception as e:
        return Z3SpecResult(task_id, spec_code, False, f"canonical exec error: {e}")

    # Step 3: Get test inputs from EvalPlus (use first 3 base test inputs)
    # EvalPlus problem dict has 'base_input' or we construct simple inputs
    test_inputs = _get_test_inputs(problem)  # list of input tuples

    # Step 4: Validate spec does NOT false-negative on canonical solution
    for inputs in test_inputs[:3]:
        try:
            import signal
            # Use timeout via threading (cross-platform)
            result = _run_with_timeout(check_spec_fn, (canon_fn, *inputs), timeout)
            if result is False:
                # Spec rejects canonical solution = false negative → reject spec
                return Z3SpecResult(task_id, spec_code, False,
                                    f"false negative on canonical: inputs={inputs}")
        except Exception as e:
            return Z3SpecResult(task_id, spec_code, False, f"spec runtime error: {e}")

    return Z3SpecResult(task_id, spec_code, True, None)
```

**Key invariant**: A valid spec MUST return True (or UNSAT on violation) when called with canonical solution. False negatives = discard.

---

## E4: Z3 Counterexample Extraction [Complexity: 13, Budget: 2 subtasks]

### API Signatures

```python
# z3_utils.py (continued)

def extract_z3_counterexample(spec_code: str,
                               candidate_code: str,
                               entry_point: str,
                               timeout: int = 10) -> Optional[dict]:
    """
    Run Z3 to find concrete input where candidate violates spec.
    Returns: {input_var_name: value} if counterexample found, else None.
    None on: unsat (no violation), timeout, any Z3/exec error.
    """

def format_z3_ce_for_prompt(ce: dict, entry_point: str,
                              candidate_output: Optional[str] = None) -> str:
    """
    Format CE dict as human-readable string for LLM repair prompt.
    Returns: multi-line string describing the counterexample.
    """
```

---

## L-4-1: extract_z3_counterexample() [Subtask 1/2 for E4]

### Pseudo-code

```
def extract_z3_counterexample(spec_code, candidate_code, entry_point, timeout=10):
    """
    Strategy: exec spec_code to get check_spec(), exec candidate to get candidate_fn(),
    then call check_spec with Z3 symbolic inputs instead of concrete — but this requires
    spec_code to be written as a Z3 constraint builder, not a concrete checker.

    SIMPLIFIED APPROACH (PoC viable):
    Run candidate_fn on a set of concrete test inputs, find one where it fails,
    then use Z3 to encode WHY it fails (arithmetic violation).
    If that's too complex, fall back to: "Z3 CE: inputs from spec domain where
    candidate output != expected."
    """
    try:
        # Exec spec and candidate
        spec_ns = {}
        exec(spec_code, spec_ns)
        cand_ns = {}
        exec(candidate_code, cand_ns)
        candidate_fn = cand_ns.get(entry_point)
        if candidate_fn is None:
            return None

        # Try check_spec with small concrete input search (bounded)
        check_spec_fn = spec_ns.get("check_spec")
        if check_spec_fn is None:
            return None

        # Bounded concrete search: try integer inputs in [-10, 10]
        import itertools
        for inputs in _generate_test_inputs_bounded(spec_ns, bound=10, max_tries=50):
            result = _run_with_timeout(check_spec_fn, (candidate_fn, *inputs), timeout)
            if result is False:  # spec violated by candidate on these inputs
                try:
                    actual = candidate_fn(*inputs)
                except Exception as e:
                    actual = f"<error: {e}>"
                return {
                    "inputs": inputs,
                    "actual_output": actual,
                    "status": "counterexample_found"
                }

        return None  # No CE found in bounded search

    except Exception:
        return None  # Graceful degradation: no CE, Condition C falls back to B prompt
```

---

## L-4-2: format_z3_ce_for_prompt() [Subtask 2/2 for E4]

### Pseudo-code

```
def format_z3_ce_for_prompt(ce, entry_point, candidate_output=None):
    if ce is None or ce.get("status") != "counterexample_found":
        return ""

    inputs = ce["inputs"]
    actual = ce.get("actual_output", "unknown")

    lines = [
        "\nZ3 Formal Counterexample:",
        f"  Inputs: {entry_point}({', '.join(repr(x) for x in inputs)})",
        f"  Your output: {actual}",
        f"  Expected: correct output per formal spec",
        "  Fix your solution to handle this input correctly.",
    ]
    return "\n".join(lines)
```

**Output**: plain text appended to repair prompt in Condition C.

---

## E6: Condition C Repair Loop [Complexity: 11, Budget: 1 subtask]

### API Signatures

```python
# repair_loop.py

from dataclasses import dataclass, field
from typing import Optional
from openai import OpenAI

@dataclass
class RoundResult:
    round_num: int
    passed: bool
    exec_feedback: str
    mypy_feedback: str
    z3_ce: Optional[dict]   # None for Condition B or when no CE found

@dataclass
class ProblemResult:
    task_id: str
    condition: str           # "B" or "C"
    passed: bool
    rounds_to_pass: int      # k+1 if never passed
    final_solution: str
    z3_ce_found_count: int   # always 0 for Condition B
    round_history: list[RoundResult] = field(default_factory=list)

def repair_loop_b(problem: dict, initial_solution: str,
                  client: OpenAI, cfg) -> ProblemResult:
    """k=5 rounds: execute → mypy → build_repair_prompt_b → LLM repair."""

def repair_loop_c(problem: dict, initial_solution: str,
                  spec_code: str, client: OpenAI, cfg) -> ProblemResult:
    """k=5 rounds: execute → mypy → Z3 CE → build_repair_prompt_c → LLM repair.
    Z3 timeout/error: degrades gracefully to Condition B prompt for that round."""

def build_repair_prompt_b(problem: dict, solution: str,
                           exec_fb: str, mypy_fb: str) -> str:
    """Build repair prompt with execution + mypy feedback only."""

def build_repair_prompt_c(problem: dict, solution: str,
                           exec_fb: str, mypy_fb: str,
                           z3_ce: Optional[dict]) -> str:
    """Build repair prompt with execution + mypy + Z3 CE (if found)."""
```

---

## L-6-1: repair_loop_c() [Subtask 1/1 for E6]

### Pseudo-code

```
def repair_loop_c(problem, initial_solution, spec_code, client, cfg):
    solution = initial_solution
    z3_ce_found_count = 0
    round_history = []

    for round_num in range(1, cfg.k_repair_rounds + 1):
        # Step 1: Evaluate
        passed = evaluate_solution(problem["task_id"], solution, problem)
        if passed:
            return ProblemResult(
                task_id=problem["task_id"], condition="C",
                passed=True, rounds_to_pass=round_num,
                final_solution=solution, z3_ce_found_count=z3_ce_found_count,
                round_history=round_history
            )

        # Step 2: Collect execution feedback
        exec_fb = _get_exec_feedback(problem, solution)  # error traceback

        # Step 3: Collect mypy feedback (4-tuple: has_error, count, categories, stdout)
        has_mypy_error, _, _, mypy_stdout = run_mypy(solution)
        mypy_fb = mypy_stdout if has_mypy_error else "No mypy errors."

        # Step 4: Z3 counterexample (Condition C only)
        z3_ce = extract_z3_counterexample(
            spec_code, solution, problem["entry_point"], cfg.z3_timeout
        )
        if z3_ce is not None:
            z3_ce_found_count += 1

        # Step 5: Build Condition C repair prompt
        prompt = build_repair_prompt_c(problem, solution, exec_fb, mypy_fb, z3_ce)

        # Step 6: LLM repair (temperature=0.0 for deterministic repair)
        response = client.chat.completions.create(
            model=cfg.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=cfg.repair_temperature,
            max_tokens=cfg.max_tokens,
            seed=cfg.seed,
        )
        solution = extract_code(response.choices[0].message.content)

        round_history.append(RoundResult(
            round_num=round_num, passed=False,
            exec_feedback=exec_fb, mypy_feedback=mypy_fb, z3_ce=z3_ce
        ))

    # k rounds exhausted, not passed
    return ProblemResult(
        task_id=problem["task_id"], condition="C",
        passed=False, rounds_to_pass=cfg.k_repair_rounds + 1,
        final_solution=solution, z3_ce_found_count=z3_ce_found_count,
        round_history=round_history
    )
```

**Graceful degradation**: `extract_z3_counterexample` returns `None` on timeout/error → `build_repair_prompt_c` with `z3_ce=None` produces identical output to Condition B prompt for that round. No special error handling needed.

---

## curate_arithmetic_subset() [E2 helper, no subtask]

### Pseudo-code

```
CURATION_CRITERIA = {
    "pure_numeric_inputs": lambda p: _all_inputs_numeric(p),
    "numeric_output": lambda p: _output_is_numeric(p),
    "no_string_primary": lambda p: not _string_is_primary(p),
    "pure_function": lambda p: not _has_side_effects(p),
    "arithmetic_keywords": lambda p: _has_arithmetic_keywords(p),
}

ARITHMETIC_KEYWORDS = [
    "sum", "product", "factorial", "fibonacci", "gcd", "lcm",
    "prime", "digit", "mod", "divisor", "arithmetic", "sequence",
    "multiply", "divide", "power", "sqrt", "median", "average"
]

def curate_arithmetic_subset(problems):
    accepted = {}
    rejected = {}

    for task_id, problem in problems.items():
        prompt_lower = problem["prompt"].lower()

        # Keyword check: fast pre-filter
        has_keyword = any(kw in prompt_lower for kw in ARITHMETIC_KEYWORDS)
        if not has_keyword:
            rejected[task_id] = "no arithmetic keywords"
            continue

        # String-primary check: reject if primarily string manipulation
        string_ops = ["split", "join", "strip", "replace", "upper", "lower",
                      "startswith", "endswith", "format", "encode"]
        string_heavy = sum(1 for op in string_ops if op in prompt_lower)
        if string_heavy >= 3:
            rejected[task_id] = f"string-heavy ({string_heavy} string ops)"
            continue

        # I/O side effect check: reject if file/print/global
        side_effects = ["open(", "print(", "global ", "import os", "import sys"]
        canon = problem.get("canonical_solution", "")
        if any(se in canon for se in side_effects):
            rejected[task_id] = "has side effects"
            continue

        accepted[task_id] = problem
        logging.info(f"Accepted {task_id}: arithmetic problem")

    logging.info(f"Curation: {len(accepted)} accepted, {len(rejected)} rejected")
    if len(accepted) < 30:
        logging.warning(f"Only {len(accepted)} curated problems — below minimum 30")
    return accepted
```

---

## Subtask Summary

| ID | Subtask | Parent Epic | Description |
|----|---------|-------------|-------------|
| L-3-1 | generate_z3_spec | E3 | LLM prompt → Z3 spec code string |
| L-3-2 | validate_z3_spec | E3 | Exec spec vs canonical; reject false negatives |
| L-4-1 | extract_z3_counterexample | E4 | Bounded concrete search for CE; graceful None on failure |
| L-4-2 | format_z3_ce_for_prompt | E4 | Format CE dict as repair prompt text |
| L-6-1 | repair_loop_c | E6 | k=5 repair rounds with Z3 CE; degrades to B on Z3 failure |

**Total subtasks: 5 / 5 budget used**
