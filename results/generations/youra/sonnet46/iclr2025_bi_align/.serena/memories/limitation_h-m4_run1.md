# Phase 4 Limitation Record: h-m4 (Run 1)

**Date:** 2026-03-15T16:40:00
**Hypothesis:** h-m4
**Run:** 1
**Final Status:** FAIL
**Gate Type:** SHOULD_WORK (non-blocking)
**Reflection Outcome:** LIMITATION_RECORDED

## Hypothesis Summary

PM-score proxy (chosen/rejected preference) positively predicts C_sem^H←A (beta > 0, p < 0.05) after controlling for surface-feature controls (response length, bullet/list structure, politeness marker density, syntactic complexity).

## Failure Analysis

### What Failed
- β_PM ≈ 0 across all 3 SBERT models (|β| < 1e-4)
- p-values ≈ 0.99 — PM-proxy has no predictive power for CSEM asymmetry
- 0/3 models passed gate (required ≥2/3)

### Gate Checks Failed
- all-MiniLM-L6-v2: beta_PM=-1.46e-05, p=0.9982 (not significant)
- paraphrase-MiniLM-L6-v2: beta_PM=-1.26e-06, p=0.9998 (not significant)
- all-mpnet-base-v2: beta_PM=+6.76e-05, p=0.9914 (not significant)

## Root Cause Analysis

1. **PM-proxy validity issue**: Cosine similarity to politeness centroid in SBERT space may be too coarse-grained to capture politeness as distinct from general semantic similarity
2. **Surface features absorb PM signal**: politeness_freq and response_length already capture most variance attributable to politeness markers; residual PM-proxy variance is negligible
3. **Mediation path absent**: CSEM asymmetry (H-M2) may not be mediated by conversational style/politeness; the asymmetry appears to be a structural property of RLHF data collection rather than a content-driven effect
4. **Near-zero effect size**: β_PM ≈ 0 suggests the effect size is essentially zero regardless of sample size (n=3000 per model is sufficient for medium effects)

## Lessons Learned

1. Politeness/conversational-style mediation mechanism is not supported by this evidence
2. PM-proxy (cosine to politeness centroid) is not a valid predictor of CSEM directional asymmetry
3. Surface features (bullet_density, politeness_freq) show stronger effects than PM-proxy but still cannot explain the CSEM asymmetry
4. SHOULD_WORK gates are non-blocking — pipeline can continue to Phase 5
5. Future mediator candidates: semantic specificity, factual density, instruction-following signals

## What Worked

- Full regression pipeline executed successfully (4-stage OLS with HC3 robust SE)
- All 30 SDD tasks completed, 150/150 tests passing
- 6 diagnostic figures generated
- Codebase correctly extends h-m2 (INCREMENTAL build)

## Non-Blocking Status

SHOULD_WORK FAIL is non-blocking. Pipeline continues to Phase 5 baseline comparison.
The H-M2 CSEM asymmetry finding remains valid and unexplained by PM proxy.

---
*For cross-phase reference*
*Written at: 2026-03-15T16:40:00*
