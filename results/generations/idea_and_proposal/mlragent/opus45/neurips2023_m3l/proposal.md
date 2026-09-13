# Research Proposal: Understanding Grokking Through the Lens of Representation Learning Dynamics

## 1. Introduction

### Background

Deep learning has achieved remarkable empirical success across diverse domains, yet many fundamental phenomena remain theoretically unexplained. Among these, *grokking*—the sudden emergence of generalization long after a neural network has memorized its training data—stands as one of the most intriguing puzzles in modern machine learning. First systematically documented by Power et al. (2022) in the context of algorithmic tasks like modular arithmetic, grokking challenges our conventional understanding of the learning process, where generalization typically develops concurrently with training loss reduction.

The phenomenon of grokking carries profound implications for both theory and practice. From a theoretical perspective, it suggests that the mechanisms governing memorization and generalization are fundamentally distinct, operating on different timescales and potentially driven by different dynamics. From a practical standpoint, understanding grokking could unlock strategies for accelerating generalization in large-scale models, where prolonged training incurs enormous computational costs.

Recent investigations have approached grokking from multiple angles. The $\mathbf{Li_2}$ framework (Tian, 2025) delineates three learning stages involving lazy learning, independent feature learning, and interactive feature learning. GrokAlign (Walker et al., 2025) demonstrates that Jacobian regularization can induce grokking efficiently, while Musat (2025) interprets post-memorization dynamics as constrained optimization on the zero-loss manifold. Zhou et al. (2024) offer a frequency-based explanation, and Kumar et al. (2024) frame grokking as a transition from lazy to rich training dynamics. Despite these valuable contributions, a unified theoretical framework that explains *when* and *why* grokking occurs—and that provides predictive power—remains elusive.

### Research Objectives

This research proposes to develop a comprehensive theoretical framework for understanding grokking through the lens of representation learning dynamics. Our central hypothesis is that grokking occurs when learned representations undergo a phase transition from "memorization-compatible" configurations (high-dimensional, sample-specific encodings) to "generalization-compatible" configurations (low-dimensional, structure-aligned representations). Specifically, we aim to:

1. **Establish geometric metrics** that quantitatively characterize representation quality during training, including intrinsic dimensionality, class manifold separation, and alignment with task structure.

2. **Derive theoretical conditions** under which gradient descent induces representation compression, connecting to implicit regularization and norm minimization on the loss manifold.

3. **Develop predictive models** for grokking timing based on measurable properties of data structure, model architecture, and regularization strength.

4. **Validate the framework** through comprehensive experiments across synthetic and real-world tasks, demonstrating practical utility for accelerating generalization.

### Significance

This research addresses the critical need for principled understanding of deep learning phenomena as we enter the large model era. By providing a predictive theory of grokking, we can potentially: (1) detect imminent generalization without exhaustive training, (2) design training protocols that accelerate the transition from memorization to generalization, and (3) inform architectural choices that promote favorable representation dynamics. These advances would significantly reduce the computational burden of training foundation models while deepening our fundamental understanding of neural network learning.

## 2. Methodology

### 2.1 Theoretical Framework: Representation Geometry Analysis

#### 2.1.1 Representation Quality Metrics

We define a comprehensive set of geometric metrics to characterize the evolution of learned representations during training. Let $\mathbf{h}_l(x) \in \mathbb{R}^d$ denote the representation at layer $l$ for input $x$, and let $\mathcal{H}_l = \{\mathbf{h}_l(x_i)\}_{i=1}^n$ be the set of representations for training samples.

**Intrinsic Dimensionality (ID):** We measure the effective dimensionality of the representation manifold using the two-nearest-neighbor estimator:

$$\text{ID}(\mathcal{H}_l) = \left( \frac{1}{n} \sum_{i=1}^n \log \frac{r_2(i)}{r_1(i)} \right)^{-1}$$

where $r_1(i)$ and $r_2(i)$ are the distances to the first and second nearest neighbors of $\mathbf{h}_l(x_i)$.

**Class Manifold Capacity:** Following Zheng et al. (2024), we compute the manifold capacity $\alpha_M$ based on the separability of class-conditional representations:

$$\alpha_M = \frac{P}{N_{\text{eff}}}$$

where $P$ is the number of classifiable dichotomies and $N_{\text{eff}}$ is the effective number of feature dimensions.

**Structure Alignment Score (SAS):** We introduce a metric quantifying how well representations align with underlying task structure:

