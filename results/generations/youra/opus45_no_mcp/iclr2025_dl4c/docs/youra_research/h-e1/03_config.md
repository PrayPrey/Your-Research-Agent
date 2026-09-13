# Configuration Spec: h-e1 (Error-Type Gating)

**Type:** EXISTENCE (PoC) — single fixed config, no sweep
**Format:** Python Dataclass

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - new config design (no base hypothesis, no existing config files)
**Config Files Found:** None
**Pattern Used:** dataclass

**Applied:** Standard RLTF/PPO fine-tuning config pattern (from experiment brief, no KB access this session)

---

## Config Definitions

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class ModelConfig:
    base_model: str = "Salesforce/codet5-large"
    max_input_length: int = 512
    max_output_length: int = 256


@dataclass
class TrainingConfig:
    learning_rate: float = 5e-5
    batch_size: int = 8
    epochs: int = 5
    total_steps: int = 50_000          # 5 epochs x 10,000 steps
    warmup_steps: int = 500
    optimizer: str = "AdamW"
    adam_beta1: float = 0.9
    adam_beta2: float = 0.999
    weight_decay: float = 0.01
    entropy_bonus: float = 0.01        # PPO entropy coefficient
    seed: int = 42


@dataclass
class RewardConfig:
    fine_penalty: float = -1.0         # penalty at error line
    coarse_penalty: float = -0.1       # uniform penalty elsewhere / U_ignore gated
    pass_reward: float = 1.0
    gating_mode: str = "fine_gated"    # 'fine_always' | 'fine_gated'


@dataclass
class ErrorCategoryConfig:
    u_line: List[str] = field(default_factory=lambda: [
        "SyntaxError", "IndentationError", "NameError", "TypeError",
        "AttributeError", "KeyError", "IndexError",
    ])
    u_ignore: List[str] = field(default_factory=lambda: [
        "RuntimeError", "RecursionError", "MemoryError",
        "TimeoutError", "AssertionError",
    ])


@dataclass
class EvalConfig:
    checkpoint_interval: int = 1000    # steps
    pass_at_1_threshold: float = 0.30
    test_set_size: int = 5000
    execution_timeout: int = 30        # seconds


@dataclass
class ExperimentConfig:
    seeds: List[int] = field(default_factory=lambda: [42])
    conditions: List[str] = field(default_factory=lambda: ["fine_always", "fine_gated"])
    gpu: str = "A100-40GB"
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    reward: RewardConfig = field(default_factory=RewardConfig)
    error_categories: ErrorCategoryConfig = field(default_factory=ErrorCategoryConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)
```

## YAML Equivalent (reference only, dataclass is source of truth)

```yaml
experiment:
  seeds: [42]
  conditions: ["fine_always", "fine_gated"]
  gpu: "A100-40GB"
model:
  base_model: "Salesforce/codet5-large"
  max_input_length: 512
  max_output_length: 256
training:
  learning_rate: 5.0e-5
  batch_size: 8
  epochs: 5
  total_steps: 50000
  warmup_steps: 500
  optimizer: "AdamW"
  adam_beta1: 0.9
  adam_beta2: 0.999
  weight_decay: 0.01
  entropy_bonus: 0.01
  seed: 42
reward:
  fine_penalty: -1.0
  coarse_penalty: -0.1
  pass_reward: 1.0
  gating_mode: "fine_gated"
error_categories:
  u_line: ["SyntaxError", "IndentationError", "NameError", "TypeError", "AttributeError", "KeyError", "IndexError"]
  u_ignore: ["RuntimeError", "RecursionError", "MemoryError", "TimeoutError", "AssertionError"]
eval:
  checkpoint_interval: 1000
  pass_at_1_threshold: 0.30
  test_set_size: 5000
  execution_timeout: 30
```

## Default Value Sources

| Field | Value | Source |
|---|---|---|
| learning_rate, optimizer, beta1/2, weight_decay | 5e-5, AdamW, 0.9/0.999, 0.01 | RLTF paper (Liu et al., NeurIPS 2023) default |
| batch_size, epochs, total_steps, warmup_steps | 8, 5, 50000, 500 | RLTF training protocol (02c_experiment_brief.md) |
| fine_penalty, coarse_penalty, pass_reward | -1.0, -0.1, +1.0 | RLTF eqs. 4-5 |
| u_line / u_ignore error lists | see above | RLTF Appendix B, extended in brief with KeyError/IndexError/AssertionError |
| max_input_length, max_output_length | 512, 256 | CodeT5 tokenizer limits used for APPS |
| pass_at_1_threshold | 0.30 | Gate condition (30% pass@1) |
| test_set_size | 5000 | APPS full test set |
| seeds | [42] | Single-seed PoC per EXISTENCE rules |

## Validation Rules

- `training.total_steps == training.epochs * (train_set_size / training.batch_size)` — must hold given train_set_size=5000, batch_size=8 (~625 steps/epoch; brief specifies 10,000/epoch as approximation, use `total_steps=50000` as authoritative).
- `reward.gating_mode in {"fine_always", "fine_gated"}` — no other values permitted.
- `error_categories.u_line` and `error_categories.u_ignore` must be disjoint sets.
- `eval.pass_at_1_threshold` in (0, 1].
- `training.warmup_steps < training.total_steps`.
- `experiment.conditions` must exactly match `{"fine_always", "fine_gated"}` for this PoC (both required for gate comparison).
- `experiment.seeds` length == 1 for PoC (multi-seed reserved for Phase 5).

## Subtasks

No subtask decomposition — EXISTENCE hypothesis uses single fixed config only.
