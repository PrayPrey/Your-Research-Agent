# Config: h-c2

**Type:** CONDITION | Budget: 3 subtasks

Applied: No matching KB pattern (best sim 0.44, unrelated diffusion repos) — using field names as fixed in 03_architecture.md verbatim.

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-m1) referenced, but green-field in practice
**Status**: h-m1/code/ absent on disk (confirmed in architecture doc) — no actual config classes to verify. h-c2/code/ also empty. Treated as green-field; field names below are taken directly from h-c2's own architecture.md (already authoritative for this hypothesis).
**Config Files Found**: None
**Pattern Used**: dataclass

---

## A-1: Config & Seeding [Complexity: 4, Budget: 3]

**Applied**: Standard PyTorch dataclass config; values from PRD (batch_size=128, r_threshold=0.7, Bonferroni α=0.05/3, checkpoint every 10 epochs).

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    seed: int = 42
    batch_size: int = 128
    checkpoint_every: int = 10
    proj_dim: int = 2048              # TRAK random projection dim
    probes_per_mode: int = 1000
    r_threshold: float = 0.7
    bonferroni_alpha: float = 0.05 / 3  # 3 pairwise comparisons
    n_boot: int = 1000                # bootstrap resamples for CI
    probe_subset_fraction: float = 0.5  # ABL-2
    min_test_accuracy: float = 0.85   # FR-1 gate
    data_root: str = "./data"
    ckpt_dir: str = "./h-c2/checkpoints"
    fig_dir: str = "./h-c2/figures"


@dataclass
class ModelTrainConfig:
    name: str          # 'resnet18' | 'vit_small' | 'convnext_tiny'
    epochs: int
    lr: float
    optimizer: str      # 'sgd' | 'adamw'


# Per-model defaults (NFR-1: <4h total training on single GPU)
MODEL_CONFIGS: dict[str, ModelTrainConfig] = {
    "resnet18": ModelTrainConfig(name="resnet18", epochs=30, lr=0.01, optimizer="sgd"),
    "vit_small": ModelTrainConfig(name="vit_small", epochs=20, lr=3e-4, optimizer="adamw"),
    "convnext_tiny": ModelTrainConfig(name="convnext_tiny", epochs=20, lr=3e-4, optimizer="adamw"),
}
```

**Non-standard**: ViT-Small/ConvNeXt-Tiny use AdamW + lower lr (3e-4) — standard for transformer/modern-CNN fine-tuning from pretrained weights; ResNet-18 uses SGD + higher lr (0.01), conventional for CNN-from-scratch-ish fine-tuning on CIFAR-10.

### YAML Representation (optional CLI override)

```yaml
seed: 42
batch_size: 128
checkpoint_every: 10
proj_dim: 2048
probes_per_mode: 1000
r_threshold: 0.7
bonferroni_alpha: 0.016667
n_boot: 1000
probe_subset_fraction: 0.5
min_test_accuracy: 0.85

models:
  resnet18:
    epochs: 30
    lr: 0.01
    optimizer: sgd
  vit_small:
    epochs: 20
    lr: 3e-4
    optimizer: adamw
  convnext_tiny:
    epochs: 20
    lr: 3e-4
    optimizer: adamw
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | ExperimentConfig dataclass | Global hyperparams (seed, batch_size, thresholds, dirs) |
| C-1-2 | ModelTrainConfig + MODEL_CONFIGS | Per-model (resnet18/vit_small/convnext_tiny) epochs/lr/optimizer |
| C-1-3 | Global seeding utility | `set_seed(seed)` seeding torch/numpy/random/cuda + deterministic dataloader flags (NFR-2) |
