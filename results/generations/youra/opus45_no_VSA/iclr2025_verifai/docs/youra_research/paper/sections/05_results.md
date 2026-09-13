# Results

We present evidence for the ordering effect (RQ1) and its mechanism (RQ2).

## Main Results (RQ1)

Table 1 presents our primary comparison between static→execution (Condition A) and execution→static (Condition B) orderings.

**Table 1: Main Results on HumanEval + MBPP**

| Condition | pass@1 | 95% CI |
|-----------|--------|--------|
| Static→Execution (A) | **55.57%** | — |
| Execution→Static (B) | 43.07% | — |
| **Relative Improvement** | **29.02%** | [15.74%, 44.53%] |
| McNemar p-value | 6.31×10⁻⁶ | — |

**Key Observations:**

1. **Large effect size:** Static→execution ordering achieves 29.02% relative improvement over execution→static ordering. This nearly doubles our 15% success threshold and substantially exceeds prior self-repair improvements of 10-17%.

2. **Strong statistical significance:** McNemar's paired test yields p = 6.31×10⁻⁶, far below the α = 0.05 threshold. The 95% bootstrap CI [15.74%, 44.53%] excludes zero by a wide margin.

3. **Matched content control:** Both conditions received byte-identical feedback content. The 12.5 percentage point absolute improvement (55.57% vs 43.07%) stems purely from presentation order.

This confirms our primary hypothesis: feedback ordering independently affects repair quality, even when content is identical.

## Mechanism Analysis (RQ2)

We test two candidate mechanisms for the ordering effect.

### H-M1: Early-Gain Amplification

If static-first scaffolds repair, we would expect larger gains in early iterations:

**Table 2: Early Iteration Gains**

| Condition | pass@iter1 | pass@iter2 | ΔPass₁→₂ |
|-----------|------------|------------|----------|
| Static-First (A) | 34.49% | 46.99% | **12.50%** |
| Exec-First (B) | 20.63% | 32.68% | 12.05% |
| Difference | — | — | +0.45pp |
| McNemar p-value | — | — | 0.859 |

**Finding:** Early gains are nearly identical between conditions (+0.45 percentage points, p = 0.859). The scaffolding effect does **not** operate by accelerating early progress.

### H-M2: Regression Prevention

If static-first stabilizes repair trajectories, regression rates should be lower:

**Table 3: Regression Rates**

| Condition | Regression Rate₁→₂ | Relative Reduction |
|-----------|-------------------|-------------------|
| Static-First (A) | **21.53%** | — |
| Exec-First (B) | 34.69% | — |
| Difference | 13.15pp | **38%** |
| McNemar p-value | 0.0198 | — |

**Finding:** Static-first ordering reduces regression rate by 38% (21.53% vs 34.69%, p = 0.0198). Previously passing tests are significantly more likely to stay passing when static feedback appears first.

Figure 1 visualizes the regression rate comparison.

![Regression Rate Comparison](figures/regression_bar.png)

*Figure 1: Regression rates between iterations 1 and 2. Static-first ordering (left) exhibits 38% lower regression rate than execution-first ordering (right).*

### Mechanism Summary

| Mechanism | Prediction | Result | Verdict |
|-----------|------------|--------|---------|
| H-M1: Early-gain amplification | ΔPass₁→₂(A) > ΔPass₁→₂(B) | +0.45pp, p=0.859 | **Not supported** |
| H-M2: Regression prevention | RegRate(A) < RegRate(B) | -13.15pp, p=0.0198 | **Supported** |

The effect operates through trajectory stabilization, not acceleration. Static-first ordering doesn't help the LLM repair faster—it helps it repair more stably.

## Trajectory Visualization

Figure 2 shows the per-iteration pass rate trajectories for both conditions.

![Iteration Trajectory](figures/iteration_trajectory.png)

*Figure 2: Per-iteration pass rates for static-first (blue) and execution-first (orange) conditions. Static-first maintains higher pass rates throughout, with the gap widening after iteration 2 due to lower regressions.*

The divergence between conditions increases after iteration 1, consistent with the regression prevention mechanism: static-first repairs accumulate fewer setbacks over multiple iterations.

## Effect Size Interpretation

**Primary effect (h-e1):** Large. The 29% relative improvement far exceeds both our 15% threshold and the 10-17% range observed in prior self-repair studies. This suggests ordering is a first-order variable in feedback-driven repair.

**Mechanism effect (h-m2):** Moderate. The 13.15 percentage point (38% relative) regression reduction is statistically significant and mechanistically interpretable, but smaller than the primary effect. Other factors may contribute.

**Null mechanism (h-m1):** Negligible. The 0.45 percentage point difference in early gains is indistinguishable from noise. Early-gain amplification is not the operative mechanism.
