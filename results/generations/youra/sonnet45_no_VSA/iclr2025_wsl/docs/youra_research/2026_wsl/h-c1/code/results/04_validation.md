# H-C1 Validation Report

**Date:** 2026-07-11 21:15:36

**Hypothesis:** Statistical features maintain >70% accuracy on edge cases

## 1. Executive Summary

- **Overall Accuracy:** 83.3% (95% CI: [55.2%, 95.3%])
- **Degradation:** 1.7% (baseline: 85.0%)
- **Gate Status:** PASS
- **Rationale:** Overall accuracy 83.3% >= 70% threshold

## 2. Results

### Overall Metrics

- Sample size: 12
- Correct predictions: 10
- Extraction time: 49.76s
- Total runtime: 50.41s

### Per-Family Accuracy

| Family | Accuracy | Correct | Total | Status |
|--------|----------|---------|-------|--------|
| NormFree | 0.0% | 0 | 1 | FAIL |
| SENet | 100.0% | 3 | 3 | PASS |
| RegNet | 100.0% | 5 | 5 | PASS |
| ViT-Extreme | 100.0% | 2 | 2 | PASS |
| Unknown | 0.0% | 0 | 1 | FAIL |

## 3. Failure Mode Analysis

See detailed analysis in `results/failure_analysis.md`

### Key Findings

- **NormFree:** All 1 models misclassified as Hybrid
- **SENet:** No failures
- **RegNet:** No failures
- **ViT-Extreme:** No failures
- **Unknown:** All 1 models misclassified as Transformer

## 4. Conclusion

The edge case robustness validation **PASSED** the SHOULD_WORK gate. Statistical features generalize to edge case architectures with acceptable degradation.

## 5. Recommendations

- NormFree accuracy (0.0%) below threshold - consider targeted features
- Unknown accuracy (0.0%) below threshold - consider targeted features
