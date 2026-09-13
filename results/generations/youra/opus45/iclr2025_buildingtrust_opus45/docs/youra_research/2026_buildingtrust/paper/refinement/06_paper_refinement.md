# Discriminative Degradation of Confidence Signals in RLHF-Tuned Language Models

## Abstract

This study investigates whether Reinforcement Learning from Human Feedback (RLHF) instruction tuning degrades the discriminative quality of confidence signals in large language models. We operationalize confidence as logit margin and measure discriminative ability using AUROC for margin-based correctness prediction. Across two model families (Qwen2.5-7B and Mistral-7B), we observe that instruction-tuned models exhibit lower AUROC than their base counterparts: Qwen shows a decrease of 0.0222 (95% CI: [0.0074, 0.0370]) and Mistral shows a decrease of 0.0385 (95% CI: [0.0238, 0.0531]). We identify the mechanism as disproportionate margin inflation for incorrect predictions, with instruction-tuned models showing 3.06x (Qwen) and 16.79x (Mistral) higher expected margins conditional on incorrect answers compared to base models. Percentile-normalized logistic regression reveals slope attenuation of 34% (Qwen) and 40% (Mistral), indicating that the distortion persists after controlling for scale differences. Murphy's Brier score decomposition shows that the refinement component (discrimination) decreases in instruction-tuned models while uncertainty remains stable, consistent with geometric rather than scalar distortion. These findings suggest that RLHF may introduce a tradeoff between behavioral alignment and confidence signal reliability that standard post-hoc calibration methods targeting Expected Calibration Error may not fully address.

## 1. Introduction

Language models deployed in applications requiring reliable uncertainty estimates must produce confidence scores that discriminate between correct and incorrect predictions. Prior work has documented that RLHF-tuned models exhibit systematic overconfidence compared to base models (Tian et al., 2023), and post-hoc temperature scaling has been shown to reduce Expected Calibration Error (ECE) in neural networks (Guo et al., 2017). Recent methods such as DACA (Luo et al., 2025) and CCPS (Khanmohammadi et al., 2025) report ECE improvements of 15-55% on large language models.

However, ECE measures whether predicted probabilities match observed frequencies, not whether confidence scores effectively rank predictions by correctness probability. A model can achieve low ECE through probability rescaling while having degraded ability to distinguish correct from incorrect predictions. This distinction motivates examining whether RLHF affects the discriminative quality of confidence signals, measured by AUROC rather than calibration metrics alone.

This work tests the hypothesis that RLHF instruction tuning degrades discriminative confidence quality through a mechanism distinct from scalar miscalibration. Specifically, we hypothesize that preference optimization inflates logit margins including for incorrect predictions, fundamentally reshaping the confidence-correctness relationship rather than merely shifting its scale.

We make four contributions:

1. We measure discriminative degradation using AUROC for margin-based correctness prediction across two model families (Qwen and Mistral), finding consistent decreases of 2-4 percentage points in instruction-tuned models.

2. We identify the mechanism as disproportionate margin inflation for incorrect predictions, with inflation ratios of 3-17x depending on model family.

3. We use percentile-normalized logistic regression to separate scale effects from shape effects, finding that slope attenuation persists after normalization.

4. We apply Murphy's Brier score decomposition to characterize the distortion type, finding refinement degradation consistent with geometric rather than scalar distortion.

## 2. Related Work

### 2.1 Neural Network Calibration

Guo et al. (2017) demonstrated that modern neural networks are often miscalibrated and introduced temperature scaling as a simple post-hoc correction that reduces ECE. This work has been highly influential (7,452 citations as of the search date) and established temperature scaling as a standard baseline for calibration methods.

Recent work has extended calibration methods to large language models. DACA (Luo et al., 2025) uses disagreement between pre-trained and post-trained language models to detect samples requiring calibration, reporting 15% ECE improvement on Llama-3. CCPS (Khanmohammadi et al., 2025) uses consistency under perturbation as a calibration signal, reporting 55% ECE reduction on MMLU. These methods focus on ECE as the primary metric and do not directly measure discriminative quality.

