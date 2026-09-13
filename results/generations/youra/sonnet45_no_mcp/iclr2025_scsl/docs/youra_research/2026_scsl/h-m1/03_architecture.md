# System Architecture: h-m1 Hessian Outlier Concentration

**Hypothesis ID:** h-m1  
**Type:** MECHANISM (Step 1 of 4)  
**Gate:** MUST_WORK  
**Date:** 2026-04-24  
**Architect:** Architecture Agent  
**Prerequisites:** h-e1 (COMPLETED ✅)

---

## Codebase Analysis (Serena)

**Project Type**: Incremental (extends h-e1)  
**Status**: Building on h-e1 validated baseline  
**Analyzed Path**: `../h-e1/code/`  
**Base Hypothesis:** h-e1  

**Findings from h-e1 Code:**
- Existing modules: `data.py`, `model.py`, `train.py`, `hessian_analysis.py`, `evaluate.py`, `visualize.py`
- Checkpoint format: `{'model_state_dict': ..., 'optimizer_state_dict': ..., 'epoch': ..., 'metrics': ...}`
- Hessian computation: Uses `pytorch-hessian-eigenthings` library
- MP fitting: Implemented in `hessian_analysis.py::fit_marchenko_pastur()`
- Data loading: `get_dataloaders()` and `get_minority_loader()` APIs

**Import Paths (Verified from h-e1 Implementation):**
```python
# From h-e1/code/
from h_e1.code.data import get_dataloaders, get_minority_loader
from h_e1.code.hessian_analysis import (
    compute_hessian_spectrum, 
    fit_marchenko_pastur
)
from h_e1.code.model import get_resnet50
```

---

## Knowledge Base Patterns Applied

Applied: Incremental Hypothesis Pattern (reuse validated baseline)  
Applied: Hessian Eigendecomposition Pattern  
Applied: Outlier Detection via Marchenko-Pastur Bulk Edge  

---

## System Overview

**Purpose**: Validate mechanism hypothesis that sharp curvature concentrates in Hessian outlier subspaces (eigenvalues beyond MP bulk edge) for ERM vs DRO solutions.

**Core Components**:
- Checkpoint loading (from h-e1 trained models)
- Data loading (reuse h-e1 data module)
- Hessian analysis (extend h-e1 hessian module)
- Outlier identification (NEW module)
- Outlier comparison (NEW module)
- Visualization (extend h-e1 visualize module)

**Infrastructure Tier**: FULL (30 tasks, standard logging, unit tests)

---

## External Dependencies (from h-e1)

**Critical**: h-m1 depends on h-e1's validated implementation. The following h-e1 components are required:

| Component | h-e1 Path | Used For |
|-----------|-----------|----------|
| ERM Checkpoint | `../h-e1/checkpoints/erm_best.pth` | Load converged ERM model |
| DRO Checkpoint | `../h-e1/checkpoints/dro_best.pth` | Load converged DRO model |
| Data Module | `../h-e1/code/data.py` | Dataset loading |
| Hessian Module | `../h-e1/code/hessian_analysis.py` | Hessian computation, MP fitting |
| Model Module | `../h-e1/code/model.py` | ResNet-50 architecture |

**Integration Points:**
- Load h-e1 checkpoints → No retraining
- Import h-e1 data functions → Same dataset
- Import h-e1 Hessian functions → Same computation method
- Extend with NEW outlier analysis

---

## Module Structure

### 1. Checkpoint Loader Module (`checkpoint_loader.py`) [NEW]

**Dependencies**: h-e1 model module

```python
import torch
from pathlib import Path
from h_e1.code.model import get_resnet50

def load_h_e1_checkpoint(checkpoint_path: str, device: str = 'cuda') -> nn.Module:
    """
    Load trained model from h-e1 baseline
    
    Args:
        checkpoint_path: Path to h-e1 checkpoint
    
    Returns:
        model: Loaded ResNet-50 model in eval mode
    """
    ...

def verify_checkpoint_metrics(checkpoint_path: str) -> Dict[str, float]:
    """
    Verify checkpoint metrics match h-e1 validation results
    
    Returns:
        metrics: dict with worst_group_acc, avg_acc from checkpoint
    """
    ...
```

---

### 2. Outlier Analysis Module (`outlier_analysis.py`) [NEW]

