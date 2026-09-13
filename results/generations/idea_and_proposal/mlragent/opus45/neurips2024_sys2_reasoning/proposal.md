# Research Proposal: Compositional Reasoning Probes: Detecting and Steering System-2 Emergence in Transformers

## 1. Introduction

### Background

The distinction between System-1 (fast, intuitive) and System-2 (slow, deliberate) reasoning, originally proposed in cognitive psychology, has become increasingly relevant to understanding the capabilities and limitations of large language models (LLMs). While modern transformers demonstrate remarkable performance across diverse tasks, fundamental questions remain about whether their success stems from genuine compositional reasoning—the ability to systematically combine learned rules to solve novel problems—or from sophisticated pattern matching over memorized training examples.

Recent research has illuminated this tension. Dziri et al. (2023) demonstrated that transformer success on compositional tasks largely arises from pattern memorization, with errors propagating exponentially as complexity increases. Press et al. (2023) introduced the "compositionality gap," showing that larger models memorize more factual knowledge without corresponding improvements in compositional reasoning. These findings challenge the assumption that scale alone will yield systematic reasoning capabilities, directly addressing the workshop's question about whether the "bitter lesson" will dictate AI's future.

The inability to distinguish memorization from rule-based composition has profound implications for AI safety. If models appear to follow rules but actually rely on memorized patterns, their behavior becomes unpredictable when encountering genuinely novel situations—precisely the scenarios where reliable reasoning is most critical. Furthermore, without interpretable signals of compositional processing, we cannot design training procedures that explicitly encourage System-2 mechanisms.

### Research Objectives

This proposal introduces **Compositional Reasoning Probes (CRPs)**—a novel framework for detecting, measuring, and actively steering compositional reasoning in transformers. Our objectives are threefold:

1. **Detection**: Develop lightweight diagnostic classifiers that operate on model internals (attention patterns, hidden states) to distinguish compositional processing from retrieval-based pattern matching in real-time.

2. **Measurement**: Establish quantitative metrics for compositional reasoning that avoid data contamination by construction, providing reliable benchmarks for System-2 generalization.

3. **Steering**: Utilize probe activations as reward signals within reinforcement learning frameworks to actively guide models toward compositional processing modes during training.

### Significance

This research addresses multiple core questions posed by the workshop. First, it provides empirical methodology to determine whether scale induces genuine compositional reasoning or merely broader memorization. Second, it offers a practical mechanism for implementing System-2 reasoning implicitly within models, as an alternative to external scaffolding like search or graph-of-thought. Third, by constructing synthetic tasks with known compositional structure, it establishes contamination-resistant benchmarks for System-2 generalization. Finally, the interpretable nature of linear probes contributes to AI safety by making model decision-making processes more transparent and predictable.

## 2. Methodology

### 2.1 Synthetic Task Construction

We construct a family of synthetic tasks with precisely controlled compositional structure, enabling definitive separation of novel compositions from memorizable patterns.

**Function Composition Tasks**: Define a set of primitive functions $\{f_1, f_2, ..., f_k\}$ operating on symbolic tokens. Training data contains compositions up to depth $d$, while evaluation requires compositions of depth $d+1$ or novel combinations of primitives never seen together during training.

Formally, let $\mathcal{F} = \{f_i: \Sigma \rightarrow \Sigma\}$ be primitive functions over alphabet $\Sigma$. Training examples are drawn from:

$$\mathcal{D}_{train} = \{(x, f_{i_n} \circ f_{i_{n-1}} \circ ... \circ f_{i_1}(x)) : n \leq d, (i_1, ..., i_n) \in \mathcal{C}_{seen}\}$$

where $\mathcal{C}_{seen}$ represents composition patterns observed during training. Evaluation sets include:

- **Depth Generalization**: $\mathcal{D}_{depth} = \{(x, f_{i_{d+1}} \circ ... \circ f_{i_1}(x))\}$
- **Compositional Generalization**: $\mathcal{D}_{comp} = \{(x, f_{i_n} \circ ... \circ f_{i_1}(x)) : (i_1, ..., i_n) \notin \mathcal{C}_{seen}\}$

