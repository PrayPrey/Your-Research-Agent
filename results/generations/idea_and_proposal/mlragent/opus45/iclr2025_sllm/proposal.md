# Research Proposal: Sparse Expert Activation via Interpretable Routing: Unifying MoE Efficiency with Mechanistic Understanding

## 1. Introduction

### Background

Large Language Models (LLMs) have revolutionized artificial intelligence, demonstrating remarkable capabilities across diverse tasks from code generation to complex reasoning. However, their computational demands during inference present significant challenges for deployment at scale. Mixture of Experts (MoE) architectures have emerged as a promising solution, enabling models to scale parameters while maintaining computational efficiency through sparse expert activation—typically activating only 1-2 experts per token from a pool of dozens or hundreds.

Despite their efficiency benefits, MoE models suffer from a fundamental limitation: their routing mechanisms operate as opaque "black boxes." Traditional gating networks learn to distribute tokens across experts through end-to-end training, but the resulting routing decisions lack interpretability. Practitioners cannot easily understand why specific experts activate for particular inputs, hindering debugging, model editing, and trustworthy deployment.

Concurrently, the field of mechanistic interpretability has made substantial progress through Sparse Autoencoders (SAEs). Recent work by Cunningham et al. (2023) demonstrated that SAEs can extract monosemantic, interpretable features from language model activations, addressing the polysemanticity problem where individual neurons encode multiple unrelated concepts. These interpretable feature dictionaries provide a principled vocabulary for describing neural network computations.

Currently, these two research directions—MoE efficiency and SAE-based interpretability—operate largely independently. This separation represents a missed opportunity: the interpretable features discovered by SAEs could serve as semantically meaningful routing signals for expert activation, potentially improving both efficiency and transparency simultaneously.

### Research Objectives

This research proposes **Interpretable Sparse Routing (ISR)**, a novel framework that bridges MoE efficiency with mechanistic interpretability by replacing traditional learned gating networks with SAE-derived feature activations. Our specific objectives are:

1. **Develop a methodology** for training SAEs on MoE intermediate representations and associating experts with interpretable feature subsets based on specialization analysis.

2. **Design and implement** an ISR architecture where sparse feature activations directly determine expert routing, eliminating opaque gating mechanisms.

3. **Empirically validate** that ISR achieves comparable or improved performance while providing transparent, semantically meaningful expert assignments.

4. **Demonstrate practical applications** including targeted model editing, expert pruning based on semantic overlap, and dynamic expert composition for specific tasks.

### Significance

This research addresses multiple key challenges identified in the literature. First, it tackles the opacity of routing mechanisms by grounding expert activation in interpretable features. Second, it leverages SAEs' ability to extract monosemantic features to resolve polysemanticity concerns in routing decisions. Third, it provides a principled framework for analyzing and controlling expert specialization. The proposed approach aligns with recent work on interpretable MoE architectures (MoE-X, ERMoE, SRA) while introducing a novel SAE-based perspective that enables deeper mechanistic understanding.

## 2. Methodology

### 2.1 Overview

Our methodology consists of four main phases: (1) SAE training for interpretable feature extraction, (2) expert-feature association analysis, (3) ISR architecture design and training, and (4) comprehensive experimental validation.

### 2.2 Phase 1: Sparse Autoencoder Training

We train SAEs on the intermediate representations immediately preceding MoE layers to extract interpretable feature dictionaries. Given an input activation $\mathbf{h} \in \mathbb{R}^d$ at an MoE layer, the SAE learns an encoding function:

$$\mathbf{f} = \text{ReLU}(\mathbf{W}_{\text{enc}}(\mathbf{h} - \mathbf{b}_{\text{dec}}) + \mathbf{b}_{\text{enc}})$$

where $\mathbf{W}_{\text{enc}} \in \mathbb{R}^{m \times d}$ projects to a higher-dimensional sparse feature space ($m \gg d$, typically $m = 8d$ to $32d$), and a corresponding decoder:

