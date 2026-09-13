# Research Proposal: Learning Dynamics Signatures: Predicting Representation Alignment from Early Training Trajectories

## 1. Introduction

### Background

The emergence of similar internal representations across distinct neural networks—whether biological or artificial—has become one of the most intriguing phenomena in modern machine learning and neuroscience. When trained on comparable tasks, neural networks with different initializations, architectures, or even modalities often converge to remarkably similar representational structures. This observation, supported by growing empirical evidence, suggests fundamental principles governing how learning systems extract and organize information from their environment.

Recent theoretical advances have begun to shed light on this phenomenon. The Canonical Representation Hypothesis (CRH) proposed by Ziyin et al. (2024) suggests that during training, latent representations, weights, and neuron gradients become mutually aligned, leading to compact, task-invariant representations. Similarly, van Rossem and Saxe (2024) developed an effective theory demonstrating that certain representation learning dynamics are conserved across various deep network architectures, pointing to universal principles in representation formation.

Despite these advances, a critical gap remains: current approaches predominantly analyze fully-trained models, treating representation alignment as a post-hoc phenomenon. This retrospective analysis misses crucial insights embedded within the learning process itself. Understanding the *dynamics* of representation formation—not just its end state—could unlock predictive capabilities with profound practical implications.

### Research Objectives

This research aims to develop a principled framework for predicting representation alignment between neural networks based on early training dynamics. Specifically, we pursue three interconnected objectives:

1. **Characterize trajectory signatures**: Identify and formalize the geometric and statistical properties of representation trajectories during early training that correlate with eventual cross-model alignment.

2. **Build predictive models**: Develop meta-learning approaches that can predict final representation similarity scores from minimal training observations.

3. **Discover critical periods**: Determine the minimal training duration required for reliable alignment prediction, establishing analogues to neuroscientific critical periods in artificial learning systems.

### Significance

This research addresses both theoretical and practical imperatives. Theoretically, it bridges the gap between identifiability theory in machine learning and learning dynamics perspectives from neuroscience, potentially revealing universal principles governing representation emergence. Practically, the ability to predict representation alignment early in training enables:

- **Efficient model zoo curation**: Early identification of models likely to develop unique versus redundant representations
- **Computational savings**: Early-stopping decisions for models that will converge to similar representations
- **Improved model merging**: Identification of merge-compatible checkpoints without full training
- **Transfer learning optimization**: Selection of source models most likely to align with target task representations

## 2. Methodology

### 2.1 Experimental Framework Overview

Our methodology comprises three integrated components: (1) systematic trajectory data collection across diverse training configurations, (2) trajectory fingerprinting and feature extraction, and (3) alignment prediction model development with critical period analysis.

### 2.2 Data Collection and Training Protocol

#### Model Zoo Construction

We construct a comprehensive model zoo spanning multiple axes of variation:

**Architectures**: ResNet-18/34/50, VGG-16/19, Vision Transformer (ViT-S/B), MLP-Mixer, and ConvNeXt variants for vision; LSTM, GRU, and Transformer variants for sequence tasks.

**Datasets**: CIFAR-10/100, ImageNet-1K (subsets), and domain-specific datasets to examine task transfer.

**Training Configurations**: For each architecture-dataset pair, we train $N = 50$ models with:
- Different random initializations (Xavier, Kaiming, orthogonal)
- Learning rate variations: $\eta \in \{10^{-4}, 10^{-3}, 10^{-2}\}$
- Batch sizes: $B \in \{32, 128, 512\}$
- Optimizer choices: SGD (with/without momentum), Adam, AdamW

#### Trajectory Logging Protocol

For each model, we record comprehensive trajectory data at logarithmically-spaced checkpoints $\{t_0, t_1, ..., t_T\}$ where $t_k = \lfloor t_0 \cdot \alpha^k \rfloor$ iterations ($\alpha = 1.5$, $t_0 = 100$):

1. **Layer-wise activations**: For a fixed probe dataset $\mathcal{D}_{probe}$ of 5,000 samples, store activations $\{H^{(l)}(t_k)\}_{l=1}^L$ for all layers $l$.

