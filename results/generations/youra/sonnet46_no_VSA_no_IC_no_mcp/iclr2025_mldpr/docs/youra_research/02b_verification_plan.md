---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
status: complete
completedAt: "2026-08-25T00:00:00Z"
hypothesis_id: H-BenchSat-v1
date: "2026-08-25"
---

# Verification Plan: Automated Temporal Benchmark Saturation Detection

**Date:** 2026-08-25
**Hypothesis ID:** H-BenchSat-v1
**Confidence:** 0.78
**Total Hypotheses:** 6

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under the condition that a benchmark has ≥ 50 leaderboard submissions in Papers With Code with date coverage from ≥ 2019, if we fit a logistic growth model to the score-over-time timeseries and compare it against linear and sub-linear alternatives via AIC, then the logistic model will be statistically preferred AND its detected saturation date (inflection point + asymptote exceedance) will match the community-recognized saturation event within ±6 months, because benchmark overfitting accumulates gradually as models are tuned against a fixed test set, producing a characteristic S-curve that the logistic model captures while linear models cannot.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in AIC between the logistic growth model and a linear trend model fitted to benchmark score-over-time timeseries (ΔAIC < 4); or, the logistic-detected saturation dates do not match community-recognized saturation events within ±6 months for at least one of GLUE or SuperGLUE.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Papers With Code Leaderboard Timeseries (standard) | Direct source of score-over-time data; public API; no new collection required |
| **Model** | Logistic Growth Model (3-parameter, scipy curve_fit) | Canonical S-curve model; directly captures saturation mechanism hypothesized |

**Dataset Details:**
- Source: Papers With Code public API (paperswithcode-client)
- Path: Retrieved via API: benchmark_results(benchmark_id='glue'), benchmark_results(benchmark_id='superglue'), etc.

**Model Details:**
- Type: Statistical curve (scipy curve_fit)
- Source: scipy.optimize.curve_fit with logistic kernel: K / (1 + exp(-r*(t - t0)))

### 1.4 Baseline Methods (for comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Recht et al. 2019 (ImageNet-v2 overfitting detection) | 11–14 pp accuracy gap documented | ImageNet + ImageNet-v2 |
| Visual leaderboard curves on Papers With Code (no formal model) | N/A (descriptive only) | All Papers With Code benchmarks |
| Community expert judgment (SuperGLUE creation as GLUE saturation response) | Community consensus ≈ Sept 2019 for GLUE | GLUE |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Papers With Code leaderboard submission dates accurate to month-level for entries from ≥ 2019 | PwC actively maintained since 2018; major submissions linked to dated arXiv papers | Temporal resolution insufficient; fallback to year-level reduces statistical power |
| A2 | Successor benchmark publication date is valid independent ground truth for saturation | SuperGLUE explicitly created because GLUE saturated (stated in paper); BIG-bench similarly | Circular validation risk; mitigation: use paper publication date, not submission rate |
| A3 | Self-reporting selection bias biases K upward but does not destroy sigmoid structure | Even with censoring, growth + plateau phases remain observable in major benchmarks | K overestimated; saturation detected prematurely; sensitivity analysis required |
| A4 | Logistic parameters (K, r, t0) identifiable from available timeseries | GLUE/SuperGLUE have hundreds of entries spanning all three curve phases | Non-identification for benchmarks with <50 entries or no plateau; scope restriction mitigates |
| A5 | Successor benchmark publication dates available for ≥2 target benchmarks | SuperGLUE paper Sept 2019; BIG-bench 2021; both documented public records | Cannot validate saturation date detection; hypothesis degrades to descriptive claim only |

### 1.6 Research Gap & Novelty

No published automated pipeline for temporal benchmark saturation detection from leaderboard timeseries exists. Prior work (Recht et al. 2019) requires new independently-collected test sets; community critiques are qualitative. This hypothesis operationalizes saturation detection as a fully automated statistical procedure over existing public data, including prospective forecasting capability (P3 — predicting saturation 6 months in advance).

**Scope Reduction:** 57% of claims are BUILD_ON (pre-validated). Only 3 PROVE_NEW claims require hypothesis generation: (a) automated logistic pipeline, (b) statistical model preference, (c) saturation date validation.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | MUST_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |
| H-C1 | CONDITION | SHOULD_WORK | H-M4 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Leaderboard Data Sufficiency for Logistic Curve Fitting**

**Statement**: Under the condition that a benchmark is hosted on Papers With Code with ≥ 50 leaderboard submissions from ≥ 2019, if we retrieve its score-over-time timeseries via the Papers With Code API, then the data will contain sufficient coverage of growth, inflection, and plateau phases for scipy curve_fit to converge on a 3-parameter logistic model with R² > 0.9, because major benchmarks (GLUE, SuperGLUE) have hundreds of dated submissions spanning their full lifecycle.

