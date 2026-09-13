# Adaptive Margin Regularization for Mitigating Spurious Correlations Through Loss Landscape Engineering

## 1. Introduction

### Background

Deep neural networks (DNNs) have achieved remarkable success across diverse domains, yet their vulnerability to spurious correlations remains a fundamental challenge that threatens their deployment in safety-critical applications. Spurious correlations arise when models exploit statistical associations between features and labels that hold in training data but fail to generalize to deployment scenarios. For instance, medical diagnosis models may rely on hospital-specific imaging artifacts rather than disease symptoms, or image classifiers may associate "cow" with "grass" backgrounds instead of learning bovine anatomical features.

The root cause of this phenomenon lies in the statistical nature of gradient-based optimization and the inductive biases inherent to deep learning. Recent theoretical investigations have revealed that DNNs exhibit a tendency to maximize margins during training, which paradoxically contributes to spurious correlation reliance. Spurious features—being simpler, more prevalent, or more easily separable—often enable faster margin maximization than core features, leading optimizers to preferentially exploit these shortcuts. This simplicity bias manifests across architectures and training paradigms, making it a foundational issue requiring principled solutions.

Existing approaches to mitigating spurious correlations largely fall into three categories: (1) methods requiring explicit group annotations indicating spurious attributes (e.g., group distributionally robust optimization), (2) data manipulation techniques that prune or reweight samples, and (3) representation learning methods that enforce specific structural properties. However, these approaches suffer from critical limitations. Group annotation is labor-intensive, non-scalable, and presupposes knowledge of which correlations are spurious—a requirement often violated in practice. Data manipulation methods may inadvertently remove informative samples or fail when spurious correlations are pervasive. Meanwhile, current representation learning approaches lack direct mechanisms to intervene in the optimization dynamics that cause spurious correlation reliance.

### Research Objectives

This research proposes **Adaptive Margin Regularization (AMR)**, a novel framework that directly addresses the optimization mechanisms underlying shortcut learning by engineering the loss landscape. Our approach is grounded in three key insights: (1) spurious features exhibit systematically different learning dynamics than core features, particularly in terms of convergence speed and margin evolution, (2) the loss landscape geometry encodes information about feature reliability that can be exploited during training, and (3) adaptive regularization based on temporal learning patterns can discourage spurious solutions without requiring external annotations.

The primary objectives of this research are:

1. **Develop a training algorithm** that identifies and penalizes rapid margin maximization on potentially spurious features through temporal gradient analysis
2. **Establish theoretical foundations** connecting loss landscape geometry, margin dynamics, and worst-group generalization guarantees
3. **Create evaluation protocols** for assessing robustness improvements without access to group labels during training
4. **Validate empirically** across vision and language benchmarks exhibiting known spurious correlations
5. **Provide mechanistic insights** into how optimization dynamics can be steered toward robust solutions through landscape engineering

### Significance

This research makes several significant contributions to the foundations and solutions for spurious correlation challenges:

**Theoretical Contributions**: We provide a mathematical framework characterizing how margin dynamics on different feature types influence loss landscape geometry, establishing formal connections between optimization trajectories and worst-group performance. This advances foundational understanding of why DNNs learn spurious correlations.

**Methodological Contributions**: AMR introduces a principled, annotation-free approach to robustification that operates at the optimization level, making it applicable across architectures, modalities, and learning paradigms. Unlike post-hoc correction methods, our approach intervenes during the learning process itself.

**Practical Impact**: By eliminating the need for group labels or prior knowledge of spurious features, AMR enables robustification in realistic scenarios where such information is unavailable. This has immediate implications for deploying robust models in domains like healthcare, autonomous systems, and fairness-critical applications.

**Bridging Research Directions**: This work connects multiple workshop topics including foundational understanding of spurious correlation origins, novel robustification methods, and loss landscape analysis, demonstrating how theoretical insights can inform practical solutions.

## 2. Methodology

### Overview

Our methodology consists of four integrated components: (1) temporal feature learning dynamics analysis, (2) adaptive margin-aware regularization, (3) theoretical characterization of loss landscape properties, and (4) comprehensive empirical validation. We detail each component below.

### 2.1 Temporal Feature Learning Dynamics Analysis

**Motivation**: Spurious features typically enable faster loss reduction and margin increases during early training compared to core features. We formalize this observation to create detection mechanisms.

**Formalization**: Consider a classification task with input space $\mathcal{X}$, label space $\mathcal{Y}$, and a neural network $f_\theta: \mathcal{X} \to \mathbb{R}^{|\mathcal{Y}|}$ parameterized by $\theta$. Each input $x$ can be decomposed into core features $x_c$ and spurious features $x_s$. Let $\ell(\theta; x, y)$ denote the loss for sample $(x, y)$.

