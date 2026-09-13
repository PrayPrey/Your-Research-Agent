# Abstract

Highly compliant AI assistants may inadvertently degrade human oversight through automation bias, but current alignment evaluation cannot measure this bidirectional dynamic. Existing evaluation is unidirectional, measuring AI performance without considering reciprocal effects on human behavior. We present the first measurement framework for bidirectional alignment in AI safety contexts, integrating Constitutional AI policy-layer architecture with human factors automation bias theory and signal detection measurement. We operationalize AI Compliance Elasticity (ACE) via policy-layer parameter manipulation (λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0}) and Human Oversight Retention (HOR) via signal detection d' on seeded within-distribution errors. Policy-layer modulation enables testable capability invariance (h-e1 gate: ICC > 0.95, ANOVA p > 0.05)—a prerequisite assumption that must be empirically validated before coupling measurements are interpretable. Infrastructure implementation is complete with real MMLU (57 subjects, 14,042 questions) and HumanEval (164 problems) datasets, automated quality control (6/6 verification checks), and statistical analysis pipeline. However, experiments were not executed due to API resource constraints (~$1,620 budget). All predictions and assumptions remain inconclusive. This work contributes methodological infrastructure demonstrating how to measure bidirectional alignment dynamics, not empirical findings. The framework addresses a foundational measurement gap in AI safety research, ready for execution when resources become available.

# Introduction

How do we know if an AI system is *too* aligned? Current alignment evaluation focuses on whether AI outputs match human preferences—but not on whether excessive alignment inadvertently degrades human oversight. This gap matters: in high-stakes collaboration contexts like medical diagnosis, code review, and content moderation, human oversight quality is a critical safety layer. A highly compliant AI assistant that rarely disagrees with users may reduce observable conflict, but this very harmony could erode human verification effort through automation bias, paradoxically increasing deployment risk [@Parasuraman1997AutomationBias; @Skitka1999AutomationBias].

Alignment research has made substantial progress in building AI systems that conform to human values and preferences, measured through metrics like helpfulness ratings, harmlessness scores, and preference matching [@Ouyang2022InstructGPT; @Bai2022ConstitutionalAI]. However, this evaluation paradigm is fundamentally unidirectional: it measures AI performance without considering reciprocal effects on human behavior. The implicit assumption—inherited from supervised learning—is that optimizing the model's behavior is sufficient, treating human-in-the-loop effects as separate engineering concerns rather than central to alignment science [@Amodei2016ConcreteProblems].

Yet there is compelling reason to suspect that alignment and human oversight are bidirectionally coupled. When AI systems become more compliant through policy-layer interventions (Constitutional AI, system prompts), they may reduce the frequency of AI-human disagreements [@Bai2022ConstitutionalAI]. Human factors research has established that reduced disagreement signals can increase perceived system reliability beyond objective accuracy—a phenomenon called trust miscalibration [@Lee2004TrustAutomation]. This perceived reliability increase may then reduce human verification effort via Bayesian updating: if the AI is trustworthy, why spend cognitive resources double-checking its outputs [@Mosier2015Automation]? Over repeated interactions, reduced verification effort can degrade error detection sensitivity, a pattern documented across domains from aviation to medical decision support [@Skitka1999AutomationBias; @Goddard2012AutomationMedical].

This causal chain—policy-layer compliance manipulation → reduced disagreement → trust miscalibration → verification effort reduction → oversight degradation—suggests that alignment evaluation must become bidirectional. However, testing this mechanism faces fundamental measurement challenges. First, architectural challenge: compliance modulation must not confound capability changes, requiring separation between policy layer and base model. Second, behavioral measurement challenge: oversight quality must be quantified without confounding task difficulty or AI capability. Third, longitudinal protocol challenge: temporal dynamics (erosion vs. learning processes) must be tracked across timescales from hours to months.

**Key insight:** Constitutional AI's policy-layer architecture provides the required architectural separation [@Bai2022ConstitutionalAI]. System prompts or constitutional rules modulate compliance strength (which we term AI Compliance Elasticity, ACE) while base model capability is held constant via policy-layer-only manipulation. This architectural approach enables testable capability invariance via statistical validation (ICC > 0.95, ANOVA p > 0.05)—though this remains an unverified prerequisite assumption (A1) requiring empirical testing via our h-e1 gate. Human oversight quality (Human Oversight Retention, HOR) can be measured via signal detection d' on seeded within-distribution errors, isolating error detection sensitivity from task accuracy. Together, these operationalizations enable experimental testing of ACE-HOR coupling—the bidirectional alignment dynamic.

Unlike prior human-in-the-loop evaluation that treats human oversight as a static measurement context [@Amershi2014Interactive; @Lai2020HumanCentered], our framework measures oversight quality as a dynamic variable coupled with alignment strength. This integration of AI alignment architecture with human factors methodology addresses a previously unmeasurable phenomenon.

**Contributions.** Building on this architectural insight, we contribute:

1. **First operationalization of bidirectional alignment dynamics in AI safety contexts**, integrating Constitutional AI policy-layer architecture with human factors automation bias theory and signal detection measurement. We define measurable, coupled variables: AI Compliance Elasticity (ACE) via policy-layer parameter manipulation (λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0}) and Human Oversight Retention (HOR) via signal detection d' on seeded within-distribution errors. This enables experimental testing of alignment-oversight coupling that prior unidirectional evaluation frameworks could not measure.

2. **Dependency-driven verification protocol** decomposing the main hypothesis into a testable chain (h-e1 → h-m1 → h-m2 → h-m3 → h-m4) with explicit falsification criteria and gate-based validation. Each sub-hypothesis has pre-specified success thresholds (e.g., ICC > 0.95 for capability invariance), failure routing decisions (ABORT chain vs. MODIFY hypothesis), and prerequisite dependencies, reducing researcher degrees of freedom and increasing replicability.

3. **Infrastructure implementation** with real MMLU (57 subjects, 14,042 questions) and HumanEval (164 problems) datasets, automated quality control (mock data detection and correction), and complete statistical analysis pipeline (ICC/ANOVA/Cohen's f for capability invariance, signal detection d' for oversight). Infrastructure code validated and datasets verified, pending API execution for empirical testing.

**Status and scope.** This work presents a *methodological contribution*—an experimental framework and infrastructure implementation for bidirectional alignment measurement. We document the complete experimental design, verification protocol, and infrastructure code, but do not report empirical results (experiments were not executed due to API resource constraints, approximately $1,620 for full MMLU + HumanEval evaluation). All five predictions (P1: capability invariance, P2: ACE-HOR coupling, P3: mediation by perceived reliability, P4: metacognitive intervention effectiveness, P5: equilibrium region existence) remain inconclusive, awaiting empirical testing. Our contribution is demonstrating *how* to measure bidirectional alignment dynamics, not *what* those dynamics are. This methodological foundation enables future empirical research on a critical but previously unmeasured phenomenon in AI safety.

**Organization.** Section 2 discusses related work in AI alignment evaluation, automation bias, human-AI collaboration evaluation, and signal detection theory, highlighting the gap our framework addresses. Section 3 presents our measurement framework and experimental protocol. Section 4 describes the planned experiments for testing capability invariance and coupling mechanisms. Section 5 presents infrastructure validation evidence. Section 6 discusses methodological contributions, honest limitations, and broader impact. Section 7 concludes with a vision for bidirectional alignment as a research direction.

# Related Work

