# Adaptive Multi-Fidelity Scaling for Scientific Foundation Models: Balancing Data Quality and Quantity

## 1. Introduction

### Background

The rapid advancement of artificial intelligence has catalyzed transformative changes across scientific disciplines, enabling researchers to model complex phenomena, accelerate hypothesis generation, and extract insights from unprecedented volumes of data. The success of foundation models in domains such as natural language processing and computer vision has inspired their application to scientific discovery, where models like AlphaFold for protein structure prediction and neural operators for solving partial differential equations (PDEs) have demonstrated remarkable capabilities. Central to these achievements is the scaling paradigm—the observation that larger models trained on more extensive datasets often yield superior performance.

However, the direct application of scaling principles from general AI to scientific domains encounters a fundamental challenge: the **multi-fidelity data problem**. Unlike text or image data that can be collected at relatively uniform quality, scientific data exists across a spectrum of fidelities. High-fidelity experimental measurements (e.g., cryo-EM protein structures, high-resolution climate observations, precise quantum chemistry calculations) are expensive, time-consuming, and scarce. Conversely, low-fidelity data (e.g., molecular dynamics simulations with approximate force fields, coarse-grained climate models, density functional theory calculations) are abundant but contain systematic biases and reduced accuracy.

Current scaling approaches in AI for Science predominantly assume homogeneous data quality, either limiting themselves to scarce high-fidelity data—thereby constraining model capacity—or indiscriminately mixing multi-fidelity data, which can introduce noise that degrades performance and obscures interpretability. Recent work on foundation models for PDEs (PDE-FM) and multi-fidelity surrogate modeling (MFRNP, D-MFDAL) has begun addressing heterogeneous data integration, but a comprehensive framework for intelligent scaling that optimally balances data quality and quantity remains elusive.

### Research Objectives

This research proposes to develop **Adaptive Multi-Fidelity Scaling (AMFS)**, a principled framework for training scientific foundation models that intelligently leverages heterogeneous data sources. Our specific objectives are:

1. **Develop a hierarchical curriculum learning strategy** that progressively trains models on data of increasing fidelity, preventing low-quality data from overwhelming high-fidelity signals while maximizing data efficiency.

2. **Design fidelity-aware architectural components** including learnable fidelity embeddings and adaptive fusion mechanisms that enable models to distinguish and appropriately weight information from different data sources.

3. **Establish information-theoretic principles for active data selection** that determine when scaling with additional low-fidelity data improves versus harms model performance, creating dynamic Pareto frontiers balancing scale, accuracy, and interpretability.

4. **Validate the framework across diverse scientific domains** including molecular property prediction, climate modeling, and computational fluid dynamics to demonstrate generalizability and establish domain-specific best practices.

### Significance

This research addresses critical questions posed by the AI for Science community regarding scaling:

- **How scaling can be done in AI for Science**: By providing a systematic methodology for scaling with heterogeneous multi-fidelity data rather than assuming uniform data quality.

- **How scaling changes the Pareto frontier**: By quantifying trade-offs between model scale, prediction accuracy, data acquisition costs, and interpretability in scientific applications.

- **Limitations of scaling and potential cures**: By identifying when naive scaling with low-quality data becomes counterproductive and providing adaptive mechanisms to mitigate these limitations.

The expected impact includes enabling scientific foundation models to achieve state-of-the-art performance with 10-100× less high-fidelity experimental data, reducing research costs, accelerating scientific discovery, and maintaining model interpretability crucial for scientific validation and hypothesis generation.

## 2. Methodology

### 2.1 Overall Framework Architecture

The AMFS framework consists of three interconnected components operating synergistically:

**Component 1: Hierarchical Multi-Fidelity Curriculum Learning (HMFCL)**

**Component 2: Fidelity-Aware Neural Architecture (FANA)**

**Component 3: Information-Theoretic Active Data Selection (ITADS)**

### 2.2 Hierarchical Multi-Fidelity Curriculum Learning

