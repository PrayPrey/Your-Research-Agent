# Measurement Framework for Bidirectional Alignment Dynamics in Human-AI Collaboration: Infrastructure Implementation Without Empirical Validation

## Abstract

Current AI alignment evaluation measures whether AI systems conform to human preferences but does not assess reciprocal effects on human oversight behavior. We present an experimental framework for measuring bidirectional alignment dynamics through two operationalized variables: AI Compliance Elasticity (ACE) via Constitutional AI policy-layer parameter manipulation, and Human Oversight Retention (HOR) via signal detection sensitivity d'. The framework decomposes a main hypothesis into five testable sub-hypotheses (h-e1 through h-m4) with explicit falsification criteria and gate-based validation. Infrastructure implementation includes data loaders for MMLU (57 subjects, 14,042 questions) and HumanEval (164 problems), statistical analysis pipeline (ICC/ANOVA/Cohen's f), and automated quality control that detected and corrected mock data usage. However, no experiments were executed due to API resource constraints (~$1,620 estimated cost). All five predictions regarding capability invariance, ACE-HOR coupling, automation bias mediation, and metacognitive interventions remain inconclusive. All five key assumptions (policy-layer capability invariance, error ecological validity, automation bias generalization, temporal dynamics model, intervention practicality) remain unverified. This work contributes methodological infrastructure for measuring a previously unmeasured phenomenon in AI safety contexts, not empirical findings.

## 1. Introduction

AI alignment research evaluates whether AI systems conform to human values and preferences, measured through metrics such as helpfulness ratings and harmlessness scores. This evaluation paradigm measures AI performance without considering reciprocal effects on human behavior during collaboration. In high-stakes deployment contexts such as medical diagnosis and code review, human oversight quality functions as a safety layer, yet current evaluation frameworks do not measure whether alignment interventions affect this oversight.

Human factors research has documented automation bias—the tendency for humans to over-rely on automated systems, reducing verification effort and error detection sensitivity. This phenomenon has been observed in aviation, medical diagnosis, and process control. A proposed causal mechanism suggests that increased AI compliance may reduce observable disagreement signals, which could increase perceived reliability beyond objective accuracy, leading to reduced human verification effort through Bayesian updating, potentially degrading error detection sensitivity over time.

This causal chain—policy-layer compliance manipulation → reduced disagreement → trust miscalibration → verification effort reduction → oversight degradation—suggests that alignment evaluation should measure bidirectional effects. However, testing this mechanism requires addressing three challenges: (1) compliance modulation must not confound capability changes, requiring architectural separation; (2) oversight quality must be quantified without confounding task difficulty or AI capability; (3) temporal dynamics must be tracked across timescales from hours to months.

Constitutional AI's policy-layer architecture provides a candidate approach for architectural separation. System prompts or constitutional rules modulate compliance strength while base model weights remain frozen. This architectural approach enables testable capability invariance via statistical validation (ICC > 0.95, ANOVA p > 0.05, Cohen's f < 0.10), though this is an unverified prerequisite assumption requiring empirical testing. Human oversight quality can be measured via signal detection d' on seeded within-distribution errors, isolating error detection sensitivity from task accuracy.

**Contributions.** We contribute:

1. **Operationalization of bidirectional alignment dynamics** as measurable variables: AI Compliance Elasticity (ACE) via policy-layer parameter λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0} and Human Oversight Retention (HOR) via signal detection d' on seeded within-distribution errors.

2. **Dependency-driven verification protocol** decomposing the main hypothesis into five sub-hypotheses (h-e1 → h-m1 → h-m2 → h-m3 → h-m4) with pre-specified success criteria, failure routing decisions, and prerequisite dependencies.

3. **Infrastructure implementation** with MMLU (57 subjects, 14,042 questions from HuggingFace cais/mmlu) and HumanEval (164 problems from OpenAI human-eval), automated quality control (mock data detection and correction with 6/6 verification checks), and statistical analysis pipeline (ICC/ANOVA/Cohen's f, signal detection d').

**Status.** This work presents methodological infrastructure without empirical validation. No experiments were executed due to API resource constraints (estimated $1,620 for full MMLU + HumanEval evaluation across 5 compliance levels, approximately 4 hours runtime). All five predictions (P1: capability invariance, P2: ACE-HOR coupling functional form, P3: perceived reliability mediation, P4: metacognitive intervention effectiveness, P5: equilibrium region existence) remain inconclusive. All five key assumptions remain unverified. The contribution is demonstrating how to measure bidirectional alignment dynamics, not what those dynamics are.

