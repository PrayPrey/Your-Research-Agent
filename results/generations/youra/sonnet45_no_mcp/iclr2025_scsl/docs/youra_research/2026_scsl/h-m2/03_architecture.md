# System Architecture: h-m2 Minority-Gradient Alignment Analysis

**Hypothesis ID:** h-m2  
**Type:** MECHANISM (Step 2 of 4)  
**Gate:** SHOULD_WORK  
**Date:** 2026-04-24  
**Architect:** Architecture Agent  
**Prerequisites:** h-m1 (COMPLETED ✅)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m1)  
**Status**: patterns found from base code  
**Analyzed Path**: `../h-m1/code/`  
**Findings**: h-m1 implements outlier identification and Hessian analysis. Reuse outlier eigenvectors, add gradient alignment computation.

---

## Knowledge Base Patterns Applied

Applied: Incremental Hypothesis Pattern (reuse h-m1 outliers)  
Applied: Gradient Projection Analysis Pattern  
Applied: Group-Aware Data Loading Pattern

---

## System Overview

**Purpose**: Validate that sharp curvature directions (h-m1 outlier subspace) align with minority-group gradient directions.

**Core Components**:
- h-m1 artifact loading (outlier eigenvectors)
- Group-aware data loading (minority/majority splits)
- Gradient computation (per group)
- Alignment analysis (projection onto outlier subspace)
- Comparison and visualization

**Infrastructure Tier**: STANDARD (8 tasks for MECHANISM PoC)

---

## External Dependencies (h-m1)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| Outlier Eigenvectors | Direct load: `../h-m1/results/outlier_eigenvectors_erm.npy` | h-m1 results artifact |
| ERM Eigenvalues | Direct load: `../h-m1/results/erm_eigenvalues.npy` | h-m1 results artifact |
| Config Pattern | `from h_m1.code.config import load_config` | `h-m1/code/config.py` |

**Verified from**: `h-m1/code/` actual implementation

**Note**: h-m2 loads h-m1 results artifacts (NumPy arrays), not code modules. No checkpoint loading needed.

---

## Module Structure

### 1. Artifact Loader Module (`artifact_loader.py`) [NEW]

**Dependencies**: NumPy

```python
import numpy as np
from pathlib import Path
from typing import Dict, Tuple

def load_h_m1_outliers(h_m1_results_dir: str = '../h-m1/results') -> Dict[str, np.ndarray]:
    """Load outlier eigenvectors and statistics from h-m1"""
    ...

def verify_outlier_artifacts(outlier_data: Dict) -> bool:
    """Verify loaded artifacts match h-m1 validation"""
    ...
```

---

### 2. Group Data Loader Module (`group_data.py`) [NEW]

**Dependencies**: PyTorch, h-e1 data module

```python
import torch
from torch.utils.data import DataLoader, Subset
from typing import Dict

def get_group_loaders(dataset, batch_size: int = 128) -> Dict[str, DataLoader]:
    """Create minority and majority group DataLoaders"""
    ...

def get_per_group_loaders(dataset, batch_size: int = 128) -> Dict[int, DataLoader]:
    """Create DataLoaders for all 4 Waterbirds groups"""
    ...
```

---

### 3. Gradient Computation Module (`gradient_computation.py`) [NEW]

**Dependencies**: PyTorch

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np

def compute_group_gradient(model: nn.Module, group_loader: DataLoader, 
                          device: str = 'cuda') -> np.ndarray:
    """Compute gradient vector for specific group"""
    ...

def flatten_gradients(model: nn.Module) -> torch.Tensor:
    """Flatten all parameter gradients into single vector"""
    ...
```

---

### 4. Alignment Analysis Module (`alignment_analysis.py`) [NEW]

**Dependencies**: NumPy

```python
import numpy as np
from typing import Dict, Any

def compute_alignment(gradient: np.ndarray, outlier_eigenvectors: np.ndarray) -> float:
    """
    Compute A(w) = ||P @ g||² / ||g||² via on-the-fly projection
    Uses memory-efficient: P @ g = V @ (V^T @ g)
    """
    ...

def compare_alignments(minority_gradient: np.ndarray, majority_gradient: np.ndarray,
                      outlier_eigenvectors: np.ndarray) -> Dict[str, Any]:
    """Compare minority vs majority gradient alignment (GATE METRIC)"""
    ...

