# Hypothesis h-m2: Attention Correction Mechanism

**ID**: h-m2  
**Type**: MECHANISM  
**Gate**: SHOULD_WORK (mechanism hypothesis)  
**Status**: Experiment design complete, ready for Phase 3  
**Archon Task ID**: 477802a1-5780-457f-9d7b-a6cf7081730f

---

## Statement

ViT or ResNet-CBAM shows steeper worst-group gap reduction slope (≥0.3pp/epoch more negative) from epoch 20-50 than ResNet-BN on Waterbirds.

---

## Motivation

Tests whether attention mechanisms enable mid-training correction of spurious features. CBAM isolates channel+spatial attention while preserving ResNet's local architecture. ViT tests global self-attention (confounded: global receptive field + parameter count).

If confirmed, informs architecture selection for spurious correlation robustness.

---

## Prerequisites

**h-e1** (EXISTENCE hypothesis) — must validate before h-m2 starts Phase 2C.

Status: h-e1 VALIDATED (gap difference 9.41pp, p=5.43e-05, d=3.94)

---

## Dependencies

None — h-m2 does NOT block other hypotheses (SHOULD_WORK gate).

Sibling hypotheses (also depend on h-e1):
- h-m1 (BN amplification mechanism)
- h-c1 (signature consistency condition)

---

## Success Criterion

- (ResNet-CBAM OR ViT) shows steeper negative slope than ResNet-BN by ≥0.3pp/epoch AND
- Non-overlapping 95% confidence intervals AND
- Cohen's d ≥ 0.8 (large effect size)

Statistical power: 10 seeds, 31-epoch window (epochs 20-50) provides robust slope estimation.

---

## Falsification Criterion

- Both CBAM and ViT CIs overlap with ResNet-BN CI OR
- Slope difference < 0.2pp/epoch OR
- Cohen's d < 0.5 (medium effect)

**Interpretation if falsified**: Attention does NOT enable mid-training correction under these conditions (constant LR, 100 epochs). Document null result (publishable finding).

**Partial success (ViT only)**: Weaken claim to "global architecture enables correction, not attention alone."

---

## Experiment Overview

**Dataset**: Waterbirds (same as h-e1)  
**Architectures**: ResNet-18-BN (control), ResNet-18-CBAM (ablation), ViT-Small (global attention)  
**Training**: 10 seeds × 100 epochs × constant LR=0.01  
**Analysis**: Linear regression slope of worst-group gap over epochs 20-50  
**Test**: Bootstrap 95% CI comparison, Cohen's d effect size

---

## Next Phase Actions

### Phase 3 (Implementation Planning)
1. Initialize Archon project with experiment brief
2. Generate PRD: slope-based trajectory analysis for 3 architectures
3. Generate Architecture document:
   - Module 1: Data loader (reuse h-e1)
   - Module 2: ResNet-CBAM implementation (~50 lines CBAM module)
   - Module 3: ViT-Small integration (timm library)
   - Module 4: Training loop (3 architectures × 10 seeds)
   - Module 5: Slope computation (scipy linear regression + bootstrap CI)
4. Break into Epic tasks:
   - EPIC-MODEL-CBAM: CBAM attention module
   - EPIC-MODEL-VIT: ViT-Small integration
   - EPIC-TRAIN: Multi-architecture training
   - EPIC-EVAL: Slope analysis and statistical test

### Phase 4 (PoC Validation)
1. Implement and execute experiment
2. Validate: trajectory plots, slope CIs, statistical tests
3. Generate 04_validation.md report

### Phase 5 (Conditional)
- SHOULD_WORK gate → h-m2 failure does NOT block Phase 5 baseline comparison
- Null result is publishable (architectural limitation documented)

---

## Risk Summary

| Risk | Mitigation |
|------|------------|
| ViT convergence instability | Gradient clipping, reduce LR to 0.001 for ViT if needed |
| CBAM implementation bug | Validate on CIFAR-10 first, compare with reference |
| Epoch 20-50 misses correction phase | Plot full trajectories, test alternative windows |
| High variance (wide CIs) | 10 seeds provides 80% power; accept uncertainty if needed |

---

**Phase 2C Status**: COMPLETED  
**Ready for Phase 3**: YES (h-e1 prerequisite validated)  
**Blocking Issues**: NONE
