# Research Proposal: Adaptive Compute Scaling for Scientific Foundation Models via Uncertainty-Guided Inference

## 1. Introduction

### Background

The application of artificial intelligence to scientific discovery has entered a transformative era, with foundation models demonstrating remarkable capabilities across diverse domains including molecular property prediction, protein structure determination, climate modeling, and materials discovery. However, a fundamental inefficiency plagues current scientific foundation models: they apply uniform computational resources regardless of problem complexity. A simple water molecule receives the same computational treatment as a complex protein-ligand interaction; a laminar flow simulation consumes resources identical to those allocated for turbulent cascade phenomena.

This uniform compute paradigm creates a critical bottleneck in scaling AI for science. The escalating costs of training and deploying frontier AI models, as documented in recent analyses showing exponential growth in computational requirements, demand more intelligent resource allocation strategies. Scientific problems exhibit vastly heterogeneous complexity distributions—estimates suggest that 60-80% of routine scientific predictions could be handled by significantly smaller computational budgets, while the remaining challenging cases may require even more compute than currently allocated.

The intersection of uncertainty quantification and adaptive computation presents a promising yet underexplored direction. Recent advances in uncertainty-aware architectures, including Nested Subspace Networks (NSNs) that enable dynamic compute adjustment across continuous budgets, and frameworks like AdaThink-Med that calibrate reasoning length based on problem difficulty, demonstrate the feasibility of adaptive computation. Similarly, work on decomposing aleatoric and epistemic uncertainty in deep features provides principled foundations for complexity estimation. However, these advances have not been systematically applied to scientific foundation models, where domain-specific structure such as physical symmetries, conservation laws, and multi-scale phenomena offer unique opportunities for informed compute allocation.

### Research Objectives

This research proposes to develop **Uncertainty-Aware Adaptive Compute (UAAC)** mechanisms for scientific foundation models that dynamically scale inference-time computation based on estimated problem complexity. Our specific objectives are:

1. **Design a domain-aware complexity estimation module** that leverages both learned uncertainty estimates and physics-informed priors to predict computational requirements for scientific inputs.

2. **Develop adaptive depth and width routing mechanisms** that efficiently allocate transformer layers and expert networks based on complexity estimates while maintaining differentiability for end-to-end training.

3. **Create uncertainty-calibrated output frameworks** that provide scientists with reliable confidence intervals and interpretable indicators of model extrapolation.

4. **Validate the approach** across multiple scientific domains, demonstrating improved Pareto frontiers between computational cost, prediction accuracy, and interpretability.

### Significance

This research addresses a fundamental challenge in scaling AI for science: the mismatch between uniform compute allocation and heterogeneous problem complexity. Success would yield: (1) 3-5× inference speedup on routine predictions, dramatically reducing deployment costs; (2) improved accuracy on complex cases through targeted compute allocation; (3) enhanced interpretability through explicit uncertainty quantification; and (4) new scientific insights into neural network difficulty landscapes across scientific domains. These outcomes directly advance the workshop's central questions about how scaling can be optimized in AI for Science and how it transforms the methodology-interpretability-discovery Pareto frontier.

## 2. Methodology

### 2.1 Overall Framework Architecture

The UAAC framework consists of three integrated components operating on a scientific foundation model backbone $f_\theta$:

$$\text{UAAC}(x) = \text{Router}(\text{CEst}(x), f_\theta) \rightarrow (\hat{y}, \sigma_{\text{alea}}, \sigma_{\text{epi}}, c)$$

where $x$ is the scientific input (molecular graph, simulation state, etc.), $\hat{y}$ is the prediction, $\sigma_{\text{alea}}$ and $\sigma_{\text{epi}}$ are aleatoric and epistemic uncertainty estimates, and $c$ is a calibrated confidence score.

### 2.2 Complexity Estimation Module (CEst)

The complexity estimation module predicts problem hardness from input features using a lightweight network that combines learned representations with domain-specific priors.

**Architecture**: We employ a small transformer encoder $g_\phi$ that processes the initial embedding of scientific inputs:

$$h_0 = \text{Embed}(x), \quad z = g_\phi(h_0)$$

where $z \in \mathbb{R}^d$ is a complexity-aware representation.

