# Logic Design: h-m1 Hessian Outlier Concentration

**Hypothesis ID:** h-m1  
**Type:** MECHANISM (Step 1 of 4)  
**Budget:** 8 subtasks (High-complexity modules)  
**Date:** 2026-04-24  
**Designer:** Logic Agent  
**Prerequisites:** h-e1 (COMPLETED ✅)

---

## Codebase Analysis (Serena)

**Project Type**: Incremental (extends h-e1)  
**Status**: Building on h-e1 validated implementation  
**Analyzed Path**: `../h-e1/code/`  
**Base Hypothesis:** h-e1

**Relevant Symbols from h-e1:**
- `h_e1.code.data.get_dataloaders() -> Dict[str, DataLoader]`
- `h_e1.code.model.get_resnet50(num_classes=2, pretrained=True) -> nn.Module`
- `h_e1.code.hessian_analysis.compute_hessian_spectrum(model, loader) -> Tuple[np.ndarray, np.ndarray]`
- `h_e1.code.hessian_analysis.fit_marchenko_pastur(eigenvalues) -> Tuple[float, float, float]`

**Checkpoint Format (from h-e1 implementation):**
```python
checkpoint = {
    'model_state_dict': model.state_dict(),
    'optimizer_state_dict': optimizer.state_dict(),
    'epoch': epoch,
    'metrics': {
        'worst_group_acc': worst_group_acc,
        'avg_acc': avg_acc,
        'val_loss': val_loss
    }
}
```

---

## Knowledge Base Patterns Applied

Applied: Incremental Hypothesis Pattern (extend validated baseline)  
Applied: Outlier Detection via Statistical Thresholding  
Applied: Eigenvalue Spectrum Analysis Pattern  

---

## External Dependencies API (from h-e1)

**Critical**: h-m1 imports and calls h-e1 functions directly. All signatures verified from h-e1 implementation.

### From h-e1/code/data.py

```python
def get_dataloaders(
    data_dir: str, 
    batch_size: int = 128,
    num_workers: int = 4
) -> Dict[str, DataLoader]:
    """
    Returns:
        dataloaders: dict with keys 'train', 'val', 'test'
    """
    ...
```

### From h-e1/code/model.py

```python
def get_resnet50(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """
    Returns:
        model: ResNet-50 with modified final layer
        Output shape: [B, num_classes]
    """
    ...
```

### From h-e1/code/hessian_analysis.py

```python
def compute_hessian_spectrum(
    model: nn.Module,
    data_loader: DataLoader,
    num_eigenthings: int = 100,
    device: str = 'cuda'
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Returns:
        eigenvalues: (num_eigenthings,) - descending order
        eigenvectors: (P, num_eigenthings) - P = num parameters
    """
    ...

def fit_marchenko_pastur(eigenvalues: np.ndarray) -> Tuple[float, float, float]:
    """
    Returns:
        bulk_edge: float - λ_+ = σ²(1 + √γ)²
        sigma_sq: float - noise variance estimate
        gamma: float - aspect ratio estimate
    """
    ...
```

---

## A-2: Checkpoint Loader Module [Complexity: 7, Budget: 2 subtasks]

**Applied**: PyTorch Checkpoint Loading Pattern

### API Signatures

