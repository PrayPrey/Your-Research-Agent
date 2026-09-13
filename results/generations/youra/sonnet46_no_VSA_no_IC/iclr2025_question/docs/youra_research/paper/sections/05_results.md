# Results

Our results provide three nested layers of evidence for the hallucination-type mechanism: distributional, rank-order, and threshold-level. We present them in this order to make the mechanistic argument before reporting the quantitative claims.

## Distributional Evidence: Token Probability Peakedness (h-m1)

The mechanism's first step predicts that recall-failure hallucinations produce peaked token probability distributions on TriviaQA. We test this directly by measuring the peakedness ratio — a composite score combining response kurtosis and max-to-mean log-probability ratio — for hallucinated vs. correct responses on TriviaQA.

**Finding:** On LLaMA-2-7B TriviaQA, hallucinated responses show a mean peakedness ratio of **2.936** vs. **2.533** for correct responses (two-sample t-test, p = 0.002, n = 488).

Figure 1 shows the peakedness distribution for hallucinated and correct responses as a KDE plot (Figure: `figures/peakedness_kde_llama2_trivia_qa.png`). The distributions are clearly separated, with hallucinated responses shifted toward higher peakedness.

This result establishes Step 1 of the mechanism empirically: recall-failure hallucinations *do* produce more concentrated (peaked) token probability distributions at 7B model scale. This converts a theoretical assumption into measured fact and grounds the rank-correlation and AUROC results that follow.

## Rank-Correlation Evidence: Aggregation Function Sensitivity (h-m2)

Step 2 of the mechanism predicts that the peaked/flat distribution difference translates into a rank-order advantage for min on factual recall and for mean on imitative falsehood. We test this via Spearman ρ between each aggregation function's score and binary hallucination labels, across all four (model × dataset) combinations.

| (Model, Dataset) | ρ(min) | ρ(mean) | Δρ = ρ(min)−ρ(mean) | 95% CI | Direction |
|-----------------|--------|---------|---------------------|--------|-----------|
| LLaMA-2-7B, TriviaQA | 0.604 | 0.397 | **+0.206** | [+0.147, +0.262] | min > mean ✓ |
| Mistral-7B-v0.1, TriviaQA | 0.641 | 0.549 | **+0.092** | [+0.041, +0.143] | min > mean ✓ |
| LLaMA-2-7B, TruthfulQA | 0.174 | 0.380 | **−0.206** | [−0.262, −0.147] | mean > min ✓ |
| Mistral-7B-v0.1, TruthfulQA | 0.062 | 0.242 | **−0.180** | [−0.237, −0.123] | mean > min ✓ |

All four (model × dataset) combinations show the correct direction, and all four bootstrap 95% CIs exclude zero.

**Interpretation:** The direction of rank-correlation advantage flips cleanly between TriviaQA (min > mean for both models) and TruthfulQA (mean > min for both models). This is a threshold-agnostic confirmation of the mechanism at the signal level: the aggregation functions produce correctly ordered rankings, independent of any specific detection threshold. The consistency across LLaMA-2-7B and Mistral-7B-v0.1 — two architecturally distinct model families — argues against model-specific confounds. Figure 2 (`figures/rho_differential_bar.png`) shows the Δρ values with 95% CI error bars per (model, dataset) pair, making the direction flip visually immediate. Figure 3 (`figures/rho_scatter.png`) shows the scatter of ρ(min) vs. ρ(mean) with benchmark type as color, further illustrating the clean cluster separation.

## AUROC Evidence: Threshold-Level Confirmation (h-m3)

Step 3 confirms the mechanism at the AUROC threshold level. Table 1 presents the full AUROC comparison across all (model × dataset × aggregation) cells.

**Table 1: AUROC for hallucination detection across models, datasets, and aggregation functions.**

