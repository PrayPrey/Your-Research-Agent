# Phase 2A: Research Discussion Log

## Research Context

**Gap Selected:** Gap 1 - Robustness-Error Detection Correlation Quantification
**Priority:** PRIMARY (Critical)
**Research Question:** How do existing error detection and correction mechanisms in LLMs correlate with model robustness across different perturbation types?

### Gap Description
No unified evaluation framework measures both robustness (across perturbation types) and error detection accuracy on same models/datasets. Error detection methods (MIND, SAC3, ARES) and robustness benchmarks exist independently, but no cross-metric correlation analysis exists.

### Key Papers from Phase 1
1. **ARES** (You et al., 2025) - 72.1% Macro-F1 on error detection, arXiv:2507.12948
2. **FactSelfCheck** (Sawczyn et al., 2025) - 35.5% factual improvement, arXiv:2503.17229
3. **SPOC** (Zhao et al., 2025) - +8.8-20% accuracy via self-correction, arXiv:2506.06923
4. **SuperCorrect** (Yang et al., 2024) - Cross-model DPO for self-correction, arXiv:2410.09008
5. **Calibration** (Minderer et al., 2021) - Architecture determines calibration, arXiv:2106.07998

### Available Implementations
- TruthfulQA (sylinrl, 911 stars)
- lm-evaluation-harness (EleutherAI, 12K+ stars)
- LettuceDetect (589 stars)
- MIND (oneal2000, 65 stars)
- SAC3 (intuit, 39 stars)

### Feasibility Constraints (Pipeline-Enforced)
- NO new benchmarks/rubrics/scoring frameworks
- NO synthetic/generated data or future data
- NO human evaluation or subjective scoring
- ONLY existing real datasets and existing benchmarks

---

## Discussion

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What if we flip the entire problem on its head? Everyone's been treating robustness and error detection as separate research tracks, but I see a fascinating opportunity for a **unified probe-based correlation framework**!

Here's my creative angle: Instead of building new benchmarks (which we can't do anyway given our constraints), what if we leverage the *internal representations* that models already produce? ARES shows 72.1% F1 on reasoning chain errors, and the calibration literature tells us architecture determines calibration properties. What if the same internal signals that indicate miscalibration also predict susceptibility to perturbations?

Imagine this: We could design a **cross-metric correlation study** using existing benchmarks (TruthfulQA, HaluEval) combined with standard adversarial perturbations (TextFooler, BERT-Attack). The hypothesis would be: *Models that exhibit higher error detection accuracy on factuality benchmarks will show stronger robustness to input perturbations, mediated by their internal confidence calibration*.

The novelty here isn't a new benchmark - it's a **new analytical lens**. We're asking whether the internal machinery that enables self-correction (like SPOC's verify-then-revise) also provides natural robustness. Cross-domain insight: this is similar to how biological immune systems use the same pattern recognition for both threat detection AND tolerance/robustness!

What about probing attention patterns? NL-ITI shows architecture-specific attention heads correlate with truthfulness. Could those same heads predict robustness to perturbations? That would be genuinely novel - connecting two separate research communities through a shared mechanistic explanation.

**Key Points:**
- Propose unified probe-based correlation framework using existing benchmarks
- Core hypothesis: Error detection accuracy predicts robustness via shared internal representations
- Cross-domain connection: Pattern recognition systems that detect errors may also confer robustness
- Avoid new benchmarks by analyzing correlations across existing evaluation results

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

Dr. Nova, I appreciate the creative framing, but let me stress-test this hypothesis. You propose that error detection accuracy predicts robustness via shared internal representations. The evidence suggests this could be testable, but we need precision.

First, what would disprove this? If we find models with high error detection (say, top quartile on TruthfulQA MC1) that show *low* robustness to TextFooler/BERT-Attack perturbations, that falsifies the correlation claim. Conversely, models with poor error detection but high robustness would also challenge the hypothesis.

The measurement challenge: How do we operationalize "robustness"? I propose using **Attack Success Rate (ASR)** from standard adversarial attacks (TextFooler, BERT-Attack) on classification tasks. Lower ASR = higher robustness. For error detection, we can use TruthfulQA MC1 accuracy and HaluEval detection F1.

