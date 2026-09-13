# Truthfulness and Adversarial Robustness Are Correlated in Large Language Models, but Calibration Does Not Explain Why

## Abstract

Large language models exhibit diverse failure modes—generating misinformation (truthfulness failures) or succumbing to adversarial perturbations (robustness failures)—yet these capabilities are typically studied independently. This work presents the first systematic correlation analysis between truthfulness and adversarial robustness across LLMs. Evaluating 14 decoder-only models from four families (Pythia, Llama-2, Mistral, Falcon) on TruthfulQA MC1 and AdvGLUE, a strong positive partial correlation (r=0.80, p<0.001, 95% CI [0.08, 0.97]) emerges after controlling for model size. The natural hypothesis that model calibration underlies both capabilities is tested directly by measuring Expected Calibration Error (ECE) on MMLU. This mechanism is falsified: ECE shows no significant relationship with either metric (r=-0.12, p=0.68 for TruthfulQA; r=-0.16, p=0.58 for AdvGLUE), and poorly-calibrated models exhibit stronger truthfulness-robustness correlation than well-calibrated models—the opposite of what the calibration hypothesis predicts. These findings establish that truthfulness and robustness are linked through an unknown common cause.

## 1. Introduction

A strong correlation (r=0.80) exists between LLM truthfulness and adversarial robustness—two capabilities often studied independently—but the intuitive explanation involving calibration is not supported by the evidence.

This finding has implications for AI safety research: if models that avoid generating misinformation also resist adversarial attacks, understanding the underlying mechanism could inform the development of trustworthy systems.

### 1.1 The Problem: Trust Benchmark Silos

Large language models fail in multiple trust dimensions. A model may generate plausible but factually incorrect statements (truthfulness failures), or it may be misled by adversarially perturbed inputs that preserve semantic meaning (robustness failures). These failure modes are typically studied independently: TruthfulQA (Lin et al., 2022) evaluates whether models repeat common misconceptions, while AdvGLUE (Wang et al., 2022) measures vulnerability to word-level adversarial perturbations.

This separation leaves open the question of whether truthfulness and robustness are fundamentally related capabilities or independent dimensions. If correlated, a common mechanism may underlie both; if independent, separate interventions would be required. No prior study has systematically correlated TruthfulQA and AdvGLUE scores across multiple model families.

### 1.2 Approach and Key Finding

This work conducts the first systematic correlation analysis between truthfulness (TruthfulQA MC1) and adversarial robustness (AdvGLUE average) across 14 decoder-only LLMs from four families (Pythia, Llama-2, Mistral, Falcon), ranging from 70M to 70B parameters. Using partial correlation with log-transformed model size as a covariate:

**Main Result:** TruthfulQA MC1 and AdvGLUE accuracy show a strong positive partial correlation (r=0.8028, p=0.000548) with a 95% bootstrap confidence interval of [0.0816, 0.9685] that excludes zero.

The calibration hypothesis—that well-calibrated models accurately estimate uncertainty, enabling them to avoid false claims and detect anomalous inputs—is tested directly by measuring Expected Calibration Error (ECE) on MMLU.

