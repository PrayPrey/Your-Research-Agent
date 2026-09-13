# Methodology

## Overview

The key insight driving our design is that adversarial vulnerability, viewed as a scalar, discards the multivariate structure that carries architecture-family signal. Different attack types stress different model components: lexical substitution attacks (AdvGLUE adv_qqp, adv_qnli) stress lexical matching; paraphrase and NLI attacks (adv_rte, ANLI-R3) stress semantic inference under structural transformation. Whether a model is more vulnerable to lexical or semantic attacks is directly related to how its attention mechanism processes perturbations. We therefore represent each model as a Δ*-vector — one normalized vulnerability score per attack category — and test whether architecture family explains a significant portion of variance in this multivariate space.

## The Δ*-Vector Framework

### Normalized Vulnerability (Δ*)

For a model m evaluated on attack category c, the normalized adversarial vulnerability is:

> Δ*(m, c) = (Acc_clean(m, c) − Acc_adv(m, c)) / Acc_clean(m, c)

where Acc_clean is accuracy on the clean validation split and Acc_adv is accuracy on the adversarially perturbed examples. The normalization by Acc_clean removes the clean-accuracy confound: a model with low clean accuracy on a task appears vulnerable under raw accuracy-drop, but Δ* measures the *proportional* degradation from its own baseline.

**Rationale:** Without normalization, a model performing at 60% clean accuracy on a difficult NLI task would appear more vulnerable than a model at 90% clean accuracy after the same absolute accuracy drop. Δ* isolates the adversarial vulnerability effect from task difficulty and model capacity effects.

For each model, we collect the per-attack-category Δ* scores into a vector **x**(m) ∈ ℝ^K, where K is the number of reliable attack categories (K=6 in our experiments after reliability filtering). The resulting data matrix X ∈ ℝ^(N×K) (N=9 models, K=6 categories) is the input to the statistical analysis.

### Reliability Filtering

Not all attack categories yield stable Δ* estimates with finite model pools. We apply a split-half reliability filter: for each attack category c, we split the adversarial examples into two halves, compute Δ* on each half, and compute the Spearman-Brown corrected correlation r_SB. Categories with r_SB < 0.7 or fewer than 50 examples are excluded from X. This filter ensures the multivariate analysis is not driven by noise in low-count attack categories.

**Rationale:** Including unreliable categories would inflate within-group variance, reducing effect size estimates and producing misleadingly conservative significance tests. The filter makes the effect-size measurement conservative: we exclude noisy categories before testing, so η² is estimated from the cleanest available signal.

## Model Selection and Scale Matching

We evaluate nine transformer models spanning three architecture families:

| Family | Models |
|--------|--------|
| Encoder-only | bert-base-uncased, roberta-base, google/electra-base-discriminator, albert-base-v2 |
| Decoder-only | gpt2, facebook/opt-125m, facebook/opt-350m |
| Encoder-decoder | t5-base, facebook/bart-base |

**Scale matching criterion:** All models are in the 110–350M parameter range. This controls for the capacity effect: at sufficiently large scale, decoder-only models may exhibit qualitatively different robustness dynamics than at base scale.

**Rationale:** Scale matching is essential for attributing Δ*-vector variance to architecture family rather than to model capacity. We do not include models at 1B+ parameters in this PoC, as the family-level effect at large scale is an open empirical question.

## Fine-Tuning Protocol

All models are fine-tuned on GLUE tasks (SST-2, MNLI, QQP, QNLI, RTE) using the HuggingFace Trainer with family-specific learning rates:

| Family | Learning Rate | Batch Size | Epochs |
|--------|--------------|------------|--------|
| Encoder-only | 2×10⁻⁵ | 32 | 3 |
| Decoder-only | 5×10⁻⁵ | 16 | 3 (SST-2/QQP), 5 (MNLI) |
| Encoder-decoder | 1×10⁻⁴ | 32 | 3 (SST-2), 5 (MNLI/QQP) |

