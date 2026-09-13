# Physics-Informed Neural Acquisition Functions for Safe Multi-Fidelity Bayesian Optimization in Materials Design

## 1. Introduction

### Background

Materials design represents one of the most challenging domains for experimental optimization, where the discovery of novel materials with desired properties requires navigating vast design spaces under stringent safety and cost constraints. Traditional experimental approaches involve expensive laboratory tests that can cost thousands of dollars per sample and may pose safety hazards when exploring unknown regions of the chemical or structural space. While computational simulations offer cheaper alternatives, they exist across multiple fidelity levels—from fast but approximate density functional theory (DFT) calculations to expensive but accurate molecular dynamics simulations—each providing different trade-offs between accuracy and computational cost.

Bayesian Optimization (BO) has emerged as a powerful framework for sample-efficient optimization in expensive black-box settings. However, standard BO methods face critical limitations when applied to real-world materials design: (1) they treat the optimization problem as purely data-driven, ignoring well-established physical laws and domain knowledge; (2) they struggle to effectively balance information from multiple simulation fidelities; and (3) they lack principled mechanisms to enforce safety constraints that prevent proposing potentially hazardous or physically impossible experimental conditions.

Recent advances in physics-informed neural networks (PINNs) have demonstrated the value of embedding domain knowledge directly into neural architectures, while multi-fidelity optimization methods have shown promise in leveraging hierarchical information sources. However, these advances have remained largely disconnected from the safety-critical requirements of real-world materials experimentation. The integration of physics-based constraints, multi-fidelity information fusion, and safety guarantees within a unified acquisition function framework remains an open challenge.

### Research Objectives

This research proposes a novel framework for **Physics-Informed Neural Acquisition Functions for Safe Multi-Fidelity Bayesian Optimization** with the following specific objectives:

1. **Develop physics-informed surrogate models** that embed fundamental physical laws (thermodynamic constraints, conservation principles, stability conditions) as differentiable neural network components, ensuring all proposed experiments respect domain knowledge.

2. **Design multi-fidelity risk-aware acquisition functions** that jointly optimize expected improvement across simulation fidelities while maintaining probabilistic safety certificates derived from physical models.

3. **Create adaptive constraint learning mechanisms** that actively refine safety boundaries through strategic querying of low-fidelity simulations before committing to expensive high-fidelity experiments.

4. **Validate the framework** on real-world materials design problems, specifically battery electrolyte optimization and catalyst design, demonstrating substantial cost reductions while maintaining safety guarantees.

### Significance

This research addresses a critical gap between theoretical Bayesian optimization and practical materials science applications. The expected contributions include:

- **Theoretical advancement**: A principled framework for incorporating physics-based constraints into acquisition functions with provable safety guarantees and convergence properties.

- **Practical impact**: Demonstrated 50% reduction in experimental costs while maintaining safety, enabling faster materials discovery in high-impact applications such as renewable energy storage and sustainable catalysis.

- **Methodological innovation**: A unified approach that bridges physics-informed machine learning, multi-fidelity optimization, and safe exploration, applicable across diverse scientific domains including drug design, protein engineering, and robotics.

- **Broader implications**: Accelerating the adoption of AI-driven experimental design in safety-critical scientific domains by providing trustworthy, interpretable, and efficient optimization strategies.

## 2. Methodology

### 2.1 Problem Formulation

We formulate the materials design problem as a safe multi-fidelity Bayesian optimization task. Let $\mathbf{x} \in \mathcal{X} \subset \mathbb{R}^d$ represent a material design (e.g., composition ratios, processing parameters), where $\mathcal{X}$ is the design space. We have access to $M$ information sources with varying fidelities:

$$f^{(m)}: \mathcal{X} \rightarrow \mathbb{R}, \quad m = 1, \ldots, M$$

where $f^{(M)}$ represents the true expensive experimental objective (highest fidelity), and $f^{(m)}$ for $m < M$ represent computational simulations of decreasing cost and accuracy. Each evaluation at fidelity $m$ has cost $c^{(m)}$ with $c^{(1)} \ll c^{(2)} \ll \cdots \ll c^{(M)}$.

