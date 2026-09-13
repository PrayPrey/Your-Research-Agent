# Config: H-M1 Adversarial BAI Probing

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None
**Pattern Used**: YAML (loaded into dataclass)

**Applied**: Standard PyTorch/HuggingFace training config defaults (no KB match for GRL-specific pattern).

---

## A-1: Adversarial Probing Config [Complexity: 3, Budget: 3]

Single fixed config per model (no HP grid — MECHANISM test with fixed hyperparameters, 3-seed reproducibility only).

### YAML Schema

```yaml
# config.yaml
model:
  name: str              # one of: meta-llama/Meta-Llama-3-8B, mistralai/Mistral-7B-v0.1, Qwen/Qwen2-7B
  dtype: str              # bfloat16
  device: str              # cuda

optimizer:
  type: str                # adamw
  lr: float                # 1e-4
  weight_decay: float      # 0.01
  warmup_steps: int        # 100

training:
  batch_size: int          # 32
  epochs: int               # 3
  seeds: list[int]         # [42, 123, 456]
  grl_alpha_schedule: str   # linear_0_to_1_epoch1
  loss_lambda: float        # 1.0
  checkpoint_every_epoch: bool  # true

dataset:
  hh_rlhf_subsets: list[str]
    # [helpful-base, helpful-online, helpful-rejection-sampled, harmless-base]
  val_dataset: str          # allenai/reward-bench
  bai_label_source: str     # h-e1_agency_proxies
  bai_binarize: str         # median_split

paths:
  activation_cache_dir: str
  checkpoint_dir: str
  output_dir: str
```

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class ModelConfig:
    name: str
    dtype: str = "bfloat16"
    device: str = "cuda"

@dataclass
class OptimizerConfig:
    type: str = "adamw"
    lr: float = 1e-4
    weight_decay: float = 0.01
    warmup_steps: int = 100

@dataclass
class TrainingConfig:
    batch_size: int = 32
    epochs: int = 3
    seeds: list = field(default_factory=lambda: [42, 123, 456])
    grl_alpha_schedule: str = "linear_0_to_1_epoch1"  # alpha: 0->1 over epoch 1, then fixed at 1
    loss_lambda: float = 1.0
    checkpoint_every_epoch: bool = True

@dataclass
class DatasetConfig:
    hh_rlhf_subsets: list = field(default_factory=lambda: [
        "helpful-base", "helpful-online", "helpful-rejection-sampled", "harmless-base"
    ])
    val_dataset: str = "allenai/reward-bench"
    bai_label_source: str = "h-e1_agency_proxies"
    bai_binarize: str = "median_split"

@dataclass
class PathConfig:
    activation_cache_dir: str = "./cache/activations"
    checkpoint_dir: str = "./checkpoints"
    output_dir: str = "./results"

@dataclass
class ExperimentConfig:
    model: ModelConfig
    optimizer: OptimizerConfig = field(default_factory=OptimizerConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    paths: PathConfig = field(default_factory=PathConfig)
```

### Validation Constraints

| Field | Constraint |
|---|---|
| `model.name` | must be one of the 3 allocated HF model IDs |
| `optimizer.lr` | > 0 |
| `training.batch_size` | > 0, divides dataset without excessive drop (<5% last-batch loss) |
| `training.epochs` | == 3 (fixed per PRD, not tunable) |
| `training.seeds` | exactly 3 seeds, no duplicates |
| `training.loss_lambda` | > 0 |
| `dataset.hh_rlhf_subsets` | all 4 subsets required, non-empty |
| `dataset.bai_binarize` | must be "median_split" (per FR-2) |
| GRL alpha | monotonic 0→1 over epoch 1 steps, clamped to 1.0 for epochs 2-3 |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | GRL alpha scheduler | Implement linear alpha ramp: `alpha = min(1.0, step / steps_per_epoch)` during epoch 1, else 1.0 |
| C-1-2 | Config loader/validator | YAML -> dataclass loader with constraint checks above |
| C-1-3 | Per-model config instantiation | Generate 3 concrete YAML files (one per model) from schema |

---

## Example Configs (Per Model)

```yaml
# llama3_8b.yaml
model:
  name: meta-llama/Meta-Llama-3-8B
  dtype: bfloat16
  device: cuda
optimizer: {type: adamw, lr: 1.0e-4, weight_decay: 0.01, warmup_steps: 100}
training: {batch_size: 32, epochs: 3, seeds: [42, 123, 456], grl_alpha_schedule: linear_0_to_1_epoch1, loss_lambda: 1.0, checkpoint_every_epoch: true}
dataset:
  hh_rlhf_subsets: [helpful-base, helpful-online, helpful-rejection-sampled, harmless-base]
  val_dataset: allenai/reward-bench
  bai_label_source: h-e1_agency_proxies
  bai_binarize: median_split
paths: {activation_cache_dir: ./cache/activations/llama3_8b, checkpoint_dir: ./checkpoints/llama3_8b, output_dir: ./results/llama3_8b}
```

```yaml
# mistral_7b.yaml
model:
  name: mistralai/Mistral-7B-v0.1
  dtype: bfloat16
  device: cuda
optimizer: {type: adamw, lr: 1.0e-4, weight_decay: 0.01, warmup_steps: 100}
training: {batch_size: 32, epochs: 3, seeds: [42, 123, 456], grl_alpha_schedule: linear_0_to_1_epoch1, loss_lambda: 1.0, checkpoint_every_epoch: true}
dataset:
  hh_rlhf_subsets: [helpful-base, helpful-online, helpful-rejection-sampled, harmless-base]
  val_dataset: allenai/reward-bench
  bai_label_source: h-e1_agency_proxies
  bai_binarize: median_split
paths: {activation_cache_dir: ./cache/activations/mistral_7b, checkpoint_dir: ./checkpoints/mistral_7b, output_dir: ./results/mistral_7b}
```

```yaml
# qwen2_7b.yaml
model:
  name: Qwen/Qwen2-7B
  dtype: bfloat16
  device: cuda
optimizer: {type: adamw, lr: 1.0e-4, weight_decay: 0.01, warmup_steps: 100}
training: {batch_size: 32, epochs: 3, seeds: [42, 123, 456], grl_alpha_schedule: linear_0_to_1_epoch1, loss_lambda: 1.0, checkpoint_every_epoch: true}
dataset:
  hh_rlhf_subsets: [helpful-base, helpful-online, helpful-rejection-sampled, harmless-base]
  val_dataset: allenai/reward-bench
  bai_label_source: h-e1_agency_proxies
  bai_binarize: median_split
paths: {activation_cache_dir: ./cache/activations/qwen2_7b, checkpoint_dir: ./checkpoints/qwen2_7b, output_dir: ./results/qwen2_7b}
```
