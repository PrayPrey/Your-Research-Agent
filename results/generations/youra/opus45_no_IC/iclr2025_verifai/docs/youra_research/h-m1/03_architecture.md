# Architecture: H-M1 — Grammar-Constrained Decoding

**Tier**: FULL | **Type**: MECHANISM

Applied: SynCode wrapper pattern (DFA mask store, inference-time constraint, no training)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch, first mechanism hypothesis (no base hypothesis code to reuse)

---

## File Organization

```
h-m1/code/
├── config.py
├── data_loader.py
├── generators.py       # BaselineGenerator + ConstrainedGenerator
├── evaluate.py          # syntax check + error rate
├── visualize.py
├── run_experiment.py    # orchestrator
└── figures/
```

---

## Module Interfaces

### Config (`config.py`)

**Dependencies**: none

```python
@dataclass
class ExperimentConfig:
    model_id: str = "meta-llama/CodeLlama-7b-hf"
    dataset_id: str = "openai/openai_humaneval"
    num_samples: int = 10
    temperature: float = 0.2
    max_new_tokens: int = 512
    seed: int = 1
    device: str = "cuda"
    output_dir: str = "results"
    figures_dir: str = "figures"
```

### DataLoader (`data_loader.py`)

**Dependencies**: Config, datasets

```python
def load_humaneval_problems(dataset_id: str) -> list[dict]: ...
    # returns [{"task_id": str, "prompt": str}, ...]
```

### BaselineGenerator (`generators.py`)

**Dependencies**: Config, transformers

```python
class BaselineGenerator:
    def __init__(self, model_id: str, device: str, seed: int): ...
    def generate(self, prompt: str, num_samples: int, temperature: float, max_new_tokens: int) -> list[str]: ...
```

### ConstrainedGenerator (`generators.py`)

**Dependencies**: Config, syncode

```python
class ConstrainedGenerator:
    def __init__(self, model_id: str, grammar: str, device: str, seed: int): ...
    def generate(self, prompt: str, num_samples: int, temperature: float, max_new_tokens: int) -> list[str]: ...
```

### Evaluator (`evaluate.py`)

**Dependencies**: ast (stdlib)

```python
def check_syntax(code: str) -> bool: ...
def compilation_error_rate(samples: list[str]) -> float: ...
def evaluate_condition(problem_results: dict[str, list[str]]) -> dict: ...
    # returns {"error_rate": float, "n_errors": int, "n_total": int, "per_problem": dict}
```

### Visualizer (`visualize.py`)

**Dependencies**: matplotlib, Evaluator outputs

```python
def plot_error_rate_comparison(baseline_rate: float, constrained_rate: float, out_path: str) -> None: ...
def plot_error_by_difficulty(per_problem_baseline: dict, per_problem_constrained: dict, out_path: str) -> None: ...
def save_summary_table(baseline_stats: dict, constrained_stats: dict, out_path: str) -> None: ...
```

### Orchestrator (`run_experiment.py`)

**Dependencies**: all modules above

```python
def main() -> None: ...
    # 1. load config + set seed
    # 2. load HumanEval problems
    # 3. run BaselineGenerator over all problems -> save raw samples
    # 4. run ConstrainedGenerator over all problems -> save raw samples
    # 5. evaluate both conditions
    # 6. check gate: constrained_error_rate < baseline_error_rate
    # 7. generate figures + summary table
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Config & scaffolding | ExperimentConfig, dirs, seeding | 5 | 1+1+1+2 |
| A-2 | Data loading | Load HumanEval via datasets, extract prompts | 5 | 2+2+1+0 |
| A-3 | Baseline generator | Load CodeLlama-7B, unconstrained generate loop | 10 | 3+3+2+2 |
| A-4 | Constrained generator | SynCode integration, grammar_strict mode | 13 | 3+4+4+2 |
| A-5 | Generation run (baseline) | Execute 164×10 baseline generations, persist | 9 | 2+2+2+3 |
| A-6 | Generation run (constrained) | Execute 164×10 constrained generations, persist | 10 | 2+3+2+3 |
| A-7 | Evaluation pipeline | ast.parse syntax check, error-rate aggregation | 6 | 2+1+2+1 |
| A-8 | Gate check | Compare rates, PASS/FAIL determination | 4 | 1+1+1+1 |
| A-9 | Visualization | Bar chart, per-problem heatmap, summary table | 7 | 2+2+1+2 |
| A-10 | End-to-end orchestration | Wire all modules, logging, error handling | 8 | 2+3+1+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-4, A-5, A-6, A-10], Low(4-8): [A-1, A-2, A-7, A-8, A-9]