Additionally, we define a set of safety constraints derived from physical principles:

$$g_i(\mathbf{x}) \geq 0, \quad i = 1, \ldots, K$$

where violations may indicate physically impossible states or hazardous conditions (e.g., thermodynamic instability, explosive compositions, toxic byproducts).

**Optimization objective**: Find $\mathbf{x}^* = \arg\max_{\mathbf{x} \in \mathcal{X}} f^{(M)}(\mathbf{x})$ subject to $g_i(\mathbf{x}) \geq 0$ for all $i$, while minimizing total experimental cost.

### 2.2 Physics-Informed Surrogate Model Architecture

#### 2.2.1 Neural Network Design

We propose a composite neural network architecture that combines data-driven learning with physics-based constraints:

$$\hat{f}(\mathbf{x}) = \text{NN}_{\text{data}}(\mathbf{x}) + \lambda \cdot \text{NN}_{\text{physics}}(\mathbf{x}, \boldsymbol{\theta})$$

where $\text{NN}_{\text{data}}$ is a standard Gaussian process or deep kernel learning model for capturing empirical patterns, and $\text{NN}_{\text{physics}}$ enforces physical constraints through differentiable layers. The parameter $\lambda$ controls the relative weighting, which is adaptively adjusted during optimization.

#### 2.2.2 Physics-Informed Layers

We embed domain knowledge through specialized neural layers:

**Thermodynamic consistency layer**: For materials design, we enforce energy conservation and thermodynamic stability:

$$\mathcal{L}_{\text{thermo}} = \sum_{j} \left[\frac{\partial \hat{f}}{\partial T}\Big|_{\mathbf{x}_j} - \frac{C_p(\mathbf{x}_j)}{T_j}\right]^2$$

where $C_p$ is the known heat capacity function, and $T$ is temperature.

**Conservation constraint layer**: Enforce mass/charge conservation in material compositions:

$$\mathcal{L}_{\text{cons}} = \sum_{j} \left[\sum_{k=1}^{d} x_{j,k} - 1\right]^2$$

for compositional variables that must sum to unity.

**Physical bounds layer**: Apply sigmoid transformations to ensure outputs respect known physical ranges:

$$\hat{f}_{\text{bounded}}(\mathbf{x}) = f_{\min} + (f_{\max} - f_{\min}) \cdot \sigma(\hat{f}(\mathbf{x}))$$

#### 2.2.3 Multi-Fidelity Correlation Learning

Following the composite approach, we model the relationship between fidelities using a hierarchical structure:

$$f^{(m)}(\mathbf{x}) = \rho^{(m)} f^{(m-1)}(\mathbf{x}) + \delta^{(m)}(\mathbf{x})$$

where $\rho^{(m)}$ captures linear correlation and $\delta^{(m)}$ represents nonlinear discrepancies modeled by separate Gaussian processes:

$$\delta^{(m)} \sim \mathcal{GP}(0, k^{(m)}(\mathbf{x}, \mathbf{x}'))$$

We use the following kernel structure:

$$k^{(m)}(\mathbf{x}, \mathbf{x}') = \sigma_m^2 \exp\left(-\sum_{j=1}^d \frac{(x_j - x_j')^2}{2\ell_{m,j}^2}\right)$$

with automatic relevance determination (ARD) for dimension-specific length scales $\ell_{m,j}$.

### 2.3 Safe Multi-Fidelity Acquisition Function

#### 2.3.1 Risk-Aware Expected Improvement

We develop a novel acquisition function that balances expected improvement, cost, and safety:

$$\alpha_{\text{safe-MF}}(\mathbf{x}, m) = \frac{\text{EI}^{(m)}(\mathbf{x}) \cdot P_{\text{safe}}(\mathbf{x})}{c^{(m)}} \cdot \beta^{(m)}$$

