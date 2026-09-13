# Adaptive Data Quality Signals via Multi-Armed Bandits for Streaming Foundation Model Training

## 1. Introduction

### Background

The training of large-scale foundation models has become increasingly dependent on massive, continuously growing datasets sourced from diverse origins including web scrapes, synthetic generation, and user-generated content. While recent years have witnessed remarkable advances in model architectures and scaling laws, the critical role of data quality has emerged as a fundamental bottleneck in achieving optimal model performance. Current approaches to data quality filtering predominantly rely on static thresholds and fixed combinations of quality signals—such as perplexity filters, CLIP scores, toxicity classifiers, and diversity metrics—determined through extensive manual tuning before training commences.

However, foundation model training represents a dynamic process where both the model's capabilities and the incoming data distributions evolve continuously. Static quality criteria fail to account for temporal shifts in data characteristics, changes in model needs at different training stages, and domain-specific variations that emerge in streaming data. For instance, early training stages may benefit from high-diversity, moderately-quality data to establish broad coverage, while later stages require high-precision, specialized examples for refinement. Similarly, as models develop stronger representations, previously filtered samples may become valuable, while initially acceptable data may become redundant.

This fundamental mismatch between static quality filters and dynamic training needs results in substantial inefficiencies: valuable training samples are discarded based on outdated criteria, computational resources are wasted on degraded data, and manual intervention is required to adjust thresholds as training progresses. Given that foundation models consume petaFLOPs of computation and process trillions of tokens, even modest improvements in data selection efficiency translate to significant resource savings and performance gains.

### Research Objectives

This research proposes a novel framework that fundamentally reconceptualizes data quality filtering as an adaptive, online learning problem. Specifically, we formulate quality signal selection as a contextual multi-armed bandit problem where different quality signals and their combinations compete as "arms," and the system learns to dynamically weight these signals based on their observed impact on model performance and training stability.

Our primary objectives are:

1. **Develop an adaptive data quality framework** that continuously adjusts quality signal weights throughout the training lifecycle based on real-time feedback from validation performance and training dynamics.

2. **Design efficient bandit algorithms** tailored to the computational constraints and evaluation latency inherent in foundation model training, enabling practical deployment at scale.

3. **Establish principled methodologies** for correlating quality signal combinations with downstream model performance across diverse domains including vision, language, and multimodal tasks.

4. **Demonstrate empirical improvements** in data efficiency, measured as improved validation performance with reduced data volume, alongside decreased requirements for manual hyperparameter tuning.

### Significance

This research addresses critical gaps at the intersection of data-centric machine learning and foundation model development. The proposed framework offers several transformative contributions:

**Scientific Impact**: We introduce a theoretically grounded approach to adaptive data curation that bridges reinforcement learning principles with large-scale model training, establishing new paradigms for online data quality optimization.

**Practical Impact**: By reducing data requirements by 15-30% while maintaining or improving model quality, our approach enables more sustainable and cost-effective foundation model training, democratizing access to these powerful technologies.

**Methodological Impact**: The framework provides a general-purpose solution applicable across domains and modalities, eliminating the need for extensive domain-specific quality signal engineering and manual threshold tuning.

**Broader Implications**: As foundation models increasingly serve critical applications, adaptive quality control becomes essential for maintaining performance under distribution shift, addressing a key challenge for deployed systems operating in dynamic environments.

## 2. Methodology

### 2.1 Problem Formulation

We formulate the adaptive data quality selection problem as a contextual multi-armed bandit with the following components:

**Arms (Actions)**: Let $\mathcal{A} = \{a_1, a_2, ..., a_K\}$ represent $K$ different quality signal configurations, where each arm $a_i$ corresponds to a weighted combination of base quality signals. For base signals $\{s_1, s_2, ..., s_M\}$ (e.g., perplexity, CLIP score, toxicity score), each arm is defined by a weight vector $\mathbf{w}_i = [w_{i,1}, ..., w_{i,M}]$ where $\sum_{j=1}^M w_{i,j} = 1$ and $w_{i,j} \geq 0$.