**Nested Logical Operations**: Design tasks involving nested quantifiers and logical connectives where surface patterns are insufficient for correct solutions. For instance:

$$\phi = \forall x. \exists y. (P(x,y) \land Q(y)) \rightarrow R(x)$$

We systematically vary quantifier depth, predicate combinations, and logical structure to create distributions where memorization strategies fail.

**Random Hierarchy Model (RHM)**: Following Liu (2025), we employ RHM to generate hierarchically structured data where compositional rules are precisely specified, enabling ground-truth labeling of whether any given solution requires genuine composition.

### 2.2 Compositional Reasoning Probe Architecture

CRPs are linear classifiers trained to predict compositional engagement from model internals. We focus on linear probes for interpretability, following the principle that linearly decodable information reflects genuine model representations rather than artifacts of probe capacity.

**Feature Extraction**: For a transformer with $L$ layers and hidden dimension $h$, given input sequence of length $T$, we extract:

1. **Hidden State Features**: $H^{(l)} \in \mathbb{R}^{T \times h}$ at each layer $l$
2. **Attention Pattern Features**: $A^{(l)} \in \mathbb{R}^{n_h \times T \times T}$ where $n_h$ is the number of attention heads

We compute aggregated features through mean pooling and principal component projection:

$$z^{(l)}_{hidden} = \text{PCA}_k(\frac{1}{T}\sum_{t=1}^{T} H^{(l)}_t)$$

$$z^{(l)}_{attn} = \text{vec}(\frac{1}{n_h}\sum_{i=1}^{n_h} A^{(l)}_i)$$

**Probe Training**: For each layer $l$, we train a linear probe $p^{(l)}: \mathbb{R}^{k} \rightarrow [0,1]$:

$$p^{(l)}(z) = \sigma(W^{(l)} z + b^{(l)})$$

where the binary label indicates whether the model's solution required compositional generalization (determined by whether the input belongs to $\mathcal{D}_{comp}$ or $\mathcal{D}_{depth}$ and was solved correctly).

**Compositional Engagement Score**: The final CRP score aggregates layer-wise predictions:

$$\text{CRP}(x) = \sum_{l=1}^{L} \alpha_l \cdot p^{(l)}(z^{(l)})$$

where $\alpha_l$ are learned attention weights optimized on a validation set.

### 2.3 Training Procedure for Probes

**Data Labeling**: We create training data for probes using the following labeling scheme:

- **Positive (Compositional)**: Examples from $\mathcal{D}_{comp} \cup \mathcal{D}_{depth}$ that the model solves correctly
- **Negative (Retrieval)**: Examples from $\mathcal{D}_{train}$ that match memorizable patterns, plus incorrect solutions on compositional examples

This labeling captures the intuition that correct generalization to structurally novel examples requires compositional processing.

**Contrastive Learning Enhancement**: To improve probe discriminability, we employ contrastive pairs where the same abstract rule is applied to different surface forms:

$$\mathcal{L}_{contrastive} = -\log \frac{\exp(\text{sim}(z_i, z_j)/\tau)}{\sum_{k \neq i} \exp(\text{sim}(z_i, z_k)/\tau)}$$

where $(z_i, z_j)$ share compositional structure but differ superficially.

### 2.4 Reinforcement Learning with CRP Rewards

We integrate CRP activations into training to steer models toward compositional processing.

**Reward Formulation**: The reward function combines task accuracy with compositional engagement:

$$R(x, y, \hat{y}) = \mathbb{1}[\hat{y} = y] \cdot (1 + \lambda \cdot \text{CRP}(x))$$

where $\lambda$ controls the weight of the compositional bonus.

**Training Algorithm**: We employ Proximal Policy Optimization (PPO) with the modified reward:

$$\mathcal{L}_{PPO} = \mathbb{E}_t[\min(r_t(\theta)\hat{A}_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\hat{A}_t)]$$

