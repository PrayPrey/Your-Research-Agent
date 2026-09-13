# Research Proposal: Causal Attribution Networks for Discovering Mechanistic Pathways in Climate Tipping Points

## 1. Title

**Causal Attribution Networks for Discovering Mechanistic Pathways in Climate Tipping Points: A Physics-Constrained Deep Learning Framework for Explainable Climate Science**

## 2. Introduction

### 2.1 Background

Climate tipping points represent critical thresholds in Earth's climate system where small perturbations can trigger large-scale, potentially irreversible transitions between climate states. Examples include the collapse of the Atlantic Meridional Overturning Circulation (AMOC), Arctic sea ice loss, Amazon rainforest dieback, and permafrost thaw. While contemporary climate models can predict these events with increasing accuracy, they often function as "black boxes" that fail to provide mechanistic explanations for *why* and *how* these transitions occur. This explanatory gap undermines scientific understanding, limits our ability to develop effective intervention strategies, and reduces trust in climate predictions among policymakers and stakeholders.

Traditional post-hoc explainability methods in machine learning, such as saliency maps, SHAP values, and attention mechanisms, identify important features but cannot reveal the temporal causal chains and feedback mechanisms that characterize climate tipping points. For instance, knowing that Arctic ice extent is important for predicting temperature anomalies does not explain the multi-step causal pathway: ice melt → reduced albedo → increased solar absorption → regional warming → further ice loss. Understanding these mechanistic pathways is essential for identifying early warning signals, intervention points, and previously unknown feedback mechanisms.

Recent work has begun to address this gap. Högner et al. (2025) demonstrated causal discovery methods on observational data to identify stabilizing interactions between the AMOC and Southern Amazon Rainforest. Sleeman et al. (2023) introduced TIP-GAN for exploring parameter spaces to detect tipping points. Falasca (2025) proposed reduced-order neural stochastic models for investigating causal mechanisms in climate dynamics. However, these approaches either focus on specific climate subsystems, lack general frameworks for extracting interpretable causal pathways from deep learning models, or do not adequately incorporate physical constraints.

### 2.2 Research Objectives

This research proposes to develop **Causal Attribution Networks (CANs)**, a novel hybrid framework that combines physics-informed neural differential equations with structured causal discovery to identify and explain mechanistic pathways leading to climate tipping points. The specific objectives are:

1. **Develop a physics-constrained neural architecture** that learns climate dynamics while respecting fundamental physical laws (conservation laws, thermodynamic principles, temporal causality)

2. **Design causal extraction algorithms** that identify multi-step causal pathways from trained models, moving beyond single-variable attribution to reveal feedback loops and interaction chains

3. **Create validation frameworks** that assess discovered pathways against established climate mechanisms, reanalysis data, and expert knowledge

4. **Apply the framework** to multiple climate tipping point scenarios (AMOC collapse, Arctic-permafrost feedback, Amazon dieback) to demonstrate generalizability

5. **Generate actionable insights** including early warning indicators, intervention points, and testable hypotheses about unknown mechanisms

### 2.3 Significance

This research addresses critical gaps at the intersection of explainable AI (XAI) and climate science:

**Scientific Impact**: The framework will enable climate scientists to move beyond predictive accuracy to mechanistic understanding, facilitating hypothesis generation about unknown feedback mechanisms and improving process-based climate models.

**Methodological Contribution**: CANs represent a novel approach to post-hoc explainability that extracts structured causal knowledge rather than simple feature importance, applicable beyond climate science to other scientific domains involving complex dynamical systems.

**Societal Relevance**: Interpretable climate predictions with mechanistic explanations can inform evidence-based policy decisions, help identify leverage points for climate intervention, and build public trust in climate science during a critical period for climate action.

**Bridging ML and Domain Science**: By incorporating physical constraints and validating against domain knowledge, this work exemplifies responsible AI deployment in science, where models augment rather than replace human understanding.

## 3. Methodology

### 3.1 Overall Framework Architecture

The Causal Attribution Networks framework consists of three integrated components:

**Component 1**: Physics-Informed Neural Differential Equations (PI-NDEs) for learning climate dynamics
**Component 2**: Temporal Causal Graph Extraction via constrained attention mechanisms
**Component 3**: Multi-level validation against physical principles, reanalysis data, and expert knowledge

### 3.2 Data Collection and Preprocessing

**Climate Simulation Data**: We will utilize multiple sources:
- CMIP6 (Coupled Model Intercomparison Project Phase 6) ensemble simulations providing multi-model climate projections under various scenarios
- ERA5 reanalysis data (1979-present) offering high-resolution observational constraints
- High-resolution regional climate model outputs for specific tipping point regions
- Paleoclimate proxy data for historical tipping point events

**Variables of Interest**: For each tipping point scenario, we will select 20-30 key variables including:
- Thermodynamic variables (temperature, pressure, humidity)
- Dynamic variables (wind patterns, ocean currents)
- Radiative variables (albedo, cloud cover, radiation fluxes)
- Biogeochemical variables (vegetation indices, carbon fluxes, sea ice extent)

**Preprocessing Pipeline**:
1. Spatiotemporal alignment across different data sources
2. Anomaly calculation relative to baseline periods
3. Multi-scale decomposition (seasonal, interannual, decadal trends)
4. Quality control and gap-filling using established climate science methods
5. Normalization while preserving physical units for constraint enforcement

### 3.3 Physics-Informed Neural Differential Equations (PI-NDEs)

#### 3.3.1 Model Architecture

The core predictive model is a Neural Ordinary Differential Equation (Neural ODE) augmented with physical constraints. The climate state at time $t$ is represented as $\mathbf{x}(t) \in \mathbb{R}^d$ where $d$ is the number of climate variables. The temporal evolution is modeled as:

$$\frac{d\mathbf{x}(t)}{dt} = f_\theta(\mathbf{x}(t), t, \mathbf{c})$$

where $f_\theta$ is a neural network parameterized by $\theta$, and $\mathbf{c}$ represents external forcing conditions (greenhouse gas concentrations, solar forcing, etc.).

The neural network $f_\theta$ is designed as a multi-layer architecture:

$$f_\theta(\mathbf{x}, t, \mathbf{c}) = \text{PhysicalLayer}(\text{AttentionBlock}(\text{EncoderLayers}(\mathbf{x}, t, \mathbf{c})))$$

**Encoder Layers**: Multi-layer perceptrons with residual connections process concatenated inputs:
$$\mathbf{h}_0 = [\mathbf{x}; \phi(t); \mathbf{c}]$$
$$\mathbf{h}_{i+1} = \mathbf{h}_i + \sigma(W_i \mathbf{h}_i + \mathbf{b}_i)$$

where $\phi(t)$ is a temporal encoding (sinusoidal positional encoding).

**Attention Block**: Self-attention mechanism to capture variable interactions:
$$\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^T}{\sqrt{d_k}}\right)\mathbf{V}$$

This attention mechanism is crucial for later causal extraction, as attention weights provide interpretable interaction patterns.

**Physical Constraint Layer**: Ensures outputs respect conservation laws and physical bounds:
$$\mathbf{x}_{\text{out}} = \Pi_{\mathcal{C}}(\mathbf{x}_{\text{pred}})$$

where $\Pi_{\mathcal{C}}$ is a projection operator onto the constraint set $\mathcal{C}$.

#### 3.3.2 Physics-Informed Loss Function

The training objective combines prediction accuracy with physical constraint satisfaction:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{pred}} + \lambda_1 \mathcal{L}_{\text{physics}} + \lambda_2 \mathcal{L}_{\text{conservation}} + \lambda_3 \mathcal{L}_{\text{stability}}$$

**Prediction Loss**: Mean squared error on trajectory predictions:
$$\mathcal{L}_{\text{pred}} = \frac{1}{NT}\sum_{i=1}^{N}\sum_{t=1}^{T} \|\mathbf{x}_i(t) - \hat{\mathbf{x}}_i(t)\|^2$$

