---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
status: complete
hypothesis_id: H-SatOnset-v1
created_at: "2026-08-21"
completedAt: "2026-08-21"
pipeline_project_id: "cb6df221-7e69-46e4-b45c-0b7f51d06368"
hypothesis_task_mapping:
  h-e1: "cb10be8e-ae57-4bdf-9216-39bcc06be1f8"
  h-m1: "12d967b0-0c06-4cc3-b00e-0af383811583"
  h-m2: "9ac08e5f-8d5c-4951-9815-4822846eace3"
  h-m3: "8725ea11-b0d0-4a30-9d8b-e5f8542a09ee"
---

# Verification Plan: Benchmark Saturation Onset Threshold (H-SatOnset-v1)

**Date:** 2026-08-21
**Hypothesis ID:** H-SatOnset-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under PwC leaderboard benchmark data (N=111 benchmarks with confirmed CoV and paper_count), if we apply PELT change-point detection to linearly detrended residual CoV values sorted by paper_count, then a statistically significant structural break (paper_count*) will be detected, because Goodhart saturation dynamics create a genuine regime shift from high-variance CoV (performance exploration) to low-variance CoV (ceiling compression) as paper counts cross the threshold.

### 1.2 Alternative Hypothesis (H0)

There is no statistically significant change-point in the CoV-vs-paper_count relationship in PwC data (permutation test p ≥ 0.05 and/or Brown-Forsythe p ≥ 0.05). The rho=−0.28 relationship is best described as a smooth monotonic trend without a regime shift.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Papers With Code Leaderboard Data — N=111 CoV-computed benchmarks (standard) | N=111 benchmarks with pre-computed CoV and paper_count are the direct empirical anchor; no new data loading required — derive.py output is the input |
| **Model** | PELT Change-Point Detection + Piecewise Linear Regression | PELT detects unknown-N change-points in 1D series; piecewise linear regression provides independent F-test validation; both operate on N=111 observations — computationally trivial |

**Dataset Details:**
- Source: paperswithcode/paperswithcode-data (GitHub, 932 stars)
- Path: Available via ingest_pwc.py (confirmed working from H-E1 v2)

**Model Details:**
- Type: Statistical analysis (no ML model training)
- Source: ruptures (deepcharles/ruptures, 2000+ stars), statsmodels, scipy

### 1.4 Baseline Methods (for comparison)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| OLS linear regression (CoV ~ paper_count, no change-point) | rho=−0.28, R²≈0.08 — explains ~8% of CoV variance | PwC N=111 benchmarks | Monotonic linear model cannot detect regime shifts; provides no retirement threshold |
| S_index (arXiv:2602.16763) | Validated on 60 LLM benchmarks; no paper_count* threshold reported | LLM benchmarks (not PwC internal) | Different domain; composite metric conflates paper_count and ceiling effects; no change-point analysis |
| Liao et al. 2022 CV-based saturation metric | 3,765 benchmarks, time-to-saturation in years; no paper_count* threshold | PwC + other sources | Time-based metric, not paper_count-based; aggregate trend, no individual threshold |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Pooled cross-sectional CoV values sorted by paper_count form a valid PELT input series after linear detrending | Linear detrending removes the global monotonic component (rho=−0.28), leaving residuals that detect structural breaks in dispersion | PELT detects heterogeneity between benchmark subpopulations rather than a saturation threshold; stratified analysis would reveal this |
| A2 | N=111 benchmarks is sufficient for reliable PELT change-point detection | VPWBS (arXiv:1906.11364): O_p(1/n) localization rate; with N=111, min_size=3, localization accuracy ≈ ±1 paper | Bootstrap CI width > 20 papers, indicating paper_count* estimate is too uncertain for policy use |
| A3 | PwC benchmark task_type metadata is accurate enough for stratification (N ≥ 20 per major stratum) | Phase 1 analysis: image_classification ~30, NLP/reading_comprehension ~40, object_detection ~15-20 | Object_detection stratum falls below N=20; use piecewise regression F-test only for that stratum |
| A4 | Goodhart saturation is the primary driver of CoV reduction, not metric heterogeneity | rho=−0.28 persists across diverse benchmark types; linear detrending controls for paper_count | Metric heterogeneity drives patterns; robustness check: repeat with score-normalized CoV |
| A5 | A single structural break adequately characterizes the CoV-vs-paper_count relationship | Parsimony: rho=−0.28 suggests one dominant transition; BIC-tuned penalty selects simpler models | PELT detects 2+ change-points; still interpretable — report all change-points |

