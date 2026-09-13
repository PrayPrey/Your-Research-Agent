# Configuration Specification: h-m2 Minority-Gradient Alignment Analysis

**Hypothesis ID:** h-m2  
**Type:** MECHANISM (Step 2 of 4)  
**Infrastructure:** STANDARD (Hardcoded dict for PoC)  
**Date:** 2026-04-24  
**Configuration Agent:** Autonomous  
**Prerequisites:** h-m1 (COMPLETED ✅)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m1)  
**Status**: h-m1 config verified - using YAML + dataclass pattern  
**Config Pattern**: h-m2 uses hardcoded dict (STANDARD tier, simpler than h-m1 FULL tier)  
**Analysis**: h-m2 is analysis-only (no training), requires minimal config complexity

---

## Applied Patterns

Applied: Hardcoded Dict Pattern (STANDARD tier)  
Applied: Incremental Hypothesis Config (inherit from h-m1)  
Applied: Path-based Artifact Loading

---

## Configuration Schema (Hardcoded Dict)

**Format**: Single Python dict for copy-paste into experiment script.

### config.py

```python
"""
h-m2 Configuration
Analysis-only hypothesis - no training required
Extends h-m1 outlier eigenvectors for gradient alignment analysis
"""

CONFIG = {
    # Project metadata
    'project': {
        'hypothesis_id': 'h-m2',
        'hypothesis_type': 'MECHANISM',
        'tier': 'STANDARD',
        'base_hypothesis': 'h-m1',
    },
    
    # Paths to h-m1 artifacts and h-e1 dependencies
    'paths': {
        'h_m1_results': '../h-m1/results',
        'h_m1_outlier_eigenvectors': '../h-m1/results/outlier_eigenvectors_erm.npy',
        'h_m1_eigenvalues': '../h-m1/results/erm_eigenvalues.npy',
        'h_e1_checkpoint': '../h-e1/code/checkpoints/erm_best.pth',
        'h_e1_data': '../h-e1/code/data/waterbirds/',
        'results_dir': './results/',
        'figures_dir': './figures/',
    },
    
    # Reproducibility (inherited from h-m1)
    'seed': 42,
    
    # Dataset configuration
    'dataset': {
        'batch_size': 128,
        'num_workers': 4,
        'minority_group_ids': [1, 3],  # landbirds on water, waterbirds on land
        'majority_group_ids': [0, 2],  # landbirds on land, waterbirds on water
    },
    
    # Gradient computation
    'gradient': {
        'device': 'cuda',
        'loss_reduction': 'sum',  # Sum over batch, then average over groups
        'normalize_gradients': False,  # Use raw gradients (not normalized)
    },
    
    # Alignment analysis
    'alignment': {
        'projection_method': 'memory_efficient',  # V @ (V^T @ g) instead of materializing P
        'validate_range': True,  # Assert alignment in [0, 1]
        'expected_outlier_count': 23,  # From h-m1 validation
    },
    
    # Visualization
    'visualization': {
        'dpi': 300,
        'format': 'png',
        'colors': {
            'minority': 'darkred',
            'majority': 'darkblue',
            'group_0': 'blue',
            'group_1': 'red',
            'group_2': 'blue',
            'group_3': 'red',
        },
        'alpha': 0.7,
        'figures': {
            'alignment_comparison': 'fig1_alignment_comparison.png',  # GATE METRIC
            'per_group_alignments': 'fig2_per_group_alignments.png',
            'projection_magnitude': 'fig3_projection_magnitude.png',
        },
    },
    
    # Logging
    'logging': {
        'level': 'INFO',
        'csv_outputs': {
            'alignment_metrics': 'alignment_metrics.csv',
            'per_group_alignments': 'per_group_alignments.csv',
        },
        'json_output': 'comparison_results.json',
    },
}
```

---

## Inherited Configuration (from h-m1)

### Values Verified from h-m1 Config Specs

The following configs are inherited from h-m1 (verified from `../h-m1/03_config.md`):

| Parameter | h-m1 Value | h-m2 Value | Rationale |
|-----------|------------|------------|-----------|
| seed | 42 | 42 | Same seed for reproducibility |
| batch_size | 128 | 128 | Same batch size for gradient computation |
| expected_outlier_count | 23 | 23 | h-m1 validated 23 outliers above bulk edge |
| device | cuda | cuda | Single GPU execution |

