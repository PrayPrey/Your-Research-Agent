# Hypothesis Refinement: Empirical Validation of Simple Classification for Repository Maintenance Prediction

**Hypothesis ID**: h-lr1  
**Version**: 1.0  
**Date**: 2026-07-13  
**Status**: Ready for Phase 2B  
**Phase**: 2A-Dialogue (Round Table Discussion Converged)

---

## Executive Summary

This hypothesis addresses **Gap 1** from Phase 1 research: the absence of empirical validation for simple classification methods (Logistic Regression) in repository maintenance prediction. While prior work ([He et al., 2024]; [Adejumo & Johnson, 2025]) demonstrates that GitHub metadata predicts repository health using complex methods (gradient boosting, network analysis) or simple aggregation (weighted sums), NO prior work has systematically compared these approaches on the same dataset with temporal validation.

**Core Claim**: Logistic Regression trained on basic GitHub metadata achieves ≥75% binary classification accuracy for repository maintenance status, demonstrating that simple methods suffice for moderate-accuracy maintenance prediction without complex ensemble or network analysis.

**Novel Contribution**: First controlled three-way comparison (CSI aggregation vs LR simple classification vs GB complex ensemble) with temporal validation (2020-2022 train → 2023-2024 test), quantifying when simple methods suffice vs when complex methods are necessary.

---

## Research Question

**Primary**: Can simple classification methods predict benchmark maintenance status from GitHub metadata with ≥75% accuracy on real benchmark repositories?

**Detailed Sub-Questions**:
1. Which GitHub metadata features correlate with benchmark maintenance status? (ANSWERED by Phase 1: stars, forks, commits, contributors, last_commit_date)
2. What is a realistic accuracy target for binary maintenance classification? (TARGET: 75% based on [Adejumo & Johnson, 2025] F1 0.80 precedent)
3. Can Logistic Regression achieve this target without ensemble methods? (HYPOTHESIS TO TEST)
4. How should maintenance status be defined from metadata timestamps? (DEFINITION: last_commit <180 days)
5. What simple baseline demonstrates the method's utility? (BASELINES: majority class, CSI replication)

---

## Hypothesis Statement

### Core Hypothesis

**"Logistic Regression trained on basic GitHub metadata (stars, forks, commits, contributors, last_commit_date, derived features) achieves ≥75% binary classification accuracy for repository maintenance status, demonstrating that simple methods suffice for moderate-accuracy maintenance prediction without complex ensemble or network analysis."**

### Mechanism

Repository maintenance is determined by a **linear combination** of log-scaled GitHub metadata features:

1. **Feature Extraction**: stars, forks, contributors, total_commits, open_issues, last_commit_date, derived features (commit_frequency_median_weekly, issue_resolution_rate)
2. **Feature Transformation**: log1p for long-tail distributions (addresses [He et al., 2024] observation that GitHub metrics are long-tailed)
3. **Normalization**: StandardScaler (zero mean, unit variance) for Logistic Regression
4. **Classification**: L2-regularized logistic loss with balanced class weights (handles class imbalance)

**Causal Pathway**: Maintained repositories exhibit higher recent activity (low days_since_last_commit), higher community engagement (stars, forks, contributors), and higher development velocity (commit_frequency). These patterns are **linearly separable** in feature space, allowing Logistic Regression to classify maintained vs abandoned repositories with 75-80% accuracy.

---

## Three Testable Predictions

### Prediction 1: Absolute Performance
**Claim**: LR achieves 75-80% accuracy on held-out test set (stratified 80/20 split) with F1 ≥0.73  
**Measurement**: Binary classification accuracy, precision, recall, F1  
**Pass Criterion**: Accuracy ≥75% AND F1 ≥0.73  
**Fail Criterion**: Accuracy <70% OR F1 <0.68 → Complex methods necessary

### Prediction 2: Relative Performance vs Baselines
**Claim**: LR outperforms majority-class baseline by ≥10% AND matches CSI within 3%  
**Measurement**: Δ(LR - Majority), Δ(LR - CSI) on same test set  
**Pass Criterion**: LR - Majority ≥10% AND |LR - CSI| ≤3%  
**Fail Criterion**: LR - Majority <8% → Insufficient utility over trivial baseline

