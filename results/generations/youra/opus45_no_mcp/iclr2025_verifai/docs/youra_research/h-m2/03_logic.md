# Logic: H-M2 (Execution Detects Behavioral Errors)

**Type:** MECHANISM
**Applied:** Extend-and-filter pattern (reuse H-M1 pipeline, add static-clean filter)
**Applied:** Filter-then-categorize pattern (identify static-clean, execute tests, categorize failures)
**Applied:** Parallelized-pipeline pattern (ProcessPoolExecutor, gate evaluation, figure generation)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M1)
**Status:** API signatures verified from actual H-M1 code (direct file read; Serena MCP unavailable this session)
**Analyzed Path:** `h-m1/code/`
**Relevant Symbols:**
- `run_static_analysis(code: str) -> set` in `static_analysis.py` — returns **prefixed strings** `"pylint:E0602"` / `"mypy:incompatible..."`. H-M2 checks `len(result) == 0` for static-clean.
- `run_execution_tests(problem_id: str, code: str, problem: dict, timeout: int = 5) -> Set[str]` in `exec_analysis.py` — returns tags like `"exec:wrong_answer"`, `"exec:runtime_error"`, `"exec:timeout"`. Non-empty set = test-failing problem.
- `load_problems() -> dict` and `get_benchmark(problem_id: str) -> str` in `generate.py`.
- `run_analysis.py::process_one(args)` / `main()` — orchestration shape (ProcessPoolExecutor, `min(8, os.cpu_count())` workers, `as_completed`, results dict, save JSON, `evaluate_gate`, `generate_all_figures`).
- `config.py::ExperimentConfig` — simple `@dataclass` singleton `CONFIG`.

**Key Insight:** H-M2 filters to `len(static_errors) == 0` problems, then checks `len(exec_errors) > 0` for behavioral failures.

---

## External Dependencies API (From Actual H-M1 Code)

```python
# From: h-m1/code/static_analysis.py (ACTUAL CODE)
def run_static_analysis(code: str) -> set:
    """Returns union of {'pylint:<msg-id>', ...} | {'mypy:<truncated msg>', ...}."""
    ...

# From: h-m1/code/exec_analysis.py (ACTUAL CODE)
def run_execution_tests(problem_id: str, code: str, problem: dict, timeout: int = 5) -> Set[str]:
    """Returns {'exec:wrong_answer'|'exec:runtime_error'|'exec:timeout', ...}. Empty = passing."""
    ...

# From: h-m1/code/generate.py (ACTUAL CODE)
def load_problems() -> dict: ...          # 563 problems, {pid: {..., "benchmark": "humaneval"|"mbpp"}}
def get_benchmark(problem_id: str) -> str: ...
```

**Verified from:** `h-m1/code/` (actual implementation). H-M2 copies these 3 files unchanged (NFR-03).

---

## A-1/A-2: Copy base infra + config.py [Complexity: 3+3, Budget: 6]

**Applied:** Standard file copy, dataclass config pattern

Copy `static_analysis.py`, `exec_analysis.py`, `generate.py` from `h-m1/code/` into `h-m2/code/` unchanged.

```python
# h-m2/code/config.py
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    seed: int = 42
    pylint_timeout_sec: int = 30
    mypy_timeout_sec: int = 30
    exec_timeout_sec: int = 5
    behavioral_gate: float = 0.40
    output_dir: str = "outputs/"
    figures_dir: str = "../figures/"
    results_file: str = "outputs/results.json"

CONFIG = ExperimentConfig()
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Copy files | Copy 3 H-M1 modules unchanged |
| L-2-1 | config.py | New dataclass w/ behavioral_gate=0.40 |

---

## A-3: is_static_clean [Complexity: 2, Budget: 2]

**Applied:** Simple predicate function pattern

### API Signature

```python
# h-m2/code/behavioral_errors.py
def is_static_clean(static_errors: set) -> bool:
    """Return True if len(static_errors) == 0."""
    return len(static_errors) == 0
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | is_static_clean | Trivial predicate |

---

## A-4/A-5: behavioral_errors.py [Complexity: 4+6, Budget: 10]

**Applied:** Category lookup + string matching pattern

### API Signatures

