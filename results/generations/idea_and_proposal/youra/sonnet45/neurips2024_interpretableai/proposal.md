# Research Proposal: Unified Interpretability Evaluation Framework for AI Systems Across Model Scales and Paradigms

## 1. Title

**Unified Interpretability Evaluation Framework: Standardizing AI Transparency Assessment Across Model Scales and Paradigms Using Multidimensional Item Response Theory**

## 2. Introduction

### 2.1 Background

The rapid advancement of artificial intelligence has led to an unprecedented diversity in model architectures, ranging from classical tabular models to large-scale foundation models with billions of parameters. As these systems increasingly influence high-stakes decisions in healthcare, criminal justice, autonomous systems, and financial lending, the demand for interpretable and transparent AI has become paramount. However, the field of interpretability research faces a critical challenge: the absence of standardized evaluation methods that can consistently assess interpretability across different model scales, paradigms, and application domains.

Current interpretability evaluation practices are fragmented and inconsistent. Classical interpretability methods for tabular data rely on rule-based models (decision trees, risk scores) and linear models (sparse linear regression, generalized additive models), which are evaluated using paradigm-specific metrics such as rule fidelity and sparsity. Modern deep learning interpretability employs attribution-based methods (LIME, SHAP, integrated gradients) assessed through faithfulness scores and stability measures. Emerging mechanistic interpretability for foundation models uses circuit analysis and feature visualization, evaluated via completeness and causal intervention metrics. This fragmentation creates several critical problems:

1. **Incomparability**: Researchers cannot reliably compare interpretability methods across paradigms, hindering scientific progress and method selection.
2. **Regulatory Compliance Uncertainty**: Emerging AI regulations (e.g., EU AI Act Article 13) require transparency assessments, but lack standardized evaluation frameworks.
3. **Domain Mismatch**: Evaluation metrics developed for one domain (e.g., computer vision) may not translate appropriately to others (e.g., healthcare diagnostics).
4. **Scalability Barriers**: Expert-based evaluation, while comprehensive, is expensive, time-consuming, and non-reproducible.

Recent surveys have highlighted this evaluation gap. Ibrahim et al. (2024) taxonomized interpretability evaluation approaches but noted the absence of unified frameworks. Carrasco Limeros et al. (2022) demonstrated domain-specific holistic evaluation for healthcare but acknowledged limited generalizability. Singh et al. (2024) identified evaluation challenges specific to large language models, emphasizing the need for scale-adaptive assessment methods.

### 2.2 Research Objectives

This research proposes the **Unified Interpretability Evaluation Framework (UIEF)**, which applies multidimensional item response theory (MIRT) from psychometrics to enable standardized, reproducible interpretability assessment across diverse AI systems. The framework draws inspiration from the Rasch model's "person-free measurement" in educational testing, adapting it to achieve "model-free interpretability measurement" in AI evaluation.

**Primary Objective**: Develop and validate a unified framework that provides consistent interpretability assessment across:
- **Model scales**: Tabular models → Neural networks → Foundation models
- **Interpretability paradigms**: Rule-based → Attribution-based → Mechanistic interpretability
- **Application domains**: Healthcare, criminal justice, autonomous systems, finance

**Secondary Objectives**:
1. Formalize scale translation functions that preserve interpretability properties (locality, faithfulness, stability, plausibility) across model architectures
2. Establish a three-level metric hierarchy (atomic → composite → holistic) enabling both detailed and summary assessments
3. Develop adaptive metric selection algorithms using MIRT to automatically filter inappropriate metrics for specific model-paradigm-domain configurations
4. Create domain-specific weighting schemes that align evaluation with regulatory requirements and stakeholder priorities
5. Validate the framework through comprehensive empirical studies demonstrating cross-scale consistency, calibration validity, and practical utility

### 2.3 Significance

This research addresses a fundamental gap in interpretability research and practice with significant theoretical, methodological, and practical implications:

**Theoretical Significance**: UIEF introduces the first formal theory of multi-scale interpretability evaluation, demonstrating that interpretability can be hierarchically composed and semantically translated across model architectures. This advances interpretability from an ad-hoc collection of methods to a principled engineering discipline with standardized assessment protocols.

**Methodological Significance**: By adapting MIRT from psychometrics, the framework enables adaptive, data-driven metric selection that accounts for both model complexity and metric difficulty. This cross-disciplinary innovation demonstrates the value of transferring measurement theory from social sciences to AI evaluation.

