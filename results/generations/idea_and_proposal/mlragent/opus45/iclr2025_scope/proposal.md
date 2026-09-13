# Research Proposal: Dynamic KV Cache Compression via Learned Query-Aware Retention Policies

## 1. Introduction

### Background

The rapid advancement of foundation models has enabled unprecedented capabilities in natural language understanding, generation, and reasoning. However, as these models are deployed to handle increasingly longer contexts—spanning tens of thousands to millions of tokens—a critical computational bottleneck has emerged: the Key-Value (KV) cache. During autoregressive generation, transformers store key and value representations from all previous tokens, resulting in memory consumption that grows linearly with sequence length. For a model like LLaMA-70B processing 100K tokens, the KV cache alone can exceed 40GB of GPU memory, severely limiting deployment on memory-constrained devices and reducing inference throughput.

Current approaches to KV cache management fall into two unsatisfactory extremes. Static compression methods—including uniform quantization, fixed-window eviction, or predetermined sparsity patterns—apply identical compression strategies regardless of content, inevitably discarding information that proves crucial for subsequent queries. Conversely, full retention strategies maintain complete KV caches, incurring prohibitive memory costs that scale poorly with context length. This tension is particularly acute in emerging application scenarios: continual learning systems that must integrate streaming information, retrieval-augmented generation (RAG) pipelines that inject external knowledge into conversation history, and long-document understanding tasks requiring holistic reasoning across extensive contexts.

Recent work has made significant progress on KV cache compression. FAEDKV leverages frequency-domain transformations for unbiased compression, while KVzip introduces context reconstruction for importance quantification. GEAR combines quantization with low-rank approximation, and xKV exploits cross-layer redundancy through shared SVD subspaces. However, these methods largely operate in a query-agnostic manner, compressing the cache before knowing what information future queries will require. This fundamental limitation means they cannot adapt to the semantic demands of downstream tasks.

### Research Objectives

This research proposes **Dynamic KV Cache Compression via Learned Query-Aware Retention Policies (QARP)**, a novel framework that learns to predict which KV entries will be most relevant to future queries and allocates compression resources accordingly. Our specific objectives are:

1. **Design a lightweight Relevance Predictor Network** that scores KV entries based on learned query prototypes, enabling anticipatory importance estimation without access to actual future queries.

2. **Develop an Adaptive Retention Policy** that implements budget-constrained optimization over heterogeneous compression operations—full retention, quantization, merging, and eviction—guided by predicted relevance scores.

3. **Implement Continual Calibration mechanisms** that leverage online attention feedback to adapt retention policies during inference, handling distribution shifts in streaming scenarios.

4. **Validate the framework** across diverse long-context benchmarks, demonstrating significant memory reduction with minimal quality degradation.

### Significance

This research addresses a fundamental challenge in efficient foundation model deployment. By introducing query-awareness into KV cache compression, we bridge the gap between static compression methods and the dynamic information requirements of real-world applications. The framework enables: (1) deployment of long-context models on consumer-grade GPUs, (2) efficient RAG integration by intelligently managing retrieved context alongside conversation history, (3) continual adaptation scenarios where models must integrate streaming information while maintaining retrieval quality. Success in this research would substantially advance the accessibility and scalability of foundation models across memory-constrained deployment environments.

## 2. Methodology

### 2.1 Problem Formulation

Consider a transformer model processing a sequence of $n$ tokens with $L$ layers and $H$ attention heads. At layer $l$ and head $h$, the KV cache stores matrices $\mathbf{K}^{l,h}, \mathbf{V}^{l,h} \in \mathbb{R}^{n \times d}$, where $d$ is the head dimension. The total memory footprint is $\mathcal{O}(2LHnd)$, which becomes prohibitive for large $n$.

Our goal is to learn a compression function $\mathcal{C}$ that maps the full cache to a compressed representation:

$$\mathcal{C}: (\mathbf{K}^{l,h}, \mathbf{V}^{l,h}) \mapsto (\tilde{\mathbf{K}}^{l,h}, \tilde{\mathbf{V}}^{l,h})$$

such that the memory footprint is reduced by factor $\gamma$ while maintaining generation quality:

$$\frac{\text{Memory}(\tilde{\mathbf{K}}, \tilde{\mathbf{V}})}{\text{Memory}(\mathbf{K}, \mathbf{V})} \leq \frac{1}{\gamma}, \quad \mathbb{E}[\mathcal{L}(\tilde{y}, y^*)] \leq \mathbb{E}[\mathcal{L}(y, y^*)] + \epsilon$$

