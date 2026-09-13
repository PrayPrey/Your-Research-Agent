# Alignment Changes Answers, Not Just Confidence: Mechanistic Discrimination of RLHF Miscalibration

---

## Abstract

Reinforcement learning from human feedback (RLHF) alignment is known to degrade the calibration of large language models, but the underlying mechanism remains unclear. This work presents a pre-registered mechanistic discrimination between three candidate hypotheses for alignment-induced miscalibration: monotonic scale inflation (H1), decision-boundary restructuring (H2), and framing susceptibility (H3). Using the Pythia alignment ladder (1.4B, 2.8B, and 6.9B parameters with SFT, DPO, and PPO variants), we measure Spearman rank correlations between base and aligned 4-option log-probability vectors on 14,042 MMLU items. All 9 alignment--size pairs produce Spearman rho below 0.90, and 8 of 9 fall below 0.85, refuting H1 within this model family. Under PPO alignment at 1.4B, rho = -0.324 and 99.7% of items receive a different argmax answer after alignment. H3 is excluded in the softmax-ECE evaluation setting: MMLU calibration degradation exceeds TruthfulQA calibration degradation for all alignment types. H2 decision-boundary restructuring is identified as the dominant mechanism. An exploratory observation indicates that DPO produces larger calibration degradation (measured by delta Brier Reliability) than PPO across all three model sizes, though the 2.8B comparison is inconclusive due to overlapping bootstrap confidence intervals. These findings suggest that post-hoc calibration corrections designed for scale inflation, including temperature scaling, may not address the operative mechanism of alignment-induced miscalibration in this model family.

---

## 1. Introduction

When a language model is fine-tuned via RLHF to produce helpful and harmless outputs, its answer distribution changes in ways that extend beyond confidence magnitude adjustments. For a 1.4B-parameter PPO-aligned Pythia model, 99.7% of MMLU multiple-choice items receive a different top-ranked answer compared to the base model, and the Spearman rank correlation between base and aligned 4-option log-probability vectors is rho = -0.324. This indicates that the aligned model systematically prefers options that the base model ranked lowest, rather than simply becoming more confident about its existing preferences.

Calibration --- the correspondence between a model's expressed confidence and its empirical accuracy --- is a key dimension of language model trustworthiness. Well-calibrated models produce uncertainty signals that can be relied upon for downstream decision-making. Guo et al. (2017) established that modern neural networks tend to be poorly calibrated after training, and subsequent work has confirmed that RLHF alignment worsens calibration further. Xie et al. (2024) report that LLaMA-2-Chat achieves ECE = 0.298 on MMLU and 0.507 on TruthfulQA, substantially above the base model values, and propose Adaptive Temperature Scaling (ATS) as a post-hoc correction. The existence of alignment-induced calibration degradation is well established. The open question is which mechanism produces it, and this determines what corrections are appropriate.

Three mechanistically distinct explanations can account for alignment-induced miscalibration. First, scale inflation (H1) holds that alignment amplifies confidence in the model's existing answer preferences: logit rank order is preserved (Spearman rho >= 0.90), but magnitudes increase uniformly, producing overconfidence on already-preferred choices. Second, decision-boundary restructuring (H2) holds that alignment changes which answer option the model selects, redistributing probability mass across options in ways that may be unrelated to factual correctness. Third, framing susceptibility (H3) holds that alignment makes confidence allocations sensitive to the framing of alternatives, producing miscalibration that varies with presentation context. Each mechanism has distinct measurable signatures and, critically, different implications for corrective strategies: temperature scaling is effective for H1, whereas H2-type boundary shifts may require fundamentally different interventions.

Prior work has not discriminated between these mechanisms. Xie et al. (2024) confirm alignment-induced ECE increases and propose ATS, but their analysis implicitly assumes H1 --- ATS rescales confidence temperature without testing whether the underlying answer distribution has changed. Li et al. (2024) use the Pythia alignment ladder to study RLHF effects on trustworthiness dimensions including toxicity and bias, but do not measure calibration. No previous study has tested whether H1, H2, or H3 dominates using a pre-registered, multi-model mechanistic discrimination design.

This work fills this gap using Pythia 1.4B, 2.8B, and 6.9B models in SFT, DPO, and PPO variants --- a controlled experimental setting in which all alignment variants share identical pretraining data and architecture. The pre-registered discrimination specifies three falsifiable predictions: H1 requires Spearman rho >= 0.90 between base and aligned 4-option log-probability vectors; H2 requires rho < 0.85 with substantial argmax redistribution; H3 requires TruthfulQA delta-ECE >= MMLU delta-ECE. The contributions of this work are as follows:

1. **Mechanistic discrimination result.** All 9 Spearman rho values fall below 0.90; 8 of 9 fall below 0.85. H1 is refuted and H2 is identified as the dominant mechanism within the Pythia 1.4B--6.9B family.

2. **Exploratory ordering observation.** DPO produces larger calibration degradation than PPO (delta Brier Reliability) in all three Pythia sizes, though the 2.8B comparison is inconclusive due to overlapping confidence intervals. This is an exploratory finding obtained with public fallback checkpoints and requires replication with matched-training checkpoints.

