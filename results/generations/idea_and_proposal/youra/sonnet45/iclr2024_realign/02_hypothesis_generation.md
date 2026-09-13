# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** Round 1 - Causal Dissection of Representational Alignment and Computational Mechanisms
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-2024-ALIGN-CAUSAL-001
**Confidence Level:** 0.85 (FEASIBLE)

**Main Hypothesis:**
Representational alignment (measured by CKA similarity to a reference system) and computational mechanism properties (measured by attention entropy and mutual information flow) are dissociable neural network properties. Systematically manipulating alignment strength via REPA-style intervention training (alignment loss weight λ ∈ {0, 0.5, 1.0}) while controlling task accuracy (±5%) will reveal the causal relationship: either (1) alignment changes drive computational mechanism changes (causal hypothesis), or (2) alignment increases without affecting computational flow patterns (epiphenomenal hypothesis).

**Alternative Hypothesis (H0):**
Representational alignment and computational mechanisms are intrinsically coupled properties. Any manipulation of alignment strength will either (a) simultaneously change computational mechanisms through shared underlying parameters, making independent measurement impossible, or (b) fail to change alignment without also changing task performance beyond ±5% tolerance, making controlled causal inference infeasible.

### 1.2 Variables

| Variable Type | Variable Name | Operationalization | Measurement Method | Range/Values |
|---------------|---------------|-------------------|-------------------|--------------|
| **Independent** | Alignment Intervention Strength (λ) | REPA loss weight in L_total = (1-λ)L_task + λL_align | Training hyperparameter | {0, 0.5, 1.0} |
| **Dependent** | Representational Alignment | CKA similarity between model layer L and reference system | Linear CKA with RBF kernel | [0, 1] continuous |
| **Dependent** | Attention Entropy | Shannon entropy H(A) over attention weights per head | -Σ(a_ij × log(a_ij)) | [0, log(seq_len)] |
| **Dependent** | Attention Flow Concentration | Gini coefficient over attention weight distribution | 1 - Σ((2i-n-1)×a_i)/(n×Σa_i) | [0, 1] |
| **Dependent** | Mutual Information I(X;T) | MI between input X and layer T representations | MINE estimator (neural network) | [0, ∞) bits |
| **Dependent** | Mutual Information I(T;Y) | MI between layer T and output Y | MINE estimator | [0, log(num_classes)] |
| **Controlled** | Task Accuracy | ImageNet-1K top-1 classification accuracy | Standard evaluation | Target: 76±4% (±5% tolerance) |
| **Controlled** | Architecture | Vision Transformer variant | Model specification | ViT-B/16 (86M params) |
| **Controlled** | Dataset | Training data distribution | ImageNet-1K (1.28M images, 1000 classes) | Fixed |
| **Controlled** | OOD Robustness | Out-of-distribution generalization | ImageNet-V2 top-1 accuracy | Measured, not controlled |

### 1.3 Causal Mechanism

**Proposed Causal Chain:**

```
Alignment Intervention (λ)
    → Alignment Loss Gradient Signal During Training
        → Layer Representation Geometry Changes (measured by CKA)
            ↓
    [HYPOTHESIZED CAUSAL LINK - TO BE TESTED]
            ↓
        → Computational Flow Pattern Changes
            ├─→ Attention Mechanism Adjustments (entropy, concentration)
            └─→ Information Bottleneck Characteristics (I(X;T), I(T;Y))
                ↓
            [IF CAUSAL]
                → Downstream Task Behavior Changes (controlled at ±5%)

            [IF EPIPHENOMENAL]
                → No Computational Flow Changes (alignment ⊥ computation)
```

**Evidence for Causal Links:**

