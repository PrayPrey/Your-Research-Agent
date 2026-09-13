# Research Proposal

## Title
SymVAE: Symmetry-Aware Variational Autoencoders for Neural Network Weight Generation via Learned Canonicalization and Equivariant Processing

## 1. Introduction

### Background

The proliferation of publicly available neural network models—now exceeding one million on platforms like Hugging Face—represents an unprecedented opportunity to treat neural network weights as a first-class data modality. Just as the machine learning community has developed sophisticated methods for processing images, text, and audio, there is emerging recognition that model weights themselves encode rich information that can be analyzed, manipulated, and synthesized. This paradigm shift toward weight space learning promises to revolutionize transfer learning, model initialization, and efficient deployment of neural networks across diverse applications.

However, neural network weight spaces possess unique mathematical properties that distinguish them from conventional data modalities. Chief among these are the inherent symmetries present in weight configurations. Specifically, permuting the neurons within a hidden layer while correspondingly adjusting incoming and outgoing weights produces a functionally equivalent network—this is known as permutation symmetry. Additionally, scaling symmetries arise in networks with homogeneous activation functions, where weights can be rescaled between layers without changing the network's function. These symmetries create vast equivalence classes of weight configurations that represent identical functions, posing fundamental challenges for generative modeling approaches.

Recent work has begun addressing these challenges. DeepWeightFlow (Gupta et al., 2026) applies Git Re-Basin for neural network canonicalization before flow matching, demonstrating improved generation quality. Scale Equivariant Graph Metanetworks (Kuipers et al., 2025) provide theoretical analysis of scaling symmetries and leverage equivariant architectures for amortized optimization. Text2Weight (Tian et al., 2025) explores conditioning weight generation on natural language descriptions. Despite these advances, current methods either treat canonicalization as a fixed preprocessing step or focus on specific symmetry types in isolation, leaving significant room for improvement in unified symmetry handling.

### Research Objectives

This proposal introduces **SymVAE**, a novel variational autoencoder framework that comprehensively addresses weight space symmetries through three integrated innovations:

1. **Learned Canonicalization**: Rather than relying on fixed canonicalization procedures, we propose learning an optimal transport-based canonicalization module that adapts to the data distribution and downstream generation objectives.

2. **Equivariant Encoder-Decoder Architecture**: We develop a graph neural network-based encoder that produces symmetry-invariant latent codes and a decoder that generates weights while respecting architectural constraints.

3. **Hierarchical Latent Structure**: We design a latent space that disentangles task-level knowledge from architecture-specific weight patterns, enabling flexible transfer and interpolation.

### Significance

This research addresses fundamental challenges identified in the weight space learning community. By developing principled methods for handling symmetries, SymVAE could enable "model synthesis on demand"—generating high-quality, task-specific neural network weights without expensive training from scratch. This has profound implications for democratizing AI by reducing computational costs, enabling rapid prototyping, and facilitating model adaptation in resource-constrained settings. Furthermore, our theoretical contributions regarding weight space geometry and symmetry handling will advance the foundational understanding necessary for this emerging field.

## 2. Methodology

### 2.1 Problem Formulation

Let $\mathcal{W}$ denote the space of neural network weights for a given architecture with $L$ layers. A weight configuration $W = \{W^{(l)}, b^{(l)}\}_{l=1}^{L}$ consists of weight matrices $W^{(l)} \in \mathbb{R}^{n_{l} \times n_{l-1}}$ and bias vectors $b^{(l)} \in \mathbb{R}^{n_l}$, where $n_l$ is the number of neurons in layer $l$.

The permutation symmetry group $\mathcal{G}_\pi$ acts on weights as follows: for permutation matrices $P^{(l)} \in \mathbb{R}^{n_l \times n_l}$, the transformed weights:

$$\tilde{W}^{(l)} = P^{(l)} W^{(l)} (P^{(l-1)})^T, \quad \tilde{b}^{(l)} = P^{(l)} b^{(l)}$$

yield a functionally equivalent network. Similarly, scaling symmetries for ReLU networks allow transformations $W^{(l)} \rightarrow \alpha^{(l)} W^{(l)}$ with corresponding inverse scaling in adjacent layers.

Our goal is to learn a generative model $p_\theta(W | c)$ conditioned on task descriptors $c$ that produces high-quality weights while efficiently handling these symmetries.

### 2.2 SymVAE Architecture

#### 2.2.1 Learned Canonicalization Module

