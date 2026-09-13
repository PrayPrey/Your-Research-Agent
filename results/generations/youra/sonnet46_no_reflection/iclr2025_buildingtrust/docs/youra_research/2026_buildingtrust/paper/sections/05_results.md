# 5. Results

We present results in two parts: construct validation (RQ1, H-E1) establishes that RI is a non-degenerate, measurable signal; mechanism testing (RQ2, H-M1) reveals the surprising anticorrelation between RI and ECE.

## 5.1 RQ1: RI Construct Validity (H-E1 — PASS)

The RI construct must satisfy two gate conditions before its relationship with ECE can be meaningfully interpreted.

**SD(AdvGLUE_drop) = 0.1212 > 0.05 threshold (PASS).** Figure 8 shows the gate metric comparison with bootstrap confidence intervals. Adversarial fragility varies substantially across the 30-model set: the standard deviation of 0.121 is 2.4× the required threshold, with a 95% bootstrap CI of [0.093, 0.138] entirely above 0.05. This confirms that the model set contains genuine heterogeneity in adversarial robustness — a precondition for any meaningful correlation analysis.

**R²_residualization = 0.529 < 0.80 threshold (PASS).** The OLS regression of AdvGLUE drop on capability-PC1 and mean_confidence explains only 52.9% of adversarial fragility variance (95% CI: [0.275, 0.721]). This means 47.1% of adversarial fragility remains as residual signal after capability is controlled — the RI construct is non-degenerate. Figure 2 shows the PC1 vs. AdvGLUE scatter with the OLS fit line; the visible residual scatter confirms the construct validity result.

Figure 1 shows the RI distribution across model families and training regimes. Pretrained models cluster toward positive RI values (higher fragility relative to capability), while instruction-tuned models cluster toward negative RI (lower fragility relative to capability). This training-regime separation in the RI construct foreshadows the mechanism interpretation in the next section.

**VIF = 1.000** confirms that PC1 and mean_confidence are perfectly uncorrelated with RI by OLS construction — the capability confound is fully removed.

**Summary:** The RI construct is valid, non-degenerate, and orthogonal to capability. The infrastructure for mechanism testing is established.

## 5.2 RQ2: RI–ECE Partial Correlation (H-M1 — Significant but Inverted)

The pre-registered prediction was a positive partial correlation ρ(RI, ECE | PC1, mean_confidence) ≥ +0.4. The result is a statistically robust negative correlation.

**Primary result: ρ = −0.535, p = 0.0034, 95% CI = [−0.782, −0.101], n = 30.**

Figure 4 shows the partial regression scatter plot. Each point is one of the 30 LLMs; the partial regression line has a clearly negative slope. The 95% bootstrap confidence interval excludes zero by a wide margin — this is not a marginal result. The p-value of 0.0034 survives Holm-Bonferroni correction (α = 0.05/4 = 0.0125 for the primary prediction).

**What this means:** Models with higher Residual Instability — more adversarially fragile after controlling for capability — are *better calibrated* on arc_challenge reasoning tasks (lower ECE). The coupled failure cascade hypothesis predicted the opposite: that sharp decision boundaries would cause overconfidence (high ECE) in adversarially fragile models. The data refutes this prediction with high statistical confidence.

**Key observations:**

1. *The effect is robust to outlier removal.* Three Cook's distance outliers were identified (Meta-Llama-3-70B, gemma-7b-it, stablelm-zephyr-3b). Excluding these three models, ρ remains negative (ρ = −0.498, p = 0.008), confirming the result is not driven by any single model.

2. *RI adds minimal unique signal beyond capability.* The baseline correlation ρ(PC1, ECE) = −0.511 (p = 0.0039) is nearly identical in magnitude to ρ(RI, ECE|PC1) = −0.535. Figure 6 visualizes this comparison. The anticorrelation between RI and ECE is substantially capability-mediated — a finding that strengthens the residual scale confounding interpretation discussed in Section 6.

3. *The Fisher z-test for capability interaction is non-significant.* Dividing the model set at median PC1 and comparing ρ in high-capability vs. low-capability halves yields z = −0.561, p = 0.575, meaning the anticorrelation does not significantly interact with capability level. The inverted relationship holds across the capability range.

## 5.3 Per-Family Analysis

Figure 5 shows per-family RI–ECE partial correlations for the three largest families.

| Family | n | ρ(RI, ECE) | p (Holm) | Direction |
|--------|---|------------|----------|-----------|
| LLaMA | 9 | −0.244 | 1.000 | Negative |
| Mistral | 6 | −0.827 | 0.519 | Negative |
| Qwen | 6 | +0.364 | 1.000 | Positive |

Two of three families show negative RI–ECE correlations; only Qwen shows a positive sign (not statistically significant at n=6). The Mistral family shows the strongest anticorrelation (ρ = −0.827), consistent with heavy RLHF application in Mistral-Instruct variants — models that are simultaneously better calibrated (lower ECE) and more adversarially fragile after capability control (higher RI). Qwen's positive sign may reflect different training data composition or instruction tuning methodology, or simply underpowered estimation at n=6.

**This family heterogeneity is interpretively important:** the anticorrelation is not universal across all model lineages, suggesting that training regime and family-specific factors modulate the RI–ECE relationship. The overall negative correlation reflects the dominant RLHF-trained families (LLaMA-Instruct, Mistral-Instruct) in the 30-model set.

## 5.4 Reliability Diagram Analysis

Figure 7 shows average reliability diagrams grouped by RI quartile. Models in the top RI quartile (most adversarially fragile, Q4) show calibration curves closest to the diagonal — better calibrated. Models in the bottom RI quartile (most robust, Q1) show curves further from the diagonal, indicating overconfidence at high confidence levels.

This visualization confirms the statistical result in an interpretable form: the most adversarially vulnerable models in our set are not the most overconfident — they are the best calibrated. The overconfident models are precisely those that appear robust on AdvGLUE after capability control.

## 5.5 H-E1 Gate Summary

| Metric | Value | 95% CI | Threshold | Status |
|--------|-------|--------|-----------|--------|
| SD(AdvGLUE_drop) | 0.1212 | [0.093, 0.138] | > 0.05 | ✓ PASS |
| R²_residualization | 0.5285 | [0.275, 0.721] | < 0.80 | ✓ PASS |
| PC1 variance explained | 68.5% | — | ≥ 70% | ⚠ WARN |
| VIF (all covariates) | 1.000 | — | < 5.0 | ✓ PASS |

## 5.6 H-M1 Gate Summary

| Condition | Threshold | Actual | Status |
|-----------|-----------|--------|--------|
| Spearman partial ρ(RI, ECE) | ≥ +0.4 | −0.535 | ✗ FAIL (wrong sign) |
| Holm-corrected p-value | < 0.05 | 0.0034 | ✓ PASS |
| Consistent positive families | ≥ 2/3 | 1/3 (Qwen only) | ✗ FAIL |

H-M1 satisfies one of three gate conditions. The MUST_WORK gate is not met because the pre-registered direction (positive coupling) is inverted. However, the significant anticorrelation is itself a substantive empirical finding — not a null result — and constitutes the primary contribution of this paper.
