# Experiment Design: h-m1

**Date:** 2026-04-24
**Author:** Anonymous
**Hypothesis Statement:** Under ERM training on Waterbirds, if spurious features dominate learning, then sharp curvature will concentrate in specific Hessian eigenspace subspaces (outliers beyond MP bulk edge), because Gauss-Newton decomposition shows Hessian outliers align with data structure.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (Step 1 of 4) Template** - Validates causal mechanism in hypothesis chain.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-e1 (COMPLETED ✅)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM (Step 1 of 4)
- **Prerequisites:** h-e1

### Gate Condition
MUST_WORK - Sharp curvature must concentrate in outlier subspace. Failure breaks mechanism chain.

---

## Continuation Context

This is a **continuation experiment** building on h-e1 validated results.

**Proven from h-e1:**
- ERM alignment A(w) = 0.7234 vs DRO alignment = 0.3156
- ERM has 23 outlier eigenvalues vs DRO's 15
- Geometric signature validated - proceed to mechanism chain

**Reuse for controlled comparison:**
- Dataset: Waterbirds (same as h-e1)
- Model: ResNet-50 (same baseline)
- Configuration: Inherited optimal hyperparameters

### Previous Hypothesis Results (h-e1)
- **Status:** COMPLETED ✅
- **Gate Result:** PASS
- **Key Finding:** ERM vs DRO geometric signature exists
- **Optimal Config:** SGD, lr=0.1, batch=128, epochs=200

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Hessian Eigenvalue Spectrum Analysis**
- **Result 1:** Exploring the Loss Landscape of Neural Networks (Sagun et al. 2017)
  - Dataset: CIFAR-10, CIFAR-100
  - Hyperparameters: Power iteration with Lanczos, top 100-200 eigenvalues, convergence 1e-5
  - Key insight: Bulk edge separates signal from noise. Top eigenvalues correspond to data structure.
  
- **Result 2:** Loss Landscape Mode Connectivity (Garipov et al. 2018)
  - Dataset: ImageNet, CIFAR-10
  - Hyperparameters: Hutchinson trace estimator, batch=128 for Hessian, scipy.sparse.linalg.eigsh
  - Key insight: Eigenspectrum stable across modes. Use 128-256 batch for stable estimates.
  
- **Result 3:** Sharpness-Aware Minimization (Foret et al. 2020)
  - Dataset: CIFAR-10, ImageNet
  - Hyperparameters: perturbation rho=0.05, max eigenvalue as sharpness
  - Key insight: Flat minima correlate with generalization.

**Query 2: Implementation Challenges**
- **Best Practices:**
  - Use pytorch-hessian-eigenthings for efficient computation
  - Compute top-100-200 eigenvalues only (not full Hessian)
  - Use double precision for Hessian-vector products
  - Average over multiple batches for stability
  - Validate MP fit with Q-Q plot
  
- **Pitfalls to Avoid:**
  - Full Hessian O(n²) memory → use power iteration
  - Small eigenvalues numerically unstable → threshold 1e-5
  - Batch size affects estimates → use 128+ samples
  - Outlier detection sensitive to bulk edge → iterative fitting

**Query 3: Benchmark Results**
- **ResNet-50 on CIFAR-10:**
  - Expected outliers: 15-25 eigenvalues beyond bulk edge
  - Bulk edge: λ+ ≈ 2.0-3.0
  - Max eigenvalue: λ_max ≈ 5.0-10.0
  - Source: Sagun et al. 2017

### Archon Code Examples

**Example 1: Hessian Eigenvalue Computation**
- **Source:** pytorch-hessian-eigenthings library
- **Code Pattern:**
  ```python
  from hessian_eigenthings import compute_hessian_eigenthings
  
  eigenvalues, eigenvectors = compute_hessian_eigenthings(
      model, dataloader, loss_fn,
      num_eigenthings=100,  # top 100 eigenvalues
      mode='power_iter',
      use_gpu=True
  )
  ```
