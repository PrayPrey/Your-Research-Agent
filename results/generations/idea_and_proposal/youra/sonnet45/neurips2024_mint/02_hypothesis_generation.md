# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-01
**Confidence Level:** 0.87

**Main Hypothesis:**
IF we use sparse autoencoder (SAE) features to guide the design and validation of activation steering interventions (rather than using heuristic or probe-only approaches), THEN we can achieve more interpretable, targeted, and capability-preserving control over foundation model behavior across multiple objectives (safety, factuality, style), BECAUSE SAE features provide monosemantic, causally-relevant control dimensions that enable systematic intervention design and feature-space validation of intervention effects.

**Alternative Hypothesis (H0):**
Heuristic activation steering methods (SafeSteer-style category contrasts) or probe-only approaches (Dubey 2025) achieve equivalent control effectiveness, interpretability, and capability preservation compared to SAE-guided steering, rendering the additional computational cost of SAE training and feature-space validation unjustified.

### 1.2 Variables

| Variable Type | Variable Name | Operationalization | Measurement Method | Source/Justification |
|---------------|---------------|---------------------|-------------------|---------------------|
| **Independent Variable (IV)** | Intervention Design Method | Categorical: (1) SAE-guided (our framework), (2) Heuristic steering (SafeSteer baseline), (3) Probe-only (Dubey baseline), (4) No intervention (control) | Framework selection per experimental condition | Framework comparison is core hypothesis test |
| **Mediating Variable (MV)** | Feature Causality | Continuous: Causal effect size from activation patching (measured as ∆logit when ablating SAE feature) | Activation patching with mean ablation; measure output logit change on validation set | Campbell 2023 methodology; validates SAE features are causal, not just correlational |
| **Mediating Variable (MV)** | Feature Interpretability | Binary: Monosemantic (single concept) vs. Polysemantic (multiple concepts) | Human annotation of top-10 activating examples per feature; inter-rater agreement >0.7 required | Abdulaal 2024 SAE-Rad protocol; critical for "interpretability-guided" claim |
| **Dependent Variable (DV1)** | Control Effectiveness | Continuous: Task-specific metric (Toxicity reduction %, Factuality accuracy %, Style transfer success rate) | Safety: Perspective API toxicity score; Factuality: TruthfulQA accuracy; Style: Sentiment classifier agreement | Ghosh 2025 SafeSteer evaluation metrics |
| **Dependent Variable (DV2)** | Capability Preservation | Continuous: Benchmark performance retention (MMLU, BBH scores pre/post intervention) | Standard benchmark evaluation; compute % retention: (post_score / pre_score) × 100 | Dubey 2025 capability assessment; critical for practical deployment |
| **Dependent Variable (DV3)** | Interpretability Gain | Ordinal: Expert rating (1-5 scale) of intervention transparency and debugging ease | Expert survey (5 MI researchers) rating: "How well can you understand WHY this intervention works?" | Novel metric for interpretability-first framework value |
| **Control Variable (CV)** | Model Scale | Fixed: GPT-2-large (774M) or LLaMA-7B | Model selection at experiment start; use same model across all conditions | Scoped to demonstrated SAE feasibility scale (Abdulaal 2024, Villegas Garcia 2025) |
| **Control Variable (CV)** | Intervention Strength | Continuous: Steering vector scaling coefficient (grid search 0.1-2.0) | Optimize per condition to achieve target control level (e.g., 80% toxicity reduction), then fix for comparison | Fair comparison requires equivalent control strength across methods |

### 1.3 Causal Mechanism

**Mechanism Chain:**

```
SAE Feature Discovery (Phase 1)
   ↓ (Causal Link 1: Feature Identification)
Identified Monosemantic Features Causally Relevant to Control Objective
   ↓ (Causal Link 2: Feature-Guided Design)
Steering Vectors Computed in SAE Feature Space (Not Raw Activation Space)
   ↓ (Causal Link 3: Interpretable Intervention)
Feature-Space Steering → Activation Space Projection → Model Generation
   ↓ (Causal Link 4: Feature-Space Validation)
Monitor SAE Feature Activations During Generation
   ↓ (Causal Link 5: Iterative Refinement)
Detect Unintended Feature Changes → Refine Steering → Improved Control
```

