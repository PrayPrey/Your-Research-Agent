# Validation Report: h-e1

**Date:** 2026-08-29  
**Hypothesis:** Rankings shift significantly between ImageNet and ImageNet-V2 (Kendall-τ < 0.90 with p < 0.001)  
**Type:** EXISTENCE (PoC)  
**Gate:** MUST_WORK

---

## Executive Summary

**GATE RESULT: FAILED**

The experiment tested whether model rankings shift significantly between ImageNet and ImageNet-V2. Contrary to the hypothesis, rankings are highly preserved (τ = 0.9647) despite substantial accuracy drops (mean 11.68%).

---

## Results

### Primary Metrics

| Metric | Threshold | Actual | Pass? |
|--------|-----------|--------|-------|
| Kendall-τ | < 0.90 | **0.9647** | ❌ |
| p-value | < 0.001 | 1.58e-43 | ✓ |

### Statistical Summary

- **Sample size:** 96 models
- **Kendall-τ:** 0.9647
- **95% CI:** [0.9454, 0.9795]
- **Spearman-ρ:** 0.9964 (confirming strong correlation)
- **Mean accuracy drop:** 11.68%
- **Max rank change:** 9 positions

---

## Interpretation

The hypothesis is **NOT supported**:

1. **High rank correlation:** τ = 0.9647 significantly exceeds the 0.90 threshold. Models that perform well on ImageNet generally also perform well on ImageNet-V2 relative to other models.

2. **Uniform accuracy drop:** While all models experience ~10-14% accuracy drops on V2, this drop is approximately uniform across models. The ranking order is preserved because better models drop by similar absolute percentages.

3. **Statistical power confirmed:** With 96 models and p < 10^-43, we have high confidence in the correlation estimate. The 95% CI [0.9454, 0.9795] entirely excludes values below 0.90.

---

## Gate Decision

**MUST_WORK gate: FAILED**

The core existence hypothesis—that rankings shift significantly—is not supported by the data. Rankings remain stable (τ > 0.94 with high confidence).

### Implications

Per MUST_WORK gate failure protocol:
- The phenomenon (significant rank shifts) does not exist at the hypothesized magnitude
- Downstream hypotheses (h-m1, h-c1, h-c2) depend on existence of rank shifts
- Route back to Phase 2A to reformulate the hypothesis

### Alternative Directions

1. **Lower threshold:** If τ < 0.95 is considered "significant shift", hypothesis would pass (95% CI upper = 0.9795 < 0.98)
2. **Focus on top-K:** Rank stability at top-10 may differ from overall correlation (preview for h-m2)
3. **Architecture-specific analysis:** Some architecture families may show larger rank shifts than others

---

## Artifacts

### Data
- `data/merged_rankings.csv`: 96 models with rankings

### Figures
- `figures/ranking_scatter.png`: ImageNet vs V2 rank scatter plot
- `figures/accuracy_drop.png`: Distribution of accuracy drops
- `figures/gate_metrics.png`: Gate metrics comparison
- `figures/rank_change_distribution.png`: Distribution of rank changes

### Results
- `results.json`: Full statistical results

---

## Conclusion

**Hypothesis h-e1 is NOT SUPPORTED.** Rankings between ImageNet and ImageNet-V2 show Kendall-τ = 0.9647, which exceeds the 0.90 threshold. While models do experience accuracy drops on V2, these drops are approximately uniform, preserving relative rankings.

The MUST_WORK gate fails, indicating the core phenomenon does not exist at the hypothesized level.

---

*Generated: 2026-08-29*
