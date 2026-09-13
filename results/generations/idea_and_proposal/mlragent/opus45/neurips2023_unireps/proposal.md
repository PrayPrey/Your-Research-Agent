# Research Proposal: Learning Dynamics-Guided Model Merging via Representation Trajectory Alignment

## 1. Introduction

### Background

The convergence of neural representations across distinct learning systems—whether biological or artificial—has emerged as one of the most fascinating phenomena in modern machine learning and neuroscience. Research has consistently demonstrated that neural networks trained independently on similar data distributions often develop remarkably similar internal representations, suggesting underlying universal principles governing representation learning. This observation has profound implications for both our theoretical understanding of learning systems and practical applications in model combination and knowledge transfer.

Model merging has gained significant attention as a technique to combine the capabilities of multiple trained models without expensive retraining. Applications range from federated learning, where models trained on distributed private data must be combined, to multi-task learning scenarios where specialist models are merged into unified systems. Current approaches to model merging primarily operate on final model weights through techniques such as weight averaging, task arithmetic, and Fisher-weighted averaging. However, these methods frequently encounter a fundamental limitation: they assume that models occupying similar regions in weight space will produce compatible merged models, an assumption that often fails when models have undergone divergent learning trajectories.

Recent theoretical work by van Rossem and Saxe (2024) has revealed universal patterns in representation learning dynamics, demonstrating that different architectures develop similar representations under specific conditions. This finding suggests that understanding *when* and *how* representations align during training—not just at convergence—could provide crucial insights for model merging. The challenge of divergent learning trajectories, identified as a key obstacle in the literature, motivates our investigation into the temporal dynamics of representation formation.

### Research Objectives

This proposal introduces **Trajectory-Aligned Model Merging (TAMM)**, a novel framework that fundamentally reconceptualizes model merging by incorporating the temporal evolution of representations. Our primary objectives are:

1. To develop a systematic methodology for capturing and analyzing representation trajectories during neural network training
2. To identify "synchronization windows"—temporal phases where models develop maximally compatible representations
3. To design dynamics-informed merging algorithms that leverage trajectory alignment for superior merged model performance
4. To establish theoretical connections between representation dynamics and linear mode connectivity
5. To provide practical guidelines for determining merge compatibility between models

### Significance

This research addresses critical gaps at the intersection of representation learning theory and practical model combination. By bridging insights from learning dynamics analysis with model merging techniques, TAMM offers both theoretical contributions—advancing our understanding of representation universality—and practical benefits—enabling more effective model merging in federated learning, multi-task scenarios, and efficient fine-tuning strategies. The cross-disciplinary nature of this work aligns with the broader goal of unifying perspectives from machine learning, neuroscience, and cognitive science on neural representation similarity.

## 2. Methodology

### 2.1 Representation Trajectory Logging

The foundation of TAMM is the systematic capture of representation evolution during training. For a neural network with $L$ layers, we define the representation trajectory as:

$$\mathcal{T}^{(l)} = \{R^{(l)}_{t_1}, R^{(l)}_{t_2}, ..., R^{(l)}_{t_K}\}$$

where $R^{(l)}_{t_k} \in \mathbb{R}^{n \times d_l}$ represents the activations at layer $l$ for a fixed probe dataset of $n$ samples at training checkpoint $t_k$, and $d_l$ is the hidden dimension of layer $l$.

**Checkpoint Strategy**: We employ logarithmically-spaced checkpoints during training to capture both rapid early-stage changes and gradual late-stage refinements:

$$t_k = T \cdot \left(\frac{k}{K}\right)^\alpha$$

where $T$ is total training steps, $K$ is the number of checkpoints (typically 50-100), and $\alpha > 1$ concentrates checkpoints in later training phases.

**Memory-Efficient Storage**: Rather than storing full activation matrices, we compute and store compressed representation summaries using random projection:

$$\tilde{R}^{(l)}_{t_k} = R^{(l)}_{t_k} \cdot P^{(l)}$$

where $P^{(l)} \in \mathbb{R}^{d_l \times m}$ is a random Gaussian projection matrix with $m \ll d_l$.

### 2.2 Trajectory Alignment Analysis

Given two models $A$ and $B$ with representation trajectories $\mathcal{T}_A$ and $\mathcal{T}_B$, we compute time-resolved similarity matrices to identify synchronization patterns.

**Centered Kernel Alignment (CKA)**: For representations $R_A$ and $R_B$, we compute:

$$\text{CKA}(R_A, R_B) = \frac{\text{HSIC}(K_A, K_B)}{\sqrt{\text{HSIC}(K_A, K_A) \cdot \text{HSIC}(K_B, K_B)}}$$

where $K_A = R_A R_A^T$ and $K_B = R_B R_B^T$ are kernel matrices, and HSIC denotes the Hilbert-Schmidt Independence Criterion:

$$\text{HSIC}(K_A, K_B) = \frac{1}{(n-1)^2} \text{tr}(K_A H K_B H)$$

with $H = I - \frac{1}{n}\mathbf{1}\mathbf{1}^T$ being the centering matrix.

**Trajectory Similarity Matrix**: We construct a layer-wise trajectory similarity matrix:

$$S^{(l)}_{ij} = \text{CKA}(R^{(l)}_{A,t_i}, R^{(l)}_{B,t_j})$$

This matrix reveals temporal alignment patterns, where diagonal dominance indicates synchronized development and off-diagonal peaks suggest phase shifts in representation evolution.

**Synchronization Window Detection**: We identify synchronization windows by analyzing the trajectory similarity matrix. A synchronization window $[t_a, t_b]$ is defined where:

$$\bar{S}^{(l)}_{[t_a, t_b]} = \frac{1}{|W|} \sum_{t_i, t_j \in [t_a, t_b]} S^{(l)}_{ij} > \tau$$

where $\tau$ is a threshold determined through validation. We additionally compute a synchronization score:

$$\Psi(t) = \frac{1}{L} \sum_{l=1}^{L} S^{(l)}_{tt}$$

measuring instantaneous cross-model alignment at time $t$.

### 2.3 Dynamics-Informed Merging Algorithms

Based on trajectory analysis, we propose three complementary merging strategies:

**Strategy 1: Synchronization Point Merging (SPM)**

Rather than merging final weights, we identify optimal merge points where $\Psi(t^*)$ is maximized:

$$t^* = \arg\max_t \Psi(t) \cdot \phi(t)$$

where $\phi(t)$ is a task performance weighting function ensuring merged models retain adequate capability. The merged model weights at optimal point are:

$$\theta^*_{\text{merged}} = \lambda \theta^A_{t^*} + (1-\lambda) \theta^B_{t^*}$$

with $\lambda$ determined by relative model performance.

**Strategy 2: Trajectory-Guided Transformation Merging (TGTM)**

When synchronization is imperfect, we learn transformations that align representation trajectories. For each layer $l$, we compute an optimal affine transformation:

$$W^{(l)}_{\text{align}} = \arg\min_W \sum_{k=1}^{K} \|R^{(l)}_{A,t_k} - R^{(l)}_{B,t_k} W\|_F^2 + \lambda_{\text{reg}} \|W - I\|_F^2$$

The closed-form solution is:

$$W^{(l)}_{\text{align}} = \left(\sum_k (R^{(l)}_{B,t_k})^T R^{(l)}_{B,t_k} + \lambda_{\text{reg}} I\right)^{-1} \left(\sum_k (R^{(l)}_{B,t_k})^T R^{(l)}_{A,t_k} + \lambda_{\text{reg}} I\right)$$

**Strategy 3: Curvature-Aware Weight Interpolation (CAWI)**

We incorporate information about the curvature of representation evolution into weight interpolation:

$$\theta_{\text{merged}} = \sum_{i \in \{A,B\}} w_i(t) \cdot \theta^i_{t}$$

where the time-varying weights are:

$$w_A(t) = \frac{\exp(-\beta \cdot C_A(t))}{\exp(-\beta \cdot C_A(t)) + \exp(-\beta \cdot C_B(t))}$$

and $C_i(t) = \|\ddot{\mathcal{T}}_i(t)\|$ measures trajectory curvature (rapid representation change), with models in stable phases receiving higher weight.

### 2.4 Experimental Design

**Datasets and Tasks**:
- **Vision**: CIFAR-100 (coarse/fine label splits), ImageNet subsets for multi-domain merging
- **Language**: GLUE benchmark subsets for multi-task NLP merging
- **Federated Learning Simulation**: Non-IID partitions of CIFAR-10 across simulated clients

**Model Architectures**:
- ResNet-18/50 and Vision Transformers (ViT-B/16) for vision tasks
- BERT-base and RoBERTa for language tasks

**Baselines**:
- Weight averaging
- Fisher-weighted averaging (AlignMerge-style)
- Task arithmetic
- TIES-Merging
- MAGIC magnitude calibration

**Evaluation Metrics**:
1. **Task Performance Retention**: $\text{TPR} = \frac{\text{Acc}_{\text{merged}}}{\max(\text{Acc}_A, \text{Acc}_B)}$
2. **Multi-task Performance**: Average accuracy across all source tasks
3. **Negative Transfer Measurement**: Performance degradation on individual tasks
4. **Representation Quality**: CKA similarity between merged model and source models
5. **Computational Overhead**: Storage and computation costs relative to baselines

**Ablation Studies**:
- Impact of checkpoint frequency $K$
- Sensitivity to synchronization threshold $\tau$
- Comparison of similarity metrics (CKA vs. SVCCA vs. Procrustes)
- Effect of training hyperparameter divergence on trajectory alignment

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Empirical Results**: We anticipate TAMM will achieve 5-15% improvement in merged model performance compared to weight averaging baselines, with particularly strong gains in scenarios with divergent training dynamics. The synchronization point analysis is expected to reveal consistent patterns across architectures, identifying optimal merge windows typically occurring at 60-80% of training.

**Theoretical Insights**: This research will establish formal connections between:
- Representation trajectory alignment and linear mode connectivity
- Synchronization window characteristics and loss landscape geometry
- Trajectory curvature and model merge compatibility

**Practical Guidelines**: We will deliver:
- A merge compatibility score predicting merging success from early trajectory analysis
- Recommendations for training procedures that enhance merge compatibility
- Open-source toolkit for trajectory logging and TAMM implementation

### Broader Impact

**Scientific Contributions**: TAMM advances our understanding of representation universality by characterizing *when* similarities emerge during learning, bridging theoretical insights from neuroscience (learning dynamics) with practical ML applications. This contributes to the workshop's core question of why and how similar representations arise across neural models.

**Practical Applications**: The framework enables more effective model combination in:
- Federated learning with heterogeneous client training
- Continual learning through trajectory-aware model updates
- Efficient multi-task model deployment

**Cross-Disciplinary Implications**: By analyzing representation trajectories, TAMM provides a methodology applicable to studying biological neural systems, potentially enabling comparison of developmental trajectories across species or individuals, thereby fostering collaboration between ML and neuroscience communities.