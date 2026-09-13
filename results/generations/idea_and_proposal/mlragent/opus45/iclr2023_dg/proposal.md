# Research Proposal: Domain-Conditional Invariance Specification: A Framework for Encoding Expert Knowledge in Domain Generalization

## 1. Introduction

### Background

Domain generalization (DG) represents one of the most fundamental challenges in machine learning: developing models that can reliably perform under distribution shifts encountered in real-world deployment. Despite significant research efforts, a sobering finding persists—general-purpose DG methods have consistently struggled to outperform standard Empirical Risk Minimization (ERM) baselines across diverse benchmarks. This observation suggests that purely data-driven approaches to learning invariances may be fundamentally limited without additional sources of information.

The literature reveals a growing recognition of this limitation. Recent work by Long et al. (2025) on generative classifiers and Jin et al. (2025) on angular invariance demonstrates the community's ongoing search for better inductive biases. Vuong et al. (2025) provide theoretical insight into why DG methods fail, highlighting the necessity and sufficiency conditions that current approaches fail to satisfy. Meanwhile, work on causal invariance and rationale invariance (Chen et al., 2023) points toward the importance of identifying which features should remain stable across domains.

A critical observation motivates our research: in virtually every application domain, practitioners possess substantial prior knowledge about what should and should not vary across deployment conditions. A radiologist understands that diagnostic features of a tumor should be independent of the MRI scanner manufacturer. An autonomous vehicle engineer knows that object detection should be invariant to weather conditions but may legitimately vary with geographic region due to different vehicle types. Yet current DG frameworks provide no principled mechanism to encode such specifications.

### Research Objectives

This research proposes the **Differentiable Invariance Specification Language (DISL)**, a novel framework that bridges the gap between domain expertise and algorithmic robustness. Our specific objectives are:

1. **Design a formal specification language** that enables practitioners to declaratively express known invariances in an intuitive yet mathematically precise manner.

2. **Develop a compilation mechanism** that transforms human-readable specifications into differentiable loss terms that can be seamlessly integrated into gradient-based optimization.

3. **Create a confidence-weighted enforcement scheme** that handles uncertainty in specifications and gracefully resolves conflicts between constraints and empirical evidence.

4. **Validate the framework** through comprehensive experiments demonstrating that incorporating expert knowledge leads to measurable improvements in out-of-distribution generalization.

### Significance

This research addresses a fundamental gap identified in the workshop's call: the need for additional information sources to achieve successful domain generalization. By providing a structured mechanism for encoding prior knowledge, DISL offers several significant contributions:

- **Democratization of robustness**: Domain experts without deep ML expertise can contribute to model reliability through natural specifications.
- **Interpretable invariance learning**: Unlike black-box approaches, DISL makes the assumed invariances explicit and auditable.
- **Principled integration of causal knowledge**: The framework provides a practical implementation path for encoding causal assumptions about domain shift.

## 2. Methodology

### 2.1 Specification Language Design

We design DISL as a declarative language with the following grammar:

```
INVARIANCE_RULE := INVARIANT(target, domain_factors, conditional_factors, confidence)
```

Where:
- `target`: The prediction or representation component that should remain invariant
- `domain_factors`: Set of factors across which invariance should hold
- `conditional_factors`: Variables upon which the invariance is conditioned
- `confidence`: A score $c \in [0, 1]$ indicating the practitioner's certainty

**Example specifications**:
```
INVARIANT(prediction, {scanner_type, hospital}, {lesion_type}, 0.95)
INVARIANT(features[layer=4], {lighting, background}, {object_class}, 0.8)
INVARIANT(logits, {time_of_capture}, {}, 1.0)
```

Formally, we define an invariance specification as a tuple $\mathcal{I} = (t, D, C, c)$ where $t$ denotes the target function, $D = \{d_1, ..., d_k\}$ the domain factors, $C = \{c_1, ..., c_m\}$ the conditioning variables, and $c$ the confidence weight.

### 2.2 Constraint Compilation

Each specification $\mathcal{I}$ is compiled into a differentiable penalty term. We propose three complementary compilation strategies:

**Strategy 1: Distribution Matching**

For a specification requiring $t(x)$ to be invariant across domain factor $d$ given conditioning $C$, we minimize the Maximum Mean Discrepancy (MMD) between conditional distributions:

$$\mathcal{L}_{\text{MMD}}(\mathcal{I}) = \sum_{c \in \mathcal{C}} \sum_{d_i, d_j \in D} \text{MMD}^2\left( P(t(X) | C=c, d=d_i), P(t(X) | C=c, d=d_j) \right)$$

The MMD is computed using a Gaussian kernel:

$$\text{MMD}^2(P, Q) = \mathbb{E}_{x,x' \sim P}[k(x,x')] - 2\mathbb{E}_{x \sim P, y \sim Q}[k(x,y)] + \mathbb{E}_{y,y' \sim Q}[k(y,y')]$$

**Strategy 2: Gradient-Based Invariance**

Inspired by invariant risk minimization, we penalize the gradient of the target with respect to domain indicators:

$$\mathcal{L}_{\text{grad}}(\mathcal{I}) = \mathbb{E}_{x, c}\left[ \left\| \nabla_{d} t(x) \big|_{C=c} \right\|^2 \right]$$

This ensures that infinitesimal changes in domain factors do not affect the target.

**Strategy 3: Contrastive Invariance**

We construct positive pairs from samples sharing conditioning variables but differing in domain factors:

$$\mathcal{L}_{\text{contrastive}}(\mathcal{I}) = -\mathbb{E}_{(x_i, x_j) \in \mathcal{P}^+} \left[ \log \frac{\exp(\text{sim}(t(x_i), t(x_j))/\tau)}{\sum_{k} \exp(\text{sim}(t(x_i), t(x_k))/\tau)} \right]$$

where $\mathcal{P}^+ = \{(x_i, x_j) : C(x_i) = C(x_j), D(x_i) \neq D(x_j)\}$.

### 2.3 Confidence-Weighted Enforcement

The total invariance loss integrates all specifications with their confidence weights:

$$\mathcal{L}_{\text{inv}} = \sum_{i=1}^{N} c_i \cdot \lambda_i(t) \cdot \mathcal{L}_{\text{compile}}(\mathcal{I}_i)$$

where $\lambda_i(t)$ is an adaptive weight that decreases when the constraint conflicts with task performance:

$$\lambda_i(t) = \lambda_0 \cdot \exp\left(-\beta \cdot \max(0, \mathcal{L}_{\text{task}} - \mathcal{L}_{\text{task}}^{\text{baseline}})\right)$$

This mechanism allows graceful degradation when specified invariances are partially incorrect.

### 2.4 Complete Training Algorithm

**Algorithm 1: DISL Training**

**Input**: Training data $\mathcal{D} = \{(x_i, y_i, d_i)\}$, invariance specifications $\{\mathcal{I}_1, ..., \mathcal{I}_N\}$, model $f_\theta$

**Output**: Trained model parameters $\theta^*$

1. **Initialize** model parameters $\theta$, adaptive weights $\lambda_i = \lambda_0$
2. **Compile** each specification $\mathcal{I}_i$ into loss function $\mathcal{L}_i$
3. **For** epoch $= 1$ to $E$ **do**:
   - **For** each mini-batch $B \subset \mathcal{D}$ **do**:
     - Compute task loss: $\mathcal{L}_{\text{task}} = \frac{1}{|B|}\sum_{(x,y) \in B} \ell(f_\theta(x), y)$
     - **For** each specification $\mathcal{I}_i$ **do**:
       - Identify relevant samples based on $C_i, D_i$
       - Compute $\mathcal{L}_i$ using compiled constraint
       - Update $\lambda_i$ based on task loss degradation
     - Compute total loss: $\mathcal{L} = \mathcal{L}_{\text{task}} + \sum_i c_i \lambda_i \mathcal{L}_i$
     - Update $\theta \leftarrow \theta - \eta \nabla_\theta \mathcal{L}$
4. **Return** $\theta^*$

### 2.5 Experimental Design

**Datasets and Benchmarks**

We evaluate on standard DG benchmarks with added invariance annotations:

1. **PACS** (Photo, Art, Cartoon, Sketch): 7 classes, 4 domains
2. **DomainNet**: 345 classes, 6 domains  
3. **Camelyon17-WILDS**: Medical imaging with hospital as domain
4. **A custom Medical Imaging benchmark** with ground-truth scanner invariances

For each benchmark, we will create invariance annotation sets through:
- Expert consultation (for medical datasets)
- Synthetic ground-truth (for datasets with known generative factors)
- Crowdsourced specifications (to study robustness to noisy constraints)

**Baselines**

- ERM (Empirical Risk Minimization)
- IRM (Invariant Risk Minimization)
- GroupDRO (Distributionally Robust Optimization)
- CORAL (Domain alignment via covariance matching)
- DANN (Domain-adversarial training)
- Recent methods: GCDG, FedAlign, DIDM

**Evaluation Metrics**

1. **Out-of-domain accuracy**: Standard leave-one-domain-out protocol
2. **Invariance satisfaction score**: 
$$\text{ISS}(\mathcal{I}) = 1 - \frac{\mathcal{L}_{\text{compile}}(\mathcal{I})}{\mathcal{L}_{\text{compile}}^{\text{random}}}$$
3. **Specification efficiency**: Performance gain per constraint
4. **Robustness to specification noise**: Accuracy under corrupted constraints

**Ablation Studies**

- Compilation strategy comparison (MMD vs. gradient vs. contrastive)
- Confidence weighting impact
- Adaptive vs. fixed constraint weights
- Number and granularity of specifications

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Empirical Performance Gains**: We anticipate 3-8% improvement in out-of-domain accuracy over ERM baselines when appropriate invariance specifications are provided, with larger gains on datasets where domain shift aligns with specified factors.

2. **Invariance Verification**: Models trained with DISL will demonstrably satisfy specified invariances (ISS > 0.9), providing verifiable guarantees about model behavior.

3. **Robustness to Specification Quality**: The confidence-weighted enforcement will show graceful degradation, maintaining baseline performance even with 20-30% incorrect specifications.

4. **Practical Guidelines**: We will provide actionable recommendations for practitioners on how to elicit and formulate effective invariance specifications.

### Broader Impact

**Scientific Contributions**:
- First formal framework connecting declarative knowledge specification to differentiable learning
- Theoretical analysis of conditions under which expert specifications improve generalization
- Comprehensive benchmark with invariance annotations for future research

**Practical Applications**:
- Healthcare AI: Encoding known clinical invariances for robust diagnostic models
- Autonomous systems: Specifying safety-critical invariances for deployment across conditions
- Scientific discovery: Incorporating physical laws as invariance constraints

**Limitations and Future Work**:
- Current framework requires domain factors to be observed during training
- Extension to unsupervised domain discovery is a natural next step
- Integration with foundation models and prompt-based specification is an exciting direction

This research directly addresses the workshop's central question by demonstrating that expert knowledge, when properly encoded, provides the additional information necessary for successful domain generalization—transforming DG from a purely data-driven endeavor into a collaborative process between human expertise and machine learning.