where:
- $\text{EI}^{(m)}(\mathbf{x})$ is the expected improvement at fidelity $m$
- $P_{\text{safe}}(\mathbf{x})$ is the safety probability
- $c^{(m)}$ is the cost at fidelity $m$
- $\beta^{(m)}$ is a fidelity-specific exploration bonus

**Expected Improvement at fidelity $m$**:

$$\text{EI}^{(m)}(\mathbf{x}) = \mathbb{E}\left[\max(f^{(m)}(\mathbf{x}) - f^{(M)}_{\text{best}}, 0)\right]$$

Under the Gaussian process posterior, this has closed form:

$$\text{EI}^{(m)}(\mathbf{x}) = (\mu^{(m)}(\mathbf{x}) - f^{(M)}_{\text{best}})\Phi(Z) + \sigma^{(m)}(\mathbf{x})\phi(Z)$$

where $Z = \frac{\mu^{(m)}(\mathbf{x}) - f^{(M)}_{\text{best}}}{\sigma^{(m)}(\mathbf{x})}$, and $\Phi, \phi$ are the standard normal CDF and PDF.

**Safety Probability**:

$$P_{\text{safe}}(\mathbf{x}) = \prod_{i=1}^K P(g_i(\mathbf{x}) \geq 0) = \prod_{i=1}^K \Phi\left(\frac{\mu_{g_i}(\mathbf{x})}{\sigma_{g_i}(\mathbf{x})}\right)$$

where $\mu_{g_i}, \sigma_{g_i}$ are the GP posterior mean and standard deviation for constraint $g_i$.

#### 2.3.2 Information-Theoretic Fidelity Selection

To decide which fidelity to query, we compute the expected information gain per unit cost:

$$m^* = \arg\max_{m} \frac{\text{IG}^{(m)}(\mathbf{x})}{c^{(m)}}$$

where the information gain is:

$$\text{IG}^{(m)}(\mathbf{x}) = H[f^{(M)}] - \mathbb{E}_{y^{(m)} \sim p(y^{(m)}|\mathbf{x})}[H[f^{(M)}|y^{(m)}]]$$

This quantity measures how much observing fidelity $m$ at $\mathbf{x}$ reduces uncertainty about the true objective $f^{(M)}$.

### 2.4 Active Constraint Learning

Before exploring expensive regions, we actively learn safety boundaries using low-fidelity simulations:

**Algorithm: Adaptive Safety Boundary Refinement**

1. Initialize constraint models $\{g_i\}_{i=1}^K$ using physics-based priors
2. For iteration $t = 1$ to $T_{\text{safety}}$:
   - Compute uncertainty-weighted boundary distance:
   $$\mathbf{x}_t = \arg\max_{\mathbf{x}} \min_i \left|\frac{\mu_{g_i}(\mathbf{x})}{\sigma_{g_i}(\mathbf{x})}\right| \cdot \sigma_{g_i}(\mathbf{x})$$
   - Query lowest fidelity $m=1$ at $\mathbf{x}_t$
   - Update constraint GPs with observation
3. Return refined safe region $\mathcal{S} = \{\mathbf{x} : P_{\text{safe}}(\mathbf{x}) \geq 1-\epsilon\}$

This stage uses inexpensive simulations to map the feasible space before proposing costly experiments.

### 2.5 Complete Optimization Algorithm

**Algorithm: Physics-Informed Safe Multi-Fidelity Bayesian Optimization**

**Input**: Design space $\mathcal{X}$, fidelities $M$, costs $\{c^{(m)}\}$, budget $B$, safety threshold $\epsilon$

**Output**: Optimal safe design $\mathbf{x}^*$

1. **Initialization**:
   - Collect initial Latin hypercube samples at each fidelity: $\mathcal{D}^{(m)}_0$
   - Train physics-informed multi-fidelity GP: $\{f^{(m)}\}_{m=1}^M$
   - Initialize constraint models: $\{g_i\}_{i=1}^K$

2. **Active Safety Learning** (Phase 1):
   - Execute boundary refinement for $T_{\text{safety}}$ iterations
   - Update safe region $\mathcal{S}$