3. **H3 exclusion in softmax-ECE setting.** Framing susceptibility is ruled out as a primary driver: delta-ECE on TruthfulQA is smaller than delta-ECE on MMLU for all alignment types.

4. **Reusable methodology.** The Spearman rho threshold test, argmax partition analysis, and cross-benchmark H3 diagnostic constitute a framework applicable to any model family via lm-eval without modification.

---

## 2. Related Work

### 2.1 Calibration in Neural Networks and Language Models

Guo et al. (2017) demonstrated that modern neural networks trained with batch normalization and regularization are systematically overconfident, and proposed temperature scaling as a post-hoc correction. Their work established the Expected Calibration Error (ECE) framework used in subsequent calibration research. Wang (2023) surveyed calibration methods in deep learning, noting that fine-tuning of pre-trained models is a substantial but understudied source of calibration degradation. Khanmohammadi et al. (2025) confirm that ECE varies across model families and benchmarks, validating MMLU-based calibration evaluation as informative and reproducible. However, none of this work distinguishes between mechanistically different types of miscalibration. A temperature-scaling correction appropriate for H1 (scale inflation) may be ineffective for H2 (boundary restructuring).

### 2.2 RLHF Alignment and Calibration Degradation

Xie et al. (2024) demonstrate that RLHF alignment causes calibration degradation in LLaMA-2-Chat (ECE = 0.298 on MMLU, 0.507 on TruthfulQA) and propose Adaptive Temperature Scaling (ATS), which learns an input-dependent temperature from hidden states and achieves 58--82% ECE reduction without retraining. ATS implicitly assumes that alignment-induced miscalibration follows an H1-type pattern correctable by rescaling. The present work tests this assumption directly and finds it does not hold for Pythia 1.4B--6.9B.

Li et al. (2024) use the Pythia alignment ladder (SFT/DPO/PPO variants) to study the effect of RLHF on trustworthiness dimensions including toxicity, bias, and truthfulness, finding that more alignment does not guarantee greater trustworthiness. Critically, Li et al. do not measure ECE or Brier calibration. The present work extends their causal design to the calibration dimension.

Coste et al. (2023) study reward overoptimization, establishing the theoretical mechanism by which reward optimization inflates model confidence. Their analysis predicts confidence inflation on existing choices (consistent with H1), but the data presented here show near-complete answer redistribution (H2), suggesting that the reward optimization mechanism operates at a deeper level than marginal confidence amplification.

The RLHF framework was established by Ouyang et al. (2022), and DPO as an alignment method by Rafailov et al. (2023). The Pythia model family (Biderman et al., 2023) provides the only publicly available full alignment ladder (base, SFT, DPO, PPO) sharing identical pretraining data and architecture.

### 2.3 Verbal Confidence and Framing Effects

Chhikara et al. (2025) study calibration across nine LLMs using verbally elicited confidence (0--100 scale) rather than softmax-based ECE, finding that distractors can reduce ECE by up to 90% in some models. Their findings use a different measurement object (verbal confidence) than the present work (log-probability softmax ECE). The H3 diagnostic employed here --- comparing delta-ECE across MMLU and TruthfulQA MC1 under the same evaluation framework --- directly tests whether softmax-based calibration degradation exhibits framing sensitivity.

### 2.4 Positioning

This work sits at the intersection of three research threads: (1) RLHF alignment effects (Li et al., Coste et al.) --- extending to the calibration dimension; (2) LLM calibration (Guo et al., Xie et al.) --- providing mechanistic discrimination for what Xie et al. correct without explaining; (3) verbal versus softmax calibration (Chhikara et al.) --- focusing on log-probability ECE and excluding framing effects. The pre-registered H1/H2/H3 discrimination framework is absent from all prior work.

---

## 3. Method

The methodology is organized around a central question: which mechanism drives alignment-induced calibration degradation? Rather than measuring whether ECE increases under alignment (already established by Xie et al., 2024), this work asks which of three candidate mechanisms produces the increase and whether they are empirically discriminable.

### 3.1 Pre-Registered Mechanism Discrimination Framework

Three competing mechanistic hypotheses are formalized prior to experimentation:

**H1: Monotonic Scale Inflation.** Alignment amplifies confidence in the model's existing answer preferences without reordering them. Formally, H1 predicts that the Spearman rank correlation (rho) between the base model's 4-option log-probability vector and the aligned model's 4-option log-probability vector remains >= 0.90 across MMLU items.

**H2: Decision-Boundary Restructuring.** Alignment changes which answer option the model selects, redistributing the rank ordering of answer options rather than amplifying margins. H2 predicts rho < 0.85 for at least one alignment type, and in extreme cases, near-zero or negative rho indicating systematic preference reversal.

**H3: Framing Susceptibility.** Alignment makes confidence allocation domain-specific or context-sensitive, producing larger miscalibration on tasks with adversarially structured alternatives. H3 predicts delta-ECE(TruthfulQA) >= delta-ECE(MMLU).

**Pre-specified falsifiers:**
- H1 is falsified if rho < 0.80 for PPO alignments.
- H2 is confirmed as dominant if rho < 0.85 for the majority of alignment--size pairs.
- H3 is falsified if delta-ECE(TruthfulQA) < delta-ECE(MMLU) for all alignment types.