where advantage estimates incorporate CRP-augmented rewards.

**Curriculum Strategy**: Training proceeds in phases:
1. **Phase 1**: Standard supervised learning on $\mathcal{D}_{train}$
2. **Phase 2**: PPO with CRP rewards on mixture of in-distribution and compositional examples
3. **Phase 3**: Progressive increase of compositional difficulty

### 2.5 Experimental Design

**Models**: We evaluate across model scales (125M to 7B parameters) using GPT-2, LLaMA, and Pythia families to assess scaling effects.

**Baselines**:
- Standard fine-tuning without CRP steering
- Chain-of-Thought prompting
- External scaffolding (Tree-of-Thought, Graph-of-Thought)
- ReasonFormer (Zhong et al., 2023)

**Evaluation Metrics**:
1. **Compositional Accuracy**: Performance on $\mathcal{D}_{comp}$ and $\mathcal{D}_{depth}$
2. **Compositionality Gap** (Press et al., 2023): Difference between sub-problem and full-problem accuracy
3. **CRP-Accuracy Correlation**: Spearman correlation between probe predictions and actual generalization success
4. **Probe Selectivity**: Area under ROC curve for distinguishing compositional from retrieval processing
5. **Scaling Behavior**: How metrics change with model size

**Ablation Studies**:
- Layer-wise probe contribution analysis
- Feature type comparison (attention vs. hidden states)
- Reward weight sensitivity ($\lambda$ variation)
- Effect of synthetic task complexity

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Quantitative Metrics**: We anticipate developing CRPs achieving >85% accuracy in distinguishing compositional from retrieval-based processing, validated through held-out structural generalizations. This provides the first real-time diagnostic for System-2 engagement.

**Training Procedures**: Models trained with CRP-guided reinforcement learning are expected to show 15-30% improvement on compositional generalization benchmarks while maintaining in-distribution performance, demonstrating that System-2 mechanisms can be explicitly incentivized.

**Scaling Insights**: We expect to provide definitive evidence on whether scale genuinely induces compositional reasoning. Preliminary hypotheses suggest that while larger models show higher raw accuracy, the CRP signatures may reveal that compositional processing itself does not increase proportionally—potentially validating concerns about memorization-driven scaling.

**Interpretable Evidence**: Layer-wise probe analysis will reveal which transformer components specialize for compositional reasoning, extending findings from Liu (2025) on layer specialization and informing architectural innovations.

### Broader Impact

**Benchmarking Solution**: By constructing tasks where compositional structure is known by design and evaluation sets are generated procedurally, CRPs provide contamination-resistant benchmarks—directly addressing the workshop's concern about reliable System-2 evaluation.

**Implicit vs. Explicit System-2**: This work provides a practical mechanism for implementing System-2 reasoning implicitly within models, offering an alternative to external scaffolding. The resulting models may achieve compositional reasoning without the computational overhead of search-based methods.

**AI Safety**: Interpretable probes that predict when models engage systematic reasoning contribute to AI safety by enabling:
- Real-time monitoring of reasoning modes during deployment
- Detection of potential failures before they manifest in outputs
- Principled trust calibration based on processing signatures

**Theoretical Contributions**: The framework connects empirical observations to theoretical questions about transformer expressivity (Kozachinskiy et al., 2025) and complexity control (Zhang et al., 2025), providing experimental testbeds for theoretical predictions.

### Limitations and Future Work

We acknowledge that synthetic tasks may not fully capture the complexity of natural language reasoning. Future work will extend CRPs to naturalistic benchmarks and explore whether probes trained on synthetic tasks transfer to real-world compositional reasoning. Additionally, the reliance on linear probes may miss non-linear compositional signatures, motivating investigation of more expressive probe architectures while maintaining interpretability.

In conclusion, Compositional Reasoning Probes offer a principled framework for detecting, measuring, and steering System-2 reasoning in transformers, addressing fundamental questions about the nature of neural network reasoning and providing practical tools for developing more reliable and interpretable AI systems.