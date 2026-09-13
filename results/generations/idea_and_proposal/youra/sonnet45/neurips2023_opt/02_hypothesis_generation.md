# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-08
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-RG-HP-Scaling-v1
**Confidence Level:** 0.90 (90%)

**Main Hypothesis:**
Under conditions where neural network model size N transforms as N → λN parameters (λ > 1), if hyperparameters (learning rate, batch size, weight decay) are treated as effective couplings that evolve according to renormalization group β-functions, then optimal hyperparameter configurations will exhibit scale-invariant fixed points manifesting as the empirically-observed "collapse" phenomenon, because the β-functions governing hyperparameter evolution encode the mathematical structure of the loss landscape's scale transformation properties, enabling prediction of optimal hyperparameters at new scales without exhaustive grid search.

**Alternative Hypothesis (H0):**
Hyper parameters do not follow predictable β-function evolution across model scales, and the collapse phenomenon is either a statistical artifact or results from mechanisms unrelated to renormalization group fixed points, requiring empirical grid search at each new model scale.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Model Size (N) | Independent | Number of trainable parameters | 10^6 to 10^12 parameters (6 orders of magnitude) |
| Learning Rate (lr) | Effective Coupling | Initial learning rate for optimizer | 10^-5 to 10^-2 (varies with scale) |
| Batch Size (bs) | Effective Coupling | Training batch size | 32 to 8192 (varies with scale) |
| Weight Decay (wd) | Effective Coupling | L2 regularization coefficient | 10^-6 to 10^-1 (varies with scale) |
| Optimal Loss (L*) | Dependent | Validation loss at convergence | Power-law decay: L ∝ N^(-α) |
| β-Functions | Theoretical Observable | β_lr = d(log lr)/d(log N), β_bs, β_wd | Fitted from empirical data |
| Fixed Points (HP*) | Derived Variable | Hyperparameters where β(HP*) = 0 | Scale-invariant configurations |
| Collapse Signature | Observable | Deviation of loss curves from universal trajectory | Binary: collapse (≈0) or no-collapse (>threshold) |

### 1.3 Causal Mechanism

**Causal Chain** (N=3 steps from complexity assessment):

**Step 1: Scale Transformation Induces Hyperparameter Flow**
- **Mechanism**: When model size increases N → λN, loss landscape geometry changes in a scale-dependent manner
- **Evidence**: Xie et al. 2024 shows learning rate schedules follow predictable stochastic differential equations; Jeon & Van Roy 2024 establishes information-theoretic linear relationship between data and model size
- **Falsification Point**: If hyperparameters do NOT change systematically with scale (random/arbitrary patterns)

**Step 2: Hyperparameter Flow Follows β-Function Dynamics**
- **Mechanism**: The evolution of optimal hyperparameters with scale can be characterized by differential equations β = d(log HP)/d(log N), analogous to renormalization group flow in statistical physics
- **Evidence**: Peraza Coppola et al. 2025 demonstrates RG framework works for neural networks using "scaling intervals" for finite systems; Bergsma et al. 2025 shows collapse emerges when hyperparameters are optimally set
- **Falsification Point**: If β-functions cannot be extracted with R² > 0.9, or fitted functions show no predictive power

**Step 3: Fixed Points of β-Functions Correspond to Collapse Phenomenon**
- **Mechanism**: At scale-invariant hyperparameter configurations (β(HP*) = 0), loss curves across different model sizes collapse onto a universal trajectory, enabling efficient hyperparameter prediction
- **Evidence**: Bergsma et al. 2025 empirically demonstrates whole training curves collapse when hyperparameters optimally set; Dereich et al. 2024 proves adaptive methods require learning rate decay for convergence (relevant perturbation theory)
- **Falsification Point**: If collapse does NOT correlate with β-function fixed points (r < 0.8), or if predicted hyperparameters perform >5% worse than grid search optimal

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step 1 → Step 2 | Xie et al. 2024 (dbdda156) | LR schedules follow predictable SDEs across scales | Strong (5 citations, 2024) |
| Step 1 → Step 2 | Jeon & Van Roy 2024 (71589222) | Data-model size relation is linear (info-theoretic foundation) | Medium (1 citation, theoretical) |
| Step 2 → Step 3 | Peraza Coppola et al. 2025 (3b467780) | RG framework validated for finite neural networks with scaling intervals | Medium (1 citation, recent cross-domain) |
| Step 2 → Step 3 | Bergsma et al. 2025 (8b91aedd) | Collapse emerges with optimal hyperparameters (empirical validation) | Strong (3 citations, direct observation) |
| Step 3 → Outcome | Dereich et al. 2024 (4baabe81) | Adam requires LR decay for convergence (theoretical constraint) | Strong (7 citations, convergence theory) |
| Step 3 → Outcome | Ayed & Hayou 2023 (bb4721b1) | Data pruning limits as boundary conditions | Medium (13 citations, fundamental limits) |

