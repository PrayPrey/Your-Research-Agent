# Reflection Report: h-e1

## Summary

| Field | Value |
|-------|-------|
| **Hypothesis ID** | h-e1 |
| **Type** | EXISTENCE |
| **Gate Type** | MUST_WORK |
| **Gate Result** | FAIL |
| **Reflection Outcome** | ROUTED_TO_PHASE_0 |
| **Completed At** | 2026-03-29T00:00:00Z |

## Hypothesis Statement

> A probe trained on hidden states with semantic similarity auxiliary signal produces meaningful SE predictions (rho >= 0.3) on the same model it was trained on.

## Gate Evaluation

| Criterion | Threshold | Actual | Status |
|-----------|-----------|--------|--------|
| SEDP Spearman rho | >= 0.3 | 0.0843 | **FAIL** |

The gate result was **FAIL** (not PARTIAL). The actual performance (rho=0.0843) is **72% below** the required threshold (0.3), indicating a fundamental failure rather than a marginal miss.

## Experiment Results

### Performance Metrics

| Metric | SEP (Baseline) | SEDP (Proposed) | Delta |
|--------|----------------|-----------------|-------|
| Spearman rho | 0.0835 | 0.0843 | +0.0009 |
| AUROC | 0.5214 | 0.5219 | +0.0004 |
| p-value | 0.288 | 0.283 | - |

### Key Findings

1. **Near-random performance:** Both SEP and SEDP achieve AUROC ~0.52, barely above random chance (0.5)
2. **Negligible improvement:** SEDP improves over SEP by only +0.0009 rho - statistically insignificant
3. **Hidden states don't encode SE:** Layer 25 hidden states do not contain extractable semantic entropy signal
4. **Similarity features ineffective:** The 4-dimensional similarity features provide minimal additional information

## Root Cause Analysis

1. **Layer selection assumption invalid:** Layer 25 was chosen based on prior work assumptions, but may not contain SE-relevant information for this model/task
2. **Probe architecture too simple:** Logistic regression may be insufficient to capture complex SE patterns
3. **Token position suboptimal:** TBG (To-Be-Generated) token position may not be the optimal extraction point
4. **Feature engineering insufficient:** 4-dimensional similarity features are too low-dimensional to capture semantic structure

## Reflection Decision

### Decision Matrix Application

| Question | Assessment |
|----------|------------|
| Meaningful findings? | NO - Performance is near-random |
| Actionable insight? | NO - No clear path to improvement |
| Partial success? | NO - Complete failure (72% below threshold) |

### Decision: ROUTED_TO_PHASE_0

Per the step-06b decision logic:
- Gate result = **FAIL** (not PARTIAL)
- FAIL → Route to Phase 0 (fundamental flaw)

This is not a marginal miss that could be addressed with parameter tuning or scope reduction. The fundamental assumption that hidden states encode extractable SE signal has not been validated.

## Cascade Impact

The following dependent hypotheses are marked CASCADE_FAILED:

| Hypothesis | Type | Original Status | New Status |
|------------|------|-----------------|------------|
| h-m1 | MECHANISM | NOT_STARTED | CASCADE_FAILED |
| h-m2 | MECHANISM | NOT_STARTED | CASCADE_FAILED |
| h-m3 | MECHANISM | NOT_STARTED | CASCADE_FAILED |

## Lessons Learned

1. **Validate existence before mechanism:** The probe approach requires that hidden states actually encode SE. Without validating this existence claim first with strong evidence, the mechanism hypotheses cannot succeed.

2. **Layer ablation is essential:** Future work should systematically evaluate multiple layers before committing to a single layer.

3. **Consider richer representations:** 4-dimensional similarity features are insufficient. Consider:
   - Full attention pattern analysis
   - Multiple layer aggregation
   - Residual stream probing
   - Token sequence features (not just TBG)

4. **Architecture matters:** Logistic regression may be too simple. Consider MLP probes, attention-based probes, or ensemble methods.

## Recommendations for Phase 0 Restart

1. **Reconsider fundamental approach:** Question whether single-pass hidden states can predict SE at all
2. **Literature review:** Search for evidence that SE signal exists in hidden states
3. **Alternative signals:** Consider attention weights, layer-wise activations, or generation dynamics
4. **Different uncertainty measures:** Explore alternatives to semantic entropy that may be more tractable

## Serena Memory

- **Memory File:** `failures/phase4_h-e1_sedp_must_work_fail`
- **Purpose:** Cross-phase learning for future hypothesis formulation

## Next Action

**Route to Phase 0** - The pipeline will terminate this hypothesis loop and restart with a new research direction.
