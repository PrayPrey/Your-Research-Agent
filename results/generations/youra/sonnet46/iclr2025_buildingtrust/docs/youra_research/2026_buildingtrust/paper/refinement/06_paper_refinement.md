# Mechanistic Discrimination of Alignment-Induced Miscalibration in Language Models

## Abstract

Reinforcement learning from human feedback (RLHF) alignment is known to degrade the calibration of large language models, yet the underlying mechanism remains unresolved. This study presents a pre-registered mechanistic discrimination among three candidate hypotheses: monotonic scale inflation (H1), decision-boundary restructuring (H2), and framing susceptibility (H3). Experiments were conducted on the Pythia alignment ladder (1.4B, 2.8B, and 6.9B parameters) with SFT, DPO, and PPO variants, evaluated on MMLU (14,042 items) and TruthfulQA MC1 (817 items) using lm-eval-harness v0.4.11. The principal finding is that H1 is not supported within this model family: all nine Spearman rank correlations between base and aligned log-probability distributions fall below the pre-registered H1 threshold of rho >= 0.90, and eight of nine fall below 0.85. Under PPO alignment at 1.4B parameters, rho = -0.324 and 99.7% of MMLU items receive a different top-ranked answer after alignment. H3 is not supported in the softmax-ECE evaluation setting, as MMLU calibration degradation exceeds TruthfulQA calibration degradation for all alignment types. These results are consistent with H2 (decision-boundary restructuring) as the dominant mechanism within the Pythia 1.4B-6.9B family. An exploratory observation indicates that DPO produces larger calibration degradation than PPO across all three model sizes, contrary to the pre-registered ordering prediction; this finding is based on public fallback checkpoints and requires replication with matched-training checkpoints. One planned sub-hypothesis (H-M4, testing ATS correction effectiveness) was not executed.

## 1. Introduction

Calibration -- the correspondence between a model's expressed confidence and its empirical accuracy -- is a central dimension of language model trustworthiness. Well-calibrated models provide uncertainty signals that can inform downstream decision-making: high confidence should correlate with high accuracy. Guo et al. (2017) established that modern neural networks tend to exhibit systematic overconfidence after training, and subsequent work has confirmed that RLHF alignment substantially amplifies this effect. Xie et al. (2024) reported that LLaMA-2-Chat achieves ECE values of 0.298 on MMLU and 0.507 on TruthfulQA, substantially exceeding its base model counterparts.

While the existence of alignment-induced miscalibration is well-documented, the mechanistic cause remains unresolved. Three distinct hypotheses have been proposed in the literature, each with different implications for corrective interventions:

**H1 (Scale Inflation).** Alignment amplifies confidence in the model's existing answer preferences without reordering them. Under H1, the Spearman rank correlation between base and aligned log-probability vectors should remain high (rho >= 0.90), and temperature scaling is expected to be an effective correction.

**H2 (Decision-Boundary Restructuring).** Alignment fundamentally changes which answer option the model selects, redistributing probability mass across options rather than merely inflating confidence margins. Under H2, Spearman rho should fall below 0.85, and temperature scaling may be insufficient because the underlying answer distribution has changed.

**H3 (Framing Susceptibility).** Alignment makes confidence allocation sensitive to question framing, producing larger miscalibration on tasks with adversarially designed alternatives. Under H3, calibration degradation on TruthfulQA (which contains plausible-but-false alternatives) should equal or exceed degradation on MMLU.

Prior work has not discriminated among these mechanisms. Xie et al. (2024) proposed Adaptive Temperature Scaling (ATS) as a correction but did not test whether the underlying mechanism is H1, H2, or H3. Li et al. (2024) used the Pythia alignment ladder to study RLHF effects on trustworthiness dimensions including toxicity and bias, but did not measure calibration. No study has conducted a pre-registered, multi-model mechanistic discrimination experiment for alignment-induced miscalibration.

This study addresses that gap using the Pythia model family (1.4B, 2.8B, 6.9B) with SFT, DPO, and PPO alignment variants -- a controlled setting where all variants share identical pretraining data and architecture. The contributions are as follows:

1. A mechanistic discrimination result: within the Pythia 1.4B-6.9B family, the data are consistent with H2 (decision-boundary restructuring) rather than H1 (scale inflation). All nine alignment-size pairs fall below the H1 threshold; eight of nine fall below the H2 diagnostic threshold.

2. An exploratory ordering observation: DPO produces larger calibration degradation than PPO in all three Pythia sizes, contrary to the pre-registered prediction. This observation is based on public fallback checkpoints and should be treated as preliminary.

3. H3 exclusion in the softmax-ECE setting: framing susceptibility is not supported as a primary driver, as MMLU calibration degradation exceeds TruthfulQA degradation for all alignment types.

4. A reusable pre-registered methodology (Spearman rho thresholds, argmax partition, cross-benchmark diagnostic) applicable to any model family.

## 2. Related Work

### 2.1 Calibration in Neural Networks and Language Models

Guo et al. (2017) demonstrated that modern neural networks trained with batch normalization and regularization exhibit systematic overconfidence, and proposed temperature scaling as a post-hoc correction. Their Expected Calibration Error (ECE) framework has become the standard evaluation metric for calibration research. Wang (2023) surveyed calibration methods in deep learning and noted that fine-tuning of pre-trained models introduces calibration degradation, an observation that motivates studying the alignment-calibration relationship. Khanmohammadi et al. (2025) confirmed that ECE varies across model families and benchmarks, supporting the use of MMLU-based calibration evaluation.

None of this prior work distinguishes between mechanistically different sources of miscalibration. A correction appropriate for scale inflation (H1) may be ineffective for boundary restructuring (H2).

### 2.2 RLHF Alignment and Calibration Degradation

Xie et al. (2024) demonstrated that RLHF alignment causes significant calibration degradation in LLaMA-2-Chat and proposed Adaptive Temperature Scaling (ATS), which learns an input-dependent temperature from hidden states and achieves 58-82% ECE reduction. ATS implicitly assumes an H1-type pattern correctable by rescaling. The present study tests this assumption directly.

Li et al. (2024) used the Pythia alignment ladder (SFT/DPO/PPO variants) to study RLHF effects on trustworthiness, finding that more alignment does not guarantee more trust, with approximately 25% truthfulness degradation relative to SFT on benchmark suites. However, Li et al. did not measure ECE or Brier calibration. The present study extends their causal design to the calibration dimension.

Coste et al. (2023) studied reward overoptimization, establishing a theoretical mechanism by which reward optimization inflates model confidence. Their analysis predicts confidence inflation on existing choices (consistent with H1), but the present data show near-complete answer redistribution (consistent with H2).

The RLHF framework was established by Ouyang et al. (2022), and DPO by Rafailov et al. (2023). The Pythia model family (Biderman et al., 2023) provides the only publicly available full alignment ladder sharing identical pretraining data and architecture.

### 2.3 Verbal Confidence and Framing Effects

Chhikara et al. (2025) studied calibration using verbally elicited confidence (0-100 scale) and found that distractors can reduce ECE by up to 90% in some models. Their findings use a different measurement modality (verbal confidence) than the present study (log-probability softmax ECE). The H3 diagnostic employed here tests whether softmax-based calibration degradation exhibits framing sensitivity within the Pythia family.

## 3. Method

### 3.1 Pre-Registered Mechanism Discrimination Framework

Three mechanistic hypotheses were formalized before experiments were conducted:

- **H1 (Monotonic Scale Inflation):** Spearman rank correlation (rho) between base and aligned 4-option log-probability vectors >= 0.90 across MMLU items.
- **H2 (Decision-Boundary Restructuring):** rho < 0.85 for at least one alignment type, with substantial argmax redistribution.
- **H3 (Framing Susceptibility):** ΔECE on TruthfulQA >= ΔECE on MMLU.