**Rationale**: This existence hypothesis establishes that the raw data preconditions are met before any mechanism test. If logistic fitting fails to converge, all downstream H-M hypotheses are blocked. This is the foundation gate.

**Variables**:
- Independent: Benchmark identity (GLUE, SuperGLUE, ImageNet, SQuAD)
- Dependent: scipy curve_fit convergence (boolean), R² of logistic fit
- Controlled: ≥50 entries, month-level dates ≥2019, single composite metric

**Verification Protocol**:
1. Retrieve full leaderboard timeseries for GLUE and SuperGLUE via paperswithcode-client API.
2. Clean data: standardize metric, convert dates to months-since-release, deduplicate (keep best score per model).
3. Fit 3-parameter logistic model via scipy.optimize.curve_fit with bounded initialization (K ∈ [0.8,1.0], r ∈ [0.1,2.0], t0 ∈ [6,36]).
4. Confirm convergence (no RuntimeError) and compute R² against raw data points.
5. Visually inspect fit; confirm growth + inflection + plateau phases are represented.

**Success Criteria** (PoC: direction-based):
- Primary: scipy curve_fit converges for both GLUE and SuperGLUE (no RuntimeError)
- Secondary: R² > 0.9 for logistic fit on both benchmarks

**Failure Response**:
- IF fails: PIVOT — investigate data quality issues; try year-level granularity; consider fewer benchmarks

**Dependencies**: None (foundation)

**Source**: Phase 2A Section 5 (sh1_existence), Section 1.3 (A4)

---
**H-M1: Benchmark Overfitting Accumulation Leaves Observable Temporal Signal**

**Statement**: Under the condition that GLUE and SuperGLUE leaderboard timeseries are available with month-level precision, if models are iteratively developed with awareness of benchmark test set performance, then the score-over-time trajectory will exhibit a non-random temporal structure consistent with gradual overfitting accumulation (monotonically increasing scores with decelerating gains over time), because models are tuned against a fixed test set producing diminishing returns as benchmark-exploitable signal exhausts.

**Rationale**: Step 1 of the causal chain must be verified empirically — the temporal signal must exist before it can be modeled. This tests whether the pre-condition for logistic fitting is structurally valid, not just numerically tractable.

**Variables**:
- Independent: Time (months since benchmark release)
- Dependent: Score trajectory shape (monotonic, decelerating gains)
- Controlled: Same benchmark set as H-E1; top-3 scores per time period

**Verification Protocol**:
1. Compute month-over-month score gains from the cleaned GLUE/SuperGLUE timeseries.
2. Run Spearman correlation between time and score to confirm monotonicity.
3. Run Spearman correlation between time and gain rate to confirm deceleration (negative correlation).
4. Plot score trajectory and visually confirm S-curve shape.
5. Compare pre-inflection vs. post-inflection gain rates to quantify deceleration.

**Success Criteria** (PoC: direction-based):
- Primary: Spearman ρ(time, score) > 0.8 for both GLUE and SuperGLUE
- Secondary: Spearman ρ(time, gain_rate) < -0.3 (deceleration present)

**Failure Response**:
- IF fails: EXPLORE — investigate data artifacts; may indicate PwC date quality issue (A1 violation)

**Dependencies**: H-E1

**Source**: Phase 2A Section 1.3 Step 1, Recht et al. 2019 (BUILD_ON)

---
**H-M2: Score-Over-Time Exhibits Nonlinear S-Curve Structure Captured by Logistic Model**

**Statement**: Under the condition that the score-over-time trajectory shows temporal structure (H-M1 confirmed), if we fit logistic, linear, and power law models to the timeseries and compute AIC for each, then the logistic model will be statistically preferred (ΔAIC > 4 vs. linear) for both GLUE and SuperGLUE, because benchmark-specific overfitting produces genuine nonlinear saturation dynamics (not just diminishing returns) that the S-curve uniquely captures.

**Rationale**: This is the core statistical test of the hypothesis. AIC model comparison directly operationalizes the "logistic preferred" claim. A ΔAIC > 4 threshold (Burnham & Anderson 2002) establishes substantial evidence — not just marginally better fit.

**Variables**:
- Independent: Model type (logistic, linear, power law)
- Dependent: AIC per model, ΔAIC(logistic - linear)
- Controlled: Same benchmark timeseries; identical time-score pairs used for all model fits

**Verification Protocol**:
1. Fit linear model (numpy.polyfit degree=1) to (time, score) pairs for GLUE and SuperGLUE.
2. Fit power law model (log-linear via numpy.polyfit on log-transformed data) for both benchmarks.
3. Fit logistic model (from H-E1 confirmed fit) for both benchmarks.
4. Compute AIC = 2k - 2*ln(L) for each model (k=parameters, L=likelihood from residual variance).
5. Compute ΔAIC = AIC_logistic - AIC_linear; verify ΔAIC > 4 in favor of logistic.