**Practical Significance**: UIEF provides immediate value to three key stakeholder groups:
- **Researchers**: Standardized benchmarks enable reproducible method comparison, reducing evaluation time from weeks (expert panels) to minutes (automated assessment)
- **Industry Practitioners**: Automated regulatory compliance checking reduces audit costs by ~90% (weeks to hours) while improving method selection accuracy by >15%
- **Regulators**: Objective, reproducible evaluation supports evidence-based policy development and enforcement

The framework's open-source implementation with sklearn-like API (`uief.evaluate(model, data, paradigm='auto', domain='healthcare')`) ensures broad accessibility and adoption potential across academia and industry.

## 3. Methodology

### 3.1 Framework Architecture

UIEF operates through a five-stage pipeline that transforms raw model outputs into standardized interpretability scores:

**Stage 1: Atomic Metric Computation (L1)**  
Paradigm-specific metrics are computed based on the model's interpretability paradigm:
- **Rule-based**: Rule fidelity $F_r$, rule count $N_r$, rule overlap $O_r$
- **Attribution-based**: Faithfulness score $F_a$, stability $S_a$, sparsity $Sp_a$
- **Mechanistic**: Circuit completeness $C_m$, intervention causality $I_m$, feature interpretability $F_m$

**Stage 2: Adaptive Calibration via MIRT**  
Model complexity $\theta_{model}$ and metric difficulty $\Delta_{metric}$ are estimated using a two-parameter logistic MIRT model:

$$P(m_{ij} = 1 | \theta_i, \Delta_j, \alpha_j) = \frac{1}{1 + \exp(-\alpha_j(\theta_i - \Delta_j))}$$

where:
- $m_{ij}$: Binary indicator of metric $j$ applicability to model $i$
- $\theta_i$: Latent complexity of model $i$ (estimated from architecture features)
- $\Delta_j$: Difficulty parameter of metric $j$ (calibrated from expert annotations)
- $\alpha_j$: Discrimination parameter of metric $j$

This adaptive filtering prevents inappropriate metric application (e.g., circuit analysis to decision trees).

**Stage 3: Scale Translation**  
When cross-scale comparison is required, semantic-preserving translation functions map metrics across architectures while maintaining core interpretability properties:

$$f_{locality}: I_{tabular}^{feature} \rightarrow I_{neural}^{saliency} \rightarrow I_{transformer}^{attention}$$

Translation functions are defined for four core properties:
- **Locality**: $L(x) = \mathbb{E}_{x' \sim \mathcal{N}(x, \sigma)}[|I(x) - I(x')|]$ (consistency under local perturbations)
- **Faithfulness**: $F(x) = \text{corr}(I(x), \Delta f(x))$ (correlation between importance and model output change)
- **Stability**: $S(x) = 1 - \text{Var}_{seed}[I(x)]$ (robustness to random initialization)
- **Plausibility**: $P(x) = \text{agreement}(I(x), \text{expert}(x))$ (alignment with domain expertise)

**Stage 4: Hierarchical Aggregation**  
Metrics are composed from atomic (L1) to composite (L2) to holistic (L3) levels:

$$I_{L2}^{consistency} = w_1 \cdot F_a + w_2 \cdot S_a + w_3 \cdot \text{cross-method-agreement}$$

$$I_{L3}^{overall} = \sum_{k=1}^{K} w_k^{domain} \cdot I_{L2}^{(k)}$$

where $w_k^{domain}$ are domain-specific weights (e.g., healthcare emphasizes transparency and fairness; autonomous systems emphasize real-time interpretability).

**Stage 5: Domain Adaptation**  
Domain-specific weighting vectors $\mathbf{W}_{domain}$ adjust metric importance based on regulatory requirements and stakeholder priorities:

$$\mathbf{W}_{healthcare} = [0.4_{transparency}, 0.3_{fairness}, 0.2_{stability}, 0.1_{efficiency}]$$

$$\mathbf{W}_{autonomous} = [0.5_{real-time}, 0.3_{safety}, 0.15_{transparency}, 0.05_{fairness}]$$

### 3.2 Data Collection

