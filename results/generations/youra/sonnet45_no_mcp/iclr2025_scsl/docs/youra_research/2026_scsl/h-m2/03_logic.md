# Logic Design: h-m2 Minority-Gradient Alignment Analysis

**Hypothesis ID:** h-m2  
**Type:** MECHANISM (Step 2 of 4)  
**Budget:** 5 subtasks (Standard-tier MECHANISM PoC)  
**Date:** 2026-04-24  
**Designer:** Logic Agent  
**Prerequisites:** h-m1 (COMPLETED ✅)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m1)  
**Status**: API signatures verified from h-m1 actual code  
**Analyzed Path**: `../h-m1/code/`  
**Relevant Symbols from h-m1:**
- `h_m1.code.outlier_analysis.identify_outliers(eigenvalues, bulk_edge) -> Dict[str, Any]`
- `h_m1.code.config.load_config(config_path) -> H_M1_Config`

**Note**: h-m2 loads h-m1 **result artifacts** (NumPy arrays), not code modules.

---

## Knowledge Base Patterns Applied

Applied: Incremental Hypothesis Pattern (reuse h-m1 artifacts)  
Applied: Gradient Projection Pattern  
Applied: Group-Aware Data Loading Pattern

---

## External Dependencies API (from h-m1)

### Artifact Files (Direct NumPy Load)

```python
# From: ../h-m1/code/results/ (artifacts, not code imports)

# Load outlier eigenvectors (NumPy array)
outlier_eigenvectors = np.load('../h-m1/code/results/outlier_eigenvectors_erm.npy')
# Expected shape: (num_params, K) where K = 23 outliers from h-m1

# Load ERM eigenvalues (optional, for validation)
erm_eigenvalues = np.load('../h-m1/code/results/erm_eigenvalues.npy')
# Expected shape: (100,)
```

**Verified from**: h-m1 results structure (artifacts saved by h-m1 experiment)

---

## B-2: Artifact Loader Module [Complexity: 8, Budget: 2 subtasks]

**Applied**: Artifact Loading Pattern

### API Signatures

```python
# File: artifact_loader.py

import numpy as np
from pathlib import Path
from typing import Dict

def load_h_m1_outliers(h_m1_results_dir: str = '../h-m1/code/results') -> Dict[str, np.ndarray]:
    """
    Load outlier eigenvectors from h-m1
    
    Args:
        h_m1_results_dir: Path to h-m1 results directory
    
    Returns:
        outlier_data: dict with keys:
            - 'eigenvectors': (num_params, K) outlier eigenvectors
            - 'eigenvalues': (100,) full eigenspectrum
            - 'num_outliers': int (K)
    """
    ...

def verify_outlier_artifacts(outlier_data: Dict) -> bool:
    """
    Verify loaded artifacts match h-m1 validation
    
    Args:
        outlier_data: Data from load_h_m1_outliers()
    
    Returns:
        valid: bool - True if artifacts pass validation
    
    Checks:
        - num_outliers == 23 (from h-m1)
        - eigenvectors shape[1] == 23
        - No NaN/Inf values
    """
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Load Artifacts | Load .npy files, verify paths exist |
| L-2-2 | Validate Artifacts | Verify shape (num_params, 23), check integrity |

---

## B-3: Group Data Loader Module [Complexity: 10, Budget: 2 subtasks]

**Applied**: Group-Aware Data Loading Pattern

### API Signatures

```python
# File: group_data.py

import torch
from torch.utils.data import DataLoader, Subset
from typing import Dict

def get_group_loaders(dataset, batch_size: int = 128) -> Dict[str, DataLoader]:
    """
    Create minority and majority group DataLoaders
    
    Args:
        dataset: Waterbirds dataset with metadata (from h-e1/h-m1)
        batch_size: Batch size for DataLoaders
    
    Returns:
        loaders: dict with keys:
            - 'minority': Combined minority groups [1, 3]
            - 'majority': Combined majority groups [0, 2]
            - 'minority_count': int (~240 samples)
            - 'majority_count': int (~4,555 samples)
    """
    ...

