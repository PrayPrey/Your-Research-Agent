# Research Proposal: Learning Invariant Representations through Multi-Environment Causal Discovery with Minimal Supervision

## 1. Title

**Automated Discovery of Causal Invariances for Domain Generalization: A Weakly-Supervised Contrastive Framework with Statistical Certification**

## 2. Introduction

### Background

Domain generalization (DG) represents one of the most critical challenges in modern machine learning: training models that perform reliably under distribution shifts encountered during deployment. Despite significant research efforts, general-purpose DG approaches have consistently failed to outperform empirical risk minimization (ERM) baselines across diverse benchmarks. This persistent failure suggests a fundamental gap in our understanding of what enables successful generalization beyond the training distribution.

Recent theoretical work has established that successful domain generalization requires exploiting invariant relationships—those causal mechanisms that remain stable across environments. However, existing causal approaches to DG face a practical dilemma: they either require extensive domain expertise to specify causal structures manually, assume access to perfectly labeled domain annotations, or depend on unrealistic assumptions about domain diversity in training data. This creates a significant barrier to deploying robust ML systems in real-world scenarios where such supervision is expensive, unavailable, or infeasible to obtain.

The challenge is further compounded by the prevalence of spurious correlations in observational data. Models naturally exploit any statistical regularity available during training, including environment-specific shortcuts that fail to transfer. For instance, a model trained to recognize cows might learn to rely on grassy backgrounds if such correlations exist in training domains, leading to catastrophic failures when encountering cows in different settings.

### Research Objectives

This research proposes a novel framework that bridges the gap between theoretically sound causal DG approaches and practical deployment constraints. Our primary objectives are:

1. **Develop an automated environment discovery mechanism** that leverages weak supervision (timestamps, coarse metadata, or clustering signals) to partition training data into meaningful environments without requiring explicit domain annotations.

2. **Design a contrastive causal discovery algorithm** that automatically identifies invariant predictive features by contrasting their behavior across discovered environments, while actively penalizing spuriously correlated features.

3. **Establish statistical certification procedures** that quantify confidence in discovered invariances and provide actionable uncertainty estimates about generalization capability.

4. **Validate the framework** on standard DG benchmarks, demonstrating superior performance compared to ERM and existing DG methods while using only minimal supervision.

### Significance

This research addresses several critical gaps in the domain generalization literature:

**Practical Applicability**: By requiring only weak supervision rather than full domain annotations or causal graphs, our approach makes robust generalization accessible to practitioners lacking deep domain expertise or extensive labeling resources.

**Theoretical Grounding**: Unlike heuristic data augmentation or learning strategies, our method is grounded in causal principles that provide formal guarantees about when and why generalization should succeed.

**Interpretability**: The framework produces human-interpretable invariant features and confidence scores, enabling practitioners to understand model behavior and make informed decisions about deployment.

**Bridging Theory and Practice**: This work operationalizes recent theoretical insights about invariant risk minimization and causal inference in a practical algorithm that can be applied to real-world problems.

The anticipated impact extends beyond academic contributions to practical ML deployment, particularly in high-stakes domains like healthcare, autonomous systems, and scientific discovery where distribution shifts are common and reliability is paramount.

## 3. Methodology

Our proposed framework consists of three integrated components: automated environment partitioning, contrastive causal discovery, and invariance certification. We detail each component below.

### 3.1 Data Collection and Preprocessing

**Datasets**: We will evaluate our method on established DG benchmarks including:
- PACS (Photo, Art, Cartoon, Sketch domain shifts)
- VLCS (different object recognition datasets)
- OfficeHome (office environment variations)
- DomainNet (large-scale multi-domain dataset)
- Camelyon17 (medical imaging with hospital shifts)

**Weak Supervision Sources**: For each dataset, we assume access to one or more of:
- Temporal metadata (collection timestamps)
- Coarse grouping labels (batches, sources)
- High-dimensional covariates suitable for clustering
- Partial domain annotations (10-20% labeled)

### 3.2 Automated Environment Partitioning

The first challenge is discovering meaningful environments from weakly supervised data. We propose a hierarchical approach:

**Step 1: Feature Extraction**
Extract high-level representations using a pretrained encoder $\phi_{\text{init}}: \mathcal{X} \rightarrow \mathbb{R}^d$. For images, we use ResNet-50 pretrained on ImageNet; for other modalities, appropriate foundation models.

**Step 2: Environment Discovery via Distributional Clustering**

We formulate environment discovery as clustering in representation space, with the objective of maximizing between-environment distributional distance while maintaining within-environment coherence. Define the environment assignment function $e: \{1, \ldots, N\} \rightarrow \{1, \ldots, K\}$ where $K$ is the number of environments.

The clustering objective combines three terms:

$$\mathcal{L}_{\text{env}} = \mathcal{L}_{\text{sep}} + \lambda_1 \mathcal{L}_{\text{coh}} + \lambda_2 \mathcal{L}_{\text{weak}}$$

where:

- **Separation loss** encourages distributional distance between environments:
$$\mathcal{L}_{\text{sep}} = -\sum_{k \neq k'} D_{\text{MMD}}(P_k, P_{k'})$$
where $D_{\text{MMD}}$ is the Maximum Mean Discrepancy between environment distributions $P_k$ and $P_{k'}$.

- **Coherence loss** ensures environments are internally consistent:
$$\mathcal{L}_{\text{coh}} = \sum_{k=1}^K \mathbb{E}_{(x_i, x_j) \sim P_k}[\|\phi_{\text{init}}(x_i) - \phi_{\text{init}}(x_j)\|^2]$$

- **Weak supervision loss** incorporates available metadata:
$$\mathcal{L}_{\text{weak}} = -\sum_{i=1}^N \log p(m_i | e(i))$$
where $m_i$ represents available metadata for sample $i$.

We optimize this objective using differentiable clustering (e.g., soft k-means with Gumbel-softmax) or spectral methods depending on dataset size.

### 3.3 Contrastive Causal Discovery

Given discovered environments $\mathcal{E} = \{E_1, \ldots, E_K\}$, we learn invariant representations through a novel contrastive objective.

**Causal Model**: We assume a structural causal model where:
- $S$: spurious features (environment-dependent)
- $C$: causal features (environment-invariant)
- $Y$: target label
- $E$: environment

The data generation process follows: $E \rightarrow S \rightarrow X \leftarrow C \rightarrow Y$

**Architecture**: Our model consists of:
1. Feature encoder: $f_{\theta}: \mathcal{X} \rightarrow \mathbb{R}^d$
2. Causal feature extractor: $g_{\text{causal}}: \mathbb{R}^d \rightarrow \mathbb{R}^{d_c}$
3. Spurious feature extractor: $g_{\text{spur}}: \mathbb{R}^d \rightarrow \mathbb{R}^{d_s}$
4. Classifier: $h: \mathbb{R}^{d_c} \rightarrow \mathcal{Y}$

**Contrastive Invariance Loss**: For causal features to be invariant, their relationship with $Y$ should remain stable across environments. We define:

$$\mathcal{L}_{\text{inv}} = \sum_{k=1}^K w_k \cdot \mathcal{R}_k(h \circ g_{\text{causal}} \circ f_{\theta})$$

where $\mathcal{R}_k$ is the risk in environment $k$, and $w_k$ are adaptive weights that upweight environments with higher risk to enforce worst-case robustness:

$$w_k = \frac{\exp(\eta \cdot \mathcal{R}_k)}{\sum_{j=1}^K \exp(\eta \cdot \mathcal{R}_j)}$$

**Contrastive Spurious Penalty**: To identify spurious features, we maximize their variation across environments:

$$\mathcal{L}_{\text{spur}} = -\frac{1}{K(K-1)}\sum_{k \neq k'} D_{\text{KL}}(p(g_{\text{spur}}(f(X))|E=k) \| p(g_{\text{spur}}(f(X))|E=k'))$$

**Independence Constraint**: Enforce statistical independence between causal and spurious features using HSIC (Hilbert-Schmidt Independence Criterion):

$$\mathcal{L}_{\text{ind}} = \text{HSIC}(g_{\text{causal}}(f(X)), g_{\text{spur}}(f(X)))$$

**Total Objective**:
$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{inv}} + \alpha \mathcal{L}_{\text{spur}} + \beta \mathcal{L}_{\text{ind}} + \gamma \|\theta\|^2$$

where $\alpha, \beta, \gamma$ are hyperparameters controlling the trade-off between objectives.

### 3.4 Invariance Certification

To provide confidence in discovered invariances, we develop statistical tests:

**Cross-Environment Risk Variance Test**: For truly invariant features, classification risk should be similar across environments. We compute:

$$\sigma^2_{\text{risk}} = \frac{1}{K}\sum_{k=1}^K (\mathcal{R}_k - \bar{\mathcal{R}})^2$$

where $\bar{\mathcal{R}} = \frac{1}{K}\sum_{k=1}^K \mathcal{R}_k$. We construct confidence intervals using bootstrap resampling.

**Causal Effect Stability Test**: We employ a conditional independence test to verify that the relationship between causal features and labels is stable:

$$H_0: P(Y|g_{\text{causal}}(X), E=k) = P(Y|g_{\text{causal}}(X), E=k') \quad \forall k, k'$$

We use the Hilbert-Schmidt Conditional Independence Criterion (HSCIC) as the test statistic, with permutation testing for p-values.

**Generalization Confidence Score**: We define a composite score:

$$\text{GCS} = \alpha_1 \exp(-\sigma^2_{\text{risk}}) + \alpha_2 (1 - p_{\text{HSCIC}}) + \alpha_3 \mathcal{I}_{\text{pred}}$$

where $\mathcal{I}_{\text{pred}}$ measures prediction consistency across environment-transformed versions of test samples.

### 3.5 Experimental Design

**Training Protocol**:
1. Phase 1 (5 epochs): Environment discovery with frozen pretrained encoder
2. Phase 2 (50 epochs): Joint training of all components with $\mathcal{L}_{\text{total}}$
3. Phase 3 (10 epochs): Fine-tuning with invariance constraints tightened

**Baselines**: We compare against:
- ERM (Empirical Risk Minimization)
- IRM (Invariant Risk Minimization)
- CORAL (Deep CORAL)
- DANN (Domain Adversarial Neural Networks)
- Mixup and related augmentation methods
- Recent methods: SDCL, DDN, ICRL

**Evaluation Protocol**: Standard leave-one-domain-out evaluation where each domain serves as test set while others form training set.

**Metrics**:
- **Accuracy**: Standard classification accuracy on held-out domains
- **Worst-case accuracy**: Minimum accuracy across all test domains
- **Average accuracy**: Mean accuracy across test domains
- **Calibration**: Expected Calibration Error (ECE)
- **Invariance Quality**: $\sigma^2_{\text{risk}}$ and HSCIC scores
- **Efficiency**: Number of samples requiring domain labels (for partial supervision variants)

**Statistical Significance**: All experiments run with 5 random seeds, reporting mean and standard deviation. Paired t-tests for significance at $p < 0.05$.

**Ablation Studies**:
1. Effect of environment discovery quality (varying $K$, weak supervision strength)
2. Impact of each loss component ($\mathcal{L}_{\text{spur}}$, $\mathcal{L}_{\text{ind}}$)
3. Sensitivity to hyperparameters ($\alpha$, $\beta$, $\gamma$, $\eta$)
4. Comparison of different weak supervision sources

**Interpretability Analysis**: We will visualize learned causal vs. spurious features using t-SNE, analyze feature attributions via GradCAM, and conduct user studies to assess interpretability of discovered invariances.

## 4. Expected Outcomes & Impact

### Expected Technical Outcomes

**Performance Improvements**: We anticipate 3-7% accuracy improvements over ERM baselines on standard DG benchmarks, with more substantial gains (10-15%) on datasets with strong spurious correlations. Crucially, we expect consistent improvements across diverse domains, addressing the reproducibility issues plaguing current DG methods.

**Reduced Supervision Requirements**: The framework should successfully operate with only 10-20% labeled domain information or purely temporal/batch metadata, reducing annotation costs by 80-90% compared to fully supervised DG methods.

**Reliable Uncertainty Estimates**: The certification component should provide calibrated confidence scores that correlate strongly (Pearson's $r > 0.7$) with actual test performance, enabling practitioners to make informed deployment decisions.

**Interpretable Invariances**: We expect to extract human-interpretable invariant features that domain experts can validate, providing transparency currently lacking in black-box DG approaches.

### Scientific Contributions

**Theoretical Insights**: This work will provide empirical validation of recent causal DG theory while identifying practical challenges in operationalizing these principles. We will characterize conditions under which automated environment discovery succeeds and establish sample complexity bounds.

**Methodological Innovations**: The contrastive causal discovery framework represents a novel approach to disentangling invariant from spurious features without full supervision. The certification procedures offer new tools for validating learned representations.

**Benchmark Contributions**: We will release comprehensive evaluation results, trained models, and discovered environments for major DG benchmarks, facilitating reproducible research.

### Practical Impact

**Accessible Robust ML**: By eliminating extensive supervision requirements, this framework democratizes access to robust ML, enabling smaller organizations and research groups to deploy reliable systems.

**High-Stakes Applications**: The combination of improved generalization and certified confidence makes the approach particularly valuable in healthcare, autonomous vehicles, and scientific domains where distribution shifts are common and failures costly.

**Deployment Guidelines**: The research will produce actionable guidelines for practitioners on when and how to apply the framework, including diagnostic tools for assessing whether sufficient environment diversity exists in training data.

### Broader Impact

**Bridging Communities**: This work connects causal inference, representation learning, and domain generalization communities, fostering cross-pollination of ideas.

**Educational Value**: The interpretable nature of discovered invariances provides pedagogical value, helping students and practitioners build intuition about what enables generalization.

**Societal Benefits**: More reliable ML systems reduce risks of algorithmic failures that disproportionately affect marginalized populations who may be underrepresented in training distributions.

### Limitations and Future Directions

We acknowledge several limitations that suggest future research directions:

1. **Environment Discovery Challenges**: When true environments are highly overlapping, automated discovery may struggle. Future work should explore active learning approaches to gather discriminative weak supervision.

2. **Computational Costs**: The framework requires training multiple components jointly. Investigation of efficient approximations and distillation procedures could improve scalability.

3. **Theoretical Guarantees**: While grounded in causal principles, formal generalization bounds for the complete framework remain an open problem requiring theoretical analysis.

4. **Extension to Other Shifts**: The current focus is on domain shift; extending to label shift, concept drift, and other distribution changes represents important future work.

Despite these limitations, we believe this research represents a significant step toward practical, theoretically grounded domain generalization that can be deployed in real-world systems with confidence.