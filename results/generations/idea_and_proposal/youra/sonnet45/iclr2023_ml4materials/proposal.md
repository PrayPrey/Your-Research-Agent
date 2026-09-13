# Research Proposal: Compositional Material Embeddings with Adaptive Periodic Graphs for Unified Cross-Class Transfer Learning in Materials Discovery

## 1. Introduction

### 1.1 Background

Materials discovery represents one of the most critical bottlenecks in addressing global challenges such as renewable energy, energy storage, and clean water access. The development of new materials—from advanced battery electrodes to efficient catalysts and high-performance polymers—requires navigating vast chemical spaces that are prohibitively expensive to explore through traditional experimental and computational methods. A single density functional theory (DFT) calculation can require hours to days of computational time, and discovering a new material class typically demands thousands of such calculations, translating to hundreds of thousands of CPU-hours and months of researcher effort.

Machine learning (ML) has revolutionized molecular and protein modeling, enabling breakthroughs such as AlphaFold's protein structure prediction and the discovery of novel antibiotics. Geometric deep learning methods, particularly equivariant graph neural networks, have shown tremendous promise in modeling atomic structures by respecting fundamental physical symmetries. However, materials science presents unique challenges that distinguish it from biomolecular modeling:

**Challenge 1: Diverse Structural Representations.** Unlike molecules (represented as 2D graphs) or proteins (represented as sequences), materials span fundamentally different structural classes. Inorganic crystals require periodic boundary conditions with infinite lattice repetition; polymers exist as semi-periodic chain structures; catalytic surfaces demand slab geometries with vacuum regions. Current ML approaches treat each class separately, requiring bespoke architectures and extensive datasets for each material type.

**Challenge 2: Data Fragmentation and Scarcity.** While crystalline materials benefit from large databases like the Materials Project (~150,000 structures), emerging classes like functional polymers or novel catalysts have limited data availability. For instance, polymer property databases contain only 1,000-10,000 well-characterized structures—insufficient for training deep learning models from scratch. This data imbalance prevents the materials community from leveraging knowledge across the 100,000+ known crystals to accelerate discovery in data-scarce domains.

**Challenge 3: Physical Transferability Remains Unexplored.** Despite sharing fundamental physics—quantum mechanics governs all materials—no existing framework exploits the transferability of atomic environments across structural classes. A carbon atom in sp³ hybridization contributes similarly to bonding whether in diamond (crystal), polyethylene (polymer), or a diamond surface (catalyst substrate), yet current models cannot transfer this knowledge across classes.

### 1.2 Research Gap

The literature reveals a critical gap: **no unified ML framework exists for cross-class materials modeling**. State-of-the-art models like Matformer (crystals), CHGNet (universal potentials for crystals), and polymer-specific QSPR methods operate in isolation. Recent work on out-of-distribution (OOD) generalization (Omee et al., Nature Communications 2024) addresses compositional shifts within crystals but does not tackle class-level transfer. Multi-modal contrastive learning (e.g., CLIP for vision-language) and transfer learning (e.g., BERT for NLP) have demonstrated the power of unified representations across domains, yet these paradigms remain unexplored for materials with their unique physical constraints.

### 1.3 Research Objectives

This research proposes **CoME-APG+ (Compositional Material Embeddings with Adaptive Periodic Graphs)**, a unified framework that enables cross-class transfer learning in materials discovery. Our central hypothesis is:

> **Atomic environments are transferable across material classes**: Materials with similar local atomic environments (measured by SOAP descriptor similarity >0.9) exhibit correlated property contributions (Pearson r > 0.7) regardless of global structure class, enabling pre-training on data-rich crystals to achieve ≥70% of full-data performance on data-scarce polymers using only 10% of typical training data.

**Specific Objectives:**

1. **Develop Adaptive Periodic Graphs (APG)**: Create a unified graph construction framework that handles crystals (3D periodic), polymers (1D periodic), and surfaces (2D periodic) within a single message-passing architecture.

2. **Design Physics-Informed Hierarchical Contrastive Alignment (PIHCA)**: Implement a three-level contrastive learning scheme (composition → electronics → geometry) that aligns embeddings across material classes using domain knowledge.