**Note**: h-m1 specs indicate YAML + dataclass, but h-m2 uses simpler hardcoded dict (STANDARD tier vs FULL tier).

---

## Task Configuration Breakdown

### B-1: Environment Setup (Complexity: 5, Budget: 1 subtask)

**Configuration**:
```python
SETUP_CONFIG = {
    'verify_paths': [
        '../h-m1/results/outlier_eigenvectors_erm.npy',
        '../h-m1/results/erm_eigenvalues.npy',
        '../h-e1/code/checkpoints/erm_best.pth',
        '../h-e1/code/data/waterbirds/',
    ],
    'create_dirs': ['./results/', './figures/'],
}
```

**Subtasks [1/1 used]**:
| ID | Subtask | Description |
|----|---------|-------------|
| B-1-1 | Verify all paths and create output directories | Check h-m1 artifacts exist, setup h-m2 dirs |

---

### B-2: Artifact Loading (Complexity: 8, Budget: 1 subtask)

**Configuration**:
```python
ARTIFACT_CONFIG = {
    'outlier_eigenvectors_path': '../h-m1/results/outlier_eigenvectors_erm.npy',
    'expected_shape': (None, 23),  # (num_params, 23 outliers)
    'validate_orthonormal': True,  # Verify V^T @ V = I
}
```

**Subtasks [1/1 used]**:
| ID | Subtask | Description |
|----|---------|-------------|
| B-2-1 | Load and validate h-m1 outlier eigenvectors | Implement artifact_loader.py with validation |

---

### B-3: Group Data Loading (Complexity: 10, Budget: 1 subtask)

**Configuration**:
```python
GROUP_DATA_CONFIG = {
    'dataset_path': '../h-e1/code/data/waterbirds/',
    'batch_size': 128,
    'num_workers': 4,
    'minority_group_ids': [1, 3],
    'majority_group_ids': [0, 2],
    'expected_minority_count': 240,  # Approximate
    'expected_majority_count': 4555,  # Approximate
}
```

**Subtasks [1/1 used]**:
| ID | Subtask | Description |
|----|---------|-------------|
| B-3-1 | Implement group-aware DataLoaders | Create minority/majority loaders with group filtering |

---

### B-4: Gradient Computation (Complexity: 11, Budget: 1 subtask)

**Configuration**:
```python
GRADIENT_CONFIG = {
    'device': 'cuda',
    'loss_fn': 'cross_entropy',
    'loss_reduction': 'sum',
    'flatten_method': 'concat',  # Concatenate all param.grad.flatten()
    'normalize_gradients': False,
}
```

**Subtasks [1/1 used]**:
| ID | Subtask | Description |
|----|---------|-------------|
| B-4-1 | Implement gradient computation for minority and majority groups | compute_group_gradient() function |

---

### B-5: Alignment Analysis (Complexity: 13, Budget: 1 subtask)

**Configuration**:
```python
ALIGNMENT_CONFIG = {
    'projection_method': 'memory_efficient',  # V @ (V^T @ g)
    'validate_range': True,  # Assert 0 <= alignment <= 1
    'epsilon': 1e-10,  # For numerical stability in division
    'compute_delta': True,  # delta_align = A_minority - A_majority
}
```

**Subtasks [1/1 used]**:
| ID | Subtask | Description |
|----|---------|-------------|
| B-5-1 | Implement alignment metric computation and comparison | compute_alignment() and compare_alignments() |

---

### B-6: Per-Group Analysis (Complexity: 9, Budget: 1 subtask)

**Configuration**:
```python
PER_GROUP_CONFIG = {
    'num_groups': 4,
    'group_ids': [0, 1, 2, 3],
    'group_names': [
        'landbirds_on_land',
        'landbirds_on_water',
        'waterbirds_on_water',
        'waterbirds_on_land',
    ],
    'minority_indices': [1, 3],
    'majority_indices': [0, 2],
}
```

**Subtasks [1/1 used]**:
| ID | Subtask | Description |
|----|---------|-------------|
| B-6-1 | Compute alignment for all 4 Waterbirds groups | Per-group gradient computation and alignment |

