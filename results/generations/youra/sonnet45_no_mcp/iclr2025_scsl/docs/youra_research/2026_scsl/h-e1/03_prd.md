# Product Requirements Document: h-e1 Curvature Subspace Alignment

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-04-24  
**Author:** Anonymous
**Source:** Phase 2C Experiment Brief (02c_experiment_brief.md)

---

## Executive Summary

This PRD defines the implementation requirements for validating the foundational hypothesis that ERM and Group-DRO training produce solutions with geometrically distinct curvature properties. On the Waterbirds dataset, we will measure Marchenko-Pastur-defined curvature subspace alignment A(w) to determine if ERM solutions exhibit significantly higher alignment than Group-DRO solutions.

**Key Objectives:**
1. Train ResNet-50 models using ERM and Group-DRO on Waterbirds dataset
2. Compute Hessian eigenspectrum and identify Marchenko-Pastur bulk edge
3. Measure curvature subspace alignment A(w) = ||P_S_out g_minority||² / ||g_minority||²
4. Validate significant difference between ERM and DRO alignment (direction-based PoC)

**Gate Type:** MUST_WORK (foundational geometric signature validation)

---

## Problem Statement

### Research Question
Do ERM and Group-DRO solutions occupy geometrically distinct regions in loss landscape, measurable via Marchenko-Pastur-defined curvature subspace alignment?

### Hypothesis Statement
Under standard ERM and Group-DRO training on Waterbirds, if we measure Marchenko-Pastur-defined curvature subspace alignment A(w), then ERM solutions will exhibit significantly higher alignment than Group-DRO solutions, because ERM exploits spurious features that create sharp, concentrated curvature.

### Success Impact
If validated, this provides:
- First geometric signature differentiating spurious vs robust solutions
- Marchenko-Pastur-based outlier subspace definition for curvature analysis
- Foundation for mechanism hypotheses (h-m1 through h-m4)

### Failure Impact
If A(w)_ERM ≤ A(w)_DRO: STOP—geometric signature doesn't exist, abandon entire hypothesis chain.

---

## Functional Requirements

### FR-1: Dataset Preparation
**Priority:** CRITICAL  
**Description:** Download and prepare the Waterbirds dataset with standard preprocessing