$$\text{SAS}(\mathcal{H}_l, \mathcal{G}) = \frac{\text{tr}(\mathbf{K}_h \mathbf{K}_g)}{\|\mathbf{K}_h\|_F \|\mathbf{K}_g\|_F}$$

where $\mathbf{K}_h$ is the kernel matrix of representations and $\mathbf{K}_g$ is the kernel matrix induced by the ground-truth task structure $\mathcal{G}$.

**Representation Compression Ratio (RCR):** We define the compression ratio as:

$$\text{RCR}(t) = \frac{\text{ID}(\mathcal{H}_l^{(0)})}{\text{ID}(\mathcal{H}_l^{(t)})}$$

tracking how representations compress over training time $t$.

#### 2.1.2 Phase Transition Model

We hypothesize that grokking corresponds to a phase transition in representation space. Let $\phi: \mathcal{X} \to \mathcal{H}$ denote the learned representation mapping. We model the representation dynamics as:

$$\frac{d\phi}{dt} = -\nabla_\phi \mathcal{L}_{\text{train}} + \lambda \mathcal{R}(\phi)$$

where $\mathcal{L}_{\text{train}}$ is the training loss and $\mathcal{R}(\phi)$ represents implicit or explicit regularization effects. We decompose the representation into memorization and generalization components:

$$\phi(x) = \phi_{\text{mem}}(x) + \phi_{\text{gen}}(x)$$

where $\phi_{\text{mem}}$ captures sample-specific information and $\phi_{\text{gen}}$ captures task-relevant structure.

**Phase Transition Condition:** We conjecture that grokking occurs when:

$$\|\phi_{\text{gen}}\|^2 > \gamma \|\phi_{\text{mem}}\|^2$$

for some critical threshold $\gamma$ that depends on task complexity and model architecture.

### 2.2 Theoretical Analysis: Implicit Regularization and Representation Compression

#### 2.2.1 Gradient Flow Analysis on Zero-Loss Manifold

Building on Musat (2025), we analyze the post-memorization dynamics when the network reaches the zero-loss manifold $\mathcal{M}_0 = \{\theta : \mathcal{L}(\theta) = 0\}$. The projected gradient flow becomes:

$$\frac{d\theta}{dt} = -P_{\mathcal{M}_0}(\theta) \nabla \|\theta\|^2$$

where $P_{\mathcal{M}_0}(\theta)$ is the projection onto the tangent space of $\mathcal{M}_0$.

**Theorem 1 (Representation Compression under Weight Decay):** For a two-layer network $f(x) = W_2 \sigma(W_1 x)$ with weight decay $\lambda$, under mild regularity conditions, the intrinsic dimensionality of hidden representations satisfies:

$$\frac{d \text{ID}(\mathcal{H})}{dt} \leq -\lambda \cdot g(\text{ID}(\mathcal{H}), \kappa)$$

where $g$ is a monotonically increasing function and $\kappa$ measures the rank deficiency of the Jacobian.

#### 2.2.2 Grokking Time Prediction

We derive a predictive model for grokking time $T_{\text{grok}}$ based on observable quantities:

$$T_{\text{grok}} \approx T_{\text{mem}} + \frac{1}{\lambda_{\text{eff}}} \log\left(\frac{\text{ID}_0}{\text{ID}_{\text{crit}}}\right) \cdot \mathcal{C}(\text{task})$$

where:
- $T_{\text{mem}}$ is the memorization time
- $\lambda_{\text{eff}}$ is the effective regularization strength (combining explicit weight decay and implicit regularization)
- $\text{ID}_0$ is the initial intrinsic dimensionality
- $\text{ID}_{\text{crit}}$ is the critical dimensionality for generalization
- $\mathcal{C}(\text{task})$ is a task complexity measure related to the minimum description length of the target function

### 2.3 Experimental Design

#### 2.3.1 Synthetic Experiments

**Modular Arithmetic Tasks:** Following Power et al., we study grokking on modular arithmetic operations ($a \circ b \mod p$ for operations $\circ \in \{+, -, \times, \div\}$) using transformers and MLPs. We systematically vary:
- Prime $p \in \{17, 31, 59, 97, 113\}$
- Weight decay $\lambda \in \{0, 10^{-3}, 10^{-2}, 10^{-1}\}$
- Learning rate $\eta \in \{10^{-4}, 10^{-3}, 10^{-2}\}$
- Training fraction $\rho \in \{0.3, 0.5, 0.7\}$

**Sparse Parity Tasks:** We study parity functions over $k$-sparse subsets of $n$-bit inputs, which provide controllable task complexity.

