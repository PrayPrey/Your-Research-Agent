# Research Proposal: Hierarchical Flow Matching for Scalable Boltzmann Sampling of Large Proteins

## 1. Introduction

### 1.1 Background

Sampling from Boltzmann distributions lies at the heart of computational biophysics and drug discovery. The Boltzmann distribution $p(\mathbf{x}) \propto \exp(-E(\mathbf{x})/k_BT)$ describes the equilibrium probability of molecular configurations $\mathbf{x}$ at temperature $T$, where $E(\mathbf{x})$ is the potential energy and $k_B$ is Boltzmann's constant. Accurate sampling from this distribution enables computation of thermodynamic quantities such as free energies, binding affinities, and conformational populations—all critical for understanding protein function and designing therapeutics.

Traditional approaches to Boltzmann sampling rely on Molecular Dynamics (MD) simulations or Markov Chain Monte Carlo (MCMC) methods. While theoretically exact, these methods suffer from critical slowing down: the autocorrelation time grows dramatically with system size, requiring prohibitively long simulations to adequately sample conformational space. For proteins of therapeutic interest (typically 2,000-20,000 atoms), obtaining converged equilibrium samples can require milliseconds of simulation time—computationally equivalent to months or years of GPU time.

Recent advances in machine learning have introduced Boltzmann Generators (BGs), which learn to directly sample from target distributions using normalizing flows or diffusion models. These approaches train generative models on MD trajectories and use importance reweighting to correct for imperfect learning, enabling exact thermodynamic calculations. State-of-the-art methods like Sequential Boltzmann Generators combine flow-based sampling with Sequential Monte Carlo (SMC) and achieve impressive efficiency on small peptides (~100 atoms). However, a critical scalability gap remains: current methods fail to maintain reasonable Effective Sample Size (ESS) as system size increases beyond a few hundred atoms, precisely where biological applications become most relevant.

### 1.2 Research Objectives

This research proposes **Hierarchical Conditional Flow Matching for Boltzmann Generators (HCFM-BG)**, a novel approach that addresses the scalability challenge through principled hierarchical decomposition. Our primary objectives are:

1. **Develop a hierarchical factorization framework** that decomposes Boltzmann sampling into $P(\text{backbone}) \times P(\text{all-atom}|\text{backbone})$, exploiting the natural separation of timescales in protein dynamics.

2. **Design SE(3)-equivariant flow matching architectures** for both backbone and conditional all-atom generation that respect the geometric symmetries of molecular systems.

3. **Establish rigorous importance reweighting schemes** that correct factorization approximation errors while maintaining statistically efficient sampling.

4. **Demonstrate scalability** to protein systems of 5,000-10,000 atoms with ESS/GPU-hour exceeding 5%, where current baselines achieve less than 1%.

### 1.3 Significance

Successfully addressing the scalability barrier in Boltzmann sampling would have transformative implications:

- **Drug Discovery:** Enable accurate binding free energy calculations for drug-protein complexes, currently limited by sampling convergence.
- **Protein Engineering:** Allow thermodynamic characterization of designed proteins without prohibitive MD simulations.
- **Fundamental Science:** Provide insights into protein folding landscapes and allosteric mechanisms for large, therapeutically relevant systems.

Our hierarchical approach represents a paradigm shift from single-scale methods, potentially enabling a 10-fold increase in tractable system size while maintaining thermodynamic rigor.

## 2. Methodology

### 2.1 Theoretical Framework

#### 2.1.1 Hierarchical Factorization

We decompose the Boltzmann distribution over all-atom coordinates $\mathbf{x} \in \mathbb{R}^{3N}$ into a hierarchical product:

$$p(\mathbf{x}) = p(\mathbf{x}_{\text{bb}}) \cdot p(\mathbf{x}_{\text{sc}} | \mathbf{x}_{\text{bb}})$$

where $\mathbf{x}_{\text{bb}} \in \mathbb{R}^{3N_{\text{bb}}}$ represents backbone coordinates (C$_\alpha$, C, N, O atoms) and $\mathbf{x}_{\text{sc}}$ represents side-chain coordinates. This factorization is motivated by the timescale separation in protein dynamics: backbone motions occur on microsecond-millisecond timescales, while side-chain rotameric transitions occur on nanosecond timescales.

