# Methodology

The geometric framing introduced in the introduction implies a specific operationalization: if alignment-induced argmax instability reflects the distance of each item from a decision boundary, then pre-alignment confidence margin should predict post-alignment flip probability. This section describes how we test that implication rigorously. We define the prediction task formally, specify the data and models used, describe the margin-based predictor and its design rationale, and present the two mechanistic analyses — non-isotropy and quintile stratification — that probe the geometric structure underlying the predictor's performance.

## Problem Formulation

Let M_base denote a pre-trained, unaligned language model and M_aligned its aligned counterpart produced by a single alignment procedure (DPO or SFT). For a multiple-choice question item i with answer options {A, B, C, D}, let **v**_base(i) ∈ ℝ⁴ and **v**_aligned(i) ∈ ℝ⁴ denote the logit vectors assigned to the four answer tokens by M_base and M_aligned, respectively.

We define the **argmax flip indicator** as:

  flip_i = 𝟙[argmax(**v**_base(i)) ≠ argmax(**v**_aligned(i))]

This is a binary outcome: 1 if the top-predicted answer changes after alignment, 0 otherwise. The prediction task is: given only **v**_base(i) (and hence M_base alone), predict flip_i before M_aligned is applied.

We define the **pre-alignment confidence margin** for item i as:

  margin_i = (v_base^(1)(i) − v_base^(2)(i)) / σ

where v_base^(1)(i) and v_base^(2)(i) are the top-1 and top-2 logits from **v**_base(i) sorted in decreasing order, and σ is the standard deviation of all raw margins within the model pair (i.e., z-scoring over the full evaluation set). The margin captures the gap between the most-likely and second-most-likely predicted answer in the base model's output distribution.

The z-scoring step is critical: it removes scale differences between model pairs (which may have different logit magnitudes due to architectural differences) and centers the predictor so that regression coefficients are interpretable as effects per standard-deviation change in margin. Without z-scoring, the coefficient β₁ would conflate true predictive signal with arbitrary scale artifacts introduced by model-specific softmax temperature.

## Dataset and Model Setup

We evaluate on three multiple-choice benchmarks. **MMLU** (cais/mmlu, test split) provides 14,042 items spanning 57 subject areas, making it the primary training dataset for our predictor. **TruthfulQA** (817 items) and **ARC-Challenge** (1,172 items) serve as held-out evaluation benchmarks: the predictor is trained on MMLU and evaluated on TruthfulQA and ARC-Challenge without any retraining or threshold adjustment. This cross-benchmark evaluation protocol tests generalization in a strict sense — not just held-out items from the same distribution, but held-out distributions entirely.

We study two model pairs:

- **Pair 2 (primary):** allenai/tulu-2-7b (base) → allenai/tulu-2-dpo-7b (DPO-aligned). This 7B parameter pair provides our main evidence for the existence hypothesis and the non-isotropy and quintile analyses.
- **Pair 4 (secondary):** EleutherAI/pythia-6.9b (base) → dvruette/oasst-pythia-6.9b-4000-steps (SFT-aligned). This pair allows us to examine whether the margin predictor generalizes across alignment algorithms (DPO vs. SFT) and model families.

Two additional model pairs (pair 1 and pair 3) were initially planned but excluded: pair 1 and pair 3 models returned HTTP 404 errors from the HuggingFace Hub or produced tokenizer errors that prevented consistent 4-token logit extraction. We report results for pairs 2 and 4 only and note that our primary evidence is concentrated in pair 2, a limitation we discuss in the results.

PPO-aligned model pairs were not available on HuggingFace at the time of our experiments, precluding direct DPO vs. PPO comparison. This constrains our algorithmic comparison to DPO vs. SFT.

The MCQ-specific scope of our analysis is intentional rather than incidental: for MCQ items, the 4D logit vector over answer options is a well-defined and consistently extractable object across all models, enabling the geometric analyses in Sections 3.4 and 3.5. Extending the margin predictor to open-ended generation would require a different operationalization of both margin and flip, which we leave for future work.

## Margin-Based Predictor

To quantify the relationship between pre-alignment margin and post-alignment flip probability, we fit a **mixed-effects logistic regression** of the form:

  logit(P(flip_i = 1)) = β₀ + β₁ · margin_i + u_{d(i)}

