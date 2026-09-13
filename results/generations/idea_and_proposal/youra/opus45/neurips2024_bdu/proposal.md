# Research Proposal: Predictive Prior Networks: LLM-Conditioned Foundation Model Surrogates for High-Dimensional Bayesian Optimization

## 1. Introduction

### 1.1 Background

Bayesian optimization (BO) has emerged as a powerful framework for optimizing expensive black-box functions, finding widespread applications in hyperparameter tuning, drug discovery, materials design, and neural architecture search. The core principle involves constructing a probabilistic surrogate model of the objective function and using an acquisition function to balance exploration and exploitation when selecting the next evaluation point. However, despite significant advances, BO methods face fundamental challenges when scaling to moderate-to-high dimensional settings (50-500 dimensions), where surrogate model accuracy degrades rapidly and uninformative priors lead to poor sample efficiency.

Traditional Gaussian Process (GP) surrogates, while providing principled uncertainty quantification, suffer from cubic computational complexity and struggle to capture complex dependencies in high-dimensional spaces. Recent innovations such as TuRBO (Trust Region Bayesian Optimization) and SAASBO (Sparse Axis-Aligned Subspace Bayesian Optimization) have partially addressed these limitations through local modeling and dimensionality reduction, respectively. More recently, foundation model surrogates like TabPFN and its extension GIT-BO have demonstrated remarkable zero-shot generalization capabilities by leveraging pre-trained transformers that encode implicit priors from diverse function classes.

Concurrently, Large Language Models (LLMs) have shown surprising capabilities in encoding domain knowledge across scientific and engineering disciplines. Recent work on LLM-BI (LLM-Based Bayesian Inference) and prior elicitation has demonstrated that LLMs can extract meaningful probabilistic priors from natural language problem descriptions. However, a critical gap remains: while LLMs contain rich semantic knowledge about optimization landscapes, constraints, and domain heuristics, no principled mechanism exists to integrate this knowledge into foundation model surrogates for Bayesian optimization.

### 1.2 Research Objectives

This research proposes **Predictive Prior Networks (PPN)**, a novel framework that bridges the gap between LLM-encoded domain knowledge and foundation model surrogates through attention-based hierarchical integration. Our primary objectives are:

1. **Develop a principled architecture** for conditioning foundation model surrogates (specifically TabPFN) on LLM-extracted semantic priors through cross-attention mechanisms.

2. **Design adaptive weighting mechanisms** that balance prior exploitation versus data-driven exploration, ensuring robustness against misleading or uninformative priors.

3. **Validate the hypothesis** that hierarchical prior integration improves sample efficiency by at least 20% compared to unconditioned baselines in moderate-to-high dimensional settings.

4. **Establish theoretical and empirical understanding** of when and why LLM priors provide complementary information to gradient-based methods.

### 1.3 Significance

This research addresses a critical bottleneck in deploying Bayesian optimization for real-world applications where function evaluations are expensive and domain expertise is available but underutilized. Success would enable:

- **Accelerated drug discovery** by incorporating pharmaceutical domain knowledge into molecular optimization
- **More efficient neural architecture search** by leveraging LLM understanding of architectural design principles
- **Improved hyperparameter tuning** through semantic understanding of algorithm behavior

Furthermore, this work contributes to the broader goal of integrating symbolic knowledge (encoded in LLMs) with neural probabilistic inference (foundation model surrogates), advancing the frontier of hybrid AI systems for decision-making under uncertainty.

## 2. Methodology

### 2.1 Overview of the PPN Framework

The Predictive Prior Networks framework operates through a three-stage hierarchical mechanism:

**Stage 1: LLM Prior Extraction** — Processing problem descriptions to generate structured semantic prior embeddings

**Stage 2: Cross-Attention Integration** — Conditioning TabPFN's context encoding on prior embeddings

**Stage 3: Adaptive Acquisition** — Balancing prior exploitation and data-driven exploration through learned weighting

### 2.2 Stage 1: LLM Prior Extraction

#### 2.2.1 Standardized Prompt Templates

We design three complementary prompt templates to elicit different types of prior knowledge:

**Template 1 (Constraint Elicitation):**
```
Given the optimization problem: [PROBLEM_DESCRIPTION]
Identify: (1) Hard constraints on input variables
         (2) Soft preferences or regularities
         (3) Known infeasible regions
Output as structured JSON with confidence scores.
```

**Template 2 (Region Suggestion):**
```
For optimizing [OBJECTIVE] over [DOMAIN]:
Suggest promising regions based on domain knowledge.
Provide: center coordinates, expected radius, confidence.
```

**Template 3 (Heuristic Encoding):**
```
What domain heuristics apply to [PROBLEM_TYPE]?
Encode as: variable importance rankings, interaction patterns,
monotonicity assumptions.
```

#### 2.2.2 Prior Embedding Generation

Let $\mathcal{P} = \{p_1, p_2, p_3\}$ denote the outputs from the three templates. We process these through a learned embedding network:

$$\mathbf{e}_{\text{prior}} = \text{MLP}_{\theta}\left(\text{Concat}\left[\phi(p_1), \phi(p_2), \phi(p_3)\right]\right) \in \mathbb{R}^{d_e}$$

where $\phi(\cdot)$ denotes the LLM's final-layer embedding and $d_e$ is the embedding dimension (set to match TabPFN's hidden dimension, typically 512).

### 2.3 Stage 2: Cross-Attention Integration

#### 2.3.1 TabPFN Context Encoding

TabPFN processes observed data $\mathcal{D}_t = \{(\mathbf{x}_i, y_i)\}_{i=1}^t$ through a transformer encoder to produce context representations:

$$\mathbf{H}_{\text{context}} = \text{TabPFN}_{\text{encoder}}(\mathcal{D}_t) \in \mathbb{R}^{t \times d_h}$$

#### 2.3.2 Prior-Conditioned Cross-Attention

We introduce cross-attention layers that condition the context encoding on prior embeddings:

$$\mathbf{Q} = \mathbf{H}_{\text{context}} \mathbf{W}_Q, \quad \mathbf{K} = \mathbf{e}_{\text{prior}} \mathbf{W}_K, \quad \mathbf{V} = \mathbf{e}_{\text{prior}} \mathbf{W}_V$$

$$\mathbf{A} = \text{softmax}\left(\frac{\mathbf{Q}\mathbf{K}^\top}{\sqrt{d_k}}\right)$$

$$\mathbf{H}_{\text{conditioned}} = \mathbf{H}_{\text{context}} + \alpha_t \cdot \mathbf{A}\mathbf{V}$$

where $\alpha_t \in [0, 1]$ is the adaptive weighting parameter (detailed in Stage 3).

#### 2.3.3 Prediction Head

The conditioned representation feeds into TabPFN's prediction head:

$$p(y^* | \mathbf{x}^*, \mathcal{D}_t, \mathbf{e}_{\text{prior}}) = \text{TabPFN}_{\text{decoder}}(\mathbf{H}_{\text{conditioned}}, \mathbf{x}^*)$$

This yields a predictive distribution with mean $\mu(\mathbf{x}^*)$ and variance $\sigma^2(\mathbf{x}^*)$.

### 2.4 Stage 3: Adaptive Weighting and Acquisition

#### 2.4.1 Prior-Data Agreement Score

We compute a dynamic agreement score between LLM priors and observed data:

$$s_t = \frac{1}{t} \sum_{i=1}^t \cos\left(\nabla_{\mathbf{x}} \mu_{\text{prior}}(\mathbf{x}_i), \nabla_{\mathbf{x}} \mu_{\text{data}}(\mathbf{x}_i)\right)$$

where $\mu_{\text{prior}}$ denotes predictions from a prior-only model and $\mu_{\text{data}}$ from a data-only model.

#### 2.4.2 Adaptive Weight Computation

The adaptive weight balances prior influence based on agreement and data quantity:

$$\alpha_t = \sigma\left(\beta_1 \cdot s_t + \beta_2 \cdot \log(t_0 / t)\right)$$

where $\sigma(\cdot)$ is the sigmoid function, $t_0$ is a reference iteration count, and $\beta_1, \beta_2$ are learned parameters. This formulation ensures:
- High $\alpha_t$ when prior-data agreement is strong and data is scarce
- Low $\alpha_t$ when disagreement occurs or sufficient data accumulates

#### 2.4.3 Prediction-Error Acquisition Function (PEAF)

We propose a novel acquisition function that leverages prediction error as an exploration signal:

$$\text{PEAF}(\mathbf{x}) = \mu(\mathbf{x}) + \kappa \cdot \sigma(\mathbf{x}) + \lambda \cdot |\mu_{\text{prior}}(\mathbf{x}) - \mu_{\text{data}}(\mathbf{x})|$$

The third term encourages exploration in regions where prior and data disagree, potentially revealing informative observations. Parameters $\kappa$ and $\lambda$ control exploration-exploitation trade-offs.

### 2.5 Training Procedure

#### 2.5.1 Two-Phase Training

**Phase 1: Cross-Attention Pre-training**
- Freeze TabPFN base weights
- Train cross-attention layers on synthetic functions with simulated LLM priors
- Loss: Negative log-likelihood of held-out observations

$$\mathcal{L}_1 = -\mathbb{E}_{\mathcal{D}, \mathbf{e}_{\text{prior}}}\left[\sum_{i \in \text{test}} \log p(y_i | \mathbf{x}_i, \mathcal{D}_{\text{train}}, \mathbf{e}_{\text{prior}})\right]$$

**Phase 2: End-to-End Fine-tuning**
- Jointly optimize cross-attention, adaptive weighting, and acquisition parameters
- Loss: Cumulative regret on meta-training tasks

$$\mathcal{L}_2 = \mathbb{E}_{\text{tasks}}\left[\sum_{t=1}^T \left(f(\mathbf{x}^*) - f(\mathbf{x}_t)\right)\right]$$

