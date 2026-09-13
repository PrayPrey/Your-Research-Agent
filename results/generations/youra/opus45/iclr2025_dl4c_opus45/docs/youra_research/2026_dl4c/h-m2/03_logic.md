# Logic: H-M2 Execution Depth Analysis

**Applied**: Standard Python stdlib trace pattern (signal-based timeout, ast line counting)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m1)
**Status**: API signatures verified from base code
**Analyzed Path**: `docs/youra_research/20260323_dl4c/h-m1/code/`
**Relevant Symbols**:
- `HM1Config` (config.py) - dataclass pattern with `__post_init__` path normalization
- `load_h_e1_results(config: HM1Config) -> Tuple[List[dict], List[dict]]`
- `classify_error(error_trace: str) -> str` - ICSE 2025 taxonomy, inlined (not imported)
- `validate_data_integrity(rl_results, dpo_results, config) -> Dict`
- H-E1 record format: `{"status": "fail"|"pass", "error_trace": str|None, "generated_code": str, "problem_id": str}`
- H-E1 result paths: `../../h-e1/code/outputs/rl_execution_results.json` and `dpo_execution_results.json`

---

## External Dependencies API (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-m1/code/data_loader.py (ACTUAL CODE)
def load_h_e1_results(config: HM1Config) -> Tuple[List[dict], List[dict]]:
    """Returns (rl_results, dpo_results) - all samples including passes."""

def classify_error(error_trace: str) -> str:
    """Returns one of: 'pass', 'syntax', 'runtime', 'assertion', 'other'."""

def validate_data_integrity(
    rl_results: List[dict],
    dpo_results: List[dict],
    config: HM1Config,  # ← verified: 'config' not 'cfg'
) -> Dict:
    """Returns dict with keys: rl_failures, dpo_failures, rl_total, dpo_total, valid, warnings."""

# From: h-m1/code/config.py (ACTUAL CODE)
@dataclass
class HM1Config:
    rl_results_path: str   # ← verified field name
    dpo_results_path: str  # ← verified field name
    expected_rl_failures: int = 236
    expected_dpo_failures: int = 530
    def __post_init__(self): ...  # normalizes all paths to absolute
```

**Note**: H-M2 does NOT import from h-m1. `classify_error` is inlined per h-m1 lesson learned.
**Verified from**: `h-m1/code/data_loader.py` and `h-m1/code/config.py` (actual implementation)

---

## A-3: Executable Line Counter [Complexity: 10, Budget: 2 subtasks]

**Applied**: Standard Python stdlib trace pattern

### API Signatures

```python
# depth_tracer.py
import ast
from typing import Set

def count_executable_lines(code_string: str) -> int:
    """Count non-blank, non-comment lines using ast.parse. Returns 0 on SyntaxError."""
    ...
```

### Pseudo-code (non-trivial: AST node line extraction)

```
1. try: tree = ast.parse(code_string)
2. except SyntaxError: return 0
3. lines: Set[int] = set()
4. for node in ast.walk(tree):
       if hasattr(node, 'lineno'): lines.add(node.lineno)
5. return len(lines)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | AST parse line extraction | Walk AST nodes, collect unique lineno values |
| L-3-2 | Edge case handling | Empty string -> 0, comments-only -> 0, SyntaxError -> 0 |

---

## A-4: Trace Execution Engine [Complexity: 15, Budget: 2 subtasks]

**Applied**: Standard Python stdlib trace pattern

### API Signatures

```python
# depth_tracer.py
import trace
import signal
import tempfile
import sys
from dataclasses import dataclass
from typing import Optional

@dataclass
class DepthResult:
    sample_id: str
    model: str           # "rl" or "dpo"
    problem_id: str
    total_lines: int
    executed_lines: int
    execution_depth: float   # executed_lines / max(total_lines, 1)
    error_type: str          # "syntax" | "runtime" | "assertion" | "other"
    trace_success: bool

def measure_execution_depth(
    code_string: str,
    sample_id: str,
    problem_id: str,
    model: str,
    timeout: float = 5.0,
) -> DepthResult:
    """Measure lines executed before failure using trace.Trace(count=True, trace=False).
    SyntaxError -> depth=0. Timeout -> depth=partial from collected trace so far."""
    ...
```

### Pseudo-code (complex: timeout + trace + isolation)