The key insight is that learning $p(\mathbf{x}_{\text{bb}})$ in a reduced-dimensional space ($\sim$4 atoms per residue vs. $\sim$15 average) dramatically simplifies the sampling problem, while the conditional distribution $p(\mathbf{x}_{\text{sc}} | \mathbf{x}_{\text{bb}})$ is inherently simpler due to the constrained local environment.

#### 2.1.2 Flow Matching Formulation

We employ Conditional Flow Matching (CFM) to learn both distributions. For a target distribution $p(\mathbf{x})$, CFM learns a time-dependent velocity field $v_\theta(\mathbf{x}, t)$ that transports samples from a simple prior $p_0(\mathbf{x})$ (e.g., Gaussian) to the target. The training objective is:

$$\mathcal{L}_{\text{CFM}}(\theta) = \mathbb{E}_{t \sim \mathcal{U}[0,1], \mathbf{x}_0 \sim p_0, \mathbf{x}_1 \sim p_{\text{data}}} \left[ \| v_\theta(\mathbf{x}_t, t) - u_t(\mathbf{x}_t | \mathbf{x}_0, \mathbf{x}_1) \|^2 \right]$$

where $\mathbf{x}_t = (1-t)\mathbf{x}_0 + t\mathbf{x}_1$ is the linear interpolation and $u_t = \mathbf{x}_1 - \mathbf{x}_0$ is the conditional velocity.

#### 2.1.3 SE(3)-Equivariance

Molecular systems possess rotational and translational symmetry. We enforce SE(3)-equivariance in our flow networks:

$$v_\theta(R\mathbf{x} + \mathbf{t}, t) = R \cdot v_\theta(\mathbf{x}, t)$$

for any rotation $R \in SO(3)$ and translation $\mathbf{t} \in \mathbb{R}^3$. This is achieved using equivariant graph neural networks (EGNNs) that operate on invariant features (distances, angles) and equivariant vectors (positions, velocities).

#### 2.1.4 Importance Reweighting for Exactness

The learned distribution $q_\theta(\mathbf{x})$ approximates but does not exactly match $p(\mathbf{x})$. We correct this via importance reweighting:

$$w(\mathbf{x}) = \frac{p(\mathbf{x})}{q_\theta(\mathbf{x})} = \frac{\exp(-E(\mathbf{x})/k_BT)}{Z \cdot q_\theta(\mathbf{x})}$$

For hierarchical sampling, the weight factorizes as:

$$w(\mathbf{x}) = \frac{p(\mathbf{x}_{\text{bb}})}{q_\theta^{(1)}(\mathbf{x}_{\text{bb}})} \cdot \frac{p(\mathbf{x}_{\text{sc}}|\mathbf{x}_{\text{bb}})}{q_\theta^{(2)}(\mathbf{x}_{\text{sc}}|\mathbf{x}_{\text{bb}})}$$

The Effective Sample Size quantifies sampling efficiency:

$$\text{ESS} = \frac{(\sum_i w_i)^2}{\sum_i w_i^2}$$

### 2.2 Algorithm Design

#### 2.2.1 Two-Stage Training Pipeline

**Stage 1: Backbone Flow ($q_\theta^{(1)}$)**

1. Extract backbone coordinates $\{\mathbf{x}_{\text{bb}}^{(i)}\}$ from MD trajectories
2. Center and align structures to remove global translation/rotation
3. Train SE(3)-equivariant flow matching network:
   - Architecture: EGNN with 8 layers, 256 hidden dimensions
   - Input: Backbone atom positions + residue type embeddings
   - Output: Velocity field $v_\theta^{(1)}(\mathbf{x}_{\text{bb}}, t)$
4. Compute log-likelihood via ODE integration:
   $$\log q_\theta^{(1)}(\mathbf{x}_{\text{bb}}) = \log p_0(\mathbf{x}_0) - \int_0^1 \nabla \cdot v_\theta^{(1)}(\mathbf{x}_t, t) dt$$

