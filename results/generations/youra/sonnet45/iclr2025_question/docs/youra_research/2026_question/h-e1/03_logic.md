# Logic Design: h-e1 Variance Measurement

**Date:** 2026-03-21
**Hypothesis ID:** h-e1 (EXISTENCE)
**Version:** 3.0
**Phase:** 3 (Implementation Planning)
**Budget:** 4 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase
**Status:** Existing patterns found in `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_question/code/`
**Analyzed Path:** `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_question/code/`
**Relevant Symbols:**
- `data.py`: `set_seed()`, `get_mnist_loaders()`
- `model.py`: `MLP`, `create_model()`
- `train.py`: `train_epoch()`, `evaluate()`, `train_single_seed()`
- `evaluate.py`, `visualize.py`, `run_experiment.py` (orchestration)

**Finding:** Existing codebase uses similar structure (config, data, model, train, evaluate, visualize, run_experiment). New implementation extends with dual-dataset and dual-architecture support.

---

## Applied Patterns

**Applied:** PyTorch deterministic training pattern
**Applied:** DataLoader generator seeding for reproducibility
**Applied:** Modular experiment orchestration pattern

---

## A-1: Configuration Setup [Complexity: 6, Budget: 1/4]

**Applied:** Dataclass configuration pattern

### API Signatures

```python
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class ExperimentConfig:
    """Configuration for variance measurement experiments."""

    datasets: List[str] = field(default_factory=lambda: ["mnist", "fashion_mnist"])
    architectures: List[str] = field(default_factory=lambda: ["1layer", "2layer"])
    seeds: List[int] = field(default_factory=lambda: list(range(30)))
    epochs: int = 10
    lr: float = 0.01
    momentum: float = 0.9
    batch_size: int = 64
    cudnn_deterministic: bool = True
    cudnn_benchmark: bool = False
    data_root: str = "./data"
    results_dir: str = "./results"
    figures_dir: str = "./figures"

    def get_conditions(self) -> List[Tuple[str, str]]:
        """Get all condition combinations. Returns: [(dataset, arch), ...]"""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Config dataclass | Implement ExperimentConfig with validation |

---

## A-2: Data Loading [Complexity: 9, Budget: 1/4]

**Applied:** PyTorch DataLoader with generator seeding

### API Signatures

```python
from torch.utils.data import DataLoader, Dataset
from torchvision import datasets, transforms
import torch

def get_transforms(dataset_name: str) -> transforms.Compose:
    """Get dataset-specific normalization. dataset_name -> transforms"""
    ...

def create_seeded_dataloader(
    dataset: Dataset,
    batch_size: int,
    shuffle: bool,
    seed: int,
    num_workers: int = 0
) -> DataLoader:
    """Create DataLoader with generator. Returns: DataLoader with seeded generator"""
    ...

def load_dataset(
    dataset_name: str,
    data_root: str,
    batch_size: int,
    seed: int
) -> Tuple[DataLoader, DataLoader]:
    """Load MNIST or Fashion-MNIST. Returns: (train_loader, test_loader)"""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Dataset factory | Implement dual-dataset loading with proper normalization |

---

## A-3: Model Implementation [Complexity: 7, Budget: 0/4]

**Applied:** Standard PyTorch nn.Module pattern

### API Signatures

```python
import torch.nn as nn
import torch

class SimpleMLP1Layer(nn.Module):
    """1-layer MLP: 784 -> 128 (ReLU) -> 10"""

    def __init__(self, input_size: int = 784, hidden_size: int = 128, output_size: int = 10):
        ...

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass. x: [B, 1, 28, 28] -> [B, 10]"""
        ...

class SimpleMLP2Layer(nn.Module):
    """2-layer MLP: 784 -> 256 (ReLU) -> 128 (ReLU) -> 10"""

    def __init__(self, input_size: int = 784, hidden1: int = 256, hidden2: int = 128, output_size: int = 10):
        ...

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass. x: [B, 1, 28, 28] -> [B, 10]"""
        ...

def create_model(architecture: str) -> nn.Module:
    """Factory function. architecture: '1layer' or '2layer' -> nn.Module"""
    ...
```

---

## A-4: Training Logic [Complexity: 11, Budget: 1/4]

**Applied:** PyTorch deterministic seed protocol

### API Signatures

```python
import torch
import torch.nn as nn
from torch.optim import SGD, Optimizer
from torch.utils.data import DataLoader

def set_seed_deterministic(seed: int) -> None:
    """Set all random seeds for reproducibility."""
    ...

def train_epoch(
    model: nn.Module,
    train_loader: DataLoader,
    optimizer: Optimizer,
    criterion: nn.Module,
    device: str
) -> float:
    """Train for one epoch. Returns: average loss"""
    ...

def train_model(
    model: nn.Module,
    train_loader: DataLoader,
    epochs: int,
    lr: float,
    momentum: float,
    device: str
) -> None:
    """Full training loop. Modifies model in-place."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Deterministic training | Implement seed control and training loop |

---

## A-5: Evaluation & Metrics [Complexity: 10, Budget: 1/4]

**Applied:** SciPy bootstrap confidence intervals

### API Signatures

```python
import numpy as np
from scipy import stats
from typing import Dict, List

def evaluate_model(model: nn.Module, test_loader: DataLoader, device: str) -> float:
    """Compute test accuracy. Returns: accuracy in % (0-100)"""
    ...

