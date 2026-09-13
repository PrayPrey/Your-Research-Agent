# Research Proposal: Hierarchical Predictive Coding Networks with Bidirectional Error Minimization for Few-Shot Visual Learning

## 1. Introduction

### Background

The remarkable success of artificial neural networks (ANNs) in recent years has been fundamentally dependent on access to massive datasets and substantial computational resources. State-of-the-art vision models like those underlying DALL-E and Sora require billions of training examples and enormous GPU clusters. This stands in stark contrast to biological intelligence systems, where humans and other animals routinely learn to recognize new objects from just a handful of examples. A child can learn to identify a "giraffe" after seeing only one or two pictures, while current deep learning systems would require thousands of labeled examples to achieve comparable performance.

Predictive coding theory, originating from computational neuroscience, offers a compelling explanation for the brain's remarkable data efficiency. According to this framework, the brain continuously generates top-down predictions about incoming sensory data and propagates prediction errors in a bottom-up fashion. This bidirectional information flow enables hierarchical error minimization, where each cortical layer attempts to predict and explain away the activity of the layer below it. The residual prediction errors that propagate upward carry only the "surprising" information that cannot be explained by existing models, enabling efficient information processing and rapid learning.

Despite growing interest in implementing predictive coding principles in artificial systems, existing approaches have failed to fully capture the brain's few-shot learning capabilities. Recent work by Han et al. (2018) demonstrated bidirectional predictive coding networks for object recognition, but these systems still require substantial training data. Similarly, while hierarchical prototypical networks (Li et al., 2021) and contrastive pretraining methods (Mittal et al., 2023) have advanced few-shot learning, they lack the neurobiologically-grounded architecture that could provide both computational efficiency and interpretability.

### Research Objectives

This research aims to develop **Hierarchical Predictive Coding Networks (HPCNs)** that explicitly implement bidirectional prediction error propagation across multiple cortical-inspired layers for few-shot visual learning. Our specific objectives are:

1. To design a novel neural network architecture with reciprocal connections that generate top-down predictions and propagate bottom-up prediction errors, mimicking the computational principles of visual cortex.

2. To develop a hybrid learning mechanism that combines Hebbian-like local learning rules with global error signals, enabling rapid adaptation from limited examples through hierarchical prior knowledge.

3. To empirically validate the model's few-shot learning performance against state-of-the-art methods while simultaneously comparing learned representations with neural recordings from primate visual cortex.

4. To demonstrate that biologically-inspired architectures can achieve competitive performance with significantly reduced training data requirements.

### Significance

This research addresses the critical NeuroAI objective of developing computationally efficient AI systems that can learn in small-data regimes. By grounding our approach in predictive coding theory, we create a bridge between neuroscience and machine learning that advances understanding in both fields. The resulting systems will not only be more practical for real-world applications where labeled data is scarce but will also provide interpretable representations that align with our understanding of cortical processing, contributing to the field of explainable AI in neuroscience.

## 2. Methodology

### 2.1 Architecture Design

The Hierarchical Predictive Coding Network (HPCN) consists of $L$ hierarchical layers, each implementing reciprocal connections for bidirectional information flow. For layer $l \in \{1, 2, ..., L\}$, we define:

**State Representation**: Each layer maintains a representation state $\mathbf{r}^{(l)} \in \mathbb{R}^{d_l}$, where $d_l$ is the dimensionality at layer $l$.

**Top-Down Prediction**: Layer $l+1$ generates predictions of layer $l$'s activity through a generative pathway:

$$\hat{\mathbf{r}}^{(l)} = g^{(l)}(\mathbf{r}^{(l+1)}; \boldsymbol{\theta}_g^{(l)})$$

where $g^{(l)}$ is implemented as a transposed convolutional network with learnable parameters $\boldsymbol{\theta}_g^{(l)}$.

**Prediction Error Computation**: The prediction error at each layer quantifies the discrepancy between actual and predicted representations:

$$\mathbf{e}^{(l)} = \mathbf{r}^{(l)} - \hat{\mathbf{r}}^{(l)}$$

**Bottom-Up Error Propagation**: Prediction errors are transmitted upward through a feedforward pathway:

$$\boldsymbol{\epsilon}^{(l+1)} = f^{(l)}(\mathbf{e}^{(l)}; \boldsymbol{\theta}_f^{(l)})$$

where $f^{(l)}$ is implemented as a convolutional network with parameters $\boldsymbol{\theta}_f^{(l)}$.

**Precision Weighting**: Following the free energy principle, we introduce learnable precision parameters $\boldsymbol{\Pi}^{(l)}$ that weight prediction errors according to their estimated reliability:

$$\mathbf{e}_{\text{weighted}}^{(l)} = \boldsymbol{\Pi}^{(l)} \odot \mathbf{e}^{(l)}$$

### 2.2 Inference Dynamics

During inference, the network performs iterative settling to minimize prediction error across all layers. The state update at each layer follows:

$$\frac{d\mathbf{r}^{(l)}}{dt} = -\mathbf{e}_{\text{weighted}}^{(l)} + \boldsymbol{\epsilon}^{(l)} - \kappa \mathbf{r}^{(l)}$$

where $\kappa$ is a decay constant ensuring bounded activations. This dynamics is discretized using Euler integration:

$$\mathbf{r}^{(l)}_{t+1} = \mathbf{r}^{(l)}_t + \alpha \left(-\mathbf{e}_{\text{weighted}}^{(l)}_t + \boldsymbol{\epsilon}^{(l)}_t - \kappa \mathbf{r}^{(l)}_t\right)$$

where $\alpha$ is the integration step size. The network iterates for $T$ steps until convergence, defined as $\|\mathbf{r}^{(l)}_{t+1} - \mathbf{r}^{(l)}_t\|_2 < \delta$ for all layers.

### 2.3 Hybrid Learning Mechanism

Our key innovation is a hybrid learning rule that combines local Hebbian plasticity with global error guidance.

**Local Hebbian Update**: For generative weights, we apply a Hebbian-like rule that strengthens connections between co-active units:

$$\Delta \boldsymbol{\theta}_g^{(l)} = \eta_{\text{local}} \cdot \mathbf{e}^{(l)} \otimes \mathbf{r}^{(l+1)}$$

where $\eta_{\text{local}}$ is the local learning rate and $\otimes$ denotes the outer product.

**Global Error Modulation**: The local updates are modulated by a global error signal derived from the top-level representation:

$$\Delta \boldsymbol{\theta}_g^{(l)} \leftarrow \Delta \boldsymbol{\theta}_g^{(l)} \cdot \sigma\left(\mathcal{L}_{\text{global}}\right)$$

where $\mathcal{L}_{\text{global}}$ is the task-specific loss at the highest layer and $\sigma$ is a sigmoid gating function.

**Total Variational Free Energy**: The overall objective minimizes the variational free energy:

$$\mathcal{F} = \sum_{l=1}^{L} \frac{1}{2} \|\mathbf{e}_{\text{weighted}}^{(l)}\|_2^2 + \lambda_{\text{KL}} \sum_{l=1}^{L} D_{\text{KL}}(\mathbf{r}^{(l)} \| \mathbf{r}^{(l)}_{\text{prior}})$$

where the KL divergence term encourages representations to align with learned hierarchical priors.

### 2.4 Few-Shot Learning Protocol

**Meta-Training Phase**: The network is pre-trained on a large set of base classes $\mathcal{C}_{\text{base}}$ to learn hierarchical structural priors. During this phase, we employ episodic training where each episode samples a subset of classes and constructs support/query sets.

**Few-Shot Adaptation**: Given a novel class with $K$ support examples $\{(\mathbf{x}_k, y)\}_{k=1}^{K}$, the network adapts through:

1. **Prior Activation**: Feed each support example through the network, performing $T$ inference iterations.
2. **Prototype Computation**: Compute a class prototype at the highest layer:
   $$\mathbf{p}_y = \frac{1}{K} \sum_{k=1}^{K} \mathbf{r}^{(L)}_k$$
3. **Rapid Weight Adaptation**: Apply few-shot Hebbian updates:
   $$\boldsymbol{\theta}_g^{(l)} \leftarrow \boldsymbol{\theta}_g^{(l)} + \eta_{\text{fast}} \sum_{k=1}^{K} \Delta \boldsymbol{\theta}_g^{(l)}(\mathbf{x}_k)$$