$$\hat{\mathbf{h}} = \mathbf{W}_{\text{dec}}\mathbf{f} + \mathbf{b}_{\text{dec}}$$

The training objective combines reconstruction fidelity with sparsity:

$$\mathcal{L}_{\text{SAE}} = \|\mathbf{h} - \hat{\mathbf{h}}\|_2^2 + \lambda \|\mathbf{f}\|_1$$

where $\lambda$ controls the sparsity-reconstruction trade-off. We employ the TopK variant where only the top-$k$ feature activations are retained:

$$\mathbf{f}^{\text{sparse}} = \text{TopK}(\mathbf{f}, k)$$

Following best practices, we normalize decoder columns to unit norm and use auxiliary losses to encourage feature utilization and prevent dead features.

### 2.3 Phase 2: Expert-Feature Association Analysis

With trained SAEs, we analyze the relationship between interpretable features and expert utilization in a pretrained MoE model. For each expert $e_j$ and feature $f_i$, we compute the conditional activation probability:

$$P(e_j | f_i > \tau) = \frac{\sum_{t} \mathbb{1}[f_i^{(t)} > \tau] \cdot \mathbb{1}[e_j \text{ selected for } t]}{\sum_{t} \mathbb{1}[f_i^{(t)} > \tau]}$$

where $t$ indexes tokens and $\tau$ is an activation threshold. We construct an affinity matrix $\mathbf{A} \in \mathbb{R}^{E \times m}$ where $E$ is the number of experts:

$$A_{ji} = P(e_j | f_i > \tau) - P(e_j)$$

This matrix captures how strongly each feature is associated with each expert beyond baseline selection probability. We apply spectral clustering on $\mathbf{A}$ to identify natural feature-expert groupings and compute expert specialization scores:

$$S_j = \frac{1}{|\mathcal{F}_j|} \sum_{i \in \mathcal{F}_j} A_{ji}$$

where $\mathcal{F}_j$ denotes the feature set most associated with expert $j$.

### 2.4 Phase 3: Interpretable Sparse Routing Architecture

Based on the association analysis, we design the ISR routing mechanism. Given input $\mathbf{h}$, we first compute sparse features $\mathbf{f}^{\text{sparse}}$ using the trained SAE encoder. The routing score for expert $j$ is computed as:

$$r_j = \sum_{i=1}^{m} w_{ji} \cdot f_i^{\text{sparse}}$$

where $\mathbf{W}_{\text{route}} \in \mathbb{R}^{E \times m}$ is initialized from the normalized affinity matrix and can be optionally fine-tuned. Expert selection follows standard top-$k$ routing:

$$\text{Selected Experts} = \text{TopK}(\{r_1, ..., r_E\}, k_{\text{exp}})$$

The final output combines selected expert outputs weighted by normalized routing scores:

$$\mathbf{y} = \sum_{j \in \text{Selected}} \frac{\exp(r_j)}{\sum_{j' \in \text{Selected}} \exp(r_{j'})} \cdot e_j(\mathbf{h})$$

**Training Procedure**: We propose two training variants:

1. **ISR-Frozen**: Initialize from pretrained MoE, replace gating with ISR using frozen $\mathbf{W}_{\text{route}}$ derived from association analysis, and fine-tune only expert weights.

2. **ISR-Learned**: Allow $\mathbf{W}_{\text{route}}$ to be fine-tuned with an interpretability regularization term:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{task}} + \alpha \|\mathbf{W}_{\text{route}} - \mathbf{W}_{\text{route}}^{\text{init}}\|_F^2 + \beta \mathcal{L}_{\text{sparsity}}$$

where $\mathcal{L}_{\text{sparsity}}$ encourages sparse expert activation patterns.

### 2.5 Phase 4: Experimental Design

