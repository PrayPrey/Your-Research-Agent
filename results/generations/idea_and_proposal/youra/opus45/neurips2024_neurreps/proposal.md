# Research Proposal: Symmetry-Adaptive Spectral Correspondence for Comparing Geometric Structure in Biological and Artificial Neural Networks

## 1. Introduction

### 1.1 Background

A remarkable convergence is emerging between neuroscience and deep learning: both fields have independently discovered that neural systems mirror the geometric and topological structure of the information they encode. In biological systems, this principle manifests across multiple brain regions. Head direction circuits in the fly brain form ring attractors that preserve the circular topology of angular orientation (Kim et al., 2017; Chaudhuri et al., 2019). Grid cells in the entorhinal cortex generate activity patterns that tile space with hexagonal periodicity, forming toroidal manifolds that reflect the two-dimensional structure of spatial navigation (Gardner et al., 2022). Motor cortex exhibits low-dimensional manifold structure that captures the geometry of movement trajectories (Gallego et al., 2017).

Independently, the field of Geometric Deep Learning has formalized how incorporating geometric priors—particularly symmetry and equivariance—into artificial neural networks yields substantial improvements in computational efficiency, robustness, and generalization (Bronstein et al., 2021). Equivariant neural networks explicitly preserve group structure through their layers, ensuring that transformations of inputs produce corresponding transformations of outputs. This architectural principle has proven successful across domains from molecular modeling to computer vision.

The parallel emergence of geometric structure in biological and artificial neural systems suggests deep, substrate-agnostic principles for neural computation. However, despite this conceptual convergence, a critical gap exists: **no quantitative framework currently enables direct comparison of geometric representations across biological and artificial systems**. Existing comparison methods such as Centered Kernel Alignment (CKA) and Representational Similarity Analysis (RSA) measure statistical relationships between representations but ignore the underlying symmetry structure. Conversely, topological data analysis methods applied to neural recordings lack the spectral comparison tools developed for equivariant networks. This methodological gap prevents rigorous testing of whether brains and machines implement the same computational principles.

### 1.2 Research Objectives

This proposal introduces **Symmetry-Adaptive Spectral Correspondence (SASC)**, a unified framework for quantitatively comparing geometric structure in biological and artificial neural networks. Our primary objectives are:

1. **Develop a two-stage analytical pipeline** that first discovers symmetry type via topological data analysis (persistent homology signatures), then decomposes neural activity into irreducible representations using group Fourier transforms.

2. **Establish quantitative metrics** for comparing spectral energy distributions in irreducible representation space across biological and artificial systems.

3. **Validate the framework** on matched biological-artificial pairs: head direction circuits versus SO(2)-equivariant RNNs, and grid cells versus T²-equivariant networks.

4. **Demonstrate superiority** over symmetry-agnostic baselines (CKA, RSA) in distinguishing systems with matched versus mismatched symmetry structure.

### 1.3 Core Hypothesis

**Under conditions where neural systems encode continuous variables (head direction, spatial position), if symmetry-adaptive spectral correspondence (SASC) analysis is applied to neural population activity, then quantitative comparison metrics will reveal matching geometric structure between biological neural circuits and artificial equivariant networks, because both systems can be decomposed into irreducible representations of the same symmetry groups via group Fourier transform.**

We predict that biological circuits and artificial equivariant networks encoding the same symmetry (SO(2), T², SO(3)) will exhibit spectral correspondence scores exceeding 0.8 in irreducible representation space, significantly above chance level (0.5).

### 1.4 Significance

Success of this research would establish the first quantitative bridge between geometric neuroscience and geometric deep learning, with several important implications:

- **Theoretical unification**: Providing mathematical evidence that biological and artificial systems implement equivalent computational strategies for preserving geometric structure.
- **Principled architecture design**: Enabling transfer of architectural insights from neuroscience to machine learning and vice versa.
- **Interpretable neural network analysis**: Offering new tools for understanding what geometric structure artificial networks learn.
- **Neuroscience methodology**: Providing quantitative metrics for characterizing geometric representations in neural data.

## 2. Methodology

### 2.1 Overview of the SASC Framework

The SASC framework consists of two stages: **Stage 1 (Symmetry Discovery)** identifies the symmetry group from neural activity using topological data analysis, and **Stage 2 (Spectral Correspondence)** decomposes activity into irreducible representations and computes comparison metrics.

