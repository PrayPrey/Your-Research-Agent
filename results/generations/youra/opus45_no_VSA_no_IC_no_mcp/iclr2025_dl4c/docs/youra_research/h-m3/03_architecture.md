# Architecture: h-m3

**Hypothesis:** Targeted edits have higher probability of fixing bugs than global rewrites
**Type:** MECHANISM (EXISTENCE-scoped PoC per experiment brief)

Applied: Self-Debug edit-scope classification pattern (localized feedback -> smaller diffs)
Applied: AST/line-diff edit-distance threshold pattern (targeted <= N ops, global > N)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m2)
**Status**: Patterns found from base code — read directly via file tool (Serena MCP unavailable in this run; PRD/brief for h-m2 confirm architecture matches implementation)
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Findings**: h-m2 measures edit scope with **difflib line-diff**, NOT tree-sitter AST (`edit_metrics.py::measure_edit_scope` returns `lines_changed`, `change_ratio`, `is_global_rewrite`). `edit_records` already contain `lines_changed`/`iteration`/`feedback_type` per refinement step, but NOT fix outcome per edit. `model.py::generate_with_refinement` returns `(code, passed, iteration, edit_records)` — final pass/fail is per-problem, not per-edit-step. h-m3 must patch model call site to tag each edit record with the outcome of the *next* execution to get per-edit fix/not-fixed labels. PRD requests tree-sitter AST distance (threshold=5); given base code uses line-diff and brief's fallback clause allows difflib, we reuse h-m2's `measure_edit_scope`/threshold-based classifier instead of introducing tree-sitter — smaller diff, same causal question (edit scope -> fix rate).

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_all_problems | `from data import load_all_problems` | `h-m2/code/data.py` |
| execute_code, ExecResult | `from sandbox import execute_code, ExecResult` | `h-m2/code/sandbox.py` |
| format_detailed_feedback | `from feedback import format_detailed_feedback` | `h-m2/code/feedback.py` |
| measure_edit_scope | `from edit_metrics import measure_edit_scope` | `h-m2/code/edit_metrics.py` |
| ExecutionFeedbackRefinement | `from model import ExecutionFeedbackRefinement` | `h-m2/code/model.py` |
| CONFIG | `from config import CONFIG` | `h-m2/code/config.py` |

**Verified from**: `h-m2/code/` (actual implementation, read directly).
**Copy strategy**: h-m3 copies `data.py`, `sandbox.py`, `feedback.py`, `edit_metrics.py`, `config.py`, `model.py` verbatim into `h-m3/code/` (per-hypothesis isolation convention used by h-m2), then adds new files below. Only `model.py::generate_with_refinement` needs a small patch to record per-edit fix outcome.

---

## Files

- `h-m3/code/data.py`, `sandbox.py`, `feedback.py`, `edit_metrics.py`, `config.py` — copied unchanged from h-m2
- `h-m3/code/model.py` — copied from h-m2, `generate_with_refinement` patched to tag each edit record with `fixed: bool` (result of executing code produced by that edit)
- `h-m3/code/edit_scope_classify.py` — NEW: classify edit records as targeted/global by threshold
- `h-m3/code/run_poc.py` — NEW: PoC driver, reuses detailed-feedback condition only (single condition, no detailed/binary split needed for this hypothesis)
- `h-m3/code/evaluate.py` — NEW: fix-rate comparison, gate check, figures

---

## Module: model.py patch (`h-m3/code/model.py`)

**Dependencies**: sandbox, feedback, edit_metrics, config

```python
# generate_with_refinement — same signature, edit_records now include "fixed"
def generate_with_refinement(self, problem: dict, feedback_type: str = "detailed") -> tuple[str, bool, int, list[dict]]: ...
# Inside loop, after producing new `code` from refine_code():
#   next_result = execute_code(code, problem["tests"], ...)
#   scope["fixed"] = next_result.passed
#   edit_records.append(scope)
#   if next_result.passed: return code, True, iteration, edit_records
```

---

## Module: EditScopeClassifier (`h-m3/code/edit_scope_classify.py`)

**Dependencies**: none (pure function over edit_records from edit_metrics.measure_edit_scope)

```python
def classify_edit_scope(edit_record: dict, threshold_lines: int = 5) -> str:
    """'targeted' if lines_changed <= threshold_lines else 'global'."""
    ...

def label_edit_records(edit_records: list[dict], threshold_lines: int = 5) -> list[dict]:
    """Adds 'edit_scope' key to each record in place; returns records."""
    ...
```

---

## Module: PoC Driver (`h-m3/code/run_poc.py`)

**Dependencies**: config, data, model, edit_scope_classify

```python
POC_SAMPLES = 50  # per dataset, matches h-m2 PoC scale

def run_condition(problems: list[dict], refiner, dataset_name: str) -> list[dict]: ...
def main() -> None:
    """Loads problems, runs detailed-feedback refinement only,
    labels edit_scope per record, saves results.json with
    'results' and 'edit_records' (each edit_record has fixed + edit_scope)."""
```

---

## Module: Evaluation (`h-m3/code/evaluate.py`)

**Dependencies**: config, edit_scope_classify

```python
def compute_fix_rates(edit_records: list[dict]) -> dict:
    """Returns {'targeted': rate, 'global': rate, 'targeted_n': int, 'global_n': int}."""
    ...

def plot_fix_rate_bar(rates: dict, out_path: str) -> None: ...
def plot_edit_distance_histogram(edit_records: list[dict], out_path: str) -> None: ...
def plot_fix_prob_vs_distance(edit_records: list[dict], out_path: str) -> None: ...

def main() -> dict:
    """Loads results.json, computes fix rates, gate check
    (targeted_fix_rate > global_fix_rate), saves evaluation_summary.json,
    generates 3 figures to CONFIG.figures_dir."""
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Copy base modules | Copy data.py, sandbox.py, feedback.py, edit_metrics.py, config.py unchanged from h-m2 | 4 | 1+1+1+1 |
| A-2 | Patch model.py | Add `fixed` outcome to each edit record in generate_with_refinement | 8 | 2+2+3+1 |
| A-3 | Edit scope classifier | Implement classify_edit_scope + label_edit_records using lines_changed threshold | 5 | 1+1+2+1 |
| A-4 | PoC driver | run_poc.py: load 50/dataset, run detailed-feedback refinement, label edits, save results.json | 9 | 2+3+2+2 |
| A-5 | Evaluation + gate | evaluate.py: compute_fix_rates, gate check, 3 figures, summary json | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4], Low(4-8): [A-1, A-2, A-3, A-5]