3. **Validate Compositional Transferability**: Empirically demonstrate that atomic environment similarity predicts property correlation across classes through systematic correlation studies.

4. **Achieve Data-Efficient Transfer Learning**: Show that pre-training on 100,000 crystals enables polymer property prediction with 1,000 structures (vs. 7,000 typically required), saving ~600,000 CPU-hours per new material class.

5. **Enable Mixed-Class System Prediction**: Extend the framework to heterogeneous materials like polymer nanocomposites and supported catalysts.

### 1.4 Significance

**Scientific Impact:** This research establishes the theoretical foundation for "structural dialects" in materials—the concept that material classes share atomic "vocabulary" but differ in physical "grammar." It extends equivariance theory to multi-class hierarchical symmetry groups and connects thermochemical bond additivity principles to modern transfer learning.

**Practical Impact:** CoME-APG+ addresses the data bottleneck in materials discovery by enabling 7× data reduction for new material classes. This translates to:
- Accelerating polymer discovery from months to weeks
- Reducing computational costs by ~600,000 CPU-hours per new dataset
- Enabling rapid adaptation to emerging classes (2-3 days for architecture definition vs. 1-3 months currently)
- Unlocking prediction capabilities for mixed-class systems critical to technologies like batteries and catalysis

**Broader Impact:** By democratizing materials ML through reduced data requirements, this work enables smaller research groups and developing regions to participate in computational materials discovery, potentially accelerating solutions to global challenges in energy and sustainability.

---

## 2. Methodology

### 2.1 Overall Research Design

The research follows a five-phase validation strategy with staged hypothesis testing:

- **Phase 0 (Weeks 1-4)**: Empirical validation of atomic environment transferability
- **Phase 1 (Weeks 5-9)**: APG architecture development and equivariance testing
- **Phase 2 (Weeks 10-14)**: PIHCA implementation and latent space analysis
- **Phase 3 (Weeks 15-19)**: Transfer learning experiments (primary hypothesis test)
- **Phase 4 (Weeks 20-24)**: Multi-class OOD evaluation and ablation studies

### 2.2 Data Collection and Preparation

#### 2.2.1 Datasets

**Crystal Dataset (Pre-training):**
- Source: Materials Project (MP) database
- Size: 100,000 DFT-optimized inorganic crystal structures
- Properties: Formation energy ($E_f$), band gap ($E_g$), bulk modulus
- DFT Method: PBE functional, PAW pseudopotentials
- Quality Control: Remove structures with forces >0.05 eV/Å

**Polymer Dataset (Transfer Target):**
- Source: PoLyInfo database + Polymer Genome
- Size: 7,000 polymer structures (1,000 for transfer learning experiments)
- Properties: Glass transition temperature ($T_g$), thermal conductivity
- Generation: Molecular dynamics (MD) equilibration at 300K using OPLS-AA force field
- Quality Control: Exclude structures with unrealistic bond lengths (>2σ from mean)

**Surface Dataset (Validation):**
- Source: Catalysis-Hub + Open Catalyst Project
- Size: 5,000 slab structures with adsorbates
- Properties: Adsorption energy ($E_{ads}$), reaction barriers
- DFT Method: PBE+D3 (dispersion corrections)
- Slab Construction: 4-layer slabs with 15Å vacuum

**Cross-Class Validation Set:**
- Curated set of 1,500 materials with matched atomic environments across classes
- Example: sp³ carbon in diamond (crystal), polyethylene (polymer), diamond(111) surface
- Used for Phase 0 correlation studies

#### 2.2.2 Data Preprocessing

**Structure Normalization:**
1. Convert all structures to standardized coordinate systems (fractional coordinates for periodic dimensions)
2. Apply Niggli reduction for crystal lattices
3. Center polymer chains and surfaces in non-periodic dimensions

**Property Standardization:**
- Formation energy: Per-atom normalization ($E_f$ in eV/atom)
- Band gap: Direct/indirect gap distinction preserved
- $T_g$: Kelvin scale, experimental values cross-referenced with MD predictions
- $E_{ads}$: Referenced to gas-phase molecules

