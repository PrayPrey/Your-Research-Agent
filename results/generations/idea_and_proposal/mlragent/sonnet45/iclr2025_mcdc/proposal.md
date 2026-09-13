# Dynamic Expert Consolidation for Continual Learning in Modular Mixture-of-Experts

## 1. Introduction

### Background

The rapid advancement of deep learning has been primarily driven by the "bigger is better" paradigm, where increasingly large models trained on massive datasets have achieved remarkable performance across diverse tasks. However, this approach faces critical sustainability challenges, including prohibitive computational costs, environmental concerns, and the wasteful practice of training models from scratch when updates are needed. More fundamentally, current monolithic models suffer from catastrophic forgetting when adapted to new tasks, lack modularity for targeted updates, and require complete retraining even for minor modifications.

Mixture-of-Experts (MoE) architectures offer a promising alternative by decomposing models into specialized, sparsely-activated modules. In continual learning scenarios, MoE systems can theoretically allocate new experts for new tasks while preserving existing knowledge in frozen experts. However, this approach faces a critical scalability challenge: naive expert addition leads to unbounded model growth, while expert reuse risks catastrophic forgetting. Recent works have explored various strategies, including fine-grained rank-based decomposition (MoRA), null-space constrained gating (MINGLE), and prompt-based approaches, yet none adequately address the fundamental tension between bounded capacity and indefinite learning.

The core limitation of existing approaches is their static view of expert allocation. Models either grow indefinitely by adding experts for each new task or maintain fixed capacity at the cost of knowledge interference. This binary choice ignores the dynamic nature of knowledge: some expertise becomes redundant over time, complementary knowledge can be consolidated, and new specializations may emerge as task distributions evolve.

### Research Objectives

This research proposes **Dynamic Expert Consolidation (DEC)**, a novel framework that enables continual learning in MoE systems through adaptive knowledge consolidation and re-specialization. Our specific objectives are:

1. **Develop functional similarity metrics** that capture semantic and behavioral overlap between experts beyond parameter-space distances, enabling identification of consolidation opportunities.

2. **Design selective expert merging mechanisms** that consolidate redundant or complementary knowledge while maintaining a branching history for potential future specialization.

3. **Create adaptive re-specialization protocols** that allow merged experts to split when encountering tasks requiring finer-grained expertise, guided by routing patterns and performance metrics.

4. **Establish theoretical guarantees** on forgetting bounds and capacity utilization in the proposed framework.

5. **Demonstrate practical effectiveness** across diverse continual learning benchmarks, showing superior performance-capacity trade-offs compared to existing approaches.

### Significance

This research addresses a fundamental challenge in building sustainable, continually learning AI systems. By enabling dynamic knowledge consolidation, we transform the continual learning problem from managing unbounded growth to optimizing a bounded, evolving knowledge structure. The significance extends across multiple dimensions:

**Scientific Impact**: The work bridges model merging, continual learning, and MoE architectures, providing theoretical insights into knowledge consolidation in neural networks and establishing principles for dynamic modular architectures.

**Practical Impact**: DEC enables deployment of continual learning systems in resource-constrained environments where model size must remain bounded, supporting applications in edge computing, personalized AI, and long-running autonomous systems.

**Sustainability Impact**: By reusing and consolidating knowledge rather than perpetually adding capacity, this approach reduces computational waste and energy consumption associated with continual model expansion.

## 2. Methodology

### 2.1 Problem Formulation

We consider a continual learning scenario where a model encounters a sequence of tasks $\mathcal{T} = \{T_1, T_2, ..., T_n, ...\}$ with potentially unbounded $n$. Each task $T_i$ consists of a data distribution $\mathcal{D}_i$ over input-output pairs $(x, y)$. The model is a Mixture-of-Experts system with a set of experts $\mathcal{E}_t = \{E_1, E_2, ..., E_{k_t}\}$ at time $t$, where $k_t$ is the current number of experts.

The MoE output for input $x$ is computed as:
$$f(x) = \sum_{i=1}^{k_t} g_i(x) \cdot E_i(x)$$

