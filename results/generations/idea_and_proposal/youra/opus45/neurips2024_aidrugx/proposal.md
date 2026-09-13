# Research Proposal: CLAM: Closed-Loop Active Learning for Multi-Objective mRNA Therapeutic Optimization

## 1. Introduction

### 1.1 Background

Messenger RNA (mRNA) therapeutics have emerged as a transformative modality in modern medicine, exemplified by the rapid development and deployment of COVID-19 vaccines. Unlike traditional small molecule drugs or protein biologics, mRNA therapeutics offer programmable protein expression, rapid manufacturing scalability, and the potential to address previously undruggable targets. However, the design of optimal mRNA sequences remains a formidable challenge due to the complex interplay between multiple therapeutic objectives: maximizing protein expression, ensuring mRNA stability, and minimizing immunogenicity.

Current approaches to mRNA therapeutic design predominantly rely on one-shot optimization methods. These include rule-based codon optimization algorithms, machine learning models trained on existing datasets, and more recently, foundation models such as Helix-mRNA and RiboDecode that generate sequences in a single forward pass. While these methods have achieved notable successes—RiboDecode demonstrated 10-fold improvement in antibody response, and Helix-mRNA enabled generation of sequences 6 times longer than previous methods—they share a fundamental limitation: they operate without iterative experimental feedback. This one-shot paradigm assumes that computational models can fully capture the sequence-to-function landscape, an assumption that often fails given the complexity of cellular translation machinery, mRNA degradation pathways, and innate immune recognition.

The emergence of RNA foundation models, such as AIDO.RNA with 1.6 billion parameters, has provided powerful representations of RNA sequence features. Simultaneously, advances in Bayesian optimization have demonstrated remarkable sample efficiency in navigating high-dimensional design spaces, with frameworks like ALBF achieving 60% improvement in drug discovery applications. Furthermore, closed-loop optimization paradigms have proven transformative in synthetic biology, with systems like METIS achieving 10-100x improvements through iterative experimental feedback.

### 1.2 Research Gap

Despite these individual advances, no existing framework integrates RNA foundation model embeddings with closed-loop Bayesian optimization for mRNA therapeutic design. This gap results in several critical limitations:

1. **Suboptimal sequence exploration**: One-shot methods cannot adapt to experimental observations, potentially missing superior regions of sequence space.
2. **Inefficient resource utilization**: Without principled acquisition strategies, experimental budgets are often wasted on uninformative sequences.
3. **Inadequate multi-objective handling**: Therapeutic mRNA design requires simultaneous optimization of competing objectives, which one-shot methods address only implicitly.

### 1.3 Research Objectives

This proposal introduces CLAM (Closed-Loop Active Learning for Multi-Objective mRNA Therapeutic Optimization), a framework that addresses these limitations through the following objectives:

1. **Primary Objective**: Develop and validate a closed-loop optimization framework that achieves ≥2x improvement in protein expression within 20-30 experimental rounds compared to one-shot baselines.
2. **Secondary Objective**: Demonstrate sample-efficient navigation of the expression-stability-immunogenicity Pareto front, reducing experimental costs by 50-70%.
3. **Mechanistic Objective**: Establish the causal contribution of each framework component through systematic ablation studies.

### 1.4 Significance

Successful development of CLAM would represent a paradigm shift in mRNA therapeutic design, transitioning from static, one-shot optimization to dynamic, feedback-driven discovery. This has immediate implications for vaccine development, protein replacement therapies, and cancer immunotherapies, potentially accelerating development timelines while reducing costs.

## 2. Methodology

### 2.1 Framework Overview

CLAM operates through a four-step causal mechanism that iteratively refines mRNA sequence design:

**Step 1: LoRA-Adapted RNA-FM Embedding Generation**
**Step 2: Gaussian Process Surrogate Modeling**
**Step 3: Multi-Objective Acquisition Function Optimization**
**Step 4: Experimental Feedback Integration**

### 2.2 Component 1: LoRA-Adapted RNA Foundation Model Embeddings

We leverage pre-trained RNA foundation models (AIDO.RNA or RNA-FM) as the embedding backbone, with Low-Rank Adaptation (LoRA) fine-tuning to capture mRNA-specific features.

**Mathematical Formulation:**

For an mRNA sequence $s = (s_1, s_2, ..., s_n)$ where $s_i \in \{A, U, G, C\}$, the base foundation model produces embeddings:

$$h = f_{\text{RNA-FM}}(s) \in \mathbb{R}^d$$

LoRA adaptation modifies the attention weights $W$ with low-rank updates:

$$W' = W + \Delta W = W + BA$$

where $B \in \mathbb{R}^{d \times r}$, $A \in \mathbb{R}^{r \times d}$, and $r \ll d$ is the rank (typically $r = 8$ or $r = 16$).

