# Research Proposal: Phase Transitions in Simplicity Bias: Understanding the Competition Between Feature Learning Stages

## 1. Introduction

### Background

Deep neural networks exhibit a remarkable phenomenon known as simplicity bias—the tendency to learn simple, low-complexity features before gradually acquiring more complex representations. This hierarchical learning process has been observed across diverse architectures, from convolutional networks to transformers, and appears fundamental to how neural networks organize their representations during training. Recent work by Zhang et al. (2025) has established theoretical foundations connecting this bias to saddle-to-saddle dynamics, demonstrating that networks progressively traverse invariant manifolds corresponding to increasingly complex solutions.

However, while the existence of simplicity bias is well-documented, the precise dynamics governing transitions between learning stages remain poorly understood. These transitions appear to involve complex competition between structures at different complexity scales, potentially explaining several puzzling phenomena in deep learning: the sudden generalization characteristic of grokking (Clauw et al., 2024; Li et al., 2023), the plateaus observed in neural scaling laws, and the emergence of reasoning capabilities in large language models (Hu et al., 2025). Understanding when and how these phase transitions occur is crucial for both theoretical insight and practical applications.

The challenge lies in the high-dimensional nature of neural network learning dynamics. As demonstrated in recent literature, intuitions from low-dimensional geometry often lead to inaccurate predictions about model behavior. The competition between feature learning stages involves intricate interactions across many neurons, layers, and timescales, requiring sophisticated mathematical frameworks that can capture these dependencies while remaining analytically tractable.

### Research Objectives

This research proposes to develop a comprehensive mathematical framework for understanding phase transitions in feature learning, with three primary objectives:

1. **Theoretical Foundation**: Derive mean-field equations capturing the competition dynamics between hierarchical feature learning stages, parameterized by network architecture (width, depth), optimization hyperparameters, and data complexity.

2. **Phase Diagram Construction**: Identify and characterize critical points where networks transition from learning one dominant feature class to another, mapping the boundaries between qualitatively different learning regimes.

3. **Empirical Validation and Application**: Validate theoretical predictions on real architectures, particularly transformers, and translate insights into practical methods for accelerating beneficial transitions through principled curriculum design.

### Significance

This research addresses fundamental questions at the intersection of optimization theory, statistical physics, and deep learning. By establishing predictive equations for transition timing and understanding the geometry of feature competition, we can:

- Explain why certain hyperparameter regimes produce staircase-like learning curves
- Provide principled guidance for training reasoning-capable models more efficiently
- Connect optimizer geometry to the sequential emergence of abstract representations
- Offer theoretical grounding for curriculum learning strategies
- Illuminate the mechanisms underlying emergent capabilities in large-scale models

## 2. Methodology

### 2.1 Theoretical Framework: Mean-Field Analysis of Hierarchical Feature Learning

#### Model Setup

We consider a neural network learning a target function decomposable into features of varying complexity. Let the target function be represented as:

$$f^*(x) = \sum_{k=1}^{K} \alpha_k \phi_k(x)$$

where $\phi_k(x)$ represents features of complexity level $k$, ordered such that $\phi_1$ corresponds to the simplest features (e.g., low-frequency Fourier components) and $\phi_K$ to the most complex. The coefficients $\alpha_k$ determine the relative importance of each feature class in the target.

For a two-layer network with hidden layer width $n$, we parameterize the network output as:

$$f(x; W, a) = \frac{1}{\sqrt{n}} \sum_{i=1}^{n} a_i \sigma(w_i^\top x)$$

where $w_i \in \mathbb{R}^d$ are first-layer weights, $a_i \in \mathbb{R}$ are second-layer weights, and $\sigma$ is the activation function.

#### Order Parameters and Mean-Field Equations

Following the mean-field approach, we introduce order parameters capturing the network's alignment with each feature class:

$$m_k(t) = \frac{1}{n} \sum_{i=1}^{n} \langle w_i(t), v_k \rangle^2$$

where $v_k$ represents the direction in weight space associated with feature class $k$. The dynamics of these order parameters under gradient descent with learning rate $\eta$ can be derived as:

$$\frac{dm_k}{dt} = \eta \left[ \underbrace{\beta_k(m_k)}_{\text{self-reinforcement}} - \underbrace{\sum_{j \neq k} \gamma_{kj}(m_k, m_j)}_{\text{competition}} + \underbrace{\xi_k(t)}_{\text{noise}} \right]$$

The self-reinforcement term $\beta_k(m_k)$ captures how learning feature $k$ promotes further learning of the same feature. The competition term $\gamma_{kj}$ models how learning feature $j$ affects the learning of feature $k$. We derive explicit forms for these terms:

$$\beta_k(m_k) = \alpha_k^2 \cdot g_k(m_k) \cdot (1 - m_k)$$

$$\gamma_{kj}(m_k, m_j) = \lambda_{kj} \cdot m_j \cdot h(m_k)$$

where $g_k$ and $h$ are functions determined by the activation function and data distribution, and $\lambda_{kj}$ encodes the structural interference between feature classes.

#### Width and Depth Scaling

To extend to deep networks, we employ a layer-wise mean-field analysis. For a network of depth $L$, we introduce layer-specific order parameters $m_k^{(\ell)}(t)$ and derive coupled ODEs:

$$\frac{dm_k^{(\ell)}}{dt} = \eta \left[ \beta_k^{(\ell)}(m_k^{(\ell)}, m_k^{(\ell-1)}) - \sum_{j \neq k} \gamma_{kj}^{(\ell)} + \chi_k^{(\ell)}(m_k^{(\ell+1)}) \right]$$

where $\chi_k^{(\ell)}$ captures the backward influence from later layers. In the infinite-width limit ($n \to \infty$), we establish connections to Neural Tangent Kernel theory while maintaining feature learning dynamics through appropriate scaling of the learning rate: $\eta = \eta_0 / n^\alpha$ with $\alpha \in [0, 1]$.

### 2.2 Phase Diagram Characterization

#### Critical Point Analysis

Phase transitions occur when the system's qualitative behavior changes, corresponding to bifurcations in the ODE system. We identify critical points by analyzing the stability of fixed points:

$$\frac{dm_k}{dt} = 0 \quad \forall k$$

The Jacobian matrix of the system at equilibrium determines stability:

$$J_{kj} = \frac{\partial}{\partial m_j}\left(\frac{dm_k}{dt}\right)$$

Phase transitions occur when eigenvalues of $J$ cross zero, indicating loss of stability of the current learning regime.

#### Control Parameters

We construct phase diagrams parameterized by:

1. **Learning rate** $\eta$: Affects the timescale of dynamics and the sharpness of transitions
2. **Batch size** $B$: Modulates the noise term $\xi_k(t)$ with variance $\propto 1/B$
3. **Weight decay** $\lambda_{\text{wd}}$: Adds regularization term favoring simpler features
4. **Data complexity** $\kappa$: Ratio of complex to simple features in the training data

The critical boundaries are derived by solving:

$$\det(J(\eta, B, \lambda_{\text{wd}}, \kappa)) = 0$$

### 2.3 Experimental Design and Validation

#### Synthetic Experiments

**Dataset Construction**: We create controlled datasets with known hierarchical structure:
- Fourier-based targets: $f^*(x) = \sum_{k=1}^{K} \alpha_k \cos(k \cdot \omega^\top x)$ where frequency $k$ determines complexity
- Boolean function compositions: nested XOR and AND operations of varying depth
- Polynomial features: $f^*(x) = \sum_{k=1}^{K} \alpha_k P_k(x)$ where $P_k$ are Hermite polynomials of degree $k$

**Metrics for Feature Complexity Tracking**:
1. **Spectral analysis**: Track the power spectrum of learned representations via Fourier decomposition
2. **Effective rank**: $r_{\text{eff}}(W) = \exp(H(\sigma_i / \|\sigma\|_1))$ where $H$ is entropy and $\sigma_i$ are singular values
3. **Alignment scores**: $A_k(t) = \|\text{proj}_{V_k} W(t)\|_F^2 / \|W(t)\|_F^2$ measuring projection onto feature subspaces

#### Transformer Experiments

