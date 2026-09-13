# Configuration: h-m2 Architectural Comparison (CNN vs ViT)

**Hypothesis:** h-m2  
**Type:** MECHANISM (EXISTENCE PoC)  
**Date:** 2026-08-29  
**Author:** yoon303@ust.ac.kr  

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Extends h-e1 config - convergence detection and ablation setup reused  
**Config Files Found**: h-e1/code/config.py (verified)  
**Pattern Used**: Hardcoded dict (EXISTENCE PoC - single fixed config)

---

## Applied Patterns

Applied: EXISTENCE PoC config (no hyperparameter variations, single seed baseline, minimal epochs)

---

## Inherited Configuration (Base Hypothesis h-e1)

Reused from h-e1 (verified):

```python
# Convergence detection (from h-e1)
CONVERGENCE_CONFIG = {
    'threshold': 0.1,  # 10% of peak gradient norm
    'window': 3,  # consecutive epochs below threshold
    'min_epochs': 5
}

# Optimizer base
OPTIMIZER_CONFIG = {
    'type': 'sgd',
    'momentum': 0.9,
    'nesterov': False
}

# Data preprocessing (ImageNet normalization)
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]
```

---

## Architecture-Specific Configs

### ResNet-50 Config

```python
RESNET_CONFIG = {
    'model': 'resnet50',
    'lr': 0.001,  # kohpangwei/group_DRO default
    'batch_size': 256,
    'weight_decay': 1e-4,
    'lr_schedule': 'cosine'
}
```

### ViT-B/16 Config

```python
VIT_CONFIG = {
    'model': 'vit_base_patch16_224',
    'lr': 0.0003,  # timm default (3x lower than CNN)
    'batch_size': 512,  # ViT needs larger batches
    'weight_decay': 0.05,  # Higher for ViT
    'lr_schedule': 'cosine'
}
```

Rationale: Learning rate and batch size differences follow timm/kohpangwei defaults for fair architectural comparison.

---

## Dataset Config

```python
DATASET_CONFIG = {
    'primary': 'waterbirds',  # WILDS package
    'fallback': 'celebA',
    'image_size': 224,
    'num_workers': 4
}

# Waterbirds-specific
WATERBIRDS_CONFIG = {
    'source': 'wilds',
    'download': True,
    'splits': ['train', 'val', 'test'],
    'augmentation': {
        'random_flip': 0.5,
        'random_crop_padding': 4
    }
}

# CelebA fallback
CELEBA_CONFIG = {
    'source': 'wilds',  # or torchvision
    'target_attr': 'Blond_Hair',
    'spurious_attr': 'Male',
    'download': True
}
```

---

## Experiment Config

```python
EXPERIMENT_CONFIG = {
    'num_seeds': 10,
    'seed_start': 42,
    'epochs': 50,  # Sufficient for convergence detection
    'device': 'cuda' if torch.cuda.is_available() else 'cpu',
    'mixed_precision': False  # PoC: skip
}

REPRODUCIBILITY_CONFIG = {
    'torch_deterministic': True,
    'cudnn_benchmark': False,
    'cudnn_deterministic': True
}
```

---

## Gate Criterion

```python
GATE_CONFIG = {
    'statistical_test': 'independent_ttest',  # Test 7
    'alpha': 0.05,
    'min_delta_diff': 2,  # (Δ_ResNet - Δ_ViT) ≥ 2 epochs
    'alternative': 'greater'  # Δ_ResNet > Δ_ViT
}
```

---

## Output Config

```python
OUTPUT_CONFIG = {
    'results_dir': './h-m2/results',
    'figures_dir': './h-m2/figures',
    'convergence_csv': 'architecture_convergence.csv',
    'comparison_plot': 'resnet_vs_vit_comparison.png',  # MANDATORY
    'stats_json': 'stats_summary.json'
}

PLOT_CONFIG = {
    'backend': 'Agg',
    'dpi': 150,
    'figsize': (10, 6),
    'color_resnet': '#E74C3C',
    'color_vit': '#3498DB'
}
```

---

## Complete Config Module

```python
# h-m2/code/config.py
import torch

# Architecture configs
RESNET_CONFIG = {
    'model': 'resnet50',
    'lr': 0.001,
    'batch_size': 256,
    'weight_decay': 1e-4,
    'lr_schedule': 'cosine'
}

VIT_CONFIG = {
    'model': 'vit_base_patch16_224',
    'lr': 0.0003,
    'batch_size': 512,
    'weight_decay': 0.05,
    'lr_schedule': 'cosine'
}

# Dataset config
DATASET_CONFIG = {
    'primary': 'waterbirds',
    'fallback': 'celebA',
    'image_size': 224,
    'num_workers': 4
}

WATERBIRDS_CONFIG = {
    'source': 'wilds',
    'download': True,
    'splits': ['train', 'val', 'test'],
    'augmentation': {
        'random_flip': 0.5,
        'random_crop_padding': 4
    }
}

CELEBA_CONFIG = {
    'source': 'wilds',
    'target_attr': 'Blond_Hair',
    'spurious_attr': 'Male',
    'download': True
}

# Inherited from h-e1
CONVERGENCE_CONFIG = {
    'threshold': 0.1,
    'window': 3,
    'min_epochs': 5
}

OPTIMIZER_CONFIG = {
    'type': 'sgd',
    'momentum': 0.9,
    'nesterov': False
}

IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Experiment execution
EXPERIMENT_CONFIG = {
    'num_seeds': 10,
    'seed_start': 42,
    'epochs': 50,
    'device': 'cuda' if torch.cuda.is_available() else 'cpu',
    'mixed_precision': False
}

REPRODUCIBILITY_CONFIG = {
    'torch_deterministic': True,
    'cudnn_benchmark': False,
    'cudnn_deterministic': True
}

# Gate criterion
GATE_CONFIG = {
    'statistical_test': 'independent_ttest',
    'alpha': 0.05,
    'min_delta_diff': 2,
    'alternative': 'greater'
}

# Output paths
OUTPUT_CONFIG = {
    'results_dir': './h-m2/results',
    'figures_dir': './h-m2/figures',
    'convergence_csv': 'architecture_convergence.csv',
    'comparison_plot': 'resnet_vs_vit_comparison.png',
    'stats_json': 'stats_summary.json'
}

PLOT_CONFIG = {
    'backend': 'Agg',
    'dpi': 150,
    'figsize': (10, 6),
    'color_resnet': '#E74C3C',
    'color_vit': '#3498DB'
}
```

---

## Validation Checklist

- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] No KB search logs
- [x] EXISTENCE rules: Single fixed config, no variations
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Inherited config verified from h-e1 actual code
- [x] Architecture-specific hyperparameters from experiment brief sources
- [x] Ready-to-copy-paste code blocks
