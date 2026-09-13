# Verification Plan: Automated Benchmark Saturation Detection

**Date:** 2026-08-28
**Hypothesis ID:** H-BenchmarkSaturationDetection-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under active benchmark leaderboard conditions (Papers With Code, 2018-2024), IF we detect saturation using dual metrics—score convergence (std top-5 <0.5% for 6 months) AND improvement velocity decay (<0.1 improvement/month for 6 months)—THEN detected saturation dates align with high-confidence expert consensus (±1 year, >70% agreement among responses rated ≥4/5 confidence), BECAUSE saturation is a multi-metric syndrome with observable leading indicators that precede paradigm shifts by >6 months, indicating internal benchmark exhaustion independent of external disruptions.

### 1.2 Alternative Hypothesis (H0)
There is no significant alignment between algorithmically detected saturation dates and expert consensus saturation dates (alignment <50% within ±1 year, or expert consensus weak with <50% agreement).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Papers With Code Leaderboard Snapshots (2018-2024) (standard) | Provides historical leaderboard data for saturation detection (ImageNet, GLUE, SQuAD). Timestamped submissions enable score convergence + velocity decay analysis. API access allows forward monitoring (2024-2025 predictions). |
| **Model** | Saturation Detection Algorithm (Dual-Metric Threshold) | Operationalizes saturation as score convergence (std <0.5% for 6mo) AND velocity decay (<0.1/mo for 6mo). Thresholds justified by ImageNet historical data (2015-2020 convergence patterns). |

**Dataset Details:**
- Source: Papers With Code public API + manual scraping for missing timestamps
- Path: https://paperswithcode.com/api/v1/benchmarks/

**Model Details:**
- Type: rule-based + statistical
- Source: Custom implementation: rolling window std(top-5 scores) + linear regression (score vs. time)

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Score-Only Saturation Detection | Single metric: std(top-5) <0.5% for 6mo (ignore velocity) | Historical benchmarks |
| Velocity-Only Saturation Detection | Single metric: velocity <0.1/mo for 6mo (ignore convergence) | Historical benchmarks |
| Expert Intuition Baseline | Survey responses without algorithmic detection (ground truth for P1) | Expert survey |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Expert consensus on saturation dates exists and is measurable (>70% high-confidence agreement within ±1 year) | ImageNet saturation timing likely has community consensus around 2017-2020 window (ResNets plateau → ViT arrival) | Ground truth validation collapses—must pivot to citation-based validation (SOTA mention decay in published papers) |
| A2 | Saturation is internal to benchmark (architectural exploration exhaustion), not purely driven by external paradigm shifts | Temporal hypothesis: saturation signals precede paradigm shifts by >6 months (E3 test) | Mechanism spuriously correlates with unrelated trends—saturation detector becomes lag indicator, not lead predictor |
| A3 | Papers With Code leaderboard snapshots (2018+) preserve sufficient historical data for retrospective validation | PWC archives major benchmarks, submission timestamps available for recent entries | Historical validation limited to post-2020 data, pre-2020 benchmarks excluded, sample size reduced |
| A4 | 'Main results' citations distinguish primary research usage from ablation/diagnostic usage | Papers typically declare benchmark used for 'main evaluation' vs. 'ablation study' in methods section | Citation drop metric conflates primary migration with total abandonment—MNIST control addresses this |
| A5 | Conference policies can incentivize rotation infrastructure adoption without enforcement mechanisms | Analogous to data/code availability statements—NeurIPS Benchmark Track could mandate rotation criteria disclosure | Infrastructure remains unused—contribution becomes academic exercise without real-world impact |

### 1.6 Research Gap & Novelty

**Key Innovation:** Rotation infrastructure layer—automated saturation detection with time-boxed validity periods and community coordination protocols. Treats benchmarks as consumables with lifecycle phases (analogous to drug approval cycles, software versioning), not permanent monuments.

