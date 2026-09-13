# Configuration Design: H-E1

**Hypothesis**: Per-sample loss trajectory features predict minority group membership (AUROC > 0.75)
**Type**: EXISTENCE (PoC)
**Date**: 2026-04-14

Applied: Standard PyTorch defaults (Archon KB matched generic PyTorch docs; no domain-specific pattern found)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## Inherited Configuration

None - H-E1 is the foundation hypothesis with no prior codebase.

---

## A-2: Data Loading [Complexity: 10, Budget: 2 subtasks]

Applied: Standard PyTorch defaults

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class Config:
    # Dataset
    data_root: str = "./data"
    dataset: str = "waterbirds"
    num_workers: int = 4
    pin_memory: bool = True
    # Preprocessing
    train_crop_size: int = 224
    eval_resize: int = 256
    eval_crop_size: int = 224
    # Non-standard: ImageNet normalization constants (fixed values, not learned)
    img_mean: tuple = (0.485, 0.456, 0.406)
    img_std: tuple = (0.229, 0.224, 0.225)
    # Model
    model_name: str = "resnet50"
    num_classes: int = 2
    # Training
    seed: int = 42
    epochs: int = 20
    trajectory_epochs: int = 5
    batch_size: int = 128
    lr: float = 0.001
    momentum: float = 0.9
    weight_decay: float = 0.0001
    # Evaluation
    n_folds: int = 5
    auroc_threshold: float = 0.75
    # Non-standard: max_iter=1000 ensures convergence for imbalanced minority classification
    lr_clf_max_iter: int = 1000
    # Output
    output_dir: str = "./results"
    figures_dir: str = "./figures"


def get_config() -> Config:
    return Config()
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Dataset Config | data_root, dataset name, split handling, group label tracking |
| C-2-2 | Transform Config | train/eval transform parameters, ImageNet normalization constants |

---

## A-6: Visualization + Gate Check [Complexity: 9, Budget: 1 subtask]

Applied: Standard matplotlib defaults

### Configuration (Python Dataclass)

Config fields (added to the same `Config` dataclass above):

```python
# Visualization (add to Config dataclass)
fig_dpi: int = 300
fig_format: str = "png"
fig_gate_filename: str = "gate_metrics.png"
fig_trajectory_filename: str = "loss_trajectories.png"
fig_roc_filename: str = "roc_curve.png"
fig_features_filename: str = "feature_distributions.png"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Visualization + Gate Config | figure output paths, DPI, format, gate threshold for pass/fail |

---

## Complete Config (copy-paste ready for `code/config.py`)

```python
from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class Config:
    # Dataset
    data_root: str = "./data"
    dataset: str = "waterbirds"
    num_workers: int = 4
    pin_memory: bool = True
    # Preprocessing
    train_crop_size: int = 224
    eval_resize: int = 256
    eval_crop_size: int = 224
    img_mean: Tuple[float, float, float] = (0.485, 0.456, 0.406)
    img_std: Tuple[float, float, float] = (0.229, 0.224, 0.225)
    # Model
    model_name: str = "resnet50"
    num_classes: int = 2
    # Training
    seed: int = 42
    epochs: int = 20
    trajectory_epochs: int = 5
    batch_size: int = 128
    lr: float = 0.001
    momentum: float = 0.9
    weight_decay: float = 0.0001
    # Evaluation
    n_folds: int = 5
    auroc_threshold: float = 0.75
    lr_clf_max_iter: int = 1000
    # Output
    output_dir: str = "./results"
    figures_dir: str = "./figures"
    # Visualization
    fig_dpi: int = 300
    fig_format: str = "png"
    fig_gate_filename: str = "gate_metrics.png"
    fig_trajectory_filename: str = "loss_trajectories.png"
    fig_roc_filename: str = "roc_curve.png"
    fig_features_filename: str = "feature_distributions.png"


def get_config() -> Config:
    return Config()
```

---

## Hyperparameter Documentation

| Parameter | Value | Source |
|-----------|-------|--------|
| lr | 0.001 | kohpangwei/group_DRO (official Waterbirds config) |
| momentum | 0.9 | kohpangwei/group_DRO |
| weight_decay | 0.0001 | kohpangwei/group_DRO |
| batch_size | 128 | kohpangwei/group_DRO |
| epochs | 20 | PoC (literature uses 300; 20 sufficient for trajectory divergence) |
| trajectory_epochs | 5 | Phase 2C experiment brief |
| n_folds | 5 | Phase 2C experiment brief |
| auroc_threshold | 0.75 | Phase 2B gate condition |
| seed | 42 | Standard reproducibility default |
| lr_clf_max_iter | 1000 | sklearn LogisticRegression convergence for imbalanced data |

---

*Config for EXISTENCE hypothesis H-E1*
*Green-field project - new config schema*
*Subtasks used: 3/3*