- **Insight:** Power iteration avoids forming full Hessian, handles large networks efficiently

**Example 2: Marchenko-Pastur Bulk Edge Detection**
- **Source:** Sagun et al. 2017 supplementary code
- **Code Pattern:**
  ```python
  from scipy.optimize import curve_fit
  from scipy.stats import marchenko_pastur
  
  # Fit MP distribution
  sigma_sq, bulk_edge = fit_marchenko_pastur(eigenvalues, gamma=0.1)
  
  # Detect outliers
  outliers = eigenvalues[eigenvalues > bulk_edge]
  num_outliers = len(outliers)
  ```
- **Insight:** Fit bulk eigenvalues only, iterate to refine outlier threshold

### Exa GitHub Implementations

**Repository 1**: tomgoldstein/loss-landscape (⭐ 2.8k)
- **URL**: https://github.com/tomgoldstein/loss-landscape
- **Relevance**: Official loss landscape visualization with Hessian eigenvalue computation
- **Architecture**: ResNet, VGG, DenseNet support
- **Key Code**:
  ```python
  from hessian_eigenthings import compute_hessian_eigenthings
  
  eigenvalues, eigenvectors = compute_hessian_eigenthings(
      net, dataloader, criterion,
      num_eigenthings=100,
      power_iter_steps=20,
      power_iter_err_threshold=1e-5,
      use_gpu=True
  )
  ```
- **Training Config**:
  - Optimizer: SGD (momentum=0.9, weight_decay=5e-4)
  - Learning rate: 0.1, schedule: MultiStepLR [100,150], gamma=0.1
  - Batch size: 128
  - Epochs: 200
- **Dataset**: CIFAR-10, CIFAR-100
- **Results**: Eigenvalue spectrum visualizations for various architectures
- **Used For**: Hessian computation parameters, power iteration configuration

**Repository 2**: noahgolmant/pytorch-hessian-eigenthings (⭐ 485)
- **URL**: https://github.com/noahgolmant/pytorch-hessian-eigenthings
- **Relevance**: Standard PyTorch library for efficient Hessian eigenvalue computation
- **Architecture**: Model-agnostic (works with any nn.Module)
- **Key Code**:
  ```python
  eigenvals, eigenvecs = compute_hessian_eigenthings(
      model=net,
      dataloader=train_loader,
      loss=nn.CrossEntropyLoss(),
      num_eigenthings=100,
      mode='power_iter',
      use_gpu=True,
      max_samples=512
  )
  ```
- **Used For**: Primary implementation library (pip install hessian-eigenthings)

**Repository 3**: kohpangwei/group_DRO (⭐ 412)
- **URL**: https://github.com/kohpangwei/group_DRO
- **Relevance**: Official Waterbirds dataset + Group-DRO baseline implementation
- **Architecture**: ResNet-50 pretrained on ImageNet
- **Key Code**:
  ```python
  from wilds import get_dataset
  
  dataset = get_dataset(dataset="waterbirds", download=True)
  train_data = dataset.get_subset("train")
  group_array = train_data.metadata_array[:, 0]  # 4 groups
  ```
- **Training Config**:
  - Optimizer: SGD (momentum=0.9, weight_decay=1e-4)
  - Learning rate: 0.001
  - Batch size: 128
  - Epochs: 300
- **Dataset**: Waterbirds (11,788 images, 4 groups)
- **Results**: ERM worst-group 72.6%, Group-DRO worst-group 91.4%
- **Used For**: Dataset loading method, baseline ERM configuration

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Priority Analysis:**
1. ⭐⭐⭐ **HIGHEST**: pytorch-hessian-eigenthings library (standard, well-tested)
2. ⭐⭐⭐ **HIGHEST**: kohpangwei/group_DRO for Waterbirds dataset (official)
3. ⭐⭐ **MEDIUM**: tomgoldstein/loss-landscape for visualization patterns

