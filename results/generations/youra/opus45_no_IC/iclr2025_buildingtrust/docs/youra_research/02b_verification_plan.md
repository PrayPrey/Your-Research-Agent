# Verification Plan: Category-Specific Calibration for LLM Truthfulness

**Date:** 2026-08-10
**Hypothesis ID:** H-ClusterCal-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under evaluation on TruthfulQA benchmark with pre-registered semantic category clusters,
if LLM predictions are calibrated using cluster-specific temperature scaling,
then Expected Calibration Error will be significantly lower than global temperature scaling,
because semantic category membership captures systematic variation in model confidence behavior.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in ECE between cluster-specific temperature scaling
and global temperature scaling on TruthfulQA. Category membership does not provide
useful calibration information beyond a single global temperature.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TruthfulQA (standard) | 38 category labels enable cluster-level analysis; standard truthfulness benchmark |
| **Model** | Multiple open-weight LLMs | Open models with logit access; scale comparison for RQ4 |

**Dataset Details:**
- Source: https://github.com/sylinrl/TruthfulQA
- Path: TruthfulQA.csv

**Model Details:**
- Type: decoder-only transformers
- Source: HuggingFace Hub
- Variants: Llama-2-7B, Mistral-7B, Llama-2-13B

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Uncalibrated Softmax | Known overconfident | General |
| Global Temperature Scaling | Reduces ECE significantly | CIFAR, ImageNet; untested per-category on TruthfulQA |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | TruthfulQA categories are semantically meaningful and stable | Categories defined by domain experts in [Lin et al., 2022] | Cluster assignments would be arbitrary noise |
| A2 | LLM logits are accessible for calibration | HuggingFace transformers provide logit access for open models | Cannot apply temperature scaling; would need verbalized confidence |
| A3 | Category clusters have sufficient samples for reliable ECE estimation | ~100-150 questions per cluster with 7 clusters from 817 total | Bootstrap CIs would be too wide for significance |
| A4 | Temperature scaling is appropriate for LLM calibration | Prior work shows it helps neural networks; limited LLM evaluation exists | Null result could mean method, not hypothesis, is wrong |
| A5 | Cross-validation generalizes to unseen questions from same clusters | Standard ML evaluation assumption; questions within cluster are exchangeable | Train/test split would not reflect deployment generalization |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First systematic per-category calibration analysis on TruthfulQA

**Key Innovation:** Cluster-specific temperature scaling with pre-registered semantic groupings

**Differentiation:**
- Guo et al., 2017 — Temperature Scaling: Applied globally; we extend to per-cluster with regularization
- Lin et al., 2022 — TruthfulQA: Evaluated truthfulness, not calibration by category
- Xiong et al., 2023 — LLM Uncertainty: Compared confidence types globally, not per-category

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | pending |
| H-M1 | Mechanism | MUST_WORK | H-E1 | pending |
| H-M2 | Mechanism | MUST_WORK | H-M1 | pending |
| H-M3 | Mechanism | MUST_WORK | H-M2 | pending |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Category-Dependent Calibration Variation Exists**

**Statement**: Under evaluation on TruthfulQA with 7 pre-registered semantic clusters, if per-cluster ECE values are computed, then significant variation will exist across clusters, because LLMs exhibit category-specific confidence patterns from training.

**Rationale**: Establishes foundation for cluster-specific calibration. If ECE is homogeneous across categories, the entire mechanism fails. ANOVA test on cluster-level ECE validates the premise.

**Variables**:
- Independent: Semantic cluster (7 levels)
- Dependent: Expected Calibration Error (ECE, 15 bins)
- Controlled: Model architecture, evaluation protocol

**Verification Protocol**:
1. Run inference on TruthfulQA with Llama-2-7B, extract logits
2. Assign questions to 7 pre-registered clusters
3. Compute per-cluster ECE with bootstrap CI
4. Run ANOVA F-test on cluster ECE values
5. Report cluster-level ECE distribution

**Success Criteria** (PoC):
- Primary: ANOVA p < 0.05 (clusters differ)
- Secondary: At least 2 clusters differ by >0.05 ECE

**Failure Response**: IF fails → ABANDON (no category structure to exploit)

**Dependencies**: None (foundation)

**Source**: Phase 2A Section 5 - sh1_existence