where $y$ and $\tilde{y}$ denote outputs with full and compressed caches respectively, and $\epsilon$ bounds quality degradation.

### 2.2 Relevance Predictor Network

The core innovation is a **Relevance Predictor Network (RPN)** that estimates the future importance of each KV entry. Rather than conditioning on unknown future queries, we learn a set of $M$ query prototypes $\{\mathbf{q}_m\}_{m=1}^M$ that represent canonical query patterns.

**Architecture**: The RPN consists of a lightweight 2-layer transformer with hidden dimension $d_{\text{rpn}} = 128$ operating on pooled KV representations:

$$\mathbf{z}_i = \text{Pool}(\mathbf{K}_i^{1:L}, \mathbf{V}_i^{1:L}) \in \mathbb{R}^{d_{\text{rpn}}}$$

where pooling aggregates across layers via learned weighted averaging. The RPN then computes:

$$\mathbf{h}_i = \text{TransformerRPN}(\mathbf{z}_{1:n})_i$$

**Relevance Scoring**: For each position $i$, we compute relevance scores against learned query prototypes:

$$s_i = \max_{m \in [M]} \frac{\mathbf{h}_i^\top \mathbf{q}_m}{\|\mathbf{h}_i\| \|\mathbf{q}_m\|} + \lambda \cdot \text{RecencyBias}(i, n)$$

where the recency bias $\text{RecencyBias}(i, n) = \exp(-\alpha(n-i)/n)$ encodes the empirical observation that recent tokens tend to be more relevant, with learnable temperature $\alpha$.

**Training via Distillation**: We train the RPN by distilling knowledge from full-cache attention patterns. Given a dataset of query-context pairs $(c, q)$, we compute target importance scores:

$$s_i^* = \frac{1}{|q|} \sum_{j \in q} \text{Attn}(j, i)$$

where $\text{Attn}(j, i)$ is the average attention weight from query token $j$ to context position $i$ across layers and heads. The training loss is:

$$\mathcal{L}_{\text{RPN}} = \text{KL}(\text{softmax}(s^*/\tau) \| \text{softmax}(s/\tau)) + \beta \|\Theta_{\text{RPN}}\|_2^2$$

with temperature $\tau$ and regularization coefficient $\beta$.

### 2.3 Adaptive Retention Policy

Given relevance scores, the **Adaptive Retention Policy (ARP)** determines the compression strategy for each KV entry under a memory budget constraint.

**Compression Operations**: We define four operations with associated memory costs:
- **Full Retention** ($\mathcal{R}_{\text{full}}$): Cost = 1.0 (baseline)
- **Quantization** ($\mathcal{R}_{\text{quant}}$): 4-bit quantization, Cost = 0.25
- **Merging** ($\mathcal{R}_{\text{merge}}$): Combine $k$ consecutive entries, Cost = $1/k$
- **Eviction** ($\mathcal{R}_{\text{evict}}$): Remove entry, Cost = 0

**Budget-Constrained Optimization**: Let $\pi_i \in \{0, 1, 2, 3\}$ denote the policy assignment for position $i$. We solve:

$$\max_{\pi} \sum_{i=1}^{n} s_i \cdot \mathbb{1}[\pi_i \neq \text{evict}] \cdot \text{Fidelity}(\pi_i)$$

$$\text{s.t.} \quad \sum_{i=1}^{n} \text{Cost}(\pi_i) \leq B$$

where $B = n/\gamma$ is the memory budget and $\text{Fidelity}(\cdot)$ quantifies information preservation (1.0 for full, 0.9 for quantization, 0.7 for merging).

This integer program is solved efficiently via a greedy algorithm: sort entries by $s_i \cdot \text{Fidelity}(\text{full}) / \text{Cost}(\text{full})$, then iteratively assign the highest-fidelity affordable operation until the budget is exhausted.

**Merging Mechanism**: For entries assigned to merging, we compute summary states:

$$\tilde{\mathbf{K}}_{\text{merged}} = \sum_{i \in \mathcal{G}} w_i \mathbf{K}_i, \quad w_i = \frac{\exp(s_i)}{\sum_{j \in \mathcal{G}} \exp(s_j)}$$

where $\mathcal{G}$ denotes a group of consecutive low-relevance entries, with relevance-weighted averaging preserving more important information.

### 2.4 Continual Calibration

To handle distribution shifts during inference, we implement **Continual Calibration (CC)** that updates the retention policy using online feedback.

**Attention Feedback Signal**: After each generation step $t$, we observe actual attention weights $\mathbf{a}_t$ over the compressed cache. We compute a calibration signal:

$$\delta_i^{(t)} = \mathbf{a}_t[i] - \hat{\mathbf{a}}_t[i]$$

where $\hat{\mathbf{a}}_t[i]$ is the predicted attention based on relevance scores. Large positive $\delta_i^{(t)}$ indicates underestimated importance.

**Online Update**: We maintain exponential moving averages of prediction errors:

$$e_i \leftarrow \rho \cdot e_i + (1-\rho) \cdot \delta_i^{(t)}$$

and adjust scores: $s_i' = s_i + \eta \cdot e_i$, where $\rho = 0.9$ is the momentum and $\eta = 0.1$ is the learning rate.

**Promotion Mechanism**: Entries with persistent positive errors are promoted to higher-fidelity representations when budget allows, implementing a "cache promotion" strategy analogous to CPU cache hierarchies.

### 2.5 Experimental Design

**Datasets and Benchmarks**:
- **LongBench**: Multi-task benchmark covering summarization, QA, and few-shot learning (4K-32K tokens)
- **RULER**: Synthetic retrieval tasks with controllable needle-in-haystack complexity (up to 128K tokens)
- **InfiniteBench**: Extended reasoning tasks requiring integration across very long contexts
- **StreamingQA**: Custom benchmark simulating continual learning with evolving knowledge bases

**Baselines**:
- Full KV cache (upper bound)
- Uniform quantization (4-bit, 8-bit)
- StreamingLLM (attention sink + recent window)
- H2O (Heavy Hitter Oracle)
- GEAR, KVzip, xKV (state-of-the-art compression)

**Evaluation Metrics**:
- **Memory Reduction**: Compression ratio $\gamma$ achieved
- **Quality Preservation**: Task-specific metrics (F1, ROUGE, accuracy) relative to full cache
- **Inference Efficiency**: Tokens/second throughput, time-to-first-token latency
- **Adaptation Quality**: Performance on distribution-shifted streaming inputs

**Implementation Details**: We implement QARP on LLaMA-2 (7B, 13B) and Mistral (7B) using PyTorch with custom CUDA kernels for compressed attention. The RPN adds only 2M parameters (<0.03% overhead). Training uses 50K examples from RedPajama with diverse query types, requiring approximately 8 A100-hours.

**Ablation Studies**:
- Impact of number of query prototypes $M$
- Contribution of each compression operation
- Effectiveness of continual calibration under varying distribution shift magnitudes
- Sensitivity to memory budget $B$

## 3. Expected Outcomes & Impact

### Expected Outcomes

We anticipate the following quantitative results:

1. **Memory Efficiency**: 4-8× KV cache reduction ($\gamma \in [4, 8]$) across tested models and context lengths, with the adaptive policy achieving superior Pareto frontiers compared to uniform compression baselines.

2. **Quality Preservation**: <2% degradation on LongBench aggregate scores at 4× compression, <5% at 8× compression, significantly outperforming query-agnostic methods like H2O (typically 5-10% degradation at 4×).

3. **Inference Speedup**: 1.5-2× throughput improvement due to reduced memory bandwidth requirements, with minimal latency overhead from the lightweight RPN (<5ms per 1K tokens).

4. **Continual Adaptation**: Stable performance on StreamingQA benchmark under distribution shift, demonstrating the effectiveness of online calibration—a capability absent in static compression methods.

5. **RAG Integration**: Efficient management of retrieved passages alongside conversation history, enabling 2× longer effective context within fixed memory budgets.

### Broader Impact

**Democratizing Long-Context Models**: By enabling deployment on consumer GPUs (e.g., RTX 3090 with 24GB), QARP democratizes access to powerful long-context capabilities previously restricted to high-end infrastructure.

**Enabling New Applications**: The framework unlocks applications requiring both long context and memory efficiency: personal assistants maintaining extensive conversation history, document analysis systems processing entire books, and real-time RAG systems integrating dynamic knowledge bases.

**Advancing Compression Research**: The query-aware paradigm represents a conceptual shift from static to anticipatory compression, potentially inspiring similar approaches in other domains (video streaming, database systems).

**Sustainability**: Reduced memory footprint translates to lower energy consumption and carbon emissions, contributing to sustainable AI deployment.

### Limitations and Future Work

We acknowledge limitations including: (1) training data requirements for the RPN, (2) potential brittleness to highly out-of-distribution queries, and (3) overhead in extreme latency-sensitive applications. Future work will explore: extending to multi-modal models, integrating with speculative decoding, and developing theoretical guarantees on compression-quality tradeoffs.