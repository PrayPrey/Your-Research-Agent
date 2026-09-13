# Validation Report: H-M3 Query Complexity Attention

**Hypothesis**: Simple queries show higher query-token attention concentration than complex queries.
**Date**: 2026-08-20

## Gate Decision

**Result**: FAIL

No significance (p=0.9537) or wrong direction (Δ=-0.003)

## Results

| Metric | Simple | Complex | Difference |
|--------|--------|---------|------------|
| Mean Concentration | 0.020 | 0.023 | -0.003 |
| 95% CI | [0.017, 0.022] | [0.020, 0.025] | - |
| t-statistic | -1.690 | - | - |
| p-value | 0.9537 | - | - |
| Cohen's d | -0.242 | - | - |

## Sample Sizes

- Simple queries: 98
- Complex queries: 100

## Figures

### Bar Chart
![Bar Chart](../figures/bar_chart.png)

### Distributions
![Distributions](../figures/distributions.png)

### Scatter Plot
![Scatter](../figures/scatter.png)

### Boxplots
![Boxplots](../figures/boxplots.png)

## Interpretation

Hypothesis not validated. Fallback to uniform tiering recommended.

## Implementation Notes

- Entity classification: spaCy NER en_core_web_sm
- Attention extraction: Llama-2-7B last layer, averaged across heads
- Statistical test: Two-sample t-test with alternative='greater'
- Effect size: Cohen's d = -0.242

## Next Steps

Document uniform tiering as fallback. Core eviction mechanisms (H-M1, H-M4) remain valid.