**Evidence for Causal Links:**

**Link 1 Evidence (Feature Identification):**
- Villegas Garcia 2025: SAE features in protein LMs correlate with zinc finger domains; features guide targeted generation
- Abdulaal 2024: SAE features in vision transformers interpretable to radiologists; features predict report content
- MECHANISTIC GROUNDING: SAE sparsity constraint (L1 penalty) encourages monosemantic feature learning (Sharkey et al. 2023 theoretical analysis)

**Link 2 Evidence (Feature-Guided Design):**
- Villegas Garcia 2025: Directly manipulates SAE features to steer protein generation toward target domains
- Novel contribution: We extend feature manipulation from single-domain (protein) to multi-objective LLM framework

**Link 3 Evidence (Interpretable Intervention):**
- Dubey 2025: Linear probes identify bias-relevant dimensions; steering vectors computed from probe directions
- SafeSteer (Ghosh 2025): Category-specific steering computed via contrastive examples
- Our framework: Replaces heuristic contrast with SAE feature-space contrast (interpretable dimensions)

**Link 4 Evidence (Feature-Space Validation):**
- Campbell 2023: Activation patching validates causal relevance of identified attention heads
- Our framework: Extends patching from analysis to validation (verify SAE features modulate as intended during steering)

**Link 5 Evidence (Iterative Refinement):**
- SafeSteer (Ghosh 2025): Notes steering can fail but lacks interpretable debugging mechanism
- Our framework: Feature-space monitoring enables interpretable diagnosis of steering failures (e.g., "Feature 42 not suppressed → steering vector insufficient in that dimension")

**Key Tension:**

**Computational Cost vs. Interpretability Benefit**
- SAE training requires activation dataset collection + gradient descent (one-time cost: ~GPU-hours for GPT-2-large)
- SAE inference adds encoder forward pass during validation (~10-20% latency overhead)
- **Tension:** Does interpretability gain justify this cost vs. lightweight probe-only or heuristic methods?
- **Resolution Strategy:** Measure interpretability gain quantitatively (expert ratings) + show capability preservation improves with SAE validation (fewer unintended side effects)

### 1.4 Key Assumptions

| Assumption | Type | Justification | Risk if Violated | Mitigation |
|------------|------|---------------|------------------|------------|
| **A1:** SAE features are more monosemantic than raw activation dimensions | THEORETICAL | Sparse coding theory (Olshausen & Field 1996); recent SAE work shows improved interpretability (Abdulaal 2024) | If features are polysemantic, interpretability-guided design loses advantage | Measure interpretability explicitly (human annotation); report polysemantic features as limitation |
| **A2:** Causally-relevant features for control objectives are discoverable via probing + patching | METHODOLOGICAL | Campbell 2023 localized lying behavior to specific heads; Dubey 2025 found bias-relevant probe directions | If features are causal for one task but not others, framework applicability limited | Test across 3 objectives (safety, factuality, style); report per-objective success rates |
| **A3:** Feature-space validation detects capability degradation earlier than end-task benchmarks | EMPIRICAL | Novel assumption — no direct prior evidence | If feature monitoring doesn't correlate with capability degradation, validation loop provides no early warning | Validate correlation: Feature shift magnitude vs. benchmark score drop; include benchmark validation regardless |
| **A4:** Multi-objective steering doesn't cause catastrophic feature interference | SCALABILITY | SafeSteer (Ghosh 2025) shows category-specific steering works, but doesn't test multi-objective | If steering for safety corrupts factuality features, multi-objective framework fails | Measure cross-objective interference explicitly (safety steering → factuality benchmark); use feature subset selection if interference detected |
| **A5:** SAE training converges to stable, reproducible features across random seeds | TECHNICAL | Standard ML reproducibility assumption; Abdulaal 2024 and Villegas Garcia 2025 don't report major instability | If SAE features are highly seed-dependent, framework reproducibility compromised | Train SAEs with 3 random seeds; measure feature consistency via activation correlation across seeds |