### 2.3 Adaptive Periodic Graph (APG) Construction

#### 2.3.1 Mathematical Formulation

An APG is defined as a tuple $\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathbf{L}, \mathbf{P})$ where:
- $\mathcal{V} = \{v_i\}_{i=1}^N$: Node set (atoms)
- $\mathcal{E}$: Edge set (bonds/interactions)
- $\mathbf{L} \in \mathbb{R}^{3 \times 3}$: Lattice matrix
- $\mathbf{P} \in \{0,1\}^3$: Periodicity mask ($P_i = 1$ if dimension $i$ is periodic)

**Class-Specific Graph Construction Rules:**

**Crystals (3D Periodic):**
$$\mathbf{P}_{\text{crystal}} = [1, 1, 1]$$
$$\mathcal{E}_{\text{crystal}} = \{(i,j,\mathbf{n}) : \|\mathbf{r}_{ij} + \mathbf{L}\mathbf{n}\| < r_{\text{cut}}, \mathbf{n} \in \mathbb{Z}^3\}$$

where $\mathbf{r}_{ij}$ is the displacement vector and $r_{\text{cut}} = 5.0$ Å.

**Polymers (1D Periodic):**
$$\mathbf{P}_{\text{polymer}} = [1, 0, 0]$$
$$\mathcal{E}_{\text{polymer}} = \{(i,j,n) : \|\mathbf{r}_{ij} + nL_x\hat{\mathbf{x}}\| < r_{\text{cut}}, n \in \mathbb{Z}\}$$

**Surfaces (2D Periodic):**
$$\mathbf{P}_{\text{surface}} = [1, 1, 0]$$
$$\mathcal{E}_{\text{surface}} = \{(i,j,\mathbf{n}) : \|\mathbf{r}_{ij} + n_xL_x\hat{\mathbf{x}} + n_yL_y\hat{\mathbf{y}}\| < r_{\text{cut}}, n_x, n_y \in \mathbb{Z}\}$$

#### 2.3.2 Unified Message Passing

The APG enables a single message-passing neural network (MPNN) architecture:

$$\mathbf{h}_i^{(l+1)} = \phi_{\text{update}}\left(\mathbf{h}_i^{(l)}, \bigoplus_{(j,\mathbf{n}) \in \mathcal{N}_i} \phi_{\text{message}}(\mathbf{h}_i^{(l)}, \mathbf{h}_j^{(l)}, \mathbf{e}_{ij,\mathbf{n}})\right)$$

where:
- $\mathbf{h}_i^{(l)} \in \mathbb{R}^{d}$: Node embedding at layer $l$ (dimension $d=512$)
- $\mathcal{N}_i$: Neighbors of node $i$ (includes periodic images)
- $\mathbf{e}_{ij,\mathbf{n}}$: Edge features (distance, direction)
- $\phi_{\text{message}}, \phi_{\text{update}}$: Learnable functions (MLPs)
- $\bigoplus$: Permutation-invariant aggregation (sum)

**Equivariant Edge Features:**
To preserve rotational equivariance, edge features use spherical harmonics:

$$\mathbf{e}_{ij,\mathbf{n}} = \left[\|\mathbf{r}_{ij,\mathbf{n}}\|, Y_l^m(\hat{\mathbf{r}}_{ij,\mathbf{n}})\right]$$

where $Y_l^m$ are spherical harmonics up to $l_{\max} = 3$, and $\hat{\mathbf{r}}_{ij,\mathbf{n}}$ is the normalized displacement vector.

### 2.4 Physics-Informed Hierarchical Contrastive Alignment (PIHCA)

#### 2.4.1 Three-Level Alignment Strategy

PIHCA aligns embeddings across material classes at three hierarchical levels:

**Level 1: Compositional Alignment**
Matches materials with identical elemental composition:
$$\mathcal{L}_{\text{comp}} = -\log \frac{\exp(\text{sim}(\mathbf{z}_i, \mathbf{z}_j^+)/\tau)}{\sum_{k=1}^K \exp(\text{sim}(\mathbf{z}_i, \mathbf{z}_k)/\tau)}$$