**Success Criteria** (PoC: direction-based):
- Primary: ΔAIC(logistic vs. linear) > 4 for both GLUE and SuperGLUE (logistic substantially preferred)
- Secondary: ΔAIC(logistic vs. power law) > 2 for both benchmarks

**Failure Response**:
- IF fails: PIVOT — if linear is preferred, S-curve structure claim is unsupported; reassess mechanism

**Dependencies**: H-M1

**Source**: Phase 2A Section 1.3 Step 2-3, Section 1.6 P1

---
**H-M3: Logistic Model Parameters Encode Saturation Dynamics Interpretably**

**Statement**: Under the condition that the logistic model is AIC-preferred (H-M2 confirmed), if we extract the fitted parameters (K=ceiling, r=growth rate, t0=inflection point) from the GLUE and SuperGLUE fits, then the parameters will be interpretable and physically plausible (K ∈ [0.85, 1.0], t0 aligns with known rapid growth periods, r > 0), because the logistic model's three parameters directly encode the mechanism: K is the performance ceiling, t0 is when overfitting dominates, r quantifies the exploitation rate.

**Rationale**: Parameter interpretability validates that the logistic fit is mechanistically meaningful, not just a curve-fitting artifact. Physically implausible parameters (K > 1, t0 before benchmark launch, r < 0) would indicate numerical issues rather than genuine saturation dynamics.

**Variables**:
- Independent: Benchmark identity (GLUE, SuperGLUE)
- Dependent: Fitted K, r, t0 values; parameter confidence intervals
- Controlled: scipy curve_fit with bounded initialization from H-E1

**Verification Protocol**:
1. Extract fitted (K, r, t0) with 95% confidence intervals from scipy curve_fit for GLUE and SuperGLUE.
2. Verify K ∈ [0.85, 1.0] (performance ceiling in normalized score space).
3. Verify t0 ∈ [6, 48] months since benchmark release (inflection within observed leaderboard history).
4. Verify r > 0 (positive growth rate — not negative/inverted S-curve).
5. Report confidence interval widths; flag if CIs are very wide (poor identifiability signal).

**Success Criteria** (PoC: direction-based):
- Primary: All three parameters physically plausible for both GLUE and SuperGLUE
- Secondary: 95% CI for t0 width < 12 months (sufficient precision for date detection)

**Failure Response**:
- IF fails: EXPLORE — investigate initialization sensitivity; may indicate A4 violation (poor identifiability)

**Dependencies**: H-M2

**Source**: Phase 2A Section 1.3 Step 3, Section 1.4 A4

---
**H-M4: Logistic Saturation Date Criterion Matches Community-Recognized Events**

**Statement**: Under the condition that logistic model parameters are plausible (H-M3 confirmed), if we apply the saturation detection criterion (top-3 models exceed fitted asymptote K AND monthly gain rate < 5% of peak rate) to the full historical GLUE and SuperGLUE timeseries, then the detected saturation dates will match community-recognized ground truth dates (SuperGLUE publication Sept 2019 for GLUE; BIG-bench announcement ~2021 for SuperGLUE) within ±6 months, because the inflection point + asymptote exceedance criterion operationalizes the same exhaustion of benchmark-exploitable signal that motivated the community to create successor benchmarks.

**Rationale**: This is the final mechanism test — connecting the statistical model to real-world benchmark lifecycle events. Success validates the end-to-end pipeline: data retrieval → curve fitting → saturation detection → date matching.

**Variables**:
- Independent: Benchmark identity
- Dependent: Detected saturation date, saturation date error (months vs. ground truth)
- Controlled: Ground truth = successor benchmark publication date; tolerance = ±6 months

**Verification Protocol**:
1. Apply saturation criterion: find first month when top-3 scores exceed 0.99×K AND monthly gain rate < 0.05×peak_rate.
2. Record detected saturation date for GLUE and SuperGLUE.
3. Compare to ground truth: GLUE → Sept 2019, SuperGLUE → BIG-bench announcement ~2021.
4. Compute saturation date error |detected - ground_truth| in months.
5. Prospective test (P3): truncate GLUE at March 2019 (6 months before T_sat); re-fit; forecast; compare.

**Success Criteria** (PoC: direction-based):
- Primary: Saturation date error < 6 months for both GLUE and SuperGLUE
- Secondary (P3): Prospective forecast error < 3 months for GLUE

**Failure Response**:
- IF fails: EXPLORE — try alternative saturation criteria (e.g., 2% gain rate threshold); document failure