**3.2.1 Model Dataset**  
We will construct a comprehensive benchmark suite spanning 45 configurations:
- **5 model scales**: Decision trees, random forests, feedforward neural networks, ResNet-50, GPT-2
- **3 paradigms**: Rule-based (CART, RuleFit), attribution-based (LIME, SHAP, IntegratedGradients), mechanistic (circuit analysis, feature visualization)
- **3 domains**: Healthcare (MIMIC-III mortality prediction), criminal justice (COMPAS recidivism), autonomous systems (BDD100K driving decisions)

Each configuration includes:
- Pre-trained model checkpoints
- Standardized test datasets (N=1000 samples per domain)
- Ground-truth interpretability annotations from domain experts

**3.2.2 Expert Calibration Data**  
To calibrate MIRT parameters, we will collect expert assessments:
- **N=5 experts** per domain (total 15 experts: 5 healthcare ML researchers, 5 criminal justice AI ethicists, 5 autonomous systems engineers)
- **Assessment protocol**: Each expert evaluates 60 models (20 per domain) on:
  - Model complexity (1-10 scale): architectural complexity, parameter count, training data size
  - Metric difficulty (1-10 scale): computational cost, interpretability of metric output, domain expertise required
  - Holistic interpretability (1-10 scale): overall transparency, trustworthiness, actionability

**3.2.3 Synthetic Calibration Bootstrap**  
To reduce initial expert annotation burden, we employ a three-phase calibration strategy:

1. **Phase 1 (Synthetic)**: Generate 200 synthetic models with known complexity parameters (linear models with controlled sparsity, neural networks with controlled depth/width)
2. **Phase 2 (Transfer)**: Use transfer learning to map synthetic parameters to real model architectures via feature-based regression:
   $$\theta_{real} = g(\text{depth}, \text{width}, \text{params}, \text{FLOPs}) + \epsilon$$
3. **Phase 3 (Community)**: Continuously refine calibration as community contributes additional expert annotations

### 3.3 Algorithmic Steps

**Algorithm 1: UIEF Evaluation Pipeline**

```
Input: model M, dataset D, paradigm P (optional), domain Dom
Output: Interpretability score I_overall, detailed report R

1. Paradigm Detection (if P not specified):
   P ← detect_paradigm(M)  // Rule-based, attribution, mechanistic

2. Atomic Metric Computation (L1):
   metrics_L1 ← compute_atomic_metrics(M, D, P)
   // Returns {F_r, N_r, O_r} or {F_a, S_a, Sp_a} or {C_m, I_m, F_m}

3. MIRT Adaptive Filtering:
   θ_M ← estimate_model_complexity(M)
   applicable_metrics ← filter_metrics(metrics_L1, θ_M, Δ_calibrated)
   // Removes metrics where P(applicable | θ_M, Δ_j) < 0.5

4. Scale Translation (if cross-scale comparison):
   if requires_translation(M, reference_scale):
       metrics_L1 ← translate_metrics(metrics_L1, M.scale, reference_scale)
       // Applies f_locality, f_faithfulness, f_stability, f_plausibility

5. Hierarchical Aggregation:
   metrics_L2 ← aggregate_L1_to_L2(applicable_metrics)
   // Computes consistency, human_alignment, robustness composites
   
   I_overall ← aggregate_L2_to_L3(metrics_L2, W_domain[Dom])
   // Applies domain-specific weighting

6. Report Generation:
   R ← generate_report(metrics_L1, metrics_L2, I_overall, Dom)
   // Includes regulatory compliance check, method comparison

Return I_overall, R
```

**Algorithm 2: MIRT Calibration**

```
Input: Expert annotations E = {(model_i, complexity_i, {metric_j, difficulty_ij})}
Output: Calibrated parameters Θ = {θ_i}, Δ = {Δ_j, α_j}

1. Initialize parameters:
   Θ ← random_normal(0, 1, n_models)
   Δ ← random_normal(0, 1, n_metrics)
   α ← ones(n_metrics)

2. Expectation-Maximization:
   for epoch in 1..max_epochs:
       // E-step: Estimate latent complexity
       for model_i in models:
           θ_i ← argmax_θ P(E_i | θ, Δ, α)
       
       // M-step: Update metric parameters
       for metric_j in metrics:
           Δ_j, α_j ← argmax_{Δ,α} P(E_j | Θ, Δ, α)
       
       if convergence_criterion(Θ, Δ, α):
           break

3. Validation:
   ρ_complexity ← correlation(Θ, expert_complexity)
   ρ_difficulty ← correlation(Δ, expert_difficulty)
   
   if ρ_complexity < 0.7 or ρ_difficulty < 0.7:
       warn("Calibration quality below threshold")

Return Θ, Δ, α
```

