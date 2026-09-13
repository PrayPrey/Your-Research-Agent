# Research Proposal: Curriculum-Trained Compute Value Estimators for Test-Time Compute Extrapolation in LLM Reasoning

## 1. Introduction

### 1.1 Background

Large language models (LLMs) have demonstrated remarkable capabilities in complex reasoning tasks, from mathematical problem-solving to code generation. Recent advances, exemplified by OpenAI's o1 model, have shown that extended chain-of-thought reasoning can significantly improve performance on challenging problems. However, a fundamental tension exists in deploying these reasoning-capable models: allocating fixed compute budgets wastes resources on simple problems while potentially under-serving complex ones, yet current adaptive methods rely on training-free heuristics that cannot generalize beyond observed patterns.

Existing approaches to adaptive test-time compute (TTC) allocation fall into two categories. First, entropy-based heuristics such as HALT-CoT and EAGER use token probability distributions to signal stopping points, achieving 15-30% token reduction but lacking any mechanism for extrapolation beyond training-time reasoning patterns. Second, fixed-budget methods allocate predetermined token limits regardless of problem difficulty, leading to inefficiency on easy problems and potential failure on hard ones. Neither approach addresses the critical challenge of enabling models to "think longer" on novel hard problems—to reliably scale reasoning beyond what was observed during training.

This limitation has significant practical implications. In resource-constrained deployment settings, inefficient compute allocation increases costs and latency. More fundamentally, the inability to extrapolate reasoning prevents models from tackling problems that require deeper thinking than any training example demonstrated. As LLMs are increasingly applied to open-ended scientific reasoning and complex planning tasks, this extrapolation capability becomes essential.

### 1.2 Research Objectives

This research proposes to develop and validate **Compute Value Estimators (CVEs)**—lightweight neural heads that predict expected accuracy improvement from additional reasoning tokens—trained using a novel **curriculum multi-budget reinforcement learning** framework. Our specific objectives are:

1. **Design and implement CVE architecture**: Create a parameter-efficient mechanism (~0.001% overhead) that queries LLM hidden states to predict compute value.

2. **Develop curriculum multi-budget RL training**: Establish a progressive training protocol that expands token budget ranges (50→500→1000→2000 tokens) to learn budget-invariant value estimation.

3. **Demonstrate reliable extrapolation**: Achieve test-time compute scaling to 2-10x training budgets with extrapolation coefficient >1.0.

4. **Validate efficiency gains**: Achieve 40-60% token reduction on easy problems while maintaining accuracy.

5. **Ensure calibration quality**: Produce well-calibrated predictions with Expected Calibration Error (ECE) <0.15.

### 1.3 Significance

This research addresses a fundamental gap in LLM reasoning capabilities with both theoretical and practical significance. Theoretically, we establish that compute value is learnable from hidden state representations and that curriculum training enables out-of-distribution generalization to unseen budget ranges. Practically, our approach enables more efficient deployment of reasoning-capable LLMs while simultaneously expanding their problem-solving capabilities to harder problems than seen during training.

The proposed method aligns directly with multiple workshop themes: training methodologies for enhancing reasoning (curriculum RL), inference time scaling for complex tasks (adaptive compute allocation), and benchmarking reasoning capabilities (extrapolation metrics). Success would provide a principled framework for adaptive test-time compute that the community can build upon.

## 2. Methodology

### 2.1 Compute Value Estimator Architecture

The CVE is designed as a lightweight head attached to a frozen pretrained LLM. Given hidden states $\mathbf{h}_t \in \mathbb{R}^d$ at reasoning step $t$, the CVE predicts the probability of accuracy improvement from $K$ additional tokens:

$$P_{\text{improve}}(K | \mathbf{h}_t) = \sigma(\mathbf{W} \cdot \text{pool}(\mathbf{h}_{t-w:t}) + b)$$