---

### B-7: Visualization (Complexity: 10, Budget: 1 subtask)

**Configuration**:
```python
VIS_CONFIG = {
    'dpi': 300,
    'format': 'png',
    'figures': {
        'alignment_comparison': {
            'filename': 'fig1_alignment_comparison.png',
            'type': 'bar',
            'title': 'Minority vs Majority Gradient Alignment to Outlier Subspace',
            'colors': ['darkred', 'darkblue'],
            'labels': ['Minority\nGradient', 'Majority\nGradient'],
        },
        'per_group_alignments': {
            'filename': 'fig2_per_group_alignments.png',
            'type': 'bar',
            'title': 'Per-Group Gradient Alignment to Outlier Subspace',
            'colors': ['blue', 'red', 'blue', 'red'],
        },
        'projection_magnitude': {
            'filename': 'fig3_projection_magnitude.png',
            'type': 'bar',
            'title': 'Projection Magnitude Comparison',
        },
    },
}
```

**Subtasks [1/1 used]**:
| ID | Subtask | Description |
|----|---------|-------------|
| B-7-1 | Generate all 3 alignment visualization figures | Implement visualize_alignment.py module |

---

### B-8: Integration Testing (Complexity: 9, Budget: 1 subtask)

**Configuration**:
```python
INTEGRATION_CONFIG = {
    'run_full_pipeline': True,
    'validate_outputs': {
        'figures': ['fig1_alignment_comparison.png', 'fig2_per_group_alignments.png', 'fig3_projection_magnitude.png'],
        'results': ['alignment_metrics.csv', 'per_group_alignments.csv', 'comparison_results.json'],
    },
    'gate_metric': {
        'check': 'A_minority > A_majority',
        'expected_delta': 0.0,  # Any positive delta confirms mechanism
    },
}
```

**Subtasks [1/1 used]**:
| ID | Subtask | Description |
|----|---------|-------------|
| B-8-1 | Run full pipeline and validate gate metric | End-to-end execution and validation |

---

## Configuration Usage Example

```python
# run_h_m2_experiment.py

import torch
import numpy as np
import random
from pathlib import Path
from config import CONFIG

def setup_environment(config):
    """Setup experiment environment"""
    # Set random seed
    seed = config['seed']
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    
    # Create output directories
    Path(config['paths']['results_dir']).mkdir(parents=True, exist_ok=True)
    Path(config['paths']['figures_dir']).mkdir(parents=True, exist_ok=True)
    
    # Verify h-m1 artifacts exist
    outlier_path = Path(config['paths']['h_m1_outlier_eigenvectors'])
    assert outlier_path.exists(), f"h-m1 outliers not found: {outlier_path}"
    
    # Verify h-e1 checkpoint exists
    ckpt_path = Path(config['paths']['h_e1_checkpoint'])
    assert ckpt_path.exists(), f"h-e1 checkpoint not found: {ckpt_path}"
    
    print(f"Environment setup complete (seed={seed})")

def main():
    # Load configuration
    config = CONFIG
    
    # Setup environment
    setup_environment(config)
    
    # Load h-m1 outlier eigenvectors
    from artifact_loader import load_h_m1_outliers, verify_outlier_artifacts
    outlier_data = load_h_m1_outliers(config['paths']['h_m1_results'])
    verify_outlier_artifacts(outlier_data, expected_count=config['alignment']['expected_outlier_count'])
    
    # Load ERM model
    from models.model import get_resnet50
    model = get_resnet50(num_classes=2)
    checkpoint = torch.load(config['paths']['h_e1_checkpoint'])
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(config['gradient']['device'])
    model.eval()
    
    # Create group loaders
    from group_data import get_group_loaders
    group_loaders = get_group_loaders(
        config['paths']['h_e1_data'],
        batch_size=config['dataset']['batch_size'],
        minority_ids=config['dataset']['minority_group_ids'],
        majority_ids=config['dataset']['majority_group_ids']
    )
    
    # Compute gradients
    from gradient_computation import compute_group_gradient
    minority_gradient = compute_group_gradient(
        model, group_loaders['minority'], 
        device=config['gradient']['device']
    )
    majority_gradient = compute_group_gradient(
        model, group_loaders['majority'],
        device=config['gradient']['device']
    )
    
    # Compute alignment
    from alignment_analysis import compare_alignments
    comparison = compare_alignments(
        minority_gradient, majority_gradient,
        outlier_data['eigenvectors']
    )
    
    # Visualize
    from visualize_alignment import generate_all_figures
    generate_all_figures(
        comparison,
        figures_dir=config['paths']['figures_dir'],
        vis_config=config['visualization']
    )
    
    # Gate check
    print(f"\n=== GATE CHECK (SHOULD_WORK) ===")
    print(f"A_minority: {comparison['A_minority']:.4f}")
    print(f"A_majority: {comparison['A_majority']:.4f}")
    print(f"Delta: {comparison['delta_align']:.4f}")
    print(f"Mechanism Confirmed: {comparison['mechanism_confirmed']}")

if __name__ == '__main__':
    main()
```

