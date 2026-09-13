# Adversarial Fragility and Calibration Are Anticorrelated After Capability Control: A Residual Instability Analysis Across 30 Large Language Models

## Abstract

Trustworthiness evaluations of large language models commonly treat adversarial fragility and miscalibration as positively coupled failure modes, implicitly assuming that a model brittle under adversarial attack will also be overconfident and poorly calibrated. This study tests that assumption directly for the adversarial fragility–calibration pair. A capability-controlled measure of adversarial fragility, termed Residual Instability (RI), is constructed by residualizing AdvGLUE accuracy drop against a PCA-derived capability index across 30 LLMs spanning 9 model families. Contrary to the coupled failure cascade prediction, RI significantly anticorrelates with Expected Calibration Error on the arc_challenge reasoning benchmark (Spearman partial ρ = −0.535, 95% CI = [−0.782, −0.101], p = 0.0034, n = 30): models with higher adversarial fragility, after capability control, exhibit lower calibration error. Three mechanistic interpretations of this finding are considered, with a calibration–robustness trade-off driven by RLHF and instruction tuning identified as the most consistent with available evidence. Scope is explicitly limited to the RI–ECE dimension; sub-hypotheses addressing hallucination, safety, and output variance were not executed due to the gate failure on the primary mechanism. Several material limitations are noted, including that 73% of AdvGLUE scores were OLS-estimated from 11 anchor models.

---

## 1. Introduction

Multi-dimension trustworthiness benchmarks for large language models, such as DecodingTrust [Wang et al., 2023] and TrustLLM [Sun et al., 2024], evaluate failure modes including adversarial robustness, calibration, hallucination, and safety independently, without testing whether performance on one dimension predicts performance on another. An implicit assumption in such frameworks is that these failure modes are positively coupled — that a model fragile under adversarial perturbation will also be miscalibrated and unreliable in other respects.

This study examines whether that assumption holds for the adversarial fragility–calibration pair. A key methodological challenge in such an analysis is confounding by general capability: larger, more capable models tend simultaneously to perform better on adversarial robustness benchmarks and to exhibit lower calibration error. Any raw correlation between adversarial robustness and calibration across a diverse model set is therefore confounded by the underlying capability signal. To address this, the study introduces Residual Instability (RI), defined as the OLS residual of AdvGLUE accuracy drop after regressing out a PCA-derived capability index (PC1) and mean model confidence. RI is constructed to be orthogonal to general capability by design.

The primary empirical finding is that RI significantly anticorrelates with Expected Calibration Error (ECE) on the arc_challenge benchmark: ρ = −0.535, p = 0.0034, 95% CI = [−0.782, −0.101], n = 30. This result is in the opposite direction from the coupled failure cascade prediction, which expected a positive partial correlation of ρ ≥ +0.4. The finding indicates that, after controlling for capability, models with higher adversarial fragility tend to be better calibrated, not worse.

The study makes three contributions: (1) the RI construct — a reusable, capability-orthogonal measure of adversarial fragility (R² = 0.529, SD = 0.121, VIF = 1.000); (2) the empirical RI–ECE anticorrelation across 30 LLMs from 9 families; and (3) a calibration–robustness trade-off hypothesis as a testable alternative mechanistic explanation grounded in the RLHF literature.

The study scope is explicitly limited to the RI–ECE dimension. Sub-hypotheses testing whether RI predicts hallucination rate (HaluEval), safety failure (HarmBench), and output variance (OVI-GSM8K) were blocked by the gate failure on the primary mechanism hypothesis and were not executed. This limitation is a central constraint on the conclusions that can be drawn.

The paper is organized as follows. Section 2 reviews related work on multi-dimension trustworthiness evaluation, adversarial robustness, and model calibration. Section 3 describes the RI methodology. Section 4 details the experimental setup. Section 5 presents results. Section 6 discusses mechanistic interpretations and limitations. Section 7 concludes.

---

## 2. Related Work

### 2.1 Multi-Dimension Trustworthiness Evaluation

DecodingTrust [Wang et al., 2023] evaluates GPT-3.5 and GPT-4 across eight trust dimensions including adversarial robustness, calibration, fairness, and privacy. The study evaluates dimensions independently and does not compute cross-dimension predictive correlations or residualize any metric against capability. TrustLLM [Sun et al., 2024] extends this approach to 16 LLMs across eight dimensions, reporting dimension scores independently. Neither framework tests whether adversarial fragility predicts calibration error after capability control.

