# H-M5 Validation Report

**Date:** 2026-08-10
**Hypothesis:** Concentration-diversity cycle reinforces itself via positive feedback loop
**Gate Type:** SHOULD_WORK
**Gate Result:** **FAIL**

---

## Executive Summary

H-M5 tested whether benchmark concentration (HHI) temporally precedes and predicts diversity decline (entropy) using lagged panel regression with fixed effects. **The gate failed**: the coefficient on lagged HHI was positive (not negative as required) and statistically insignificant (p=0.098 > 0.05).

**Interpretation:** There is no evidence that high concentration in year t-1 predicts lower diversity in year t. The strong negative correlation found in H-M4 (ρ=-0.958) is contemporaneous, not temporally ordered. This refutes the causal feedback loop hypothesis.

---

## Gate Evaluation

### Primary Gate Condition

| Criterion | Required | Observed | Status |
|-----------|----------|----------|--------|
| β(HHI_{t-1}) | < 0 | **+1.603** | ❌ FAIL |
| p-value | < 0.05 | **0.098** | ❌ FAIL |

### Secondary Gate Condition (Granger Causality)

| Test | Required | Observed | Status |
|------|----------|----------|--------|
| HHI → entropy (any lag p<0.05) | Yes | **0 venues** | ❌ FAIL |
| Entropy → HHI (no reverse) | p > 0.05 | **0 venues tested** | ⚠️ N/A |

**Note:** Granger tests could not run due to insufficient per-venue observations (7 years per venue, need at least 4 + maxlag=2).

---

## Model Results

### Primary Model: Panel OLS with Two-Way Fixed Effects

```
Entropy_{it} = α_i + γ_t + β₁·HHI_{i,t-1} + β₂·PaperCount_{it} + ε_{it}
```

| Parameter | Estimate | 95% CI | p-value |
|-----------|----------|--------|---------|
| β(HHI_{t-1}) | 1.603 | [-0.37, 3.58] | 0.098 |
| R² | 0.682 | - | - |
| N | 18 | - | - |

**Clustered standard errors by entity (venue).**

### Baseline Model: Pooled OLS (No Fixed Effects)

| Parameter | Estimate | p-value |
|-----------|----------|---------|
| β(HHI_{t-1}) | 1.561 | 0.106 |
| R² | 0.756 | - |

### Robustness Checks

| Specification | β(HHI) | p-value | R² |
|---------------|--------|---------|-----|
| Lag-2 (HHI_{t-2}) | 0.457 | 0.441 | 0.529 |
| Entity-only FE | 2.935 | <0.001 | 0.826 |
| Delta spec (ΔHHI → ΔEntropy) | 0.580 | 0.770 | 0.007 |

**Entity-only FE shows strong positive relationship** - when removing time effects, higher lagged HHI predicts *higher* entropy (opposite of hypothesis). This suggests the H-M4 negative correlation is driven by common time trends, not causal feedback.

---

## Granger Causality Results

Granger tests require minimum 4 observations per time series. With 7 years per venue and maxlag=2, only 4-5 observations available per test — insufficient statistical power.

| Direction | Venues Tested | Significant (p<0.05) |
|-----------|---------------|----------------------|
| HHI → Entropy | 0 | 0 |
| Entropy → HHI | 0 | 0 |

---

## Data Summary

- **Panel Structure:** 3 venues × 7 years = 21 venue-years
- **After lag-1 drop:** 18 observations (first year per venue dropped)
- **After lag-2 drop:** 15 observations

### Limitations

1. **Small N:** 18 observations limits statistical power
2. **Wide CIs:** 95% CI spans zero: [-0.37, 3.58]
3. **Granger infeasible:** Insufficient time series length per venue

---

## Figures Generated

| Figure | Path | Description |
|--------|------|-------------|
| Gate Metrics | figures/gate_metrics.png | β coefficient with 95% CI |
| Scatter Plot | figures/hhi_entropy_scatter.png | HHI_{t-1} vs Entropy_t by venue |
| Time Series | figures/time_series.png | HHI and entropy trends per venue |
| Granger Heatmap | figures/granger_heatmap.png | p-values (empty due to insufficient data) |
| Residuals | figures/residual_diagnostics.png | QQ plot + residuals vs fitted |

---

## Conclusion

**Gate Status: FAIL**

The hypothesis that concentration temporally precedes and causes diversity decline is **not supported**. The positive coefficient suggests, if anything, that higher past concentration predicts *higher* future diversity — the opposite of the feedback loop hypothesis.

**Recommended Action:** Per PRD, report H-M4 finding as correlation only. Abandon causal claim about concentration-diversity feedback loop.

---

## Files Generated

- `h-m5/code/analyze.py` - Main analysis script
- `h-m5/code/data_loader.py` - Panel data loading
- `h-m5/code/models.py` - Regression models
- `h-m5/code/granger.py` - Granger causality tests
- `h-m5/code/visualize.py` - Figure generation
- `h-m5/results/h_m5_results.json` - Structured results
- `h-m5/figures/*.png` - 5 visualization figures
