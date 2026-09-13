# Research Proposal: Conformal Prediction for Probabilistic Correctness Guarantees in LLM-Generated Code

## 1. Title

**Conformal Prediction for Probabilistic Correctness Guarantees in LLM-Generated Code: A Distribution-Free Framework for Bridging Formal Verification and Generative AI**

## 2. Introduction

### 2.1 Background

The rapid advancement of large language models (LLMs) has revolutionized code generation, with systems like GitHub Copilot, GPT-4, and CodeLlama demonstrating remarkable capabilities in producing functional code from natural language descriptions. However, a critical trust gap persists: while these models generate syntactically plausible code, they provide no reliability guarantees about correctness. This gap creates significant barriers to deploying LLM-generated code in production environments, where developers need calibrated uncertainty estimates to make informed decisions about code acceptance.

Traditional formal verification methods—including theorem provers, satisfiability (SAT) solvers, and symbolic execution—offer strong correctness guarantees through rigorous mathematical proofs. These approaches have demonstrated success in safety-critical domains such as avionics, medical devices, and cryptographic protocols. However, formal verification faces severe scalability challenges: verification complexity grows exponentially with program size, many verification problems are undecidable, and the expertise required to write formal specifications remains a significant bottleneck.

Recent work has explored hybrid approaches combining AI and formal methods. AutoSafeCoder (2024) integrates static analyzers with dynamic fuzzing to reduce security vulnerabilities by 13%, while ROCODE (2025) achieves 99.1% compilation pass rates using program analysis with backtracking mechanisms. These systems demonstrate that lightweight verification oracles—type checkers, static analyzers, and test suites—can provide actionable signals about code quality without requiring complete formal proofs.

Despite these advances, existing approaches fall into two unsatisfactory categories: (1) deterministic formal verification that provides absolute guarantees but remains computationally intractable at scale, or (2) heuristic confidence scores from probabilistic models that lack theoretical grounding and calibration guarantees. This creates a critical gap for practitioners who need reliable uncertainty quantification: formal methods are too expensive for rapid prototyping and iterative development, while uncalibrated confidence scores cannot support principled decision-making about code acceptance thresholds.

### 2.2 Research Objectives

This research proposes a novel framework applying **conformal prediction** with domain-specific calibration to provide distribution-free probabilistic correctness guarantees for LLM-generated code. Conformal prediction is a statistical framework that produces prediction intervals with finite-sample coverage guarantees under the exchangeability assumption, without requiring distributional assumptions about the underlying data-generating process.

Our primary objectives are:

**O1: Develop a conformal prediction framework** that maps lightweight verification oracle outputs (type checker severity, static analyzer warnings, test coverage) to calibrated prediction intervals $[p_{\text{lower}}, p_{\text{upper}}]$ representing probabilistic correctness guarantees with theoretical coverage rate $(1-\alpha)$.

**O2: Validate empirical coverage guarantees** by demonstrating that empirical coverage rates match theoretical guarantees within statistical tolerance (target: 90-95% empirical coverage for 90-95% theoretical coverage) across multiple narrow code domains.

**O3: Optimize prediction interval informativeness** by investigating multi-oracle ensembles and calibration dataset size effects, targeting 15% tighter intervals compared to single-oracle baselines while maintaining coverage guarantees.

**O4: Establish practical deployment guidelines** for non-safety-critical applications where probabilistic assurances suffice, including domain selection criteria, calibration data requirements, and distribution shift monitoring protocols.

### 2.3 Research Hypothesis

**Main Hypothesis (H-DC-CP-CodeVerif-v1):**

Under code generation scenarios where complete formal verification is computationally intractable, if a conformal prediction framework is applied with domain-specific calibration ($n=100$-$1000+$ verified samples per domain) and lightweight verification oracles (type checkers, static analyzers, test suites), then probabilistic correctness guarantees with distribution-free finite-sample coverage will be achieved (empirical coverage rate matching theoretical $(1-\alpha)$ within statistical tolerance), because conformal prediction's exchangeability assumption combined with oracle-based nonconformity scores produces calibrated prediction intervals for code correctness.

The hypothesis operates through three causal steps:

1. **Domain-specific calibration → Empirical quantiles**: Collecting $n=100$-$1000+$ verified code samples from narrow domains establishes empirical quantiles of nonconformity scores under the exchangeability assumption.