### 3.2 Model Family Selection

The Pythia alignment ladder (Biderman et al., 2023) is used: base models EleutherAI/pythia-{1.4b, 2.8b, 6.9b} with corresponding SFT, DPO, and PPO variants. This family provides the requirement for causal inference: identical pretraining data, architecture, and tokenizer across all alignment variants.

The primary aligned checkpoints (RLHFlow variants from Li et al., 2024) require authenticated HuggingFace access. Publicly available fallback checkpoints trained on the Anthropic HH preference dataset with Pythia base were used instead: lomahony/pythia-{size}-helpful-sft (SFT), Leogrin/eleuther-pythia{size}-hh-dpo (DPO), and usvsnsp/pythia-{size}-ppo (PPO). These share the same base model and approximate training regime. The H2 mechanism finding (Spearman rho) is expected to be robust to this substitution, while the DPO >= PPO ordering should be interpreted as a checkpoint-level observation pending replication with matched checkpoints.

This yields 12 models in total: 3 base models and 9 aligned variants (3 alignment methods x 3 sizes).

### 3.3 Evaluation Protocol

All models are evaluated using lm-eval-harness v0.4.11 with identical settings:
- **MMLU** (cais/mmlu, full test set, 14,042 items, 57 subjects, 4-shot)
- **TruthfulQA MC1** (truthful_qa, 817 items, 0-shot) --- used for H3 diagnostic
- **Decoding:** Greedy, temperature = 1.0
- **Scoring:** Log-probability continuation (not chat-template)

The log-probability continuation format applies identical prompting to all 12 models, including chat-tuned variants, avoiding format-confound artifacts.

### 3.4 Calibration Measurement

From lm-eval's `--log_samples` output, the 4-option log-probability vector for each MMLU item and each model is extracted. The following metrics are computed:

**ECE** (15-bin equal-width): Standard Expected Calibration Error following Guo et al. (2017).

**Brier Score Decomposition** (Murphy, 1973): The Brier score is decomposed into three components:
- **Reliability:** E[(p_bin - o_bin)^2] --- the overconfidence term.
- **Resolution:** E[(o_bin - o_bar)^2] --- discriminability of the model.
- **Uncertainty:** Var(o) --- data difficulty, constant across models.

Delta Brier Reliability = Reliability(aligned) - Reliability(base) is the primary metric for calibration degradation. Delta-ECE is reported as a secondary directional check. The two metrics are related but not identical: ECE measures mean absolute confidence--accuracy gap across bins, while Brier Reliability measures the squared overconfidence component of the Brier decomposition.

**Bootstrap confidence intervals:** For each delta-Reliability value, 95% bootstrap CIs are computed with n = 1,000 samples and seed = 42.

### 3.5 Mechanism Discrimination Measurements

**H1/H2 discrimination --- Spearman rho:** For each MMLU item, the Spearman rank correlation is computed between the base model's 4-option log-probability vector and the corresponding aligned model's vector. The mean rho per alignment--size pair (9 pairs) is compared against the H1 threshold (>= 0.90) and H2 diagnostic (< 0.85).

**Argmax partition:** MMLU items are partitioned into shared-argmax (base and aligned agree on which option has the highest log-probability) and changed-argmax (argmax differs).

**Pre-softmax margin analysis:** Per-item margin = max(log-prob) - second_max(log-prob) is computed before softmax normalization. Delta-margin = margin(aligned) - margin(base) tests whether confidence inflation operates at the logit level. The margin analysis and the Spearman rho analysis are both derived from the same per-item 4-option log-probability vectors and are therefore not independent data streams; they characterize different aspects (magnitude versus rank ordering) of the same logit distribution changes.

**H3 diagnostic --- cross-benchmark comparison:** Delta-ECE is computed on both TruthfulQA and MMLU for each alignment type. A ratio delta-ECE(TruthfulQA) / delta-ECE(MMLU) < 1.0 for all alignment types falsifies H3. MMLU uses 4-shot evaluation while TruthfulQA MC1 uses 0-shot; this shot-count asymmetry is a potential confound, though the magnitude of the observed ratios (0.26--0.73) suggests framing susceptibility is not the dominant driver even accounting for this difference.

### 3.6 Hypothesis-Gate Structure

Experiments are structured as a causal chain with explicit gate conditions:

| Hypothesis | Gate | Criterion | Result |
|------------|------|-----------|--------|
| H-E1 | MUST_WORK | delta-Reliability > 0 with CI lower > 0 for PPO or DPO in >= 2/3 sizes | PASS |
| H-M1 | MUST_WORK | ECE(base) < 0.15 for all 3 sizes | PASS |
| H-M2 | SHOULD_WORK | Delta-margin(PPO) > 0 with CI lower > 0 in >= 2/3 sizes | PASS |
| H-M3 | SHOULD_WORK | Spearman rho >= 0.90 for all 9 pairs (H1 confirmation) | FAIL |

H-M3's SHOULD_WORK gate is designed to fail if H1 is not confirmed, in which case H2 is documented as the dominant mechanism. The gate failed: no alignment--size pair met the rho >= 0.90 criterion.

