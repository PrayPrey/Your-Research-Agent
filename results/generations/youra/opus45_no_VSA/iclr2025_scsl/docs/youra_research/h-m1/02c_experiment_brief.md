# Experiment Design: H-M1

**Date:** 2026-08-09
**Author:** Anonymous
**Hypothesis Statement:** Per-sample gradient ratio decay precedes SR divergence (τ_r→SR > 0)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing causal relationship via temporal precedence.

---

## Workflow Status

**Verification State:** EXPERIMENT_DESIGN_COMPLETED
**Prerequisites Satisfied:** H-E1 (VALIDATED - SR ≈ 1 at initialization confirmed)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition
τ_r→SR > 0 with 95% CI excluding zero across seeds. Gradient ratio decay must temporally precede SR divergence.

---

## Continuation Context

H-E1 established baseline: SR₀ = 0.9999 (95% CI [0.9953, 1.0046]) at random initialization. No intrinsic curvature asymmetry exists before training. H-M1 tests whether differential gradient magnitudes between groups cause SR to diverge during training.

### Previous Hypothesis Results (if applicable)
- **H-E1 Result:** PASS - Mean SR = 0.9999 at random init, 95% CI includes 1.0
- **Implication:** Any SR > 1 during training is caused by training dynamics, not initialization

---

## Implementation Research Summary

### Archon Knowledge Base Findings

- No direct match for sharpness ratio / gradient group fairness in knowledge base
- Training loop patterns available (diffusers examples)
- General PyTorch training infrastructure patterns applicable

### Archon Code Examples

- Training loop pattern: `loss.backward()` → `optimizer.step()` cycle
- Gradient computation via standard PyTorch autograd

### Exa GitHub Implementations

**Per-Sample Gradient Computation:**
- PyTorch `torch.func.vmap` + `torch.func.grad` for efficient per-sample gradients
- Opacus library: backward hooks with `einsum` for vectorized computation
- `register_module_full_backward_hook` for capturing gradient flow

**Cross-Correlation Analysis:**
- `scipy.signal.correlate` + `correlation_lags` for lag computation
- `statsmodels.tsa.stattools.ccf` for normalized cross-correlation with confidence intervals
- Normalization: subtract mean, divide by std×len for Pearson-style correlation

**Waterbirds Dataset:**
- Official: `kohpangwei/group_DRO` repository (MIT License)
- HuggingFace: `arubique/waterbirds`
- 4 groups: landbird/waterbird × land/water background
- 95% confounder strength (majority groups dominate)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

1. **Waterbirds Dataset**: Use official `kohpangwei/group_DRO` generation script or HuggingFace mirror
2. **Per-sample Gradients**: Use `torch.func.vmap` + `grad` (PyTorch native, no Opacus dependency)
3. **Cross-correlation**: Use `scipy.signal.correlate` + `correlation_lags` (most flexible)

**Recommended Implementation Path:**
- Primary: PyTorch `torch.func` for per-sample gradients (official tutorial pattern)
- Fallback: Manual loop with `torch.autograd.grad` per sample
- Justification: `torch.func.vmap` is 10-100x faster than manual loop, officially supported

### Code Analysis (Serena MCP)

*Skipped - no existing codebase to analyze for this novel mechanism experiment*

---

## Experiment Specification

### Dataset

**Name:** Waterbirds
**Type:** standard
**Source:** kohpangwei/group_DRO (official) or HuggingFace arubique/waterbirds
**Groups:** 4 (landbird_land, landbird_water, waterbird_land, waterbird_water)
**Confounder Strength:** 95% (majority groups dominate)
**Splits:** Train ~4,795 / Val ~1,199 / Test ~5,794

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets or custom loader from group_DRO repo
- Identifier: `arubique/waterbirds` or local generation from CUB-200 + Places
- Code:
```python
from datasets import load_dataset
dataset = load_dataset("arubique/waterbirds")
# OR use kohpangwei/group_DRO/dataset_scripts/generate_waterbirds.py
```

