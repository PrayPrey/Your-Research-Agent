# Research Proposal: Attractor-Equivariant Layers: Inducing Geometric Symmetries via Soft Topological Constraints on Neural Manifolds

## 1. Introduction

### Background

The quest to understand how neural systems—both biological and artificial—encode and process information has revealed a striking convergence: geometric and topological structures appear to be fundamental organizing principles across substrates. In neuroscience, decades of research have uncovered that neural circuits often mirror the mathematical structure of the quantities they represent. Head direction cells in the fly brain form ring attractors that encode angular position on a circle (SO(2)), grid cells in the entorhinal cortex tile space with hexagonal patterns reflecting toroidal topology (T²), and motor cortex activity unfolds on low-dimensional manifolds that preserve the geometry of movement. These findings suggest that biological neural networks have evolved to exploit geometric structure as a computational strategy.

Independently, the field of deep learning has arrived at remarkably similar principles through the framework of Geometric Deep Learning (GDL). By incorporating geometric priors—such as translation equivariance in convolutional neural networks or rotation equivariance in architectures like e3nn—artificial neural networks achieve improved sample efficiency, robustness, and generalization. The mathematical foundation of GDL rests on group theory: a function $f$ is equivariant to a group $G$ if $f(g \cdot x) = g \cdot f(x)$ for all group elements $g \in G$ and inputs $x$. Current approaches achieve this through hard architectural constraints that explicitly encode symmetry operations into network structure.

However, a fundamental gap exists between these two paradigms. Biological neural circuits achieve equivariant representations through soft, emergent dynamics rather than hard-wired architectural constraints. The ring attractor in the fly brain, for instance, emerges from recurrent connectivity patterns that constrain neural activity to a one-dimensional manifold, with the position of an activity "bump" encoding the current heading direction. This raises a profound question: can we bridge the gap between the hard constraints of geometric deep learning and the soft, dynamic constraints observed in biological systems?

### Research Objectives

This research proposes to develop and validate **Attractor-Equivariant Layers (AELs)**—a novel neural network architecture that induces equivariant representations through soft topological constraints on network dynamics rather than hard architectural constraints. Our central hypothesis is:

> Under the condition of neural networks with recurrent dynamics constrained to specific manifold topologies, if the attractor manifold is topologically isomorphic to the task's symmetry group, then the network will exhibit equivariant representations by construction, because the activity bump position on the attractor encodes a group element and bump translation implements the group action.

Our specific objectives are:
1. To develop differentiable topological loss functions based on persistent homology that constrain neural network dynamics to target manifold topologies (ring, torus, sphere).
2. To demonstrate that these soft constraints induce measurable equivariance with error below 0.1 as measured by Lie derivatives.
3. To validate the causal mechanism linking manifold topology to equivariance through systematic ablation studies.
4. To compare AELs against state-of-the-art hard-constraint methods (e3nn) on standard benchmarks.

### Significance

This research addresses a critical gap at the intersection of neuroscience and machine learning. By establishing substrate-agnostic principles linking attractor dynamics to equivariance, we contribute to:

1. **Theoretical unification**: Demonstrating that soft topological constraints can achieve equivariance provides a mathematical bridge between biological and artificial neural computation.
2. **Interpretability**: Unlike black-box equivariant architectures, AELs offer interpretable dynamics where the activity bump position directly encodes geometric quantities.
3. **Biological plausibility**: Soft constraints maintain gradient-based trainability while respecting biological constraints, enabling more realistic models of neural computation.
4. **Practical applications**: If successful, AELs could provide a new paradigm for building equivariant networks in domains where hard constraints are difficult to specify or implement.

## 2. Methodology

### 2.1 Theoretical Framework

We formalize the relationship between attractor manifolds and equivariance as follows. Let $\mathcal{M}$ be a compact manifold serving as the attractor of a recurrent neural network, and let $G$ be a Lie group representing the symmetry of the task. We hypothesize that if $\mathcal{M} \cong G$ (topological isomorphism), then the network naturally implements equivariant representations.

**Definition (Attractor-Equivariance)**: A recurrent neural network with state $h \in \mathbb{R}^n$ and attractor manifold $\mathcal{M}$ is attractor-equivariant with respect to group $G$ if:
1. There exists a homeomorphism $\phi: \mathcal{M} \rightarrow G$
2. For input transformation $g \cdot x$, the activity bump translates by $g$: $\phi(h_{g \cdot x}) = g \cdot \phi(h_x)$
3. The output function $f$ satisfies $f(h_{g \cdot x}) = g \cdot f(h_x)$

### 2.2 Architecture Design

**Attractor-Equivariant Layer (AEL)** consists of three components:

**Component 1: Recurrent Dynamics Module**
We employ a continuous-time recurrent neural network with dynamics:
$$\tau \frac{dh}{dt} = -h + W_r \sigma(h) + W_x x + b$$
where $h \in \mathbb{R}^n$ is the hidden state, $W_r \in \mathbb{R}^{n \times n}$ is the recurrent weight matrix, $W_x$ is the input projection, $\sigma$ is a nonlinearity (tanh), and $\tau$ is the time constant. In practice, we discretize using Euler integration with step size $\Delta t$.

**Component 2: Topological Constraint Module**
To constrain dynamics to target manifold $\mathcal{M}$, we introduce a differentiable topological loss based on persistent homology. Given a batch of hidden states $\{h_i\}_{i=1}^B$, we:

1. Construct a Vietoris-Rips complex from pairwise distances
2. Compute persistent homology using differentiable persistence (via the method of Carrière et al.)
3. Define the topological loss:
$$\mathcal{L}_{topo} = \sum_{k=0}^{K} \lambda_k \left| \beta_k^{computed} - \beta_k^{target} \right|^2 + \gamma \sum_{(b,d) \in \text{Dgm}_k} (d-b)^{-1}$$

where $\beta_k$ are Betti numbers (e.g., $\beta_1 = 1$ for ring, $\beta_1 = 2$ for torus), and the second term encourages persistence of topological features.

**Component 3: Readout Module**
The output is computed from the bump position on the manifold:
$$y = W_o \cdot \text{BumpPosition}(h) + b_o$$
where BumpPosition extracts the center of mass of activity on the attractor manifold using soft argmax.

### 2.3 Training Procedure

The total loss function combines task loss and topological regularization:
$$\mathcal{L}_{total} = \mathcal{L}_{task} + \alpha \mathcal{L}_{topo} + \beta \mathcal{L}_{reg}$$

where $\mathcal{L}_{task}$ is cross-entropy for classification or MSE for regression, $\alpha$ controls topological constraint strength (hyperparameter), and $\mathcal{L}_{reg}$ includes standard regularization (weight decay, spectral normalization).

**Training Algorithm:**
```
Input: Dataset D, target topology T, epochs E
Initialize: Recurrent weights W_r, input weights W_x, output weights W_o
For epoch = 1 to E:
    For batch (x, y) in D:
        1. Forward pass: h = RNN_dynamics(x, W_r, W_x)
        2. Compute task loss: L_task = CrossEntropy(Readout(h), y)
        3. Compute topological loss: L_topo = PersistentHomologyLoss(h, T)
        4. Total loss: L = L_task + α * L_topo
        5. Backward pass: Compute gradients via backpropagation
        6. Update weights using Adam optimizer
    End For
    Evaluate equivariance error on validation set
End For
Output: Trained AEL model
```

### 2.4 Equivariance Measurement

We measure equivariance error using the Lie derivative approach from Gruver et al. (2022). For a function $f$ and infinitesimal generator $V$ of group action:
$$\mathcal{E}_{equiv} = \mathbb{E}_{x \sim \mathcal{D}} \left[ \frac{\| \mathcal{L}_V f(x) \|^2}{\| f(x) \|^2 + \epsilon} \right]$$

where $\mathcal{L}_V f = \lim_{t \rightarrow 0} \frac{f(\exp(tV) \cdot x) - f(x)}{t}$ is the Lie derivative. In practice, we approximate this with finite differences using small rotation angles $\theta \in \{1°, 5°, 10°\}$.

### 2.5 Experimental Design

**Experiment 1: Manifold Emergence Validation (SH1)**
- **Objective**: Verify that soft topological constraints induce target manifold structure
- **Method**: Train AELs with ring topology constraint on RotMNIST; analyze learned representations using persistent homology
- **Metrics**: Betti numbers ($\beta_0$, $\beta_1$, $\beta_2$), persistence diagrams, manifold visualization via UMAP
- **Success Criterion**: $\beta_1 = 1 \pm 0.1$ for ring attractor (averaged over 20 runs)

**Experiment 2: Equivariance Induction (Primary - P1)**
- **Objective**: Demonstrate that AELs achieve low equivariance error
- **Dataset**: RotMNIST (60,000 training images with random rotations)
- **Baselines**: (a) Standard RNN without topological constraint, (b) e3nn with hard SO(2) equivariance, (c) Data augmentation baseline
- **Metrics**: Lie derivative equivariance error, classification accuracy
- **Success Criterion**: Equivariance error < 0.1 with $p < 0.05$ (one-sample t-test, $n = 20$)

**Experiment 3: Mechanism Ablation (P2)**
- **Objective**: Confirm causal role of topological constraints
- **Method**: Compare full AEL vs. ablated versions: (a) no topological loss ($\alpha = 0$), (b) wrong topology (torus instead of ring), (c) random topology target
- **Metrics**: Equivariance error change, manifold structure degradation
- **Success Criterion**: Removing topological loss increases equivariance error by >50% ($p < 0.05$, paired t-test)

