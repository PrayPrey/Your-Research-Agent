# Research Proposal: Marginal Value Data Curation: Compute-Aware Filtering via Proxy-Based Bayesian Threshold Optimization

## 1. Introduction

### 1.1 Background

The emergence of large-scale foundation models has fundamentally transformed machine learning across vision, language, and multimodal domains. Models such as CLIP, GPT-4, and LLaMA demonstrate remarkable capabilities when trained on massive datasets comprising billions of samples. However, recent research has increasingly recognized that model architecture alone cannot explain these advances—the quality, diversity, and curation of training data play equally critical roles in determining model performance.

A central challenge in foundation model training is the quality-quantity tradeoff in data curation. Aggressive filtering strategies improve average data quality but reduce dataset size, potentially limiting model exposure to diverse concepts. Conversely, lenient filtering preserves dataset scale but wastes computational resources on low-value or noisy samples. Current state-of-the-art approaches, including those evaluated on benchmarks like DataComp, typically employ fixed filtering thresholds (e.g., CLIP score > 0.3) regardless of the available compute budget. This static approach ignores a fundamental insight: optimal filtering thresholds should adapt to compute constraints because larger budgets can tolerate more data since repetition penalties decrease with increased training iterations.

Recent work by Goyal et al. (2024) demonstrates that compute-agnostic curation is inherently suboptimal, showing that optimal filtering thresholds vary significantly with compute budget. Similarly, Sorscher et al. (2022) establish that effective data pruning metrics can transform scaling behavior from power-law to exponential, dramatically improving compute efficiency. However, existing methods for compute-aware curation either require expensive gradient-based computations (e.g., FLYT) or lack principled optimization frameworks for threshold selection.

### 1.2 Research Objectives

This research proposes **Marginal Value Data Curation (MVDC)**, a novel framework that dynamically optimizes filtering thresholds based on compute budget using pre-computed quality proxies and Bayesian optimization. Our specific objectives are:

1. **Develop a scalable value estimation framework** that aggregates proxy signals (CLIP scores, perplexity, embedding density) at cluster granularity to enable efficient marginal value estimation for billion-scale datasets.

2. **Design a Bayesian threshold optimization algorithm** that leverages scaling law predictions to find optimal filtering thresholds $\tau^*$ under uncertainty, maximizing performance-per-FLOP.

3. **Validate the MVDC framework** on established benchmarks (DataComp-medium) demonstrating superior performance over fixed-threshold baselines while maintaining computational overhead below 5% of total training compute.

4. **Characterize the relationship** between optimal filtering thresholds and compute budgets, testing the prediction that this relationship is monotonic.

### 1.3 Significance

This research addresses a critical gap between data valuation theory and practical foundation model training. By enabling compute-aware curation at billion-scale without expensive gradient-based methods, MVDC has the potential to:

- **Improve training efficiency** by 5-15% in performance-per-compute metrics, translating to significant cost savings at scale
- **Democratize foundation model training** by enabling smaller organizations to achieve competitive results with limited compute budgets
- **Advance understanding** of the quality-quantity tradeoff in data curation through principled Bayesian analysis
- **Provide practical tools** for the data-centric ML community aligned with benchmarks like DataComp and DataPerf

## 2. Methodology

### 2.1 Overview

MVDC operates through three integrated stages: (1) cluster-based value estimation using pre-computed quality proxies, (2) Bayesian optimization over scaling law parameters to determine optimal thresholds, and (3) adaptive filtering to maximize performance-per-FLOP. Figure 1 illustrates the complete pipeline.

### 2.2 Stage 1: Cluster-Based Value Estimation

#### 2.2.1 Proxy Signal Computation

For each sample $x_i$ in the data pool $\mathcal{D}$, we compute a vector of quality proxy signals:

$$\mathbf{p}_i = [s_{\text{CLIP}}(x_i), s_{\text{perp}}(x_i), s_{\text{div}}(x_i)]$$

where:
- $s_{\text{CLIP}}(x_i) \in [0, 1]$: CLIP cosine similarity between image and text embeddings
- $s_{\text{perp}}(x_i) \in [10, 1000]$: Text perplexity under a reference language model (normalized via $1 - \frac{\log(p)}{\log(1000)}$)
- $s_{\text{div}}(x_i)$: Local diversity score based on embedding density in the neighborhood

#### 2.2.2 Clustering and Aggregation

To enable scalable value estimation, we cluster samples based on their CLIP embeddings using k-means:

$$\mathcal{C} = \{C_1, C_2, \ldots, C_K\}$$

where $K$ is chosen to balance granularity and computational efficiency (we use $K = \sqrt{|\mathcal{D}|}$ as a heuristic). For each cluster $C_k$, we compute aggregate statistics:

$$\bar{\mathbf{p}}_k = \frac{1}{|C_k|} \sum_{x_i \in C_k} \mathbf{p}_i$$