def compute_per_group_alignments(gradients: Dict[int, np.ndarray],
                                outlier_eigenvectors: np.ndarray) -> Dict[int, float]:
    """Compute alignment for all 4 Waterbirds groups"""
    ...
```

---

### 5. Visualization Module (`visualize_alignment.py`) [NEW]

**Dependencies**: matplotlib

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

def plot_projection_magnitude(minority_proj: float, majority_proj: float, save_path: str):
    """Projection magnitude comparison"""
    ...

def generate_all_figures(comparison: Dict, group_alignments: Dict, figures_dir: str):
    """Generate all required figures"""
    ...
```

---

### 6. Main Experiment Script (`run_h_m2_experiment.py`) [NEW]

**Dependencies**: All modules above

```python
from artifact_loader import load_h_m1_outliers, verify_outlier_artifacts
from group_data import get_group_loaders, get_per_group_loaders
from gradient_computation import compute_group_gradient
from alignment_analysis import compute_alignment, compare_alignments, compute_per_group_alignments
from visualize_alignment import generate_all_figures
import torch
import sys
from pathlib import Path

def main():
    # Load h-m1 outlier eigenvectors
    outlier_data = load_h_m1_outliers('../h-m1/results')
    verify_outlier_artifacts(outlier_data)
    
    # Load Waterbirds dataset
    sys.path.insert(0, str(Path('../h-e1/code')))
    from data.dataset import get_dataloaders
    loaders = get_dataloaders(data_dir='../h-e1/code/data/waterbirds/', batch_size=128)
    
    # Create group-specific loaders
    group_loaders = get_group_loaders(loaders['train'].dataset)
    
    # Load ERM model from h-m1 (uses h-e1 checkpoint path)
    from models.model import get_resnet50
    model = get_resnet50(num_classes=2)
    checkpoint = torch.load('../h-e1/code/checkpoints/erm_best.pth')
    model.load_state_dict(checkpoint['model_state_dict'])
    model.eval()
    
    # Compute minority gradient
    minority_gradient = compute_group_gradient(model, group_loaders['minority'], device)
    
    # Compute majority gradient
    majority_gradient = compute_group_gradient(model, group_loaders['majority'], device)
    
    # Compare alignments (GATE METRIC)
    comparison = compare_alignments(minority_gradient, majority_gradient, 
                                   outlier_data['eigenvectors'])
    
    # Per-group analysis
    per_group_loaders = get_per_group_loaders(loaders['train'].dataset)
    per_group_gradients = {gid: compute_group_gradient(model, loader, device) 
                          for gid, loader in per_group_loaders.items()}
    group_alignments = compute_per_group_alignments(per_group_gradients, 
                                                   outlier_data['eigenvectors'])
    
    # Visualize
    generate_all_figures(comparison, group_alignments, figures_dir='./figures/')
    
    # Save results
    save_alignment_metrics(comparison, group_alignments, results_dir='./results/')
    
    # Gate check
    print(f"GATE CHECK (SHOULD_WORK): A_minority > A_majority")
    print(f"A_minority: {comparison['A_minority']:.4f}")
    print(f"A_majority: {comparison['A_majority']:.4f}")
    print(f"Delta: {comparison['delta_align']:.4f}")
    print(f"Mechanism Confirmed: {comparison['mechanism_confirmed']}")
    
    return comparison['mechanism_confirmed']
```

---

## File Structure

```
h-m2/
├── code/
│   ├── artifact_loader.py              # Load h-m1 outlier eigenvectors (NEW)
│   ├── group_data.py                   # Group-aware data loading (NEW)
│   ├── gradient_computation.py         # Gradient computation per group (NEW)
│   ├── alignment_analysis.py           # Alignment metric computation (NEW)
│   ├── visualize_alignment.py          # Alignment visualizations (NEW)
│   ├── run_h_m2_experiment.py          # Main execution script (NEW)
│   ├── config.py                       # Hyperparameters (NEW)
│   └── requirements.txt                # Dependencies (same as h-m1)
├── results/                            # Analysis outputs
│   ├── alignment_metrics.csv
│   ├── per_group_alignments.csv
│   └── comparison_results.json
└── figures/                            # Visualizations
    ├── fig1_alignment_comparison.png   (GATE METRIC)
    ├── fig2_per_group_alignments.png
    └── fig3_projection_magnitude.png
```

