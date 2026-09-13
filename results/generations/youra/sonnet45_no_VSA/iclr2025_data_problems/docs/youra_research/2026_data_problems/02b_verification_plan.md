# Phase 2B: Verification Plan

**Generated:** 2026-07-10T23:42:54Z  
**Main Hypothesis ID:** h-c1  
**Pipeline Project ID:** 01ed3ac8-ad89-4e0a-8121-d72f11f7b9a7  
**Archon Project:** Anonymous Pipeline: Confidence-Calibrated Iteration Control

---

## Main Hypothesis

**ID:** h-c1  
**Title:** Confidence-Calibrated Iteration Control for Agentic Code Generation

**Statement:**
> Calibrated confidence, implemented via temperature-scaled log-probability gating, enables adaptive iteration control that reduces execution attempts by 20-40% on code generation benchmarks while preserving pass@k accuracy.

**Type:** CONDITION (demonstrates when calibrated confidence enables cost-effective iteration control)

---

## Sub-Hypothesis Decomposition

### Sequential Validation Structure

The verification follows a **sequential gate structure** aligned with the three validation gates identified in Phase 2A:

```
H-E1 (Foundation)
  ↓
H-M1 (Gate 1: Monotonicity - CRITICAL)
  ↓
H-M2 (Gate 2: Marginal Benefit)
  ↓
H-C1 (Gate 3: Full Ablation)
```

### H-E1: Temperature Scaling Calibration (EXISTENCE)

**Statement:** Temperature scaling produces calibrated confidence scores that reduce Expected Calibration Error (ECE) by ≥30% compared to uncalibrated logits

**Type:** EXISTENCE  
**Gate Type:** MUST_WORK  
**Prerequisites:** None (foundation hypothesis)  
**Status:** READY

**Rationale:**
- Validates that the calibration mechanism itself works
- Establishes baseline calibration quality before testing behavioral relevance
- Directly tests the first component of the causal chain

**Key Metrics:**
- Expected Calibration Error (ECE)
- Reliability diagram alignment
- Calibration curve visualization

**Success Criteria:**
- ECE reduction ≥ 30% compared to uncalibrated logits
- Reliability diagram shows improved diagonal alignment
- Calibration curves demonstrate monotonic confidence-accuracy relationship

**Risk Level:** LOW  
**Estimated Effort:** 2-3 days

**Archon Task ID:** e372e957-4213-4e57-b682-229fc1a2d4cc

---

### H-M1: Confidence-Correctness Monotonicity (MECHANISM)

**Statement:** Calibrated confidence exhibits monotonic relationship with empirical code correctness (Spearman ρ ≥ 0.7, p < 0.05)

**Type:** MECHANISM  
**Gate Type:** MUST_WORK (Gate 1 - CRITICAL)  
**Prerequisites:** [h-e1]  
**Status:** NOT_STARTED

**Rationale:**
- **CRITICAL GATE:** Tests whether calibration is behaviorally meaningful
- Validates that calibrated confidence actually predicts correctness
- If this fails, the entire gating approach collapses
- Maps directly to Gate 1 from Phase 2A refinement

**Key Metrics:**
- Spearman rank correlation (ρ) between confidence bins and empirical pass rate
- Statistical significance (p-value)
- Per-bin pass rate visualization

**Success Criteria:**
- Spearman ρ ≥ 0.7
- p < 0.05
- Monotonic trend across confidence deciles

**Failure Action:** **STOP** - If monotonicity validation fails, calibration is not behaviorally relevant. Route to Phase 0 for new research direction.

**Risk Level:** HIGH (critical gate)  
**Estimated Effort:** 2-3 days

**Archon Task ID:** 8977ed16-6518-4a50-855d-1ea681affbfa

---

### H-M2: Marginal Benefit Regression (MECHANISM)

**Statement:** Marginal benefit from self-critique decreases with initial confidence (regression coefficient β < 0, p < 0.05)

**Type:** MECHANISM  
**Gate Type:** SHOULD_WORK (Gate 2)  
**Prerequisites:** [h-m1]  
**Status:** NOT_STARTED

**Rationale:**
- Tests the justification for confidence-based gating policy
- Validates that self-critique provides diminishing returns at high confidence
- Maps directly to Gate 2 from Phase 2A refinement
- SHOULD_WORK (not MUST_WORK): failure doesn't block Phase 5, but weakens the resource allocation claim

