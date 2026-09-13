# Research Proposal: Domain-Adaptive Machine Learning Interatomic Potentials via Shared-Private Representation Learning for Improved Surface and Interface Predictions

## 1. Introduction

### 1.1 Background

The discovery and design of novel materials underpin solutions to humanity's most pressing challenges, from renewable energy generation and storage to catalysis and clean water production. Machine learning (ML) has emerged as a transformative tool in computational materials science, with geometric deep learning methods demonstrating remarkable success in modeling atomic structures. Universal machine learning interatomic potentials (MLIPs), such as MACE (Multi-Atomic Cluster Expansion), NequIP, and CHGNet, have achieved near-DFT accuracy for bulk materials while offering computational speedups of several orders of magnitude.

However, a critical limitation persists: these universal MLIPs exhibit systematic errors when applied to surfaces and interfaces—structures that are fundamentally important for catalysis, battery electrodes, corrosion, and semiconductor devices. Recent studies have identified a "systematic softening" phenomenon where MLIPs trained predominantly on bulk configurations underestimate surface energies and exhibit degraded force predictions at interfaces. This domain shift problem arises because bulk-dominated training datasets bias learned atomic representations toward configurations with high coordination numbers and symmetric local environments, leaving surface atoms—characterized by under-coordination, asymmetric environments, and distinct electronic structures—poorly represented.

Current approaches to address this limitation are unsatisfactory. Fine-tuning on surface-specific data risks catastrophic forgetting of bulk accuracy, while training separate models for different material domains sacrifices the universality that makes MLIPs practically valuable. The fundamental challenge lies in learning atomic representations that can transfer across material domains while capturing the domain-specific physics essential for accurate energy and force predictions.

### 1.2 Research Objectives

This research proposes a novel **Shared-Private Domain-Adaptive MLIP (SP-DA-MLIP)** architecture that systematically addresses the domain shift problem in materials modeling. Our primary objectives are:

1. **Develop a shared-private representation learning framework** that augments MACE with domain-adaptive components, enabling simultaneous learning of domain-invariant and domain-specific atomic features.

2. **Demonstrate significant improvement in surface/interface predictions** (>30% MAE reduction) while maintaining bulk accuracy within 3% of baseline performance.

3. **Validate the causal mechanism** through systematic ablation studies, confirming that domain adversarial training produces genuinely domain-invariant representations.

4. **Establish a generalizable methodology** applicable to other domain shift problems in materials science, including bulk-to-defect and crystal-to-amorphous transitions.

### 1.3 Significance

This research addresses a fundamental bottleneck in computational materials discovery. Surfaces and interfaces govern critical phenomena including heterogeneous catalysis (responsible for >90% of industrial chemical processes), battery electrode reactions, and corrosion mechanisms. By enabling accurate surface predictions without domain-specific retraining, SP-DA-MLIP will:

- **Accelerate catalyst discovery** by providing reliable surface energy and adsorption energy predictions across diverse material compositions.
- **Enable high-throughput interface screening** for battery materials and semiconductor heterostructures.
- **Reduce computational costs** by eliminating the need for separate surface-specific models or expensive fine-tuning procedures.
- **Advance the theoretical understanding** of transferable atomic representations in geometric deep learning.

## 2. Methodology

### 2.1 Architecture Design

The SP-DA-MLIP architecture augments the MACE framework with three key components: a shared encoder trained with domain adversarial loss, a private encoder conditioned on domain embeddings, and a learned gating mechanism for adaptive fusion.

#### 2.1.1 Shared Encoder with Domain Adversarial Training

The shared encoder $\mathcal{E}_s$ processes atomic environments using MACE's equivariant message passing layers while being trained to produce domain-invariant representations. Given an atomic configuration $\mathcal{G} = (\mathbf{r}, \mathbf{Z})$ with positions $\mathbf{r}$ and atomic numbers $\mathbf{Z}$, the shared encoder produces node features:

$$\mathbf{h}_i^{(s)} = \mathcal{E}_s(\mathbf{r}, \mathbf{Z})_i \in \mathbb{R}^{d_s}$$

Domain invariance is enforced through a gradient reversal layer (GRL) connected to a domain classifier $\mathcal{D}$. The GRL acts as an identity function during forward propagation but reverses gradients during backpropagation:

$$\text{GRL}_\lambda(\mathbf{x}) = \mathbf{x}, \quad \frac{\partial \text{GRL}_\lambda}{\partial \mathbf{x}} = -\lambda \mathbf{I}$$

where $\lambda$ is a scheduling parameter that increases during training. The domain classifier predicts whether an atomic environment belongs to bulk or surface domains:

$$p_{\text{domain}}(i) = \sigma(\mathcal{D}(\mathbf{h}_i^{(s)}))$$

The adversarial loss encourages the shared encoder to produce features that confuse the domain classifier:

$$\mathcal{L}_{\text{adv}} = -\frac{1}{N}\sum_{i=1}^{N}\left[y_i \log p_{\text{domain}}(i) + (1-y_i)\log(1-p_{\text{domain}}(i))\right]$$

where $y_i \in \{0, 1\}$ indicates the domain label.

#### 2.1.2 Private Encoder with Domain Conditioning

The private encoder $\mathcal{E}_p$ captures domain-specific physics by conditioning on automatically computed domain embeddings. For each atom $i$, we compute local environment statistics:

$$\mathbf{d}_i = \left[\text{CN}_i, \bar{r}_i, \sigma_r^{(i)}, \bar{\theta}_i, \sigma_\theta^{(i)}, \text{ASA}_i\right]$$

where $\text{CN}_i$ is the coordination number, $\bar{r}_i$ and $\sigma_r^{(i)}$ are mean and standard deviation of neighbor distances, $\bar{\theta}_i$ and $\sigma_\theta^{(i)}$ characterize angular distributions, and $\text{ASA}_i$ is the accessible surface area indicator. These statistics are embedded through a learnable projection:

$$\mathbf{e}_i^{(d)} = \text{MLP}_{\text{embed}}(\mathbf{d}_i) \in \mathbb{R}^{d_e}$$

The private encoder incorporates domain conditioning through feature-wise linear modulation (FiLM):

$$\mathbf{h}_i^{(p)} = \gamma(\mathbf{e}_i^{(d)}) \odot \mathcal{E}_p(\mathbf{r}, \mathbf{Z})_i + \beta(\mathbf{e}_i^{(d)})$$

where $\gamma$ and $\beta$ are learned scaling and shifting functions.

#### 2.1.3 Gated Fusion Mechanism

The shared and private representations are combined through a learned gating mechanism that adaptively weights their contributions:

$$\mathbf{g}_i = \sigma\left(\mathbf{W}_g[\mathbf{h}_i^{(s)} \| \mathbf{h}_i^{(p)} \| \mathbf{e}_i^{(d)}] + \mathbf{b}_g\right)$$

$$\mathbf{h}_i^{(\text{fused})} = \mathbf{g}_i \odot \mathbf{h}_i^{(s)} + (1 - \mathbf{g}_i) \odot \mathbf{h}_i^{(p)}$$

The fused representation maintains E(3)-equivariance by operating on invariant scalar features while preserving equivariant geometric information through separate channels.

#### 2.1.4 Energy and Force Prediction

The total energy is predicted as a sum of atomic contributions:

$$E = \sum_{i=1}^{N} \text{MLP}_{\text{energy}}(\mathbf{h}_i^{(\text{fused})})$$

Forces are computed as negative gradients of the energy with respect to atomic positions, ensuring energy conservation:

$$\mathbf{F}_i = -\frac{\partial E}{\partial \mathbf{r}_i}$$

### 2.2 Training Procedure

#### 2.2.1 Data Collection and Preparation

Training data combines two primary sources:

1. **Bulk structures**: Materials Project database (~150,000 structures) covering diverse chemistries and crystal systems.

2. **Surface structures**: Open Catalyst 2020 (OC20) dataset (~1.3 million surface configurations) with DFT-computed energies and forces.

Data preprocessing includes:
- Standardization of energy references across datasets
- Computation of domain embeddings for all configurations
- Stratified splitting ensuring balanced representation of material classes
- Train/validation/test splits of 80%/10%/10%

#### 2.2.2 Loss Function and Optimization

The total training loss combines energy prediction, force prediction, and domain adversarial terms:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_E + \alpha \mathcal{L}_F + \lambda(t) \mathcal{L}_{\text{adv}}$$

where:

$$\mathcal{L}_E = \frac{1}{M}\sum_{j=1}^{M}\left|E_j^{\text{pred}} - E_j^{\text{DFT}}\right|$$

$$\mathcal{L}_F = \frac{1}{3MN}\sum_{j=1}^{M}\sum_{i=1}^{N_j}\left\|\mathbf{F}_{ij}^{\text{pred}} - \mathbf{F}_{ij}^{\text{DFT}}\right\|_2$$

The adversarial weight $\lambda(t)$ follows a scheduled increase:

$$\lambda(t) = \frac{2}{1 + \exp(-\gamma_{\text{schedule}} \cdot t/T)} - 1$$

where $t$ is the current epoch, $T$ is total epochs, and $\gamma_{\text{schedule}} = 10$.

