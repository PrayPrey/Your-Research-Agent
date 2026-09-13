# Research Proposal: Adaptive Difficulty Calibration for Mathematical Reasoning Benchmarks via Student-Teacher LLM Dynamics

## 1. Introduction

### Background

Mathematical reasoning represents one of the most challenging frontiers in artificial intelligence research. Unlike pattern recognition tasks where deep learning has achieved remarkable success, mathematical reasoning requires symbolic manipulation, logical inference, and the ability to generalize abstract concepts to novel situations. Recent advancements in large language models (LLMs) have demonstrated unprecedented capabilities in solving mathematical problems, from elementary arithmetic to competition-level mathematics. However, this rapid progress has exposed a critical flaw in our evaluation methodology: static benchmarks become saturated quickly, creating an illusion of continuous improvement while potentially masking fundamental limitations in genuine reasoning capabilities.

The evaluation crisis manifests in several ways. First, benchmark contamination through training data overlap leads to inflated performance metrics. Second, models may exploit superficial patterns rather than developing true mathematical understanding—a phenomenon that static test sets cannot reliably detect. Third, as models improve, existing benchmarks lose their discriminative power, making it impossible to distinguish between incremental improvements and genuine breakthroughs in reasoning capabilities. Recent works such as SMART, Mathador-LM, and DyVal have begun addressing these challenges through dynamic evaluation frameworks, yet they lack mechanisms for continuous self-calibration that can keep pace with the rapid evolution of LLM capabilities.

### Research Objectives

This research proposes a novel self-calibrating benchmark system that leverages adversarial student-teacher dynamics between LLMs to create evaluation frameworks that adapt to model capabilities while maintaining consistent difficulty calibration. Our specific objectives are:

1. **Develop a difficulty-conditioned problem generator** trained via reinforcement learning to produce mathematical problems at precisely calibrated difficulty levels.

2. **Design a dynamic Item Response Theory (IRT) model** that continuously updates difficulty estimates based on empirical solving performance across diverse model populations.

3. **Create "boundary problem" generation mechanisms** that specifically probe the limits of current models to detect reasoning shortcuts and capability boundaries.

4. **Validate the framework's effectiveness** in maintaining benchmark discriminability and producing fine-grained capability profiles across mathematical subdomains.

### Significance

This research addresses fundamental challenges in measuring mathematical reasoning progress. By creating benchmarks that adapt to model improvements rather than becoming obsolete, we enable more reliable tracking of genuine advances in AI mathematical reasoning. The proposed framework has implications beyond evaluation—understanding where models truly struggle versus where they merely fail to generalize can guide research toward more robust reasoning architectures. Furthermore, the methodology generalizes to other reasoning domains, potentially establishing a new paradigm for dynamic evaluation in AI research.

## 2. Methodology

### 2.1 System Architecture Overview

Our framework consists of three interconnected components: (1) a Teacher LLM serving as a difficulty-conditioned problem generator, (2) a population of Student LLMs acting as solvers, and (3) a Dynamic IRT Calibration Module that maintains and updates difficulty estimates. These components interact through a continuous feedback loop, enabling the system to self-calibrate over time.

### 2.2 Difficulty-Conditioned Problem Generator

#### Architecture

The Teacher LLM is fine-tuned from a capable base model (e.g., GPT-4 or DeepSeek) to generate mathematical problems conditioned on three inputs: (1) target difficulty level $d \in [0, 1]$, (2) mathematical subdomain $s \in \mathcal{S}$ (e.g., algebra, geometry, number theory), and (3) problem structure template $t \in \mathcal{T}$.

The generation process is formalized as:

$$P(problem | d, s, t) = \text{TeacherLLM}(d, s, t; \theta_T)$$

where $\theta_T$ represents the teacher model's parameters.

#### Reinforcement Learning Training

We train the Teacher using Proximal Policy Optimization (PPO) with a reward function designed to achieve target solve rates. Let $\hat{p}(problem)$ denote the empirical solve rate of a generated problem across the student population. The reward function is:

$$R(problem, d) = -\lambda_1 |d - \hat{p}(problem)| - \lambda_2 \cdot \mathbb{1}[\text{invalid}(problem)] + \lambda_3 \cdot \text{diversity}(problem)$$

where:
- The first term penalizes deviation from target solve rate (higher $d$ means easier problems)
- The second term penalizes invalid or ambiguous problems
- The third term rewards novel problem structures to prevent repetition

The diversity measure is computed using embedding-based similarity:

$$\text{diversity}(problem) = 1 - \max_{p' \in \mathcal{B}} \cos(\phi(problem), \phi(p'))$$

where $\mathcal{B}$ is a buffer of recently generated problems and $\phi(\cdot)$ produces problem embeddings.

### 2.3 Dynamic Item Response Theory Model

We employ a multi-dimensional IRT framework to maintain calibrated difficulty estimates. For each problem $i$ and model $j$, the probability of correct response is modeled as:

$$P(X_{ij} = 1 | \theta_j, a_i, b_i, c_i) = c_i + \frac{1 - c_i}{1 + e^{-a_i(\theta_j - b_i)}}$$

where:
- $\theta_j$ is the ability parameter of model $j$
- $b_i$ is the difficulty parameter of problem $i$
- $a_i$ is the discrimination parameter
- $c_i$ is the pseudo-guessing parameter

#### Continuous Calibration Update

As new solving attempts are recorded, we update the IRT parameters using online expectation-maximization. For a mini-batch of $N$ new responses, the difficulty update is:

$$b_i^{(t+1)} = b_i^{(t)} + \eta \sum_{j=1}^{N} (X_{ij} - P_{ij})$$

where $P_{ij}$ is the predicted probability and $\eta$ is the learning rate.

We extend the standard IRT model to multi-dimensional abilities to capture performance across mathematical subdomains:

$$\theta_j = [\theta_j^{(1)}, \theta_j^{(2)}, ..., \theta_j^{(K)}]$$

where $K$ is the number of mathematical subdomains. This enables fine-grained capability profiling.

### 2.4 Boundary Problem Generation

To detect reasoning shortcuts and probe capability limits, we introduce a boundary problem generation mechanism. The key insight is that problems near a model's capability boundary are most informative for evaluation.

#### Adaptive Targeting Algorithm

For a target model with estimated ability $\hat{\theta}$, we generate problems at difficulty levels clustered around the boundary:

$$d_{target} = \Phi^{-1}(0.5 + \epsilon \cdot U(-1, 1))$$

where $\Phi^{-1}$ is the inverse of the IRT response function and $\epsilon$ controls the spread around the 50% solve rate boundary.

#### Shortcut Detection Module

We identify potential reasoning shortcuts by generating problem variants that preserve mathematical structure but alter surface features. For a problem $p$, we generate perturbations:

$$p' = \text{Perturb}(p, \text{type})$$

where perturbation types include: variable renaming, numerical value substitution, context reframing, and step ordering changes.

A model exhibits shortcut behavior if:

$$|P(\text{correct}|p) - P(\text{correct}|p')| > \tau_{shortcut}$$

for mathematically equivalent problems.

### 2.5 Experimental Design

#### Data Collection

We initialize the system with seed problems from existing benchmarks (MATH, GSM8K, MMLU-Math) covering diverse difficulty levels and subdomains. The student population includes:
- Open-source models: LLaMA-2 (7B, 13B, 70B), Mistral-7B, DeepSeek-Math
- API-based models: GPT-3.5-turbo, GPT-4, Claude-3

Each generated problem undergoes validation through:
1. Syntax checking for mathematical well-formedness
2. Solution verification using symbolic computation (SymPy)
3. Ambiguity detection via multi-model consensus

#### Training Protocol

**Phase 1 - Teacher Pre-training (2 weeks):**
- Fine-tune base model on curated problem-solution pairs with difficulty annotations
- Initial dataset: 50,000 problems with human-annotated difficulty levels

**Phase 2 - RL Training (4 weeks):**
- PPO training with student population feedback
- Generate 1,000 problems per iteration, collect 10 solving attempts per problem
- Update teacher every 100 iterations

**Phase 3 - Continuous Calibration (Ongoing):**
- Deploy IRT model with continuous updates
- Re-calibrate difficulty estimates weekly
- Generate boundary problems for new models within 24 hours of release

#### Evaluation Metrics

1. **Calibration Accuracy**: Mean absolute error between target and empirical solve rates
$$\text{MAE}_{cal} = \frac{1}{N}\sum_{i=1}^{N}|d_i - \hat{p}_i|$$

2. **Discrimination Index**: Correlation between model ability estimates and solve rates
$$\rho(\theta, \hat{p})$$

3. **Temporal Stability**: Consistency of difficulty estimates over time
$$\sigma_{temporal} = \text{std}(b_i^{(t)} - b_i^{(t-1)})$$

4. **Shortcut Detection Rate**: Proportion of identified shortcuts confirmed by manual analysis

5. **Capability Profile Accuracy**: Agreement between predicted and observed subdomain performance patterns

#### Baseline Comparisons

We compare against:
- Static benchmarks (MATH, GSM8K)
- Existing dynamic frameworks (DyVal, Mathador-LM, DARG)
- Random problem generation with post-hoc difficulty filtering

#### Ablation Studies

We conduct ablations on:
- RL reward components (calibration vs. diversity vs. validity)
- IRT model complexity (1PL vs. 2PL vs. 3PL)
- Student population diversity
- Update frequency for difficulty calibration

## 3. Expected Outcomes & Impact

### Expected Outcomes

1. **Self-Calibrating Benchmark System**: A fully operational framework capable of generating problems at any target difficulty level with calibration error below 5% solve rate deviation.

2. **Fine-Grained Capability Profiles**: Detailed multi-dimensional assessments of LLM mathematical reasoning across 10+ subdomains, revealing previously hidden strengths and weaknesses.

3. **Shortcut Detection Toolkit**: Automated identification of reasoning shortcuts with expected detection precision above 80%, enabling researchers to distinguish genuine understanding from pattern exploitation.

4. **Longitudinal Progress Tracking**: A methodology for meaningful comparison of model capabilities over time, accounting for benchmark adaptation and difficulty recalibration.

5. **Open-Source Release**: Public release of the framework, including trained teacher models, IRT calibration code, and a continuously updated problem repository.

### Scientific Impact

This research contributes to the fundamental question motivating the workshop: "To what extent can machine learning models comprehend mathematics?" By creating evaluation tools that adapt to model improvements while detecting superficial pattern matching, we provide more precise instruments for measuring genuine mathematical understanding. The boundary problem generation mechanism specifically addresses the challenge of distinguishing true comprehension from memorization or shortcut exploitation.

### Practical Applications

**Education**: The difficulty-calibrated problem generation can power adaptive learning systems, particularly valuable in resource-limited contexts where personalized tutoring is unavailable.

**Model Development**: Fine-grained capability profiles enable targeted improvements in model training, identifying specific mathematical reasoning skills requiring attention.

**Benchmarking Standards**: The framework establishes a new paradigm for dynamic evaluation that may extend beyond mathematical reasoning to other complex reasoning domains.

### Broader Impact

As LLMs become increasingly integrated into scientific discovery, engineering, and finance, reliable assessment of their mathematical reasoning becomes critical for safe deployment. This research provides tools to ensure that reported capabilities accurately reflect genuine understanding, preventing potentially dangerous over-reliance on systems with hidden reasoning limitations. The methodology also democratizes advanced evaluation, allowing smaller research groups to rigorously assess mathematical reasoning without requiring extensive human annotation resources.