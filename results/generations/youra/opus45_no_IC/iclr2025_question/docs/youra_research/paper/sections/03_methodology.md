# Methodology

Our approach has three stages: (1) compute semantic entropy distributions per benchmark, (2) cluster benchmarks by JS-divergence, and (3) evaluate transfer success within and across clusters. This design directly tests our hypothesis that distribution similarity predicts transfer success.

## Semantic Entropy Computation

Following Kuhn et al. (2023), we compute semantic entropy for each query as follows:

**Generation.** For each query $q$, we generate $N=10$ responses $\{r_1, \ldots, r_N\}$ using temperature $T=0.7$ sampling from Llama-2-7B-Chat.

**Semantic clustering.** We cluster responses by meaning using bidirectional entailment. Two responses $r_i, r_j$ belong to the same semantic cluster if $\text{NLI}(r_i, r_j) = \text{ENTAILMENT}$ and $\text{NLI}(r_j, r_i) = \text{ENTAILMENT}$, using DeBERTa-v3-large-MNLI as the NLI model.

**Entropy computation.** Let $C_1, \ldots, C_k$ be the semantic clusters with empirical probabilities $p_c = |C_c|/N$. Semantic entropy is:
$$
H_{\text{sem}}(q) = -\sum_{c=1}^{k} p_c \log p_c
$$

High entropy indicates diverse semantic content across generations (hallucination signal); low entropy indicates consistent responses (likely correct).

## Distribution Distance via JS-Divergence

To quantify similarity between benchmark uncertainty distributions, we use Jensen-Shannon divergence. For benchmarks $B_i$ and $B_j$ with semantic entropy distributions $P_i$ and $P_j$:

$$
\text{JS}(P_i \| P_j) = \frac{1}{2} D_{\text{KL}}(P_i \| M) + \frac{1}{2} D_{\text{KL}}(P_j \| M)
$$

where $M = \frac{1}{2}(P_i + P_j)$.

We estimate distributions using kernel density estimation (KDE) with Gaussian kernels over the entropy values for each benchmark. JS-divergence is symmetric, bounded in $[0, 1]$, and interpretable: values near 0 indicate similar distributions; values near 1 indicate dissimilar distributions.

Figure 1 shows the resulting $6 \times 6$ JS-divergence matrix across our benchmark suite.

## Hierarchical Clustering

We discover benchmark families using hierarchical agglomerative clustering with Ward linkage on the JS-divergence matrix. This approach:

- Does not require pre-specifying the number of clusters
- Produces interpretable dendrograms showing cluster hierarchy
- Uses Ward linkage to minimize within-cluster variance

We select the optimal cluster count by maximizing silhouette score, which measures how similar each benchmark is to its own cluster versus other clusters.

## Transfer Evaluation Protocol

To test whether cluster membership predicts transfer success, we use a calibration-transfer protocol:

**Threshold calibration.** For source benchmark $B_s$, we split data 70/30 into calibration and held-out sets. We calibrate a threshold $\tau_s$ to achieve 10% false positive rate on the calibration set.

**Transfer evaluation.** We apply threshold $\tau_s$ to target benchmark $B_t$ and measure AUROC. Transfer degradation is:
$$
\Delta_{\text{AUROC}} = \text{AUROC}(B_s) - \text{AUROC}(B_t | \tau_s)
$$

**Within-cluster transfer.** For benchmark pairs in the same cluster, we expect low degradation ($\leq 0.08$).

**Cross-cluster transfer.** For benchmark pairs in different clusters, we expect high degradation ($> 0.15$).

## Experimental Design Summary

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Model | Llama-2-7B-Chat | Open-weight, logit access, representative of 7B class |
| Generations | N=10 per query | Within standard range (5-20) |
| Temperature | T=0.7 | Balance diversity and coherence |
| NLI model | DeBERTa-v3-large-MNLI | ~90% MNLI accuracy |
| Distance | JS-divergence | Symmetric, bounded, interpretable |
| Clustering | Hierarchical/Ward | No pre-specified k; interpretable |
| Transfer threshold | FPR=10% calibration | Standard operating point |

This methodology directly tests whether distribution similarity (operationalized via JS-divergence) predicts transfer success (operationalized via AUROC degradation). The hierarchical clustering discovers structure without imposing assumptions about cluster count, and the transfer protocol provides quantitative degradation measurements.