We define the **feature gradient magnitude** at training step $t$ as:
$$g_i^{(t)} = \|\nabla_{\theta_i} \mathcal{L}^{(t)}\|_2$$
where $\theta_i$ represents parameters in layer $i$ and $\mathcal{L}^{(t)}$ is the batch loss at step $t$.

The **temporal gradient acceleration** captures how quickly gradients decay:
$$a_i^{(t)} = \frac{g_i^{(t-\tau)} - g_i^{(t)}}{g_i^{(0)}}$$
where $\tau$ is a lookback window. Features learned rapidly exhibit high acceleration early in training.

We also track **prediction confidence evolution**:
$$c^{(t)}(x) = \max_{y'} \sigma(f_{\theta^{(t)}}(x))_{y'}$$
where $\sigma$ is the softmax function. Samples with rapidly increasing confidence may indicate reliance on spurious patterns.

**Spurious Feature Score**: We aggregate these signals into a per-sample spurious feature score:
$$s^{(t)}(x) = \alpha \cdot \mathbb{I}[c^{(t)}(x) > \gamma_c] \cdot \mathbb{I}[a^{(t)} > \gamma_a] + \beta \cdot m^{(t)}(x)$$

where $m^{(t)}(x)$ is the margin $f_{\theta^{(t)}}(x)_y - \max_{y'\neq y}f_{\theta^{(t)}}(x)_{y'}$, and $\alpha, \beta, \gamma_c, \gamma_a$ are hyperparameters. This score is high for samples where the model achieves high confidence and large margins rapidly.

### 2.2 Adaptive Margin Regularization

**Core Regularization Term**: We introduce a penalty that discourages excessive margins on potentially spurious features while encouraging continued learning on uncertain samples:

$$\mathcal{R}_{\text{AMR}}^{(t)} = \frac{1}{|\mathcal{B}|}\sum_{(x,y)\in\mathcal{B}} w^{(t)}(x) \cdot h(m^{(t)}(x))$$

where $\mathcal{B}$ is a training batch, and the sample weight is:
$$w^{(t)}(x) = \text{sigmoid}\left(\eta \cdot (s^{(t)}(x) - \delta)\right)$$

This weight assigns higher penalties to samples with high spurious feature scores. The margin penalty function is:
$$h(m) = \begin{cases} 
(m - m_{\text{target}})^2 & \text{if } m > m_{\text{target}} \\
-\lambda \log(m + \epsilon) & \text{if } m \leq m_{\text{target}}
\end{cases}$$

This bimodal penalty discourages margins exceeding a target $m_{\text{target}}$ (applied to likely spurious samples) while preventing margin collapse on other samples through the logarithmic term.

**Complete Training Objective**: The full objective combines standard cross-entropy loss with AMR:
$$\mathcal{L}_{\text{total}}^{(t)} = \mathcal{L}_{\text{CE}}^{(t)} + \mu^{(t)} \cdot \mathcal{R}_{\text{AMR}}^{(t)}$$

where the regularization strength $\mu^{(t)}$ adapts over training:
$$\mu^{(t)} = \mu_0 \cdot \left(1 + \cos\left(\frac{\pi t}{T}\right)\right)$$

This cosine schedule applies stronger regularization early (when spurious learning is most rapid) and gradually reduces it, allowing refinement of learned features.

**Gradient Dynamics Intervention**: To further stabilize training, we apply selective gradient clipping:
$$\nabla_\theta \mathcal{L}_{\text{total}} \leftarrow \begin{cases}
\text{clip}(\nabla_\theta \mathcal{L}_{\text{total}}, C_{\text{spurious}}) & \text{if } \bar{s}^{(t)} > \tau_s \\
\nabla_\theta \mathcal{L}_{\text{total}} & \text{otherwise}
\end{cases}$$

where $\bar{s}^{(t)}$ is the batch-averaged spurious score and $C_{\text{spurious}} < C_{\text{default}}$ is a tighter clipping threshold. This prevents rapid optimization toward spurious solutions.

### 2.3 Theoretical Analysis

**Loss Landscape Geometry**: We characterize how AMR reshapes the loss landscape using Hessian analysis. Let $\mathcal{L}_{\text{std}}(\theta)$ denote the standard training loss and $\mathcal{L}_{\text{AMR}}(\theta) = \mathcal{L}_{\text{std}}(\theta) + \mu \mathcal{R}_{\text{AMR}}(\theta)$ our regularized objective.

**Proposition 1** (Margin-based Landscape Flattening): For parameters $\theta^*$ achieving large margins $m(x) \gg m_{\text{target}}$ on samples with high spurious scores $s(x) > \delta$, the Hessian eigenvalues of $\mathcal{L}_{\text{AMR}}$ in directions corresponding to these samples are bounded:
$$\lambda_{\max}(H_{\mathcal{L}_{\text{AMR}}}(\theta^*)) \geq \lambda_{\max}(H_{\mathcal{L}_{\text{std}}}(\theta^*)) + \mu \cdot \mathbb{E}_{x: s(x)>\delta}[\nabla^2 h(m(x))]$$

