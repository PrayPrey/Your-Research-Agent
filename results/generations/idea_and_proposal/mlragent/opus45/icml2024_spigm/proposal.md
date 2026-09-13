# Research Proposal: Hierarchical Graph Diffusion Models with Domain-Aware Structure Priors

## 1. Introduction

### Background

Generative models for structured data have witnessed remarkable progress, with diffusion models emerging as a powerful paradigm for high-fidelity synthesis across images, audio, and more recently, graphs. Graph-structured data pervades scientific domains—molecules in drug discovery, protein structures in biology, circuit topologies in electronic design, and crystalline materials in materials science. However, applying diffusion models to graph generation presents fundamental challenges that distinguish it from continuous data modalities.

Current graph diffusion approaches, such as GDSS and DiGress, typically treat graph generation as an unstructured denoising problem, progressively refining a noise distribution toward valid graph structures. While these methods achieve promising results on benchmark datasets, they struggle in highly structured scientific domains where generated samples must satisfy strict physical laws, chemical valence rules, or topological constraints. The core limitation is that standard diffusion processes operate uniformly across all graph elements, ignoring the inherent hierarchical organization present in real-world structured data—molecules decompose into functional groups, proteins into secondary and tertiary structures, and circuits into modular subcircuits.

### Research Objectives

This research proposes **Hierarchical Graph Diffusion Models with Domain-Aware Structure Priors (HiGD-SP)**, a novel framework that fundamentally reimagines graph diffusion by incorporating multi-scale structural decomposition and domain-specific constraints directly into the generative process. Our specific objectives are:

1. **Develop a learnable hierarchy extraction mechanism** that discovers meaningful graph abstractions aligned with domain concepts (e.g., molecular scaffolds, protein motifs).

2. **Design a cascaded diffusion architecture** where generation proceeds coarse-to-fine, with each hierarchical level conditioning on previously generated coarser structures.

3. **Formulate domain-aware guidance mechanisms** that incorporate physical and chemical constraints as soft score function modifications, enabling constraint satisfaction without expensive rejection sampling.

4. **Demonstrate substantial improvements** in validity rates, sampling efficiency, and interpretability across molecular generation, protein design, and circuit synthesis tasks.

### Significance

This research addresses a critical gap at the intersection of probabilistic generative modeling and structured scientific knowledge. By explicitly encoding hierarchical inductive biases and domain constraints, HiGD-SP promises to transform graph diffusion from a general-purpose technique into a practical tool for scientific discovery. The framework offers interpretable intermediate representations that align with expert understanding, facilitating human-AI collaboration in complex design tasks. Success in this endeavor would accelerate applications in drug discovery, materials design, and automated circuit synthesis, potentially reducing development cycles from years to weeks.

## 2. Methodology

### 2.1 Problem Formulation

Let $\mathcal{G} = (V, E, \mathbf{X}, \mathbf{E})$ represent a graph with node set $V$, edge set $E$, node features $\mathbf{X} \in \mathbb{R}^{|V| \times d_v}$, and edge features $\mathbf{E} \in \mathbb{R}^{|E| \times d_e}$. Our goal is to learn a generative distribution $p_\theta(\mathcal{G})$ that produces valid graphs adhering to domain constraints $\mathcal{C}$.

We define a hierarchy of graph abstractions $\{\mathcal{G}^{(L)}, \mathcal{G}^{(L-1)}, \ldots, \mathcal{G}^{(0)}\}$, where $\mathcal{G}^{(L)}$ represents the coarsest level and $\mathcal{G}^{(0)} = \mathcal{G}$ is the original graph. The hierarchical diffusion process generates graphs by:

$$p_\theta(\mathcal{G}) = p_\theta(\mathcal{G}^{(L)}) \prod_{\ell=L-1}^{0} p_\theta(\mathcal{G}^{(\ell)} | \mathcal{G}^{(\ell+1)})$$

### 2.2 Learnable Hierarchy Extraction

We employ a differentiable graph pooling network to learn meaningful hierarchical decompositions. For each level $\ell$, we compute soft cluster assignments:

$$\mathbf{S}^{(\ell)} = \text{softmax}\left(\text{GNN}_\phi^{(\ell)}(\mathbf{X}^{(\ell)}, \mathbf{A}^{(\ell)})\right) \in \mathbb{R}^{n_\ell \times n_{\ell+1}}$$