2. **Oracle evaluation → Nonconformity scores**: Lightweight verification oracles evaluate new LLM-generated code to compute nonconformity scores $s_{\text{new}}$ representing deviation from typical correct code patterns.

3. **Score mapping → Prediction intervals**: Nonconformity scores are mapped to prediction intervals $[p_{\text{lower}}, p_{\text{upper}}]$ using calibrated quantiles, producing coverage-guaranteed uncertainty quantification.

### 2.4 Significance

This research addresses a critical gap at the intersection of formal methods and generative AI, directly aligned with the VerifAI workshop's themes:

**Theoretical Significance:** We introduce the first application of conformal prediction to code verification, extending distribution-free uncertainty quantification from continuous domains (biological systems, regression tasks) to discrete correctness assessment. This demonstrates how rigorous statistical frameworks can provide "soft assurances" where hard guarantees are intractable.

**Practical Significance:** The framework enables principled deployment decisions for LLM-generated code in non-safety-critical applications (rapid prototyping, educational tools, preliminary code screening). Developers gain interpretable uncertainty estimates with coverage guarantees, supporting risk-informed acceptance thresholds without requiring expensive formal verification.

**Methodological Significance:** By validating the exchangeability assumption within narrow code domains using Maximum Mean Discrepancy (MMD < 0.10), we establish empirical protocols for applying conformal prediction to structured generation tasks beyond traditional i.i.d. settings.

**Broader Impact:** This work contributes to trustworthy AI deployment by providing calibrated uncertainty quantification—a critical requirement for human-AI collaboration in software development. The framework's distribution-free nature makes it applicable across programming languages and code domains without retraining probabilistic models.

## 3. Methodology

### 3.1 Research Design Overview

Our methodology follows a three-phase experimental design: (1) **Calibration Phase** establishing domain-specific nonconformity score distributions, (2) **Prediction Phase** applying conformal prediction to new LLM-generated code, and (3) **Validation Phase** empirically verifying coverage guarantees and interval informativeness.

### 3.2 Data Collection

#### 3.2.1 Calibration Dataset Construction

For each target code domain, we construct calibration datasets containing $n \in \{100, 500, 1000\}$ verified code samples:

**Domain Selection Criteria:**
- **Narrow scope**: Well-defined task categories (e.g., "Python sorting functions", "Java data processing with type annotations", "Python numerical code with type hints")
- **Homogeneity**: Tasks within domain share structural patterns and verification oracle applicability
- **Verification feasibility**: Ground-truth correctness determinable via test suites or formal specifications

**Data Sources:**
- **Benchmark repositories**: SV-COMP (385 verified Java programs), JetBrains verified-cogen, KTH Vecogen
- **Synthetic generation**: LLM-generated code with human verification for domains lacking existing benchmarks
- **Open-source projects**: Curated functions from well-tested codebases with comprehensive test suites

**Verification Protocol:**
Each calibration sample undergoes multi-stage verification:
1. **Compilation check**: Code must compile without errors
2. **Test suite execution**: Must pass domain-specific test cases (minimum 10 tests per sample)
3. **Manual review**: Expert inspection for correctness (subset of 20% for quality control)
4. **Binary labeling**: Each sample labeled as correct (1) or incorrect (0)

#### 3.2.2 Test Dataset Construction

For each domain, we construct independent test sets ($n \geq 100$ samples) following identical verification protocols. Test sets are temporally separated from calibration sets to simulate deployment conditions.

**Exchangeability Validation:**
We compute Maximum Mean Discrepancy (MMD) between calibration and test distributions using code embeddings from CodeBERT:

$$\text{MMD}^2(\mathcal{C}, \mathcal{T}) = \mathbb{E}_{x,x' \sim \mathcal{C}}[k(x,x')] + \mathbb{E}_{y,y' \sim \mathcal{T}}[k(y,y')] - 2\mathbb{E}_{x \sim \mathcal{C}, y \sim \mathcal{T}}[k(x,y)]$$

where $k(\cdot, \cdot)$ is a Gaussian RBF kernel on CodeBERT embeddings. Domains with MMD > 0.10 are rejected or further narrowed.