2. **Gradient statistics**: Layer-wise gradient norms, variance, and directional consistency:
$$G^{(l)}(t_k) = \frac{1}{|\mathcal{B}|}\sum_{x \in \mathcal{B}} \nabla_{W^{(l)}} \mathcal{L}(x; \theta(t_k))$$

3. **Loss landscape geometry**: Local curvature estimates via Hessian trace approximation using Hutchinson's method:
$$\text{Tr}(\mathbf{H}(t_k)) \approx \frac{1}{M}\sum_{m=1}^M \mathbf{v}_m^\top \mathbf{H}(t_k) \mathbf{v}_m$$
where $\mathbf{v}_m$ are random Rademacher vectors.

### 2.3 Trajectory Fingerprinting

#### Representation Geometry Features

For each checkpoint $t_k$ and layer $l$, we extract geometric features from the activation matrix $H^{(l)}(t_k) \in \mathbb{R}^{n \times d}$:

**Spectral Profile**: The normalized singular value distribution captures representation dimensionality:
$$\sigma^{(l)}(t_k) = \left[\frac{s_1}{\sum_i s_i}, \frac{s_2}{\sum_i s_i}, ..., \frac{s_r}{\sum_i s_i}\right]$$
where $\{s_i\}$ are singular values of $H^{(l)}(t_k)$.

**Participation Ratio**: Effective dimensionality measure:
$$PR^{(l)}(t_k) = \frac{\left(\sum_i s_i^2\right)^2}{\sum_i s_i^4}$$

**Representation Velocity**: Rate of geometric change between checkpoints:
$$v^{(l)}(t_k) = \frac{d_{geo}(H^{(l)}(t_k), H^{(l)}(t_{k-1}))}{t_k - t_{k-1}}$$
where $d_{geo}$ is the geodesic distance on the Grassmann manifold of subspaces.

#### Gradient Flow Features

**Gradient Alignment Index**: Measures consistency of gradient directions:
$$\text{GAI}^{(l)}(t_k) = \frac{1}{|\mathcal{B}|^2}\sum_{x,x' \in \mathcal{B}} \cos\left(\nabla_{W^{(l)}}\mathcal{L}(x), \nabla_{W^{(l)}}\mathcal{L}(x')\right)$$

**Layer-wise Learning Coefficient**: Effective learning rate based on weight change:
$$\lambda^{(l)}(t_k) = \frac{\|W^{(l)}(t_k) - W^{(l)}(t_{k-1})\|_F}{\|W^{(l)}(t_{k-1})\|_F \cdot (t_k - t_{k-1})}$$

#### Trajectory Embedding

We consolidate features into a trajectory fingerprint. For observation window $[t_0, t_\tau]$, define:
$$\Phi(t_\tau) = \text{Concat}\left[\phi_{spec}(t_\tau), \phi_{grad}(t_\tau), \phi_{curv}(t_\tau)\right]$$

where each $\phi$ aggregates the respective feature time series using temporal statistics (mean, variance, trend coefficients from linear regression, and autocovariance at lag 1).

### 2.4 Alignment Prediction Model

#### Ground Truth Alignment Computation

For fully-trained model pairs $(M_i, M_j)$, we compute alignment scores using Centered Kernel Alignment (CKA):
$$\text{CKA}(H_i, H_j) = \frac{\text{HSIC}(H_i, H_j)}{\sqrt{\text{HSIC}(H_i, H_i) \cdot \text{HSIC}(H_j, H_j)}}$$

where HSIC is the Hilbert-Schmidt Independence Criterion:
$$\text{HSIC}(H_i, H_j) = \frac{1}{(n-1)^2}\text{Tr}(K_i \tilde{H} K_j \tilde{H})$$
with $K_i = H_i H_i^\top$, $K_j = H_j H_j^\top$, and $\tilde{H} = I_n - \frac{1}{n}\mathbf{1}\mathbf{1}^\top$.

We also compute Canonical Correlation Analysis (CCA) similarity and Procrustes distance for robustness.