### 1.5 Scope & Boundaries

**Scope:**

- **Models:** GPT-2-large (774M) or LLaMA-7B
  *Rationale:* SAE feasibility demonstrated at this scale (Abdulaal 2024 on vision transformer ~100M, Villegas Garcia 2025 on ESM-2 8M). GPT-2-large provides open access for reproducibility.

- **Control Objectives:** (1) Safety (toxicity reduction), (2) Factuality (hallucination mitigation), (3) Style (sentiment control)
  *Rationale:* Safety and factuality = high practical value (Ghosh 2025, Dubey 2025 address these). Style = proof of generality (demonstrates framework not locked to safety domain).

- **Intervention Type:** Activation steering (additive vectors to residual stream activations)
  *Rationale:* Lightweight, inference-time intervention. Excludes weight-space interventions (LoRA) to isolate interpretability→steering mechanism.

- **Validation Layers:** Middle-to-late transformer layers (e.g., layers 15-20 for GPT-2-large)
  *Rationale:* Campbell 2023 found lying behavior in layers 15-25 of LLaMA-70B. Dubey 2025 used middle layers for bias detection.

**Out of Scope:**

- **Large-scale models (70B+):** Computational cost of SAE training on 70B activations exceeds standard research budgets. Future work: Selective layer SAEs, sparse caching.
- **Weight-space interventions:** LoRA, fine-tuning excluded to isolate activation-space steering mechanism.
- **Real-time deployment optimization:** Framework focuses on proof-of-concept. Production deployment (low-latency inference) is future engineering work.
- **Adversarial robustness:** Testing against adversarial prompts (jailbreaks) is important but out of initial scope. Focus on standard evaluation sets.

**Boundary Conditions:**

- If SAE features are <60% monosemantic (per human evaluation), interpretability claim weakens → report as limitation
- If activation patching shows features have <0.2 causal effect size, framework's causal grounding fails → abort that control objective
- If capability preservation <95% on MMLU/BBH, framework unsuitable for production → investigate feature interference causes

### 1.6 Testable Predictions

**Primary Prediction:**

**P1 (Control + Capability):** SAE-guided steering will achieve equivalent or better control effectiveness (toxicity reduction, factuality accuracy, style transfer) compared to heuristic and probe-only baselines, WHILE maintaining ≥98% capability preservation on MMLU and BBH benchmarks, measured as (post-intervention score / pre-intervention score) ≥ 0.98.

*Statistical Test:* Two-tailed t-test comparing SAE-guided vs. baselines on capability retention. Significance: p < 0.05. Expected effect size: d ≥ 0.5 (medium effect favoring SAE-guided).

**Secondary Predictions:**

**P2 (Interpretability Gain):** Expert evaluators will rate SAE-guided steering significantly higher (mean rating ≥ 4.0/5.0) on interpretability and debugging ease compared to heuristic (expected ≤ 2.5/5.0) and probe-only (expected ≤ 3.0/5.0) methods.

*Statistical Test:* Friedman test (non-parametric repeated measures) across 5 experts rating 3 methods. Post-hoc Wilcoxon signed-rank tests with Bonferroni correction. Significance: p < 0.05.

**P3 (Multi-Objective Interference):** Cross-objective capability degradation (e.g., safety steering → factuality score drop) will be ≤5% for SAE-guided steering, compared to ≥10% expected for heuristic methods lacking feature-space validation.

*Statistical Test:* One-way ANOVA comparing cross-objective degradation across methods. Significance: p < 0.05. Expected effect size: η² ≥ 0.14 (large effect).

**Falsification Criteria:**

The hypothesis is **FALSIFIED** if any of the following occur:

1. **F1 (No Control Advantage):** SAE-guided steering fails to achieve statistically significant improvement (p ≥ 0.05) in EITHER control effectiveness OR capability preservation compared to at least one baseline.

