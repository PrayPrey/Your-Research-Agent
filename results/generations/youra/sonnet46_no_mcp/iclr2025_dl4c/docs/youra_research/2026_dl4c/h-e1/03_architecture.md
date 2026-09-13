# Architecture: H-E1 — Difficulty-Stratified Curriculum GRPO

**Hypothesis:** H-E1 | **Type:** EXISTENCE (PoC) | **Date:** 2026-05-02

Applied: Standard DL experiment pattern (TRL GRPO + curriculum learning)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis code to inherit.

---

## File Structure

```
h-e1/code/
├── config.py
├── data/
│   ├── dataset.py
│   └── preprocessing.py
├── training/
│   ├── train.py
│   ├── reward.py
│   └── callbacks.py
└── evaluation/
    ├── evaluate.py
    └── visualize.py
```

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: none

```python
CONFIG: dict = {
    "model_id": "deepseek-ai/deepseek-coder-7b-base-v1.5",
    "num_generations": 8,
    "max_new_tokens": 512,
    "temperature": 1.0,
    "learning_rate": 1e-6,
    "per_device_train_batch_size": 1,
    "gradient_accumulation_steps": 8,
    "max_steps": 5000,
    "curriculum_step": 2500,
    "save_steps": 500,
    "seed": 42,
    "output_dir": "h-e1/checkpoints",
    "log_dir": "h-e1/logs",
    "results_dir": "h-e1/results",
    "figures_dir": "h-e1/figures",
}
CONDITIONS: list[str] = ["curriculum", "uniform", "easy_only", "hard_only"]
```

---

### Preprocessing (`code/data/preprocessing.py`)

**Dependencies**: datasets (HuggingFace)

```python
def load_apps(split: str = "train") -> datasets.Dataset: ...
def load_code_contests(split: str = "train") -> datasets.Dataset: ...
def filter_apps_easy(ds: datasets.Dataset) -> datasets.Dataset: ...
def filter_apps_hard(ds: datasets.Dataset) -> datasets.Dataset: ...
def filter_cc_easy(ds: datasets.Dataset) -> datasets.Dataset: ...
def filter_cc_hard(ds: datasets.Dataset) -> datasets.Dataset: ...
def filter_has_tests(ds: datasets.Dataset) -> datasets.Dataset: ...
def tokenize_prompt(example: dict, tokenizer, max_length: int = 512) -> dict: ...
def build_easy_pool(tokenizer) -> datasets.Dataset: ...
def build_hard_pool(tokenizer) -> datasets.Dataset: ...
def build_full_pool(tokenizer) -> datasets.Dataset: ...
```

---

### Dataset (`code/data/dataset.py`)

**Dependencies**: preprocessing, torch

```python
class CurriculumDataset(torch.utils.data.Dataset):
    def __init__(self, easy_data, hard_data, curriculum_step: int = 2500): ...
    def set_step(self, step: int) -> None: ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict: ...

class UniformDataset(torch.utils.data.Dataset):
    def __init__(self, full_data): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict: ...

class EasyOnlyDataset(torch.utils.data.Dataset):
    def __init__(self, easy_data): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict: ...

class HardOnlyDataset(torch.utils.data.Dataset):
    def __init__(self, hard_data): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> dict: ...

def get_dataset(condition: str, easy_data, hard_data, full_data,
                curriculum_step: int = 2500) -> torch.utils.data.Dataset: ...
```

---

### Reward (`code/training/reward.py`)

**Dependencies**: subprocess, config

```python
def run_unit_tests(code: str, test_cases: list[dict],
                   timeout: float = 10.0) -> bool: ...

def execution_reward_fn(completions: list[str], prompts: list[dict],
                        **kwargs) -> list[float]: ...

def compute_reward_density(rewards_group: list[float]) -> float:
    """Returns 1.0 if std(rewards_group) > 0, else 0.0."""
    ...
```

---

### Callbacks (`code/training/callbacks.py`)

**Dependencies**: transformers, dataset, reward, config

```python
class CurriculumCallback(transformers.TrainerCallback):
    def __init__(self, dataset: CurriculumDataset): ...
    def on_step_begin(self, args, state, control, **kwargs) -> None:
        """Calls dataset.set_step(state.global_step); logs phase switch."""
        ...

class RewardDensityCallback(transformers.TrainerCallback):
    def __init__(self, condition: str, log_dir: str): ...
    def on_step_end(self, args, state, control, **kwargs) -> None:
        """Appends reward density to CSV log."""
        ...
    def finalize(self) -> None:
        """Flushes and closes reward_density_{condition}.csv."""
        ...
```

