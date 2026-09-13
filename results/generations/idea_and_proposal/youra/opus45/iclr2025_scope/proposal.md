# Research Proposal: DT-CaPEFT: Dual-Timescale Context-Aware Parameter-Efficient Fine-Tuning for Continual Learning

## 1. Introduction

### 1.1 Background

Foundation models have revolutionized artificial intelligence, demonstrating remarkable capabilities across vision, language, and multimodal domains. However, deploying these models in real-world scenarios presents significant challenges, particularly when models must continuously adapt to new tasks while maintaining efficiency. The field of continual learning addresses the challenge of sequential task acquisition without catastrophic forgetting, while parameter-efficient fine-tuning (PEFT) methods such as LoRA enable adaptation with minimal parameter overhead. Despite substantial progress in both areas, a critical gap remains: existing PEFT methods employ fixed-capacity adapters regardless of input complexity, leading to systematic inefficiency.

Current approaches like LoRA, AdaLoRA, and their continual learning variants (C-LoRA, CL-LoRA) allocate uniform adapter capacity across all inputs. This one-size-fits-all strategy creates a fundamental tension: simple inputs that could be processed with minimal parameters are over-provisioned, while complex inputs requiring high-capacity representations may be under-served. Empirical observations from recent work on attention mechanisms reveal that input complexity—measurable through attention entropy—varies dramatically across samples. High-entropy attention patterns indicate complex, distributed information requiring parallel encoding, while low-entropy patterns suggest focused, simple processing needs.

This observation draws inspiration from biological memory systems, particularly the complementary learning systems theory describing hippocampus-neocortex interactions. The hippocampus rapidly encodes new experiences with high capacity, while the neocortex gradually consolidates knowledge into efficient, generalizable representations. This dual-timescale architecture enables biological systems to balance plasticity (learning new information) with stability (retaining old knowledge) while optimizing resource utilization.

### 1.2 Research Objectives

This research proposes **DT-CaPEFT (Dual-Timescale Context-Aware Parameter-Efficient Fine-Tuning)**, a novel framework that dynamically allocates adapter capacity based on input complexity while enabling knowledge consolidation across timescales. Our primary objectives are:

1. **Develop a complexity-aware routing mechanism** that uses attention entropy to dynamically gate between low-rank (fast) and high-rank (slow) adapters, enabling proportional capacity allocation.

2. **Design a dual-timescale consolidation strategy** that transfers knowledge from high-capacity slow adapters to efficient fast adapters via exponential moving average (EMA) updates, mimicking hippocampal-neocortical consolidation.

3. **Validate the hypothesis** that context complexity determines optimal adapter capacity, with simple inputs achieving 95%+ performance using only 12.5% of parameters while complex inputs benefit from full capacity.

4. **Demonstrate practical efficiency gains** of 40-60% parameter reduction on simple contexts while maintaining continual learning performance with less than 5% computational overhead.

### 1.3 Significance

This research addresses multiple critical challenges identified in the workshop's scope:

- **Efficient Fine-Tuning for Continual Adaptation**: DT-CaPEFT enables models to continuously learn from new data streams while dynamically adjusting computational resources.
- **Task-Specific Adaptive Foundation Models**: The complexity-aware routing naturally adapts to task-specific requirements without manual intervention.
- **Model Optimization for Latency and Throughput Efficient Inference**: By reducing active parameters on simple inputs, DT-CaPEFT improves inference efficiency.
- **Adaptive Routing with Mixture of Experts**: The soft-gated dual-adapter architecture represents a principled approach to learned routing policies.

The proposed method bridges the gap between adaptive capacity allocation and continual learning, offering both theoretical insights into complexity-aware adaptation and practical benefits for deploying foundation models in resource-constrained, continuously evolving environments.

## 2. Methodology

### 2.1 Problem Formulation

Consider a foundation model $f_\theta$ with frozen parameters $\theta$ and trainable adapter parameters $\phi$. In continual learning, the model encounters a sequence of tasks $\mathcal{T} = \{T_1, T_2, ..., T_n\}$. For each input $x$, we seek to compute the output as:

$$y = f_\theta(x) + \Delta f_\phi(x)$$

where $\Delta f_\phi$ represents the adapter contribution. Traditional PEFT methods use fixed-rank adapters, while DT-CaPEFT dynamically allocates capacity based on input complexity.

### 2.2 Architecture Overview

DT-CaPEFT consists of three core components operating in sequence:

**Component 1: Complexity Estimation Module**
**Component 2: Soft-Gated Dual-Adapter Routing**
**Component 3: EMA-Based Knowledge Consolidation**

#### 2.2.1 Complexity Estimation via Attention Entropy

For an input sequence $x$ processed through the transformer's attention mechanism, we compute the attention entropy as a complexity signal. Given attention weights $A \in \mathbb{R}^{H \times L \times L}$ where $H$ is the number of heads and $L$ is sequence length, the entropy for head $h$ at position $i$ is:

$$H_h^{(i)} = -\sum_{j=1}^{L} A_{h,i,j} \log(A_{h,i,j} + \epsilon)$$

The aggregate complexity score is computed as:

$$\alpha_{complexity} = \frac{1}{H \cdot L} \sum_{h=1}^{H} \sum_{i=1}^{L} H_h^{(i)}$$

This complexity score is normalized to the range $[0, 1]$ using running statistics maintained during training.

#### 2.2.2 Soft-Gated Dual-Adapter Architecture

We maintain two parallel adapter modules:
- **Fast Adapter** $\phi_{fast}$: Low-rank adapter with $r_{fast} = 4$
- **Slow Adapter** $\phi_{slow}$: High-rank adapter with $r_{slow} = 32$

Each adapter follows the LoRA formulation:

$$\Delta W_{fast} = B_{fast} A_{fast}, \quad B_{fast} \in \mathbb{R}^{d \times r_{fast}}, A_{fast} \in \mathbb{R}^{r_{fast} \times d}$$

$$\Delta W_{slow} = B_{slow} A_{slow}, \quad B_{slow} \in \mathbb{R}^{d \times r_{slow}}, A_{slow} \in \mathbb{R}^{r_{slow} \times d}$$

The gating mechanism computes a soft routing coefficient:

$$\alpha_{gate} = \sigma\left(\frac{W_{gate} \cdot \alpha_{complexity} + b_{gate}}{\tau}\right)$$

where $W_{gate}$ and $b_{gate}$ are learnable parameters, $\tau$ is the temperature controlling routing sharpness, and $\sigma$ is the sigmoid function.

The final adapter output combines both pathways:

$$\Delta h = \alpha_{gate} \cdot \phi_{slow}(h) + (1 - \alpha_{gate}) \cdot \phi_{fast}(h)$$

#### 2.2.3 EMA-Based Knowledge Consolidation

To transfer knowledge from the high-capacity slow adapter to the efficient fast adapter, we employ exponential moving average consolidation. After each training step, the fast adapter parameters are updated:

$$\phi_{fast} \leftarrow \beta \cdot \phi_{fast} + (1 - \beta) \cdot \text{project}(\phi_{slow})$$

where $\beta \in \{0.99, 0.999, 0.9999\}$ is the decay rate and $\text{project}(\cdot)$ performs dimensionality reduction from $r_{slow}$ to $r_{fast}$ via SVD truncation:

$$\text{project}(B_{slow} A_{slow}) = U_{:,:r_{fast}} \Sigma_{:r_{fast},:r_{fast}} V_{:r_{fast},:}^T$$

This consolidation enables the fast adapter to gradually absorb generalizable knowledge while the slow adapter handles complex, task-specific patterns.

#### 2.2.4 Orthogonality Constraint

To encourage complementary rather than redundant learning between adapters, we add an orthogonality regularization term:

$$\mathcal{L}_{orth} = \left\| A_{fast}^T A_{slow}[:r_{fast},:] \right\|_F^2$$

The total training objective becomes:

$$\mathcal{L}_{total} = \mathcal{L}_{task} + \lambda_{orth} \mathcal{L}_{orth}$$

where $\lambda_{orth} = 0.01$ balances task performance and adapter diversity.

### 2.3 Algorithmic Procedure

**Algorithm 1: DT-CaPEFT Training**

```
Input: Foundation model f_θ, task sequence T, hyperparameters (β, τ, λ_orth)
Initialize: φ_fast (r=4), φ_slow (r=32), W_gate, b_gate

For each task T_k in T:
    For each batch (x, y) in T_k:
        1. Forward pass through f_θ, cache attention weights A
        2. Compute complexity: α_complexity = AttentionEntropy(A)
        3. Compute gate: α_gate = sigmoid((W_gate · α_complexity + b_gate) / τ)
        4. Compute adapter outputs:
           Δh_fast = φ_fast(h), Δh_slow = φ_slow(h)
        5. Combine: Δh = α_gate · Δh_slow + (1 - α_gate) · Δh_fast
        6. Compute loss: L = L_task(f_θ(x) + Δh, y) + λ_orth · L_orth
        7. Update φ_fast, φ_slow, W_gate via gradient descent
        8. Consolidate: φ_fast ← β · φ_fast + (1-β) · project(φ_slow)
    End For
End For

Output: Trained adapters φ_fast, φ_slow, routing parameters W_gate, b_gate
```

### 2.4 Experimental Design

#### 2.4.1 Datasets and Benchmarks

We evaluate DT-CaPEFT on three benchmark categories:

1. **Long-Context Understanding**: SCROLLS (7 tasks including QMSum, NarrativeQA, Qasper) and LongBench (21 tasks across 6 categories)

2. **Continual Learning**: Split-CIFAR-100 (20 tasks, 5 classes each) adapted for vision transformers, and a custom continual NLP benchmark constructed from sequential domains

