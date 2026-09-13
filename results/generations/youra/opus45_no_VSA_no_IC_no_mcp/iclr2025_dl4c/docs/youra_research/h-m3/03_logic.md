# Logic: h-m3

**Hypothesis:** Targeted edits have higher probability of fixing bugs than global rewrites
**Type:** MECHANISM (EXISTENCE-scoped PoC)

Applied: Self-Debug edit-scope classification pattern (localized feedback -> smaller diffs)
Applied: line-diff edit-distance threshold pattern (targeted <= N ops, global > N)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m2)
**Status**: Serena MCP unavailable this run; API signatures verified by direct file read of `h-m2/code/`.
**Analyzed Path**: `docs/youra_research/h-m2/code/`
**Relevant Symbols**: `ExecutionFeedbackRefinement.generate_with_refinement` (model.py:82), `measure_edit_scope` (edit_metrics.py:5), `execute_code`/`ExecResult` (sandbox.py), `ExperimentConfig`/`CONFIG` (config.py)

**Key deviation from architecture doc**: `generate_with_refinement(self, problem, feedback_type)` has **no default value** for `feedback_type` in actual h-m2 code (architecture doc listed `= "detailed"` — incorrect, do not copy). `measure_edit_scope` returns `{lines_changed, total_lines, change_ratio, is_global_rewrite}` — no threshold classification; h-m3 adds `edit_scope: "targeted"|"global"` on top of this via a new module.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-m2/code/model.py (ACTUAL CODE, no default on feedback_type)
class ExecutionFeedbackRefinement:
    def generate_with_refinement(
        self, problem: dict, feedback_type: str
    ) -> tuple[str, bool, int, list[dict]]:
        """Returns (final_code, passed, iteration, edit_records).
        edit_records: list of dicts from measure_edit_scope + iteration/feedback_type keys."""
        ...

# From: h-m2/code/edit_metrics.py (ACTUAL CODE)
def measure_edit_scope(old_code: str, new_code: str) -> dict:
    """Returns {lines_changed: int, total_lines: int, change_ratio: float, is_global_rewrite: bool}."""
    ...

# From: h-m2/code/sandbox.py (ACTUAL CODE)
@dataclass
class ExecResult:
    passed: bool; error_type: str | None; line_number: int | None
    expected: str | None; actual: str | None; stdout: str; stderr: str

def execute_code(code: str, tests: str, timeout: int = 10, mem_limit_mb: int = 512) -> ExecResult: ...

# From: h-m2/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    seed: int = 42
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    max_iterations: int = 3
    timeout_sec: int = 10
    mem_limit_mb: int = 512
    datasets: list[str]  # ["humaneval", "mbpp"]
    results_path: str = "results.json"
    figures_dir: str = "../figures/"
CONFIG = ExperimentConfig()
```

**Verified from**: `h-m2/code/` (actual implementation, read directly — Serena unavailable).
**Copy strategy**: `data.py`, `sandbox.py`, `feedback.py`, `edit_metrics.py`, `config.py` copied verbatim into `h-m3/code/`. Only `model.py::generate_with_refinement` patched (adds `fixed` key to each edit record).

---

## A-1/A-2/A-3: Copy base + patch model.py + edit scope classifier [Complexity: 17, Budget: 1 subtask]

**Applied**: Reuse base modules verbatim; patch only the outcome-tagging gap.

### API Signatures

```python
# h-m3/code/model.py — same file as h-m2, ONLY generate_with_refinement body changes.
# Signature unchanged (no default on feedback_type, matches base):
def generate_with_refinement(
    self, problem: dict, feedback_type: str
) -> tuple[str, bool, int, list[dict]]:
    """edit_records now also carry 'fixed': bool (did the edit's resulting code pass?)."""
    ...
```

```python
# h-m3/code/edit_scope_classify.py — NEW
def classify_edit_scope(edit_record: dict, threshold_lines: int = 5) -> str:
    """'targeted' if lines_changed <= threshold_lines else 'global'."""
    ...

def label_edit_records(edit_records: list[dict], threshold_lines: int = 5) -> list[dict]:
    """Adds 'edit_scope' key in place to each record; returns same list."""
    ...
```

### Pseudo-code (model.py patch — replaces lines 100-106 of base)

```
old_code = code
code = self.refine_code(problem["prompt"], code, feedback)
scope = measure_edit_scope(old_code, code)          # unchanged base call
scope["iteration"] = iteration
scope["feedback_type"] = feedback_type
next_result = execute_code(code, problem["tests"], CONFIG.timeout_sec, CONFIG.mem_limit_mb)
scope["fixed"] = next_result.passed                  # NEW: per-edit outcome label
edit_records.append(scope)
if next_result.passed:
    return code, True, iteration, edit_records        # NEW: early return, avoids duplicate exec next loop
```

### Subtasks [3/3 used within this task group]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1a | Copy base files | Copy data.py, sandbox.py, feedback.py, edit_metrics.py, config.py unchanged |
| L-3-1b | Patch model.py | Apply pseudo-code above to `generate_with_refinement` |
| L-3-1c | edit_scope_classify.py | Implement `classify_edit_scope` + `label_edit_records` |

---

## A-4/A-5: PoC driver + Evaluation [Complexity: 17, Budget: 1 subtask]

**Applied**: Standard PyTorch/pandas PoC harness (single-condition run, no ablation split).

### API Signatures

```python
# h-m3/code/run_poc.py — NEW
POC_SAMPLES = 50  # per dataset

def run_condition(problems: list[dict], refiner: "ExecutionFeedbackRefinement", dataset_name: str) -> list[dict]:
    """Runs generate_with_refinement(feedback_type='detailed') per problem.
    Returns list of {problem_id, dataset, passed, iteration}."""
    ...

def main() -> None:
    """Loads POC_SAMPLES problems/dataset via load_all_problems, runs detailed-feedback
    condition only, collects all edit_records (already carry 'fixed'), calls
    label_edit_records(all_edit_records), saves {'results': [...], 'edit_records': [...]}
    to CONFIG.results_path."""
    ...
```

```python
# h-m3/code/evaluate.py — NEW
def compute_fix_rates(edit_records: list[dict]) -> dict:
    """Returns {'targeted': float, 'global': float, 'targeted_n': int, 'global_n': int}.
    rate = mean('fixed') within each edit_scope group."""
    ...

def plot_fix_rate_bar(rates: dict, out_path: str) -> None: ...
def plot_edit_distance_histogram(edit_records: list[dict], out_path: str) -> None: ...
def plot_fix_prob_vs_distance(edit_records: list[dict], out_path: str) -> None: ...

def main() -> dict:
    """Loads results.json, compute_fix_rates, gate check
    (targeted_fix_rate > global_fix_rate), saves evaluation_summary.json,
    writes 3 figures to CONFIG.figures_dir. Returns evaluation_summary dict."""
    ...
```

### Tensor / Data Shapes

| Variable | Shape/Type | Note |
|----------|-----------|------|
| edit_records | `list[dict]` | keys: lines_changed, total_lines, change_ratio, is_global_rewrite, iteration, feedback_type, fixed, edit_scope |
| rates | `dict[str, float\|int]` | targeted/global rate + n |

### Subtasks [2/2 used within this task group]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-2a | run_poc.py | `run_condition` + `main`, detailed-feedback only, save results.json |
| L-3-2b | evaluate.py | `compute_fix_rates`, gate check, 3 plots, evaluation_summary.json |

---

## Total Subtask Budget: 2 used / 2 allocated