---
**H-M1: LLMs Produce Category-Specific Confidence Distributions**

**Statement**: Under evaluation on TruthfulQA, if confidence histograms are computed per cluster, then distributions will differ significantly across clusters, because training data contains category-specific confidence rhetoric.

**Rationale**: First mechanism step. Category-specific calibration requires different underlying distributions. Kolmogorov-Smirnov test validates distribution differences.

**Variables**:
- Independent: Semantic cluster
- Dependent: Confidence distribution (histogram)
- Controlled: Model, binning strategy

**Verification Protocol**:
1. Extract softmax confidence for all TruthfulQA predictions
2. Group by cluster, compute confidence histograms
3. Run pairwise Kolmogorov-Smirnov tests
4. Visualize cluster-level confidence distributions
5. Report distribution statistics per cluster

**Success Criteria** (PoC):
- Primary: KS test p < 0.05 for majority of cluster pairs
- Secondary: Mean confidence differs by >0.1 across clusters

**Failure Response**: IF fails → PIVOT (try alternative clustering)

**Dependencies**: H-E1

**Source**: Phase 2A causal_mechanism.steps[0]

---
**H-M2: Different Distributions Require Different Temperature Parameters**

**Statement**: Under optimization of temperature scaling, if cluster-specific temperatures are learned, then optimal T values will differ across clusters, because different confidence-accuracy relationships require different scaling.

**Rationale**: Second mechanism step. If optimal temperatures are identical, no benefit from cluster-specific scaling. Mathematical consequence of M1.

**Variables**:
- Independent: Cluster (for T optimization)
- Dependent: Optimal temperature value
- Controlled: Loss function (NLL), regularization

**Verification Protocol**:
1. Split data 80/20 per cluster (5-fold CV)
2. Optimize T per cluster on training fold
3. Compare optimal T values across clusters
4. Test if T variance exceeds regularization noise
5. Report T distribution with confidence intervals

**Success Criteria** (PoC):
- Primary: Coefficient of variation of optimal T > 0.1
- Secondary: Range of T values spans >0.3

**Failure Response**: IF fails → EXPLORE (check regularization strength)

**Dependencies**: H-M1

**Source**: Phase 2A causal_mechanism.steps[1]

---
**H-M3: Cluster-Specific Temperatures Achieve Better Calibration**

**Statement**: Under 5-fold cross-validation on TruthfulQA, if cluster-specific temperatures are applied, then ECE will be lower than global temperature scaling, because per-cluster parameters capture calibration heterogeneity.

**Rationale**: Final mechanism step and primary prediction. Validates the practical benefit of cluster-specific calibration over global baseline.

**Variables**:
- Independent: Calibration method (global vs cluster-specific)
- Dependent: ECE (test fold)
- Controlled: CV protocol, random seed

**Verification Protocol**:
1. Train global T on combined training data
2. Train cluster-specific T with L2 regularization
3. Evaluate both on held-out fold
4. Compute ECE improvement and bootstrap CI
5. Run paired t-test across 5 folds

**Success Criteria** (PoC):
- Primary: ECE(cluster-T) < ECE(global-T), p < 0.05
- Secondary: Cohen's d > 0.3 (practical significance)

**Failure Response**: IF fails → ABANDON (hypothesis refuted)

**Dependencies**: H-M2

**Source**: Phase 2A causal_mechanism.steps[2], prediction P1

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | ANOVA p < 0.05 on cluster ECE | ABANDON all |
| H-M1 | MUST_WORK | KS test p < 0.05 majority pairs | PIVOT clustering |
| H-M2 | SHOULD_WORK | CV(optimal T) > 0.1 | EXPLORE regularization |
| H-M3 | MUST_WORK | Paired t-test p < 0.05, d > 0.3 | ABANDON hypothesis |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1 - Foundation | H-E1 | 1 day |
| Phase 2 - Mechanisms | H-M1, H-M2, H-M3 | 3 days |
| Phase 3 - Validation | Cross-model replication | 2 days |

**Total Duration:** 6 days (excluding Phase 5 baseline comparison)

---

## 4. Risk Analysis

### 4.1 Risk Identification

