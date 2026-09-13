# Phase 4 Failure: H-E1 Taxonomy Validation

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Result:** FAIL  
**Date:** 2026-08-19

## Failure Summary

Four-category preprocessing documentation ambiguity taxonomy (Underspecified, Contradictory, Missing, Correct) does NOT achieve substantial inter-rater agreement.

**Primary Metric:** Cohen's kappa = 0.065 (95% CI: [-0.053, 0.194])  
**Threshold:** κ >0.7 (substantial agreement)  
**Outcome:** Far below threshold (slight agreement, essentially random)

## Root Cause

Taxonomy categories are NOT operationally distinguishable by independent human coders:
- **Category overlap:** Underspecified vs Missing boundary unclear
- **Reconstruction ambiguity:** Multiple preprocessing variants may all be "correct"
- **Training insufficient:** 5 practice datasets don't cover edge cases
- **Confusion matrix:** Uniform scatter (no diagonal dominance)

## Evidence

**Per-category agreement rates:**
- Underspecified: 34.6%
- Contradictory: 29.2%
- Missing: 32.0%
- Correct: 20.0%

All categories <35% agreement. No category reliably distinguishable.

**Repository-level kappa:**
- HuggingFace: -0.012
- OpenML: 0.151
- UCI: 0.063

Failure is repository-invariant (not data-specific).

## Implications

1. **Blocks H-M3:** Pattern validation hypothesis depends on reliable taxonomy measurement
2. **Assumption A2 violated:** Four-category taxonomy does NOT capture meaningful distinctions
3. **Measurement instrument invalid:** Cannot use taxonomy for repository comparison studies

## Lessons Learned

### What Worked
- Dual-coder protocol execution (stratified sampling, blind assignment, independent work)
- Statistical rigor (bootstrap CI, confusion matrix)
- Code pipeline (end-to-end automation)

### What Failed
- Four-category taxonomy too fine-grained
- Reconstruction-based categorization too subjective
- Coder training insufficient for edge cases

## Recommended Fix

**Binary taxonomy:** Collapse categories into Ambiguous/Correct
- Simpler boundary (can/cannot reconstruct preprocessing)
- Higher expected kappa (fewer confusion points)
- Retry with binary taxonomy in Phase 0

**Alternative:** Replace human categorization with automated NLP similarity metric (doc-code embedding distance)

## Related Hypotheses

- **H-M1:** Mechanism hypothesis (dual-coder → kappa >0.7) — READY for Phase 2C
- **H-M2:** Should-work chain step — awaiting H-M1 completion
- **H-M3:** BLOCKED by H-E1 failure (requires valid taxonomy)

## Routing Decision

**Route to:** Phase 0 (hypothesis refinement)  
**Reason:** MUST_WORK gate failure per workflow failure routing protocol  
**Stop pipeline:** No (only H-M3 blocked; H-M1/H-M2 can proceed independently)
