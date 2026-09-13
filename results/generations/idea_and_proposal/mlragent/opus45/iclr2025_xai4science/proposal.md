# Research Proposal: Concept Bottleneck Networks with Automated Scientific Concept Discovery for Climate Model Interpretation

## 1. Introduction

### Background

Climate science faces an unprecedented challenge: while machine learning models demonstrate remarkable predictive capabilities for extreme weather events, their opacity undermines scientific trust and limits their utility for advancing domain knowledge. Deep neural networks trained on climate data can forecast heat waves, hurricanes, and precipitation patterns with impressive accuracy, yet their decision-making processes remain largely inscrutable. This "black box" problem is particularly acute in climate science, where understanding *why* a prediction is made is often as valuable as the prediction itself.

Current approaches to explaining climate ML models predominantly rely on post-hoc attribution techniques such as saliency maps, integrated gradients, and SHAP values. However, recent research has demonstrated that these methods can produce inconsistent, unreliable explanations that fail to capture the true reasoning of the underlying model (Yang et al., 2024). More critically, these pixel-level attributions rarely map onto the physically meaningful concepts that climate scientists use to understand atmospheric dynamics—concepts like the El Niño-Southern Oscillation (ENSO), the North Atlantic Oscillation (NAO), or blocking patterns.

Concept Bottleneck Models (CBMs) offer a promising alternative by structuring predictions around human-interpretable concepts. Rather than providing post-hoc explanations, CBMs force the model to first predict intermediate concepts before making final predictions, creating an inherently interpretable architecture. However, traditional CBMs require extensive manual annotation of training data with concept labels—an approach that becomes impractical for complex climate systems where (1) the relevant concepts may number in the hundreds, (2) expert annotation is prohibitively expensive, and (3) some relevant physical concepts may be unknown or poorly characterized.

### Research Objectives

This research proposes **Auto-CBM-Climate**, a novel framework that bridges the gap between the interpretability benefits of concept bottleneck models and the practical constraints of climate science applications. Our specific objectives are:

1. To develop an automated pipeline for discovering physically meaningful concepts from neural network representations trained on climate data, eliminating the need for manual concept annotation.

2. To create a validation framework that verifies discovered concepts against established climate indices and physical principles, ensuring scientific coherence.

3. To demonstrate the framework's utility for both accurate prediction and knowledge discovery using extreme heat wave forecasting as a case study.

4. To investigate whether the automated concept discovery process can identify novel teleconnections or precursor patterns not previously documented in climate literature.

### Significance

This research addresses multiple key challenges identified in the literature. By automating concept discovery, we overcome the manual annotation bottleneck that limits CBM applicability. By grounding discovered concepts in physical climate indices, we ensure alignment with established scientific knowledge. By using sparse dictionary learning and large language model validation, we create a scalable approach suitable for complex climate datasets. The resulting framework will enable climate scientists to not only trust ML predictions but also potentially discover new physical relationships, advancing both XAI methodology and climate science.

## 2. Methodology

### 2.1 Overall Framework Architecture

Auto-CBM-Climate consists of four integrated stages: (1) base model training, (2) concept extraction via sparse dictionary learning, (3) LLM-assisted concept labeling and filtering, and (4) concept bottleneck construction and validation. The complete pipeline transforms an opaque neural network into an interpretable concept-based model while potentially discovering novel climate phenomena.

### 2.2 Data Collection and Preprocessing

We will utilize the ERA5 reanalysis dataset from the European Centre for Medium-Range Weather Forecasts (ECMWF), covering 1979-2023. Our primary variables include:

- **Atmospheric fields**: Geopotential height (Z500, Z850), temperature (T2m, T850), specific humidity (Q850), wind components (U/V at 200hPa and 850hPa), mean sea level pressure (MSLP)
- **Surface variables**: Sea surface temperature (SST), soil moisture, surface heat fluxes
- **Temporal resolution**: Daily means
- **Spatial resolution**: 1° × 1° global grid

For the heat wave prediction task, we define heat wave events using the World Meteorological Organization definition: periods where daily maximum temperature exceeds the 90th percentile of the climatological distribution for at least three consecutive days. We will focus on three regions with well-documented heat wave mechanisms: Western Europe, Central North America, and Eastern Asia.

