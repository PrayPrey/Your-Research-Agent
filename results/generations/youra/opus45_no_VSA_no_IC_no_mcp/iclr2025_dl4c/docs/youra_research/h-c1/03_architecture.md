# Architecture: H-C1

**Type:** CONDITION | **Applied:** execution-feedback-vs-critic comparison pattern (Self-Refine / Self-Debug)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1)
**Status**: Reusable patterns found from H-M1 actual code
**Analyzed Path**: `docs/youra_research/h-m1/code/`
**Findings**: `data_loader.py` (HumanEval/MBPP unified-schema loading) and `sandbox_executor.py` (subprocess-based `SandboxExecutor.run(code, tests) -> ExecutionResult`) are directly reusable as-is. `config.py` uses a `@dataclass Config` + module-level `CFG` singleton pattern — reused for H-C1 config.

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| load_humaneval, load_mbpp | `from base.data_loader import load_humaneval, load_mbpp` | `h-m1/code/data_loader.py` |
| SandboxExecutor, ExecutionResult | `from base.sandbox_executor import SandboxExecutor, ExecutionResult` | `h-m1/code/sandbox_executor.py` |

**Verified from**: `docs/youra_research/h-m1/code/` (actual implementation). Copy both files unmodified into `h-c1/code/base/`.

---

## File Structure

- `h-c1/code/base/data_loader.py` (copied from H-M1)
- `h-c1/code/base/sandbox_executor.py` (copied from H-M1)
- `h-c1/code/config.py`
- `h-c1/code/model_client.py`
- `h-c1/code/feedback.py`
- `h-c1/code/refine.py`
- `h-c1/code/evaluator.py`
- `h-c1/code/metrics.py`
- `h-c1/code/visualize.py`
- `h-c1/code/run_pipeline.py`
- `h-c1/figures/`
- `h-c1/results/`

---

## Modules

### Config (`config.py`)

**Dependencies**: none

```python
@dataclass
class Config:
    seed: int = 42
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    temperature: float = 0.2
    max_new_tokens: int = 512
    timeout_s: int = 10
    memory_mb: int = 512
    results_dir: str = "results"
CFG = Config()
```

### ModelClient (`model_client.py`)

**Dependencies**: Config

```python
class ModelClient:
    def __init__(self, model_id: str, temperature: float): ...
    def generate(self, prompt: str) -> str: ...
```

### FeedbackMechanisms (`feedback.py`)

**Dependencies**: base.sandbox_executor, ModelClient

```python
def build_exec_feedback(exec_result: ExecutionResult) -> str: ...
def build_critic_feedback(client: ModelClient, code: str, problem: dict) -> str: ...
```

### Refiner (`refine.py`)

**Dependencies**: ModelClient

```python
REFINE_PROMPT_TEMPLATE: str

def refine_with_feedback(client: ModelClient, code: str, feedback: str, problem: dict) -> str: ...
```

### Evaluator (`evaluator.py`)

**Dependencies**: base.sandbox_executor

```python
def pass_at_1(executor: SandboxExecutor, code: str, tests: str) -> float: ...

def compare_feedback_mechanisms(
    client: ModelClient,
    executor: SandboxExecutor,
    problem: dict,
    initial_code: str,
) -> dict:  # {"execution_pass": float, "critic_pass": float, "execution_advantage": float}
    ...
```

### Metrics (`metrics.py`)

**Dependencies**: none

```python
def compute_complexity_effect(humaneval_results: list[dict], mbpp_results: list[dict]) -> dict:
    # {"humaneval_exec_advantage", "mbpp_exec_advantage", "complexity_effect", "hypothesis_supported"}
    ...
```

### Visualize (`visualize.py`)

**Dependencies**: matplotlib

```python
def plot_exec_advantage_bar(complexity_effect_result: dict, out_path: str) -> None: ...
def plot_pass_at_1_grouped(he_results: list[dict], mbpp_results: list[dict], out_path: str) -> None: ...
def plot_error_type_breakdown(results: list[dict], out_path: str) -> None: ...
def plot_complexity_scatter(results: list[dict], out_path: str) -> None: ...
```

### Pipeline (`run_pipeline.py`)

**Dependencies**: all above

```python
def main() -> None:
    # load HE + MBPP -> generate initial code -> compare_feedback_mechanisms per problem
    # -> compute_complexity_effect -> save results/experiment_results.json -> generate figures
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & copy base modules | Copy data_loader.py, sandbox_executor.py from H-M1; config.py | 6 | 2+1+1+2 |
| A-2 | ModelClient | Load CodeLlama-7B-Instruct, generate() wrapper | 10 | 3+3+2+2 |
| A-3 | Initial code generation | Generate initial solutions for HE+MBPP (591 problems) | 8 | 2+2+2+2 |
| A-4 | Execution feedback mechanism | Run code, parse ExecutionResult into feedback string | 8 | 2+2+2+2 |
| A-5 | AI-critic feedback mechanism | LLM critique prompt, no execution info | 6 | 2+1+2+1 |
| A-6 | Refinement | Single-iteration refine_with_feedback for both paths | 8 | 2+2+2+2 |
| A-7 | Evaluator (pass@1 + comparison) | pass_at_1, compare_feedback_mechanisms over full dataset | 10 | 3+3+2+2 |
| A-8 | Metrics computation | compute_complexity_effect, gate check | 6 | 1+2+2+1 |
| A-9 | Visualization | 4 figures (bar, grouped bar, stacked bar, scatter) | 9 | 2+2+2+3 |
| A-10 | End-to-end pipeline | run_pipeline.py orchestration, logging, seed control | 8 | 2+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-7, A-9], Low(4-8): [A-1, A-3, A-4, A-5, A-6, A-8, A-10]