where $\mathbf{z}_i$ is the embedding of material $i$, $\mathbf{z}_j^+$ is a positive pair (same composition, different class), $K$ is batch size, $\tau = 0.07$ is temperature, and $\text{sim}(\cdot, \cdot)$ is cosine similarity.

**Level 2: Electronic Structure Alignment**
Matches materials with similar electronic properties (band gap, density of states):
$$\mathcal{L}_{\text{elec}} = -\log \frac{\exp(\text{sim}(\mathbf{z}_i, \mathbf{z}_j^+)/\tau)}{\sum_{k \in \mathcal{B}_{\text{elec}}} \exp(\text{sim}(\mathbf{z}_i, \mathbf{z}_k)/\tau)}$$

where $\mathcal{B}_{\text{elec}}$ contains materials with $|E_g^i - E_g^k| < 0.5$ eV.

**Level 3: Geometric Alignment**
Matches materials with similar local atomic environments (SOAP descriptors):
$$\mathcal{L}_{\text{geom}} = -\log \frac{\exp(\text{sim}(\mathbf{z}_i, \mathbf{z}_j^+)/\tau)}{\sum_{k \in \mathcal{B}_{\text{SOAP}}} \exp(\text{sim}(\mathbf{z}_i, \mathbf{z}_k)/\tau)}$$

where $\mathcal{B}_{\text{SOAP}}$ contains materials with SOAP similarity $> 0.9$.

**Combined Loss:**
$$\mathcal{L}_{\text{PIHCA}} = \alpha_{\text{comp}}\mathcal{L}_{\text{comp}} + \alpha_{\text{elec}}\mathcal{L}_{\text{elec}} + \alpha_{\text{geom}}\mathcal{L}_{\text{geom}}$$

with weights $\alpha_{\text{comp}} = 0.3$, $\alpha_{\text{elec}} = 0.3$, $\alpha_{\text{geom}} = 0.4$ (determined via pilot study in Week 2).

#### 2.4.2 SOAP Descriptor Computation

Smooth Overlap of Atomic Positions (SOAP) descriptors quantify local atomic environments:

$$\mathbf{p}_{nn'l}(i) = \sum_{m=-l}^l c_{nlm}^*(i) c_{n'lm}(i)$$

where $c_{nlm}(i)$ are expansion coefficients of the atomic density around atom $i$ in a basis of radial functions and spherical harmonics. Hyperparameters:
- Cutoff radius: $r_{\text{cut}} = 5.0$ Å
- Radial basis: $n_{\max} = 8$
- Angular basis: $l_{\max} = 6$

SOAP similarity between environments $i$ and $j$:
$$S_{\text{SOAP}}(i,j) = \frac{\mathbf{p}(i) \cdot \mathbf{p}(j)}{\|\mathbf{p}(i)\| \|\mathbf{p}(j)\|}$$

### 2.5 Compositional Atomic Environment Tokenization

Inspired by subword tokenization in NLP, we treat atomic environments as transferable units:

1. **Environment Extraction**: For each atom $i$, extract 3-hop neighborhood subgraph $\mathcal{G}_i^{(3)}$
2. **Descriptor Computation**: Compute SOAP descriptor $\mathbf{p}(i)$
3. **Vocabulary Construction**: Cluster SOAP descriptors across all materials using k-means ($k=10,000$ clusters)
4. **Token Assignment**: Assign each environment to nearest cluster centroid

This enables "materials BERT" pre-training where the model learns to predict masked environment tokens.

### 2.6 Model Architecture

**Encoder:**
- 6-layer equivariant graph neural network (E3NN framework)
- Hidden dimension: 512
- Spherical harmonics up to $l=3$
- Radial basis functions: 64 Gaussian RBFs
- Activation: SiLU (Swish)

**Decoder (Property Prediction):**
- Global pooling: Weighted sum over atoms (learned weights)
- 3-layer MLP: [512, 256, 128, 1]
- Dropout: 0.1
- Output activation: None (regression)

