# Verification Plan: ImageNet Model Ranking Stability Analysis

**Date:** 2026-08-29
**Hypothesis ID:** H-RankingStability-v1
**Confidence:** 0.80
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under controlled evaluation conditions (same models, same task semantics),
if we evaluate ImageNet models on an independently-collected benchmark variant (ImageNet-V2),
then model rankings will shift significantly (Kendall-τ < 0.90),
because iterative community optimization on popular benchmarks creates benchmark-specific
adaptations that don't transfer to novel test distributions.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in model rankings between ImageNet and ImageNet-V2;
Kendall-τ ≥ 0.95 indicating rankings are essentially preserved across benchmark variants.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | ImageNet + ImageNet-V2 (standard) | Direct benchmark pair for testing ranking stability across original vs alternative test set |
| **Model** | ImageNet classification models (2015-2024) | Diverse models spanning temporal range needed for both ranking and temporal analysis |

**Dataset Details:**
- Source: Papers With Code leaderboards + Recht et al. supplementary + subsequent papers
- Path: paperswithcode.com/sota/image-classification-on-imagenet

**Model Details:**
- Type: Various architectures: ResNet, ViT, ConvNeXt, EfficientNet, etc.
- Source: Published papers with ImageNet and ImageNet-V2 results

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Random baseline | Expected τ under random permutation | ImageNet/V2 |
| Perfect correlation | τ = 1.0 (rankings preserved) | ImageNet/V2 |
| Recht et al. (2019) | 11-14% accuracy drops | ImageNet-V2 |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | ImageNet-V2 results from different papers are comparable (same evaluation protocol) | Recht et al. released standardized evaluation code widely adopted | Ranking correlations confounded by protocol differences |
| A2 | Papers With Code leaderboard data accurately reflects published results | Standard community resource, regularly updated | Data collection errors; cross-validate with original papers |
| A3 | Model publication year is reasonable proxy for benchmark-specific knowledge exposure | Cumulative community knowledge increases over time | Temporal effect could reflect other trends; use multivariate controls |
| A4 | Kendall-τ is appropriate metric for ranking stability | Standard metric in statistics for comparing rankings | Results might not capture practically important changes; also report Top-K overlap |
| A5 | Selection of models with ImageNet-V2 results is not severely biased | ImageNet-V2 evaluation has become standard | Results may understate true population effect; note potential selection bias |

### 1.6 Research Gap & Novelty

**Gap:** No prior work computed Kendall-τ between ImageNet/ImageNet-V2 model rankings. Recht et al. (2019) measured accuracy drops but not ranking correlations. Dehghani et al. (2021) analyzed task selection in NLU, not benchmark variant generalization.

**Novelty:** First systematic analysis of ranking stability (vs accuracy drops) between ImageNet and ImageNet-V2. Shifts focus from absolute accuracy degradation to relative ranking preservation, which is more practically relevant for model selection decisions. Introduces temporal dimension to benchmark overfitting analysis.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| h-e1 | EXISTENCE | MUST_WORK | None | READY |
| h-m1 | MECHANISM | MUST_WORK | h-e1 | READY |
| h-m2 | MECHANISM | SHOULD_WORK | h-m1 | READY |
| h-m3 | MECHANISM | SHOULD_WORK | h-m1 | READY |

---

### 2.2 Hypothesis Specifications

#### h-e1: Ranking Shift Existence

**Type:** EXISTENCE
**Statement:** Under controlled evaluation conditions, if we compute Kendall-τ between ImageNet and ImageNet-V2 model rankings, then τ < 0.90, because benchmark-specific optimizations create non-uniform performance degradation.

**Variables:**
- IV: Benchmark variant (ImageNet vs ImageNet-V2)
- DV: Kendall-τ ranking correlation coefficient
- CV: Same model set, same task semantics

**Success Criteria:**
- τ < 0.90 with 95% CI not including 0.95
- p < 0.001 for deviation from perfect correlation

**Gate:**
- Type: MUST_WORK
- If Fail: Core phenomenon not present; revisit Phase 2A

**Prerequisites:** None

**Verification Protocol:**
1. Collect accuracy data from Papers With Code for models evaluated on both ImageNet and ImageNet-V2
2. Compute ranking for each benchmark based on top-1 accuracy
3. Calculate Kendall-τ between the two rankings
4. Bootstrap 95% confidence intervals
5. Test H0: τ ≥ 0.95

