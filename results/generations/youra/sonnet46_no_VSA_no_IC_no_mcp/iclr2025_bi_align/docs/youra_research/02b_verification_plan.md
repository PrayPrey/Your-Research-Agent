---
stepsCompleted:
  - step-00-init-environment
  - step-01-init-parsing
  - step-02-input-hypothesis
  - step-03-hypothesis-generation
  - step-04-hypothesis-inventory
  - step-05-risk-analysis
  - step-06-dependency-graph
  - step-07-timeline-planning
  - step-08-dialectical-analysis
  - step-09-summary
  - step-10-finalize
status: complete
completedAt: "2026-08-26T00:00:00Z"
hypothesisId: H-BiAlign-v1
researchMode: incremental
totalHypotheses: 5
---

# Verification Plan: H-BiAlign-v1 — Bidirectional Alignment Tension in RLHF

**Date:** 2026-08-26
**Hypothesis ID:** H-BiAlign-v1
**Confidence:** 0.78
**Total Hypotheses:** 5
**Research Mode:** Incremental (60% scope reduction from Phase 2A established facts)

---

## Section 0: Established Facts & Scope Reduction

### BUILD_ON (Do NOT re-verify — 3 claims, 60% scope reduction)

| Claim | Evidence |
|-------|----------|
| Current AI alignment benchmarks predominantly measure AI→Human direction | ICLR 2025 Workshop (400 papers); TruthfulQA/BBQ/HELM/HHH-RLHF all measure AI output only |
| RLHF overoptimization creates proxy-gold divergence | Coste et al. 2023 (arXiv 2310.02743): RM score diverges from held-out gold preference under KL budget |
| Human-AI interaction produces over-reliance and automation bias | Lai et al. 2021: 60-80% human agreement with AI predictions regardless of AI accuracy |

### PROVE_NEW (Verification required — 2 claims, addressed by this plan)

| Claim | Addressed By |
|-------|-------------|
| No paper has co-measured both alignment directions for same model family | H-E1 |
| The proxy-gold divergence slope is significantly positive (calibration-alignment divergence) | H-M1, H-M2, H-M3, H-M4 |

**Phase 2B-4 Scope Instructions (from Phase 2A):**
Focus on: (1) digitization fidelity of figure data, (2) normalization protocol validity, (3) regression slope positivity in at least two independent datasets. Coverage ratio computation requires no experimental setup.

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under NLP alignment evaluation settings (published RLHF benchmark papers 2018-2024),
if AI→Human alignment optimization pressure increases (measured as KL budget from base policy),
then the calibration-alignment divergence gap (normalized RM score minus gold human preference rate)
increases monotonically with a significantly positive slope (β > 0, p < 0.05),
because RLHF trains against a proxy metric (reward model score) that diverges from actual human
behavioral response (gold preference) under sustained optimization — creating an anti-correlated
relationship between proxy-metric optimization and human-behavioral calibration satisfaction.

### 1.2 Alternative Hypothesis (H0)

There is no significant positive relationship between RLHF optimization pressure (KL budget)
and the calibration-alignment divergence gap (H0: β ≤ 0). Equivalently, improving AI→Human proxy
alignment metrics does not systematically degrade human calibration satisfaction.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Coste et al. 2023 + Gao et al. 2023 figure data (digitized) (standard) | Only published datasets providing both AI→Human proxy (RM score) and Human→AI-adjacent signal (gold preference) at varying optimization pressure for same model family |
| **Model** | Reward model + base LLM (as used in Coste et al. / Gao et al.) | Re-analysis of published experimental results — no new model training required |

**Dataset Details:**
- Source: Published figures from arXiv 2310.02743 (Coste) and arXiv 2210.10760 (Gao); digitized using WebPlotDigitizer
- Path: Available from published papers; raw data may be available in author GitHub repos

