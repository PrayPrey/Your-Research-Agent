# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-PPVP-v1
**Confidence Level:** 0.85

**Main Hypothesis:**
Under the condition of Healthcare GenAI systems (LLMs and multimodal models) being deployed for clinical decision support, IF a Phased Prospective Validation Protocol (PPVP) with graduated exposure (Phase 0-Baseline, Phase I-Shadow Mode, Phase II-Pilot, Phase III-RCT) is implemented, THEN the system will achieve regulatory-acceptable evidence of safety and efficacy with 50% faster time-to-deployment compared to ad-hoc validation approaches, BECAUSE graduated exposure allows early identification of safety issues (>90% in Shadow Mode) while building incremental evidence for regulatory bodies, similar to how drug development Phase I/II/III trials manage risk while generating approval evidence.

**Alternative Hypothesis (H0):**
There is no significant difference between PPVP and ad-hoc validation approaches in terms of safety issue identification rate, time-to-deployment, or regulatory approval success. Ad-hoc approaches may achieve equivalent or better outcomes without the overhead of formalized phase transitions.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Validation Protocol Type | Independent | PPVP (4-phase graduated) vs. Ad-hoc validation | Categorical: PPVP / Ad-hoc |
| Risk Stratification Track | Independent | Track A (High-Risk: 4-phase) vs. Track B (Low-Risk: 3-phase) | Categorical: A / B |
| GenAI Application Type | Independent | High-Risk (diagnosis, treatment) vs. Low-Risk (documentation) | Categorical by clinical risk |
| Safety Issue Identification Rate | Dependent | % of critical discordances identified in Phase I before patient exposure | Target: >90% |
| Adverse Event Rate | Dependent | Serious adverse events per 1000 patient interactions in Phase II | Target: <1% (<10 per 1000) |
| Time-to-Deployment | Dependent | Months from Phase 0 initiation to Phase III completion | Track A: 12-24 mo, Track B: 6-12 mo |
| Regulatory Approval Success | Dependent | FDA/EMA approval granted with PPVP evidence package | Binary: Yes/No |
| Clinician Adoption Rate | Dependent | % of invited clinicians participating in Shadow Mode | Target: >75% |
| GenAI System Version | Controlled | Fixed model version; no updates during validation | Version-locked |
| Clinical Domain | Controlled | Specific specialty held constant within trial | e.g., Cardiology, Oncology |
| Patient Population | Controlled | Defined inclusion/exclusion criteria per phase | Representative demographics |

### 1.3 Causal Mechanism

**Causal Chain (N=4 steps):**

```
Phase 0 (Baseline) → Phase I (Shadow) → Phase II (Pilot) → Phase III (RCT) → Regulatory Approval
```

**Step 1: Phase 0 Retrospective Baseline → Phase I Shadow Mode Readiness**
- **Mechanism:** Establish performance bounds using existing benchmarks. Conduct regulatory pre-submission.
- **Evidence:** HealthBench provides 5,000 physician-graded conversations for baseline rubrics.
- **Duration:** 4-8 weeks

**Step 2: Phase I Shadow Mode → Phase II Pilot Safety Clearance**
- **Mechanism:** AI runs parallel to clinician decisions with no patient exposure. Target >90% safety issue identification.
- **Evidence:** NAVOY Sepsis achieved 0.79 accuracy in prospective validation. RWE-LLM demonstrated 6,234 clinicians can validate at scale.
- **Duration:** 8-16 weeks, minimum 1,000 shadow decisions

**Step 3: Phase II Pilot Deployment → Phase III RCT Evidence (HIGH-RISK TRACK ONLY)**
- **Mechanism:** Limited patient cohort (n=200-500) with mandatory clinician override.
- **Evidence:** STRATIFYHF protocol recruiting 1,600 participants validates multicentre feasibility.
- **Duration:** 12-24 weeks, exit criterion: <1% serious adverse events

**Step 4: Phase III RCT Completion → Regulatory Approval + Clinical Adoption**
- **Mechanism:** RCT comparing AI-assisted care to standard care. Non-inferiority design.
- **Evidence:** EU AI Act Article 43(3) allows MDR certification for AI devices.
- **Duration:** 24-52 weeks

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Phase 0 → Phase I | HealthBench (OpenAI) | 5,000 realistic conversations with physician rubrics | Strong |
| Phase I → Phase II | NAVOY Sepsis (2024) | 0.79 accuracy, 0.80 sensitivity in prospective ICU | Strong |
| Phase I → Phase II | RWE-LLM (Hippocratic AI) | 307K calls validated by 6,234 clinicians | Strong |
| Phase II → Phase III | STRATIFYHF (2025) | 1,600 participants, 24-month multicentre protocol | Strong |
| Phase III → Approval | EU AI Act Article 43(3) | MDR certification pathway for high-risk AI devices | Medium |

