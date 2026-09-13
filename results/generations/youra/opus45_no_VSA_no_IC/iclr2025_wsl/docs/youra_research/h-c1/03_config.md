# Configuration: H-C1

**Type**: CONDITION | **Applied**: Standard PyTorch defaults, inherited from H-M2

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code (`h-m2/code/config.py`)
**Config Files Found**: `docs/youra_research/h-m2/code/config.py` (dataclass pattern)
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis: H-M2)

```python
# From: docs/youra_research/h-m2/code/config.py (ACTUAL CODE)
@dataclass
class NFNConfig:
    hidden_dim: int = 128
    num_layers: int = 3

@dataclass
class MLPConfig:
    hidden_dim: int = 256
    num_hidden_layers: int = 2

@dataclass
class TrainConfig:
    lr: float = 1e-3
    batch_size: int = 32
    epochs: int = 50          # H-C1 overrides to 100 (see below)
    seeds: List[int] = field(default_factory=lambda: list(range(10)))
```

**Verified from**: `docs/youra_research/h-m2/code/config.py`

---

## H-C1 Configuration (Single Fixed Config, N=5000)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class DataConfig:
    zoo_dir: str = "../h-m2/code/data/model_zoo"  # reuse H-M2 model zoo
    n_train: int = 5000
    n_test: int = 500
    split_seed: int = 42

@dataclass
class NFNConfig:
    nfn_channels: int = 32
    num_nplinear_layers: int = 2

@dataclass
class MLPConfig:
    hidden_dims: List[int] = field(default_factory=lambda: [256, 128])

@dataclass
class StatsConfig:
    pass  # Linear regression, no hyperparameters

@dataclass
class TrainConfig:
    optimizer: str = "adam"
    lr: float = 1e-3
    batch_size: int = 32
    epochs: int = 100
    loss: str = "mse"
    seeds: List[int] = field(default_factory=lambda: list(range(10)))

R2_PAIRWISE_THRESHOLD: float = 0.03
R2_SANITY_MIN: float = 0.5

@dataclass
class Config:
    data: DataConfig = field(default_factory=DataConfig)
    nfn: NFNConfig = field(default_factory=NFNConfig)
    mlp: MLPConfig = field(default_factory=MLPConfig)
    stats: StatsConfig = field(default_factory=StatsConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
    figures_dir: str = "figures"
    results_dir: str = "results"

CONFIG = Config()
```

Non-standard: `epochs=100` (H-M2 used 50) per PRD Section 6 — larger N=5000 needs more epochs to converge.

---

## Evaluation Config

| Param | Value |
|-------|-------|
| Metric | R² (`sklearn.metrics.r2_score`) |
| Seeds | 10 (`range(10)`) |
| Pairwise threshold | ≤ 0.03 (all 3 pairs: NFN-Stats, NFN-MLP, Stats-MLP) |
| Sanity check | individual R² > 0.5 |
| Gate | SHOULD_WORK (all pairwise diffs ≤ 0.03) |

---

## Output Paths

```
h-c1/results/metrics.json              # R² per method/seed
h-c1/figures/r2_comparison_N5000.png   # required bar chart w/ error bars
h-c1/figures/pairwise_heatmap.png      # optional
h-c1/figures/convergence_curve.png     # optional, if time permits
```
