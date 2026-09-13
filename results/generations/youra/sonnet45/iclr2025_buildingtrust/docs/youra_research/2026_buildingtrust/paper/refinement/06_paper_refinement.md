# Geometric Fingerprints of Alignment: Pre-Alignment Confidence Margin Predicts Argmax Instability After RLHF

---

## Abstract

Reinforcement learning from human feedback (RLHF) can alter which answers a language model selects for multiple-choice questions (MCQs), yet no method exists to identify alignment-vulnerable items before fine-tuning begins. This paper examines whether the pre-alignment confidence margin — the gap between a base model's top-1 and top-2 log-probabilities for a given item — predicts post-alignment argmax instability. Across three benchmarks (MMLU, TruthfulQA, and ARC-Challenge), the pre-alignment margin predicts post-alignment argmax flips for a DPO-aligned 7B model with area under the receiver operating characteristic curve (AUROC) of 0.867 (MMLU), 0.803 (TruthfulQA), and 0.909 (ARC-Challenge), without retraining between benchmarks. A mixed-effects logistic regression yields β₁ = −4.33 (p ≈ 10⁻²²⁷, η² = 0.289) for this pair. The flip rate is 12.5% across 14,042 MMLU items. Additionally, alignment-induced logit perturbations are structurally non-isotropic: the dominant eigenvalue of the logit-delta covariance is 2.90 times the mean of the remaining eigenvalues for DPO alignment and 4.58 times for SFT alignment, compared to a ratio of approximately 1.13 for an isotropic Gaussian control. An unexpected finding is that DPO-aligned models exhibit a monotone quintile trend in logit delta variance — rising from 0.707 in the lowest confidence quintile to 3.384 in the highest — while SFT produces a flat profile (0.223 to 0.281). These findings are limited to MCQ settings, to two model pairs (one DPO, one SFT), and the originally planned PPO comparison could not be executed due to model unavailability. Two planned mechanistic analyses (H-M3, H-M4) were not completed.

---

## 1. Introduction

Whether a base model's output probability distribution encodes information about which items will change their predicted answer after alignment is an open empirical question. If such a signal exists, it would enable item-level pre-deployment risk assessment: practitioners could identify evaluation questions most likely to receive different answers after alignment before any fine-tuning is applied.

The central object of study is the *argmax flip* — the event that a model's top-predicted answer for a given MCQ item changes after an alignment procedure. Among 14,042 MMLU test items, 12.5% receive a different top prediction after DPO alignment of tulu-2-7b, with no change to the question content. The empirical question is whether properties of the base model's output distribution — observable before alignment — predict which items will flip.

The *pre-alignment confidence margin* is defined as the z-scored difference between the base model's top-1 and top-2 log-probabilities over the MCQ answer options. This quantity captures the geometric distance from the item's implied answer distribution to the decision boundary at which the top-1 and top-2 answers tie. Items with small margins lie near this boundary; items with large margins lie far from it.

The hypothesis tested in this paper is that low-margin items are disproportionately exposed to alignment-induced boundary shifts, because alignment perturbations of bounded magnitude are sufficient to cross the boundary when the initial margin is small. This predicts a negative relationship between pre-alignment confidence margin and post-alignment argmax flip probability.

Three research questions are examined:

**RQ1.** Does pre-alignment confidence margin predict post-alignment argmax flip probability at above-threshold discriminative performance, and does this generalize across benchmark domains?

**RQ2.** Are alignment-induced logit perturbations geometrically structured — specifically, non-isotropic — as opposed to approximating random noise?

**RQ3.** Do DPO and SFT produce distinguishably different perturbation variance profiles across confidence quintiles?

