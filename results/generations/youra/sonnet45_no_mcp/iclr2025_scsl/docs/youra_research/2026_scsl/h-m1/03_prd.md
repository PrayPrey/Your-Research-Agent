# Product Requirements Document: h-m1 Hessian Outlier Concentration

**Hypothesis ID:** h-m1  
**Type:** MECHANISM (Step 1 of 4)  
**Date:** 2026-04-24  
**Author:** Anonymous
**Source:** Phase 2C Experiment Brief (02c_experiment_brief.md)  
**Prerequisites:** h-e1 (COMPLETED ✅)

---

## Executive Summary

This PRD defines the implementation requirements for validating the first mechanism hypothesis in the causal chain: that sharp curvature concentrates in specific Hessian eigenspace subspaces (outliers beyond Marchenko-Pastur bulk edge). Building on h-e1's validated geometric signature, we will analyze the eigenvalue spectrum structure to confirm curvature concentration in outlier subspaces.

**Key Objectives:**
1. Reuse ERM and Group-DRO trained models from h-e1 baseline
2. Compute full Hessian eigenspectrum (top-100 eigenvalues)
3. Identify outlier eigenvalues using Marchenko-Pastur bulk edge detection
4. Compare ERM vs DRO outlier concentration (count and magnitude distribution)
5. Validate MECHANISM: ERM has more outliers than DRO (sharp curvature concentrates)

**Gate Type:** MUST_WORK (mechanism link validation - breaks chain if fails)

---

## Problem Statement

### Research Question
Does sharp curvature in ERM solutions concentrate in specific Hessian outlier subspaces (beyond MP bulk edge), as opposed to being diffused across the spectrum?

### Hypothesis Statement
Under ERM training on Waterbirds, if spurious features dominate learning, then sharp curvature will concentrate in specific Hessian eigenspace subspaces (outliers beyond MP bulk edge), because Gauss-Newton decomposition shows Hessian outliers align with data structure.

### Success Impact
If validated, this provides:
- Confirmation that curvature concentration is measurable via outlier count
- Evidence that ERM creates sharper, more concentrated curvature than DRO
- Foundation for h-m2 (minority-gradient alignment to outlier subspace)

### Failure Impact
If ERM outliers ≤ DRO outliers: STOP—curvature doesn't concentrate in outliers, mechanism chain broken.

---

## Functional Requirements

### FR-1: Model Checkpoint Loading (from h-e1)
**Priority:** CRITICAL  
**Description:** Load trained ERM and Group-DRO models from h-e1 baseline

**Acceptance Criteria:**
- Load ERM checkpoint from h-e1: `../h-e1/checkpoints/erm_best.pth`
- Load DRO checkpoint from h-e1: `../h-e1/checkpoints/dro_best.pth`
- Verify models are converged (worst-group accuracy matches h-e1 results)
- Use same ResNet-50 architecture as h-e1
- No retraining required - use h-e1 converged solutions

**Technical Specifications:**
```python
import torch
import torchvision.models as models
from pathlib import Path

def load_h_e1_model(checkpoint_path: str, device: str = 'cuda') -> nn.Module:
    """
    Load trained model from h-e1 baseline
    
    Args:
        checkpoint_path: Path to h-e1 checkpoint (erm_best.pth or dro_best.pth)
        device: Device to load model on
    
    Returns:
        model: Trained ResNet-50 model
    """
    # Load architecture (same as h-e1)
    model = models.resnet50(pretrained=False)
    model.fc = nn.Linear(2048, 2)
    
    # Load weights
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    return model
```

**Dependencies:** PyTorch, torchvision, h-e1 checkpoints

**Reuse from h-e1:**
- Model architecture: ResNet-50
- Trained weights: ERM and DRO converged solutions
- Training configuration: No retraining needed

---

### FR-2: Dataset Preparation (Reused from h-e1)
**Priority:** CRITICAL  
**Description:** Use same Waterbirds dataset and preprocessing as h-e1

**Acceptance Criteria:**
- Reuse h-e1 data loading code (`data.py` module)
- Same preprocessing: resize 224×224, ImageNet normalization
- Same splits: train (4,795), val (1,199), test (5,794)
- No changes to data pipeline - exact replication for controlled comparison

