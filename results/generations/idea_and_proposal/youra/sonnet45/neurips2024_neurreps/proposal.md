# Research Proposal: Topological-Geometric Neural Networks for Unified Representation Learning

## 1. Title

**Topological-Geometric Neural Networks: Unifying Local Symmetries and Global Structure for Enhanced Representation Learning in Scientific Data**

## 2. Introduction

### 2.1 Background

The convergence of neuroscience and geometric deep learning has revealed fundamental principles about how neural systems—both biological and artificial—represent structured information. Recent findings in sensory and motor neuroscience demonstrate that neural circuits mirror the geometric and topological structure of the systems they represent, as evidenced in head direction circuits in flies (Kim et al., 2017; Wolff et al., 2015), grid cells (Gardner et al., 2022), and motor cortex manifolds (Gallego et al., 2017). Independently, the field of Geometric Deep Learning (Bronstein et al., 2021) has incorporated geometric priors into artificial neural networks, achieving provable gains in computational efficiency, robustness, and generalization.

Current state-of-the-art neural architectures excel at capturing either local geometric symmetries through equivariant architectures (e.g., E(n)-equivariant networks) or global topological features through persistent homology and topological data analysis. However, these approaches operate in isolation, creating a critical gap in representation learning for structured scientific data where both local and global structure are essential. For instance, in molecular property prediction, local geometric arrangements of atoms (captured by equivariant convolutions) and global topological features like ring structures (captured by persistent homology) both critically determine molecular properties. Similarly, in 3D shape classification, local surface geometry and global topological invariants like genus jointly characterize shapes.

The theoretical foundation for unifying these approaches exists in category theory, where Maruyama (2025) has proven that topological and geometric constraints are compositional via functorial composition. The persistence stability theorem guarantees that topological features remain stable under perturbations, providing a natural regularization mechanism. However, no existing architecture integrates these complementary constraints in an end-to-end learnable framework.

### 2.2 Research Objectives

This research proposes **Topological-Geometric Neural Networks (TGNNs)**, a novel architecture that integrates differentiable persistent homology layers with E(n)-equivariant convolutions to simultaneously learn local geometric symmetries and global topological structure. Our specific objectives are:

1. **Develop a unified theoretical framework** grounded in category theory that formalizes the composition of topological invariants and geometric equivariance
2. **Design and implement differentiable persistent homology layers** compatible with automatic differentiation and scalable to scientific datasets
3. **Create an integration protocol** for combining equivariant geometric processing with topological feature extraction
4. **Validate performance improvements** on topologically-structured tasks in molecular science, 3D computer vision, and neuroscience
5. **Establish sample efficiency gains** through controlled experiments demonstrating reduced data requirements

### 2.3 Research Hypothesis

**Main Hypothesis (H1):** Neural networks integrating differentiable persistent homology layers with E(n)-equivariant convolutions will achieve 10-15% higher accuracy and 2-3× sample efficiency on tasks with topological structure (molecular rings, 3D genus, neural circuits) compared to geometric-only baselines, because topological priors reduce hypothesis space by encoding global structural constraints that local geometric features cannot capture.

**Null Hypothesis (H0):** Geometric features alone are sufficient—adding topology provides <5% improvement and <1.5× sample efficiency because local geometry already captures relevant structure.

**Causal Mechanism:** The proposed architecture operates through: (1) persistent homology layers computing multi-scale topological signatures (Betti numbers β₀, β₁, β₂), (2) topological constraints guiding representations toward correct global structure, (3) fusion with geometric features to disambiguate locally similar patterns, and (4) complementary constraints reducing hypothesis space.

### 2.4 Significance

This research addresses fundamental questions at the intersection of geometric deep learning, topological data analysis, and neuroscience:

- **Theoretical Impact:** Establishes a category-theoretic framework unifying algebraic topology with geometric deep learning, providing theoretical sample complexity bounds explaining efficiency gains
- **Methodological Impact:** Introduces the first fully differentiable persistent homology layers compatible with modern deep learning frameworks, enabling end-to-end learning of topological features
- **Practical Impact:** Delivers performance improvements on critical scientific applications including drug discovery (molecular property prediction), 3D perception (robotics and computer vision), and computational neuroscience (connectome analysis)
- **Neuroscience Relevance:** Provides computational models that mirror how biological neural circuits preserve both local geometric structure and global topological invariants, contributing to the NeurReps workshop's mission of understanding substrate-agnostic principles for information processing