2. **F2 (Interpretability Failure):** Expert ratings show no significant difference (p ≥ 0.05) between SAE-guided and probe-only methods on interpretability, indicating SAE features provide no practical interpretability gain.

3. **F3 (Feature Polysemanticity):** <50% of top-10 SAE features (ranked by causal effect size) are monosemantic per human evaluation, undermining core "interpretability-guided" claim.

4. **F4 (Catastrophic Interference):** Multi-objective steering causes >15% capability degradation on any cross-objective benchmark, making framework impractical for multi-objective deployment.

### 1.7 SOTA Baseline (Comparison Mode)

**Baseline Methods:**

| Method | Reference | Implementation Details | Why This Baseline? |
|--------|-----------|------------------------|---------------------|
| **Heuristic Steering** | SafeSteer (Ghosh 2025) | Category-specific steering vectors via gradient-free contrastive prompts (harmful vs. neutral examples) | Current SOTA for fine-grained safety steering; no interpretability layer |
| **Probe-Only Steering** | Dubey (2025) | Linear probes on activations → steering vectors from probe directions | Closest to SAE-guided (uses interpretability) but no SAE features; tests SAE's added value |
| **No Intervention** | (Control) | Standard model generation without steering | Establishes baseline performance and control necessity |

**SOTA Performance Benchmarks:**

- **SafeSteer (Ghosh 2025):** 87% toxicity reduction on RealToxicityPrompts; maintains 96% text quality (MAUVE score)
- **Dubey (2025):** 94% bias detection accuracy (linear probe); 85% bias mitigation via steering; MMLU score retention ~97%

**Target Performance:**

- **Control Effectiveness:** Match or exceed SafeSteer's 87% toxicity reduction
- **Capability Preservation:** Exceed Dubey's 97% MMLU retention → Target ≥98%
- **Interpretability:** No SOTA quantitative benchmark exists; establish baseline with our expert rating protocol

### 1.8 Statistical Verification Design

**Experimental Design:** 2×3 factorial + control
- **Factor 1 (Model):** 2 levels — GPT-2-large, LLaMA-7B
- **Factor 2 (Method):** 3 levels — SAE-guided, Heuristic, Probe-only
- **Control:** No intervention baseline
- **Total conditions:** 2 models × 4 methods = 8 conditions

**Sample Size Calculation:**
- **Power analysis:** Target power = 0.80, α = 0.05, expected effect size d = 0.5 (medium)
- **Result:** n = 64 evaluation prompts per condition (G*Power calculation for independent t-test)
- **Total evaluation set:** 64 prompts × 3 objectives (safety, factuality, style) = 192 prompts

**Randomization:**
- Prompts randomly assigned to conditions using stratified sampling (ensure balanced representation across topics)
- SAE training seeds randomized (3 seeds per model)
- Baseline method hyperparameters (steering strength) optimized independently per condition

**Statistical Tests:**

| Hypothesis | Test | Variables | Significance Level |
|------------|------|-----------|-------------------|
| P1 (Capability preservation) | Two-sample t-test (SAE vs. each baseline) | DV: Capability retention (%) | α = 0.05, two-tailed |
| P2 (Interpretability) | Friedman test + Wilcoxon post-hoc | DV: Expert ratings (ordinal 1-5) | α = 0.05, Bonferroni corrected |
| P3 (Multi-objective) | One-way ANOVA (method factor) | DV: Cross-objective degradation (%) | α = 0.05 |
| Feature causality (A2 validation) | Correlation analysis | IV: Activation patching effect size; DV: Control effectiveness | r > 0.5 required for causality claim |

**Confound Control:**
- **Steering strength normalized:** Optimize each method to achieve equivalent control level (e.g., 80% toxicity reduction), then compare capability preservation at that level
- **Model checkpoints fixed:** Use same pre-trained model checkpoint across all conditions
- **Evaluation metrics standardized:** Same benchmark datasets (MMLU, BBH, TruthfulQA, RealToxicityPrompts) across all methods

