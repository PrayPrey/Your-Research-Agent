# Configuration: h-e3 GradCAM Temporal Ratio Tracking

**Hypothesis:** h-e3  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-08-28  
**Author:** yoon303@ust.ac.kr  

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Extending h-e1 infrastructure  
**Analyzed Path**: `/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_scsl/docs/youra_research/h-e1/code/`  
**Findings**: Verified DatasetConfig, TrainConfig, DATASET_CONFIGS from actual code. Reusing data loader and model initialization.

---

## Applied Patterns

Applied: Hardcoded dict for EXISTENCE PoC (minimal GradCAM extension)

---

## Inherited Configuration (Base Hypothesis h-e1)

### Config Classes (From Actual Code)

```python
# From: h-e1/code/data.py (ACTUAL CODE)
@dataclass
class DatasetConfig:
    name: Literal['CMNIST', 'Waterbirds', 'CelebA', 'NICO++']
    batch_size: int
    num_workers: int = 4

# From: h-e1/code/train.py (ACTUAL CODE)
@dataclass
class TrainConfig:
    dataset: str
    lr: float
    max_epochs: int
    weight_decay: float
    batch_size: int
    seed: int

# From: h-e1/code/train.py (ACTUAL CODE)
DATASET_CONFIGS = {
    'CMNIST': {
        'lr': 0.001,
        'batch_size': 128,
        'max_epochs': 20,  # Reduced for PoC
        'weight_decay': 1e-4
    },
    'Waterbirds': {
        'lr': 0.001,
        'batch_size': 64,
        'max_epochs': 100,
        'weight_decay': 1e-4
    },
    'CelebA': {
        'lr': 0.0001,
        'batch_size': 64,
        'max_epochs': 80,
        'weight_decay': 1e-4
    },
    'NICO++': {
        'lr': 0.001,
        'batch_size': 64,
        'max_epochs': 100,
        'weight_decay': 1e-4
    }
}
```

**Verified from**: h-e1/code/data.py, h-e1/code/train.py (actual implementation)

---

## A-1: GradCAM Tracker [Complexity: 12, Budget: 2 subtasks]

### Configuration

