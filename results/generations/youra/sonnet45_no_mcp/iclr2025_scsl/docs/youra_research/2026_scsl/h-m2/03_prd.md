# Product Requirements Document: h-m2 Minority-Gradient Alignment Analysis

**Hypothesis ID:** h-m2  
**Type:** MECHANISM (Step 2 of 4)  
**Date:** 2026-04-24  
**Author:** Anonymous
**Source:** Phase 2C Experiment Brief (02c_experiment_brief.md)  
**Prerequisites:** h-m1 (COMPLETED ✅)

---

## Executive Summary

This PRD defines the implementation requirements for validating the second mechanism hypothesis in the causal chain: that sharp curvature directions (outlier subspace from h-m1) align with minority-group gradient directions. Building on h-m1's validated outlier concentration, we will measure alignment between minority/majority gradients and the outlier subspace to confirm the geometric-behavioral link.

**Key Objectives:**
1. Reuse ERM trained model and outlier subspace from h-m1
2. Compute minority-group gradients on Waterbirds minority samples
3. Compute majority-group gradients on Waterbirds majority samples
4. Measure alignment A(w) = ||P_S_out @ g||² / ||g||² for both groups
5. Validate MECHANISM: minority alignment > majority alignment

**Gate Type:** SHOULD_WORK (mechanism link validation - failure documented as limitation)

---

## Problem Statement

### Research Question
Do sharp curvature directions (Hessian outlier subspace) align more strongly with minority-group gradients than majority-group gradients?

### Hypothesis Statement
Under ERM training, if sharp curvature exists in outlier subspace (H-M1), then these sharp directions will align with minority-group gradient directions (high A(w)), because minority groups expose spurious correlations and their gradients point toward spurious-feature directions.

### Success Impact
If validated, this provides:
- Confirmation that sharp directions have behavioral meaning (minority alignment)
- Evidence that geometry predicts robustness (alignment correlates with worst-group accuracy)
- Foundation for h-m3 (SGD dynamics along flat vs sharp directions)

### Failure Impact
If minority alignment ≤ majority alignment: Document as limitation—explore alternative gradient definitions or minority sampling strategies.

---

## Functional Requirements

### FR-1: Model and Outlier Subspace Loading (from h-m1)
**Priority:** CRITICAL  
**Description:** Load trained ERM model and outlier eigenvectors from h-m1

**Acceptance Criteria:**
- Load ERM checkpoint from h-m1: `../h-m1/checkpoints/erm_best.pth`
- Load outlier eigenvectors from h-m1: `../h-m1/results/outlier_eigenvectors.npy`
- Verify 23 outlier eigenvectors (from h-m1 validation)
- Use same ResNet-50 architecture as h-m1
- No retraining required - use h-m1 converged solution

**Technical Specifications:**
```python
import torch
import numpy as np
import torchvision.models as models
from pathlib import Path

def load_h_m1_artifacts(device: str = 'cuda') -> Tuple[nn.Module, np.ndarray]:
    """
    Load trained ERM model and outlier subspace from h-m1
    
    Args:
        device: Device to load model on
    
    Returns:
        model: Trained ResNet-50 ERM model
        outlier_eigenvectors: (num_params, 23) outlier eigenvectors
    """
    # Load ERM model (same as h-m1)
    model = models.resnet50(pretrained=False)
    model.fc = nn.Linear(2048, 2)
    
    checkpoint_path = Path('../h-m1/checkpoints/erm_best.pth')
    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])
    model.to(device)
    model.eval()
    
    # Load outlier eigenvectors from h-m1
    outlier_path = Path('../h-m1/results/outlier_eigenvectors.npy')
    outlier_eigenvectors = np.load(outlier_path)
    
    # Verify shape: (num_params, 23)
    assert outlier_eigenvectors.shape[1] == 23, "Expected 23 outlier eigenvectors from h-m1"
    
    return model, outlier_eigenvectors
```

**Dependencies:** PyTorch, NumPy, h-m1 artifacts

**Reuse from h-m1:**
- Model: ERM ResNet-50 checkpoint
- Outlier subspace: 23 eigenvectors with eigenvalues > 2.456
- No Hessian recomputation needed