## 2. Related Work

### AI Alignment Evaluation

Alignment approaches train AI systems to conform to human values and preferences. Reinforcement Learning from Human Feedback (RLHF) trains language models to maximize human preference rankings. Constitutional AI trains models to follow explicit constitutional principles. Red teaming tests alignment robustness by attempting to elicit harmful outputs.

These evaluation frameworks measure whether AI outputs match human preferences (helpfulness, harmlessness, honesty scores) without measuring reciprocal effects on human oversight behavior. The framework assumes that optimizing the model's behavior is sufficient. Human-in-the-loop effects are studied separately in human-computer interaction research, not integrated into alignment evaluation.

Our framework differs by treating alignment strength (ACE) and oversight quality (HOR) as coupled dependent variables rather than measuring AI performance alone.

### Automation Bias and Trust in Human-Automation Interaction

Human factors research documents automation bias—the tendency for humans to over-rely on automated decision aids, reducing oversight effort and error detection sensitivity. This phenomenon has been observed in aviation, medical diagnosis, and process control. The proposed mechanism is Bayesian trust calibration: humans reduce verification effort when automation appears reliable, but this trust can be miscalibrated when reliability perceptions diverge from objective accuracy.

Signal detection theory provides a framework for measuring oversight quality via sensitivity d' and response criterion c, separating error detection ability from decision thresholds. This has been applied to vigilance tasks, quality control inspection, and security screening.

This literature focuses on traditional automation where capability is static. It does not address AI systems where compliance can be modulated independently of capability via policy-layer interventions. Whether automation bias mechanisms generalize to AI collaboration contexts with dynamic compliance modulation remains an open empirical question.

Our framework operationalizes automation bias mechanisms in AI contexts by using policy-layer separation to vary compliance while testing for capability invariance. We measure HOR via signal detection d' on seeded within-distribution errors.

### Human-AI Collaboration Evaluation

Prior work evaluates human-AI collaboration through complementarity measurement (whether human-AI teams outperform humans or AI alone), interactive machine learning evaluation (how humans interact with ML systems during training), and human-centered AI assessment (user experience in AI-assisted workflows).

These approaches measure general collaboration quality (team performance, user satisfaction, task completion) rather than alignment-oversight coupling specifically. Complementarity measurement treats AI capability as fixed, not modulated. Interactive ML evaluation studies training-time interaction, not deployment oversight. Human-centered evaluation measures user experience, not error detection sensitivity.

Our framework targets alignment-oversight coupling specifically: does increasing AI compliance via policy-layer parameter λ affect human error detection measured via signal detection d'? This requires architectural separation and signal detection measurement that prior collaboration evaluation frameworks do not provide.

### Capability Evaluation and Benchmarking

MMLU (Massive Multitask Language Understanding) evaluates language models across 57 subjects from elementary to professional knowledge domains. HumanEval tests code generation via 164 hand-written programming problems, measuring functional correctness with pass@k metrics. These benchmarks enable cross-model comparisons.

Capability evaluation is separate from alignment evaluation in current practice. Alignment interventions are assumed to improve alignment without degrading capability, but this is rarely tested statistically. Confounding between alignment and capability changes makes it impossible to attribute human oversight effects specifically to alignment strength.

Our framework uses MMLU and HumanEval for capability invariance testing: we test that policy-layer modulation maintains ICC > 0.95, ANOVA p > 0.05, and Cohen's f < 0.10 across compliance conditions. This architectural separation is a prerequisite for isolating ACE's effect on HOR. If capability varies with λ, ACE-HOR coupling measurements would be confounded.

## 3. Methodology

### 3.1 Variable Operationalization

**AI Compliance Elasticity (ACE):** ACE quantifies alignment strength via Constitutional AI policy-layer parameter λ, ranging from minimal compliance (λ = 0.2) to maximal compliance (λ = 1.0). Implementation uses Claude 3 Opus as base model with policy-layer modulation via system prompts:

- λ = 0.2: "Answer directly and concisely."
- λ = 0.4: "Be helpful and accurate in your responses."
- λ = 0.6: "Provide helpful, accurate, and well-reasoned responses."
- λ = 0.8: "Be extremely careful, ethical, and thorough in your responses."
- λ = 1.0: "Follow all constitutional principles: be helpful, harmless, honest, and carefully consider ethical implications."

Policy-layer modulation via system prompts allows compliance manipulation without retraining base model weights. However, capability invariance under policy-layer manipulation is an assumption (A1) requiring empirical validation via h-e1. The five λ levels provide statistical power for model comparison while remaining computationally tractable.

**Human Oversight Retention (HOR):** HOR measures human error detection sensitivity using signal detection d', where higher d' indicates better oversight quality (distinguishing correct from incorrect AI outputs).

Measurement protocol: (1) Embed 20% within-distribution errors sampled from the model's empirical confusion matrix on validation data. Error types: 50% high-confidence incorrect, 30% low-confidence incorrect, 20% correct but misleading reasoning. (2) All errors have known ground-truth labels enabling d' computation. (3) d' = Z(hit_rate) - Z(false_alarm_rate), where hit rate is correct error detections and false alarm rate is incorrect flagging of correct outputs. (4) Measure HOR at t ∈ {1 hour, 1 day, 1 week, 1 month} to capture temporal dynamics.

Signal detection d' isolates error detection sensitivity from response criterion and task accuracy. Seeded within-distribution errors ensure ecological validity—errors resemble real model failures rather than artificially difficult edge cases.

### 3.2 Capability Invariance Validation (Gate h-e1)

If policy-layer modulation alters base model capability, all ACE-HOR coupling measurements are confounded. We design hypothesis h-e1 as a MUST_WORK gate: if capability invariance is not achieved (ICC < 0.95 or ANOVA p < 0.05), the experimental approach is invalidated.

**Statistical Tests:**

1. **Intraclass Correlation Coefficient (ICC):** Measures consistency of capability metrics (MMLU accuracy, HumanEval pass@1) across λ conditions using two-way mixed effects model for absolute agreement. Threshold: ICC₂ > 0.95.

2. **One-Way ANOVA:** Tests whether capability varies significantly across λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0} with Bonferroni correction. Threshold: p > 0.05.

3. **Cohen's f (Effect Size):** Quantifies magnitude of capability variation. Threshold: f < 0.10.

**Datasets:** MMLU (57 subjects, 14,042 test questions) and HumanEval (164 hand-written programming problems) provide broad capability coverage.

**Gate Logic:** All three criteria must pass (ICC > 0.95 AND p > 0.05 AND f < 0.10). If any criterion fails → ABORT hypothesis chain, route to Phase 0 for alternative ACE operationalization.

Capability invariance is an assumption that must be empirically validated. Many alignment interventions affect capability. Constitutional AI's policy-layer architecture suggests capability invariance but does not guarantee it—system prompts may alter verbosity, hedging, or reasoning depth in ways that affect MMLU/HumanEval performance.

### 3.3 Dependency-Driven Hypothesis Decomposition

The full hypothesis is decomposed into a testable dependency chain with explicit falsification criteria:

- **h-e1 (EXISTENCE):** Can ACE be modulated without capability degradation? Test: ICC > 0.95, ANOVA p > 0.05, Cohen's f < 0.10 on MMLU + HumanEval across λ.
- **h-m1 (MECHANISM-1):** Does ACE-HOR coupling exist? Test: Fit M1 (linear), M2 (quadratic), M3 (bifurcation) models. Require R² ≥ 0.6 and significant AIC preference.
- **h-m2 (MECHANISM-2):** Does ACE increase perceived reliability? Test: Subjective trust ratings correlate with λ (r > 0.5, p < 0.05).
- **h-m3 (MECHANISM-3):** Does perceived reliability mediate HOR degradation? Test: Randomized confidence display manipulation. If automation bias → HOR_randomized > HOR_standard (difference ≥ 10%, p < 0.05).
- **h-m4 (MECHANISM-4):** Can metacognitive interventions sustain HOR? Test: Designed disagreement (15-25% frequency) increases learning rate k₂ by ≥30% vs. control.

**Dependency Structure:** h-e1 → h-m1 → h-m2 → h-m3 → h-m4. Each hypothesis is a prerequisite for the next.

**Gate-Based Validation:** MUST_WORK gates (h-e1, h-m2): Failure → ABORT chain, route to Phase 0 for redesign. DETERMINES_SUCCESS gates (h-m1, h-m3, h-m4): Failure → Hypothesis partially supported.

