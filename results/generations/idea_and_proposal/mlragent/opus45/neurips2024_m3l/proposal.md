# Research Proposal

## Title
**Understanding Adam's Superiority over SGD on Transformers through Attention-Induced Loss Landscape Geometry: Theory, Analysis, and Architecture-Aware Optimizer Design**

---

## 1. Introduction

### Background

Deep learning has revolutionized artificial intelligence, yet the practice of training neural networks remains largely empirical, requiring extensive hyperparameter tuning and trial-and-error experimentation. This challenge is particularly acute in the large model era, where training billion-parameter Transformers incurs enormous computational costs. A fundamental question that exemplifies this gap between theory and practice concerns optimizer selection: why does Adam consistently outperform SGD when training Transformers, despite SGD's theoretical guarantees and success in convolutional networks?

The empirical dominance of Adam over SGD for Transformer training has been well-documented across natural language processing, computer vision, and multimodal learning tasks. Recent work by Kunstner et al. (2023) demonstrated that this performance gap persists even when controlling for gradient noise through large batch sizes, ruling out heavy-tailed gradient distributions as the primary explanation. Zhang et al. (2024) provided important empirical evidence of "block heterogeneity" in the Hessian spectrum of Transformers, suggesting that varying curvature across parameter groups may be responsible. However, a rigorous theoretical framework connecting attention mechanisms to loss landscape geometry, and subsequently to adaptive optimizer benefits, remains elusive.

### Research Objectives

This research aims to develop a comprehensive theoretical understanding of why Adam outperforms SGD specifically on Transformer architectures by:

1. **Analytically characterizing** how the softmax attention mechanism induces heterogeneous curvature across different parameter groups (query, key, value, and projection matrices).

2. **Proving theoretically** that Adam's coordinate-wise second-moment estimation provides an effective preconditioner for this heterogeneous landscape, while SGD's uniform learning rate creates fundamental mismatches.

3. **Designing and validating** architecture-aware optimizers that explicitly incorporate attention structure, achieving provable convergence guarantees tailored to Transformer geometry.

### Significance

Understanding the optimizer-architecture interaction is critical for principled neural network training. This research addresses a core topic of the Workshop on Mathematics of Modern Machine Learning—specifically, "Why does Adam optimize faster than SGD on Transformers?"—and contributes to reconciling optimization theory with deep learning practice. Success in this endeavor would:

- Reduce the computational burden of hyperparameter search in large-scale Transformer training
- Provide guidelines for optimizer selection based on architectural properties
- Enable the design of theoretically-grounded optimizers for emerging architectures
- Bridge the gap between classical optimization theory and modern deep learning

---

## 2. Methodology

### 2.1 Theoretical Framework: Attention-Induced Curvature Analysis

#### 2.1.1 Attention Mechanism Formalization

Consider a single-head attention layer with input $X \in \mathbb{R}^{n \times d}$, where $n$ is sequence length and $d$ is embedding dimension. The attention computation is:

$$A = \text{softmax}\left(\frac{XW_Q(XW_K)^\top}{\sqrt{d_k}}\right), \quad O = A \cdot XW_V \cdot W_P$$

where $W_Q, W_K \in \mathbb{R}^{d \times d_k}$ are query and key matrices, $W_V \in \mathbb{R}^{d \times d_v}$ is the value matrix, and $W_P \in \mathbb{R}^{d_v \times d}$ is the projection matrix.

#### 2.1.2 Curvature Heterogeneity Derivation

We will analyze the Hessian structure of the loss function $\mathcal{L}$ with respect to different parameter groups. For query/key parameters, the gradient involves the softmax Jacobian:

$$\frac{\partial \mathcal{L}}{\partial W_Q} = X^\top \left(\frac{\partial \mathcal{L}}{\partial A} \odot J_{\text{softmax}}\right) XW_K$$

where $J_{\text{softmax}} = \text{diag}(a) - aa^\top$ for attention weights $a$. The second-order information reveals:

$$\frac{\partial^2 \mathcal{L}}{\partial W_Q^2} \propto X^\top \left(\frac{\partial^2 \text{softmax}}{\partial z^2}\right) X$$

**Key Insight:** The softmax second derivative introduces multiplicative interactions that amplify curvature in directions corresponding to attention logits near decision boundaries (where softmax is neither saturated nor uniform). We will prove that:

$$\lambda_{\max}\left(\nabla^2_{W_Q} \mathcal{L}\right) / \lambda_{\max}\left(\nabla^2_{W_V} \mathcal{L}\right) = \Theta\left(\kappa_{\text{softmax}} \cdot \|X\|^2\right)$$

where $\kappa_{\text{softmax}}$ captures the sensitivity of softmax outputs to input perturbations.

#### 2.1.3 Block Heterogeneity Quantification

We define the **heterogeneity ratio** $\mathcal{H}$ for a Transformer as:

$$\mathcal{H} = \frac{\max_{b \in \{Q,K,V,P\}} \lambda_{\max}(H_b)}{\min_{b \in \{Q,K,V,P\}} \lambda_{\min}^+(H_b)}$$

where $H_b$ denotes the Hessian block corresponding to parameter group $b$. We will derive bounds on $\mathcal{H}$ as a function of:
- Input statistics (token embedding variance, sequence correlations)
- Architecture parameters (attention dimension $d_k$, number of heads)
- Training dynamics (attention entropy evolution during training)

### 2.2 Convergence Analysis: SGD vs. Adam under Heterogeneous Curvature

#### 2.2.1 Problem Setup

Consider minimizing $\mathcal{L}(\theta)$ where $\theta = (\theta_Q, \theta_K, \theta_V, \theta_P)$ with block-wise smoothness constants $L_b$ for each parameter group $b$. We assume:

**Assumption 1 (Block Smoothness):** $\|\nabla_b \mathcal{L}(\theta) - \nabla_b \mathcal{L}(\theta')\| \leq L_b \|\theta_b - \theta'_b\|$

**Assumption 2 (Gradient Boundedness):** $\mathbb{E}[\|\nabla \mathcal{L}(\theta)\|^2] \leq G^2$

#### 2.2.2 SGD Convergence Under Heterogeneity

For SGD with learning rate $\eta$: $\theta_{t+1} = \theta_t - \eta \nabla \mathcal{L}(\theta_t)$

The optimal learning rate is constrained by the sharpest direction:

$$\eta^* \leq \frac{2}{\max_b L_b} = \frac{2}{L_Q}$$

**Theorem 1 (SGD Convergence Rate):** Under Assumptions 1-2, SGD converges at rate:

$$\frac{1}{T}\sum_{t=1}^T \mathbb{E}[\|\nabla \mathcal{L}(\theta_t)\|^2] \leq \frac{2(\mathcal{L}(\theta_0) - \mathcal{L}^*)}{\eta T} + \eta L_{\max} \sigma^2$$

The effective convergence rate scales as $O(\mathcal{H}^{1/2} / \sqrt{T})$, degrading with heterogeneity.

#### 2.2.3 Adam's Implicit Preconditioning

Adam updates: $m_t = \beta_1 m_{t-1} + (1-\beta_1)g_t$, $v_t = \beta_2 v_{t-1} + (1-\beta_2)g_t^2$, $\theta_{t+1} = \theta_t - \alpha \frac{\hat{m}_t}{\sqrt{\hat{v}_t}+\epsilon}$

**Theorem 2 (Adam as Approximate Block Preconditioner):** Under stationary gradient statistics, Adam's update approximates:

$$\theta_{t+1} = \theta_t - \alpha D_t^{-1} \nabla \mathcal{L}(\theta_t)$$

where $D_t \approx \text{diag}(\sqrt{\mathbb{E}[g_t^2]})$ provides coordinate-wise scaling that adapts to local curvature.

**Theorem 3 (Adam Convergence Under Heterogeneity):** For the heterogeneous block model, Adam achieves:

$$\frac{1}{T}\sum_{t=1}^T \mathbb{E}[\|\nabla \mathcal{L}(\theta_t)\|^2] \leq O\left(\frac{\sqrt{\sum_b d_b / L_b}}{\sqrt{T}}\right)$$

This rate is **independent of $\mathcal{H}$** when the preconditioner correctly adapts to block curvatures.

### 2.3 Architecture-Aware Optimizer Design

Based on our analysis, we propose **Attention-Aware Adam (A³)** that explicitly incorporates attention structure:

$$v_t^{(b)} = \beta_2^{(b)} v_{t-1}^{(b)} + (1-\beta_2^{(b)}) (g_t^{(b)})^2$$

where $\beta_2^{(b)}$ is adapted based on the expected curvature of block $b$:

$$\beta_2^{(Q)} = \beta_2^{(K)} = \beta_2^{\text{base}} + \Delta\beta \cdot \mathcal{H}_{\text{est}}$$

Here, $\mathcal{H}_{\text{est}}$ is an online estimate of heterogeneity computed from gradient statistics.

### 2.4 Experimental Design

#### 2.4.1 Synthetic Experiments

**Objective:** Validate theoretical predictions in controlled settings.

**Setup:** Construct synthetic attention layers with controllable curvature ratios by varying:
- Input covariance structure
- Temperature parameter in softmax
- Dimension ratios $d_k/d$

**Metrics:**
- Empirical Hessian eigenvalue distribution
- Convergence rate vs. predicted bounds
- Correlation between $\mathcal{H}$ and SGD-Adam performance gap

#### 2.4.2 Real Transformer Experiments

**Models:** GPT-2 (124M), BERT-base (110M), ViT-B/16 (86M)

**Tasks:**
- Language modeling on WikiText-103
- GLUE benchmark for BERT
- ImageNet classification for ViT

**Optimizer Comparisons:**
- SGD with optimal tuned learning rate
- Adam with default and tuned hyperparameters
- Our proposed A³ optimizer
- Ablations: Adam without adaptivity per block

**Metrics:**
- Training loss curves and wall-clock time to target loss
- Validation accuracy/perplexity
- Gradient and Hessian statistics throughout training

#### 2.4.3 Scaling Analysis

**Objective:** Verify that theoretical insights scale to larger models.

**Setup:** Train GPT-style models at scales 125M, 350M, 1.3B parameters on the Pile dataset.

**Analysis:**
- Track $\mathcal{H}$ evolution during training
- Measure optimizer performance gap as function of scale
- Validate A³ benefits at scale

### 2.5 Evaluation Metrics

1. **Convergence Speed:** Steps and wall-clock time to reach target training loss
2. **Final Performance:** Best validation metric achieved
3. **Heterogeneity Correlation:** Spearman correlation between measured $\mathcal{H}$ and optimizer gap
4. **Theoretical Bound Tightness:** Ratio of empirical to predicted convergence rates
5. **Computational Overhead:** Additional compute cost of A³ vs. standard Adam

---

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Theoretical Contributions:**
   - Rigorous characterization of attention-induced curvature heterogeneity with explicit dependence on architecture parameters
   - Convergence theorems for SGD and Adam under block-heterogeneous smoothness, showing Adam's provable advantage scales with $\mathcal{H}$
   - Analysis framework applicable to other attention variants (linear attention, sparse attention)

2. **Algorithmic Contributions:**
   - A³ optimizer with theoretical guarantees tailored to Transformer geometry
   - Practical guidelines for setting optimizer hyperparameters based on architecture analysis
   - Diagnostic tools for measuring optimization difficulty from gradient statistics

3. **Empirical Contributions:**
   - Comprehensive benchmarking validating theoretical predictions
   - Evidence for the causal role of block heterogeneity in optimizer performance
   - Scaling analysis demonstrating practical relevance at production scales

### Impact

**Scientific Impact:** This research bridges optimization theory and deep learning practice by providing the first rigorous explanation for a widely-observed phenomenon. The framework establishes a template for architecture-aware optimization analysis applicable beyond Transformers.

**Practical Impact:** By understanding *why* Adam works, practitioners can make informed optimizer choices without exhaustive tuning. The A³ optimizer offers potential efficiency gains for large-scale training, where even small improvements translate to significant cost savings.

**Broader Impact:** As foundation models become increasingly central to AI systems, principled training methods are essential for democratizing access to large-scale model development. This research contributes to making Transformer training more predictable and accessible.

### Timeline

- **Months 1-3:** Complete theoretical analysis and derive main theorems
- **Months 4-6:** Implement A³ optimizer and conduct synthetic experiments
- **Months 7-9:** Real Transformer experiments and scaling analysis
- **Months 10-12:** Paper writing, code release, and dissemination

This research directly addresses the workshop's call for theoretical understanding that guides practice, providing both fundamental insights into Transformer optimization and practical tools for the deep learning community.