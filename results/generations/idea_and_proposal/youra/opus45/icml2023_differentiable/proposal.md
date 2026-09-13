# Research Proposal: Unified Differentiable Discrete Operations via Learnable Optimal Transport

## 1. Introduction

### 1.1 Background

Gradient-based optimization forms the backbone of modern deep learning, enabling efficient parameter updates through backpropagation. However, many real-world applications require discrete operations—categorical selection, sorting, ranking, and top-k extraction—that fundamentally break gradient flow. These operations produce zero or undefined gradients almost everywhere, creating a critical barrier for end-to-end differentiable learning.

The machine learning community has developed numerous operation-specific relaxations to address this challenge. Gumbel-Softmax (Jang et al., 2016; Maddison et al., 2016) provides differentiable categorical sampling through temperature-controlled continuous relaxation. Sinkhorn-based methods (Mena et al., 2018; Cuturi, 2013) enable differentiable sorting and permutation learning by relaxing permutation matrices to doubly-stochastic matrices. Differentiable top-k operators (Xie et al., 2020; Cordonnier et al., 2021) extend selection mechanisms to variable-size subsets. While individually successful, these approaches create a fragmented landscape where practitioners must manually select, implement, and tune separate mechanisms for each discrete operation.

This fragmentation poses significant practical and theoretical challenges. First, models requiring multiple discrete operations demand careful orchestration of incompatible relaxation schemes. Second, the optimal choice of discrete operation may itself be task-dependent and learnable, yet current frameworks provide no mechanism for automatic operation selection. Third, the lack of a unified theoretical foundation obscures the relationships between these operations and prevents principled extensions to novel discrete computations.

### 1.2 Research Objectives

This research proposes **OT-UNI** (Optimal Transport Unified), a novel framework that unifies categorical selection, sorting, and top-k operations within a single differentiable layer based on optimal transport theory. Our central hypothesis posits that these seemingly disparate discrete operations are special cases of optimal transport problems with different cost matrix structures, and that a learnable parameterization of these structures enables both operation recovery and automatic operation-type selection.

Specifically, we aim to:

1. **Demonstrate theoretical unification**: Prove that categorical selection, sorting, and top-k operations emerge as special cases of entropic optimal transport with structured cost matrices.

2. **Develop a unified differentiable layer**: Implement OT-UNI with learnable cost matrix parameterization $C(\theta)$ that recovers baseline operation behaviors while enabling gradient flow.

3. **Enable automatic operation selection**: Introduce Gumbel reparameterization over operation-type embeddings, allowing end-to-end learning of which discrete operation to apply.

4. **Validate empirically**: Demonstrate that OT-UNI achieves comparable performance to specialized implementations across diverse tasks while providing the flexibility of operation adaptation.

### 1.3 Significance

This research addresses a fundamental gap in differentiable computing by providing a principled, unified approach to discrete operations. Success would yield several significant contributions:

- **Simplified implementation**: A single layer replacing multiple operation-specific modules reduces engineering complexity and potential for implementation errors.
- **Automatic operation discovery**: Learnable operation types enable models to discover task-optimal discrete computations without manual specification.
- **Theoretical insight**: The optimal transport perspective reveals deep connections between discrete operations, potentially inspiring novel hybrid operations.
- **Broader applicability**: A unified framework facilitates extension to new discrete operations through cost matrix design rather than bespoke relaxation schemes.

## 2. Methodology

### 2.1 Theoretical Foundation

#### 2.1.1 Optimal Transport Formulation

We formulate discrete operations as optimal transport problems. Given input scores $\mathbf{s} \in \mathbb{R}^n$ and a cost matrix $C \in \mathbb{R}^{n \times n}$, the discrete optimal transport problem seeks a coupling matrix $P^* \in \{0,1\}^{n \times n}$ minimizing:

$$P^* = \arg\min_{P \in \Pi(\mathbf{a}, \mathbf{b})} \langle C, P \rangle$$

where $\Pi(\mathbf{a}, \mathbf{b}) = \{P \geq 0 : P\mathbf{1} = \mathbf{a}, P^\top\mathbf{1} = \mathbf{b}\}$ denotes the transportation polytope with marginals $\mathbf{a}, \mathbf{b} \in \Delta^{n-1}$.

#### 2.1.2 Operation-Specific Cost Structures

We establish that standard discrete operations correspond to specific cost matrix structures:

**Categorical Selection (Softmax/Argmax)**: Setting $C_{ij} = -s_i \cdot \mathbf{1}[i=j]$ (diagonal cost proportional to negative scores) with uniform marginals yields:

$$P^*_{ii} \propto \exp(s_i / \varepsilon)$$

recovering the softmax distribution as $\varepsilon \to 0$.

**Sorting/Permutation**: Setting $C_{ij} = -s_i \cdot r_j$ where $r_j = j/n$ represents target rank positions, with uniform marginals on both sides, yields the permutation matrix that sorts elements by score.