**Training Objective:**
$$\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{property}} + \lambda \mathcal{L}_{\text{PIHCA}}$$

where $\mathcal{L}_{\text{property}}$ is mean absolute error (MAE) for property prediction and $\lambda = 0.5$ balances supervised and contrastive learning.

### 2.7 Experimental Design

#### 2.7.1 Phase 0: Transferability Validation (Weeks 1-4)

**Objective:** Test if SOAP similarity predicts property correlation across classes.

**Protocol:**
1. Select 1,500 materials (500 crystals, 500 polymers, 500 surfaces)
2. For each material, compute local formation energy contributions via Bader charge analysis
3. Identify 5,000 cross-class environment pairs with SOAP similarity $> 0.9$
4. Compute Pearson correlation between local energy contributions

**Success Criterion:** $r > 0.7$ (80% statistical power for $n=5000$, $\alpha=0.05$)

**Falsification:** If $r < 0.3$, hypothesis is falsified; proceed to alternative (composition-only alignment)

#### 2.7.2 Phase 1: APG Development (Weeks 5-9)

**Objective:** Implement APG and validate equivariance.

**Equivariance Tests:**
1. Apply symmetry operations (rotations, translations, lattice permutations)
2. Measure property prediction change: $|\Delta E| < 0.001$ eV/atom

**Baselines:**
- Crystal-only: Matformer (replicated)
- Polymer-only: SchNet with chain-specific features
- Surface-only: DimeNet++ with slab geometry

#### 2.7.3 Phase 2: PIHCA Implementation (Weeks 10-14)

**Objective:** Train CoME-APG+ with hierarchical alignment.

**Training Protocol:**
- Pre-training: 100k crystals, 100 epochs, batch size 64
- Optimizer: AdamW, learning rate $3 \times 10^{-4}$, weight decay $10^{-5}$
- Learning rate schedule: Cosine annealing with warmup (10 epochs)
- Hardware: 4× NVIDIA V100 GPUs (32GB), ~200 GPU-hours

**Latent Space Analysis:**
1. Extract embeddings for 10k materials (all classes)
2. Compute t-SNE visualization
3. Measure clustering metrics:
   - Silhouette score by chemistry (target: $> 0.6$)
   - Silhouette score by class (target: $< 0.3$, indicating class-agnostic clustering)

#### 2.7.4 Phase 3: Transfer Learning Experiments (Weeks 15-19)

**Primary Hypothesis Test:**

**Experimental Conditions:**
1. **From-scratch baseline**: Train on polymer data only (varying sizes: 100, 500, 1k, 3k, 7k)
2. **Transfer learning**: Pre-train on crystals → fine-tune on polymers (same data sizes)
3. **Random initialization**: Pre-train on random labels → fine-tune (control for architecture benefits)

**Evaluation Protocol:**
- 5-fold cross-validation
- 3 random seeds per fold (15 runs total)
- Metrics: MAE, RMSE, Pearson $r$
- Statistical test: Paired t-test ($p < 0.05$)

**Transfer Efficiency Metric:**
$$\text{TE}(n) = \frac{\text{MAE}_{\text{scratch}}(7k) - \text{MAE}_{\text{transfer}}(n)}{\text{MAE}_{\text{scratch}}(7k) - \text{MAE}_{\text{scratch}}(n)}$$

**Success Criterion:** $\text{TE}(1k) \geq 0.70$ (achieves 70% of full-data performance with 1k samples)

**Learning Curve Analysis:**
Plot MAE vs. training set size (log scale) to identify data efficiency gains.

#### 2.7.5 Phase 4: Multi-Class OOD Evaluation (Weeks 20-24)

**Class-OOD Benchmark:**
1. Train on crystals + polymers → test on surfaces
2. Train on crystals + surfaces → test on polymers
3. Train on polymers + surfaces → test on crystals

**Metrics:**
- OOD ratio: $\text{MAE}_{\text{OOD}} / \text{MAE}_{\text{ID}}$ (target: $< 2.0$)
- Calibration: Expected calibration error (ECE)

