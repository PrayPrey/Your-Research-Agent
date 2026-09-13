# Verification Plan: Empirical Validation of Simple Classification for Repository Maintenance Prediction

**Date:** 2026-07-13
**Hypothesis ID:** h-lr1
**Confidence:** 0.75
**Total Hypotheses:** 2

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
**Hypothesis:** Logistic Regression trained on basic GitHub metadata (stars, forks, commits, contributors, last_commit_date, derived features) achieves ≥75% binary classification accuracy for repository maintenance status, demonstrating that simple methods suffice for moderate-accuracy maintenance prediction without complex ensemble or network analysis.

**Research Question:** Can simple classification methods predict benchmark maintenance status from GitHub metadata with ≥75% accuracy on real benchmark repositories?

### 1.2 Alternative Hypothesis (H0)
Logistic Regression achieves <70% accuracy, confirming non-linear methods necessary

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Papers with Code benchmark repositories (2000 repos, 2020-2024) | Provides real-world benchmark repository metadata with temporal validation |
| **Model** | sklearn.linear_model.LogisticRegression | Tests linear separability hypothesis for repository maintenance classification |

**Dataset Details:**
- Source: Papers with Code benchmark repositories + GitHub REST API
- Path: GitHub REST API extraction (2020-2024)
- Size: 2000 repositories
- Selection: min_stars=32, non-fork, benchmark status

**Model Details:**
- Type: Linear classifier with L2 regularization
- Source: scikit-learn 1.x
- Parameters: max_iter=1000, class_weight='balanced', solver='lbfgs', random_state=42
- Training Time: ~30 seconds on single CPU

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Majority Baseline | ~60% (class distribution dependent) | Same test set |
| Composite Stability Index (CSI) | F1 0.80 (Adejumo & Johnson 2025) | 100 repos |
| Gradient Boosting + HITS | C-Index 0.810 (He et al. 2024) | 103,354 repos |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Linear separability: Repository maintenance is linearly separable in log-scaled feature space | Testable via LR performance | If LR <70%, assumption rejected → non-linear methods necessary |
| A2 | Timestamp proxy: last_commit <180 days is valid proxy for 'maintained' status | He et al. 2024 validation | Label noise → high-confidence subset validation |
| A3 | Feature sufficiency: Basic GitHub metadata captures maintenance signal without network analysis | Testable via LR vs CSI comparison | If LR far below CSI, basic features insufficient |
| A4 | Temporal stationarity: Models trained on 2020-2022 generalize to 2023-2024 | Testable via temporal split | Distribution shifts → KS test + honest reporting |
| A5 | Class balance: Majority baseline accuracy ~60% (more repos maintained than abandoned) | Verifiable via dataset inspection | Report actual class distribution |

### 1.6 Research Gap & Novelty

**Gap Addressed:** Gap 1 - Empirical Validation of Logistic Regression for Repository Maintenance Classification

**Novelty:**
- First controlled comparison of CSI (aggregation) vs LR (simple classification) vs GB (complex ensemble) on same dataset
- First temporal validation of repository maintenance prediction (train 2020-2022, test 2023-2024)
- Tests linear separability hypothesis for repository maintenance classification
- Quantifies complexity-accuracy-compute trade-offs (30s LR vs 10min GB vs 1000hr HITS infrastructure)

**Methodological Contribution:** First controlled three-way comparison (CSI vs LR vs GB) with temporal validation

**Practical Impact:** Quantifies when simple methods suffice vs complex methods necessary for repository maintenance prediction

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | Pending |
| H-M1 | Mechanism | MUST_WORK | H-E1 | Pending |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Logistic Regression Achieves Accuracy Threshold

**Type:** EXISTENCE
**Statement:** Under standard supervised learning conditions, if Logistic Regression is trained on log-scaled GitHub metadata (8 features) with balanced class weights, then it achieves ≥75% accuracy on held-out test set, because repository maintenance status is linearly separable in transformed feature space.

**Rationale:** This hypothesis validates the core claim that simple linear methods suffice for moderate-accuracy repository maintenance prediction. Success proves linear separability, eliminating need for complex ensemble methods for this threshold.

