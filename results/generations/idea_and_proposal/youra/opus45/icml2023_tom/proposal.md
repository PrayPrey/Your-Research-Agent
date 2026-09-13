# Research Proposal: Hierarchical Multi-Timescale Architecture for Depth-Scalable Theory of Mind Reasoning

## 1. Introduction

### 1.1 Background

Theory of Mind (ToM) represents a fundamental cognitive capacity enabling humans to attribute mental states—beliefs, desires, intentions, and knowledge—to themselves and others. This ability underpins virtually all sophisticated social interactions, from everyday conversations to complex negotiations. In computational systems, robust ToM capabilities are essential for developing AI agents that can effectively collaborate with humans, understand pragmatic communication, and navigate the nuanced landscape of social cognition.

Recent advances in large language models (LLMs) have demonstrated impressive performance across numerous natural language processing tasks. However, these models exhibit a critical limitation in higher-order ToM reasoning—the ability to process nested beliefs such as "Alice thinks that Bob believes that Carol knows the secret is hidden." Empirical studies on benchmarks like HI-TOM reveal that LLM accuracy degrades by approximately 10-15% for each additional level of belief nesting. This steep degradation fundamentally limits AI systems' capacity to model the recursive structure inherent in human social cognition.

Current approaches to improving ToM in language models fall into two categories: prompting-based methods (e.g., SimToM, Decompose-ToM) and architectural modifications. Prompting methods attempt to guide models through perspective-taking steps but remain constrained by the underlying flat transformer architecture. These approaches treat all reasoning uniformly regardless of depth complexity, lacking explicit mechanisms to track and maintain nested belief structures. The architectural mismatch between flat attention mechanisms and the inherently recursive nature of ToM reasoning represents a fundamental bottleneck.

### 1.2 Research Objectives

This research proposes HMT-ToM (Hierarchical Multi-Timescale Theory of Mind), a novel architecture designed to address the depth-scaling limitation in ToM reasoning. Our primary objectives are:

1. **Design and implement** a hierarchical multi-timescale architecture that explicitly separates meta-belief reasoning from belief-state computation through distinct processing modules operating at different temporal scales.

2. **Develop** a Linguistic Depth Detector (LDD) capable of identifying belief-introducing linguistic markers to trigger appropriate timescale transitions during processing.

3. **Evaluate** the architecture's effectiveness in reducing depth-scaling degradation on the HI-TOM benchmark, comparing against state-of-the-art baselines.

4. **Validate** the causal mechanism through systematic ablation studies, demonstrating that the architectural components contribute meaningfully to improved performance.

### 1.3 Significance

This research addresses a fundamental challenge at the intersection of cognitive science and artificial intelligence. Success would demonstrate that cognitively-inspired architectural constraints can overcome limitations that scaling alone cannot resolve. The implications extend beyond benchmark performance to practical applications in human-AI collaboration, dialogue systems, and social robotics where understanding nested mental states is crucial.

Furthermore, this work contributes to the broader scientific understanding of how computational architectures can embody cognitive principles. By explicitly modeling the recursive structure of ToM through timescale separation, we provide a testable computational theory of how hierarchical belief reasoning might be implemented in artificial systems.

## 2. Methodology

### 2.1 Architecture Design

The HMT-ToM architecture comprises three integrated components: a Linguistic Depth Detector (LDD), a Meta-Belief Module (slow timescale), and a Belief-State Module (fast timescale).

#### 2.1.1 Linguistic Depth Detector (LDD)

The LDD identifies belief-introducing verbs and constructions that signal transitions in belief depth. Given an input sequence $\mathbf{x} = (x_1, x_2, ..., x_n)$, the LDD produces depth transition signals:

$$d_t = \sigma(W_{ldd} \cdot h_t + b_{ldd})$$

where $h_t$ is the hidden representation at position $t$, $W_{ldd}$ and $b_{ldd}$ are learnable parameters, and $\sigma$ is the sigmoid function. The detector is trained to recognize belief-introducing verbs ("thinks," "believes," "knows," "assumes," "suspects") and their syntactic contexts.

For robustness, we implement a hybrid approach combining rule-based pattern matching with learned representations:

$$d_t^{final} = \alpha \cdot d_t^{rule} + (1-\alpha) \cdot d_t^{learned}$$

where $\alpha$ is a tunable hyperparameter balancing interpretability and flexibility.

#### 2.1.2 Meta-Belief Module (Slow Timescale)

The Meta-Belief Module maintains a belief stack representation $\mathbf{S} = [s_1, s_2, ..., s_k]$ where $k$ is the maximum depth (default: 5). This module operates at a slower timescale, updating only when the LDD detects depth transitions:

$$\mathbf{S}^{(t)} = \begin{cases} \text{PUSH}(\mathbf{S}^{(t-1)}, h_t^{meta}) & \text{if } d_t > \theta_{push} \\ \text{POP}(\mathbf{S}^{(t-1)}) & \text{if } d_t < \theta_{pop} \\ \mathbf{S}^{(t-1)} & \text{otherwise} \end{cases}$$