**Model Details:**
- Type: Autoregressive language model with RLHF fine-tuning
- Source: Described in Coste et al. 2023 and Gao et al. 2023 papers

### 1.4 Baseline Methods

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| Standard RLHF evaluation (RM score only) | High RM scores correlate with human preference at low KL; diverge at high KL | Coste et al. 2023 | Only measures AI→Human proxy; misses calibration degradation signal |
| ICLR 2025 Bidirectional Survey taxonomy | Qualitative identification of 400 papers; no quantitative coverage ratio | 400-paper literature review | Does not compute coverage ratio or divergence curve; purely descriptive |
| Lai et al. appropriate reliance measurement | 60-80% over-reliance rate in human-AI decision studies | Lai et al. 2021 | Measures user calibration directly but cannot be linked to AI→Human benchmark scores without additional experimental design |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Gold human preference in Coste et al. is a valid proxy for Human→AI calibration quality | Gold preference = held-out human evaluation not used in RM training; represents authentic human judgment | Core construct interpretation collapses; divergence curve cannot be reframed as bidirectional alignment evidence |
| A2 | Figure digitization yields sufficient precision for regression analysis | WebPlotDigitizer ~2-5% precision; large effect sizes in Coste et al. make this sufficient | Regression results may be imprecise; mitigate by reporting confidence intervals |
| A3 | Coverage ratio from Phase 1 benchmark paper list (n≈10) is representative of alignment evaluation literature | Includes most-cited benchmarks: TruthfulQA, BBQ, HELM, HHH-RLHF, WinoBias, InstructGPT, Constitutional AI | Coverage ratio has limited generalizability; note as limitation |
| A4 | RLHF overoptimization phenomenon generalizes beyond specific datasets/model families in Coste + Gao | Different model scales and datasets; convergent results suggest generalizability | Divergence curve is dataset/model specific; limit claims to exact experimental settings |
| A5 | Dual-axis classification schema applies reliably to benchmark metrics | Phase 1 cross-reference matrix shows clean separation: all 10 sources classifiable without ambiguity | Coverage ratio has low inter-rater reliability; mitigate with explicit rubric and kappa statistic |

### 1.6 Research Gap & Novelty

**Novelty:** First empirical quantification of the calibration-alignment divergence curve as a bidirectional alignment construct; first computation of the AI→Human coverage ratio using a dual-axis classification schema.

**Key Innovation:** Reframing RLHF reward hacking (proxy-gold divergence) as the empirical instantiation of bidirectional alignment tension; naming and quantifying the "calibration-alignment divergence curve" as a novel evaluation construct.

**Differentiation from Prior Work:**
- vs. ICLR 2025 Bidirectional Survey: That survey identifies the asymmetry qualitatively; we quantify it with a dual-axis schema and coverage ratio metric
- vs. Coste et al. 2023: Coste frames proxy-gold divergence as reward hacking; we reframe it as the first calibration-alignment divergence curve — a novel bidirectional alignment construct
- vs. Gao et al. 2023: Gao studies divergence scaling with model size; we use Gao's data to replicate under a bidirectional alignment interpretation

---

## 2. Hypotheses

### 2.1 Inventory

| ID   | Type      | Gate        | Prerequisites | Status      |
|------|-----------|-------------|---------------|-------------|
| H-E1 | EXISTENCE | MUST_WORK   | None          | READY       |
| H-M1 | MECHANISM | MUST_WORK   | H-E1          | NOT_STARTED |
| H-M2 | MECHANISM | MUST_WORK   | H-M1          | NOT_STARTED |
| H-M3 | MECHANISM | MUST_WORK   | H-M2          | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3          | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Bidirectional Signal Co-existence**

**Statement**: Under published RLHF experimental settings (Coste et al. 2023, Gao et al. 2023), if the experimental design tracks both reward model (RM) score and held-out gold human preference across varying KL budget levels for the same model family, then both signals co-exist as separable time-series in the same dataset, because the experimental protocols report both proxy and gold metrics at each KL checkpoint.

