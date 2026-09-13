# Experimental Design

Our experimental framework tests bidirectional alignment dynamics through a dependency-driven hypothesis chain. We describe the planned experimental protocols (infrastructure validated but not executed due to API resource constraints). Each experiment addresses a specific research question with pre-specified success criteria and falsification logic.

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
1. **Model:** Claude 3 Opus with frozen pretrained weights, temperature 0.0 (deterministic)
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

**Current Status:** Infrastructure validated (real datasets loaded, statistical pipeline functional, mock data fix completed), experiments NOT executed.

**Blocking Factor:** API resource constraint (ANTHROPIC_API_KEY unavailable, ~$1,620 budget for h-e1 execution).

**Next Step:** Execute h-e1 with API access. If h-e1 passes, proceed to h-m1 through h-m4. If h-e1 fails, route to Phase 0 for ACE operationalization redesign (e.g., frozen base + trainable policy head, retrieval-augmented rules).