```
1. total_lines = count_executable_lines(code_string)
2. if total_lines == 0:
       return DepthResult(..., executed_lines=0, execution_depth=0.0, error_type="syntax", ...)
3. try: compile(code_string, "<string>", "exec")  # SyntaxError fast path
4. except SyntaxError:
       return DepthResult(..., execution_depth=0.0, error_type="syntax", trace_success=True)
5. tracer = trace.Trace(count=True, trace=False, ignoredirs=[sys.prefix])
6. error_type = "other"; executed_lines = 0
7. def _handler(sig, frame): raise TimeoutError
8. signal.signal(signal.SIGALRM, _handler)
9. signal.alarm(int(timeout) + 1)
10. try:
        namespace = {}
        tracer.runfunc(exec, compile(code_string, "<string>", "exec"), namespace)
        # if no exception: shouldn't happen (we're measuring failures), but handle gracefully
11. except AssertionError: error_type = "assertion"
12. except TimeoutError: error_type = "runtime"  # timeout treated as runtime
13. except SyntaxError: error_type = "syntax"
14. except Exception as e: error_type = classify_error(repr(e))
15. finally: signal.alarm(0)
16. counts = tracer.results().counts  # dict: {(filename, lineno): count}
17. executed_lines = len([ln for (fn, ln), c in counts.items() if c > 0 and fn == "<string>"])
18. depth = executed_lines / max(total_lines, 1)
19. return DepthResult(sample_id, model, problem_id, total_lines, executed_lines, depth, error_type, True)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | trace.Trace integration | Run tracer.runfunc(exec, ...), extract counts from tracer.results() |
| L-4-2 | Timeout + isolation | signal.SIGALRM handler, alarm cancel in finally, compile fast-path |

---

## A-5: Batch Depth Measurement [Complexity: 10, Budget: 1 subtask]

**Applied**: Standard Python stdlib trace pattern

### API Signatures

```python
# depth_tracer.py
import logging
from typing import List
from config import HM2Config

def measure_all_failures(
    failures: List[dict],
    model: str,
    config: HM2Config,
) -> List[DepthResult]:
    """Batch measure with progress reporting every 50 samples. Per-sample error catching.
    failures: list of H-E1 records with 'generated_code', 'problem_id', 'sample_id' keys."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Batch loop with error catching | Enumerate failures, call measure_execution_depth, catch per-sample exceptions, log progress |

---

## A-6: Statistical Analysis [Complexity: 12, Budget: 1 subtask]

**Applied**: Standard scipy stats pattern

### API Signatures

```python
# analyze.py
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple
from depth_tracer import DepthResult
from config import HM2Config

def run_ttest(
    rl_depths: List[float],
    dpo_depths: List[float],
    alternative: str = "greater",
) -> Tuple[float, float]:
    """scipy.stats.ttest_ind one-sided. Returns (t_statistic, p_value)."""
    ...

def compute_cohens_d(
    rl_depths: List[float],
    dpo_depths: List[float],
) -> float:
    """Pooled-std Cohen's d. Returns (mean_rl - mean_dpo) / pooled_std."""
    ...

def compute_descriptive_stats(depths: List[float]) -> Dict:
    """Returns dict: mean, std, median, min, max, n, ci_lower, ci_upper (95%)."""
    ...

def run_analysis(
    rl_results: List[DepthResult],
    dpo_results: List[DepthResult],
    config: HM2Config,
) -> Dict:
    """Full pipeline: t-test + Cohen's d + descriptive stats. Saves outputs. Returns metrics dict."""
    ...
```

### Pseudo-code for `compute_cohens_d`

```
1. n1, n2 = len(rl_depths), len(dpo_depths)
2. pooled_std = sqrt(((n1-1)*std(rl)**2 + (n2-1)*std(dpo)**2) / (n1+n2-2))
3. return (mean(rl) - mean(dpo)) / max(pooled_std, 1e-10)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | run_analysis orchestration | Extract depth lists from DepthResult, call t-test + Cohen's d + descriptive, gate pass logic, save JSON/CSV |

---

## H-E1 Record Format (Verified from h-m1 Code)

```python
# H-E1 record structure (verified from h-m1/code/data_loader.py usage):
{
    "status": "fail" | "pass",      # filter for "fail" only
    "error_trace": str | None,      # passed to classify_error()
    "generated_code": str,          # passed to measure_execution_depth()
    "problem_id": str,              # e.g. "HumanEval/0"
    # sample_id: derive as f"{model}_{i}" (index-based if no explicit field)
}
```

---

## Key Implementation Notes for Phase 4

- `trace.Trace` is NOT thread-safe; use `signal.SIGALRM` (Linux only) for timeout, not threading
- `tracer.results().counts` keys are `(filename, lineno)` tuples; filter by `filename == "<string>"`
- `classify_error` MUST be inlined in `depth_tracer.py` (not imported from h-m1)
- `HM2Config` follows exact same dataclass + `__post_init__` pattern as `HM1Config`
- All modules use flat imports: `from config import HM2Config` (no subdirectory packages)
- Gate pass condition: `p_value < config.t_test_p_threshold AND mean(rl_depths) > mean(dpo_depths)`
- `depth_data.csv` columns: `sample_id, model, problem_id, total_lines, executed_lines, depth, error_type`

---

*Generated by Phase 3 Logic Workflow | Anonymous Research Pipeline*
*Hypothesis: H-M2 | Type: MECHANISM | Gate: SHOULD_WORK*
*Base Code Verified: h-m1/code/data_loader.py, h-m1/code/config.py*