The meta-belief state is computed using a recurrent update with time constant $\tau_{slow}$:

$$h_t^{meta} = (1 - \frac{1}{\tau_{slow}}) \cdot h_{t-1}^{meta} + \frac{1}{\tau_{slow}} \cdot \tanh(W_{meta}[h_t; \mathbf{S}^{(t-1)}] + b_{meta})$$

where $\tau_{slow} \gg 1$ ensures slow integration of information, maintaining stable representations of nested belief structures.

#### 2.1.3 Belief-State Module (Fast Timescale)

The Belief-State Module computes concrete belief content at each depth level using filtered context from the Meta-Belief Module. It operates at a fast timescale with time constant $\tau_{fast} \approx 1$:

$$h_t^{belief} = (1 - \frac{1}{\tau_{fast}}) \cdot h_{t-1}^{belief} + \frac{1}{\tau_{fast}} \cdot \tanh(W_{belief}[h_t; c_t] + b_{belief})$$

The context vector $c_t$ is computed through cross-module attention:

$$c_t = \sum_{i=1}^{k} \alpha_i \cdot s_i, \quad \alpha_i = \text{softmax}(q_t^T K_S / \sqrt{d})$$

where $q_t$ is the query from the current position and $K_S$ are keys derived from the belief stack.

#### 2.1.4 Output Layer

The final ToM prediction combines information from both modules:

$$\mathbf{y} = \text{softmax}(W_{out}[h_T^{meta}; h_T^{belief}; \mathbf{S}^{(T)}] + b_{out})$$

### 2.2 Training Procedure

#### 2.2.1 Data Collection and Preprocessing

We utilize the HI-TOM benchmark (He et al., 2023), which provides Theory of Mind scenarios annotated with belief depth levels from 1st to 4th order. The dataset is split into training (70%), validation (15%), and test (15%) sets, stratified by depth level to ensure balanced representation.

Data preprocessing includes:
1. Tokenization using a standard subword tokenizer
2. Annotation of belief-introducing verb positions for LDD supervision
3. Generation of ground-truth depth transition sequences

#### 2.2.2 Multi-Task Training Objective

The model is trained with a combined loss function:

$$\mathcal{L} = \mathcal{L}_{ToM} + \lambda_1 \mathcal{L}_{LDD} + \lambda_2 \mathcal{L}_{stack}$$

where:
- $\mathcal{L}_{ToM}$ is the cross-entropy loss for ToM question answering
- $\mathcal{L}_{LDD}$ is the binary cross-entropy loss for depth transition detection
- $\mathcal{L}_{stack}$ is an auxiliary loss encouraging proper stack operations

The hyperparameters $\lambda_1 = 0.3$ and $\lambda_2 = 0.1$ are determined through validation set performance.

#### 2.2.3 Training Configuration

- **Model size**: ~27M parameters (following HRM precedent for parameter efficiency)
- **Optimizer**: AdamW with learning rate $3 \times 10^{-4}$, weight decay 0.01
- **Batch size**: 32
- **Training epochs**: 50 with early stopping (patience: 5 epochs)
- **Timescale parameters**: $\tau_{slow} = 10$, $\tau_{fast} = 1$

### 2.3 Experimental Design

#### 2.3.1 Baseline Comparisons

We compare HMT-ToM against the following baselines:

1. **Flat Transformer**: Standard transformer architecture with equivalent parameter count (~27M)
2. **SimToM** (Wilf et al., 2023): Prompting-based perspective-taking approach
3. **Decompose-ToM**: Chain-of-thought prompting for ToM decomposition
4. **ToM-LM**: Fine-tuned language model baseline
5. **Large-scale LLMs**: GPT-4, Claude-3 for reference (not direct comparison due to scale difference)

#### 2.3.2 Evaluation Metrics

**Primary Metrics:**

1. **Depth-Scaling Slope**: Linear regression coefficient of accuracy vs. depth level
   $$\text{slope} = \frac{\sum_{d=1}^{4}(d - \bar{d})(acc_d - \overline{acc})}{\sum_{d=1}^{4}(d - \bar{d})^2}$$

2. **Per-Depth Accuracy**: Accuracy at each belief depth level (1st through 4th order)

3. **Overall ToM Accuracy**: Macro-averaged accuracy across all depth levels

**Secondary Metrics:**

4. **LDD Precision/Recall**: Performance of depth transition detection
5. **Parameter Efficiency Ratio**: Accuracy per million parameters
6. **Inference Latency**: Time per sample (milliseconds)

#### 2.3.3 Statistical Analysis

- **Sample size**: n = 20 independent training runs per condition
- **Statistical tests**: Mixed ANOVA (Architecture × Depth Level) with Bonferroni-corrected post-hoc comparisons
- **Significance level**: α = 0.05
- **Effect size reporting**: Cohen's d for pairwise comparisons, η² for ANOVA effects
- **Confidence intervals**: 95% CI for all reported metrics

