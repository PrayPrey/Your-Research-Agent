# Research Proposal: PhysTac: Physics-Informed Disentangled Representations for Cross-Sensor Tactile Transfer

## 1. Introduction

### 1.1 Background

Touch sensing represents a fundamental modality for both biological and artificial systems to perceive and interact with the physical world. Recent advances in vision-based tactile sensors—including GelSight, DIGIT, TacTip, and 9DTact—have dramatically expanded the accessibility of high-resolution tactile perception for robotic manipulation. These sensors capture contact information through optical imaging of elastomer deformation, producing rich visual data that encodes contact geometry, force distributions, and surface properties. The proliferation of such sensors has catalyzed a new era of computational research dedicated to tactile processing, with applications spanning agricultural robotics, telemedicine, prosthetics, and augmented reality systems.

Despite this progress, a critical bottleneck impedes the widespread deployment of tactile intelligence: the lack of transferability across sensor types. Each vision-based tactile sensor produces visually distinct outputs due to differences in optical design, elastomer properties, illumination configurations, and marker patterns. A GelSight sensor's output appears fundamentally different from a DIGIT or TacTip image, even when sensing identical physical contact phenomena. This heterogeneity forces practitioners to collect extensive labeled datasets and retrain models for each new sensor deployment—a process that is costly, time-consuming, and fundamentally limits scalability.

Current approaches to cross-sensor transfer, including T3 (Transferable Tactile Transformers) and AnyTouch, rely primarily on data-driven alignment strategies. These methods learn shared representations through large-scale multi-sensor pre-training, requiring substantial labeled data from each sensor type. While effective when abundant data is available, they struggle in low-data regimes and offer limited theoretical guarantees about what features transfer across sensors. The fundamental insight motivating our work is that contact mechanics is inherently sensor-agnostic: when two different sensors press against the same object with identical force, the underlying physical deformation follows the same mechanical principles. Only the optical encoding of this deformation differs across sensors.

### 1.2 Research Objectives

This research proposes PhysTac, a physics-informed disentangled representation learning framework that explicitly separates sensor-agnostic contact physics from sensor-specific appearance characteristics. Our primary objectives are:

1. **Develop a dual-branch architecture** that disentangles physics-invariant contact features (deformation fields, force distributions) from sensor-specific optical features through Finite Element Method (FEM) supervision and disentanglement regularization.

2. **Demonstrate superior zero-shot transfer** to unseen sensors, achieving >10% improvement over state-of-the-art data-driven baselines on standardized benchmarks.

3. **Enable sample-efficient adaptation** to novel sensors, requiring <10× fewer labeled samples compared to existing methods to achieve equivalent performance.

4. **Validate the causal mechanism** linking physics-grounded representations to improved transferability through systematic ablation studies and probing analyses.

### 1.3 Significance

This research addresses a fundamental challenge in tactile AI: how to build representations that capture the invariant physical structure of touch rather than the variable optical encoding. By grounding representations in contact mechanics, PhysTac offers several significant contributions:

**Theoretical Contribution:** We establish a principled framework for understanding cross-sensor transfer through the lens of physics-appearance disentanglement, providing theoretical grounding for why certain features should transfer while others should not.

**Practical Impact:** PhysTac enables rapid deployment of tactile intelligence on novel sensor hardware with minimal data collection, dramatically reducing the barrier to entry for new tactile applications and custom sensor designs.

**Scientific Foundation:** By demonstrating that physics-informed supervision improves representation quality, we contribute to the broader understanding of how domain knowledge can be integrated into deep learning for tactile processing.

## 2. Methodology

### 2.1 Problem Formulation

Let $\mathcal{S} = \{s_1, s_2, ..., s_K\}$ denote a set of $K$ vision-based tactile sensor types. For each sensor $s_k$, we observe tactile images $x^{(k)} \in \mathbb{R}^{H \times W \times 3}$ that encode underlying physical contact states $\phi \in \Phi$, where $\Phi$ represents the space of contact configurations (geometry, forces, contact masks). The key insight is that the mapping from physical state to observation can be decomposed as:

