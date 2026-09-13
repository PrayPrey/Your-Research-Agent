# Architecture: H-M2

**Applied**: Feedback-granularity ablation pattern (Self-Debug/Reflexion) + difflib edit-scope metric pattern (CodeRL-style)

**Hypothesis Type**: MECHANISM
**Codebase**: h-e1/code/ (reused execution/model/data infra) + new edit-metrics module

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Actual H-E1 code inspected directly (Serena tool unavailable in this run; used direct file read as substitute, per "trust actual code over specs" rule).
**Analyzed Path**: `h-e1/code/` (sandbox.py, model.py, feedback.py, data.py, config.py, train.py, evaluate.py)
**Findings**: H-E1's `ExecutionFeedbackRefinement.generate_with_refinement(problem, feedback_type)` branches on `feedback_type == "execution"` vs `"random"`. H-M2 reuses this class verbatim, only changing feedback_type values to `"detailed"`/`"binary"` and swapping `format_execution_feedback`/`generate_random_feedback` for new detailed/binary formatters. `ExecResult` dataclass (sandbox.py) already carries `error_type, line_number, expected, actual, stderr` — sufficient for detailed formatting (traceback via `stderr.splitlines()[-3:]`). No H-E1 code requires modification; only `feedback.py` is replaced and `train.py`/`evaluate.py` are new (edit-scope focus vs pass@1 focus).

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| ExecResult, execute_code | `from sandbox import ExecResult, execute_code` | `h-e1/code/sandbox.py` |
| ExecutionFeedbackRefinement | `from model import ExecutionFeedbackRefinement` | `h-e1/code/model.py` |
| load_all_problems | `from data import load_all_problems` | `h-e1/code/data.py` |
| ExperimentConfig | `from config import CONFIG` | `h-e1/code/config.py` (extend, don't reuse directly — see below) |

**Verified from**: `h-e1/code/` (actual implementation, not 03_architecture.md spec)

**Note**: `sandbox.py`, `model.py`, `data.py` copied unmodified into `h-m2/code/`. `model.py`'s `generate_with_refinement` already accepts arbitrary `feedback_type` string and only needs the `if feedback_type == "execution"` branch condition changed to `"detailed"` (binary branch reuses existing `else`). This one-line edit is done in the copy.

---

## File Structure

- `h-m2/code/config.py` — new config (feedback_types = ["detailed","binary"])
- `h-m2/code/sandbox.py` — copied from H-E1 (unmodified)
- `h-m2/code/feedback.py` — NEW: detailed + binary formatters
- `h-m2/code/model.py` — copied from H-E1, `"execution"`→`"detailed"` branch rename
- `h-m2/code/data.py` — copied from H-E1 (unmodified)
- `h-m2/code/edit_metrics.py` — NEW: difflib-based edit scope measurement
- `h-m2/code/train.py` — NEW: runs both conditions, logs edit metrics per iteration
- `h-m2/code/evaluate.py` — NEW: aggregates edit-scope stats, t-test, figures

---

## Modules

### feedback.py (`h-m2/code/feedback.py`)

**Dependencies**: sandbox.ExecResult

```python
def format_detailed_feedback(result: ExecResult) -> str: ...
def format_binary_feedback(result: ExecResult) -> str: ...
```

### edit_metrics.py (`h-m2/code/edit_metrics.py`)

**Dependencies**: difflib (stdlib)

```python
def measure_edit_scope(old_code: str, new_code: str) -> dict: ...
    # returns: lines_changed, total_lines, change_ratio, is_global_rewrite

def aggregate_edit_metrics(edit_records: list[dict]) -> dict: ...
    # returns: detailed_avg_lines_changed, binary_avg_lines_changed,
    #          detailed_global_rewrite_rate, binary_global_rewrite_rate,
    #          edit_scope_ratio, p_value
```

### model.py (`h-m2/code/model.py`) — modified copy of H-E1

**Dependencies**: sandbox, feedback, config

```python
class ExecutionFeedbackRefinement:
    def __init__(self, model_id=None, max_iterations=None, temperature=None,
                 max_tokens=None, top_p=None): ...
    def initial_generate(self, prompt: str) -> str: ...
    def refine_code(self, prompt: str, code: str, feedback: str) -> str: ...
    def generate_with_refinement(
        self, problem: dict, feedback_type: str  # "detailed" | "binary"
    ) -> tuple[str, bool, int, list[dict]]: ...
        # returns final_code, passed, iterations_used, edit_records (list of measure_edit_scope dicts)
```

### config.py (`h-m2/code/config.py`)

```python
@dataclass
class ExperimentConfig:
    seed: int = 42
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    max_iterations: int = 3
    temperature: float = 0.2
    max_tokens: int = 512
    top_p: float = 0.95
    timeout_sec: int = 10
    mem_limit_mb: int = 512
    datasets: list[str] = field(default_factory=lambda: ["humaneval", "mbpp"])
    feedback_types: list[str] = field(default_factory=lambda: ["detailed", "binary"])
    results_path: str = "results.json"
    figures_dir: str = "../figures/"
CONFIG = ExperimentConfig()
```

### train.py (`h-m2/code/train.py`)

**Dependencies**: config, data, model

```python
def run_condition(problems: list[dict], refiner, feedback_type: str, dataset_name: str) -> list[dict]: ...
def main() -> None: ...  # loads datasets, model, runs both conditions, dumps results.json
```

### evaluate.py (`h-m2/code/evaluate.py`)

**Dependencies**: config, edit_metrics, scipy.stats (t-test), matplotlib

```python
def compute_pass_at_1(results: list[dict]) -> float: ...
def run_ttest(detailed_lines: list[int], binary_lines: list[int]) -> tuple[float, float]: ...
def plot_edit_scope_boxplot(detailed, binary, out_path: str) -> None: ...
def plot_change_ratio_histogram(detailed, binary, out_path: str) -> None: ...
def plot_global_rewrite_bar(metrics: dict, out_path: str) -> None: ...
def main() -> None: ...  # aggregates, gate check (edit_scope_ratio < 0.9), saves summary.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Copy H-E1 infra | Copy sandbox.py, data.py unmodified; verify imports | 4 | 1+1+1+1 |
| A-2 | Config setup | New config.py with detailed/binary feedback_types | 3 | 1+1+1+0 |
| A-3 | Feedback formatters | Implement format_detailed_feedback, format_binary_feedback | 5 | 2+1+2+0 |
| A-4 | Edit scope metrics | Implement measure_edit_scope with difflib | 6 | 2+1+2+1 |
| A-5 | Model adaptation | Copy+adapt model.py: detailed/binary branch, embed edit_scope measurement per iteration | 9 | 3+3+2+1 |
| A-6 | Aggregate metrics | Implement aggregate_edit_metrics with t-test | 6 | 2+2+2+0 |
| A-7 | Training loop | train.py: run both conditions across HumanEval+MBPP, log JSONL | 8 | 3+3+1+1 |
| A-8 | Evaluation + gate check | evaluate.py: compute edit_scope_ratio, verify_mechanism_activation, gate logic | 8 | 3+2+2+1 |
| A-9 | Visualization | 3 required figures (boxplot, histogram, bar chart) | 7 | 3+2+1+1 |
| A-10 | End-to-end run | Full experiment execution, results.json + evaluation_summary.json | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-5], Low(4-8): [A-1, A-2, A-3, A-4, A-6, A-7, A-8, A-9, A-10]
