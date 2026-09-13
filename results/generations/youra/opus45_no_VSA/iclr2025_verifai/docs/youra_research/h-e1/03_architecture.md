# Architecture: H-E1 (Feedback Ordering Effect in LLM Code Repair)

**Type**: EXISTENCE (PoC) | **Applied**: sequential-pipeline-with-two-branch-conditions (standard pattern, KB search returned no directly relevant DL-repair results; using established repair-loop pattern from PRD/brief)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Structure (Minimal - EXISTENCE)

```
h-e1/code/
  config.py          # fixed experiment config (models, tokens, iterations)
  data.py             # HumanEval + MBPP loading
  llm.py              # GPT-4o-mini generation + repair calls
  feedback.py         # static (pylint+mypy) + execution feedback, truncation
  sandbox.py          # sandboxed test execution with timeout
  repair_loop.py       # 3-iteration repair loop, condition A/B branching
  metrics.py           # pass@1, bootstrap CI, McNemar test
  run_experiment.py    # main entrypoint, orchestrates full pipeline
  results/             # output artifacts (jsonl/json)
```

---

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
@dataclass
class ExperimentConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_tokens: int = 2048
    feedback_token_budget: int = 500  # per feedback type
    n_iterations: int = 3
    exec_timeout_s: int = 10
    exec_retries: int = 3  # majority vote
    seed: int = 42
```

### Data Loader (`data.py`)

**Dependencies**: Config

```python
@dataclass
class Problem:
    problem_id: str
    source: str  # "humaneval" | "mbpp"
    prompt: str
    tests: str
    entry_point: str

def load_problems(seed: int) -> list[Problem]: ...
```

### LLM Client (`llm.py`)

**Dependencies**: Config

```python
def generate_initial_code(problem: Problem, cfg: ExperimentConfig) -> str: ...
def repair_code(problem: Problem, code: str, feedback_prompt: str, cfg: ExperimentConfig) -> str: ...
# internal: exponential backoff, max 3 retries on rate limit
```

### Feedback (`feedback.py`)

**Dependencies**: sandbox.py

```python
def get_static_feedback(code: str, token_budget: int) -> str: ...
    # runs pylint + mypy, truncates: errors > warnings > info

def get_execution_feedback(code: str, problem: Problem, cfg: ExperimentConfig, token_budget: int) -> str: ...
    # truncates: failed tests first, then pass summary

def truncate_deterministic(items: list[str], token_budget: int) -> str: ...

def build_feedback_prompt(static_fb: str, exec_fb: str, condition: str) -> str: ...
    # condition "A" = static+exec order, "B" = exec+static order
```

### Sandbox (`sandbox.py`)

**Dependencies**: Config

```python
@dataclass
class ExecResult:
    passed: bool
    stdout: str
    stderr: str
    traceback: str | None

def run_tests(code: str, problem: Problem, timeout_s: int) -> ExecResult: ...
def run_tests_majority_vote(code: str, problem: Problem, cfg: ExperimentConfig) -> ExecResult: ...
```

### Repair Loop (`repair_loop.py`)

**Dependencies**: llm.py, feedback.py, sandbox.py, Config

```python
@dataclass
class IterationLog:
    problem_id: str
    condition: str
    iteration: int
    code: str
    exec_result: ExecResult
    static_fb: str
    exec_fb: str

def run_condition(problem: Problem, condition: str, cfg: ExperimentConfig) -> list[IterationLog]: ...
def run_all(problems: list[Problem], cfg: ExperimentConfig) -> list[IterationLog]: ...
    # runs both conditions A and B per problem
```

### Metrics (`metrics.py`)

**Dependencies**: repair_loop.py (IterationLog)

```python
def pass_at_1(logs: list[IterationLog], condition: str) -> float: ...
def relative_improvement(pass_a: float, pass_b: float) -> float: ...
def bootstrap_ci(logs: list[IterationLog], n_resamples: int = 10000) -> tuple[float, float]: ...
def mcnemar_test(logs: list[IterationLog]) -> float: ...  # returns p-value
```

### Entrypoint (`run_experiment.py`)

**Dependencies**: all modules

```python
def main() -> None: ...
    # load problems -> generate initial -> run_all (A & B) ->
    # compute metrics -> write results/h-e1_raw.jsonl,
    # h-e1_metrics.json, h-e1_iteration_logs.jsonl
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config + Data Loading | ExperimentConfig, load HumanEval/MBPP via HF datasets | 6 | 2+1+1+2 |
| A-2 | LLM Client | GPT-4o-mini generation + repair calls with backoff/retry | 8 | 2+3+2+1 |
| A-3 | Sandbox Executor | Sandboxed test exec, timeout, majority vote for flaky tests | 10 | 3+2+3+2 |
| A-4 | Feedback Generation | pylint+mypy wrapper, execution feedback parsing, deterministic truncation | 12 | 3+2+4+3 |
| A-5 | Repair Loop | 3-iteration loop, condition A/B prompt branching, logging | 11 | 3+3+3+2 |
| A-6 | Metrics & Stats | pass@1, bootstrap CI (10k resamples), McNemar test | 9 | 2+2+4+1 |
| A-7 | Main Pipeline + Output | Orchestrate end-to-end run, write result artifacts | 7 | 2+2+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4, A-5, A-6], Low(4-8): [A-1, A-2, A-7]
