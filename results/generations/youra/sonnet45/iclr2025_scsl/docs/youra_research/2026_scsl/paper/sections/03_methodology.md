# Methodology

Building on our hypothesis that spurious correlations manifest as discrete, geometrically separable clusters in SSL embedding space, we design a three-stage experimental framework to test: (M1) whether InfoNCE loss creates dense spurious clusters, (M2) whether clusterability predicts intervention efficacy, and (M3) whether LA-SSL disperses clusters while preserving separability.

## Problem Formulation

Consider a dataset $\mathcal{D} = \{(x_i, y_i, g_i)\}_{i=1}^N$ where $x_i$ is an input image, $y_i$ is the label, and $g_i$ is the spurious group (unobserved during training). A spurious correlation exists when a feature $s$ (e.g., background type) correlates strongly with $y$ but is not causally related to the prediction task. In Waterbirds, $s$ is background (land/water), $y$ is bird type (landbird/waterbird), and the spurious correlation is 93% in training data.

Our goal is to test whether SSL embeddings $z = f_\theta(x)$ learned via InfoNCE loss exhibit:
1. **High clusterability**: Spurious groups form geometrically separable clusters measurable by AMI $\geq$ 0.4
2. **Diagnostic power**: AMI predicts whether cluster-balanced retraining improves worst-group accuracy
3. **Dispersion under LA-SSL**: Learning-speed resampling reduces AMI by $\geq$ 30% while preserving linear separability

## Clusterability Measurement

### Adjusted Mutual Information (AMI)

We measure embedding clusterability using Adjusted Mutual Information (AMI) (Vinh et al., 2010), which quantifies agreement between k-means cluster assignments and ground-truth spurious groups:

$$\text{AMI}(C, G) = \frac{I(C, G) - E[I(C, G)]}{\max(H(C), H(G)) - E[I(C, G)]}$$

where $C$ are cluster labels, $G$ are ground-truth spurious groups, $I(\cdot, \cdot)$ is mutual information, and $H(\cdot)$ is entropy. AMI ranges from 0 (chance-level clustering) to 1 (perfect agreement). We use $k=4$ clusters corresponding to Waterbirds' 4 spurious groups.

**Rationale:** AMI adjusts for chance agreement and handles varying cluster sizes/densities better than alternatives like Silhouette score or Davies-Bouldin index. It directly measures whether spurious groups occupy distinct density modes.

### Silhouette Score

As a complementary metric, we compute Silhouette score $s_i$ for each sample:

$$s_i = \frac{b_i - a_i}{\max(a_i, b_i)}$$

where $a_i$ is mean intra-cluster distance and $b_i$ is mean nearest-cluster distance. Mean Silhouette $\geq$ 0.3 indicates well-separated clusters.

## SimCLR Training and Mechanism M1

We train SimCLR (Chen et al., 2020) on Waterbirds to test M1: InfoNCE loss creates dense spurious clusters.

### Architecture and Training

- **Encoder**: ResNet-50 backbone with 2048-dimensional embedding space
- **InfoNCE loss**: $\mathcal{L} = -\log \frac{\exp(\text{sim}(z_i, z_i^+)/\tau)}{\sum_{k=1}^{2N} \mathbb{1}_{k \neq i} \exp(\text{sim}(z_i, z_k)/\tau)}$
- **Augmentations**: Random crop, color jitter, Gaussian blur (standard SimCLR protocol)
- **Hyperparameters**: Learning rate $\in \{0.01, 0.001, 0.0001\}$, weight decay $\in \{10^{-4}, 10^{-5}, 10^{-6}\}$, batch size 32, temperature $\tau=0.5$

**Mechanism Hypothesis M1:** InfoNCE pulls together samples with shared spurious features (water backgrounds), creating dense clusters. If M1 holds, AMI $\geq$ 0.4 and Silhouette $\geq$ 0.3.

## Cluster-Balanced Retraining and Mechanism M2

To test M2 (clusterability predicts efficacy), we implement cluster-balanced retraining:

### Cluster-Balanced Loss

Given k-means cluster assignments $c_i$ from SSL embeddings:

$$\mathcal{L}_{\text{CB}} = \sum_{c=1}^K w_c \cdot \mathcal{L}_{\text{CE}}(\{(x_i, y_i) : c_i = c\})$$

where $w_c = N / (K \cdot |C_c|)$ balances cluster representation and $\mathcal{L}_{\text{CE}}$ is cross-entropy loss.

**Mechanism Hypothesis M2:** If clusterability (AMI) is high, cluster-balanced retraining improves WGA by $\geq$ 2 percentage points. If AMI is low (<0.3), improvement should be <0.5pp. We test this by stratifying models by AMI and measuring correlation between AMI and $\Delta$WGA.

## LA-SSL Training and Mechanism M3

We test M3 (LA-SSL disperses clusters) by training LA-SSL and comparing geometry to SimCLR.

### Learning-Speed Aware Sampling

LA-SSL (Zhu et al., 2023) resamples training data based on per-sample learning speed $v_i$:

$$v_i = \mathbb{E}_{e \in [e_{\text{start}}, e_{\text{end}}]} |\mathcal{L}_e(x_i) - \mathcal{L}_{e-1}(x_i)|$$

Slow-learning samples (low $v_i$) are upweighted with probability proportional to $\exp(-\alpha v_i)$ where $\alpha$ is a temperature parameter.

**Mechanism Hypothesis M3:** Learning-speed resampling upweights minority groups (slow learners), disrupting spurious cluster coherence. If M3 holds, LA-SSL should reduce AMI by $\geq$ 30% compared to SimCLR while preserving linear separability ($\Delta$AUC < 0.05).

## Experimental Design

### Proof-of-Concept Training

We conduct POC experiments with 20 epochs to validate implementation before full-scale training (100 epochs, 48-96 GPU hours). This is standard practice to catch implementation bugs early.

### Success Criteria

- **M1 (cluster formation)**: AMI $\geq$ 0.4 OR Silhouette $\geq$ 0.3
- **M2 (diagnostic power)**: Pearson correlation (AMI, $\Delta$WGA) > 0, p < 0.05
- **M3 (cluster dispersion)**: AMI reduction $\geq$ 30% AND $\Delta$AUC < 0.05

### Evaluation Metrics

- **Worst-Group Accuracy (WGA)**: $\min_{g} \text{Acc}_g$ across 4 spurious groups
- **Average Accuracy**: Overall classification accuracy
- **Linear Probe AUC**: Binary classification AUC on minority vs majority groups using linear probe on frozen embeddings

All experiments use real Waterbirds data (verified via Phase 4 validation) with no synthetic mocks.
