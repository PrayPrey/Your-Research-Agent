# Experimental Setup

We design experiments to test whether RLHF instruction tuning causes geometric distortion of confidence signals. Our experimental design follows the hypothesis chain established in Section 3, with each experiment addressing a specific component of the discriminative degradation phenomenon.

## Research Questions

Our experiments address the following questions:

**RQ1 (Existence):** Does AUROC for margin-based correctness prediction decrease in instruction-tuned models compared to their base counterparts?

**RQ2 (Mechanism):** Is the mechanism underlying discriminative degradation margin inflation for incorrect predictions?

**RQ3 (Characterization):** Is the distortion geometric (persisting after percentile normalization) or scalar (eliminated by normalization)?

**RQ4 (Confirmation):** Does Brier score decomposition independently confirm geometric distortion through refinement degradation?

## Models

We evaluate instruction-tuned models and their base counterparts from two major model families:

**Qwen Family:**
- Base: `Qwen/Qwen2.5-7B`
- Instruct: `Qwen/Qwen2.5-7B-Instruct`

**Mistral Family:**
- Base: `mistralai/Mistral-7B-v0.1`
- Instruct: `mistralai/Mistral-7B-Instruct-v0.2`

**Rationale:** Paired base-instruct comparison within families isolates the effect of instruction tuning while controlling for architecture and pretraining data. Cross-family validation distinguishes RLHF effects from vendor-specific implementation details.

**Note on Llama:** We planned to include the Llama-2-7B family, but the models require HuggingFace authentication access that was not available during our experiments. The consistent effects across Qwen and Mistral suggest our findings are not vendor-specific.

## Dataset

**MMLU (Massive Multitask Language Understanding):**
- 14,042 test samples
- 57 subjects across STEM, humanities, social sciences, and other domains
- 4-way multiple choice format

**Rationale:** MMLU is a standard benchmark for LLM evaluation with established use in calibration research [Khanmohammadi et al., 2025; Luo et al., 2025]. The multiple-choice format enables clean margin extraction, and the large sample size (14,042) provides statistical power for detecting moderate effect sizes.

## Inference Protocol

All models use identical inference settings:

- **Decoding:** Greedy (temperature T=0) to eliminate sampling variance
- **Prompt format:** Zero-shot with standard MMLU formatting
- **Logit extraction:** First token logits for answer options (A, B, C, D)
- **Margin computation:** $\text{margin} = \text{logit}_{(1)} - \text{logit}_{(2)}$

## Evaluation Metrics

**Primary Metrics:**

1. **AUROC** (RQ1): Area under ROC curve for margin → correctness classification. Measures discriminative ability directly—higher AUROC indicates better ability to rank predictions by correctness probability.

2. **Margin Inflation Ratio** (RQ2): $\frac{E[\text{margin}|\text{incorrect}]_{\text{instruct}}}{E[\text{margin}|\text{incorrect}]_{\text{base}}}$. Measures mechanism—inflation ratio > 1 indicates margin inflation for incorrect predictions.

3. **β_percentile** (RQ3): Slope coefficient from $P(\text{correct}) = \sigma(\alpha + \beta \cdot z(\text{margin}))$ where $z(\cdot)$ is percentile z-score. Measures geometric distortion—if $\beta_{\text{instruct}} < \beta_{\text{base}}$ after percentile normalization, the distortion is geometric.

4. **Brier Refinement** (RQ4): Resolution component from Murphy decomposition. Measures discrimination independent of calibration—refinement degradation confirms geometric distortion.

**Statistical Inference:**

- Bootstrap confidence intervals (n=1,000) for AUROC and β_percentile
- Permutation tests (n=10,000) for conditional margin comparisons
- Effect sizes (Cohen's d) for practical significance
- All tests use α=0.05 significance level

## Implementation Details

**Hardware:** Single NVIDIA A100 GPU (40GB)

**Software:** PyTorch 2.0, Transformers 4.36, scikit-learn 1.3

**Reproducibility:** All experiments use fixed random seeds. Inference is deterministic (T=0).

**Compute:** Model loading and full MMLU inference takes approximately 30 minutes per model on A100.

## Experimental Procedures

**H-E1 (AUROC):** For each model, compute margin for all 14,042 MMLU questions. Calculate AUROC using margin as predictor and correctness as target. Bootstrap the AUROC difference (base - instruct) 1,000 times to obtain 95% CI.

**H-M1 (Margin Inflation):** Partition samples into correct/incorrect by model prediction. Compute conditional means E[margin|correct] and E[margin|incorrect] for each model. Permutation test (n=10,000) for significance of E[margin|incorrect] difference.

**H-M2 (β_percentile):** Transform margins to percentile ranks within each model. Fit logistic regression to obtain β. Paired bootstrap (n=1,000) for Δβ = β_base - β_instruct.

**H-M3 (Brier Refinement):** Convert margins to calibrated probabilities. Apply 15-bin Murphy decomposition. Compare refinement components between base and instruct models.
