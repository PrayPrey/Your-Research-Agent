# Research Proposal: Sparse Bayesian Epistasis Networks for Sample-Efficient Black-Box Discrete Optimization

## 1. Title

**Sparse Bayesian Epistasis Networks for Sample-Efficient Black-Box Discrete Optimization: A Hierarchical Structure Learning Approach for Expensive Epistatic Problems**

## 2. Introduction

### 2.1 Background

Discrete optimization in black-box settings represents a fundamental challenge across numerous scientific and engineering domains. Unlike continuous optimization where gradient-based methods have achieved remarkable success, discrete spaces lack the geometric structure that enables efficient local search. This challenge becomes particularly acute when three conditions coincide: (1) the objective function is expensive to evaluate (>$100 per evaluation), (2) the problem exhibits epistatic interactions where variables interact non-additively, and (3) the evaluation budget is severely constrained by cost or time limitations.

Epistasis—the phenomenon where the effect of one variable depends on the state of other variables—is ubiquitous in real-world applications. In protein engineering, amino acid substitutions often exhibit complex epistatic relationships where individual mutations may be deleterious but synergistic combinations yield improved fitness. In molecular design, functional groups interact through steric and electronic effects that cannot be decomposed into independent contributions. In compiler optimization, instruction scheduling decisions interact through register allocation and cache behavior. These epistatic interactions create rugged fitness landscapes where local optima proliferate and simple additive models fail catastrophically.

Recent advances in discrete sampling and optimization have pursued three primary directions. First, gradient-based MCMC algorithms extend Langevin dynamics to discrete spaces, enabling efficient exploration when gradient information can be approximated. Second, embedding methods map discrete problems into continuous spaces where powerful continuous optimization techniques apply, then project solutions back to discrete space. Third, novel proposal strategies including Stein variational methods and GFlowNets have demonstrated improved efficiency across multiple domains.

However, a critical gap remains for expensive epistatic problems. Variational autoencoder (VAE)-based memetic algorithms (Kato et al., 2025) can detect and exploit epistatic structure but require 2,000-5,000 black-box evaluations to train effective latent representations. GFlowNets (Zhu et al., 2023) achieve sample efficiency with hundreds of evaluations but model epistatic interactions implicitly through neural network approximations rather than explicit structure learning. For wet-lab applications where each evaluation costs $1,000 or more, neither approach enables practical optimization campaigns.

### 2.2 Research Objectives

This research proposes **Sparse Bayesian Epistasis Networks (SBEN)**, a novel framework that explicitly learns sparse interaction graphs while maintaining sample efficiency through three synergistic mechanisms: (1) spike-and-slab priors that concentrate probability mass on sparse subsets of possible interactions, (2) hierarchical expansion protocols that adaptively discover high-order interactions only when lower-order models prove insufficient, and (3) active learning strategies that select maximally informative samples for structure discovery.

The primary research objectives are:

**O1. Methodological Development**: Design and implement a sparse Bayesian network framework with hierarchical expansion (L2 → L3 → Ln) that achieves epistasis detection with <500 black-box evaluations, representing a 4-10× improvement over existing VAE-based approaches.

**O2. Theoretical Characterization**: Establish information-theoretic sample complexity bounds for hierarchical epistasis detection and prove computational complexity remains O(n²) for sparse interaction graphs under the hierarchical expansion protocol.

**O3. Empirical Validation**: Demonstrate superior sample efficiency on standardized epistatic benchmarks (NK landscapes with k=3) and real-world protein fitness optimization problems from the poli benchmark library.

**O4. Practical Impact**: Enable previously infeasible wet-lab experimental campaigns by reducing evaluation requirements from thousands to hundreds of samples, making $500K optimization budgets viable where $5M budgets were previously required.

### 2.3 Research Significance

This research addresses a critical bottleneck in expensive black-box optimization with three significant contributions:

**Scientific Contribution**: SBEN represents the first method to combine explicit sparse structure learning with sample efficiency competitive with implicit neural approaches. By learning interpretable interaction graphs rather than opaque latent representations, SBEN enables scientific insight into epistatic mechanisms while achieving practical sample budgets. The hierarchical expansion protocol draws inspiration from quantum chemistry perturbation theory, representing a novel cross-domain transfer of hierarchical interaction discovery principles.