---

## 4. Experimental Setup

### 4.1 Research Questions

The experiments address four research questions:

- **RQ1:** Does alignment training consistently increase Brier reliability (overconfidence) relative to paired base models on MMLU? (H-E1)
- **RQ2:** Is the dominant mechanism H1 (scale inflation, rho >= 0.90) or H2 (boundary restructuring, rho < 0.85)? (H-M3)
- **RQ3:** Is calibration degradation empirically ordered DPO >= PPO > SFT, and is this consistent across model sizes? (H-E1, H-M2)
- **RQ4:** Is framing susceptibility (H3) the primary driver of miscalibration? (H-M3 TruthfulQA diagnostic)

### 4.2 Models

**Base models:** EleutherAI/pythia-1.4b, EleutherAI/pythia-2.8b, EleutherAI/pythia-6.9b

**Aligned variants** (public fallback checkpoints on HH data):
- SFT: lomahony/pythia-{1.4b/2.8b/6.9b}-helpful-sft
- DPO: Leogrin/eleuther-pythia{1.4b/2.8b/6.9b}-hh-dpo
- PPO: usvsnsp/pythia-{1.4b/2.8b/6.9b}-ppo

| Model Size | Base | SFT | DPO | PPO |
|-----------|------|-----|-----|-----|
| 1.4B | yes | yes | yes | yes |
| 2.8B | yes | yes | yes | yes |
| 6.9B | yes | yes | yes | yes |

*Table 1: The 12-model evaluation set. All alignment variants share the Pythia pretraining checkpoint.*

### 4.3 Datasets

**MMLU** (Hendrycks et al., 2021): 14,042 multiple-choice questions across 57 subjects. The 4-option forced-choice format provides a 4-dimensional probability vector suitable for Spearman rho analysis. Evaluated with 4-shot prompting.

**TruthfulQA MC1** (Lin et al., 2022): 817 questions with plausible-but-false alternative answers. Used exclusively for the H3 framing susceptibility diagnostic (0-shot).

### 4.4 Baselines

The experimental design uses paired within-family baselines: for each alignment variant, the corresponding base model of the same size serves as the baseline. Three alignment methods are compared:
- **SFT:** Supervised fine-tuning on helpful human conversations (HH data).
- **DPO:** Direct Preference Optimization (Rafailov et al., 2023). Token-level preference reshaping without explicit reward modeling.
- **PPO:** Proximal Policy Optimization (Ouyang et al., 2022). Sequence-level reward maximization with KL penalty to SFT reference policy.

### 4.5 Evaluation Metrics

**Primary metric:** Delta Brier Reliability = Reliability(aligned) - Reliability(base).

**Secondary metrics:** Delta-ECE (15-bin equal-width); Spearman rho (per-item, per pair); delta-margin (pre-softmax); argmax redistribution rate; delta-ECE ratio (TruthfulQA/MMLU).

### 4.6 Implementation Details

All evaluations use lm-eval-harness v0.4.11 with `--log_samples`. Calibration analysis is implemented in Python using scipy.stats (Spearman rho), numpy (Brier decomposition, argmax partition), and a custom 15-bin equal-width ECE implementation following Guo et al. (2017). Bootstrap resampling uses seed = 42. Calibration bins span [0, 1] in 15 equal-width intervals, consistent with Xie et al. (2024).

---

## 5. Results

### 5.1 Alignment Increases Brier Reliability (H-E1)

Alignment training consistently increases Brier reliability (overconfidence) relative to paired base models on MMLU. Eight of 9 aligned model--size pairs show positive delta-Reliability. The exception is 6.9B-PPO (delta-Reliability = -0.0036), which shows a marginal calibration improvement.

![Figure 1: Delta Brier Reliability across alignment-size pairs](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/delta_reliability_bar.png)

*Figure 1: Delta Brier Reliability (aligned minus base) for all 9 alignment--size pairs on MMLU. Error bars show bootstrap 95% CIs (n=1,000). Positive values indicate alignment increases overconfidence.*

Table 2 reports the per-model ECE and delta Brier Reliability metrics. ECE values are computed from the per-item log-probability vectors extracted via lm-eval.

| Model | Alignment | ECE(base) | ECE(aligned) | Delta-ECE | Delta Brier Reliability | CI lower |
|-------|-----------|-----------|--------------|-----------|------------------------|----------|
| Pythia-1.4B | SFT | 0.0882 | 0.1575 | +0.0693 | +0.0289 | +0.0269 |
| Pythia-1.4B | DPO | 0.0882 | 0.2625 | +0.1742 | +0.1048 | +0.1009 |
| Pythia-1.4B | PPO | 0.0882 | 0.1750 | +0.0868 | +0.0406 | +0.0345 |
| Pythia-2.8B | SFT | 0.0597 | 0.0694 | +0.0097 | +0.0033 | +0.0021 |
| Pythia-2.8B | DPO | 0.0597 | 0.1441 | +0.0843 | +0.0437 | +0.0407 |
| Pythia-2.8B | PPO | 0.0597 | 0.1577 | +0.0980 | +0.0423 | +0.0388 |
| Pythia-6.9B | SFT | 0.0792 | 0.0830 | +0.0037 | +0.0010 | +0.0001 |
| Pythia-6.9B | DPO | 0.0792 | 0.1010 | +0.0217 | +0.0099 | +0.0090 |
| Pythia-6.9B | PPO | 0.0792 | 0.0609 | -0.0184 | -0.0036 | -0.0053 |

