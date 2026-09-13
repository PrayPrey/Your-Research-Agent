# Architecture: H-E1 — Execution-RL vs DPO Structural Efficiency (EXISTENCE PoC)

**Version:** 1.0
**Date:** 2026-05-19
**Hypothesis Type:** EXISTENCE
**Applied:** Standard DL Experiment Pipeline Pattern

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field — no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch. All patterns sourced from TRL and evalplus official APIs.

---

## File Structure

```
h-e1/code/
├── config.py              # Single fixed config for all conditions
├── data.py                # Data loading: CodeAlpaca, DPO pairs, KL prompt set
├── rewards.py             # Execution reward functions (binary + error-type)
├── ast_metric.py          # AST semantic edit distance computation
├── kl_metric.py           # KL divergence computation + checkpoint matching
├── train_grpo.py          # GRPO training script (binary + error-type variants)
├── train_dpo.py           # DPO training script + preference pair generation
├── evaluate.py            # HumanEval+/MBPP+ evaluation + bootstrap CI
├── run_experiment.py      # Top-level orchestrator (all 4 conditions)
└── visualize.py           # Figure generation (4 required plots)
```

---

## Module Definitions

### Config (`h-e1/code/config.py`)

**Dependencies:** None

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    # Model
    model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
    seed: int = 42
    dtype: str = "bfloat16"

    # Training — GRPO
    grpo_lr: float = 1e-6
    grpo_batch_size: int = 4
    grpo_grad_accum: int = 4
    grpo_num_generations: int = 8
    grpo_beta: float = 0.04
    grpo_steps: int = 1000
    grpo_save_steps: int = 100

    # Training — DPO
    dpo_lr: float = 5e-7
    dpo_batch_size: int = 2
    dpo_grad_accum: int = 8
    dpo_beta: float = 0.1
    dpo_steps: int = 1000
    dpo_save_steps: int = 100

    # Data
    training_dataset: str = "sahil2801/CodeAlpaca-20k"
    kl_prompt_count: int = 100
    dpo_min_pairs: int = 1000

    # Evaluation
    kl_tolerance: float = 0.05
    bootstrap_samples: int = 10000
    bootstrap_ci: float = 0.95
    gate_magnitude: float = 0.20

    # Paths
    output_dir: str = "h-e1/outputs"
    figures_dir: str = "h-e1/figures"
    checkpoint_dir: str = "h-e1/checkpoints"

def get_config() -> ExperimentConfig: ...
```

---

### DataModule (`h-e1/code/data.py`)

**Dependencies:** config.py

```python
from datasets import Dataset
from config import ExperimentConfig

def load_grpo_dataset(cfg: ExperimentConfig) -> Dataset:
    """Load CodeAlpaca-20K, format with DeepSeek-Coder chat template."""
    ...

def load_kl_prompts(cfg: ExperimentConfig) -> list[str]:
    """Return fixed 100-prompt held-out set for KL computation (seed=42)."""
    ...

def generate_dpo_pairs(cfg: ExperimentConfig, model_id: str) -> Dataset:
    """Generate execution-oracle preference pairs from CodeAlpaca prompts.
    Each record: {prompt, chosen (passing), rejected (failing)}.
    Minimum cfg.dpo_min_pairs pairs.
    """
    ...

def load_humaneval_plus() -> dict:
    """Return 164-problem HumanEval+ dict via evalplus."""
    ...

def load_mbpp_plus() -> dict:
    """Return 378-problem MBPP+ dict via evalplus."""
    ...
```

---

### RewardFunctions (`h-e1/code/rewards.py`)

**Dependencies:** None (evalplus subprocess)

```python
def run_evalplus_tests(task_id: str, completion: str) -> dict:
    """Execute completion against evalplus test suite.
    Returns: {passed: bool, error_type: str | None}
    error_type in {None, 'syntax', 'runtime', 'logic'}
    """
    ...

def execution_reward_binary(
    completions: list[str],
    prompts: list[str],
    task_ids: list[str],
    **kwargs
) -> list[float]:
    """Binary reward: +1.0 if all tests pass, 0.0 otherwise."""
    ...

def execution_reward_error_type(
    completions: list[str],
    prompts: list[str],
    task_ids: list[str],
    **kwargs
) -> list[float]:
    """Graded reward: +1.0 (pass), -0.5 (syntax), -0.2 (runtime), +0.2 (logic)."""
    ...
```

---

### ASTMetric (`h-e1/code/ast_metric.py`)

**Dependencies:** None (stdlib ast, zss)

```python
import ast
from typing import Any

SEMANTIC_NODE_TYPES = frozenset([
    "If", "For", "While", "Try", "With",       # control-flow
    "Assign", "AugAssign", "Call", "Return",    # data-flow
])

