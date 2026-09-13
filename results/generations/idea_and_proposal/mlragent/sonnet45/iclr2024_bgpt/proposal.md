# Research Proposal: Unifying Edge of Stability Phenomenon with Generalization: A Sharpness-Aware Optimization Perspective

## 1. Title

**Theoretical and Empirical Analysis of Edge of Stability Training Dynamics: Connecting Progressive Sharpening with Generalization Through Loss Landscape Geometry**

## 2. Introduction

### Background

Deep learning has achieved remarkable success across diverse domains, yet a significant gap persists between empirical observations and theoretical understanding. One of the most intriguing phenomena challenging classical optimization theory is the Edge of Stability (EoS), first systematically characterized by Cohen et al. (2021). In the EoS regime, neural networks train successfully with gradient descent even when the loss sharpness—measured by the maximum eigenvalue of the Hessian $\lambda_{\max}(\nabla^2 L)$—exceeds the classical stability threshold of $2/\eta$ (where $\eta$ is the learning rate). This contradicts traditional convergence theory, which predicts divergence under such conditions.

The EoS phenomenon manifests through distinctive oscillatory dynamics: the sharpness progressively increases until approaching the stability edge, then suddenly decreases, creating characteristic sharpening-reduction cycles throughout training. While this behavior has been empirically observed across various architectures including ResNets, Vision Transformers, and MLPs, the theoretical mechanisms underlying EoS and—more critically—its connection to generalization performance remain poorly understood.

Simultaneously, the machine learning community has made significant progress in understanding generalization through the lens of loss landscape geometry. Sharpness-Aware Minimization (SAM) and its variants have demonstrated that explicitly seeking flat minima correlates with improved generalization. Recent work by Fojtik et al. (2025) reveals that different implicit regularization mechanisms—parameter norm minimization versus sharpness reduction—may conflict during training, with the learning rate mediating this balance particularly in the EoS regime.

### Research Gap

Despite these advances, critical questions remain unanswered:

1. **Mechanistic Understanding**: What are the fundamental mechanisms that enable stable training in the EoS regime despite violating classical stability conditions?

2. **Generalization Connection**: How do the sharpening-reduction cycles characteristic of EoS training relate to the implicit regularization that drives generalization?

3. **Predictive Framework**: Can we derive quantitative relationships between EoS dynamics and generalization performance that enable practical optimizer design?

4. **Unified Theory**: How can we reconcile the implicit bias toward flat minima with the oscillatory sharpness dynamics observed in EoS training?

### Research Objectives

This research aims to bridge the theory-practice gap in deep learning optimization by:

1. **Developing a rigorous theoretical framework** that characterizes EoS training dynamics through the lens of progressive sharpening-reduction cycles and their relationship to loss landscape geometry.

2. **Establishing quantitative connections** between EoS phenomena and generalization performance, unifying insights from sharpness-aware optimization with empirical observations of training dynamics.

3. **Deriving practical indicators** from EoS dynamics that can predict generalization and inform adaptive optimization strategies.

4. **Validating theoretical predictions** through systematic empirical investigation across diverse architectures, datasets, and hyperparameter configurations.

### Significance

This research addresses fundamental questions at the intersection of optimization and generalization theory, two critical topics identified in the workshop's call. The outcomes will:

- **Advance theoretical understanding** by providing mathematical characterizations of why and how neural networks succeed in regimes where classical theory predicts failure.

- **Enable practical improvements** by translating theoretical insights into optimizer modifications that exploit EoS dynamics for enhanced performance.

- **Bridge disciplinary gaps** by connecting optimization theory, statistical learning theory, and empirical deep learning practice.

- **Inform future research** by establishing a framework for analyzing other theory-practice gaps in deep learning.

## 3. Methodology

### 3.1 Theoretical Framework Development

#### 3.1.1 Mathematical Modeling of EoS Dynamics

We will develop a continuous-time model of gradient descent dynamics that captures the EoS phenomenon. Consider the gradient flow:

