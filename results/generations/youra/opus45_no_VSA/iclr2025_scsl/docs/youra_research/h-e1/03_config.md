# Configuration: H-E1 (EXISTENCE / PoC)

**Hypothesis:** SR₀ ≈ 1.0 at initialization
**Applied:** No matching KB pattern found (generic diffusion/SD configs only) — standard PyTorch dataclass config used.

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field - no existing code to analyze
**Config Files Found:** None - new config
**Pattern Used:** dataclass

---

## Config (Python Dataclass)

Single fixed config, no hyperparameter search (EXISTENCE rule).

```python
from dataclasses import dataclass, field


@dataclass
class Config:
    # Data
    data_root: str = "./data/waterbird_complete95_forest2water2"
    img_size: int = 224
    batch_size: int = 32
    imagenet_mean: tuple[float, float, float] = (0.485, 0.456, 0.406)
    imagenet_std: tuple[float, float, float] = (0.229, 0.224, 0.225)

    # Groups: 0=landbird/land, 1=landbird/water, 2=waterbird/land, 3=waterbird/water
    minority_groups: tuple[int, int] = (1, 2)
    majority_groups: tuple[int, int] = (0, 3)

    # Model
    num_classes: int = 2
    pretrained: bool = False  # random init required for SR0 measurement

    # Sharpness (power iteration)
    num_power_iter: int = 20

    # Experiment
    seeds: tuple[int, ...] = (0, 1, 2, 3, 4)
    epochs: int = 0  # measurement-only, no training

    # Output
    results_path: str = "results/sr_values.json"
    figure_path: str = "figures/sr_comparison.png"


CONFIG = Config()
```

---

## YAML Schema (equivalent, reference only)

```yaml
data_root: "./data/waterbird_complete95_forest2water2"
img_size: 224
batch_size: 32
imagenet_mean: [0.485, 0.456, 0.406]
imagenet_std: [0.229, 0.224, 0.225]
minority_groups: [1, 2]
majority_groups: [0, 3]
num_classes: 2
pretrained: false
num_power_iter: 20
seeds: [0, 1, 2, 3, 4]
epochs: 0
results_path: "results/sr_values.json"
figure_path: "figures/sr_comparison.png"
```

---

## Subtasks

**Budget: 0** — no subtask decomposition for EXISTENCE config (single fixed config only, per PoC rules).
