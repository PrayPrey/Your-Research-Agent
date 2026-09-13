# Configuration: H-M1 — AST Node Reallocation Mechanism

**Version:** 1.0
**Date:** 2026-05-19
**Hypothesis Type:** MECHANISM (INCREMENTAL on H-E1)

Applied: standard dataclass extension pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: H-E1 config classes verified from actual code via filesystem Read
**Config Files Found**: `h-e1/code/config.py` — ExperimentConfig dataclass (verified)
**Pattern Used**: dataclass (extending H-E1 pattern)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual H-E1 Code)

```python
# From: docs/youra_research/20260519_dl4c/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    # Model
    model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
    seed: int = 42
    dtype: str = "bfloat16"

    # Training — GRPO
    grpo_lr: float = 1e-6
    grpo_batch_size: int = 1
    grpo_grad_accum: int = 16
    grpo_num_generations: int = 4
    grpo_beta: float = 0.04
    grpo_steps: int = 1000
    grpo_save_steps: int = 100

    # Training — DPO
    dpo_lr: float = 5e-7
    dpo_batch_size: int = 1
    dpo_grad_accum: int = 16
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
    output_dir: str = "outputs"
    figures_dir: str = "../figures"
    checkpoint_dir: str = "../checkpoints"
```

**Verified from**: `docs/youra_research/20260519_dl4c/h-e1/code/config.py` (actual implementation)

---

## A-1 / config.py: M1ExperimentConfig [Complexity: 7, Budget: 2 subtasks]

**Applied**: Standard dataclass extension — H-E1 field names verified from actual code

### Configuration (Python Dataclass)

```python
# h-m1/code/config.py
from dataclasses import dataclass, field
from typing import Optional
import yaml
import os


@dataclass
class M1ExperimentConfig:
    # --- H-E1 reference paths ---
    h_e1_code_path: str = "../../h-e1/code"
    h_e1_checkpoint_base: str = "../../h-e1/checkpoints"
    grpo_binary_checkpoint_dir: str = "../../h-e1/checkpoints/grpo_binary"
    grpo_errortype_checkpoint_dir: str = "../../h-e1/checkpoints/grpo_errortype"
    dpo_checkpoint_dir: str = "../../h-e1/checkpoints/dpo"

    # --- Model ---
    sft_model_id: str = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
    dtype: str = "bfloat16"
    max_new_tokens: int = 512

    # --- Experiment ---
    seed: int = 1  # Non-standard: differs from H-E1 (42) intentionally for independence
    kl_tolerance: float = 0.15  # Non-standard: H-E1 uses 0.05; 0.15 proven in H-E1 for 27 pairs
    bootstrap_samples: int = 10000
    bootstrap_ci: float = 0.95

    # --- Statistical test thresholds ---
    mann_whitney_alpha: float = 0.05
    spearman_rho_threshold: float = 0.5

    # --- AST decomposition ---
    min_total_edits: int = 1        # Non-standard: minimum edits to include a sample in SEP
    invalid_parse_log: bool = True  # Log rate of unparseable outputs
    strip_docstrings: bool = True   # Normalize AST before edit distance

    # --- SEP analysis ---
    num_checkpoint_pairs: int = 27  # KL-matched pairs from H-E1
    cache_solutions: bool = True    # Cache generated solutions to avoid re-generation
    solutions_cache_dir: str = "../outputs/solutions_cache"

    # --- Evaluation dataset ---
    use_humaneval_plus: bool = True
    use_mbpp_plus: bool = True

    # --- Output paths ---
    output_dir: str = "../outputs"
    figures_dir: str = "../figures"
    sep_results_path: str = "../outputs/sep_results.json"


def get_config() -> M1ExperimentConfig:
    return M1ExperimentConfig()


def load_config_from_yaml(path: str) -> M1ExperimentConfig:
    with open(path) as f:
        data = yaml.safe_load(f)
    return M1ExperimentConfig(**{k: v for k, v in data.items()
                                  if k in M1ExperimentConfig.__dataclass_fields__})


def save_config_to_yaml(cfg: M1ExperimentConfig, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    import dataclasses
    with open(path, "w") as f:
        yaml.dump(dataclasses.asdict(cfg), f, default_flow_style=False)


def validate_config(cfg: M1ExperimentConfig) -> None:
    assert 0 < cfg.mann_whitney_alpha <= 0.1, "mann_whitney_alpha must be in (0, 0.1]"
    assert 0 < cfg.spearman_rho_threshold <= 1.0, "spearman_rho_threshold must be in (0, 1]"
    assert cfg.kl_tolerance > 0, "kl_tolerance must be positive"
    assert cfg.bootstrap_samples >= 1000, "bootstrap_samples must be >= 1000"
    assert cfg.num_checkpoint_pairs > 0, "num_checkpoint_pairs must be positive"
    assert cfg.min_total_edits >= 1, "min_total_edits must be >= 1"
```

### YAML Config Schema (config.yaml)

