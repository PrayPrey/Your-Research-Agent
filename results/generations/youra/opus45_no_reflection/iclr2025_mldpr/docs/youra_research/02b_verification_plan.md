# Verification Plan: Foundation Model Phase Transition in Benchmark Concentration

**Date:** 2026-08-18
**Hypothesis ID:** H-BenchmarkPhaseTransition-v1
**Confidence:** 0.75
**Total Hypotheses:** 6

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the condition of measuring ML benchmark usage patterns (2018-2024) using Papers With Code data, if the foundation model paradigm shift (2020-2021) represents a genuine structural change in research evaluation practices, then we will observe: (a) a statistically significant change point in aggregate Gini coefficient time series, (b) divergent concentration trajectories across input modalities, and (c) elevated benchmark portfolio churn, because foundation models redirect researcher attention toward emergent-capability benchmarks while fragmenting the previously unified benchmark ecosystem.

### 1.2 Alternative Hypothesis (H0)

Benchmark concentration 2018-2024 follows a single monotonic trend with no structural break; modality-specific patterns remain correlated (r > 0.5); foundation model emergence had no detectable effect on concentration dynamics or portfolio churn.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Papers With Code Historical Data (standard) | Contains task-dataset-metric triplets with paper associations; daily granularity enables monthly aggregation |
| **Model** | Statistical Analysis Pipeline | Standard methods for change-point detection and concentration measurement |

**Dataset Details:**
- Source: https://github.com/paperswithcode/paperswithcode-data
- Path: PWC daily dumps (2018-2024)

**Model Details:**
- Type: Time series analysis + concentration metrics
- Source: ruptures (PELT), scipy (stats), custom Gini/Jaccard implementation

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Koch et al. (2021) concentration metrics | Gini ~0.6-0.7 for 2015-2020 | Papers With Code + Semantic Scholar |
| Bechler-Speicher et al. (2025) benchmark critique | N/A (position paper) | Graph ML benchmarks |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Papers With Code data accurately represents ML benchmark usage patterns | PWC is primary source for Koch et al. (2021); 932★ repo with daily dumps | Results may not generalize to full ML research community |
| A2 | Task-dataset-metric triplet is appropriate unit for measuring benchmark usage | More precise than paper-dataset pairs; captures actual evaluation contexts | Concentration metrics may be miscalibrated |
| A3 | Input modality classification from PWC task categories is accurate | PWC uses expert-curated task hierarchies | Modality-specific analysis may have misclassification noise |
| A4 | Monthly temporal resolution is sufficient to detect structural breaks | PELT/Bai-Perron designed for time series with this granularity | Change points may be missed or falsely detected |
| A5 | Publication volume growth is separable from concentration effects | Gini normalizes within-period; volume normalization as robustness check | Cannot distinguish volume-driven from structure-driven changes |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First study to test phase transition hypothesis for benchmark concentration dynamics

**Key Innovation:** Churn-concentration matrix and velocity metrics for dynamic ecosystem analysis

**Differentiation:**
- Koch et al. (2021): Static snapshots vs dynamic metrics (velocity, change-point detection)
- Raji et al. (2021): Qualitative critique vs quantitative hypothesis testing
- TabArena (2025): Living benchmark design vs ecosystem-level concentration analysis

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | SHOULD_WORK | H-M2 | NOT_STARTED |
| H-M4 | Mechanism | SHOULD_WORK | H-M3 | NOT_STARTED |
| H-M5 | Mechanism | SHOULD_WORK | H-M4 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Existence of Phase Transition Signal

**Type:** EXISTENCE
**Statement:** Under the condition of analyzing Papers With Code data (2018-2024), if foundation model emergence represents a structural break, then PELT change-point detection will identify a statistically significant change point in aggregate Gini coefficient time series within the 2019-2022 window at α=0.05.

**Rationale:** This establishes whether a detectable phase transition signal exists in the data before testing the causal mechanism. Without confirming existence, mechanism testing is premature.

**Variables:**
- IV: Time period (pre-2020 vs post-2021)
- DV: Gini coefficient of benchmark usage distribution [0,1]
- CV: Publication volume (normalized by monthly paper count)

**Verification Protocol:**
1. Download PWC historical dumps and parse task-dataset-metric triplets (2018-2024)
2. Compute monthly aggregate Gini coefficient time series
3. Apply PELT algorithm with α=0.05 significance threshold
4. Test if change point falls within 2019-2022 window

**Success Criteria (PoC: Direction-based):**
- Primary: Change point detected within 2019-2022 at α=0.05
- Secondary: Segmented model fits better than single monotonic trend (BIC comparison)