**Key Tension:**
- **Tension:** STRATIFYHF and NAVOY Sepsis are single-disease/single-application studies, while PPVP claims GENERAL-PURPOSE transferability.
- **Resolution:** Verification plan tests generalizability across 2+ distinct clinical domains with different risk profiles.

### 1.4 Key Assumptions

| # | Assumption | Supporting Evidence | Consequence if Violated |
|---|------------|-------------------|------------------------|
| 1 | Institutions have capacity for multi-phase validation | RWE-LLM: 307K calls by 6K clinicians | May require consortium approach |
| 2 | Clinicians willing to participate in Shadow Mode | RWE-LLM high participation rates | Phase I duration extends; additional incentives needed |
| 3 | Regulators accept AI-adapted trial methodology | FDA AI/ML guidance, EU AI Act 43(3) | Evidence package rejected; revision required |
| 4 | Patient populations available for Phase II/III | STRATIFYHF 1,600 participants | Trial underpowered; multi-institutional collaboration |

### 1.5 Scope & Boundaries

**Applies To:**
- Healthcare GenAI systems for clinical decision support
- Applications: diagnosis, treatment, documentation, triage
- Regulatory contexts: FDA, EMA, similar frameworks

**Does NOT Apply To:**
- Fully autonomous AI without clinician oversight
- Non-healthcare AI applications
- Real-time critical systems requiring immediate deployment

**Limitations:**
- Resource-intensive (12-24 months for Track A)
- Requires clinical trial infrastructure
- Not validated for pediatric populations
- Assumes stable GenAI version

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Safety Issue Identification in Shadow Mode):**
If Phase I Shadow Mode is implemented with minimum 1,000 parallel decisions, then >90% of safety-critical discordances will be identified before patient exposure.

*Measurement:* Safety Issue Identification Rate > 90% (p < 0.05)
*Falsification:* Rate ≤ 70% triggers rejection

**Secondary Predictions:**

**P2 (Phase II Adverse Event Control):**
<1% serious adverse event rate in Pilot Deployment with statistically significant outcome improvement.

**P3 (Time-to-Deployment Efficiency):**
50% shorter total validation time compared to ad-hoc approaches.

**P4 (Regulatory Acceptance):**
>80% regulatory acceptance rate for PPVP evidence packages.

**Falsification Criteria:**

The hypothesis will be **REJECTED** if:

1. **Primary Failure:** Safety Issue Identification Rate ≤ 70%
2. **Mechanism Failure:** Phase II adverse event rate exceeds 5%
3. **Efficiency Failure:** Time-to-deployment equals or exceeds ad-hoc
4. **Generalization Failure:** Protocol fails to transfer across 2+ clinical domains

**Statistical Verification Design:**
- Primary (P1): One-sample proportion test, α = 0.05
- Sample: Minimum 50 safety-relevant decisions per domain
- Phase II: n = 200-500 participants with interim analysis
- Report format: Proportion, 95% CI, p-value

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does PPVP successfully identify safety issues in Shadow Mode before patient exposure at rates exceeding retrospective-only approaches?"
- Maps to: Primary prediction (P1)
- Verification type: Empirical
- Critical: MUST PASS

**SH2 (Mechanism):**
"Does graduated exposure (Phase 0→I→II→III) correctly manage risk while building regulatory evidence?"
- Maps to: Causal mechanism (N=4 steps)
- Decomposes into 4 sub-hypotheses:
  - H-M1: Phase 0 → Phase I transition
  - H-M2: Phase I → Phase II transition
  - H-M3: Phase II → Phase III transition
  - H-M4: Phase III → Regulatory Approval
- Verification type: Causal analysis

**SH3 (Comparison):**
"Does PPVP achieve faster time-to-deployment and higher regulatory acceptance vs. ad-hoc approaches?"
- Maps to: Secondary predictions (P3, P4)
- Verification type: Comparative empirical

**Total Sub-Hypotheses for Phase 2B:** 6 (SH1 + SH2×4 + SH3)

### Readiness Checklist

- [x] Hypothesis in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID: H-PPVP-v1
- [x] Confidence level: 0.85
- [x] Alternative hypothesis (H0) defined
- [x] All variables operationalized
- [x] Causal mechanism with evidence (N=4 steps)
- [x] Key tension identified with resolution
- [x] Assumptions list consequences if violated
- [x] Testable predictions (4 total, P1 primary)
- [x] Falsification criteria defined (4 criteria)
- [x] Baselines identified (ad-hoc, RWE-LLM, STRATIFYHF)
- [x] SH1, SH2, SH3 clear starting points

### Open Questions

1. **Resource Requirements:** Minimum institutional capacity for Phase I Shadow Mode?
2. **Regulatory Pre-Engagement:** FDA Q-Sub timing - Phase 0 or Phase II?
3. **Cross-Domain Priority:** Which 2 clinical domains for initial validation?
4. **Track Selection Criteria:** Quantitative thresholds for Track A vs. Track B assignment?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
