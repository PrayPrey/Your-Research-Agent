# Hypothesis Context: H-E1

**Generated from:** 02b_verification_plan.md (Phase 2B)  
**Date:** 2026-07-13  
**Hypothesis ID:** h-e1

---

## Hypothesis Statement

**Type:** EXISTENCE

**Statement:** Under standard supervised learning conditions, if Logistic Regression is trained on log-scaled GitHub metadata (8 features) with balanced class weights, then it achieves ≥75% accuracy on held-out test set, because repository maintenance status is linearly separable in transformed feature space.

---

## Rationale

This hypothesis validates the core claim that simple linear methods suffice for moderate-accuracy repository maintenance prediction. Success proves linear separability, eliminating need for complex ensemble methods for this threshold.

---

## Variables

- **IV:** GitHub metadata features (stars_log, forks_log, contributors_log, total_commits_log, open_issues_log, days_since_last_commit, commit_frequency_median_weekly, issue_resolution_rate)
- **DV:** Binary classification accuracy on stratified test split
- **CV:** Dataset period (2020-2024), min_stars=32, stratified 80/20 split, StandardScaler normalization

---

## Experimental Setup (from Phase 2B Section 1.3)

### Dataset
- **Source:** Papers with Code benchmark repositories + GitHub REST API
- **Path:** GitHub REST API extraction (2020-2024)
- **Size:** 2000 repositories
- **Selection:** min_stars=32, non-fork, benchmark status

### Model
- **Type:** Linear classifier with L2 regularization
- **Source:** scikit-learn 1.x
- **Parameters:** max_iter=1000, class_weight='balanced', solver='lbfgs', random_state=42
- **Training Time:** ~30 seconds on single CPU

---

## Baseline & Comparison Targets

| Method | Performance | Dataset |
|--------|-------------|---------|
| Majority Baseline | ~60% (class distribution dependent) | Same test set |
| Composite Stability Index (CSI) | F1 0.80 (Adejumo & Johnson 2025) | 100 repos |
| Gradient Boosting + HITS | C-Index 0.810 (He et al. 2024) | 103,354 repos |

---

## Verification Protocol

1. Extract 2000 Papers with Code benchmark repositories via GitHub REST API (2020-2024, min_stars=32)
2. Engineer 8 features with log1p transform for long-tail distributions, compute derived features (commit_frequency_median_weekly, issue_resolution_rate)
3. Create binary labels from days_since_last_commit < 180, perform stratified 80/20 split with random_state=42
4. Train sklearn LogisticRegression(max_iter=1000, class_weight='balanced', solver='lbfgs') on training set
5. Evaluate on test set: compute accuracy, precision, recall, F1 score
6. Validate on high-confidence subset (last_commit <90 days OR archived/keywords) to check label noise impact

---

## Success Criteria

- **Primary:** Accuracy ≥75% AND F1 ≥0.73 on held-out test set
- **Secondary:** Accuracy ≥70% on high-confidence subset (validates labeling strategy)
- **Statistical:** Performance exceeds majority baseline by ≥10%

---

## Failure Response

- **IF 70-74% accuracy:** PIVOT to moderate success interpretation (simple provides baseline, complex offers incremental gains)
- **IF <70% accuracy:** EXPLORE non-linear methods, analyze feature interactions, investigate distributional assumptions

---

## Gate Condition

- **Type:** MUST_WORK
- **If Fail:** Linear separability hypothesis rejected, pivot to analyzing why non-linear methods necessary

---

## Prerequisites

None (foundation hypothesis)

---

## Dependencies

**Dependent Hypotheses:** H-M1 (Mechanism - must wait for H-E1 to pass)

---

*Source: Phase 2B Section 2.2 (H-E1 Specification)*
