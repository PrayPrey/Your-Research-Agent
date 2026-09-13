# Research Proposal: Phase Transitions in In-Context Learning: A Statistical Mechanics Framework for Emergent Capabilities

## 1. Introduction

### 1.1 Background

Large language models (LLMs) have revolutionized artificial intelligence, demonstrating remarkable capabilities across diverse tasks including reasoning, translation, and code generation. Among the most intriguing phenomena exhibited by these models is in-context learning (ICL)—the ability to perform new tasks by conditioning on a few demonstration examples without any parameter updates. This capability emerges seemingly spontaneously as models scale, representing one of the most significant yet poorly understood aspects of modern deep learning.

Current scaling laws, exemplified by Kaplan et al.'s (2020) power-law relationships between model size and loss, predict smooth, continuous improvements in model performance. However, these laws fundamentally fail to explain the abrupt emergence of ICL capabilities at specific model scales. Models below certain thresholds exhibit virtually no ICL ability, while models exceeding these thresholds demonstrate robust few-shot learning—a discontinuity that smooth scaling laws cannot capture. This theoretical gap has profound practical implications: training billion-parameter models involves enormous computational costs, and the inability to predict when capabilities will emerge forces practitioners into expensive trial-and-error approaches.

The phenomenon of sudden capability emergence bears striking resemblance to phase transitions in statistical mechanics, where systems undergo qualitative changes in behavior at critical points. In physical systems, phase transitions are characterized by order parameters that exhibit power-law scaling near critical points, with universal critical exponents that depend only on broad symmetry classes rather than microscopic details. Recent theoretical work has begun exploring connections between deep learning dynamics and statistical physics, including analyses of loss landscape geometry and the role of saddle points in training dynamics.

### 1.2 Research Objectives

This research aims to develop and validate a statistical mechanics framework for understanding the emergence of in-context learning capabilities in large language models. Our specific objectives are:

1. **Establish the existence of phase transitions in ICL emergence** by defining and measuring an order parameter based on attention-task mutual information across multiple model scales.

2. **Characterize the universality of critical behavior** by testing whether critical exponents remain consistent across different architecture families, supporting the hypothesis that ICL emergence follows universal scaling laws.

3. **Quantify the role of task diversity** in modulating critical thresholds, providing actionable insights for training data curation.

4. **Compare the phase transition framework against existing baselines** including broken neural scaling laws (BSNL) to establish superior predictive power.

### 1.3 Significance

This research addresses a critical gap between deep learning theory and practice identified as a central challenge in modern machine learning. By providing a principled framework for predicting capability emergence, this work would:

- **Enable efficient resource allocation** by predicting the minimum model scale required for specific capabilities, potentially saving millions of dollars in training costs.
- **Guide architecture design** by identifying which structural features influence critical thresholds.
- **Advance theoretical understanding** by connecting emergent phenomena in deep learning to well-established physics frameworks.
- **Provide falsifiable predictions** that can guide future theoretical investigations, regardless of whether the hypothesis is confirmed or refuted.

## 2. Methodology

### 2.1 Theoretical Framework

#### 2.1.1 Order Parameter Definition

We define the order parameter $\psi(N, D)$ as the normalized mutual information between attention patterns and task identity across a set of in-context learning tasks:

$$\psi(N, D) = \frac{1}{|C|} \sum_{c \in C} \frac{I(A_c^{[l^*]}; T_c)}{H(T_c)}$$

where:
- $C$ is the set of ICL evaluation tasks
- $A_c^{[l^*]}$ represents attention patterns at the optimal layer $l^*$ for task $c$
- $T_c$ is the task identity variable
- $I(\cdot; \cdot)$ denotes mutual information
- $H(\cdot)$ denotes entropy

The optimal layer $l^*$ is selected as the layer maximizing average mutual information across tasks:

$$l^* = \arg\max_l \frac{1}{|C|} \sum_{c \in C} I(A_c^{[l]}; T_c)$$

#### 2.1.2 Phase Transition Hypothesis

We hypothesize that near the critical scale $N^*(D)$, the order parameter exhibits power-law scaling:

$$\psi(N, D) \sim (N - N^*(D))^\beta \quad \text{for } N > N^*(D)$$

with universal critical exponent $\beta \approx 0.5$. The susceptibility, defined as:

$$\chi(N, D) = \frac{\partial^2 \psi}{\partial N^2}$$

should exhibit a peak at $N = N^*(D)$, analogous to divergent susceptibility at phase transitions in physical systems.

#### 2.1.3 Task Diversity Dependence

We model the critical scale as a function of task diversity:

$$N^*(D) = N_0 \cdot D^{-\gamma}$$

where $N_0$ is a baseline critical scale and $\gamma > 0$ captures how increased task diversity lowers the threshold for ICL emergence.

