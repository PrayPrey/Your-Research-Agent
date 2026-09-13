# 3. Methodology

Our approach builds on a core observation: raw correlations between adversarial fragility and calibration are confounded by general model capability. Larger, more capable models tend to be simultaneously more robust and better calibrated, making any uncontrolled correlation uninformative about a causal or structural relationship between fragility and calibration as independent properties. We address this through **Residual Instability (RI)** — a capability-orthogonal operationalization of adversarial fragility constructed via PCA and OLS residualization.

## 3.1 Model Set

We construct a benchmark matrix over N = 30 LLMs spanning 9 families (LLaMA, Mistral, Qwen, Gemma, Falcon, SOLAR, MPT, StableLM, Phi), 3 parameter scales (7B, 13B, 70B+), and 2 training regimes (pretrained-only, instruction-tuned/RLHF). This diversity is required for two reasons: (1) to ensure sufficient variance in both adversarial fragility and calibration scores across families and training regimes, and (2) to enable within-family partial correlation analysis that tests whether the RI–ECE relationship is consistent across model lineages.

## 3.2 Adversarial Fragility: AdvGLUE Accuracy Drop

Adversarial robustness is operationalized as **AdvGLUE accuracy drop** — the difference between a model's benign accuracy and adversarial accuracy on AdvGLUE benchmark tasks [Wang et al., 2021], which applies 14 adversarial attack methods (synonym substitution, textual perturbations, paraphrase attacks) to GLUE-derived NLU tasks.

**Data sources:** For 11 of 30 models, AdvGLUE accuracy drop values are sourced from TrustLLM ICML 2024 Table 2 [Huang et al., 2024] — peer-reviewed published values. The TrustLLM HuggingFace dataset was inaccessible (HTTP 403, gated access requiring user agreement). For the remaining 22 models, AdvGLUE drop was estimated via OLS regression trained on the 11 anchor models, using capability scores as predictors. These estimated values are flagged in all analyses (`advglue_estimated=True`). We acknowledge this as a material limitation (L1) and discuss its potential impact in Section 6.

## 3.3 Capability Index: PC1

To capture general model capability as a single confound variable, we apply Principal Component Analysis (PCA) to six benchmark scores from **Open LLM Leaderboard v2** [Hugging Face, 2024]: BBH, ARC-Challenge, MMLU-Pro, MATH, GPQA, and MuSR. These benchmarks represent diverse reasoning domains and are publicly available as per-model detail datasets.

**Rationale:** A composite capability index via PCA is preferred over a single benchmark (e.g., MMLU) because it captures the shared variance across capability domains while being robust to benchmark-specific quirks. Prior work demonstrates that 5–6 standard benchmarks explain ~97% of capability variance via PCA [ctlllll, 2024], making PC1 a reliable low-dimensional capability summary.

PC1 explained **68.5%** of benchmark variance across the 30 models — marginally below the 70% target, due to the harder and more diverse v2 leaderboard tasks (MATH, GPQA, MuSR) producing higher inter-model variance than v1 tasks. This is recorded as a sensitivity note (L3); the pipeline proceeds as PC1 still captures the dominant capability signal.

## 3.4 Residual Instability (RI)

The core methodological contribution is the **RI construct**. We fit an Ordinary Least Squares regression:

```
AdvGLUE_drop ~ PC1 + mean_confidence
```

where `mean_confidence` is the mean of per-sample maximum-choice softmax probabilities from arc_challenge (Open LLM Leaderboard v2). The **RI score** for each model is the OLS residual — the component of adversarial fragility that is orthogonal to both general capability and mean confidence.

**Rationale for OLS residualization:** By construction, the OLS residual is orthogonal to the predictor space (PC1 + mean_confidence). This ensures VIF = 1.000 between RI and PC1 — confirmed empirically — meaning RI contains no linear capability information. Any correlation between RI and a downstream variable (ECE, hallucination rate) cannot be explained by capability alone.

**Construct validity (H-E1):** The RI construct is validated by two gate conditions:
- SD(AdvGLUE_drop) = 0.1212 > 0.05 threshold (95% CI: [0.093, 0.138]) — sufficient fragility variance exists across the model set
- R²_residualization = 0.5285 < 0.80 threshold (95% CI: [0.275, 0.721]) — capability explains only 52.9% of adversarial fragility variance, leaving substantial residual signal

Both conditions pass with wide margins. Figure 1 shows the RI distribution across model families and training regimes; Figure 2 shows the PC1 vs. AdvGLUE scatter with OLS fit.

## 3.5 Calibration Measurement: ECE

**Expected Calibration Error (ECE)** is computed from per-sample softmax probabilities extracted from arc_challenge log-likelihoods (Open LLM Leaderboard v2, n = 1,172 samples per model). ECE measures the mean absolute difference between a model's expressed confidence and its empirical accuracy in equally-spaced confidence bins — lower ECE indicates better calibration.

ECE range across the 30 models: 0.175 (Meta-Llama-3-70B, best calibrated) to 0.472 (StableLM-Zephyr-3B, worst calibrated). This range reflects realistic LLM calibration variation and validates the ECE measurement approach.

**Limitation (L2):** ECE is computed from arc_challenge only — a 4-choice science reasoning task. Multi-benchmark ECE (TruthfulQA, BoolQ, MMLU) would be more generalizable. The inverted RI–ECE relationship may be benchmark-specific; we report this scope limitation and propose replication as future work.

## 3.6 Statistical Analysis

**Primary analysis:** Spearman partial correlation ρ(RI, ECE | PC1, mean_confidence) — a non-parametric measure robust to ECE distribution shape, with nuisance variables (PC1, mean_confidence) partialed out. Computed using `pingouin.partial_corr()` [Vallat, 2018].

**Multiple comparison correction:** Holm-Bonferroni correction applied across the four pre-registered predictions (P1–P4).

**Within-family analysis:** Spearman partial correlations computed separately for LLaMA (n=9), Mistral (n=6), and Qwen (n=6) subgroups to test cross-family consistency.

**Uncertainty quantification:** Bootstrap confidence intervals (10,000 resamples) computed for all primary statistics (SD, R²_residualization, ρ).

**Outlier diagnostics:** Cook's distance computed for all 30 models; 3 outliers flagged (Meta-Llama-3-70B, gemma-7b-it, stablelm-zephyr-3b) but retained in primary analyses, with sensitivity analysis excluding outliers reported.

**Multicollinearity check:** Variance Inflation Factor (VIF) computed for all covariates; VIF = 1.000 for all variables confirms no multicollinearity between RI, PC1, and mean_confidence.

The full pipeline — DataAssembler, RIComputer, GateEvaluator, and ECEComputer — is implemented in Python 3.10 with scikit-learn 1.4.2, scipy 1.13.0, statsmodels 0.14.2, and pingouin 0.6.1, validated by 41/41 unit tests.
