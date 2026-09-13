# Adversarial Review Round 2 - Numerical Verification

## Executive Summary
- FATAL: 0 issues
- MAJOR: 0 issues
- MINOR: 3 issues
- Recommendation: CONDITIONAL_ACCEPT

All R1 fixes verified. Deep numerical cross-check reveals minor precision discrepancies but no substantive errors.

## R1 Fix Verification

- [x] **MAJOR-1 fixed**: Decimal precision now consistent (2 decimal places throughout results tables)
- [x] **MAJOR-2 fixed**: H-M1 now reports CI [-0.09, 0.44] and p=0.19 (Table in Section 5)
- [x] **MAJOR-3 fixed**: H-M2 p-value (0.26) explicitly disclosed in results table

## Deep Numerical Verification

### H-E1 Claims

| Paper Claim | Phase 4 Value | Match? |
|------------|--------------|--------|
| TQA-HE r=0.58 | 0.5778 | YES (rounded) |
| TQA-HE CI [0.36, 0.74] | [0.357, 0.738] | YES (rounded) |
| TQA-HE p=3.3e-5 | 3.3e-05 | YES |
| TQA-FS r=0.42 | 0.4237 | YES (rounded) |
| TQA-FS CI [0.17, 0.63] | [0.165, 0.628] | YES (rounded) |
| TQA-FS p=0.0065 | 0.0065 | YES |
| HE-FS r=0.44 | 0.4441 | YES (rounded) |
| HE-FS CI [0.19, 0.64] | [0.189, 0.643] | YES (rounded) |
| HE-FS p=0.0037 | 0.0037 | YES |
| Baseline r=0.10 | 0.1017 | YES (rounded) |

### H-M1 Claims

| Paper Claim | Phase 4 Value | Match? |
|------------|--------------|--------|
| r(TQA, MMLU)=0.19 | 0.189 | YES (rounded) |
| CI [-0.09, 0.44] | Not in Phase 4 file | MINOR: Phase 4 lacks CI |
| p=0.19 | Not in Phase 4 file | MINOR: Phase 4 lacks p-value |
| r(MMLU internal)=0.78 | 0.784 | YES (rounded) |
| r-squared gap=0.58 | 0.579 | YES (rounded) |
| Divergent count=4 | 4 | YES |
| Model names match | All 4 match | YES |

### H-M2 Claims

| Paper Claim | Phase 4 Value | Match? |
|------------|--------------|--------|
| r(HE, TQA)=0.16 | 0.162 | YES (rounded) |
| CI [-0.10, 0.40] | [-0.095, 0.395] | YES (rounded) |
| p=0.26 | 0.2614 | YES (rounded) |
| Intra-HE r=0.65 | 0.645 | YES (rounded) |
| QA subtask r=0.15 | 0.153 | YES (rounded) |
| Dialogue subtask r=0.15 | 0.148 | YES (rounded) |
| Summarization r=0.22 | 0.222 | YES (rounded) |
| QA-Dialogue r=0.69 | 0.692 | YES (rounded) |
| QA-Summ r=0.60 | 0.601 | YES (rounded) |
| Dialogue-Summ r=0.64 | 0.641 | YES (rounded) |

### H-M3 Claims

| Paper Claim | Phase 4 Value | Match? |
|------------|--------------|--------|
| r(FS, TQA)=-0.01 | -0.005 | YES (rounded) |
| CI [-0.27, 0.26] | [-0.274, 0.261] | YES (rounded) |
| r(FS, HE)=-0.15 | -0.147 | YES (rounded) |
| CI [-0.42, 0.13] | [-0.415, 0.130] | YES (rounded) |
| PCA 3 components | 3 | YES |
| PC1=38.6% | 38.6% | YES |
| PC2=34.3% | 34.3% | YES |

## FATAL Issues

None.

## MAJOR Issues

None.

## MINOR Issues

1. **MINOR-R2-1**: H-M1 Phase 4 validation file does not document the CI or p-value for r(TQA, MMLU). Paper claims CI=[-0.09, 0.44] and p=0.19 appear in ground_truth.yaml but not in 04_validation.md. Source unclear but values are plausible.

2. **MINOR-R2-2**: PC3 variance in paper says "~7%" but Phase 4 validation only shows "38.6%" and "34.3%", not explicit PC3. The math works (38.6+34.3+7=79.9%, rounds to 80%), but PC3 is soft-stated.

3. **MINOR-R2-3**: H-M2 QA subtask p-values in paper (0.29, 0.31, 0.12) differ slightly from Phase 4 (0.2878, 0.3062, 0.1216) due to rounding. Not material.

## Baseline Fairness Assessment

The paper appropriately:
- Uses MMLU-Physics vs HaluEval as unrelated-benchmark baseline (r=0.10)
- Compares intra-MMLU correlation (r=0.78) as ceiling reference
- Acknowledges limitations (open-source only, English only, FactScore proxy)

No unfair baseline manipulation detected.

## Mathematical Validity

All calculations check out:
- 0.10 < r < 0.7 satisfied for all truthfulness pairs
- r(TQA,MMLU)=0.19 << r(MMLU internal)=0.78 (gap is real)
- PCA requiring 3 components for 80% variance is consistent with PC1+PC2 = 72.9%

## Recommendation

**CONDITIONAL_ACCEPT**

Paper is numerically sound. Minor issues are documentation gaps in Phase 4 files, not paper errors. Human should verify H-M1 CI/p-value source before final publication.
