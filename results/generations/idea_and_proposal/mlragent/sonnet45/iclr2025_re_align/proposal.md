# Causal Interventions for Controlled Representational Alignment in Neural Networks

## 1. Title

**Causal Interventions for Controlled Representational Alignment in Neural Networks: A Systematic Framework for Steering Biological-Artificial Intelligence Correspondence**

## 2. Introduction

### Background

Representational alignment—the degree to which different intelligent systems develop similar internal representations—has emerged as a fundamental concept bridging machine learning, neuroscience, and cognitive science. Recent advances have demonstrated that deep neural networks trained on visual tasks exhibit striking similarities to representations found in biological visual systems (Yamins et al., 2014). However, despite extensive research measuring this phenomenon through metrics like Centered Kernel Alignment (CKA), Representational Similarity Analysis (RSA), and more recently, Hierarchical Optimal Transport (HOT), a critical gap remains: we can measure alignment, but we cannot systematically control it.

Current approaches to representational alignment are primarily observational and correlational. Researchers train models, measure alignment with biological systems, and attempt to infer what architectural or training choices led to observed similarities. This passive stance limits our ability to answer fundamental causal questions: What factors truly drive representational convergence? Can we deliberately engineer systems that align more (or less) with biological intelligence? What are the computational principles that necessitate similar representations across systems facing similar tasks?

The challenge of controlling representational alignment is particularly acute given recent findings. Kapoor et al. (2025) demonstrated that significant alignment occurs early in training, suggesting that shared input statistics and architectural biases drive convergence. However, without intervention tools, we cannot test whether these factors are merely correlated with alignment or causally responsible for it. Similarly, while Geiger et al. (2021) introduced Interchange Intervention Training (IIT) for aligning neural networks with causal models, their framework focuses on abstract causal structures rather than representational alignment with biological systems.

### Research Objectives

This research proposal aims to develop a comprehensive causal intervention framework for systematically manipulating representational alignment between artificial neural networks and biological neural systems. Our specific objectives are:

1. **Design a toolkit of differentiable intervention operators** that can modify intermediate representations in neural networks with controllable strength and interpretability, enabling targeted manipulation of alignment.

2. **Establish causal relationships** between representational properties (geometry, dimensionality, sparsity, temporal dynamics) and alignment metrics by leveraging interventional rather than purely observational data.

3. **Develop alignment gradient methods** that optimize intervention parameters to achieve target alignment levels, treating alignment as a controllable objective rather than an emergent property.

4. **Validate interventions across multiple scales**, measuring downstream effects on behavioral alignment (similarity in task performance patterns) and decision preferences to understand the broader implications of representational control.

5. **Create a principled framework** for researchers to test causal hypotheses about representational alignment, addressing the workshop's central question: "How can scientists and engineers intervene on this alignment?"

### Significance

This research addresses several critical needs in the representational alignment community:

**Theoretical Significance**: By moving from correlation to causation, we can identify which computational principles are necessary versus merely sufficient for alignment. This shifts the field from descriptive to explanatory science, enabling mechanistic understanding of why certain systems converge in representation space.

**Methodological Significance**: The proposed framework provides tools that complement existing measurement approaches. While metrics like CKA and RSA tell us *what* alignment exists, our intervention framework reveals *how* and *why* alignment emerges, directly addressing the workshop's question about advancing measurement approaches.

**Practical Significance**: Controlled alignment has immediate applications in AI interpretability (steering models toward human-understandable representations), neuroscience-inspired AI (deliberately incorporating biological priors), and human-AI collaboration (ensuring complementary rather than redundant representations).

**Ethical Significance**: Understanding how to control alignment addresses concerns about value alignment and behavioral similarity between AI and human decision-making, with implications for AI safety and fairness.

## 3. Methodology

### 3.1 Overall Research Design

Our methodology consists of four interconnected components: (1) intervention operator design, (2) alignment gradient computation, (3) multi-scale validation experiments, and (4) causal discovery protocols. We will implement and evaluate this framework using convolutional neural networks trained on visual tasks, with alignment measured against primate visual cortex representations (using publicly available neural recordings from the Allen Brain Observatory and datasets from Majaj et al., 2015).

### 3.2 Intervention Operator Design

