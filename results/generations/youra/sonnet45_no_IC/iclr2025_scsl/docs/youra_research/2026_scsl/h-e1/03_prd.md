# Product Requirements Document: Repository Maintenance Classification (H-E1)

**Version:** 1.0  
**Date:** 2026-07-13  
**Author:** Anonymous  
**Hypothesis:** H-E1 (EXISTENCE)  
**Project:** Empirical Validation of Simple Classification for Repository Maintenance Prediction

---

## Executive Summary

This PRD defines the implementation requirements for validating hypothesis H-E1: testing whether Logistic Regression achieves ≥75% accuracy on repository maintenance classification using log-scaled GitHub metadata. This is a MUST_WORK gate experiment that validates the foundational assumption of linear separability before investigating mechanisms (H-M1).

**Success Criteria:** Accuracy ≥75% AND F1 ≥0.73 on held-out test set

**Scope:** Data collection via GitHub API, feature engineering, model training/evaluation, results validation

**Timeline:** Phase 3 → Phase 4 (implementation) → Gate validation

---

## Problem Statement

### Research Question
Can simple log-scaled features from GitHub metadata (stars, forks, commits, etc.) enable linear classification of repository maintenance status with accuracy ≥75%?

### Current Limitations
- **Baseline Reference (He et al. 2024):** Gradient Boosting + HITS centrality achieves C-Index 0.810 but requires graph features and complex ensemble
- **Baseline Reference (Adejumo & Johnson 2025):** Composite Stability Index achieves F1 0.80 but uses manual scoring
- **Gap:** Unknown if simple linear model on basic metadata can achieve competitive performance

### Hypothesis to Test
**H-E1 Statement:** Under standard supervised learning conditions, if Logistic Regression is trained on log-scaled GitHub metadata (8 features) with balanced class weights, then it achieves ≥75% accuracy on held-out test set, because repository maintenance status is linearly separable in transformed feature space.

**Gate Type:** MUST_WORK  
**Implications if Failed:** Linear separability hypothesis rejected → non-linear methods required

---

## Functional Requirements

### FR-1: Dataset Collection via GitHub API

**Priority:** P0 (Critical Path)

**Description:** Collect repository metadata from Papers with Code benchmark repositories using GitHub REST API v3

**Acceptance Criteria:**
- Query Papers with Code API for 2000 benchmark repositories (2020-2024, min_stars=32, non-fork)
- Extract metadata for each repository via GitHub API:
  - stars, forks, contributors, total_commits, open_issues
  - last_commit_date (for days_since_last_commit calculation)
  - commit history (for commit_frequency_median_weekly)
  - issue history (for issue_resolution_rate)
- Store raw metadata in structured format (CSV or JSON)
- Validate completeness: all 2000 repositories have complete metadata (no missing values)

**Dependencies:** GitHub API authentication token

**Data Specification:**
- **Source:** GitHub REST API v3 + Papers with Code API
- **Size:** 2000 repositories
- **Time Period:** 2020-2024
- **Format:** CSV with columns [repo_id, stars, forks, contributors, total_commits, open_issues, last_commit_date, commit_frequency_median_weekly, issue_resolution_rate]

---

### FR-2: Feature Engineering Pipeline

**Priority:** P0 (Critical Path)

**Description:** Transform raw GitHub metadata into 8 log-scaled features for linear classification

**Acceptance Criteria:**
- Apply log1p transformation to long-tail features: stars, forks, contributors, total_commits, open_issues
- Compute derived features:
  - `days_since_last_commit`: Current date - last_commit_date
  - `commit_frequency_median_weekly`: Median commits per week over repository lifetime
  - `issue_resolution_rate`: Closed issues / total issues (or 0 if no issues)
- Output 8-dimensional feature matrix with shape (2000, 8)
- Validate feature distributions: log-transformed features should be approximately normal

**Dependencies:** FR-1 (raw data collection)

**Implementation Notes:**
```python
import numpy as np

# Log1p transforms
features['stars_log'] = np.log1p(features['stars'])
features['forks_log'] = np.log1p(features['forks'])
features['contributors_log'] = np.log1p(features['contributors'])
features['total_commits_log'] = np.log1p(features['total_commits'])
features['open_issues_log'] = np.log1p(features['open_issues'])

# Keep raw: days_since_last_commit, commit_frequency_median_weekly, issue_resolution_rate
```

---

### FR-3: Label Generation

**Priority:** P0 (Critical Path)

**Description:** Create binary maintenance labels from temporal criteria

**Acceptance Criteria:**
- Generate binary labels: `maintained = 1` if `days_since_last_commit < 180`, else `abandoned = 0`
- Validate class distribution: report counts of maintained vs abandoned
- Check for extreme imbalance (warning if minority class < 10%)

**Dependencies:** FR-2 (days_since_last_commit feature)

---

### FR-4: Train/Test Split