#### 2.3.4 Ablation Studies

To validate the causal mechanism, we conduct systematic ablations:

| Ablation | Modification | Expected Effect |
|----------|--------------|-----------------|
| A1: No LDD | Random depth signals | Degraded depth-scaling |
| A2: No Slow Module | Single timescale | Loss of hierarchical tracking |
| A3: No Stack | Remove belief stack | Impaired nested belief maintenance |
| A4: No Cross-Attention | Remove context filtering | Reduced perspective-taking |

Each ablation tests a specific component of the proposed causal mechanism.

#### 2.3.5 Generalization Tests

Beyond HI-TOM, we evaluate on:
1. **ToMi** (Le et al., 2019): Alternative ToM benchmark
2. **FANToM** (Kim et al., 2023): False belief understanding
3. **Synthetic depth extension**: Generated scenarios with 5th-6th order beliefs

### 2.4 Implementation Details

The architecture is implemented in PyTorch with the following specifications:

```
Embedding dimension: 256
Number of attention heads: 8
Meta-module layers: 2
Belief-state module layers: 4
Maximum sequence length: 512
Maximum belief depth (stack size): 5
Dropout rate: 0.1
```

Training is conducted on 4× NVIDIA A100 GPUs with mixed-precision (FP16) training. Expected training time is approximately 8 hours for the full model.

## 3. Expected Outcomes & Impact

### 3.1 Primary Expected Outcomes

**Outcome 1: Reduced Depth-Scaling Degradation**

We hypothesize that HMT-ToM will achieve a depth-scaling slope of approximately -3% to -5% per depth level, compared to the -10% to -15% observed in flat transformer baselines. This represents a ≥50% reduction in degradation rate.

Quantitative predictions:
- 1st-order accuracy: ~92% (comparable to baselines)
- 2nd-order accuracy: ~88% (vs. ~80% baseline)
- 3rd-order accuracy: ~84% (vs. ~68% baseline)
- 4th-order accuracy: ~80% (vs. ~55% baseline)

**Outcome 2: Validated Causal Mechanism**

Ablation studies will demonstrate that each architectural component contributes meaningfully:
- LDD ablation: Expected 15-20% increase in depth-scaling slope
- Slow module ablation: Expected 25-30% increase in depth-scaling slope
- Full ablation (single timescale): Performance equivalent to flat transformer baseline

**Outcome 3: Parameter Efficiency**

HMT-ToM with ~27M parameters is expected to match or exceed the 3rd and 4th order ToM accuracy of flat transformers with 270M+ parameters, demonstrating 10× parameter efficiency for higher-order reasoning.

### 3.2 Broader Impact

**Scientific Contributions:**

1. **Cognitive-Computational Bridge**: This work provides empirical evidence that cognitively-inspired architectural constraints can address limitations in AI social reasoning that scaling alone cannot resolve.

2. **Architectural Principles**: The multi-timescale separation principle may generalize to other recursive reasoning tasks beyond ToM, including planning, causal reasoning, and pragmatic inference.

3. **Benchmark Insights**: Detailed analysis of depth-scaling behavior will inform future benchmark design and evaluation protocols for social cognition in AI.

**Practical Applications:**

1. **Human-AI Collaboration**: Improved ToM capabilities enable more natural and effective collaboration between humans and AI systems, particularly in scenarios requiring understanding of nested intentions.

2. **Dialogue Systems**: Conversational agents with robust higher-order ToM can better model user beliefs and expectations, leading to more coherent and contextually appropriate responses.

3. **Educational Technology**: AI tutors capable of modeling student mental states at multiple levels can provide more personalized and effective instruction.

4. **Social Robotics**: Robots operating in human environments require sophisticated ToM for safe and effective interaction.

### 3.3 Limitations and Future Directions

**Acknowledged Limitations:**

1. The current approach focuses on explicit, text-based belief statements and may not generalize to implicit ToM scenarios.
2. The fixed stack size imposes an upper bound on belief depth.
3. Cross-cultural and multilingual generalization remains untested.

**Future Research Directions:**

1. Extension to multimodal ToM incorporating visual and embodied cues
2. Integration with large language models as a plug-in module
3. Application to real-time dialogue systems with latency constraints
4. Investigation of developmental trajectories in ToM acquisition

### 3.4 Conclusion

This research proposal presents HMT-ToM, a hierarchical multi-timescale architecture designed to address the fundamental limitation of depth-scaling degradation in Theory of Mind reasoning. By explicitly separating meta-belief reasoning from belief-state computation and implementing a Linguistic Depth Detector to trigger timescale transitions, we hypothesize significant improvements in higher-order ToM accuracy with parameter-efficient models. Success in this endeavor would advance both our scientific understanding of computational social cognition and the practical capabilities of AI systems operating in human social environments.