**Variables:**
- IV: GitHub metadata features (stars_log, forks_log, contributors_log, total_commits_log, open_issues_log, days_since_last_commit, commit_frequency_median_weekly, issue_resolution_rate)
- DV: Binary classification accuracy on stratified test split
- CV: Dataset period (2020-2024), min_stars=32, stratified 80/20 split, StandardScaler normalization

**Verification Protocol:**
1. Extract 2000 Papers with Code benchmark repositories via GitHub REST API (2020-2024, min_stars=32)
2. Engineer 8 features with log1p transform for long-tail distributions, compute derived features (commit_frequency_median_weekly, issue_resolution_rate)
3. Create binary labels from days_since_last_commit < 180, perform stratified 80/20 split with random_state=42
4. Train sklearn LogisticRegression(max_iter=1000, class_weight='balanced', solver='lbfgs') on training set
5. Evaluate on test set: compute accuracy, precision, recall, F1 score
6. Validate on high-confidence subset (last_commit <90 days OR archived/keywords) to check label noise impact

**Success Criteria:**
- Primary: Accuracy ≥75% AND F1 ≥0.73 on held-out test set
- Secondary: Accuracy ≥70% on high-confidence subset (validates labeling strategy)
- Statistical: Performance exceeds majority baseline by ≥10%

**Failure Response:**
- IF 70-74% accuracy: PIVOT to moderate success interpretation (simple provides baseline, complex offers incremental gains)
- IF <70% accuracy: EXPLORE non-linear methods, analyze feature interactions, investigate distributional assumptions

**Gate:**
- Type: MUST_WORK
- If Fail: Linear separability hypothesis rejected, pivot to analyzing why non-linear methods necessary

**Prerequisites:** None (foundation hypothesis)

**Source:** Phase 2A Section 1.6 (Primary Prediction), Section 5 (SH1 Existence)

---

#### H-M1: Linear Separability Mechanism

**Type:** MECHANISM
**Statement:** Under log-scaled feature transformation, if repository maintenance patterns (recent activity, community engagement, development velocity) are present, then they form linearly separable clusters in feature space, because maintained repositories exhibit consistently higher activity metrics and lower staleness that align with a linear decision boundary.

**Rationale:** This hypothesis tests the underlying mechanism that enables H-E1. Validates whether linear combination of features suffices or whether complex feature interactions require non-linear methods. Critical for understanding when to use LR vs GB.

**Variables:**
- IV: Linear decision boundary (Logistic Regression coefficients on log-scaled features)
- DV: Classification performance metrics (accuracy, F1, coefficient interpretability)
- CV: Same dataset and normalization as H-E1, controlled comparison with Gradient Boosting

**Verification Protocol:**
1. Train LR model per H-E1 protocol and extract learned coefficients
2. Analyze coefficient signs and magnitudes: expect negative for days_since_last_commit, positive for activity metrics (stars, forks, commits, contributors)
3. Visualize decision boundary in 2D PCA space to assess linear vs non-linear separation patterns
4. Train Gradient Boosting baseline (XGBoost: n_estimators=50, max_depth=6) on identical dataset
5. Compare LR vs GB performance gap: if gap ≤5%, linear mechanism sufficient; if gap >10%, complex interactions present
6. Calculate feature importance and correlation with maintenance status to validate causal pathway

**Success Criteria:**
- Primary: LR coefficients show expected signs (negative days_since_last_commit, positive activity) AND accuracy ≥75%
- Secondary: LR performance within 5% of Gradient Boosting (validates linear sufficiency)
- Mechanistic: Feature importance aligns with causal pathway (recent activity + engagement predict maintenance)

**Failure Response:**
- IF coefficients incorrect signs: EXPLORE feature engineering issues, check for multicollinearity, investigate label noise
- IF GB >> LR (>10% gap): PIVOT to analyzing feature interactions, consider polynomial features or interaction terms

**Gate:**
- Type: MUST_WORK
- If Fail: Linear mechanism rejected, investigate non-linear patterns, report complexity requirements

**Prerequisites:** H-E1 (must establish baseline accuracy before analyzing mechanism)

**Source:** Phase 2A Section 1.3 (Causal Mechanism - linear_classification), Section 5 (SH2 Mechanism)

---

<!--
Each hypothesis follows this format:

#### {H-ID}: {Title}