**Key Tension:**
**Tension**: Peraza Coppola et al. 2025 applies RG to LAYER-WISE transformations (treating depth as scale), while our hypothesis applies RG to MODEL-SIZE transformations (treating parameter count as scale). These are fundamentally different scale variables.

**Resolution**: Both are valid RG applications but at different hierarchical levels. Layer-wise RG (Peraza Coppola) explains within-model feature learning, while model-size RG (our hypothesis) explains cross-model hyperparameter evolution. The verification plan will explicitly test whether β-functions exist for the N → λN transformation (model size scaling), independent of layer-wise effects. If both frameworks are correct, they should be complementary rather than contradictory.

### 1.4 Key Assumptions

1. **Scale Transformation Validity**: Model size increase N → λN constitutes a well-defined scale transformation analogous to spatial rescaling in physics.
   - **Evidence**: Peraza Coppola et al. 2025 demonstrates RG framework applicability to neural networks; 6 orders of magnitude (10^6 to 10^12 parameters) provides sufficient range for asymptotic behavior.
   - **Consequence if violated**: β-functions may not exist or may be unstable; framework collapses to empirical curve-fitting without theoretical foundation.

2. **Hyperparameter Flow Continuity**: Optimal hyperparameters vary continuously and differentiably with model size, not discontinuously.
   - **Evidence**: Xie et al. 2024 shows smooth LR schedule evolution via SDEs; no evidence of discrete jumps in published scaling studies.
   - **Consequence if violated**: β-functions (differential equations) cannot be defined; would require discrete transition models instead.

3. **Finite-Size RG Validity**: RG concepts (fixed points, β-functions, universality) apply to finite neural networks using "scaling intervals" framework.
   - **Evidence**: Peraza Coppola et al. 2025 explicitly addresses finite-size effects with scaling intervals replacing traditional scaling dimensions.
   - **Consequence if violated**: Fixed point analysis becomes meaningless; predictions may only hold in infinite-width/infinite-data limit (impractical).

4. **Collapse Robustness**: The collapse phenomenon observed by Bergsma et al. 2025 is a robust signature of optimal hyperparameter settings, not a statistical artifact or dataset-specific effect.
   - **Evidence**: Bergsma et al. 2025 demonstrates collapse across multiple model sizes; deviation-from-collapse serves as early diagnostic.
   - **Consequence if violated**: Cannot use collapse as fixed point signature; would require alternative validation methods (computational cost increases significantly).

5. **Architecture-Specific Universality**: Different neural network architectures (Transformers, CNNs, MLPs) may belong to different universality classes with distinct β-functions, but within each class, relationships are universal.
   - **Evidence**: RG universality theory predicts this; Dereich et al. 2024 shows optimizer-specific behavior (Adam vs SGD).
   - **Consequence if violated**: β-functions would be model-specific (not architecture-class-specific), requiring individual calibration for each model variant; practical value diminishes.

### 1.5 Scope & Boundaries

**Where This Hypothesis Applies:**
- **Model Scales**: 10^6 to 10^12 parameters (6 orders of magnitude); sufficient range for asymptotic β-function behavior
- **Architectures**: Transformer-based language models initially; extensible to CNNs and MLPs as separate universality classes
- **Hyperparameters**: Learning rate, batch size, weight decay (3 primary couplings); other hyperparameters (warmup steps, β₁, β₂) as secondary analysis
- **Training Regime**: Standard supervised pre-training; excludes fine-tuning, continual learning, and reinforcement learning from human feedback (RLHF)
- **Data Availability**: Requires access to published scaling studies (OpenAI, Google, Meta) OR single validation run at target scale

**Where This Does NOT Apply:**
- **Very Small Models**: < 10^6 parameters may exhibit discrete rather than continuous scaling behavior
- **Extremely Large Models**: > 10^12 parameters may encounter new physical constraints (communication overhead dominates per CarbonScaling 2025)
- **Non-Standard Training**: Transfer learning, few-shot adaptation, meta-learning may have different hyperparameter dynamics
- **Multi-Objective Optimization**: Framework currently addresses loss minimization; extending to Pareto frontiers (loss vs carbon, loss vs inference speed) requires multi-dimensional β-functions
- **Architecture Search**: Framework predicts optimal hyperparameters for FIXED architecture; does not predict optimal architecture given compute budget

