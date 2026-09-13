# Research Proposal: Disentangling Task Structure from Architectural Bias in Representation Convergence through Controlled Synthetic Environments

## 1. Title

**Disentangling Task Structure from Architectural Bias in Representation Convergence: A Systematic Framework Using Parametrically Controlled Synthetic Environments**

## 2. Introduction

### Background

Recent advances in both neuroscience and artificial intelligence have revealed a striking phenomenon: different learning systems, whether biological or artificial, tend to converge toward similar internal representations when processing similar information. This convergence has been observed across diverse neural network architectures, from convolutional neural networks (CNNs) to transformers, and even between artificial networks and biological visual systems. This phenomenon has profound implications for model merging, transfer learning, multi-modal learning, and our understanding of the correspondence between artificial and biological intelligence.

However, a fundamental question remains largely unexplored: **what drives this representational convergence?** Current literature presents two competing (but not mutually exclusive) hypotheses. First, convergence may be driven by the inherent structure of the task itself—certain problems may necessitate specific representational structures regardless of the learning system. Second, convergence may arise from shared architectural biases—different architectures may impose similar constraints that guide learning toward particular solutions, even when alternative representations might be equally valid.

Distinguishing between these two sources of convergence is not merely an academic curiosity. Understanding this distinction is critical for several practical and theoretical reasons. For practitioners, this knowledge would enable prediction of when different models will naturally align, informing decisions about model merging, stitching, and reuse strategies. For architecture designers, it would reveal which inductive biases accelerate convergence toward optimal task-relevant representations versus which biases lead to suboptimal but architecturally convenient solutions. For neuroscientists, it would help distinguish truly universal computational principles from implementation-specific artifacts when comparing biological and artificial systems.

Despite the growing body of work on representational similarity analysis (RSA), including methods like Centered Kernel Alignment (CKA), Singular Vector Canonical Correlation Analysis (SVCCA), and more recent approaches like ContraSim, most studies have focused on measuring similarity rather than explaining its origins. The field lacks a systematic framework for causally attributing observed convergence to specific task properties versus architectural constraints.

### Research Objectives

This research proposes to address this gap through the following specific objectives:

1. **Develop a systematic framework** for creating parametrically controlled synthetic tasks where task complexity, symmetries, hierarchical structure, and statistical properties can be precisely manipulated independently.

2. **Conduct comprehensive experiments** training diverse neural architectures (CNNs, Transformers, MLPs, RNNs, and hybrid models) on these controlled tasks while systematically varying both task properties and architectural constraints.

3. **Quantify representational convergence** across conditions using multiple similarity measures (CKA, SVCCA, and novel pointwise methods) to create a multi-dimensional similarity landscape.

4. **Perform causal ablation studies** that isolate the contribution of specific task properties and architectural biases to observed representational structures.

5. **Develop predictive models** that can forecast representation similarity patterns given task specifications and architectural properties, enabling a priori predictions about model alignment.

6. **Create a comprehensive taxonomy** mapping task properties to representation convergence patterns, providing actionable insights for model design and integration.

### Significance

This research will make several significant contributions to the field:

**Theoretical Impact**: By causally disentangling task structure from architectural bias, this work will advance our fundamental understanding of representation learning, potentially revealing universal principles that govern how information should be structured for different computational problems.

**Methodological Impact**: The framework of parametrically controlled synthetic environments will provide the research community with a powerful tool for systematic investigation of representation learning, applicable beyond the specific questions addressed here.

**Practical Impact**: The resulting taxonomy and predictive models will enable practitioners to make informed decisions about architecture selection, model merging strategies, and transfer learning approaches, potentially reducing computational costs and improving model performance.

**Interdisciplinary Impact**: By clarifying the origins of representational convergence, this work will strengthen bridges between artificial intelligence and neuroscience, helping to identify which similarities between artificial and biological systems reflect fundamental computational constraints versus implementation details.

## 3. Methodology

### 3.1 Controlled Synthetic Task Generation

The foundation of this research is a parametric framework for generating synthetic tasks with precisely controlled properties. We will design task families across multiple dimensions:

#### Task Property Dimensions

**Compositional Structure**: Tasks will vary in their degree of compositional complexity, defined by the function $f: \mathcal{X} \rightarrow \mathcal{Y}$ where:

$$f(x) = g_n \circ g_{n-1} \circ \ldots \circ g_1(x)$$

with $n \in \{1, 2, 3, 5, 10\}$ representing compositional depth. Each $g_i$ represents a primitive operation (rotation, scaling, color transformation, pattern matching).

**Hierarchical Structure**: We define hierarchical complexity through multi-scale features where the target depends on information at different spatial/temporal scales. The hierarchy index $h$ ranges from 0 (flat) to 3 (deeply hierarchical):