**Type:** {EXISTENCE|MECHANISM|CONDITION|COMPARISON}
**Statement:** {Full Under-If-Then-Because statement}

**Variables:**
- IV: {independent variable}
- DV: {dependent variable}
- CV: {controlled variables}

**Success Criteria:**
- {quantitative threshold 1}
- {quantitative threshold 2}

**Gate:**
- Type: {MUST_WORK|SHOULD_WORK|DETERMINES_SUCCESS}
- If Fail: {consequence}

**Prerequisites:** {list or "None"}

**Verification Protocol:** (100-150 words)
{step-by-step protocol}

---
-->

---

## 2.3 Risk Analysis

### Risk-Hypothesis Mapping

| Risk ID | Source | Description | Affected Hypotheses | Severity |
|---------|--------|-------------|---------------------|----------|
| R1 | A1 | Linear separability violation: Repository maintenance may require non-linear decision boundaries | H-E1, H-M1 | High |
| R2 | A2 | Timestamp proxy noise: last_commit <180 days may misclassify stable-but-inactive repos as abandoned | H-E1 | Medium |
| R3 | A3 | Feature insufficiency: Basic metadata may miss critical maintenance signals without network analysis | H-E1, H-M1 | Medium |
| R4 | A4 | Temporal drift: Distribution shifts between 2020-2022 train and 2023-2024 test periods | H-E1, H-M1 | High |
| R5 | A5 | Class imbalance: Actual distribution may differ from assumed ~60% majority baseline | H-E1 | Low |

### Mitigation Strategies

**Risk R1: Non-Linear Separability**
- **Source Assumption:** A1 - Linear separability in log-scaled feature space
- **Description:** If repository maintenance patterns exhibit non-linear interactions (e.g., stars×commits synergy), LR will underperform, requiring complex methods
- **Affected Hypotheses:** H-E1 (accuracy), H-M1 (mechanism validation)
- **Severity:** High (undermines core linear hypothesis)
- **Mitigation Strategy:**
  1. **Prevention:** Validate linear assumption via PCA visualization, check feature correlation matrix for multicollinearity
  2. **Detection:** Compare LR vs GB performance gap: if GB >10% better, non-linearity present
  3. **Response:**
     - PIVOT: Test polynomial features (degree=2) to capture interactions while maintaining interpretability
     - SCOPE: Reframe as "when does linear suffice vs when is non-linear needed" analysis
     - ABORT: If LR <60% (below trivial baseline), abandon linear approach
- **Early Warning Indicators:**
  - LR coefficients unstable or unexpected signs
  - PCA reveals non-convex clusters
  - Training accuracy significantly higher than test (overfitting to linear boundary)

**Risk R2: Label Noise from Timestamp Proxy**
- **Source Assumption:** A2 - last_commit <180 days is valid proxy for maintained status
- **Description:** Stable projects with infrequent updates may be misclassified as abandoned; archived projects with recent activity misclassified as maintained
- **Affected Hypotheses:** H-E1 (accuracy measurement)
- **Severity:** Medium (affects accuracy but can be validated)
- **Mitigation Strategy:**
  1. **Prevention:** Create high-confidence subset (last_commit <90 days & recent activity OR archived flag OR keywords like "deprecated")
  2. **Detection:** Compare accuracy on full dataset vs high-confidence subset; significant gap indicates label noise
  3. **Response:**
     - PIVOT: Use high-confidence labels for primary evaluation, full dataset as secondary
     - SCOPE: Report accuracy range (high-conf to full dataset) to bound uncertainty
     - ABORT: If high-conf accuracy <65%, labeling strategy fundamentally flawed
- **Early Warning Indicators:**
  - Manual inspection reveals obvious misclassifications
  - High-confidence subset accuracy 10%+ better than full dataset
  - High false positive rate on archived repositories