where $g_i(x)$ is the gating function output for expert $i$, satisfying $\sum_{i=1}^{k_t} g_i(x) = 1$ and typically implemented as:
$$g_i(x) = \frac{\exp(w_i^T h(x))}{\sum_{j=1}^{k_t} \exp(w_j^T h(x))}$$

with $h(x)$ being a learned representation and $w_i$ the gating parameters for expert $i$.

Our objective is to maintain bounded capacity $|\mathcal{E}_t| \leq K_{max}$ while minimizing cumulative forgetting across all tasks seen up to time $t$:
$$\min_{\theta} \mathcal{L}_{total} = \sum_{i=1}^{t} \mathbb{E}_{(x,y) \sim \mathcal{D}_i}[\ell(f_{\theta_t}(x), y)]$$

subject to the constraint that $k_t \leq K_{max}$ for all $t$.

### 2.2 Functional Similarity Metrics

To identify consolidation opportunities, we develop multi-faceted similarity metrics that capture functional overlap between experts beyond parameter distance.

#### 2.2.1 Gradient-based Similarity

For two experts $E_i$ and $E_j$, we measure their functional similarity on a task $T$ by analyzing gradient alignment on a validation set $\mathcal{V}_T$:

$$S_{grad}(E_i, E_j | T) = \frac{1}{|\mathcal{V}_T|} \sum_{(x,y) \in \mathcal{V}_T} \cos(\nabla_{\theta_i} \ell(E_i(x), y), \nabla_{\theta_j} \ell(E_j(x), y))$$

where $\theta_i, \theta_j$ are the parameters of experts $E_i, E_j$ respectively. High gradient alignment indicates that experts are learning similar features and would benefit similarly from the same updates.

#### 2.2.2 Representation Similarity

We measure similarity in the learned representations using Centered Kernel Alignment (CKA):

$$S_{rep}(E_i, E_j | \mathcal{X}) = \frac{||H_i^T H_j||_F^2}{||H_i^T H_i||_F \cdot ||H_j^T H_j||_F}$$

where $H_i, H_j$ are centered representation matrices for a sample set $\mathcal{X}$, computed at intermediate layers of experts $E_i$ and $E_j$.

#### 2.2.3 Behavioral Similarity

We measure output-level similarity across the input distribution:

$$S_{behav}(E_i, E_j | \mathcal{X}) = 1 - \frac{1}{|\mathcal{X}|} \sum_{x \in \mathcal{X}} D_{KL}(E_i(x) || E_j(x))$$

where $D_{KL}$ is the KL divergence between output distributions.

#### 2.2.4 Composite Similarity Score

We combine these metrics into a composite similarity score:
$$S(E_i, E_j) = \alpha S_{grad} + \beta S_{rep} + \gamma S_{behav}$$

where $\alpha, \beta, \gamma$ are learned or tuned weights, and all similarities are computed over a diverse replay buffer maintaining samples from all seen tasks.

### 2.3 Selective Expert Merging

When similarity $S(E_i, E_j)$ exceeds a threshold $\tau_{merge}$ or when capacity approaches $K_{max}$, we initiate expert consolidation.

#### 2.3.1 Task Arithmetic Merging

For experts specialized on complementary tasks, we use task arithmetic:
$$\theta_{merged} = \theta_{pretrained} + \lambda_i(\theta_i - \theta_{pretrained}) + \lambda_j(\theta_j - \theta_{pretrained})$$

where $\theta_{pretrained}$ is a shared initialization, and $\lambda_i, \lambda_j$ are scaling factors determined by expert importance scores:
$$\lambda_i = \frac{U_i}{U_i + U_j}, \quad U_i = \sum_{x \in \mathcal{R}_i} g_i(x)$$

where $\mathcal{R}_i$ is the set of samples historically routed to expert $i$.

#### 2.3.2 TIES-Merging for Redundant Experts

For experts with high functional overlap, we apply TIES-merging to reduce interference:

1. **Trim**: Remove parameters with small magnitude changes: $\delta_i = \text{trim}(\theta_i - \theta_{init}, \text{top-k})$
2. **Elect**: Resolve sign conflicts by majority voting across experts
3. **Merge**: Average aligned parameters with usage-based weighting