### 1.6 Research Gap & Novelty

**Gap:** No prior work applies change-point detection to PwC-internal CoV-vs-paper_count series to identify an empirically grounded benchmark retirement threshold (paper_count*).

**Novelty:** First application of PELT change-point detection to PwC-internal CoV-vs-paper_count series. Reframes benchmark saturation from a continuous property (aggregate trend) to a discrete phase transition (detectable regime shift), enabling a quantitative retirement criterion. Differentiates from: Liao et al. 2022 (aggregate trends only), S_index (conflates paper_count and ceiling effects), nandomp/AI_Research_Dynamics (performance jumps ≠ CoV saturation, N=25 vs our N=111).

**Scope Reduction:** 67% — 4/6 claims are BUILD_ON (established; do not re-verify). Only 2 PROVE_NEW claims drive hypothesis generation.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Statement (Brief) | Gate | Prerequisites | Status |
|----|------|-------------------|------|---------------|--------|
| H-E1 | EXISTENCE | Structural break (paper_count*) detectable via PELT on N=111 PwC residual CoV (permutation p < 0.05) | MUST_WORK | None | READY |
| H-M1 | MECHANISM | Early-phase high CoV regime exists (paper_count < paper_count*: high-variance exploration) | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | Post-breakpoint variance compression confirmed (Brown-Forsythe p < 0.05, ratio < 1.0) | MUST_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | Goodhart mechanism specificity: variance reduction is directional (post < pre), not just a mean shift | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Structural Break Detection (Existence)**

**Type:** EXISTENCE
**Statement:** Under PwC N=111 benchmark data, if PELT change-point detection is applied to linearly detrended residual CoV sorted by paper_count, then a statistically significant structural break (paper_count*) will be detected (permutation test p < 0.05, paper_count* ∈ [10, 120]).

**Rationale:** This is the foundational PROVE_NEW claim: no prior work has detected paper_count* in PwC CoV-vs-paper_count data. Detection must precede all mechanism verification — if no structural break exists, the Goodhart regime-shift framing is falsified and H0 (smooth monotonic trend) is the supported description.

**Variables:**
- Independent: paper_count (count of result rows per benchmark in PwC data)
- Dependent: residual_CoV (CoV linearly detrended by paper_count; sorted ascending for PELT input)
- Controlled: Linear paper_count trend (removed via OLS); PELT penalty (BIC-tuned, sensitivity range [1,50])

**Verification Protocol:**
1. Load CoV and paper_count from derive.py output (N=111 confirmed benchmarks).
2. Fit OLS: CoV ~ paper_count; extract residuals (residual_CoV).
3. Sort residual_CoV by paper_count ascending; tune PELT penalty via elbow method.
4. Apply rpt.Pelt(model='l2', min_size=3).fit(residual_cov_sorted).predict(pen=bic_tuned).
5. Permutation test: shuffle paper_count labels ×1000, rerun PELT, compute p-value; bootstrap CI via resample ×1000.

**Success Criteria (PoC):**
- Primary: Permutation test p < 0.05 AND paper_count* ∈ [10, 120] (excludes boundary artifacts)
- Secondary: Bootstrap 95% CI width ≤ 20 papers (stable estimate)

**Failure Response:**
- IF fails: PIVOT — null result (rho=−0.28 smooth monotonic) is publishable as primary finding; H0 is the empirically supported description.

**Dependencies:** None (foundation)
**Source:** Phase 2A Section 5 (sh1_existence), Section 1.6 (P1)