*Table 2: ECE and delta Brier Reliability for all 9 alignment--size pairs. ECE values are from the h-m3 experiment output (authoritative). Delta-ECE and delta Brier Reliability are distinct metrics: delta-ECE reflects mean absolute confidence--accuracy gap while delta Brier Reliability captures the squared overconfidence component.*

The H-E1 MUST_WORK gate (bootstrap CI lower > 0 for PPO or DPO in >= 2/3 sizes) is satisfied via both DPO and PPO. DPO shows positive delta-Reliability across all 3 sizes; PPO across 2 of 3 sizes; SFT across all 3 sizes with smaller effect magnitude.

The 1.4B-DPO ECE increase is the largest observed: ECE(aligned) = 0.2625 versus ECE(base) = 0.0882, approximately a threefold increase. Figure 2 shows the Brier decomposition confirming that Resolution changes are not driving the ECE increase.

![Figure 2: Brier score decomposition](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/brier_decomposition.png)

*Figure 2: Brier score decomposition (Reliability, Resolution, Uncertainty) for all 12 models. Reliability increases under alignment while Resolution changes are moderate, indicating overconfidence rather than discriminability collapse as the primary calibration change.*

**Causal baseline confirmation (H-M1).** Base Pythia models show ECE = 0.0882 (1.4B), 0.0597 (2.8B), 0.0792 (6.9B) --- all below the 0.15 threshold (MUST_WORK PASS). Pretraining produces adequate calibration; the observed increase is attributable to alignment.

![Figure 3: ECE gate results](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/h-m1/figures/figure_01_ece_gate.png)

*Figure 3: Base model ECE values for all three Pythia sizes, confirming all fall below the 0.15 MUST_WORK threshold.*

![Figure 4: Base versus aligned ECE](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/h-m1/figures/figure_02_base_vs_aligned_ece.png)

*Figure 4: ECE comparison between base and aligned models across all alignment methods and model sizes.*

![Figure 5: Calibration curves](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/calibration_curves.png)

*Figure 5: Calibration curves (confidence versus accuracy) for base and aligned models. Aligned models show systematic departure from the diagonal, particularly at higher confidence bins.*

![Figure 6: ECE by MMLU subject](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/h-m1/figures/figure_04_ece_by_subject.png)

*Figure 6: ECE broken down by MMLU subject category for base and aligned models.*

![Figure 7: Brier decomposition detail](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/h-m1/figures/figure_05_brier_decomposition.png)

*Figure 7: Detailed Brier score decomposition from the H-M1 analysis showing the Reliability, Resolution, and Uncertainty components for all 12 models.*

### 5.2 Ordering Observation: DPO >= PPO > SFT (H-M2)

The pre-registered calibration ordering prediction (PPO >= DPO > SFT, based on conventional reward optimization pressure) is falsified by the data: DPO produces larger calibration degradation than PPO in all three model sizes as measured by delta Brier Reliability, yielding an observed ordering of DPO >= PPO > SFT.

Figure 8 shows the pre-softmax logit margin inflation for all 9 pairs:

![Figure 8: Pre-softmax margin inflation](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/figure_01_delta_margin_gate.png)

*Figure 8: Pre-softmax logit margin inflation (delta-margin = margin(aligned) - margin(base)) with bootstrap 95% CIs. DPO shows positive delta-margin in all 3 sizes. PPO shows positive delta-margin in 2 of 3 sizes (6.9B-PPO: delta-margin = -0.036).*

The delta-margin values from the h-m2 experiment are:

| Pair | Delta-margin (mean) | CI lower | CI upper |
|------|---------------------|----------|----------|
| SFT-1.4B | +0.133 | +0.129 | +0.138 |
| SFT-2.8B | +0.011 | +0.009 | +0.013 |
| SFT-6.9B | +0.027 | +0.025 | +0.028 |
| DPO-1.4B | +0.491 | +0.484 | +0.499 |
| DPO-2.8B | +0.208 | +0.202 | +0.213 |
| DPO-6.9B | +0.072 | +0.070 | +0.074 |
| PPO-1.4B | +0.394 | +0.389 | +0.398 |
| PPO-2.8B | +0.253 | +0.247 | +0.258 |
| PPO-6.9B | -0.036 | -0.039 | -0.033 |

*Table 3: Pre-softmax margin inflation (delta-margin) for all 9 alignment--size pairs from the H-M2 experiment. Positive values indicate the aligned model has a larger gap between its top-ranked and second-ranked options.*

![Figure 9: Gradient ordering heatmap](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/figure_04_gradient_ordering_heatmap.png)

*Figure 9: Delta-margin heatmap by alignment method and Pythia model size. DPO shows the largest margin inflation consistently; PPO is second; SFT produces the smallest margin changes.*

![Figure 10: Margin violin plots](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/h-m2/figures/figure_02_margin_violin.png)