## 3. Methodology

### 3.1 Theoretical Framework

#### 3.1.1 Category-Theoretic Formulation

We formalize TGNNs using category theory to prove the compositionality of geometric and topological constraints. Let $\mathcal{C}_{\text{Geom}}$ be the category of geometric spaces with equivariant maps, and $\mathcal{C}_{\text{Top}}$ be the category of topological spaces with continuous maps. We define a functor $F: \mathcal{C}_{\text{Geom}} \rightarrow \mathcal{C}_{\text{Top}}$ that forgets geometric structure while preserving topology.

The TGNN architecture implements a natural transformation between functors that preserves both structures:

$$\text{TGNN}: (\mathcal{X}, G, \tau) \rightarrow (\mathcal{Y}, H, \sigma)$$

where $\mathcal{X}$ is the input space, $G$ is the symmetry group (e.g., E(3)), $\tau$ is the topological structure, $\mathcal{Y}$ is the output space, $H$ is the output symmetry group, and $\sigma$ is the preserved topological invariants.

#### 3.1.2 Persistent Homology Formulation

For a point cloud $X = \{x_1, \ldots, x_n\} \subset \mathbb{R}^d$, we construct a filtration of simplicial complexes:

$$\emptyset = K_0 \subseteq K_1 \subseteq \cdots \subseteq K_m = K$$

The $k$-th Betti number $\beta_k(r)$ counts the number of $k$-dimensional holes at filtration parameter $r$. The persistence diagram $\text{Dgm}_k(X)$ records birth-death pairs $(b, d)$ of topological features.

We vectorize persistence diagrams using persistence landscapes:

$$\lambda_k(t) = \sup_{(b,d) \in \text{Dgm}_k} \min(t-b, d-t, 0)$$

### 3.2 Architecture Design

#### 3.2.1 Overall Architecture

The TGNN architecture consists of four main components:

1. **Geometric Feature Extraction:** E(n)-equivariant convolutional layers
2. **Local Sampling:** k-nearest neighbor selection for scalable topology computation
3. **Topological Feature Extraction:** Differentiable persistent homology layers
4. **Feature Fusion:** Multi-layer perceptron combining geometric and topological features

Mathematically, the forward pass is:

$$\mathbf{h}_{\text{geom}} = \text{E3Conv}(X, E)$$
$$X_{\text{local}} = \text{kNN}(\mathbf{h}_{\text{geom}}, k)$$
$$\mathbf{h}_{\text{top}} = \text{DiffPH}(X_{\text{local}})$$
$$\mathbf{y} = \text{MLP}([\mathbf{h}_{\text{geom}} \oplus \mathbf{h}_{\text{top}}])$$

where $X$ is the input point cloud, $E$ are edges, $\oplus$ denotes concatenation, and $k$ is the neighborhood size.

#### 3.2.2 Differentiable Persistent Homology Layer

The key innovation is making persistent homology differentiable. We employ three techniques:

**Soft Sorting:** Replace discrete sorting in filtration construction with differentiable soft-sorting:

$$\text{SoftSort}(x_i; \tau) = \sum_{j=1}^n P_{ij}(\tau) x_j$$

where $P_{ij}(\tau) = \frac{\exp(-|r_i - r_j|/\tau)}{\sum_k \exp(-|r_i - r_k|/\tau)}$ and $\tau$ is the temperature parameter.

**Chain Complex Gradients:** Compute gradients through the boundary operator $\partial_k: C_k \rightarrow C_{k-1}$ using implicit differentiation:

$$\frac{\partial \beta_k}{\partial \theta} = \frac{\partial}{\partial \theta}(\dim \ker \partial_k - \dim \text{im } \partial_{k+1})$$

**Landscape Vectorization:** Convert persistence diagrams to persistence landscapes with $L^p$ norm:

$$\|\lambda\|_p = \left(\int_{-\infty}^{\infty} |\lambda(t)|^p dt\right)^{1/p}$$

Gradients flow through the landscape representation:

$$\frac{\partial \|\lambda\|_p}{\partial X} = \frac{\partial \|\lambda\|_p}{\partial \lambda} \cdot \frac{\partial \lambda}{\partial \text{Dgm}} \cdot \frac{\partial \text{Dgm}}{\partial X}$$

#### 3.2.3 E(n)-Equivariant Layers

We use tensor field networks that transform equivariantly under the Euclidean group E(n):

$$\mathbf{h}_i^{(l+1)} = \phi\left(\sum_{j \in \mathcal{N}(i)} W^{(l)}(\mathbf{x}_i - \mathbf{x}_j) \mathbf{h}_j^{(l)}\right)$$

where $W^{(l)}$ are learnable radial functions and $\phi$ is a nonlinearity preserving equivariance.

### 3.3 Data Collection and Preprocessing

#### 3.3.1 Datasets

**QM9 Molecular Dataset:**
- 134,000 organic molecules with up to 9 heavy atoms
- Properties: HOMO-LUMO gap, dipole moment, isotropic polarizability
- Topological relevance: Ring structures (β₁), molecular connectivity (β₀)
- Preprocessing: 3D coordinates, atomic numbers, bond types

**ModelNet40 3D Shapes:**
- 12,311 CAD models across 40 categories
- Topological relevance: Genus (β₁), connected components (β₀), voids (β₂)
- Preprocessing: Point cloud sampling (2048 points), normalization

**Connectome Dataset:**
- C. elegans neural connectome (302 neurons, ~7000 synapses)
- Drosophila hemibrain connectome (25,000 neurons)
- Topological relevance: Circuit motifs, feedback loops
- Preprocessing: Adjacency matrices, spatial coordinates, neuron types

#### 3.3.2 Synthetic Topology-Labeled Data

To validate Betti number recovery, we generate synthetic datasets:

- **Tori:** Point clouds sampled from $S^1 \times S^1$ (β₀=1, β₁=2, β₂=1)
- **Spheres:** Point clouds from $S^2$ (β₀=1, β₁=0, β₂=1)
- **Linked Rings:** Two linked circles (β₀=1, β₁=2, β₂=0)
- **Noise Levels:** Gaussian noise σ ∈ {0.0, 0.05, 0.1, 0.2}

### 3.4 Experimental Design

#### 3.4.1 Sub-Hypothesis 1 (SH1): Differentiable PH Validation

**Objective:** Validate that differentiable PH layers compute topological features with >90% Betti number recovery and stable gradients.

**Experiment:**
1. Train TGNN on synthetic topology-labeled data
2. Measure Betti number recovery: $\text{Accuracy} = \frac{1}{N}\sum_{i=1}^N \mathbb{1}[\hat{\beta}_k^{(i)} = \beta_k^{(i)}]$
3. Compute gradient signal-to-noise ratio: $\text{SNR} = \frac{\|\mathbb{E}[\nabla_\theta L]\|}{\text{std}(\nabla_\theta L)}$
4. Vary temperature τ ∈ {0.01, 0.05, 0.1, 0.5} and neighborhood size k ∈ {100, 200, 500, 1000}

**Success Criteria:**
- Betti number recovery >90% for β₀, β₁, β₂
- Gradient SNR >10
- Stable training (loss convergence within 100 epochs)

#### 3.4.2 Sub-Hypothesis 2 (SH2): Feature Complementarity

**Objective:** Demonstrate that topological and geometric features are complementary and fusion outperforms either alone.

**Experiment:**
1. Train three variants: Geometric-only, Topological-only, Fusion (TGNN)
2. Measure feature correlation: $\rho = \text{corr}(\mathbf{h}_{\text{geom}}, \mathbf{h}_{\text{top}})$
3. Ablation study: Compare fusion strategies (concatenation, addition, attention)
4. Gradient attribution: Measure $\|\nabla_{\mathbf{h}_{\text{top}}} L\|$ vs. $\|\nabla_{\mathbf{h}_{\text{geom}}} L\|$