```python
# h-e3/code/config.py

# GradCAM attribution tracking
GRADCAM_CONFIG = {
    'target_layer': 'layer4',  # ResNet-50 final conv block
    'max_batches_per_epoch': 100,  # Sample for efficiency
    'epsilon': 1e-8,  # Numerical stability for R_temporal division
    'device': 'cuda' if torch.cuda.is_available() else 'cpu'
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | GradCAMTemporalTracker | LayerGradCam wrapper + R_temporal computation |
| C-1-2 | compute_epoch_ratio | Batch attribution aggregation |

---

## A-2: Region Masking [Complexity: 9, Budget: 2 subtasks]

### Configuration

```python
# Region mask extraction (Waterbirds-specific for PoC)
REGION_CONFIG = {
    'spurious_method': 'background',  # Background segmentation
    'core_method': 'bbox_fallback',  # Bird bbox or GradCAM peak
    'mask_shape': (224, 224),  # Match ResNet input
    'bbox_default': [56, 56, 168, 168]  # Center fallback (H/4 to 3H/4)
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | create_region_masks | Extract spurious/core masks from WILDS metadata |
| C-2-2 | apply_attribution_mask | Sum GradCAM values within mask regions |

---

## A-3: Training Loop [Complexity: 11, Budget: 2 subtasks]

### Configuration

```python
# Experiment settings (PoC: Waterbirds only, single seed)
EXPERIMENT_CONFIG = {
    'dataset': 'Waterbirds',
    'lr': 0.001,  # From h-e1 DATASET_CONFIGS
    'batch_size': 128,  # Increased for PoC speed
    'max_epochs': 50,  # PRD requirement
    'weight_decay': 1e-4,
    'seed': 0,
    'tracking_interval': 5,  # Compute R_temporal every 5 epochs
    'model': 'resnet50',
    'pretrained': True  # ImageNet initialization
}

# Training schedule
SCHEDULER_CONFIG = {
    'type': 'step',
    'step_epochs': [30],  # Single decay for PoC
    'gamma': 0.1
}

# Optimizer (SGD from PRD)
OPTIMIZER_CONFIG = {
    'type': 'sgd',
    'momentum': 0.9,
    'weight_decay': 1e-4
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | run_experiment | 50-epoch training loop with GradCAM tracking |
| C-3-2 | tracking_schedule | Compute R_temporal at epochs 5, 10, ..., 50 |

---

## A-4: PoC Validation [Complexity: 6, Budget: 2 subtasks]

### Configuration

```python
# PoC pass conditions
POC_GATE = {
    'delta_threshold': 0.1,  # R_temporal(5) - R_temporal(50) >= 0.1
    'direction_check': 'decreasing',  # R_temporal(5) > R_temporal(50)
    'min_worst_group_acc': 0.7  # Sanity: model converged
}

# Output paths
OUTPUT_CONFIG = {
    'results_dir': './h-e3/results',
    'figures_dir': './h-e3/figures',
    'temporal_csv': 'temporal_ratios.csv',
    'validation_report': '../04_validation.md'
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | check_poc_pass | Validate delta >= 0.1 and direction |
| C-4-2 | compute_delta | R_temporal(5) - R_temporal(50) |

---

## A-5: Visualization [Complexity: 9, Budget: 2 subtasks]

### Configuration

```python
# Plot settings
PLOT_CONFIG = {
    'backend': 'Agg',  # Headless
    'dpi': 150,
    'figsize': (10, 6),
    'color_primary': '#3498DB',
    'marker_style': 'o-',
    'grid': True
}

# Heatmap visualization
HEATMAP_CONFIG = {
    'epochs_to_plot': [5, 25, 50],  # Early/mid/late
    'num_samples': 3,  # Sample images per epoch
    'alpha': 0.5,  # Overlay transparency
    'colormap': 'jet'
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | plot_temporal_ratio | Line plot R_temporal vs epoch (MANDATORY) |
| C-5-2 | plot_gradcam_heatmaps | GradCAM evolution at 3 epochs |

---

## Complete Config Module

```python
# h-e3/code/config.py
import torch

# Inherited from h-e1 (import these)
# from h-e1.code.data import DatasetConfig
# from h-e1.code.train import DATASET_CONFIGS

# GradCAM configuration
GRADCAM_CONFIG = {
    'target_layer': 'layer4',
    'max_batches_per_epoch': 100,
    'epsilon': 1e-8,
    'device': 'cuda' if torch.cuda.is_available() else 'cpu'
}

# Region masking
REGION_CONFIG = {
    'spurious_method': 'background',
    'core_method': 'bbox_fallback',
    'mask_shape': (224, 224),
    'bbox_default': [56, 56, 168, 168]
}

# Experiment (PoC: single seed Waterbirds)
EXPERIMENT_CONFIG = {
    'dataset': 'Waterbirds',
    'lr': 0.001,
    'batch_size': 128,
    'max_epochs': 50,
    'weight_decay': 1e-4,
    'seed': 0,
    'tracking_interval': 5,
    'model': 'resnet50',
    'pretrained': True
}

# Training schedule
SCHEDULER_CONFIG = {
    'type': 'step',
    'step_epochs': [30],
    'gamma': 0.1
}

# Optimizer
OPTIMIZER_CONFIG = {
    'type': 'sgd',
    'momentum': 0.9,
    'weight_decay': 1e-4
}

# PoC validation
POC_GATE = {
    'delta_threshold': 0.1,
    'direction_check': 'decreasing',
    'min_worst_group_acc': 0.7
}

# Output paths
OUTPUT_CONFIG = {
    'results_dir': './h-e3/results',
    'figures_dir': './h-e3/figures',
    'temporal_csv': 'temporal_ratios.csv',
    'validation_report': '../04_validation.md'
}

# Plotting
PLOT_CONFIG = {
    'backend': 'Agg',
    'dpi': 150,
    'figsize': (10, 6),
    'color_primary': '#3498DB',
    'marker_style': 'o-',
    'grid': True
}

# Heatmap visualization
HEATMAP_CONFIG = {
    'epochs_to_plot': [5, 25, 50],
    'num_samples': 3,
    'alpha': 0.5,
    'colormap': 'jet'
}
```

---

## Validation Checklist

- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Subtask count within budget (all tasks: 2/2)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] EXISTENCE rules: Single fixed config, no variations
- [x] Inherited Configuration section with verified field names
- [x] Field names match actual h-e1 code (DatasetConfig, TrainConfig)
- [x] Ready-to-copy-paste code blocks
