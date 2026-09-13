# Verification Plan: Meta-Method Selector for Supervised Learning Benchmarks

**Date:** 2026-07-13
**Hypothesis ID:** H-MetaMethodSelector-v1
**Confidence:** 0.7 (70%)
**Total Hypotheses:** 6 (H-E1, H-M1-4, H-C1)

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under supervised learning settings with existing benchmark datasets, if a meta-classifier is trained on aggregated benchmark results (50-60 datasets) using fast-to-compute dataset features (sample size, dimensionality, class imbalance, signal statistics), then it will predict method families (Linear/Polynomial/RNN/Augmentation) that achieve top-30% ranking performance on held-out datasets with >50% success rate, because systematic performance patterns correlate dataset characteristics with method strengths.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in top-30% ranking accuracy between meta-classifier predictions and random method selection (≤35% vs. 30% random baseline, p > 0.05).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Aggregated Benchmark Collection (standard) | Collection spans vision/time-series/tabular domains with documented baseline comparisons, providing diverse training examples for meta-learning |
| **Model** | Random Forest Meta-Classifier | Interpretable (feature importance via SHAP), handles nonlinear feature relationships, robust to small sample sizes, proven for tabular data |

**Dataset Details:**
- Source: Literature mining: OGB (15 graph datasets), FedML (6), LEAF (5), pFL-Bench (8), Champneys NLSI (5), Zhou medical FL (9), Papers with Code leaderboards (10+)
- Path: To be collected from public repositories and published papers

**Model Details:**
- Type: Ensemble tree-based classifier
- Source: scikit-learn RandomForestClassifier(n_estimators=100, max_depth=10)

### 1.4 Baseline Methods (for comparison)

| Method | Performance | Description |
|--------|-------------|-------------|
| Random Selection | 30% top-30% accuracy (expected) | Uniformly sample method family from {Linear, Polynomial, RNN, Augmentation} |
| Domain Folklore | 40-50% accuracy (expected) | Predict based on domain only (vision→CNN, time-series→RNN) |
| Majority Class | 30-40% accuracy (expected) | Always predict most frequent winner in training set (degeneracy check) |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Published benchmark results aggregate enough datapoints (≥50) to learn robust relationships | Exchange 7 mining plan: OGB+FedML+LEAF+pFL-Bench+Champneys+Zhou = 48-60 total | If <30 benchmarks collectible, meta-classifier overfits (Exchange 6: 14 samples insufficient per Prof. Rex) |
| A2 | Fast features (Tier 1+2) capture sufficient dataset characteristics to differentiate method performance | Exchange 3 (Prof. Pax): sample size, variance, dimensionality trivial to compute. Exchange 7: Tier 2 adds autocorrelation/edge density for domain-specific patterns | If Tier 1+2 features achieve <40% accuracy (no better than domain folklore baseline), need expensive Tier 3 probing that violates feasibility |
| A3 | Method families exhibit consistent behavior across similar datasets (generalization) | Champneys: RNN family wins 3/5 benchmarks, Zhou: DDPM+LS wins 7/9. Not random variation | If method rankings are chaotic (no feature correlation), meta-learning is impossible |
| A4 | Cross-validation on published benchmarks approximates zero-shot generalization to new datasets | Exchange 5 (Dr. Sage): temporal generalization test - train on pre-2024, test on 2024+ benchmarks | If CV accuracy high but new-benchmark accuracy low, meta-classifier learned benchmark-specific artifacts not generalizable features |
| A5 | Top-30% ranking threshold represents useful guidance for practitioners | Exchange 5: 'Top-30% is useful starting point vs. top-1% unrealistic perfection or >70% avoid catastrophic failure' | If practitioners demand >90% accuracy to trust predictions (measured via user survey), adoption unlikely |

### 1.6 Research Gap & Novelty

**Key Innovation:** Predictive model using fast-to-compute dataset fingerprints (vs. manual domain expertise or exhaustive trial-and-error). Tiered feature approach balances feasibility (Tier 1 universal, 1 sec) with predictive power (Tier 2 domain-specific, 5-15 sec).

**Gap Addressed:** First work to frame dataset-to-method selection as a trainable meta-learning problem, transforming descriptive observations (Zhou 2025: "rankings vary", Champneys 2024: "winners differ") into actionable guidance.