**Context**: At each decision epoch $t$, the system observes a context vector $\mathbf{x}_t \in \mathbb{R}^d$ encoding:
- Training stage indicators (step number, epoch, learning rate schedule position)
- Recent training dynamics (loss trajectory, gradient norms, validation metrics)
- Data domain distribution (source proportions, detected distribution shifts)
- Model state features (layer-wise activation statistics, representation quality)

**Reward Function**: The reward $r_t$ for selecting arm $a$ at time $t$ with context $\mathbf{x}_t$ is defined as:

$$r_t(a, \mathbf{x}_t) = \alpha \cdot \Delta\mathcal{V}_t - \beta \cdot \mathcal{C}_t + \gamma \cdot \mathcal{S}_t$$

where:
- $\Delta\mathcal{V}_t$ is the improvement in validation performance (perplexity reduction, accuracy gain)
- $\mathcal{C}_t$ represents computational cost per sample
- $\mathcal{S}_t$ measures training stability (reduced loss variance, gradient norm consistency)
- $\alpha, \beta, \gamma$ are tunable hyperparameters balancing objectives

**Data Selection**: For a batch of candidate samples $\mathcal{D}_t = \{d_1, ..., d_N\}$, each with quality signal evaluations $\mathbf{s}(d_i) = [s_1(d_i), ..., s_M(d_i)]$, the composite quality score under arm $a$ with weights $\mathbf{w}$ is:

$$Q(d_i, \mathbf{w}) = \mathbf{w}^T \mathbf{s}(d_i)$$

Samples with $Q(d_i, \mathbf{w}) > \tau$ are selected for training, where $\tau$ is a dynamic threshold adjusted to maintain target batch sizes.

### 2.2 Base Quality Signals

We incorporate a diverse set of quality signals spanning multiple dimensions:

1. **Perplexity-based filtering**: $s_{\text{ppl}}(d) = \exp\left(-\frac{1}{|d|}\sum_{i} \log p_{\theta_{\text{ref}}}(w_i|w_{<i})\right)$ using a reference language model

2. **Visual-semantic coherence**: $s_{\text{CLIP}}(d) = \cos(\text{CLIP}_v(I), \text{CLIP}_t(T))$ for image-text pairs

3. **Toxicity and safety**: $s_{\text{safety}}(d) = 1 - \max(\text{ToxicityClassifier}(d))$

4. **Diversity metrics**: $s_{\text{div}}(d) = \min_{d' \in \mathcal{B}_t} \text{distance}(d, d')$ measuring novelty relative to recent batches

5. **Domain-specific signals**: Task-relevant metrics such as code compilation success, mathematical proof validity, or factual consistency scores

### 2.3 Bandit Algorithm Design

We employ **Thompson Sampling with Linear Contextual Bandits** for its balance of exploration-exploitation and computational efficiency:

**Model Assumption**: Assume the expected reward for arm $a$ given context $\mathbf{x}_t$ follows:

$$\mathbb{E}[r_t | a, \mathbf{x}_t] = \mathbf{x}_t^T \boldsymbol{\theta}_a$$

where $\boldsymbol{\theta}_a \in \mathbb{R}^d$ represents arm-specific parameters to be learned.

**Bayesian Update**: Maintain Gaussian posterior distributions over parameters:

$$\boldsymbol{\theta}_a \sim \mathcal{N}(\boldsymbol{\mu}_a, \mathbf{\Sigma}_a)$$

Initialize with prior $\boldsymbol{\mu}_a^{(0)} = \mathbf{0}$, $\mathbf{\Sigma}_a^{(0)} = \lambda^{-1}\mathbf{I}$ where $\lambda$ is a regularization parameter.

**Algorithm Steps**:

At each decision epoch $t$:

1. **Sampling**: For each arm $a \in \mathcal{A}$, draw parameter sample:
   $$\tilde{\boldsymbol{\theta}}_a^{(t)} \sim \mathcal{N}(\boldsymbol{\mu}_a^{(t)}, \mathbf{\Sigma}_a^{(t)})$$

