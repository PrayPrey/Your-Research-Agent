# Phase 2B Context: h-m3 (Confound Flagging Precision)

**Date:** 2026-08-25
**Hypothesis ID:** h-m3
**Type:** MECHANISM
**Status:** IN_PROGRESS

---

## Hypothesis Statement

Under confound pattern detection, if the system flags hypotheses with known confounds from literature, then precision >40% is achieved on labeled confound cases, because cross-domain confound patterns (tokenizer-size, resolution-architecture) generalize across DL subfields.

---

## Rationale

Confound flagging prevents "technically correct but pragmatically useless" outputs. Low precision creates noise (false alarms reduce trust). This extends h-m2's testability classification with a second layer: "should this be tested?" (confound detection) vs "can it be tested?" (∃(D,B,M) verification).

---

## Variables

- **Independent:** Confound database (NLP/vision/training patterns)
- **Dependent:** Flagging precision
- **Controlled:** Labeled confound test set (15 known-confounded, 15 unconfounded)

---

## Verification Protocol

1. Populate confound database with literature patterns (tokenizer-size ↔ BLEU, resolution ↔ accuracy)
2. Run confound flagging on 30 labeled hypotheses
3. Measure precision: (true positives) / (true positives + false positives)

---

## Success Criteria (PoC: Direction-based)

- **Primary:** Precision >40%

---

## Gate Condition

- **Type:** SHOULD_WORK
- **If Fail:** PIVOT to domain-specific confound databases (skip cross-domain transfer claim)

---

## Prerequisites

- **h-m2 (Formal Verification Precision):** COMPLETED
  - Status: PASS (FPR=0.0 < 0.25 threshold)
  - Provides: KB with 49 (D,B,M) triples, verified extraction logic
  - Limitation: Does not detect confounds (only checks existence)

---

## Experimental Setup (from Phase 2B Section 1.3)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Confound-Labeled Hypothesis Test Set (custom) | Manually curated hypotheses with literature-verified confound ground truth |
| **Model** | Cross-Domain Confound Pattern Detector | Rule-based keyword matching with literature-sourced pattern database |

**Dataset Details:**
- Source: Custom generation (literature-based confound examples)
- Size: 30 hypotheses (15 confounded, 15 unconfounded)
- Domains: NLP (5), Vision (5), Training (5) per category

**Model Details:**
- Type: Symbolic reasoning system (rule-based)
- Source: Custom implementation (no pre-trained model)

---

## Baseline Methods

| Method | Performance | Why Insufficient |
|--------|-------------|------------------|
| Random Flagging | ~50% precision | No reasoning; pure baseline |

---

## Dependencies

- **h-m2:** Provides verified testability classification system
- **Literature:** Confound patterns from Salesky et al. 2020 (tokenizer-BLEU), Touvron et al. 2019 (resolution-accuracy), Goyal et al. 2017 (batch-LR)

---

## Key Assumptions

- **A1:** Cross-domain confound patterns generalize (NLP tokenizer-metric ≈ vision resolution-metric structurally)
- **A2:** Literature-sourced patterns cover representative confound cases
- **A3:** Keyword-based matching captures pattern instances reliably

---

*Generated: 2026-08-25 (JIT from 02b_verification_plan.md)*
