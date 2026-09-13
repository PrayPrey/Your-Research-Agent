# Experimental Setup

We design three experiments to test the BiDPO causal chain: (E1) orthogonality of collaboration scores, (E2) training stability, and (E3) generation-time transfer. Each experiment tests a specific link in the mechanism.

## E1: Orthogonality Validation (H-E1)

**Question:** Does the collaboration score capture information orthogonal to preference labels?

**Rationale:** If collaboration scores correlate strongly with preferences, the agency objective is redundant—DPO already optimizes for it. Orthogonality is a prerequisite for BiDPO to provide novel training signal.

**Method:** Sample 2000 response pairs from HH-RLHF (helpful-base). Compute collaboration scores for chosen and rejected responses. Test Pearson correlation between score and preference indicator.

**Success Criterion:** |r| < 0.7 (substantial non-redundancy).

## E2: Training Stability (H-M1)

**Question:** Does BiDPO train stably without numerical instabilities?

**Rationale:** Adding auxiliary objectives can destabilize optimization. We must verify that L_agency integrates with L_DPO without causing NaN/Inf values or divergent loss.

**Method:** Train Mistral-7B-Instruct-v0.2 on HH-RLHF (4000 samples, PoC scale) with BiDPO loss (λ = 0.5). Monitor loss curves and gradient norms. Run for 250 steps (1 epoch on PoC subset).

**Success Criteria:** 
- Training completes without NaN/Inf
- Final loss < initial loss

**Configuration:**
- Model: Mistral-7B-Instruct-v0.2
- β = 0.1, λ = 0.5
- Learning rate: 5×10⁻⁷ with cosine warmup
- Batch size: 16 (gradient accumulation)
- Precision: bfloat16

## E3: Generation Transfer (H-M2)

**Question:** Do BiDPO-trained models generate responses with higher collaboration scores?

**Rationale:** Training-time gradient pressure should produce generation-time behavioral change. This experiment tests whether the auxiliary objective transfers to inference.

**Method:** Generate responses from BiDPO and DPO models on 500 held-out prompts. Compute collaboration scores for each response. Perform one-sided t-test and effect size analysis.

**Success Criteria:**
- BiDPO mean > DPO mean (directional)
- p < 0.05 (statistical significance)
- Cohen's d ≥ 0.2 (small effect size)

**Generation Parameters:**
- Temperature: 0.7
- Top-p: 0.9
- Max tokens: 512

## Blocked Experiments (H-M3, H-M4)

The experimental design included MT-Bench and TruthfulQA evaluation (H-M3, H-M4) to test downstream effects on dialogue quality and factual accuracy. These experiments were blocked by H-M2 failure: without significant improvement in collaboration scores, evaluating downstream benchmarks would not test the hypothesized mechanism.

## Dataset

We use the Anthropic HH-RLHF dataset (helpful-base split), containing 170K human preference pairs over assistant responses. For PoC experiments, we subsample 4000 training pairs and 500 test prompts. The dataset provides:
- Paired preferences (chosen/rejected)
- Full response text (enabling collaboration score computation)
- Diverse task types (information, advice, creative)

## Baseline

Our baseline is standard DPO (λ = 0) trained with identical hyperparameters. This isolates the effect of the agency objective.