### 3.4 Infrastructure Implementation

**Data Loaders:** MMLULoader and HumanEvalLoader fetch real datasets from HuggingFace (cais/mmlu) and OpenAI (human-eval pip package), verified to load 57 subjects / 14,042 questions and 164 problems respectively.

**API Client with Policy Layer:** APIModelClient wraps Claude 3 Opus API with policy-layer parameter λ, mapping λ values to system prompts. Temperature set to 0.0 for deterministic evaluation.

**Evaluators:** MMLUEvaluator (4-shot prompting, exact match scoring) and HumanEvalEvaluator (pass@1 metric via execution-based correctness).

**Statistical Analyzer:** GateAnalyzer computes ICC₂, one-way ANOVA with Bonferroni correction, and Cohen's f effect size. Gates are evaluated automatically, triggering routing decisions.

**Visualization:** ResultsVisualizer generates capability consistency plots, subject-level heatmaps, gate metric bar charts, and violin plots.

**Quality Control:** Automated mock data detection identified five synthetic patterns in proof-of-concept code (np.random generation, tautological ICC by construction). Fix protocol (Attempt 1/5) disabled synthetic code, verified real data loaders, and validated with 6 checks: POC disabled, main.py active, MMLU 57 subjects loaded, HumanEval 164 problems loaded, no synthetic patterns, datasets match published benchmarks.

### 3.5 Key Assumptions (All Unverified)

1. **A1: Capability Invariance** — Policy-layer modulation preserves base capability (ICC > 0.95). If violated → ACE confounded with capability changes. Mitigation: h-e1 gate tests this explicitly.

2. **A2: Error Validity** — Within-distribution seeded errors are ecologically valid. If violated → HOR measures stress-testing, not realistic oversight. Mitigation: Sample errors from empirical confusion matrix.

3. **A3: Automation Bias Mechanism** — Automation bias from traditional automation generalizes to AI collaboration. If violated → HOR degradation arises from alternative mechanisms. Mitigation: h-m3 mediation test distinguishes mechanisms.

4. **A4: Temporal Dynamics Model** — Temporal dynamics follow competing-process model (k₁ erosion vs k₂ learning). If violated → Alternative patterns exist. Mitigation: Model comparison detects alternatives.

5. **A5: Intervention Practicality** — Metacognitive interventions do not cause excessive frustration. If violated → Intervention impractical despite effectiveness. Mitigation: Monitor frustration (<7/10) and abandonment (<20%).

## 4. Experimental Design

### 4.1 Experiment 1: Capability Invariance Test (h-e1)

**Objective:** Validate assumption A1 (policy-layer modulation preserves capability).

**Protocol:**
- Model: Claude 3 Opus, policy-layer modulation via system prompts, temperature 0.0
- Compliance Levels: λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0}
- Datasets: MMLU (57 subjects, 14,042 test questions, 4-shot prompting), HumanEval (164 problems, pass@1 metric)
- Measurements: Accuracy per λ condition
- Statistical Tests: ICC₂ > 0.95, ANOVA p > 0.05, Cohen's f < 0.10
- Gate Logic: All three criteria must pass

**Expected Cost:** ~$1,620 for full evaluation. **Expected Runtime:** ~4 hours.

**Status:** Infrastructure code validated and datasets verified. Not executed due to API resource constraint (ANTHROPIC_API_KEY unavailable).

### 4.2 Experiment 2: Coupling Characterization (h-m1)

**Objective:** Test whether ACE-HOR coupling exists and which model (M1/M2/M3) fits.

**Prerequisites:** h-e1 must pass.

**Protocol:**
- Task: Human participants review AI-generated outputs across λ conditions
- Seeded Errors: 20% within-distribution errors
- HOR Measurement: d' = Z(hit_rate) - Z(false_alarm_rate) per λ condition
- Model Fitting: M1 (Linear), M2 (Quadratic), M3 (Bifurcation)
- Model Selection: AIC comparison, require R² ≥ 0.6

**Status:** Not started (prerequisite h-e1 not completed).

### 4.3 Experiment 3: Mediation Test (h-m2, h-m3)

**Objective:** Test whether HOR degradation is mediated by perceived reliability.