### 3.4 Experimental Design

We will conduct five validation studies to test the framework's core hypotheses:

**Study 1: Cross-Scale Consistency Validation (P1)**

*Objective*: Verify that scale translation preserves interpretability semantics (target: $\rho_{cross-scale} > 0.6$)

*Design*:
- **Models**: N=30 (10 tabular, 10 neural, 10 transformer)
- **Methods**: 6 interpretability methods (2 per paradigm)
- **Procedure**:
  1. Compute interpretability scores using paradigm-native metrics
  2. Translate scores to common reference scale (neural network scale)
  3. Compare translated scores with direct neural network evaluations
- **Metrics**: Spearman correlation $\rho_{cross-scale}$ between translated and native scores
- **Success Criterion**: $\rho_{cross-scale} > 0.6$ (moderate-to-strong consistency)
- **Falsification**: $\rho_{cross-scale} < 0.3$ invalidates scale translation approach

**Study 2: MIRT Calibration Validity (P2)**

*Objective*: Validate that MIRT-estimated parameters align with expert judgments (target: $\rho > 0.7$)

*Design*:
- **Models**: N=60 (20 per domain)
- **Metrics**: 25 interpretability metrics across paradigms
- **Experts**: 5 per domain (15 total)
- **Procedure**:
  1. Collect expert ratings of model complexity and metric difficulty
  2. Calibrate MIRT parameters using Algorithm 2
  3. Correlate $\theta_{model}$ with expert complexity ratings
  4. Correlate $\Delta_{metric}$ with expert difficulty ratings
- **Metrics**: 
  - $\rho(\theta_{MIRT}, \text{complexity}_{expert})$
  - $\rho(\Delta_{MIRT}, \text{difficulty}_{expert})$
- **Success Criterion**: Both correlations $> 0.7$
- **Falsification**: Either correlation $< 0.4$ suggests MIRT doesn't generalize to interpretability evaluation

**Study 3: Hierarchical Composition Validation (P3)**

*Objective*: Verify that L3 holistic scores preserve information from L1 atomic metrics (target: $\rho > 0.7$)

*Design*:
- **Models**: N=30 (10 per domain)
- **Experts**: 10 (mixed domain expertise)
- **Procedure**:
  1. Compute UIEF L3 holistic scores
  2. Collect independent expert holistic interpretability ratings
  3. Correlate UIEF L3 with expert holistic judgments
- **Metrics**: Spearman correlation $\rho(I_{L3}, \text{expert}_{holistic})$
- **Success Criterion**: $\rho > 0.7$
- **Falsification**: $\rho < 0.4$ indicates critical information loss in aggregation

**Study 4: Domain Adaptation Effectiveness (P4)**

*Objective*: Demonstrate that domain-specific weighting improves deployment prediction (target: AUC improvement $> 0.1$)

*Design*:
- **Models**: N=40 deployed models (20 healthcare, 20 autonomous systems)
- **Ground Truth**: Binary deployment success (maintained in production >6 months)
- **Procedure**:
  1. Compute UIEF scores with domain-agnostic weights (equal weighting)
  2. Compute UIEF scores with domain-specific weights
  3. Train logistic regression: $P(\text{success}) = \sigma(\beta_0 + \beta_1 \cdot I_{UIEF})$
  4. Compare AUC for domain-adapted vs. agnostic scores
- **Metrics**: $\Delta AUC = AUC_{domain} - AUC_{agnostic}$
- **Success Criterion**: $\Delta AUC > 0.1$
- **Falsification**: $\Delta AUC \leq 0$ suggests domain adaptation provides no value

**Study 5: Framework Utility Randomized Controlled Trial (P5)**

*Objective*: Demonstrate practical utility in method selection tasks (target: $>15\%$ improvement)

*Design*:
- **Participants**: N=40 ML researchers (20 treatment, 20 control)
- **Task**: Select best interpretability method for 5 scenarios (healthcare diagnosis, loan approval, autonomous driving, content moderation, fraud detection)
- **Conditions**:
  - **Treatment**: Access to UIEF evaluation reports
  - **Control**: Access to method documentation only (current practice)
