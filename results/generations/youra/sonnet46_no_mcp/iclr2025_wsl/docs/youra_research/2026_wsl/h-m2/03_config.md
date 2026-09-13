# Config: H-M2
# NFN Equivariant Encoder Permutation Sensitivity Probing

Applied: PyTorch dataclass configuration pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code (h-m1/code/config.py read directly)
**Config Files Found**: `h-m1/code/config.py`
**Pattern Used**: dataclass

**Verified field names from h-m1/code/config.py:**
- `data_dir`, `he1_code_dir`, `results_dir`, `figures_dir`, `zoo_name` (paths)
- `seed`, `epochs`, `batch_size`, `lr`, `weight_decay`, `betas`, `t_max`, `eta_min` (training)
- `embed_dim`, `dropout`, `target_params_min`, `target_params_max`, `hidden_dims_candidates` (model)
- `n_pairs`, `min_pairs`, `acc_threshold`, `sensitivity_gate`, `spearman_target` (probing)
- `VisualizationConfig`: `figure_size`, `dpi`, `colormap`, `figures_dir`

**Key differences in h-m2:**
- `sensitivity_gate` (scalar) → replaced by `sensitivity_gate_absolute` + `sensitivity_gate_relative` (dual thresholds)
- `hidden_dims_candidates` → replaced by `channel_dim_candidates` + `n_layers_candidates` (NFN grid search)
- `dropout` dropped (NFN encoder has no dropout in NPLinear layers)
- Added: `weight_shapes`, `flat_mlp_sensitivity_score`
- `spearman_target` updated from 0.5 to 0.1041 (h-m1 actual result)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-m1/code/config.py (ACTUAL CODE — verified)
@dataclass
class ExperimentConfig:
    # Paths
    data_dir: Path = Path("../../.data_cache/datasets/mnist_hyp_rand")
    he1_code_dir: Path = Path("../../h-e1/code")
    results_dir: Path = Path("./results")
    figures_dir: Path = Path("./figures")
    zoo_name: str = "mnist_cnn_hyp_rand"

    # Training — INHERITED UNCHANGED
    seed: int = 42
    epochs: int = 150
    batch_size: int = 32
    lr: float = 1e-3
    weight_decay: float = 1e-4
    betas: Tuple[float, float] = (0.9, 0.999)
    t_max: int = 150
    eta_min: float = 1e-6

    # Model — PARTIALLY INHERITED
    embed_dim: int = 128
    dropout: float = 0.1                        # ← dropped in h-m2
    target_params_min: int = 475_000
    target_params_max: int = 525_000
    hidden_dims_candidates: List[List[int]] = ...  # ← replaced in h-m2

    # Probing — PARTIALLY INHERITED
    n_pairs: int = 500
    min_pairs: int = 50
    acc_threshold: float = 0.01
    sensitivity_gate: float = 0.3              # ← replaced by dual thresholds in h-m2
    spearman_target: float = 0.5              # ← updated to 0.1041 in h-m2

@dataclass
class VisualizationConfig:
    figure_size: tuple = (10, 6)
    dpi: int = 150
    colormap: str = "tab10"
    figures_dir: Path = Path("./figures")
```

**Verified from**: `h-m1/code/config.py` (actual implementation)

---

## A-1: Project Setup [Complexity: 5]

**Applied**: PyTorch dataclass configuration pattern

### Configuration

```python
"""ExperimentConfig for H-M2: NFN Equivariant Encoder Permutation Sensitivity Probing."""
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple

import numpy as np
import torch


MNIST_CNN_WEIGHT_SHAPES: List[tuple] = [
    (32, 1, 3, 3),   # conv1.weight
    (32,),            # conv1.bias
    (64, 32, 3, 3),  # conv2.weight
    (64,),            # conv2.bias
    (128, 1024),      # fc1.weight
    (128,),           # fc1.bias
    (10, 128),        # fc2.weight
    (10,),            # fc2.bias
]


@dataclass
class ExperimentConfig:
    # Paths
    data_dir: Path = Path("../../.data_cache/datasets/mnist_hyp_rand")
    he1_code_dir: Path = Path("../../h-e1/code")
    results_dir: Path = Path("./results")
    figures_dir: Path = Path("./figures")
    zoo_name: str = "mnist_cnn_hyp_rand"

    # Training (identical to h-m1 — controlled experiment)
    seed: int = 42
    epochs: int = 150
    batch_size: int = 32
    lr: float = 1e-3
    weight_decay: float = 1e-4
    betas: Tuple[float, float] = (0.9, 0.999)
    t_max: int = 150
    eta_min: float = 1e-6

    # NFN model
    embed_dim: int = 128
    weight_shapes: List[tuple] = field(default_factory=lambda: MNIST_CNN_WEIGHT_SHAPES)
    channel_dim_candidates: List[int] = field(default_factory=lambda: [24, 32, 40, 48, 56])
    n_layers_candidates: List[int] = field(default_factory=lambda: [2, 3, 4])
    target_params_min: int = 475_000
    target_params_max: int = 525_000

    # Probing
    n_pairs: int = 500
    min_pairs: int = 50
    acc_threshold: float = 0.01
    # Non-standard: dual thresholds replace h-m1 single sensitivity_gate=0.3
    sensitivity_gate_absolute: float = 0.1
    sensitivity_gate_relative: float = 0.3245   # flat_mlp_sensitivity_score * 0.5
    flat_mlp_sensitivity_score: float = 0.6490  # from h-m1 result
    spearman_target: float = 0.1041             # h-m1 actual Spearman rho (informational)

    def __post_init__(self):
        self.data_dir = Path(self.data_dir)
        self.he1_code_dir = Path(self.he1_code_dir)
        self.results_dir = Path(self.results_dir)
        self.figures_dir = Path(self.figures_dir)


