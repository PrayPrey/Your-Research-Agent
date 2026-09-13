# Research Proposal: Hierarchical Decomposition Representation Learning (HDRL) for Compositional Generalization in Instruction-Following LLMs

## 1. Introduction

### 1.1 Background

Large language models (LLMs) have achieved remarkable success in following natural language instructions across diverse tasks, from question answering to code generation. This capability, primarily enabled through instruction tuning—fine-tuning on datasets of instruction-response pairs—has transformed LLMs into versatile assistants capable of understanding and executing open-ended language commands. Industrial models like GPT-4 and open-source alternatives have demonstrated impressive performance on standard benchmarks, driving widespread adoption across applications.

However, a fundamental limitation persists: LLMs struggle with **compositional generalization**—the ability to execute novel combinations of known instructions or generalize to longer, more complex instruction sequences than those seen during training. For instance, a model trained on instructions like "translate to French" and "summarize the text" may fail when asked to "translate to French and then summarize," despite understanding each component individually. This limitation is particularly evident in systematic generalization benchmarks like SCAN, where models trained on shorter command sequences fail catastrophically on longer sequences, achieving as low as 16% accuracy on length splits.

Current approaches to address this limitation primarily operate at inference time. Chain-of-Thought (CoT) prompting encourages models to decompose complex problems into intermediate steps, while Least-to-Most prompting explicitly guides models through hierarchical problem decomposition. While these methods achieve strong results—Least-to-Most prompting reaches 99% on SCAN—they require verbose prompting, increase inference costs, and critically, do not address the underlying representation problem. The model's internal representations remain unchanged; decomposition is externally imposed rather than internally learned.

Recent theoretical work by Li (2025) provides crucial insight into this problem, proving that for a model to achieve compositional generalization, its computational graph must match the compositional structure of the task. This theoretical requirement suggests that the solution lies not in inference-time interventions but in fundamentally restructuring how models internally represent compositional tasks.

### 1.2 Research Objectives

This research proposes **Hierarchical Decomposition Representation Learning (HDRL)**, a novel training objective that supervises hidden states to encode hierarchical sub-task structure derived from Chain-of-Thought annotations. Our primary objectives are:

1. **Develop the HDRL training framework** that combines standard instruction tuning with auxiliary contrastive losses designed to create hierarchical structure in hidden state representations.

2. **Validate the causal mechanism** linking representation-level supervision to improved compositional generalization through systematic probing and ablation studies.

3. **Demonstrate practical benefits** including improved accuracy on compositional generalization benchmarks and reduced inference costs compared to prompting-based methods.

### 1.3 Research Significance

This research addresses a fundamental gap between inference-time decomposition techniques and representation-level learning. While prompting methods demonstrate that decomposition enables compositional generalization, they do not teach models to internalize this capability. HDRL bridges this gap by supervising internal representations to encode the hierarchical structure that theoretical work identifies as necessary for generalization.

The significance extends beyond benchmark improvements. If successful, HDRL establishes representation-level supervision as a principled approach to compositional generalization, complementing rather than replacing inference-time techniques. This has implications for building more robust instruction-following systems that can handle novel instruction combinations without explicit decomposition prompts, reducing inference costs and improving reliability in deployment scenarios.

## 2. Methodology

### 2.1 Overview

HDRL operates through a three-step causal mechanism: (1) contrastive loss clusters related sub-task representations while separating unrelated ones, (2) this creates decomposition-aware internal processing with graded activation patterns, and (3) aligned computational graphs enable compositional generalization per theoretical requirements. We detail each component below.

### 2.2 Data Collection and Preprocessing

**Source Datasets:** We utilize existing Chain-of-Thought annotated datasets including FLAN-CoT and GSM8K-CoT, totaling approximately 100,000 examples with explicit reasoning chains.

**Auto-Parsing Decomposition Annotations:** We develop an automated pipeline to extract hierarchical sub-task structure from CoT annotations:

1. **Step Segmentation:** Parse CoT responses into discrete reasoning steps using delimiter patterns (e.g., "Step 1:", "First,", numbered lists) and semantic boundaries detected via sentence embeddings.

2. **Dependency Extraction:** Identify dependencies between steps through:
   - Explicit references (e.g., "Using the result from step 2...")
   - Variable tracking (entities introduced in one step and referenced in subsequent steps)
   - Temporal markers indicating sequential dependencies

3. **Hierarchy Construction:** Build a directed acyclic graph (DAG) representing the sub-task hierarchy, where nodes are reasoning steps and edges represent dependencies.

For each training example, we obtain:
- Original instruction $I$
- Sequence of sub-tasks $S = \{s_1, s_2, ..., s_k\}$
- Dependency structure $D$ encoding relationships between sub-tasks
- Final response $R$

