# Research Proposal: CLS-LoRA: Neuroscience-Inspired Dual-Adapter Architecture for Scalable Continual Learning in Foundation Models

## 1. Introduction

### 1.1 Background

Foundation models (FMs) have revolutionized machine learning across vision, language, and multimodal domains, achieving unprecedented performance through large-scale pretraining on massive datasets. However, these models face a fundamental limitation: they are trained on static data snapshots, leading to outdated encoded information, knowledge saturation, and inefficient compute utilization when updates are required. As foundation models continue to scale—with modern architectures containing billions of parameters—even fine-tuning becomes prohibitively resource-intensive, demanding novel approaches for efficient knowledge updates.

Continual learning (CL) emerges as a crucial framework for addressing these challenges, enabling models to sequentially acquire new knowledge while preserving previously learned information. The central challenge in CL is catastrophic forgetting, where learning new tasks degrades performance on previously mastered ones. This plasticity-stability dilemma becomes particularly acute when fine-tuning foundation models on smaller, less diverse datasets compared to their extensive pretraining corpora.

Parameter-efficient fine-tuning (PEFT) methods, particularly Low-Rank Adaptation (LoRA), have gained prominence for updating foundation models with minimal parameter overhead. Recent works have extended LoRA for continual learning scenarios: CL-LoRA introduces dual-adapter architectures separating cross-task and task-specific knowledge; LoRA⁻ employs subtraction mechanisms to create drift-resistant subspaces; and ShareLoRA explores parameter sharing across tasks. However, these approaches either use static dual-adapters without knowledge consolidation or employ simple subtraction mechanisms without importance weighting—neither capturing the sophisticated memory consolidation processes observed in biological systems.

### 1.2 Neuroscience Inspiration: Complementary Learning Systems

The mammalian brain has evolved an elegant solution to the plasticity-stability dilemma through Complementary Learning Systems (CLS). In this framework, the hippocampus rapidly encodes new episodic experiences with sparse, pattern-separated representations, while the neocortex gradually consolidates stable semantic knowledge through interleaved replay and slow learning. This dual-system architecture enables rapid acquisition of new information without catastrophic interference with existing knowledge—precisely the capability required for continual learning in foundation models.

Despite the proven effectiveness of CLS principles in biological learning, this template remains largely unexploited in LoRA-based continual learning. Existing methods either lack the dual-system architecture entirely or implement it without the critical consolidation mechanism that transfers knowledge from rapid to stable storage.

### 1.3 Research Objectives

This research proposes **CLS-LoRA**, a neuroscience-inspired dual-adapter architecture that operationalizes CLS theory within the LoRA framework for scalable continual learning in foundation models. Our primary objectives are:

1. **Design a CLS-inspired dual-adapter architecture** comprising a "hippocampal" LoRA module for rapid task-specific encoding and a "neocortical" LoRA module for consolidated knowledge storage.

2. **Develop a periodic second-order importance-weighted consolidation mechanism** that selectively transfers critical parameters from the hippocampal to neocortical module, mimicking biological memory consolidation.

3. **Validate the approach** on standard continual learning benchmarks, demonstrating superior performance (>88.5% accuracy, <5% forgetting) compared to state-of-the-art LoRA-CL methods while maintaining parameter efficiency (<2% of backbone).

4. **Establish causal understanding** through systematic ablation studies isolating each component of the proposed mechanism.

### 1.4 Significance

This research addresses a critical gap in scalable continual learning for foundation models by bridging neuroscience principles with parameter-efficient fine-tuning. Success would establish neuroscience-grounded design principles for lifelong foundation model learning, potentially replacing static retraining paradigms with efficient, incremental knowledge updates. The approach maintains the parameter efficiency essential for practical deployment while achieving superior plasticity-stability balance through biologically-inspired mechanisms.

## 2. Methodology

### 2.1 Overview of CLS-LoRA Architecture

CLS-LoRA implements a dual-adapter architecture inspired by Complementary Learning Systems theory. The system comprises two LoRA modules operating on a frozen foundation model backbone:

1. **Hippocampal LoRA Module ($\mathcal{H}$)**: Rapidly encodes task-specific knowledge with orthogonal initialization to prevent gradient interference.

2. **Neocortical LoRA Module ($\mathcal{N}$)**: Stores consolidated knowledge through periodic importance-weighted merging from the hippocampal module.