**Priority:** P0 (Critical Path)

**Description:** Create stratified 80/20 train/test split for evaluation

**Acceptance Criteria:**
- Use stratified split to preserve class distribution
- Set random_state=42 for reproducibility
- Train set: 1600 samples (80%)
- Test set: 400 samples (20%)
- Validate: class distribution in train matches test within 2%

**Dependencies:** FR-3 (labels)

**Implementation:**
```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, stratify=y, random_state=42
)
```

---

### FR-5: Feature Normalization

**Priority:** P0 (Critical Path)

**Description:** Apply StandardScaler normalization to features

**Acceptance Criteria:**
- Fit StandardScaler on training data only
- Transform both train and test sets
- Validate: mean ≈ 0, std ≈ 1 for all training features
- Store scaler for inference

**Dependencies:** FR-4 (train/test split)

**Implementation:**
```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)
```

---

### FR-6: Logistic Regression Training

**Priority:** P0 (Critical Path)

**Description:** Train L2-regularized logistic regression classifier

**Acceptance Criteria:**
- Initialize LogisticRegression with:
  - max_iter=1000 (convergence guarantee)
  - class_weight='balanced' (handle class imbalance)
  - solver='lbfgs' (recommended for small datasets)
  - random_state=42 (reproducibility)
- Train on scaled training data
- Validate convergence: no convergence warnings
- Store trained model for evaluation

**Dependencies:** FR-5 (normalized features)

**Model Configuration:**
```python
from sklearn.linear_model import LogisticRegression

model = LogisticRegression(
    max_iter=1000,
    class_weight='balanced',
    solver='lbfgs',
    random_state=42
)

model.fit(X_train_scaled, y_train)
```

---

### FR-7: Evaluation Metrics Computation

**Priority:** P0 (Critical Path)

**Description:** Compute accuracy, precision, recall, F1 on held-out test set

**Acceptance Criteria:**
- Generate predictions on test set
- Compute metrics using sklearn.metrics:
  - Accuracy (primary success criterion)
  - F1 score (secondary success criterion)
  - Precision
  - Recall
- Compare against success thresholds:
  - Primary: accuracy ≥ 0.75 AND f1 ≥ 0.73
  - Baseline margin: accuracy ≥ (majority_baseline + 0.10)
- Display classification report

**Dependencies:** FR-6 (trained model)

**Expected Baselines:**
- Majority baseline: ~60% (class-distribution dependent)
- Target: ≥75% accuracy
- Context: CSI (F1 0.80), GB (C-Index 0.810)

**Implementation:**
```python
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

y_pred = model.predict(X_test_scaled)

accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

success = (accuracy >= 0.75) and (f1 >= 0.73)
print(f"Accuracy: {accuracy:.3f} (target: ≥0.75)")
print(f"F1 Score: {f1:.3f} (target: ≥0.73)")
print(f"Gate Status: {'✅ PASS' if success else '❌ FAIL'}")
```

---

### FR-8: Visualization Generation

**Priority:** P1 (Required for validation report)

**Description:** Generate visualizations to validate experiment results

**Acceptance Criteria:**
- Generate and save all figures to `{hypothesis_folder}/figures/`:
  1. **Gate Metrics Comparison** (mandatory): Bar chart showing target vs actual metrics
  2. **Confusion Matrix**: Heatmap showing TP/FP/TN/FN counts
  3. **Feature Importance**: Bar chart of LR coefficient magnitudes for 8 features
  4. **ROC Curve**: ROC curve with AUC score
  5. **Class Distribution**: Bar chart of maintained vs abandoned counts (train/test)
- All figures use consistent style and labels
- Save as PNG with 300 DPI for publication quality

**Dependencies:** FR-7 (evaluation results)

**Required Figures:**
```python
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, roc_curve, auc
import seaborn as sns

# 1. Gate Metrics Comparison
fig, ax = plt.subplots(figsize=(8, 5))
metrics_df = pd.DataFrame({
    'Metric': ['Accuracy', 'F1'],
    'Target': [0.75, 0.73],
    'Actual': [accuracy, f1]
})
# Bar chart implementation...

# 2. Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.title('Confusion Matrix')
plt.savefig(f'{hypothesis_folder}/figures/confusion_matrix.png', dpi=300)

# 3-5. Additional figures as specified...
```

---

### FR-9: Results Validation Report

**Priority:** P0 (Critical Path)

**Description:** Generate validation report documenting experiment results and gate decision

**Acceptance Criteria:**
- Document experimental setup (dataset size, model config, hyperparameters)
- Report all metrics with comparison to targets
- Include gate decision: PASS/FAIL based on accuracy ≥ 0.75 AND f1 ≥ 0.73
- Embed or reference all generated visualizations
- Save as `04_validation.md` in hypothesis folder

**Dependencies:** FR-7 (metrics), FR-8 (visualizations)