Pre-specified falsifiers:
- H1 is falsified if rho < 0.80 for PPO alignments.
- H2 is indicated as dominant if rho < 0.85 for the majority of alignment-size pairs.
- H3 is falsified if ΔECE_TruthfulQA < ΔECE_MMLU for all alignment types.

### 3.2 Model Family

The Pythia alignment ladder was used: base models EleutherAI/pythia-{1.4b, 2.8b, 6.9b} with corresponding SFT, DPO, and PPO variants. This family provides identical pretraining data, architecture, and tokenizer across all alignment variants, enabling causal attribution of calibration differences to the alignment procedure.

The primary aligned checkpoints (RLHFlow variants from Li et al., 2024) required authenticated HuggingFace access. Publicly available fallback checkpoints were used instead: lomahony/pythia-{size}-helpful-sft (SFT), Leogrin/eleuther-pythia{size}-hh-dpo (DPO), and usvsnsp/pythia-{size}-ppo (PPO). These share the same base model and approximate training regime. The H2 mechanism finding (Spearman rho) is expected to be robust to this substitution, while the DPO vs. PPO ordering should be interpreted as a checkpoint-level observation pending replication with matched checkpoints.

This yields 12 models: 3 base models and 9 aligned variants (3 alignment methods x 3 sizes).

### 3.3 Evaluation Protocol

All models were evaluated using lm-eval-harness v0.4.11 with identical settings:
- **MMLU** (cais/mmlu, full test set, 14,042 items, 57 subjects, 4-shot)
- **TruthfulQA MC1** (817 items, 0-shot) -- used exclusively for the H3 diagnostic
- Greedy decoding, temperature = 1.0
- Log-probability continuation scoring (not chat-template)

The log-probability continuation format was applied identically to all 12 models, including chat-tuned variants, to avoid format-confound artifacts.

### 3.4 Calibration Measurement

From lm-eval log_samples output, 4-option log-probability vectors were extracted for each MMLU item and each model. The following metrics were computed:

**ECE (15-bin equal-width):** Standard Expected Calibration Error following Guo et al. (2017).

**Brier Score Decomposition (Murphy, 1973):**
- Reliability: the overconfidence term. Higher values indicate greater overconfidence.
- Resolution: discriminability. Higher values indicate better calibration.
- Uncertainty: data difficulty, constant across models.

The primary metric is ΔBrier Reliability = Reliability_aligned - Reliability_base. ΔECE is reported as a secondary directional check. Bootstrap 95% confidence intervals were computed with n = 1,000 samples and seed = 42.

### 3.5 Mechanism Discrimination Measurements

**H1/H2 discrimination (Spearman rho):** For each MMLU item, the Spearman rank correlation between the base model's 4-option log-probability vector and the aligned model's vector was computed. The mean rho per alignment-size pair (9 pairs) was compared against the H1 threshold (>= 0.90) and H2 diagnostic (< 0.85).

**Argmax partition:** MMLU items were partitioned into shared-argmax (base and aligned agree on top option) and changed-argmax (argmax differs).

**Pre-softmax margin analysis:** Per-item margin = max(log-prob) - second_max(log-prob) before softmax normalization. This tests whether confidence inflation operates at the logit level. The margin analysis and Spearman rho analysis are computed from the same per-item log-probability vectors and are therefore not independent data streams.

**H3 diagnostic:** ΔECE_TruthfulQA and ΔECE_MMLU were compared for each alignment type. A ratio < 1.0 for all alignment types is inconsistent with H3. A methodological caveat applies: MMLU uses 4-shot evaluation while TruthfulQA MC1 uses 0-shot, which may contribute to the observed pattern independently of framing susceptibility.

### 3.6 Hypothesis-Gate Structure

Experiments were structured as a causal chain with explicit gate conditions:

| Hypothesis | Gate Type | Criterion | Result |
|------------|-----------|-----------|--------|
| H-E1 (Existence) | MUST_WORK | ΔReliability > 0 with CI lower > 0 for PPO or DPO in >= 2/3 sizes | PASS |
| H-M1 (Baseline) | MUST_WORK | ECE_base < 0.15 for all 3 sizes | PASS |
| H-M2 (Margins) | SHOULD_WORK | Δmargin_PPO > 0 with CI lower > 0 in >= 2/3 sizes | PASS |
| H-M3 (Mechanism) | SHOULD_WORK | Spearman rho >= 0.90 for all 9 pairs (H1 confirmation) | FAIL |
| H-M4 (ATS correction) | SHOULD_WORK | Not executed | N/A |

The H-M3 gate was designed so that failure constitutes a scientifically informative negative result (H2 dominance) rather than an experiment failure.

## 4. Experimental Setup

### 4.1 Models

| Model Size | Base | SFT | DPO | PPO |
|------------|------|-----|-----|-----|
| 1.4B | EleutherAI/pythia-1.4b | lomahony/pythia-1.4b-helpful-sft | Leogrin/eleuther-pythia1.4b-hh-dpo | usvsnsp/pythia-1.4b-ppo |
| 2.8B | EleutherAI/pythia-2.8b | lomahony/pythia-2.8b-helpful-sft | Leogrin/eleuther-pythia2.8b-hh-dpo | usvsnsp/pythia-2.8b-ppo |
| 6.9B | EleutherAI/pythia-6.9b | lomahony/pythia-6.9b-helpful-sft | Leogrin/eleuther-pythia6.9b-hh-dpo | usvsnsp/pythia-6.9b-ppo |

All aligned variants share the Pythia pretraining checkpoint. Public fallback checkpoints (trained on Anthropic HH preference data) were used in place of the primary RLHFlow checkpoints.

### 4.2 Datasets

**MMLU (Hendrycks et al., 2021):** 14,042 multiple-choice questions across 57 subjects. The 4-option forced-choice format provides a 4-dimensional probability vector for Spearman rho analysis. Evaluated with 4-shot prompting.

**TruthfulQA MC1 (Lin et al., 2022):** 817 questions with adversarially crafted plausible-but-false alternatives. Used exclusively as the H3 framing susceptibility diagnostic (0-shot).

### 4.3 Metrics

- **Primary:** ΔBrier Reliability (aligned minus base)
- **Secondary:** ΔECE (15-bin equal-width), Spearman rho (per-item, per pair), Δmargin (pre-softmax), argmax redistribution rate, ΔECE ratio (TruthfulQA/MMLU)

### 4.4 Implementation

All evaluations used lm-eval-harness v0.4.11 with --log_samples. Calibration analysis was implemented in Python using scipy.stats (Spearman rho), numpy (Brier decomposition, argmax partition), and a 15-bin equal-width ECE implementation following Guo et al. (2017). Bootstrap resampling used seed = 42. Calibration bins span [0, 1] in 15 equal-width intervals, consistent with Xie et al. (2024).

## 5. Results

### 5.1 Alignment Increases Brier Reliability (H-E1)

Eight of nine aligned model-size pairs showed positive ΔBrier Reliability, indicating that alignment training consistently increases overconfidence relative to paired base models on MMLU. The exception was 6.9B-PPO (ΔReliability = -0.0036), which showed a marginal calibration improvement.

**Table 1.** ΔECE and ΔBrier Reliability for all nine alignment-size pairs on MMLU.

| Model | Alignment | ECE_base | ECE_aligned | ΔECE | ΔBrier Reliability | 95% CI Lower |
|-------|-----------|----------|-------------|------|--------------------|-------------|
| Pythia-1.4B | SFT | 0.0849 | 0.1415 | +0.0566 | +0.0289 | +0.0269 |
| Pythia-1.4B | DPO | 0.0849 | 0.2516 | +0.1667 | +0.1048 | +0.1009 |
| Pythia-1.4B | PPO | 0.0849 | 0.1923 | +0.1074 | +0.0406 | +0.0345 |
| Pythia-2.8B | SFT | 0.0597 | 0.0694 | +0.0097 | +0.0033 | +0.0021 |
| Pythia-2.8B | DPO | 0.0597 | 0.1441 | +0.0844 | +0.0437 | +0.0407 |
| Pythia-2.8B | PPO | 0.0597 | 0.1577 | +0.0980 | +0.0423 | +0.0388 |
| Pythia-6.9B | SFT | 0.0792 | 0.0830 | +0.0038 | +0.0010 | +0.0001 |
| Pythia-6.9B | DPO | 0.0792 | 0.1010 | +0.0218 | +0.0099 | +0.0090 |
| Pythia-6.9B | PPO | 0.0792 | 0.0609 | -0.0183 | -0.0036 | -0.0053 |