$$\sigma_k = \sqrt{\frac{1}{|C_k|} \sum_{x_i \in C_k} \|\mathbf{p}_i - \bar{\mathbf{p}}_k\|^2}$$

#### 2.2.3 Marginal Value Estimation

We estimate the marginal training value of cluster $C_k$ using a learned value function:

$$V(C_k) = f_\theta(\bar{\mathbf{p}}_k, |C_k|, \sigma_k)$$

where $f_\theta$ is a lightweight neural network trained on pilot experiments that correlate proxy statistics with downstream performance improvements. The marginal value accounts for diminishing returns:

$$V_{\text{marginal}}(C_k | \mathcal{S}) = V(C_k) \cdot g(|\mathcal{S}|)$$

where $\mathcal{S}$ is the currently selected data and $g(\cdot)$ is a monotonically decreasing function capturing repetition penalties.

### 2.3 Stage 2: Bayesian Threshold Optimization

#### 2.3.1 Scaling Law Formulation

We model the expected performance $P$ as a function of effective data size $D_{\text{eff}}$ and compute budget $C$:

$$P(D_{\text{eff}}, C) = P_\infty - \alpha \cdot D_{\text{eff}}^{-\beta} - \gamma \cdot C^{-\delta}$$

where $D_{\text{eff}}(\tau) = \sum_{k: \bar{s}_k > \tau} |C_k|$ is the effective dataset size after filtering with threshold $\tau$, and $\{P_\infty, \alpha, \beta, \gamma, \delta\}$ are scaling law parameters.

#### 2.3.2 Bayesian Optimization Framework

We place Gaussian process priors over the scaling law parameters:

$$\theta = \{P_\infty, \alpha, \beta, \gamma, \delta\} \sim \mathcal{GP}(\mu_0, k_\theta)$$

Given pilot observations $\mathcal{O} = \{(\tau_j, C_j, P_j)\}_{j=1}^{n_{\text{pilot}}}$, we update the posterior:

$$p(\theta | \mathcal{O}) \propto p(\mathcal{O} | \theta) \cdot p(\theta)$$

The optimal threshold $\tau^*$ for a given compute budget $C$ is found by maximizing the expected improvement:

$$\tau^*(C) = \arg\max_\tau \mathbb{E}_{\theta | \mathcal{O}}\left[\frac{P(D_{\text{eff}}(\tau), C)}{C}\right]$$

#### 2.3.3 Acquisition Function

We use the Expected Improvement (EI) acquisition function with compute-awareness:

$$\text{EI}(\tau | C) = \mathbb{E}\left[\max\left(0, \frac{P(D_{\text{eff}}(\tau), C)}{C} - \eta^*\right)\right]$$

where $\eta^* = \max_j \frac{P_j}{C_j}$ is the best observed performance-per-compute ratio.

### 2.4 Stage 3: Adaptive Filtering

Given the optimized threshold $\tau^*(C)$, we filter the dataset:

$$\mathcal{D}_{\text{filtered}} = \{x_i : x_i \in C_k \text{ and } \bar{s}_k > \tau^*(C)\}$$

For fine-grained control, we additionally apply within-cluster filtering:

$$\mathcal{D}_{\text{final}} = \{x_i \in \mathcal{D}_{\text{filtered}} : s_{\text{CLIP}}(x_i) > \tau^*(C) - \epsilon\}$$

where $\epsilon$ is a small margin allowing retention of high-value samples in borderline clusters.

### 2.5 Experimental Design

#### 2.5.1 Datasets and Benchmarks

**Primary Benchmark:** DataComp-medium (128M image-text pairs from a 12.8B pool)
- Training compute: ~1000 GPU-hours
- Evaluation: ImageNet zero-shot accuracy

**Secondary Benchmark:** DCLM (text-only, 240T token pool)
- Training compute: Variable (100-10000 GPU-hours)
- Evaluation: MMLU score

#### 2.5.2 Baselines

1. **Fixed-threshold CLIP filtering** ($\tau = 0.3$): Standard DataComp baseline
2. **DataComp CLIP baseline**: Official competition baseline (~35% accuracy)
3. **FLYT (M-FLYT)**: State-of-the-art gradient-based filtering (40.1% accuracy)
4. **Random sampling**: Lower bound baseline

#### 2.5.3 Experimental Protocol

**Pilot Phase (10% compute budget):**
- Run 5 training experiments with varied thresholds $\tau \in \{0.2, 0.25, 0.3, 0.35, 0.4\}$
- Collect scaling law observations for Bayesian calibration

**Main Experiments:**
- Apply MVDC to determine $\tau^*(C)$ for target compute budget
- Train foundation model on filtered dataset
- Repeat with 25 random seeds for statistical validity

**Ablation Studies:**
- Cluster granularity: $K \in \{1000, 10000, 100000\}$
- Proxy signal combinations: CLIP-only, perplexity-only, combined
- Bayesian vs. grid search optimization

