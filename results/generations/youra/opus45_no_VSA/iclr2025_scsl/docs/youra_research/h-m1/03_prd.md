# Product Requirements Document: H-M1

**Hypothesis:** Per-sample gradient ratio decay precedes SR divergence (τ_r→SR > 0)
**Type:** MECHANISM
**Date:** 2026-08-09
**Author:** Anonymous

---

## 1. Executive Summary

Implement temporal precedence analysis for gradient ratio and sharpness ratio dynamics during ERM training on Waterbirds dataset. Goal: demonstrate τ_r→SR > 0 (gradient decay precedes curvature divergence).

---

## 2. Problem Statement

H-E1 established SR ≈ 1 at initialization. H-M1 tests the causal hypothesis: differential gradient magnitudes between majority/minority groups cause SR to diverge during training. Success requires temporal precedence evidence via cross-correlation analysis.

---

## 3. Functional Requirements

### FR-1: Data Pipeline
- Load Waterbirds dataset (4 groups: landbird_land, landbird_water, waterbird_land, waterbird_water)
- Apply standard preprocessing: 224×224 resize, ImageNet normalization
- Track group labels per sample for gradient ratio computation

### FR-2: Model Architecture
- ResNet-50 pretrained on ImageNet
- Replace final fc layer: Linear(2048, 2)
- No architectural modifications beyond standard ERM

### FR-3: Per-Sample Gradient Computation
- Implement `torch.func.vmap` + `grad` for efficient per-sample gradients
- Compute L2 norm per sample across all parameters
- Group by majority (groups 0,3) vs minority (groups 1,2)
- Output: gradient ratio r_t = mean(majority_norms) / mean(minority_norms)

### FR-4: Sharpness Ratio Computation
- Compute SR_t = max_eigenvalue(H_minority) / max_eigenvalue(H_majority)
- Use power iteration or Lanczos approximation for Hessian top eigenvalue
- Log per epoch

### FR-5: Cross-Correlation Analysis
- Compute lagged cross-correlation between r_t and SR_t time series
- Find τ_r→SR: lag at which correlation peaks
- Compute 95% CI across 5 seeds

### FR-6: Visualization
- Gate metrics figure: τ vs correlation plot with 95% CI band
- Time series plot: r_t and SR_t over epochs (dual y-axis)
- Per-seed τ values with mean and CI

---

## 4. Data Specification

### Primary Dataset
- **Name:** Waterbirds
- **Source:** kohpangwei/group_DRO or HuggingFace arubique/waterbirds
- **Splits:** Train ~4,795 / Val ~1,199 / Test ~5,794
- **Groups:** 4 (95% confounder strength)

### Preprocessing
- Resize: 224×224
- Normalize: ImageNet mean/std
- Train augmentation: RandomResizedCrop(224), RandomHorizontalFlip

---

## 5. Success Criteria

### Primary Gate (MUST_WORK)
- τ_r→SR > 0 with 95% CI excluding zero
- Gradient ratio decay temporally precedes SR divergence

### Secondary Metrics
- SR > 1.2 by epoch 30-50 (expected from prior literature)
- Reproducibility across 5 seeds

---

## 6. Non-Functional Requirements

- Training time: ~2-4 hours per seed on single GPU
- Memory: <16GB GPU for batch size 128
- Reproducibility: Seeded random states

---

## 7. Dependencies

### 7.1 Python Packages
```
torch>=2.0
torchvision
scipy
numpy
matplotlib
datasets  # HuggingFace
```

### 7.2 External References
- group_DRO paper: arXiv:1911.08731
- PyTorch per-sample gradients tutorial

---

## 8. Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Hessian computation expensive | Use power iteration approximation |
| SR may not diverge significantly | Extend to 50+ epochs if needed |
| τ = 0 (no temporal precedence) | Report as negative result |

---

*Generated for Phase 3 Implementation Planning*