**Key Metrics:**
- Regression coefficient (β) for confidence → Δpass@1 after critique
- Statistical significance (p-value)
- Stratified analysis across confidence tertiles

**Success Criteria:**
- Regression coefficient β < 0 (negative relationship)
- p < 0.05
- Effect size significant across difficulty levels

**Failure Action:** Continue to H-C1, but note that gating may not be justified over fixed schedules. May need to reframe contribution as "calibration enables adaptive policies" rather than "confidence justifies skipping critique."

**Risk Level:** MEDIUM  
**Estimated Effort:** 3-4 days

**Archon Task ID:** 1ffb853d-f67f-4b37-87d1-f1c20ea4b3fc

---

### H-C1: Gated Execution Reduction (CONDITION)

**Statement:** Confidence-based gating reduces execution attempts by 20-40% while preserving pass@1 accuracy (Δpass@1 ≤ 2%)

**Type:** CONDITION  
**Gate Type:** MUST_WORK (Gate 3 - Full Ablation)  
**Prerequisites:** [h-m2]  
**Status:** NOT_STARTED

**Rationale:**
- Tests the complete system: calibration + gating policy
- Validates the main empirical claim (20-40% execution reduction)
- 2×2 factorial design disentangles calibration effect from gating effect
- Maps directly to Gate 3 from Phase 2A refinement

**Key Metrics:**
- Execution attempts per problem
- pass@1 accuracy
- Wall-clock time
- Cost-adjusted utility (R=1× to 10×)

**Success Criteria:**
- Execution attempts reduced by 20-40%
- Δpass@1 ≤ 2% (absolute change)
- Treatment condition (Scaled + Gated) outperforms both single-factor conditions
- Generalization to HumanEval (held-out test set)

**Experimental Design:**

| Condition | Temperature Scaling | Gating Policy | Purpose |
|-----------|---------------------|---------------|---------|
| Baseline | None | Fixed (N=1 critique) | Control |
| Scaled-only | Learned | Fixed (N=1 critique) | Calibration effect only |
| Gated-only | None | Confidence-based | Gating effect only |
| Treatment | Learned | Confidence-based | Combined effect |

**Risk Level:** HIGH (main claim validation)  
**Estimated Effort:** 5-7 days

**Archon Task ID:** ebe5cdb0-0086-49fe-9cc7-b21ef5e58fb8

---

## Dependency Graph (DAG)

```
[H-E1: Temperature Scaling Calibration]
   │
   │ (Establishes calibration quality)
   ↓
[H-M1: Confidence-Correctness Monotonicity] ← GATE 1 (CRITICAL)
   │
   │ (If PASS: confidence predicts correctness)
   ↓
[H-M2: Marginal Benefit Regression] ← GATE 2
   │
   │ (If PASS: gating justified; If FAIL: continue but weaker claim)
   ↓
[H-C1: Gated Execution Reduction] ← GATE 3 (Full Ablation)
   │
   │ (If PASS: main claim validated)
   ↓
[Phase 5: Baseline Comparison] ← DETERMINES_SUCCESS gate
```

**Critical Path:**
- H-E1 → H-M1 (Gate 1 - make-or-break) → H-M2 → H-C1 → Phase 5
- Total estimated effort: 12-17 days

**Parallelization Opportunities:**
- None - sequential dependencies enforce strict ordering
- Each hypothesis builds on validated results from previous steps

---

## Risk Analysis

### Technical Risks

| Risk | Likelihood | Impact | Mitigation | Hypothesis |
|------|-----------|--------|------------|------------|
| Temperature scaling doesn't reduce ECE | LOW | HIGH | Use established methods (UniCR, QaTS) | H-E1 |
| Calibration doesn't predict correctness | MEDIUM | CRITICAL | **STOP gate** - Route to Phase 0 | H-M1 |
| Per-round calibration drift | MEDIUM | MEDIUM | Pool rounds if needed, test per-round ECE | H-M1, H-C1 |
| Self-critique benefit doesn't correlate with confidence | MEDIUM | MEDIUM | Continue but weaken gating justification claim | H-M2 |
| Execution reduction below 20% threshold | MEDIUM | HIGH | Adjust thresholds via cost-adjusted utility | H-C1 |
| Accuracy degradation > 2% | MEDIUM | CRITICAL | Analyze failure modes, may need PARTIAL routing | H-C1 |

### Methodological Risks