**Note**: No training required. Reuse h-e1 ERM checkpoint and h-m1 outlier eigenvectors.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| B-1 | Environment Setup | Verify h-m1 artifacts exist, setup paths | 5 | 1+1+2+1 |
| B-2 | Artifact Loading | Load h-m1 outlier eigenvectors and verify | 8 | 2+2+2+2 |
| B-3 | Group Data Loading | Create minority/majority DataLoaders | 10 | 3+2+3+2 |
| B-4 | Gradient Computation | Compute minority and majority gradients | 11 | 3+3+3+2 |
| B-5 | Alignment Analysis | Compute alignment metrics and comparison | 13 | 3+3+4+3 |
| B-6 | Per-Group Analysis | Compute alignment for all 4 groups | 9 | 2+3+2+2 |
| B-7 | Visualization | Generate 3 figures (gate metric + analysis) | 10 | 3+2+3+2 |
| B-8 | Integration Testing | Run full pipeline, verify gate metric | 9 | 3+2+2+2 |

**Total Complexity**: 75  
**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [B-3, B-4, B-5, B-6, B-7, B-8], Low(4-8): [B-1, B-2]

**Complexity Scoring**:
- B-1: Module(1) + Deps(1) + Algo(2) + Integration(1) = 5
- B-2: Module(2) + Deps(2) + Algo(2) + Integration(2) = 8
- B-3: Module(3) + Deps(2) + Algo(3) + Integration(2) = 10
- B-4: Module(3) + Deps(3) + Algo(3) + Integration(2) = 11
- B-5: Module(3) + Deps(3) + Algo(4) + Integration(3) = 13
- B-6: Module(2) + Deps(3) + Algo(2) + Integration(2) = 9
- B-7: Module(3) + Deps(2) + Algo(3) + Integration(2) = 10
- B-8: Module(3) + Deps(2) + Algo(2) + Integration(2) = 9

---

## Task Breakdown Details

### B-1: Environment Setup (Complexity: 5)

**Subtasks**:
1. Verify h-m1 results directory exists
2. Verify h-e1 checkpoint exists
3. Setup h-m2 results and figures directories
4. Verify PyTorch and dependencies installed

**Deliverables**:
- h-m1 artifacts accessible
- h-e1 checkpoint accessible
- Directory structure created

---

### B-2: Artifact Loading (Complexity: 8)

**Subtasks**:
1. Implement `load_h_m1_outliers()` function
2. Load outlier eigenvectors from h-m1 results
3. Implement `verify_outlier_artifacts()` validation
4. Verify 23 outlier eigenvectors (from h-m1)
5. Unit tests for artifact loading

**Deliverables**:
- `artifact_loader.py` module
- Outlier eigenvectors loaded (shape: [num_params, 23])
- Validation passed

---

### B-3: Group Data Loading (Complexity: 10)

**Subtasks**:
1. Implement `get_group_loaders()` function
2. Parse Waterbirds group metadata
3. Create minority group subset (groups 1, 3)
4. Create majority group subset (groups 0, 2)
5. Implement `get_per_group_loaders()` for 4-way split
6. Verify group sizes match expected distributions

**Deliverables**:
- `group_data.py` module
- Minority loader (~240 samples)
- Majority loader (~4,555 samples)
- 4 per-group loaders

---

### B-4: Gradient Computation (Complexity: 11)

**Subtasks**:
1. Implement `compute_group_gradient()` function
2. Implement `flatten_gradients()` helper
3. Compute minority gradient on minority loader
4. Compute majority gradient on majority loader
5. Validate gradient shapes match model parameters
6. Unit tests for gradient computation

**Deliverables**:
- `gradient_computation.py` module
- Minority gradient vector (num_params,)
- Majority gradient vector (num_params,)
- Gradient computation tests passing

---

### B-5: Alignment Analysis (Complexity: 13)

