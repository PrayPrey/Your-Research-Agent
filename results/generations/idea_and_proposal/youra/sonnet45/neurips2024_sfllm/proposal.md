# Research Proposal: Entropy-Calibrated Conformal Prediction for Uncertainty Quantification in Auto-Regressive LLM Generation

## 1. Title

**Entropy-Calibrated Conformal Prediction for Uncertainty Quantification in Auto-Regressive LLM Generation: A Black-Box Statistical Framework with Formal Coverage Guarantees**

## 2. Introduction

### 2.1 Background

The deployment of Large Language Models (LLMs) in high-stakes applications—including medical diagnosis support, legal document generation, and automated customer service—demands rigorous uncertainty quantification (UQ) to mitigate operational risks. Traditional statistical methods assume access to model internals (weights, gradients) and rely on i.i.d. data assumptions, neither of which hold for modern foundation models deployed as black-box APIs. This fundamental mismatch between classical statistical theory and contemporary ML deployment practices creates a critical gap in our ability to provide reliability guarantees for production LLM systems.

Conformal Prediction (CP) has emerged as a promising distribution-free framework for UQ, providing finite-sample coverage guarantees without parametric assumptions. Recent work has adapted CP to LLM settings: COPU (Wang et al., 2025) applies logit-based nonconformity scoring to natural language generation, while CPQ (Noorani et al., 2025) develops query-only methods using missing mass estimators. However, these approaches face fundamental limitations when applied to auto-regressive text generation:

1. **Assumption Violations**: Existing methods assume i.i.d. calibration sets, which is violated by sequential dependencies in auto-regressive generation where each token depends on previous context.

2. **Static Nonconformity Measures**: Current scoring functions (logits, missing mass) do not explicitly account for the cumulative uncertainty that accumulates along generation paths.

3. **Lack of Theoretical Validation**: No formal proof exists that CP coverage guarantees hold for auto-regressive LLM generation under realistic assumptions.

These limitations prevent reliable deployment of CP-based UQ for generative LLM systems, leaving practitioners without principled statistical tools for risk assessment.

### 2.2 Research Objectives

This research proposes **Entropy-Calibrated Conformal Prediction (ECCP)**, a novel black-box statistical framework that addresses the identified limitations through three core innovations:

**Objective 1: Theoretical Foundation**
Establish formal coverage guarantees for conformal prediction applied to auto-regressive LLM generation under exchangeability assumptions (weaker than i.i.d.), providing the first rigorous statistical validation for CP in sequential generative settings.

**Objective 2: Methodological Innovation**
Develop an entropy-based nonconformity measure that naturally captures sequential dependencies through cumulative Shannon entropy accumulation along generation paths, with adaptive threshold calibration accounting for context length variations.

**Objective 3: Empirical Validation**
Demonstrate that ECCP achieves valid coverage (90% ± 2% for α=0.1) across diverse text generation tasks (summarization, translation, question answering) while maintaining computational efficiency (≤20% overhead) and practical prediction set sizes (≤10 candidates).

### 2.3 Research Significance

This work addresses a critical gap in the statistical foundations of LLM deployment by providing:

**Theoretical Contributions:**
- First formal proof of CP coverage guarantees under exchangeability for auto-regressive generation
- Novel connection between information theory (Shannon entropy) and conformal nonconformity scoring
- Characterization of error bounds for sequential dependencies in generative models

**Practical Impact:**
- Production-ready UQ framework compatible with any LLM API providing token probabilities (OpenAI, Anthropic)
- Enables confidence-aware text generation for high-stakes applications
- Provides auditable uncertainty bounds for regulatory compliance and safety analysis

**Broader Significance:**
The proposed framework directly addresses the NSF/NIST call for "new statistical tools for the era of black-box models" by demonstrating how classical statistical theory (conformal prediction) can be rigorously extended to modern foundation models through principled relaxation of assumptions (exchangeability vs. i.i.d.) and domain-appropriate nonconformity measures (entropy accumulation). This work establishes a template for developing statistically valid UQ methods for other sequential generative models beyond text (e.g., code generation, structured data synthesis).

## 3. Methodology

### 3.1 Theoretical Framework

#### 3.1.1 Problem Formulation

Let $\mathcal{X}$ denote the input space (prompts) and $\mathcal{Y}$ the output space (generated text sequences). An auto-regressive LLM defines a conditional distribution:

$$p_\theta(y|x) = \prod_{t=1}^{T} p_\theta(y_t | y_{1:t-1}, x)$$

where $y = (y_1, \ldots, y_T)$ is a token sequence, $x \in \mathcal{X}$ is the input prompt, and $\theta$ represents model parameters (inaccessible in black-box settings).

**Goal**: Construct prediction sets $C(x) \subseteq \mathcal{Y}$ such that:

$$\mathbb{P}(y_{\text{true}} \in C(x)) \geq 1 - \alpha$$

for a user-specified miscoverage rate $\alpha$ (e.g., $\alpha = 0.1$ for 90% coverage), without access to $\theta$ and under realistic assumptions about data distribution.

#### 3.1.2 Exchangeability Assumption

**Definition**: A sequence of random variables $(Z_1, \ldots, Z_n)$ is exchangeable if their joint distribution is invariant to permutations:

$$P(Z_1, \ldots, Z_n) = P(Z_{\pi(1)}, \ldots, Z_{\pi(n)})$$

for any permutation $\pi$.

**Application to LLM Generation**: We assume the calibration set $\{(x_i, y_i)\}_{i=1}^n$ and test point $(x_{n+1}, y_{n+1})$ are exchangeable. This is weaker than i.i.d. (which implies exchangeability but not vice versa) and is satisfied when:
- Calibration and test samples are drawn from the same task distribution
- No temporal ordering effects exist (e.g., model drift, concept shift)

**Validation Protocol**: Empirically test exchangeability via permutation tests:
1. Compute test statistic $T(\{(x_i, y_i)\})$ on original calibration set
2. Generate 1000 random permutations and compute $T$ for each
3. Reject exchangeability if original $T$ falls outside 95% quantile range

#### 3.1.3 Entropy-Based Nonconformity Measure

**Token-Wise Entropy**: At generation step $t$, compute Shannon entropy over the token distribution:

$$H(p_t) = -\sum_{v \in \mathcal{V}} p_\theta(y_t = v | y_{1:t-1}, x) \log p_\theta(y_t = v | y_{1:t-1}, x)$$

where $\mathcal{V}$ is the vocabulary.

**Sequential Accumulation**: Define the path-level nonconformity score as cumulative entropy:

$$S(y_{1:T} | x) = \sum_{t=1}^{T} H(p_t) = -\sum_{t=1}^{T} \sum_{v \in \mathcal{V}} p_\theta(y_t = v | y_{1:t-1}, x) \log p_\theta(y_t = v | y_{1:t-1}, x)$$

**Rationale**: 
- Higher entropy indicates greater uncertainty at each step
- Cumulative entropy naturally captures total generation uncertainty along the path
- Monotonicity: $S(y_{1:t+1}) \geq S(y_{1:t})$ since $H(p_t) \geq 0$

**Adaptive Threshold**: To account for varying context lengths $l$, define:

$$\tau(l) = \tau_0 \cdot \log(1 + l/l_0)$$

where $\tau_0$ and $l_0$ are hyperparameters calibrated from validation data. This logarithmic scaling reflects diminishing marginal entropy growth for longer contexts.

#### 3.1.4 Coverage Guarantee (Theoretical Result)

**Theorem (ECCP Coverage Guarantee)**: Let $\{(x_i, y_i)\}_{i=1}^{n+1}$ be exchangeable. Define the conformity threshold:

$$\tau = \text{Quantile}_{1-\alpha}\left(\{S(y_i | x_i)\}_{i=1}^n\right)$$

and prediction set:

$$C(x_{n+1}) = \{y : S(y | x_{n+1}) \leq \tau\}$$

Then:

$$\mathbb{P}\left(y_{n+1} \in C(x_{n+1})\right) \geq \frac{n+1-\lfloor \alpha(n+1) \rfloor}{n+1}$$

**Proof Sketch**:
1. By exchangeability, the rank of $S(y_{n+1} | x_{n+1})$ among $\{S(y_i | x_i)\}_{i=1}^{n+1}$ is uniformly distributed over $\{1, \ldots, n+1\}$
2. The threshold $\tau$ is the $(1-\alpha)$-quantile of the first $n$ scores
3. For $y_{n+1} \in C(x_{n+1})$, we need $S(y_{n+1} | x_{n+1}) \leq \tau$, which occurs when the rank is at most $\lceil (1-\alpha)(n+1) \rceil$
4. Probability of this event is $\frac{\lceil (1-\alpha)(n+1) \rceil}{n+1} \geq 1 - \alpha$ for large $n$

