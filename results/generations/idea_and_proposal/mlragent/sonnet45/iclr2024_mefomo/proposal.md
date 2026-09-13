# Research Proposal: Geometric Analysis of In-Context Learning: How Pre-training Data Structure Enables Few-Shot Adaptation

## 1. Introduction

### Background

Foundation models (FMs) have achieved remarkable success across diverse domains, yet their most striking capability—in-context learning (ICL)—remains poorly understood. ICL enables models to adapt to new tasks using only a few demonstration examples presented in the prompt, without any parameter updates. This emergent capability appears suddenly at scale and varies dramatically across different tasks and domains, raising fundamental questions about the conditions that enable it.

Recent empirical work has revealed intriguing patterns: language models exhibit stronger ICL capabilities than vision models, certain task types benefit more from ICL than others, and the quality and structure of pre-training data significantly impact ICL performance. Chen et al. (2024) demonstrated that parallel structures in pre-training data—pairs of phrases following similar templates within the same context window—are critical for ICL emergence. Yang et al. (2025) provided theoretical evidence that ICL exhibits an implicit bias toward low-frequency (smooth) representations through a "double convergence" mechanism. However, a unified framework connecting data structure, geometry, and ICL capability remains elusive.

The geometric perspective offers a promising lens for understanding ICL. If pre-training exposes models to tasks that lie on low-dimensional manifolds in the input-output space, the model may learn to identify and exploit these geometric regularities during inference. This hypothesis aligns with observations that ICL works best when demonstration examples share structural similarities with the query, and that models develop specialized attention patterns ("inductive heads") that facilitate pattern matching across contexts.

### Research Objectives

This research aims to establish a rigorous, predictive framework relating pre-training data geometry to in-context learning capability through the following specific objectives:

1. **Characterize the geometric properties of pre-training data** that enable ICL emergence, including manifold dimension, curvature, task diversity, and structural regularity.

2. **Develop quantitative metrics** to measure data geometry and predict ICL performance across different tasks and domains.

3. **Establish causal relationships** between specific geometric properties and ICL capability through controlled experiments on synthetic datasets.

4. **Validate the geometric framework** on real-world datasets by demonstrating that geometric measurements correlate with and predict ICL performance.

5. **Design data-efficient pre-training strategies** informed by geometric principles to maximize ICL capability with minimal data.

### Significance

This research addresses critical gaps in our understanding of foundation models identified by the workshop themes. First, it provides mathematical and empirical insights into how pre-training data structure enables emergent capabilities, directly addressing the workshop's focus on understanding FMs through rigorous characterization. Second, it offers practical guidance for data curation and selection, enabling more efficient pre-training strategies—a crucial consideration given the computational costs of training FMs. Third, by predicting which tasks will benefit from ICL based on their geometric properties, this work can guide adaptation strategies and inform decisions about when to use ICL versus fine-tuning.

The broader impact extends to making foundation models more accessible and interpretable. Understanding the geometric prerequisites for ICL can help practitioners design better datasets for specialized domains (e.g., medicine, scientific computing) where labeled data is scarce but ICL could be transformative. Furthermore, geometric analysis may reveal biases encoded in data structure, contributing to safety and alignment efforts.

## 2. Methodology

### 2.1 Theoretical Framework

We formalize ICL through the lens of meta-learning on task manifolds. Consider a distribution over tasks $\mathcal{T}$, where each task $\tau \in \mathcal{T}$ defines a function $f_\tau: \mathcal{X} \rightarrow \mathcal{Y}$. We hypothesize that ICL emerges when tasks exhibit geometric regularity—specifically, when task parameters lie on a low-dimensional manifold $\mathcal{M} \subset \mathbb{R}^d$ embedded in the function space.

**Definition 1 (Task Manifold):** A task manifold $\mathcal{M}$ is a $k$-dimensional smooth manifold in function space, where $k \ll d$, such that tasks $\{f_\tau\}_{\tau \in \mathcal{T}}$ can be parameterized by coordinates on $\mathcal{M}$.

We measure geometric properties using:

1. **Intrinsic Dimension**: $k = \dim(\mathcal{M})$, estimated using persistent homology and local dimensionality estimators.

2. **Curvature**: Gaussian curvature $K$ and sectional curvature to measure manifold smoothness.

3. **Reach**: $\text{reach}(\mathcal{M}) = \inf_{p \in \mathcal{M}} \|p - p'\|$ where $p'$ is the nearest point not on $\mathcal{M}$.

4. **Task Diversity Index**: 
$$\text{TDI}(\mathcal{T}) = \frac{1}{|\mathcal{T}|^2} \sum_{\tau_i, \tau_j \in \mathcal{T}} d_{\mathcal{M}}(\tau_i, \tau_j)$$
where $d_{\mathcal{M}}$ is the geodesic distance on the manifold.

**Hypothesis**: ICL capability $\mathcal{I}$ scales with:
$$\mathcal{I} \propto \frac{\text{TDI}(\mathcal{T}) \cdot \text{reach}(\mathcal{M})}{k \cdot (1 + K_{\text{avg}})}$$

