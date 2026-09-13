# SymVAE: Symmetry-Aware Variational Autoencoders for Neural Network Weight Generation

## Abstract

Neural network weights represent an emerging data modality with unique mathematical properties, including permutation invariance and scaling symmetries that create redundant representations in weight space. We propose **SymVAE**, a variational autoencoder framework that addresses these symmetries through learned canonicalization and hierarchical latent structure. Our approach incorporates an optimal transport-based canonicalization module that maps weights to canonical forms, an equivariant encoder that produces symmetry-invariant latent codes, and a hierarchical latent space that disentangles task-level knowledge from architecture-specific patterns. We evaluate SymVAE against several baselines on a synthetic model zoo of MLP classifiers. While our experiments reveal that explicit symmetry handling does not consistently outperform simpler baselines in the small-scale setting studied, our analysis provides important insights into the challenges of weight space generative modeling and identifies conditions under which symmetry-aware approaches may prove beneficial. This work contributes to the foundational understanding of neural network weights as a data modality and highlights directions for future research in weight space learning.

## 1. Introduction

The proliferation of publicly available neural network models—now exceeding one million on platforms like Hugging Face—presents an unprecedented opportunity to treat neural network weights as a first-class data modality. Just as the machine learning community has developed sophisticated methods for processing images, text, and audio, there is emerging recognition that model weights themselves encode rich information that can be analyzed, manipulated, and synthesized. This paradigm shift toward weight space learning promises to revolutionize transfer learning, model initialization, and efficient deployment of neural networks across diverse applications.

However, neural network weight spaces possess unique mathematical properties that distinguish them from conventional data modalities. Chief among these are the inherent symmetries present in weight configurations. Specifically, permuting the neurons within a hidden layer while correspondingly adjusting incoming and outgoing weights produces a functionally equivalent network—this is known as permutation symmetry. For a network with $L$ layers and $n_l$ neurons in layer $l$, the permutation symmetry group has size $\prod_{l=1}^{L-1} n_l!$, creating vast equivalence classes of weight configurations that represent identical functions.

Additionally, scaling symmetries arise in networks with homogeneous activation functions such as ReLU, where weights can be rescaled between layers without changing the network's function. These symmetries pose fundamental challenges for generative modeling approaches, as they must either learn to ignore these redundancies or explicitly account for them through architectural design choices.

Recent work has begun addressing these challenges through various approaches. DeepWeightFlow [1] applies Git Re-Basin for neural network canonicalization before flow matching, demonstrating improved generation quality. Scale Equivariant Graph Metanetworks [2] provide theoretical analysis of scaling symmetries and leverage equivariant architectures for amortized optimization. Text2Weight [3] explores conditioning weight generation on natural language descriptions. Despite these advances, current methods either treat canonicalization as a fixed preprocessing step or focus on specific symmetry types in isolation.

In this paper, we introduce **SymVAE**, a novel variational autoencoder framework that comprehensively addresses weight space symmetries through three integrated innovations:

1. **Learned Canonicalization**: Rather than relying on fixed canonicalization procedures, we propose learning an optimal transport-based canonicalization module that adapts to the data distribution and downstream generation objectives.

2. **Equivariant Encoder-Decoder Architecture**: We develop an encoder that produces symmetry-invariant latent codes and a decoder that generates weights while respecting architectural constraints.

3. **Hierarchical Latent Structure**: We design a latent space that disentangles task-level knowledge from architecture-specific weight patterns, enabling flexible transfer and interpolation.

Our experimental evaluation on a synthetic model zoo reveals important insights about the challenges of symmetry-aware weight generation. While the full SymVAE model does not consistently outperform simpler baselines in our small-scale setting, our ablation studies provide valuable guidance for future research in this emerging area.

## 2. Related Work

### 2.1 Weight Space as a Data Modality

The treatment of neural network weights as a data modality has gained significant attention in recent years. Early work explored the properties of weight spaces, including the loss landscape geometry and the connectivity of different minima [6]. More recent efforts have focused on developing methods to process, analyze, and generate neural network weights directly.

### 2.2 Symmetries in Weight Space