This extends classical CP theory (Vovk et al., 2005) to auto-regressive generation via entropy-based scoring.

### 3.2 Algorithm Design

#### 3.2.1 ECCP Calibration Phase

**Input**: 
- Calibration set $\mathcal{D}_{\text{cal}} = \{(x_i, y_i^*)\}_{i=1}^n$ where $y_i^*$ is ground truth
- LLM API with token probability access
- Desired coverage level $1-\alpha$
- Context length normalization parameters $\tau_0, l_0$

**Algorithm**:
```
1. For each (x_i, y_i*) in D_cal:
   a. Generate token probabilities: {p_t(·|y_{1:t-1}*, x_i)}_{t=1}^{T_i}
   b. Compute token-wise entropy: H_t = -Σ_v p_t(v) log p_t(v)
   c. Accumulate path entropy: S_i = Σ_{t=1}^{T_i} H_t
   d. Record context length: l_i = |tokenize(x_i)|

2. Fit adaptive threshold:
   a. Regress S_i ~ log(1 + l_i/l_0) to estimate τ_0
   b. Alternatively, use fixed τ_0 and select l_0 via cross-validation

3. Compute calibration threshold:
   τ = Quantile_{1-α}({S_i}_{i=1}^n)

4. Return: (τ, τ_0, l_0)
```

**Computational Complexity**: $O(n \cdot T_{\text{avg}} \cdot |\mathcal{V}|)$ where $T_{\text{avg}}$ is average generation length and $|\mathcal{V}|$ is vocabulary size. In practice, entropy computation adds ~15% overhead to standard generation.

#### 3.2.2 ECCP Prediction Phase

**Input**:
- Test prompt $x_{\text{test}}$
- Calibrated threshold $\tau$
- LLM API
- Maximum candidates $K$ (e.g., $K=10$)

**Algorithm**:
```
1. Initialize prediction set: C = ∅

2. Generate candidate outputs via sampling:
   For k = 1 to K:
     a. Sample y_k ~ p_θ(·|x_test) using temperature T=0.7
     b. Compute S(y_k | x_test) via entropy accumulation
     c. If S(y_k | x_test) ≤ τ:
        Add y_k to C

3. If |C| = 0 (empty set):
   Add greedy output: y_greedy = argmax_y p_θ(y|x_test)

4. Return: C
```

**Adaptive Sampling**: To efficiently explore the output space, use nucleus sampling (Holtzman et al., 2020) with $p=0.9$ to focus on high-probability regions while maintaining diversity.

### 3.3 Experimental Design

#### 3.3.1 Datasets and Tasks

**Task 1: Abstractive Summarization**
- Dataset: CNN/DailyMail (Hermann et al., 2015)
- Samples: 5000 (3000 calibration, 2000 test)
- Context lengths: {64, 128, 256} tokens
- Ground truth: Human-written summaries
- Evaluation: ROUGE-L for semantic equivalence

**Task 2: Machine Translation**
- Dataset: WMT14 English-German (Bojar et al., 2014)
- Samples: 5000 (3000 calibration, 2000 test)
- Context lengths: {32, 64, 128} tokens
- Ground truth: Reference translations
- Evaluation: BLEU score for semantic equivalence

**Task 3: Question Answering**
- Dataset: Natural Questions (Kwiatkowski et al., 2019)
- Samples: 5000 (3000 calibration, 2000 test)
- Context lengths: {128, 256} tokens
- Ground truth: Annotated short answers
- Evaluation: Exact match and F1 score

#### 3.3.2 LLM Models

**Primary Model**: GPT-4 (OpenAI API)
- Rationale: State-of-the-art performance, token probability access via `logprobs` parameter
- Configuration: Temperature $T=0.7$, top-p $p=0.9$, max tokens $T_{\max}=512$

**Secondary Model**: Claude-3.5-Sonnet (Anthropic API)
- Rationale: Architectural diversity, independent validation
- Configuration: Matched to GPT-4 settings

#### 3.3.3 Baseline Methods

**Baseline 1: COPU (Wang et al., 2025)**
- Nonconformity: Negative log-likelihood $-\log p_\theta(y|x)$
- Assumption: i.i.d. calibration set
- Implementation: Official codebase with default hyperparameters