### 2.3 HDRL Training Objective

The complete training objective combines three loss components:

$$L_{total} = L_{instruction} + \lambda_1 \cdot L_{HDRL} + \lambda_2 \cdot L_{probe}$$

where $\lambda_1 \in [0.1, 1.0]$ and $\lambda_2 \in [0.01, 0.1]$ are hyperparameters controlling the contribution of each auxiliary loss.

**Component 1: Standard Instruction Loss ($L_{instruction}$)**

The standard autoregressive language modeling loss on instruction-response pairs:

$$L_{instruction} = -\sum_{t=1}^{T} \log P(y_t | y_{<t}, I; \theta)$$

where $y_t$ is the $t$-th token of the response and $\theta$ represents model parameters.

**Component 2: HDRL Contrastive Loss ($L_{HDRL}$)**

The core HDRL objective supervises hidden states to encode hierarchical sub-task structure through contrastive learning. For a given instruction with sub-tasks $S = \{s_1, ..., s_k\}$, we extract hidden state representations at layer $l$ corresponding to each sub-task:

$$h_i^{(l)} = \text{MeanPool}(H^{(l)}[t_{start}^i : t_{end}^i])$$

where $H^{(l)}$ is the hidden state matrix at layer $l$, and $t_{start}^i, t_{end}^i$ denote the token positions corresponding to sub-task $s_i$.

The contrastive loss follows an InfoNCE formulation with structure-aware positive/negative sampling:

$$L_{HDRL} = -\sum_{i=1}^{k} \log \frac{\sum_{j \in \mathcal{P}(i)} \exp(\text{sim}(h_i, h_j) / \tau)}{\sum_{j \in \mathcal{P}(i)} \exp(\text{sim}(h_i, h_j) / \tau) + \sum_{n \in \mathcal{N}(i)} \exp(\text{sim}(h_i, h_n) / \tau)}$$

where:
- $\text{sim}(h_i, h_j) = \frac{h_i^\top h_j}{\|h_i\| \|h_j\|}$ is cosine similarity
- $\tau$ is a temperature parameter (default 0.07)
- $\mathcal{P}(i)$ is the set of positive samples for sub-task $i$: sub-tasks from the same instruction or semantically similar sub-tasks from other instructions (determined by sub-task type clustering)
- $\mathcal{N}(i)$ is the set of negative samples: sub-tasks from different instructions with different semantic types

**Hierarchical Structure Encoding:** To encode the hierarchical dependency structure $D$, we introduce an additional ordering loss:

$$L_{order} = \sum_{(i,j) \in D} \max(0, \text{sim}(h_i, h_{root}) - \text{sim}(h_j, h_{root}) + \gamma)$$

where $(i,j) \in D$ indicates that sub-task $i$ is a parent of sub-task $j$ in the dependency graph, $h_{root}$ is the representation of the root instruction, and $\gamma$ is a margin hyperparameter. This loss encourages parent sub-tasks to be closer to the root instruction representation than their children, encoding hierarchical depth.

**Component 3: Behavioral Probe Loss ($L_{probe}$)**

To ensure that hierarchical representations translate to behavioral capabilities, we include an auxiliary probe loss:

$$L_{probe} = -\sum_{i=1}^{k} \log P(s_i^{type} | h_i; \phi)$$

where $s_i^{type}$ is the sub-task type label (e.g., "arithmetic operation," "text transformation," "logical reasoning") and $\phi$ are parameters of a lightweight probe network (2-layer MLP). This loss encourages hidden states to encode sub-task identity in a linearly separable manner.

### 2.4 Model Architecture and Training

**Base Model:** LLaMA-7B, chosen for its strong baseline performance and accessibility for research.

**Layer Selection:** We apply HDRL supervision to layers in the middle-to-upper range (layers 16-24 of 32), based on prior work showing that these layers encode more abstract, task-relevant information while earlier layers focus on syntactic processing.

**Training Configuration:**
- Optimizer: AdamW with $\beta_1=0.9$, $\beta_2=0.999$
- Learning rate: $2 \times 10^{-5}$ with cosine decay
- Batch size: 32 (with gradient accumulation)
- Training steps: 50,000
- Warmup: 1,000 steps
- Loss weights: $\lambda_1 = 0.5$, $\lambda_2 = 0.05$ (tuned via validation)

**Computational Overhead:** HDRL introduces approximately 20% additional compute during training due to the contrastive loss computation and probe forward passes.

### 2.5 Experimental Design

**Experiment 1: Compositional Generalization Benchmarks**