---

### FR-2: Dataset Preparation with Group Labels (Reused from h-m1/h-e1)
**Priority:** CRITICAL  
**Description:** Use Waterbirds dataset with group annotations for minority/majority sampling

**Acceptance Criteria:**
- Reuse h-m1/h-e1 data loading code
- Same preprocessing: resize 224×224, ImageNet normalization
- Access group labels: 4 groups (landbirds on land, landbirds on water, waterbirds on water, waterbirds on land)
- Identify minority groups: landbirds on water (n≈56), waterbirds on land (n≈184)
- Identify majority groups: landbirds on land (n≈3,498), waterbirds on water (n≈3,498)

**Technical Specifications:**
```python
from wilds import get_dataset
from torch.utils.data import DataLoader, Subset

def get_group_loaders(data_dir: str, batch_size: int = 128) -> Dict[str, DataLoader]:
    """
    Create DataLoaders for minority and majority groups
    
    Returns:
        loaders: dict with keys:
            - 'minority': Combined minority groups (landbirds on water + waterbirds on land)
            - 'majority': Combined majority groups (landbirds on land + waterbirds on water)
    """
    # Load Waterbirds with group annotations
    dataset = get_dataset(dataset="waterbirds", download=True, root_dir=data_dir)
    train_data = dataset.get_subset("train")
    
    # Group definitions from dataset metadata
    # Group 0: landbirds on land (majority)
    # Group 1: landbirds on water (minority)
    # Group 2: waterbirds on water (majority)
    # Group 3: waterbirds on land (minority)
    
    minority_indices = []
    majority_indices = []
    
    for idx in range(len(train_data)):
        group_id = train_data.metadata_array[idx, 0].item()  # Group ID
        if group_id in [1, 3]:  # Minority groups
            minority_indices.append(idx)
        else:  # Majority groups
            majority_indices.append(idx)
    
    # Create subset loaders
    minority_subset = Subset(train_data, minority_indices)
    majority_subset = Subset(train_data, majority_indices)
    
    minority_loader = DataLoader(minority_subset, batch_size=batch_size, shuffle=False)
    majority_loader = DataLoader(majority_subset, batch_size=batch_size, shuffle=False)
    
    return {
        'minority': minority_loader,
        'majority': majority_loader,
        'minority_count': len(minority_indices),
        'majority_count': len(majority_indices)
    }
```

**Dependencies:** WILDS dataset library, PyTorch, h-m1 data module

**Reuse from h-m1:**
- Dataset: Waterbirds (same location)
- Preprocessing: Same transforms
- Data loading base: Import from h-m1

**NEW for h-m2:**
- Group-aware sampling: Separate minority/majority loaders

---

### FR-3: Minority Gradient Computation (NEW for h-m2)
**Priority:** CRITICAL  
**Description:** Compute gradient vector on minority-group samples

**Acceptance Criteria:**
- Compute loss on minority samples only
- Backpropagate to get gradients w.r.t. all model parameters
- Flatten gradient into single vector (num_params,)
- Store gradient for alignment computation
- Use cross-entropy loss (same as training)

**Technical Specifications:**
```python
def compute_group_gradient(model: nn.Module, 
                          group_loader: DataLoader, 
                          device: str = 'cuda') -> torch.Tensor:
    """
    Compute gradient vector for a specific group
    
    Args:
        model: Trained ResNet-50 model
        group_loader: DataLoader for specific group (minority or majority)
        device: Device for computation
    
    Returns:
        gradient_flat: (num_params,) flattened gradient vector
    """
    model.eval()
    model.zero_grad()
    
    total_loss = 0.0
    num_batches = 0
    
    # Accumulate loss over all batches
    for batch_idx, (inputs, targets, metadata) in enumerate(group_loader):
        inputs = inputs.to(device)
        targets = targets.to(device)
        
        # Forward pass
        outputs = model(inputs)
        loss = F.cross_entropy(outputs, targets, reduction='sum')
        total_loss += loss
        num_batches += 1
    
    # Average loss
    avg_loss = total_loss / num_batches
    
    # Compute gradient
    avg_loss.backward()
    
    # Flatten all parameter gradients into single vector
    gradient_flat = torch.cat([
        p.grad.flatten() for p in model.parameters() if p.grad is not None
    ])
    
    return gradient_flat.cpu().numpy()
```

