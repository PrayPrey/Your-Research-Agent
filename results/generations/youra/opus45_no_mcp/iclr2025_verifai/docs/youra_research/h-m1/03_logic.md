# Logic: H-M1 (Static Analysis Detects Structural Errors)

**Type:** MECHANISM
**Applied:** Extend-and-categorize pattern (reuse H-E1 pipeline, add categorization layer)
**Applied:** Parallelized-pipeline pattern (ProcessPoolExecutor, gate evaluation, figure generation)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-E1)
**Status:** API signatures verified from actual H-E1 code (direct file read; Serena MCP unavailable this session)
**Analyzed Path:** `h-e1/code/`
**Relevant Symbols:**
- `run_static_analysis(code: str) -> set` in `static_analysis.py` — returns **prefixed strings** `"pylint:E0602"` / `"mypy:incompatible type..."`, NOT raw pylint JSON dicts or a mypy text blob as the Phase 2C brief's pseudo-code assumed. **H-M1's `categorize_static_errors` must parse this prefixed-string set, not `(pylint_errors, mypy_errors)` tuples.**
- `run_execution_tests(problem_id: str, code: str, problem: dict, timeout: int = 5) -> Set[str]` in `exec_analysis.py` — returns tags like `"exec:wrong_answer"`, `"exec:runtime_error"`, `"exec:timeout"`. Non-empty set = test-failing problem.
- `generate_code(problem: dict, problem_id: str, model_name: str = None, seed: int = 42) -> str` in `generate.py`.
- `load_problems() -> dict` and `get_benchmark(problem_id: str) -> str` in `generate.py`.
- `run_analysis.py::process_one(args)` / `main()` — orchestration shape (ProcessPoolExecutor, `min(8, os.cpu_count())` workers, `as_completed`, results dict, save JSON, `evaluate_gate`, `generate_all_figures`).
- `config.py::ExperimentConfig` — simple `@dataclass` singleton `CONFIG`.

**⚠️ Deviation from 02c_experiment_brief.md pseudo-code:** brief's `categorize_static_errors(pylint_errors, mypy_errors)` signature is WRONG for actual H-E1 API. Correct signature below takes a single `static_errors: set` of prefixed strings.

---

## External Dependencies API (From Actual H-E1 Code)

```python
# From: h-e1/code/static_analysis.py (ACTUAL CODE)
def run_static_analysis(code: str) -> set:
    """Returns union of {'pylint:<msg-id>', ...} | {'mypy:<truncated msg>', ...}."""
    ...

# From: h-e1/code/exec_analysis.py (ACTUAL CODE)
def run_execution_tests(problem_id: str, code: str, problem: dict, timeout: int = 5) -> Set[str]:
    """Returns {'exec:wrong_answer'|'exec:runtime_error'|'exec:timeout', ...}. Empty = passing."""
    ...

# From: h-e1/code/generate.py (ACTUAL CODE)
def load_problems() -> dict: ...          # 563 problems, {pid: {..., "benchmark": "humaneval"|"mbpp"}}
def get_benchmark(problem_id: str) -> str: ...
def generate_code(problem: dict, problem_id: str, model_name: str = None, seed: int = 42) -> str: ...
```

**Verified from:** `h-e1/code/` (actual implementation). H-M1 copies these 3 files unchanged (NFR-03).

---

## A-1/A-2: Copy base infra + config.py [Complexity: 3+3, Budget: 6]

**Applied:** Standard file copy, dataclass config pattern

Copy `static_analysis.py`, `exec_analysis.py`, `generate.py` from `h-e1/code/` into `h-m1/code/` unchanged.

```python
# h-m1/code/config.py
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    seed: int = 42
    pylint_timeout_sec: int = 30
    mypy_timeout_sec: int = 30
    exec_timeout_sec: int = 5
    structural_gate: float = 0.60
    output_dir: str = "outputs/"
    figures_dir: str = "../figures/"
    results_file: str = "outputs/results.json"

CONFIG = ExperimentConfig()
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Copy files | Copy 3 H-E1 modules unchanged |
| L-2-1 | config.py | New dataclass w/ structural_gate=0.60 |

---

## A-3/A-4: structural_errors.py [Complexity: 4+8, Budget: 12]

**Applied:** Dict lookup + string parsing (no KB pattern needed — pure Python)

### API Signatures

```python
# h-m1/code/structural_errors.py
from typing import Set, List, Tuple

STRUCTURAL_ERROR_CODES: dict = {
    # pylint codes -> category
    "E0001": "syntax-error",
    "E0102": "function-redefined",
    "E0602": "undefined-variable",
    "E0603": "undefined-all-variable",
    "E1101": "no-member",
    "E1120": "no-value-for-parameter",
    "E1121": "too-many-function-args",
    "W0612": "unused-variable",
    "W0611": "unused-import",
    # mypy substring keys -> category
    "incompatible": "type-mismatch",
    "arg-type": "argument-type-error",
    "return": "return-type-error",
    "name": "undefined-name",
}