#### Meta-Model Architecture

We design a Siamese trajectory encoder with attention-based aggregation:

**Input**: Trajectory fingerprints $(\Phi_i(t_\tau), \Phi_j(t_\tau))$ from two models up to observation time $t_\tau$.

**Encoder**: Shared temporal transformer encoder:
$$Z_i = \text{TransformerEnc}(\Phi_i(t_\tau))$$

**Comparison Module**: Compute pairwise features:
$$F_{ij} = [Z_i \odot Z_j; |Z_i - Z_j|; Z_i + Z_j]$$

**Prediction Head**: MLP outputting alignment score:
$$\hat{A}_{ij} = \text{MLP}(F_{ij}) \in [0, 1]$$

**Training Objective**:
$$\mathcal{L}_{pred} = \frac{1}{|\mathcal{P}|}\sum_{(i,j) \in \mathcal{P}} \left(\hat{A}_{ij} - A_{ij}^{CKA}\right)^2 + \lambda \cdot \text{RankLoss}(\hat{A}, A^{CKA})$$

where RankLoss ensures correct ordering of alignment predictions.

### 2.5 Critical Period Analysis

To identify minimal observation windows, we train separate predictors for $\tau \in \{1\%, 5\%, 10\%, 20\%, 50\%\}$ of total training iterations and evaluate:

**Prediction Accuracy**: Correlation between predicted and actual alignment scores.

**Decision Reliability**: AUC-ROC for binary classification (alignable vs. non-alignable at threshold $A > 0.7$).

**Critical Period**: Defined as minimal $\tau^*$ achieving 90% of full-training prediction performance.

### 2.6 Evaluation Metrics

1. **Pearson/Spearman Correlation**: Between predicted and actual alignment scores
2. **Mean Absolute Error (MAE)**: $\frac{1}{|\mathcal{P}|}\sum_{(i,j)}|\hat{A}_{ij} - A_{ij}|$
3. **Classification Metrics**: Precision, Recall, F1 for alignment/non-alignment classification
4. **Generalization Gap**: Performance difference between seen and unseen architecture pairs
5. **Computational Efficiency**: Training iterations required for reliable prediction vs. full training

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Primary Deliverables**:

1. **Trajectory Signature Taxonomy**: A comprehensive characterization of early training dynamics features that predict representation alignment, including identification of architecture-specific versus universal signatures.

2. **Alignment Prediction System**: An open-source toolkit for predicting pairwise representation alignment from early training checkpoints, with expected Spearman correlation $> 0.85$ at 10% training observation.

3. **Critical Period Maps**: Quantified minimal observation windows for different architecture families and tasks, hypothesized to range from 5-15% of total training for standard configurations.

4. **Theoretical Insights**: Formalization of connections between trajectory geometry (spectral evolution, gradient alignment) and the Canonical Representation Hypothesis, potentially extending CRH to predictive settings.

### Scientific Impact

This research directly addresses the workshop's core question of *when* and *why* different neural models learn similar representations by shifting focus from post-hoc analysis to predictive dynamics. Our framework will:

1. **Bridge ML and neuroscience perspectives**: The critical period concept directly parallels sensitive periods in neural development, enabling cross-disciplinary dialogue on universal learning principles.

2. **Advance identifiability theory**: By connecting trajectory properties to final representation structure, we contribute to understanding when representations are identifiable from learning dynamics alone.

3. **Enable practical applications**: Model zoo curation, merge-compatible checkpoint identification, and efficient ensemble construction become computationally tractable.

### Broader Impact

Beyond immediate scientific contributions, this work has implications for:

- **Sustainable AI**: Reducing redundant training computation through early alignment prediction
- **Model sharing ecosystems**: Principled guidelines for when models can be effectively merged or stitched
- **Understanding learning universals**: Contributing to fundamental questions about what aspects of representation learning are universal versus contingent

The proposed framework transforms representation alignment from a retrospective observation to a predictive science, ultimately supporting the workshop's goal of unifying representations in neural models into a cohesive theoretical and practical whole.