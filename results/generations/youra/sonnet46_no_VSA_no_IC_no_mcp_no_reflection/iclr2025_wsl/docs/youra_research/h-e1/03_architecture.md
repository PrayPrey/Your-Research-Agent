---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
tier: LIGHT
date: "2026-08-31"
author: "yoon303@ust.ac.kr"
---

# Architecture: H-E1 — CNN Weight-Space Encoder for Generalization Gap

Applied: Shared-Encoder-Interface — common forward(weights) → scalar API across all 4 encoder types
Applied: Train-Val-Test-Split-First — fixed split computed before any model training to prevent data leakage
Applied: Best-Checkpoint-Selection — save model state at best val Spearman; evaluate test only once
Applied: Pre-condition-Audit-Gate — mandatory Spearman(gap, -test_acc) < 0.95 check before training

---

## Codebase Analysis (Serena)

Green-field project — no existing codebase to analyze. Serena MCP skipped per protocol.
All 4 encoder architectures are sourced from official author repositories (DWSNets, neural-graphs, nfn, cnns_weight_prediction).

---

## File Structure

```
h-e1/
├── run_experiment.py          # main entrypoint
├── config.py                  # all hyperparameters, fixed config
├── data/
│   ├── loader.py              # load_zoo(), ZooDataset, make_loader()
│   └── audit.py               # run_audit(), compute_split()
├── encoders/
│   ├── flat_mlp.py            # FlatMLP
│   ├── dwsnet.py              # DWSNet
│   ├── nft.py                 # NFT
│   └── gnn.py                 # GNN
├── training/
│   └── train.py               # train_encoder(), random_search()
├── evaluation/
│   └── evaluate.py            # eval_spearman(), eval_mse(), gate_check()
├── visualization/
│   └── figures.py             # all 5 figure functions
└── figures/                   # output directory (created at runtime)
```

---

## Module Interfaces

### data/loader.py

**Dependencies**: numpy, torch, sklearn

```python
from dataclasses import dataclass
from typing import List
import numpy as np
from torch.utils.data import DataLoader

@dataclass
class ZooData:
    weights: np.ndarray        # [N, total_params] or list of per-layer arrays
    gap: np.ndarray            # [N] — train_acc - test_acc
    train_acc: np.ndarray      # [N]
    test_acc: np.ndarray       # [N]
    idx_train: np.ndarray
    idx_val: np.ndarray
    idx_test: np.ndarray

def load_zoo(path: str) -> ZooData: ...
def make_loader(zoo: ZooData, split: str, batch_size: int, shuffle: bool = True) -> DataLoader: ...
```

### data/audit.py

**Dependencies**: scipy, numpy

```python
def run_audit(zoo: ZooData) -> float:
    """Computes Spearman(gap, -test_acc). Raises AssertionError if >= 0.95."""
    ...

def compute_split(n: int, seed: int = 42) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Returns (idx_train, idx_val, idx_test) for 80/10/10 split."""
    ...
```

### encoders/flat_mlp.py

**Dependencies**: torch

```python
import torch.nn as nn

class FlatMLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 256): ...
    def forward(self, weights_flat: "Tensor[B, D]") -> "Tensor[B]": ...
    # Sorts weights by L2 magnitude per layer before concat — handled in loader
```

### encoders/dwsnet.py

**Dependencies**: torch (reference: AvivNavon/DWSNets)

```python
import torch.nn as nn

class DWSNet(nn.Module):
    def __init__(self, weight_shapes: list, hidden_dim: int, n_heads: int): ...
    def forward(self, weights: "list[Tensor]") -> "Tensor[B]": ...
    # Per-layer equivariant layers + mean pool + scalar head
```

### encoders/nft.py

**Dependencies**: torch (reference: AllanYangZhou/nfn)

```python
import torch.nn as nn

class NFT(nn.Module):
    def __init__(self, weight_shapes: list, d_model: int, n_heads: int, n_layers: int): ...
    def forward(self, weights: "list[Tensor]") -> "Tensor[B]": ...
    # Weight rows/cols as tokens → cross-layer transformer → CLS → scalar
    # batch_size=32 required (memory constraint)
```

### encoders/gnn.py

**Dependencies**: torch, torch_geometric (reference: mkofinas/neural-graphs)

```python
import torch.nn as nn

class GNN(nn.Module):
    def __init__(self, node_dim: int, edge_dim: int, hidden_dim: int, n_layers: int): ...
    def forward(self, weights: "list[Tensor]") -> "Tensor[B]": ...
    # Bipartite neuron-weight graph → message passing → global pool → scalar
```

### training/train.py