### 2.3 Stage 1: Base Model Training

We train a deep convolutional neural network $f_\theta$ to predict heat wave occurrence probability 7-14 days in advance:

$$f_\theta: \mathcal{X} \rightarrow [0,1]$$

where $\mathcal{X} \in \mathbb{R}^{C \times T \times H \times W}$ represents the multi-channel, multi-temporal input with $C$ variables, $T$ time steps, and spatial dimensions $H \times W$.

The architecture employs a modified ResNet-50 backbone with 3D convolutions to capture spatiotemporal patterns:

$$\mathbf{h}^{(l)} = \sigma(\text{Conv3D}(\mathbf{h}^{(l-1)}) + \mathbf{h}^{(l-1)})$$

where $\mathbf{h}^{(l)}$ represents the hidden representation at layer $l$. The model is trained using binary cross-entropy loss with class weighting to address the imbalance between heat wave and non-heat wave days:

$$\mathcal{L}_{\text{pred}} = -\frac{1}{N}\sum_{i=1}^{N} \left[w_+ y_i \log(\hat{y}_i) + w_- (1-y_i)\log(1-\hat{y}_i)\right]$$

### 2.4 Stage 2: Sparse Dictionary Learning for Concept Extraction

Following training, we extract candidate concepts from intermediate representations using sparse dictionary learning. Let $\mathbf{H} \in \mathbb{R}^{N \times D}$ represent the flattened activations from a chosen intermediate layer across $N$ samples with $D$ dimensions. We learn a dictionary $\mathbf{D} \in \mathbb{R}^{K \times D}$ and sparse codes $\mathbf{A} \in \mathbb{R}^{N \times K}$ by solving:

$$\min_{\mathbf{D}, \mathbf{A}} \|\mathbf{H} - \mathbf{A}\mathbf{D}\|_F^2 + \lambda \|\mathbf{A}\|_1$$

subject to $\|\mathbf{d}_k\|_2 = 1$ for all dictionary atoms $k \in \{1, ..., K\}$.

The $\ell_1$ penalty encourages sparsity, ensuring each sample is represented by a small number of active concepts. We set $K = 200$ candidate concepts initially, with the expectation that filtering will reduce this to 50-100 validated concepts. The optimization is performed using the SPAMS library with alternating minimization.

For each dictionary atom $\mathbf{d}_k$, we generate interpretable visualizations by:
1. Identifying the top-100 samples with highest activation $a_{ik}$
2. Computing composite anomaly maps showing the average climate state when concept $k$ is active
3. Generating temporal activation patterns showing seasonal and interannual variability

### 2.5 Stage 3: LLM-Assisted Concept Labeling and Filtering

We employ large language models with climate science knowledge to label discovered concepts and filter physically implausible candidates. For each concept $k$, we construct a structured prompt containing:

- The composite anomaly map as a spatial pattern description
- Temporal activation statistics (seasonality, trends)
- Correlation with the prediction target
- Top-5 correlated ERA5 variables

The LLM (GPT-4 or Claude with climate science fine-tuning) is prompted to:

1. **Label the concept**: Provide a descriptive name based on known climate patterns
2. **Assess physical plausibility**: Rate confidence (1-5) that the pattern represents a real physical mechanism
3. **Suggest validation indices**: Recommend established climate indices for verification
4. **Identify novelty**: Flag patterns that may represent undocumented phenomena

We implement a filtering criterion combining LLM confidence scores with quantitative metrics:

$$\text{Retain}(k) = \mathbb{1}\left[\text{LLM\_conf}(k) \geq 3 \land \text{Var\_explained}(k) \geq \tau_v \land \text{Corr\_target}(k) \geq \tau_c\right]$$

where $\tau_v = 0.01$ (minimum variance explained) and $\tau_c = 0.1$ (minimum correlation with heat wave occurrence).

### 2.6 Stage 4: Concept Bottleneck Construction and Validation

Using the filtered concepts, we construct a concept bottleneck model with architecture:

$$\hat{\mathbf{c}} = g_\phi(\mathbf{x}), \quad \hat{y} = h_\psi(\hat{\mathbf{c}})$$

