# Research Proposal: Hierarchical Latent Diffusion for Discrete Optimization with Long-Range Dependencies

## 1. Introduction

### Background

Discrete sampling and optimization constitute fundamental problems across numerous scientific and engineering domains, including combinatorial optimization, compiler design, protein engineering, and natural language processing. Unlike their continuous counterparts, discrete optimization problems present unique challenges due to the non-differentiable nature of the search space and the combinatorial explosion of possible configurations. The difficulty intensifies significantly when the objective function exhibits long-range, high-order correlations—a characteristic prevalent in modern language models and biological sequences.

Recent advances have introduced several promising paradigms for discrete sampling and optimization. Gradient-based discrete MCMC methods extend Langevin dynamics to discrete spaces by leveraging gradient information of relaxed objectives. Embedding approaches map discrete structures to continuous representations, perform sampling in the continuous domain, and project solutions back to discrete space. Additionally, methods such as GFlowNets and Stein variational approaches have demonstrated improved efficiency in structured domains. Despite these advances, significant limitations persist. Gradient-based methods frequently become trapped in local modes when facing complex energy landscapes. Continuous embedding approaches often fail to faithfully preserve intricate discrete structural properties. GFlowNets require extensive training data and struggle with black-box objectives where gradient information is unavailable.

The emergence of discrete diffusion models offers a promising direction, as evidenced by recent works on masked diffusion, absorbing-state diffusion, and discrete denoising processes. These methods have shown success in molecular design, text generation, and graph synthesis. However, current discrete diffusion approaches predominantly operate at a single resolution, limiting their ability to capture hierarchical structure and long-range dependencies efficiently.

### Research Objectives

This research proposes a novel **Hierarchical Latent Diffusion (HLD)** framework for discrete optimization that addresses the fundamental challenge of capturing long-range dependencies while maintaining computational efficiency. Our primary objectives are:

1. To develop a multi-scale discrete variational autoencoder (DVAE) that learns hierarchical representations of discrete structures, where coarser levels encode global patterns and finer levels capture local details.

2. To design a hierarchical diffusion sampling mechanism that generates solutions in a coarse-to-fine manner, enabling efficient exploration of the global structure before refining local configurations.

3. To integrate surrogate modeling for black-box objective optimization, allowing gradient-guided refinement across hierarchy levels without requiring differentiable objectives.

4. To validate the framework on challenging benchmarks including combinatorial optimization problems, constrained text generation, and protein fitness landscape optimization.

### Significance

This research bridges a critical gap between the efficiency of continuous diffusion methods and the structural fidelity required for discrete optimization. By introducing hierarchical abstractions, we enable the model to reason about long-range dependencies at appropriate scales, dramatically reducing the effective search space complexity. The framework's ability to handle black-box objectives through learned surrogates extends its applicability to real-world scientific discovery tasks where analytical gradients are unavailable. Success in this endeavor would provide practitioners with a powerful tool for tackling previously intractable discrete optimization problems in drug discovery, materials science, and artificial intelligence.

## 2. Methodology

### 2.1 Overview

The HLD framework consists of three interconnected components: (1) a hierarchical discrete variational autoencoder for learning multi-scale representations, (2) a hierarchical diffusion process for coarse-to-fine sampling, and (3) a surrogate-guided optimization module for black-box objectives. We detail each component below.

### 2.2 Hierarchical Discrete Variational Autoencoder

#### Architecture Design

Let $\mathbf{x} \in \mathcal{V}^N$ denote a discrete sequence of length $N$ over vocabulary $\mathcal{V}$. We construct a hierarchy of $L$ latent levels, where level $l \in \{1, \ldots, L\}$ represents progressively coarser structure. The encoder maps input to hierarchical latents:

$$q_\phi(\mathbf{z}^{1:L} | \mathbf{x}) = \prod_{l=1}^{L} q_\phi(\mathbf{z}^l | \mathbf{z}^{<l}, \mathbf{x})$$

where $\mathbf{z}^l \in \mathcal{V}_l^{N_l}$ represents the discrete latent at level $l$, with $N_l < N_{l-1}$ (coarsening) and potentially different vocabularies $\mathcal{V}_l$.

The coarsening operation employs learned pooling through a transformer-based encoder:

$$\mathbf{h}^l = \text{TransformerEnc}_l(\mathbf{z}^{l-1})$$
$$\mathbf{z}^l = \text{GumbelSoftmax}(\text{Pool}_l(\mathbf{h}^l))$$

where $\text{Pool}_l$ reduces the sequence length by factor $r_l$ (typically 2 or 4) using strided convolutions or learned attention pooling.

The decoder reconstructs finer levels conditioned on coarser ones:

$$p_\theta(\mathbf{x}, \mathbf{z}^{1:L-1} | \mathbf{z}^L) = p_\theta(\mathbf{x} | \mathbf{z}^1) \prod_{l=1}^{L-1} p_\theta(\mathbf{z}^l | \mathbf{z}^{l+1})$$

#### Training Objective

The hierarchical DVAE is trained by maximizing the evidence lower bound (ELBO):

$$\mathcal{L}_{\text{DVAE}} = \mathbb{E}_{q_\phi}[\log p_\theta(\mathbf{x} | \mathbf{z}^{1:L})] - \sum_{l=1}^{L} \beta_l D_{\text{KL}}(q_\phi(\mathbf{z}^l | \cdot) \| p(\mathbf{z}^l | \mathbf{z}^{>l}))$$

where $\beta_l$ controls the information bottleneck at each level, and the prior $p(\mathbf{z}^l | \mathbf{z}^{>l})$ is parameterized by a learned autoregressive model at the coarsest level and conditional models for finer levels.

### 2.3 Hierarchical Diffusion Sampling

#### Discrete Diffusion Formulation

We employ a masked diffusion process at each hierarchy level. For level $l$, the forward process progressively masks tokens:

$$q(\mathbf{z}^l_t | \mathbf{z}^l_0) = \text{Cat}(\mathbf{z}^l_t; \alpha_t \mathbf{z}^l_0 + (1 - \alpha_t) \mathbf{m})$$

where $\mathbf{m}$ is the mask token distribution and $\alpha_t$ follows a cosine schedule from 1 to 0.

The reverse process learns to denoise:

$$p_\psi(\mathbf{z}^l_{t-1} | \mathbf{z}^l_t, \mathbf{z}^{>l}) = \prod_{i=1}^{N_l} \text{Cat}(z^l_{t-1,i}; f_\psi(\mathbf{z}^l_t, \mathbf{z}^{>l}, t)_i)$$

where $f_\psi$ is a transformer network conditioned on the coarser level representation $\mathbf{z}^{>l}$.

#### Hierarchical Sampling Procedure

The coarse-to-fine sampling algorithm proceeds as follows:

**Algorithm 1: Hierarchical Latent Diffusion Sampling**
```
Input: Trained models {f_ψ^l}, decoder p_θ, diffusion steps T
Output: Discrete sample x

1. Sample z^L_T ~ Uniform(mask tokens)
2. For l = L down to 1:
   a. For t = T down to 1:
      z^l_{t-1} ~ p_ψ(z^l_{t-1} | z^l_t, z^{>l})  // Conditional denoising
   b. If l > 1:
      Initialize z^{l-1}_T using upsampled z^l_0 with noise
3. Decode: x = argmax p_θ(x | z^1_0)
Return x
```

The key insight is that coarser levels establish global structure, which then conditions and constrains the refinement at finer levels, dramatically reducing the effective search space.

### 2.4 Surrogate-Guided Optimization for Black-Box Objectives

For black-box objective $f: \mathcal{V}^N \rightarrow \mathbb{R}$, we train a surrogate model $\hat{f}_\omega$ using sparse evaluations:

$$\mathcal{L}_{\text{surrogate}} = \mathbb{E}_{(\mathbf{x}, y) \sim \mathcal{D}}[(\hat{f}_\omega(\mathbf{z}^{1:L}(\mathbf{x})) - y)^2]$$

where the surrogate operates on the hierarchical latent representation for improved generalization.

During optimization, we modify the diffusion sampling to incorporate gradient guidance:

$$\tilde{p}_\psi(\mathbf{z}^l_{t-1} | \mathbf{z}^l_t, \mathbf{z}^{>l}) \propto p_\psi(\mathbf{z}^l_{t-1} | \mathbf{z}^l_t, \mathbf{z}^{>l}) \cdot \exp(\lambda \nabla_{\mathbf{z}^l} \hat{f}_\omega(\mathbf{z}^{1:L}))$$

