# Phase 2B Context: H-M1

**Extracted:** 2026-08-10
**Source:** 02b_verification_plan.md

## Hypothesis Information

- **ID:** H-M1
- **Type:** MECHANISM
- **Statement:** Execution trace collection enables accurate token-level execution classification
- **Gate Type:** MUST_WORK
- **Prerequisites:** H-E1 (COMPLETED, PASS)

## Rationale

This validates the first causal step in the FGO mechanism chain. Without accurate trace collection, FGO cannot know which tokens to mask. StepCoder's trace collection must transfer to our PPO setup.

## Variables

- **Independent:** Trace collection (enabled vs disabled)
- **Dependent:** Token execution classification accuracy
- **Controlled:** Same test cases, same code samples

## Verification Protocol

1. Instrument test execution with Python trace module
2. Map line-level traces to token positions
3. Verify >95% accuracy in identifying executed vs non-executed tokens
4. Validate trace overhead is <20× slowdown

## Success Criteria (PoC)

- **Primary:** Token classification accuracy > 95%
- **Secondary:** Trace collection overhead < 20× baseline

## Failure Response

IF fails → EXPLORE (alternative trace methods: AST-based, bytecode)

## Dependencies

- H-E1 must pass (COMPLETED: PASS)

## Experimental Setup (from Phase 2B Section 1.3)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval + MBPP (standard) | Standard benchmarks for code generation evaluation |
| **Model** | CodeLlama-7B-Instruct | Widely used baseline; instruction-tuned for code tasks |

## Previous Hypothesis Results

### H-E1 Results (Prerequisite)
- **Status:** COMPLETED
- **Result:** PASS
- **Metrics:**
  - compile_improvement: 2.15
  - test_improvement: 2.24
  - combined_improvement: 2.24
- **Conclusion:** FGO token masking improves code generation performance across ALL feedback content types

## Context for This Experiment

H-M1 focuses on validating the **trace collection mechanism** that underlies FGO. While H-E1 proved FGO works, H-M1 verifies WHY it works by testing whether:
1. Python trace module can capture execution paths
2. Line-level traces can be accurately mapped to token positions
3. The mapping achieves >95% accuracy for executed/non-executed classification
