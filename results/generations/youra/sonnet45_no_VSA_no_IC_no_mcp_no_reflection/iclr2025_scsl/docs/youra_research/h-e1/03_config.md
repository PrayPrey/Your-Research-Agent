# Configuration: h-e1 Temporal Convergence Validation

**Hypothesis:** h-e1  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-08-28  
**Author:** yoon303@ust.ac.kr  

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation - no existing config to reuse  
**Config Pattern**: Hardcoded dict (minimal PoC)

---

## Applied Patterns

Applied: Hardcoded dict for EXISTENCE PoC (no variations needed)

---

## A-1: Data Infrastructure [Complexity: 11, Budget: 2 subtasks]

### Configuration

```python
# h-e1/code/config.py

DATASET_CONFIGS = {
    'CMNIST': {
        'lr': 0.001,
        'batch_size': 128,
        'max_epochs': 50,
        'weight_decay': 1e-4,
        'model': 'resnet18',
        'lr_schedule': 'cosine',
        'image_size': 224,
        'num_workers': 4
    },
    'Waterbirds': {
        'lr': 0.001,
        'batch_size': 64,
        'max_epochs': 100,
        'weight_decay': 1e-4,
        'model': 'resnet50',
        'lr_schedule': 'step',
        'step_epochs': [30, 60],
        'image_size': 224,
        'num_workers': 4
    },
    'CelebA': {
        'lr': 0.0001,
        'batch_size': 64,
        'max_epochs': 80,
        'weight_decay': 1e-4,
        'model': 'resnet50',
        'lr_schedule': 'cosine',
        'image_size': 224,
        'num_workers': 4
    },
    'NICO++': {
        'lr': 0.001,
        'batch_size': 64,
        'max_epochs': 100,
        'weight_decay': 1e-4,
        'model': 'resnet50',
        'lr_schedule': 'cosine',
        'image_size': 224,
        'num_workers': 4
    }
}

# Masking parameters
MASKING_CONFIG = {
    'CMNIST': {
        'spurious': {'method': 'gaussian_blur', 'kernel_size': 15},
        'core': {'method': 'grayscale'}
    },
    'Waterbirds': {
        'spurious': {'method': 'foreground_mask'},
        'core': {'method': 'background_mask'}
    },
    'CelebA': {
        'spurious': {'method': 'face_region_mask'},
        'core': {'method': 'gender_invariant'}
    },
    'NICO++': {
        'spurious': {'method': 'object_mask'},
        'core': {'method': 'context_mask'}
    }
}

# Data paths
DATA_ROOT = './data'
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Dataset loaders | 4 loaders + ImageNet normalization |
| C-1-2 | Masking functions | apply_spurious_mask, apply_core_mask per dataset |

---

## A-2: Baseline Model [Complexity: 6, Budget: 2 subtasks]

### Configuration

```python
# Model selection (uses DATASET_CONFIGS['model'] field)
MODEL_CONFIG = {
    'pretrained': True,
    'num_classes': 2,
    'freeze_backbone': False
}

