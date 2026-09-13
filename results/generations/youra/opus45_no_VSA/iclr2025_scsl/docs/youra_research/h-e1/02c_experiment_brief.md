# Experiment Design: H-E1

**Date:** 2026-08-09
**Author:** Anonymous
**Hypothesis Statement:** SR ≈ 1 at initialization (no intrinsic curvature asymmetry)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (no prerequisites)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
SR₀ ∈ [0.9, 1.1] with 95% CI including 1.0

---

## Continuation Context

First hypothesis in verification chain. No previous context.

### Previous Hypothesis Results (if applicable)
N/A - This is the first hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Sharpness/Curvature Implementation**
- Limited direct results for sharpness ratio computation
- Found general neural network architecture patterns
- No specific SR initialization measurement code in KB

**Query 2: Loss Landscape / Hessian**
- No directly relevant results for group-wise Hessian eigenvalue computation
- General diffusion model references found (not applicable)

**Insight:** Archon KB lacks specific sharpness/curvature measurement implementations. Exa search provides better coverage.

### Archon Code Examples

- PyTorch tensor operations and model architectures found
- `torch.nn.utils.clip_grad_norm_` for gradient manipulation
- `scaled_dot_product_attention` implementation (not directly relevant)
- No Hessian eigenvalue computation code in KB

### Exa GitHub Implementations

**Query 1: Sharpness-Aware Minimization (SAM)**

