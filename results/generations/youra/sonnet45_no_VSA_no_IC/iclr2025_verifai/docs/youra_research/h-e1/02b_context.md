# H-E1 Context (from Phase 2B)

**Generated**: 2026-08-20
**Hypothesis ID**: H-E1
**Type**: EXISTENCE
**Gate**: MUST_WORK

## Hypothesis Information

**Statement**: Pure automated prover (lean-auto) achieves 10-25% baseline success on miniF2F Lean 4 subset

**Rationale**: Foundation measurement for all comparisons. Establishes baseline automated proving capability without LLM assistance.

**Success Criteria**: 
- Code runs without error
- Success rate falls within 10-25% range
- N ≥ 50 problems evaluated

**Gate Condition**: MUST_WORK (foundation for H-M3, H-C1 and all LLM comparisons)

## Experimental Setup (from Phase 2B Section 1.3)

**Dataset**: miniF2F Lean 4 subset (N ≥ 50 problems)
**Model/Prover**: lean-auto (automated theorem prover with hammers)
**Configuration**:
- Tactic budget: 10 evaluations/problem
- Timeout: 300s per problem
- Mathlib version: Lean 4 compatible

**Baseline Comparison Target**: This IS the baseline (15% predicted)

## Dependencies

**Prerequisites**: None (independent measurement)
**Blocks**: H-M3 (corpus sampling), H-C1 (tactic budget equalization)

**Dependency Logic**:
- H-E1 must complete before H-M3 (needs lean-auto baseline for Δ comparison)
- H-E1 must complete before H-C1 (measures tactic count for budget equalization)

## Risk Assessment

**Risk Level**: LOW

**Known Risks**:
- Lean 4 subset size < 50 (Probability 20%, Impact MEDIUM)
  - Mitigation: Report as pilot, propose full Lean 4 port
- Infrastructure compatibility
  - Mitigation: Pilot N=20 problems to verify

**Pilot Protocol**: N=20 problems to verify lean-auto/miniF2F compatibility

## Context from Previous Hypotheses

N/A (first hypothesis in execution order)

## Controlled Variables (Main Hypothesis)

- Dataset: miniF2F Lean 4 subset (N≥50)
- Prover configurations: lean-auto (hammers), LeanCopilot (LLM-guided)
- Tactic budget: 10 evaluations/problem (equalized via H-E1 measurement)
- Timeout: 300s per problem
- Mathlib version: Lean 4 compatible