$$\theta_{merged} = \theta_{init} + \frac{\sum_i \lambda_i \cdot \text{sign\_elect}(\delta_i)}{|\{i\}|}$$

#### 2.3.3 Branching History Maintenance

To enable future re-specialization, we maintain a lightweight branching history:
$$\mathcal{H}(E_{merged}) = \{(E_i, E_j, S_{ij}, t_{merge}, \mathcal{T}_{merge})\}$$

storing the parent experts, similarity at merge time, timestamp, and task context. We also preserve low-rank residuals:
$$R_i = \theta_i - \theta_{merged} \approx U_i \Sigma_i V_i^T$$

where the rank is adaptively chosen to capture 95% of variance while minimizing storage.

### 2.4 Adaptive Re-specialization

During continual learning, we monitor routing patterns and performance to identify when merged experts should re-split.

#### 2.4.1 Split Triggering Conditions

We trigger re-specialization when:

1. **High routing entropy**: $H(g(x) | x \sim \mathcal{D}_{current}) < \tau_{entropy}$ for samples routed to $E_{merged}$, indicating the merged expert handles diverse, conflicting patterns.

2. **Performance degradation**: Validation performance on historically strong tasks drops below threshold: $\text{Acc}(E_{merged}, \mathcal{V}_i) < \text{Acc}(E_i, \mathcal{V}_i) - \delta_{perf}$

3. **Available capacity**: Current expert count allows splitting: $k_t < K_{max} - 1$

#### 2.4.2 Split Initialization

When splitting $E_{merged}$ with history $\mathcal{H}(E_{merged}) = \{E_i, E_j, ...\}$:

$$\theta_{split,1} = \theta_{merged} + \alpha \cdot (U_i \Sigma_i V_i^T)$$
$$\theta_{split,2} = \theta_{merged} + \alpha \cdot (U_j \Sigma_j V_j^T)$$

where $\alpha$ is a scaling factor (typically 0.5) and $U_i \Sigma_i V_i^T$ is the stored low-rank residual.

#### 2.4.3 Routing Refinement

After splitting, we refine the gating network using a regularized objective:
$$\mathcal{L}_{gate} = \mathcal{L}_{task} + \lambda_{load} \cdot \text{LoadBalance}(g) + \lambda_{spec} \cdot \text{Specialization}(g)$$

where:
$$\text{LoadBalance}(g) = \sum_{i} (f_i - \frac{1}{k_t})^2, \quad f_i = \frac{1}{|\mathcal{B}|}\sum_{x \in \mathcal{B}} g_i(x)$$

$$\text{Specialization}(g) = -\sum_{i} \sum_{x \in \mathcal{B}} g_i(x) \log g_i(x)$$

encouraging balanced expert usage while promoting specialized routing.

### 2.5 Training Algorithm

**Algorithm 1: Dynamic Expert Consolidation for Continual Learning**

**Input:** Task sequence $\{\mathcal{T}_1, \mathcal{T}_2, ...\}$, max experts $K_{max}$, similarity threshold $\tau_{merge}$
**Output:** MoE model with consolidated experts