The forward pass combines both modules:

$$h = W_0 x + \alpha_{\mathcal{H}} B_{\mathcal{H}} A_{\mathcal{H}} x + \alpha_{\mathcal{N}} B_{\mathcal{N}} A_{\mathcal{N}} x$$

where $W_0$ is the frozen pretrained weight matrix, $A_{\mathcal{H}}, B_{\mathcal{H}}$ and $A_{\mathcal{N}}, B_{\mathcal{N}}$ are the low-rank decomposition matrices for hippocampal and neocortical modules respectively, and $\alpha_{\mathcal{H}}, \alpha_{\mathcal{N}}$ are scaling factors.

### 2.2 Four-Step Causal Mechanism

The CLS-LoRA mechanism operates through four sequential steps:

#### Step 1: Orthogonal Initialization

To prevent gradient interference between sequential tasks, we initialize the hippocampal LoRA matrices using orthogonal initialization:

$$A_{\mathcal{H}}^{(t)} \sim \text{Orthogonal}(d_{in}, r), \quad B_{\mathcal{H}}^{(t)} \leftarrow \mathbf{0}$$

where $r$ is the LoRA rank and $d_{in}$ is the input dimension. This ensures that task-specific adaptations occupy orthogonal subspaces, minimizing interference during sequential learning.

#### Step 2: Hippocampal Rapid Encoding

For each new task $t$, only the hippocampal module is trained while the neocortical module remains frozen:

$$\mathcal{L}_t = \mathcal{L}_{CE}(f_{\theta}(x; \mathcal{H}^{(t)}, \mathcal{N}), y) + \lambda_{orth} \mathcal{L}_{orth}$$

where $\mathcal{L}_{CE}$ is the cross-entropy loss, and $\mathcal{L}_{orth}$ is an orthogonality regularization term:

$$\mathcal{L}_{orth} = \|A_{\mathcal{H}}^{(t)\top} A_{\mathcal{H}}^{(t)} - I\|_F^2$$

This enables rapid task-specific learning without disturbing consolidated knowledge.

#### Step 3: Second-Order Importance-Weighted Consolidation

After every $k$ tasks (consolidation interval), we perform importance-weighted merging from the hippocampal to neocortical module. The importance of each parameter is estimated using second-order information:

**First-order importance (gradient magnitude):**
$$I_1(\theta_i) = \left|\frac{\partial \mathcal{L}}{\partial \theta_i}\right|$$

**Second-order importance (curvature via Fisher Information):**
$$I_2(\theta_i) = \mathbb{E}\left[\left(\frac{\partial \mathcal{L}}{\partial \theta_i}\right)^2\right]$$

**Combined importance score:**
$$I(\theta_i) = \sqrt{I_1(\theta_i) \cdot I_2(\theta_i)}$$

Following the PIECE methodology, we normalize importance scores and select the top-$p\%$ critical parameters for consolidation.

**Consolidation update rule:**
$$\mathcal{N}^{(t+k)} = (1 - \beta) \mathcal{N}^{(t)} + \beta \cdot M \odot \mathcal{H}^{(t:t+k)}$$

where $\beta$ is the consolidation rate, $M$ is the binary importance mask selecting critical parameters, and $\mathcal{H}^{(t:t+k)}$ represents the accumulated hippocampal knowledge over the consolidation interval.

#### Step 4: Drift-Resistant Subspace Protection

To protect consolidated knowledge from drift during subsequent learning, we project hippocampal gradients away from the neocortical subspace:

$$\nabla_{\mathcal{H}}^{proj} = \nabla_{\mathcal{H}} - P_{\mathcal{N}} \nabla_{\mathcal{H}}$$

where $P_{\mathcal{N}}$ is the projection matrix onto the neocortical subspace:

$$P_{\mathcal{N}} = A_{\mathcal{N}} (A_{\mathcal{N}}^\top A_{\mathcal{N}})^{-1} A_{\mathcal{N}}^\top$$

This ensures that hippocampal updates do not interfere with consolidated neocortical knowledge.

### 2.3 Algorithm

**Algorithm 1: CLS-LoRA Training**