### 3.3 Conformal Prediction Framework

#### 3.3.1 Nonconformity Score Functions

We define three oracle-based nonconformity score functions:

**Oracle 1: Type Checker Severity (mypy)**
$$s_{\text{type}}(x) = \sum_{i=1}^{n_{\text{errors}}} w_i \cdot \mathbb{I}(\text{error}_i)$$

where $w_i \in \{1, 2, 3\}$ represents severity weights (note=1, warning=2, error=3).

**Oracle 2: Static Analyzer Warnings (pylint)**
$$s_{\text{static}}(x) = \frac{n_{\text{warnings}}}{n_{\text{lines}}} \times 100$$

normalized by code length to ensure comparability.

**Oracle 3: Test Coverage Inverse**
$$s_{\text{test}}(x) = 1 - \frac{n_{\text{passed}}}{n_{\text{total}}}$$

representing the proportion of failed tests (higher score = more incorrect).

**Ensemble Nonconformity Score:**
$$s_{\text{ensemble}}(x) = w_1 \cdot s_{\text{type}}(x) + w_2 \cdot s_{\text{static}}(x) + w_3 \cdot s_{\text{test}}(x)$$

where weights $\{w_1, w_2, w_3\}$ are optimized via reliability-based calibration:

$$w_j = \frac{\rho_j}{\sum_{k=1}^3 \rho_k}, \quad \rho_j = |\text{Spearman}(s_j, y_{\text{true}})|$$

computed on the calibration set.

#### 3.3.2 Conformal Prediction Algorithm

**Calibration Phase:**

Given calibration set $\mathcal{D}_{\text{cal}} = \{(x_i, y_i)\}_{i=1}^n$ where $y_i \in \{0,1\}$ indicates correctness:

1. Compute nonconformity scores: $\{s_i = s(x_i)\}_{i=1}^n$
2. For coverage level $(1-\alpha)$, compute empirical quantile:
$$q_{\alpha} = \text{Quantile}(\{s_1, \ldots, s_n\}, 1-\alpha)$$

**Prediction Phase:**

For new LLM-generated code $x_{\text{new}}$:

1. Compute nonconformity score: $s_{\text{new}} = s(x_{\text{new}})$
2. Construct prediction set:
$$\Gamma(x_{\text{new}}) = \{y \in \{0,1\} : s_{\text{new}} \leq q_{\alpha}\}$$

3. Map to prediction interval:
$$[p_{\text{lower}}, p_{\text{upper}}] = \begin{cases}
[0.95, 1.0] & \text{if } s_{\text{new}} \leq q_{0.05} \\
[0.50, 0.95] & \text{if } q_{0.05} < s_{\text{new}} \leq q_{0.50} \\
[0.0, 0.50] & \text{if } s_{\text{new}} > q_{0.50}
\end{cases}$$

This discretization provides interpretable correctness probability ranges.

**Theoretical Guarantee:**

Under the exchangeability assumption, conformal prediction ensures:

$$\mathbb{P}(y_{\text{new}} \in \Gamma(x_{\text{new}})) \geq 1 - \alpha$$

for any new sample $(x_{\text{new}}, y_{\text{new}})$ exchangeable with calibration data.

### 3.4 Experimental Design

#### 3.4.1 Experimental Conditions

We conduct a full factorial experiment with the following factors:

| Factor | Levels | Values |
|--------|--------|--------|
| **Calibration size** | 3 | $n \in \{100, 500, 1000\}$ |
| **Oracle type** | 4 | Type checker, Static analyzer, Test coverage, Ensemble |
| **Coverage level** | 3 | $\alpha \in \{0.01, 0.05, 0.10\}$ |
| **Code domain** | 3 | Python sorting, Java data processing, Python numerical |
| **LLM model** | 3 | GPT-4, Claude-3.5-Sonnet, CodeLlama-70B |

Total experimental conditions: $3 \times 4 \times 3 \times 3 \times 3 = 324$ configurations.

#### 3.4.2 Evaluation Protocol

**Primary Evaluation: Coverage Calibration**

For each configuration, we measure empirical coverage on test set $\mathcal{D}_{\text{test}} = \{(x_j, y_j)\}_{j=1}^m$ where $m \geq 100$:

$$\text{Coverage}_{\text{emp}} = \frac{1}{m} \sum_{j=1}^m \mathbb{I}(y_j \in \Gamma(x_j))$$

**Statistical Test:**
One-sample binomial test with null hypothesis $H_0: \text{Coverage}_{\text{emp}} = (1-\alpha)$, two-tailed, significance level $\alpha_{\text{test}} = 0.05$.

**Success Criterion:** $p$-value $> 0.05$ (fail to reject $H_0$), indicating empirical coverage statistically indistinguishable from theoretical guarantee.

**Secondary Evaluation: Interval Informativeness**

Average prediction interval width:

$$\Delta W = \frac{1}{m} \sum_{j=1}^m (p_{\text{upper},j} - p_{\text{lower},j})$$

**Comparison Test:**
Paired $t$-test comparing interval widths across conditions (e.g., ensemble vs. single oracle), one-tailed, $\alpha = 0.05$.

**Target:** $\Delta W_{\text{ensemble}} \leq 0.85 \times \Delta W_{\text{single}}$ (15% improvement).

#### 3.4.3 Ablation Studies

To validate the causal mechanism, we conduct three ablation studies:

**Ablation 1: Calibration Size Effect**
- Compare coverage and interval width for $n \in \{100, 500, 1000\}$
- Hypothesis: Larger $n$ → tighter intervals while maintaining coverage
- Metric: Spearman correlation $\rho(n, \Delta W) < 0$ (negative correlation)

**Ablation 2: Oracle Monotonicity**
- Compute Spearman correlation between oracle scores and true correctness
- Requirement: $\rho > 0.6$ for oracle to be informative
- Reject oracles with $\rho < 0.3$ as non-monotonic

**Ablation 3: Exchangeability Sensitivity**
- Artificially introduce distribution shift by mixing domains
- Measure coverage degradation as MMD increases from 0.05 → 0.20
- Validate MMD < 0.10 threshold for maintaining coverage guarantees

### 3.5 Evaluation Metrics

**Primary Metrics:**

1. **Empirical Coverage Rate**: $\text{Coverage}_{\text{emp}} \in [0, 1]$
   - Target: $(1-\alpha) \pm 0.05$ for well-calibrated framework
   - Reported with 95% binomial confidence intervals

2. **Coverage Calibration Error**: $|\text{Coverage}_{\text{emp}} - (1-\alpha)|$
   - Target: $< 0.05$ (within 5 percentage points)

**Secondary Metrics:**

3. **Average Interval Width**: $\Delta W \in [0, 1]$
   - Interpretation: $< 0.40$ (tight), $0.40$-$0.70$ (moderate), $> 0.70$ (wide/uninformative)

4. **Interval Efficiency**: $\frac{\text{Coverage}_{\text{emp}}}{\Delta W}$
   - Higher values indicate better trade-off between coverage and informativeness

5. **Oracle Reliability**: Spearman $\rho$ between oracle scores and true correctness
   - Minimum acceptable: $\rho > 0.6$

6. **Distribution Shift Detection**: MMD between calibration and test sets
   - Threshold: MMD $< 0.10$ for valid exchangeability

**Deployment Simulation Metrics:**

7. **Acceptance Rate at Threshold**: Proportion of code accepted at $p_{\text{lower}} \geq 0.90$
8. **False Acceptance Rate**: Proportion of incorrect code accepted
9. **False Rejection Rate**: Proportion of correct code rejected

### 3.6 Baseline Comparisons

We compare our conformal prediction framework against three baselines:

**Baseline 1: Uncalibrated Oracle Scores**
- Direct use of oracle outputs (e.g., pylint score) as confidence estimates
- No calibration or coverage guarantees
- Metric: Calibration error via reliability diagrams

**Baseline 2: Bayesian Probabilistic Verification**
- Train probabilistic classifier (logistic regression) on calibration data
- Predict $P(\text{correct} | \text{oracle scores})$ using Bayesian inference
- Metric: Brier score, calibration error

**Baseline 3: Temperature-Scaled LLM Confidence**
- Use LLM's token probabilities with temperature scaling
- Calibrate via Platt scaling on calibration set
- Metric: Expected Calibration Error (ECE)