1. Initialize: $\mathcal{E} \leftarrow \{E_1\}$, replay buffer $\mathcal{R} \leftarrow \emptyset$
2. **for** each task $\mathcal{T}_t$ **do**
3. $\quad$ **if** $|\mathcal{E}| < K_{max}$ **then**
4. $\quad\quad$ Add new expert $E_{new}$ initialized from $E_1$
5. $\quad$ **else**
6. $\quad\quad$ Compute $S(E_i, E_j)$ for all pairs $(i,j)$
7. $\quad\quad$ Find $(i^*, j^*) = \arg\max_{i,j} S(E_i, E_j)$
8. $\quad\quad$ **if** $S(E_{i^*}, E_{j^*}) > \tau_{merge}$ **then**
9. $\quad\quad\quad$ $E_{merged} \leftarrow \text{Merge}(E_{i^*}, E_{j^*})$ using TIES or Task Arithmetic
10. $\quad\quad\quad$ Store branching history $\mathcal{H}(E_{merged})$
11. $\quad\quad\quad$ $\mathcal{E} \leftarrow \mathcal{E} \setminus \{E_{i^*}, E_{j^*}\} \cup \{E_{merged}\}$
12. $\quad\quad\quad$ Add new expert $E_{new}$
13. $\quad$ Train on $\mathcal{T}_t$ with loss $\mathcal{L} = \mathcal{L}_{task} + \lambda_{replay}\mathcal{L}_{replay}(\mathcal{R})$
14. $\quad$ Update replay buffer: $\mathcal{R} \leftarrow \mathcal{R} \cup \text{sample}(\mathcal{D}_t)$
15. $\quad$ **for** each merged expert $E_m \in \mathcal{E}$ **do**
16. $\quad\quad$ **if** SplitCondition($E_m$) and $|\mathcal{E}| < K_{max}$ **then**
17. $\quad\quad\quad$ $(E_1', E_2') \leftarrow \text{Split}(E_m, \mathcal{H}(E_m))$
18. $\quad\quad\quad$ $\mathcal{E} \leftarrow \mathcal{E} \setminus \{E_m\} \cup \{E_1', E_2'\}$
19. $\quad\quad\quad$ Refine gating network with $\mathcal{L}_{gate}$
20. **return** $\mathcal{E}$

### 2.6 Experimental Design

#### 2.6.1 Datasets and Benchmarks

We evaluate on three continual learning scenarios:

1. **Split CIFAR-100**: 20 tasks with 5 classes each, testing class-incremental learning
2. **Permuted MNIST**: 20 tasks with different input permutations, testing domain shift robustness
3. **CORe50**: 8 object recognition tasks in different sessions, testing realistic continual learning
4. **Continual Instruction Tuning**: Sequence of 15 instruction-following tasks for language models, testing high-capacity scenarios

#### 2.6.2 Baselines

We compare against:
- **Fixed MoE**: Fixed number of experts, no consolidation
- **Growing MoE**: Add expert per task without merging
- **MoRA**: Mixture-of-Rank Adaptive learning
- **MINGLE**: Null-space constrained gating
- **PackNet**: Parameter allocation for continual learning
- **EWC**: Elastic Weight Consolidation
- **Experience Replay**: Standard replay buffer baseline

#### 2.6.3 Evaluation Metrics

1. **Average Accuracy**: $\text{ACC}_{avg} = \frac{1}{T}\sum_{i=1}^T \text{Acc}(\mathcal{D}_i)$ after training on all $T$ tasks
2. **Backward Transfer**: $\text{BWT} = \frac{1}{T-1}\sum_{i=1}^{T-1} (\text{Acc}_T(\mathcal{D}_i) - \text{Acc}_i(\mathcal{D}_i))$
3. **Forward Transfer**: $\text{FWT} = \frac{1}{T-1}\sum_{i=2}^{T} (\text{Acc}_{i-1}(\mathcal{D}_i) - \text{Acc}_{random}(\mathcal{D}_i))$
4. **Model Size Growth**: Number of parameters over time
5. **Forgetting**: $\mathcal{F} = \frac{1}{T-1}\sum_{i=1}^{T-1} \max_{j \in [i, T-1]} (\text{Acc}_j(\mathcal{D}_i) - \text{Acc}_T(\mathcal{D}_i))$
6. **Expert Utilization**: Effective number of experts via entropy: $\exp(H(p))$ where $p_i = \frac{1}{|\mathcal{D}|}\sum_{x \in \mathcal{D}} g_i(x)$

#### 2.6.4 Implementation Details

- **Architecture**: Transformer-based experts with shared embedding layer
- **Expert size**: Each expert has 4M parameters for vision tasks, 110M for language tasks
- **Maximum experts**: $K_{max} = 8$ for vision, $K_{max} = 16$ for language
- **Similarity threshold**: $\tau_{merge} = 0.75$, tuned on validation set
- **Replay buffer size**: 2000 samples for vision, 5000 for language
- **Optimization**: AdamW with learning rate 1e-4, cosine decay schedule
- **Training**: 10 epochs per task with early stopping on validation loss

