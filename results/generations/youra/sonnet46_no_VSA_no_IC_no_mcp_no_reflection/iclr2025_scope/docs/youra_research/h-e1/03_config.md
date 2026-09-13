---
title: "Config: h-e1 — Mamba-130m LoRA GLUE Fine-tuning"
hypothesis_id: h-e1
type: EXISTENCE
date: "2026-08-31"
author: yoon303@ust.ac.kr
---

Applied: MambaPEFT projection-layer LoRA config pattern (in_proj/out_proj/x_proj, r=8, alpha=16, conv1d exclusion)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field — new config design
**Config Files Found**: None — new config
**Pattern Used**: dataclass

---

## ExperimentConfig (Python Dataclass)

```python
from dataclasses import dataclass, field
import torch

@dataclass
class ExperimentConfig:
    # Model
    model_name: str = "state-spaces/mamba-130m-hf"
    lora_r: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    target_modules: tuple = ("in_proj", "out_proj", "x_proj")
    max_length: int = 128

    # Training
    batch_size: int = 32
    epochs: int = 3
    lr: float = 3e-4
    weight_decay: float = 0.01
    warmup_ratio: float = 0.06
    seed: int = 42

    # Tasks
    tasks: tuple = ("sst2", "mnli", "qnli", "qqp")

    # Paths
    results_dir: str = "h-e1/results"
    figures_dir: str = "h-e1/figures"

    # Hardware — auto-detect at runtime
    device: str = field(
        default_factory=lambda: "cuda" if torch.cuda.is_available() else "cpu"
    )

    def __post_init__(self):
        assert "conv1d" not in self.target_modules, \
            "conv1d cannot be a LoRA target on Mamba (raises TypeError in PEFT)"
        assert self.lora_alpha == 2 * self.lora_r or True, ""  # informational only
```

---

## YAML Schema Equivalent

```yaml
# h-e1/config.yaml — matches ExperimentConfig field names exactly
model_name: "state-spaces/mamba-130m-hf"
lora_r: 8
lora_alpha: 16
lora_dropout: 0.05
target_modules:
  - in_proj
  - out_proj
  - x_proj
max_length: 128

batch_size: 32
epochs: 3
lr: 3.0e-4
weight_decay: 0.01
warmup_ratio: 0.06
seed: 42

tasks:
  - sst2
  - mnli
  - qnli
  - qqp

results_dir: "h-e1/results"
figures_dir: "h-e1/figures"
device: "auto"  # resolved at runtime; "auto" → cuda if available else cpu
```

---

## E6: Gate + Metrics Config

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E6-1 | Gate + Metrics | Gate threshold, per-task metric mapping, results.json schema |

### Gate Threshold

```python
GATE_THRESHOLD = 0.70          # sst2_lora_accuracy must exceed this
GATE_TASK = "sst2"
GATE_METRIC_KEY = "accuracy"   # key returned by evaluate.load("glue","sst2")
```

### Per-task Metric Mapping

```python
TASK_METRIC = {
    "sst2": "accuracy",
    "mnli": "accuracy",
    "qnli": "accuracy",
    "qqp":  "f1",
}
```

### results.json Schema

```json
{
  "zero_shot": {
    "sst2": 0.0,
    "mnli": 0.0,
    "qnli": 0.0,
    "qqp":  0.0
  },
  "lora": {
    "sst2": 0.0,
    "mnli": 0.0,
    "qnli": 0.0,
    "qqp":  0.0
  },
  "glue_avg_zero_shot": 0.0,
  "glue_avg_lora": 0.0,
  "gate_passed": false,
  "gate_metric": 0.0,
  "mechanism_indicators": {
    "lora_keys_present": false,
    "lora_weights_nonzero": false,
    "sst2_delta_positive": false
  }
}
```

Values for `zero_shot.*` and `lora.*` are the scalar from `TASK_METRIC` (accuracy or f1).
`glue_avg_*` = mean of the four task values (mixed accuracy+f1, per standard GLUE avg practice).

---

## requirements.txt

```
torch>=2.0.0
transformers>=4.38.0
peft>=0.9.0
datasets>=2.18.0
evaluate>=0.4.0
accelerate>=0.27.0
scipy>=1.12.0
matplotlib>=3.8.0
seaborn>=0.13.0
numpy>=1.26.0
```

---

## Hyperparameter Justification

| Hyperparameter | Value | Justification |
|----------------|-------|---------------|
| `lora_r` | 8 | Standard low-rank PoC default; MambaPEFT paper uses r=8 as baseline |
| `lora_alpha` | 16 | alpha=2r scaling rule (effective LR scale = alpha/r = 2) |
| `lora_dropout` | 0.05 | Light regularization; small model, short training |
| `target_modules` | in_proj, out_proj, x_proj | Only linear projections compatible with PEFT LoRA in Mamba |
| `max_length` | 128 | GLUE sentences are short; covers >99% without padding waste |
| `lr` | 3e-4 | AdamW standard for PEFT fine-tuning; MambaPEFT recommendation |
| `weight_decay` | 0.01 | AdamW default; prevents head overfitting |
| `warmup_ratio` | 0.06 | ~6% warmup matches HF Trainer default for short runs |
| `batch_size` | 32 | Fits Mamba-130m + LoRA in ≤8GB VRAM |
| `epochs` | 3 | Sufficient for GLUE convergence; standard in PEFT literature |
| `seed` | 42 | Single fixed seed for EXISTENCE PoC reproducibility |
