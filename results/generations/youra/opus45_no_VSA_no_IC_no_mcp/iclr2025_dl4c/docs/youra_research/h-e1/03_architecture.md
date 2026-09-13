# Architecture: H-E1 (EXISTENCE / PoC)

**Applied**: Self-Debug iterative refinement pattern (generate → execute → feedback → refine)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - no existing codebase
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no prior hypothesis code to reuse.

---

## File Structure (Minimal — EXISTENCE)

```
h-e1/code/
  data.py         # dataset loading (HumanEval, MBPP)
  sandbox.py       # execution sandbox (subprocess, timeout, memory limit)
  feedback.py       # execution feedback + random feedback formatting
  model.py         # baseline + proposed refinement wrapper (CodeLlama-7B-Instruct)
  train.py         # run loop: both conditions over both datasets
  evaluate.py       # pass@1 computation, mechanism verification, figures
  config.py        # fixed config (seed, temp, max_iter, timeout)
```

---

## Modules

### data.py

**Dependencies**: None (datasets library)

```python
def load_humaneval() -> list[dict]: ...     # {task_id, prompt, test, entry_point}
def load_mbpp() -> list[dict]: ...          # {task_id, text, code, test_list} -> normalized
def normalize_problem(raw: dict, source: str) -> dict: ...  # {prompt, tests, entry_point}
```

### sandbox.py

**Dependencies**: None (subprocess, stdlib)

```python
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
```

### feedback.py

**Dependencies**: sandbox.ExecResult

```python
def format_execution_feedback(result: ExecResult) -> str: ...   # "Error: {type} at line {n}\nExpected: ..\nActual: .."
def generate_random_feedback() -> str: ...                      # random.choice(templates)
```

### model.py

**Dependencies**: sandbox, feedback

```python
class ExecutionFeedbackRefinement:
    def __init__(self, model_id: str = "codellama/CodeLlama-7b-Instruct-hf",
                 max_iterations: int = 3, temperature: float = 0.2,
                 max_tokens: int = 512, top_p: float = 0.95): ...
    def initial_generate(self, prompt: str) -> str: ...
    def refine_code(self, prompt: str, code: str, feedback: str) -> str: ...
    def generate_with_refinement(self, problem: dict, feedback_type: str) -> tuple[str, bool, int, list[str]]: ...
        # returns final_code, passed, iterations_used, feedback_log
```

### config.py

**Dependencies**: None

```python
SEED = 42
MODEL_ID = "codellama/CodeLlama-7b-Instruct-hf"
MAX_ITERATIONS = 3
TEMPERATURE = 0.2
MAX_TOKENS = 512
TOP_P = 0.95
TIMEOUT_SEC = 10
MEM_LIMIT_MB = 512
```

### train.py

**Dependencies**: data, model, config

```python
def run_condition(problems: list[dict], refiner: "ExecutionFeedbackRefinement",
                   feedback_type: str) -> list[dict]: ...  # per-problem results
def main() -> None: ...  # loads data, runs condition A (execution) and B (random), saves results.json
```

### evaluate.py

**Dependencies**: train results, sandbox

```python
def compute_pass_at_1(results: list[dict]) -> float: ...
def compute_pass_at_1_by_iteration(results: list[dict], k: int) -> dict[int, float]: ...
def verify_mechanism_activation(result_exec: dict, result_random: dict) -> bool: ...
def plot_gate_comparison(pass_exec: float, pass_random: float, out_path: str) -> None: ...
def plot_iteration_progression(results_exec: list[dict], out_path: str) -> None: ...
def plot_per_problem_heatmap(results_exec: list[dict], results_random: list[dict], out_path: str) -> None: ...
def main() -> None: ...  # loads results.json, computes metrics, generates figures to h-e1/figures/
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Load & normalize HumanEval + MBPP | 6 | 2+1+1+2 |
| A-2 | Execution sandbox | Subprocess exec, timeout, mem limit, error parsing | 12 | 3+2+4+3 |
| A-3 | Feedback generation | Execution feedback formatter + random baseline | 5 | 2+1+1+1 |
| A-4 | Model wrapper | CodeLlama load, generate, refine methods | 10 | 3+3+2+2 |
| A-5 | Refinement loop | Iterative loop wiring model+sandbox+feedback | 10 | 2+3+3+2 |
| A-6 | Run experiment | train.py: both conditions x both datasets, save results | 8 | 2+3+1+2 |
| A-7 | Evaluation & mechanism check | pass@1, mechanism verification assertions | 7 | 2+2+2+1 |
| A-8 | Figures | Gate comparison, iteration progression, heatmap | 6 | 2+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4, A-5, A-6], Low(4-8): [A-1, A-3, A-7, A-8]
