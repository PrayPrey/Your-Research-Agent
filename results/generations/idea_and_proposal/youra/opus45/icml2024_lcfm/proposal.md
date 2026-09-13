# Research Proposal: THAR: Temporal Hierarchy-Aware Routing for Efficient Long-Context Foundation Models

## 1. Introduction

### 1.1 Background

Long-context foundation models represent a critical frontier in artificial intelligence, enabling systems to synthesize information across thousands to millions of tokens spanning text, images, audio, and genomic sequences. The ability to process extended contexts is essential for applications ranging from document understanding and multi-turn dialogue to video analysis and whole-genome modeling. However, current architectures face a fundamental efficiency-accuracy trade-off that limits their practical deployment.

Transformer-based models with self-attention mechanisms excel at capturing fine-grained token interactions and precise local dependencies, but their computational complexity scales quadratically with sequence length, $O(n^2)$, making them prohibitively expensive for very long contexts. State Space Models (SSMs), exemplified by the Mamba architecture, offer an attractive alternative with linear scaling $O(n)$, achieving up to 5x throughput improvements. However, SSMs underperform on tasks requiring precise local pattern matching, such as copying and in-context learning tasks.

Recent hybrid approaches, including Mamba-2-Hybrid and TransMamba, attempt to combine these mechanisms through fixed alternation patterns—for example, interleaving attention and SSM layers at predetermined intervals. While these hybrids demonstrate improvements over pure architectures, they ignore a crucial insight: different processing stages within a neural network may benefit from different computational mechanisms. This observation is supported by neuroscience research on hierarchical temporal processing in the brain, where lower cortical areas process fast, fine-grained sensory information while higher areas integrate information over longer timescales.

### 1.2 Research Objectives

This research proposes **THAR (Temporal Hierarchy-Aware Routing)**, a novel architecture that dynamically selects between SSM and attention mechanisms on a per-layer basis through learned routing. Our primary objectives are:

1. **Develop a depth-biased routing mechanism** that learns to allocate attention to lower layers (for fine-grained parallel processing) and SSM to upper layers (for efficient long-range integration).

2. **Validate the hierarchical temporal processing hypothesis** by demonstrating that learned routing patterns systematically correlate with network depth.

3. **Achieve superior efficiency-accuracy trade-offs** compared to fixed hybrid baselines, targeting ≥95% of Mamba-2-Hybrid accuracy while using ≤60% of Transformer FLOPs.

4. **Establish cross-modal generalization** of learned routing policies from text to vision domains.

### 1.3 Significance

This research addresses a critical gap in long-context foundation model design by introducing principled, learnable mechanism selection inspired by biological neural processing. Success would yield:

- **Practical impact**: Enabling deployment of long-context models on resource-constrained hardware through significant FLOPs reduction.
- **Scientific contribution**: Validating the hierarchical temporal processing hypothesis in artificial neural networks.
- **Methodological advancement**: Establishing a framework for adaptive hybrid architectures applicable across modalities.

## 2. Methodology

### 2.1 Architecture Design

#### 2.1.1 Overall Framework

THAR consists of $L$ layers (we use $L=12$ for our primary experiments), where each layer $l$ contains both an attention module $\mathcal{A}_l$ and an SSM module $\mathcal{S}_l$, along with a lightweight router $\mathcal{R}_l$ that selects between them.

For input hidden states $\mathbf{H}^{(l-1)} \in \mathbb{R}^{n \times d}$ at layer $l$, the forward pass is:

$$\mathbf{H}^{(l)} = g_l \cdot \mathcal{A}_l(\mathbf{H}^{(l-1)}) + (1 - g_l) \cdot \mathcal{S}_l(\mathbf{H}^{(l-1)})$$

where $g_l \in \{0, 1\}$ is the hard routing decision during inference.

#### 2.1.2 Router Architecture

Each layer's router $\mathcal{R}_l$ is a lightweight MLP that takes pooled layer inputs and produces mechanism selection probabilities:

$$\mathbf{z}_l = \text{pool}(\mathbf{H}^{(l-1)}) \in \mathbb{R}^d$$

$$p_{\text{attn}}^{(l)} = \sigma\left(\mathbf{W}_2^{(l)} \cdot \text{ReLU}\left(\mathbf{W}_1^{(l)} \cdot \mathbf{z}_l\right) + b_{\text{depth}}^{(l)}\right)$$

where $\mathbf{W}_1^{(l)} \in \mathbb{R}^{h \times d}$, $\mathbf{W}_2^{(l)} \in \mathbb{R}^{1 \times h}$ with hidden dimension $h=128$, and $b_{\text{depth}}^{(l)}$ is a learnable depth-dependent bias initialized to encourage our hypothesized pattern:

$$b_{\text{depth}}^{(l)} = \alpha \cdot \left(1 - \frac{2l}{L}\right)$$

where $\alpha = 0.5$ provides a soft prior toward attention in lower layers and SSM in upper layers.

#### 2.1.3 Differentiable Training with Gumbel-Softmax

During training, we use the Gumbel-Softmax trick to enable gradient flow through discrete routing decisions:

$$g_l^{\text{soft}} = \frac{\exp\left((\log p_{\text{attn}}^{(l)} + G_1) / \tau\right)}{\exp\left((\log p_{\text{attn}}^{(l)} + G_1) / \tau\right) + \exp\left((\log(1 - p_{\text{attn}}^{(l)}) + G_2) / \tau\right)}$$

where $G_1, G_2 \sim \text{Gumbel}(0, 1)$ and temperature $\tau$ is annealed from 1.0 to 0.1 during training. During inference, we use hard routing: $g_l = \mathbb{1}[p_{\text{attn}}^{(l)} > 0.5]$.

#### 2.1.4 Attention and SSM Modules

**Attention Module**: We employ FlashAttention-2 for IO-efficient computation:

$$\mathcal{A}_l(\mathbf{H}) = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^\top}{\sqrt{d_k}}\right)\mathbf{V}$$

with $\mathbf{Q}, \mathbf{K}, \mathbf{V} = \mathbf{H}\mathbf{W}_Q, \mathbf{H}\mathbf{W}_K, \mathbf{H}\mathbf{W}_V$.

**SSM Module**: We adopt the Mamba-2 selective state space formulation:

$$\mathcal{S}_l(\mathbf{H}) = \text{SSM}(\mathbf{H}; \mathbf{A}_l, \mathbf{B}_l, \mathbf{C}_l, \Delta_l)$$

where parameters are input-dependent, enabling selective information propagation.

### 2.2 Training Procedure

#### 2.2.1 Loss Function

The total training objective combines task loss with efficiency regularization:

$$\mathcal{L} = \mathcal{L}_{\text{task}} + \lambda \cdot \mathcal{L}_{\text{efficiency}}$$

where:

$$\mathcal{L}_{\text{task}} = -\frac{1}{n}\sum_{t=1}^{n} \log P(x_t | x_{<t})$$

$$\mathcal{L}_{\text{efficiency}} = \frac{1}{L}\sum_{l=1}^{L} p_{\text{attn}}^{(l)}$$

The efficiency regularization $\lambda \in [0.01, 0.5]$ penalizes attention usage, encouraging SSM selection where beneficial. We conduct hyperparameter search over $\lambda \in \{0.01, 0.05, 0.1, 0.2, 0.3, 0.5\}$.

#### 2.2.2 Training Configuration

- **Model size**: 3B parameters (controlled)
- **Training data**: SlimPajama corpus (627B tokens), with long-context augmentation
- **Context lengths**: Progressive training from 4K → 16K → 64K → 100K tokens
- **Optimizer**: AdamW with $\beta_1=0.9$, $\beta_2=0.95$, weight decay 0.1
- **Learning rate**: Peak $3 \times 10^{-4}$ with cosine decay
- **Hardware**: 8× A100 80GB GPUs with FSDP

### 2.3 Experimental Design

#### 2.3.1 Datasets and Benchmarks

**Primary Evaluation**: LongBench v2, covering:
- Single-document QA (NarrativeQA, Qasper)
- Multi-document QA (HotpotQA, MuSiQue)
- Summarization (GovReport, QMSum)
- Code completion (LCC, RepoBench-P)
- Synthetic tasks (PassageRetrieval, PassageCount)

**Context Length Stratification**: 1K, 4K, 16K, 32K, 64K, 100K tokens

**Probing Tasks**: Synthetic copying, in-context learning, and needle-in-haystack retrieval to isolate mechanism-specific capabilities.

#### 2.3.2 Baselines

| Model | Description |
|-------|-------------|
| Transformer-3B | Pure attention baseline |
| Mamba-2-3B | Pure SSM baseline |
| Mamba-2-Hybrid-3B | Fixed 50% attention/SSM alternation |
| TransMamba-3B | Fixed interleaving pattern |
| THAR-Uniform | Our architecture with uniform random routing |
| THAR-Random | Our architecture with random (non-depth-biased) initialization |

#### 2.3.3 Ablation Studies

**A1: Routing Pattern Analysis**
- Track $p_{\text{ssm}}^{(l)}$ across all layers for 10K validation samples
- Hypothesis test: One-sample t-test comparing layer-wise routing against chance (0.5)
- Visualization: Routing heatmaps across layers and context positions

**A2: Depth Bias Necessity**
- Compare THAR (depth-biased init) vs. THAR-Random (uniform init)
- Measure convergence speed and final routing patterns

**A3: Efficiency Regularization Sensitivity**
- Sweep $\lambda \in \{0.01, 0.05, 0.1, 0.2, 0.3, 0.5\}$
- Plot Pareto frontier of accuracy vs. FLOPs

**A4: Context Length Scaling**
- Evaluate routing patterns across 1K-100K contexts
- Test whether upper-layer SSM preference strengthens with longer contexts

### 2.4 Evaluation Metrics

**Accuracy Metrics**:
- Perplexity on held-out validation set
- LongBench v2 task accuracy (F1, exact match, ROUGE as appropriate)
- Probing task accuracy (copying, retrieval)

**Efficiency Metrics**:
- FLOPs per forward pass (theoretical)
- Wall-clock inference time (ms)
- Peak memory usage (GB)
- Throughput (tokens/second)