3. **Multi-Fidelity Optimization** (Phase 2):
   - While budget remaining $< B$:
     - For each fidelity $m$:
       - Compute $\alpha_{\text{safe-MF}}(\mathbf{x}, m)$ for $\mathbf{x} \in \mathcal{S}$
     - Select query: $(\mathbf{x}^*, m^*) = \arg\max_{\mathbf{x},m} \alpha_{\text{safe-MF}}(\mathbf{x}, m)$
     - If $P_{\text{safe}}(\mathbf{x}^*) < 1-\epsilon$: continue (skip unsafe)
     - Query $y^{(m^*)} = f^{(m^*)}(\mathbf{x}^*) + \epsilon$, update $\mathcal{D}^{(m^*)}$
     - Retrain models with physics-informed loss:
       $$\mathcal{L} = \mathcal{L}_{\text{NLL}} + \lambda_1 \mathcal{L}_{\text{thermo}} + \lambda_2 \mathcal{L}_{\text{cons}}$$
     - Update cumulative cost

4. **Return**: Best safe observation $\mathbf{x}^* = \arg\max_{\mathbf{x} \in \mathcal{D}^{(M)}} f^{(M)}(\mathbf{x})$ s.t. $g_i(\mathbf{x}) \geq 0$

### 2.6 Data Collection

We will validate our framework on two real-world materials design problems:

**Battery Electrolyte Design**:
- **Design variables** ($d=8$): Solvent compositions, salt concentrations, additive ratios, temperature
- **Fidelities**: (1) COSMO-RS calculations (~1 min), (2) molecular dynamics (~1 hour), (3) electrochemical testing (~1 week)
- **Objective**: Maximize ionic conductivity
- **Safety constraints**: Non-flammability, electrochemical stability window, toxicity limits
- **Dataset**: 500 low-fidelity, 100 mid-fidelity, 20 high-fidelity initial samples from existing literature

**Catalyst Design**:
- **Design variables** ($d=6$): Metal composition ratios, support material properties, calcination temperature
- **Fidelities**: (1) DFT binding energy (~10 min), (2) kinetic Monte Carlo (~2 hours), (3) laboratory synthesis and testing (~2 weeks)
- **Objective**: Maximize conversion efficiency for CO₂ reduction
- **Safety constraints**: Temperature limits, toxicity, explosive mixture prevention
- **Dataset**: 300 DFT calculations, 80 simulations, 15 experiments from collaborating laboratory

### 2.7 Experimental Design

**Baselines for comparison**:
1. Standard BO with Expected Improvement
2. Multi-fidelity BO (cost-aware EI)
3. SafeOpt (safety-constrained BO)
4. Random search within safe regions
5. Physics-based heuristic search

**Performance metrics**:
1. **Sample efficiency**: Number of high-fidelity evaluations to reach 95% of optimal performance
2. **Cost efficiency**: Total computational/experimental cost to convergence
3. **Safety compliance**: Percentage of proposed experiments satisfying all constraints
4. **Physics consistency**: Violation rate of known physical laws
5. **Regret**: Simple regret $r_t = f(\mathbf{x}^*) - f(\mathbf{x}_t)$ and cumulative regret
6. **Diversity**: Coverage of safe design space

**Experimental protocol**:
- 10-fold cross-validation splitting initial data
- 5 independent runs per method with different random seeds
- Statistical significance testing using Wilcoxon signed-rank test
- Ablation studies removing physics constraints, multi-fidelity, or safety mechanisms
- Sensitivity analysis varying safety threshold $\epsilon$ and physics weighting $\lambda$

### 2.8 Implementation Details

- **Software**: Python with GPyTorch for GP models, PyTorch for neural networks
- **Hyperparameter optimization**: Use marginal likelihood maximization for GP hyperparameters; grid search for $\lambda, \epsilon$
- **Computational resources**: NVIDIA A100 GPUs for neural network training; parallelization across fidelities
- **Convergence criteria**: Stop when improvement $< 0.1\%$ for 10 consecutive iterations or budget exhausted

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Quantitative outcomes**:
1. **Cost reduction**: We expect to demonstrate **50-70% reduction** in total experimental costs compared to standard multi-fidelity BO, achieving comparable optimization performance with significantly fewer high-fidelity evaluations.

