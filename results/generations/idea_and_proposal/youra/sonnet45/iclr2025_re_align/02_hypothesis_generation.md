# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-CMRVA-SBE-001
**Confidence Level:** 0.85 (High)

**Main Hypothesis:**
Representational features (geometric structure of activation manifolds, attention flow patterns, sparse probe features) causally mediate the relationship between alignment interventions (RLHF, DPO, supervised fine-tuning) and value-aligned behavioral outcomes (fairness, safety, truthfulness). Specifically, the proportion of alignment effect transmitted through representational changes (Natural Indirect Effect / Total Effect) will be ≥0.60, indicating representational features are primary causal mediators rather than spurious correlates.

**Alternative Hypothesis (H0):**
Representational features do not causally mediate alignment effects. Instead, alignment interventions directly produce value-aligned behaviors through non-representational pathways (e.g., memorization of correct outputs, decision boundary shifts without geometric representation changes). Under H0, NIE/Total Effect < 0.30, indicating representational changes are epiphenomenal rather than causal.

### 1.2 Variables

| Variable | Type | Operationalization | Measurement Method | Range/Unit |
|----------|------|-------------------|-------------------|------------|
| **T (Intervention)** | Treatment (Continuous) | Alignment intervention intensity | RLHF: KL penalty weight λ ∈ [0.01, 0.1, 1.0]<br>DPO: β parameter ∈ [0.1, 0.5, 2.0]<br>SFT: Learning rate × epochs | Continuous scalar |
| **M₁ (Geometric Structure)** | Mediator | Representational similarity to reference-aligned model | Linear CKA between layer L=16 activations on 1000 evaluation samples | [0, 1] |
| **M₂ (Attention Patterns)** | Mediator | Attention flow alignment with interpretable patterns | Frobenius norm of attention matrix difference from human-aligned reference | [0, ∞), normalized to [0, 1] |
| **M₃ (Sparse Features)** | Mediator | Top-K causally important features | LASSO-selected features (K=100) from 4096-dimensional activations | Binary vector (100-dim) |
| **Y₁ (Truthfulness)** | Outcome | Factual accuracy in question-answering | TruthfulQA accuracy (% correct answers) | [0, 100]% |
| **Y₂ (Fairness)** | Outcome | Demographic parity in outputs | FairBench demographic parity ratio across protected attributes | [0, 1] (1 = perfect parity) |
| **Y₃ (Safety)** | Outcome | Refusal rate on harmful prompts | Safety refusal rate on AdvBench adversarial prompts | [0, 100]% |
| **C (Confounders)** | Confounder | Base model architecture, training data, hyperparameters | Held constant or randomized in experimental design | Categorical/Continuous |

### 1.3 Causal Mechanism

**Proposed Causal Chain:**

```
T (Intervention) → M (Representations) → Y (Behaviors)
         ↓                                      ↑
         └──────────────────────────────────────┘
                (Direct Effect - NDE)
```

**Step-by-Step Mechanism:**

1. **T → M:** Alignment intervention (RLHF/DPO) modifies training objective → Gradient updates reshape activation manifolds → Representational features shift toward reference-aligned model geometry
   - **Timing:** Occurs during training phase (steps 0 → N)
   - **Biological Analogy:** Synaptic plasticity from environmental feedback

2. **M → Y:** Modified representations propagate through model layers → Inference-time activation patterns reflect aligned geometry → Outputs exhibit value-aligned behaviors
   - **Timing:** Occurs at inference on held-out test set
   - **Mechanism:** Aligned representations encode task-relevant features that generalize to value-aligned decision-making