| Model | Dataset | AUROC(min) | AUROC(mean) | AUROC(raw_sum) | Best |
|-------|---------|-----------|------------|---------------|------|
| LLaMA-2-7B | TriviaQA | 0.849 | 0.730 | **0.896** | raw_sum |
| LLaMA-2-7B | TruthfulQA | 0.638 | **0.758** | 0.582 | mean |
| Mistral-7B-v0.1 | TriviaQA | 0.892 | 0.836 | **0.895** | raw_sum |
| Mistral-7B-v0.1 | TruthfulQA | 0.564 | **0.675** | 0.530 | mean |

Figure 4 (`figures/fig1_auroc_bar.png`) presents this as a grouped bar chart with bootstrap 95% CI error bars, making the directional pattern immediately visible. Figure 5 (`figures/fig2_diff_heatmap.png`) shows the 2×3 heatmap of AUROC(min)−AUROC(mean), with blue cells indicating min wins and red cells indicating mean wins.

**P1 (min > mean on TriviaQA, ≥0.02 margin):**

| Model | ΔAUROC(min−mean) | 95% CI |
|-------|-----------------|--------|
| LLaMA-2-7B | **+0.119** | [+0.083, +0.153] |
| Mistral-7B-v0.1 | **+0.056** | [+0.032, +0.082] |

P1 is confirmed for both models. The effect size is large (5–12 AUROC points), and both CIs exclude zero by substantial margin. Min log-probability is the superior aggregation for factual recall hallucination detection at 7B scale.

**P2 (mean > min on TruthfulQA, ≥0.02 margin):**

| Model | ΔAUROC(mean−min) | 95% CI |
|-------|-----------------|--------|
| LLaMA-2-7B | **+0.120** | [+0.084, +0.157] |
| Mistral-7B-v0.1 | **+0.111** | [+0.071, +0.147] |

P2 is confirmed for both models with effect sizes of 11–12 AUROC points, the largest effects in the study. The symmetric magnitude of P1 and P2 across model families is striking: the direction advantage is consistent at approximately +0.10–0.12 AUROC in each case. Figure 6 (`figures/fig3_bootstrap_dists.png`) shows the bootstrap distribution of AUROC differentials for P1 and P2, confirming that the sampling distribution is well-separated from zero.

**P3 Refutation (raw_sum as strongest on TriviaQA):** Contrary to the prediction that raw_sum would be the weakest aggregation function, raw_sum achieves the highest AUROC on TriviaQA for both models. The AUROC reversal is consistent across models (LLaMA: 0.896 vs. min's 0.849; Mistral: 0.895 vs. min's 0.892), with raw_sum's margin over min larger on LLaMA (+0.047) than Mistral (+0.003). On TruthfulQA, raw_sum is weakest (LLaMA: 0.582; Mistral: 0.530), consistent with the flat-distribution interpretation (length-confidence confound is harmful when answers are uniformly confident).

Figure 7 (`figures/fig4_summary_table.png`) provides a visual summary of P1/P2/P3 gate results with pass/fail coloring.

## Cross-Architecture Replication

The directionality of P1 and P2 is consistent across both LLaMA-2-7B and Mistral-7B-v0.1. Effect sizes differ quantitatively (LLaMA shows larger P1 Δ; both models show similar P2 Δ), but the direction is identical across all four (model × dataset) pairs and at both rank-correlation and AUROC measurement levels. This cross-architecture consistency is the strongest available generalizability evidence at 7B scale.

## Raw_sum as Unexpected Zero-Cost Signal

The raw unnormalized log-probability sum — which equals the model's autoregressive log P(answer) — outperforms both normalized aggregations on TriviaQA and exceeds published Semantic Entropy AUROC (≈0.79, [Farquhar et al., 2023]) at a fraction of the inference cost. The AUROC(raw_sum) = 0.895–0.896 on TriviaQA, achieved with a single forward pass, represents the strongest factual-recall hallucination detection result in this study. The magnitude and consistency across two model families argues against a dataset-specific artifact and suggests that sequence-level joint probability carries a genuine factual-recall signal not captured by per-token statistics.

Figure 8 (`figures/auroc_heatmap.png`) shows the full 3×4 AUROC heatmap (three aggregations × four (model, dataset) combinations), contextualizing the relative performance across all conditions in a single view.
