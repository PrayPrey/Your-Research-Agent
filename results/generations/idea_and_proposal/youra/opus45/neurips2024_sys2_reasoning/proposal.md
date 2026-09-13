# Research Proposal: CompDAG: Diagnosing Compositional Generalization via IRT-Calibrated DAG Benchmarks with Depth-Decay Analysis

## 1. Introduction

### 1.1 Background

The distinction between System-1 and System-2 reasoning, originally proposed in cognitive psychology, has become increasingly relevant to artificial intelligence research. System-1 reasoning is characterized by fast, automatic, and intuitive processing, while System-2 reasoning involves slow, deliberate, and analytical thinking. Modern large language models (LLMs) have demonstrated remarkable capabilities in many tasks, yet a fundamental question remains: do these models engage in genuine compositional reasoning (System-2), or do they rely on sophisticated pattern matching that mimics such reasoning (System-1)?

Compositional generalization—the ability to understand and produce novel combinations from known primitives—is a hallmark of human cognition and a prerequisite for robust System-2 reasoning. Humans can effortlessly understand sentences they have never encountered by composing meanings of familiar words according to syntactic rules. However, recent research has revealed troubling limitations in neural networks' compositional abilities. Dziri et al. (2023) demonstrated that transformers often reduce compositional tasks to "linearized subgraph matching," a pattern-matching strategy that degrades systematically with task complexity. This finding raises critical concerns about whether current models possess genuine compositional capabilities or merely approximate them through memorization.

Existing benchmarks for compositional generalization, such as SCAN and COGS, have provided valuable insights but suffer from significant limitations. First, benchmark contamination poses a persistent threat: as models are trained on increasingly large corpora, the probability that test examples or similar patterns appear in training data increases substantially. Sainz et al. (2023) have shown that contamination fundamentally undermines evaluation validity. Second, current benchmarks often fail to systematically isolate compositional complexity from other confounding factors, making it difficult to diagnose the specific nature of model failures. Third, static benchmarks become obsolete as models improve, necessitating continuous benchmark development.

### 1.2 Research Objectives

This research proposes CompDAG, a novel framework for diagnosing compositional generalization through IRT-calibrated Directed Acyclic Graph (DAG) benchmarks with depth-decay analysis. Our primary objectives are:

1. **Develop a principled benchmark generation framework** that models compositional tasks as parameterized DAGs with three controllable dimensions: Composition Depth (D), Working Memory Load (W), and Interference Level (I).

2. **Establish psychometrically valid difficulty calibration** using Item Response Theory (IRT) to ensure that generated tasks systematically vary in difficulty according to their compositional structure.

3. **Propose and validate a diagnostic criterion** based on accuracy decay patterns: models with genuine compositional generalization should exhibit flat or sublinear accuracy decay with increasing depth, while pattern-matching models should exhibit exponential decay.

4. **Demonstrate contamination resistance** through procedural generation from fixed grammar primitives with novel structural combinations.

### 1.3 Significance

This research addresses fundamental questions posed by the System-2 Reasoning at Scale workshop. By providing a rigorous diagnostic tool for compositional generalization, CompDAG will:

- Enable researchers to distinguish genuine compositional reasoning from sophisticated pattern matching, directly addressing AI safety concerns about model reliability.
- Provide contamination-resistant evaluation methodology that remains valid as models scale.
- Offer actionable insights for developing architectures with enhanced reasoning capabilities by identifying specific failure modes.
- Contribute to the broader debate about whether System-2 reasoning should emerge from training or be explicitly engineered into systems.

## 2. Methodology

### 2.1 Theoretical Framework

#### 2.1.1 DAG-Based Task Representation

We model compositional tasks as parameterized Directed Acyclic Graphs where nodes represent primitive operations and edges represent compositional dependencies. Formally, a task instance is defined as a tuple $T = (G, \phi, \psi)$ where:

- $G = (V, E)$ is a DAG with vertices $V$ representing operations and edges $E$ representing dependencies
- $\phi: V \rightarrow \mathcal{P}$ maps vertices to primitive operations from a fixed grammar $\mathcal{P}$
- $\psi: E \rightarrow \mathcal{R}$ maps edges to compositional relations from a relation set $\mathcal{R}$

#### 2.1.2 Controllable Complexity Dimensions

We define three orthogonal dimensions of compositional complexity:

**Composition Depth (D):** The longest path length in the DAG, representing the maximum number of sequential compositional operations required:
$$D(G) = \max_{v_1, v_k \in V} \min\{k-1 : \exists \text{ path } v_1 \rightarrow v_2 \rightarrow \cdots \rightarrow v_k\}$$

**Working Memory Load (W):** The maximum number of intermediate results that must be maintained simultaneously, computed as the maximum width of any level in the DAG:
$$W(G) = \max_{d \in [0, D]} |\{v \in V : \text{depth}(v) = d\}|$$

**Interference Level (I):** The number of distractor nodes that share surface features with target nodes but are not on the solution path:
$$I(G) = |V_{\text{distractor}}|$$