#### 2.2.1 Fidelity Hierarchy Construction

We formalize the multi-fidelity data landscape as follows. Let $\mathcal{D} = \{\mathcal{D}_1, \mathcal{D}_2, ..., \mathcal{D}_L\}$ represent datasets of increasing fidelity levels, where $\mathcal{D}_1$ contains the most abundant low-fidelity data and $\mathcal{D}_L$ contains scarce high-fidelity experimental data. Each dataset $\mathcal{D}_\ell$ consists of input-output pairs $\{(\mathbf{x}_i^\ell, y_i^\ell)\}_{i=1}^{N_\ell}$, where typically $N_1 >> N_2 >> ... >> N_L$.

The key insight is to model the relationship between fidelities as:

$$y^{\ell} = y^{\ell-1} + \delta^{\ell}(\mathbf{x}) + \epsilon^{\ell}$$

where $\delta^{\ell}$ represents the systematic correction from fidelity $\ell-1$ to $\ell$, and $\epsilon^{\ell}$ is observational noise with $\mathbb{E}[\epsilon^{\ell}] = 0$ and $\text{Var}(\epsilon^{\ell}) < \text{Var}(\epsilon^{\ell-1})$.

#### 2.2.2 Curriculum Training Strategy

The curriculum proceeds in $L$ stages:

**Stage 1 (Foundation)**: Pre-train the model $f_{\theta_1}$ on the abundant low-fidelity dataset $\mathcal{D}_1$ using standard supervised learning:

$$\theta_1^* = \arg\min_{\theta_1} \sum_{(\mathbf{x}, y) \in \mathcal{D}_1} \mathcal{L}(f_{\theta_1}(\mathbf{x}), y)$$

**Stage $\ell$ (Progressive Refinement, $\ell = 2, ..., L$)**: Fine-tune the model on fidelity level $\ell$ while retaining knowledge from lower fidelities using uncertainty-aware weighting:

$$\theta_\ell^* = \arg\min_{\theta_\ell} \left[\sum_{(\mathbf{x}, y) \in \mathcal{D}_\ell} w_\ell \mathcal{L}(f_{\theta_\ell}(\mathbf{x}, \ell), y) + \sum_{(\mathbf{x}, y) \in \mathcal{D}_{\ell-1}} w_{\ell-1}^{(\ell)} \mathcal{L}_{\text{KD}}(f_{\theta_\ell}(\mathbf{x}, \ell-1), f_{\theta_{\ell-1}}(\mathbf{x}, \ell-1))\right]$$

where $w_\ell$ and $w_{\ell-1}^{(\ell)}$ are adaptive weights, and $\mathcal{L}_{\text{KD}}$ is a knowledge distillation loss preserving lower-fidelity representations.

#### 2.2.3 Uncertainty-Aware Weighting

To prevent low-fidelity data from overwhelming high-fidelity signals, we introduce uncertainty-based sample weighting. For each data point, we estimate epistemic uncertainty $u(\mathbf{x})$ using Monte Carlo dropout or ensemble methods, and assign weights:

$$w(\mathbf{x}, \ell) = \frac{\alpha_\ell}{\alpha_\ell + u(\mathbf{x})}$$

where $\alpha_\ell$ is a fidelity-specific scaling parameter learned during training. This downweights uncertain predictions from lower fidelities while maintaining influence of confident predictions.

### 2.3 Fidelity-Aware Neural Architecture

#### 2.3.1 Fidelity Embedding Module

We introduce learnable fidelity embeddings $\mathbf{e}_\ell \in \mathbb{R}^{d_e}$ for each fidelity level $\ell$. These embeddings are concatenated with input representations to condition the model on data source:

$$\mathbf{h}_0 = \text{Encoder}(\mathbf{x}) \oplus \mathbf{e}_\ell$$

where $\oplus$ denotes concatenation. This explicit conditioning enables the model to learn fidelity-specific features and transformations.