---

#### h-m1: Non-Uniform Degradation Mechanism

**Type:** MECHANISM
**Statement:** Under comparison of model accuracy drops, if we compute per-model ImageNet-to-V2 accuracy drop, then variance in drops is significantly higher than expected from measurement noise, because different architectures have different degrees of benchmark-specific adaptation.

**Variables:**
- IV: Model architecture family
- DV: Accuracy drop variance across models
- CV: Same evaluation protocol, same test set size

**Success Criteria:**
- Coefficient of variation in accuracy drops > 0.15
- Architecture explains significant variance (ANOVA p < 0.05)

**Gate:**
- Type: MUST_WORK
- If Fail: Degradation is uniform; ranking shifts may be noise

**Prerequisites:** h-e1 (ranking shift must exist to explain)

**Verification Protocol:**
1. Compute accuracy drop for each model: acc_imagenet - acc_v2
2. Calculate variance and coefficient of variation across models
3. Test if variance exceeds measurement noise floor
4. ANOVA on drops by architecture family

---

#### h-m2: Top-K Overlap Degradation

**Type:** MECHANISM
**Statement:** Under ranking comparison, if we examine Top-10 models by ImageNet accuracy, then Top-10 overlap with ImageNet-V2 rankings is < 80%, because performance shifts disproportionately affect models at ranking boundaries.

**Variables:**
- IV: Benchmark variant
- DV: Top-10 overlap percentage
- CV: Same model pool, same ranking method

**Success Criteria:**
- Overlap < 80% (at most 7 of 10 in both Top-10 lists)
- Chi-square test for independence p < 0.05

**Gate:**
- Type: SHOULD_WORK
- If Fail: Ranking instability may not affect model selection decisions

**Prerequisites:** h-m1 (non-uniform degradation established)

**Verification Protocol:**
1. Identify Top-10 models by ImageNet accuracy
2. Identify Top-10 models by ImageNet-V2 accuracy
3. Count intersection
4. Test if overlap is significantly below expected (8-9 under H0)

---

#### h-m3: Temporal Correlation

**Type:** MECHANISM
**Statement:** Under multivariate analysis, if we regress pairwise ranking agreement on model publication year, then β_year < 0, because newer models have more accumulated benchmark-specific optimization.

**Variables:**
- IV: Model publication year (2015-2024)
- DV: Pairwise ranking agreement with reference models
- CV: Architecture family, parameter count

**Success Criteria:**
- β_year < 0 with p < 0.05
- R² improvement when adding year to model

**Gate:**
- Type: SHOULD_WORK
- If Fail: Temporal effect not present; benchmark overfitting may be instantaneous

**Prerequisites:** h-m1 (mechanism established)

**Verification Protocol:**
1. For each model, compute pairwise ranking agreement with all other models
2. Fit regression: agreement ~ year + architecture + log(params)
3. Test coefficient on year
4. Check if year adds predictive power beyond architecture/params

---

## 3. Execution

