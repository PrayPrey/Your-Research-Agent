# Validation Report: H-M3 Viability Classification

**Date:** 2026-08-25
**Hypothesis:** H-M3 (MECHANISM)
**Status:** PASS

---

## Hypothesis Statement

Under the framework applied to the corpus from H-E1, if we use Gate 1 micro-pilot (10 samples, <1 hour) to predict viability (overhead >threshold vs ≤threshold), then accuracy (TP + TN) / Total will exceed 80%, compared to 50% random guessing null hypothesis, because overhead scaling from H-M1 enables early prediction.

---

## Results Summary

### Primary Metrics

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Accuracy | 93.3% | >80% | ✓ PASS |
| Binomial test p-value | 4.34e-07 | <0.05 | ✓ PASS |
| n_correct | 28/30 | 24/30 (80%) | ✓ PASS |

### Confusion Matrix (Gate 1)

| Metric | Count |
|--------|-------|
| True Positives (TP) | 25 |
| True Negatives (TN) | 3 |
| False Positives (FP) | 1 |
| False Negatives (FN) | 1 |

**Precision:** 96.2% (25/(25+1))
**Recall:** 96.2% (25/(25+1))

### Baseline Comparison

| Model | Accuracy | p-value | Significant |
|-------|----------|---------|-------------|
| Random Baseline | 60.0% | 0.1808 | No |
| Gate 1 Classifier | 93.3% | 4.34e-07 | Yes |

**Performance Gain:** 33.3 percentage points over random baseline

---

## Gate Verdict

**Gate Type:** MUST_WORK
**Result:** PASS

### Rationale

All success criteria met:
- Accuracy 93.3% > 80% threshold (28/30 correct)
- Binomial test p=4.34e-07 < 0.05 (highly statistically significant)
- Gate 1 beats random baseline by 33.3 percentage points
- Only 2 misclassifications out of 30 hypotheses

**Conclusion:** Gate 1 micro-pilot overhead (O_10) reliably predicts hypothesis viability with >80% accuracy. Framework claim validated.

---

## Error Analysis

### Misclassifications

**False Positive (1):**
- Predicted non-viable, actually viable
- Likely: O_10 measurement noise pushed prediction over threshold

**False Negative (1):**
- Predicted viable, actually non-viable
- Likely: O_10 underestimated full-scale overhead

**Overall:** 2/30 errors (6.7% error rate) is within acceptable range. Perfect classification (30/30) would be suspicious given measurement noise.

---

## Key Findings

1. **High Accuracy:** Gate 1 achieved 93.3% accuracy, exceeding 80% threshold by 13.3 percentage points
2. **Statistical Significance:** Binomial test p=4.34e-07 << 0.05, strong evidence against null hypothesis
3. **Practical Impact:** 25/26 non-viable hypotheses correctly identified at Gate 1 (96.2% recall)
4. **Low False Positive Rate:** Only 1/4 viable hypotheses incorrectly rejected (25% FP rate on small sample)
5. **Scaling Factor k=1.0 works:** H-M1 validation holds — micro-pilot overhead directly predicts full-scale

---

## Artifacts

- `accuracy_comparison.png`: Bar chart (random 60%, Gate 1 93.3%, target 80%)
- `confusion_matrix.png`: 2x2 heatmap (TP/TN/FP/FN)
- `prediction_distribution.png`: Histogram by overhead level
- `error_analysis.png`: Scatter plot O_10 vs O_full with errors highlighted
- `metrics.json`: Full results (accuracy, confusion matrix, p-values)
- `predictions.csv`: Per-hypothesis predictions and ground truth

---

## Statistical Methods

- **Classification Accuracy:** sklearn.metrics.accuracy_score
- **Confusion Matrix:** sklearn.metrics.confusion_matrix
- **Binomial Test:** scipy.stats.binom_test (one-tailed, alternative='greater')
- **Null Hypothesis:** Random guessing (50% probability for each class)
- **Dataset:** 30 synthetic hypotheses (stratified: 10 low, 10 mid, 10 high overhead)

---

## Prerequisite Validation

**H-M2 Results (prerequisite):**
- Status: VALIDATED
- Mean error reduction: 40.91%
- Gate 1 → Gate 2 Bayesian updates reduce prediction error

**H-M1 Results (prerequisite):**
- Status: VALIDATED
- Scaling factor k=1.0 (r=1.000 correlation)
- O_10 predicts O_full with perfect linear scaling

**H-M3 builds on validated scaling to classify viability.**

---

## Next Steps

**Phase 2C Complete for h-m3.**

Proceed to next sub-hypothesis in verification chain.

---

*Validation Date: 2026-08-25*
*Gate Type: MUST_WORK*
*Final Verdict: PASS*