```python
# File: checkpoint_loader.py

import torch
import torch.nn as nn
from pathlib import Path
from typing import Dict, Tuple
from h_e1.code.model import get_resnet50

def load_h_e1_checkpoint(
    checkpoint_path: str,
    device: str = 'cuda'
) -> nn.Module:
    """
    Load trained model from h-e1 baseline
    
    Args:
        checkpoint_path: Path to h-e1 checkpoint (e.g., '../h-e1/checkpoints/erm_best.pth')
        device: Device to load model on
    
    Returns:
        model: Loaded ResNet-50 model in eval mode
    """
    ...

def verify_checkpoint_metrics(checkpoint_path: str) -> Dict[str, float]:
    """
    Verify checkpoint metrics match h-e1 validation results
    
    Args:
        checkpoint_path: Path to h-e1 checkpoint
    
    Returns:
        metrics: dict with keys 'worst_group_acc', 'avg_acc', 'val_loss', 'epoch'
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| model.fc.weight | [2, 2048] | Final layer weights |
| model.fc.bias | [2] | Final layer bias |
| checkpoint['model_state_dict'] | OrderedDict | All model parameters |

### Pseudo-code

#### L-2-1: Load h-e1 Checkpoint

```
1. Verify checkpoint file exists at checkpoint_path
2. Create model architecture using get_resnet50():
   - model = get_resnet50(num_classes=2, pretrained=False)
   - This creates ResNet-50 with fc: Linear(2048, 2)
3. Load checkpoint:
   - checkpoint = torch.load(checkpoint_path, map_location=device)
4. Load state dict:
   - model.load_state_dict(checkpoint['model_state_dict'])
5. Move to device and set eval mode:
   - model.to(device)
   - model.eval()
6. Return model
```

#### L-2-2: Verify Checkpoint Metrics

```
1. Load checkpoint:
   - checkpoint = torch.load(checkpoint_path, map_location='cpu')
2. Extract metrics from checkpoint:
   - metrics = checkpoint.get('metrics', {})
3. Validate metrics exist:
   - assert 'worst_group_acc' in metrics, "Checkpoint missing worst_group_acc"
   - assert 'avg_acc' in metrics, "Checkpoint missing avg_acc"
4. Print metrics for verification:
   - print(f"Checkpoint Epoch: {checkpoint['epoch']}")
   - print(f"Worst-Group Acc: {metrics['worst_group_acc']:.4f}")
   - print(f"Average Acc: {metrics['avg_acc']:.4f}")
5. Return metrics dict
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Load Checkpoint | Load h-e1 checkpoint, restore model weights, set eval mode |
| L-2-2 | Verify Metrics | Extract and verify checkpoint metrics match h-e1 validation |

---

## A-5: Outlier Identification Module [Complexity: 10, Budget: 3 subtasks]

**Applied**: Statistical Outlier Detection Pattern

### API Signatures

```python
# File: outlier_analysis.py

import numpy as np
from typing import Dict, Any, Tuple

def identify_outliers(
    eigenvalues: np.ndarray,
    bulk_edge: float
) -> Dict[str, Any]:
    """
    Identify outlier eigenvalues beyond MP bulk edge
    
    Args:
        eigenvalues: (100,) - Hessian eigenvalues (descending order)
        bulk_edge: float - Marchenko-Pastur threshold λ_+
    
    Returns:
        outlier_stats: dict with:
            - num_outliers: int
            - outlier_eigenvalues: np.ndarray
            - max_eigenvalue: float
            - mean_outlier: float
            - outlier_fraction: float
            - outlier_indices: np.ndarray
    """
    ...

def compute_outlier_distribution(
    eigenvalues: np.ndarray,
    bulk_edge: float,
    num_bins: int = 20
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Compute histogram of outlier eigenvalue distribution
    
    Args:
        eigenvalues: (100,) - Hessian eigenvalues
        bulk_edge: float - MP threshold
        num_bins: int - number of histogram bins
    
    Returns:
        bin_edges: (num_bins+1,) - histogram bin edges
        bin_counts: (num_bins,) - counts per bin
    """
    ...

def analyze_outlier_spacing(outlier_eigenvalues: np.ndarray) -> Dict[str, float]:
    """
    Analyze spacing between consecutive outlier eigenvalues
    
    Args:
        outlier_eigenvalues: (K,) - outlier eigenvalues (descending)
    
    Returns:
        spacing_stats: dict with mean_spacing, std_spacing, max_gap
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| eigenvalues | (100,) | All eigenvalues (descending) |
| outlier_mask | (100,) | Boolean mask (True = outlier) |
| outlier_eigenvalues | (K,) | K = num outliers |
| outlier_indices | (K,) | Indices of outliers in original array |
| bin_edges | (num_bins+1,) | Histogram bin edges |
| bin_counts | (num_bins,) | Counts per bin |

### Pseudo-code

#### L-5-1: Identify Outliers

```
1. Create outlier mask:
   - outlier_mask = (eigenvalues > bulk_edge)  # [100] boolean array