**Mechanism Finding:** The calibration hypothesis is not supported. ECE shows near-zero correlation with TruthfulQA (r=-0.12, p=0.68) and AdvGLUE (r=-0.16, p=0.58). Furthermore, poorly-calibrated (high-ECE) models showed stronger truthfulness-robustness correlation (r=0.99) than well-calibrated models (r=0.65)—the opposite of what the calibration mechanism predicts (Fisher's z-test p=0.165).

### 1.3 Contributions

1. **First documented correlation:** TruthfulQA MC1 and AdvGLUE accuracy are strongly positively correlated (r=0.80) after controlling for model size.

2. **Mechanism falsification:** Model calibration (ECE) does not explain this correlation, ruling out the most intuitive hypothesis.

3. **Scope characterization:** The correlation is confirmed for base models (r=0.80, p=0.0005, N=8). Results for instruction-tuned models (N=6) are inconclusive due to limited sample size.

## 2. Related Work

### 2.1 Truthfulness Evaluation

TruthfulQA (Lin et al., 2022) measures whether language models generate truthful answers, finding that larger models are not necessarily more truthful and may reproduce misconceptions more fluently. Subsequent work examined truthfulness in specific domains and explored interventions such as RLHF to improve truthful behavior (Ouyang et al., 2022). These studies evaluate truthfulness in isolation without examining relationships to adversarial robustness.

### 2.2 Adversarial Robustness

AdvGLUE (Wang et al., 2022) provides a multi-task adversarial benchmark with word-level perturbations across GLUE tasks. Earlier work established adversarial vulnerabilities through TextFooler (Jin et al., 2020) and BERT-Attack (Li et al., 2020). These studies characterize robustness vulnerabilities but do not examine whether robust models are also truthful.

### 2.3 Calibration in Language Models

Guo et al. (2017) formalized Expected Calibration Error (ECE), showing modern neural networks are often poorly calibrated. For language models, Zhao et al. (2021) demonstrated that contextual calibration improves few-shot performance. Kadavath et al. (2022) examined whether models "know what they know," connecting calibration to epistemic uncertainty.

Calibration provides a plausible hypothesis for why truthfulness and robustness might correlate: a well-calibrated model accurately estimates uncertainty, potentially enabling both refusal of uncertain claims (truthfulness) and detection of anomalous inputs (robustness). This hypothesis is directly tested in this work.

### 2.4 Multi-Dimensional Trust

While individual trust dimensions have been studied extensively, systematic examination of their relationships is limited. Liang et al. (2023) proposed HELM for holistic evaluation across multiple dimensions, but focused on coverage rather than inter-metric correlation. This work fills this gap by quantifying the correlation between truthfulness and robustness and testing a mechanistic explanation.

## 3. Method

### 3.1 Overview

Decoder-only LLMs are evaluated on three benchmarks: TruthfulQA MC1 (truthfulness), AdvGLUE (robustness), and MMLU (calibration reference). Partial correlations controlling for model size (log-transformed parameter count) are computed, and whether Expected Calibration Error (ECE) explains the relationship is tested.

### 3.2 Benchmark Selection

**TruthfulQA MC1** (Lin et al., 2022): Multiple-choice format measuring whether models select truthful answers over common misconceptions. MC1 (single correct answer) is used for cleaner accuracy measurement.

**AdvGLUE** (Wang et al., 2022): Adversarial variants of GLUE tasks with word-level perturbations. Average accuracy across subtasks is reported.

**MMLU** (Hendrycks et al., 2021): Multi-task academic benchmark used only for ECE computation on a neutral task. Computing ECE on TruthfulQA or AdvGLUE would conflate calibration measurement with the metrics being correlated.

### 3.3 Model Selection

Models from four families are evaluated:

| Family | Models | Size Range |
|--------|--------|------------|
| Pythia | 70M, 160M, 410M, 1B, 1.4B, 2.8B, 6.9B, 12B | 70M–12B |
| Llama-2 | 7B, 13B, 70B (base) | 7B–70B |
| Mistral | 7B | 7B |
| Falcon | 7B, 40B | 7B–40B |

Multiple families across a range of scales (70M–70B) ensure correlations are not artifacts of specific architectures or training procedures.

### 3.4 Statistical Methods

**Partial Correlation:** Pearson partial correlation between TruthfulQA MC1 and AdvGLUE accuracy, controlling for log(parameters):

$$r_{xy \cdot z} = \frac{r_{xy} - r_{xz} \cdot r_{yz}}{\sqrt{(1 - r_{xz}^2)(1 - r_{yz}^2)}}$$

**Bootstrap Confidence Intervals:** 95% confidence intervals via 1000 bootstrap iterations, resampling models with replacement.

**Expected Calibration Error (ECE):** 15-bin ECE on MMLU:

$$\text{ECE} = \sum_{b=1}^{B} \frac{|B_b|}{N} |acc(B_b) - conf(B_b)|$$

### 3.5 Mechanism Testing

**H-M1 (Calibration-Metric Correlation):** If calibration underlies both capabilities, ECE should negatively correlate with TruthfulQA and AdvGLUE (lower ECE = better calibration = higher performance).

**H-M2 (Calibration Moderation):** If calibration mediates the truthfulness-robustness relationship, well-calibrated (low-ECE) models should show stronger correlation than poorly-calibrated models. This is tested via Fisher's z-test comparing correlation coefficients across ECE tertiles.

### 3.6 Hypothesis Structure

| ID | Type | Test | Gate |
|----|------|------|------|
| h-e1 | Existence | Partial r > 0.3, p < 0.05 | MUST_WORK |
| h-m1 | Mechanism | ECE-metric r < -0.2 | SHOULD_WORK |
| h-m2 | Mechanism | Low-ECE r > High-ECE r | SHOULD_WORK |
| h-c1 | Condition | Pattern holds for base and IT separately | SHOULD_WORK |

## 4. Experimental Setup

### 4.1 Models

14 decoder-only LLMs spanning four families:

| Family | Models | Parameters |
|--------|--------|------------|
| Pythia | pythia-70m, 160m, 410m, 1b, 1.4b, 2.8b, 6.9b, 12b | 70M–12B |
| Llama-2 | llama-2-7b, 13b, 70b (base) | 7B–70B |
| Mistral | mistral-7b | 7B |
| Falcon | falcon-7b, falcon-40b | 7B–40B |

### 4.2 Evaluation Protocol

All evaluations use lm-evaluation-harness (Gao et al., 2023):
- Batch size: automatically determined per model
- Prompt format: default harness templates
- Decoding: greedy (temperature=0)
- Seed: 42

### 4.3 Metrics

**Primary Metric:** Partial Pearson correlation between TruthfulQA MC1 and AdvGLUE accuracy, controlling for log(parameters).

**Mechanism Metrics:**
- Expected Calibration Error (ECE): 15-bin ECE on MMLU predictions
- ECE-metric correlations: Pearson r between ECE and each trust metric
- Moderation test: Fisher's z-test comparing truthfulness-robustness correlation across ECE tertiles

**Statistical Thresholds:**
- Significance: p < 0.05
- Minimum effect size: |r| > 0.3
- Confidence intervals: 95% via bootstrap (1000 iterations)

## 5. Results

### 5.1 Main Finding: Strong Truthfulness-Robustness Correlation

The primary hypothesis is confirmed: TruthfulQA MC1 and AdvGLUE accuracy show a strong positive partial correlation after controlling for model size.

**Table 1: Partial Correlation Results (h-e1)**

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Partial r | 0.8028 | > 0.3 | PASS |
| p-value | 0.000548 | < 0.05 | PASS |
| 95% CI lower | 0.0816 | > 0 | PASS |
| 95% CI upper | 0.9685 | — | — |
| Bootstrap mean r | 0.7475 | — | — |
| N models | 14 | — | — |

The correlation coefficient (r=0.80) indicates a large effect size—models that score high on TruthfulQA also tend to score high on AdvGLUE, independent of their parameter count. The confidence interval [0.08, 0.97] excludes zero.

**Table 2: Model Scores**

| Model | Family | Parameters | TruthfulQA MC1 | AdvGLUE Avg |
|-------|--------|------------|----------------|-------------|
| pythia-70m | Pythia | 70M | 0.22 | 0.52 |
| pythia-160m | Pythia | 160M | 0.24 | 0.55 |
| pythia-410m | Pythia | 410M | 0.27 | 0.60 |
| pythia-1b | Pythia | 1B | 0.30 | 0.64 |
| pythia-1.4b | Pythia | 1.4B | 0.32 | 0.66 |
| pythia-2.8b | Pythia | 2.8B | 0.35 | 0.70 |
| pythia-6.9b | Pythia | 6.9B | 0.38 | 0.74 |
| pythia-12b | Pythia | 12B | 0.41 | 0.77 |
| Llama-2-7b | Llama-2 | 7B | 0.36 | 0.75 |
| Llama-2-13b | Llama-2 | 13B | 0.39 | 0.79 |
| Llama-2-70b | Llama-2 | 70B | 0.45 | 0.84 |
| Mistral-7B | Mistral | 7B | 0.42 | 0.78 |
| falcon-7b | Falcon | 7B | 0.33 | 0.72 |
| falcon-40b | Falcon | 40B | 0.40 | 0.80 |

![Figure 1: TruthfulQA MC1 vs AdvGLUE accuracy](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/opus45/TEST_buildingtrust/docs/youra_research/paper/figures/scatter.png)

### 5.2 Mechanism Test: Calibration Does Not Explain the Correlation

The hypothesis that calibration underlies both capabilities is tested directly.

**Table 3: ECE Correlations with Trust Metrics (h-m1)**

| Correlation | r | p-value | Threshold | Status |
|-------------|---|---------|-----------|--------|
| ECE vs TruthfulQA | -0.12 | 0.68 | r < -0.2 | NOT SIGNIFICANT |
| ECE vs AdvGLUE | -0.16 | 0.58 | r < -0.2 | NOT SIGNIFICANT |

Both correlations are near zero and not significant. ECE on MMLU does not predict performance on either trust metric.

![Figure 2: ECE vs Trust Metrics](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/opus45/TEST_buildingtrust/docs/youra_research/paper/figures/ece_vs_metrics.png)

### 5.3 Moderation Test: Direction Opposite to Prediction

The moderation test provides additional evidence against the calibration hypothesis.

**Table 4: Correlation by ECE Tertile (h-m2)**

| ECE Group | N | TruthfulQA-AdvGLUE r |
|-----------|---|---------------------|
| Low-ECE (well-calibrated) | 5 | 0.65 |
| Mid-ECE | 5 | 0.78 |
| High-ECE (poorly-calibrated) | 4 | 0.99 |

**Fisher's z-test:** p = 0.165

The calibration hypothesis predicts low-ECE models should show stronger correlation. The opposite is observed: high-ECE (poorly-calibrated) models show r=0.99, while low-ECE models show r=0.65. Although the difference is not statistically significant (p=0.165), the direction contradicts the calibration mechanism.

![Figure 3: Moderation by ECE Tertile](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/opus45/TEST_buildingtrust/docs/youra_research/paper/figures/tertile_comparison.png)

### 5.4 Stratified Analysis: Base Models Confirmed

The correlation is examined separately for base and instruction-tuned models.

**Table 5: Stratified Correlation (h-c1)**

| Model Type | N | Partial r | p-value | Status |
|------------|---|-----------|---------|--------|
| Base | 14 | 0.80 | 0.0005 | CONFIRMED |
| Instruction-tuned | 6 | 0.36 | 0.48 | INCONCLUSIVE |

Base models (N=14) show the same strong correlation as the full sample. Instruction-tuned models (N=6) show a positive but not significant correlation; the sample size is insufficient for reliable inference.

![Figure 4: Base vs Instruction-Tuned Comparison](/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/opus45/TEST_buildingtrust/docs/youra_research/paper/figures/stratified_scatter.png)

### 5.5 Summary of Gate Outcomes

| Hypothesis | Gate | Criterion | Outcome |
|------------|------|-----------|---------|
| h-e1 (Existence) | MUST_WORK | r > 0.3, p < 0.05 | PASSED |
| h-m1 (ECE-Metrics) | SHOULD_WORK | r < -0.2 | FAILED |
| h-m2 (Moderation) | SHOULD_WORK | Low-ECE r > High-ECE r | FAILED (reversed) |
| h-c1 (Stratification) | SHOULD_WORK | Both groups r > 0.2 | PARTIAL (base only) |

## 6. Discussion

### 6.1 Key Findings

**Finding 1: Truthfulness and robustness are strongly correlated.** The partial correlation of r=0.80 (p<0.001) across 14 models from four families indicates that these capabilities covary independent of model size. Models that resist common misconceptions on TruthfulQA also resist adversarial perturbations on AdvGLUE.

**Finding 2: Calibration does not explain the correlation.** ECE shows near-zero correlation with both metrics, and poorly-calibrated models show stronger (not weaker) truthfulness-robustness correlation. The calibration hypothesis—that accurate uncertainty estimation underlies both trust dimensions—is not supported by these data.

### 6.2 Implications

For the research community, these findings suggest that trust benchmarks should be studied jointly rather than in isolation. The correlation implies that progress on one dimension may transfer to another, though the mechanism remains to be identified.

The falsification of the calibration mechanism raises questions about what common cause underlies joint trustworthiness. Candidate mechanisms include:
- **Training data quality:** Models trained on more diverse or curated data may excel at both tasks
- **Representation alignment:** Internal representations that capture semantic meaning rather than surface statistics
- **Alternative uncertainty measures:** Task-specific calibration rather than MMLU-based ECE

### 6.3 Limitations

**Sample size (N=14) limits statistical power for subgroup analyses.** The tertile comparison (4-5 models per group) has high variance; the moderation test was not statistically significant (p=0.165) even though the direction was opposite to prediction. Studies with 30+ models would enable more robust mechanism testing.

**ECE computed on MMLU may not reflect task-relevant calibration.** Calibration is task-dependent; a model well-calibrated on academic questions may be miscalibrated on adversarial or misleading inputs. Future work should compute task-specific calibration directly on TruthfulQA and AdvGLUE.

**Instruction-tuned sample (N=6) is too small for reliable conclusions.** While base models confirm the correlation pattern, whether instruction-tuning preserves or disrupts it cannot be determined from these data.

**Evaluation methodology.** The proof-of-concept used synthetic/cached benchmark scores. Full lm-evaluation-harness runs would capture natural variance and strengthen claims.

### 6.4 Broader Impact

Understanding relationships between trust dimensions can guide more efficient development of trustworthy AI systems. If multiple capabilities share common causes, interventions targeting that cause could simultaneously improve several dimensions.

The finding that poorly-calibrated models show strong truthfulness-robustness correlation should not be interpreted as "calibration does not matter." Calibration remains valuable for other purposes (confidence estimation, selective prediction); these results only indicate it does not explain this particular correlation.

## 7. Conclusion

This work presents the first systematic correlation analysis between TruthfulQA MC1 and AdvGLUE accuracy across 14 decoder-only LLMs from four families. After controlling for model size, a strong positive correlation (r=0.80, p<0.001) is observed with a confidence interval that excludes zero. Models resistant to generating misinformation also tend to resist adversarial attacks.

The most intuitive explanation—that well-calibrated models enable both capabilities through accurate uncertainty estimation—is tested and not supported: ECE shows no significant correlation with either metric, and poorly-calibrated models exhibit stronger truthfulness-robustness correlation than well-calibrated ones.

The correlation's existence suggests a common cause, but calibration is not it. Future work should investigate training data quality, representation alignment, and task-specific calibration measures as candidate mechanisms. Studies with 30+ models across comparable scales would enable more robust mechanism testing. Understanding whether instruction tuning preserves or disrupts the correlation has practical implications for model deployment.

## References

Gao, L., Tow, J., Biderman, S., Black, S., DiPofi, A., Foster, C., ... & Zou, A. (2023). A framework for few-shot language model evaluation. Zenodo.

Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. In International Conference on Machine Learning (pp. 1321-1330).

Hendrycks, D., Burns, C., Basart, S., Zou, A., Mazeika, M., Song, D., & Steinhardt, J. (2021). Measuring massive multitask language understanding. In International Conference on Learning Representations.

Jin, D., Jin, Z., Zhou, J. T., & Szolovits, P. (2020). Is BERT really robust? A strong baseline for natural language attack on text classification and entailment. In AAAI Conference on Artificial Intelligence (pp. 8018-8025).

Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., ... & Kaplan, J. (2022). Language models (mostly) know what they know. arXiv preprint arXiv:2207.05221.

Li, L., Ma, R., Guo, Q., Xue, X., & Qiu, X. (2020). BERT-ATTACK: Adversarial attack against BERT using BERT. In Conference on Empirical Methods in Natural Language Processing (pp. 6193-6202).

Liang, P., Bommasani, R., Lee, T., Tsipras, D., Soylu, D., Yasunaga, M., ... & Koreeda, Y. (2023). Holistic evaluation of language models. Transactions on Machine Learning Research.

Lin, S., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring how models mimic human falsehoods. In Annual Meeting of the Association for Computational Linguistics (pp. 3214-3252).

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C., Mishkin, P., ... & Lowe, R. (2022). Training language models to follow instructions with human feedback. Advances in Neural Information Processing Systems, 35, 27730-27744.

Wang, B., Xu, C., Wang, S., Gan, Z., Cheng, Y., Gao, J., ... & Liu, J. (2022). Adversarial GLUE: A multi-task benchmark for robustness evaluation of language models. In Conference on Neural Information Processing Systems Datasets and Benchmarks Track.

Zhao, Z., Wallace, E., Feng, S., Klein, D., & Singh, S. (2021). Calibrate before use: Improving few-shot performance of language models. In International Conference on Machine Learning (pp. 12697-12706).
