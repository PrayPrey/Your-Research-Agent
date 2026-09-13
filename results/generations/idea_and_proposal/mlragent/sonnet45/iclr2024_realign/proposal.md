# Causal Intervention Framework for Controllable Representational Alignment in Neural Networks

## 1. Introduction

### Background

Representational alignment—the degree to which different intelligent systems develop similar internal representations—has emerged as a central question in modern machine learning, neuroscience, and cognitive science. Recent work has demonstrated surprising convergence between artificial neural networks and biological systems, with deep learning models showing alignment with primate visual cortex, human language processing regions, and motor control circuits. However, current research faces a fundamental limitation: while we have developed increasingly sophisticated metrics for *measuring* alignment (CKA, RSA, Procrustes distance, Hierarchical Optimal Transport), we lack principled methods for *controlling* and *manipulating* alignment in a systematic, causal manner.

This gap is critical for several reasons. First, observational studies of alignment cannot definitively establish whether shared representations reflect genuine computational equivalence or merely correlational artifacts driven by shared input statistics and architectural biases. Recent work by Kapoor et al. (2025) demonstrates that significant convergence occurs early in training, suggesting that alignment may emerge from factors other than task-specific learning. Second, without the ability to systematically intervene on alignment, we cannot test mechanistic hypotheses about what drives representational similarity. Third, engineering applications—such as designing interpretable AI systems that align with human cognitive strategies or creating robust models through alignment with biological computation—require active control over the alignment process rather than passive observation.

### Research Objectives

This research proposes a **Causal Intervention Framework for Controllable Representational Alignment** with three primary objectives:

1. **Develop steering mechanisms** that enable targeted manipulation of representational alignment through differentiable objectives and architectural modifications, creating "alignment knobs" that can systematically increase or decrease similarity to target systems.

2. **Establish causal relationships** between specific architectural components, training procedures, and resulting alignment patterns through controlled ablation studies and intervention experiments.

3. **Empirically validate** when and why representational alignment corresponds to shared computational strategies versus superficial similarity, and quantify the relationship between representational alignment and behavioral outcomes.

### Significance

This work addresses central questions posed by the Workshop on Representational Alignment: it provides tools to systematically increase or decrease alignment among biological and artificial systems, establishes whether alignment indicates shared computational strategies through causal testing, and develops robust measurement approaches that account for confounding factors. The framework has theoretical implications for understanding the nature of representation learning and practical applications for interpretable AI design, neural-AI alignment for brain-computer interfaces, and minimal intervention strategies for behavioral alignment.

## 2. Methodology

### 2.1 Alignment Steering Mechanisms

#### 2.1.1 Differentiable Alignment Objectives

We formulate representational alignment as a differentiable training objective that can be optimized alongside task performance. Given a source model $f_s$ and target system $f_t$ (which may be another neural network, biological neural recordings, or behavioral data), we define composite loss functions:

For **alignment-promoting** training:
$$\mathcal{L}_{\text{align}} = \mathcal{L}_{\text{task}} + \lambda_{\text{align}} \mathcal{L}_{\text{repr}}$$

For **alignment-reducing** training:
$$\mathcal{L}_{\text{misalign}} = \mathcal{L}_{\text{task}} + \lambda_{\text{misalign}} (-\mathcal{L}_{\text{repr}} + \mathcal{R}_{\text{div}})$$

where $\mathcal{L}_{\text{task}}$ is the primary task loss (e.g., cross-entropy), $\mathcal{L}_{\text{repr}}$ measures representational similarity, and $\mathcal{R}_{\text{div}}$ is a diversity regularizer preventing representational collapse.

We implement multiple alignment metrics as differentiable objectives:

**Centered Kernel Alignment (CKA)**: For activations $X \in \mathbb{R}^{n \times p_1}$ and $Y \in \mathbb{R}^{n \times p_2}$ from source and target:
$$\mathcal{L}_{\text{CKA}} = 1 - \frac{\text{tr}(K_X K_Y)}{\sqrt{\text{tr}(K_X^2)\text{tr}(K_Y^2)}}$$
where $K_X = XX^T - \frac{1}{n}\mathbf{1}\mathbf{1}^T XX^T$ is the centered Gram matrix.

**Soft Nearest Neighbor Loss**: Inspired by contrastive learning:
$$\mathcal{L}_{\text{SNN}} = -\mathbb{E}_{x_i}\left[\log \frac{\exp(\text{sim}(f_s(x_i), f_t(x_i))/\tau)}{\sum_{j}\exp(\text{sim}(f_s(x_i), f_t(x_j))/\tau)}\right]$$

**Representational Dissimilarity Matrix (RDM) Alignment**:
$$\mathcal{L}_{\text{RDM}} = \|D_s - D_t\|_F^2$$
where $D_s, D_t$ are pairwise dissimilarity matrices of representations.

#### 2.1.2 Adversarial Alignment Regularization

To test whether alignment can be actively prevented while maintaining task performance, we introduce an adversarial component:

