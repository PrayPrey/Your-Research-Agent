# Hypothesis Context: H-M2

**Generated:** 2026-07-11  
**Source:** Phase 2B Verification Plan (JIT Extraction)

---

## Hypothesis Information

**ID:** H-M2  
**Type:** Mechanism  
**Status:** NOT_STARTED

**Statement:**  
Staged progressive refinement (types→pre→post→inv) converges faster and achieves higher proof discharge than complete upfront specification

**Rationale:**  
Failure does not invalidate core approach - staged is optimization over baseline iterative

---

## Prerequisites

**Direct Dependencies:** [H-E1]

**Dependency Status:**
- H-E1: LLM + Structured Feedback Refinement - Foundation hypothesis

---

## Gate Condition

**Gate Type:** SHOULD_WORK (optimization, not core claim)

**Pass Criteria:**
- Staged converges in ≤70% of iterations vs. complete
- Staged achieves ≥5pp higher final proof discharge
- Statistical significance (p < 0.05)

**Failure Conditions:**
- Complete outperforms staged (backtracking overhead dominates)
- No significant difference (neutral result acceptable)

**Impact of Failure:** Does not block downstream hypotheses - positioned as optimization

---

## Experimental Setup (From Phase 2B Section 1.3)

### Dataset
**Type:** Verified C programs with gold ACSL annotations  
**Source:** Frama-C examples, Juliet verified subset  
**Benchmark Type:** Standard verification benchmarks  
**Fit:** Programs with deterministic behavior, verifiable safety/functional properties

### Model
**Type:** Large Language Model (API-based)  
**Options:** GPT-4 / Claude Opus (TBD in Phase 3)  
**Fit:** Strong reasoning capabilities for formal specification synthesis

---

## Experiment Sketch

**Approach:** Compare staged vs. complete strategies on shared benchmark with fixed iteration budget. Measure convergence speed and final performance.

**Key Comparison:**
- **Staged:** types → preconditions → postconditions → invariants (sequential)
- **Complete:** All spec components simultaneously from iteration 1

**Metrics:**
- Iterations to convergence
- Final proof discharge rate
- Statistical significance

---

## Success Criteria

✅ **Primary:**
- Staged converges in ≤70% of iterations vs. complete
- Staged achieves ≥5pp higher final proof discharge
- p < 0.05 statistical significance

✅ **Secondary:**
- Demonstrate systematic refinement (not random walk)
- Show clear convergence patterns per stage

---

## Failure Handling

**If Complete Outperforms Staged:**
- Position as neutral result (both strategies viable)
- Report that backtracking overhead dominates progressive benefits
- Does not invalidate core approach (SHOULD_WORK gate)

**If No Significant Difference:**
- Acceptable outcome - optimization hypothesis not confirmed
- Continue to Phase 5 without this optimization claim

---

## Previous Context

**Continuation from:** H-E1 (LLM + Structured Feedback)

**Expected Learnings from H-E1:**
- Proven LLM refinement loop implementation
- Baseline iterative performance metrics
- Optimal hyperparameters for feedback-driven refinement
- Validated benchmark programs

---

## Timeline Position

**Wave:** Wave 2 - Mechanism Layer  
**Weeks:** 09-14 (parallel with H-M1)  
**Dependencies:** H-E1 must pass MUST_WORK gate (Week 9)

**Execution Window:**
- Week 09-10: Implement staged & complete strategies
- Week 10-12: Comparative evaluation
- Week 12-14: Convergence analysis

---

## Risk Considerations

**R3 (Information Gradient) - Indirect:**  
If H-M1 fails (no information gradient), this hypothesis becomes less meaningful but still testable

**Position in Roadmap:**  
Optional optimization - failure does not block Phase 5 readiness

---

**Next Phase:** Phase 2C - Design detailed experiment specification for this hypothesis