**Acceptance Criteria:**
- Download Waterbirds from Group DRO repository (https://github.com/kohpangwei/group_DRO)
- Verify dataset structure: train (4,795), val (1,199), test (5,794) images
- Implement preprocessing: resize to 224×224, normalize with ImageNet stats
- Training augmentation: RandomHorizontalFlip, RandomCrop(224, padding=4)
- Validation/test: no augmentation
- Preserve ground truth group labels for minority-group gradient computation

**Technical Specifications:**
```python
# Dataset loading from Group DRO repository
# Follow official data preparation script
# Dataset path: ./data/waterbird_complete95_forest2water2/

train_transforms = transforms.Compose([
    transforms.RandomHorizontalFlip(),
    transforms.RandomCrop(224, padding=4),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                        std=[0.229, 0.224, 0.225])
])

eval_transforms = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                        std=[0.229, 0.224, 0.225])
])
```

**Dependencies:** PyTorch, torchvision, Group DRO repository scripts

---

### FR-2: ERM Baseline Model
**Priority:** CRITICAL  
**Description:** Implement standard ERM training with ResNet-50

**Acceptance Criteria:**
- Load ResNet-50 from torchvision with ImageNet pretrained weights
- Modify final FC layer: 2048 → 2 classes (landbird, waterbird)
- Train with SGD: momentum=0.9, weight_decay=1e-4, LR=0.001
- Learning rate schedule: MultiStepLR with milestones=[60, 80], gamma=0.1
- Total epochs: 100 (early stopping patience=10 on worst-group accuracy)
- Batch size: 128 (test also with 32, 512 for stability validation)
- Loss: CrossEntropyLoss (standard ERM, no group reweighting)
- Fixed seed: 42

**Expected Performance:**
- Average accuracy: ~85-90% on test set
- Worst-group accuracy: ~60-75% (minority groups)

**Technical Specifications:**
```python
import torchvision.models as models
erm_model = models.resnet50(pretrained=True)
erm_model.fc = nn.Linear(2048, 2)

optimizer = optim.SGD(erm_model.parameters(), 
                      lr=0.001, momentum=0.9, weight_decay=1e-4)
scheduler = optim.lr_scheduler.MultiStepLR(optimizer, 
                                           milestones=[60, 80], gamma=0.1)
criterion = nn.CrossEntropyLoss()
```

**Dependencies:** PyTorch, torchvision

---

### FR-3: Group-DRO Baseline Model
**Priority:** CRITICAL  
**Description:** Implement Group-DRO training with ResNet-50

**Acceptance Criteria:**
- Same architecture as ERM model (ResNet-50)
- Same hyperparameters (SGD, LR schedule, epochs)
- Group-balanced loss: minimize worst-group loss
- Requires group labels during training
- Track per-group loss and accuracy

**Expected Performance:**
- Worst-group accuracy: ~75-80%
- Average accuracy: ~75-80% (lower than ERM)

**Technical Specifications:**
```python
# Group-DRO loss computation
def compute_group_dro_loss(outputs, labels, groups, group_weights):
    """
    Compute group-balanced loss for DRO training
    
    Args:
        outputs: (B, 2) - model predictions
        labels: (B,) - true labels
        groups: (B,) - group indices (0-3)
        group_weights: (4,) - per-group weights
    
    Returns:
        loss: scalar - weighted group loss
    """
    group_losses = []
    for g in range(4):
        mask = (groups == g)
        if mask.sum() > 0:
            g_loss = F.cross_entropy(outputs[mask], labels[mask])
            group_losses.append(g_loss * group_weights[g])
    
    return sum(group_losses) / len(group_losses)
```

**Dependencies:** PyTorch

---

### FR-4: Hessian Computation Module
**Priority:** CRITICAL  
**Description:** Compute Hessian eigenspectrum using pytorch-hessian-eigenthings

**Acceptance Criteria:**
- Compute top 100 Hessian eigenvalues and eigenvectors
- Use power iteration with deflation
- Compute on full training set (or representative subset)
- Store eigenvalues for Marchenko-Pastur fitting
- Store eigenvectors for subspace projection

**Technical Specifications:**
```python
from hessian_eigenthings import compute_hessian_eigenthings

def compute_hessian_spectrum(model, train_loader):
    """
    Compute Hessian eigenspectrum
    
    Args:
        model: Trained ResNet-50 model
        train_loader: Training data loader
    
    Returns:
        eigenvalues: (100,) - top eigenvalues
        eigenvectors: (P, 100) - eigenvectors (P = num parameters)
    """
    eigenvalues, eigenvectors = compute_hessian_eigenthings(
        model, 
        train_loader, 
        loss=F.cross_entropy,
        num_eigenthings=100, 
        power_iter_steps=20, 
        momentum=0.0,
        use_gpu=True
    )
    
    return eigenvalues, eigenvectors
```

**Dependencies:** pytorch-hessian-eigenthings, PyTorch

---

### FR-5: Marchenko-Pastur Bulk Edge Estimation
**Priority:** CRITICAL  
**Description:** Fit Marchenko-Pastur distribution to identify bulk edge threshold

**Acceptance Criteria:**
- Estimate noise variance σ² and aspect ratio γ from eigenvalue spectrum
- Compute bulk edge λ_+ = σ²(1 + √γ)²
- Validate fit quality (visual inspection of spectrum vs MP distribution)
- Identify outlier eigenvalues (λ > λ_+)

**Technical Specifications:**
```python
import numpy as np
from scipy.optimize import minimize

def fit_marchenko_pastur(eigenvalues):
    """
    Fit Marchenko-Pastur distribution and return bulk edge
    
    Args:
        eigenvalues: (100,) - Hessian eigenvalues (descending order)
    
    Returns:
        bulk_edge: float - λ_+ threshold
        sigma_sq: float - noise variance estimate
        gamma: float - aspect ratio estimate
    """
    # Filter out obvious outliers for fitting (use middle portion)
    bulk_eigs = eigenvalues[eigenvalues.argsort()[20:80]]
    
    # Maximum likelihood estimation for σ² and γ
    def mp_likelihood(params):
        sigma_sq, gamma = params
        lambda_min = sigma_sq * (1 - np.sqrt(gamma))**2
        lambda_max = sigma_sq * (1 + np.sqrt(gamma))**2
        
        # Marchenko-Pastur density (simplified)
        density = np.sqrt((lambda_max - bulk_eigs) * (bulk_eigs - lambda_min))
        density /= (2 * np.pi * sigma_sq * gamma * bulk_eigs)
        
        return -np.sum(np.log(density + 1e-8))
    
    # Optimize
    result = minimize(mp_likelihood, x0=[1.0, 0.1], bounds=[(0.01, 10), (0.01, 1)])
    sigma_sq, gamma = result.x
    
    # Compute bulk edge
    bulk_edge = sigma_sq * (1 + np.sqrt(gamma))**2
    
    return bulk_edge, sigma_sq, gamma
```

**Dependencies:** NumPy, SciPy

---

### FR-6: Minority-Group Gradient Computation
**Priority:** CRITICAL  
**Description:** Compute average gradient on minority group samples

**Acceptance Criteria:**
- Identify minority groups from dataset (e.g., landbird-water, waterbird-land)
- Compute gradients on minority samples
- Flatten and concatenate all parameter gradients
- Normalize gradient vector

**Technical Specifications:**
```python
def compute_minority_gradient(model, minority_loader):
    """
    Compute average gradient on minority group samples
    
    Args:
        model: Trained model (frozen)
        minority_loader: DataLoader with minority group samples
    
    Returns:
        g_minority: (P,) - flattened parameter gradient vector
    """
    model.eval()
    total_grad = None
    count = 0
    
    for inputs, labels, groups in minority_loader:
        inputs, labels = inputs.cuda(), labels.cuda()
        
        # Forward pass
        outputs = model(inputs)
        loss = F.cross_entropy(outputs, labels)
        
        # Backward pass
        model.zero_grad()
        loss.backward()
        
        # Accumulate gradients
        if total_grad is None:
            total_grad = [p.grad.detach().clone() for p in model.parameters() if p.grad is not None]
        else:
            for i, p in enumerate([p for p in model.parameters() if p.grad is not None]):
                total_grad[i] += p.grad.detach()
        
        count += 1
    
    # Average and flatten
    total_grad = [g / count for g in total_grad]
    g_minority = torch.cat([g.flatten() for g in total_grad])
    
    return g_minority
```

**Dependencies:** PyTorch

---

### FR-7: Curvature Subspace Alignment A(w)
**Priority:** CRITICAL  
**Description:** Compute alignment metric A(w) = ||P_S_out g_minority||² / ||g_minority||²

**Acceptance Criteria:**
- Define outlier subspace S_out (eigenvectors with λ > bulk_edge)
- Project minority gradient onto outlier subspace
- Compute alignment as fraction of gradient norm in outlier subspace
- Compare ERM vs DRO alignment

**Technical Specifications:**
```python
def compute_alignment(g_minority, eigenvectors, eigenvalues, bulk_edge):
    """
    Compute curvature subspace alignment A(w)
    
    Args:
        g_minority: (P,) - minority gradient vector
        eigenvectors: (P, 100) - Hessian eigenvectors
        eigenvalues: (100,) - Hessian eigenvalues
        bulk_edge: float - Marchenko-Pastur threshold
    
    Returns:
        alignment: float - A(w) metric
    """
    # Identify outlier subspace
    outlier_mask = eigenvalues > bulk_edge
    outlier_eigenvectors = eigenvectors[:, outlier_mask]  # (P, K)
    
    # Project minority gradient onto outlier subspace
    # P_S_out g = sum_i (g · v_i) * v_i
    projection = torch.matmul(
        outlier_eigenvectors, 
        torch.matmul(outlier_eigenvectors.T, g_minority)
    )
    
    # Compute alignment
    alignment = (projection.norm() ** 2) / (g_minority.norm() ** 2)
    
    return alignment.item()
```

**Dependencies:** PyTorch

---

### FR-8: Evaluation Metrics Implementation
**Priority:** CRITICAL  
**Description:** Compare alignment metrics between ERM and DRO

**Acceptance Criteria:**
- Compute A(w)_ERM and A(w)_DRO
- Direction-based comparison: A(w)_ERM > A(w)_DRO (PoC success criterion)
- Record worst-group accuracy for both methods
- Record average accuracy for both methods

**Technical Specifications:**
```python
def evaluate_alignment(erm_alignment, dro_alignment):
    """
    Evaluate PoC success based on alignment comparison
    
    Returns:
        success: bool - True if ERM > DRO (direction confirmed)
        metrics: dict - all computed metrics
    """
    success = erm_alignment > dro_alignment
    
    metrics = {
        'A_w_ERM': erm_alignment,
        'A_w_DRO': dro_alignment,
        'difference': erm_alignment - dro_alignment,
        'ratio': erm_alignment / dro_alignment if dro_alignment > 0 else float('inf'),
        'direction_confirmed': success
    }
    
    return success, metrics
```

**Dependencies:** Python standard library

---

### FR-9: Visualization Generation
**Priority:** HIGH  
**Description:** Generate figures for curvature analysis and alignment comparison

**Acceptance Criteria:**
- Figure 1: Gate Metrics Comparison (A(w)_ERM vs A(w)_DRO bar chart)
- Figure 2: Hessian Eigenvalue Spectrum with MP bulk edge overlay
- Figure 3: Worst-Group Accuracy vs Alignment scatter plot
- Figure 4: Training Curves (loss, accuracy over epochs) for ERM and DRO
- Figure 5: Per-Group Accuracy Heatmap (4 groups × 2 methods)
- Save all figures to `{hypothesis_folder}/figures/`

**Technical Specifications:**
```python
import matplotlib.pyplot as plt

def plot_alignment_comparison(erm_alignment, dro_alignment, save_path):
    """Bar chart: A(w)_ERM vs A(w)_DRO"""
    fig, ax = plt.subplots(figsize=(8, 6))
    methods = ['ERM', 'Group-DRO']
    values = [erm_alignment, dro_alignment]
    colors = ['red', 'blue']
    
    ax.bar(methods, values, color=colors, alpha=0.7)
    ax.set_ylabel('Alignment A(w)')
    ax.set_title('Curvature Subspace Alignment: ERM vs Group-DRO')
    ax.set_ylim([0, max(values) * 1.2])
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def plot_hessian_spectrum(eigenvalues, bulk_edge, save_path):
    """Eigenvalue spectrum with MP bulk edge"""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(range(len(eigenvalues)), eigenvalues, 'o-', label='Hessian Eigenvalues')
    ax.axhline(y=bulk_edge, color='red', linestyle='--', linewidth=2, 
               label=f'MP Bulk Edge (λ+ = {bulk_edge:.4f})')
    ax.set_xlabel('Eigenvalue Index')
    ax.set_ylabel('Eigenvalue Magnitude')
    ax.set_title('Hessian Eigenvalue Spectrum')
    ax.set_yscale('log')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
```

**Dependencies:** matplotlib

---

## Non-Functional Requirements

### NFR-1: Reproducibility
**Priority:** CRITICAL  
**Description:** Ensure experiment reproducibility

**Requirements:**
- Set fixed random seed: 42 (PyTorch, NumPy, Python random)
- Log all hyperparameters to config file (hardcoded or argparse for LIGHT tier)
- Save model checkpoints: best worst-group accuracy for ERM and DRO
- Save Hessian eigenvalues and eigenvectors
- Document exact package versions

---

### NFR-2: Performance
**Priority:** MEDIUM  
**Description:** Efficient execution on single GPU

**Requirements:**
- Single GPU execution (set CUDA_VISIBLE_DEVICES to empty GPU)
- Batch size: 128 (fits in typical GPU memory for ResNet-50)
- Training time: ~3-4 hours per model (2 models total)
- Hessian computation: ~1-2 hours (100 eigenthings)
- Memory usage: ≤ 12GB GPU RAM

---

### NFR-3: Logging and Monitoring
**Priority:** MEDIUM  
**Description:** Track training progress and metrics

**Requirements:**
- Print-based logging for PoC (minimal infrastructure for LIGHT tier)
- Save metrics to CSV: epoch, train_loss, val_loss, val_acc, worst_group_acc
- Save alignment metrics: A(w)_ERM, A(w)_DRO
- Save Hessian statistics: num_outliers, bulk_edge, top_eigenvalue

**Technical Specifications:**
```python
# Minimal CSV logging for LIGHT tier
import csv

def log_training_metrics(epoch, metrics, log_file='training_log.csv'):
    with open(log_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=metrics.keys())
        if epoch == 1:
            writer.writeheader()
        writer.writerow(metrics)

def log_alignment_metrics(metrics, log_file='alignment_results.csv'):
    with open(log_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=metrics.keys())
        writer.writeheader()
        writer.writerow(metrics)
```

---

### NFR-4: Code Quality
**Priority:** MEDIUM  
**Description:** Clean, readable code with basic testing

**Requirements:**
- Smoke test: Run 1 epoch on small subset (100 samples) to verify no crashes
- Modular structure: separate files for data, model, training, hessian analysis
- Inline comments for Marchenko-Pastur fitting logic
- No complex abstractions (LIGHT tier - hardcoded configs acceptable)

---

## Dependencies and Environment

### Software Dependencies
```
python >= 3.8
torch >= 1.10.0
torchvision >= 0.11.0
numpy >= 1.21.0
scipy >= 1.7.0
matplotlib >= 3.4.0
pytorch-hessian-eigenthings
```

### Hardware Requirements
- GPU: NVIDIA GPU with ≥ 12GB VRAM (for ResNet-50 + Hessian computation)
- CPU: Any modern multi-core processor
- RAM: ≥ 16GB
- Storage: ≥ 15GB for dataset, checkpoints, and Hessian data

### Environment Setup
```bash
# Create conda environment
conda create -n h-e1 python=3.8
conda activate h-e1

# Install PyTorch with CUDA
conda install pytorch torchvision cudatoolkit=11.3 -c pytorch

# Install other dependencies
pip install numpy scipy matplotlib
pip install git+https://github.com/noahgolmant/pytorch-hessian-eigenthings.git

# Set GPU (use nvidia-smi to find empty GPU)
export CUDA_VISIBLE_DEVICES=1  # Example: GPU 1 is empty
```

---

## Success Criteria

### Primary Success Criteria (PoC: Direction-based)
1. **A(w)_ERM > A(w)_DRO**: ERM alignment higher than DRO alignment (geometric signature exists)
2. **Code runs without error**: Both models train to convergence, Hessian computation completes

### PoC Pass Criteria
- Code executes successfully
- Both ERM and DRO models converge
- Hessian eigenspectrum computed successfully
- Marchenko-Pastur bulk edge estimation stable
- A(w)_ERM > A(w)_DRO (direction confirmed)

**Note:** For PoC, statistical significance (p<0.01, Cohen's d>0.8) is NOT required. Simple directional comparison suffices.

### What "Failure" Means
- A(w)_ERM ≤ A(w)_DRO → No geometric signature, STOP hypothesis chain
- Hessian computation fails or unstable
- Marchenko-Pastur fitting fails (no clear bulk edge)

### Gate Decision
- **PASS**: A(w)_ERM > A(w)_DRO → Proceed to h-m1 (mechanism hypotheses)
- **FAIL**: A(w)_ERM ≤ A(w)_DRO → STOP entire hypothesis chain

---

## Out of Scope

The following are explicitly out of scope for this PoC:

- Statistical significance testing (PoC uses single seed, direction-based)
- Multiple random seeds (20 seeds for full verification, not PoC)
- Batch size ablation (test 32, 128, 512 only if time permits)
- CelebA and Colored MNIST cross-validation (Waterbirds only for PoC)
- Hyperparameter tuning / grid search
- Mode connectivity analysis (FGE) - reserved for h-m3, h-m4
- Comparison with other baselines (JTT, LISA, etc.) - Phase 5 only
- Advanced Hessian approximations (KFAC, etc.)
- Distributed training / multi-GPU

---

## Timeline and Milestones

**Note:** Per workflow rules, no time estimates provided. Milestones listed in logical sequence.

**Milestone 1:** Environment Setup
- Dependencies installed
- Dataset downloaded and verified
- GPU selected

**Milestone 2:** ERM Training
- ResNet-50 trained with standard ERM
- Checkpoint saved

**Milestone 3:** Group-DRO Training
- ResNet-50 trained with Group-DRO
- Checkpoint saved

**Milestone 4:** Hessian Computation
- Hessian eigenspectrum computed for both models
- Eigenvalues and eigenvectors saved

**Milestone 5:** Marchenko-Pastur Analysis
- Bulk edge estimated
- Outlier subspace defined

**Milestone 6:** Alignment Computation
- Minority gradients computed
- A(w) metrics calculated for ERM and DRO

**Milestone 7:** Evaluation and Visualization
- Alignment comparison completed
- Figures generated

**Milestone 8:** Documentation
- Results documented in 04_validation.md
- Gate decision recorded

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Hessian computation fails (OOM) | MEDIUM | CRITICAL | Use subset of training data; reduce num_eigenthings to 50 if needed |
| Marchenko-Pastur fit poor quality | MEDIUM | HIGH | Visual inspection of fit; try different bulk portion for fitting |
| Minority gradient computation unclear | LOW | HIGH | Use dataset metadata to identify minority groups explicitly |
| Alignment scores near zero | LOW | MEDIUM | Validate eigenvector projection math; check gradient magnitudes |
| ERM and DRO alignment too similar | MEDIUM | CRITICAL | This is a valid negative result (geometric signature doesn't exist) |
| Dataset download issues | LOW | MEDIUM | Clone Group DRO repository; follow official data scripts |

---

## Appendix: Reference Information

### A. Phase 2C Source
This PRD is derived from: `{hypothesis_folder}/02c_experiment_brief.md`

Key sections referenced:
- Dataset specification (Waterbirds)
- Model architecture (ResNet-50)
- Training protocol (ERM vs Group-DRO, 100 epochs, SGD)
- Analysis mechanism (Marchenko-Pastur alignment A(w))
- Evaluation metrics (direction-based comparison)
- Visualization requirements

### B. Theoretical Foundation

**Marchenko-Pastur Theory (Sagun et al. 2017):**
- Bulk edge λ_+ separates signal from noise eigenvalues
- Outlier eigenvalues capture data structure
- Application: Define curvature concentration subspace

**Group-DRO (Sagawa et al. 2020):**
- Worst-group loss minimization
- Expected performance: 75-80% worst-group accuracy
- Requires group labels during training

**Hessian Analysis (Li et al. 2018):**
- ResNets produce analyzable loss landscapes
- Skip connections create flat minima
- Filter normalization enables comparison

### C. Ground Truth Group Labels
Waterbirds dataset provides:
- `y`: Bird type label (0=landbird, 1=waterbird)
- `place`: Background label (0=land, 1=water)
- `group_idx`: 4 groups
  - 0: landbird-land (majority)
  - 1: landbird-water (minority)
  - 2: waterbird-land (minority)
  - 3: waterbird-water (majority)

**Minority groups for gradient computation:** groups 1 and 2

### D. Baseline Performance Expectations
From Sagawa et al. 2020 and Phase 2B research:
- ERM average: 85-90%, worst-group: 60-75%
- Group-DRO average: 75-80%, worst-group: 75-80%
- A(w)_ERM: Expected higher (quantitative value TBD from PoC)
- A(w)_DRO: Expected lower (quantitative value TBD from PoC)

---

*This PRD generated for Phase 3 Implementation Planning | Anonymous Research Pipeline | h-e1 EXISTENCE Hypothesis*