**Replication:**
- 3 random seeds for SAE training
- 3 random seeds for baseline method initialization
- Report mean ± std across seeds

---

## 2. Contribution Summary

**Theoretical Contributions:**

1. **Interpretability-First Intervention Paradigm:** Establishes SAE feature space as principled substrate for intervention design, moving beyond heuristic or black-box approaches. Formalizes the interpretability→intervention→validation cycle missing in prior work.

2. **Causal Feature Validation Framework:** Integrates activation patching (Campbell 2023 methodology) into intervention design, ensuring features used for steering have verified causal effects rather than mere correlations.

**Methodological Contributions:**

1. **3-Phase SAE-Guided Framework:** Systematic discover (SAE + patching) → design (feature-space steering) → validate (feature monitoring + benchmarks) methodology generalizable across control objectives.

2. **Feature-Space Steering Computation:** Novel method for computing steering vectors in SAE feature space (feature-based contrast) rather than raw activation space, enabling interpretable control dimensions.

3. **Multi-Objective Validation Protocol:** First framework to explicitly test and mitigate cross-objective interference (safety steering → factuality degradation) via feature-space monitoring.

**Practical Contributions:**

1. **Interpretable Debugging:** Feature-space monitoring enables transparent diagnosis of steering failures (e.g., "Feature 42 insufficiently suppressed") vs. black-box failure modes.

2. **Capability Preservation Mechanism:** Feature-space validation detects unintended feature changes early, enabling iterative refinement before catastrophic capability degradation.

3. **Production-Ready Validation:** Comprehensive benchmark suite (MMLU, BBH, safety metrics) ensures framework suitable for deployment, not just research demonstration.

**Novelty Claims:**

- **vs. Dubey 2025:** Extends probe-only approach to SAE features (monosemantic vs. linear combinations); adds multi-objective design; includes feature-space validation loop
- **vs. SafeSteer (Ghosh 2025):** Replaces heuristic steering with interpretability-guided design; adds causal validation (activation patching); includes capability preservation validation
- **vs. Villegas Garcia 2025:** Generalizes single-domain SAE steering (protein) to multi-objective LLM framework with systematic validation
- **vs. Campbell 2023:** Extends activation patching from analysis tool to intervention validation mechanism integrated into systematic framework

---

## 3. Key Related Work

**Direct Precursors:**

1. **Dubey, S. (2025).** *Activation Steering for Bias Mitigation: An Interpretable Approach to Safer LLMs.*
   - SS ID: 032d1e5f5e7d221f79a034e9f3af8a776b044d58
   - **Contribution:** End-to-end MI→intervention pipeline for bias; linear probes→steering vectors
   - **Limitation:** Single objective (bias); probe-only (no SAE features); no multi-objective validation
   - **How We Build On It:** Extend to SAE features, generalize to 3 objectives, add feature-space validation loop

2. **Ghosh, S., Bhattacharjee, A., Ziser, Y., & Parisien, C. (2025).** *SafeSteer: Interpretable Safety Steering with Refusal-Evasion in LLMs.*
   - SS ID: 70997a66de689b4cc70268f226b83a577822208f
   - **Contribution:** Category-specific steering for fine-grained safety; gradient-free unsupervised method
   - **Limitation:** Heuristic steering (no SAE interpretability); no capability preservation validation
   - **How We Build On It:** Add SAE-guided design for interpretability; validate capability preservation explicitly

3. **Campbell, J., Ren, R., & Guo, P. (2023).** *Localizing Lying in Llama: Understanding Instructed Dishonesty Through Prompting, Probing, and Patching.*
   - SS ID: 44348660a9b5a6a5ee83333587c64ed6cc84a0b1
   - **Contribution:** Activation patching for causal localization; 46 attention heads identified for lying
   - **Limitation:** Analysis-focused; no systematic intervention framework; single behavior (lying)
   - **How We Build On It:** Use patching as causal validation in Phase 1; extend to intervention design and multi-objective framework