2. Extract outlier eigenvalues:
   - outlier_eigenvalues = eigenvalues[outlier_mask]  # [K]
   - outlier_indices = np.where(outlier_mask)[0]  # [K]
3. Count outliers:
   - num_outliers = len(outlier_eigenvalues)
4. Compute statistics:
   - max_eigenvalue = eigenvalues[0] if len(eigenvalues) > 0 else 0.0
   - mean_outlier = np.mean(outlier_eigenvalues) if num_outliers > 0 else 0.0
   - outlier_fraction = num_outliers / len(eigenvalues)
5. Return outlier_stats dict with all metrics
```

#### L-5-2: Compute Outlier Distribution

```
1. Extract outlier eigenvalues:
   - outlier_mask = (eigenvalues > bulk_edge)
   - outlier_eigs = eigenvalues[outlier_mask]  # [K]
2. If no outliers:
   - Return empty bins
3. Create histogram:
   - bin_counts, bin_edges = np.histogram(outlier_eigs, bins=num_bins)
4. Return (bin_edges, bin_counts)
```

#### L-5-3: Analyze Outlier Spacing

```
1. If len(outlier_eigenvalues) < 2:
   - Return {mean_spacing: 0, std_spacing: 0, max_gap: 0}
2. Compute gaps between consecutive eigenvalues:
   - gaps = outlier_eigenvalues[:-1] - outlier_eigenvalues[1:]  # [K-1]
3. Compute statistics:
   - mean_spacing = np.mean(gaps)
   - std_spacing = np.std(gaps)
   - max_gap = np.max(gaps)
4. Return spacing_stats dict
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Identify Outliers | Apply threshold λ > λ_+, extract outlier eigenvalues, compute stats |
| L-5-2 | Outlier Distribution | Create histogram of outlier eigenvalue magnitudes |
| L-5-3 | Spacing Analysis | Analyze gaps between consecutive outliers |

---

## A-6: Outlier Comparison Module [Complexity: 12, Budget: 3 subtasks]

**Applied**: Statistical Comparison Pattern

### API Signatures

```python
# File: outlier_analysis.py (continued)

def compare_outlier_concentration(
    erm_stats: Dict[str, Any],
    dro_stats: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Compare outlier concentration between ERM and DRO
    
    Args:
        erm_stats: Outlier statistics for ERM model
        dro_stats: Outlier statistics for DRO model
    
    Returns:
        comparison: dict with:
            - num_outliers_ERM: int
            - num_outliers_DRO: int
            - num_outliers_diff: int (ERM - DRO)
            - max_eigenvalue_ERM: float
            - max_eigenvalue_DRO: float
            - max_eigenvalue_ratio: float (ERM / DRO)
            - mechanism_confirmed: bool (ERM > DRO)
            - percentage_increase: float
            - effect_description: str
    """
    ...

def compute_statistical_significance(
    erm_outliers: np.ndarray,
    dro_outliers: np.ndarray
) -> Dict[str, float]:
    """
    Compute statistical significance of difference (if multiple seeds)
    
    Args:
        erm_outliers: (K_erm,) - ERM outlier eigenvalues
        dro_outliers: (K_dro,) - DRO outlier eigenvalues
    
    Returns:
        stats: dict with p_value, cohens_d, significant (bool)
    
    Note: For single seed, returns descriptive statistics only
    """
    ...

def generate_comparison_summary(comparison: Dict[str, Any]) -> str:
    """
    Generate human-readable comparison summary
    
    Returns:
        summary: str - formatted summary with gate check result
    """
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| erm_outliers | (K_erm,) | ERM outlier eigenvalues |
| dro_outliers | (K_dro,) | DRO outlier eigenvalues |

### Pseudo-code

#### L-6-1: Compare Outlier Concentration

```
1. Extract key metrics:
   - num_outliers_ERM = erm_stats['num_outliers']
   - num_outliers_DRO = dro_stats['num_outliers']
   - max_eigenvalue_ERM = erm_stats['max_eigenvalue']
   - max_eigenvalue_DRO = dro_stats['max_eigenvalue']