**Ablation Studies:**
1. Remove APG (use class-specific graphs) → measure performance drop
2. Remove PIHCA (supervised only) → measure transfer efficiency drop
3. Remove tokenization (standard MPNN) → measure latent space quality drop
4. Single-level alignment (composition only) → compare to hierarchical

**Statistical Analysis:** Repeated measures ANOVA with Bonferroni correction.

### 2.8 Evaluation Metrics

**Property Prediction Accuracy:**
- Mean Absolute Error (MAE): Primary metric
- Root Mean Squared Error (RMSE): Sensitivity to outliers
- Pearson correlation ($r$): Linear relationship
- Spearman correlation ($\rho$): Monotonic relationship

**Transfer Learning Efficiency:**
- Transfer Efficiency (TE): Defined above
- Data Reduction Factor: $n_{\text{scratch}} / n_{\text{transfer}}$ for equivalent performance

**Latent Space Quality:**
- Silhouette score: Clustering quality
- Embedding distance: Within-chemistry vs. within-class
- Alignment score: SOAP similarity vs. embedding similarity correlation

**Computational Efficiency:**
- Training time (GPU-hours)
- Inference time (ms per structure)
- Memory footprint (GB)

**Physical Validity:**
- Equivariance error: $|\Delta E|$ under symmetry operations
- Energy conservation: Total energy vs. sum of local contributions
- Thermodynamic consistency: Formation energy ordering

---

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

#### 3.1.1 Quantitative Predictions

**Primary Outcome (Transfer Learning Efficiency):**
We predict that CoME-APG+ pre-trained on 100,000 crystals will achieve:
- **70% of full-data performance** on polymer $T_g$ prediction using only 1,000 training samples (vs. 7,000 required from scratch)
- **MAE < 12%** for $T_g$ prediction with 1k samples (comparable to 7k from-scratch baseline)
- **7× data reduction factor**, saving ~600,000 CPU-hours in DFT/MD calculations per new material class

**Secondary Outcomes:**

1. **Phase 0 Correlation Study:**
   - Pearson $r > 0.7$ between local energy contributions for cross-class environment pairs with SOAP similarity $> 0.9$
   - Validates atomic environment transferability assumption

2. **Latent Space Clustering:**
   - Silhouette score $> 0.6$ for chemistry-based clustering (sp², sp³, ionic, etc.)
   - Silhouette score $< 0.3$ for class-based clustering (demonstrates class-agnostic representations)
   - Embedding distance $< 0.5$ for same-chemistry, different-class pairs

3. **Equivariance Preservation:**
   - Property prediction change $|\Delta E| < 0.001$ eV/atom under symmetry operations
   - Validates APG maintains physical symmetries across classes

4. **Multi-Class OOD Performance:**
   - OOD ratio $< 2.0$ for class-OOD generalization (train on 2 classes, test on 3rd)
   - Outperforms class-specific baselines by $> 30\%$ on mixed-class systems (polymer nanocomposites)

5. **Ablation Study Results:**
   - Removing PIHCA: Transfer efficiency drops from 0.70 to $< 0.40$
   - Removing APG: Cannot handle multi-class data (architecture fails)
   - Single-level alignment: Transfer efficiency ~0.50 (confirms hierarchical design necessity)

#### 3.1.2 Qualitative Outcomes

**Theoretical Contributions:**
1. **"Structural Dialects" Framework**: Establishes materials classes as sharing atomic vocabulary but differing in physical grammar, providing theoretical foundation for cross-class transfer
2. **Extended Equivariance Theory**: Generalizes crystallographic symmetry groups to multi-class hierarchical groups
3. **Compositional Transferability Principle**: Connects thermochemical bond additivity to modern transfer learning theory

**Methodological Contributions:**
1. **APG Architecture**: First unified framework for periodic, semi-periodic, and non-periodic materials
2. **PIHCA Algorithm**: Novel physics-informed contrastive learning approach for materials
3. **Cross-Class OOD Benchmark**: New evaluation paradigm extending composition-OOD to class-OOD