**Success Criteria:**
- Feature correlation <0.7 (complementarity)
- Fusion outperforms both single-modality models by ≥5%
- Topological gradients in top 20% magnitude when topology is task-relevant

#### 3.4.3 Sub-Hypothesis 3 (SH3): Performance Comparison

**Objective:** Demonstrate TGNN outperforms baselines by ≥10% accuracy with 2-3× sample efficiency.

**Baselines:**
- **Geometric:** E3nn, SchNet, GemNet
- **Topological:** perslay (precomputed PH + MLP)
- **Hybrid (non-learnable):** Geometric features + precomputed PH concatenation

**Experiment:**
1. **Accuracy Comparison:** 5-fold cross-validation on all datasets
2. **Sample Efficiency:** Learning curves with training set sizes {100, 500, 1K, 5K, 10K, 50K}
3. **Robustness:** Add Gaussian noise σ ∈ {0.05, 0.1, 0.2} to test data
4. **Statistical Testing:** Paired t-tests (p < 0.05) across folds

**Metrics:**
- **Classification:** Accuracy, F1-score, confusion matrices
- **Regression:** Mean Absolute Error (MAE), R² score
- **Sample Efficiency:** Training samples to reach 90% of maximum performance
- **Robustness:** Accuracy drop under noise perturbations

### 3.5 Training Procedures

**Optimizer:** AdamW with learning rate 1e-3, weight decay 1e-4

**Learning Rate Schedule:** Cosine annealing with warm restarts

**Batch Size:** 32 (molecules), 16 (3D shapes), 8 (connectomes)

**Epochs:** 200 with early stopping (patience=20)

**Loss Functions:**
- Classification: Cross-entropy
- Regression: Smooth L1 loss
- Optional topological regularization: $L_{\text{total}} = L_{\text{task}} + \lambda \sum_k |\hat{\beta}_k - \beta_k^{\text{target}}|$

**Hardware:** 4× NVIDIA A100 GPUs (40GB), distributed data parallel training

### 3.6 Evaluation Metrics

**Primary Metrics:**
1. **Test Accuracy/MAE:** Performance on held-out test sets
2. **Sample Efficiency Ratio:** $\text{SER} = \frac{N_{\text{baseline}}^{90\%}}{N_{\text{TGNN}}^{90\%}}$ where $N^{90\%}$ is samples to reach 90% max performance
3. **Betti Number Recovery:** Percentage of correctly predicted topological features

**Secondary Metrics:**
1. **Training Time:** Wall-clock time to convergence
2. **Inference Speed:** Samples processed per second
3. **Memory Usage:** Peak GPU memory consumption
4. **Gradient Quality:** SNR, magnitude distribution
5. **Robustness:** Performance degradation under noise

