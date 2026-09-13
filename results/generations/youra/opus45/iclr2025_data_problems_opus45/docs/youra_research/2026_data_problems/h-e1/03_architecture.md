# Architecture: H-E1
# Data Attribution Method Comparison - Pareto Trade-off Detection

**Date:** 2026-03-26
**Hypothesis Type:** EXISTENCE (PoC)
**Gate:** MUST_WORK

Applied: Standard PyTorch training loop pattern
Applied: Bootstrap CI / scipy.stats pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. No base hypothesis code exists.

---

## Overview

Minimal PoC to test whether Pareto trade-offs exist between data attribution methods.
Four files, no sub-packages.

- `data.py` - CIFAR-10 loading + LOO retraining
- `model.py` - ResNet-18 for CIFAR-10
- `attribution.py` - TRAK, TracIn, IF, FastIF wrappers
- `evaluate.py` - metrics, bootstrap CIs, crossing detection
- `train.py` - experiment orchestration
- `config.py` - fixed experiment config

---

## File Structure

- `h-e1/code/`
  - `config.py`
  - `data.py`
  - `model.py`
  - `attribution.py`
  - `evaluate.py`
  - `train.py`
  - `figures/` (output directory)
  - `results/` (output directory)

---

## Module Definitions

### Config (`config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class ExperimentConfig:
    # Data
    data_root: str = './data'
    train_subset_size: int = 5000
    loo_test_size: int = 100
    subset_seed: int = 42
    train_batch_size: int = 128
    test_batch_size: int = 256
    # Model training
    epochs: int = 200
    lr: float = 0.1
    momentum: float = 0.9
    weight_decay: float = 5e-4
    lr_milestones: List[int] = field(default_factory=lambda: [100, 150])
    lr_gamma: float = 0.1
    # LOO
    n_loo_retrains: int = 10
    # Methods and budgets
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    method_seeds: List[int] = field(default_factory=lambda: [0, 1, 2])
    # Statistics
    n_bootstrap: int = 1000
    confidence_level: float = 0.95
    # I/O
    results_dir: str = './results'
    figures_dir: str = './figures'
    checkpoint_dir: str = './checkpoints'

def get_config() -> ExperimentConfig: ...
```

---

### Data (`data.py`)

**Dependencies**: config.py

```python
from torch.utils.data import DataLoader, Subset, Dataset
from typing import Tuple
import numpy as np

def get_cifar10_loaders(cfg: ExperimentConfig) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """Returns (train_subset_loader, loo_test_loader, full_test_loader)."""
    ...

def get_subset_indices(cfg: ExperimentConfig) -> np.ndarray:
    """Reproducible 5000-sample subset indices (seed=42)."""
    ...

def get_loo_test_indices(cfg: ExperimentConfig) -> np.ndarray:
    """Reproducible 100-sample LOO test indices (seed=42)."""
    ...
```

---

### Model (`model.py`)

**Dependencies**: config.py

```python
import torch
import torch.nn as nn
from torch.optim import SGD
from torch.optim.lr_scheduler import MultiStepLR

def build_model(device: str = 'cuda') -> nn.Module:
    """ResNet-18 modified for CIFAR-10 (32x32): conv1 kernel=3, no maxpool, fc=10."""
    ...

def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    cfg: ExperimentConfig,
    seed: int,
    device: str = 'cuda',
    save_checkpoints: bool = True,
) -> nn.Module:
    """Train ResNet-18 for cfg.epochs; saves checkpoint every 25 epochs."""
    ...

def load_checkpoint(path: str, device: str = 'cuda') -> nn.Module:
    ...
```

---

### Attribution (`attribution.py`)

**Dependencies**: model.py, config.py

```python
import numpy as np
from typing import Dict, Any

class AttributionMethod:
    """Base wrapper for a data attribution method."""
    def compute_scores(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        test_loader: DataLoader,
        budget: int,
        seed: int,
        cfg: ExperimentConfig,
        device: str = 'cuda',
    ) -> np.ndarray: ...  # shape: (n_train, n_test)


class TRAKMethod(AttributionMethod):
    """Wraps MadryLab/trak TRAKer. Budget maps to proj_dim."""
    def compute_scores(self, model, train_loader, test_loader, budget, seed, cfg, device) -> np.ndarray: ...


class TracInMethod(AttributionMethod):
    """Wraps Captum TracInCPFast. Budget maps to n_checkpoints (1-5)."""
    def compute_scores(self, model, train_loader, test_loader, budget, seed, cfg, device) -> np.ndarray: ...


class IFMethod(AttributionMethod):
    """Wraps nimarb/pytorch_influence_functions. Budget maps to recursion_depth."""
    def compute_scores(self, model, train_loader, test_loader, budget, seed, cfg, device) -> np.ndarray: ...


class FastIFMethod(AttributionMethod):
    """Wraps Captum TracInCPFast last-layer. Budget maps to n_checkpoints."""
    def compute_scores(self, model, train_loader, test_loader, budget, seed, cfg, device) -> np.ndarray: ...


def get_method(name: str) -> AttributionMethod: ...