3. **T → Y (Direct):** Intervention may directly affect outputs via non-representational pathways (e.g., memorization of training examples, decision boundary shifts that don't alter geometric structure)
   - **Natural Direct Effect (NDE):** Effect of T on Y not mediated by M
   - **Natural Indirect Effect (NIE):** Effect of T on Y flowing through M

**Mathematical Formulation:**
- Total Effect (TE) = E[Y(T=1) - Y(T=0)]
- NIE = E[Y(T=1, M(T=1)) - Y(T=1, M(T=0))]
- NDE = E[Y(T=1, M(T=0)) - Y(T=0, M(T=0))]
- TE = NIE + NDE
- **Proportion Mediated** = NIE / TE (hypothesis: ≥0.60)

**Evidence for Causal Links:**

**T → M Evidence:**
- **Empirical:** Bhattarai et al. (2025) showed knowledge distillation shifts representational geometry measured by Procrustes distance
- **Mechanistic:** Gradient-based training directly updates model parameters → activation patterns must change
- **Validation:** Measure ΔM before/after intervention T; expect correlation r > 0.7 between intervention intensity and representational change

**M → Y Evidence:**
- **Empirical:** Dapello et al. (2022) showed aligning representations with macaque IT cortex improves behavioral robustness
- **Empirical:** Bo & Khosla (2024) found metrics emphasizing geometric structure (CKA, Procrustes) correlate with functional task performance
- **Validation:** Representation engineering experiments (intervene ONLY on M) should produce ΔY matching predicted NIE

**T → M → Y Chain:**
- **Temporal Ordering:** Representations measured at training step T < behaviors measured at inference time (satisfies temporal precedence)
- **Plausibility:** Sucholutsky et al. (2023) framework establishes representational alignment as bridge between architecture and behavior
- **Gap:** Causal mechanism remains correlational in prior work; our framework formalizes via NIE/NDE decomposition

**Key Tension:**
**Correlation vs. Causation Debate:** Existing work (Dapello, Bo & Khosla, Ogg et al.) demonstrates strong correlations between representational alignment and behavioral outcomes, but correlation ≠ causation. Three alternative explanations exist:

1. **Confounding:** Hidden variables (e.g., training data composition) may cause both representational alignment AND behavioral alignment, creating spurious correlation
2. **Reverse Causation:** Behavioral task performance during training may shape representations, not vice versa
3. **Epiphenomenalism:** Representations may change in parallel with behaviors without causal influence

**Resolution via Mediation Analysis:** Our framework disentangles these alternatives through:
- **Sequential ignorability validation:** Sensitivity analysis bounds confounding effects
- **Temporal ordering verification:** Measure M before Y to rule out reverse causation
- **Representation engineering validation:** Intervene on M independently of T to test causal sufficiency

**Hypothesis Prediction:** If representations are causal mediators (not epiphenomena), then NIE/TE ≥ 0.60. If epiphenomenal, NIE/TE < 0.30.

### 1.4 Key Assumptions

**A1. Sequential Ignorability (Strong Assumption - Requires Validation)**

**Statement:** No unmeasured confounding exists between:
1. T → M (intervention affects representations only through observed pathway)
2. M → Y (representations affect behaviors only through observed pathway)
3. T → Y (no hidden direct pathways bypassing M)

**Why Necessary:** Enables causal identification of NIE/NDE; without this, effects may be confounded

**Validation Strategy:**
- **Sensitivity Analysis (Cinelli & Hazlett 2020):** Report "results hold unless unmeasured confounder explains ≥X% variance in both T→M and M→Y"
- **Randomized Pilot:** Randomly assign intervention types (eliminates T→M confounding)
- **Synthetic Validation:** Generate models with known causal graphs, validate assumption recovery

**Expected Violation:** Training data biases likely confound T→M→Y chain (e.g., certain data distributions favor both specific representations AND behaviors)

**Mitigation:** Transparent sensitivity bounds (e.g., "causal claims hold unless confounder R² ≥ 0.20")

---

**A2. Mediator Sufficiency (Medium Assumption)**

**Statement:** Measured mediators (M₁: CKA, M₂: Attention, M₃: LASSO features) capture majority of true causal pathway from T → Y

**Why Necessary:** If true mediators are unmeasured, NIE will be underestimated (Type II error)

**Validation Strategy:**
- **Representation Engineering Validation:** Intervene ONLY on M (e.g., activation steering toward aligned representations), measure ΔY; if ΔY ≈ predicted NIE (within 10%), mediator is sufficient
- **Multiple Mediator Specifications:** Test M₁, M₂, M₃ separately; if all show similar NIE, sufficiency likely
- **Residual Analysis:** Check if T→Y residual (after controlling for M) is small

**Expected Challenge:** CKA/attention may miss local causal features (specific neurons/heads); LASSO selection mitigates this

---

**A3. Temporal Ordering (Plausible Assumption)**

**Statement:** Representational changes M occur BEFORE behavioral changes Y in causal sequence

**Why Necessary:** Mediation requires cause (M) to precede effect (Y)

**Evidence:**
- Training phase: Representations evolve during gradient updates (steps 0 → N)
- Inference phase: Behaviors measured on held-out test set AFTER training completes
- Temporal precedence: ΔM observable at training step T, ΔY observable at inference time > T

**Validation:** Measure representations at multiple training checkpoints; verify ΔM precedes emergence of ΔY on validation set

---

**A4. SUTVA (Stable Unit Treatment Value Assumption) (Weak Assumption)**

**Statement:** Intervention on one model instance doesn't affect other instances

**Why Necessary:** Standard causal inference assumption for independent units

**Validity:** TRUE for isolated training runs (no cross-contamination between experimental conditions)

---

**A5. Monotonicity of Intervention (Plausible Assumption)**

**Statement:** Increasing alignment intervention intensity (higher λ in RLHF, higher β in DPO) monotonically increases representational alignment (does not decrease)

**Why Plausible:** Alignment interventions explicitly optimize for value-aligned outputs → representations should shift toward aligned geometry, not away

**Testable:** Measure ΔM across intervention intensities; verify monotonic relationship

**Alternative:** Non-monotonic relationship (e.g., very high KL penalties collapse representations) would invalidate linear mediation model → require non-linear extensions

---

**Assumption Summary Table:**

| Assumption | Strength | Validation Method | Expected Violation | Mitigation |
|------------|----------|-------------------|-------------------|------------|
| A1. Sequential Ignorability | STRONG | Sensitivity analysis, randomized pilot | Training data confounding | Transparent bounds (R² ≥ 0.20) |
| A2. Mediator Sufficiency | MEDIUM | RepE validation, multi-spec test | Local features missed | LASSO + multiple metrics |
| A3. Temporal Ordering | PLAUSIBLE | Checkpoint measurement | N/A (training→inference) | Built into design |
| A4. SUTVA | WEAK | Experimental isolation | N/A (independent runs) | Standard practice |
| A5. Monotonicity | PLAUSIBLE | Dose-response curve | Very high penalties | Non-linear extension |

### 1.5 Scope & Boundaries

**APPLIES TO:**

**Model Types:**
- Large language models (LLMs) with ≥7B parameters (LLaMA-2, GPT-3.5 class, Claude-2)
- Transformer-based architectures with accessible layer activations
- Post-training aligned models (RLHF, DPO, supervised fine-tuning applied)

**Intervention Types:**
- **Continuous interventions** with measurable intensity:
  - RLHF with varying KL penalty weights (λ ∈ [0.01, 1.0])
  - DPO with varying β parameters (β ∈ [0.1, 2.0])
  - Supervised fine-tuning with varying learning rates or epochs
- **Post-training phase** only (pretraining excluded due to complexity)

**Value Dimensions:**
- **Truthfulness:** Factual accuracy measurable via TruthfulQA benchmark
- **Fairness:** Demographic parity measurable via FairBench or equivalent
- **Safety:** Harmful output refusal measurable via AdvBench adversarial prompts

**Representational Features:**
- Layer activations accessible for CKA computation
- Attention matrices extractable for pattern analysis
- High-dimensional features (4096+) for LASSO selection

**Experimental Settings:**
- Access to base unaligned model + aligned variants
- Held-out test sets for behavior measurement
- Sufficient compute for CKA/mediation analysis (<100 GPU-hours)

---

**DOES NOT APPLY TO:**

**Out-of-Scope Model Types:**
- Black-box API-only models (no activation access)
- Small models (<1B parameters) where emergence may not occur
- Non-transformer architectures (CNNs, RNNs) without clear layer structure
- Vision models or multimodal models (different representational structure; requires adaptation)

**Out-of-Scope Interventions:**
- **Discrete architectural changes** (adding layers, changing attention mechanisms)
  - *Reason:* Requires different causal framework (structural interventions, not parametric)
- **Pretraining dynamics**
  - *Reason:* Too many confounders, no clear intervention baseline, causal chains highly complex
- **In-context learning or prompting**
  - *Reason:* No training-time intervention; representations don't change

**Out-of-Scope Value Dimensions:**
- **Emergent capabilities** without clear behavioral metrics (creativity, common sense reasoning)
  - *Reason:* Hard to quantify outcomes Y; mediation analysis requires measurable Y
- **Subjective alignment** (humor, personality)
  - *Reason:* Behavioral benchmarks lack consensus
- **Multi-agent value alignment**
  - *Reason:* Interactions between agents introduce confounding

**Out-of-Scope Settings:**
- Insufficient activation access (API-only, proprietary models)
- Low-data regimes (<100 samples) where CKA bias becomes problematic (Murphy et al. 2024)
- Cross-lingual alignment (requires language-specific mediator specifications)

---

**KNOWN LIMITATIONS:**

**L1. Sensitivity to Unmeasured Confounding**
- **Issue:** Training data biases, emergent capabilities, base model inductive biases may confound T→M→Y
- **Impact:** If confounding R² > 0.20, causal estimates may be unreliable
- **Mitigation:** Sensitivity analysis provides bounds; randomized experiments reduce confounding

**L2. Mediator Measurement Error**
- **Issue:** CKA/attention are global summaries; may miss local causal features (specific neurons)
- **Impact:** NIE underestimated if true mediators unmeasured
- **Mitigation:** LASSO feature selection + multiple mediator specifications + RepE validation

**L3. Generalization Across Scales**
- **Issue:** Causal pathways may differ between 7B and 70B models (emergence of new mechanisms)
- **Impact:** Framework validated on 7B may not generalize to 70B without re-validation
- **Mitigation:** Per-scale synthetic validation experiments

**L4. Cross-Domain Transfer Challenges**
- **Issue:** Framework designed for LLMs; vision/multimodal models have different representational structures
- **Impact:** Mediator specifications (CKA on text embeddings) may not transfer to visual representations
- **Mitigation:** Domain-specific mediator design (convolutional layer features for vision)

**L5. Non-Linear Mediation**
- **Issue:** Framework assumes approximately linear mediation; very high intervention intensities may cause non-linear effects
- **Impact:** NIE/NDE estimates biased if true relationship is non-linear
- **Mitigation:** Test linearity assumption; extend to generalized additive models if needed

---

**Scope Summary:**
- **Core Target:** Post-training alignment of 7B+ parameter transformer LLMs on truthfulness/fairness/safety
- **Primary Limitation:** Assumes sequential ignorability with sensitivity bounds; limited to models with activation access
- **Generalization:** Framework is conceptually general but requires empirical validation per domain/scale

### 1.6 Testable Predictions

**Primary Prediction (P1):**

**Prediction Statement:**
If representational features causally mediate alignment effects, then the proportion of total effect transmitted through representational changes (NIE / Total Effect) will be ≥0.60 across alignment interventions (RLHF, DPO) and value dimensions (truthfulness, fairness, safety).

**Operationalization:**
1. Apply RLHF with λ ∈ [0.01, 0.1, 1.0] to base LLaMA-2-7B model
2. Measure Total Effect: TE = E[Y(λ=1.0) - Y(λ=0.01)] for Y ∈ {TruthfulQA, FairBench, SafetyRefusal}
3. Measure NIE via mediation analysis with mediators M ∈ {CKA, Attention, LASSO features}
4. Compute Proportion Mediated = NIE / TE

**Success Criterion:**
- **Strong Support:** Proportion Mediated ≥ 0.60 for ≥2/3 value dimensions
- **Moderate Support:** Proportion Mediated ∈ [0.40, 0.60]
- **Weak/No Support:** Proportion Mediated < 0.40

**Statistical Test:**
- Bootstrap 95% confidence intervals for NIE/TE (1000 bootstrap samples across model variations)
- H0: Proportion Mediated ≤ 0.30 (epiphenomenal); H1: Proportion Mediated > 0.60 (causal)
- Significance level: α = 0.05

---

**Secondary Predictions:**

**P2: Mediator Sufficiency via Representation Engineering**

**Prediction Statement:**
If measured representational features (CKA, attention, LASSO) are causally sufficient mediators, then intervening ONLY on representations (via activation steering) will produce behavioral changes matching predicted NIE within 10% margin.

**Operationalization:**
1. Estimate NIE for specific intervention (e.g., RLHF λ=0.1 → λ=1.0) and outcome (e.g., TruthfulQA)
2. Identify target representation M* corresponding to λ=1.0
3. Apply representation engineering: Steer layer L=16 activations toward M* WITHOUT retraining
4. Measure actual behavioral change ΔY_actual
5. Compare to predicted NIE: |ΔY_actual - NIE| / |NIE|

**Success Criterion:**
- **Validated:** Relative error < 10% for ≥2/3 mediator-outcome pairs
- **Partially Validated:** Relative error 10-20%
- **Failed:** Relative error > 20% (mediators insufficient)

---

**P3: Cross-Model Generalization of Causal Estimates**

**Prediction Statement:**
If sequential ignorability holds and causal pathways are robust, then NIE/NDE estimates will generalize across model families (LLaMA, GPT, Claude) with correlation r > 0.70 between family-specific estimates.

**Operationalization:**
1. Conduct mediation analysis on LLaMA-2-7B → Estimate NIE_LLaMA
2. Conduct mediation analysis on GPT-3.5 class model → Estimate NIE_GPT
3. Conduct mediation analysis on Claude-2 class model → Estimate NIE_Claude
4. Compute Pearson correlation between NIE estimates across families

**Success Criterion:**
- **Strong Generalization:** r > 0.70 across all 3 families
- **Moderate Generalization:** r ∈ [0.50, 0.70]
- **Weak Generalization:** r < 0.50 (family-specific effects)

---

**P4: Intervention Efficiency via High-Leverage Mediators**

**Prediction Statement:**
Targeted interventions on high-leverage mediators (top-K by NIE contribution) will produce 2× larger behavioral effects per unit intervention compared to generic fine-tuning.

**Operationalization:**
1. Identify high-leverage mediators: Rank LASSO features by contribution to NIE; select top-20%
2. **Targeted Intervention:** Apply representation engineering ONLY on top-20% features
3. **Generic Intervention:** Standard fine-tuning with equal weight on all parameters
4. Measure intervention efficiency: (ΔY / ΔM) for targeted vs. generic

**Success Criterion:**
- **Validated:** Efficiency_targeted / Efficiency_generic ≥ 2.0
- **Partially Validated:** Ratio ∈ [1.5, 2.0]
- **Failed:** Ratio < 1.5

---

**Falsification Criteria:**

**The hypothesis will be considered FALSIFIED if any of the following occur:**

**F1: Low Mediation Proportion (Primary Falsification)**
- **Criterion:** NIE / TE < 0.30 across ALL value dimensions (truthfulness, fairness, safety)
- **Interpretation:** Representational changes are epiphenomenal; alignment effects flow through non-representational pathways

**F2: Mediator Intervention Failure**
- **Criterion:** Representation engineering validation shows |ΔY_actual - NIE| / |NIE| > 30% for ALL mediators
- **Interpretation:** Measured mediators (CKA, attention, LASSO) do not capture true causal pathways

**F3: Temporal Ordering Violation**
- **Criterion:** Behavioral changes ΔY precede representational changes ΔM in time-series analysis at training checkpoints
- **Interpretation:** Reverse causation (behaviors shape representations, not vice versa)

**F4: Sensitivity Analysis Catastrophic Failure**
- **Criterion:** Sensitivity bounds show results fragile to trivial confounding (R² threshold < 0.05 for unmeasured confounder to overturn results)
- **Interpretation:** Causal estimates entirely driven by confounding, not true mediation

**F5: No Generalization Across Models**
- **Criterion:** NIE estimates show zero or negative correlation (r ≤ 0) across model families (LLaMA, GPT, Claude)
- **Interpretation:** Effects are model-specific artifacts, not general causal mechanisms

---

**Prediction Summary Table:**

| Prediction | Type | Metric | Success Threshold | Falsification Threshold |
|------------|------|--------|------------------|------------------------|
| P1 | Primary | NIE / TE | ≥0.60 | <0.30 (all outcomes) |
| P2 | Secondary | \|ΔY - NIE\| / NIE | <10% | >30% (all mediators) |
| P3 | Secondary | Correlation r | >0.70 | ≤0 (zero/negative) |
| P4 | Secondary | Efficiency ratio | ≥2.0 | <1.5 |
| F1-F5 | Falsification | Various | N/A | See criteria above |

### 1.7 SOTA Baseline

**Baseline Approach:** Correlational Analysis of Representational Similarity

**Current State-of-the-Art:**
The current SOTA for understanding representational-behavioral relationships consists of:
1. **Metric Computation:** Measure representational similarity (CKA, RSA, Procrustes) between model pairs
2. **Correlation Analysis:** Compute Pearson/Spearman correlation between similarity metrics and behavioral outcomes
3. **Interpretation:** Infer that high correlation implies representational alignment "matters" for behavior

**Representative Papers:**
- Dapello et al. (2022): Correlation between macaque IT alignment and robustness (r = 0.68)
- Bo & Khosla (2024): CKA/Procrustes correlate with functional task performance
- Ogg et al. (2024): RSA similarity between GPT-4o and humans correlates with behavioral alignment

**SOTA Limitations (Why Causal Framework is Needed):**
1. **No Causal Claims:** Correlation ≠ causation; cannot distinguish confounding from true mediation
2. **No Intervention Guidance:** Cannot identify which representational features to target
3. **No Quantification:** Cannot answer "how much of alignment effect flows through representations?"
4. **No Assumption Transparency:** Unvalidated assumptions about causality

---

**Our Framework vs. SOTA Comparison:**

| Dimension | SOTA (Correlational) | CMRVA-SBE (Causal Mediation) | Advantage |
|-----------|---------------------|----------------------------|-----------|
| **Causal Claims** | Correlation only | NIE/NDE decomposition with sensitivity bounds | ✅ Rigorous causality |
| **Effect Quantification** | Correlation coefficient | Proportion mediated (NIE/TE) | ✅ Interpretable scale |
| **Intervention Design** | Ad-hoc (try and hope) | Targeted on high-leverage mediators | ✅ Principled guidance |
| **Assumption Validation** | Implicit (unstated) | Explicit sensitivity analysis | ✅ Transparent robustness |
| **Mediator Identification** | Manual selection | LASSO + RepE validation | ✅ Data-driven |
| **Generalization Evidence** | Single model studies | Cross-family validation | ✅ Robustness |

**Benchmark Tasks:**
- **Truthfulness:** TruthfulQA (Lin et al. 2022) - 817 questions across 38 categories
- **Fairness:** FairBench-style demographic parity on classification tasks
- **Safety:** AdvBench adversarial prompts (Zou et al. 2023) - harmful instruction refusal

**SOTA Performance (Correlation Approach):**
- **Dapello et al. (2022):** r = 0.68 correlation between IT alignment and adversarial robustness
- **Bo & Khosla (2024):** Linear CKA correlation with behavioral outcomes r ∈ [0.55, 0.75] depending on task
- **Limitation:** Correlation doesn't quantify causal mediation proportion

**Our Target Performance:**
- **Causal Mediation Proportion:** NIE/TE ≥ 0.60 (vs. SOTA's implicit assumption of ~100% mediation)
- **Intervention Efficiency:** 2× improvement via targeted mediator interventions (vs. SOTA's generic fine-tuning)
- **Transparency:** Sensitivity bounds (e.g., "holds unless confounder R² ≥ 0.20") vs. SOTA's unstated assumptions

**Why This is Better Than SOTA:**
1. **Scientific Rigor:** Explicit causal framework vs. implicit correlational assumptions
2. **Practical Value:** Targeted interventions vs. trial-and-error
3. **Transparency:** Quantified assumption robustness vs. opaque claims
4. **Novelty:** First application of formal mediation analysis to representational alignment

### 1.8 Statistical Verification Design

**Experimental Design:**

**Phase 1: Synthetic Validation (Ground Truth Known)**

**Objective:** Validate mediation analysis methodology on data with known causal structure

**Procedure:**
1. **Synthetic Model Generation:**
   - Create simplified neural networks (3-layer MLPs) with known causal graph:
     - T (intervention) → M (hidden layer activations) → Y (output logits)
     - Ground truth: Set NIE/TE = 0.70 via controlled weight initialization
2. **Mediation Estimation:**
   - Apply proposed framework (Wang et al. continuous treatment estimator + Cinelli sensitivity bounds)
   - Estimate NIE/TE from synthetic data
3. **Validation Metric:**
   - Recovery error: |Estimated NIE/TE - True NIE/TE|
   - **Success:** Error < 0.10 (within 10% of ground truth)
4. **Confounder Injection Test:**
   - Add synthetic confounder with known R² = 0.15
   - Verify sensitivity analysis correctly bounds effect

**Statistical Power:** N=20 synthetic models, 1000 bootstrap samples each

---

**Phase 2: Randomized Pilot (Controlled Experiment)**

**Objective:** Reduce confounding via experimental control; establish causal mediation under ideal conditions

**Procedure:**
1. **Randomization:**
   - Select base model: LLaMA-2-7B
   - Randomly assign RLHF objectives (3 different reward model targets) → Eliminates T→M confounding
   - Hold constant: Training data (use same 10K samples), hyperparameters (learning rate, batch size)
2. **Intervention Conditions:**
   - Condition 1: RLHF with truthfulness reward (KL λ=0.1)
   - Condition 2: RLHF with fairness reward (KL λ=0.1)
   - Condition 3: RLHF with safety reward (KL λ=0.1)
   - Control: No RLHF (baseline model)
3. **Measurement:**
   - T: Intervention type (randomized)
   - M: CKA, attention, LASSO features at training completion
   - Y: TruthfulQA, FairBench, SafetyRefusal on held-out 1000-sample test set
4. **Analysis:**
   - Estimate NIE/NDE for each outcome Y
   - Compute NIE/TE proportion
   - **Hypothesis Test:** H0: NIE/TE ≤ 0.30 vs. H1: NIE/TE > 0.60, α=0.05, one-sided t-test

**Sample Size Calculation:**
- **Effect Size:** Cohen's d = 0.8 (large effect)
- **Power:** 1-β = 0.80
- **Significance:** α = 0.05
- **Required N:** 26 models per condition (3 conditions × 26 = 78 models total)
- **Feasibility:** 78 models × 5 GPU-hours each = 390 GPU-hours (<$2K compute cost)

---

**Phase 3: Mediator Validation via Representation Engineering**

**Objective:** Test mediator sufficiency (M captures true causal pathway)

**Procedure:**
1. **Baseline NIE Estimation:**
   - From Phase 2, obtain predicted NIE for truthfulness outcome: NIE_pred
2. **Representation Engineering Intervention:**
   - Identify target representation M* corresponding to high-truthfulness intervention
   - Apply activation steering to layer L=16: Steer activations toward M* WITHOUT retraining
   - Use RepE method (Zou et al. 2023) with steering strength α ∈ [0.5, 1.0, 2.0]
3. **Behavioral Measurement:**
   - Measure actual behavioral change ΔY_actual on TruthfulQA
4. **Validation Test:**
   - Compute relative error: ε = |ΔY_actual - NIE_pred| / |NIE_pred|
   - **Success:** ε < 10% → Mediator validated
   - **Failure:** ε > 30% → Mediator insufficient (try alternative M specification)

**Multiple Mediator Specifications:**
Test M₁ (CKA), M₂ (attention), M₃ (LASSO) separately; if ≥2/3 show ε < 10%, mediator sufficiency likely

---

**Phase 4: Full Observational Study with Sensitivity Analysis**

**Objective:** Apply framework to production models; estimate causal effects with transparent sensitivity bounds

**Procedure:**
1. **Model Selection:**
   - LLaMA-2-7B variants: Base, Chat (RLHF-aligned), Code (SFT-aligned)
   - GPT-3.5 class: Base (via API), ChatGPT (RLHF-aligned)
   - Claude-2 class: Base, Claude-2 (Constitutional AI aligned)
2. **Intervention Variable:**
   - T = Alignment type (categorical: None, RLHF, DPO, SFT)
   - For continuous analysis: Extract KL penalty λ or equivalent from model cards
3. **Mediation Analysis:**
   - Estimate NIE/NDE using generalized propensity score (Wang et al. 2017) for continuous T
   - Bootstrap 95% CIs (B=1000 samples across model variations)
4. **Sensitivity Analysis (Cinelli & Hazlett 2020):**
   - Compute sensitivity bounds: "Results hold unless unmeasured confounder has partial R²_T ≥ X AND R²_Y ≥ X"
   - Report X for which causal estimate becomes insignificant
   - **Robustness Criterion:** X ≥ 0.15 (moderate robustness)
5. **Robustness Checks:**
   - **Mediator Specification:** Re-run with different M (CKA vs. attention vs. LASSO)
   - **Outcome Specification:** Re-run with different Y (TruthfulQA vs. FairBench vs. Safety)
   - **Model Subsample:** Re-run excluding one model family; check stability

**Statistical Tests:**
- **Primary:** Bootstrap 95% CI for NIE/TE; check if lower bound > 0.60
- **Secondary:** Permutation test (shuffle T-M-Y relationships); check p-value < 0.05 for NIE significance
- **Robustness:** Multi-specification curve analysis (plot NIE/TE across all mediator-outcome pairs)

---

**Statistical Summary Table:**

| Phase | Design Type | N (Models) | Primary Test | Success Criterion | Compute Cost |
|-------|-------------|-----------|--------------|------------------|--------------|
| 1. Synthetic | Controlled (Known GT) | 20 | Recovery error | <10% | 20 GPU-hours |
| 2. Randomized Pilot | RCT | 78 | t-test (NIE/TE > 0.60) | p < 0.05 | 390 GPU-hours |
| 3. RepE Validation | Intervention | 9 (3 mediators × 3 outcomes) | Relative error | <10% | 50 GPU-hours |
| 4. Observational | Observational + Sensitivity | 9 (3 families × 3 models) | Bootstrap CI + Sensitivity | CI_lower > 0.60, X ≥ 0.15 | 100 GPU-hours |
| **Total** | - | **116** | - | - | **560 GPU-hours** |

**Feasibility:** 560 GPU-hours @ $0.50/hour (A100) = $280 compute cost (within <$5K budget)

---

## 2. Contribution Summary

### 2.1 Theoretical Contribution

**Core Theoretical Innovation:**
First formalization of representational features as **causal mediators** in the alignment process, moving the field from correlational understanding (current state: "representational alignment correlates with behavioral outcomes") to causal quantification (proposed state: "X% of alignment effect flows through representational pathways").

**Theoretical Advance:**
- **From:** Implicit assumption that representational similarity → behavioral alignment (Dapello et al. 2022, Bo & Khosla 2024)
- **To:** Explicit causal decomposition via Natural Direct Effect (NDE) and Natural Indirect Effect (NIE) framework
- **Enables:** Distinguishing genuine causal mediation from spurious correlation via sensitivity-bounded estimates

**Gap Addressed:**
Directly resolves Gap 3 from Phase 1 research: "The causal mechanism linking representational similarity to behavioral and value alignment remains unclear" (Sucholutsky et al. 2023 identified this as open problem)

**Novel Theoretical Constructs:**
1. **Proportion Mediated** (NIE/TE): Quantifies fraction of alignment effect transmitted through representational changes
2. **Sensitivity-Bounded Causal Estimates**: Transparently reports assumption requirements (e.g., "holds unless confounder R² ≥ 0.20")
3. **High-Leverage Mediator Concept**: Identifies specific representational features contributing disproportionately to alignment

**Relationship to Existing Theory:**
- **Builds On:** Sucholutsky et al. (2023) representational alignment taxonomy
- **Formalizes:** Dapello et al. (2022) empirical observation that IT alignment → robustness
- **Extends:** Williams et al. (2021) shape metrics framework by adding causal interpretation

**Impact:**
Provides theoretical foundation for:
- Principled intervention design (target high-NIE mediators)
- Predictive modeling (estimate behavioral outcomes from representational shifts before deployment)
- Transparent causal claims (replace "alignment matters" with "alignment explains X% via representations")

---

### 2.2 Methodological Contribution

**Core Methodological Innovation:**
Adaptation of continuous treatment mediation analysis (from epidemiology/psychology) to neural network alignment interventions with high-dimensional representational mediators.

**Novel Methodological Components:**

**M1: Continuous Intervention Mediation for Gradient-Based Alignment**
- **Source Domain:** Wang et al. (2017) - continuous treatment mediation in survival analysis
- **Target Domain:** Alignment tuning with continuous intensity (RLHF KL penalty λ, DPO β)
- **Adaptation:** Generalized propensity score weighting for non-discrete interventions
- **Novelty:** First application to neural network optimization context

**M2: High-Dimensional Mediator Selection via LASSO**
- **Source Domain:** Huang et al. (2021) - LASSO for high-dimensional mediation in survival models
- **Target Domain:** Neural network activations (4096+ dimensions)
- **Adaptation:** Regularized regression to select top-K mediators from millions of parameters
- **Novelty:** Addresses "curse of dimensionality" in neural network mediation analysis

**M3: Sensitivity-Bounded Causal Estimates for Deep Learning**
- **Source Domain:** Cinelli & Hazlett (2020) - sensitivity analysis for observational studies
- **Target Domain:** Alignment interventions with unmeasured confounders (training data biases)
- **Adaptation:** Partial R² bounds for T→M and M→Y confounding
- **Novelty:** First application of formal sensitivity analysis to representational alignment

**M4: Representation Engineering Validation Protocol**
- **Integration:** Combines RepE intervention methods (Zou et al. 2023) with mediation framework
- **Procedure:** Intervene ONLY on mediator M (independent of treatment T), compare ΔY to predicted NIE
- **Novelty:** Validates mediator sufficiency empirically (not just assumed)

**Comparison to Existing Methods:**

| Method | Causal Claims | Mediator ID | Assumption Transparency | High-Dim Support |
|--------|---------------|-------------|------------------------|------------------|
| **Correlational (SOTA)** | ❌ Correlation only | Manual selection | ❌ Implicit | N/A |
| **Causal Tracing (Meng 2022)** | ⚠️ Intervention-based, no mediation | Activation patching | ⚠️ Partial | ✅ Yes |
| **RepE (Zou 2023)** | ❌ No causal framework | Manual direction selection | ❌ None | ✅ Yes |
| **CMRVA-SBE (Ours)** | ✅ NIE/NDE decomposition | LASSO + multi-spec | ✅ Sensitivity bounds | ✅ LASSO regularization |

**Technical Implementation:**
- **Framework:** PyTorch + DoWhy (causal inference library) + mediation (Python package)
- **Pipeline:** T → M measurement (CKA/attention/LASSO) → Mediator model fitting → NIE/NDE estimation → Bootstrap CIs → Sensitivity analysis
- **Computational Complexity:** O(n³) for CKA + O(p²n) for LASSO (p=features, n=samples) → Feasible for typical experiments (<100 GPU-hours)

**Reproducibility:**
- Deterministic pipeline (given random seed)
- Open-source implementations available (DoWhy, mediation library)
- Synthetic validation allows methodological verification

**Methodological Impact:**
- **Enables:** Rigorous causal claims in representational alignment research
- **Generalizes:** Framework applicable beyond alignment (e.g., transfer learning, domain adaptation)
- **Standardizes:** Provides template for causal analysis in deep learning

---

### 2.3 Practical Contribution

**Core Practical Innovation:**
Enables **targeted interventions** on high-leverage representational mediators to achieve desired value alignment outcomes with 2× greater efficiency than generic fine-tuning.

**Practical Applications:**

**PA1: Intervention Efficiency Optimization**
- **Problem:** Current practice uses trial-and-error fine-tuning on entire model
- **Solution:** Identify top-K mediators by NIE contribution → Intervene selectively
- **Benefit:** 2× larger behavioral improvement per unit intervention (Prediction P4)
- **Use Case:** Resource-constrained alignment (e.g., aligning 70B models where full fine-tuning is expensive)

**PA2: Predictive Alignment Modeling**
- **Problem:** Unknown whether alignment intervention will produce desired behavioral outcomes until after expensive training
- **Solution:** Measure representational shift ΔM → Predict behavioral outcome ΔY via NIE model → Decide whether to deploy
- **Benefit:** Reduces failed alignment attempts (saves compute + prevents misaligned model deployment)
- **Use Case:** Pre-deployment alignment verification

**PA3: Transparent Assumption Reporting**
- **Problem:** Current alignment research makes implicit causal claims without assumption validation
- **Solution:** Report sensitivity bounds (e.g., "causal claims hold unless confounder R² ≥ 0.20")
- **Benefit:** Stakeholders (regulators, deployers) understand reliability of alignment guarantees
- **Use Case:** AI safety auditing, regulatory compliance

**Application Domains:**

**Domain 1: Value Alignment Engineering**
- **Objective:** Align LLM outputs with human values (truthfulness, fairness, safety)
- **Framework Application:**
  1. Identify high-leverage mediators for each value dimension (e.g., layer 16 attention patterns for truthfulness)
  2. Design targeted RepE interventions on those mediators
  3. Predict behavioral outcomes before deployment via NIE model
- **Expected Outcome:** 50% reduction in alignment iteration cycles (fewer trial-and-error attempts)

**Domain 2: Adversarial Robustness via Representational Alignment**
- **Objective:** Improve robustness by aligning representations with robust reference models (e.g., macaque IT cortex per Dapello et al.)
- **Framework Application:**
  1. Measure NIE for robustness outcome
  2. Identify which representational features mediate robustness gains
  3. Optimize ONLY those features for maximum efficiency
- **Expected Outcome:** Maintain Dapello et al.'s robustness gains with 50% less compute

**Domain 3: Human-AI Collaboration via Representational Compatibility**
- **Objective:** Design AI systems with human-compatible representations for better collaboration
- **Framework Application:**
  1. Measure representational alignment with human cognitive patterns (via RSA behavioral similarity)
  2. Quantify how much alignment is needed for effective collaboration (via NIE/TE)
  3. Intervene on critical mediators to achieve collaboration threshold
- **Expected Outcome:** Principled design of collaborative AI systems

**Evaluation Metrics for Practical Impact:**

| Metric | Baseline (SOTA) | CMRVA-SBE Target | Measurement Method |
|--------|-----------------|------------------|-------------------|
| **Intervention Efficiency** | 1× (generic fine-tuning) | 2× (targeted mediators) | (ΔY/ΔM)_targeted / (ΔY/ΔM)_generic |
| **Alignment Iteration Cycles** | 5-10 attempts to reach target | 2-5 attempts (50% reduction) | Count of training runs to achieve Y threshold |
| **Assumption Transparency** | 0% (implicit assumptions) | 100% (sensitivity bounds reported) | Fraction of papers reporting R² bounds |
| **Predictive Accuracy** | N/A (no prediction model) | <10% error (ΔY prediction from ΔM) | \|ΔY_pred - ΔY_actual\| / ΔY_actual |

**Practical Limitations:**
- Requires activation access (not applicable to API-only models)
- Initial overhead: Mediation analysis adds ~20% compute vs. standard fine-tuning
- Long-term benefit: 2× efficiency gain outweighs overhead after 2-3 interventions

**Adoption Pathway:**
1. **Phase 1 (Research):** Validate framework on academic benchmarks (TruthfulQA, FairBench)
2. **Phase 2 (Industry Pilots):** Partner with LLM labs (Anthropic, OpenAI) for production model testing
3. **Phase 3 (Standardization):** Propose framework as standard methodology for alignment research (submit to alignment workshops/conferences)

**Practical Impact Summary:**
Transforms alignment engineering from **trial-and-error** (current state) to **principled intervention design** (proposed state) by identifying causal pathways and enabling targeted optimization.

---

## 3. Key Related Work

### 3.1 Representational Alignment Foundations

**[FOUNDATION-1] Sucholutsky et al. (2023) - "Getting aligned on representational alignment"**
- **Venue:** Transactions on Machine Learning Research (TMLR)
- **Citations:** 140
- **Semantic Scholar ID:** eeefe82172135523517cbe19624f2fab54e4a846
- **Relationship:** **Primary Foundation** - provides unifying framework and taxonomy
- **Key Contribution:** Surveys representational alignment across cognitive science, neuroscience, ML; identifies causal mechanism as open problem
- **How We Build On:** We formalize the causal mechanism they identified as missing using mediation analysis
- **Cited For:** Gap identification, framework positioning, interdisciplinary context

---

**[FOUNDATION-2] Williams et al. (2021) - "Generalized Shape Metrics on Neural Representations"**
- **Venue:** NeurIPS
- **Citations:** 134
- **SS ID:** 325100e605264947276cab315a6a97ea6fb6a097
- **Relationship:** **Mathematical Foundation** - metric spaces for representational dissimilarity
- **Key Contribution:** Defines family of metric spaces satisfying triangle inequality (enables rigorous distance comparisons)
- **How We Build On:** Use their CKA formulation as mediator measurement method (M₁)
- **Cited For:** Representational similarity metric theory, mathematical rigor

---

### 3.2 Alignment Metrics and Measurement

**[METRIC-1] Kornblith et al. (2019) - "Similarity of Neural Network Representations Revisited"**
- **Venue:** ICML
- **Citations:** ~800 (seminal work)
- **Relationship:** **Methodological Basis** - introduced CKA metric
- **Key Contribution:** Centered Kernel Alignment (CKA) outperforms CCA for representation comparison
- **How We Build On:** Use CKA as primary mediator measurement (M₁: geometric structure)
- **Cited For:** CKA methodology, kernel methods for representational similarity

---

**[METRIC-2] Bo & Khosla (2024) - "Evaluating Representational Similarity Measures from the Lens of Functional Correspondence"**
- **Venue:** Cognitive Computational Neuroscience 2025
- **Citations:** 7
- **SS ID:** 30e75408586e8ff6996049e4fc3c26c4867a6547
- **Relationship:** **Empirical Motivation** - shows geometric metrics correlate with behavior
- **Key Contribution:** CKA and Procrustes excel at predicting behavioral outcomes
- **How We Build On:** Their correlation findings motivate our causal hypothesis (correlation → causation gap)
- **Cited For:** Evidence that geometric representational features predict functional outcomes

---

**[METRIC-3] Williams (2024) - "Equivalence between RSA, CKA, and CCA"**
- **Venue:** bioRxiv
- **Citations:** 18
- **SS ID:** 7ad2a5214643b02167635afe0ec01bf6a1c96d65
- **Relationship:** **Methodological Clarification** - shows CKA-RSA equivalence
- **Key Contribution:** Demonstrates CKA and RSA produce equivalent results with mean-centering
- **How We Build On:** Justifies CKA choice (equivalent to neuroscience standard RSA)
- **Cited For:** Metric unification, bridge between ML and neuroscience methods

---

**[METRIC-4] Murphy et al. (2024) - "Correcting Biased CKA Measures in Biological and Artificial Neural Networks"**
- **Venue:** bioRxiv
- **Citations:** 9
- **SS ID:** 9d7635db800929e947b8dbbf7ea00b1e33dfcc95
- **Relationship:** **Methodological Warning** - identifies CKA bias in neural data
- **Key Contribution:** Biased CKA fails in low-data high-dimensionality regimes (fMRI/MEG)
- **How We Build On:** Use debiased CKA when applicable; acknowledge limitation
- **Cited For:** CKA bias correction, scope boundary (low-data settings excluded)

---

### 3.3 Representational-Behavioral Alignment Evidence

**[EVIDENCE-1] Dapello et al. (2022) - "Aligning Model and Macaque IT Cortex Representations Improves Behavioral Alignment and Adversarial Robustness"**
- **Venue:** bioRxiv
- **Citations:** 49
- **SS ID:** 4ce6d229d5f44239c948fd56ad744c012aae22e0
- **Relationship:** **Empirical Inspiration** - shows representational alignment → robustness
- **Key Contribution:** Fine-tuning models to align with macaque IT representations improves human behavioral alignment (r=0.68) and adversarial robustness
- **How We Build On:** Formalize their empirical observation as causal mediation hypothesis
- **Cited For:** Evidence for T→M→Y pathway (alignment intervention → representational change → behavioral outcome)

---

**[EVIDENCE-2] Sucholutsky & Griffiths (2023) - "Alignment with human representations supports robust few-shot learning"**
- **Venue:** NeurIPS
- **Citations:** 35
- **SS ID:** 7026fcb7e6df84a4c873f77be1e8d260a516cc62
- **Relationship:** **Practical Motivation** - representational alignment enables few-shot learning
- **Key Contribution:** Information-theoretic analysis predicts U-shaped relationship between human alignment and few-shot performance
- **How We Build On:** Demonstrates practical value of representational alignment; our framework explains mechanism
- **Cited For:** Behavioral benefits of representational alignment

---

**[EVIDENCE-3] Ogg et al. (2024) - "A Flexible Method for Behaviorally Measuring Alignment Between Human and Artificial Intelligence Using RSA"**
- **Venue:** arXiv
- **Citations:** 3
- **SS ID:** 2c510068273b5e9b5448d0079289f62ad259b079
- **Relationship:** **Methodological Complement** - behavioral measurement of human-AI alignment
- **Key Contribution:** GPT-4o shows strongest representational alignment with humans in text processing
- **How We Build On:** Their behavioral measurement methods inform our outcome variable Y specifications
- **Cited For:** Human-AI alignment measurement, behavioral similarity quantification

---

### 3.4 Intervention Methods (Gap 1 Context)

**[INTERVENTION-1] Bhattarai et al. (2025) - "Knowledge distillation through geometry-aware representational alignment"**
- **Venue:** arXiv
- **Citations:** 0 (recent)
- **SS ID:** 9bb98ca3db8af6094ddfa0fac674a95649ae5fc2
- **Relationship:** **Only Prior Intervention Work** - rare example of alignment-targeted method
- **Key Contribution:** Procrustes distance + Frobenius norm of Feature Gram Matrix for distillation → 2% task improvement
- **How We Build On:** Demonstrates feasibility of geometry-aware interventions; our framework quantifies causal effects
- **Cited For:** Proof-of-concept for systematic alignment intervention

---

**[INTERVENTION-2] Zou et al. (2023) - "Representation Engineering: A Top-Down Approach to AI Transparency"**
- **Venue:** arXiv (RepE paper)
- **Citations:** ~50 (estimated, widely used)
- **Relationship:** **Validation Method** - provides intervention technique for mediator validation
- **Key Contribution:** Activation steering via learned representation directions
- **How We Build On:** Use RepE for mediator sufficiency validation (intervene on M, measure ΔY)
- **Cited For:** Representation intervention methodology

---

### 3.5 Causal Inference Foundations (Cross-Domain)

**[CAUSAL-1] VanderWeele & Tchetgen (2021) - "Causal mediation analysis in the multilevel intervention and multicomponent mediator case"**
- **Domain:** Epidemiology/Statistics
- **Relationship:** **Methodological Foundation** - multilevel mediation framework
- **Key Contribution:** Natural Direct/Indirect Effect decomposition for multi-stage causal chains
- **How We Build On:** Adapt NIE/NDE framework to DL context (T→M→Y)
- **Cited For:** Causal mediation theory, effect decomposition

---

**[CAUSAL-2] Imai et al. (2010) - "Identification, Inference and Sensitivity Analysis for Causal Mediation Effects"**
- **Venue:** Statistical Science
- **Citations:** ~2000 (foundational)
- **Relationship:** **Methodological Foundation** - sequential ignorability framework
- **Key Contribution:** Establishes identification assumptions for causal mediation (sequential ignorability)
- **How We Build On:** Use their identification framework; adapt sensitivity analysis to DL
- **Cited For:** Causal identification theory, sequential ignorability assumptions

---

**[CAUSAL-3] Cinelli & Hazlett (2020) - "Making Sense of Sensitivity: Extending Omitted Variable Bias"**
- **Venue:** Journal of the Royal Statistical Society (Series B)
- **Citations:** ~300
- **SS ID:** [supplementary search result]
- **Relationship:** **Critical Methodological Addition** - resolves assumption validation gap
- **Key Contribution:** Sensitivity bounds via partial R² of unmeasured confounders
- **How We Build On:** Apply their sensitivity analysis to DL alignment context; report R² bounds
- **Cited For:** Sensitivity analysis methodology, assumption robustness quantification

---

**[CAUSAL-4] Huang et al. (2021) - "High-dimensional mediation analysis in survival models"**
- **Domain:** Biostatistics
- **Citations:** ~40
- **SS ID:** [supplementary search result]
- **Relationship:** **Methodological Solution** - addresses high-dimensional mediator challenge
- **Key Contribution:** LASSO regularization for mediator selection when p >> n
- **How We Build On:** Apply LASSO to select top-K mediators from neural network activations
- **Cited For:** High-dimensional mediation methods

---

**[CAUSAL-5] Wang et al. (2017) - "Causal mediation analysis for survival data with continuous mediators"**
- **Domain:** Biostatistics
- **SS ID:** [supplementary search result]
- **Relationship:** **Methodological Solution** - addresses continuous intervention challenge
- **Key Contribution:** Generalized propensity score for continuous treatment mediation
- **How We Build On:** Apply to continuous alignment interventions (RLHF KL penalty λ)
- **Cited For:** Continuous treatment mediation estimators

---

### 3.6 Alignment Methods (Intervention Context)

**[ALIGNMENT-1] Ouyang et al. (2022) - "Training language models to follow instructions with human feedback" (InstructGPT)**
- **Venue:** NeurIPS
- **Citations:** ~3000
- **Relationship:** **Intervention Specification** - RLHF methodology
- **Key Contribution:** RLHF pipeline for aligning LLMs with human preferences
- **How We Build On:** Use RLHF as primary intervention T in our framework
- **Cited For:** Alignment intervention operationalization

---

**[ALIGNMENT-2] Rafailov et al. (2023) - "Direct Preference Optimization: Your Language Model is Secretly a Reward Model"**
- **Venue:** NeurIPS
- **Citations:** ~500
- **Relationship:** **Alternative Intervention** - DPO as alignment method
- **Key Contribution:** DPO bypasses reward model training; directly optimizes preferences
- **How We Build On:** DPO as alternative intervention T (compare NIE across RLHF vs. DPO)
- **Cited For:** Alignment intervention diversity

---

### 3.7 Value Alignment Benchmarks

**[BENCHMARK-1] Lin et al. (2022) - "TruthfulQA: Measuring How Models Mimic Human Falsehoods"**
- **Venue:** ACL
- **Citations:** ~400
- **Relationship:** **Outcome Measurement** - truthfulness benchmark
- **Key Contribution:** 817-question benchmark across 38 categories for factual accuracy
- **How We Build On:** Use TruthfulQA as outcome variable Y₁ (truthfulness)
- **Cited For:** Truthfulness measurement, outcome operationalization

---

**[BENCHMARK-2] Zou et al. (2023) - "Universal and Transferable Adversarial Attacks on Aligned Language Models" (AdvBench)**
- **Venue:** arXiv
- **Citations:** ~200
- **Relationship:** **Outcome Measurement** - safety benchmark
- **Key Contribution:** Adversarial prompts for testing safety refusal
- **How We Build On:** Use AdvBench refusal rate as outcome variable Y₃ (safety)
- **Cited For:** Safety measurement

---

### 3.8 Contrast with Causal Tracing Methods

**[CONTRAST-1] Meng et al. (2022) - "Locating and Editing Factual Associations in GPT"**
- **Venue:** NeurIPS
- **Citations:** ~300
- **Relationship:** **Methodological Contrast** - intervention-based but not mediation
- **Key Contribution:** Causal tracing via activation patching to locate factual knowledge
- **Difference from Ours:** Intervention-only approach (no NIE/NDE decomposition, no quantification of mediation proportion)
- **Cited For:** Contrast between causal intervention and formal mediation analysis

---

**[CONTRAST-2] Geiger et al. (2023) - "Causal Abstractions of Neural Networks"**
- **Venue:** NeurIPS
- **Citations:** ~80
- **Relationship:** **Methodological Complement** - causal graphs for interpretability
- **Key Contribution:** Formalizes causal abstractions via interchange intervention accuracy (IIA)
- **Difference from Ours:** Focuses on causal abstraction alignment, not mediation quantification
- **Cited For:** Alternative causal framework in DL interpretability

---

### 3.9 Citation Gap Summary

**Gaps Filled:**
- ✅ Representational alignment foundations (Sucholutsky, Williams)
- ✅ Alignment metrics (CKA, RSA, Procrustes)
- ✅ Empirical representational-behavioral evidence (Dapello, Bo & Khosla, Ogg)
- ✅ Causal mediation theory (VanderWeele, Imai, Cinelli, Huang, Wang)
- ✅ Alignment interventions (RLHF, DPO)
- ✅ Value alignment benchmarks (TruthfulQA, AdvBench)

**Gaps to Address in Full Paper:**
- [ ] Additional fairness benchmarks (FairBench details, demographic parity literature)
- [ ] Mechanistic interpretability work (Anthropic alignment team, Elhage et al. SoLU)
- [ ] Alternative representation engineering methods (concept bottleneck models, steering vectors)
- [ ] Cross-domain causal inference applications to ML (if any exist)

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence): Representational Mediation Effect Exists**

**Sub-Hypothesis Statement:**
Alignment interventions (RLHF, DPO) produce measurable changes in representational features (geometric structure, attention patterns, sparse features) that are statistically significant and precede behavioral changes.

**Testable Claim:**
- ΔM (representational change from T=0 to T=1) is significantly different from zero: p < 0.05
- Temporal ordering: ΔM observable at training step t₁ < ΔY observable at inference time t₂
- Effect size: Cohen's d ≥ 0.5 (medium effect) for representational shift

**Measurement:**
- **M₁:** CKA between base model (T=0) and aligned model (T=1) layers; expect ΔCKA ∈ [0.2, 0.5]
- **M₂:** Frobenius norm of attention matrix difference; expect Δ_attn > 0 with p < 0.05
- **M₃:** LASSO-selected features differ between T=0 and T=1; expect ≥30% feature turnover

**Verification Experiment:**
1. Train LLaMA-2-7B with RLHF (λ=0.1)
2. Measure M at training checkpoints (every 1000 steps)
3. Statistical test: Paired t-test comparing M(baseline) vs. M(aligned)
4. Success: p < 0.05 AND Cohen's d ≥ 0.5 AND temporal precedence confirmed

---

**SH2 (Mechanism): Representational Changes Mediate Behavioral Outcomes**

**Sub-Hypothesis Statement:**
The causal pathway from alignment intervention to behavioral outcomes flows primarily through representational changes, quantified by Natural Indirect Effect (NIE) accounting for ≥60% of total effect.

**Testable Claim:**
- NIE / Total Effect ≥ 0.60 for ≥2/3 outcome variables (truthfulness, fairness, safety)
- Mediator intervention (RepE) produces behavioral changes matching predicted NIE: |ΔY_actual - NIE| / NIE < 10%
- Direct effect (NDE) is ≤40% of total effect

**Measurement:**
- Estimate NIE using Wang et al. (2017) continuous treatment estimator
- Bootstrap 95% CI for NIE/TE proportion
- Representation engineering validation: Steer activations toward M*, measure ΔY

**Verification Experiment:**
1. Randomized pilot: Assign RLHF interventions (3 reward types) to LLaMA-2-7B
2. Mediation analysis: Estimate NIE, NDE, Total Effect for each outcome Y
3. Mediator validation: Apply RepE on M, compare ΔY_actual to NIE_pred
4. Success: NIE/TE ≥ 0.60 with CI_lower > 0.50 AND RepE validation error < 10%

---

**SH3 (Comparison): Causal Framework Outperforms Correlational Baseline**

**Sub-Hypothesis Statement:**
The causal mediation framework provides superior intervention guidance compared to correlational analysis, achieving 2× higher intervention efficiency (behavioral improvement per unit representational change).

**Testable Claim:**
- **Targeted intervention** (on high-NIE mediators): Efficiency = ΔY / ΔM
- **Generic intervention** (standard fine-tuning): Efficiency_baseline = ΔY_baseline / ΔM_baseline
- Efficiency ratio: Efficiency_targeted / Efficiency_baseline ≥ 2.0

**Measurement:**
- Identify top-20% mediators by NIE contribution (LASSO ranking)
- Apply RepE ONLY on top-20% features → measure ΔY_targeted
- Apply standard fine-tuning → measure ΔY_baseline
- Compute efficiency ratio

**Verification Experiment:**
1. Baseline: Fine-tune LLaMA-2-7B for 1000 steps → measure ΔY_baseline, ΔM_baseline
2. Targeted: RepE intervention on top-20% LASSO features → measure ΔY_targeted, ΔM_targeted
3. Compute efficiencies: ΔY / ΔM for both conditions
4. Success: Efficiency_targeted / Efficiency_baseline ≥ 2.0 for ≥2/3 outcomes

**Alternative Comparison:**
- **Correlational approach (SOTA):** Measure CKA correlation with behavioral outcome; no causal decomposition
- **Our approach:** NIE/NDE decomposition with sensitivity bounds; targeted mediator intervention
- **Advantage:** Our approach provides (1) causal quantification, (2) intervention targets, (3) assumption transparency

---

### Readiness Checklist

**✅ Core Hypothesis Clarity**
- [x] Main hypothesis formalized with quantitative predictions (NIE/TE ≥ 0.60)
- [x] Alternative hypothesis (H0) clearly stated (NIE/TE < 0.30)
- [x] Causal mechanism diagram provided (T → M → Y with direct path)
- [x] All variables operationalized with measurement methods

**✅ Assumption Transparency**
- [x] 5 key assumptions identified (sequential ignorability, mediator sufficiency, temporal ordering, SUTVA, monotonicity)
- [x] Validation strategies specified for each assumption
- [x] Expected violations and mitigations documented

**✅ Scope Definition**
- [x] Applies to: Post-training LLM alignment (≥7B parameters, transformer architectures)
- [x] Does NOT apply to: Black-box models, pretraining, discrete architectural changes, emergent capabilities
- [x] Limitations acknowledged (5 limitations: confounding sensitivity, measurement error, scale generalization, cross-domain transfer, non-linearity)

**✅ Testable Predictions**
- [x] 4 primary/secondary predictions with quantitative thresholds
- [x] 5 falsification criteria specified
- [x] Statistical tests defined (t-tests, bootstrap CIs, permutation tests)

**✅ SOTA Baseline Comparison**
- [x] Current SOTA identified (correlational CKA/RSA analysis)
- [x] Benchmarks specified (TruthfulQA, FairBench, AdvBench)
- [x] Advantage over SOTA quantified (causal claims, intervention efficiency, assumption transparency)

**✅ Statistical Design**
- [x] 4-phase experimental design (synthetic, randomized pilot, RepE validation, observational + sensitivity)
- [x] Sample sizes calculated (N=116 models total, 560 GPU-hours, <$5K compute)
- [x] Statistical tests specified for each phase
- [x] Success criteria defined

**✅ Contribution Clarity**
- [x] Theoretical: Causal mediation framework for representational alignment (novelty: first application)
- [x] Methodological: Continuous treatment mediation + LASSO + sensitivity analysis (4 novel adaptations)
- [x] Practical: Targeted interventions with 2× efficiency; predictive modeling; transparent assumption reporting

**✅ Related Work Coverage**
- [x] 20+ key papers cited across 9 categories
- [x] Relationship to each paper specified (foundation, inspiration, methodology, contrast)
- [x] Citation gaps identified (fairness benchmarks, mechanistic interpretability)

**✅ Phase 2B Decomposition**
- [x] 3 sub-hypotheses defined (SH1: existence, SH2: mechanism, SH3: comparison)
- [x] Each sub-hypothesis has testable claims and verification experiments
- [x] Sub-hypotheses cover: (1) representational change detection, (2) mediation quantification, (3) practical superiority

---

### Open Questions

**OQ1: Optimal Mediator Specification**
- **Question:** Which mediator specification (CKA, attention, LASSO features, or ensemble) provides most accurate NIE estimates across diverse alignment objectives?
- **Why Important:** Mediator measurement error directly affects causal estimate reliability
- **Resolution Approach:** Phase 3 (RepE validation) will empirically test each mediator specification; select best-performing for Phase 4
- **Expected Answer:** Likely ensemble (combining M₁, M₂, M₃) will outperform single specifications; LASSO may capture local features missed by CKA/attention

---

**OQ2: Sensitivity Threshold Interpretation**
- **Question:** What level of unmeasured confounding (R² threshold) is "acceptable" for causal claims in DL alignment research?
- **Why Important:** Determines whether sensitivity bounds are reassuring or concerning
- **Resolution Approach:** Compare R² thresholds to plausible confounding scenarios (e.g., estimate training data bias R² empirically)
- **Expected Answer:** R² ≥ 0.15 likely acceptable (training data confounding typically R² ∈ [0.10, 0.20] based on domain knowledge); if threshold < 0.10, causal claims fragile

---

**OQ3: Scale-Dependent Causal Pathways**
- **Question:** Do causal mediation pathways differ between 7B and 70B models (emergent phenomena)?
- **Why Important:** Framework validated on 7B may not generalize if larger models exhibit qualitatively different alignment mechanisms
- **Resolution Approach:** Phase 4 includes 70B models (if compute allows); compare NIE/TE estimates across scales
- **Expected Answer:** Core mechanism likely generalizes (representational mediation remains dominant), but specific mediators may differ (e.g., different layers become important at larger scale)

---

**OQ4: Cross-Domain Transfer (Vision/Multimodal)**
- **Question:** Can framework transfer to vision models or multimodal LLMs with adapted mediator specifications?
- **Why Important:** Determines framework generality beyond text-only LLMs
- **Resolution Approach:** Out-of-scope for current hypothesis (text LLMs only); future work could adapt mediators (convolutional feature maps for vision)
- **Expected Answer:** Conceptual framework generalizes (NIE/NDE decomposition applies to any T→M→Y chain), but mediator measurement requires domain-specific design

---

**OQ5: Non-Linear Mediation Extensions**
- **Question:** Does linear mediation assumption hold, or are non-linear extensions (generalized additive models) needed?
- **Why Important:** Non-linearity bias NIE/NDE estimates if true relationship is non-linear
- **Resolution Approach:** Phase 2 randomized pilot tests linearity assumption (plot M vs. Y); if non-linear, extend to GAMs in Phase 4
- **Expected Answer:** Approximately linear for moderate intervention intensities (λ ∈ [0.01, 1.0]); may become non-linear at extreme values (λ > 2.0)

---

**OQ6: Multi-Mediator Interactions**
- **Question:** Do mediators (CKA, attention, LASSO) interact synergistically, or are effects additive?
- **Why Important:** Affects optimal intervention design (target single mediator vs. multiple simultaneously)
- **Resolution Approach:** Test multi-mediator models (M₁ + M₂ + M₃) vs. single-mediator models; check for interaction terms
- **Expected Answer:** Likely modest positive interactions (aligning both geometry AND attention more effective than either alone), but effects mostly additive

---

**OQ7: Temporal Dynamics of Mediation**
- **Question:** At what training step does representational mediation become dominant (early vs. late training)?
- **Why Important:** Informs when to measure mediators for maximum signal
- **Resolution Approach:** Measure NIE at multiple training checkpoints (every 1000 steps); identify when NIE/TE stabilizes
- **Expected Answer:** Mediation likely emerges mid-training (after 30-50% of total steps); early training dominated by direct effects (memorization), late training shows stable representational mediation

---

**Open Questions Summary:**
- **Critical for Phase 2B:** OQ1 (mediator specification), OQ2 (sensitivity threshold)
- **Exploratory (future work):** OQ3 (scale), OQ4 (cross-domain), OQ5 (non-linearity), OQ6 (interactions), OQ7 (temporal dynamics)
- **Resolution Timeline:** OQ1-OQ2 resolved in Phase 3-4 experiments; OQ3-OQ7 may extend beyond single hypothesis testing

---

*Generated using YouRA Research Phase 2A Extended Workflow (YOLO MODE - Automated)*
*2026-02-06*
*Source: 02a_round_1_discussion.md (Round 1 - Causal Mediation Framework)*
*Confidence: 0.85 (High)*
*Status: READY FOR PHASE 2B VERIFICATION PLANNING*
