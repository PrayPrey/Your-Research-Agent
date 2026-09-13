# Research Proposal: Modular Adapter Composition for Continual Compositional Learning: Bridging Modularity and Temporal Generalization

## 1. Introduction

### Background

Compositional learning represents a fundamental paradigm in machine learning that mirrors the human cognitive ability to understand and generate complex concepts from simpler, reusable components. This capacity for compositional understanding enables humans to generalize effortlessly to novel situations by recombining known elements in new ways—a skill that remains elusive for even the most advanced artificial intelligence systems. While foundation models such as large language models (LLMs) and vision transformers have demonstrated remarkable capabilities across diverse tasks, their ability to generalize compositionally, particularly in dynamic real-world environments where data distributions evolve continuously, remains significantly limited.

The intersection of compositional learning and continual learning presents a particularly compelling research frontier. Real-world deployment scenarios demand models that can not only decompose and recompose knowledge compositionally but also adapt to temporal distribution shifts without catastrophic forgetting of previously acquired capabilities. Current approaches to continual learning often rely on monolithic architectures that struggle to maintain compositional structure over time, while modular approaches designed for static compositional generalization have not been thoroughly evaluated in continual settings.

Recent advances in parameter-efficient fine-tuning, particularly through adapter modules, have demonstrated that modular architectural components can capture task-specific knowledge while preserving the general capabilities of pre-trained models. Works such as SEMA (Wang et al., 2024) and CMoA (Cui et al., 2023) have begun exploring adapter-based approaches for continual learning, showing promising results in mitigating forgetting. However, these approaches have not explicitly addressed whether the modularity they introduce translates to improved compositional generalization over time, nor have they developed principled mechanisms for composing adapters to handle novel combinations of learned skills.

### Research Objectives

This research proposes **Compositional Adapter Banks (CAB)**, a novel framework designed to bridge the gap between modular learning and temporal compositional generalization. Our primary objectives are:

1. To develop an automated skill decomposition mechanism that identifies reusable adapter components when learning new tasks, thereby promoting compositional knowledge representation.

2. To design a meta-routing architecture that learns to compose adapter subsets for novel task combinations, enabling zero-shot generalization to unseen compositions.

3. To establish selective consolidation strategies that manage memory efficiency while preserving compositional boundaries critical for generalization.

4. To provide empirical evidence addressing whether structural modularity in adapter-based architectures guarantees compositional generalization in continual learning settings.

### Significance

This research directly addresses multiple focus areas of the Workshop on Compositional Learning. First, it investigates whether modular structures guarantee compositional generalization—a question that remains largely unanswered despite significant interest. Second, it proposes transferable compositional learning methods compatible with existing foundation models through lightweight adapter integration. Third, it tackles unique challenges in extending compositional learning to continual environments, including memory management and temporal performance stability. The outcomes will provide both theoretical insights and practical tools for deploying compositionally-aware models in dynamic real-world scenarios.

## 2. Methodology

### 2.1 Framework Overview

The Compositional Adapter Banks (CAB) framework consists of three integrated components: (1) a Skill Decomposition Module that analyzes new tasks to identify reusable components, (2) a Composition Router that orchestrates adapter combinations for inference, and (3) a Selective Consolidation mechanism that manages the adapter library over time. The framework operates on top of a frozen pre-trained foundation model $f_\theta$, with all adaptation occurring through lightweight adapter modules.

### 2.2 Adapter Architecture

Each adapter $A_i$ in our bank follows a bottleneck architecture inserted into transformer layers. For an input hidden state $h \in \mathbb{R}^d$, the adapter transformation is defined as:

$$A_i(h) = h + W_i^{up} \cdot \sigma(W_i^{down} \cdot h + b_i^{down}) + b_i^{up}$$

where $W_i^{down} \in \mathbb{R}^{r \times d}$ and $W_i^{up} \in \mathbb{R}^{d \times r}$ are the down and up projection matrices respectively, $r \ll d$ is the bottleneck dimension, $\sigma$ is a non-linear activation function (GELU), and $b_i^{down}$, $b_i^{up}$ are bias terms. Each adapter is associated with a skill descriptor $s_i \in \mathbb{R}^k$ learned through contrastive objectives.