**Classification**: For a query image $\mathbf{x}_q$, classification is performed using cosine similarity between the query representation and class prototypes:

$$\hat{y} = \arg\max_{y} \frac{\mathbf{r}^{(L)}_q \cdot \mathbf{p}_y}{\|\mathbf{r}^{(L)}_q\| \|\mathbf{p}_y\|}$$

### 2.5 Data Collection and Experimental Design

**Datasets**:
- **Omniglot**: 1,623 handwritten characters from 50 alphabets (20 examples each), split into 964/659 training/testing classes.
- **mini-ImageNet**: 100 classes with 600 images each, split into 64/16/20 for training/validation/testing.
- **tiered-ImageNet**: 608 classes from 34 high-level categories for more challenging evaluation.

**Neural Data Comparison**:
We will utilize publicly available neural recordings from the IT cortex of macaque monkeys performing object recognition tasks (DiCarlo Lab dataset) to compare learned representations.

**Baselines**:
- Prototypical Networks
- MAML (Model-Agnostic Meta-Learning)
- Deep Predictive Coding Networks (Han et al., 2018)
- CLIP zero-shot transfer (Radford et al., 2021)
- LatHAdapter (Zhao et al., 2025)

**Evaluation Metrics**:
1. **Classification Accuracy**: 5-way 1-shot and 5-way 5-shot accuracy with 95% confidence intervals over 10,000 episodes.
2. **Data Efficiency**: Learning curves comparing accuracy vs. number of training examples.
3. **Representational Similarity Analysis (RSA)**: Correlation between HPCN layer-wise representational dissimilarity matrices (RDMs) and neural RDMs from IT cortex.
4. **Centered Kernel Alignment (CKA)**: Quantitative comparison of hierarchical representations with neural data.
5. **Computational Efficiency**: FLOPs, inference time, and memory usage.

**Implementation Details**:
- 5 hierarchical layers with dimensions [64, 128, 256, 512, 512]
- $T = 10$ inference iterations
- $\eta_{\text{local}} = 0.01$, $\eta_{\text{fast}} = 0.1$
- Training for 60,000 episodes with Adam optimizer (lr = $10^{-4}$)

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Performance**: We anticipate HPCNs will achieve competitive few-shot classification accuracy (within 2% of state-of-the-art) while requiring approximately 10x less pre-training data. On 5-way 5-shot mini-ImageNet, we expect accuracies of 75-80%, comparable to leading meta-learning methods.

**Data Efficiency**: The hierarchical prior learning mechanism should demonstrate superior sample efficiency, with HPCNs reaching 70% of peak performance using only 10% of standard training data.

**Neural Alignment**: We predict RSA correlations of $r > 0.5$ between HPCN intermediate representations and IT cortex recordings, significantly higher than standard CNNs ($r \approx 0.3$), validating the biological plausibility of our architecture.

**Interpretability**: The explicit prediction error representations at each layer will provide interpretable visualizations of what information the network considers "surprising" versus "expected," enabling human-understandable explanations of model decisions.

### Impact

**Scientific Impact**: This work will provide empirical validation of predictive coding theory as a computational principle capable of explaining both biological and artificial visual learning. The neural alignment analysis will contribute to computational neuroscience by demonstrating that normatively-derived architectures naturally develop brain-like representations.

**Practical Impact**: The demonstrated data efficiency has immediate applications in medical imaging, robotics, and other domains where labeled data is scarce or expensive to obtain. The reduced computational requirements align with sustainability goals in AI development.

**Broader NeuroAI Impact**: By demonstrating that biologically-inspired principles yield practical advantages, this research strengthens the case for continued cross-fertilization between neuroscience and AI. The open-source release of our code and trained models will provide the community with tools for further investigation of predictive coding in artificial systems.

In conclusion, this research will advance the NeuroAI agenda by developing systems that not only perform efficiently but do so through mechanisms grounded in our best understanding of biological intelligence, opening new avenues for both scientific discovery and practical applications.