This posits that ICL improves with task diversity and manifold reach, but deteriorates with high dimensionality and curvature (which increase learning complexity).

### 2.2 Synthetic Data Generation

We construct controlled synthetic datasets to isolate geometric properties:

**Dataset Family 1: Parametric Task Manifolds**

Generate tasks from explicit low-dimensional parameterizations:
- Linear manifolds: $f_{\theta}(x) = \theta^T x + b$, $\theta \in \mathbb{R}^k$
- Polynomial manifolds: $f_{\theta}(x) = \sum_{i=1}^k \theta_i x^i$
- Sinusoidal manifolds: $f_{\theta,\omega}(x) = \sum_{i=1}^k \theta_i \sin(\omega_i x + \phi_i)$

**Dataset Family 2: Structured Sequence Tasks**

Following Chen et al. (2024), create sequences with controlled parallel structures:
$$S = [t_1(c_1), t_2(c_1), ..., t_m(c_1), t_1(c_2), ..., t_m(c_2), ...]$$

where $t_i$ are template functions and $c_j$ are contexts. We vary:
- Number of parallel instances per context window
- Template diversity (manifold dimension)
- Context separation distance
- Noise levels

**Dataset Family 3: Geometric Variations**

Systematically vary geometric properties:
1. Dimension: $k \in \{2, 5, 10, 20, 50\}$
2. Curvature: Add nonlinear warping with controlled curvature
3. Noise: $f_{\tau, \epsilon}(x) = f_\tau(x) + \epsilon$, $\epsilon \sim \mathcal{N}(0, \sigma^2)$
4. Task diversity: Sample tasks from regions of varying density on the manifold

### 2.3 Model Training and Analysis

**Architecture**: We use decoder-only transformers with varying sizes (10M, 50M, 100M, 500M parameters) to study scaling effects.

**Training Protocol**:
1. Generate pre-training datasets with $10^6$ to $10^9$ tokens
2. Train with standard autoregressive objective: $\mathcal{L} = -\mathbb{E}[\log p_\theta(x_{t+1} | x_{\leq t})]$
3. Track ICL emergence during training by periodically evaluating on held-out tasks
4. Measure attention patterns, particularly inductive head formation

**ICL Evaluation**: For each task $\tau$, provide $n$ in-context examples $(x_1, y_1), ..., (x_n, y_n)$ and measure accuracy on query $(x_{n+1}, y_{n+1})$:
$$\text{ICL-Acc}(\tau, n) = \mathbb{E}_{(x,y) \sim \tau}[\mathbb{1}[\arg\max p_\theta(y|x, \text{context}) = y]]$$

**Mechanistic Analysis**:

1. **Attention Pattern Analysis**: Following the inductive heads hypothesis, measure:
$$\text{InductiveScore}_l = \frac{1}{H} \sum_{h=1}^H \text{corr}(A_h^{(l)}[i,j], \mathbb{1}[x_i = x_j])$$
   where $A_h^{(l)}$ is the attention matrix for head $h$ in layer $l$.

2. **Representation Geometry**: Analyze hidden representations $h_l(x)$ at layer $l$:
   - Measure local dimensionality using PCA on neighborhood embeddings
   - Compute alignment between representation manifold and task manifold
   - Track evolution across layers using neighborhood overlap metrics

3. **Gradient Flow Analysis**: Study how gradient information flows during pre-training:
$$G_\tau(l) = \mathbb{E}_{x \sim \tau}\left[\left\|\frac{\partial \mathcal{L}}{\partial h_l(x)}\right\|_2\right]$$

### 2.4 Real-World Dataset Validation

**Dataset Selection**: Analyze existing datasets across domains:
- **Language**: C4, The Pile, RedPajama (subsets)
- **Code**: The Stack, CodeParrot
- **Mathematics**: MATH, GSM8K pre-training corpora
- **Vision**: ImageNet (as sequences), COCO captions

**Geometric Measurement Pipeline**:

1. **Task Extraction**: Identify coherent tasks within datasets using:
   - Topic modeling (LDA, BERTopic) for language
   - Function clustering for code
   - Problem type classification for mathematics

2. **Manifold Reconstruction**: 
   - Embed tasks using pre-trained encoders
   - Apply manifold learning (UMAP, Isomap) to recover structure
   - Estimate intrinsic dimension using Maximum Likelihood Estimation (MLE) and correlation dimension methods

3. **Geometric Feature Computation**:
   - Local dimensionality: $k_{\text{local}}(x) = \arg\min_k \text{ReconstructionError}_k(x)$
   - Curvature estimation using discrete differential geometry
   - Task diversity via pairwise distance distributions

**Correlation Analysis**: 

Test the predictive power of geometric features:
$$\text{ICL-Acc} = \beta_0 + \beta_1 k + \beta_2 K + \beta_3 \text{TDI} + \beta_4 \text{reach} + \epsilon$$

