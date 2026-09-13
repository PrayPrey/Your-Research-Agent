# Results

Our experiments reveal a surprising finding: Mamba-2 duality equations produce valid SSM parameters but fail to capture attention structure for output-level reconstruction. We present evidence for both the existence result (h-e1: PASS) and the mechanism result (h-m1: FAIL).

## h-e1: Parameter Validity (PASS)

**RQ1: Do duality equations produce valid SSM parameters?**

Yes. Duality-derived parameters are numerically stable across all test samples.

| Metric | Threshold | Observed | Status |
|--------|-----------|----------|--------|
| NaN/Inf Rate | 0% | **0.0%** | ✅ PASS |
| Magnitude Ratio | < 10× | **0.11×** | ✅ PASS |
| Samples Tested | 100 | 100 | ✅ |

**Interpretation:** The duality conversion produces valid SSM parameters. All 100 samples complete forward passes without numerical issues. The magnitude ratio of 0.11× indicates conservative parameter initialization—SSM outputs are about one-tenth the scale of Transformer outputs, well within the acceptable range.

Figure 1 (figures/gate_metrics.png) shows the stability metrics relative to thresholds. The SSM output distribution (Figure 3, figures/output_distribution.png) confirms no extreme values.

**This establishes technical feasibility:** duality equations can derive SSM parameters from attention weights. The question becomes whether these parameters are *useful*.

## h-m1: Reconstruction Error (FAIL)

**RQ2: Does duality initialization provide lower reconstruction error than random?**

No. Duality initialization produces **higher** reconstruction error than random initialization.

### Global Results

| Metric | Value |
|--------|-------|
| Mean Duality Error | 91.45 |
| Mean Random Error | 89.54 |
| Error Reduction | **-2.13%** (worse) |
| P-value | < 0.0001 |
| Cohen's d | **-4.56** (large negative) |

**Interpretation:** Duality-derived parameters reconstruct attention outputs 2.13% worse than random initialization. This is statistically significant (p < 0.0001) with a large effect size (Cohen's d = -4.56). The negative finding is robust—not due to noise or insufficient samples.

Figure 4 (figures/bar_comparison.png) visualizes the error comparison.

### Per-Layer Analysis

The negative effect is consistent across all 12 BERT layers:

| Layer | Duality Error | Random Error | Δ% | Cohen's d |
|-------|---------------|--------------|-----|-----------|
| 0 | 79.75 | 77.74 | -2.58% | -5.02 |
| 1 | 93.98 | 92.16 | -1.98% | -5.50 |
| 2 | 108.35 | 106.70 | -1.55% | -5.19 |
| 3 | 104.67 | 103.04 | -1.57% | -5.97 |
| 4 | 98.18 | 96.35 | -1.89% | -4.15 |
| 5 | 96.58 | 94.85 | -1.82% | -5.92 |
| 6 | 96.29 | 94.53 | -1.86% | -5.12 |
| 7 | 91.16 | 89.18 | -2.22% | -4.71 |
| 8 | 84.44 | 82.31 | -2.58% | -5.85 |
| 9 | 87.10 | 85.06 | -2.40% | -5.38 |
| 10 | 79.79 | 77.64 | -2.77% | -5.31 |
| 11 | 77.11 | 74.91 | -2.94% | -4.84 |

**Interpretation:** Every layer shows duality performing worse than random. Effect sizes range from d = -4.15 to d = -5.97, all in the "large effect" category. This rules out layer-specific explanations—the mismatch is systematic.

Figure 5 (figures/per_layer_comparison.png) visualizes per-layer errors. Figure 6 (figures/effect_size_per_layer.png) shows the consistently negative effect sizes.

### Causal Chain Verification

Our two-stage verification identifies where the causal chain breaks:

| Step | Description | Status |
|------|-------------|--------|
| 1 | Duality equations → valid SSM parameters | ✅ VERIFIED (h-e1) |
| 2 | Duality parameters → lower reconstruction error | ❌ FALSIFIED (h-m1) |
| 3 | Lower error → better task performance | ⏸️ BLOCKED |

**Interpretation:** The mechanism fails at Step 2. Duality produces valid parameters (Step 1 passes) but these parameters do not capture attention structure for output reconstruction (Step 2 fails). Since Step 2 failed, we did not proceed to test downstream task performance (Step 3).

## Summary of Findings

| Hypothesis | Gate | Result | Confidence |
|------------|------|--------|------------|
| h-e1 (Validity) | MUST_WORK | **PASS** | HIGH |
| h-m1 (Structure) | MUST_WORK | **FAIL** | HIGH |

**Key Insight:** Numerical stability does not imply structural fidelity. Duality-derived SSM parameters are valid (no NaN/Inf, reasonable magnitude) but reconstruct attention outputs worse than random initialization. The hypothesis that duality provides a "better starting point" for distillation is refuted under the output Frobenius norm metric.