4. **Abdulaal, A., Fry, H., Montana Brown, N., et al. (2024).** *An X-Ray Is Worth 15 Features: Sparse Autoencoders for Interpretable Radiology Report Generation.*
   - SS ID: daa48c314524042a3ef4b251bac914e64eb5b74d
   - **Contribution:** First SAE application to downstream task; interpretable features for medical imaging
   - **Limitation:** Single-domain (radiology); no steering mechanism; vision-language multimodal (different from LLM text)
   - **How We Build On It:** Demonstrate SAE features→task utility in NLP domain; extend to steering intervention

5. **Villegas Garcia, E. N., & Ansuini, A. (2025).** *Interpreting and Steering Protein Language Models through Sparse Autoencoders.*
   - SS ID: cc696dd165832cb1a1d21d35ea1f504fccff7fe2
   - **Contribution:** SAE features for interpretation AND steering in protein domain; demonstrates feature manipulation works
   - **Limitation:** Single-domain (protein); single-objective (zinc finger generation); no multi-objective framework
   - **How We Build On It:** Generalize SAE steering from protein to LLM; multi-objective framework with interference analysis

**Foundational Surveys:**

6. **Bereska, L., & Gavves, E. (2024).** *Mechanistic Interpretability for AI Safety - A Review.*
   - SS ID: 8b750488d139f9beba0815ff8f46ebe15ebb3e58
   - **Contribution:** Establishes MI as critical for AI safety; comprehensive survey of causally dissecting models
   - **How It Informs Our Work:** Provides theoretical foundation for interpretability-first intervention design; identifies gap in systematic MI→intervention integration

**Cross-Domain Inspiration:**

7. **Neuroscience: Sparse Coding in the Brain** (Olshausen & Field, 1996; conceptual)
   - **Transferable Principle:** Biological neurons use sparse distributed representations for efficient encoding; selective circuit interventions based on identified components
   - **How Applied:** SAE architecture mimics sparse coding; framework's 3-phase structure parallels neuroscience circuit mapping→intervention methodology

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):** SAE features are monosemantic and causally relevant for control objectives

**Sub-Hypothesis 1.1:** SAE features exhibit monosemanticity (≥60% of top-10 features interpretable as single concept)
- **Verification:** Human annotation of top-activating examples; inter-rater agreement >0.7
- **Success Criterion:** ≥60% monosemantic features
- **Estimated Effort:** 2 annotators × 10 features × 10 examples = ~200 annotations (~4 hours)

**Sub-Hypothesis 1.2:** SAE features have causal effects on model outputs (activation patching ∆logit ≥ 0.2)
- **Verification:** Activation patching ablation studies (Campbell 2023 methodology)
- **Success Criterion:** ≥70% of top-10 features show causal effect size ≥ 0.2
- **Estimated Effort:** 10 features × 64 validation prompts = ~640 forward passes (~2 GPU-hours)

**SH2 (Mechanism):** Feature-space steering achieves control via interpretable feature modulation

**Sub-Hypothesis 2.1:** Steering vectors computed in SAE feature space modulate target features as intended
- **Verification:** Feature activation monitoring during steered generation
- **Success Criterion:** Target features suppressed/amplified by ≥50% on average
- **Estimated Effort:** Track features during 192 prompt evaluations (~1 GPU-hour)

**Sub-Hypothesis 2.2:** Feature-space steering translates to effective control in output behavior
- **Verification:** Task-specific metrics (toxicity reduction, factuality accuracy, style transfer)
- **Success Criterion:** ≥80% control effectiveness (e.g., toxicity reduction)
- **Estimated Effort:** Evaluate 192 prompts × 3 objectives × 4 methods = ~2,304 evaluations (~8 hours)

**SH3 (Comparison):** SAE-guided steering outperforms baselines on capability preservation and interpretability

**Sub-Hypothesis 3.1:** SAE-guided steering maintains ≥98% capability retention (MMLU, BBH)
- **Verification:** Standard benchmark evaluation pre/post-intervention
- **Success Criterion:** (post_score / pre_score) ≥ 0.98, significantly better than baselines (p < 0.05)
- **Estimated Effort:** 2 models × 4 methods × 2 benchmarks = ~16 benchmark runs (~4 GPU-hours)