The adapted embedding becomes:

$$h' = f_{\text{RNA-FM}}^{\text{LoRA}}(s; \theta_{\text{LoRA}}) \in \mathbb{R}^d$$

**Fine-tuning Protocol:**
- Training data: Public mRNA expression datasets from RiboDecode and Helix-mRNA (~10,000 sequences)
- Objective: Minimize MSE between predicted and measured translation efficiency
- Validation: Hold-out correlation $\rho > 0.6$ required before proceeding

### 2.3 Component 2: Multi-Output Gaussian Process Surrogate

We model the sequence-to-function landscape using a multi-output Gaussian Process (MOGP) that jointly predicts expression ($y_1$), stability ($y_2$), and immunogenicity ($y_3$).

**Mathematical Formulation:**

Given observed data $\mathcal{D} = \{(h'_i, \mathbf{y}_i)\}_{i=1}^N$ where $\mathbf{y}_i = (y_{i,1}, y_{i,2}, y_{i,3})^T$, the MOGP posterior is:

$$p(\mathbf{f}^* | h'^*, \mathcal{D}) = \mathcal{N}(\boldsymbol{\mu}^*, \boldsymbol{\Sigma}^*)$$

where:

$$\boldsymbol{\mu}^* = K(h'^*, H') [K(H', H') + \sigma^2 I]^{-1} \mathbf{Y}$$

$$\boldsymbol{\Sigma}^* = K(h'^*, h'^*) - K(h'^*, H') [K(H', H') + \sigma^2 I]^{-1} K(H', h'^*)$$

We employ the Intrinsic Coregionalization Model (ICM) kernel:

$$k_{\text{ICM}}((h', t), (h'', t')) = k_{\text{RBF}}(h', h'') \cdot B_{t,t'}$$

where $B \in \mathbb{R}^{3 \times 3}$ captures correlations between objectives and $k_{\text{RBF}}$ is the radial basis function kernel.

### 2.4 Component 3: Multi-Objective Acquisition Function

We employ the q-Expected Hypervolume Improvement (q-EHVI) acquisition function to select batches of Pareto-optimal candidates.

**Mathematical Formulation:**

The hypervolume indicator $\text{HV}(\mathcal{P}, r)$ measures the volume dominated by Pareto front $\mathcal{P}$ with reference point $r$:

$$\text{HV}(\mathcal{P}, r) = \lambda\left(\bigcup_{\mathbf{y} \in \mathcal{P}} [\mathbf{y}, r]\right)$$

where $\lambda$ denotes Lebesgue measure.

The q-EHVI acquisition function for batch selection is:

$$\alpha_{\text{q-EHVI}}(\{h'_1, ..., h'_q\}) = \mathbb{E}\left[\text{HV}(\mathcal{P} \cup \{\mathbf{f}(h'_1), ..., \mathbf{f}(h'_q)\}, r) - \text{HV}(\mathcal{P}, r)\right]$$

**Batch Selection Algorithm:**

```
Algorithm 1: CLAM Batch Selection
Input: GP posterior, current Pareto front P, batch size q
Output: Selected sequences S = {s_1, ..., s_q}

1. Initialize candidate pool C from sequence generator
2. Encode candidates: H' = {f_RNA-FM^LoRA(s) : s ∈ C}
3. For each candidate h' ∈ H':
     Compute posterior: μ(h'), Σ(h') from GP
4. Optimize q-EHVI using sequential greedy selection:
     For i = 1 to q:
       h'_i = argmax_{h' ∈ H'} α_q-EHVI(S ∪ {h'})
       S = S ∪ {h'_i}
5. Decode selected embeddings to sequences
6. Return S
```

### 2.5 Component 4: Experimental Feedback Integration

**Ribosome Profiling Protocol:**

Selected mRNA sequences are synthesized, transfected into HEK293T cells using MC3-based lipid nanoparticles (LNPs), and subjected to ribosome profiling at 6, 12, and 24 hours post-transfection.

**Measurements:**
- **Protein Expression ($y_1$)**: Ribosome-protected fragment (RPF) density normalized to mRNA abundance (RPKM)
- **mRNA Stability ($y_2$)**: Half-life estimated from RNA-seq time course using exponential decay fitting
- **Immunogenicity ($y_3$)**: Cytokine panel (IL-6, TNF-α, IFN-γ) quantified via ELISA

**GP Update:**

After each experimental round, the GP posterior is updated with new observations:

$$\mathcal{D}_{t+1} = \mathcal{D}_t \cup \{(h'_{\text{new}}, \mathbf{y}_{\text{new}})\}$$

Hyperparameters are re-optimized via marginal likelihood maximization every 5 rounds.

### 2.6 Experimental Design

**Phase 1: In Silico Validation (Weeks 1-8)**

- **Objective**: Validate framework components using simulated oracles
- **Setup**: Use RiboDecode predictions as ground truth; simulate noise with $\sigma = 0.15$
- **Metrics**: Convergence rate, hypervolume improvement, embedding quality

**Phase 2: In Vitro Validation (Weeks 9-24)**

- **Cell Line**: HEK293T (primary), A549 (secondary validation)
- **Batch Size**: 10 sequences per round
- **Total Rounds**: 25 rounds
- **Baselines**: 
  - Random selection (negative control)
  - Helix-mRNA one-shot (SOTA baseline)
  - RiboDecode one-shot (SOTA baseline)

**Phase 3: Ablation Studies (Weeks 25-32)**

| Ablation | Component Removed | Purpose |
|----------|-------------------|---------|
| A1 | LoRA adaptation | Test embedding quality contribution |
| A2 | Multi-output GP → Independent GPs | Test objective correlation modeling |
| A3 | q-EHVI → Random acquisition | Test acquisition function contribution |
| A4 | Closed-loop → One-shot | Test feedback loop contribution |

### 2.7 Evaluation Metrics

**Primary Metrics:**

1. **Expression Fold-Change**: $\text{FC} = \frac{\max_t y_{1,t}}{y_{1,0}}$ where $y_{1,0}$ is initial best expression
2. **Convergence Correlation**: Spearman $\rho$ between round number and best-in-batch expression

**Secondary Metrics:**

3. **Hypervolume Indicator**: $\text{HV}(\mathcal{P}_T, r)$ at final round $T$
4. **Pareto Front Size**: Number of non-dominated solutions
5. **Sample Efficiency**: Rounds required to achieve 2x improvement

**Statistical Analysis:**

- Mann-Whitney U test for CLAM vs. baselines (non-parametric)
- Spearman rank correlation for convergence trends
- Effect size: $r = \frac{Z}{\sqrt{N}}$ with threshold $r > 0.3$
- Significance level: $\alpha = 0.05$ with Bonferroni correction

### 2.8 Success and Falsification Criteria

**Success Criteria:**
- Expression fold-change ≥ 2x (p < 0.05)
- Convergence correlation ρ > 0.7
- Pareto front contains ≥ 3 non-dominated solutions

**Falsification Criteria:**
- Expression fold-change ≤ 1.2x after 30 rounds
- No monotonic improvement (ρ < 0.3)
- LoRA embeddings show ≤ 0.1 correlation improvement
- CLAM requires > 50 rounds to match one-shot methods

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcome**: We anticipate CLAM will achieve 2-5x improvement in protein expression within 20-30 experimental rounds, significantly outperforming one-shot baselines that achieve <1.5x improvement with equivalent experimental budgets.

**Secondary Outcomes**:
1. **Sample Efficiency**: 50-70% reduction in required experiments compared to random exploration
2. **Multi-Objective Trade-offs**: Discovery of 3-5 distinct Pareto-optimal mRNA designs representing different expression-stability-immunogenicity profiles
3. **Mechanistic Insights**: Quantified contribution of each framework component through ablation studies

### 3.2 Scientific Impact

CLAM represents a methodological advance in integrating foundation models with active learning for therapeutic design. The framework establishes:

1. **A new paradigm** for mRNA optimization that leverages iterative experimental feedback
2. **Validated protocols** for LoRA adaptation of RNA foundation models to therapeutic contexts
3. **Benchmarks** for closed-loop optimization in mRNA design

### 3.3 Translational Impact

Successful validation of CLAM would enable:

1. **Accelerated vaccine development**: Rapid optimization of mRNA vaccines for emerging pathogens
2. **Personalized mRNA therapeutics**: Patient-specific optimization for cancer neoantigens
3. **Cost reduction**: Decreased experimental burden through principled sequence selection

### 3.4 Broader Implications

The CLAM framework is generalizable beyond mRNA to other therapeutic modalities including:
- Antisense oligonucleotide design
- CRISPR guide RNA optimization
- Therapeutic aptamer development

By demonstrating the value of closed-loop optimization with foundation model embeddings, this work establishes a template for AI-driven therapeutic design across emerging drug modalities.

### 3.5 Limitations and Future Directions

**Current Limitations**:
- Requires ribosome profiling capability (specialized equipment)
- LNP delivery held constant; joint optimization is future work
- In vitro validation only; in vivo translation requires additional studies

**Future Directions**:
- Extension to joint sequence-delivery optimization
- Transfer learning across cell types and therapeutic targets
- Integration with automated wet-lab platforms for fully autonomous optimization