**Known Limitations:**
1. **Initial Validation Cost**: Requires published scaling data OR one training run per architecture class for β-function extraction (~1 GPU-day analysis + 1 full training run)
2. **Extrapolation Risk**: Predictions most reliable within interpolation range; extrapolation beyond training data range may require cautious validation
3. **Multiple β-Function Forms**: May need to test multiple functional forms (power-law, exponential, logarithmic) to find best fit
4. **Optimizer Specificity**: β-functions likely differ between Adam, SGD, AdamW, etc.; initial validation focuses on AdamW (most common for LLMs)

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (β-Function Predictive Accuracy)**:
Hyperparameters predicted using extracted β-functions will achieve validation loss within 2-5% of grid-search-optimal hyperparameters, while reducing computational cost by 10-100×.

*Measurement*:
- Extract β-functions from published scaling studies (N ∈ [10^7, 10^11])
- Predict optimal hyperparameters at new scale (e.g., 7B parameters)
- Train model with predicted hyperparameters vs. grid search baseline
- Compare final validation loss: |L_predicted - L_optimal| / L_optimal < 0.05
- Statistical test: One-sample t-test against 5% threshold, n ≥ 3 runs, p < 0.05

*Basis*:
β-function framework should capture the essential structure of hyperparameter scaling. 2-5% tolerance accounts for finite-size effects and functional form uncertainty. Grid search baseline typically requires 100-1000 trials; our method requires 1-10 validation trials (10-100× reduction).

*Success Criteria for Phase 2B*:
- Primary: Prediction error < 5% with p < 0.05
- Stretch goal: Prediction error < 2% (exceptional agreement)
- Falsification: Prediction error > 10% (no practical advantage over heuristics)

**Secondary Predictions:**
**P2 (Fixed Point-Collapse Correlation)**:
Hyperparameter configurations identified as β-function fixed points (β(HP*) ≈ 0) will correlate with empirically-observed collapse phenomenon with r > 0.8.

*Measurement*:
- Identify fixed points from fitted β-functions
- Use Bergsma et al. 2025 deviation-from-collapse metric
- Compute Pearson correlation between "proximity to fixed point" and "degree of collapse"
- Statistical test: Correlation significance test, p < 0.05

*Basis*:
Collapse is hypothesized to be the empirical manifestation of RG fixed points. Strong correlation (r > 0.8) would validate this connection.

**P3 (Computational Cost Reduction)**:
β-function-based hyperparameter selection will reduce computational cost by at least 10× compared to grid search, measured in total GPU-hours for hyperparameter tuning.

*Measurement*:
- Grid search baseline: 100-1000 full training runs (typical for LLM scaling studies)
- Our method: β-function extraction (~1 GPU-day) + 3-10 validation runs
- Cost ratio: (Baseline GPU-hours) / (Our method GPU-hours) > 10

*Basis*:
This is the primary practical benefit. Even conservative estimates (100 baseline trials vs. 10 validation trials) yield 10× reduction. Typical scaling studies use 1000+ trials, suggesting 100× reduction is achievable.

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure (β-Function Fit)**: β-functions cannot be extracted with R² > 0.9 from existing scaling data
   - Indicates hyperparameter evolution is not systematic or is dominated by noise
   - Would require alternative theoretical framework

2. **Primary Failure (Prediction Accuracy)**: Predicted hyperparameters achieve > 10% worse validation loss than grid-search optimal
   - Indicates β-functions lack predictive power
   - No practical advantage over existing empirical methods

3. **Mechanism Failure (Fixed Point-Collapse)**: Correlation between fixed points and collapse phenomenon is weak (r < 0.5)
   - Indicates collapse has different causal origin than RG fixed points
   - Theoretical framework is incorrect even if predictions work

4. **Comparative Failure (Cost)**: Computational cost reduction < 5× compared to grid search
   - Indicates practical benefit is marginal
   - Not worth complexity of framework

5. **Robustness Failure**: β-functions show no consistency across different datasets or training runs (high variance)
   - Indicates dataset-specific or stochastic effects dominate
   - Framework not generalizable

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

**Mode: Absolute Performance Validation** (Not SOTA comparison)