The H-E1 MUST_WORK gate (bootstrap CI lower > 0 for PPO or DPO in >= 2/3 sizes) was satisfied via both DPO (3/3 sizes) and PPO (2/3 sizes).

**Causal baseline confirmation (H-M1):** Base Pythia models showed ECE = 0.0849 (1.4B), 0.0597 (2.8B), 0.0792 (6.9B), all below the 0.15 threshold (MUST_WORK PASS). Pretraining yielded well-calibrated logits; the observed increases are attributable to alignment.

![Figure 1: ΔBrier Reliability across all alignment-size pairs](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/delta_reliability_bar.png)

*Figure 1. ΔBrier Reliability (aligned minus base) for all nine alignment-size pairs on MMLU. Error bars show bootstrap 95% confidence intervals (n = 1,000). Positive values indicate increased overconfidence.*

![Figure 2: Brier score decomposition](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/brier_decomposition.png)

*Figure 2. Brier score decomposition (Reliability, Resolution, Uncertainty) for all 12 models. Reliability increases under alignment while Resolution changes are moderate, indicating that overconfidence rather than discriminability collapse is the primary calibration change.*

### 5.2 Exploratory Ordering: DPO >= PPO > SFT (H-M2)

The pre-registered calibration ordering prediction (PPO >= DPO > SFT, based on conventional reward optimization pressure) was not supported by the data. DPO produced larger calibration degradation than PPO in all three model sizes as measured by ΔBrier Reliability, yielding an observed ordering of DPO >= PPO > SFT.

Pre-softmax logit margin analysis confirmed that confidence inflation operates at the logit level, not as a softmax normalization artifact. DPO showed positive Δmargin in all three sizes; PPO in two of three sizes (6.9B-PPO showed Δmargin = -0.036).

![Figure 3: Pre-softmax margin inflation](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/figure_01_delta_margin_gate.png)

*Figure 3. Pre-softmax logit margin inflation (Δmargin = margin_aligned - margin_base) with bootstrap 95% confidence intervals. DPO shows positive Δmargin in all three sizes; PPO in two of three sizes.*

![Figure 4: Gradient ordering heatmap](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/figure_04_gradient_ordering_heatmap.png)

*Figure 4. Δmargin heatmap by alignment method (rows) and Pythia model size (columns).*

**Statistical qualification.** At 2.8B, the DPO-PPO difference was narrow: ΔRel_DPO = 0.0437 (95% CI: [0.0407, 0.0469]) versus ΔRel_PPO = 0.0423 (95% CI: [0.0388, 0.0456]). These confidence intervals overlap, and the difference of 0.0014 is not statistically distinguishable at the 95% confidence level. The DPO >= PPO ordering is directionally consistent across all three sizes but should be treated as inconclusive at 2.8B. The finding is primarily supported by the clear separation at 1.4B (DPO: 0.1048, PPO: 0.0406) and 6.9B (DPO: +0.0099, PPO: -0.0036).

The margin analysis (H-M2) and Spearman rho analysis (H-M3) are both derived from the same per-item log-probability vectors and should be understood as complementary characterizations of the same logit distribution changes rather than independent confirmatory evidence.

### 5.3 Mechanism Discrimination: H2 Dominance (H-M3)

All nine alignment-size pairs fell below the H1 threshold (rho >= 0.90). Eight of nine fell below the H2 diagnostic threshold (rho < 0.85).