### 2.7 Theoretical Analysis

We provide theoretical guarantees on forgetting bounds in DEC.

**Theorem 1 (Forgetting Bound)**: Under Lipschitz continuity assumptions on the loss and bounded merging operations, the forgetting on task $i$ after learning task $t > i$ is bounded by:

$$\mathcal{F}_i^t \leq L \cdot ||\theta_t - \theta_i||_2 \leq L \cdot \sum_{j=i+1}^t \delta_j \cdot (1 - S_{min}(E_i, E_{merged}))$$

where $L$ is the Lipschitz constant, $\delta_j$ is the parameter change at step $j$, and $S_{min}$ is the minimum similarity at merge time.

This shows that merging high-similarity experts provably reduces forgetting compared to random parameter updates.

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

We anticipate the following concrete outcomes:

**Performance**: DEC should achieve 5-10% higher average accuracy compared to fixed-capacity baselines while maintaining 50% smaller model size compared to growing approaches. Specifically, we expect:
- Split CIFAR-100: >70% average accuracy with ≤8 experts (vs. 62% for fixed MoE)
- Permuted MNIST: >95% average accuracy with minimal forgetting (BWT > -0.05)
- CORe50: >80% accuracy across sessions with bounded capacity

**Efficiency**: The consolidation mechanism should reduce total parameters by 40-60% compared to naive expert addition while requiring only 10-15% additional computation for similarity metrics and merging operations during training.

**Adaptability**: The re-specialization mechanism should trigger 2-4 splits per 20-task sequence, demonstrating the system's ability to adapt its granularity to task complexity. We expect routing entropy to stabilize within 2-3 epochs after splits.

**Theoretical Insights**: Our analysis will establish:
1. Formal forgetting bounds as a function of merge similarity
2. Convergence guarantees for the dynamic expert allocation process
3. Capacity-performance trade-off characterization

### 3.2 Scientific Impact

This research advances multiple areas:

**Continual Learning Theory**: By formalizing the relationship between functional similarity and knowledge consolidation, we provide new theoretical tools for analyzing continual learning systems beyond parameter-space regularization.

**Model Merging**: DEC extends model merging from a one-time operation to a continual process, establishing principles for when and how to merge models in dynamic settings.

**Modular Architecture Design**: The dynamic consolidation framework provides design principles for truly adaptive modular systems, bridging static MoE architectures and continual learning requirements.

### 3.3 Practical Impact

**Edge Deployment**: Bounded model size enables deployment of continual learning systems on resource-constrained devices where indefinite growth is impossible.

**Personalized AI**: DEC enables efficient personalization where user-specific experts can be consolidated with general knowledge without maintaining separate large models per user.

**Long-running Systems**: Autonomous systems (robotics, recommendation engines) can learn continuously without periodic retraining or unbounded resource growth.

**Collaborative Learning**: The framework supports distributed scenarios where multiple institutions train experts that can be selectively merged, enabling privacy-preserving collaborative learning.

### 3.4 Broader Impact

**Sustainability**: By reducing unnecessary model growth and enabling knowledge reuse, DEC contributes to more environmentally sustainable AI development, potentially reducing energy consumption by 30-50% compared to retraining approaches.

**Democratization**: Bounded-capacity continual learning makes advanced AI more accessible to organizations with limited computational resources.

**Scientific Progress**: The open-source release of DEC will accelerate research in modular architectures, providing a flexible framework for exploring continual learning strategies.

### 3.5 Limitations and Future Directions

**Limitations**: DEC requires careful tuning of similarity thresholds and merge/split criteria. The effectiveness depends on the quality of functional similarity metrics, which may need task-specific calibration.

**Future Work**: 
1. Extend to heterogeneous experts with different architectures
2. Develop meta-learning approaches to automatically tune consolidation parameters
3. Explore theoretical connections to neural architecture search
4. Investigate applications to federated continual learning scenarios

This research establishes a new paradigm for sustainable continual learning through dynamic knowledge consolidation, with broad implications for building truly adaptive, long-lived AI systems.