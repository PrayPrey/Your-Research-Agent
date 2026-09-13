# Research Proposal: Understanding and Mitigating Shortcut Learning Dynamics in Self-Supervised Contrastive Learning through Loss Landscape Analysis

## 1. Introduction

### Background

Self-supervised contrastive learning (SSCL) has emerged as a cornerstone methodology for pre-training large-scale foundation models, achieving remarkable success across computer vision, natural language processing, and multimodal applications. Methods such as SimCLR, MoCo, and CLIP have demonstrated that learning representations without explicit labels can yield features that transfer effectively to diverse downstream tasks. However, a critical yet underexplored vulnerability threatens the reliability of these representations: the tendency to encode spurious correlations—statistical patterns that are predictive in training data but fail to generalize under distribution shift.

In supervised learning, the phenomenon of shortcut learning is well-documented: models exploit superficial correlations (e.g., background textures, watermarks, or dataset-specific artifacts) rather than learning causal features. Recent theoretical work has connected this behavior to the geometry of the loss landscape, showing that spurious features often correspond to sharper, more accessible minima that gradient-based optimizers preferentially discover. However, the dynamics of shortcut learning in self-supervised settings remain fundamentally unclear. Without explicit labels, SSCL relies on augmentation-based views to define positive pairs, creating a distinct learning objective where the emergence and persistence of spurious correlations may follow different patterns.

Understanding these dynamics is increasingly urgent as foundation models trained with contrastive objectives are deployed across high-stakes domains including medical imaging, autonomous systems, and content moderation. When these models encode spurious correlations during pre-training, the resulting biases propagate to all downstream applications, potentially causing systematic failures for underrepresented groups or novel deployment contexts.

### Research Objectives

This research aims to provide the first comprehensive analysis of how spurious correlations influence the loss landscape geometry in self-supervised contrastive learning and how these geometric properties govern the temporal dynamics of feature encoding. Our specific objectives are:

1. **Characterize the loss landscape geometry** associated with spurious versus core (semantic) features in contrastive learning, quantifying differences in curvature, basin width, and accessibility during optimization.

2. **Map the temporal dynamics** of spurious feature encoding, determining when and how quickly shortcuts are learned relative to semantic content, and how these dynamics differ from supervised learning.

3. **Develop a curvature-aware contrastive loss** that leverages our geometric insights to penalize optimization trajectories toward spurious feature-aligned directions, enabling more robust representation learning.

4. **Validate our theoretical findings and proposed method** through comprehensive experiments on controlled synthetic datasets and realistic benchmarks with known spurious correlations.

### Significance

This research addresses fundamental questions at the intersection of optimization theory, representation learning, and robustness—all central themes of the workshop on spurious correlations and shortcut learning. By illuminating the geometric origins of shortcuts in SSCL, we provide both theoretical foundations for understanding this phenomenon and practical tools for mitigating it. Our work directly contributes to the workshop's goals of exploring the foundations of spurious correlations, studying optimization's role in shortcut reliance, and proposing robustification methods for paradigms beyond supervised learning.

## 2. Methodology

### 2.1 Controlled Dataset Construction

To isolate and study spurious correlations in contrastive learning, we will construct synthetic datasets with precisely controlled spurious features at varying correlation strengths.

**Synthetic Contrastive Dataset (SCD):** We build upon standard image datasets (CIFAR-10, ImageNet-100) by introducing synthetic spurious features with known properties:

- **Color-based spurious features:** Each semantic class is associated with a background color with probability $p_s \in \{0.7, 0.8, 0.9, 0.95\}$, creating controlled spurious correlations.
- **Texture-based spurious features:** Overlay textures (stripes, dots, gradients) correlated with semantic content.
- **Positional spurious features:** Object locations systematically vary with class identity.

For each image $x$ with semantic label $y$, we generate spurious attribute $s$ according to:
$$P(s = y) = p_s, \quad P(s \neq y) = \frac{1-p_s}{K-1}$$
where $K$ is the number of classes.

**Augmentation-Induced Spurious Correlations:** We design augmentation pipelines that inadvertently preserve spurious features more than semantic features, mimicking real-world scenarios where standard augmentations fail to break spurious associations.