**Risk R3: Basic Features Insufficient**
- **Source Assumption:** A3 - GitHub metadata alone captures maintenance signal without network analysis
- **Description:** CSI aggregation may require network centrality (HITS) or richer features that basic metadata misses
- **Affected Hypotheses:** H-E1 (accuracy), H-M1 (feature sufficiency)
- **Severity:** Medium (CSI baseline provides comparison point)
- **Mitigation Strategy:**
  1. **Prevention:** Replicate CSI baseline to validate basic features work for aggregation approach
  2. **Detection:** If LR significantly underperforms CSI (>5% gap), basic features insufficient for classification
  3. **Response:**
     - PIVOT: Engineer derived features (issue_resolution_rate, commit_frequency_median), test feature ablation
     - SCOPE: Accept moderate accuracy (70-74%) as "simple baseline" contribution
     - ABORT: If LR <65% while CSI >75%, basic features fundamentally inadequate
- **Early Warning Indicators:**
  - Feature importance shows days_since_last_commit dominates (other features uninformative)
  - CSI baseline significantly outperforms LR
  - Adding derived features provides no improvement

**Risk R4: Temporal Distribution Shift**
- **Source Assumption:** A4 - Models trained on 2020-2022 generalize to 2023-2024
- **Description:** COVID-19 effects (2020-2021) or AI adoption surge (2023-2024) may cause distribution shifts that break temporal generalization
- **Affected Hypotheses:** H-E1 (temporal prediction), H-M1 (mechanism stability)
- **Severity:** High (temporal validity is key contribution claim)
- **Mitigation Strategy:**
  1. **Prevention:** Run KS test on feature distributions (2020-2022 vs 2023-2024), check for significant shifts (p<0.05)
  2. **Detection:** Compare IID accuracy vs temporal accuracy: large drop (>10%) indicates shift
  3. **Response:**
     - PIVOT: Report IID and temporal results separately, analyze shift causes (feature drift, label drift)
     - SCOPE: Accept temporal degradation if LR maintains ≥70% (still validates method on recent data)
     - ABORT: If temporal accuracy <60%, distribution shift too severe for generalization claims
- **Early Warning Indicators:**
  - KS test shows significant shifts in core features (stars, commits)
  - Temporal test set has very different class distribution
  - GB also shows large temporal degradation (systematic shift, not just LR problem)

**Risk R5: Class Imbalance Differs from Expected**
- **Source Assumption:** A5 - Majority baseline ~60% (more maintained than abandoned)
- **Description:** Actual dataset class distribution may be 50/50 or heavily skewed (80/20), affecting baseline comparison
- **Affected Hypotheses:** H-E1 (baseline comparison)
- **Severity:** Low (easily verifiable, does not affect method validity)
- **Mitigation Strategy:**
  1. **Prevention:** Report actual class distribution during data loading
  2. **Detection:** Check majority baseline accuracy matches expected ~60%; if not, recalibrate expectations
  3. **Response:**
     - PIVOT: Adjust baseline comparison to actual majority class performance
     - SCOPE: Use F1 score (balances precision/recall) as primary metric if severe imbalance
     - ABORT: N/A (reporting issue, not validation failure)
- **Early Warning Indicators:**
  - Majority baseline accuracy significantly different from 60% (e.g., 50% or 75%)
  - Severe class imbalance (>80/20) detected during stratified split

### Risk Summary Table

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Non-linear separability | A1 | High | H-E1, H-M1 | GB comparison, polynomial features, PCA visualization |
| R2 | Label noise (timestamp proxy) | A2 | Medium | H-E1 | High-confidence subset validation |
| R3 | Feature insufficiency | A3 | Medium | H-E1, H-M1 | CSI baseline, derived features, ablation |
| R4 | Temporal distribution shift | A4 | High | H-E1, H-M1 | KS test, separate IID/temporal reporting |
| R5 | Class imbalance mismatch | A5 | Low | H-E1 | Report actual distribution, use F1 score |

**Critical Risks:** 0
**High Risks:** 2 (R1, R4)
**Medium Risks:** 2 (R2, R3)
**Low Risks:** 1 (R5)

---

## 3. Execution

### 3.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
        DEPENDENCY GRAPH (DAG) - 2 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    H-E1 (Existence)
    │  Type: MUST_WORK gate
    │  Test: LR achieves ≥75% accuracy threshold
    │  Risk: R1 (non-linear), R2 (label noise), R4 (temporal)
    │
    └──▼
