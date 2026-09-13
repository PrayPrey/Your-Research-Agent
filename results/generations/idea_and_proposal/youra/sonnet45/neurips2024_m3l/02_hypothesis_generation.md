# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-neurips2024-m3l-r1
**Confidence Level:** 0.85 (HIGH)

**Main Hypothesis:**

IF neural network architectures are characterized by tractable implicit bias measures β(A,C) (computed via random projections for metric geometry + early-training gradient flow for implicit regularization), THEN they can be mapped to statistical physics universality classes, BECAUSE architectures with similar inductive bias profiles share scaling behavior patterns analogous to phase transition universality classes, ENABLING predictive emergence threshold formulation:

**T(C,A) = T₀(C) · β(A,C)^α(class(A))**

Where:
- T(C,A) = emergence threshold (compute/data) for capability C in architecture A
- T₀(C) = baseline capability-specific threshold
- β(A,C) = tractable capability-conditioned bias measure
- α(class(A)) = universality class scaling exponent

**Alternative Hypothesis (H₀):**

Emergence thresholds are architecture-independent (all architectures have similar thresholds for same capability), OR thresholds are architecture-specific but unpredictable from measurable properties (pure empiricism required), OR inductive bias measures do not correlate with scaling behavior (no universality class structure exists).

### 1.2 Variables

| Variable | Type | Operationalization | Measurement Method |
|----------|------|-------------------|-------------------|
| **Architecture type (A)** | Independent | Neural architecture family: Transformer variants (encoder-only, decoder-only, encoder-decoder), CNNs, GNNs, SSMs (Mamba), hybrid | Categorical classification by architectural primitives |
| **Implicit bias measure β(A,C)** | Independent | Capability-conditioned bias: (1) Random projection metric geometry O(n log n), (2) Early-training gradient flow implicit regularization, (3) Capability-specific indices | Computational: Random projections + gradient flow analysis at <1% training |
| **Capability type (C)** | Independent | Target emergent capability: in-context learning, few-shot reasoning, generation quality, translation, multi-modal understanding | Benchmark evaluation (MMLU, BIG-Bench, generation metrics) |
| **Model scale** | Independent | Parameter count (100M-100B+), training compute (FLOPs), data size (tokens) | Direct measurement during training |
| **Emergence threshold T(C,A)** | Dependent | Minimum compute/data for capability C manifestation in architecture A | Training FLOPs or token count where performance exceeds capability threshold |
| **Universality class α** | Dependent | Scaling exponent characterizing architecture family | Empirical fitting from 20-30 architectures per class, validated by bias clustering |
| **Training protocol** | Controlled | Optimizer (AdamW), LR schedule, batch size, initialization | Standardized across experiments |
| **Data distribution** | Controlled | Training dataset composition and quality | Fixed datasets across architecture comparisons |

### 1.3 Causal Mechanism

**Mechanism Chain:**

1. **Inductive Bias → Function Space Constraints**: Neural architectures impose implicit constraints on learnable function space through their structure (attention mechanisms favor token interactions, convolutions favor local patterns, recurrence favors sequential dependencies)

2. **Function Space → Early Training Dynamics**: These constraints manifest in early-training gradient flow patterns and metric geometry of learned representations, making bias tractably measurable via random projections (Johnson-Lindenstrauss) and gradient flow proxies

3. **Similar Biases → Universality Classes**: Architectures with similar bias measures β(A,C) belong to same universality class, sharing critical properties analogous to statistical physics phase transitions

4. **Universality Class → Predictable Scaling**: Within each class, emergence thresholds follow power-law T(C,A) = T₀(C) · β(A,C)^α with class-specific exponent α, enabling *a priori* prediction before full training

**Evidence for Causal Links:**

**Link 1 (Bias → Function Space):**
- Chen et al. (2025): Architecture-independent generalization bounds depend only on metric geometry of learned representations, confirming measurable bias existence
- Min et al. (2021): Initialization constrains gradient flow to invariant sets leading to min-norm solutions, proving structural constraints shape optimization

**Link 2 (Function Space → Measurability):**
- Johnson-Lindenstrauss lemma: Random projections preserve metric structure with O(log n) dimensions, making geometry tractable
- Arora et al. (2022): Edge of Stability analysis shows gradient flow dynamics are analyzable from early training