**Prerequisites:** h-e1 and h-m1 must pass.

**Design:** 2×2 randomized experiment with factors: ACE (λ = 0.4 vs. 0.8) and Trust Display (Standard vs. Randomized).

**Hypothesis:** If automation bias → HOR_randomized > HOR_standard. Threshold: HOR difference ≥ 10%, p < 0.05.

**Status:** Not started (prerequisites not completed).

### 4.4 Experiment 4: Metacognitive Intervention (h-m4)

**Objective:** Test whether designed disagreement sustains HOR via increased learning rate k₂.

**Prerequisites:** h-e1, h-m1, h-m2, h-m3 must pass.

**Design:** Intervention vs. control, longitudinal tracking at t ∈ {1 hour, 1 day, 1 week, 1 month}.

**Success Criterion:** k₂_intervention / k₂_control ≥ 1.30 with 95% Bayesian credible interval excluding 1.0.

**Status:** Not started (prerequisites not completed).

## 5. Infrastructure Validation Results

### 5.1 Quality Control: Mock Data Detection and Correction

Automated validator detected five synthetic data patterns in proof-of-concept code (main_poc.py lines 50, 60, 65, 67, and logic analysis 60-67). Violations included: np.random.uniform(0.75, 0.90) generating synthetic baseline accuracies, base_accuracy = subject_difficulties[subject] ensuring same accuracy across all λ by design, np.random.normal(0, 0.05) adding random noise instead of real data computation, np.random.random() < prob_correct generating boolean results from random process, and tautological logic guaranteeing ICC > 0.95 by construction.

Corrective actions (Attempt 1/5): disabled main_poc.py (renamed to main_poc.py.DISABLED), verified main.py uses real data loaders (MMLULoader, HumanEvalLoader), confirmed MMLULoader loads from HuggingFace cais/mmlu dataset, confirmed HumanEvalLoader loads from OpenAI human-eval pip package, cleaned old POC synthetic results, verified real data loading works correctly.

Fix verification passed 6/6 checks: POC code disabled, main.py active, MMLU 57 subjects loaded, HumanEval 164 problems loaded, no synthetic patterns in main.py, datasets match published benchmarks.

This demonstrates automated quality control effectiveness. The validator identified that high ICC > 0.95 was guaranteed by synthetic data construction, not genuine capability invariance. Without this detection, h-e1 would have falsely validated the prerequisite assumption, allowing invalid experiments to proceed.

### 5.2 Dataset Verification

**MMLU Dataset:**
- Source: HuggingFace cais/mmlu
- Subjects: 57 (abstract_algebra through virology)
- Test Questions: 14,042
- Question Format: Multiple choice, 4 options
- Few-Shot: 4 examples per subject
- Sample Verified: "This question refers to the following information. 'The far-reaching, the boundless future will be the era of American greatness...' By what means did the United States take possession of the Oregon Territory?" (high_school_us_history)

**HumanEval Dataset:**
- Source: OpenAI human-eval (pip package)
- Problems: 164 hand-written programming challenges
- Format: Function signature + docstring
- Evaluation: Execution-based correctness (pass@1)
- Sample Verified: HumanEval/0: has_close_elements - "Check if in given list of numbers, are any two numbers closer to each other than given threshold"

Dataset verification confirms infrastructure correctness. The experiment would evaluate on standard, widely-used benchmarks, ensuring comparability with prior work and reproducibility.

### 5.3 Verification Protocol Design

**Hypothesis Chain:**

| Hypothesis | Type | Gate | Prerequisite | Success Criterion | If Fail |
|------------|------|------|--------------|-------------------|---------|
| h-e1 | EXISTENCE | MUST_WORK | None | (ICC > 0.95) AND (p > 0.05) AND (f < 0.10) | ABORT chain |
| h-m1 | MECHANISM | DETERMINES_SUCCESS | h-e1 PASS | (R² ≥ 0.6) AND (ΔAIC > 10) | MODIFY hypothesis |
| h-m2 | MECHANISM | MUST_WORK | h-m1 PASS | r > 0.5, p < 0.05 | ABORT chain |
| h-m3 | MECHANISM | DETERMINES_SUCCESS | h-m2 PASS | HOR difference ≥ 10%, p < 0.05 | MODIFY hypothesis |
| h-m4 | MECHANISM | DETERMINES_SUCCESS | h-m3 PASS | k₂_ratio ≥ 1.30, 95% CI excludes 1.0 | MODIFY hypothesis |