**Differentiation from Prior Work:**
- Linzen et al. (2022 est.) DESCRIBES saturation problem. This work proposes automated DETECTION + rotation mechanisms (infrastructure layer).
- Hendrycks & Dietterich (2019) proposes ALTERNATIVE benchmarks (robustness paradigms). This work proposes how to SUNSET existing benchmarks and coordinate transitions.
- FAIR Principles (Wilkinson 2016) addresses data Findability, Accessibility, Interoperability, Reusability. This work adds Rotatability (FAIR-B framework extension).

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | SHOULD_WORK | H-E1 | READY |
| H-M2 | Mechanism | SHOULD_WORK | H-E1, H-M1 | READY |
| H-M3 | Mechanism | SHOULD_WORK | H-E1, H-M1, H-M2 | READY |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Data Availability and Expert Consensus Existence**

**Statement**: Papers With Code leaderboard data (2018-2024) exists with submission timestamps, AND expert consensus survey achieves ≥30 high-confidence (≥4/5) responses per benchmark.

**Rationale**:
This validates data infrastructure exists before attempting saturation detection. Without PWC data or expert consensus, primary validation (P1) collapses. Existence hypothesis is foundation for all mechanism tests.

**Variables**:
- Independent: Data source (PWC API snapshots 2018-2024)
- Dependent: Data completeness (submission count with timestamps), Expert response count (high-confidence ≥4/5)
- Controlled: Benchmark selection (ImageNet, GLUE, SQuAD), Survey distribution method

**Verification Protocol**:
1. Query PWC API for ImageNet/GLUE/SQuAD leaderboards, extract submission timestamps (2018-2024).
2. Count submissions with valid timestamps per benchmark, verify ≥100 entries/benchmark.
3. Distribute expert survey (50+ ML researchers, stratified vision/NLP, junior/senior).
4. Filter responses ≥4/5 confidence, count per benchmark, verify ≥30 responses/benchmark.

**Success Criteria** (PoC):
- Primary: ≥100 timestamped submissions/benchmark AND ≥30 high-confidence expert responses/benchmark
- Secondary: Survey completion rate >40%, response distribution balanced across domains

**Failure Response**:
- IF PWC data incomplete: PIVOT to citation-based validation (SOTA mention decay)
- IF expert consensus weak (<30 responses or <50% agreement): PIVOT to citation fallback per A1 assumption

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A P1 (primary prediction), sh1_existence

---

**H-M1: Score Convergence Detection**

**Statement**: Under active leaderboard conditions (PWC 2018-2024), IF leaderboard top-5 scores show convergence (std <0.5% for 6 months), THEN this signal precedes community migration, BECAUSE architectural exploration plateaus as remaining gains require exponentially more effort (diminishing returns).

**Rationale**:
First causal step in saturation mechanism. Score convergence is observable plateau visible before velocity decay. ImageNet 2015-2017 rapid convergence (6.7%→2.3%) followed by slow creep (2017-2020: 2.3%→1.8%) demonstrates measurable signal.

**Variables**:
- Independent: Rolling 6-month window of top-5 scores
- Dependent: Standard deviation of top-5 scores
- Controlled: Benchmark (ImageNet, GLUE), Score metric (top-5 error, avg score)

**Verification Protocol**:
1. Extract top-5 scores per month from PWC leaderboards (6-month rolling windows).
2. Compute std(top-5) for each window, identify first window where std <0.5%.
3. Record convergence date (first detection), compare with expert consensus dates (±1 year).
4. Verify convergence precedes velocity decay (H-M2) by ≥1 month.

**Success Criteria** (PoC):
- Primary: Convergence detected (std <0.5%) aligns with expert consensus ±1 year for ≥2/3 benchmarks
- Secondary: Convergence precedes velocity decay detection

**Failure Response**:
- IF convergence not detected or post-consensus: EXPLORE single-metric baseline, may indicate convergence alone insufficient

**Dependencies**: H-E1 (requires PWC data + expert consensus)

**Source**: Phase 2A Causal Step 1, P1 validation

---

**H-M2: Velocity Decay Detection**

**Statement**: Under saturating benchmark conditions, IF monthly improvement rate drops below threshold (<0.1 improvement/month for 6 months), THEN optimization space exhausts measurably, BECAUSE teams exhaust architectural variations and submission frequency declines.