**Dependencies**: H-M3

**Source**: Phase 2A Section 1.3 Step 4, Section 1.6 P2, P3

---
**H-C1: Logistic Fitting Fails for Benchmarks Below the 50-Entry Threshold**

**Statement**: Under the condition that the mechanism is validated for ≥50-entry benchmarks (H-M4 confirmed), if we apply the same logistic fitting pipeline to benchmarks with 30–49 leaderboard entries (boundary condition), then scipy curve_fit will either fail to converge or yield R² < 0.7 and/or physically implausible parameters, because with fewer data points the growth, inflection, and plateau phases are underrepresented, making the 3-parameter logistic model non-identifiable.

**Rationale**: Validating the scope boundary confirms that the ≥50-entry restriction is empirically motivated, not arbitrary. If the pipeline works equally well below 50 entries, the scope can be expanded. If it fails, the boundary is confirmed and the claim's scope is well-defined.

**Variables**:
- Independent: Entry count category (30–49 vs. ≥50)
- Dependent: Curve_fit convergence, R², parameter plausibility
- Controlled: Same fitting procedure as H-E1/H-M1-4; identify 2-3 benchmarks with 30-49 entries

**Verification Protocol**:
1. Identify 2-3 benchmarks in Papers With Code with 30–49 leaderboard entries from ≥2019.
2. Apply identical logistic fitting pipeline from H-E1.
3. Compare convergence rate and R² distribution to ≥50-entry benchmarks.
4. Report whether boundary condition is empirically supported or the threshold should be adjusted.
5. If pipeline succeeds at 30-49 entries, recommend expanding scope to ≥30 entries.

**Success Criteria** (PoC: direction-based):
- Primary: Convergence/fit quality is meaningfully worse for 30-49 entry benchmarks vs. ≥50
- Secondary: Recommend revised threshold if evidence suggests ≥30 is sufficient

**Failure Response**:
- IF fails (pipeline works fine below 50): EXPLORE — recommend scope expansion to ≥30 entries

**Dependencies**: H-M4

**Source**: Phase 2A Section 1.5 (scope boundary), Section 1.4 A4

---

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
          HYPOTHESIS INVENTORY (6 hypotheses)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID   | Type      | Statement (Brief)                                    | Prerequisites | Source      |
|------|-----------|------------------------------------------------------|---------------|-------------|
| H-E1 | EXISTENCE | PwC timeseries has sufficient data for logistic fit  | None          | SH1         |
| H-M1 | MECHANISM | Score trajectory shows observable temporal structure  | H-E1          | Causal Step 1 |
| H-M2 | MECHANISM | Logistic model AIC-preferred over linear (ΔAIC>4)    | H-M1          | Causal Step 2-3 |
| H-M3 | MECHANISM | Logistic parameters (K,r,t0) physically plausible    | H-M2          | Causal Step 3 |
| H-M4 | MECHANISM | Saturation dates match ground truth within ±6 months | H-M3          | Causal Step 4 |
| H-C1 | CONDITION | Pipeline fails below 50-entry threshold              | H-M4          | Scope boundary |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-C1
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | scipy curve_fit converges, R² > 0.9 | STOP — data preconditions not met; reassess hypothesis |
| H-M1 | MUST_WORK | Spearman ρ(time,score) > 0.8; ρ(time,gain_rate) < -0.3 | STOP — temporal signal absent; investigate data quality |
| H-M2 | MUST_WORK | ΔAIC > 4 for logistic vs. linear (both benchmarks) | PIVOT — S-curve claim unsupported; return to Phase 2A |
| H-M3 | MUST_WORK | All parameters physically plausible, CI(t0) < 12 months | EXPLORE — initialization tuning; may indicate A4 violation |
| H-M4 | SHOULD_WORK | Saturation date error < 6 months for GLUE and SuperGLUE | EXPLORE — try alternative criteria; document failure |
| H-C1 | SHOULD_WORK | Worse fit quality for 30-49 entries vs. ≥50 | EXPLORE — may justify scope expansion |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks (2+1+1+1) |
| Phase 2.5: Conditions | H-C1 | 1 week |

**Total Duration:** 8 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1: Date Resolution Failure (from A1)**
- Description: Papers With Code entries from 2019 may lack month-level date precision; year-level only reduces statistical power for logistic fitting.
- Severity: High | Likelihood: Medium
- Affected Hypotheses: H-E1, H-M1, H-M2
- Mitigation:
  1. Prevention: Use arXiv submission date as proxy for pre-2020 entries (PwC links to papers).
  2. Detection: Flag entries with year-only dates during data cleaning step.
  3. Response: PIVOT to arXiv API for date resolution; if insufficient, restrict to post-2020 data and re-scope.

