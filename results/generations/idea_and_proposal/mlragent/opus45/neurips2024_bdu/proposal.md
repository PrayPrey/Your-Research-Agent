# Research Proposal: LLM-Guided Adaptive Prior Construction for High-Dimensional Bayesian Optimization

## 1. Introduction

### Background

Bayesian optimization (BO) has emerged as a powerful paradigm for optimizing expensive black-box functions, achieving remarkable success in hyperparameter tuning, drug discovery, and experimental design. At its core, BO employs a probabilistic surrogate model—typically a Gaussian process (GP)—to model the objective function and an acquisition function to guide sequential sampling decisions. This principled framework naturally quantifies uncertainty, enabling intelligent exploration-exploitation trade-offs that minimize the number of expensive function evaluations required.

However, the effectiveness of standard BO degrades significantly as the dimensionality of the search space increases—a phenomenon known as the curse of dimensionality. In high-dimensional settings (e.g., 50-1000 dimensions), the volume of the search space grows exponentially, making both surrogate modeling and acquisition function optimization increasingly challenging. Traditional GP priors, which often assume stationary kernels with isotropic length scales, fail to capture the complex structure inherent in many real-world high-dimensional problems, where only a subset of variables may be relevant or where intricate variable interactions exist.

Recent work has explored various strategies to address this limitation, including adaptive dropout methods (Huang & Zhan, 2025), Lasso-based variable selection (Hoang et al., 2025), and principled length-scale scaling (Hvarfner et al., 2024). While these approaches have shown promise, they primarily rely on data-driven techniques that require substantial initial samples to discover problem structure. Simultaneously, large language models (LLMs) have demonstrated remarkable capabilities in encoding and reasoning about scientific knowledge, including understanding of function landscapes from vast corpora of scientific literature, code repositories, and experimental reports. This presents an unprecedented opportunity: leveraging LLMs to inject domain knowledge into BO priors, potentially accelerating optimization in high-dimensional spaces before observing any function evaluations.

### Research Objectives

This research proposes **LLM-Prior BO**, a novel framework that bridges the gap between the semantic knowledge encoded in LLMs and the probabilistic machinery of Bayesian optimization. Our specific objectives are:

1. **Develop a systematic methodology** for translating LLM-generated structural hypotheses about optimization problems into mathematically rigorous GP priors with structured kernel decompositions.

2. **Design an adaptive prior refinement mechanism** that iteratively updates the LLM's structural hypotheses based on observed function evaluations, enabling online learning of problem structure.

3. **Establish theoretical foundations** for incorporating LLM-derived prior information while maintaining valid uncertainty quantification.

4. **Demonstrate empirical effectiveness** on challenging high-dimensional benchmarks, including neural architecture search and molecular optimization tasks.

### Significance

This research addresses a critical gap in deploying BO for complex, high-dimensional problems encountered in scientific discovery and AI development. By harnessing the vast knowledge encoded in LLMs, we aim to achieve substantial improvements in sample efficiency—reducing the number of expensive evaluations required by 3-5×—while maintaining the principled uncertainty quantification that makes Bayesian methods trustworthy for critical applications. Furthermore, this work opens new avenues for human-AI collaborative experimental design, where domain expertise can be seamlessly integrated through natural language problem descriptions.

## 2. Methodology

### 2.1 Overview

The LLM-Prior BO framework operates in three main phases: (1) initial prior construction from LLM-generated structural hypotheses, (2) Bayesian optimization with structured GP priors, and (3) adaptive prior refinement based on observed data. Figure 1 illustrates the overall pipeline.

### 2.2 LLM-Guided Prior Construction

#### Problem Description Interface

Given an optimization problem, we first construct a structured prompt containing:
- **Task description**: Natural language description of the objective (e.g., "Optimize hyperparameters of a transformer model for text classification")
- **Variable specification**: Names, types, and ranges of all input dimensions
- **Domain context**: Relevant domain knowledge, constraints, and known relationships

#### Structural Hypothesis Generation

We prompt the LLM to generate three types of structural information:

**1. Important Subspace Identification**: The LLM identifies likely relevant variable subsets and their relative importance:
$$S = \{S_1, S_2, \ldots, S_K\} \text{ where } S_k \subseteq \{1, 2, \ldots, D\}$$
with associated importance weights $w_k \in [0, 1]$.