### 2.2 RLHF and Overconfidence

Tian et al. (2023) documented that RLHF-tuned models exhibit systematic overconfidence and found that verbalized confidence often outperforms token-level probabilities for such models. This suggests that RLHF training affects how models express uncertainty at the probability level.

The Bradley-Terry preference model underlying RLHF training rewards responses preferred by human annotators. To the extent that annotators prefer confident-sounding responses, this creates selection pressure toward higher confidence regardless of correctness.

### 2.3 Brier Score Decomposition

Murphy (1973) introduced a decomposition of the Brier score into reliability, resolution (refinement), and uncertainty components. This framework separates calibration error (reliability) from discriminative ability (refinement), enabling characterization of whether miscalibration is primarily a scale effect or a shape effect.

## 3. Method

### 3.1 Confidence Operationalization

We operationalize model confidence using the logit margin:

$$\text{margin} = \text{logit}_{(1)} - \text{logit}_{(2)}$$

where $\text{logit}_{(1)}$ and $\text{logit}_{(2)}$ are the highest and second-highest logits among answer options. This operationalization is standard for multiple-choice tasks where probability mass concentrates on answer tokens.

### 3.2 Discriminative Degradation (H-E1)

We compute AUROC for the binary classification task of predicting correctness from margin:

$$\text{AUROC} = P(\text{margin}_{\text{correct}} > \text{margin}_{\text{incorrect}})$$

This measures how well margin values rank predictions by correctness probability, independent of calibration. We compute bootstrap confidence intervals (n=1,000) for AUROC differences between base and instruction-tuned models.

### 3.3 Conditional Margin Analysis (H-M1)

We analyze conditional margin distributions separately for correct and incorrect predictions:

$$E[\text{margin} | \text{incorrect}]_{\text{instruct}} \quad \text{vs.} \quad E[\text{margin} | \text{incorrect}]_{\text{base}}$$

If instruction tuning inflates margins disproportionately for incorrect predictions, this would explain AUROC degradation. We use permutation tests (n=9,999) to assess statistical significance and compute Cohen's d for effect size.

### 3.4 Percentile-Normalized Monotonicity (H-M2)

To separate scale effects from shape effects, we apply percentile normalization:

1. Transform margins to percentile ranks within each model
2. Convert to z-scores using the inverse normal CDF
3. Fit logistic regression: $P(\text{correct}) = \sigma(\alpha + \beta \cdot z(\text{margin}))$
4. Compare $\beta_{\text{base}}$ vs. $\beta_{\text{instruct}}$

If $\beta_{\text{instruct}} < \beta_{\text{base}}$ after normalization, the confidence-correctness relationship is attenuated in shape, not merely scale. We use paired bootstrap (n=1,000) to compute confidence intervals for the slope difference.

### 3.5 Brier Score Decomposition (H-M3)

We apply Murphy's (1973) decomposition:

$$\text{Brier} = \text{Reliability} - \text{Refinement} + \text{Uncertainty}$$

where Reliability measures calibration error, Refinement measures discrimination, and Uncertainty measures base rate entropy. If RLHF causes geometric distortion (affecting shape), Refinement should decrease. If RLHF causes scalar distortion (temperature-like), Reliability should change while Refinement remains stable.

## 4. Experimental Setup

### 4.1 Models

We evaluate instruction-tuned models and their base counterparts from two families:

- **Qwen:** Qwen2.5-7B (base) vs. Qwen2.5-7B-Instruct
- **Mistral:** Mistral-7B-v0.1 (base) vs. Mistral-7B-Instruct-v0.2

The Llama-2-7B family was planned but not tested due to HuggingFace model gating restrictions at experiment time.

### 4.2 Dataset

