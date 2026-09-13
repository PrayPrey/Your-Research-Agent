# Configuration: H-M2 (Update-Norm Parity Intervention)

**Applied**: Standard PyTorch dataclass config (no group-robustness-specific KB match found; searched "DL config patterns dataclass")

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1)
**Status**: Config class verified from actual code — field names/defaults confirmed, NOT taken from H-E1 spec
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: dataclass

**Verified from actual code** (differs from what spec might imply):
- `batch_size` default in H-E1 code is `32`, not tuned — H-M2 uses PRD-specified `128` for training throughput (non-standard override, justified by FR-2 training loop needs).
- H-E1 has `pretrained: bool = False` flag already present — H-M2 sets `True` and extends rather than reinventing.
- H-E1 has `imagenet_mean`/`imagenet_std` tuples — reused verbatim for FR-1.3 augmentation.
- `num_power_iter: int = 20` reused unchanged for `sharpness.py` compatibility.

---

## Inherited Configuration (Base Hypothesis)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class Config:
    data_root: str = "./data/waterbird_complete95_forest2water2"
    img_size: int = 224
    batch_size: int = 32
    imagenet_mean: tuple = (0.485, 0.456, 0.406)
    imagenet_std: tuple = (0.229, 0.224, 0.225)
    minority_groups: tuple = (1, 2)
    majority_groups: tuple = (0, 3)
    num_classes: int = 2
    pretrained: bool = False
    num_power_iter: int = 20
    seeds: tuple = (0, 1, 2, 3, 4)
    results_path: str = "results/sr_values.json"
    figure_path: str = "figures/sr_comparison.png"
```

---

## A-1..A-10: Training Config [Complexity: 90 total, Budget: 3 subtasks]

**Applied**: Standard PyTorch dataclass config, extends H-E1 `Config`

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass


@dataclass
class Config:
    # Inherited from H-E1 (verified from code)
    data_root: str = "./data/waterbird_complete95_forest2water2"
    img_size: int = 224
    imagenet_mean: tuple = (0.485, 0.456, 0.406)
    imagenet_std: tuple = (0.229, 0.224, 0.225)
    minority_groups: tuple = (1, 2)
    majority_groups: tuple = (0, 3)
    num_classes: int = 2
    pretrained: bool = True          # H-M2 needs trained model, override
    num_power_iter: int = 20
    seeds: tuple = (0, 1, 2, 3, 4)

    # New for H-M2 (training + parity intervention)
    batch_size: int = 128            # Non-standard: PRD FR-2.3 overrides H-E1 default (32)
    lr: float = 0.001
    momentum: float = 0.9
    weight_decay: float = 0.0001
    epochs: int = 100
    early_stop_patience: int = 10
    variants: tuple = ("baseline", "full_parity", "partial_parity")
    partial_scale: float = 0.5       # FR-4.3: 50% scaling toward equal update norms
    full_scale: float = 1.0          # FR-4.2: 100% scaling
    sr_eval_epoch: int = 50          # PRD success criteria checked at epoch 50
    num_groups: int = 4
    results_path: str = "results/summary.json"
    figure_dir: str = "figures/"


CONFIG = Config()
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-1 | Config dataclass | Extend H-E1 `Config` with training/parity fields (above) |
| C-2 | Variant scale mapping | `{"baseline": 0.0, "partial_parity": 0.5, "full_parity": 1.0}` dict used by `train.py` to select `UpdateNormParityTrainer(scale=...)` |
| C-3 | Success-criteria thresholds | Constants for gate check: `SR_THRESHOLD_PASS = 1.1`, `SR_THRESHOLD_BASELINE = 1.2`, `WGA_MIN = 0.21`, `P_VALUE_THRESHOLD = 0.05` |