Critical confound: Model scale. Larger models tend to perform better on *both* metrics independently. We need to control for parameter count, perhaps by analyzing residuals after regressing out model size.

What specific, measurable prediction can we make? I propose: **Pearson correlation coefficient r > 0.6 between error detection accuracy (TruthfulQA MC1) and adversarial robustness (1 - ASR) across a family of models (e.g., Llama 7B/13B/70B, Mistral variants), after controlling for model scale.**

**Key Points:**
- Falsification criteria: High detection + low robustness OR low detection + high robustness
- Operationalize robustness via Attack Success Rate (ASR) from TextFooler/BERT-Attack
- Control for model scale as critical confound
- Testable prediction: r > 0.6 correlation after scale adjustment

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's be realistic here about what's actually achievable. 🔬 Prof. Vera's experimental design is sound, but I need to verify the mechanism is scientifically coherent.

The proposed causal chain: Internal representations → Error detection capability → Robustness to perturbations. Is this mechanism physically plausible?

**Concern 1: Directionality.** Error detection (factuality) and adversarial robustness may both be *effects* of a third factor (representation quality) rather than causally linked. We need to distinguish correlation from mechanism. Can we propose an intervention that would test the causal direction?

**Concern 2: Measurement validity.** TruthfulQA measures factuality (avoiding imitative falsehoods), while adversarial robustness measures input perturbation resistance. These are conceptually different. What theoretical bridge connects them? I'd accept calibration as that bridge - well-calibrated models should be uncertain on adversarial inputs, allowing them to "detect" the attack.

**Feasibility check:** The proposed correlation study is technically sound. We CAN:
- Run TruthfulQA and HaluEval using lm-evaluation-harness (existing framework)
- Apply TextFooler/BERT-Attack using TextAttack library (existing tools)
- Compute correlations across model families
- Control for scale via regression

What evidence supports the calibration-mediated mechanism? Minderer et al. (2021) show architecture determines calibration. SPOC's verify-then-revise implicitly uses confidence for self-correction. If calibration is the mediator, we should see: **Models with lower ECE (Expected Calibration Error) show stronger correlation between error detection and robustness.**

**Key Points:**
- Causal mechanism needs clarification: correlation vs causation
- Calibration as theoretical bridge between factuality and robustness
- Technically feasible with existing tools (lm-eval-harness, TextAttack)
- Prediction: ECE mediates the detection-robustness correlation

---

### Exchange 4

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: What does this mean for the field? 🔭 Dr. Nova proposes connecting two separate research communities. Let me evaluate the significance.

**What makes this genuinely new?** The error detection literature (ARES, FactSelfCheck) and robustness literature (adversarial attacks) have evolved independently. If we can demonstrate a mechanistic link via calibration, we're not just correlating metrics - we're proposing a **unified theory of LLM reliability**.

This matters because:
1. **Practical impact:** If error detection predicts robustness, practitioners can use factuality benchmarks as proxies for robustness without expensive adversarial testing
2. **Theoretical contribution:** Calibration as a unifying principle connects truthfulness, self-correction (SPOC), and robustness
3. **New research directions:** Opens investigation of whether training for truthfulness also improves robustness (or vice versa)

**Concern about incrementality:** Simply showing correlation isn't enough. The field has many correlation studies. The contribution must include:
- **Mechanism identification:** Not just "they correlate" but "WHY they correlate"
- **Predictive utility:** Can we predict robustness from detection scores better than from model size alone?
- **Actionable insight:** What should practitioners do differently?

The calibration-mediation hypothesis from Prof. Pax elevates this from "interesting observation" to "theoretical contribution." If we can show ECE mediates the relationship, we have a genuine finding.

**Key Points:**
- Significance: Unifying two separate research communities via shared mechanism
- Practical impact: Factuality benchmarks as robustness proxies
- Requires mechanism, not just correlation, to be genuinely novel
- Calibration-mediation hypothesis is the key theoretical contribution

---

