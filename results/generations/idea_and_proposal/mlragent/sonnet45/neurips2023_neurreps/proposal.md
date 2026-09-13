# Equivariant Graph Neural Networks for Decoding Neural Population Dynamics in Motor Cortex

## 1. Introduction

### Background

The motor cortex plays a fundamental role in planning and executing voluntary movements, with neural population activity exhibiting rich geometric structure that reflects the underlying computational principles of motor control. Recent discoveries in neuroscience have revealed that neural representations in motor cortex lie on low-dimensional manifolds whose geometry encodes movement parameters such as direction, velocity, and position. These findings align with an emerging paradigm suggesting that neural circuits throughout the brain preserve the geometric and topological structure of the systems they represent—a principle observed in head direction cells in *Drosophila*, grid cells in entorhinal cortex, and preparatory activity in motor regions.

Concurrently, the field of geometric deep learning has developed powerful frameworks for incorporating geometric priors into artificial neural networks through equivariant architectures. These models, which preserve specific symmetries as data flows through network layers, have demonstrated superior computational efficiency, robustness, and generalization compared to conventional architectures. The convergence of these neuroscientific observations and machine learning innovations suggests that fundamental, substrate-agnostic principles govern information processing in both biological and artificial systems.

Despite these parallel advances, current neural decoding methods for brain-machine interfaces (BMIs) largely ignore the inherent geometric structure and group-theoretic symmetries of motor actions. Standard linear decoders, Kalman filters, and even modern deep learning approaches treat neural activity as vectors in Euclidean space, failing to leverage the fact that reaching movements possess natural symmetries under rotations, translations, and reflections. This limitation constrains both decoding accuracy and the ability to generalize across different movement contexts—a critical requirement for practical BMI systems.

### Research Objectives

This research proposes a novel framework that bridges geometric deep learning and computational neuroscience by developing **SE(3)-equivariant graph neural networks** integrated with **topological data analysis** for decoding motor cortex population dynamics. Our specific objectives are:

1. **Develop equivariant neural decoders** that respect the rotational and translational symmetries inherent to reaching movements in 3D space
2. **Construct interpretable functional connectivity graphs** from neural population recordings that capture task-relevant interactions
3. **Integrate topological features** extracted via persistent homology to characterize neural manifold structure across movement phases
4. **Validate improved decoding performance** demonstrating 20-30% accuracy gains over state-of-the-art methods
5. **Demonstrate enhanced generalization** to novel movement directions, velocities, and workspace locations
6. **Extract interpretable geometric representations** revealing how motor cortex factorizes movement parameters

### Significance

This research addresses critical gaps at the intersection of neuroscience and machine learning. From a **practical perspective**, improved decoding accuracy and generalization capabilities will advance BMI technology, benefiting individuals with paralysis or motor impairments. The ability to generalize across contexts reduces calibration requirements—a major barrier to clinical BMI deployment.

From a **theoretical perspective**, this work tests the hypothesis that biological neural circuits implement equivariant computations analogous to those in geometric deep learning architectures. By demonstrating that SE(3)-equivariant decoders outperform traditional methods, we provide evidence that motor cortex preserves geometric structure in its representations. The interpretable features extracted by our framework may reveal computational principles of how biological systems factor complex motor variables.

Finally, this research contributes **methodological innovations** applicable beyond motor decoding, including: (1) principled approaches for constructing task-relevant neural connectivity graphs, (2) techniques for integrating discrete graph structure with continuous geometric symmetries, and (3) methods for combining equivariant neural networks with topological data analysis. These tools will benefit researchers studying neural representations across sensory, cognitive, and motor domains.

## 2. Methodology

### 2.1 Data Collection and Preprocessing

**Neural Recordings**: We will utilize publicly available datasets from non-human primate motor cortex recordings during center-out reaching tasks, specifically:
- The Neural Latents Benchmark dataset containing Utah array recordings (96-192 channels) from dorsal premotor and primary motor cortex
- Data from reaching tasks with targets distributed in 3D workspace
- Recording sessions spanning multiple days to assess generalization across time

**Movement Kinematics**: Synchronized hand position, velocity, and acceleration data in 3D Cartesian coordinates will serve as decoding targets. We denote hand position at time $t$ as $\mathbf{p}(t) = [x(t), y(t), z(t)]^T \in \mathbb{R}^3$ and velocity as $\mathbf{v}(t) = \dot{\mathbf{p}}(t)$.

