# Architecture: H-M1 — Error Traces Contain Counterfactual Information

**Type**: MECHANISM | **Gate**: MUST_WORK

Applied: pipeline-stage pattern (injector → executor → parser → annotator → scorer)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base_hypothesis folder present for h-m1.

---

## File Structure

```
h-m1/code/
  bug_injector.py
  sandbox_executor.py
  trace_parser.py
  cf_annotator.py
  metrics.py
  data_loader.py
  run_pipeline.py
  config.py
h-m1/data/
  buggy_samples.jsonl
  execution_traces.jsonl
  cf_annotations.jsonl
h-m1/results/
  cf_scores.csv
  analysis_report.md
```

---

## Modules

### DataLoader (`data_loader.py`)

**Dependencies**: datasets

```python
def load_humaneval() -> list[dict]: ...
def load_mbpp() -> list[dict]: ...
def load_all_problems() -> list[dict]:  # unified schema: id, prompt, code, tests
    ...
```

### BugInjector (`bug_injector.py`)

**Dependencies**: ast, config (seed)

```python
BUG_TYPES = ("syntax", "logic", "type", "off_by_one")

class BugInjector:
    def __init__(self, seed: int): ...
    def inject(self, correct_code: str, bug_type: str) -> tuple[str, int, str]:
        # returns (buggy_code, bug_line, bug_description)
        ...
    def inject_all_types(self, problem: dict) -> list[dict]:
        # one buggy sample per BUG_TYPES entry
        ...
```

### SandboxExecutor (`sandbox_executor.py`)

**Dependencies**: docker, subprocess

```python
class ExecutionResult:
    stdout: str; stderr: str; exit_code: int; traceback: str; timed_out: bool

class SandboxExecutor:
    def __init__(self, timeout_s: int = 10, memory_mb: int = 512): ...
    def run(self, code: str, tests: str) -> ExecutionResult: ...
```

### TraceParser (`trace_parser.py`)

**Dependencies**: re

```python
class ParsedTrace:
    line_numbers: list[int]; expected: str | None; actual: str | None
    type_info: str | None; variable_state: dict; call_chain: list[str]

class TraceParser:
    def parse(self, result: "ExecutionResult") -> ParsedTrace: ...
```

### CounterfactualAnnotator (`cf_annotator.py`)

**Dependencies**: TraceParser output

```python
class CFAnnotation:
    has_line: bool; has_expected: bool; has_actual: bool
    has_type_info: bool; has_variable_state: bool
    identifies_root_cause: bool
    cf_score: float  # sum(5 bools)/5

class CounterfactualAnnotator:
    def annotate(self, trace: "ParsedTrace", bug_line: int) -> CFAnnotation: ...
```

### MetricsCalculator (`metrics.py`)

**Dependencies**: pandas, scipy, numpy

```python
def cf_score_distribution(df) -> dict: ...  # mean, median, std, p70
def hypothesis_test(df, threshold: float = 0.4) -> dict: ...  # one-sample t-test
def cf_by_bug_type_anova(df) -> dict: ...
def root_cause_accuracy(df) -> dict: ...  # overall + by bug_type
def cohens_kappa(human_labels, auto_labels) -> float: ...
```

### Pipeline (`run_pipeline.py`)

**Dependencies**: all modules above, pyyaml config

```python
def run_bug_injection() -> None: ...   # writes buggy_samples.jsonl
def run_execution() -> None: ...       # writes execution_traces.jsonl
def run_annotation() -> None: ...      # writes cf_annotations.jsonl + cf_scores.csv
def run_analysis() -> None: ...        # writes analysis_report.md
def main(stage: str = "all") -> None: ...
```

### Config (`config.py`)

```python
SEED = 42
TIMEOUT_S = 10
MEMORY_MB = 512
BUG_TYPES = ("syntax", "logic", "type", "off_by_one")
CF_THRESHOLD = 0.4
DATA_DIR = "h-m1/data"
RESULTS_DIR = "h-m1/results"
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Load HumanEval + MBPP, unify schema | 6 | 2+1+1+2 |
| A-2 | Bug injector: syntax/logic | Implement 2 bug-type transforms + validation | 11 | 3+2+4+2 |
| A-3 | Bug injector: type/off-by-one | Implement remaining 2 bug-type transforms | 9 | 2+2+3+2 |
| A-4 | Sandbox executor | Docker-based execution w/ timeout, memory limit, pytest capture | 14 | 3+4+3+4 |
| A-5 | Trace parser | Regex/heuristic extraction of line, expected/actual, type, vars | 13 | 3+2+5+3 |
| A-6 | CF annotator | Compute 5-feature CF vector + root cause match + CF_score | 8 | 2+3+2+1 |
| A-7 | Metrics calculator | Distribution stats, hypothesis test, ANOVA, kappa | 10 | 3+2+3+2 |
| A-8 | Full pipeline runner | Orchestrate stages A-1..A-7 end-to-end, CLI, checkpointing | 9 | 2+4+1+2 |
| A-9 | Human annotation harness | Sample 100 traces, export for annotation, compute kappa vs auto | 7 | 2+2+1+2 |
| A-10 | Run experiment + analysis report | Execute full 2,656-sample run, generate analysis_report.md | 8 | 1+3+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-2, A-3, A-5, A-7, A-8], Low(4-8): [A-1, A-6, A-9, A-10]

---

## External Dependencies

None — green-field project, no base hypothesis code to reuse.