**Link 3 (Similar Biases → Classes):**
- Statistical physics universality: Systems with similar order parameters belong to same universality class despite microscopic differences (Wilson, Fisher)
- Yao et al. (2024): Encoder-only vs decoder-only Transformers exhibit different scaling profiles, suggesting architecture families exist

**Link 4 (Classes → Predictable Scaling):**
- Zhu et al. (2024): Empirical power-law formula T = T₀ · system_size^α successfully predicts GNN emergence thresholds
- Phase transition theory: Critical phenomena follow predictable power-laws with universal exponents within each class

**Key Tension:**

Neural networks lack continuous symmetries of statistical physics systems. Physical universality classes emerge from symmetry breaking and renormalization group fixed points with continuous phase transitions. Neural architectures have discrete structural differences and training is a non-equilibrium process. **Resolution**: Universality is approximate (not exact), validated empirically through clustering rather than derived from first principles. Coarse-grained classes (4-6) rather than fine-grained infinite classes.

### 1.4 Key Assumptions

1. **Bias Stability**: Inductive biases measured at initialization or early training (first 1% of steps) remain stable and predictive of late-training behavior
   - *Justification*: Min et al. show initialization constraints persist; Edge of Stability occurs early
   - *Risk*: Phase transitions during training could alter bias profiles
   - *Mitigation*: Monitor bias measures throughout training to detect instability

2. **Power-Law Scaling**: Emergence phenomena follow power-law T(C,A) = T₀(C) · β(A,C)^α
   - *Justification*: Zhu et al. validated for GNNs; widespread in scaling laws literature (Kaplan, Hoffmann)
   - *Risk*: Non-power-law regimes (saturation, multiple phases)
   - *Mitigation*: Test multiple functional forms; report goodness-of-fit

3. **Finite Universality Classes**: Discrete classes exist (hypothesis: 4-6 coarse families)
   - *Justification*: Architectural primitives (attention, convolution, recurrence) are countable
   - *Risk*: Continuous spectrum rather than discrete classes
   - *Mitigation*: Empirical clustering validation; accept soft boundaries

4. **Random Projection Preservation**: Metric structure preserved sufficiently for bias quantification
   - *Justification*: Johnson-Lindenstrauss lemma with formal guarantees
   - *Risk*: Loss of critical structure in projection
   - *Mitigation*: Validate projections preserve relevant geometry via reconstruction error

5. **Early-Late Training Correlation**: Early gradient flow proxies correlate with full-training implicit regularization
   - *Justification*: Arora et al. show EoS stabilizes early; implicit bias manifests from initialization
   - *Risk*: Late-training phenomena not captured
   - *Mitigation*: Empirical validation of early-late correlation across architectures

6. **Class Homogeneity**: Architectures with similar β exhibit similar α (within-class consistency)
   - *Justification*: Definition of universality class - shared exponents
   - *Risk*: High within-class variance
   - *Mitigation*: Report within-class standard deviation; refine class boundaries

### 1.5 Scope & Boundaries

**Applies To:**
- **Architectures**: Transformer variants (BERT-style encoder-only, GPT-style decoder-only, T5-style encoder-decoder), Convolutional networks, Graph neural networks, State space models (Mamba, S4), Hybrid architectures (ConvNeXT, CoAtNet)
- **Scales**: Overparametrized regimes (>1M parameters), foundation model scales (100M-100B+ parameters)
- **Capabilities**: In-context learning, few-shot reasoning, code generation, translation, multi-modal understanding (vision-language), long-context processing
- **Training Regimes**: Standard supervised pretraining, self-supervised learning, causal language modeling

**Does NOT Apply To:**
- **Toy Models**: Under-parameterized networks (<1M parameters), synthetic tasks without real emergence
- **Trivial Capabilities**: Tasks with no identifiable emergence threshold (linear scaling throughout)
- **Non-Standard Training**: Heavily engineered curricula, multi-stage training with architecture changes
- **Exotic Architectures**: Neuromorphic hardware, spiking networks, quantum neural networks (insufficient theory)

**Known Limitations:**
1. **Empirical Bootstrap Required**: 20-30 architectures per class needed for initial α fitting before predictive power
2. **Capability Taxonomy Evolution**: New capabilities may require new bias measures (framework extensible but not complete)
3. **Threshold Definition Sensitivity**: Capability "emergence" depends on chosen performance threshold (arbitrary but necessary)
4. **Compute Cost of Bias Measurement**: Even O(n log n) becomes expensive at trillion-token scales (but < full training cost)
5. **Cross-Domain Generalization Unknown**: Validated for language/vision models; unclear if applies to RL, continuous control, etc.