Encoder-only models use 2e-5 following standard BERT fine-tuning practice. Decoder-only models require a higher learning rate due to the causal attention mechanism's different gradient landscape. Encoder-decoder models use the highest rate with extended epochs on multi-class tasks (MNLI) to ensure convergence. Seed=42 throughout; we acknowledge this single-seed PoC does not quantify variance over initialization.

**Note on enc_dec fine-tuning:** T5-base and BART-base were fine-tuned only on SST-2 in our reported experiment, not on MNLI. This produced degenerate ANLI-R3 results (Δ*≈0 due to near-chance clean NLI accuracy). The corrected enc_dec fine-tuning protocol (adding MNLI) is included in the h-e1-v2 design; we report the limitation explicitly in Section 6.

## Statistical Methods

### Permutation MANOVA

To test whether architecture family membership explains Δ*-vector variance, we apply permutation MANOVA to the data matrix X with architecture-family labels y ∈ {encoder, decoder, enc_dec}. The test statistic is Pillai's trace; we separately compute η² = SS_between / SS_total as the effect-size measure. In the balanced three-group case, Pillai's trace and η² are numerically close (both bounded [0,1] and monotonically related), but they are not identical — we report η² throughout for interpretability, with Pillai's trace as the basis for the permutation p-value.

**Rationale:** Parametric MANOVA assumes multivariate normality and sufficient sample size; with N=9, neither assumption is reliable. Permutation MANOVA makes no distributional assumption: we permute family labels 1,000 times, recomputing η² each time, and report the empirical p-value (fraction of permuted η² exceeding observed η²). This gives a valid p-value regardless of data distribution.

We additionally compute per-category η² using univariate ANOVA on each Δ*(·, c) separately. This identifies which attack categories carry the strongest architecture-family signal and provides a richer decomposition of the global effect.

### LOMO Classification

As a complementary test of whether Δ*-vectors can support architecture-family identification, we apply leave-one-model-out (LOMO) nearest-neighbor classification: for each model m, we classify it into the family whose remaining models' Δ*-vectors are closest (cosine distance, k=1). We report accuracy (fraction of correctly classified models) and the 3×3 confusion matrix.

**Rationale:** LOMO directly operationalizes the puzzle question — can you identify a model's family from its Δ*-vector? — without held-out test data. The cosine distance metric is scale-invariant, appropriate for vulnerability profiles where absolute magnitudes differ across tasks.

**Limitation on validity:** With N=3 models per family, each LOMO fold trains on only 2 examples per family in a 6-dimensional space. This renders cosine k=1 geometrically near-degenerate: chance-level accuracy (0.333) is mathematically expected from the configuration. We report LOMO results as exploratory, not as a valid hypothesis test, and caution against interpreting LOMO accuracy at N<5 models per family as evidence about family separability.

### Mixed-Effects Controls

As a robustness check, we additionally fit a mixed-effects regression:

> Δ*(m, c) ~ arch_family × attack_type + objective + tokenizer + clean_acc + (1|model_id)

This model includes architecture family (the target variable), pretraining objective (MLM vs. CLM vs. T5-denoising), tokenizer type, and clean accuracy as covariates, with model as a random intercept to account for repeated measures across attack categories. The permutation MANOVA result is the primary test; the mixed-effects model provides sensitivity checks on confound control.

## Implementation

The full pipeline is implemented in seven Python modules:

| Module | Responsibility |
|--------|---------------|
| `data_loader.py` | AdvGLUE, ANLI-R3, clean GLUE loading |
| `fine_tuner.py` | HuggingFace Trainer-based fine-tuning; family-specific MODEL_CONFIGS |
| `evaluator.py` | Clean + adversarial accuracy evaluation with checkpoint resumption |
| `delta_star.py` | Δ* computation, split-half reliability filter, vector builder |
| `statistical_analysis.py` | Permutation MANOVA, bootstrap CI, LOMO, mixed-effects |
| `visualizer.py` | Heatmap, family profiles, LOMO confusion matrix, per-category η² |
| `run_experiment.py` | End-to-end orchestration |

The pipeline is designed for checkpoint resumption: evaluation results are persisted as JSON after each stage, enabling Stage 3 crash recovery. All code is released under the repository accompanying this paper.
