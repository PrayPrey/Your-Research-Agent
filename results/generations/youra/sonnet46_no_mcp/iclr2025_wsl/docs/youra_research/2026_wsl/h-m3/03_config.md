# Config: h-m3
# NFN vs Flat MLP Δρ Controlled Benchmark (MNIST-CNN + CIFAR-10)

Applied: Standard DL Experiment Pattern (dataclass config, AdamW+CosineAnnealing)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending h-m1 and h-m2)
**Status**: Config classes verified from actual code (direct file reads)
**Config Files Found**: `h-m1/code/config.py`, `h-m2/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-m1/code/config.py and h-m2/code/config.py (ACTUAL CODE)
# Verified fields:
#   seed: int = 42
#   epochs: int = 150
#   batch_size: int = 32
#   lr: float = 1e-3
#   weight_decay: float = 1e-4
#   betas: Tuple[float, float] = (0.9, 0.999)
#   t_max: int = 150
#   eta_min: float = 1e-6
#   embed_dim: int = 128
#   target_params_min: int = 475_000
#   target_params_max: int = 525_000
#   results_dir: Path = Path("./results")
#   figures_dir: Path = Path("./figures")
# h-m2 adds: hm1_code_dir: Path = Path("../../h-m1/code")
```

**Verified from**: `h-m1/code/config.py` and `h-m2/code/config.py` (actual implementation)

---

## A-1: ExperimentConfig Dataclass [Complexity: 2, Budget: 1]

**Applied**: Standard DL Experiment Pattern

### Configuration

```python
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

import numpy as np
import torch


CIFAR10_CNN_WEIGHT_SHAPES: List[tuple] = [
    (32, 3, 3, 3),   # conv1.weight
    (32,),            # conv1.bias
    (64, 32, 3, 3),  # conv2.weight
    (64,),            # conv2.bias
    (128, 64, 3, 3), # conv3.weight
    (128,),           # conv3.bias
    (256, 2048),      # fc1.weight  (placeholder - adjust to actual zoo)
    (256,),           # fc1.bias
    (10, 256),        # fc2.weight
    (10,),            # fc2.bias
]


@dataclass
class ExperimentConfig:
    # Paths
    mnist_data_dir: Path = Path("../../.data_cache/datasets/mnist_hyp_rand")
    cifar_data_dir: Path = Path("../../.data_cache/datasets/cifar10_hyp_rand")
    hm1_code_dir: Path = Path("../h-m1/code")
    hm2_code_dir: Path = Path("../h-m2/code")
    results_dir: Path = Path("./results")
    figures_dir: Path = Path("./figures")

    # Training (Deep Sets + CIFAR-10 retraining)
    seed: int = 42
    epochs: int = 150
    batch_size: int = 32
    lr: float = 1e-3
    weight_decay: float = 1e-4
    betas: Tuple[float, float] = (0.9, 0.999)
    t_max: int = 150
    eta_min: float = 1e-6

    # Deep Sets capacity search
    embed_dim: int = 128
    phi_hidden_candidates: List[int] = field(
        default_factory=lambda: [64, 96, 128, 160, 192, 256]
    )
    rho_hidden: int = 256
    target_params_min: int = 475_000
    target_params_max: int = 525_000

    # Bootstrap
    n_resamples: int = 1000

    # Gate thresholds
    delta_rho_mnist_threshold: float = 0.05
    delta_rho_cifar_threshold: float = 0.0

    # Device
    device: str = "auto"  # "auto" = detect CUDA at runtime

    def __post_init__(self):
        self.mnist_data_dir = Path(self.mnist_data_dir)
        self.cifar_data_dir = Path(self.cifar_data_dir)
        self.hm1_code_dir = Path(self.hm1_code_dir)
        self.hm2_code_dir = Path(self.hm2_code_dir)
        self.results_dir = Path(self.results_dir)
        self.figures_dir = Path(self.figures_dir)
        if self.device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | ExperimentConfig dataclass | All paths, hyperparameters, gate thresholds, device auto-detect |

---

## A-4: Deep Sets Training Config [Complexity: 2, Budget: 1]

**Applied**: Standard DL Experiment Pattern (AdamW + CosineAnnealingLR)

### Configuration

```python
# Training config by zoo and encoder type
# "checkpoint_load" = load from base hypothesis; "train_fresh" = train from scratch

TRAINING_MODE = {
    "mnist_cnn": {
        "FlatMLP":   "checkpoint_load",   # reuse h-m1 best_flat_mlp_encoder.pt
        "DeepSets":  "train_fresh",        # new encoder, must train
        "NFN":       "checkpoint_load",   # reuse h-m2 best_nfn_encoder.pt
    },
    "cifar10": {
        "FlatMLP":   "train_fresh",        # different weight shapes
        "DeepSets":  "train_fresh",
        "NFN":       "train_fresh",
    },
}

