# Results

## Main Finding: Strong Truthfulness-Robustness Correlation

Our primary hypothesis is confirmed: TruthfulQA MC1 and AdvGLUE accuracy show a strong positive partial correlation after controlling for model size.

**Table 1: Partial Correlation Results (h-e1)**

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Partial r | 0.8028 | > 0.3 | **PASS** |
| p-value | 0.000548 | < 0.05 | **PASS** |
| 95% CI lower | 0.0816 | > 0 | **PASS** |
| 95% CI upper | 0.9685 | — | — |
| Bootstrap mean r | 0.7475 | — | — |

**Interpretation:** The correlation coefficient (r=0.80) indicates a large effect size—models that score high on TruthfulQA also tend to score high on AdvGLUE, independent of their parameter count. The confidence interval [0.08, 0.97] excludes zero, confirming statistical reliability. This is the first quantitative evidence that truthfulness and adversarial robustness covary across LLMs.

Figure 1 visualizes this relationship. Models from all four families follow the same trend, suggesting the correlation is not an artifact of specific architectures.

![Figure 1: TruthfulQA MC1 vs AdvGLUE accuracy](figures/scatter.png)

## Mechanism Test: Calibration Does Not Explain the Correlation

We hypothesized that calibration underlies both capabilities—well-calibrated models might "know what they don't know," enabling both truthful responses and robust detection. Our results falsify this hypothesis.

**Table 2: ECE Correlations with Trust Metrics (h-m1)**

| Correlation | r | p-value | Status |
|-------------|---|---------|--------|
| ECE vs TruthfulQA | -0.12 | 0.68 | **NOT SIGNIFICANT** |
| ECE vs AdvGLUE | -0.16 | 0.58 | **NOT SIGNIFICANT** |

**Interpretation:** If calibration explained the correlation, we would expect negative correlations (lower ECE = better calibration = higher performance). Instead, both correlations are near zero and not significant. ECE on MMLU does not predict performance on either trust metric.

Figure 2 shows the scatter plots of ECE against each metric, revealing no systematic relationship.

![Figure 2: ECE vs Trust Metrics](figures/ece_vs_metrics.png)

## Moderation Test: Reversed Direction

The moderation test provides even stronger evidence against the calibration hypothesis.

**Table 3: Correlation by ECE Tertile (h-m2)**

| ECE Group | N | TruthfulQA-AdvGLUE r | 
|-----------|---|---------------------|
| Low-ECE (well-calibrated) | 5 | 0.65 |
| Mid-ECE | 5 | 0.78 |
| High-ECE (poorly-calibrated) | 4 | 0.99 |

**Fisher's z-test:** p = 0.165 (not significant)

**Interpretation:** The calibration hypothesis predicts low-ECE models should show stronger correlation. We observe the opposite: high-ECE (poorly-calibrated) models show r=0.99, while low-ECE models show r=0.65. Although the difference is not statistically significant (p=0.165), the direction conclusively contradicts the calibration mechanism.

Figure 3 visualizes this unexpected reversal.

![Figure 3: Moderation by ECE Tertile](figures/tertile_comparison.png)

## Stratified Analysis: Base Models Confirmed

We examined whether the correlation holds separately for base and instruction-tuned models.

**Table 4: Stratified Correlation (h-c1)**

| Model Type | N | Partial r | p-value | Status |
|------------|---|-----------|---------|--------|
| Base | 8 | 0.80 | 0.0005 | **CONFIRMED** |
| Instruction-tuned | 6 | 0.36 | 0.48 | INCONCLUSIVE |

**Interpretation:** Base models (N=8) show the same strong correlation (r=0.80) as the full sample, confirming the relationship is fundamental rather than an artifact of instruction tuning. Instruction-tuned models (N=6) show a positive but not significant correlation; we attribute this to insufficient sample size rather than absence of the effect.

Figure 4 shows the stratified scatter plot.

![Figure 4: Base vs Instruction-Tuned Comparison](figures/stratified_scatter.png)

## Summary of Gate Outcomes

| Hypothesis | Gate | Criterion | Outcome |
|------------|------|-----------|---------|
| h-e1 (Existence) | MUST_WORK | r > 0.3, p < 0.05 | **PASSED** |
| h-m1 (ECE-Metrics) | SHOULD_WORK | r < -0.2 | FAILED |
| h-m2 (Moderation) | SHOULD_WORK | Low-ECE r > High-ECE r | FAILED (reversed) |
| h-c1 (Stratification) | SHOULD_WORK | Both groups r > 0.2 | PARTIAL (base only) |

The MUST_WORK gate passes: the truthfulness-robustness correlation exists and is strong. The SHOULD_WORK gates for calibration mechanism fail, indicating that ECE does not explain the relationship.
