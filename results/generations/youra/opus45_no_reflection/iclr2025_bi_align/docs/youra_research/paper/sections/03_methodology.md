# Methodology

## Problem Formulation

Standard DPO learns from preference pairs (x, y_w, y_l) where y_w is preferred over y_l for prompt x. We hypothesize that response text contains implicit agency signals—patterns indicating how the response engages users—that are orthogonal to preference labels.

BiDPO augments DPO with an auxiliary agency objective:

$$\mathcal{L}_{\text{BiDPO}} = \mathcal{L}_{\text{DPO}} + \lambda \cdot \mathcal{L}_{\text{agency}}$$

where λ ∈ [0, 1] controls the relative weight of agency preservation.

## Collaboration Score

We define a heuristic collaboration score that quantifies agency-preserving patterns in response text:

$$\text{collab\_score}(y) = \frac{\text{raw\_score}(y)}{\max(|y|/100, 1)}$$

The length normalization prevents bias toward verbose responses. The raw score aggregates three pattern categories:

**Reasoning Traces (0-40 points):** Explicit step-by-step explanations, causal connectives ("because," "therefore"), and enumerated reasoning. These patterns transfer the "how" of problem-solving.

**Uncertainty Acknowledgment (0-30 points):** Epistemic markers ("I think," "likely," "uncertain"), explicit limitations, and confidence calibration. These patterns preserve user agency by avoiding false certainty.

**Engagement Cues (0-30 points):** Questions to the user, clarification requests, and collaborative framing ("let's," "together"). These patterns invite continued dialogue.

## Agency Loss

Given collaboration scores for both responses in a preference pair, the agency loss encourages the model to favor more collaborative responses:

$$\mathcal{L}_{\text{agency}} = 1 - \text{collab\_score}(y_w) + 0.5 \cdot \text{collab\_score}(y_l)$$

This formulation creates gradient pressure toward higher collaboration in preferred responses while penalizing collaboration in rejected responses less strongly.

## Orthogonality Requirement

For the agency objective to provide novel training signal, collaboration scores must not be redundant with preference labels. We verify orthogonality by computing Pearson correlation between collaboration scores and preference indicators. If |r| < 0.7, we proceed with the heuristic; higher correlation would indicate the signal is already captured by preference optimization.

## Training Configuration

We train on Mistral-7B-Instruct-v0.2 using the HH-RLHF dataset (helpful-base split). Training parameters:
- β = 0.1 (DPO temperature)
- λ = 0.5 (agency weight)
- Learning rate: 5×10⁻⁷
- Batch size: 16 (via gradient accumulation)
- Precision: bfloat16
- Training steps: 250 (PoC scale)

At PoC scale, our goal is mechanism validation—does the signal integrate stably?—not efficacy demonstration. Full-scale training (1 epoch, ~10K steps) is identified as future work.

## Evaluation Protocol

We evaluate the causal chain through three experiments:

1. **Orthogonality (H-E1):** Compute correlation between collaboration scores and preference labels on held-out data.

2. **Training Stability (H-M1):** Monitor loss decrease and numerical stability (NaN/Inf counts) during BiDPO training.

3. **Generation Transfer (H-M2):** Generate responses from BiDPO and DPO models on held-out prompts, compute collaboration scores, test for statistically significant improvement.

Downstream MT-Bench and TruthfulQA evaluations were planned but blocked by H-M2 failure.
