# Research Proposal: Equivariant Flow Matching on Homogeneous Spaces for Molecular Generation

## 1. Introduction

### Background

The generation of molecular structures with realistic geometric properties is a fundamental challenge in computational chemistry, drug discovery, and materials science. Recent advances in deep generative models have demonstrated remarkable success in learning complex data distributions, yet molecular generation poses unique challenges due to the intrinsic geometric and symmetry constraints governing molecular systems. Molecules exist in three-dimensional space and exhibit invariance under rotations, translations, and permutations of identical atoms—properties that any meaningful generative model must respect.

Current state-of-the-art approaches for molecular generation predominantly operate in Euclidean space, employing SE(3)-equivariant neural networks to ensure that generated structures transform appropriately under rigid body motions. While these methods have achieved significant progress, they fundamentally treat molecular geometry as point clouds in $\mathbb{R}^3$, overlooking the natural hierarchical structure of molecular configurations. Specifically, molecular geometry can be decomposed into distinct geometric components: global pose (position and orientation), bond lengths, bond angles, and dihedral (torsion) angles. Each of these components naturally lives on different geometric spaces—SE(3) for global pose, positive reals for bond lengths, spheres $S^2$ for bond angles, and circles $S^1$ (or tori $\mathbb{T}^n$) for dihedrals.

This observation motivates a paradigm shift: rather than learning generative models in ambient Euclidean space, we should construct them directly on the product of homogeneous spaces that naturally describe molecular geometry. Flow matching, a recently developed framework for training continuous normalizing flows, provides an elegant foundation for this approach. By designing vector fields that respect both the manifold geometry and symmetry structure, we can achieve generative models with guaranteed equivariance, improved sample quality, and enhanced training efficiency.

### Research Objectives

This research proposes **Equivariant Flow Matching on Homogeneous Spaces (EFM-HS)**, a novel framework for molecular generation that:

1. Decomposes molecular geometry into a hierarchical product of homogeneous spaces, respecting the natural geometric structure of molecules.
2. Constructs equivariant vector fields on each manifold component using fiber bundle theory and Lie group representations.
3. Develops conditional flow matching objectives with geodesic interpolants tailored to each geometric component.
4. Demonstrates superior performance on molecular generation benchmarks, particularly for flexible molecules with non-trivial conformational distributions.

### Significance

This research addresses fundamental challenges at the intersection of geometric deep learning and generative modeling. By grounding molecular generation in the natural geometry of configuration spaces, EFM-HS promises: (i) guaranteed preservation of physical symmetries by construction; (ii) more accurate modeling of molecular flexibility, critical for drug-receptor binding and protein folding; (iii) computational efficiency through closed-form optimal transport on individual manifold components; and (iv) a theoretical framework that unifies structure-preserving learning with geometric generative modeling. The outcomes have direct implications for accelerating drug discovery pipelines and enabling more realistic simulation of molecular dynamics.

## 2. Methodology

### 2.1 Geometric Decomposition of Molecular Configuration Space

We begin by formally decomposing the configuration space of a molecule with $N$ atoms. Let $\mathbf{x} = (\mathbf{x}_1, \ldots, \mathbf{x}_N) \in \mathbb{R}^{3N}$ denote atomic positions. We decompose this into:

**Global Pose:** The rigid body transformation $(R, \mathbf{t}) \in \text{SE}(3)$, where $R \in \text{SO}(3)$ is a rotation matrix and $\mathbf{t} \in \mathbb{R}^3$ is a translation vector.

**Internal Coordinates:** Following the Z-matrix convention, internal coordinates consist of:
- Bond lengths: $\{d_i\}_{i=1}^{N-1} \in \mathbb{R}_{>0}^{N-1}$
- Bond angles: $\{\theta_i\}_{i=1}^{N-2} \in (0, \pi)^{N-2} \subset S^2$
- Dihedral angles: $\{\phi_i\}_{i=1}^{N-3} \in \mathbb{T}^{N-3}$, where $\mathbb{T} = S^1$

The full configuration space is thus modeled as:
$$\mathcal{M} = \text{SE}(3) \times \mathbb{R}_{>0}^{N-1} \times S^{N-2} \times \mathbb{T}^{N-3}$$

