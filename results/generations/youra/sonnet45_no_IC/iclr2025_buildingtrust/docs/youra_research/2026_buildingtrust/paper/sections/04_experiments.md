# Experimental Setup

Our experiments test four hypotheses in a hierarchical design: existence (h-e1) validates that synchronized multi-dimensional measurement is feasible, then three mechanism hypotheses (h-m1, h-m2, h-m3) test specific coupling patterns and their causal explanations.

## Research Questions

**RQ1 (Existence):** Do synchronized multi-dimensional measurements produce sufficient variance for correlation analysis?

Without adequate variance (σ>0.2) across reliability, robustness, and fairness dimensions, correlation estimates become unstable and floor/ceiling effects preclude meaningful analysis. This foundational question validates our methodological approach before testing coupling hypotheses.

**RQ2 (Memorization Mechanism):** Is reliability-robustness correlation positive (r>0.3) on factual content, driven by shared memorization?

If pre-training creates factual knowledge representations that enable both accurate retrieval (reliability) and consistent paraphrasing (robustness), we expect strong positive correlation on prompts where memorization is relevant (factual questions with clear ground-truth answers).

**RQ3 (Alignment Tax Mechanism):** Is fairness-reliability correlation negative (r<-0.2) overall, driven by RLHF safety-accuracy trade-off?

If RLHF fine-tuning prioritizes demographic fairness over factual accuracy on socially sensitive questions, we expect negative correlation where improving fairness (reducing bias variance) degrades reliability (hedging reduces correctness).

**RQ4 (Moderation):** Do correlation magnitudes differ significantly between factual vs. misinformation prompt strata?

If memorization mechanism is specific to factual content (not universal), factual prompts should show stronger reliability-robustness coupling than misinformation prompts requiring reasoning over conflicting information.

## Datasets

**Primary:** TruthfulQA generation split (817 prompts)  
- Source: HuggingFace `truthful_qa/generation`
- Categories: Science (n=94), Law (n=76), History (n=95), Geography (n=78), Myths (n=147), Misconceptions (n=189), Superstitions (n=138)
- Stratification: Factual stratum (Science, Law, History, Geography: n=343) vs. Misinformation stratum (Myths, Misconceptions, Superstitions: n=474)
- Ground truth: Binary correct/incorrect labels for reliability evaluation

**Rationale:** TruthfulQA provides standardized reliability labels, sufficient sample size for powered correlation tests (n=817 exceeds required n≥682 for 80% power at r=0.1), and natural stratification for testing mechanism specificity (factual vs. misinformation question types).

**Augmentation for fairness:** Each prompt augmented with four demographic descriptors (Black, Asian, White, Hispanic) to create fairness variance via HONEST demographic bias measurement. Example:

- Original: "What is the capital of France?"
- Augmented: "A Black doctor asks: What is the capital of France?" (repeated for Asian, White, Hispanic)

Total inferences: 817 prompts × 3 model scales × (1 base + 4 demographic variants) = 12,255 generations.

## Models

**Llama-2-chat models:** 7B, 13B, 70B parameter scales  
- Source: HuggingFace `meta-llama/Llama-2-{7,13,70}b-chat-hf`
- Architecture: Decoder-only transformer with RLHF fine-tuning
- Primary results: 7B (detailed); 13B, 70B planned for scale generalization (not executed in h-m2/h-m3)

**Generation parameters (synchronized):**
- Temperature: 0.7
- Top-p: 0.9
- Max tokens: 256
- Seed: Fixed per prompt (deterministic generation)

**Rationale:** Llama-2 provides consistent architecture across scales (tests scale moderation), is open-source (reproducibility), and widely studied in trustworthiness research. Generation parameters match standard practice for natural language generation (avoiding greedy decoding artifacts while maintaining reproducibility via fixed seeds).

## Evaluation Metrics

### Reliability (Factual Correctness)

**Primary:** GPT-4-as-judge (gpt-4-0613)  
**Fallback:** Exact match against TruthfulQA reference answers  
**Output:** Binary score {0, 1}  
**Justification:** Scales to n=817×3 prompts; widely accepted practice with cited ≥90% human agreement (assumption A1, unverified in our study)

### Robustness (Paraphrase Consistency)

**Method:** Sentence-BERT cosine similarity (all-MiniLM-L6-v2)  
**Process:** Generate embeddings for original and three paraphrased outputs; compute average cosine similarity  
**Output:** Continuous score [0, 1]  
**Justification:** Embedding-based measurement avoids semantic drift from back-translation; captures consistency independent of surface form

### Fairness (Demographic Bias)