**Rationale**:
Second causal step validating saturation syndrome. Velocity decay complements score convergence—GLUE velocity dropped from 15-point/year (2018-2019) to <2-point/year (2020-2022), SuperGLUE submissions dropped 40%. Dual-metric syndrome stronger than single signal.

**Variables**:
- Independent: Monthly score improvement (linear regression slope score vs. time)
- Dependent: Improvement velocity (points/month)
- Controlled: Benchmark, Regression window (6 months)

**Verification Protocol**:
1. Fit linear regression (score vs. time) for 6-month rolling windows.
2. Extract slope (improvement/month), identify first window where slope <0.1/mo.
3. Record velocity decay date, compare with expert consensus ±1 year.
4. Cross-check with H-M1: decay should follow or co-occur with convergence.

**Success Criteria** (PoC):
- Primary: Velocity decay detected (<0.1/mo) aligns with expert consensus ±1 year for ≥2/3 benchmarks
- Secondary: Decay follows convergence (H-M1) temporally

**Failure Response**:
- IF decay not detected or misaligned: EXPLORE velocity-only baseline, may indicate velocity threshold needs adjustment

**Dependencies**: H-E1 (requires PWC data), H-M1 (should follow convergence)

**Source**: Phase 2A Causal Step 2, P1 validation

---

**H-M3: Temporal Lead Time (Saturation Precedes Paradigm Shifts)**

**Statement**: Under benchmark lifecycle conditions, IF detected saturations (dual-metric) occur >6 months BEFORE external paradigm shift events (GPT-3 2020, ViT 2021, LLaMA 2023), THEN saturation signals are leading indicators of internal exhaustion, BECAUSE they distinguish internal benchmark exhaustion from external disruption artifacts.

**Rationale**:
Third causal step resolving correlation vs. causation tension. Temporal decomposition critical—if saturations cluster AFTER shifts, detector is lagging indicator of external change. If BEFORE, detector isolates internal mechanism. Provides 6-12 month predictive window for rotation.

**Variables**:
- Independent: Detected saturation dates (H-M1 + H-M2 combined)
- Dependent: Lead time (months between saturation and paradigm shift adoption)
- Controlled: Paradigm shift definition (GPT-3, ViT, LLaMA adoption via citation surge)

**Verification Protocol**:
1. Identify paradigm shift adoption dates (GPT-3 Jun 2020, ViT Oct 2021, LLaMA Feb 2023) via citation surge.
2. Compare detected saturation dates with shift dates, compute lead time (saturation - shift).
3. Count saturations with lead time >6 months (positive = saturation precedes).
4. Verify ≥60% saturations occur >6mo before shifts (P3 criterion).

**Success Criteria** (PoC):
- Primary: ≥60% detected saturations occur >6mo before paradigm shift adoption
- Secondary: Mean lead time >6 months (demonstrates predictive window)

**Failure Response**:
- IF saturations cluster POST-shift (<3mo lag): ABANDON temporal claim, saturations are artifacts not predictors

**Dependencies**: H-E1 (requires data), H-M1 (requires convergence dates), H-M2 (requires velocity dates)

**Source**: Phase 2A Causal Step 3, P3 (temporal prediction)

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
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | PWC data exists + ≥30 expert responses/benchmark | PIVOT to citation-based validation |
| H-M1 | SHOULD_WORK | Convergence (std <0.5%) aligns with consensus ±1y | EXPLORE score-only baseline |
| H-M2 | SHOULD_WORK | Velocity decay (<0.1/mo) aligns with consensus ±1y | EXPLORE velocity-only baseline |
| H-M3 | SHOULD_WORK | ≥60% saturations occur >6mo before paradigm shifts | ABANDON temporal claim |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 2C | Experiment Design (H-E1, H-M1, H-M2, H-M3) | 4-6 hours |
| Phase 3 | Implementation Planning (H-E1, H-M1, H-M2, H-M3) | 6-8 hours |
| Phase 4 | Coding & Validation (sequential: H-E1 → H-M1 → H-M2 → H-M3) | 12-16 hours |

**Total Duration:** 22-30 hours

---