### 2.2 Loss Landscape Analysis Framework

We develop a comprehensive framework for analyzing how spurious features shape the contrastive loss landscape.

**Hessian Eigenspectrum Analysis:** For a contrastive encoder $f_\theta$, we compute the Hessian of the InfoNCE loss:
$$H = \nabla^2_\theta \mathcal{L}_{NCE}(\theta) = \nabla^2_\theta \left[ -\log \frac{\exp(z_i \cdot z_j / \tau)}{\sum_{k=1}^{2N} \mathbb{1}_{k \neq i} \exp(z_i \cdot z_k / \tau)} \right]$$

Due to computational constraints, we employ stochastic Hessian estimation using the Lanczos algorithm to approximate the top-$k$ eigenvalues $\{\lambda_1, \lambda_2, ..., \lambda_k\}$ and corresponding eigenvectors.

**Feature-Specific Curvature Decomposition:** To disentangle curvature contributions from spurious versus core features, we introduce probing-based projections. Let $P_s$ and $P_c$ be linear probes trained to predict spurious and core features from intermediate representations. We define:

$$\kappa_s = \mathbb{E}_{x}\left[\|P_s^\top H P_s\|_F\right], \quad \kappa_c = \mathbb{E}_{x}\left[\|P_c^\top H P_c\|_F\right]$$

These metrics quantify the sharpness of the loss landscape along directions encoding spurious versus core information.

**Basin Width Estimation:** We measure the width of local minima using random direction perturbations:
$$w(\theta) = \mathbb{E}_{\delta \sim \mathcal{N}(0, I)}\left[\min\{\alpha : \mathcal{L}(\theta + \alpha\delta) - \mathcal{L}(\theta) > \epsilon\}\right]$$

### 2.3 Temporal Dynamics Measurement

**Probing Classifier Protocol:** At regular training intervals $t \in \{t_1, t_2, ..., t_T\}$, we freeze the encoder and train linear probes to predict:
- Spurious attributes: $\hat{s} = W_s^\top f_\theta(x) + b_s$
- Semantic labels: $\hat{y} = W_c^\top f_\theta(x) + b_c$

We define the **Spurious Encoding Rate (SER)** and **Core Encoding Rate (CER)** as:
$$SER(t) = \text{Accuracy}(\hat{s}, s), \quad CER(t) = \text{Accuracy}(\hat{y}, y)$$

**Relative Learning Speed:** We measure when each feature type achieves $\alpha\%$ of its maximum probing accuracy:
$$t_s^\alpha = \min\{t : SER(t) \geq \alpha \cdot \max_\tau SER(\tau)\}$$
$$t_c^\alpha = \min\{t : CER(t) \geq \alpha \cdot \max_\tau CER(\tau)\}$$

The ratio $\rho^\alpha = t_c^\alpha / t_s^\alpha$ quantifies the relative speed of spurious versus core feature learning.

### 2.4 Curvature-Aware Contrastive Loss

Based on our hypothesis that spurious features correspond to sharper minima, we propose a **Curvature-Regularized InfoNCE (CR-InfoNCE)** loss:

$$\mathcal{L}_{CR}(\theta) = \mathcal{L}_{NCE}(\theta) + \lambda \cdot R_{curv}(\theta)$$

where the curvature regularizer is defined as:

$$R_{curv}(\theta) = \sum_{i=1}^{k} \max(0, \lambda_i - \gamma)$$

Here, $\lambda_i$ are the top-$k$ eigenvalues of the Hessian, and $\gamma$ is a threshold discouraging excessively sharp curvature.

**Efficient Implementation:** Computing the full Hessian is prohibitive. We use the following approximations:
1. **Hutchinson's trace estimator** for efficient Hessian-vector products
2. **Power iteration** to approximate the top eigenvalue
3. **Gradient penalty proxy:** As an efficient alternative, we regularize gradient norms:
$$R_{grad}(\theta) = \mathbb{E}_{x,x'}\left[\|\nabla_\theta \ell(x, x')\|_2^2\right]$$

**Adaptive Regularization Schedule:** We hypothesize that early training is most critical for shortcut formation. We implement:
$$\lambda(t) = \lambda_0 \cdot \exp(-t / \tau_{decay})$$