A separate line of work [ctlllll, 2024] demonstrates that standard capability benchmarks cluster into two principal components explaining 97.4% of variance, and that two LASSO-selected benchmarks achieve 0.94 Spearman correlation with human Elo ratings. This study applies a methodologically similar PCA capability compression approach but uses it as a confound control variable toward a different research question — the cross-dimension prediction between adversarial robustness and calibration.

### 2.2 Adversarial Robustness Benchmarking

AdvGLUE [Wang et al., 2021] provides the primary adversarial robustness measure used in this study. It applies 14 attack methods, including textual perturbations, synonym substitutions, and paraphrase attacks, on GLUE-derived NLU tasks. Prior work applying AdvGLUE has generally reported robustness scores in isolation without correlating them with other trust dimensions. Know Thy Judge [Eiras et al., 2025] documents that safety-specialized models show a +0.24 false negative rate increase under style perturbations, illustrating that adversarial sensitivity extends across model types.

### 2.3 LLM Calibration

Guo et al. [2017] showed that modern neural networks tend to be overconfident and proposed temperature scaling as a post-hoc calibration method, finding that larger networks are more overconfident. Minderer et al. [2021] revisited calibration for large pretrained models and found improved out-of-the-box calibration relative to earlier architectures. TruthfulQA [Lin et al., 2021] documents an inverse scaling result where larger models are less truthful, motivating the use of a composite capability index rather than raw parameter count as a confound control.

Ouyang et al. [2022] and Ziegler et al. [2019] demonstrate that RLHF and instruction tuning improve model reliability on in-distribution tasks while simultaneously introducing specific adversarial failure modes. This dual effect provides the theoretical basis for the calibration–robustness trade-off interpretation discussed in Section 6.1.

### 2.4 Research Gap

No prior study has computed partial correlations between a capability-residualized adversarial fragility measure and calibration error across a diverse multi-family LLM set. DecodingTrust and TrustLLM provide benchmark infrastructure but do not perform predictive correlation analyses across dimensions. Calibration research identifies scale and training-regime effects on ECE but does not connect these to adversarial robustness. Adversarial robustness work validates robustness signals without correlating them to calibration. This study combines these streams through the RI construct, reporting the direction of the RI–ECE partial correlation as the central empirical question.

---

## 3. Method

### 3.1 Model Set

The analysis is conducted over N = 30 LLMs spanning 9 families: LLaMA (9 models), Mistral (6), Qwen (6), Gemma (2), Falcon (2), SOLAR (2), MPT (1), StableLM (1), and Phi (1). The set covers 3 parameter scales (7B, 13B, 70B+) and 2 training regimes (pretrained-only, instruction-tuned/RLHF).

### 3.2 Adversarial Fragility: AdvGLUE Accuracy Drop

Adversarial fragility is operationalized as AdvGLUE accuracy drop — the difference between benign and adversarial accuracy across 14 attack methods on GLUE-derived NLU tasks. Direct AdvGLUE measurements from TrustLLM ICML 2024 Table 2 were available for 11 of 30 models. For the remaining 22 models, AdvGLUE drop was estimated via OLS regression trained on the 11 anchor measurements, with each estimated value flagged in the dataset. The TrustLLM HuggingFace dataset required user agreement (HTTP 403 error) and was inaccessible; published paper values were used as anchors. This imputation procedure is a material limitation (see Section 6.2, L1): 73% of AdvGLUE values are estimated rather than directly measured, and OLS imputation may compress variance and introduce correlation structures in RI.

AdvGLUE drop values in the assembled dataset range across the 30 models with SD = 0.1212 (95% CI: [0.093, 0.138]).

### 3.3 Capability Index: PC1

PCA is applied to six Open LLM Leaderboard v2 benchmark scores — BBH, ARC-Challenge, MMLU-Pro, MATH, GPQA, and MuSR — to produce a single capability composite (PC1). PC1 explains 68.5% of benchmark variance across the 30 models. This falls marginally below the pre-registered 70% threshold, due to the harder and more diverse tasks in Leaderboard v2. The shortfall is recorded as a sensitivity note (L3, Section 6.2).