# Optimizer
OPTIMIZER_CONFIG = {
    'type': 'sgd',
    'momentum': 0.9,
    'nesterov': False
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | get_baseline_model | Load ResNet-18/50, replace FC layer |
| C-2-2 | Model wrapper | Binary classification head integration |

---

## A-3: Ablation Trainer [Complexity: 13, Budget: 2 subtasks]

### Configuration

```python
# Convergence detection
CONVERGENCE_CONFIG = {
    'threshold': 0.1,  # 10% of peak gradient norm
    'window': 3,  # consecutive epochs below threshold
    'min_epochs': 5  # don't check convergence before this
}

# Training modes
ABLATION_MODES = ['spurious', 'core', 'baseline']

# Gradient tracking
GRADIENT_CONFIG = {
    'track_per_layer': False,  # PoC: only total norm
    'save_history': True
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | AblationTrainer class | train_variant, compute_gradient_norm |
| C-3-2 | Convergence detection | check_convergence using threshold+window |

---

## A-4: Multi-Seed Runner [Complexity: 8, Budget: 2 subtasks]

### Configuration

```python
# Experiment execution
EXPERIMENT_CONFIG = {
    'num_seeds': 10,
    'seed_start': 42,
    'device': 'cuda' if torch.cuda.is_available() else 'cpu',
    'mixed_precision': False  # PoC: skip for simplicity
}

# Reproducibility
REPRODUCIBILITY_CONFIG = {
    'torch_deterministic': True,
    'cudnn_benchmark': False,
    'cudnn_deterministic': True
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | run_single_experiment | Execute 3 variants for 1 seed |
| C-4-2 | run_all_seeds | Loop over 10 seeds, collect results |

---

## A-5: Statistical Eval [Complexity: 10, Budget: 2 subtasks]

### Configuration

```python
# Statistical testing
STATS_CONFIG = {
    'alpha': 0.05,  # significance level
    'test_type': 'paired',  # paired t-test
    'alternative': 'less'  # E_s < E_c
}

# PoC gate criteria
POC_GATE = {
    'min_seeds_correct': 6,  # >5/10 seeds
    'min_datasets_pass': 4,  # all 4 datasets
    'min_mean_delta': 2  # epochs
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | compute_temporal_gap | scipy.stats.ttest_rel on (E_s, E_c) |
| C-5-2 | check_poc_pass | Validate gate criteria |

---

## A-6: Visualization [Complexity: 7, Budget: 2 subtasks]

### Configuration

```python
# Plot settings
PLOT_CONFIG = {
    'backend': 'Agg',  # headless
    'dpi': 150,
    'figsize': (10, 6),
    'color_spurious': '#E74C3C',
    'color_core': '#3498DB',
    'color_baseline': '#95A5A6',
    'error_bar_style': 'std'  # ±1 std
}

# Output paths
OUTPUT_CONFIG = {
    'results_dir': './h-e1/results',
    'figures_dir': './h-e1/figures',
    'convergence_csv': 'convergence_data.csv',
    'stats_json': 'stats_summary.json',
    'comparison_plot': 'convergence_comparison.png'  # MANDATORY
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | plot_convergence_comparison | Bar chart mean(E_s) vs mean(E_c) |
| C-6-2 | save_results | CSV + JSON export |

---

## Complete Config Module

```python
# h-e1/code/config.py
import torch

# Dataset-specific training configs
DATASET_CONFIGS = {
    'CMNIST': {
        'lr': 0.001,
        'batch_size': 128,
        'max_epochs': 50,
        'weight_decay': 1e-4,
        'model': 'resnet18',
        'lr_schedule': 'cosine',
        'image_size': 224,
        'num_workers': 4
    },
    'Waterbirds': {
        'lr': 0.001,
        'batch_size': 64,
        'max_epochs': 100,
        'weight_decay': 1e-4,
        'model': 'resnet50',
        'lr_schedule': 'step',
        'step_epochs': [30, 60],
        'image_size': 224,
        'num_workers': 4
    },
    'CelebA': {
        'lr': 0.0001,
        'batch_size': 64,
        'max_epochs': 80,
        'weight_decay': 1e-4,
        'model': 'resnet50',
        'lr_schedule': 'cosine',
        'image_size': 224,
        'num_workers': 4
    },
    'NICO++': {
        'lr': 0.001,
        'batch_size': 64,
        'max_epochs': 100,
        'weight_decay': 1e-4,
        'model': 'resnet50',
        'lr_schedule': 'cosine',
        'image_size': 224,
        'num_workers': 4
    }
}

# Masking parameters
MASKING_CONFIG = {
    'CMNIST': {
        'spurious': {'method': 'gaussian_blur', 'kernel_size': 15},
        'core': {'method': 'grayscale'}
    },
    'Waterbirds': {
        'spurious': {'method': 'foreground_mask'},
        'core': {'method': 'background_mask'}
    },
    'CelebA': {
        'spurious': {'method': 'face_region_mask'},
        'core': {'method': 'gender_invariant'}
    },
    'NICO++': {
        'spurious': {'method': 'object_mask'},
        'core': {'method': 'context_mask'}
    }
}

# Data paths
DATA_ROOT = './data'
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Model config
MODEL_CONFIG = {
    'pretrained': True,
    'num_classes': 2,
    'freeze_backbone': False
}

# Optimizer
OPTIMIZER_CONFIG = {
    'type': 'sgd',
    'momentum': 0.9,
    'nesterov': False
}

# Convergence detection
CONVERGENCE_CONFIG = {
    'threshold': 0.1,
    'window': 3,
    'min_epochs': 5
}

# Ablation modes
ABLATION_MODES = ['spurious', 'core', 'baseline']

# Gradient tracking
GRADIENT_CONFIG = {
    'track_per_layer': False,
    'save_history': True
}

# Experiment execution
EXPERIMENT_CONFIG = {
    'num_seeds': 10,
    'seed_start': 42,
    'device': 'cuda' if torch.cuda.is_available() else 'cpu',
    'mixed_precision': False
}

# Reproducibility
REPRODUCIBILITY_CONFIG = {
    'torch_deterministic': True,
    'cudnn_benchmark': False,
    'cudnn_deterministic': True
}

# Statistical testing
STATS_CONFIG = {
    'alpha': 0.05,
    'test_type': 'paired',
    'alternative': 'less'
}

# PoC gate
POC_GATE = {
    'min_seeds_correct': 6,
    'min_datasets_pass': 4,
    'min_mean_delta': 2
}

# Plot settings
PLOT_CONFIG = {
    'backend': 'Agg',
    'dpi': 150,
    'figsize': (10, 6),
    'color_spurious': '#E74C3C',
    'color_core': '#3498DB',
    'color_baseline': '#95A5A6',
    'error_bar_style': 'std'
}

# Output paths
OUTPUT_CONFIG = {
    'results_dir': './h-e1/results',
    'figures_dir': './h-e1/figures',
    'convergence_csv': 'convergence_data.csv',
    'stats_json': 'stats_summary.json',
    'comparison_plot': 'convergence_comparison.png'
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
- [x] All defaults from PRD specifications
- [x] Ready-to-copy-paste code blocks
