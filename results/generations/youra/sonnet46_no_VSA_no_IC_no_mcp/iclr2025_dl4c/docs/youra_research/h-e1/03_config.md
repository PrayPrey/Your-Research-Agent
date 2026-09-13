---
title: "Config: H-E1 — RLEF-Fraction Difficulty-Scaling Existence Proof"
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
date: "2026-08-26"
author: yoon303@ust.ac.kr
---

Applied: Single fixed config (EXISTENCE PoC pattern — no grid, no ablations, 1 seed)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze
**Config Files Found**: None — new config design
**Pattern Used**: hardcoded dict (matches architecture's `config: dict` function signatures)

---

## Main Experiment Config

Both artifacts encode the same values. Coder may use either; `config.py` is the runtime source of truth.

### `code/config.yaml`

```yaml
model_name: "deepseek-ai/deepseek-coder-7b-base"
fallback_model_name: "deepseek-ai/deepseek-coder-1b3-base"
ceiling_check_threshold: 0.90

training:
  lr: 1.0e-5
  batch_size: 4
  grad_accum: 8          # effective batch = 32
  epochs: 3
  max_length: 1024
  max_new_tokens: 512
  seed: 42
  precision: "bfloat16"
  grad_clip: 1.0
  warmup_steps: 100
  lr_schedule: "cosine"

grpo:
  num_generations: 8     # G
  beta: 0.04
  temperature_rollout: 0.8

reward:
  timeout: 3.0
  temperature_eval: 0.2

paths:
  checkpoints_dir: "checkpoints"
  results_dir: "results/h-e1"
  logs_dir: "logs"
  figures_dir: "docs/youra_research/h-e1/figures"

logging:
  reward_monitoring: "logs/reward_monitoring.jsonl"
  config_dump: "logs/config_dump.json"

bootstrap:
  n_boot: 1000
  seed: 42
  ci_level: 0.95
  gate_ratio: 1.5

bigcode_harness:
  pinned_commit: "FILL_BEFORE_RUN"   # record git rev-parse HEAD after checkout
```

### `code/config.py`

```python
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class TrainingConfig:
    lr: float = 1e-5
    batch_size: int = 4
    grad_accum: int = 8
    epochs: int = 3
    max_length: int = 1024
    max_new_tokens: int = 512
    seed: int = 42
    precision: str = "bfloat16"
    grad_clip: float = 1.0
    warmup_steps: int = 100
    lr_schedule: str = "cosine"


@dataclass
class GRPOConfig:
    num_generations: int = 8   # G
    beta: float = 0.04
    temperature_rollout: float = 0.8


@dataclass
class RewardConfig:
    timeout: float = 3.0
    temperature_eval: float = 0.2


@dataclass
class PathsConfig:
    checkpoints_dir: str = "checkpoints"
    results_dir: str = "results/h-e1"
    logs_dir: str = "logs"
    figures_dir: str = "docs/youra_research/h-e1/figures"


@dataclass
class BootstrapConfig:
    n_boot: int = 1000
    seed: int = 42
    ci_level: float = 0.95
    gate_ratio: float = 1.5


@dataclass
class ExperimentConfig:
    model_name: str = "deepseek-ai/deepseek-coder-7b-base"
    fallback_model_name: str = "deepseek-ai/deepseek-coder-1b3-base"
    ceiling_check_threshold: float = 0.90
    training: TrainingConfig = field(default_factory=TrainingConfig)
    grpo: GRPOConfig = field(default_factory=GRPOConfig)
    reward: RewardConfig = field(default_factory=RewardConfig)
    paths: PathsConfig = field(default_factory=PathsConfig)
    bootstrap: BootstrapConfig = field(default_factory=BootstrapConfig)
    reward_monitoring_path: str = "logs/reward_monitoring.jsonl"
    config_dump_path: str = "logs/config_dump.json"
    bigcode_harness_commit: str = "FILL_BEFORE_RUN"


# Convenience: flat dict for passing to train() functions (matches architecture signatures)
def make_config_dict(cfg: ExperimentConfig = None) -> dict:
    if cfg is None:
        cfg = ExperimentConfig()
    return {
        "model_name": cfg.model_name,
        "fallback_model_name": cfg.fallback_model_name,
        "ceiling_check_threshold": cfg.ceiling_check_threshold,
        "lr": cfg.training.lr,
        "batch_size": cfg.training.batch_size,
        "grad_accum": cfg.training.grad_accum,
        "epochs": cfg.training.epochs,
        "max_length": cfg.training.max_length,
        "max_new_tokens": cfg.training.max_new_tokens,
        "seed": cfg.training.seed,
        "precision": cfg.training.precision,
        "grad_clip": cfg.training.grad_clip,
        "warmup_steps": cfg.training.warmup_steps,
        "lr_schedule": cfg.training.lr_schedule,
        "num_generations": cfg.grpo.num_generations,
        "beta": cfg.grpo.beta,
        "temperature_rollout": cfg.grpo.temperature_rollout,
        "timeout": cfg.reward.timeout,
        "temperature_eval": cfg.reward.temperature_eval,
        "checkpoints_dir": cfg.paths.checkpoints_dir,
        "results_dir": cfg.paths.results_dir,
        "logs_dir": cfg.paths.logs_dir,
        "figures_dir": cfg.paths.figures_dir,
        "n_boot": cfg.bootstrap.n_boot,
        "bootstrap_seed": cfg.bootstrap.seed,
        "ci_level": cfg.bootstrap.ci_level,
        "gate_ratio": cfg.bootstrap.gate_ratio,
        "reward_monitoring_path": cfg.reward_monitoring_path,
        "config_dump_path": cfg.config_dump_path,
    }
```

---

## C-1-1: Data Pipeline Config [Complexity: 9, Budget: 1 subtask]

Applied: Single fixed config (EXISTENCE PoC pattern)

```python
DATA_CONFIG = {
    # APPS loading
    "hf_id": "codeparrot/apps",
    "split": "train",
    "min_test_cases": 1,

    # Tokenizer
    "max_length": 1024,
    "truncation": True,
    "padding": "max_length",

    # SFT format: problem description + canonical solution
    # prompt = problem["question"], target = problem["solutions"][0]

    # RLEF format: problem description + extracted test cases
    # prompt = problem["question"]
    # test_cases = list of (input_str, expected_output_str) parsed from problem["input_output"]

    # Difficulty bucket mapping
    "difficulty_map": {
        "introductory": "intro",
        "interview": "interview",
        "competition": "competition",
    },
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Data Pipeline Config | APPS loading params, tokenizer settings, SFT/RLEF format notes, difficulty map |

---

## C-5-1: Evaluation Runner Config [Complexity: 9, Budget: 1 subtask]

Applied: Single fixed config (EXISTENCE PoC pattern)

```python
EVAL_CONFIG = {
    # bigcode-harness task name mapping
    "tasks": {
        "humaneval": "humaneval",
        "mbpp": "mbpp",
        "lcb_easy": "livecodebench",
        "lcb_medium": "livecodebench",
        "lcb_hard": "livecodebench",
    },

    # LiveCodeBench difficulty filter
    # bigcode-harness livecodebench task supports --difficulty flag: easy / medium / hard
    # CLI usage: --tasks livecodebench --difficulty easy|medium|hard
    "lcb_difficulty_flag": {
        "lcb_easy": "easy",
        "lcb_medium": "medium",
        "lcb_hard": "hard",
    },

    # Eval generation params
    "n_samples": 1,
    "temperature": 0.2,

    # Output path pattern: results/h-e1/{model_tag}_{task_name}.json
    "output_pattern": "results/h-e1/{model_tag}_{task_name}.json",

    # Reproducibility: pin harness commit before running
    # Record with: git -C bigcode-evaluation-harness rev-parse HEAD
    "harness_commit": "FILL_BEFORE_RUN",

    # CLI template (formatted per model + task)
    # accelerate launch main.py \
    #   --model {checkpoint_path} \
    #   --tasks {task_name} \
    #   --n_samples 1 \
    #   --temperature 0.2 \
    #   --allow_code_execution \
    #   --metric_output_path results/h-e1/{model_tag}_{task_name}.json
    # For livecodebench tasks, append: --difficulty {easy|medium|hard}
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Evaluation Runner Config | Harness task names, LCB difficulty filter, CLI template, output paths, commit pin |