$$x^{(k)} = g_k(\phi) + \epsilon_k$$

where $g_k: \Phi \rightarrow \mathbb{R}^{H \times W \times 3}$ is a sensor-specific rendering function and $\epsilon_k$ represents sensor noise. Our goal is to learn an encoder $f_\theta$ that extracts physics-invariant representations $z_\phi = f_\theta(x^{(k)})$ such that $z_\phi$ depends only on $\phi$ and not on the sensor identity $k$.

### 2.2 PhysTac Architecture

PhysTac employs a dual-branch architecture with shared early layers and specialized branches for physics and appearance features.

**Shared Backbone:** We utilize a Vision Transformer (ViT-B/16) as the shared backbone encoder, processing input tactile images into patch embeddings:

$$h = \text{ViT-Backbone}(x) \in \mathbb{R}^{N \times D}$$

where $N$ is the number of patches and $D$ is the embedding dimension.

**Physics Branch ($f_\phi$):** The physics branch processes shared features to extract contact geometry representations:

$$z_\phi = f_\phi(h) = \text{MLP}_\phi(\text{Attention}_\phi(h)) \in \mathbb{R}^{d_\phi}$$

This branch is supervised by FEM-derived physics labels to ensure representations capture true contact mechanics.

**Appearance Branch ($f_a$):** The appearance branch captures sensor-specific optical characteristics:

$$z_a = f_a(h) = \text{MLP}_a(\text{Attention}_a(h)) \in \mathbb{R}^{d_a}$$

This branch enables reconstruction of sensor-specific visual features while being explicitly decorrelated from physics features.

### 2.3 Training Objectives

The total training objective combines four loss components:

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{physics}} + \lambda_1 \mathcal{L}_{\text{recon}} + \lambda_2 \mathcal{L}_{\text{GRL}} + \lambda_3 \mathcal{L}_{\text{MI}}$$

**Physics Supervision Loss ($\mathcal{L}_{\text{physics}}$):** We supervise the physics branch using FEM-derived labels. Given ground-truth deformation field $D^* \in \mathbb{R}^{H \times W \times 3}$ and normal force $F^* \in \mathbb{R}$:

$$\mathcal{L}_{\text{physics}} = \|D_\theta(z_\phi) - D^*\|_2^2 + \alpha \|F_\theta(z_\phi) - F^*\|_1$$

where $D_\theta$ and $F_\theta$ are decoder heads predicting deformation fields and forces respectively.

**Reconstruction Loss ($\mathcal{L}_{\text{recon}}$):** The appearance branch is trained to reconstruct sensor-specific visual features:

$$\mathcal{L}_{\text{recon}} = \|R_\theta(z_a, z_\phi) - x\|_2^2$$

where $R_\theta$ is a decoder that combines both branches for reconstruction.

**Gradient Reversal Loss ($\mathcal{L}_{\text{GRL}}$):** To enforce that physics features are sensor-agnostic, we apply gradient reversal for sensor classification:

$$\mathcal{L}_{\text{GRL}} = -\sum_{k=1}^{K} y_k \log(\text{SensorClassifier}(\text{GRL}(z_\phi)))$$

The gradient reversal layer (GRL) multiplies gradients by $-\gamma$ during backpropagation, encouraging $z_\phi$ to be uninformative about sensor identity.

**Mutual Information Minimization ($\mathcal{L}_{\text{MI}}$):** We minimize mutual information between physics and appearance features using a variational bound:

$$\mathcal{L}_{\text{MI}} = \mathbb{E}_{p(z_\phi, z_a)}[\log q_\psi(z_\phi | z_a)] - \mathbb{E}_{p(z_\phi)}[\log q_\psi(z_\phi)]$$

