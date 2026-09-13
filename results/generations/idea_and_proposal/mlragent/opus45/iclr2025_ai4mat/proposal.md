# Research Proposal: Hierarchical Multi-Scale Foundation Model for Materials Science via Scale-Aware Tokenization

## 1. Introduction

### Background

Materials science fundamentally operates across multiple length scales—from angstrom-level atomic arrangements to micrometer-scale grain structures to macroscopic bulk properties. This inherent multi-scale nature presents a unique challenge for artificial intelligence: properties that determine a material's utility (mechanical strength, thermal conductivity, catalytic activity) emerge from complex interactions spanning these scales. A crack propagates through grain boundaries; a catalyst's selectivity depends on atomic site geometry within a nanoparticle; and semiconductor performance hinges on defect distributions across device dimensions.

The recent success of foundation models in natural language processing and computer vision has inspired the materials science community to pursue analogous unified models. However, current approaches remain fundamentally limited by their single-scale focus. Graph neural networks excel at capturing local atomic environments but struggle with long-range order; convolutional approaches on electron microscopy images capture mesoscale features but lose atomic precision. This fragmentation forces researchers to maintain separate models for different scales, losing the crucial cross-scale correlations that govern real materials behavior.

Recent work has demonstrated the potential of hierarchical tokenization schemes in related domains. The Hierarchical Quantized Tokenization Framework (Xiang et al., 2025) showed that task-adaptive multi-scale aggregation improves graph representation learning. GeoBPE (Sun et al., 2025) successfully applied geometric byte pair encoding to create hierarchical vocabularies for protein structures. The Multiscale Byte Language Model (Egli et al., 2025) demonstrated that hierarchical decoder stacks can efficiently process million-length sequences with diverse representations. These advances suggest that a unified multi-scale approach could transform materials AI.

### Research Objectives

This proposal introduces **Scale-Aware Tokenization (SAT)**, a hierarchical foundation model framework designed to unify materials representation across atomic, molecular, mesoscale, and continuum scales. Our specific objectives are:

1. **Develop a hierarchical tokenizer** that learns discrete, interpretable tokens at multiple length scales using vector quantization with scale-specific codebooks.

2. **Design cross-scale attention mechanisms** that explicitly model how perturbations at one scale propagate to influence properties at other scales.

3. **Create a multi-fidelity pre-training strategy** that leverages diverse datasets spanning DFT calculations, molecular dynamics trajectories, experimental microscopy, and macroscopic measurements.

4. **Demonstrate unified capabilities** including property prediction, structure generation, and inverse design across length scales on benchmark materials challenges.

### Significance

This research directly addresses both major themes of AI4Mat-ICLR-2025. For foundation models, SAT provides a principled architecture that respects the hierarchical physical structure of materials. For next-generation representations, our scale-aware tokenization offers a unified vocabulary that naturally integrates multiple data modalities. Success would enable: (1) transfer learning across materials systems sharing structural motifs at any scale; (2) generation of physically consistent multi-scale structures; and (3) interpretable analysis of cross-scale phenomena critical for materials engineering.

## 2. Methodology

### 2.1 Data Collection and Preparation

**Multi-Scale Dataset Assembly**: We will curate a comprehensive dataset spanning four length scales:

- **Atomic scale** ($\sim$1-10 Å): DFT calculations from Materials Project (>150,000 structures), OQMD, and AFLOW databases, including formation energies, band structures, and phonon spectra.

- **Molecular/cluster scale** ($\sim$10-100 Å): Molecular dynamics trajectories from published studies on grain boundaries, surfaces, and nanoparticles; QM9 and OC20 datasets for molecular systems.

- **Mesoscale** ($\sim$100 nm - 10 μm): Electron microscopy images (SEM, TEM) from public repositories, synthetic microstructure images generated via phase-field simulations, and EBSD grain orientation maps.

- **Macroscale**: Experimental property measurements from NIST databases, published literature, and industrial datasets (where available), including mechanical properties, thermal conductivity, and electrical resistivity.

**Data Harmonization**: We will develop standardized interfaces to convert each data type into a common format:
- Crystal structures → periodic graphs with atomic features
- MD trajectories → temporal sequences of atomic configurations
- Microscopy images → pixel arrays with resolution metadata
- Macroscopic properties → scalar/tensor values with uncertainty estimates

### 2.2 Hierarchical Scale-Aware Tokenizer

**Architecture Overview**: The SAT tokenizer consists of four scale-specific encoders coupled with vector quantization codebooks:

$$\mathcal{T} = \{\mathcal{T}_{\text{atomic}}, \mathcal{T}_{\text{molecular}}, \mathcal{T}_{\text{meso}}, \mathcal{T}_{\text{macro}}\}$$

**Atomic-Scale Tokenizer** ($\mathcal{T}_{\text{atomic}}$): Uses an equivariant graph neural network to encode local atomic environments:

$$\mathbf{h}_i^{(0)} = \text{Embed}(Z_i)$$
$$\mathbf{h}_i^{(l+1)} = \mathbf{h}_i^{(l)} + \sum_{j \in \mathcal{N}(i)} \phi_{\text{msg}}(\mathbf{h}_i^{(l)}, \mathbf{h}_j^{(l)}, \mathbf{e}_{ij})$$

where $Z_i$ is the atomic number, $\mathcal{N}(i)$ denotes neighbors within a cutoff radius, and $\mathbf{e}_{ij}$ encodes relative positions using spherical harmonics. The final atomic representations are quantized:

$$\mathbf{z}_i^{\text{atomic}} = \arg\min_{\mathbf{c}_k \in \mathcal{C}_{\text{atomic}}} \|\mathbf{h}_i^{(L)} - \mathbf{c}_k\|_2$$

where $\mathcal{C}_{\text{atomic}}$ is a learned codebook of size $K_{\text{atomic}} = 512$.

**Molecular-Scale Tokenizer** ($\mathcal{T}_{\text{molecular}}$): Aggregates atomic tokens into molecular motifs using a pooling hierarchy:

$$\mathbf{m}_g = \text{Pool}\left(\{\mathbf{z}_i^{\text{atomic}}\}_{i \in g}\right) + \text{MLP}\left(\mathbf{r}_g^{\text{geometric}}\right)$$

where $g$ denotes a local subgraph (e.g., coordination polyhedra, secondary building units) and $\mathbf{r}_g^{\text{geometric}}$ captures geometric descriptors (bond angles, dihedral distributions). Quantization uses codebook $\mathcal{C}_{\text{molecular}}$ with $K_{\text{molecular}} = 1024$.

**Mesoscale Tokenizer** ($\mathcal{T}_{\text{meso}}$): Processes microscopy images or coarse-grained representations using a Vision Transformer backbone:

$$\mathbf{p}_j = \text{ViT}_{\text{encoder}}(\mathbf{I}_{j})$$

where $\mathbf{I}_j$ represents image patches. These are quantized against $\mathcal{C}_{\text{meso}}$ with $K_{\text{meso}} = 2048$ to capture grain morphologies, defect patterns, and phase distributions.

**Macroscale Tokenizer** ($\mathcal{T}_{\text{macro}}$): Encodes bulk property vectors and processing conditions:

$$\mathbf{b} = \text{MLP}\left([\mathbf{p}_{\text{mech}}, \mathbf{p}_{\text{thermal}}, \mathbf{p}_{\text{elec}}, \mathbf{c}_{\text{process}}]\right)$$

Quantized against $\mathcal{C}_{\text{macro}}$ with $K_{\text{macro}} = 256$.

**Joint Training Objective**: The tokenizers are trained end-to-end with a combined loss:

$$\mathcal{L}_{\text{token}} = \sum_{s \in \mathcal{S}} \left[\mathcal{L}_{\text{recon}}^{(s)} + \beta \mathcal{L}_{\text{commit}}^{(s)} + \gamma \mathcal{L}_{\text{diversity}}^{(s)}\right]$$

where $\mathcal{L}_{\text{recon}}$ ensures reconstruction fidelity, $\mathcal{L}_{\text{commit}}$ is the commitment loss for stable quantization, and $\mathcal{L}_{\text{diversity}}$ encourages codebook utilization.

### 2.3 Cross-Scale Transformer Architecture

**Scale-Bridging Attention**: We introduce explicit cross-scale attention layers that model information flow between scales:

$$\text{Attention}^{s \rightarrow s'}(\mathbf{Q}^{s'}, \mathbf{K}^s, \mathbf{V}^s) = \text{softmax}\left(\frac{\mathbf{Q}^{s'} (\mathbf{K}^s)^T}{\sqrt{d_k}} \cdot \mathbf{M}^{s \rightarrow s'}\right)\mathbf{V}^s$$

where $\mathbf{M}^{s \rightarrow s'}$ is a learnable scale-coupling matrix that captures physical relationships (e.g., how atomic defects influence mesoscale crack propagation).

**Hierarchical Transformer Block**: Each block contains:
1. Intra-scale self-attention at each level
2. Bottom-up cross-scale attention (atomic → molecular → meso → macro)
3. Top-down cross-scale attention (macro → meso → molecular → atomic)
4. Feed-forward networks with scale-specific parameters

$$\mathbf{H}^{(l+1)}_s = \text{FFN}_s\left(\text{CrossAttn}\left(\text{SelfAttn}(\mathbf{H}^{(l)}_s)\right)\right)$$

### 2.4 Multi-Fidelity Pre-training Strategy

**Pre-training Tasks**:

1. **Scale-Aware Masked Token Prediction**: Randomly mask tokens at each scale and predict them conditioned on unmasked tokens across all scales:
$$\mathcal{L}_{\text{mask}} = -\sum_{s}\sum_{i \in \text{masked}} \log P(z_i^s | \mathbf{z}_{\text{unmasked}})$$

2. **Cross-Scale Consistency**: Enforce that predictions at different scales are physically consistent:
$$\mathcal{L}_{\text{consist}} = \|\mathbf{p}_{\text{pred}}^{\text{macro}} - f_{\text{agg}}(\{\mathbf{z}^{\text{meso}}\})\|_2^2$$

3. **Scale Prediction**: Given tokens at one scale, predict corresponding tokens at adjacent scales:
$$\mathcal{L}_{\text{scale}} = \text{CE}(\hat{\mathbf{z}}^{s+1}, \mathbf{z}^{s+1} | \mathbf{z}^s)$$

4. **Contrastive Scale Alignment**: Align representations of the same material across scales:
$$\mathcal{L}_{\text{align}} = -\log \frac{\exp(\text{sim}(\mathbf{h}_{\text{atomic}}, \mathbf{h}_{\text{macro}})/\tau)}{\sum_j \exp(\text{sim}(\mathbf{h}_{\text{atomic}}, \mathbf{h}_j^{\text{macro}})/\tau)}$$

### 2.5 Experimental Validation

**Benchmark Tasks**:

1. **Property Prediction**: Formation energy (MAE), band gap (MAE), bulk modulus (MAE), thermal conductivity (RMSE) on held-out test sets from Materials Project and experimental databases.

2. **Structure Generation**: Crystal structure generation evaluated via validity, uniqueness, novelty metrics, and physical feasibility (DFT relaxation stability).

3. **Inverse Design**: Given target properties, generate candidate structures and validate through DFT calculations.

4. **Cross-Scale Transfer**: Train on atomic data, evaluate prediction of mesoscale features (grain size distribution) and macroscale properties.

**Evaluation Metrics**:
- Prediction accuracy: MAE, RMSE, $R^2$ coefficient
- Generation quality: Validity rate, structural diversity (fingerprint distance)
- Codebook analysis: Codebook utilization, token interpretability scores
- Transfer efficiency: Performance vs. fine-tuning data curve

**Baselines**: CGCNN, MEGNet, SchNet (atomic scale); MicroStructGen (mesoscale); GNoME, MatterGen (generation).

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Unified Foundation Model**: A single pre-trained model capable of processing materials data across four length scales with state-of-the-art performance on scale-specific benchmarks and improved performance on cross-scale tasks.

2. **Interpretable Token Vocabularies**: Scale-specific codebooks where tokens correspond to physically meaningful motifs (e.g., octahedral coordination at atomic scale, grain boundary types at mesoscale).

3. **Cross-Scale Transfer Capabilities**: Demonstrated ability to predict mesoscale and macroscale properties from atomic-level information with 20-30% improvement over single-scale baselines.

4. **Open-Source Release**: Pre-trained model weights, tokenizer implementations, and curated multi-scale datasets released to accelerate community research.

### Scientific Impact

This work addresses fundamental challenges in materials AI identified by the community. The hierarchical tokenization provides a principled approach to the multi-scale representation problem, while cross-scale attention mechanisms offer a computational framework for modeling emergent phenomena. Success would validate the hypothesis that unified foundation models can capture the full complexity of real materials systems.

### Practical Impact

Industry applications requiring multi-scale understanding—battery electrode design, semiconductor processing, structural alloy development—would benefit from a model that connects atomic choices to macroscopic performance. The interpretable token vocabularies enable materials scientists to leverage AI insights within established physical frameworks, addressing the crucial challenge of integrating AI into experimental workflows.

### Community Contribution

By focusing on both major themes of AI4Mat-ICLR-2025, this research provides concrete progress toward materials foundation models while advancing representation learning through scale-aware tokenization. The open-source release strategy ensures broad accessibility and encourages collaborative development across the interdisciplinary materials AI community.