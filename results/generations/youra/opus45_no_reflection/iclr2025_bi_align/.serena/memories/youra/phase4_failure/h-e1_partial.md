# Phase 4 Failure: H-E1 PARTIAL Gate Result

**Hypothesis:** h-e1 (EXISTENCE - Multi-annotator variance measurement)
**Gate Type:** MUST_WORK
**Result:** PARTIAL
**Date:** 2026-08-20

## Failure Summary

Variance measurement succeeded (100% coverage) but correlation threshold NOT met (all r < 0.2, p > 0.05 for semantic ambiguity, lexical complexity, controversy).

## Root Causes

### 1. Dataset Unavailable
- **Issue:** ETHICS dataset (`hendrycks/ethics`) unavailable on HuggingFace
- **Error:** `RuntimeError: Dataset scripts are no longer supported, but found ethics.py`
- **Impact:** Used synthetic data with simulated variance patterns
- **Real Data Needed:** Actual human multi-annotator judgments required

### 2. BERTScore Model Loading Failed
- **Issue:** Torch version security conflict (CVE-2025-32434)
- **Error:** `ValueError: upgrade torch to at least v2.6`
- **Fallback:** Used text length proxy instead of semantic similarity
- **Impact:** Semantic ambiguity measurement degraded

### 3. Synthetic Data Limitations
- **Issue:** Synthetic annotator votes lack realistic correlation with task properties
- **Impact:** No emergent correlation between variance and text features
- **Evidence:** All correlations near zero (r: 0.024, 0.034, -0.043)

## What Worked

1. **Variance Computation:** Entropy-based variance computable for 100% of examples
2. **Code Architecture:** Modular pipeline (7 modules) executed without errors
3. **Validation Checks:** 4/5 checks passed (coverage, properties complete, execution time, memory)
4. **Visualization:** All 5 figures generated successfully

## Recommended Next Steps

### Option A: Fix Dataset Access (Preferred)
1. Download ETHICS raw data directly from paper repository
2. Extract multi-annotator metadata from original tar files
3. Re-run experiment with real variance patterns

### Option B: Alternative Dataset
1. Switch to GoEmotions or SocialChem (public multi-annotator data)
2. Adapt variance measurement to emotion/norm labels
3. Validate correlation on real human judgments

### Option C: Hypothesis Modification (Phase 2A-Dialogue)
1. Relax correlation threshold (r > 0.15 instead of 0.2)
2. Change variance metric (Fleiss' kappa instead of entropy)
3. Add feature: syntactic complexity, sentiment polarity

## Routing Decision

**Route to:** Phase 2A-Dialogue (1 modification attempt allowed)
**Focus:** Dataset access fix OR hypothesis relaxation
**Blocker:** H-M2 (primary prediction) cannot proceed until H-E1 PASS