```
Input: Foundation model f with frozen weights W₀, task sequence {T₁, ..., Tₙ}, 
       consolidation interval k, importance threshold p
Output: Trained neocortical module N

Initialize: N ← 0, consolidation_buffer ← []

for t = 1 to n do:
    # Step 1: Orthogonal Initialization
    H^(t) ← OrthogonalInit(rank=r)
    
    # Step 2: Hippocampal Rapid Encoding
    for epoch = 1 to E do:
        for (x, y) in Tₜ do:
            L = L_CE(f(x; H^(t), N), y) + λ_orth * L_orth(H^(t))
            ∇H ← ComputeGradient(L)
            # Step 4: Drift-Resistant Projection
            ∇H_proj ← ∇H - P_N * ∇H
            H^(t) ← H^(t) - η * ∇H_proj
        end for
    end for
    
    consolidation_buffer.append(H^(t))
    
    # Step 3: Periodic Consolidation
    if t mod k == 0 then:
        I ← ComputeSecondOrderImportance(consolidation_buffer)
        M ← SelectTopP(I, p)
        H_merged ← MergeBuffer(consolidation_buffer)
        N ← (1 - β) * N + β * (M ⊙ H_merged)
        consolidation_buffer ← []
    end if
end for

return N
```

### 2.4 Experimental Design

#### 2.4.1 Datasets and Benchmarks

**Primary Benchmark:**
- **CIFAR-100 B10**: 100 classes split into 10 tasks of 10 classes each, following the class-incremental learning protocol.

**Extended Benchmarks:**
- **ImageNet-R B20**: 200 classes across 20 tasks for domain shift evaluation
- **CORe50**: Object recognition with temporal domain shifts
- **5-Datasets**: Sequential learning across CIFAR-10, MNIST, Fashion-MNIST, SVHN, and notMNIST

#### 2.4.2 Foundation Model Backbone

- **Primary**: ViT-B/16 pretrained on ImageNet-21k (86M parameters), frozen during all experiments
- **Scalability Study**: ViT-L/16 (304M parameters) to assess scaling behavior

#### 2.4.3 Baselines

| Method | Description |
|--------|-------------|
| CL-LoRA | Dual-adapter with cross-task/task-specific separation |
| LoRA⁻ | Subtraction-based drift-resistant LoRA |
| ShareLoRA | Parameter-sharing across tasks |
| PEARL | Prompt-enhanced adapter with replay |
| SD-LoRA | Self-distillation LoRA |

#### 2.4.4 Hyperparameters

| Parameter | Value | Search Range |
|-----------|-------|--------------|
| LoRA rank $r$ | 16 | {4, 8, 16, 32} |
| Consolidation interval $k$ | 2 | {1, 2, 5} |
| Importance threshold $p$ | 30% | {10%, 30%, 50%} |
| Consolidation rate $\beta$ | 0.3 | {0.1, 0.3, 0.5} |
| Orthogonality weight $\lambda_{orth}$ | 0.01 | {0.001, 0.01, 0.1} |
| Learning rate $\eta$ | 1e-4 | {1e-5, 1e-4, 1e-3} |
| Training epochs $E$ | 5 | Fixed |

#### 2.4.5 Evaluation Metrics

**Average Accuracy (A):**
$$A = \frac{1}{T} \sum_{t=1}^{T} a_{T,t}$$

where $a_{T,t}$ is the accuracy on task $t$ after learning all $T$ tasks.

**Average Forgetting (F):**
$$F = \frac{1}{T-1} \sum_{t=1}^{T-1} \max_{j \in \{t, ..., T-1\}} (a_{j,t} - a_{T,t})$$

**Forward Transfer (FT):**
$$FT = \frac{1}{T-1} \sum_{t=2}^{T} (a_{t-1,t}^{CLS} - a_{t-1,t}^{base})$$

**Parameter Efficiency:**
$$PE = \frac{|\theta_{\mathcal{H}}| + |\theta_{\mathcal{N}}|}{|\theta_{backbone}|} \times 100\%$$

#### 2.4.6 Ablation Studies

To validate the causal mechanism, we conduct systematic ablations:

| Ablation | Configuration | Tests |
|----------|---------------|-------|
| A1: No Orthogonal Init | Random Gaussian initialization | Step 1 necessity |
| A2: No Consolidation | Static dual-adapter (like CL-LoRA) | Step 3 necessity |
| A3: First-Order Only | Gradient magnitude importance only | Second-order benefit |
| A4: No Drift Protection | Standard gradient updates | Step 4 necessity |
| A5: Single Adapter | Neocortical only, no hippocampal | Dual-system benefit |