**Software Deliverables:**
1. PyTorch Geometric extension for APG construction (open-source)
2. Pre-trained model weights for 100k crystal pre-training
3. Cross-class benchmark dataset (1,500 materials with matched environments)
4. Evaluation toolkit for transfer learning in materials

### 3.2 Scientific Impact

#### 3.2.1 Advancing Materials Informatics

**Paradigm Shift in Materials ML:**
Current practice treats each material class as a separate domain requiring custom architectures and large datasets. CoME-APG+ demonstrates that **unified representations are possible** by exploiting physical transferability, shifting the field toward:
- Universal materials models (analogous to foundation models in NLP/vision)
- Physics-informed transfer learning as standard practice
- Compositional approaches to materials representation

**Bridging Theory and Computation:**
The validation of atomic environment transferability provides empirical support for:
- Bond additivity approximations in thermochemistry
- Local density approximations in DFT
- Transferable force field development

This creates feedback between ML insights and fundamental materials theory.

#### 3.2.2 Enabling New Research Directions

**Mixed-Class Materials:**
CoME-APG+ uniquely enables prediction for heterogeneous systems:
- Polymer nanocomposites (polymer matrix + inorganic nanoparticles)
- Supported catalysts (metal surface + oxide support + adsorbates)
- Battery interfaces (crystal electrolyte + polymer separator)

These systems are critical for energy technologies but currently inaccessible to ML due to their multi-class nature.

**Rapid Adaptation to Emerging Classes:**
New material classes (e.g., metal-organic frameworks, 2D materials, high-entropy alloys) can be integrated by:
1. Defining APG construction rule (2-3 days)
2. Fine-tuning on small dataset (~100-500 samples)
3. Achieving competitive performance in 1 week vs. 1-3 months currently

This accelerates the ML development cycle for emerging materials.

### 3.3 Practical Impact

#### 3.3.1 Computational Cost Reduction

**Direct Savings:**
- **Polymer Discovery**: 7k → 1k structures needed = 6k fewer DFT/MD calculations
- **Per-Structure Cost**: ~100 CPU-hours (MD equilibration + property calculation)
- **Total Savings**: ~600,000 CPU-hours per new polymer dataset
- **Economic Value**: ~$30,000 in cloud computing costs (at $0.05/CPU-hour)

**Indirect Savings:**
- Reduced researcher time: 3-6 months → 2-4 weeks for new class adaptation
- Lower barrier to entry: Smaller groups can participate without massive compute infrastructure
- Faster iteration: Enables active learning loops with experiments

#### 3.3.2 Accelerating Materials Discovery

**Timeline Compression:**
Traditional workflow for new polymer class:
1. Literature review: 2-4 weeks
2. Dataset curation: 4-8 weeks
3. Model development: 4-12 weeks
4. Validation: 2-4 weeks
**Total: 3-7 months**

CoME-APG+ workflow:
1. Define APG rule: 2-3 days
2. Collect small dataset (1k samples): 2-3 weeks
3. Fine-tune pre-trained model: 3-5 days
4. Validation: 1 week
**Total: 4-6 weeks (5-7× faster)**

**Application Domains:**
- **Battery Materials**: Rapid screening of polymer electrolytes for solid-state batteries
- **Catalysis**: Transfer from metal surfaces to oxide supports to bimetallic catalysts
- **Sustainable Polymers**: Accelerate bio-based polymer design with limited experimental data

#### 3.3.3 Democratizing Materials ML

**Lowering Barriers:**
- **Data Requirements**: 7× reduction enables research with limited experimental/computational resources
- **Expertise Requirements**: Pre-trained models reduce need for ML architecture expertise
- **Computational Resources**: Fine-tuning requires ~50 GPU-hours vs. ~500 for training from scratch

**Broader Participation:**
- Academic labs without supercomputers can leverage pre-trained models
- Developing regions can participate in computational materials discovery
- Experimental groups can integrate ML predictions without extensive computational infrastructure

### 3.4 Broader Impact

#### 3.4.1 Addressing Global Challenges

