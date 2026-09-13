# Product Requirements Document: H-M2 Meta-Classifier Training Sufficiency

**Date:** 2026-07-13
**Author:** Anonymous
**Hypothesis:** H-M2 - Aggregated benchmark results from literature provide sufficient training examples (50-60 datasets) to learn feature-method relationships.
**Type:** MECHANISM
**Gate:** SHOULD_WORK (CV Accuracy > 35%, Generalization Gap < 25%)

---

## Executive Summary

### Problem Statement
Validate whether 50-60 training datasets provide sufficient examples for a Random Forest meta-classifier to learn generalizable feature-method relationships. This tests the data sufficiency assumption underlying the meta-method selection approach.

### Solution Overview
Train Random Forest classifier (100 trees, max_depth=10) on 63 benchmarks using leave-5-out cross-validation. Measure generalization performance (CV accuracy vs baseline) and overfitting (train-test gap). Success requires CV accuracy >35% and generalization gap <25%.

### Success Criteria
- **Primary Gate (SHOULD_WORK):** CV Accuracy > 35% AND Generalization Gap < 20%
- **Partial Success:** CV Accuracy 30-35% OR Gap 20-25%
- **Failure:** CV Accuracy ≤ 30% (no learning) OR Gap ≥ 25% (severe overfitting)

---

## Functional Requirements

### FR1: Dataset Loading and Feature Extraction
**Priority:** P0 (Critical Path)

**Description:** Load H-E1 benchmark collection (63 datasets) and compute meta-features using existing feature computation code from H-M1.

**Inputs:**
- `../h-e1/code/output/benchmarks.json` (63 benchmarks from H-E1)
- `../h-m1/code/src/feature_computer.py` (reused feature extraction)

**Feature Set:**
- **Tier 1 Features (4):** sample_size, dimensionality, num_classes, class_imbalance
- **Tier 2 Features (6):** Domain-specific (image_resolution, channel_count, sequence_length, etc.)
- **Coverage:** Variable per feature (13.8%-75.9% from H-M1 analysis)

**Outputs:**
- `X_meta_features`: (63, F) numpy array where F=4-10 after NaN removal
- `y_method_families`: (63,) target labels (Linear/Polynomial/RNN/Augmentation)

**Preprocessing:**
1. Load benchmarks.json
2. Compute features via feature_computer.py
3. Extract method family rankings (top-1 per benchmark)
4. Remove features with >70% missing data
5. Z-score normalization for remaining features

**Acceptance Criteria:**
- All 63 benchmarks loaded successfully
- Features computed without errors
- NaN features removed (columns with >70% missing)
- Target labels balanced across 4 classes (within 15-35% per class)

---

### FR2: Baseline Model Implementation
**Priority:** P0 (Critical Path)

**Description:** Implement majority class baseline to establish floor performance for meta-classifier comparison.

**Model:** `sklearn.dummy.DummyClassifier(strategy="most_frequent")`

**Configuration:**
- No trainable parameters
- Deterministic prediction (always predicts most frequent class)
- Expected accuracy: ~25-30% (4 classes, slightly imbalanced)

**Inputs:**
- `X_train`: Training features (58 benchmarks per fold)
- `y_train`: Training labels (58 benchmarks per fold)

**Outputs:**
- `baseline_accuracy`: Scalar accuracy on test fold
- `baseline_cv_scores`: Array of 13 fold accuracies

**Acceptance Criteria:**
- Baseline trains without error
- Accuracy within expected range (20-35%)
- Consistent across all 13 folds (std < 10%)

---

### FR3: Random Forest Meta-Classifier Training
**Priority:** P0 (Critical Path)

**Description:** Train Random Forest ensemble on dataset meta-features with hyperparameters optimized for small-data robustness.

**Model Architecture:**
```python
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=100,          # Ensemble size
    max_depth=10,              # Prevent overfitting
    min_samples_split=5,       # Require 5+ samples to split
    min_samples_leaf=2,        # Require 2+ samples per leaf
    random_state=42,           # Reproducibility
    criterion="gini",          # Default (works well for multi-class)
    max_features="sqrt"        # Prevent tree correlation
)
```

**Training Strategy:** Leave-5-out Cross-Validation
- Total folds: 13 (63 benchmarks ÷ 5 = 12.6 → 13 folds)
- Training per fold: 58 benchmarks
- Test per fold: 5 benchmarks
- Full coverage: 13 folds × 5 = 65 predictions (some overlap)

**Inputs:**
- `X_meta_features`: (63, F) feature matrix
- `y_method_families`: (63,) target labels

