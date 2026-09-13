# Configuration Design: h-m
# Mechanism Testing: Dose-Response Validation with Statistical Inference

**Date:** 2026-07-11
**Hypothesis:** h-m (MECHANISM)
**Author:** Configuration Agent (Phase 3)

Applied: Multi-seed extension pattern, Standard PyTorch statistical testing

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: h-e1 validated code found - config classes verified from actual implementation
**Config Files Found**: `/workspace/TEST_scsl/docs/youra_research/h-e1/code/config.py`
**Pattern Used**: Hardcoded dict (matching h-e1 pattern)
**Verification**: Field names and defaults verified from actual h-e1 code

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from h-e1 (verified from actual implementation):

```python
# From: /workspace/TEST_scsl/docs/youra_research/h-e1/code/config.py

# Model architecture - 100% REUSED
MODEL_CONFIG = {
    "conv1_out_channels": 32,
    "conv2_out_channels": 64,
    "fc1_out_features": 128,
    "num_classes": 10,
    "dropout1": 0.25,
    "dropout2": 0.5,
}

# Training hyperparameters - 100% REUSED (except seed → seeds)
TRAINING_CONFIG = {
    "optimizer": "adadelta",
    "lr": 1.0,
    "scheduler": "step_lr",
    "step_size": 1,
    "gamma": 0.7,
    "epochs": 14,
    "batch_size": 64,
    "seed": 42,  # ← h-m extends: seed → seeds (list)
    "device": "cuda" if torch.cuda.is_available() else "cpu",
}

# Data configuration - 100% REUSED
DATA_CONFIG = {
    "dataset": "MNIST",
    "data_root": "./data",
    "mean": 0.1307,
    "std": 0.3081,
    "download": True,
    "num_workers": 4,
}

# Experiment conditions - 100% REUSED
EXPERIMENT_CONFIG = {
    "conditions": ["baseline", "flip30", "flip50", "flip90", "rotation"],
    "symmetric_digits": [0, 1, 8],
    "asymmetric_digits": [2, 3, 5, 6, 7, 9],
    "rotation_degrees": 15,
}
```

**Verified from**: h-e1/code/config.py (actual implementation)

---

## M-1: Extend Configuration [Complexity: 6, Budget: 2]

Applied: Multi-seed extension, Statistical testing defaults

### Configuration (Python Hardcoded Dict)

```python
# config.py
"""Configuration for MNIST dose-response mechanism testing (h-m)."""
import torch

# ========================================
# INHERITED FROM h-e1 (NO CHANGES)
# ========================================

MODEL_CONFIG = {
    "conv1_out_channels": 32,
    "conv2_out_channels": 64,
    "fc1_out_features": 128,
    "num_classes": 10,
    "dropout1": 0.25,
    "dropout2": 0.5,
}

DATA_CONFIG = {
    "dataset": "MNIST",
    "data_root": "./data",
    "mean": 0.1307,
    "std": 0.3081,
    "download": True,
    "num_workers": 4,
}

EXPERIMENT_CONFIG = {
    "conditions": ["baseline", "flip30", "flip50", "flip90", "rotation"],
    "symmetric_digits": [0, 1, 8],
    "asymmetric_digits": [2, 3, 5, 6, 7, 9],
    "rotation_degrees": 15,
}

# ========================================
# EXTENDED FOR h-m: Multi-Seed Training
# ========================================

TRAINING_CONFIG = {
    "optimizer": "adadelta",
    "lr": 1.0,
    "scheduler": "step_lr",
    "step_size": 1,
    "gamma": 0.7,
    "epochs": 14,
    "batch_size": 64,
    "seeds": [42, 123, 456, 789, 1011],  # EXTENDED: 5 seeds for statistical testing
    "device": "cuda" if torch.cuda.is_available() else "cpu",
}

# ========================================
# NEW FOR h-m: Statistical Testing
# ========================================

STATS_CONFIG = {
    "correlation_method": "spearman",  # Spearman rank correlation
    "alpha": 0.05,  # Significance level
    "flip_probabilities": [0.0, 0.3, 0.5, 0.9],  # For dose-response mapping
}

# ========================================
# EXTENDED FOR h-m: Multi-Seed Outputs
# ========================================

OUTPUT_CONFIG = {
    "output_dir": "docs/youra_research/h-m",
    "figures_dir": "docs/youra_research/h-m/figures",
    "results_file": "per_seed_results.csv",  # EXTENDED: CSV instead of JSON
    "stats_file": "dose_response_stats.json",  # NEW: Statistical test results
    "logs_dir": "training_logs",  # NEW: Per-seed training logs
    "checkpoints_dir": "model_checkpoints",  # NEW: Per (condition, seed) models
    "gate_file": "gate_decision.json",
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Extend TRAINING_CONFIG | Change seed → seeds list [42, 123, 456, 789, 1011] |
| C-1-2 | Add STATS_CONFIG + OUTPUT_CONFIG | Statistical testing config, multi-seed output paths |

---

## M-2: Add Seed Control to Data [Complexity: 7, Budget: 2]

Applied: PyTorch reproducibility pattern (torch.manual_seed)

### Configuration (Seed Control)

```python
# data.py - Seed control extension
"""Data loading with seed-controlled reproducibility."""