1. **λ → Alignment (CKA):** Established by REPA (ICLR'25, sihyun-yu/REPA)
   - Evidence: REPA demonstrates training with alignment loss successfully increases representation similarity to reference
   - Strength: Strong (1000+ GitHub stars, peer-reviewed)

2. **Alignment → Computational Mechanism:** **UNKNOWN - Primary Research Question**
   - Current Evidence: Correlational only (Khosla et al. 2024 shows aligned axes correlate with reduced wiring costs)
   - Gap: No interventional studies manipulating alignment to measure computational effects
   - This Study's Contribution: Tests this link directly via dual measurement

3. **Computational Mechanism → Task Behavior:** Partial evidence
   - Evidence: Information Bottleneck theory (Tishby et al.) shows I(X;T), I(T;Y) relate to generalization
   - Evidence: Attention analysis literature shows entropy correlates with model performance
   - Strength: Medium (theoretical grounding + correlational empirical support)

**Key Tension:**
The central scientific question is whether the CKA → Computational Flow link exists. Neuroscience precedent (Damatac et al. 2024) shows neural synchrony (analog: alignment) and functional connectivity (analog: computational flow) can dissociate in biological systems, suggesting dissociability is possible. However, artificial neural networks may differ fundamentally due to end-to-end gradient-based optimization coupling all properties.

### 1.4 Key Assumptions

1. **REPA Intervention Validity**
   - Assumption: REPA-style alignment intervention (λ-weighted loss) successfully manipulates representational alignment across the tested range {0, 0.5, 1.0}
   - Justification: Demonstrated for diffusion models (ICLR'25), expected to transfer to discriminative ViT training
   - Testability: Verify CKA increases monotonically with λ in validation pilot
   - Risk: If REPA fails for ViT, alternative intervention needed (e.g., contrastive alignment loss)

2. **CKA Measurement Validity**
   - Assumption: Linear CKA with RBF kernel accurately captures representational alignment between ViT layers and reference system
   - Justification: CKA standard for neural network comparison (311★ implementation, widely cited)
   - Known Limitation: Murphy et al. (2024) shows CKA biased in low-data high-dim regime → use debiased estimator
   - Testability: Validation pilot compares biased vs debiased CKA; use appropriate variant

3. **Computational Flow Metrics Validity** ⚠️ **CRITICAL ASSUMPTION**
   - Assumption: Attention entropy + Gini coefficient + mutual information I(X;T), I(T;Y) reflect meaningful computational mechanism differences
   - Justification: Attention analysis established in interpretability literature; MI grounded in Information Bottleneck theory
   - Risk Mitigation: **Validation pilot** tests whether these metrics differ between known computational strategy variants (ViT vs CNN on same task)
   - Testability: If pilot shows metrics invariant across known strategy differences, hypothesis requires metric revision

4. **Accuracy Control Feasibility**
   - Assumption: Task accuracy can be held within ±5% range across alignment conditions (λ: 0, 0.5, 1.0) via hyperparameter adjustment
   - Justification: Standard experimental control in ML research; relaxed from ±2% to ±5% for feasibility
   - Risk: If accuracy control fails, alignment and performance confounded, preventing causal claims
   - Mitigation: Early stopping, learning rate adjustment, longer training for lower-performing conditions

5. **ViT Generalizability**
   - Assumption: Findings for Vision Transformers on image classification provide insight into broader alignment-computation relationship
   - Scope Limitation: Explicitly does NOT assume findings transfer to CNNs, RNNs, language models, or RL without separate validation
   - Justification: ViT represents modern Transformer architecture; ImageNet represents production-scale vision task
   - Acknowledged Limitation: Architecture-specific findings require follow-up studies for generalization claims

### 1.5 Scope & Boundaries

**APPLIES TO:**
- **Architecture:** Vision Transformers (specifically ViT-B/16 with 12 layers, 86M parameters)
- **Task Domain:** Image classification (supervised learning with cross-entropy loss)
- **Data Distribution:** Natural images (ImageNet-1K training, ImageNet-V2 OOD testing)
- **Scale:** Production-scale models and datasets (86M params, 1.28M training images)
- **Measurement:** Representation-level alignment and computational flow during inference (post-training)

**DOES NOT APPLY TO:**
- **Other Architectures:** CNNs, RNNs, MLPs, Graph Neural Networks (require separate studies)
- **Other Modalities:** Language (text), audio, multimodal, reinforcement learning
- **Training Dynamics:** Does NOT study alignment/computational changes during training process itself
- **Biological Systems:** Does NOT claim findings directly transfer to brain function without validation
- **Causal Interventions Post-Training:** Does NOT test runtime alignment manipulation (only training-time intervention)

**KNOWN LIMITATIONS:**
1. **Proxy Metrics:** Attention entropy and mutual information are computational proxies for "computational strategy" - true ground truth strategy is conceptual, not directly measurable
2. **Reference System Dependency:** Alignment measurement (CKA) requires choosing reference system (human fMRI or pre-aligned DNN) - choice affects interpretation
3. **Single Layer Analysis:** Initial study focuses on layer L (e.g., layer 6 or 9) for tractability - full layer-wise analysis deferred
4. **Finite Sample:** 3 random seeds per condition provides variance estimates but limited statistical power for small effects
5. **Accuracy Tolerance:** ±5% range allows some performance variation - may introduce minor confound between alignment and capability

### 1.6 Testable Predictions

**Primary Prediction (Causal Hypothesis - H1):**

IF representational alignment causally affects computational mechanisms, THEN:
- As λ increases from 0 → 0.5 → 1.0:
  - CKA similarity INCREASES (validation of intervention)
  - **AND** Attention entropy changes systematically (e.g., decreases if alignment promotes focused attention)
  - **AND** Attention Gini coefficient changes systematically (e.g., increases if alignment concentrates attention)
  - **AND** I(X;T) changes (e.g., decreases if alignment compresses representations)
  - **AND** I(T;Y) changes (e.g., maintained if alignment preserves task-relevant information)

**Quantitative Criterion:** At least 2 of 4 computational metrics show statistically significant monotonic relationship with λ (p < 0.05, controlling for accuracy), with effect size Cohen's d > 0.5 between λ=0 and λ=1.0 conditions.

**Secondary Prediction 1 (Epiphenomenal Hypothesis - H0):**

IF representational alignment is epiphenomenal (not causally affecting computation), THEN:
- As λ increases from 0 → 0.5 → 1.0:
  - CKA similarity INCREASES (intervention works)
  - **BUT** All computational flow metrics remain statistically invariant (p > 0.05)
  - **OR** Changes are non-monotonic and inconsistent across seeds (no systematic pattern)

**Quantitative Criterion:** All 4 computational metrics show p > 0.05 for ANOVA across λ conditions after controlling for accuracy, OR effect sizes Cohen's d < 0.2 for all metrics.

**Secondary Prediction 2 (Failure Mode Differentiation):**

IF alignment affects computational mechanisms, THEN failure modes will differ across alignment conditions:
- ImageNet-V2 (OOD) error patterns will show different misclassification distributions across λ values
- Higher alignment (λ=1.0) may show either:
  - **Better OOD generalization:** If alignment promotes robust features
  - **Worse OOD generalization:** If alignment overfits to reference system's biases

**Quantitative Criterion:** ImageNet-V2 top-1 accuracy differs by >2% between λ=0 and λ=1.0, OR error pattern analysis (confusion matrix similarity) shows Frobenius distance > threshold.

**Falsification Criteria:**

The hypothesis is **FALSIFIED** if:
1. **Intervention Failure:** CKA does not increase monotonically with λ (REPA doesn't work for ViT)
2. **Measurement Invalidity:** Validation pilot shows computational metrics (attention entropy, MI) do NOT differ between ViT and CNN (metrics don't capture computational differences)
3. **Accuracy Control Failure:** Cannot achieve ±5% accuracy tolerance across conditions despite hyperparameter tuning (confound cannot be controlled)
4. **Null Result with High Power:** All computational metrics show p > 0.05 AND post-hoc power analysis confirms >80% power to detect medium effects (true null, not underpowered study)

### 1.7 SOTA Baseline (Comparison Mode)

**Baseline Condition:** λ=0 (No Alignment Pressure)

This condition represents standard ViT-B/16 training on ImageNet-1K without representational alignment intervention. It serves as:
1. **Performance Baseline:** Expected ~76% ImageNet-1K top-1 accuracy (ViT-B/16 standard performance)
2. **Computational Mechanism Baseline:** Natural computational flow patterns emerging from task-only optimization
3. **Alignment Baseline:** Incidental alignment level achieved without explicit alignment objective

**Comparison Framework:**

| Aspect | λ=0 (Baseline) | λ=0.5 (Moderate Alignment) | λ=1.0 (Maximum Alignment) | Comparison Metric |
|--------|----------------|---------------------------|--------------------------|-------------------|
| **Task Performance** | ~76% | 76±4% (controlled) | 76±4% (controlled) | Top-1 accuracy |
| **Alignment** | Low (incidental) | Medium | High | CKA to reference |
| **Attention Entropy** | Natural baseline | Δ from baseline | Δ from baseline | Absolute entropy + Δ |
| **Attention Concentration** | Natural baseline | Δ from baseline | Δ from baseline | Gini coefficient + Δ |
| **I(X;T)** | Natural baseline | Δ from baseline | Δ from baseline | MINE estimate (bits) + Δ |
| **I(T;Y)** | Natural baseline | Δ from baseline | Δ from baseline | MINE estimate (bits) + Δ |
| **OOD Robustness** | Baseline V2 acc | V2 accuracy | V2 accuracy | ImageNet-V2 top-1 |

**SOTA Reference Points:**
- ViT-B/16 ImageNet-1K: 79.9% (original paper, Dosovitskiy et al. 2021) - our target is 76±4% to allow for alignment intervention effects
- CKA alignment studies: No established SOTA for alignment-computation causality (novel research question)
- This study establishes first baseline for causal alignment-computation research

### 1.8 Statistical Verification Design

**Experimental Design:** 3×3 Factorial with Controlled Confound
- **Factor 1:** Alignment Intervention (λ ∈ {0, 0.5, 1.0})
- **Factor 2:** Random Seed (3 independent training runs per condition)
- **Controlled Confound:** Task Accuracy (±5% tolerance via early stopping/hyperparameter adjustment)

**Sample Size:**
- Total Models: 9 (3 alignment conditions × 3 seeds)
- Measurements per Model: 4 computational metrics (attention entropy, Gini, I(X;T), I(T;Y)) + 1 alignment metric (CKA)
- ImageNet-1K Evaluation: 50,000 validation images per model
- ImageNet-V2 OOD: 10,000 test images per model

**Statistical Tests:**

1. **Primary Analysis (Causal Effect Test):**
   - **Method:** Mixed-effects ANOVA with accuracy as covariate
   - **Model:** ComputationalMetric ~ λ + Accuracy + (1|Seed)
   - **Hypothesis Test:** F-test for λ main effect (p < 0.05)
   - **Effect Size:** Partial η² for λ effect (medium effect threshold: η² > 0.06)
   - **Post-hoc:** Tukey HSD for pairwise comparisons (λ=0 vs 0.5, 0 vs 1.0, 0.5 vs 1.0)

2. **Monotonicity Test (Dose-Response):**
   - **Method:** Jonckheere-Terpstra trend test
   - **Hypothesis:** Ordered alternative H1: μ(λ=0) < μ(λ=0.5) < μ(λ=1.0) OR reversed ordering
   - **Significance:** p < 0.05 indicates systematic monotonic relationship

3. **Validation Pilot Analysis:**
   - **Comparison:** ViT vs CNN computational metrics on same ImageNet task
   - **Method:** Independent samples t-test for each metric
   - **Criterion:** At least 2 of 4 metrics show significant difference (p < 0.05, Cohen's d > 0.5)
   - **Interpretation:** If criterion met, metrics validated; otherwise, revise metric selection

4. **Accuracy Control Verification:**
   - **Method:** ANOVA testing accuracy differences across λ conditions
   - **Null Hypothesis:** No accuracy difference (H0: μ_acc(λ=0) = μ_acc(λ=0.5) = μ_acc(λ=1.0))
   - **Criterion:** Non-significant result (p > 0.05) confirms successful control
   - **Tolerance Check:** All conditions within 76±4% range

5. **Failure Mode Analysis:**
   - **Method:** Chi-square test for error pattern distribution differences
   - **Data:** Confusion matrix for top-5 most confused classes per condition
   - **Metric:** Frobenius norm distance between confusion matrices
   - **Significance:** Bootstrap resampling (1000 iterations) to estimate p-value

**Multiple Comparison Correction:**
- **Issue:** Testing 4 computational metrics increases Type I error rate
- **Correction:** Benjamini-Hochberg FDR correction at q = 0.05
- **Rationale:** Controls false discovery rate while maintaining power (less conservative than Bonferroni)

**Power Analysis:**
- **Assumed Effect Size:** Cohen's d = 0.6 (medium-large, based on pilot expectations)
- **Significance Level:** α = 0.05 (two-tailed)
- **Sample Size:** n = 3 seeds per condition (9 total)
- **Power:** ~0.65 for detecting medium effects (limited by computational cost)
- **Mitigation:** If pilot shows larger effects (d > 0.8), power exceeds 0.80; if smaller effects, acknowledge as limitation

**Robustness Checks:**
1. **Non-parametric Alternative:** Kruskal-Wallis H-test if normality assumptions violated
2. **Outlier Sensitivity:** Report results with/without outlier removal (>3 SD from mean)
3. **Accuracy Covariate:** Test both with and without accuracy covariate to assess sensitivity

---

## 2. Contribution Summary

This hypothesis makes three distinct contributions to representational alignment research:

### 2.1 Theoretical Contribution

**Resolves Fundamental Causality Question in Alignment Research**

Current alignment research demonstrates correlations between representational alignment and various beneficial properties (generalization, wiring efficiency, teaching effectiveness), but the causal direction remains unclear. This study directly tests whether alignment is a **causal driver** of computational differences or merely an **epiphenomenal byproduct** of shared optimization objectives.

**Novel Theoretical Framework:** Introduces neuroscience-inspired dual-measurement paradigm separating alignment measurement (CKA - "what representations look like") from computational mechanism measurement (attention/MI - "how information flows"). This separation, analogous to neural synchrony vs functional connectivity in brain research, enables causal inference about the alignment → computation relationship.

**Theoretical Impact:**
- If CAUSAL: Alignment becomes actionable optimization target for steering neural network computation toward desired behaviors
- If EPIPHENOMENAL: Alignment is diagnostic indicator but not intervention lever; alternative targets needed for computational control
- Either outcome advances theoretical understanding of what alignment represents in artificial neural networks

**Fills Gap 2:** Directly addresses "Mechanistic Understanding of Alignment-to-Computation Relationship" identified in Phase 1 research gaps.

### 2.2 Methodological Contribution

**First Interventional Study with Dual Measurement for Alignment-Computation Causality**

Existing work either (1) measures alignment without computational analysis (RSA/CKA studies), (2) analyzes computational properties without alignment measurement (interpretability research), or (3) observes correlations without intervention (Khosla et al. 2024, Mahner et al. 2024). This study uniquely combines all three elements:

1. **Controlled Intervention:** REPA-style alignment manipulation (λ parameter)
2. **Dual Measurement:** Simultaneous alignment (CKA) + computational flow (attention entropy, MI) tracking
3. **Causal Design:** Accuracy control (±5%) isolates alignment effect from performance confounds

**Methodological Innovation:**
- **Cross-Domain Transfer:** Applies neuroscience's dual-measurement paradigm (Damatac et al. 2024) to deep learning research for the first time
- **Metric Validation:** Introduces validation pilot protocol to verify computational metrics capture strategy differences before main study
- **Modular Framework:** Alignment intervention + computational profiling components can be reused for future studies across architectures

**Practical Toolkit:** Produces reusable experimental protocol applicable to future alignment-computation studies in vision, language, and multimodal domains (with architecture-specific adaptations).

**Fills Gap 1 (Partial):** Contributes to "Unified Benchmark" by providing first controlled comparison of alignment's computational effects, establishing baseline for future metric comparisons.

### 2.3 Practical Contribution

**Informs AI Safety and Alignment Intervention Design**

Understanding whether representational alignment causally affects computation has immediate implications for:

1. **AI Safety Strategy:** If alignment drives computation, strengthening alignment with human cognitive representations becomes viable path to behavioral alignment; if not, alternative intervention targets must be identified

2. **Representation Engineering:** Determines whether alignment-based steering (e.g., REPA, contrastive methods) should be prioritized for controlling model behavior vs. direct computational mechanism interventions

3. **Interpretability Methods:** Clarifies what CKA/RSA measurements reveal - if alignment ⊥ computation, high alignment doesn't guarantee similar computational strategies, affecting model comparison interpretations

**Decision Support:** Provides empirical evidence for practitioners choosing between alignment-based vs. computation-based intervention strategies for neural network control.

**Failure Mode Analysis:** ImageNet-V2 OOD testing reveals whether alignment-driven training affects robustness and generalization - critical for deployment decisions.

**Extension Path:** Validated methodology enables systematic testing of alignment interventions across safety-critical applications (value alignment, robustness, fairness), directly supporting AI safety research goals identified in Phase 0 workshop context.

---

## 3. Key Related Work

### 3.1 Direct Precursors (Foundational Papers)

**1. Sucholutsky et al. (2023) - "Getting aligned on representational alignment"**
- Semantic Scholar ID: eeefe82172135523517cbe19624f2fab54e4a846
- Citations: 138
- **Role:** Establishes unified framework for representational alignment research across cognitive science, neuroscience, and ML
- **Contribution to This Study:** Identifies alignment-computation relationship as open problem; motivates causal investigation
- **Relationship:** Our study operationalizes their theoretical framework by testing specific causal hypothesis

**2. Kornblith et al. (2019) - "Similarity of Neural Network Representations Revisited"**
- Widely cited (implemented in yuanli2333/CKA, 311★)
- **Role:** Introduces CKA as superior alignment metric for neural networks (invariant to orthogonal transformations)
- **Contribution to This Study:** Provides alignment measurement methodology (CKA with RBF kernel)
- **Relationship:** We apply CKA as dependent variable to measure alignment changes induced by REPA intervention

**3. Murphy et al. (2024) - "Correcting Biased Centered Kernel Alignment Measures"**
- Semantic Scholar ID: 9d7635db800929e947b8dbbf7ea00b1e33dfcc95
- Citations: 9
- **Role:** Identifies bias in CKA for biological-artificial alignment in low-data high-dim regime
- **Contribution to This Study:** Alerts to measurement validity concerns; informs decision to use debiased CKA estimator
- **Relationship:** We incorporate methodological refinements to ensure valid alignment measurement

### 3.2 Alignment-Performance Correlation Studies (Evidence Base)

**4. Khosla et al. (2024) - "Privileged representational axes in biological and artificial neural networks"**
- Semantic Scholar ID: 2c94df00ee8e812f76d1b12b89f5c29c851656b2
- Citations: 16
- **Finding:** Aligned representational axes correlate with reduced wiring costs and better generalization
- **Contribution to This Study:** Demonstrates alignment-performance correlation that motivates causal investigation
- **Limitation We Address:** Correlation ≠ causation; our intervention design tests causal direction

**5. Mahner et al. (2024) - "Dimensions underlying representational alignment of DNNs with humans"**
- Semantic Scholar ID: 151c7cb38793179d444712253a8d5c23f8717830
- Citations: 28
- **Finding:** Humans and DNNs achieve similar task performance via different representational strategies (visual vs semantic dominance)
- **Contribution to This Study:** Demonstrates dissociation between alignment and computational strategy; motivates dual measurement
- **Relationship:** Our attention/MI metrics aim to capture the "strategy differences" they observed

### 3.3 Alignment Intervention Methods (Technique Sources)

**6. sihyun-yu/REPA (ICLR 2025 Oral) - Representation alignment for diffusion models**
- GitHub: https://github.com/sihyun-yu/REPA
- Stars: 1000+
- **Method:** Trains models with L_total = (1-λ)L_task + λL_align to control alignment strength
- **Contribution to This Study:** Provides alignment intervention methodology adapted for ViT discriminative training
- **Adaptation:** We transfer REPA's loss formulation from generative (diffusion) to discriminative (classification) context

**7. Sucholutsky et al. (2024) - "Representational Alignment Supports Effective Machine Teaching"**
- Semantic Scholar ID: bc5edab352cfdc6654e292c03ff7bb3c27a407d6
- Citations: 5
- **Method:** GRADE-Match intervention improves alignment in teaching contexts
- **Finding:** Higher alignment → better learning outcomes (behavioral benefit)
- **Contribution to This Study:** Demonstrates feasibility of alignment intervention; provides complementary evidence for alignment's importance
- **Limitation We Address:** GRADE-Match is task-specific (teaching); we test general alignment intervention

### 3.4 Cross-Domain Inspiration (Neuroscience Transfer)

**8. Damatac et al. (2024) - "Sensory processing sensitivity is associated with neural synchrony and functional connectivity during threatening movies"**
- BioRxiv preprint: 2024.03.27.586963
- **Finding:** Neural synchrony (inter-subject similarity) and functional connectivity (information flow) dissociate in brain
- **Contribution to This Study:** Provides biological precedent for dual-measurement paradigm
- **Analogical Mapping:**
  - Neural synchrony (neuroscience) ↔ Representational Alignment/CKA (DL)
  - Functional connectivity (neuroscience) ↔ Computational Flow/Attention+MI (DL)
- **Methodological Transfer:** Inspired separation of "alignment measurement" from "mechanism measurement"

### 3.5 Computational Mechanism Measurement (Metric Sources)

**9. Tishby & Zaslavsky (2015) - "Deep Learning and the Information Bottleneck Principle"**
- **Theory:** Information Bottleneck characterizes optimal compression: maximize I(T;Y) while minimizing I(X;T)
- **Contribution to This Study:** Theoretical grounding for mutual information metrics as computational mechanism indicators
- **Application:** We measure I(X;T) and I(T;Y) to characterize information flow changes under alignment intervention

**10. Vaswani et al. (2017) - "Attention is All You Need" + Attention Analysis Literature**
- **Foundation:** Transformer attention mechanisms
- **Analysis Methods:** Attention entropy and Gini coefficient for measuring attention distribution
- **Contribution to This Study:** Provides established metrics for analyzing computational flow in ViT architecture
- **Implementation:** We track attention entropy and concentration as computational mechanism proxies

### 3.6 Methodological Alignment Studies

**11. Ogg et al. (2024) - "A Flexible Method for Behaviorally Measuring Alignment"**
- Semantic Scholar ID: 2c510068273b5e9b5448d0079289f62ad259b079
- Citations: 3
- **Method:** Adapted RSA for human-AI alignment using behavioral similarity ratings
- **Contribution to This Study:** Demonstrates alternative alignment measurement approach (behavioral vs neural)
- **Complementarity:** Our neural/computational focus complements their behavioral approach

**12. rsatoolbox (rsagroup/rsatoolbox, 232★) - RSA Standard Implementation**
- **Role:** Provides established RSA pipeline for representational similarity analysis
- **Contribution to This Study:** Alternative alignment metric for comparison (if CKA limitations arise)
- **Design Choice:** We selected CKA over RSA due to invariance properties better suited for neural network layers

### 3.7 Positioning in Literature

**Research Lineage:**
```
Representational Similarity (Kriegeskorte 2008)
    ↓
CKA for Neural Networks (Kornblith 2019)
    ↓
Unified Alignment Framework (Sucholutsky et al. 2023) ← Reference Paper
    ↓
├─→ Measurement Methods Branch
│   ├─ Debiased CKA (Murphy et al. 2024)
│   └─ Behavioral RSA (Ogg et al. 2024)
│
├─→ Alignment-Performance Correlation Branch
│   ├─ Privileged Axes (Khosla et al. 2024)
│   └─ DNN-Human Dimensions (Mahner et al. 2024)
│
└─→ Intervention Methods Branch
    ├─ REPA (sihyun-yu, ICLR 2025)
    └─ Machine Teaching (Sucholutsky et al. 2024)
        ↓
    [THIS STUDY: Causal Intervention + Dual Measurement]
```

**Key Differentiation:** First work integrating intervention (REPA), dual measurement (alignment + computational flow), and causal design (controlled accuracy) to test alignment → computation causality.

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence): Does REPA-style intervention successfully manipulate alignment in discriminative ViT models?**

**Test:** Train ViT-B/16 with three alignment conditions (λ = 0, 0.5, 1.0) and measure CKA similarity to reference system.

**Success Criterion:** CKA increases monotonically with λ (CKA(λ=0) < CKA(λ=0.5) < CKA(λ=1.0), p < 0.05, Jonckheere-Terpstra trend test)

**Verification Method:**
- Metric: Linear CKA with RBF kernel between ViT layer L and reference system
- Reference System: Either (a) human fMRI representations from Algonauts dataset, or (b) pre-trained ViT aligned to brain data
- Statistical Test: ANOVA + post-hoc Tukey HSD for pairwise comparisons
- Expected Outcome: If REPA works for ViT (as it does for diffusion models), CKA will increase with λ

**Contingency:** If SH1 fails (CKA does not increase with λ), hypothesis is falsified at existence level - REPA intervention ineffective for discriminative ViT training, requiring alternative intervention method.

---

**SH2 (Mechanism): Do computational flow metrics (attention entropy, MI) validly capture computational mechanism differences?**

**Test:** Validation pilot comparing ViT vs CNN computational metrics on identical ImageNet classification task.

**Success Criterion:** At least 2 of 4 metrics show significant difference (p < 0.05, Cohen's d > 0.5) between ViT and CNN, indicating metrics capture architecture-specific computational strategies.

**Verification Method:**
- Models: ViT-B/16 vs ResNet-50 (similar parameter count, same task)
- Metrics: Attention entropy (ViT self-attention) vs proxy for CNN, Gini coefficient, I(X;T), I(T;Y)
- Statistical Test: Independent samples t-test for each metric
- Expected Outcome: Metrics should differ because ViT (self-attention) and CNN (convolution) use fundamentally different computational mechanisms

**Contingency:** If SH2 fails (metrics invariant across architectures), computational flow metrics do NOT capture computational strategy differences - require alternative metrics (e.g., gradient flow, layer activation patterns) or hypothesis revision.

---

**SH3 (Comparison): Does alignment change causally affect computational mechanisms, or are they independent?**

**Test:** After validating SH1 (intervention works) and SH2 (metrics work), test whether alignment manipulation (λ) systematically changes computational metrics beyond accuracy effects.

**Success Criterion - Causal (H1):** At least 2 of 4 computational metrics show significant monotonic relationship with λ (p < 0.05 after FDR correction, Cohen's d > 0.5), controlling for accuracy.

**Success Criterion - Epiphenomenal (H0):** All computational metrics show p > 0.05 OR effect sizes d < 0.2 across λ conditions.

**Verification Method:**
- Statistical Model: Mixed-effects ANOVA with ComputationalMetric ~ λ + Accuracy + (1|Seed)
- Primary Test: F-test for λ main effect
- Effect Size: Partial η² (medium threshold: η² > 0.06)
- Multiple Comparisons: Benjamini-Hochberg FDR correction at q = 0.05

**Interpretation Framework:**
- If H1 supported: Alignment causally determines computational mechanisms → alignment is actionable intervention lever
- If H0 supported: Alignment and computation are dissociable → alignment is diagnostic but not causal driver

**Contingency:** If results are mixed (1 metric significant, 3 not), interpret as weak causal effect requiring larger sample size or refined metrics for conclusive evidence.

---

### Readiness Checklist

- [x] **Hypothesis statement is testable:** Clear predictions (H1 vs H0), quantitative criteria, falsification conditions specified
- [x] **Variables operationalized:** All IV/DV/controls have explicit measurement methods and ranges
- [x] **Causal mechanism explicit:** Proposed causal chain from λ → alignment → computation with evidence assessment for each link
- [x] **Assumptions documented:** 5 key assumptions identified with justifications, testability, and risk mitigation
- [x] **Scope clearly bounded:** Applies to/does not apply to sections prevent overgeneralization
- [x] **Statistical design specified:** Sample size, tests, power analysis, multiple comparison correction detailed
- [x] **Validation pilot planned:** SH2 includes metric validation before main study to de-risk critical assumption #3
- [x] **Baseline comparison defined:** λ=0 serves as no-intervention baseline for all comparisons
- [x] **Related work mapped:** 12 key papers with semantic scholar IDs, clear relationship to this study
- [x] **Sub-hypothesis structure:** SH1 (existence), SH2 (mechanism validity), SH3 (causal comparison) form logical progression
- [x] **Contingency plans:** Each sub-hypothesis includes failure contingency (what to do if SH fails)
- [x] **Contribution clarity:** Theoretical, methodological, practical contributions explicitly differentiated
- [x] **Phase 1 gaps addressed:** Directly tackles Gap 2 (mechanistic understanding), partially addresses Gap 1 (benchmark)
- [x] **Archon-compatible:** Hypothesis structured for Phase 2B decomposition into Archon tasks

**READY FOR PHASE 2B:** All criteria met. Hypothesis is scientifically rigorous, falsifiable, and structured for systematic verification planning.

---

### Open Questions

**Q1: Reference System Selection for CKA Alignment**
- **Question:** Should alignment target be human fMRI representations (biological gold standard) or pre-trained DNN aligned to brain data (computational convenience)?
- **Trade-offs:**
  - Human fMRI: Stronger biological grounding, but requires Algonauts dataset access and fMRI-to-layer mapping
  - Aligned DNN: Easier implementation, but introduces assumption that pre-trained alignment is valid
- **Resolution Path:** Phase 2B should specify reference system and justify choice based on research goals

**Q2: Layer Selection for Analysis**
- **Question:** Which ViT layer(s) should be analyzed? Early (layer 3-4), middle (layer 6-7), or late (layer 10-11)?
- **Consideration:** Different layers represent different abstraction levels; alignment effects may be layer-specific
- **Resolution Path:** Pilot study could test all layers, then select 1-2 representative layers for main study to balance coverage and tractability

**Q3: Attention Metric Adaptation**
- **Question:** How to compute "attention entropy" equivalent for CNN baseline in validation pilot (SH2)?
- **Challenge:** CNNs lack self-attention mechanism
- **Options:**
  - Use activation pattern entropy as proxy
  - Compare ViT attention metrics to CNN gradient flow metrics (different but complementary)
  - Acknowledge limitation: SH2 validation limited to ViT-to-ViT comparisons
- **Resolution Path:** Phase 2B experimental design should specify CNN metric adaptation or scope limitation

**Q4: Accuracy Control Mechanism**
- **Question:** What specific hyperparameter adjustments will maintain ±5% accuracy across λ conditions?
- **Candidates:** Learning rate, training epochs, weight decay, early stopping threshold
- **Concern:** Too many adjustments may introduce confounds
- **Resolution Path:** Phase 2B should specify single primary control knob (e.g., early stopping) and document all adjustments

**Q5: MINE Estimator Implementation**
- **Question:** Which MINE (Mutual Information Neural Estimation) variant to use for I(X;T) and I(T;Y)?
- **Options:** MINE-f, MINE-DV, NWJ estimator (different bias-variance trade-offs)
- **Consideration:** High-dimensional X (ImageNet images) may require specific estimator variant
- **Resolution Path:** Phase 2B should specify MINE variant and hyperparameters (network architecture, training steps)

**Q6: Sample Size and Power**
- **Question:** Is n=3 seeds per condition sufficient for detecting medium effects (d=0.6)?
- **Current Power:** ~0.65 (underpowered for small effects)
- **Trade-off:** Each additional seed = 1 full ViT training run (~$800 compute cost)
- **Resolution Path:** Phase 2B should either (a) budget for n=5 seeds to increase power to 0.80, or (b) acknowledge limited power as scope constraint

**Q7: ImageNet-V2 Failure Mode Analysis**
- **Question:** What specific error pattern metrics will be used for failure mode analysis?
- **Candidates:** Confusion matrix Frobenius distance, top-K error overlap, calibration metrics (ECE)
- **Resolution Path:** Phase 2B should specify 2-3 primary failure mode metrics with justification

**Q8: Timeline and Compute Budget**
- **Question:** What is realistic timeline for validation pilot + main study?
- **Estimate:** Validation pilot (2 weeks), main study (6-8 weeks training + 2 weeks analysis)
- **Compute:** 9 model training runs + 2 pilot runs = ~$10K GPU budget (estimated)
- **Resolution Path:** Phase 2B should produce detailed resource plan with cost-benefit analysis

---

*Generated using YouRA Research Phase 2A Extended Workflow (YOLO Mode)*
*2026-02-06*