| Risk ID | Source | Risk Description | Severity | Likelihood |
|---------|--------|------------------|----------|------------|
| R1 | A1 | TruthfulQA categories are arbitrary/unstable | High | Low |
| R2 | A2 | Logit access unavailable for some models | Medium | Low |
| R3 | A3 | Insufficient samples per cluster for reliable ECE | High | Medium |
| R4 | A4 | Temperature scaling inappropriate for LLMs | High | Low |
| R5 | A5 | Cross-validation doesn't generalize to deployment | Medium | Low |

### 4.2 Risk-Hypothesis Mapping

| Risk | Affected Hypotheses | Impact |
|------|---------------------|--------|
| R1 | H-E1, H-M1 | Foundation failure — if categories meaningless, clustering invalid |
| R2 | H-M2, H-M3 | Cannot optimize temperatures without logits |
| R3 | H-E1, H-M1, H-M2, H-M3 | Wide bootstrap CIs prevent statistical significance |
| R4 | H-M2, H-M3 | Method failure vs hypothesis failure ambiguity |
| R5 | H-M3 | Results may not transfer to real-world use |

### 4.3 Mitigation Strategies

**R1: Category Validity Risk**
- Prevention: Use pre-registered clusters based on Lin et al. expert definitions
- Detection: Check inter-cluster ECE variance before hypothesis tests
- Response: If no variance, ABANDON H-E1 and subsequent hypotheses

**R2: Logit Access Risk**
- Prevention: Use only open-weight models (Llama-2, Mistral)
- Detection: Verify logit extraction before full experiment
- Response: SCOPE to open models only; note limitation for closed APIs

**R3: Small Sample Risk**
- Prevention: Group 38 categories into 7 larger clusters (~100-150 per cluster)
- Detection: Report bootstrap CI widths prominently
- Response: If CIs too wide, PIVOT to bootstrap-based inference, report effect sizes

**R4: Method Appropriateness Risk**
- Prevention: Include uncalibrated baseline to verify temperature scaling helps at all
- Detection: If global-T doesn't improve over uncalibrated, method may be wrong
- Response: EXPLORE alternative calibration (Platt scaling, histogram binning)

**R5: Generalization Risk**
- Prevention: Use 5-fold CV with strict train/test separation
- Detection: Check variance across folds
- Response: Report as limitation; add FACTOR cross-benchmark validation

### 4.4 Risk Summary

| ID | Risk | Severity | Mitigation |
|----|------|----------|------------|
| R1 | Category validity | High | Pre-registered clusters |
| R2 | Logit access | Medium | Open models only |
| R3 | Small sample | High | Cluster grouping + bootstrap |
| R4 | Method fit | High | Include uncalibrated baseline |
| R5 | Generalization | Medium | 5-fold CV + FACTOR validation |

**Risk Profile:** 0 Critical, 3 High, 2 Medium, 0 Low

---

## 5. Dependency Graph & Timeline

### 5.1 DAG Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    ┌─────────┐
    │  H-E1   │  Existence: Category variation exists
    │MUST_WORK│
    └────┬────┘
         │
         ▼
[Level 1-3 - Mechanisms]
    ┌─────────┐
    │  H-M1   │  Mechanism: Different confidence distributions
    │MUST_WORK│
    └────┬────┘
         │
         ▼
    ┌──────────┐
    │  H-M2    │  Mechanism: Different T values needed
    │SHOULD_WORK│
    └────┬─────┘
         │
         ▼
    ┌─────────┐
    │  H-M3   │  Mechanism: Cluster-T beats Global-T
    │MUST_WORK│
    └─────────┘

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 (4 sequential steps)
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Phase |
|-------|------------|---------------|-----------|-------|
| 0 | H-E1 | None | MUST_WORK | Foundation |
| 1 | H-M1 | H-E1 | MUST_WORK | Mechanism |
| 2 | H-M2 | H-M1 | SHOULD_WORK | Mechanism |
| 3 | H-M3 | H-M2 | MUST_WORK | Mechanism |

### 5.3 Gantt Timeline

```
Day:    1         2         3         4         5         6
        |---------|---------|---------|---------|---------|
H-E1    [████████]
H-M1              [████████]
H-M2                        [████████]
H-M3                                  [████████]
Replicate                                       [████████████████]
        |---------|---------|---------|---------|---------|
Gate 1  ^         Gate 2    ^         ^         Gate 3    ^
        H-E1 pass           H-M1 pass H-M2 pass H-M3 pass
```