**Architecture and Tasks**: We study GPT-style transformers on:
- Modular arithmetic (following grokking literature)
- Multi-step reasoning benchmarks (2WikiMultiHopQA)
- Mathematical problem-solving (GSM8K subset)

**Feature Complexity Measures**:
1. **Attention entropy**: $H_{\text{attn}}^{(\ell)} = -\sum_{i,j} A_{ij} \log A_{ij}$ per layer
2. **Representation dimensionality**: Intrinsic dimension estimates via nearest-neighbor methods
3. **Circuit complexity**: Probing classifiers for identifying learned computational circuits

**Transition Detection Protocol**:
1. Compute smoothed derivatives of complexity metrics: $\dot{C}_k(t) = \frac{d}{dt}\text{EMA}(C_k(t))$
2. Identify transition points as local maxima of $|\ddot{C}_k(t)|$
3. Correlate detected transitions with task performance improvements

#### Evaluation Metrics

| Metric | Description | Purpose |
|--------|-------------|---------|
| Transition timing error | $|t_{\text{pred}} - t_{\text{actual}}|$ | Validate theoretical predictions |
| Phase boundary accuracy | Classification accuracy of learning regime | Test phase diagram |
| Curriculum acceleration | Training time reduction with designed curriculum | Practical impact |
| Generalization gap dynamics | $\mathcal{L}_{\text{test}}(t) - \mathcal{L}_{\text{train}}(t)$ | Connect to grokking |

### 2.4 Curriculum Design Application

Based on the phase transition analysis, we develop a principled curriculum learning method:

**Algorithm: Transition-Aware Curriculum Learning**

1. **Initialize**: Train network with standard procedure, monitoring complexity metrics $\{C_k(t)\}$
2. **Detect plateau**: If $\dot{C}_k(t) < \epsilon$ for $T_{\text{wait}}$ steps, predict imminent transition
3. **Accelerate transition**: 
   - Option A: Temporarily increase learning rate by factor $\rho > 1$
   - Option B: Introduce data samples enriched in next-complexity features
   - Option C: Apply targeted noise injection to escape local minima
4. **Stabilize**: After transition detected, restore normal training parameters
5. **Repeat** until convergence

The acceleration factor $\rho$ and data mixing ratios are derived from the phase diagram analysis, ensuring the system crosses critical boundaries efficiently without destabilization.

## 3. Expected Outcomes & Impact

### Theoretical Contributions

1. **Predictive Equations**: Closed-form expressions for transition timing as functions of architecture and hyperparameters:
$$t_{\text{transition}}^{(k \to k+1)} = f(\eta, n, L, \kappa, \lambda_{\text{wd}})$$

2. **Phase Diagrams**: Complete characterization of learning regime boundaries, identifying:
   - Regions of smooth progressive learning
   - Regions prone to grokking-like delayed generalization
   - Critical hyperparameter combinations enabling rapid capability emergence

3. **Unified Framework**: Connection between simplicity bias, grokking, and scaling law plateaus through the lens of phase transitions, providing a coherent theoretical narrative for emergent capabilities.

### Practical Impact

1. **Training Efficiency**: Curriculum design methods reducing training time by an estimated 20-40% for reaching equivalent capability levels, with particular benefits for reasoning tasks.

2. **Hyperparameter Selection**: Principled guidelines for choosing learning rate schedules and batch sizes based on desired feature learning progression.

3. **Predictability of Emergence**: Tools for predicting when models will acquire specific capabilities, enabling better resource planning and safety evaluation.

### Broader Scientific Impact

This research bridges statistical physics concepts (phase transitions, order parameters) with deep learning theory, contributing to the growing field of neural network phenomenology. By establishing rigorous connections between optimization geometry and representation learning, we advance understanding of how complex capabilities emerge from simple learning rules—a question with implications extending beyond machine learning to neuroscience and cognitive science.

The framework developed here will serve as a foundation for future work on:
- Designing architectures with more predictable learning dynamics
- Understanding and controlling the acquisition of reasoning capabilities in large language models
- Developing theoretical tools for analyzing the interplay between data structure and learning progression

Ultimately, this research contributes to making deep learning more predictable, efficient, and interpretable—essential goals as neural networks are deployed in increasingly critical applications requiring reliable reasoning capabilities.