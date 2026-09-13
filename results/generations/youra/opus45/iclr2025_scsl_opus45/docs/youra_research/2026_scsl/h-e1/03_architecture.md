# Architecture Design: H-E1

**Hypothesis**: Per-sample loss trajectory features predict minority group membership (AUROC > 0.75)
**Type**: EXISTENCE (PoC)
**Date**: 2026-04-14

Applied: PyTorch standard training loop pattern (reduction='none' per-sample loss)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. H-E1 is the foundation hypothesis with no prior codebase.

---

## File Organization

- `code/`
  - `config.py` - fixed experiment configuration
  - `data.py` - Waterbirds dataset loading and preprocessing
  - `model.py` - ResNet-50 model definition
  - `train.py` - ERM training loop with per-sample loss logging
  - `evaluate.py` - trajectory feature extraction, AUROC evaluation, visualization
  - `run.py` - experiment entry point

---

## Module Definitions

### Config (`code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass

@dataclass
class Config:
    # Dataset
    data_root: str = "./data"
    dataset: str = "waterbirds"
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
    # Output
    output_dir: str = "./results"
    figures_dir: str = "./figures"

def get_config() -> Config: ...
```

---

### DataModule (`code/data.py`)

**Dependencies**: Config

```python
from torch.utils.data import Dataset, DataLoader
from typing import Tuple
import torch

class WaterbirdsDataset(Dataset):
    def __init__(self, root: str, split: str, augment: bool = False): ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int, int, int]: ...
    # Returns: (image, label, group_id, sample_idx)

def get_train_transforms(): ...
def get_eval_transforms(): ...

def get_dataloaders(config: "Config") -> Tuple[DataLoader, DataLoader, DataLoader]:
    # Returns: train_loader, val_loader, test_loader
    ...

def get_eval_dataloader(config: "Config") -> DataLoader:
    # Deterministic loader, no augmentation, fixed order
    ...
```

---

### Model (`code/model.py`)

**Dependencies**: Config

```python
import torch
import torch.nn as nn

class ResNet50Classifier(nn.Module):
    def __init__(self, num_classes: int = 2, pretrained: bool = True): ...
    def forward(self, x: torch.Tensor) -> torch.Tensor: ...
    # Returns: logits shape (B, num_classes)

def build_model(config: "Config") -> ResNet50Classifier: ...
```

---

### Trainer (`code/train.py`)

**Dependencies**: Config, ResNet50Classifier, WaterbirdsDataset, LossTrajectoryTracker

```python
import torch
import numpy as np
from typing import Dict

class LossTrajectoryTracker:
    def __init__(self, num_samples: int, num_epochs: int = 5): ...
    def log_epoch_losses(self, sample_indices: np.ndarray, losses: np.ndarray) -> None: ...
    def get_loss_matrix(self) -> np.ndarray: ...
    # Returns: shape (num_samples, num_epochs)

def run_epoch_eval_pass(
    model: "ResNet50Classifier",
    eval_loader: "DataLoader",
    device: torch.device,
    tracker: LossTrajectoryTracker,
    epoch_idx: int,
) -> None: ...

def train(
    config: "Config",
    model: "ResNet50Classifier",
    train_loader: "DataLoader",
    eval_loader: "DataLoader",
    device: torch.device,
) -> Tuple[ResNet50Classifier, LossTrajectoryTracker]: ...
# Returns trained model and populated tracker
```

---

### Evaluator (`code/evaluate.py`)

**Dependencies**: Config, LossTrajectoryTracker

```python
import numpy as np
from typing import Tuple, Dict

def extract_trajectory_features(loss_matrix: np.ndarray) -> np.ndarray:
    # Returns: shape (num_samples, 4) - [L1, slope, variance, convergence_time]
    ...

def compute_auroc_cv(
    features: np.ndarray,
    minority_labels: np.ndarray,
    n_splits: int = 5,
    seed: int = 42,
) -> Tuple[float, float]: ...
# Returns: (mean_auroc, std_auroc)

def compute_per_feature_auroc(
    features: np.ndarray,
    minority_labels: np.ndarray,
) -> Dict[str, float]: ...
# Returns: {"L1": auroc, "slope": auroc, "variance": auroc, "convergence": auroc}

def evaluate_gate(auroc: float, threshold: float = 0.75) -> bool: ...

def plot_gate_metrics(auroc: float, threshold: float, save_path: str) -> None: ...
def plot_loss_trajectories(loss_matrix: np.ndarray, minority_labels: np.ndarray, save_path: str) -> None: ...
def plot_roc_curve(features: np.ndarray, minority_labels: np.ndarray, save_path: str) -> None: ...
def plot_feature_distributions(features: np.ndarray, minority_labels: np.ndarray, save_path: str) -> None: ...
```

---

### Runner (`code/run.py`)

**Dependencies**: Config, DataModule, Model, Trainer, Evaluator

```python
def main(config: "Config") -> Dict[str, float]: ...
# Orchestrates: setup → data → train → evaluate → visualize → gate check

if __name__ == "__main__":
    config = get_config()
    results = main(config)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Directory structure, config, dependencies | 5 | 1+1+1+2 |
| A-2 | Data Loading | WaterbirdsDataset with group labels, deterministic eval loader | 10 | 2+2+3+3 |
| A-3 | Model Definition | ResNet-50 pretrained with binary head | 7 | 2+1+2+2 |
| A-4 | Training Loop + Tracker | ERM training with per-sample loss logging across epochs 1-5 | 15 | 3+3+4+5 |
| A-5 | Feature Extraction + AUROC | Trajectory features (L1, slope, var, convergence), 5-fold CV | 14 | 3+3+4+4 |
| A-6 | Visualization + Gate Check | Required figures, gate evaluation, results logging | 9 | 2+2+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-4, A-5], Medium(9-13): [A-2, A-6], Low(4-8): [A-1, A-3]

---

## Data Flow

- `run.py` calls `get_config()` → `get_dataloaders()` → `build_model()` → `train()`
- `train()` after each of epochs 1-5: calls `run_epoch_eval_pass()` → `tracker.log_epoch_losses()`
- After training: `extract_trajectory_features(tracker.get_loss_matrix())`
- `compute_auroc_cv(features, minority_labels)` → `evaluate_gate(auroc)`
- Plot functions save all figures to `figures/`

## Minority Label Definition

- Groups 2 (landbirds on water) and 4 (waterbirds on land) = minority (label=1)
- Groups 1 and 3 = majority (label=0)
- Group labels sourced from WaterbirdsDataset `__getitem__` return value (group_id)

---

*Architecture for EXISTENCE hypothesis H-E1*
*Green-field project - no prior code base*