| Risk | Likelihood | Impact | Mitigation | Hypothesis |
|------|-----------|--------|------------|------------|
| Dataset size insufficient for robust calibration | LOW | MEDIUM | Use MBPP (974 problems), pool rounds | H-E1, H-M1 |
| Conformal quantiles overfit to validation set | LOW | MEDIUM | Pre-register thresholds, test on HumanEval | H-C1 |
| 2×2 factorial confounded by model variance | MEDIUM | MEDIUM | Use same random seeds across conditions | H-C1 |
| Generalization failure to HumanEval | MEDIUM | HIGH | Report as negative result, analyze domain shift | H-C1 |

### Feasibility Risks

| Risk | Likelihood | Impact | Mitigation | Hypothesis |
|------|-----------|--------|------------|------------|
| Logit access unavailable | LOW | CRITICAL | Use open-weight models (Code Llama, StarCoder2) | All |
| Computational cost exceeds budget | MEDIUM | MEDIUM | Start with single model, expand if successful | All |
| Implementation complexity underestimated | MEDIUM | MEDIUM | Phase 3 complexity assessment will flag this | All |

---

## Timeline Estimation

### Phase 2C: Experiment Design (4 hypotheses)
- **Duration:** 4-6 days
- **Parallel execution:** All 4 experiment designs can be generated in parallel
- **Output:** 4 detailed experiment specification documents

### Phase 3: Implementation Planning (4 hypotheses)
- **Duration:** 6-8 days
- **Parallel execution:** Sequential (dependency chain)
- **Output:** PRD, Architecture, task breakdown for each hypothesis

### Phase 4: Code Implementation & Validation (4 hypotheses)
- **Duration:** 12-17 days (sequential execution due to dependencies)
  - H-E1: 2-3 days
  - H-M1: 2-3 days
  - H-M2: 3-4 days
  - H-C1: 5-7 days
- **Output:** Validated code with 04_validation.md reports

### Phase 5: Baseline Comparison
- **Duration:** 3-5 days
- **Output:** 05_baseline_comparison.md, DETERMINES_SUCCESS gate result

**Total Estimated Duration:** 25-36 days

---

## Gate Decision Rules

