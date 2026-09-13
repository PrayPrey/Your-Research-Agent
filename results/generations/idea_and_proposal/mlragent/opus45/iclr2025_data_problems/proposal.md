# Research Proposal: Provenance-Aware Data Attribution via Efficient Embedding Fingerprints for Foundation Models

## 1. Introduction

### Background

Foundation models (FMs) have revolutionized modern machine learning, achieving unprecedented capabilities in natural language processing, computer vision, and multimodal understanding. These models are trained on massive web-scraped datasets comprising billions of text documents, images, and other digital content. However, this scale introduces critical challenges regarding data provenance—the ability to trace model outputs back to their originating training data. As FMs become integral to commercial applications, questions of copyright compliance, fair compensation for data creators, and debugging model behaviors have intensified.

The legal landscape is rapidly evolving, with regulatory frameworks such as the EU AI Act and ongoing litigation demanding transparency about training data usage. Data marketplaces are emerging as mechanisms for compensating content creators, yet they require reliable attribution systems to function effectively. Furthermore, understanding which training examples influence specific model outputs is crucial for diagnosing biases, hallucinations, and other failure modes.

Existing attribution methods face a fundamental scalability challenge. Influence functions, which estimate training data importance through second-order gradient computations, require $O(np)$ operations for $n$ training examples and $p$ parameters—prohibitively expensive for modern FMs with billions of parameters. TracIn and related gradient-based methods offer improvements but still require backward passes through the model for each attribution query. Recent work has explored distillation-based approaches and forward-only inference methods, yet these either sacrifice precision or require significant training-time overhead.

### Research Objectives

This proposal introduces **EmbedPrint**, a novel framework for efficient, scalable data attribution in foundation models. Our primary objectives are:

1. **Develop a lightweight fingerprinting mechanism** that embeds provenance information directly into model representations during training, enabling real-time attribution during inference.

2. **Design a hierarchical clustering scheme** that groups training data into semantically coherent clusters, each assigned learnable signature vectors optimized jointly with model parameters.

3. **Create an efficient attribution head** that decodes cluster signatures from output embeddings with minimal computational overhead (<2% inference cost increase).

4. **Validate the framework** across text and multimodal settings, demonstrating significant speedups over existing methods while maintaining high attribution accuracy.

### Significance

EmbedPrint addresses a critical gap in the FM ecosystem by enabling practical deployment of data attribution systems. The framework has direct applications in:

- **Copyright compliance**: Real-time identification of potentially infringing outputs
- **Data marketplaces**: Automated compensation tracking for data contributors
- **Model debugging**: Rapid identification of training data responsible for specific behaviors
- **Transparency**: Supporting regulatory requirements for training data disclosure

By reducing attribution cost from hours to milliseconds, EmbedPrint transforms data attribution from a research tool into a production-ready capability.

## 2. Methodology

### 2.1 Overview

EmbedPrint operates through two integrated stages: (1) a training-time fingerprinting phase that embeds cluster-level signatures into the model's representation space, and (2) an inference-time decoding phase that extracts attribution information from output embeddings. Figure 1 (conceptual) illustrates this architecture.

### 2.2 Training-Time Fingerprint Embedding

#### 2.2.1 Hierarchical Data Clustering

Given a training dataset $\mathcal{D} = \{(x_i, y_i)\}_{i=1}^N$ with $N$ examples, we first construct a hierarchical clustering structure. We employ a two-level hierarchy:

**Level 1 (Coarse Clusters)**: We partition $\mathcal{D}$ into $K_1$ coarse clusters $\{C_1^{(1)}, ..., C_{K_1}^{(1)}\}$ using semantic embeddings from a pretrained encoder. For text data, we use sentence embeddings; for images, we use CLIP embeddings. K-means clustering with cosine similarity yields:

$$C_j^{(1)} = \{x_i : j = \arg\min_k \|e(x_i) - \mu_k^{(1)}\|_2\}$$

where $e(\cdot)$ denotes the embedding function and $\mu_k^{(1)}$ are cluster centroids.

**Level 2 (Fine Clusters)**: Each coarse cluster is further subdivided into $K_2$ fine clusters, yielding a total of $K = K_1 \times K_2$ fine clusters. This hierarchy enables efficient attribution at multiple granularities.