This indicates that spurious minima (characterized by large margins on spuriously-correlated samples) become sharper under AMR, making them less attractive to SGD.

**Proposition 2** (Worst-Group Margin Lower Bound): Under mild assumptions on feature separability, AMR provides a lower bound on worst-group margins. Let $\mathcal{G}$ denote data groups. Then with probability $1-\delta$:
$$\min_{g\in\mathcal{G}} \mathbb{E}_{(x,y)\sim\mathcal{D}_g}[m(x)] \geq m_{\text{target}} - O\left(\sqrt{\frac{\log(|\mathcal{G}|/\delta)}{n_{\min}}}\right)$$

where $n_{\min}$ is the smallest group size. This guarantee holds without explicit group supervision.

**Proof Sketch**: The regularization term penalizes deviations from $m_{\text{target}}$ on samples identified as potentially spurious. Since minority groups are more likely to lack spurious features present in majority groups, they receive lower spurious scores and thus lower penalty weights. This effectively implements an implicit reweighting favoring robust learning.

### 2.4 Data Collection and Experimental Design

**Datasets**: We evaluate AMR on established benchmarks across vision and language:

*Vision*:
- **Waterbirds**: 4,795 training and 5,794 test images with spurious background correlations
- **CelebA**: Face attribute classification with 162,770 training images and spurious attribute correlations
- **ImageNet-9L**: Large-scale dataset with 318,000 images exhibiting realistic spurious correlations
- **CIFAR-10-C**: 50,000 training images; test robustness to synthetic corruptions

*Language*:
- **CivilComments**: Toxicity classification with 269,038 training comments and spurious identity term correlations
- **MultiNLI**: Natural language inference with 392,702 premise-hypothesis pairs exhibiting lexical overlap shortcuts
- **HANS**: Evaluation set of 30,000 examples testing heuristic-based spurious patterns

**Baseline Comparisons**: We compare against:
1. **ERM**: Standard empirical risk minimization
2. **Group DRO**: Requires group labels, represents upper bound
3. **JTT**: Just Train Twice, identifies hard samples
4. **CNC**: Correct-N-Contrast contrastive learning
5. **LC**: Logit Correction loss
6. **ElRep**: Elastic Representation with norm penalties
7. **Data Pruning**: Recent spurious sample removal approach

**Evaluation Metrics**:
- **Worst-Group Accuracy**: $\min_{g\in\mathcal{G}} \text{Acc}_g$, primary metric
- **Average Accuracy**: Overall performance across all groups
- **Effective Robustness**: $\text{Worst-Acc} - (\text{Avg-Acc} - \text{Random-Baseline})$
- **Margin Statistics**: Mean and minimum margins across groups
- **Feature Attribution Alignment**: Gradient-based attribution correlation with core vs. spurious features

**Implementation Details**:
- Architectures: ResNet-50 for vision, BERT-base for language
- Optimization: SGD with momentum 0.9 for vision, AdamW for language
- Hyperparameters: $m_{\text{target}}=1.0$, $\mu_0 \in \{0.1, 0.5, 1.0\}$ (tuned via validation), $\tau=10$ epochs, $\eta=5.0$, $\delta=0.5$
- Training: 3 random seeds, standard data augmentation, learning rate schedules following dataset conventions

**Ablation Studies**:
1. Effect of each component: temporal tracking, margin penalty, adaptive weighting
2. Sensitivity to hyperparameters: $m_{\text{target}}$, $\mu_0$, $\tau$
3. Temporal analysis: tracking spurious scores and margins throughout training
4. Loss landscape visualization: comparing Hessian spectra and gradient flow between AMR and baselines
5. Transferability: pre-training with AMR then fine-tuning on downstream tasks

**Computational Resources**: Experiments conducted on NVIDIA A100 GPUs, estimated 500 GPU-hours total across all experiments.

### 2.5 Analysis Methodology

**Loss Landscape Visualization**: We employ two complementary techniques:

1. **Linear Interpolation Analysis**: For two trained models $\theta_{\text{AMR}}$ and $\theta_{\text{ERM}}$, we compute:
$$\mathcal{L}(\alpha) = \mathcal{L}((1-\alpha)\theta_{\text{ERM}} + \alpha\theta_{\text{AMR}})$$
for $\alpha \in [0,1]$ and visualize barrier heights and sharpness differences.

2. **Hessian Spectral Analysis**: At convergence, we compute leading eigenvalues of $H_{\mathcal{L}}(\theta)$ and their corresponding eigenvectors, examining whether spurious vs. core feature directions exhibit different curvature properties.