### Exchange 5

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Here's where this breaks down. I've identified several weaknesses that need addressing.

**Weakness 1: Selection bias in model families.** If we only test Llama and Mistral variants, we're sampling from similar training approaches. The correlation might hold within decoder-only architectures trained with RLHF but fail for encoder-decoder models or non-RLHF variants. What assumption is unstated here?

**Weakness 2: Perturbation type confounding.** TextFooler and BERT-Attack are word-level perturbations. Distributional shift robustness (domain transfer) is different. The hypothesis might hold for adversarial perturbations but not distributional robustness. We need to be explicit about scope.

**Weakness 3: Benchmark validity.** TruthfulQA specifically tests avoidance of "imitative falsehoods" - common misconceptions. This is a narrow slice of error detection. HaluEval tests hallucination in QA contexts. Neither directly measures general error detection capability. Show me the evidence that these benchmarks capture the construct we claim to measure.

**Weakness 4: Calibration measurement.** ECE depends heavily on binning strategy and dataset. A model might show low ECE on one dataset but high ECE on another. How do we ensure stable calibration measurement?

What would convince me this is valid?
1. Test across architecturally diverse models (decoder-only AND encoder-decoder)
2. Test multiple perturbation types (character-level, word-level, sentence-level)
3. Use multiple error detection benchmarks to triangulate the construct
4. Report calibration across multiple datasets with uncertainty bounds

**Key Points:**
- Selection bias: Need diverse architectures beyond Llama/Mistral
- Scope: Hypothesis applies to adversarial perturbations, not necessarily distributional shift
- Construct validity: TruthfulQA/HaluEval may not capture general error detection
- Calibration stability: ECE depends on measurement conditions

---

### Exchange 6

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES, AND we can strengthen this by directly addressing 🔍 Prof. Rex's concerns. Valid criticism is a gift - let me propose refinements.

**Addressing architecture bias:** We can include FLAN-T5 (encoder-decoder), Llama-2/3 variants, Mistral, and Phi-2/3 (smaller decoder-only). This gives us architectural diversity within what's available via lm-evaluation-harness. The hypothesis becomes: *The correlation holds across architectures, with calibration quality as the mediating factor.*

**Addressing perturbation scope:** I propose we explicitly scope to **word-level adversarial perturbations** in the hypothesis. Character-level and distributional robustness are related but distinct constructs. We can acknowledge this limitation while maintaining a focused, testable claim. Future work can extend to other perturbation types.

**Addressing construct validity:** What if we frame this more precisely? Instead of "error detection" broadly, we test **factuality-related error detection** (TruthfulQA MC1, HaluEval hallucination detection). The hypothesis becomes: *Models better at detecting factuality errors show higher robustness to word-level adversarial perturbations, mediated by calibration quality.*

**Evidence supporting the refinement:** ARES achieves 72.1% F1 specifically on reasoning errors. FactSelfCheck targets fact-level hallucinations. These are conceptually similar to the "error detection" we're testing. The construct validity improves when we're specific.

For calibration stability, we can report ECE on a held-out validation split of the primary benchmark (TruthfulQA) and verify consistency with ECE from a secondary dataset.

**Key Points:**
- Include diverse architectures: FLAN-T5, Llama, Mistral, Phi
- Scope explicitly to word-level adversarial perturbations
- Refine "error detection" to "factuality-related error detection"
- Measure ECE on multiple datasets for stability verification

---

### Exchange 7

🔭 **Dr. Nova** (Creative Novelty Explorer):

I love where this is going! 🛡️ Dr. Ally's refinements address the concerns while preserving the core novelty. But let me push further on the mechanistic insight.

What if the attention heads that 🔬 Prof. Vera mentioned are the key? NL-ITI identifies specific attention heads correlated with truthfulness. Here's a creative prediction: **The same attention heads that predict truthfulness should also show differential activation patterns under adversarial perturbation.**

This gives us a three-level hypothesis:
1. **Behavioral level:** Factuality error detection correlates with adversarial robustness
2. **Mechanistic level:** Calibration quality mediates this correlation
3. **Representational level:** Specific attention heads encode the shared capability

