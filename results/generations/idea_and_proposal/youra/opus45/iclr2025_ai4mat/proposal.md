# Research Proposal: Hierarchical Local Environment Encoding with Adversarial Domain Alignment for Cross-Material-Type Transfer in Materials Foundation Models

## 1. Introduction

### 1.1 Background

The intersection of artificial intelligence and materials science has emerged as one of the most promising frontiers for accelerating scientific discovery. Foundation models, which have revolutionized natural language processing and computer vision through their ability to learn transferable representations from large-scale data, are now being adapted for materials science applications. However, a fundamental challenge persists: current materials foundation models trained predominantly on crystalline structures exhibit catastrophic performance degradation—often exceeding 50% accuracy loss—when applied to amorphous materials, surfaces, and other non-periodic systems.

This limitation represents a critical barrier to real-world deployment of AI-driven materials discovery. Practical applications in catalysis, battery materials, and semiconductor manufacturing frequently involve amorphous phases, grain boundaries, and surface phenomena that cannot be adequately modeled by systems trained exclusively on periodic crystalline data. The Materials Project database, while containing approximately 150,000 crystalline structures with computed properties, represents only a fraction of the materials space relevant to technological applications.

The core scientific insight motivating this research is that local atomic coordination chemistry follows universal physical principles across material types. The bonding environment around a silicon atom, for instance, obeys the same quantum mechanical rules whether that atom resides in crystalline silicon, amorphous silica, or at a silicon surface. However, existing graph neural network (GNN) architectures for materials property prediction conflate these transferable local features with domain-specific global features such as periodicity and long-range order, preventing effective knowledge transfer across material type boundaries.

### 1.2 Research Objectives

This research proposes HLEE (Hierarchical Local Environment Encoding), a novel architecture designed to enable cross-material-type transfer in materials foundation models. The primary objectives are:

1. **Develop a hierarchical architecture** that explicitly separates local atomic environment features from global structural features, enabling selective transfer of physics-invariant local representations.

2. **Implement adversarial domain alignment** at the local environment level using gradient reversal layers, extracting domain-invariant representations that transfer across material type boundaries.

3. **Validate cross-domain generalization** by pre-training on Materials Project crystalline data and evaluating transfer to JARVIS amorphous and surface materials, demonstrating <15% cross-domain degradation compared to >50% for baseline methods.

4. **Demonstrate sample efficiency** by showing that HLEE with 100 target domain samples matches baseline performance requiring 1000+ samples.

### 1.3 Significance

This research addresses a fundamental limitation identified in the AI4Mat workshop themes: the need for foundation models that generalize across diverse material types and the challenge of developing next-generation representations for complex materials systems. Success would enable:

- **Broader applicability** of materials foundation models to real-world problems involving non-crystalline materials
- **Reduced data requirements** for new material types through efficient transfer learning
- **Accelerated discovery** in domains where experimental data is scarce but crystalline training data is abundant
- **Theoretical insights** into the transferability of local versus global features in materials representations

## 2. Methodology

### 2.1 Architecture Design

#### 2.1.1 Hierarchical Local Environment Encoding

The HLEE architecture consists of three main components: a local environment encoder, a global structure encoder, and an adversarial domain discriminator.

**Local Environment Encoder:** For each atom $i$ in a material structure, we define the local environment $\mathcal{N}_i$ as the set of atoms within a cutoff radius $r_c = 6.0$ Å. The local environment is encoded using equivariant message passing:

$$\mathbf{h}_i^{(l+1)} = \mathbf{h}_i^{(l)} + \sum_{j \in \mathcal{N}_i} \phi_m\left(\mathbf{h}_i^{(l)}, \mathbf{h}_j^{(l)}, \mathbf{e}_{ij}\right)$$

where $\mathbf{h}_i^{(l)}$ is the hidden representation of atom $i$ at layer $l$, $\mathbf{e}_{ij}$ encodes the edge features including distance and angular information, and $\phi_m$ is a learnable message function implemented as an equivariant neural network preserving E(3) symmetry.

The edge features incorporate both radial and angular components:

$$\mathbf{e}_{ij} = \left[\text{RBF}(r_{ij}), Y_l^m(\hat{\mathbf{r}}_{ij})\right]$$

where $\text{RBF}(r_{ij})$ represents radial basis functions and $Y_l^m(\hat{\mathbf{r}}_{ij})$ are spherical harmonics encoding angular information.

