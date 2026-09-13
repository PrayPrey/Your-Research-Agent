# Product Requirements Document: H-M3

**Date:** 2026-08-25
**Author:** Anonymous
**Hypothesis ID:** H-M3
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## Executive Summary

This document specifies requirements for validating H-M3: whether Gate 1 micro-pilot overhead measurements (O_10, 10 samples, <1 hour) can predict hypothesis viability with >80% accuracy using the scaling factor k validated in H-M1. The implementation will apply binary classification (viable/non-viable) to a 30-hypothesis corpus and test against a 50% random guessing baseline using binomial statistical testing.

---

## Hypothesis Statement

Under the framework applied to the corpus from H-E1, if we use Gate 1 micro-pilot (10 samples, <1 hour) to predict viability (overhead >threshold vs ≤threshold), then accuracy (TP + TN) / Total will exceed 80%, compared to 50% random guessing null hypothesis, because overhead scaling from H-M1 enables early prediction.

---

## Success Criteria

### Primary (PoC)
- **Accuracy:** >80% (24/30 correct predictions)
- **Statistical significance:** Binomial test p <0.05 vs null hypothesis (50% random guessing)

### Secondary
- **Non-viable filtering:** 60%+ hypotheses predicted non-viable at Gate 1 (validates prediction P2)
- **Confusion matrix:** Report TP/TN/FP/FN counts for error analysis

### Failure Thresholds
- **MUST_WORK gate failure:** Accuracy ≤60% → framework doesn't beat random + margin, core claim unsupported
- **Partial success:** 60% < accuracy ≤80% → explore per-type threshold calibration

---

## Gate Condition

**Type:** MUST_WORK (core framework claim)

**Rationale:** H-M3 validates primary prediction P1 from Phase 2A. If Gate 1 cannot achieve >80% accuracy, the framework's viability prediction claim is unsupported. Accuracy ≤60% means the framework performs only marginally better than random guessing, invalidating deployment value.

**Failure response:** If accuracy ≤60%, report MUST_WORK gate failure and recommend framework redesign or abandonment.

---

## Technical Requirements

### Dataset Requirements

**Dataset:** Retrospective ML Projects Corpus (custom)

**Source:** Papers with Code leaderboards + conference papers (NeurIPS, ICML, ICLR 2020-2024) with published micro-pilot overhead data

**Structure:**
- Total samples: 30 hypotheses
- Stratification: 10 low-overhead (<20%), 10 mid (20-80%), 10 high (>80%)
- Required columns:
  - `O_10`: 10-sample overhead measurement (proportion, 0.0-1.0)
  - `O_full`: full-dataset overhead measurement (ground truth, 0.0-1.0)
  - `hypothesis_type`: Hypothesis category (e.g., attention/gradient/etc) for per-type calibration
  - `threshold`: Viability threshold (default 10% for deployment context)
- Labels: Binary (viable/non-viable based on O_full >threshold)

**Loading:**
```python
import pandas as pd
corpus_df = pd.read_csv("../h-m1/data/retrospective_corpus_30.csv")
# Expected columns: hypothesis_id, O_10, O_full, hypothesis_type, threshold
```

**Preprocessing:**
- No normalization (overhead values already in proportion format)
- No augmentation (retrospective data, fixed corpus)
- Validation: Check O_10 and O_full columns exist and are numeric

**Continuation note:** Reuse corpus from h-m1 and h-m2 for controlled comparison. Only the prediction task changes (correlation → error reduction → viability classification).

---

### Model Requirements

#### Baseline Model

**Architecture:** Random Guessing (Null Hypothesis)

**Implementation:**
```python
import numpy as np

def random_baseline(n_samples, seed=42):
    """Random guessing: 50% probability for each class."""
    np.random.seed(seed)
    return np.random.choice(["viable", "non-viable"], size=n_samples)
```

**Expected performance:** ~50% accuracy (15/30 correct by chance)

#### Proposed Model

**Architecture:** Gate1ViabilityClassifier (Rule-Based)

**Core mechanism:**
```python
class Gate1ViabilityClassifier:
    """
    Predict hypothesis viability using Gate 1 micro-pilot overhead.
    Uses scaling factor k from h-m1 corpus analysis.
    """
    def __init__(self, scaling_factor_k, threshold=0.10):
        self.k = scaling_factor_k
        self.threshold = threshold
    
    def predict(self, O_10):
        """
        Predict viability for single hypothesis.
        
        Args:
            O_10: 10-sample overhead (proportion, 0.0-1.0)
        
        Returns:
            prediction: "non-viable" if O_pred >threshold, else "viable"
            O_pred: Predicted full-scale overhead
        """
        O_pred = O_10 * self.k
        prediction = "non-viable" if O_pred > self.threshold else "viable"
        return prediction, O_pred
    
    def predict_batch(self, O_10_array):
        """Predict viability for batch of hypotheses."""
        predictions = []
        O_preds = []
        for O_10 in O_10_array:
            pred, O_pred = self.predict(O_10)
            predictions.append(pred)
            O_preds.append(O_pred)
        return predictions, O_preds
```

**Training protocol:** None (rule-based classifier)
- Load scaling factor k from h-m1 validation results (r ≥0.7 validated prerequisite)
- k = slope from `scipy.stats.linregress(O_10_values, O_full_values)`
- No optimizer, learning rate, epochs, or loss function needed

---

### Evaluation Requirements

**Primary Metrics:**

1. **Classification Accuracy**
   - Definition: (TP + TN) / Total
   - TP: Correctly predicted non-viable (O_pred >threshold AND O_full >threshold)
   - TN: Correctly predicted viable (O_pred ≤threshold AND O_full ≤threshold)
   - FP: Incorrectly predicted non-viable (O_pred >threshold BUT O_full ≤threshold)
   - FN: Incorrectly predicted viable (O_pred ≤threshold BUT O_full >threshold)