**Physics Loss**: Enforces known physical relationships (e.g., Stefan-Boltzmann law, geostrophic balance):
$$\mathcal{L}_{\text{physics}} = \sum_{j} w_j \|\mathcal{P}_j(\mathbf{x}, f_\theta)\|^2$$

where $\mathcal{P}_j$ represents physical constraint $j$.

**Conservation Loss**: Enforces energy and mass conservation:
$$\mathcal{L}_{\text{conservation}} = \left\|\frac{d}{dt}\left(\int_\Omega \rho \mathbf{x} \, d\Omega\right) - \text{Sources} + \text{Sinks}\right\|^2$$

**Stability Loss**: Penalizes unphysical instabilities:
$$\mathcal{L}_{\text{stability}} = \text{max}(0, \|\nabla_{\mathbf{x}} f_\theta\| - \gamma)$$

where $\gamma$ is a stability threshold derived from physical principles.

### 3.4 Temporal Causal Graph Extraction

#### 3.4.1 Attention-Based Causal Discovery

After training the PI-NDE, we extract causal relationships through a structured causal discovery procedure:

**Step 1: Attention Weight Aggregation**: Collect attention weights across temporal sequences:
$$A_{ij}(t) = \text{Attention weight from variable } i \text{ to } j \text{ at time } t$$

**Step 2: Temporal Lagged Cross-Correlation**: Compute time-lagged correlations accounting for physical propagation delays:
$$C_{ij}(\tau) = \frac{1}{T}\sum_{t=1}^{T-\tau} \frac{\partial \mathbf{x}_j(t+\tau)}{\partial \mathbf{x}_i(t)}$$

**Step 3: Granger Causality Testing**: For each variable pair, test if past values of $\mathbf{x}_i$ improve prediction of $\mathbf{x}_j$:
$$\mathbf{x}_j(t) = \sum_{k=1}^{K} \alpha_k \mathbf{x}_j(t-k) + \sum_{k=1}^{K} \beta_k \mathbf{x}_i(t-k) + \epsilon$$

Test $H_0: \beta_1 = \beta_2 = ... = \beta_K = 0$ using F-tests with physical constraint-aware null distributions.

**Step 4: Causal Graph Construction**: Build directed graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ where:
- Vertices $\mathcal{V}$ represent climate variables
- Directed edges $\mathcal{E}$ exist where: (1) Granger causality is significant, (2) attention weights exceed threshold, (3) temporal precedence is respected, (4) physical plausibility criteria are met

#### 3.4.2 Multi-Step Pathway Identification

To identify causal chains leading to tipping points:

**Algorithm: Pathway Discovery**
```
Input: Causal graph G, initial state x₀, tipping point indicator T
Output: Set of causal pathways P

1. Identify critical transition events: E = {t : |T(t) - T_threshold| < ε}
2. For each event e in E:
   a. Backtrack through G to find source variables active before e
   b. Apply breadth-first search with temporal constraints
   c. Score paths by: strength = ∏(edge_weights) × temporal_consistency
3. Filter paths by minimum strength threshold
4. Cluster similar paths to identify common mechanisms
5. Rank pathways by: frequency × strength × physical plausibility
Return top-k pathways
```

**Pathway Representation**: Each pathway is represented as:
$$P = \{(v_1, t_1) \xrightarrow{\tau_1, w_1} (v_2, t_2) \xrightarrow{\tau_2, w_2} ... \xrightarrow{\tau_n, w_n} (v_{n+1}, t_{n+1})\}$$

where $v_i$ are variables, $t_i$ are times, $\tau_i$ are temporal delays, and $w_i$ are causal strengths.

### 3.5 Validation Framework

#### 3.5.1 Physical Consistency Validation

**Conservation Principle Checks**: Verify discovered pathways don't violate:
- Energy conservation: $\Delta E_{\text{total}} = Q - W$
- Mass conservation: $\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \mathbf{v}) = 0$
- Momentum balance