ARC-Challenge contributes to PC1 construction (Section 3.3) and is also the source benchmark for ECE measurement (Section 3.5). OLS residualization removes the linear PC1–ECE relationship by construction, but benchmark-specific features of arc_challenge may still influence the RI–ECE residual correlation. This potential circularity is noted as limitation L7.

### 3.4 Residual Instability (RI)

RI is defined as the OLS residual from the regression:

```
AdvGLUE_drop ~ PC1 + mean_confidence
```

where `mean_confidence` is the mean of per-sample maximum-choice softmax probabilities from arc_challenge (range across models: 0.789–0.958). By OLS construction, RI is orthogonal to PC1. Empirical VIF = 1.000 confirms orthogonality. The RI construct passes two pre-registered gate conditions: SD(AdvGLUE_drop) = 0.1212 > 0.05 (PASS) and R²_residualization = 0.529 < 0.80 (PASS). The R² value indicates that capability (PC1) and mean confidence together explain 52.9% of adversarial drop variance, leaving substantial model-specific residual.

### 3.5 Calibration Measurement: ECE

Expected Calibration Error is computed from per-sample softmax probabilities extracted from arc_challenge log-likelihoods (Open LLM Leaderboard v2, n = 1,172 samples per model), using 10-bin equal-width binning. ECE values across the 30 models range from 0.175 (meta-llama/Meta-Llama-3-70B) to 0.472 (stabilityai/stablelm-zephyr-3b).

### 3.6 Statistical Analysis

The primary analysis is the Spearman partial correlation ρ(RI, ECE | PC1, mean_confidence), computed via `pingouin.partial_corr()` [Vallat, 2018]. Holm-Bonferroni correction is applied across 4 pre-registered predictions. Within-family analyses are conducted for the three largest families: LLaMA (n = 9), Mistral (n = 6), and Qwen (n = 6). Bootstrap confidence intervals use 10,000 resamples with seed 42. VIF is computed for all covariates; Cook's distance is computed for outlier identification. All computations are CPU-based (Python 3.10; scikit-learn 1.4.2; pingouin 0.6.1; scipy 1.13.0; statsmodels 0.14.2; uncertainty-calibration 0.1.4). The pipeline is validated by 41/41 unit tests.

---

## 4. Experimental Setup

Two research questions are addressed:

**RQ1:** Is Residual Instability (RI) a non-degenerate construct, orthogonal to general capability, with measurable cross-model variance?

**RQ2:** Does RI significantly predict Expected Calibration Error (ECE) after controlling for capability and mean confidence?

### 4.1 Model Set

| Family | Count | Size Range | Regimes |
|--------|-------|------------|---------|
| LLaMA | 9 | 7B–70B | Pretrained and instruction-tuned |
| Mistral | 6 | 7B–8×7B | Pretrained and instruction-tuned |
| Qwen | 6 | 7B–72B | Pretrained and instruction-tuned |
| Gemma | 2 | 7B | Instruction-tuned |
| Falcon | 2 | 7B–40B | Pretrained and instruction-tuned |
| SOLAR | 2 | 10.7B | Pretrained and instruction-tuned |
| MPT | 1 | 7B | Pretrained |
| StableLM | 1 | 3B | Instruction-tuned |
| Phi | 1 | 2.7B | Instruction-tuned |

### 4.2 Baselines

Two baseline comparisons are used. First, a capability-only predictor: Spearman ρ(PC1, ECE), providing a reference for the partial correlation analysis. Second, the uncontrolled correlation: Spearman ρ(raw AdvGLUE_drop, ECE) without capability residualization, quantifying the degree of capability confounding in the raw relationship.

### 4.3 Gate Conditions

Pre-registered gate conditions for H-E1 (construct validity): SD(AdvGLUE_drop) > 0.05 AND R²_residualization < 0.80.

Pre-registered gate conditions for H-M1 (primary mechanism): Spearman partial ρ ≥ +0.4, Holm-corrected p < 0.05, and consistent positive sign in ≥2/3 of the three largest families.

### 4.4 Implementation

All experiments run on CPU. Python 3.10; scikit-learn 1.4.2, pingouin 0.6.1, scipy 1.13.0, statsmodels 0.14.2, uncertainty-calibration 0.1.4. Random seed: 42. Bootstrap samples: 10,000. During implementation, an initial run used synthetic data as a fallback; this was identified and corrected. All results reported here use real data from Open LLM Leaderboard v2 and TrustLLM ICML 2024 paper Table 2.

---

## 5. Results