- **Procedure**:
  1. Participants select methods for each scenario
  2. Expert panel (N=3 per domain) rates selection quality (1-10 scale)
  3. Compare mean quality scores between conditions
- **Metrics**: 
  - Mean selection quality: $\bar{Q}_{UIEF}$ vs. $\bar{Q}_{control}$
  - Improvement: $\frac{\bar{Q}_{UIEF} - \bar{Q}_{control}}{\bar{Q}_{control}}$
- **Success Criterion**: Improvement $> 15\%$
- **Falsification**: Improvement $< 5\%$ questions practical adoption value

### 3.5 Evaluation Metrics

**Primary Metrics**:
1. **Cross-scale consistency**: $\rho_{cross-scale}$ (Spearman correlation)
2. **Calibration validity**: $\rho(\theta, \text{expert})$, $\rho(\Delta, \text{expert})$
3. **Composition fidelity**: $\rho(I_{L3}, \text{expert}_{holistic})$
4. **Domain adaptation gain**: $\Delta AUC$
5. **Practical utility**: Percentage improvement in method selection quality

**Secondary Metrics**:
1. **Computational efficiency**: Evaluation time (seconds per model)
2. **Calibration data efficiency**: Minimum expert annotations for $\rho > 0.7$
3. **Robustness**: Score stability under metric perturbations (bootstrap resampling)
4. **Coverage**: Percentage of model-paradigm-domain configurations successfully evaluated

