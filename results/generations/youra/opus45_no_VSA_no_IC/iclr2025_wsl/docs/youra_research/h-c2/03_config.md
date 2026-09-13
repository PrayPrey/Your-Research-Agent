# H-C2 Configuration: Crossing Point N* (NFN vs Statistics)

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (sibling hypothesis h-c1)
**Status**: Existing patterns found — H-C1 uses YAML-comment style dataclass config
**Config Files Found**: `docs/youra_research/h-c1/code/config.py` (same experiment family: NFN vs Statistics/MLP crossing)
**Pattern Used**: dataclass (following h-c1 convention for consistency)

**Applied**: KB pattern — dataclass config with grouped sub-configs (data/model/train), consistent with h-c1.

---

## Full Configuration (YAML)

```yaml
# ============================================================
# H-C2: Crossing point N* where NFN R2 matches Statistics R2
# ============================================================

experiment:
  # Training set sizes to sweep (crossing point search grid)
  n_values: [100, 250, 500, 1000, 2500]
  # Seeds per (N, method) pair — 10 * 5 * 2 = 100 runs total
  seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
  # Fixed held-out test set size (same 500 models across all N)
  test_size: 500
  # Seed for the train/test split itself (kept separate from training seeds)
  split_seed: 42
  # |NFN_R2 - Stats_R2| below this = crossing point found
  crossing_threshold: 0.03
  # Hard requirement from hypothesis: N* must be below this
  crossing_max_n: 2500

data:
  # Model Zoo CIFAR-10 population (Zenodo record 5645138)
  zoo_dir: "data/cifar10_zoo"
  zoo_url: "https://zenodo.org/record/5645138/files/cifar10_zoo.zip"
  n_pool_models: 1000  # total models available in zoo

nfn:
  hidden_channels: 64      # NPLinear hidden width
  num_layers: 2            # encoder depth (NPLinear + ReLU) x2
  head_hidden: 64           # MLP head hidden width after pooling

stats:
  # No hyperparameters — linear regressor on hand-crafted features
  # (per-layer mean, std, L2 norm, spectral norm)
  features: ["mean", "std", "l2_norm", "spectral_norm"]

train:
  optimizer: "adam"
  lr: 0.001                     # 1e-3, NFN paper default
  weight_decay: 0.0001          # 1e-4
  batch_size: 32
  epochs: 100
  early_stopping_patience: 10   # on validation loss
  loss: "mse"

eval:
  metrics: ["r2", "kendall_tau", "mse"]
  ci_level: 0.95   # 95% CI across 10 seeds

paths:
  results_dir: "results"
  figures_dir: "figures"
  checkpoints_dir: "checkpoints"

visualization:
  # Mandatory: N (log-x) vs R2 for NFN and Statistics, crossing point annotated
  crossing_plot:
    x_log_scale: true
    nfn_color: "blue"
    stats_color: "orange"
    show_ci_band: true
  # Autonomous extras
  extra_plots: ["learning_curves", "pred_vs_actual_at_crossing", "r2_bar_chart"]
```

---

## Python Dataclass (Phase 4 copy-paste)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ExperimentConfig:
    n_values: List[int] = field(default_factory=lambda: [100, 250, 500, 1000, 2500])
    seeds: List[int] = field(default_factory=lambda: list(range(10)))
    test_size: int = 500
    split_seed: int = 42
    crossing_threshold: float = 0.03
    crossing_max_n: int = 2500

@dataclass
class DataConfig:
    zoo_dir: str = "data/cifar10_zoo"
    zoo_url: str = "https://zenodo.org/record/5645138/files/cifar10_zoo.zip"
    n_pool_models: int = 1000

@dataclass
class NFNConfig:
    hidden_channels: int = 64
    num_layers: int = 2
    head_hidden: int = 64

@dataclass
class StatsConfig:
    features: List[str] = field(default_factory=lambda: ["mean", "std", "l2_norm", "spectral_norm"])

@dataclass
class TrainConfig:
    optimizer: str = "adam"
    lr: float = 1e-3
    weight_decay: float = 1e-4
    batch_size: int = 32
    epochs: int = 100
    early_stopping_patience: int = 10
    loss: str = "mse"

@dataclass
class EvalConfig:
    metrics: List[str] = field(default_factory=lambda: ["r2", "kendall_tau", "mse"])
    ci_level: float = 0.95

@dataclass
class Config:
    experiment: ExperimentConfig = field(default_factory=ExperimentConfig)
    data: DataConfig = field(default_factory=DataConfig)
    nfn: NFNConfig = field(default_factory=NFNConfig)
    stats: StatsConfig = field(default_factory=StatsConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
    eval: EvalConfig = field(default_factory=EvalConfig)
    results_dir: str = "results"
    figures_dir: str = "figures"
    checkpoints_dir: str = "checkpoints"

CONFIG = Config()
```

---

## Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-C2-1 | Data pipeline | Download/load CIFAR-10 model zoo, build fixed 500-model test split + statistics feature extractor |
| C-C2-2 | NFN training loop | Train NFN across 5 N-values x 10 seeds with early stopping |
| C-C2-3 | Stats baseline loop | Train linear regressor on stats features, same N/seed grid |
| C-C2-4 | Crossing point analysis + viz | Compute R2/tau/MSE with 95% CI, locate N*, generate mandatory + extra figures |