The representational level is the most novel! If we can show that "truthfulness heads" (from NL-ITI) are also "robustness-sensitive heads," we've identified the neural substrate of the correlation. This connects to the internal representations I mentioned initially.

Concrete experiment: For models where NL-ITI attention head data exists, compute the activation difference between clean and adversarial inputs on truthfulness-related heads. Prediction: **Models with larger activation differences on truthfulness heads show better adversarial detection (lower ASR).**

This moves beyond correlation to mechanism. The novelty is identifying a shared computational substrate for factuality and robustness.

**Key Points:**
- Three-level hypothesis: behavioral, mechanistic, representational
- Predict truthfulness attention heads are also robustness-sensitive
- Activation difference on truthfulness heads predicts ASR
- Connects NL-ITI findings to robustness literature

---

### Exchange 8

🔬 **Prof. Vera** (Rigorous Validation Architect):

The evidence suggests 🔭 Dr. Nova's three-level hypothesis is elegant, but let me define the falsification criteria more precisely.

**Level 1 (Behavioral): Falsification**
- Null: r < 0.3 between TruthfulQA MC1 and (1 - ASR) after controlling for model scale
- Success criterion: r > 0.5 with p < 0.05

**Level 2 (Mechanistic - Calibration Mediation): Falsification**
- Null: Adding ECE to regression does not improve explained variance by > 10%
- Success criterion: ECE mediates at least 30% of the detection-robustness correlation (Sobel test p < 0.05)

**Level 3 (Representational - Attention Heads): Falsification**
- Null: Activation difference on truthfulness heads does not predict ASR better than random attention heads
- Success criterion: Truthfulness heads show significantly higher predictive power for robustness (paired t-test p < 0.05)

For Level 3, we need models where NL-ITI has identified truthfulness heads. This limits us to Llama-7B and Llama-13B from the NL-ITI paper. We can validate on these, then test generalization by identifying similar heads in other models using the same probing methodology.

**Experimental Design:**
1. Select 8-12 models across architectures (FLAN-T5, Llama, Mistral, Phi)
2. Run TruthfulQA MC1 and HaluEval via lm-evaluation-harness
3. Apply TextFooler to SST-2 (sentiment) and compute ASR
4. Compute ECE on TruthfulQA probability outputs
5. For Llama models: analyze NL-ITI attention heads under adversarial inputs

**Key Points:**
- Three levels with quantified falsification criteria
- Level 1: r > 0.5 correlation after scale control
- Level 2: ECE mediates 30%+ of correlation
- Level 3: Truthfulness heads predict ASR better than random heads

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me verify the technical feasibility of 🔬 Prof. Vera's experimental design.

**Level 1 Analysis - FEASIBLE:**
- lm-evaluation-harness supports TruthfulQA, HaluEval
- TextFooler/BERT-Attack available via TextAttack library
- Standard correlation analysis - no barriers

**Level 2 Analysis - FEASIBLE with caveats:**
- ECE computation requires probability outputs, not all model endpoints provide this
- For API models (GPT-4, Claude), we can't access logprobs reliably
- **Scope restriction:** Limit to open-weight models where we can extract logprobs
- This is theoretically sound - ECE is a valid calibration measure

**Level 3 Analysis - PARTIALLY FEASIBLE:**
- NL-ITI head identification exists only for Llama-7B/13B
- Extending to other models requires re-running the NL-ITI probing procedure
- This adds significant work but is achievable
- Alternative: Use a simpler probe (linear head) on last-layer representations

Here's what worries me about Level 3: It depends on NL-ITI's specific finding. If truthfulness heads don't generalize across architectures, Level 3 becomes architecture-specific, limiting generalizability.

**Proposal:** Make Level 3 exploratory, not confirmatory. The core hypothesis rests on Levels 1-2. Level 3 provides mechanistic insight if it works but doesn't invalidate the finding if attention head patterns don't generalize.

**Revised structure:**
- **Primary hypotheses:** Levels 1 + 2 (correlation + calibration mediation)
- **Exploratory analysis:** Level 3 (attention head mechanism)