2. **Safety guarantees**: Achieve **zero constraint violations** in proposed experiments while standard methods may suggest 10-20% unsafe candidates.

3. **Sample efficiency**: Reach 90% of optimal performance within **30-40 high-fidelity samples** compared to 60-80 for baseline methods.

4. **Physics consistency**: Reduce thermodynamic constraint violations by **>90%** through physics-informed layers.

**Qualitative outcomes**:
1. **Interpretable optimization paths**: Physics-informed acquisition functions will produce interpretable trajectories aligned with domain expert intuition.

2. **Transferable framework**: Demonstrate generalization to both battery and catalyst design problems with minimal problem-specific tuning.

3. **Uncertainty calibration**: Well-calibrated predictive uncertainties enabling trustworthy decision-making.

### 3.2 Theoretical Contributions

1. **Convergence guarantees**: Prove sub-linear cumulative regret bounds for the proposed safe multi-fidelity acquisition function under physics-informed GP assumptions:
   $$R_T = O\left(\sqrt{T \gamma_T \log T}\right)$$
   where $\gamma_T$ is the maximum information gain, modified by physics constraints.

2. **Safety certificates**: Establish probabilistic safety guarantees with confidence bounds:
   $$P\left(\forall t: g_i(\mathbf{x}_t) \geq 0\right) \geq 1 - \delta$$
   for user-specified failure probability $\delta$.

3. **Multi-fidelity information theory**: Derive optimal fidelity allocation strategies balancing bias-variance-cost trade-offs in the presence of physics constraints.

### 3.3 Practical Impact

**Immediate applications**:
- **Battery development**: Accelerate discovery of next-generation solid-state electrolytes, reducing development time from years to months
- **Sustainable catalysis**: Enable rapid screening of earth-abundant catalysts for CO₂ conversion, supporting climate change mitigation efforts
- **Cost savings**: Potential to save millions of dollars in experimental costs for industrial R&D laboratories

**Broader impact**:
1. **Accelerated scientific discovery**: The framework can be adapted to drug design, protein engineering, and materials for renewable energy, fundamentally changing the pace of experimental science.

2. **Democratization of experimental design**: By reducing costs and improving safety, smaller research groups and developing countries can participate in cutting-edge materials research.

3. **Trust in AI-driven experimentation**: Physics-informed approaches with safety guarantees will increase adoption of autonomous experimentation systems in high-stakes domains.

4. **Educational value**: The integration of domain knowledge with machine learning provides a blueprint for interdisciplinary training of next-generation scientists.

### 3.4 Limitations and Future Work

**Limitations**:
- Physics-based priors require domain expertise to formulate
- Computational overhead of physics-informed layers may be significant for very high-dimensional problems
- Assumes availability of multi-fidelity information sources

**Future directions**:
1. **Automatic physics discovery**: Develop methods to learn physical constraints from data when explicit formulations are unavailable
2. **Distributed experimentation**: Extend to batch acquisition for parallel experimental facilities
3. **Meta-learning across materials families**: Transfer learned physics-informed priors across related optimization problems
4. **Human-in-the-loop integration**: Incorporate expert feedback to refine safety boundaries and physics constraints adaptively

### 3.5 Dissemination Plan

- **Publications**: Target top-tier venues (NeurIPS, ICML, Nature Communications)
- **Open-source software**: Release Python package with documentation and tutorials
- **Industry partnerships**: Collaborate with battery manufacturers and chemical companies for real-world validation
- **Workshops**: Organize tutorials at ML and materials science conferences to train practitioners

This research proposal addresses critical challenges at the intersection of machine learning, materials science, and safe experimentation, with potential to transform how experimental design is conducted in safety-critical scientific domains. The physics-informed approach ensures that algorithmic efficiency does not come at the cost of domain knowledge or safety, bridging the gap between theoretical optimization and practical scientific discovery.