**Preprocessing Pipeline**:
1. Spike sorting and quality metrics to isolate single units
2. Binning spike counts in 50ms windows
3. Square-root transformation for variance stabilization: $r_i(t) = \sqrt{n_i(t)}$ where $n_i(t)$ is the spike count for neuron $i$
4. Z-score normalization per neuron across the session
5. Alignment of neural data to behavioral events (movement onset, target acquisition)

### 2.2 Functional Connectivity Graph Construction

We construct a task-dependent functional connectivity graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ where nodes represent neurons and edges encode functional interactions.

**Node Features**: For neuron $i$ at time $t$, the feature vector is:
$$\mathbf{h}_i^{(0)}(t) = [r_i(t-\tau), ..., r_i(t), ..., r_i(t+\tau)]^T \in \mathbb{R}^{2\tau+1}$$
capturing temporal context with window $\tau = 5$ bins (250ms).

**Edge Construction**: We employ a hybrid approach combining:

1. **Noise correlation edges**: For neuron pairs $(i,j)$, compute trial-averaged noise correlation:
$$\rho_{ij} = \text{corr}(r_i(t) - \mathbb{E}[r_i(t)|\mathbf{p}(t)], r_j(t) - \mathbb{E}[r_j(t)|\mathbf{p}(t)])$$
where the conditional expectation removes tuning-related activity. Connect neurons if $|\rho_{ij}| > \theta_\rho$ (threshold = 0.3).

2. **Tuning similarity edges**: Compute preferred direction correlation between tuning vectors to capture functional similarity. Connect neurons with correlated tuning (threshold = 0.5).

3. **k-nearest neighbors**: Ensure graph connectivity by adding k=5 nearest neighbors based on feature similarity.

The final adjacency matrix $\mathbf{A} \in \{0,1\}^{N \times N}$ represents the union of these edge sets, where $N$ is the number of neurons.

### 2.3 SE(3)-Equivariant Graph Neural Network Architecture

Our core innovation is designing GNN layers that are equivariant to the special Euclidean group $SE(3)$ representing rotations and translations in 3D space.

**Equivariance Constraint**: For any transformation $g \in SE(3)$ acting on movement kinematics $\mathbf{p} \mapsto g \cdot \mathbf{p} = R\mathbf{p} + \mathbf{t}$, we require the network output to transform accordingly:
$$f_\theta(T_g(\mathbf{H})) = g \cdot f_\theta(\mathbf{H})$$
where $\mathbf{H}$ represents node features and $T_g$ is the induced transformation on neural activity.

**Architecture Design**: We employ a multi-layer equivariant GNN with the following structure:

*Layer 1: Feature Extraction*
Initial node embeddings combine scalar (invariant) and vector (equivariant) features:
$$\mathbf{h}_i = [\mathbf{s}_i, \mathbf{V}_i]$$
where $\mathbf{s}_i \in \mathbb{R}^{d_s}$ are scalar features (firing rates, spectral features) and $\mathbf{V}_i \in \mathbb{R}^{d_v \times 3}$ are vector features (directional tuning coefficients).

*Layers 2-L: Equivariant Message Passing*
At layer $\ell$, each node aggregates information from neighbors via:

$$\mathbf{m}_{ij}^{(\ell)} = \phi_e^{(\ell)}(\mathbf{s}_i^{(\ell)}, \mathbf{s}_j^{(\ell)}, \|\mathbf{r}_{ij}\|, \mathbf{a}_{ij})$$

where $\mathbf{r}_{ij}$ is the relative position vector (if spatial positions are available), $\mathbf{a}_{ij}$ are edge attributes, and $\phi_e^{(\ell)}$ is an MLP producing scalar messages.

Vector features are updated equivariantly:
$$\mathbf{V}_i^{(\ell+1)} = \mathbf{V}_i^{(\ell)} + \sum_{j \in \mathcal{N}(i)} \mathbf{m}_{ij}^{(\ell)} \cdot \frac{\mathbf{r}_{ij}}{\|\mathbf{r}_{ij}\|} \otimes \mathbf{W}_v^{(\ell)}$$

Scalar features are updated using rotationally invariant combinations:
$$\mathbf{s}_i^{(\ell+1)} = \phi_h^{(\ell)}\left(\mathbf{s}_i^{(\ell)}, \sum_{j \in \mathcal{N}(i)} \mathbf{m}_{ij}^{(\ell)}, \|\mathbf{V}_i^{(\ell)}\|^2\right)$$

