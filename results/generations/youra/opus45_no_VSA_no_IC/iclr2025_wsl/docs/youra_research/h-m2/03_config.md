# Config: H-M2 (NFN Data Efficiency vs MLP)

**Type**: MECHANISM | **Applied**: dataclass config pattern (matches H-M1 style, extended with N-sweep + multi-seed)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 provides data pipeline + NFN model)
**Status**: Serena project not active for this path — direct Read used as equivalent analysis (per architecture doc precedent). Config classes verified from H-M1's actual `code/config.py`.
**Config Files Found**: `docs/youra_research/h-m1/code/config.py` (dataclass style: `DataConfig`, `ModelConfig`, `TrainConfig`, `EvalConfig`, `Config`)
**Pattern Used**: dataclass (Python)

**Deviation note**: PRD (FR-3.1) assumes official `nfn` PyPI library; actual H-M1 code implements a custom equivariant NFN (no such library dependency). Config below has no `nfn_channels`/library-specific fields — follows actual H-M1 `ModelConfig` shape (`hidden_dim`, `num_layers`) renamed to `NFNConfig` for H-M2's two-model comparison.

---

## Inherited Configuration (Base Hypothesis)

```python
# From: docs/youra_research/h-m1/code/config.py (ACTUAL CODE)
@dataclass
class DataConfig:
    zoo_dir: str = "data/model_zoo"
    n_train: int = 2000
    n_test: int = 500
    split_seed: int = 42

@dataclass
class ModelConfig:          # H-M1's NFN config, renamed NFNConfig in H-M2
    hidden_dim: int = 64
    num_layers: int = 2

@dataclass
class TrainConfig:
    lr: float = 1e-3
    weight_decay: float = 1e-4
    batch_size: int = 64
    epochs: int = 30
    early_stop_patience: int = 10
    lr_patience: int = 5
    seeds: List[int] = field(default_factory=lambda: [42])
```

**Verified from**: `docs/youra_research/h-m1/code/config.py` (actual implementation)

H-M2 does NOT reuse `early_stop_patience`/`lr_patience` (architecture: no early-stop val carve-out — N can be as low as 100) and increases `hidden_dim` 64→128 / `num_layers` 2→3 per architecture spec (matches H-M1's larger validated variant, not the "smaller model" comment default).

---

## A-1..A-9: Full Sweep Config [Complexity: 4-8 each, Budget: Low tier]

**Applied**: paired-comparison sweep config (N x seed grid, fixed test set) — standard for data-efficiency ablations

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class DataConfig:
    zoo_dir: str = "data/model_zoo"
    n_pool_models: int = 6000   # covers max N=5000 train + 500 test
    n_test: int = 500
    split_seed: int = 42        # same seed as H-M1 for consistent test split

@dataclass
class NFNConfig:
    hidden_dim: int = 128
    num_layers: int = 3

@dataclass
class MLPConfig:
    hidden_dim: int = 256       # FR-2.1
    num_hidden_layers: int = 2  # FR-2.1

@dataclass
class TrainConfig:
    lr: float = 1e-3            # FR-4.1
    batch_size: int = 32        # FR-4.2
    epochs: int = 50            # FR-4.3
    seeds: List[int] = field(default_factory=lambda: list(range(10)))  # FR-4.5

N_VALUES = [100, 250, 500, 1000, 2500, 5000]  # FR-1.2
PRIMARY_N = 500        # gate check N (PRD success criteria)
R2_DELTA_TARGET = 0.1  # PRD success criteria
ALPHA = 0.05            # paired t-test significance threshold

@dataclass
class Config:
    data: DataConfig = field(default_factory=DataConfig)
    nfn: NFNConfig = field(default_factory=NFNConfig)
    mlp: MLPConfig = field(default_factory=MLPConfig)
    train: TrainConfig = field(default_factory=TrainConfig)
    figures_dir: str = "figures"
    results_dir: str = "results"

CONFIG = Config()
```

### Subtasks [9/9 used — mirrors architecture Epic Tasks]

| ID | Subtask | Description |
|----|---------|--------------|
| A-1 | Bootstrap module | Copy H-M1 `data.py`/`nfn_model.py`, write `config.py` with above dataclasses |
| A-2 | Data pool prep | Generate/load 6000-model zoo, fixed 500-test split (`split_seed=42`) |
| A-3 | MLP baseline model | `mlp_model.py` using `MLPConfig` (hidden_dim=256, 2 layers) |
| A-4 | Generic train/eval loop | `train_common.py`, uses `TrainConfig` (no early-stop fields — omitted vs H-M1) |
| A-5 | Per-run trainer | `sweep.py::run_single`, seeded via `TrainConfig.seeds` |
| A-6 | Sweep orchestration | `sweep.py::run_sweep` over `N_VALUES x seeds` |
| A-7 | Statistical testing | `stats.py`, gate = `R2_DELTA_TARGET` + `ALPHA` at `PRIMARY_N` |
| A-8 | Figures | `evaluate.py`, reads `CONFIG.figures_dir` |
| A-9 | Orchestration + results | `run_experiment.py`, writes to `CONFIG.results_dir` |

**Non-standard values**: `n_pool_models=6000` (vs H-M1's `n_train=2000`) — sized to cover max sweep N=5000 + fixed 500 test; `hidden_dim=128`/`num_layers=3` for NFN (vs H-M1's 64/2) — architecture-specified capacity increase to support larger N range; no early-stop fields — N=100 too small to carve a val split.