**Experiment 4: Comparative Benchmark (P3)**
- **Objective**: Compare AEL performance against state-of-the-art
- **Datasets**: RotMNIST, ModelNet40 (3D object classification)
- **Baselines**: e3nn, GE-CNN, standard CNN with augmentation
- **Metrics**: Classification accuracy, equivariance error, training time, parameter count
- **Success Criterion**: Accuracy within 2% of e3nn baseline

**Experiment 5: Biological Plausibility Analysis**
- **Objective**: Compare AEL dynamics to biological ring attractors
- **Method**: Analyze bump dynamics, drift patterns, and response to perturbations
- **Comparison**: Qualitative comparison to fly head direction system (Biswas et al., 2024)
- **Metrics**: Bump width, drift velocity, recovery time after perturbation

### 2.6 Implementation Details

- **Framework**: PyTorch with custom persistent homology module (Gudhi backend)
- **Hardware**: Single NVIDIA A100 GPU for SO(2) experiments; 4× A100 for SO(3)
- **Hyperparameters**: Hidden dimension $n = 256$, time constant $\tau = 10$, topological weight $\alpha \in \{0.01, 0.1, 1.0\}$ (grid search), learning rate $10^{-4}$, batch size 32, 100 epochs
- **Reproducibility**: Fixed random seeds (42, 123, 456, ...), code release on GitHub

### 2.7 Statistical Analysis Plan

- **Sample size**: $n = 20$ independent runs per condition (power analysis: $d = 0.8$, power $= 0.8$, $\alpha = 0.05$)
- **Primary analysis**: One-sample t-test for equivariance error < 0.1
- **Secondary analyses**: Paired t-tests for ablations, independent t-tests for baseline comparisons
- **Multiple comparison correction**: Bonferroni correction for secondary analyses
- **Effect size reporting**: Cohen's $d$ with 95% confidence intervals

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Primary Outcome (P1)**: We expect AELs with ring manifold topology to achieve equivariance error below 0.1 on rotation tasks, demonstrating that soft topological constraints can induce meaningful equivariance. Based on prior work showing that well-trained vision models achieve equivariance errors of 0.05-0.15, we anticipate our method will fall within this range while providing interpretable attractor dynamics.

**Mechanism Validation (P2)**: We predict that removing the topological loss term will increase equivariance error by more than 50%, confirming that manifold structure is causally responsible for equivariance rather than being an incidental byproduct of training.

**Comparative Performance (P3)**: We expect AELs to achieve classification accuracy within 2% of e3nn baselines on RotMNIST (target: >98% accuracy) while offering advantages in interpretability and biological plausibility.

**Negative Results Protocol**: If equivariance error exceeds 0.5 despite topological constraints, we will investigate whether: (a) the topological loss is insufficiently strong, (b) the discrete approximation to continuous attractors is inadequate, or (c) the fundamental hypothesis requires revision.

### Scientific Impact

1. **Theoretical Contribution**: This work establishes a formal connection between attractor dynamics and equivariance, providing a mathematical framework that unifies findings from neuroscience and geometric deep learning. The principle that "manifold topology determines equivariance type" could become a foundational result in computational neuroscience.

2. **Methodological Contribution**: The development of differentiable topological loss functions for inducing specific manifold structures represents a novel tool for the machine learning community, with applications beyond equivariance to manifold learning, representation learning, and topological data analysis.

3. **Neuroscience Implications**: By demonstrating that soft constraints can achieve equivariance, we provide computational support for the hypothesis that biological neural circuits exploit attractor dynamics for geometric computation. This could inform experimental predictions about neural coding in systems beyond head direction and grid cells.

### Broader Impact

**Applications**: AELs could enable equivariant architectures in domains where hard constraints are difficult to specify, such as robotics (learning SE(3) equivariance for manipulation), drug discovery (molecular symmetries), and climate modeling (spherical geometry).

**Interpretability**: Unlike black-box equivariant networks, AELs provide interpretable representations where geometric quantities are explicitly encoded as bump positions, facilitating debugging, verification, and scientific understanding.

**Limitations and Risks**: Soft constraints yield approximate rather than exact equivariance, which may be insufficient for safety-critical applications requiring guaranteed symmetry properties. Additionally, the computational overhead of persistent homology calculations may limit scalability to very large networks.

### Timeline and Milestones

- **Months 1-2**: Implement AEL architecture and topological loss functions
- **Months 3-4**: Conduct Experiments 1-2 (manifold emergence, equivariance induction)
- **Months 5-6**: Conduct Experiments 3-5 (ablations, benchmarks, biological analysis)
- **Month 7**: Statistical analysis, paper writing, code release

This research program, if successful, will establish a new paradigm for understanding and building equivariant neural networks—one grounded in the elegant mathematical principles that appear to govern computation in both biological and artificial neural systems.