def get_per_group_loaders(dataset, batch_size: int = 128) -> Dict[int, DataLoader]:
    """
    Create DataLoaders for all 4 Waterbirds groups individually
    
    Returns:
        loaders: dict mapping group_id (0-3) to DataLoader
            0: landbirds on land (majority)
            1: landbirds on water (minority)
            2: waterbirds on water (majority)
            3: waterbirds on land (minority)
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| images | [B, 3, 224, 224] | Batch of images |
| labels | [B] | Class labels (0=landbird, 1=waterbird) |
| groups | [B] | Group IDs (0-3) |
| minority_indices | [~240] | Indices for groups 1, 3 |
| majority_indices | [~4555] | Indices for groups 0, 2 |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Minority/Majority Split | Parse metadata, create minority/majority loaders |
| L-3-2 | Per-Group Split | Create 4 individual group loaders |

---

## B-4: Gradient Computation Module [Complexity: 11, Budget: 1 subtask]

**Applied**: PyTorch Gradient Computation Pattern

### API Signatures

```python
# File: gradient_computation.py

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
import numpy as np

def compute_group_gradient(
    model: nn.Module, 
    group_loader: DataLoader, 
    device: str = 'cuda'
) -> np.ndarray:
    """
    Compute gradient vector for specific group
    
    Args:
        model: Trained ResNet-50 model (from h-e1 checkpoint)
        group_loader: DataLoader for specific group
        device: Device for computation
    
    Returns:
        gradient_flat: (num_params,) flattened gradient vector (NumPy)
    
    Algorithm:
        1. model.eval() - disable dropout/batchnorm updates
        2. Accumulate loss over all batches: loss = sum(CE(outputs, targets))
        3. Average: avg_loss = total_loss / num_batches
        4. Backprop: avg_loss.backward()
        5. Flatten: gradient = cat([p.grad.flatten() for p in model.parameters()])
    """
    ...

def flatten_gradients(model: nn.Module) -> torch.Tensor:
    """
    Flatten all parameter gradients into single vector
    
    Returns:
        gradient: (num_params,) flattened gradient tensor
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| outputs | [B, 2] | Model predictions per batch |
| loss | scalar | Cross-entropy loss (accumulated) |
| p.grad | varies | Per-parameter gradients |
| gradient_flat | [num_params] | ~23M for ResNet-50 |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Gradient Computation | Accumulate loss, backprop, flatten gradients |

---

## B-5: Alignment Analysis Module [Complexity: 13, Budget: 0 subtasks]

**Applied**: Projection Analysis Pattern (included in main flow - no separate allocation)

### API Signatures

```python
# File: alignment_analysis.py

import numpy as np
from typing import Dict, Any

def compute_alignment(
    gradient: np.ndarray, 
    outlier_eigenvectors: np.ndarray
) -> float:
    """
    Compute A(w) = ||P @ g||² / ||g||² via on-the-fly projection
    
    Args:
        gradient: (num_params,) gradient vector
        outlier_eigenvectors: (num_params, 23) eigenvectors from h-m1
    
    Returns:
        alignment: float in [0, 1]
    
    Algorithm (memory-efficient):
        1. V = outlier_eigenvectors  # (num_params, 23)
        2. VT_g = V.T @ gradient  # (23,) - project onto subspace
        3. projected = V @ VT_g  # (num_params,) - reconstruct P @ g
        4. alignment = ||projected||² / ||gradient||²
    """
    ...

def compare_alignments(
    minority_gradient: np.ndarray,
    majority_gradient: np.ndarray,
    outlier_eigenvectors: np.ndarray
) -> Dict[str, Any]:
    """
    Compare minority vs majority gradient alignment (GATE METRIC)
    
    Returns:
        comparison: dict with:
            - A_minority: float
            - A_majority: float
            - delta_align: float (minority - majority)
            - mechanism_confirmed: bool (delta_align > 0)
            - percentage_difference: float
    """
    ...

def compute_per_group_alignments(
    gradients: Dict[int, np.ndarray],
    outlier_eigenvectors: np.ndarray
) -> Dict[int, float]:
    """
    Compute alignment for all 4 Waterbirds groups
    
    Returns:
        group_alignments: dict mapping group_id to alignment value
    """
    ...
```

---

## Supporting Module APIs (Included in Main Script)

### Visualization Module (visualize_alignment.py)

```python
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict

def plot_alignment_comparison(comparison: Dict, save_path: str):
    """Bar chart: A_minority vs A_majority (GATE METRIC)"""
    ...

def plot_per_group_alignments(group_alignments: Dict[int, float], save_path: str):
    """Bar chart: Alignment for all 4 Waterbirds groups"""
    ...

def generate_all_figures(
    comparison: Dict, 
    group_alignments: Dict, 
    figures_dir: str
):
    """Generate all required figures"""
    ...
```

### Main Experiment Script (run_h_m2_experiment.py)

