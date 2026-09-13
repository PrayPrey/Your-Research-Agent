# Failure Memory: h-e1-v2 SUPERSEDED

**Hypothesis ID:** h-e1-v2
**Gate Result:** PARTIAL (2/3)
**Reflection Outcome:** SUPERSEDED
**Date:** 2026-03-16
**Pipeline:** YouRA / Spurious Correlations & Shortcut Learning

---

## What Failed

The oscillation_index criterion (OI < 0) was not satisfied.

- **Observed OI:** +1.00 (positive/aligned)
- **Required OI:** < 0.0 (negative/opposing)

The bug from h-e1 (OI=NaN) was **correctly fixed** — nu1 is now available at epoch 5.
But the fixed OI reveals the criterion itself is wrong.

---

## Root Cause

The cosine similarity between **mean minority gradient projections** and **mean majority gradient projections** onto nu1 (top Hessian eigenvector) is +1.0 at epoch 5.

Both groups project their gradients in the **same direction** onto nu1. The "opposing signal" in Rosenfeld & Risteski (2023) does NOT manifest as directional opposition in the nu1 projection space for this setting.

**The spurious correlation mechanism manifests as:**
- Gradient **magnitude disparity** (6.37x–14.73x ratio) ✅ confirmed
- Loss asymmetry (minority_loss >> majority_loss at all epochs) ✅ confirmed
- NOT directional opposition on nu1 ❌ criterion invalid

---

## What Was Confirmed (carry forward)

| Finding | Value |
|---------|-------|
| gradient_norm_ratio | 6.37x (epoch 5), 14.73x (epoch 4) |
| lambda1 EOS dynamics | 689.7 → 586.1 → 545.5 (all >> 500 threshold) |
| Nu1 background alignment | -0.301, -0.039, -0.288 (anti-correlated with spurious feature) |
| Loss asymmetry | Group 2 loss 0.9238 vs Group 0 loss 0.0189 at epoch 5 |

---

## Routing Decision

SUPERSEDED → Phase 2A-Dialogue for hypothesis redesign.

modification_attempt=1 at max (max_attempts=1).
LLM assessment: Interface ✓, Data ✓, Behavior ✗, Recoverability ✗.

---

## New Hypothesis Direction

The new existence criterion should explore:
1. **Magnitude-based opposing signal**: gradient norm ratio >> 2x IS the criterion (already confirmed)
2. **Loss asymmetry**: minority_loss / majority_loss > threshold as primary indicator
3. **Multi-eigenvector analysis**: nu2, nu3, ... may show directional opposition where nu1 does not
4. **Alternative oscillation metrics**: per-class gradient direction divergence (not mean projections)
5. **Later epochs**: OI at epoch 5 is early training — directional divergence may emerge at epochs 10-20

---

## Validated Infrastructure (reuse in new hypothesis)

- Dataset loading: Waterbirds with group-stratified DataLoader ✅
- ResNet-50 ERM training loop with group loss tracking ✅
- Per-sample gradient norm computation ✅
- Hessian eigenvalue computation via PyHessian ✅
- Nu1 background alignment computation ✅
- Gradient vector collection (collect_gradient_vectors) ✅
- Hyperparameters: lr=0.001, momentum=0.9, wd=1e-4, epochs=20, bs=128 ✅
- EOS threshold = 500.0 (empirically validated) ✅