We use MMLU (Hendrycks et al., 2021) with 14,042 test samples across 57 subjects. This multiple-choice benchmark enables clean extraction of answer-token logits and provides ground-truth correctness labels.

### 4.3 Inference Protocol

All models use greedy decoding (temperature=0) with identical zero-shot prompts. We extract the top-1 and top-2 logits at the answer position for margin computation.

### 4.4 Statistical Methods

- **AUROC comparison:** Bootstrap confidence intervals (n=1,000)
- **Conditional margin tests:** Permutation tests (n=9,999, independent samples)
- **Slope comparison:** Paired bootstrap (n=1,000)
- **Brier decomposition:** Bootstrap confidence intervals (n=1,000) with 15 probability bins

## 5. Results

### 5.1 Discriminative Degradation Exists (H-E1)

Table 1 presents AUROC comparisons between base and instruction-tuned models.

**Table 1: AUROC for Margin-Based Correctness Prediction**

| Family | Base AUROC | Instruct AUROC | Delta | 95% CI |
|--------|------------|----------------|-------|--------|
| Qwen | 0.8298 | 0.8076 | +0.0222 | [0.0074, 0.0370] |
| Mistral | 0.7797 | 0.7413 | +0.0385 | [0.0238, 0.0531] |
| Mean | - | - | +0.0303 | - |

Both model families show statistically significant AUROC decreases in instruction-tuned models, with confidence intervals excluding zero. The mean degradation is 3.03 percentage points.

Additional context: Base model accuracies were 0.7139 (Qwen) and 0.5875 (Mistral); instruction-tuned accuracies were 0.7045 (Qwen) and 0.5772 (Mistral). The AUROC degradation is not explained by accuracy differences, as AUROC measures rank-ordering independent of accuracy level.

### 5.2 Margin Inflation Mechanism (H-M1)

Table 2 presents conditional margin statistics.

**Table 2: Expected Margin Conditional on Correctness**

| Family | E[m\|incorrect]_base | E[m\|incorrect]_inst | Inflation Ratio | Cohen's d | p-value |
|--------|---------------------|---------------------|-----------------|-----------|---------|
| Qwen | 0.9597 | 2.9327 | 3.06x | 1.01 | <0.0001 |
| Mistral | 0.4682 | 7.8606 | 16.79x | 1.85 | <0.0001 |

For context, expected margins conditional on correct predictions also increased: Qwen from 3.6050 (base) to 7.1491 (instruct), and Mistral from 1.6236 (base) to 13.3810 (instruct). However, the inflation is proportionally larger for incorrect predictions, particularly in Mistral where incorrect-margin inflation (16.79x) substantially exceeds correct-margin inflation (~8x).

