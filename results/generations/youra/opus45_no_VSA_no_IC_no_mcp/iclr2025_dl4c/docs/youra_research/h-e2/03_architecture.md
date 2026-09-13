# Architecture: h-e2 (EXISTENCE PoC)

**Hypothesis:** AI-critic feedback yields higher pass@1 than random baseline after k=3 refinement.

Applied: self-refine iterative feedback loop pattern (Init → Feedback → Iterate)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Structure

```
h-e2/code/
  config.py
  data.py
  model.py
  refine.py
  evaluate.py
  train.py        # entrypoint (inference-only pipeline)
figures/
```

---

## Modules

### config.py

**Dependencies**: none

```python
MODEL_ID = "codellama/CodeLlama-7b-Instruct-hf"
K_ITERS = 3
TEMPERATURE = 0.7
MAX_TOKENS = 512
SEED = 42
DATASETS = {"humaneval": "openai_humaneval", "mbpp": ("mbpp", "test")}
```

### data.py (`code/data.py`)

**Dependencies**: datasets

```python
def load_problems(name: str) -> list[dict]: ...  # {"id","prompt","test","entry_point"}
```

### model.py (`code/model.py`)

**Dependencies**: transformers, torch, config

```python
class CodeLLM:
    def __init__(self, model_id: str): ...
    def generate(self, prompt: str, temperature: float, max_tokens: int) -> str: ...
```

### refine.py (`code/refine.py`)

**Dependencies**: model.CodeLLM

```python
class AICriticRefinement:
    def __init__(self, generator: CodeLLM, k: int): ...
    def generate_initial(self, prompt: str) -> str: ...
    def generate_feedback(self, code: str, problem: str) -> str: ...
    def refine_code(self, code: str, feedback: str, problem: str) -> str: ...
    def run(self, problem: str) -> list[str]: ...  # code snapshot per iteration [k=0..3]

class RandomFeedbackRefinement(AICriticRefinement):
    def generate_feedback(self, code: str, problem: str) -> str: ...  # random/nonsense text
```

### evaluate.py (`code/evaluate.py`)

**Dependencies**: none (uses exec/subprocess for test execution)

```python
def run_tests(code: str, test: str, entry_point: str) -> bool: ...
def compute_pass_at_1(results: list[dict]) -> float: ...
def plot_comparison(pass_rates: dict[str, float], out_path: str) -> None: ...
def plot_iteration_curve(curves: dict[str, list[float]], out_path: str) -> None: ...
```

### train.py (`code/train.py`)

**Dependencies**: data, model, refine, evaluate, config

```python
def main() -> None: ...
# loads data -> zero-shot pass@1 -> AI-critic loop -> random-baseline loop
# -> compute pass@1 per condition per iteration -> save figures -> assert AI > random
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & config | Project skeleton, config.py, deps | 5 | 1+1+1+2 |
| A-2 | Data pipeline | Load HumanEval + MBPP via HF datasets, parse prompts/tests | 6 | 2+2+1+1 |
| A-3 | Model wrapper | Load CodeLlama-7B-Instruct, generate() with temp/max_tokens | 8 | 3+3+1+1 |
| A-4 | Zero-shot baseline eval | Generate + execute + pass@1 for baseline | 6 | 2+2+1+1 |
| A-5 | AI-critic refinement loop | Implement AICriticRefinement (init/feedback/refine, k=3) | 10 | 3+3+3+1 |
| A-6 | Random-baseline refinement loop | RandomFeedbackRefinement control variant | 5 | 1+2+1+1 |
| A-7 | Execution & pass@1 evaluation | Sandbox test execution, pass@1 across 3 conditions + per-iter curve | 9 | 3+2+3+1 |
| A-8 | Comparison, visualization & gate check | Bar chart, iteration curve, assert AI>random, save figures | 6 | 2+1+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-5, A-7], Low(4-8): [A-1, A-2, A-3, A-4, A-6, A-8]

---

## Notes

- Inference-only; no training loop needed beyond orchestration in train.py.
- Same model used as generator and critic (per FR-3).
- Random baseline: swap `generate_feedback` with random token/sentence sampling (control for signal vs noise).
- Skipped: separate critic model, ablation modules, multi-seed runs — deferred (EXISTENCE scope only).