**Thermodynamic Feasibility**: Ensure entropy changes respect second law:
$$\Delta S_{\text{pathway}} \geq 0 \text{ for isolated subsystems}$$

#### 3.5.2 Empirical Validation

**Reanalysis Data Comparison**: Test discovered pathways on held-out ERA5 data:
1. Identify pathway activation in observational record
2. Verify temporal sequences match predictions
3. Quantify pathway strength in observations vs. models

**Intervention Analysis**: If pathway suggests $A \rightarrow B \rightarrow C$, test if intervening on $B$ (in simulations) blocks $A \rightarrow C$.

**Synthetic Experiments**: Use climate model emulators to:
1. Artificially strengthen/weaken specific pathways
2. Verify predicted outcomes match framework predictions

#### 3.5.3 Expert Knowledge Validation

**Structured Expert Elicitation**:
1. Present discovered pathways to climate scientists as annotated causal diagrams
2. Collect ratings on: (a) plausibility, (b) novelty, (c) actionability
3. Identify mechanisms that: match known physics, contradict understanding, or represent novel hypotheses

**Literature Comparison**: Systematically compare discovered pathways against published mechanisms in climate literature, quantifying overlap and divergence.

### 3.6 Experimental Design

#### 3.6.1 Case Study 1: AMOC Collapse

**Objective**: Discover causal pathways leading to AMOC weakening/collapse

**Data**: CMIP6 models showing AMOC decline, observational proxies (SSH, temperature, salinity)

**Variables**: AMOC strength, North Atlantic SST, sea ice extent, freshwater fluxes, atmospheric circulation patterns

**Expected Pathways**: Arctic ice melt → freshwater influx → density reduction → AMOC weakening

#### 3.6.2 Case Study 2: Arctic-Permafrost Feedback

**Objective**: Identify feedback loops between Arctic warming and permafrost thaw

**Data**: ESM outputs with active carbon cycle, satellite observations of permafrost extent

**Variables**: Surface temperature, permafrost extent, albedo, methane emissions, snow cover

**Expected Pathways**: Temperature increase → permafrost thaw → methane release → additional warming

#### 3.6.3 Case Study 3: Amazon Rainforest Dieback

**Objective**: Uncover mechanisms linking precipitation changes to forest dieback

**Data**: Regional climate models, vegetation models, precipitation datasets

**Variables**: Precipitation, soil moisture, vegetation indices, evapotranspiration, fire frequency

**Expected Pathways**: Precipitation reduction → drought stress → tree mortality → reduced transpiration → further drying

### 3.7 Evaluation Metrics

**Predictive Performance**:
- Tipping point prediction accuracy: ROC-AUC, precision-recall
- Temporal trajectory RMSE for climate variables
- Lead time for early warning signals

**Causal Discovery Quality**:
- Precision/recall against known mechanisms (where available)
- Graph edit distance from expert-constructed causal diagrams
- Intervention accuracy in controlled simulations

**Physical Fidelity**:
- Conservation law violation rates
- Physical constraint satisfaction percentage
- Thermodynamic consistency scores

**Interpretability & Utility**:
- Expert plausibility ratings (Likert scale 1-5)
- Number of novel, testable hypotheses generated
- Actionability scores for intervention points

**Computational Efficiency**:
- Training time vs. baseline climate models
- Inference time for causal pathway extraction
- Scalability to higher-resolution datasets

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Scientific Discoveries**:
1. **Comprehensive Causal Maps**: For each case study, we expect to produce detailed causal pathway diagrams showing multi-step mechanisms leading to tipping points, including pathway strengths, temporal delays, and uncertainty quantification.

2. **Novel Feedback Mechanisms**: We anticipate discovering 3-5 previously unrecognized or underappreciated feedback loops in each climate system studied. For example, potential cross-scale interactions between atmospheric blocking patterns and ocean heat transport in AMOC dynamics.

3. **Early Warning Indicators**: Identification of leading indicators positioned earlier in causal chains, potentially extending warning times by 1-5 years compared to current methods.