def extract_semantic_ast(code: str) -> Any:
    """Parse code with ast module, filter to SEMANTIC_NODE_TYPES only.
    Returns zss-compatible tree node.
    Raises ValueError on syntax error.
    """
    ...

def compute_ast_semantic_edit_distance(code_a: str, code_b: str) -> float:
    """Zhang-Shasha edit distance between semantic ASTs via zss.simple_distance().
    Returns float; returns float('inf') on parse failure.
    """
    ...

def batch_ast_edit_distances(
    reference_codes: dict[str, str],
    candidate_codes: dict[str, str],
) -> dict[str, float]:
    """Compute per-problem edit distance vs reference (SFT-only).
    Keys: task_ids present in both dicts.
    """
    ...
```

---

### KLMetric (`h-e1/code/kl_metric.py`)

**Dependencies:** config.py

```python
import torch
from transformers import PreTrainedModel, PreTrainedTokenizer
from config import ExperimentConfig

def compute_kl_divergence(
    model: PreTrainedModel,
    ref_model: PreTrainedModel,
    prompts: list[str],
    tokenizer: PreTrainedTokenizer,
    n_samples: int = 100,
) -> float:
    """Monte Carlo KL(pi_theta || pi_ref) estimate on held-out prompts."""
    ...

def load_checkpoint_kl_log(checkpoint_dir: str) -> dict[int, float]:
    """Load step → KL mapping from checkpoint training logs.
    Returns: {step: kl_value}
    """
    ...

def match_checkpoints(
    kl_logs: dict[str, dict[int, float]],
    tolerance: float = 0.05,
) -> list[dict[str, int]]:
    """Match checkpoints across conditions within ±tolerance KL.
    Args:
        kl_logs: {condition_name: {step: kl_value}}
    Returns: list of {condition_name: matched_step} dicts
    """
    ...
```

---

### TrainGRPO (`h-e1/code/train_grpo.py`)

**Dependencies:** config.py, data.py, rewards.py, kl_metric.py

```python
from config import ExperimentConfig

def train_grpo(
    cfg: ExperimentConfig,
    reward_variant: str,  # "binary" | "error_type"
    output_dir: str,
) -> str:
    """Run GRPOTrainer with specified reward function.
    Saves checkpoints every cfg.grpo_save_steps steps.
    Returns: path to final checkpoint directory.
    """
    ...

if __name__ == "__main__":
    # CLI: python train_grpo.py --variant binary|error_type
    ...
```

---

### TrainDPO (`h-e1/code/train_dpo.py`)

**Dependencies:** config.py, data.py

```python
from config import ExperimentConfig

def train_dpo(
    cfg: ExperimentConfig,
    output_dir: str,
) -> str:
    """Run DPOTrainer on execution-oracle preference pairs.
    Calls generate_dpo_pairs() internally if pairs not cached.
    Saves checkpoints every cfg.dpo_save_steps steps.
    Returns: path to final checkpoint directory.
    """
    ...

if __name__ == "__main__":
    # CLI: python train_dpo.py
    ...
```

---

### Evaluate (`h-e1/code/evaluate.py`)

**Dependencies:** config.py, data.py, ast_metric.py, kl_metric.py

```python
import numpy as np
from config import ExperimentConfig

def generate_solutions(
    model_path: str,
    problems: dict,
    tokenizer_id: str,
    cfg: ExperimentConfig,
) -> dict[str, str]:
    """Generate greedy-decoded solutions for all problems.
    Returns: {task_id: solution_code}
    """
    ...

def run_evalplus_evaluation(
    solutions_path: str,
    dataset: str,  # "humaneval" | "mbpp"
) -> dict[str, float]:
    """Run evalplus CLI evaluation. Returns per-task pass@1 results."""
    ...

def compute_semantic_edit_per_kl(
    ast_distances: dict[str, float],
    kl_value: float,
) -> float:
    """Mean AST edit distance across problems divided by KL value."""
    ...

def bootstrap_ci(
    grpo_efficiencies: np.ndarray,
    dpo_efficiencies: np.ndarray,
    n_samples: int = 10000,
    ci: float = 0.95,
) -> dict:
    """Bootstrap CI for (GRPO - DPO) efficiency differential.
    Returns: {point_estimate, ci_lower, ci_upper, gate_pass: bool}
    """
    ...

def run_full_evaluation(
    condition_checkpoints: dict[str, str],
    cfg: ExperimentConfig,
) -> dict:
    """Evaluate all 4 conditions at KL-matched checkpoints.
    Args:
        condition_checkpoints: {condition_name: checkpoint_path}
    Returns: aggregated results dict for bootstrap CI and visualization.
    """
    ...
```

---

### RunExperiment (`h-e1/code/run_experiment.py`)

**Dependencies:** config.py, train_grpo.py, train_dpo.py, evaluate.py, visualize.py

```python
from config import ExperimentConfig

