# Adversarial Review Round 2

**Date:** 2026-08-29
**Paper:** 06_paper_r1.md (post-R1 revision)
**Focus:** Numerical Verification

---

## Executive Summary

| Severity | Count |
|----------|-------|
| FATAL | 0 |
| MAJOR | 0 |
| MINOR | 0 |

**Recommendation:** CONVERGED — No numerical discrepancies found.

---

## Ground Truth Verification Table

| Claim | Paper | Ground Truth | Phase 4 Validation | Match |
|-------|-------|--------------|-------------------|-------|
| Spurious alignment (epoch 5) | 0.000 | 0.0000 | 0.0000 | ✓ |
| Core alignment (epoch 5) | 0.000 | 0.0000 | 0.0000 | ✓ |
| Spurious alignment (epoch 10) | 0.052 | 0.0520 | 0.0520 | ✓ |
| Core alignment (epoch 10) | 0.056 | 0.0557 | 0.0557 | ✓ |
| Spurious alignment (epoch 45) | 0.018 | 0.0179 | 0.0179 | ✓ |
| Core alignment (epoch 45) | 0.028 | 0.0283 | 0.0283 | ✓ |
| Validation accuracy | 91.8% | 0.9183 | 0.9183 | ✓ |
| Training samples | 4,795 | 4795 | 4795 | ✓ |
| Model parameters | 25.6M | 25600000 | 25600000 | ✓ |
| SVD rank requested | 50 | 50 | 50 | ✓ |
| SVD rank actual | 10 | 10 | 10 | ✓ |
| Spurious correlation | 95% | 0.95 | 0.95 | ✓ |
| Batch size | 128 | 128 | 128 | ✓ |

**Result:** 13/13 claims verified. NO discrepancies.

---

## Mathematical Validity Analysis

### Check 1: Subspace Rank Calculation

**Paper claim:** "10-dimensional subspace in a 25-million-parameter space captures approximately 10/25M = 4×10^{-7} of variance"

**Verification:**
- 10 / 25,000,000 = 0.0000004 = 4×10^{-7}
- **Result:** VALID ✓

### Check 2: Batch Count Calculation

**Paper claim:** "~38 batches per epoch (4,795 samples / 128 batch size)"

**Verification:**
- 4795 / 128 = 37.46 → rounds to ~38
- **Result:** VALID ✓

### Check 3: Multi-batch Sample Count

**Paper claim:** "multi-batch accumulation would yield ~380 gradient samples"

**Verification:**
- 38 batches × 10 epochs = 380
- **Result:** VALID ✓

### Check 4: Success Criteria

**Paper claim:** Spurious alignment > 0.70, Core alignment < 0.30

**Verification:**
- These thresholds are stated as targets, not measured values
- Actual values (0.052, 0.056) correctly reported as failing targets
- **Result:** VALID ✓ (honest reporting of failure)

---

## Baseline Fairness Assessment

**Status:** N/A

Paper explicitly acknowledges "No baseline comparison performed" in Section 6.2 Limitations. This is honest reporting — there are no unfair baseline comparisons to evaluate.

---

## Methodology Consistency Check

| Description | Paper | Actual | Match |
|-------------|-------|--------|-------|
| Gradient accumulation | 1 per epoch | 1 per epoch | ✓ |
| Accumulation epochs | 1-10 | 1-10 | ✓ |
| SVD computation | On accumulated matrix | On accumulated matrix | ✓ |
| Alignment metric | Projection energy | Projection energy | ✓ |

**Result:** Methodology description matches implementation.

---

## Serena MCP Verification Log

Note: In this session, direct file reads used instead of Serena MCP due to known file locations.

| File | Content Verified |
|------|-----------------|
| h-e1/04_validation.md | All alignment values, gate results |
| paper/065_ground_truth.yaml | All quantitative claims |
| paper/06_narrative_blueprint.yaml | Narrative structure |

---

## Issues Found

**FATAL:** 0
**MAJOR:** 0  
**MINOR:** 0

---

## Conclusion

Round 2 numerical verification complete. All claims in the paper match ground truth and Phase 4 validation results. Mathematical calculations are correct. No baseline fairness issues (no baselines compared). Methodology description is consistent with implementation.

**Recommendation:** Paper is ready for finalization.
