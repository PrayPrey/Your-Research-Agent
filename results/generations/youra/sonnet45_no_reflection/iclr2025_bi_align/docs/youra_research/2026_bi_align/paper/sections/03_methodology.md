# Methodology

Building on our architectural insight—that Constitutional AI's policy-layer separation enables capability-invariant compliance modulation—we design a measurement framework for bidirectional alignment dynamics. Our approach has three components: (1) operationalizing ACE and HOR as measurable variables, (2) statistical validation of capability invariance, and (3) dependency-driven hypothesis decomposition with falsification criteria.

## 3.1 Variable Operationalization

### AI Compliance Elasticity (ACE)

**Definition:** ACE quantifies alignment strength via Constitutional AI policy-layer parameter λ, ranging from minimal compliance (λ = 0.2) to maximal compliance (λ = 1.0).

**Implementation:** We use Claude 3 Opus [@Anthropic2024Claude3] as the base model with frozen pretrained weights. Compliance is modulated via system prompts that encode constitutional principles with varying intensity:

- **λ = 0.2:** "Answer directly and concisely." (minimal constitutional guidance)
- **λ = 0.4:** "Be helpful and accurate in your responses." (moderate helpfulness emphasis)
- **λ = 0.6:** "Provide helpful, accurate, and well-reasoned responses." (default constitutional AI)
- **λ = 0.8:** "Be extremely careful, ethical, and thorough in your responses." (heightened constitutional emphasis)
- **λ = 1.0:** "Follow all constitutional principles: be helpful, harmless, honest, and carefully consider ethical implications." (maximal compliance)

**Rationale:** Policy-layer modulation via system prompts allows compliance manipulation without retraining base model weights, the critical architectural separation needed for our causal inference [@Bai2022ConstitutionalAI]. Alternative approaches (RLHF fine-tuning, prompt engineering without frozen base) confound alignment with capability changes, making it impossible to isolate ACE's effect on HOR. The five λ levels provide sufficient statistical power for model comparison (M1 linear vs. M2 quadratic vs. M3 bifurcation) while remaining computationally tractable.

### Human Oversight Retention (HOR)

**Definition:** HOR measures human error detection sensitivity using signal detection d', where higher d' indicates better oversight quality (distinguishing correct from incorrect AI outputs).

**Measurement Protocol:**
1. **Seeded Errors:** Embed 20% within-distribution errors sampled from the model's empirical confusion matrix on validation data. Error types: 50% high-confidence incorrect, 30% low-confidence incorrect, 20% correct but misleading reasoning [@Parasuraman1997AutomationBias].
2. **Ground Truth:** All errors have known ground-truth labels (correct/incorrect), enabling d' computation.
3. **Signal Detection d':** Computed as `d' = Z(hit_rate) - Z(false_alarm_rate)`, where hit rate is correct error detections and false alarm rate is incorrect flagging of correct outputs [@Swets1964SignalDetection].
4. **Temporal Tracking:** Measure HOR at t ∈ {1 hour, 1 day, 1 week, 1 month} to capture erosion dynamics vs. learning effects.

**Rationale:** Signal detection d' isolates error detection sensitivity from response criterion (tendency to flag outputs) and task accuracy (AI capability). This separation is critical: if we measured oversight via task accuracy, improvements could reflect better AI capability rather than better human oversight. Seeded within-distribution errors (not adversarial) ensure ecological validity—errors resemble real model failures, not artificially difficult edge cases [@Goddard2012AutomationMedical]. Temporal measurement enables testing competing-process models (k₁ erosion rate vs. k₂ learning rate).

## 3.2 Capability Invariance Validation (Gate h-e1)

**The Critical Prerequisite:** If policy-layer modulation alters base model capability, all ACE-HOR coupling measurements are confounded and uninterpretable. We therefore design hypothesis h-e1 as a MUST_WORK gate: if capability invariance is not achieved (ICC < 0.95 or ANOVA p < 0.05), the entire experimental approach is invalidated and must be redesigned.

**Statistical Tests:**

1. **Intraclass Correlation Coefficient (ICC):** Measures consistency of capability metrics (MMLU accuracy, HumanEval pass@1) across λ conditions using two-way mixed effects model for absolute agreement [@Shrout1979ICC]. **Threshold:** ICC₂ > 0.95 (capability remains statistically equivalent across compliance levels).

2. **One-Way ANOVA:** Tests whether capability varies significantly across λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0} with Bonferroni correction for multiple comparisons. **Threshold:** p > 0.05 (no significant variation).

3. **Cohen's f (Effect Size):** Quantifies magnitude of capability variation. **Threshold:** f < 0.10 (negligible effect).

**Datasets:** MMLU (57 subjects spanning abstract algebra through virology, 14,042 test questions) [@Hendrycks2021MMLU] and HumanEval (164 hand-written programming problems) [@Chen2021HumanEval]. These provide broad capability coverage (knowledge + reasoning) and statistical power for invariance testing.

**Gate Logic:** ALL three criteria must pass (ICC > 0.95 AND p > 0.05 AND f < 0.10). If any criterion fails → ABORT hypothesis chain, route to Phase 0 for alternative ACE operationalization (e.g., frozen base model with trainable policy head, retrieval-augmented constitutional rules).

**Rationale:** Capability invariance is an *assumption* (A1 in our framework) that must be empirically validated, not taken on faith. Many alignment interventions inadvertently affect capability [@Ouyang2022InstructGPT reports capability improvements from RLHF]. By enforcing statistical validation, we prevent confounded measurements and ensure ACE isolates compliance strength.

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

**Rationale:** Infrastructure validation demonstrates the framework is not just a conceptual proposal but an executable system ready for empirical testing. Mock data detection prevents false validation (Attempt 1/5 successfully identified and corrected synthetic ICC > 0.95 by design). Real dataset verification ensures reproducibility and comparability with prior work.

## 3.5 Limitations and Assumptions

**Key Assumptions (All Unverified Pending Empirical Testing):**

1. **A1: Capability Invariance** — Policy-layer modulation preserves base capability (ICC > 0.95). If violated → ACE confounded with capability changes, all coupling measurements uninterpretable. *Mitigation:* h-e1 gate tests this explicitly; failure triggers architecture redesign.

2. **A2: Error Validity** — Within-distribution seeded errors are ecologically valid (representative of real failures). If violated → HOR measures stress-testing, not realistic oversight. *Mitigation:* Sample errors from empirical confusion matrix (not adversarial fabrications).

3. **A3: Automation Bias Mechanism** — Automation bias from traditional automation generalizes to AI collaboration. If violated → HOR degradation arises from alternative mechanisms (cognitive load, task engagement). *Mitigation:* h-m3 mediation test distinguishes automation bias from alternatives.

**Scope:** Framework applies to human-AI collaboration where: (1) AI can be policy-layer modulated with frozen base capability, (2) human oversight is critical and measurable via error detection, (3) repeated interactions occur over hours to months. Primary domains: medical diagnosis, code review, content moderation.