**Energy Storage:**
- Accelerate discovery of polymer electrolytes for safer, higher-capacity batteries
- Enable rapid screening of electrode materials for next-generation energy storage

**Catalysis:**
- Speed up catalyst design for CO₂ reduction, hydrogen production, ammonia synthesis
- Reduce reliance on expensive platinum-group metals through computational screening

**Sustainable Materials:**
- Facilitate design of biodegradable polymers and recyclable materials
- Enable discovery of materials for water purification and environmental remediation

#### 3.4.2 Methodological Influence Beyond Materials

**Transfer to Adjacent Domains:**
The APG framework and PIHCA methodology are generalizable to:
- **Drug Discovery**: Molecules, proteins, and molecular complexes as different "classes"
- **Climate Science**: Transferring knowledge across atmospheric, oceanic, and terrestrial systems
- **Astrophysics**: Unified models for stellar, galactic, and cosmological structures

**Advancing ML Theory:**
- Physics-informed contrastive learning as general paradigm for scientific ML
- Compositional approaches to representation learning in structured domains
- Hierarchical alignment strategies for multi-modal scientific data

### 3.5 Validation and Dissemination Plan

**Publication Strategy:**
1. **Primary Paper**: Nature Machine Intelligence or NeurIPS (methodology + main results)
2. **Application Papers**: Domain-specific journals (e.g., Chemistry of Materials for polymers)
3. **Software Paper**: Journal of Open Source Software (APG toolkit)

**Open Science Commitments:**
- All code released under MIT license on GitHub
- Pre-trained models on Hugging Face Hub
- Benchmark datasets on Materials Cloud
- Reproducibility package with Docker containers

**Community Engagement:**
- Tutorial at NeurIPS ML4PS workshop
- Webinar series for materials science community
- Integration with existing tools (ASE, Pymatgen, JARVIS)

**Impact Metrics:**
- Citations (target: 100+ in 2 years)
- GitHub stars (target: 500+)
- Model downloads (target: 1,000+ users)
- Derived works (target: 5+ follow-up studies)

### 3.6 Risk Mitigation and Alternative Outcomes

**If Primary Hypothesis Fails (TE < 0.70):**
- **Partial Success (TE = 0.40-0.70)**: Still valuable for data reduction, publish as "moderate transfer"
- **Mechanism Insights**: Analyze which environment types transfer vs. which don't → inform future work
- **Alternative Applications**: APG still useful for multi-class datasets even without transfer

**If Phase 0 Fails (r < 0.7):**
- **Weaker Alignment**: Proceed with composition-only alignment (simpler hypothesis)
- **Class-Specific Modules**: Hybrid architecture with shared encoder, class-specific decoders
- **Theoretical Contribution**: Negative result informs limits of transferability

**Contingency Plans:**
- Budget includes 20% time buffer for troubleshooting
- Staged validation allows early detection of fundamental issues
- Ablation studies ensure publishable outcomes even if full system underperforms

---

## 4. Conclusion

This research proposal presents CoME-APG+, a unified framework for cross-class transfer learning in materials discovery that addresses the critical data bottleneck limiting ML applications in materials science. By exploiting the transferability of atomic environments across structural classes through Adaptive Periodic Graphs and Physics-Informed Hierarchical Contrastive Alignment, we predict achieving 70% of full-data performance with only 10% of typical training data—a 7× reduction translating to ~600,000 CPU-hours saved per new material class.

The staged validation strategy, from empirical correlation studies (Phase 0) through transfer learning experiments (Phase 3) to multi-class OOD evaluation (Phase 4), provides rigorous hypothesis testing with clear falsification criteria. The expected outcomes span theoretical contributions (structural dialects framework), methodological innovations (APG architecture, PIHCA algorithm), and practical impact (accelerating polymer discovery from months to weeks).

By democratizing materials ML through reduced data requirements and enabling prediction for previously inaccessible mixed-class systems, this work has the potential to accelerate solutions to global challenges in energy storage, catalysis, and sustainable materials—ultimately contributing to the broader goal of using machine learning to overcome materials bottlenecks in critical technologies.