### 2.2 Stage 1: Symmetry Discovery

#### Step 1: Manifold Projection

Given neural population activity $\mathbf{X} \in \mathbb{R}^{N \times T}$ where $N$ is the number of neurons and $T$ is the number of time points, we first project to a low-dimensional embedding:

$$\mathbf{Z} = \phi(\mathbf{X}) \in \mathbb{R}^{d \times T}, \quad d \in [10, 20]$$

We employ diffusion maps for this projection, which preserves local geometric structure. The diffusion map constructs a kernel matrix $\mathbf{K}$ with entries:

$$K_{ij} = \exp\left(-\frac{\|\mathbf{x}_i - \mathbf{x}_j\|^2}{\epsilon}\right)$$

where $\epsilon$ is determined adaptively. The embedding coordinates are given by the eigenvectors of the normalized graph Laplacian.

#### Step 2: Topological Data Analysis

We apply persistent homology to the embedded point cloud $\mathbf{Z}$ to extract topological signatures. Using Vietoris-Rips filtration, we compute persistence diagrams $\text{PD}_k$ for homology dimensions $k \in \{0, 1, 2\}$.

The Betti numbers $\beta_k$ count the number of $k$-dimensional holes:
- $\beta_0$: connected components
- $\beta_1$: loops/tunnels  
- $\beta_2$: voids/cavities

We extract persistence features including:
- **Betti curves**: $\beta_k(\epsilon)$ as a function of filtration parameter
- **Persistence entropy**: $H_k = -\sum_i p_i \log p_i$ where $p_i$ is the normalized lifetime of feature $i$
- **Persistence landscapes**: functional summaries of persistence diagrams

#### Step 3: Symmetry Classification

We classify the symmetry group based on topological signatures using a template matching approach:

| Symmetry Group | Expected Signature |
|----------------|-------------------|
| SO(2) (circle) | $\beta_1 = 1$, single persistent H₁ feature |
| T² (torus) | $\beta_1 = 2$, $\beta_2 = 1$, two persistent H₁ features |
| SO(3) (sphere) | $\beta_2 = 1$, single persistent H₂ feature |

For approximate symmetries, we compute the Wasserstein distance between observed persistence diagrams and template diagrams:

$$W_p(\text{PD}_{\text{obs}}, \text{PD}_{\text{template}}) = \left(\inf_{\gamma} \sum_{(x,y) \in \gamma} \|x - y\|^p\right)^{1/p}$$

The symmetry group is assigned as:

$$G^* = \arg\min_{G \in \mathcal{G}} W_2(\text{PD}_{\text{obs}}, \text{PD}_G)$$

where $\mathcal{G} = \{\text{SO}(2), \text{T}^2, \text{SO}(3)\}$ is the template library.

### 2.3 Stage 2: Spectral Correspondence

#### Step 4: Group Fourier Transform

Given identified symmetry group $G^*$, we decompose neural activity into irreducible representations (irreps) using the group Fourier transform.

**For SO(2) (circular symmetry):**

The irreps are indexed by integer $m \in \mathbb{Z}$. For neural activity $f(\theta)$ parameterized by angle $\theta$, the Fourier coefficients are:

$$\hat{f}_m = \frac{1}{2\pi} \int_0^{2\pi} f(\theta) e^{-im\theta} d\theta$$

The spectral energy in mode $m$ is $E_m = |\hat{f}_m|^2$.

**For T² (toroidal symmetry):**

The irreps are indexed by pairs $(m_1, m_2) \in \mathbb{Z}^2$. For activity $f(\theta_1, \theta_2)$:

$$\hat{f}_{m_1, m_2} = \frac{1}{4\pi^2} \int_0^{2\pi} \int_0^{2\pi} f(\theta_1, \theta_2) e^{-i(m_1\theta_1 + m_2\theta_2)} d\theta_1 d\theta_2$$

**For SO(3) (spherical symmetry):**

The irreps are the spherical harmonics $Y_l^m$ indexed by $l \in \mathbb{N}$ and $m \in [-l, l]$:

$$\hat{f}_l^m = \int_{S^2} f(\omega) \overline{Y_l^m(\omega)} d\omega$$

#### Spectral Energy Distribution

We compute the normalized spectral energy distribution vector:

$$\mathbf{s} = \frac{1}{\sum_\rho E_\rho} [E_{\rho_1}, E_{\rho_2}, \ldots, E_{\rho_K}]$$