**Recommended Implementation Path:**
- Primary: Use pytorch-hessian-eigenthings + WILDS Waterbirds dataset
- Fallback: Manual power iteration if library unavailable
- Justification: Standard libraries ensure reproducibility, match h-e1 successful approach

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Standard library usage (pytorch-hessian-eigenthings, WILDS) does not require deep semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset**: Waterbirds  
**Type**: standard (WILDS benchmark dataset)  
**Source**: WILDS library (https://wilds.stanford.edu/)

**Continuation Reuse:** Same dataset as h-e1 for controlled comparison (only analysis method changes)

**Statistics:**
- Total samples: 11,788 images
- Splits: Train=4,795, Val=1,199, Test=5,794
- Classes: 2 (landbird vs waterbird)
- Groups: 4 (bird_type × background)
  - Group 0: Landbird on land (majority)
  - Group 1: Landbird on water (minority)
  - Group 2: Waterbird on land (minority)
  - Group 3: Waterbird on water (majority)
- Image size: 224×224

**Preprocessing:**
- Resize to 224×224
- ImageNet normalization: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]

**Augmentation (Training only):**
- RandomResizedCrop(224)
- RandomHorizontalFlip()

**Loading Information** (for Phase 4 download):
- Method: WILDS library (programmatic-api)
- Identifier: `waterbirds`
- Code: 
  ```python
  from wilds import get_dataset
  dataset = get_dataset(dataset="waterbirds", download=True)
  train_data = dataset.get_subset("train")
  ```

### Models

#### Baseline Model

**Architecture**: ResNet-50 (pretrained on ImageNet)  
**Type**: Standard CNN with residual connections

**Continuation Reuse:** Same baseline as h-e1 (proven stable, enables controlled comparison)

**Configuration:**
- Layers: 50 layers (residual blocks)
- Parameters: ~25.6M
- Input: (B, 3, 224, 224)
- Output: (B, 2) for binary bird classification

**Modifications for Waterbirds:**
- Replace final FC layer: `nn.Linear(2048, 2)`
- Finetune all layers on Waterbirds dataset

**Loading Information** (for Phase 4 download):
- Method: torchvision.models
- Identifier: `resnet50`
- Code:
  ```python
  import torchvision.models as models
  model = models.resnet50(pretrained=True)
  # Replace final layer
  model.fc = nn.Linear(2048, 2)
  ```

#### Proposed Model

**Architecture:** ResNet-50 + Hessian Eigenspectrum Analysis Module

**Integration Point:** Post-training analysis (not a model modification)
- Train baseline ERM model to convergence
- Compute Hessian eigenspectrum at final parameters
- Analyze outlier concentration via Marchenko-Pastur fitting

**Core Mechanism Implementation:**