@dataclass
class VisualizationConfig:
    figure_size: tuple = (10, 6)
    dpi: int = 150
    colormap: str = "tab10"
    figures_dir: Path = Path("./figures")

    def __post_init__(self):
        self.figures_dir = Path(self.figures_dir)


def set_seed(seed: int) -> None:
    """Set random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
```

---

## A-2: NFNWeightDataset [Complexity: 10, Budget: 1 subtask]

**Applied**: PyTorch dataclass configuration pattern

Dataset config is embedded in `ExperimentConfig`. Key fields used by `NFNWeightDataset` and `load_and_split_dataset_nfn`:

| Field | Value | Source |
|-------|-------|--------|
| `data_dir` | `Path("../../.data_cache/datasets/mnist_hyp_rand")` | ExperimentConfig |
| `zoo_name` | `"mnist_cnn_hyp_rand"` | ExperimentConfig |
| `weight_shapes` | `MNIST_CNN_WEIGHT_SHAPES` (8 tensors) | ExperimentConfig |
| `batch_size` | `32` | ExperimentConfig |
| `seed` | `42` | ExperimentConfig |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | NFNWeightDataset + collate | Implement dataset yielding `(weight_list, flat_w_normalized, acc)` with `collate_nfn` and `load_and_split_dataset_nfn` |

---

## A-5: Train Loop Adaptation [Complexity: 9, Budget: 1 subtask]

**Applied**: PyTorch dataclass configuration pattern

Training config is fully provided by `ExperimentConfig`. No additional dataclass needed. Key fields:

| Field | Value | Note |
|-------|-------|------|
| `lr` | `1e-3` | Adam |
| `weight_decay` | `1e-4` | Adam |
| `betas` | `(0.9, 0.999)` | Adam |
| `t_max` | `150` | CosineAnnealingLR |
| `eta_min` | `1e-6` | CosineAnnealingLR |
| `epochs` | `150` | Training loop |
| `batch_size` | `32` | DataLoader |

`TrainHistory` dataclass lives in `train.py` (not config):

```python
from dataclasses import dataclass, field

@dataclass
class TrainHistory:
    train_loss: list = field(default_factory=list)
    val_loss: list = field(default_factory=list)
    train_spearman: list = field(default_factory=list)
    val_spearman: list = field(default_factory=list)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Train loop adaptation | Adapt `train_encoder` for NFN `(weight_list, flat_w, acc)` collated batches; same optimizer/scheduler/loss as h-m1 |

---

## A-8: 6 Required Figures [Complexity: 10, Budget: 1 subtask]

**Applied**: PyTorch dataclass configuration pattern

`VisualizationConfig` (defined in A-1) covers all figure output settings. Figure functions take `figures_dir` and plot-specific data arguments.

| Figure | Function | Required Data |
|--------|----------|---------------|
| FR-7.1 | `plot_gate_metrics_comparison` | `nfn_score`, `flat_mlp_score=0.6490`, `threshold_abs=0.1`, `threshold_rel=0.3245` |
| FR-7.2 | `plot_l2_distribution_comparison` | `nfn_equiv_dists`, `nfn_random_dists`, `mlp_equiv_dists`, `mlp_random_dists` |
| FR-7.3 | `plot_embedding_pca` | `embeddings (N, 128)`, `accuracies (N,)`, `equiv_pair_indices` |
| FR-7.4 | `plot_training_curves` | `history: TrainHistory` |
| FR-7.5 | `plot_sensitivity_by_decile` | `nfn_decile_scores`, `mlp_decile_scores` |
| FR-7.6 | `plot_nfn_vs_mlp_decile_comparison` | `nfn_decile_scores`, `mlp_decile_scores` |

Config fields used: `cfg.figures_dir`, `vcfg.figure_size=(10,6)`, `vcfg.dpi=150`, `vcfg.colormap="tab10"`.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | 6 figure implementations | Implement all 6 `visualize.py` functions using `VisualizationConfig` fields |

---

## A-9: run_experiment.py [Complexity: 9, Budget: 1 subtask]

**Applied**: PyTorch dataclass configuration pattern

`run_experiment.py` instantiates `ExperimentConfig()` and `VisualizationConfig()` with all defaults. No additional runtime config dataclass needed.

Runtime constants used by `main()`:

| Step | Config Field | Value |
|------|-------------|-------|
| Grid search | `channel_dim_candidates` | `[24, 32, 40, 48, 56]` |
| Grid search | `n_layers_candidates` | `[2, 3, 4]` |
| Grid search | `target_params_min/max` | `[475_000, 525_000]` |
| Gate check | `sensitivity_gate_absolute` | `0.1` |
| Gate check | `sensitivity_gate_relative` | `0.3245` |
| Results file | `results_dir` | `Path("./results")` |
| Figures | `figures_dir` | `Path("./figures")` |

Entry point pattern:
```python
cfg = ExperimentConfig()
vcfg = VisualizationConfig()
set_seed(cfg.seed)
# ... pipeline steps
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | run_experiment.py wiring | Wire all modules; verify param_count in [475K, 525K] pre-training; dual gate logging; save results + 6 figures |