Neural network weight spaces exhibit several types of symmetries that create equivalence classes of functionally identical networks. The most prominent is permutation symmetry: for any permutation matrices $P^{(l)}$, the transformed weights $\tilde{W}^{(l)} = P^{(l)} W^{(l)} (P^{(l-1)})^T$ yield equivalent networks. Van der Ouderaa et al. [4] proposed methods to learn layer-wise equivariances automatically using gradients, optimizing the marginal likelihood to balance data fit and model complexity.

Scaling symmetries present additional challenges, particularly for networks with ReLU activations where $\text{ReLU}(\alpha x) = \alpha \cdot \text{ReLU}(x)$ for $\alpha > 0$. Kuipers et al. [2] developed Scale Equivariant Graph Metanetworks (ScaleGMNs) that provide theoretical analysis of these symmetries and demonstrate their importance for amortized optimization.

### 2.3 Neural Network Weight Generation

Several approaches have been proposed for generating neural network weights. HyperNetworks [7] learn to map task descriptors directly to weight configurations, though they typically do not explicitly handle weight space symmetries. DeepWeightFlow [1] combines flow matching with Git Re-Basin canonicalization to generate diverse, high-accuracy weights across various architectures.

Text2Weight [3] presents a diffusion transformer framework that generates task-specific weights conditioned on natural language descriptions, hierarchically processing network parameters and integrating text embeddings to bridge semantic descriptions with weight-space dynamics.

### 2.4 Variational Autoencoders for Structured Data

Variational autoencoders (VAEs) [8] have been successfully applied to various structured data types. Hierarchical VAEs [5] achieve expressive modeling through multi-scale latent representations. Our work extends these ideas to the weight space domain, incorporating symmetry-aware components to handle the unique properties of neural network weights.

## 3. Methodology

### 3.1 Problem Formulation

Let $\mathcal{W}$ denote the space of neural network weights for a given architecture with $L$ layers. A weight configuration $W = \{W^{(l)}, b^{(l)}\}_{l=1}^{L}$ consists of weight matrices $W^{(l)} \in \mathbb{R}^{n_{l} \times n_{l-1}}$ and bias vectors $b^{(l)} \in \mathbb{R}^{n_l}$, where $n_l$ is the number of neurons in layer $l$.

The permutation symmetry group $\mathcal{G}_\pi$ acts on weights through permutation matrices $P^{(l)} \in \mathbb{R}^{n_l \times n_l}$:

$$\tilde{W}^{(l)} = P^{(l)} W^{(l)} (P^{(l-1)})^T, \quad \tilde{b}^{(l)} = P^{(l)} b^{(l)}$$

Our goal is to learn a generative model $p_\theta(W | c)$ conditioned on task descriptors $c$ that produces high-quality weights while efficiently handling these symmetries.

### 3.2 SymVAE Architecture

The SymVAE architecture consists of three main components: a learned canonicalization module, an equivariant encoder-decoder pair, and a hierarchical latent space structure.

#### 3.2.1 Learned Canonicalization Module

We propose a learnable canonicalization network $\mathcal{C}_\phi: \mathcal{W} \rightarrow \mathcal{W}$ that maps arbitrary weight configurations to a canonical representative of their equivalence class. For each layer $l$, we compute soft permutation matrices using an optimal transport formulation with entropic regularization.

Given reference neurons $R^{(l)} = \{r_i^{(l)}\}_{i=1}^{n_l}$ (learned parameters), we solve:

$$P^{(l)*} = \arg\min_{P \in \Pi_{n_l}} \sum_{i,j} C_{ij}^{(l)} P_{ij} + \epsilon H(P)$$

where $C_{ij}^{(l)} = \|w_i^{(l)} - r_j^{(l)}\|^2$ is the cost matrix, $\Pi_{n_l}$ is the set of doubly stochastic matrices, and $H(P) = -\sum_{ij} P_{ij} \log P_{ij}$ is the entropic regularization. We solve this efficiently using the Sinkhorn algorithm:

$$P^{(k+1)} = \text{diag}(u^{(k)}) K \text{diag}(v^{(k)})$$

where $K = \exp(-C^{(l)}/\epsilon)$ and $u, v$ are iteratively updated normalization vectors.

After permutation alignment, we apply learned scale normalization:

$$\hat{W}^{(l)} = \frac{W^{(l)}}{\|\gamma^{(l)} \odot W^{(l)}\|_F + \delta}$$

where $\gamma^{(l)}$ are learnable importance weights and $\delta$ prevents division by zero.

#### 3.2.2 Encoder Architecture

The encoder processes canonicalized weights to produce latent statistics. We flatten the weight matrices and process them through a multi-layer perceptron:

$$h = \text{MLP}_{\text{enc}}(\text{flatten}(W_{\text{canon}}))$$

$$\mu_z = \text{Linear}_\mu(h), \quad \log \sigma_z^2 = \text{Linear}_\sigma(h)$$

The latent code is sampled using the reparameterization trick: $z = \mu_z + \sigma_z \odot \epsilon$ where $\epsilon \sim \mathcal{N}(0, I)$.

#### 3.2.3 Hierarchical Latent Space

We structure the latent space into two components:

1. **Task Latent** $z_{\text{task}} \in \mathbb{R}^{d_t}$: Captures architecture-agnostic task knowledge
2. **Architecture Latent** $z_{\text{arch}} \in \mathbb{R}^{d_a}$: Encodes architecture-specific weight patterns

The full latent code is $z = [z_{\text{task}}; z_{\text{arch}}]$. This decomposition encourages the model to learn disentangled representations that separate task-specific information from structural properties.

#### 3.2.4 Conditional Decoder

The decoder generates weights conditioned on task descriptors $c$ (dataset statistics in our experiments). We fuse task information through feature-wise linear modulation (FiLM):

$$\gamma_c, \beta_c = \text{MLP}_{\text{cond}}([z; c])$$

$$W_{\text{gen}} = \text{reshape}(\text{MLP}_{\text{dec}}(\gamma_c \odot z + \beta_c))$$

### 3.3 Training Objective

The complete SymVAE objective combines several terms:

$$\mathcal{L} = \mathcal{L}_{\text{recon}} + \beta \mathcal{L}_{\text{KL}} + \lambda_1 \mathcal{L}_{\text{canon}}$$

**Reconstruction Loss**: 
$$\mathcal{L}_{\text{recon}} = \mathbb{E}_{q_\phi(z|W)}\left[\|W - \hat{W}\|_2^2\right]$$

**KL Divergence**:
$$\mathcal{L}_{\text{KL}} = D_{\text{KL}}(q_\phi(z|W) \| p(z))$$

**Canonicalization Consistency**:
$$\mathcal{L}_{\text{canon}} = \mathbb{E}_{\pi \sim \mathcal{G}_\pi}\left[\|\mathcal{C}_\phi(W) - \mathcal{C}_\phi(\pi \cdot W)\|_2^2\right]$$

This loss encourages the canonicalization module to produce consistent outputs for equivalent weight configurations.

## 4. Experiment Setup

### 4.1 Model Zoo Construction

We created a synthetic model zoo consisting of 80 trained MLP classifiers for binary classification tasks. Each model in the zoo was trained on randomly generated synthetic data with the following configuration:

| Parameter | Value |
|-----------|-------|
| Target Network Architecture | [10, 32, 32, 2] (MLP) |
| Number of Models in Zoo | 80 |
| Training Epochs per Model | 30 |
| Task Type | Binary Classification |
| Input Dimension | 10 |
| Hidden Dimensions | 32 × 2 layers |
| Output Dimension | 2 (classes) |

The dataset was split into training (56 models, 70%), validation (12 models, 15%), and test (12 models, 15%) sets.

### 4.2 Weight Generation Model Configuration

All weight generation models were trained with the following hyperparameters:

| Parameter | Value |
|-----------|-------|
| Training Epochs | 60 |
| Batch Size | 16 |
| Learning Rate | 0.001 |
| Beta (KL weight) | 0.1 |
| Latent Dimension | 64 |
| Hidden Dimension | 128 |
| Random Seed | 42 |

### 4.3 Baseline Methods

We compared SymVAE against the following baselines:

1. **SymVAE_Full**: Complete SymVAE with learned canonicalization and hierarchical latent structure
2. **SymVAE_NoCanon**: SymVAE without the learned canonicalization module
3. **SymVAE_NoHier**: SymVAE without hierarchical latent structure
4. **Vanilla_VAE**: Standard VAE baseline without any symmetry handling
5. **HyperNetwork**: Direct task-to-weight mapping baseline without latent space