#### 2.1.3 Decay Pattern Hypothesis

Our core hypothesis posits that the accuracy decay pattern with respect to depth distinguishes compositional strategies:

**Compositional Generalization (Sublinear Decay):**
$$\text{Acc}(D) = \alpha - \beta \cdot \log(D + 1) + \epsilon$$

where $\beta \approx 0$ for truly compositional models, because each composition step applies learned primitives with constant cost $O(1)$.

**Pattern Matching (Exponential Decay):**
$$\text{Acc}(D) = \alpha \cdot e^{-\gamma D} + \epsilon$$

where $\gamma > 0$ reflects the exponentially growing search space of memorized patterns as depth increases.

### 2.2 Benchmark Generation Pipeline

#### 2.2.1 Grammar Specification

We extend the SCAN/COGS grammar framework with additional primitives to create a grammar $\mathcal{G} = (\mathcal{P}, \mathcal{R}, \mathcal{S})$ where:

- $\mathcal{P}$ contains 50-100 primitive operations (e.g., `FILTER`, `MAP`, `REDUCE`, `JOIN`)
- $\mathcal{R}$ contains compositional relations (e.g., `SEQUENCE`, `PARALLEL`, `CONDITIONAL`)
- $\mathcal{S}$ contains semantic type constraints ensuring well-formed compositions

#### 2.2.2 Procedural DAG Generation

Algorithm 1 describes the task generation procedure:

```
Algorithm 1: GenerateCompDAGTask(D_target, W_target, I_target, seed)
Input: Target depth D_target, width W_target, interference I_target, random seed
Output: Task instance T = (G, φ, ψ, input, output)

1. Initialize random generator with seed
2. Create root node v_0 with random primitive from P
3. For d = 1 to D_target:
   a. Sample n_d ~ Uniform(1, W_target) nodes for level d
   b. For each new node v:
      - Sample primitive φ(v) from P respecting type constraints
      - Connect to parent nodes from level d-1 with relation ψ(e)
4. Add I_target distractor nodes with plausible but incorrect connections
5. Generate natural language input from DAG structure
6. Compute ground truth output by DAG traversal
7. Return T = (G, φ, ψ, input, output)
```

#### 2.2.3 IRT Calibration

We employ a hierarchical 3-parameter logistic (3PL) IRT model to calibrate task difficulty:

$$P(Y_{ij} = 1 | \theta_j, a_i, b_i, c_i) = c_i + \frac{1 - c_i}{1 + e^{-a_i(\theta_j - b_i)}}$$

where:
- $Y_{ij}$ indicates whether model $j$ correctly solves task $i$
- $\theta_j$ represents model $j$'s latent ability
- $a_i$ is the discrimination parameter
- $b_i$ is the difficulty parameter
- $c_i$ is the guessing parameter

We extend this to incorporate DAG parameters through a hierarchical prior:

$$b_i \sim \mathcal{N}(\mu_b(D_i, W_i, I_i), \sigma_b^2)$$

where $\mu_b(D, W, I) = \beta_0 + \beta_D \cdot D + \beta_W \cdot W + \beta_I \cdot I + \beta_{DW} \cdot D \cdot W$

### 2.3 Experimental Design

#### 2.3.1 Pilot Study for IRT Calibration

**Objective:** Establish IRT model parameters and validate that DAG parameters predict difficulty.

**Procedure:**
1. Generate 500 tasks spanning the full range of $(D, W, I)$ combinations
2. Evaluate 10 diverse models (GPT-4, Claude-3, Llama-3-70B, Mistral-Large, T5-XXL, BART-Large, CodeLlama-34B, Gemini-Pro, Command-R+, Phi-3-Medium)
3. Fit hierarchical IRT model using Markov Chain Monte Carlo (MCMC)
4. Compute calibration correlation between predicted and observed difficulty

**Success Criterion:** Pearson correlation $r > 0.8$ between IRT-predicted difficulty and observed error rates.

#### 2.3.2 Main Experiment: Decay Pattern Analysis

**Objective:** Test whether accuracy decay patterns distinguish compositional generalization from pattern matching.

**Task Generation:**
- Depth levels: $D \in \{1, 2, 3, 4, 5, 6, 8, 10\}$
- Working memory: $W \in \{1, 2, 3\}$ (controlled)
- Interference: $I \in \{0, 3, 6\}$ (controlled)
- Tasks per condition: $n = 100$
- Total tasks: $8 \times 3 \times 3 \times 100 = 7,200$

**Models Under Evaluation:**
- Large-scale models: GPT-4, Claude-3-Opus, Gemini-Ultra
- Medium-scale models: Llama-3-70B, Mistral-Large, Command-R+
- Specialized models: Models fine-tuned on compositional tasks
- Baseline models: T5-Base, BART-Base (expected pattern-matching behavior)

**Analysis:**

For each model $m$, we fit both decay models and compare:

$$\mathcal{M}_{\text{linear}}: \text{Acc}_m(D) = \alpha_m - \beta_m \cdot D$$
$$\mathcal{M}_{\text{exp}}: \text{Acc}_m(D) = \alpha_m \cdot e^{-\gamma_m \cdot D}$$

Model comparison uses Akaike Information Criterion (AIC):
$$\text{AIC} = 2k - 2\ln(\hat{L})$$

where $k$ is the number of parameters and $\hat{L}$ is the maximum likelihood.

**Statistical Tests:**
1. Linear mixed-effects model with depth as fixed effect, model as random effect
2. Likelihood ratio test comparing linear vs. exponential fits
3. Bootstrap confidence intervals (95%) for decay slopes
4. Significance threshold: $\alpha = 0.05$

#### 2.3.3 Contamination Resistance Validation

**Objective:** Demonstrate that procedural generation provides contamination resistance.

**Procedure:**
1. Generate test set $T_1$ at time $t_1$
2. Generate test set $T_2$ at time $t_2 = t_1 + 30$ days using same grammar but different seeds
3. Evaluate identical models on both test sets
4. Compare decay patterns using paired t-tests

**Success Criterion:** No significant difference in decay patterns ($p > 0.1$).

#### 2.3.4 Ablation Studies

**Objective:** Isolate the contribution of each complexity dimension.

**Conditions:**
1. Depth-only variation: Fix $W=2$, $I=3$, vary $D$
2. Width-only variation: Fix $D=5$, $I=3$, vary $W$
3. Interference-only variation: Fix $D=5$, $W=2$, vary $I$
4. Surface feature control: Match surface statistics while varying DAG structure

### 2.4 Evaluation Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Exact Match Accuracy | Proportion of exactly correct outputs | Per-condition |
| Decay Slope ($\beta$ or $\gamma$) | Coefficient from fitted decay model | Slope difference > 0.05 |
| IRT Calibration Correlation | Pearson $r$ between predicted and observed difficulty | $r > 0.8$ |
| Model Fit (AIC/BIC) | Information criteria for decay model selection | Lower is better |
| Discrimination Index | Difference in accuracy between high/low ability models | > 0.3 |
| Contamination Resistance | Consistency across temporally separated test sets | $p > 0.1$ |

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcome (P1):** We expect to observe a clear bifurcation in decay patterns across model types. Specifically:
- Large-scale models with extensive training may show moderate decay slopes ($\beta \approx 0.03-0.05$), suggesting partial compositional capability
- Specialized models fine-tuned on compositional tasks should show flatter decay ($\beta < 0.02$)
- Baseline models without compositional training should show steep exponential decay ($\gamma > 0.15$)

**Secondary Outcome (P2):** The IRT calibration study will establish that DAG parameters $(D, W, I)$ systematically predict task difficulty with high reliability ($r > 0.8$), validating the theoretical framework.

**Tertiary Outcome (P3):** Contamination resistance validation will demonstrate that procedural generation from fixed primitives maintains evaluation validity across time, addressing a critical limitation of static benchmarks.

### 3.2 Potential Falsification

The hypothesis will be rejected if:
1. All models show similar decay patterns regardless of architecture (slope difference < 0.02)
2. IRT calibration fails ($r < 0.5$), indicating DAG parameters do not capture difficulty
3. Depth has no significant effect when controlling for surface features ($p > 0.1$)

Such outcomes would suggest that compositional complexity, as operationalized through DAG structure, does not distinguish reasoning strategies, necessitating alternative theoretical frameworks.

### 3.3 Broader Impact

**For AI Safety:** CompDAG provides a diagnostic tool for identifying models that may fail unpredictably on novel compositional problems. Models exhibiting exponential decay should be flagged for potential brittleness in deployment scenarios requiring genuine reasoning.

**For Architecture Development:** By identifying specific failure modes (depth sensitivity, working memory limitations, interference susceptibility), CompDAG guides the development of architectures with enhanced compositional capabilities. This directly addresses the workshop question of whether System-2 reasoning requires new mechanisms or emerges from training.

**For Benchmark Methodology:** The IRT-calibrated procedural generation framework establishes a template for contamination-resistant evaluation that can be extended to other reasoning domains (mathematical reasoning, visual composition, multi-step planning).

**For Theoretical Understanding:** The decay pattern analysis provides empirical evidence for or against the hypothesis that current models rely on pattern matching rather than genuine composition, informing debates about the nature of neural network reasoning and the role of scale in achieving System-2 capabilities.

### 3.4 Limitations and Future Directions

We acknowledge several limitations: (1) semantic parsing may not fully capture all aspects of compositional reasoning; (2) the DAG formalism assumes discrete, well-defined primitives that may not exist in all domains; (3) results are correlational rather than mechanistic. Future work should extend CompDAG to other domains, develop mechanistic interpretability analyses to complement behavioral diagnostics, and investigate training interventions that improve compositional generalization as measured by decay patterns.