**Baseline 2: CPQ (Noorani et al., 2025)**
- Nonconformity: Missing mass estimator $\hat{m}(y|x) = 1 - \sum_{v \in y} p_\theta(v|x)$
- Assumption: Query-only access
- Implementation: Good-Turing estimator with Laplace smoothing

**Baseline 3: Naive CP**
- Nonconformity: Uniform scoring (all outputs equally conforming)
- Assumption: None (worst-case baseline)
- Implementation: Random prediction sets of size $K$

#### 3.3.4 Evaluation Metrics

**Primary Metric: Empirical Coverage**

$$\text{Coverage} = \frac{1}{|\mathcal{D}_{\text{test}}|} \sum_{(x,y^*) \in \mathcal{D}_{\text{test}}} \mathbb{1}[y^* \in C(x)]$$

**Success Criterion**: $|\text{Coverage} - (1-\alpha)| \leq 0.02$ (within 2% of nominal level)

**Secondary Metrics**:

1. **Prediction Set Size**:
$$\text{Avg Size} = \frac{1}{|\mathcal{D}_{\text{test}}|} \sum_{x \in \mathcal{D}_{\text{test}}} |C(x)|$$
Target: $\leq 10$ candidates for practical usability

2. **Computational Overhead**:
$$\text{Overhead} = \frac{T_{\text{ECCP}} - T_{\text{baseline}}}{T_{\text{baseline}}}$$
Target: $\leq 0.20$ (20% overhead)

3. **Coverage Stability** (across context lengths):
$$\text{Stability} = \sigma(\{\text{Coverage}_l\}_{l \in \{32,64,128,256\}})$$
Target: $\sigma \leq 0.03$ (3% standard deviation)

#### 3.3.5 Statistical Testing Protocol

**Hypothesis Tests**:

1. **Coverage Validity** (One-sample proportion test):
   - $H_0$: Coverage $= 1-\alpha$
   - $H_1$: Coverage $\neq 1-\alpha$
   - Test statistic: $z = \frac{\hat{p} - (1-\alpha)}{\sqrt{(1-\alpha)\alpha/n}}$
   - Significance level: $\alpha_{\text{test}} = 0.05$

2. **Baseline Comparison** (Two-sample proportion test):
   - $H_0$: Coverage$_{\text{ECCP}}$ = Coverage$_{\text{baseline}}$
   - $H_1$: Coverage$_{\text{ECCP}}$ $\neq$ Coverage$_{\text{baseline}}$
   - Test statistic: Pooled z-test
   - Bonferroni correction: $\alpha' = 0.05/3 = 0.017$ (3 baselines)

3. **Exchangeability Validation** (Permutation test):
   - Test statistic: $T = \max_i |S(y_i|x_i) - \bar{S}|$
   - Null distribution: 1000 random permutations
   - Reject if $p$-value $< 0.05$

**Sample Size Justification**:
For 90% coverage with 2% margin of error at 95% confidence:
$$n = \frac{z_{0.975}^2 \cdot 0.9 \cdot 0.1}{0.02^2} \approx 865$$
We use $n=2000$ test samples per task for safety margin and subgroup analysis.

**Power Analysis**:
With $n=2000$, statistical power to detect $|\Delta \text{Coverage}| \geq 0.03$ is:
$$\text{Power} = 1 - \beta \approx 0.95$$
at $\alpha_{\text{test}} = 0.05$.

#### 3.3.6 Ablation Studies

**Ablation 1: Nonconformity Measure**
- Variants: (a) Token-wise entropy only, (b) Cumulative entropy (ECCP), (c) Maximum entropy, (d) Entropy variance
- Metric: Coverage accuracy and prediction set size
- Purpose: Validate cumulative entropy design choice

**Ablation 2: Threshold Adaptation**
- Variants: (a) Fixed $\tau$, (b) Linear $\tau(l) = \tau_0 + \tau_1 l$, (c) Logarithmic $\tau(l) = \tau_0 \log(1+l/l_0)$ (ECCP), (d) Learned $\tau(l)$ via regression
- Metric: Coverage stability across context lengths
- Purpose: Validate adaptive threshold functional form

**Ablation 3: Calibration Set Size**
- Variants: $n \in \{500, 1000, 2000, 3000, 5000\}$
- Metric: Coverage convergence to nominal level
- Purpose: Determine minimum calibration requirements

**Ablation 4: Temperature Sensitivity**
- Variants: $T \in \{0.3, 0.5, 0.7, 1.0\}$
- Metric: Coverage robustness and prediction set diversity
- Purpose: Assess sensitivity to sampling hyperparameters