#### 2.4.7 Statistical Validation

- **Runs**: 20 independent runs (5 random seeds × 4 task orderings)
- **Statistical Tests**: Paired t-test with Bonferroni correction ($\alpha = 0.05/4 = 0.0125$)
- **Reporting**: Mean ± standard deviation, 95% confidence intervals, Cohen's d effect size

### 2.5 Implementation Details

- **Framework**: PyTorch with HuggingFace PEFT library
- **Hardware**: NVIDIA A100 (40GB) GPUs
- **Estimated Memory**: ~16GB for ViT-B/16 with dual LoRA (r=16)
- **Training Time**: ~2 hours per full CIFAR-100 B10 experiment

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our hypothesis and the supporting evidence from related work, we anticipate the following outcomes:

**Primary Performance Targets:**

| Metric | CLS-LoRA (Expected) | SOTA Baseline | Improvement |
|--------|---------------------|---------------|-------------|
| Average Accuracy | >88.5% | ~86% (CL-LoRA) | +2.5% |
| Average Forgetting | <5% | ~8-10% (CL-LoRA) | -50% relative |
| Parameter Efficiency | <2% | ~2% (ShareLoRA) | Comparable |

**Ablation Predictions:**
- Removing orthogonal initialization: +3-5% forgetting
- Removing consolidation mechanism: -2-3% accuracy
- First-order only importance: -1-2% accuracy vs second-order
- Removing drift protection: +2-4% forgetting

**Scalability Predictions:**
- Long sequence robustness (50 tasks): <10% accuracy degradation from task 10
- Scaling to ViT-L/16: Maintained relative improvements with <3% parameter overhead

### 3.2 Scientific Contributions

1. **Neuroscience-ML Bridge**: First systematic operationalization of CLS theory within LoRA-based continual learning, establishing design principles transferable to other PEFT methods.

2. **Mechanistic Understanding**: Comprehensive ablation studies providing causal evidence for each component's contribution, advancing theoretical understanding of plasticity-stability trade-offs in parameter-efficient settings.

3. **Scalable Consolidation**: Novel second-order importance-weighted consolidation mechanism applicable beyond the proposed architecture.

### 3.3 Practical Impact

1. **Efficient Foundation Model Updates**: Enables incremental knowledge updates without full retraining, reducing computational costs by orders of magnitude.

2. **Deployment Flexibility**: Maintains parameter efficiency essential for edge deployment while achieving superior continual learning performance.

3. **Benchmark Advancement**: Establishes new state-of-the-art on standard CL benchmarks, providing strong baselines for future research.

### 3.4 Broader Implications

Success of CLS-LoRA would validate the broader principle that neuroscience-inspired architectures can provide systematic advantages in machine learning systems facing similar computational challenges to biological brains. This opens avenues for:

- **Multimodal Continual Learning**: Extension to vision-language models with modality-specific hippocampal modules
- **Online Learning**: Adaptation for streaming scenarios without explicit task boundaries
- **Federated Continual Learning**: Distributed consolidation across edge devices

### 3.5 Limitations and Future Directions

**Current Limitations:**
- Requires known task boundaries for consolidation timing
- Consolidation adds ~5% computational overhead per interval
- Initial validation limited to vision transformers

**Future Extensions:**
- Task-free consolidation using representation similarity metrics
- Application to large language models (LLaMA, GPT architectures)
- Integration with retrieval-augmented generation for knowledge grounding

### 3.6 Falsification Criteria

The hypothesis will be rejected if:
1. Average accuracy ≤ 83% on CIFAR-100 B10 (below SOTA - 1σ)
2. Ablations show no benefit from consolidation vs simple averaging
3. Parameter overhead exceeds 5% of backbone
4. No improvement on any metric versus CL-LoRA baseline

This rigorous falsification framework ensures scientific integrity and provides clear decision criteria for evaluating the proposed approach.

---

**Conclusion**: CLS-LoRA represents a principled approach to scalable continual learning in foundation models, grounded in neuroscience theory and validated through rigorous empirical methodology. By bridging biological learning principles with parameter-efficient fine-tuning, this research addresses critical challenges in lifelong foundation model learning while maintaining practical efficiency constraints.