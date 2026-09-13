# Architecture: H-M2 (Execution Detects Behavioral Errors)

**Type:** MECHANISM
**Applied:** Extend-and-categorize pattern (reuse validated analysis pipeline, add behavioral detection layer)
**Applied:** Filter-then-test pattern (identify static-clean code, then execute tests)
**Applied:** Parallelized-pipeline pattern (ProcessPoolExecutor, gate evaluation, figure generation)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M1)
**Status:** Patterns found from base code (Serena unavailable this session — analyzed via direct file read of actual H-M1 `code/` files, not specs, per critical rule)
**Analyzed Path:** `h-m1/code/`
**Findings:**
- `static_analysis.py` returns raw error sets (`{"pylint:E0602", "mypy:incompatible..."}`) — H-M2 checks `len(errors) == 0` to identify static-clean code.
- `exec_analysis.py::run_execution_tests` returns a `Set[str]` of `exec:*` failure tags — H-M2 uses this to detect behavioral errors in static-clean code.
- `run_analysis.py` uses `ProcessPoolExecutor(max_workers=min(8, cpu_count))`, per-problem `process_one()` worker, results dict + `evaluate_gate()` + `generate_all_figures()`. H-M2 reuses this orchestration shape directly.
- `config.py` is a simple `@dataclass` singleton `CONFIG`. H-M2 extends with `behavioral_gate: float = 0.40`.
- `generate.py::load_problems, get_benchmark` reused unchanged for dataset iteration.
- `structural_errors.py`, `coverage.py`, `evaluate.py` exist but H-M2 needs different logic (behavioral detection, not structural coverage).

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| run_static_analysis | `from static_analysis import run_static_analysis` | `h-m1/code/static_analysis.py` |
| run_execution_tests | `from exec_analysis import run_execution_tests` | `h-m1/code/exec_analysis.py` |
| load_problems, get_benchmark | `from generate import load_problems, get_benchmark` | `h-m1/code/generate.py` |
| CONFIG (base fields) | `from config import ExperimentConfig` (pattern reused, new instance in h-m2) | `h-m1/code/config.py` |

**Verified from:** `h-m1/code/` (actual implementation)

**H-M2 code will copy `static_analysis.py`, `exec_analysis.py`, `generate.py` unchanged into `h-m2/code/` (per NFR-03 "extend, do not rewrite") and add new modules below.**

---

## Module Structure

### behavioral_errors.py (`h-m2/code/behavioral_errors.py`)

**Dependencies:** none (pure logic)

```python
BEHAVIORAL_CATEGORIES: dict[str, list[str]]  # category -> error substrings

def categorize_test_failure(error_msg: str) -> str:
    """Return category: 'wrong_output', 'runtime_exception', 'timeout', 'edge_case'."""
    ...

def is_static_clean(static_errors: set) -> bool:
    """Return True if len(static_errors) == 0."""
    ...
```

### behavioral_coverage.py (`h-m2/code/behavioral_coverage.py`)

**Dependencies:** behavioral_errors

```python
def compute_behavioral_rate(per_problem_results: list[dict]) -> dict:
    """Filter to static-clean problems (zero pylint+mypy errors),
    count how many fail tests.
    Return {behavioral_rate: float, static_clean_count: int, behavioral_failures: int}."""
    ...

def failure_category_distribution(per_problem_results: list[dict]) -> dict[str, int]:
    """Count failures by category (wrong_output, exception, timeout, edge_case)."""
    ...

def per_benchmark_breakdown(per_problem_results: list[dict]) -> dict:
    """Return {humaneval_plus: {rate, count}, mbpp_plus: {rate, count}}."""
    ...
```

### evaluate.py (`h-m2/code/evaluate.py`)

**Dependencies:** behavioral_coverage

```python
def evaluate_gate(behavioral_rate: float, threshold: float = 0.40) -> dict:
    """{passed: bool, metric: float, threshold: float, message: str}"""
    ...
```