**Method:** HONEST lexical bias with demographic augmentation  
**Process:** Generate outputs for 4 demographic variants per prompt; compute normalized bias variance across variants; fairness = 1 - normalized_variance  
**Output:** Continuous score [0, 1]  
**Justification:** Creates fairness signal on TruthfulQA (not inherently fairness-sensitive); validated to produce σ>0.2 variance (h-e1 result)

## Baselines

### Independence Baseline (r=0)

**Method:** Null hypothesis test via two-tailed p-value  
**Rationale:** Tests whether observed correlations differ significantly from zero (independence assumption)  
**Success criterion:** Reject H0 if p<0.05

### Permutation Test

**Method:** Shuffle dimension scores 1000 times; recompute correlations  
**Rationale:** Non-parametric validation that observed r exceeds 95th percentile of random pairings  
**Success criterion:** Observed r > 95th percentile of permuted distribution

## Experimental Protocol

### h-e1: Variance Validation

**Sample:** 817 TruthfulQA prompts on Llama-2-7b  
**Procedure:**
1. Generate outputs with synchronized parameters
2. Score reliability (GPT-4), robustness (SBERT), fairness (HONEST + demographic augmentation)
3. Compute σ for each dimension
4. Validate σ > 0.2 for all three dimensions

**Success criteria:**
- Primary: σ_reliability > 0.2, σ_robustness > 0.2, σ_fairness > 0.2
- Secondary: No floor/ceiling effects (mean ∈ [0.3, 0.7] for all dimensions)

**Gate:** MUST_WORK—failure indicates methodological flaw (e.g., fairness floor effect, reliability ceiling effect)

### h-m1: Memorization-Driven Coupling

**Sample:** 343 factual prompts (Science, Law, History, Geography) on Llama-2-7b  
**Procedure:**
1. Subset TruthfulQA to factual stratum
2. Compute Pearson r(reliability, robustness) with 95% CI via Fisher z-transform
3. Test against threshold r>0.3, p<0.05 (two-tailed)
4. Compare with misinformation stratum (n=474) for mechanism specificity

**Success criteria:**
- Primary: r > 0.3, p < 0.05
- Secondary: 95% CI lower bound > 0.2 (robustly positive)
- Tertiary: Contrast with misinformation stratum |Δr| > 0.1 (mechanism specificity)

**Gate:** MUST_WORK—failure contradicts memorization hypothesis

### h-m2: Alignment Tax Quantification

**Sample:** 817 TruthfulQA prompts on Llama-2-7b  
**Procedure:**
1. Compute Pearson r(fairness, reliability) on full dataset
2. Test against threshold r<-0.2, p<0.05 (two-tailed)
3. Verify 95% CI upper bound <-0.1

**Success criteria:**
- Primary: r < -0.2, p < 0.05
- Secondary: 95% CI upper bound < -0.1 (robustly negative)

**Gate:** SHOULD_WORK—failure indicates alignment tax absent or too weak to detect

### h-m3: Prompt-Type Moderation

**Sample:** 10 factual + 10 misinformation prompts (pilot) on Llama-2-7b  
**Procedure:**
1. Compute r_factual and r_misinfo separately
2. Fisher z-test for independent correlations
3. Test significance p<0.05, effect size |Δr|≥0.1

**Success criteria:**
- Primary: Fisher z-test p < 0.05
- Secondary: |r_factual - r_misinfo| ≥ 0.1
- Tertiary: Directional pattern (r_factual > 0.4, r_misinfo < 0.3)

**Gate:** SHOULD_WORK—pilot test to validate Fisher z-test pipeline before scaling to n≥100

**Note:** This was executed as underpowered pilot (n=10 per stratum). Power analysis recommended n≥85 per stratum for 80% power to detect r=0.3 at α=0.05. Full-scale execution deferred to future work.

## Statistical Analysis

All correlation tests use:
- **Pearson r** (assumes linear relationship, normality—validated via Q-Q plots)
- **Two-tailed p-values** (α=0.05, conservative for exploratory analysis)
- **95% confidence intervals** via Fisher z-transform (robustness check—CIs must exclude null region)
- **Effect size thresholds:** r>0.3 (positive coupling), r<-0.2 (negative coupling), chosen to exceed typical noise levels

**Power analysis:**
- h-m1 (n=343, r=0.3): >95% power
- h-m2 (n=817, r=0.2): >99% power
- h-m3 (n=10, r=0.3): ~15% power (underpowered pilot)

Next, we present results from these experiments, showing two validated coupling patterns and one inconclusive moderation test requiring larger sample size.
