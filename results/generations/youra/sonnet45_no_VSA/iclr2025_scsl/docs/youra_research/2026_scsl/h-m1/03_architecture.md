# System Architecture: h-m1

**Hypothesis**: Asymmetric digit degradation increases monotonically with flip probability (dose-response relationship)  
**Type**: MECHANISM  
**Date**: 2026-07-11

---

## Applied Patterns

**Archon KB**: PyTorch experiment module structure (standard training/evaluation separation)

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase  
**Status**: Patterns found from h-e1 experiment  
**Analyzed Path**: experiments/h-e1/  
**Findings**: Dataclass config pattern, modular train/eval separation, optimizer abstractions

---

## System Overview

```
experiments/h-m1/
├── config.py           # Experiment configuration (dataclasses)
├── data/
│   ├── __init__.py
│   └── datasets.py     # MNIST loading, transforms
├── models/
│   ├── __init__.py
│   └── baseline.py     # Standard CNN
├── train.py            # Training loop
├── evaluate.py         # Metrics computation
├── visualize.py        # Plotting functions
└── run_experiment.py   # Main orchestration
```

---

## Module Specifications

### 1. Configuration (`config.py`)

**Dependencies**: None

```python
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class DataConfig:
    dataset_name: str = "mnist"
    data_root: str = "data/mnist"
    batch_size: int = 64
    num_workers: int = 4
    flip_probabilities: List[float] = field(default_factory=lambda: [0.0, 0.3, 0.5, 0.9])
    mean: Tuple[float] = (0.1307,)
    std: Tuple[float] = (0.3081,)

@dataclass
class ModelConfig:
    architecture: str = "standard_cnn"
    in_channels: int = 1
    num_classes: int = 10
    dropout_conv: float = 0.25
    dropout_fc: float = 0.5

@dataclass
class TrainingConfig:
    optimizer: str = "adam"
    lr: float = 0.001
    max_epochs: int = 30
    patience: int = 5
    scheduler_step: int = 1
    scheduler_gamma: float = 0.7
    gradient_clip_norm: float = 1.0
    seeds: List[int] = field(default_factory=lambda: [42, 43, 44, 45, 46])

@dataclass
class ExperimentConfig:
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    output_dir: str = "experiments/h-m1/results"
    device: str = "cuda"

def get_config(**kwargs) -> ExperimentConfig: ...
```

---

### 2. Data Module (`data/datasets.py`)

**Dependencies**: DataConfig

```python
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

def create_transform(flip_prob: float, mean: Tuple[float], std: Tuple[float]) -> transforms.Compose: ...

def get_dataloaders(
    config: DataConfig,
    flip_prob: float
) -> Tuple[DataLoader, DataLoader]: ...
```

---

### 3. Model Module (`models/baseline.py`)

**Dependencies**: ModelConfig

```python
import torch.nn as nn

class StandardCNN(nn.Module):
    def __init__(self, config: ModelConfig): ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...
```

---

### 4. Training Module (`train.py`)

**Dependencies**: DataConfig, ModelConfig, TrainingConfig

```python
from typing import Dict, Tuple
import torch.nn as nn
from torch.utils.data import DataLoader

def train_epoch(
    model: nn.Module,
    dataloader: DataLoader,
    optimizer,
    scheduler,
    criterion: nn.Module,
    device: str,
    gradient_clip_norm: float
) -> Dict[str, float]: ...

def validate(
    model: nn.Module,
    dataloader: DataLoader,
    criterion: nn.Module,
    device: str
) -> Dict[str, float]: ...

def train_model(
    config: ExperimentConfig,
    flip_prob: float,
    seed: int
) -> Tuple[nn.Module, Dict]: ...
```

---

### 5. Evaluation Module (`evaluate.py`)

**Dependencies**: None

```python
import numpy as np
from typing import Dict, List
from scipy.stats import spearmanr

def compute_asymmetric_accuracy(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    asymmetric_digits: List[int] = [2, 3, 5, 6, 7, 9]
) -> float: ...

def compute_per_digit_accuracy(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[int, float]: ...

def evaluate_model(
    model: nn.Module,
    dataloader: DataLoader,
    device: str
) -> Dict: ...

def dose_response_test(
    results: Dict[float, List[float]]
) -> Dict: ...
```

---

### 6. Visualization Module (`visualize.py`)

**Dependencies**: None