### 1.6 Testable Predictions

**Primary Prediction (P1):**

If two architectures A₁ and A₂ have similar bias measures β(A₁,C) ≈ β(A₂,C) (within 20% relative difference), then their emergence thresholds T(C,A₁) and T(C,A₂) will differ by less than 2× (50% relative difference) for capability C.

*Measurement*: Train A₁ and A₂ at multiple scales, measure T at performance threshold crossing, compute |T(C,A₁) - T(C,A₂)| / min(T(C,A₁), T(C,A₂))
*Success Criterion*: >70% of architecture pairs meeting β similarity exhibit <2× threshold difference

**Secondary Predictions:**

**P2 (Universality Class Prediction Accuracy):**
If architectures belong to same universality class (assigned by β clustering), then threshold prediction using T(C,A) = T₀(C) · β(A,C)^α(class) achieves <15% mean absolute percentage error (MAPE) across class members.

*Measurement*: Fit α per class, predict T for held-out architectures, compute MAPE
*Success Criterion*: MAPE < 15% for ≥3 classes with ≥5 architectures each

**P3 (Compute Savings):**
If threshold prediction is used for architecture selection (choosing A with lowest predicted T for target C), then compute savings are 5-10× compared to trial-and-error, reducing current O(10×) prediction error to O(2×).

*Measurement*: Compare total compute for threshold discovery via (a) exhaustive training vs (b) bias measurement + prediction
*Success Criterion*: ≥5× reduction in total FLOPs to identify architectures crossing threshold

**Falsification Criteria:**

The hypothesis is **FALSIFIED** if:
1. **No β-T Correlation**: Architectures with similar β exhibit uncorrelated T (Spearman ρ < 0.3)
2. **No Class Structure**: Bias measures do not cluster into discrete families (silhouette score < 0.3)
3. **Power-Law Failure**: Threshold data does not fit power-law (R² < 0.7) or requires non-power-law functions
4. **No Predictive Advantage**: Bias-based prediction has MAPE ≥30% (worse than 2× from random guessing in log-space)
5. **Early-Late Decorrelation**: Early training bias measures (1% steps) have ρ < 0.5 with late-training measures

### 1.7 SOTA Baseline

**Current State-of-the-Art:**

1. **Empirical Scaling Laws (Kaplan et al., Hoffmann et al., "Chinchilla")**
   - *Approach*: Fit power-laws L(N,D) = (N₀/N)^αₙ + (D₀/D)^αᴅ to training loss vs model size N and data size D
   - *Limitation*: Architecture-agnostic (fits per architecture family separately), no emergence threshold prediction, requires full training runs

2. **Domain-Specific Threshold Discovery (Zhu et al. 2024 - GNNs)**
   - *Approach*: Empirical power-law T = T₀ · system_size^α for GNN emergence in power systems
   - *Limitation*: Single architecture family, requires per-domain fitting, no cross-architecture prediction

3. **Neural Architecture Search (DARTS, NAS)**
   - *Approach*: Search over architectures to optimize task performance
   - *Limitation*: Expensive (requires training many candidates), no theoretical guidance, no threshold prediction

**Proposed Advantage Over SOTA:**

| Aspect | SOTA | This Hypothesis | Improvement |
|--------|------|-----------------|-------------|
| **Architecture Generality** | Per-family empirical fitting | Cross-architecture prediction via universality classes | Generalizes from 20-30 architectures to unlimited variants |
| **Training Cost** | Full training required | Bias measurement at <1% training + class lookup | 5-10× compute savings |
| **Threshold Prediction** | Post-hoc (after training) | *A priori* (before training) | Enables proactive architecture selection |
| **Theoretical Foundation** | Empirical curve-fitting | Grounded in implicit bias theory + statistical physics | Explanatory power + principled extrapolation |
| **Prediction Error** | O(10×) trial-and-error | O(2×) targeted prediction (MAPE <15%) | 5× error reduction |

**Benchmark Comparison:**
- Baseline: Trial-and-error architecture selection (test N architectures at multiple scales, total cost: N × K_train)
- Proposed: Bias measurement (N × K_bias, K_bias << K_train) + targeted training (M × K_train, M << N)
- Success if: (N × K_bias + M × K_train) < 0.2 × (N × K_train), i.e., 5× savings

### 1.8 Statistical Verification Design

**Experimental Design:**