This hypothesis does not target SOTA comparison on benchmark accuracy metrics. Instead, it proposes a **meta-level improvement**: reducing the computational cost of hyperparameter optimization while maintaining comparable performance to grid search.

**Relevant Baselines:**
1. **Grid Search**: Exhaustive search over hyperparameter space (100-1000 trials)
2. **Bayesian Optimization**: CARBS (Fetterman et al. 2023) - learns scaling relationships
3. **Empirical Scaling Laws**: Li et al. 2025 - empirical hyperparameter relationships
4. **Transfer Learning**: Reuse hyperparameters from smaller models (common heuristic)

**Comparison Metric**: Not accuracy on benchmark, but **hyperparameter tuning efficiency**:
- Cost: GPU-hours for hyperparameter search
- Quality: Final validation loss relative to grid-search optimal

Our hypothesis targets 10-100× cost reduction while staying within 2-5% of optimal loss.

### 1.8 Statistical Verification Design

**Phase 1: β-Function Extraction (Empirical Analysis)**
- **Data Source**: Published scaling studies from OpenAI Scaling Laws (Kaplan et al. 2020), Chinchilla (Hoffmann et al. 2022), and recent LLM papers
- **Sample Size**: Minimum 10 data points across model sizes (10^6 to 10^11 parameters)
- **Method**: Nonlinear regression to fit β = d(log HP)/d(log N)
- **Functional Forms to Test**: Power-law, exponential, logarithmic, piecewise
- **Goodness of Fit**: R² > 0.9 required; report 95% confidence intervals for β-function parameters
- **Cross-Validation**: Hold-out validation on 20% of scale range

**Phase 2: Fixed Point Analysis (Theoretical Validation)**
- **Method**: Solve β(HP*) = 0 numerically for each fitted β-function
- **Stability Analysis**: Compute eigenvalues of Jacobian ∂β/∂HP at fixed points
- **Collapse Correlation**: Pearson correlation test between fixed-point proximity and collapse metric
- **Statistical Test**: Two-tailed correlation test, α = 0.05, report r and p-value

**Phase 3: Prediction Validation (Experimental Validation)**
- **Sample Size Calculation**:
  - Effect size (prediction error target): δ = 5%
  - Baseline variance (from literature): σ ≈ 10%
  - Cohen's d = δ/σ = 0.5 (medium effect)
  - Required runs: n ≥ 25 (power = 0.8, α = 0.05, one-sample t-test)
  - Practical constraint: Use n = 3-10 runs (cost-limited)
- **Test Specification**:
  - Null hypothesis (H0): Prediction error ≥ 10% (no advantage)
  - Alternative (H1): Prediction error < 5% (practical advantage)
  - Test: One-sample t-test against 5% threshold
  - Significance level: α = 0.05 (one-tailed)
- **Report Format**: Mean prediction error ± standard deviation, 95% CI, Cohen's d, p-value
- **Robustness Check**: Repeat with different random seeds (n ≥ 3)

**Phase 4: Computational Cost Analysis (Efficiency Validation)**
- **Measurement**: Total GPU-hours for hyperparameter tuning
- **Baseline**: Grid search with 100-1000 trials (from literature reports)
- **Our Method**: β-function extraction (~1 GPU-day) + validation runs (n trials)
- **Cost Ratio**: Report mean and 95% CI
- **Success Criterion**: Cost ratio > 10× with statistical significance

**Multiple Testing Correction**:
- Bonferroni correction for 4 primary hypotheses: α_corrected = 0.05/4 = 0.0125
- Report both uncorrected and corrected p-values

**Open Science Commitment**:
- Pre-register hypotheses and analysis plan
- Release β-function extraction code and fitted parameters
- Report all experiments (no selective reporting)

---

## 2. Contribution Summary

**Primary Contribution:**
- **Type**: Theoretical + Methodological
- **Statement**: First application of renormalization group β-functions to explain and predict hyperparameter scaling across neural network model sizes. Provides theoretical foundation for empirically-observed collapse phenomenon and enables 10-100× reduction in hyperparameter tuning computational cost.
- **Novelty**: While RG has been applied to layer-wise learning in neural networks (Peraza Coppola et al. 2025), no prior work applies RG to hyperparameter evolution across model scales. This bridges statistical physics (RG theory) with machine learning optimization (scaling laws), explaining WHY scaling works rather than just describing WHAT works.

