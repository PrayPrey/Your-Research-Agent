"""Validation report generator."""
import numpy as np
from scipy import stats as scipy_stats
from typing import Dict
from pathlib import Path


def generate_validation_report(
    t_stat: float,
    p_value: float,
    layer_means: Dict[str, float],
    layer_rho_j: Dict[str, np.ndarray],
    output_path: Path,
    alpha: float = 0.05
):
    """Generate 04_validation.md with gate verdict and statistics."""
    # Gate verdict
    early = np.concatenate([layer_rho_j['conv1'], layer_rho_j['layer1']])
    late = np.concatenate([layer_rho_j['layer3'], layer_rho_j['layer4']])

    early_mean = np.mean(early)
    late_mean = np.mean(late)
    gate_pass = (p_value < alpha) and (early_mean > late_mean)

    # Cohen's d effect size
    early_std = np.std(early)
    late_std = np.std(late)
    pooled_std = np.sqrt((early_std**2 + late_std**2) / 2)
    cohens_d = (early_mean - late_mean) / pooled_std if pooled_std > 0 else 0

    # Build markdown
    report = f"""# Validation Report: h-m1

## Gate Verdict: {'✅ PASS' if gate_pass else '❌ FAIL'}

**Test:** Layer-wise neuron consistency (early > late spurious correlation)
**Result:** p = {p_value:.4f}, t = {t_stat:.2f}, d = {cohens_d:.2f}
**Conclusion:** {'Mechanism hypothesis SUPPORTED' if gate_pass else 'Mechanism hypothesis NOT SUPPORTED'}

## Statistical Test Results

| Metric | Value |
|--------|-------|
| Early Mean (ρ) | {early_mean:.3f} |
| Late Mean (ρ) | {late_mean:.3f} |
| Difference | {early_mean - late_mean:.3f} |
| t-statistic | {t_stat:.2f} |
| p-value (one-sided) | {p_value:.4f} |
| Cohen's d | {cohens_d:.2f} |

## Per-Layer Statistics

| Layer | Mean(ρ_j) | Std(ρ_j) | 95% CI |
|-------|----------|----------|--------|
"""

    for layer_name in ['conv1', 'layer1', 'layer2', 'layer3', 'layer4']:
        mean = layer_means[layer_name]
        std = np.std(layer_rho_j[layer_name])
        ci = 1.96 * scipy_stats.sem(layer_rho_j[layer_name])
        report += f"| {layer_name} | {mean:.3f} | {std:.3f} | ±{ci:.3f} |\n"

    report += f"""
## Visualizations

1. **Bar Chart:** `figures/layer_correlation_means.png` - Mean ρ_j per layer with 95% CI
2. **Heatmap:** `figures/neuron_correlation_heatmap.png` - Per-neuron correlations
3. **CDF:** `figures/correlation_cdf.png` - Early vs late distribution comparison

## Interpretation

{
'Early layers (conv1, layer1) show significantly higher spurious correlation than late layers (layer3, layer4), supporting the feature complexity hypothesis. Simpler spurious features (color) are learned earlier in the network hierarchy.'
if gate_pass else
'No significant difference found between early and late layers. Alternative mechanisms should be investigated.'
}

## Raw Data Summary

- **Sample Size:** {len(early) + len(late)} neurons total
  - Early layers: {len(early)} neurons
  - Late layers: {len(late)} neurons
- **Test:** One-sided independent t-test (early > late)
- **Significance Level:** α = {alpha}
"""

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"Report written to {output_path}")
