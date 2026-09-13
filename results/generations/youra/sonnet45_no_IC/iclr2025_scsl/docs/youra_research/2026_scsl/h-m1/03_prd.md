# Product Requirements Document: H-M1 Linear Separability Mechanism

**Document Type:** PRD (Product Requirements Document)  
**Hypothesis ID:** H-M1  
**Hypothesis Type:** MECHANISM  
**Date:** 2026-07-13  
**Author:** Anonymous  
**Status:** Phase 3 - Implementation Planning

---

## Executive Summary

This PRD defines the requirements for implementing H-M1, a mechanism analysis experiment that investigates **why** the H-E1 logistic regression model achieved perfect accuracy. The experiment analyzes linear separability by extracting learned coefficients, comparing LR vs Gradient Boosting performance, and visualizing decision boundaries.

**Key Deliverable:** Mechanism validation showing that repository maintenance patterns form linearly separable clusters in log-scaled feature space.

---

## Problem Statement

### Context

H-E1 demonstrated that logistic regression achieves perfect classification (Accuracy 1.0, F1 1.0) on repository maintenance prediction. However, **why** this linear model works so well remains unexplained. Understanding the mechanism is critical for:
1. Validating the linear separability assumption
2. Confirming feature importance aligns with causal pathway
3. Determining if non-linear models are necessary

### Hypothesis Statement

Under log-scaled feature transformation, if repository maintenance patterns (recent activity, community engagement, development velocity) are present, then they form linearly separable clusters in feature space, because maintained repositories exhibit consistently higher activity metrics and lower staleness that align with a linear decision boundary.

### Prerequisites

- **H-E1 COMPLETED (PASS):** Trained logistic regression model with perfect accuracy
- **Dataset:** Papers with Code repos (2000 samples, 8 log-scaled features)
- **Validated Model:** `h-e1/models/logistic_regression.pkl`

---

## Functional Requirements

### FR-1: Load H-E1 Trained Model

**Priority:** CRITICAL  
**Description:** Load the validated logistic regression model from H-E1 validation phase.

**Acceptance Criteria:**
- Model loaded from `docs/youra_research/h-e1/models/logistic_regression.pkl`
- Model type: sklearn LogisticRegression with balanced class weights
- Coefficients shape: (8,) for 8 features
- Fallback: Retrain if model file not found

**Dependencies:** H-E1 validation complete

---

### FR-2: Extract and Interpret Coefficients

**Priority:** CRITICAL  
**Description:** Extract learned coefficients from LR model and verify signs match expected causal pathway.

**Acceptance Criteria:**
- Extract `model.coef_[0]` (8 feature weights)
- Map coefficients to feature names: [stars_log, forks_log, contributors_log, commits_log, issues_log, days_since_last, commit_freq_weekly, issue_resolution_rate]
- **Verification:** `days_since_last_commit` coefficient < 0 (negative)
- **Verification:** All activity metrics coefficients > 0 (positive)
- Generate bar chart visualization showing coefficients

**Success Metric:** Coefficient signs match expected (negative for staleness, positive for activity)

---

### FR-3: Train Gradient Boosting Baseline

**Priority:** CRITICAL  
**Description:** Train XGBoost Gradient Boosting classifier as non-linear baseline for comparison.

**Acceptance Criteria:**
- Model: `sklearn.ensemble.GradientBoostingClassifier`
- Hyperparameters:
  - n_estimators: 50
  - max_depth: 6
  - learning_rate: 0.1
  - random_state: 42
- Training data: Same as H-E1 (1600 train samples, StandardScaler normalized)
- Training time: ~10 minutes on multi-core CPU

**Dependencies:** Dataset loaded and preprocessed

---

### FR-4: Compare LR vs GB Performance

**Priority:** CRITICAL  
**Description:** Measure accuracy gap between logistic regression and gradient boosting to validate linear sufficiency.

**Acceptance Criteria:**
- Compute accuracy for both models on test set (400 samples)
- Calculate performance gap: `|LR_accuracy - GB_accuracy|`
- **Linear Sufficient:** Gap ≤ 5%
- **Non-linear Needed:** Gap > 10%
- Generate side-by-side bar chart (LR vs GB accuracy + F1)

**Success Metric:** Performance gap ≤ 5% validates linear mechanism

---

### FR-5: Visualize Decision Boundary via PCA

**Priority:** HIGH  
**Description:** Project 8D feature space to 2D using PCA and visualize linear decision boundary.