where $\mathbf{W} \in \mathbb{R}^{1 \times d}$ is a learnable weight matrix, $b$ is a bias term, $\sigma$ is the sigmoid activation, and $\text{pool}(\cdot)$ applies mean pooling over the last $w=10$ token hidden states to capture recent reasoning context.

The CVE is queried every $\Delta=50$ tokens during generation. Reasoning continues if $P_{\text{improve}}(K) > \theta$ for threshold $\theta \in \{0.2, 0.3, 0.4\}$, and terminates otherwise. This design ensures minimal computational overhead while providing frequent decision points.

**Parameter Overhead Analysis**: For a model with hidden dimension $d=4096$ (e.g., Llama-3-8B), the CVE adds $4096 + 1 = 4097$ parameters, representing approximately 0.00005% of the base model's 8 billion parameters.

### 2.2 Curriculum Multi-Budget Reinforcement Learning

The key innovation is training the CVE through progressive budget expansion, enabling it to learn budget-invariant value estimation that generalizes to unseen budget ranges.

**Training Phases**:

| Phase | Budget Range | Transition Criterion | Duration |
|-------|--------------|---------------------|----------|
| 1 | [50, 500] tokens | >80% max-budget accuracy | ~5000 steps |
| 2 | [100, 1000] tokens | >80% max-budget accuracy | ~5000 steps |
| 3 | [200, 2000] tokens | Convergence | ~10000 steps |

**RL Formulation**: We formulate CVE training as a Markov Decision Process where:
- **State** $s_t$: Current hidden states $\mathbf{h}_t$ and tokens generated so far
- **Action** $a_t \in \{\text{continue}, \text{stop}\}$: Binary decision based on CVE prediction
- **Reward** $r_t$: Combination of accuracy and efficiency signals

The reward function balances correctness and efficiency:

$$r(s_T, a_T) = \mathbb{1}[\text{correct}] - \lambda_{\text{eff}} \cdot \frac{T}{B_{\max}}$$

where $T$ is the total tokens used, $B_{\max}$ is the maximum budget for the current phase, and $\lambda_{\text{eff}} \in [0.1, 0.3]$ controls the efficiency penalty.

**Dense Intermediate Rewards**: To stabilize RL training, we provide intermediate rewards every $\Delta$ tokens:

$$r_{\text{intermediate}}(s_t) = \alpha \cdot \text{SC}_t + \beta \cdot \text{PRM}_t$$

where $\text{SC}_t$ is the self-consistency score (agreement among sampled continuations) and $\text{PRM}_t$ is the process reward model score for the current reasoning step. We set $\alpha = 0.3$ and $\beta = 0.2$.

**Policy Gradient Update**: The CVE parameters are updated using REINFORCE with baseline:

$$\nabla_\theta J(\theta) = \mathbb{E}\left[\sum_{t} \nabla_\theta \log \pi_\theta(a_t | s_t) \cdot (R_t - V(s_t))\right]$$