### 3.4 Implementation Details

**Software Stack**:
- Python 3.10+ with NumPy, SciPy for statistical computations
- OpenAI Python SDK v1.0+ for GPT-4 API access
- Anthropic Python SDK for Claude API access
- Hugging Face Transformers for tokenization
- Weights & Biases for experiment tracking

**Reproducibility**:
- Random seeds fixed: `np.random.seed(42)`, `torch.manual_seed(42)`
- API calls logged with timestamps and model versions
- All hyperparameters version-controlled in YAML configs
- Code and data released under MIT license upon publication

**Computational Resources**:
- Estimated API costs: ~$500 for 15,000 LLM generations (GPT-4 + Claude)
- Calibration time: ~2 hours for 3000 samples per task
- Total experiment runtime: ~20 hours on standard workstation

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

#### 4.1.1 Theoretical Outcomes

**Outcome T1: Formal Coverage Guarantee**
We expect to prove that ECCP achieves coverage:
$$\mathbb{P}(y_{\text{true}} \in C(x)) \geq 1 - \alpha - O(n^{-1/2})$$
under exchangeability, with explicit error bounds characterized by calibration set size $n$ and generation length $T$. This will be the first rigorous statistical guarantee for CP applied to auto-regressive LLM generation.

**Outcome T2: Entropy Accumulation Validity**
We expect to demonstrate that cumulative entropy $S(y) = \sum_t H(p_t)$ satisfies:
1. **Monotonicity**: $S(y_{1:t+1}) \geq S(y_{1:t})$ in $>95\%$ of generation samples
2. **Discriminative Power**: Correlation between $S(y)$ and generation quality (ROUGE/BLEU) $\rho > 0.6$
3. **Calibration Stability**: Threshold $\tau$ variance $<10\%$ across random calibration splits

#### 4.1.2 Empirical Outcomes

**Outcome E1: Coverage Accuracy**
Across all three tasks (summarization, translation, QA) and two models (GPT-4, Claude), we expect:
- **Primary**: Empirical coverage within $90\% \pm 2\%$ for $\alpha=0.1$ (success rate $>80\%$ of experimental conditions)
- **Comparison**: ECCP coverage error $\leq$ COPU coverage error in $>70\%$ of conditions
- **Robustness**: Coverage stability $\sigma < 3\%$ across context lengths

**Outcome E2: Prediction Set Quality**
- **Size**: Average prediction set size $\leq 10$ candidates for 90% coverage
- **Informativeness**: Prediction sets contain ground truth in top-3 ranked outputs (by entropy) in $>60\%$ of cases
- **Diversity**: Pairwise BLEU between candidates $< 0.7$ (avoiding redundant outputs)

**Outcome E3: Computational Efficiency**
- **Overhead**: Entropy computation adds $15\% \pm 5\%$ to baseline generation time
- **Scalability**: Linear complexity $O(T)$ in generation length confirmed empirically
- **API Compatibility**: Successful deployment on both OpenAI and Anthropic APIs without model access

#### 4.1.3 Negative Results (Falsification Scenarios)

**Scenario N1: Coverage Failure**
If empirical coverage deviates $>5\%$ from nominal level in $>30\%$ of conditions, this would indicate:
- Exchangeability assumption violated in practice
- Entropy accumulation insufficient for auto-regressive dependencies
- **Mitigation**: Investigate conditional exchangeability (stratified calibration by prompt type)

**Scenario N2: Impractical Prediction Sets**
If average set size $>20$ candidates for 90% coverage, this would indicate:
- Entropy-based scoring too conservative
- Output space too large for conformal methods
- **Mitigation**: Hybrid approach combining ECCP with retrieval-based filtering

**Scenario N3: Baseline Equivalence**
If ECCP shows no statistically significant improvement over COPU ($p > 0.05$), this would suggest:
- Entropy and logit-based scoring are functionally equivalent
- Auto-regressive dependencies negligible for coverage
- **Interpretation**: Still valuable as ECCP provides theoretical guarantees under weaker assumptions

### 4.2 Scientific Impact

#### 4.2.1 Advancing Statistical Foundations of LLMs

This work directly addresses the NSF/NIST call for "new statistical tools for the era of black-box models" by:

1. **Bridging Theory and Practice**: Demonstrating how classical statistical theory (conformal prediction) can be rigorously extended to modern foundation models through principled assumption relaxation (exchangeability vs. i.i.d.)