**Methodological Contribution**: The integration of spike-and-slab priors, hierarchical expansion, and active learning creates a new algorithmic paradigm for discrete optimization. Unlike existing methods that treat structure learning and optimization as separate phases, SBEN performs joint structure discovery and optimization through active sample selection. The theoretical analysis of sample complexity bounds and computational scaling provides rigorous foundations for understanding when sparse structure learning outperforms dense latent representations.

**Practical Contribution**: By reducing evaluation requirements from thousands to hundreds, SBEN transforms the economics of expensive optimization problems. Protein engineering campaigns that previously required $2-5M in synthesis and assay costs become viable at $500K budgets. Molecular design projects can explore larger chemical spaces within fixed budgets. Compiler optimization for specialized hardware can evaluate more candidate strategies within development timelines. This order-of-magnitude cost reduction enables new classes of optimization problems to be tackled with experimental validation rather than pure simulation.

The broader impact extends to the discrete optimization research community by demonstrating that explicit structure learning remains competitive with modern neural approaches when properly designed for sample efficiency. This challenges the prevailing assumption that implicit neural representations necessarily dominate in low-data regimes and suggests renewed investigation of structured probabilistic models with modern computational techniques.

## 3. Methodology

### 3.1 Problem Formulation

We consider black-box discrete optimization problems of the form:

$$\mathbf{x}^* = \arg\max_{\mathbf{x} \in \mathcal{X}} f(\mathbf{x})$$

where $\mathcal{X} = \mathcal{D}_1 \times \mathcal{D}_2 \times \cdots \times \mathcal{D}_n$ is a discrete product space with $|\mathcal{D}_i| = d$ (typically $d \in \{2, 4, 20\}$ for binary, DNA, or amino acid alphabets), and $f: \mathcal{X} \rightarrow \mathbb{R}$ is an expensive black-box objective function with evaluation cost $c > \$100$ per sample.

The objective exhibits epistatic structure when it cannot be decomposed as:

$$f(\mathbf{x}) \neq \sum_{i=1}^n f_i(x_i)$$

but instead contains interaction terms:

$$f(\mathbf{x}) = \sum_{i=1}^n f_i(x_i) + \sum_{i<j} f_{ij}(x_i, x_j) + \sum_{i<j<k} f_{ijk}(x_i, x_j, x_k) + \cdots$$

Our goal is to discover the sparse interaction graph $\mathcal{G} = (\mathcal{V}, \mathcal{E})$ where vertices $\mathcal{V} = \{1, \ldots, n\}$ represent variables and edges $\mathcal{E}$ represent epistatic interactions, using a sample budget $N < 500$ black-box evaluations.

### 3.2 Sparse Bayesian Network with Spike-and-Slab Priors

#### 3.2.1 Network Structure

We model the objective function using a Bayesian network with structure $\mathcal{G}$ and parameters $\boldsymbol{\theta}$:

$$p(f(\mathbf{x}) | \mathcal{G}, \boldsymbol{\theta}) = \mathcal{N}\left(\sum_{C \in \mathcal{C}(\mathcal{G})} \phi_C(\mathbf{x}_C; \boldsymbol{\theta}_C), \sigma^2\right)$$

where $\mathcal{C}(\mathcal{G})$ denotes the set of cliques in graph $\mathcal{G}$, $\mathbf{x}_C$ are variables in clique $C$, and $\phi_C$ are clique potential functions parameterized by $\boldsymbol{\theta}_C$.

#### 3.2.2 Spike-and-Slab Prior for Sparsity

To enforce sparsity in the interaction graph, we employ spike-and-slab priors on edge weights. For each potential edge $(i,j)$, we introduce a binary indicator $\gamma_{ij} \in \{0, 1\}$ and weight $w_{ij}$:

$$p(w_{ij} | \gamma_{ij}) = \gamma_{ij} \cdot \mathcal{N}(w_{ij}; 0, \sigma_{\text{slab}}^2) + (1 - \gamma_{ij}) \cdot \mathcal{N}(w_{ij}; 0, \sigma_{\text{spike}}^2)$$

where $\sigma_{\text{spike}}^2 \ll \sigma_{\text{slab}}^2$ (typically $\sigma_{\text{spike}} = 0.01, \sigma_{\text{slab}} = 1.0$). The indicator variables follow a Bernoulli prior:

$$p(\gamma_{ij}) = \text{Bernoulli}(\pi_0)$$

with sparsity parameter $\pi_0 \in [0.05, 0.30]$ representing expected edge density.

This prior concentrates probability mass on sparse graphs while allowing sufficient flexibility to capture true interactions. The effective search space reduces from $O(2^{n^2})$ possible graphs to approximately $O(2^{cn})$ where $c = \pi_0 n$ is the expected edge count.

### 3.3 Hierarchical Expansion Protocol

#### 3.3.1 Level-2 (Pairwise) Initialization

The algorithm begins by learning pairwise interactions only. We construct an initial graph $\mathcal{G}^{(2)}$ containing only edges representing pairwise interactions:

$$\mathcal{E}^{(2)} = \{(i,j) : \gamma_{ij} = 1, i < j \leq n\}$$

The pairwise model is:

$$\hat{f}^{(2)}(\mathbf{x}) = \sum_{i=1}^n \beta_i x_i + \sum_{(i,j) \in \mathcal{E}^{(2)}} w_{ij} \mathbb{I}[x_i = a, x_j = b]$$

where $\mathbb{I}[\cdot]$ is an indicator function and the sum ranges over all alphabet combinations $(a,b) \in \mathcal{D}_i \times \mathcal{D}_j$.

#### 3.3.2 Sufficiency Test and Expansion Decision

After fitting the L2 model using current samples $\mathcal{D}_t = \{(\mathbf{x}_i, f(\mathbf{x}_i))\}_{i=1}^t$, we compute the coefficient of determination:

$$R^2 = 1 - \frac{\sum_{i=1}^t (f(\mathbf{x}_i) - \hat{f}^{(2)}(\mathbf{x}_i))^2}{\sum_{i=1}^t (f(\mathbf{x}_i) - \bar{f})^2}$$

If $R^2 > \tau$ (typically $\tau = 0.7$), pairwise interactions sufficiently explain observed variance and we terminate expansion. Otherwise, we proceed to L3 expansion.

#### 3.3.3 Level-3 (Triplet) Expansion

For L3 expansion, we identify variable clusters with high residual error:

$$\mathcal{V}_{\text{high}} = \{i : \sum_{\mathbf{x} \in \mathcal{D}_t : x_i \text{ varies}} (f(\mathbf{x}) - \hat{f}^{(2)}(\mathbf{x}))^2 > \delta\}$$

where $\delta$ is a threshold set to the 75th percentile of per-variable residuals.

We then search for triplet interactions only among high-residual variables:

$$\mathcal{E}^{(3)} = \{(i,j,k) : i,j,k \in \mathcal{V}_{\text{high}}, \gamma_{ijk} = 1\}$$

This adaptive expansion maintains computational complexity at $O(|\mathcal{V}_{\text{high}}|^3)$ rather than $O(n^3)$, typically yielding $O(n^2)$ scaling when $|\mathcal{V}_{\text{high}}| \propto \sqrt{n}$ for sparse epistasis.

### 3.4 Active Learning for Sample Selection

#### 3.4.1 Acquisition Function

At each iteration $t$, we select the next sample $\mathbf{x}_{t+1}$ to maximize expected information gain about the interaction structure. We use a variance-based acquisition function as a computationally tractable approximation to mutual information:

$$\mathbf{x}_{t+1} = \arg\max_{\mathbf{x} \in \mathcal{X}} \alpha(\mathbf{x}; \mathcal{D}_t)$$

where the acquisition function is:

$$\alpha(\mathbf{x}; \mathcal{D}_t) = \text{Var}_{p(\boldsymbol{\theta}, \mathcal{G} | \mathcal{D}_t)}[\hat{f}(\mathbf{x}; \boldsymbol{\theta}, \mathcal{G})] + \lambda \cdot H(\mathbf{x})$$

The first term is the posterior predictive variance:

$$\text{Var}_{p(\boldsymbol{\theta}, \mathcal{G} | \mathcal{D}_t)}[\hat{f}(\mathbf{x}; \boldsymbol{\theta}, \mathcal{G})] = \mathbb{E}_{p(\mathcal{G}|\mathcal{D}_t)}\left[\text{Var}_{p(\boldsymbol{\theta}|\mathcal{G}, \mathcal{D}_t)}[\hat{f}(\mathbf{x}; \boldsymbol{\theta}, \mathcal{G})]\right]$$

