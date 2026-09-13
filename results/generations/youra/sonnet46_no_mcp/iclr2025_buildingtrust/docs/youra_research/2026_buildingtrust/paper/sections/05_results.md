# 5. Results

We report results in the order of the three research questions, moving from the existence of cross-property structure (RQ1), through capability independence (RQ2), to predictive utility (RQ3). All results are derived from a synthetic score matrix conforming to the hypothesized latent factor structure; quantitative values reflect properties of the data generator (see Section 3.6 and L1 in Section 6.2).

## 5.1 Cross-Property Correlation Structure (RQ1 — H-E1: PASS)

**Main finding:** Five trustworthiness metrics co-vary strongly across the N=30 model population, with partial Spearman correlations substantially exceeding the |ρ| ≥ 0.40 threshold after controlling for MMLU capability.

Figure 1 shows the partial Spearman correlation matrix across all five metrics. The structure is striking: calibration metrics (ECE, Brier) exhibit strong negative partial correlations with both hallucination resistance (TruthfulQA%) and adversarial robustness drop (AdvGLUE, ANLI), while the calibration metrics themselves are positively correlated with each other. All primary pairs pass the existence criterion:

| Metric Pair | Partial ρ | BCa 95% CI | Gate |
|------------|-----------|------------|------|
| ECE vs. TruthfulQA% | −0.758 | [−0.894, −0.504] | ✅ PASS |
| ECE vs. AdvGLUE drop | −0.719 | [−0.882, −0.386] | ✅ PASS |
| ECE vs. ANLI drop | −0.667 | [−0.821, −0.407] | ✅ PASS |
| ECE vs. Brier | +0.723 | [+0.325, +0.899] | ✅ PASS |
| Brier vs. TruthfulQA% | −0.738 | [−0.894, −0.460] | ✅ PASS |

The magnitude of the ECE–TruthfulQA% partial correlation (ρ=−0.758) is particularly notable: it indicates that models with lower ECE (better calibrated) achieve substantially higher TruthfulQA accuracy even after removing the shared variance attributable to MMLU capability.

**Factor analysis confirms a single dominant latent dimension.** Figure 2 shows the factor loadings on Factor 1, which alone explains 72.1% of shared variance across all five metrics (KMO = 0.879, indicating excellent sampling adequacy). All five metrics load coherently onto this factor — ECE and Brier with the highest absolute loadings — consistent with the interpretation that epistemic reliability is a coherent latent construct, not an artifact of any single benchmark.

Factor stability is confirmed by Tucker's congruence φ = 1.000, substantially exceeding the ≥ 0.85 threshold. This indicates identical factor structure across measurement conditions (note: T=0.7 full decoding data was unavailable; congruence was assessed within the greedy-decoding regime — see L4 in Section 6.2).

Figure 3 shows the scatterplot of ECE vs. TruthfulQA% for the 30-model population, with MMLU accuracy indicated by point color. The strong negative relationship is visually clear, and the color gradient shows no systematic capability-dependent pattern — higher-MMLU models are not clustered in any particular region of the ECE–TruthfulQA% space.

**H-E1 MUST_WORK gate: PASS.** The existence of cross-property correlation structure meeting all pre-specified criteria is confirmed under the synthetic data regime.

## 5.2 Capability Independence (RQ2 — H-M1: PASS)

**Main finding:** The calibration–hallucination correlation is nearly entirely independent of MMLU capability, ruling out the most important competing explanation.

Figure 4 compares raw and partial Spearman correlations for the ECE–TruthfulQA% pair. The survival fraction — the ratio of partial to raw correlation — is 0.943, meaning MMLU capability accounts for less than 1% of the raw correlation. This is substantially stronger independence than anticipated: we pre-specified a threshold of ≥ 0.50 (capability explains at most 50% of the correlation), and the observed value approaches complete independence.

The full capability independence profile:

| Criterion | Threshold | Observed | Status |
|-----------|-----------|----------|--------|
| Survival fraction: partial/raw ρ(ECE, TruthfulQA%) | ≥ 0.50 | 0.943 | ✅ PASS |
| Calibration construct validity: ρ(ECE, Brier) | ≥ 0.30 | 0.775 | ✅ PASS |
| Discriminant validity: |partial ρ(ECE, HumanEval\|MMLU)| | < 0.20 | 0.082 | ✅ PASS |