$$y = \sum_{i=1}^{h} w_i \phi_i(x, s_i)$$

where $\phi_i$ operates at scale $s_i$ and $w_i$ are learned weights.

**Symmetry and Invariance Requirements**: Tasks will explicitly require different invariances:
- Translation invariance: $f(T_\delta x) = f(x)$ for translation operator $T_\delta$
- Rotation invariance: $f(R_\theta x) = f(x)$ for rotation operator $R_\theta$
- Scale invariance: $f(S_\alpha x) = f(x)$ for scaling operator $S_\alpha$
- Permutation invariance: $f(\pi(x)) = f(x)$ for permutation $\pi$

**Statistical Structure**: Control over data distribution properties:
- Signal-to-noise ratio: $\text{SNR} \in \{1, 5, 10, 20\}$
- Feature correlation structure parameterized by covariance matrix $\Sigma$
- Spurious correlation strength $\rho_{\text{spurious}} \in \{0, 0.3, 0.6, 0.9\}$

#### Specific Task Instantiations

1. **Synthetic Visual Tasks**: 2D image classification with controlled geometric properties
2. **Sequential Pattern Recognition**: Temporal sequences with varying memory requirements
3. **Graph Structure Tasks**: Node/graph classification with controllable graph properties
4. **Compositional Reasoning**: Symbolic tasks requiring chained logical operations

Each task will be implemented with a ground-truth generative process, allowing us to measure alignment with task-optimal representations.

### 3.2 Architecture Selection and Configuration

We will systematically evaluate diverse architectures representing different inductive biases:

**Convolutional Neural Networks (CNNs)**: 
- Architecture: ResNet-18 variants
- Bias: Translation equivariance, local connectivity, hierarchical processing
- Configuration variables: kernel size $k \in \{3, 5, 7\}$, depth, receptive field

**Transformers**:
- Architecture: Vision Transformer (ViT) variants
- Bias: Permutation equivariance (with position encoding), global receptive field
- Configuration variables: patch size, number of heads, positional encoding type

**Multi-Layer Perceptrons (MLPs)**:
- Architecture: Deep fully-connected networks
- Bias: Minimal architectural inductive bias
- Configuration variables: depth $\in \{3, 6, 12\}$, width $\in \{128, 256, 512\}$

**Recurrent Neural Networks (RNNs)**:
- Architecture: LSTM and GRU variants
- Bias: Temporal locality, sequential processing
- Configuration variables: hidden dimension, number of layers

**Hybrid Architectures**:
- CNN-Transformer hybrids
- Graph Neural Networks (for graph tasks)

### 3.3 Training Protocol

All models will be trained using a standardized protocol to ensure comparability:

**Optimization**: Adam optimizer with learning rate $\eta = 10^{-3}$, cosine annealing schedule:

$$\eta_t = \eta_{\min} + \frac{1}{2}(\eta_{\max} - \eta_{\min})\left(1 + \cos\left(\frac{t}{T}\pi\right)\right)$$

**Regularization**: L2 weight decay $\lambda = 10^{-4}$, dropout rate $p = 0.1$

**Training Duration**: Fixed computational budget of $10^6$ gradient steps or convergence (whichever comes first)

**Multiple Initializations**: 10 random seeds per configuration to account for initialization effects

**Checkpointing**: Save model checkpoints at initialization, 25%, 50%, 75%, and 100% of training to analyze representation dynamics

### 3.4 Representational Similarity Analysis

We will employ multiple complementary similarity measures to create a comprehensive picture of representational alignment:

#### Centered Kernel Alignment (CKA)

For representations $X \in \mathbb{R}^{n \times p_1}$ and $Y \in \mathbb{R}^{n \times p_2}$ from two models:

$$\text{CKA}(X, Y) = \frac{\text{HSIC}(K, L)}{\sqrt{\text{HSIC}(K, K) \cdot \text{HSIC}(L, L)}}$$

where $K = XX^T$ and $L = YY^T$ are Gram matrices, and HSIC is the Hilbert-Schmidt Independence Criterion:

$$\text{HSIC}(K, L) = \frac{1}{(n-1)^2}\text{tr}(KHLH)$$

with centering matrix $H = I - \frac{1}{n}\mathbf{1}\mathbf{1}^T$.

#### Singular Vector Canonical Correlation Analysis (SVCCA)

1. Apply SVD to obtain low-dimensional representations: $X = U_X \Sigma_X V_X^T$
2. Compute canonical correlation analysis between top singular vectors
3. Similarity score: mean of top $k$ canonical correlations

#### Pointwise Normalized Kernel Alignment (PNKA)