**2. Kernel Structure Suggestions**: For each identified subspace, the LLM suggests appropriate kernel forms:
$$k_{S_k}(x, x') \in \{\text{RBF}, \text{Matérn}_{1/2}, \text{Matérn}_{5/2}, \text{Periodic}, \text{Linear}\}$$

**3. Length-Scale Estimates**: Initial length-scale parameters $\ell_k$ for each subspace, normalized relative to the variable ranges.

#### Translation to Structured GP Prior

We translate LLM outputs into a compositional kernel structure:
$$k(x, x') = \sigma_f^2 \left( \sum_{k=1}^{K} w_k \cdot k_{S_k}(x_{S_k}, x'_{S_k}) + \lambda \cdot k_{\text{residual}}(x, x') \right)$$

where $k_{S_k}$ operates on the variable subset $S_k$, and $k_{\text{residual}}$ is an isotropic RBF kernel with large length scales to capture any structure not anticipated by the LLM. The mixing parameter $\lambda > 0$ ensures robustness against LLM errors.

For suggested variable interactions, we employ multiplicative kernel compositions:
$$k_{\text{interact}}(x, x') = k_{S_i}(x_{S_i}, x'_{S_i}) \cdot k_{S_j}(x_{S_j}, x'_{S_j})$$

### 2.3 Bayesian Optimization with LLM Priors

#### GP Posterior Computation

Given observations $\mathcal{D}_n = \{(x_i, y_i)\}_{i=1}^{n}$, we compute the GP posterior:
$$p(f(x) | \mathcal{D}_n) = \mathcal{N}(\mu_n(x), \sigma_n^2(x))$$

where:
$$\mu_n(x) = k(x, X)^T (K + \sigma_\epsilon^2 I)^{-1} y$$
$$\sigma_n^2(x) = k(x, x) - k(x, X)^T (K + \sigma_\epsilon^2 I)^{-1} k(x, X)$$

Here, $K$ is the kernel matrix computed using our structured kernel, and $\sigma_\epsilon^2$ represents observation noise.

#### Acquisition Function Optimization

We employ Expected Improvement (EI) as our primary acquisition function:
$$\alpha_{\text{EI}}(x) = \mathbb{E}[\max(f(x) - f^+, 0)]$$

where $f^+ = \max_{i \leq n} y_i$. Given the structured kernel, acquisition optimization benefits from the reduced effective dimensionality, as gradients flow primarily through the identified important subspaces. We optimize using multi-start L-BFGS-B with gradient projections onto the LLM-identified subspaces.

### 2.4 Adaptive Prior Refinement

A key innovation of LLM-Prior BO is the online refinement of structural hypotheses. After every $\tau$ observations (default $\tau = 5$), we prompt the LLM with an updated context:

**Refinement Prompt Structure**:
```
Previous hypotheses: [summarized kernel structure]
Observations: [top-k points with evaluations]
Correlation analysis: [empirical variable importance from GP hyperparameters]
Residual patterns: [description of unexplained variance]

Please refine structural hypotheses...
```

The LLM generates updated structural recommendations, which we integrate using a Bayesian model averaging approach:
$$k^{(t+1)}(x, x') = \beta \cdot k^{(t)}_{\text{LLM}}(x, x') + (1-\beta) \cdot k^{(t)}(x, x')$$

where $\beta \in [0, 1]$ controls the influence of new LLM suggestions, decaying over iterations to ensure convergence:
$$\beta_t = \beta_0 \cdot \gamma^t, \quad \gamma \in (0, 1)$$

### 2.5 Uncertainty Calibration

To maintain valid uncertainty quantification despite LLM-derived priors, we employ two mechanisms:

**1. Prior Robustification**: We add an uninformative component to all priors:
$$k_{\text{robust}}(x, x') = (1 - \epsilon) \cdot k_{\text{LLM}}(x, x') + \epsilon \cdot k_{\text{isotropic}}(x, x')$$

with $\epsilon = 0.1$ ensuring coverage even when LLM hypotheses are incorrect.

**2. Posterior Calibration**: We periodically validate uncertainty estimates using held-out observations and adjust the noise variance $\sigma_\epsilon^2$ to achieve calibrated credible intervals.

### 2.6 Experimental Design

#### Benchmark Tasks

We evaluate LLM-Prior BO on three categories of problems:

**1. Synthetic Benchmarks** (D = 50-200):
- Branin (embedded in 50D with irrelevant dimensions)
- Hartmann6 (embedded in 100D)
- Ackley (embedded in 200D with correlated variables)

**2. Hyperparameter Tuning** (D = 100-500):
- Transformer architecture search (hidden dims, layers, attention heads, dropout, learning rate schedules)
- ResNet configuration on CIFAR-100
- XGBoost on large-scale tabular datasets

**3. Molecular Optimization** (D = 256):
- Molecular fingerprint optimization for drug-likeness (QED score)
- Binding affinity optimization using molecular descriptors

#### Baselines

We compare against:
- **Vanilla BO**: Standard GP with RBF kernel
- **SAASBO**: Sparse axis-aligned subspace BO
- **TuRBO**: Trust-region BO for high dimensions
- **ALEBO**: Adaptive linear embedding BO
- **Dropout-BO**: Adaptive dropout method (Huang & Zhan, 2025)
- **Random Search**: With 10× budget

#### Evaluation Metrics

1. **Simple Regret**: $r_n = f^* - \max_{i \leq n} f(x_i)$ at iteration $n$
2. **Sample Efficiency Ratio**: Number of evaluations to reach target value relative to baselines
3. **Uncertainty Calibration**: Expected calibration error of 90% credible intervals
4. **Wall-clock Time**: Total computational overhead including LLM queries

#### Implementation Details

- **LLM Backend**: GPT-4 or Claude-3 with temperature 0.3 for structured generation
- **GP Implementation**: GPyTorch with automatic differentiation
- **Optimization Budget**: 200 evaluations per run
- **Repetitions**: 20 independent runs per configuration
- **Statistical Tests**: Wilcoxon signed-rank tests for significance

## 3. Expected Outcomes & Impact

### Expected Results

We anticipate the following outcomes:

1. **Sample Efficiency Gains**: LLM-Prior BO is expected to achieve 3-5× improvement in sample efficiency on high-dimensional benchmarks, reaching target function values with significantly fewer evaluations than existing methods. This improvement should be most pronounced in the early stages of optimization (first 50-100 evaluations), where informative priors have the greatest impact.

2. **Robust Uncertainty Quantification**: Despite incorporating LLM-derived knowledge, the framework should maintain well-calibrated uncertainty estimates, with expected calibration errors below 5% for 90% credible intervals.

3. **Adaptive Structure Discovery**: The online refinement mechanism should demonstrate the ability to correct initial LLM misconceptions, converging to accurate structural hypotheses as data accumulates.

4. **Generalizable Framework**: The methodology should transfer across problem domains, with the LLM successfully generating relevant priors for hyperparameter tuning, molecular optimization, and other scientific applications without domain-specific engineering.

### Broader Impact

This research has significant implications for several areas:

**Scientific Discovery**: By dramatically reducing the sample complexity of high-dimensional optimization, LLM-Prior BO could accelerate drug discovery, materials science, and other domains where each experiment is costly and time-consuming.

**Democratization of BO**: The natural language interface lowers the barrier to entry for practitioners who lack expertise in kernel design, making advanced BO techniques accessible to domain experts across fields.

**Human-AI Collaboration**: This work establishes a paradigm for integrating human knowledge (via LLMs trained on human-generated content) with principled probabilistic methods, opening new directions for collaborative experimental design.

**Theoretical Foundations**: The framework provides a testbed for studying how to formally incorporate LLM-derived knowledge into Bayesian methods while maintaining theoretical guarantees, a challenge of growing importance as LLMs become ubiquitous in scientific workflows.

### Limitations and Future Work

We acknowledge potential limitations: LLM suggestions may be unreliable for highly novel problems outside their training distribution, and computational overhead from LLM queries may be significant for very fast objective functions. Future work will explore fine-tuning LLMs specifically for prior generation, developing theoretical regret bounds that account for prior quality, and extending the framework to multi-objective and constrained optimization settings.

In summary, LLM-Prior BO represents a significant step toward harnessing the complementary strengths of large language models and Bayesian methods, with the potential to transform how we approach complex optimization problems in science and engineering.