**Statistical Analysis:**
- 5-fold cross-validation with different random seeds
- Paired t-tests for significance testing (α = 0.05)
- Bonferroni correction for multiple comparisons
- Effect size reporting (Cohen's d)

### 3.7 Falsification Criteria

The hypothesis will be considered falsified if:
1. Accuracy improvement <5% over geometric baselines (vs. predicted 10-15%)
2. Sample efficiency ratio <1.5× (vs. predicted 2-3×)
3. Topological features show low gradient magnitude (<10th percentile)
4. Training time overhead >5× (impractical for deployment)
5. Betti number recovery <70% (approximation too lossy)

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Theoretical Contributions:**
1. **Category-Theoretic Framework:** Formal proof that topological and geometric constraints compose via functorial composition, establishing theoretical foundations for unified architectures
2. **Sample Complexity Bounds:** Theoretical analysis showing that dual constraints reduce VC dimension, explaining 2-3× sample efficiency gains
3. **Stability Analysis:** Proof that TGNN representations inherit stability properties from both persistence stability theorem and equivariance

**Methodological Contributions:**
1. **Differentiable Persistent Homology:** First fully differentiable PH layers compatible with PyTorch autodiff, enabling end-to-end learning
2. **Integration Protocol:** Reusable architectural pattern for combining equivariant layers with topological feature extraction
3. **Local Sampling Strategy:** Scalable approach reducing computational complexity from O(n³) to O(k³) while maintaining >95% of global topology performance

**Empirical Contributions:**
1. **Performance Improvements:** 10-15% accuracy gains on QM9 (molecular property prediction), ModelNet40 (3D shape classification), and connectome analysis
2. **Sample Efficiency:** 2-3× reduction in required training data, critical for data-scarce scientific domains
3. **Robustness:** +20% improved performance under noise perturbations due to topological stability
4. **Ablation Studies:** Comprehensive analysis of architectural choices, hyperparameters, and fusion strategies

### 4.2 Scientific Impact

**Geometric Deep Learning:**
- Extends the geometric deep learning blueprint (Bronstein et al., 2021) to incorporate topological priors
- Demonstrates that symmetry and topology are complementary inductive biases
- Provides new tools for learning on structured scientific data

**Topological Data Analysis:**
- Bridges the gap between TDA and deep learning through differentiable persistence
- Enables learning of task-relevant topological features rather than hand-crafted descriptors
- Validates topological methods on large-scale benchmarks

**Neuroscience:**
- Provides computational models mirroring biological neural circuits that preserve geometric and topological structure
- Offers new analysis tools for connectome data incorporating both local connectivity patterns and global circuit topology
- Contributes to understanding substrate-agnostic principles for neural representation

### 4.3 Practical Applications

**Drug Discovery:**
- Improved molecular property prediction incorporating ring structures and 3D geometry
- Better generalization to novel molecular scaffolds
- Reduced data requirements for training on expensive experimental measurements

**Robotics and 3D Vision:**
- Enhanced 3D object recognition using genus and geometric features
- Robust shape classification under occlusions and noise
- Applications in manipulation, navigation, and scene understanding

**Computational Neuroscience:**
- Automated analysis of neural connectomes identifying circuit motifs
- Prediction of functional properties from structural connectivity
- Cross-species comparison of circuit architectures

### 4.4 Open-Source Contributions

We will release:
1. **tgnn Library:** PyTorch implementation of TGNNs built on e3nn and giotto-tda
2. **Pretrained Models:** Checkpoints for QM9, ModelNet40, and connectome tasks
3. **Benchmarks:** Standardized evaluation protocols and datasets
4. **Documentation:** Tutorials, API reference, and example notebooks

### 4.5 Future Directions

**Short-term (1-2 years):**
- Extension to larger point clouds (>10K points) using hierarchical methods
- Application to protein structure prediction and RNA folding
- Integration with graph neural networks for molecular graphs

**Medium-term (3-5 years):**
- Advanced topological descriptors beyond Betti numbers (persistence images, Euler characteristics)
- Transfer learning across domains (molecules → 3D shapes)
- Theoretical analysis of expressiveness and universal approximation

**Long-term (5+ years):**
- Biological plausibility: Can biological neural circuits implement topological computation?
- Unified theory of geometric and topological representation learning
- Applications to higher-dimensional data (4D spacetime, high-dimensional scientific data)

### 4.6 Broader Impact

This research addresses fundamental questions about how neural systems—both biological and artificial—represent structured information. By unifying geometric and topological approaches, we contribute to the NeurReps workshop's mission of discovering substrate-agnostic principles for information processing. The convergence of findings from neuroscience, mathematics, and machine learning suggests deep principles that transcend specific implementations, much as symmetry and geometry unified 20th-century physics.

The practical applications in drug discovery, robotics, and neuroscience have potential for significant societal benefit. Improved molecular property prediction can accelerate drug development, enhanced 3D perception can enable more capable robots, and better connectome analysis tools can advance our understanding of brain function and dysfunction.

By releasing open-source tools and establishing benchmarks, we aim to catalyze further research at the intersection of topology, geometry, and deep learning, fostering a community that bridges mathematics, neuroscience, and machine learning.

---

**Total Word Count:** ~4,200 words (extended for comprehensiveness; can be condensed to 2,000 words by reducing background and future directions sections if needed)