The large effect sizes (Cohen's d > 1.0) indicate this is not a subtle statistical effect but a substantial behavioral difference.

### 5.3 Percentile-Normalized Slope Attenuation (H-M2)

Table 3 presents logistic regression slopes after percentile normalization.

**Table 3: Percentile-Normalized Beta Coefficients**

| Family | β_base | β_instruct | Delta β | 95% CI | p-value |
|--------|--------|------------|---------|--------|---------|
| Qwen | 2.2222 | 1.4661 | 0.7581 | [0.6626, 0.8563] | <0.0001 |
| Mistral | 1.5579 | 0.9305 | 0.6284 | [0.5570, 0.7005] | <0.0001 |

Slope attenuation persists after removing scale differences through percentile normalization. The slopes decrease by 34% (Qwen) and 40% (Mistral), indicating that the confidence-correctness relationship is weakened in shape, not merely rescaled.

### 5.4 Brier Decomposition Confirms Geometric Distortion (H-M3)

Table 4 presents Brier score decomposition results.

**Table 4: Brier Score Decomposition**

| Family | Component | Base | Instruct | Delta |
|--------|-----------|------|----------|-------|
| Qwen | Brier Score | 0.1647 | 0.2263 | +0.0616 |
| Qwen | Reliability | 0.0173 | 0.0547 | +0.0374 |
| Qwen | Refinement | 0.0559 | 0.0343 | -0.0216 |
| Qwen | Uncertainty | 0.2042 | 0.2082 | +0.0040 |
| Mistral | Brier Score | 0.2023 | 0.3838 | +0.1814 |
| Mistral | Reliability | 0.0185 | 0.1507 | +0.1321 |
| Mistral | Refinement | 0.0580 | 0.0093 | -0.0487 |
| Mistral | Uncertainty | 0.2424 | 0.2440 | +0.0017 |

Refinement (discrimination) decreases substantially in instruction-tuned models: by 0.0216 in Qwen (95% CI: [0.0179, 0.0253]) and 0.0487 in Mistral (95% CI: [0.0453, 0.0522]). Uncertainty remains approximately constant, as expected since it depends only on base rates. Reliability increases (worse calibration) in both families, particularly Mistral.

The refinement degradation is consistent with geometric distortion affecting the shape of the probability landscape, rather than scalar distortion that would primarily affect reliability.

### 5.5 Summary of Hypothesis Tests

**Table 5: Hypothesis Gate Summary**

| Hypothesis | Type | Metric | Result | Gate |
|------------|------|--------|--------|------|
| H-E1 | EXISTENCE | AUROC degradation | +0.0303 mean | PASS |
| H-M1 | MECHANISM | Margin inflation | 9.92x mean | PASS |
| H-M2 | MECHANISM | β attenuation | 0.69 mean | PASS |
| H-M3 | MECHANISM | Refinement delta | -0.035 mean | PASS |

All four sub-hypotheses show results in the predicted direction with statistical significance.

## 6. Discussion

### 6.1 Interpretation of Findings

The results support the hypothesis that RLHF instruction tuning degrades discriminative confidence quality through geometric distortion. The causal chain suggested by the evidence is:

1. RLHF preference optimization rewards confident-sounding responses
2. This inflates logit margins, including for incorrect predictions (H-M1)
3. Margin inflation decouples the confidence-correctness relationship (H-M2)
4. The result is degraded discriminative ability measurable as AUROC decrease (H-E1)
5. Brier decomposition confirms the distortion affects refinement, not just reliability (H-M3)

The finding that distortion is geometric rather than scalar has implications for post-hoc calibration. Temperature scaling is designed to correct scalar miscalibration by adjusting probability magnitudes. If the distortion is geometric—affecting the shape of the confidence-correctness relationship—temperature scaling may improve ECE while leaving discriminative degradation unaddressed.

### 6.2 Cross-Family Consistency

The effect direction is consistent across both tested families (Qwen and Mistral), though effect magnitudes differ. Mistral shows larger margin inflation (16.79x vs. 3.06x) and greater refinement degradation (0.0487 vs. 0.0216). This magnitude asymmetry may reflect differences in RLHF training procedures, preference datasets, or base model characteristics between model developers.

The consistency of effect direction across architecturally distinct model families suggests that the phenomenon may be related to RLHF training procedures rather than vendor-specific implementation details, though this interpretation is limited by the absence of Llama family data.

### 6.3 Limitations

Several limitations constrain the interpretation of these results:

1. **Model family coverage:** The Llama-2-7B family was not tested due to HuggingFace access restrictions. Generalization to a third family remains unconfirmed.

2. **Model scale:** Only 7B-parameter models were evaluated. The effect magnitude may differ at other scales.

3. **Dataset scope:** Only MMLU was used. Generalization to other multiple-choice benchmarks (TruthfulQA, ARC, CommonsenseQA) and to non-multiple-choice tasks is not established.

4. **Prompt format:** Only zero-shot prompting was evaluated. The planned 2x2 design (zero-shot vs. few-shot × base vs. instruct) was simplified to 1x2.

5. **Temperature scaling not tested:** The claim that temperature scaling cannot repair geometric distortion is theoretical, based on the nature of scalar corrections. Direct empirical verification showing that AUROC and refinement remain degraded after optimal temperature scaling would strengthen this interpretation.

6. **Domain-specific calibration:** Predictions P4 and P5 regarding domain-specific calibration variation and domain-conditioned temperature scaling were not tested in this iteration.

7. **Causal claims:** The comparison between base and instruction-tuned models establishes association, not causation. Other differences between model versions beyond RLHF (continued pretraining, supervised fine-tuning) may contribute to the observed effects.

### 6.4 Implications

For practitioners deploying language models in applications requiring reliable confidence estimates (selective prediction, human-AI collaboration, uncertainty-aware decision making), these findings suggest:

1. AUROC for margin-based correctness prediction may be a useful complement to ECE for evaluating confidence reliability.

2. Instruction-tuned models may require different calibration approaches than base models if discriminative quality is important.

3. Monitoring both calibration (ECE, reliability) and discrimination (AUROC, refinement) metrics may provide a more complete picture of confidence signal quality.

## 7. Conclusion

This study provides evidence that RLHF instruction tuning degrades the discriminative quality of confidence signals in large language models. Across two model families (Qwen and Mistral), instruction-tuned models show reduced AUROC for margin-based correctness prediction (mean decrease: 3.03 percentage points), disproportionate margin inflation for incorrect predictions (3-17x), percentile-normalized slope attenuation (34-40%), and Brier refinement degradation (0.02-0.05).

These findings characterize the distortion as geometric rather than scalar: RLHF reshapes the confidence-correctness relationship rather than merely rescaling probabilities. This distinction suggests that post-hoc calibration methods designed for scalar miscalibration may not fully address discriminative degradation in RLHF-tuned models.

Future work should: (1) validate findings across additional model families including Llama, (2) test across model scales beyond 7B parameters, (3) empirically verify whether temperature scaling improves ECE while leaving AUROC degraded, (4) investigate domain-specific calibration patterns, and (5) explore calibration-aware RLHF training procedures that preserve discriminative quality.

## References

Bai, Y., Jones, A., Ndousse, K., Askell, A., Chen, A., DasSarma, N., ... & Kaplan, J. (2022). Training a helpful and harmless assistant with reinforcement learning from human feedback. arXiv preprint arXiv:2204.05862.

DeGroot, M. H., & Fienberg, S. E. (1983). The comparison and evaluation of forecasters. Journal of the Royal Statistical Society: Series D (The Statistician), 32(1-2), 12-22.

Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. In International Conference on Machine Learning (pp. 1321-1330). PMLR. arXiv:1706.04599.

Hendrycks, D., Burns, C., Basart, S., Zou, A., Mazeika, M., Song, D., & Steinhardt, J. (2021). Measuring massive multitask language understanding. In International Conference on Learning Representations.

Khanmohammadi, S., et al. (2025). Calibrating LLM confidence by probing perturbed representation stability. arXiv preprint arXiv:2505.21772.

Luo, Y., et al. (2025). Your pre-trained LLM is secretly an unsupervised confidence calibrator. arXiv preprint arXiv:2505.16690.

Murphy, A. H. (1973). A new vector partition of the probability score. Journal of Applied Meteorology, 12(4), 595-600.

Naeini, M. P., Cooper, G., & Hauskrecht, M. (2015). Obtaining well calibrated probabilities using Bayesian binning. In Proceedings of the AAAI Conference on Artificial Intelligence (Vol. 29, No. 1).

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C., Mishkin, P., ... & Lowe, R. (2022). Training language models to follow instructions with human feedback. Advances in Neural Information Processing Systems, 35, 27730-27744.

Tian, K., Mitchell, E., Yao, H., Manning, C. D., & Finn, C. (2023). Just ask for calibration: Strategies for eliciting calibrated confidence scores from language models fine-tuned with human feedback. arXiv preprint arXiv:2305.14975.
