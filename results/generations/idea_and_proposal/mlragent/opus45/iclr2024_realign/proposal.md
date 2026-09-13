# Research Proposal: Causal Intervention Framework for Bidirectional Representational Alignment

## 1. Introduction

### Background

Understanding how intelligent systems—both biological and artificial—represent information is a fundamental challenge spanning machine learning, neuroscience, and cognitive science. Recent advances have enabled increasingly sophisticated measurements of representational similarity between neural networks and biological systems using metrics such as Centered Kernel Alignment (CKA), Representational Similarity Analysis (RSA), and newer approaches like Hierarchical Optimal Transport (Shah & Khosla, 2025). These measurement tools have revealed surprising convergences: deep neural networks trained on visual tasks develop representations remarkably similar to those found in primate visual cortex, and language models exhibit activation patterns that correlate with human neural recordings during language processing.

However, a critical gap exists in the current research landscape. While we have developed sophisticated tools for *measuring* representational alignment, we lack systematic frameworks for *intervening* on alignment—for deliberately increasing or decreasing the similarity between artificial and biological representations. This limitation constrains both scientific understanding and engineering applications. Scientifically, without causal intervention capabilities, we cannot distinguish whether observed alignments reflect shared computational strategies or mere correlational artifacts. From an engineering perspective, we cannot systematically build AI systems that interface optimally with human cognition or that intentionally diverge to provide complementary capabilities.

Recent work has highlighted several challenges that complicate alignment research. Kapoor et al. (2025) demonstrated that representational alignment evolves differently across network layers and training epochs, with most convergence occurring early in training. Shah and Khosla (2025) showed that depth mismatches between networks require sophisticated alignment methods. Furthermore, Longon et al. (2025) revealed that superposition in neural representations can obscure true alignment, while work on causal interventions (arXiv:2511.04638) demonstrated that naive interventions can produce representations that diverge from natural latent distributions.

### Research Objectives

This research proposes a **Causal Intervention Framework for Bidirectional Representational Alignment (CIFBRA)** with the following primary objectives:

1. Develop differentiable alignment objectives that can be incorporated as auxiliary losses during neural network training, enabling controlled manipulation of representational alignment with biological systems.

2. Create a systematic taxonomy of interventions categorized by network layer, modality, and alignment direction (toward or away from biological representations).

3. Establish causal relationships between representational alignment and downstream behavioral outcomes, including task performance, generalization, and human-AI collaboration effectiveness.

4. Provide practical tools and guidelines for alignment-aware model development that bridge the measurement-intervention gap.

### Significance

This research addresses a fundamental question posed by the Re-Align workshop: "How can we systematically increase (or decrease) representational alignment among biological and artificial systems?" By developing causal intervention tools, we can move beyond correlational observations to test mechanistic hypotheses about shared computational strategies. The framework will enable researchers to determine which representational components are causally necessary for behavioral alignment, opening new avenues for both understanding biological intelligence and engineering more effective AI systems.

## 2. Methodology

### 2.1 Overview

The proposed framework consists of three interconnected components: (1) Bidirectional Alignment Losses, (2) Intervention Taxonomy and Implementation, and (3) Behavioral Consequence Mapping. Each component addresses a specific aspect of the measurement-intervention gap.

### 2.2 Bidirectional Alignment Losses

#### 2.2.1 Differentiable Alignment Objectives

We define a family of differentiable alignment objectives that can serve as auxiliary training losses. Let $\mathbf{X} \in \mathbb{R}^{n \times d_x}$ represent activations from an artificial neural network for $n$ stimuli, and $\mathbf{Y} \in \mathbb{R}^{n \times d_y}$ represent corresponding biological representations (e.g., fMRI voxel patterns, neural population recordings).

**CKA-based Loss**: We formulate a differentiable CKA loss as:

$$\mathcal{L}_{\text{CKA}}(\mathbf{X}, \mathbf{Y}) = 1 - \frac{\text{HSIC}(\mathbf{X}, \mathbf{Y})}{\sqrt{\text{HSIC}(\mathbf{X}, \mathbf{X}) \cdot \text{HSIC}(\mathbf{Y}, \mathbf{Y})}}$$

where HSIC (Hilbert-Schmidt Independence Criterion) is computed as:

$$\text{HSIC}(\mathbf{X}, \mathbf{Y}) = \frac{1}{(n-1)^2} \text{tr}(\mathbf{K}_X \mathbf{H} \mathbf{K}_Y \mathbf{H})$$

