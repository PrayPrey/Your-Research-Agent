# Hypothesis Context: H-M1

**Generated:** 2026-04-20
**Source:** Phase 2B Verification Plan (Section 2.2)

---

## Hypothesis Information

**ID:** H-M1
**Type:** MECHANISM
**Statement:** Under neural theorem proving, if LLM confidence (softmax entropy) is measured during proof search, then confidence reflects familiarity with proof state patterns from training distribution, because the model's uncertainty increases when encountering states outside the manifold of successful proofs seen during training.

**Rationale:** Tests the first step of the causal chain - that confidence is a geometric proxy for proof space manifold structure, not just random noise.

---

## Variables

- **Independent:** Proof state characteristics (novel vs. familiar patterns)
- **Dependent:** LLM confidence (softmax entropy)
- **Controlled:** Base model (ReProver), training data distribution

---

## Verification Protocol

1. Collect proof states from successful and failed searches
2. Measure confidence at each state
3. Analyze correlation between state novelty and confidence levels
4. Verify that successful proofs show stable confidence patterns

---

## Success Criteria (PoC: Direction-based)

- **Primary:** Successful proofs show lower variance in confidence than timeouts
- **Secondary:** Confidence trajectory analysis shows geometric clustering

---

## Gate Condition

**Type:** MUST_WORK
**Pass Condition:** Successful proofs show lower variance in confidence than timeouts
**Fail Action:** PIVOT to symbolic-only approach

---

## Dependencies

**Prerequisites:** H-E1 (must establish correlation exists)

**Previous Results:**
- H-E1: COMPLETED, PASSED
- Pearson r = 0.8048, p = 6.218e-24
- Spearman ρ = 0.7954, p = 4.919e-23
- AUC = 0.9755
- Sample size = 100
- Gate satisfied: TRUE

**Key Findings from H-E1:**
- Strong correlation found between confidence derivatives and timeout outcomes
- Foundation hypothesis validated - confidence signals are highly predictive
- Mock test validates methodology works
- Ready for mechanism investigation

---

## Experimental Setup (from Phase 2B Section 1.3)

**Dataset:** LeanDojo Benchmark (standard)
- Source: Yang et al., 2023 - 98,734 theorems from Lean math library
- Path: https://github.com/lean-dojo/LeanDojo
- Justification: Standard benchmark for neural theorem proving

**Model:** LeanDojo ReProver
- Type: Retrieval-augmented LLM for theorem proving
- Source: Yang et al., 2023
- Justification: State-of-the-art LLM-based prover with accessible confidence scores via DojoCritic interface

---

## Baseline & Comparison Targets

**Baseline Methods (for Phase 5 comparison):**
- LeanDojo ReProver: 48.9% success rate on held-out theorems
- Dataset: LeanDojo benchmark (98,734 theorems)

---

## Source Reference

**Phase 2B Section:** 2.2 - Hypothesis Specifications (H-M1)
**Phase 2A Source:** Causal Step 1