2. **Information-Theoretic UQ**: Establishing Shannon entropy as a principled nonconformity measure for generative models, connecting information theory and statistical inference

3. **Sequential Dependency Handling**: Providing the first formal treatment of CP for auto-regressive generation, with implications for other sequential models (code generation, time series forecasting)

#### 4.2.2 Enabling Trustworthy LLM Deployment

**Practical Applications**:

1. **High-Stakes Decision Support**: Medical diagnosis systems can use ECCP to flag uncertain predictions requiring human review (e.g., "90% confidence this diagnosis is in top-5 candidates")

2. **Regulatory Compliance**: Financial institutions can provide auditable uncertainty bounds for LLM-generated reports, satisfying regulatory requirements for model risk management

3. **Safety-Critical Systems**: Autonomous vehicles using LLM-based planning can reject actions with high entropy (uncertain outcomes)

**Deployment Framework**:
```
User Prompt → LLM API → ECCP Calibration → Prediction Set
                ↓                              ↓
         Token Probabilities          {Output 1, ..., Output K}
                                      with Coverage Guarantee
```

#### 4.2.3 Broader Research Directions

This work opens several follow-up research directions:

1. **Adaptive Conformal Prediction**: Extend ECCP to online settings with distribution shift detection and automatic recalibration

2. **Multi-Modal Foundation Models**: Apply entropy-based CP to vision-language models (CLIP, GPT-4V) for image captioning and VQA

3. **Structured Output Spaces**: Generalize to code generation (syntax-constrained entropy), molecule design (graph-structured outputs)

4. **Fairness-Aware UQ**: Investigate whether ECCP prediction sets exhibit demographic parity across subgroups (bias detection via coverage disparity)

### 4.3 Limitations and Future Work

**Limitation 1: Token Probability Access**
ECCP requires LLM APIs to expose token probabilities, which some production APIs (e.g., ChatGPT web interface) do not provide.
- **Future Work**: Develop probability-free variants using CPQ's missing mass estimators or query-based entropy approximation

**Limitation 2: Exchangeability Assumption**
Real-world deployment may violate exchangeability due to temporal drift, adversarial inputs, or domain shift.
- **Future Work**: Develop exchangeability monitoring tools and conditional CP methods for non-stationary distributions

**Limitation 3: Single Ground Truth**
Current evaluation assumes unique correct outputs, which is unrealistic for creative generation tasks.
- **Future Work**: Extend to multi-reference evaluation using set-valued ground truth and Hausdorff distance-based coverage

**Limitation 4: Computational Cost**
While ECCP adds only 15-20% overhead, this may be prohibitive for real-time applications (<10ms latency).
- **Future Work**: Investigate amortized calibration (pre-compute thresholds for common prompt templates) and approximate entropy computation

### 4.4 Timeline and Milestones

**Month 1-2: Theoretical Development**
- Formalize exchangeability assumptions for LLM generation
- Prove coverage guarantee theorem with explicit error bounds
- Develop adaptive threshold theory

**Month 3-4: Implementation and Calibration**
- Implement ECCP algorithm with OpenAI/Anthropic APIs
- Collect calibration datasets (3000 samples × 3 tasks)
- Validate exchangeability via permutation tests

**Month 5-6: Experimental Validation**
- Run main experiments (24 conditions × 2000 test samples)
- Conduct ablation studies (4 ablations × 5 variants each)
- Perform statistical hypothesis testing

**Month 7-8: Analysis and Dissemination**
- Analyze results, investigate failure cases
- Write manuscript for submission to NeurIPS/ICML
- Release open-source implementation and datasets

**Total Duration**: 8 months

### 4.5 Success Criteria Summary

This research will be considered successful if:

1. **Theoretical**: Formal coverage proof completed with explicit error bounds
2. **Empirical**: Coverage within $\pm 2\%$ of nominal level in $>80\%$ of experimental conditions
3. **Practical**: Prediction set size $\leq 10$ candidates with $\leq 20\%$ computational overhead
4. **Comparative**: Statistically significant improvement over baselines OR equivalent coverage under weaker assumptions
5. **Reproducible**: Open-source release with documentation enabling independent validation

Even partial success (e.g., coverage guarantees proven but empirical performance mixed) would represent significant progress toward rigorous statistical foundations for LLM uncertainty quantification, advancing the field's ability to deploy foundation models with formal reliability guarantees.