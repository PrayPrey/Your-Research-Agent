# Architecture: H-M1 (Static Analysis Detects Structural Errors)

**Type:** MECHANISM
**Applied:** Extend-and-categorize pattern (reuse validated analysis pipeline, add categorization layer)
**Applied:** Parallelized-pipeline pattern (ProcessPoolExecutor, gate evaluation, figure generation)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-E1)
**Status:** Patterns found from base code (Serena unavailable this session — analyzed via direct file read of actual H-E1 `code/` files, not specs, per critical rule)
**Analyzed Path:** `h-e1/code/`
**Findings:**
- `static_analysis.py` returns raw error sets (`{"pylint:E0602", "mypy:incompatible..."}`) — H-M1 must parse the `pylint:`/`mypy:` prefix to categorize.
- `run_analysis.py` uses `ProcessPoolExecutor(max_workers=min(8, cpu_count))`, per-problem `process_one()` worker, results dict + `evaluate_gate()` + `generate_all_figures()`. H-M1 reuses this orchestration shape directly.
- `config.py` is a simple `@dataclass` singleton `CONFIG`. H-M1 extends with `structural_gate: float = 0.60`.
- `exec_analysis.py::run_execution_tests` returns a `Set[str]` of `exec:*` failure tags — used as-is to determine "test-failing problems" (non-empty set = failure).
- No `generate.py`/`jaccard.py` reuse needed for categorization logic itself, but `generate.py` (problem loading/generation) and `get_benchmark()` are reused unchanged for dataset iteration.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| run_static_analysis | `from static_analysis import run_static_analysis` | `h-e1/code/static_analysis.py` |
| run_execution_tests | `from exec_analysis import run_execution_tests` | `h-e1/code/exec_analysis.py` |
| load_problems, generate_code, get_benchmark | `from generate import load_problems, generate_code, get_benchmark` | `h-e1/code/generate.py` |
| CONFIG (base fields) | `from config import ExperimentConfig` (pattern reused, new instance in h-m1) | `h-e1/code/config.py` |

**Verified from:** `h-e1/code/` (actual implementation, read directly)

**H-M1 code will copy `static_analysis.py`, `exec_analysis.py`, `generate.py` unchanged into `h-m1/code/` (per NFR-03 "extend, do not rewrite") and add new modules below.**

---

## Module Structure

### structural_errors.py (`h-m1/code/structural_errors.py`)

**Dependencies:** none (pure logic)

```python
STRUCTURAL_ERROR_CODES: dict[str, str]  # pylint codes + mypy keys -> category name

def categorize_static_errors(static_errors: set) -> tuple[list, list]:
    """Split raw static_errors set (from static_analysis.run_static_analysis)
    into (structural: list[tuple[str,str]], other: list[str])."""
    ...

def has_structural_error(static_errors: set) -> bool: ...
```

### coverage.py (`h-m1/code/coverage.py`)

**Dependencies:** structural_errors

```python
def compute_structural_coverage(per_problem_results: list[dict]) -> dict:
    """Filter to problems with non-empty exec_errors (test-failing),
    return {structural_coverage: float, n_failing: int, n_structural: int}."""
    ...

def error_category_distribution(per_problem_results: list[dict]) -> dict[str, int]: ...

def per_benchmark_breakdown(per_problem_results: list[dict]) -> dict: ...
```

### evaluate.py (`h-m1/code/evaluate.py`)

**Dependencies:** coverage

```python
def evaluate_gate(structural_coverage: float, threshold: float = 0.60) -> dict:
    """{passed, metric, threshold, message}"""
    ...
```

### config.py (`h-m1/code/config.py`)

**Dependencies:** none

```python
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

### run_analysis.py (`h-m1/code/run_analysis.py`)

**Dependencies:** config, generate (reused), static_analysis (reused), exec_analysis (reused), structural_errors, coverage, evaluate, visualize

```python
def process_one(args: tuple) -> dict:
    """pid, problem -> {problem_id, benchmark, static_errors, exec_errors,
    structural, other, has_structural}. Mirrors H-E1 process_one()."""
    ...

def main() -> dict: ...  # load 563 problems, ProcessPoolExecutor(8), compute
                          # coverage, evaluate_gate, save results.json, figures
```

### visualize.py (`h-m1/code/visualize.py`)

**Dependencies:** none

```python
def generate_all_figures(results: dict, figures_dir: str) -> None:
    """Bar: structural_coverage vs 0.60 threshold.
    Pie: structural error category distribution.
    Bar: per-benchmark (HumanEval+ vs MBPP+) coverage."""
    ...
```

---

## File Organization

```
h-m1/code/
  config.py            (new, extends H-E1 pattern)
  structural_errors.py (new — STRUCTURAL_ERROR_CODES + categorize)
  coverage.py           (new — coverage/distribution/breakdown)
  evaluate.py           (new — gate check, 0.60 threshold)
  run_analysis.py       (new — orchestration, mirrors h-e1/run_analysis.py)
  visualize.py          (new — 3 figures)
  static_analysis.py    (copied unchanged from h-e1/code/)
  exec_analysis.py      (copied unchanged from h-e1/code/)
  generate.py           (copied unchanged from h-e1/code/)
  outputs/results.json
h-m1/figures/
  gate_metrics.png
  category_breakdown.png
  per_benchmark.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Copy base infra | Copy static_analysis.py, exec_analysis.py, generate.py from h-e1 unchanged | 3 | 1+1+1+0 |
| A-2 | Config setup | config.py with structural_gate=0.60 | 3 | 1+1+1+0 |
| A-3 | STRUCTURAL_ERROR_CODES dict | Define pylint+mypy code->category mapping | 4 | 2+0+2+0 |
| A-4 | categorize_static_errors | Parse pylint:/mypy: prefixed error strings into structural/other | 8 | 3+2+3+0 |
| A-5 | coverage.py | compute_structural_coverage, distribution, per-benchmark breakdown | 9 | 3+3+2+1 |
| A-6 | evaluate.py gate | Gate check against 0.60 threshold | 3 | 1+1+1+0 |
| A-7 | run_analysis.py pipeline | ProcessPoolExecutor over 563 problems, integrate all modules | 12 | 4+4+2+2 |
| A-8 | visualize.py | 3 figures (bar gate, pie category, bar per-benchmark) | 7 | 3+2+1+1 |
| A-9 | Mechanism verification | verify_mechanism() assertion check, spot-check categorization correctness | 5 | 2+1+2+0 |
| A-10 | End-to-end run + results | Execute full pipeline, save results.json, validate gate outcome | 6 | 2+2+1+1 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-5, A-7], Low(4-8): [A-3, A-4, A-6, A-8, A-9, A-10], Trivial(<4): [A-1, A-2]
