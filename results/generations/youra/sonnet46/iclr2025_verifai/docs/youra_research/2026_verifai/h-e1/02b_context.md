# Phase 2B Context: H-E1 Tier Sample Size Viability

**Hypothesis ID:** H-E1
**Type:** EXISTENCE
**Generated:** 2026-03-18 (JIT by Phase 2C step-01 from 02b_verification_plan.md)

---

## Hypothesis Statement

Under k=5 self-contained solution generation on HumanEval+/MBPP+ (542 problems), if we stratify problems by pass@1 per model (hard = 0/5 correct, easy = ≥3/5 correct), then each tier will contain n≥20 problems per model per benchmark, enabling reliable ECE computation with M=15 bins.

## Type & Rationale

**Type:** EXISTENCE (foundational check)

**Rationale:** Reliable ECE computation requires sufficient samples per tier. The n≥20 threshold per (model, benchmark) combination ensures each calibration bin has meaningful population. This is the foundational check that gates all subsequent mechanism hypotheses.

## Variables

- **IV:** Difficulty tier assignment (hard/easy by pass@1 from k=5 solutions)
- **DV:** Tier sample size n per (model, benchmark) pair; threshold n≥20
- **CV:** 3 model families fixed; 542 total problems; EvalPlus augmented oracle

## Gate Condition

- **Gate Type:** MUST_WORK
- **Pass:** n_hard ≥ 20 AND n_easy ≥ 20 for ≥2/3 models on ≥1 benchmark
- **Fail Action:** Relax hard threshold to pass@1≤0.2; if still underpowered, PIVOT to pooled analysis or label as underpowered pilot

## Prerequisites

None (foundation hypothesis)

## Experimental Setup (from Phase 2A via Phase 2B)

### Dataset

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | HumanEval+ and MBPP+ (EvalPlus) | Augmented test suite (~760 tests/problem) provides reliable correctness oracle. 542 problems total (164 + 378) provides sufficient n for ECE per tier. Already validated in Run 3. |

- **Type:** standard (programmatic-api via pip)
- **Source:** Liu et al. 2023 (EvalPlus); https://github.com/evalplus/evalplus
- **Install:** `pip install evalplus`
- **Problems:** 164 (HumanEval+) + 378 (MBPP+) = 542 total
- **Test density:** ~760 augmented tests per problem

### Model

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Model** | Llama3-8B, CodeLlama-7B, DeepSeek-Coder-6.7B | Three families span general-purpose to code-specialized spectrum. Previously validated in Run 3 with successful P(True) elicitation. |

- **Type:** HuggingFace decoder-only LLMs
- **Sources:**
  - NousResearch/Meta-Llama-3-8B
  - codellama/CodeLlama-7b-hf
  - deepseek-ai/deepseek-coder-6.7b-base

### Verification Protocol (from Phase 2B)

1. Reuse Run 3 solutions (k=5 per problem, 3 models) or regenerate with fixed seed.
2. Run EvalPlus check_correctness for each (problem, solution) pair.
3. Compute pass@1 = correct_count/5 per (problem, model).
4. Assign tiers: hard = pass@1=0.0, easy = pass@1≥0.6, medium = excluded.
5. Count n_hard and n_easy per (model, benchmark); verify n≥20 for each.

### Success Criteria

- **Primary:** n_hard ≥ 20 AND n_easy ≥ 20 for ≥2/3 models on ≥1 benchmark
- **Secondary:** 6-point pass@1 distribution reported (0.0–1.0 histogram per model)

## Dependencies

- **Depends on:** None
- **Unlocks:** H-M1 (solution generation + oracle validation)

## Source

Phase 2A Section 5 (sh1_existence), Prediction P1 (viability precondition)