---

**H-M1: Early-Phase High CoV Regime (Mechanism Step 1)**

**Type:** MECHANISM
**Statement:** Under PwC benchmark data, if benchmarks are split at detected paper_count*, then pre-breakpoint residual CoV will exhibit significantly higher variance than the overall CoV distribution baseline, confirming the early-phase exploration regime of the Goodhart saturation mechanism.

**Rationale:** The three-step mechanism requires that the early phase (paper_count < paper_count*) is genuinely high-variance — not merely higher than the post-breakpoint segment. This tests that the detected break is a true regime boundary, not a statistical artifact. ImageNet history (arXiv:2205.04596) and Goodhart's Law theory both predict this pre-breakpoint behavior.

**Variables:**
- Independent: paper_count (split at paper_count* from H-E1)
- Dependent: residual_CoV variance in pre-breakpoint segment
- Controlled: paper_count* value from H-E1 (fixed input); linear detrending applied upstream

**Verification Protocol:**
1. Use paper_count* from H-E1; split residual_CoV into pre- and post-breakpoint segments.
2. Compute variance of pre-breakpoint residual_CoV vs. variance of full series.
3. Apply one-sample F-test: pre-segment variance > global variance.
4. Confirm pre-segment mean residual_CoV is positive (above trend).
5. Report pre-segment N, mean, variance, and F-test p-value.

**Success Criteria (PoC):**
- Primary: Pre-segment variance > full-series variance (F-test p < 0.10 one-tailed)
- Secondary: Pre-segment mean residual_CoV > 0 (directional confirmation)

**Failure Response:**
- IF fails: EXPLORE — early phase may not be distinctly high-variance; document as limitation; proceed to H-M2 (variance compression is the more critical test).

**Dependencies:** H-E1 (paper_count* required as input)
**Source:** Phase 2A Section 1.3, Causal Step 1

---

**H-M2: Post-Breakpoint Variance Compression (Mechanism Step 2 — Core)**

**Type:** MECHANISM
**Statement:** Under PwC N=111 benchmark data, if residual CoV is split at paper_count*, then the post-breakpoint segment will show significantly lower variance than the pre-breakpoint segment (Brown-Forsythe p < 0.05, variance ratio post/pre < 1.0), confirming Goodhart saturation compression.

**Rationale:** This is the second PROVE_NEW claim and the direct empirical test of the Goodhart mechanism. Variance compression (homogeneous post-saturation residuals) is the mechanistic signature distinguishing true saturation from a mere performance plateau. Brown-Forsythe center='median' is robust to non-normality in CoV distributions.

**Variables:**
- Independent: paper_count regime (pre vs. post paper_count* from H-E1)
- Dependent: residual_CoV variance ratio (post/pre)
- Controlled: paper_count* (fixed from H-E1); linear detrending applied upstream

**Verification Protocol:**
1. Split residual_CoV at paper_count* into pre- and post-breakpoint segments.
2. Apply scipy.stats.levene(pre_segment, post_segment, center='median') [Brown-Forsythe variant].
3. Test H1: variance(post) < variance(pre) — one-tailed interpretation.
4. Compute variance ratio = var(post) / var(pre); report point estimate and direction.
5. Validate via piecewise linear regression F-test (statsmodels) as independent check.

**Success Criteria (PoC):**
- Primary: Brown-Forsythe p < 0.05 AND variance ratio (post/pre) < 1.0
- Secondary: Piecewise regression F-test also significant (dual-method confirmation)

**Failure Response:**
- IF fails: PIVOT — change-point (if detected) reflects mean shift only, not variance homogenization; Goodhart mechanism as described is not operating; document alternative interpretation.

**Dependencies:** H-E1 (paper_count* required), H-M1 (pre-segment characterization)
**Source:** Phase 2A Section 1.6 (P2), Section 1.3 Causal Step 3

---

**H-M3: Directional Specificity of Variance Reduction (Mechanism Step 3)**

