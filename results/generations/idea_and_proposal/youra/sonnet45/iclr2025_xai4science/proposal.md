# Research Proposal: SynthEx - Synthetic Oracle Verification Framework for Ante-Hoc Explainable AI in Scientific Discovery

## 1. Title

**SynthEx: A Hybrid Synthetic-Real Verification Framework for Validating Explanation Faithfulness in Ante-Hoc Interpretable Models for Scientific Discovery**

## 2. Introduction

### 2.1 Background

Machine learning (ML) models have become indispensable tools in scientific discovery, driving breakthroughs in climate science, materials engineering, and healthcare diagnostics. However, a critical challenge undermines their potential: we cannot reliably verify whether model explanations reflect true causal reasoning or merely spurious correlations. This "faithfulness gap" creates a fundamental barrier to using ML for knowledge discovery—scientists cannot trust model explanations to guide hypothesis generation, experimental design, or mechanistic understanding.

Current approaches to explainable AI (XAI) fall into two categories: post-hoc methods that explain black-box models after training (e.g., SHAP, LIME, GradCAM) and ante-hoc methods that build interpretability into model architecture (e.g., concept bottleneck networks, attention mechanisms, prototype-based models). While ante-hoc models promise inherently interpretable representations, recent work by Christiansen et al. (2023) demonstrates that self-explainable models often generate unfaithful explanations—their highlighted features do not causally influence predictions despite appearing interpretable.

The verification challenge is particularly acute for ante-hoc models. Unlike post-hoc methods where explanation quality can be compared against the base model, ante-hoc explanations are the model's primary output, requiring independent ground truth for validation. Current verification approaches rely on: (1) qualitative expert assessment—expensive, subjective, and unscalable; (2) post-hoc comparison methods—circular reasoning when validating ante-hoc models; or (3) synthetic tasks without validated transfer to real applications. None provide objective, scalable verification with proven real-world validity.

This gap is especially problematic in scientific domains where explanation faithfulness directly impacts knowledge discovery. In climate attribution, unfaithful explanations could misidentify drivers of extreme weather events. In materials science, incorrect feature importance could waste experimental resources on irrelevant compositional factors. In healthcare diagnostics, misleading explanations could compromise clinical decision-making and patient safety.

### 2.2 Research Objectives

This research proposes **SynthEx**, a two-stage hybrid verification framework that addresses the faithfulness verification challenge through synthetic tasks with constructible ground-truth "explanation oracles." Our primary objectives are:

**O1. Develop Explanation Oracle Methodology:** Adapt test oracle concepts from systems engineering to create synthetic scientific tasks where ground-truth explanations are embedded by construction, enabling objective faithfulness measurement.

**O2. Establish Synthetic-Real Transfer Validity:** Empirically validate that faithfulness scores on synthetic tasks predict expert-validated faithfulness on real-world scientific problems across climate, materials, and healthcare domains.

**O3. Create Efficient Verification Pipeline:** Design a two-stage framework where Stage 1 provides scalable synthetic screening (reducing expert annotation burden by ~70%) and Stage 2 validates transfer to real applications.

**O4. Benchmark Ante-Hoc Architectures:** Systematically evaluate concept-based, attention-based, and prototype-based models to identify architectural features that promote faithful explanations.

Our **central hypothesis** (H1) states: Ante-hoc interpretable models achieving high explanation-oracle alignment on synthetic tasks (composite faithfulness score ≥0.80 across structural, semantic, and causal metrics) will demonstrate significantly higher expert-validated faithfulness on real-world tasks (agreement ≥0.70) compared to models selected without synthetic verification (baseline ~0.45-0.55).

### 2.3 Significance

This research makes four critical contributions to XAI and scientific ML:

**Theoretical Contribution:** We introduce the **explanation oracle framework**—the first systematic adaptation of test oracle methodology from systems engineering to ante-hoc XAI. This establishes a principled foundation for constructing verifiable ground-truth explanations and formalizes the synthetic-real transfer principle for explanation faithfulness.

**Methodological Contribution:** SynthEx provides the first unified verification framework applicable across diverse ante-hoc architectures (concept bottleneck networks, attention mechanisms, prototype models) and scientific domains. The multi-metric assessment (structural + semantic + causal alignment) captures complementary aspects of faithfulness that single metrics miss.

**Practical Contribution:** By reducing expert annotation requirements by ~70% while maintaining validity, SynthEx makes rigorous explanation verification feasible for resource-constrained scientific teams. The resulting benchmark suite (60-90 synthetic tasks across three domains) provides standardized evaluation infrastructure for the XAI community.

**Scientific Impact:** Most importantly, SynthEx enables trustworthy deployment of interpretable ML for knowledge discovery. Scientists can confidently use verified model explanations to generate hypotheses about climate mechanisms, materials properties, or disease pathways, accelerating the scientific discovery cycle.