where $\rho_k$ indexes the first $K$ irreps (ordered by frequency/degree) and $E_\rho$ is the energy in irrep $\rho$.

### 2.4 Comparison Metrics

**Spectral Correspondence Score (SCS):**

For two systems with spectral distributions $\mathbf{s}^{(A)}$ and $\mathbf{s}^{(B)}$:

$$\text{SCS}(\mathbf{s}^{(A)}, \mathbf{s}^{(B)}) = \frac{\mathbf{s}^{(A)} \cdot \mathbf{s}^{(B)}}{\|\mathbf{s}^{(A)}\| \|\mathbf{s}^{(B)}\|}$$

This cosine similarity ranges from 0 (orthogonal) to 1 (identical).

**Symmetry Fidelity Index (SFI):**

$$\text{SFI} = \frac{\sum_{\rho \in \mathcal{R}_G} E_\rho}{\sum_{\text{all } \rho} E_\rho}$$

where $\mathcal{R}_G$ are the irreps consistent with symmetry group $G$. This measures how much energy lies in the expected symmetry modes.

**Representation Efficiency Ratio (RER):**

$$\text{RER} = \frac{K_{90}}{K_{\text{total}}}$$

where $K_{90}$ is the number of irreps needed to capture 90% of variance. Lower values indicate more efficient representations.

### 2.5 Experimental Design

#### 2.5.1 Datasets

**Biological Data:**
- **Head direction circuits**: Drosophila ellipsoid body recordings from publicly available datasets (Seelig & Jayaraman, 2015), N ≥ 100 neurons
- **Grid cells**: Rat entorhinal cortex recordings from Gardner et al. (2022) dataset, N ≥ 200 neurons

**Artificial Networks:**
- **SO(2)-equivariant RNN**: Recurrent network with circular convolutions trained on angular velocity integration
- **T²-equivariant network**: Network with toroidal convolutions trained on 2D spatial navigation
- **Non-equivariant baselines**: Standard RNNs and MLPs trained on identical tasks

#### 2.5.2 Validation Experiments

**Experiment 1: Symmetry Discovery Validation**

*Objective*: Verify that Stage 1 correctly identifies symmetry type.

*Protocol*:
1. Generate synthetic data with known symmetry (ring, torus, sphere manifolds with added noise)
2. Apply SASC Stage 1 to classify symmetry
3. Compute classification accuracy across noise levels (SNR from 1 to 20 dB)

*Success criterion*: Classification accuracy > 90% for SNR > 10 dB.

**Experiment 2: Spectral Correspondence for Matched Symmetries**

*Objective*: Test primary hypothesis that matched biological-artificial pairs show high spectral correspondence.

*Protocol*:
1. Extract spectral distributions from head direction circuits and SO(2)-equivariant RNNs
2. Compute SCS for matched pairs (biological HD ↔ SO(2) RNN)
3. Compute SCS for mismatched pairs (biological HD ↔ T² network)
4. Repeat for grid cells ↔ T²-equivariant networks

*Statistical analysis*:
- One-sample t-test: SCS vs. chance level (0.5)
- Two-sample t-test: matched vs. mismatched pairs
- Sample size: n = 20 independent recordings/training runs per condition
- Significance level: α = 0.05

*Success criterion*: Mean SCS > 0.8 for matched pairs, p < 0.05.

**Experiment 3: Comparison with Baselines**

*Objective*: Demonstrate SASC superiority over symmetry-agnostic methods.

*Protocol*:
1. Compute CKA and RSA similarity between all biological-artificial pairs
2. Compute SASC metrics for same pairs
3. Evaluate discriminability: ability to distinguish matched vs. mismatched symmetry pairs

*Metrics*:
- ROC-AUC for classifying matched vs. mismatched pairs
- Cohen's d effect size for separation between conditions

*Success criterion*: SASC achieves higher ROC-AUC than CKA and RSA (p < 0.05, paired t-test).

**Experiment 4: Training Dynamics**

*Objective*: Track how artificial networks develop geometric structure during training.

*Protocol*:
1. Train SO(2)-equivariant RNN on angular integration task
2. Compute SASC metrics at regular intervals (every 100 epochs)
3. Compare trajectory to biological attractor spectrum

*Analysis*: Correlation between training progress and spectral convergence toward biological template.