**Failure Response:**
- IF fails: PIVOT to quarterly aggregation or alternative change-point method (Bai-Perron)

**Dependencies:** None

**Source:** Phase 2A Prediction P1, SH1

---

#### H-M1: Foundation Model Emergence Timeline

**Type:** MECHANISM
**Statement:** Under the condition of examining ML publication records (2019-2021), if foundation models represent a paradigm shift, then GPT-3 (2020), ViT (2020), and BERT successors are identifiable as high-impact papers with citation counts exceeding field medians by >2σ.

**Rationale:** This validates that foundation model emergence actually occurred as hypothesized and was significant enough to plausibly drive ecosystem change.

**Variables:**
- IV: Paper publication date (2019-2021)
- DV: Citation impact relative to field median
- CV: Publication venue, paper type

**Verification Protocol:**
1. Identify foundation model papers from Semantic Scholar (GPT-3, ViT, BERT variants)
2. Compute citation counts and field-normalized impact
3. Compare to contemporaneous ML paper distribution
4. Confirm >2σ impact for key papers

**Success Criteria (PoC: Direction-based):**
- Primary: Foundation model papers have citation impact >2σ above field median
- Secondary: Timeline aligns with hypothesized 2019-2021 emergence window

**Failure Response:**
- IF fails: EXPLORE alternative paradigm shift markers (GitHub stars, leaderboard positions)

**Dependencies:** H-E1

**Source:** Phase 2A Causal Step 1

---

#### H-M2: Emergent-Capability Benchmark Creation

**Type:** MECHANISM
**Statement:** Under the condition of tracking benchmark creation dates on Papers With Code, if foundation models drove new evaluation practices, then MMLU (2020), BIG-Bench (2022), HumanEval (2021) and similar emergent-capability benchmarks were created post-foundation-model emergence.

**Rationale:** This tests whether new benchmarks actually emerged to evaluate foundation model capabilities, supporting the causal mechanism.

**Variables:**
- IV: Benchmark creation date
- DV: Benchmark type (emergent-capability vs traditional)
- CV: Modality, task category

**Verification Protocol:**
1. Extract benchmark creation dates from Papers With Code
2. Classify benchmarks as emergent-capability (MMLU, BIG-Bench, HumanEval) vs traditional
3. Compare creation date distributions pre-2020 vs post-2020
4. Confirm emergent-capability benchmarks cluster post-foundation-model

**Success Criteria (PoC: Direction-based):**
- Primary: >80% of emergent-capability benchmarks created post-2020
- Secondary: Creation rate of emergent-capability benchmarks increases post-2020

**Failure Response:**
- IF fails: Document as limitation; emergent benchmarks may predate hypothesis

**Dependencies:** H-M1

**Source:** Phase 2A Causal Step 2

---

#### H-M3: Researcher Attention Shift

**Type:** MECHANISM
**Statement:** Under the condition of analyzing leaderboard submission patterns, if researcher attention shifted to emergent-capability benchmarks, then paper counts on MMLU/BIG-Bench/HumanEval leaderboards increased relative to traditional benchmarks post-2021.

**Rationale:** This tests whether researchers actually redirected evaluation effort toward new benchmarks, the key behavioral mechanism.

**Variables:**
- IV: Benchmark category (emergent vs traditional)
- DV: Paper submission count (monthly)
- CV: Publication volume normalization

**Verification Protocol:**
1. Extract monthly paper counts per benchmark from PWC leaderboards
2. Compute relative share of emergent vs traditional benchmarks
3. Compare pre-2021 vs post-2021 distributions
4. Test for significant shift via chi-square test

**Success Criteria (PoC: Direction-based):**
- Primary: Emergent-capability benchmark share increases post-2021
- Secondary: Absolute paper counts on emergent benchmarks exceed traditional by 2024

**Failure Response:**
- IF fails: EXPLORE whether attention shift is domain-specific (NLP vs CV)

**Dependencies:** H-M2

**Source:** Phase 2A Causal Step 3

---

#### H-M4: Traditional Benchmark Persistence with Reduced Dominance

**Type:** MECHANISM
**Statement:** Under the condition of tracking ImageNet and CIFAR benchmark usage (2018-2024), if traditional benchmarks persist with reduced dominance, then their share of total benchmark usage decreases while absolute paper counts remain stable.

**Rationale:** This distinguishes ecosystem fragmentation (many benchmarks) from traditional benchmark abandonment.