**Uncertainty Decomposition**: Following recent advances in uncertainty decomposition, we estimate:

1. *Epistemic uncertainty* via ensemble disagreement in feature space:
$$\sigma_{\text{epi}}^2(x) = \frac{1}{K}\sum_{k=1}^{K}\|z_k - \bar{z}\|^2$$
where $z_k$ are representations from $K$ stochastic forward passes using MC Dropout.

2. *Aleatoric uncertainty* via a heteroscedastic output head:
$$\sigma_{\text{alea}}^2(x) = \text{MLP}_{\text{alea}}(z)$$

**Domain-Specific Hardness Indicators**: We incorporate physics-informed features $\psi(x)$ that capture known complexity drivers:

- **Molecular systems**: Symmetry breaking indicators, ring strain, charge distribution variance, rare functional group presence
- **Fluid dynamics**: Reynolds number estimates, gradient magnitudes, boundary layer indicators
- **Materials science**: Defect density, phase boundary proximity, compositional complexity

The final complexity score combines learned and physics-informed components:

$$\kappa(x) = \text{MLP}_{\text{hard}}([z; \psi(x); \sigma_{\text{epi}}(x); \sigma_{\text{alea}}(x)])$$

**Training Objective**: The complexity estimator is trained with a difficulty-aware loss using oracle difficulty labels $d^*$ derived from prediction residuals on a held-out calibration set:

$$\mathcal{L}_{\text{CEst}} = \mathbb{E}_x\left[(\kappa(x) - d^*(x))^2 + \lambda_{\text{rank}}\mathcal{L}_{\text{ranking}}\right]$$

where $\mathcal{L}_{\text{ranking}}$ is a pairwise ranking loss ensuring proper ordering of complexity estimates.

### 2.3 Adaptive Depth/Width Routing

**Early Exit Mechanism**: We implement confidence-based early exits at intermediate transformer layers. Let $h_l$ denote hidden states at layer $l$ of an $L$-layer transformer. At designated exit points $\mathcal{E} = \{l_1, l_2, ..., l_E\}$, we compute:

$$p_{\text{exit}}^{(l)} = \sigma\left(\text{MLP}_{\text{exit}}^{(l)}(h_l) - \tau(\kappa(x))\right)$$

where $\tau(\kappa)$ is a complexity-dependent threshold function. The exit decision is:

$$\text{Exit at } l^* = \min\{l \in \mathcal{E} : p_{\text{exit}}^{(l)} > 0.5 \text{ or } l = L\}$$

**Mixture-of-Experts Routing**: For width adaptation, we employ a sparse mixture-of-experts (MoE) architecture where the number of activated experts scales with complexity:

$$n_{\text{experts}}(x) = \lceil n_{\min} + (n_{\max} - n_{\min}) \cdot \kappa(x) \rceil$$

The routing mechanism selects top-$n_{\text{experts}}(x)$ experts based on gating scores:

$$\text{MoE}(h) = \sum_{i \in \text{TopK}(G(h), n_{\text{experts}})} G_i(h) \cdot E_i(h)$$

where $G(h) = \text{softmax}(W_g h)$ are gating weights and $E_i$ are expert networks.

**Nested Subspace Integration**: Inspired by NSNs, we re-parameterize linear layers to enable continuous compute scaling:

$$W = U\Sigma V^T, \quad W_r = U_{:,:r}\Sigma_{:r,:r}V_{:,:r}^T$$

where rank $r$ is determined by $\kappa(x)$: $r(x) = \lceil r_{\min} + (r_{\max} - r_{\min}) \cdot \kappa(x) \rceil$.

### 2.4 Uncertainty-Calibrated Outputs

**Conformal Prediction Integration**: We employ split conformal prediction to provide valid coverage guarantees. Given calibration data $\{(x_i, y_i)\}_{i=1}^n$, we compute nonconformity scores:

$$s_i = \frac{|y_i - \hat{y}_i|}{\hat{\sigma}_i}$$

where $\hat{\sigma}_i = \sqrt{\sigma_{\text{alea}}^2(x_i) + \sigma_{\text{epi}}^2(x_i)}$. The prediction interval at confidence level $1-\alpha$ is:

$$\hat{C}_{1-\alpha}(x) = \left[\hat{y}(x) - q_{1-\alpha}\hat{\sigma}(x), \hat{y}(x) + q_{1-\alpha}\hat{\sigma}(x)\right]$$

where $q_{1-\alpha}$ is the $(1-\alpha)$ quantile of calibration scores.

**Extrapolation Detection**: We flag potential extrapolation when:

$$\text{OOD}(x) = \mathbb{1}\left[\sigma_{\text{epi}}(x) > \mu_{\text{epi}} + 2\sigma_{\text{epi,std}}\right]$$

### 2.5 Joint Training Procedure

The complete system is trained end-to-end with a multi-objective loss:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{task}} + \lambda_1\mathcal{L}_{\text{CEst}} + \lambda_2\mathcal{L}_{\text{compute}} + \lambda_3\mathcal{L}_{\text{calibration}}$$

where:
- $\mathcal{L}_{\text{task}}$: Domain-specific prediction loss (MSE, cross-entropy, etc.)
- $\mathcal{L}_{\text{compute}} = \mathbb{E}_x[c(x) \cdot (1 - \kappa(x))]$: Penalizes high compute on easy problems
- $\mathcal{L}_{\text{calibration}}$: Expected calibration error for uncertainty estimates

### 2.6 Experimental Design

**Datasets and Domains**:
1. **Molecular Property Prediction**: QM9, PCQM4Mv2, and OGB-LSC datasets
2. **Protein Structure**: CASP14/15 targets with varying structural complexity
3. **Fluid Dynamics**: Turbulent flow simulations from Johns Hopkins Turbulence Database
4. **Materials Science**: Materials Project database for formation energy prediction

**Baselines**:
- Fixed-compute foundation models (GNNs, transformers)
- Standard early-exit networks without uncertainty guidance
- Uniform MoE routing
- Post-hoc uncertainty quantification methods

**Evaluation Metrics**:
1. **Efficiency**: FLOPs reduction, inference latency, throughput
2. **Accuracy**: Task-specific metrics (MAE, RMSE, accuracy)
3. **Uncertainty Quality**: Expected Calibration Error (ECE), Brier score, coverage validity
4. **Pareto Analysis**: Multi-objective frontier visualization

**Ablation Studies**:
- Contribution of physics-informed features vs. learned complexity
- Impact of different routing mechanisms
- Sensitivity to hyperparameters $\lambda_1, \lambda_2, \lambda_3$

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Computational Efficiency**: We anticipate achieving 3-5× inference speedup on routine scientific predictions while maintaining or improving accuracy on complex cases. Preliminary estimates suggest 70% of molecular property predictions can exit early with <5% accuracy degradation.

2. **Improved Accuracy-Compute Trade-offs**: By reallocating saved compute to challenging instances, we expect 10-15% accuracy improvements on the hardest 10% of test cases, particularly for out-of-distribution scientific systems.

3. **Calibrated Uncertainty Estimates**: The framework will provide well-calibrated confidence intervals with valid coverage guarantees, enabling scientists to identify predictions requiring experimental validation.

4. **Interpretable Complexity Insights**: Analysis of learned complexity predictors will reveal what makes scientific problems computationally hard for neural networks, potentially discovering new structure-difficulty relationships.

### Scientific Impact

This research will fundamentally advance our understanding of scaling in AI for Science by demonstrating that intelligent compute allocation, rather than uniform scaling, better serves scientific discovery. The explicit separation of aleatoric and epistemic uncertainty provides interpretable signals about data quality versus model limitations, directly addressing the workshop's interest in how scaling changes the interpretability frontier.

### Practical Impact

The UAAC framework will enable: (1) deployment of powerful scientific foundation models on resource-constrained platforms; (2) real-time scientific predictions in experimental workflows; (3) principled identification of novel scientific systems requiring human expert attention; and (4) more sustainable AI for Science through reduced computational footprint.

### Broader Implications

By revealing the limitations of uniform scaling and providing principled alternatives, this work contributes to the workshop's inquiry into "the limitation of scaling and what is the cure for it." The methodology generalizes beyond scientific applications to any domain with heterogeneous problem complexity, establishing a new paradigm for efficient foundation model deployment.