**Dependencies**: None (uses NumPy)

```python
import numpy as np
from typing import Dict, Tuple, Any

def identify_outliers(eigenvalues: np.ndarray, bulk_edge: float) -> Dict[str, Any]:
    """
    Identify outlier eigenvalues beyond MP bulk edge
    
    Returns:
        outlier_stats: dict with num_outliers, outlier_eigenvalues, max, mean, fraction
    """
    ...

def compare_outlier_concentration(erm_stats: Dict, dro_stats: Dict) -> Dict[str, Any]:
    """
    Compare outlier concentration between ERM and DRO
    
    Returns:
        comparison: dict with differences, ratios, mechanism_confirmed
    """
    ...

def compute_outlier_distribution(eigenvalues: np.ndarray, bulk_edge: float, 
                                 num_bins: int = 20) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute histogram of outlier eigenvalue distribution
    
    Returns:
        bin_edges: (num_bins+1,) - histogram bin edges
        bin_counts: (num_bins,) - counts per bin
    """
    ...
```

---

### 3. Extended Visualization Module (`visualize_outliers.py`) [NEW]

**Dependencies**: h-e1 visualize module (for base patterns)

```python
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict

def plot_outlier_comparison(erm_stats: Dict, dro_stats: Dict, save_path: str):
    """Bar chart: num_outliers_ERM vs num_outliers_DRO (GATE METRIC)"""
    ...

def plot_spectra_comparison(eigenvalues_erm: np.ndarray, eigenvalues_dro: np.ndarray,
                            bulk_edge_erm: float, bulk_edge_dro: float, save_path: str):
    """Side-by-side eigenvalue spectra with bulk edge overlays"""
    ...

def plot_outlier_distributions(erm_outliers: np.ndarray, dro_outliers: np.ndarray, 
                               save_path: str):
    """Histogram comparison of outlier eigenvalue distributions"""
    ...

def plot_mp_fit_quality(eigenvalues: np.ndarray, bulk_edge: float, 
                        sigma_sq: float, gamma: float, save_path: str):
    """Q-Q plot for MP fit validation"""
    ...

def plot_eigenvalue_decay(eigenvalues_erm: np.ndarray, eigenvalues_dro: np.ndarray, 
                         save_path: str):
    """Cumulative eigenvalue decay curves"""
    ...
```

---

### 4. Main Experiment Script (`run_h_m1_experiment.py`) [NEW]

**Dependencies**: All modules + h-e1 dependencies

```python
from checkpoint_loader import load_h_e1_checkpoint, verify_checkpoint_metrics
from h_e1.code.data import get_dataloaders
from h_e1.code.hessian_analysis import compute_hessian_spectrum, fit_marchenko_pastur
from outlier_analysis import identify_outliers, compare_outlier_concentration
from visualize_outliers import (plot_outlier_comparison, plot_spectra_comparison,
                                plot_outlier_distributions, plot_mp_fit_quality,
                                plot_eigenvalue_decay)
import torch

def main():
    # Setup
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # Load h-e1 checkpoints
    erm_model = load_h_e1_checkpoint('../h-e1/checkpoints/erm_best.pth', device)
    dro_model = load_h_e1_checkpoint('../h-e1/checkpoints/dro_best.pth', device)
    
    # Verify checkpoints
    erm_metrics = verify_checkpoint_metrics('../h-e1/checkpoints/erm_best.pth')
    dro_metrics = verify_checkpoint_metrics('../h-e1/checkpoints/dro_best.pth')
    
    # Load data (reuse h-e1)
    dataloaders = get_dataloaders(data_dir='./data/waterbird_complete95_forest2water2/', 
                                   batch_size=128)
    
    # Compute Hessian eigenspectra
    erm_eigenvalues, erm_eigenvectors = compute_hessian_spectrum(erm_model, dataloaders['train'])
    dro_eigenvalues, dro_eigenvectors = compute_hessian_spectrum(dro_model, dataloaders['train'])
    
    # Fit MP distributions
    erm_bulk_edge, erm_sigma_sq, erm_gamma = fit_marchenko_pastur(erm_eigenvalues)
    dro_bulk_edge, dro_sigma_sq, dro_gamma = fit_marchenko_pastur(dro_eigenvalues)
    
    # Identify outliers (NEW)
    erm_outlier_stats = identify_outliers(erm_eigenvalues, erm_bulk_edge)
    dro_outlier_stats = identify_outliers(dro_eigenvalues, dro_bulk_edge)
    
    # Compare outlier concentration (NEW)
    comparison = compare_outlier_concentration(erm_outlier_stats, dro_outlier_stats)
    
    # Visualize (NEW)
    generate_all_figures(erm_eigenvalues, dro_eigenvalues, 
                        erm_outlier_stats, dro_outlier_stats,
                        erm_bulk_edge, dro_bulk_edge,
                        erm_sigma_sq, erm_gamma, dro_sigma_sq, dro_gamma)
    
    # Save results
    save_outlier_metrics(erm_outlier_stats, dro_outlier_stats, comparison)
    
    # Gate check
    print(f"\n{'='*60}")
    print(f"GATE CHECK (MUST_WORK): ERM outliers > DRO outliers")
    print(f"{'='*60}")
    print(f"ERM Outliers: {erm_outlier_stats['num_outliers']}")
    print(f"DRO Outliers: {dro_outlier_stats['num_outliers']}")
    print(f"Difference: {comparison['num_outliers_diff']}")
    print(f"Mechanism Confirmed: {comparison['mechanism_confirmed']}")
    print(f"{'='*60}\n")
    
    return comparison['mechanism_confirmed']
```

