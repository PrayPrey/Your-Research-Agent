# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-05-11 01:23:55
- **Workflow**: phase2a-dialogue v10.0.0
- **Architecture**: Self-Contained Tikitaka Loop v10.0.0
- **Gap ID**: gap-1
- **Gap Title**: Integrated Evaluation Metrics for Bidirectional Alignment
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 16

---

## Research Dialogue Context

**Participants**: Dr. Nova (Novelty Assessor), Prof. Vera (Falsifiability Judge), Dr. Sage (Significance Evaluator), Prof. Pax (Plausibility Validator), Dr. Ally (Advocate), Prof. Rex (Devil's Advocate)

**Total Exchanges**: 16

**Convergence Reason**: Consensus on three-level hypothesis framework with mechanistic grounding

### Key Insights

1. **Policy-layer decoupling** (frozen base + variable compliance) resolves the capability-compliance confound that would otherwise make experimental results uninterpretable.

2. **Automation bias** from human factors research provides mechanistic grounding for the ACE-HOR coupling, transforming this from a speculative hypothesis to one grounded in established cognitive theory.

3. **Three competing models** (M1 linear degradation, M2 quadratic equilibrium, M3 bifurcation) allow for discovery vs confirmation testing—the framework values negative results (Pareto tradeoff) as much as positive ones (equilibrium existence).

4. **Metacognitive interventions** (designed disagreement 15-25%) target k₂ increase via comparative evaluation, shifting from passive alignment to active cognitive partnership.

5. **Success matrix** includes valuable negative results: if M1 or M3 wins, we discover a fundamental Pareto tradeoff between compliance and oversight, which is scientifically significant even though it rules out equilibrium.

### Breakthrough Moments

- **Exchange 4-5**: Prof. Pax + Dr. Ally synthesis on policy-layer decoupling architecture—the realization that Constitutional AI's frozen-base + variable rules architecture could cleanly isolate compliance from capability.

- **Exchange 7**: Prof. Vera's mathematical formalization with three competing models (M1/M2/M3), transforming vague "equilibrium" claims into falsifiable predictions with distinct functional forms.

- **Exchange 11**: Dr. Ally's comprehensive response addressing all Prof. Rex critiques, including the capability-compliance decoupling protocol (ICC > 0.95 validation) and mechanistic grounding via automation bias literature.

- **Exchange 12**: Prof. Vera's pre-registered prediction framework with success criteria matrix, establishing that both positive and negative results (equilibrium vs Pareto tradeoff) are scientifically valuable.

- **Exchange 14**: Dr. Ally's metacognitive mechanism specification (k₂ = α·0.2 + β), providing quantitative predictions for intervention effects rather than qualitative hand-waving.

### Resolved Tensions

- **Compliance-capability confound** → Resolved via policy-layer manipulation (frozen base model + variable Constitutional AI rules). Validated through ICC > 0.95 on MMLU/HumanEval across all λ conditions.

- **Equilibrium assumption** → Resolved via pre-registered model comparison. Testing M1 (linear), M2 (quadratic), and M3 (bifurcation) allows null discovery—if no equilibrium exists, that's a valuable result.

- **Timescale vagueness** → Resolved via competing-process model with specific k₁ (erosion) and k₂ (learning) parameters. Temporal dynamics measured at t ∈ {1hr, 1day, 1week, 1month}.

- **Metacognitive mechanism** → Resolved via levels-of-processing theory + quantitative k₂ prediction. 15-25% disagreement frequency calibrated from desirable difficulties literature.

- **Threshold justification** → Resolved via domain literature grounding. 0.6 AIC weight threshold from model selection standards, 0.7 HOR baseline from human performance + safety standards.

---

## Final Hypothesis

### Title
**Bidirectional Alignment Stability via Policy-Layer Compliance Modulation and Metacognitive Intervention**

### Core Claim
Under human-AI collaborative tasks with policy-layer compliance manipulation, **if AI Compliance Elasticity (ACE) is increased while holding base capability constant**, **then Human Oversight Retention (HOR) will exhibit coupling governed by Bayesian trust calibration** (ACE → perceived reliability → HOR degradation), with functional form distinguishable as linear (M1), quadratic/inverted-U (M2), or bifurcation (M3), **because increased compliance reduces observable AI-human disagreement signals, leading to automation bias through reduced verification effort**.

### Mechanism
**Four-step causal chain:**

1. **Policy-layer compliance manipulation** (λ increase) reduces AI-human observable disagreement frequency without changing base capability
   - **Evidence**: Constitutional AI architectural separation (frozen base + variable policy layer)
   - **Falsifier**: If base capability varies significantly across λ → mechanism fails (P1 falsification)

2. **Reduced disagreement signals** increase perceived AI reliability beyond objective accuracy (trust miscalibration)
   - **Evidence**: Automation bias via consistency signals (Prof. Vera & Prof. Pax, Exchanges 2, 7, 11)
   - **Falsifier**: If perceived reliability tracks objective accuracy → mediation pathway fails (P3 test)

3. **Increased perceived reliability** reduces human verification effort via Bayesian updating (automation bias)
   - **Evidence**: Human factors literature on automation bias, cognitive mediation hypothesis
   - **Falsifier**: If HOR remains constant despite increased perceived reliability → automation bias mechanism does not apply

4. **Reduced verification effort** degrades error detection sensitivity (HOR decline) over repeated exposure
   - **Evidence**: Signal detection theory + skill degradation from reduced reinforcement frequency
   - **Falsifier**: If HOR improves or remains stable over time under high λ → temporal degradation hypothesis false

**Key Tension**: Whether equilibrium region exists (quadratic M2) vs fundamental Pareto tradeoff (linear M1 or bifurcation M3). All three outcomes scientifically valuable.

---

## Predictions

### P1: Base Model Capability Invariance (Primary Validity Check)
**Statement**: Base model capability remains invariant across λ conditions (decoupling validity)

**Test Method**: Measure MMLU and HumanEval scores across 5 λ levels (0.2-1.0). Compute intraclass correlation coefficient (ICC).

**Success Criterion**: ICC > 0.95 AND one-way ANOVA p > 0.05 (no significant capability variation)

**Falsification**: If ICC < 0.95 OR ANOVA p < 0.05 → compliance-capability confound NOT resolved. Experiment invalid.

---

### P2: ACE-HOR Functional Form (Primary Research Question)
**Statement**: ACE-HOR coupling follows one of three distinguishable functional forms (linear M1, quadratic M2, bifurcation M3)

**Test Method**: Fit three pre-registered models to Dataset A (N=50). Select best model via minimum AIC. Validate on Dataset B (N=100).

**Success Criterion**: Selected model achieves R² ≥ 0.6 on Dataset B validation. AIC weight > 0.7 for winning model.

**Falsification**: If R² < 0.6 on Dataset B → functional form does not generalize. If AIC weights distributed ~equal → models indistinguishable.

---

### P3: Mediation by Perceived Reliability (Mechanism Test)
**Statement**: HOR degradation is mediated by perceived reliability (trust calibration pathway)

**Test Method**: Compare HOR in Condition B (high λ, standard confidence) vs Condition C (high λ, randomized confidence displays). If mediation exists, Condition C should show higher HOR than B.

**Success Criterion**: HOR_C - HOR_B ≥ 10% with p < 0.05 (paired t-test or mixed-effects model)

**Falsification**: If HOR_C ≈ HOR_B (difference < 5% or p > 0.05) → degradation NOT mediated by perceived reliability

---

### P4: Metacognitive Intervention Effect (Learning Rate Increase)
**Statement**: Metacognitive intervention (designed disagreement 15-25%) increases learning rate k₂ by ≥30%

**Test Method**: Fit competing-process model HOR(t) = erosion + learning to intervention vs control groups. Compare k₂_intervention vs k₂_control.

**Success Criterion**: k₂_intervention / k₂_control ≥ 1.30 with 95% Bayesian credible interval excluding 1.0

**Falsification**: If 95% CI includes 1.0 at t=1week AND t=1month → metacognitive hypothesis rejected

---

### P5: Equilibrium Region Existence (Conditional on M2)
**Statement**: Equilibrium region exists where ACE ≥ 0.6 AND HOR ≥ 0.7*HOR_baseline

**Test Method**: Conditional on P2 model selection: IF M2 (quadratic) wins, compute optimal λ* = -b₁/(2b₂). Test whether λ* ∈ [0.4, 0.8] AND HOR(λ*, t_∞) ≥ 0.7*HOR_0.

**Success Criterion**: M2 wins AIC comparison AND λ* within practical range AND HOR threshold met

**Falsification**: If M1 (linear) or M3 (bifurcation) wins → no interior equilibrium, fundamental Pareto tradeoff confirmed

---

## Novelty

### Preserved Novelty
First framework treating bidirectional alignment as measurable temporal dynamics problem rather than static performance evaluation

### Key Innovation
Three-level framework combining **measurement** (ACE+HOR via policy-layer + d'), **mechanism** (Bayesian trust calibration), and **intervention** (metacognitive designed disagreement). Shift from 'alignment quality' to 'alignment stability' with actionable design constraints.

### Differentiation from Prior Work

**vs. RLHF evaluation via unidirectional benchmarks (HHH, TruthfulQA)**
- **Difference**: We measure bidirectional coupling with temporal dynamics (k₁/k₂ competing processes) rather than static AI-only scores

**vs. Automation bias research in traditional human-automation interaction**
- **Difference**: We operationalize automation bias in AI collaboration with policy-layer decoupling and metacognitive interventions specific to LLM systems

**vs. Human-AI teaming research treating agency preservation as side constraint**
- **Difference**: We treat ACE and HOR as co-dependent optimization targets with measurable equilibrium regions and temporal stability analysis

---

## Experimental Design

### Dataset
**Name**: Medical Diagnosis Cases (Dataset A,B) + Code Review Tasks (Dataset C)

**Type**: Standard

**Source**: Medical: MIMIC-III clinical notes with diagnostic tasks. Coding: CodeReview benchmark with bug detection tasks.

**Hypothesis Fit**: Both domains require critical human oversight where AI suggestions must be verified. Medical provides high-stakes context; coding provides cross-domain validation.

### Model
**Name**: Constitutional AI (Anthropic) OR GPT-4 with system prompts

**Type**: Large Language Model with policy-layer separation

**Source**: Anthropic Claude (Constitutional AI architecture) or OpenAI GPT-4

**Hypothesis Fit**: Constitutional AI explicitly separates base capability (frozen model) from alignment rules (policy layer), enabling clean ACE manipulation without capability change.

### Baselines
1. **Static Baseline (λ=0.5)**: Standard AI assistance without compliance modulation. Serves as reference for ACE=neutral condition.

2. **Human-Only Control**: Task performance without AI assistance. Establishes HOR_baseline measurement.

### Measurement Plan

**Data Collection**:
- Phase 1 (Dataset A, N=50): Medical diagnosis tasks, 5 λ levels, 4 time points
- Phase 2 (Dataset B, N=100): Medical diagnosis validation
- Phase 3 (Dataset C, N=75): Code review cross-domain transfer

**Procedure**:
1. Baseline HOR measurement (human-only, no AI)
2. Expose participants to AI with assigned λ condition
3. Measure HOR at t ∈ {1hr, 1day, 1week, 1month} via seeded error detection
4. Validate base capability invariance (MMLU/HumanEval every timepoint)
5. Fit competing-process models, select via AIC, validate cross-domain

**Success Criteria**:
- P1: ICC > 0.95 for capability invariance
- P2: R² ≥ 0.6 on validation set for selected model
- P3: HOR_C - HOR_B ≥ 10% with p < 0.05
- P4: k₂_intervention / k₂_control ≥ 1.30 with 95% CI excluding 1.0
- P5: λ* ∈ [0.4, 0.8] AND HOR(λ*, t_∞) ≥ 0.7*HOR_0 (conditional on M2 winning)

---

## Variables

### Independent Variable
**AI Compliance Elasticity (ACE) - λ parameter**
- **Type**: Categorical
- **Operationalization**: Policy-layer compliance strength via Constitutional AI rule weight or system prompt intensity. Frozen base model, variable policy head.
- **Levels**: 0.2, 0.4, 0.6, 0.8, 1.0

### Dependent Variable (Primary)
**Human Oversight Retention (HOR)**
- **Type**: Continuous
- **Operationalization**: Signal detection sensitivity d' on seeded within-distribution errors. Range: -∞ to +∞, typical 0-4. Measured at t ∈ {1hr, 1day, 1week, 1month}

### Dependent Variable (Secondary)
**Task Accuracy**
- **Type**: Continuous
- **Operationalization**: Human-AI collaborative task success rate (0-100%)

### Controlled Variables
1. **Base Model Capability**: Frozen pretrained weights. Validated via ICC > 0.95 on MMLU and HumanEval across all λ conditions.
2. **Task Difficulty**: Stratified sampling across difficulty levels (easy/medium/hard) in each experimental condition
3. **Seeded Error Distribution**: 20% errors sampled from model's empirical confusion matrix (within-distribution). 50% high-conf incorrect, 30% low-conf incorrect, 20% correct with misleading reasoning

---

## Key Assumptions

**A1**: Policy-layer compliance manipulation can be implemented without materially altering base model capability
- **Supporting Evidence**: Constitutional AI architecture separates base model from constitutional rules. System prompts modulate behavior without retraining. Testable via ICC > 0.95 validation.
- **Consequence if Violated**: ACE becomes confounded with capability. All coupling results uninterpretable. Experiment fails P1 validity check.

**A2**: Within-distribution seeded errors are ecologically valid (representative of real model failures)
- **Supporting Evidence**: Sampled from empirical confusion matrix on validation set. Avoids adversarial fabrications.
- **Consequence if Violated**: HOR measurement reflects stress-testing, not realistic oversight. Results don't generalize to deployment.

**A3**: Automation bias mechanism applies to AI collaboration contexts (not just traditional automation)
- **Supporting Evidence**: Human factors literature precedent. Prof. Pax validation across Exchanges 7-12.
- **Consequence if Violated**: HOR degradation could arise from other mechanisms (cognitive load, task engagement). Mediation test (P3) would distinguish.

**A4**: Temporal dynamics follow competing-process model (k₁ erosion vs k₂ learning)
- **Supporting Evidence**: Cognitive psychology precedent (skill acquisition + decay models). Testable via functional form fitting.
- **Consequence if Violated**: Alternative temporal patterns (oscillatory, chaotic) could emerge. Model comparison (M1/M2/M3) would detect.

**A5**: Metacognitive interventions increase k₂ via comparative evaluation without excessive user frustration
- **Supporting Evidence**: Desirable difficulties literature (Bjork), levels-of-processing theory (Craik & Lockhart). 15-25% disagreement frequency calibrated from education research.
- **Consequence if Violated**: Users report frustration ≥7/10. Task abandonment increases. Intervention fails P4 test.

---

## Scope & Boundaries

### Applies To
Human-AI collaborative tasks in domains where:
1. AI systems can be policy-layer modulated while keeping base capability fixed (e.g., Constitutional AI, system-prompted LLMs)
2. Human oversight is critical and measurable via error detection
3. Repeated human-AI interactions occur over timescales of hours to months

**Primary domains**: medical diagnosis, code review, content moderation

### Does Not Apply To
Tasks where:
1. AI capability cannot be decoupled from compliance (deeply entangled architectures)
2. Human oversight is not required or measurable
3. Single-shot interactions (no temporal dynamics)
4. High-frequency real-time domains where 1-second decisions dominate (may require different timescale analysis)

### Known Limitations
1. Cross-domain generalization tested only on medical→coding transfer (Phase 1). Broader validation needed for creative writing, scientific research.
2. Optimal disagreement frequency (15-25%) estimated from educational literature, not empirically validated in AI collaboration.
3. Constitutional AI implementation details may constrain achievable λ range.

---

## Limitations

1. **Constitutional AI implementation details** need pilot validation (Prof. Rex Exchange 13) to confirm that rule strength variation truly maps to compliance without capability shift.

2. **Disagreement frequency optimization** (15-25%) is estimated from educational literature, not empirically validated in AI collaboration context. May need adaptive tuning during Phase 2B.

3. **Cross-domain generalization** (medical→coding) tests only two domains. Broader validation (creative writing, scientific research) needed for universal claims.

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | Consensus on three-level hypothesis framework with mechanistic grounding |
| **Clarity Verified** | Yes |
| **Remaining Objections** | See mitigation strategy below |

### Remaining Concerns & Mitigation Strategy

**Concern 1**: Constitutional AI implementation details - need to verify that rule strength variation truly maps to compliance without capability shift. Requires pilot study confirming ICC > 0.95 before main experiment.

**Concern 2**: Designed disagreement frequency optimization (15-25%) is estimated from educational literature, not empirically validated in AI collaboration context. May need adaptive tuning during Phase 2B.

**Concern 3**: Cross-domain generalization (medical→coding) tests only two domains. Broader validation (creative writing, scientific research) needed for universal claims.

**Mitigation Strategy**: Phase 2B should include pilot validation of Constitutional AI manipulation, adaptive disagreement frequency tuning based on user feedback, and plan for Phase 3 extension to additional domains if P3 passes in Phase 2.

---

## Persona Verdicts Summary

**🔭 Dr. Nova (Novelty)**: STRONG
- The metacognitive alignment paradigm—treating AI as a partner that actively maintains human critical thinking rather than just following instructions—is genuinely novel. The designed disagreement mechanism shifts the field from passive alignment to active cognitive partnership.

**🔬 Prof. Vera (Falsifiability)**: STRONG
- Five pre-registered predictions (P1-P5) with explicit statistical thresholds, three competing mathematical models distinguished via AIC, and multiple falsification paths including valuable negative results. The decoupling validity check (P1) makes confounds a blocker, not a caveat.

**🎯 Dr. Sage (Significance)**: STRONG
- Transforms alignment evaluation from static quality scores to temporal stability analysis. Opens four major research directions (domain-specific equilibria, expertise dependencies, architectural differences, metacognitive design). Provides actionable design constraints for real deployment.

**⚙️ Prof. Pax (Feasibility)**: MODERATE-STRONG
- Policy-layer decoupling is technically achievable via Constitutional AI or system prompts, with explicit validation (ICC > 0.95). The metacognitive intervention mechanism is grounded in established cognitive science. Risk: Constitutional AI implementation details may constrain λ range. Overall feasible with named architectures.

**🛡️ Dr. Ally (Synthesis)**: CONVERGED
- Bidirectional alignment can be measured and optimized through a three-level framework combining measurement, mechanism, and intervention. The hypothesis predicts distinguishable functional forms, is implementable in Constitutional AI architectures, and is falsifiable through five predictions.

**🔍 Prof. Rex (Critique)**: ADDRESSED
- All major concerns addressed through: (1) ICC > 0.95 capability invariance validation, (2) Pre-registered model comparison allowing null discovery, (3) Mechanistic grounding via automation bias literature, (4) Quantitative temporal dynamics model, (5) Domain literature threshold justification.

---

*Generated by Phase 2A-Dialogue Workflow v10.0.0 (Self-Contained Tikitaka Loop, Free-Parse)*