where $q_\psi$ is a variational approximation. In practice, we implement this using the CLUB (Contrastive Log-ratio Upper Bound) estimator.

### 2.4 FEM-Based Physics Label Generation

We generate physics supervision labels using Finite Element Method simulation following the TensorTouch methodology:

1. **Mesh Generation:** Create tetrahedral meshes of sensor elastomers with material properties (Young's modulus $E$, Poisson's ratio $\nu$) calibrated to each sensor type.

2. **Contact Simulation:** For each tactile image, simulate the corresponding contact scenario using known object geometry and estimated contact pose.

3. **Deformation Field Extraction:** Extract nodal displacements $\mathbf{u}$ by solving:

$$\mathbf{K}\mathbf{u} = \mathbf{f}$$

where $\mathbf{K}$ is the stiffness matrix and $\mathbf{f}$ is the applied force vector.

4. **Force Distribution Computation:** Compute stress tensor $\boldsymbol{\sigma}$ and derive normal/shear force components at the contact interface.

5. **Domain Randomization:** Apply randomization to material properties ($E \pm 20\%$, $\nu \pm 10\%$) and contact parameters to improve simulation-to-real transfer.

### 2.5 Physics-Informed Contrastive Learning

Beyond supervised physics prediction, we incorporate contrastive learning where positive pairs are defined by physical similarity rather than visual similarity:

$$\mathcal{L}_{\text{contrast}} = -\log \frac{\exp(\text{sim}(z_\phi^i, z_\phi^j) / \tau)}{\sum_{k \neq i} \exp(\text{sim}(z_\phi^i, z_\phi^k) / \tau)}$$

where samples $i$ and $j$ are positive pairs if they share similar physics labels (deformation field cosine similarity > 0.9), regardless of sensor type. This encourages the physics branch to cluster representations by physical contact properties rather than sensor appearance.

### 2.6 Data Collection and Datasets

**Pre-training Dataset:** We utilize the FoTa (Foundation for Tactile) dataset containing 3M+ tactile samples across multiple sensor types (GelSight, DIGIT, TacTip, 9DTact). We augment this with FEM-derived physics labels generated using the pipeline described above.

**Evaluation Benchmark:** We evaluate on TacBench, a standardized benchmark comprising six tasks:
- Grasp stability prediction
- Slip detection
- Texture classification
- Object pose estimation
- Force estimation
- Contact localization

**Held-out Sensors:** To evaluate zero-shot transfer, we designate one sensor type (rotating across experiments) as completely held-out during pre-training.

### 2.7 Experimental Design

**Experiment 1: Zero-Shot Transfer Evaluation**
- **Design:** Train PhysTac on $K-1$ sensors, evaluate on held-out sensor
- **Baselines:** T3, AnyTouch, Sparsh, single-sensor training
- **Metrics:** TacBench aggregate accuracy, per-task accuracy
- **Statistical Test:** Independent t-test with Bonferroni correction ($\alpha = 0.017$)

**Experiment 2: Few-Shot Adaptation**
- **Design:** Vary target sensor samples $n \in \{0, 10, 50, 100, 500, 1000\}$
- **Metric:** Samples required to match T3-1000 baseline performance
- **Analysis:** Learning curve analysis with confidence intervals

**Experiment 3: Physics Supervision Ablation**
- **Conditions:** (a) Full deformation field, (b) Contact mask + force only, (c) No physics supervision
- **Metric:** Zero-shot transfer accuracy, force estimation MAE
- **Statistical Test:** One-way ANOVA with Tukey HSD post-hoc

**Experiment 4: Disentanglement Verification**
- **Probing Task:** Train linear classifier to predict sensor identity from $z_\phi$
- **Expected Result:** Chance-level accuracy (1/K) if disentanglement succeeds
- **Metric:** Sensor classification accuracy from physics vs. appearance branches

