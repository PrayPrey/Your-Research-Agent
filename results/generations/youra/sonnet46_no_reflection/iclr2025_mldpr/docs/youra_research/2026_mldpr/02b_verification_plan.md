---
title: "Verification Plan: BCBHS — Benchmark-Calibrated Health Score for Cross-Domain Discriminative Collapse Prediction"
hypothesis_id: "H-BCBHS-v1"
date: "2026-05-19"
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
status: complete
completedAt: "2026-05-19T06:37:45Z"
research_mode: incremental
pipeline_project_id: "3e07f6ec-3096-4eec-96e7-ea10800001bc"
total_hypotheses: 5
---

# Verification Plan: BCBHS — Benchmark-Calibrated Health Score for Cross-Domain Discriminative Collapse Prediction

**Date:** 2026-05-19
**Hypothesis ID:** H-BCBHS-v1
**Confidence:** 0.78
**Total Hypotheses:** 5 (H-E1, H-M1, H-M2, H-M3, H-M4)

---

## 0. Established Facts & Scope Reduction

**Scope Reduction: 33%** (4 of 6 Phase 2A claims are BUILD_ON — not re-verified in Phase 2B–4)

| Claim | Status | Evidence |
|-------|--------|----------|
| S_index = exp(-R_norm²) quantifies score ceiling compression | BUILD_ON | Polo et al. arXiv:2602.16763 (Bayesian R²=0.884) |
| Score compression predicts reduced generalization to shifted test sets | BUILD_ON | Recht et al. 2019 (ImageNet, 1200+ citations) |
| Test set contamination inflates apparent benchmark performance | BUILD_ON | lm-sys/llm-decontaminator; ConStat eth-sri |
| Domain-specific signals are independently computable from APIs | BUILD_ON | PWC API; OpenML Python client; ConStat; evaleval |
| No cross-domain benchmark health scoring system exists | **PROVE_NEW** | Phase 1 gap analysis |
| BCBHS can prospectively predict collapse ≥12 months in advance | **PROVE_NEW** | No prior prospective validation study |

**Phase 2B–4 Focus:** Only PROVE_NEW claims require experimental sub-hypotheses.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under heterogeneous ML benchmarks spanning CV, NLP, and tabular domains (Papers With Code + OpenML corpora), if we compute domain-specific health estimators H_d(B,t) — robustness gap (CV), contamination-adjusted S_index via ConStat (NLP), block-bootstrapped Kendall τ rank stability (tabular) — and calibrate these into a shared Cox proportional hazards model (controlling for benchmark age, submission volume, model scale growth trend), then the resulting BCBHS(B,t) will predict time-to-discriminative-collapse T(B) — operationalized as the first quarter where expected Kendall τ(ranking_t, ranking_{t+Δ}) > 0.90 with bootstrap CI — with C-index ≥ 0.70 and lowest-quintile benchmarks showing ≥2× hazard ratio for collapse within 24 months, because benchmark health degrades through domain-specific measurable signals whose shared hazard calibration structure enables prospective early warning ≥12 months before community consensus.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in time-to-discriminative-collapse between benchmarks in the lowest BCBHS quintile and all other benchmarks after controlling for age, submission volume, and model scale growth (Cox model hazard ratio = 1.0, p > 0.05).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Papers With Code Leaderboard Panel + OpenML Benchmark Panel (standard) | Papers With Code provides time-series submission data across 3000+ CV and NLP benchmarks spanning 2018–2025. OpenML provides 21,000+ tabular datasets. Together they cover all three target domains with sufficient history for collapse event detection. |
| **Model** | Cox Proportional Hazards Model (domain-stratified) + CFA for invariance testing | Cox PH model directly tests the core survival prediction claim. Domain stratification handles baseline hazard heterogeneity. CFA tests measurement invariance for latent universality claim. |

**Dataset Details:**
- Source: Papers With Code API (paperswithcode.com/api); OpenML Python client (openml-python)
- Path: External APIs — no local storage required for metadata; leaderboard CSVs downloadable

**Model Details:**
- Type: survival analysis + structural equation modeling
- Source: lifelines (Python); semopy or lavaan-equivalent for CFA; scikit-learn for baseline models

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| S_index (slope-only for NLP) | Bayesian R²=0.884 (retrospective) | 60 LLM benchmarks | LLM-only; no prospective validation; no cross-domain generalization |
| Roelofs 2019 overfitting measurement | ~11% accuracy drop on CIFAR-10 retest | CIFAR-10, ImageNet (CV only) | CV-only; retrospective; no prediction framework |
| Score variance + improvement slope (naive baseline) | Unknown — key baseline to beat | Papers With Code (proposed) | No domain-specific signals; no survival analysis framing |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | PWC + OpenML contain ≥20 confirmed collapse events for survival model training | PWC has 3000+ benchmarks × 6 years panel; est. 40-60 events (MMLU, SQuAD, CIFAR-10, GLUE sub-tasks) | Insufficient power; restrict to well-documented benchmarks; report as preliminary study |
| A2 | Discriminative collapse (Kendall τ > 0.90) is valid proxy for reduced scientific utility | If top-k rankings are statistically indistinguishable, new methods cannot demonstrate improvement | Ground truth misaligned; require alternative outcome definition (mediation test) |
| A3 | Domain-specific signals are causally upstream of collapse (leading, not concurrent) | Contamination precedes inflation then collapse (LLM benchmarks); robustness gap precedes score plateau (Recht 2019) | BCBHS is concurrent descriptor not prospective predictor; early-warning claim fails |
| A4 | Leaderboard submissions are sufficiently complete to reconstruct ranking distributions | PWC tracks 3000+ tasks; OpenML has standardized protocols; submission selectivity may bias rankings | Kendall τ estimates biased toward apparent stability; sensitivity analysis required |
| A5 | Shared Cox PH model is appropriately specified (PH assumption holds) | Domain stratification absorbs baseline hazard differences; Schoenfeld residuals test planned | Switch to AFT model; causal structure still testable |