Using multiple regression and cross-validation across datasets and model sizes.

### 2.5 Intervention Experiments

**Data Curation Based on Geometry**:

1. **Geometric Augmentation**: Enhance datasets by adding synthetic tasks that fill gaps in the task manifold
2. **Manifold-Aware Sampling**: Prioritize examples that improve manifold coverage
3. **Dimension Reduction**: Remove redundant tasks that don't contribute to manifold diversity

**Controlled Ablations**:
- Remove high-curvature regions and measure ICL degradation
- Subsample to reduce task diversity while maintaining other properties
- Add noise to increase effective manifold dimension

### 2.6 Evaluation Metrics

**Primary Metrics**:
1. **ICL Accuracy**: Performance on few-shot tasks $(n \in \{0, 1, 5, 10, 50\})$
2. **Geometric Alignment Score**: 
$$\text{GAS} = \text{corr}(\text{Predicted-ICL}, \text{Actual-ICL})$$
   based on geometric features

3. **Data Efficiency**: 
$$\text{DE} = \frac{\text{ICL-Acc}_{\text{geometric}}}{\text{ICL-Acc}_{\text{baseline}}} \times \frac{\text{Tokens}_{\text{baseline}}}{\text{Tokens}_{\text{geometric}}}$$

**Secondary Metrics**:
1. Inductive head formation rate and strength
2. Representation quality (linear probing accuracy)
3. Transfer learning performance across geometric regimes
4. Scaling behavior: $\text{ICL-Acc}(N, k) = A(k) + B(k) \log(N)$

## 3. Expected Outcomes & Impact

### 3.1 Theoretical Contributions

**Predictive Framework**: We expect to establish quantitative relationships between data geometry and ICL capability, formalized as scaling laws:
$$\text{ICL-Acc}(k, N, K, \text{TDI}) = f(k, K) \cdot g(N) \cdot h(\text{TDI})$$

This framework will enable practitioners to predict ICL performance from data analysis alone, without expensive model training.

**Mechanistic Understanding**: The research will clarify how geometric properties of data translate into learned model mechanisms (attention patterns, representations) that enable ICL. We anticipate demonstrating that:
- Low manifold dimension enables formation of task-specific inductive heads
- High task diversity promotes generalization across contexts
- Manifold curvature creates barriers to ICL that require larger models to overcome

### 3.2 Practical Outcomes

**Data Curation Guidelines**: Concrete recommendations for constructing pre-training datasets that maximize ICL capability:
- Target intrinsic dimensions for different model sizes
- Optimal task diversity levels to balance coverage and redundancy
- Strategies for identifying and amplifying parallel structures

**Domain-Specific Insights**: Explanations for why certain domains (language, code) exhibit stronger ICL than others (vision, audio), grounded in geometric analysis. This will guide domain adaptation strategies.

**Efficient Pre-training**: Demonstrations that geometry-informed data selection can achieve comparable ICL with 2-5× less data, making FM pre-training more accessible to resource-constrained researchers.

### 3.3 Broader Impacts

**Democratization of Foundation Models**: By reducing data requirements through principled selection, this research can enable smaller organizations to develop effective FMs for specialized domains where data is scarce but valuable (medical imaging, scientific simulations, low-resource languages).

**Interpretability and Safety**: Geometric analysis provides an interpretable lens for understanding model capabilities. Identifying geometric signatures of undesirable behavior (e.g., bias amplification, spurious correlations) could inform safety interventions and alignment strategies.

**Scientific Understanding**: This work advances fundamental understanding of how learning systems extract and exploit structure from data—a question relevant beyond FMs to neuroscience, cognitive science, and learning theory.

**Methodological Innovations**: The geometric measurement pipeline and synthetic dataset generation framework will serve as tools for future research on data quality, transfer learning, and emergent capabilities.

### 3.4 Validation and Success Criteria

The research will be considered successful if:

1. **Predictive Accuracy**: Geometric features predict ICL performance with $R^2 > 0.7$ across diverse tasks and model sizes
2. **Causal Evidence**: Controlled interventions on synthetic data geometry produce predicted changes in ICL capability (effect sizes > 0.3)
3. **Real-World Validation**: Geometry-curated datasets improve ICL performance by >20% compared to random sampling baselines
4. **Reproducibility**: Findings replicate across at least three distinct domains (language, code, mathematics)
5. **Practical Utility**: Data efficiency improvements of 2× or greater in resource-constrained settings

### 3.5 Timeline and Milestones

**Months 1-3**: Develop synthetic data generation framework and theoretical formalism
**Months 4-6**: Conduct controlled experiments on synthetic datasets, establish causal relationships
**Months 7-9**: Apply geometric measurement pipeline to real-world datasets, validate predictions
**Months 10-12**: Design and test geometry-informed data curation strategies, prepare comprehensive findings

This research promises to transform our understanding of in-context learning from an empirical curiosity into a predictable, controllable phenomenon grounded in data geometry—advancing both the science and practice of foundation models.