**Routing Analysis Metrics**:
- Layer-wise attention probability: $\bar{p}_{\text{attn}}^{(l)} = \mathbb{E}[p_{\text{attn}}^{(l)}]$
- Depth correlation: Pearson's $r$ between layer index and $p_{\text{ssm}}$
- Routing entropy: $H_l = -p_{\text{attn}}^{(l)} \log p_{\text{attn}}^{(l)} - (1-p_{\text{attn}}^{(l)}) \log(1-p_{\text{attn}}^{(l)})$

### 2.5 Statistical Analysis Plan

**Sample Size Justification**: Based on power analysis with Cohen's $d = 0.6$, $\alpha = 0.05$, power $= 0.8$, we require $n \geq 25$ independent runs.

**Primary Analysis**:
- Paired t-tests comparing THAR vs. each baseline
- Bonferroni correction for multiple comparisons
- Report: mean difference, 95% CI, Cohen's $d$, $p$-value

**Routing Pattern Verification**:
- One-sample t-test: $H_0: \bar{p}_{\text{ssm}}^{(\text{upper})} = 0.5$ vs. $H_1: \bar{p}_{\text{ssm}}^{(\text{upper})} > 0.7$
- Correlation analysis: Test $r(\text{layer index}, p_{\text{ssm}}) > 0$

### 2.6 Cross-Modal Transfer Experiment

To test generalization (Prediction P3), we:
1. Train THAR on text (SlimPajama)
2. Freeze router parameters
3. Fine-tune only attention/SSM modules on video understanding (LVU benchmark)
4. Compare against training routers from scratch
5. Success criterion: <10% of from-scratch training cost for equivalent performance

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Prediction (P1)**: We expect trained routers to exhibit systematic depth-dependent patterns:
- Layers 1-4 (lower): $\bar{p}_{\text{attn}} > 0.60$
- Layers 5-8 (middle): $\bar{p}_{\text{attn}} \approx 0.40-0.60$
- Layers 9-12 (upper): $\bar{p}_{\text{ssm}} > 0.70$

**Secondary Predictions**:
- **P2**: THAR achieves ≥95% of Mamba-2-Hybrid accuracy on LongBench v2 while using ≤60% of Transformer FLOPs, yielding effective complexity of $O(n \cdot \log n)$.
- **P3**: Text-trained routing policies transfer to vision with <10% fine-tuning cost.

**Quantitative Targets**:
| Metric | Transformer | Mamba-2-Hybrid | THAR (Expected) |
|--------|-------------|----------------|-----------------|
| LongBench Avg | 65.0% | 67.5% | ≥66.5% |
| FLOPs (64K ctx) | 1.0× | 0.55× | ≤0.40× |
| Throughput | 1.0× | 4.5× | ≥5.0× |

### 3.2 Falsification Criteria

The hypothesis will be considered falsified if:
1. Routing shows no depth correlation ($|r| < 0.3$, $p > 0.05$)
2. THAR achieves <90% of Mamba-2-Hybrid accuracy OR requires >80% of Transformer FLOPs
3. >80% of layers converge to a single mechanism (routing collapse)
4. Vision transfer requires >50% of from-scratch training cost

### 3.3 Scientific Impact

**Theoretical Contributions**:
- First empirical validation of hierarchical temporal processing principles in artificial neural networks
- Framework for understanding when attention vs. recurrence is computationally optimal
- Insights into the relationship between network depth and temporal processing timescales

**Methodological Contributions**:
- Novel depth-biased routing mechanism applicable to other hybrid architectures
- Efficiency-regularized training procedure for mechanism selection
- Comprehensive evaluation protocol for hybrid long-context models

### 3.4 Practical Impact

**Deployment Benefits**:
- 2.5× throughput improvement enables longer contexts on existing hardware
- Reduced memory footprint allows processing 100K+ tokens on consumer GPUs
- Adaptive routing provides graceful degradation under resource constraints

**Application Domains**:
- Document understanding and legal analysis
- Long-form video comprehension
- Genomic sequence modeling
- Multi-turn conversational AI

### 3.5 Limitations and Future Work

**Known Limitations**:
- Router adds ~2% parameter overhead
- Depth bias may not generalize to all modalities without adaptation
- Hard routing prevents fine-grained mechanism mixing within layers

**Future Directions**:
- Token-level routing for finer-grained mechanism selection
- Extension to mixture-of-experts with >2 mechanisms
- Application to streaming/online inference scenarios
- Theoretical analysis of optimal routing under different task distributions

### 3.6 Timeline

| Phase | Duration | Activities |
|-------|----------|------------|
| 1 | Months 1-2 | Implementation, infrastructure setup |
| 2 | Months 3-4 | Pretraining at 1B scale, hyperparameter tuning |
| 3 | Months 5-7 | Full 3B training, primary evaluation |
| 4 | Months 8-9 | Ablations, cross-modal experiments |
| 5 | Months 10-12 | Analysis, paper writing, release |

This research will advance our understanding of efficient long-context processing while delivering practical architectures for next-generation foundation models.