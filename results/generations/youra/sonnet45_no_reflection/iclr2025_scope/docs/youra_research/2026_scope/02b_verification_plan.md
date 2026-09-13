# Verification Plan: Performance-Weighted Hierarchical Coordination

**Date:** 2026-05-12
**Hypothesis ID:** H-HierarchicalAlign-v1
**Confidence:** 0.80
**Total Hypotheses:** 3

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under conditions of intermediate task heterogeneity (mean pairwise KL divergence 0.3-1.5 between independent routing distributions), if we apply performance-weighted alignment between adapter-specific routing biases and expert utilization patterns, then joint LoRA-MoE training achieves super-additive efficiency gains (≥2% above additive baseline), because alignment induces functional decoupling where high mutual information between adapters and experts reduces cross-task gradient interference.

### 1.2 Alternative Hypothesis (H0)
There is no significant interaction effect between LoRA and MoE in a parameter-matched 2×2 factorial design (F_interaction ≤ 2.0, p ≥ 0.10).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Multi-task NLP Suite (15 task triplets) (standard) | Requires task diversity to span low/mid/high KL heterogeneity regimes. 15 triplets × 3 tasks = 45 total tasks covering NLP, code, reasoning domains. |
| **Model** | Foundation model with MoE layers (e.g., Mixtral-8x7B or equivalent) | Requires MoE architecture with 4+ experts for meaningful routing alignment. LoRA rank 8-16 for parameter efficiency. |

**Dataset Details:**
- Source: GLUE, SuperGLUE, code tasks, cross-domain QA/summarization/translation
- Path: TBD by Phase 2C

**Model Details:**
- Type: Mixture-of-Experts transformer
- Source: Pre-trained checkpoint

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Independent LoRA + MoE | Additive gains (LoRA +5%, MoE +4% = +9%) | Various downstream tasks | No adapter alignment—misses coordination benefits |
| Shared adapter (no MoE) | Established baseline | Various | No expert routing coordination—misses token-level specialization |
| MoE-only (no adapters) | Established baseline | Large-scale LM | No adapter alignment—routing is task-agnostic at token level |
| MoE-based PEFT (2024) | Structural composition | Multi-task | Structural (not functional) coordination—doesn't test regime-dependent applicability |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Independent routing distributions stable (ICC ≥ 0.7) | Required for KL-based heterogeneity measurement | ICC < 0.5: heterogeneity axis built on noise—abort analysis |
| A2 | Soft routing probabilities provide gradient signal | Standard in MoE literature (Switch Transformers) | Gradients vanish: alignment mechanism breaks |
| A3 | Performance attribution ΔL_e has SNR (CV < 1.0) | Measured via coefficient of variation | CV > 1.0: alignment amplifies stochasticity not structure |
| A4 | Task heterogeneity follows inverted-U regime | Pre-registered inequality predictions | >30% triplets violate: design-law claim rejected |
| A5 | Coordination generalizes across PEFT methods | Tested via prefix tuning validation subset | Fails in prefix tuning: principle limited to LoRA |

### 1.6 Research Gap & Novelty

**Novel Contribution:** Performance-weighted hierarchical alignment as coordination principle with regime-dependent design law. Bidirectional functional coordination (not structural composition) through differentiable performance attribution signals, validated via temporal mediation and counterfactual destruction tests.

**Differentiation from Prior Work:**
- vs. MoE-based PEFT (2024): Prior work uses MoE within adapter architecture (structural). We propose cross-level alignment between hierarchical selection mechanisms (functional)—adapters influence routing via learned biases, routing patterns refine adapter specialization via performance signals.
- vs. Standard joint LoRA+MoE: Independent co-training lacks alignment mechanism. We add performance-weighted coupling with falsifiable mediation chain and regime-dependent applicability.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M-integrated | Mechanism | MUST_WORK | H-E1 | READY |
| H-C1 | Condition | SHOULD_WORK | H-M-integrated | READY |

---

### 2.2 Hypothesis Specifications

---
#### H-E1: Super-Additive Gains Under Intermediate Heterogeneity

**Type:** EXISTENCE