def categorize_static_errors(static_errors: Set[str]) -> Tuple[List[Tuple[str, str]], List[str]]:
    """Split run_static_analysis() output into (structural, other).
    structural: list[(code_or_key, category)]. other: list[raw error string]."""
    ...

def has_structural_error(static_errors: Set[str]) -> bool:
    """True if categorize_static_errors returns any structural entries."""
    ...
```

### Pseudo-code

```
categorize_static_errors(static_errors):
  structural, other = [], []
  for err in static_errors:
    if err.startswith("pylint:"):
      code = err.split("pylint:", 1)[1]
      if code in STRUCTURAL_ERROR_CODES:
        structural.append((code, STRUCTURAL_ERROR_CODES[code]))
      else:
        other.append(err)
    elif err.startswith("mypy:"):
      msg = err.split("mypy:", 1)[1].lower()
      matched = False
      for key in ("incompatible", "arg-type", "return", "name"):
        if key in msg:
          structural.append((key, STRUCTURAL_ERROR_CODES[key]))
          matched = True
          break
      if not matched:
        other.append(err)
    else:
      other.append(err)
  return structural, other

has_structural_error(static_errors):
  structural, _ = categorize_static_errors(static_errors)
  return len(structural) > 0
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | STRUCTURAL_ERROR_CODES | Dict per FR-03 |
| L-4-1 | categorize/has_structural | Parse prefixed-string set (matches real API, not brief's tuple signature) |

---

## A-5: coverage.py [Complexity: 9, Budget: 9]

**Applied:** Filter-reduce aggregation pattern

### API Signatures

```python
# h-m1/code/coverage.py
from typing import List, Dict

def compute_structural_coverage(per_problem_results: List[dict]) -> dict:
    """Filter to items where exec_errors non-empty (test-failing).
    Returns {structural_coverage: float, n_failing: int, n_structural: int}."""
    ...

def error_category_distribution(per_problem_results: List[dict]) -> Dict[str, int]:
    """Count occurrences per structural category name across all problems."""
    ...

def per_benchmark_breakdown(per_problem_results: List[dict]) -> dict:
    """Returns {'humaneval': {structural_coverage, n_failing, n_structural},
    'mbpp': {...}} using same filter as compute_structural_coverage, split by benchmark."""
    ...
```

### Tensor Shapes (N/A — no tensors, dict-based aggregation)

| Variable | Type | Note |
|----------|------|------|
| per_problem_results | `list[dict]` | Each dict has keys: problem_id, benchmark, static_errors, exec_errors, structural, other, has_structural |

### Pseudo-code

```
compute_structural_coverage(results):
  failing = [r for r in results if len(r["exec_errors"]) > 0]
  structural_count = sum(1 for r in failing if r["has_structural"])
  coverage = structural_count / len(failing) if failing else 0.0
  return {"structural_coverage": coverage, "n_failing": len(failing), "n_structural": structural_count}

error_category_distribution(results):
  counts = {}
  for r in results:
    for code, category in r["structural"]:
      counts[category] = counts.get(category, 0) + 1
  return counts

per_benchmark_breakdown(results):
  out = {}
  for bench in ("humaneval", "mbpp"):
    subset = [r for r in results if r["benchmark"] == bench]
    out[bench] = compute_structural_coverage(subset)
  return out
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | compute_structural_coverage | Filter test-failing, ratio calc |
| L-5-2 | error_category_distribution | Count per category |
| L-5-3 | per_benchmark_breakdown | Split by humaneval/mbpp |
| L-5-4 | Edge case: empty failing set | Return 0.0 not ZeroDivisionError |

---

## A-6: evaluate.py [Complexity: 3, Budget: 3]

**Applied:** Standard PyTorch-free gate check (reuses H-E1's evaluate_gate shape)

```python
# h-m1/code/evaluate.py
def evaluate_gate(structural_coverage: float, threshold: float = 0.60) -> dict:
    """Returns {passed, metric, threshold, message}."""
    return {
        "passed": structural_coverage > threshold,
        "metric": structural_coverage,
        "threshold": threshold,
        "message": f"Structural coverage: {structural_coverage:.1%} (threshold: >{threshold:.0%})",
    }
```

### Subtasks [1/1 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | evaluate_gate | Threshold check, matches FR-05 |

---

## A-7: run_analysis.py [Complexity: 12, Budget: 12]

**Applied:** Parallelized-pipeline pattern (mirrors `h-e1/code/run_analysis.py::main`)

### API Signatures

```python
# h-m1/code/run_analysis.py
import sys, os, json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

sys.path.insert(0, str(Path(__file__).parent))
from config import CONFIG
from generate import load_problems, generate_code, get_benchmark
from static_analysis import run_static_analysis
from exec_analysis import run_execution_tests
from structural_errors import categorize_static_errors, has_structural_error
from coverage import compute_structural_coverage, error_category_distribution, per_benchmark_breakdown
from evaluate import evaluate_gate
from visualize import generate_all_figures

def process_one(args: tuple) -> dict:
    """args = (pid, problem). Mirrors H-E1 process_one().
    Returns {problem_id, benchmark, static_errors, exec_errors,
    structural, other, has_structural}."""
    ...

def main() -> dict:
    """Load 563 problems -> ProcessPoolExecutor(min(8, cpu_count)) ->
    process_one per problem -> compute_structural_coverage,
    error_category_distribution, per_benchmark_breakdown ->
    evaluate_gate(CONFIG.structural_gate) -> save results.json -> generate_all_figures."""
    ...

if __name__ == "__main__":
    main()
```

### Pseudo-code

```
process_one((pid, problem)):
  code = generate_code(problem, pid)
  static_errors = run_static_analysis(code)          # set of "pylint:X"/"mypy:Y"
  exec_errors = run_execution_tests(pid, code, problem, timeout=CONFIG.exec_timeout_sec)
  structural, other = categorize_static_errors(static_errors)
  return {
    "problem_id": pid, "benchmark": get_benchmark(pid),
    "static_errors": list(static_errors), "exec_errors": list(exec_errors),
    "structural": structural, "other": other,
    "has_structural": len(structural) > 0,
  }

main():
  problems = load_problems()                          # 563
  workers = min(8, os.cpu_count() or 4)
  per_problem = []
  with ProcessPoolExecutor(workers) as pool:
    futures = {pool.submit(process_one, item): item[0] for item in problems.items()}
    for f in as_completed(futures):
      per_problem.append(f.result())

  cov = compute_structural_coverage(per_problem)
  dist = error_category_distribution(per_problem)
  breakdown = per_benchmark_breakdown(per_problem)
  gate = evaluate_gate(cov["structural_coverage"], CONFIG.structural_gate)

  results = {"per_problem": per_problem, "coverage": cov,
             "category_distribution": dist, "per_benchmark": breakdown, "gate": gate}
  save results -> CONFIG.results_file
  generate_all_figures(results, CONFIG.figures_dir)
  return results
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | process_one | Per-problem worker, mirrors H-E1 shape |
| L-7-2 | main orchestration | Load, pool, aggregate |
| L-7-3 | Integrate coverage/evaluate modules | Wire compute_structural_coverage + evaluate_gate |
| L-7-4 | Save results.json + error handling | Match H-E1's try/except in as_completed loop |

---

## A-8: visualize.py [Complexity: 7, Budget: 7]

**Applied:** matplotlib bar/pie pattern (standard, no KB search needed)

```python
# h-m1/code/visualize.py
def generate_all_figures(results: dict, figures_dir: str) -> None:
    """Saves 3 PNGs to figures_dir:
    1. gate_metrics.png - bar: structural_coverage vs 0.60 threshold line
    2. category_breakdown.png - pie: error_category_distribution counts
    3. per_benchmark.png - bar: humaneval vs mbpp structural_coverage"""
    ...
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | gate + category figures | Bar (coverage vs threshold) + pie (categories) |
| L-8-2 | per-benchmark figure | Bar (humaneval vs mbpp) |

---

## A-9: Mechanism verification [Complexity: 5, Budget: 5]

**Applied:** Assertion-based sanity check (per 02c_experiment_brief.md verify_mechanism)

```python
# in run_analysis.py or separate verify.py
def verify_mechanism(per_problem: list, dist: dict) -> bool:
    """Assert structural errors were actually detected + categories are known."""
    total_structural = sum(len(r["structural"]) for r in per_problem)
    assert total_structural > 0, "No structural errors detected - mechanism not working"
    valid_categories = set(STRUCTURAL_ERROR_CODES.values())
    for r in per_problem[:10]:
        for code, category in r["structural"]:
            assert category in valid_categories, f"Unknown category {category}"
    print(f"Mechanism verified: {total_structural} structural errors categorized")
    return True
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | verify_mechanism | Assertion checks per brief |
| L-9-2 | Spot-check categorization | Validate first 10 problems' category labels |

---

## A-10: End-to-end run + results [Complexity: 6, Budget: 6]

**Applied:** Standard pipeline execution (no new API — invokes A-7's `main()`)

Run `python run_analysis.py`, verify `outputs/results.json` written, `figures/*.png` generated (3 files), gate result recorded. `verify_mechanism()` called before final print.

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|--------------|
| L-10-1 | Execute pipeline | Full run over 563 problems |
| L-10-2 | Validate outputs | Check results.json schema + gate outcome + 3 figures exist |

---

## File Organization

```
h-m1/code/
  config.py
  structural_errors.py
  coverage.py
  evaluate.py
  run_analysis.py
  visualize.py
  static_analysis.py   (copied unchanged)
  exec_analysis.py     (copied unchanged)
  generate.py          (copied unchanged)
  outputs/results.json
h-m1/figures/
  gate_metrics.png
  category_breakdown.png
  per_benchmark.png
```