**Risk R2: Circular Validation (from A2)**
- Description: Community saturation dates are inferred from successor benchmark creation, which could be correlated with leaderboard submission rates rather than independent — circular if both track the same community awareness signal.
- Severity: High | Likelihood: Low
- Affected Hypotheses: H-M4
- Mitigation:
  1. Prevention: Use successor benchmark paper publication date (arXiv submission date, not community awareness date).
  2. Detection: If detected saturation date and ground truth differ by 0 months exactly, flag for circularity check.
  3. Response: SCOPE — report sensitivity analysis; use ±3/±6/±12 month windows.

**Risk R3: Self-Reporting Bias Destroys S-Curve (from A3)**
- Description: If teams only submit when beating SOTA, the plateau phase is underrepresented; logistic K is overestimated; may cause H-E1 convergence with wrong K, leading H-M4 to detect saturation too early.
- Severity: Medium | Likelihood: Medium
- Affected Hypotheses: H-M2, H-M3, H-M4
- Mitigation:
  1. Prevention: Report K with uncertainty bounds; report bias direction explicitly.
  2. Detection: Compare K estimate to known theoretical ceiling (accuracy ≤ 1.0 for classification).
  3. Response: SCOPE — sensitivity analysis with K fixed at 0.99 vs. free K; document effect on detected date.

**Risk R4: Parameter Non-Identifiability (from A4)**
- Description: scipy curve_fit may fail to converge if the timeseries doesn't span all three logistic phases, particularly for benchmarks with <50 entries or recent benchmarks lacking plateau data.
- Severity: Medium | Likelihood: Low (for main targets GLUE/SuperGLUE)
- Affected Hypotheses: H-E1, H-C1
- Mitigation:
  1. Prevention: Scope restriction to ≥50 entries; parameter initialization within physically plausible bounds.
  2. Detection: Check convergence flag from scipy; compute parameter condition number.
  3. Response: SCOPE — restrict to confirmed GLUE/SuperGLUE; reduce claim from "benchmark-agnostic" to "GLUE-class benchmarks".

**Risk R5: No Validatable Ground Truth for Key Benchmarks (from A5)**
- Description: If successor benchmark publication dates are ambiguous or not cleanly documentable for GLUE/SuperGLUE, the date validation test cannot be performed.
- Severity: High | Likelihood: Very Low (GLUE→SuperGLUE dates are published facts)
- Affected Hypotheses: H-M4
- Mitigation:
  1. Prevention: Pre-confirm ground truth dates before running H-M4 (SuperGLUE arXiv:1905.00537 = Sept 2019).
  2. Detection: Cross-check multiple sources (arXiv submission + publication + press coverage dates).
  3. Response: SCOPE — if GLUE/SuperGLUE ground truth is ambiguous, substitute ImageNet→ImageNet-v2 as ground truth benchmark pair.

### 4.2 Risk-Hypothesis Mapping

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RISK-HYPOTHESIS MAPPING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Risk | Source | Affected Hypotheses       | Severity |
|------|--------|---------------------------|----------|
| R1   | A1     | H-E1, H-M1, H-M2         | High     |
| R2   | A2     | H-M4                      | High     |
| R3   | A3     | H-M2, H-M3, H-M4         | Medium   |
| R4   | A4     | H-E1, H-C1                | Medium   |
| R5   | A5     | H-M4                      | High     |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.3 Risk Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    RISK SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| ID | Risk                          | Source | Severity | Affected         | Primary Mitigation       |
|----|-------------------------------|--------|----------|------------------|--------------------------|
| R1 | Date resolution failure       | A1     | High     | H-E1, H-M1, H-M2| arXiv date proxy         |
| R2 | Circular validation           | A2     | High     | H-M4             | Publication date as GT   |
| R3 | Selection bias destroys curve | A3     | Medium   | H-M2-4           | Sensitivity analysis     |
| R4 | Parameter non-identifiability | A4     | Medium   | H-E1, H-C1       | Scope restriction        |
| R5 | No validatable ground truth   | A5     | High     | H-M4             | Pre-confirm dates        |

Critical Risks: 0
High Risks: 3 (R1, R2, R5)
Medium Risks: 2 (R3, R4)
Low Risks: 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 4.4 Baseline Failure Patterns → Risks

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| Recht et al. requires new test set | Our pipeline may have lower accuracy than human-curated detection | H-M4 tests this directly |
| Visual leaderboard curves lack formal model | AIC comparison may show marginal differences only | ±ΔAIC threshold (>4) is the formal criterion |
| Community judgment is retrospective | Our prospective P3 test may show higher error than retrospective P2 | Test prospective separately; document gap |

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 6 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    H-E1: Existence (no dependencies)
         │
         ▼