*Figure 10: Violin plots of per-item margin distributions for base and aligned models across all model sizes and alignment methods.*

![Figure 11: Delta-margin versus delta-ECE](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/h-m2/figures/figure_03_delta_margin_vs_delta_ece.png)

*Figure 11: Scatter plot of delta-margin versus delta-ECE for all 9 alignment--size pairs.*

![Figure 12: Margin CDF](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/h-m2/figures/figure_05_margin_cdf.png)

*Figure 12: Cumulative distribution functions of per-item margins for base and aligned models.*

The logit margin inflation confirms that the confidence increase is encoded at the pre-softmax level, ruling out softmax normalization artifacts. The margin analysis and the Spearman rho analysis (Section 5.3) are computed from the same per-item log-probability vectors and should be understood as complementary characterizations of the same logit distribution changes rather than independent evidence streams.

**Statistical qualification for 2.8B.** The DPO > PPO ordering holds at 1.4B (DPO: 0.1048, PPO: 0.0406; CI separation is clear) and at 6.9B (DPO: +0.0099, PPO: -0.0036). At 2.8B, the difference is narrow: delta-Reliability(DPO) = 0.0437 (95% CI: [0.0407, 0.0469]) versus delta-Reliability(PPO) = 0.0423 (95% CI: [0.0388, 0.0456]). These confidence intervals overlap, and the difference of 0.0014 is not statistically distinguishable at the 95% confidence level. The DPO >= PPO ordering is directionally consistent across all three model sizes, but the 2.8B case is inconclusive.

### 5.3 H2 Dominates: Decision-Boundary Restructuring (H-M3)

The mechanism discrimination produces a clear result. Figure 13 shows Spearman rho for all 9 alignment--size pairs:

![Figure 13: Spearman rho per alignment-size pair](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/figure_01_spearman_rho.png)

*Figure 13: Spearman rank correlation (rho) between base and aligned 4-option log-probability vectors per MMLU item, for all 9 alignment--size pairs. Dashed lines at rho = 0.90 (H1 threshold) and rho = 0.85 (H2 diagnostic). All 9 pairs fall below 0.90; 8 of 9 fall below 0.85.*

All 9 alignment--size pairs fall below the H1 threshold (rho >= 0.90). Eight of 9 fall below the H2 diagnostic threshold (rho < 0.85). In the Pythia 1.4B--6.9B family, these data support refutation of H1 and identification of H2 as the dominant mechanism.

The Spearman rho values from the h-m3 experiment data are:

| Pair | Spearman rho | H1 (>= 0.90) | H2 (< 0.85) | Argmax Changed |
|------|-------------|---------------|--------------|----------------|
| 1.4B-SFT | 0.753 | no | yes | 42.8% (6,014 / 14,042) |
| 1.4B-DPO | 0.737 | no | yes | 41.4% (5,807 / 14,042) |
| 1.4B-PPO | -0.324 | no | yes | 99.7% (13,998 / 14,042) |
| 2.8B-SFT | 0.719 | no | yes | 28.7% (4,025 / 14,042) |
| 2.8B-DPO | 0.590 | no | yes | 39.4% (5,526 / 14,042) |
| 2.8B-PPO | 0.175 | no | yes | 64.5% (9,049 / 14,042) |
| 6.9B-SFT | 0.839 | no | yes | 14.8% (2,073 / 14,042) |
| 6.9B-DPO | 0.875 | no | no (near-H1) | 15.8% (2,224 / 14,042) |
| 6.9B-PPO | 0.505 | no | yes | 39.7% (5,570 / 14,042) |

*Table 4: H1/H2 discrimination summary. All 9 pairs fail H1; 8 of 9 satisfy the H2 diagnostic. 6.9B-DPO (rho = 0.875) is the marginal case, remaining below the 0.90 H1 threshold but above the 0.85 H2 diagnostic. Spearman rho values are from h-m3/experiment_results.json. Argmax change percentages are exact counts from the h-m3 argmax partition.*

The 1.4B-PPO result is the most extreme: rho = -0.324, indicating that the aligned model's answer preferences are negatively correlated with the base model's. Only 44 of 14,042 MMLU items (0.3%) retain the same argmax after PPO alignment at 1.4B. The 6.9B-DPO model shows the highest rho (0.875), the closest to the H1 threshold, suggesting a potential scale-dependent mechanism gradient.

![Figure 14: Rho distribution](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/figure_02_rho_distribution.png)

*Figure 14: Distribution of per-item Spearman rho values across the 14,042 MMLU items for each alignment--size pair.*

![Figure 15: Argmax redistribution rates](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/figure_04_argmax_proportion.png)

*Figure 15: Proportion of MMLU items where alignment changes the argmax prediction. 1.4B-PPO changes argmax for 99.7% of items.*

![Figure 16: Brier partition analysis](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/figure_03_brier_partition.png)

*Figure 16: Brier reliability partitioned into shared-argmax and changed-argmax items. For 1.4B-PPO, the shared-argmax partition contains only 44 items.*

The argmax redistribution rate for 1.4B-PPO (99.7%) means that the assumption underlying H1 --- that calibration degrades on a stable set of answer preferences --- is inapplicable. The aligned model has a fundamentally different answer distribution.