### 5.4 Critical Path Analysis

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → Replication

- Total length: 6 days
- No parallelization possible (sequential dependencies)
- Gate 1 (Day 1): H-E1 must pass or all stops
- Gate 2 (Day 3): H-M1 must pass or pivot clustering
- Gate 3 (Day 5): H-M3 determines hypothesis validity

### 5.5 Resource Summary

| Resource | Requirement |
|----------|-------------|
| Compute | Single A100 GPU, ~6 hours total |
| Data | TruthfulQA CSV (817 questions) |
| Models | Llama-2-7B, Mistral-7B, Llama-2-13B |
| Software | HuggingFace transformers, calibration-toolbox |

### 5.6 Execution Order

1. **Day 1:** H-E1 — Compute per-cluster ECE, run ANOVA
2. **Day 2:** H-M1 — Confidence histograms, KS tests
3. **Day 3:** H-M2 — Optimize per-cluster T, check variance
4. **Day 4:** H-M3 — 5-fold CV comparison, paired t-test
5. **Day 5-6:** Replicate across Mistral-7B and Llama-2-13B

---

## 6. Dialectical Analysis

### 6.1 Thesis Statement

**Core Claim:** Cluster-specific temperature scaling achieves lower ECE than global temperature scaling on TruthfulQA because semantic category membership captures systematic variation in model confidence behavior.

**Supporting Evidence:**
1. Temperature scaling optimizes a single parameter to align confidence with accuracy
2. If confidence-accuracy relationship varies by category, separate temperatures should help
3. 5-fold cross-validation distinguishes real structure from noise fitting