**Phase 1 - Universality Class Discovery (Exploratory)**
- Sample: 30-40 diverse architectures across families (10 Transformers, 10 CNNs, 5 GNNs, 5 SSMs, 5 hybrids)
- Procedure: (1) Measure β(A,C) for 3-5 capabilities per architecture at initialization + 1% training, (2) Train to varying scales (100M, 1B, 10B params), (3) Record emergence thresholds T(C,A) for each capability
- Analysis: K-means clustering on β vectors to discover classes (silhouette score), fit power-law per class, report within-class α variance

**Phase 2 - Predictive Validation (Confirmatory)**
- Sample: 20 held-out architectures (5 per discovered class)
- Procedure: (1) Measure β, (2) Predict T using class-specific formula, (3) Train to validate, (4) Compare predicted vs actual T
- Analysis: MAPE, per-class accuracy, failure modes analysis

**Statistical Tests:**

1. **β-T Correlation**: Spearman rank correlation between β(A,C) and T(C,A) within capabilities. H₀: ρ = 0, H₁: ρ > 0.5. α = 0.01 (Bonferroni corrected for multiple capabilities).

2. **Class Structure**: Silhouette score for β clustering. H₀: score < 0.3 (weak structure), H₁: score ≥ 0.5 (clear structure).

3. **Power-Law Fit**: R² for T(C,A) = T₀(C) · β(A,C)^α regression (log-log space). H₀: R² < 0.7, H₁: R² ≥ 0.85.

4. **Prediction Accuracy**: MAPE for Phase 2 held-out set. H₀: MAPE ≥ 30%, H₁: MAPE < 15%. t-test against baseline random prediction.

5. **Early-Late Correlation**: Spearman ρ between β measured at 1% vs 100% training. H₀: ρ < 0.5, H₁: ρ ≥ 0.7.

**Sample Size Justification:**
- 30-40 architectures in Phase 1 provides 5-10 per class (assuming 4-6 classes), sufficient for initial power-law fitting (minimum 5 points per curve)
- 20 held-out architectures provides power 0.8 to detect MAPE difference of 15% with α = 0.05 (power analysis via bootstrap)

**Controls:**
- Architecture randomization to avoid confounding (e.g., Transformer bias from recent popularity)
- Fixed data distribution, training protocol, evaluation benchmarks
- Blinded threshold assessment (automated benchmark evaluation)

**Null Results Plan:**
- If no class structure (silhouette < 0.3): Report continuous bias spectrum, fit per-architecture regressions
- If power-law fails (R² < 0.7): Test alternative functions (log-linear, exponential saturation)
- If prediction accuracy insufficient (MAPE > 15%): Analyze failure modes, refine bias measures

---

## 2. Contribution Summary

### Theoretical Contribution

**Novel Framework**: First mathematical unification of implicit bias theory (generalization research), scaling law prediction (emergence research), and statistical physics universality classes into a coherent predictive framework for architecture-conditioned emergence thresholds.

**Key Innovation**: Treats measurable inductive biases as "order parameters" analogous to statistical physics phase transitions, enabling cross-architecture threshold prediction without per-architecture empirical fitting.

**Advancement Over Prior Work**:
- **vs Kaplan/Hoffmann scaling laws**: Moves from post-hoc architecture-specific curve-fitting to *a priori* cross-architecture prediction grounded in architectural properties
- **vs Zhu et al. emergence formulas**: Generalizes domain-specific (GNN) empirical laws to universal framework applicable across architecture families
- **vs Chen et al. architecture-independent bounds**: Leverages architecture dependence (bias measures) for *prediction* rather than proving independence for *generalization*

**Gap Resolution**: Directly addresses Gap 2 (Predictive Theory for Emergence Thresholds Across Model Families) by providing mathematical formalism and computational protocol for threshold prediction before expensive training.

### Methodological Contribution

**Tractable Bias Quantification Protocol**:
1. Random projection for metric geometry (O(n log n) via Johnson-Lindenstrauss)
2. Early-training gradient flow proxies (first 1% of training steps)
3. Capability-conditioned bias taxonomy (ICL: attention entropy, Reasoning: compositional structure, Generation: diversity measures)

**Universality Class Classification Algorithm**:
1. Measure β(A,C) for architecture-capability pairs
2. K-means clustering on β vectors with silhouette-score validation
3. Fit power-law exponent α per class via log-log regression
4. Cross-validate on held-out architectures