**Acceptance Criteria:**
- Apply PCA with n_components=2 to test set
- Create scatter plot with class colors (maintained vs abandoned)
- Overlay LR decision boundary using contour plot
- Generate mesh grid for boundary visualization
- Save figure to `figures/decision_boundary_pca.png`

**Dependencies:** LR model loaded, test set available

---

### FR-6: Feature Importance Analysis

**Priority:** MEDIUM  
**Description:** Compare feature importance between LR (coefficients) and GB (feature_importances_) to validate causal pathway alignment.

**Acceptance Criteria:**
- Extract LR coefficient magnitudes as importance scores
- Extract GB `feature_importances_` attribute
- Generate side-by-side bar chart comparing both models
- **Expected Top Features:** days_since_last, stars_log, commits_log
- Save figure to `figures/feature_importance_comparison.png`

**Success Metric:** Top-3 features consistent between LR and GB

---

### FR-7: Generate Visualizations

**Priority:** HIGH  
**Description:** Create all required figures for mechanism interpretation.

**Required Figures:**
1. **Coefficient Bar Chart:** LR coefficients with sign verification
2. **Performance Comparison:** LR vs GB accuracy and F1
3. **Decision Boundary:** 2D PCA projection with linear separator
4. **Feature Importance:** Side-by-side comparison (LR vs GB)
5. **Confusion Matrices:** Both LR and GB for detailed analysis

**Acceptance Criteria:**
- All figures saved to `docs/youra_research/h-m1/figures/`
- PNG format with 300 DPI resolution
- Clear axis labels and legends
- Consistent color scheme (seaborn default)

---

## Data Requirements

### DR-1: Dataset Reuse from H-E1

**Source:** Papers with Code Benchmark Repositories + GitHub Metadata  
**Method:** Load from H-E1 validation artifacts  
**Path:** `docs/youra_research/h-e1/data/github_repos_metadata.csv`

**Specifications:**
- **Size:** 2000 repositories
- **Features:** 8 log-scaled features
  1. stars_log (log1p transformed)
  2. forks_log (log1p transformed)
  3. contributors_log (log1p transformed)
  4. total_commits_log (log1p transformed)
  5. open_issues_log (log1p transformed)
  6. days_since_last_commit (raw value)
  7. commit_frequency_median_weekly (derived)
  8. issue_resolution_rate (derived)
- **Labels:** Binary (maintained=1 if days_since_last < 180, else 0)
- **Split:** Stratified 80/20 train/test (random_state=42)

**Preprocessing:**
- Log1p transform on count features (already applied)
- StandardScaler normalization (fit on train, transform on train+test)

**Rationale:** H-M1 analyzes the mechanism of H-E1's success. Must use identical dataset for controlled comparison.

---

## Evaluation Metrics

### EM-1: Coefficient Sign Verification

**Metric:** Binary pass/fail  
**Calculation:**
```python
signs_correct = (
    coefficients[5] < 0 and  # days_since_last_commit
    all(coefficients[i] > 0 for i in [0,1,2,3,4,6,7])  # activity metrics
)
```
**Threshold:** PASS if all signs match expected

---

### EM-2: Performance Gap (LR vs GB)

**Metric:** Absolute accuracy difference  
**Calculation:** `|accuracy_LR - accuracy_GB|`  
**Thresholds:**
- ≤ 5%: Linear sufficient (PASS)
- 5-10%: Gray zone (investigate)
- > 10%: Non-linear needed (mechanism rejected)

---

### EM-3: Feature Importance Alignment

**Metric:** Top-3 feature overlap between LR and GB  
**Calculation:** Jaccard similarity of top-3 feature sets  
**Threshold:** ≥ 2 features overlap (PASS)

---

### EM-4: Gate Condition (MUST_WORK)

**Combined Metric:**
```python
mechanism_validated = (
    coefficient_signs_correct AND
    performance_gap <= 0.05 AND
    feature_importance_overlap >= 2
)
```
**Result:**
- PASS: All three conditions met → Linear mechanism confirmed
- FAIL: Any condition fails → Investigate non-linear patterns, report complexity requirements

---

## Non-Functional Requirements

### NFR-1: Reproducibility

**Description:** All results must be reproducible with fixed random seeds.

**Requirements:**
- random_state=42 for all sklearn models
- Same dataset split as H-E1 (stratified 80/20)
- Document library versions: sklearn 1.x, numpy, pandas