2. Compute differences:
   - num_outliers_diff = num_outliers_ERM - num_outliers_DRO
3. Compute ratios:
   - max_eigenvalue_ratio = max_eigenvalue_ERM / max_eigenvalue_DRO if max_eigenvalue_DRO > 0 else inf
4. Determine mechanism confirmation:
   - mechanism_confirmed = (num_outliers_diff > 0)
5. Compute percentage increase:
   - percentage_increase = (num_outliers_diff / num_outliers_DRO * 100) if num_outliers_DRO > 0 else inf
6. Generate effect description:
   - If mechanism_confirmed: "ERM has {num_outliers_diff} more outliers than DRO ({percentage_increase:.1f}% increase)"
   - Else: "GATE FAILURE: ERM does not have more outliers than DRO"
7. Return comparison dict with all metrics
```

#### L-6-2: Compute Statistical Significance

```
1. For single seed (as in h-m1 PoC):
   - Return descriptive statistics only (mean, std of outlier magnitudes)
2. For multiple seeds (future work):
   - Perform two-sample t-test on outlier counts
   - Compute Cohen's d effect size
   - Return p_value, cohens_d, significant (p < 0.05)
```

#### L-6-3: Generate Comparison Summary

```
1. Format header:
   - summary = "="*60 + "\n"
   - summary += "OUTLIER CONCENTRATION COMPARISON\n"
   - summary += "="*60 + "\n"
2. Add metrics:
   - summary += f"ERM Outliers: {comparison['num_outliers_ERM']}\n"
   - summary += f"DRO Outliers: {comparison['num_outliers_DRO']}\n"
   - summary += f"Difference: {comparison['num_outliers_diff']}\n"
   - summary += f"Percentage Increase: {comparison['percentage_increase']:.1f}%\n"
3. Add gate check:
   - summary += "\nGATE CHECK (MUST_WORK):\n"
   - summary += f"Mechanism Confirmed: {comparison['mechanism_confirmed']}\n"
   - summary += f"Result: {'PASS ✓' if comparison['mechanism_confirmed'] else 'FAIL ✗'}\n"
4. Add effect description:
   - summary += f"\n{comparison['effect_description']}\n"
5. Return summary
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Outlier Comparison | Compute differences, ratios, determine mechanism confirmation |
| L-6-2 | Statistical Significance | Compute p-value and effect size (descriptive for single seed) |
| L-6-3 | Summary Generation | Generate human-readable comparison summary with gate check |

---

## Supporting Module APIs (No Budget Required)

### From h-e1: Data Module

```python
# Already implemented in h-e1/code/data.py
# Direct import: from h_e1.code.data import get_dataloaders

def get_dataloaders(data_dir: str, batch_size: int = 128) -> Dict[str, DataLoader]:
    """
    Returns:
        dataloaders: dict with keys 'train', 'val', 'test'
        Each DataLoader yields: (images, labels, groups)
            images: [B, 3, 224, 224]
            labels: [B] (0=landbird, 1=waterbird)
            groups: [B] (0-3)
    """
    ...
```

### From h-e1: Hessian Analysis Module

```python
# Already implemented in h-e1/code/hessian_analysis.py
# Direct import: from h_e1.code.hessian_analysis import compute_hessian_spectrum, fit_marchenko_pastur

def compute_hessian_spectrum(
    model: nn.Module,
    data_loader: DataLoader,
    num_eigenthings: int = 100
) -> Tuple[np.ndarray, np.ndarray]:
    """Uses pytorch-hessian-eigenthings library"""
    ...

def fit_marchenko_pastur(eigenvalues: np.ndarray) -> Tuple[float, float, float]:
    """Returns (bulk_edge, sigma_sq, gamma)"""
    ...
```

