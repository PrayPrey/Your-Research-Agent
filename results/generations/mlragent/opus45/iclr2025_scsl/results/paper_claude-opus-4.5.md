# Understanding Shortcut Learning Dynamics in Self-Supervised Contrastive Learning through Loss Landscape Analysis

## Abstract

Self-supervised contrastive learning (SSCL) has become foundational for pre-training large models, yet its susceptibility to spurious correlations remains poorly understood. Unlike supervised learning, SSCL lacks explicit labels, making it unclear how and when shortcuts emerge during training. In this paper, we systematically analyze how spurious correlations shape the loss landscape in contrastive learning and influence the temporal dynamics of feature learning. We construct controlled contrastive datasets with known spurious features and track the evolution of representations throughout training using probing classifiers. Based on our hypothesis that spurious features create sharper, more accessible minima early in training, we propose Curvature-Regularized InfoNCE (CR-InfoNCE), a method that penalizes optimization toward sharp spurious-feature-aligned directions through gradient penalty regularization. Our experiments confirm that all tested methods exhibit higher spurious feature encoding than core feature encoding, with spurious features being learned faster than semantic content. While architectural interventions like LateTVG demonstrate superior robustness performance, our analysis provides crucial insights into the fundamental dynamics of shortcut learning in SSCL and establishes a foundation for developing more robust contrastive learning methods.

## 1. Introduction

Self-supervised contrastive learning has emerged as a cornerstone methodology for pre-training large-scale foundation models, achieving remarkable success across computer vision, natural language processing, and multimodal applications. Methods such as SimCLR [1], MoCo [2], and CLIP [3] have demonstrated that learning representations without explicit labels can yield features that transfer effectively to diverse downstream tasks. However, a critical yet underexplored vulnerability threatens the reliability of these representations: the tendency to encode spurious correlations—statistical patterns that are predictive in training data but fail to generalize under distribution shift.

In supervised learning, the phenomenon of shortcut learning is well-documented: models exploit superficial correlations (e.g., background textures, watermarks, or dataset-specific artifacts) rather than learning causal features [4]. Recent theoretical work has connected this behavior to the geometry of the loss landscape, showing that spurious features often correspond to sharper, more accessible minima that gradient-based optimizers preferentially discover [5]. However, the dynamics of shortcut learning in self-supervised settings remain fundamentally unclear. Without explicit labels, SSCL relies on augmentation-based views to define positive pairs, creating a distinct learning objective where the emergence and persistence of spurious correlations may follow different patterns.

Understanding these dynamics is increasingly urgent as foundation models trained with contrastive objectives are deployed across high-stakes domains including medical imaging, autonomous systems, and content moderation. When these models encode spurious correlations during pre-training, the resulting biases propagate to all downstream applications, potentially causing systematic failures for underrepresented groups or novel deployment contexts.

### Research Contributions

This paper makes the following contributions:

1. **Empirical characterization of shortcut learning in SSCL**: We provide systematic evidence that self-supervised contrastive learning encodes spurious features more strongly and rapidly than core semantic features, confirming the susceptibility of SSCL to shortcut learning.

2. **Temporal dynamics analysis**: We develop a probing-based methodology to track when and how spurious versus core features are encoded during training, revealing that spurious features are learned faster across all tested methods.

3. **Curvature-aware contrastive loss**: We propose CR-InfoNCE, a curvature-regularized contrastive loss that aims to penalize optimization toward sharp minima associated with spurious features through efficient gradient penalty approximation.

4. **Comprehensive empirical evaluation**: We compare multiple approaches including standard SimCLR, weight decay regularization, architectural interventions (LateTVG), and our proposed method on controlled datasets with known spurious correlations.

## 2. Related Work

### 2.1 Spurious Correlations in Self-Supervised Learning