**Outputs:**
- `trained_model`: Fitted RandomForestClassifier per fold
- `cv_scores`: Array of 13 fold accuracies
- `train_scores`: Array of 13 training accuracies (for gap calculation)
- `predictions`: (63,) predicted method families (full dataset coverage)

**Acceptance Criteria:**
- Model trains successfully on all 13 folds
- Training time <5 seconds per fold
- No sklearn warnings or convergence issues
- Predictions generated for all 63 benchmarks

---

### FR4: Cross-Validation Evaluation
**Priority:** P0 (Critical Path)

**Description:** Evaluate meta-classifier generalization using leave-5-out cross-validation and compare against baseline.

**Primary Metrics:**
1. **CV Accuracy:** Mean test accuracy across 13 folds
2. **Generalization Gap:** (Train Accuracy - Test Accuracy)
3. **Baseline Comparison:** CV Accuracy - Baseline Accuracy

**Evaluation Procedure:**
```python
from sklearn.model_selection import cross_val_score
from sklearn.metrics import accuracy_score

# Cross-validation scores
cv_scores = cross_val_score(model, X, y, cv=13, scoring='accuracy')
cv_mean = cv_scores.mean()
cv_std = cv_scores.std()

# Per-fold train/test gap
for train_idx, test_idx in cv_splitter.split(X):
    model.fit(X[train_idx], y[train_idx])
    train_acc = model.score(X[train_idx], y[train_idx])
    test_acc = model.score(X[test_idx], y[test_idx])
    gap = train_acc - test_acc
```

**Inputs:**
- `cv_scores`: Array of 13 test fold accuracies
- `train_scores`: Array of 13 training fold accuracies
- `baseline_cv_scores`: Array of 13 baseline fold accuracies

**Outputs:**
- `cv_accuracy`: Mean CV accuracy (scalar)
- `generalization_gap`: Mean (train - test) gap (scalar)
- `baseline_delta`: CV accuracy - baseline accuracy (scalar)
- `gate_result`: PASS | PARTIAL | FAIL based on thresholds

**Gate Evaluation Logic:**
```python
if cv_accuracy > 0.35 and generalization_gap < 0.20:
    gate_result = "PASS"
elif cv_accuracy >= 0.30 and generalization_gap < 0.25:
    gate_result = "PARTIAL"
else:
    gate_result = "FAIL"
```

**Acceptance Criteria:**
- All metrics computed without error
- Gate result matches thresholds exactly
- Results logged to `04_validation.md`

---

### FR5: Per-Domain Accuracy Analysis
**Priority:** P1 (Important)

**Description:** Break down CV accuracy by benchmark domain (Vision/NLP/Tabular) to identify domain-specific performance patterns.

**Domain Distribution (from H-E1):**
- Vision: 27 benchmarks (42.9%)
- NLP: 15 benchmarks (23.8%)
- Tabular: 11 benchmarks (17.5%)
- Other: 10 benchmarks (15.9%)

**Analysis:**
```python
for domain in ["Vision", "NLP", "Tabular", "Other"]:
    domain_mask = [b["domain"] == domain for b in benchmarks]
    domain_accuracy = accuracy_score(y_true[domain_mask], y_pred[domain_mask])
```

**Outputs:**
- `domain_accuracies`: Dict mapping domain → accuracy
- `domain_counts`: Dict mapping domain → sample count

**Acceptance Criteria:**
- Accuracies computed for all 4 domains
- Results show if model generalizes across domains or only some

---

### FR6: Feature Importance Extraction
**Priority:** P1 (Important)

**Description:** Extract Random Forest feature importances to validate which meta-features drive method predictions.

**Extraction:**
```python
feature_importances = model.feature_importances_
feature_names = X_meta_features.columns
importance_df = pd.DataFrame({
    'feature': feature_names,
    'importance': feature_importances
}).sort_values('importance', ascending=False)
```

**Outputs:**
- `feature_importance_df`: Sorted DataFrame (feature, importance)
- Top-3 features identified

**Acceptance Criteria:**
- Importances sum to 1.0 (normalized)
- All features have importance ≥ 0
- Top feature has importance > 0.1

---

## Non-Functional Requirements

### NFR1: Reproducibility
- Fixed random seed (`random_state=42`) for all stochastic operations
- Identical CV splits across runs using fixed seed
- Feature computation deterministic (no random sampling)

### NFR2: Performance
- Total runtime <5 minutes (including feature extraction)
- Per-fold training <5 seconds
- Feature extraction <1 minute

### NFR3: Code Quality
- Reuse H-M1 feature computation code (no duplication)
- Clear separation: data loading → feature extraction → training → evaluation
- Type hints for all functions
- Docstrings for core functions (feature_computer, train_model, evaluate)