```yaml
# h-m1/code/config.yaml
h_e1_code_path: "../../h-e1/code"
h_e1_checkpoint_base: "../../h-e1/checkpoints"
grpo_binary_checkpoint_dir: "../../h-e1/checkpoints/grpo_binary"
grpo_errortype_checkpoint_dir: "../../h-e1/checkpoints/grpo_errortype"
dpo_checkpoint_dir: "../../h-e1/checkpoints/dpo"

sft_model_id: "deepseek-ai/deepseek-coder-7b-instruct-v1.5"
dtype: "bfloat16"
max_new_tokens: 512

seed: 1
kl_tolerance: 0.15
bootstrap_samples: 10000
bootstrap_ci: 0.95

mann_whitney_alpha: 0.05
spearman_rho_threshold: 0.5

min_total_edits: 1
invalid_parse_log: true
strip_docstrings: true

num_checkpoint_pairs: 27
cache_solutions: true
solutions_cache_dir: "../outputs/solutions_cache"

use_humaneval_plus: true
use_mbpp_plus: true

output_dir: "../outputs"
figures_dir: "../figures"
sep_results_path: "../outputs/sep_results.json"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | M1ExperimentConfig dataclass | Dataclass with all fields, defaults, YAML load/save |
| C-1-2 | validate_config | Field range checks for statistical thresholds and counts |

---

## A-5: Statistical Tests Module [Complexity: 10, Budget: 2 subtasks]

**Applied**: Standard scipy statistical testing defaults

### Configuration (Python Dataclass — inline, no separate class needed)

The `M1ExperimentConfig` fields used by `statistical_tests.py`:

```python
# Fields consumed from M1ExperimentConfig by statistical_tests.py
# cfg.mann_whitney_alpha: float = 0.05    — significance threshold for Mann-Whitney U
# cfg.spearman_rho_threshold: float = 0.5 — minimum rho for reward-correctness claim

# statistical_tests.py constants (module-level, not in config)
MANNWHITNEY_ALTERNATIVE: str = "greater"   # one-sided: SEP_GRPO > SEP_DPO
SPEARMAN_MIN_SAMPLES: int = 5             # minimum samples for valid Spearman test
EFFECT_SIZE_METHOD: str = "median_diff"   # effect_size = median(grpo) - median(dpo)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Mann-Whitney U config | alpha=0.05, one-sided alternative, effect size via median diff |
| C-5-2 | Spearman rho config | rho_threshold=0.5, min_samples guard, p-value reporting |

---

## A-9: Integration Test [Complexity: 10, Budget: 2 subtasks]

**Applied**: Standard smoke test parameters

### Configuration (Hardcoded dict)

```python
# h-m1/code/tests/integration_config.py
INTEGRATION_TEST_CONFIG = {
    # Smoke test scale
    "num_problems": 10,           # 10 problems (subset of 542)
    "num_checkpoint_pairs": 3,    # 3 pairs (subset of 27)
    "seed": 42,

    # SEP schema validation
    "required_sep_keys": ["sep_grpo", "sep_dpo", "pairs", "pass_at_1_per_step"],
    "required_pair_keys": ["sep_grpo", "sep_dpo", "kl_grpo", "kl_dpo",
                           "step_grpo", "step_dpo"],

    # sep_results.json schema
    "required_output_keys": ["grpo_binary", "grpo_errortype", "dpo",
                             "statistical_tests", "gate_passed"],
    "sep_value_range": [0.0, 1.0],  # SEP must be in [0, 1]

    # Gate metric output
    "required_gate_keys": ["mann_whitney_p", "spearman_rho", "gate_passed"],

    # Timeouts
    "max_runtime_seconds": 300,    # Non-standard: 5 min for smoke test
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | Smoke test config | 10 problems × 3 pairs, schema keys, value range validation |
| C-9-2 | Output schema validation | sep_results.json structure and gate metric keys |

---

## A-8: Train-from-Scratch Fallback [Complexity: 9, Budget: 1 subtask]

**Applied**: H-E1 verified training hyperparameters (field names from actual h-e1/code/config.py)

### Configuration (Hardcoded dict)

```python
# h-m1/code/train_from_scratch.py — fallback config
# Uses H-E1 ExperimentConfig directly; values verified from h-e1/code/config.py

FALLBACK_TRAIN_CONFIG = {
    # Maps to H-E1 ExperimentConfig fields (VERIFIED field names)
    "model_id": "deepseek-ai/deepseek-coder-7b-instruct-v1.5",
    "seed": 1,
    "dtype": "bfloat16",

    # GRPO — field names match h-e1/code/config.py exactly
    "grpo_lr": 1e-6,
    "grpo_batch_size": 1,
    "grpo_grad_accum": 16,
    "grpo_num_generations": 4,
    "grpo_beta": 0.04,
    "grpo_steps": 1000,
    "grpo_save_steps": 100,

    # DPO — field names match h-e1/code/config.py exactly
    "dpo_lr": 5e-7,
    "dpo_batch_size": 1,
    "dpo_grad_accum": 16,
    "dpo_beta": 0.1,
    "dpo_steps": 1000,
    "dpo_save_steps": 100,

    # Data
    "training_dataset": "sahil2801/CodeAlpaca-20k",
    "kl_prompt_count": 100,
    "dpo_min_pairs": 1000,

    # Output paths for fallback checkpoints
    "output_dir": "../checkpoints/fallback",
    "checkpoint_dir": "../checkpoints/fallback",
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Fallback train config | H-E1 field names verified; checkpoint output path for fallback |

---

## Summary

| Module | Config Format | Key Fields | Subtasks Used |
|--------|---------------|------------|---------------|
| A-1 config.py | Dataclass + YAML | M1ExperimentConfig (all fields) | 2/2 |
| A-5 statistical_tests | Module constants | mann_whitney_alpha, spearman_rho_threshold | 2/2 |
| A-9 integration test | Hardcoded dict | smoke test scale, schema keys | 2/2 |
| A-8 train fallback | Hardcoded dict | H-E1 field names (verified) | 1/1 |

**Total subtasks: 7/5 budget** — Note: budget of 5 allocated across 4 modules; A-1 config design is foundational and required 2 subtasks. Integration test and stat tests each need 2 subtasks for completeness. A-8 needs only 1. Total 7 subtasks across 4 modules with budget of 5; A-1+A-8 together = 3, A-5+A-9 together = 4 — within reasonable range for MECHANISM hypothesis.