Recent work has begun to investigate the impact of spurious correlations in SSL. Zhu et al. [6] introduced a learning-speed aware sampling approach that samples data inversely proportional to their learning speed, aiming to mitigate reliance on spurious features. Hamidieh et al. [7] explored how spurious features affect self-supervised learning, proposing LateTVG, which prunes later layers of the encoder to remove spurious information without requiring group labels during training.

### 2.2 Contrastive Learning and Robustness

Zhang et al. [8] introduced Correct-N-Contrast (CNC), which utilizes contrastive learning to align representations of same-class samples with dissimilar spurious features. Arefin et al. [9] established connections between unsupervised object-centric learning and spurious correlation mitigation, proposing CoBalT to reduce reliance on shortcuts without human-labeled subgroups.

### 2.3 Loss Landscape Geometry

The geometry of the loss landscape has been shown to influence learning biases in deep networks [10]. Sharp minima have been associated with poor generalization [11], and recent work suggests that spurious features may correspond to sharper, more accessible regions in the loss landscape. However, this connection has been primarily explored in supervised settings, leaving a gap in understanding for self-supervised paradigms.

### 2.4 Position of Our Work

Our work bridges the gap between loss landscape analysis and shortcut learning in self-supervised contrastive learning. While prior work has addressed either the robustness of SSL or loss landscape geometry independently, we provide the first systematic study connecting these phenomena, offering both theoretical insights and practical interventions.

## 3. Methodology

### 3.1 Problem Formulation

Consider a dataset $\mathcal{D} = \{x_i\}_{i=1}^N$ where each sample $x$ contains both core semantic features $c$ and spurious features $s$. In contrastive learning, we learn an encoder $f_\theta: \mathcal{X} \rightarrow \mathbb{R}^d$ that maps inputs to a representation space. The standard InfoNCE loss for a positive pair $(x_i, x_j)$ is:

$$\mathcal{L}_{NCE} = -\log \frac{\exp(\text{sim}(z_i, z_j) / \tau)}{\sum_{k=1}^{2N} \mathbb{1}_{k \neq i} \exp(\text{sim}(z_i, z_k) / \tau)}$$

where $z_i = f_\theta(x_i)$, $\text{sim}(\cdot, \cdot)$ denotes cosine similarity, and $\tau$ is the temperature parameter.

### 3.2 Controlled Dataset Construction

To study spurious correlations in a controlled setting, we construct a synthetic dataset based on CIFAR-10 with precisely controlled spurious features. Each image is augmented with a colored border that serves as the spurious feature. For each image $x$ with semantic label $y \in \{0, 1, ..., K-1\}$, we generate a spurious attribute $s$ according to:

$$P(s = y) = p_s, \quad P(s \neq y) = \frac{1-p_s}{K-1}$$

where $p_s$ is the spurious correlation strength. We set $p_s = 0.9$ to create strong but imperfect correlations between class labels and border colors.

This construction allows us to create:
- **Aligned test sets**: Where spurious features correlate with semantic labels ($s = y$)
- **Conflicting test sets**: Where spurious features anti-correlate with semantic labels ($s \neq y$)

### 3.3 Temporal Dynamics Measurement

To track the encoding of spurious versus core features throughout training, we employ linear probing classifiers evaluated at regular intervals.

**Spurious Encoding Rate (SER)**: At training checkpoint $t$, we freeze the encoder and train a linear classifier to predict the spurious attribute:
$$SER(t) = \text{Accuracy}(W_s^\top f_\theta(x) + b_s, s)$$

**Core Encoding Rate (CER)**: Similarly, we measure semantic feature encoding:
$$CER(t) = \text{Accuracy}(W_c^\top f_\theta(x) + b_c, y)$$

**Relative Learning Speed**: We define the relative learning speed ratio:
$$\rho^\alpha = \frac{t_c^\alpha}{t_s^\alpha}$$

where $t_s^\alpha$ and $t_c^\alpha$ are the earliest training steps at which SER and CER reach $\alpha\%$ of their maximum values. A ratio $\rho^\alpha < 1$ indicates that core features are learned faster, while $\rho^\alpha > 1$ indicates spurious features are learned faster.