### 1.6 Research Gap & Novelty

**Gap:** No cross-domain benchmark health scoring system exists covering CV, NLP, and tabular domains. Prior work (S_index, Polo et al. 2026) is LLM-specific and retrospective. Roelofs 2019 covers CV only, post-hoc. No prior work uses survival analysis on Papers With Code + OpenML panel data for prospective benchmark lifecycle prediction.

**Novelty:** First application of survival analysis to benchmark lifecycle prediction on panel leaderboard data. First cross-domain framework with domain-calibrated feature extractors unified via shared hazard calibration. Key conceptual reframe: 'universal benchmark health' = shared risk prediction structure (not a single formula). Two-stage architecture separates domain-specific signal extraction from cross-domain hazard calibration.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Domain-Specific Health Signal Existence & Discriminability**

**Type:** EXISTENCE
**Statement:** Under ML benchmarks with structured leaderboard submissions (Papers With Code CV+NLP, OpenML tabular, ≥20 submissions, ≥2 years history), if we compute domain-specific health estimators H_d(B, t-24mo) — robustness gap for CV, contamination-adjusted S_index for NLP, block-bootstrapped Kendall τ for tabular — then these signals will show statistically significant differences (Mann-Whitney U p<0.05, Cohen's d>0.5) between benchmarks confirmed saturated vs. healthy at t, because benchmark over-optimization creates measurable domain-specific degradation signals that precede community-recognized saturation.

**Rationale:** This is the foundation hypothesis validating that BCBHS features contain signal. Without discriminable domain-specific signals at t-24 months, neither the Cox model nor the early-warning claim is viable. Establishes the existence of the phenomenon before mechanism testing.

**Variables:**
- Independent: H_d(B,t) per domain (robustness gap / contamination-adjusted S_index / Kendall τ)
- Dependent: Binary saturation label (confirmed saturated τ>0.90 vs. healthy τ<0.70 at t)
- Controlled: Benchmark age, submission volume, domain type (stratification)

**Verification Protocol:**
1. Construct benchmark panel from PWC API (CV+NLP, 2018-2025) and OpenML (tabular)
2. Label benchmarks as saturated (τ>0.90) vs. healthy (τ<0.70) at each time point t
3. Compute H_d(B, t-24mo) for each domain using ConStat (NLP), robustness gap (CV), block-bootstrapped Kendall τ (tabular)
4. Mann-Whitney U test between saturated/healthy groups per domain; compute Cohen's d
5. AUC evaluation for each domain-specific signal in binary saturation classification

**Success Criteria (PoC: Direction-based):**
- Primary: Mann-Whitney U p<0.05 AND Cohen's d>0.5 in at least 2 of 3 domains
- Secondary: AUC >0.70 per domain-specific signal; signals at t-24mo show earlier separation than t-12mo

**Failure Response:** IF fails → PIVOT: reassess whether domain-specific signals are concurrent rather than leading; explore alternative feature operationalizations

**Dependencies:** None (foundation)

**Source:** Phase 2A Section 1.3 Step 1-2; SH1 (sh1_existence); Prediction P1

---
**H-M1: Benchmark Over-Optimization → Score Compression (Causal Step 1)**

**Type:** MECHANISM
**Statement:** Under ML benchmarks with ≥20 submissions and ≥2 years history, if submission count accumulates beyond a critical threshold (empirically estimated per benchmark), then score variance in top-k models will fall below 1.5σ_measurement for ≥2 consecutive quarters, because models increasingly overfit test-set statistical properties rather than generalizing, compressing the discriminative score distribution.

**Rationale:** Tests the first link in the causal chain: that high submission volume causes measurable score compression. This is the mechanism connecting benchmark popularity to degradation. Required before establishing that domain-specific signals emerge from this compression.

**Variables:**
- Independent: Cumulative submission count trajectory per benchmark
- Dependent: Score variance in top-k models per quarter; compression indicator (variance < 1.5σ threshold)
- Controlled: Benchmark age, model scale growth trend

**Verification Protocol:**
1. Extract per-benchmark submission time series from Papers With Code API
2. Compute score variance of top-10 models per benchmark per quarter (2018-2025)
3. Estimate σ_measurement per benchmark from repeated submission scores
4. Apply compression threshold: variance < 1.5σ_measurement for ≥2 consecutive quarters
5. Granger causality test: submission count → score compression (lag analysis)

**Success Criteria (PoC):**
- Primary: Score compression events co-occur with high submission counts (Spearman ρ >0.4, p<0.05)
- Secondary: Granger causality p<0.05 for submission count → compression (2-quarter lag)

**Failure Response:** IF fails → EXPLORE: test alternative compression thresholds; check if domain-specific variation explains null result

**Dependencies:** H-E1 (existence validated)

**Source:** Phase 2A Section 1.3 Step 1; causal_step 1

---
**H-M2: Score Compression → Domain-Specific Degradation Signals (Causal Step 2)**

**Type:** MECHANISM
**Statement:** Under benchmarks showing score compression (H-M1 confirmed), if compression is present, then domain-specific degradation signals — robustness gap widening (CV), contamination probability increase (NLP), premature rank correlation stabilization (tabular) — will emerge significantly earlier than discriminative collapse, providing measurable t-24 month leading indicators.

**Rationale:** Tests that score compression triggers domain-specific observable signals — the second causal link. Validates that H_d features are mechanistically downstream of over-optimization, not independent phenomena. Critical for establishing BCBHS features as legitimate causal proxies.

**Variables:**
- Independent: Score compression indicator (from H-M1)
- Dependent: H_d signal magnitude per domain at t-24mo relative to collapse event
- Controlled: Domain type, benchmark age

**Verification Protocol:**
1. Filter benchmarks where H-M1 compression confirmed
2. Measure H_d signal onset time relative to collapse event E(B,t) for each domain
3. Test temporal ordering: does H_d signal precede collapse by ≥12 months in majority of cases
4. Compare H_d signal magnitude in compressed vs. non-compressed benchmarks (Mann-Whitney U)
5. Assess domain-specific signal emergence patterns via survival-style event timing analysis

**Success Criteria (PoC):**
- Primary: H_d signals emerge significantly earlier (≥12mo) than collapse in ≥60% of confirmed events
- Secondary: H_d magnitude significantly higher in compressed vs. non-compressed benchmarks (p<0.05)

**Failure Response:** IF fails → EXPLORE: document as limitation (signals concurrent not leading); retain H-M3/M4 as separate testable claims

**Dependencies:** H-M1

**Source:** Phase 2A Section 1.3 Step 2; causal_step 2

---
**H-M3: Shared Hazard Calibration — Cox Model Cross-Domain Prediction (Causal Step 3)**

**Type:** MECHANISM
**Statement:** Under the BCBHS framework with domain-stratified Cox PH model (trained ≤2022, tested 2023-2025), if domain-specific H_d signals share partial metric invariance (CFA: configural+metric), then a shared Cox model will achieve C-index ≥0.70 with ΔC-index ≥0.05 over slope+variance+age baseline, and leave-one-domain-out evaluation will show positive transfer (ΔC-index ≥0.03), because the shared hazard calibration structure transcends domain-specific manifestations.

**Rationale:** Tests the core novel claim — that a single shared model can calibrate domain-specific signals into a unified risk score. This is the 'universal = shared hazard structure' reframe. Directly tests whether the two-stage BCBHS architecture adds value over domain-specific baselines.

**Variables:**
- Independent: BCBHS(B,t) from domain-stratified Cox PH model
- Dependent: C-index on 2023-2025 test set; LODO ΔC-index vs. domain-specific baseline
- Controlled: Domain stratification in Cox model; time-varying confounds

**Verification Protocol:**
1. Train domain-stratified Cox PH on ≤2022 (benchmark × quarter) panel with BCBHS H_d features + confounds
2. Compute Harrell's C-index on 2023-2025 held-out benchmarks
3. Nested ablation: slope → slope+variance → slope+variance+age → full BCBHS (report ΔC-index each step)
4. CFA measurement invariance testing: configural → metric → scalar across CV+NLP domains
5. Leave-one-domain-out: train on 2 domains, evaluate on held-out domain; compare vs. domain-specific Cox
6. Schoenfeld residuals test for PH assumption validity

**Success Criteria (PoC):**
- Primary: C-index ≥0.70 on 2023-2025 test set; ΔC-index ≥0.05 over slope+variance+age baseline
- Secondary: Hazard ratio ≥2.0 for lowest-quintile BCBHS benchmarks; LODO ΔC-index ≥0.03

**Failure Response:** IF fails → PIVOT: try AFT model if PH assumption violated; report partial metric invariance as honest finding; restrict to best-performing domain

**Dependencies:** H-M2

**Source:** Phase 2A Section 1.3 Step 3; Prediction P1, P3; causal_step 3

---
**H-M4: Early Warning Window — ≥12 Month Lead Time (Causal Step 4)**

**Type:** MECHANISM
**Statement:** Under the validated BCBHS framework (H-M3 confirmed), if the pre-registered Youden's J threshold (optimized on ≤2022 training folds) is applied prospectively to 2023-2025 benchmarks, then median lead time between first BCBHS threshold crossing and discriminative collapse event will be ≥12 months in both CV and NLP domains, with ≥70% of collapse events preceded by threshold crossing, because benchmark health degrades along a gradual trajectory that BCBHS signals capture 12-24 months before community consensus.

**Rationale:** Validates the practical utility claim — that BCBHS provides actionable early warning. The 12-month threshold is motivated by the observed ~18-month community consensus lag in MMLU and ImageNet cases. This hypothesis determines whether BCBHS can actually enable proactive benchmark replacement.

**Variables:**
- Independent: BCBHS threshold crossing time (pre-registered Youden's J on ≤2022 data)
- Dependent: Lead time = months(threshold crossing → collapse event E(B,t)); coverage = % collapse events preceded
- Controlled: Domain type; threshold sensitivity (IQR reported)

**Verification Protocol:**
1. Pre-register Youden's J threshold on ≤2022 training folds (maximize sensitivity+specificity for collapse detection)
2. Apply threshold to 2023-2025 benchmarks; record first crossing time per benchmark
3. Compute lead time distribution for benchmarks that subsequently experienced collapse
4. Kaplan-Meier analysis of lead time distribution; stratify by domain (CV vs. NLP)
5. Compute coverage: % of 2023-2025 collapse events preceded by BCBHS threshold crossing
6. Threshold sensitivity analysis: vary threshold ±20% from Youden's J; report IQR of lead times

**Success Criteria (PoC):**
- Primary: Median lead time ≥12 months in both CV and NLP
- Secondary: ≥70% of collapse events preceded by threshold crossing; IQR reported

**Failure Response:** IF fails → EXPLORE: document lead time distribution; report as 'insufficient for 12-month planning horizon' and adjust practical utility claim; retain mechanistic findings from H-M1–H-M3

**Dependencies:** H-M3

**Source:** Phase 2A Section 1.3 Step 4; Prediction P2; causal_step 4

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | AUC >0.70 in ≥2 domains; Mann-Whitney p<0.05; Cohen's d>0.5 | STOP — reassess entire hypothesis |
| H-M1 | MUST_WORK | Spearman ρ >0.4 submission→compression; Granger causality p<0.05 | EXPLORE alternative compression thresholds |
| H-M2 | SHOULD_WORK | H_d signals at t-24mo precede collapse in ≥60% of events | Document as limitation; proceed to H-M3 |
| H-M3 | MUST_WORK | C-index ≥0.70; ΔC-index ≥0.05 over baseline; LODO ΔC-index ≥0.03 | PIVOT to AFT model or domain-local models |
| H-M4 | SHOULD_WORK | Median lead time ≥12 months in CV and NLP; ≥70% coverage | Document lead-time limitation; retain mechanistic findings |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1 | 2 weeks |
| Phase 2: Mechanisms | H-M2 | 1 week |
| Phase 2: Mechanisms | H-M3 | 1 week |
| Phase 2: Mechanisms | H-M4 | 1 week |

**Total Duration:** 7 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1 — Insufficient Collapse Events (from A1)**
- Source: A1 (PWC+OpenML must contain ≥20 confirmed events)
- Description: If panel data yields <20 confirmed collapse events in training period, Cox model will be underpowered; latent factor model underfitted
- Severity: HIGH | Likelihood: MEDIUM
- Affected Hypotheses: H-E1 (binary labeling), H-M3 (Cox model training), H-M4 (lead time distribution)

**Risk R2 — Ground Truth Validity (from A2)**
- Source: A2 (Kendall τ > 0.90 threshold validity)
- Description: If τ>0.90 threshold does not correlate with actual research impact reduction, experiments measure the wrong outcome; all results become uninterpretable
- Severity: HIGH | Likelihood: LOW-MEDIUM
- Affected Hypotheses: H-E1, H-M1, H-M2, H-M3, H-M4 (all depend on collapse label)

**Risk R3 — Signal Timing: Concurrent not Upstream (from A3) — CRITICAL**
- Source: A3 (domain-specific signals causally upstream of collapse)
- Description: If robustness gap, contamination probability, and rank stability emerge simultaneously with collapse rather than ≥12 months before, BCBHS becomes a concurrent descriptor rather than a prospective predictor; entire early-warning claim invalidated
- Severity: CRITICAL | Likelihood: MEDIUM
- Affected Hypotheses: H-M2 (causal timing), H-M4 (early warning), entire prospective claim

**Risk R4 — Submission Completeness Bias (from A4)**
- Source: A4 (leaderboard submissions sufficiently complete)
- Description: Only competitive results are submitted to PWC/OpenML, creating right-skewed rank distributions; Kendall τ stability may appear artificially high, inflating apparent benchmark health
- Severity: HIGH | Likelihood: MEDIUM
- Affected Hypotheses: H-E1 (signal discriminability), H-M3 (C-index estimation)

**Risk R5 — Cox PH Assumption Violation (from A5)**
- Source: A5 (proportional hazards assumption holds)
- Description: If Schoenfeld residuals indicate time-varying hazard ratios, the shared Cox model is misspecified; core survival analysis framework invalid in its current form
- Severity: MEDIUM | Likelihood: LOW-MEDIUM
- Affected Hypotheses: H-M3 (Cox model), H-M4 (lead time analysis)

**Risk R6 — ConStat Generalizability (additional)**
- Source: Data infrastructure assumption
- Description: ConStat contamination estimates validated for LLM benchmarks; application to CV benchmarks may produce unreliable estimates
- Severity: MEDIUM | Likelihood: LOW (by design, ConStat restricted to NLP)
- Affected Hypotheses: H-E1 (NLP signal only)

### Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Insufficient collapse events | A1 | H-E1, H-M3, H-M4 | HIGH |
| R2: Ground truth validity | A2 | All (H-E1 through H-M4) | HIGH |
| R3: Signal timing concurrent | A3 | H-M2, H-M4, full prospective claim | CRITICAL |
| R4: Submission completeness bias | A4 | H-E1, H-M3 | HIGH |
| R5: Cox PH assumption violation | A5 | H-M3, H-M4 | MEDIUM |
| R6: ConStat generalizability | Infrastructure | H-E1 (NLP component) | MEDIUM |

### Mitigation Strategies

**R1 — Insufficient Collapse Events**
1. Prevention: Pre-register power analysis before data collection; estimate event count from published benchmark lists
2. Detection: During data construction, count (benchmark × quarter) events with τ>0.90 threshold; if <20, trigger mitigation
3. Response:
   - PIVOT: Use (benchmark × quarter) panel observations to multiply effective N; lower threshold to τ>0.85 with sensitivity analysis
   - SCOPE: Restrict analysis to well-documented benchmarks (MMLU, SQuAD, CIFAR-10, GLUE subtasks) and report as preliminary
   - Early Warning: Event count <20 during data preparation phase triggers scope restriction

**R2 — Ground Truth Validity**
1. Prevention: Pre-register τ>0.90 threshold with justification; include auxiliary validation against community consensus dates
2. Detection: Test whether labeled collapse events predict publication entropy reduction for that benchmark
3. Response:
   - PIVOT: If τ>0.90 shows no correlation with research impact, optimize threshold via Youden's J against community retirement dates
   - SCOPE: Report τ>0.90 as operational definition and note sociological validation gap

**R3 — Signal Timing Concurrent (CRITICAL)**
1. Prevention: Strict temporal design — measure H_d signals ONLY at t-24mo and t-12mo; never at t (concurrent)
2. Detection: Compare signal AUC at t-24mo vs. t-12mo vs. t; if AUC at t-24mo ≈ random, signals are concurrent
3. Response:
   - PIVOT: Reframe from "prospective predictor" to "concurrent health monitor"; report as negative result for early-warning; retain mechanistic findings
   - ABORT: If AUC at t-24mo <0.55 in all domains, early-warning claim is unsupported; document and proceed only with descriptive analysis
   - Early Warning: AUC at t-24mo <0.60 in ≥2 domains during H-E1 execution

**R4 — Submission Completeness Bias**
1. Prevention: Use OpenML as complementary source (standardized evaluation protocols, less selection bias)
2. Detection: Compare rank stability estimates between PWC and OpenML for tabular benchmarks; large divergence indicates bias
3. Response:
   - PIVOT: Impute missing submissions using model family submission patterns; sensitivity analysis with ±10% imputation
   - SCOPE: Flag benchmarks with <50% estimated submission coverage; exclude from primary analysis

**R5 — Cox PH Assumption Violation**
1. Prevention: Include domain stratification in Cox model (absorbs baseline hazard differences); use time-varying covariates
2. Detection: Schoenfeld residuals test (global and per-variable); global p>0.05 required
3. Response:
   - PIVOT: Switch to Accelerated Failure Time (AFT) model; causal structure still testable
   - SCOPE: Report PH violation as limitation; note that AFT model results are equivalent for substantive conclusions

**R6 — ConStat Generalizability**
1. Prevention: ConStat restricted to NLP benchmarks by design; CV uses robustness gap (no ConStat)
2. Detection: N/A — restricted by design
3. Response: Already mitigated by domain-specific signal architecture

### Risk Summary

| ID | Risk | Source | Severity | Affected | Primary Mitigation |
|----|------|--------|----------|----------|-------------------|
| R1 | Insufficient collapse events | A1 | HIGH | H-E1, H-M3, H-M4 | Pre-register power analysis; use panel (B×t) observations |
| R2 | Ground truth validity | A2 | HIGH | All hypotheses | Auxiliary validation vs. community consensus dates |
| R3 | Signal timing concurrent | A3 | CRITICAL | H-M2, H-M4 | Strict t-24mo temporal measurement; AUC early detection |
| R4 | Submission completeness | A4 | HIGH | H-E1, H-M3 | OpenML complement; imputation sensitivity analysis |
| R5 | Cox PH violation | A5 | MEDIUM | H-M3, H-M4 | Schoenfeld residuals test; AFT fallback |
| R6 | ConStat scope | Infrastructure | MEDIUM | H-E1 NLP | Restricted to NLP by design |

Critical Risks: 1 (R3)
High Risks: 3 (R1, R2, R4)
Medium Risks: 2 (R5, R6)

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 5 Hypotheses
═══════════════════════════════════════════════════════════════

[Level 0 — Root: No prerequisites]
    H-E1 (EXISTENCE — Domain Signal Existence & Discriminability)
         │
         ▼  [Gate 1: MUST_WORK — if fail → STOP, reassess entire hypothesis]
[Level 1 — Core Mechanism Entry]
    H-M1 ← H-E1  (Benchmark Over-Optimization → Score Compression)
         │
         ▼  [Gate 1b: MUST_WORK — if fail → EXPLORE alternative compression operationalizations]
[Level 2 — Signal Timing]
    H-M2 ← H-M1  (Score Compression → Domain-Specific Degradation Signals)
         │
         ▼  [Gate 2a: SHOULD_WORK — fail narrows prospective claim; does not block H-M3]
[Level 3 — Shared Calibration]
    H-M3 ← H-M2  (Shared Hazard Calibration — Cox Model Cross-Domain Prediction)
         │
         ▼  [Gate 2b: MUST_WORK — C-index ≥0.70 required; if fail → PIVOT to AFT model]
[Level 4 — Early Warning]
    H-M4 ← H-M3  (Early Warning Window — ≥12 Month Lead Time)
         │
         ▼  [Gate 3: SHOULD_WORK — fail narrows practical utility claim]

═══════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
All sequential — no parallelization (incremental mode)
═══════════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Fail Action |
|-------|-----------|---------------|-----------|-------------|
| 0 | H-E1 | None | MUST_WORK | STOP — reassess entire hypothesis |
| 1 | H-M1 | H-E1 | MUST_WORK | EXPLORE alternative operationalizations |
| 2 | H-M2 | H-M1 | SHOULD_WORK | Document as limitation; proceed to H-M3 |
| 3 | H-M3 | H-M2 | MUST_WORK | PIVOT to AFT model; or restrict to best domain |
| 4 | H-M4 | H-M3 | SHOULD_WORK | Document lead-time limitation; retain mechanistic findings |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 5 Hypotheses | Total: 7 weeks
═══════════════════════════════════════════════════════════════════════
Phase/Hypothesis   │ W1-2    │ W3-4    │ W5      │ W6      │ W7
───────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
PHASE 1: Foundation
  H-E1             │ ████████│         │         │         │
  [Gate 1]         │        ◆│         │         │         │
───────────────────┼─────────┼─────────┼─────────┼─────────┼─────────
PHASE 2: Mechanisms
  H-M1             │         │ ████████│         │         │
  H-M2             │         │         │ ████    │         │
  H-M3             │         │         │         │ ████    │
  H-M4             │         │         │         │         │ ████
  [Gate 2]         │         │        ◆│         │         │
  [Gate 3]         │         │         │         │         │    ◆
═══════════════════════════════════════════════════════════════════════
Legend: ████ = Active work  │  ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

Total Duration: 7 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (H-M4)

Slack Available: 0 weeks (fully sequential chain)

MUST_WORK Gates (blockers): H-E1, H-M1, H-M3
SHOULD_WORK Gates (non-blockers): H-M2, H-M4

Risk Checkpoint (R3 temporal test): During H-E1 week 2
  → If AUC at t-24mo < 0.60 in ≥2 domains → STOP, pivot to concurrent monitor framing
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Hypotheses: 5
  - Existence: 1 (H-E1)
  - Mechanism: 4 (H-M1 to H-M4)
  - Condition: 0 (not needed)

Verification Phases: 2
  1. Foundation (H-E1) — 2 weeks
  2. Mechanisms (H-M1 through H-M4) — 5 weeks

Data Sources Required:
  - Papers With Code API (CV + NLP leaderboards, 2018–2025)
  - OpenML Python client (tabular, 21,000+ datasets)
  - ConStat (eth-sri) for NLP contamination estimates
  - evaleval/benchmark-saturation for S_index cross-validation

Statistical Tools: lifelines (Cox PH), semopy/lavaan-equiv (CFA), scikit-learn (baselines)

Total Duration: 7 weeks | Critical Path: 7 weeks
Execution Mode: Sequential chain (all MUST_WORK dependencies)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

**Step 1:** Execute H-E1 (Foundation — domain signal existence) — Week 1-2
  → R3 temporal test at Week 2: AUC at t-24mo; if <0.60 in ≥2 domains → STOP
**Step 2:** Evaluate Gate 1 (MUST_WORK) → If pass, proceed
**Step 3:** Execute H-M1 (Score compression mechanism) — Week 3-4
**Step 4:** Evaluate Gate 1b (MUST_WORK) → If pass, proceed
**Step 5:** Execute H-M2 (Signal timing & causal ordering) — Week 5
**Step 6:** Evaluate Gate 2a (SHOULD_WORK) → Document result; proceed regardless
**Step 7:** Execute H-M3 (Shared Cox model, C-index validation) — Week 6
**Step 8:** Evaluate Gate 2b (MUST_WORK) → If fail, PIVOT to AFT model
**Step 9:** Execute H-M4 (Early warning lead time) — Week 7
**Step 10:** Evaluate Gate 3 (SHOULD_WORK) → Document lead time result
**Final:** Verification complete → Phase 2C experiment design per hypothesis

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** BCBHS(B,t) predicts time-to-discriminative-collapse with C-index ≥0.70 and provides ≥12 months early warning across CV and NLP benchmark domains, because domain-specific degradation signals share a common latent hazard calibration structure detectable before community consensus.

**Supporting Evidence:**
1. Benchmark over-optimization empirically established: score compression documented in MMLU, ImageNet, CIFAR-10 (Recht 2019, Roelofs 2019)
2. Domain-specific signals computable from existing APIs: ConStat (eth-sri), evaleval, PWC robustness gap methodology
3. Community consensus lag documented: MMLU ~18 months, ImageNet post-2018 patterns
4. Panel survival analysis resolves small-N: (benchmark × quarter) observations multiply effective N

**Strengths:**
- Theoretically grounded in established overfitting literature
- Pre-registered thresholds prevent post-hoc rationalization
- Two-stage architecture cleanly separates domain extraction from cross-domain calibration

**Expected Outcomes:**
- P1: C-index ≥0.70 on 2023-2025 test; HR ≥2× for lowest BCBHS quintile
- P2: Median lead time ≥12 months in CV and NLP
- P3: Partial metric invariance (CFI ≥0.90 for configural+metric); LODO ΔC-index ≥0.03

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in time-to-discriminative-collapse between benchmarks in the lowest BCBHS quintile and all others after controlling for age, submission volume, and model scale growth (HR = 1.0, p > 0.05).

**Counter-Arguments:**
1. Domain-specific signals may be concurrent symptoms, not upstream predictors — causal direction unverified
2. Slope+variance+age baseline may explain apparent predictive signal (ΔC-index < 0.02)
3. Measurement invariance across domains is empirically unverified — metric invariance may be rejected
4. Small-N (~20-40 test events) yields wide C-index CI — apparent ≥0.70 may be noise

**Potential Failure Points:**
- R3 (CRITICAL): Signal timing concurrent → prospective claim invalidated
- R1: Insufficient events → Cox model underpowered
- R4: Submission bias → inflated apparent rank stability

**Conditions Under Which H0 Would Be Supported:**
- C-index < 0.65 on 2023-2025 test set
- ΔC-index < 0.02 over slope+variance+age baseline
- AUC at t-24mo < 0.60 in ≥2 domains (concurrent signal detection)

### 6.3 Synthesis

The verification plan is designed to robustly resolve this dialectic. H-E1's strict temporal test (AUC at t-24mo vs. t-12mo vs. t) directly addresses R3 before committing to Cox model development. Nested ablation in H-M3 isolates BCBHS contribution from baseline confounds. Pre-registered thresholds ensure honest evaluation regardless of direction.

**Resolution Path:**
1. H-E1 temporal analysis → determines concurrent vs. upstream (resolves antithesis R3)
2. H-M1 Granger causality → establishes submission→compression mechanism
3. H-M3 nested ablation → isolates BCBHS signal from confounds (resolves antithesis R2 baseline concern)
4. Pre-registered Youden's J threshold → prevents lead-time threshold fishing

**Outcome Mapping:**
| Scenario | H0 Status | Publication Value |
|----------|-----------|-------------------|
| All MUST_WORK pass, lead time ≥12mo | Rejected | Full BCBHS prospective predictor claim |
| H-M3 passes, H-M4 fails (lead time <12mo) | Partially rejected | BCBHS as concurrent health monitor; lead time insufficient |
| H-M1/M3 fails, H-E1 passes | Not rejected | Domain signals exist but no shared structure; domain-local models only |
| H-E1 fails | Not rejected | Signals not discriminable; fundamental reframe needed |

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Domain signals discriminable at t-24mo | Signals concurrent with collapse | H-E1 AUC at t-24mo vs. t test |
| Mechanism Step 1 | Submission→compression causal | Spurious correlation with age | H-M1 Granger causality analysis |
| Mechanism Step 2 | Compression→signals causal timing | Signals emerge simultaneously | H-M2 temporal onset analysis |
| Shared structure | Partial metric invariance sufficient | Domains fundamentally incomparable | H-M3 CFA + LODO evaluation |
| Early warning | ≥12 months median lead time | Lead time <6 months (impractical) | H-M4 Kaplan-Meier analysis |

**Overall Robustness Score:** Medium-High (0.78 confidence, CRITICAL risk R3 is addressable by design)

**Confidence in Verification Plan:** 0.78 — design is scientifically sound; outcome is genuinely uncertain

---

## 7. Executive Summary & Appendices

### 7.1 Executive Summary

**Main Hypothesis:** H-BCBHS-v1 — BCBHS predicts benchmark discriminative collapse via domain-calibrated Cox survival model
- ID: H-BCBHS-v1 | Confidence: 0.78 | Mode: Incremental

**Verification Structure:**
- Sub-Hypotheses: 5 total — H-E1 (Existence) + H-M1–H-M4 (Mechanism chain)
- Phases: 2 over 7 weeks | Gates: 5 decision points (3 MUST_WORK, 2 SHOULD_WORK)
- Scope Reduction: 33% (4 of 6 claims BUILD_ON, not re-verified)
- Transfer Validation: Not required (no cross-domain mechanism transfer)

**Risk Assessment:** MEDIUM-HIGH
- Critical: R3 (signal timing concurrent vs. upstream) — tested in H-E1 Week 2
- High: R1 (event count), R2 (ground truth validity), R4 (submission bias)

**Immediate Action:** Begin Phase 2C/3/4 with H-E1; temporal AUC test is critical go/no-go checkpoint

### 7.2 Final Summary & Conclusions

**Key Achievements:**
- 5 sub-hypotheses spanning 2 phases, 7 weeks, 5 gate decision points
- H0 explicitly addressed: no BCBHS signal after confound control
- CRITICAL risk R3 built into H-E1 design as early go/no-go checkpoint

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Compute H_d(B, t-24mo) for all domains; test discriminability vs. healthy benchmarks
- Gate 1 (MUST_WORK): AUC>0.70 in ≥2 domains, Mann-Whitney U p<0.05, Cohen's d>0.5
- R3 checkpoint: AUC at t-24mo vs. t-12mo vs. t — determines prospective vs. concurrent framing

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: Submission count → score compression (Granger causality)
- H-M2: Compression → domain-specific signal emergence (temporal ordering)
- H-M3: Shared Cox model C-index ≥0.70, ΔC-index ≥0.05, CFA invariance (MUST_WORK)
- H-M4: ≥12 month median lead time (SHOULD_WORK)

**Critical Decision Points:**
1. Gate 1 (H-E1 MUST_WORK): AUC >0.70 + p<0.05 → FAIL means STOP, reframe hypothesis
2. R3 Check (within H-E1): AUC at t-24mo < 0.60 → PIVOT to concurrent monitor framing
3. Gate 2b (H-M3 MUST_WORK): C-index ≥0.70 → FAIL means PIVOT to AFT or domain-local models
4. Gate 3 (H-M4 SHOULD_WORK): Lead time ≥12mo → FAIL narrows practical utility claim

**Open Questions:**
- Does partial metric invariance hold across CV+NLP (sufficient for shared Cox model)?
- How many confirmed collapse events exist in PWC 2018–2025 for power analysis?
- Is Kendall τ > 0.90 the right threshold for discriminative collapse, or domain-optimized?
- Can ConStat contamination estimates be reliably applied to non-LLM NLP benchmarks?

**Recommendations:**
1. Immediate: Begin H-E1 data construction; pre-register power analysis and Youden's J threshold
2. Resource: Allocate 7 weeks for critical path; reserve 2-week buffer for API data issues
3. Risk Management: Execute R3 temporal test in H-E1 before investing in Cox model infrastructure

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: 03_refinement.yaml (ID: H-BCBHS-v1, schema v10.0.0, generated 2026-05-19)
- Key convergence: 15 exchanges, all 6 criteria met, VALIDATED status

**B. MCP Tool Usage Summary**
- Total MCP calls: 7 (4× scientificmethod, 1× collaborativereasoning, 3× structuredargumentation)
- Reasoning tools: Sequential thinking (H-E1, H-M chains), collaborative risk analysis, dialectical evaluation

**C. Established Facts (BUILD_ON — not re-verified)**
- S_index validity (Polo et al. arXiv:2602.16763)
- Score-generalization link (Recht et al. 2019)
- Contamination inflation (lm-sys/llm-decontaminator; ConStat)
- Domain signals computability (PWC API; OpenML; ConStat; evaleval)

---

## 10. Finalization Status

- verification_state.yaml: CREATED at docs/youra_research/20260519_mldpr/verification_state.yaml
- Pipeline tasks updated in Archon:
  - Phase 1 task: done
  - Phase 2B task (9fbb4c7a): done
  - Phase 2C task (f048366c): doing
- Hypothesis tasks created in Archon (project: 3e07f6ec):
  - H-E1 (5e812a14): READY, MUST_WORK, todo
  - H-M1 (82935e7d): NOT_STARTED, MUST_WORK, todo
  - H-M2 (a60c198c): NOT_STARTED, SHOULD_WORK, todo
  - H-M3 (5ab30226): NOT_STARTED, MUST_WORK, todo
  - H-M4 (64507c17): NOT_STARTED, SHOULD_WORK, todo

*Generated by YouRA Phase 2B | 2026-05-19*