#### 2.3.2 Multi-Fidelity Fusion Layers

We design adaptive fusion layers that combine information across fidelities. Following the residual learning paradigm from MFRNP, the model architecture consists of:

1. **Base predictor** $f_{\text{base}}(\mathbf{x})$ trained on aggregated low-fidelity data
2. **Residual predictors** $\{\delta_\ell(\mathbf{x})\}_{\ell=2}^L$ learning corrections at each fidelity level
3. **Attention-based fusion** mechanism weighting contributions:

$$f(\mathbf{x}, \ell) = f_{\text{base}}(\mathbf{x}) + \sum_{k=2}^{\ell} \alpha_k(\mathbf{x}) \delta_k(\mathbf{x})$$

where attention weights $\alpha_k(\mathbf{x}) = \text{softmax}(\mathbf{W}_k \mathbf{h}(\mathbf{x}))$ are computed from intermediate representations $\mathbf{h}(\mathbf{x})$.

#### 2.3.3 Cross-Fidelity Consistency Regularization

To encourage coherent representations across fidelities, we add a consistency regularization term:

$$\mathcal{L}_{\text{cons}} = \sum_{\ell=1}^{L-1} \mathbb{E}_{\mathbf{x}} \left[\|\mathbf{h}_\ell(\mathbf{x}) - \mathbf{h}_{\ell+1}(\mathbf{x})\|_2^2\right]$$

where $\mathbf{h}_\ell(\mathbf{x})$ are intermediate layer representations conditioned on fidelity $\ell$. This prevents the model from learning entirely disjoint representations for different fidelities.

### 2.4 Information-Theoretic Active Data Selection

#### 2.4.1 Value of Information Metric

We formulate active data selection as optimizing the value of information (VoI) per unit cost. For a candidate data point $\mathbf{x}^*$ at fidelity level $\ell$, the VoI is:

$$\text{VoI}(\mathbf{x}^*, \ell) = \mathbb{E}_{y \sim p(y|\mathbf{x}^*, \ell)} \left[D_{\text{KL}}(p(\theta|\mathcal{D} \cup \{(\mathbf{x}^*, y)\}, \ell) \| p(\theta|\mathcal{D}))\right]$$

This measures the expected reduction in posterior uncertainty over model parameters $\theta$ upon observing $(\mathbf{x}^*, y)$ at fidelity $\ell$.

#### 2.4.2 Cost-Aware Acquisition Function

Balancing information gain against acquisition cost $c_\ell$, we define:

$$(\mathbf{x}^*, \ell^*) = \arg\max_{\mathbf{x}, \ell} \frac{\text{VoI}(\mathbf{x}, \ell)}{c_\ell^\beta}$$

where $\beta \in [0, 1]$ controls the cost-sensitivity trade-off. Computing VoI exactly is intractable; we approximate using:

$$\text{VoI}(\mathbf{x}, \ell) \approx \mathbb{H}[p(y|\mathbf{x}, \ell)] - \mathbb{E}_{p(\theta|\mathcal{D})}[\mathbb{H}[p(y|\mathbf{x}, \theta, \ell)]]$$

representing the mutual information between predictions and model parameters.

#### 2.4.3 Dynamic Pareto Frontier Construction

We track the evolving Pareto frontier between model performance (measured by validation RMSE), total data acquisition cost, and interpretability (measured by fidelity attribution entropy). At each training iteration $t$, we record:

- Performance: $P(t) = \text{RMSE}_{\text{val}}(t)$
- Cost: $C(t) = \sum_{\ell=1}^L c_\ell N_\ell(t)$
- Interpretability: $I(t) = -\sum_{\ell=1}^L p_\ell(t) \log p_\ell(t)$

where $p_\ell(t)$ is the proportion of predictions primarily attributed to fidelity $\ell$ via gradient-based attribution. The Pareto frontier $\mathcal{F}(t) = \{(P, C, I)\}$ guides decisions on whether to acquire more data and at which fidelity.