```python
# Core Mechanism: Hessian Eigenspectrum Analysis with MP Bulk Edge Detection
# Based on: pytorch-hessian-eigenthings + Sagun et al. 2017

import torch
from hessian_eigenthings import compute_hessian_eigenthings
from scipy.optimize import curve_fit
from scipy.stats import marchenko_pastur
import numpy as np

class HessianMPAnalyzer:
    """
    Analyzes Hessian eigenspectrum and detects outliers beyond 
    Marchenko-Pastur bulk edge to test curvature concentration hypothesis.
    """
    def __init__(self, model, dataloader, loss_fn, num_eigenvalues=100):
        self.model = model
        self.dataloader = dataloader
        self.loss_fn = loss_fn
        self.num_eigenvalues = num_eigenvalues
        
    def compute_eigenspectrum(self):
        """Compute top-k Hessian eigenvalues via power iteration"""
        eigenvals, eigenvecs = compute_hessian_eigenthings(
            self.model,
            self.dataloader,
            self.loss_fn,
            num_eigenthings=self.num_eigenvalues,
            mode='power_iter',
            power_iter_steps=20,
            power_iter_err_threshold=1e-5,
            use_gpu=True
        )
        return eigenvals, eigenvecs
    
    def fit_marchenko_pastur(self, eigenvals, gamma):
        """
        Fit MP distribution to bulk eigenvalues, detect outliers
        
        Args:
            eigenvals: array of eigenvalues
            gamma: aspect ratio p/n (params/samples)
        Returns:
            bulk_edge: MP bulk edge threshold lambda_+
            num_outliers: count of eigenvalues > bulk_edge
        """
        # Theoretical MP PDF
        def mp_pdf(x, sigma_sq):
            return marchenko_pastur.pdf(x, gamma, scale=sigma_sq)
        
        # Histogram for fitting
        hist, bins = np.histogram(eigenvals, bins=50, density=True)
        bin_centers = (bins[:-1] + bins[1:]) / 2
        
        # Initial estimate
        sigma_sq_init = np.median(eigenvals) / (1 + np.sqrt(gamma))**2
        
        # Fit bulk (iterative: exclude current outliers)
        popt, _ = curve_fit(mp_pdf, bin_centers, hist, p0=[sigma_sq_init])
        sigma_sq = popt[0]
        
        # Compute bulk edge: lambda_+ = sigma^2 * (1 + sqrt(gamma))^2
        bulk_edge = sigma_sq * (1 + np.sqrt(gamma))**2
        
        # Count outliers
        outliers = eigenvals[eigenvals > bulk_edge]
        num_outliers = len(outliers)
        
        return bulk_edge, num_outliers, sigma_sq

# Integration: Run analysis after ERM training converges
# Compare ERM outlier count vs DRO outlier count (from h-e1)
```

### Training Protocol

**Reused from h-e1 (Continuation Experiment):**

**Optimizer**: SGD
  - Momentum: 0.9
  - Weight decay: 5e-4
  - **Source**: h-e1 validated configuration

**Learning Rate**: 0.1 (initial)
  - **Schedule**: MultiStepLR, milestones=[100, 150], gamma=0.1
  - **Source**: h-e1 validated, matches tomgoldstein/loss-landscape

**Batch Size**: 128
  - **Source**: h-e1 validated, stable for Hessian computation (Garipov et al.)

**Epochs**: 200 (with early stopping)
  - **Source**: h-e1 validated

**Loss Function**: CrossEntropyLoss (standard ERM)
  - **Source**: h-e1 baseline

**Seeds**: 3 seeds (42, 123, 456)
  - **Rationale**: MECHANISM hypothesis requires statistical validation across seeds

**Hessian Computation Parameters** (new for h-m1):
  - Method: Power iteration via pytorch-hessian-eigenthings
  - Num eigenvalues: 100 (top eigenvalues)
  - Convergence threshold: 1e-5
  - Batch size for Hessian: 128 (matches training)
  - **Source**: Sagun et al. 2017, tomgoldstein/loss-landscape

### Evaluation

**Primary Metrics:**
1. **Num Outliers (ERM)**: Count of eigenvalues beyond MP bulk edge
2. **Bulk Edge λ+ (ERM)**: Marchenko-Pastur bulk edge threshold
3. **Max Eigenvalue λ_max (ERM)**: Largest eigenvalue (sharpness indicator)

**Comparison Baseline:**
- DRO outlier count from h-e1: 15 outliers
- DRO bulk edge from h-e1: λ+ = 1.987

**Success Criteria (MECHANISM: Statistical validation required):**
- Primary: ERM num_outliers > DRO num_outliers (from h-e1)
  - Expected: ERM ≈ 23+ outliers (h-e1 reference), DRO = 15
  - Statistical test: Two-sample t-test across seeds, p < 0.05
- Secondary: ERM bulk edge λ+ > DRO bulk edge
  - Expected: ERM λ+ ≈ 2.4+, DRO λ+ = 1.987
  - Effect size: Cohen's d > 0.8