**Subtasks**:
1. Implement `compute_alignment()` function
2. Implement memory-efficient projection: P @ g = V @ (V^T @ g)
3. Compute A_minority alignment
4. Compute A_majority alignment
5. Implement `compare_alignments()` function
6. Compute delta_align and mechanism_confirmed
7. Validate alignment ∈ [0, 1]
8. Unit tests for alignment computation

**Deliverables**:
- `alignment_analysis.py` module
- A_minority, A_majority metrics
- Comparison dict with gate metric result
- Tests passing

---

### B-6: Per-Group Analysis (Complexity: 9)

**Subtasks**:
1. Implement `compute_per_group_alignments()` function
2. Compute gradient for group 0 (landbirds on land)
3. Compute gradient for group 1 (landbirds on water)
4. Compute gradient for group 2 (waterbirds on water)
5. Compute gradient for group 3 (waterbirds on land)
6. Compute alignment for all 4 groups
7. Verify minority groups (1, 3) have higher alignment

**Deliverables**:
- Per-group alignments dict
- Alignment values for all 4 groups
- Validation of minority > majority pattern

---

### B-7: Visualization (Complexity: 10)

**Subtasks**:
1. Implement `plot_alignment_comparison()` (GATE METRIC bar chart)
2. Implement `plot_per_group_alignments()` (4-group bar chart)
3. Implement `plot_projection_magnitude()` (projection comparison)
4. Implement `generate_all_figures()` orchestration
5. Generate all 3 figures and save to `figures/` directory

**Deliverables**:
- `visualize_alignment.py` module
- 3 figures in `figures/` directory
- Figure 1 (gate metric) clearly labeled

---

### B-8: Integration Testing (Complexity: 9)

**Subtasks**:
1. Implement unit tests for all new modules
2. Run full pipeline end-to-end
3. Verify all outputs generated correctly
4. Validate gate metric (A_minority > A_majority)
5. Save results to CSV and JSON
6. Document results

**Deliverables**:
- All unit tests passing
- Complete pipeline execution confirmation
- All artifacts verified (figures, metrics, results)
- Gate check result documented

---

## Integration with h-m1

**Critical Integration Points:**

1. **Outlier Eigenvectors**: Load from `h-m1/results/outlier_eigenvectors_erm.npy`
2. **Outlier Count**: Expect 23 eigenvectors (from h-m1 validation)
3. **ERM Model**: Load from `h-e1/checkpoints/erm_best.pth` (same as h-m1)
4. **Dataset**: Use h-e1 Waterbirds dataset location

**Verification Strategy:**
- Load h-m1 artifacts → Verify shape (num_params, 23)
- Load ERM checkpoint → Same checkpoint used in h-m1
- Compute gradients → Validate shapes match model parameters
- Compute alignments → Verify range [0, 1]
- NEW: Gradient alignment comparison (not in h-m1)

**Expected Consistency with h-m1:**
- Outlier eigenvectors: 23 from h-m1 validation
- ERM model: Same checkpoint as h-m1
- Bulk edge: Use h-m1's validated λ+ = 2.456

---

## Configuration Schema

```python
@dataclass
class H_M2_Config:
    """h-m2 specific configuration"""
    
    project: ProjectConfig = field(default_factory=lambda: ProjectConfig(
        hypothesis_id="h-m2",
        hypothesis_type="MECHANISM",
        tier="STANDARD",
        base_hypothesis="h-m1"
    ))
    
    paths: PathsConfig = field(default_factory=lambda: PathsConfig(
        h_m1_results='../h-m1/results',
        h_e1_checkpoints='../h-e1/code/checkpoints',
        h_e1_data='../h-e1/code/data/waterbirds',
        results_dir='./code/results/',
        figures_dir='./code/figures/'
    ))
    
    alignment: AlignmentConfig = field(default_factory=lambda: AlignmentConfig(
        projection_method='memory_efficient',  # V @ (V^T @ g)
        normalize_gradients=False,
        validate_range=True  # Assert alignment in [0, 1]
    ))
    
    groups: GroupConfig = field(default_factory=lambda: GroupConfig(
        minority_ids=[1, 3],  # landbirds on water, waterbirds on land
        majority_ids=[0, 2],  # landbirds on land, waterbirds on water
        batch_size=128
    ))
```

---

*Architecture designed for Phase 4 Implementation | h-m2 MECHANISM Hypothesis | Extends h-m1 outlier analysis*