**Strengths:**
- Built on established temperature scaling methodology (Guo et al., 2017)
- TruthfulQA provides expert-defined category labels (Lin et al., 2022)
- Clear quantitative success criteria (paired t-test p < 0.05, Cohen's d > 0.3)

**Expected Outcomes:**
- Primary: ECE(cluster-T) < ECE(global-T) with statistical significance
- Secondary: Per-cluster ECE values differ significantly (ANOVA p < 0.05)
- Tertiary: Calibration improvement transfers to FACTOR benchmark

### 6.2 Antithesis Development

**Null Hypothesis (H0):** There is no significant difference in ECE between cluster-specific temperature scaling and global temperature scaling on TruthfulQA. Category membership does not provide useful calibration information beyond a single global temperature.

**Counter-Arguments:**
1. Category differences may reflect difficulty variation, not calibration structure — ECE already accounts for accuracy, so this is handled
2. Small per-cluster samples (~100-150) may produce noise rather than signal
3. Optimal cluster-specific temperatures may converge to similar values, providing no benefit

**Potential Failure Points:**
- R1: Categories are arbitrary, no real semantic structure to exploit
- R3: Wide bootstrap CIs prevent statistical significance detection
- R4: Temperature scaling itself may be inappropriate for LLMs

**Conditions Under Which H0 Would Be Supported:**
- ANOVA on cluster ECE fails (p > 0.05) — no category variation exists
- Optimal T values identical across clusters — no calibration heterogeneity
- Paired t-test on cluster-T vs global-T fails (p > 0.05 OR d < 0.3)

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis H-ClusterCal-v1 presents a testable claim that semantic category membership captures calibration heterogeneity in LLMs. However, the null hypothesis raises valid concerns regarding statistical power with small per-cluster samples and whether observed variation reflects real structure versus noise.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** ANOVA on cluster ECE establishes existence of variation before mechanism testing
2. **Sequential mechanism testing (H-M1-3):** Tests each causal step independently
3. **Gate conditions:** Early detection of H0 support prevents wasted effort

**Conditions for Thesis Support:**
- All MUST_WORK gates pass (H-E1, H-M1, H-M3)
- Paired t-test confirms ECE improvement with p < 0.05 and d > 0.3
- Results replicate across Llama-2-7B, Mistral-7B, and Llama-2-13B

**Conditions for Antithesis Support:**
- H-E1 fails: No significant cluster ECE variation (ANOVA p > 0.05)
- H-M3 fails: Cluster-T does not beat global-T on held-out folds
- Effect size too small: d < 0.3 even if p < 0.05

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated, proceed to Phase 5
2. **Partial Support:** H-M2 fails but H-M3 passes → Document that T variance is small but still beneficial
3. **No Support:** H-E1 or H-M3 fail → Antithesis supported, hypothesis abandoned

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Category variation exists | May be artifact | H-E1 ANOVA test |
| Mechanism | Different T values needed | Optimal T converges | H-M2 variance check |
| Performance | Cluster-T beats global-T | Marginal improvement | H-M3 with effect size |
| Generalization | Transfers to FACTOR | TruthfulQA-specific | Phase 5 validation |

**Overall Robustness Score:** Medium-High

**Rationale:** Clear falsification criteria, pre-registered design, and established methodology. Main vulnerability is small per-cluster sample size.

**Confidence in Verification Plan:** 0.75

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Cluster-specific temperature scaling achieves lower ECE than global temperature scaling on TruthfulQA
- ID: H-ClusterCal-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 4 total (H-E1, H-M1, H-M2, H-M3)
- Duration: 6 days for Phase 4 PoC, 2 days replication
- Critical Gates: 3 decision points (H-E1, H-M1, H-M3)

**Risk Assessment:** Medium-High
- Primary concerns: Small per-cluster samples (R3), method appropriateness (R4)

**Immediate Action:** Begin with H-E1 — compute per-cluster ECE and run ANOVA

### 7.2 Final Summary

**Verification Execution Order:**

| Phase | Hypothesis | Duration | Gate |
|-------|------------|----------|------|
| 1 - Foundation | H-E1 | Day 1 | MUST_WORK |
| 2 - Mechanisms | H-M1, H-M2, H-M3 | Days 2-4 | H-M1 MUST_WORK |
| 3 - Replication | Cross-model validation | Days 5-6 | Complete |

**Critical Decision Points:**
1. Gate 1 (Day 1): H-E1 ANOVA p < 0.05 → PROCEED or ABANDON
2. Gate 2 (Day 2): H-M1 KS tests pass → PROCEED or PIVOT
3. Gate 3 (Day 4): H-M3 paired t-test p < 0.05, d > 0.3 → VALIDATED or REFUTED

### 7.3 Conclusions

**Open Questions (from Phase 2A):**
- Optimal number of clusters (currently 7 by expert judgment)
- Whether mechanism generalizes to other truthfulness benchmarks
- Interaction with model scale

**Recommendations:**
1. Start H-E1 immediately with Llama-2-7B on TruthfulQA
2. Pre-register cluster definitions before data analysis
3. Reserve FACTOR benchmark for Phase 5 cross-benchmark validation
4. Report bootstrap CIs prominently due to small per-cluster n

### 7.4 Appendices

**A. Phase 2A Reference:**
- Source: 03_refinement.yaml
- Hypothesis ID: H-ClusterCal-v1
- Schema version: 10.0.0

**B. MCP Tool Usage:**
- scientificmethod: 2 calls (H-E1, H-M integrated)
- Total MCP calls: 2

**C. Experimental Resources:**
- Models: Llama-2-7B, Mistral-7B, Llama-2-13B
- Dataset: TruthfulQA (817 questions, 38 categories → 7 clusters)
- Compute: ~6 hours on single A100

---

## 8. State & Pipeline

### 8.1 Verification State Status

✅ **verification_state.yaml** created at `docs/youra_research/verification_state.yaml`

| Field | Value |
|-------|-------|
| Main Hypothesis | H-ClusterCal-v1 |
| Sub-Hypotheses | 4 (H-E1, H-M1, H-M2, H-M3) |
| Ready to Start | H-E1 |
| Blocked | H-M1, H-M2, H-M3 (awaiting prerequisites) |

### 8.2 Pipeline Tasks Updated

⚠️ **Standalone Mode** — No Archon pipeline project found.
- Phase 2B: COMPLETE (local tracking)
- Phase 2C: NOT_STARTED (ready to begin)

### 8.3 Hypothesis Tasks Created

Local task tracking in verification_state.yaml:
- `h-e1`: READY → Execute first
- `h-m1`: NOT_STARTED → Awaits H-E1
- `h-m2`: NOT_STARTED → Awaits H-M1
- `h-m3`: NOT_STARTED → Awaits H-M2

---

**Phase 2B Complete.** Use `/phase2c-experiment-design` or `/hypothesis-next` to continue.