We propose a hierarchical set of differentiable intervention operators $\mathcal{I}_\theta$ that act on intermediate network representations, where $\theta$ parameterizes the intervention strength and specificity.

#### 3.2.1 Geometric Interventions

**Rotation Interventions**: For a layer representation $\mathbf{H} \in \mathbb{R}^{n \times d}$ (where $n$ is batch size and $d$ is feature dimension), we define:

$$\mathcal{I}^{\text{rot}}_\theta(\mathbf{H}) = \mathbf{H}\mathbf{R}_\theta + (1-\alpha)\mathbf{H}$$

where $\mathbf{R}_\theta \in SO(d)$ is a rotation matrix parameterized by $\theta$, and $\alpha \in [0,1]$ controls intervention strength. To maintain differentiability, we parameterize rotations using Lie algebra: $\mathbf{R}_\theta = \exp(\mathbf{A}_\theta)$ where $\mathbf{A}_\theta$ is a skew-symmetric matrix.

**Alignment-Targeted Projection**: Given reference biological representations $\mathbf{B} \in \mathbb{R}^{m \times d'}$, we compute an optimal linear transformation:

$$\mathcal{I}^{\text{proj}}_\theta(\mathbf{H}) = \mathbf{H} + \alpha \mathbf{H}\mathbf{W}_\theta$$

where $\mathbf{W}_\theta$ is optimized to maximize CKA between $\mathbf{H}\mathbf{W}_\theta$ and $\mathbf{B}$.

#### 3.2.2 Structural Interventions

**Selective Pruning**: To test whether sparsity affects alignment, we introduce learned masking:

$$\mathcal{I}^{\text{prune}}_\theta(\mathbf{H}) = \mathbf{H} \odot \sigma(\mathbf{m}_\theta)$$

where $\mathbf{m}_\theta \in \mathbb{R}^d$ are learnable mask parameters, $\sigma$ is the sigmoid function, and $\odot$ denotes element-wise multiplication. During training, we use straight-through estimators for gradient flow.

**Dimensionality Manipulation**: To control effective dimensionality:

$$\mathcal{I}^{\text{dim}}_\theta(\mathbf{H}) = \mathbf{U}_k\mathbf{U}_k^T\mathbf{H}^T$$

where $\mathbf{U}_k$ contains the top-$k$ principal components of $\mathbf{H}$, with $k$ controlled by $\theta$.

#### 3.2.3 Distributional Interventions

**Contrastive Alignment Loss**: To encourage alignment through training objectives:

$$\mathcal{L}^{\text{align}}_\theta = -\log\frac{\exp(\text{sim}(\mathbf{h}_i, \mathbf{b}_i)/\tau)}{\sum_{j=1}^m\exp(\text{sim}(\mathbf{h}_i, \mathbf{b}_j)/\tau)}$$

where $\mathbf{h}_i$ are network representations, $\mathbf{b}_i$ are corresponding biological representations, $\text{sim}(\cdot,\cdot)$ is cosine similarity, and $\tau$ is a temperature parameter controlled by $\theta$.

### 3.3 Alignment Gradient Computation

To enable optimization of intervention parameters toward target alignment levels, we compute gradients of alignment metrics with respect to $\theta$.

For CKA alignment between intervened representations $\tilde{\mathbf{H}} = \mathcal{I}_\theta(\mathbf{H})$ and biological representations $\mathbf{B}$:

$$\text{CKA}(\tilde{\mathbf{H}}, \mathbf{B}) = \frac{\text{tr}(\mathbf{K}_{\tilde{\mathbf{H}}}\mathbf{K}_{\mathbf{B}})}{\sqrt{\text{tr}(\mathbf{K}_{\tilde{\mathbf{H}}}^2)\text{tr}(\mathbf{K}_{\mathbf{B}}^2)}}$$

where $\mathbf{K}_{\tilde{\mathbf{H}}} = \tilde{\mathbf{H}}\tilde{\mathbf{H}}^T$ is the Gram matrix. We compute:

$$\frac{\partial \text{CKA}}{\partial \theta} = \frac{\partial \text{CKA}}{\partial \tilde{\mathbf{H}}} \frac{\partial \tilde{\mathbf{H}}}{\partial \theta}$$

This enables gradient-based optimization to find intervention parameters that achieve target alignment scores $A^*$:

$$\theta^* = \arg\min_\theta |\text{CKA}(\mathcal{I}_\theta(\mathbf{H}), \mathbf{B}) - A^*|^2 + \lambda\|\theta\|^2$$

where $\lambda$ regularizes intervention complexity.

### 3.4 Experimental Design and Validation

#### 3.4.1 Dataset and Models

We will use ImageNet-pretrained ResNet-50 and vision transformers (ViT-B/16) as our artificial neural networks. For biological reference data, we will use:
- Neural recordings from macaque V1, V4, and IT cortex (Majaj et al., 2015)
- fMRI data from human visual cortex (Natural Scenes Dataset; Allen et al., 2022)

#### 3.4.2 Multi-Scale Validation Protocol

**Layer-wise Analysis**: Apply interventions at different network depths (early, middle, late layers) and measure alignment changes across all layers using HOT (Shah & Khosla, 2025) to capture hierarchical correspondence.

**Training Dynamics**: Following Kapoor et al. (2025), apply interventions at different training checkpoints to understand when alignment is most malleable and test whether early-stage interventions have lasting effects.

**Cross-Modal Transfer**: Test whether interventions that increase alignment in one modality (e.g., visual) transfer to other modalities (e.g., auditory), addressing generalization challenges.

#### 3.4.3 Causal Discovery Protocol

To establish causal relationships, we employ a systematic intervention schedule:

1. **Baseline Measurement**: Measure alignment without interventions across layers and training stages.

2. **Single-Factor Interventions**: Apply each intervention type independently with varying strengths $\alpha \in \{0.2, 0.4, 0.6, 0.8, 1.0\}$.

3. **Factorial Design**: Test combinations of interventions to identify interaction effects (e.g., does rotation + pruning differ from additive effects?).

4. **Counterfactual Testing**: For each intervention that increases alignment, apply the "opposite" intervention (e.g., anti-alignment projection) to verify causal directionality.

5. **Mediator Analysis**: Measure intermediate representational properties (effective dimensionality, sparsity, geodesic distance) to identify mechanistic pathways.

### 3.5 Evaluation Metrics

#### 3.5.1 Alignment Metrics

- **CKA**: For transformation-invariant similarity
- **RSA**: For second-order relational structure
- **HOT**: For hierarchical layer-to-layer correspondence
- **Procrustes Distance**: After optimal linear alignment

#### 3.5.2 Behavioral Alignment Metrics

To measure downstream effects:

$$\text{BehavAlign} = \text{corr}(\text{errors}_{\text{model}}, \text{errors}_{\text{human}})$$

measuring correlation between model and human error patterns across stimuli.

#### 3.5.3 Performance Metrics

- **Task Accuracy**: Classification performance on ImageNet validation
- **Out-of-Distribution Robustness**: Performance on ImageNet-C, ImageNet-R
- **Transfer Learning Efficiency**: Fine-tuning performance on downstream tasks

#### 3.5.4 Intervention Complexity

To prefer simpler interventions:

$$\text{Complexity}(\theta) = \|\theta\|_1 + \text{KL}(\mathcal{I}_\theta(\mathbf{H})\|\mathbf{H})$$

measuring both parameter magnitude and distributional change.

### 3.6 Statistical Analysis

We will employ:
- **Mixed-effects models** to account for variability across layers, models, and datasets
- **Causal mediation analysis** to decompose total intervention effects into direct and mediated pathways
- **Bayesian model comparison** to assess evidence for different causal hypotheses
- **Permutation tests** for statistical significance of alignment changes (10,000 permutations)

### 3.7 Implementation Details

All experiments will be implemented in PyTorch with the following specifications:
- Batch size: 128
- Intervention optimization: Adam optimizer, learning rate 0.001
- Training duration for intervention parameters: 10 epochs
- Hardware: 4× NVIDIA A100 GPUs
- Reproducibility: All code, trained models, and intervention parameters will be open-sourced

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcomes:**

1. **Causal Intervention Toolkit**: A comprehensive, open-source library implementing all proposed intervention operators with documented APIs and tutorials. This toolkit will enable researchers to systematically test causal hypotheses about representational alignment.

2. **Causal Hierarchy of Alignment Factors**: A quantitative ranking of which representational properties (geometry, dimensionality, sparsity, temporal dynamics) causally influence alignment versus those that merely correlate, with effect sizes measured through interventional experiments.

3. **Alignment-Performance Trade-off Curves**: Empirical characterization of how increasing/decreasing alignment affects task performance, OOD robustness, and transfer learning efficiency, informing when alignment is beneficial versus detrimental.

4. **Mechanistic Insights**: Identification of specific computational principles that necessitate representational convergence (e.g., "optimal linear separability of classes requires similar geometric structure") versus domain-specific accidents.

**Secondary Outcomes:**

5. **Layer-Specific Intervention Strategies**: Guidelines for which interventions are most effective at different network depths, informed by hierarchical alignment dynamics.

6. **Cross-Modal Generalization Patterns**: Evidence regarding whether interventions that increase alignment in vision transfer to other modalities or remain domain-specific.

7. **Behavioral-Representational Alignment Link**: Quantitative models relating representational similarity to behavioral similarity, addressing whether aligned representations guarantee aligned decisions.

### 4.2 Scientific Impact

**Advancing Representational Alignment Theory**: This work shifts the field from descriptive to mechanistic science. By demonstrating that specific interventions causally increase alignment, we move beyond correlational studies toward understanding the computational necessities that drive convergence.

**Resolving Metric Debates**: By showing which interventions affect different metrics differently, we provide empirical grounding for ongoing debates about metric selection. If an intervention that should theoretically increase alignment (based on domain knowledge) affects CKA but not RSA, this suggests which metric better captures meaningful alignment.

**Informing Neuroscience**: If specific interventions increase alignment while maintaining task performance, this suggests that biological systems may implement similar computational strategies for reasons other than task optimization (e.g., metabolic efficiency, robustness).

### 4.3 Practical Impact

**Improved AI Interpretability**: Alignment-increasing interventions can steer models toward more human-interpretable representations, facilitating debugging and verification of AI systems.

**Neuroscience-Inspired AI Design**: Rather than hoping architectures naturally align with biology, engineers can deliberately incorporate interventions that enforce biological priors where beneficial.

**Human-AI Collaboration**: By controlling alignment, we can engineer systems with complementary rather than redundant representations, improving collaborative performance.

**Fairness and Bias Mitigation**: Understanding how interventions affect representational structure enables targeted debiasing while maintaining alignment with desired reference systems.

### 4.4 Broader Impacts

**Addressing Workshop Themes**: This research directly addresses the Re-Align workshop's central questions:
- *When do systems learn aligned representations?* We identify causal factors through intervention.
- *How can we intervene?* We provide concrete, validated intervention methods.
- *What are the implications?* We measure behavioral and performance consequences.

**Reproducibility and Standardization**: By providing open-source tools and comprehensive experimental protocols, we contribute to the workshop hackathon goals of establishing common methodologies and increasing reproducibility.

**Interdisciplinary Bridge**: The framework connects machine learning (intervention methods), neuroscience (biological reference data), and cognitive science (behavioral alignment metrics), exemplifying the interdisciplinary collaboration the workshop seeks to foster.

**Ethical Considerations**: We will explicitly document potential misuse cases (e.g., malicious alignment manipulation) and provide guidelines for responsible use of alignment control methods, contributing to broader discussions of AI safety and value alignment.

### 4.5 Limitations and Future Directions

**Limitations**: Our initial scope focuses on visual processing in feedforward networks. Recurrent dynamics, attention mechanisms, and other modalities present additional complexity. The biological reference data comes from constrained laboratory settings, which may not capture full ecological representational richness.

**Future Directions**: Extensions include (1) temporally-structured interventions for recurrent networks, (2) multi-objective optimization balancing alignment with multiple reference systems, (3) meta-learning approaches to discover optimal intervention strategies, and (4) application to large language models with human cognitive linguistic representations as reference.

This research proposal presents a systematic, causal approach to one of representational alignment's most pressing challenges: moving from measurement to control. By developing principled intervention methods, we enable the scientific community to test mechanistic hypotheses and engineers to deliberately shape representational structure, advancing both our theoretical understanding and practical capabilities in aligning artificial and biological intelligence.