**Variables:**
- IV: Benchmark type (ImageNet/CIFAR vs others)
- DV: Relative share of total benchmark usage
- CV: Absolute paper counts

**Verification Protocol:**
1. Extract monthly usage counts for ImageNet, CIFAR-10/100
2. Compute relative share vs all benchmarks
3. Track absolute counts over time
4. Confirm share decreases while absolute counts stable

**Success Criteria (PoC: Direction-based):**
- Primary: Traditional benchmark share decreases post-2020
- Secondary: Absolute paper counts remain within 20% of pre-2020 levels

**Failure Response:**
- IF fails: Document as finding; traditional benchmarks may be actively declining

**Dependencies:** H-M3

**Source:** Phase 2A Causal Step 4

---

#### H-M5: Modality Divergence (Phase Transition Effect)

**Type:** MECHANISM
**Statement:** Under the condition of computing modality-specific Gini coefficients, if foundation models caused modality-differentiated dynamics, then post-2021 Pearson correlation between CV and NLP Gini series drops below 0.4 from pre-2020 baseline of >0.6.

**Rationale:** This is the key test of phase transition: unified concentration dynamics should fragment into modality-specific patterns.

**Variables:**
- IV: Modality (text, image, tabular, multimodal)
- DV: Rolling-window Pearson correlation between modality Gini series
- CV: Window size, temporal alignment

**Verification Protocol:**
1. Compute monthly Gini per modality (text, image, tabular, multimodal)
2. Calculate rolling-window Pearson correlations (6-month window)
3. Compare pre-2020 vs post-2021 correlation distributions
4. Apply Fisher z-test for significance

**Success Criteria (PoC: Direction-based):**
- Primary: Pre-2020 r > 0.6; Post-2021 r < 0.4
- Secondary: Fisher z-test significant at α=0.05

**Failure Response:**
- IF fails: PIVOT to testing whether divergence is domain-pair specific (CV-NLP vs others)

**Dependencies:** H-M4

**Source:** Phase 2A Prediction P2, Causal Step 5

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-M5
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Change point in 2019-2022 at α=0.05 | STOP, reassess hypothesis |
| H-M1 | MUST_WORK | Foundation papers >2σ impact | STOP, no paradigm shift evidence |
| H-M2 | SHOULD_WORK | >80% emergent benchmarks post-2020 | Document limitation |
| H-M3 | SHOULD_WORK | Attention shift to emergent benchmarks | Document limitation |
| H-M4 | SHOULD_WORK | Share decrease, counts stable | Document finding |
| H-M5 | SHOULD_WORK | Correlation drop >0.6 to <0.4 | Pivot to domain-pair analysis |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1 to H-M5 | 6 weeks |

**Total Duration:** 8 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: PWC data incomplete | A1 | H-E1, H-M1-5 | High |
| R2: Triplet unit miscalibrated | A2 | H-E1, H-M3-5 | Medium |
| R3: Modality misclassification | A3 | H-M5 | Medium |
| R4: Temporal resolution insufficient | A4 | H-E1 | High |
| R5: Volume confound inseparable | A5 | H-E1, H-M3-5 | High |

### 4.2 Mitigation Strategies

**R1: PWC Data Incomplete**
- Prevention: Verify PWC coverage via comparison with Semantic Scholar counts
- Detection: Compute coverage ratio by year and modality
- Response: PIVOT to Semantic Scholar supplementation if coverage <70%

**R2: Triplet Unit Miscalibrated**
- Prevention: Validate against Koch et al. methodology
- Detection: Compare paper-dataset pair vs triplet Gini values
- Response: SCOPE to paper-dataset pairs as robustness check

**R3: Modality Misclassification**
- Prevention: Use PWC expert-curated task hierarchies
- Detection: Manual audit of 100 random benchmark-modality assignments
- Response: SCOPE to high-confidence classifications only

**R4: Temporal Resolution Insufficient**
- Prevention: Use PELT with established parameters for monthly data
- Detection: Run sensitivity analysis with quarterly aggregation
- Response: PIVOT to quarterly if monthly PELT unstable

**R5: Volume Confound Inseparable**
- Prevention: Always report volume-normalized metrics alongside raw
- Detection: Compare raw vs normalized Gini trajectories
- Response: If patterns diverge, report both as distinct findings

### 4.3 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | PWC data incomplete | A1 | High | All | Semantic Scholar supplementation |
| R2 | Triplet miscalibration | A2 | Medium | H-E1, H-M3-5 | Paper-dataset pair robustness |
| R3 | Modality misclassification | A3 | Medium | H-M5 | Manual audit sample |
| R4 | Temporal resolution | A4 | High | H-E1 | Quarterly sensitivity |
| R5 | Volume confound | A5 | High | H-E1, H-M3-5 | Dual reporting |

