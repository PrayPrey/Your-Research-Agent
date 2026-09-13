# Results

Our main finding is that model rankings are highly preserved between ImageNet and ImageNet-V2, with Kendall-τ = 0.9647—substantially above our pre-registered threshold of 0.90. This contradicts our original hypothesis that rankings would shift significantly under distribution shift.

## Main Results

### Ranking Correlation

| Metric | Value | 95% CI |
|--------|-------|--------|
| Kendall-τ | 0.9647 | [0.9454, 0.9795] |
| Spearman-ρ | 0.9964 | — |
| p-value | 1.58 × 10⁻⁴³ | — |

**Interpretation:** The observed τ = 0.9647 indicates near-perfect ranking preservation. The 95% confidence interval [0.9454, 0.9795] lies entirely above our 0.90 threshold, providing strong statistical evidence against our original hypothesis. Spearman-ρ = 0.9964 confirms this finding with an alternative metric.

Figure 1 visualizes the ranking correlation. Points cluster tightly along the diagonal, indicating that a model's rank on ImageNet closely predicts its rank on ImageNet-V2.

![Ranking scatter plot](figures/ranking_scatter.png)
*Figure 1: ImageNet rank vs. ImageNet-V2 rank for 96 models. Points along the diagonal indicate ranking preservation (τ = 0.9647).*

### Hypothesis Test Outcome

Our pre-registered hypothesis (τ < 0.90) is **not supported**. The data strongly favor the null hypothesis that rankings are preserved (τ ≥ 0.90). This is a null result in the sense that our original prediction was falsified—but it is a positive finding for practitioners, as it validates benchmark-based model selection.

## Accuracy Degradation Analysis

Despite ranking stability, models do experience substantial accuracy drops on ImageNet-V2:

| Statistic | Value |
|-----------|-------|
| Mean accuracy drop | 11.68% |
| Median accuracy drop | 11.52% |
| Standard deviation | 1.87% |
| Min drop | 7.4% |
| Max drop | 16.2% |

**Interpretation:** Accuracy drops are substantial (~12% on average) but remarkably uniform across models. This uniformity explains ranking preservation: when all models lose similar percentages, their relative ordering remains unchanged.

Figure 2 shows the distribution of accuracy drops.

![Accuracy drop distribution](figures/accuracy_drop.png)
*Figure 2: Distribution of accuracy drops from ImageNet to ImageNet-V2. The narrow spread (SD = 1.87%) indicates uniform degradation across models.*

## Rank Change Analysis

| Statistic | Value |
|-----------|-------|
| Mean rank change | 2.8 positions |
| Median rank change | 2 positions |
| Max rank change | 9 positions |
| Models with no rank change | 8 (8.3%) |
| Models with ≤3 position change | 72 (75%) |

**Interpretation:** Most models change rank by only 2-3 positions. The maximum rank change of 9 positions (out of 96) is modest. This distribution of small rank changes is consistent with the high τ correlation.

Figure 4 shows the distribution of rank changes.

![Rank change distribution](figures/rank_change_distribution.png)
*Figure 4: Distribution of rank changes. 75% of models change by ≤3 positions; maximum change is 9.*

## Gate Evaluation

Our pre-registered gate metric (τ < 0.90) was not met:

| Metric | Threshold | Actual | Gate Status |
|--------|-----------|--------|-------------|
| Kendall-τ | < 0.90 | 0.9647 | FAILED |
| p-value | < 0.001 | 1.58e-43 | PASSED |

**Interpretation:** The MUST_WORK gate fails because the core phenomenon (significant ranking shift) does not exist at the hypothesized magnitude. This is proper scientific falsification: our hypothesis made a specific, testable prediction (τ < 0.90) that the data refute.

Figure 3 visualizes the gate evaluation.

![Gate metrics](figures/gate_metrics.png)
*Figure 3: Target threshold (τ < 0.90) vs. observed value (τ = 0.9647). The observed correlation substantially exceeds the threshold.*