**Type:** MECHANISM
**Statement:** Under PwC N=111 data, if post-breakpoint variance compression is confirmed (H-M2), then the reduction is directional (post-segment CoV values are concentrated near the lower end of the CoV distribution, not randomly distributed), consistent with ceiling-optimization rather than general convergence.

**Rationale:** Goodhart saturation predicts not just lower variance but downward clustering — optimized scores press toward the performance ceiling, compressing the CoV distribution asymmetrically. This distinguishes Goodhart saturation from benign convergence (e.g., methods becoming standardized without ceiling pressure). This is a SHOULD_WORK test — its failure narrows the mechanism claim but does not invalidate H-E1 or H-M2.

**Variables:**
- Independent: Breakpoint regime (post-breakpoint segment)
- Dependent: Skewness and lower-tail concentration of post-breakpoint residual_CoV distribution
- Controlled: paper_count* from H-E1; baseline: pre-breakpoint skewness

**Verification Protocol:**
1. Compute skewness of pre- and post-breakpoint residual_CoV distributions.
2. Test: post-segment skewness > pre-segment skewness (right-skew reduction = downward concentration).
3. Compute 10th percentile of post-segment residual_CoV vs. 10th percentile of pre-segment.
4. Report distribution moments (mean, variance, skewness, kurtosis) for both segments.
5. Visual check: histogram overlay of pre vs. post residual_CoV distributions.

**Success Criteria (PoC):**
- Primary: Post-segment skewness ≠ pre-segment in direction consistent with ceiling compression
- Secondary: Post-segment 10th percentile < pre-segment 10th percentile (lower-tail concentration)

**Failure Response:**
- IF fails: EXPLORE — variance reduction exists but distribution shape is symmetric; Goodhart ceiling pressure not the primary driver; document as scope limitation (SHOULD_WORK).

**Dependencies:** H-E1, H-M1, H-M2
**Source:** Phase 2A Section 1.3 Causal Step 3, key_tension

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Permutation p < 0.05, paper_count* ∈ [10, 120] | STOP — null result published; H0 supported |
| H-M1 | MUST_WORK | Pre-segment variance > global (F p < 0.10) | EXPLORE — document as limitation, proceed to H-M2 |
| H-M2 | MUST_WORK | Brown-Forsythe p < 0.05, ratio < 1.0 | PIVOT — mean-shift only; Goodhart mechanism not confirmed |
| H-M3 | SHOULD_WORK | Directional skewness consistent with ceiling compression | EXPLORE — narrows claim; does not invalidate H-E1/H-M2 |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3 | 4 weeks |
| Total | 4 hypotheses | 6 weeks |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1 (from A1): Cross-Sectional Pooling Invalidity**

**Source Assumption:** A1 — Pooled CoV sorted by paper_count forms a valid PELT input series.

**Description:** If cross-sectional pooling mixes heterogeneous benchmark subpopulations (e.g., image vs. NLP tasks with systematically different CoV scales), PELT may detect task-type heterogeneity rather than a saturation threshold.

**Affected Hypotheses:** H-E1, H-M1, H-M2, H-M3

**Severity:** High

**Mitigation Strategy:**
1. Prevention: Apply linear detrending to remove global trend before PELT; stratify by task_type in parallel.
2. Detection: If stratified paper_count* estimates diverge widely (non-overlapping CIs), pooling invalidity is detected.
3. Response: PIVOT — report stratified results as primary finding; pooled estimate becomes secondary. If all strata agree, pooling is validated.

---

**Risk R2 (from A2): Insufficient Sample Size**

**Source Assumption:** A2 — N=111 sufficient for PELT reliability.

**Description:** If bootstrap CI width exceeds 20 papers, the paper_count* estimate is too imprecise for policy use, undermining the contribution claim of a quantitative retirement criterion.

**Affected Hypotheses:** H-E1

**Severity:** Medium