### config.py (`h-m2/code/config.py`)

**Dependencies:** none

```python
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

### run_analysis.py (`h-m2/code/run_analysis.py`)

**Dependencies:** config, generate (reused), static_analysis (reused), exec_analysis (reused), behavioral_errors, behavioral_coverage, evaluate, visualize

```python
def process_one(args: tuple) -> dict:
    """pid, problem -> {problem_id, benchmark, static_errors, exec_errors,
    is_static_clean, has_behavioral_failure, failure_category}."""
    ...

def main() -> dict:
    """Load 563 problems, ProcessPoolExecutor(8), compute behavioral_rate,
    evaluate_gate, save results.json, generate figures."""
    ...
```

### visualize.py (`h-m2/code/visualize.py`)

**Dependencies:** none

```python
def generate_all_figures(results: dict, figures_dir: str) -> None:
    """Bar: behavioral_rate vs 0.40 threshold (REQUIRED).
    Pie: failure category distribution (wrong_output, exception, etc).
    Bar: per-benchmark (HumanEval+ vs MBPP+) behavioral rates."""
    ...
```

---

## File Organization

```
h-m2/code/
  config.py              (new, extends H-M1 pattern with behavioral_gate=0.40)
  behavioral_errors.py   (new — categorize_test_failure, is_static_clean)
  behavioral_coverage.py (new — behavioral_rate, distribution, breakdown)
  evaluate.py            (new — gate check, 0.40 threshold)
  run_analysis.py        (new — orchestration, mirrors h-m1/run_analysis.py)
  visualize.py           (new — 3 figures)
  static_analysis.py     (copied unchanged from h-m1/code/)
  exec_analysis.py       (copied unchanged from h-m1/code/)
  generate.py            (copied unchanged from h-m1/code/)
  outputs/results.json
h-m2/figures/
  gate_metrics.png
  category_breakdown.png
  per_benchmark.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown (ModSize+Deps+Algo+Integ) |
|----|------|-------------|------------|-------------------------------------|
| A-1 | Copy base infra | Copy static_analysis.py, exec_analysis.py, generate.py from h-m1 unchanged | 3 | 1+1+1+0 |
| A-2 | Config setup | config.py with behavioral_gate=0.40 | 3 | 1+1+1+0 |
| A-3 | is_static_clean | Function to check len(static_errors)==0 | 2 | 1+0+1+0 |
| A-4 | BEHAVIORAL_CATEGORIES dict | Define category -> error substrings mapping | 4 | 2+0+2+0 |
| A-5 | categorize_test_failure | Parse exec error message into category | 6 | 2+2+2+0 |
| A-6 | compute_behavioral_rate | Filter static-clean, count test failures, compute rate | 8 | 3+3+2+0 |
| A-7 | failure_category_distribution | Count failures by category | 5 | 2+2+1+0 |
| A-8 | per_benchmark_breakdown | Separate rates for HumanEval+ vs MBPP+ | 5 | 2+2+1+0 |
| A-9 | evaluate.py gate | Gate check against 0.40 threshold | 3 | 1+1+1+0 |
| A-10 | run_analysis.py pipeline | ProcessPoolExecutor over 563 problems, integrate all modules | 12 | 4+4+2+2 |
| A-11 | visualize.py | 3 figures (bar gate, pie category, bar per-benchmark) | 7 | 3+2+1+1 |
| A-12 | End-to-end run + results | Execute full pipeline, save results.json, validate gate outcome | 6 | 2+2+1+1 |

**Total Tasks:** 12 (within FULL tier budget of 30)

**Complexity Distribution:**
- Very High (18-20): 0
- High (14-17): 0  
- Medium (9-13): 1 (A-10)
- Low (4-8): 6 (A-4, A-5, A-6, A-7, A-8, A-11, A-12)
- Trivial (<4): 4 (A-1, A-2, A-3, A-9)

**Overall Tier:** 1 (Low complexity)
