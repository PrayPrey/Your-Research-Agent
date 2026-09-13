# 4. Experimental Setup

We design experiments to answer two research questions that map directly to the claims in the Introduction:

**RQ1:** Is Residual Instability (RI) a non-degenerate, measurable construct orthogonal to general capability? *(H-E1: existence/construct validity)*

**RQ2:** Does RI significantly predict Expected Calibration Error (ECE) after controlling for capability and mean confidence? *(H-M1: primary mechanism)*

These questions are intentionally narrow. Our hypothesis originally included RQ3 (RI → HaluEval), RQ4 (RI → HarmBench LOFO-CV), and RQ5 (RI → GSM8K output variance), but these sub-hypotheses depend on H-M1 passing a MUST_WORK gate. Because H-M1 produced an inverted result, we transparently scope this paper to RQ1 and RQ2.

## 4.1 Model Set

We evaluate 30 LLMs covering 9 model families (Table 1), 3 parameter scales (7B, 13B, 70B+), and 2 training regimes (pretrained-only, instruction-tuned/RLHF). The model set is constructed from publicly available leaderboard data and covers a diversity of architectural lineages, training data compositions, and alignment procedures.

| Family | Count | Size Range | Regimes |
|--------|-------|------------|---------|
| LLaMA | 9 | 7B–70B | Both |
| Mistral | 6 | 7B–8×7B | Both |
| Qwen | 6 | 7B–72B | Both |
| Gemma | 2 | 7B | Instruction-tuned |
| Falcon | 2 | 7B–40B | Both |
| SOLAR | 2 | 10.7B | Both |
| MPT | 1 | 7B | Pretrained |
| StableLM | 1 | 3B | Instruction-tuned |
| Phi | 1 | 2.7B | Instruction-tuned |

**Rationale:** The diversity requirement (≥3 families, ≥2 scales, ≥2 training regimes) ensures that any observed RI–ECE correlation is not an artifact of a single family's architectural or training properties. LOFO-CV across families would detect family-specific confounds; within-family partial correlations assess cross-family consistency.

## 4.2 Datasets and Benchmarks

**Adversarial fragility — AdvGLUE** [Wang et al., 2021]: Accuracy drop under 14 adversarial attack methods on GLUE-derived NLU tasks. For 11 models: published values from TrustLLM ICML 2024 Table 2. For 22 models: OLS-estimated from the 11 anchors (flagged in all analyses).

**Capability benchmarks — Open LLM Leaderboard v2** [Hugging Face, 2024]: Per-model scores on BBH, ARC-Challenge, MMLU-Pro, MATH, GPQA, and MuSR. Fetched from public HuggingFace per-model detail datasets (`open-llm-leaderboard/<model-slug>-details`). Used to construct PC1 capability index.

**Calibration — arc_challenge ECE** [Open LLM Leaderboard v2]: Per-sample softmax probabilities from arc_challenge log-likelihoods (n = 1,172 samples per model). ECE computed using `uncertainty-calibration` library via 10-bin equal-width binning.

**Why arc_challenge for ECE:** arc_challenge is a 4-choice multiple-choice task where per-sample softmax probabilities are directly interpretable as choice confidences. Leaderboard v2 stores per-sample probability outputs in parquet format, enabling ECE computation without model re-evaluation. This is the only benchmark in leaderboard v2 for which full per-sample probability distributions are readily accessible across all 30 models.

## 4.3 Baselines

We compare RI-augmented models against two baselines:

**Capability-only predictor (PC1 → ECE):** OLS regression using PC1 alone to predict ECE. This baseline quantifies how much predictive power RI adds beyond raw capability. The baseline correlation ρ(PC1, ECE) = −0.511 provides a reference point for interpreting ρ(RI, ECE|PC1).

**Raw AdvGLUE drop (uncontrolled):** Spearman correlation ρ(AdvGLUE_drop, ECE) without capability residualization. Comparing this to the partial correlation ρ(RI, ECE|PC1) quantifies the extent of capability confounding in the raw relationship.

## 4.4 Evaluation Metrics

**Primary — Spearman partial correlation ρ(RI, ECE | PC1, mean_confidence):** Non-parametric, robust to non-normality in ECE distribution. Positive values would support the coupled failure cascade hypothesis; negative values indicate the anticorrelation we observe.

**Gate conditions for H-E1 (RQ1):**
- SD(AdvGLUE_drop) > 0.05 — sufficient fragility variance
- R²_residualization < 0.80 — RI non-degenerate (capability explains < 80% of fragility)

**Gate conditions for H-M1 (RQ2):**
- Spearman partial ρ ≥ +0.4 (pre-registered direction)
- Holm-corrected p < 0.05
- Consistent positive sign in ≥ 2/3 family subgroups

Statistical significance evaluated at α = 0.05 with Holm-Bonferroni correction across 4 pre-registered predictions. Bootstrap confidence intervals use 10,000 resamples.

## 4.5 Implementation Details

All experiments run on CPU (no GPU required — analysis of pre-computed benchmark scores). Implementation in Python 3.10 with the following key libraries:

| Package | Version | Role |
|---------|---------|------|
| scikit-learn | 1.4.2 | PCA, OLS |
| pingouin | 0.6.1 | Spearman partial correlation, Holm correction |
| scipy | 1.13.0 | Bootstrap CI, Fisher z-test |
| statsmodels | 0.14.2 | OLS diagnostics, VIF |
| uncertainty-calibration | 0.1.4 | ECE computation |
| pandas | 2.2.2 | Data assembly |

**Seed:** 42 (all random operations). **Bootstrap samples:** 10,000. All code, data (where redistributable), and experiment logs are available in the supplementary material.