**Technical Specifications:**
```python
# Reuse from h-e1/code/data.py
from h_e1.code.data import get_dataloaders, get_minority_loader

# Load data with same configuration
dataloaders = get_dataloaders(data_dir='./data/waterbird_complete95_forest2water2/', 
                               batch_size=128)
```

**Dependencies:** h-e1 data module, Waterbirds dataset (already downloaded)

**Reuse from h-e1:**
- Dataset: Waterbirds (same location)
- Preprocessing: Same transforms
- Data loading logic: Import from h-e1

---

### FR-3: Hessian Eigenspectrum Computation (Extended from h-e1)
**Priority:** CRITICAL  
**Description:** Compute Hessian eigenvalues and eigenvectors using pytorch-hessian-eigenthings

**Acceptance Criteria:**
- Compute top-100 eigenvalues (same as h-e1)
- Use power iteration with 20 steps (same as h-e1)
- Compute on full training set
- Store eigenvalues in descending order
- Store eigenvectors for future use (h-m2 will need them)

**Technical Specifications:**
```python
from hessian_eigenthings import compute_hessian_eigenthings

def compute_hessian_spectrum(model, train_loader, num_eigenthings=100):
    """
    Compute Hessian eigenspectrum (reuse h-e1 implementation)
    
    Returns:
        eigenvalues: (100,) - top eigenvalues (descending)
        eigenvectors: (P, 100) - eigenvectors (P = num parameters)
    """
    eigenvalues, eigenvectors = compute_hessian_eigenthings(
        model, 
        train_loader, 
        loss=F.cross_entropy,
        num_eigenthings=num_eigenthings,
        power_iter_steps=20,
        momentum=0.0,
        use_gpu=True
    )
    
    return eigenvalues, eigenvectors
```

**Dependencies:** pytorch-hessian-eigenthings, PyTorch

**Reuse from h-e1:**
- Hessian computation code: `hessian_analysis.py`
- Parameters: num_eigenthings=100, power_iter_steps=20
- Same computation method

---

### FR-4: Marchenko-Pastur Bulk Edge Detection (Reused from h-e1)
**Priority:** CRITICAL  
**Description:** Fit Marchenko-Pastur distribution to identify bulk edge threshold

**Acceptance Criteria:**
- Reuse h-e1 MP fitting code (`fit_marchenko_pastur` function)
- Estimate σ² and γ from eigenvalue spectrum
- Compute bulk edge λ_+ = σ²(1 + √γ)²
- Use same fitting range [20:80] as h-e1
- Validate fit quality (visual inspection)

**Technical Specifications:**
```python
# Reuse from h-e1/code/hessian_analysis.py
from h_e1.code.hessian_analysis import fit_marchenko_pastur

def detect_bulk_edge(eigenvalues):
    """
    Fit MP distribution and return bulk edge (reuse h-e1)
    
    Returns:
        bulk_edge: float - λ_+ threshold
        sigma_sq: float - noise variance
        gamma: float - aspect ratio
    """
    return fit_marchenko_pastur(eigenvalues)
```

**Dependencies:** NumPy, SciPy, h-e1 hessian_analysis module

**Reuse from h-e1:**
- MP fitting algorithm
- Fitting parameters
- Bulk edge computation

---

### FR-5: Outlier Eigenvalue Identification (NEW for h-m1)
**Priority:** CRITICAL  
**Description:** Identify and count outlier eigenvalues beyond MP bulk edge

**Acceptance Criteria:**
- Identify outliers: eigenvalues where λ > bulk_edge
- Count number of outliers for ERM and DRO
- Compute outlier statistics: max eigenvalue, mean outlier magnitude
- Compare ERM vs DRO outlier counts
- Primary metric: num_outliers_ERM vs num_outliers_DRO