### 2.3 Skill Decomposition Module

When a new task $\mathcal{T}_t$ arrives with training data $\mathcal{D}_t = \{(x_j, y_j)\}_{j=1}^{N_t}$, the Skill Decomposition Module determines the optimal combination of existing adapters and identifies requirements for new adapter creation.

**Step 1: Task Embedding Generation.** We first compute a task embedding $e_t$ by aggregating gradients of the loss with respect to the frozen model's intermediate representations:

$$e_t = \frac{1}{N_t} \sum_{j=1}^{N_t} \nabla_h \mathcal{L}(f_\theta(x_j), y_j)$$

**Step 2: Adapter Relevance Scoring.** For each existing adapter $A_i$ in the bank $\mathcal{B} = \{A_1, ..., A_K\}$, we compute a relevance score using the gradient-based attribution:

$$r_i^t = \text{sim}(e_t, s_i) \cdot \exp\left(-\frac{1}{|\mathcal{D}_t|}\sum_{(x,y) \in \mathcal{D}_t} \mathcal{L}(f_\theta \circ A_i(x), y)\right)$$

where $\text{sim}(\cdot, \cdot)$ denotes cosine similarity.

**Step 3: Sparse Adapter Selection.** We select a subset of adapters $\mathcal{S}_t \subseteq \mathcal{B}$ using a threshold $\tau$:

$$\mathcal{S}_t = \{A_i \in \mathcal{B} : r_i^t > \tau\}$$

**Step 4: Residual Skill Detection.** We measure the residual learning requirement after applying selected adapters:

$$\mathcal{R}_t = \mathcal{L}\left(f_\theta \circ \sum_{A_i \in \mathcal{S}_t} \alpha_i A_i(x), y\right) - \epsilon$$

If $\mathcal{R}_t > 0$, we initialize a new adapter $A_{K+1}$ to capture the residual skill, where $\alpha_i$ are learned composition weights.

### 2.4 Composition Router

The Composition Router $\mathcal{R}_\phi$ is a lightweight neural network that learns to predict adapter compositions for arbitrary inputs. Given an input $x$, the router outputs a sparse weight vector:

$$w = \text{Softmax}(\text{TopK}(\mathcal{R}_\phi(x), k))$$

where $\text{TopK}$ retains only the $k$ highest values and sets others to negative infinity before softmax. The final adapted representation is:

$$h' = h + \sum_{i=1}^{K} w_i \cdot A_i(h)$$

The router is trained using a combination of task-specific loss and a compositional consistency regularizer:

$$\mathcal{L}_{router} = \mathcal{L}_{task} + \lambda_{comp} \cdot \mathcal{L}_{comp}$$

where the compositional consistency loss ensures that compositions of adapters for individual concepts yield similar results to adapters trained on combined concepts:

$$\mathcal{L}_{comp} = \mathbb{E}_{x \sim \mathcal{D}_{comp}}\left[\left\| \sum_{i \in C_1} w_i A_i(h) + \sum_{j \in C_2} w_j A_j(h) - A_{C_1 \cup C_2}(h) \right\|^2\right]$$

### 2.5 Selective Consolidation

To prevent unbounded growth of the adapter bank while preserving compositional boundaries, we implement a periodic consolidation procedure.

**Co-activation Analysis.** We maintain a co-activation matrix $M \in \mathbb{R}^{K \times K}$ where $M_{ij}$ records the frequency with which adapters $A_i$ and $A_j$ are simultaneously activated:

$$M_{ij} = \frac{1}{T} \sum_{t=1}^{T} \mathbb{1}[w_i^t > \delta] \cdot \mathbb{1}[w_j^t > \delta]$$

**Structured Merging.** When $M_{ij}$ exceeds a threshold $\gamma$, we merge adapters using a parameter averaging scheme that preserves their combined functionality:

$$A_{merged} = \alpha \cdot A_i + (1-\alpha) \cdot A_j$$