**Report Structure:**
```markdown
# Validation Report: H-E1

## Experiment Setup
- Dataset: 2000 Papers with Code repositories
- Features: 8 (log-scaled GitHub metadata)
- Model: Logistic Regression (sklearn, class_weight='balanced')
- Split: 80/20 stratified train/test

## Results
- Accuracy: {accuracy:.3f} (target: ≥0.75)
- F1 Score: {f1:.3f} (target: ≥0.73)
- Precision: {precision:.3f}
- Recall: {recall:.3f}

## Gate Decision
- Status: {PASS/FAIL}
- Rationale: {explanation based on metrics}

## Visualizations
[Links to 5 generated figures]
```

---

## Non-Functional Requirements

### NFR-1: Reproducibility

**Description:** All experiments must be fully reproducible

**Acceptance Criteria:**
- Fixed random seeds: random_state=42 for all stochastic operations
- Document all library versions (scikit-learn, numpy, pandas)
- Store raw data locally for re-runs
- Version control all code

---

### NFR-2: Performance

**Description:** Experiment execution should complete in reasonable time

**Acceptance Criteria:**
- Dataset collection: ≤10 minutes (with GitHub API rate limits)
- Model training: ≤1 minute on single CPU
- Total pipeline: ≤15 minutes end-to-end

---

### NFR-3: Code Quality

**Description:** Code should be readable and maintainable

**Acceptance Criteria:**
- Follow PEP 8 style guidelines
- Include docstrings for all functions
- Use type hints where appropriate
- Add comments for non-obvious logic (feature engineering, labeling criteria)

---

## Dependencies

### External Services
- **GitHub REST API v3** (authentication required)
- **Papers with Code API** (public, no auth required)

### Python Libraries
- scikit-learn ≥1.0 (LogisticRegression, metrics, preprocessing)
- pandas ≥1.3 (data manipulation)
- numpy ≥1.20 (numerical operations)
- matplotlib ≥3.4 (visualizations)
- seaborn ≥0.11 (enhanced visualizations)
- requests ≥2.26 (API calls)

### Environment
- Python 3.8+ (compatible with sklearn 1.x)
- Single CPU sufficient (no GPU required)
- ~500 MB disk space (dataset + figures)

---

## Success Criteria

### Primary Success (MUST_WORK Gate)
✅ **PASS:** accuracy ≥ 0.75 AND f1 ≥ 0.73

### Secondary Success
- Accuracy ≥ 0.70 on high-confidence subset (validates labeling quality)
- Performance exceeds majority baseline by ≥10%

### Partial Success
⚠️ **PARTIAL:** 0.70 ≤ accuracy < 0.75 (moderate evidence, interpretation needed)

### Failure
❌ **FAIL:** accuracy < 0.70 (linear separability hypothesis rejected)

---

## Risks and Mitigations

### R-1: GitHub API Rate Limiting
**Risk:** API quota exceeded during data collection  
**Mitigation:** Use authentication token (5000 requests/hour), implement retry logic, cache responses

### R-2: Class Imbalance
**Risk:** Extreme class imbalance (e.g., 90/10 split) biases model  
**Mitigation:** Use class_weight='balanced' in LogisticRegression, validate with F1 score (handles imbalance)

### R-3: Labeling Noise
**Risk:** 180-day threshold may mislabel temporarily inactive maintained repos  
**Mitigation:** Secondary validation with high-confidence subset, report class distribution statistics

### R-4: Feature Distribution Issues
**Risk:** Log transformation may not normalize all features  
**Mitigation:** Use StandardScaler normalization, validate feature distributions, add outlier detection

---

## Out of Scope

The following are explicitly NOT included in this implementation:

- ❌ Graph-based features (HITS centrality, PageRank) - reserved for H-M1
- ❌ Ensemble methods (Gradient Boosting, Random Forest) - comparison baseline only
- ❌ Hyperparameter tuning (C, solver comparison) - using sklearn defaults
- ❌ Temporal validation (train on 2020-2022, test on 2023-2024) - future work
- ❌ Deployment as production API - PoC validation only

---

## Appendix: Traceability

All requirements are traceable to Phase 2C experiment brief (`02c_experiment_brief.md`):

| Requirement | Source Section |
|-------------|----------------|
| FR-1: Dataset | "Dataset" → Papers with Code + GitHub API |
| FR-2: Features | "Features (8 total)" → log1p transforms |
| FR-3: Labels | "Labels" → 180-day threshold |
| FR-4: Split | "Splits" → stratified 80/20 |
| FR-5: Normalization | "Preprocessing" → StandardScaler |
| FR-6: Model | "Baseline Model" → LogisticRegression config |
| FR-7: Metrics | "Primary Metrics" + "Success Criteria" |
| FR-8: Visualizations | "Visualization Requirements" |
| FR-9: Report | "PoC Success Check" + gate criteria |

---

**End of PRD**