**Global Structure Encoder:** The global encoder aggregates local representations while capturing long-range structural features:

$$\mathbf{g} = \text{Attention}\left(\frac{1}{N}\sum_{i=1}^{N} \mathbf{h}_i^{(L)}, \{\mathbf{h}_i^{(L)}\}_{i=1}^{N}\right)$$

This attention-based pooling allows the model to weight contributions from different local environments based on their relevance to global properties.

**Hierarchical Separation:** The key innovation is the explicit separation of local and global feature streams:

$$\mathbf{z}_{\text{local}} = f_{\text{local}}(\{\mathbf{h}_i^{(L)}\}_{i=1}^{N})$$
$$\mathbf{z}_{\text{global}} = f_{\text{global}}(\mathbf{g}, \mathbf{z}_{\text{local}})$$

where $f_{\text{local}}$ and $f_{\text{global}}$ are separate neural network heads.

#### 2.1.2 Adversarial Domain Alignment

To extract domain-invariant local representations, we employ adversarial training with gradient reversal. A domain discriminator $D$ attempts to classify whether local environment features originate from crystalline or amorphous/surface materials:

$$\mathcal{L}_{\text{domain}} = -\mathbb{E}_{x \sim \mathcal{D}_s}[\log D(\mathbf{z}_{\text{local}})] - \mathbb{E}_{x \sim \mathcal{D}_t}[\log(1 - D(\mathbf{z}_{\text{local}}))]$$

where $\mathcal{D}_s$ and $\mathcal{D}_t$ represent source (crystalline) and target (amorphous/surface) domains.

The gradient reversal layer (GRL) inverts gradients during backpropagation:

$$\text{GRL}(\mathbf{z}) = \mathbf{z} \quad \text{(forward)}$$
$$\frac{\partial \text{GRL}}{\partial \mathbf{z}} = -\lambda \mathbf{I} \quad \text{(backward)}$$

where $\lambda$ is the gradient reversal weight, scheduled as:

$$\lambda(p) = \frac{2}{1 + \exp(-\gamma p)} - 1$$

with $p$ representing training progress and $\gamma = 10$.

**Total Training Objective:**

$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{property}} + \alpha \mathcal{L}_{\text{domain}} + \beta \mathcal{L}_{\text{GP}}$$

where $\mathcal{L}_{\text{property}}$ is the property prediction loss (MAE for formation energy and forces), $\mathcal{L}_{\text{GP}}$ is a gradient penalty for training stability, and $\alpha, \beta$ are hyperparameters.

### 2.2 Data Collection and Preprocessing

**Source Domain (Crystalline):** We utilize the Materials Project database containing approximately 150,000 crystalline structures with DFT-computed formation energies and atomic forces. Data preprocessing includes:
- Filtering structures with formation energy within [-5, 5] eV/atom
- Removing structures with atomic forces exceeding 10 eV/Å
- Standardizing cell representations to primitive cells

**Target Domain (Amorphous/Surface):** The JARVIS database provides amorphous and surface material structures. We extract:
- Amorphous structures generated via melt-quench molecular dynamics
- Surface slabs with various Miller indices and terminations
- Target dataset size: >1,000 structures for validation

**Data Splits:** 80/10/10 train/validation/test splits for source domain; 100/200/700 splits for target domain to evaluate few-shot transfer.

### 2.3 Experimental Design

#### 2.3.1 Baseline Methods

1. **MatGL:** State-of-the-art materials GNN without domain adaptation
2. **NequIP:** Equivariant neural network potential without hierarchical separation
3. **HLEE-lite:** Ablated version without adversarial training (hierarchical encoding only)
4. **Fine-tuned baselines:** MatGL and NequIP with standard fine-tuning on target domain

#### 2.3.2 Evaluation Metrics

**Primary Metrics:**
- Formation energy MAE (eV/atom)
- Force MAE (eV/Å)
- Cross-domain degradation: $\delta = \frac{\text{MAE}_{\text{target}} - \text{MAE}_{\text{source}}}{\text{MAE}_{\text{source}}} \times 100\%$

**Secondary Metrics:**
- Transfer efficiency: Performance gain per fine-tuning sample
- Training convergence: Epochs to reach 90% of final performance
- Domain discriminator accuracy: Measure of feature alignment

#### 2.3.3 Experimental Protocol

**Experiment 1: Cross-Domain Generalization**
- Pre-train all models on Materials Project crystalline data (500 epochs)
- Evaluate directly on JARVIS amorphous/surface test set (zero-shot)
- Measure cross-domain degradation for each method

