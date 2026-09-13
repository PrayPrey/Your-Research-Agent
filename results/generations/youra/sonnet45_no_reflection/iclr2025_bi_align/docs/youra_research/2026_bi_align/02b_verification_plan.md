# Verification Plan: Bidirectional Alignment Stability via Policy-Layer Compliance Modulation

**Date:** 2026-05-11
**Hypothesis ID:** H-BiAlign-v1
**Confidence:** 0.8
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under human-AI collaborative tasks with policy-layer compliance manipulation, if AI Compliance Elasticity (ACE) is increased while holding base capability constant, then Human Oversight Retention (HOR) will exhibit coupling governed by Bayesian trust calibration (ACE → perceived reliability → HOR degradation), with functional form distinguishable as linear (M1), quadratic/inverted-U (M2), or bifurcation (M3), because increased compliance reduces observable AI-human disagreement signals, leading to automation bias through reduced verification effort.

### 1.2 Alternative Hypothesis (H0)
There is no significant relationship between AI Compliance Elasticity (ACE) and Human Oversight Retention (HOR) when base model capability is held constant (ICC > 0.95 on objective benchmarks).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Medical Diagnosis Cases (Dataset A,B) + Code Review Tasks (Dataset C) (standard) | Both domains require critical human oversight where AI suggestions must be verified. Medical provides high-stakes context; coding provides cross-domain validation. |
| **Model** | Constitutional AI (Anthropic) OR GPT-4 with system prompts | Constitutional AI explicitly separates base capability (frozen model) from alignment rules (policy layer), enabling clean ACE manipulation without capability change. |

**Dataset Details:**
- Source: Medical: MIMIC-III clinical notes with diagnostic tasks. Coding: CodeReview benchmark with bug detection tasks.
- Path: To be specified in Phase 2C

**Model Details:**
- Type: Large Language Model with policy-layer separation
- Source: Anthropic Claude (Constitutional AI architecture) or OpenAI GPT-4

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|-----------------|
| Standard RLHF alignment | Improves AI task accuracy but HOR effects unmeasured | Various (HHH, TruthfulQA, etc.) | Unidirectional evaluation. Doesn't measure human oversight retention or temporal dynamics. |
| Constitutional AI | Provides value alignment through constitutional rules | Anthropic internal benchmarks | Evaluates AI alignment quality, not bidirectional stability. No HOR measurement or temporal dynamics model. |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Policy-layer compliance manipulation can be implemented without materially altering base model capability | Constitutional AI architecture separates base model from constitutional rules. System prompts modulate behavior without retraining. Testable via ICC > 0.95 validation. | ACE becomes confounded with capability. All coupling results uninterpretable. Experiment fails P1 validity check. |
| A2 | Within-distribution seeded errors are ecologically valid (representative of real model failures) | Sampled from empirical confusion matrix on validation set. Avoids adversarial fabrications. | HOR measurement reflects stress-testing, not realistic oversight. Results don't generalize to deployment. |
| A3 | Automation bias mechanism applies to AI collaboration contexts (not just traditional automation) | Human factors literature precedent. Prof. Pax validation across Exchanges 7-12. | HOR degradation could arise from other mechanisms (cognitive load, task engagement). Mediation test (P3) would distinguish. |
| A4 | Temporal dynamics follow competing-process model (k₁ erosion vs k₂ learning) | Cognitive psychology precedent (skill acquisition + decay models). Testable via functional form fitting. | Alternative temporal patterns (oscillatory, chaotic) could emerge. Model comparison (M1/M2/M3) would detect. |
| A5 | Metacognitive interventions increase k₂ via comparative evaluation without excessive user frustration | Desirable difficulties literature (Bjork), levels-of-processing theory (Craik & Lockhart). 15-25% disagreement frequency calibrated from education research. | Users report frustration ≥7/10. Task abandonment increases. Intervention fails P4 test. |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First framework treating bidirectional alignment as measurable temporal dynamics problem rather than static performance evaluation.