### Visualization Module (visualize_outliers.py)

```python
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict

def plot_outlier_comparison(erm_stats: Dict, dro_stats: Dict, save_path: str):
    """
    Bar chart: num_outliers_ERM vs num_outliers_DRO (GATE METRIC)
    
    Inputs:
        erm_stats['num_outliers']: int
        dro_stats['num_outliers']: int
    """
    ...

def plot_spectra_comparison(
    eigenvalues_erm: np.ndarray,  # (100,)
    eigenvalues_dro: np.ndarray,  # (100,)
    bulk_edge_erm: float,
    bulk_edge_dro: float,
    save_path: str
):
    """Side-by-side eigenvalue spectra with bulk edge overlays"""
    ...

def plot_outlier_distributions(
    erm_outliers: np.ndarray,  # (K_erm,)
    dro_outliers: np.ndarray,  # (K_dro,)
    save_path: str
):
    """Histogram comparison of outlier eigenvalue distributions"""
    ...

def plot_mp_fit_quality(
    eigenvalues: np.ndarray,  # (100,)
    bulk_edge: float,
    sigma_sq: float,
    gamma: float,
    model_name: str,
    save_path: str
):
    """Q-Q plot for MP fit validation"""
    ...

def plot_eigenvalue_decay(
    eigenvalues_erm: np.ndarray,  # (100,)
    eigenvalues_dro: np.ndarray,  # (100,)
    save_path: str
):
    """Cumulative eigenvalue decay curves"""
    ...
```

---

## Main Experiment Flow