**Mitigation Strategy:**
1. Prevention: Use min_size=3 (per VPWBS recommendation), BIC penalty tuning.
2. Detection: CI width computed automatically during bootstrap (1000 resamples).
3. Response: SCOPE — if CI > 20 papers, publish as exploratory estimate with explicit uncertainty bounds; still scientifically valid.

---

**Risk R3 (from A3): Stratum Size Insufficiency**

**Source Assumption:** A3 — N ≥ 20 per stratum for stratified PELT.

**Description:** Object_detection stratum (N~15-20) may fall below the PELT reliability threshold, producing unreliable stratum-specific estimates.

**Affected Hypotheses:** H-E1 (stratified), Phase 5 comparison

**Severity:** Low (pre-specified fallback exists)

**Mitigation Strategy:**
1. Prevention: Pre-specify rule: N ≥ 20 → PELT; N < 20 → piecewise regression F-test only.
2. Detection: Count stratum N before analysis; apply rule automatically.
3. Response: SCOPE — object_detection stratum reported with F-test only; image/NLP strata use PELT.

---

**Risk R4 (from A4): Metric Heterogeneity Confound**

**Source Assumption:** A4 — Goodhart saturation is the primary CoV driver, not metric scale heterogeneity.

**Description:** Benchmarks with different performance scales (accuracy 0-100% vs. F1 0-1 vs. perplexity 0-∞) may show systematic CoV differences unrelated to saturation.

**Affected Hypotheses:** H-E1, H-M2

**Severity:** Medium

**Mitigation Strategy:**
1. Prevention: Restrict analysis to percentage-based/normalized metrics (pre-specified scope).
2. Detection: Robustness check — repeat analysis with score-normalized CoV (min-max per benchmark).
3. Response: SCOPE — if normalized CoV gives different paper_count*, report both; note metric heterogeneity as scope limitation.

---

**Risk R5 (from A5): Multiple Structural Breaks**

**Source Assumption:** A5 — Single change-point adequately characterizes the relationship.

**Description:** If the CoV-vs-paper_count relationship has 2+ change-points, the single-break model underfits, and the reported paper_count* may correspond to the wrong regime boundary.

**Affected Hypotheses:** H-E1, H-M1, H-M2

**Severity:** Low (PELT handles naturally)

**Mitigation Strategy:**
1. Prevention: BIC penalty naturally selects parsimony; PELT detects 2+ breaks if present.
2. Detection: Report ALL detected change-points; BIC improvement plot shows if 2-break model is better.
3. Response: EXPLORE — if 2+ breaks detected, report all; interpret additional breaks as evidence of more complex saturation dynamics (richer finding, not failure).

---

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Cross-sectional pooling invalidity | A1 | H-E1, H-M1, H-M2, H-M3 | High |
| R2: Sample size insufficiency | A2 | H-E1 | Medium |
| R3: Stratum size (object_detection) | A3 | H-E1 (stratified) | Low |
| R4: Metric heterogeneity confound | A4 | H-E1, H-M2 | Medium |
| R5: Multiple structural breaks | A5 | H-E1, H-M1, H-M2 | Low |

**Risk R6 (from MCP critique — Dr. Chang): Multiple Testing in Stratified Analysis**

**Source:** MCP collaborativereasoning critique — statistician perspective.

**Description:** Running both global and stratified PELT introduces multiple testing. Without correction, stratified results inflate false-positive rate.

**Affected Hypotheses:** H-E1 (stratified analysis)

**Severity:** Low (pre-specified mitigation)

**Mitigation Strategy:**
1. Prevention: Pre-register global PELT as single primary test (no correction needed).
2. Detection: Stratified tests are explicitly labeled exploratory.
3. Response: Apply Bonferroni correction across strata (divide α=0.05 by number of strata tested).

---

**Risk R7 (from MCP critique — Dr. Patel): paper_count Inflation via Informal PwC Submissions**

**Source:** MCP collaborativereasoning critique — ML methodologist perspective.

**Description:** PwC paper_count includes informal submissions (hyperparameter searches, fine-tuning runs). High paper_count benchmarks may not reflect true community saturation, weakening the theoretical basis for a break at that point.

