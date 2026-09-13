# Step 06b Reflection Report: h-m2

**Date:** 2026-05-21T04:10:00Z
**Hypothesis:** h-m2
**Gate Type:** MUST_WORK
**Gate Result:** FAIL
**Reflection Outcome:** ROUTED_TO_PHASE_0

---

## 1. Experiment Summary

**Hypothesis Statement:**
Under weight space analysis on Small CNN Zoo checkpoint trajectories, if weight vectors are projected onto permutation orbit directions and GL orbit directions, then Var_perm / (Var_perm + Var_GL) > 0.60.

**Key Results:**
- `var_ratio_mean` = 0.3479 ± 0.054 (threshold: > 0.60) → **FAIL**
- Conv2d layers: ratio = 0.637 → **PASS**
- Linear layers: ratio = 0.133 → **FAIL**
- n_models = 1000 (CIFAR-10-GS only; SVHN had 0 models)
- Epoch trajectory: ratio decreases 0.49 (epoch 0) → 0.28 (epoch 50)

---

## 2. Reflection Analysis

### 2.1 What Succeeded

- Conv2d layers show permutation orbit dominance (0.637 > 0.60 ✅)
- Orbit basis computation is successful (orbit_basis_dim=64)
- Large-scale validation (1000 models × 50 epochs) confirms statistical reliability
- The h-m2 gate pre-specified the correct pivot: "hybrid orbit-PE + GL trace features"

### 2.2 What Failed

- Overall var_ratio_mean = 0.3479, well below 0.60 threshold
- Linear/FC layers: GL orbit variance dominates (ratio=0.133 ≪ 0.60)
- The fundamental assumption — that permutation orbits dominate across ALL layer types — is empirically false for Linear layers

### 2.3 Root Cause Analysis

1. **Layer type asymmetry is fundamental**: Conv2d and Linear layers have structurally different orbit geometries. Convolutional weights have spatial structure that makes permutation orbits dominant; FC layer weights organize differently under training dynamics.
2. **Training dynamics amplify GL variance in Linear layers**: The epoch-trajectory analysis shows ratio decreases monotonically during training. As FC layers learn task-specific representations, GL-type variance increases. This is not an implementation bug.
3. **NFN success argument was overgeneralized**: NFN's permutation equivariance success is specific to its architecture (predominantly convolutional). Generalizing to mixed CNN architectures with FC classifiers was invalid.
4. **Missing SVHN data**: Cross-dataset stability check was incomplete (n_svhn=0), but this does not change the primary FAIL verdict.

### 2.4 Meaningful Findings

Despite FAIL, the experiment produced scientifically valuable findings:
- **Conv2d orbit structure confirmed** → orbit-PE is valid for convolutional layers
- **Linear layer GL dominance quantified** → informs hybrid encoding design
- **Training trajectory insight** → novel finding on how orbit ratio evolves during training (decreases with more training)

---

## 3. Decision Matrix

| Criterion | Value | Assessment |
|-----------|-------|------------|
| Gate type | MUST_WORK | Mandatory gate |
| Gate result | FAIL (not PARTIAL) | Complete failure of primary criterion |
| modification_attempt | 0 | First attempt |
| Is failure fundamental? | YES | Mathematical property, not implementation bug |
| SELF_MODIFY possible? | NO | Would require changing hypothesis statement (different mechanism) |

**Decision: ROUTED_TO_PHASE_0**

FAIL gate (not PARTIAL) → no self-modification path. The hypothesis mechanism claim is empirically falsified. Route to Phase 0 for hypothesis redesign incorporating the empirical findings.

---

## 4. Routing Decision

**Route To:** Phase 0 (hypothesis redesign)
**Reason:** MUST_WORK gate FAIL — permutation orbit variance does not dominate for Linear layers (ratio=0.133 vs threshold 0.60)
**Pre-specified Pivot (from h-m2 gate condition):** Hybrid orbit-PE + GL trace features

### Cascade Effects

- **h-m3**: Blocked (prerequisite h-m2 FAILED)
- **h-c1**: Cascade blocked (prerequisite h-m2 FAILED)

---

## 5. Lessons for Phase 0

1. **Layer-type-specific encoding**: New hypothesis must differentiate Conv2d (permutation orbit) from Linear (GL orbit or hybrid)
2. **Hybrid orbit-PE + GL trace features**: Explicitly encode GL orbit information for Linear layers
3. **Preserved findings**: h-e1 (orbit-PE computable) + h-m1 (efficient implementation) remain valid
4. **New mechanism claim**: "Hybrid orbit encoding captures dominant variance across both Conv2d (permutation) and Linear (GL) layer types"
5. **Consider GL trace features**: GL orbit variance for Linear layers suggests trace-based features may capture meaningful geometry

---

## 6. Serena Memory Written

- `failure_h-m2_run2`: Phase 4 reflection failure record with pivot directions for Phase 0

---

*Reflection executed: 2026-05-21T04:10:00Z*
*Step 06b (automatic reflection) — UNATTENDED mode*
*Next: Step 07 (report generation) → Step 08 (completion)*
