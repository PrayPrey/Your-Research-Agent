# Configuration: H-M3 (Task-Conditioned SSM Training)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: YAML (loaded into dataclasses)

**Applied**: Standard PyTorch/HuggingFace training config conventions (AdamW + linear warmup)

---

## Config Schema (YAML)

```yaml
# config.yaml — H-M3 TC-SSM experiment

model:
  name: "state-spaces/mamba-130m"
  d_model: 768
  n_layer: 24
  d_state: 16
  d_conv: 4
  expand: 2

task_conditioning:
  rank: 32
  n_tasks: 5              # BoolQ, CB, COPA, RTE, WiC

baseline_lora:
  r: 16
  alpha: 32
  target_modules: ["out_proj", "in_proj"]

conversion_training:
  source_model: "gpt2"    # or "bert-base-uncased"
  loss_weights:
    kl: 1.0
    mse_hidden: 1.0
    adaptation_reg: 0.1

few_shot_training:
  optimizer: "adamw"
  lr: 2.0e-5
  betas: [0.9, 0.999]
  weight_decay: 0.01
  warmup_ratio: 0.1
  lr_schedule: "linear"
  batch_size: 8
  max_steps: 100
  grad_clip: 1.0
  dropout: 0.1
  seeds: [42, 123, 2024]
  checkpoint_every: 25

few_shot_eval:
  k_shots: [8, 16]
  sample_selection: "stratified_random"
  tasks: ["boolq", "cb", "copa", "rte", "wic"]

hardware:
  device: "cuda"
  precision: "bf16"
  gradient_checkpointing: true
```

---

## Dataclasses (Python)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ModelConfig:
    name: str = "state-spaces/mamba-130m"
    d_model: int = 768
    n_layer: int = 24
    d_state: int = 16
    d_conv: int = 4
    expand: int = 2

@dataclass
class TaskConditioningConfig:
    rank: int = 32          # Source: H-M2 optimal rank
    n_tasks: int = 5

@dataclass
class BaselineLoRAConfig:
    r: int = 16
    alpha: int = 32
    target_modules: List[str] = field(default_factory=lambda: ["out_proj", "in_proj"])

@dataclass
class ConversionTrainingConfig:
    source_model: str = "gpt2"
    kl_weight: float = 1.0
    mse_weight: float = 1.0
    adaptation_reg_weight: float = 0.1

@dataclass
class FewShotTrainingConfig:
    lr: float = 2e-5
    beta1: float = 0.9
    beta2: float = 0.999
    weight_decay: float = 0.01
    warmup_ratio: float = 0.1
    batch_size: int = 8
    max_steps: int = 100
    grad_clip: float = 1.0
    dropout: float = 0.1
    seeds: List[int] = field(default_factory=lambda: [42, 123, 2024])
    checkpoint_every: int = 25

@dataclass
class FewShotEvalConfig:
    k_shots: List[int] = field(default_factory=lambda: [8, 16])
    tasks: List[str] = field(default_factory=lambda: ["boolq", "cb", "copa", "rte", "wic"])

@dataclass
class HardwareConfig:
    device: str = "cuda"
    precision: str = "bf16"
    gradient_checkpointing: bool = True
```

---

## Hyperparameter Table

| Param | Default | Source |
|-------|---------|--------|
| d_model | 768 | Mamba-130M spec (state-spaces/mamba) |
| n_layer | 24 | Mamba-130M spec |
| d_state | 16 | Mamba-130M spec |
| d_conv | 4 | Mamba-130M spec |
| expand | 2 | Mamba-130M spec |
| task_conditioning.rank | 32 | H-M2 validated optimum |
| n_tasks | 5 | SuperGLUE task count (BoolQ, CB, COPA, RTE, WiC) |
| lora.r / alpha | 16 / 32 | huggingface/peft baseline |
| lr | 2e-5 | PEFT/LoRA recommended, PRD 02c |
| warmup_ratio | 0.1 | PRD 02c |
| batch_size | 8 | Few-shot constraint, PRD 02c |
| max_steps | 100 | Hypothesis constraint (<100 steps) |
| grad_clip | 1.0 | PRD 02c |
| dropout | 0.1 | PRD 02c |
| seeds | [42, 123, 2024] | MECHANISM hypothesis requires 3 seeds |
| k_shots | [8, 16] | PRD 02c few-shot protocol |
| checkpoint_every | 25 | PRD 03 risk mitigation (OOM/divergence recovery) |
| precision | bf16 | Mamba supports bf16 natively |

---

## Validation Constraints

- `task_conditioning.rank` must be in `{16, 32, 64}` (H-M2 validated range)
- `n_tasks == len(few_shot_eval.tasks)` (must equal 5)
- `max_steps <= 100` (hypothesis gate condition; hard fail if exceeded)
- `batch_size * max_steps >= max(k_shots)` per task (ensure at least one pass over few-shot set)
- `warmup_ratio * max_steps >= 1` (avoid zero warmup steps)
- `len(seeds) == 3` (MECHANISM hypothesis statistical requirement)
- `precision in {"bf16", "fp16", "fp32"}`

---

## Environment Requirements

| Resource | Requirement |
|----------|-------------|
| GPU | 1x A100 40GB (or equivalent, e.g., A6000 48GB) |
| VRAM | ~8-12GB (130M model, bf16, batch=8) — headroom for conversion training with source transformer loaded concurrently |
| Disk | ~5GB (model checkpoints + SuperGLUE cache) |
| Runtime | 4-6 hours total (conversion + few-shot x 3 seeds x 5 tasks x 2 k-shots) |
| Python deps | `torch>=2.1`, `transformers`, `mamba-ssm`, `datasets`, `evaluate`, `scikit-learn` |