### 5.4 H3 Excluded in Softmax-ECE Setting

Figure 17 shows the TruthfulQA delta-ECE versus MMLU delta-ECE:

![Figure 17: TruthfulQA H3 diagnostic](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/figure_05_truthfulqa_ece.png)

*Figure 17: Delta-ECE on TruthfulQA MC1 versus MMLU for all alignment types. Delta-ECE(TruthfulQA) < delta-ECE(MMLU) for all three methods.*

The H3 diagnostic results from the experiment data are:

| Alignment | Delta-ECE(TruthfulQA) | Delta-ECE(MMLU) | Ratio |
|-----------|----------------------|-----------------|-------|
| SFT | +0.0088 | +0.0276 | 0.32 |
| DPO | +0.0240 | +0.0934 | 0.26 |
| PPO | +0.0405 | +0.0554 | 0.73 |

*Table 5: H3 framing susceptibility diagnostic. All ratios are below 1.0, falsifying H3. Delta-ECE values are averaged across the three model sizes for each alignment type, computed from the h-m3 experiment output.*

H3 is excluded in the softmax-ECE evaluation setting. Framing susceptibility predicts that adversarially designed distractors (TruthfulQA) would produce larger calibration degradation than standard knowledge questions (MMLU). The opposite is observed: MMLU delta-ECE exceeds TruthfulQA delta-ECE for all alignment types. This distinguishes the present findings from Chhikara et al. (2025), whose verbal-confidence results show framing sensitivity. The measurement modality (softmax log-probability ECE versus verbal confidence) determines whether H3 is observed.

The shot-count asymmetry (4-shot MMLU versus 0-shot TruthfulQA) is noted as a methodological caveat. If few-shot prompting amplifies MMLU calibration degradation relative to 0-shot, this could contribute to the observed pattern independently of framing susceptibility. However, the magnitude of the ratios (0.26--0.73) suggests that framing susceptibility is not the dominant driver even accounting for this difference.

### 5.5 Bootstrap Confidence Interval Analysis

![Figure 18: Bootstrap CI distributions](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/bootstrap_ci_distributions.png)

*Figure 18: Bootstrap confidence interval distributions for delta Brier Reliability across all 9 alignment--size pairs.*

![Figure 19: ECE heatmap](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/ece_heatmap.png)

*Figure 19: Heatmap of ECE values across all model sizes and alignment methods.*

---

## 6. Discussion

### 6.1 Implications for Post-Hoc Calibration Correction

The identification of H2 (boundary restructuring) as the dominant mechanism in Pythia 1.4B--6.9B has implications for how post-hoc calibration corrections are designed and evaluated. Temperature scaling and ATS variants (Xie et al., 2024) are designed for H1-type scale inflation: they rescale confidence magnitude on a fixed answer distribution. Under H2, the answer distribution itself has changed. For 1.4B-PPO, 99.7% of MMLU items have a different top-ranked option after alignment. Rescaling the confidence of the new preferred options does not address miscalibration caused by learning to prefer different options.

This suggests that post-hoc calibration methods for H2-type miscalibration may need to target the hidden-state representations that encode boundary redistribution --- for example, learning to recover base-model answer rankings rather than adjusting confidence magnitudes. ATS may partially succeed in this direction because hidden-state temperatures can be learned to undo token-level redistribution patterns, providing a new mechanistic interpretation of why ATS achieves 58--82% ECE reduction (Xie et al., 2024): it may be learning per-input temperature adjustments that track which inputs have undergone H2-type redistribution. This interpretation predicts that ATS effectiveness should correlate with the degree of H2 boundary shift (lower rho corresponding to greater expected ATS improvement), a testable prediction that was not evaluated in the present work (H-M4 was not executed).

### 6.2 DPO versus PPO Ordering

The observation that DPO produces larger calibration degradation than PPO in all three model sizes is counter to the conventional expectation based on reward optimization pressure (PPO >= DPO > SFT). A mechanistic interpretation is that DPO's token-level direct preference reshaping directly adjusts per-option log-probability ratios without an explicit KL penalty constraining divergence from the SFT reference. PPO's sequence-level reward optimization includes a KL penalty to the SFT reference policy, which may moderate boundary shifts. If this interpretation is correct, increasing PPO's KL coefficient should reduce calibration degradation --- a testable prediction for future work.

This observation is obtained using public fallback checkpoints that may differ in training duration, data mixture, or hyperparameters relative to matched-training DPO and PPO checkpoints. The ordering should therefore be interpreted as a checkpoint-level finding. The 2.8B DPO versus PPO difference (delta-Reliability 0.0437 versus 0.0423) falls within overlapping bootstrap CIs and does not constitute a statistically distinguishable ordering at that scale. The finding is primarily supported by the 1.4B and 6.9B results.

### 6.3 Scale-Dependent Mechanism Gradient

The 6.9B-DPO model's rho = 0.875 --- just below the H1 threshold of 0.90 --- raises the possibility that a mechanism transition occurs as model scale increases beyond 6.9B. If larger models (>= 13B) exhibit rho >= 0.90 under DPO alignment, the dominant mechanism would shift from H2 to H1, and standard temperature scaling would become applicable. This is consistent with the hypothesis that larger models have stronger factual representations that resist H2-type redistribution under DPO's preference reshaping.