**Stage 2: Conditional All-Atom Flow ($q_\theta^{(2)}$)**

1. For each backbone configuration, extract corresponding side-chain coordinates
2. Train conditional SE(3)-equivariant flow:
   - Input: Side-chain positions + backbone context (fixed)
   - Conditioning: Backbone coordinates via cross-attention
   - Output: Conditional velocity $v_\theta^{(2)}(\mathbf{x}_{\text{sc}}, t | \mathbf{x}_{\text{bb}})$

**Algorithm 1: HCFM-BG Training**
```
Input: MD trajectory {x^(i)}, energy function E(x), temperature T
Output: Trained flows θ₁, θ₂

# Stage 1: Backbone Flow
for epoch in 1...N_epochs:
    Sample batch {x_bb^(i)} from trajectory
    Sample t ~ U[0,1], x₀ ~ N(0,I)
    x_t = (1-t)x₀ + t·x_bb
    L₁ = ||v_θ₁(x_t, t) - (x_bb - x₀)||²
    Update θ₁ via gradient descent

# Stage 2: Conditional Flow  
for epoch in 1...N_epochs:
    Sample batch {(x_bb^(i), x_sc^(i))}
    Sample t ~ U[0,1], x₀ ~ N(0,I)
    x_t = (1-t)x₀ + t·x_sc
    L₂ = ||v_θ₂(x_t, t | x_bb) - (x_sc - x₀)||²
    Update θ₂ via gradient descent
```

#### 2.2.2 Sampling and Reweighting

**Algorithm 2: HCFM-BG Sampling**
```
Input: Trained flows θ₁, θ₂, number of samples M
Output: Weighted samples {(x^(i), w^(i))}

for i in 1...M:
    # Stage 1: Sample backbone
    x₀ ~ N(0, I)
    x_bb = ODESolve(v_θ₁, x₀, t: 0→1)
    log_q₁ = ComputeLogLikelihood(x_bb, θ₁)
    
    # Stage 2: Sample side-chains conditioned on backbone
    x₀ ~ N(0, I)  
    x_sc = ODESolve(v_θ₂(·|x_bb), x₀, t: 0→1)
    log_q₂ = ComputeLogLikelihood(x_sc|x_bb, θ₂)
    
    # Combine and compute weight
    x^(i) = Combine(x_bb, x_sc)
    log_w^(i) = -E(x^(i))/(k_B·T) - log_q₁ - log_q₂
    
return {(x^(i), exp(log_w^(i)))}
```

### 2.3 Experimental Design

#### 2.3.1 Data Collection

**Training Data:**
- Generate MD trajectories using OpenMM with AMBER ff14SB force field
- Temperature: 300K with Langevin integrator
- Systems: Curated set of globular proteins spanning 100-10,000 atoms
  - Small: Chignolin (138 atoms), Trp-cage (304 atoms)
  - Medium: Villin headpiece (596 atoms), BBA (1,012 atoms)
  - Large: Ubiquitin (1,231 atoms), Lysozyme (2,023 atoms)
  - Very Large: DHFR (5,124 atoms), Adenylate kinase (7,892 atoms)
- Simulation length: 10 μs per system (aggregated from multiple replicas)
- Sampling interval: 10 ps (1M frames per system)

**Validation Data:**
- Hold out 20% of trajectory for validation
- Independent long MD runs (100 μs) for ground-truth free energy estimates

#### 2.3.2 Baseline Methods

1. **Sequential Boltzmann Generator (Sequential BG):** Current state-of-the-art combining normalizing flows with SMC
2. **Single-scale Flow Matching:** Non-hierarchical CFM baseline
3. **Transferable Boltzmann Generator:** Pre-trained flow with fine-tuning
4. **Enhanced Sampling MD:** Replica Exchange MD (REMD) as traditional baseline

#### 2.3.3 Evaluation Metrics

**Primary Metrics:**
- **ESS/GPU-hour:** Effective Sample Size normalized by computational cost
  $$\text{ESS/GPU-hour} = \frac{\text{ESS}}{N_{\text{samples}}} \times \frac{N_{\text{samples}}}{\text{GPU-hours}}$$