*Output Layer: Equivariant Decoding*
The final layer produces position and velocity estimates:
$$\hat{\mathbf{p}}(t) = \sum_{i=1}^N \alpha_i \mathbf{V}_i^{(L)}, \quad \hat{\mathbf{v}}(t) = \sum_{i=1}^N \beta_i \mathbf{V}_i^{(L)}$$
where attention weights $\alpha_i, \beta_i$ are computed from scalar features via softmax.

### 2.4 Topological Feature Integration

To capture global manifold structure, we integrate persistent homology features computed from neural population activity.

**Persistence Diagram Computation**:
1. For each trial, construct point cloud $\mathcal{X} = \{\mathbf{r}_1(t), ..., \mathbf{r}_N(t)\}_{t \in [t_{\text{start}}, t_{\text{end}}]}$ in neural state space using dimensionality reduction (PCA to 10D)
2. Compute Vietoris-Rips filtration and extract persistence diagrams $PD_k$ for homology dimensions $k=0,1,2$
3. Convert to persistence landscapes: $\lambda_k(t) = \text{PL}_k(PD_k)$
4. Extract summary statistics: total persistence, number of features, maximum persistence

**Integration with GNN**: Topological features are concatenated with graph-level pooled features:
$$\mathbf{z}_{\text{graph}} = [\text{mean}_i(\mathbf{s}_i^{(L)}), \text{max}_i(\mathbf{s}_i^{(L)}), \boldsymbol{\lambda}_{\text{topo}}]$$

This combined representation is processed through fully connected layers to produce auxiliary outputs (movement phase classification, confidence estimates).

### 2.5 Training Procedure

**Loss Function**: Multi-task loss combining position/velocity reconstruction with auxiliary tasks:
$$\mathcal{L} = \mathcal{L}_{\text{pos}} + \lambda_v \mathcal{L}_{\text{vel}} + \lambda_{\text{phase}} \mathcal{L}_{\text{phase}} + \lambda_{\text{reg}} \mathcal{L}_{\text{reg}}$$

where:
- $\mathcal{L}_{\text{pos}} = \|\hat{\mathbf{p}}(t) - \mathbf{p}(t)\|_2^2$ (position MSE)
- $\mathcal{L}_{\text{vel}} = \|\hat{\mathbf{v}}(t) - \mathbf{v}(t)\|_2^2$ (velocity MSE)
- $\mathcal{L}_{\text{phase}}$ is cross-entropy for movement phase classification
- $\mathcal{L}_{\text{reg}} = \|\mathbf{\Theta}\|_2^2$ regularizes parameters

Hyperparameters: $\lambda_v = 0.5$, $\lambda_{\text{phase}} = 0.1$, $\lambda_{\text{reg}} = 10^{-4}$.

**Optimization**: Adam optimizer with learning rate $10^{-3}$, exponential decay (factor 0.95 every 20 epochs). Training for 200 epochs with early stopping (patience = 30 epochs).

**Data Augmentation via Equivariance**: Exploit SE(3) symmetry by augmenting training data with random rotations/translations of movement trajectories and correspondingly transformed neural responses.

### 2.6 Experimental Design and Validation

**Experiment 1: Decoding Accuracy**
- **Setup**: Standard train/test split (80/20) within single sessions
- **Baselines**: Wiener filter, Kalman filter, feedforward DNN, standard GNN
- **Metrics**: $R^2$, mean absolute error (MAE), correlation coefficient for each spatial dimension
- **Hypothesis**: SE(3)-equivariant GNN achieves 20-30% improvement in $R^2$

**Experiment 2: Generalization to Novel Directions**
- **Setup**: Train on movements to 6 cardinal directions, test on 18 intermediate directions
- **Analysis**: Compare angular error between predicted and actual movement direction
- **Hypothesis**: Equivariant architecture generalizes better due to learned symmetries

**Experiment 3: Cross-Session Generalization**
- **Setup**: Train on day 1, test on days 2-5 with minimal fine-tuning
- **Analysis**: Track degradation in performance over days; compare with/without topological features
- **Hypothesis**: Topological features capture stable manifold structure improving generalization

**Experiment 4: Ablation Studies**
- Remove equivariance constraints (compare to standard GNN)
- Remove topological features
- Vary graph construction methods
- Analyze contribution of each component

**Experiment 5: Interpretability Analysis**
- **Feature Visualization**: Project learned node embeddings to 2D/3D; analyze clustering by tuning properties
- **Attention Analysis**: Visualize attention weights $\alpha_i$ to identify important neurons for different movement phases
- **Symmetry Verification**: Numerically verify equivariance by comparing $f_\theta(T_g(\mathbf{H}))$ and $g \cdot f_\theta(\mathbf{H})$ for sampled transformations
- **Geometric Features**: Extract and visualize learned vector features $\mathbf{V}_i$; test if they align with preferred directions