**Threshold Prediction Formula**: T(C,A) = T₀(C) · β(A,C)^α(class(A))
- Enables resource-efficient architecture selection (5-10× compute savings)
- Reduces prediction error from O(10×) to O(2×) vs trial-and-error

**Comparison to Baselines**:
- **vs NAS/DARTS**: Theory-guided search vs black-box optimization; 10× faster via bias measurement
- **vs Empirical scaling laws**: Cross-architecture prediction vs per-architecture fitting
- **vs Architecture search benchmarks**: Threshold-focused vs task-performance focused

### Practical Contribution

**Application**: Pre-training architecture selection tool for foundation model development

**Use Cases**:
1. **Resource-Constrained Research**: Predict which architectures will reach ICL at <1B parameters before training
2. **Capability-Driven Design**: Select architecture families (encoder-only vs decoder-only) based on target capabilities (reasoning vs generation)
3. **Scaling Roadmaps**: Forecast compute requirements for capability emergence, inform resource allocation

**Impact Estimates**:
- **Compute Savings**: 5-10× reduction in wasted training (avoiding sub-threshold models)
- **Development Speed**: 3-5× faster architecture iteration via predictive selection
- **Cost Reduction**: $100K-$1M saved per foundation model development cycle (at current cloud GPU pricing)

**Target Users**: ML research labs, foundation model companies, academic groups with limited compute budgets

**Evaluation Metrics**:
- Threshold prediction accuracy (MAPE < 15%)
- Compute savings (FLOPs avoided / total FLOPs)
- Architecture selection success rate (% models reaching target capability at predicted scale)

---

## 3. Key Related Work

### Foundational Papers

**1. Chen et al. (2025) - "Architecture independent generalization bounds"**
- Semantic Scholar ID: f5b291ba396778b7058cab7112f7e545cd372247
- Citation: 1 | Year: 2025
- **Core Result**: Generalization bounds for overparametrized networks depend only on metric geometry of data, activation regularity, and operator norms - independent of architecture details
- **Relevance to Hypothesis**: Provides theoretical foundation that inductive biases are quantifiable via metric geometry, validating approach of characterizing architectures through measurable bias properties
- **How Used**: Justifies random projection method for bias measurement; shows architecture differences manifest in learnable function space geometry

**2. Zhu et al. (2024) - "Scaling Graph Neural Networks: Empirical Laws for Emergent Abilities"**
- Semantic Scholar ID: 3928d022baccbfd9b4e894a2d95ebe5eec77df15
- Citation: 62 | Year: 2024
- **Core Result**: Introduces "emergent abilities" in GNNs where performance improves dramatically above threshold; empirical power-law formula T = T₀ · system_size^α predicts emergence
- **Relevance to Hypothesis**: Demonstrates feasibility of power-law threshold prediction in specific domain; validates that emergence follows predictable mathematical patterns
- **How Used**: Serves as existence proof that predictive formulas work; methodological template for power-law fitting; baseline to extend beyond single-architecture families

**3. Min et al. (2021) - "On the Explicit Role of Initialization on Convergence and Implicit Bias"**
- Semantic Scholar ID: fbf59c1f0e6785af0dc6d5b98091ce20859088e0
- Citation: 53 | Year: 2021
- **Core Result**: Initialization constrains gradient flow dynamics to invariant sets leading to min-norm solutions; explicit analysis of how overparametrization affects implicit bias
- **Relevance to Hypothesis**: Shows inductive bias is measurable via gradient flow analysis; proves initialization effects persist throughout training
- **How Used**: Theoretical foundation for early-training bias measurement; justifies stability assumption that early biases predict late-training behavior

**4. Yao et al. (2024) - "Towards Neural Scaling Laws for Time Series Foundation Models"**
- Semantic Scholar ID: a87d911bee64f961730142670dadf9f5b8cc9210
- Citation: 24 | Year: 2024
- **Core Result**: Encoder-only Transformers demonstrate better scalability than decoder-only for time series; architecture plays significant role in scaling
- **Relevance to Hypothesis**: Critical evidence that architectures have different scaling profiles; motivates architecture-specific inductive bias measurement
- **How Used**: Validates that architecture differences matter for scaling; supports hypothesis that universality classes exist based on architectural primitives

### Supporting Literature

**Statistical Physics Foundations:**
- Wilson & Fisher - Renormalization group theory and universality classes
- Goldowsky-Dill et al. (2023) - Phase transitions in neural networks
- Roberts et al. (2022) - RG analysis of neural training

