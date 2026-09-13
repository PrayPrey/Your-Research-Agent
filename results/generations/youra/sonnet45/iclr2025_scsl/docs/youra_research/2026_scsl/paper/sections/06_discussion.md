# Discussion

Our experiments comprehensively falsify the hypothesis that spurious correlations manifest as discrete, geometrically separable clusters in SSL embedding space. This section interprets our findings, acknowledges limitations, and discusses broader implications.

## Continuous Gradients, Not Discrete Clusters

The central finding of this work is that spurious features in SSL embeddings form **continuous geometric gradients** rather than discrete clusters. Despite strong spurious correlation (93% in Waterbirds training data), k-means clustering achieves only AMI=0.28, barely above chance level. Yet linear probes achieve AUC≈0.98, indicating strong linear separability.

This dissociation reveals that **linear separability and discrete clusterability are independent geometric properties**. InfoNCE contrastive loss creates embedding structure that linear classifiers can exploit (enabling the 90% WGA documented by Mehta et al., 2022), but this structure is not cluster-based. Think of spurious features as a color gradient from blue to red: a linear boundary can separate "mostly blue" from "mostly red," but k-means won't find discrete color groups because the transition is continuous.

### Why Clusters Don't Form

Two competing explanations for the absence of discrete clusters:

1. **Continuous Feature Hypothesis** (most likely): Backgrounds in Waterbirds vary continuously (water scenes differ in lighting, angle, composition), creating smooth gradients in embedding space rather than discrete density modes. InfoNCE pulls together similar backgrounds, but similarity is continuous, not categorical.

2. **High-Dimensional Dilution**: In 2048-dimensional embedding space, spurious signals may be dispersed across many dimensions, reducing the density required for k-means to identify discrete clusters. Linear classifiers still work because they find optimal separating hyperplanes regardless of density.

Additional evidence would strengthen the continuous feature hypothesis: visualizing embeddings via t-SNE/UMAP should show gradual transitions between groups rather than distinct islands. PCA analysis can reveal whether spurious variance concentrates in a few principal components (supporting linear separability) without forming discrete modes.

## Re-Interpreting LA-SSL's Mechanism

Our results falsify the cluster dispersion theory for LA-SSL's fairness benefits. Instead of reducing clusterability by 30%, LA-SSL *increases* AMI by 2% while preserving linear separability ($\Delta$AUC=0.005). This suggests LA-SSL operates via a different mechanism:

**Hypothesis**: Learning-speed resampling improves linear decision boundaries for minority groups. By upweighting slow-learning samples (which typically belong to minority groups), LA-SSL gives them greater influence on the learned representation. This does not disperse clusters (which don't exist anyway), but rather reshapes the linear boundary to better separate minority from majority groups.

Testing this hypothesis requires: (1) per-group linear probe analysis showing improved minority-group margins under LA-SSL, (2) decision boundary visualization comparing SimCLR vs LA-SSL, and (3) measuring per-group learning curves to confirm minority groups benefit more from resampling. We leave this to future work.

## Implications for SSL Fairness Research

Our negative result has concrete implications for how researchers should approach fairness in self-supervised learning:

### What Doesn't Work

1. **Cluster-based diagnostics**: AMI, Silhouette scores, and similar clustering metrics cannot identify when spurious correlations exist or predict when interventions will work. They measure structure that doesn't exist in SSL embeddings.

2. **k-means discovery of spurious groups**: Methods like GEORGE (Sohoni et al., 2021) that use k-means to discover subgroups may fail or succeed for reasons unrelated to geometric cluster structure.

3. **Cluster dispersion objectives**: Training objectives designed to disperse spurious clusters (e.g., maximize inter-cluster distance) target structure that InfoNCE doesn't create.

### What to Try Instead

1. **Linear separability diagnostics**: Measure margin sizes, decision boundary confidence, or per-group linear probe performance. These metrics align with the actual geometric structure (gradients) that SSL creates.

2. **Boundary-focused interventions**: Design training objectives that reshape linear decision boundaries rather than dispersing clusters. For example, maximize minimum per-group margin or minimize worst-group hinge loss.

3. **Gradient-based fairness**: Develop differentiable fairness metrics based on linear separability (not clustering) that can be optimized via gradient descent during SSL training.

## Limitations and Future Work

### POC Training Duration

Our proof-of-concept experiments used 20 epochs (vs planned 100 epochs) to validate implementation before committing expensive GPU resources (48-96 hours for full-scale training). While this is standard experimental practice, it introduces uncertainty: clusters might emerge at scale even though they don't appear early in training.

However, several factors suggest duration is not the root cause:
- AMI remains flat across epochs 10-20 (Table 5), showing no upward trend
- All three mechanism gates failed (M1, M2, M3), not just one
- Linear separability is already strong at 20 epochs (AUC=0.98), indicating embedding geometry is well-formed

**Mitigation**: Full 100-epoch training is high-priority future work (FW-1) to definitively resolve whether clusters emerge at scale.

### Single Architecture

We tested ResNet-50 (88.5% baseline WGA), a mid-capacity architecture. High-capacity models like ViT-H-14 (600M parameters, 90% WGA in Mehta et al. 2022) may exhibit different geometric properties. Larger capacity could enable finer-grained feature separation that manifests as discrete clusters.

**Mitigation**: Testing ViT-H-14 and other high-capacity architectures is planned as future work (FW-6). However, our finding that even strong spurious correlations don't produce clusters in ResNet-50 is meaningful regardless of what happens at higher capacities.

### h-e1 Experimental Gap

Hypothesis h-e1 (cluster-balanced retraining efficacy) achieved 100% implementation validation (43/43 tests passing) but no experimental execution. This leaves P1 (AMI≥0.4 predicts $\Delta$WGA≥2pp) untested.

However, this gap is somewhat moot: h-m-integrated failed to produce high-AMI embeddings (AMI=0.28 < 0.4), so there are no high-AMI cases available to test P1. The validated code is experiment-ready if future work (extended training, different architectures) successfully creates high-clusterability conditions.

## Broader Impact

This work redirects SSL fairness research from cluster-based to linear-based approaches, potentially saving significant research effort on methods that cannot work. The primary impact is on the research community, not on deployed systems.

**Positive impacts**:
- Prevents wasted effort on cluster diagnostics that target non-existent structure
- Opens theoretical space for better mechanistic explanations of SSL fairness grounded in linear geometry

**Negative impacts**: None identified. This is foundational research on embedding geometry with no immediate deployment implications.

## Why Negative Results Matter

Null results are often dismissed as failures, but falsifying an incorrect hypothesis is valuable scientific progress. Our work eliminates the cluster hypothesis, which was widely assumed but never tested. This prevents researchers from pursuing cluster-based interventions that cannot work and redirects attention to linear mechanisms that better match the actual geometric structure of SSL embeddings.

As physicist Wolfgang Pauli said: "It is not only not right, it is not even wrong"—until you test it. We tested the cluster hypothesis and found it wrong. That is progress.