### 2.6 Experimental Design

#### 2.6.1 Benchmark Suite

**Synthetic Benchmarks:**
- Hartmann-6 (scaled to 50, 100, 200 dimensions via embedding)
- Rosenbrock (native high-dimensional)
- Ackley, Levy, Rastrigin (50-200 dimensions)

**Real-World Benchmarks:**
- MOPTA08 (124 dimensions, automotive design)
- Rover trajectory planning (60 dimensions)
- NAS-Bench-201 (architecture search, ~100 effective dimensions)
- HPO-B (hyperparameter optimization suite)

#### 2.6.2 Baselines

| Method | Description |
|--------|-------------|
| GIT-BO | Gradient-informed TabPFN (primary baseline) |
| SAASBO | Sparse axis-aligned subspace BO |
| TuRBO | Trust region BO |
| Vanilla TabPFN | Unconditioned foundation model |
| Random Search | Lower bound reference |

#### 2.6.3 Ablation Studies

1. **Prior Source Ablation:** Compare LLM priors vs. random priors vs. oracle priors
2. **Architecture Ablation:** Cross-attention vs. concatenation vs. FiLM conditioning
3. **Adaptive Weight Ablation:** Learned $\alpha_t$ vs. fixed $\alpha$ vs. no weighting
4. **Template Ablation:** Individual templates vs. combined

#### 2.6.4 Evaluation Metrics

**Primary Metric:**
- Simple regret at iteration $T$: $r_T = f(\mathbf{x}^*) - \max_{t \leq T} f(\mathbf{x}_t)$

**Secondary Metrics:**
- Area under regret curve (AUC)
- Iterations to reach target threshold
- Prior-data agreement score trajectory

#### 2.6.5 Statistical Analysis

- **Sample Size:** $n \geq 20$ random seeds per method per benchmark
- **Statistical Tests:** Paired t-test with Bonferroni correction ($\alpha = 0.05$)
- **Effect Size:** Cohen's $d > 0.5$ required for significance claims
- **Reporting:** Mean $\pm$ standard deviation, 95% confidence intervals

### 2.7 Falsification Criteria

The hypothesis will be **rejected** if:

1. **Primary Failure:** Regret reduction $< 5\%$ vs. GIT-BO ($p > 0.05$)
2. **Mechanism Failure:** Conditioned TabPFN shows $> 10\%$ degradation on standard regression benchmarks
3. **Robustness Failure:** With adversarial/misleading priors, adaptive weighting fails to recover within $50\%$ of baseline performance

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Prediction (P1):** We expect PPN to achieve $\geq 20\%$ lower simple regret than GIT-BO at 100 iterations on benchmarks where LLMs possess relevant domain knowledge (NAS, HPO, molecular optimization). Based on preliminary analysis of LLM prior quality and the complementary nature of semantic versus gradient information, we anticipate effect sizes of Cohen's $d \approx 0.6-0.8$.

**Secondary Prediction (P2):** Performance advantages will be most pronounced in early iterations ($t < 50$) when gradient estimates are noisy and data is scarce. We expect the gap to narrow as data accumulates, with PPN maintaining a $10-15\%$ advantage at convergence.

**Secondary Prediction (P3):** The adaptive weighting mechanism will demonstrate robustness to misleading priors, recovering to within $10\%$ of baseline performance, while fixed-weight variants will show $> 30\%$ degradation.

### 3.2 Scientific Contributions

1. **Methodological Innovation:** First principled framework for integrating LLM semantic priors with foundation model surrogates for Bayesian optimization

2. **Architectural Insights:** Understanding of how cross-attention conditioning affects transformer-based surrogate models

3. **Theoretical Understanding:** Characterization of when LLM priors provide complementary versus redundant information to gradient-based methods

4. **Benchmark Contributions:** Standardized evaluation protocols for LLM-augmented Bayesian optimization

### 3.3 Broader Impact

**Practical Applications:**
- Reduced experimental costs in drug discovery through more sample-efficient optimization
- Faster neural architecture search by leveraging architectural design knowledge
- Improved AutoML systems with semantic understanding of algorithm behavior

**Research Directions:**
- Foundation for hybrid symbolic-neural decision-making systems
- New paradigm for incorporating domain expertise into probabilistic inference
- Pathway toward more interpretable Bayesian optimization through explicit prior representation

### 3.4 Limitations and Future Work

**Current Limitations:**
- LLM inference cost ($\sim\$0.01-0.10$ per iteration) may be prohibitive for some applications
- Prior quality depends on LLM's domain knowledge coverage
- Requires prompt engineering for novel domains

**Future Directions:**
- Distillation of LLM priors into lightweight models for real-time applications
- Extension to multi-objective and constrained optimization
- Integration with active learning for experimental design
- Theoretical analysis of regret bounds under prior misspecification

This research represents a significant step toward unifying the complementary strengths of large language models and probabilistic machine learning for decision-making under uncertainty, with immediate applications in scientific discovery and engineering optimization.