BUDGET_MAP: Dict[str, Dict[int, Any]] = {
    'TRAK':   {10: {'proj_dim': 10}, 25: {'proj_dim': 25}, 50: {'proj_dim': 50}, 75: {'proj_dim': 75}, 100: {'proj_dim': 100}},
    'TracIn': {10: {'n_ckpts': 1},   25: {'n_ckpts': 2},   50: {'n_ckpts': 3},   75: {'n_ckpts': 4},  100: {'n_ckpts': 5}},
    'IF':     {10: {'depth': 10},    25: {'depth': 25},    50: {'depth': 50},    75: {'depth': 75},   100: {'depth': 100}},
    'FastIF': {10: {'n_ckpts': 1},   25: {'n_ckpts': 2},   50: {'n_ckpts': 3},   75: {'n_ckpts': 4},  100: {'n_ckpts': 5}},
}
```

---

### Evaluate (`evaluate.py`)

**Dependencies**: config.py

```python
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class MetricResult:
    rho_r: float        # Spearman correlation
    rho_m: float        # Pearson correlation
    S: float            # Normalized stability
    rho_r_ci: Tuple[float, float]   # 95% bootstrap CI
    rho_m_ci: Tuple[float, float]

@dataclass
class CrossingResult:
    method_a: str
    method_b: str
    budget: int
    crosses_rho_r: bool   # CI-separated, opposite sign
    crosses_rho_m: bool

def compute_loo_ground_truth(
    model_fn,           # Callable: seed -> nn.Module
    train_loader: DataLoader,
    loo_test_loader: DataLoader,
    loo_test_indices: np.ndarray,
    cfg: ExperimentConfig,
    device: str = 'cuda',
) -> np.ndarray: ...    # shape: (n_train, n_loo_test)

def compute_metrics(
    pred_scores: np.ndarray,
    loo_ground_truth: np.ndarray,
    cfg: ExperimentConfig,
) -> MetricResult: ...

def detect_crossings(
    results: Dict[str, Dict[int, List[MetricResult]]],  # [method][budget][seeds]
    cfg: ExperimentConfig,
) -> List[CrossingResult]: ...

def identify_pareto_front(
    results: Dict[str, Dict[int, List[MetricResult]]],
    budget: int,
) -> List[str]: ...     # non-dominated method names

def plot_all_figures(
    results: Dict[str, Dict[int, List[MetricResult]]],
    crossings: List[CrossingResult],
    cfg: ExperimentConfig,
) -> None: ...
```

---

### Train (`train.py`)

**Dependencies**: config.py, data.py, model.py, attribution.py, evaluate.py

```python
import json
import numpy as np
from pathlib import Path

def run_experiment(cfg: ExperimentConfig, device: str = 'cuda') -> None:
    """
    Main entry point.
    1. Load data
    2. Train base model + save checkpoints
    3. Compute LOO ground truth (or load cached)
    4. For each method x budget x seed: compute attribution scores + metrics
    5. Detect crossings, identify Pareto fronts
    6. Save results CSV + JSON
    7. Generate all figures
    """
    ...

def save_results(results: dict, cfg: ExperimentConfig) -> None: ...

def load_cached_loo(cfg: ExperimentConfig) -> np.ndarray | None: ...

if __name__ == '__main__':
    cfg = get_config()
    run_experiment(cfg)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Env, config, data loading, CIFAR-10 subset + LOO split | 7 | 2+1+2+2 |
| A-2 | Model Training | ResNet-18 CIFAR-10 modification, training loop, checkpoint saving | 9 | 2+2+3+2 |
| A-3 | LOO Ground Truth | R=10 retraining loop, leave-one-out delta computation, caching | 13 | 3+2+5+3 |
| A-4 | Attribution Methods | TRAK + TracIn + IF + FastIF wrappers with budget mapping | 16 | 3+4+5+4 |
| A-5 | Metrics + Stats | rho_r, rho_m, S computation, bootstrap CIs, crossing detection | 12 | 2+2+5+3 |
| A-6 | Orchestration + Visualization | Full experiment loop, results CSV, 4+ figures, report | 10 | 2+3+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-3, A-5, A-6, A-2], Low(4-8): [A-1]

---

## Module Dependency Graph

- `train.py` -> `config.py`, `data.py`, `model.py`, `attribution.py`, `evaluate.py`
- `attribution.py` -> `model.py`, `config.py`
- `evaluate.py` -> `config.py`
- `data.py` -> `config.py`
- `model.py` -> `config.py`

---

## External Libraries

| Library | Install | Usage |
|---------|---------|-------|
| `traker[fast]` | `pip install traker[fast]` | TRAK attribution |
| `captum` | `pip install captum` | TracIn, FastIF |
| `pytorch_influence_functions` | `pip install pytorch-influence-functions` | IF |
| `scipy` | `pip install scipy` | bootstrap CI, spearmanr, pearsonr |
| `torchvision` | bundled | ResNet-18, CIFAR-10 |
| `matplotlib` | bundled | figures |
| `pandas` | bundled | results CSV |