**Differentiation from Prior Work:**
- Afkanpour et al. 2024 systematic review: Qualitative guidance only ('consider data structure'), no predictive model
- Liao et al. 2025 heterogeneity challenges: Descriptive problem statement, no decision framework
- Zhou et al. 2025 FL benchmark: Reports method rankings on 9 datasets but provides no predictor for NEW datasets
- Champneys et al. 2024 NLSI baselines: Establishes baseline comparisons but no meta-analysis of what dataset features predict winners

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | todo |
| H-M1 | MECHANISM | SHOULD_WORK | H-E1 | todo |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | todo |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | todo |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | todo |
| H-C1 | CONDITION | OPTIONAL | H-M4 | todo |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Benchmark Collection Sufficiency**

**Statement**: Under supervised learning literature mining from target benchmark suites (OGB, FedML, LEAF, pFL-Bench, Champneys, Zhou), if we systematically extract method rankings from published papers, then at least 50 benchmarks with complete baseline comparisons will be collected, because these suites collectively provide diverse coverage across vision, time-series, tabular, and graph domains.

**Rationale**: Validates Phase 2A Assumption A1 (≥50 benchmarks needed for robust meta-learning). Without sufficient training data, meta-classifier overfits and predictions fail to generalize.

**Variables**:
- Independent: Target benchmark suites (OGB, FedML, LEAF, pFL-Bench, Champneys NLSI, Zhou medical FL)
- Dependent: Count of successfully collected benchmarks with method rankings
- Controlled: Minimum 3 methods compared per benchmark, domain diversity (≥3 domains)

**Verification Protocol**:
1. Search each target suite systematically and extract dataset metadata, method rankings, and domain labels
2. Filter benchmarks: require ≥3 method comparisons and complete ranking data
3. Count total collected benchmarks and measure domain distribution
4. Statistical check: ≥50 total AND ≥10 per domain

**Success Criteria** (MUST_WORK gate):
- Primary: ≥50 benchmarks collected with complete rankings
- Secondary: Domain diversity ≥3 domains with ≥10 benchmarks each

**Failure Response**: IF 40-49: EXPLORE additional sources; IF <40: ABANDON (A1 violated)

**Dependencies**: None (foundation)

**Source**: Phase 2A SH1, Section 1.4 (A1)

---

**H-M1: Dataset Features Determine Structural Advantages**

**Statement**: Dataset characteristics (sample size, dimensionality, signal properties) determine which method families have structural advantages.

**Rationale**: Tests causal step 1 of 4. Zhou: small datasets benefit from augmentation (+17pp), Champneys: structured problems favor polynomial bases.

**Variables**:
- Independent: Dataset features (sample size, dimensionality, class imbalance, signal statistics)
- Dependent: Method family structural advantage indicators (correlation with rankings)
- Controlled: Tier 1+2 feature computation (<1 min), domain diversity

**Verification Protocol**:
1. Compute Tier 1+2 features for all collected benchmarks
2. Measure correlation between features and method rankings (Spearman ρ)
3. Test: features show significant correlation (p < 0.05) with method performance

**Success Criteria** (SHOULD_WORK gate):
- Primary: Feature-ranking correlation ρ > 0.3, p < 0.05
- Secondary: No features show inverse correlation

**Failure Response**: EXPLORE Tier 3 features or PIVOT to simpler model

**Dependencies**: H-E1

**Falsifier**: If features show zero correlation (ρ ≈ 0, p > 0.1)

**Source**: Phase 2A Causal Step 1

---

**H-M2: Aggregated Benchmarks Provide Sufficient Training Examples**

**Statement**: Aggregated benchmark results from literature provide sufficient training examples (50-60 datasets) to learn feature-method relationships.

**Rationale**: Tests causal step 2 of 4. OGB+FedML+LEAF+pFL-Bench+Champneys+Zhou = 48-60 total benchmarks.

**Variables**:
- Independent: Training set size (50-55 benchmarks in leave-5-out CV)
- Dependent: Meta-classifier cross-validation accuracy
- Controlled: Leave-5-out CV protocol, stratification by domain

**Verification Protocol**:
1. Run 10 rounds of leave-5-out CV on collected benchmarks
2. Train Random Forest on 50-55, test on 5 held-out
3. Measure accuracy: predicted method's actual ranking percentile

**Success Criteria** (SHOULD_WORK gate):
- Primary: CV accuracy >45% (better than 40% domain folklore baseline)
- Secondary: Accuracy stable across CV rounds (std < 10%)

**Failure Response**: PIVOT to collect more benchmarks or reduce method granularity

**Dependencies**: H-M1

**Falsifier**: If <30 benchmarks collectible or lack diversity

**Source**: Phase 2A Causal Step 2

---

**H-M3: Random Forest Extracts Generalizable Patterns**

**Statement**: Random Forest meta-classifier trained on features extracts generalizable patterns (not domain folklore).