**Dependencies:** PyTorch

**NEW Implementation:** Gradient computation per group

---

### FR-4: Projection Matrix Construction (NEW for h-m2)
**Priority:** CRITICAL  
**Description:** Construct projection matrix P_S_out = V @ V^T from outlier eigenvectors

**Acceptance Criteria:**
- Use 23 outlier eigenvectors from h-m1
- Compute projection matrix: P = V @ V^T
- Verify projection is symmetric: P = P^T
- Verify projection is idempotent: P @ P = P (within numerical tolerance)
- Store projection matrix for reuse

**Technical Specifications:**
```python
def construct_projection_matrix(outlier_eigenvectors: np.ndarray) -> np.ndarray:
    """
    Construct projection matrix onto outlier subspace
    
    Args:
        outlier_eigenvectors: (num_params, 23) - eigenvectors from h-m1
    
    Returns:
        P: (num_params, num_params) - projection matrix
    
    Note: For large num_params, this is memory-intensive.
          Alternative: compute projection on-the-fly as V @ (V^T @ g)
    """
    # Memory-efficient approach: don't materialize full P matrix
    # Instead, compute projection on-the-fly in compute_alignment()
    
    # Verification only (for small test)
    # P = outlier_eigenvectors @ outlier_eigenvectors.T
    # assert np.allclose(P, P.T), "Projection matrix should be symmetric"
    # assert np.allclose(P @ P, P, atol=1e-4), "Projection should be idempotent"
    
    return outlier_eigenvectors  # Return V for on-the-fly projection
```

**Dependencies:** NumPy

**NEW Implementation:** Projection matrix construction

---

### FR-5: Alignment Metric Computation (NEW for h-m2)
**Priority:** CRITICAL  
**Description:** Compute alignment A(w) = ||P @ g||² / ||g||² for minority and majority gradients

**Acceptance Criteria:**
- Compute alignment for minority gradient: A_minority
- Compute alignment for majority gradient: A_majority
- Verify alignment ∈ [0, 1] (fraction of gradient in subspace)
- Compute difference: Δ_align = A_minority - A_majority
- Primary metric: Δ_align > 0 (minority aligns more with outliers)

**Technical Specifications:**
```python
def compute_alignment(gradient: np.ndarray, 
                     outlier_eigenvectors: np.ndarray) -> float:
    """
    Compute alignment A(w) = ||P @ g||² / ||g||²
    
    Uses memory-efficient on-the-fly projection: P @ g = V @ (V^T @ g)
    
    Args:
        gradient: (num_params,) gradient vector
        outlier_eigenvectors: (num_params, 23) eigenvectors
    
    Returns:
        alignment: float in [0, 1]
    """
    # On-the-fly projection: P @ g = V @ (V^T @ g)
    V = outlier_eigenvectors
    VT_g = V.T @ gradient  # (23,)
    projected = V @ VT_g   # (num_params,)
    
    # Compute alignment
    numerator = np.sum(projected ** 2)  # ||P @ g||²
    denominator = np.sum(gradient ** 2)  # ||g||²
    
    alignment = numerator / (denominator + 1e-10)  # Avoid division by zero
    
    # Verify range [0, 1]
    assert 0 <= alignment <= 1, f"Alignment {alignment} out of bounds [0, 1]"
    
    return alignment


def compare_alignments(minority_gradient: np.ndarray,
                      majority_gradient: np.ndarray,
                      outlier_eigenvectors: np.ndarray) -> Dict[str, float]:
    """
    Compare minority vs majority gradient alignment
    
    Returns:
        comparison: dict with:
            - A_minority: float - minority alignment
            - A_majority: float - majority alignment
            - delta_align: float - difference (minority - majority)
            - mechanism_confirmed: bool - delta_align > 0
    """
    A_minority = compute_alignment(minority_gradient, outlier_eigenvectors)
    A_majority = compute_alignment(majority_gradient, outlier_eigenvectors)
    delta_align = A_minority - A_majority
    
    return {
        'A_minority': A_minority,
        'A_majority': A_majority,
        'delta_align': delta_align,
        'mechanism_confirmed': delta_align > 0,
        'percentage_difference': (delta_align / A_majority * 100) if A_majority > 0 else float('inf')
    }
```