2. **Selection**: Choose arm with highest expected reward:
   $$a_t = \arg\max_{a \in \mathcal{A}} \mathbf{x}_t^T \tilde{\boldsymbol{\theta}}_a^{(t)}$$

3. **Execution**: Apply quality signal configuration $a_t$ to filter current data batch $\mathcal{D}_t$, obtaining filtered set $\mathcal{D}_t^*$

4. **Training**: Train model on $\mathcal{D}_t^*$ for $N_{\text{step}}$ gradient steps

5. **Observation**: Evaluate reward $r_t$ based on validation performance, cost, and stability metrics

6. **Update**: Update posterior for selected arm $a_t$:
   $$\mathbf{\Sigma}_{a_t}^{(t+1)} = \left(\left(\mathbf{\Sigma}_{a_t}^{(t)}\right)^{-1} + \mathbf{x}_t\mathbf{x}_t^T\right)^{-1}$$
   $$\boldsymbol{\mu}_{a_t}^{(t+1)} = \mathbf{\Sigma}_{a_t}^{(t+1)}\left(\left(\mathbf{\Sigma}_{a_t}^{(t)}\right)^{-1}\boldsymbol{\mu}_{a_t}^{(t)} + r_t\mathbf{x}_t\right)$$

### 2.4 Computational Efficiency Optimizations

To address computational constraints:

**Delayed Feedback Aggregation**: Accumulate multiple training steps before reward evaluation, amortizing validation costs:
$$r_t = \frac{1}{N_{\text{agg}}}\sum_{i=1}^{N_{\text{agg}}} r_{t,i}$$

**Hierarchical Arm Selection**: Organize arms in a two-level hierarchy: first select signal subset (coarse), then select weights (fine), reducing action space from $O(K^M)$ to $O(K \cdot M)$.

**Asynchronous Evaluation**: Maintain parallel evaluation streams where subset of batches use exploratory configurations while primary training continues with current best arm.

**Warm-start Initialization**: Pre-train posterior distributions using offline evaluation on historical training runs, accelerating initial convergence.

### 2.5 Experimental Design

#### 2.5.1 Datasets and Domains

We validate the framework across three domains:

1. **Language**: Pre-training transformer models (1B parameters) on C4 dataset subset (100B tokens) with continuous streaming

2. **Vision**: Training vision transformers on ImageNet-21k with synthetic augmentations and web-crawled images

3. **Multimodal**: Training CLIP-style models on CC12M and LAION-400M subsets with image-text pairs

#### 2.5.2 Baseline Comparisons

- **Static-Optimal**: Best fixed quality signal combination determined through grid search
- **Rule-based Scheduling**: Manual threshold adjustments at predefined training milestones
- **Random Selection**: Uniform random sampling from candidate arms
- **UCB Algorithm**: Upper confidence bound approach as alternative bandit algorithm
- **No Filtering**: Training on all available data without quality filtering

#### 2.5.3 Evaluation Metrics

**Primary Metrics**:
- **Data Efficiency**: Validation performance achieved per million samples processed
- **Sample Efficiency Ratio**: $(P_{\text{proposed}} - P_{\text{baseline}}) / N_{\text{proposed}}$ where $P$ is performance and $N$ is samples used
- **Regret**: Cumulative difference from oracle optimal arm selection

**Secondary Metrics**:
- Computational overhead percentage
- Convergence speed (steps to target performance)
- Robustness to distribution shift (performance on held-out domains)
- Quality signal utilization patterns over training

#### 2.5.4 Ablation Studies

1. **Context feature importance**: Evaluate with subsets of context features removed
2. **Reward function components**: Isolate contributions of validation, cost, and stability terms
3. **Update frequency**: Vary decision epoch intervals from per-batch to per-epoch
4. **Number of arms**: Test with 5, 10, 20, 50 arms to assess scalability
5. **Base signal variations**: Test with different subsets of quality signals

### 2.6 Implementation Details

The framework will be implemented in PyTorch with integration into existing training pipelines through modular interfaces. Key components include:

- **Signal Evaluation Module**: Batched computation of all quality signals with GPU acceleration
- **Bandit Controller**: Lightweight process managing arm selection and posterior updates
- **Monitoring Dashboard**: Real-time visualization of arm performance, signal weights, and training metrics
- **Checkpoint Management**: Periodic saving of bandit states for recovery and analysis

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Performance Improvements**: We anticipate 15-30% reduction in data requirements to achieve equivalent validation performance compared to static filtering baselines. This translates to proportional computational savings in GPU-hours and carbon emissions.

**Adaptivity Demonstrations**: The system should exhibit clear adaptation patterns:
- Higher diversity emphasis during early training (broad coverage)
- Increased quality signal weights during later training (refinement)
- Automatic response to distribution shifts with appropriate signal reweighting

**Cross-domain Generalization**: The framework should achieve consistent improvements across language, vision, and multimodal domains with minimal domain-specific tuning, demonstrating the universality of the approach.

**Reduced Manual Intervention**: Compared to baselines requiring extensive hyperparameter sweeps (hundreds of configurations), our approach should require only high-level objective specification (reward function weights), reducing human effort by orders of magnitude.

**Theoretical Insights**: Analysis of learned signal weights and context-reward relationships will provide new understanding of:
- Which quality signals matter most at different training stages
- How optimal quality criteria vary with model scale and architecture
- Generalizable patterns in data quality needs across domains

### 3.2 Scientific Impact

This research advances the theoretical foundations of data-centric machine learning by:

1. **Establishing principled frameworks** for online data curation in non-stationary learning environments
2. **Bridging reinforcement learning and dataset construction**, creating new research directions at their intersection
3. **Providing regret bounds and sample complexity analysis** for adaptive data filtering under realistic training constraints
4. **Contributing open-source implementations** that enable reproducible research and lower barriers to entry

### 3.3 Practical Impact

For practitioners and industry deployments:

**Cost Reduction**: 15-30% data efficiency improvements translate to millions of dollars in computational savings for organizations training foundation models, making these technologies more accessible to resource-constrained researchers.

**Operational Simplification**: Automated quality signal adaptation eliminates error-prone manual tuning, reducing engineering overhead and accelerating development cycles.

**Improved Model Quality**: Adaptive filtering enables models to benefit from a broader range of data throughout training, potentially improving generalization and robustness to distribution shift in deployed systems.

**Sustainability**: Reduced computational requirements directly decrease carbon emissions associated with foundation model training, supporting environmental sustainability goals.

### 3.4 Broader Implications

**Democratization**: By reducing both computational and human expert requirements for effective data curation, this framework lowers barriers to foundation model development for academic and non-profit organizations.

**Dynamic Environments**: The adaptive nature of our approach is particularly valuable for continual learning scenarios where models must incorporate new data distributions while maintaining performance on existing tasks.

**Ethical Considerations**: Adaptive toxicity and safety signal weighting enables more nuanced approaches to content moderation that evolve with changing social norms and emerging harmful patterns.

**Future Research Directions**: This work opens avenues for:
- Multi-objective bandits balancing performance, fairness, and efficiency
- Federated bandit approaches for collaborative data quality learning
- Integration with active learning for targeted data acquisition
- Extension to model architecture and hyperparameter selection

### 3.5 Validation and Dissemination

We will validate our claims through:
- Comprehensive experiments on publicly available datasets ensuring reproducibility
- Open-source release of implementation and trained models
- Submission to premier venues (NeurIPS, ICML, ICLR) and data-centric workshops
- Collaboration with industry partners for large-scale deployment validation

The expected timeline spans 12-18 months: 3 months for framework development, 6 months for comprehensive experimentation, 2 months for theoretical analysis, and 3 months for paper preparation and open-source release.

By addressing the critical challenge of adaptive data quality in foundation model training through principled bandit algorithms, this research contributes essential methodology for the next generation of data-centric machine learning systems, enabling more efficient, robust, and sustainable development of AI technologies that serve broad societal needs.