```python
from artifact_loader import load_h_m1_outliers, verify_outlier_artifacts
from group_data import get_group_loaders, get_per_group_loaders
from gradient_computation import compute_group_gradient
from alignment_analysis import (compute_alignment, compare_alignments, 
                                compute_per_group_alignments)
from visualize_alignment import generate_all_figures
import torch
import sys
import json
import csv
from pathlib import Path

def main():
    """
    Main execution flow for h-m2 experiment
    
    Steps:
    1. Load h-m1 outlier eigenvectors (artifacts)
    2. Load Waterbirds dataset (reuse h-e1 data module)
    3. Create group-specific loaders (minority/majority)
    4. Load ERM model from h-e1 checkpoint
    5. Compute minority gradient
    6. Compute majority gradient
    7. Compute alignments and compare (GATE METRIC)
    8. Per-group analysis (all 4 groups)
    9. Generate visualizations
    10. Save results
    11. Report gate check
    """
    
    # Setup
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # 1. Load h-m1 outlier eigenvectors
    outlier_data = load_h_m1_outliers('../h-m1/code/results')
    verify_outlier_artifacts(outlier_data)
    
    # 2. Load Waterbirds dataset (import from h-e1)
    sys.path.insert(0, str(Path('../h-e1/code')))
    from data.dataset import get_dataloaders
    loaders = get_dataloaders(data_dir='../h-e1/code/data/waterbirds/', batch_size=128)
    
    # 3. Create group-specific loaders
    group_loaders = get_group_loaders(loaders['train'].dataset)
    
    # 4. Load ERM model from h-e1 checkpoint
    from models.model import get_resnet50
    model = get_resnet50(num_classes=2)
    checkpoint = torch.load('../h-e1/code/checkpoints/erm_best.pth')
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    # 5-6. Compute gradients
    minority_gradient = compute_group_gradient(model, group_loaders['minority'], device)
    majority_gradient = compute_group_gradient(model, group_loaders['majority'], device)
    
    # 7. Compare alignments (GATE METRIC)
    comparison = compare_alignments(
        minority_gradient, 
        majority_gradient, 
        outlier_data['eigenvectors']
    )
    
    # 8. Per-group analysis
    per_group_loaders = get_per_group_loaders(loaders['train'].dataset)
    per_group_gradients = {
        gid: compute_group_gradient(model, loader, device) 
        for gid, loader in per_group_loaders.items()
    }
    group_alignments = compute_per_group_alignments(
        per_group_gradients, 
        outlier_data['eigenvectors']
    )
    
    # 9. Visualize
    generate_all_figures(comparison, group_alignments, figures_dir='./code/figures/')
    
    # 10. Save results
    save_alignment_metrics(comparison, group_alignments, results_dir='./code/results/')
    
    # 11. Gate check
    print("="*60)
    print("GATE CHECK (SHOULD_WORK)")
    print("="*60)
    print(f"Metric: A_minority > A_majority")
    print(f"A_minority: {comparison['A_minority']:.4f}")
    print(f"A_majority: {comparison['A_majority']:.4f}")
    print(f"Delta: {comparison['delta_align']:.4f}")
    print(f"Mechanism Confirmed: {comparison['mechanism_confirmed']}")
    print(f"Result: {'PASS' if comparison['mechanism_confirmed'] else 'FAIL'}")
    print("="*60)
    
    return 0 if comparison['mechanism_confirmed'] else 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
```

### Configuration Module (config.py)

```python
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class PathsConfig:
    """File paths configuration"""
    h_m1_results: str = '../h-m1/code/results'
    h_e1_checkpoints: str = '../h-e1/code/checkpoints'
    h_e1_data: str = '../h-e1/code/data/waterbirds'
    results_dir: str = './code/results/'
    figures_dir: str = './code/figures/'

@dataclass
class AlignmentConfig:
    """Alignment computation configuration"""
    projection_method: str = 'memory_efficient'  # V @ (V^T @ g)
    normalize_gradients: bool = False
    validate_range: bool = True  # Assert alignment in [0, 1]

@dataclass
class GroupConfig:
    """Group configuration"""
    minority_ids: list = field(default_factory=lambda: [1, 3])
    majority_ids: list = field(default_factory=lambda: [0, 2])
    batch_size: int = 128

@dataclass
class H_M2_Config:
    """Complete h-m2 configuration"""
    paths: PathsConfig = field(default_factory=PathsConfig)
    alignment: AlignmentConfig = field(default_factory=AlignmentConfig)
    groups: GroupConfig = field(default_factory=GroupConfig)
```

---

## Self-Validation Checklist

- [x] Codebase Analysis section included
- [x] External Dependencies API section with h-m1 artifacts
- [x] API signatures with type hints
- [x] Tensor shapes documented
- [x] Subtask count within budget (5/5 used: 2+2+1+0+0)
- [x] Total length < 600 lines
- [x] No ASCII diagrams
- [x] Main experiment flow included
- [x] "Applied: {pattern}" lines for KB patterns

---

*Logic designed for Phase 4 Implementation | h-m2 MECHANISM Hypothesis | Extends h-m1 artifacts | 5 subtasks allocated*