[Level 1 - Mechanism Foundation]
    H-M1 ← H-E1
    (Observable temporal signal)
         │
         ▼
[Level 2 - Core Statistical Test]
    H-M2 ← H-M1
    (Logistic AIC-preferred)
         │
         ▼
[Level 3 - Parameter Validation]
    H-M3 ← H-M2
    (Parameters physically plausible)
         │
         ▼
[Level 4 - End-to-End Validation]
    H-M4 ← H-M3
    (Saturation dates match ground truth)
         │
         ▼
[Level 5 - Condition/Scope Boundary]
    H-C1 ← H-M4
    (Pipeline fails below 50-entry threshold)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
═══════════════════════════════════════════════════════════
```

### 5.2 Verification Phases with Gate Conditions

**Phase 1 - Foundation**
| Hypothesis | Test | Gate |
|------------|------|------|
| H-E1 | scipy curve_fit convergence, R² > 0.9 | MUST PASS |

→ **Gate 1**: If H-E1 fails → STOP, data preconditions not met; reassess entire hypothesis.

**Phase 2 - Core Mechanisms (4 hypotheses)**
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-M1 | H-E1 | MUST PASS — temporal signal must exist |
| H-M2 | H-M1 | MUST PASS — AIC test is the core claim |
| H-M3 | H-M2 | MUST PASS — parameter plausibility required |
| H-M4 | H-M3 | SHOULD PASS — date validation (failure = document limitation) |

→ **Gate 2**: H-M1, H-M2, H-M3 must pass. H-M4 failure = document limitation but doesn't block scope.

**Phase 2.5 - Conditions (1 hypothesis)**
| Hypothesis | Dependencies | Gate |
|------------|--------------|------|
| H-C1 | H-M4 | SHOULD PASS — scope boundary confirmation |

→ **Gate 2.5**: H-C1 failure narrows scope claim but doesn't invalidate core mechanism.

### 5.3 Dependency Hierarchy Table

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 DEPENDENCY HIERARCHY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Level | Hypothesis | Prerequisites | Gate Type    |
|-------|------------|---------------|--------------|
| 0     | H-E1       | None          | MUST_WORK    |
| 1     | H-M1       | H-E1          | MUST_WORK    |
| 2     | H-M2       | H-M1          | MUST_WORK    |
| 3     | H-M3       | H-M2          | MUST_WORK    |
| 4     | H-M4       | H-M3          | SHOULD_WORK  |
| 5     | H-C1       | H-M4          | SHOULD_WORK  |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.4 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 6 Hypotheses
═══════════════════════════════════════════════════════════════════════════
Phase/Hypothesis  │ W1-2    │ W3-4    │ W5      │ W6      │ W7      │ W8
──────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼──────
PHASE 1: Foundation
  H-E1            │ ████████│         │         │         │         │
  [Gate 1]        │       ◆ │         │         │         │         │
──────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼──────
PHASE 2: Mechanisms
  H-M1            │         │ ████████│         │         │         │
  H-M2            │         │         │ ████████│         │         │
  H-M3            │         │         │         │ ████████│         │
  H-M4            │         │         │         │         │ ████████│
  [Gate 2]        │         │         │         │         │       ◆ │
──────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼──────
PHASE 2.5: Conditions
  H-C1            │         │         │         │         │         │ ████
  [Gate 2.5]      │         │         │         │         │         │    ◆
──────────────────┼─────────┼─────────┼─────────┼─────────┼─────────┼──────
═══════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 8 weeks
═══════════════════════════════════════════════════════════════════════════
```

### 5.5 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-C1

Total Duration: 8 weeks
  Formula: 2 (H-E1) + 4 (H-M: 2+1+1+1) + 1 (H-C) = 8 weeks

Slack Available: 0 weeks (all sequential)

Duration Breakdown:
  Phase 1 (Foundation):   2 weeks (H-E1)
  Phase 2 (Mechanisms):   5 weeks (H-M1: 2w, H-M2-4: 1w each)
  Phase 2.5 (Condition):  1 week  (H-C1)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 6
- Existence:   1 (H-E1)
- Mechanism:   4 (H-M1 to H-M4)
- Condition:   1 (H-C1)

Verification Phases: 3
1. Foundation (H-E1)
2. Mechanisms (H-M1 through H-M4)
3. Conditions (H-C1)

Total Duration: 8 weeks
Critical Path Length: 8 weeks
Execution Mode: Sequential chain
Libraries Required: paperswithcode-client, scipy, numpy

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.7 Execution Order