2. **Confusion Matrix:** Report TP, TN, FP, FN counts

3. **Binomial Test p-value**
   - Null hypothesis: Accuracy = 50% (random guessing)
   - Alternative: Accuracy >80%
   - Test: `scipy.stats.binom_test(n_correct, n_total=30, p=0.5, alternative='greater')`

**Implementation:**
```python
from sklearn.metrics import accuracy_score, confusion_matrix
from scipy.stats import binom_test

# Compute accuracy
accuracy = accuracy_score(y_true, y_pred)

# Confusion matrix
cm = confusion_matrix(y_true, y_pred, labels=["viable", "non-viable"])
TN, FP, FN, TP = cm.ravel()

# Binomial test
n_correct = int(accuracy * len(y_true))
p_value = binom_test(n_correct, len(y_true), p=0.5, alternative='greater')
```

**Expected baseline performance:**
- Random guessing: 50% accuracy (15/30 correct by chance)
- Expert intuition: 60-70% accuracy (estimated from h-e1 anecdote)
- Framework target: >80% accuracy

---

### Visualization Requirements

#### Mandatory Figure
1. **Gate Metrics Comparison:** Accuracy bar chart showing:
   - Random baseline (50%)
   - Expert intuition (65%, optional reference)
   - Gate 1 actual (measured)
   - Target threshold (80%, red horizontal line)

#### Additional Figures (LLM Autonomous)
2. **Confusion Matrix Heatmap:** 2x2 matrix showing TP/TN/FP/FN counts
3. **Prediction Distribution:** Histogram of predicted vs actual viability by overhead level (low/mid/high stratification)
4. **Error Analysis:** Scatter plot O_10 vs O_full with correct/incorrect predictions color-coded
5. **Per-Type Performance:** Accuracy breakdown by hypothesis type (attention/gradient/etc) if stratification available

**Output location:** `h-m3/figures/`

**Implementation note:** All figures must be generated programmatically in experiment code. Save as PNG with 300 DPI for paper inclusion.

---

## Implementation Constraints

### Hard Constraints
1. **Reuse scaling factor k from h-m1:** No retraining or recalibration (use validated k with r ≥0.7)
2. **Deterministic classifier:** No ML training, no random seeds except baseline
3. **Full corpus validation:** All 30 hypotheses must be evaluated (no train/test splits)
4. **Statistical rigor:** Binomial test p <0.05 required for primary success criterion

### Soft Constraints
1. **Runtime:** <5 minutes total (classification + evaluation + visualization)
2. **Dependencies:** Minimal (numpy, pandas, scipy, sklearn, matplotlib)
3. **Reproducibility:** Fixed threshold (10%), validated k from h-m1, deterministic classification

---

## Dependencies

### Prerequisites
- **H-M2 validated:** Mean error reduction 40.91%, paired t-test p=0.0003 (provides Gate 1/2 baseline context)
- **H-M1 validated:** Scaling factor k with r ≥0.7 correlation (core component for h-m3)

### Data Dependencies
- **Corpus:** h-m1 Retrospective ML Projects Corpus with O_10 and O_full measurements
- **Scaling factor k:** Load from h-m1 validation results (e.g., `h-m1/results/scaling_factor.json`)

### External Dependencies
- Python 3.8+
- numpy, pandas, scipy, scikit-learn, matplotlib

---

## PoC Success Check

**Pass conditions:**
1. Code runs without error
2. `accuracy_gate1 > accuracy_baseline` (Gate 1 beats random guessing)
3. Accuracy >80% AND binomial test p <0.05 (primary criterion)

**Failure escalation:**
- Accuracy ≤60%: Report MUST_WORK gate failure
- 60% < accuracy ≤80%: Report partial success, recommend threshold calibration investigation

---

## Phase 4 Implementation Checklist

For the Phase 4 Coder agent:

1. [ ] Load corpus from `../h-m1/data/retrospective_corpus_30.csv`
2. [ ] Load scaling factor k from h-m1 validation results
3. [ ] Implement `Gate1ViabilityClassifier` with predict and predict_batch methods
4. [ ] Implement random baseline with fixed seed (42)
5. [ ] Run classification on all 30 hypotheses
6. [ ] Compute accuracy, confusion matrix (TP/TN/FP/FN)
7. [ ] Run binomial test (n_correct, n_total=30, p=0.5, alternative='greater')
8. [ ] Generate 4 required figures (accuracy bar chart, confusion matrix, prediction distribution, error analysis)
9. [ ] Save all figures to `h-m3/figures/`
10. [ ] Generate `04_validation.md` report with results, success/failure verdict, next steps

---

## Appendix: Reference Context

### H-M2 Results (Prerequisite)
- Status: VALIDATED
- Mean error reduction: 40.91%
- Paired t-test: t=4.453, p=0.0003, dof=19
- Gate 1 mean error: 0.6966, Gate 2 mean error: 0.1111

### H-M1 Results (Prerequisite)
- Status: VALIDATED
- Scaling factor k: Validated with r ≥0.7 correlation between O_10 and O_full
- Per-hypothesis-type k calibration: CV <30%

### Traceability
- Dataset specification: Phase 2B Section 2.2, H-M1 corpus reuse
- Baseline model: Phase 2B null hypothesis (random guessing 50%)
- Proposed model: H-M1 scaling factor k (validated prerequisite)
- Success criteria: Phase 2B Section 2.2 (>80% accuracy, p <0.05)
- Threshold value: Phase 2B deployment context (10% overhead)

---

*Next Phase: Phase 4 - Coding (validate hypothesis with implementation)*
