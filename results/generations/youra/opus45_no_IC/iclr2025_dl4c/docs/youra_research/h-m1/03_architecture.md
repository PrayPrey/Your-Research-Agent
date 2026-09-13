# Architecture: H-M1 (Execution Trace → Token Classification)

**Type:** MECHANISM validation (no training)
**Applied:** stdlib-first tracing pattern (sys.settrace + tokenizer offset_mapping), no custom dependencies

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** No existing codebase — H-M1 is a standalone validation experiment. Serena skipped per rules (green-field acceptable).
**Analyzed Path:** N/A
**Findings:** New implementation from scratch, stdlib only (sys, ast, tokenize) + transformers tokenizer + sklearn.metrics.

---

## File Organization

```
h-m1/code/
  trace_collector.py      # ExecutionTraceCollector
  token_mapper.py          # LineToTokenMapper
  classifier.py             # TokenClassifier
  ground_truth.py           # GroundTruthGenerator
  overhead_bench.py         # OverheadBenchmark
  metrics.py                 # ValidationMetrics
  data_loader.py             # HumanEval/MBPP loading + code sample generation
  run_experiment.py          # main entry point, orchestrates full pipeline
  visualize.py                # figure generation (4 required figures)
  config.py                   # fixed experiment config
```

---

## Modules

### ExecutionTraceCollector (`trace_collector.py`)

**Dependencies**: None (stdlib `sys`)

```python
class ExecutionTraceCollector:
    def __init__(self): ...
    def trace_function(self, frame, event, arg) -> Callable: ...
    def collect_trace(self, code_str: str, test_input: str, timeout: float = 5.0) -> set[int]: ...
```

### LineToTokenMapper (`token_mapper.py`)

**Dependencies**: transformers tokenizer (offset_mapping)

```python
class LineToTokenMapper:
    def __init__(self, tokenizer): ...
    def build_line_map(self, code_str: str, tokens: list) -> dict[int, int]: ...  # token_idx -> line_num
    def map_offsets_to_lines(self, code_str: str, offset_mapping: list[tuple[int,int]]) -> dict[int, int]: ...
```

### TokenClassifier (`classifier.py`)

**Dependencies**: ExecutionTraceCollector, LineToTokenMapper

```python
class TokenClassifier:
    def __init__(self, mapper: LineToTokenMapper): ...
    def classify_tokens(self, tokens: list, line_map: dict, executed_lines: set[int]) -> list[int]: ...
```

### GroundTruthGenerator (`ground_truth.py`)

**Dependencies**: `ast`, `coverage` (optional cross-check, stdlib-adjacent)

```python
class GroundTruthGenerator:
    def __init__(self): ...
    def ast_executable_lines(self, code_str: str) -> set[int]: ...
    def coverage_cross_validate(self, code_str: str, test_input: str) -> set[int]: ...
    def generate(self, code_str: str, test_input: str) -> set[int]: ...
```

### OverheadBenchmark (`overhead_bench.py`)

**Dependencies**: ExecutionTraceCollector, `time`

```python
class OverheadBenchmark:
    def __init__(self, collector: ExecutionTraceCollector): ...
    def measure(self, code_str: str, test_input: str) -> dict: ...  # {trace_time, baseline_time, overhead}
    def run_batch(self, samples: list[tuple[str,str]]) -> dict: ...  # mean/median/p95
```

### ValidationMetrics (`metrics.py`)

**Dependencies**: sklearn.metrics

```python
class ValidationMetrics:
    def __init__(self): ...
    def token_accuracy(self, pred_mask: list[int], gt_mask: list[int]) -> float: ...
    def precision_recall(self, pred_mask: list[int], gt_mask: list[int]) -> dict: ...
    def line_coverage_accuracy(self, pred_lines: set[int], gt_lines: set[int]) -> float: ...
    def confusion_matrix(self, pred_mask: list[int], gt_mask: list[int]) -> Any: ...
```

### Data / Generation (`data_loader.py`)

**Dependencies**: datasets, transformers (CodeLlama-7B-Instruct)

```python
def load_problems() -> list[dict]: ...  # HumanEval(164) + MBPP test(500)
def generate_code_sample(model, tokenizer, problem: dict) -> str: ...
```

### Orchestration (`run_experiment.py`)

**Dependencies**: all modules above

```python
def main(config_path: str = "config.py") -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Load HumanEval + MBPP, generate code w/ CodeLlama-7B | 8 | 2+2+2+2 |
| A-2 | ExecutionTraceCollector | sys.settrace wrapper, exception-safe, timeout | 9 | 2+1+3+3 |
| A-3 | LineToTokenMapper | offset_mapping → line map, multi-line handling | 10 | 3+2+3+2 |
| A-4 | TokenClassifier | Binary mask generation from trace + line map | 6 | 2+2+1+1 |
| A-5 | GroundTruthGenerator | AST executable-line analysis + coverage.py cross-check | 9 | 3+2+3+1 |
| A-6 | OverheadBenchmark | Timed trace vs baseline over 100+ samples, mean/median/p95 | 6 | 2+2+1+1 |
| A-7 | ValidationMetrics | Accuracy/precision/recall/confusion matrix via sklearn | 5 | 2+1+1+1 |
| A-8 | Pipeline orchestration | Wire all modules, run on 664 problems, seed=42 | 8 | 2+3+1+2 |
| A-9 | Visualization | 4 required figures (gate metric, confusion matrix, overhead hist, coverage heatmap) | 7 | 2+2+1+2 |
| A-10 | Gate check + report | Compute PASS/FAIL vs >95% accuracy, <20x overhead thresholds | 4 | 1+1+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-3, A-5], Low(4-8): [A-1, A-4, A-6, A-7, A-8, A-9, A-10]

---

## Notes

- No neural network training — CodeLlama-7B used only for code sample generation (inference).
- Sandboxed exec: run generated code in subprocess with resource limits for safety (timeout in `collect_trace`).
- Fixed seed 42 per NFR-3.