**Key Innovation:** Three-level framework combining measurement (ACE+HOR via policy-layer + d'), mechanism (Bayesian trust calibration), and intervention (metacognitive designed disagreement). Shift from 'alignment quality' to 'alignment stability' with actionable design constraints.

**Differentiation:**
- **vs. RLHF unidirectional evaluation**: We measure bidirectional coupling with temporal dynamics (k₁/k₂ competing processes) rather than static AI-only scores
- **vs. Automation bias in traditional systems**: We operationalize automation bias in AI collaboration with policy-layer decoupling and metacognitive interventions specific to LLM systems
- **vs. Human-AI teaming treating agency preservation as side constraint**: We treat ACE and HOR as co-dependent optimization targets with measurable equilibrium regions and temporal stability analysis

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | BLOCKED |
| H-M2 | MECHANISM | MUST_WORK | H-M1 | BLOCKED |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | BLOCKED |
| H-M4 | MECHANISM | DETERMINES_SUCCESS | H-M3 | BLOCKED |

---

### 2.2 Hypothesis Specifications

#### H-E1: Policy-Layer Capability Decoupling Validation

**Type:** EXISTENCE

**Statement:** Under conditions where Constitutional AI or system-prompted LLMs are evaluated across multiple compliance strength levels (λ ∈ {0.2, 0.4, 0.6, 0.8, 1.0}), if base model capability is held frozen while policy-layer rules are varied, then base capability metrics (MMLU, HumanEval) will remain invariant (ICC > 0.95, ANOVA p > 0.05), because the architectural separation between base weights and policy layer allows compliance modulation without capability degradation.

**Variables:**
- IV: Policy-layer compliance strength (λ parameter: 0.2, 0.4, 0.6, 0.8, 1.0)
- DV: Base capability metrics (MMLU accuracy, HumanEval pass@1)
- CV: Model architecture (frozen base weights), evaluation prompts (identical across conditions), temperature (fixed at 0.0 for deterministic evaluation)

**Success Criteria:**
- Intraclass Correlation Coefficient (ICC) > 0.95 across all λ conditions
- One-way ANOVA p > 0.05 (no significant variation in MMLU/HumanEval)
- Effect size: Cohen's f < 0.10 (negligible effect of λ on capability)

**Gate:**
- Type: MUST_WORK
- If Fail: ABORT entire verification chain. Policy-layer decoupling is foundation for all subsequent hypotheses. Route to Phase 0 for architecture re-selection.

**Prerequisites:** None (foundational validation)

**Verification Protocol:**
1. Select Constitutional AI (Claude) or GPT-4 with system prompts architecture
2. Implement 5 compliance conditions (λ = 0.2, 0.4, 0.6, 0.8, 1.0) via rule strength or prompt intensity modulation
3. Freeze base model weights (no fine-tuning between conditions)
4. Evaluate each condition on MMLU (full 57-subject test, ~14k questions) and HumanEval (164 coding problems)
5. Compute ICC (two-way mixed effects, absolute agreement) across conditions
6. Perform one-way ANOVA with Bonferroni correction (α = 0.05)
7. Calculate Cohen's f effect size to quantify practical significance
8. Pass Gate: (ICC > 0.95) AND (ANOVA p > 0.05) AND (Cohen's f < 0.10)

---

#### H-M1: Disagreement Reduction via Compliance Increase

**Type:** MECHANISM (Causal Step 1)

**Statement:** Under conditions where policy-layer compliance λ is manipulated while base capability is held constant (validated via H-E1), if λ increases from 0.2 to 1.0, then AI-human observable disagreement frequency will decrease monotonically (Spearman ρ < -0.7, p < 0.01), because higher compliance strength causes the model to align more closely with human preferences, reducing instances where AI suggestions contradict human judgment.

**Variables:**
- IV: Policy-layer compliance strength (λ: 0.2 → 1.0)
- DV: AI-human disagreement frequency (measured on N=500 medical diagnosis tasks)
- CV: Base capability (ICC > 0.95 validated via H-E1), task difficulty (stratified sampling across easy/medium/hard), human annotator pool (N=50)

**Success Criteria:**
- Spearman ρ < -0.7 (strong negative monotonic correlation between λ and disagreement)
- p-value < 0.01 (statistical significance)
- Disagreement reduction: λ=0.2 frequency ≥ 1.5× λ=1.0 frequency (practical effect size)

**Gate:**
- Type: MUST_WORK
- If Fail: First causal link broken. Mechanism chain cannot proceed. ABORT H-M2/H-M3/H-M4. Route to Phase 2A for mechanism revision.

**Prerequisites:** H-E1 (capability decoupling validated)

**Verification Protocol:**
1. Deploy Constitutional AI across 5 λ conditions (validated for capability invariance)
2. Collect N=500 medical diagnosis task outputs per condition (Dataset A)
3. Stratify tasks by difficulty (MIMIC-III severity scores: easy=1-2, medium=3-4, hard=5-6)
4. Recruit N=50 human medical professionals to annotate AI suggestions as "agree" or "disagree"
5. Calculate disagreement frequency = (# disagree annotations) / (total annotations) per λ condition
6. Compute Spearman rank correlation coefficient ρ between λ and disagreement frequency
7. Test monotonicity with Jonckheere-Terpstra trend test (additional validation)
8. Pass Gate: (Spearman ρ < -0.7) AND (p < 0.01) AND (disagreement_0.2 / disagreement_1.0 ≥ 1.5)

---

#### H-M2: Trust Miscalibration via Reduced Disagreement

**Type:** MECHANISM (Causal Step 2)

**Statement:** Under conditions where AI-human disagreement frequency is reduced (validated via H-M1), if reduced disagreement signals are presented to human participants over repeated interactions (t = 1hr, 1day, 1week), then perceived AI reliability will increase beyond objective accuracy (calibration error > 0.15), because humans use consistency/agreement as a heuristic for reliability (Bayesian updating via observed agreement), leading to trust that exceeds actual AI performance.

**Variables:**
- IV: Observed AI-human disagreement frequency (manipulated via λ from H-M1)
- DV: Perceived reliability - Objective accuracy (calibration error)
- CV: Objective AI accuracy (held constant ~75-80% via capability decoupling), exposure time (t = 1hr, 1day, 1week), task domain (medical diagnosis Dataset A)

**Success Criteria:**
- Calibration error > 0.15 for high-compliance condition (λ=0.8, 1.0) at t=1week
- Pearson correlation r > 0.6 between reduced disagreement and perceived reliability increase
- p-value < 0.05 (paired t-test: perceived reliability at λ=0.8 vs λ=0.2)

**Gate:**
- Type: MUST_WORK
- If Fail: Second causal link (trust miscalibration) broken. Mediation pathway (P3) prediction fails. ABORT H-M3/H-M4. Consider alternative mechanisms (cognitive load, task familiarity).

**Prerequisites:** H-M1 (disagreement reduction validated)

**Verification Protocol:**
1. Deploy two conditions: High-compliance (λ=0.8) and Low-compliance (λ=0.2)
2. Recruit N=100 participants (medical students, residents) for longitudinal study
3. Expose participants to AI-assisted diagnostic tasks at t=1hr, 1day, 1week intervals
4. Measure **perceived reliability**: "Rate AI reliability 0-100%" after each session
5. Measure **objective accuracy**: Ground truth diagnostic accuracy of AI outputs (~75-80% held constant)
6. Calculate calibration error = (Perceived Reliability / 100) - (Objective Accuracy)
7. Compare calibration error between λ=0.8 and λ=0.2 conditions at t=1week
8. Test correlation between disagreement reduction (from H-M1) and perceived reliability increase
9. Pass Gate: (Calibration error_λ=0.8 > 0.15) AND (r > 0.6) AND (p < 0.05)

---

#### H-M3: Verification Effort Reduction via Automation Bias

**Type:** MECHANISM (Causal Step 3)

**Statement:** Under conditions where perceived AI reliability exceeds objective accuracy (validated via H-M2), if participants are exposed to high-reliability perception over time (t = 1week, 1month), then human verification effort will decrease measurably (verification time reduction > 20%, attention allocation to AI outputs < 60%), because increased perceived reliability triggers automation bias (reliance on automated systems), reducing cognitive resources allocated to error detection and critical evaluation.

**Variables:**
- IV: Perceived reliability - Objective accuracy gap (from H-M2)
- DV: Verification effort (measured via: verification time per task, eye-tracking attention to AI outputs, self-reported effort ratings)
- CV: Task difficulty (stratified), objective AI accuracy (held constant), participant expertise (medical residents)

**Success Criteria:**
- Verification time reduction > 20% (High perceived reliability vs Low perceived reliability conditions)
- Attention allocation to AI outputs < 60% of total task time (eye-tracking metric)
- Self-reported effort ratings decrease by ≥1 point on 7-point Likert scale
- p-value < 0.05 for all metrics (paired comparisons)

**Gate:**
- Type: MUST_WORK
- If Fail: Third causal link (verification reduction) broken. Automation bias mechanism does not apply to AI collaboration context (A3 violated). ABORT H-M4. Consider alternative mechanisms.

**Prerequisites:** H-M2 (trust miscalibration validated)

**Verification Protocol:**
1. Use participants from H-M2 longitudinal study (N=100) at t=1week, 1month timepoints
2. Instrument task interface with:
   - Verification time tracking (time spent reviewing AI suggestions before accepting/rejecting)
   - Eye-tracking (attention allocation: % time looking at AI outputs vs patient data vs other sources)
   - Self-reported effort: "How much effort did you invest in verifying AI suggestions? (1=minimal, 7=maximum)"
3. Compare High perceived reliability (λ=0.8, calibration error > 0.15) vs Low perceived reliability (λ=0.2, calibration error < 0.10)
4. Calculate verification time reduction = (Time_low - Time_high) / Time_low × 100%
5. Measure eye-tracking attention allocation to AI outputs (requires eye-tracker hardware)
6. Collect self-reported effort ratings after each task session
7. Perform paired t-tests comparing High vs Low perceived reliability conditions
8. Pass Gate: (Verification time reduction > 20%) AND (Attention < 60%) AND (Effort decrease ≥ 1 point) AND (all p < 0.05)

---

#### H-M4: Error Detection Sensitivity Degradation via Reduced Verification

**Type:** MECHANISM (Causal Step 4)

**Statement:** Under conditions where verification effort is reduced (validated via H-M3), if reduced verification persists over repeated exposure (t = 1week, 1month), then error detection sensitivity (HOR measured via d' on seeded errors) will degrade over time (d'_t=1month < 0.7 × d'_baseline), because reduced verification frequency decreases error encounter and correction opportunities, leading to skill degradation via reduced reinforcement and practice in error detection tasks.

**Variables:**
- IV: Verification effort reduction (from H-M3)
- DV: Human Oversight Retention (HOR) measured as signal detection sensitivity d' on seeded within-distribution errors
- CV: Seeded error distribution (20% error rate, stratified by: 50% high-confidence incorrect, 30% low-confidence incorrect, 20% correct with misleading reasoning), baseline HOR (d'_baseline measured at t=0 before AI exposure)

**Success Criteria:**
- HOR degradation: d'_t=1month < 0.7 × d'_baseline (≥30% decline)
- Temporal trend: negative slope in d' over time (linear regression β < -0.5 per week)
- Statistical significance: Repeated measures ANOVA p < 0.05 (time effect)
- Condition effect: d'_λ=0.8 < d'_λ=0.2 at t=1month (compliance effect on degradation)

**Gate:**
- Type: DETERMINES_SUCCESS
- If Pass: Full causal chain validated (H-M1→H-M2→H-M3→H-M4). ACE-HOR coupling mechanism confirmed. Proceed to P2 functional form model selection.
- If Fail: Fourth causal link broken. Temporal degradation hypothesis false (A4 violated). Mechanism chain incomplete but partial validation achieved (automation bias applies, but HOR remains stable). Document as limitation and proceed to P2 with revised mechanism.

**Prerequisites:** H-M3 (verification effort reduction validated)

**Verification Protocol:**
1. Continue longitudinal study from H-M2/H-M3 (N=100 participants, t=1week, 1month)
2. Measure baseline HOR (d'_baseline) at t=0 before any AI exposure:
   - Present N=100 diagnostic tasks with 20% seeded errors (no AI assistance)
   - Calculate d' = Z(hit rate) - Z(false alarm rate) for error detection
3. At each timepoint (t=1hr, 1day, 1week, 1month), re-measure HOR with seeded errors:
   - Insert 20% seeded errors in AI suggestions (sampled from model's empirical confusion matrix)
   - Stratify errors: 50% high-conf incorrect, 30% low-conf incorrect, 20% correct with misleading reasoning
   - Measure participant error detection accuracy (hits, misses, false alarms, correct rejections)
   - Calculate d' at each timepoint
4. Compare High verification reduction (λ=0.8) vs Low verification reduction (λ=0.2) conditions
5. Perform repeated measures ANOVA: d' ~ time × condition + (1|participant)
6. Fit linear regression to d' over time, test slope significance (β < -0.5 per week)
7. Pass Gate: (d'_t=1month < 0.7 × d'_baseline) AND (ANOVA p < 0.05) AND (β < -0.5) AND (d'_λ=0.8 < d'_λ=0.2)

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | (ICC > 0.95) AND (ANOVA p > 0.05) AND (Cohen's f < 0.10) | ABORT entire chain → Route to Phase 0 for architecture re-selection |
| H-M1 | MUST_WORK | (ρ < -0.7) AND (p < 0.01) AND (disagreement reduction ≥ 1.5×) | ABORT H-M2/H-M3/H-M4 → Route to Phase 2A for mechanism revision |
| H-M2 | MUST_WORK | (Calibration error > 0.15) AND (r > 0.6) AND (p < 0.05) | ABORT H-M3/H-M4 → Consider alternative mechanisms |
| H-M3 | MUST_WORK | (Time reduction > 20%) AND (Attention < 60%) AND (Effort ≥ 1) AND (p < 0.05) | ABORT H-M4 → Alternative mechanisms |
| H-M4 | DETERMINES_SUCCESS | (d'_t=1m < 0.7×d'_base) AND (ANOVA p < 0.05) AND (β < -0.5) | Partial validation → Document limitation, proceed with revised mechanism |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1 | H-E1 (Capability decoupling) | 2-3 days (MMLU + HumanEval evaluation) |
| Phase 2 | H-M1 (Disagreement reduction) | 1-2 weeks (N=500 tasks × 5 conditions, human annotation) |
| Phase 3 | H-M2 (Trust miscalibration) | 4-5 weeks (Longitudinal study t=1hr, 1day, 1week, 1month) |
| Phase 4 | H-M3 (Verification reduction) | (Concurrent with Phase 3, eye-tracking instrumentation) |
| Phase 5 | H-M4 (HOR degradation) | (Concurrent with Phase 3, seeded error protocol) |

**Total Duration:** 6-8 weeks (Phases 3-5 run concurrently in longitudinal design)

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source Assumption | Affected Hypotheses | Mitigation Strategy |
|------|------------------|---------------------|---------------------|
| R1: Capability-compliance confound | A1 | H-E1, ALL | Pilot test Constitutional AI λ modulation, validate ICC > 0.95 before main study. Use frozen base weights. |
| R2: Seeded errors unrepresentative | A2 | H-M4 | Sample errors from empirical confusion matrix on validation set. Avoid adversarial examples. Validate error distribution matches real model failures. |
| R3: Automation bias does not apply to AI | A3 | H-M2, H-M3 | Include mediation test (P3) with randomized confidence displays. If P3 fails, automation bias mechanism rejected. |
| R4: Alternative temporal patterns | A4 | H-M4 | Pre-register three competing models (M1 linear, M2 quadratic, M3 bifurcation). Model comparison allows null discovery. |
| R5: User frustration from metacognitive intervention | A5 | (Not directly tested in H-E/H-M, tested in P4) | Monitor self-reported frustration (7-point scale). Threshold: frustration ≥7/10 → intervention fails P4. |

### 4.2 Critical Risks (Highest Impact)

**R1 (Capability-compliance confound):**
- **Likelihood:** MEDIUM (Constitutional AI architecture designed for this, but implementation details matter)
- **Impact:** CRITICAL (If violated, all results uninterpretable)
- **Mitigation:** MANDATORY pilot validation with ICC > 0.95 before proceeding to H-M1
- **Contingency:** If ICC < 0.95, switch to alternative architecture (e.g., Llama-3 with LoRA adapters for policy layer)

**R3 (Automation bias inapplicable):**
- **Likelihood:** LOW (Human factors literature supports this mechanism)
- **Impact:** HIGH (Would require mechanism revision, but partial results still valuable)
- **Mitigation:** Include P3 mediation test to isolate perceived reliability pathway
- **Contingency:** If P3 fails, explore alternative mechanisms (cognitive load, task familiarity, user interface effects)

---

## 5. Dialectical Analysis

### 5.1 Thesis (Main Hypothesis)
**Claim:** Bidirectional alignment can be measured and optimized through policy-layer ACE manipulation, with ACE-HOR coupling mediated by Bayesian trust calibration (4-step causal chain) and temporal dynamics captured by competing-process model (k₁ erosion vs k₂ learning).

**Supporting Evidence:**
1. Constitutional AI architecture enables clean policy-layer manipulation (H-E1 validation)
2. Automation bias literature from human factors research provides mechanistic grounding (H-M2, H-M3)
3. Signal detection theory + skill degradation models predict temporal HOR decline (H-M4)
4. Three competing models (M1/M2/M3) allow discovery-based testing rather than confirmation bias

**Predictions:**
- P1: Capability decoupling achievable (ICC > 0.95)
- P2: ACE-HOR coupling follows distinguishable functional form (R² ≥ 0.6)
- P3: HOR degradation mediated by perceived reliability (10% difference with randomized confidence)
- P4: Metacognitive intervention increases k₂ by ≥30%
- P5: Equilibrium region exists if M2 wins (λ* ∈ [0.4, 0.8], HOR ≥ 0.7×baseline)

---

### 5.2 Antithesis (H0 and Alternative Explanations)

**Counter-Claim:** There is no significant ACE-HOR coupling when base capability is held constant. Observed HOR changes arise from confounds (capability variation, task difficulty, user fatigue) rather than compliance-mediated trust calibration.

**Alternative Explanations:**
1. **Capability Confound (H0 primary):** λ modulation inadvertently changes base capability → all coupling spurious
   - **Test:** H-E1 with ICC > 0.95 threshold
   - **Falsifier:** If ICC < 0.95, main hypothesis fails

2. **Cognitive Load Mechanism:** High compliance reduces cognitive load (not trust) → HOR decline via reduced engagement
   - **Test:** P3 mediation test with randomized confidence displays
   - **Falsifier:** If HOR_C ≈ HOR_B (confidence randomization has no effect), perceived reliability is not the mediator

3. **Task Familiarity:** Repeated exposure (not compliance) causes HOR decline
   - **Test:** Control group without AI (human-only baseline) should show stable HOR over time
   - **Falsifier:** If human-only HOR also declines over t=1month, familiarity confound present

4. **No Equilibrium (M1 Linear or M3 Bifurcation):** Fundamental Pareto tradeoff exists, no sweet spot
   - **Test:** P2 model selection via AIC
   - **Outcome:** If M1 or M3 wins (AIC weight > 0.7), no interior equilibrium → valuable negative result

---

### 5.3 Synthesis (Integrated Understanding)

**Resolved Tensions:**
1. **Capability-Compliance Confound:** Policy-layer architectural separation (H-E1) + ICC > 0.95 validation resolves this concern. If H-E1 fails, main hypothesis invalid (appropriately strict gate).

2. **Equilibrium vs Pareto Tradeoff:** Pre-registered model comparison (M1/M2/M3) allows null discovery. Both outcomes scientifically valuable:
   - **M2 wins:** Equilibrium exists → actionable design constraints (optimal λ*)
   - **M1/M3 wins:** Fundamental tradeoff → theoretical insight (bidirectional alignment inherently constrained)

3. **Automation Bias Applicability:** P3 mediation test distinguishes automation bias (perceived reliability pathway) from alternative mechanisms (cognitive load, task familiarity). If P3 fails, mechanism revision needed but partial validation achieved.

4. **Temporal Dynamics Uncertainty:** Competing-process model (k₁ erosion vs k₂ learning) is testable via functional form fitting. Alternative patterns (oscillatory, chaotic) would be detected by model comparison.

**Robustness Assessment:**
- **5 pre-registered predictions** with explicit success criteria (no p-hacking)
- **Multiple falsification paths** (H-E1 capability check, P3 mediation test, P2 model selection)
- **Valuable negative results** (Pareto tradeoff discovery if M1/M3 wins)
- **Contingency plans** for each gate failure (documented in Risk Analysis)

**Remaining Open Questions:**
1. Optimal disagreement frequency for metacognitive intervention (15-25% range requires empirical tuning in Phase 2C)
2. Cross-domain generalization beyond medical→coding (creative writing, scientific research untested)
3. Timescale extension: do dynamics extend beyond 1-month measurement window?
4. Individual differences: expertise-dependent HOR curves (novice vs expert users)

---

## 6. Executive Summary

**Main Hypothesis:** Under human-AI collaborative tasks with policy-layer compliance manipulation, ACE-HOR coupling is governed by Bayesian trust calibration (4-step causal chain: disagreement reduction → trust miscalibration → verification reduction → HOR degradation), with functional form distinguishable as M1/M2/M3.

**Total Hypotheses:** 5 (1 existence, 4 mechanism)

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3 → H-M4

**Key Gates:**
- H-E1 (MUST_WORK): Capability decoupling validation (ICC > 0.95) → If fail, ABORT chain
- H-M1-M3 (MUST_WORK): Causal chain validation → If any fails, mechanism revision needed
- H-M4 (DETERMINES_SUCCESS): Temporal degradation test → Pass/fail both valuable outcomes

**Execution Plan:**
1. **Phase 1 (2-3 days):** H-E1 capability decoupling validation
2. **Phase 2 (1-2 weeks):** H-M1 disagreement reduction test
3. **Phases 3-5 (6-8 weeks concurrent):** Longitudinal study (H-M2/H-M3/H-M4) with t=1hr, 1day, 1week, 1month measurements

**Risk Mitigation:**
- **R1 (Capability confound):** Pilot ICC validation before main study
- **R3 (Automation bias):** P3 mediation test isolates mechanism
- **R4 (Alternative temporal patterns):** Pre-registered model comparison allows null discovery

**Success Criteria:**
- If all gates pass: Full causal chain validated → Proceed to P2 functional form selection
- If H-E1 fails: Architecture inadequate → Route to Phase 0
- If H-M1/M2/M3 fails: Mechanism revision → Route to Phase 2A
- If H-M4 fails: Partial validation → Document limitation, proceed with revised mechanism

**Next Steps:**
1. Pilot Constitutional AI λ modulation (validate ICC > 0.95)
2. Recruit N=100 participants for longitudinal study
3. Implement eye-tracking and seeded error protocols
4. Execute H-E1 → H-M1 → H-M2/M3/M4 (concurrent) verification sequence

---

*Generated by YouRA Phase 2B Planning Workflow v7.7.0 | 2026-05-11*
