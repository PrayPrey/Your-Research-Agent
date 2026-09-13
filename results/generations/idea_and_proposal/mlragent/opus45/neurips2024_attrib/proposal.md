# Research Proposal: Training Data Attribution via Gradient-Weighted Influence Sketching

## 1. Introduction

### Background

The remarkable capabilities of modern machine learning models—particularly large language models (LLMs) trained on billions of examples—have revolutionized artificial intelligence applications. However, this progress has created a fundamental opacity problem: as training datasets grow to internet scale, understanding which specific training examples drive particular model behaviors becomes increasingly intractable. This attribution challenge has profound implications for model debugging, data contamination detection, copyright compliance, and responsible AI deployment.

Influence functions, originally developed in robust statistics, offer a principled framework for quantifying how individual training examples affect model predictions. Given a test point $z_{\text{test}}$ and training point $z_i$, the influence of removing $z_i$ on the loss at $z_{\text{test}}$ is approximated as:

$$\mathcal{I}(z_i, z_{\text{test}}) = -\nabla_\theta \mathcal{L}(z_{\text{test}}, \hat{\theta})^\top H_{\hat{\theta}}^{-1} \nabla_\theta \mathcal{L}(z_i, \hat{\theta})$$

where $H_{\hat{\theta}}$ is the Hessian of the training loss at optimal parameters $\hat{\theta}$. While theoretically elegant, this formulation faces critical scalability barriers: computing the inverse Hessian is $O(p^3)$ for $p$ parameters, and evaluating influences for $n$ training examples requires $O(n)$ gradient computations per query.

Recent work has attempted to address these challenges through various approximations. The EK-FAC method approximates the Hessian using Kronecker factorization, enabling influence computation in models up to 52 billion parameters. Dropout-based compression reduces memory overhead by selectively retaining gradient components. Forward-only methods shift computation to training time, eliminating per-query backward passes. However, these approaches still face fundamental limitations: EK-FAC remains computationally expensive for real-time attribution, dropout methods may lose critical gradient information, and forward-only approaches require substantial storage overhead.

### Research Objectives

This proposal introduces **Gradient-Weighted Influence Sketching (GWIS)**, a novel two-stage framework that achieves scalable data attribution through:

1. **Compact gradient sketching during training**: Maintaining streaming-compatible data structures that compress gradient information while preserving influence relationships
2. **Efficient candidate retrieval at inference**: Enabling O(log n) query time to identify candidate influential examples
3. **Precise refinement on candidate sets**: Computing exact influence only on small, high-probability candidate sets

Our primary objectives are:
- Achieve 1000× speedup over exact influence function computation
- Maintain attribution accuracy within 5% of exact methods
- Enable real-time data attribution for billion-parameter models
- Demonstrate practical utility for data contamination detection and dataset curation

### Significance

GWIS addresses a critical gap in the model attribution landscape. By enabling efficient, accurate attribution at scale, this research will:
- Empower practitioners to debug model failures by tracing them to specific training examples
- Enable detection of data contamination and memorization in real-time
- Support principled dataset curation for capability improvement
- Provide interpretable explanations for model behaviors tied to training data

## 2. Methodology

### 2.1 Overview of GWIS Framework

GWIS operates in two distinct phases: (1) an online sketching phase during model training that builds compact representations of gradient information, and (2) an offline query phase that efficiently retrieves and ranks influential training examples for any model output.

### 2.2 Gradient-Aware Sketch Construction

#### 2.2.1 Gradient Signature Computation

For each training example $z_i = (x_i, y_i)$ processed during training at step $t$, we compute the gradient of the loss with respect to model parameters:

$$g_i^{(t)} = \nabla_\theta \mathcal{L}(z_i, \theta^{(t)})$$

To make this tractable for models with billions of parameters, we project gradients into a lower-dimensional space using a fixed random projection matrix $R \in \mathbb{R}^{d \times p}$ where $d \ll p$:

$$\tilde{g}_i^{(t)} = R \cdot g_i^{(t)}$$