### 2.5 Experimental Design and Validation

#### 2.5.1 Datasets and Domains

We validate AMFS across three scientific domains with natural multi-fidelity structures:

**Domain 1: Molecular Property Prediction**
- Low-fidelity: Semi-empirical quantum chemistry (PM6, AM1) calculations ($10^6$ molecules)
- Medium-fidelity: DFT with modest basis sets (B3LYP/6-31G*) ($10^5$ molecules)
- High-fidelity: Coupled-cluster calculations (CCSD(T)/aug-cc-pVTZ) and experimental measurements ($10^3$ molecules)
- Target properties: HOMO-LUMO gap, atomization energy, dipole moment

**Domain 2: Climate Modeling**
- Low-fidelity: Coarse-resolution climate simulations (100km grid, simplified physics) (1000 years)
- Medium-fidelity: Regional climate models (25km grid) (100 years)
- High-fidelity: Reanalysis data and observations (ERA5, station data) (40 years)
- Target variables: Temperature, precipitation, extreme event frequencies

**Domain 3: Computational Fluid Dynamics**
- Low-fidelity: RANS simulations with turbulence models ($10^5$ configurations)
- Medium-fidelity: LES at moderate resolution ($10^4$ configurations)
- High-fidelity: DNS and experimental measurements ($10^2$ configurations)
- Target quantities: Drag coefficients, velocity fields, pressure distributions

#### 2.5.2 Baseline Comparisons

We compare AMFS against:

1. **Single-fidelity baseline**: Model trained only on high-fidelity data
2. **Naive multi-fidelity**: Model trained on mixed multi-fidelity data with uniform weighting
3. **Transfer learning**: Pre-train on low-fidelity, fine-tune on high-fidelity without fidelity-awareness
4. **D-MFDAL**: Disentangled multi-fidelity deep active learning
5. **MFRNP**: Multi-fidelity residual neural processes
6. **PDE-FM** (for PDE-related tasks): Foundation model for PDEs with physics-aware conditioning

#### 2.5.3 Evaluation Metrics

**Prediction Performance**:
- Root Mean Square Error (RMSE) on held-out high-fidelity test set
- Mean Absolute Error (MAE)
- $R^2$ coefficient of determination
- Calibration error for uncertainty quantification

**Data Efficiency**:
- Performance vs. number of high-fidelity samples (learning curves)
- Cost-normalized performance: RMSE × total acquisition cost

**Interpretability**:
- Fidelity attribution scores: For each prediction, compute $\text{Attr}_\ell = \frac{\|\nabla_{\mathbf{e}_\ell} f(\mathbf{x})\|}{\sum_{k} \|\nabla_{\mathbf{e}_k} f(\mathbf{x})\|}$
- Feature importance consistency across fidelities
- Uncertainty decomposition by fidelity source

**Scalability**:
- Training time vs. dataset size
- Inference latency
- Memory consumption

#### 2.5.4 Ablation Studies

To validate individual components:

1. **Curriculum ordering**: Compare different fidelity orderings and simultaneous multi-fidelity training
2. **Uncertainty weighting**: Evaluate uniform vs. uncertainty-aware sample weights
3. **Architectural components**: Ablate fidelity embeddings, fusion mechanisms, consistency regularization
4. **Active selection strategies**: Compare VoI-based selection with random, uncertainty-based, and diversity-based sampling

#### 2.5.5 Hyperparameter Configuration

Key hyperparameters include:
- Fidelity embedding dimension: $d_e \in \{64, 128, 256\}$
- Curriculum stage lengths: proportional to dataset sizes with tunable scaling
- Uncertainty weighting parameters: $\alpha_\ell$ learned via gradient-based optimization
- Cost sensitivity: $\beta \in \{0.25, 0.5, 0.75\}$
- Consistency regularization weight: $\lambda_{\text{cons}} \in \{0.01, 0.1, 1.0\}$