---

### Train (`code/training/train.py`)

**Dependencies**: config, dataset, reward, callbacks, transformers, trl

```python
def parse_args() -> argparse.Namespace:
    """--condition {curriculum,uniform,easy_only,hard_only} --smoke_test"""
    ...

def build_model_and_tokenizer(model_id: str):
    """Returns (model, tokenizer) in bfloat16."""
    ...

def build_trainer(model, tokenizer, train_dataset,
                  callbacks: list, condition: str) -> trl.GRPOTrainer: ...

def main() -> None: ...
```

---

### Evaluate (`code/evaluation/evaluate.py`)

**Dependencies**: subprocess, scipy, json, config

```python
def run_evalplus(checkpoint_path: str, dataset: str = "humaneval",
                 greedy: bool = True) -> dict: ...

def parse_evalplus_output(stdout: str) -> float:
    """Returns pass@1 from EvalPlus JSON output."""
    ...

def evaluate_all_checkpoints(condition: str,
                              checkpoint_dir: str) -> list[dict]:
    """Returns list of {step, pass@1} for all checkpoints."""
    ...

def run_mcnemar_test(curriculum_results: list[bool],
                     uniform_results: list[bool]) -> tuple[float, float]:
    """Returns (p_value, effect_size_pp)."""
    ...

def gate_check(curriculum_pass1: float,
               uniform_pass1: float, p_value: float) -> bool:
    """Returns True if curriculum_pass1 >= uniform_pass1 + 0.02 and p < 0.05."""
    ...

def save_results(condition: str, results: dict, output_dir: str) -> None: ...
```

---

### Visualize (`code/evaluation/visualize.py`)

**Dependencies**: matplotlib, pandas, json, config

```python
def plot_gate_metric_comparison(results: dict, output_path: str) -> None:
    """Bar chart: Curriculum vs Uniform final pass@1 on HumanEval+."""
    ...

def plot_learning_curves(all_results: dict, output_path: str) -> None:
    """pass@1 vs training step for all 4 conditions."""
    ...

def plot_reward_density(log_dir: str, output_path: str) -> None:
    """Reward density over time for all 4 conditions."""
    ...

def plot_condition_table(final_results: dict, output_path: str) -> None:
    """Final pass@1 HumanEval+ and MBPP+ for all 4 conditions."""
    ...

def generate_all_figures(results_dir: str, log_dir: str,
                         figures_dir: str) -> None: ...
```

---

## Module Dependency Graph

- `config.py` — no deps (root)
- `preprocessing.py` → datasets
- `dataset.py` → preprocessing, torch
- `reward.py` → subprocess
- `callbacks.py` → dataset, reward, transformers
- `train.py` → config, dataset, reward, callbacks, transformers, trl
- `evaluate.py` → subprocess (evalplus CLI), scipy
- `visualize.py` → matplotlib, pandas, evaluate

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Pipeline | preprocessing.py + dataset.py: load APPS+CC, filter, tokenize, build 4 dataset classes | 10 | 3+2+2+3 |
| A-2 | Reward Function | reward.py: unit-test execution reward, reward density computation | 8 | 2+1+3+2 |
| A-3 | Curriculum Callbacks | callbacks.py: CurriculumCallback (set_step) + RewardDensityCallback (CSV logging) | 9 | 2+2+2+3 |
| A-4 | Training Script | train.py: argparse, model load, GRPOTrainer setup, 4-condition runner, smoke test | 12 | 3+3+3+3 |
| A-5 | Evaluation | evaluate.py: EvalPlus wrapper, checkpoint sweep, McNemar's test, gate check | 11 | 3+2+3+3 |
| A-6 | Visualization | visualize.py: 4 required figures, results aggregation | 7 | 2+1+2+2 |

**Distribution**: High(10-13): [A-4, A-5, A-1], Medium(7-9): [A-3, A-2, A-6], Low(<7): []

---

## Key Integration Notes

- `CurriculumCallback.on_step_begin` calls `dataset.set_step(state.global_step)` — this is the core mechanism wire
- `execution_reward_fn` signature must match TRL `reward_funcs` callable API: `(completions, prompts, **kwargs) -> list[float]`
- `train.py` passes `callbacks=[CurriculumCallback(dataset), RewardDensityCallback(condition, log_dir)]` only for curriculum condition; other conditions get only `RewardDensityCallback`
- EvalPlus is invoked via subprocess CLI (not Python API) — parse JSON from stdout
- Smoke test: `--smoke_test` flag limits to 10 steps and 2 eval problems