The framework directly addresses the workshop's core challenge: moving beyond understanding model behavior to discovering new scientific knowledge. By establishing when and why ante-hoc explanations can be trusted, we create a pathway for ML models to genuinely aid human knowledge rather than merely producing opaque predictions.

## 3. Methodology

### 3.1 Overall Framework Architecture

SynthEx operates as a two-stage verification pipeline:

**Stage 1 (Synthetic Screening):** Models are evaluated on a battery of 60-90 synthetic tasks with constructible ground-truth explanation oracles. High-performing models (composite score ≥0.80) advance to Stage 2.

**Stage 2 (Real-World Validation):** Stage 1 survivors are tested on real scientific tasks with expert-annotated explanations to validate synthetic-real transfer and measure practical faithfulness.

### 3.2 Stage 1: Synthetic Oracle Construction

#### 3.2.1 Domain-Informed Task Design

For each scientific domain, we construct 20-30 synthetic tasks embedding known causal mechanisms:

**Climate Attribution Tasks:**
- **Task Example:** Predict extreme precipitation events from atmospheric variables
- **Ground-Truth Mechanism:** Embedded causal graph with known relationships (e.g., moisture convergence → precipitation, temperature → evaporation → moisture)
- **Data Generation:** Physics-informed simulation using simplified climate models with controllable parameters
- **Oracle Construction:** True causal factors are known by construction (e.g., moisture flux has weight 0.6, temperature 0.3, pressure 0.1)

**Materials Property Prediction Tasks:**
- **Task Example:** Predict bandgap energy from elemental composition
- **Ground-Truth Mechanism:** Embedded quantum mechanical relationships (e.g., electronegativity difference, atomic radius effects)
- **Data Generation:** Density functional theory (DFT) calculations with known feature contributions
- **Oracle Construction:** Feature importance derived from sensitivity analysis of DFT parameters

**Healthcare Diagnostic Tasks:**
- **Task Example:** Predict disease risk from clinical biomarkers
- **Ground-Truth Mechanism:** Embedded pathophysiological pathways (e.g., glucose → insulin resistance → diabetes)
- **Data Generation:** Mechanistic disease models with known biomarker relationships
- **Oracle Construction:** Causal pathway weights from established clinical literature

#### 3.2.2 Synthetic Data Generation Protocol

For each task $T_i$, we generate dataset $D_i = \{(x_j, y_j, e_j^*)\}_{j=1}^{N}$ where:
- $x_j \in \mathbb{R}^d$: Input features
- $y_j \in \mathbb{R}$ or $\{0,1\}$: Target variable
- $e_j^* = (f_1^*, f_2^*, ..., f_k^*)$: Ground-truth explanation oracle (true causal features)

The generation process follows:

$$x_j = g(\theta, \epsilon_j)$$

$$y_j = h(x_j; w^*) + \eta_j$$

where $g$ is a domain-specific data generator with parameters $\theta$, $h$ is the known causal function with true weights $w^*$, $\epsilon_j$ is input noise, and $\eta_j$ is output noise.

The explanation oracle $e_j^*$ is derived from $w^*$ through:

$$e_j^* = \text{TopK}(\nabla_{x_j} h(x_j; w^*), k)$$

This ensures ground-truth explanations reflect true causal influence by construction.

#### 3.2.3 Task Complexity Calibration

Synthetic tasks span controlled complexity levels:
- **Simple:** 2-3 causal factors, linear relationships
- **Moderate:** 4-6 causal factors, non-linear interactions
- **Complex:** 7-10 causal factors, hierarchical dependencies

This range ensures tasks are simple enough for oracle construction yet complex enough to test explanation mechanisms that transfer to real problems.

### 3.3 Multi-Metric Faithfulness Assessment

For each model $M$ producing explanation $e_M(x)$ on input $x$ with oracle $e^*(x)$, we compute three complementary metrics:

#### 3.3.1 Structural Alignment (S)

Measures overlap between model-identified and oracle-identified important features:

$$S(e_M, e^*) = \frac{|\text{TopK}(e_M, k) \cap \text{TopK}(e^*, k)|}{k}$$

where $k$ is the number of ground-truth causal features. Threshold: $S \geq 0.85$.

#### 3.3.2 Semantic Similarity (M)

Measures continuous similarity of explanation representations:

$$M(e_M, e^*) = \frac{e_M \cdot e^*}{\|e_M\|_2 \|e^*\|_2}$$

This captures whether explanation magnitudes align with oracle importance weights. Threshold: $M \geq 0.80$.

#### 3.3.3 Causal Consistency (C)

Measures whether model explanations predict correct intervention effects. For feature $f_i$, we intervene by setting $x_i' = x_i + \delta$ and measure:

$$C_i = \mathbb{1}[\text{sign}(\Delta y_M) = \text{sign}(\Delta y^*)]$$

where $\Delta y_M = M(x') - M(x)$ is the model's prediction change and $\Delta y^* = h(x'; w^*) - h(x; w^*)$ is the oracle's true effect. Overall causal consistency:

$$C = \frac{1}{k}\sum_{i=1}^{k} C_i$$

Threshold: $C \geq 0.75$.

#### 3.3.4 Composite Faithfulness Score

The final synthetic faithfulness score combines all metrics:

$$F_{\text{synthetic}} = 0.4 \cdot S + 0.3 \cdot M + 0.3 \cdot C$$

Weights reflect relative importance: structural alignment (40%) is most critical, while semantic and causal metrics (30% each) provide complementary validation. Models advance to Stage 2 if $F_{\text{synthetic}} \geq 0.80$.

### 3.4 Stage 2: Real-World Validation

#### 3.4.1 Real Task Selection

For each domain, we select 100-150 samples from established scientific datasets:

**Climate:** CMIP6 extreme event attribution dataset with expert-labeled causal factors
**Materials:** Materials Project bandgap prediction with DFT-validated feature importance
**Healthcare:** MIMIC-III clinical diagnosis with physician-annotated decision factors

#### 3.4.2 Expert Annotation Protocol

Three domain experts independently annotate ground-truth explanations for each sample:
1. Identify top-k causal features (forced ranking)
2. Assign importance weights (sum to 1.0)
3. Validate causal direction (positive/negative influence)

Final oracle $e_{\text{expert}}$ is determined by majority vote with conflict resolution through discussion.

#### 3.4.3 Real-World Faithfulness Measurement

For model explanation $e_M$ and expert oracle $e_{\text{expert}}$, we compute:

$$F_{\text{real}} = \kappa(e_M, e_{\text{expert}})$$

where $\kappa$ is Cohen's kappa measuring inter-rater agreement. Success criterion: $F_{\text{real}} \geq 0.70$.

### 3.5 Experimental Design

#### 3.5.1 Model Architectures

We evaluate 15-25 ante-hoc models across three architecture families:

**Concept-Based Models (5-8 variants):**
- Concept Bottleneck Networks (CBN)
- Concept Embedding Models (CEM)
- Self-Explaining Neural Networks (SENN)

**Attention-Based Models (5-8 variants):**
- Multi-head self-attention with explanation heads
- Sparse attention mechanisms
- Hierarchical attention networks

**Prototype-Based Models (5-8 variants):**
- ProtoPNet
- ProtoTree
- Case-based reasoning networks

Each architecture is trained with standard hyperparameters: Adam optimizer, learning rate $10^{-3}$, batch size 32, 100 epochs with early stopping.

#### 3.5.2 Hypothesis Testing

**Primary Hypothesis Test (H1):**

$$H_1: \mu(F_{\text{real}} | F_{\text{synthetic}} \geq 0.80) > \mu(F_{\text{real}} | \text{no verification})$$

**Test:** Independent samples t-test
**Expected Effect:** Cohen's $d \geq 0.8$ (large effect)
**Sample Size:** $n=15$ models per group provides 80% power at $\alpha=0.05$
**Success Criterion:** $p < 0.05$ with mean difference $\geq 0.15$

**Secondary Analysis - Transfer Correlation:**

$$H_2: \rho(F_{\text{synthetic}}, F_{\text{real}}) \geq 0.6$$

**Test:** Pearson correlation across all models
**Success Criterion:** $r \geq 0.6$, $p < 0.01$

**Tertiary Analysis - Domain Specificity:**

Mixed ANOVA with factors:
- **Between:** Architecture (3 levels)
- **Within:** Domain (3 levels)

This tests whether synthetic verification advantage generalizes across domains or requires domain-specific calibration.

#### 3.5.3 Falsification Criteria

The hypothesis is **falsified** if any of:
1. **No correlation:** $r(F_{\text{synthetic}}, F_{\text{real}}) < 0.3$, $p > 0.05$ across $\geq 5$ model types
2. **No advantage:** Verified models show $F_{\text{real}} \leq 0.55$ (within baseline range)
3. **Gaming observed:** $F_{\text{synthetic}} \geq 0.85$ but $F_{\text{real}} < 0.40$ for any model
4. **Cross-domain failure:** Framework works in one domain but $r < 0.2$ in others

### 3.6 Evaluation Metrics

**Primary Metrics:**
- **Synthetic Faithfulness:** $F_{\text{synthetic}}$ (composite score 0-1)
- **Real Faithfulness:** $F_{\text{real}}$ (Cohen's kappa 0-1)
- **Transfer Validity:** Pearson $r$ between synthetic and real scores

**Secondary Metrics:**
- **Efficiency Gain:** Reduction in expert annotation burden (target: 70%)
- **Threshold Sensitivity:** Performance across $F_{\text{synthetic}}$ thresholds [0.70, 0.75, 0.80, 0.85]
- **Architecture Ranking:** Consistency of model rankings between Stage 1 and Stage 2

**Diagnostic Metrics:**
- **Oracle Plausibility:** Expert assessment of synthetic oracle quality (target: ≥0.80)
- **Metric Reliability:** Cronbach's alpha for S, M, C metrics (target: ≥0.75)
- **Inter-Expert Agreement:** Fleiss' kappa for real-world annotations (target: ≥0.60)

### 3.7 Implementation Plan

**Phase 1 (Months 1-4):** Synthetic task construction
- Design 60-90 tasks with domain expert input
- Validate oracle plausibility (expert review)
- Generate synthetic datasets (10,000 samples per task)

**Phase 2 (Months 5-8):** Stage 1 evaluation
- Train 15-25 ante-hoc models on synthetic tasks
- Compute S, M, C metrics and composite scores
- Analyze metric reliability and task difficulty

**Phase 3 (Months 9-12):** Stage 2 validation
- Collect expert annotations for real tasks (300-450 samples)
- Evaluate Stage 1 survivors on real tasks
- Conduct correlation and hypothesis testing

**Phase 4 (Months 13-15):** Analysis and dissemination
- Cross-domain comparison
- Sensitivity analyses
- Benchmark release and documentation

## 4. Expected Outcomes & Impact

### 4.1 Expected Outcomes

**Primary Outcome:** We expect to demonstrate that ante-hoc models passing synthetic verification (Stage 1 score ≥0.80) achieve expert-validated faithfulness ≥0.70 on real tasks, compared to baseline ~0.50 for unverified models. This 20-point improvement (Cohen's $d \geq 0.8$) would establish synthetic oracles as valid proxies for real faithfulness.

**Transfer Validity:** We anticipate moderate-to-strong correlation ($r = 0.6-0.75$) between synthetic and real faithfulness scores, with strongest transfer in climate attribution (physics-informed tasks) and weakest in healthcare (more complex causal structures). This would validate the synthetic-real transfer principle while identifying boundary conditions.

**Architectural Insights:** We expect concept-based models to achieve highest structural alignment ($S \geq 0.90$) due to explicit concept representations, attention-based models to excel at semantic similarity ($M \geq 0.85$) through learned importance weights, and prototype-based models to show strongest causal consistency ($C \geq 0.80$) via case-based reasoning. These differential strengths would guide architecture selection for specific scientific applications.

**Efficiency Gains:** By screening 15-25 models in Stage 1 and advancing only 5-8 to expert validation in Stage 2, we project 67-73% reduction in expert annotation burden while maintaining verification quality. This would make rigorous faithfulness assessment feasible for typical research teams.

### 4.2 Scientific Impact

**Trustworthy Knowledge Discovery:** SynthEx enables scientists to confidently use model explanations for hypothesis generation. A climate scientist could trust a verified model's attribution of extreme rainfall to moisture convergence patterns, guiding targeted observational campaigns. A materials scientist could rely on verified feature importance to prioritize compositional experiments, reducing costly trial-and-error.

**Standardized Evaluation Infrastructure:** The benchmark suite provides the XAI community with standardized tasks for comparing ante-hoc methods, similar to how ImageNet standardized computer vision. This accelerates progress by enabling fair comparisons and identifying promising architectural directions.

**Methodological Foundation:** The explanation oracle framework establishes theoretical grounding for XAI verification, moving the field beyond ad-hoc validation toward principled evaluation. This could inspire similar oracle-based approaches for other ML trustworthiness dimensions (robustness, fairness, privacy).

### 4.3 Broader Implications

**Regulatory Compliance:** In high-stakes domains like healthcare, SynthEx provides auditable evidence of explanation quality, supporting regulatory requirements for AI transparency (e.g., EU AI Act, FDA guidance on medical AI).

**Interdisciplinary Bridge:** By adapting systems engineering V&V methodology to ML, this work strengthens connections between computer science and traditional engineering disciplines, fostering cross-pollination of verification techniques.

**Limitations and Future Work:** SynthEx focuses on supervised tasks with 2-10 causal factors—extending to unsupervised learning, high-dimensional causal structures, or purely qualitative explanations remains future work. The framework also requires domain expertise for synthetic task design, which may limit accessibility. Future research could develop automated oracle construction methods or transfer learning approaches to reduce expert involvement.

**Long-Term Vision:** Ultimately, SynthEx contributes to a future where ML models are not just predictive tools but trusted scientific instruments—where model explanations carry the same epistemic weight as experimental measurements, enabling AI to genuinely advance human knowledge rather than merely automating pattern recognition.

---

**Word Count:** ~2,000 words