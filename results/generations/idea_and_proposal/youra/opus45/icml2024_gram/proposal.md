# Research Proposal: Unified Constraint Annealing Networks (UCANs): Joint Optimization of Geometric Equivariance and Physics Constraints

## 1. Introduction

### 1.1 Background

Modern machine learning increasingly addresses problems rooted in the physical world, where data inherently possesses geometric structure and obeys physical laws. Two powerful paradigms have emerged to incorporate these inductive biases: Geometric Deep Learning (GDL) and Physics-Informed Neural Networks (PINNs). GDL leverages symmetry preservation through equivariant architectures, ensuring that learned representations transform predictably under group actions such as rotations, translations, and reflections. This approach has achieved remarkable success in computational chemistry, molecular dynamics, and materials science, with architectures like E(n)-Equivariant Graph Neural Networks (EGNNs) and NequIP demonstrating superior data efficiency and generalization. Concurrently, PINNs embed physical laws directly into neural network training by incorporating partial differential equation (PDE) residuals as loss terms, enabling physics-consistent predictions even with limited data.

Despite their complementary nature—both encoding fundamental physical principles—these paradigms have evolved largely in isolation. GDL research focuses on architectural constraints that enforce exact equivariance, while PINN research emphasizes loss function design for physics constraint satisfaction. This separation creates a critical gap: many real-world applications, such as molecular dynamics simulations and fluid mechanics, require simultaneous satisfaction of both geometric symmetries and physical conservation laws. Current approaches that attempt to combine these constraints face significant optimization challenges. Hard equivariance constraints restrict the solution space, potentially trapping optimization in local minima, while fixed physics loss weights create gradient conflicts that destabilize training.

Recent work has begun addressing these challenges independently. Pertigkiozoglou et al. (2024) demonstrated that relaxing equivariance constraints during training improves molecular property prediction by 15-20%, while DB-PINN (2025) showed that adaptive physics loss weighting resolves spectral bias in PINNs. However, no existing method provides a unified framework for jointly optimizing both constraint types through a principled annealing mechanism.

### 1.2 Research Objectives

This research proposes Unified Constraint Annealing Networks (UCANs), a novel framework that treats geometric equivariance and physics constraints as symmetric soft constraints controlled by a single annealing parameter. Our primary objectives are:

1. **Develop a unified optimization framework** that jointly relaxes and progressively tightens both equivariance and physics constraints through a single scheduling mechanism.

2. **Demonstrate improved training convergence** compared to hard-constraint baselines and single-constraint methods, achieving at least 10% faster convergence to target loss thresholds.

3. **Achieve superior task performance** with at least 5% lower prediction error compared to best single-constraint approaches while guaranteeing satisfaction of both constraint types at convergence.

4. **Validate cross-domain applicability** by demonstrating the framework's effectiveness across molecular dynamics (MD17, QM9) and fluid dynamics (Navier-Stokes) benchmarks.

### 1.3 Significance

This research addresses a fundamental gap at the intersection of geometric deep learning and physics-informed machine learning. By providing a unified optimization perspective, UCANs bridge two major research communities (GDL with 3.6K+ citations and PINNs with 14K+ citations) that have operated largely independently. The theoretical contribution—viewing geometric symmetries and physical laws as symmetric soft constraints amenable to joint annealing—offers a generalizing perspective that could inspire future work on constraint-aware neural network optimization.

Practically, UCANs enable a new capability: simultaneous satisfaction of geometric and physics constraints with improved training stability. This is essential for applications in computational physics, drug discovery, and climate modeling, where both symmetry preservation and physical law satisfaction are non-negotiable requirements. The framework's simplicity—requiring only a single annealing parameter—makes it accessible for practitioners while maintaining theoretical rigor.

## 2. Methodology

### 2.1 Problem Formulation

Consider a neural network $f_\theta: \mathcal{X} \rightarrow \mathcal{Y}$ parameterized by $\theta$, where the input space $\mathcal{X}$ admits a group action by $G$ (e.g., $E(n)$ for Euclidean transformations). We seek to learn $f_\theta$ that satisfies two constraint types:

**Geometric Equivariance Constraint:** For all $g \in G$ and $x \in \mathcal{X}$:
$$f_\theta(g \cdot x) = \rho(g) \cdot f_\theta(x)$$
where $\rho: G \rightarrow GL(\mathcal{Y})$ is the representation of $G$ on the output space.

**Physics Constraint:** The network output satisfies physical laws expressed as PDE residuals:
$$\mathcal{R}[f_\theta](x) = 0$$
where $\mathcal{R}$ is a differential operator encoding the governing equations.

### 2.2 Unified Constraint Annealing Framework

UCANs introduce a unified annealing parameter $\alpha(t) \in [0, 1]$ that evolves over training time $t \in [0, T]$. The core mechanism couples equivariance relaxation and physics enforcement through complementary schedules:

**Equivariance Relaxation Schedule:**
$$\lambda_{eq}(t) = \lambda_{max} \times (1 - \alpha(t))$$