---

## Hyperparameter Rationale

**Non-Standard Values Only**:

- **batch_size=128**: Inherited from h-m1/h-e1. Standard for ResNet-50 on single GPU. Gradient computation doesn't require small batches like Hessian computation (no memory-intensive Hessian-vector products).

- **loss_reduction='sum'**: Sum over batch samples, then average across groups. This ensures equal weighting of minority/majority groups despite size imbalance (240 vs 4555 samples).

- **projection_method='memory_efficient'**: Avoid materializing full (num_params × num_params) projection matrix P. Instead compute P @ g = V @ (V^T @ g) on-the-fly. For ResNet-50 with ~25M parameters, full P would require ~2.5TB memory.

- **expected_outlier_count=23**: From h-m1 validation (eigenvalues above bulk edge λ+ = 2.456). This is a validation checkpoint, not a tunable parameter.

---

## File Output Structure

```
h-m2/
├── code/
│   ├── config.py                          # CONFIG dict
│   ├── artifact_loader.py                 # Load h-m1 outliers
│   ├── group_data.py                      # Group DataLoaders
│   ├── gradient_computation.py            # Gradient computation
│   ├── alignment_analysis.py              # Alignment metrics
│   ├── visualize_alignment.py             # Visualizations
│   └── run_h_m2_experiment.py             # Main script
├── results/
│   ├── alignment_metrics.csv
│   ├── per_group_alignments.csv
│   └── comparison_results.json
└── figures/
    ├── fig1_alignment_comparison.png      (GATE METRIC)
    ├── fig2_per_group_alignments.png
    └── fig3_projection_magnitude.png
```

---

## Configuration Validation

```python
def validate_config(config):
    """Validate configuration before experiment"""
    
    # Verify paths
    assert Path(config['paths']['h_m1_outlier_eigenvectors']).exists(), \
        "h-m1 outlier eigenvectors not found"
    assert Path(config['paths']['h_e1_checkpoint']).exists(), \
        "h-e1 ERM checkpoint not found"
    
    # Verify alignment config
    assert config['alignment']['expected_outlier_count'] == 23, \
        "Expected 23 outliers from h-m1 validation"
    assert config['alignment']['projection_method'] == 'memory_efficient', \
        "Must use memory-efficient projection for large models"
    
    # Verify group IDs
    assert config['dataset']['minority_group_ids'] == [1, 3], \
        "Minority groups: landbirds on water (1), waterbirds on land (3)"
    assert config['dataset']['majority_group_ids'] == [0, 2], \
        "Majority groups: landbirds on land (0), waterbirds on water (2)"
    
    # Verify reproducibility
    assert config['seed'] == 42, \
        "Must match h-m1 seed for reproducibility"
    
    print("✓ Configuration validation passed")
```

---

## Self-Validation Checklist

- [x] Hardcoded dict format (STANDARD tier)
- [x] No ASCII diagrams
- [x] Rationale only for non-standard values
- [x] Codebase Analysis section included
- [x] Inherited configuration documented from h-m1 specs
- [x] Total length < 400 lines
- [x] Per-task configs with subtask breakdown
- [x] All 8 tasks covered with 1 subtask each (8/8 budget used)
- [x] Configuration usage example included

---

*Configuration designed for Phase 4 Implementation | h-m2 MECHANISM Hypothesis | Extends h-m1 outlier analysis | STANDARD tier infrastructure*