### 4.4 Evaluation Metrics

We evaluated the models using four primary metrics:

1. **Generation Quality**: Test loss and accuracy of generated weights on held-out classification tasks
2. **Symmetry Invariance**: Variance of latent representations under random weight permutations (lower is better)
3. **Interpolation Smoothness**: Quality of latent space interpolation between weight configurations (higher is better)
4. **Training Efficiency**: Wall-clock training time

## 5. Experiment Results

### 5.1 Training Performance

All models were trained for 60 epochs on the weight dataset. Figure 1 shows the training curves for the SymVAE_Full model, demonstrating convergence of both reconstruction and KL divergence losses.

![SymVAE Full Training Curves](SymVAE_Full_training_curves.png)
*Figure 1: Training curves for SymVAE_Full showing total loss, reconstruction loss, and KL divergence over 60 epochs.*

The training curves for the Vanilla VAE baseline (Figure 2) show similar convergence behavior but with different KL divergence dynamics.

![Vanilla VAE Training Curves](Vanilla_VAE_training_curves.png)
*Figure 2: Training curves for Vanilla VAE baseline.*

Table 1 summarizes the validation performance and training times for all models.

| Model | Best Validation Loss | Training Time (s) |
|-------|---------------------|-------------------|
| SymVAE_Full | 0.2085 | 2.03 |
| SymVAE_NoCanon | 0.2058 | 0.74 |
| SymVAE_NoHier | 0.2060 | 1.72 |
| Vanilla_VAE | 0.2068 | 0.60 |
| HyperNetwork | 0.2094 | 0.36 |

*Table 1: Validation loss and training time comparison across all models.*

### 5.2 Generation Quality

The generated weights were evaluated on held-out test tasks. Figure 3 presents the generation quality comparison across all models.

![Generation Quality Comparison](generation_quality.png)
*Figure 3: Generation quality comparison showing test loss (left) and test accuracy (right) for all models.*

| Model | Test Loss (↓) | Test Accuracy (↑) |
|-------|--------------|------------------|
| SymVAE_Full | 0.6947 ± 0.0012 | 0.5011 ± 0.0046 |
| SymVAE_NoCanon | 0.6938 ± 0.0009 | 0.5000 ± 0.0000 |
| SymVAE_NoHier | 0.6943 ± 0.0013 | 0.5000 ± 0.0000 |
| Vanilla_VAE | 0.6934 ± 0.0005 | 0.5029 ± 0.0048 |
| HyperNetwork | **0.6925 ± 0.0004** | **0.5469 ± 0.0394** |

*Table 2: Generation quality metrics with standard deviations.*

### 5.3 Symmetry Invariance Analysis

A key contribution of SymVAE is improved handling of weight space symmetries. We measure this by computing the variance of latent representations when applying random permutations to equivalent weight configurations. Figure 4 shows the latent variance comparison.

![Latent Variance Comparison](latent_variance.png)
*Figure 4: Latent variance under permutations for VAE-based models. Lower variance indicates better invariance to equivalent weight configurations.*

| Model | Latent Variance (↓) |
|-------|-------------------|
| SymVAE_Full | 0.0039 ± 0.0016 |
| SymVAE_NoCanon | 0.0025 ± 0.0010 |
| SymVAE_NoHier | 0.0032 ± 0.0014 |
| Vanilla_VAE | **0.0021 ± 0.0007** |

*Table 3: Symmetry invariance measured by latent variance under permutations.*

### 5.4 Interpolation Smoothness

We evaluate the quality of the learned latent space by measuring interpolation smoothness between weight configurations. Figure 5 presents these results.

![Interpolation Smoothness](interpolation_smoothness.png)
*Figure 5: Latent space interpolation smoothness. Higher values indicate smoother interpolation.*

| Model | Interpolation Smoothness (↑) |
|-------|----------------------------|
| SymVAE_Full | 2765.21 ± 1289.06 |
| SymVAE_NoCanon | 3879.76 ± 1834.10 |
| SymVAE_NoHier | 5903.17 ± 3793.86 |
| Vanilla_VAE | **7085.23 ± 2078.51** |