**Sub-Hypothesis 3.2:** SAE-guided steering achieves higher interpretability ratings (≥4.0/5.0)
- **Verification:** Expert survey (5 MI researchers)
- **Success Criterion:** Mean rating ≥ 4.0, significantly higher than baselines (p < 0.05)
- **Estimated Effort:** 5 experts × 3 methods × ~30 min evaluation = ~7.5 hours human time

### Readiness Checklist

✅ **Hypothesis is falsifiable:** Clear falsification criteria (F1-F4) with quantitative thresholds
✅ **Variables operationalized:** All variables have concrete measurement methods (Perspective API, TruthfulQA, MMLU, etc.)
✅ **Statistical design specified:** Power analysis complete (n=64), tests selected (t-test, Friedman, ANOVA)
✅ **Baselines identified:** 3 baseline methods with implementation details (SafeSteer, Dubey, No intervention)
✅ **Success criteria quantified:** All predictions have numerical thresholds (≥98% capability, ≥4.0/5.0 rating, etc.)
✅ **Confounds controlled:** Steering strength normalized, model checkpoints fixed, evaluation metrics standardized
✅ **Scope realistic:** Limited to GPT-2-large/LLaMA-7B (demonstrated feasibility); 70B+ noted as future work
✅ **Assumptions testable:** 5 assumptions with validation methods and risk mitigation strategies
✅ **Computational cost estimated:** SAE training ~GPU-hours, evaluation ~8 hours, benchmarks ~4 GPU-hours
✅ **Replication planned:** 3 random seeds for SAE training and baseline initialization

**Phase 2B Ready:** YES ✅

### Open Questions

**Q1 (Technical):** What is the optimal SAE hidden dimension and sparsity coefficient for GPT-2-large?
- **Resolution Strategy:** Grid search over hidden_dim ∈ {2048, 4096, 8192} and sparsity_coeff ∈ {1e-3, 1e-4, 1e-5}; select based on reconstruction loss + interpretability trade-off
- **Impact if Unresolved:** Sub-optimal SAE may yield polysemantic features → interpretability claim weakens
- **Phase to Resolve:** Phase 3 (Implementation Planning) - specify architecture before Phase 4 coding

**Q2 (Methodological):** How many top-k features should be used for steering to balance control effectiveness and interference risk?
- **Resolution Strategy:** Ablation study varying k ∈ {5, 10, 20, 50}; measure control effectiveness vs. cross-objective degradation
- **Impact if Unresolved:** Too few features → weak control; too many features → interference
- **Phase to Resolve:** Phase 2C (Experiment Design) - design ablation study protocol

**Q3 (Evaluation):** What constitutes "interpretable" for expert evaluators? Need rubric.
- **Resolution Strategy:** Develop 5-point rubric with concrete criteria (e.g., "Can you identify which concept each feature represents?" 1=No, 5=Yes for all)
- **Impact if Unresolved:** Expert ratings may be inconsistent → P2 test invalid
- **Phase to Resolve:** Phase 2C (Experiment Design) - finalize evaluation protocol before Phase 4

**Q4 (Resource):** Do we have access to 5 MI expert evaluators for interpretability rating?
- **Resolution Strategy:** Identify experts from lab/collaborators; consider crowdsourcing as backup (MTurk with qualification test)
- **Impact if Unresolved:** Cannot validate P2 (interpretability gain)
- **Phase to Resolve:** Phase 3 (Implementation Planning) - confirm resource availability

**Q5 (Scope):** Should we test on instruction-tuned models (GPT-2-XL-instruct) or base models?
- **Resolution Strategy:** Primary experiments on base models (cleaner intervention effects); secondary analysis on instruct models if time permits
- **Impact if Unresolved:** Framework applicability to production models (usually instruction-tuned) unclear
- **Phase to Resolve:** Phase 2C (Experiment Design) - finalize model selection

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-06*
