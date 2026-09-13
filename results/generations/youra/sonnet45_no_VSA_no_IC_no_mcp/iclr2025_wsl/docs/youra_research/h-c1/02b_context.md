# Phase 2B Context: h-c1

**Hypothesis ID:** h-c1
**Type:** CONDITION
**Gate:** SHOULD_WORK
**Prerequisites:** h-m4

---

## Hypothesis Statement

Under domain boundary conditions, if a hypothesis is from a domain without established benchmark infrastructure (novel modalities, emerging applications), then the system correctly classifies it as "not testable" (or flags domain limitation), because the KB contains no matching (D,B,M) triples for that domain.

---

## Rationale

Scope boundaries are critical for system usability. If the system fails to detect out-of-scope domains, users receive misleading classifications.

---

## Variables

- **Independent Variable:** Domain type (benchmark-rich vs benchmark-poor)
- **Dependent Variable:** Classification accuracy on boundary cases
- **Controlled Variables:** Test set of 10 boundary hypotheses (5 novel modality, 5 emerging app)

---

## Success Criteria

**Primary:**
- ≥8/10 boundary cases correctly flagged

---

## Gate Condition

**Type:** SHOULD_WORK
**If Fail:** EXPLORE domain detection heuristics (keyword matching, metadata analysis)

---

## Verification Protocol

1. Curate 10 boundary hypotheses from domains known to lack benchmarks (e.g., olfactory AI, quantum ML)
2. Run system classification
3. Verify: system marks as "not testable" or flags "domain outside scope"

---

## Experimental Setup (from Phase 2B Section 1.3)

**Dataset:**
- Name: Papers With Code Catalog (Jan 2026 snapshot)
- Type: standard
- Source: https://paperswithcode.com/
- Storage: Scraped and stored as structured KB (YAML/JSON)

**Model:**
- Name: Formal Constraint-Satisfiability Verifier
- Type: symbolic reasoning system
- Source: Custom implementation (no pre-trained model required)

---

## Dependencies

**Prerequisites:** h-m4

**Prerequisite Results Summary:**
- h-m4 validates that system-classified 'testable' hypotheses yield ≥65% p < 0.05 results
- Successful (D,B,M) existence checks predict experimental feasibility

---

## Source

Phase 2A Section 1.5 Scope & Boundaries
02b_verification_plan.md Section 2.2
