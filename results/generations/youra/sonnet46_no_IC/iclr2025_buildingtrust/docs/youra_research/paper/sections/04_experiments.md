# 4. Experimental Setup

## 4.1 Research Questions

We design our experiments to answer four questions that together characterize the trustworthiness correlation structure and its implications:

**RQ1:** Do LLM trustworthiness dimensions exhibit statistically significant pairwise correlations after controlling for model scale and RLHF status? *(Addresses the existence of correlation structure.)*

**RQ2:** Is RLHF fine-tuning the mechanism behind the joint optimization of safety and ethics, as evidenced by within-family comparisons? *(Addresses the causal mechanism driving the cluster.)*

**RQ3:** What is the cluster structure of the 6×6 partial Spearman correlation matrix, and does it match the predicted RLHF-sensitive vs RLHF-insensitive grouping? *(Addresses the 2-cluster structure.)*

**RQ4:** What is the minimum sufficient evaluation set derivable from the MST of the correlation matrix, and how stable is it under bootstrap resampling? *(Addresses the practical evaluation compression.)*

## 4.2 Dataset

**TrustLLM evaluation data.** We use the publicly available TrustLLM benchmark scores [Sun et al., 2024], a 16-model × 6-dimension evaluation matrix. The six dimensions are: truthfulness (T), safety (S), fairness (F), adversarial robustness (R), privacy (P), and machine_ethics (E).

| Property | Value |
|---|---|
| Number of models | 16 |
| Dimensions | 6 |
| Score range | [0, 1] |
| Source | HowieHwong/TrustLLM published Table 1 |

**Why TrustLLM.** TrustLLM is the most comprehensive published multi-dimensional trustworthiness benchmark for text LLMs, with the widest model coverage (7B to ~175B parameters, base and chat variants) and most detailed dimension breakdown. Published scores enable reproducible analysis without re-running evaluations.

**Model annotation.** Each of the 16 models is annotated with:
- `log₁₀(parameter_count)`: log-scaled model size (range: 3.85 to 5.24)
- `is_RLHF`: binary flag (1 = RLHF/instruction fine-tuned; 0 = base model)

| Model family | Base | Chat (RLHF) |
|---|---|---|
| LLaMA-2 | 7B, 13B, 70B | 7B-Chat, 13B-Chat, 70B-Chat |
| Vicuna | — | 7B, 13B |
| Mistral | 7B | — |
| ChatGLM, Baichuan, WizardLM | various | — |
| Proprietary | — | Claude-2, GPT-3.5-turbo, GPT-4 |

## 4.3 Baselines

To contextualize our partial correlation findings, we compare against three baselines:

**Raw Spearman correlation.** The same pairwise analysis without controlling for scale and RLHF — shows what analysis naively applied to the data would find. Expected to show mostly positive correlations due to scale confound.

**Scale-only control.** Partial correlation controlling for log₁₀_params only (not RLHF) — isolates the RLHF-specific contribution to the correlation structure.

**Capability benchmark baseline.** General capability benchmarks have median Spearman ρ = 0.73 (Epoch AI, 17 benchmarks) — provides the reference point for comparing trustworthiness dimension correlations against the known high-correlation capability baseline.

## 4.4 Implementation Details

**Language:** Python 3.10. Libraries: scipy 1.11 (hierarchical clustering, statistical tests), networkx 3.1 (MST), numpy 1.25 (bootstrap), sklearn 1.3 (silhouette score with precomputed distances).

**Statistical setup:**
- Partial Spearman: OLS residualization approach (H-E1 implementation)
- Multiple comparison correction: Bonferroni (α/15 = 0.0033; conservative)
- Significance threshold: |ρ_partial| > 0.5 AND p < 0.0033
- Bootstrap: np.random.default_rng(seed=42), 1000 resamples of 14/16 models (row bootstrap)

**Clustering:** scipy.cluster.hierarchy.linkage with Ward, average, and complete methods applied to the precomputed distance matrix d(i,j) = 1 − |ρ_partial(i,j)|. Sklearn Ward with precomputed matrices is avoided due to sklearn issue #27655.

**MST:** networkx.minimum_spanning_tree (Kruskal algorithm) on the 6×6 distance graph.

**Within-family RLHF experiment:** Paired comparison of LLaMA-2 7B/13B/70B base vs chat variants on dimensions {safety, machine_ethics, robustness}. Signed delta test for each pair. Binary sign test (n=3) to assess joint optimization.

All analysis code is designed for reproducibility with the published TrustLLM Table 1 scores as input.

## 4.5 Evaluation Metrics

| Metric | Definition | Connection to claims |
|---|---|---|
| ρ_partial | Partial Spearman correlation, controlling for log₁₀_params and is_RLHF | Tests RQ1 — whether dimensions are independently correlated |
| Significance (Bonferroni) | p < 0.0033 for each pair | RQ1 — whether correlation exceeds noise threshold |
| Silhouette score (k=2) | Ratio of between-cluster to within-cluster distance | RQ3 — quality of 2-cluster partition |
| Cluster membership alignment | Fraction of dimensions correctly assigned to predicted RLHF-sensitive/insensitive clusters | RQ3 — whether cluster matches RLHF mechanism prediction |
| MST min set size | Number of hub nodes in minimum spanning tree | RQ4 — evaluation compression |
| Mean per-edge bootstrap frequency | Average fraction of bootstrap MSTs containing each MST edge (Tumminello 2007) | RQ4 — stability of MST topology |
| Δ_d (within-family) | Chat score minus Base score for each LLaMA-2 pair | RQ2 — whether RLHF jointly optimizes safety and ethics |