For individual samples $x_i$, compute local similarity:

$$\text{PNKA}(x_i) = \frac{\langle K_i, L_i \rangle_F}{\|K_i\|_F \|L_i\|_F}$$

where $K_i$ and $L_i$ are local Gram matrices computed over a neighborhood of $x_i$.

#### Procrustes Distance

Measure alignment after optimal linear transformation:

$$d_{\text{Procrustes}}(X, Y) = \min_{W} \|XW - Y\|_F$$

This quantifies whether representations differ only by a linear transformation.

### 3.5 Causal Ablation Framework

To causally attribute representational convergence to specific factors, we will employ a systematic ablation methodology:

#### Task Property Ablations

For each task property $p$ (e.g., translation invariance), create matched task pairs that differ only in $p$:
- $\mathcal{T}_p$: task requiring property $p$
- $\mathcal{T}_{\neg p}$: otherwise identical task not requiring $p$

Measure the change in cross-architecture similarity:

$$\Delta S_p = \text{Similarity}(\text{Arch}_1, \text{Arch}_2 | \mathcal{T}_p) - \text{Similarity}(\text{Arch}_1, \text{Arch}_2 | \mathcal{T}_{\neg p})$$

Positive $\Delta S_p$ indicates that task property $p$ drives convergence.

#### Architectural Bias Ablations

For each architectural bias $b$ (e.g., local connectivity in CNNs):
- Train architecture with bias intact
- Train modified architecture with bias removed/weakened
- Measure impact on within-architecture consistency and cross-architecture similarity

#### Interaction Analysis

Use a factorial design to test interactions between task properties and architectural biases:

$$S_{i,j,k} = \text{Similarity}(\text{Arch}_i, \text{Arch}_j | \text{Task}_k)$$

Apply multi-way ANOVA to decompose variance:

$$S_{i,j,k} = \mu + \alpha_i + \alpha_j + \beta_k + (\alpha\beta)_{ik} + (\alpha\beta)_{jk} + \epsilon_{ijk}$$

where $\alpha$ represents architecture effects, $\beta$ represents task effects, and $(\alpha\beta)$ represents interaction terms.

### 3.6 Predictive Model Development

Using the comprehensive dataset of similarity measurements, we will develop predictive models:

#### Feature Engineering

Extract features describing:
- **Task properties**: $\mathbf{t} = [t_1, t_2, \ldots, t_m]$ (compositional depth, hierarchy, required invariances, SNR, etc.)
- **Architecture properties**: $\mathbf{a}_i = [a_{i,1}, a_{i,2}, \ldots, a_{i,n}]$ (inductive biases, capacity, depth, etc.)

#### Regression Model

Train gradient boosted trees to predict similarity:

$$\hat{S}_{i,j}(\mathbf{t}) = f(\mathbf{t}, \mathbf{a}_i, \mathbf{a}_j, \mathbf{a}_i \odot \mathbf{a}_j)$$

where $\odot$ represents interaction features.

#### Validation Strategy

- Split tasks into training (70%), validation (15%), and test (15%) sets
- Use cross-validation to prevent overfitting
- Evaluate prediction accuracy using $R^2$, RMSE, and Spearman correlation
- Test generalization to novel architectures and task types

### 3.7 Experimental Design and Validation

**Phase 1: Pilot Study** (Months 1-3)
- Implement core synthetic task framework
- Train 4 architectures (CNN, Transformer, MLP, LSTM) on 3 task families
- Validate measurement pipeline and establish baseline similarity patterns

**Phase 2: Comprehensive Experiments** (Months 4-9)
- Full factorial design: 5 architectures × 8 task families × 5 property levels
- Total of ~1000 unique training runs with 10 random seeds each
- Compute all pairwise similarities across conditions

**Phase 3: Ablation Studies** (Months 10-15)
- Systematic ablations for 6 key task properties and 8 architectural biases
- Matched pair designs for causal inference
- Analyze representation dynamics throughout training

**Phase 4: Predictive Modeling** (Months 16-20)
- Feature engineering and model training
- Validation on held-out tasks and architectures
- Refinement based on prediction errors

**Phase 5: Taxonomy Development** (Months 21-24)
- Synthesize findings into coherent taxonomy
- Validate taxonomy predictions on real-world tasks
- Prepare comprehensive documentation and code release

### 3.8 Evaluation Metrics

**Primary Metrics**:
- **Cross-architecture similarity**: Mean CKA, SVCCA scores across architecture pairs
- **Task-driven convergence index**: Variance in similarity explained by task properties vs. architectural biases
- **Prediction accuracy**: $R^2$ and RMSE of predictive models on held-out data