**Top-k Selection**: Setting $C_{ij}$ with block-sparse structure where only the first $k$ columns have finite costs, combined with marginal constraints $\mathbf{b} = [\mathbf{1}_k/k, \mathbf{0}_{n-k}]$, selects the top-k elements.

#### 2.1.3 Entropic Regularization for Differentiability

To enable gradient flow, we introduce entropic regularization:

$$P^*_\varepsilon = \arg\min_{P \in \Pi(\mathbf{a}, \mathbf{b})} \langle C, P \rangle - \varepsilon H(P)$$

where $H(P) = -\sum_{ij} P_{ij} \log P_{ij}$ is the entropy. This admits the closed-form solution via the Sinkhorn algorithm.

### 2.2 OT-UNI Architecture

#### 2.2.1 Learnable Cost Matrix Parameterization

We parameterize the cost matrix as a function of learnable parameters $\theta$:

$$C(\theta) = \alpha_{\text{diag}}(\theta) \cdot C_{\text{diag}}(\mathbf{s}) + \alpha_{\text{sort}}(\theta) \cdot C_{\text{sort}}(\mathbf{s}) + \alpha_{\text{topk}}(\theta) \cdot C_{\text{topk}}(\mathbf{s}, k)$$

where:
- $C_{\text{diag}}(\mathbf{s})_{ij} = -s_i \cdot \mathbf{1}[i=j]$
- $C_{\text{sort}}(\mathbf{s})_{ij} = -s_i \cdot (j/n)$
- $C_{\text{topk}}(\mathbf{s}, k)_{ij} = -s_i \cdot \mathbf{1}[j \leq k] + M \cdot \mathbf{1}[j > k]$ (with large $M$)

The mixing coefficients $\alpha(\theta) = \text{softmax}(W_\alpha \theta + b_\alpha)$ are derived from an operation embedding $\theta \in \mathbb{R}^d$.

#### 2.2.2 Adaptive Marginal Constraints

Marginals are also parameterized:

$$\mathbf{a}(\theta) = \text{softmax}(W_a \theta), \quad \mathbf{b}(\theta) = \text{softmax}(W_b \theta)$$

This allows the layer to learn appropriate constraint structures for each operation type.

#### 2.2.3 Sinkhorn Layer with Learnable Regularization

The Sinkhorn algorithm iteratively normalizes rows and columns:

$$P^{(t+1)} = \text{diag}(\mathbf{u}^{(t+1)}) K \text{diag}(\mathbf{v}^{(t+1)})$$

where $K = \exp(-C(\theta)/\varepsilon(\theta))$, and:

$$\mathbf{u}^{(t+1)} = \mathbf{a} \oslash (K\mathbf{v}^{(t)}), \quad \mathbf{v}^{(t+1)} = \mathbf{b} \oslash (K^\top\mathbf{u}^{(t+1)})$$

The regularization strength $\varepsilon(\theta) = \sigma(w_\varepsilon^\top \theta + b_\varepsilon) \cdot (\varepsilon_{\max} - \varepsilon_{\min}) + \varepsilon_{\min}$ is also learned, bounded in $[\varepsilon_{\min}, \varepsilon_{\max}] = [0.01, 1.0]$.

#### 2.2.4 Gumbel Reparameterization for Operation Selection

To enable gradient flow through discrete operation-type selection, we apply Gumbel-Softmax to the mixing coefficients:

$$\tilde{\alpha}_i = \frac{\exp((\log \alpha_i + g_i)/\tau)}{\sum_j \exp((\log \alpha_j + g_j)/\tau)}$$

where $g_i \sim \text{Gumbel}(0,1)$ and $\tau$ is an annealing temperature.

### 2.3 Training Procedure

#### 2.3.1 Loss Function

The total loss combines task-specific loss with regularization:

$$\mathcal{L} = \mathcal{L}_{\text{task}}(P^*_\varepsilon, y) + \lambda_{\text{entropy}} H(\alpha) + \lambda_{\text{sparse}} \|\theta\|_1$$

The entropy term encourages exploration of operation types during early training, while sparsity promotes convergence to specific operations.

#### 2.3.2 Temperature Annealing

We employ a cosine annealing schedule for the Gumbel temperature:

$$\tau(t) = \tau_{\min} + \frac{1}{2}(\tau_{\max} - \tau_{\min})(1 + \cos(\pi t / T))$$

with $\tau_{\max} = 1.0$, $\tau_{\min} = 0.1$, over $T$ training steps.

### 2.4 Experimental Design

#### 2.4.1 Datasets and Tasks

We evaluate OT-UNI across three experimental settings:

**Experiment 1: Operation Recovery (Synthetic)**
- Generate random input scores $\mathbf{s} \sim \mathcal{N}(0, I_n)$ for $n \in \{10, 100, 1024\}$
- Target outputs from ground-truth discrete operations
- Measure L2 distance between OT-UNI output and baseline implementations

**Experiment 2: Learning-to-Rank (MSLR-WEB30K)**
- Standard learning-to-rank benchmark with 30,000 queries
- Compare OT-UNI sorting against NeuralSort and SoftSort
- Metrics: NDCG@5, NDCG@10, MAP

