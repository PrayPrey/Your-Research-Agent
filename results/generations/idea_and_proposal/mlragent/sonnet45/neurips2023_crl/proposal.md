# Research Proposal: Hierarchical Causal Abstraction Learning for Multi-Granularity Visual Understanding

## 1. Title

**Hierarchical Causal Abstraction Learning for Multi-Granularity Visual Understanding**

## 2. Introduction

### 2.1 Background

Current machine learning systems, despite their impressive performance on various tasks, fundamentally rely on statistical correlations and struggle with domain generalization, adversarial robustness, and causal reasoning. The emerging field of causal representation learning (CRL) addresses these limitations by learning high-level causal variables and their relationships directly from raw, unstructured data. However, existing CRL approaches predominantly operate at a single level of abstraction, either focusing on fine-grained low-level features or high-level conceptual representations.

Human cognition, in contrast, naturally processes information across multiple scales of abstraction simultaneously. When diagnosing a medical condition, for instance, physicians reason about cellular-level abnormalities, tissue-level patterns, and organ-level dysfunctions concurrently, understanding how causal mechanisms operate at each level and how they interact across levels. Similarly, understanding a complex scene involves recognizing both primitive visual elements (edges, textures) and abstract concepts (objects, relationships, events) while maintaining awareness of the causal dependencies within and across these hierarchical levels.