### 2.7 Computational Implementation

**Software Framework**: PyTorch Geometric for graph operations, e3nn library for equivariant neural network layers, Gudhi/Ripser for persistent homology computation.

**Hardware Requirements**: Training on NVIDIA A100 GPU (40GB memory), estimated 6-10 hours per full training run.

**Reproducibility**: All code, hyperparameters, and random seeds will be version-controlled and publicly released. Preprocessing pipelines will be documented with example notebooks.

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Quantitative Performance Gains**: We anticipate our SE(3)-equivariant GNN framework will achieve:
- **20-30% improvement** in position decoding $R^2$ compared to Kalman filter baselines (from ~0.75 to ~0.90-0.95)
- **15-25% reduction** in angular error when generalizing to novel movement directions
- **Sustained performance** across days with <10% degradation in cross-session experiments
- **Superior sample efficiency**, requiring 30-40% fewer training trials to achieve equivalent performance

**Interpretable Geometric Representations**: The model will extract:
- **Learned vector features** $\mathbf{V}_i$ that align with neurons' preferred directions, demonstrating the model discovers tuning properties
- **Attention patterns** revealing functional subnetworks activated during different movement phases
- **Topological signatures** characterizing the geometry of neural manifolds (e.g., ring topology during rotational movements)

**Validated Equivariance**: Numerical experiments will confirm:
- **Preservation of SE(3) symmetries** with equivariance error $<10^{-4}$
- **Learned invariant features** that remain stable under workspace transformations
- **Factorized representations** separating movement direction from speed/position

### Scientific Impact

**Neuroscience Insights**: This research will provide evidence that:
1. Motor cortex representations implement approximate equivariance to movement symmetries
2. Functional connectivity patterns reflect geometric task structure
3. Topological manifold features capture behaviorally relevant information across temporal scales
4. Biological neural circuits may employ computational strategies analogous to geometric deep learning

These findings contribute to the emerging paradigm that symmetry and geometry are fundamental organizing principles for neural representations across brain regions.

**Theoretical Contributions**: Our work advances understanding of:
- How discrete graph structure (connectivity) interfaces with continuous geometric symmetries
- The role of topological constraints in shaping neural population dynamics
- Connections between equivariant representation learning and neural coding principles

**Methodological Innovations**: The framework provides:
- General-purpose tools for constructing task-relevant neural graphs
- Techniques for integrating persistent homology with deep learning
- Benchmark comparisons for equivariant vs. standard architectures on neural data

### Practical Impact

**Brain-Machine Interfaces**: Improved decoding accuracy and generalization directly benefit:
- Clinical BMI systems for paralyzed patients, reducing calibration time
- Robotic prosthetics requiring accurate real-time motor control
- Closed-loop neuroscience experiments requiring precise decoding

**Broader Applications**: The methodology extends to:
- Decoding spatial navigation from hippocampal recordings (exploiting toroidal grid cell geometry)
- Analyzing sensory representations in visual/auditory cortex
- Understanding cognitive representations in prefrontal cortex

### Future Directions

This work opens avenues for:
1. **Extending to other symmetry groups**: E(3) for full Euclidean group, SO(3) for rotational tasks, cyclic groups for rhythmic movements
2. **Online learning and adaptation**: Developing equivariant meta-learning approaches for rapid BMI calibration
3. **Causal interventions**: Using the framework to design closed-loop experiments testing geometric coding hypotheses
4. **Cross-species validation**: Applying the methods to rodent motor cortex, comparing geometric principles across species

### Broader Significance

This research exemplifies the productive convergence of neuroscience and machine learning. By demonstrating that geometric deep learning principles—developed independently for artificial systems—improve our understanding and decoding of biological neural circuits, we provide evidence for substrate-agnostic computational principles. Just as symmetry and geometry unified 20th-century physics, this work contributes to a unified framework for information processing in both biological and artificial neural systems.

The explicit connection between equivariant neural networks and motor cortex function may inspire new architectures in machine learning (e.g., bio-inspired designs for robotic control) while simultaneously providing neuroscience with powerful analytical tools. This bidirectional exchange between fields exemplifies the vision of the NeurReps workshop: illuminating deep principles of neural representation through the lens of mathematical structure.

---

**Word Count**: ~2000 words