### NFR4: Error Handling
- Graceful handling of missing features (NaN removal with warning)
- Validation of feature matrix shape before training
- Assertion checks for CV fold counts (13 expected)

---

## Data Dependencies

### Input Data Sources

| Data Source | Path | Description | Provider |
|-------------|------|-------------|----------|
| H-E1 Benchmarks | `../h-e1/code/output/benchmarks.json` | 63 benchmarks with method rankings | H-E1 (prerequisite) |
| Feature Computer | `../h-m1/code/src/feature_computer.py` | Tier 1+2 feature extraction | H-M1 (prerequisite) |

### Data Specifications

**Benchmark JSON Structure:**
```json
{
  "name": "CIFAR-10",
  "domain": "Vision",
  "method_rankings": {
    "Linear": 45.2,
    "Polynomial": 78.9,
    "RNN": 23.1,
    "Augmentation": 89.3
  },
  "metadata": {
    "sample_size": 50000,
    "image_resolution": [32, 32],
    "num_classes": 10
  }
}
```

**Feature Matrix Shape:**
- Rows: 63 benchmarks
- Columns: 4-10 features (after NaN removal)
- Format: pandas DataFrame with named columns

**Target Labels:**
- Values: ["Linear", "Polynomial", "RNN", "Augmentation"]
- Encoding: Top-1 method family per benchmark (argmax of rankings)

---

## Evaluation Metrics

### Primary Metrics (Gate Evaluation)

| Metric | Formula | Threshold | Gate |
|--------|---------|-----------|------|
| CV Accuracy | mean(accuracy per fold) | > 35% | PASS |
| Generalization Gap | mean(train_acc - test_acc) | < 20% | PASS |
| Baseline Delta | CV Accuracy - Baseline | > 5% | Validation |

### Secondary Metrics (Analysis)

| Metric | Purpose | Expected Range |
|--------|---------|----------------|
| Per-Domain Accuracy | Domain generalization | 25-50% per domain |
| Feature Importance | Feature contribution | Top-3 total > 0.5 |
| Confusion Matrix | Method family confusion | Diagonal dominance |

---

## Visualization Requirements

### Mandatory Figures

#### V1: Gate Metrics Comparison (Required)
**Type:** Bar chart
**X-axis:** [Baseline, Target (35%), Actual CV Accuracy]
**Y-axis:** Accuracy (%)
**Elements:**
- Horizontal threshold lines: PASS (35%), Target (40%)
- Baseline bar (red), Target bar (blue), Actual bar (green if PASS, yellow if PARTIAL, red if FAIL)

**Acceptance:** Figure must be generated and saved to `figures/gate_metrics.png`

### Recommended Figures (LLM Autonomous)

#### V2: Learning Curve
**Purpose:** Test if accuracy improves with more training data
**X-axis:** Training size (10, 20, 30, 40, 50, 58 benchmarks)
**Y-axis:** CV Accuracy
**Shows:** Whether 50-60 datasets is sufficient or more would help

#### V3: Confusion Matrix
**Purpose:** Identify which method families are confused
**Type:** Heatmap (4×4: Linear, Polynomial, RNN, Augmentation)
**Shows:** If model generalizes across all families or only some

#### V4: Per-Domain Accuracy
**Purpose:** Show domain-specific performance
**X-axis:** Vision, NLP, Tabular, Other
**Y-axis:** Accuracy (%)
**Shows:** Whether model works equally well across domains

#### V5: Feature Importance
**Purpose:** Validate which features drive predictions
**Type:** Horizontal bar chart
**X-axis:** Importance score
**Y-axis:** Feature names (sample_size, dimensionality, etc.)

#### V6: Generalization Gap per Fold
**Purpose:** Show overfitting severity
**Type:** Line plot with two lines (train vs test)
**X-axis:** Fold index (1-13)
**Y-axis:** Accuracy (%)
**Lines:** Train (blue), Test (red)

**Note:** Phase 4 Coder decides final figure set. All figures saved to `figures/` subdirectory.

---

## Success Criteria

### Phase 3 Success (This PRD)
- ✅ PRD captures all Phase 2C experiment specifications
- ✅ Functional requirements cover full experiment pipeline
- ✅ Data dependencies clearly documented
- ✅ Gate evaluation logic explicitly defined

### Phase 4 Success (Implementation & Validation)
- ✅ All FRs implemented and tested
- ✅ CV Accuracy > 35% (PASS threshold)
- ✅ Generalization Gap < 20% (no severe overfitting)
- ✅ Results logged to `04_validation.md`