**Technical Specifications:**
```python
def identify_outliers(eigenvalues: np.ndarray, bulk_edge: float) -> Dict[str, Any]:
    """
    Identify outlier eigenvalues beyond bulk edge
    
    Args:
        eigenvalues: (100,) - Hessian eigenvalues (descending)
        bulk_edge: float - Marchenko-Pastur threshold λ_+
    
    Returns:
        outlier_stats: dict with keys:
            - num_outliers: int - count of λ > bulk_edge
            - outlier_eigenvalues: array - outlier values
            - max_eigenvalue: float - largest eigenvalue
            - mean_outlier: float - average outlier magnitude
            - outlier_fraction: float - num_outliers / total
    """
    outlier_mask = eigenvalues > bulk_edge
    outlier_eigenvalues = eigenvalues[outlier_mask]
    num_outliers = len(outlier_eigenvalues)
    
    return {
        'num_outliers': num_outliers,
        'outlier_eigenvalues': outlier_eigenvalues,
        'max_eigenvalue': eigenvalues[0] if len(eigenvalues) > 0 else 0.0,
        'mean_outlier': np.mean(outlier_eigenvalues) if num_outliers > 0 else 0.0,
        'outlier_fraction': num_outliers / len(eigenvalues)
    }
```

**Dependencies:** NumPy

**NEW Implementation:** Outlier identification and statistics computation

---

### FR-6: Outlier Concentration Comparison (NEW for h-m1)
**Priority:** CRITICAL  
**Description:** Compare outlier concentration between ERM and DRO

**Acceptance Criteria:**
- Compute outlier stats for both ERM and DRO models
- Primary comparison: num_outliers_ERM > num_outliers_DRO
- Secondary metrics: max eigenvalue ratio, mean outlier ratio
- Statistical validation: t-test across seeds (if multiple runs)
- Effect size: Cohen's d for difference

**Technical Specifications:**
```python
def compare_outlier_concentration(erm_stats: Dict, dro_stats: Dict) -> Dict[str, Any]:
    """
    Compare outlier concentration between ERM and DRO
    
    Args:
        erm_stats: Outlier statistics for ERM model
        dro_stats: Outlier statistics for DRO model
    
    Returns:
        comparison: dict with:
            - num_outliers_diff: int - ERM outliers - DRO outliers
            - max_eigenvalue_ratio: float - ERM_max / DRO_max
            - mechanism_confirmed: bool - ERM outliers > DRO outliers
            - effect_size: float - Cohen's d (if multiple seeds)
    """
    num_outliers_diff = erm_stats['num_outliers'] - dro_stats['num_outliers']
    max_ratio = erm_stats['max_eigenvalue'] / dro_stats['max_eigenvalue'] if dro_stats['max_eigenvalue'] > 0 else float('inf')
    
    return {
        'num_outliers_ERM': erm_stats['num_outliers'],
        'num_outliers_DRO': dro_stats['num_outliers'],
        'num_outliers_diff': num_outliers_diff,
        'max_eigenvalue_ERM': erm_stats['max_eigenvalue'],
        'max_eigenvalue_DRO': dro_stats['max_eigenvalue'],
        'max_eigenvalue_ratio': max_ratio,
        'mechanism_confirmed': num_outliers_diff > 0,
        'percentage_increase': (num_outliers_diff / dro_stats['num_outliers'] * 100) if dro_stats['num_outliers'] > 0 else float('inf')
    }
```

**Dependencies:** Python standard library

**NEW Implementation:** Outlier comparison and mechanism validation

---

### FR-7: Eigenvalue Distribution Analysis (NEW for h-m1)
**Priority:** HIGH  
**Description:** Analyze eigenvalue distribution patterns for ERM vs DRO

**Acceptance Criteria:**
- Plot eigenvalue spectra with bulk edge overlay (both ERM and DRO)
- Histogram of outlier eigenvalues (distribution comparison)
- Cumulative eigenvalue plot (verify spectrum decay)
- Q-Q plot for MP fit validation