where $R_t = \sum_{t'=t}^{T} \gamma^{t'-t} r_{t'}$ is the discounted return and $V(s_t)$ is a learned value baseline (separate small network).

**Curriculum Transition Logic**: Phase transition occurs when:

$$\frac{1}{N}\sum_{i=1}^{N} \mathbb{1}[\text{correct}_i \text{ at } B_{\max}] > 0.8$$

evaluated on a held-out validation set of $N=500$ problems.

### 2.3 Data Collection and Preparation

**Training Datasets**:
- **MetaMath** (Yu et al., 2023): 395K mathematical reasoning problems with step-by-step solutions, covering arithmetic, algebra, and competition mathematics.
- **CodeContests** (Li et al., 2022): 13K competitive programming problems with test cases for verification.

**Data Augmentation for Difficulty Control**: To ensure coverage across difficulty levels, we augment training data by:
1. Generating easier variants by simplifying numerical values
2. Creating harder variants by composing multiple problems
3. Labeling difficulty based on baseline model solve rates at fixed budgets

**Train/Validation/Test Splits**: 80%/10%/10% with stratification by difficulty level.

### 2.4 Experimental Design

**Base Models**: 
- Primary: Llama-3-8B-Instruct (frozen weights)
- Secondary: Qwen-2.5-7B-Instruct (for generalization testing)

**Evaluation Benchmarks**:
- **MATH** (Hendrycks et al., 2021): 5000 competition mathematics problems across 7 categories
- **GSM8K** (Cobbe et al., 2021): 8500 grade school math word problems
- **HumanEval** (Chen et al., 2021): 164 Python programming problems

**Baselines**:
1. **Fixed Budget**: Allocate maximum training budget (2000 tokens) to all problems
2. **HALT-CoT** (2025): Entropy-based stopping using token probability distributions
3. **REFRAIN** (2025): Adaptive stopping with self-consistency verification
4. **EAGER** (Scalena et al., 2025): Early exit based on confidence thresholds

**Evaluation Metrics**:

| Metric | Definition | Target |
|--------|------------|--------|
| **Extrapolation Coefficient** | $\frac{\text{Acc}@2x - \text{Acc}@1x}{\text{Acc}_{\text{baseline}}@2x - \text{Acc}_{\text{baseline}}@1x}$ | >1.0 |
| **Token Efficiency** | $\frac{\text{Tokens}_{\text{baseline}} - \text{Tokens}_{\text{CVE}}}{\text{Tokens}_{\text{baseline}}}$ on easy problems | 40-60% |
| **Expected Calibration Error** | $\sum_{b=1}^{B} \frac{n_b}{N} |P_{\text{predicted}}^b - P_{\text{actual}}^b|$ | <0.15 |
| **Pass@1 Accuracy** | Fraction of problems solved correctly | Maintain within 1% of oracle |

**Extrapolation Testing Protocol**:
1. Train CVE with maximum budget $B_{\text{train}} = 2000$ tokens
2. Evaluate at budgets $B_{\text{test}} \in \{2000, 4000, 6000, 8000, 10000, 20000\}$ tokens
3. Measure accuracy improvement curves and compare against baselines

### 2.5 Ablation Studies

**A1: Curriculum Necessity**
- Condition: Train with fixed budget [200, 2000] only (no curriculum)
- Prediction: Extrapolation coefficient drops below 0.5 at 2x budget

**A2: CVE Architecture Variants**
- Compare: Linear (proposed) vs. 2-layer MLP vs. Attention pooling
- Prediction: Linear achieves comparable performance with lowest overhead

**A3: Query Frequency**
- Compare: $\Delta \in \{25, 50, 100, 200\}$ tokens
- Prediction: $\Delta=50$ balances granularity and overhead

**A4: Reward Balance**
- Compare: $\lambda_{\text{eff}} \in \{0.0, 0.1, 0.2, 0.3, 0.5\}$
- Prediction: $\lambda_{\text{eff}} \in [0.1, 0.3]$ achieves best efficiency-accuracy tradeoff

### 2.6 Statistical Analysis Plan

**Sample Size Justification**: With 5 random seeds and 5 budget levels, we obtain $n=25$ measurements per condition. For Cohen's $d=0.5$ (medium effect) and power $=0.8$, this exceeds the minimum required $n=21$.

**Statistical Tests**:
- Primary comparison: Paired t-test with Bonferroni correction for multiple comparisons
- Effect size: Cohen's $d$ with 95% confidence intervals
- Significance threshold: $p < 0.05$ after correction

**Reporting Format**: All results reported as Mean ± Std with 95% CI, effect size, and p-value.

### 2.7 Implementation Details

**Training Infrastructure**: 8× NVIDIA A100 GPUs (80GB), estimated 16 GPU-hours for full curriculum training

**Hyperparameters**:
- Learning rate: $3 \times 10^{-4}$ with cosine decay
- Batch size: 32 problems
- Discount factor: $\gamma = 0.99$
- Gradient clipping: max norm 1.0

**Reproducibility**: All code, trained checkpoints, and evaluation scripts will be released under MIT license. Random seeds: {42, 123, 456, 789, 1024}.

## 3. Expected Outcomes & Impact

### 3.1 Expected Results

**Primary Outcome (P1 - Extrapolation)**: We expect CVE-guided reasoning to achieve extrapolation coefficient >1.0 at 2x training budget, meaning accuracy improvements exceed those of fixed-budget baselines when given additional compute. At 4x budget, we anticipate continued positive extrapolation (coefficient >0.8), with diminishing but positive returns up to 10x budget.

**Secondary Outcomes**:
- **P2 (Efficiency)**: 40-60% token reduction on problems solvable within 200 tokens by baseline, with accuracy maintained within 1 percentage point.
- **P3 (Calibration)**: ECE <0.15 across all budget ranges, indicating CVE predictions reliably reflect true improvement probabilities.
- **P4 (Ablation)**: Removing curriculum training will cause extrapolation failure, validating the necessity of progressive budget expansion.

**Quantitative Targets**:

| Metric | HALT-CoT | REFRAIN | Fixed | **CVE (Ours)** |
|--------|----------|---------|-------|----------------|
| Token Reduction (easy) | 15-30% | 20-55% | 0% | **40-60%** |
| Extrapolation @2x | None | None | None | **>1.0** |
| Extrapolation @4x | None | None | None | **>0.8** |
| ECE | N/A | N/A | N/A | **<0.15** |

### 3.2 Potential Risks and Mitigation

**Risk 1: CVE fails to learn meaningful predictions**
- Detection: ECE >0.25 after Phase 1 training
- Mitigation: Increase hidden state context window, add attention pooling

**Risk 2: RL training instability**
- Detection: Reward variance increases over training
- Mitigation: Reduce learning rate, increase baseline network capacity, add entropy regularization

**Risk 3: Extrapolation plateaus early**
- Detection: No accuracy improvement beyond 3x budget
- Mitigation: Extend curriculum to Phase 4 with [500, 4000] budget range

### 3.3 Broader Impact

**Scientific Contributions**:
1. First demonstration that compute value is learnable from hidden states with sufficient calibration for adaptive control
2. Novel curriculum RL framework for training budget-invariant estimators
3. New evaluation methodology for test-time compute extrapolation

**Practical Applications**:
- **Cost-efficient deployment**: Reduce inference costs by 40-60% on routine queries while maintaining capability for hard problems
- **Latency optimization**: Enable real-time applications by early-stopping on easy problems
- **Capability expansion**: Allow models to tackle harder problems than seen during training

**Community Resources**:
- Open-source CVE training framework compatible with popular LLM architectures
- Benchmark suite for evaluating TTC extrapolation
- Pretrained CVE heads for Llama-3 and Qwen-2.5 families

### 3.4 Limitations and Future Work

**Current Limitations**:
- Requires access to hidden states (not applicable to black-box APIs)
- Separate CVE training needed for each base model architecture
- Extrapolation may plateau beyond 5-10x training budget

**Future Directions**:
1. **Multi-modal extension**: Train CVEs for vision-language models reasoning over images
2. **Transfer learning**: Investigate CVE transfer across model scales and architectures
3. **Collaborative reasoning**: Extend to multi-agent settings where CVE coordinates compute allocation across agents
4. **Causal reasoning**: Apply CVE framework to tasks requiring explicit causal inference

### 3.5 Conclusion

This research proposes a principled approach to adaptive test-time compute allocation through learned Compute Value Estimators trained with curriculum multi-budget reinforcement learning. By enabling reliable extrapolation beyond training budgets while maintaining efficiency on easy problems, our method addresses a fundamental limitation of current LLM reasoning systems. Success would establish a new paradigm for adaptive inference that balances efficiency and capability, with broad implications for deploying reasoning-capable LLMs in resource-constrained and open-ended problem-solving settings.