**Secondary Contributions:**
- **Methodological**: β-function extraction protocol from published scaling studies; algorithmic framework for cross-scale hyperparameter prediction with uncertainty quantification
- **Empirical**: Validation that collapse phenomenon correlates with RG fixed points; demonstration that 2-5% prediction accuracy is achievable with orders-of-magnitude cost reduction
- **Practical**: Open-source library for β-function extraction and hyperparameter prediction; benchmark dataset enabling reproducible hyperparameter scaling research

---

## 3. Key Related Work

**Foundation Sources (Mechanism Evidence):**

1. **"Optimization Hyper-parameter Laws for Large Language Models"** (2024)
   - Authors: Xingyu Xie, Kuang-Yu Ding, Shuicheng Yan, Kim-Chuan Toh, Tianwen Wei
   - Semantic Scholar ID: dbdda156a9de5d8ba73a12d9b50c6eed097da055
   - URL: https://www.semanticscholar.org/paper/dbdda156a9de5d8ba73a12d9b50c6eed097da055
   - Key Finding: Learning rate schedules follow predictable stochastic differential equations (SDEs) across scales → Direct evidence for β-function existence

2. **"Scaling with Collapse: Efficient and Predictable Training of LLM Families"** (2025)
   - Authors: Shane Bergsma, Bin Claire Zhang, Nolan Dey, et al.
   - Semantic Scholar ID: 8b91aedddfe1d27d7f1a837c252e3e7c61d1d1c1
   - URL: https://www.semanticscholar.org/paper/8b91aedddfe1d27d7f1a837c252e3e7c61d1d1c1
   - Key Finding: Loss curves collapse onto universal trajectory when hyperparameters optimally set → Empirical signature of RG fixed points

3. **"Renormalization group for deep neural networks: Universality of learning and scaling laws"** (2025)
   - Authors: Peraza Coppola et al.
   - Semantic Scholar ID: 3b467780515433e7bbac1679f0e86764e6795d95
   - Key Finding: RG framework works for finite neural networks using "scaling intervals" → Validates finite-size RG applicability

4. **"Information-Theoretic Foundations for Neural Scaling Laws"** (2024)
   - Authors: Hong Jun Jeon, Benjamin Van Roy
   - Semantic Scholar ID: 71589222ecf9700a519dd430ac00177b3b467fda
   - Key Finding: Optimal data-model size relation is linear (info-theoretic bound) → Conservation laws in RG framework

5. **"Non-convergence of Adam and other adaptive stochastic gradient descent optimization methods"** (2024)
   - Authors: Steffen Dereich, Robin Graeber, Arnulf Jentzen
   - Semantic Scholar ID: 4baabe81670772edb9952d6c15381a814af8d2a8
   - Key Finding: Adaptive methods require learning rate decay for convergence → Relevant perturbation analysis for RG flow

**Comparison Baselines:**

6. **"Tune As You Scale: Hyperparameter Optimization For Compute Efficient Training"** (2023)
   - Authors: Abraham J. Fetterman, Ellie Kitanidis, Joshua Albrecht, et al.
   - Semantic Scholar ID: 196e48016d66617fe21f3d2fdde9657b9bb52ca3
   - Method: CARBS - learns scaling relationships via Bayesian optimization
   - Comparison: Empirical learning vs. our theoretical RG framework

7. **"Predictable Scale: Part I - Optimal Hyperparameter Scaling Law in Large Language Model Pretraining"** (2025)
   - Authors: Li et al.
   - Semantic Scholar ID: 495c0fd22341f46294236c9331b37e40cba1c028
   - Method: Empirical hyperparameter scaling laws
   - Comparison: Descriptive (WHAT) vs. our explanatory (WHY) framework

**Gap Evidence:**

8. **"Data pruning and neural scaling laws"** (2023)
   - Authors: Fadhel Ayed, Soufiane Hayou
   - Semantic Scholar ID: bb4721b1a806ac00308bfb174edf3c36b6f0b620
   - Gap: Fundamental limits of data pruning show boundary conditions for scaling
   - Relevance: Defines where RG framework boundaries lie (data quality limits)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**Sub-Hypothesis Structure** (Total: 2 + N = 2 + 3 = 5 sub-hypotheses)

**SH1 (Existence - Foundation):**
"Do hyperparameters (learning rate, batch size, weight decay) exhibit systematic, predictable evolution across model scales (N ∈ [10^6, 10^12]) that can be characterized by smooth β-functions with R² > 0.9?"