**Affected Hypotheses:** H-E1, H-M2

**Severity:** Low (robustness check)

**Mitigation Strategy:**
1. Prevention: Primary analysis uses all result rows (as in H-E1 v2 baseline).
2. Detection: Robustness check — repeat analysis restricted to result_type='model' entries.
3. Response: If paper_count* shifts substantially under restriction, flag as sensitivity finding; report both estimates.

---

**Critical Risks:** 0 | **High:** 1 | **Medium:** 2 | **Low:** 4 (R3, R5, R6, R7)

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1 (Existence — no dependencies)
    MUST_WORK gate: permutation p < 0.05
         │
         ▼
[Level 1 - Mechanism: Early Phase]
    H-M1 ← H-E1
    MUST_WORK: pre-segment variance > global
         │
         ▼
[Level 2 - Mechanism: Variance Compression]
    H-M2 ← H-M1
    MUST_WORK: Brown-Forsythe p < 0.05, ratio < 1.0
         │
         ▼
[Level 3 - Mechanism: Directional Specificity]
    H-M3 ← H-M2
    SHOULD_WORK: skewness consistent with ceiling compression

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total: 4 hypotheses, 4 levels, 2 verification phases
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | MUST_WORK |
| 3 | H-M3 | H-M2 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis   │ W1-2    │ W3-4    │  W5     │  W6     │
───────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 1: Foundation
  H-E1             │ ████████│         │         │         │
  [Gate 1]         │        ◆│         │         │         │
───────────────────┼─────────┼─────────┼─────────┼─────────┤
PHASE 2: Mechanisms
  H-M1             │         │ ████████│         │         │
  H-M2             │         │         │ ████████│         │
  H-M3             │         │         │         │ ████████│
  [Gate 2]         │         │        ◆│         │         │
  [Gate Final]     │         │         │         │        ◆│
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Duration: 6 weeks
  Formula: 2 (H-E1) + 1 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (gate buffer) = 6 weeks
Slack Available: 0 weeks (all sequential)
```

### 5.5 Resource Summary

```
Total Hypotheses: 4
  - Existence: 1 (H-E1)
  - Mechanism: 3 (H-M1, H-M2, H-M3)
  - Condition: 0 (no H-C required)

Verification Phases: 2
  1. Foundation (H-E1) — MUST_WORK
  2. Mechanisms (H-M1, H-M2, H-M3) — MUST_WORK + SHOULD_WORK

Total Duration: 6 weeks
Critical Path: 6 weeks
Execution Mode: Sequential chain (all hypotheses depend on prior)
Compute: Trivial (N=111, statistical tests only — no GPU required)
```

### 5.6 Execution Order

```
Step 1: Execute H-E1 (Foundation) — Week 1-2
  → Detect paper_count* via PELT + permutation test
  → Bootstrap CI for stability
Step 2: Evaluate Gate 1 → If FAIL: STOP, publish null result
Step 3: Execute H-M1 (Early-phase regime) — Week 3-4
  → Characterize pre-breakpoint variance
Step 4: Evaluate Gate 2 (H-M1 MUST_WORK) → If FAIL: EXPLORE, proceed to H-M2
Step 5: Execute H-M2 (Variance compression) — Week 5
  → Brown-Forsythe test; piecewise regression F-test validation
Step 6: Execute H-M3 (Directional specificity) — Week 6
  → Distribution moment analysis; histogram overlay
Step 7: Final gate evaluation → synthesis for Phase 4.5/6
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
THESIS
══════════════════════════════════════════════════════════
Core Claim: PwC benchmark leaderboards exhibit a detectable
structural break (paper_count*) in CoV-vs-paper_count,
driven by Goodhart saturation (community optimization toward
known ceiling). The post-breakpoint regime shows significantly
lower CoV variance — empirically testable via PELT + permutation.

Supporting Evidence:
1. rho=−0.28 (confirmed empirical anchor from H-E1 v2) establishes
   the global trend that PELT residualizes before break detection.
