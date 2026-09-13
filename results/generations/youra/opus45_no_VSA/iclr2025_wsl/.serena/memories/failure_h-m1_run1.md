# Phase 4 Failure Record: h-m1 (Run 1)

**Date:** 2026-08-09T16:30:00Z
**Hypothesis:** h-m1
**Run:** 1
**Final Status:** FAIL
**Failure Type:** HYPOTHESIS_FALSIFIED
**Gate Type:** MUST_WORK

## Hypothesis Statement

ED vs EcD PR comparison rules out contrastive-induced compression — ED PR ≤ EcD PR confirms bounded d* is intrinsic, not encoder artifact.

## Experimental Results

| Latent Size L | ED PR | EcD PR | Comparison |
|---------------|-------|--------|------------|
| 16 | 13.01 | 3.65 | ED >> EcD |
| 32 | 23.55 | 4.01 | ED >> EcD |
| 64 | 37.35 | 4.09 | ED >> EcD |

## Key Findings

1. ED PR scales linearly with L (no saturation): L=16→13.01, L=32→23.55, L=64→37.35
2. EcD PR saturates at ~4: L=16→3.65, L=32→4.01, L=64→4.09
3. **Critical:** ED PR > EcD PR for ALL L values tested
4. Gate FAIL: Result is OPPOSITE of hypothesis prediction

## Root Cause Analysis

- Hypothesis predicted ED PR ≤ EcD PR to confirm bounded d* is intrinsic to weight manifolds
- Actual result: ED PR >> EcD PR, indicating bounded d* is CONTRASTIVE-INDUCED, not intrinsic
- The contrastive loss in EcD compresses representations; without it, ED scales freely
- This falsifies the mechanism hypothesis that bounded d* is intrinsic

## Lessons Learned

1. Contrastive loss is the primary driver of PR saturation, not weight manifold structure
2. ED encoder without contrastive loss does NOT exhibit bounded dimensionality
3. The phenomenon (h-e1) exists but the proposed mechanism (h-m1) is wrong
4. Need to reformulate: bounded d* is a CONSEQUENCE of contrastive learning, not an intrinsic property

## Implications for Main Hypothesis

- h-e1 (EXISTENCE) validated: PR saturation at d* ∈ [5,15] confirmed
- h-m1 (MECHANISM) falsified: bounded d* is NOT intrinsic to weight manifolds
- Must route to Phase 2A reflection to reformulate mechanism hypothesis
- Alternative mechanism: contrastive loss induces low-rank structure in encoder

## Feedback for Phase 2A

### Suggested Modifications
- Reformulate mechanism: "Contrastive loss induces bounded d* through representation alignment"
- Investigate WHY contrastive loss creates this saturation
- Consider alternative mechanisms: information bottleneck, alignment constraint, spectral properties

### What NOT To Do
- Do not assume bounded d* is intrinsic to weight space without contrastive loss
- Do not compare ED vs EcD expecting similar PR behavior

### What Showed Promise
- Experimental setup correctly distinguishes ED vs EcD behavior
- PR measurement methodology is valid
- Clear separation between encoder types confirms measurement sensitivity

---
*Gate Type: MUST_WORK - requires route to Phase 2A reflection*
*Written at: 2026-08-09T16:30:00Z*
