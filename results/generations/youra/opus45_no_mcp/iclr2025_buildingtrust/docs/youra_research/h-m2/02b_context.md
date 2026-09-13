# Phase 2B Context: H-M2

**Extracted From:** 02b_verification_plan.md
**Date:** 2026-08-19

## Hypothesis Information

- **ID:** H-M2
- **Type:** MECHANISM
- **Statement:** Under CoT+confidence conditions, if reasoning chains are generated, then outputs will contain uncertainty indicators (hedging words, qualifications, alternatives), because complex reasoning surfaces epistemic uncertainty.
- **Rationale:** Validates Step 2 of causal mechanism. The hypothesis predicts reasoning chains contain signals that inform confidence. Finding no hedging markers would falsify the mechanism.
- **Prerequisites:** H-M1 (VALIDATED)
- **Gate:** SHOULD_WORK

## Success Criteria (PoC)

- **Primary:** Hedging markers present in >30% of CoT outputs
- **Secondary:** Marker frequency correlates with item difficulty

## Variables

- **Independent:** Reasoning chain presence
- **Dependent:** Hedging marker count (might, possibly, alternatively, however)
- **Controlled:** Temperature=0, item difficulty distribution

## Verification Protocol

1. Extract reasoning chains from CoT+confidence outputs on full TruthfulQA (817 items)
2. Count hedging markers using keyword list: might, possibly, could, perhaps, alternatively, however, uncertain
3. Compare marker frequency across item difficulty levels
4. Verify markers are present and vary with difficulty

## Failure Response

IF fails → EXPLORE (expand hedging marker dictionary)

## Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TruthfulQA (817 items) | Tests adversarial misconceptions; covers calibration across factual domains |
| **Model** | GPT-3.5-turbo + Llama-2-70B-chat | Two major model families ensure findings aren't model-specific |

**Dataset Details:**
- Source: HuggingFace datasets
- Path: truthful_qa (generation subset)
- Split: Full validation set (817 items)

**Model Details:**
- Type: instruction-tuned chat models
- Source: OpenAI API, HuggingFace/Together AI
- Temperature: 0 (deterministic)

## Continuation Context

### Previous Hypothesis Results (H-M1)

H-M1 VALIDATED with following metrics:
- CoT reasoning rate: 1.0 (100% of CoT outputs contain multi-step reasoning)
- Baseline reasoning rate: 0.0
- Rate difference: 1.0
- Mean step count: 2.61 (> 2.0 threshold)
- All gates passed

**Implications for H-M2:**
- CoT reliably produces reasoning chains (H-M1 confirmed)
- H-M2 now tests whether these chains contain uncertainty indicators
- Use same CoT+confidence outputs from H-M1 validation

## Dependencies

- **H-E1:** VALIDATED - ECE computation confirmed working
- **H-M1:** VALIDATED - CoT reasoning chain generation confirmed
