# Configuration: H-M2 (Spurious-Specificity Mechanism Test)

Applied: Standard PyTorch dataclass config pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from actual h-e1/code/config.py
**Config Files Found**: `h-e1/code/config.py` - single `Config` dataclass, `get_config()` factory
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-e1/code/config.py (ACTUAL CODE - verified)
@dataclass
class Config:
    # Dataset
    data_root: str = "./data/waterbirds"
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
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    # Visualization
    fig_dpi: int = 300
    fig_format: str = "png"
    fig_gate_filename: str = "gate_metrics.png"
    fig_trajectory_filename: str = "loss_trajectories.png"
    fig_roc_filename: str = "roc_curve.png"
    fig_features_filename: str = "feature_distributions.png"
```

**Verified from**: `h-e1/code/config.py` (actual implementation)

---

## H-M2 Extended Configuration

```python
from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class Config:
    # --- Inherited from H-E1 (field names verified from actual code) ---
    data_root: str = "../../.data_cache/datasets/waterbirds/waterbird_complete95_forest2water2"
    num_workers: int = 4
    pin_memory: bool = True
    train_crop_size: int = 224
    eval_resize: int = 256
    eval_crop_size: int = 224
    img_mean: Tuple[float, float, float] = (0.485, 0.456, 0.406)
    img_std: Tuple[float, float, float] = (0.229, 0.224, 0.225)
    model_name: str = "resnet50"
    num_classes: int = 2
    epochs: int = 20
    trajectory_epochs: int = 5
    batch_size: int = 128
    lr: float = 0.001
    momentum: float = 0.9
    n_folds: int = 5
    lr_clf_max_iter: int = 1000
    output_dir: str = "./outputs"
    figures_dir: str = "./figures"
    fig_dpi: int = 300
    fig_format: str = "png"

    # --- H-M2 additions: Multi-seed ---
    base_seed: int = 42          # seed for regime i = base_seed + i
    num_seeds: int = 3

    # --- H-M2 additions: Group info ---
    num_groups: int = 4

    # --- ERM hyperparams ---
    weight_decay_erm: float = 0.0001

    # --- GroupDRO hyperparams ---
    weight_decay_gdro: float = 1.0   # Strong regularization per kohpangwei/group_DRO
    groupdro_gamma: float = 0.1      # Exponentiated gradient step size

    # --- Gate thresholds ---
    delta_gdro_threshold: float = 0.10
    delta_random_threshold: float = 0.05

    # --- Figure filenames ---
    fig_gate_filename: str = "gate_metrics.png"
    fig_auroc_comparison_filename: str = "auroc_comparison.png"
    fig_group_weights_filename: str = "group_weights_evolution.png"
    fig_grad_variance_filename: str = "gradient_variance.png"
    fig_trajectory_panels_filename: str = "loss_trajectory_panels.png"

    # --- Results output ---
    results_filename: str = "results.json"


def get_config() -> Config:
    """Return default experiment configuration."""
    return Config()
```

---

## A-7: Orchestrator [Complexity: 12, Budget: 2 subtasks]

Applied: Standard PyTorch dataclass config pattern

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Regime Orchestration Config | Seed scheduling, regime sequencing, device setup |
| C-7-2 | Results Aggregation Schema | JSON output schema for all metrics |

### Results JSON Schema

```python
# Expected structure of outputs/results.json
RESULTS_SCHEMA = {
    "auroc": {
        "erm":      {"mean": float, "std": float},
        "groupdro": {"mean": float, "std": float},
        "random":   {"mean": float, "std": float},
    },
    "delta_auroc": {
        "delta_gdro":    float,   # AUROC_ERM - AUROC_GroupDRO
        "delta_random":  float,   # AUROC_ERM - AUROC_Random
    },
    "gate": {
        "passed":         bool,
        "delta_gdro_threshold":   0.10,
        "delta_random_threshold": 0.05,
        "result":         str,    # "PASS" | "FAIL"
    },
    "mechanism": {
        "gdro_weights_diverged":  bool,
        "variance_matched":       bool,   # within 20% tolerance
        "gdro_grad_var":          float,
        "random_grad_var":        float,
    },
    "seeds_used": [42, 43, 44],
}
```

### Regime Seed Table

```python
# Seed assignment: base_seed=42, num_seeds=3
# regime_idx: 0=ERM, 1=GroupDRO, 2=Random
# seed_i = base_seed + seed_offset_i
SEEDS = [42, 43, 44]  # one run per seed, averaged
```

---

## A-6: Visualization [Complexity: 10, Budget: 1 subtask]

Applied: Standard PyTorch dataclass config pattern

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Figure Configuration | All plot filenames, DPI, format settings |

### Figure Config (from Config dataclass above)

| Field | Value | Figure |
|-------|-------|--------|
| `fig_gate_filename` | `"gate_metrics.png"` | Bar chart: ΔAUROC_GDRO vs ΔAUROC_Random + threshold lines |
| `fig_auroc_comparison_filename` | `"auroc_comparison.png"` | Bar chart: ERM / GroupDRO / Random AUROC with error bars |
| `fig_group_weights_filename` | `"group_weights_evolution.png"` | GroupDRO group weights across epochs |
| `fig_grad_variance_filename` | `"gradient_variance.png"` | Histogram: GroupDRO vs Random gradient variance |
| `fig_trajectory_panels_filename` | `"loss_trajectory_panels.png"` | 3-panel per-group loss curves |
| `fig_dpi` | `300` | All figures |
| `fig_format` | `"png"` | All figures |

---

## A-8: Integration & Gate [Complexity: 9, Budget: 1 subtask]

Applied: Standard PyTorch dataclass config pattern

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Gate Thresholds & Output Paths | Gate config, output path resolution |

### Gate Config (from Config dataclass above)

```python
# Gate evaluation uses:
#   delta_gdro_threshold = 0.10   (ΔAUROC_GroupDRO must exceed this)
#   delta_random_threshold = 0.05 (ΔAUROC_Random must stay below this)

# Output paths resolved at runtime:
import os

def get_output_paths(config: Config) -> dict:
    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(config.figures_dir, exist_ok=True)
    return {
        "results_json": os.path.join(config.output_dir, config.results_filename),
        "fig_gate":     os.path.join(config.figures_dir, config.fig_gate_filename),
        "fig_auroc":    os.path.join(config.figures_dir, config.fig_auroc_comparison_filename),
        "fig_weights":  os.path.join(config.figures_dir, config.fig_group_weights_filename),
        "fig_grad_var": os.path.join(config.figures_dir, config.fig_grad_variance_filename),
        "fig_panels":   os.path.join(config.figures_dir, config.fig_trajectory_panels_filename),
    }
```

---

## Self-Validation

- [x] ONE format only (dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values (`weight_decay_gdro=1.0`, `groupdro_gamma=0.1`)
- [x] Subtask count within budget (4 total: 2+1+1)
- [x] "Codebase Analysis (Serena)" section included
- [x] Field names verified from actual h-e1/code/config.py
- [x] Inherited Configuration section included