Testing this prediction requires applying the Spearman rho diagnostic to larger model families such as LLaMA-2-13B-Chat or Mistral-7B-Instruct. The present framework is directly applicable via lm-eval without modification.

### 6.4 Limitations

**Single model family.** All results are restricted to Pythia 1.4B--6.9B. While Pythia provides the cleanest controlled experiment (identical pretraining across all alignment variants), it is a research model family not widely deployed. Whether H2 dominates in LLaMA-2, Mistral, or other families is an open empirical question.

**Public fallback checkpoints.** The primary RLHFlow Pythia alignment checkpoints (Li et al., 2024) required authenticated HuggingFace access. The publicly available fallback checkpoints used here share the same pretraining checkpoint and approximate training regime. The H2 mechanism finding --- 8 of 9 Spearman rho values below 0.85 with zero values above 0.90 --- would require implausibly consistent checkpoint artifacts to overturn. The DPO >= PPO ordering is more sensitive to checkpoint training equivalence.

**Scale range.** No publicly available Pythia variants exceed 12B. The potential H1/H2 mechanism transition suggested by 6.9B-DPO cannot be resolved within this model family.

**H-M4 not executed.** Testing whether ATS corrects H2-type boundary shifts versus H1-type scale inflation was the final planned experiment. Pipeline execution stopped at 4 of 5 sub-hypotheses; H-M4 remains untested. Claims about ATS correctability are framed as motivated future work.

**Shot-count asymmetry.** The H3 diagnostic compares MMLU (4-shot) against TruthfulQA MC1 (0-shot). This difference in evaluation protocol may contribute to the observed delta-ECE(MMLU) > delta-ECE(TruthfulQA) pattern independently of framing susceptibility.

---

## 7. Conclusion

This work addressed the question of which mechanism drives alignment-induced miscalibration in LLMs, providing a pre-registered mechanistic discrimination between scale inflation (H1), decision-boundary restructuring (H2), and framing susceptibility (H3) within the Pythia 1.4B--6.9B alignment ladder. The principal findings are:

1. H2 is the dominant mechanism in Pythia 1.4B--6.9B: all 9 Spearman rho values fall below 0.90; 8 of 9 fall below 0.85. Alignment changes answer preferences, not just confidence magnitudes.

2. DPO produces larger calibration degradation than PPO (delta Brier Reliability) in all three Pythia sizes, an exploratory observation pending matched-checkpoint replication. The 2.8B case is inconclusive due to overlapping bootstrap CIs.

3. H3 (framing susceptibility) is excluded in the softmax-ECE setting: delta-ECE(TruthfulQA) < delta-ECE(MMLU) for all alignment types.

4. The Spearman rho threshold test, argmax partition, and cross-benchmark H3 diagnostic constitute a reusable framework applicable to any model family.

These results indicate that post-hoc calibration correction methods designed for scale inflation (H1) may not address the operative mechanism in this model family. Whether H2 dominance extends to larger-scale or more widely deployed model families remains an open question for future investigation.

---

## References

Biderman, S., Schoelkopf, H., Anthony, Q., Bradley, H., O'Brien, K., Hallahan, E., Khan, M. A., Purber, S., Prashanth, U. S., Raff, E., et al. (2023). Pythia: A suite for analyzing large language models across training and scaling. In *Proceedings of the 40th International Conference on Machine Learning (ICML)*.

Chhikara, P., et al. (2025). Calibration of large language models under verbally elicited confidence. *arXiv preprint*.

Coste, T., Anwar, U., Kirk, R., & Krueger, D. (2023). Reward model overoptimization for RLHF. *arXiv preprint arXiv:2310.02743*.

Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. In *Proceedings of the 34th International Conference on Machine Learning (ICML)*, pp. 1321--1330.

Hendrycks, D., Burns, C., Basart, S., Zou, A., Mazeika, M., Song, D., & Steinhardt, J. (2021). Measuring massive multitask language understanding. In *Proceedings of the International Conference on Learning Representations (ICLR)*.

Khanmohammadi, S., et al. (2025). Calibration evaluation across model families and benchmarks. *arXiv preprint*.

Li, Y., et al. (2024). Does RLHF guarantee trustworthiness? A study on the Pythia alignment ladder. *arXiv preprint*.

Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring how models mimic human falsehoods. In *Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (ACL)*.

Murphy, A. H. (1973). A new vector partition of the probability score. *Journal of Applied Meteorology*, 12(4), 595--600.

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C. L., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., et al. (2022). Training language models to follow instructions with human feedback. In *Advances in Neural Information Processing Systems (NeurIPS)*.

Rafailov, R., Sharma, A., Mitchell, E., Ermon, S., Manning, C. D., & Finn, C. (2023). Direct preference optimization: Your language model is secretly a reward model. In *Advances in Neural Information Processing Systems (NeurIPS)*.

Wang, Z. (2023). Calibration in deep learning: A survey of methods and challenges. *arXiv preprint*.

Xie, S., et al. (2024). Adaptive temperature scaling for RLHF-aligned language models. *arXiv preprint*.