### Prediction 3: Temporal Generalization
**Claim**: LR trained on 2020-2022 maintains ≥70% accuracy on 2023-2024 test set, matching or exceeding GB generalization  
**Measurement**: Accuracy drop: (Test_IID - Test_Temporal) for LR vs GB  
**Pass Criterion**: LR_Temporal ≥70% AND |LR_drop| ≤ |GB_drop| + 5%  
**Fail Criterion**: LR_Temporal <65% OR LR_drop > GB_drop + 10% → Simple methods fail to generalize

---

## Experimental Design (Replication-Ready)

### Dataset
- **Size**: 2000 benchmark repositories
- **Source**: Papers with Code benchmark list + GitHub REST API
- **Date Range**: 2020-2024
- **Selection Criteria**: min_stars=32, non-fork, benchmark status
- **Justification**: 10-20× [Adejumo & Johnson, 2025] scale (N=100), 1.7% of [Li et al., 2026] demonstrated scale (N=116K)

### Features (8 Total)

**Log-Scaled Features** (handles long-tail distributions):
1. `stars_log` = log1p(stargazers_count)
2. `forks_log` = log1p(forks_count)
3. `contributors_log` = log1p(contributor_count)
4. `total_commits_log` = log1p(commit_count)
5. `open_issues_log` = log1p(open_issues_count)

**Raw Features**:
6. `days_since_last_commit` = (now - last_push_date).days

**Derived Features** ([Adejumo & Johnson, 2025] approach):
7. `commit_frequency_median_weekly` = median weekly commits (outlier-robust)
8. `issue_resolution_rate` = closed / (open + closed + 1)

**Feature Normalization**: StandardScaler for LR (zero mean, unit variance). Raw features for GB/CSI.

### Labels
- **Definition**: Binary from `days_since_last_commit < 180` (maintained=1, abandoned=0)
- **Validation Subset**: High-confidence labels for noise check
  - **High-conf maintained**: last_commit <90 days & recent_commits >0 & not archived
  - **High-conf abandoned**: last_commit >365 days OR archived OR has_deprecation_keywords

### Models

**Baseline: Majority Class**
```python
sklearn.dummy.DummyClassifier(strategy='most_frequent')
```

**Baseline: CSI Replication** ([Adejumo & Johnson, 2025])
```python
CSI = 0.30*CSI_C + 0.25*CSI_I + 0.25*CSI_PR + 0.20*CSI_CE
y_pred = (CSI > 0.6).astype(int)
```

**Model: Logistic Regression**
```python
sklearn.linear_model.LogisticRegression(
    max_iter=1000,
    class_weight='balanced',  # Handles class imbalance
    solver='lbfgs',
    random_state=42
)
```
- **Training Time**: ~30 seconds on single CPU

**Model: Gradient Boosting** ([He et al., 2024] replication)
```python
xgboost.XGBClassifier(
    n_estimators=50,
    max_depth=6,
    scale_pos_weight=(n_abandoned / n_maintained),
    random_state=42
)
```
- **Training Time**: ~10 minutes on multi-core

### Evaluation

**Split 1: IID (Standard)**
- Method: stratified_split(0.8/0.2, random_state=42)
- Purpose: Standard ML evaluation

**Split 2: Temporal (Generalization)**
- Train: 2020-01-01 to 2022-12-31
- Test: 2023-01-01 to 2024-12-31
- Purpose: Test temporal robustness

**Metrics**: accuracy, precision, recall, F1

**Validation Checks**:
1. **Temporal Stability Analysis**: scipy.stats.ks_2samp on features (train vs test distributions)
2. **Label Noise Check**: Report accuracy on high-confidence subset

---

## Novelty & Contribution

### Methodological Contribution (Guaranteed)
"First systematic empirical comparison of aggregation (CSI), simple classification (LR), and complex methods (GB) for repository maintenance prediction with controlled temporal validation."

**Why it matters**: Prior work ([He et al., 2024]; [Adejumo & Johnson, 2025]) used different datasets, no controlled comparison. The field needs this baseline study.

### Theoretical Contribution (Either Outcome)
- **IF LR ≥75%**: "Empirically confirms repository maintenance is linearly separable problem in basic GitHub metadata space"
- **IF LR <70%**: "Empirically demonstrates repository maintenance requires non-linear methods, identifies which features show non-linear relationships"

### Practical Contribution (If LR ≥75%)
"Establishes that practitioners can achieve 75-80% maintenance prediction accuracy with interpretable Logistic Regression (30s training) vs complex GB (10min training) or infrastructure-heavy HITS computation (1000+ core-hours)."

---

## Positioning Against Prior Work

