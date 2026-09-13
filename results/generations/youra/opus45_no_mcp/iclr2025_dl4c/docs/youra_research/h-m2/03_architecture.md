# Architecture: h-m2 (Error Localization Varies by Type) — MECHANISM

**Applied:** RLTF error categorization + AST-based ground-truth localization heuristics.
**Applied:** chi-square / Mann-Whitney statistical comparison pattern for categorical accuracy metrics.

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (extends h-m1)
**Status:** h-m1/code is self-contained (no external h-e1 dependency despite a stale `sys.path` insert in sample_collector.py). Reuses `sample_collector.py`, `config.py` functions/constants directly.
**Analyzed Path:** `h-m1/code/`
**Findings:**
- `sample_collector.py` already implements `classify_error(traceback_str) -> str`, `parse_traceback_line(traceback_str) -> Optional[int]`, `execute_code_safely`, `generate_failing_samples`, `generate_synthetic_samples`. Each collected sample dict has keys: `code, traceback, error_type, error_line, problem_id`.
- `config.py` defines `U_LINE_ERRORS`, `U_IGNORE_ERRORS` sets (differ slightly from PRD FR-2 list — PRD adds `ZeroDivisionError`/`ValueError` to U_line and `SystemExit` to U_ignore). h-m2 will use its own `config.py` constants per PRD FR-2, documented below.
- h-m1 samples do NOT include ground-truth bug line (only traceback-reported `error_line`) — h-m2 must add ground truth via AST heuristics (new capability, FR-3).
- No prior localization-accuracy or statistical-testing module exists; h-m2 adds this net-new.

---

## File Structure (Extends h-m1)

```
h-m2/code/
  ground_truth.py        # NEW: AST-based ground-truth bug line heuristics
  localization_analysis.py  # NEW: accuracy measurement per category
  stats_tests.py          # NEW: chi-square + Mann-Whitney
  visualization.py        # NEW: 3 required figures
  config.py               # NEW: U_LINE_ERRORS/U_IGNORE_ERRORS per RLTF Appendix B (PRD FR-2)
  run_analysis.py         # NEW: main entry point
h-m2/figures/
h-m2/results/
```

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| classify_error | `from h_m1_sample_collector import classify_error` (or relative sys.path insert to `../h-m1/code`) | `h-m1/code/sample_collector.py` |
| parse_traceback_line | same module | `h-m1/code/sample_collector.py` |
| execute_code_safely | same module | `h-m1/code/sample_collector.py` |
| generate_failing_samples | same module | `h-m1/code/sample_collector.py` |
| generate_synthetic_samples | same module | `h-m1/code/sample_collector.py` (fallback if model unavailable) |
| H_M1_Config / SEED / MODEL_NAME | `from config import get_config, SEED, MODEL_NAME` | `h-m1/code/config.py` |

**Verified from**: `h-m2/../h-m1/code/` (actual implementation, read directly — not from h-m1/03_architecture.md spec, which references a nonexistent h-e1 split).

**Reuse strategy**: h-m2 imports h-m1's `sample_collector.generate_failing_samples`/`generate_synthetic_samples` to obtain the same 500-sample pool (seed=42) so `error_type`/`error_line`/`traceback` are consistent with h-m1. Ground truth bug line is computed fresh in h-m2 (`ground_truth.py`) since h-m1 never computed it.

---

## Module Interfaces

### config.py (NEW)

```python
U_LINE_ERRORS = {'SyntaxError', 'IndentationError', 'NameError', 'TypeError',
                  'AttributeError', 'ZeroDivisionError', 'IndexError', 'KeyError', 'ValueError'}
U_IGNORE_ERRORS = {'AssertionError', 'RuntimeError', 'TimeoutError',
                    'RecursionError', 'MemoryError', 'SystemExit'}
TOLERANCE_LINES = 2
SEED = 42
```

### ground_truth.py (NEW)

**Dependencies**: ast (stdlib)

```python
def find_bug_line_ast(code: str, error_type: str, traceback_str: str) -> int | None: ...
    # Heuristic dispatch by error_type:
    #  NameError/AttributeError -> first AST Name/Attribute node matching undefined identifier
    #  IndexError/KeyError -> first Subscript node on the traceback line's containing statement
    #  TypeError/ValueError/ZeroDivisionError -> BinOp/Call node on traceback line
    #  SyntaxError/IndentationError -> traceback line itself (always accurate by definition)
    #  U_ignore types (AssertionError/RuntimeError/TimeoutError/RecursionError/MemoryError)
    #    -> walk call stack / loop structure heuristically; often diverges from traceback line

def annotate_ground_truth(samples: list[dict]) -> list[dict]: ...
    # Adds 'actual_bug_line' key to each sample dict via find_bug_line_ast

def spot_check_sample(samples: list[dict], n: int = 50, seed: int = 42) -> list[dict]: ...
    # Returns random subset for manual validation (NFR-3)
```