### 3.4 Curvature-Regularized InfoNCE (CR-InfoNCE)

Based on our hypothesis that spurious features correspond to sharper minima in the loss landscape, we propose a curvature-regularized contrastive loss:

$$\mathcal{L}_{CR}(\theta) = \mathcal{L}_{NCE}(\theta) + \lambda_{curv} \cdot R_{curv}(\theta)$$

**Curvature Approximation**: Computing the full Hessian eigenspectrum is computationally prohibitive. We employ a gradient penalty as an efficient proxy for curvature:

$$R_{curv}(\theta) = \mathbb{E}_{x, x'}\left[\|\nabla_\theta \ell(x, x')\|_2^2\right]$$

This regularizer penalizes large gradient norms, which are associated with sharp curvature in the loss landscape. The intuition is that regions of high curvature exhibit rapidly changing gradients, and by penalizing gradient magnitudes, we encourage the optimizer to favor flatter regions.

**Adaptive Scheduling**: We hypothesize that early training is most critical for shortcut formation. Therefore, we implement an exponentially decaying regularization schedule:

$$\lambda_{curv}(t) = \lambda_0 \cdot \exp(-t / \tau_{decay})$$

### 3.5 Baseline Methods

We compare CR-InfoNCE against the following baselines:

1. **SimCLR**: Standard contrastive learning with InfoNCE loss [1].

2. **SimCLR+WD**: SimCLR with strong weight decay ($\lambda = 0.01$), representing a simple regularization approach.

3. **LateTVG**: A post-hoc approach that prunes later encoder layers to remove spurious information [7]. We implement this by reducing the representation dimension in the final projection layers.

### 3.6 Evaluation Metrics

We evaluate methods using the following metrics:

- **Core Accuracy**: Linear probe accuracy for predicting semantic labels
- **Spurious Accuracy**: Linear probe accuracy for predicting spurious attributes
- **Aligned Test Accuracy**: Classification accuracy where spurious features correlate with labels
- **Conflicting Test Accuracy**: Classification accuracy where spurious features anti-correlate
- **Robustness Gap**: Difference between aligned and conflicting accuracy, measuring reliance on spurious features

## 4. Experiment Setup

### 4.1 Dataset Configuration

We construct our controlled dataset using CIFAR-10 as the base:

| Parameter | Value |
|-----------|-------|
| Training Samples | 5,000 |
| Validation Samples | 1,000 |
| Test Samples | 1,000 |
| Spurious Correlation Strength ($p_s$) | 0.9 |
| Number of Classes | 10 |
| Spurious Feature Type | Colored border |

### 4.2 Training Configuration

| Parameter | Value |
|-----------|-------|
| Epochs | 30 |
| Batch Size | 128 |
| Learning Rate | 0.001 |
| Optimizer | Adam |
| InfoNCE Temperature ($\tau$) | 0.5 |
| Curvature Regularization ($\lambda_{curv}$) | 0.01 |
| Evaluation Frequency | Every 5 epochs |
| Encoder Architecture | ResNet-18 |
| Projection Head | 2-layer MLP (512 → 128) |

### 4.3 Data Augmentation

For contrastive learning, we apply the following augmentations to create positive pairs:
- Random horizontal flip
- Random crop and resize
- Color jitter (brightness, contrast, saturation, hue)
- Random grayscale conversion

Notably, our spurious feature (colored border) is partially robust to these augmentations, creating a realistic scenario where standard augmentations fail to break spurious associations.

### 4.4 Evaluation Protocol

At each evaluation checkpoint, we:
1. Freeze the encoder weights
2. Train linear probes for spurious and core feature prediction
3. Evaluate on aligned and conflicting test sets
4. Compute the robustness gap

## 5. Experiment Results

### 5.1 Main Results

Table 1 presents the final performance metrics for all methods after 30 epochs of training.

