# Results

Our experiments reveal strong evidence for enumeration preference in decoder-based reward models, with a surprising architectural boundary: the effect is absent in encoder-only models.

## Main Results: Per-Model Effect Sizes

Table 1 presents Cohen's *d* for each reward model, quantifying the enumeration preference under controlled conditions.

**Table 1: Enumeration Effect Sizes by Reward Model**

| Reward Model | Cohen's *d* | 95% CI | *t*-statistic | *p*-value | *n* |
|--------------|-------------|--------|---------------|-----------|-----|
| ArmoRM | **1.446** | [1.267, 1.626] | 17.81 | 6.89×10⁻⁴⁹ | 300 |
| UltraRM | **0.881** | [0.714, 1.049] | 10.36 | 1.06×10⁻²¹ | 300 |
| Starling-RM | **0.378** | [0.216, 0.539] | 4.83 | 2.22×10⁻⁶ | 300 |
| PairRM | 0.077 | [-0.083, 0.237] | 0.94 | 0.346 | 300 |

**Bold** indicates *d* ≥ 0.3 (exceeds pre-registered threshold)

**Key Observations:**

1. **Three of four models exceed the d=0.3 threshold**, satisfying our primary success criterion of ≥2 architecturally distinct models. This confirms that enumeration preference is not a single-model artifact but a reproducible phenomenon across decoder-based reward models.

2. **Effect sizes span a wide range (d=0.08 to d=1.45)**, suggesting that model architecture and training dynamics modulate the strength of structural encoding. ArmoRM shows a very large effect (d=1.45), while Starling-RM shows a medium effect (d=0.38).

3. **All four models show positive enumeration effects** (d > 0), satisfying our secondary criterion that ≥75% of models exhibit same-sign effects. Even PairRM's non-significant effect is positive in direction.

Figure 1 visualizes these results as a forest plot with the d=0.3 threshold overlay.

![Forest Plot](figures/forest_plot.png)
*Figure 1: Effect sizes (Cohen's d) for enumeration preference across four reward models. Horizontal lines indicate 95% confidence intervals. The dashed vertical line marks the d=0.3 threshold. Three decoder-based models (ArmoRM, UltraRM, Starling-RM) exceed the threshold, while encoder-only PairRM shows no significant effect.*

## Score Distributions

To understand the underlying data, Figure 2 shows violin plots of score distributions by structure for each reward model.

![Violin Plot](figures/violin_plot.png)
*Figure 2: Distribution of normalized reward scores for enumerated (blue) and synthesized (orange) responses. The separation between distributions is most pronounced in ArmoRM and UltraRM, moderate in Starling-RM, and negligible in PairRM.*

**Interpretation:** The decoder-based models show clear separation between enumerated and synthesized score distributions, with enumerated responses consistently scoring higher. PairRM's distributions overlap almost completely, indicating no systematic preference.

## Gate Condition Evaluation

Our pre-registered success criterion requires Cohen's *d* ≥ 0.3 in at least two architecturally distinct reward models.

**Gate Evaluation:**

| Model | Architecture | *d* ≥ 0.3? |
|-------|--------------|------------|
| ArmoRM | Decoder (MoE) | ✓ Yes (1.446) |
| UltraRM | Decoder (Regression) | ✓ Yes (0.881) |
| Starling-RM | Decoder (BT) | ✓ Yes (0.378) |
| PairRM | Encoder (Pairwise) | ✗ No (0.077) |

**Result: PASS** --- Three models exceed the threshold, satisfying the minimum requirement of two.

Figure 3 visualizes the gate condition with effect sizes and threshold overlay.

![Gate Metrics](figures/gate_metrics.png)
*Figure 3: Bar chart showing per-model effect sizes with d=0.3 threshold (dashed line). Three of four models exceed the threshold, satisfying the MUST_WORK gate condition.*

## Aggregate Statistics

Pooling across all four models using random-effects meta-analysis:

| Metric | Value |
|--------|-------|
| Pooled Cohen's *d* | 0.696 |
| Pooled SE | 0.115 |
| 95% CI | [0.471, 0.921] |
| I² (heterogeneity) | 99.1% |
| Cochran's Q | 332.4 (*p* < 0.001) |

**Interpretation:** The pooled effect size (d=0.70) represents a medium-to-large effect, indicating that across diverse reward models, enumerated responses receive substantially higher scores than synthesized alternatives. High heterogeneity (I²=99.1%) is expected given architectural diversity and suggests model-specific factors moderate the effect strength.

## Surprising Finding: The PairRM Non-Effect

One of our most striking findings is that PairRM, the only encoder-based model in our evaluation, shows no significant enumeration preference (d=0.077, p=0.346).

**Mean Scores by Structure:**

| Model | Mean (Enumerated) | Mean (Synthesized) | Difference |
|-------|-------------------|---------------------|------------|
| ArmoRM | 0.646 | 0.397 | +0.250 |
| UltraRM | 0.639 | 0.466 | +0.173 |
| Starling-RM | 0.585 | 0.504 | +0.080 |
| PairRM | 0.538 | 0.527 | +0.011 |

**Our interpretation:** The architectural difference between decoder-only and encoder-only models may explain this divergence. In decoder-only transformers with causal attention, each token's representation is conditioned on all preceding tokens, allowing enumeration markers (e.g., "1.", "2.", "3.") to create cumulative structural signals across the sequence. In contrast, bidirectional encoders like DeBERTa process enumeration markers as local patterns within the full-context representation, without sequential accumulation.

This finding suggests that enumeration preference is not simply a property of RLHF training but depends on how models process sequential structure during inference.

## Factorial Interaction Analysis

Figure 4 shows the interaction between structure and our control variables (correctness, completeness).

![Interaction Plot](figures/interaction_plot.png)
*Figure 4: Interaction plot showing structure effect across correctness and completeness conditions. The enumeration preference is robust across all factorial combinations, with no significant structure × correctness × completeness interaction.*

**Interpretation:** The enumeration preference persists across all combinations of correctness and completeness, indicating that the effect is not confounded with response quality or thoroughness. This supports our claim that enumeration is encoded as an independent structural feature.

## Summary

Our results provide strong evidence for three conclusions:

1. **Existence confirmed:** Decoder-based RLHF reward models exhibit significant enumeration preference (d=0.38-1.45) under controlled conditions.

2. **Cross-model replication:** The effect replicates across three architecturally distinct decoder models (ArmoRM, UltraRM, Starling-RM), ruling out single-model artifacts.

3. **Architecture-conditional:** The effect is absent in encoder-only PairRM, suggesting that causal attention mechanisms contribute to structural encoding.

These findings satisfy our pre-registered success criteria and reveal an unexplored dimension of reward model behavior with implications for RLHF-based alignment.