```python
# h-m2/code/behavioral_errors.py
from typing import Set

BEHAVIORAL_CATEGORIES: dict = {
    "wrong_output": ["AssertionError", "Expected", "expected", "!=", "assert"],
    "runtime_exception": ["TypeError", "ValueError", "IndexError", "KeyError", 
                          "AttributeError", "ZeroDivisionError", "RuntimeError"],
    "timeout": ["timeout", "Timeout", "TimeoutError", "time limit"],
    "edge_case": []  # default category
}

def categorize_test_failure(exec_errors: Set[str]) -> str:
    """Return category: 'wrong_output', 'runtime_exception', 'timeout', 'edge_case'.
    Checks exec error set for substrings matching each category."""
    ...

def is_static_clean(static_errors: set) -> bool:
    """Return True if len(static_errors) == 0."""
    ...
```

### Pseudo-code

```
categorize_test_failure(exec_errors):
    error_str = " ".join(exec_errors)
    
    for category in ["wrong_output", "runtime_exception", "timeout"]:
        for keyword in BEHAVIORAL_CATEGORIES[category]:
            if keyword in error_str:
                return category
    
    return "edge_case"  # default
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | BEHAVIORAL_CATEGORIES | Dict mapping category -> keywords |
| L-5-1 | categorize_test_failure | Parse exec error set into category |

---

## A-6/A-7/A-8: behavioral_coverage.py [Complexity: 8+5+5, Budget: 18]

**Applied:** Filter-reduce aggregation pattern

### API Signatures

```python
# h-m2/code/behavioral_coverage.py
from typing import List, Dict

def compute_behavioral_rate(per_problem_results: List[dict]) -> dict:
    """Filter to static-clean problems (zero static errors).
    Count how many fail tests.
    Returns {behavioral_rate: float, static_clean_count: int, behavioral_failures: int}."""
    ...

def failure_category_distribution(per_problem_results: List[dict]) -> Dict[str, int]:
    """Count failures by category (wrong_output, exception, timeout, edge_case)
    among static-clean problems only."""
    ...

def per_benchmark_breakdown(per_problem_results: List[dict]) -> dict:
    """Returns {'humaneval_plus': {behavioral_rate, static_clean, failures},
    'mbpp_plus': {...}} split by benchmark."""
    ...
```

### Data Flow

| Variable | Type | Note |
|----------|------|------|
| per_problem_results | `list[dict]` | Each dict has keys: problem_id, benchmark, static_errors, exec_errors, is_static_clean, has_behavioral_failure, failure_category |

### Pseudo-code

```
compute_behavioral_rate(results):
    static_clean = [r for r in results if r["is_static_clean"]]
    failures = [r for r in static_clean if r["has_behavioral_failure"]]
    rate = len(failures) / len(static_clean) if static_clean else 0.0
    return {
        "behavioral_rate": rate,
        "static_clean_count": len(static_clean),
        "behavioral_failures": len(failures)
    }

failure_category_distribution(results):
    counts = {"wrong_output": 0, "runtime_exception": 0, "timeout": 0, "edge_case": 0}
    static_clean = [r for r in results if r["is_static_clean"]]
    for r in static_clean:
        if r["has_behavioral_failure"]:
            counts[r["failure_category"]] += 1
    return counts

per_benchmark_breakdown(results):
    humaneval = [r for r in results if "humaneval" in r["benchmark"].lower()]
    mbpp = [r for r in results if "mbpp" in r["benchmark"].lower()]
    return {
        "humaneval_plus": compute_behavioral_rate(humaneval),
        "mbpp_plus": compute_behavioral_rate(mbpp)
    }
```

### Subtasks [3/3 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | compute_behavioral_rate | Filter static-clean, count failures |
| L-7-1 | failure_category_distribution | Count by category |
| L-8-1 | per_benchmark_breakdown | Split HumanEval+ vs MBPP+ |

---

## A-9: evaluate.py [Complexity: 3, Budget: 3]

**Applied:** Gate threshold check pattern

### API Signature

```python
# h-m2/code/evaluate.py
def evaluate_gate(behavioral_rate: float, threshold: float = 0.40) -> dict:
    """Returns {passed: bool, metric: float, threshold: float, message: str}."""
    passed = behavioral_rate > threshold
    return {
        "passed": passed,
        "metric": behavioral_rate,
        "threshold": threshold,
        "message": f"Behavioral rate {behavioral_rate:.1%} {'>' if passed else '<='} {threshold:.0%}"
    }
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | evaluate_gate | Gate check against 0.40 threshold |