We employ Bayesian optimization for hyperparameter tuning using validation performance as the objective.

## 3. Expected Outcomes & Impact

### 3.1 Anticipated Results

**Performance Gains**: We expect AMFS to achieve comparable or superior predictive accuracy to models trained on 10-100× more high-fidelity data. Specifically:
- In molecular property prediction: RMSE reduction of 30-50% compared to single-fidelity models with equivalent data budgets
- In climate modeling: Improved extreme event prediction with 20-40% fewer observational data points
- In fluid dynamics: Accurate surrogate models using 5-10× fewer expensive DNS simulations

**Cost Efficiency**: By intelligently leveraging low-fidelity data, we anticipate 50-80% reduction in total data acquisition costs while maintaining target performance thresholds, enabling scientific studies previously prohibitive due to resource constraints.

**Interpretability Preservation**: Unlike black-box scaling approaches, AMFS will maintain interpretability through:
- Transparent fidelity attribution revealing which data sources contribute to predictions
- Uncertainty decomposition identifying epistemic vs. aleatoric uncertainty sources
- Learned residual corrections interpretable as systematic bias corrections between fidelity levels

**Scalability Insights**: The dynamic Pareto frontier analysis will reveal:
- Domain-specific scaling laws relating data fidelity distributions to model performance
- Critical thresholds where additional low-fidelity data transitions from beneficial to detrimental
- Optimal data budgets balancing exploration (low-fidelity) and exploitation (high-fidelity)

### 3.2 Scientific Impact

**Accelerating Scientific Discovery**: AMFS directly addresses data scarcity bottlenecks in critical scientific domains:
- **Drug Discovery**: Reducing dependence on expensive wet-lab experiments by maximally leveraging computational predictions
- **Climate Science**: Enhancing long-term climate projections by optimally combining observations with multi-resolution simulations
- **Materials Design**: Enabling high-throughput screening with minimal costly synthesis and characterization

**Methodological Contributions**: The framework establishes principled guidelines for:
- Constructing curriculum learning strategies for heterogeneous scientific data
- Designing neural architectures that explicitly model data quality hierarchies
- Quantifying value of information in multi-fidelity contexts

**Bridging AI and Domain Sciences**: By providing transparent, interpretable multi-fidelity models, AMFS facilitates collaboration between AI researchers and domain scientists, addressing the critical need for trustworthy AI in scientific applications.

### 3.3 Broader Implications for Scaling in AI for Science

This research contributes to fundamental questions about scaling:

**Redefining Scaling Laws**: Traditional scaling laws (e.g., Chinchilla laws for language models) assume homogeneous data quality. AMFS will derive multi-fidelity scaling laws parameterized by fidelity distributions, providing theoretical grounding for data curation strategies.

**Interpretability-Performance Trade-offs**: By explicitly tracking interpretability metrics alongside performance, we quantify how scaling with heterogeneous data affects model transparency—crucial for scientific validation and regulatory compliance.

**Limitations and Future Directions**: The research will identify scenarios where multi-fidelity scaling fails:
- When systematic biases in low-fidelity data cannot be corrected
- When fidelity hierarchies are ill-defined or domain-dependent
- When computational overhead of fidelity-aware mechanisms outweighs benefits

Proposed cures include:
- Adversarial training to detect and mitigate systematic biases
- Meta-learning approaches to automatically discover fidelity relationships
- Hybrid symbolic-neural methods combining data-driven and physics-based corrections

### 3.4 Open Science and Reproducibility

To maximize impact, we commit to:
- Releasing open-source implementations of AMFS framework
- Providing curated multi-fidelity benchmark datasets across domains
- Publishing detailed ablation studies and negative results
- Creating interactive visualization tools for exploring Pareto frontiers

This comprehensive approach will establish AMFS as a foundational methodology for intelligent scaling in AI for Science, enabling researchers across disciplines to harness the full potential of heterogeneous scientific data while maintaining the interpretability and rigor essential to scientific progress.