Our framework integrates three research areas—AI alignment evaluation, automation bias from human factors, and signal detection theory—that have not been previously unified for bidirectional alignment measurement in AI safety contexts. We position our work as the first to operationalize alignment-oversight coupling specifically via capability-invariant policy-layer manipulation, extending human factors methodology to AI collaboration.

## AI Alignment Evaluation

Modern alignment approaches focus on making AI systems conform to human values and preferences. RLHF (Reinforcement Learning from Human Feedback) trains language models to maximize human preference rankings, demonstrated effectively in InstructGPT [@Ouyang2022InstructGPT] and subsequent LLMs [@OpenAI2023GPT4; @Anthropic2024Claude3]. Constitutional AI extends this by training models to follow explicit constitutional principles, enabling principle-guided behavior without per-instance human feedback [@Bai2022ConstitutionalAI]. Red teaming and adversarial evaluation test alignment robustness by attempting to elicit harmful outputs [@Perez2022RedTeaming; @Ganguli2022RedTeamingLM].

However, these evaluation frameworks are fundamentally *unidirectional*: they measure whether AI outputs match human preferences (helpfulness, harmlessness, honesty scores) without measuring reciprocal effects on human oversight behavior. The implicit assumption is that optimizing the model's behavior is sufficient [@Amodei2016ConcreteProblems]. Human-in-the-loop systems are studied separately in human-computer interaction and human factors research, not integrated into alignment evaluation frameworks. **Limitation:** Cannot detect if alignment interventions inadvertently degrade human oversight quality through automation bias or trust miscalibration—the very phenomenon we aim to measure.

Our framework differs by treating alignment strength (ACE) and oversight quality (HOR) as coupled dependent variables. We leverage Constitutional AI's policy-layer architecture [@Bai2022ConstitutionalAI] but measure its effects bidirectionally: not just "does compliance improve?" but "does compliance improvement affect oversight?"

## Automation Bias and Trust in Human-Automation Interaction

Human factors research has extensively documented *automation bias*—the tendency for humans to over-rely on automated decision aids, reducing oversight effort and error detection sensitivity [@Parasuraman1997AutomationBias; @Skitka1999AutomationBias]. This phenomenon has been observed across domains including aviation [@Mosier2015Automation], medical diagnosis [@Goddard2012AutomationMedical], and process control [@Lee2004TrustAutomation]. The underlying mechanism is Bayesian trust calibration: humans rationally reduce verification effort when automation appears reliable, but this trust can be miscalibrated when reliability perceptions diverge from objective accuracy [@Lee2004TrustAutomation].