### localization_analysis.py (NEW)

**Dependencies**: ground_truth.py, config.py

```python
def is_accurate(traceback_line: int, actual_line: int, tolerance: int = 2) -> bool: ...

def compute_category_accuracy(samples: list[dict]) -> dict[str, dict]: ...
    # Returns {'U_line': {'accuracy': float, 'n': int, 'correct': int, 'ci_low': float, 'ci_high': float},
    #          'U_ignore': {...}}

def compute_distance_distribution(samples: list[dict]) -> dict[str, list[int]]: ...
    # Returns {'U_line': [abs(tb_line - actual_line), ...], 'U_ignore': [...]}

def compute_per_exception_breakdown(samples: list[dict]) -> dict[str, dict]: ...
    # Per specific exception type (e.g. NameError, AssertionError): accuracy + n
```

### stats_tests.py (NEW)

**Dependencies**: scipy.stats

```python
def chi_square_test(u_line_correct: int, u_line_total: int,
                     u_ignore_correct: int, u_ignore_total: int) -> dict: ...
    # Returns {'chi2': float, 'p_value': float, 'significant': bool}

def mann_whitney_test(u_line_distances: list[int], u_ignore_distances: list[int]) -> dict: ...
    # Returns {'u_statistic': float, 'p_value': float, 'significant': bool}
```

### visualization.py (NEW)

**Dependencies**: results from localization_analysis.py

```python
def plot_accuracy_bar(category_accuracy: dict, path: str): ...
    # Required: U_line vs U_ignore accuracy bars with 95% CI error bars

def plot_distance_distribution(distance_dist: dict, path: str): ...
    # Histogram/KDE of traceback-to-actual-line distances per category

def plot_exception_breakdown(breakdown: dict, path: str): ...
    # Bar chart accuracy per specific exception type
```

### run_analysis.py (NEW)

**Dependencies**: all above + h-m1/code/sample_collector.py

```python
def load_or_generate_samples(n_samples: int = 500, reuse_h_m1: bool = True) -> list[dict]: ...
    # If reuse_h_m1 and h-m1/results checkpoint exists -> load it
    # Else -> call h-m1 sample_collector.generate_failing_samples / generate_synthetic_samples

def main() -> dict: ...
    # 1. load_or_generate_samples (seed=42)
    # 2. annotate_ground_truth
    # 3. compute_category_accuracy, compute_distance_distribution, compute_per_exception_breakdown
    # 4. chi_square_test, mann_whitney_test
    # 5. generate 3 figures
    # 6. Return verdict (PASS/FAIL vs success criteria)
```

---

## Data Flow

```
h-m1 samples (reuse checkpoint) OR sample_collector.generate_failing_samples
  -> ground_truth.annotate_ground_truth (AST heuristics) -> actual_bug_line per sample
  -> localization_analysis.compute_category_accuracy (U_line vs U_ignore)
  -> localization_analysis.compute_distance_distribution
  -> localization_analysis.compute_per_exception_breakdown
  -> stats_tests.chi_square_test + mann_whitney_test
  -> visualization.py generates 3 figures
  -> run_analysis.main aggregates -> PASS/FAIL verdict
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Reuse/load samples | load_or_generate_samples, integrate h-m1 sample_collector | 6 | 2+2+1+1 |
| B-2 | AST ground truth heuristics | find_bug_line_ast per error type (9 error types) | 14 | 4+2+5+3 |
| B-3 | Ground truth annotation + spot-check | annotate_ground_truth, spot_check_sample | 6 | 2+1+2+1 |
| B-4 | Accuracy computation | compute_category_accuracy with CI | 8 | 2+2+3+1 |
| B-5 | Distance distribution | compute_distance_distribution | 5 | 1+1+2+1 |
| B-6 | Per-exception breakdown | compute_per_exception_breakdown | 5 | 1+1+2+1 |
| B-7 | Statistical tests | chi_square_test, mann_whitney_test | 6 | 2+2+1+1 |
| B-8 | Visualization | 3 required figures | 7 | 2+2+2+1 |
| B-9 | Main runner | run_analysis.py orchestration + verdict logic | 6 | 2+1+2+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [B-2], Medium(9-13): [], Low(4-8): [B-1, B-3, B-4, B-5, B-6, B-7, B-8, B-9]

**Total tasks: 9 (within 6-12 epic range)**

---

## Self-Validation

- No ASCII diagrams (text arrows only) - OK
- Interface-only module code - OK
- 9 epic tasks with complexity - OK
- Base hypothesis (h-m1) actual code read via Read tool; import paths verified - OK
- External Dependencies section included with file locations - OK
- Codebase Analysis (Serena) section included - OK
- MECHANISM tier complexity appropriate - OK