4. **Intervention Points**: Specific variables in causal pathways where interventions (geoengineering, emissions reductions) would have maximum leverage in preventing or delaying tipping points.

**Methodological Contributions**:
1. **Open-Source Framework**: Fully documented CANs implementation in Python/PyTorch, enabling application to other climate phenomena and scientific domains.

2. **Benchmark Datasets**: Curated datasets pairing climate simulations with expert-annotated causal mechanisms for evaluating future XAI methods in climate science.

3. **Validation Protocols**: Standardized procedures for validating discovered causal relationships against physical principles and domain knowledge.

**Publications & Dissemination**:
- 2-3 primary research papers in venues like Nature Climate Change, Nature Machine Intelligence, or ICML/NeurIPS
- Workshop presentations at XAI4Science and climate science conferences
- Policy briefs translating findings for IPCC and national climate assessment processes

### 4.2 Impact

**Advancing Climate Science**:
The framework will transform how climate scientists use machine learning, moving from "black box" predictions to mechanistic insights that enhance process understanding. By validating discovered pathways against observations and generating testable hypotheses, CANs will accelerate the feedback loop between data-driven discovery and theory development.

**Improving Climate Model Development**:
Discovered mechanisms can inform parameterization improvements in Earth System Models. For instance, if CANs identify a critical but under-resolved feedback loop, model developers can prioritize refining that process representation.

**Informing Climate Policy**:
Mechanistically grounded explanations will help policymakers understand *why* certain climate interventions work, building confidence in climate action recommendations. Identified intervention points can guide strategic investment in mitigation and adaptation measures.

**Broader XAI Contributions**:
CANs represent a paradigm for post-hoc explainability in scientific applications: extracting structured causal knowledge while respecting domain constraints. This approach is transferable to other complex systems (epidemiology, ecology, materials science) where understanding mechanisms is as important as prediction accuracy.

**Responsible AI in Science**:
By explicitly incorporating physical constraints, validating against domain knowledge, and engaging experts throughout, this research exemplifies responsible AI deployment. Rather than replacing climate scientists, CANs augment their capabilities, generating hypotheses for human evaluation and enabling discovery at scales infeasible for manual analysis.

**Educational Impact**:
The research will produce educational materials demonstrating how modern ML can be applied to critical societal challenges while maintaining scientific rigor and interpretability, inspiring next-generation researchers at the intersection of AI and climate science.

### 4.3 Risks and Limitations

**Potential Limitations**:
1. **Data Quality Dependence**: Causal discovery quality depends on input data; systematic biases in climate models could propagate to discovered pathways.
2. **Computational Demands**: Training physics-informed neural ODEs on high-dimensional climate data is computationally intensive.
3. **Validation Challenges**: For truly novel mechanisms, ground truth validation may not be possible until targeted observational campaigns or process studies are conducted.

**Mitigation Strategies**:
1. Use multi-model ensembles and hybrid model-observation datasets to reduce model bias impact
2. Employ efficient Neural ODE solvers and multi-resolution approaches inspired by Yang et al. (2023)
3. Design controlled numerical experiments and synthetic data tests where ground truth is known
4. Engage climate scientists iteratively to refine physical constraints and validation criteria

### 4.4 Future Directions

This research opens multiple avenues for extension:
- **Real-time Early Warning Systems**: Deploying CANs operationally for monitoring tipping point approach in near-real-time
- **Cross-Tipping Point Interactions**: Extending framework to discover causal links *between* different tipping elements
- **Counterfactual Intervention Design**: Using discovered pathways to design optimal intervention strategies via reinforcement learning
- **Multi-Scale Causality**: Incorporating causal relationships across spatial and temporal scales
- **Uncertainty Quantification**: Developing Bayesian variants of CANs to quantify epistemic and aleatoric uncertainty in discovered pathways

---

**Word Count**: Approximately 2,800 words

This proposal establishes a comprehensive research plan for developing Causal Attribution Networks, addressing a critical need in climate science for interpretable, mechanistically grounded explanations of complex tipping point phenomena while contributing novel methodologies to the broader XAI community.