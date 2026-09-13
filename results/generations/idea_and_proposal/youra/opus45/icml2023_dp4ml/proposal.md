# Research Proposal: Sparse Dual-Potential Attention: Leveraging q-Deformed Optimal Transport for Faithful Transformer Interpretability

## 1. Introduction

### Background

Transformer architectures have revolutionized machine learning across natural language processing, computer vision, and numerous other domains. Central to their success is the self-attention mechanism, which computes weighted relationships between all pairs of tokens in a sequence. These attention weights are frequently used as post-hoc explanations for model predictions—practitioners examine which tokens the model "attends to" when making decisions. However, recent empirical studies have revealed a troubling disconnect: attention weights often fail as faithful explanations. Liu et al. (2022) demonstrated that in 30-50% of cases, masking the highest-attended tokens actually *increases* prediction confidence, directly contradicting the intuition that these tokens drive the prediction. This phenomenon, termed "faithfulness violation," undermines the trustworthiness of attention-based interpretability.

Simultaneously, duality principles—foundational concepts in optimization and mathematics—remain underexploited in modern deep learning. Optimal transport (OT) theory, in particular, offers a mathematically rigorous framework where Kantorovich dual potentials encode marginal contributions to transport costs. These dual potentials have clear optimization-theoretic interpretations: they represent the sensitivity of the optimal transport cost to perturbations in the marginal distributions. This property suggests a natural connection to gradient-based sensitivity measures used in interpretability.

Recent work has begun exploring optimal transport in attention mechanisms. Sinkformers (Sander et al., 2022) replaced softmax attention with Sinkhorn-normalized doubly-stochastic matrices, improving training stability. However, this approach suffers from "spectral collapse"—the attention matrices converge toward uniform distributions, losing expressivity. Moreover, existing OT-attention work focuses on computational efficiency rather than interpretability, leaving the potential of dual potentials for explanation entirely unexplored.

### Research Objectives

This research proposes **Sparse Dual-Potential Attention (SDPA)**, a novel attention mechanism that replaces standard softmax attention with q-deformed optimal transport using Tsallis entropy regularization. Our primary objectives are:

1. **Develop a theoretically grounded attention mechanism** where Kantorovich dual potentials serve as interpretability scores with direct optimization-theoretic meaning.

2. **Demonstrate that sparse OT attention preserves spectral expressivity** while avoiding the collapse observed in dense doubly-stochastic attention.

3. **Empirically validate that dual potentials provide more faithful explanations** than raw attention weights, integrated gradients, and attention rollout methods.

4. **Maintain competitive task performance** while achieving interpretability improvements.

### Significance

This work bridges classical duality principles from optimal transport theory with practical deep learning interpretability. By grounding attention-based explanations in optimization theory, we address a fundamental limitation of current transformer interpretability methods. The significance extends across multiple dimensions:

- **Theoretical contribution**: Establishing formal connections between Kantorovich dual potentials and gradient-based sensitivity measures in neural networks.
- **Methodological contribution**: Providing a drop-in replacement for softmax attention that yields mathematically meaningful interpretability scores.
- **Practical impact**: Enabling more trustworthy explanations for high-stakes applications in healthcare, finance, and legal domains where model interpretability is crucial.

## 2. Methodology

### 2.1 Theoretical Foundation

#### Standard Attention Mechanism

In standard transformer self-attention, given queries $Q$, keys $K$, and values $V \in \mathbb{R}^{n \times d}$, the attention output is:

$$A = \text{softmax}\left(\frac{QK^T}{\sqrt{d}}\right), \quad \text{Output} = AV$$

where the softmax is applied row-wise. The attention weights $A_{ij}$ are commonly interpreted as the importance of token $j$ for computing the representation of token $i$.

#### q-Deformed Optimal Transport Formulation

We reformulate attention as an optimal transport problem with Tsallis entropy regularization. Given cost matrix $C = -\frac{QK^T}{\sqrt{d}}$ (negative similarity as transport cost), we solve:

$$A^* = \arg\min_{A \in \Pi(\mu, \nu)} \langle C, A \rangle + \frac{1}{\lambda} H_q(A)$$

where $\Pi(\mu, \nu)$ is the set of transport plans with marginals $\mu$ and $\nu$ (typically uniform), and $H_q(A)$ is the Tsallis entropy:

$$H_q(A) = \frac{1}{q-1}\left(1 - \sum_{i,j} A_{ij}^q\right)$$

For $q < 1$, Tsallis entropy promotes **sparse** solutions, unlike Shannon entropy ($q \to 1$) which yields dense doubly-stochastic matrices.

#### Kantorovich Dual Potentials

The dual formulation of the q-deformed OT problem yields:

$$\max_{u, v} \langle u, \mu \rangle + \langle v, \nu \rangle - \frac{1}{\lambda} \Omega_q^*(u \oplus v - C)$$

where $u \in \mathbb{R}^n$ and $v \in \mathbb{R}^n$ are the dual potentials, and $\Omega_q^*$ is the convex conjugate of the Tsallis entropy. The optimal dual potentials satisfy:

$$u_i^* = \frac{\partial \text{OT}_q(C, \mu, \nu)}{\partial \mu_i}$$

This equation reveals that **dual potentials encode the marginal contribution of each source token to the optimal transport cost**—a direct measure of token importance with clear optimization-theoretic meaning.

### 2.2 Sparse Dual-Potential Attention (SDPA) Algorithm

**Algorithm 1: SDPA Forward Pass**

```
Input: Q, K, V ∈ ℝ^{n×d}, q ∈ [0.5, 0.8], λ > 0, max_iter = 30
Output: Attention output O, dual potentials u

1. Compute cost matrix: C = -QK^T / √d
2. Initialize: u = 0_n, v = 0_n
3. For t = 1 to max_iter:
   a. Update v: v_j = λ · log_q(Σ_i exp_q((u_i - C_{ij})/λ) / ν_j)
   b. Update u: u_i = λ · log_q(Σ_j exp_q((v_j - C_{ij})/λ) / μ_i)
   c. Check convergence: if ||u^{(t)} - u^{(t-1)}||_∞ < ε, break
4. Compute transport plan: A_{ij} = exp_q((u_i + v_j - C_{ij})/λ)
5. Compute output: O = AV
6. Return O, u (dual potentials as interpretability scores)
```

where $\exp_q(x) = [1 + (1-q)x]_+^{1/(1-q)}$ is the q-exponential and $\log_q(x) = (x^{1-q} - 1)/(1-q)$ is the q-logarithm.

**Gradient Computation**: For backpropagation, we use implicit differentiation through the optimality conditions, following Cuturi et al. (2019).

### 2.3 Causal Mechanism Validation

Our hypothesis posits a 4-step causal chain:

**Step 1 → Step 2 (q-OT → Sparsity)**: Tsallis entropy with $q < 1$ induces sparse attention matrices. We measure sparsity as the fraction of entries below threshold $\tau = 0.01$.

**Step 2 → Step 3 (Sparsity → Expressivity)**: Sparse matrices avoid spectral collapse. We measure effective rank:

$$\text{EffRank}(A) = \exp\left(-\sum_i \tilde{\sigma}_i \log \tilde{\sigma}_i\right)$$

where $\tilde{\sigma}_i = \sigma_i / \sum_j \sigma_j$ are normalized singular values.

**Step 3 → Step 4 (Expressivity → Dual Potentials)**: Preserved expressivity enables meaningful dual potential extraction. We verify by computing correlation between dual potentials and input gradients:

$$\rho = \text{Corr}\left(u_i, \left\|\frac{\partial \mathcal{L}}{\partial x_i}\right\|\right)$$

**Step 4 → Outcome (Dual Potentials → Faithfulness)**: Dual potentials provide faithful explanations. Measured via SaCo coefficient and faithfulness violation rate.

### 2.4 Experimental Design

#### Datasets and Models

| Domain | Model | Dataset | Task |
|--------|-------|---------|------|
| NLP | BERT-base | SST-2 | Sentiment Classification |
| Vision | ViT-B/16 | ImageNet-1K | Image Classification |

#### Baselines

1. **Raw Attention**: Standard softmax attention weights
2. **Sinkhorn Attention**: Dense doubly-stochastic attention ($q = 1$)
3. **Integrated Gradients**: Gradient-based attribution method
4. **Attention Rollout**: Aggregated attention across layers

#### Evaluation Metrics

**Primary Metrics (Faithfulness)**:

1. **SaCo Coefficient** (Wu et al., 2024): Measures consistency between explanation rankings and model behavior under perturbation.

$$\text{SaCo} = \frac{1}{N}\sum_{i=1}^N \text{Corr}(\text{rank}(e_i), \text{rank}(\Delta f_i))$$

where $e_i$ is the explanation score for token $i$ and $\Delta f_i$ is the change in model output when token $i$ is masked.

2. **Faithfulness Violation Rate** (Liu et al., 2022): Percentage of samples where masking top-attended tokens increases prediction confidence.

$$\text{FVR} = \frac{1}{N}\sum_{i=1}^N \mathbb{1}[f(x_{\text{masked}}) > f(x)]$$

**Secondary Metrics**:

3. **Effective Rank**: Spectral expressivity measure (target: > 0.5n)
4. **Task Accuracy**: Classification accuracy (target: within 2% of baseline)
5. **Computational Overhead**: Wall-clock time ratio vs. softmax attention

#### Hyperparameter Configuration

| Parameter | Values | Selection Method |
|-----------|--------|------------------|
| q (Tsallis parameter) | {0.5, 0.6, 0.7, 0.8} | Grid search on validation set |
| λ (regularization) | {0.1, 0.5, 1.0} | Grid search |
| max_iter | 30 | Fixed (with early stopping) |
| Layers with SDPA | Final 3 layers | Fixed |

#### Statistical Analysis

- **Sample size**: 1000 test samples per dataset
- **Random seeds**: 5 seeds (42, 123, 456, 789, 1000)
- **Statistical tests**: Paired t-test with Bonferroni correction
- **Significance level**: α = 0.05
- **Effect size**: Cohen's d with 95% confidence intervals

### 2.5 Ablation Studies

1. **q-value ablation**: Vary q from 0.3 to 1.0 to validate the [0.5, 0.8] range
2. **Layer selection**: Compare applying SDPA to all layers vs. final layers only
3. **Marginal constraints**: Compare uniform vs. learned marginals
4. **Dual potential aggregation**: For multi-head attention, compare averaging, max-pooling, and learned weighting

### 2.6 Implementation Details

- **Framework**: PyTorch with custom CUDA kernels for q-exponential operations
- **OT Solver**: Modified POT library with Tsallis entropy support
- **Hardware**: 4× NVIDIA A100 GPUs
- **Training**: Fine-tune pre-trained models with SDPA replacement for 3 epochs
- **Reproducibility**: All code and checkpoints will be released

## 3. Expected Outcomes & Impact

### Expected Results

Based on our theoretical analysis and preliminary evidence from related work, we anticipate the following outcomes:

**Primary Outcome (Faithfulness Improvement)**:
- SaCo coefficient improvement: SDPA expected to achieve 0.65-0.75 vs. 0.50-0.55 for raw attention (>15% absolute improvement)
- Faithfulness violation rate reduction: SDPA expected to achieve 15-25% vs. 35-45% for raw attention (>40% relative reduction)

**Secondary Outcomes**:
- Effective rank preservation: SDPA with q ∈ [0.5, 0.8] expected to maintain effective rank > 0.6n, compared to < 0.3n for Sinkhorn attention
- Task accuracy: Expected degradation < 1.5% on both SST-2 and ImageNet
- Computational overhead: Expected 2-3× increase in attention computation time

**Mechanism Validation**:
- Strong correlation (ρ > 0.7) expected between dual potentials and input gradients
- Sparsity level of 60-80% expected for q ∈ [0.5, 0.8]

### Potential Challenges and Mitigations

1. **Convergence issues**: If q-OT fails to converge, we will implement warm-starting from previous layer's solution and adaptive λ scheduling.

2. **Performance degradation**: If accuracy drops exceed 2%, we will explore hybrid architectures with SDPA only in final layers.

3. **Computational overhead**: If overhead exceeds 3×, we will implement approximate solvers with theoretical guarantees.

### Broader Impact

**Scientific Impact**:
This work demonstrates that classical duality principles remain highly relevant for modern deep learning. By showing that Kantorovich dual potentials provide superior interpretability scores, we open new research directions at the intersection of optimal transport theory and neural network explanation methods.

**Practical Impact**:
Faithful model explanations are critical for deploying AI systems in high-stakes domains. SDPA provides practitioners with mathematically grounded explanations that more accurately reflect model behavior, enabling better debugging, auditing, and trust calibration.

**Limitations and Ethical Considerations**:
- Computational overhead may limit applicability in resource-constrained settings
- Improved interpretability does not guarantee model correctness—faithful explanations of flawed models may create false confidence
- We will clearly document failure modes and appropriate use cases

### Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| Phase 1 | Months 1-2 | Implementation of SDPA, integration with BERT and ViT |
| Phase 2 | Months 3-4 | Primary experiments on SST-2 and ImageNet |
| Phase 3 | Month 5 | Ablation studies and mechanism validation |
| Phase 4 | Month 6 | Analysis, paper writing, code release |

### Conclusion

This proposal presents Sparse Dual-Potential Attention, a principled approach to transformer interpretability grounded in optimal transport duality. By replacing heuristic attention weights with mathematically meaningful dual potentials, we address fundamental faithfulness limitations in current explanation methods. Our comprehensive experimental design will rigorously test the hypothesis that optimization-theoretic sensitivity measures outperform raw attention for model interpretation, while validating the underlying causal mechanism. Success in this research will demonstrate the continued relevance of classical duality principles for modern deep learning challenges.