**Datasets and Models**: We conduct experiments on multiple scales:
- Small-scale: Phi-MoE (2.7B parameters, 16 experts)
- Medium-scale: Mixtral-8x7B
- Validation datasets: The Pile (pretraining distribution), MMLU, GSM8K, HumanEval, and domain-specific benchmarks

**Baselines**:
1. Original MoE with learned gating
2. MoE-X (interpretable MoE baseline)
3. ERMoE (eigenbasis routing)
4. SRA (semantic resonance routing)

**Evaluation Metrics**:

*Performance Metrics*:
- Perplexity on held-out text
- Accuracy on downstream tasks (MMLU, GSM8K, HumanEval)
- Inference latency and throughput

*Efficiency Metrics*:
- Average expert activation rate
- Expert utilization balance (Gini coefficient across experts)
- FLOPs per token

*Interpretability Metrics*:
- Feature interpretability score: Human evaluation of feature-expert associations
- Routing consistency: Correlation between semantically similar inputs and expert selection
- Intervention success rate: Accuracy of predictions when editing specific features

**Ablation Studies**:
1. SAE dictionary size ($m$) impact on routing quality
2. Sparsity level ($k$) in SAE features
3. Number of experts per token ($k_{\text{exp}}$)
4. Fine-tuning vs. frozen routing weights

**Interpretability Case Studies**:
1. **Expert Semantic Profiling**: Characterize each expert's specialization using top-associated interpretable features
2. **Targeted Model Editing**: Demonstrate ability to suppress or enhance specific expert activation by manipulating feature signals
3. **Expert Pruning**: Remove experts with high semantic overlap and measure performance impact
4. **Task-Specific Expert Composition**: Show dynamic expert selection for different task categories

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Technical Contributions**:
1. A novel ISR framework demonstrating that SAE-derived features can effectively replace learned gating mechanisms in MoE models, achieving comparable task performance (within 1-2% on benchmarks) while providing transparent routing decisions.

2. Empirical evidence of improved efficiency through semantically-grounded routing, with expected 10-20% reduction in unnecessary expert activations compared to baseline gating.

3. Comprehensive analysis of expert specialization patterns, revealing interpretable taxonomies of expert functionality (e.g., "syntax expert," "factual knowledge expert," "reasoning expert").

4. Validated methodology for expert pruning and merging based on semantic overlap, enabling more compact MoE deployments without arbitrary performance thresholds.

**Practical Artifacts**:
- Open-source implementation of ISR for popular MoE architectures
- Pretrained SAE dictionaries for Mixtral and Phi-MoE
- Visualization tools for exploring expert-feature associations

### Research Impact

**Bridging Efficiency and Interpretability**: This work demonstrates that efficiency and interpretability are not competing objectives but can be synergistically pursued through principled integration of SAEs and MoE architectures. This challenges the prevailing assumption that understanding must be sacrificed for performance.

**Enabling Trustworthy Deployment**: By making routing decisions transparent and controllable, ISR enables practitioners to audit model behavior, identify potential biases in expert utilization, and make informed decisions about model deployment in sensitive applications.

**Foundation for Future Research**: The ISR framework opens several research directions:
- Hierarchical interpretable routing for very large expert pools
- Online adaptation of routing based on deployment feedback
- Cross-model transfer of interpretable routing patterns

**Workshop Relevance**: This proposal directly addresses the workshop's goal of "fostering connections and unlocking synergies between traditionally independent yet highly related research areas" by explicitly bridging MoE efficiency with SAE-based interpretability. It demonstrates how sparsity serves as a "unifying framework" across efficiency, interpretability, and modularity dimensions.

### Broader Impact

The proposed research contributes to more accessible and environmentally sustainable AI by potentially reducing computational waste from suboptimal expert activation. More importantly, it advances the broader goal of building AI systems that humans can understand and control—a critical requirement as LLMs are deployed in increasingly consequential applications. By grounding expert specialization in interpretable features, ISR provides a path toward modular, auditable, and editable language models that align with principles of responsible AI development.