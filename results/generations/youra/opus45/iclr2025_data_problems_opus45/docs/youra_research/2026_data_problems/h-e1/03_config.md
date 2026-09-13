# Configuration: h-e1 Data Attribution Pareto Trade-offs

**Hypothesis**: h-e1 (EXISTENCE)
**Date**: 2026-03-26

Applied: Standard PyTorch defaults (Archon KB returned unrelated results - no domain-specific config patterns found; config derived from TRAK paper / Park et al. ICML 2023 CIFAR-10 setup)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass (single ExperimentConfig, consistent with 03_architecture.md)

---

## A-6: Orchestration [Complexity: 1, Budget: 1]

Applied: Standard experiment orchestration pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class ExperimentConfig:
    # --- Data ---
    data_root: str = './data'
    train_subset_size: int = 5000
    loo_test_size: int = 100
    subset_seed: int = 42
    train_batch_size: int = 128
    test_batch_size: int = 256

    # --- Model Training ---
    epochs: int = 200
    lr: float = 0.1
    momentum: float = 0.9
    weight_decay: float = 5e-4
    lr_milestones: List[int] = field(default_factory=lambda: [100, 150])
    lr_gamma: float = 0.1

    # --- LOO Ground Truth ---
    n_loo_retrains: int = 10

    # --- Attribution Methods and Compute Budgets ---
    methods: List[str] = field(default_factory=lambda: ['TRAK', 'TracIn', 'IF', 'FastIF'])
    compute_budgets: List[int] = field(default_factory=lambda: [10, 25, 50, 75, 100])
    # Non-standard: 3 seeds per method to compute stability metric S
    method_seeds: List[int] = field(default_factory=lambda: [0, 1, 2])

    # --- Bootstrap Statistics ---
    n_bootstrap: int = 1000
    confidence_level: float = 0.95

    # --- I/O Paths ---
    results_dir: str = './results'
    figures_dir: str = './figures'
    checkpoint_dir: str = './checkpoints'


def get_config() -> ExperimentConfig:
    return ExperimentConfig()
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | ExperimentConfig (paths + orchestration fields) | Paths, methods list, compute budgets, LOO and bootstrap settings |

---

## A-2: Training [Complexity: 1, Budget: 1]

Applied: Standard ResNet CIFAR-10 training defaults (TRAK paper / Park et al. ICML 2023)

Training hyperparameters are part of `ExperimentConfig` (no separate class for PoC). Key fields:

| Field | Value | Note |
|-------|-------|------|
| `lr` | 0.1 | TRAK CIFAR-10 quickstart standard |
| `momentum` | 0.9 | Standard SGD |
| `weight_decay` | 5e-4 | Standard ResNet CIFAR-10 |
| `epochs` | 200 | Standard CIFAR-10 convergence |
| `lr_milestones` | [100, 150] | MultiStepLR schedule |
| `lr_gamma` | 0.1 | Standard decay |
| `train_batch_size` | 128 | TRAK quickstart |
| `n_loo_retrains` | 10 | PoC: limited retrains for feasibility |

CIFAR-10 normalization constants (used in `data.py`, not in config dataclass):
```python
NORMALIZE_MEAN = [0.4914, 0.4822, 0.4465]
NORMALIZE_STD  = [0.2470, 0.2435, 0.2616]
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Training hyperparameters | SGD + MultiStepLR defaults embedded in ExperimentConfig |