**Comparison Criteria:**
- Coverage guarantee validity (only conformal prediction provides finite-sample guarantees)
- Interval width (informativeness)
- Computational cost (calibration time, inference time)
- Robustness to distribution shift

### 3.7 Implementation Details

**Software Stack:**
- **Conformal prediction**: Custom implementation using `numpy` and `scipy.stats`
- **Verification oracles**: `mypy` (type checking), `pylint` (static analysis), `pytest` (test execution)
- **Code embeddings**: HuggingFace `transformers` with CodeBERT
- **LLM inference**: OpenAI API (GPT-4), Anthropic API (Claude), local deployment (CodeLlama)
- **Statistical analysis**: `statsmodels`, `scikit-learn`

**Computational Resources:**
- Calibration: 4 CPU cores, 16GB RAM per domain (estimated 2-4 hours per domain)
- Inference: Single CPU core, <1 second per code sample
- Total estimated compute: ~100 GPU hours for LLM generation, ~50 CPU hours for calibration

**Reproducibility:**
- All code and data released under MIT license
- Random seeds fixed for LLM sampling (temperature=0.7, top-p=0.95)
- Calibration/test splits documented with SHA-256 hashes

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome 1: Validated Coverage Guarantees**

We expect empirical coverage rates to match theoretical guarantees within statistical tolerance across all three code domains:
- For $\alpha = 0.05$ (95% coverage): empirical coverage $\in [0.90, 1.00]$
- For $\alpha = 0.10$ (90% coverage): empirical coverage $\in [0.85, 0.95]$
- Binomial test $p$-values $> 0.05$ for $\geq 80\%$ of experimental configurations

This outcome validates the core hypothesis that conformal prediction provides distribution-free probabilistic correctness guarantees for LLM-generated code.

**Primary Outcome 2: Informative Prediction Intervals**

We expect multi-oracle ensembles to achieve 15-20% tighter prediction intervals compared to single best oracle:
- Single oracle average width: $\Delta W_{\text{single}} \approx 0.45$-$0.55$
- Ensemble average width: $\Delta W_{\text{ensemble}} \approx 0.35$-$0.45$
- Paired $t$-test $p < 0.05$ demonstrating significant improvement

This demonstrates practical value: narrower intervals provide more actionable uncertainty estimates for deployment decisions.

**Secondary Outcome 1: Calibration Size Effects**

We expect diminishing returns in interval tightness as calibration size increases:
- $n=100 \to 500$: ~10% width reduction
- $n=500 \to 1000$: ~5% width reduction
- Practical recommendation: $n=500$ provides optimal cost-benefit trade-off

**Secondary Outcome 2: Exchangeability Validation**

We expect narrow code domains to satisfy exchangeability (MMD < 0.10) while broad domains fail:
- "Python sorting functions": MMD $\approx 0.06$-$0.08$ ✓
- "Mixed Python tasks": MMD $\approx 0.15$-$0.25$ ✗

This establishes empirical protocols for domain selection and validates the theoretical foundation.

**Negative Result Contingency:**

If coverage guarantees fail (empirical coverage < 0.85 for 95% theoretical), we will investigate:
1. **Exchangeability violations**: Refine domain definitions, increase MMD threshold sensitivity
2. **Oracle quality issues**: Develop oracle reliability diagnostics, filter low-quality oracles
3. **Calibration set bias**: Augment calibration data with adversarial examples

Even negative results contribute valuable insights about conformal prediction's applicability limits in code verification.

### 4.2 Scientific Impact

**Theoretical Contributions:**

1. **Extension of conformal prediction to discrete verification tasks**: First application to code correctness assessment, demonstrating distribution-free uncertainty quantification beyond continuous regression/classification.

2. **Empirical validation of exchangeability in structured generation**: Establishes MMD-based protocols for validating conformal prediction assumptions in non-i.i.d. settings (code generation with deliberate design patterns).

3. **Multi-oracle ensemble theory**: Develops reliability-weighted ensemble methods for combining heterogeneous verification signals with coverage guarantees.

**Methodological Contributions:**

1. **Practical calibration protocols**: Provides concrete guidelines for calibration dataset size ($n=500$ recommended), domain selection (MMD < 0.10), and oracle quality thresholds ($\rho > 0.6$).