We propose a learnable canonicalization network $\mathcal{C}_\phi: \mathcal{W} \rightarrow \mathcal{W}$ that maps arbitrary weight configurations to a canonical representative of their equivalence class. Unlike fixed procedures like Git Re-Basin, our approach learns the optimal canonical form jointly with the generative model.

**Optimal Transport-Based Neuron Alignment**: For each layer $l$, we compute soft permutation matrices using an optimal transport formulation. Given reference neurons $R^{(l)} = \{r_i^{(l)}\}_{i=1}^{n_l}$ (learned parameters), we solve:

$$P^{(l)*} = \arg\min_{P \in \Pi_{n_l}} \sum_{i,j} C_{ij}^{(l)} P_{ij} + \epsilon H(P)$$

where $C_{ij}^{(l)} = \|w_i^{(l)} - r_j^{(l)}\|^2$ is the cost matrix comparing neuron $i$'s weights to reference $j$, $\Pi_{n_l}$ is the set of doubly stochastic matrices, and $H(P) = -\sum_{ij} P_{ij} \log P_{ij}$ is the entropic regularization. We solve this efficiently using the Sinkhorn algorithm:

$$P^{(k+1)} = \text{diag}(u^{(k)}) K \text{diag}(v^{(k)})$$

where $K = \exp(-C^{(l)}/\epsilon)$ and $u, v$ are iteratively updated normalization vectors.

**Scale Normalization**: After permutation alignment, we apply learned scale normalization:

$$\hat{W}^{(l)} = \frac{W^{(l)}}{\|\gamma^{(l)} \odot W^{(l)}\|_F + \delta}$$

where $\gamma^{(l)}$ are learnable importance weights and $\delta$ prevents division by zero.

The complete canonicalization is differentiable, enabling end-to-end training:

$$W_{\text{canon}} = \mathcal{C}_\phi(W) = \text{ScaleNorm}(\text{Permute}(W; P^*))$$

#### 2.2.2 Equivariant Encoder

We represent canonicalized weights as a bipartite graph $G = (V, E)$ where nodes $V$ represent neurons across all layers and edges $E$ connect neurons between adjacent layers, with edge features being the corresponding weights.

**Node Features**: For neuron $i$ in layer $l$:
$$h_i^{(0)} = \text{MLP}_{\text{init}}\left([W_{\text{in},i}^{(l)}; W_{\text{out},i}^{(l)}; b_i^{(l)}; e_l]\right)$$

where $W_{\text{in},i}^{(l)}$ and $W_{\text{out},i}^{(l)}$ are incoming and outgoing weight vectors, and $e_l$ is a learned layer embedding.

**Message Passing**: We employ $K$ rounds of message passing:

$$m_i^{(k)} = \sum_{j \in \mathcal{N}(i)} \text{MLP}_{\text{msg}}^{(k)}\left([h_i^{(k-1)}; h_j^{(k-1)}; w_{ij}]\right)$$
$$h_i^{(k)} = \text{MLP}_{\text{update}}^{(k)}\left([h_i^{(k-1)}; m_i^{(k)}]\right)$$

**Global Aggregation**: The encoder produces latent statistics through permutation-invariant pooling:

$$\mu_z = \text{MLP}_\mu\left(\sum_{i \in V} h_i^{(K)}\right), \quad \log \sigma_z^2 = \text{MLP}_\sigma\left(\sum_{i \in V} h_i^{(K)}\right)$$

#### 2.2.3 Hierarchical Latent Space

We structure the latent space into two components:

1. **Task Latent** $z_{\text{task}} \in \mathbb{R}^{d_t}$: Captures architecture-agnostic task knowledge
2. **Architecture Latent** $z_{\text{arch}} \in \mathbb{R}^{d_a}$: Encodes architecture-specific weight patterns

The full latent code is $z = [z_{\text{task}}; z_{\text{arch}}]$. During training, we encourage disentanglement through:

$$\mathcal{L}_{\text{disentangle}} = \text{MI}(z_{\text{task}}; z_{\text{arch}})$$

estimated using the MINE estimator.

#### 2.2.4 Conditional Decoder

The decoder generates weights conditioned on task descriptors $c$ (e.g., dataset statistics, task embeddings, or natural language descriptions encoded via a frozen language model).

**Conditioning Mechanism**: We fuse task information through FiLM layers:
$$\gamma_c, \beta_c = \text{MLP}_{\text{cond}}([z; c])$$