The second term $H(\mathbf{x})$ is a diversity penalty encouraging exploration of undersampled regions:

$$H(\mathbf{x}) = \min_{\mathbf{x}' \in \mathcal{D}_t} d_H(\mathbf{x}, \mathbf{x}')$$

where $d_H$ is Hamming distance and $\lambda = 0.1$ balances exploitation and exploration.

#### 3.4.2 Posterior Inference

We perform Bayesian inference over graph structures and parameters using Markov Chain Monte Carlo (MCMC) with Metropolis-Hastings sampling. The posterior distribution is:

$$p(\mathcal{G}, \boldsymbol{\theta} | \mathcal{D}_t) \propto p(\mathcal{D}_t | \mathcal{G}, \boldsymbol{\theta}) \cdot p(\boldsymbol{\theta} | \mathcal{G}) \cdot p(\mathcal{G})$$

The likelihood is:

$$p(\mathcal{D}_t | \mathcal{G}, \boldsymbol{\theta}) = \prod_{i=1}^t \mathcal{N}(f(\mathbf{x}_i); \hat{f}(\mathbf{x}_i; \boldsymbol{\theta}, \mathcal{G}), \sigma^2)$$

We use a structure MCMC proposal that adds, deletes, or reverses edges with probabilities proportional to edge posterior probabilities from the previous iteration. For computational efficiency with $t < 500$ samples, we maintain a particle filter with $K = 20$ graph samples and perform variational inference for parameters $\boldsymbol{\theta}$ given each graph structure.

### 3.5 Complete SBEN Algorithm

**Algorithm 1: Sparse Bayesian Epistasis Networks (SBEN)**

```
Input: Black-box function f, budget N, initial samples N_init
Output: Optimized solution x*, learned graph G

1. Initialize:
   - Collect N_init = 50 random samples: D_0 = {(x_i, f(x_i))}
   - Set current level L = 2
   - Initialize graph G^(2) with empty edge set

2. For t = N_init to N:
   
   3. Structure Learning (Level L):
      - Perform MCMC inference: p(G^(L), θ | D_t)
      - Update edge posteriors: p(γ_ij = 1 | D_t)
      - Construct MAP graph: G^(L) = argmax p(G | D_t)
   
   4. Sufficiency Test:
      - Compute R² on validation set (20% of D_t)
      - If R² > τ and L < L_max:
         * Identify high-residual variables V_high
         * Expand to level L+1 if |V_high| > 0.1n
         * Otherwise terminate expansion
   
   5. Active Sample Selection:
      - Compute acquisition function α(x; D_t) for all x
      - Select x_{t+1} = argmax α(x; D_t)
      - Evaluate f(x_{t+1}) and update D_{t+1} = D_t ∪ {(x_{t+1}, f(x_{t+1}))}
   
   6. Optimization:
      - Update current best: x* = argmax_{x ∈ D_{t+1}} f(x)

7. Return x*, G^(L)
```

### 3.6 Experimental Design

#### 3.6.1 Benchmark Problems

We evaluate SBEN on three benchmark categories:

**B1. NK Landscapes (Controlled Epistasis)**
- Problem size: $n \in \{50, 100, 200\}$
- Epistasis parameter: $k \in \{2, 3, 4\}$
- Alphabet size: $d = 2$ (binary)
- Number of instances: 20 random seeds per configuration
- Purpose: Controlled evaluation of epistasis detection accuracy

**B2. Protein Fitness Optimization (Real-World)**
- Benchmarks from poli library: GFP fluorescence, AAV capsid binding
- Sequence length: $n \in \{100, 500\}$
- Alphabet size: $d = 20$ (amino acids)
- Number of instances: 5 proteins × 4 random initializations
- Purpose: Validate practical applicability to wet-lab problems

**B3. Molecular Design (Chemical Space)**
- ZINC dataset molecular optimization
- Representation: SELFIES strings, $n \approx 50-100$ tokens
- Alphabet size: $d = 26$ (SELFIES vocabulary)
- Objectives: QED, penalized logP, docking scores
- Purpose: Demonstrate generalization to chemical optimization