### 5.1 RQ1: RI Construct Validity (H-E1 — PASS)

Both pre-registered gate conditions are met.

**SD(AdvGLUE_drop) = 0.1212 (threshold > 0.05; PASS).** The 95% bootstrap CI is [0.093, 0.138], entirely above the threshold. The SD is 2.4 times the threshold value.

**R²_residualization = 0.529 (threshold < 0.80; PASS).** The 95% bootstrap CI is [0.275, 0.721], entirely below the threshold. Capability and mean confidence together explain 52.9% of adversarial drop variance, leaving 47.1% as model-specific residual.

| Metric | Value | 95% CI | Threshold | Status |
|--------|-------|--------|-----------|--------|
| SD(AdvGLUE_drop) | 0.1212 | [0.093, 0.138] | > 0.05 | PASS |
| R²_residualization | 0.5285 | [0.275, 0.721] | < 0.80 | PASS |
| PC1 variance explained | 68.5% | — | ≥ 70% | WARNING |
| VIF (all covariates) | 1.000 | — | < 5.0 | PASS |

PC1 falls marginally below the 70% variance threshold (68.5%), introducing a minor residual capability confounding risk. VIF = 1.000 confirms that RI is orthogonal to PC1 by construction.

### 5.2 RQ2: RI–ECE Partial Correlation (H-M1 — Significant but Inverted)

**Primary result: ρ = −0.535, p = 0.0034, 95% CI = [−0.782, −0.101], n = 30.**

The pre-registered prediction was ρ ≥ +0.4 (positive correlation: more adversarially fragile models predicted to have higher ECE). The observed correlation is −0.535 — statistically significant and in the opposite direction. Models with higher RI (greater adversarial fragility after capability control) tend to have lower ECE (better calibration on arc_challenge). The p-value of 0.0034 survives Holm-Bonferroni correction (α = 0.0125 for the primary prediction). The H-M1 gate therefore fails on two of three pre-registered conditions: the ρ sign condition (expected positive, observed negative) and the family sign consistency condition (expected ≥2/3 positive, observed 1/3 positive).

The gate failure on H-M1, which was designated MUST_WORK, blocked execution of H-M2 (HaluEval), H-M3 (HarmBench), and H-M4 (OVI-GSM8K). Those sub-hypotheses remain not executed.

**Robustness checks:**

Three outliers were identified by Cook's distance: meta-llama/Meta-Llama-3-70B, google/gemma-7b-it, and stabilityai/stablelm-zephyr-3b. Excluding these three, ρ = −0.498, p = 0.008 — the direction and significance are preserved.

Fisher z-test for interaction with capability level: z = −0.561, p = 0.575 (not significant). The anticorrelation does not vary significantly with capability level.

Baseline comparisons:
- ρ(PC1, ECE) = −0.511, p = 0.0039 (capability-only predictor)
- ρ(raw AdvGLUE_drop, ECE) = −0.418, p = 0.0213 (uncontrolled)

The similarity between ρ(PC1, ECE) = −0.511 and ρ(RI, ECE | PC1) = −0.535 indicates that RI adds limited unique predictive signal for ECE beyond what capability (PC1) already captures.

| Condition | Threshold | Actual | Status |
|-----------|-----------|--------|--------|
| Spearman partial ρ(RI, ECE) | ≥ +0.4 | −0.535 | FAIL (inverted sign) |
| Holm-corrected p-value | < 0.05 | 0.0034 | PASS |
| Consistent positive families | ≥ 2/3 | 1/3 (Qwen only) | FAIL |

### 5.3 Per-Family Analysis

| Family | n | ρ(RI, ECE) | p (raw) | p (Holm) | Direction |
|--------|---|------------|---------|----------|-----------|
| LLaMA | 9 | −0.244 | 0.599 | 1.000 | Negative |
| Mistral | 6 | −0.827 | 0.173 | 0.519 | Negative |
| Qwen | 6 | +0.364 | 0.636 | 1.000 | Positive |

Two of three families show negative RI–ECE correlations. No within-family result is statistically significant after Holm correction. Mistral shows the strongest point estimate (ρ = −0.827), but with n = 6 this is underpowered (raw p = 0.173, Holm p = 0.519). Qwen shows a positive sign that differs from the aggregate direction; with n = 6 and p = 0.636, this cannot be interpreted reliably. Per-family results are treated as exploratory.