**Physics Enforcement Schedule:**
$$\beta_{phys}(t) = \beta_{max} \times \alpha(t)$$

where $\lambda_{max}$ controls the maximum equivariance relaxation magnitude and $\beta_{max}$ is the maximum physics constraint weight.

**Training Dynamics:**
- **Early training ($\alpha \approx 0$):** Equivariance is relaxed ($\lambda_{eq} \approx \lambda_{max}$), enlarging the solution space and enabling escape from local minima. Physics weights remain low ($\beta_{phys} \approx 0$), reducing gradient conflicts and allowing focus on representation learning.
- **Progressive training ($\alpha \rightarrow 1$):** Constraints gradually tighten, creating smooth optimization trajectories that avoid the "hard constraint shock" observed in fixed-constraint training.
- **Convergence ($\alpha = 1$):** Exact equivariance is restored ($\lambda_{eq} = 0$) and full physics enforcement is achieved ($\beta_{phys} = \beta_{max}$).

### 2.3 Loss Function Design

The total training loss combines task-specific, equivariance, and physics terms:

$$\mathcal{L}_{total}(\theta, t) = \mathcal{L}_{task}(\theta) + \lambda_{eq}(t) \cdot \mathcal{L}_{eq}(\theta) + \beta_{phys}(t) \cdot \mathcal{L}_{phys}(\theta)$$

**Task Loss:** Domain-specific supervised loss (e.g., energy/force prediction for molecular systems):
$$\mathcal{L}_{task}(\theta) = \frac{1}{N} \sum_{i=1}^{N} \|y_i - f_\theta(x_i)\|^2$$

**Equivariance Violation Loss:** Measures deviation from exact equivariance:
$$\mathcal{L}_{eq}(\theta) = \mathbb{E}_{g \sim G, x \sim \mathcal{X}} \left[ \|f_\theta(g \cdot x) - \rho(g) \cdot f_\theta(x)\|^2 \right]$$

In practice, we sample $K$ group elements per batch and compute:
$$\mathcal{L}_{eq}(\theta) = \frac{1}{K \cdot B} \sum_{k=1}^{K} \sum_{i=1}^{B} \|f_\theta(g_k \cdot x_i) - \rho(g_k) \cdot f_\theta(x_i)\|^2$$

**Physics Constraint Loss:** PDE residual in $L^2$ norm:
$$\mathcal{L}_{phys}(\theta) = \frac{1}{M} \sum_{j=1}^{M} \|\mathcal{R}[f_\theta](x_j)\|^2$$

where collocation points $\{x_j\}_{j=1}^{M}$ are sampled from the domain.

### 2.4 Annealing Schedule

The primary schedule is linear:
$$\alpha(t) = \frac{t}{T}$$

where $T$ is the total training duration. We also investigate cosine annealing as an ablation:
$$\alpha(t) = \frac{1}{2}\left(1 - \cos\left(\frac{\pi t}{T}\right)\right)$$

### 2.5 Architecture Integration

UCANs are architecture-agnostic but designed for integration with equivariant neural networks. We implement the framework on two base architectures:

1. **E(n)-EGNN:** For molecular property prediction, using message-passing with coordinate updates that preserve E(n) equivariance.

2. **e3nn-based networks:** For tasks requiring higher-order tensor features, using spherical harmonics and Clebsch-Gordan tensor products.

The relaxation mechanism modifies equivariant layers by introducing learnable deviation terms:
$$\tilde{f}_\theta(x) = f_\theta^{eq}(x) + \lambda_{eq}(t) \cdot \Delta_\theta(x)$$

where $f_\theta^{eq}$ is the strictly equivariant component and $\Delta_\theta$ is an unconstrained deviation network.

### 2.6 Experimental Design

#### 2.6.1 Datasets

**Molecular Dynamics:**
- **MD17:** 8 small organic molecules with DFT-computed energies and forces. Training: 1,000 samples; Test: 10,000 samples per molecule.
- **QM9:** 134K molecules with 12 quantum mechanical properties. Standard train/validation/test splits.

**Fluid Dynamics:**
- **Navier-Stokes:** 2D incompressible flow with Reynolds numbers Re ∈ {100, 500, 1000}. Generated using spectral methods with 64×64 spatial resolution.

#### 2.6.2 Baselines

| Method | Equivariance | Physics | Description |
|--------|--------------|---------|-------------|
| Hard-EGNN | Hard | None | Standard E(n)-EGNN |
| NequIP | Hard | Implicit | Energy-conserving architecture |
| Relaxed-EGNN | Soft (fixed) | None | Pertigkiozoglou et al. (2024) |
| DB-PINN | None | Adaptive | Zhou et al. (2025) |
| UCANs (Ours) | Soft (annealed) | Annealed | Unified framework |

#### 2.6.3 Evaluation Metrics

**Task Performance:**
- Energy MAE (meV) and Force MAE (meV/Å) for molecular systems
- Velocity MSE for fluid dynamics

**Constraint Satisfaction:**
- Equivariance error: $E_{eq} = \mathbb{E}_{g,x}[\|f(gx) - \rho(g)f(x)\|^2]$
- Physics error: $E_{phys} = \|\mathcal{R}[f]\|_{L^2}$