Recent work has begun to explore hierarchical representations in vision (Ge et al., 2022; Xu et al., 2022) and causal abstraction principles (D'Acunto et al., 2025), but these approaches lack a unified framework that simultaneously learns multi-level causal structures and the abstraction mappings between them. The Humanoid-inspired Structural Causal Model (Tao et al., 2025) demonstrates the value of hierarchical processing for domain generalization, but does not explicitly model causal relationships across abstraction levels or enable cross-level interventions.

### 2.2 Research Objectives

This research proposes a novel **Hierarchical Causal Abstraction Learning (HCAL)** framework that addresses the following objectives:

1. **Develop a principled approach** for automatically discovering multi-level causal abstractions from raw visual data, learning both the causal variables at each level and the abstraction functions mapping between levels.

2. **Design cross-level intervention mechanisms** that enable learning when different granularities are causally relevant and how causal effects propagate across abstraction hierarchies.

3. **Establish theoretical foundations** for identifiability of hierarchical causal structures under realistic assumptions about multi-environment or multi-modal visual data.

4. **Validate the framework** on both synthetic benchmarks with known ground-truth hierarchical causal structures and real-world applications in medical imaging and robotic vision.

### 2.3 Significance

This research addresses several critical gaps in current CRL literature:

**Theoretical Contribution**: We provide formal conditions under which hierarchical causal structures are identifiable from observational and interventional data, extending existing identifiability results in CRL to the multi-level setting.

**Methodological Innovation**: Our framework introduces novel mechanisms for bottom-up causal discovery, top-down consistency enforcement, and cross-level intervention design, enabling more flexible and interpretable causal representation learning.

**Practical Impact**: By learning appropriate abstractions automatically, HCAL can improve sample efficiency, enhance interpretability through multi-scale causal explanations, and achieve better generalization across domains—particularly valuable for applications like medical diagnosis, autonomous systems, and scientific discovery where reasoning at multiple scales is essential.

## 3. Methodology

### 3.1 Problem Formulation

We formalize the hierarchical causal representation learning problem as follows. Let $\mathbf{x} \in \mathbb{R}^d$ denote high-dimensional raw visual observations (e.g., image pixels). We assume there exists a hierarchy of $L$ abstraction levels, where level $\ell=0$ represents the finest granularity and level $\ell=L-1$ the coarsest.

At each level $\ell$, we have:
- Latent causal variables $\mathbf{z}^{(\ell)} = (z^{(\ell)}_1, \ldots, z^{(\ell)}_{n_\ell}) \in \mathbb{R}^{n_\ell}$
- A structural causal model (SCM) defined by: $$z^{(\ell)}_i = f^{(\ell)}_i(\text{pa}^{(\ell)}_i, \epsilon^{(\ell)}_i)$$
where $\text{pa}^{(\ell)}_i$ denotes the parents of $z^{(\ell)}_i$ in the causal graph $\mathcal{G}^{(\ell)}$, and $\epsilon^{(\ell)}_i$ are independent exogenous noise variables.

Between adjacent levels, abstraction functions $\alpha^{(\ell)}: \mathbb{R}^{n_\ell} \to \mathbb{R}^{n_{\ell+1}}$ map from finer to coarser representations: $$\mathbf{z}^{(\ell+1)} = \alpha^{(\ell)}(\mathbf{z}^{(\ell)})$$

The observation is generated from the finest level: $$\mathbf{x} = g(\mathbf{z}^{(0)}, \epsilon_x)$$

**Goal**: Learn the causal variables $\{\mathbf{z}^{(\ell)}\}_{\ell=0}^{L-1}$, causal graphs $\{\mathcal{G}^{(\ell)}\}_{\ell=0}^{L-1}$, and abstraction functions $\{\alpha^{(\ell)}\}_{\ell=0}^{L-2}$ from observational data $\{\mathbf{x}^{(i)}\}_{i=1}^N$ collected under multiple environments or interventions.

### 3.2 Model Architecture

Our HCAL framework consists of three main components:

#### 3.2.1 Hierarchical Encoder

We employ a multi-scale variational autoencoder (VAE) architecture with $L$ levels:

$$q_\phi(\mathbf{z}^{(0)}, \ldots, \mathbf{z}^{(L-1)} | \mathbf{x}) = q_\phi(\mathbf{z}^{(0)}|\mathbf{x}) \prod_{\ell=1}^{L-1} q_\phi(\mathbf{z}^{(\ell)}|\mathbf{z}^{(\ell-1)})$$

The encoder $q_\phi(\mathbf{z}^{(0)}|\mathbf{x})$ maps raw observations to the finest-level representation using a convolutional neural network. Each subsequent encoder $q_\phi(\mathbf{z}^{(\ell)}|\mathbf{z}^{(\ell-1)})$ implements the learned abstraction function.

#### 3.2.2 Causal Graph Networks

At each level $\ell$, we model causal dependencies using a graph neural network (GNN) with a learned adjacency matrix $\mathbf{A}^{(\ell)} \in \{0,1\}^{n_\ell \times n_\ell}$:

$$\tilde{\mathbf{z}}^{(\ell)} = \text{GNN}_\theta^{(\ell)}(\mathbf{z}^{(\ell)}, \mathbf{A}^{(\ell)})$$

We enforce acyclicity through a continuous relaxation and DAG constraint (Zheng et al., 2018):
$$\mathcal{L}_{\text{DAG}}^{(\ell)} = \text{tr}(e^{\mathbf{A}^{(\ell)} \odot \mathbf{A}^{(\ell)}}) - n_\ell$$

#### 3.2.3 Hierarchical Decoder

The decoder reconstructs observations from the multi-level representations:
$$p_\psi(\mathbf{x}|\mathbf{z}^{(0)}, \ldots, \mathbf{z}^{(L-1)}) = p_\psi(\mathbf{x}|\mathbf{z}^{(0)})$$

### 3.3 Training Objectives

#### 3.3.1 Bottom-Up Causal Discovery

For the finest level, we maximize a causal variational objective inspired by recent CRL work:

$$\mathcal{L}_{\text{causal}}^{(0)} = \mathbb{E}_{q_\phi}[\log p_\psi(\mathbf{x}|\mathbf{z}^{(0)})] - \beta \text{KL}(q_\phi(\mathbf{z}^{(0)}|\mathbf{x}) \| p(\mathbf{z}^{(0)}))$$

where the prior $p(\mathbf{z}^{(0)}) = \prod_i p(z^{(0)}_i | \text{pa}^{(0)}_i)$ factorizes according to the learned graph $\mathcal{G}^{(0)}$.

To encourage disentanglement and causal structure, we add:
$$\mathcal{L}_{\text{indep}}^{(0)} = \sum_{i,j} \text{HSIC}(z^{(0)}_i, z^{(0)}_j | \text{pa}^{(0)}_i, \text{pa}^{(0)}_j)$$

where HSIC denotes the Hilbert-Schmidt Independence Criterion.

#### 3.3.2 Abstraction Learning

For learning abstraction functions, we introduce an **intervention-based abstraction consistency** loss. Given interventions at level $\ell$, the abstracted representations should exhibit consistent causal effects at level $\ell+1$:

$$\mathcal{L}_{\text{abs}}^{(\ell)} = \mathbb{E}_{\mathbf{z}^{(\ell)}, \text{do}(z^{(\ell)}_i)} \| \alpha^{(\ell)}(\mathbf{z}^{(\ell)}_{\text{do}(z_i)}) - \mathbf{z}^{(\ell+1)}_{\text{do}(\alpha_i)} \|^2$$

This ensures that interventions at finer levels induce consistent interventional distributions at coarser levels, following the semantic embedding principle (D'Acunto et al., 2025).

#### 3.3.3 Top-Down Refinement

To leverage high-level causal structure for guiding low-level learning, we introduce a **causal consistency constraint**:

$$\mathcal{L}_{\text{refine}}^{(\ell)} = \mathbb{E}\left[\sum_{i,j} |\mathbb{I}[A^{(\ell+1)}_{ij} = 1] - \sigma(\text{GroupCausal}(\mathbf{z}^{(\ell)}, \alpha^{(\ell)}))|\right]$$

where GroupCausal measures whether groups of fine-level variables mapped to the same coarse-level variable exhibit consistent causal relationships.

#### 3.3.4 Cross-Level Intervention

We design a novel **cross-level intervention mechanism** where we:
1. Sample intervention targets at level $\ell$: $\text{do}(z^{(\ell)}_i = v)$
2. Propagate effects downward through learned inverse abstractions $\alpha^{-1}$
3. Propagate effects upward through forward abstractions $\alpha$
4. Enforce consistency: $$\mathcal{L}_{\text{cross}} = \sum_{\ell} \mathbb{E}\|\mathbf{z}^{(\ell)}_{\text{intervened}} - \alpha^{(\ell-1)}(\alpha^{-1,(\ell)}(\mathbf{z}^{(\ell)}_{\text{intervened}}))\|^2$$

### 3.4 Overall Optimization

The complete objective combines all components:

$$\mathcal{L}_{\text{total}} = \sum_{\ell=0}^{L-1} \left[\mathcal{L}_{\text{causal}}^{(\ell)} + \lambda_1 \mathcal{L}_{\text{indep}}^{(\ell)} + \lambda_2 \mathcal{L}_{\text{DAG}}^{(\ell)}\right] + \sum_{\ell=0}^{L-2} \left[\lambda_3 \mathcal{L}_{\text{abs}}^{(\ell)} + \lambda_4 \mathcal{L}_{\text{refine}}^{(\ell)}\right] + \lambda_5 \mathcal{L}_{\text{cross}}$$

We optimize using a **three-stage curriculum**:
1. **Stage 1**: Learn finest-level representations with $\mathcal{L}_{\text{causal}}^{(0)}$ and $\mathcal{L}_{\text{indep}}^{(0)}$
2. **Stage 2**: Learn abstractions bottom-up with $\mathcal{L}_{\text{abs}}$
3. **Stage 3**: Joint refinement with all objectives including cross-level interventions

### 3.5 Data Collection

We collect data from three sources:

**Synthetic Benchmarks**: Generate hierarchical datasets with known ground-truth causal structures at multiple levels:
- Multi-scale geometric shapes (primitive features → objects → scenes)
- Hierarchical physical simulations (particle dynamics → rigid bodies → articulated systems)
- Temporal hierarchies (frames → events → activities)

**Medical Imaging**: Utilize multi-modal medical datasets:
- Histopathology images (cellular → tissue → organ levels)
- Brain MRI scans (voxel → region → network levels)
- Retinal imaging (pixel → vessel → pathology levels)

**Multi-Environment Vision**: Collect or use existing datasets with distribution shifts:
- DomainNet, PACS for object recognition
- Causal3DIdent for controlled 3D scenes
- Robot manipulation datasets with varying conditions

### 3.6 Experimental Design

#### 3.6.1 Synthetic Evaluation

**Metrics**:
- **Causal Graph Recovery**: Structural Hamming Distance (SHD) at each level
- **Abstraction Accuracy**: Normalized Mutual Information between learned and true abstractions
- **Intervention Prediction**: Mean Squared Error on held-out interventional distributions
- **Identifiability**: Mean Correlation Coefficient (MCC) between learned and ground-truth factors

**Experiments**:
1. Vary number of abstraction levels (L = 2, 3, 4)
2. Vary number of environments/interventions (5, 10, 20, 50)
3. Compare against baselines: standard VAE, β-VAE, iVAE, single-level causal VAE

#### 3.6.2 Medical Imaging Evaluation

**Task**: Multi-level disease diagnosis in diabetic retinopathy

**Metrics**:
- Classification accuracy at organ level (disease present/absent)
- Localization accuracy at tissue level (lesion segmentation)
- Feature attribution at pixel level (interpretability)
- Cross-domain generalization (train on one dataset, test on another)

**Experiments**:
1. Supervised learning with limited labels
2. Transfer learning across imaging modalities
3. Counterfactual generation for data augmentation
4. Expert evaluation of multi-scale explanations

#### 3.6.3 Domain Generalization Evaluation

**Datasets**: PACS, DomainNet, Causal3DIdent

**Metrics**:
- Out-of-domain classification accuracy
- Intervention accuracy (predict effect of style changes)
- Sample efficiency (performance vs. training size)

**Baselines**:
- Domain-invariant representation learning methods (IRM, VREx)
- Single-level CRL methods
- Standard domain adaptation approaches

#### 3.6.4 Ablation Studies

Systematically remove components:
- Remove cross-level interventions ($\lambda_5 = 0$)
- Remove top-down refinement ($\lambda_4 = 0$)
- Remove abstraction consistency ($\lambda_3 = 0$)
- Use fixed hierarchy vs. learned number of levels

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Theoretical Contributions**:
1. **Identifiability Theorems**: We expect to establish sufficient conditions (e.g., number of environments, intervention diversity, abstraction smoothness) under which hierarchical causal structures are identifiable up to appropriate equivalence classes.

2. **Complexity Analysis**: Characterization of the sample and computational complexity of learning $L$-level hierarchies as a function of graph density, abstraction cardinality, and environment diversity.

**Empirical Results**:
1. **Synthetic Benchmarks**: We anticipate achieving >90% causal graph recovery accuracy (SHD < 5% of total edges) with 20+ environments and correctly identifying abstraction hierarchies with >0.8 NMI.

2. **Medical Imaging**: Expected improvements of 10-15% in out-of-domain generalization over single-level baselines, with physician-validated interpretability improvements in multi-scale explanations.

3. **Domain Generalization**: Anticipated 5-10% accuracy improvement on PACS/DomainNet with 30-50% reduction in sample complexity compared to existing methods.

**Algorithmic Artifacts**:
- Open-source implementation of HCAL framework
- Synthetic benchmark suite with configurable hierarchical causal structures
- Pre-trained models for medical imaging applications

### 4.2 Impact on Causal Representation Learning

**Advancing CRL Theory**: This work extends the theoretical foundations of CRL from single-level to multi-level settings, addressing a fundamental limitation of current identifiability results. The cross-level intervention framework provides new theoretical tools for reasoning about causal abstraction.

**Methodological Innovation**: The proposed bottom-up discovery with top-down refinement paradigm offers a new template for hierarchical learning that can be adapted to other domains beyond vision, including hierarchical reinforcement learning, multi-scale time series analysis, and scientific modeling.

**Bridging Theory and Practice**: By demonstrating practical benefits in medical imaging—a domain requiring both interpretability and accuracy—this work helps bridge the gap between theoretical CRL advances and real-world deployment.

### 4.3 Broader Impact

**Medical Applications**: Multi-granularity causal understanding can revolutionize medical diagnosis by providing interpretable explanations at appropriate abstraction levels for different stakeholders (researchers need cellular-level insights, clinicians need organ-level assessments). This could improve diagnostic accuracy while increasing trust and adoption.

**Scientific Discovery**: The framework can accelerate scientific discovery in fields requiring multi-scale reasoning (materials science, climate modeling, systems biology) by automatically identifying causal mechanisms at appropriate granularities and their interactions.

**Robust AI Systems**: By learning causal structures across abstraction levels, HCAL-based models should exhibit improved robustness to distribution shifts, adversarial perturbations, and domain changes—critical for deploying AI in safety-critical applications like autonomous vehicles and healthcare.

**Efficient Learning**: Leveraging causal structure at appropriate abstraction levels can dramatically improve sample efficiency, reducing the data requirements for training effective models—particularly valuable when data collection is expensive or raises privacy concerns.

### 4.4 Limitations and Future Directions

**Known Limitations**:
- Assumes existence of discrete abstraction levels rather than continuous hierarchies
- Computational cost increases with number of levels and variables
- Requires sufficient environment diversity for identifiability

**Future Research Directions**:
1. Extend to continuous, adaptive hierarchies that adjust granularity based on task demands
2. Incorporate temporal dynamics for learning hierarchical causal processes
3. Develop active intervention selection strategies to minimize required environments
4. Apply to reinforcement learning for hierarchical planning and transfer
5. Investigate connections to neuroscience and cognitive models of hierarchical perception

This research represents a significant step toward AI systems that can reason about the world at multiple scales of abstraction, mirroring human cognitive abilities and moving beyond simple correlation-based learning toward true causal understanding.