### 3.1 Dependency Chain
```
h-e1 → h-m1 → h-m2
            → h-m3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| h-e1 | MUST_WORK | τ < 0.90, p < 0.001 | ABORT: Core phenomenon absent |
| h-m1 | MUST_WORK | CV > 0.15, ANOVA p < 0.05 | ABORT: No mechanism to explain |
| h-m2 | SHOULD_WORK | Overlap < 80% | CONTINUE: Note limitation |
| h-m3 | SHOULD_WORK | β_year < 0, p < 0.05 | CONTINUE: Temporal effect absent |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Existence | h-e1 | 1 day |
| Phase 2: Core Mechanism | h-m1 | 1 day |
| Phase 3: Extended Analysis | h-m2, h-m3 (parallel) | 2 days |

**Total Duration:** 4 days

---

## 4. Risk Analysis

### 4.1 Risk Identification

| Risk ID | Risk | Probability | Impact | Mitigation |
|---------|------|-------------|--------|------------|
| R1 | Insufficient model count with V2 results | Medium | High | Pre-check Papers With Code; minimum 30 models required |
| R2 | Evaluation protocol inconsistencies | Low | High | Verify evaluation protocol matches across papers |
| R3 | Selection bias in V2 evaluation | Medium | Medium | Acknowledge as limitation; note direction of bias |
| R4 | Kendall-τ near threshold (0.88-0.92) | Medium | Medium | Report confidence intervals; interpret cautiously |
| R5 | Architecture confounding temporal effect | Low | Medium | Include architecture in multivariate model |

### 4.2 Risk-Hypothesis Mapping

| Hypothesis | Primary Risks | Mitigation Priority |
|------------|---------------|---------------------|
| h-e1 | R1, R2, R4 | High |
| h-m1 | R2, R3 | High |
| h-m2 | R1, R3 | Medium |
| h-m3 | R3, R5 | Medium |

### 4.3 Mitigation Strategies

**R1 Mitigation:** Pre-flight data collection check before Phase 4 implementation. If <30 models available, expand search to original papers beyond leaderboards.

**R2 Mitigation:** Cross-validate 10% of entries with original paper tables. Flag and exclude inconsistent entries.

**R3 Mitigation:** Document selection criteria clearly. Perform sensitivity analysis excluding newest models (most likely to have V2 results).

**R4 Mitigation:** Bootstrap confidence intervals. If 95% CI crosses 0.90, interpret as "inconclusive" rather than "confirmed" or "rejected".

**R5 Mitigation:** Always include architecture family as covariate. Report stratified analyses by architecture.

---

## 5. Dependency Graph

### 5.1 DAG Visualization

```
┌─────────────────────────────────────────────────────────────┐
│                    VERIFICATION DAG                          │
└─────────────────────────────────────────────────────────────┘

            ┌──────────┐
            │   h-e1   │ ← MUST_WORK (Ranking shift exists)
            │ EXISTENCE│
            └────┬─────┘
                 │
                 ▼
            ┌──────────┐
            │   h-m1   │ ← MUST_WORK (Non-uniform degradation)
            │MECHANISM │
            └────┬─────┘
                 │
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
   ┌──────────┐     ┌──────────┐
   │   h-m2   │     │   h-m3   │
   │MECHANISM │     │MECHANISM │
   │Top-K     │     │Temporal  │
   └──────────┘     └──────────┘
   SHOULD_WORK      SHOULD_WORK

Legend:
  ─── = Sequential dependency (must pass before proceeding)
  ─┬─ = Parallel execution possible after gate passes
```

### 5.2 Dependency Hierarchy

| Level | Hypotheses | Gate | Parallel? |
|-------|------------|------|-----------|
| 1 | h-e1 | MUST_WORK | No |
| 2 | h-m1 | MUST_WORK | No |
| 3 | h-m2, h-m3 | SHOULD_WORK | Yes |

---

## 6. Timeline (Gantt)

```
Day:     1         2         3         4
        |---------|---------|---------|---------|
h-e1:   [=========]
                   GATE ✓
h-m1:             [=========]
                             GATE ✓
h-m2:                       [=========]
h-m3:                       [=========]
                                       |
                                    COMPLETE