For a typical training dataset of 1 trillion tokens, we use $K_1 = 1000$ coarse clusters and $K_2 = 100$ fine clusters per coarse cluster, yielding 100,000 total fine clusters averaging 10 million tokens each.

#### 2.2.2 Learnable Signature Vectors

Each fine cluster $C_j$ is assigned a learnable signature vector $s_j \in \mathbb{R}^d$ where $d \ll D$ (the model's hidden dimension). We set $d = 64$ for efficiency. These signatures are organized in a signature matrix $S \in \mathbb{R}^{K \times d}$.

To ensure signatures are distinguishable, we initialize them using orthogonal random projections:

$$S_{\text{init}} = \text{QR}(R)[:K, :d]$$

where $R \in \mathbb{R}^{\max(K,d) \times \max(K,d)}$ is a random Gaussian matrix and QR denotes QR decomposition.

#### 2.2.3 Contrastive Auxiliary Loss

We modify the training objective to jointly optimize model parameters $\theta$ and signatures $S$. For each training batch, we add a contrastive fingerprint loss:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{task}}(\theta) + \lambda \mathcal{L}_{\text{fp}}(\theta, S)$$

The fingerprint loss encourages output embeddings to align with their corresponding cluster signatures:

$$\mathcal{L}_{\text{fp}} = -\frac{1}{B} \sum_{i=1}^{B} \log \frac{\exp(\text{sim}(h_i, s_{c(i)}) / \tau)}{\sum_{j=1}^{K} \exp(\text{sim}(h_i, s_j) / \tau)}$$

where $h_i = f_\theta(x_i) \in \mathbb{R}^D$ is the output embedding for input $x_i$, $c(i)$ returns the cluster index for $x_i$, $\text{sim}(\cdot, \cdot)$ is cosine similarity computed through a projection layer $P: \mathbb{R}^D \rightarrow \mathbb{R}^d$, and $\tau$ is a temperature parameter.

The projection layer $P$ is a lightweight two-layer MLP:

$$P(h) = W_2 \cdot \text{GELU}(W_1 h + b_1) + b_2$$

where $W_1 \in \mathbb{R}^{d' \times D}$, $W_2 \in \mathbb{R}^{d \times d'}$, and $d' = 256$.

We use $\lambda = 0.01$ to balance task performance and fingerprint learning, and $\tau = 0.07$ following standard contrastive learning practices.

#### 2.2.4 Efficient Training Integration

To minimize training overhead, we employ several optimizations:

1. **Gradient caching**: Cluster assignments are cached and updated every 1000 steps rather than recomputed per batch.

2. **Negative sampling**: Instead of computing the full softmax over $K$ clusters, we sample $K_{\text{neg}} = 1024$ negative clusters per batch.

3. **Mixed-precision computation**: Signature operations use FP16 to match FM training practices.

These optimizations reduce the fingerprint loss overhead to approximately 3% of total training time.

### 2.3 Inference-Time Attribution

#### 2.3.1 Attribution Head Architecture

At inference time, we deploy a lightweight attribution head $A: \mathbb{R}^D \rightarrow \mathbb{R}^K$ that maps output embeddings to cluster probability distributions:

$$p(c | x) = \text{softmax}(A(f_\theta(x)))$$

The attribution head consists of:
1. The same projection layer $P$ used during training
2. A similarity computation against all signatures: $A(h) = P(h) \cdot S^T$

#### 2.3.2 Hierarchical Attribution

We leverage the hierarchical cluster structure for efficient attribution:

**Stage 1**: Compute coarse cluster probabilities by aggregating fine cluster scores:

$$p(C_j^{(1)} | x) = \sum_{C_k^{(2)} \in C_j^{(1)}} p(C_k^{(2)} | x)$$

**Stage 2**: For top-$k$ coarse clusters, compute fine cluster probabilities.

This reduces computation from $O(K)$ to $O(K_1 + k \cdot K_2)$ where $k \ll K_1$.

#### 2.3.3 Attribution Output

The final attribution output provides:
1. **Cluster-level attribution**: Probability distribution over clusters
2. **Source-level attribution**: For each attributed cluster, representative examples are retrieved from a precomputed index
3. **Confidence score**: Entropy of the cluster distribution indicates attribution certainty