#### 3.6.2 Baseline Methods

**Primary Baseline:**
- **VAE-Memetic** (Kato et al., 2025): State-of-the-art for epistatic discrete optimization
- Implementation: Official code from authors
- Configuration: 2000-5000 evaluation budget as reported

**Secondary Baselines:**
- **GFlowNets** (Zhu et al., 2023): Sample-efficient neural approach
- **Random Search + Gaussian Process BO**: Non-epistatic baseline
- **CMA-ES with integer encoding**: Evolutionary baseline
- **DRAKES** (gradient-based discrete optimization): When gradients available

#### 3.6.3 Evaluation Metrics

**Primary Metrics:**

**M1. Sample Efficiency to Target Accuracy:**
$$N_{\tau} = \min\{t : R^2_t > \tau\}$$
where $R^2_t$ is epistasis detection accuracy at iteration $t$, $\tau = 0.7$.

**M2. Optimization Performance:**
$$\text{Regret}_t = f(\mathbf{x}^*) - \max_{i \leq t} f(\mathbf{x}_i)$$
where $\mathbf{x}^*$ is the global optimum (known for NK landscapes) or best-known solution (protein/molecular benchmarks).

**M3. Computational Efficiency:**
$$T_{\text{iter}} = \text{wall-clock time per iteration}$$
measured as function of problem size $n$ to verify $O(n^2)$ scaling.

**Secondary Metrics:**

**M4. Structure Recovery (NK Landscapes):**
- Edge precision: $P = \frac{|\mathcal{E}_{\text{true}} \cap \mathcal{E}_{\text{pred}}|}{|\mathcal{E}_{\text{pred}}|}$
- Edge recall: $R = \frac{|\mathcal{E}_{\text{true}} \cap \mathcal{E}_{\text{pred}}|}{|\mathcal{E}_{\text{true}}|}$
- F1 score: $F_1 = \frac{2PR}{P+R}$

**M5. Active Learning Gain:**
$$G_{\text{AL}} = \frac{N_{\text{random}}}{N_{\text{active}}}$$
where $N_{\text{random}}$ and $N_{\text{active}}$ are samples required to reach same performance with random vs. active sampling.

#### 3.6.4 Statistical Analysis

**Hypothesis Testing:**

**Test 1 (Primary - Sample Efficiency):**
- Null hypothesis: $\mu_{N_{\text{SBEN}}} \geq 500$ evaluations to reach $R^2 > 0.7$
- Alternative: $\mu_{N_{\text{SBEN}}} < 500$
- Test: One-sample t-test, $\alpha = 0.05$, $n = 20$ runs
- Power analysis: Detects effect size $d = 0.8$ with power $> 0.90$

**Test 2 (Comparative - vs VAE-Memetic):**
- Null hypothesis: $\mu_{N_{\text{SBEN}}} / \mu_{N_{\text{VAE}}} \geq 0.25$ (less than 4× improvement)
- Alternative: $\mu_{N_{\text{SBEN}}} / \mu_{N_{\text{VAE}}} < 0.25$
- Test: Independent samples Welch's t-test, $\alpha = 0.05$
- Sample size: $n = 20$ runs per method
- Expected effect size: Cohen's $d = 1.5$ (large effect)

**Test 3 (Mechanism - Active Learning):**
- Null hypothesis: $G_{\text{AL}} \leq 1.5$ (less than 50% improvement)
- Alternative: $G_{\text{AL}} > 3.0$ (3× improvement)
- Test: Paired t-test (same benchmarks), $\alpha = 0.05$

**Ablation Studies:**

To validate the causal mechanism, we perform ablation experiments removing each component:

1. **SBEN-NoSparsity**: Uniform prior on edges ($\pi_0 = 0.5$) instead of spike-and-slab
2. **SBEN-NoHierarchy**: Direct L3 search without L2 initialization
3. **SBEN-NoActive**: Random sampling instead of active learning
4. **SBEN-Full**: Complete method

We measure $\Delta N = N_{\text{ablated}} - N_{\text{full}}$ to quantify each component's contribution.

#### 3.6.5 Implementation Details

**Software Stack:**
- Bayesian inference: PyMC3 with NUTS sampler
- Graph structure learning: pgmpy library
- Active learning: Custom implementation with BoTorch acquisition optimization
- Benchmarks: poli library (proteins), BB-DOB suite (NK landscapes)

