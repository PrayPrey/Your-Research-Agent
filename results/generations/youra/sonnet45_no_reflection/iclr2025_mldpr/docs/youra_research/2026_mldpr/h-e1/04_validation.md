# Phase 4 Validation Report: h-e1 (Real Dataset Run)

**Hypothesis ID:** h-e1  
**Hypothesis Type:** EXISTENCE  
**Gate Type:** MUST_WORK  
**Experiment Date:** 2026-05-12  
**Status:** ✅ MOCK DATA FIXED - Re-run Complete

---

## Mock Data Fix Summary

**Original Issue:** External verification detected mock/synthetic data in experiment code  
**Resolution:** ✅ **COMPLETE** - All mock data removed, experiment re-run with 9 real datasets  
**Verification:** 100% real data confirmed via execution log analysis

---

## Executive Summary

**Gate Result:** ❌ **FAILED** (Same as initial run - hypothesis fundamentally invalid)

The SVAD drift detection classifier was re-run with **9 real dataset pairs** after removing all mock/dummy data. The system still fails the MUST_WORK gate:

- **Precision (MAJOR):** 16.7% (Target: ≥70%) - Gap: -53.3pp
- **Recall (MAJOR):** 100% (Target: ≥85%) - Gap: +15pp  
- **Overall Accuracy:** 44.4% (Target: ≥85%) - Gap: -40.6pp

**Conclusion:** Fixed thresholds (7%/2%/0.5%) do not generalize. Hypothesis remains **INVALID**.

---

## Dataset Coverage - 100% Real Data

### Successfully Loaded (9/15)

**Vision (1/4):**
- ✅ MNIST → USPS/EMNIST (real cross-dataset shift)

**NLP (8/11):**
- ✅ GLUE MRPC, RTE, QNLI, SST2 (train→validation)
- ✅ SNLI (train→test)
- ✅ MultiNLI (matched→mismatched)
- ✅ CoLA (in-domain→out-of-domain)
- ✅ WNLI (train→validation)

### Unavailable (6/15)
- ❌ ImageNet/CIFAR-10.1 (require manual download)
- ❌ Fashion-MNIST, QQP, SQuAD, MS-MARCO (loading errors)

---

## Results

### Metrics

| Metric | Value | Target | Gap | Status |
|--------|-------|--------|-----|--------|
| Accuracy | 44.4% | 85% | -40.6pp | ❌ |
| Precision (MAJOR) | 16.7% | 70% | -53.3pp | ❌ |
| Recall (MAJOR) | 100% | 85% | +15pp | ✅ |
| F1 (MAJOR) | 28.6% | 75% | -46.4pp | ❌ |

### Confusion Matrix
```
            Predicted
         MAJOR MINOR PATCH
MAJOR      1     0     0   (1 total)
MINOR      0     3     0   (3 total)  
PATCH      5     0     0   (5 total)
```

**Key Issue:** 100% PATCH error rate (all 5 misclassified as MAJOR)

---

## Root Causes

**RC1: Fixed Thresholds Don't Generalize** (CRITICAL)
- 5/5 PATCH datasets misclassified as MAJOR
- Thresholds calibrated for ImageNet don't transfer to small NLP datasets

**RC2: Dataset Substitutions** (HIGH)  
- MNIST→USPS is cross-dataset shift, not version drift
- Creates artificially high drift scores (0.597 vs expected <0.005)

**RC3: Missing Vision Datasets** (MEDIUM)
- Only 1/4 vision datasets available
- Cannot validate cross-modality generalization

---

## Mock Data Verification

**Status:** ✅ **PASSED**

**Removed:**
- ❌ `_create_dummy_nlp_pair()` function deleted
- ❌ All `torch.randint()` synthetic data generation removed
- ❌ Proxy datasets (CIFAR-10 for ImageNet) removed

**Replaced with:**
- ✅ Real HuggingFace datasets (GLUE, SNLI, MultiNLI, CoLA, WNLI)
- ✅ Real torchvision datasets (MNIST, USPS/EMNIST)
- ✅ Proper error handling (raises exception instead of falling back to dummy data)

**Verification Evidence:**
- Execution log shows real dataset downloads
- No `torch.randint()` calls in log
- All 9 datasets loaded from external sources

---

## Artifacts

- `04_results.json` - Full results with drift scores
- `04_validation.md` - This report
- `experiment.log` - Execution log
- `figures/` - 4 visualization PNGs

**Runtime:** 4.7 minutes  
**Datasets:** 9/15 (100% real)

---

## Conclusion

**Mock Data Issue:** ✅ RESOLVED  
**Gate Status:** ❌ FAILED (hypothesis invalid)

The experiment now uses 100% real datasets. However, the MUST_WORK gate still fails due to fundamental issues with fixed thresholds. The hypothesis requires revision.

**Next Steps:** Route to Phase 0 for hypothesis redesign with adaptive thresholds.

---

*Report Updated: 2026-05-12*  
*Mock Data Status: RESOLVED*  
*Gate Result: FAILED*
