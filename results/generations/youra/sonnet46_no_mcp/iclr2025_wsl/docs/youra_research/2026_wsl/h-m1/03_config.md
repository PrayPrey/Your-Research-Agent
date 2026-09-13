# Config: H-M1 — Flat MLP Encoder Permutation Sensitivity Probing

Applied: PyTorch dataclass config pattern with pathlib.Path fields

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from actual h-e1 code (file read; MCP unavailable in TEST environment)
**Config Files Found**: `docs/youra_research/20260505_wsl/h-e1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual h-e1 Code)

```python
# From: docs/youra_research/20260505_wsl/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    data_dir: Path = Path("./data/model_zoo")
    results_dir: Path = Path("./results")
    figures_dir: Path = Path("./figures")
    zoo_name: str = "mnist_cnn"
    seed: int = 42
    n_per_decile: int = 50
    n_deciles: int = 10
    acc_threshold: float = 0.01
    cosine_dist_threshold: float = 0.1
    orbit_proportion_gate: float = 0.05
    bn_verify_sample_size: int = 5

@dataclass
class VisualizationConfig:
    figure_size: tuple = (10, 6)
    dpi: int = 150
    colormap: str = "tab10"
```

**Verified from**: `docs/youra_research/20260505_wsl/h-e1/code/config.py` (actual implementation)

**Note**: h-e1 ExperimentConfig has no training hyperparameters (lr, epochs, etc.) — h-e1 is a statistical analysis, not a training experiment. h-m1 introduces a new ExperimentConfig that is conceptually related but structurally independent.

---

## A-1: Config & Project Setup [Low, Complexity: 6, Budget: 0 subtasks]

Applied: Standard PyTorch defaults

### Configuration

```python
# h-m1/code/config.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple


@dataclass
class ExperimentConfig:
    # Paths
    data_dir: Path = Path("../../.data_cache/datasets/mnist_hyp_rand")
    he1_code_dir: Path = Path("../../h-e1/code")
    results_dir: Path = Path("./results")
    figures_dir: Path = Path("./figures")
    zoo_name: str = "mnist_cnn_hyp_rand"

    # Training
    seed: int = 42
    epochs: int = 150
    batch_size: int = 32
    lr: float = 1e-3
    weight_decay: float = 1e-4
    betas: Tuple[float, float] = (0.9, 0.999)
    t_max: int = 150       # matches epochs for full cosine cycle
    eta_min: float = 1e-6

    # Model
    embed_dim: int = 128
    dropout: float = 0.1
    target_params_min: int = 475_000
    target_params_max: int = 525_000
    hidden_dims_candidates: List[List[int]] = field(default_factory=lambda: [
        [9], [10], [8, 256], [8, 512], [16, 128], [16, 256]
    ])

    # Probing
    n_pairs: int = 500
    min_pairs: int = 50
    acc_threshold: float = 0.01   # inherited from h-e1 same semantics
    sensitivity_gate: float = 0.3
    spearman_target: float = 0.5

    def __post_init__(self):
        self.data_dir = Path(self.data_dir)
        self.he1_code_dir = Path(self.he1_code_dir)
        self.results_dir = Path(self.results_dir)
        self.figures_dir = Path(self.figures_dir)
```

---

## A-2: Data Loading & Normalization [Medium, Complexity: 13, Budget: 2 subtasks]

Applied: Schurholt model zoo split pattern + z-score normalization from train set

### Configuration

No separate config class — all parameters live in ExperimentConfig. Relevant fields:

| Field | Value | Purpose |
|-------|-------|---------|
| `data_dir` | `../../.data_cache/datasets/mnist_hyp_rand` | Zoo dataset path |
| `zoo_name` | `"mnist_cnn_hyp_rand"` | Dataset identifier |
| `batch_size` | `32` | DataLoader batch size |
| `seed` | `42` | Reproducible split shuffling |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | WeightDataset + z-score norm | Implement WeightDataset with train-mean/std normalization; handle `_flat_weights` pre-vectorized format from Zenodo dataset |
| C-2-2 | Schurholt splits + DataLoaders | Extract 70/15/15 train/val/test split; build DataLoader with batch_size=32, shuffle=True for train only |

---

## A-3: FlatMLPEncoder + Grid Search [Medium, Complexity: 10, Budget: 2 subtasks]

Applied: Parameter-budget grid search pattern

### Configuration

Relevant ExperimentConfig fields for model construction:

| Field | Value | Purpose |
|-------|-------|---------|
| `embed_dim` | `128` | Output embedding dimension |
| `dropout` | `0.1` | Dropout in hidden layers |
| `target_params_min` | `475_000` | Lower bound of param budget |
| `target_params_max` | `525_000` | Upper bound of param budget |
| `hidden_dims_candidates` | `[[9],[10],[8,256],[8,512],[16,128],[16,256]]` | Grid search candidates |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | FlatMLPEncoder + FlatMLPWithHead | Implement encoder (Linear+BN+ReLU+Dropout stack → embed_dim) and prediction head (embed_dim → 1) |
| C-3-2 | grid_search_architecture + count_params | Iterate candidates; return first encoder within [475K, 525K] param budget |

---

## A-7: Evaluation & Gate Check [Medium, Complexity: 9, Budget: 2 subtasks]

Applied: Standard PyTorch defaults

### Configuration

Relevant ExperimentConfig fields for evaluation:

| Field | Value | Purpose |
|-------|-------|---------|
| `sensitivity_gate` | `0.3` | MUST_WORK gate threshold |
| `spearman_target` | `0.5` | Quality check (non-gating) |
| `min_pairs` | `50` | Minimum valid pair count |
| `target_params_min/max` | `475K / 525K` | Param-range check in gate |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | compute_spearman | scipy.stats.spearmanr on test loader predictions vs labels |
| C-7-2 | run_gate_check + save_results | Check sensitivity_score > 0.3; log gate pass/fail with [H-M1] prefix; save JSON results to results_dir |

---

## A-8: Visualization (5 figures) [Medium, Complexity: 11, Budget: 1 subtask]

Applied: Standard matplotlib defaults, VisualizationConfig pattern from h-e1

### Configuration

```python
@dataclass
class VisualizationConfig:
    figure_size: tuple = (10, 6)
    dpi: int = 150
    colormap: str = "tab10"
    figures_dir: Path = Path("./figures")  # mirrors ExperimentConfig.figures_dir

    def __post_init__(self):
        self.figures_dir = Path(self.figures_dir)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | All 5 figures | Implement plot_gate_metrics, plot_l2_distribution, plot_training_curve, plot_sensitivity_by_decile, plot_embedding_scatter (PCA) in visualize.py; save to figures_dir |