**Autoregressive Weight Generation**: We generate weights layer-by-layer:

$$W^{(l)} = \text{MLP}_{\text{dec}}^{(l)}\left(\text{FiLM}(z; \gamma_c, \beta_c), W^{(1:l-1)}\right)$$

### 2.3 Training Objective

The complete SymVAE objective combines several terms:

$$\mathcal{L} = \mathcal{L}_{\text{recon}} + \beta \mathcal{L}_{\text{KL}} + \lambda_1 \mathcal{L}_{\text{canon}} + \lambda_2 \mathcal{L}_{\text{disentangle}} + \lambda_3 \mathcal{L}_{\text{func}}$$

**Reconstruction Loss**: 
$$\mathcal{L}_{\text{recon}} = \mathbb{E}_{q_\phi(z|W)}\left[\|W - \hat{W}\|_2^2\right]$$

**KL Divergence**:
$$\mathcal{L}_{\text{KL}} = D_{\text{KL}}(q_\phi(z|W) \| p(z))$$

**Canonicalization Consistency**:
$$\mathcal{L}_{\text{canon}} = \mathbb{E}_{\pi \sim \mathcal{G}_\pi}\left[\|\mathcal{C}_\phi(W) - \mathcal{C}_\phi(\pi \cdot W)\|_2^2\right]$$

**Functional Loss** (ensures generated weights perform the intended task):
$$\mathcal{L}_{\text{func}} = \mathbb{E}_{(x,y) \sim \mathcal{D}_c}\left[\ell(f_{\hat{W}}(x), y)\right]$$

### 2.4 Experimental Design

#### 2.4.1 Datasets

1. **Model Zoos**: We will curate collections of trained networks:
   - MNIST/CIFAR-10 classifiers (MLPs and CNNs) with varying hyperparameters
   - INR weights from ShapeNet and SIREN-based image representations
   - Pre-trained models from Hugging Face for larger-scale experiments

2. **Task Descriptors**: For each model, we store:
   - Training dataset statistics
   - Architecture specifications
   - Performance metrics
   - Natural language task descriptions

#### 2.4.2 Baselines

- **DeepWeightFlow**: Flow matching with Git Re-Basin canonicalization
- **HyperNetworks**: Standard hypernetwork weight generation
- **Neural Functional Transformers**: Recent transformer-based approaches
- **Vanilla VAE**: VAE without symmetry handling (ablation)

#### 2.4.3 Evaluation Metrics

1. **Generation Quality**:
   - Functional accuracy of generated weights on held-out test sets
   - FID-like metrics adapted for weight distributions

2. **Interpolation Smoothness**:
   - Functional similarity along latent interpolation paths
   - Loss landscape analysis between interpolated weights

3. **Symmetry Handling**:
   - Variance of latent codes across equivalent weight configurations
   - Canonicalization consistency metric

4. **Transfer Efficiency**:
   - Few-shot adaptation performance using generated initializations
   - Training speedup compared to random initialization

5. **Computational Efficiency**:
   - Generation time vs. training from scratch
   - Memory footprint and scalability analysis

#### 2.4.4 Ablation Studies

- Effect of learned vs. fixed canonicalization
- Impact of hierarchical latent structure
- Contribution of functional loss
- Scalability to larger architectures

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Technical Contributions**:
   - A novel learned canonicalization approach that adapts to data distributions
   - Theoretically grounded equivariant encoder architecture for weight spaces
   - Hierarchical latent space enabling disentangled task and architecture representations

2. **Empirical Results**:
   - State-of-the-art weight generation quality on INR synthesis benchmarks
   - Improved interpolation smoothness in weight space
   - Efficient few-shot model adaptation through generated initializations

3. **Open Resources**:
   - Released model zoo datasets with standardized formats
   - Open-source implementation of SymVAE
   - Pre-trained models for common architectures

### Broader Impact

This research directly addresses the workshop's core questions about weight space properties, efficient representation, and practical weight generation. By developing principled methods for handling symmetries, SymVAE could enable:

- **Democratized AI Development**: Reducing computational costs through efficient weight synthesis
- **Accelerated Research**: Rapid prototyping via task-conditioned model generation
- **Sustainable AI**: Decreased energy consumption by avoiding redundant training

Furthermore, our theoretical analysis of canonicalization and equivariant processing will contribute to the foundational understanding of weight spaces as a data modality, fostering the interdisciplinary collaboration this workshop aims to promote.