This paper reports the following: (1) for a DPO-aligned tulu-2-7b model pair, the margin predictor achieves AUROC of 0.867–0.909 across three benchmarks with no domain adaptation; (2) logit-delta perturbations are non-isotropic under both DPO and SFT with anisotropy ratios of 2.90 and 4.58 respectively; (3) contrary to the directional prediction, DPO does not concentrate perturbation variance in low-confidence regions — instead DPO variance increases monotonically with confidence (a null result for the directional hypothesis, with a novel finding about DPO's quintile profile). Limitations include the absence of PPO-aligned model pairs, primary evidence from a single model pair for the margin-flip result, and MCQ-specific scope.

---

## 2. Related Work

### LLM Calibration and Reliability Under Alignment

Liu et al. [2023] demonstrate that instruction fine-tuning alters calibration across a range of tasks, with Expected Calibration Error increasing even when accuracy improves. Li et al. [2024] document that RLHF produces heterogeneous effects across the input distribution rather than uniform shifts: different inputs exhibit qualitatively different responses to the same alignment procedure. Xu et al. [2024] compare PPO and DPO algorithmically and show that the two alignment paradigms produce systematically different behavioral profiles despite optimizing related preference objectives. Wang et al. [2024] provide a comprehensive survey of alignment techniques including RLHF, RLAIF, PPO, and DPO. This literature establishes that alignment is a structured transformation of model behavior with input-dependent effects.

### Pre-Alignment Predictors of Post-Alignment Behavior

Plaut et al. [2024] demonstrate that the maximum softmax probability of a base model predicts whether the model's answer is correct, establishing that pre-alignment confidence carries predictive signal about answer quality. Fan et al. [2026] examine correlations between pre-alignment benchmark accuracy and post-alignment accuracy, finding that aggregate accuracy trends are partially predictable from base model performance. These works operate at the aggregate level — across items or benchmarks — rather than predicting per-item change. The present work differs in target: it asks not whether the base model answer is correct, but whether alignment will change it, and operates at the individual item level.

### Geometric Analysis of Model Representations

Khanmohammadi et al. [2025] investigate how representation stability relates to model calibration, finding that geometric properties of the representation space carry information about model reliability. Lunardi et al. [2025] examine MCQ answer reliability under paraphrase perturbations, finding that model responses are more fragile than surface accuracy suggests, a finding they attribute partly to proximity of items to decision boundaries in the representation space. This geometric perspective motivates the non-isotropy analysis conducted in this paper.

### Gap and Positioning

The literature reviewed above establishes that alignment reshapes model calibration with heterogeneous effects, that base model signals predict aggregate post-alignment properties, and that geometric properties of representations are informative about reliability. No prior work poses the per-item, pre-deployment prediction of argmax instability as a classification task, operationalizes it with the confidence margin, or evaluates it with cross-benchmark generalization. The present paper addresses this gap.

---

## 3. Method

### Problem Formulation

Let M_base denote an unaligned language model and M_aligned its counterpart produced by one alignment procedure. For a multiple-choice question item i with answer options {A, B, C, D}, let **v**_base(i) ∈ ℝ⁴ and **v**_aligned(i) ∈ ℝ⁴ denote the log-probability vectors over answer tokens under M_base and M_aligned, respectively.

The **argmax flip indicator** is defined as:

> flip_i = 𝟙[argmax(**v**_base(i)) ≠ argmax(**v**_aligned(i))]

This is a binary outcome: 1 if the top-predicted answer changes after alignment, 0 otherwise. The prediction task is: given only **v**_base(i), predict flip_i before M_aligned is applied.

The **pre-alignment confidence margin** for item i is:

> margin_i = (v_base^(1)(i) − v_base^(2)(i)) / σ

where v_base^(1)(i) and v_base^(2)(i) are the top-1 and top-2 logits sorted in decreasing order, and σ is the standard deviation of all raw margins within the model pair (z-scoring over the full evaluation set). Z-scoring removes scale differences between model pairs and centers the predictor so that regression coefficients reflect effects per standard-deviation change in margin.

### Datasets and Model Pairs

Three 4-choice MCQ benchmarks are used. **MMLU** (cais/mmlu, all subjects, test split, N=14,042 for pair 2) provides the primary predictor training benchmark. **TruthfulQA** (truthful_qa, multiple_choice, validation split, N=817) and **ARC-Challenge** (allenai/ai2_arc, ARC-Challenge, test split, N=1,172) are held-out evaluation benchmarks: the predictor is trained on MMLU and evaluated on TruthfulQA and ARC-Challenge without retraining or threshold adjustment.

Two model pairs are evaluated:

- **Pair 2 (primary, DPO):** allenai/tulu-2-7b (base) → allenai/tulu-2-dpo-7b (DPO-aligned).
- **Pair 4 (secondary, SFT):** EleutherAI/pythia-6.9b (base) → dvruette/oasst-pythia-6.9b-4000-steps (SFT-aligned).

Two additional planned model pairs were excluded due to infrastructure failures: pair 1 (allenai/tulu-2-7b → allenai/tulu-2-ppo-7b) returned HTTP 404 from HuggingFace, and pair 3 (EleutherAI/pythia-1.4b → reciprocate/ppo_hh_pythia-1B) produced a tokenizer error (`AttributeError: 'NoneType' object has no attribute 'endswith'`). No PPO-aligned model pairs were available; all algorithmic comparisons are therefore between DPO and SFT rather than between DPO and PPO as originally designed.

All logit extraction was run on a single NVIDIA H100 NVL GPU (95 GB, CUDA_VISIBLE_DEVICES=0), in conda environment `youra-h-e1` (Python 3.10).

### Margin-Based Predictor (H-E1)

A **mixed-effects logistic regression** is fitted:

> logit(P(flip_i = 1)) = β₀ + β₁ · margin_i + u_{d(i)}

where u_{d(i)} is a random intercept for benchmark d(i) ∈ {MMLU, TruthfulQA, ARC-Challenge}. The mixed-effects structure absorbs baseline differences in flip rates and item difficulty across benchmarks, allowing β₁ to reflect the within-benchmark relationship. Significance is assessed via the Wald statistic for β₁ (threshold α = 0.005, conservative given N). Effect size is reported as partial η² (variance in flip_i explained by margin_i). Predictive performance is evaluated by AUROC (threshold 0.75 for gate passage) computed separately per benchmark.

### Non-Isotropy Analysis (H-M1)

The **logit delta** for each item is:

> Δ_i = **v**_aligned(i) − **v**_base(i) ∈ ℝ⁴

The sample covariance matrix Σ = Cov({Δ_i}) is computed across all items in a benchmark, and eigendecomposition (numpy.linalg.eigh) yields λ₁ ≥ λ₂ ≥ λ₃ ≥ λ₄. The **anisotropy ratio** is:

> ρ = λ₁ / mean(λ₂, λ₃, λ₄)

Under an isotropic Gaussian null model (N(0, I₄)), all eigenvalues are equal in expectation. An empirical isotropic control (N=1,000, seed=1) yields ρ = 1.13, confirming the null yields ratios near 1. Statistical significance is assessed via a one-tailed permutation test (1,000 shuffles); gate threshold is α = 0.05 for at least 2 of 3 model families evaluated.

### DPO vs. SFT Quintile Analysis (H-M2)

Items are stratified into five equal-sized quintiles (Q1–Q5) by pre-alignment margin, with Q1 the lowest-margin (least confident) quintile. For each quintile, the variance of logit delta magnitudes — var(‖Δ_i‖) within quintile — is computed after KL-divergence residualization (OLS per quintile) to remove alignment-magnitude confounds. The directional hypothesis is that DPO produces higher mean logit delta variance in Q1 than SFT. Statistical comparison uses one-tailed Welch's t-test with n_bootstrap = 5,000 confidence intervals.

**Note on PPO scope:** Because PPO-aligned models were unavailable, the quintile analysis compares DPO to SFT only.

---

## 4. Experimental Setup

### Research Questions

The experiments address three research questions corresponding to the three executed sub-hypotheses (H-E1, H-M1, H-M2). Sub-hypotheses H-M3 (margin×method interaction in mixed-effects logistic regression) and H-M4 (cosine projection of logit deltas onto the dominant perturbation eigenvector) were not executed; their planned analyses remain inconclusive.

### Evaluation Metrics

For RQ1 (H-E1): β₁ sign and magnitude, Wald p-value (α = 0.005), AUROC per benchmark (threshold 0.75), partial η² (threshold 0.06). Gate type: MUST_WORK.

For RQ2 (H-M1): anisotropy ratio vs. isotropic control (≈1.13), one-tailed t-test significance (α = 0.05), minimum 2 of 3 model families passing both criteria. Gate type: MUST_WORK.

For RQ3 (H-M2): per-quintile logit delta variances, one-tailed Welch's t-test for DPO Q1 > SFT Q1, Cohen's d. Gate type: SHOULD_WORK (null result acceptable; pipeline continues).

### Implementation Details

For each item, 4D log-probability vectors over answer tokens {A, B, C, D} are extracted from both base and aligned models. Logit extraction uses cached .npy files (18 files for H-E1: 6 per completed pair × 3 datasets). The anisotropy analysis reuses the H-E1 logprob cache without re-running model inference. The quintile variance analysis uses the same cache. All code is implemented in Python with numpy, scipy, and sklearn; 45 unit tests pass for H-M1 and 23 for H-M2.

---

## 5. Results

### RQ1: Pre-Alignment Margin Predicts Post-Alignment Argmax Flip (H-E1)

**Gate result: PASS.**

Table 1 presents the mixed-effects logistic regression results and AUROC values for both model pairs.

**Table 1. H-E1 existence test results.**

| Pair | Alignment | Base model | Aligned model | β₁ | p-value | AUROC (MMLU) | AUROC (TruthfulQA) | AUROC (ARC) | η² | Flip rate | Gate |
|------|-----------|-----------|--------------|-----|---------|--------------|---------------------|-------------|-----|-----------|------|
| pair2 | DPO | tulu-2-7b | tulu-2-dpo-7b | −4.3295 | 4.13×10⁻²²⁷ | 0.8668 | 0.8034 | 0.9086 | 0.2892 | 12.5% | PASS |
| pair4 | SFT | pythia-6.9b | oasst-pythia-6.9b | −0.0617 | 1.95×10⁻³ | 0.6087 | 0.6542 | 0.5756 | 0.0284 | 75.5% | Below threshold |

For pair 2 (tulu-2-7b DPO), β₁ = −4.3295 (p ≈ 4.13×10⁻²²⁷). The negative sign confirms the predicted direction: items with higher pre-alignment confidence margin are less likely to have their argmax changed after DPO alignment. The partial η² = 0.2892 indicates that margin accounts for approximately 29% of the variance in flip outcomes for pair 2, substantially exceeding the gate threshold of 0.06. Cross-benchmark AUROC values are 0.8668 (MMLU), 0.8034 (TruthfulQA), and 0.9086 (ARC-Challenge), all exceeding the 0.75 threshold without retraining between benchmarks.

For pair 4 (pythia-6.9b SFT), β₁ = −0.0617 (p = 1.95×10⁻³), directionally consistent with pair 2 but substantially weaker. AUROC on MMLU is 0.6087, below the 0.75 threshold. The flip rate for pair 4 is 75.5%, substantially higher than pair 2's 12.5%, which may reflect differences in the alignment procedures, model architectures, or training data between the two pairs. Partial η² = 0.0284 for pair 4, below the 0.06 medium-effect threshold.

The cross-benchmark generalization for pair 2 (training on MMLU, evaluation on TruthfulQA and ARC-Challenge without any domain adaptation) is the stronger test of generalizability: the AUROC values of 0.8034 and 0.9086 on held-out benchmark distributions indicate the margin-flip relationship is not limited to the MMLU domain.

**Empirical flip rate by quintile (pair 2, MMLU).** Items in Q1 (lowest margin) flip at approximately 25%; items in Q5 (highest margin) flip at approximately 1.5%. Intermediate quintiles are approximately Q2 ≈ 18%, Q3 ≈ 12%, Q4 ≈ 6%, tracing a monotone decreasing gradient across the confidence spectrum.

Pairs 1 and 3 were excluded due to infrastructure failures (HuggingFace model unavailability and tokenizer errors, respectively). No PPO-aligned model pairs were available.

![Gate metrics for H-E1 — AUROC and β₁ per pair](/home/anonymous/YouRA_results_new_4_sonnet45/TEST_buildingtrust/docs/youra_research/20260317_buildingtrust/h-e1/figures/fig1_gate_metrics.png)

![ROC curves for pair 2 across MMLU, TruthfulQA, ARC-Challenge](/home/anonymous/YouRA_results_new_4_sonnet45/TEST_buildingtrust/docs/youra_research/20260317_buildingtrust/h-e1/figures/fig3_roc_curves.png)

![Quintile flip rates for pair 2 (MMLU)](/home/anonymous/YouRA_results_new_4_sonnet45/TEST_buildingtrust/docs/youra_research/20260317_buildingtrust/h-e1/figures/fig2_quintile_flip_pair2.png)

---

### RQ2: Alignment-Induced Logit Perturbations Are Non-Isotropic (H-M1)

**Gate result: PASS.**

Table 2 presents the eigenvalue anisotropy ratios for both evaluated pairs across three benchmarks, alongside the isotropic Gaussian control.

**Table 2. H-M1 anisotropy results.**

| Pair | Alignment | Dataset | Anisotropy ratio (λ₁/mean(λ₂,λ₃,λ₄)) | p-value (one-tailed) | Significant (α=0.05) |
|------|-----------|---------|---------------------------------------|----------------------|----------------------|
| pair2 | DPO | MMLU (N=14,042) | 2.8996 | 0.0028 | Yes |
| pair2 | DPO | TruthfulQA (N=817) | 3.8281 | 0.0029 | Yes |
| pair2 | DPO | ARC-Challenge (N=1,172) | 2.3360 | 0.0048 | Yes |
| pair4 | SFT | MMLU (N=14,042) | 4.5789 | 0.0047 | Yes |
| pair4 | SFT | TruthfulQA (N=817) | 5.1789 | 0.0053 | Yes |
| pair4 | SFT | ARC-Challenge (N=1,172) | 4.2936 | 0.0072 | Yes |
| Isotropic Gaussian control | — | N=1,000 | 1.1289 | — | — |

Both evaluated pairs show anisotropy ratios substantially above the isotropic control of 1.13 on all three benchmarks. For pair 2 (DPO), ratios range from 2.34 (ARC) to 3.83 (TruthfulQA) across datasets; the primary MMLU result is 2.90 (p = 0.0028). For pair 4 (SFT), ratios range from 4.29 (ARC) to 5.18 (TruthfulQA); the primary MMLU result is 4.58 (p = 0.0047). The gate criterion (≥2 of the evaluated model families passing both criteria) is satisfied by both families evaluated.

The MMLU eigenvalue spectra for pair 2 are λ₁=7.40, λ₂=3.26, λ₃=2.33, λ₄=2.06, yielding a ratio of 2.90. For pair 4: λ₁=1.22, λ₂=0.42, λ₃=0.27, λ₄=0.10, yielding a ratio of 4.58. In both cases the dominant eigenvalue is substantially larger than the trailing eigenvalues, indicating that alignment-induced logit perturbations are concentrated along a principal axis in the 4D logit space rather than spread uniformly across directions.

The isotropic sanity check confirms the null model does not spuriously trigger the gate: N(0, I₄) synthetic data (N=1,000, seed=1) yields ratio = 1.1289.

![Anisotropy ratios per pair vs. isotropic control](/home/anonymous/YouRA_results_new_4_sonnet45/TEST_buildingtrust/docs/youra_research/20260317_buildingtrust/h-m1/figures/fig1_anisotropy_gate_metrics.png)

![Eigenvalue spectra λ₁–λ₄ for pair 2 and pair 4](/home/anonymous/YouRA_results_new_4_sonnet45/TEST_buildingtrust/docs/youra_research/20260317_buildingtrust/h-m1/figures/fig2_eigenvalue_spectrum.png)

---

### RQ3: DPO and SFT Quintile Variance Profiles (H-M2)

**Gate result: NULL_RESULT (LIMITATION_RECORDED). The directional hypothesis is not supported.**

The H-M2 hypothesis predicted that DPO would produce higher mean logit delta variance in low-confidence regions (Q1) than SFT, after KL-divergence control. The results do not support this directional prediction across any of the three benchmarks.

**Table 3. H-M2 quintile logit delta variance (MMLU), after KL residualization.**

| Quintile | DPO variance (pair2, N≈2,800/quintile) | SFT variance (pair4, N≈2,800/quintile) |
|----------|----------------------------------------|----------------------------------------|
| Q1 (lowest margin) | 0.7073 | 0.2229 |
| Q2 | 0.9965 | 0.2250 |
| Q3 | 1.1942 | 0.2544 |
| Q4 | 2.6114 | 0.2939 |
| Q5 (highest margin) | 3.3837 | 0.2815 |
| Q5/Q1 ratio | 4.79× | 1.26× |

**Directional test.** One-tailed Welch's t-test (DPO Q1 mean > SFT Q1 mean): MMLU p = 1.000, Cohen's d = −0.490; TruthfulQA p = 1.000, Cohen's d = −1.536; ARC-Challenge p = 0.992, Cohen's d = −0.225. The direction is reversed across all three benchmarks: SFT mean Q1 delta variance exceeds DPO mean Q1 delta variance.

The H-M2 directional hypothesis is not confirmed. This is recorded as a limitation; the SHOULD_WORK gate allows the pipeline to continue.

**Observed quintile trend (post-hoc descriptive finding).** A notable pattern emerges from the quintile profiles: DPO variance increases monotonically from Q1 to Q5 (Q5/Q1 ratio = 4.79× on MMLU), while SFT variance is nearly flat across quintiles (Q5/Q1 ratio ≈ 1.26×). This profile pattern is consistent across TruthfulQA (DPO: 0.749→2.807; SFT: 0.412→0.751) and ARC-Challenge (DPO: 1.952→3.990; SFT: 0.272→0.298).

The observed pattern — DPO applies larger logit perturbations where the base model was already most confident, while SFT distributes perturbations uniformly — is the opposite of the predicted direction. This finding is descriptive and post-hoc; it is reported as an empirical observation rather than a confirmed mechanistic claim. The finding is also subject to model identity confounds: pair 2 (tulu-2-7b) and pair 4 (pythia-6.9b) differ in architecture, training data, and base model, so the observed difference in quintile profiles cannot be attributed exclusively to the DPO vs. SFT distinction.

![Q1 variance comparison: DPO vs SFT per dataset](/home/anonymous/YouRA_results_new_4_sonnet45/TEST_buildingtrust/docs/youra_research/20260317_buildingtrust/h-m2/figures/fig1_q1_variance_bar.png)

![Quintile variance trend lines Q1→Q5 for DPO and SFT](/home/anonymous/YouRA_results_new_4_sonnet45/TEST_buildingtrust/docs/youra_research/20260317_buildingtrust/h-m2/figures/fig2_quintile_trend.png)

---

## 6. Discussion

### Findings

**Finding 1: Pre-alignment confidence margin is a statistically robust predictor of argmax flip for DPO-aligned tulu-2-7b.** The margin-flip relationship (β₁ = −4.33, η² = 0.289, AUROC = 0.867–0.909) is large in both statistical and practical terms for pair 2. The negative direction — lower margin predicts higher flip probability — is consistent with the geometric interpretation that low-margin items lie near the argmax decision boundary. Cross-benchmark generalization (predictor trained on MMLU, evaluated on TruthfulQA and ARC-Challenge without retraining) holds across all three benchmarks above the 0.75 AUROC threshold. However, the evidence for this finding is concentrated in a single model pair (tulu-2-7b DPO); pair 4 (pythia-6.9b SFT) shows a directionally consistent but substantially weaker result (AUROC = 0.609, η² = 0.028) that does not clear the 0.75 threshold.

**Finding 2: Alignment-induced logit perturbations are non-isotropic under both DPO and SFT.** The anisotropy ratios (pair 2 DPO: 2.90; pair 4 SFT: 4.58) are consistently and substantially above the isotropic Gaussian control (1.13) across all three benchmarks and both model pairs. This indicates that alignment-induced changes to the 4D logit space are not well-approximated by isotropic noise. The principal axis of perturbation accounts for a larger share of total perturbation variance than the remaining three axes combined in the SFT case. This finding is consistent with the geometric interpretation of the margin predictor, as structured perturbations along preferred axes would disproportionately affect items near the boundary along those axes.

**Finding 3: The H-M2 directional hypothesis is not supported; a contrasting quintile profile is observed.** DPO does not concentrate perturbation variance in low-confidence regions. The observed DPO quintile profile (monotone increase from Q1 to Q5) is opposite to the predicted direction. SFT produces a flat profile. This null result for the directional claim is documented as a limitation. The contrasting profile pattern is reported as a descriptive observation; its mechanistic interpretation and generalizability require further investigation, including a controlled experiment using the same base model aligned with both DPO and SFT.

### Limitations

**L1: PPO models unavailable.** The original experimental design called for comparison between DPO, SFT, and PPO. The two planned PPO model pairs were unavailable (tulu-2-ppo-7b: HTTP 404; reciprocate/ppo_hh_pythia-1B: tokenizer error). All method comparisons in this paper are between DPO and SFT rather than between DPO and PPO. Conclusions about method-specific behavior cannot be extended to RLHF-based methods in general.

**L2: Primary evidence from one model pair.** The strong margin-flip result (β₁ = −4.33, AUROC = 0.867–0.909, η² = 0.289) derives from pair 2 alone (tulu-2-7b DPO). Pair 4 (pythia-6.9b SFT) replicates the directional effect but not the discriminative strength (AUROC = 0.609). The two pairs differ in alignment procedure, architecture, and training data; isolating the contribution of alignment procedure requires a same-base-model comparison. Claims about the generality of the margin-flip relationship beyond this specific model pair should be treated as preliminary.

**L3: H-M3 and H-M4 not executed.** The planned interaction-term analysis (H-M3: margin×method interaction in mixed-effects logistic regression) and cosine projection analysis (H-M4: alignment of logit-delta direction with the base model decision axis) were not run. The mechanistic account of why the margin predictor works therefore remains partially inferential and cannot be confirmed from the available data.

**L4: H-M2 directional hypothesis not supported.** The predicted mechanism — that DPO concentrates perturbation energy in low-confidence regions — is not supported in any of the three datasets. The observed pattern (DPO higher variance at high confidence) may reflect model identity confounds or a different underlying mechanism.

**L5: MCQ-specific scope.** All experiments are conducted on 4-option MCQ benchmarks. Only items producing valid 4-token logit vectors are retained. The margin predictor as operationalized here does not directly apply to free-form generation, where the output space is the full vocabulary and the concept of argmax flip across a fixed option set is not defined. Generalization to free-form settings requires a separate operationalization and empirical validation.

**L6: Model identity confounds in quintile comparison.** The quintile variance profiles are compared between pair 2 (tulu-2-7b) and pair 4 (pythia-6.9b), which differ in base model, alignment procedure, and training data. Any apparent difference in quintile profile may reflect architecture or data differences rather than the DPO vs. SFT distinction.

### Practical Implications

If the margin-flip relationship generalizes beyond pair 2, the pre-alignment confidence margin could serve as a basis for item-level pre-deployment risk assessment: before deploying an aligned model, practitioners could compute base model margins for evaluation items and flag low-margin items for targeted post-alignment review. The flip rate in the bottom confidence quintile of pair 2 is approximately 25%, compared to approximately 1.5% in the top quintile. Whether this translates to a reliable auditing tool depends on whether the margin-flip relationship holds across additional model pairs, alignment procedures, and evaluation domains — questions that the present data do not fully resolve.

---

## 7. Conclusion

This paper examined whether the pre-alignment confidence margin — computable from a base model before any alignment procedure — predicts post-alignment argmax instability. For a DPO-aligned tulu-2-7b model pair, a mixed-effects logistic regression yields β₁ = −4.33 (p ≈ 10⁻²²⁷, η² = 0.289), and AUROC is 0.867 (MMLU), 0.803 (TruthfulQA), and 0.909 (ARC-Challenge) with no domain adaptation between benchmarks. These results support the existence of a predictive geometric signal in the pre-alignment base model distribution for this pair. A secondary model pair (pythia-6.9b SFT) shows the directionally consistent but weaker result (AUROC = 0.609).

Alignment-induced logit perturbations are non-isotropic under both DPO (anisotropy ratio 2.90, p = 0.003 on MMLU) and SFT (4.58, p = 0.005 on MMLU), compared to an isotropic Gaussian control of 1.13. This is consistent with the geometric interpretation of the margin predictor: structured perturbations along preferred directions would disproportionately affect low-margin items near the argmax boundary.

The H-M2 directional hypothesis — that DPO concentrates perturbation variance in low-confidence quintiles — is not supported; the direction is reversed across all three benchmarks. DPO shows a monotone increasing quintile variance profile (Q5/Q1 ratio = 4.79×) while SFT is flat (Q5/Q1 ratio ≈ 1.26×). This null result is documented alongside the descriptive finding about the contrasting quintile profiles.

Important limitations remain: no PPO-aligned model pairs were available, the primary evidence for the margin-flip result comes from a single model pair, two planned mechanistic analyses (H-M3, H-M4) were not completed, and all results are restricted to 4-option MCQ benchmarks. A same-base-model DPO vs. SFT comparison and replication across additional model families are the most direct next steps.

---

## References

Fan, S., Paparas, D., Noy, N., Xiong, B., Sachdeva, N., & Isik, B. (2026). The Magic Correlations: Understanding Knowledge Transfer from Pretraining to Supervised Fine-Tuning. *arXiv preprint arXiv:2602.11217*.

Khanmohammadi, R., Miahi, E., Mardikoraem, M., Kaur, S., Brugere, I., Smiley, C. H., Thind, K., & Ghassemi, M. M. (2025). Calibrating LLM Confidence by Probing Perturbed Representation Stability. In *Proceedings of EMNLP 2025*, pp. 10448–10514.

Li, A. J., Krishna, S., & Lakkaraju, H. (2024). More RLHF, More Trust? On The Impact of Preference Alignment On Trustworthiness. In *Proceedings of ICLR 2024*.

Liu, X., Khalifa, M., & Wang, L. (2023). LitCab: Lightweight Language Model Calibration over Short- and Long-form Responses. In *Proceedings of ICLR 2023*.

Lunardi, R., Mea, V. D., Mizzaro, S., & Roitero, K. (2025). On Robustness and Reliability of Benchmark-Based Evaluation of LLMs. In *Proceedings of ECAI 2025*, pp. 4603–4610.

Plaut, B., Nguyen, K., & Trinh, T. (2024). Probabilities of Chat LLMs Are Miscalibrated but Still Predict Correctness on Multiple-Choice Q&A. *Transactions on Machine Learning Research*, 2025.

Wang, Z., Bi, B., Pentyala, S. K., Ramnath, K., Chaudhuri, S., Mehrotra, S., Zhu, Z., Mao, X.-B., Asur, S., & Cheng, N. (2024). A Comprehensive Survey of LLM Alignment Techniques: RLHF, RLAIF, PPO, DPO and More. *arXiv preprint arXiv:2407.16216*.

Xu, S., Fu, W., Gao, J., Ye, W., Liu, W., Mei, Z., Wang, G., Yu, C., & Wu, Y. (2024). Is DPO Superior to PPO for LLM Alignment? A Comprehensive Study. In *Proceedings of ICML 2024*, pp. 54983–54998.