*Datasets:*
- **SCAN Length Splits:** Training on commands up to length 22, testing on lengths 23-48. This tests systematic generalization to longer command sequences.
- **Chain-of-Instructions (CoI):** A custom benchmark where we construct novel instruction chains by combining atomic instructions from the training set in unseen combinations.

*Baselines:*
- Standard instruction-tuned LLaMA-7B
- LLaMA-7B with Chain-of-Thought prompting
- LLaMA-7B with Least-to-Most prompting
- LLaMA-7B with standard contrastive learning (without hierarchical structure)

*Metrics:*
- Exact match accuracy on SCAN
- Success rate on CoI (percentage of correctly executed instruction chains)
- Accuracy stratified by composition complexity (number of sub-tasks)

**Experiment 2: Probing Analysis**

*Objective:* Verify that HDRL creates hierarchical structure in hidden states.

*Method:* Train linear probes on frozen hidden states to predict:
- Sub-task type (classification accuracy)
- Sub-task position in hierarchy (ordinal regression)
- Dependency relationships between sub-tasks (binary classification)

*Metrics:*
- Probing accuracy for each prediction task
- Comparison between HDRL-trained and baseline models
- Layer-wise analysis of where hierarchical information is encoded

**Experiment 3: Ablation Studies**

*Ablations:*
- Remove $L_{HDRL}$: Standard instruction tuning + probe loss only
- Remove $L_{order}$: Contrastive loss without hierarchical ordering
- Remove $L_{probe}$: HDRL without behavioral probe
- Vary $\lambda_1$: Test sensitivity to HDRL loss weight
- Vary layer selection: Apply HDRL to different layer ranges

**Experiment 4: Efficiency Analysis**

*Objective:* Quantify inference efficiency gains over prompting-based methods.

*Metrics:*
- Average tokens generated per task (HDRL vs. Least-to-Most prompting)
- Inference latency comparison
- Performance-efficiency Pareto frontier

### 2.6 Statistical Analysis

All experiments use $n \geq 25$ independent runs with different random seeds. We report:
- Mean and standard deviation for all metrics
- 95% confidence intervals
- Paired t-tests for baseline comparisons ($\alpha = 0.05$, one-tailed)
- Cohen's d effect size (target: $d > 0.8$ for primary predictions)

**Falsification Criteria:**
1. SCAN accuracy $\leq 25\%$: Reject hypothesis (no meaningful improvement)
2. Probing accuracy $< 60\%$: Reject mechanism (no hierarchical structure formed)
3. Good probing ($>70\%$) but downstream accuracy $< 50\%$: Reject transfer assumption

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Prediction (P1):** HDRL-trained models achieve $>90\%$ accuracy on SCAN length splits, compared to $\sim16\%$ for standard instruction-tuned baselines. This represents a fundamental improvement in compositional generalization, approaching the 99% achieved by Least-to-Most prompting but without requiring explicit decomposition prompts at inference time.

**Secondary Prediction (P2):** Probing accuracy for sub-task identification exceeds 70%, compared to $<50\%$ for baseline models. This validates that HDRL successfully creates hierarchical structure in hidden state representations.

**Secondary Prediction (P3):** HDRL achieves 50-70% reduction in inference tokens compared to Least-to-Most prompting while maintaining comparable accuracy. This demonstrates practical efficiency benefits of internalized decomposition.

### 3.2 Scientific Impact

This research establishes **representation-level supervision** as a principled approach to compositional generalization, providing empirical validation for theoretical predictions about the relationship between computational graph structure and generalization capability. The work bridges the gap between inference-time decomposition techniques and learned representations, demonstrating that models can internalize hierarchical task structure rather than relying on external scaffolding.

The probing analysis contributes to interpretability research by characterizing how hierarchical information is encoded across transformer layers, potentially informing future architectural innovations.

### 3.3 Practical Impact

**Reduced Inference Costs:** By internalizing decomposition capabilities, HDRL-trained models require fewer tokens at inference time, reducing computational costs and latency in deployment scenarios.

**Improved Robustness:** Models with internalized hierarchical representations may be more robust to prompt variations and less dependent on carefully crafted decomposition prompts.

**Foundation for Future Work:** The HDRL framework provides a template for supervising other structural properties in hidden states, potentially extending to temporal reasoning, causal understanding, and multi-step planning.

### 3.4 Limitations and Future Directions

HDRL requires Chain-of-Thought annotated data with parseable decomposition structure, limiting applicability to domains where such data is available or can be synthesized. Future work should explore self-supervised approaches to discovering hierarchical structure without explicit annotations.

The 20% training compute overhead may be prohibitive for very large models; investigating more efficient contrastive learning formulations is an important direction. Additionally, extending HDRL to multimodal settings—where compositional generalization is equally challenging—represents a promising avenue for future research.