**Experiment 3: Set Prediction (CLEVR-Sets)**
- Predict variable-size sets of objects from images
- Compare OT-UNI top-k against differentiable top-k baselines
- Metrics: Set accuracy, F1 score

**Experiment 4: Multi-Operation Learning (Synthetic Multi-Task)**
- Tasks requiring different operations within the same model
- Evaluate whether OT-UNI learns appropriate operation types
- Metrics: Operation clustering purity, task accuracy

#### 2.4.2 Baselines

- **Gumbel-Softmax**: For categorical selection (Jang et al., 2016)
- **Gumbel-Sinkhorn**: For sorting/permutation (Mena et al., 2018)
- **NeuralSort**: For differentiable sorting (Grover et al., 2019)
- **SoftSort**: For continuous sorting relaxation (Prillo & Eisenschlos, 2020)
- **Differentiable Top-k**: For subset selection (Xie et al., 2020)

#### 2.4.3 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| L2 Recovery Error | $\|P_{\text{OT-UNI}} - P_{\text{baseline}}\|_2$ | < 0.01 |
| Gradient SNR | $\|\mathbb{E}[\nabla]\| / \text{std}(\nabla)$ | ≥ 0.5× baseline |
| Sinkhorn Convergence | Proportion of runs without divergence | > 90% |
| Operation Purity | k-means clustering accuracy on $\theta$ | > 0.8 |
| Task Performance | NDCG, accuracy, F1 as appropriate | Within 5% of baselines |

#### 2.4.4 Statistical Analysis

All experiments use $n \geq 20$ independent runs with different random seeds. We report mean ± standard deviation and conduct:
- One-sample t-tests for recovery error (H0: mean ≥ 0.01)
- Paired t-tests for gradient SNR comparison
- Proportion tests for convergence rates
- Bootstrap confidence intervals for task metrics

#### 2.4.5 Ablation Studies

1. **Cost structure ablation**: Remove individual cost components to verify necessity
2. **Learnable vs. fixed $\varepsilon$**: Compare adaptive regularization against fixed values
3. **Sinkhorn iterations**: Vary $K \in \{10, 20, 50\}$ to assess convergence-accuracy tradeoff
4. **Embedding dimension**: Test $d \in \{16, 32, 64\}$ for operation embeddings

#### 2.4.6 Implementation Details

- Framework: PyTorch with custom autograd for Sinkhorn
- Hardware: NVIDIA A100 GPUs
- Optimization: Adam with learning rate $10^{-3}$, batch size 64
- Sinkhorn iterations: $K = 20$ (default)
- Estimated compute: 50-100 GPU-hours total

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1 - Unification Validation)**: We expect OT-UNI to recover baseline operation behaviors with L2 error < 0.01 across all three operation types. This validates our theoretical claim that optimal transport provides a universal framework for discrete operations.

**Secondary Outcome (P2 - Learnable Operations)**: We anticipate that operation embeddings $\theta$ will form distinct clusters corresponding to operation types when trained on multi-task objectives, achieving clustering purity > 0.8. This demonstrates that operation selection can be learned end-to-end.

**Tertiary Outcome (P3 - Competitive Performance)**: We expect OT-UNI to achieve task performance within 5% of specialized baselines on learning-to-rank and set prediction tasks, with gradient SNR at least 0.5× that of baselines.

### 3.2 Potential Challenges and Mitigations

**Challenge 1: Sinkhorn Instability**
- Risk: Divergence with extreme cost matrices or small $\varepsilon$
- Mitigation: Log-domain Sinkhorn, gradient clipping, $\varepsilon$ lower bound

**Challenge 2: Gradient Variance**
- Risk: High variance through Gumbel reparameterization
- Mitigation: Variance reduction via control variates, careful temperature annealing

**Challenge 3: Scalability**
- Risk: $O(n^2)$ complexity limits large-scale applications
- Mitigation: Sparse Sinkhorn approximations, low-rank cost matrices

### 3.3 Broader Impact

**Scientific Impact**: This work establishes optimal transport as a unifying principle for differentiable discrete computation, opening new theoretical directions for understanding and extending relaxation methods.

**Practical Impact**: OT-UNI simplifies the implementation of models requiring discrete operations, reducing engineering overhead and enabling automatic operation adaptation. This is particularly valuable for neural architecture search, combinatorial optimization, and structured prediction.

**Future Directions**: Success would motivate extensions to graph algorithms (shortest paths, matching), logical operations, and dynamic programming, potentially through hierarchical cost matrix structures.

### 3.4 Falsification Criteria

We commit to rejecting the hypothesis if:
1. L2 recovery error exceeds 0.1 for any operation type
2. Sinkhorn diverges in more than 10% of training iterations
3. Gradient SNR falls below 0.1 (10× worse than baselines)
4. Operation embedding clustering purity falls below 0.5

These criteria ensure scientific rigor and prevent overfitting conclusions to favorable results.