Critical Risks: 0
High Risks: 3
Medium Risks: 2
Low Risks: 0

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 6 Hypotheses
═══════════════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence - Phase Transition Signal)
         │
         ▼
[Level 1 - Mechanisms]
    H-M1 (Foundation Model Emergence) ← H-E1
         │
         ▼
    H-M2 (Emergent Benchmark Creation) ← H-M1
         │
         ▼
    H-M3 (Researcher Attention Shift) ← H-M2
         │
         ▼
    H-M4 (Traditional Benchmark Persistence) ← H-M3
         │
         ▼
    H-M5 (Modality Divergence) ← H-M4
         │
         ▼
    [COMPLETE]

═══════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-M5
═══════════════════════════════════════════════════════════════════
```

### 5.2 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 6 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2 │ W3-4 │ W5 │ W6 │ W7 │ W8
─────────────────┼──────┼──────┼────┼────┼────┼────
PHASE 1: Foundation
  H-E1           │██████│      │    │    │    │
  [Gate 1]       │      │◆     │    │    │    │
─────────────────┼──────┼──────┼────┼────┼────┼────
PHASE 2: Mechanisms
  H-M1           │      │██████│    │    │    │
  H-M2           │      │      │████│    │    │
  H-M3           │      │      │    │████│    │
  H-M4           │      │      │    │    │████│
  H-M5           │      │      │    │    │    │████
  [Gate 2]       │      │      │    │    │    │   ◆
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 8 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.3 Critical Path Analysis

- Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-M5
- Total Duration: 8 weeks (2 + 2 + 1 + 1 + 1 + 1)
- Slack Available: 0 weeks (all sequential)
- Execution Mode: Sequential chain

### 5.4 Execution Order

1. **Week 1-2:** Execute H-E1 (Foundation) - PELT change-point detection
2. **Gate 1:** If H-E1 passes, proceed; if fails, STOP
3. **Week 3-4:** Execute H-M1 (Foundation model emergence validation)
4. **Week 5:** Execute H-M2 (Emergent benchmark creation)
5. **Week 6:** Execute H-M3 (Attention shift)
6. **Week 7:** Execute H-M4 (Traditional benchmark persistence)
7. **Week 8:** Execute H-M5 (Modality divergence)
8. **Gate 2:** Final assessment

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Foundation model emergence (2020-2021) created a structural break in ML benchmark concentration patterns, observable through PELT change-point detection on Gini coefficient time series, divergent modality-specific trajectories, and elevated portfolio churn.

**Supporting Evidence:**
1. Foundation model timeline (GPT-3: 2020, ViT: 2020) aligns with hypothesized change point
2. New benchmark creation (MMLU, BIG-Bench, HumanEval) observable in Papers With Code
3. Koch et al. (2021) established baseline concentration patterns 2015-2020

**Strengths:**
- Five-step causal mechanism with testable predictions at each step
- Four quantitative predictions with explicit success criteria
- Builds on established Koch et al. (2021) methodology
- Either confirmation or refutation is publishable result

**Expected Outcomes:**
- P1: PELT detects change point in 2019-2022 at α=0.05
- P2: CV-NLP Gini correlation drops from >0.6 to <0.4
- P3: Text-modality Gini velocity exceeds image-modality by >2σ
- P4: Portfolio churn significantly increases post-2020

### 6.2 Antithesis

**Null Hypothesis (H0):** Benchmark concentration 2018-2024 follows a single monotonic trend with no structural break; modality-specific patterns remain correlated (r > 0.5); foundation model emergence had no detectable effect on concentration dynamics or portfolio churn.

**Counter-Arguments:**
1. Publication volume growth alone could explain concentration changes
2. PELT may detect false change points due to window selection bias
3. New benchmark creation is part of normal field evolution, not paradigm shift

**Potential Failure Points:**
- R4: Temporal resolution insufficient for PELT
- R5: Volume confound inseparable from concentration effect
- R1: PWC data incomplete for certain periods/modalities

**Conditions Under Which H0 Would Be Supported:**
- No change point detected in 2019-2022 via PELT
- Single monotonic trend fits better than segmented model (BIC)
- Modality correlations remain above 0.5 throughout period

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis H-BenchmarkPhaseTransition-v1 presents a testable claim that foundation model emergence created a structural break in benchmark concentration dynamics. However, the null hypothesis raises valid concerns regarding publication volume confounds and PELT sensitivity.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes existence before mechanism testing
2. **Sequential mechanism testing (H-M1-5):** Tests causal chain step-by-step
3. **Gate conditions:** Allow early detection of H0 support
4. **Volume normalization:** Always report alongside raw metrics

**Conditions for Thesis Support:**
- All MUST_WORK gates pass (H-E1, H-M1)
- P1 (change point) is confirmed
- Mechanism chain validates through H-M5

**Conditions for Antithesis Support:**
- H-E1 fails (no change point detected)
- H-M1 fails (foundation models not high-impact)
- Volume-normalized metrics show no effect

**Nuanced Outcome Possibilities:**
1. **Full Support:** All hypotheses pass → Thesis validated
2. **Partial Support:** Some H-M fail → Refined thesis with limitations
3. **No Support:** H-E1 or H-M1 fail → Antithesis supported

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Change point exists | May be artifact | H-E1 PELT test |
| Mechanism | Causal chain valid | Volume confound | H-M1-5 with normalization |
| Scope | All modalities affected | Domain-specific | H-M5 modality analysis |
| Performance | vs Koch baseline | Incremental continuation | Phase 5 comparison |

**Overall Robustness Score:** Medium-High

**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary

**Main Hypothesis:** Foundation model emergence (2020-2021) created structural break in ML benchmark concentration patterns
- ID: H-BenchmarkPhaseTransition-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 6 total
  - H-E: 1, H-M: 5
- Phases: 2 phases over 8 weeks
- Critical Gates: 2 decision points

**Risk Assessment:** Medium-High
- Primary concerns: Volume confound (R5), Temporal resolution (R4)

**Immediate Action:** Begin Phase 1 with H-E1 (PELT change-point detection)

---

## 8. Conclusions

### 8.1 Key Achievements

- 6 hypotheses across 2 phases
- H0 addressed via dialectical analysis
- All risks mapped with mitigation strategies

### 8.2 Verification Execution Order

**Phase 1: Foundation** (2 weeks)
- H-E1: PELT change-point detection on aggregate Gini series
- Gate 1: MUST PASS

**Phase 2: Core Mechanisms** (6 weeks)
- H-M1: Foundation model emergence validation
- H-M2: Emergent benchmark creation
- H-M3: Researcher attention shift
- H-M4: Traditional benchmark persistence
- H-M5: Modality divergence
- Gate 2: H-M1 must pass

### 8.3 Critical Decision Points

1. **Gate 1 (Foundation):** H-E1 must pass
   - FAIL → STOP, reassess hypothesis
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** H-M1 must pass
   - CRITICAL FAIL → Execute failure response
   - OPTIONAL FAIL → Document limitation

### 8.4 Open Questions

- Exact correlation threshold justification (>0.6 to <0.4) needs effect size analysis
- Robustness of PELT to window selection requires sensitivity analysis
- Volume normalization may affect velocity comparisons

### 8.5 Recommendations

1. **Immediate Actions:**
   - Start Phase 1 with H-E1
   - Set up PWC data pipeline

2. **Resource Allocation:**
   - Allocate 8 weeks for critical path
   - Reserve 2-week buffer for failures

3. **Failure Management:**
   - Document all failures
   - Execute PIVOT strategies as defined

---

## Appendices

### A. Phase 2A Reference
- **Source:** 03_refinement.yaml (ID: H-BenchmarkPhaseTransition-v1)

### B. MCP Tool Usage Summary
- **Total MCP calls:** 4
- **Tools:** scientificmethod (2x), structuredargumentation (2x)

### C. Established Facts Registry

| Claim | Status | Evidence |
|-------|--------|----------|
| Benchmark concentration increased 2015-2020 with Gini ~0.6-0.7 | BUILD_ON | Koch et al. (2021) |
| Elite institution dataset dominance documented | BUILD_ON | Koch et al. (2021) |
| Gini coefficient is valid concentration metric | BUILD_ON | Standard economics metric |
| Foundation models created structural break | PROVE_NEW | Requires testing |
| Modality-specific concentration dynamics differ | PROVE_NEW | Requires testing |
| Benchmark portfolio churn increased post-2020 | PROVE_NEW | Requires testing |

**Scope Reduction:** 50% (3 BUILD_ON claims, 3 PROVE_NEW claims)

---

**Document Status:** Complete
**Generated By:** Phase 2B Planning Workflow
**Next Phase:** Phase 2C Experiment Design