| Paper | Method | Result | Gap Filled By Us |
|-------|---------|---------|------------------|
| [He et al., 2024] | GB + HITS centrality | C-Index 0.810 | We test if HITS necessary OR if simple features suffice |
| [Adejumo & Johnson, 2025] | CSI (weighted sum) | F1 0.80 | We test if classification improves over aggregation |
| [Our Work] | LR vs CSI vs GB | Accuracy 70-80% | First controlled comparison + temporal validation |

---

## Success Criteria & Adaptive Outcomes

### Strong Success
- LR ≥75% accuracy
- LR within 3% of CSI
- LR generalizes better than GB temporally
- **Interpretation**: "Simple methods suffice, complex unnecessary"

### Moderate Success
- LR 70-74% accuracy
- LR > majority + 10%
- **Interpretation**: "Simple provides moderate baseline, complex offers incremental gains"

### Failure (Still Valuable Finding)
- LR <70% accuracy
- **Interpretation**: "Problem requires non-linear methods" + analyze which features show non-linear relationships

**Adaptive Framework**: All outcomes yield scientific findings about complexity requirements for repository maintenance prediction.

---

## Feasibility Assessment

### Data Collection: ✅ FEASIBLE
- GitHub REST API provides all required metadata
- [Li et al., 2026] demonstrated 116K-scale extraction feasibility
- Papers with Code API lists benchmark repositories (no scraping needed)

### Automatic Labeling: ✅ SOUND
- Timestamp proxy (last_commit < 180 days) validated by [He et al., 2024] dual-definition approach
- High-confidence subset addresses label noise concerns

### Compute Requirements: ✅ TRIVIAL
- LR training: 30s on single CPU
- CSI computation: 5s (numpy operations)
- GB training: 10min on multi-core
- **No Spark/TiDB infrastructure needed** (vs [He et al., 2024] 1000 core-hours for HITS)

### Fundamental Barriers: ✅ NONE
- Linear classification mathematically straightforward
- No graph algorithms, no network analysis
- Standard sklearn/xgboost implementations

---

## Addressing Prior Failures (Serena Memory Lessons)

This hypothesis explicitly addresses lessons from prior attempts documented in `.serena/memories/`:

### h-m1 Failure Lessons Applied
- ✅ **Single dimension** (maintained yes/no) NOT multi-dimensional (data provenance, evaluation, metrics)
- ✅ **Realistic target** (75% accuracy) NOT aspirational (85% agreement threshold)
- ✅ **Simple method** (Logistic Regression) NOT multi-dimensional classification

### h-e1 Failure Lessons Applied
- ✅ **Real data** (GitHub REST API) NOT synthetic/mock data
- ✅ **No calibration requirements** (no ECE metrics) - just accuracy/F1
- ✅ **No ensemble methods** - Logistic Regression baseline first

### Mandatory Feasibility Constraints Satisfied
- ✅ No new benchmarks/rubrics (use existing GitHub repos)
- ✅ No synthetic/generated data (real GitHub metadata)
- ✅ No human evaluation (automated timestamp labeling)
- ✅ Immediately testable (GitHub REST API available now)

---

## Falsification Conditions

The hypothesis is **DISPROVEN** if ANY of:
1. LR_IID accuracy <70%
2. LR improvement over majority <8%
3. LR_temporal <65% while GB_temporal >75%

If disproven, we report: "Non-linear methods necessary for repository maintenance prediction" + analysis of which features require interactions.

---

## Phase 2B Readiness

This hypothesis is **ready for Phase 2B: Research Planning** with:

✅ **Specific core claim** with measurable threshold (75% accuracy)  
✅ **Testable mechanism** (linear classification on log-scaled features)  
✅ **Three explicit predictions** with pass/fail criteria  
✅ **Novel contribution** articulated (methodological gap-filling)  
✅ **Feasibility validated** (GitHub API sufficient, compute trivial)  
✅ **All objections addressed** (label noise, temporal validity, feature specs)  
✅ **Replication-ready protocol** (sklearn code, explicit parameters)  
✅ **Adaptive outcome framework** (all results yield scientific findings)

**Round Table Discussion**: 15 exchanges, 6 personas, convergence achieved  
**Convergence Criteria**: All 6 met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

---

**Next Phase**: Phase 2B - Research Planning  
**Expected Outputs**: Experimental protocol document, data collection pipeline, baseline implementations

---

*Generated by Phase 2A Round Table Discussion*  
*Date: 2026-07-13*  
*Discussion Exchanges: 15*  
*Convergence Round: 1*