#### 2.5.4 Evaluation Metrics

**Primary Metrics:**
- ImageNet zero-shot accuracy (%)
- Performance-per-FLOP ratio: $\eta = \frac{P}{C}$

**Secondary Metrics:**
- Filtering overhead: Percentage of total compute spent on curation
- Threshold stability: Variance of $\tau^*$ across random seeds
- Calibration error: $|\hat{P} - P_{\text{actual}}|$ for scaling law predictions

#### 2.5.5 Statistical Analysis

**Sample Size Justification:**
Based on effect size $d = 0.83$ (targeting 2.5% accuracy improvement over 3% standard deviation), power analysis indicates $n \geq 25$ runs for 80% power at $\alpha = 0.05$.

**Hypothesis Testing:**
- Primary: Paired t-test comparing MVDC vs. fixed-threshold baseline
- Report: Mean difference, 95% confidence interval, Cohen's d, p-value

**Success Criteria:**
- Primary: ImageNet zero-shot accuracy > 38.5% with $p < 0.05$
- Secondary: Filtering overhead < 5% of training compute
- Falsification: Accuracy ≤ 33% triggers hypothesis rejection

### 2.6 Implementation Details

**Computational Requirements:**
- Proxy computation: Pre-computed CLIP scores from DataComp; perplexity computed using GPT-2 (~10 GPU-hours)
- Clustering: Faiss library with GPU acceleration (~2 GPU-hours for 128M samples)
- Bayesian optimization: GPyTorch implementation (~1 GPU-hour)
- Training: ViT-B/32 CLIP model following DataComp protocol

**Software Stack:**
- PyTorch 2.0+ for model training
- Faiss for efficient clustering
- BoTorch/GPyTorch for Bayesian optimization
- Weights & Biases for experiment tracking

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome:** We expect MVDC to achieve ImageNet zero-shot accuracy of 38.5-40% on DataComp-medium, representing a 2.5-4% improvement over the fixed-threshold baseline (36%) while maintaining filtering overhead below 5% of total training compute.

**Mechanistic Findings:**
1. **Threshold-Compute Relationship:** We predict a monotonic relationship where optimal threshold $\tau^*$ decreases as compute budget increases, formalized as $\frac{\partial \tau^*}{\partial C} < 0$.

2. **Efficiency Gains:** Performance-per-FLOP improvements of 5-15% over fixed baselines, with larger gains at constrained compute budgets.

3. **Proxy Validity:** Strong positive correlation ($r > 0.6$) between cluster-aggregated proxy scores and actual training value contribution.

### 3.2 Scientific Contributions

1. **Theoretical Framework:** First principled integration of Bayesian optimization with scaling laws for compute-aware data curation, providing a mathematical foundation for the quality-quantity tradeoff.

2. **Scalable Algorithm:** Demonstration that cluster-based value estimation achieves comparable accuracy to per-sample methods with 100x computational speedup, enabling billion-scale curation.

3. **Empirical Insights:** Characterization of how optimal filtering strategies vary with compute budget, informing future benchmark design and evaluation protocols.

### 3.3 Practical Impact

**For Practitioners:**
- Ready-to-use filtering pipeline compatible with DataComp and similar benchmarks
- Guidelines for threshold selection based on available compute budget
- Reduced training costs through improved data efficiency

**For the Research Community:**
- New baseline for compute-aware data curation methods
- Open-source implementation and pre-computed proxy scores
- Contribution to data-centric ML benchmarks (DataPerf, DataComp)

**Broader Impact:**
- Democratization of foundation model training by enabling competitive results with limited resources
- Reduced environmental impact through improved compute efficiency
- Framework extensible to new domains and modalities as quality proxies become available

### 3.4 Limitations and Future Work

**Known Limitations:**
- Requires pre-computed quality proxies, limiting applicability to novel modalities
- Cluster granularity may miss high-value outlier samples
- Initial pilot runs needed for Bayesian calibration add overhead

**Future Directions:**
- Extension to streaming data scenarios with online threshold adaptation
- Integration with active learning for iterative data collection
- Application to multimodal and cross-domain foundation models
- Development of domain-agnostic quality proxies using self-supervised methods

### 3.5 Timeline and Milestones

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Pilot experiments | 4 weeks | Scaling law calibration, proxy validation |
| Main experiments | 8 weeks | Primary results on DataComp-medium |
| Ablation studies | 4 weeks | Mechanism validation, sensitivity analysis |
| Analysis & writing | 4 weeks | Paper submission, code release |

This research directly addresses the workshop's focus on data-centric approaches for foundation models, contributing novel methodology for dataset construction and quality signals while engaging with established benchmarks like DataComp. By bridging data valuation theory with practical training considerations, MVDC represents a significant step toward principled, compute-aware data curation at scale.