**Secondary Metrics**:
- **Representation efficiency**: Mutual information between representations and task-relevant variables
- **Generalization performance**: Test accuracy on out-of-distribution samples
- **Training dynamics alignment**: Similarity of representation evolution trajectories

**Qualitative Analysis**:
- Visualization of representation spaces using UMAP/t-SNE
- Identification of emergent feature dimensions
- Case studies of maximally convergent vs. divergent conditions

## 4. Expected Outcomes & Impact

### Expected Outcomes

**Empirical Findings**: We expect to discover that representational convergence is driven by a complex interaction between task structure and architectural bias, with several anticipated patterns:

1. **Strong Task-Driven Convergence**: For tasks with well-defined mathematical structure (e.g., group-theoretic symmetries), we expect high convergence across diverse architectures, suggesting that task structure dominates.

2. **Architecture-Dependent Solutions**: For under-constrained tasks with multiple valid solutions, we expect divergence between architectures with different inductive biases, revealing architectural artifacts.

3. **Convergence Dynamics**: We anticipate that task-driven convergence emerges earlier in training, while architectural biases become more apparent in later stages or over-parameterized regimes.

4. **Hierarchical Organization**: Deeper layers should show more task-specific convergence, while early layers reflect architectural biases.

**Predictive Framework**: The resulting predictive models should achieve $R^2 > 0.75$ in forecasting representation similarity from task and architecture specifications, providing actionable guidance for practitioners.

**Comprehensive Taxonomy**: The taxonomy will map specific task properties (e.g., "requires translation invariance" + "hierarchical structure depth 3") to expected convergence patterns across architecture classes, with confidence intervals derived from our empirical studies.

**Open-Source Resources**: All synthetic task generators, trained models, analysis code, and comprehensive datasets will be released publicly, creating a valuable resource for the community.

### Scientific Impact

**Theoretical Advances**: This work will provide the first systematic, causal account of what drives representational convergence, resolving a fundamental question in representation learning. By distinguishing task-essential features from architectural artifacts, we will clarify the interpretation of model-brain alignment studies and inform debates about the universality of learned representations.

**Methodological Contributions**: The parametric synthetic task framework will establish a new paradigm for controlled experimentation in deep learning, enabling future researchers to isolate specific factors in representation learning with unprecedented precision.

**Architectural Insights**: Understanding which inductive biases accelerate convergence to task-optimal representations will guide architecture design, potentially leading to more efficient models that align with task structure from initialization.

### Practical Impact

**Model Merging and Stitching**: The taxonomy and predictive models will enable practitioners to predict, a priori, when different models will have compatible representations, drastically improving the success rate of model merging and stitching operations.

**Transfer Learning**: Understanding the origins of representational similarity will inform transfer learning strategies, helping practitioners select source models whose representations align with target task structure rather than merely achieving high source-task performance.

**Multi-Modal Learning**: For multi-modal systems, knowing which aspects of representations are task-driven versus architecture-specific will guide the design of fusion strategies and shared representation spaces.

**Computational Efficiency**: By identifying cases where diverse architectures naturally converge, we can avoid redundant exploration of architecture space, focusing design effort on genuinely distinct solutions.

### Broader Impact

**Neuroscience Applications**: By clarifying which similarities between artificial and biological neural systems reflect fundamental computational constraints versus implementation details, this work will strengthen neuroscience-AI collaboration and inform interpretation of brain imaging studies.

**Educational Value**: The clear categorization of task-driven versus architecture-driven representations will provide intuitive teaching examples for courses on deep learning and representation learning.

**Interdisciplinary Bridges**: This research will foster connections between machine learning, neuroscience, cognitive science, and applied mathematics (particularly group theory and symmetry analysis), potentially leading to novel interdisciplinary collaborations.

### Risk Mitigation

**Generalization to Real Tasks**: While synthetic tasks enable control, there is a risk that findings may not generalize to real-world problems. We mitigate this by: (1) designing synthetic tasks that capture key properties of real problems, (2) validating findings on a subset of real tasks, and (3) making task complexity progressively more realistic.

**Measurement Reliability**: Different similarity measures may provide conflicting results. We address this by employing multiple complementary measures and investigating cases of disagreement as potentially informative edge cases.

**Computational Resources**: The proposed experiments are computationally intensive. We will leverage cloud computing resources and optimize implementation, potentially using smaller-scale models for most experiments and validating key findings with larger models.

In conclusion, this research proposal outlines a comprehensive, systematic investigation into the fundamental question of what drives representational convergence in neural models. By disentangling task structure from architectural bias through controlled experimentation, we will advance both theoretical understanding and practical applications, ultimately contributing to the workshop's goal of unifying representations in neural models through principled, evidence-based approaches.