**Rationale**: Validates the foundational data infrastructure for the main hypothesis. Without confirmed co-existence of both directional signals in the same experiment, the divergence curve cannot be computed and all downstream H-M hypotheses are moot.

**Variables**:
- Independent: RLHF Optimization Pressure (KL budget)
- Dependent: RM score series + gold preference rate series (both must be present)
- Controlled: Same model family, same evaluation protocol across KL levels

**Verification Protocol**:
1. Access Coste et al. 2023 (arXiv 2310.02743) figures/data
2. Confirm both RM score and gold preference curves are reported at ≥5 KL levels
3. Access Gao et al. 2023 (arXiv 2210.10760) figures/data; confirm same structure
4. Apply WebPlotDigitizer to extract numerical values from both curves in both papers
5. Confirm digitized data has ≥5 paired (KL, RM_score, gold_preference) observations per paper

**Success Criteria** (PoC: Direction-based):
- Primary: Both RM score and gold preference curves present in ≥2 independent datasets with ≥5 KL levels each
- Secondary: Digitized data precision within ±5% visual inspection estimate

**Failure Response**:
- IF fails: PIVOT — contact authors for raw data; if unavailable, document as fundamental data availability limitation and reassess scope

**Dependencies**: None (foundation)

**Source**: Phase 2A SH1, Section 2 Experimental Setup

---
**H-M1: Proxy-Gold Metric Decoupling Under RLHF**

**Statement**: Under RLHF optimization on the same model family (Coste et al. 2023), if KL budget increases from 0 to high optimization pressure (~10 nats), then the RM score increases monotonically while gold human preference rate peaks (at intermediate KL) and reverses, because the reward model is trained to maximize a proxy that diverges from actual human judgment under sustained optimization.

**Rationale**: Tests the first causal step — whether proxy-gold decoupling empirically occurs in the digitized data. Established by Coste et al. but must be confirmed in our digitized version to ensure data fidelity for subsequent regression analysis.

**Variables**:
- Independent: KL budget (continuous, 0 to ~10 nats)
- Dependent: RM score trajectory (monotone?), gold preference trajectory (peak-reversal?)
- Controlled: Model family (Coste et al. same pretrained LLM), evaluation task domain

**Verification Protocol**:
1. Plot digitized RM score vs. KL budget from H-E1 data
2. Confirm monotone increase in RM score across all KL levels (Spearman ρ > 0.8)
3. Identify peak KL level for gold preference; confirm reversal post-peak
4. Compute difference (RM_final - gold_final) as preliminary divergence estimate
5. Compare visual pattern against Coste et al. paper figures for digitization fidelity check

**Success Criteria** (PoC):
- Primary: RM score monotonically increases AND gold preference shows peak-reversal in Coste et al. digitized data
- Secondary: Peak-reversal pattern consistent with visual inspection of paper figures

**Failure Response**:
- IF fails: EXPLORE — check digitization error; if data confirms no reversal, document fundamental data issue; PIVOT to requesting raw data

**Dependencies**: H-E1

**Source**: Phase 2A Causal Steps 1-2, Prediction P1

---
**H-M2: Divergence Gap Formation**

**Statement**: Under Coste et al. 2023 experimental data, if RM score is normalized to [0,1] range and gold preference rate is expressed as a fraction, then the calibration-alignment divergence gap (normalized RM score minus gold preference rate) is strictly positive at high KL levels and grows with increasing optimization pressure, because proxy-gold decoupling (confirmed in H-M1) creates a widening measurement gap.

**Rationale**: Tests the second causal step — that the proxy-gold decoupling translates into a well-defined, positive, growing divergence gap metric. This operationalizes the abstract bidirectional tension as a measurable quantity required for the regression in H-M3.