Here, $\mathbf{K}_X = \mathbf{X}\mathbf{X}^\top$ and $\mathbf{K}_Y = \mathbf{Y}\mathbf{Y}^\top$ are kernel matrices, and $\mathbf{H} = \mathbf{I} - \frac{1}{n}\mathbf{1}\mathbf{1}^\top$ is the centering matrix.

**RSA-based Loss**: For representational similarity analysis, we define:

$$\mathcal{L}_{\text{RSA}}(\mathbf{X}, \mathbf{Y}) = 1 - \rho(\text{vec}(\mathbf{D}_X), \text{vec}(\mathbf{D}_Y))$$

where $\mathbf{D}_X$ and $\mathbf{D}_Y$ are representational dissimilarity matrices, and $\rho$ denotes Spearman correlation.

**Learned Metric Loss**: To address limitations of fixed metrics, we introduce a learned alignment metric using a neural network $f_\phi$:

$$\mathcal{L}_{\text{learned}}(\mathbf{X}, \mathbf{Y}) = f_\phi(\mathbf{X}, \mathbf{Y}; \theta_{\text{prior}})$$

where $\theta_{\text{prior}}$ encodes prior knowledge about meaningful alignment from previous neuroscience studies.

#### 2.2.2 Controllable Alignment Training

The total training objective combines task performance with alignment control:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{task}} + \lambda \cdot s \cdot \mathcal{L}_{\text{align}}(\mathbf{X}^{(l)}, \mathbf{Y}^{(r)})$$

where $\lambda \geq 0$ controls alignment strength, $s \in \{-1, +1\}$ determines alignment direction (toward or away from biological representations), $l$ indexes the network layer, and $r$ indexes the brain region. For $s = +1$, minimizing $\mathcal{L}_{\text{align}}$ increases alignment; for $s = -1$, it decreases alignment.

To prevent representational collapse when pushing away from biological representations, we add a diversity regularizer:

$$\mathcal{L}_{\text{diversity}} = -\log \det(\mathbf{X}^\top \mathbf{X} + \epsilon \mathbf{I})$$

### 2.3 Intervention Taxonomy

We systematically categorize interventions along four dimensions:

**Layer Position**: 
- Early layers (layers 1-3): typically encoding low-level features
- Middle layers (layers 4-7): intermediate representations  
- Late layers (layers 8+): high-level, task-specific representations

**Modality**:
- Visual representations (V1-IT pathway correspondence)
- Linguistic representations (language processing regions)
- Multimodal representations (cross-modal binding areas)

**Alignment Direction**:
- Positive alignment ($s = +1$): toward biological representations
- Negative alignment ($s = -1$): away from biological representations
- Selective alignment: toward some regions, away from others

**Alignment Strength**:
- Weak intervention: $\lambda \in [0.01, 0.1]$
- Moderate intervention: $\lambda \in [0.1, 1.0]$
- Strong intervention: $\lambda \in [1.0, 10.0]$

### 2.4 Data Collection and Experimental Design

#### 2.4.1 Datasets

**Biological Representations**:
1. Natural Scenes Dataset (NSD): High-resolution fMRI data from 8 subjects viewing 10,000 natural images
2. Neural Latents Benchmark: Neural population recordings from primate motor and visual cortex
3. MEG/EEG language datasets: Temporal dynamics of language processing

**Artificial Systems**:
1. Vision models: ResNet, ViT, CLIP (visual encoder)
2. Language models: GPT-2, LLaMA variants
3. Multimodal models: CLIP, Flamingo

#### 2.4.2 Experimental Protocol

**Experiment 1: Alignment Controllability**

We train models with varying $\lambda$ values and measure resulting alignment using held-out stimuli:

1. Train baseline model on ImageNet with $\lambda = 0$
2. Train alignment-enhanced models with $\lambda \in \{0.01, 0.1, 0.5, 1.0, 5.0\}$, $s = +1$
3. Train alignment-reduced models with same $\lambda$ values, $s = -1$
4. Measure CKA, RSA, and linear predictivity with NSD fMRI data

**Experiment 2: Layer-Specific Intervention Effects**

We apply alignment losses to specific layers and measure propagation effects:

$$\mathcal{L}_{\text{layer-specific}} = \mathcal{L}_{\text{task}} + \sum_{l \in \mathcal{S}} \lambda_l \cdot \mathcal{L}_{\text{align}}(\mathbf{X}^{(l)}, \mathbf{Y}^{(r_l)})$$

where $\mathcal{S}$ is a subset of layers and $r_l$ maps layers to brain regions.

**Experiment 3: Behavioral Consequence Mapping**

We evaluate downstream effects across multiple dimensions:

1. *Task Performance*: Top-1/Top-5 accuracy on ImageNet, transfer learning performance on CIFAR-100, ObjectNet
2. *Generalization*: Out-of-distribution performance on ImageNet-C, ImageNet-R, ImageNet-Sketch
3. *Human-AI Collaboration*: Joint human-AI classification accuracy, calibration of uncertainty estimates with human uncertainty
4. *Adversarial Robustness*: Performance under PGD attacks, correlation between alignment and robustness

#### 2.4.3 Evaluation Metrics

**Alignment Metrics**:
- CKA (linear and RBF kernel variants)
- RSA with Spearman and Pearson correlation
- Linear predictivity (ridge regression $R^2$)
- Hierarchical Optimal Transport score (Shah & Khosla, 2025)

**Behavioral Metrics**:
- Classification accuracy and calibration (ECE)
- Human-AI agreement rate: $\text{Agreement} = \frac{1}{N}\sum_{i=1}^{N} \mathbb{1}[\hat{y}_{\text{AI}}^{(i)} = \hat{y}_{\text{human}}^{(i)}]$
- Collaboration gain: $\Delta_{\text{collab}} = \text{Acc}_{\text{joint}} - \max(\text{Acc}_{\text{AI}}, \text{Acc}_{\text{human}})$

**Control Metrics**:
- Representation diversity: effective dimensionality
- Training stability: loss variance across seeds
- Computational overhead: training time increase

### 2.5 Addressing Key Challenges

**Superposition Handling**: Following Longon et al. (2025), we apply sparse autoencoders to disentangle representations before computing alignment losses:

$$\mathbf{Z} = \text{SparseAE}(\mathbf{X}), \quad \mathcal{L}_{\text{align-disentangled}} = \mathcal{L}_{\text{align}}(\mathbf{Z}, \mathbf{Y})$$

**Divergence Mitigation**: We incorporate the Counterfactual Latent loss (arXiv:2511.04638) to ensure interventions remain within the natural latent distribution:

$$\mathcal{L}_{\text{CL}} = D_{\text{KL}}(p(\mathbf{X}|\text{intervened}) \| p(\mathbf{X}|\text{natural}))$$

**Multi-Scale Alignment**: To address hierarchical organization (arXiv:2506.00000), we define alignment at multiple abstraction levels:

$$\mathcal{L}_{\text{multi-scale}} = \sum_{k=1}^{K} \omega_k \cdot \mathcal{L}_{\text{align}}(\mathbf{X}^{(l_k)}, \mathbf{Y}^{(r_k)})$$

where $k$ indexes abstraction levels from fine to coarse.

## 3. Expected Outcomes & Impact

### Scientific Outcomes

1. **Causal Understanding of Alignment**: By manipulating alignment and observing behavioral consequences, we will establish which representational similarities are causally necessary versus merely correlational. We hypothesize that early-layer alignment is less behaviorally consequential than late-layer alignment for high-level tasks.

2. **Intervention Taxonomy**: A comprehensive characterization of how different intervention types affect both alignment metrics and behavioral outcomes, providing guidance for future research.

3. **Mechanistic Insights**: Identification of specific representational dimensions that drive human-AI behavioral agreement, advancing understanding of shared computational strategies.

### Engineering Outcomes

1. **Alignment-Aware Training Tools**: Open-source PyTorch library implementing differentiable alignment losses, enabling researchers to incorporate alignment objectives into standard training pipelines.

2. **Practical Guidelines**: Best practices for when to increase versus decrease alignment based on application requirements (e.g., increase for human-AI collaboration, potentially decrease for complementary AI capabilities).

3. **Benchmark Suite**: Standardized evaluation protocols for measuring both representational and behavioral alignment.

### Broader Impact

This research addresses the Re-Align workshop's central question about intervention on alignment. Positive impacts include:

- **Improved Human-AI Interaction**: Systems aligned with human representations may be more intuitive and predictable
- **Scientific Discovery**: Causal tools enable testing hypotheses about biological computation
- **Safety Considerations**: Understanding alignment-behavior relationships informs AI safety research

Potential negative implications, such as creating systems that manipulate human cognition, will be addressed through responsible disclosure and collaboration with ethics researchers.

### Limitations and Future Directions

We acknowledge that biological representations are noisy and variable across individuals. Future work should extend this framework to personalized alignment and investigate developmental and learning-induced changes in alignment. Additionally, scaling to larger models and more comprehensive neural datasets will strengthen the generalizability of findings.

Through this causal intervention framework, we aim to transform representational alignment from a descriptive endeavor into a prescriptive science, enabling principled design of AI systems with desired alignment properties.