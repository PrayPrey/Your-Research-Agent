# Hypothesis Context: H-M3

**Date:** 2026-08-25
**Hypothesis ID:** H-M3
**Type:** MECHANISM
**Gate:** MUST_WORK

---

## Hypothesis Statement

Under the framework applied to the corpus from H-E1, if we use Gate 1 micro-pilot (10 samples, <1 hour) to predict viability (overhead >threshold vs ≤threshold), then accuracy (TP + TN) / Total will exceed 80%, compared to 50% random guessing null hypothesis, because overhead scaling from H-M1 enables early prediction.

---

## Rationale

**CORE CLAIM** - validates primary prediction P1. This is the main testable hypothesis for the Pilot-Driven Viability Gates framework.

---

## Variables

- **Independent:** Viability Gate Stage (Gate 1 micro-pilot)
- **Dependent:** Prediction accuracy (0-100%)
- **Controlled:** Overhead threshold (10% for deployment context), hypothesis type

---

## Verification Protocol

1. For each hypothesis in corpus, apply Gate 1 prediction using O_10 × k.
2. Compare predicted viability (O_pred >threshold) to actual viability (O_full >threshold).
3. Classify: TP (correctly predicted non-viable), TN (correctly predicted viable), FP, FN.
4. Compute accuracy = (TP + TN) / 30.
5. Binomial test: accuracy >80% vs null hypothesis 50%, p <0.05.

---

## Success Criteria (PoC)

- **Primary:** Accuracy >80% (24/30 correct predictions), binomial test p <0.05
- **Secondary:** 60%+ non-viable filtered at Gate 1 (P2 claim)

---

## Failure Response

- IF accuracy ≤60%: MUST_WORK fail → Framework doesn't beat random + margin
- IF 60% <accuracy ≤80%: PARTIAL → Explore per-type thresholds or calibration

---

## Gate Condition

- Type: MUST_WORK (core claim)
- If Fail: Framework prediction claim unsupported

---

## Dependencies

**Prerequisites:** H-M2 (builds on scaling + updates)

**H-M2 Results (Prerequisite):**
- Status: VALIDATED
- Mean error reduction: 40.91%
- Paired t-test: t=4.453, p=0.0003
- Gate 1 mean error: 0.6966, Gate 2 mean error: 0.1111

---

## Dataset & Model (from Phase 2A)

**Dataset:** Retrospective ML Projects Corpus (custom)
- Source: Papers with Code leaderboards + conference papers with published micro-pilot data
- Target: 30 hypotheses (10 low-overhead <20%, 10 mid 20-80%, 10 high >80%)

**Model:** Gate 1 Viability Classifier
- Type: Classification model using O_10 × k to predict viability
- Input: 10-sample overhead measurement (O_10)
- Output: Binary classification (viable/non-viable)
- Baseline: Random guessing (50% accuracy)

---

## Source

Phase 2A Section 1.6 Prediction P1 (primary)
Phase 2B Section 2.2 (H-M3 specification)
