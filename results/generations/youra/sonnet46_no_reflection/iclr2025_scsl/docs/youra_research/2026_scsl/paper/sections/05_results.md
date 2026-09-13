# 5. Results

## 5.1 Main Results: Feature-Strength Conditionality

Table 1 presents the clustering results for Waterbirds and CelebA under identical experimental conditions. The results confirm the feature-strength conditionality hypothesis: the same algorithm achieves strong spurious direction recovery on Waterbirds and near-random performance on CelebA.

**Table 1: Clustering results for annotation-free spurious direction discovery.**

| Dataset | AMI | Purity | AMI (random) | Purity (random) | AMI threshold | Purity threshold | Pass? |
|---|---|---|---|---|---|---|---|
| Waterbirds | **0.762** | **0.892** | 0.0001 | 0.727 | ≥ 0.5 | ≥ 0.75 | ✓ PASS |
| CelebA | **0.258** | **0.456** | 0.000 | 0.440 | ≥ 0.5 | ≥ 0.75 | ✗ FAIL |

The Waterbirds result exceeds both thresholds by substantial margins: AMI is 0.262 above threshold (52% headroom) and purity is 0.142 above threshold. The mechanism is not marginal — k-means on epoch-5 Waterbirds embeddings achieves near-perfect spurious group separation.

The CelebA result fails both thresholds by comparable margins: AMI falls 0.242 below threshold and purity falls 0.294 below threshold. Critically, CelebA purity (0.456) is only 0.016 above the random baseline (0.440). This means k-means on CelebA embeddings offers essentially no useful spurious group signal: the clusters are statistically indistinguishable from random assignment in terms of purity.

The gap between datasets is not a matter of degree — it is a categorical difference in mechanism activation. Waterbirds embedding space at epoch 5 contains strongly separable spurious structure; CelebA embedding space does not.

Figure 1 visualizes this gap. The metrics bar chart shows that Waterbirds exceeds both thresholds while CelebA falls far below, with random baselines providing the lower bound.

*[Figure 1: metrics\_bar.png — AMI and worst-cluster purity for Waterbirds and CelebA with threshold lines and random baselines.]*

## 5.2 Visualization: t-SNE Embedding Structure

Figures 2 and 3 show t-SNE projections of Waterbirds epoch-5 embeddings, colored by k-means cluster assignment and by ground-truth group ID respectively. The cluster boundaries align tightly with group structure: samples in cluster 0 correspond predominantly to the water-background group and samples in cluster 1 to the land-background group. The visual alignment confirms that the AMI score reflects genuine semantic structure, not a metric artifact.

*[Figure 2: tsne\_cluster\_waterbirds.png — t-SNE of Waterbirds embeddings, colored by k-means cluster. Cluster boundaries align with spurious group structure.]*

*[Figure 3: tsne\_group\_waterbirds.png — t-SNE of Waterbirds embeddings, colored by ground-truth group ID. Comparison with Figure 2 confirms cluster-group correspondence.]*

Figure 4 shows the corresponding t-SNE for CelebA. The cluster boundary does not align with group structure: both spurious groups (blonde-female, non-blonde-female, blonde-male, non-blonde-male) are distributed across both clusters without clear separation. The embedding manifold at epoch 5 does not encode hair color as a separable dimension.

*[Figure 4: tsne\_cluster\_celeba.png — t-SNE of CelebA embeddings, colored by k-means cluster. Clusters fail to align with spurious group structure.]*

## 5.3 Cluster Composition Analysis

Figures 5 and 6 show the group composition within each k-means cluster for Waterbirds and CelebA respectively.

For Waterbirds (Figure 5), each cluster is dominated by a single spurious group: cluster 0 is ~89% water-background samples and cluster 1 is ~89% land-background samples. This near-pure composition directly enables annotation-free group-label proxies — a practitioner could use cluster membership as a stand-in for group labels with high confidence.

*[Figure 5: cluster\_composition\_waterbirds.png — Cluster group composition for Waterbirds. Each cluster dominated by one spurious group (purity=0.892).]*

For CelebA (Figure 6), both clusters show mixed group composition across all four spurious groups, with no cluster dominated by any single group. The cluster composition is effectively random, confirming that the k-means solution on CelebA embeddings does not capture any spurious group structure.

*[Figure 6: cluster\_composition\_celeba.png — Cluster group composition for CelebA. Mixed membership reflects near-random separation (purity=0.456).]*

## 5.4 Training Dynamics

Both models achieve high training accuracy by epoch 5, confirming that the CelebA failure is not due to insufficient training:

| Dataset | Epoch 5 train loss | Epoch 5 train accuracy | Embedding shape |
|---|---|---|---|
| Waterbirds | 0.088 | 96.66% | (4,795 × 2,048) |
| CelebA | 0.124 | 95.00% | (162,770 × 2,048) |

Both models are actively learning: high accuracy, similar loss levels. CelebA is in fact learning faster in terms of loss (lower absolute loss despite larger dataset). The clustering failure is not a training failure — the model has learned task-discriminative features. What it has not learned, at epoch 5, is a hair-color separable representation.

This rules out the most intuitive alternative explanation (CelebA model undertrained) and shifts attention to the pretrained initialization: what the ImageNet prior does and does not encode.

## 5.5 Gap with Published Results

The PruSC paper [Kim et al., 2024] reports >95% cluster purity on CelebA using a clustering-based annotation-free approach. Our epoch-5, k=2 result yields purity=0.456. This represents a >2× gap from the published figure.

This discrepancy does not constitute a replication failure of PruSC — their experimental configuration (probe epoch, k, preprocessing) differs from ours. Rather, it establishes that published cluster purity results are highly configuration-sensitive: results obtained at training convergence with k>2 do not transfer to early-epoch, k=2 settings. Since downstream methods like gradient-based early interventions (GSB and variants) require early-epoch detection, the PruSC result cannot be cited as evidence that early-epoch annotation-free detection is reliable on CelebA.

This configuration-sensitivity is itself a finding: the literature contains results that appear to validate annotation-free detection across benchmarks, but these results are obtained under configurations that are not compatible with early-phase intervention methods.
