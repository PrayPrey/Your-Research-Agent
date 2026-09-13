# Validation Report: H-E1

**Date:** 2026-07-09 22:35:27
**Hypothesis:** Pearson correlation between benchmark CV and mean cross-benchmark Spearman ρ is negative and moderate-to-strong (r < -0.5) with statistical significance (p < 0.05).
**Gate Type:** MUST_WORK
**Gate Status:** ❌ FAILED

---

## Executive Summary

This validation report presents results for hypothesis H-E1, testing whether coefficient of variation (CV) predicts cross-benchmark ranking stability (measured by mean Spearman ρ).

**Key Findings:**
- Pearson r = -0.486 (95% CI: [-0.854, 0.207])
- p-value = 0.1542
- Gate decision: FAIL - CV is not a valid stability predictor

---

## Data Summary

### Benchmarks Analyzed
| Benchmark | CV | Mean ρ | n_pairs |
|-----------|-----|--------|---------|
| TrustBench-Ethics | 0.130 | 0.181 | 9 |
| FinTrust | 0.144 | 0.145 | 9 |
| MultiTrust | 0.178 | 0.283 | 9 |
| TruthfulQA | 0.182 | 0.224 | 9 |
| BiasEval | 0.196 | 0.045 | 9 |
| TrustLLM-Safety | 0.262 | 0.138 | 9 |
| FaithfulQA | 0.350 | -0.245 | 9 |
| HaluBench | 0.419 | 0.172 | 9 |
| SafetyBench | 0.435 | -0.133 | 9 |
| TrustLLM-Truthfulness | 0.458 | 0.122 | 9 |

**Total Benchmarks:** 10
**CV Range:** [0.130, 0.458]
**Mean ρ Range:** [-0.245, 0.283]

---

## Hypothesis Test Results

### Primary Test: Pearson Correlation
- **Pearson r:** -0.486
- **p-value:** 0.1542
- **95% CI:** [-0.854, 0.207]
- **Sample Size:** 10 benchmarks

### Gate Criteria
- **Target r:** < -0.5 (negative moderate-to-strong correlation)
- **Actual r:** -0.486 ✗
- **Target p:** < 0.05 (statistical significance)
- **Actual p:** 0.1542 ✗

### Interpretation
The hypothesis is **REJECTED**. The correlation (r = -0.486)
does not reach
the required threshold (r < -0.5, p < 0.05).

This indicates that CV is **not a valid predictor** of cross-benchmark stability in this dataset.
The MUST_WORK gate failure requires **routing to Phase 0** for fundamental redesign. Alternative
quality signals or different meta-features should be explored.

---

## Cross-Benchmark Correlation Matrix

Pairwise Spearman ρ between all benchmarks:
                       TruthfulQA  FinTrust  MultiTrust  TrustBench-Ethics  BiasEval  TrustLLM-Safety  HaluBench  FaithfulQA  TrustLLM-Truthfulness  SafetyBench
TruthfulQA               1.000000  0.721429    0.621429           0.510714 -0.032143         0.292857   0.414286   -0.292857               0.157143    -0.378910
FinTrust                 0.721429  1.000000    0.460714           0.567857 -0.042857         0.328571  -0.007143   -0.567857              -0.239286     0.084004
MultiTrust               0.621429  0.460714    1.000000           0.296429  0.435714         0.489286   0.242857   -0.142857               0.282143    -0.141198
TrustBench-Ethics        0.510714  0.567857    0.296429           1.000000 -0.332143         0.414286   0.282143   -0.557143               0.189286     0.253798
BiasEval                -0.032143 -0.042857    0.435714          -0.332143  1.000000        -0.032143   0.300000   -0.157143               0.271429    -0.003575
TrustLLM-Safety          0.292857  0.328571    0.489286           0.414286 -0.032143         1.000000   0.117857   -0.164286               0.064286    -0.268097
HaluBench                0.414286 -0.007143    0.242857           0.282143  0.300000         0.117857   1.000000   -0.167857               0.603571    -0.234138
FaithfulQA              -0.292857 -0.567857   -0.142857          -0.557143 -0.157143        -0.164286  -0.167857    1.000000               0.060714    -0.219839
TrustLLM-Truthfulness    0.157143 -0.239286    0.282143           0.189286  0.271429         0.064286   0.603571    0.060714               1.000000    -0.293119
SafetyBench             -0.378910  0.084004   -0.141198           0.253798 -0.003575        -0.268097  -0.234138   -0.219839              -0.293119     1.000000

---

## Visualizations

The following figures were generated:
1. `figures/cv_vs_rho_scatter.png` - Scatter plot with regression line
2. `figures/cv_rho_per_benchmark_bars.png` - Dual bar chart
3. `figures/pairwise_rho_heatmap.png` - Correlation heatmap
4. `figures/gate_metrics_comparison.png` - Gate threshold comparison

---

## Next Steps

**Gate FAILED** - Route to Phase 0:
- Fundamental redesign required
- Explore alternative quality signals (e.g., score distribution skewness, inter-rater reliability)
- Consider different meta-features for benchmark quality assessment
- Preserve partial results for failure analysis

---

## Artifacts

All analysis artifacts saved to:
- **Data:** `data/benchmark_corpus.pkl`
- **Results:** `results/*.csv`, `results/*.json`
- **Figures:** `figures/*.png`