---

### 5. Unit Test Module (`test_outlier_analysis.py`) [NEW]

**Dependencies**: All modules

```python
import pytest
import numpy as np
from outlier_analysis import identify_outliers, compare_outlier_concentration

def test_identify_outliers():
    """Test outlier identification with known eigenvalues"""
    eigenvalues = np.array([10.0, 5.0, 3.0, 2.0, 1.5, 1.0, 0.8, 0.6, 0.4, 0.2])
    bulk_edge = 2.5
    stats = identify_outliers(eigenvalues, bulk_edge)
    
    assert stats['num_outliers'] == 3  # 10.0, 5.0, 3.0 > 2.5
    assert len(stats['outlier_eigenvalues']) == 3
    assert stats['max_eigenvalue'] == 10.0

def test_compare_outlier_concentration():
    """Test outlier comparison logic"""
    erm_stats = {'num_outliers': 20, 'max_eigenvalue': 8.0}
    dro_stats = {'num_outliers': 12, 'max_eigenvalue': 5.0}
    
    comparison = compare_outlier_concentration(erm_stats, dro_stats)
    
    assert comparison['num_outliers_diff'] == 8
    assert comparison['mechanism_confirmed'] == True
    assert comparison['max_eigenvalue_ratio'] > 1.0

def test_checkpoint_loading():
    """Test h-e1 checkpoint loading"""
    # Smoke test with dummy checkpoint
    ...

def run_unit_tests():
    """Run all unit tests"""
    pytest.main([__file__, '-v'])
```

---

## File Structure

```
h-m1/
├── code/
│   ├── checkpoint_loader.py           # Load h-e1 checkpoints (NEW)
│   ├── outlier_analysis.py           # Outlier identification & comparison (NEW)
│   ├── visualize_outliers.py         # Outlier-specific visualizations (NEW)
│   ├── run_h_m1_experiment.py        # Main execution script (NEW)
│   ├── test_outlier_analysis.py      # Unit tests (NEW)
│   ├── config.py                      # Hyperparameters (NEW)
│   └── requirements.txt               # Dependencies (same as h-e1)
├── results/                           # Analysis outputs
│   ├── outlier_metrics.csv
│   ├── hessian_stats_erm.csv
│   ├── hessian_stats_dro.csv
│   └── comparison_results.json
└── figures/                           # Visualizations
    ├── fig1_outlier_comparison.png    (GATE METRIC)
    ├── fig2_spectra_comparison.png
    ├── fig3_outlier_distributions.png
    ├── fig4_mp_fit_quality_erm.png
    ├── fig5_mp_fit_quality_dro.png
    └── fig6_eigenvalue_decay.png
```