**Technical Specifications:**
```python
def analyze_eigenvalue_distribution(eigenvalues_erm: np.ndarray, 
                                   eigenvalues_dro: np.ndarray,
                                   bulk_edge_erm: float,
                                   bulk_edge_dro: float) -> Dict[str, np.ndarray]:
    """
    Analyze eigenvalue distribution patterns
    
    Returns:
        distributions: dict with eigenvalue histograms and cumulative sums
    """
    return {
        'erm_spectrum': eigenvalues_erm,
        'dro_spectrum': eigenvalues_dro,
        'erm_bulk_edge': bulk_edge_erm,
        'dro_bulk_edge': bulk_edge_dro,
        'erm_outliers': eigenvalues_erm[eigenvalues_erm > bulk_edge_erm],
        'dro_outliers': eigenvalues_dro[eigenvalues_dro > bulk_edge_dro]
    }
```

**Dependencies:** NumPy, matplotlib

**NEW Implementation:** Distribution analysis for mechanism validation

---

### FR-8: Visualization Generation (Extended from h-e1)
**Priority:** HIGH  
**Description:** Generate figures for outlier concentration analysis

**Acceptance Criteria:**
- Figure 1: Gate Metrics Comparison (num_outliers_ERM vs num_outliers_DRO bar chart) **[MANDATORY]**
- Figure 2: ERM vs DRO Eigenvalue Spectra (side-by-side with bulk edges)
- Figure 3: Outlier Eigenvalue Distributions (histogram comparison)
- Figure 4: MP Fit Quality (Q-Q plot for both models)
- Figure 5: Eigenvalue Decay Curves (cumulative eigenvalue plots)
- Save all figures to `{hypothesis_folder}/figures/`

**Technical Specifications:**
```python
def plot_outlier_comparison(erm_stats: Dict, dro_stats: Dict, save_path: str):
    """Bar chart: num_outliers_ERM vs num_outliers_DRO (GATE METRIC)"""
    fig, ax = plt.subplots(figsize=(8, 6))
    methods = ['ERM', 'Group-DRO']
    values = [erm_stats['num_outliers'], dro_stats['num_outliers']]
    colors = ['red', 'blue']
    
    ax.bar(methods, values, color=colors, alpha=0.7)
    ax.set_ylabel('Number of Outlier Eigenvalues (λ > λ+)')
    ax.set_title('Hessian Outlier Concentration: ERM vs Group-DRO')
    ax.set_ylim([0, max(values) * 1.2])
    
    # Add values on bars
    for i, v in enumerate(values):
        ax.text(i, v + 1, str(v), ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()

def plot_spectra_comparison(eigenvalues_erm, eigenvalues_dro, 
                            bulk_edge_erm, bulk_edge_dro, save_path):
    """Side-by-side eigenvalue spectra with bulk edges"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # ERM spectrum
    ax1.plot(range(len(eigenvalues_erm)), eigenvalues_erm, 'o-', color='red', alpha=0.6, label='ERM Eigenvalues')
    ax1.axhline(y=bulk_edge_erm, color='darkred', linestyle='--', linewidth=2, label=f'Bulk Edge (λ+ = {bulk_edge_erm:.4f})')
    ax1.set_xlabel('Eigenvalue Index')
    ax1.set_ylabel('Eigenvalue Magnitude')
    ax1.set_title('ERM Eigenvalue Spectrum')
    ax1.set_yscale('log')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # DRO spectrum
    ax2.plot(range(len(eigenvalues_dro)), eigenvalues_dro, 'o-', color='blue', alpha=0.6, label='DRO Eigenvalues')
    ax2.axhline(y=bulk_edge_dro, color='darkblue', linestyle='--', linewidth=2, label=f'Bulk Edge (λ+ = {bulk_edge_dro:.4f})')
    ax2.set_xlabel('Eigenvalue Index')
    ax2.set_ylabel('Eigenvalue Magnitude')
    ax2.set_title('Group-DRO Eigenvalue Spectrum')
    ax2.set_yscale('log')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()
```

**Dependencies:** matplotlib

**Extended from h-e1:** Reuse visualization patterns, add outlier-specific plots

---

## Non-Functional Requirements

### NFR-1: Reproducibility
**Priority:** CRITICAL  
**Description:** Ensure experiment reproducibility

**Requirements:**
- Use same seed as h-e1: 42
- Load exact h-e1 checkpoints (no retraining)
- Same Hessian computation parameters
- Save outlier statistics to CSV
- Document comparison with h-e1 results

---

