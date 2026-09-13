# Limitation Record: h-m2 (Run 1)

**Date:** 2026-08-29T00:39:00Z  
**Hypothesis:** h-m2  
**Run:** 1  
**Gate Type:** SHOULD_WORK  
**Result:** LIMITATION_RECORDED  
**Pipeline Status:** Continued (not blocked)

## Limitation Details

Architecture comparison (ResNet-50 vs ViT-B/16) on CMNIST with 70% accuracy threshold showed **opposite effect** from predicted direction:
- ResNet-50: Δ = 0 epochs (no temporal gap)
- ViT-B/16: Δ = 1 epoch (small gap)
- Difference: -1 epochs (ViT > ResNet, opposite of hypothesis)

Gate threshold (Δ_ResNet - Δ_ViT ≥ 2 epochs) not met.

## Failed Checks

- Gate threshold: Δ_ResNet - Δ_ViT = -1 < 2 epochs (FAIL)
- Direction: ViT showed larger gap than ResNet (opposite of predicted)
- Convergence speed: Both architectures converged epoch 1-2 (too fast for meaningful comparison)

## Partial Results

| Metric | Value |
|--------|-------|
| ResNet-50 E_spurious | 1 |
| ResNet-50 E_core | 1 |
| ResNet-50 Δ | 0 |
| ViT-B/16 E_spurious | 1 |
| ViT-B/16 E_core | 2 |
| ViT-B/16 Δ | 1 |
| Difference (ResNet - ViT) | -1 |
| Gate threshold | 2 |
| Gate result | FAIL |

## Experiment Summary

**Dataset:** CMNIST (10% subset, ~6000 train samples)  
**Convergence criterion:** 70% accuracy (lowered from 90% due to spurious correlation strength)  
**Training:** 30 epochs max, SGD + momentum 0.9  
**Masking:**
- Spurious-only: Gaussian blur (kernel=31) to remove digit shape, keep color
- Core-only: Grayscale to remove color, keep digit shape

**Results:** Both architectures converged extremely fast (1-2 epochs), indicating:
1. 70% threshold too low for CMNIST task difficulty
2. Color cue dominates both architectures equally
3. No architectural difference in temporal dynamics at this threshold
4. Opposite direction suggests ViT slightly more sensitive to shape (grayscale) than ResNet

## Context

This limitation was recorded but **did not block the pipeline**.
The hypothesis proceeded to Phase 5 with this limitation noted.

Future research attempts should consider:
1. Raising accuracy threshold to 85-90% to distinguish temporal dynamics
2. Using harder datasets (Waterbirds, CelebA) with stronger spurious/core feature separation
3. Testing with longer training (100+ epochs) to capture convergence differences
4. Verifying masking strategy preserves architectural differences (grayscale may not sufficiently isolate "core" features for ViT)

---

## When This Memory Is Read

- **Phase 0:** If pipeline routes back to Phase 0 (from Phase 5 PARTIAL),
  this limitation informs brainstorming to avoid similar issues
- **Phase 6 Discussion:** Limitation is included in paper's Limitations section

---
*Limitation recorded at: 2026-08-29T00:39:00Z*  
*For cross-phase reference*