**Dependencies:** NumPy

**NEW Implementation:** Alignment metric computation and comparison

---

### FR-6: Correlation Analysis with Worst-Group Accuracy (NEW for h-m2)
**Priority:** HIGH  
**Description:** Test correlation between alignment and worst-group accuracy

**Acceptance Criteria:**
- Compute worst-group accuracy from h-m1/h-e1 results
- Compute Spearman correlation: ρ(A_minority, WGA)
- Expected: negative correlation (higher alignment = worse robustness)
- Report p-value for statistical significance
- Secondary validation of geometric-behavioral link

**Technical Specifications:**
```python
from scipy.stats import spearmanr

def analyze_alignment_robustness_correlation(alignment_values: np.ndarray,
                                            wga_values: np.ndarray) -> Dict[str, float]:
    """
    Compute correlation between alignment and worst-group accuracy
    
    Args:
        alignment_values: (n_seeds,) - A_minority values across seeds
        wga_values: (n_seeds,) - worst-group accuracy values
    
    Returns:
        correlation: dict with rho, p_value, interpretation
    """
    rho, p_value = spearmanr(alignment_values, wga_values)
    
    return {
        'spearman_rho': rho,
        'p_value': p_value,
        'significant': p_value < 0.01,
        'expected_negative': rho < 0,
        'interpretation': 'Higher alignment correlates with worse robustness' if rho < -0.3 else 'Weak or no correlation'
    }
```

**Dependencies:** SciPy

**NEW Implementation:** Correlation analysis

---

### FR-7: Per-Group Alignment Breakdown (NEW for h-m2)
**Priority:** MEDIUM  
**Description:** Analyze alignment for all 4 Waterbirds groups individually

**Acceptance Criteria:**
- Compute alignment for each group: landbirds on land, landbirds on water, waterbirds on water, waterbirds on land
- Verify minority groups (1, 3) have higher alignment than majority groups (0, 2)
- Identify which minority group has highest alignment
- Report alignment distribution across groups

**Technical Specifications:**
```python
def compute_per_group_alignments(model: nn.Module,
                                 dataset: Dataset,
                                 outlier_eigenvectors: np.ndarray,
                                 device: str = 'cuda') -> Dict[int, float]:
    """
    Compute alignment for each of 4 Waterbirds groups
    
    Returns:
        group_alignments: dict mapping group_id to alignment value
            0: landbirds on land (majority)
            1: landbirds on water (minority)
            2: waterbirds on water (majority)
            3: waterbirds on land (minority)
    """
    group_alignments = {}
    
    for group_id in range(4):
        # Get indices for this group
        group_indices = [idx for idx in range(len(dataset)) 
                        if dataset.metadata_array[idx, 0].item() == group_id]
        
        # Create loader for this group
        group_subset = Subset(dataset, group_indices)
        group_loader = DataLoader(group_subset, batch_size=128, shuffle=False)
        
        # Compute gradient for this group
        gradient = compute_group_gradient(model, group_loader, device)
        
        # Compute alignment
        alignment = compute_alignment(gradient, outlier_eigenvectors)
        
        group_alignments[group_id] = alignment
    
    return group_alignments
```

**Dependencies:** PyTorch, NumPy

**NEW Implementation:** Per-group analysis

---

### FR-8: Visualization Generation (NEW for h-m2)
**Priority:** HIGH  
**Description:** Generate figures for minority-gradient alignment analysis

**Acceptance Criteria:**
- Figure 1: Gate Metrics Comparison (A_minority vs A_majority bar chart) **[MANDATORY]**
- Figure 2: Alignment Distribution (histogram of alignment values)
- Figure 3: Correlation Analysis (scatter plot: A_minority vs WGA)
- Figure 4: Gradient Projection Visualization (projection magnitude comparison)
- Figure 5: Per-Group Alignment Breakdown (4 bars for 4 groups)
- Figure 6: Alignment vs Eigenvalue Spectrum (contribution by eigenvalue rank)
- Save all figures to `{hypothesis_folder}/figures/`

