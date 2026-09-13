# Phase 2B Context: H-M2 (Formal Verification Precision)

**Date:** 2026-08-25
**Hypothesis ID:** h-m2
**Type:** MECHANISM
**Status:** IN_PROGRESS

---

## Hypothesis Statement

Under formal constraint-satisfiability verification, if a hypothesis H is evaluated against the KB, then the system produces <25% false positives (marks untestable as testable), because the ∃ (D,B,M) verification logic correctly distinguishes measurable interventions from non-measurable ones.

---

## Rationale

Precision is critical. High false positive rate means researchers receive "testable" labels for untestable hypotheses, wasting experimental effort.

---

## Variables

- **Independent:** Verification logic (∃ (D,B,M) check)
- **Dependent:** False positive rate
- **Controlled:** Test set of labeled hypotheses (ground truth: expert-labeled)

---

## Verification Protocol

1. Create test set: 20 hypotheses (10 expert-labeled testable, 10 untestable)
2. Run formal verification on all 20
3. Measure false positives: (# untestable marked testable) / 10

---

## Success Criteria (PoC: Direction-based)

- **Primary:** False positive rate <25% (≤2 out of 10 untestable mislabeled)

---

## Gate Condition

- **Type:** MUST_WORK
- **If Fail:** EXPLORE stricter verification conditions or manual review step

---

## Prerequisites

- **h-m1:** KB Extraction Coverage (VALIDATED - 84% coverage)

---

## Experimental Setup

### Dataset
- **Name:** Test set of expert-labeled hypotheses
- **Type:** custom
- **Size:** 20 hypotheses (10 testable, 10 untestable)
- **Source:** Expert curation with ground-truth labels

### Model
- **Name:** Formal Constraint-Satisfiability Verifier
- **Type:** symbolic reasoning system
- **Source:** Custom implementation (∃ (D,B,M) verification logic)

---

## Dependencies

This hypothesis depends on h-m1 (KB Extraction Coverage). The KB constructed in h-m1 provides the (D,B,M) triples against which hypotheses are verified.

**h-m1 Results:**
- Coverage: 84% (42/50 datasets)
- Status: VALIDATED (gate PASSED)

---

## Source

Phase 2A Causal Mechanism Step 2, 02b_verification_plan.md lines 145-171
