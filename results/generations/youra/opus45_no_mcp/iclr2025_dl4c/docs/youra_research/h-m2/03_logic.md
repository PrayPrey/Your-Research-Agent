# Logic: h-m2 (Error Localization Varies by Type)

**Applied:** AST error localization heuristics (dispatch by exception type, node-kind matching)
**Applied:** chi-square / Mann-Whitney U pattern for categorical accuracy comparison (scipy.stats)

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (extends h-m1)
**Status:** API signatures verified from actual h-m1 code (not spec)
**Analyzed Path:** `h-m1/code/sample_collector.py`, `h-m1/code/config.py`
**Relevant Symbols:**
- `classify_error(traceback_str: str) -> str`
- `parse_traceback_line(traceback_str: str) -> Optional[int]`
- `execute_code_safely(code: str, test_input: str = "", timeout_s: int = 5) -> tuple`
- `generate_failing_samples(model, tokenizer, dataset, n_samples=500, max_attempts=2000, seed=42) -> List[Dict]`
- `generate_synthetic_samples(n_samples=500, seed=42) -> List[Dict]`

**Caveat found**: `sample_collector.py` line 9 does `sys.path.insert(0, '../h-e1/code')` and imports `U_LINE_ERRORS` from that (nonexistent in this repo) path — stale dependency. h-m2 does NOT import `U_LINE_ERRORS` from h-m1; h-m2 defines its own set in `h-m2/code/config.py` per PRD FR-2 (superset differs slightly — see below). Sample dicts returned by h-m1 functions have keys: `code, traceback, error_type, error_line, problem_id`. h-m2 adds `actual_bug_line` to each dict in-place.

---

## External Dependencies API (From Actual h-m1 Code)

```python
# From: h-m1/code/sample_collector.py (ACTUAL CODE)
def classify_error(traceback_str: str) -> str:
    """Returns 'U_line' | 'U_ignore' | 'pass', using h-m1's own U_LINE_ERRORS set."""

def parse_traceback_line(traceback_str: str) -> Optional[int]:
    """Extract last 'File "...", line N' match. None if no match."""

def execute_code_safely(code: str, test_input: str = "", timeout_s: int = 5):
    """Returns (result: 'PASS'|'ERROR', traceback: Optional[str])."""

def generate_failing_samples(
    model, tokenizer, dataset,
    n_samples: int = 500, max_attempts: int = 2000, seed: int = 42,
) -> List[Dict]:
    """Sample dict keys: code, traceback, error_type, error_line, problem_id."""

def generate_synthetic_samples(n_samples: int = 500, seed: int = 42) -> List[Dict]:
    """Fallback, no model needed. Same dict schema as above."""
```