- **Maps to**: Primary prediction (β-function predictive accuracy)
- **Verification type**: Empirical (data analysis + regression fitting)
- **Critical**: MUST PASS for Phase 2B to proceed - if β-functions don't exist, framework collapses
- **Timeline**: 2-4 weeks (β-function extraction from published data)

**SH2 (Mechanism - Core):**
"Is the renormalization group framework with β-function flow and fixed points the correct theoretical explanation for hyperparameter scaling behavior?"

- **Maps to**: Causal mechanism (3 steps)
- **Verification type**: Multi-step causal analysis
- **Critical**: Determines explanatory power (WHY vs. just WHAT)
- **Phase 2B Decomposition**: Will split into N=3 sub-hypotheses:
  - **SH2-M1**: Does scale transformation (N → λN) induce systematic hyperparameter flow? (Step 1)
  - **SH2-M2**: Do fitted β-functions accurately describe this flow? (Step 2)
  - **SH2-M3**: Do β-function fixed points correlate with empirically-observed collapse? (Step 3)
- **Timeline**: 6-8 weeks (sequential verification of each mechanism step)

**SH3 (Comparison - Validation):**
"Does the RG-based hyperparameter prediction approach achieve 10-100× computational cost reduction compared to grid search while maintaining prediction error < 5%?"

- **Maps to**: Secondary predictions (P3 cost reduction + P1 accuracy)
- **Verification type**: Comparative empirical (head-to-head vs. baselines)
- **Critical**: Determines practical value (is it worth the complexity?)
- **Baselines**: Grid search, CARBS (Bayesian opt), empirical scaling laws (Li et al. 2025)
- **Timeline**: 8-12 weeks (full training runs for validation)

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned (H-RG-HP-Scaling-v1)
- [x] Confidence level specified (0.90)
- [x] Alternative hypothesis (H0) defined (hyperparameters do not follow β-function evolution)
- [x] All variables have operationalization from evidence (8 variables with measurement methods)
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence table with 6 links)
- [x] Causal chain length (N=3) determined and stored
- [x] Key tension identified and resolution proposed (layer-wise vs. model-size RG - complementary frameworks)
- [x] Key assumptions list consequences if violated (5 assumptions with clear consequences)
- [x] At least 2 testable predictions exist (3 predictions: P1 accuracy, P2 correlation, P3 cost)
- [x] Primary prediction marked and quantitative (P1 with < 5% error threshold)
- [x] Falsification criteria are defined (5 failure modes with quantitative thresholds)
- [x] Baselines are identified for comparison (Grid search, CARBS, Li et al. 2025, Transfer learning)
- [x] SH1, SH2, SH3 are clear starting points (5 total sub-hypotheses: SH1 + SH2-M1/M2/M3 + SH3)
- [x] Statistical verification design complete (4-phase plan with sample sizes and tests)
- [x] Evidence sources documented (8 key papers with Semantic Scholar IDs)

**Status**: ✅ **ALL Phase 2B requirements met - Ready for verification planning**

### Open Questions

**For Phase 2B Verification Planning:**

1. **Data Availability & Access**: Can we obtain sufficient published scaling data (minimum 10 model sizes) from OpenAI, Google, Meta studies? If proprietary data is unavailable, should we conduct our own scaling study (significantly higher cost)?

2. **Computational Resources**: What is realistic budget for validation experiments? Single 7B model training run requires ~$10-50K in compute. Phase 2B must determine if we can afford full validation or must rely primarily on published data analysis.

3. **Priority Verification Order**: Should we verify sequentially (SH1 → SH2 → SH3) or in parallel? Sequential is safer (don't invest in mechanism testing if β-functions don't exist) but slower. What's the optimal strategy given resource constraints?

4. **Functional Form Selection**: β-functions could follow power-law, exponential, or logarithmic forms. How many functional forms should we test in Phase 2B? Need balance between thoroughness and parsimony (avoid overfitting).

5. **Architecture Scope**: Should Phase 2B focus exclusively on Transformers (most relevant for LLMs), or test universality hypothesis by including CNNs/MLPs? Broader scope increases confidence but multiplies validation cost.

6. **Risk Mitigation Strategy**: If SH1 (β-function existence) fails partially (e.g., R² = 0.85 instead of > 0.9), do we:
   - Relax threshold and continue? (pragmatic)
   - Refine approach with additional functional forms? (thorough)
   - Pivot to alternative framework? (conservative)

   Phase 2B must define decision criteria for partial failures.

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-08*
