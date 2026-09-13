# Config: H-M1 (MECHANISM)

Applied: fixed-hyperparameter dataclass pattern (standard PyTorch training config, no grid/sweep — MECHANISM test uses single protocol inherited from H-E1)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing config code; H-E1 code not present on disk (spec-only reference)
**Config Files Found**: None
**Pattern Used**: dataclass

---

## A-1: Dataset setup [Complexity: 10, Budget: 1 subtask]

**Applied**: Waterbirds standard preprocessing (224x224, ImageNet norm) — from PRD FR-1

### Configuration (Python Dataclass)

```python
@dataclass
class Config:
    # Reproducibility
    seeds: tuple[int, ...] = (42, 123, 456)

    # Data
    data_root: str = "./data/waterbirds_v1.0"
    image_size: int = 224
    imagenet_mean: tuple[float, float, float] = (0.485, 0.456, 0.406)
    imagenet_std: tuple[float, float, float] = (0.229, 0.224, 0.225)
    batch_size: int = 128
    num_workers: int = 4

    # Model
    num_classes: int = 2
    pretrained_weights: str = "IMAGENET1K_V1"
    target_layer: str = "layer4"

    # Optimizer (SGD, inherited from H-E1 protocol)
    lr: float = 0.001
    momentum: float = 0.9
    weight_decay: float = 1e-4
    step_sizes: tuple[int, ...] = (60, 120)
    gamma: float = 0.1

    # Training
    epochs: int = 50

    # Gate check
    early_epoch_range: tuple[int, int] = (1, 10)
    ratio_threshold: float = 1.5

    # Output
    output_dir: str = "./h-m1/results"
    figures_dir: str = "./h-m1/figures"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1-1 | Dataset download + mask loading config | `download_waterbirds`, `WaterbirdsDataset` transform pipeline (resize 224, ImageNet normalize), `get_dataloaders(root_dir, batch_size)` using `Config.data_root`, `image_size`, `batch_size`, `num_workers` |

---

## Notes

- Single fixed config, no hyperparameter sweep (MECHANISM hypothesis inherits verified training protocol from H-E1, per PRD Dependencies section).
- 3 seeds run sequentially via `run_training(config, seed)` in `train.py`, not part of dataset config.
- No YAML — dataclass with in-code defaults is sufficient (small, single-experiment config; Phase 4 copies directly into `config.py`).