**Note**: No `data/` or `checkpoints/` directories needed - reuse from h-e1.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Environment Setup | Verify h-e1 dependencies, install any new packages | 4 | 1+1+1+1 |
| A-2 | Checkpoint Loader | Load h-e1 ERM/DRO checkpoints, verify metrics | 7 | 2+2+2+1 |
| A-3 | Hessian Computation | Compute eigenspectra for ERM and DRO (reuse h-e1) | 8 | 2+2+2+2 |
| A-4 | MP Bulk Edge Detection | Fit MP distributions for both models (reuse h-e1) | 6 | 2+1+2+1 |
| A-5 | Outlier Identification | Identify outliers beyond bulk edge | 10 | 3+2+3+2 |
| A-6 | Outlier Comparison | Compare ERM vs DRO outlier concentration | 12 | 3+3+3+3 |
| A-7 | Distribution Analysis | Analyze outlier eigenvalue distributions | 9 | 2+3+2+2 |
| A-8 | Visualization | Generate 6 figures (gate metric + analysis) | 11 | 3+2+3+3 |
| A-9 | Metrics Logging | Save outlier stats and comparison results | 6 | 2+1+2+1 |
| A-10 | Integration Testing | Run full pipeline, verify gate metric | 10 | 3+2+3+2 |

**Total Complexity**: 83  
**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-5, A-6, A-7, A-8, A-10], Low(4-8): [A-1, A-2, A-3, A-4, A-9]

**Complexity Scoring**:
- A-1: Module(1) + Deps(1) + Algo(1) + Integration(1) = 4
- A-2: Module(2) + Deps(2) + Algo(2) + Integration(1) = 7
- A-3: Module(2) + Deps(2) + Algo(2) + Integration(2) = 8
- A-4: Module(2) + Deps(1) + Algo(2) + Integration(1) = 6
- A-5: Module(3) + Deps(2) + Algo(3) + Integration(2) = 10
- A-6: Module(3) + Deps(3) + Algo(3) + Integration(3) = 12
- A-7: Module(2) + Deps(3) + Algo(2) + Integration(2) = 9
- A-8: Module(3) + Deps(2) + Algo(3) + Integration(3) = 11
- A-9: Module(2) + Deps(1) + Algo(2) + Integration(1) = 6
- A-10: Module(3) + Deps(2) + Algo(3) + Integration(2) = 10

---

## Task Breakdown Details

### A-1: Environment Setup (Complexity: 4)

**Subtasks**:
1. Verify h-e1 dependencies are installed (PyTorch, pytorch-hessian-eigenthings)
2. Verify h-e1 checkpoints exist and are accessible
3. Verify Waterbirds dataset is downloaded
4. Install any new packages (pytest for unit tests)

**Deliverables**:
- h-e1 dependencies verified
- Checkpoint paths confirmed
- `requirements.txt` file

---

### A-2: Checkpoint Loader (Complexity: 7)

**Subtasks**:
1. Implement `load_h_e1_checkpoint()` function
2. Implement `verify_checkpoint_metrics()` function
3. Load ERM checkpoint and verify worst-group accuracy
4. Load DRO checkpoint and verify worst-group accuracy
5. Unit tests for checkpoint loading

**Deliverables**:
- `checkpoint_loader.py` module
- ERM and DRO models loaded in memory
- Checkpoint metrics verified against h-e1 results

---

### A-3: Hessian Computation (Complexity: 8)

**Subtasks**:
1. Reuse h-e1 data loading (`get_dataloaders`)
2. Import h-e1 Hessian computation (`compute_hessian_spectrum`)
3. Compute Hessian for ERM model (top-100 eigenvalues)
4. Compute Hessian for DRO model (top-100 eigenvalues)
5. Save eigenvalues and eigenvectors to disk
6. Log Hessian computation progress

**Deliverables**:
- ERM eigenspectrum (eigenvalues, eigenvectors)
- DRO eigenspectrum (eigenvalues, eigenvectors)
- Hessian statistics saved to CSV

---

### A-4: MP Bulk Edge Detection (Complexity: 6)

**Subtasks**:
1. Import h-e1 MP fitting (`fit_marchenko_pastur`)
2. Fit MP distribution to ERM eigenvalues
3. Fit MP distribution to DRO eigenvalues
4. Save bulk edge parameters (σ², γ, λ+) for both models
5. Validate fit quality (visual inspection)

**Deliverables**:
- ERM bulk edge: λ+, σ², γ
- DRO bulk edge: λ+, σ², γ
- MP parameters saved to CSV