**Experiment 2: Few-Shot Transfer**
- Fine-tune pre-trained models with varying target domain samples: {10, 50, 100, 500, 1000}
- Plot learning curves comparing sample efficiency
- Test hypothesis that HLEE with 100 samples matches baselines with 1000+ samples

**Experiment 3: Ablation Studies**
- Compare HLEE-full vs HLEE-lite to isolate adversarial contribution
- Vary gradient reversal weight $\lambda \in \{0.1, 0.3, 0.5, 0.7, 1.0\}$
- Test different cutoff radii $r_c \in \{4.0, 5.0, 6.0, 7.0\}$ Å

**Experiment 4: Mechanism Verification**
- Visualize learned representations using t-SNE
- Analyze domain discriminator confusion matrix
- Compute feature similarity between crystalline and amorphous local environments

#### 2.3.4 Statistical Analysis

- Minimum 20 independent runs per condition with different random seeds
- Report mean ± standard deviation and 95% confidence intervals
- Two-sample t-tests with $\alpha = 0.05$ for hypothesis testing
- Effect size reporting using Cohen's d

### 2.4 Implementation Details

**Model Architecture:**
- Local encoder: 4 message passing layers, 128 hidden dimensions
- Global encoder: 2 attention layers, 256 hidden dimensions
- Domain discriminator: 3-layer MLP with 256 hidden units
- Total parameters: ~1M

**Training Configuration:**
- Optimizer: Adam with learning rate $10^{-3}$
- Learning rate schedule: Cosine annealing with warm restarts
- Batch size: 32 structures
- Training epochs: 500 (source), 100 (fine-tuning)
- Hardware: 4× NVIDIA A100 GPUs

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Prediction (P1):** HLEE will achieve cross-domain degradation below 15% when transferring from crystalline to amorphous/surface materials, compared to >50% degradation for baseline GNNs. Specifically, we expect:
- HLEE formation energy MAE: 0.03-0.05 eV/atom on target domain
- Baseline formation energy MAE: 0.08-0.15 eV/atom on target domain

**Secondary Prediction (P2):** HLEE with 100 target domain samples will match or exceed baseline performance with 1000+ samples, representing a 10× improvement in sample efficiency.

**Secondary Prediction (P3):** HLEE-full will outperform HLEE-lite by >10% on cross-domain metrics, confirming the essential contribution of adversarial domain alignment.

### 3.2 Falsification Criteria

The hypothesis will be considered falsified if:
1. Cross-domain degradation exceeds 25% for HLEE
2. HLEE-lite matches HLEE-full performance (adversarial training provides no benefit)
3. Standard fine-tuning matches HLEE sample efficiency
4. Adversarial training fails to converge within 500 epochs

### 3.3 Scientific Impact

This research will provide:

1. **Theoretical Contribution:** Empirical validation of the hypothesis that local atomic environment features are transferable across material types, with quantitative bounds on transferability.

2. **Methodological Contribution:** A novel architecture combining hierarchical feature separation with adversarial domain alignment, applicable beyond materials science to other scientific domains with similar local-global feature structures.

3. **Practical Contribution:** A pre-trained model capable of generalizing to new material types with minimal fine-tuning data, directly addressing the data scarcity challenge in materials discovery.

### 3.4 Broader Impact

Success in this research would:

- **Enable foundation models for materials science** that truly generalize across the diverse material types encountered in real-world applications
- **Accelerate discovery** in technologically critical areas including catalysis, energy storage, and semiconductor manufacturing
- **Reduce computational costs** by enabling transfer from abundant crystalline data to scarce amorphous/surface data
- **Inform future architecture design** for scientific foundation models by demonstrating the importance of physics-informed feature hierarchies

### 3.5 Limitations and Future Work

Acknowledged limitations include:
- Scope limited to local properties (formation energy, forces); extension to band gap and conductivity requires additional mechanisms
- Adversarial training hyperparameter sensitivity may require careful tuning for new material systems
- Extreme out-of-distribution generalization (e.g., to entirely new element combinations) is not guaranteed

Future work will explore:
- Extension to electronic properties through multi-task learning
- Integration with active learning for efficient experimental validation
- Scaling to larger foundation models with billions of parameters

This research directly addresses the AI4Mat workshop themes of building foundation models for materials science and developing next-generation materials representations, with potential for significant impact on the field of AI-driven materials discovery.