By the Johnson-Lindenstrauss lemma, for $d = O(\epsilon^{-2} \log n)$, pairwise distances (and thus inner products relevant to influence computation) are preserved up to factor $(1 \pm \epsilon)$.

#### 2.2.2 Hierarchical Count-Min Sketch with Gradient Weighting

We maintain a hierarchical sketch structure $\mathcal{S} = \{S_1, S_2, \ldots, S_L\}$ with $L$ levels. Each level $l$ contains a count-min sketch $S_l$ with $w_l$ buckets and $k$ hash functions $\{h_{l,1}, \ldots, h_{l,k}\}$.

For each projected gradient $\tilde{g}_i^{(t)}$, we compute gradient-aware hash values:

$$h_{l,j}(\tilde{g}_i^{(t)}) = \left\lfloor \frac{\tilde{g}_i^{(t)} \cdot r_{l,j}}{\Delta_l} \right\rfloor \mod w_l$$

where $r_{l,j}$ are random direction vectors and $\Delta_l$ is a resolution parameter that decreases with level (finer granularity at higher levels).

Each bucket in the sketch stores:
1. A weighted sum of gradient signatures: $\sum_{i \in \text{bucket}} \alpha_i \tilde{g}_i$
2. A list of training example indices that hash to this bucket
3. An accumulated influence estimate

The weighting factor $\alpha_i$ incorporates gradient magnitude and training step information:

$$\alpha_i = \|\tilde{g}_i^{(t)}\|_2 \cdot \gamma^{T-t}$$

where $\gamma \in (0,1)$ is a decay factor and $T$ is the final training step, emphasizing more recent gradients.

#### 2.2.3 Streaming Updates for Distributed Training

For compatibility with distributed training across $M$ workers, we employ a merge-friendly sketch design. Each worker $m$ maintains a local sketch $\mathcal{S}^{(m)}$. Periodically, sketches are merged using:

$$S_l[b] = \sum_{m=1}^{M} S_l^{(m)}[b]$$

This operation is commutative and associative, enabling asynchronous updates without synchronization barriers.

### 2.3 Efficient Influence Query Algorithm

#### 2.3.1 Query Gradient Computation

Given a test example $z_{\text{test}}$ whose prediction we wish to attribute, we compute:

$$g_{\text{test}} = \nabla_\theta \mathcal{L}(z_{\text{test}}, \hat{\theta})$$

and its projection $\tilde{g}_{\text{test}} = R \cdot g_{\text{test}}$.

#### 2.3.2 Hierarchical Candidate Retrieval

We query the sketch hierarchy from coarse to fine:

1. **Level 1 (coarse)**: Compute hash values $h_{1,j}(\tilde{g}_{\text{test}})$ for all $j \in [k]$. Retrieve candidate sets $C_1 = \bigcup_j \text{indices}(S_1[h_{1,j}(\tilde{g}_{\text{test}})])$.

2. **Subsequent levels**: For candidates surviving from level $l-1$, compute finer hashes at level $l$ and retain only examples with matching hashes:

$$C_l = C_{l-1} \cap \bigcup_j \text{indices}(S_l[h_{l,j}(\tilde{g}_{\text{test}})])$$

3. **Scoring candidates**: For each candidate $i \in C_L$, compute a sketch-based influence estimate:

$$\hat{\mathcal{I}}_{\text{sketch}}(z_i, z_{\text{test}}) = \tilde{g}_{\text{test}}^\top \tilde{g}_i \cdot \hat{H}^{-1}_{\text{diag}}$$

where $\hat{H}^{-1}_{\text{diag}}$ is a diagonal approximation of the inverse Hessian computed using exponential moving averages of squared gradients during training.

#### 2.3.3 Precise Refinement

The top-$k$ candidates (typically $k = 100$) are subjected to precise influence computation using EK-FAC or exact methods:

$$\mathcal{I}_{\text{exact}}(z_i, z_{\text{test}}) = -g_{\text{test}}^\top H^{-1}_{\text{EK-FAC}} g_i$$

This hybrid approach ensures high accuracy while limiting expensive computations to a small candidate set.

### 2.4 Theoretical Analysis

