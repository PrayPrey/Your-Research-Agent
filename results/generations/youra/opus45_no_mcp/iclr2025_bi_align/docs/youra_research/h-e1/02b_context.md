# Phase 2B Context: H-E1

**Hypothesis ID:** H-E1
**Type:** EXISTENCE
**Gate:** MUST_WORK

## Hypothesis Statement

Under RLHF benchmark evaluation, if we compute calibration scores across all tasks, then tasks showing calibration inversion (P(wrong) > P(correct) + 0.1) will cluster non-randomly (silhouette > 0.3), because systematic model behavior patterns exist.

## Success Criteria

- **Primary:** Silhouette score > 0.3
- **Secondary:** Clusters show distinct calibration profiles

## Failure Response

ABANDON - No systematic pattern exists to correlate with features

## Experimental Setup

### Dataset
- **Name:** Combined RLHF Benchmarks
- **Type:** standard
- **Source:** TruthfulQA (817 tasks) + ETHICS justice (~500 tasks) + HHH single-turn (~200 tasks)
- **Path:** Hugging Face datasets / lm-evaluation-harness
- **Total Samples:** ~1500

### Models
- Llama-2-7B-Chat (meta-llama/Llama-2-7b-chat-hf)
- Llama-2-13B-Chat (meta-llama/Llama-2-13b-chat-hf)
- Mistral-7B-Instruct (mistralai/Mistral-7B-Instruct-v0.2)

## Verification Protocol

1. Generate model responses with logprobs for all benchmark tasks (~1500 tasks)
2. Compute calibration score per task (sequence-level log probability, length-normalized)
3. Apply k-means clustering (k=3) on calibration scores
4. Compute silhouette score to validate cluster quality

## Dependencies

None (first hypothesis in chain)

## Gate Condition

This is a MUST_WORK gate. If silhouette score < 0.3, workflow STOPS.

## Risks

- R1 (High): Calibration scores unreliable/noisy
- R5 (High): Feature base rate outside informative range

## Mitigation

- Use length-normalized log probabilities
- Test multiple aggregation methods
- Validate feature base rate in preliminary analysis