$$\frac{d\theta}{dt} = -\nabla L(\theta; \mathcal{D})$$

where $\theta \in \mathbb{R}^d$ represents network parameters and $L(\theta; \mathcal{D})$ is the empirical loss over dataset $\mathcal{D}$.

To analyze sharpness evolution, we track the maximum Hessian eigenvalue:

$$\lambda_{\max}(t) = \max_{\|v\|=1} v^T \nabla^2 L(\theta(t)) v$$

**Key theoretical question**: Characterize the dynamics of $\lambda_{\max}(t)$ and establish conditions under which the system exhibits stable oscillations around the threshold $\lambda_{\text{edge}} = 2/\eta$.

We will extend the quadratic approximation framework by considering the third-order Taylor expansion:

$$L(\theta + \Delta\theta) \approx L(\theta) + \nabla L^T \Delta\theta + \frac{1}{2}\Delta\theta^T \nabla^2 L \Delta\theta + \frac{1}{6}\sum_{i,j,k} \frac{\partial^3 L}{\partial\theta_i\partial\theta_j\partial\theta_k}\Delta\theta_i\Delta\theta_j\Delta\theta_k$$

This allows us to analyze how third-order terms contribute to the self-stabilizing behavior observed in EoS.

#### 3.1.2 Connection to Implicit Regularization

We will formalize the relationship between EoS dynamics and implicit regularization through a sharpness-aware perspective. Define the sharpness-regularized objective:

$$L_{\text{SA}}(\theta) = L(\theta) + \alpha \cdot S(\theta)$$

where $S(\theta)$ measures local sharpness. We conjecture that EoS dynamics implicitly optimize a time-varying version:

$$L_{\text{effective}}(\theta, t) = L(\theta) + \alpha(t) \cdot S(\theta)$$

where $\alpha(t)$ varies according to the oscillatory EoS dynamics.

**Theoretical goal**: Prove that gradient descent in the EoS regime approximates gradient descent on $L_{\text{effective}}$ with appropriately characterized $\alpha(t)$, thereby establishing implicit bias toward flatter minima.

#### 3.1.3 Generalization Bounds

Building on PAC-Bayesian theory, we will derive generalization bounds that incorporate EoS-specific quantities. The standard generalization gap can be bounded as:

$$\mathbb{E}[L_{\text{test}}(\theta) - L_{\text{train}}(\theta)] \leq \sqrt{\frac{1}{2n}\left(\text{KL}(\theta \| \theta_0) + \log\frac{1}{\delta}\right)}$$

We will refine this by incorporating sharpness oscillation characteristics:

$$\mathbb{E}[L_{\text{test}}(\theta) - L_{\text{train}}(\theta)] \leq f\left(\int_0^T g(\lambda_{\max}(t), \eta) dt, n, \delta\right)$$

where $g(\lambda_{\max}(t), \eta)$ captures the regularization effect of EoS dynamics and $T$ is training duration.

### 3.2 Empirical Validation

#### 3.2.1 Experimental Design

**Architectures**: We will conduct experiments across:
- Convolutional networks: ResNet-18, ResNet-50, VGG-16
- Vision Transformers: ViT-Small, ViT-Base
- Multi-Layer Perceptrons: 3-10 hidden layers with varying widths

**Datasets**:
- Image classification: CIFAR-10, CIFAR-100, ImageNet (subset)
- Toy datasets: Two-dimensional classification for visualization
- Synthetic datasets: Controlled label noise levels (0%, 10%, 20%, 40%)

**Hyperparameter Sweeps**:
- Learning rates: $\eta \in \{0.001, 0.01, 0.05, 0.1, 0.5, 1.0\}$
- Batch sizes: $\{32, 64, 128, 256, 512\}$
- Optimizers: SGD, SGD with momentum (0.9), Adam
- Initialization schemes: Xavier, He, orthogonal

#### 3.2.2 Measurement Protocol

At regular intervals (every epoch or mini-batch), we will compute:

1. **Sharpness Metrics**:
   - Maximum Hessian eigenvalue $\lambda_{\max}$ via power iteration
   - Trace of Hessian $\text{tr}(\nabla^2 L)$
   - Top-k eigenvalues and eigenvectors
   - Local sharpness: $\max_{\|\epsilon\|=\rho} L(\theta + \epsilon) - L(\theta)$

2. **Loss Landscape Geometry**:
   - Loss along top eigenvector directions
   - 2D loss surface visualizations using filter normalization
   - Gradient predictiveness: $\nabla L(\theta)^T (\theta_{t+1} - \theta_t)$

3. **Generalization Indicators**:
   - Train/test accuracy and loss
   - Cross-entropy loss gap
   - Calibration error (Expected Calibration Error)

4. **Oscillation Characteristics**:
   - Frequency of sharpening-reduction cycles
   - Amplitude of $\lambda_{\max}$ oscillations
   - Phase relationship between loss and sharpness

#### 3.2.3 Analysis Methods

**Statistical Analysis**: We will employ:
- Correlation analysis between sharpness dynamics and generalization gap
- Principal Component Analysis (PCA) of Hessian spectra evolution
- Time-series analysis of oscillation patterns using Fourier transforms
- Causal inference methods to distinguish correlation from causation

**Comparative Studies**:
- EoS regime (large $\eta$) vs. stable regime (small $\eta$)
- Standard SGD vs. sharpness-aware variants (SAM, ESAM, GCSAM)
- Different phases of training (early, EoS onset, late)

### 3.3 Predictive Model Development

#### 3.3.1 EoS-based Generalization Indicators

We will derive practical indicators $\mathcal{I}_{\text{EoS}}$ that predict generalization from observable EoS dynamics:

$$\mathcal{I}_{\text{EoS}} = h\left(\langle\lambda_{\max}\rangle_T, \sigma_{\lambda}, f_{\text{osc}}, A_{\text{osc}}, \eta\right)$$

where:
- $\langle\lambda_{\max}\rangle_T$ is time-averaged maximum eigenvalue
- $\sigma_{\lambda}$ is standard deviation of sharpness oscillations
- $f_{\text{osc}}$ is oscillation frequency
- $A_{\text{osc}}$ is oscillation amplitude

**Validation**: Correlation between $\mathcal{I}_{\text{EoS}}$ and actual test performance across diverse settings.

#### 3.3.2 Adaptive Learning Rate Schedules

Based on theoretical insights, we will design adaptive learning rate strategies:

$$\eta(t) = \eta_0 \cdot \phi\left(\frac{\lambda_{\max}(t)}{\lambda_{\text{edge}}}, \frac{d\lambda_{\max}}{dt}\right)$$

where $\phi$ adjusts the learning rate based on proximity to the stability edge and sharpness evolution rate.

**Hypothesis**: This adaptive schedule will maintain beneficial EoS dynamics while preventing harmful instability.

### 3.4 Optimizer Modifications

We will develop novel optimizers that explicitly leverage EoS dynamics:

**EoS-Aware SAM (EoS-SAM)**:

$$
\begin{aligned}
\epsilon_t &= \rho \frac{\nabla L(\theta_t)}{\|\nabla L(\theta_t)\|} \cdot w(\lambda_{\max}(t), \lambda_{\text{edge}}) \\
\theta_{t+1} &= \theta_t - \eta \nabla L(\theta_t + \epsilon_t)
\end{aligned}
$$

where $w(\lambda_{\max}, \lambda_{\text{edge}})$ modulates perturbation magnitude based on EoS state.

### 3.5 Evaluation Metrics

**Theoretical Contributions**:
- Tightness of derived generalization bounds
- Accuracy of predicted oscillation dynamics
- Correspondence between continuous-time analysis and discrete updates

**Empirical Performance**:
- Test accuracy improvements
- Generalization gap reduction
- Computational efficiency (FLOPs, wall-clock time)
- Robustness to label noise
- Calibration quality