[Level 1 - Mechanism Validation]
    H-M1 (Mechanism)
    │  Type: MUST_WORK gate
    │  Test: Linear separability mechanism validation
    │  Dependencies: H-E1 (must pass first)
    │  Risk: R1 (non-linear), R3 (feature insufficiency)
    │
    └──▼
[Terminal]
    Verification Complete
    → Phase 2C: Experiment Design

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 (sequential, 2 steps)
Parallelization: None (linear dependency chain)
Total Gates: 2 MUST_WORK gates
═══════════════════════════════════════════════════════════
```

### 3.1.1 Verification Phases

**Phase 1 - Foundation (H-E1)**
- **Hypothesis:** H-E1 (Existence)
- **Test:** Logistic Regression achieves ≥75% accuracy on held-out test set
- **Gate:** MUST_WORK
- **Duration:** 1-2 days (data collection + training + evaluation)
- **If Fail:** STOP → Reassess linear separability assumption, consider non-linear methods

**Phase 2 - Mechanism Validation (H-M1)**
- **Hypothesis:** H-M1 (Mechanism)
- **Test:** Linear separability mechanism via coefficient analysis + GB comparison
- **Dependencies:** H-E1 must pass
- **Gate:** MUST_WORK
- **Duration:** 1 day (coefficient analysis + GB baseline + comparison)
- **If Fail:** PIVOT → Analyze feature interactions, test polynomial features

**Total Verification Duration:** 2-3 days

### 3.2 Verification Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════
        VERIFICATION TIMELINE - 2 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis     │ Day 1-2 │ Day 3  │
─────────────────────┼─────────┼────────┤
PHASE 1: Foundation
  H-E1               │ ███████ │        │
  Data Collection    │ ██      │        │
  Feature Engineer   │   ██    │        │
  Training/Eval      │     ███ │        │
  [Gate 1]           │         │ ◆      │
─────────────────────┼─────────┼────────┤
PHASE 2: Mechanism
  H-M1               │         │ ██████ │
  Coefficient Anal   │         │ ██     │
  GB Baseline        │         │   ███  │
  Comparison         │         │      █ │
  [Gate 2]           │         │      ◆ │
─────────────────────┼─────────┼────────┤
═══════════════════════════════════════════════════════════════════
Legend: ███ = Active work | ◆ = Gate decision point
Total Duration: 3 days (H-E1: 2 days, H-M1: 1 day)
Critical Path: H-E1 → H-M1 (no parallelization, sequential gates)
═══════════════════════════════════════════════════════════════════
```

### 3.3 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 (2-step sequential chain)

**Total Duration:** 3 days
- Phase 1 (H-E1 Foundation): 2 days
  - Day 1: Data collection (GitHub API extraction, 2000 repos)
  - Day 2: Feature engineering + LR training + evaluation
- Phase 2 (H-M1 Mechanism): 1 day
  - Coefficient analysis + GB baseline + comparison

**Slack Available:** 0 days (all hypotheses sequential, no parallelization)

**Gate Decision Points:**
- Gate 1 (Day 2): H-E1 must achieve ≥75% accuracy to proceed
- Gate 2 (Day 3): H-M1 must validate linear separability mechanism

### 3.4 Resource Summary

**Compute Requirements:**
- LR Training: 30 seconds on single CPU (trivial)
- GB Training: 10 minutes on multi-core (baseline comparison)
- Total Compute: <15 minutes training time

**Data Requirements:**
- 2000 repositories from Papers with Code API + GitHub REST API
- 8 features per repository (basic metadata + 2 derived)
- Estimated storage: <10 MB (metadata only, no code/issues text)

**MCP Services Used:**
- None required for Phase 4 execution (data collection via standard APIs)
- Archon MCP: Used for risk identification in Phase 2B planning only

**Personnel:**
- Single researcher (all tasks executable by one person)
- No parallel work (sequential hypothesis chain)

### 3.5 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Accuracy ≥75% AND F1 ≥0.73 | STOP → Reassess linear separability, consider non-linear methods |
| H-M1 | MUST_WORK | Coefficients correct signs AND LR within 5% of GB | PIVOT → Analyze feature interactions, test polynomial features |

**Both gates are blocking:** Failure at any gate triggers hypothesis revision via Phase 2A reflection.

---

## 4. Dialectical Analysis

### 4.1 Thesis Statement