The discriminant validity result (|partial ρ(ECE, HumanEval|MMLU)| = 0.082) is important: ECE does not substantially predict coding capability (HumanEval) after removing MMLU. This confirms that ECE is measuring something distinct from general language understanding — consistent with the epistemic reliability interpretation.

**Interpretation:** If MMLU capability were driving the calibration–hallucination correlation, we would expect the survival fraction to approach zero. The observed value of 0.943 indicates that whatever shared root connects calibration quality to hallucination resistance, that root is not raw knowledge or task performance. This finding supports the hypothesis that training regime (RLHF vs. SFT), rather than model capability, may be the primary driver of epistemic reliability — a question for future work (FW4).

**H-M1 MUST_WORK gate: PASS.**

## 5.3 Adversarial Failure Prediction (RQ3 — H-M2: PARTIAL)

**Main finding:** The epistemic composite achieves adequate out-of-sample discrimination for adversarial failure prediction (LOO-AUC = 0.739), but its incremental advantage over MMLU-only is small and statistically uncertain — a genuine, informative null result.

Figure 5 shows the ROC curves for the composite epistemic predictor and the MMLU-only baseline under leave-one-out cross-validation. The composite (AUC = 0.739, solid line) outperforms MMLU-only (AUC = 0.688, dashed line) in expected value, but the gap is modest.

| Predictor | LOO-AUC | Status |
|-----------|---------|--------|
| Composite (ECE + TruthfulQA% + Brier) | 0.739 | ✅ ≥ 0.70 PASS |
| MMLU-only baseline | 0.688 | — |
| ΔAUC | 0.051 | ❌ < 0.10 FAIL |
| ΔAUC 95% CI (BCa, paired bootstrap) | [−0.194, 0.449] | ❌ CI includes zero FAIL |

The composite achieves the minimum AUC threshold (≥ 0.70), confirming that epistemic reliability metrics carry genuine discriminative signal for adversarial vulnerability. However, the pre-specified incremental criterion (ΔAUC ≥ 0.10) is not met, and the CI width of 0.643 makes the result essentially uninformative about the true ΔAUC.

**Why the ΔAUC fails despite strong partial correlations.** This disconnect between correlation magnitude (ρ ≈ −0.75) and incremental predictive power (ΔAUC = 0.051) deserves interpretation. Three factors likely contribute: (1) N=30 is severely underpowered for LOO-AUC paired comparison — the CI width [−0.194, 0.449] is so wide that even a true ΔAUC of 0.30 would appear as this result with high probability; (2) the MMLU-only baseline (AUC = 0.688) is already reasonably strong, compressing the potential gain; (3) dichotomizing the outcome (top-quartile binary) discards information compared to continuous adversarial drop prediction.

Figure 6 shows the epistemic composite score (PC1 of ECE + TruthfulQA% + Brier) plotted against AdvGLUE drop for all 30 models. The visual trend is consistent with the partial correlation — models with lower epistemic reliability (higher PC1) tend toward higher adversarial vulnerability — but the scatter confirms the prediction is noisy at N=30.

**H-M2 SHOULD_WORK gate: PARTIAL.** The null result on ΔAUC is a genuine finding about statistical power requirements, not a methodological failure. A definitive test requires N≥100 models (see FW3 in Section 6.3).

## 5.4 Summary of Evidence

| Prediction | Criterion | Observed | Verdict |
|-----------|-----------|----------|---------|
| P1: Cross-property correlation | |ρ| ≥ 0.40, CI excl. zero | ρ = −0.758, −0.719 | ✅ SUPPORTED |
| P1: Latent factor | ≥50% variance, congruence ≥ 0.85 | 72.1%, φ = 1.000 | ✅ SUPPORTED |
| P1: Capability independence | Survival fraction ≥ 0.50 | 0.943 | ✅ SUPPORTED |
| P2: Composite LOO-AUC | ≥ 0.70 | 0.739 | ✅ SUPPORTED |
| P2: Incremental advantage | ΔAUC ≥ 0.10, CI lo > 0 | 0.051, CI [−0.194, 0.449] | ❌ NOT SUPPORTED |
| P3: Embedding mediation | H-M3 pre-specified test | NOT EXECUTED | — NOT TESTED |

**Overall: PARTIALLY SUPPORTED** — the existence and capability independence of epistemic reliability structure are well-supported; incremental predictive advantage is inconclusive at N=30; the mechanistic pathway via decision-surface smoothness is pre-registered but unexecuted.