2. **Distribution shift monitoring**: Introduces continuous MMD monitoring for detecting exchangeability violations in deployment, triggering recalibration when needed.

3. **Benchmark datasets**: Releases three curated code verification benchmarks (Python sorting, Java data processing, Python numerical) with ground-truth labels and oracle scores.

### 4.3 Practical Impact

**Deployment Scenarios:**

1. **Rapid Prototyping Tools**: Integrate framework into IDE plugins (VS Code, IntelliJ) to provide real-time uncertainty estimates for LLM-generated code suggestions. Developers see calibrated confidence intervals, enabling informed accept/reject decisions.

2. **Code Review Automation**: Use prediction intervals to prioritize human review—code with $p_{\text{lower}} < 0.70$ flagged for mandatory expert inspection, while $p_{\text{lower}} > 0.90$ fast-tracked.

3. **Educational Platforms**: Provide students with uncertainty-aware code generation assistants that explicitly communicate confidence levels, promoting critical evaluation of AI suggestions.

**Industry Adoption Pathway:**

- **Phase 1 (Months 1-6)**: Open-source Python library release with documentation and tutorials
- **Phase 2 (Months 6-12)**: Integration with popular LLM code generation tools (GitHub Copilot API, Tabnine)
- **Phase 3 (Months 12-24)**: Enterprise pilot programs with software companies for non-safety-critical applications

**Limitations and Scope:**

The framework is **not suitable** for:
- Safety-critical systems requiring deterministic guarantees (medical devices, avionics)
- Cross-domain code generation where exchangeability fails
- Real-time applications requiring <10ms latency (oracle evaluation overhead)

The framework **is suitable** for:
- Rapid prototyping and iterative development
- Educational tools and coding assistants
- Preliminary screening before expensive formal verification
- Non-safety-critical web/mobile application development

### 4.4 Broader Impact on AI Verification Research

**Bridging Formal Methods and Generative AI:**

This work exemplifies the VerifAI workshop's vision of integrating formal analysis with probabilistic AI:
- **Formal methods contribution**: Conformal prediction provides mathematical coverage guarantees
- **Generative AI contribution**: LLMs generate code at scale, oracles provide verification signals
- **Synergy**: Probabilistic assurances enable practical deployment where deterministic proofs are intractable

**Future Research Directions:**

1. **Adaptive conformal prediction**: Develop online learning methods that update calibration sets continuously as new verified code becomes available.

2. **Hierarchical domain decomposition**: Investigate multi-level conformal prediction (language-level → task-level → function-level) for broader applicability.

3. **Conformal prediction for other verification tasks**: Extend framework to bug localization, vulnerability detection, performance prediction.

4. **Integration with neurosymbolic methods**: Combine conformal prediction intervals with symbolic execution for hybrid verification pipelines.

**Alignment with Workshop Themes:**

- **Generative AI for formal methods**: LLMs generate code, conformal prediction provides verification
- **Formal methods for generative AI**: Statistical theory (conformal prediction) ensures AI reliability
- **AI as verifiers**: Probabilistic methods (oracles + conformal prediction) provide "soft assurances"
- **Datasets and benchmarks**: Releases curated verification benchmarks for community use
- **LLMs for code generation (special theme)**: Directly addresses uncertainty quantification for LLM-generated code

### 4.5 Success Metrics

**Publication Targets:**
- Tier-1 ML conference (NeurIPS, ICML, ICLR) or PL conference (PLDI, POPL, OOPSLA)
- VerifAI workshop paper (accepted)
- Journal extension (JMLR, TOPLAS) within 18 months

**Community Adoption Metrics:**
- GitHub repository stars: >100 within 6 months
- Downstream citations: >10 within 12 months
- Industry pilot programs: ≥2 companies within 18 months

**Technical Milestones:**
- Empirical coverage validation: ≥80% configurations pass binomial test
- Interval informativeness: ≥15% improvement over single-oracle baselines
- Computational efficiency: <1 second inference time per code sample
- Open-source release: Complete implementation with documentation and tutorials

This research addresses a critical gap in trustworthy AI for code generation, providing the first distribution-free probabilistic correctness guarantees for LLM-generated code. By bridging formal verification theory and practical generative AI deployment, we enable principled uncertainty quantification that supports informed human decision-making in software development.