**Core Claim:** Logistic Regression trained on basic GitHub metadata achieves ≥75% accuracy for repository maintenance classification, demonstrating that simple linear methods suffice for moderate-accuracy prediction without complex ensemble or network analysis.

**Supporting Evidence:**
1. **Causal Mechanism:** Maintained repositories exhibit higher recent activity (low days_since_last_commit), higher community engagement (stars, forks, contributors), and higher development velocity (commit_frequency) that are linearly separable in log-scaled feature space
2. **Established Baselines:** Composite Stability Index (aggregation) achieves F1 0.80 with similar features (Adejumo & Johnson 2025), suggesting basic metadata captures maintenance signal
3. **Testable Predictions:** Three quantitative predictions with pass/fail thresholds (≥75% absolute, ≥10% vs majority, ≥70% temporal)

**Strengths:**
- Clear causal pathway with established evidence (He et al. 2024, Adejumo & Johnson 2025)
- Falsifiable with explicit thresholds (accuracy <70% = rejection)
- Adaptive outcome framework (all results yield scientific findings)
- Minimal compute requirements (30s training) enables rapid iteration

**Expected Outcomes:**
- Primary: LR accuracy ≥75% AND F1 ≥0.73 on held-out test set
- Secondary: LR exceeds majority baseline by ≥10%, matches CSI within 3%
- Tertiary: LR maintains ≥70% accuracy on temporal 2023-2024 test set

### 4.2 Antithesis Development

**Null Hypothesis (H0):** Logistic Regression achieves <70% accuracy, confirming non-linear methods necessary

**Counter-Arguments:**
1. **Baseline Limitations:** He et al. 2024 achieved C-Index 0.810 with Gradient Boosting + HITS centrality, suggesting complex methods superior. No prior work tested simple LR baseline, so gap magnitude unknown.
2. **Assumption Violations:**
   - A1 (Linear Separability): Repository patterns may exhibit non-linear interactions (e.g., stars×commits synergy effects) that linear decision boundaries cannot capture
   - A2 (Timestamp Proxy): Label noise from conflating stable-but-inactive with truly abandoned repositories degrades signal quality
   - A4 (Temporal Stationarity): COVID-19 (2020-2021) and AI adoption surge (2023-2024) may cause distribution shifts breaking generalization
3. **Scope Limitations:** Benchmark repositories (Papers with Code) may be atypical with higher maintenance rates than general OSS, limiting generalization

**Potential Failure Points:**
- R1 (Non-linear separability): LR <70% while GB >80% indicates complex feature interactions
- R2 (Label noise): High-confidence subset shows 10%+ accuracy gap, indicating timestamp proxy unreliable
- R4 (Temporal drift): KS test shows significant shifts (p<0.05), temporal accuracy drops >15%

**Conditions Under Which H0 Would Be Supported:**
- If LR accuracy <70% on IID split → linear separability assumption rejected
- If GB outperforms LR by >10% → non-linear methods necessary
- If temporal accuracy <65% → temporal generalization fails
- If A1-A4 assumptions systematically violated → basic features insufficient

### 4.3 Synthesis

**Balanced Assessment:**

The hypothesis h-lr1 presents a testable claim that simple linear classification suffices for moderate-accuracy (≥75%) repository maintenance prediction using basic GitHub metadata. The thesis is supported by established evidence that metadata correlates with maintenance (He et al. 2024, Adejumo & Johnson 2025, Li et al. 2026) and that aggregation methods (CSI) achieve F1 0.80 with similar features. However, the null hypothesis raises valid concerns: no prior work has tested simple LR baseline, so the complexity gap magnitude is unknown; label noise from timestamp proxy may degrade accuracy; and temporal distribution shifts may break generalization.

**Resolution Path:**

The verification plan addresses this dialectic through a 2-hypothesis sequential chain with MUST_WORK gates:

1. **Foundation Verification (H-E1):** Tests absolute accuracy threshold (≥75%) and baseline comparison (≥10% vs majority, within 3% of CSI) to establish whether linear methods achieve moderate accuracy before analyzing mechanism
2. **Mechanism Validation (H-M1):** Analyzes learned coefficients, visualizes decision boundary, and compares LR vs GB to validate linear separability assumption and quantify complexity gap
3. **Gate Conditions:** Allow early detection of H0 support (H-E1 <70% → stop, reassess) and adaptive outcomes (70-74% = moderate success, <70% = non-linear necessary)