**Computational Resources:**
- Hardware: NVIDIA A100 GPU (40GB), 32-core CPU
- Parallelization: 20 independent runs in parallel
- Estimated time: 2 weeks for full benchmark suite

**Hyperparameters:**
- Spike-and-slab: $\sigma_{\text{spike}} = 0.01$, $\sigma_{\text{slab}} = 1.0$
- Sparsity prior: $\pi_0 = 0.15$ (tuned on validation set)
- Sufficiency threshold: $\tau = 0.7$
- Active learning balance: $\lambda = 0.1$
- Initial samples: $N_{\text{init}} = 50$
- MCMC: 1000 burn-in + 2000 samples, 20 particles

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome 1: Sample Efficiency Achievement**

We expect SBEN to achieve epistasis detection with $N < 500$ black-box evaluations on NK landscapes ($k=3$, $n=100$), representing a 4-10× reduction compared to VAE-memetic baselines requiring 2,000-5,000 evaluations. Specifically, we predict:

- Mean samples to $R^2 > 0.7$: $\mu_N = 350 \pm 80$ evaluations
- Success rate (achieving target within budget): $> 90\%$ of runs
- Comparative ratio: $\mu_{N_{\text{SBEN}}} / \mu_{N_{\text{VAE}}} < 0.20$ (5× improvement)

This outcome directly validates the core hypothesis that sparse structure learning with hierarchical expansion enables sample-efficient epistasis detection.

**Primary Outcome 2: Mechanism Validation**

Ablation studies will quantify each component's contribution:

- Sparse priors: Expected $\Delta N_{\text{sparsity}} \approx 100$ evaluations saved (22% reduction)
- Hierarchical expansion: Expected $\Delta N_{\text{hierarchy}} \approx 150$ evaluations saved (30% reduction)
- Active learning: Expected $\Delta N_{\text{active}} \approx 120$ evaluations saved (25% reduction)
- Combined effect: Synergistic improvement beyond additive contributions

These results will establish which causal links in the proposed mechanism are strongest and identify opportunities for further improvement.

**Primary Outcome 3: Computational Scaling**

We expect wall-clock time per iteration to scale as $T_{\text{iter}} = O(n^{2.2})$ empirically, confirming near-quadratic complexity:

- $n=50$: $T_{\text{iter}} \approx 2$ seconds
- $n=100$: $T_{\text{iter}} \approx 9$ seconds (4.5× increase)
- $n=200$: $T_{\text{iter}} \approx 40$ seconds (4.4× increase)

This validates that hierarchical expansion maintains tractable computational costs even for moderate-scale problems ($n \sim 200$).

**Secondary Outcome 1: Real-World Protein Optimization**

On protein fitness benchmarks (GFP, AAV), we expect:

- Optimization performance: Reach top 5% fitness with $< 400$ evaluations
- Comparison to GFlowNets: Comparable or superior performance with explicit structure interpretability
- Structure insights: Recovered interaction graphs reveal known epistatic hotspots (e.g., GFP chromophore residues)

**Secondary Outcome 2: Generalization to Molecular Design**

On ZINC molecular optimization:

- QED optimization: Achieve QED $> 0.9$ molecules within 500 evaluations
- Multi-objective performance: Pareto front quality competitive with GFlowNets
- Chemical interpretability: Learned graphs identify functional group interactions

### 4.2 Potential Limitations

**Limitation 1: Dense Interaction Graphs**

If the true interaction graph is dense ($|\mathcal{E}| > 0.5n^2$), sparse priors will be misspecified and SBEN may underperform. Mitigation: Adaptive sparsity parameter $\pi_0$ updated via empirical Bayes during optimization.

**Limitation 2: Very High-Order Interactions**

For problems dominated by 4-way or higher interactions without lower-order structure, hierarchical expansion may waste samples on uninformative L2/L3 search. Mitigation: Early termination of expansion levels based on information-theoretic criteria.

**Limitation 3: Scalability Beyond n=500**

Bayesian inference over graph structures may become intractable for $n > 500$ variables. Mitigation: Variational inference approximations and local structure learning (learning subgraphs independently).

**Limitation 4: Hyperparameter Sensitivity**

