# Phase 2B Context: h-e1

**Generated:** 2026-08-29
**Source:** 02b_verification_plan.md

## Hypothesis

**ID:** h-e1
**Type:** EXISTENCE
**Statement:** Under decoder-only LLMs, if we compute UQ scores for LLM outputs, then at least one method achieves AUROC > 0.55 on hallucination detection, because uncertainty signals correlate with output quality.

## Gate Condition

- **Type:** MUST_WORK
- **Pass Condition:** At least one UQ method achieves AUROC > 0.55
- **Fail Action:** STOP - UQ methods do not work for hallucination detection

## Variables

- **IV:** UQ Method (token_entropy, semantic_entropy, p_true, selfcheckgpt)
- **DV:** AUROC for hallucination detection
- **CV:** LLM Model (Llama-3-8B), Sample Budget (10), Benchmark Splits

## Success Criteria

- **Primary:** At least one UQ method achieves AUROC > 0.55
- **Secondary:** All methods produce non-random uncertainty scores

## Experimental Setup

### Dataset
- **Name:** TruthfulQA mc1
- **Type:** standard
- **Source:** HuggingFace (truthful_qa)
- **Justification:** Standard factuality benchmark with ground truth labels

### Model
- **Name:** Llama-3-8B-Instruct
- **Source:** meta-llama/Meta-Llama-3-8B-Instruct
- **Type:** decoder-only transformer

## Dependencies

- **Prerequisites:** None (foundation hypothesis)
- **Dependents:** H-M1, H-M2, H-M3, H-M4, H-C1, H-C2

## Baseline Methods

| Method | Expected Performance | Notes |
|--------|---------------------|-------|
| Token Entropy | AUROC ~0.60-0.65 | Literature baseline |
| Random | AUROC = 0.5 | Null baseline |

## Risk Factors

- R1: Benchmark label quality
- R3: Implementation correctness