### 2.2 Data Collection

#### 2.2.1 Model Selection

We will evaluate models across three architecture families with at least 8 scale points each:

**Family 1: GPT-style (Decoder-only)**
- GPT-2 variants: 117M, 345M, 762M, 1.5B
- GPT-Neo/GPT-J: 2.7B, 6B
- Llama family: 7B, 13B, 33B, 70B

**Family 2: Encoder-Decoder**
- T5 variants: 60M, 220M, 770M, 3B, 11B
- FLAN-T5 variants for comparison

**Family 3: Alternative Architectures**
- Mamba (state-space models): 130M, 370M, 790M, 1.4B, 2.8B
- RWKV variants for recurrent comparison

#### 2.2.2 Task Diversity Manipulation

We construct four task diversity levels:

| Level | D Value | Task Categories |
|-------|---------|-----------------|
| Low | 10 | Single domain (e.g., sentiment only) |
| Medium | 50 | 5 domains, 10 tasks each |
| High | 200 | 20 domains, 10 tasks each |
| Very High | 1000 | Full benchmark suite |

Task categories include: sentiment analysis, natural language inference, question answering, translation, summarization, arithmetic, logical reasoning, code completion, and commonsense reasoning.

#### 2.2.3 Evaluation Benchmarks

Primary ICL evaluation will use:
- BIG-Bench Hard (23 challenging tasks)
- MMLU (57 subjects)
- Custom synthetic tasks with controlled complexity

### 2.3 Algorithmic Procedures

#### 2.3.1 Mutual Information Estimation

For each model and task, we estimate mutual information using the MINE (Mutual Information Neural Estimation) framework:

**Algorithm 1: Order Parameter Computation**

```
Input: Model M with N parameters, task set C, layer range L
Output: Order parameter ψ(N, D)

1. For each layer l in L:
   a. For each task c in C:
      i. Sample K prompts with demonstrations
      ii. Extract attention patterns A_c^[l] ∈ R^{K × H × S × S}
         (K samples, H heads, S sequence length)
      iii. Flatten to feature vectors: a_c^[l] ∈ R^{K × d}
      iv. Estimate I(A_c^[l]; T_c) using MINE:
          - Train discriminator D_θ to distinguish (a, t) pairs
          - MI estimate: Î = E_P[D_θ] - log(E_Q[e^{D_θ}])
   b. Compute layer score: S_l = (1/|C|) Σ_c Î(A_c^[l]; T_c)

2. Select optimal layer: l* = argmax_l S_l

3. Compute normalized order parameter:
   ψ(N, D) = (1/|C|) Σ_c Î(A_c^[l*]; T_c) / H(T_c)

4. Return ψ(N, D)
```

#### 2.3.2 Critical Point Identification

**Algorithm 2: Critical Scale Detection**

```
Input: Order parameters {ψ(N_i, D)}_i for scale points {N_i}
Output: Critical scale N*(D), critical exponent β

1. Compute numerical second derivative (susceptibility):
   χ(N_i) = (ψ(N_{i+1}) - 2ψ(N_i) + ψ(N_{i-1})) / (ΔN)^2

2. Identify candidate N* as argmax_i χ(N_i)

3. For scales N > N*:
   a. Fit power-law model: log(ψ) = β·log(N - N*) + c
   b. Use nonlinear least squares with N* as free parameter
   c. Optimize: (N*, β, c) = argmin Σ_i (ψ_i - (N_i - N*)^β · e^c)^2

4. Compute goodness of fit: R^2, confidence intervals

5. Return N*, β with 95% CI
```

#### 2.3.3 Baseline Comparison

We compare against the Broken Neural Scaling Law (BSNL) model:

$$\psi_{BSNL}(N) = \begin{cases} a_1 N^{-\alpha_1} + c_1 & N < N_{break} \\ a_2 N^{-\alpha_2} + c_2 & N \geq N_{break} \end{cases}$$

Model comparison uses Akaike Information Criterion (AIC) and Bayesian Information Criterion (BIC):

$$AIC = 2k - 2\ln(\hat{L})$$
$$BIC = k\ln(n) - 2\ln(\hat{L})$$

where $k$ is the number of parameters, $n$ is the number of data points, and $\hat{L}$ is the maximum likelihood.

### 2.4 Experimental Design

#### 2.4.1 Experiment 1: Phase Transition Existence (Primary)

**Objective:** Test whether ψ(N, D) exhibits phase transition behavior.

**Procedure:**
1. Compute ψ for all GPT-family models at fixed D = 200
2. Identify N* via susceptibility peak
3. Fit power-law model for N > N*
4. Validate ICL correlation: compute Spearman ρ between ψ and ICL accuracy