**Technical Specifications:**
```python
import matplotlib.pyplot as plt

def plot_alignment_comparison(comparison: Dict, save_path: str):
    """Bar chart: A_minority vs A_majority (GATE METRIC)"""
    fig, ax = plt.subplots(figsize=(8, 6))
    groups = ['Minority\nGradient', 'Majority\nGradient']
    values = [comparison['A_minority'], comparison['A_majority']]
    colors = ['darkred', 'darkblue']
    
    bars = ax.bar(groups, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Alignment A(w) = ||P @ g||² / ||g||²', fontsize=12)
    ax.set_title('Minority vs Majority Gradient Alignment to Outlier Subspace', fontsize=14, fontweight='bold')
    ax.set_ylim([0, max(values) * 1.2])
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add values on bars
    for i, (bar, v) in enumerate(zip(bars, values)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{v:.4f}', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Add difference annotation
    delta = comparison['delta_align']
    ax.text(0.5, max(values) * 1.1, f'Δ = {delta:.4f}', 
            ha='center', fontsize=11, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_per_group_alignments(group_alignments: Dict[int, float], save_path: str):
    """Bar chart: Alignment for all 4 Waterbirds groups"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    group_names = [
        'Landbirds\non Land\n(Majority)',
        'Landbirds\non Water\n(Minority)',
        'Waterbirds\non Water\n(Majority)',
        'Waterbirds\non Land\n(Minority)'
    ]
    
    values = [group_alignments[i] for i in range(4)]
    colors = ['blue', 'red', 'blue', 'red']  # Red for minority, blue for majority
    
    bars = ax.bar(group_names, values, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    ax.set_ylabel('Alignment A(w)', fontsize=12)
    ax.set_title('Per-Group Gradient Alignment to Outlier Subspace', fontsize=14, fontweight='bold')
    ax.set_ylim([0, max(values) * 1.2])
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add values on bars
    for bar, v in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                f'{v:.4f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()


def plot_correlation_analysis(alignment_values: np.ndarray, 
                              wga_values: np.ndarray,
                              correlation: Dict,
                              save_path: str):
    """Scatter plot: A_minority vs worst-group accuracy"""
    fig, ax = plt.subplots(figsize=(8, 6))
    
    ax.scatter(alignment_values, wga_values, s=100, alpha=0.6, edgecolors='black', linewidth=1.5)
    ax.set_xlabel('Minority Gradient Alignment A_minority', fontsize=12)
    ax.set_ylabel('Worst-Group Accuracy (%)', fontsize=12)
    ax.set_title('Alignment vs Robustness Correlation', fontsize=14, fontweight='bold')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Add correlation annotation
    rho = correlation['spearman_rho']
    p_val = correlation['p_value']
    ax.text(0.05, 0.95, f"Spearman ρ = {rho:.3f}\np = {p_val:.4f}",
            transform=ax.transAxes, fontsize=11, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Add trend line
    z = np.polyfit(alignment_values, wga_values, 1)
    p = np.poly1d(z)
    ax.plot(alignment_values, p(alignment_values), "r--", alpha=0.8, linewidth=2)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
```

**Dependencies:** matplotlib, NumPy

**NEW Implementation:** h-m2 specific visualizations

---

## Non-Functional Requirements

### NFR-1: Reproducibility
**Priority:** CRITICAL  
**Description:** Ensure experiment reproducibility

**Requirements:**
- Use exact h-m1 checkpoint (no retraining)
- Use same seed as h-m1: 42
- Same gradient computation parameters
- Save alignment statistics to CSV
- Document comparison with h-m1 results

---

### NFR-2: Performance
**Priority:** HIGH  
**Description:** Efficient execution on single GPU