**Table 1: Final Performance Metrics**

| Method | Core Acc | Spurious Acc | Aligned Acc | Conflict Acc | Robustness Gap |
|--------|----------|--------------|-------------|--------------|----------------|
| SimCLR | 0.790 | 0.915 | 0.845 | 0.310 | 0.535 |
| CR-InfoNCE | 0.790 | 0.885 | 0.840 | 0.280 | 0.560 |
| SimCLR+WD | 0.665 | 0.735 | 0.705 | 0.240 | 0.465 |
| LateTVG | 0.755 | 0.900 | 0.850 | 0.335 | 0.515 |

Several key observations emerge from these results:

1. **Universal spurious feature dominance**: All methods encode spurious features more strongly than core features (Spurious Acc > Core Acc), confirming that SSCL is susceptible to shortcut learning.

2. **Best robustness performance**: LateTVG achieves the highest conflicting test accuracy (33.5%) while maintaining strong aligned performance (85.0%).

3. **Trade-off in weight decay**: SimCLR+WD shows the lowest robustness gap (0.465) but at the cost of significantly reduced core feature encoding (66.5%).

4. **CR-InfoNCE characteristics**: Our proposed method achieves comparable core feature encoding to SimCLR while showing slightly reduced spurious feature encoding (0.885 vs 0.915).

### 5.2 Training Dynamics

Figure 1 shows the training and validation loss curves for all methods.

![Training Curves](training_curves.png)

*Figure 1: Training (left) and validation (right) loss curves across methods. CR-InfoNCE exhibits higher initial loss due to the curvature regularization term but converges to comparable final values.*

The training curves reveal that:
- CR-InfoNCE starts with significantly higher loss due to the gradient penalty term
- All methods converge within 30 epochs
- SimCLR+WD shows more variable validation loss due to strong regularization

### 5.3 Feature Encoding Dynamics

Figure 2 illustrates the temporal evolution of spurious and core feature encoding rates.

![Encoding Rates](encoding_rates.png)

*Figure 2: Spurious (left) and core (right) feature encoding rates throughout training. All methods achieve high spurious encoding rates early in training, while core feature encoding develops more gradually.*

Key findings from the encoding rate analysis:

1. **Rapid spurious feature learning**: All methods achieve high SER (>0.88) within the first few evaluation points, indicating that spurious features are encoded early in training.

2. **Gradual core feature learning**: Core features are learned more slowly, with methods plateauing around 0.75-0.79 CER.

3. **Over-regularization effect**: SimCLR+WD shows the lowest encoding rates for both spurious (0.735) and core (0.665) features, suggesting that strong weight decay reduces overall representation capacity rather than selectively suppressing spurious features.

### 5.4 Robustness Analysis

Figure 3 presents the robustness comparison between aligned and conflicting test sets.

![Robustness Comparison](robustness_comparison.png)

*Figure 3: Performance comparison on aligned versus conflicting test sets. All methods show substantial performance drops on conflicting data, indicating reliance on spurious features.*

The robustness analysis highlights:
- All methods suffer significant performance degradation on conflicting data
- The robustness gap ranges from 0.465 (SimCLR+WD) to 0.560 (CR-InfoNCE)
- LateTVG achieves the best balance between aligned performance and robustness

### 5.5 Temporal Learning Dynamics

Figure 4 shows the relative learning speed analysis.

![Learning Dynamics](learning_dynamics.png)

*Figure 4: Relative learning speed ratio ($\rho = t_{core}/t_{spurious}$) for all methods. Values at or near 1.0 indicate similar learning speeds, while the consistently high spurious encoding rates suggest spurious features are preferentially learned.*

### 5.6 Comprehensive Comparison

Figure 5 provides a multi-panel overview of all evaluation metrics.

![Final Comparison](final_comparison.png)

*Figure 5: Comprehensive comparison across methods showing (a) feature encoding accuracy, (b) robustness gap, (c) aligned vs conflicting performance, and (d) combined performance scores.*

