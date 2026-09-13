# Config: H-E1 (EXISTENCE PoC)

**Date:** 2026-08-29
**Hypothesis:** H-E1 — Gradient subspace alignment (spurious >70%, core <30% at epoch 10)

Applied: EXISTENCE PoC pattern — single fixed hardcoded dict, no hyperparameter search (Archon KB unavailable this session).

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — new config design, no existing code
**Config Files Found**: None
**Pattern Used**: dataclass (single fixed instance, no variants)

---

## ExperimentConfig (Python Dataclass)

PoC: single fixed config, 1 seed, no hyperparameter variation.

```python
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    # Reproducibility
    seed: int = 42

    # Data
    data_root: str = "./data/waterbirds"
    batch_size: int = 128
    num_workers: int = 4
    image_size: int = 224
    # ImageNet normalization
    norm_mean: tuple = (0.485, 0.456, 0.406)
    norm_std: tuple = (0.229, 0.224, 0.225)

    # Model
    num_classes: int = 2
    pretrained: bool = True

    # Optimizer (SGD, from group_DRO defaults)
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    step_milestones: tuple = (60, 75)
    gamma: float = 0.1

    # Training
    num_epochs: int = 90
    accumulation_epochs: int = 10   # epochs 1-10: gradient accumulation window
    subspace_rank: int = 50         # top-k SVD directions
    log_epochs: tuple = (5, 10, 45)

    # Paths
    checkpoint_dir: str = "./checkpoints"
    figures_dir: str = "./figures"
    csv_log_path: str = "./logs/alignment.csv"

    # Gate thresholds (PoC success criteria)
    spurious_gate: float = 0.70
    core_gate: float = 0.30

CONFIG = ExperimentConfig()
```

## YAML Schema Equivalent

```yaml
seed: 42

data:
  root: "./data/waterbirds"
  batch_size: 128
  num_workers: 4
  image_size: 224
  norm_mean: [0.485, 0.456, 0.406]
  norm_std: [0.229, 0.224, 0.225]

model:
  num_classes: 2
  pretrained: true

optimizer:
  lr: 0.001
  momentum: 0.9
  weight_decay: 0.0001
  step_milestones: [60, 75]
  gamma: 0.1

training:
  num_epochs: 90
  accumulation_epochs: 10
  subspace_rank: 50
  log_epochs: [5, 10, 45]

paths:
  checkpoint_dir: "./checkpoints"
  figures_dir: "./figures"
  csv_log_path: "./logs/alignment.csv"

gate:
  spurious_threshold: 0.70
  core_threshold: 0.30
```

---

## A-1: Setup + Data Loading [Complexity: 10, Budget: 10]

**Applied**: Standard PyTorch Dataset/DataLoader defaults, ImageNet transforms.

### Configuration

Uses `ExperimentConfig.data_root`, `batch_size`, `image_size`, `norm_mean/std` above. No extra fields needed.

Train transform: `RandomResizedCrop(224)` + `RandomHorizontalFlip` + normalize.
Eval transform: `Resize(256)` + `CenterCrop(224)` + normalize.

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | WaterbirdsDataset | Load CSV/metadata, return (img, label, group) |
| C-1-2 | Transforms | Train/eval transform pipelines from config |
| C-1-3 | DataLoaders | Build train/val/test loaders with seed-fixed shuffling |
| C-1-4 | get_direction_pairs | Index pairs for spurious (bg-diff, label-same) and core (bird-diff) groups |

---

## A-4: Direction Computation [Complexity: 10, Budget: 10]

**Applied**: Group-paired gradient averaging (standard from experiment brief).

### Configuration

No new hyperparameters — reuses `subspace_rank` for output dim check and `batch_size` for pair-batch gradient eval. Uses existing `ExperimentConfig`.

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Pair sampling | Sample fixed set of spurious/core pairs from get_direction_pairs (seeded) |
| C-4-2 | Per-pair gradient | Forward+backward on single pair, extract flat grad via get_flat_grad |
| C-4-3 | Direction averaging | Average per-pair gradients into single direction vector per type |
| C-4-4 | Normalization | L2-normalize direction vectors before cosine similarity use |

---

## Logging Configuration

```python
LOGGING = {
    "csv_path": CONFIG.csv_log_path,
    "csv_columns": ["epoch", "spurious_alignment", "core_alignment"],
    "console_level": "INFO",
    "log_every_n_steps": 100,  # batch-level training loss logging
}
```

Checkpoint saved once at `epoch == accumulation_epochs` (epoch 10) to `{checkpoint_dir}/epoch10.pt`.
