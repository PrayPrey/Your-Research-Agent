# Logic: H-M2

**Hypothesis Type**: MECHANISM
**Budget**: 2 subtasks max

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from actual H-E1 code (Serena unavailable; direct Read used per fallback rule).
**Analyzed Path**: `h-e1/code/sandbox.py`, `h-e1/code/model.py`, `h-e1/code/feedback.py`
**Relevant Symbols**: `ExecResult` (dataclass), `execute_code()`, `ExecutionFeedbackRefinement.generate_with_refinement()`, `format_execution_feedback()`

**Critical correction vs specs (03_architecture.md / 02c_experiment_brief.md)**:
- `ExecResult` has **no** `error_message` or `traceback` fields. Actual fields: `passed, error_type, line_number, expected, actual, stdout, stderr`. Detailed feedback must use `stderr.splitlines()[-3:]` for traceback, not `result.traceback`.
- `generate_with_refinement` in H-E1 returns `feedback_log: list[str]`, **not** `edit_records: list[dict]`. H-M2's model.py must be adapted to additionally track edit-scope dicts per iteration (new 4th return element renamed `edit_records`).
- `feedback_type` branch in H-E1 is `if feedback_type == "execution": ... else: generate_random_feedback()`. H-M2 renames to `"detailed"` branch calling `format_detailed_feedback`, else branch calling `format_binary_feedback` (replaces random baseline — H-M2 has no random condition).

---

## External Dependencies API (Verified from H-E1 Actual Code)

```python
# From: h-e1/code/sandbox.py (ACTUAL CODE - reused unmodified)
@dataclass
class ExecResult:
    passed: bool
    error_type: str | None
    line_number: int | None
    expected: str | None
    actual: str | None
    stdout: str
    stderr: str

def execute_code(code: str, tests: str, timeout: int = 10, mem_limit_mb: int = 512) -> ExecResult: ...

# From: h-e1/code/model.py (base class pattern, adapted below)
class ExecutionFeedbackRefinement:
    def __init__(self, model_id=None, max_iterations=None, temperature=None,
                 max_tokens=None, top_p=None): ...
    def initial_generate(self, prompt: str) -> str: ...
    def refine_code(self, prompt: str, code: str, feedback: str) -> str: ...
```

**Verified from**: `h-e1/code/sandbox.py`, `h-e1/code/model.py` (actual implementation).

---

## A-3+A-4: Feedback Formatters + Edit Scope Metrics [Complexity: 11, Budget: 2 subtasks]

**Applied**: difflib unified_diff line-counting pattern (CodeRL-style, stdlib only)

### API Signatures

```python
# feedback.py
from sandbox import ExecResult

def format_detailed_feedback(result: ExecResult) -> str:
    """Full error trace with localization."""
    ...

def format_binary_feedback(result: ExecResult) -> str:
    """Pass/fail only, no localization."""
    ...
```

```python
# edit_metrics.py
def measure_edit_scope(old_code: str, new_code: str) -> dict:
    """difflib-based line diff. Returns lines_changed, total_lines, change_ratio, is_global_rewrite."""
    ...

def aggregate_edit_metrics(edit_records: list[dict]) -> dict:
    """Split by feedback_type, compute avg lines_changed, rewrite rate, t-test p_value."""
    ...
```

### Pseudo-code

```
format_detailed_feedback(result):
    if result.passed: return "Test passed."
    lines = [f"Error: {result.error_type} at line {result.line_number}"]
    if result.expected and result.actual:
        lines += [f"Expected: {result.expected}", f"Actual: {result.actual}"]
    tb = result.stderr.splitlines()[-3:]  # last 3 lines, no traceback field exists
    lines.append("Traceback: " + " | ".join(tb))
    return "\n".join(lines)

format_binary_feedback(result):
    return "Test passed." if result.passed else "Test failed."

measure_edit_scope(old_code, new_code):
    diff = difflib.unified_diff(old_code.splitlines(), new_code.splitlines())
    lines_changed = count(d for d in diff if d[0] in '+-' and d[:3] not in ('+++','---'))
    total_lines = max(len(old_code.splitlines()), 1)
    change_ratio = lines_changed / total_lines
    return {lines_changed, total_lines, change_ratio, is_global_rewrite: change_ratio > 0.5}

aggregate_edit_metrics(edit_records):
    detailed = [e for e in edit_records if e["feedback_type"] == "detailed"]
    binary   = [e for e in edit_records if e["feedback_type"] == "binary"]
    d_avg, b_avg = mean(detailed.lines_changed), mean(binary.lines_changed)
    _, p_value = scipy.stats.ttest_ind(detailed.lines_changed, binary.lines_changed)
    return {detailed_avg_lines_changed: d_avg, binary_avg_lines_changed: b_avg,
            detailed_global_rewrite_rate: mean(detailed.is_global_rewrite),
            binary_global_rewrite_rate: mean(binary.is_global_rewrite),
            edit_scope_ratio: d_avg / max(b_avg, 1), p_value: p_value}
```

### Tensor Shapes

N/A — no tensors; all string/scalar/dict operations.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M2-1 | feedback.py | format_detailed_feedback, format_binary_feedback (uses stderr, not nonexistent traceback field) |
| L-M2-2 | edit_metrics.py + model.py adaptation | measure_edit_scope, aggregate_edit_metrics; adapt `generate_with_refinement` to call measure_edit_scope per iteration and return `edit_records: list[dict]` as 4th tuple element (replacing H-E1's `feedback_log: list[str]`) |

---

## model.py Adaptation (Reference for L-M2-2)

```python
# h-m2/code/model.py — copied from h-e1/code/model.py, then:
# 1. import: from feedback import format_detailed_feedback, format_binary_feedback
# 2. import: from edit_metrics import measure_edit_scope
# 3. generate_with_refinement signature unchanged; body adapted:

def generate_with_refinement(
    self, problem: dict, feedback_type: str  # "detailed" | "binary"
) -> tuple[str, bool, int, list[dict]]:
    # returns final_code, passed, iterations_used, edit_records
    code = self.initial_generate(problem["prompt"])
    edit_records = []
    for iteration in range(1, self.max_iterations + 1):
        result = execute_code(code, problem["tests"], CONFIG.timeout_sec, CONFIG.mem_limit_mb)
        if result.passed:
            return code, True, iteration, edit_records
        feedback = (format_detailed_feedback(result) if feedback_type == "detailed"
                    else format_binary_feedback(result))
        old_code = code
        code = self.refine_code(problem["prompt"], code, feedback)
        scope = measure_edit_scope(old_code, code)
        scope["iteration"] = iteration
        scope["feedback_type"] = feedback_type
        edit_records.append(scope)
    result = execute_code(code, problem["tests"], CONFIG.timeout_sec, CONFIG.mem_limit_mb)
    return code, result.passed, self.max_iterations, edit_records
```