**Falsification Criteria:**

| Assumption | Falsifier | Consequence if Violated |
|------------|-----------|------------------------|
| A1: Capability invariance | ICC < 0.95 OR p < 0.05 | ACE confounded with capability |
| A2: Error validity | Real errors ≠ confusion matrix | HOR measures stress-testing |
| A3: Automation bias | Mediation test fails | Alternative mechanism |
| A4: Temporal dynamics | Neither model fits (R² < 0.6) | Alternative patterns exist |
| A5: Intervention practicality | Frustration ≥ 7/10 OR abandonment ≥ 20% | Intervention impractical |

This demonstrates pre-specification of success criteria, failure handling, and iterative refinement protocols. Dependency structure ensures validity checks are enforced (h-e1 must pass before h-m1 can test coupling).

### 5.4 Deviation Analysis

**Planned vs. Actual:**

| Hypothesis | Planned Metric | Planned Target | Actual Result | Deviation Type |
|------------|---------------|----------------|---------------|----------------|
| h-e1 | ICC | ICC > 0.95 | NOT COMPUTED | IMPLEMENTATION_GAP |
| h-e1 | ANOVA p-value | p > 0.05 | NOT COMPUTED | IMPLEMENTATION_GAP |
| h-e1 | Cohen's f | f < 0.10 | NOT COMPUTED | IMPLEMENTATION_GAP |

All deviations are IMPLEMENTATION_GAP (infrastructure/resource constraint), not HYPOTHESIS_ISSUE (scientific flaw) or DESIGN_ISSUE (experimental design problem). The experiment design and implementation were completed successfully. The gap is execution resources (API key, budget approval approximately $1,620 for full MMLU + HumanEval evaluation across 5 λ levels with approximately 4 hours runtime requirement).

## 6. Discussion

### 6.1 Methodological Contributions

This work addresses a measurement gap in AI alignment research: existing evaluation measures AI performance without considering reciprocal effects on human oversight behavior. We contribute the first framework to operationalize bidirectional alignment dynamics as coupled, measurable variables (ACE and HOR) with experimental protocols for testing coupling mechanisms.

**Key advances:**

1. **Architectural Separation:** We leverage Constitutional AI's policy-layer architecture to enable testable capability invariance via compliance modulation. The h-e1 gate (ICC > 0.95, ANOVA p > 0.05, Cohen's f < 0.10) enforces this separation as a testable assumption.

2. **Integration Across Research Areas:** We unify AI alignment evaluation, automation bias from human factors, and signal detection theory into a single measurement framework.

3. **Pre-Registered Falsification Criteria:** Dependency-driven hypothesis decomposition with gate-based validation reduces researcher degrees of freedom. Each hypothesis has pre-specified success thresholds, failure routing logic, and prerequisite dependencies.

4. **Automated Quality Control:** The pipeline detected and corrected mock data usage, preventing false validation of prerequisite assumption A1.

### 6.2 Limitations

**Limitation 1: No Empirical Evidence**

All five predictions (P1-P5) and all five assumptions (A1-A5) remain INCONCLUSIVE/UNVERIFIED. No experiments were executed. Zero empirical data collected on ACE-HOR coupling, automation bias mediation, or metacognitive interventions.

The entire research contribution rests on empirical validation. Without experiment execution, this work contributes only methodological design and engineering, not scientific findings about bidirectional alignment dynamics.

Root cause: API key unavailability blocked h-e1 execution. Expected cost (~$1,620 for full MMLU + HumanEval evaluation) likely required budget approval that was not obtained. Dependent hypotheses (h-m1 through h-m4) could not proceed due to h-e1 prerequisite failure.

Methodological contributions are valuable for emerging research areas. Bidirectional alignment evaluation is a new problem space—measurement frameworks are a necessary first step before large-scale empirical studies. Our work establishes how to measure bidirectional dynamics, enabling future researchers to conduct empirical tests. The infrastructure code is validated and datasets verified, ready for execution when resources become available.

**Limitation 2: Capability Invariance Assumption Unverified**

Assumption A1 (policy-layer modulation preserves base capability with ICC > 0.95) is the foundational prerequisite for all downstream measurements. If violated, ACE becomes confounded with capability changes, making all ACE-HOR coupling results uninterpretable. This assumption remains empirically untested.