For discrete gradients, we use the straight-through estimator with Gumbel-softmax relaxation during guidance.

### 2.5 Experimental Design

#### Datasets and Benchmarks

1. **Combinatorial Optimization**: Traveling Salesman Problem (TSP) with 50-500 cities; Maximum Satisfiability (MaxSAT) instances from SAT Competition benchmarks; Maximum Independent Set (MIS) on random graphs.

2. **Constrained Text Generation**: CommonGen benchmark for constrained sentence generation; poetry generation with structural constraints (rhyme, meter).

3. **Protein Optimization**: GFP fluorescence landscape; AAV capsid fitness optimization; stability prediction on ProteinGym benchmarks.

#### Baseline Methods

We compare against: (1) Gradient-based discrete MCMC (Gibbs-with-Gradients, DMALA); (2) GFlowNet with various architectures; (3) Standard discrete diffusion (D3PM, MDLM); (4) Simulated annealing and genetic algorithms; (5) Recent methods including DRAKES and scalable discrete diffusion samplers.

#### Evaluation Metrics

- **Optimization Quality**: Best objective value found, optimality gap (for problems with known optima), area under convergence curve
- **Sample Quality**: Validity rate, diversity (pairwise distance), novelty relative to training data
- **Efficiency**: Wall-clock time to reach target objective, number of function evaluations
- **Long-range Dependency Capture**: Mutual information between distant positions, perplexity on held-out sequences

#### Implementation Details

- Hierarchy depth $L = 3$ with coarsening ratios $[4, 4, 4]$
- Transformer architectures with 6 layers, 8 heads, 512 hidden dimensions per level
- Diffusion steps $T = 100$ with cosine noise schedule
- Training: AdamW optimizer, learning rate $10^{-4}$, batch size 128
- Surrogate model: Ensemble of 5 neural networks for uncertainty quantification

## 3. Expected Outcomes & Impact

### Expected Outcomes

We anticipate the following quantitative improvements:

1. **Convergence Speed**: 3-5× faster convergence on TSP and MaxSAT benchmarks compared to standard discrete diffusion and GFlowNet baselines, measured by iterations to reach 95% of optimal objective value.

2. **Solution Quality**: 5-10% improvement in best-found solutions for large-scale combinatorial problems (TSP-500, MaxSAT with 10K+ clauses) where existing methods struggle with long-range dependencies.

3. **Sample Diversity**: 2× higher diversity in constrained text generation tasks while maintaining comparable or better constraint satisfaction rates.

4. **Black-Box Optimization**: Competitive performance on protein fitness landscapes using 10× fewer function evaluations than Bayesian optimization baselines.

5. **Scalability**: Linear scaling with sequence length due to hierarchical factorization, enabling application to problems with thousands of discrete variables.

### Scientific Impact

This research contributes to multiple scientific fronts:

1. **Theoretical Advancement**: We provide a principled framework for incorporating multi-scale structure into discrete diffusion models, with analysis of how hierarchical decomposition affects mixing times and mode coverage.

2. **Methodological Innovation**: The integration of learned hierarchical representations with diffusion sampling creates a new paradigm applicable beyond the specific applications studied.

3. **Practical Tools**: Open-source implementation will enable practitioners to apply these methods to domain-specific discrete optimization challenges.

### Broader Impact

The ability to efficiently optimize discrete structures with long-range dependencies has profound implications:

- **Drug Discovery**: Accelerated optimization of molecular structures and protein sequences could reduce development timelines for therapeutics.
- **Materials Science**: Design of novel materials with targeted properties through discrete structure optimization.
- **AI Systems**: Improved discrete optimization underpins advances in program synthesis, neural architecture search, and compiler optimization.
- **Scientific Discovery**: General-purpose discrete optimization tools enable hypothesis generation and experimental design in data-limited regimes.

### Limitations and Future Directions

We acknowledge potential limitations: the hierarchical structure requires domain-appropriate design choices; training the DVAE requires substantial data; and surrogate model uncertainty may lead to over-optimization. Future work will explore adaptive hierarchy learning, active learning for surrogate improvement, and theoretical analysis of convergence guarantees under the hierarchical framework.

In conclusion, this research addresses a fundamental challenge in discrete optimization by introducing hierarchical structure into diffusion-based methods. The proposed framework promises significant improvements in handling long-range dependencies while maintaining computational tractability, with broad applications across science and engineering.