**Expected Baseline Performance** (from h-e1 and research):
- ERM outliers: 23 (h-e1 empirical)
- DRO outliers: 15 (h-e1 empirical)
- ResNet-50 CIFAR-10 benchmark: 15-25 outliers (Sagun et al.)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: multiclass_classification
- Library: torchmetrics + custom group accuracy + numpy/scipy
- Code:
  ```python
  import torchmetrics
  acc = torchmetrics.Accuracy(task="multiclass", num_classes=2)
  
  # Custom group-wise accuracy (reused from h-e1)
  def compute_group_accuracy(preds, labels, groups):
      group_accs = []
      for g in range(4):
          mask = (groups == g)
          if mask.sum() > 0:
              group_accs.append((preds[mask] == labels[mask]).float().mean())
      return min(group_accs)  # worst-group
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: ERM outliers vs DRO outliers bar chart (with h-e1 baseline)

#### Additional Figures (LLM Autonomous)

Based on Hessian eigenspectrum analysis, generate:

1. **Eigenvalue Spectrum Plot**: Scatter plot of all 100 eigenvalues with MP bulk edge threshold line
2. **MP Distribution Fit**: Histogram of eigenvalues overlaid with fitted Marchenko-Pastur PDF
3. **ERM vs DRO Spectrum Comparison**: Side-by-side eigenvalue spectra with outlier regions highlighted
4. **Outlier Eigenvalues Distribution**: Box plot comparing outlier eigenvalue magnitudes (ERM vs DRO)
5. **Curvature Concentration Heatmap**: Visualize top-10 eigenvector directions in parameter space

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: Exploring the Loss Landscape of Neural Networks (Sagun et al. 2017)
- **Type**: Knowledge base article / Research paper
- **Query Used**: "Hessian eigenvalue spectrum Marchenko-Pastur bulk edge detection experiment design"
- **Relevance**: Foundational work on Hessian eigenspectrum analysis in neural networks
- **Key Insights**:
  - Bulk edge separates signal eigenvalues from noise
  - Top eigenvalues correspond to data structure
  - Use power iteration with Lanczos algorithm for efficiency
- **Used For**: Hessian computation methodology, MP bulk edge concept

**Source 2**: Loss Landscape Mode Connectivity (Garipov et al. 2018)
- **Type**: Knowledge base article
- **Query Used**: "Hessian eigenvalue spectrum Marchenko-Pastur bulk edge detection experiment design"
- **Key Insights**:
  - Eigenspectrum stable across connected modes
  - Batch size 128-256 for stable Hessian estimates
  - Use scipy.sparse.linalg.eigsh for eigenvalue computation
- **Used For**: Hessian computation batch size (128), stability requirements

**Source 3**: PyTorch-Hessian-Eigenthings Library Best Practices
- **Type**: Knowledge base / Implementation guide
- **Query Used**: "Hessian eigenvalue computation implementation challenges best practices PyTorch"
- **Key Insights**:
  - Compute top-100-200 eigenvalues only (avoid full Hessian O(n²))
  - Use double precision for Hessian-vector products
  - Convergence threshold 1e-5 for numerical stability
- **Used For**: Implementation parameters, best practices

### B. Archon Code Examples

**Code Source 1**: pytorch-hessian-eigenthings library pattern
- **Query Used**: "Hessian eigenvalue Marchenko-Pastur PyTorch implementation"
- **Key Code**:
  ```python
  from hessian_eigenthings import compute_hessian_eigenthings
  eigenvalues, eigenvectors = compute_hessian_eigenthings(
      model, dataloader, loss_fn,
      num_eigenthings=100,
      mode='power_iter',
      use_gpu=True
  )
  ```
- **Used For**: Core Hessian computation API in pseudo-code

**Code Source 2**: Marchenko-Pastur Bulk Edge Fitting
- **Query Used**: "Hessian eigenvalue Marchenko-Pastur PyTorch implementation"
- **Key Code**: MP distribution fitting with scipy.optimize.curve_fit
- **Used For**: Bulk edge detection algorithm in pseudo-code

### C. GitHub Implementations (Exa)

**Repository 1**: tomgoldstein/loss-landscape (⭐ 2.8k)
- **URL**: https://github.com/tomgoldstein/loss-landscape
- **Query Used**: "Sagun Hessian eigenvalue neural network official implementation GitHub"
- **Relevance**: Official loss landscape visualization with Hessian analysis
- **Key Code**: Power iteration implementation with convergence threshold 1e-5
- **Configuration Extracted**: 
  - num_eigenvalues=100
  - power_iter_steps=20
  - SGD training: lr=0.1, momentum=0.9, weight_decay=5e-4
- **Used For**: Power iteration parameters, training hyperparameters

**Repository 2**: noahgolmant/pytorch-hessian-eigenthings (⭐ 485)
- **URL**: https://github.com/noahgolmant/pytorch-hessian-eigenthings
- **Query Used**: "pytorch-hessian-eigenthings Marchenko-Pastur implementation"
- **Relevance**: Standard PyTorch library for Hessian eigenvalue computation
- **Key Code**: Model-agnostic eigenvalue computation API
- **Used For**: Primary implementation library (pip install hessian-eigenthings)

**Repository 3**: kohpangwei/group_DRO (⭐ 412)
- **URL**: https://github.com/kohpangwei/group_DRO
- **Query Used**: "Waterbirds spurious correlation Group-DRO benchmark implementation"
- **Relevance**: Official Waterbirds dataset implementation
- **Key Code**: WILDS dataset loading, group label extraction
- **Configuration Extracted**: ResNet-50, SGD training protocol
- **Their Results**: ERM worst-group 72.6%, DRO worst-group 91.4%
- **Used For**: Dataset loading method, baseline comparison reference

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - h-e1
- **File**: `h-e1/04_validation.md`
- **Reused Components**:
  - Dataset: Waterbirds (proven stable, same dataset for controlled comparison)
  - Model: ResNet-50 pretrained on ImageNet
  - Hyperparameters: SGD lr=0.1, batch=128, epochs=200
  - Training protocol: MultiStepLR schedule [100, 150], gamma=0.1
- **h-e1 Empirical Results** (used as baseline):
  - ERM outliers: 23 eigenvalues
  - DRO outliers: 15 eigenvalues
  - ERM bulk edge: λ+ = 2.456
  - DRO bulk edge: λ+ = 1.987
- **Why Reused**: Enables controlled experiment - only analysis method changes (deeper eigenspectrum analysis)

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (Waterbirds) | Previous (h-e1) + GitHub | h-e1/04_validation.md, kohpangwei/group_DRO |
| Model (ResNet-50) | Previous (h-e1) + Archon KB | h-e1/04_validation.md, Sagun et al. 2017 |
| Hessian computation | GitHub + Archon Code | pytorch-hessian-eigenthings, Archon Code Source 1 |
| MP bulk edge fitting | Archon Code | Archon Code Source 2 (Sagun et al. supplementary) |
| Power iteration params | GitHub | tomgoldstein/loss-landscape (steps=20, threshold=1e-5) |
| Training protocol | Previous (h-e1) | h-e1/04_validation.md |
| Baseline comparison | Previous (h-e1) | h-e1 empirical results (23 vs 15 outliers) |
| Success criteria | Phase 2B + h-e1 | 02b_verification_plan.md Section 2.2 + h-e1 validation |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-24

### Workflow History for This Hypothesis

From verification_state.yaml:
- **2026-04-24**: h-m1 set to IN_PROGRESS (external loop starting Phase 2C → 3 → 4)
- **Prerequisites**: h-e1 COMPLETED ✅ (validation passed, gate satisfied)
- **Current Phase**: Phase 2C (Experiment Design)
- **Next Phase**: Phase 3 (Implementation Planning)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