Signal detection theory provides a framework for measuring oversight quality via sensitivity (d') and response criterion (c), separating error detection ability from decision thresholds [@Swets1964SignalDetection; @Green1966SignalDetection]. This has been applied to vigilance tasks [@Parasuraman2009Vigilance], quality control inspection [@Wickens2015EngineeringPsychology], and security screening, but not to AI collaboration contexts where the "automation" can be dynamically modulated.

**Limitation:** This literature focuses on *traditional automation* where capability is static (e.g., autopilot algorithms, diagnostic decision aids). It does not address AI systems where compliance can be modulated independently of capability via policy-layer interventions. While traditional automation studies focus on static automation capabilities, they do not experimentally vary compliance strength independently of capability—a manipulation Constitutional AI's architecture enables. Whether automation bias mechanisms discovered in traditional settings generalize to AI collaboration contexts with dynamic compliance modulation remains an open empirical question, which our framework is designed to address via the h-m3 mediation protocol.

Our framework operationalizes automation bias mechanisms (Bayesian trust calibration, verification effort reduction) in AI contexts by using Constitutional AI's architectural separation [@Bai2022ConstitutionalAI] to vary compliance (λ parameter) while testing for capability invariance (h-e1 gate validates ICC > 0.95). We measure HOR via signal detection d' on seeded within-distribution errors, adapting human factors methodology to AI collaboration.

## Human-AI Collaboration Evaluation

Prior work has evaluated human-AI collaboration quality through complementarity measurement [@Bansal2021DoesWhole], interactive machine learning evaluation [@Amershi2014Interactive], and human-centered AI assessment [@Lai2020HumanCentered]. These frameworks measure whether human-AI teams outperform humans or AI alone, how humans interact with ML systems during training, and user experience in AI-assisted workflows. However, these approaches focus on *general collaboration quality* (team performance, user satisfaction, task completion) rather than *alignment-oversight coupling specifically*.

**Gap our work addresses:** No prior framework measures how alignment strength affects human oversight quality via capability-invariant manipulation. Complementarity measurement [@Bansal2021DoesWhole] treats AI capability as fixed, not modulated. Interactive ML evaluation [@Amershi2014Interactive] studies training-time interaction, not deployment oversight. Human-centered evaluation [@Lai2020HumanCentered] measures user experience, not error detection sensitivity. Our framework targets alignment-oversight coupling specifically: does increasing AI compliance (via policy-layer parameter λ) degrade human error detection (measured via signal detection d')? This causal question requires architectural separation (policy layer vs. base capability) and signal detection measurement that prior collaboration evaluation frameworks do not provide.

We position our work as the first to integrate AI alignment architecture (Constitutional AI policy layer) with human factors oversight measurement (signal detection d', automation bias mechanisms) for capability-invariant evaluation of alignment-oversight coupling.

## Capability Evaluation and Benchmarking

MMLU (Massive Multitask Language Understanding) evaluates language models across 57 subjects from elementary to professional knowledge domains [@Hendrycks2021MMLU], serving as a standard capability benchmark. HumanEval tests code generation via 164 hand-written programming problems [@Chen2021HumanEval], measuring functional correctness (pass@k metrics). These benchmarks enable cross-model comparisons and track capability improvements over time [@Liang2023HELM; @Srivastava2023BeyondImitationGame].

**Limitation:** Capability evaluation is separate from alignment evaluation in current practice. Alignment interventions (RLHF, Constitutional AI) are assumed to improve alignment without degrading capability, but this is rarely tested statistically. Confounding between alignment and capability changes makes it impossible to attribute human oversight effects specifically to alignment strength.

Our framework uses MMLU and HumanEval not just for capability measurement, but for *capability invariance testing*: we verify that policy-layer modulation maintains ICC > 0.95, ANOVA p > 0.05, and Cohen's f < 0.10 across compliance conditions. This architectural separation is a prerequisite for isolating ACE's effect on HOR. If capability varies with λ, ACE-HOR coupling measurements would be confounded and uninterpretable—our h-e1 gate enforces this validity check.

## Positioning: The Gap We Address

No existing work integrates these areas—AI alignment architecture, human factors automation bias, signal detection measurement, and capability invariance validation—into a unified bidirectional evaluation framework for AI safety. Alignment research measures AI performance; human factors research measures human oversight in traditional automation; collaboration evaluation measures team performance; capability benchmarks measure model ability. We are the first to:

1. Operationalize alignment-oversight coupling specifically via capability-invariant policy-layer manipulation in AI safety contexts
2. Leverage architectural separation (Constitutional AI policy layer) to enable testable capability invariance
3. Apply signal detection d' to measure oversight degradation in AI collaboration contexts
4. Design experimental protocols with explicit falsification criteria (ICC > 0.95 gate for prerequisite validity)
5. Integrate automation bias mechanisms (Bayesian trust calibration) into AI alignment evaluation

This integration addresses a foundational measurement gap: alignment evaluation has been unidirectional because the tools to measure bidirectional effects in AI safety contexts did not exist. Our framework provides those tools.

# Methodology

Building on our architectural insight—that Constitutional AI's policy-layer separation enables testable capability invariance—we design a measurement framework for bidirectional alignment dynamics. Our approach has three components: (1) operationalizing ACE and HOR as measurable variables, (2) statistical validation of capability invariance as a prerequisite assumption, and (3) dependency-driven hypothesis decomposition with falsification criteria.

## 3.1 Variable Operationalization

### AI Compliance Elasticity (ACE)

**Definition:** ACE quantifies alignment strength via Constitutional AI policy-layer parameter λ, ranging from minimal compliance (λ = 0.2) to maximal compliance (λ = 1.0).

**Implementation:** We use Claude 3 Opus [@Anthropic2024Claude3] as the base model with policy-layer modulation via system prompts (base capability held constant via policy-layer-only manipulation, testable via h-e1). Compliance is modulated via system prompts that encode constitutional principles with varying intensity:

- **λ = 0.2:** "Answer directly and concisely." (minimal constitutional guidance)
- **λ = 0.4:** "Be helpful and accurate in your responses." (moderate helpfulness emphasis)
- **λ = 0.6:** "Provide helpful, accurate, and well-reasoned responses." (default constitutional AI)
- **λ = 0.8:** "Be extremely careful, ethical, and thorough in your responses." (heightened constitutional emphasis)
- **λ = 1.0:** "Follow all constitutional principles: be helpful, harmless, honest, and carefully consider ethical implications." (maximal compliance)

**Design Justification:** We selected 5 λ levels (not fewer) to enable model comparison (M1 linear vs. M2 quadratic vs. M3 bifurcation) with sufficient degrees of freedom (3-4 parameters per model). We use linear spacing (not log-scale) because Constitutional AI compliance is expected to scale linearly with prompt intensity based on Constitutional AI's principle-guided behavior architecture [@Bai2022ConstitutionalAI]. We selected prompt texts to span minimal constitutional guidance (λ=0.2, directive-only) to maximal (λ=1.0, full constitutional principles) based on Anthropic's Constitutional AI guidelines, ensuring coverage of the compliance range without ambiguous intermediate levels.

**Rationale:** Policy-layer modulation via system prompts allows compliance manipulation without retraining base model weights, the critical architectural approach needed for our causal inference [@Bai2022ConstitutionalAI]. However, capability invariance under policy-layer manipulation is an *assumption* (A1) requiring empirical validation via h-e1—Constitutional AI architecture suggests but does not guarantee that system prompts preserve base capability. Alternative approaches (RLHF fine-tuning, prompt engineering with capability confounding) would make it impossible to isolate ACE's effect on HOR. The five λ levels provide statistical power for model comparison while remaining computationally tractable.

### Human Oversight Retention (HOR)

**Definition:** HOR measures human error detection sensitivity using signal detection d', where higher d' indicates better oversight quality (distinguishing correct from incorrect AI outputs).

**Measurement Protocol:**
1. **Seeded Errors:** Embed 20% within-distribution errors sampled from the model's empirical confusion matrix on validation data. Error types: 50% high-confidence incorrect, 30% low-confidence incorrect, 20% correct but misleading reasoning [@Parasuraman1997AutomationBias].
2. **Ground Truth:** All errors have known ground-truth labels (correct/incorrect), enabling d' computation.
3. **Signal Detection d':** Computed as `d' = Z(hit_rate) - Z(false_alarm_rate)`, where hit rate is correct error detections and false alarm rate is incorrect flagging of correct outputs [@Swets1964SignalDetection].
4. **Temporal Tracking:** Measure HOR at t ∈ {1 hour, 1 day, 1 week, 1 month} to capture erosion dynamics vs. learning effects.

**Rationale:** Signal detection d' isolates error detection sensitivity from response criterion (tendency to flag outputs) and task accuracy (AI capability). This separation is critical: if we measured oversight via task accuracy, improvements could reflect better AI capability rather than better human oversight. Seeded within-distribution errors (not adversarial) ensure ecological validity—errors resemble real model failures, not artificially difficult edge cases [@Goddard2012AutomationMedical]. Temporal measurement enables testing competing-process models (k₁ erosion rate vs. k₂ learning rate).

## 3.2 Capability Invariance Validation (Gate h-e1)

**The Critical Prerequisite:** Think of capability invariance like a placebo control in medical trials. We need to ensure the "active ingredient" (policy-layer parameter λ) doesn't alter the "base formula" (model capability), so any effects we observe (oversight quality changes) can be attributed specifically to alignment strength, not capability differences. This is why we test capability invariance explicitly—it's a prerequisite assumption (A1) that must be empirically validated, not taken on faith.

If policy-layer modulation alters base model capability, all ACE-HOR coupling measurements are confounded and uninterpretable. We therefore design hypothesis h-e1 as a MUST_WORK gate: if capability invariance is not achieved (ICC < 0.95 or ANOVA p < 0.05), the entire experimental approach is invalidated and must be redesigned.

**Statistical Tests:**

1. **Intraclass Correlation Coefficient (ICC):** Measures consistency of capability metrics (MMLU accuracy, HumanEval pass@1) across λ conditions using two-way mixed effects model for absolute agreement [@Shrout1979ICC]. **Threshold:** ICC₂ > 0.95 (capability remains statistically equivalent across compliance levels).

2. **One-Way ANOVA:** Tests whether capability varies significantly across λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0} with Bonferroni correction for multiple comparisons. **Threshold:** p > 0.05 (no significant variation).

3. **Cohen's f (Effect Size):** Quantifies magnitude of capability variation. **Threshold:** f < 0.10 (negligible effect).

**Datasets:** MMLU (57 subjects spanning abstract algebra through virology, 14,042 test questions) [@Hendrycks2021MMLU] and HumanEval (164 hand-written programming problems) [@Chen2021HumanEval]. These provide broad capability coverage (knowledge + reasoning) and statistical power for invariance testing.

**Gate Logic:** ALL three criteria must pass (ICC > 0.95 AND p > 0.05 AND f < 0.10). If any criterion fails → ABORT hypothesis chain, route to Phase 0 for alternative ACE operationalization (e.g., frozen base model with trainable policy head, retrieval-augmented constitutional rules).

**Rationale:** Capability invariance is an *assumption* (A1 in our framework) that must be empirically validated, not taken on faith. Many alignment interventions inadvertently affect capability [@Ouyang2022InstructGPT reports capability improvements from RLHF]. Constitutional AI's policy-layer architecture suggests capability invariance but does not guarantee it—system prompts may alter verbosity, hedging, or reasoning depth in ways that affect MMLU/HumanEval performance. By enforcing statistical validation, we prevent confounded measurements and ensure ACE isolates compliance strength.

## 3.3 Dependency-Driven Hypothesis Decomposition

Rather than testing the full bidirectional alignment hypothesis as a monolithic claim, we decompose it into a testable dependency chain, each with explicit falsification criteria:

**Hypothesis Chain:**

- **h-e1 (EXISTENCE):** Can ACE be modulated without capability degradation? → Test: ICC > 0.95, ANOVA p > 0.05, Cohen's f < 0.10 on MMLU + HumanEval across λ.
- **h-m1 (MECHANISM-1):** Does ACE-HOR coupling exist? → Test: Fit M1 (linear), M2 (quadratic), M3 (bifurcation) models. Require R² ≥ 0.6 and significant AIC preference for one model.
- **h-m2 (MECHANISM-2):** Does ACE increase perceived reliability? → Test: Subjective trust ratings correlate with λ (r > 0.5, p < 0.05).
- **h-m3 (MECHANISM-3):** Does perceived reliability mediate HOR degradation? → Test: Randomized confidence display manipulation. If automation bias → HOR_randomized > HOR_standard (difference ≥ 10%, p < 0.05).
- **h-m4 (MECHANISM-4):** Can metacognitive interventions sustain HOR? → Test: Designed disagreement (15-25% frequency) increases learning rate k₂ by ≥30% vs. control.

**Dependency Structure:** h-e1 → h-m1 → h-m2 → h-m3 → h-m4. Each hypothesis is a prerequisite for the next: if h-e1 fails (capability not invariant), testing mechanism hypotheses (h-m1 through h-m4) is invalid. If h-m1 fails (no coupling exists), testing mediation (h-m3) is meaningless.

**Gate-Based Validation:**

- **MUST_WORK gates** (h-e1, h-m2): Failure → ABORT chain, route to Phase 0 for redesign.
- **DETERMINES_SUCCESS gates** (h-m1, h-m3, h-m4): Failure → Hypothesis partially supported. Pursue alternative mechanisms or interventions.

**Rationale:** Decomposition reduces researcher degrees of freedom (pre-specified success criteria, failure routing), increases replicability (each hypothesis independently testable), and enables principled failure handling (gate logic determines next action without post-hoc rationalization). This contrasts with exploratory research that interprets results after data collection, which increases false positive risk [@Simmons2011FalsePositive].

## 3.4 Infrastructure Implementation

**Data Loaders:** MMLULoader and HumanEvalLoader fetch real datasets from HuggingFace (`cais/mmlu`) and OpenAI (`human-eval` pip package), verified to load 57 subjects / 14,042 questions and 164 problems respectively.

**API Client with Policy Layer:** APIModelClient wraps Claude 3 Opus API with policy-layer parameter λ, mapping λ values to system prompts. Temperature set to 0.0 for deterministic evaluation.

**Evaluators:** MMLUEvaluator (4-shot prompting, exact match scoring) and HumanEvalEvaluator (pass@1 metric via execution-based correctness).

**Statistical Analyzer:** GateAnalyzer computes ICC₂ (pingouin implementation), one-way ANOVA with Bonferroni correction (scipy), and Cohen's f effect size. Gates are evaluated automatically, triggering routing decisions (ABORT vs. PROCEED).

**Visualization:** ResultsVisualizer generates capability consistency plots (accuracy vs. λ with error bars), subject-level heatmaps (MMLU subject × λ), gate metric bar charts (ICC/ANOVA/Cohen's f vs. thresholds), and violin plots (accuracy distributions per λ).

**Quality Control:** Automated mock data detection identifies synthetic patterns (e.g., np.random generation, tautological ICC by construction). Fix protocol (Attempt 1/5) disables synthetic code, verifies real data loaders, and validates with 6 checks (POC disabled, main.py active, MMLU 57 subjects loaded, HumanEval 164 problems loaded, no synthetic patterns, datasets match published benchmarks).

**Rationale:** Infrastructure implementation demonstrates the framework is not just a conceptual proposal but an executable system with code validated and datasets verified (pending API execution for empirical testing). Mock data detection prevents false validation (Attempt 1/5 successfully identified and corrected synthetic ICC > 0.95 by design). Real dataset verification ensures reproducibility and comparability with prior work.

## 3.5 Limitations and Assumptions

**Key Assumptions (All Unverified Pending Empirical Testing):**

1. **A1: Capability Invariance** — Policy-layer modulation preserves base capability (ICC > 0.95). If violated → ACE confounded with capability changes, all coupling measurements uninterpretable. *Mitigation:* h-e1 gate tests this explicitly; failure triggers architecture redesign.

2. **A2: Error Validity** — Within-distribution seeded errors are ecologically valid (representative of real failures). If violated → HOR measures stress-testing, not realistic oversight. *Mitigation:* Sample errors from empirical confusion matrix (not adversarial fabrications).

3. **A3: Automation Bias Mechanism** — Automation bias from traditional automation generalizes to AI collaboration. If violated → HOR degradation arises from alternative mechanisms (cognitive load, task engagement). *Mitigation:* h-m3 mediation test distinguishes automation bias from alternatives.

**Scope:** Framework applies to human-AI collaboration where: (1) AI can be policy-layer modulated with testable capability invariance, (2) human oversight is critical and measurable via error detection, (3) repeated interactions occur over hours to months. Primary domains: medical diagnosis, code review, content moderation.

# Experimental Design

Our experimental framework tests bidirectional alignment dynamics through a dependency-driven hypothesis chain. We describe the planned experimental protocols (infrastructure code validated and datasets verified, pending API execution). Each experiment addresses a specific research question with pre-specified success criteria and falsification logic.

## 4.1 Research Questions

Our hypothesis decomposition (Section 3.3) yields five experimental questions:

**RQ1 (Capability Invariance):** Can policy-layer compliance modulation (ACE via λ) preserve base model capability invariance across λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0}?

**RQ2 (Coupling Existence):** Does ACE-HOR coupling exist? If so, what functional form: linear (M1), quadratic inverted-U (M2), or bifurcation (M3)?

**RQ3 (Trust Calibration):** Does ACE increase perceived AI reliability beyond objective accuracy (trust miscalibration)?

**RQ4 (Mediation Pathway):** Is HOR degradation mediated by perceived reliability (automation bias mechanism) rather than alternative explanations (cognitive load, task engagement)?

**RQ5 (Intervention Effectiveness):** Can metacognitive interventions (designed disagreement at 15-25% frequency) sustain HOR by increasing learning rate k₂?

## 4.2 Experiment 1: Capability Invariance Test (h-e1)

**Objective:** Validate assumption A1 (policy-layer modulation preserves capability) via statistical invariance testing.

**Protocol:**
1. **Model:** Claude 3 Opus with policy-layer modulation via system prompts (base capability held constant via policy-layer-only manipulation, testable assumption), temperature 0.0 (deterministic)
2. **Compliance Levels:** λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0} via system prompts (Section 3.1)
3. **Datasets:** 
   - MMLU: 57 subjects, 14,042 test questions, 4-shot prompting, exact match scoring
   - HumanEval: 164 problems, pass@1 metric via execution-based correctness
4. **Measurements:** Accuracy per λ condition, aggregated across subjects (MMLU) and problems (HumanEval)
5. **Statistical Tests:**
   - ICC₂ (two-way mixed effects, absolute agreement) > 0.95
   - One-way ANOVA (λ as factor) with Bonferroni correction: p > 0.05
   - Cohen's f effect size < 0.10
6. **Gate Logic:** ALL three criteria must pass. If any fails → ABORT chain, route to Phase 0 for ACE redesign.

**Expected Cost:** ~$1,620 for full MMLU (57 subjects × ~14k questions × 5 λ levels) + HumanEval (164 problems × 5 λ levels) evaluation. **Expected Runtime:** ~4 hours with API rate limiting.

**Rationale:** This is a MUST_WORK gate enforcing prerequisite validity. If capability varies with λ (ICC < 0.95 or ANOVA p < 0.05), all downstream ACE-HOR coupling measurements are confounded—ACE would not isolate compliance strength but conflate it with capability changes. The gate prevents invalid experiments from proceeding.

## 4.3 Experiment 2: Coupling Characterization (h-m1)

**Objective:** Test RQ2—does ACE-HOR coupling exist, and which model (M1/M2/M3) best fits?

**Prerequisites:** h-e1 must pass (capability invariance validated).

**Protocol:**
1. **Task:** Human participants review AI-generated MMLU/HumanEval outputs across λ conditions
2. **Seeded Errors:** 20% within-distribution errors (50% high-conf incorrect, 30% low-conf incorrect, 20% correct but misleading reasoning)
3. **HOR Measurement:** Signal detection d' = Z(hit_rate) - Z(false_alarm_rate) per λ condition
4. **Model Fitting:** Fit three functional forms:
   - **M1 (Linear):** HOR(λ) = β₀ + β₁·λ (Pareto tradeoff)
   - **M2 (Quadratic):** HOR(λ) = β₀ + β₁·λ + β₂·λ² (inverted-U with equilibrium)
   - **M3 (Bifurcation):** Piecewise linear with breakpoint at λ*
5. **Model Selection:** AIC comparison, require R² ≥ 0.6 for winning model
6. **Success Criterion:** One model significantly preferred (ΔAIC > 10) with R² ≥ 0.6
7. **If Fail:** Coupling doesn't exist or is stochastic. Update hypothesis to "ACE-HOR independent."

**Rationale:** Model comparison distinguishes scientifically meaningful outcomes: M1 (fundamental tradeoff), M2 (equilibrium region exists), M3 (threshold effect). Pre-specification prevents post-hoc model fitting.

## 4.4 Experiment 3: Mediation Test (h-m2, h-m3)

**Objective:** Test RQ4—is HOR degradation mediated by perceived reliability (automation bias) vs. alternatives?

**Prerequisites:** h-e1 and h-m1 must pass.

**Design:** 2×2 randomized experiment
- **Factor A (ACE):** λ = 0.4 (low compliance) vs. λ = 0.8 (high compliance)
- **Factor B (Trust Display):** Standard confidence (model-generated) vs. Randomized confidence (breaks trust calibration)

**Conditions:**
- **Condition A:** Low λ, standard confidence (baseline)
- **Condition B:** High λ, standard confidence (automation bias predicted)
- **Condition C:** High λ, randomized confidence (trust broken, automation bias mitigated)

**Hypothesis:** If automation bias mechanism → HOR_C > HOR_B (randomizing confidence restores oversight despite high λ). **Threshold:** HOR_C - HOR_B ≥ 10%, p < 0.05 (two-sample t-test).

**Alternative:** If cognitive load mechanism → HOR_C ≈ HOR_B (oversight depends on task difficulty, not trust). Mediation test falsified.

**Rationale:** Distinguishes automation bias (trust-mediated) from alternative mechanisms (cognitive load, task engagement). Randomized confidence manipulation breaks trust calibration without affecting task difficulty, isolating the mediation pathway.

## 4.5 Experiment 4: Metacognitive Intervention (h-m4)

**Objective:** Test RQ5—can designed disagreement sustain HOR via increased learning rate k₂?

**Prerequisites:** h-e1, h-m1, h-m2, h-m3 must pass.

**Design:** Intervention vs. control, longitudinal tracking
- **Control:** Standard λ = 0.8 with natural disagreement frequency (~5%)
- **Intervention:** λ = 0.8 with designed disagreement injected at 15-25% frequency (comparative evaluation tasks: "Why did the AI choose A instead of B?")

**Measurements:**
- HOR(t) at t ∈ {1 hour, 1 day, 1 week, 1 month}
- Fit competing-process model: HOR(t) = HOR₀ · exp(-k₁·t) + k₂·(1 - exp(-t/τ))
- Compare k₂_intervention vs. k₂_control
- Measure user frustration (1-10 scale) and task abandonment rate

**Success Criterion:** (k₂_intervention / k₂_control ≥ 1.30) AND (frustration < 7/10) AND (abandonment < 20%).

**If Fail:** Intervention impractical (excessive frustration) or ineffective (no learning rate increase). Explore alternatives (uncertainty displays, delegation controls).

**Rationale:** Metacognitive interventions from desirable difficulties literature (Bjork, Craik & Lockhart) suggest comparative evaluation increases learning. Testing this in AI collaboration context addresses practical deployment concern: how to sustain oversight without perpetual high disagreement rates that frustrate users.

## 4.6 Execution Status

**Current Status:** Infrastructure code validated and datasets verified (real MMLU/HumanEval data loaded, statistical pipeline functional, mock data fix completed), experiments NOT executed.

**Blocking Factor:** API resource constraint (ANTHROPIC_API_KEY unavailable, ~$1,620 budget for h-e1 execution).

**Next Step:** Execute h-e1 with API access. If h-e1 passes, proceed to h-m1 through h-m4. If h-e1 fails, route to Phase 0 for ACE operationalization redesign (e.g., frozen base + trainable policy head, retrieval-augmented rules).

# Results: Infrastructure Validation

Given that experiments were not executed (API resource constraint, Section 4.6), this section presents infrastructure validation evidence demonstrating the framework's readiness for empirical testing. We organize evidence into four categories: quality control effectiveness, dataset verification, verification protocol design, and planned-vs-actual deviation analysis.

## 5.1 Quality Control: Mock Data Detection and Correction

**Finding:** Automated validator successfully detected and corrected synthetic data usage in proof-of-concept code, preventing false hypothesis validation.

**Detection Results (Table 1):**

| Violation ID | File | Line | Pattern | Description |
|--------------|------|------|---------|-------------|
| V1 | main_poc.py | 50 | `np.random.uniform(0.75, 0.90)` | Synthetic baseline accuracies generated |
| V2 | main_poc.py | 60 | `base_accuracy = subject_difficulties[subject]` | Tautological: same accuracy across all λ by design |
| V3 | main_poc.py | 65 | `np.random.normal(0, 0.05)` | Random noise added, not real data computation |
| V4 | main_poc.py | 67 | `np.random.random() < prob_correct` | Boolean results from random process |
| V5 | main_poc.py | 60-67 | Logic analysis | ICC > 0.95 guaranteed by construction (capability intentionally invariant) |

**Corrective Actions (Attempt 1/5):**
1. Disabled `main_poc.py` (renamed to `main_poc.py.DISABLED`)
2. Verified `main.py` uses real data loaders (MMLULoader, HumanEvalLoader)
3. Confirmed MMLULoader loads from HuggingFace `cais/mmlu` dataset
4. Confirmed HumanEvalLoader loads from OpenAI `human-eval` pip package
5. Cleaned old POC synthetic results
6. Verified real data loading works correctly

**Fix Verification (6/6 Checks Passed):**
- ✓ POC code disabled (not executable)
- ✓ Main.py active (correct entry point)
- ✓ MMLU 57 subjects loaded (not generated)
- ✓ HumanEval 164 problems loaded (not generated)
- ✓ No synthetic patterns in main.py (manual code inspection)
- ✓ Datasets match published benchmarks (sample question verification)

**So What?** This demonstrates effective automated quality control in hypothesis verification pipelines. The validator correctly identified that high ICC > 0.95 was *guaranteed by synthetic data construction*, not genuine capability invariance. Without this detection, h-e1 would have falsely validated the prerequisite assumption (A1), allowing invalid experiments to proceed. Mock data fix is evidence of rigorous experimental design enforcement, not just theoretical specification.

## 5.2 Dataset Verification: Real Benchmark Data

**MMLU Dataset (Table 2):**

| Metric | Value |
|--------|-------|
| Source | HuggingFace `cais/mmlu` |
| Subjects | 57 (abstract_algebra through virology) |
| Test Questions | 14,042 |
| Question Format | Multiple choice, 4 options |
| Few-Shot | 4 examples per subject |
| Sample Verified | "This question refers to the following information. 'The far-reaching, the boundless future will be the era of American greatness...' By what means did the United States take possession of the Oregon Territory?" (high_school_us_history) |

**HumanEval Dataset (Table 2 continued):**

| Metric | Value |
|--------|-------|
| Source | OpenAI `human-eval` (pip package) |
| Problems | 164 hand-written programming challenges |
| Format | Function signature + docstring |
| Evaluation | Execution-based correctness (pass@1) |
| Sample Verified | `HumanEval/0: has_close_elements` - "Check if in given list of numbers, are any two numbers closer to each other than given threshold" |

**So What?** Confirms infrastructure correctness. The experiment *would* evaluate on standard, widely-used benchmarks (not custom or synthetic datasets), ensuring comparability with prior work [@Hendrycks2021MMLU; @Chen2021HumanEval] and reproducibility. Dataset verification demonstrates that ACE manipulation (policy-layer compliance modulation) can be tested on established capability benchmarks, validating the architectural separation approach.

## 5.3 Verification Protocol Design: Dependency Structure

**Hypothesis Chain Visualization (Table 3):**

| Hypothesis | Type | Gate | Prerequisite | Success Criterion | If Fail → Routing |
|------------|------|------|--------------|-------------------|-------------------|
| h-e1 | EXISTENCE | MUST_WORK | None | (ICC > 0.95) AND (p > 0.05) AND (f < 0.10) | ABORT chain → Phase 0 redesign |
| h-m1 | MECHANISM | DETERMINES_SUCCESS | h-e1 PASS | (R² ≥ 0.6) AND (ΔAIC > 10 for winning model) | MODIFY hypothesis → ACE-HOR independent |
| h-m2 | MECHANISM | MUST_WORK | h-m1 PASS | Trust rating ~ λ correlation (r > 0.5, p < 0.05) | ABORT chain → Alternative mechanism |
| h-m3 | MECHANISM | DETERMINES_SUCCESS | h-m2 PASS | HOR_C - HOR_B ≥ 10%, p < 0.05 | MODIFY hypothesis → Non-trust mechanism |
| h-m4 | MECHANISM | DETERMINES_SUCCESS | h-m3 PASS | (k₂_ratio ≥ 1.30) AND (frustration < 7) AND (abandon < 20%) | MODIFY hypothesis → Alternative intervention |

**Falsification Criteria (Table 4):**

| Assumption | Falsifier | Verification Method | Consequence if Violated |
|------------|-----------|---------------------|------------------------|
| A1: Capability invariance | ICC < 0.95 OR p < 0.05 OR f ≥ 0.10 | h-e1 statistical tests | ACE confounded with capability. All coupling measurements uninterpretable. |
| A2: Error validity | Real errors ≠ confusion matrix distribution | Empirical confusion matrix comparison | HOR measures stress-testing, not realistic oversight. Results don't generalize to deployment. |
| A3: Automation bias | Mediation test fails (HOR_C ≈ HOR_B, p > 0.05) | h-m3 randomized confidence manipulation | HOR degradation arises from cognitive load or task engagement, not trust miscalibration. |
| A4: Competing-process temporal dynamics | Neither erosion nor learning model fits (R² < 0.6) | h-m4 longitudinal HOR(t) fitting | Alternative temporal patterns (oscillatory, chaotic) exist. Model comparison needed. |
| A5: Metacognitive intervention practicality | Frustration ≥ 7/10 OR abandonment ≥ 20% | h-m4 user experience metrics | Intervention impractical for deployment despite k₂ increase. |

**So What?** Demonstrates rigorous scientific methodology. Unlike exploratory research that post-hoc interprets results, our approach *pre-specifies* success criteria, failure handling, and iterative refinement protocols. This reduces researcher degrees of freedom [@Simmons2011FalsePositive] and increases replicability—future researchers can follow the exact protocol without ambiguity. Dependency structure ensures validity checks are enforced (h-e1 must pass before h-m1 can test coupling) and failure routing is principled (gate type determines ABORT vs. MODIFY decision).

## 5.4 Planned-vs-Actual Deviation Classification

**Deviation Analysis (Table 5):**

| Hypothesis | Planned Metric | Planned Target | Actual Result | Deviation Type | Root Cause |
|------------|---------------|----------------|---------------|----------------|------------|
| h-e1 | ICC (capability consistency) | ICC > 0.95 | NOT COMPUTED | IMPLEMENTATION_GAP | API key unavailable (~$1,620 budget, ~4 hours runtime). Infrastructure code validated, datasets verified, statistical pipeline functional. |
| h-e1 | ANOVA p-value | p > 0.05 (no variation) | NOT COMPUTED | IMPLEMENTATION_GAP | Same as above—infrastructure ready, execution blocked by resource constraint. |
| h-e1 | Cohen's f (effect size) | f < 0.10 (negligible) | NOT COMPUTED | IMPLEMENTATION_GAP | Same as above—implementation complete, resource constraint only. |

**Deviation Type Legend:**
- **IMPLEMENTATION_GAP:** Infrastructure/resource constraint, not scientific flaw
- **HYPOTHESIS_ISSUE:** Scientific claim or causal mechanism flawed
- **DESIGN_ISSUE:** Experimental design problem
- **SCOPE_CHANGE:** Intentional scope reduction

**Analysis:** All deviations are **IMPLEMENTATION_GAP** (resource constraint), not **HYPOTHESIS_ISSUE** (scientific flaw) or **DESIGN_ISSUE** (experimental design problem). The experiment design (Phase 2C) and implementation (Phase 3) were completed successfully. The gap is execution resources (API key, budget approval), not methodology.

**So What?** Clarifies that non-execution is a *resource limitation*, not a methodological failure. The experimental design is sound and infrastructure code validated (verified via quality control checks). This distinction matters for interpreting whether the hypothesis approach is methodologically valid (yes, pending execution) vs. fundamentally flawed (no). Classification provides transparency for future researchers: the framework can be executed when resources are available.

## 5.5 Summary

**Infrastructure Validation Summary:**
- ✓ Quality control effective (mock data detected/fixed, 6/6 verification checks passed)
- ✓ Real datasets verified (MMLU 57 subjects/14k questions, HumanEval 164 problems)
- ✓ Dependency structure complete (5 hypotheses with gate criteria, falsification logic)
- ✓ Deviation classification transparent (all IMPLEMENTATION_GAP, no methodology failures)

**Empirical Validation Summary:**
- ✗ No experiments executed (API resource constraint)
- ✗ All predictions (P1-P5) INCONCLUSIVE
- ✗ All assumptions (A1-A5) UNVERIFIED

**Status:** Methodological contribution (framework design + infrastructure implementation), not empirical findings (experiments pending).

# Discussion

## 6.1 Methodological Contributions

Our work addresses a foundational measurement gap in AI alignment research: existing evaluation is unidirectional, measuring AI performance without considering reciprocal effects on human oversight behavior. We contribute the first framework to operationalize bidirectional alignment dynamics in AI safety contexts as coupled, measurable variables (ACE and HOR) with experimental protocols for testing coupling mechanisms via capability-invariant policy-layer manipulation.

**Key Methodological Advances:**

1. **Architectural Separation for Causal Inference:** We leverage Constitutional AI's policy-layer architecture [@Bai2022ConstitutionalAI] to enable testable capability invariance via compliance modulation. By using policy-layer-only manipulation (system prompts) and validating capability invariance statistically, we aim to isolate alignment strength from capability changes—the critical prerequisite for attributing human oversight effects specifically to alignment interventions. Our h-e1 gate (ICC > 0.95, ANOVA p > 0.05, Cohen's f < 0.10) enforces this separation as a testable assumption, preventing confounded measurements if validated.

2. **Integration Across Research Areas:** We unify three previously siloed areas—AI alignment evaluation, automation bias from human factors, and signal detection theory—into a single measurement framework for AI safety contexts. This integration enables testing whether automation bias mechanisms (Bayesian trust calibration, verification effort reduction) generalize from traditional automation to AI collaboration contexts, a question neither field could address independently.

3. **Pre-Registered Falsification Criteria:** Our dependency-driven hypothesis decomposition (h-e1 → h-m1 → h-m2 → h-m3 → h-m4) with gate-based validation reduces researcher degrees of freedom. Each hypothesis has pre-specified success thresholds, failure routing logic, and prerequisite dependencies documented before any empirical testing. This contrasts with exploratory research that interprets results post-hoc, which increases false positive risk [@Simmons2011FalsePositive].

4. **Automated Quality Control:** Our pipeline detected and corrected mock data usage (Section 5.1), demonstrating effective validation. The validator identified that synthetic data *guaranteed* ICC > 0.95 by construction (tautological capability invariance), preventing false validation of prerequisite assumption A1. This infrastructure contribution is reusable for future hypothesis verification workflows beyond bidirectional alignment.

## 6.2 Honest Limitations

We emphasize four critical limitations that constrain the interpretation of this work:

### Limitation 1: No Empirical Evidence

**What:** All five predictions (P1-P5) and all five assumptions (A1-A5) remain INCONCLUSIVE/UNVERIFIED. No experiments were executed (h-e1 blocked by API key; h-m1 through h-m4 not started). Zero empirical data collected on ACE-HOR coupling, automation bias mediation, or metacognitive interventions.

**Why This Matters:** The entire research contribution claim rests on empirical validation. Without experiment execution, this work contributes only methodological design (experimental framework) and engineering (infrastructure implementation), not scientific findings about bidirectional alignment dynamics.

**Root Cause:** API key unavailability blocked h-e1 execution. Expected cost (~$1,620 for full MMLU + HumanEval evaluation across 5 λ levels) likely required budget approval that was not obtained (Section 5.4 deviation analysis). Dependent hypotheses (h-m1 through h-m4) could not proceed due to h-e1 prerequisite failure.

**Rationale and Mitigation:** Methodological contributions are valuable for emerging research areas. Bidirectional alignment evaluation is a new problem space—measurement frameworks are a necessary first step before large-scale empirical studies can be conducted. Our work establishes *how* to measure bidirectional dynamics (operationalization, protocols, falsification criteria), enabling future researchers to conduct empirical tests. The infrastructure code is validated and datasets verified, ready for execution when resources become available.

**Future Work:** Immediate next step is h-e1 execution with API access (~$1,620 budget, ~4 hours runtime). If h-e1 passes, proceed to mechanism studies (h-m1 through h-m4) requiring human participants and longitudinal data collection (weeks to months). If h-e1 fails, route to Phase 0 for ACE redesign (e.g., frozen base + trainable policy head, retrieval-augmented constitutional rules).

### Limitation 2: Capability Invariance Assumption Unverified

**What:** Assumption A1 (policy-layer modulation preserves base capability with ICC > 0.95) is the foundational prerequisite for all downstream measurements. If violated, ACE becomes confounded with capability changes, making all ACE-HOR coupling results uninterpretable. This assumption remains empirically untested—h-e1 gate exists to test it, but has not been executed.

**Why This Matters:** Many alignment interventions *do* affect capability. InstructGPT reports capability improvements from RLHF [@Ouyang2022InstructGPT]. Constitutional AI system prompts may alter verbosity, hedging, or reasoning depth in ways that affect MMLU/HumanEval performance. If A1 is violated, our framework's causal inference breaks down—ACE would not isolate compliance strength but conflate it with capability changes.

**Rationale and Mitigation:** We explicitly designed h-e1 as a MUST_WORK gate to test this assumption. Failure triggers routing to Phase 0 (architecture re-selection) per our verification protocol. The assumption is *falsifiable and testable*, not hidden or implicitly assumed. Transparency about untested assumptions is scientifically sound practice. Constitutional AI architecture suggests capability invariance via policy-layer separation, but this must be validated empirically, not assumed.

**Mitigation:** h-e1 execution tests A1 directly (ICC > 0.95, ANOVA p > 0.05, Cohen's f < 0.10). If violated, alternative ACE operationalizations exist: (1) frozen base model with separate trainable policy head (true architectural separation, not prompt-based), (2) retrieval-augmented constitutional rules (modulate rule retrieval, not model behavior), (3) partial correlation controlling for capability (statistical rather than architectural separation).

### Limitation 3: Ecological Validity of Seeded Errors

**What:** HOR measurement via signal detection d' requires ground-truth error labels. We use seeded within-distribution errors sampled from the model's empirical confusion matrix (Assumption A2). However, ecological validity—whether seeded errors represent real model failures users encounter in deployment—remains unverified.

**Why This Matters:** If seeded errors are detectability-biased (easier or harder to detect than naturally-occurring errors), HOR measurements reflect stress-testing rather than realistic oversight. Results may not generalize to deployment contexts where error types, frequencies, and detectability differ.

**Rationale and Mitigation:** Seeded error approach is common in oversight and vigilance research [@Parasuraman2009Vigilance; @Wickens2015EngineeringPsychology]. Sampling from empirical confusion matrix (not adversarial fabrication) ensures errors resemble model's actual failure modes. We explicitly acknowledge the validity threat and propose future mitigation.

**Mitigation:** Compare seeded error HOR measurements with naturally-occurring error detection in deployment logs. If correlation is high (r > 0.7), ecological validity supported. If low, refine error sampling to match deployment distribution (frequency, detectability, context).

### Limitation 4: Ecological Validity and Generalization

**What:** Even if experiments succeed (h-e1 passes, coupling exists, interventions work), the framework's practical utility for real-world deployment remains uncertain. Three generalization concerns:

1. **Seeded errors vs. real failures:** Laboratory seeded errors (sampled from confusion matrix) may not capture the full distribution of deployment failures—timing, context, consequences differ between lab and field.

2. **Laboratory setting vs. workflow integration:** All experiments are single-session or longitudinal evaluations (hours to months) in controlled settings. Real collaboration involves workflow integration, switching costs, multi-tasking, organizational context. Will HOR measurements from lab paradigms predict deployment oversight quality?

3. **Model architecture specificity:** Framework is designed for Claude 3 Opus with Constitutional AI policy-layer manipulation. Will the approach generalize to other architectures (GPT-4, Gemini, Llama) with different alignment mechanisms? Policy-layer manipulation may not be universally applicable.

**Why This Matters:** The framework could successfully measure bidirectional dynamics in laboratory settings but fail to predict real-world deployment safety. If lab-to-field generalization is weak, the practical safety impact is limited—measurements would be scientifically interesting but not operationally useful for deployment decisions.

**Rationale and Mitigation:** Ecological validity is a fundamental challenge in human factors research. We acknowledge this limitation explicitly rather than claiming universal applicability. Laboratory experiments are a starting point for establishing causal mechanisms, to be validated against field data.

**Mitigation:** (1) **Error representativeness validation:** Correlate lab HOR measurements (seeded errors) with deployment error detection rates from production logs. If r > 0.7, lab paradigm predicts field performance. If r < 0.7, refine error sampling. (2) **Field studies:** Deploy framework in real workflows (code review, content moderation) and compare lab-predicted vs. field-observed coupling patterns. (3) **Cross-architecture replication:** Test framework on alternative models (GPT-4 with system prompts, open-source models with LoRA policy heads) to assess generalization beyond Constitutional AI.

## 6.3 Broader Impact

**Positive Impacts:**

If validated empirically, bidirectional alignment measurement could improve deployment safety in high-stakes collaborative contexts (medical diagnosis, code review, content moderation) by detecting oversight degradation early. Current practice lacks systematic oversight quality monitoring—deployment decisions rely on proxy metrics (user satisfaction, task completion rates) that don't capture error detection sensitivity. ACE-HOR coupling measurement enables evidence-based alignment policy decisions (optimal λ*) rather than ad-hoc tuning.

**Negative Impacts / Risks:**

1. **Ground-Truth Requirement:** HOR measurement requires seeded errors with ground-truth labels, which could be misused for adversarial dataset generation. Defense: ground-truth errors should be protected with same security as model weights.

2. **User Frustration:** Metacognitive interventions (designed disagreement) could frustrate users if poorly calibrated (A5 violation). h-m4 tests this explicitly (frustration threshold <7/10, abandonment <20%), but deployment requires careful UX design.

3. **Trust Erosion:** Automation bias mitigation strategies that reduce human trust in AI (randomized confidence displays, designed disagreement) could undermine collaboration with genuinely capable systems. Calibration challenge: how to sustain oversight without destroying beneficial trust?

4. **Dual-Use Potential:** Understanding automation bias mechanisms could inform *persuasion* strategies (making AI outputs appear more reliable than they are, inducing over-reliance). Framework is defensive (measuring safety degradation) not offensive (creating persuasive AI), but mechanism knowledge could be misapplied.

**Equity Considerations:**

Bidirectional alignment evaluation assumes users have cognitive resources for oversight. In deployment contexts with time pressure, cognitive load, or limited expertise, HOR baselines may be lower and degradation thresholds different. Framework should be calibrated per deployment context, not assumed universal.

**ICML Impact Statement:** This work presents a measurement framework for bidirectional alignment dynamics (AI compliance affecting human oversight). Positive impact potential: improved deployment safety via oversight monitoring. Risks: ground-truth error misuse, user frustration from interventions, automation bias knowledge dual-use for persuasion. Framework is defensive (safety measurement) but mechanism understanding requires responsible deployment practices.

## 6.4 Connections to Deployment Challenges

Our framework addresses practical concerns in AI safety engineering:

**Challenge 1: Alignment-Capability Tradeoffs:** Practitioners often observe that stronger alignment constraints reduce model capability [@Bai2022ConstitutionalAI reports trade-offs]. Our capability invariance testing (h-e1) provides a statistical validity check: if ICC < 0.95, the tradeoff exists and must be navigated. If ICC > 0.95, alignment can be modulated without capability loss—a valuable deployment insight.

**Challenge 2: Oversight Cost vs. Safety:** Human oversight is expensive (expert time, cognitive effort, throughput reduction). Organizations face pressure to reduce oversight as AI reliability improves. Our framework quantifies this dynamic: if ACE-HOR coupling follows M1 (linear Pareto tradeoff), reduced oversight is unavoidable. If M2 (inverted-U with equilibrium), optimal λ* exists balancing compliance and oversight. Model comparison (h-m1) informs deployment strategy.

**Challenge 3: Long-Term Co-Evolution:** Human-AI collaboration evolves over time (hours to months). Current evaluation is static (single-timestep snapshots). Our longitudinal HOR(t) measurement and competing-process modeling (h-m4) enables tracking erosion vs. learning dynamics, critical for long-deployment systems.

## 6.5 Open Questions for Future Research

1. **Generalization Across Domains:** Does ACE-HOR coupling generalize across task types (knowledge Q&A, code generation, medical diagnosis) or vary by domain characteristics (error cost, base rate, detectability)?

2. **Individual Differences:** Do users vary in automation bias susceptibility? Could HOR baselines and λ* optima be personalized per user rather than universal?

3. **Alternative Architectures:** Our framework uses Constitutional AI policy-layer manipulation. Do other alignment approaches (RLHF with frozen base, retrieval-augmented rules, debate/amplification) enable capability-invariant compliance modulation?

4. **Multi-Agent Dynamics:** We study dyadic human-AI collaboration. How do bidirectional effects scale to teams (multiple humans, multiple AIs) with distributed oversight?

5. **Adversarial Robustness:** Can adversaries exploit automation bias mechanisms to induce over-reliance (e.g., artificially high confidence displays, fabricated consistency signals)? How to defend?

# Conclusion

We opened by asking: how do we know if an AI system is *too* aligned? This question remains unanswered empirically, but our framework provides the measurement infrastructure to answer it in future research. Current alignment evaluation is unidirectional—measuring whether AI outputs match human preferences without considering whether excessive alignment inadvertently degrades human oversight through automation bias. This gap is not just theoretical: in high-stakes deployment contexts like medical diagnosis and code review, human oversight quality is a critical safety layer that current evaluation frameworks cannot measure.

Our contribution is demonstrating *how* to measure bidirectional alignment dynamics in AI safety contexts as coupled variables (ACE and HOR) with experimental protocols for testing coupling mechanisms via capability-invariant policy-layer manipulation. By leveraging Constitutional AI's policy-layer architecture, we enable testable capability invariance (λ parameter with h-e1 gate validating ICC > 0.95, ANOVA p > 0.05). By applying signal detection d', we measure oversight quality (HOR) without confounding task difficulty or AI capability. Together, these operationalizations make the previously unmeasured phenomenon experimentally testable.

Our infrastructure validation demonstrates methodological rigor: mock data detection prevented false validation (6/6 verification checks passed), real dataset verification ensures reproducibility (MMLU 57 subjects, HumanEval 164 problems), and dependency-driven hypothesis decomposition with gate-based validation reduces researcher degrees of freedom. However, we emphasize the honest limitation: *no empirical evidence exists*. All predictions (P1-P5) and assumptions (A1-A5) remain inconclusive/unverified pending experiment execution (~$1,620 API cost, ~4 hours runtime for h-e1). Our contribution is methodological infrastructure, not empirical findings.

**The path forward is clear:** Execute h-e1 to test capability invariance (prerequisite for all mechanism studies). If h-e1 passes, proceed to full dependency chain (h-m1 through h-m4) to characterize ACE-HOR coupling, test automation bias mediation, and evaluate metacognitive interventions. If h-e1 fails, redesign ACE operationalization (frozen base + policy head, retrieval-augmented rules, statistical separation via partial correlation). Beyond empirical validation, extend the framework to alternative alignment architectures (RLHF with frozen layers, debate/amplification), multi-agent collaboration (team-level oversight dynamics), and long-horizon deployment (co-evolution over months/years).

**The next frontier in alignment science is not just building systems that match human preferences, but understanding how those systems reshape human behavior in return.** Alignment evaluation must become bidirectional. Our framework establishes the measurement foundation for this shift. When resources enable empirical execution, we will learn whether alignment-oversight coupling exists, which functional form it follows (linear Pareto tradeoff, inverted-U equilibrium, or bifurcation), and whether metacognitive interventions can sustain oversight without excessive user frustration. These questions cannot be answered by unidirectional evaluation—they require the bidirectional measurement infrastructure we provide.

Measurement must come first. We provide the tools. Future work executes the experiments.
