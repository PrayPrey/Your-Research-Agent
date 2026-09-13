# Phase 2B Context: H-M1 (Linear Separability Mechanism)

**Generated:** 2026-07-13T18:34:24Z
**Source:** 02b_verification_plan.md (Section 2.2)

---

## Hypothesis Information

**ID:** H-M1
**Type:** MECHANISM
**Statement:** Under log-scaled feature transformation, if repository maintenance patterns (recent activity, community engagement, development velocity) are present, then they form linearly separable clusters in feature space, because maintained repositories exhibit consistently higher activity metrics and lower staleness that align with a linear decision boundary.

**Rationale:** This hypothesis tests the underlying mechanism that enables H-E1. Validates whether linear combination of features suffices or whether complex feature interactions require non-linear methods. Critical for understanding when to use LR vs GB.

---

## Variables

- **IV:** Linear decision boundary (Logistic Regression coefficients on log-scaled features)
- **DV:** Classification performance metrics (accuracy, F1, coefficient interpretability)
- **CV:** Same dataset and normalization as H-E1, controlled comparison with Gradient Boosting

---

## Experimental Setup (from Phase 2B Section 1.3)

### Dataset
- **Source:** Papers with Code benchmark repositories + GitHub REST API
- **Path:** GitHub REST API extraction (2020-2024)
- **Size:** 2000 repositories
- **Selection:** min_stars=32, non-fork, benchmark status
- **Features:** 8 log-scaled features (stars_log, forks_log, contributors_log, total_commits_log, open_issues_log, days_since_last_commit, commit_frequency_median_weekly, issue_resolution_rate)
- **Labels:** Binary from days_since_last_commit < 180

### Model
- **Type:** Linear classifier with L2 regularization
- **Source:** scikit-learn 1.x
- **Parameters:** max_iter=1000, class_weight='balanced', solver='lbfgs', random_state=42
- **Training Time:** ~30 seconds on single CPU

---

## Success Criteria

- **Primary:** LR coefficients show expected signs (negative days_since_last_commit, positive activity) AND accuracy ≥75%
- **Secondary:** LR performance within 5% of Gradient Boosting (validates linear sufficiency)
- **Mechanistic:** Feature importance aligns with causal pathway (recent activity + engagement predict maintenance)

---

## Failure Response

- **IF coefficients incorrect signs:** EXPLORE feature engineering issues, check for multicollinearity, investigate label noise
- **IF GB >> LR (>10% gap):** PIVOT to analyzing feature interactions, consider polynomial features or interaction terms

---

## Gate Condition

- **Type:** MUST_WORK
- **If Fail:** Linear mechanism rejected, investigate non-linear patterns, report complexity requirements

---

## Prerequisites

**H-E1 (COMPLETED):**
- Status: COMPLETED with PASS gate
- Result: Accuracy 1.0, F1 1.0
- Validation File: /workspace/TEST_scsl/docs/youra_research/h-e1/04_validation.md
- Key Findings: Linear separability hypothesis validated, baseline model achieved perfect accuracy on test set

---

## Verification Protocol (from Phase 2B)

1. Train LR model per H-E1 protocol and extract learned coefficients
2. Analyze coefficient signs and magnitudes: expect negative for days_since_last_commit, positive for activity metrics (stars, forks, commits, contributors)
3. Visualize decision boundary in 2D PCA space to assess linear vs non-linear separation patterns
4. Train Gradient Boosting baseline (XGBoost: n_estimators=50, max_depth=6) on identical dataset
5. Compare LR vs GB performance gap: if gap ≤5%, linear mechanism sufficient; if gap >10%, complex interactions present
6. Calculate feature importance and correlation with maintenance status to validate causal pathway

---

## Baseline & Comparison Targets

| Method | Performance | Dataset |
|--------|-------------|---------|
| H-E1 LR Model | Accuracy 1.0, F1 1.0 | Same test set |
| Gradient Boosting Target | Expected: similar to LR if linear sufficient | Same test set |
| Performance Gap Threshold | ≤5% gap validates linear mechanism | Comparison metric |

---

## Risk Analysis (Relevant to H-M1)

**R1: Non-Linear Separability (High)**
- Description: Repository maintenance may require non-linear decision boundaries
- Detection: GB performance >10% better than LR
- Mitigation: Test polynomial features, analyze feature interactions

**R3: Feature Insufficiency (Medium)**
- Description: Basic metadata may miss critical maintenance signals
- Detection: LR significantly underperforms CSI baseline (>5% gap)
- Mitigation: Engineer derived features, test feature ablation

---

## Continuation Context

H-M1 builds on H-E1's validated baseline model. The experiment design should:
1. Reuse H-E1's trained model and extract coefficients
2. Implement coefficient interpretation analysis
3. Train Gradient Boosting comparison model
4. Generate visualization of decision boundary (PCA)
5. Calculate and compare feature importance
6. Assess linear vs non-linear separation quality