**Predictive Power**:
- Correlation coefficient between $\mathcal{I}_{\text{EoS}}$ and test performance ($r > 0.8$ target)
- Early-stopping decisions based on EoS indicators
- Hyperparameter selection guided by EoS theory

## 4. Expected Outcomes & Impact

### 4.1 Theoretical Contributions

**Unified Framework**: We expect to establish the first comprehensive theoretical framework that:
- Explains stable training in the EoS regime through analysis of higher-order loss landscape geometry
- Connects oscillatory sharpness dynamics to implicit regularization mechanisms
- Provides rigorous generalization bounds that incorporate EoS-specific phenomena

**Key Theoretical Results**:
1. **Convergence analysis** showing that third-order terms enable self-stabilization in EoS
2. **Implicit regularization equivalence** between EoS dynamics and time-varying sharpness-aware optimization
3. **Generalization bounds** that tighten classical results by accounting for EoS oscillations
4. **Phase transition characterization** describing the transition from stable to EoS regime

### 4.2 Practical Contributions

**Optimizer Design**: 
- EoS-SAM: A computationally efficient optimizer combining EoS insights with sharpness awareness, expected to achieve 1-2% accuracy improvements over SAM while reducing computational overhead by 20-30%
- Adaptive learning rate schedules that maintain optimal EoS dynamics throughout training

**Predictive Tools**:
- Online generalization indicators computable during training with minimal overhead (<5% additional computation)
- Early stopping criteria based on EoS dynamics that reduce training time by 15-25% without sacrificing performance
- Hyperparameter selection guidelines derived from EoS theory

### 4.3 Empirical Insights

**Comprehensive Characterization**: 
- Detailed maps of how architecture, learning rate, batch size, and initialization affect EoS dynamics and their relationship to generalization
- Identification of architectural properties that enhance beneficial EoS behavior
- Quantification of the generalization benefit attributable to EoS versus other implicit biases

**Robustness Analysis**:
- Demonstration that EoS-aware methods maintain advantages under label noise
- Analysis of failure modes and limitations of EoS-based approaches
- Guidelines for practitioners on when to exploit EoS dynamics

### 4.4 Broader Impact

**Bridging Theory-Practice Gap**: This research directly addresses the workshop's central theme by:
- Providing rigorous theoretical explanations for empirically observed phenomena
- Translating theoretical insights into practical algorithmic improvements
- Identifying new theory-practice discrepancies for future investigation

**Advancing Multiple Subfields**:
- **Optimization theory**: New analysis techniques for understanding training beyond classical stability
- **Generalization theory**: Refined understanding of implicit regularization mechanisms
- **Optimizer design**: Principled methods for developing next-generation optimizers

**Enabling Future Research**: The framework and tools developed will facilitate:
- Investigation of EoS in other domains (NLP, reinforcement learning)
- Analysis of EoS in large language models and foundation models
- Extension to other optimization phenomena (gradient starvation, catastrophic forgetting)

**Societal Benefits**: Improved optimizers and generalization understanding can:
- Reduce computational costs of training (environmental impact)
- Enable more reliable models (safety-critical applications)
- Lower barriers to entry for deep learning practitioners (democratization)

### 4.5 Validation and Dissemination

**Validation Criteria**:
- Theoretical predictions match empirical observations with <15% error
- Proposed optimizers outperform baselines on ≥80% of benchmark tasks
- At least one theoretical result provides novel insight not previously known
- Generalization indicators achieve correlation r > 0.8 with test performance

**Dissemination Plan**:
- Publication in top-tier venues (NeurIPS, ICML, ICLR)
- Open-source release of code, datasets, and trained models
- Interactive visualizations of EoS dynamics for educational purposes
- Workshop presentations and tutorial materials

This research proposal offers a comprehensive approach to understanding and exploiting the Edge of Stability phenomenon, with the potential to significantly advance both theoretical understanding and practical performance in deep learning. By rigorously connecting optimization dynamics to generalization through the unifying lens of loss landscape geometry, we aim to bridge a critical gap between theory and practice in modern machine learning.