where $g_\phi: \mathcal{X} \rightarrow \mathbb{R}^{K'}$ is the concept predictor (using the base model encoder with a new projection head), $\hat{\mathbf{c}}$ is the predicted concept activation vector, and $h_\psi: \mathbb{R}^{K'} \rightarrow [0,1]$ is a lightweight interpretable classifier (logistic regression or small MLP).

The training objective combines prediction accuracy with concept alignment:

$$\mathcal{L}_{\text{CBM}} = \mathcal{L}_{\text{pred}}(\hat{y}, y) + \alpha \sum_{k \in \mathcal{V}} \mathcal{L}_{\text{align}}(\hat{c}_k, I_k)$$

where $\mathcal{V}$ is the set of concepts with established climate index correspondences $I_k$, and $\mathcal{L}_{\text{align}}$ is the mean squared error between predicted concept activations and normalized climate indices.

**Validation against climate indices**: We compute Pearson correlations between discovered concepts and established indices including ENSO (Niño 3.4 SST), NAO, Pacific Decadal Oscillation (PDO), Arctic Oscillation (AO), and regional blocking indices. Concepts achieving $|r| > 0.5$ with any established index are considered validated.

### 2.7 Experimental Design and Evaluation Metrics

**Prediction Performance**:
- Area Under ROC Curve (AUC-ROC)
- Critical Success Index (CSI) for heat wave detection
- Brier Skill Score relative to climatological baseline

**Interpretability Quality**:
- Concept alignment: Average correlation of discovered concepts with established climate indices
- Concept completeness: Fraction of variance in base model predictions explained by concept bottleneck
- Human evaluation: Climate scientists rate interpretability and physical meaningfulness (1-5 scale) for 20 random concepts

**Knowledge Discovery**:
- Number of concepts flagged as potentially novel by LLM
- Expert validation of novel concepts through consultation with climate scientists
- Literature search to verify whether "novel" patterns exist in prior publications

**Baselines**:
- Standard CNN without concept bottleneck
- Post-hoc explanation methods: Integrated Gradients, SHAP, Layer-wise Relevance Propagation
- Traditional CBM with manually defined concepts (subset of 20 known climate patterns)

**Ablation Studies**:
- Impact of dictionary size $K$ on concept quality
- Comparison of different sparse coding algorithms
- Effect of LLM filtering threshold on concept set quality

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Validated Concept Set**: We anticipate discovering 50-80 physically meaningful concepts, with approximately 60% corresponding to established climate patterns (validating the methodology) and 40% representing less-documented or novel phenomena worthy of further investigation.

2. **Predictive Performance**: The Auto-CBM-Climate model is expected to achieve AUC-ROC within 5% of the black-box baseline while providing full concept-level interpretability—demonstrating that interpretability need not sacrifice accuracy.

3. **Novel Scientific Insights**: Based on preliminary analysis, we expect to identify 3-5 candidate novel teleconnections or precursor patterns, particularly related to soil moisture-atmosphere feedbacks and stratosphere-troposphere coupling in heat wave development.

4. **Open-Source Framework**: We will release the complete Auto-CBM-Climate codebase, including the sparse dictionary learning pipeline, LLM prompting templates, and concept validation tools.

### Scientific Impact

This research will establish a new paradigm for interpretable climate ML that moves beyond pixel-level attributions toward semantically meaningful, physically grounded explanations. By automating concept discovery, we lower the barrier for applying CBMs to complex scientific domains where manual annotation is infeasible. The validation framework ensures that interpretability gains translate to genuine scientific understanding rather than plausible-sounding but incorrect explanations.

### Broader Impact

The methodology extends beyond climate science to any scientific domain where neural networks are applied to complex, high-dimensional data. Potential applications include materials science (discovering structure-property relationships), healthcare (identifying disease biomarkers), and oceanography (understanding ocean circulation patterns). By bridging the gap between ML capabilities and scientific interpretability, Auto-CBM-Climate contributes to the responsible deployment of AI in high-stakes scientific applications.

Furthermore, by potentially discovering novel climate phenomena, this work demonstrates that interpretable ML can serve not merely as a trust-building tool but as an instrument for scientific discovery—advancing human knowledge rather than simply automating existing understanding.