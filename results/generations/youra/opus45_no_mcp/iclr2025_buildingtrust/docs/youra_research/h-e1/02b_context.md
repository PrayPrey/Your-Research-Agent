# Phase 2B Context: H-E1

**Hypothesis ID:** H-E1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Status:** IN_PROGRESS

## Hypothesis Statement

Under multiple-choice QA tasks, if CoT+confidence prompting is applied, then ECE can be reliably computed across all 5 conditions, because confidence values are extractable and accuracy is determinable.

## Rationale

Validates that the experimental infrastructure works. ECE computation requires both confidence extraction and accuracy measurement to succeed. This gates all subsequent mechanism tests.

## Variables

- **Independent:** Prompting strategy (5 levels: baseline, CoT-only, confidence-only, CoT+confidence, token-padding control)
- **Dependent:** ECE (15-bin, range [0,1])
- **Controlled:** Temperature=0, model family, dataset

## Success Criteria (PoC)

- **Primary:** Confidence extraction >95% success rate
- **Secondary:** ECE computable for all 5 conditions

## Verification Protocol

1. Run all 5 conditions on 100-item pilot sample from TruthfulQA
2. Extract confidence scores using regex pattern `Confidence: (\d+)%`
3. Verify >95% extraction success rate per Xiong et al. 2023 baseline
4. Compute ECE for each condition and verify values in valid range [0,1]

## Failure Response

IF fails → PIVOT (revise extraction prompt)

## Dependencies

None (root hypothesis)

## Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TruthfulQA + MMLU (standard) | TruthfulQA tests adversarial misconceptions; MMLU tests general knowledge |
| **Model** | GPT-3.5-turbo + Llama-2-70B-chat | Two major model families ensure findings aren't model-specific |

## Gate Condition

MUST_WORK: Extraction >95%, ECE computable for all 5 conditions. Failure blocks all downstream hypotheses (H-M1 through H-M4).

## Previous Hypothesis Results

None (first hypothesis in chain)

## Continuation Context

This is the first hypothesis in the verification chain. No prior results to build upon.
