---
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
phase: 3
date: 2026-08-26
author: yoon303@ust.ac.kr
---

# Logic: H-E1 — Type Error Prevalence in LLM-Generated Python Code

Applied: subprocess-tempfile pattern for static analysis integration

> **Note**: Tensor shapes not applicable — this is a CLI pipeline experiment with no neural components.

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing codebase to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## E3: Evaluation + mypy [Complexity: 10, Budget: 2 subtasks]

### API Signatures

```python
# pipeline.py

def evaluate_solution(task_id: str, code: str, problem: dict) -> bool:
    """Run EvalPlus test suite; return True=PASS."""
    ...

def run_mypy(code: str) -> tuple[bool, int]:
    """Run mypy on code string; return (has_error, error_count). Timeout -> (False, 0)."""
    ...
```

---

## L-E3-1: evaluate_solution() [Subtask 1/2]

### API Signature

```python
def evaluate_solution(task_id: str, code: str, problem: dict) -> bool:
    """Run EvalPlus test suite on code; return True if all tests pass."""
    ...
```

### EvalPlus Integration

EvalPlus does not expose a simple `check_correctness(task_id, solution)` callable in its public Python API. The correct approach is subprocess-based, calling the `evalplus.evaluate` CLI or using `evalplus.evaluate.check_correctness` from the internal module. Based on the evalplus codebase (as of 2024), the usable internal path is:

```python
from evalplus.evaluate import check_correctness
# signature: check_correctness(dataset, problem, solution, max_as_limit, fast_check, identifier, min_time_limit, gt_time_limit_factor)
# Returns: dict with "passed": bool, "result": str
```

If this import fails (API may change), fall back to subprocess.

### Pseudo-code

```
def evaluate_solution(task_id, code, problem):
    try:
        from evalplus.evaluate import check_correctness
        result = check_correctness(
            dataset="humaneval",         # or "mbpp" — derived from task_id prefix
            problem=problem,
            solution=code,
            max_as_limit=3*1024,
            fast_check=False,
            identifier=task_id,
            min_time_limit=1.0,
            gt_time_limit_factor=3.0,
        )
        return result["passed"]
    except ImportError:
        # fallback: subprocess evalplus CLI not practical for per-solution calls
        raise RuntimeError("evalplus.evaluate.check_correctness unavailable")
    except Exception as e:
        logging.warning(f"evaluate_solution {task_id} exception: {e}")
        return False  # conservative: treat exception as FAIL
```

**Dataset derivation** (for `dataset` param):
```python
dataset = "mbpp" if task_id.startswith("Mbpp") else "humaneval"
```

**Return contract**: `True` = all tests passed, `False` = any test failed or exception.

---

## L-E3-2: run_mypy() [Subtask 2/2]

### API Signature

```python
def run_mypy(code: str) -> tuple[bool, int]:
    """
    Write code to tempfile, run mypy, return (has_error, error_count).
    Timeout or FileNotFoundError -> (False, 0).
    """
    ...
```

### Pseudo-code

```
MYPY_FLAGS = ["--ignore-missing-imports", "--no-strict-optional"]
MYPY_TIMEOUT = 30

def run_mypy(code):
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
            f.write(code)
            tmp = f.name

        result = subprocess.run(
            ["mypy", *MYPY_FLAGS, tmp],
            capture_output=True,
            text=True,
            timeout=MYPY_TIMEOUT,
        )

        error_count = sum(1 for line in result.stdout.splitlines() if "error:" in line)
        has_error = result.returncode != 0
        return (has_error, error_count)

    except FileNotFoundError:
        # mypy not installed
        raise  # caller (run.py) catches this and exits with install instructions

    except subprocess.TimeoutExpired:
        logging.warning("mypy timeout on temp file")
        return (False, 0)  # conservative: no false positives

    finally:
        if tmp:
            pathlib.Path(tmp).unlink(missing_ok=True)
```

### Error Category Extraction (FR-6.4, optional)

```python
MYPY_CATEGORIES = {
    "name-error": r'\[name-defined\]',
    "type-error": r'\[arg-type\]|\[assignment\]|\[operator\]',
    "return-value": r'\[return-value\]',
    "attribute-error": r'\[attr-defined\]',
}

def extract_error_categories(mypy_stdout: str) -> dict[str, int]:
    """Parse mypy output for error category counts. Returns {category: count}."""
    import re
    counts = {cat: 0 for cat in MYPY_CATEGORIES}
    for line in mypy_stdout.splitlines():
        if "error:" not in line:
            continue
        for cat, pattern in MYPY_CATEGORIES.items():
            if re.search(pattern, line):
                counts[cat] += 1
    return counts
```

This function is called from `run_benchmark()` when FR-6.4 breakdown is needed. Add `error_categories: dict` to the per-solution result dict.

---

## Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E3-1 | evaluate_solution | EvalPlus correctness check via internal `check_correctness` API |
| L-E3-2 | run_mypy | subprocess mypy with tempfile, timeout, error count + category parsing |