**Statistical Analysis**:
- **Power analysis**: All studies powered at 0.80 to detect medium effect sizes (Cohen's d=0.5) at α=0.05
- **Multiple comparison correction**: Bonferroni correction for five primary hypotheses (adjusted α=0.01)
- **Sensitivity analysis**: Bootstrap confidence intervals (10,000 iterations) for all correlation estimates

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Theoretical Outcomes**:
1. **Formalization of Multi-Scale Interpretability Theory**: Mathematical framework demonstrating that interpretability properties (locality, faithfulness, stability, plausibility) can be preserved across model scales through semantic-preserving translation functions
2. **Hierarchical Composition Theory**: Proof-of-concept that interpretability can be hierarchically composed (atomic → composite → holistic) without critical information loss ($\rho > 0.7$)
3. **Model-Free Measurement Paradigm**: First demonstration of architecture-agnostic interpretability evaluation analogous to Rasch model's person-free measurement in psychometrics

**Methodological Outcomes**:
1. **Validated UIEF Framework**: Open-source Python library (`uief`) with sklearn-compatible API, achieving:
   - Cross-scale consistency: $\rho_{cross-scale} > 0.6$
   - MIRT calibration validity: $\rho > 0.7$ for both complexity and difficulty parameters
   - Hierarchical composition fidelity: $\rho(I_{L3}, \text{expert}) > 0.7$
2. **Comprehensive Benchmark Suite**: 45-configuration test suite (5 scales × 3 paradigms × 3 domains) with standardized evaluation protocols
3. **Calibrated Metric Database**: Community-contributed database of MIRT-calibrated metrics with difficulty and discrimination parameters
4. **Regulatory Compliance Checker**: Automated EU AI Act Article 13 compliance assessment tool

**Empirical Outcomes**:
1. **Domain Adaptation Effectiveness**: $>10\%$ AUC improvement in deployment success prediction using domain-specific weighting
2. **Practical Utility**: $>15\%$ improvement in method selection quality when researchers use UIEF vs. ad-hoc evaluation
3. **Efficiency Gains**: Evaluation time reduction from days (expert panels) to minutes (automated UIEF), representing ~99% time savings

### 4.2 Scientific Impact

**Advancing Interpretability Research**:
- **Standardization**: UIEF provides the first standardized benchmark enabling reproducible method comparison across paradigms, addressing a critical gap identified by Ibrahim et al. (2024)
- **Evaluation Rigor**: Shifts interpretability evaluation from subjective expert judgment to objective, data-driven assessment, raising methodological standards
- **Cross-Paradigm Insights**: Enables systematic comparison of rule-based, attribution-based, and mechanistic interpretability approaches, revealing relative strengths and limitations
- **Accelerated Innovation**: Frees researchers from evaluation debates to focus on method development, potentially accelerating interpretability research progress

**Methodological Contributions to ML**:
- **Cross-Domain Transfer**: Demonstrates successful adaptation of psychometric measurement theory (MIRT) to ML evaluation, opening new research directions in ML assessment
- **Multi-Scale Modeling**: Advances understanding of how properties can be preserved across architectural scales, with implications beyond interpretability (e.g., robustness, fairness evaluation)
- **Hierarchical Evaluation Design**: Establishes template for multi-level evaluation frameworks applicable to other ML properties (privacy, fairness, robustness)

### 4.3 Practical Impact

**Industry Deployment**:
- **Method Selection**: $>15\%$ improvement in deployment success rate through evidence-based interpretability method selection
- **Cost Reduction**: ~90% reduction in regulatory compliance audit costs (weeks to hours) through automated assessment
- **Risk Mitigation**: Early detection of interpretability failures before deployment, reducing reputational and legal risks
- **Stakeholder Communication**: Standardized scores facilitate transparent communication with non-technical stakeholders (regulators, patients, defendants)

**Regulatory Support**:
- **Evidence-Based Policy**: Provides objective evaluation framework supporting evidence-based AI regulation development
- **Compliance Verification**: Enables scalable, reproducible compliance checking for regulations requiring transparency (EU AI Act, FDA medical device guidance)
- **International Harmonization**: Standardized evaluation facilitates international regulatory alignment and mutual recognition

**Societal Impact**:
- **Trust in AI**: Objective, reproducible interpretability assessment increases public trust in high-stakes AI systems
- **Accountability**: Standardized evaluation enables meaningful accountability for AI decisions affecting human lives
- **Equity**: Reduces barriers to interpretability adoption by providing accessible, automated evaluation tools to under-resourced organizations

### 4.4 Limitations and Future Work

**Known Limitations**:
1. **Calibration Overhead**: Initial 3-6 month calibration period required for new domains
2. **Paradigm Coverage**: Current version excludes example-based and interactive explanations
3. **MIRT Assumptions**: Assumes continuous latent dimensions, which may not hold for discrete interpretability properties
4. **Expert Dependence**: Calibration quality depends on expert panel diversity and expertise

**Future Research Directions**:
1. **Extension to LLM Natural Language Explanations**: Develop semantic similarity metrics for evaluating textual explanations from large language models
2. **Reinforcement Learning Adaptation**: Extend framework to policy interpretability in RL agents
3. **Causal Interpretability**: Integrate causal discovery methods to evaluate causal (not just correlational) explanations
4. **Automated Calibration**: Develop self-supervised calibration methods reducing expert annotation requirements
5. **Real-Time Evaluation**: Optimize computational efficiency for online interpretability monitoring in production systems

### 4.5 Dissemination and Adoption Strategy

**Academic Dissemination**:
- **Publications**: Target top-tier venues (NeurIPS, ICML, ICLR, FAccT) for framework paper and validation studies
- **Workshop Presentations**: Present at Interpretable AI workshops to gather community feedback
- **Tutorial Sessions**: Organize tutorials at major conferences demonstrating UIEF usage

**Open-Source Community Building**:
- **GitHub Repository**: Comprehensive documentation, tutorials, and example notebooks
- **Community Contribution Platform**: Enable researchers to contribute calibration data and new metrics
- **Benchmark Leaderboard**: Public leaderboard tracking interpretability method performance across UIEF benchmark suite

**Industry Engagement**:
- **Industry Partnerships**: Collaborate with healthcare (Epic, Cerner), finance (Stripe, Square), and autonomous systems (Waymo, Cruise) companies for real-world validation
- **Regulatory Engagement**: Present framework to regulatory bodies (FDA, EU AI Office) as potential compliance assessment tool
- **Professional Training**: Develop certification program for UIEF-based interpretability auditing

**Timeline**: 12-month research phase, followed by 6-month community adoption phase, with ongoing maintenance and extension.

**Budget**: Estimated $30,000 for academic-scale implementation (expert annotation costs, compute resources, conference travel), scalable to $150,000 for industry-scale validation with larger expert panels and real-world deployment studies.

This research has the potential to transform interpretability evaluation from a fragmented, subjective practice into a standardized, objective discipline, ultimately advancing the responsible development and deployment of AI systems in high-stakes domains.