**Rationale**: Tests causal step 3 of 4. Ablation: removing domain labels reduces accuracy <5%, proving features are predictive independent of domain.

**Variables**:
- Independent: Feature set (WITH vs WITHOUT domain labels)
- Dependent: Ablation accuracy drop
- Controlled: Random Forest hyperparameters (n=100, max_depth=10)

**Verification Protocol**:
1. Train meta-classifier WITH domain one-hot encoding
2. Train meta-classifier WITHOUT domain labels
3. Compare CV accuracies, compute SHAP feature importance

**Success Criteria** (SHOULD_WORK gate):
- Primary: Accuracy drop <5% without domain labels
- Secondary: SHAP domain importance <0.2

**Failure Response**: PIVOT to feature engineering or reject hypothesis

**Dependencies**: H-M2

**Falsifier**: If accuracy drops >20% without domain OR domain SHAP >0.5

**Source**: Phase 2A Causal Step 3

---

**H-M4: Predictions Achieve Competitive Performance**

**Statement**: Predicted method family achieves competitive performance (top-30%) on new datasets without exhaustive search.

**Rationale**: Tests causal step 4 of 4. Practitioner value: informed starting point reduces wasted compute vs trying everything.

**Variables**:
- Independent: Meta-classifier predictions (method family)
- Dependent: Predicted method's ranking percentile on held-out benchmarks
- Controlled: Leave-5-out CV, top-30% threshold

**Verification Protocol**:
1. For each held-out benchmark, predict method family via trained meta-classifier
2. Lookup predicted method's actual ranking percentile from literature
3. Compute success rate: fraction where ranking ≤30%
4. Statistical test: success rate vs 30% random baseline (Chi-square, p<0.05)

**Success Criteria** (SHOULD_WORK gate):
- Primary: Success rate ≥50% (significantly better than random)
- Secondary: p < 0.05 vs random baseline

**Failure Response**: PIVOT to different prediction threshold or ABANDON

**Dependencies**: H-M3

**Falsifier**: If predicted methods rank >70th percentile on majority of held-out datasets

**Source**: Phase 2A Causal Step 4

---

**H-C1: Sample Size and Computation Time Boundary Conditions**

**Statement**: Under supervised learning settings, if benchmark sample size n ∈ [100, 100K] AND feature computation completes in <1 min, then meta-classifier predictions achieve ≥50% top-30% success rate, because these boundaries define the feasibility scope. Outside this range, mechanism may fail.

**Rationale**: Validates scope boundaries from Phase 2A Section 1.5. Tests whether mechanism degrades at boundaries.

**Variables**:
- Independent: Sample size range (n<100, n∈[100,100K], n>100K), feature computation time
- Dependent: Meta-classifier success rate within each stratum
- Controlled: Leave-5-out CV, Random Forest hyperparameters

**Verification Protocol**:
1. Stratify collected benchmarks by sample size: n<100, n∈[100,100K], n>100K
2. Measure feature computation time for each benchmark
3. Run leave-5-out CV within each stratum, compute success rate
4. Statistical test: compare success rates across strata (ANOVA)

**Success Criteria** (OPTIONAL gate):
- Primary: Success rate ≥50% for n∈[100,100K] AND <40% out-of-range
- Secondary: Feature computation <1 min for in-range

**Failure Response**: IF untestable: document limitation; IF works out-of-range: UPDATE scope

**Dependencies**: H-M4

**Source**: Phase 2A Section 1.5 (scope)

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

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-C1
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | ≥50 benchmarks collected | IF <40: ABANDON; IF 40-49: EXPLORE |
| H-M1 | SHOULD_WORK | Feature-ranking correlation ρ>0.3, p<0.05 | EXPLORE Tier 3 or PIVOT |
| H-M2 | SHOULD_WORK | CV accuracy >45% | PIVOT: collect more or reduce granularity |
| H-M3 | SHOULD_WORK | Accuracy drop <5% without domain | PIVOT or REJECT |
| H-M4 | SHOULD_WORK | Success rate ≥50%, p<0.05 | PIVOT threshold or ABANDON |
| H-C1 | OPTIONAL | In-range ≥50%, out-of-range <40% | Document or UPDATE scope |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Collection | H-E1 | 1-2 weeks |
| Phase 2: Feature Analysis | H-M1 | 3-5 days |
| Phase 3: Training | H-M2, H-M3 | 1 week |
| Phase 4: Evaluation | H-M4 | 3-5 days |
| Phase 5: Boundary Test | H-C1 | 2-3 days |

**Total Duration:** 4-5 weeks

---