**Conditions for Thesis Support:**
- Both MUST_WORK gates pass (H-E1 ≥75%, H-M1 coefficients correct)
- Primary prediction confirmed: LR ≥75% accuracy AND F1 ≥0.73
- Mechanism validates: LR within 5% of GB (linear sufficient)

**Conditions for Antithesis Support:**
- H-E1 fails: LR <70% accuracy on IID split → linear separability rejected
- H-M1 fails: GB >> LR (>10% gap) → non-linear interactions present
- Temporal fails: LR <65% on 2023-2024 test → generalization broken

**Nuanced Outcome Possibilities:**

1. **Full Thesis Support (Strong Success):** H-E1 ≥75%, H-M1 validates, temporal ≥70% → Simple methods suffice, complex unnecessary. Impact: "Linear baseline establishes simplicity threshold."

2. **Partial Thesis Support (Moderate Success):** H-E1 70-74%, H-M1 partial → Simple provides moderate baseline, complex offers incremental gains. Impact: "Quantifies complexity-accuracy trade-off: +5% accuracy costs 20× compute (10min GB vs 30s LR)."

3. **Antithesis Support (Hypothesis Rejection):** H-E1 <70% or H-M1 fails → Non-linear methods necessary. Impact: "Analyzes why: feature interactions (polynomial terms help?), label noise (high-conf subset better?), or distributional assumptions violated."

**All outcomes yield scientific findings:** Success validates simple methods, rejection quantifies complexity requirements, partial support establishes trade-off curve.

### 4.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| **Existence** | LR achieves ≥75% accuracy | May be <70%, confirming non-linear necessary | H-E1 test with 3 thresholds (75% pass, 70-74% moderate, <70% fail) |
| **Mechanism** | Linear separability in log-space | Complex feature interactions require GB | H-M1 coefficient analysis + LR vs GB comparison (≤5% gap = linear sufficient) |
| **Temporal Validity** | 2020-2022 train generalizes to 2023-2024 | Distribution shifts break generalization | KS test + separate IID/temporal reporting, accept ≥70% temporal as success |
| **Feature Sufficiency** | Basic metadata captures signal | Network centrality (HITS) or richer features needed | CSI baseline comparison (within 3% = features sufficient) |

**Overall Robustness Score:** Medium-High
- **Strengths:** Explicit thresholds, adaptive outcomes, established baseline comparisons, rapid iteration
- **Weaknesses:** Untested hypothesis (no prior LR baseline work), label noise risk, temporal drift risk
- **Confidence Calibration:** 75% confidence reflects uncertainty in linear separability assumption (A1) and temporal stationarity (A4)

**Confidence in Verification Plan:** 0.75
- High confidence in feasibility (data accessible, compute trivial, 3-day duration)
- Medium confidence in thesis support (linear separability unproven, temporal shifts possible)
- High confidence in scientific value (all outcomes interpretable and publishable)

---

## 5. Executive Summary & Recommendations

### 5.1 Executive Summary

**Main Hypothesis:** Logistic Regression trained on basic GitHub metadata (stars, forks, commits, contributors, last_commit_date, derived features) achieves ≥75% binary classification accuracy for repository maintenance status.
- ID: h-lr1, Confidence: 0.75
- Research Question: Can simple classification methods predict benchmark maintenance with ≥75% accuracy?

**Verification Structure:**
- Mode: Incremental (Phase 2A pre-mapping applied)
- Sub-Hypotheses: 2 total
  - H-E1: LR achieves ≥75% accuracy threshold (Existence)
  - H-M1: Linear separability mechanism validation (Mechanism)
- Phases: 2 phases over 3 days
- Critical Gates: 2 MUST_WORK decision points
- Critical Path: H-E1 → H-M1 (sequential, no parallelization)

**Risk Assessment:** Medium-High
- High Risks: R1 (non-linear separability), R4 (temporal distribution shifts)
- Medium Risks: R2 (label noise), R3 (feature insufficiency)
- All risks have mitigation strategies and early warning indicators