```python
from pathlib import Path
from typing import Dict, List
import matplotlib.pyplot as plt

def plot_dose_response_curve(
    results: Dict[float, List[float]],
    output_path: Path
) -> None: ...

def plot_per_digit_heatmap(
    per_digit_results: Dict[float, Dict[int, float]],
    output_path: Path
) -> None: ...

def plot_degradation_bars(
    results: Dict[float, List[float]],
    output_path: Path
) -> None: ...

def plot_gate_metrics(
    target_rho: float,
    target_p: float,
    actual_rho: float,
    actual_p: float,
    output_path: Path
) -> None: ...
```

---

### 7. Orchestration (`run_experiment.py`)

**Dependencies**: All modules

```python
from pathlib import Path
from typing import Dict

def run_single_condition(
    config: ExperimentConfig,
    flip_prob: float
) -> Dict: ...

def run_all_conditions(
    config: ExperimentConfig
) -> Dict: ...

def save_results(
    results: Dict,
    output_dir: Path
) -> None: ...

def main() -> None: ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup | Project structure + config | 6 | Module(2) + Deps(1) + Algo(1) + Integ(2) |
| A-2 | Data Pipeline | MNIST loading + transforms | 8 | Module(2) + Deps(2) + Algo(2) + Integ(2) |
| A-3 | Model | Standard CNN implementation | 7 | Module(2) + Deps(1) + Algo(2) + Integ(2) |
| A-4 | Training | Training loop + early stopping | 12 | Module(3) + Deps(3) + Algo(3) + Integ(3) |
| A-5 | Evaluation | Metrics + dose-response test | 10 | Module(3) + Deps(2) + Algo(3) + Integ(2) |
| A-6 | Visualization | 4 required plots | 9 | Module(2) + Deps(2) + Algo(3) + Integ(2) |
| A-7 | Orchestration | Multi-condition execution | 14 | Module(3) + Deps(4) + Algo(3) + Integ(4) |
| A-8 | Validation | Statistical tests + report | 8 | Module(2) + Deps(2) + Algo(2) + Integ(2) |

**Total Complexity**: 74 points  
**Distribution**: VeryHigh(18-20): [], High(14-17): [A-7], Medium(9-13): [A-4, A-5], Low(4-8): [A-1, A-2, A-3, A-6, A-8]

---

## Implementation Notes

### Critical Design Decisions

1. **Architecture Reuse**: Uses h-e1 dataclass config pattern for consistency
2. **No Base Hypothesis**: Green-field MNIST implementation (no code reuse from previous hypotheses)
3. **Dose-Response Focus**: Four flip probabilities × 5 seeds = 20 training runs total

### Key Interfaces

**Data Flow**:
```
config → create_transform(flip_prob) → get_dataloaders → train_model → evaluate_model → dose_response_test
```

**Statistical Pipeline**:
```
results[flip_prob][seeds] → mean_accuracy → spearmanr(flip_probs, mean_accs) → gate_decision
```

### Gate Validation

**Criterion**: Spearman ρ < 0, p < 0.05  
**Validation Module**: evaluate.py (dose_response_test function)  
**Gate Type**: SHOULD_WORK (failure documented, workflow continues)

---

## File Structure

```
experiments/h-m1/
├── config.py                    # 150 lines
├── data/
│   ├── __init__.py             # 5 lines
│   └── datasets.py             # 80 lines
├── models/
│   ├── __init__.py             # 5 lines
│   └── baseline.py             # 60 lines
├── train.py                     # 180 lines
├── evaluate.py                  # 120 lines
├── visualize.py                 # 150 lines
├── run_experiment.py            # 140 lines
├── results/                     # Created at runtime
│   ├── checkpoints/
│   ├── logs/
│   └── figures/
└── README.md                    # Usage instructions
```

**Total LOC Estimate**: ~890 lines (excluding tests)

---

## Dependencies

### External Libraries

```python
# requirements.txt
torch>=2.0.0
torchvision>=0.15.0
numpy>=1.24.0
scipy>=1.10.0
matplotlib>=3.7.0
pandas>=2.0.0
```

### Internal Dependencies

None (green-field implementation)

---

## Validation Checklist

- [ ] All 20 training runs complete (4 conditions × 5 seeds)
- [ ] Baseline (p=0.0) achieves ≥98.5% test accuracy
- [ ] Asymmetric digit accuracy computed for all conditions
- [ ] Spearman correlation test performed
- [ ] Gate decision logged (PASS/PARTIAL)
- [ ] 4 required visualizations generated
- [ ] Results saved to results.json
- [ ] Model checkpoints saved (20 files)
- [ ] Training logs saved (20 CSV files)

---

**Next Phase**: Phase 4 - Implementation  
**Estimated Duration**: 4-6 hours (coding + 20 training runs)  
**Primary Risk**: Training divergence (mitigated by gradient clipping + early stopping)