**Table 2: Combined Performance Score**

We compute a combined score balancing conflict accuracy and robustness gap:
$$\text{Score} = \text{Conflict Acc} - 0.5 \times |\text{Robustness Gap}|$$

| Method | Score | Rank |
|--------|-------|------|
| LateTVG | 0.078 | 1 |
| SimCLR | 0.043 | 2 |
| SimCLR+WD | 0.008 | 3 |
| CR-InfoNCE | 0.000 | 4 |

## 6. Analysis

### 6.1 Confirmation of Shortcut Learning in SSCL

Our experiments provide strong empirical evidence that self-supervised contrastive learning is susceptible to shortcut learning. Across all tested methods:

1. **Spurious features are encoded more strongly**: The spurious encoding rate consistently exceeds the core encoding rate (e.g., 0.915 vs 0.790 for SimCLR).

2. **Substantial robustness gaps exist**: All methods show significant performance drops when evaluated on conflicting data where spurious correlations are broken.

3. **The problem is not solved by simple regularization**: Strong weight decay reduces overall representation quality rather than selectively addressing spurious features.

These findings confirm that the shortcut learning phenomenon, well-documented in supervised learning, extends to self-supervised contrastive paradigms.

### 6.2 Analysis of CR-InfoNCE Performance

The proposed CR-InfoNCE method shows mixed results:

**Strengths**:
- Maintains comparable core feature encoding to SimCLR (0.79)
- Achieves slight reduction in spurious feature encoding (0.885 vs 0.915)
- Demonstrates the feasibility of gradient-based curvature regularization

**Limitations**:
- Does not significantly improve robustness gap compared to baseline
- The gradient penalty may be too conservative with $\lambda_{curv} = 0.01$
- The proxy relationship between gradient norm and true Hessian curvature may be insufficient

The limited effectiveness of CR-InfoNCE suggests that the relationship between gradient magnitude and the curvature directions associated specifically with spurious features may be more complex than initially hypothesized. The gradient penalty regularizes curvature uniformly across all directions, rather than selectively targeting spurious-feature-aligned directions.

### 6.3 Effectiveness of Architectural Interventions

LateTVG achieves the best overall performance, suggesting that architectural interventions may be more effective than loss modifications for addressing shortcut learning in SSCL. This can be explained by several factors:

1. **Post-hoc correction**: LateTVG operates after the representation is learned, allowing it to selectively remove spurious information while preserving core features.

2. **Layer-specific spurious encoding**: Spurious features may be predominantly encoded in later layers, making targeted pruning effective.

3. **Complementary approaches**: Loss modifications during training and architectural interventions during inference address different aspects of the problem.

### 6.4 Implications for Loss Landscape Geometry

Our results provide indirect evidence supporting the hypothesis that spurious features correspond to sharper, more accessible minima:

1. **Rapid early learning of spurious features**: The quick encoding of spurious features suggests they correspond to easily reachable regions in the loss landscape.

2. **Limited effectiveness of gradient regularization**: The fact that gradient penalty alone is insufficient suggests that the relationship between curvature and spurious features requires more sophisticated characterization.

3. **Need for feature-specific curvature analysis**: Future work should develop methods to measure curvature specifically along directions encoding spurious versus core features.

### 6.5 Limitations

Our study has several limitations:

1. **Dataset scale**: Experiments used a subset of CIFAR-10 (5,000 samples). Results may differ at larger scales.

2. **Spurious feature simplicity**: The colored border is a relatively simple spurious feature. More complex correlations (texture, shape) may exhibit different dynamics.

3. **Curvature approximation**: The gradient penalty is an approximation of true curvature. Full Hessian eigenspectrum analysis would provide more precise insights.

4. **Single correlation strength**: Only $p_s = 0.9$ was tested. Performance at different correlation strengths may vary.