**Theorem 1 (Retrieval Guarantee)**: For appropriate choice of sketch parameters, if training example $z_i$ has true influence $|\mathcal{I}(z_i, z_{\text{test}})| \geq \tau$ for threshold $\tau$, then $z_i$ is retrieved in the candidate set $C_L$ with probability at least $1 - \delta$, where $\delta$ depends on the sketch width and depth.

**Theorem 2 (Query Complexity)**: The expected query time is $O(k \cdot L + |C_L| \cdot d)$, which is $O(\log n)$ when $|C_L| = O(\log n)$.

### 2.5 Experimental Design

#### 2.5.1 Datasets and Models

We evaluate GWIS across multiple scales:
- **Small-scale validation**: CIFAR-10/100 with ResNet-50
- **Medium-scale**: ImageNet with ViT-Large
- **Large-scale**: The Pile dataset with LLaMA-7B and LLaMA-70B

#### 2.5.2 Baselines

- **Exact influence functions** (where tractable)
- **EK-FAC approximation** (Grosse et al., 2023)
- **Dropout-compressed influence** (Zhang & Amiri, 2025)
- **Forward-only attribution** (Ma & Nyarko, 2025)
- **TracIn** (Pruthi et al., 2020)

#### 2.5.3 Evaluation Metrics

1. **Attribution accuracy**: 
   - Spearman correlation with exact influence rankings
   - Recall@k: fraction of true top-k influential examples retrieved

2. **Computational efficiency**:
   - Wall-clock query time
   - Memory overhead during training
   - Storage requirements for sketches

3. **Downstream task performance**:
   - Leave-one-out retraining correlation
   - Data debugging accuracy (identifying mislabeled examples)
   - Contamination detection precision/recall

4. **Scalability analysis**:
   - Query time vs. training set size
   - Attribution accuracy vs. sketch size

#### 2.5.4 Application Studies

**Data Contamination Detection**: Inject known test examples into training data and evaluate GWIS's ability to detect memorization through unusually high self-influence scores.

**Mislabel Detection**: On CIFAR-10 with synthetic label noise (5-20%), measure precision@k for identifying corrupted examples.

**Targeted Data Curation**: Use GWIS to select high-influence examples for specific capabilities, then verify through retraining experiments.

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Computational Efficiency**: We expect GWIS to achieve 1000× speedup over exact influence functions, enabling query times under 1 second for billion-scale training sets. This will be validated through systematic timing experiments across model scales.

2. **Attribution Accuracy**: We anticipate maintaining Spearman correlation > 0.95 with exact methods and Recall@100 > 0.90 for identifying top influential examples, representing less than 5% degradation from exact computation.

3. **Practical Utility**: We expect to demonstrate:
   - >95% precision in contamination detection for memorized examples
   - >80% precision@100 for mislabel detection at 10% noise rate
   - Statistically significant improvement in downstream task performance through influence-guided data selection

4. **Open-Source Toolkit**: We will release a production-ready implementation compatible with PyTorch and JAX, including pre-computed sketches for common training datasets.

### Broader Impact

**Scientific Impact**: GWIS will enable new research directions in understanding training dynamics at scale. By providing efficient attribution, researchers can systematically study how data composition affects emergent capabilities, validate or refute claims about data contamination, and develop principled approaches to dataset curation.

**Practical Impact**: For practitioners, GWIS offers actionable insights for model debugging. When models exhibit undesirable behaviors—from factual errors to harmful outputs—attribution to training data provides a clear path to remediation through targeted data removal or augmentation.

**Societal Impact**: Data attribution is increasingly important for AI governance. GWIS can support copyright compliance by identifying training examples that heavily influence specific outputs, inform consent and compensation frameworks for data contributors, and enhance transparency in AI systems.

### Limitations and Future Directions

We acknowledge limitations: sketch-based approximations may miss subtle influence patterns, and the method assumes gradient-based training. Future work will extend GWIS to reinforcement learning settings, develop theoretical guarantees under distribution shift, and explore connections to mechanistic interpretability for unified attribution frameworks.

---

**Total estimated timeline**: 18 months, with preliminary results on medium-scale experiments within 6 months.