**Success Criteria:**
- Power-law fit R² > 0.9
- Identifiable susceptibility peak
- Spearman ρ(ψ, ICL accuracy) > 0.7

#### 2.4.2 Experiment 2: Universality Test

**Objective:** Test whether β is universal across architectures.

**Procedure:**
1. Repeat Experiment 1 for all three architecture families
2. Extract β estimates with confidence intervals
3. Test for consistency: H₀: all β values equal

**Success Criteria:**
- std(β) < 0.15 across families
- All β within 0.5 ± 0.1

#### 2.4.3 Experiment 3: Task Diversity Dependence

**Objective:** Quantify relationship between D and N*.

**Procedure:**
1. For each diversity level D ∈ {10, 50, 200, 1000}:
   a. Compute ψ(N, D) across all scales
   b. Identify N*(D)
2. Fit: log(N*) = -γ·log(D) + log(N₀)
3. Compute correlation coefficient

**Success Criteria:**
- Pearson r < -0.7 (strong negative correlation)
- γ > 0 with p < 0.05

#### 2.4.4 Experiment 4: Baseline Comparison

**Objective:** Compare phase transition model against BSNL.

**Procedure:**
1. Fit both models to ψ(N) data
2. Compute AIC, BIC for each
3. Perform likelihood ratio test

**Success Criteria:**
- ΔAIC > 10 favoring phase transition model
- ΔBIC > 10 favoring phase transition model

### 2.5 Evaluation Metrics

| Metric | Description | Threshold |
|--------|-------------|-----------|
| R² (power-law) | Goodness of fit for ψ ~ (N-N*)^β | > 0.9 |
| β estimate | Critical exponent | 0.5 ± 0.1 |
| std(β) | Cross-architecture consistency | < 0.15 |
| Spearman ρ | ψ-ICL correlation | > 0.7 |
| Pearson r | N*-D correlation | < -0.7 |
| ΔAIC | Model comparison | > 10 |

## 3. Expected Outcomes & Impact

### 3.1 Expected Outcomes

**Primary Outcome:** We expect to identify clear phase transition behavior in the order parameter ψ(N, D), with susceptibility peaks at critical scales N*(D) that depend systematically on task diversity. Based on preliminary theoretical analysis and related empirical findings, we anticipate:

1. **Critical exponent β ≈ 0.5** consistent with mean-field universality class, suggesting that ICL emergence shares fundamental properties with second-order phase transitions in statistical mechanics.

2. **Task diversity scaling** with γ ≈ 0.3-0.5, implying that doubling task diversity reduces the critical scale by approximately 20-30%.

3. **Architecture-independent universality** with critical exponents consistent across GPT, T5, and alternative architectures, supporting the hypothesis that ICL emergence is governed by general principles rather than architecture-specific mechanisms.

**Alternative Outcomes:** If the phase transition hypothesis is falsified, we expect to find:
- Monotonically increasing ψ without identifiable critical points
- BSNL providing superior fit with fewer parameters
- Architecture-dependent scaling behavior

Either outcome provides valuable scientific insight into the nature of emergent capabilities.

### 3.2 Scientific Impact

This research will advance the theoretical foundations of deep learning by:

1. **Establishing connections to statistical physics:** Demonstrating that emergent capabilities follow phase transition dynamics would open new avenues for applying well-developed physics tools to deep learning analysis.

2. **Providing falsifiable predictions:** The framework generates specific, testable predictions about critical scales and exponents that can guide future theoretical work.

3. **Resolving theoretical tensions:** By directly comparing phase transition and BSNL frameworks, this work will clarify which mathematical formalism better captures capability emergence.

### 3.3 Practical Impact

The practical implications of this research include:

1. **Training efficiency:** Predicting N*(D) enables practitioners to determine minimum model sizes for desired capabilities, potentially reducing training costs by orders of magnitude.

2. **Data curation guidance:** Quantifying the N*-D relationship provides principled guidance for constructing pretraining datasets that lower capability thresholds.

3. **Architecture design:** Understanding which architectural features influence critical behavior can inform the design of more efficient model architectures.

### 3.4 Limitations and Future Directions

We acknowledge several limitations that suggest future research directions:

1. **Computational constraints:** MI estimation at 70B scale may require approximations; future work should develop more efficient estimation methods.

2. **Scope limitations:** This framework applies specifically to transformer-based ICL; extensions to other architectures and capabilities require additional investigation.

3. **Causal mechanism validation:** While we characterize the phenomenology of phase transitions, fully validating the proposed 4-step causal mechanism requires targeted intervention experiments beyond this initial study.

This research represents a significant step toward building a mathematical theory of machine learning that can both explain and inspire modern practice, directly addressing the workshop's central mission of bridging deep learning theory and practice.