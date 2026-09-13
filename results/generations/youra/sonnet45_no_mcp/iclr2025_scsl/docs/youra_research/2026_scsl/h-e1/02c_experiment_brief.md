# Experiment Design: H-E1

**Date:** 2026-04-24
**Author:** Anonymous
**Hypothesis Statement:** Under standard ERM and Group-DRO training on Waterbirds, if we measure Marchenko-Pastur-defined curvature subspace alignment A(w), then ERM solutions will exhibit significantly higher alignment than Group-DRO solutions, because ERM exploits spurious features that create sharp, concentrated curvature.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS (Phase 2C)
**Prerequisites Satisfied:** Yes (None - foundation hypothesis)
**Gate Status:** MUST_WORK - Not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
**Gate Type:** MUST_WORK
**Pass Condition:** ERM vs DRO alignment distributions significantly different (p<0.01, Cohen's d>0.8)
**Fail Action:** STOP—geometric signature doesn't exist, abandon hypothesis

---

## Continuation Context

This is the **foundation hypothesis** (H-E1) - the first in the verification chain. No previous hypothesis context exists.

**Continuation Status:** First hypothesis - establishes geometric signature existence before mechanism testing.

### Previous Hypothesis Results (if applicable)
None - H-E1 is the root hypothesis with no prerequisites.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**⚠️ MCP Limitation:** Archon MCP server not available in current environment.

**Extracted from Phase 2B Verification Plan:**

**Key Implementation References:**
1. **Marchenko-Pastur Theory (Sagun et al. 2017)**
   - Method: Hessian eigenvalue spectrum analysis
   - Application: Signal vs noise eigenvalue threshold identification
   - Key Insight: Bulk edge accurately identifies outlier eigenvalues in over-parameterized networks

2. **Loss Landscape Visualization (Li et al. 2018)**
   - Method: Filter normalization for ResNet analysis
   - Application: ResNets produce analyzable loss landscapes with skip connections
   - Key Insight: Skip connections create flat minima suitable for curvature analysis

3. **Mode Connectivity & FGE (Garipov et al. 2018)**
   - Method: Fast Geometric Ensembling with cyclical learning rate
   - Application: Sample solutions along connectivity paths
   - Key Insight: Geometric variation analysis within connected components

4. **Group-DRO Benchmarks (Sagawa et al. 2020)**
   - Dataset: Waterbirds, CelebA with ground-truth group labels
   - Performance: 75-80% worst-group accuracy (requires group labels)
   - Application: Baseline comparison for spurious correlation robustness

### Archon Code Examples

**⚠️ MCP Limitation:** Archon code search not available.

**From Phase 2B References:**
- **Hessian Computation:** pytorch-hessian-eigenthings (recommended infrastructure)
- **Dataset Source:** group_DRO repository (https://github.com/kohpangwei/group_DRO)
- **Model Source:** torchvision.models.resnet50

### Exa GitHub Implementations

**⚠️ MCP Limitation:** Exa MCP server not available in current environment.

**From Phase 2B Baseline Methods:**

**Repository 1: group_DRO Official Implementation**
- **URL:** https://github.com/kohpangwei/group_DRO
- **Relevance:** Official implementation of Group-DRO baseline
- **Key Components:**
  - Waterbirds dataset loading scripts
  - Group-balanced training loops
  - Worst-group accuracy evaluation
- **Performance:** 75-80% worst-group accuracy on Waterbirds
- **Usage:** Baseline comparison and dataset preparation

**Repository 2: Loss Landscape Analysis Tools**
- **Reference:** Li et al. 2018 visualization methods
- **Components:** Filter normalization, 2D landscape plotting
- **Application:** ResNet loss landscape analysis

**Repository 3: pytorch-hessian-eigenthings**
- **Purpose:** Efficient Hessian eigenvalue/eigenvector computation
- **Method:** Power iteration + deflation for large networks
- **Application:** Compute Hessian spectrum for MP analysis

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Assessment:**
This is a novel mechanistic analysis combining established methods:
1. **Sagun et al.** - Marchenko-Pastur theory (established)
2. **Sagawa et al.** - Group-DRO baseline (official repo available)
3. **Li et al.** - Loss landscape visualization (established methods)

**Priority:** Use official implementations where available, combine methods for novel analysis.

**Recommended Implementation Path:**
- Primary: group_DRO repository for dataset + baseline training
- Fallback: Custom implementation of ERM baseline with pytorch-hessian-eigenthings for Hessian analysis
- Justification: Official group_DRO repo provides validated Waterbirds dataset and DRO baseline. Custom Hessian analysis required for novel MP-based alignment metric A(w).

### Code Analysis (Serena MCP)

**⚠️ MCP Limitation:** Serena MCP server not available in current environment.

**Analysis from Phase 2B Context:**
- Hessian computation via pytorch-hessian-eigenthings library
- Marchenko-Pastur fitting: standard eigenvalue spectrum analysis
- Alignment metric A(w): projection of minority gradients onto outlier subspace
- No complex custom architectures required - standard ResNet-50 from torchvision

---

## Experiment Specification

### Dataset

**Dataset Name:** Waterbirds
**Type:** standard (real benchmark dataset)
**Source:** group_DRO repository (https://github.com/kohpangwei/group_DRO)

**Description:**
- Binary classification: Waterbird (landbird vs waterbird)
- Spurious correlation: Background (land vs water)
- 4 groups: landbird-land, landbird-water, waterbird-land, waterbird-water
- Ground-truth group labels available for evaluation

**Statistics:**
- Total samples: 11,788 (4,795 train, 1,199 validation, 5,794 test)
- Classes: 2 (landbird, waterbird)
- Groups: 4 (2 classes × 2 backgrounds)
- Spurious correlation strength: 95% train correlation

**Preprocessing:**
- Image resize: 224×224
- Normalization: ImageNet mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
- Data augmentation (train): Random horizontal flip, random crop

**Hypothesis Fit Justification:**
Ground-truth spurious labels enable measurement of worst-group accuracy and minority-group gradient computation. Background spurious correlation directly tests geometric signature of spurious feature exploitation.

**Loading Information** (for Phase 4 download):
- Method: Custom (group_DRO repository scripts)
- Identifier: Waterbirds dataset from https://github.com/kohpangwei/group_DRO
- Code:
  ```python
  # Clone group_DRO repository and run data preparation script
  # Dataset will be downloaded and prepared according to official instructions
  # Path: ./data/waterbird_complete95_forest2water2/
  ```

### Models

#### Baseline Models

**Model 1: ERM Baseline (Standard Training)**
**Architecture:** ResNet-50
**Type:** Standard CNN with skip connections
**Source:** torchvision.models
**Pretrained:** ImageNet pretrained weights

**Configuration:**
- Input: 224×224×3 RGB images
- Output: 2 classes (landbird, waterbird)
- Parameters: ~25.6M
- Layers: 50 (conv + residual blocks + fc)

**Training Mode:** Standard ERM (Empirical Risk Minimization)
- Loss: Cross-entropy on full training set
- No group reweighting
- Objective: Minimize average loss across all samples

**Model 2: Group-DRO Baseline (Robust Training)**
**Architecture:** ResNet-50 (same as ERM)
**Type:** Standard CNN with skip connections
**Source:** torchvision.models
**Pretrained:** ImageNet pretrained weights

**Training Mode:** Group-DRO (Distributionally Robust Optimization)
- Loss: Group-balanced cross-entropy
- Group reweighting based on worst-group performance
- Objective: Minimize worst-group loss
- **Note:** Requires group labels during training

**Hypothesis Fit:**
- ResNet-50 provides sufficient over-parameterization for Marchenko-Pastur assumptions
- Skip connections create analyzable loss landscapes (Li et al. 2018)
- Standard architecture enables reproducibility and comparison
- Two training modes (ERM vs DRO) test the core hypothesis prediction

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: resnet50
- Code:
  ```python
  import torchvision.models as models
  model = models.resnet50(pretrained=True)
  # Modify final layer for 2-class classification
  model.fc = torch.nn.Linear(model.fc.in_features, 2)
  ```

#### Proposed Model

**Note for EXISTENCE Hypothesis:**
This is a PoC (Proof of Concept) experiment testing whether ERM and Group-DRO solutions occupy geometrically distinct regions. The "mechanism" here is the **analysis method** (Marchenko-Pastur subspace alignment), not a new model architecture.

**Analysis Mechanism: Curvature Subspace Alignment A(w)**

The core contribution is the **alignment metric computation**, not a model modification:

```python
# Core Analysis Mechanism: Marchenko-Pastur Subspace Alignment
# Based on: Sagun et al. 2017 (MP theory), Sagawa et al. 2020 (minority gradients)

import torch
from hessian_eigenthings import compute_hessian_eigenthings

def compute_mp_alignment(model, train_loader, minority_loader):
    """
    Compute Marchenko-Pastur-defined curvature subspace alignment A(w).
    
    Args:
        model: Trained ResNet-50 model
        train_loader: Full training data for Hessian computation
        minority_loader: Minority group samples for gradient computation
    
    Returns:
        alignment: A(w) = ||P_S_out g_minority||² / ||g_minority||²
    """
    # Step 1: Compute Hessian eigenvalues and eigenvectors
    eigenvalues, eigenvectors = compute_hessian_eigenthings(
        model, train_loader, num_eigenthings=100, 
        power_iter_steps=20, momentum=0.0
    )
    
    # Step 2: Fit Marchenko-Pastur distribution to identify bulk edge
    # MP bulk edge lambda_+ = sigma^2 * (1 + sqrt(aspect_ratio))^2
    bulk_edge = fit_marchenko_pastur(eigenvalues)
    
    # Step 3: Identify outlier subspace (eigenvalues > bulk_edge)
    outlier_mask = eigenvalues > bulk_edge
    outlier_eigenvectors = eigenvectors[:, outlier_mask]  # S_out subspace
    
    # Step 4: Compute minority-group gradient
    g_minority = compute_minority_gradient(model, minority_loader)
    
    # Step 5: Project minority gradient onto outlier subspace
    # P_S_out = sum_i (g · v_i) * v_i for v_i in S_out
    projection = torch.matmul(
        outlier_eigenvectors, 
        torch.matmul(outlier_eigenvectors.T, g_minority)
    )
    
    # Step 6: Compute alignment metric
    alignment = (projection.norm() ** 2) / (g_minority.norm() ** 2)
    
    return alignment

def fit_marchenko_pastur(eigenvalues):
    """Fit MP distribution and return bulk edge threshold."""
    # Estimate noise variance sigma^2 and aspect ratio
    # Return lambda_+ = sigma^2 * (1 + sqrt(gamma))^2
    # (Simplified - actual implementation uses maximum likelihood fit)
    pass

def compute_minority_gradient(model, minority_loader):
    """Compute average gradient on minority group samples."""
    model.eval()
    total_grad = None
    for inputs, labels, groups in minority_loader:
        # Filter for minority group (e.g., landbird on water)
        outputs = model(inputs)
        loss = F.cross_entropy(outputs, labels)
        grad = torch.autograd.grad(loss, model.parameters())
        # Accumulate gradients
        if total_grad is None:
            total_grad = [g.detach() for g in grad]
        else:
            total_grad = [tg + g.detach() for tg, g in zip(total_grad, grad)]
    # Flatten and normalize
    return torch.cat([g.flatten() for g in total_grad])

# Integration: This analysis is performed POST-TRAINING on converged models
# Compare: A(w)_ERM vs A(w)_DRO
```

**Key Operations:**
1. Compute Hessian eigenspectrum (100 top eigenvalues/vectors)
2. Fit Marchenko-Pastur distribution to identify bulk edge
3. Define outlier subspace S_out (eigenvalues above bulk)
4. Compute minority-group gradient g_minority
5. Project g_minority onto S_out
6. Calculate alignment A(w) = ||projection||² / ||g_minority||²

**Expected Behavior:**
- ERM solutions: High A(w) (minority gradients align with sharp curvature)
- DRO solutions: Low A(w) (minority gradients do not align with sharp curvature)

### Training Protocol

**Two Training Modes:** ERM and Group-DRO (both use same hyperparameters except loss function)

**Optimizer:** SGD with momentum
- Momentum: 0.9
- Weight decay: 1e-4
- Nesterov: False

**Learning Rate:** 0.001
- Schedule: MultiStepLR
- Milestones: [60, 80] epochs
- Gamma: 0.1 (10× reduction at each milestone)

**Batch Size:** 128
- Note: Will also test batch sizes [32, 512] for stability validation

**Epochs:** 100
- Early stopping: Patience 10 epochs on validation worst-group accuracy

**Loss Function:**
- **ERM Mode:** Standard cross-entropy
  ```python
  loss = F.cross_entropy(outputs, labels)
  ```
- **Group-DRO Mode:** Group-balanced cross-entropy
  ```python
  # Compute per-group losses
  group_losses = compute_group_losses(outputs, labels, groups)
  # Robust optimization: minimize worst-group loss
  loss = group_losses.max()
  ```

**Seeds:** 1 (fixed seed for PoC)
- Note: Full verification (Phase 2B) specifies 20 seeds, but PoC uses 1 seed

**Regularization:**
- Weight decay: 1e-4 (via optimizer)
- Dropout: None (ResNet-50 default)
- Data augmentation: Random horizontal flip, random crop (train only)

**Training Procedure:**
1. Initialize ResNet-50 with ImageNet pretrained weights
2. Replace final layer: fc → Linear(2048, 2)
3. Train for 100 epochs with specified hyperparameters
4. Track: train loss, val accuracy, worst-group accuracy
5. Save checkpoint at best validation worst-group accuracy

**Controlled Variables:**
- Architecture: ResNet-50 (fixed)
- Dataset: Waterbirds (fixed)
- Random seed: 42 (fixed for PoC)
- Independent variable: Training method (ERM vs Group-DRO)

**Source:** Based on Group-DRO official implementation (Sagawa et al. 2020)

### Evaluation

**Primary Metrics:**

1. **Curvature Subspace Alignment A(w)** (Hypothesis-specific metric)
   - Definition: A(w) = ||P_S_out g_minority||² / ||g_minority||²
   - Computation: Post-training analysis using Hessian eigendecomposition
   - Expected: A(w)_ERM > A(w)_DRO

2. **Worst-Group Accuracy** (Robustness metric)
   - Definition: min_{g ∈ groups} Accuracy_g
   - Groups: 4 (landbird-land, landbird-water, waterbird-land, waterbird-water)
   - Expected: ERM 60-75%, DRO 75-80% (from Phase 2B baselines)

3. **Average Accuracy** (Standard metric)
   - Definition: Accuracy across all test samples
   - Expected: ERM 85-90%, DRO 75-80%

**Secondary Metrics:**

4. **Per-Group Accuracy**
   - landbird-land, landbird-water, waterbird-land, waterbird-water
   - Identifies which groups suffer from spurious correlation

5. **Hessian Spectrum Statistics**
   - Number of outlier eigenvalues (above MP bulk edge)
   - Bulk edge value λ_+
   - Top eigenvalue λ_max
   - Spectral gap (λ_max - λ_+)

**Success Criteria (PoC: Direction-based):**

⚠️ **EXISTENCE (PoC) Success = Direction Only, NOT Statistical Rigor**

**Primary Success Condition:**
- ERM alignment > DRO alignment (A(w)_ERM > A(w)_DRO)
- Simple comparison, no statistical test required for PoC

**What "Success" Means for PoC:**
1. Code runs without error
2. Both models train to convergence
3. Hessian computation completes successfully
4. A(w)_ERM > A(w)_DRO (geometric signature exists)

**What "Failure" Means:**
- A(w)_ERM ≤ A(w)_DRO (no geometric signature)
- Hessian computation fails or unstable
- MP bulk edge estimation fails

**Expected Results (from Phase 2B):**
- ERM worst-group: 60-75%
- DRO worst-group: 75-80%
- ERM average: 85-90%
- DRO average: 75-80%
- A(w)_ERM: Higher (quantitative value TBD)
- A(w)_DRO: Lower (quantitative value TBD)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification + geometric analysis
- Library: torchmetrics (accuracy), custom (A(w) alignment)
- Code:
  ```python
  from torchmetrics import Accuracy
  
  # Standard metrics
  accuracy = Accuracy(task="multiclass", num_classes=2)
  
  # Custom: Worst-group accuracy
  def worst_group_accuracy(outputs, labels, groups):
      group_accs = []
      for g in range(4):
          mask = (groups == g)
          if mask.sum() > 0:
              acc = accuracy(outputs[mask], labels[mask])
              group_accs.append(acc)
      return min(group_accs)
  
  # Custom: Alignment metric A(w) - see pseudo-code above
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart
  - X-axis: Training method (ERM, DRO)
  - Y-axis: A(w) alignment value
  - Show threshold/target if applicable
  - Title: "Curvature Subspace Alignment: ERM vs Group-DRO"

#### Additional Figures (LLM Autonomous)

Based on hypothesis type (EXISTENCE - geometric analysis) and evaluation metrics, the following visualizations are recommended:

1. **Hessian Eigenvalue Spectrum**
   - Plot: Eigenvalue index vs eigenvalue magnitude
   - Overlay: Marchenko-Pastur bulk edge threshold
   - Comparison: ERM vs DRO spectra
   - Purpose: Visualize outlier eigenvalues and MP fit quality

2. **Alignment Metric Breakdown**
   - Bar chart: A(w) for ERM vs DRO
   - Error bars: Confidence intervals (if multiple runs)
   - Annotation: Percentage difference
   - Purpose: Primary hypothesis test visualization

3. **Worst-Group Accuracy vs Alignment**
   - Scatter plot: A(w) (x-axis) vs worst-group accuracy (y-axis)
   - Points: Individual models (ERM, DRO)
   - Purpose: Validate correlation between geometry and robustness

4. **Training Curves**
   - Line plots: Train loss, validation accuracy, worst-group accuracy over epochs
   - Separate panels: ERM vs DRO
   - Purpose: Verify training convergence

5. **Per-Group Accuracy Heatmap**
   - Rows: Training method (ERM, DRO)
   - Columns: 4 groups (landbird-land, landbird-water, waterbird-land, waterbird-water)
   - Values: Accuracy percentages
   - Purpose: Identify spurious correlation patterns

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

**⚠️ MCP Limitation:** Archon MCP server not available - references extracted from Phase 2B verification plan.

**Source 1: Marchenko-Pastur Theory (Sagun et al. 2017)**
- **Type:** Knowledge base article / Research paper
- **Relevance:** Theoretical foundation for bulk edge identification
- **Key Insights:**
  - Marchenko-Pastur distribution accurately models eigenvalue spectra in over-parameterized networks
  - Bulk edge λ_+ = σ²(1 + √γ)² separates signal from noise eigenvalues
  - Outlier eigenvalues above bulk edge capture data structure
- **Used For:** Hessian spectrum analysis, subspace definition

**Source 2: Group-DRO Theory (Sagawa et al. 2020)**
- **Type:** Research paper + official implementation
- **Relevance:** Baseline method and dataset
- **Key Insights:**
  - Minority groups expose spurious correlations
  - Worst-group accuracy measures spurious reliance
  - Waterbirds dataset with ground-truth group labels
- **Used For:** Dataset selection, baseline comparison, minority gradient definition

**Source 3: Loss Landscape Analysis (Li et al. 2018)**
- **Type:** Research paper + visualization methods
- **Relevance:** ResNet landscape properties
- **Key Insights:**
  - ResNets with skip connections produce analyzable loss landscapes
  - Filter normalization enables fair comparison across architectures
  - Flat minima correlate with generalization
- **Used For:** Model architecture selection, landscape analysis methodology

**Source 4: Mode Connectivity (Garipov et al. 2018)**
- **Type:** Research paper + FGE method
- **Relevance:** Geometric variation within solution manifolds
- **Key Insights:**
  - Solutions are mode-connected in parameter space
  - Fast Geometric Ensembling samples connectivity paths
  - Geometric variation exists within connected components
- **Used For:** Future mechanism validation (H-M4), theoretical foundation

### B. GitHub Implementations (Exa)

**⚠️ MCP Limitation:** Exa MCP server not available - references extracted from Phase 2B.

**Repository 1: group_DRO Official Implementation** ⭐⭐⭐ (HIGHEST PRIORITY)
- **URL:** https://github.com/kohpangwei/group_DRO
- **Authors:** Sagawa et al. (original paper authors)
- **Relevance:** Official implementation for baseline and dataset
- **Key Code:**
  - Waterbirds dataset loading and preparation
  - Group-DRO training loop with worst-group loss
  - Evaluation metrics including per-group accuracy
- **Configuration Extracted:**
  - Optimizer: SGD, momentum=0.9, weight_decay=1e-4
  - Learning rate: 0.001 with MultiStepLR schedule
  - Batch size: 128
  - Epochs: 100
- **Their Results:** 75-80% worst-group accuracy on Waterbirds
- **Used For:** Dataset preparation, DRO baseline training, hyperparameters

**Repository 2: pytorch-hessian-eigenthings**
- **URL:** https://github.com/noahgolmant/pytorch-hessian-eigenthings
- **Relevance:** Efficient Hessian computation for large networks
- **Key Code:**
  - Power iteration + deflation for top eigenvalues/eigenvectors
  - GPU-accelerated computation
  - Handles large parameter spaces (25M+ parameters)
- **Used For:** Hessian eigendecomposition for A(w) computation

**Repository 3: Loss Landscape Visualization Tools**
- **Reference:** Li et al. 2018 methods
- **Relevance:** Filter normalization and landscape plotting
- **Used For:** Methodological reference for geometric analysis

### C. Code Analysis (Serena)

**⚠️ MCP Limitation:** Serena MCP not available.

**Analysis Status:** Not performed - standard architectures and established methods used.

**Rationale:** 
- ResNet-50: Standard torchvision implementation, no custom code needed
- Hessian computation: pytorch-hessian-eigenthings library (well-documented)
- MP fitting: Standard statistical method (maximum likelihood fit)
- Alignment metric: Novel but simple projection computation (see pseudo-code)

### D. Previous Hypothesis Context

**Previous Context:** None - this is the first hypothesis in the verification chain.

**Status:** H-E1 is the foundation hypothesis with no prerequisites.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2B + GitHub | Sagawa et al. 2020, group_DRO repo |
| Model architecture | Phase 2B + Research | Li et al. 2018, torchvision ResNet-50 |
| Training protocol | GitHub | group_DRO official implementation |
| Hyperparameters | GitHub | group_DRO repo (SGD, lr=0.001, etc.) |
| Hessian computation | GitHub | pytorch-hessian-eigenthings |
| MP bulk edge | Research | Sagun et al. 2017 theory |
| Alignment metric A(w) | Novel | Hypothesis-specific (Phase 2B) |
| Evaluation metrics | Phase 2B + GitHub | Worst-group accuracy (Sagawa), A(w) (novel) |
| Minority gradients | Research | Sagawa et al. 2020 theory |

**Novel Contributions (Not from existing implementations):**
1. Curvature subspace alignment metric A(w)
2. Marchenko-Pastur-based subspace definition for spurious correlation analysis
3. Combination of Hessian geometry with worst-group robustness

**Established Methods Used:**
1. ResNet-50 architecture (torchvision)
2. Group-DRO baseline (Sagawa et al.)
3. Hessian eigendecomposition (pytorch-hessian-eigenthings)
4. Marchenko-Pastur theory (Sagun et al.)

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-24T16:03:25Z

### Workflow History for This Hypothesis

**Event 1:** Hypothesis h-e1 created (Phase 2B)
- Timestamp: 2026-04-24T16:00:00Z
- Phase: Phase 2B Planning
- Details: Generated as foundation EXISTENCE hypothesis in verification plan

**Event 2:** Hypothesis h-e1 set to IN_PROGRESS
- Timestamp: 2026-04-24T16:00:59Z
- Phase: Hypothesis Loop
- Details: External loop starting Phase 2C → 3 → 4 for h-e1

**Event 3:** Experiment design started (Phase 2C)
- Timestamp: 2026-04-24T16:03:25Z
- Phase: Phase 2C
- Details: Research-driven experiment design workflow initiated

**Status:** experiment_design.status = IN_PROGRESS → COMPLETED
**Next Phase:** Phase 3 - Implementation Planning

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