**Group Theory Tasks:** Learning group operations on finite groups of varying sizes and structures.

#### 2.3.2 Real-World Experiments

**Image Classification:** We investigate grokking phenomena on CIFAR-10 and subsets of ImageNet using ResNets and Vision Transformers with varying degrees of overparameterization.

**Language Modeling:** We examine representation dynamics during fine-tuning of small language models on algorithmic reasoning tasks.

#### 2.3.3 Measurement Protocol

At regular training intervals, we compute:
1. Training and test accuracy/loss
2. Intrinsic dimensionality of representations at each layer
3. Manifold capacity metrics
4. Structure alignment scores (when ground truth structure is available)
5. Weight norms and gradient statistics
6. Jacobian rank and singular value distributions

#### 2.3.4 Evaluation Metrics

**Prediction Accuracy:** We evaluate our grokking time prediction model using:

$$\text{MAPE} = \frac{1}{N}\sum_{i=1}^N \left|\frac{T_{\text{grok}}^{(i)} - \hat{T}_{\text{grok}}^{(i)}}{T_{\text{grok}}^{(i)}}\right|$$

**Phase Transition Detection:** We use change-point detection on representation metrics to identify phase transitions and measure correlation with generalization emergence:

$$\rho_{\text{transition}} = \text{Corr}(t_{\text{metric}}, t_{\text{gen}})$$

where $t_{\text{metric}}$ is the detected transition time in representation metrics and $t_{\text{gen}}$ is the generalization onset time.

**Early Stopping Criterion Effectiveness:** We evaluate whether representation metrics can serve as reliable early stopping criteria:

$$\text{Efficiency} = \frac{T_{\text{grok}} - T_{\text{early}}}{T_{\text{grok}}}$$

measuring the fraction of training saved while achieving target generalization performance.

### 2.4 Algorithmic Contributions

Based on our theoretical framework, we propose two practical algorithms:

**Algorithm 1: Representation-Based Grokking Predictor**
```
Input: Training data D, model f, hyperparameters θ
Output: Predicted grokking time T_grok

1. Train until memorization (training accuracy ≈ 100%)
2. Compute initial ID_0 = ID(H_l)
3. Estimate effective regularization λ_eff
4. Compute task complexity C(task) from data statistics
5. Apply prediction formula: T_grok = T_mem + (1/λ_eff) × log(ID_0/ID_crit) × C(task)
```

**Algorithm 2: Accelerated Grokking via Representation Shaping**
```
Input: Training data D, model f, target compression rate c
Output: Trained model with accelerated generalization

1. Standard training until memorization
2. While test accuracy below threshold:
   a. Compute current ID and SAS
   b. Add auxiliary loss: L_aux = β₁ × ID(H) - β₂ × SAS(H, G)
   c. Update: θ ← θ - η∇(L_train + L_aux)
3. Return trained model
```

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Theoretical Contributions:**
   - A unified framework characterizing grokking through representation geometry phase transitions
   - Formal conditions under which gradient-based optimization induces representation compression
   - Predictive bounds on grokking timing as a function of task complexity, architecture, and regularization

2. **Empirical Contributions:**
   - Comprehensive characterization of representation dynamics across diverse grokking scenarios
   - Validation of the phase transition hypothesis through systematic experiments
   - Demonstration that representation metrics provide early indicators of impending generalization

3. **Practical Tools:**
   - Grokking prediction algorithms enabling efficient training resource allocation
   - Representation shaping techniques that accelerate the transition from memorization to generalization
   - Guidelines for hyperparameter selection to achieve favorable representation dynamics

### Impact

**Scientific Impact:** This research will advance our fundamental understanding of how neural networks transition from memorization to generalization. By establishing connections between representation geometry and generalization dynamics, we contribute to the broader goal of developing a mathematical theory of deep learning that explains modern practice.

**Practical Impact:** For foundation model training, our predictive framework could significantly reduce computational costs by enabling early detection of generalization potential. The proposed acceleration techniques could shorten training times while maintaining or improving final model quality. For practitioners, our guidelines on regularization and architecture choices will provide principled approaches to training design.

**Broader Impact:** Understanding the memorization-generalization transition has implications for data privacy (determining when models have truly "forgotten" training examples), model efficiency (avoiding unnecessary training), and AI safety (understanding when models develop robust generalizations versus brittle memorized patterns).

By bridging the gap between deep learning theory and practice through the lens of representation learning dynamics, this research aims to provide both explanatory power for observed phenomena and actionable insights for improving large-scale model training.