**Feature Learning Dynamics**: We track the evolution of:
- Layer-wise gradient norms for different sample groups
- Prediction confidence trajectories separated by group membership
- Spurious feature scores over time to validate detection accuracy

**Statistical Significance Testing**: We employ bootstrap confidence intervals (10,000 samples) for worst-group accuracy and perform paired t-tests across random seeds to assess significance of improvements.

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Empirical Performance**: We anticipate AMR will achieve:
- **5-15% improvement** in worst-group accuracy over ERM across benchmarks
- Performance **within 2-3%** of Group DRO despite not using group labels
- **Superior robustness-accuracy tradeoff** compared to annotation-free baselines (JTT, CNC, LC)
- **Consistent improvements** across both vision and language domains, demonstrating generality

**Theoretical Insights**: We expect to establish:
- Formal characterization of loss landscape differences between spurious and robust minima
- Convergence guarantees for AMR showing it steers optimization toward flatter, more robust regions
- Connections between margin dynamics, learning speed, and feature reliability
- Lower bounds on worst-group performance as a function of regularization strength

**Mechanistic Understanding**: Analysis will reveal:
- Temporal patterns distinguishing spurious from core feature learning
- How adaptive regularization modifies gradient flow to prevent premature convergence
- The relationship between sample-level spurious scores and true group membership
- Architectural differences in susceptibility to spurious correlations

### Impact on the Field

**Advancing Foundational Understanding**: This research directly addresses the workshop's goal of elucidating the foundations of spurious correlation reliance by:
- Providing quantitative characterization of optimization dynamics leading to shortcut learning
- Connecting high-level phenomena (spurious correlations) to low-level mechanisms (loss landscape geometry, margin maximization)
- Offering a unifying framework applicable across architectures and modalities

**Practical Robustification Solutions**: AMR addresses critical gaps in existing methods:
- **Annotation-Free Operation**: Eliminates the impractical requirement for group labels, enabling deployment where spurious correlations are unknown
- **Training-Time Intervention**: Unlike post-hoc corrections, operates during learning to prevent spurious reliance from forming
- **Generality**: Applicable across supervised learning tasks without domain-specific modifications
- **Scalability**: Computational overhead minimal (~10-15% increase) compared to standard training

**Enabling New Research Directions**:
- **Automated Spurious Correlation Detection**: The temporal feature analysis component could be extended to diagnostic tools identifying unknown spurious patterns
- **Meta-Learning Applications**: AMR's adaptive regularization could inform meta-learning algorithms that automatically adjust to distribution shifts
- **Foundation Model Robustification**: Principles could be adapted to self-supervised and contrastive learning paradigms used in training large-scale models
- **Benchmark Development**: Spurious feature scoring methodology could inform construction of evaluation benchmarks without requiring human annotation

**Broader Impacts**:
- **Fairness and Ethics**: Reducing spurious correlations often aligned with protected attributes (race, gender) has direct fairness implications
- **Safety-Critical Deployment**: Enabling robust models without extensive annotation reduces barriers to deploying AI in healthcare, autonomous vehicles, etc.
- **Democratizing Robustness**: Annotation-free methods make robustness accessible to practitioners without specialized domain knowledge

### Limitations and Future Work

**Acknowledged Limitations**:
- Detection accuracy for spurious features may vary with dataset characteristics
- Hyperparameter sensitivity requires validation-based tuning (though less intensive than group annotation)
- Theoretical guarantees rely on assumptions about feature separability that may not hold universally

**Future Research Directions**:
1. **Extension to Other Paradigms**: Adapting AMR to reinforcement learning, few-shot learning, and continual learning settings
2. **Foundation Model Integration**: Incorporating margin regularization into pre-training of large language and vision models
3. **Multi-Modal Spurious Correlations**: Addressing spurious associations across modalities in vision-language models
4. **Theoretical Refinement**: Tightening bounds and relaxing assumptions in convergence analysis
5. **Automated Hyperparameter Tuning**: Developing meta-learned or adaptive schemes for setting $m_{\text{target}}$, $\mu_0$, etc.

### Conclusion

This research proposes Adaptive Margin Regularization, a principled framework addressing spurious correlations through loss landscape engineering. By directly targeting the optimization mechanisms underlying shortcut learning—specifically, the tendency toward rapid margin maximization on spurious features—AMR provides both theoretical insights and practical solutions aligned with the workshop's objectives. The annotation-free nature and generality across domains make this approach particularly valuable for real-world deployment, while the theoretical characterization advances foundational understanding of how deep networks learn and fail to generalize. Through comprehensive empirical validation and rigorous analysis, we expect this work to meaningfully contribute to both the foundations and solutions for spurious correlation challenges in modern AI systems.