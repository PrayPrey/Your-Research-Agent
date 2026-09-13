# Results

Our experiments provide converging evidence that RLHF instruction tuning causes geometric distortion of confidence signals. We present results for each research question in sequence, building the argument that discriminative degradation exists (RQ1), is caused by margin inflation (RQ2), is geometric rather than scalar (RQ3), and is independently confirmed by Brier decomposition (RQ4).

## RQ1: Discriminative Degradation Exists

Table 1 presents AUROC results for margin-based correctness prediction across model families.

**Table 1: AUROC Comparison (Margin → Correctness)**

| Family | Base AUROC | Instruct AUROC | Δ AUROC | 95% CI |
|--------|------------|----------------|---------|---------|
| Qwen | 0.8298 | 0.8076 | +0.0222 | [0.0074, 0.0370] |
| Mistral | 0.7797 | 0.7413 | +0.0385 | [0.0238, 0.0531] |
| **Mean** | - | - | **+0.0303** | - |

Both model families show statistically significant AUROC degradation after instruction tuning—the 95% confidence intervals exclude zero. The mean degradation of 3.03 percentage points represents a meaningful reduction in the model's ability to distinguish correct from incorrect predictions based on confidence.

**Interpretation:** This result establishes that discriminative degradation is real and consistent across model families. The effect is not attributable to vendor-specific implementation: both Qwen (Chinese origin) and Mistral (European origin) show the same qualitative pattern despite different training pipelines. This suggests RLHF itself—not idiosyncratic training choices—is the cause.

## RQ2: Margin Inflation Explains the Mechanism

Table 2 presents conditional margin analysis, revealing the mechanism underlying AUROC degradation.

**Table 2: Conditional Margin Statistics**

| Family | E[m|correct]_base | E[m|correct]_inst | E[m|incorr]_base | E[m|incorr]_inst | Inflation Ratio |
|--------|-------------------|-------------------|------------------|------------------|-----------------|
| Qwen | 3.605 | 7.149 | 0.960 | 2.933 | **3.06x** |
| Mistral | 1.624 | 13.381 | 0.468 | 7.861 | **16.79x** |

**Key Finding:** While margins inflate for both correct and incorrect predictions after instruction tuning, the inflation for incorrect predictions is disproportionate. In both families, E[margin|incorrect] increases substantially—3.06x for Qwen and 16.79x for Mistral—with permutation test p-values < 0.001 for both.

**Effect Sizes:** Cohen's d = 1.01 for Qwen and d = 1.85 for Mistral, indicating large effects with practical significance.

**Interpretation:** This explains *why* AUROC degrades. RLHF's preference optimization rewards decisive responses regardless of correctness. When incorrect predictions have inflated margins, the confidence-correctness boundary becomes blurred—high margins no longer reliably indicate high probability of being correct.

## RQ3: Distortion is Geometric, Not Scalar

Table 3 presents percentile-normalized monotonicity analysis, the key test for geometric vs. scalar distortion.

**Table 3: Percentile-Normalized β Coefficients**

| Family | β_base | β_instruct | Δβ | 95% CI | Effect Size |
|--------|--------|------------|-----|---------|-------------|
| Qwen | 2.222 | 1.466 | 0.756 | [0.663, 0.856] | 15.3 |
| Mistral | 1.558 | 0.931 | 0.627 | [0.557, 0.701] | 17.0 |

**Key Finding:** Even after percentile normalization (which removes scale differences), the slope of the confidence-correctness relationship is significantly attenuated in instruction-tuned models. Both families show β_instruct < β_base with p < 0.001.

**Interpretation:** If RLHF caused only scalar distortion (like temperature miscalibration), percentile normalization would eliminate the difference—a higher constant factor applied uniformly would not change the rank-based relationship. The persistence of slope attenuation after normalization proves the distortion is *geometric*: RLHF changes the shape of the probability landscape, not just its scale.

This has critical practical implications: temperature scaling (a scalar correction) cannot repair geometric distortion. Practitioners who apply temperature scaling to RLHF models may achieve improved ECE while discrimination remains degraded.

## RQ4: Brier Decomposition Confirms Geometric Distortion

Table 4 presents Murphy's Brier score decomposition, providing independent confirmation of geometric distortion.

**Table 4: Brier Score Decomposition**

| Family | Model | Reliability (↓) | Refinement (↑) | Uncertainty |
|--------|-------|-----------------|----------------|-------------|
| Qwen | Base | 0.0173 | **0.0559** | 0.2042 |
| Qwen | Instruct | 0.0547 | 0.0343 | 0.2082 |
| Mistral | Base | 0.0185 | **0.0580** | 0.2424 |
| Mistral | Instruct | 0.1507 | 0.0093 | 0.2440 |

**Refinement Degradation:**
- Qwen: Δ = +0.0216 (95% CI: [0.0179, 0.0253]), Cohen's d = 11.3
- Mistral: Δ = +0.0487 (95% CI: [0.0453, 0.0522]), Cohen's d = 28.6

**Interpretation:** The Brier decomposition separates calibration (Reliability) from discrimination (Refinement). Scalar distortion (temperature-like rescaling) primarily affects Reliability by shifting probabilities toward or away from extremes. Geometric distortion affects Refinement by degrading the model's ability to discriminate outcomes.

The observed Refinement degradation in both families confirms the geometric interpretation independently of the monotonicity analysis. Refinement measures how well predictions distinguish correct from incorrect answers—its degradation means the probability landscape has been reshaped, not merely rescaled.

## Aggregate Summary

Table 5 summarizes results across all four experiments.

**Table 5: Summary of Experimental Results**

| RQ | Metric | Qwen | Mistral | Hypothesis | Gate |
|----|--------|------|---------|------------|------|
| RQ1 | Δ AUROC | +0.0222** | +0.0385** | Degradation exists | **PASS** |
| RQ2 | Inflation ratio | 3.06x** | 16.79x** | Margin inflation mechanism | **PASS** |
| RQ3 | Δβ_percentile | 0.756** | 0.627** | Geometric distortion | **PASS** |
| RQ4 | Δ Refinement | +0.0216** | +0.0487** | Independent confirmation | **PASS** |

** p < 0.001

All four experiments pass their respective gates. The evidence converges on the conclusion that RLHF instruction tuning causes geometric distortion of confidence signals through the mechanism of disproportionate margin inflation for incorrect predictions.

## Unexpected Finding: Magnitude Asymmetry

We observe a surprising asymmetry in effect magnitudes between families. Mistral shows 16.79x margin inflation for incorrect predictions compared to Qwen's 3.06x—a 5x difference in mechanism strength—yet both show similar AUROC degradation magnitudes (3.85pp vs 2.22pp).

**Competing Explanations:**

1. **Training procedure differences:** Mistral may use more aggressive RLHF (longer training, stronger KL penalty) than Qwen.
2. **Base model quality:** Mistral's lower base accuracy (58.75% vs 71.39%) may provide more "room" for margin inflation on incorrect predictions.
3. **Architecture effects:** Different attention patterns or layer normalizations may respond differently to preference optimization.

We consider (1) most likely: different model providers make different RLHF strength choices, creating a discrimination-capability tradeoff that manifests as varying distortion magnitudes.