2. Goodhart's Law literature (community ceiling optimization) provides
   theoretical mechanism for the regime shift at step 2.
3. Liao et al. 2022 and S_index document aggregate saturation;
   PELT operationalizes individual-benchmark thresholds they lack.

Strengths:
  - Established empirical foundation (rho=−0.28, verified tools)
  - Clear three-step causal mechanism with individual falsifiers
  - Novel framing (discrete phase transition vs. aggregate trend)
  - Immediately testable on existing data — no new experiments needed

Expected Outcomes:
  PRIMARY (P1): Permutation p < 0.05, paper_count* ∈ [10, 120]
  SECONDARY (P2): Brown-Forsythe p < 0.05, ratio (post/pre) < 1.0
  TERTIARY (P3): Stratified paper_count* differ across domains
══════════════════════════════════════════════════════════
```

### 6.2 Antithesis

```
ANTITHESIS
══════════════════════════════════════════════════════════
Null Hypothesis (H0): The rho=−0.28 relationship is a smooth
monotonic trend without a detectable regime shift.
Permutation test p ≥ 0.05 and/or Brown-Forsythe p ≥ 0.05.

Counter-Arguments:
1. OLS linear model (R²≈0.08) already captures the relationship;
   adding change-point complexity may not improve fit beyond noise.
2. Cross-sectional pooling of heterogeneous benchmarks (image,
   NLP, object detection) conflates subpopulation differences
   with saturation signal — violating A1.
3. N=111 may be insufficient for PELT to distinguish a genuine
   regime shift from high-variance noise in the series.

Potential Failure Points:
  - R1 (High): Task-type heterogeneity masquerades as regime shift
  - R2 (Medium): Bootstrap CI > 20 papers → estimate too uncertain
  - R4 (Medium): Metric scale heterogeneity drives observed CoV patterns

Conditions Supporting H0:
  - Permutation test p ≥ 0.05 (no significant change-point)
  - Brown-Forsythe p ≥ 0.05 (no variance compression)
  - Stratified results: all stratum-specific CIs overlap
══════════════════════════════════════════════════════════
```

### 6.3 Synthesis

```
SYNTHESIS
══════════════════════════════════════════════════════════
Balanced Assessment:

H-SatOnset-v1 presents a testable reframing of benchmark saturation
as a discrete phase transition. The null hypothesis raises a valid
concern: the rho=−0.28 monotonic trend may adequately describe the
data without invoking a structural break. The dialectic is resolved
empirically — the permutation test directly compares both models.

Resolution Path:
1. H-E1 (Foundation): Permutation test adjudicates Thesis vs. Antithesis
   in a controlled, pre-registered test. P < 0.05 confirms regime shift.
2. H-M2 (Variance compression): Brown-Forsythe directly tests whether
   the detected break is a mean shift (weak) or variance homogenization
   (Goodhart mechanism). This distinguishes between plausible stories.
3. Gate conditions: If H-E1 fails, H0 is empirically supported and
   published; null result is scientifically valid and equally publishable.

Outcome Possibilities:
  FULL SUPPORT: All MUST_WORK gates pass → Thesis validated with
    quantitative paper_count* for benchmarks.
  PARTIAL SUPPORT: H-E1 passes, H-M2 fails → Mean-shift only;
    change-point exists but not Goodhart compression; refined claim.
  NO SUPPORT: H-E1 fails → Antithesis supported; rho=−0.28 smooth
    monotonic model is the empirically best description.

Nuance: Task-type stratification (Phase 5) may reveal that pooled
analysis masks domain-specific thresholds — a richer finding
that bridges Gap 1 and Gap 2 simultaneously.
══════════════════════════════════════════════════════════
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Structural break exists in PwC CoV series | May be task-type heterogeneity artifact | H-E1 + stratified analysis |
| Mechanism | Goodhart compression: variance collapses | Mean shift only; no variance homogenization | H-M2 Brown-Forsythe test |
| Directionality | Post-breakpoint downward clustering | Random variance reduction | H-M3 skewness analysis |
| Sample Adequacy | N=111 sufficient (VPWBS O_p(1/n)) | CI too wide for policy use | Bootstrap CI width check |