```

### 6.1 Critical Path

**Critical Path:** h-e1 → h-m1 → (h-m2 ∥ h-m3)

- h-e1 and h-m1 are sequential gates; any failure aborts
- h-m2 and h-m3 can run in parallel after h-m1 passes
- SHOULD_WORK hypotheses can fail without aborting

### 6.2 Resource Summary

| Resource | Required | Notes |
|----------|----------|-------|
| Papers With Code API | Optional | Manual collection acceptable |
| Compute | Minimal | Statistical analysis only |
| Time | 4 days | Conservative estimate |

### 6.3 Execution Order

1. **Day 1:** Execute h-e1 (data collection + Kendall-τ computation)
2. **Day 2:** Execute h-m1 (variance analysis + ANOVA)
3. **Days 3-4:** Execute h-m2 and h-m3 in parallel (Top-K overlap + temporal regression)

---

## 7. Dialectical Analysis

### 7.1 Thesis

**Claim:** Model rankings shift significantly between ImageNet and ImageNet-V2 (Kendall-τ < 0.90) due to iterative benchmark-specific optimization.

**Supporting Evidence:**
- Recht et al. (2019) documented 11-14% accuracy drops on V2
- Accuracy drops are model-specific, not uniform
- Benchmark concentration (90% usage in top 10% of benchmarks) creates optimization pressure

### 7.2 Antithesis (Devil's Advocate)

**Counter-Claim (H0):** Rankings are preserved (τ ≥ 0.95) despite accuracy drops because:

1. **Uniform degradation:** All models may experience similar percentage drops, preserving relative rankings
2. **Architecture dominance:** Fundamental architecture quality may overwhelm benchmark-specific effects
3. **Selection artifact:** Models evaluated on V2 are often those expected to generalize well (publication bias)

**Evidence for Antithesis:**
- Accuracy drops in Recht et al. were relatively consistent (11-14% range)
- Strong correlation between ImageNet and V2 accuracy in many prior analyses
- Researchers may avoid publishing poor V2 results

### 7.3 Synthesis

**Resolution:** The empirical test directly resolves this tension:

- If τ < 0.90: Thesis confirmed; ranking shifts are practically significant
- If τ ∈ [0.90, 0.95): Weak support for thesis; ranking shifts exist but are moderate
- If τ ≥ 0.95: Antithesis confirmed; rankings are essentially preserved

**Key Insight:** The synthesis is not theoretical but empirical. The hypothesis is designed to be falsifiable with clear thresholds. The Kendall-τ value will definitively resolve the debate.

### 7.4 Robustness Assessment

| Aspect | Assessment | Confidence |
|--------|------------|------------|
| Thesis support | Strong (prior evidence of non-uniform drops) | 0.70 |
| Antithesis plausibility | Moderate (possible but less parsimonious) | 0.30 |
| Falsifiability | High (clear quantitative threshold) | 0.95 |
| Mitigation of bias | Moderate (selection bias remains concern) | 0.70 |

**Overall Robustness:** The hypothesis is well-designed for empirical resolution. The main uncertainty is whether the effect size will cross the pre-specified threshold.

---

## 8. Executive Summary

### Key Findings

- **4 sub-hypotheses** defined: 1 existence (h-e1), 3 mechanism (h-m1, h-m2, h-m3)
- **2 MUST_WORK gates** (h-e1, h-m1): Core phenomenon and mechanism must be validated
- **2 SHOULD_WORK gates** (h-m2, h-m3): Extended analysis; failure does not abort
- **Critical path:** 4 days estimated duration
- **Primary metric:** Kendall-τ < 0.90 with p < 0.001

### Scope Reduction

Building on established facts (60% scope reduction from Phase 2A):
- Accuracy drops (BUILD_ON) → Not re-tested
- Benchmark concentration (BUILD_ON) → Not re-tested
- Kendall-τ computation (PROVE_NEW) → Core of h-e1
- Temporal correlation (PROVE_NEW) → Core of h-m3

### Decision Points

| Gate | Decision | Action if Fail |
|------|----------|----------------|
| h-e1 | τ < 0.90? | ABORT pipeline |
| h-m1 | Non-uniform degradation? | ABORT pipeline |
| h-m2 | Top-K < 80%? | Continue with caveat |
| h-m3 | Temporal effect? | Continue; temporal component optional |

### Next Steps

1. **Phase 2C:** Design detailed experiment for each hypothesis
2. **Phase 3:** Implementation planning (data collection + analysis scripts)
3. **Phase 4:** Execute PoC validation (MUST_WORK gates)

---

## Appendices

### A. Phase 2A Cross-Reference

| Phase 2A Section | Used In |
|------------------|---------|
| established_facts | Section 8 (Scope Reduction) |
| core_statement | Section 1.1 |
| variables | Section 2.2 (all hypotheses) |
| causal_mechanism | h-m1, h-m2, h-m3 design |
| key_assumptions | Section 1.5, Risk Analysis |
| predictions | Success criteria mapping |

### B. Hypothesis ID Mapping

| Phase 2B ID | Phase 2A Prediction | Type |
|-------------|---------------------|------|
| h-e1 | P1 (Kendall-τ) | EXISTENCE |
| h-m1 | Causal step 3-4 | MECHANISM |
| h-m2 | P2 (Top-10 overlap) | MECHANISM |
| h-m3 | P3 (Temporal) | MECHANISM |

### C. State File Reference

- **verification_state.yaml:** Generated by Step 10; contains hypothesis states for Phase 2C-4 loop
- **Per-hypothesis context:** Generated JIT by Phase 2C

---

*Generated by Phase 2B Planning Workflow*
*Architecture: Step-file (11 steps)*
*Mode: UNATTENDED*