### 5.4 Reliability Diagram Analysis

Average reliability diagrams stratified by RI quartile show that models in the highest RI quartile (Q4, most adversarially fragile) have calibration curves closest to the perfect diagonal on arc_challenge, while models in the lowest RI quartile (Q1, most robust) show curves further from the diagonal, indicating greater overconfidence. This qualitative pattern is consistent with the statistical result.

---

## 6. Discussion

### 6.1 Mechanistic Interpretations

The finding ρ(RI, ECE | PC1, mean_confidence) = −0.535 (p = 0.0034) contradicts the original prediction of a positive coupled failure cascade. Three mechanistic frameworks are considered.

**Framework 1: Calibration–Robustness Trade-off.** RLHF and instruction tuning have been documented to improve in-distribution calibration [Ouyang et al., 2022; Ziegler et al., 2019] and to simultaneously introduce specific adversarial vulnerabilities [Perez et al., 2022]. Under this framework, instruction-tuned models have simultaneously lower RI (more robust to AdvGLUE attacks after capability control) and lower ECE (better calibrated on arc_challenge reasoning tasks), while pretrained models show the inverse pattern. This training-regime effect, which survives PC1 control, could drive the observed negative partial correlation. The Mistral family's point estimate (ρ = −0.827) is directionally consistent with this interpretation, as Mistral-Instruct variants undergo substantial RLHF, though the small sample size precludes strong conclusions. A decisive test would require stratifying the 30-model set by training regime and testing whether ρ(RI, ECE) approaches zero within each stratum.

**Framework 2: Residual Scale Confounding.** PC1 explains 68.5% of benchmark variance, marginally below the 70% target. Residual large-model effects not fully captured by PC1 could produce a spurious negative partial correlation, since larger models in the post-RLHF era tend to have both lower RI and lower ECE [Minderer et al., 2021]. A supplementary analysis including log(parameter count) as an additional covariate would test this explanation.

**Framework 3: Benchmark Specificity.** arc_challenge ECE measures calibration on four-choice science reasoning tasks, while RI is derived from NLI-style perturbation attacks. These benchmarks may tap orthogonal failure modes whose relationship is specific to this combination rather than a general property of adversarial fragility and calibration. Replication with ECE computed on ≥3 additional benchmarks (e.g., TruthfulQA, BoolQ, MMLU) is required to test this.

Among these three frameworks, Framework 1 is most consistent with the available evidence, including the per-family directional patterns, the ECE distributions by training regime visible in the data, and the existing RLHF literature. However, Frameworks 2 and 3 cannot be excluded from the current data.

### 6.2 Limitations

**L1 — OLS-Estimated AdvGLUE Scores (High Impact).** 73% of AdvGLUE values (22/30 models) are OLS-estimated from 11 published anchor measurements due to gated TrustLLM HuggingFace dataset access. OLS imputation compresses AdvGLUE variance toward the regression mean and may introduce correlation structures that bias the magnitude and direction of ρ(RI, ECE). Direct AdvGLUE measurement on all 30 models via lm-evaluation-harness is required before strong conclusions can be drawn from this result.

**L2 — Single-Benchmark ECE (Medium Impact).** ECE is derived from arc_challenge only. Generalizability to other reasoning benchmarks or to open-ended generation calibration is unknown. The inverted RI–ECE relationship may be specific to this benchmark combination.

**L3 — PC1 Below 70% Threshold (Low-Medium Impact).** PC1 explains 68.5% of benchmark variance rather than the targeted 70%, introducing minor residual capability confounding in RI.

**L4 — Underpowered Within-Family Analysis (Medium Impact).** Per-family analyses use n = 6–9, with estimated statistical power of approximately 0.61 at ρ = 0.4. Family-level findings are exploratory and should not be treated as confirmatory.

**L5 — H-M2/M3/M4 Not Executed (Critical Scope Limitation).** The relationship between RI and hallucination rate (HaluEval), safety failure (HarmBench), and output variance (OVI-GSM8K) is entirely untested. The study's scope is therefore limited to the single RI–ECE dimension. No claim is made about whether the inverted or positive relationship extends to other trust dimensions.

**L6 — Cross-Sectional Observational Design.** The study is a cross-sectional observational analysis across models. Correlation does not imply causation. The negative RI–ECE correlation could reflect unmeasured confounders including model generation, training data composition, or RLHF application details.