where we treat bond angles as points on spheres via their spherical embedding. For molecules with fixed bond lengths and angles (rigid bonds), the relevant space reduces to $\mathcal{M}_{\text{flex}} = \text{SE}(3) \times \mathbb{T}^{N-3}$.

### 2.2 Flow Matching on Product Manifolds

Flow matching learns a time-dependent vector field $v_t: \mathcal{M} \times [0,1] \rightarrow T\mathcal{M}$ that transports samples from a prior distribution $p_0$ to a target distribution $p_1$. The flow is defined by the ordinary differential equation:
$$\frac{d\mathbf{z}_t}{dt} = v_t(\mathbf{z}_t), \quad \mathbf{z}_0 \sim p_0$$

For product manifolds $\mathcal{M} = \mathcal{M}_1 \times \cdots \times \mathcal{M}_K$, the tangent space decomposes as $T_{\mathbf{z}}\mathcal{M} = T_{z_1}\mathcal{M}_1 \oplus \cdots \oplus T_{z_K}\mathcal{M}_K$. We design the vector field as:
$$v_t(\mathbf{z}) = (v_t^{(1)}(z_1; \mathbf{z}), \ldots, v_t^{(K)}(z_K; \mathbf{z}))$$

where each component $v_t^{(k)}$ is a vector field on $\mathcal{M}_k$ that may depend on the full configuration $\mathbf{z}$ for coordination.

**Geodesic Interpolants:** For each manifold component, we construct conditional flows using geodesic interpolation. Given samples $z_0^{(k)} \sim p_0^{(k)}$ and $z_1^{(k)} \sim p_1^{(k)}$, the geodesic interpolant is:
$$z_t^{(k)} = \exp_{z_0^{(k)}}\left(t \cdot \log_{z_0^{(k)}}(z_1^{(k)})\right)$$

where $\exp$ and $\log$ are the Riemannian exponential and logarithmic maps on $\mathcal{M}_k$.

For specific manifolds:
- **On $\mathbb{T}^n$ (tori):** $z_t = z_0 + t(z_1 - z_0) \mod 2\pi$, with the shortest arc connection.
- **On SO(3):** $R_t = R_0 \exp(t \cdot \log(R_0^T R_1))$, using the matrix exponential.
- **On $S^2$ (spheres):** Spherical linear interpolation (slerp).

The conditional vector field generating this interpolation is:
$$u_t(z_t | z_0, z_1) = \frac{d z_t}{dt} = \text{PT}_{z_0 \to z_t}\left(\log_{z_0}(z_1)\right)$$

where $\text{PT}$ denotes parallel transport along the geodesic.

### 2.3 Equivariant Vector Field Parameterization

To ensure the generative model respects molecular symmetries, we parameterize the vector field using equivariant neural networks. We employ fiber bundle theory to structure this construction.

**Fiber Bundle Framework:** We model the molecular configuration as a principal G-bundle $\pi: P \rightarrow B$, where:
- $B$ is the base space of invariant features (e.g., interatomic distances, angles)
- $G = \text{SE}(3) \times S_N$ is the symmetry group (Euclidean motions and permutations)
- $P$ encodes the full geometric configuration

The equivariant vector field must satisfy:
$$v_t(g \cdot \mathbf{z}) = g_* v_t(\mathbf{z}), \quad \forall g \in G$$

where $g_*$ is the pushforward of the group action.

**Network Architecture:** We design a hierarchical equivariant architecture:

1. **Invariant Feature Extraction:** Compute pairwise distances $d_{ij} = \|\mathbf{x}_i - \mathbf{x}_j\|$, angles, and other invariant descriptors.

2. **Equivariant Message Passing:** Use SE(3)-equivariant graph neural networks with steerable features. Node features $h_i^{(\ell)}$ at layer $\ell$ transform as:
$$h_i^{(\ell+1)} = \phi^{(\ell)}\left(h_i^{(\ell)}, \bigoplus_{j \in \mathcal{N}(i)} \psi^{(\ell)}(h_j^{(\ell)}, \mathbf{r}_{ij})\right)$$

where $\mathbf{r}_{ij} = \mathbf{x}_j - \mathbf{x}_i$ and operations use Clebsch-Gordan tensor products for equivariance.