**Gate Result Interpretation:**
- **PASS:** 50-60 datasets sufficient → proceed to H-M3
- **PARTIAL:** Limited learning → investigate feature quality in H-M3
- **FAIL:** Insufficient data → hypothesis rejected

---

## Dependencies and Prerequisites

### Upstream Dependencies
- **H-E1 (EXISTENCE):** Benchmark collection (63 datasets)
  - Status: COMPLETED (PASS)
  - Output: `benchmarks.json` with 63 benchmarks
  
- **H-M1 (MECHANISM):** Feature-ranking correlation analysis
  - Status: COMPLETED (PARTIAL - 2/3 correlations found)
  - Output: `feature_computer.py` for feature extraction
  - Lesson: Limited feature diversity (Vision-heavy, sparse Tier 2 coverage)

### Downstream Dependencies
- **H-M3:** Tests if Random Forest extracts generalizable patterns
  - Prerequisite: H-M2 must PASS or PARTIAL (demonstrates learning)
  - If H-M2 FAIL: H-M3 cannot proceed (no pattern to extract)

### External Dependencies
- `sklearn` (v1.0+): RandomForestClassifier, cross_val_score, DummyClassifier
- `numpy` (v1.20+): Array operations
- `pandas` (v1.3+): DataFrame handling
- `scipy` (v1.7+): Statistical functions (if needed)
- `matplotlib` (v3.4+): Visualization

---

## Risk Mitigation

### Risk 1: Insufficient Feature Diversity (from H-M1 lesson)
**Likelihood:** HIGH (H-M1 showed 0% coverage for many Tier 2 features)
**Impact:** Meta-classifier may only learn Vision-specific patterns
**Mitigation:**
- Focus on Tier 1 features (universal across domains)
- Document per-domain accuracy to identify domain-specific failures
- If PARTIAL result, annotate which domains/features work vs don't

### Risk 2: Small Sample Size Overfitting
**Likelihood:** MEDIUM (63 samples is small for ML)
**Impact:** High generalization gap (>25%), FAIL gate
**Mitigation:**
- Conservative hyperparameters (max_depth=10, min_samples_split=5)
- Leave-5-out CV (mimics real deployment: predict on 5 new datasets)
- Compare train vs test accuracy explicitly (detect overfitting early)

### Risk 3: Class Imbalance
**Likelihood:** LOW (4 method families, likely 15-35% each)
**Impact:** Model biased toward majority class
**Mitigation:**
- Measure baseline (majority class predictor) to establish floor
- Check per-class accuracy in confusion matrix
- If severe imbalance detected, note in validation report

---

## Appendix: Reference Implementations

### A1: sklearn RandomForestClassifier
- **URL:** https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html
- **Key Parameters:** n_estimators, max_depth, min_samples_split, min_samples_leaf
- **Usage:** Standard multi-class classification

### A2: sklearn Cross-Validation
- **URL:** https://scikit-learn.org/stable/modules/cross_validation.html
- **Strategy:** Leave-K-out for small datasets
- **Implementation:** `cross_val_score` with custom CV splitter

### A3: H-M1 Feature Computation
- **Path:** `../h-m1/code/src/feature_computer.py`
- **Functions:** `compute_tier1_features()`, `compute_tier2_features()`
- **Note:** Mock data fix already applied (no synthetic defaults)

### A4: H-E1 Benchmark Collection
- **Path:** `../h-e1/code/output/benchmarks.json`
- **Format:** JSON array with 63 benchmark objects
- **Fields:** name, domain, method_rankings, metadata

---

## Validation Plan (Phase 4)

### Validation Steps
1. **Data Loading:** Verify 63 benchmarks loaded, features computed
2. **Baseline Check:** Baseline accuracy within expected range (20-35%)
3. **Training:** All 13 folds train without error
4. **Gate Evaluation:** Compare CV accuracy and gap against thresholds
5. **Documentation:** Write `04_validation.md` with gate result and findings

### Expected Outcomes
- **Best Case (PASS):** CV Accuracy 40-50%, Gap <15%
  - Interpretation: 50-60 datasets sufficient for meta-learning
  
- **Likely Case (PARTIAL):** CV Accuracy 30-35%, Gap 15-20%
  - Interpretation: Limited learning, likely due to sparse features from H-M1
  
- **Worst Case (FAIL):** CV Accuracy <30% or Gap >25%
  - Interpretation: Insufficient data or no learnable patterns

---

**Next Steps:**
- Phase 3 Step 3: Architecture design (epic-level task breakdown)
- Phase 3 Step 5: Logic + Config agents (API signatures, hyperparameters)
- Phase 4: Implementation and validation