---

## A-10: run_analysis.py [Complexity: 12, Budget: 12]

**Applied:** ProcessPoolExecutor orchestration pattern (from H-M1)

### API Signatures

```python
# h-m2/code/run_analysis.py
from concurrent.futures import ProcessPoolExecutor, as_completed

def process_one(args: tuple) -> dict:
    """(pid, problem) -> {problem_id, benchmark, static_errors, exec_errors,
    is_static_clean, has_behavioral_failure, failure_category}."""
    ...

def main() -> dict:
    """Load 563 problems, ProcessPoolExecutor(8), compute behavioral_rate,
    evaluate_gate, save results.json, generate figures."""
    ...
```

### Pseudo-code

```
process_one((pid, problem)):
    code = load_or_generate_code(pid, problem)
    static_errors = run_static_analysis(code)
    exec_errors = run_execution_tests(pid, code, problem)
    
    is_clean = is_static_clean(static_errors)
    has_failure = len(exec_errors) > 0 if is_clean else False
    category = categorize_test_failure(exec_errors) if has_failure else None
    
    return {
        "problem_id": pid,
        "benchmark": get_benchmark(pid),
        "static_errors": list(static_errors),
        "exec_errors": list(exec_errors),
        "is_static_clean": is_clean,
        "has_behavioral_failure": has_failure,
        "failure_category": category
    }

main():
    problems = load_problems()  # 563
    
    with ProcessPoolExecutor(max_workers=min(8, os.cpu_count())) as executor:
        futures = {executor.submit(process_one, (pid, p)): pid for pid, p in problems.items()}
        results = []
        for future in as_completed(futures):
            results.append(future.result())
    
    metrics = compute_behavioral_rate(results)
    gate_result = evaluate_gate(metrics["behavioral_rate"])
    
    output = {
        "metrics": metrics,
        "gate_result": gate_result,
        "category_distribution": failure_category_distribution(results),
        "per_benchmark": per_benchmark_breakdown(results),
        "per_problem": results
    }
    
    save_json(CONFIG.results_file, output)
    generate_all_figures(output, CONFIG.figures_dir)
    
    return output
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-10-1 | process_one | Per-problem worker with static-clean check |
| L-10-2 | main | Orchestration with ProcessPoolExecutor |

---

## A-11: visualize.py [Complexity: 7, Budget: 7]

**Applied:** Matplotlib bar/pie chart pattern (from H-M1)

### API Signature

```python
# h-m2/code/visualize.py
def generate_all_figures(results: dict, figures_dir: str) -> None:
    """Generate 3 figures:
    1. Bar: behavioral_rate vs 0.40 threshold (REQUIRED)
    2. Pie: failure category distribution
    3. Bar: per-benchmark (HumanEval+ vs MBPP+) behavioral rates"""
    ...
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-11-1 | generate_all_figures | 3 matplotlib figures |

---

## A-12: End-to-end run [Complexity: 6, Budget: 6]

**Applied:** Integration test pattern

### Pseudo-code

```
run_experiment():
    results = main()
    
    # Validate gate
    assert "gate_result" in results
    gate = results["gate_result"]
    
    print(f"Behavioral Rate: {gate['metric']:.1%}")
    print(f"Gate Passed: {gate['passed']}")
    print(f"Message: {gate['message']}")
    
    return results
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-12-1 | Integration | Execute full pipeline, validate outputs |

---

## Subtask Budget Summary

| Epic | Description | Complexity | Subtasks |
|------|-------------|------------|----------|
| A-1/A-2 | Copy infra + config | 6 | 2 |
| A-3 | is_static_clean | 2 | 1 |
| A-4/A-5 | behavioral_errors | 10 | 2 |
| A-6/A-7/A-8 | behavioral_coverage | 18 | 3 |
| A-9 | evaluate gate | 3 | 1 |
| A-10 | run_analysis pipeline | 12 | 2 |
| A-11 | visualize | 7 | 1 |
| A-12 | End-to-end | 6 | 1 |
| **Total** | | **64** | **13** |

**Budget Check:** 12 Epics + 13 subtasks = 25 total tasks < 30 (FULL tier) ✅