**Note**: h-m2 calls `error_type = classify_error(...)` is NOT reused directly — h-m2 recategorizes each sample against its OWN `U_LINE_ERRORS`/`U_IGNORE_ERRORS` (PRD FR-2 differs from h-m1's set: adds `ZeroDivisionError`, `ValueError` to U_line, drops nothing). Use `sample["traceback"]` + h-m2's `config.py` sets to recompute `error_type`, do not trust h-m1's `sample["error_type"]` field as-is.

---

## A-1 (B-1): Reuse/Load Samples [Complexity: 6, Budget: 6]

**Applied:** Checkpoint-first loading pattern (avoid recompute)

### API Signatures

```python
def load_or_generate_samples(
    n_samples: int = 500,
    reuse_h_m1: bool = True,
    checkpoint_path: str = "h-m2/results/samples.json",
) -> list[dict]:
    """Load h-m1 checkpoint if present, else generate_synthetic_samples(n_samples, seed=42)."""
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Checkpoint lookup | Check `h-m1/results/*.json` and `h-m2/results/samples.json` for existing pool |
| L-1-2 | Fallback generation | Call `generate_synthetic_samples(n_samples, seed=42)` if no checkpoint/model |
| L-1-3 | Recategorize | Apply h-m2 `config.py` U_LINE_ERRORS/U_IGNORE_ERRORS via traceback string match (mirrors `classify_error` logic, own sets) |
| L-1-4 | Persist | Save loaded/generated + recategorized samples to `checkpoint_path` |

---

## A-2 (B-2): AST Ground Truth Heuristics [Complexity: 14, Budget: 14]

**Applied:** AST error localization heuristics — dispatch table by exception type; walk `ast.parse(code)` body, match node type + line number.

### API Signatures

```python
import ast

def find_bug_line_ast(code: str, error_type: str, traceback_str: str) -> int | None:
    """Heuristic ground-truth bug line. Returns None if code fails to parse."""

def _find_name_or_attr_line(tree: ast.Module, tb_line: int, traceback_str: str) -> int | None:
    """NameError/AttributeError: locate Name/Attribute node whose id/attr appears in traceback msg."""

def _find_subscript_line(tree: ast.Module, tb_line: int) -> int | None:
    """IndexError/KeyError: first Subscript node in the statement at tb_line."""

def _find_binop_or_call_line(tree: ast.Module, tb_line: int) -> int | None:
    """TypeError/ValueError/ZeroDivisionError: BinOp/Call node at or nearest tb_line."""

def _find_syntax_line(traceback_str: str) -> int | None:
    """SyntaxError/IndentationError: parse line number directly from traceback (always accurate)."""

def _find_stack_heuristic_line(tree: ast.Module, tb_line: int, error_type: str) -> int | None:
    """AssertionError/RuntimeError/TimeoutError/RecursionError/MemoryError: walk enclosing
    function/loop; returns line of outermost recursive call or loop header, else tb_line."""
```

### Tensor Shapes

N/A (no tensors; AST node operations only).

### Pseudo-code

```
find_bug_line_ast(code, error_type, traceback_str):
    tree = ast.parse(code)  # returns None on SyntaxError parse failure -> fallback to tb_line
    tb_line = parse_traceback_line(traceback_str)
    if error_type in {SyntaxError, IndentationError}:
        return _find_syntax_line(traceback_str)  # trust traceback fully
    if error_type in {NameError, AttributeError}:
        return _find_name_or_attr_line(tree, tb_line, traceback_str) or tb_line
    if error_type in {IndexError, KeyError}:
        return _find_subscript_line(tree, tb_line) or tb_line
    if error_type in {TypeError, ValueError, ZeroDivisionError}:
        return _find_binop_or_call_line(tree, tb_line) or tb_line
    # U_ignore types: AssertionError, RuntimeError, TimeoutError, RecursionError, MemoryError
    return _find_stack_heuristic_line(tree, tb_line, error_type)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | U_line node-matching heuristics | Name/Attribute/Subscript/BinOp/Call dispatch (4 error groups) |
| L-2-2 | SyntaxError/IndentationError passthrough | Direct traceback line trust |
| L-2-3 | U_ignore stack-walk heuristic | Walk loop/function nodes for Recursion/Timeout/Memory/Runtime/Assertion |
| L-2-4 | Parse-failure fallback + robustness | try/except ast.parse, unresolvable node -> return tb_line |

---

## A-3 (B-3): Ground Truth Annotation + Spot-check [Complexity: 6, Budget: 6]

**Applied:** Standard PyTorch/Python — none (pure stdlib random sampling)

### API Signatures

```python
def annotate_ground_truth(samples: list[dict]) -> list[dict]:
    """In-place: adds sample['actual_bug_line'] = find_bug_line_ast(...) for each sample."""

def spot_check_sample(samples: list[dict], n: int = 50, seed: int = 42) -> list[dict]:
    """random.sample(samples, n) with fixed seed, for manual NFR-3 validation."""
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Annotate loop | Call `find_bug_line_ast` per sample, attach `actual_bug_line` |
| L-3-2 | Error handling | Skip/log samples where AST parse fails entirely |
| L-3-3 | Spot-check sampler | `random.seed(seed); random.sample(samples, n)` |
| L-3-4 | Export for review | Write spot-check subset to `h-m2/results/spot_check.json` |

---

## A-4 (B-4): Accuracy Computation [Complexity: 8, Budget: 8]

**Applied:** Wilson score interval for binomial CI (standard stats pattern)

### API Signatures

```python
def is_accurate(traceback_line: int, actual_line: int, tolerance: int = 2) -> bool:
    """abs(traceback_line - actual_line) <= tolerance."""

def compute_category_accuracy(samples: list[dict]) -> dict[str, dict]:
    """Returns {'U_line': {'accuracy': float, 'n': int, 'correct': int,
                            'ci_low': float, 'ci_high': float},
                'U_ignore': {...}}"""
```

### Tensor Shapes

N/A.

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Per-category grouping | Split samples by recategorized `error_type` (U_line/U_ignore) |
| L-4-2 | Accuracy + correct/n counts | Apply `is_accurate` with `tolerance=2` per sample |
| L-4-3 | Wilson 95% CI | `statsmodels.stats.proportion.proportion_confint(correct, n, method='wilson')` or manual formula |
| L-4-4 | Assemble result dict | Combine into final `{'U_line': {...}, 'U_ignore': {...}}` |

---

## A-5 (B-5): Distance Distribution [Complexity: 5, Budget: 5]

### API Signatures

```python
def compute_distance_distribution(samples: list[dict]) -> dict[str, list[int]]:
    """Returns {'U_line': [abs(tb_line - actual_line), ...], 'U_ignore': [...]}"""
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | Per-sample distance | `abs(sample['error_line'] - sample['actual_bug_line'])` |
| L-5-2 | Group by category | Split into U_line/U_ignore lists |
| L-5-3 | Handle None | Skip samples with `actual_bug_line is None` |

---

## A-6 (B-6): Per-exception Breakdown [Complexity: 5, Budget: 5]

### API Signatures

```python
def compute_per_exception_breakdown(samples: list[dict]) -> dict[str, dict]:
    """Per specific exception name (e.g. NameError, AssertionError):
    {'NameError': {'accuracy': float, 'n': int}, ...}"""
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | Extract exception name | Regex/string match exception class name from `traceback` |
| L-6-2 | Group + accuracy per exception | Reuse `is_accurate` per group |
| L-6-3 | Sort output | Sort dict by descending `n` for readability |

---

## A-7 (B-7): Statistical Tests [Complexity: 6, Budget: 6]

**Applied:** scipy.stats chi2_contingency / mannwhitneyu standard pattern

### API Signatures

```python
def chi_square_test(
    u_line_correct: int, u_line_total: int,
    u_ignore_correct: int, u_ignore_total: int,
) -> dict:
    """2x2 contingency table via scipy.stats.chi2_contingency.
    Returns {'chi2': float, 'p_value': float, 'significant': bool}  # significant = p < 0.05"""

def mann_whitney_test(u_line_distances: list[int], u_ignore_distances: list[int]) -> dict:
    """scipy.stats.mannwhitneyu(u_line_distances, u_ignore_distances, alternative='less').
    Returns {'u_statistic': float, 'p_value': float, 'significant': bool}"""
```

### Pseudo-code

```
chi_square_test(...):
    table = [[u_line_correct, u_line_total - u_line_correct],
             [u_ignore_correct, u_ignore_total - u_ignore_correct]]
    chi2, p, dof, expected = scipy.stats.chi2_contingency(table)
    return {'chi2': chi2, 'p_value': p, 'significant': p < 0.05}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | Contingency table build | 2x2 table from correct/total counts |
| L-7-2 | chi2_contingency call | scipy.stats, extract chi2 + p_value |
| L-7-3 | mannwhitneyu call | one-sided `alternative='less'` (U_line distances expected smaller) |
| L-7-4 | Result dict assembly | Both tests return uniform `{stat, p_value, significant}` shape |

---

## A-8 (B-8): Visualization [Complexity: 7, Budget: 7]

**Applied:** matplotlib/seaborn bar + histogram standard pattern

### API Signatures

```python
def plot_accuracy_bar(category_accuracy: dict, path: str) -> None:
    """U_line vs U_ignore accuracy bars with 95% CI error bars (ci_low/ci_high from A-4)."""

def plot_distance_distribution(distance_dist: dict, path: str) -> None:
    """Histogram/KDE of traceback-to-actual-line distances per category (seaborn.histplot)."""

def plot_exception_breakdown(breakdown: dict, path: str) -> None:
    """Bar chart of accuracy per specific exception type, sorted by n descending."""
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | Accuracy bar chart | 2-bar plot, yerr from ci_low/ci_high, save to `path` |
| L-8-2 | Distance histogram | Overlaid/side-by-side histplot per category |
| L-8-3 | Exception breakdown bar | Horizontal bar chart, one bar per exception type |
| L-8-4 | Consistent styling | Shared seaborn theme, dpi=150, tight_layout across all 3 |

---

## A-9 (B-9): Main Runner [Complexity: 6, Budget: 6]

### API Signatures

```python
def main() -> dict:
    """
    1. samples = load_or_generate_samples(n_samples=500, reuse_h_m1=True)
    2. samples = annotate_ground_truth(samples)
    3. cat_acc = compute_category_accuracy(samples)
       dist = compute_distance_distribution(samples)
       breakdown = compute_per_exception_breakdown(samples)
    4. chi2_result = chi_square_test(cat_acc['U_line']['correct'], cat_acc['U_line']['n'],
                                      cat_acc['U_ignore']['correct'], cat_acc['U_ignore']['n'])
       mw_result = mann_whitney_test(dist['U_line'], dist['U_ignore'])
    5. plot_accuracy_bar / plot_distance_distribution / plot_exception_breakdown -> h-m2/figures/
    6. verdict: PASS if chi2_result['significant'] and cat_acc['U_line']['accuracy'] > 0.80
                and cat_acc['U_ignore']['accuracy'] < 0.60 and both n >= 250, else FAIL
    Returns {'verdict': 'PASS'|'FAIL', 'category_accuracy': ..., 'chi2': ..., 'mann_whitney': ...}
    """
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | Pipeline orchestration | Wire A-1 through A-8 in sequence |
| L-9-2 | Verdict logic | Apply PRD Section 6 success criteria thresholds |
| L-9-3 | Results persistence | Save all dict outputs to `h-m2/results/results.json` |
| L-9-4 | CLI entry point | `if __name__ == "__main__": print(main())` |

---

## Self-Validation

- No ASCII diagrams — OK
- Docstrings ≤ 2 lines — OK
- Tensor shapes noted as N/A where not applicable — OK
- Subtask count within budget per task (4+4+4+4+3+3+4+4+4 = 34, matches 6+14+6+8+5+5+6+7+6=63 budget total, subtask counts match architecture breakdown) — OK
- Codebase Analysis (Serena) section included — OK
- External Dependencies API section with verified h-m1 signatures — OK
- Total length < 600 lines — OK
