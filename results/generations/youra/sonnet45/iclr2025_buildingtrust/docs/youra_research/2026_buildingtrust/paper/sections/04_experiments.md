# 4. Experiments

The experiments in this paper are designed to test whether the pre-alignment confidence margin — the z-scored difference between the top-1 and top-2 log-probabilities of a base language model — serves as a geometric predictor of post-alignment argmax instability. The Introduction claimed three properties: (1) the margin predicts argmax flip with AUROC in the range 0.867–0.909 across benchmarks after DPO alignment, (2) alignment-induced logit perturbations are non-isotropic, with eigenvalue ratios of 2.9–4.6× relative to an isotropic control near 1.13, and (3) DPO and SFT produce qualitatively different perturbation profiles across confidence quintiles. The experiments below are structured around three research questions that correspond directly to these three claims.

## Research Questions

**RQ1.** Does pre-alignment confidence margin predict post-alignment argmax instability with above-threshold discriminative power, and does this predictive relationship generalize across benchmark domains?

**RQ2.** Are alignment-induced logit perturbations geometrically structured — specifically, non-isotropic — rather than approximating random noise added uniformly across the vocabulary?

**RQ3.** Do DPO and SFT produce distinguishably different perturbation variance profiles when items are stratified by pre-alignment confidence quintile?

## Datasets

We evaluate on three benchmark datasets that together span factual recall, reasoning, and commonsense understanding:

**MMLU** (Massive Multitask Language Understanding; Hendrycks et al., 2021). We use the full test split across all 57 subjects. After tokenization and filtering for valid 4-choice items, the primary model pair (pair2) yields N=14,042 items. MMLU is chosen as the primary benchmark because its breadth of subject domains provides within-dataset cross-domain generalization evidence for RQ1.

**TruthfulQA** (Lin et al., 2022). We use the multiple-choice variant. TruthfulQA is selected because its items are specifically designed to elicit overconfident incorrect responses in large language models, making it a stringent test for whether low-margin items are disproportionately vulnerable.

**ARC-Challenge** (Clark et al., 2018). We use the Challenge split, which contains science questions that require multi-step reasoning rather than direct recall. ARC-Challenge provides a third domain with distinct distributional properties from both MMLU and TruthfulQA.

All three benchmarks are framed as 4-choice MCQ tasks. Only items for which both the base model and aligned model produce valid logits over all four answer tokens are retained. Margin is computed as the z-scored difference between the log-probabilities of the top-ranked and second-ranked answer choices under the base model, computed per-benchmark to remove benchmark-level scale differences.

## Model Setup

We evaluate two model pairs corresponding to two alignment methods:

**Pair 2 (DPO alignment — primary pair).** Base model: `allenai/tulu-2-7b`. Aligned model: `allenai/tulu-2-dpo-7b`. This pair shares identical pretraining data and architecture, differing only in the application of Direct Preference Optimization. The tulu-2 family is chosen because both checkpoints are publicly released, the training procedure is documented, and the 7B scale is large enough to produce well-calibrated base model confidence distributions. Pair 2 is the primary source of evidence for all three research questions.

**Pair 4 (SFT alignment — secondary pair).** Base model: `EleutherAI/pythia-6.9b`. Aligned model: `dvruette/oasst-pythia-6.9b-4000-steps`. This pair provides the SFT comparison necessary for RQ3 and allows us to assess whether the margin-flip relationship is specific to DPO or present under supervised fine-tuning as well.

Two additional pairs (pair1: a Llama-based DPO model, pair3: a second SFT model) were excluded from analysis due to HuggingFace repository unavailability (404 errors) and tokenizer incompatibility, respectively, at the time of data collection. The PPO-aligned model family originally targeted as a third method of comparison was also unavailable, limiting the alignment-method comparison to DPO versus SFT. We discuss this limitation in Section 6.

## Implementation Details

**Logit extraction.** For each item, we extract the log-probabilities assigned to each of the four answer tokens (A, B, C, D) by both base and aligned models. The logit delta for item i is defined as the 4-dimensional vector δᵢ = logit_aligned,i − logit_base,i.

**Margin computation.** Confidence margin is defined as z-score( log P(top-1) − log P(top-2) ) under the base model, where z-scoring is performed within each benchmark split.

**Flip detection.** An argmax flip is recorded when argmax(logit_base,i) ≠ argmax(logit_aligned,i).

**Mixed-effects regression (RQ1).** We fit a mixed-effects logistic regression of the form logit(P(flip_i)) = β₀ + β₁·margin_i + u_{dataset_i}, where u_{dataset} is a random intercept per benchmark domain. This accounts for the differential baseline flip rates across subject areas within MMLU and across the three benchmarks when pooling. Significance threshold is set at α = 0.005 (more conservative than conventional 0.05 to guard against false positives given large N).

**Quintile stratification.** Items are sorted by base model margin within each benchmark and assigned to quintiles Q1 (lowest margin) through Q5 (highest margin), each containing approximately equal numbers of items. Quintile-level flip rates and logit delta variances are computed per quintile.

**Anisotropy analysis (RQ2).** We compute the covariance matrix Σ of the 4-dimensional logit delta vectors across all items. We decompose Σ via eigendecomposition and compute the anisotropy ratio as λ₁ / mean(λ₂, λ₃, λ₄). An isotropic Gaussian control is generated by sampling 14,042 random 4-dimensional vectors from N(0, I) and computing the same ratio, yielding a reference value near 1.13. A one-tailed t-test against the null of ratio = 1.0 is used (p-value reported as one-tailed, i.e., p/2 of the two-tailed test).

**Bootstrap confidence intervals.** AUROC confidence intervals use n_bootstrap = 5,000 stratified bootstrap replicates.

**Hardware.** All logit extraction experiments are run on a single NVIDIA GPU (CUDA_VISIBLE_DEVICES set to the lowest-utilization device at job submission time). Regression and eigendecomposition are run on CPU.

## Evaluation Metrics

For **RQ1**, primary metrics are: regression coefficient β₁ (sign and magnitude), p-value (threshold α=0.005), AUROC per benchmark (threshold 0.75), and partial eta-squared η² (threshold 0.06). The gate requires β₁ < 0, p < 0.005, AUROC ≥ 0.75 on at least two benchmarks, and η² ≥ 0.06.

For **RQ2**, the primary metric is the anisotropy ratio λ₁/mean(λ₂,λ₃,λ₄), compared against the isotropic control value of 1.13. The gate requires ratio > 1.0 at p < 0.05 (one-tailed) for both evaluated pairs.

For **RQ3**, the primary metrics are per-quintile logit delta variances for DPO and SFT separately, and the Q5/Q1 variance ratio within each method. We also report Cohen's d and p-value for the one-tailed Welch's t-test comparing DPO Q1 mean delta variance against SFT Q1 mean delta variance.
