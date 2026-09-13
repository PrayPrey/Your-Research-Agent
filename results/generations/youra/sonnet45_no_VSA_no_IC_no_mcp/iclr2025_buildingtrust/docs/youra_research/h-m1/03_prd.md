# Product Requirements Document (PRD)

**Hypothesis:** h-m1  
**Type:** MECHANISM  
**Gate:** MUST_WORK  
**Date:** 2026-08-24  
**Author:** Anonymous  

---

## Executive Summary

Build threshold-based binary classifier to classify failure types (entity-error vs non-entity-error) using attention entropy values from h-e1. Validates whether h-e1's statistical difference (entity errors show lower entropy) is actionable for automated routing.

**Success Metric:** Classification accuracy ≥70% on held-out test set (13 samples).

**Dependencies:** h-e1 validation outputs (entropy values for 73 samples).

---

## Problem Statement

h-e1 proved entity-substitution errors exhibit significantly lower attention entropy (mean=0.062) vs non-entity errors (mean=0.300), p=7.5e-07. Gate question: Is this difference actionable for classification?

If accuracy < 70%, entropy pattern exists but cannot reliably route failures → entire failure-type routing framework invalidated.

---

## Functional Requirements

### FR1: Data Loading
**Priority:** P0  
**Description:** Load h-e1 entropy outputs (73 samples: 50 entity-errors, 23 non-entity-errors).  
**Input:** `h-e1/code/entropy_results.json` or h-e1 experiment outputs  
**Output:** Arrays `entropies` (73 floats), `labels` (73 binary: 0=entity-error, 1=non-entity-error)  
**Acceptance:**
- Loads 73 samples successfully
- Preserves entity/non-entity class labels
- Entropy values match h-e1 outputs

### FR2: Train/Test Split
**Priority:** P0  
**Description:** Split data 80/20 stratified by error type.  
**Input:** entropies, labels  
**Output:** X_train (60 samples), X_test (13 samples), y_train, y_test  
**Acceptance:**
- Test set = 13 samples (20% of 73, rounded)
- Stratified split preserves class balance
- Random seed=42 for reproducibility

### FR3: Threshold Grid Search
**Priority:** P0  
**Description:** Find optimal entropy threshold via grid search on training set.  
**Input:** X_train, y_train  
**Output:** best_threshold (float in [0, 1])  
**Acceptance:**
- Search 101 thresholds [0.00, 0.01, ..., 1.00]
- Classification rule: entropy < threshold → entity-error (0)
- Returns threshold with highest training accuracy

### FR4: Test Set Evaluation
**Priority:** P0  
**Description:** Evaluate threshold on held-out test set.  
**Input:** X_test, y_test, best_threshold  
**Output:** test_acc (float), classification_report, confusion_matrix  
**Acceptance:**
- Applies threshold to 13 test samples
- Computes accuracy, precision, recall, F1
- Generates 2x2 confusion matrix

### FR5: Gate Check
**Priority:** P0  
**Description:** Verify test accuracy ≥ 0.70.  
**Input:** test_acc  
**Output:** gate_pass (bool)  
**Acceptance:**
- PASS if test_acc ≥ 0.70
- FAIL if test_acc < 0.70
- Report gate outcome clearly

### FR6: Baseline Comparison
**Priority:** P1  
**Description:** Compare against random classifier (50% baseline).  
**Input:** y_test  
**Output:** baseline_acc (float, ~0.5)  
**Acceptance:**
- Random assignment to classes
- Confirms proposed model improvement over 50% floor

### FR7: Visualization Generation
**Priority:** P1  
**Description:** Generate 3 figures: (1) Threshold vs Accuracy curve, (2) Confusion Matrix, (3) Entropy Distribution by Class.  
**Output:** PNG files saved to `h-m1/figures/`  
**Acceptance:**
- threshold_curve.png: 101-point line plot
- confusion_matrix.png: 2x2 heatmap
- entropy_distribution.png: Overlaid histograms with threshold line

---

## Non-Functional Requirements

### NFR1: Reproducibility
All random operations use seed=42. Results must be deterministic.

### NFR2: Minimal Dependencies
Use only: scikit-learn, NumPy, Matplotlib. No deep learning frameworks.

### NFR3: Execution Time
Complete experiment in <1 minute (no model training, threshold search is deterministic).

### NFR4: Code Clarity
Single Python script, <200 lines. Functions: load_data, split_data, find_threshold, evaluate, visualize.

---

## Data Specifications

**Primary Dataset:** h-e1 entropy outputs  
**Format:** JSON or Python pickle  
**Schema:**
```json
{
  "sample_id": "string",
  "error_type": "entity-error | non-entity-error",
  "entropy": float (0.0-1.0)
}
```

**Size:** 73 samples (50 entity-errors, 23 non-entity-errors)  
**Source:** h-e1 validation outputs

---

## Model Specifications

### Baseline Model
**Type:** Random Classifier  
**Implementation:** `np.random.choice([0, 1], size=len(y_test))`  
**Expected Performance:** ~50% accuracy

### Proposed Model
**Type:** Threshold-based Binary Classifier  
**Input:** Single entropy value (scalar)  
**Parameters:** threshold (float, optimized via grid search)  
**Classification Rule:** 
```python
prediction = 0 if entropy < threshold else 1
# 0 = entity-error, 1 = non-entity-error
```

---

## Evaluation Metrics

### Primary Metric (Gate)
**Metric:** Classification Accuracy  
**Target:** ≥ 70%  
**Gate:** MUST_WORK

### Secondary Metrics
- Precision (entity-error class)
- Recall (entity-error class)
- F1 Score (both classes)
- Confusion Matrix

---

## Success Criteria

### Gate Pass
✅ test_accuracy ≥ 0.70 on 13-sample held-out test set

### Gate Fail
❌ test_accuracy < 0.70 → Entropy difference not actionable, framework invalidated

### Baseline Improvement
Proposed model accuracy > 50% (random baseline)

---

## Dependencies

**Prerequisite:** h-e1 (VALIDATED)  
**Required Artifacts:**
- h-e1 entropy computation results (73 samples)
- h-e1 error type labels

**Dependent Hypotheses:** h-m2 (requires classification capability)

---

## Implementation Scope

**In Scope:**
- Load h-e1 outputs
- Threshold classifier
- Train/test split
- Gate evaluation
- Visualizations

**Out of Scope:**
- Re-running attention extraction (use h-e1 outputs)
- Neural network classifiers (threshold-based only)
- Multi-class classification (binary only)
- Cross-validation (single 80/20 split sufficient for 73 samples)

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Small test set (13 samples) | High variance in accuracy estimate | Use stratified split; report confidence intervals |
| h-e1 outputs unavailable | Blocker | Verify h-e1 validation artifacts exist before Phase 4 |
| Threshold overfits train set | False gate pass | Test set evaluation mandatory |

---

## Appendix: Phase 2C Alignment

**Experiment Brief:** `h-m1/02c_experiment_brief.md`  
**Key Elements Covered:**
- ✅ Dataset: h-e1 outputs (73 samples)
- ✅ Baseline: Random classifier (50%)
- ✅ Proposed: Threshold classifier
- ✅ Metrics: Accuracy, precision, recall, F1
- ✅ Gate: ≥70% accuracy
- ✅ Visualizations: 3 figures specified

**Ablation Studies:** Not applicable (single threshold parameter, no ablations)

---

**PRD Version:** 1.0  
**Status:** Ready for Phase 3 Architecture Design
