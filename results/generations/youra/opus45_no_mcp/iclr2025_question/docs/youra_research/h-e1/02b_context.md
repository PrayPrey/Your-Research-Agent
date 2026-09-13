# Phase 2B Context: H-E1

**Hypothesis ID:** H-E1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Status:** IN_PROGRESS

## Hypothesis Statement

Under QA task conditions with Llama-2-7B-chat, if we generate multiple responses per question and access token logits, then token entropy and semantic consistency can be computed for every response, because the model provides logit access and semantic similarity is computable via embedding models.

## Variables

- **IV:** Generation of N samples per question with logit access
- **DV:** Successful computation of (entropy, consistency) pair for each question
- **CV:** Model (Llama-2-7B-chat), samples (10), temperature (0.7)

## Verification Protocol

1. Load TriviaQA validation set (full ~11K questions for statistically meaningful evaluation)
2. Generate 10 responses per question with temperature 0.7
3. Compute token entropy from logit distributions
4. Compute semantic consistency via embedding cosine similarity
5. Verify both metrics computed successfully for >99% of questions

## Success Criteria (PoC)

- **Primary:** Both entropy and consistency computed for >99% of questions
- **Secondary:** Variance in both metrics across questions (not constant)

## Failure Response

- IF fails: PIVOT to alternative uncertainty estimation (e.g., verbalized)

## Experimental Setup

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | TriviaQA (standard) | Large-scale factual QA with ground-truth answers |
| **Model** | Llama-2-7B-chat | Open-source model with logit access |

### Dataset Details
- Source: mandarjoshi/trivia_qa (HuggingFace)
- Path: trivia_qa/rc.nocontext

### Model Details
- Type: instruction-tuned LLM
- Source: meta-llama/Llama-2-7b-chat-hf (HuggingFace)

## Dependencies

None (root hypothesis)

## Gate Condition

**MUST_WORK Gate:** If H-E1 fails → STOP, cannot proceed without metrics.

This is a prerequisite for all subsequent mechanism hypotheses (H-M1 through H-M4).
