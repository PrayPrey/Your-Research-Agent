# Phase 4 Failure Record: h-e1 (MTLD-SE Correlation)

**Date:** 2026-03-28T12:45:00Z
**Hypothesis:** h-e1
**Run:** 3 (after pd3_se_correlation_run1 and whitened_dispersion attempts)
**Final Status:** FAIL
**Failure Type:** MUST_WORK_FAIL
**Gate Type:** MUST_WORK

## Hypothesis Statement

> Under the condition of LLM response generation with temperature sampling (N=20, T=1.0), if we compute MTLD across responses, then MTLD will correlate with SE (Spearman rho >= 0.25, p < 0.05) because epistemic uncertainty drives both semantic clustering and lexical diversification.

## Performance Gap

| Metric | Expected | Observed | Status |
|--------|----------|----------|--------|
| Spearman rho | >= 0.25 (positive) | -0.2528 (negative) | **OPPOSITE DIRECTION** |
| p-value | < 0.05 | 2.29e-13 | PASS (but wrong direction) |
| Category Coverage | >= 75% | 15.8% | FAIL |

## Key Finding

**CRITICAL: The experiment found a significant NEGATIVE correlation (rho = -0.25) between MTLD and Semantic Entropy, which is the OPPOSITE of the hypothesized positive correlation.**

This is not a partial failure or implementation issue - the fundamental hypothesis assumption was incorrect.

## Root Cause Analysis

1. **Wrong Assumption:** The hypothesis assumed that epistemic uncertainty drives both semantic clustering AND lexical diversification in the same direction. This is incorrect.

2. **Actual Relationship:** 
   - High MTLD (diverse vocabulary) → Responses are semantically similar but expressed differently → LOWER semantic entropy
   - Low MTLD (repetitive vocabulary) → Responses are semantically distinct using similar domain vocabulary → HIGHER semantic entropy

3. **Mechanistic Interpretation:**
   - Lexical diversity measures surface-level variation
   - Semantic entropy measures deep semantic variation
   - These are inversely related, not positively correlated

## Lessons Learned

1. Lexical diversity and semantic entropy measure different (inversely related) aspects of response variation
2. Surface-level lexical metrics may not complement deep semantic uncertainty measures
3. MTLD is NOT a suitable complementary signal to Semantic Entropy for uncertainty quantification
4. Future hypotheses should consider metrics that measure orthogonal rather than opposing signals

## Routing Decision

**Route to Phase 0** for new research direction.

The negative correlation finding suggests the entire research direction (lexical diversity as complementary UQ signal) may need fundamental reconsideration.

## Recommendations for Phase 0

1. Consider syntactic structure metrics instead of lexical diversity
2. Explore response-level coherence measures
3. Investigate computational efficiency improvements to SE rather than complementary metrics
4. Consider ensemble-based approaches that don't rely on lexical features

---
*Failure recorded at: 2026-03-28T12:45:00Z*
*For cross-phase reference*
