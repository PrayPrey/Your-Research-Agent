# Configuration: h-e2 Gradient Variance & Forgetting Analysis

**Hypothesis:** h-e2  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-08-28  
**Author:** yoon303@ust.ac.kr  

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Extends h-e1 validated infrastructure  
**Config Pattern**: Hardcoded dict (EXISTENCE PoC)  

---

## Applied Patterns

Applied: Minimal PoC extension (reuse h-e1 config + add tracker params)

---

## Inherited Configuration (Base Hypothesis)

### Config Values (From Actual Code)

The following configs are inherited from h-e1 actual implementation:

```python
# From: h-e1/code/train.py (ACTUAL CODE - lines 12-48)
@dataclass
class TrainConfig:
    dataset: str
    lr: float
    max_epochs: int
    weight_decay: float
    batch_size: int
    seed: int

DATASET_CONFIGS = {
    'CMNIST': {
        'lr': 0.001,
        'batch_size': 128,
        'max_epochs': 20,  # h-e1 reduced for PoC
        'weight_decay': 1e-4
    }
}

# From: h-e1/code/data.py (ACTUAL CODE - lines 14-18)
@dataclass
class DatasetConfig:
    name: Literal['CMNIST', 'Waterbirds', 'CelebA', 'NICO++']
    batch_size: int
    num_workers: int = 4
```

**Verified from**: h-e1/code/train.py, h-e1/code/data.py (actual implementation)

---

## B-1: Gradient Tracker [Complexity: 8, Budget: 0 subtasks]

**Applied**: Standard PyTorch gradient hooks

### Configuration

```python
# h-e2/code/config.py

GRADIENT_TRACKER_CONFIG = {
    'window_size': 3,  # epochs for rolling variance
    'checkpoint_epochs': [10, 20, 30],  # when to compute variance
    'track_per_param': False  # PoC: aggregate all gradients
}
```

---

## B-2: Forgetting Tracker [Complexity: 9, Budget: 0 subtasks]

**Applied**: Toneva et al. 2019 forgetting events metric

### Configuration

```python
FORGETTING_TRACKER_CONFIG = {
    'log_interval': 1,  # every epoch
    'num_samples': 50000  # CMNIST train size
}
```

---

## B-3: Extended Training [Complexity: 11, Budget: 0 subtasks]

**Applied**: h-e1 training loop extension

### Configuration

```python
# Extends h-e1 TrainConfig
EXTENDED_TRAIN_CONFIG = {
    'dataset': 'CMNIST',
    'lr': 0.001,  # inherited from h-e1
    'max_epochs': 30,  # extended from h-e1's 20 for variance analysis
    'weight_decay': 1e-4,  # inherited from h-e1
    'batch_size': 128,  # inherited from h-e1
    'seed': 0,  # PoC: single seed
    'enable_tracking': True  # new: activate trackers
}
```

---

## B-4: Statistical Tests [Complexity: 7, Budget: 0 subtasks]

**Applied**: SciPy standard tests

### Configuration

```python
STATS_CONFIG = {
    'variance_ratio_threshold': 0.7,  # V_spurious/V_core gate
    'p_value_threshold': 0.05,
    'test_variance': 'f_test',
    'test_forgetting': 'paired_ttest'
}
```

---

## B-5: PoC Gate Check [Complexity: 5, Budget: 0 subtasks]

**Applied**: Directional validation (no stats for PoC)

### Configuration

```python
POC_GATE = {
    'variance_ratio_max': 0.7,  # V_s/V_c < 0.7
    'forgetting_direction': 'spurious_less_than_core',
    'require_stats': False  # PoC: direction only
}
```

---

## B-6: Visualization [Complexity: 8, Budget: 0 subtasks]

**Applied**: Matplotlib standard plots

### Configuration

```python
PLOT_CONFIG = {
    'backend': 'Agg',
    'dpi': 150,
    'figsize': (10, 6),
    'color_spurious': '#E74C3C',  # inherited from h-e1
    'color_core': '#3498DB',  # inherited from h-e1
    'output_dir': './h-e2/figures'
}

PLOT_TYPES = ['gate_metrics', 'rolling_variance']  # MANDATORY plots
```

---

## Complete Config Module

```python
# h-e2/code/config.py
import torch
from dataclasses import dataclass
from typing import Literal

# Inherited from h-e1/code/train.py
@dataclass
class TrainConfig:
    dataset: str
    lr: float
    max_epochs: int
    weight_decay: float
    batch_size: int
    seed: int

# Inherited from h-e1/code/data.py
@dataclass
class DatasetConfig:
    name: Literal['CMNIST', 'Waterbirds', 'CelebA', 'NICO++']
    batch_size: int
    num_workers: int = 4

# Extended config for h-e2
EXTENDED_TRAIN_CONFIG = {
    'dataset': 'CMNIST',
    'lr': 0.001,
    'max_epochs': 30,
    'weight_decay': 1e-4,
    'batch_size': 128,
    'seed': 0,
    'enable_tracking': True
}

# Gradient tracking
GRADIENT_TRACKER_CONFIG = {
    'window_size': 3,
    'checkpoint_epochs': [10, 20, 30],
    'track_per_param': False
}

# Forgetting tracking
FORGETTING_TRACKER_CONFIG = {
    'log_interval': 1,
    'num_samples': 50000
}

# Statistical tests
STATS_CONFIG = {
    'variance_ratio_threshold': 0.7,
    'p_value_threshold': 0.05,
    'test_variance': 'f_test',
    'test_forgetting': 'paired_ttest'
}

# PoC gate
POC_GATE = {
    'variance_ratio_max': 0.7,
    'forgetting_direction': 'spurious_less_than_core',
    'require_stats': False
}

# Visualization
PLOT_CONFIG = {
    'backend': 'Agg',
    'dpi': 150,
    'figsize': (10, 6),
    'color_spurious': '#E74C3C',
    'color_core': '#3498DB',
    'output_dir': './h-e2/figures'
}

PLOT_TYPES = ['gate_metrics', 'rolling_variance']

# Reproducibility (inherited from h-e1)
REPRODUCIBILITY_CONFIG = {
    'torch_deterministic': True,
    'cudnn_benchmark': False,
    'cudnn_deterministic': True
}

# Output paths
OUTPUT_CONFIG = {
    'results_dir': './h-e2/results',
    'figures_dir': './h-e2/figures',
    'variance_csv': 'variance_ratios.csv',
    'forgetting_csv': 'forgetting_rates.csv',
    'gate_plot': 'gate_metrics.png',
    'variance_plot': 'rolling_variance.png'
}
```

---

## Validation Checklist

- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Subtask count within budget (all tasks: 0/0)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] EXISTENCE rules: Single fixed config (seed=0), no variations
- [x] Inherited Configuration section with verified field names from h-e1 actual code
- [x] All defaults from h-e1 + minimal extensions
- [x] Ready-to-copy-paste code blocks