### 2.8 Evaluation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Zero-Shot Accuracy | TacBench accuracy on held-out sensor | >71.5% (vs T3 ~65%) |
| Few-Shot Efficiency | Samples to match T3-1000 | ≤100 samples |
| Force MAE | Mean Absolute Error on force prediction | ≥15% improvement over Sparsh |
| Disentanglement Score | Sensor classification accuracy from $z_\phi$ | ≤ chance + 5% |

### 2.9 Implementation Details

- **Backbone:** ViT-B/16 initialized from ImageNet pre-training
- **Physics/Appearance branch dimensions:** $d_\phi = d_a = 256$
- **Training:** AdamW optimizer, learning rate $1 \times 10^{-4}$, batch size 256
- **Loss weights:** $\lambda_1 = 1.0$, $\lambda_2 = 0.5$, $\lambda_3 = 0.1$
- **GRL strength:** $\gamma = 1.0$ (annealed from 0 during first 10 epochs)
- **Hardware:** 8× NVIDIA A100 GPUs, ~48 hours pre-training

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1):** We expect PhysTac to achieve >71.5% zero-shot transfer accuracy on TacBench (compared to T3 baseline of ~65%), representing a >10% relative improvement. This improvement should be consistent across held-out sensor types, demonstrating that physics-grounded representations generalize better than appearance-based features.

**Secondary Outcome (P2):** PhysTac should require ≤100 labeled samples from a new sensor to match the performance of T3 trained with 1000 samples, demonstrating 10× sample efficiency improvement. This dramatically reduces the data collection burden for deploying tactile systems on novel hardware.

**Tertiary Outcome (P3):** The physics branch should achieve ≥15% lower Mean Absolute Error on force estimation compared to appearance-only baselines (Sparsh), validating that FEM supervision successfully grounds representations in physical contact properties.

**Mechanistic Validation:** Probing experiments should confirm successful disentanglement: sensor classification from physics features should be at chance level (±5%), while appearance features should enable accurate sensor identification (>90%).

### 3.2 Potential Failure Modes and Mitigations

1. **FEM Simulation Gap:** If simulation-to-real domain gap undermines physics label quality, we will increase domain randomization and explore learned simulation calibration.

2. **Disentanglement Collapse:** If branches fail to separate, we will increase MI regularization strength and explore alternative disentanglement objectives (e.g., β-VAE formulation).

3. **Limited Sensor Diversity:** If FoTa dataset lacks sufficient sensor diversity, we will augment with synthetic sensor variations through optical simulation.

### 3.3 Broader Impact

**Scientific Impact:** PhysTac establishes a new paradigm for tactile representation learning grounded in physical principles rather than visual statistics. This contributes to the broader goal of building AI systems that understand the physical world, not just its visual appearance.

**Practical Impact:** By enabling rapid deployment on novel sensors with minimal data, PhysTac lowers the barrier to entry for tactile AI applications. This is particularly valuable for:
- Custom sensor designs optimized for specific applications
- Low-resource settings where extensive data collection is infeasible
- Rapid prototyping of tactile manipulation systems

**Community Impact:** We will release pre-trained PhysTac models, FEM simulation pipelines, and physics label datasets to accelerate research in tactile processing. This aligns with the workshop's goal of lowering entry barriers for AI researchers exploring touch sensing.

### 3.4 Limitations and Future Work

PhysTac is designed for vision-based optical tactile sensors with elastomer-based deformation sensing. Extension to non-optical modalities (resistive, capacitive, piezoelectric) would require different physics formulations. Future work could explore unified physics representations spanning multiple sensing modalities, as well as integration with language models for tactile-language grounding.

In conclusion, PhysTac represents a principled approach to cross-sensor tactile transfer that leverages the fundamental insight that contact physics is sensor-agnostic. By disentangling physics from appearance through FEM supervision and regularization, we expect to achieve substantial improvements in both zero-shot transfer and sample efficiency, advancing the foundations of computational touch processing.