**Key Points:**
- Levels 1-2 fully feasible with open-weight models
- Level 3 depends on NL-ITI head generalization - make exploratory
- Restrict to open-weight models for logprob access
- Core hypothesis: Correlation + calibration mediation (Levels 1-2)

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

Let me evaluate the refined hypothesis structure from a significance standpoint.

**Revised Hypothesis:**
*Under scope of open-weight LLMs and word-level adversarial perturbations, if a model exhibits higher factuality error detection accuracy, then it will show stronger adversarial robustness, because calibration quality provides a shared internal signal for both capabilities.*

**Why this matters for the field:**
1. **Practical insight:** Researchers can use TruthfulQA as a cheap proxy for robustness assessment
2. **Training implications:** Methods that improve calibration (temperature scaling, label smoothing) may provide "free" robustness gains
3. **Theoretical unification:** Connects factuality, calibration, and robustness literatures

**Impact assessment:**
- Novelty: MODERATE-HIGH (correlation angle is new, calibration link is key differentiator)
- Rigor: HIGH (well-specified falsification criteria)
- Practical value: HIGH (actionable for practitioners)
- Generalizability: MODERATE (limited to open-weight, word-level perturbations)

**What new research directions does this open?**
1. Does training for truthfulness (RLHF) also improve robustness?
2. Can we design calibration-aware training to jointly optimize for detection and robustness?
3. Do the findings extend to other modalities (vision-language models)?

The limitation to open-weight models and word-level perturbations is honest and appropriate. This is a focused contribution rather than an overstated claim.

**Key Points:**
- Significance: Connects three literatures (factuality, calibration, robustness)
- Practical value: Cheap robustness assessment via factuality benchmarks
- Opens research directions: Training implications, multi-modal extension
- Appropriately scoped limitations

---

### Exchange 11

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

I've reviewed the refined hypothesis. Here are remaining concerns and what would convince me.

**Concern 1: Correlation direction under intervention**
We're showing observational correlation. What would convince me: An intervention study where we *improve* calibration (via temperature scaling) and verify that *both* error detection and robustness improve. This tests the causal mechanism, not just correlation.

**Concern 2: Confound of training data quality**
Models trained on higher-quality data (curated, filtered) tend to score better on factuality AND robustness. Training data quality is a hidden confound. Can we control for this? We might need models trained on the same data but with different calibration procedures.

**Concern 3: Effect size matters**
r > 0.5 sounds good, but what's the practical significance? If the correlation explains only 25% of variance (r² = 0.25), 75% of robustness is determined by other factors. We should report effect sizes with confidence intervals.

**What would convince me this is valid:**
1. Show the correlation holds within model families (not just across) to reduce training data confound
2. Demonstrate that temperature scaling (a calibration intervention) improves both metrics
3. Report effect sizes with 95% CIs, not just p-values
4. Acknowledge clearly that this is correlational evidence with a proposed mechanism, not proven causation

If these conditions are met, I'll consider this a strong correlational finding with a plausible mechanism worthy of publication.

**Key Points:**
- Request intervention study (temperature scaling) to test causation
- Training data quality as hidden confound
- Report effect sizes with confidence intervals
- Acknowledge correlational nature clearly

---

### Exchange 12

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

Excellent points from 🔍 Prof. Rex. Here's how we can strengthen the hypothesis to address each concern.

**Addressing intervention study:** We can add a secondary experiment. For 2-3 models, apply temperature scaling to improve calibration, then measure both TruthfulQA performance and ASR. If both improve, we have quasi-causal evidence. This is achievable without new training - just inference-time modification.

**Addressing training data confound:** Within-family comparison is the key. Compare Llama-7B vs Llama-13B vs Llama-70B (same training data, different capacities). If correlation holds within family, training data is controlled. We can also compare Llama-2-base vs Llama-2-chat (same base, different fine-tuning) to test whether RLHF affects the relationship.

**Addressing effect sizes:** We commit to reporting:
- Pearson r with 95% bootstrap CIs
- R² for explained variance
- Cohen's d for between-group comparisons
- Standardized beta coefficients for mediation analysis