**Dependencies**: torch, scipy, data/loader, encoders/*

```python
from typing import Type
import torch.nn as nn

def train_encoder(
    encoder: nn.Module,
    zoo: "ZooData",
    lr: float,
    batch_size: int,
    epochs: int,
    seed: int = 42,
    lr_schedule: str = "none",
) -> tuple[nn.Module, float]:
    """Returns (best_model, best_val_spearman)."""
    ...

def random_search(
    encoder_cls: Type[nn.Module],
    arch_kwargs: dict,
    zoo: "ZooData",
    lr_candidates: list,
    batch_size: int,
    epochs: int,
    n_trials: int = 50,
) -> tuple[nn.Module, dict]:
    """Returns (best_model, best_config)."""
    ...
```

### evaluation/evaluate.py

**Dependencies**: scipy, sklearn, torch

```python
import torch.nn as nn

def eval_spearman(model: nn.Module, loader: "DataLoader") -> tuple[float, float]:
    """Returns (r, p_value)."""
    ...

def eval_mse(model: nn.Module, loader: "DataLoader") -> float: ...

def gate_check(results: dict[str, tuple[float, float]]) -> bool:
    """results: {encoder_name: (test_r, test_mse)}. Returns True if >=1 encoder r > 0.5."""
    ...
```

### visualization/figures.py

**Dependencies**: matplotlib, seaborn, numpy

```python
def plot_spearman_bar(results: dict, save_dir: str) -> None:
    """Bar chart of test Spearman r per encoder; threshold line at 0.5."""
    ...

def plot_best_scatter(model: "nn.Module", loader: "DataLoader", save_dir: str) -> None:
    """Predicted gap vs. true gap scatter for best encoder."""
    ...

def plot_gap_histogram(zoo: "ZooData", save_dir: str) -> None: ...

def plot_audit_scatter(zoo: "ZooData", audit_r: float, save_dir: str) -> None: ...

def plot_training_curves(curves: dict[str, list[float]], save_dir: str) -> None:
    """Val Spearman per epoch per encoder (best trial)."""
    ...
```

### config.py

```python
from dataclasses import dataclass, field

@dataclass
class EncoderConfig:
    lr_candidates: list
    batch_size: int
    epochs: int
    lr_schedule: str
    hidden_dim: int

ENCODER_CONFIGS: dict[str, EncoderConfig] = {
    "FlatMLP": EncoderConfig([1e-4, 5e-4, 1e-3], 64, 100, "none", 256),
    "DWSNet":  EncoderConfig([1e-4, 5e-4, 1e-3], 64, 100, "none", 256),
    "NFT":     EncoderConfig([1e-5, 1e-4, 5e-4], 32, 200, "cosine", 256),
    "GNN":     EncoderConfig([1e-4, 5e-4, 1e-3], 64, 100, "cosine", 256),
}

ZOO_PATH: str = "data/cifar10_zoo.npz"
FIGURES_DIR: str = "h-e1/figures"
SEED: int = 42
N_TRIALS: int = 50
GATE_THRESHOLD: float = 0.5
```

### run_experiment.py

```python
def main() -> None:
    # 1. Load zoo
    # 2. run_audit() — raises if A1 fail
    # 3. compute_split() — fixed before any training
    # 4. For each encoder: random_search() → eval_spearman() → eval_mse()
    # 5. gate_check() → print results table
    # 6. All 5 figures
    ...
```

---

## External Dependencies (Reference Repositories)

| Encoder | Repository | URL | Import Note |
|---------|-----------|-----|-------------|
| FlatMLP | cnns_weight_prediction | https://github.com/google-research/google-research/tree/master/cnns_weight_prediction | Reimplemented from paper; no import |
| DWSNet | AvivNavon/DWSNets | https://github.com/AvivNavon/DWSNets | Port equivariant layer into dwsnet.py |
| NFT | AllanYangZhou/nfn | https://github.com/AllanYangZhou/nfn | Port NF transformer into nft.py |
| GNN | mkofinas/neural-graphs | https://github.com/mkofinas/neural-graphs | Port graph encoder into gnn.py |

**Note**: All 4 encoders are ported/adapted into local files. Prediction target changed from `test_acc` to `gap` — the only modification.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Data Pipeline | load_zoo, run_audit, compute_split, ZooDataset, make_loader | 10 | 2+2+2+4 |
| E2 | FlatMLP Encoder | Sort-by-L2 preprocessing + 3-layer MLP + forward interface | 7 | 2+1+1+3 |
| E3 | Equivariant Encoders | Port DWSNet + NFT + GNN from official repos; adapt target | 17 | 4+4+5+4 |
| E4 | Training Loop | train_encoder, random_search (50 trials), checkpoint saving, lr schedules | 13 | 3+3+3+4 |
| E5 | Evaluation + Gate | eval_spearman, eval_mse, gate_check, results table print | 8 | 2+2+2+2 |
| E6 | Visualization | 5 figures (bar, scatter, histogram, audit scatter, training curves) | 8 | 2+2+2+2 |

**Distribution**: High(14-17): [E3], Medium(9-13): [E4], Low(4-8): [E1, E2, E5, E6]

**Total Epics**: 6 (within LIGHT tier 4–8 budget)
**Subtask budget remaining**: ~9 for Logic + Config agents