---

### NFR-2: Execution Time

**Description:** Analysis completes within reasonable time on standard CPU.

**Requirements:**
- GB training: ≤ 15 minutes
- PCA visualization: ≤ 2 minutes
- Total runtime: ≤ 20 minutes

---

### NFR-3: Code Modularity

**Description:** Analysis implemented as reusable MechanismAnalyzer class.

**Requirements:**
- Class interface: `__init__(lr_model, X, y)`
- Methods: `extract_coefficients()`, `compare_with_gb()`, `visualize_decision_boundary()`
- Enable reuse for future mechanism analysis experiments

---

## Success Criteria

### Primary Success Criteria

1. **Coefficient Signs Correct:** All 8 features show expected signs (negative for staleness, positive for activity)
2. **Linear Sufficient:** LR vs GB accuracy gap ≤ 5%
3. **Causal Pathway Validated:** Feature importance aligns between models (≥2 top features overlap)

### Secondary Success Criteria

4. **Visualization Quality:** All 5 required figures generated and interpretable
5. **MUST_WORK Gate:** All primary criteria met → H-M1 PASS

### Failure Triggers

- Coefficient signs incorrect → Feature engineering issues
- GB >> LR (>10% gap) → Non-linear interactions present, linear mechanism rejected
- Feature importance misalignment → Causal pathway incorrect

---

## Dependencies and Constraints

### Dependencies

1. **H-E1 Completion:** Trained LR model and validated dataset
2. **Libraries:** scikit-learn 1.x, numpy, pandas, matplotlib, seaborn
3. **Hardware:** Multi-core CPU for GB training

### Constraints

1. **No Model Retraining:** H-M1 analyzes existing H-E1 model (load only, no new training for LR)
2. **Dataset Frozen:** Must use exact H-E1 dataset for controlled comparison
3. **Single Seed:** random_state=42 inherited from H-E1 (no multi-seed averaging)

---

## Deliverables

### Code Artifacts

1. `mechanism_analysis.py` - MechanismAnalyzer class implementation
2. `run_h_m1_experiment.py` - Experiment execution script

### Output Files

1. `docs/youra_research/h-m1/figures/coefficient_bar_chart.png`
2. `docs/youra_research/h-m1/figures/performance_comparison.png`
3. `docs/youra_research/h-m1/figures/decision_boundary_pca.png`
4. `docs/youra_research/h-m1/figures/feature_importance_comparison.png`
5. `docs/youra_research/h-m1/figures/confusion_matrix_comparison.png`
6. `docs/youra_research/h-m1/04_validation.md` - Validation report with results

---

## Risk Assessment

### High Risk

**Risk:** GB training fails due to memory constraints  
**Mitigation:** Use n_estimators=50 (lightweight), reduce max_depth if needed

**Risk:** H-E1 model file not found  
**Mitigation:** Fallback to retraining LR model with same hyperparameters

### Medium Risk

**Risk:** PCA loses critical variance in 2D projection  
**Mitigation:** Report explained variance ratio, use first 2 PCs only for visualization (not evaluation)

### Low Risk

**Risk:** Coefficient interpretation ambiguous due to feature scaling  
**Mitigation:** Use StandardScaler consistently, interpret coefficient magnitudes relative to each other

---

## Appendix: Traceability Matrix

| Requirement | Source | Phase 2C Section |
|-------------|--------|------------------|
| FR-1 (Load Model) | H-E1 Validation | Baseline Model |
| FR-2 (Coefficients) | Phase 2B H-M1 Protocol | Primary Metrics |
| FR-3 (GB Training) | Phase 2C Experiment Brief | Proposed Model |
| FR-4 (LR vs GB) | Phase 2B Success Criteria | Primary Metrics |
| FR-5 (PCA Viz) | Phase 2C Visualization | Visualization Requirements |
| FR-6 (Feature Importance) | Phase 2B Mechanism Prediction | Primary Metrics |
| DR-1 (Dataset) | H-E1 Validation | Dataset (Continuation) |
| EM-1 (Coefficient Signs) | Phase 2B H-M1 Protocol | Success Criteria |
| EM-2 (Performance Gap) | Phase 2B H-M1 Protocol | Success Criteria |
| EM-4 (MUST_WORK Gate) | Phase 2B Verification Plan | Gate Condition |

---

**PRD Status:** Complete and ready for Architecture design (Step 3)