where $\mathbf{A}^{(\ell)}$ is the adjacency matrix at level $\ell$, and $n_{\ell+1} < n_\ell$ determines the coarsened graph size. The coarsened representations are computed as:

$$\mathbf{X}^{(\ell+1)} = (\mathbf{S}^{(\ell)})^\top \mathbf{X}^{(\ell)}, \quad \mathbf{A}^{(\ell+1)} = (\mathbf{S}^{(\ell)})^\top \mathbf{A}^{(\ell)} \mathbf{S}^{(\ell)}$$

To encourage domain-aligned clusters, we introduce an auxiliary loss that promotes grouping chemically or functionally related nodes:

$$\mathcal{L}_{\text{hier}} = \sum_{\ell} \left( \mathcal{L}_{\text{cut}}^{(\ell)} + \lambda_{\text{ortho}} \mathcal{L}_{\text{ortho}}^{(\ell)} + \lambda_{\text{domain}} \mathcal{L}_{\text{domain}}^{(\ell)} \right)$$

where $\mathcal{L}_{\text{cut}}$ minimizes edge cuts within clusters, $\mathcal{L}_{\text{ortho}}$ encourages orthogonal assignments, and $\mathcal{L}_{\text{domain}}$ leverages domain-specific supervision (e.g., known functional groups in molecules).

### 2.3 Cascaded Diffusion Process

At each hierarchical level $\ell$, we define a continuous-time diffusion process. The forward process corrupts the graph structure over time $t \in [0, T]$:

$$q(\mathcal{G}_t^{(\ell)} | \mathcal{G}_0^{(\ell)}) = \mathcal{N}(\mathcal{G}_t^{(\ell)}; \alpha_t^{(\ell)} \mathcal{G}_0^{(\ell)}, \sigma_t^{(\ell)2} \mathbf{I})$$

**Domain-Aware Noise Schedule:** A key innovation is our level-specific noise schedule $(\alpha_t^{(\ell)}, \sigma_t^{(\ell)})$ designed to respect structural hierarchies:

$$\sigma_t^{(\ell)} = \sigma_{\min}^{(\ell)} \left(\frac{\sigma_{\max}^{(\ell)}}{\sigma_{\min}^{(\ell)}}\right)^{t/T} \cdot \gamma^{L-\ell}$$

where $\gamma > 1$ ensures coarser levels experience stronger noise, forcing the model to first establish high-level structure before refining details. The parameters $\sigma_{\min}^{(\ell)}, \sigma_{\max}^{(\ell)}$ are learned per domain.

**Conditional Generation:** The reverse process at level $\ell$ is conditioned on the coarser structure $\mathcal{G}^{(\ell+1)}$:

$$p_\theta(\mathcal{G}_{t-\Delta t}^{(\ell)} | \mathcal{G}_t^{(\ell)}, \mathcal{G}^{(\ell+1)}) = \mathcal{N}(\mathcal{G}_{t-\Delta t}^{(\ell)}; \mu_\theta^{(\ell)}, \Sigma_\theta^{(\ell)})$$

The mean is predicted by a graph neural network that jointly processes the current noisy state and the conditioning structure:

$$\mu_\theta^{(\ell)} = \frac{1}{\alpha_{t|t-\Delta t}}\left(\mathcal{G}_t^{(\ell)} - \frac{\sigma_t^2 - \alpha_{t|t-\Delta t}^2 \sigma_{t-\Delta t}^2}{\sigma_t} \epsilon_\theta^{(\ell)}(\mathcal{G}_t^{(\ell)}, \mathcal{G}^{(\ell+1)}, t)\right)$$

### 2.4 Domain Constraint Guidance

We incorporate domain constraints $\mathcal{C}$ through classifier-free guidance modified for structured outputs. Define a constraint satisfaction score $c(\mathcal{G})$ that quantifies adherence to domain rules (e.g., chemical valence, circuit connectivity laws). The guided score function becomes:

$$\tilde{s}_\theta(\mathcal{G}_t, t) = s_\theta(\mathcal{G}_t, t) + \omega \nabla_{\mathcal{G}_t} \log p_\psi(c | \mathcal{G}_t)$$

where $\omega$ controls guidance strength and $p_\psi(c | \mathcal{G}_t)$ is a learned constraint predictor trained on domain-valid graphs.

For hard constraints (e.g., valence rules), we employ a projection step after each denoising update:

$$\mathcal{G}_{t-\Delta t}' = \Pi_{\mathcal{C}}(\mathcal{G}_{t-\Delta t})$$

where $\Pi_{\mathcal{C}}$ projects onto the feasible constraint set through efficient combinatorial operations specific to each domain.

### 2.5 Training Procedure

The complete training objective combines denoising losses across all hierarchical levels with hierarchy regularization:

$$\mathcal{L}_{\text{total}} = \sum_{\ell=0}^{L} \mathbb{E}_{t, \mathcal{G}_0^{(\ell)}, \epsilon}\left[\lambda_\ell \|\epsilon - \epsilon_\theta^{(\ell)}(\mathcal{G}_t^{(\ell)}, \mathcal{G}^{(\ell+1)}, t)\|^2\right] + \mathcal{L}_{\text{hier}}$$

where $\lambda_\ell$ weights each level's contribution, with higher weights for finer levels to ensure detail preservation.

**Algorithm 1: HiGD-SP Training**
```
Input: Training graphs {G}, hierarchy depth L, constraint set C
1. For each graph G, extract hierarchy {G^(0),...,G^(L)} using pooling networks
2. For each training iteration:
   a. Sample t ~ Uniform(0,T), ε ~ N(0,I)
   b. For ℓ = L to 0:
      - Compute noisy graph: G_t^(ℓ) = α_t^(ℓ)G_0^(ℓ) + σ_t^(ℓ)ε
      - Predict noise: ε_hat = ε_θ^(ℓ)(G_t^(ℓ), G^(ℓ+1), t)
      - Accumulate loss
   c. Update θ, φ via gradient descent on L_total
```

### 2.6 Experimental Design

**Datasets:**
- **Molecules:** ZINC-250K, MOSES benchmark, GuacaMol for drug-likeness
- **Proteins:** CATH 4.2 for secondary structure motifs
- **Circuits:** ISCAS-85/89 benchmark circuits

**Baselines:** GraphVAE, GCPN, DiGress, GDSS, HiGen, MolGAN

**Evaluation Metrics:**
1. **Validity:** Percentage of chemically valid molecules, physically realizable circuits
2. **Uniqueness:** Proportion of distinct generated samples
3. **Novelty:** Fraction not in training set
4. **Fréchet Graph Distance (FGD):** Distribution similarity to real data
5. **Constraint Satisfaction Rate (CSR):** Domain-specific constraint adherence
6. **Sampling Time:** Wall-clock time per generated graph
7. **Hierarchical Alignment Score:** Mutual information between learned clusters and domain concepts

**Ablation Studies:**
- Effect of hierarchy depth $L$
- Impact of domain-aware noise schedules vs. uniform schedules
- Contribution of constraint guidance mechanisms
- Scalability analysis with increasing graph size

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Validity Improvements:** We anticipate achieving >95% validity rates on molecular generation benchmarks, compared to 80-90% for current state-of-the-art methods, through explicit constraint guidance.

2. **Sampling Efficiency:** The hierarchical decomposition should yield 3-5× faster sampling by reducing the effective dimensionality at each level and enabling parallel generation of independent substructures.

3. **Interpretable Representations:** Learned hierarchies are expected to align with domain concepts (>0.8 normalized mutual information with expert annotations), providing transparency into the generation process.

4. **Generalization:** Models trained on drug-like molecules should transfer effectively to related chemical spaces with minimal fine-tuning, demonstrating the inductive bias benefits of hierarchical structure.

### Broader Impact

**Scientific Discovery:** HiGD-SP will enable researchers in drug discovery to generate novel molecular candidates that satisfy both structural validity and desired property profiles, potentially accelerating lead optimization timelines.

**Materials Science:** Application to crystalline materials and polymers will support automated discovery of materials with target properties, contributing to sustainable technology development.

**Methodological Advances:** The framework establishes a template for incorporating domain knowledge into probabilistic generative models, with principles transferable to other structured modalities including temporal graphs, 3D point clouds, and combinatorial structures.

**Open Science:** We commit to releasing code, pretrained models, and benchmark datasets to foster reproducibility and community development, aligning with the workshop's goal of fostering collaboration in probabilistic methods.

This research directly addresses the workshop's emphasis on encoding domain knowledge in structured probabilistic inference, offering both theoretical contributions in hierarchical diffusion design and practical advances for scientific applications.