where $\alpha = \frac{\|W_i\|_F}{\|W_i\|_F + \|W_j\|_F}$ weights by parameter magnitude.

**Compositional Boundary Preservation.** Before merging, we verify that the merged adapter does not destroy compositional generalization by testing on held-out compositional combinations:

$$\Delta_{comp} = \text{Acc}(A_{merged}, \mathcal{D}_{comp}) - \text{Acc}(\{A_i, A_j\}, \mathcal{D}_{comp})$$

Merging proceeds only if $\Delta_{comp} > -\epsilon_{tol}$.

### 2.6 Experimental Design

**Datasets and Benchmarks:**

1. **CLEVR-Continual**: We extend CLEVR with temporal distribution shifts, introducing new object attributes (colors, shapes, materials) and relations over 10 sequential stages. We evaluate compositional generalization on held-out attribute-relation combinations.

2. **COGS-Evolving**: We adapt the COGS semantic parsing benchmark to include evolving schemas, introducing new predicates and argument structures incrementally over 8 stages.

3. **Action-Genome-Continual**: Based on ViLPAct, we create a continual action understanding benchmark with progressive introduction of actions and objects.

**Baselines:**
- Sequential fine-tuning (monolithic)
- Experience Replay with adapters
- SEMA (Wang et al., 2024)
- CMoA (Cui et al., 2023)
- ATLAS (Li et al., 2024)
- EWC + Adapters

**Evaluation Metrics:**

1. **Forward Transfer (FT)**: Measures performance improvement on new tasks due to prior learning:
$$FT = \frac{1}{T-1}\sum_{t=2}^{T}(Acc_t^{CAB} - Acc_t^{scratch})$$

2. **Backward Transfer (BT)**: Measures forgetting of previous tasks:
$$BT = \frac{1}{T-1}\sum_{t=1}^{T-1}(Acc_{t,T} - Acc_{t,t})$$

3. **Compositional Generalization Score (CGS)**: Accuracy on held-out novel compositions:
$$CGS = \frac{1}{|\mathcal{D}_{novel}|}\sum_{(x,y) \in \mathcal{D}_{novel}} \mathbb{1}[\hat{y} = y]$$

4. **Memory Efficiency**: Number of parameters added relative to baseline.

**Implementation Details:**
We implement CAB on ViT-B/16 for visual tasks and T5-base for semantic parsing. Adapters use bottleneck dimension $r=64$, router hidden dimension 256, and we set $\tau=0.3$, $\gamma=0.7$, $k=4$, and $\lambda_{comp}=0.1$.

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Improved Compositional Generalization**: We anticipate CAB will achieve 15-25% higher CGS compared to monolithic continual learning baselines, demonstrating that principled modular composition enables better generalization to novel combinations.

2. **Reduced Catastrophic Forgetting**: Through selective adapter reuse and consolidation, we expect backward transfer improvements of 10-20% compared to sequential fine-tuning, with performance approaching replay-based methods without requiring memory buffers.

3. **Efficient Scaling**: The selective consolidation mechanism should maintain adapter bank size within 2-3x of task count while preserving compositional capabilities, demonstrating practical memory efficiency.

4. **Theoretical Insights**: Our ablation studies will provide empirical evidence regarding the relationship between structural modularity and compositional generalization, addressing a fundamental question in the field.

### Impact

This research will contribute to the workshop's core themes in several ways. For **Perspectives**, our empirical analysis will illuminate when and why modular structures support compositional generalization, providing guidance for foundation model design. For **Methods**, CAB offers a practical, model-agnostic framework compatible with existing pre-trained models through standard adapter interfaces. For the intersection of **Methods and Perspectives**, our systematic evaluation directly tests whether modularity guarantees compositional generalization. For **Paths Forward**, we address the critical challenge of deploying compositional learning in continual settings, providing solutions for memory management and temporal stability.

The broader impact includes enabling more robust deployment of AI systems in dynamic environments such as robotics, dialogue systems, and autonomous agents, where continuous adaptation without forgetting is essential. Our code and benchmarks will be released to facilitate future research in this emerging intersection of compositional and continual learning.