```
Step 1: Execute H-E1 (Foundation) — Week 1-2
Step 2: Evaluate Gate 1 → If pass, proceed; If fail, STOP
Step 3: Execute H-M1 (Temporal signal) — Week 3-4
Step 4: Evaluate H-M1 gate → If fail, STOP
Step 5: Execute H-M2 (AIC model comparison) — Week 5
Step 6: Evaluate H-M2 gate → If fail, PIVOT to Phase 2A
Step 7: Execute H-M3 (Parameter plausibility) — Week 6
Step 8: Evaluate H-M3 gate → If fail, EXPLORE
Step 9: Execute H-M4 (Date validation) — Week 7
Step 10: Evaluate Gate 2 → If pass, proceed; If fail, EXPLORE
Step 11: Execute H-C1 (Scope boundary condition) — Week 8
Step 12: Evaluate Gate 2.5 → Scope determination
Final: Verification complete → Phase 2C/3/4 per hypothesis
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: Logistic curve fitting on Papers With Code leaderboard
timeseries provides a statistically valid, automated, and prospective
method for benchmark saturation detection.

Supporting Evidence:
1. GLUE/SuperGLUE temporal trajectories show visible S-curves
   (community-documented saturation events with hard dates).
2. Benchmark overfitting is empirically real (Recht et al. 2019 BUILD_ON).
3. 3-library implementation feasible in <1 week (Prof. Pax confirmed).

Strengths:
- No new data collection required (contrast: Recht et al.)
- Fully automated and benchmark-agnostic (contrast: expert judgment)
- Prospective capability (P3) — qualitatively novel vs. all prior work
- Hard ground truth dates available (GLUE→SuperGLUE, SuperGLUE→BIG-bench)

Expected Outcomes:
- Primary (P1): ΔAIC > 4 logistic vs. linear for GLUE and SuperGLUE
- Secondary (P2): Saturation dates within ±6 months of ground truth
- Tertiary (P3): Prospective forecast within ±3 months for GLUE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): There is no significant difference in AIC
between the logistic growth model and a linear trend model; or
logistic-detected saturation dates differ by > 6 months.

Counter-Arguments:
1. Score ceilings (accuracy bounded at 100%) produce S-curves even
   without overfitting — logistic may fit ceiling effects, not saturation.
2. Self-reporting bias (teams submit only when beating SOTA) creates
   informative censoring; the apparent plateau may be submission dropout,
   not genuine saturation.
3. ±6-month tolerance may be too lenient — any "reasonable" date
   detection method could achieve this threshold by chance.

Potential Failure Points:
- R1: Pre-2019 date resolution insufficient → logistic fitting unreliable
- R3: Selection bias so severe sigmoid structure is destroyed
- R2: Ground truth dates are not truly independent of the leaderboard signal

Conditions Under Which H0 Would Be Supported:
- If ΔAIC < 4 for GLUE or SuperGLUE (linear model equally good)
- If H-E1 fails (logistic doesn't converge)
- If detected saturation date > 6 months off for both benchmarks

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:
The hypothesis H-BenchSat-v1 presents a testable, mechanistically grounded
claim that logistic curve fitting enables automated benchmark saturation
detection. However, the null hypothesis raises valid concerns about
ceiling effects vs. genuine overfitting, and selection bias distorting
the sigmoid structure.

Resolution Path:
The verification plan addresses this dialectic through:
1. Foundation verification (H-E1): Data quality gate — convergence required
   before any statistical claim is made.
2. Sequential mechanism testing (H-M1 through H-M4): Each causal step
   tested independently; failure at any MUST_WORK gate stops the chain.
3. Cross-benchmark divergence (secondary analysis in H-M4): Tests whether
   the S-curve is genuine saturation vs. ceiling effect — GLUE and SuperGLUE
   should show different inflection timing consistent with their release dates.
4. Gate conditions: Allow early detection of H0 support (H-M2 AIC test
   is the primary falsification).

Conditions for Thesis Support:
- H-E1, H-M1, H-M2, H-M3 all pass (MUST_WORK)
- ΔAIC > 4 confirmed (P1 = primary prediction validated)
- H-M4 passes: detected dates within ±6 months (P2 validated)

Conditions for Antithesis Support:
- H-E1 fails (data insufficient for logistic fitting)
- H-M2 fails (linear equally good or better by AIC)
- H-M4 fails for both GLUE and SuperGLUE (date detection unreliable)

Nuanced Outcome Possibilities:
1. Full Support: All MUST_WORK + H-M4 pass → Thesis validated, P1+P2+P3 confirmed
2. Partial Support: H-M1-3 pass, H-M4 fails → Pipeline works statistically
   but date detection needs refinement; publication with scope limitation
3. No Support: H-E1 or H-M2 fail → H0 supported; fundamental claim invalid

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect       | Thesis Position                    | Antithesis Challenge           | Resolution             |
|--------------|------------------------------------|---------------------------------|------------------------|
| Data Quality | PwC API has month-level dates      | Pre-2019 dates are year-only    | H-E1 gate + arXiv proxy|
| S-Curve      | Overfitting creates genuine sigmoid | Ceiling effects look identical  | Cross-benchmark diverge|
| AIC Test     | Logistic substantially preferred   | Marginal ΔAIC < 4               | H-M2 gate (strict)     |
| Date Match   | Saturation event correlates ±6m    | Selection bias shifts detection | H-M4 + sensitivity     |
| Scope        | ≥50 entries threshold justified    | Pipeline may work below 50      | H-C1 direct test       |

Overall Robustness Score: Medium-High
(Strong theoretical grounding; 2 of 5 risks are data-quality contingent)

Confidence in Verification Plan: 0.78

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Logistic curve fitting on Papers With Code leaderboard timeseries enables automated, prospective benchmark saturation detection.
- ID: H-BenchSat-v1 | Confidence: 0.78

**Verification Structure:**
- Mode: Incremental (57% scope reduction from established facts)
- Sub-Hypotheses: 6 total — H-E: 1, H-M: 4, H-C: 1
- Phases: 3 phases over 8 weeks
- Critical Gates: 3 decision points (Gate 1: H-E1, Gate 2: H-M1-3, Gate 2.5: H-C1)

**Risk Assessment:** Medium
- Primary concerns: Date resolution quality (A1/R1), ground truth independence (A2/R2), selection bias (A3/R3)

**Immediate Action:** Begin Phase 1 with H-E1 — retrieve Papers With Code leaderboard data for GLUE and SuperGLUE, run scipy logistic fitting, confirm convergence.

### 7.2 Conclusions

**Key Achievements:**
- 6 hypotheses across 3 phases; all derived from 3 PROVE_NEW claims in Phase 2A
- H0 addressed: No AIC difference between logistic and linear → H-M2 direct test
- 57% scope reduction preserves researcher time by excluding BUILD_ON claims
- Full pipeline (data → fit → AIC → date detection) validated end-to-end before Phase 5 comparison

**Verification Execution Order:**

Phase 1: Foundation (2 weeks)
- H-E1: PwC timeseries data sufficiency
- Gate 1: MUST PASS

Phase 2: Core Mechanisms (5 weeks)
- H-M1: Observable temporal signal (Week 3-4)
- H-M2: AIC model comparison — core statistical test (Week 5)
- H-M3: Parameter plausibility (Week 6)
- H-M4: Saturation date validation (Week 7)
- Gate 2: H-M1-M3 must pass

Phase 2.5: Conditions (1 week)
- H-C1: 50-entry threshold boundary test (Week 8)
- Gate 2.5: Scope determination

**Critical Decision Points:**

1. Gate 1 (Foundation): H-E1 must pass
   - FAIL → STOP, fundamental data precondition not met; revisit hypothesis
   - PASS → Proceed to Phase 2

2. Gate 2 (Mechanisms): H-M1, H-M2, H-M3 must all pass
   - H-M2 FAIL → PIVOT (linear preferred = S-curve claim unsupported; return to Phase 2A)
   - H-M4 FAIL → EXPLORE (date detection refinement; document as limitation)

3. Gate 2.5 (Conditions): Scope determination
   - H-C1 failure (pipeline works at <50 entries) → EXPAND scope claim to ≥30 entries

**Open Questions:**
- Exact month-level date coverage quality for pre-2020 GLUE submissions
- Whether scipy curve_fit converges for all 4+ target benchmarks or requires benchmark-specific initialization
- Tolerance sensitivity: does ±6-month criterion hold for SQuAD where saturation is less community-documented

**Recommendations:**

1. Immediate Actions:
   - Start Phase 1 with H-E1 — data retrieval and logistic fitting
   - Pre-confirm ground truth dates: GLUE → arXiv:1905.00537 (Sept 2019); SuperGLUE → BIG-bench (~2021)

2. Resource Allocation:
   - Allocate 8 weeks for critical path; reserve 1-2 week buffer for data quality issues (R1)
   - All implementation in Python with paperswithcode-client + scipy + numpy

3. Failure Management:
   - Document all failures with explicit root cause mapping to A1-A5
   - Execute sensitivity analysis at ±3/±6/±12 month windows for H-M4

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: `docs/youra_research/03_refinement.yaml` (ID: H-BenchSat-v1)
- Architecture: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- Convergence: All 6 criteria met at Exchange 7

**B. MCP Tool Usage Summary**
- Total MCP calls: 3 (internal reasoning substitutes in ablation mode)
- Tools planned: scientificmethod (3x), collaborativereasoning (1x), structuredargumentation (1x)
- Ablation note: No live MCP servers available; analysis performed via internal structured reasoning