#### 2.5.3 Evaluation Metrics Summary

| Metric | Definition | Expected Value (Matched) | Threshold for Success |
|--------|------------|-------------------------|----------------------|
| SCS | Cosine similarity of spectral distributions | > 0.8 | > 0.6 |
| SFI | Energy ratio in target symmetry modes | > 0.7 | > 0.5 |
| RER | Efficiency of representation | < 0.3 | < 0.5 |
| Classification accuracy | Symmetry type identification | > 90% | > 70% |
| ROC-AUC | Discriminability vs. baselines | > 0.9 | > 0.75 |

### 2.6 Implementation Details

**Software**: Implementation in Python using:
- `Giotto-tda` for persistent homology computation
- `e3nn` for SO(3) irreducible representations
- Custom PyTorch modules for equivariant RNNs

**Computational requirements**: 
- TDA computation: O(n³) for n points; GPU acceleration via CUDA-Ripser for n > 5000
- Group FFT: O(n log n) for SO(2)/T², O(n²) for SO(3)

**Reproducibility**: All code, trained models, and analysis scripts will be released publicly.

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

Based on our theoretical framework and preliminary evidence from the literature, we anticipate the following outcomes:

1. **High spectral correspondence for matched symmetries**: We expect SCS > 0.8 between head direction circuits and SO(2)-equivariant RNNs, and between grid cells and T²-equivariant networks. This would provide the first quantitative evidence that biological and artificial systems implement equivalent geometric computations.

2. **Clear separation from mismatched pairs**: Mismatched symmetry pairs (e.g., head direction circuits vs. T² networks) should show SCS near chance level (~0.5), demonstrating that the correspondence is specific to shared symmetry structure.

3. **Superior discriminability over baselines**: SASC should achieve ROC-AUC > 0.9 for distinguishing matched vs. mismatched pairs, compared to < 0.7 for CKA and RSA, which ignore symmetry structure.

4. **Interpretable training dynamics**: Monitoring equivariant network training via SASC should reveal progressive convergence toward biological spectral signatures, providing insight into how geometric structure emerges during learning.

### 3.2 Potential Negative Results and Interpretation

If the hypothesis is not supported, several interpretations are possible:

- **SCS ≤ 0.6 for matched pairs**: Would suggest that biological emergent symmetries and artificial hardcoded symmetries produce fundamentally different representations, despite encoding the same group structure.

- **High variance in SCS (σ > 0.15)**: Would indicate that the correspondence is not robust, possibly due to individual differences in biological circuits or sensitivity to training conditions in artificial networks.

- **No advantage over baselines**: Would suggest that symmetry-specific analysis does not provide additional information beyond general representational similarity.

Each outcome would provide valuable scientific insight into the relationship between biological and artificial geometric representations.

### 3.3 Broader Impact

**For Neuroscience:**
- New quantitative tools for characterizing geometric structure in neural populations
- Framework for comparing representations across brain regions, species, and recording modalities
- Principled approach to testing theories of neural computation based on symmetry

**For Machine Learning:**
- Interpretable metrics for understanding what geometric structure networks learn
- Guidance for architecture design based on biological principles
- New benchmarks for evaluating geometric deep learning methods

**For the Field:**
- Establishing a common mathematical language between neuroscience and deep learning
- Enabling systematic investigation of substrate-agnostic computational principles
- Opening new research directions at the intersection of representation theory, topology, and neural computation

### 3.4 Limitations and Future Directions

**Current limitations:**
- Symmetry template library limited to SO(2), T², SO(3); extension to other groups (e.g., discrete symmetries, Lie groups) requires additional development
- Computational cost of TDA may limit application to very large populations or real-time analysis
- Framework assumes clean symmetry cases; mixed or broken symmetries require soft matching extensions

**Future directions:**
- Extension to hierarchical symmetries and symmetry breaking
- Application to other brain regions (visual cortex, hippocampus, motor cortex)
- Development of SASC-guided training objectives for artificial networks
- Integration with mechanistic interpretability methods for understanding how symmetry emerges

In conclusion, the SASC framework offers a principled, mathematically grounded approach to one of the most exciting questions at the intersection of neuroscience and artificial intelligence: whether biological and artificial neural systems implement the same geometric computational strategies. By providing quantitative tools for this comparison, we aim to advance both our understanding of the brain and our ability to design more effective artificial neural networks.