**Variables**:
- Independent: KL budget
- Dependent: Calibration-alignment divergence gap = normalize(RM_score) - gold_preference_rate
- Controlled: Normalization protocol (min-max within each paper's KL range)

**Verification Protocol**:
1. Apply normalization: RM_norm = (RM - RM_min) / (RM_max - RM_min) per paper
2. Compute gap = RM_norm - gold_preference_rate at each KL level
3. Verify gap is positive at ≥3 high-KL levels (KL > median)
4. Plot gap vs. KL budget to visualize growth trend
5. Report descriptive statistics (mean gap, max gap, proportion of KL levels with positive gap)

**Success Criteria** (PoC):
- Primary: Gap > 0 at high KL levels (≥3 of top 50% KL observations); gap increases directionally with KL
- Secondary: Gap metric is well-defined with no missing values in digitized data

**Failure Response**:
- IF fails: EXPLORE — recheck normalization protocol; if gap is negative, hypothesis may need reframing as "calibration-alignment convergence"

**Dependencies**: H-M1

**Source**: Phase 2A Causal Step 3, Prediction P1 test method

---
**H-M3: Regression Slope Significance (Primary Empirical Test)**

**Statement**: Under Coste et al. 2023 digitized data, if a linear regression is fit with KL budget as predictor and calibration-alignment divergence gap as outcome, then the regression slope β is significantly positive (β > 0, p < 0.05, R² > 0.5), because the divergence gap formed in H-M2 increases linearly (or super-linearly) with optimization pressure as RLHF compounds proxy-gold divergence.

**Rationale**: The primary statistical test of the main hypothesis. A significantly positive slope formally establishes the calibration-alignment divergence curve as a quantifiable bidirectional tension. This is the MUST_WORK gate for the entire verification plan.

**Variables**:
- Independent: KL budget (continuous predictor)
- Dependent: Calibration-alignment divergence gap (continuous outcome)
- Controlled: Model family, dataset (within Coste et al. analysis)

**Verification Protocol**:
1. Prepare regression dataset: (KL_level_i, gap_i) pairs from H-M2 computation
2. Fit OLS linear regression: gap ~ KL_budget + intercept
3. Extract β (slope), p-value (t-test), R², 95% CI for β
4. Apply same procedure to Gao et al. data as preliminary replication check
5. Report: β, SE, t, p, R², N (number of KL levels per dataset)

**Success Criteria** (PoC):
- Primary: β > 0 AND p < 0.05 AND R² > 0.5 in Coste et al. data (N ≥ 5)
- Secondary: β > 0 in Gao et al. preliminary check (formal test in H-M4)

**Failure Response**:
- IF fails (β ≤ 0 or p > 0.05): ABANDON H-BiAlign-v1; H0 is not rejected; document as negative result; route to Phase 0

**Dependencies**: H-M2

**Source**: Phase 2A Causal Step 3, Prediction P1 primary

---
**H-M4: Cross-Dataset Replication (Gao et al. 2023)**

**Statement**: Under Gao et al. 2023 (arXiv 2210.10760) digitized data (independent dataset, different model scale), if the same regression procedure from H-M3 is applied, then the slope β is again significantly positive (β > 0, p < 0.05), because the calibration-alignment divergence mechanism is a general property of RLHF optimization, not an artifact of Coste et al.'s specific model family.

**Rationale**: Tests generalizability across independent datasets. A single-dataset regression is weak; replication in Gao et al. (different model scale, different paper) provides cross-dataset validation needed to claim the divergence curve is a general phenomenon.

**Variables**:
- Independent: KL budget (continuous, from Gao et al. figures)
- Dependent: Calibration-alignment divergence gap (same computation as H-M3)
- Controlled: Same normalization protocol, same regression method

**Verification Protocol**:
1. Digitize Gao et al. 2023 KL-vs-reward/preference figures using WebPlotDigitizer
2. Apply identical normalization and gap computation as H-M2/H-M3
3. Fit OLS regression: gap ~ KL_budget on Gao et al. data
4. Compare slope magnitude and significance between Coste et al. and Gao et al.
5. Report joint replication summary: both β > 0, both p < 0.05 = successful replication

**Success Criteria** (PoC):
- Primary: β > 0, p < 0.05 in Gao et al. data (independent of Coste et al. result)
- Secondary: |β_Gao| within order of magnitude of |β_Coste| (consistent effect size)

**Failure Response**:
- IF fails: SCOPE — limit claims to Coste et al. only; document non-replication as scope limitation; label divergence curve as model-specific

**Dependencies**: H-M3

**Source**: Phase 2A Causal Step 4, Prediction P2

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type   | Pass Condition                                  | Fail Action                                      |
|------------|-------------|-------------------------------------------------|--------------------------------------------------|
| H-E1       | MUST_WORK   | Both RM + gold preference data present ≥2 datasets, ≥5 KL levels each | STOP — contact authors for raw data, reassess scope |
| H-M1       | MUST_WORK   | RM score monotone↑ AND gold preference shows peak-reversal in Coste et al. | EXPLORE digitization; PIVOT to raw data request |
| H-M2       | MUST_WORK   | Gap > 0 at ≥3 high-KL levels; grows directionally | EXPLORE normalization; PIVOT if gap is negative |
| H-M3       | MUST_WORK   | β > 0, p < 0.05, R² > 0.5 in Coste et al.     | ABANDON H-BiAlign-v1; route to Phase 0          |
| H-M4       | SHOULD_WORK | β > 0, p < 0.05 in Gao et al.                  | SCOPE to Coste et al. only; does NOT invalidate  |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks (W1-2) |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3 | 3 weeks (W3-5) |
| Phase 3: Replication | H-M4 | 1 week (W6) |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1 — Construct validity collapse | A1 | H-E1, H-M1, H-M2, H-M3, H-M4 | Critical |
| R2 — Digitization imprecision | A2 | H-M1, H-M2, H-M3, H-M4 | High |
| R3 — Coverage ratio unrepresentativeness | A3 | H-M4 | Medium |
| R4 — Limited generalizability | A4 | H-M4 | High |
| R5 — Classification schema low κ | A5 | H-M4 | Medium |

### 4.2 Mitigation Strategies

**R1 (Critical): Construct Validity Collapse**
- Prevention: Frame all claims as "evaluation calibration" not "user calibration"; add explicit construct validity section
- Detection: If H-M3 fails with β ≤ 0, assess whether construct invalidity is the cause
- Response: PIVOT to "proxy optimization efficiency degradation" framing; SCOPE to reward hacking reanalysis; ABORT if reviewers reject construct

**R2 (High): Digitization Imprecision**
- Prevention: Digitize each figure twice independently; use mean; report CI reflecting ±5% uncertainty
- Detection: Check that β CI excludes 0 with precision margins applied
- Response: PIVOT — contact Coste/Gao authors for raw data (Open Question Q1); SCOPE to directional claim if β not robustly > 0

**R3 (Medium): Coverage Ratio Unrepresentativeness**
- Prevention: Use 9 most-cited benchmarks from ICLR 2025 survey as reference set; report R with explicit denominator
- Detection: Sensitivity analysis — recompute R excluding each paper
- Response: SCOPE — report R with explicit caveat about n=9 sample

**R4 (High): Limited Generalizability**
- Prevention: Explicitly scope claims to "RLHF-trained LMs with published KL-budget data"
- Detection: If H-M4 fails, document as scope boundary not hypothesis failure
- Response: SCOPE — limit to Coste et al. only; reframe as "first instance" rather than "general phenomenon"

**R5 (Medium): Classification Schema Low κ**
- Prevention: Create explicit classification rubric with worked examples before applying; compute inter-rater kappa
- Detection: Apply schema to 3 papers first; refine if ambiguity arises
- Response: SCOPE — report kappa explicitly; if < 0.6, label R as "preliminary estimate"

### 4.3 Risk Summary

| ID | Risk | Severity | Affected | Primary Mitigation |
|----|------|----------|----------|--------------------|
| R1 | Construct validity collapse | Critical | All | Explicit "evaluation calibration" framing + PIVOT scope |
| R2 | Digitization imprecision | High | H-M1-4 | Dual-digitize + author contact |
| R3 | Coverage ratio unrep. | Medium | H-M4 | Sensitivity analysis + caveat |
| R4 | Limited generalizability | High | H-M4 | Explicit scope + PIVOT to Coste-only |
| R5 | Classification schema low κ | Medium | H-M4 | Rubric + inter-rater kappa |

**Risk Counts:** Critical: 1 | High: 2 | Medium: 2 | Low: 0

---

## 5. Dependency Graph (DAG) & Timeline

### 5.1 DAG Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root: Existence]
    H-E1  Bidirectional Signal Co-existence
    (no dependencies)
         │
         ▼
[Level 1 - Mechanism: Proxy-Gold Decoupling]
    H-M1  ← H-E1
    RM score monotone↑; gold preference peak+reversal
         │
         ▼
[Level 2 - Mechanism: Gap Formation]
    H-M2  ← H-M1
    Divergence gap = positive, grows with KL budget
         │
         ▼
[Level 3 - Mechanism: Primary Statistical Test]
    H-M3  ← H-M2
    β > 0, p < 0.05, R² > 0.5 (Coste et al.)
         │
         ▼
[Level 4 - Mechanism: Replication]
    H-M4  ← H-M3
    β > 0, p < 0.05 (Gao et al. independent)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Critical Gates (MUST_WORK): H-E1, H-M1, H-M2, H-M3
Optional Gate (SHOULD_WORK): H-M4
═══════════════════════════════════════════════════════════
```

### 5.2 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════════
Phase/Hypothesis      │ W1-2     │ W3       │ W4       │ W5       │ W6
──────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────
PHASE 1: Foundation
  H-E1 (Co-existence) │ ████████ │          │          │          │
  [Gate 1 - MUST]     │        ◆ │          │          │          │
──────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────
PHASE 2: Core Mechanisms
  H-M1 (Decoupling)   │          │ ████████ │          │          │
  H-M2 (Gap)          │          │          │ ████████ │          │
  H-M3 (Regression)   │          │          │          │ ████████ │
  [Gate 2 - MUST]     │          │          │          │        ◆ │
──────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────
PHASE 3: Replication
  H-M4 (Gao replic.)  │          │          │          │          │ ████████
  [Gate 3 - SHOULD]   │          │          │          │          │        ◆
──────────────────────┼──────────┼──────────┼──────────┼──────────┼──────────
═══════════════════════════════════════════════════════════════════════
Legend: ████ = Active work │ ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════════
```

### 5.3 Critical Path Analysis

```
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
Total Duration: 6 weeks
  Formula: 2 (H-E1) + 4×1 (H-M1 to H-M4) = 6 weeks
Slack: 0 weeks (all sequential)
Early Exit: Gate 1 (W2) or Gate 2 (W5) on critical failure
```

### 5.4 Execution Order

```
Step 1: Execute H-E1 (Foundation) — Week 1-2
Step 2: Evaluate Gate 1 → If pass: proceed; If fail: STOP
Step 3: Execute H-M1 (Proxy-Gold Decoupling) — Week 3
Step 4: Execute H-M2 (Divergence Gap Formation) — Week 4
Step 5: Execute H-M3 (Regression Slope Test) — Week 5
Step 6: Evaluate Gate 2 → β > 0, p < 0.05: proceed to H-M4
         β ≤ 0 or p > 0.05: STOP, route to Phase 0
Step 7: Execute H-M4 (Gao et al. Replication) — Week 6
Step 8: Evaluate Gate 3 → PASS: full divergence curve claim
         FAIL: scope-limited claim (Coste only)
Final:  Verification complete → Route to Phase 5 (Coverage Ratio / SH3)
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** H-BiAlign-v1 — As AI→Human RLHF optimization pressure (KL budget) increases, the calibration-alignment divergence gap increases monotonically with β > 0, p < 0.05.

**Supporting Evidence:**
1. Coste et al. 2023 demonstrates RM score rising while gold preference peaks then reverses
2. Gao et al. 2023 shows same qualitative pattern at different model scales
3. RLHF overoptimization theory (Ouyang et al. 2022) predicts proxy-gold divergence as general optimization phenomenon

**Strengths:**
- Grounded in two independent empirical datasets (Coste + Gao)
- Clear quantifiable mechanism: proxy metric ≠ gold metric
- Testable statistical prediction (β > 0, p < 0.05)
- Novel construct naming + coverage ratio operationalization

**Expected Outcomes:**
- Primary (P1): β > 0, p < 0.05, R² > 0.5 in Coste et al.
- Secondary (P2): Replication in Gao et al. with same direction
- Tertiary (P3): Coverage ratio R > 0.90 across benchmarks

### 6.2 Antithesis (H0-Based)

**Null Hypothesis (H0):** β ≤ 0 — no significant positive relationship between RLHF optimization pressure and calibration-alignment divergence gap.

**Counter-Arguments:**
1. Proxy-gold gap may reflect preference for output quality (length, fluency), not a bidirectional alignment construct — construct validity risk
2. Coverage ratio from n=10 papers may not generalize; ICLR 2025 (400 papers) provides no quantitative basis for R > 0.90 claim
3. Regression with n≈5-10 data points has very low statistical power; β > 0 may be spurious given wide CIs

**Potential Failure Points:**
- R1: Gold preference ≠ calibration proxy → entire framing is construct validity error
- R2: >10% digitization error → regression β could flip sign within precision margin
- R4: Non-replication in Gao → model-specificity rather than general phenomenon

**Conditions Under Which H0 Is Supported:**
- β ≤ 0 or p > 0.05 in Coste et al. regression (P1 fails)
- Gold preference does not reverse at high KL in digitized data (H-M1 fails)
- R < 0.80 in coverage ratio computation

### 6.3 Synthesis

**Balanced Assessment:**
H-BiAlign-v1 presents a theoretically coherent reframing of a known phenomenon (RLHF overoptimization) as a bidirectional alignment construct. The thesis is grounded in two existing empirical datasets and makes clear falsifiable predictions. H0 raises legitimate concerns: statistical power is limited (n≈5-10 per regression), construct validity of "evaluation calibration" as a bidirectional signal is contestable, and digitization imprecision could obscure the true effect.

**Resolution Path:**
1. **Foundation (H-E1):** Establish data fidelity before any inference — fail fast if data is unusable
2. **Sequential mechanism testing (H-M1→H-M3):** Each step independently falsifiable; early failure prevents wasted work
3. **SHOULD_WORK gate (H-M4):** Explicitly separates "single-paper effect" from "general phenomenon" — honest scope constraint

**Nuanced Outcome Possibilities:**
1. **Full Support:** H-E1 through H-M4 all pass → Divergence curve established as replicable bidirectional construct
2. **Partial Support:** H-M4 fails → Coste-only claim; publishable as single-paper reframing with replication caveat
3. **No Support:** H-M3 fails (β ≤ 0) → H0 retained; document as negative result; route to Phase 0

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Data existence | Both signals in Coste+Gao datasets | Data may not digitize cleanly | H-E1 test |
| Decoupling | RM↑ while gold preference peaks+reverses | Reversal may be noise artifact | H-M1 test |
| Gap metric | Gap positive and grows with KL | Gap may be non-monotone | H-M2 + plot |
| Significance | β > 0, p < 0.05 (large effect expected) | Low power, wide CI at n≈5-10 | H-M3 + CI reporting |
| Generalization | Gao et al. replicates pattern | Model-specific effect | H-M4 (SHOULD) |

**Overall Robustness Score:** Medium  
(Strong theoretical grounding and existing visual evidence; limited by small n per regression and digitization uncertainty)

**Confidence in Verification Plan:** 0.78

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-BiAlign-v1 — As RLHF optimization pressure (KL budget) increases, the calibration-alignment divergence gap (normalized RM score minus gold preference rate) increases with β > 0, p < 0.05, empirically establishing bidirectional alignment tension in published RLHF data.
- ID: H-BiAlign-v1, Confidence: 0.78

**Verification Structure:**
- Mode: Incremental (Phase 2A Dialogue available)
- Sub-Hypotheses: 5 total — H-E1 (Existence) + H-M1-4 (Mechanism)
- Phases: 3 phases over 6 weeks
- Critical Gates: 3 decision points (Gates 1-3); Gates 1 and 2 are MUST_WORK

**Risk Assessment:** Medium-High
- Primary concerns: R1 (construct validity, Critical), R2 (digitization imprecision, High)

**Scope Reduction:** 60% (3 established facts excluded from re-verification)

**Immediate Action:** Begin Phase 1 — H-E1 data acquisition and WebPlotDigitizer digitization of Coste et al. 2023 + Gao et al. 2023 figures

### 7.2 Key Achievements

- 5 hypotheses across 3 phases; H0 (β ≤ 0) explicitly addressed
- 60% scope reduction from Phase 2A established facts (3 BUILD_ON claims excluded)
- Sequential gate structure ensures early exit on critical failure before wasted analysis

### 7.3 Critical Decision Points

1. **Gate 1 (Foundation, W2):** H-E1 must pass
   - FAIL → STOP, contact authors for raw data, reassess scope

2. **Gate 2 (Primary Test, W5):** H-M3 must pass (β > 0, p < 0.05)
   - FAIL → STOP, route to Phase 0, new hypothesis needed
   - PASS → Continue to replication

3. **Gate 3 (Replication, W6):** H-M4 SHOULD pass
   - FAIL → Narrow scope to Coste et al. only; does NOT invalidate main claim

### 7.4 Open Questions

- Can Coste et al. raw data be obtained from authors to improve regression precision beyond figure digitization?
- Does the Lai et al. decision-making dataset have machine-readable format available on OSF or GitHub?
- Is the dual-axis classification schema reliable enough for inter-rater agreement measurement (kappa > 0.8)?

### 7.5 Recommendations

1. **Immediate Actions:**
   - Start H-E1: Access arXiv 2310.02743 and arXiv 2210.10760; begin WebPlotDigitizer extraction
   - Set up Python environment for OLS regression and normalization pipeline

2. **Resource Allocation:**
   - Allocate 6 weeks for critical path; no parallelism possible
   - Reserve 1-week buffer for digitization rework (R2 risk mitigation)

3. **Failure Management:**
   - Document all digitization precision metrics for transparency
   - Execute PIVOT to raw data request (Q1) immediately if H-E1 shows imprecision risk

---

## Appendices

### A. Phase 2A Reference
- **Source:** docs/youra_research/03_refinement.yaml (ID: H-BiAlign-v1)
- **Generated:** 2026-08-26, schema_version: 10.0.0, architecture: Self-Contained Tikitaka Loop (Independent-Controller Ablation)
- **Discussion exchanges:** 10, convergence: All 6 criteria met

### B. MCP Tool Usage Summary
- **Total MCP calls:** 0 (ablation mode — no MCP servers available in this session)
- **Reasoning method:** Scientific method applied analytically from Phase 2A structured data
- **Tools available in full mode:** mcp__clearThought__scientificmethod (3x), mcp__clearThought__structuredargumentation (1x), mcp__clearThought__collaborativereasoning (1x)
