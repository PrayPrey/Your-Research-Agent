# Configuration Specification: h-e1 Curvature Subspace Alignment

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Infrastructure:** LIGHT (hardcoded configs, argparse)  
**Date:** 2026-04-24  
**Configuration Agent:** Autonomous

---

## Codebase Analysis (Serena)

**Project Type**: Green-field  
**Status**: FOUNDATION hypothesis - designing new config schema  
**Config Files Found**: None - new config  
**Pattern Used**: Hardcoded dict (LIGHT tier)

---

## Applied Patterns

Applied: Minimal PoC Pattern (EXISTENCE hypothesis)  
Applied: PyTorch Standard Hyperparameters

---

## Core Configuration (Hardcoded Dict)

**Format**: Single hardcoded dictionary for LIGHT tier infrastructure.

```python
# config.py
CONFIG = {
    # Reproducibility
    "seed": 42,
    
    # Dataset
    "data_dir": "./data/waterbird_complete95_forest2water2/",
    "batch_size": 128,
    "num_workers": 4,
    "num_classes": 2,
    "num_groups": 4,
    
    # Model
    "model_name": "resnet50",
    "pretrained": True,
    
    # Training - ERM
    "epochs": 100,
    "lr": 0.001,
    "momentum": 0.9,
    "weight_decay": 1e-4,
    "lr_milestones": [60, 80],
    "lr_gamma": 0.1,
    "patience": 10,
    
    # Training - Group-DRO (same hyperparameters as ERM)
    "dro_step_size": 0.01,  # Group weight adjustment rate
    
    # Hessian Analysis
    "num_eigenthings": 100,
    "power_iter_steps": 20,
    "hessian_batch_size": 32,
    
    # Marchenko-Pastur Fitting
    "mp_fit_range": (20, 80),  # Use middle eigenvalues for fitting
    
    # Paths
    "checkpoint_dir": "./checkpoints/",
    "results_dir": "./results/",
    "figures_dir": "./figures/",
    
    # Logging
    "log_interval": 10,  # Print every N batches
}
```

---

## A-6: Visualization Configuration (1 subtask)

**Applied**: Standard matplotlib defaults for research figures

### Visualization Settings

```python
VIZ_CONFIG = {
    # Figure settings
    "figsize_bar": (8, 6),
    "figsize_spectrum": (10, 6),
    "figsize_curves": (10, 6),
    "figsize_heatmap": (8, 6),
    "figsize_scatter": (8, 6),
    "dpi": 300,
    "format": "png",
    
    # Colors
    "color_erm": "red",
    "color_dro": "blue",
    "color_bulk_edge": "red",
    "alpha": 0.7,
    
    # Output paths (relative to figures_dir)
    "fig_alignment": "fig1_alignment_comparison.png",
    "fig_spectrum_erm": "fig2_hessian_spectrum_erm.png",
    "fig_spectrum_dro": "fig3_hessian_spectrum_dro.png",
    "fig_training": "fig4_training_curves.png",
    "fig_heatmap": "fig5_group_accuracy_heatmap.png",
}
```

### Subtasks (1/1 used)

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Figure Configuration | Define output paths and plot settings for 5 required figures |

**Rationale**: PoC requires 5 specific visualizations (alignment comparison, Hessian spectra, training curves, accuracy heatmap). Hardcoded paths ensure consistent output structure.

---

## A-7: Integration Testing Configuration (1 subtask)

**Applied**: PyTorch smoke test pattern (minimal data, 1 epoch)

### Smoke Test Settings

```python
SMOKE_TEST_CONFIG = {
    # Reduced dataset
    "smoke_num_samples": 100,  # Per split (train/val/test)
    "smoke_batch_size": 16,
    
    # Reduced training
    "smoke_epochs": 1,
    "smoke_num_eigenthings": 10,  # Instead of 100
    
    # Quick validation
    "smoke_timeout": 300,  # 5 minutes max
}
```

### Test Suite Structure

```python
# test_smoke.py
def run_smoke_tests():
    """Execute all smoke tests in sequence"""
    tests = [
        test_data_loading,
        test_model_forward,
        test_erm_training_one_epoch,
        test_dro_training_one_epoch,
        test_hessian_small,
        test_mp_fitting,
        test_alignment_computation,
        test_visualization_creation,
    ]
    
    for test in tests:
        print(f"Running: {test.__name__}")
        test()
        print(f"PASS: {test.__name__}")
```

### Subtasks (1/1 used)

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Smoke Test Config | Define reduced settings for fast validation (100 samples, 1 epoch, 10 eigenthings) |

**Rationale**: Smoke tests must complete quickly (<5 min) to validate pipeline without full training. 100 samples sufficient to test data flow, 1 epoch tests training loop, 10 eigenthings tests Hessian computation.

---

## Environment Variables (Optional)

```python
# Optional argparse overrides for flexibility
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--gpu', type=int, default=0, help='GPU ID')
    parser.add_argument('--data_dir', type=str, default=CONFIG['data_dir'])
    parser.add_argument('--seed', type=int, default=CONFIG['seed'])
    parser.add_argument('--epochs', type=int, default=CONFIG['epochs'])
    parser.add_argument('--smoke', action='store_true', help='Run smoke test')
    return parser.parse_args()
```

---

## Configuration Usage Example

```python
# run_experiment.py
import torch
import numpy as np
import random
from config import CONFIG, VIZ_CONFIG, SMOKE_TEST_CONFIG

def set_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True

def main():
    # Setup
    set_seed(CONFIG['seed'])
    
    # GPU selection (set via environment)
    # export CUDA_VISIBLE_DEVICES=1
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Load data
    dataloaders = get_dataloaders(
        CONFIG['data_dir'], 
        CONFIG['batch_size']
    )
    
    # Train models
    erm_model = train_erm(dataloaders, CONFIG, device)
    dro_model = train_dro(dataloaders, CONFIG, device)
    
    # Analyze
    results = analyze_and_visualize(
        erm_model, dro_model, dataloaders, 
        CONFIG, VIZ_CONFIG, device
    )
    
    # Save results
    save_results(results, CONFIG['results_dir'])

if __name__ == '__main__':
    main()
```

---

## Hyperparameter Rationale

**Non-Standard Values Only**:

- **lr_milestones=[60, 80]**: From Sagawa et al. 2020 Group-DRO paper, standard schedule for Waterbirds
- **num_eigenthings=100**: Sufficient to capture outlier subspace while avoiding OOM (ResNet-50 has ~25M parameters)
- **mp_fit_range=(20, 80)**: Exclude top outliers and bottom noise for stable bulk edge estimation
- **hessian_batch_size=32**: Smaller than training batch to reduce memory during Hessian computation

---

## File Output Structure

```
h-e1/
├── checkpoints/
│   ├── erm_best.pth
│   └── dro_best.pth
├── results/
│   ├── training_log_erm.csv
│   ├── training_log_dro.csv
│   ├── alignment_results.csv
│   └── hessian_stats.csv
└── figures/
    ├── fig1_alignment_comparison.png
    ├── fig2_hessian_spectrum_erm.png
    ├── fig3_hessian_spectrum_dro.png
    ├── fig4_training_curves.png
    └── fig5_group_accuracy_heatmap.png
```

---

## Self-Validation Checklist

- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values
- [x] Subtask count within budget (2/2 used)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] EXISTENCE PoC rules followed (single config, no variations)

---

*Configuration designed for Phase 4 Implementation | h-e1 EXISTENCE Hypothesis | 2 subtasks allocated*