---

### A-5: Outlier Identification (Complexity: 10)

**Subtasks**:
1. Implement `identify_outliers()` function
2. Identify ERM outliers (λ > λ+_ERM)
3. Identify DRO outliers (λ > λ+_DRO)
4. Compute outlier statistics (count, max, mean, fraction)
5. Validate outlier detection logic with unit tests

**Deliverables**:
- `outlier_analysis.py::identify_outliers()`
- ERM outlier statistics
- DRO outlier statistics
- Unit tests passing

---

### A-6: Outlier Comparison (Complexity: 12)

**Subtasks**:
1. Implement `compare_outlier_concentration()` function
2. Compute num_outliers difference (ERM - DRO)
3. Compute max eigenvalue ratio (ERM_max / DRO_max)
4. Determine mechanism confirmation (ERM > DRO)
5. Compute percentage increase
6. Validate comparison logic with unit tests

**Deliverables**:
- `outlier_analysis.py::compare_outlier_concentration()`
- Comparison metrics (difference, ratio, mechanism_confirmed)
- Gate metric result (PASS/FAIL)

---

### A-7: Distribution Analysis (Complexity: 9)

**Subtasks**:
1. Implement `compute_outlier_distribution()` function
2. Create histogram of ERM outlier eigenvalues
3. Create histogram of DRO outlier eigenvalues
4. Compute cumulative eigenvalue sums
5. Statistical analysis (mean, std, range)

**Deliverables**:
- Outlier distribution histograms
- Cumulative eigenvalue data
- Statistical summary

---

### A-8: Visualization (Complexity: 11)

**Subtasks**:
1. Implement `plot_outlier_comparison()` (GATE METRIC bar chart)
2. Implement `plot_spectra_comparison()` (side-by-side spectra)
3. Implement `plot_outlier_distributions()` (histogram comparison)
4. Implement `plot_mp_fit_quality()` (Q-Q plots)
5. Implement `plot_eigenvalue_decay()` (cumulative curves)
6. Generate all 6 figures and save to `figures/` directory

**Deliverables**:
- `visualize_outliers.py` module
- 6 figures in `figures/` directory
- Figure 1 (gate metric) clearly labeled

---

### A-9: Metrics Logging (Complexity: 6)

**Subtasks**:
1. Implement CSV logging for outlier metrics
2. Save comparison results to JSON
3. Save Hessian statistics for both models
4. Create summary report with gate check result

**Deliverables**:
- `results/outlier_metrics.csv`
- `results/comparison_results.json`
- `results/hessian_stats_{erm,dro}.csv`
- Summary report with PASS/FAIL

---

### A-10: Integration Testing (Complexity: 10)

**Subtasks**:
1. Implement unit tests for all new modules
2. Run full pipeline end-to-end
3. Verify all outputs generated correctly
4. Validate gate metric (num_outliers_ERM > num_outliers_DRO)
5. Cross-check with h-e1 baseline (same checkpoints = should match h-e1 outlier counts)
6. Document any deviations

**Deliverables**:
- `test_outlier_analysis.py` with all tests passing
- Complete pipeline execution confirmation
- All artifacts verified (figures, metrics, results)
- Gate check PASS confirmation

---

## Integration with h-e1

**Critical Integration Points:**

1. **Checkpoint Loading**: Must correctly load h-e1's PyTorch checkpoint format
2. **Data Pipeline**: Import and use h-e1's data loading functions
3. **Hessian Computation**: Import and use h-e1's Hessian analysis module
4. **MP Fitting**: Import and use h-e1's MP fitting function

**Verification Strategy:**
- Load h-e1 checkpoints → Verify metrics match h-e1 validation report
- Compute Hessian on same models → Should get similar eigenvalue spectrum
- Apply same MP fitting → Should get similar bulk edge values
- NEW: Outlier identification and comparison (not in h-e1)

**Expected Consistency with h-e1:**
- ERM outliers: Should match h-e1's 23 outliers (same checkpoint)
- DRO outliers: Should match h-e1's 15 outliers (same checkpoint)
- Bulk edges: Should match h-e1's reported values

---

*Architecture designed for Phase 4 Implementation | h-m1 MECHANISM Hypothesis | Extends h-e1 baseline*