**Statement**: Under conditions of intermediate task heterogeneity (mean pairwise KL divergence 0.3-1.5 between independent routing distributions), if we apply performance-weighted alignment between adapter-specific routing biases and expert utilization patterns, then joint LoRA-MoE training achieves super-additive efficiency gains exceeding the additive baseline by ≥2% absolute accuracy.

**Rationale**: This hypothesis validates the core existence claim—that coordination produces measurable super-additive benefits beyond what LoRA and MoE provide independently. Without demonstrating super-additivity in the predicted intermediate regime, the entire coordination principle lacks empirical foundation.

**Variables**:
- Independent: Alignment mechanism (enabled/disabled)
- Dependent: Super-additive gain magnitude (interaction effect from 2×2 ANOVA, % accuracy)
- Controlled: Total parameter count, optimization steps (12K all conditions), model architecture

**Verification Protocol**:
1. Select 5 task triplets with intermediate heterogeneity (mean pairwise KL 0.3-1.5)
2. Train 4 conditions per triplet: Baseline, LoRA-only, MoE-only, LoRA+MoE with alignment (5 seeds each)
3. Compute 2×2 factorial ANOVA with interaction term for each triplet
4. Test statistical significance (F_interaction > 4.0, p < 0.05) AND practical significance (coordinated - additive ≥ 2%)
5. Validate that ≥70% of mid-KL triplets satisfy both significance criteria

**Success Criteria** (PoC: Direction-based):
- Primary: Interaction F > 4.0, p < 0.05 AND coordinated outperforms additive baseline by ≥2% in ≥70% of mid-KL triplets
- Secondary: No super-additivity in low-KL (<0.3) or high-KL (>1.5) triplets (regime specificity)

**Failure Response**:
- IF fails: ABANDON (coordination hypothesis fundamentally flawed—no super-additive effect exists)

**Dependencies**: None (foundational)

**Source**: Phase 2A P1 (Primary Prediction), SH1 (Existence)

---

#### H-M-integrated: Four-Step Causal Mechanism with Temporal Mediation

**Type:** MECHANISM

**Statement**: The coordination mechanism operates through four connected steps: (1) Performance-weighted alignment loss creates differentiable gradient path from adapters to experts via soft routing probabilities, (2) Alignment training increases normalized mutual information I(A;E)/log(E) as adapters learn task-specific expert preferences (path a: β_a > 0, p < 0.001), (3) Increased MI induces functional decoupling where high-MI task pairs show reduced cross-task gradient interference (gradient cosine similarity < entropy-matched control by ≥0.2), and (4) Functional decoupling mediates super-additive performance gains (path b: β_b > 0, p < 0.01) with temporal precedence (ΔMI at step t predicts ΔPerf at t+500).

**Rationale**: This hypothesis validates the causal mechanism explaining HOW coordination produces super-additive gains. Mediation analysis with temporal precedence distinguishes true causality from spurious correlation, while destruction tests provide counterfactual evidence that alignment-MI coupling is causal not epiphenomenal.

**Variables**:
- Independent: Alignment mechanism (performance-weighted alignment loss L_align)
- Dependent: Normalized MI I(A;E)/log(E), Gradient interference (cosine similarity), Performance gains (validation accuracy)
- Controlled: Parameter count, entropy-matched random routing baseline, training steps

**Verification Protocol**:
1. Train 20 task pairs (mid-KL) with alignment enabled, track MI and performance every 100 steps; train matched baseline without alignment
2. Compute mediation paths: (a) Alignment→MI (β_a), (b) MI→Performance (β_b), (c) Total effect (β_c), (c′) Direct effect controlling for MI
3. Test temporal precedence via lagged regression: ΔMI at step t predicts ΔPerf at step t+500 (p < 0.05)
4. Measure gradient interference (cosine similarity) at 3 checkpoints (early/mid/late) for high-MI vs low-MI task pairs
5. Destruction test: permute adapter-expert associations post-training, measure performance drop proportional to MI
6. Compare gradient interference against entropy-matched random routing baseline (effect size ≥0.2)

**Success Criteria** (PoC: Direction-based):
- Primary: Path a significant (β_a > 0, p < 0.001), Path b significant (β_b > 0, p < 0.01), Mediation (β_c′ < 0.5·β_c), Temporal precedence validated
- Secondary: High-MI tasks show gradient interference < entropy-matched control by ≥0.2, Destruction test shows performance drop ∝ MI