Training uses the AdamW optimizer with learning rate $10^{-3}$, weight decay $10^{-4}$, and cosine annealing schedule over 500 epochs.

### 2.3 Experimental Design

#### 2.3.1 Baseline Comparisons

We compare SP-DA-MLIP against:
1. **MACE-MP-0**: Pretrained universal MACE model
2. **MACE fine-tuned**: MACE fine-tuned on surface data
3. **CHGNet**: Universal potential with charge equilibration
4. **Separate models**: Independent MACE models for bulk and surface

#### 2.3.2 Ablation Studies

Systematic ablations isolate the contribution of each component:
- **Shared-only**: Remove private encoder and gating
- **Private-only**: Remove shared encoder and adversarial training
- **No-gating**: Simple concatenation instead of learned fusion
- **No-adversarial**: Remove GRL and domain classifier

#### 2.3.3 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Surface Energy MAE | Mean absolute error on OC20-IS2RE | <0.70× baseline |
| Bulk Energy MAE | Mean absolute error on MP test set | <1.03× baseline |
| Force MAE | Mean absolute error on forces | <1.05× baseline |
| Domain Classifier Accuracy | Classification accuracy on held-out test | <60% |
| Computational Overhead | Inference time relative to baseline | <1.5× |

#### 2.3.4 Statistical Analysis

- **Sample size**: 15 independent runs (5 random seeds × 3 hyperparameter configurations)
- **Statistical test**: Paired t-test with Bonferroni correction ($\alpha' = 0.0125$)
- **Effect size**: Target Cohen's d > 0.8 (large effect)
- **Confidence intervals**: 95% CI reported for all metrics

#### 2.3.5 Mechanism Validation

To verify the causal mechanism, we analyze:
1. **Representation visualization**: t-SNE projections of shared and private encoder outputs, expecting domain overlap in shared and separation in private representations.
2. **Gating analysis**: Distribution of gating weights across bulk vs. surface atoms.
3. **Domain classifier trajectory**: Accuracy evolution during training, confirming convergence toward random chance.

### 2.4 Implementation Details

The implementation builds on the MACE codebase with modifications using PyTorch and e3nn for equivariant operations. Key architectural parameters:
- Hidden dimension: 128
- Number of message passing layers: 4 (2 shared, 2 private)
- Maximum angular momentum: $l_{\text{max}} = 2$
- Cutoff radius: 5.0 Å
- Domain embedding dimension: 64

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our hypothesis and preliminary analysis, we anticipate:

1. **Primary outcome**: Surface energy MAE reduction of 30-40% compared to baseline MACE on OC20-IS2RE benchmark, with statistical significance ($p < 0.01$).

2. **Bulk preservation**: Bulk energy MAE within 3% of baseline, demonstrating successful avoidance of catastrophic forgetting.

3. **Mechanism validation**: Domain classifier accuracy decreasing from >90% to <60%, confirming that domain adversarial training produces genuinely invariant representations.

4. **Interpretable gating**: Gating weights showing systematic differences between bulk and surface atoms, with surface atoms relying more heavily on private encoder outputs.

### 3.2 Scientific Impact

This research will advance the field in several dimensions:

**Methodological contributions**: The shared-private domain-adaptive framework provides a principled approach to handling domain shift in geometric deep learning, applicable beyond materials science to molecular modeling and protein structure prediction.

**Theoretical insights**: Analysis of learned representations will illuminate what constitutes "domain-invariant" atomic features and how domain-specific physics manifests in neural network representations.

**Practical tools**: The trained SP-DA-MLIP model and codebase will be released as open-source resources, enabling immediate application to surface-sensitive materials discovery problems.

### 3.3 Broader Impact

**Catalyst discovery**: Accurate surface energy predictions will accelerate identification of promising catalyst materials for sustainable chemistry, including CO2 reduction, nitrogen fixation, and hydrogen evolution.

**Battery materials**: Improved interface modeling will enable more reliable screening of solid electrolyte interfaces and electrode-electrolyte compatibility.

**Methodology transfer**: The domain adaptation framework can be extended to other domain shift problems in materials science, including bulk-to-defect, crystalline-to-amorphous, and equilibrium-to-reactive transitions.

### 3.4 Limitations and Future Directions

We acknowledge several limitations that define future research directions:
- The current approach requires surface data during training; zero-shot surface prediction remains an open challenge.
- Domain embeddings rely on heuristic local environment statistics; learned domain detection could improve generalization.
- Computational overhead of ~1.3-1.5× may limit application to very large-scale simulations.

Future work will explore extension to additional material domains (polymers, nanoporous materials), integration with active learning for efficient data acquisition, and development of uncertainty quantification methods calibrated across domains.