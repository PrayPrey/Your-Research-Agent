# Research Proposal: Physics-Informed Active Learning for Multi-Fidelity Materials Discovery

## 1. Introduction

### Background

Materials discovery represents one of the most impactful applications of machine learning in the physical sciences, with profound implications for energy storage, catalysis, electronics, and sustainable technologies. The discovery pipeline typically involves evaluating material candidates across multiple fidelity levels: rapid screening methods like classical force fields, intermediate-accuracy density functional theory (DFT) calculations, high-accuracy quantum chemistry methods (e.g., coupled cluster), and ultimately physical synthesis and experimental characterization. Each fidelity level offers a different trade-off between computational/experimental cost and predictive accuracy—low-fidelity methods can screen thousands of candidates cheaply but with significant errors, while high-fidelity evaluations provide ground truth but at costs that limit throughput to dozens of candidates.

Current approaches to this multi-fidelity optimization challenge suffer from a fundamental disconnect. Standard multi-fidelity Bayesian optimization methods, while theoretically principled, treat the correlation structure between fidelity levels as purely statistical, ignoring the rich physical knowledge that governs material properties. Simultaneously, physics-informed machine learning approaches have demonstrated the power of incorporating domain knowledge but typically operate at single fidelity levels. This gap leads to inefficient exploration strategies that waste precious high-fidelity evaluations on candidates that violate known physical constraints or fail to exploit predictable relationships between fidelity levels.

### Research Objectives

This research proposes a unified framework—Physics-Informed Multi-Fidelity Active Learning (PIMFAL)—that jointly addresses three interconnected challenges:

1. **Joint sample-fidelity selection**: Developing an acquisition strategy that simultaneously determines which material candidates to evaluate and at which fidelity level, optimizing the information-to-cost ratio across the entire experimental campaign.

2. **Physics-constrained surrogate modeling**: Constructing Gaussian process surrogates with kernels that encode known physical relationships (symmetries, conservation laws, thermodynamic bounds) to dramatically reduce the effective search space.

3. **Physically-grounded fidelity transfer**: Leveraging domain knowledge about systematic biases between fidelity levels to improve the correlation structure and enable more efficient propagation of information from low to high fidelity.

### Significance

This research addresses a critical gap between theoretical advances in active learning and practical needs in materials discovery pipelines. Success would enable:

- **Accelerated discovery**: Achieving target material properties with 3-5× fewer high-fidelity evaluations, translating to substantial cost and time savings in real discovery campaigns.
- **Resource optimization**: Intelligent allocation of computational and experimental budgets across fidelity levels based on principled information-theoretic criteria.
- **Broader applicability**: A framework that generalizes across material systems by incorporating physics at a fundamental level rather than relying on system-specific heuristics.

## 2. Methodology

### 2.1 Problem Formulation

Consider a materials design problem where we seek to optimize an objective function $f^*: \mathcal{X} \rightarrow \mathbb{R}$ over a design space $\mathcal{X} \subseteq \mathbb{R}^d$ representing material compositions or structural parameters. We have access to $M$ fidelity levels with evaluation functions $\{f_1, f_2, \ldots, f_M\}$ ordered by increasing accuracy and cost, where $f_M \approx f^*$. Each evaluation at fidelity $m$ incurs cost $\lambda_m$, with $\lambda_1 \ll \lambda_2 \ll \cdots \ll \lambda_M$. Additionally, we possess physics-based constraints $\mathcal{C} = \{c_1, \ldots, c_K\}$ that valid material candidates must satisfy.

Our goal is to identify $x^* = \arg\max_{x \in \mathcal{X}} f^*(x)$ while minimizing total evaluation cost $\sum_{t=1}^T \lambda_{m_t}$, where $(x_t, m_t)$ denotes the candidate and fidelity selected at iteration $t$.

### 2.2 Physics-Informed Multi-Fidelity Gaussian Process Surrogate

We model the multi-fidelity objective using a hierarchical Gaussian process with physics-informed kernels. For each fidelity level $m$, we define:

$$f_m(x) = \rho_m(x) f_{m-1}(x) + \delta_m(x)$$

where $\rho_m(x)$ captures the (potentially input-dependent) correlation between adjacent fidelity levels, and $\delta_m(x)$ represents the fidelity-specific residual. The base function $f_0(x)$ is assigned a GP prior with physics-informed kernel $k_0$.