**Repository 1**: [davda54/sam](https://github.com/davda54/sam) (⭐ Popular)
- **URL**: https://github.com/davda54/sam
- **Relevance**: SAM optimizer implementation with Hessian eigenvalue analysis
- **Key Insight**: Uses Lanczos algorithm for Hessian spectrum approximation
- **Reference**: https://github.com/google/spectral-density for Hessian spectra computation

**Repository 2**: [RitianLuo/EigenSAM](https://github.com/RitianLuo/EigenSAM)
- **URL**: https://github.com/RitianLuo/EigenSAM
- **Relevance**: Explicit top eigenvalue regularization via power method
- **Key Code**: Power method for top eigenvector estimation (q=5 iterations, every p=100 steps)

**Paper References (from Exa):**
1. Foret et al. (2022) "Sharpness-Aware Minimization" - SAM algorithm, Lanczos for Hessian spectrum
2. Agarwala et al. (2023) "SAM operates far from home" - Eigenvalue stabilization dynamics
3. Bartlett et al. (2023) "Dynamics of SAM" - Bouncing across ravines, spectral norm descent
4. Kaur et al. (2023) "Maximum Hessian Eigenvalue and Generalization" - λ_max as flatness metric

**Query 2: Waterbirds Dataset**

**Repository**: [kohpangwei/group_DRO](https://github.com/kohpangwei/group_DRO) (⭐ 294)
- **URL**: https://github.com/kohpangwei/group_DRO
- **Relevance**: Official Waterbirds dataset + Group DRO baseline
- **Dataset**: CUB-200-2011 + Places365 backgrounds
- **Groups**: 4 groups (waterbird/landbird × water/land background)
- **Confounder Strength**: 95% (majority groups)
- **Key Script**: `dataset_scripts/generate_waterbirds.py`

**Repository**: [PolinaKirichenko/deep_feature_reweighting](https://github.com/PolinaKirichenko/deep_feature_reweighting)
- **URL**: https://github.com/PolinaKirichenko/deep_feature_reweighting
- **Relevance**: Last-layer retraining for spurious correlation robustness
- **Insight**: ERM learns core features despite spurious correlations

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Use Case |
|----------|--------|----------|
| 1 | kohpangwei/group_DRO | Waterbirds dataset loading, group labels |
| 2 | google/spectral-density (Lanczos) | Hessian spectrum computation |
| 3 | PyHessian library | Alternative Hessian eigenvalue computation |

**Recommended Implementation Path:**
- Primary: Use `kohpangwei/group_DRO` for dataset + adapt Lanczos algorithm from SAM papers
- Fallback: PyHessian library for top eigenvalue computation
- Justification: Official Waterbirds implementation ensures correct group labels; Lanczos is standard for large-scale Hessian approximation

### Code Analysis (Serena MCP)

*Skipped* - No complex codebase to analyze. Implementation will be custom SR computation.

---

## Experiment Specification

### Dataset

**Name:** Waterbirds
**Type:** standard (composite: CUB-200-2011 + Places365)
**Source:** kohpangwei/group_DRO

**Statistics:**
- Training: ~4,795 samples
- Validation: ~1,199 samples
- Test: ~5,794 samples
- Classes: 2 (waterbird, landbird)
- Groups: 4 (bird_type × background_type)
- Minority group size: ~56 samples (landbird on water)

**Preprocessing:**
- Resize: 224×224
- Normalization: ImageNet mean/std ([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
- Center crop for validation/test

**Augmentation (Training):**
- RandomResizedCrop(224)
- RandomHorizontalFlip()

**Loading Information** (for Phase 4 download):
- Method: Custom (kohpangwei/group_DRO scripts)
- Identifier: CUB-200-2011 + Places365
- Code:
```python
# Download CUB-200-2011 and Places365
# Run: python dataset_scripts/generate_waterbirds.py
from data.waterbird_dataset import WaterbirdDataset
dataset = WaterbirdDataset(root='./data/waterbird_complete95_forest2water2', split='train')
```

### Models

#### Baseline Model

**Architecture:** ResNet-50
**Type:** CNN (pretrained on ImageNet)
**Source:** torchvision.models

**Configuration:**
- Backbone: ResNet-50 (pretrained=True)
- Final layer: Linear(2048, 2) for binary classification
- Freeze: None (full fine-tuning)

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: resnet50
- Code:
```python
import torchvision.models as models
model = models.resnet50(pretrained=True)
model.fc = torch.nn.Linear(2048, 2)
```

#### Proposed Model

**Architecture:** Baseline (no modification needed for H-E1)

**Note:** H-E1 is a measurement hypothesis, not an intervention. We measure SR at random initialization, not after training. No "proposed" model variant needed.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Sharpness Ratio (SR) Computation at Initialization
# Based on: Lanczos algorithm (Ghorbani et al. 2019), SAM papers

import torch
from torch.autograd.functional import hvp  # Hessian-vector product

def compute_group_sharpness(model, dataloader, group_mask, num_eigenvalues=5, num_iterations=20):
    """
    Compute top Hessian eigenvalue for a specific group using Lanczos iteration.
    
    Args:
        model: Neural network (at random init)
        dataloader: Group-specific data loader
        group_mask: Boolean mask for group membership
        num_eigenvalues: Number of top eigenvalues to compute
        num_iterations: Lanczos iterations
    Returns:
        lambda_max: Top eigenvalue (sharpness proxy)
    """
    # Collect parameters as flat vector
    params = torch.cat([p.view(-1) for p in model.parameters()])
    
    def hessian_vector_product(v):
        # Compute Hv using autograd
        loss = compute_loss(model, dataloader, group_mask)
        grads = torch.autograd.grad(loss, model.parameters(), create_graph=True)
        flat_grads = torch.cat([g.view(-1) for g in grads])
        hvp_result = torch.autograd.grad(flat_grads, model.parameters(), grad_outputs=v)
        return torch.cat([h.view(-1) for h in hvp_result])
    
    # Power iteration for top eigenvalue (simplified Lanczos)
    v = torch.randn_like(params)
    v = v / v.norm()
    for _ in range(num_iterations):
        Hv = hessian_vector_product(v)
        lambda_max = torch.dot(v, Hv)
        v = Hv / Hv.norm()
    
    return lambda_max.item()

def compute_sharpness_ratio(model, dataloader, group_labels):
    """
    Compute SR = sharpness(minority) / sharpness(majority)
    """
    # Groups: 0=landbird/land, 1=landbird/water(minority), 2=waterbird/land(minority), 3=waterbird/water
    minority_groups = [1, 2]  # Minority = mismatched bird/background
    majority_groups = [0, 3]  # Majority = matched bird/background
    
    sharpness_minority = np.mean([compute_group_sharpness(model, dataloader, g) for g in minority_groups])
    sharpness_majority = np.mean([compute_group_sharpness(model, dataloader, g) for g in majority_groups])
    
    SR = sharpness_minority / sharpness_majority
    return SR

# Expected: SR₀ ≈ 1.0 at random initialization
```

### Training Protocol

**Note:** H-E1 does NOT require training. This is a measurement-only experiment at random initialization.

**Protocol:**
1. Initialize ResNet-50 with random weights (5 different seeds)
2. Load Waterbirds dataset with group labels
3. Compute SR₀ for each seed
4. Report mean SR₀ and 95% CI

**Seeds:** 5 (for statistical confidence)
**Epochs:** 0 (no training)
**Compute:** ~5 minutes per seed (Hessian computation)

### Evaluation

**Primary Metric:** SR₀ (Sharpness Ratio at initialization)

**Success Criteria (MUST_WORK gate):**
- SR₀ ∈ [0.9, 1.1]
- 95% CI includes 1.0

**Falsification:**
- SR₀ > 1.1 with CI excluding 1.0 → Intrinsic asymmetry exists → Main hypothesis threatened

**Expected Result:** SR₀ ≈ 1.0 (no bias at random init)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: measurement (not classification)
- Library: numpy/scipy for statistics
- Code:
```python
import numpy as np
from scipy import stats

sr_values = [compute_sharpness_ratio(model_seed_i, dataloader, groups) for i in range(5)]
mean_sr = np.mean(sr_values)
ci_95 = stats.t.interval(0.95, len(sr_values)-1, loc=mean_sr, scale=stats.sem(sr_values))
print(f"SR₀ = {mean_sr:.3f}, 95% CI = [{ci_95[0]:.3f}, {ci_95[1]:.3f}]")
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: SR₀ values across seeds with error bars, horizontal line at SR=1.0

#### Additional Figures (LLM Autonomous)
- SR₀ distribution histogram across seeds
- Hessian eigenvalue spectrum comparison (minority vs majority groups)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: Yes - SR computation is defined
- `mechanism_isolatable`: Yes - Measurement only, no training
- `baseline_measurable`: Yes - Random init is the baseline

### Architecture Compatibility
- ResNet-50 supports gradient computation through all layers
- Hessian-vector product computable via PyTorch autograd

### Activation Indicators
- `mechanism_log_message`: "Computing SR for group {group_id}..."
- `tensor_shape_change`: N/A (measurement only)
- `metric_delta_expected`: SR should be ~1.0 ± 0.1

### Verification Code
```python
# Verify SR computation works
model = create_random_model(seed=42)
sr_test = compute_sharpness_ratio(model, test_loader, group_labels)
assert 0.5 < sr_test < 2.0, f"SR computation failed: {sr_test}"
print(f"✓ Mechanism verified: SR = {sr_test:.3f}")
```

### Hypothesis Support Threshold
- `hypothesis_support_metric`: SR₀
- `hypothesis_support_threshold`: SR₀ ∈ [0.9, 1.1] AND 95% CI includes 1.0

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. SR₀ computed for all 5 seeds
3. Mean SR₀ ∈ [0.9, 1.1]
4. 95% CI includes 1.0

---

## Appendix: Reference Implementations

### Hessian Computation
1. **PyHessian**: https://github.com/amirgholami/PyHessian
   - Top eigenvalue via power iteration
   - Trace estimation via Hutchinson

2. **Spectral Density (Google)**: https://github.com/google/spectral-density
   - Full Lanczos algorithm implementation
   - Used in SAM paper for Figure 3

3. **SAM Repository**: https://github.com/davda54/sam
   - Example of sharpness-aware training
   - References Lanczos implementation

### Waterbirds Dataset
1. **Official**: https://github.com/kohpangwei/group_DRO
   - Dataset generation script
   - Group labels (4 groups)
   - Standard splits

2. **DFR**: https://github.com/PolinaKirichenko/deep_feature_reweighting
   - Alternative Waterbirds loader
   - Last-layer retraining baseline

### Key Papers
1. Foret et al. (2022) "Sharpness-Aware Minimization for Efficiently Improving Generalization"
2. Sagawa et al. (2020) "Distributionally Robust Neural Networks for Group Shifts"
3. Ghorbani et al. (2019) - Lanczos algorithm for Hessian spectrum

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-09

### Workflow History for This Hypothesis
- 2026-08-09: Phase 2C started (experiment design)
- 2026-08-09: Phase 2C completed (experiment brief generated)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
