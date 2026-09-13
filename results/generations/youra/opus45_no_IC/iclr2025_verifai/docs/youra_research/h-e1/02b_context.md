# Phase 2B Context: H-E1

**Hypothesis ID:** H-E1
**Type:** EXISTENCE
**Status:** IN_PROGRESS
**Gate:** MUST_WORK

## Hypothesis Statement

Error classes targeted by grammar constraints, static analysis, and SMT-guided repair are largely independent (overlap < 30% Jaccard index)

## Full Statement (from 02b_verification_plan.md)

Under HumanEval benchmark conditions, if grammar constraints, static analysis, and SMT-guided repair are applied independently, then the sets of problems improved by each strategy have Jaccard overlap < 30%, because each strategy targets fundamentally different error categories.

## Rationale

This hypothesis validates the core assumption that error classes are independent. If overlap exceeds 30%, the multiplicative improvement model fails and strategies are redundant rather than complementary.

## Variables

- **Independent:** verification_strategy (grammar, static, SMT)
- **Dependent:** error_overlap_rate (Jaccard index)
- **Controlled:** llm_model, benchmark_dataset, temperature (0.2), sample_count (n=10)

## Verification Protocol

1. Generate n=10 samples per HumanEval problem with baseline LLM
2. Apply each verification strategy independently, record improved problem sets
3. Compute pairwise Jaccard indices between strategy-improved sets
4. Aggregate across both LLM models (CodeLlama-7B, GPT-4)
5. Report mean and variance of overlap metrics

## Success Criteria (PoC: Direction-based)

- **Primary:** Jaccard(grammar_improved, static_improved) < 0.30
- **Secondary:** All pairwise overlaps < 0.30

## Failure Response

- IF fails: PIVOT to investigating which error classes overlap and why

## Dependencies

None (foundation hypothesis)

## Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval + HumanEval-Verus | Standard benchmark with test cases plus formal specs |
| **Model** | CodeLlama-7B, GPT-4 | Two models spanning capability spectrum |

## Gate Condition

Jaccard index < 0.30 for all strategy pairs

## Prerequisites

None - this is the foundation hypothesis

## Source

Phase 2A SH1, Prediction P1