CHECKPOINT_PATHS = {
    "FlatMLP": "../h-m1/code/results/best_flat_mlp_encoder.pt",
    "NFN":     "../h-m2/code/results/best_nfn_encoder.pt",
}

# AdamW + CosineAnnealing — inherited from h-m1/h-m2 (verified from actual code)
OPTIMIZER_DEFAULTS = {
    "lr": 1e-3,
    "weight_decay": 1e-4,
    "betas": (0.9, 0.999),
}

SCHEDULER_DEFAULTS = {
    "T_max": 150,   # matches epochs
    "eta_min": 1e-6,
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Training mode + checkpoint paths | Per-encoder, per-zoo train/load decision |

---

## A-8: Visualization Config [Complexity: 2, Budget: 2]

**Applied**: Standard DL Experiment Pattern (seaborn + matplotlib)

### Configuration

```python
@dataclass
class VisualizationConfig:
    # Figure sizes (width, height) in inches
    figure_size_bar: tuple = (10, 6)        # bar chart (ρ per encoder)
    figure_size_delta: tuple = (8, 5)       # Δρ tier analysis
    figure_size_bootstrap: tuple = (12, 4)  # bootstrap histograms (subplots)
    figure_size_cross_zoo: tuple = (10, 6)  # cross-zoo comparison
    figure_size_spectrum: tuple = (10, 4)   # symmetry spectrum

    dpi: int = 150
    style: str = "seaborn-v0_8-whitegrid"

    # Per-encoder colors
    encoder_colors: dict = None  # set in __post_init__

    figures_dir: Path = Path("./figures")

    def __post_init__(self):
        self.figures_dir = Path(self.figures_dir)
        if self.encoder_colors is None:
            self.encoder_colors = {
                "FlatMLP":  "#4C72B0",   # blue
                "DeepSets": "#DD8452",   # orange
                "NFN":      "#55A868",   # green
            }


# Output file naming
OUTPUT_FILES = {
    # Results
    "results_json":         "results/h-m3_results.json",

    # Figures
    "fig_rho_bar_mnist":    "figures/rho_bar_mnist.png",
    "fig_rho_bar_cifar":    "figures/rho_bar_cifar.png",
    "fig_delta_rho":        "figures/delta_rho_comparison.png",
    "fig_bootstrap_mnist":  "figures/bootstrap_ci_mnist.png",
    "fig_bootstrap_cifar":  "figures/bootstrap_ci_cifar.png",
    "fig_cross_zoo":        "figures/cross_zoo_comparison.png",
    "fig_tier_analysis":    "figures/tier_analysis.png",
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | VisualizationConfig dataclass | Figure sizes, colors per encoder, seaborn style |
| C-8-2 | Output file naming dict | All results and figures paths |

---

## A-9: Run Experiment Config [Complexity: 1, Budget: 1]

**Applied**: Standard DL Experiment Pattern

### Configuration

```python
@dataclass
class RunConfig:
    # Step control
    skip_cifar_if_unavailable: bool = True   # gracefully skip CIFAR zoo steps
    run_train: bool = True
    run_evaluate: bool = True
    run_visualize: bool = True
    run_gate_check: bool = True

    # Logging
    log_level: str = "INFO"   # "DEBUG" | "INFO" | "WARNING"
    log_to_file: bool = True
    log_file: Path = Path("./results/run.log")

    def __post_init__(self):
        self.log_file = Path(self.log_file)
```

### Results Schema (h-m3_results.json)

```python
RESULTS_SCHEMA = {
    "encoders": {
        "<encoder_name>": {
            "mnist_cnn": {
                "rho": float,
                "ci_lower": float,
                "ci_upper": float,
                "param_count": int,
            },
            "cifar10": {
                "rho": float,
                "ci_lower": float,
                "ci_upper": float,
                "param_count": int,
            },
        }
    },
    "delta_metrics": {
        "delta_rho_mnist": float,     # NFN_rho - FlatMLP_rho (MNIST)
        "delta_rho_cifar": float,     # NFN_rho - FlatMLP_rho (CIFAR)
        "ci_lower_mnist": float,
        "ci_lower_cifar": float,
    },
    "gate_results": {
        "p1_pass": bool,
        "p2_pass": bool,
        "p3_tier_analysis": dict,
    },
    "training_metadata": {
        "<encoder_name>_<zoo>": {
            "epochs": int,
            "best_val_loss": float,
            "phi_hidden_selected": int,   # Deep Sets only
        }
    },
}
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | RunConfig dataclass + results schema | Step control, logging, JSON schema |

---

## Summary

| Task | Config Class | Subtasks |
|------|-------------|----------|
| A-1  | ExperimentConfig | 1/1 |
| A-4  | TRAINING_MODE + CHECKPOINT_PATHS dicts | 1/1 |
| A-8  | VisualizationConfig + OUTPUT_FILES | 2/2 |
| A-9  | RunConfig + RESULTS_SCHEMA | 1/1 |

**Total subtasks**: 5/5