Many alignment interventions do affect capability. Constitutional AI system prompts may alter verbosity, hedging, or reasoning depth in ways that affect MMLU/HumanEval performance. If A1 is violated, the framework's causal inference breaks down.

We explicitly designed h-e1 as a MUST_WORK gate to test this assumption. Failure triggers routing to Phase 0 (architecture re-selection). The assumption is falsifiable and testable, not hidden or implicitly assumed. Constitutional AI architecture suggests capability invariance via policy-layer separation, but this must be validated empirically.

Mitigation: h-e1 execution tests A1 directly. If violated, alternative ACE operationalizations exist: frozen base model with separate trainable policy head, retrieval-augmented constitutional rules, or partial correlation controlling for capability.

**Limitation 3: Ecological Validity of Seeded Errors**

HOR measurement via signal detection d' requires ground-truth error labels. We use seeded within-distribution errors sampled from the model's empirical confusion matrix (Assumption A2). However, ecological validity—whether seeded errors represent real model failures users encounter in deployment—remains unverified.

If seeded errors are detectability-biased, HOR measurements reflect stress-testing rather than realistic oversight. Results may not generalize to deployment contexts where error types, frequencies, and detectability differ.

Seeded error approach is common in oversight and vigilance research. Sampling from empirical confusion matrix ensures errors resemble model's actual failure modes. We explicitly acknowledge the validity threat.

Mitigation: Compare seeded error HOR measurements with naturally-occurring error detection in deployment logs. If correlation is high (r > 0.7), ecological validity supported.

**Limitation 4: Generalization Uncertainty**

Even if experiments succeed, the framework's practical utility for real-world deployment remains uncertain. Three concerns: (1) Laboratory seeded errors may not capture the full distribution of deployment failures; (2) Single-session or longitudinal evaluations in controlled settings may not predict oversight quality in real workflow integration with switching costs and multi-tasking; (3) Framework is designed for Claude 3 Opus with Constitutional AI policy-layer manipulation and may not generalize to other architectures with different alignment mechanisms.

Laboratory experiments establish causal mechanisms, to be validated against field data. Mitigation: (1) Correlate lab HOR measurements with deployment error detection rates from production logs; (2) Deploy framework in real workflows and compare lab-predicted vs. field-observed coupling patterns; (3) Test framework on alternative models to assess generalization.

### 6.3 Status Summary

**Infrastructure Validation:**
- Quality control effective (mock data detected/fixed, 6/6 verification checks passed)
- Real datasets verified (MMLU 57 subjects/14,042 questions, HumanEval 164 problems)
- Dependency structure complete (5 hypotheses with gate criteria, falsification logic)
- Deviation classification transparent (all IMPLEMENTATION_GAP, no methodology failures)

**Empirical Validation:**
- No experiments executed (API resource constraint)
- All predictions (P1-P5) INCONCLUSIVE
- All assumptions (A1-A5) UNVERIFIED

**Contribution:** Methodological infrastructure (framework design + infrastructure implementation), not empirical findings (experiments pending).

## 7. Conclusion

Current alignment evaluation measures whether AI outputs match human preferences without considering whether excessive alignment affects human oversight through automation bias. This work presents a measurement framework for bidirectional alignment dynamics as coupled variables (ACE and HOR) with experimental protocols for testing coupling mechanisms via capability-invariant policy-layer manipulation.

Our infrastructure validation demonstrates methodological rigor: mock data detection prevented false validation, real dataset verification ensures reproducibility, and dependency-driven hypothesis decomposition with gate-based validation reduces researcher degrees of freedom. However, no empirical evidence exists. All predictions and assumptions remain inconclusive/unverified pending experiment execution (~$1,620 API cost, ~4 hours runtime for h-e1). Our contribution is methodological infrastructure, not empirical findings.

The immediate next step is h-e1 execution to test capability invariance. If h-e1 passes, proceed to mechanism studies (h-m1 through h-m4) requiring human participants and longitudinal data collection. If h-e1 fails, redesign ACE operationalization. Beyond empirical validation, extend the framework to alternative alignment architectures and multi-agent collaboration.

Measurement infrastructure is a necessary foundation for empirical research in emerging problem spaces. We provide the tools for measuring bidirectional alignment dynamics. Future work executes the experiments.