**Requirements:**
- Single GPU execution (same as h-m1)
- No training required (load checkpoint only)
- Gradient computation: ~30 seconds (2 gradients: minority + majority)
- Alignment computation: ~5 seconds
- Total runtime: ~1-2 minutes (vs hours for h-m1 Hessian computation)
- Memory usage: ≤ 8GB GPU RAM

---

### NFR-3: Logging and Monitoring
**Priority:** MEDIUM  
**Description:** Track analysis progress and metrics

**Requirements:**
- CSV logging for alignment statistics
- Save alignment values (A_minority, A_majority, delta)
- Save per-group alignments
- Print progress during gradient computation

**Technical Specifications:**
```python
def log_alignment_metrics(comparison: Dict, 
                         group_alignments: Dict,
                         log_file: str = 'alignment_metrics.csv'):
    """Save alignment statistics to CSV"""
    import csv
    
    with open(log_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['A_minority', comparison['A_minority']])
        writer.writerow(['A_majority', comparison['A_majority']])
        writer.writerow(['Delta_align', comparison['delta_align']])
        writer.writerow(['Mechanism_confirmed', comparison['mechanism_confirmed']])
        writer.writerow([''])
        writer.writerow(['Per-Group Alignments', ''])
        for group_id, alignment in group_alignments.items():
            writer.writerow([f'Group {group_id}', alignment])
```

---

## Success Criteria

### Primary Gate Metric (SHOULD_WORK)
- **A_minority > A_majority** (directional validation)
- Expected: Δ_align > 0.1 (meaningful difference)
- Interpretation: Minority gradients align more with sharp outlier directions

### Secondary Metrics
- Correlation: Spearman ρ(A_minority, WGA) < -0.3 (negative correlation)
- Per-group validation: Both minority groups (1, 3) show higher alignment than majority groups (0, 2)
- Visual confirmation: Clear separation in alignment bar chart

### Expected Results from Phase 2C
- ERM A_minority: ~0.6-0.8 (high alignment with outliers)
- ERM A_majority: ~0.3-0.5 (lower alignment)
- Δ_align: ~0.2-0.3 (minority gradients point toward sharp directions)

---

## Dependencies

### External Packages
- PyTorch >= 1.12
- torchvision >= 0.13
- numpy >= 1.21
- scipy >= 1.7
- matplotlib >= 3.5
- wilds >= 2.0 (for Waterbirds dataset with group labels)

### Internal Dependencies (from h-m1)
- h-m1 model checkpoint: `../h-m1/checkpoints/erm_best.pth`
- h-m1 outlier eigenvectors: `../h-m1/results/outlier_eigenvectors.npy`
- h-m1 data module: `h_m1/code/data.py`
- h-m1 Waterbirds dataset: Same location as h-m1

---

## Experiment Scale

**Dataset:** Full Waterbirds training set (4,795 samples)  
- Minority samples: ~240 (landbirds on water + waterbirds on land)
- Majority samples: ~4,555 (landbirds on land + waterbirds on water)

**Models:** 1 (ERM only) - loaded from h-m1  
**Gradient Computations:** 2 (minority + majority)  
**Alignment Computations:** 2 (minority + majority) + 4 (per-group analysis)  
**Total Runtime:** ~1-2 minutes  

This satisfies the requirement for statistically meaningful sample sizes (full training set) rather than trivially small subsets.

---

## Reuse Summary from h-m1

| Component | Reuse Status | Source |
|-----------|--------------|--------|
| Model Architecture | ✅ Full Reuse | h-m1 ResNet-50 |
| Trained Weights | ✅ Full Reuse | h-m1 ERM checkpoint |
| Outlier Subspace | ✅ Full Reuse | h-m1 23 eigenvectors |
| Dataset | ✅ Full Reuse | h-m1 Waterbirds |
| Data Loading Base | ✅ Full Reuse | h-m1 data.py |
| Minority Gradient Computation | ❌ NEW | h-m2 specific |
| Alignment Metric | ❌ NEW | h-m2 specific |
| Per-Group Analysis | ❌ NEW | h-m2 specific |
| Visualization | ❌ NEW | h-m2 specific |

---

*PRD designed for Phase 4 Implementation | h-m2 MECHANISM Hypothesis | Building on h-m1 outlier subspace*