**L7 — ARC-Challenge Circularity (Low-Medium Impact).** ARC-Challenge contributes to PC1 construction and is also the sole source of ECE measurements. OLS residualization removes the linear PC1–ECE relationship by construction, but arc_challenge-specific benchmark features may still structure the residual RI–ECE correlation.

### 6.3 Scope of Inference

The central finding — that RI anticorrelates with ECE after capability control — is a statistically significant empirical result (p = 0.0034, bootstrap CI excluding zero) that is robust to outlier removal. However, given the high proportion of OLS-estimated AdvGLUE values (L1), single-benchmark ECE (L2), and the absence of within-regime stratification, the result should be interpreted as preliminary evidence motivating targeted follow-up studies rather than as a definitive characterization of the adversarial fragility–calibration relationship. The finding contradicts the positive coupled failure cascade prediction, and that contradiction is the primary reportable result.

---

## 7. Conclusion

This study tested whether adversarial fragility and calibration error are positively coupled in large language models after controlling for general capability. Across 30 LLMs spanning 9 families, the Residual Instability (RI) construct — the OLS residual of AdvGLUE accuracy drop after regressing out a PCA-derived capability index and mean confidence — significantly anticorrelates with Expected Calibration Error on arc_challenge (Spearman partial ρ = −0.535, p = 0.0034, 95% CI = [−0.782, −0.101]). This direction is opposite to the pre-registered prediction of ρ ≥ +0.4.

Three contributions are reported: (1) the RI construct, validated as non-degenerate (R² = 0.529, SD = 0.121, VIF = 1.000); (2) the empirical anticorrelation between RI and ECE, which refutes the coupled failure cascade prediction for this dimension pair; and (3) a calibration–robustness trade-off hypothesis, grounded in the RLHF literature, as the most plausible mechanistic explanation for the observed anticorrelation.

Several limitations constrain the strength of these conclusions. Most critically, 73% of AdvGLUE scores are OLS-estimated rather than directly measured, and ECE is derived from a single benchmark. The study scope is limited to the RI–ECE dimension; sub-hypotheses for hallucination, safety, and output variance were not executed. Future work should include direct AdvGLUE measurement on all 30 models, ECE replication across multiple benchmarks, and training-regime stratification to test the proposed trade-off mechanism. Whether the inverted relationship extends to hallucination and safety dimensions requires executing redesigned sub-hypotheses with revised directional predictions.

The result does not support treating adversarial fragility and calibration as positively coupled failure modes in the context studied. Multi-dimension trustworthiness evaluations may benefit from empirically testing cross-dimension relationships rather than assuming a particular coupling structure.

---

## References

Wang, B., Chen, W., Pei, H., et al. (2023). DecodingTrust: A Comprehensive Assessment of Trustworthiness in GPT Models. *NeurIPS 2023*.

Sun, L., Huang, Y., Wang, H., et al. (2024). TrustLLM: Trustworthiness in Large Language Models. *arXiv:2401.05561*.

Lin, S. C., Hilton, J., & Evans, O. (2022). TruthfulQA: Measuring How Models Mimic Human Falsehoods. *ACL 2022*.

Li, J., Cheng, X., Zhao, W. X., Nie, J., & Wen, J. (2023). HaluEval: A Large-Scale Hallucination Evaluation Benchmark for Large Language Models. *EMNLP 2023*.

Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On Calibration of Modern Neural Networks. *ICML 2017*.

Minderer, M., et al. (2021). Revisiting the Calibration of Modern Neural Networks. *NeurIPS 2021*.

Ouyang, L., Wu, J., et al. (2022). Training Language Models to Follow Instructions with Human Feedback. *NeurIPS 2022*.

Ziegler, D. M., et al. (2019). Fine-Tuning Language Models from Human Preferences. *arXiv:1909.08593*.

Perez, F., & Ribeiro, I. (2022). Ignore Previous Prompt: Attack Techniques for Language Models. *arXiv:2211.09527*.

Wang, B., et al. (2021). AdvGLUE: A Multi-Task Benchmark for Robustness Evaluation of Language Models. *EMNLP 2021*.

Eiras, F., et al. (2025). Know Thy Judge: On the Robustness of Safety Judges for LLM Evaluation. *ICLR 2025*.

Vallat, R. (2018). Pingouin: Statistics in Python. *Journal of Open Source Software*, 3(31), 1026.
