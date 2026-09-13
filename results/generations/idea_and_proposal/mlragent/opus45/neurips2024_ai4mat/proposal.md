# Research Proposal: MatImpute: Multi-Fidelity Graph Neural Networks for Intelligent Imputation of Incomplete Materials Databases

## 1. Introduction

### Background

Artificial intelligence has revolutionized numerous scientific domains, with drug discovery and computational biology experiencing exponential growth through foundation models trained on comprehensive molecular databases. However, AI-driven materials science has not witnessed a comparable transformation, despite its potential to accelerate the discovery of novel materials for energy storage, catalysis, electronics, and sustainable technologies. A fundamental barrier to this "GPT moment" for materials AI lies in the pervasive incompleteness of materials databases.

Unlike molecular datasets where properties can be systematically computed through standardized protocols, materials databases such as the Materials Project, AFLOW, and ICSD suffer from severe data sparsity. Typical database entries contain measurements for only 10-30% of relevant properties, with characterization data scattered across diverse modalities including X-ray diffraction (XRD), transmission electron microscopy (TEM), various spectroscopic techniques, and mechanical testing. Furthermore, the data quality varies dramatically between high-fidelity experimental measurements and low-fidelity density functional theory (DFT) predictions, creating a heterogeneous landscape that conventional machine learning approaches struggle to navigate.

Current strategies for handling incomplete materials data are inadequate. Discarding samples with missing values drastically reduces effective dataset sizes, while naive imputation methods (mean substitution, k-nearest neighbors) ignore the complex physical correlations between material properties and fail to account for varying data fidelities. This data completeness crisis directly impedes the development of large-scale foundation models that could transform materials discovery.

### Research Objectives

This research proposes **MatImpute**, a novel multi-fidelity graph neural network architecture designed specifically for intelligent imputation of incomplete materials databases. Our primary objectives are:

1. To develop a physics-informed graph neural network that learns property correlations across diverse material characteristics while explicitly modeling data fidelity hierarchies.
2. To create calibrated uncertainty quantification mechanisms that distinguish between imputed and measured values, enabling reliable downstream applications.
3. To demonstrate that intelligent imputation can expand effective training set sizes by 3-5× for downstream materials prediction tasks.
4. To establish an experimental prioritization framework that identifies high-value missing measurements to guide resource allocation in materials characterization.

### Significance

This research addresses the critical "Why Isn't it Real Yet?" question posed by the AI4Mat community. By tackling the fundamental data completeness challenge, MatImpute could serve as essential infrastructure enabling the training of foundation models for materials science. The approach directly confronts the unique challenge of managing multimodal, incomplete materials data—a distinguishing characteristic that separates materials science from more data-rich domains. Success in this endeavor could catalyze transformative advances in AI-accelerated materials discovery, bringing the field closer to the exponential growth observed in adjacent scientific domains.

## 2. Methodology

### 2.1 Problem Formulation

Let a materials database be represented as $\mathcal{D} = \{(M_i, \mathbf{p}_i, \mathbf{f}_i, \mathbf{m}_i)\}_{i=1}^{N}$, where $M_i$ denotes the material structure (composition and atomic arrangement), $\mathbf{p}_i \in \mathbb{R}^{K}$ represents the property vector across $K$ properties, $\mathbf{f}_i \in \{0, 1, 2\}^{K}$ indicates the fidelity level (0: missing, 1: computational, 2: experimental) for each property, and $\mathbf{m}_i \in \{0, 1\}^{K}$ is the observation mask where $m_{ik} = 1$ indicates property $k$ is observed.

Our goal is to learn a function $f_\theta: (M_i, \mathbf{p}_i \odot \mathbf{m}_i, \mathbf{f}_i, \mathbf{m}_i) \rightarrow (\hat{\mathbf{p}}_i, \boldsymbol{\sigma}_i)$ that predicts complete property vectors $\hat{\mathbf{p}}_i$ with associated uncertainty estimates $\boldsymbol{\sigma}_i$.

### 2.2 Architecture Design

#### 2.2.1 Property-Material Heterogeneous Graph Construction

MatImpute employs a heterogeneous graph representation with two node types: material nodes and property nodes. For each material $M_i$, we construct a local graph $\mathcal{G}_i = (\mathcal{V}_i, \mathcal{E}_i)$ where:

- **Material node** $v_M$: Encoded using a pre-trained crystal graph neural network (CGCNN or M3GNet) to capture structural information, yielding embedding $\mathbf{h}_M \in \mathbb{R}^{d}$.
- **Property nodes** $\{v_{p_k}\}_{k=1}^{K}$: Each property $k$ is represented as a node with initial features:

$$\mathbf{h}_{p_k}^{(0)} = \text{MLP}_{\text{init}}\left([p_{ik} \cdot m_{ik}; m_{ik}; \text{onehot}(f_{ik}); \mathbf{e}_k]\right)$$

where $\mathbf{e}_k$ is a learnable property-type embedding.

Edges connect: (1) material node to all property nodes, (2) property nodes to each other based on a physics-informed adjacency matrix $\mathbf{A}^{\text{phys}}$ encoding known correlations (e.g., band gap ↔ electrical conductivity, bulk modulus ↔ hardness).

#### 2.2.2 Multi-Fidelity Hierarchical Attention Mechanism

The core of MatImpute is a multi-fidelity message passing scheme that weighs contributions based on both structural relevance and data fidelity. For layer $l$, the update for property node $k$ is:

$$\mathbf{h}_{p_k}^{(l+1)} = \mathbf{h}_{p_k}^{(l)} + \sum_{j \in \mathcal{N}(k)} \alpha_{kj}^{(l)} \cdot \gamma_{kj}^{(l)} \cdot \text{MLP}^{(l)}\left(\mathbf{h}_{p_j}^{(l)}\right)$$

where $\alpha_{kj}^{(l)}$ is the structural attention weight:

$$\alpha_{kj}^{(l)} = \frac{\exp\left(\text{LeakyReLU}\left(\mathbf{a}^T[\mathbf{W}\mathbf{h}_{p_k}^{(l)} \| \mathbf{W}\mathbf{h}_{p_j}^{(l)}]\right)\right)}{\sum_{j' \in \mathcal{N}(k)} \exp\left(\text{LeakyReLU}\left(\mathbf{a}^T[\mathbf{W}\mathbf{h}_{p_k}^{(l)} \| \mathbf{W}\mathbf{h}_{p_{j'}}^{(l)}]\right)\right)}$$

and $\gamma_{kj}^{(l)}$ is the fidelity-aware gating factor:

$$\gamma_{kj}^{(l)} = \sigma\left(\text{MLP}_{\text{fid}}^{(l)}\left([\text{onehot}(f_{ij}); m_{ij}; \mathbf{h}_{p_j}^{(l)}]\right)\right)$$

This mechanism ensures that high-fidelity experimental values contribute more strongly than computational predictions, while missing values propagate information through learned correlations.

#### 2.2.3 Cross-Material Context Aggregation

To leverage patterns across the database, we introduce a cross-material attention layer that allows property nodes to attend to similar materials:

$$\mathbf{c}_{p_k}^{(i)} = \sum_{j=1}^{N} \beta_{ij} \cdot \mathbf{h}_{p_k}^{(j,L)}$$

where $\beta_{ij} = \text{softmax}_j\left(\frac{\mathbf{h}_M^{(i)} \cdot \mathbf{h}_M^{(j)}}{\sqrt{d}}\right)$ measures material similarity.

#### 2.2.4 Uncertainty-Aware Output Layer

The final prediction employs a heteroscedastic Gaussian output:

$$\hat{p}_{ik} = \text{MLP}_{\mu}\left([\mathbf{h}_{p_k}^{(L)}; \mathbf{c}_{p_k}^{(i)}; \mathbf{h}_M^{(i)}]\right)$$

$$\log \sigma_{ik}^2 = \text{MLP}_{\sigma}\left([\mathbf{h}_{p_k}^{(L)}; \mathbf{c}_{p_k}^{(i)}; \mathbf{h}_M^{(i)}; m_{ik}]\right)$$

The uncertainty estimate explicitly conditions on the observation mask, allowing the model to output higher uncertainty for imputed values.

### 2.3 Training Procedure

#### 2.3.1 Masked Property Prediction Objective

Training follows a masked prediction paradigm. For each training sample, we randomly mask an additional $\rho \in [0.3, 0.7]$ of observed properties. The loss function combines negative log-likelihood with fidelity-weighted terms:

$$\mathcal{L} = \sum_{i=1}^{N} \sum_{k: m_{ik}^{\text{orig}}=1} w_{f_{ik}} \cdot \left[\frac{(p_{ik} - \hat{p}_{ik})^2}{2\sigma_{ik}^2} + \log \sigma_{ik}\right] + \lambda \mathcal{L}_{\text{reg}}$$

where $w_{f_{ik}} \in \{w_{\text{comp}}, w_{\text{exp}}\}$ weights experimental data more heavily, and $\mathcal{L}_{\text{reg}}$ includes physics-informed regularization enforcing known property constraints.

#### 2.3.2 Curriculum Learning Strategy

Training proceeds in stages: (1) low masking ratios with high-fidelity data only, (2) increased masking with mixed fidelities, (3) full training with aggressive masking and all data sources.

### 2.4 Data Collection and Preprocessing

We aggregate data from multiple sources:
- **Materials Project**: ~150,000 compounds with DFT-computed properties
- **AFLOW**: ~3.5 million entries with formation energies, band gaps
- **ICSD**: Experimental crystal structures
- **Citrination/Matminer**: Experimental measurements for mechanical, thermal properties

Properties are standardized using robust scaling, and fidelity labels are assigned based on data provenance. The physics-informed adjacency matrix $\mathbf{A}^{\text{phys}}$ is constructed from domain knowledge and correlation analysis of complete data subsets.

### 2.5 Experimental Validation

#### 2.5.1 Imputation Quality Evaluation

We evaluate on held-out test sets using:
- **Mean Absolute Error (MAE)** and **Root Mean Square Error (RMSE)** for point predictions
- **Negative Log-Likelihood (NLL)** and **Calibration Error** for uncertainty quantification
- **Coverage Probability** at various confidence levels

Baselines include: mean imputation, k-NN imputation, matrix factorization (SVD), standard GNN without fidelity awareness, and the neural network approach from Verpoort et al. (2018).

#### 2.5.2 Downstream Task Enhancement

We measure the impact on downstream prediction tasks:
- Train property predictors (formation energy, band gap, bulk modulus) on: (a) original incomplete data, (b) MatImpute-augmented data
- Report relative improvement in test MAE and sample efficiency gains

#### 2.5.3 Experimental Prioritization Validation

Using historical data, we simulate scenarios where MatImpute's uncertainty estimates guide measurement selection. We compare against random selection and active learning baselines, measuring information gain per measurement.

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Pre-trained Imputation Model**: A publicly released MatImpute model capable of imputing missing properties across major materials databases with calibrated uncertainties. We anticipate achieving 20-35% lower MAE compared to baseline methods, with well-calibrated uncertainty estimates (calibration error < 0.05).

2. **Expanded Effective Training Sets**: Demonstration that MatImpute enables 3-5× larger effective training sets for downstream tasks, with corresponding improvements of 15-25% in prediction accuracy for formation energy, band gap, and mechanical property predictions.

3. **Experimental Prioritization Framework**: A validated methodology for identifying high-value missing measurements, potentially reducing experimental costs by prioritizing measurements with highest expected information gain. We expect 40-60% improvement in information efficiency compared to random measurement selection.

4. **Open-Source Software and Benchmark**: Release of the MatImpute codebase, pre-trained models, and a standardized benchmark for evaluating materials data imputation methods.

### Broader Impact

This research addresses a foundational infrastructure challenge that currently limits AI-driven materials discovery. By enabling the effective use of incomplete, multi-fidelity data, MatImpute could:

- **Accelerate Foundation Model Development**: Provide the data completeness necessary for training large-scale materials foundation models analogous to those transforming other scientific domains.
- **Democratize Materials AI**: Enable researchers with limited experimental resources to leverage imputed data for initial explorations, reducing barriers to entry.
- **Optimize Research Resource Allocation**: Guide experimental campaigns toward measurements with highest expected value, improving the efficiency of materials characterization efforts.
- **Bridge Computational and Experimental Communities**: Create a unified framework for integrating computational predictions with experimental measurements, fostering collaboration across the materials science community.

Ultimately, MatImpute represents critical infrastructure for realizing the full potential of AI in materials science, directly addressing why the field has not yet experienced the transformative growth seen in adjacent domains and paving the way toward accelerated materials discovery for societal challenges including clean energy, sustainable manufacturing, and advanced electronics.