**Preprocessing:**
- Resize: 224×224
- Normalize: ImageNet mean/std ([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
- Train augmentation: RandomResizedCrop(224), RandomHorizontalFlip

### Models

#### Baseline Model

**Architecture:** ResNet-50 pretrained on ImageNet
**Final Layer:** Replace fc with Linear(2048, 2) for binary classification
**Source:** torchvision.models

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: resnet50
- Code:
```python
import torchvision.models as models
model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
model.fc = nn.Linear(2048, 2)
```

#### Proposed Model

**Architecture:** Baseline + Per-epoch gradient ratio and SR logging

**Core Mechanism Implementation:**

```python
# Core Mechanism: Gradient Ratio & SR Time-Series Logging
# Based on: PyTorch torch.func per-sample gradients + scipy cross-correlation

def compute_per_sample_grad_norms(model, params, buffers, data, targets, loss_fn):
    """Compute per-sample gradient L2 norms using torch.func.vmap."""
    from torch.func import grad, vmap, functional_call
    
    def compute_loss(params, buffers, sample, target):
        pred = functional_call(model, (params, buffers), (sample.unsqueeze(0),))
        return loss_fn(pred, target.unsqueeze(0))
    
    ft_grad = grad(compute_loss)
    ft_sample_grad = vmap(ft_grad, in_dims=(None, None, 0, 0))
    grads = ft_sample_grad(params, buffers, data, targets)
    # Compute L2 norm per sample across all params
    norms = torch.stack([g.flatten(1).norm(dim=1) for g in grads.values()]).sum(0)
    return norms  # (batch_size,)

def compute_gradient_ratio(grad_norms, group_labels):
    """Compute ratio of majority to minority group gradient norms."""
    majority_mask = (group_labels == 0) | (group_labels == 3)  # landbird_land, waterbird_water
    minority_mask = ~majority_mask
    r = grad_norms[majority_mask].mean() / grad_norms[minority_mask].mean()
    return r

def compute_sharpness_ratio(model, data_loader, epsilon=0.01):
    """Compute SR = max_eigenvalue(H_minority) / max_eigenvalue(H_majority)."""
    # Approximate via gradient norm under perturbation (power iteration proxy)
    # Full Hessian eigenvalue computation deferred to detailed implementation
    pass  # Placeholder - actual implementation uses torch.autograd.functional.hvp

def compute_lagged_cross_correlation(r_series, sr_series, max_lag=5):
    """Compute τ_r→SR: lag at which r best predicts SR."""
    from scipy.signal import correlate, correlation_lags
    r_norm = (r_series - r_series.mean()) / r_series.std()
    sr_norm = (sr_series - sr_series.mean()) / sr_series.std()
    corr = correlate(sr_norm, r_norm, mode='full') / len(r_series)
    lags = correlation_lags(len(sr_norm), len(r_norm), mode='full')
    valid = (lags >= -max_lag) & (lags <= max_lag)
    tau = lags[valid][np.argmax(corr[valid])]
    return tau, corr[valid], lags[valid]
```

### Training Protocol

**Optimizer:** SGD
- momentum: 0.9
- weight_decay: 1e-4
- **Source:** group_DRO paper defaults

**Learning Rate:** 1e-3
- **Source:** group_DRO paper

**Schedule:** StepLR
- step_size: 10
- gamma: 0.1

**Batch Size:** 128
- **Source:** group_DRO paper

**Epochs:** 50
- **Source:** Sufficient for SR divergence observation

**Loss Function:** CrossEntropyLoss

**Seeds:** 5 (for 95% CI computation)

**Per-Epoch Logging:**
- Gradient ratio r_t (majority/minority gradient norm ratio)
- Sharpness ratio SR_t (minority/majority curvature ratio)

### Evaluation

**Primary Metrics:**
- τ_r→SR: Lagged cross-correlation peak lag between gradient ratio decay and SR divergence
- 95% CI for τ_r→SR across 5 seeds

**Success Criteria:**
- τ_r→SR > 0 (gradient ratio decay temporally precedes SR divergence)
- 95% CI excludes zero

**Expected Baseline Performance:**
- SR₀ ≈ 1.0 at init (established by H-E1)
- SR > 1.2 by epoch 30-50 under ERM training (from prior literature on group imbalance)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Time-series analysis
- Library: scipy.signal, numpy
- Code:
```python
from scipy.signal import correlate, correlation_lags
import numpy as np
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: τ_r→SR lag correlation plot showing:
  - X-axis: lag (epochs), Y-axis: cross-correlation
  - Peak at positive lag confirms temporal precedence
  - 95% CI band across seeds

#### Additional Figures (LLM Autonomous)
- Time series plot: r_t and SR_t over epochs (dual y-axis)
- Per-seed τ values with mean and CI
- Heatmap: correlation at each lag × seed

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. τ_r→SR > 0 with 95% CI excluding zero

---

## Appendix: Reference Implementations

### Per-Sample Gradient Computation
- **PyTorch Official Tutorial:** https://docs.pytorch.org/tutorials/intermediate/per_sample_grads.html
- **Pattern:** `torch.func.vmap(grad(compute_loss))` for efficient batch computation
- **Alternative:** Opacus library with backward hooks and einsum

### Cross-Correlation Analysis
- **SciPy:** `scipy.signal.correlate` + `correlation_lags`
- **Statsmodels:** `statsmodels.tsa.stattools.ccf` with confidence intervals
- **Normalization:** Subtract mean, divide by std×len for Pearson correlation

### Waterbirds Dataset
- **Official Repository:** https://github.com/kohpangwei/group_DRO
- **Paper:** Sagawa et al. "Distributionally Robust Neural Networks for Group Shifts" (2019)
- **HuggingFace Mirror:** arubique/waterbirds
- **Generation Script:** dataset_scripts/generate_waterbirds.py (requires CUB-200 + Places)

### Group DRO Training
- **Paper:** arXiv:1911.08731
- **Key Insight:** Regularization (L2 + early stopping) critical for worst-group generalization
- **Hyperparameters:** SGD, lr=1e-3, batch=128, momentum=0.9, weight_decay=1e-4

### Training Dynamics Literature
- **Spectral Edge Dynamics:** Xu (2026) - rolling-window SVD reveals spectral edge
- **Correlated Mode Decomposition:** Brokman et al. (ICLR 2024) - parameter correlation over epochs
- **SGD Noise Correlations:** Kühn & Rosenow - epoch-based anti-correlations

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-09T19:00:00Z

### Workflow History for This Hypothesis
- H-E1 VALIDATED: SR ≈ 1 at initialization (Mean SR = 0.9999, 95% CI [0.9953, 1.0046])
- H-M1 IN_PROGRESS: Experiment design COMPLETED

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Code Context)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