def compute_variance_metrics(test_accuracies: List[float]) -> Dict[str, float]:
    """Calculate variance, std, CV%, CI. Returns: metrics dict"""
    ...

def check_gate_condition(
    variance_summary: Dict[str, Dict[str, float]],
    threshold: float = 0.3
) -> Dict[str, any]:
    """Validate MUST_WORK gate. Returns: gate result dict"""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Variance statistics | Implement variance metrics with bootstrap CI |

---

## A-6: Experiment Orchestration [Complexity: 14, Budget: 0/4]

**Applied:** Sequential experiment executor pattern

### API Signatures

```python
import pandas as pd
import json
import time
from pathlib import Path
from typing import Dict, Any

def run_single_experiment(
    dataset_name: str,
    architecture: str,
    seed: int,
    config: ExperimentConfig,
    device: str
) -> Dict[str, Any]:
    """Execute one training run. Returns: result dict with test_accuracy"""
    ...

def run_all_experiments(config: ExperimentConfig, device: str = "cuda") -> pd.DataFrame:
    """Run 120 experiments (4 conditions × 30 seeds). Returns: DataFrame"""
    ...

def generate_variance_summary(results_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """Aggregate variance metrics per condition. Returns: summary dict"""
    ...

def save_results(
    results_df: pd.DataFrame,
    variance_summary: Dict,
    gate_result: Dict,
    config: ExperimentConfig
) -> None:
    """Save experiment logs, variance summary, gate result."""
    ...
```

---

## A-7: Visualization [Complexity: 12, Budget: 0/4]

**Applied:** matplotlib + seaborn standard plots

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

def plot_gate_metrics_comparison(
    variance_summary: Dict[str, Dict[str, float]],
    threshold: float,
    save_path: str
) -> None:
    """Bar chart: target vs actual variance with CI error bars."""
    ...

def plot_variance_by_condition(variance_summary: Dict[str, Dict[str, float]], save_path: str) -> None:
    """Bar chart: variance for all 4 conditions."""
    ...

def plot_accuracy_distributions(results_df: pd.DataFrame, save_path: str) -> None:
    """2×2 histogram grid for test accuracies."""
    ...

def plot_cv_comparison(variance_summary: Dict[str, Dict[str, float]], save_path: str) -> None:
    """Bar chart: coefficient of variation."""
    ...

def plot_accuracy_ranges(variance_summary: Dict[str, Dict[str, float]], save_path: str) -> None:
    """Error bar plot showing min/max/mean per condition."""
    ...

def generate_all_figures(
    results_df: pd.DataFrame,
    variance_summary: Dict,
    threshold: float,
    figures_dir: str
) -> None:
    """Generate all 5 required figures."""
    ...
```

---

## A-8: Gate Validation [Complexity: 8, Budget: 0/4]

**Applied:** Simple threshold comparison

### API Signatures

```python
def validate_and_save_gate(
    variance_summary: Dict[str, Dict[str, float]],
    threshold: float,
    results_dir: str
) -> Dict[str, Any]:
    """Check MUST_WORK condition and save gate_result.json. Returns: gate result"""
    ...
```

---

## Main Orchestration Flow

```python
def main():
    """Entry point: orchestrate full experiment workflow."""
    config = ExperimentConfig()
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Run experiments (120 total)
    results_df = run_all_experiments(config, device)

    # Compute variance metrics
    variance_summary = generate_variance_summary(results_df)

    # Validate gate
    gate_result = validate_and_save_gate(variance_summary, threshold=0.3, results_dir=config.results_dir)

    # Save results
    save_results(results_df, variance_summary, gate_result, config)

    # Generate figures
    generate_all_figures(results_df, variance_summary, threshold=0.3, figures_dir=config.figures_dir)

    print(f"Gate Result: {gate_result['gate_result']}")
```

---

## Budget Summary

**Total Budget:** 4 subtasks
**Allocated:**
- A-1 Configuration: 1 subtask (L-1-1)
- A-2 Data Loading: 1 subtask (L-2-1)
- A-4 Training Logic: 1 subtask (L-4-1)
- A-5 Evaluation: 1 subtask (L-5-1)

**Remaining:** 0 subtasks
**Status:** EXACT budget compliance (4/4 used)

---

## Implementation Notes

### Determinism Protocol
1. `torch.manual_seed(seed)`, `np.random.seed(seed)`, `random.seed(seed)`
2. `torch.backends.cudnn.deterministic = True`
3. `torch.backends.cudnn.benchmark = False`
4. `CUBLAS_WORKSPACE_CONFIG=:4096:8`
5. DataLoader `generator` parameter for reproducible shuffling
6. `num_workers=0` to avoid multiprocessing non-determinism

### Expected Variance Ranges
- MNIST 1-layer: σ² ≈ 0.09-0.25%
- MNIST 2-layer: σ² ≈ 0.16-0.49%
- Fashion-MNIST 1-layer: σ² ≈ 0.25-1.0%
- Fashion-MNIST 2-layer: σ² ≈ 0.49-1.44%

---

**Architecture Complexity:** LIGHT (EXISTENCE PoC)
**Total Subtasks:** 4
**Expected Implementation Time:** Phase 4 (1-2 days)
**Next Phase:** Phase 4 (Coding and Experimentation)