### NFR-2: Performance
**Priority:** MEDIUM  
**Description:** Efficient execution on single GPU

**Requirements:**
- Single GPU execution (same as h-e1)
- No training required (load checkpoints only)
- Hessian computation: ~1-2 hours per model (2 models total)
- Total runtime: ~3-4 hours (Hessian + analysis + visualization)
- Memory usage: ≤ 12GB GPU RAM

---

### NFR-3: Logging and Monitoring
**Priority:** MEDIUM  
**Description:** Track analysis progress and metrics

**Requirements:**
- CSV logging for outlier statistics
- Save MP fitting parameters (σ², γ, bulk_edge)
- Save outlier counts and ratios
- Print progress during Hessian computation

**Technical Specifications:**
```python
def log_outlier_metrics(erm_stats, dro_stats, comparison, log_file='outlier_metrics.csv'):
    """Save outlier statistics to CSV"""
    import csv
    
    with open(log_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'ERM', 'DRO', 'Difference'])
        writer.writerow(['Num Outliers', erm_stats['num_outliers'], dro_stats['num_outliers'], comparison['num_outliers_diff']])
        writer.writerow(['Max Eigenvalue', erm_stats['max_eigenvalue'], dro_stats['max_eigenvalue'], '-'])
        writer.writerow(['Mean Outlier', erm_stats['mean_outlier'], dro_stats['mean_outlier'], '-'])
        writer.writerow(['Bulk Edge', erm_stats.get('bulk_edge'), dro_stats.get('bulk_edge'), '-'])
```

---

## Success Criteria

### Primary Gate Metric (MUST_WORK)
- **num_outliers_ERM > num_outliers_DRO** (direction confirmed)
- Expected: ERM ≈ 20-25 outliers, DRO ≈ 10-15 outliers (based on h-e1 results)

### Secondary Metrics
- Max eigenvalue ratio: ERM_max / DRO_max > 1.0
- Outlier fraction: ERM_fraction > DRO_fraction
- Visual confirmation: Eigenvalue spectra show clear separation

### Validation Against h-e1
- ERM outliers from h-e1: 23 eigenvalues (reference)
- DRO outliers from h-e1: 15 eigenvalues (reference)
- h-m1 should reproduce these values (same checkpoints)

---

## Dependencies

### External Packages
- PyTorch >= 1.12
- torchvision >= 0.13
- pytorch-hessian-eigenthings >= 0.2
- numpy >= 1.21
- scipy >= 1.7
- matplotlib >= 3.5

### Internal Dependencies (from h-e1)
- h-e1 model checkpoints: `../h-e1/checkpoints/erm_best.pth`, `../h-e1/checkpoints/dro_best.pth`
- h-e1 data module: `h_e1/code/data.py`
- h-e1 Hessian module: `h_e1/code/hessian_analysis.py`

---

## Experiment Scale

**Dataset:** Full Waterbirds training set (4,795 samples)  
**Models:** 2 (ERM, Group-DRO) - both loaded from h-e1  
**Hessian Computations:** 2 (one per model)  
**Eigenvalues per Model:** 100  
**Total Runtime:** ~3-4 hours  

This satisfies the requirement for statistically meaningful sample sizes (full training set) rather than trivially small subsets.

---

## Reuse Summary from h-e1

| Component | Reuse Status | Source |
|-----------|--------------|--------|
| Model Architecture | ✅ Full Reuse | h-e1 ResNet-50 |
| Trained Weights | ✅ Full Reuse | h-e1 checkpoints |
| Dataset | ✅ Full Reuse | h-e1 Waterbirds |
| Data Loading | ✅ Full Reuse | h-e1 data.py |
| Hessian Computation | ✅ Full Reuse | h-e1 hessian_analysis.py |
| MP Fitting | ✅ Full Reuse | h-e1 fit_marchenko_pastur |
| Outlier Identification | ❌ NEW | h-m1 specific |
| Outlier Comparison | ❌ NEW | h-m1 specific |
| Visualization | ⚠️ Extended | h-e1 + new outlier plots |

---

*PRD designed for Phase 4 Implementation | h-m1 MECHANISM Hypothesis | Building on h-e1 baseline*