3. **Manifold-Specific Heads:** For each manifold component, dedicated output heads project features to the appropriate tangent space:
   - For $\mathbb{T}^n$: Output $\mathbb{R}^n$ representing angular velocities
   - For SO(3): Output $\mathfrak{so}(3) \cong \mathbb{R}^3$ (Lie algebra)
   - For $\mathbb{R}^3$: Standard translation vectors

### 2.4 Training Objective

The flow matching loss on the product manifold is:
$$\mathcal{L}_{\text{FM}} = \mathbb{E}_{t, z_0, z_1}\left[\sum_{k=1}^{K} \lambda_k \left\| v_\theta^{(k)}(z_t^{(k)}, t; \mathbf{z}_t) - u_t^{(k)}(z_t^{(k)} | z_0^{(k)}, z_1^{(k)}) \right\|_{g_k}^2\right]$$

where $\|\cdot\|_{g_k}$ is the Riemannian norm on $\mathcal{M}_k$, $\lambda_k$ are weighting coefficients, and $t \sim \mathcal{U}[0,1]$.

For optimal transport efficiency, we use mini-batch optimal transport matching on each manifold component independently, then combine assignments. The OT cost on tori uses geodesic distance:
$$c(z, z') = \min_{k \in \mathbb{Z}} |z - z' + 2\pi k|$$

### 2.5 Experimental Design

**Datasets:**
1. **QM9:** Small organic molecules (up to 9 heavy atoms) for benchmarking basic generation quality.
2. **GEOM-Drugs:** Drug-like molecules with multiple conformers, emphasizing torsional flexibility.
3. **GEOM-QM9:** Conformer ensembles for evaluating distribution matching of flexible molecules.

**Baselines:**
- EDM (Equivariant Diffusion Models)
- GeoLDM (Geometric Latent Diffusion)
- Flow Matching in Euclidean space with SE(3)-equivariance
- Torsional Diffusion (specialized for conformer generation)

**Evaluation Metrics:**
1. **Validity:** Percentage of chemically valid molecules (checked via RDKit).
2. **Uniqueness:** Percentage of unique valid molecules.
3. **Novelty:** Percentage of valid molecules not in training set.
4. **FCD (Fréchet ChemNet Distance):** Distribution similarity to reference molecules.
5. **Conformer RMSD:** For flexible molecules, alignment-free RMSD between generated and ground-truth conformer ensembles.
6. **Torsion Distribution Matching:** KL divergence between generated and true dihedral angle distributions.
7. **Sampling Efficiency:** NFE (number of function evaluations) required for generation.

**Ablation Studies:**
- Comparison of geodesic vs. Euclidean interpolants on tori
- Effect of hierarchical decomposition vs. flat Euclidean representation
- Impact of coupling between manifold components in vector field design

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Improved Generation Quality:** We expect EFM-HS to achieve state-of-the-art results on molecular generation benchmarks, with particular improvements on flexible molecule datasets. The explicit modeling of torsional spaces should yield more accurate dihedral angle distributions, improving conformer generation quality by 15-25% in terms of ensemble RMSD.

2. **Guaranteed Equivariance:** By construction, EFM-HS guarantees SE(3) × $S_N$ equivariance, eliminating the need for data augmentation and ensuring consistent behavior under coordinate transformations.

3. **Training Efficiency:** Closed-form optimal transport on individual manifold components (particularly tori and SO(3)) should reduce training time by 30-40% compared to methods requiring numerical OT solvers in high-dimensional Euclidean spaces.

4. **Theoretical Contributions:** The fiber bundle formulation provides a unifying theoretical framework connecting equivariant neural networks, geometric flows, and molecular representations, with potential extensions to other domains (robotics, protein design).

### Broader Impact

**Drug Discovery:** Accurate conformer generation is critical for virtual screening and molecular docking. EFM-HS could accelerate early-stage drug discovery by providing more realistic molecular poses, reducing false positives in binding affinity prediction.

**Protein Design:** The methodology extends naturally to protein backbone generation, where the Ramachandran space ($\mathbb{T}^{2n}$ for $n$ residues) governs backbone conformations. This could impact de novo protein design and antibody engineering.

**Foundational Advances:** This work contributes to the broader agenda of geometry-grounded representation learning, demonstrating how respecting natural geometric structure leads to more effective and principled machine learning models. The framework establishes design patterns for generative modeling on product manifolds applicable beyond molecular systems.