**Table 2.** H1/H2 discrimination summary for all nine alignment-size pairs.

| Pair | Spearman rho | H1 (>= 0.90) | H2 (< 0.85) | Argmax Changed (%) |
|------|-------------|---------------|--------------|-------------------|
| 1.4B-SFT | 0.753 | No | Yes | 42.8% (6,014 / 14,042) |
| 1.4B-DPO | 0.737 | No | Yes | 41.4% (5,807 / 14,042) |
| 1.4B-PPO | -0.324 | No | Yes | 99.7% (13,998 / 14,042) |
| 2.8B-SFT | 0.719 | No | Yes | 28.7% (4,025 / 14,042) |
| 2.8B-DPO | 0.590 | No | Yes | 39.4% (5,526 / 14,042) |
| 2.8B-PPO | 0.175 | No | Yes | 64.5% (9,049 / 14,042) |
| 6.9B-SFT | 0.839 | No | Yes | 14.8% (2,073 / 14,042) |
| 6.9B-DPO | 0.875 | No | No (near threshold) | 15.8% (2,224 / 14,042) |
| 6.9B-PPO | 0.505 | No | Yes | 39.7% (5,570 / 14,042) |

The 1.4B-PPO case is particularly notable: rho = -0.324 indicates that the aligned model's answer preferences are negatively correlated with the base model's. Only 44 of 14,042 MMLU items (0.3%) maintain the same top-ranked answer option after PPO alignment at 1.4B. The 6.9B-DPO model showed the highest rho (0.875), the closest to the H1 threshold, suggesting a possible scale-mediated effect.

![Figure 5: Spearman rho per alignment-size pair](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/figure_01_spearman_rho.png)

*Figure 5. Spearman rank correlation (rho) between base and aligned 4-option log-probability vectors per MMLU item. Dashed lines at rho = 0.90 (H1 threshold) and rho = 0.85 (H2 diagnostic). All nine pairs fall below 0.90; eight of nine fall below 0.85.*

![Figure 6: Argmax redistribution rates](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/figure_04_argmax_proportion.png)

*Figure 6. Proportion of MMLU items where alignment changes the argmax prediction. 1.4B-PPO changes argmax for 99.7% of items.*

![Figure 7: Brier partition by argmax agreement](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/figure_03_brier_partition.png)

*Figure 7. Brier reliability partitioned into shared-argmax and changed-argmax items. For 1.4B-PPO, the shared-argmax partition contains only 44 items.*

### 5.4 H3 Exclusion in Softmax-ECE Setting

ΔECE on TruthfulQA MC1 was less than ΔECE on MMLU for all three alignment types (SFT ratio = 0.32, DPO ratio = 0.26, PPO ratio = 0.73). The H3 hypothesis predicts ratios >= 1.0 if framing susceptibility is the primary driver. The observed ratios are inconsistent with H3 as a dominant mechanism in the softmax-ECE evaluation setting.

This result is distinct from the findings of Chhikara et al. (2025), who observed framing sensitivity using verbally elicited confidence. The measurement modality (softmax log-probability ECE versus verbal confidence) appears to determine whether framing effects are observed. A methodological caveat applies: the shot-count asymmetry between MMLU (4-shot) and TruthfulQA MC1 (0-shot) could contribute to the ΔECE_MMLU > ΔECE_TruthfulQA pattern independently of framing susceptibility, though the magnitude of the ratios (0.26-0.73) suggests framing is unlikely to be the dominant driver even accounting for this difference.

![Figure 8: TruthfulQA H3 diagnostic](/home/anonymous/YouRA_results_new_4/TEST_buildingtrust/docs/youra_research/20260315_buildingtrust/paper/figures/figure_05_truthfulqa_ece.png)

*Figure 8. ΔECE on TruthfulQA MC1 versus MMLU for all alignment types. ΔECE_TruthfulQA < ΔECE_MMLU for all three methods.*

## 6. Discussion

### 6.1 Summary of Findings

Three principal findings emerge from these experiments:

First, within the Pythia 1.4B-6.9B family, alignment-induced miscalibration is consistent with H2 (decision-boundary restructuring) rather than H1 (scale inflation). All nine Spearman rho values fall below the H1 threshold. This implies that post-hoc correction methods designed under an H1 assumption -- including temperature scaling and ATS variants -- may not address the actual mechanism. Temperature scaling adjusts confidence magnitude on a fixed answer distribution; H2 restructuring changes the distribution itself.

Second, DPO produced larger calibration degradation than PPO across all three model sizes. This observation reverses the pre-registered ordering prediction. A possible explanation is that DPO's token-level direct preference reshaping operates more aggressively on answer distributions than PPO's KL-constrained sequence-level optimization. However, this interpretation should be treated as exploratory given that the fallback checkpoints may not be training-equivalent. At 2.8B, the DPO-PPO difference falls within overlapping bootstrap confidence intervals and is not statistically distinguishable.

Third, H3 (framing susceptibility) is not supported in the softmax-ECE evaluation setting. Calibration degradation is domain-general within the Pythia family, not driven by adversarial framing.

### 6.2 Implications for Post-Hoc Calibration Correction

If the dominant miscalibration mechanism is boundary restructuring rather than scale inflation, then corrections that merely rescale confidence on the aligned model's preferred answers may be insufficient. Under 1.4B-PPO, 99.7% of MMLU items have a different top-ranked option after alignment. Rescaling confidence on these new preferences does not address the underlying problem that the model has learned to prefer different -- and potentially incorrect -- answers.

Xie et al. (2024) reported that ATS reduces LLaMA-2-Chat ECE by 58-82%. If alignment shifts decision boundaries in hidden-state space, ATS may succeed by learning per-input temperature adjustments that partially track boundary redistribution. This interpretation predicts that ATS effectiveness should correlate with the degree of H2 boundary shift. Testing this prediction was planned as H-M4 but was not executed.

### 6.3 Scale Effects

The 6.9B-DPO model's rho = 0.875 -- below but near the H1 threshold of 0.90 -- raises the possibility that the dominant mechanism may shift from H2 toward H1 at larger scales. If models above approximately 13B parameters exhibit rho >= 0.90 under DPO alignment, standard temperature scaling would be expected to become more effective. Testing this hypothesis requires applying the Spearman rho diagnostic to larger model families such as LLaMA-2 or Mistral.

### 6.4 Limitations

**Fallback checkpoints.** Public fallback checkpoints were used instead of the primary RLHFlow Pythia alignment checkpoints. These share the same base model and approximate training regime, but training equivalence is not guaranteed. The H2 mechanism finding (8/9 Spearman rho values below 0.85 with zero above 0.90) would require implausibly consistent checkpoint artifacts to overturn. The DPO >= PPO ordering, however, is more sensitive to checkpoint training differences and should be interpreted with caution.

**Single model family.** All results are restricted to Pythia 1.4B-6.9B. This family provides the cleanest controlled experiment but is a research model family not widely deployed in production. Whether H2 dominates in LLaMA-2, Mistral, or other families is an open empirical question.

**Scale range.** The scale range of 1.4B-6.9B is limited. No publicly available Pythia variants exceed 12B parameters, preventing resolution of the potential H1/H2 mechanism transition suggested by the 6.9B-DPO result.

**H-M4 not executed.** The planned experiment testing whether ATS corrects H2-type boundary shifts was not conducted. The claim about ATS correctability is therefore framed as motivated future work rather than an empirical finding.

**Shot-count asymmetry.** The H3 diagnostic compares 4-shot MMLU with 0-shot TruthfulQA. If few-shot prompting amplifies MMLU calibration degradation relative to 0-shot, this could contribute to the observed ΔECE_MMLU > ΔECE_TruthfulQA pattern independently of framing susceptibility.

### 6.5 Broader Impact

If RLHF-aligned models are miscalibrated via boundary restructuring rather than confidence inflation, standard reliability checks that probe whether a model's confidence on its predicted class is accurate may not capture the actual problem: that the predicted class itself has changed systematically. Alignment-induced answer restructuring may be more consequential than overconfidence on stable predictions, as it implies the model has learned different answer preferences across a wide range of inputs.