### 2.5 Experimental Design

**Baselines:** We compare against:
1. Standard InfoNCE (SimCLR, MoCo v3)
2. Learning-speed aware sampling (Zhu et al., 2023)
3. LateTVG (Hamidieh et al., 2024)
4. Standard regularization techniques (weight decay, spectral normalization)

**Datasets:**
- *Synthetic:* Our constructed SCD datasets with controlled spurious correlations
- *Semi-synthetic:* Waterbirds (background spurious), CelebA (gender-attribute correlations)
- *Real-world:* ImageNet with natural spurious correlations identified via saliency analysis

**Evaluation Metrics:**
1. **Worst-group accuracy** on downstream classification tasks
2. **Spurious feature reliance score:** Accuracy drop when spurious features are randomized at test time
3. **Effective robustness:** Performance on out-of-distribution test sets where spurious correlations are broken
4. **Representation quality:** Linear probe accuracy, k-NN accuracy, transfer learning performance

**Architecture and Training:**
- ResNet-50 and Vision Transformer (ViT-B/16) encoders
- Training: 200 epochs on CIFAR-scale, 100 epochs on ImageNet-scale
- Optimizer: LARS with cosine learning rate schedule
- Batch sizes: 256-4096 depending on computational resources

**Statistical Rigor:** All experiments are repeated with 5 random seeds, reporting mean ± standard deviation. We use paired t-tests for significance testing with Bonferroni correction for multiple comparisons.

## 3. Expected Outcomes & Impact

### Theoretical Contributions

1. **Geometric Characterization of Shortcuts in SSCL:** We expect to demonstrate that spurious features in contrastive learning correspond to regions of higher curvature (sharper minima) in the loss landscape compared to semantic features. We hypothesize the curvature ratio satisfies:
$$\frac{\kappa_s}{\kappa_c} > 1 + \delta$$
for some significant $\delta > 0$, explaining the optimization bias toward spurious features.

2. **Temporal Dynamics Model:** We anticipate finding that $\rho^\alpha < 1$ across varying spurious correlation strengths, confirming that shortcuts are learned before core features in SSCL. We will develop a theoretical model relating the learning speed ratio to the curvature ratio and spurious correlation strength $p_s$.

3. **Generalization Bounds:** Building on our geometric analysis, we aim to derive generalization bounds for contrastively learned representations that explicitly account for spurious feature encoding, providing theoretical guidance for robust pre-training.

### Practical Contributions

1. **CR-InfoNCE Method:** Our curvature-aware contrastive loss is expected to improve worst-group accuracy by 5-15% on standard benchmarks while maintaining competitive average accuracy. The method requires no group annotations and is applicable during standard pre-training.

2. **Diagnostic Tools:** We will release a toolkit for analyzing shortcut learning dynamics in contrastive learning, including efficient Hessian estimation code, probing protocols, and visualization tools for loss landscape geometry.

3. **Benchmark Contributions:** Our synthetic and semi-synthetic datasets with controlled spurious correlations will provide standardized testbeds for evaluating robustness of self-supervised methods.

### Broader Impact

This research directly addresses the workshop's objectives by:

- **Advancing foundational understanding:** We provide the first systematic study of loss landscape geometry's role in shortcut learning for self-supervised paradigms, extending prior work limited to supervised settings.

- **Enabling robust foundation models:** As SSCL becomes the dominant pre-training paradigm, our methods and insights help ensure that foundation models do not propagate spurious correlations to downstream applications, improving reliability in high-stakes domains.

- **Bridging theory and practice:** Our geometric insights translate directly into practical regularization techniques, demonstrating how fundamental understanding enables effective solutions.

- **Catalyzing future research:** By establishing connections between optimization geometry and shortcut learning in SSCL, we open new research directions exploring similar phenomena in other self-supervised paradigms (masked modeling, generative approaches) and modalities (text, audio, graphs).

The expected outcomes position this work as a significant contribution to both the theoretical understanding of spurious correlations in modern learning paradigms and the practical toolkit for building robust AI systems—goals central to the workshop's mission of addressing the foundations and solutions for shortcut learning in deep learning.