- **Free Energy RMSE:** Root mean square error vs. long MD reference
  $$\text{RMSE}_{\Delta G} = \sqrt{\frac{1}{K}\sum_{k=1}^K (\Delta G_k^{\text{pred}} - \Delta G_k^{\text{ref}})^2}$$

**Secondary Metrics:**
- **KL Divergence:** $D_{\text{KL}}(q_\theta \| p)$ estimated via importance sampling
- **Ramachandran Agreement:** Distribution overlap in $(\phi, \psi)$ space
- **Contact Map Correlation:** Pearson correlation of residue-residue contact frequencies

#### 2.3.4 Statistical Analysis

- **Sample Size:** n ≥ 20 independent runs per condition
- **Hypothesis Testing:** Paired t-test comparing HCFM-BG vs. baselines (α = 0.05, one-tailed)
- **Effect Size:** Cohen's d with 95% confidence intervals
- **Scaling Analysis:** Log-log regression of ESS vs. system size

### 2.4 Implementation Details

- **Framework:** PyTorch with PyTorch Geometric for graph operations
- **Hardware:** 8× NVIDIA A100 GPUs (80GB)
- **Training:** AdamW optimizer, learning rate 1e-4, cosine annealing
- **ODE Solver:** Dormand-Prince (dopri5) with adaptive step size
- **Energy Evaluation:** OpenMM for force field calculations

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1 - Scalability):**
We expect HCFM-BG to achieve ESS/GPU-hour > 5% for protein systems with 5,000-10,000 atoms, representing a >5× improvement over Sequential BG baselines that achieve <1% ESS at this scale. The hierarchical factorization should reduce effective dimensionality from $O(3N)$ to $O(3N_{\text{bb}}) + O(3N_{\text{sc}}|N_{\text{bb}})$, enabling tractable learning.

**Secondary Outcome (P2 - Thermodynamic Accuracy):**
Free energy estimates should match long MD references within 1 kT RMSE, validating that importance reweighting successfully corrects factorization approximation errors.

**Tertiary Outcome (P3 - Scaling Behavior):**
The performance advantage of hierarchical over single-scale approaches should increase monotonically with system size, confirming that our method specifically addresses the scalability bottleneck rather than providing uniform improvement.

### 3.2 Potential Challenges and Mitigations

1. **Weight Variance Explosion:** If importance weights exhibit high variance, ESS will collapse. Mitigation: Implement adaptive tempering and weight clipping; explore annealed importance sampling.

2. **Conditional Distribution Complexity:** Side-chain distributions may be more complex than anticipated for certain residue types. Mitigation: Use residue-type-specific conditional flows or mixture models.

3. **Training Data Requirements:** Large proteins may require extensive MD data. Mitigation: Leverage transfer learning from smaller systems; explore data augmentation via symmetry operations.

### 3.3 Broader Impact

**Scientific Impact:**
- Enable thermodynamic characterization of therapeutically relevant proteins previously intractable
- Provide a general framework for hierarchical decomposition applicable beyond proteins (e.g., nucleic acids, polymers)
- Advance understanding of connections between optimal transport, flow matching, and statistical mechanics

**Practical Applications:**
- Accelerate drug discovery pipelines through accurate binding affinity predictions
- Enable rational protein engineering with thermodynamic guidance
- Reduce computational costs for pharmaceutical R&D

**Community Contributions:**
- Open-source implementation with pre-trained models
- Benchmark suite for evaluating Boltzmann sampling methods at scale
- Training datasets and evaluation protocols for reproducibility

### 3.4 Limitations and Future Directions

This work focuses on folded globular proteins at equilibrium. Extensions to intrinsically disordered proteins, membrane proteins, and non-equilibrium dynamics represent important future directions. Additionally, integration with enhanced sampling techniques (e.g., metadynamics) and extension to protein-ligand complexes would further expand applicability.

In conclusion, HCFM-BG represents a principled approach to overcoming the scalability barrier in Boltzmann sampling, with potential to transform computational biophysics and drug discovery by enabling accurate thermodynamic calculations for large, therapeutically relevant protein systems.