## 7. Conclusion

This study addressed the question of which mechanism drives alignment-induced miscalibration in language models, providing the first pre-registered mechanistic discrimination among scale inflation (H1), decision-boundary restructuring (H2), and framing susceptibility (H3). The main findings, restricted to the Pythia 1.4B-6.9B family, are:

1. **H2 is the dominant mechanism:** All nine Spearman rho values fall below the H1 threshold of 0.90; eight of nine fall below 0.85. Alignment changes answer preferences rather than merely amplifying confidence magnitudes.

2. **DPO >= PPO > SFT ordering (exploratory):** DPO produces larger calibration degradation than PPO in all three sizes, reversing the pre-registered prediction. The 2.8B case is inconclusive due to overlapping confidence intervals. This finding is based on public fallback checkpoints and requires matched-checkpoint replication.

3. **H3 is not supported in softmax-ECE:** ΔECE_TruthfulQA < ΔECE_MMLU for all alignment types, indicating domain-general miscalibration in this evaluation framework.

4. **Reusable framework:** The Spearman rho threshold test, argmax partition, and cross-benchmark diagnostic are applicable to any model family via lm-eval without modification.

Three categories of follow-up work are motivated by these results: (a) matched-training DPO versus PPO experiments to verify the ordering observation; (b) testing whether ATS effectiveness correlates with the degree of H2 boundary shift (H-M4); and (c) applying the discrimination framework to larger and more widely deployed model families to determine whether H2 dominance persists at production scale.

## References

- Biderman, S., et al. (2023). Pythia: A Suite for Analyzing Large Language Models Across Training and Scaling. *ICML 2023*. arXiv:2304.01373.
- Brier, G. W. (1950). Verification of Forecasts Expressed in Terms of Probability. *Monthly Weather Review*, 78(1), 1-3.
- Chhikara, P. (2025). Mind the Confidence Gap: Overconfidence, Calibration, and Distractor Effects in Large Language Models. arXiv:2502.11028.
- Coste, T., Anwar, U., Kirk, R., & Krueger, D. (2023). Reward Model Ensembles Help Mitigate Overoptimization. *ICLR 2024*. arXiv:2310.02743.
- Gao, L., et al. (2021). Language Model Evaluation Harness. https://github.com/EleutherAI/lm-evaluation-harness. v0.4.11.
- Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On Calibration of Modern Neural Networks. *ICML 2017*, 1321-1330. arXiv:1706.04599.
- Hendrycks, D., et al. (2021). Measuring Massive Multitask Language Understanding. *ICLR 2021*. arXiv:2009.03300.
- Khanmohammadi, A., et al. (2025). Calibrating LLM Confidence by Probing Perturbed Representation Stability. arXiv:2505.21772.
- Li, X., Krishna, K., & Lakkaraju, H. (2024). More RLHF, More Trust? On The Impact of Preference Alignment On Trustworthiness. *ICLR 2025*. arXiv:2404.18870.
- Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring How Models Mimic Human Falsehoods. *ACL 2022*. arXiv:2109.07958.
- Murphy, A. H. (1973). A New Vector Partition of the Probability Score. *Journal of Applied Meteorology*, 12(4), 595-600.
- Ouyang, L., et al. (2022). Training Language Models to Follow Instructions with Human Feedback. *NeurIPS 2022*. arXiv:2203.02155.
- Rafailov, R., et al. (2023). Direct Preference Optimization: Your Language Model is Secretly a Reward Model. *NeurIPS 2023*. arXiv:2305.18290.
- Wang, L. (2023). Calibration in Deep Learning: A Survey of Methods. arXiv:2308.01222.
- Xie, J., Su, A., Bhatt, S., & Hashimoto, T. (2024). Calibrating Language Models with Adaptive Temperature Scaling. *EMNLP 2024*. arXiv:2409.19817.
