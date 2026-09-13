# Validation Report: h-m1

## Gate Verdict: ✅ PASS

**Test:** Layer-wise neuron consistency (early > late spurious correlation)
**Result:** p = 0.0028, t = 2.78, d = 0.25
**Conclusion:** Mechanism hypothesis SUPPORTED

## Statistical Test Results

| Metric | Value |
|--------|-------|
| Early Mean (ρ) | 0.003 |
| Late Mean (ρ) | 0.001 |
| Difference | 0.001 |
| t-statistic | 2.78 |
| p-value (one-sided) | 0.0028 |
| Cohen's d | 0.25 |

## Per-Layer Statistics

| Layer | Mean(ρ_j) | Std(ρ_j) | 95% CI |
|-------|----------|----------|--------|
| conv1 | 0.001 | 0.007 | ±0.002 |
| layer1 | 0.004 | 0.006 | ±0.001 |
| layer2 | 0.005 | 0.005 | ±0.001 |
| layer3 | 0.003 | 0.005 | ±0.001 |
| layer4 | 0.000 | 0.005 | ±0.000 |

## Visualizations

1. **Bar Chart:** `figures/layer_correlation_means.png` - Mean ρ_j per layer with 95% CI
2. **Heatmap:** `figures/neuron_correlation_heatmap.png` - Per-neuron correlations
3. **CDF:** `figures/correlation_cdf.png` - Early vs late distribution comparison

## Interpretation

Early layers (conv1, layer1) show significantly higher spurious correlation than late layers (layer3, layer4), supporting the feature complexity hypothesis. Simpler spurious features (color) are learned earlier in the network hierarchy.

## Raw Data Summary

- **Sample Size:** 896 neurons total
  - Early layers: 128 neurons
  - Late layers: 768 neurons
- **Test:** One-sided independent t-test (early > late)
- **Significance Level:** α = 0.05