**Convergence:**
- Epochs to reach target loss threshold (defined as 110% of best baseline final loss)

#### 2.6.4 Experimental Protocol

**Hyperparameter Selection:**
- $\lambda_{max} \in \{0.1, 0.3, 0.5\}$: Grid search on validation set
- $\beta_{max} \in \{0.1, 1.0, 10.0\}$: Grid search on validation set
- Training duration $T$: 500 epochs for MD17, 300 epochs for QM9, 1000 epochs for Navier-Stokes

**Statistical Rigor:**
- 5 random seeds per condition
- Paired t-tests for UCANs vs. hard-constraint baselines ($\alpha = 0.05$)
- Wilcoxon signed-rank tests for UCANs vs. single-constraint methods
- Bonferroni correction for multiple comparisons
- Report mean ± standard deviation, 95% confidence intervals, and Cohen's d effect sizes

#### 2.6.5 Ablation Studies

1. **Schedule comparison:** Linear vs. cosine vs. learned $\alpha(t)$
2. **Unified vs. separate:** Single $\alpha(t)$ vs. independent $\alpha_{eq}(t)$ and $\alpha_{phys}(t)$
3. **Relaxation magnitude:** Sensitivity to $\lambda_{max}$ choice
4. **Training duration:** Effect of $T$ on final constraint satisfaction

### 2.7 Implementation Details

- **Framework:** PyTorch with PyTorch Geometric for graph operations
- **Equivariant layers:** e3nn library for spherical tensor operations
- **Optimizer:** AdamW with learning rate $10^{-3}$, weight decay $10^{-4}$
- **Batch size:** 32 for molecular, 16 for fluid dynamics
- **Hardware:** 4× NVIDIA A100 GPUs
- **Group sampling:** $K = 8$ random rotations per batch for equivariance loss

## 3. Expected Outcomes & Impact

### 3.1 Primary Expected Outcomes

**Convergence Improvement:** We expect UCANs to achieve at least 10% faster convergence compared to hard-constraint baselines. The progressive relaxation mechanism should enable smoother optimization trajectories, avoiding the gradient conflicts that slow training when both constraints are enforced from initialization.

**Task Performance:** We anticipate at least 5% improvement in prediction error compared to the best single-constraint method. For MD17, this translates to energy MAE ≤ 2.5 meV (vs. NequIP's 2.8 meV). For Navier-Stokes, we target velocity MSE ≤ $10^{-4}$.

**Dual Constraint Satisfaction:** Unlike existing methods that satisfy only one constraint type, UCANs should achieve both $E_{eq} < \epsilon_{eq}$ and $E_{phys} < \epsilon_{phys}$ at convergence, where thresholds are defined relative to hard-constraint baselines.

### 3.2 Secondary Expected Outcomes

**Hyperparameter Efficiency:** The unified schedule should perform comparably to separately-tuned dual schedules while requiring 50% fewer hyperparameters (one $\alpha(t)$ vs. separate $\alpha_{eq}(t)$ and $\alpha_{phys}(t)$).

**Cross-Domain Transfer:** The annealing framework should transfer across molecular and fluid dynamics domains without architecture modifications, demonstrating the generality of the unified constraint optimization perspective.

### 3.3 Theoretical Impact

UCANs provide a novel theoretical contribution by unifying geometric equivariance and physics constraints under a common optimization framework. This perspective—treating both constraint types as soft constraints amenable to joint annealing—bridges the GDL and PINN research communities and offers a generalizing view on constraint-aware neural network training. The framework draws on established principles from simulated annealing and curriculum learning, providing theoretical grounding for the progressive constraint tightening approach.

### 3.4 Practical Impact

**Computational Physics:** UCANs enable more stable training of physics-informed equivariant models for molecular dynamics, fluid simulation, and materials science applications where both symmetry preservation and physical law satisfaction are essential.

**Drug Discovery:** Improved molecular property prediction with guaranteed physical consistency could accelerate virtual screening and lead optimization in pharmaceutical research.

**Climate Modeling:** The framework's applicability to fluid dynamics suggests potential for climate and weather prediction models that respect both geometric symmetries and conservation laws.

### 3.5 Limitations and Future Work

**Scope Limitations:** The current framework focuses on continuous symmetry groups (E(n)) and differentiable physics constraints. Extension to discrete symmetries and non-differentiable physics (e.g., contact mechanics) remains future work.

**Scalability:** While validated on small-to-medium datasets, scalability to large-scale industrial applications requires further investigation.

**Schedule Learning:** The fixed linear schedule may be suboptimal for some problems. Future work could explore learned annealing schedules that adapt to problem-specific optimization landscapes.

### 3.6 Broader Impact

By providing a principled framework for combining geometric and physics constraints, UCANs contribute to the broader goal of building neural networks that respect the fundamental structure of physical reality. This aligns with the workshop's focus on geometry-grounded representation learning and could inspire future work on unified constraint optimization across diverse scientific domains.