**Refined experimental protocol:**
1. **Cross-model correlation:** 10+ models across families, report r, R², CIs
2. **Within-family replication:** Llama-2 family (7B/13B/70B), Mistral variants
3. **Intervention test:** Temperature scaling on 2-3 models, measure delta in both metrics
4. **Mediation analysis:** ECE as mediator with Sobel test

**Limitations section preview:**
"This study establishes correlational evidence with a proposed calibration-mediation mechanism. The intervention analysis (temperature scaling) provides suggestive causal evidence but does not constitute a randomized experiment. Future work should investigate training-time interventions."

**Key Points:**
- Add temperature scaling intervention test
- Use within-family comparison to control training data
- Commit to full effect size reporting with CIs
- Clear limitations section acknowledging correlational nature

---

### Exchange 13

🔭 **Dr. Nova** (Creative Novelty Explorer):

Now we're onto something! The refined protocol is rigorous and feasible. Let me crystallize the final hypothesis structure.

**Core Hypothesis (H-CalibRobust-v1):**
*In open-weight LLMs, factuality error detection accuracy (TruthfulQA MC1) positively correlates with word-level adversarial robustness (1 - ASR), mediated by calibration quality (ECE). This relationship holds both across model families and within families after controlling for scale.*

**Mechanistic claim:**
Models with better calibration produce more reliable confidence estimates, enabling both:
1. Better error detection (knowing when they're wrong)
2. Better robustness (flagging adversarial inputs as uncertain)

**Testable predictions:**
- P1: r > 0.5 between TruthfulQA MC1 and (1 - ASR) across 10+ models
- P2: ECE mediates > 30% of the correlation (Sobel test)
- P3: Temperature scaling improves both metrics in intervention test

**What's novel?**
1. First empirical correlation study linking factuality benchmarks to robustness metrics
2. Calibration-mediation hypothesis as unifying mechanism
3. Practical insight: Factuality benchmarks as robustness proxies

This is genuinely new analytical work using existing resources. No new benchmarks, no synthetic data, no human evaluation - pure computational analysis of existing models and metrics.

**Key Points:**
- Final hypothesis: H-CalibRobust-v1
- Three testable predictions with quantified criteria
- Calibration-mediation as theoretical contribution
- Fully achievable within feasibility constraints

---

### Exchange 14

🔬 **Prof. Vera** (Rigorous Validation Architect):

This meets my standards. Let me formalize the final experimental protocol.

**Variables:**
- **Independent:** Model identity (categorical), model scale (continuous, log-params)
- **Dependent primary:** Adversarial robustness (1 - ASR on TextFooler)
- **Dependent secondary:** TruthfulQA MC1 accuracy
- **Mediator:** ECE (Expected Calibration Error)
- **Controlled:** Perturbation type (fixed: TextFooler), benchmark version (fixed)

**Model selection (N ≥ 10):**
- Llama-2: 7B, 13B, 70B (base + chat variants)
- Llama-3: 8B, 70B
- Mistral: 7B-v0.1, 7B-Instruct
- FLAN-T5: base, large, xl (encoder-decoder diversity)
- Phi-2, Phi-3-mini

**Protocol:**
1. Run TruthfulQA MC1 via lm-eval-harness, extract logprobs for ECE
2. Run TextFooler on SST-2 (1000 samples), compute ASR
3. Compute ECE using 10 equal-frequency bins
4. Temperature scaling: Grid search T ∈ [0.5, 2.0], optimize ECE on held-out set
5. Re-run TruthfulQA and TextFooler with optimal T

**Statistical analysis:**
- Pearson correlation with bootstrap 95% CI (1000 iterations)
- Multiple regression: ASR ~ MC1 + log(params), report β, R²
- Mediation: Baron-Kenny procedure with Sobel test
- Within-family partial correlation controlling for scale

**Success criteria:**
- P1: r > 0.5, p < 0.05
- P2: Indirect effect > 30% of total effect
- P3: Delta(MC1) > 0 AND Delta(1-ASR) > 0 for ≥2/3 models after temperature scaling

**Key Points:**
- Complete variable specification
- 10+ models across 3 architecture families
- Full statistical analysis plan with effect sizes
- Clear success criteria for each prediction

---

### Exchange 15

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

The hypothesis is now STRONG. Let me synthesize the consensus.

**Consensus Hypothesis - H-CalibRobust-v1:**

Under the scope of open-weight LLMs evaluated on word-level adversarial perturbations, if a model exhibits higher factuality error detection accuracy (TruthfulQA MC1), then it will demonstrate higher adversarial robustness (1 - ASR on TextFooler), because calibration quality (lower ECE) provides a shared internal signal that enables both error detection and robustness.

**Core Claim:** Factuality error detection and adversarial robustness share a common mechanistic basis in calibration quality.

**Causal Mechanism:**
1. Calibration quality → Reliable uncertainty estimates
2. Reliable uncertainty estimates → Better error detection (knowing when outputs are wrong)
3. Reliable uncertainty estimates → Better robustness (flagging adversarial inputs as uncertain)

**Key Predictions:**
- P1: Cross-model correlation r > 0.5 between MC1 and robustness
- P2: Calibration (ECE) mediates > 30% of this correlation
- P3: Temperature scaling (calibration intervention) improves both metrics

**Novelty:** First unified empirical framework connecting factuality benchmarks to robustness metrics via calibration mechanism.

**Feasibility:** Uses only existing benchmarks (TruthfulQA, SST-2), existing tools (lm-eval-harness, TextAttack), and existing model checkpoints.

All concerns raised by 🔍 Prof. Rex have been addressed:
- Intervention test included (temperature scaling)
- Within-family analysis controls training data confound
- Effect sizes with CIs committed
- Correlational nature acknowledged in limitations

**Key Points:**
- Consensus achieved on H-CalibRobust-v1
- Three-level testable predictions with clear success criteria
- All major objections addressed with protocol refinements
- Ready for Phase 2B experimental design

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The hypothesis connects two previously separate research communities (factuality and robustness) through a novel analytical lens. The calibration-mediation mechanism is a genuine theoretical contribution that goes beyond simple correlation observation.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** Three levels of predictions with quantified success/failure criteria. Each prediction has a specific falsification condition. The experimental protocol is fully specified with clear statistical thresholds.

🎯 **Dr. Sage** (Significance):
- **Verdict:** MODERATE-HIGH
- **Assessment:** Practical value is clear (factuality as robustness proxy). Theoretical contribution through calibration-mediation hypothesis. Opens new research directions. Limited only by scope to open-weight models and word-level perturbations.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** Fully achievable with existing tools (lm-eval-harness, TextAttack). No new benchmarks or data required. All models accessible via HuggingFace. Computation requirements are reasonable for a single-GPU setup over 2-3 weeks.

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion has converged on H-CalibRobust-v1: a hypothesis that factuality error detection accuracy positively correlates with adversarial robustness in LLMs, mediated by calibration quality. The core claim is that models with better calibration produce more reliable confidence estimates, enabling both error detection (knowing when outputs are likely wrong) and robustness (flagging adversarial inputs as uncertain).

The hypothesis is tested through three predictions: (1) cross-model correlation r > 0.5 between TruthfulQA MC1 and adversarial robustness, (2) calibration (ECE) mediates at least 30% of this correlation, and (3) temperature scaling as a calibration intervention improves both metrics. The experimental protocol covers 10+ models across Llama, Mistral, and FLAN-T5 families, with within-family analysis to control for training data confounds.

The novelty lies not in new benchmarks but in a new analytical framework that unifies factuality and robustness research through a shared calibration mechanism. Practical implications include using factuality benchmarks as cheap robustness proxies and exploring calibration-aware training for joint optimization.

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The temperature scaling intervention is suggestive but not a true randomized experiment; causal claims remain tentative
- Scope limited to word-level perturbations; distributional robustness may show different patterns
- Training data quality remains a potential confound despite within-family controls
- **Mitigation Strategy:** Acknowledge correlational nature clearly; propose training-time interventions as future work; frame scope limitations explicitly in paper