**Failure Response**:
- IF path a fails: PIVOT (alignment doesn't increase MI—check attribution noise, gradient flow)
- IF path b fails OR mediation insufficient: EXPLORE (MI exists but doesn't mediate performance—alternative mechanism)
- IF temporal precedence fails: ABANDON (correlation not causation—mechanism explanation invalid)
- IF destruction test null: ABANDON (alignment epiphenomenal—coordination is decorative not functional)

**Dependencies**: H-E1 (requires super-additivity to exist before explaining mechanism)

**Source**: Phase 2A Causal Mechanism (4 steps), P2 (Mediation prediction)

---

#### H-C1: Regime-Switching Inverted-U Pattern Across Heterogeneity

**Type:** CONDITION

**Statement**: Task heterogeneity (measured via mean pairwise KL divergence between independent routing distributions) determines optimal architectural choice following an inverted-U pattern: Low KL (<0.3) tasks achieve best performance with shared adapters, mid KL (0.3-1.5) tasks benefit from coordinated alignment (outperforming baselines by ≥2%), and high KL (>1.5) tasks perform best with independent adapters, with ≥70% of task triplets within each regime satisfying directional inequality predictions.

**Rationale**: This hypothesis validates the regime-dependent design law—transforming coordination from an optimization trick into a predictive architectural choice framework. Pre-registered inequality tests prevent post-hoc rationalization and establish clear boundary conditions for when coordination applies.

**Variables**:
- Independent: Task heterogeneity (mean pairwise KL divergence)
- Dependent: Optimal architecture performance ranking (Shared vs Coordinated vs Independent)
- Controlled: Architecture types (fixed: Shared, Coordinated, Independent), parameter count, training protocol

**Verification Protocol**:
1. Pre-register KL bin boundaries (0.3, 1.5) and directional inequalities before data collection
2. Measure task heterogeneity via independent routing distributions (no alignment), validate ICC ≥ 0.7 for reliable KL measurement
3. Stratify 15 triplets into bins: 5 low KL (<0.3), 5 mid KL (0.3-1.5), 5 high KL (>1.5)
4. Train each triplet with 3 architectures (Shared, Coordinated, Independent) × 5 seeds
5. Test pre-registered inequalities: Low KL (Shared ≥ Coordinated), Mid KL (Coordinated > baselines by ≥2%), High KL (Independent ≥ Coordinated)
6. Count violations: if >30% triplets violate predictions within any bin, regime structure rejected

**Success Criteria** (PoC: Direction-based):
- Primary: ≥70% triplets within each KL bin satisfy directional inequality predictions (≤30% violation tolerance)
- Secondary: ICC ≥ 0.7 for routing distributions (validates heterogeneity measurement is stable not noise)

**Failure Response**:
- IF low-KL violations >30%: EXPLORE (homogeneous tasks may still benefit from coordination—scope narrower than predicted)
- IF mid-KL violations >30%: ABANDON (coordination sweet spot doesn't exist—core regime claim fails)
- IF high-KL violations >30%: EXPLORE (orthogonal tasks may benefit from coordination—scope broader than predicted)
- IF ICC < 0.5: ABORT (heterogeneity measurement unreliable—cannot validate regime structure)

**Dependencies**: H-M-integrated (requires mechanism validation before testing regime boundaries)

**Source**: Phase 2A Scope & Boundaries (Section 1.5), A4 (Inverted-U assumption)

---

## 3. Risk Analysis

### 3.1 Assumption-Based Risks

**Risk R1: Unstable Routing Distributions**

**Source Assumption:** A1 - Independent routing distributions are stable across random seeds (ICC ≥ 0.7)

**Description:** If routing distributions vary significantly across random seeds (ICC < 0.7), KL-based heterogeneity measurement becomes unreliable. The regime-switching framework would be built on noise rather than meaningful task structure.

**Affected Hypotheses:** H-E1 (mid-KL selection unreliable), H-C1 (entire regime structure invalid)

**Severity:** High (invalidates heterogeneity-based claims)

**Mitigation Strategy:**
1. **Prevention:** Pre-validate ICC ≥ 0.7 on pilot task sets before full experiment. Use multiple seeds (≥5) for ICC estimation.
2. **Detection:** Monitor within-task vs between-task KL variance ratio. If ICC < 0.5 for >30% of tasks, routing reliability compromised.
3. **Response:**
   - PIVOT: If ICC ∈ [0.5, 0.7): Increase seeds to 10, aggregate measurements
   - SCOPE: If ICC < 0.5: Exclude unreliable tasks from heterogeneity analysis, document as limitation
   - ABORT: If ICC < 0.5 for >50% of tasks: Heterogeneity axis fundamentally unreliable, abandon H-C1

**Early Warning Indicators:**
- ICC < 0.7 in pilot runs
- High variance in KL measurements across seeds
- Inconsistent task binning across random initializations

---

**Risk R2: Vanishing Gradients Through Soft Routing**

**Source Assumption:** A2 - Soft routing probabilities (pre-top-k) provide sufficient gradient signal for alignment

**Description:** If gradients vanish or become too noisy when backpropagating through soft routing probabilities, the alignment mechanism cannot learn meaningful adapter-expert associations.

**Affected Hypotheses:** H-M-integrated (path a: Alignment→MI fails)

**Severity:** Critical (breaks core mechanism)

**Mitigation Strategy:**
1. **Prevention:** Use temperature-scaled softmax with tunable τ (start τ=1.0). Monitor gradient norms through routing layer during warmup.
2. **Detection:** Track alignment loss magnitude and gradient flow metrics. If ∂L_align/∂A_e < 10⁻⁶ consistently, gradients insufficient.
3. **Response:**
   - PIVOT: Adjust temperature τ ∈ [0.5, 2.0] to strengthen gradient signal
   - PIVOT: Use straight-through estimator for discrete routing if continuous optimization fails
   - ABORT: If gradient flow absent across all temperature settings, soft routing incompatible with alignment

**Early Warning Indicators:**
- Alignment loss plateau at initialization value
- Gradient norms through routing layer < 10⁻⁶
- MI does not increase despite alignment loss applied

---

**Risk R3: High Attribution Noise**

**Source Assumption:** A3 - Performance attribution ΔL_e has acceptable signal-to-noise ratio (CV < 1.0)

**Description:** If performance attribution ΔL_e is too noisy across minibatches (CV > 1.0), alignment loss amplifies stochasticity rather than learning stable expert-task affinity structure.

**Affected Hypotheses:** H-M-integrated (alignment signal quality), H-E1 (super-additivity may fail due to unstable learning)

**Severity:** High (degrades mechanism quality)

**Mitigation Strategy:**
1. **Prevention:** Use larger batch sizes (≥32 per task) for stable attribution estimates. Exponential moving average (EMA) with α=0.9 for ΔL_e smoothing.
2. **Detection:** Monitor coefficient of variation CV(ΔL_e) = σ(ΔL_e) / μ(ΔL_e) across batches. If CV > 1.0 for >30% of training, attribution too noisy.
3. **Response:**
   - PIVOT: Increase batch size to 64 or 128 to reduce variance
   - PIVOT: Increase EMA α to 0.95 for stronger smoothing
   - SCOPE: If CV remains high: Reduce alignment loss weight λ_align, accept weaker coordination
   - ABORT: If CV > 2.0 persistently: Attribution fundamentally unstable, mechanism infeasible

**Early Warning Indicators:**
- High variance in alignment loss across batches
- MI increases but with high jitter (unstable growth)
- Performance gains inconsistent across seeds despite similar MI

---

**Risk R4: Violated Regime Inequalities**

**Source Assumption:** A4 - Task heterogeneity follows inverted-U regime structure (shared→coordinated→independent)

**Description:** If >30% of task triplets within a KL bin violate the pre-registered directional inequalities, the regime-switching design law fails. Coordination may work uniformly or not at all.

**Affected Hypotheses:** H-C1 (entire regime hypothesis), H-E1 scope claims (mid-KL specificity)

**Severity:** Medium (limits theoretical contribution but doesn't invalidate core mechanism)

**Mitigation Strategy:**
1. **Prevention:** Pre-register inequality predictions and KL bin boundaries (0.3, 1.5) before data collection. Use diverse task sources to ensure broad regime coverage.
2. **Detection:** Track violation rate per bin during experiments. If violations exceed 30% in any bin, regime structure unsupported.
3. **Response:**
   - PIVOT: If low-KL violations: Document that coordination benefits extend to homogeneous tasks (broader scope)
   - PIVOT: If high-KL violations: Document that coordination benefits extend to orthogonal tasks (broader scope)
   - SCOPE: If mid-KL violations: Coordination exists but regime boundaries differ—refine thresholds post-hoc as exploratory
   - ABORT: If >50% overall violations: No regime structure exists, coordination benefits are task-independent or absent

**Early Warning Indicators:**
- Violation rate >20% in pilot experiments
- Regime boundaries (0.3, 1.5) produce unbalanced bin sizes
- Performance trends continuous rather than regime-switching

---

**Risk R5: PEFT-Specific Coordination (No Generalization)**

**Source Assumption:** A5 - Coordination mechanism generalizes across PEFT methods (not LoRA-specific)

**Description:** If prefix tuning validation fails to show inverted-U pattern and MI mediation (p ≥ 0.1), the coordination principle depends on low-rank parameterization and does not generalize beyond LoRA.

**Affected Hypotheses:** All (limits scope to LoRA-only, reduces theoretical significance)

**Severity:** Medium (scope limitation, not fundamental failure)

**Mitigation Strategy:**
1. **Prevention:** Design prefix tuning validation carefully: same task sets, matched parameter budgets, same routing architecture.
2. **Detection:** Run prefix tuning on 5 mid-KL tasks. Test: super-additive interaction (F > 4.0) AND MI mediation (paths a, b significant).
3. **Response:**
   - PIVOT: If interaction absent but MI increases: Mechanism operates but effect size insufficient—document as LoRA-specific optimization
   - SCOPE: If both fail: Scope coordination principle to low-rank PEFT methods (LoRA, LoRA variants)
   - DOCUMENT: Generalization failure is acceptable—contribution remains significant even if LoRA-specific

**Early Warning Indicators:**
- Prefix tuning shows no MI increase under alignment
- Prefix tuning super-additive interaction F < 2.0
- Mechanism operates differently in prefix vs LoRA settings

---

### 3.2 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Unstable routing distributions | A1 | High | H-E1, H-C1 | Pre-validate ICC ≥ 0.7, exclude unreliable tasks |
| R2 | Vanishing gradients through soft routing | A2 | Critical | H-M-integrated | Tune temperature, monitor gradient flow |
| R3 | High attribution noise | A3 | High | H-M-integrated, H-E1 | Larger batches, EMA smoothing |
| R4 | Violated regime inequalities | A4 | Medium | H-C1 | Pre-register predictions, 30% tolerance |
| R5 | PEFT-specific (no generalization) | A5 | Medium | All (scope) | Prefix tuning validation on subset |

**Risk Distribution:**
- Critical: 1 (R2)
- High: 2 (R1, R3)
- Medium: 2 (R4, R5)

All risks have defined mitigation strategies with prevention, detection, and response protocols.

---

## 4. Execution

### 3.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════════════
        DEPENDENCY GRAPH (DAG) - 3 Hypotheses
═══════════════════════════════════════════════════════════════════

[Phase 1 - Foundation]
    ┌─────────────────────────────────────────────────────────┐
    │  H-E1: Super-Additive Gains (EXISTENCE)                 │
    │  Gate: MUST_WORK                                        │
    │  Test: 2×2 ANOVA interaction F > 4.0, p < 0.05          │
    └─────────────────────────────────────────────────────────┘
                            │
                            ▼
    ┌──────────────── GATE 1 ────────────────┐
    │ Pass: Proceed to mechanism validation  │
    │ Fail: ABORT - no super-additivity      │
    └────────────────────────────────────────┘
                            │
                            ▼
[Phase 2 - Mechanism]
    ┌─────────────────────────────────────────────────────────┐
    │  H-M-integrated: 4-Step Causal Mechanism (MECHANISM)    │
    │  Prerequisites: H-E1                                    │
    │  Gate: MUST_WORK                                        │
    │  Test: Mediation paths (a, b), temporal precedence     │
    └─────────────────────────────────────────────────────────┘
                            │
                            ▼
    ┌──────────────── GATE 2 ────────────────┐
    │ Pass: Proceed to regime validation     │
    │ Fail: EXPLORE - alternative mechanism  │
    └────────────────────────────────────────┘
                            │
                            ▼
[Phase 3 - Regime Boundaries]
    ┌─────────────────────────────────────────────────────────┐
    │  H-C1: Regime-Switching Pattern (CONDITION)            │
    │  Prerequisites: H-M-integrated                          │
    │  Gate: SHOULD_WORK                                      │
    │  Test: Pre-registered inequality predictions           │
    └─────────────────────────────────────────────────────────┘
                            │
                            ▼
    ┌──────────────── GATE 3 ────────────────┐
    │ Pass: Design law validated              │
    │ Fail: SCOPE - document limitations      │
    └────────────────────────────────────────┘
                            │
                            ▼
                     [COMPLETE]

═══════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M-integrated → H-C1
Parallelization: None (sequential dependencies)
═══════════════════════════════════════════════════════════════════
```

### 3.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | If Fails |
|-------|-----------|---------------|-----------|----------|
| 0 | H-E1 | None | MUST_WORK | ABORT entire hypothesis |
| 1 | H-M-integrated | H-E1 | MUST_WORK | EXPLORE alternative mechanisms |
| 2 | H-C1 | H-M-integrated | SHOULD_WORK | SCOPE reduction (no design law) |

### 3.3 Gate Summary

| Gate | Hypothesis | Pass Condition | Fail Action |
|------|-----------|----------------|-------------|
| Gate 1 | H-E1 | F > 4.0, p < 0.05 AND ≥2% gain in ≥70% triplets | ABORT - no super-additivity exists |
| Gate 2 | H-M-integrated | All mediation paths significant + temporal precedence | EXPLORE - mechanism differs from theory |
| Gate 3 | H-C1 | ≤30% inequality violations across bins | SCOPE - regime structure limited/absent |

### 3.4 Execution Timeline

| Phase | Hypotheses | Duration | Gate |
|-------|------------|----------|------|
| Phase 1 | H-E1 | 2-3 weeks | MUST_WORK |
| Phase 2 | H-M-integrated | 3-4 weeks | MUST_WORK |
| Phase 3 | H-C1 | 4-5 weeks | SHOULD_WORK |
| Integration | Analysis & reporting | 1 week | - |

**Total Duration:** ~10-13 weeks (Phase 2C → 4 execution)

**Critical Path:** H-E1 → H-M-integrated → H-C1 (Sequential, no parallelization)

---

## 5. Executive Summary & Recommendations

**Main Hypothesis:** Performance-weighted hierarchical coordination between LoRA adapters and MoE routing yields super-additive efficiency gains under intermediate task heterogeneity.
- ID: H-HierarchicalAlign-v1, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (Phase 2A pre-validated)
- Sub-Hypotheses: 3 total (H-E1, H-M-integrated, H-C1)
- Phases: 3 phases over 10-13 weeks
- Critical Gates: 3 decision points (2 MUST_WORK, 1 SHOULD_WORK)

**Risk Assessment:** Medium-High
- Critical: Vanishing gradients through soft routing (R2)
- High: Unstable routing distributions (R1), Attribution noise (R3)
- All risks have mitigation strategies

**Scope Reduction:** 60% efficiency gain (LoRA, MoE, maturity BUILD_ON claims)

**Immediate Action:** Begin Phase 2C experiment design for H-E1

**Key Recommendations:**
1. **Phase 1 Priority:** Validate H-E1 super-additivity first (MUST_WORK gate)
2. **Risk Monitoring:** Pre-validate ICC ≥ 0.7, monitor gradient flow, use large batches
3. **Resource Allocation:** Reserve 10-13 weeks for sequential execution (no parallelization)
4. **Failure Protocol:** Execute PIVOT strategies per risk mitigation plan

---

*Generated by YouRA Phase 2B Planning | 2026-05-12 | 3 hypotheses validated*