```python
# File: run_h_m1_experiment.py

from checkpoint_loader import load_h_e1_checkpoint, verify_checkpoint_metrics
from h_e1.code.data import get_dataloaders
from h_e1.code.hessian_analysis import compute_hessian_spectrum, fit_marchenko_pastur
from outlier_analysis import (identify_outliers, compare_outlier_concentration,
                              compute_statistical_significance, generate_comparison_summary)
from visualize_outliers import (plot_outlier_comparison, plot_spectra_comparison,
                                plot_outlier_distributions, plot_mp_fit_quality,
                                plot_eigenvalue_decay)
import torch
import json

def main():
    """
    Main execution flow for h-m1 experiment
    
    Steps:
    1. Load h-e1 checkpoints (ERM, DRO)
    2. Load data (reuse h-e1)
    3. Compute Hessian eigenspectra
    4. Fit MP distributions
    5. Identify outliers
    6. Compare outlier concentration
    7. Generate visualizations
    8. Save results
    9. Report gate check
    """
    
    # 1. Setup
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    
    # 2. Load h-e1 checkpoints
    print("\nLoading h-e1 checkpoints...")
    erm_model = load_h_e1_checkpoint('../h-e1/checkpoints/erm_best.pth', device)
    dro_model = load_h_e1_checkpoint('../h-e1/checkpoints/dro_best.pth', device)
    
    # 3. Verify checkpoint metrics
    print("\nVerifying checkpoint metrics...")
    erm_metrics = verify_checkpoint_metrics('../h-e1/checkpoints/erm_best.pth')
    dro_metrics = verify_checkpoint_metrics('../h-e1/checkpoints/dro_best.pth')
    
    # 4. Load data
    print("\nLoading Waterbirds dataset...")
    dataloaders = get_dataloaders(data_dir='./data/waterbird_complete95_forest2water2/', 
                                   batch_size=128)
    
    # 5. Compute Hessian eigenspectra
    print("\nComputing Hessian eigenspectrum for ERM...")
    erm_eigenvalues, erm_eigenvectors = compute_hessian_spectrum(erm_model, dataloaders['train'])
    
    print("Computing Hessian eigenspectrum for DRO...")
    dro_eigenvalues, dro_eigenvectors = compute_hessian_spectrum(dro_model, dataloaders['train'])
    
    # 6. Fit MP distributions
    print("\nFitting Marchenko-Pastur distributions...")
    erm_bulk_edge, erm_sigma_sq, erm_gamma = fit_marchenko_pastur(erm_eigenvalues)
    dro_bulk_edge, dro_sigma_sq, dro_gamma = fit_marchenko_pastur(dro_eigenvalues)
    
    print(f"ERM Bulk Edge: λ+ = {erm_bulk_edge:.4f}")
    print(f"DRO Bulk Edge: λ+ = {dro_bulk_edge:.4f}")
    
    # 7. Identify outliers
    print("\nIdentifying outlier eigenvalues...")
    erm_outlier_stats = identify_outliers(erm_eigenvalues, erm_bulk_edge)
    dro_outlier_stats = identify_outliers(dro_eigenvalues, dro_bulk_edge)
    
    print(f"ERM Outliers: {erm_outlier_stats['num_outliers']}")
    print(f"DRO Outliers: {dro_outlier_stats['num_outliers']}")
    
    # 8. Compare outlier concentration
    print("\nComparing outlier concentration...")
    comparison = compare_outlier_concentration(erm_outlier_stats, dro_outlier_stats)
    
    # 9. Generate summary
    summary = generate_comparison_summary(comparison)
    print("\n" + summary)
    
    # 10. Generate visualizations
    print("\nGenerating visualizations...")
    plot_outlier_comparison(erm_outlier_stats, dro_outlier_stats, 
                            'figures/fig1_outlier_comparison.png')
    plot_spectra_comparison(erm_eigenvalues, dro_eigenvalues,
                           erm_bulk_edge, dro_bulk_edge,
                           'figures/fig2_spectra_comparison.png')
    plot_outlier_distributions(erm_outlier_stats['outlier_eigenvalues'],
                              dro_outlier_stats['outlier_eigenvalues'],
                              'figures/fig3_outlier_distributions.png')
    plot_mp_fit_quality(erm_eigenvalues, erm_bulk_edge, erm_sigma_sq, erm_gamma,
                       'ERM', 'figures/fig4_mp_fit_quality_erm.png')
    plot_mp_fit_quality(dro_eigenvalues, dro_bulk_edge, dro_sigma_sq, dro_gamma,
                       'DRO', 'figures/fig5_mp_fit_quality_dro.png')
    plot_eigenvalue_decay(erm_eigenvalues, dro_eigenvalues,
                         'figures/fig6_eigenvalue_decay.png')
    
    # 11. Save results
    print("\nSaving results...")
    results = {
        'erm_outlier_stats': {k: v.tolist() if isinstance(v, np.ndarray) else v 
                             for k, v in erm_outlier_stats.items()},
        'dro_outlier_stats': {k: v.tolist() if isinstance(v, np.ndarray) else v 
                             for k, v in dro_outlier_stats.items()},
        'comparison': comparison,
        'gate_check': {
            'type': 'MUST_WORK',
            'metric': 'num_outliers_ERM > num_outliers_DRO',
            'result': 'PASS' if comparison['mechanism_confirmed'] else 'FAIL'
        }
    }
    
    with open('results/comparison_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # 12. Return gate check result
    return comparison['mechanism_confirmed']

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
```

---

## Self-Validation Checklist

- [x] Codebase Analysis section included with h-e1 symbols
- [x] External Dependencies API section with verified signatures
- [x] API signatures with type hints
- [x] Tensor shapes documented
- [x] Pseudo-code for all subtasks
- [x] Subtask count within budget (8/8 used)
- [x] Total length < 600 lines
- [x] No ASCII diagrams
- [x] Main experiment flow included

---

*Logic designed for Phase 4 Implementation | h-m1 MECHANISM Hypothesis | Extends h-e1 baseline | 8 subtasks allocated*