3. **Complexity-Stratified Evaluation**: We create complexity-stratified splits by computing attention entropy on validation sets and partitioning into Low (entropy < 2.0), Medium (2.0-4.0), and High (> 4.0) complexity subsets

#### 2.4.2 Baselines

We compare against state-of-the-art PEFT and continual learning methods:

- **LoRA**: Fixed-rank adapter (r=16) as standard baseline
- **AdaLoRA**: Adaptive rank allocation based on importance scores
- **PEARL**: Dynamic rank allocation based on task proximity
- **C-LoRA**: Continual LoRA with orthogonality constraints
- **CL-LoRA**: Continual learning LoRA with replay mechanisms

#### 2.4.3 Implementation Details

- **Base Model**: Llama-3.1-8B with frozen backbone
- **Optimizer**: AdamW with learning rate $1 \times 10^{-4}$, weight decay 0.01
- **Batch Size**: 8 per GPU, gradient accumulation for effective batch size 32
- **Training**: 3 epochs per task, early stopping based on validation loss
- **Hardware**: 4× NVIDIA A100 80GB GPUs
- **Hyperparameter Search**: Grid search over $\beta \in \{0.99, 0.999, 0.9999\}$, $\tau \in \{0.1, 0.5, 1.0\}$

#### 2.4.4 Evaluation Metrics

1. **Task Accuracy**: Average accuracy across all tasks after training completion

2. **Forgetting Rate (FR)**: 
$$FR = \frac{1}{K-1} \sum_{k=1}^{K-1} \max_{t \in \{1,...,K-1\}} (a_{t,k} - a_{K,k})$$
where $a_{t,k}$ is accuracy on task $k$ after learning task $t$

3. **Parameter Efficiency Ratio (PER)**:
$$PER = \frac{\text{Active Parameters per Inference}}{\text{Total Adapter Parameters}}$$

4. **Computational Overhead**: Additional latency compared to single-adapter baseline

5. **Complexity-Stratified Performance**: Accuracy breakdown by input complexity tier

#### 2.4.5 Ablation Studies

To validate the causal mechanism, we conduct systematic ablations:

- **A1**: Remove complexity estimation (random routing)
- **A2**: Replace soft gating with hard switching
- **A3**: Disable EMA consolidation (independent adapters)
- **A4**: Remove orthogonality constraint
- **A5**: Reverse consolidation direction (fast → slow)
- **A6**: Single adapter baselines at r=4, r=16, r=32

#### 2.4.6 Statistical Analysis

- **Sample Size**: Minimum 20 runs per condition with different random seeds
- **Statistical Tests**: Paired t-tests for within-method comparisons, independent t-tests for between-method comparisons
- **Significance Level**: $\alpha = 0.05$ with Bonferroni correction for multiple comparisons
- **Effect Size**: Cohen's d reported for all significant results
- **Confidence Intervals**: 95% CI for all primary metrics

## 3. Expected Outcomes & Impact

### 3.1 Primary Expected Results

Based on our hypothesis and supporting evidence from related work, we anticipate the following outcomes:

**Prediction 1 (Parameter Efficiency)**: On low-complexity inputs (entropy < 2.0), DT-CaPEFT will achieve ≥95% of full-model performance while using only 12.5% of adapter parameters. This represents an 8× parameter reduction for approximately 40-50% of typical inputs.

**Prediction 2 (High-Complexity Performance)**: On high-complexity inputs (entropy > 4.0), engaging the slow adapter will improve accuracy by ≥5% compared to fast-only processing, validating the need for adaptive capacity allocation.

**Prediction 3 (Consolidation Benefit)**: EMA consolidation will improve generalization on held-out tasks by ≥3% compared to independent adapter training, demonstrating effective knowledge transfer.

**Prediction 4 (Continual Learning)**: DT-CaPEFT will achieve forgetting rates comparable to or better than C-LoRA while using 40-60% fewer active parameters on average.

### 3.2 Broader Impact

**Theoretical Contributions**:
- Establishes a principled connection between input complexity and optimal adapter capacity
- Provides empirical validation of dual-timescale learning in artificial neural networks
- Introduces attention entropy as a practical complexity measure for adaptive computation

**Practical Applications**:
- Enables more efficient deployment of foundation models in resource-constrained environments
- Supports personalized adaptation where user-specific inputs may have varying complexity
- Facilitates continual learning in production systems with streaming data

**Limitations and Future Work**:
- The method requires attention mechanisms for complexity estimation, limiting applicability to non-attention architectures
- Optimal hyperparameters may require task-specific tuning
- Future work will explore extending to state-space models and investigating cross-modal complexity measures

### 3.3 Conclusion

DT-CaPEFT represents a novel approach to parameter-efficient fine-tuning that bridges adaptive capacity allocation with continual learning. By leveraging attention entropy as a complexity signal and implementing dual-timescale consolidation inspired by biological memory systems, we expect to achieve significant efficiency gains while maintaining or improving continual learning performance. This work contributes to the broader goal of developing scalable, adaptive foundation models capable of efficient deployment in dynamic, real-world environments.