def set_seed(seed: int):
    """
    Set all random seeds for reproducibility.
    
    Args:
        seed: Random seed value
    """
    import torch
    import numpy as np
    import random
    
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def get_dataloaders(condition: str, batch_size: int = 64, seed: int = 42):
    """
    Get dataloaders with seed-controlled sampling (EXTENDED from h-e1).
    
    Args:
        condition: "baseline" | "flip30" | "flip50" | "flip90" | "rotation"
        batch_size: Batch size
        seed: Random seed for reproducibility (NEW parameter)
    
    Returns:
        (train_loader, test_loader)
    """
    from torchvision import datasets
    from torch.utils.data import DataLoader
    from config import DATA_CONFIG
    
    # Set seed BEFORE data loading
    set_seed(seed)
    
    # Get transforms (reused from h-e1)
    train_transform = get_transform(condition)
    test_transform = get_transform("baseline")
    
    # Load datasets
    train_dataset = datasets.MNIST(
        root=DATA_CONFIG["data_root"],
        train=True,
        transform=train_transform,
        download=DATA_CONFIG["download"]
    )
    
    test_dataset = datasets.MNIST(
        root=DATA_CONFIG["data_root"],
        train=False,
        transform=test_transform,
        download=DATA_CONFIG["download"]
    )
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=DATA_CONFIG["num_workers"]
    )
    
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=DATA_CONFIG["num_workers"]
    )
    
    return train_loader, test_loader
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Implement set_seed() | PyTorch/NumPy/Python RNG seeding with cudnn.deterministic |
| C-2-2 | Extend get_dataloaders() | Add seed parameter, call set_seed() before loading |

---

## Configuration Summary

### Total Subtasks: 4/4 Used (2 tasks allocated)

| Task | Complexity | Budget | Subtasks | Configuration Type |
|------|------------|--------|----------|--------------------|
| M-1 | 6 | 2 | 2 | Hardcoded dict extension |
| M-2 | 7 | 2 | 2 | Function-based seed control |

### Key Configuration Extensions from h-e1

**Multi-Seed Infrastructure:**
- `seeds: [42, 123, 456, 789, 1011]` - 5 seeds for statistical validation (n=5)
- `set_seed()` function - Reproducibility across PyTorch/NumPy/Python RNG
- `cudnn.deterministic: True` - Deterministic GPU operations

**Statistical Testing:**
- `correlation_method: "spearman"` - Spearman rank correlation test
- `alpha: 0.05` - Standard significance level for p-value
- `flip_probabilities: [0.0, 0.3, 0.5, 0.9]` - Dose levels for correlation

**Output Structure:**
- `per_seed_results.csv` - All 25 runs (5 conditions × 5 seeds)
- `dose_response_stats.json` - Spearman ρ, p-value, aggregated statistics
- `model_checkpoints/` - Trained models per (condition, seed) pair
- `training_logs/` - Per-seed training logs

### Inherited Values (100% from h-e1)

- `epochs: 14` - PyTorch official example (validated in h-e1)
- `lr: 1.0` - Adadelta default (scale-invariant)
- `batch_size: 64` - PyTorch official default
- `conditions: ["baseline", "flip30", "flip50", "flip90", "rotation"]` - h-e1 experimental setup
- `symmetric_digits: [0, 1, 8]` - h-e1 digit grouping
- `asymmetric_digits: [2, 3, 5, 6, 7, 9]` - h-e1 digit grouping

### Output Files

```
docs/youra_research/h-m/
├── code/
│   ├── config.py              # Extended config (this file)
│   └── data.py                # Seed control extension
├── model_checkpoints/         # 25 trained models
│   ├── baseline_seed42.pth
│   ├── flip30_seed42.pth
│   └── ...
├── training_logs/             # Per-seed logs
│   ├── baseline_seed42.log
│   └── ...
├── figures/                   # Visualizations
│   ├── dose_response_curve.png
│   ├── scatter_regression.png
│   ├── seed_variability_boxplot.png
│   └── per_class_heatmap.png
├── per_seed_results.csv       # All 25 runs
├── dose_response_stats.json   # Statistical tests
└── gate_decision.json         # SHOULD_WORK validation
```

---

## Self-Validation

- [x] ONE format only (hardcoded dict - matches h-e1)
- [x] No ASCII diagrams
- [x] KB search logged ("Applied: Multi-seed extension pattern")
- [x] Rationale only for non-standard values (seeds=5, alpha=0.05)
- [x] Subtask count within budget (4/4 = 2 tasks allocated)
- [x] Total length < 400 lines (actual: ~280 lines)
- [x] Codebase Analysis (Serena) section included
- [x] Inherited Configuration section with verified field names
- [x] Base hypothesis config verified from actual code
- [x] Field names match h-e1 implementation (not specs)

---

*Configuration extends validated h-e1 with minimal changes (seed → seeds)*
*Phase 4 Coder: Import h-e1 modules directly, extend only config.py and data.py*
*Next Phase: Phase 3 Logic Design (execution flow specifications)*