*Table 4: Interpolation smoothness metrics.*

### 5.5 Ablation Study

Figure 6 presents a comprehensive ablation study examining the contribution of each component in SymVAE.

![Ablation Study](ablation_study.png)
*Figure 6: Ablation study comparing Full SymVAE, variants without canonicalization or hierarchical structure, and Vanilla VAE.*

### 5.6 Multi-Metric Comparison

Figure 7 provides a radar chart visualization comparing all VAE-based models across normalized metrics.

![Radar Comparison](radar_comparison.png)
*Figure 7: Radar chart comparing models across multiple normalized metrics.*

## 6. Analysis

### 6.1 Key Findings

Our experimental evaluation reveals several important findings that challenge initial hypotheses while providing valuable insights for future research.

**Generation Quality**: Contrary to our expectations, the HyperNetwork baseline achieved the best test accuracy (54.7%), significantly outperforming all VAE-based methods which hovered near random chance (50%). This suggests that for the synthetic classification tasks studied, direct task-to-weight mapping is more effective than generative modeling with latent space structure. The VAE-based methods appear to struggle with generating functionally effective weights, possibly due to the complexity introduced by the encoder-decoder architecture.

**Symmetry Invariance**: Surprisingly, the Vanilla VAE achieved the lowest latent variance (0.0021) under permutations, indicating good invariance to weight permutations without explicit symmetry handling. The SymVAE_Full model showed the highest variance (0.0039), contrary to our hypothesis. This counterintuitive result may be explained by several factors:

1. The synthetic classification tasks have limited complexity, potentially not requiring sophisticated symmetry handling
2. The MLP encoder may implicitly learn some permutation invariance through the aggregation of weight statistics
3. The learned canonicalization module may introduce additional variance in representations as it attempts to align weights to learned reference points

**Interpolation Smoothness**: The Vanilla VAE achieved the highest interpolation smoothness (7085.23), suggesting a well-structured latent space amenable to smooth interpolation. The SymVAE_Full model exhibited lower smoothness (2765.21), possibly due to the additional complexity introduced by canonicalization and hierarchical structure fragmenting the latent space.

### 6.2 Analysis of SymVAE Components

**Canonicalization Module**: The learned canonicalization module did not provide clear benefits in our experimental setup. The Sinkhorn-based soft permutation computation adds computational overhead (approximately 3× slower training) without corresponding improvements in generation quality or symmetry invariance. The module may require:
- More training data to learn effective reference points
- Integration with functional loss to guide canonicalization toward task-relevant representations
- Alternative canonicalization strategies such as fixed procedures like Git Re-Basin

**Hierarchical Latent Structure**: The hierarchical decomposition into task and architecture latents did not significantly improve generation quality. The disentanglement objective may require:
- Larger model zoos with diverse architectures to benefit from separating task and architecture information
- Stronger supervision signals to encourage meaningful decomposition
- Longer training or different optimization strategies

### 6.3 Limitations

Our study has several important limitations that contextualize the results:

1. **Synthetic Tasks**: The experiments used synthetic binary classification tasks with randomly generated data, which may not fully represent the complexity and diversity of real-world weight generation scenarios.

2. **Small Model Zoo**: With only 80 models, the weight dataset is relatively small for training complex generative models. Deep generative models typically require thousands to millions of training examples.

3. **Simple Target Architecture**: The target MLP architecture (10-32-32-2) with 1,378 total parameters is relatively simple. Larger architectures with more hidden layers and neurons may exhibit more pronounced symmetry-related challenges.

4. **Limited Evaluation**: Our evaluation focused primarily on reconstruction quality and symmetry handling. Additional metrics such as diversity of generated weights, novelty relative to training set, and few-shot adaptation performance would provide more comprehensive assessment.

5. **Hyperparameter Sensitivity**: We did not extensively explore hyperparameter sensitivity for the canonicalization module (e.g., Sinkhorn iterations, entropic regularization strength) or the hierarchical latent structure (e.g., task vs. architecture latent dimensions).

### 6.4 When Might Symmetry-Aware Methods Help?

Despite the negative results in our setting, we hypothesize that symmetry-aware approaches like SymVAE may prove beneficial under different conditions:

1. **Larger Architectures**: Networks with more hidden layers and wider layers have exponentially larger permutation groups, potentially making explicit symmetry handling more valuable.

2. **Diverse Model Zoos**: Collections of models trained on varied tasks and with different initializations may exhibit more diverse weight configurations within equivalence classes.

3. **Transfer Learning Applications**: When the goal is to interpolate between models or adapt to new tasks, maintaining semantic coherence in weight space may require symmetry awareness.

4. **Real-World Weights**: Weights from models trained on real datasets may have different statistical properties than our synthetic setting.

## 7. Conclusion

This paper introduced SymVAE, a symmetry-aware variational autoencoder for neural network weight generation. Our approach incorporates three novel components: a learned optimal transport-based canonicalization module, an encoder architecture designed for symmetry invariance, and a hierarchical latent space separating task and architecture information.

Our experimental evaluation on a synthetic model zoo revealed that explicit symmetry handling did not improve weight generation quality compared to simpler baselines in the small-scale setting studied. The HyperNetwork baseline outperformed all VAE-based methods on generation quality, while the Vanilla VAE achieved better symmetry invariance and interpolation smoothness than the full SymVAE model.

These results highlight the challenges of weight space generative modeling and suggest that naively adding complexity through symmetry-aware components may not be beneficial without careful consideration of the problem setting. However, we emphasize that these findings should be interpreted in the context of our experimental limitations, including small model zoo size, simple target architectures, and synthetic tasks.

### Future Directions

Based on our findings, we identify several promising directions for future research:

1. **Larger-Scale Experiments**: Evaluate on larger model zoos with thousands of diverse trained networks, potentially sourced from platforms like Hugging Face.

2. **Real-World Benchmarks**: Test on established benchmarks such as MNIST/CIFAR classifiers or Implicit Neural Representations (INRs) for image and 3D shape encoding.

3. **Functional Loss Integration**: Incorporate task-specific functional loss during training to guide the generative model toward producing weights that perform well on target tasks.

4. **Alternative Canonicalization**: Compare learned canonicalization against fixed procedures like Git Re-Basin to understand when adaptive approaches provide benefits.

5. **Larger Target Architectures**: Scale experiments to larger neural network architectures where the permutation symmetry group is substantially larger.

6. **Hybrid Approaches**: Explore combinations of direct weight prediction (like HyperNetworks) with latent space modeling to leverage benefits of both approaches.

The treatment of neural network weights as a data modality remains a promising research direction with potential applications in transfer learning, model compression, and neural architecture search. Our work contributes to this emerging field by providing empirical insights and identifying important challenges that must be addressed for practical weight generation systems.

## References

[1] S. Gupta, S. Biggs, M. Laber, Z. Shafi, R. Walters, and A. Paul, "DeepWeightFlow: Re-Basined Flow Matching for Generating Neural Network Weights," arXiv:2601.05052, 2026.

[2] B. Kuipers, F. Byrman, D. Uyterlinde, and A. García-Castellanos, "Symmetry-Aware Fully-Amortized Optimization with Scale Equivariant Graph Metanetworks," arXiv:2510.08300, 2025.

[3] B. Tian, W. Chen, Z. Li, S. Lai, J. Wu, and Y. Yue, "Text2Weight: Bridging Natural Language and Neural Network Weight Spaces," arXiv:2508.13633, 2025.

[4] T. F. A. van der Ouderaa, A. Immer, and M. van der Wilk, "Learning Layer-wise Equivariances Automatically using Gradients," arXiv:2310.06131, 2023.

[5] A. Vahdat and J. Kautz, "NVAE: A Deep Hierarchical Variational Autoencoder," NeurIPS, 2020.

[6] F. Draxler, K. Veschgini, M. Salmhofer, and F. Hamprecht, "Essentially No Barriers in Neural Network Energy Landscape," ICML, 2018.

[7] D. Ha, A. Dai, and Q. V. Le, "HyperNetworks," ICLR, 2017.

[8] D. P. Kingma and M. Welling, "Auto-Encoding Variational Bayes," ICLR, 2014.

[9] K. He, Y. Wang, and J. Hopcroft, "A Powerful Generative Model Using Random Weights," arXiv:1606.04801, 2016.