def run_all_conditions(cfg: ExperimentConfig) -> dict:
    """Orchestrate all 4 training conditions sequentially.
    1. SFT-only: no training, use base model directly
    2. SFT+DPO: train_dpo()
    3. SFT+GRPO-binary: train_grpo(variant='binary')
    4. SFT+GRPO-error-type: train_grpo(variant='error_type')
    Returns: results dict with all metrics.
    """
    ...

def save_results(results: dict, output_dir: str) -> None:
    """Save results JSON to output_dir/results.json."""
    ...

if __name__ == "__main__":
    # python run_experiment.py
    ...
```

---

### Visualize (`h-e1/code/visualize.py`)

**Dependencies:** config.py

```python
from config import ExperimentConfig

def plot_gate_metric_comparison(results: dict, cfg: ExperimentConfig) -> str:
    """Bar chart: semantic-edit-per-KL for all 4 conditions + 95% CI error bars.
    Saves to cfg.figures_dir/gate_metric_comparison.png. Returns path.
    """
    ...

def plot_kl_trajectories(kl_logs: dict[str, dict[int, float]], cfg: ExperimentConfig) -> str:
    """KL divergence vs training steps for all 4 conditions.
    Saves to cfg.figures_dir/kl_trajectories.png. Returns path.
    """
    ...

def plot_ast_vs_kl_scatter(results: dict, cfg: ExperimentConfig) -> str:
    """AST edit distance vs KL value scatter plot (sanity check).
    Saves to cfg.figures_dir/ast_vs_kl_scatter.png. Returns path.
    """
    ...

def plot_pass1_curves(results: dict, cfg: ExperimentConfig) -> str:
    """pass@1 HumanEval+ learning curves for all conditions vs training steps.
    Saves to cfg.figures_dir/pass1_curves.png. Returns path.
    """
    ...

def generate_all_figures(results: dict, kl_logs: dict, cfg: ExperimentConfig) -> list[str]:
    """Generate all 4 required figures. Returns list of saved paths."""
    ...
```

---

## Module Dependency Graph

- `run_experiment.py` → `train_grpo.py`, `train_dpo.py`, `evaluate.py`, `visualize.py`, `config.py`
- `train_grpo.py` → `data.py`, `rewards.py`, `kl_metric.py`, `config.py`
- `train_dpo.py` → `data.py`, `config.py`
- `evaluate.py` → `data.py`, `ast_metric.py`, `kl_metric.py`, `config.py`
- `visualize.py` → `config.py`
- `data.py` → `config.py`
- `rewards.py` → (none — evalplus subprocess)
- `ast_metric.py` → (none — stdlib + zss)
- `kl_metric.py` → `config.py`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Setup + Data Pipeline | config.py + data.py: load CodeAlpaca, KL prompts, DPO pair generation, evalplus loaders | 10 | 2+2+3+3 |
| E-2 | Reward Functions + AST Metric | rewards.py (binary + error-type execution rewards) + ast_metric.py (semantic AST edit distance with zss) | 12 | 3+2+4+3 |
| E-3 | GRPO Training | train_grpo.py: GRPOTrainer setup for binary and error-type variants, checkpoint saving | 13 | 3+3+4+3 |
| E-4 | DPO Training | train_dpo.py: DPOTrainer setup + preference pair caching, checkpoint saving | 11 | 3+3+3+2 |
| E-5 | KL Metric + Checkpoint Matching | kl_metric.py: Monte Carlo KL computation, checkpoint log parsing, cross-condition matching | 12 | 2+3+4+3 |
| E-6 | Evaluation + Bootstrap CI | evaluate.py: solution generation, evalplus pass@1, semantic-edit-per-KL, bootstrap CI gate | 14 | 3+3+4+4 |
| E-7 | Orchestrator + Visualization | run_experiment.py (full pipeline) + visualize.py (4 required figures) | 10 | 2+3+2+3 |

**Distribution:** High(11-14): [E-2, E-3, E-4, E-5, E-6], Medium(8-10): [E-1, E-7], Low(1-7): []

**Total Tasks:** 7 (within LIGHT tier ≤15 limit)

---

## External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| torch | >=2.0.0 | Model training |
| transformers | >=4.40.0 | AutoModelForCausalLM, tokenizer |
| trl | >=1.3.0 | GRPOTrainer, DPOTrainer |
| evalplus | >=0.3.0 | HumanEval+/MBPP+ evaluation harness |
| zss | >=1.4.0 | Zhang-Shasha AST edit distance |
| datasets | >=2.18.0 | CodeAlpaca-20K loading |
| scipy | >=1.11.0 | Bootstrap CI |
| numpy | >=1.24.0 | Array operations |
| matplotlib | >=3.7.0 | Figure generation |
| peft | >=0.10.0 | LoRA adapters (optional for memory) |
| accelerate | >=0.28.0 | Device placement |
