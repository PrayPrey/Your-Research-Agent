# Phase 2B Context: H-M1

**Generated:** 2026-07-11  
**Hypothesis ID:** h-m1  
**Type:** MECHANISM  
**Status:** IN_PROGRESS

---

## Hypothesis Statement

Information gradient hypothesis: Proof discharge rate scales monotonically with feedback richness (FullStructured > ObligationSlice > TagOnly > RawError by ≥10pp between adjacent conditions)

---

## Gate Configuration

**Type:** MUST_WORK  
**Rationale:** Core mechanism claim - if ablation shows no gradient, information-theoretic framing is invalid  
**Prerequisites:** h-e1  
**Current Status:** Not Satisfied (null)

---

## Success Criteria

- Monotonic ordering holds: C > B > A > Raw
- Adjacent gaps ≥10 percentage points
- Regression coefficients strictly positive (p < 0.05)

---

## Failure Conditions

- Non-monotonic ordering (e.g., B > C or A > B)
- Adjacent gaps ≤5 percentage points (no gradient)
- Regression shows no significant relationship

---

## Experiment Sketch

Controlled ablation across 4 feedback conditions on 30-50 benchmark programs, regression analysis with pre-registered monotonic ordering.

---

## Research Variables

**Independent Variables:**
1. **FeedbackCondition**: Type of feedback provided to LLM
   - FullStructured (C): All three dimensions (Witness + Structure + Dependency)
   - ObligationSlice (B): Structure + Dependency only
   - TagOnly (A): Structure only
   - RawError (Raw): Unstructured verifier output

**Dependent Variables:**
1. **ProofDischargeRate** (Primary): Percentage of proof obligations successfully discharged (0-100%)
2. **IterationsToConvergence**: Number of refinement iterations until stabilization (1-10)

**Controlled Variables:**
- ComputeBudget (tokens + verifier time)
- BenchmarkPrograms (verified C programs with ACSL annotations)
- VerifierToolVersion (Frama-C WP, Z3/Alt-Ergo backends)
- LLMModel (GPT-4 / Claude Opus)

---

## Dependencies

**Prerequisites:** 
- h-e1 (VALIDATED) - LLM + Structured Feedback Refinement

**Status of Prerequisites:**
- h-e1: VALIDATED ✓
  - Mean discharge rate: 62.9%
  - Target achieved: 50%
  - All programs improved: 100%

---

## Continuation Context

This hypothesis builds on h-e1's validated finding that LLMs can utilize structured feedback. H-M1 now tests the core mechanism: whether there is a measurable information gradient where more structured feedback leads to better performance.

The ablation study will validate the information-theoretic framing of the verifier-as-teacher approach. If the gradient does not hold, the theoretical foundation requires revision.

---

## Risk Analysis

**Primary Risks:**
- R3: Information gradient ordering may not hold empirically (HIGH severity, 0.3 probability)
  - Mitigation: Pre-registered regression with monotonic ordering
  - Contingency: Revise to comparative claim (FullStructured vs RawError only)

**Mitigation Strategies:**
1. Pre-register regression analysis with expected monotonic ordering
2. Define explicit falsification boundary: non-monotonic or ≤5pp gaps
3. Fallback to pairwise comparisons if full ordering fails

---

## Dataset & Model Context

**Dataset:** Verified C programs with gold ACSL annotations  
**Source:** Frama-C examples, Juliet verified subset  
**Scale:** 30-50 benchmark programs for ablation study

**Model:** GPT-4 / Claude Opus (TBD in Phase 3)  
**Task:** Specification synthesis with iterative refinement

---

*Source: 02b_verification_plan.md Section 2.2 (H-M1)*
