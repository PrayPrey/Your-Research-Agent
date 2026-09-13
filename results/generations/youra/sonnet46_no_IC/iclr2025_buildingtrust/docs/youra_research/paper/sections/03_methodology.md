# 3. Methodology

Our goal is to characterize the correlation structure of LLM trustworthiness dimensions after removing the effect of two known confounds: model scale and RLHF alignment status. The key design principle is **confound removal before structure discovery**: raw Spearman correlations would show mostly positive values because larger, better-trained models score higher on all dimensions — masking the genuine trustworthiness geometry. Figure 1 illustrates the difference between raw and partial correlation heatmaps.

## 3.1 Data

**Dataset.** We use TrustLLM [Sun et al., 2024] published evaluation scores: a 16-model × 6-dimension matrix with dimensions {truthfulness (T), safety (S), fairness (F), adversarial robustness (R), privacy (P), machine_ethics (E)}. Scores are published as normalized values in [0, 1] and represent the fraction of benchmark items on which a model meets the threshold for that dimension. We load these from the published Table 1 values.

**Models.** The 16-model set spans a range of scales (~7B to ~175B parameters) and alignment approaches, including base models (LLaMA-2 7B/13B/70B, Falcon-7B, Mistral-7B) and RLHF-fine-tuned chat/instruct variants (LLaMA-2-7B-Chat, -13B-Chat, -70B-Chat, Vicuna-7B/13B, ChatGLM, Baichuan, WizardLM, Claude-2, GPT-3.5-turbo, GPT-4). Each model is annotated with log₁₀(parameter_count) and a binary is_RLHF flag (1 = RLHF/instruction fine-tuned, 0 = base).

**VIF Check.** Variance inflation factors for the two covariates are VIF(log₁₀_params) = 3.37, VIF(is_RLHF) = 3.37, confirming acceptable collinearity (< 5) for partial correlation analysis with df = 12.

## 3.2 Partial Spearman Correlation via OLS Residualization

Building on our observation that scale and RLHF status confound raw correlations, we compute partial Spearman correlations using OLS residualization [Kendall & Stuart, 1979]:

**Algorithm 1:** Partial Spearman via OLS Residualization
```
for each dimension d ∈ {T, S, F, R, P, E}:
    rank_d ← scipy.stats.rankdata(scores[:, d])
    residual_d ← OLS(rank_d ~ log10_params + is_RLHF).resid

for each pair (i, j):
    ρ_partial(i,j) ← scipy.stats.spearmanr(residual_i, residual_j).statistic
    t_stat ← ρ_partial * sqrt((n-2) / (1 - ρ_partial²))  ; df = n-2 = 14
    p_value ← 2 * scipy.stats.t.sf(|t_stat|, df=14)
```

**Rationale for OLS residualization.** Direct partial correlation formulas (e.g., pingouin) use df = n − k − 2 for k covariates, giving df = 12. The OLS residualization approach uses df = n − 2 = 14, yielding slightly higher statistical power. We adopt OLS residualization (as implemented in H-E1) but note that the Bonferroni threshold (α/15 = 0.0033) is conservative enough that the df difference does not affect our significance conclusions.

**Bonferroni correction.** With 15 pairwise comparisons, we apply Bonferroni correction: α_corrected = 0.05/15 = 0.0033. This is conservative; significant findings at this threshold have strong evidence.

## 3.3 Hierarchical Clustering

To characterize the cluster structure of the 6×6 partial correlation matrix, we construct a distance matrix:

d(i, j) = 1 − |ρ_partial(i, j)|

and apply three linkage methods — Ward, average, and complete — to assess robustness. We use `scipy.cluster.hierarchy.linkage` with the `precomputed` distance matrix directly. **Critical implementation note:** `sklearn.cluster.AgglomerativeClustering` with Ward linkage does not support precomputed distance matrices (sklearn GitHub issue #27655). We use scipy's hierarchical clustering throughout.

Cluster quality is assessed via silhouette score (`sklearn.metrics.silhouette_score` with precomputed distance matrix). We evaluate k ∈ {2, 3, 4} and report silhouette for each.

## 3.4 Minimum Spanning Tree and Evaluation Set

The MST of the distance matrix d(i,j) identifies the minimum set of edges connecting all 6 dimensions. **Rationale:** in a correlation network, dimensions connected by short MST edges (high |ρ|) are redundant for evaluation purposes — knowing one predicts the other. The hub nodes (high degree in MST) constitute the minimum evaluation set, as they are most informative for spanning the correlation space.

```
G ← networkx.Graph(edge_weight = d(i,j) for all i≠j)
MST ← networkx.minimum_spanning_tree(G, algorithm='kruskal')
min_eval_set ← {d : degree_MST(d) > 1}  # Hub nodes
```

**Bootstrap stability** (Tumminello, 2007). We assess MST topology stability by bootstrap resampling: sample 14 of 16 models × 1000 iterations, compute MST for each, report per-edge frequency (fraction of bootstrap MSTs containing each edge). Following Tumminello (2007), we use mean per-edge bootstrap frequency as the stability metric, with threshold ≥ 0.90.

## 3.5 RLHF Mechanism: Within-Family Natural Experiment

To test whether RLHF is mechanistically responsible for the correlation cluster, we exploit the LLaMA-2 within-family design: three base–chat pairs (7B, 13B, 70B) that share identical architecture and differ only in RLHF fine-tuning. For each pair, we compute:

Δ_d = score_Chat(d) − score_Base(d)  for d ∈ {safety, machine_ethics, robustness}

We test whether RLHF jointly increases safety AND machine_ethics using a sign test (n = 3 pairs). The binary sign test is the appropriate statistic for n = 3 (minimum achievable p = 0.125). For adversarial robustness, we test whether Δ_robustness ≤ 0.

Figure 1 shows the raw vs partial Spearman heatmaps for the full 6×6 matrix, with Figure 4 illustrating OLS residualization for the highest-correlation pair (safety–privacy, ρ = 0.971).