**Physics-Informed Kernel Design**: We construct the kernel $k_0$ to encode known physical constraints:

1. **Symmetry constraints**: For materials with compositional symmetries (e.g., $A_xB_{1-x}$ binary alloys), we use permutation-invariant kernels:
$$k_{\text{sym}}(x, x') = \frac{1}{|\mathcal{G}|} \sum_{g \in \mathcal{G}} k_{\text{base}}(gx, x')$$
where $\mathcal{G}$ is the symmetry group.

2. **Convexity constraints**: For properties like formation energies that must be convex in composition space, we incorporate second-derivative constraints through constrained GP inference.

3. **Physical bounds**: We encode thermodynamic bounds (e.g., non-negative elastic moduli) using warped GPs:
$$f_m(x) = \phi^{-1}(g_m(x))$$
where $\phi$ maps to the physically valid range and $g_m \sim \mathcal{GP}$.

**Physically-Grounded Fidelity Correlation**: Rather than learning $\rho_m(x)$ purely from data, we parameterize it using known systematic biases:

$$\rho_m(x) = \rho_m^0 + \sum_{j=1}^J \beta_{mj} \psi_j(x)$$

where $\psi_j(x)$ are physics-motivated basis functions capturing known error patterns (e.g., DFT's systematic underbinding of van der Waals interactions in certain chemical environments).

### 2.3 Physics-Constrained Multi-Fidelity Acquisition Function

We develop a novel acquisition function that balances information gain against fidelity costs while respecting physical constraints. Our approach extends the multi-fidelity predictive entropy search framework with constraint handling.

**Information-Cost Ratio Acquisition**: For candidate $(x, m)$, we define:

$$\alpha(x, m) = \frac{I(f^*(x^*); y_m(x) | \mathcal{D}_t)}{\lambda_m} \cdot \mathbb{P}(x \in \mathcal{F} | \mathcal{D}_t)$$

where $I(\cdot; \cdot | \mathcal{D}_t)$ denotes the conditional mutual information about the optimum location given current data $\mathcal{D}_t$, and $\mathbb{P}(x \in \mathcal{F} | \mathcal{D}_t)$ is the posterior probability that $x$ lies in the feasible region $\mathcal{F}$ defined by physical constraints.

**Efficient Computation**: Direct computation of the mutual information is intractable. We employ an approximation based on expected improvement in the posterior over the optimum:

$$I(f^*(x^*); y_m(x) | \mathcal{D}_t) \approx H[p(x^* | \mathcal{D}_t)] - \mathbb{E}_{y_m(x)}[H[p(x^* | \mathcal{D}_t, y_m(x))]]$$

We approximate this using Thompson sampling: draw $S$ samples from the posterior GP, identify the optimum for each sample, and compute the entropy reduction.

**Constraint Probability Estimation**: The feasibility probability incorporates both explicit constraints and physics-derived soft constraints:

$$\mathbb{P}(x \in \mathcal{F} | \mathcal{D}_t) = \prod_{k=1}^K \Phi\left(\frac{c_k^{\max} - \mu_{c_k}(x)}{\sigma_{c_k}(x)}\right)$$

where $\mu_{c_k}$ and $\sigma_{c_k}$ are posterior mean and standard deviation for constraint function $c_k$, and $\Phi$ is the standard normal CDF.

### 2.4 Algorithm: PIMFAL

```
Algorithm: Physics-Informed Multi-Fidelity Active Learning (PIMFAL)
Input: Design space X, fidelity levels M, costs {λ_m}, physics constraints C, budget B
Output: Best candidate x* and predicted optimal value

1. Initialize with space-filling design at lowest fidelity: D_1 ← LHS(X, n_init)
2. Evaluate initial points: y_1 ← {f_1(x) : x ∈ D_1}
3. Initialize total cost: cost ← n_init × λ_1
4. While cost < B:
   a. Fit physics-informed multi-fidelity GP to all data D_t = ∪_m D_m
   b. For each candidate x ∈ X_candidate and fidelity m ∈ {1,...,M}:
      i. Compute information gain I(x,m) via Thompson sampling
      ii. Compute feasibility probability P(x ∈ F)
      iii. Compute acquisition: α(x,m) = I(x,m) × P(x ∈ F) / λ_m
   c. Select (x_t, m_t) = argmax α(x,m)
   d. Evaluate y_t = f_{m_t}(x_t)
   e. Update: D_{m_t} ← D_{m_t} ∪ {(x_t, y_t)}, cost ← cost + λ_{m_t}
   f. Update physics-based fidelity correlations using domain knowledge
5. Return x* = argmax_x μ_M(x | D_t)
```

### 2.5 Experimental Design and Validation

**Benchmark Problems**:

1. **Battery Electrolyte Design**: Optimize ionic conductivity across a 5-dimensional space of salt concentrations and solvent ratios. Fidelity levels: classical molecular dynamics ($\lambda_1 = 1$), reactive force fields ($\lambda_2 = 10$), DFT-MD ($\lambda_3 = 100$). Physics constraints: electroneutrality, solubility limits.

2. **Catalyst Surface Design**: Identify optimal adsorption energies for hydrogen evolution reaction across bimetallic surfaces. Fidelity levels: scaling relations ($\lambda_1 = 0.1$), GGA-DFT ($\lambda_2 = 1$), hybrid functional DFT ($\lambda_3 = 50$). Physics constraints: d-band model relationships, Sabatier principle bounds.

3. **Alloy Composition Optimization**: Maximize hardness in quaternary alloy systems. Fidelity levels: CALPHAD ($\lambda_1 = 0.01$), DFT ($\lambda_2 = 1$), experimental synthesis ($\lambda_3 = 1000$). Physics constraints: Vegard's law, convex hull stability.

**Baselines**:
- Standard multi-fidelity BO (MF-GP-UCB)
- Single-fidelity BO at each level
- Random multi-fidelity sampling
- Physics-informed single-fidelity BO

**Evaluation Metrics**:
1. **Sample efficiency**: Number of high-fidelity evaluations to reach within $\epsilon$ of the true optimum
2. **Cost efficiency**: Total cost to achieve target performance, $\sum_t \lambda_{m_t}$
3. **Constraint satisfaction rate**: Fraction of selected candidates satisfying physical constraints
4. **Inference quality**: RMSE and calibration of the final surrogate model

**Statistical Validation**: All experiments will be repeated with 20 random seeds, reporting mean and 95% confidence intervals. We will conduct ablation studies isolating the contribution of: (a) physics-informed kernels, (b) constrained acquisition, and (c) physically-grounded fidelity transfer.

## 3. Expected Outcomes & Impact

### Expected Outcomes

**Quantitative Results**:
- 3-5× reduction in high-fidelity evaluations required to identify optimal candidates across all benchmark problems
- 2-3× improvement in total cost efficiency compared to standard multi-fidelity BO
- >95% constraint satisfaction rate for physics-feasible candidates, compared to ~60-70% for unconstrained methods
- Improved surrogate calibration with 20-30% reduction in RMSE through physics-informed priors

**Methodological Contributions**:
- A unified framework for joint sample-fidelity selection with physics constraints
- Novel physics-informed kernel constructions for common material property relationships
- Theoretical analysis connecting physics-based constraint incorporation to reduced sample complexity
- Open-source implementation integrated with existing materials simulation workflows

### Broader Impact

**Scientific Impact**: This work bridges the gap between principled active learning theory and practical materials discovery, addressing a key barrier identified in the workshop's focus on "missing links that hinder direct application of principled research ideas into practically relevant solutions."

**Practical Applications**: The framework directly enables acceleration of discovery campaigns for:
- Next-generation battery materials for energy storage
- Efficient catalysts for green hydrogen production
- Novel alloys for aerospace and automotive applications

**Community Resources**: We will release:
- Modular Python library implementing PIMFAL
- Benchmark datasets with multi-fidelity evaluations
- Tutorials connecting to common materials simulation codes (VASP, Quantum ESPRESSO, LAMMPS)

**Future Directions**: This research opens avenues for:
- Extension to batch multi-fidelity active learning for parallel experimental facilities
- Integration with foundation models for materials as physics-informed priors
- Application to other domains requiring multi-fidelity optimization (drug design, robotics)

By developing methods that respect physical reality while maintaining theoretical rigor, this work exemplifies the workshop's goal of advancing adaptive experimental design for real-world scientific discovery.