### H-E1 MUST_WORK Gate
- **PASS:** ECE reduction ≥ 30% → Proceed to H-M1
- **PARTIAL:** 15-30% ECE reduction → Modify (improve calibration method), max 1 attempt
- **FAIL:** < 15% ECE reduction → Route to Phase 0 (calibration doesn't work)

### H-M1 MUST_WORK Gate (CRITICAL)
- **PASS:** Spearman ρ ≥ 0.7, p < 0.05 → Proceed to H-M2
- **PARTIAL:** 0.5 ≤ ρ < 0.7 → **STOP** - Monotonicity too weak, route to Phase 2A-Dialogue
- **FAIL:** ρ < 0.5 → **STOP** - Confidence doesn't predict correctness, route to Phase 0

### H-M2 SHOULD_WORK Gate
- **PASS:** β < 0, p < 0.05 → Proceed to H-C1
- **PARTIAL/FAIL:** Continue to H-C1 but note weakened gating justification

### H-C1 MUST_WORK Gate
- **PASS:** 20-40% execution reduction, Δpass@1 ≤ 2% → Proceed to Phase 5
- **PARTIAL:** 10-20% reduction OR 2-5% accuracy drop → Modify (tune thresholds), max 1 attempt
- **FAIL:** < 10% reduction OR > 5% accuracy drop → Route to Phase 0

---

## Controlled Variables

From Phase 2A refinement (03_refinement.yaml):

### Datasets
- **Primary:** MBPP (974 problems)
  - Train: 60% (584 problems)
  - Calibration: 20% (195 problems)
  - Validation: 20% (195 problems)
- **Generalization Test:** HumanEval (164 problems, held-out)

### Models
- Code Llama (open-weight, logit access)
- StarCoder2 (open-weight, logit access)
- DeepSeek-Coder (open-weight, logit access)

### Calibration Method
- Temperature scaling (learned on calibration split)
- Conformal quantiles: α=0.05, β=0.20

### Gating Policy
- High confidence (> 90th percentile): Submit directly
- Medium confidence (70-90th percentile): Self-critique before submission
- Low confidence (< 70th percentile): Request execution feedback

---

## Dialectical Analysis

### Thesis
Temperature-scaled confidence can serve as an active control signal for iteration depth in agentic code generation, reducing computational cost while maintaining accuracy.

### Antithesis
Calibration may reduce descriptive error (ECE) without providing prescriptive value (behavioral prediction). Self-critique benefit may be independent of initial confidence. Cost savings may only appear under unrealistic assumptions about execution cost.

### Synthesis
Sequential validation gates test each link in the causal chain:
1. **H-E1:** Does calibration work descriptively? (ECE reduction)
2. **H-M1:** Does calibration predict behaviorally? (confidence → correctness)
3. **H-M2:** Is gating justified over fixed policies? (marginal benefit analysis)
4. **H-C1:** Does the complete system deliver the claimed benefit? (execution reduction)

This structure makes the hypothesis **maximally falsifiable** - each gate is a disconfirmation point. If Gate 1 fails, we stop immediately rather than proceeding to a doomed ablation study.

---

## Novelty & Contributions

### Primary Contribution
**First integration of temperature scaling for intermediate control flow (not just final prediction) in agentic code generation.**

Prior work:
- Calibration methods (UniCR, QaTS, ATS): Calibrate final predictions only
- Agentic systems (CODESIM, OpenCodeInterpreter): Use fixed iteration policies

This work: **Calibrated confidence as active control signal** for iteration depth

### Secondary Contribution
**Meta-level principle:** Calibration-based resource allocation for agentic systems (code generation is instantiation)

Generalizable to:
- Formal verification (when to invoke SMT solver vs. heuristic checks)
- Database query optimization (when to use expensive join strategies)
- Multi-modal agents (when to invoke vision models vs. text-only reasoning)
- Scientific discovery agents (when to run experiments vs. simulate)

### Tertiary Contribution
**Bridges model-heavy and execution-heavy paradigms** via confidence-based routing:
- Model-heavy (CODESIM): Pure simulation, no execution until final submission
- Execution-heavy (OpenCodeInterpreter): Iterate until tests pass
- This work: Confidence determines which paradigm to apply per problem

---

## Phase 2C Readiness Checklist

- [x] Main hypothesis clearly stated
- [x] Sub-hypotheses decomposed with clear statements
- [x] Gate types assigned (MUST_WORK vs. SHOULD_WORK)
- [x] Prerequisites identified (dependency chain)
- [x] Initial status set (READY vs. NOT_STARTED)
- [x] Archon project created (01ed3ac8-ad89-4e0a-8121-d72f11f7b9a7)
- [x] Hypothesis tasks created in Archon
- [x] Pipeline phase tasks created
- [x] Risk analysis completed
- [x] Timeline estimated
- [x] Controlled variables specified

**Next Action:** Proceed to Phase 2C - Generate detailed experiment design for H-E1 (first READY hypothesis)

---

## Archon Integration

### Pipeline Project
- **ID:** 01ed3ac8-ad89-4e0a-8121-d72f11f7b9a7
- **Title:** Anonymous Pipeline: Confidence-Calibrated Iteration Control
- **URL:** Check Archon dashboard for project details

### Hypothesis Task Mapping
- **H-E1:** e372e957-4213-4e57-b682-229fc1a2d4cc
- **H-M1:** 8977ed16-6518-4a50-855d-1ea681affbfa
- **H-M2:** 1ffb853d-f67f-4b37-87d1-f1c20ea4b3fc
- **H-C1:** ebe5cdb0-0086-49fe-9cc7-b21ef5e58fb8

### Pipeline Phase Tasks
- **Phase 0:** 8fa7c7ce-6f36-4900-8ff7-e36bee7ae271
- **Phase 1:** fe796b5f-9c5e-471f-a869-ccb3a65c0138
- **Phase 2A:** 104e817e-190d-448c-82f2-440021819a20
- **Phase 2B:** b8925073-85f4-4df4-ad67-50f638bfd9d3
- **Phase 2C:** 84876319-4a32-45ac-b884-071c209e9f54
- **Phase 3:** 99513db5-128b-4e4c-8b2d-ebe167ede975
- **Phase 4:** ee89fe2e-a5b5-47a9-a3bb-b7206f0f919e
- **Phase 5:** cbe7f90d-9c34-4911-837c-f0d5bf44c105
- **Phase 6:** 5ee5baad-f56a-439a-a392-990818751229
- **Phase 6.5:** bcab2be9-1283-4bb5-b115-3ae79058a725
- **Phase 6.5.1:** 6b29e44e-d304-4f63-b92a-f6c96642ffb6

---

**Phase 2B Status:** ✅ COMPLETED  
**Generated:** 2026-07-10T23:42:54Z  
**Next Phase:** Phase 2C - Experiment Design (4 hypotheses)