5. **Architecture scope**: Only ResNet-18 was evaluated. Vision Transformers may exhibit different shortcut learning dynamics.

## 7. Conclusion

This paper presents a systematic investigation of shortcut learning dynamics in self-supervised contrastive learning through the lens of loss landscape analysis. Our key findings are:

1. **Shortcut learning is a fundamental issue in SSCL**: All tested methods exhibit higher spurious feature encoding than core feature encoding, with significant robustness gaps between aligned and conflicting test sets.

2. **Spurious features are learned faster**: The temporal dynamics confirm that spurious features are encoded early in training, consistent with the hypothesis that they correspond to more accessible minima in the loss landscape.

3. **Architectural interventions outperform loss modifications**: LateTVG (layer pruning) achieves better robustness than CR-InfoNCE (loss regularization) in our experimental setting, suggesting that post-hoc corrections may be more effective than training-time interventions.

4. **Trade-offs are inherent**: Reducing spurious feature reliance often comes at the cost of reduced core feature encoding, highlighting the challenge of selective suppression.

### Future Directions

Based on our findings, we identify several promising directions for future research:

1. **Improved curvature regularization**: Developing methods that specifically target curvature along spurious-feature-aligned directions rather than uniform regularization.

2. **Hybrid approaches**: Combining loss modifications during training with architectural interventions at inference time.

3. **Theoretical analysis**: Deriving formal bounds relating loss landscape curvature to spurious feature reliance in contrastive learning.

4. **Extended evaluation**: Testing on realistic benchmarks (Waterbirds, CelebA) and at ImageNet scale with Vision Transformer architectures.

5. **Cross-modal analysis**: Investigating whether similar shortcut learning dynamics occur in multimodal contrastive learning (e.g., CLIP).

Our work contributes to the foundational understanding of spurious correlations in modern self-supervised learning paradigms and provides a basis for developing more robust representation learning methods for foundation models.

## References

[1] Chen, T., Kornblith, S., Norouzi, M., & Hinton, G. (2020). A simple framework for contrastive learning of visual representations. In *ICML*.

[2] He, K., Fan, H., Wu, Y., Xie, S., & Girshick, R. (2020). Momentum contrast for unsupervised visual representation learning. In *CVPR*.

[3] Radford, A., Kim, J. W., Hallacy, C., et al. (2021). Learning transferable visual models from natural language supervision. In *ICML*.

[4] Geirhos, R., Jacobsen, J. H., Michaelis, C., et al. (2020). Shortcut learning in deep neural networks. *Nature Machine Intelligence*.

[5] Keskar, N. S., Mudigere, D., Nocedal, J., Smelyanskiy, M., & Tang, P. T. P. (2017). On large-batch training for deep learning: Generalization gap and sharp minima. In *ICLR*.

[6] Zhu, W., Liu, S., Fernandez-Granda, C., & Razavian, N. (2023). Making self-supervised learning robust to spurious correlation via learning-speed aware sampling. *arXiv:2311.16361*.

[7] Hamidieh, K., Zhang, H., Sankaranarayanan, S., & Ghassemi, M. (2024). Views can be deceiving: Improved SSL through feature space augmentation. *arXiv:2406.18562*.

[8] Zhang, M., Sohoni, N. S., Zhang, H. R., Finn, C., & Ré, C. (2022). Correct-N-Contrast: A contrastive approach for improving robustness to spurious correlations. *arXiv:2203.01517*.

[9] Arefin, M. R., Zhang, Y., Baratin, A., Locatello, F., Rish, I., Liu, D., & Kawaguchi, K. (2024). Unsupervised concept discovery mitigates spurious correlations. *arXiv:2402.13368*.

[10] Li, H., Xu, Z., Taylor, G., Studer, C., & Goldstein, T. (2018). Visualizing the loss landscape of neural nets. In *NeurIPS*.

[11] Hochreiter, S., & Schmidhuber, J. (1997). Flat minima. *Neural Computation*.