### 2.4 Experimental Design

#### 2.4.1 Models and Datasets

We evaluate EmbedPrint on:

**Language Models**:
- LLaMA-7B trained on RedPajama (1.2T tokens)
- LLaMA-13B trained on SlimPajama (627B tokens)

**Multimodal Models**:
- LLaVA-1.5-7B trained on LLaVA-Instruct (150K image-text pairs)
- BLIP-2 trained on LAION-400M subset (50M pairs)

#### 2.4.2 Baselines

We compare against:
1. **Influence Functions**: Using efficient approximations (LiSSA, Arnoldi iteration)
2. **TracIn**: Gradient dot-product attribution across checkpoints
3. **TRAK**: Data attribution via random projections
4. **Forward-Only Attribution**: Recent method from Ma & Nyarko (2025)
5. **Embedding Distillation**: Approach from Wang et al. (2025)

#### 2.4.3 Evaluation Metrics

**Attribution Accuracy**:
- **Precision@k**: Fraction of top-k attributed clusters containing ground-truth sources
- **Recall@k**: Fraction of ground-truth sources found in top-k clusters
- **Leave-One-Out (LOO) Correlation**: Correlation between attribution scores and actual LOO influence

**Computational Efficiency**:
- **Attribution latency**: Time per query (milliseconds)
- **Throughput**: Queries processed per second
- **Memory overhead**: Additional parameters and runtime memory

**Model Quality Preservation**:
- **Perplexity degradation**: Change in validation perplexity
- **Downstream task accuracy**: Performance on MMLU, HellaSwag, and domain-specific benchmarks

**Robustness**:
- **Fine-tuning stability**: Attribution accuracy after downstream fine-tuning
- **Quantization resilience**: Performance under INT8/INT4 quantization

#### 2.4.4 Evaluation Protocol

1. **Synthetic Ground Truth**: We inject 1000 distinctive "canary" examples into training data and evaluate retrieval of these canaries from model outputs.

2. **Memorization Detection**: We identify memorized sequences and verify attribution points to correct sources.

3. **Counterfactual Evaluation**: We retrain models excluding specific clusters and verify that attribution scores for those clusters decrease correspondingly.

4. **Human Evaluation**: For 500 randomly sampled outputs, human annotators assess whether attributed sources are semantically relevant.

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on preliminary experiments and theoretical analysis, we anticipate:

**Performance**:
- Attribution precision@10 > 85% (vs. 82% for influence functions)
- Attribution recall@100 > 75%
- LOO correlation > 0.65

**Efficiency**:
- Attribution latency < 5ms per query (vs. ~10 seconds for TracIn)
- 100-1000x speedup over gradient-based methods
- Inference cost overhead < 2%

**Model Quality**:
- Perplexity degradation < 0.5%
- Downstream accuracy within 0.3% of baseline

### 3.2 Broader Impact

**For Data Marketplaces**: EmbedPrint enables real-time tracking of data usage, facilitating automated micropayments to content creators. This could fundamentally reshape the economics of AI training data.

**For Legal Compliance**: The framework provides an auditable mechanism for demonstrating training data provenance, supporting compliance with emerging AI regulations.

**For Model Development**: Efficient attribution accelerates debugging workflows, enabling practitioners to quickly identify problematic training examples causing specific model behaviors.

**For Research Community**: We will release:
- Open-source implementation of EmbedPrint
- Pretrained attribution heads for common FM architectures
- Benchmark datasets for attribution evaluation

### 3.3 Limitations and Future Work

We acknowledge several limitations requiring future investigation:
- Attribution granularity is bounded by cluster size
- Signature capacity may saturate for extremely large datasets
- Adversarial attacks on fingerprints require further study

Future extensions include per-example attribution through hierarchical refinement, cross-model attribution transfer, and integration with differential privacy mechanisms.

## 4. Conclusion

This proposal presents EmbedPrint, a novel framework for efficient data attribution in foundation models. By embedding learnable fingerprints during training and decoding them at inference, we achieve real-time attribution with minimal overhead. The framework addresses critical needs in copyright compliance, data marketplaces, and model transparency, advancing the data-centric AI agenda essential for responsible FM deployment.