**Immediate Action:** Begin Phase 1 with H-E1 foundation verification (data collection + LR training, 2 days)

### 5.2 Key Achievements

**Verification Plan Deliverables:**
- 2 hypotheses with complete specifications (40-50 lines each)
- 5 identified risks with mitigation strategies
- 3-day execution timeline with 2 gate decision points
- Dialectical analysis with thesis-antithesis-synthesis framework
- Adaptive outcome framework (all results yield scientific findings)

**H0 Addressed:** Null hypothesis (LR <70% accuracy) integrated as antithesis with explicit conditions for support

**Scope Reduction:** 0% (no established facts to exclude from Phase 2A)

### 5.3 Verification Execution Order

**Phase 1: Foundation (2 days)**
- H-E1: Logistic Regression achieves ≥75% accuracy on held-out test set
- Test Protocol: 2000 repos, 8 features, stratified 80/20 split, sklearn LR with balanced weights
- Gate 1: MUST PASS (accuracy ≥75% AND F1 ≥0.73)
- If Fail: STOP → Reassess linear separability assumption

**Phase 2: Mechanism Validation (1 day)**
- H-M1: Linear separability mechanism via coefficient analysis + GB comparison
- Test Protocol: Extract coefficients, visualize decision boundary (PCA), compare LR vs GB
- Gate 2: MUST PASS (coefficients correct signs AND LR within 5% of GB)
- If Fail: PIVOT → Analyze feature interactions, test polynomial features

**Total Duration:** 3 days (H-E1: 2 days, H-M1: 1 day)

### 5.4 Critical Decision Points

**Gate 1 (End of Day 2): H-E1 Foundation**
- **PASS (≥75%):** Proceed to H-M1 mechanism validation
- **MODERATE (70-74%):** Pivot to "moderate success" interpretation, continue to H-M1
- **FAIL (<70%):** STOP → Execute failure response
  - Analyze why: PCA visualization, feature correlation, label noise check
  - Pivot options: Polynomial features (degree=2), high-confidence labels only, non-linear methods

**Gate 2 (End of Day 3): H-M1 Mechanism**
- **PASS:** Linear separability validated, simple methods suffice
- **FAIL:** Non-linear interactions present, analyze complexity requirements
  - Analyze why: GB feature importance, interaction effects, distributional assumptions
  - Pivot options: Test interaction terms, report complexity-accuracy trade-off

### 5.5 Open Questions

**From Phase 2A:**
1. **Linear Separability:** Will log-scaled features form linearly separable clusters, or do complex interactions require non-linear boundaries?
2. **Temporal Generalization:** Do models trained on 2020-2022 maintain ≥70% accuracy on 2023-2024, or do distribution shifts break generalization?
3. **Feature Sufficiency:** Do basic GitHub metadata features capture maintenance signal without network centrality (HITS) or richer features?

**Resolution:** All questions answered by H-E1 (thresholds) + H-M1 (mechanism) tests with adaptive outcomes.

### 5.6 Recommendations

**Immediate Actions (Day 1):**
1. Extract 2000 Papers with Code benchmark repositories via GitHub REST API (2020-2024, min_stars=32)
2. Engineer 8 features with log1p transforms and derive commit_frequency_median_weekly, issue_resolution_rate
3. Create binary labels from days_since_last_commit < 180, perform stratified 80/20 split
4. Set up validation infrastructure: high-confidence subset, KS test for distribution shifts

**Resource Allocation:**
- Single researcher (all tasks executable by one person)
- Compute: Single CPU sufficient (<30s LR training, <10min GB baseline)
- Data Storage: <10 MB (metadata only, no code/issues text)
- No MCP services required for Phase 4 execution

**Risk Mitigation Priorities:**
1. **R1 (Non-linear):** Run PCA visualization early (Day 1) to assess cluster structure
2. **R4 (Temporal):** Run KS test on train vs test features (Day 1) to detect shifts
3. **R2 (Label noise):** Create high-confidence subset during data loading (Day 1)

**Next Steps:**
- Phase 2C: Experiment Design (generate detailed implementation specifications)
- Phase 3: Implementation Planning (PRD, Architecture, PRP, Archon tasks)
- Phase 4: Coding & Validation (implement + validate hypotheses)

---