$$\min_{\theta_f} \max_{\theta_g} \mathcal{L}_{\text{task}}(\theta_f) - \lambda \mathcal{L}_{\text{disc}}(\theta_g, \theta_f)$$

where $\theta_g$ parameterizes a discriminator attempting to predict whether representations come from the source or target system. This ensures that the model learns task-relevant features while minimizing detectable similarity to the target.

#### 2.1.3 Layer-Specific Alignment Control

Building on insights from Shah & Khosla (2025) regarding hierarchical alignment, we implement layer-specific alignment objectives:

$$\mathcal{L}_{\text{layer}} = \sum_{l=1}^L w_l \cdot \mathcal{L}_{\text{repr}}(h_s^{(l)}, h_t^{(\pi(l))})$$

where $w_l$ are learnable or prescribed weights, and $\pi(l)$ maps source layers to target layers using optimal transport:

$$\pi^* = \arg\min_{\pi} \sum_{l,l'} c(l,l') \pi(l,l')$$

subject to marginal constraints, where $c(l,l')$ measures the cost of matching layers.

### 2.2 Systematic Ablation Studies

#### 2.2.1 Architectural Component Removal

We design controlled ablation experiments to identify which architectural elements contribute to alignment:

1. **Attention mechanism ablations**: Systematically remove attention heads in transformer models, measuring alignment changes using attribution methods to identify heads most responsible for target similarity.

2. **Layer type variations**: Replace standard components (e.g., convolutional layers with fully connected, or vice versa) and measure resulting alignment shifts.

3. **Normalization scheme modifications**: Test batch normalization, layer normalization, group normalization variants to assess their role in representational convergence.

For each ablation, we compute:
$$\Delta_{\text{align}} = \mathcal{A}(f_{\text{ablated}}, f_t) - \mathcal{A}(f_{\text{full}}, f_t)$$
$$\Delta_{\text{perf}} = \text{Acc}(f_{\text{full}}) - \text{Acc}(f_{\text{ablated}})$$

where $\mathcal{A}$ is an alignment metric. This reveals whether components contribute to alignment independently of task performance.

#### 2.2.2 Training Procedure Interventions

We manipulate training dynamics to assess their causal role in alignment:

1. **Data curriculum**: Train with progressively increasing diversity to test whether alignment emerges from simple shared statistics.

2. **Optimization algorithms**: Compare SGD, Adam, and second-order methods to assess whether optimization trajectory affects alignment.

3. **Initialization schemes**: Use controlled initialization (Xavier, He, orthogonal) and measure alignment evolution from random initialization.

### 2.3 Controlled Experimental Design

#### 2.3.1 Model Families with Varying Alignment Levels

We construct model families systematically varying in alignment to a fixed target (e.g., primate IT cortex recordings or human behavioral data):

- **High-alignment models**: Trained with $\lambda_{\text{align}} \in \{1.0, 5.0, 10.0\}$
- **Medium-alignment models**: Standard task-only training ($\lambda_{\text{align}} = 0$)
- **Low-alignment models**: Adversarially de-aligned with $\lambda_{\text{misalign}} \in \{1.0, 5.0, 10.0\}$

Each family includes 10 replications with different random seeds to ensure statistical reliability.

#### 2.3.2 Multi-Domain Validation

To ensure generalizability, we conduct experiments across three domains:

**Vision Domain**: 
- Target: Primate IT cortex neural recordings from publicly available datasets
- Models: ResNet, Vision Transformer, ConvNeXT variants
- Tasks: ImageNet classification, object recognition

**Language Domain**:
- Target: fMRI recordings from human language processing (e.g., Pereira et al. dataset)
- Models: BERT, GPT, RoBERTa variants
- Tasks: Natural language understanding benchmarks

**Motor Control Domain**:
- Target: Mouse/primate motor cortex recordings
- Models: Recurrent networks (LSTM, GRU), Transformers
- Tasks: Reaching trajectory prediction, motor sequence generation

#### 2.3.3 Evaluation Protocol

For each trained model, we assess:

**Representational Alignment Metrics**:
- CKA across layers
- RSA correlation
- Procrustes distance
- HOT hierarchical alignment scores

**Behavioral Similarity**:
- Confusion matrix correlation with target system
- Error consistency (proportion of shared errors)
- Response time correlation (where applicable)

**Generalization Properties**:
- Out-of-distribution generalization on shifted datasets
- Few-shot learning performance
- Adversarial robustness (PGD, FGSM attacks)

**Computational Efficiency**:
- Parameter count
- FLOPs required
- Inference time

### 2.4 Causal Mediation Analysis

To establish causal pathways from interventions to alignment to behavior, we employ mediation analysis:

$$\text{Total Effect} = \text{Direct Effect} + \text{Indirect Effect}_{\text{via alignment}}$$

Formally, we estimate:
$$\text{IE}_{\text{align}} = \mathbb{E}[\text{Behavior}(M(X=1)) - \text{Behavior}(M(X=0))]$$

where $X$ is the intervention (e.g., alignment loss weight), $M$ is the mediator (representational alignment), and Behavior is the outcome (e.g., task accuracy, generalization).

### 2.5 Datasets and Computational Resources

**Biological Data**:
- Primate neural recordings: Majaj et al. IT cortex dataset
- Human fMRI: Natural language processing datasets (Pereira et al.)
- Mouse neural recordings: Steinmetz et al. Neuropixels dataset

**Benchmark Datasets**:
- Vision: ImageNet-1K, ImageNet-C (corruptions), ObjectNet (OOD)
- Language: GLUE, SuperGLUE, SQuAD
- Motor: Reaching datasets from neuroscience repositories

**Computational Requirements**:
- GPU cluster: 4-8 NVIDIA A100 GPUs
- Estimated compute: ~5000 GPU-hours for full experimental suite
- Storage: ~500 GB for model checkpoints and activation caches

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Theoretical Contributions**:

1. **Causal taxonomy of alignment factors**: We expect to identify specific architectural components (e.g., particular normalization schemes, skip connections) and training choices (e.g., batch size, learning rate schedules) that causally influence alignment, quantifying their individual and interactive effects.

2. **Dissociation of alignment types**: We anticipate finding cases where high representational alignment (measured by CKA) does not predict behavioral alignment, particularly in out-of-distribution scenarios, establishing that superficial similarity does not guarantee computational equivalence.

3. **Alignment dynamics theory**: Results should reveal whether alignment is primarily determined early in training by architectural priors and data statistics (supporting Kapoor et al.'s findings) or whether task-specific learning drives late-stage alignment in deeper layers.

**Methodological Contributions**:

1. **Alignment control toolkit**: A software package implementing differentiable alignment objectives, ablation utilities, and evaluation metrics, enabling other researchers to conduct controlled alignment experiments.

2. **Benchmark suite**: Standardized experimental protocols and datasets for evaluating alignment interventions across vision, language, and motor domains.

3. **Best practices guide**: Evidence-based recommendations for when alignment-promoting training is beneficial versus detrimental for specific applications.

**Empirical Findings**:

1. **Quantified alignment-behavior relationships**: Precise characterization of how varying representational alignment (e.g., CKA from 0.3 to 0.9) affects generalization, robustness, and interpretability metrics.

2. **Minimal intervention strategies**: Identification of the smallest architectural or training changes needed to achieve desired alignment levels, enabling efficient alignment engineering.

3. **Domain-specific patterns**: Discovery of whether alignment mechanisms generalize across domains or require domain-specific approaches.

### 3.2 Impact

**Scientific Impact**:

This framework addresses fundamental questions in representational learning by moving from correlational observation to causal manipulation. It provides mechanistic insights into why certain architectures converge to similar solutions and tests the hypothesis that alignment reflects shared computational strategies. The work bridges machine learning, neuroscience, and cognitive science by providing common tools for studying representation across these fields.

**Engineering Impact**:

The ability to control alignment enables several practical applications:

1. **Interpretable AI design**: Engineers can train models that align with human cognitive representations, improving explainability and trust in high-stakes domains (medical diagnosis, autonomous vehicles).

2. **Brain-computer interfaces**: Improved alignment between artificial and biological neural systems could enhance neural prosthetics and brain-computer interface performance.

3. **Efficient knowledge transfer**: Understanding alignment mechanisms informs better transfer learning and domain adaptation strategies.

4. **Robustness engineering**: If biological systems exhibit superior robustness, alignment-promoting training could transfer these properties to artificial systems.

**Societal Impact**:

Controllable alignment has implications for AI safety and value alignment. By understanding how to align AI representations with human cognitive strategies, we can potentially build systems whose reasoning is more transparent and whose failures are more predictable. Conversely, the framework also reveals risks: adversarial actors could use alignment-reducing techniques to create systems that are deliberately opaque.

### 3.3 Limitations and Future Work

**Limitations**:

1. **Biological data constraints**: Neural recordings have limited coverage, resolution, and variability across subjects, potentially restricting the scope of biological alignment experiments.

2. **Computational costs**: Systematic exploration of large architecture and hyperparameter spaces requires substantial computational resources.

3. **Metric dependence**: Results may vary depending on chosen alignment metrics; no single metric perfectly captures representational similarity.

**Future Directions**:

1. **Dynamic alignment**: Extend to continual learning settings where alignment must be maintained or adapted over time.

2. **Multi-target alignment**: Develop methods for aligning with multiple target systems simultaneously (e.g., multiple brain regions or human participants).

3. **Theoretical foundations**: Develop information-theoretic or geometric frameworks that predict when alignment should emerge from first principles.

This research establishes a rigorous, causal approach to understanding and controlling representational alignment, providing both theoretical insights into the nature of learned representations and practical tools for engineering interpretable, robust, and human-compatible AI systems.