**Scaling Laws Baseline:**
- Kaplan et al. (2020) - Neural scaling laws for language models
- Hoffmann et al. (2022) - Chinchilla optimal scaling

**Implicit Bias Theory:**
- Neural Tangent Kernel literature
- Mean field analysis of overparametrization
- Feature learning and implicit regularization

**Emergence Research:**
- BIG-Bench capability evaluation
- GPT-3/GPT-4 in-context learning analysis
- Threshold characterization methodology

### Citation Gaps to Fill

- [ ] Johnson-Lindenstrauss lemma (random projection preservation)
- [ ] Arora et al. (2022) Edge of Stability paper
- [ ] Original universality class formulations (Wilson, Fisher)
- [ ] Attention mechanism inductive bias characterization
- [ ] Architecture search literature (DARTS baseline)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence - Bias Measurability):**
Inductive bias measures β(A,C) can be computed tractably (O(n log n)) at initialization or early training (first 1% of steps) using random projections for metric geometry and gradient flow analysis for implicit regularization, and these measures exhibit sufficient variance across architecture families to enable discrimination.

*Verification Approach*: Implement bias measurement pipeline, apply to 10 diverse architectures, report measurement cost, demonstrate variance via ANOVA (F-test for between-architecture variance)

**SH2 (Mechanism - Bias → Threshold Link):**
Architectures with similar inductive bias measures β(A₁,C) ≈ β(A₂,C) exhibit similar emergence thresholds T(C,A₁) ≈ T(C,A₂), with correlation ρ(β, T) ≥ 0.7 within capability types, demonstrating causal link between measurable architectural properties and scaling behavior.

*Verification Approach*: Train 20-30 architecture pairs across multiple scales, measure β and T, compute Spearman correlation, test H₀: ρ = 0 vs H₁: ρ ≥ 0.7

**SH3 (Comparison - Prediction Advantage):**
Bias-based threshold prediction using formula T(C,A) = T₀(C) · β(A,C)^α achieves MAPE < 15% on held-out architectures, providing 5× error reduction compared to trial-and-error baseline (O(10×) error) and 5-10× compute savings through targeted architecture selection.

*Verification Approach*: Phase 2 confirmatory study with 20 held-out architectures, compare predicted vs actual T, compute MAPE and total FLOPs, benchmark against random architecture selection

### Readiness Checklist

- [x] **Hypothesis Well-Formed**: IF-THEN-BECAUSE structure with explicit causal mechanism
- [x] **Variables Operationalized**: All 8 variables have clear measurement methods
- [x] **Predictions Quantified**: Three testable predictions with numerical success criteria
- [x] **Falsification Criteria**: Five explicit conditions that would reject hypothesis
- [x] **Assumptions Explicit**: Six key assumptions with justifications and risk mitigation
- [x] **Scope Defined**: Clear boundaries of applicability and known limitations
- [x] **Related Work Mapped**: 4 foundational papers with explicit usage documentation
- [x] **Statistical Design**: Phase 1 (exploratory) and Phase 2 (confirmatory) with power analysis
- [x] **SOTA Baseline**: Quantified comparison to Kaplan, Zhu, NAS methods
- [x] **Sub-Hypotheses**: Three SH preview for Phase 2B decomposition
- [x] **Contribution Claims**: Theoretical, methodological, practical impacts specified

**Phase 2B Ready**: YES ✅

### Open Questions

1. **Capability Taxonomy Completeness**: Current bias measures specified for ICL, reasoning, generation - are there other capability types requiring new measures? (Non-blocking - framework extensible)

2. **Universality Class Count**: Hypothesis assumes 4-6 classes - empirical discovery may reveal more or fewer. (Non-blocking - adaptive to findings)

3. **Cross-Domain Transfer**: Validated approach for language/vision - does it extend to RL, continuous control, graph learning? (Future work - not required for core validation)

4. **Temporal Bias Stability**: Assumption that early training bias predicts late training - needs empirical validation across architectures. (Blocking - SH1 verification)

5. **Threshold Definition Sensitivity**: How robust are predictions to choice of capability performance threshold (e.g., 70% vs 80% accuracy)? (Non-blocking - can report sensitivity analysis)

6. **Hybrid Architecture Handling**: How to assign universality class to hybrid architectures (e.g., ConvNeXT = convolution + attention)? (Non-blocking - can use mixed-class interpolation)

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-06*