where u_{d(i)} is a random intercept for the dataset d(i) ∈ {MMLU, TruthfulQA, ARC-Challenge} to which item i belongs. The mixed-effects structure is important for two reasons. First, the three benchmarks differ substantially in base flip rates and item difficulty distributions; a fixed-effects model would attribute between-benchmark differences to the margin coefficient, inflating or deflating β₁ depending on the correlation between margin distribution and benchmark identity. The random intercepts absorb these baseline differences, allowing β₁ to reflect the within-benchmark relationship between margin and flip probability. Second, items within a benchmark are not fully independent (they share a generation process and domain structure), and the random effects provide a partial correction for this clustering.

We estimate the model using maximum likelihood and assess significance via the Wald statistic for β₁. Effect size is reported as η² (eta-squared), computed as the proportion of variance in flip_i explained by margin_i in the logistic regression sense. Predictive performance is evaluated by AUROC, computed separately for each benchmark using the predicted flip probability from the logistic model as the ranking score. The AUROC provides a threshold-free summary of discriminative performance that is robust to class imbalance — relevant here because flip_rate = 12.5% overall, meaning the classes are substantially imbalanced.

## Non-Isotropy Analysis

The margin predictor's success would be mechanistically uninformative if alignment perturbations were isotropic — i.e., if they acted equally in all directions of the 4D logit space. In that case, items near the argmax boundary would be vulnerable to flipping simply by chance, and the margin would predict flips only because random perturbations are more likely to cross a nearby boundary. However, if alignment perturbations are directionally concentrated, then items near the boundary in the principal perturbation direction are specifically vulnerable, and the predictive power of margin has a deeper geometric explanation.

To distinguish these cases, we define the **logit delta** for each item:

  Δ_i = **v**_aligned(i) − **v**_base(i) ∈ ℝ⁴

and compute the sample covariance matrix Σ = Cov({Δ_i}) across all items in a benchmark. We then perform eigendecomposition of Σ to obtain eigenvalues λ₁ ≥ λ₂ ≥ λ₃ ≥ λ₄ and define the **anisotropy ratio** as:

  ρ = λ₁ / mean(λ₂, λ₃, λ₄)

Under isotropic Gaussian perturbations (our null model), all eigenvalues are equal in expectation and ρ ≈ 1.0. We confirm this empirically using a synthetic isotropic Gaussian control, which yields ρ = 1.13. Ratios substantially above this baseline indicate that alignment perturbations are concentrated along a principal direction rather than spread uniformly.

Statistical significance of the observed anisotropy ratios is assessed by a permutation test: we randomly shuffle the item-to-perturbation assignments, recompute ρ, and repeat 1,000 times to construct a null distribution. The p-value is the proportion of permuted ratios exceeding the observed ratio.

## DPO vs. SFT Quintile Analysis

The non-isotropy analysis characterizes the global structure of alignment perturbations. The quintile analysis asks a finer question: does the *magnitude* of alignment perturbation vary systematically with the base model's confidence level, and does this relationship differ between DPO and SFT alignment?

We stratify evaluation items into five equal-sized quintiles (Q1–Q5) based on their pre-alignment margin, with Q1 containing the lowest-margin (least confident) items and Q5 the highest-margin (most confident) items. For each quintile, we compute the variance of the logit delta magnitudes, var(||Δ_i||) within the quintile. This captures whether alignment applies larger or smaller perturbations to items at different confidence levels.

To ensure that observed quintile differences reflect confidence-dependent effects rather than pre-existing distributional differences between benchmarks, we residualize the logit deltas by regressing out dataset indicators before computing quintile variances. This is analogous to the random-effect structure in the logistic regression: it ensures that the quintile trend is estimated within-benchmark rather than confounded by between-benchmark variation.

The rationale for comparing DPO and SFT in this analysis is that the two alignment algorithms have different optimization objectives: DPO directly optimizes a contrastive log-ratio objective over preference pairs, while SFT optimizes next-token prediction on curated demonstrations. If confidence-dependent amplification is a general property of alignment, both algorithms should exhibit similar quintile trends. If it is specific to DPO's optimization dynamics — as our results suggest — the quintile trend becomes a behavioral signature that discriminates DPO from SFT and warrants further mechanistic investigation.

**Scope note:** Because PPO-aligned models were unavailable, we cannot include a PPO condition in the quintile or non-isotropy analyses. The DPO-vs-SFT comparison thus stands as the extent of our algorithmic comparison, and conclusions about DPO-specific behavior should be interpreted relative to SFT rather than to RLHF algorithms in general. Additionally, all analyses are restricted to multiple-choice evaluation items, where the 4D logit vector is well-defined; generalization to other task formats is an open question.