**Overall Robustness Score:** Medium-High (strong theoretical grounding + direct empirical test; null result risk acknowledged)

**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-SatOnset-v1 — PELT detects paper_count* (structural break) in PwC N=111 CoV-vs-paper_count data
- ID: H-SatOnset-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A Dialogue loaded; 67% scope reduction)
- Sub-Hypotheses: 4 total (H-E1: 1, H-M1-3: 3, H-C: 0)
- Phases: 2 phases over 6 weeks; critical path is fully sequential
- Critical Gates: 2 MUST_WORK gates (H-E1, H-M2) + 1 SHOULD_WORK (H-M3)

**Risk Assessment:** Medium
- Primary concerns: Cross-sectional pooling confound (R1, High); metric heterogeneity (R4, Medium)
- Both have pre-specified mitigations (stratification, normalized CoV robustness check)

**Immediate Action:** Begin Phase 1 with H-E1 (PELT + permutation test on derive.py output)

### 7.2 Conclusions

**Key Achievements:**
- 4 hypotheses across 2 phases; H0 fully addressed (permutation test adjudicates directly)
- All verification tools exist (ruptures, statsmodels, scipy); data confirmed (derive.py, N=111)
- Null result handling pre-specified: publishable as rho=−0.28 smooth monotonic primary finding

**Verification Execution Order:**

Phase 1: Foundation (2 weeks)
- H-E1: PELT + permutation test on linearly detrended residual CoV
- Gate 1: MUST PASS (permutation p < 0.05, paper_count* ∈ [10,120])

Phase 2: Core Mechanisms (4 weeks)
- H-M1: Pre-segment variance characterization (Week 3-4)
- H-M2: Brown-Forsythe variance compression test (Week 5)
- H-M3: Directional skewness analysis (Week 6)
- Gate 2: H-M2 MUST_WORK; H-M3 SHOULD_WORK

**Critical Decision Points:**

1. Gate 1 (Foundation / H-E1): Permutation p < 0.05 required
   - FAIL → STOP pipeline; publish null result (H0 supported, rho=−0.28 primary)
   - PASS → Proceed to Phase 2

2. Gate 2 (Mechanism / H-M2): Brown-Forsythe p < 0.05 required
   - FAIL (Brown-Forsythe) → PIVOT; mean-shift change-point only; Goodhart compression not confirmed
   - PASS → Full mechanism validated; proceed to H-M3 (SHOULD_WORK)

3. H-M3 (SHOULD_WORK): Directional specificity
   - FAIL → Document as scope limitation; does not invalidate H-E1/H-M2

**Open Questions (from Phase 2A):**
- What is the quantitative value of paper_count* (expected range 20-100)?
- Do image_classification and NLP paper_count* values differ significantly?
- Does paper_count* correlate with ceiling proximity (Gap 3 connection)?
- Is paper_count* predictive of rank_reversal_rate (Gap 3, Q5)?

**Recommendations:**
1. Immediate: Execute H-E1 on existing derive.py output — computationally trivial (N=111)
2. Resources: 6 weeks total; all analysis in Python (ruptures, statsmodels, scipy)
3. Failure management: Document all results; null result is fully publishable (pre-registered)

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: docs/youra_research/03_refinement.yaml (ID: H-SatOnset-v1)
- Discussion: 10 exchanges, 6 agents, all convergence criteria met at Exchange 10

**B. MCP Tool Usage Summary**
- Total MCP calls: 4 (ClearThought scientificmethod ×3 incremental, collaborativereasoning ×1)
- Scope reduction: 67% (4/6 BUILD_ON claims skipped)
- Transfer validation: Not required (no cross-domain transfer)

---

*Phase 2B Complete — Ready for Phase 2C experiment design per hypothesis*