Spike-and-slab widths and sufficiency thresholds may require domain-specific tuning. Mitigation: Provide principled default values and sensitivity analysis across benchmarks.

### 4.3 Scientific Impact

**Theoretical Contributions:**

1. **Sample Complexity Bounds**: First rigorous analysis of sample complexity for hierarchical epistasis detection in discrete black-box optimization, establishing information-theoretic lower bounds and proving SBEN achieves near-optimal rates under sparsity assumptions.

2. **Computational Complexity Analysis**: Proof that hierarchical expansion maintains $O(n^2)$ complexity for sparse graphs with bounded treewidth, extending classical Bayesian network learning theory to active optimization settings.

3. **Cross-Domain Transfer**: Formalization of quantum chemistry perturbation theory principles (hierarchical interaction discovery) as a general algorithmic strategy for machine learning structure learning.

**Methodological Contributions:**

1. **Unified Framework**: SBEN provides a principled integration of structure learning and optimization, resolving the tension between explicit interpretable models (Bayesian networks) and sample-efficient implicit models (VAEs, GFlowNets).

2. **Active Structure Learning**: Novel acquisition functions for joint structure and parameter learning, extending Bayesian experimental design to graph discovery problems.

3. **Benchmark Suite**: Standardized evaluation protocol for epistatic discrete optimization with controlled epistasis strength, enabling systematic comparison of future methods.

### 4.4 Practical Impact

**Enabling Wet-Lab Optimization:**

The 4-10× sample reduction directly translates to cost savings:

- Protein engineering: $2-5M → $500K per optimization campaign
- Molecular synthesis: 2,000 → 400 compounds synthesized
- Timeline reduction: 2-3 years → 6-12 months for iterative design cycles

This makes previously infeasible experimental campaigns viable for academic labs and small biotech companies with limited budgets.

**Industry Applications:**

1. **Pharmaceutical Discovery**: Optimize antibody binding affinity with reduced animal testing
2. **Materials Science**: Design catalysts and polymers with fewer synthesis iterations
3. **Compiler Optimization**: Explore larger optimization spaces for specialized hardware (TPUs, neuromorphic chips)
4. **Synthetic Biology**: Engineer metabolic pathways with reduced strain construction costs

**Open-Source Software:**

We will release a production-quality Python package (`sben`) with:

- Modular implementation supporting custom objectives and acquisition functions
- Integration with poli benchmark library
- Tutorials for protein engineering and molecular design applications
- Pre-trained models for transfer learning on common domains

### 4.5 Future Research Directions

**Extension 1: Transfer Learning**

Leverage learned interaction graphs from related problems (e.g., homologous proteins) as informative priors, potentially reducing sample requirements to $< 200$ evaluations for well-studied domains.

**Extension 2: Multi-Fidelity Optimization**

Integrate cheap low-fidelity evaluations (computational predictions) with expensive high-fidelity evaluations (wet-lab experiments) through hierarchical Bayesian models.

**Extension 3: Constrained Optimization**

Extend SBEN to handle hard constraints (e.g., synthesizability, toxicity) through constrained Bayesian optimization and feasibility modeling.

**Extension 4: Continuous-Discrete Hybrid Spaces**

Generalize to mixed discrete-continuous optimization (e.g., molecular design with continuous conformational degrees of freedom) through hybrid graph-GP models.

### 4.6 Broader Implications

This research challenges the prevailing assumption in modern machine learning that neural implicit representations necessarily outperform structured probabilistic models in low-data regimes. By demonstrating that explicit structure learning can achieve competitive sample efficiency when properly designed with sparse priors and active learning, SBEN suggests renewed investigation of interpretable structured models across machine learning.

The success of hierarchical expansion protocols inspired by quantum chemistry also highlights the value of cross-domain transfer from physical sciences to machine learning algorithm design. Future work may identify additional algorithmic principles from physics, chemistry, and biology that can be formalized as machine learning methods.

Finally, by enabling order-of-magnitude cost reductions in expensive experimental optimization, SBEN may accelerate scientific discovery in domains where iteration speed is currently limited by evaluation costs rather than algorithmic capabilities. This shifts the bottleneck from computation to experimentation, potentially transforming how optimization-driven science is conducted in wet-lab settings.

---

**Total Word Count: 5,847 words**