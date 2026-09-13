# Research Proposal: APIDS: Adaptive Perplexity-Influence Data Selection for Foundation Model Pre-training

## 1. Introduction

### 1.1 Background

The landscape of machine learning has undergone a fundamental paradigm shift with the emergence of large-scale foundation models. While architectural innovations dominated research attention for decades, recent evidence demonstrates that data quality, curation, and selection have become the primary determinants of model performance. This data-centric perspective is exemplified by initiatives such as DataComp, which established standardized benchmarks for evaluating data selection strategies, and DCLM (DataComp for Language Models), which achieved state-of-the-art performance through principled data curation rather than architectural modifications.

Web-crawled datasets like CommonCrawl and LAION provide unprecedented scale but suffer from heterogeneous quality, containing noise, duplicates, toxic content, and low-utility samples alongside valuable training data. The challenge of efficiently identifying high-quality subsets from these massive corpora has become a critical bottleneck in foundation model development. Current approaches to data selection typically rely on single metrics: perplexity-based filtering uses a reference language model to identify "typical" text, while influence-based methods estimate each sample's contribution to model training. However, each approach has fundamental limitations.

Perplexity-based filtering is computationally efficient with $O(n)$ complexity but captures only data typicality—how well a sample fits the reference model's distribution. This metric fails to distinguish between typical-but-uninformative samples and atypical-but-valuable domain-specific content. Conversely, influence-based methods directly estimate training utility through gradient analysis but incur prohibitive $O(n^2)$ computational costs at web scale. Recent theoretical work by Ayed and Hayou (2023) formalized this challenge through "No Free Lunch" theorems for data pruning, demonstrating that no single metric universally outperforms others across all data distributions and downstream tasks.

### 1.2 Research Objectives

This research proposes APIDS (Adaptive Perplexity-Influence Data Selection), a hierarchical three-stage framework that combines complementary data quality signals to achieve superior sample efficiency in foundation model pre-training. Our primary objectives are:

1. **Develop a principled hybrid selection framework** that leverages perplexity as a cheap global filter and self-influence as an expensive local utility estimator, applying each metric where it provides maximum value per compute.

2. **Establish the complementarity hypothesis** by empirically validating that perplexity and self-influence capture orthogonal aspects of data quality (typicality vs. utility) with correlation $\rho < 0.8$ on web-crawled datasets.

3. **Demonstrate superior sample efficiency** by achieving >90% of full-data downstream performance at 50% data retention, outperforming single-metric baselines by 3-5%.

4. **Validate scale invariance** across model sizes from 160M to 7B parameters using standardized DataComp benchmarks.

### 1.3 Significance

Success in this research would establish principled hybrid selection as a new paradigm for data-centric foundation model development. The practical implications are substantial: reducing pre-training data requirements by 50% while maintaining performance would halve computational costs, energy consumption, and carbon emissions associated with foundation model training. Furthermore, the framework provides a template for combining complementary quality signals that extends beyond the specific metrics studied here, potentially enabling future research on multi-signal data curation.

The theoretical contribution lies in demonstrating how the "No Free Lunch" limitation can be circumvented through strategic metric combination—not by finding a universally superior single metric, but by identifying conditions under which hybrid approaches provide guaranteed improvements.

## 2. Methodology

### 2.1 Framework Overview

APIDS operates through three sequential stages, each designed to maximize information gain per computational unit:

**Stage 1: Perplexity-Based Noise Filtering** removes obvious outliers and noise at minimal cost, establishing a quality floor for subsequent processing.

**Stage 2: Self-Influence Utility Ranking** computes training utility scores only on the filtered subset, reducing computational burden while identifying high-value samples.

**Stage 3: Adaptive Threshold Learning** uses Bayesian optimization to determine optimal selection boundaries on a held-out validation set.

### 2.2 Stage 1: Perplexity-Based Noise Filtering

For each document $d_i$ in the raw dataset $\mathcal{D}$, we compute perplexity using a small reference language model $\mathcal{M}_{ref}$ (GPT-2 125M):

$$PPL(d_i) = \exp\left(-\frac{1}{|d_i|}\sum_{t=1}^{|d_i|} \log P_{\mathcal{M}_{ref}}(w_t | w_{<t})\right)$$

where $w_t$ denotes the $t$-th token and $|d_i|$ is the document length. Documents with perplexity exceeding threshold $\tau_{ppl}$ are removed:

$$\mathcal{D}_{filtered} = \{d_i \in \mathcal{D} : PPL(d_i) \leq \tau_{ppl}\}$$

The initial threshold $\tau_{ppl}$ is set to the $p$-th percentile of the perplexity distribution, where $p \in [0.50, 0.95]$ is a hyperparameter optimized in Stage 3. This stage has complexity $O(n)$ and typically retains 50-70% of the original data.

**Rationale:** High-perplexity documents often contain formatting errors, repeated text, code artifacts, or non-natural language content that provides minimal training value. By removing these samples first, we reduce the computational burden of the expensive influence computation in Stage 2.

### 2.3 Stage 2: Self-Influence Utility Ranking

For each document $d_i \in \mathcal{D}_{filtered}$, we compute self-influence using the TRAK (Tracing with the Randomly-projected After Kernel) approximation:

$$\mathcal{I}(d_i) = \nabla_\theta \mathcal{L}(d_i; \theta)^\top H_\theta^{-1} \nabla_\theta \mathcal{L}(d_i; \theta)$$

where $\mathcal{L}(d_i; \theta)$ is the training loss on document $d_i$, $\nabla_\theta \mathcal{L}$ is the gradient, and $H_\theta^{-1}$ is the inverse Hessian approximated via random projections.

In practice, we use the DataInf efficient approximation:

$$\mathcal{I}_{approx}(d_i) = \|\phi(d_i)\|^2 \cdot \lambda_{eff}^{-1}$$

where $\phi(d_i)$ is the projected gradient representation and $\lambda_{eff}$ is an effective regularization parameter. This reduces complexity from $O(n^2)$ to $O(nk)$ where $k$ is the projection dimension (typically $k=4096$).

Documents are ranked by self-influence score, with higher scores indicating greater training utility.

### 2.4 Stage 3: Adaptive Threshold Learning

We formulate threshold selection as a Bayesian optimization problem. Let $\mathbf{t} = (\tau_{ppl}, \tau_{inf})$ denote the threshold vector, where $\tau_{ppl}$ is the perplexity percentile cutoff and $\tau_{inf}$ is the influence percentile cutoff. The objective is:

$$\mathbf{t}^* = \arg\max_{\mathbf{t}} \mathbb{E}[f(\mathbf{t})]$$

where $f(\mathbf{t})$ is the downstream validation performance when training on data selected with thresholds $\mathbf{t}$.

We model $f(\mathbf{t})$ with a Gaussian Process:

$$f(\mathbf{t}) \sim \mathcal{GP}(\mu(\mathbf{t}), k(\mathbf{t}, \mathbf{t}'))$$

using a Matérn 5/2 kernel. The acquisition function is Expected Improvement:

$$\alpha_{EI}(\mathbf{t}) = \mathbb{E}[\max(f(\mathbf{t}) - f^+, 0)]$$

where $f^+$ is the best observed value. We run 50-100 Bayesian optimization iterations, each requiring a small-scale training run on the validation set.

**Search Space:**
- $\tau_{ppl} \in [0.50, 0.95]$ (percentile)
- $\tau_{inf} \in [0.10, 0.90]$ (percentile)

### 2.5 Complementarity Validation

Before applying the hybrid framework, we validate the complementarity assumption by computing the Spearman correlation between perplexity and self-influence scores:

$$\rho = 1 - \frac{6\sum_{i=1}^{n} d_i^2}{n(n^2-1)}$$

where $d_i$ is the difference between ranks. If $\rho > 0.8$, the metrics are highly correlated and the hybrid approach provides minimal benefit; in this case, APIDS falls back to single-metric selection (perplexity-only, as it is cheaper).

### 2.6 Data Collection and Experimental Design

**Datasets:**
- **Primary:** DataComp-medium (128M image-text pairs) for vision-language experiments
- **Secondary:** DCLM-pool (240T tokens from CommonCrawl) for language model experiments
- **Validation:** 1-5% held-out subset for threshold learning

**Model Architectures:**
- Vision-Language: ViT-B/32 CLIP (fixed architecture per DataComp protocol)
- Language Models: GPT-2 scale (160M, 1B) and Llama-style (7B)

**Baselines:**
1. **Random Selection:** Uniform random sampling at target retention rates
2. **Perplexity-Only:** Stage 1 filtering with fixed percentile cutoffs
3. **Influence-Only:** Self-influence ranking without perplexity pre-filtering
4. **SOTA Model-Based:** CLIPScore filtering (vision-language), fastText classifier (language)

**Experimental Conditions:**
- Retention rates: 10%, 25%, 50%, 75%, 100%
- Model scales: 160M, 1B, 7B parameters
- Random seeds: 5 seeds per condition, 20 total runs for statistical power

**Evaluation Metrics:**
1. **Sample Efficiency Ratio:** $SE_r = \frac{Perf_{r\%}}{Perf_{100\%}}$ where $r$ is retention rate
2. **Downstream Performance:** Average accuracy across DataComp 38-task evaluation suite
3. **Computational Overhead:** Wall-clock time relative to perplexity-only baseline
4. **Complementarity Coefficient:** Spearman $\rho$ between perplexity and influence

**Statistical Analysis:**
- Paired t-tests comparing APIDS vs. each baseline (same random seeds)
- Significance level: $\alpha = 0.05$ with Bonferroni correction for multiple comparisons
- Effect size: Cohen's d with 95% confidence intervals
- Required: $n \geq 20$ runs for statistical power $\geq 0.8$

### 2.7 Falsification Criteria

The hypothesis will be **rejected** if any of the following occur:

1. **Primary Failure:** Sample efficiency at 50% retention $\leq 0.85$ with $p > 0.05$
2. **Complementarity Failure:** No advantage over single metrics regardless of correlation level
3. **Compute Failure:** Total compute exceeds 2× perplexity-only baseline
4. **Scale Failure:** Improvement at 160M disappears at 1B+ scale

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Prediction (P1):** APIDS will achieve >90% of full-data downstream performance at 50% data retention, while perplexity-only achieves <85% and random selection achieves <80%. Based on prior work showing 5.3% ImageNet improvement from CLIPLoss+NormSim and 6.6pp MMLU improvement from DCLM filtering, we expect APIDS to provide 3-5% improvement over perplexity-only baselines.

**Secondary Predictions:**
- **P2 (Complementarity):** When $\rho < 0.5$, APIDS improvement >3%; when $\rho > 0.8$, improvement <1%
- **P3 (Efficiency):** Total compute <1.5× perplexity-only despite influence computation

**Quantitative Targets:**

| Metric | Target | Baseline |
|--------|--------|----------|
| Sample Efficiency (50%) | >0.90 | 0.80-0.85 |
| Improvement over PPL-only | 3-5% | — |
| Compute Overhead | <1.5× | 1.0× |
| Correlation $\rho$ | <0.8 | — |

### 3.2 Scientific Impact

This research addresses a fundamental tension in data-centric machine learning: the "No Free Lunch" theorem suggests no single metric universally succeeds, yet practical systems require principled selection strategies. APIDS demonstrates that strategic combination of complementary metrics can circumvent this limitation under identifiable conditions (low metric correlation).

The theoretical contribution establishes a framework for analyzing when hybrid approaches provide guaranteed improvements over single-metric methods. This extends beyond perplexity and influence to any pair of metrics capturing orthogonal quality dimensions.

### 3.3 Practical Impact

**Computational Savings:** Achieving 90% performance at 50% data retention would halve pre-training compute requirements. For a 7B parameter model requiring \$1M in compute, this represents \$500K savings per training run.

**Environmental Impact:** Reduced data requirements directly translate to lower energy consumption and carbon emissions, supporting sustainable AI development.

**Democratization:** Lower compute requirements make foundation model training accessible to organizations with limited resources, reducing concentration of AI capabilities.

### 3.4 Broader Implications

Success would establish principled hybrid selection as a new paradigm for data-centric foundation model development. The framework provides a template for:

1. **Multi-signal curation:** Combining quality signals beyond perplexity and influence (e.g., diversity, toxicity, domain relevance)
2. **Adaptive pipelines:** Learning selection strategies rather than hand-tuning thresholds
3. **Benchmark contributions:** Potential submission to DataComp and DataPerf benchmarks

### 3.5 Limitations and Future Work

**Known Limitations:**
- Requires held-out validation set (1-5% of data)
- Self-influence adds ~30% compute overhead vs. perplexity-only
- May miss domain-specific high-value content with atypical perplexity

**Future Directions:**
- Extension to streaming/online settings via incremental influence estimation
- Multi-objective optimization incorporating diversity and coverage metrics
- Transfer of learned thresholds across datasets and domains

This research represents a significant step toward principled, efficient data curation for foundation models, addressing one of the most pressing challenges in modern machine learning.