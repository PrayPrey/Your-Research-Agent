---
title: "Verification Plan: Equivariant Encoders for Generalization Gap Prediction"
hypothesis_id: H-GenGapEquiv-v1
date: "2026-08-31"
status: complete
stepsCompleted:
  - step-00-init-environment
  - step-01-init-parsing
  - step-02-input-hypothesis
  - step-03-hypothesis-generation
  - step-04-hypothesis-inventory
  - step-05-risk-analysis
  - step-06-dependency-graph
  - step-07-timeline-planning
  - step-08-dialectical-analysis
  - step-09-summary
  - step-10-finalize
completedAt: "2026-08-31"
---

# Verification Plan: Equivariant Encoders for Generalization Gap Prediction

**Date:** 2026-08-31
**Hypothesis ID:** H-GenGapEquiv-v1
**Confidence:** 0.83
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Permutation-equivariant weight encoders (DWS, NFT, GNN) show a disproportionately larger Spearman correlation improvement over flat MLP on generalization gap prediction (train_acc − test_acc at convergence) compared to their improvement on test accuracy prediction, because architectural parameter sharing across neuron equivalence classes forces distributed weight statistics extraction — the type of signal that generalization gap encodes.

**Key Quantity:** Δ = Spearman_r(gap, equivariant) − Spearman_r(gap, flat_MLP) − [Spearman_r(test_acc, equivariant) − Spearman_r(test_acc, flat_MLP)]
**Prediction:** Δ > 0.02 for ≥2 of 3 equivariant encoders (DWS, NFT, GNN)

### 1.2 Alternative Hypothesis (H0)

Equivariant encoders do NOT show a differential improvement on generalization gap prediction relative to test accuracy prediction; any observed difference is within noise (Δ ≤ 0.02 Spearman units). Architectural equivariance provides no target-specific advantage; both gap and test_acc are equally (un)accessible to all encoder types.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Unterthiner CIFAR-10 CNN zoo (~10K models, standard) | Contains both train_acc and test_acc; generalization_gap = train_acc − test_acc directly computable |
| **Model** | DWS, NFT, GNN (vs. flat MLP baseline) | All public codebases; equivariant property is the key independent variable |

**Dataset Details:**
- Source: Unterthiner et al. 2020 (arxiv 2002.11448), public
- Path: TBD (public repository download)
- Secondary: Schürholt PDFD zoo (2110.15288) as cross-zoo generalization test / A1-failure fallback

**Model Details:**
- Type: Weight-space encoders (permutation-equivariant vs. non-equivariant)
- Source: DWSNets repo (Navon 2023), neural-graphs repo (Zhou 2023, Kofinas 2024), flat MLP (Unterthiner 2020)

### 1.4 Baseline Methods

| Method | Performance (test_acc) | Dataset | Role |
|--------|------------------------|---------|------|
| Flat MLP (Unterthiner) | Spearman r baseline | CIFAR-10 zoo | Primary comparison |
| DWS (Navon 2023) | Spearman r ≈ 0.9 | CIFAR-10 zoo | Equivariant encoder 1 |
| NFT (Zhou 2023) | State-of-art test_acc | CIFAR-10 zoo | Equivariant encoder 2 |
| GNN (Kofinas 2024) | Competitive with DWS | CIFAR-10 zoo | Equivariant encoder 3 |
| Eilertsen weight stats | TBD (spectral norms) | CIFAR-10 zoo | Hand-crafted baseline |

**Note:** All baselines evaluated on test_acc only (prior work). This study adds gap as second target.

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Generalization gap has meaningful independent variance from test_acc (Spearman(gap, −test_acc) < 0.95) | Statistical independence expected from training diversity | Switch to Schürholt PDFD as primary venue |
| A2 | Weight tensor information sufficient for gap prediction is accessible to all encoder types | All encoders operate on full weight tensor; flat MLP has sufficient capacity | Design controls unaffected; reduces theoretical claim |
| A3 | Equal 50-trial random search budget approximates best performance for each encoder | Standard practice in neural architecture search | Report top-5 sensitivity analysis; conclusion narrowed |
| A4 | Unterthiner zoo training regime provides meaningful test (fixed arch, varying LR/WD/optimizer) | Established benchmark for weight encoders | Limits generalizability; clearly scoped in paper |

### 1.6 Research Gap & Novelty

**Primary novelty:** First controlled comparison of equivariant vs. non-equivariant weight encoders on **generalization gap** as prediction target (all prior work targets test accuracy only).

**Secondary novelty:** First empirical test of whether equivariance advantage is **target-dependent** (gap vs. test_acc), connecting inductive bias design to the nature of the prediction target.

**Theoretical novelty:** First to connect permutation-equivariant inductive bias to PAC-Bayes-style generalization measures — equivariant encoders share the permutation-invariance property with PAC-Bayes flatness/margin measures.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | MUST_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | NOT_STARTED |
| H-M4 | MECHANISM | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Generalization Gap Predictability Existence**

**Statement**: Under convergence-regime conditions in the Unterthiner CIFAR-10 CNN zoo, if weight encoders are trained to predict generalization gap (train_acc − test_acc), then at least one encoder type achieves Spearman r > 0.5 on the held-out test set, because generalization gap at convergence encodes a non-trivial learnable signal in the weight tensor.

**Rationale**: Before testing differential equivariance effects, we must verify that gap is predictable at all. If no encoder achieves Spearman > 0.5, the premise of the main hypothesis (that gap encodes a distinctive signal) is false. This also validates A1: if gap is highly correlated with test_acc, it adds no new information.

**Variables**:
- Independent: encoder_type ∈ {flat_MLP, DWS, NFT, GNN}
- Dependent: Spearman_r(predicted gap, true gap) on test split
- Controlled: Dataset (Unterthiner zoo), 80/10/10 split, 50-trial budget, equal compute

**Verification Protocol**:
1. Run data audit: compute Spearman(gap, −test_acc) on full zoo; if ≥ 0.95, switch to PDFD zoo (A1 check)
2. Train all 4 encoders on gap target using 50-trial random search; select best by Spearman on validation set
3. Evaluate best model per encoder on held-out test set; report Spearman r and MSE
4. Check: ≥1 encoder achieves Spearman(gap) > 0.5 on test set
5. Record gap distribution statistics (mean, std, range) for context

**Success Criteria (PoC)**:
- Primary: ≥1 encoder achieves Spearman_r(gap) > 0.5 on test split
- Secondary: Data audit passes (Spearman(gap, −test_acc) < 0.95)

**Failure Response**:
- IF Spearman(gap) ≤ 0.5 for all encoders AND A1 holds: PIVOT → investigate gap distribution, consider PDFD zoo
- IF A1 fails (gap ≈ −test_acc): PIVOT → switch primary venue to PDFD zoo (per pre-specified fallback)

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 1.6 (P1), Section 1.4 (A1), phase2b_readiness.sh1_existence

---

**H-M1: Distributed Gap Signal in Weight Tensor**

**Statement**: Under convergence-regime conditions, if generalization gap is predicted from weight tensors, then the prediction error is lower when the encoder computes globally distributed statistics (across all neurons) compared to locally position-indexed statistics, because overfitting signal is spread across the full weight tensor — no single neuron or layer localizes it.

**Rationale**: This is the first causal mechanism step: gap signal is distributed, not local. If flat MLP (position-indexed) achieves comparable Spearman to equivariant encoders on gap, the distribution hypothesis fails and the mechanism is broken. This step validates that the gap target fundamentally differs from test_acc in its weight-space structure.

**Variables**:
- Independent: encoder_type (flat_MLP as position-indexed proxy vs. equivariant encoders)
- Dependent: Spearman_r(gap) per encoder; relative ranking flat_MLP vs. equivariant
- Controlled: Same dataset, same budget, same evaluation protocol as H-E1

**Verification Protocol**:
1. Use results from H-E1 encoder training (no retraining needed)
2. Compare Spearman_r(gap) across flat_MLP vs. {DWS, NFT, GNN}
3. Compute Δ_gap = mean Spearman_r(gap, equivariant) − Spearman_r(gap, flat_MLP)
4. Verify: Δ_gap > 0 for ≥1 equivariant encoder (directional test)
5. Report: gap vs. test_acc Spearman rank ordering across encoders

**Success Criteria (PoC)**:
- Primary: ≥1 equivariant encoder shows higher Spearman(gap) than flat_MLP

**Failure Response**:
- IF flat_MLP matches or exceeds equivariant encoders on gap: EXPLORE → check A3 (budget sufficiency), tune equivariant encoders further; if persists: PIVOT on mechanism claim

**Dependencies**: H-E1 (gap must be predictable first)

**Source**: Phase 2A synthesis.mechanistic_story.step1, Section 1.3 causal mechanism

---

**H-M2: Equivariant Parameter Sharing Forces Orbit-Averaged Representations**

**Statement**: Under fixed hyperparameter search conditions, if permutation-equivariant encoders (DWS, NFT, GNN) are applied to weight tensors from the same model zoo, then their internal representations are measurably different from flat MLP representations in that they capture orbit-averaged (globally distributed) statistics, because architectural parameter sharing across neuron equivalence classes prevents learning of position-specific spurious features.

**Rationale**: This mechanism step validates the architectural reason for the advantage. Even if H-M1 shows equivariant encoders outperform flat MLP on gap, we need to verify the mechanism: equivariant encoders cannot learn sorting-dependent features during training, while flat MLP on sorted weights retains this capacity. This is the theoretical cornerstone.

**Variables**:
- Independent: encoder_type (equivariant vs. flat_MLP)
- Dependent: differential performance on gap vs. test_acc prediction (Δ = differential advantage)
- Controlled: Same zoo, budget, seeds

**Verification Protocol**:
1. Compute Spearman_r(test_acc) for all 4 encoders (standard task from prior work)
2. Compute Δ = Spearman_r(gap, equivariant) − Spearman_r(gap, flat_MLP) − [Spearman_r(test_acc, equivariant) − Spearman_r(test_acc, flat_MLP)]
3. Verify: Δ > 0.02 for ≥2 of 3 equivariant encoders (P1 threshold)
4. Perform partial correlation: Spearman(equivariant_pred_gap, true_gap | test_acc) > 0, p < 0.05 (P3)
5. Report: Δ with 95% CI via bootstrap over top-5 configurations

**Success Criteria (PoC)**:
- Primary: Δ > 0.02 for ≥2 equivariant encoders (P1 confirmed)
- Secondary: Partial Spearman > 0, p < 0.05 for ≥1 equivariant encoder (P3 confirmed)

**Failure Response**:
- IF Δ ≤ 0 for all equivariant encoders: PIVOT → check A3 (budget equality), verify training convergence
- IF Δ > 0 but < 0.02 for all: Document as marginal effect, scope conclusions carefully

**Dependencies**: H-M1 (equivariant advantage on gap must exist first)

**Source**: Phase 2A key_quantity.formula, predictions.P1, predictions.P3, synthesis.differential_effect_hypothesis

---

**H-M3: Orbit-Averaged Statistics Capture Distributed Gap Signal More Faithfully**

**Statement**: Under convergence-regime conditions with the Unterthiner zoo, if equivariant encoders outperform flat MLP on generalization gap prediction (Δ > 0), then this advantage is specific to the gap target and NOT equally present for test accuracy prediction, because gap's distributed weight-space structure selectively benefits architectures that compute globally-averaged statistics.

**Rationale**: This is the target-specificity claim — the core novelty. It distinguishes between "equivariant encoders are better at everything" (uninformative) and "equivariant encoders have a differential advantage on gap relative to test_acc" (the specific claim). Without this, the result is a replication of known equivariant encoder superiority, not a new finding.

**Variables**:
- Independent: prediction target (gap vs. test_acc) × encoder_type
- Dependent: Δ = differential advantage metric (defined in H-M2)
- Controlled: same encoders, same zoo, same budget

**Verification Protocol**:
1. Use Spearman_r(test_acc) and Spearman_r(gap) from H-M1/H-M2 experiments
2. Compute Δ for each equivariant encoder (already computed in H-M2 Step 2)
3. Verify: Δ > 0.02 for ≥2 encoders confirms target-specificity claim
4. Report sensitivity: mean ± std of Δ across top-5 configurations per encoder
5. Cross-zoo validation: replicate on Schürholt PDFD zoo for generalization check

**Success Criteria (PoC)**:
- Primary: Δ > 0.02 confirmed for ≥2 of 3 equivariant encoders across both zoos
- Secondary: Cross-zoo consistency (PDFD results directionally consistent with Unterthiner)

**Failure Response**:
- IF Δ > 0 for gap but equivariant also outperform by similar margin on test_acc: EXPLORE → partial correlation to tease apart; scope claim narrowly
- IF PDFD contradicts Unterthiner: Document as zoo-specific effect; narrow generalization claim

**Dependencies**: H-M2 (differential metric must be defined and non-trivial)

**Source**: Phase 2A novelty.secondary, predictions.P1, experimental_setup.phase_4_cross_zoo

---

**H-M4: NFT Cross-Layer Attention Provides Additional Gap-Specific Advantage**

**Statement**: Under the same experimental conditions, if NFT (cross-layer attention encoder) is compared to DWS (within-layer equivariant encoder) on generalization gap prediction, then NFT achieves higher Spearman_r(gap) than DWS by ≥ 0.01, because NFT's cross-layer attention captures inter-layer weight co-variation which is specifically relevant for overfitting signal (which spans multiple layers) but less so for test accuracy (which is more locally predictable).

**Rationale**: This tests the architectural hierarchy within equivariant encoders — not all equivariant encoders are equal for gap prediction. NFT's cross-layer mechanism provides an additional inductive bias beyond within-layer equivariance. This is P2 from Phase 2A and represents the most specific, highest-risk prediction. Failure narrows but does not invalidate the main claim.

**Variables**:
- Independent: encoder architecture (NFT vs. DWS, both equivariant)
- Dependent: Spearman_r(gap) for NFT vs. DWS
- Controlled: same zoo, equal budget, same evaluation

**Verification Protocol**:
1. Extract Spearman_r(gap) for NFT and DWS from H-M1-M3 experiments
2. Compute NFT_gap − DWS_gap (P2 test)
3. Verify: NFT_Spearman(gap) > DWS_Spearman(gap) by ≥ 0.01
4. Check: DWS_Spearman(test_acc) ≥ NFT_Spearman(test_acc) (confirming target-specificity of NFT advantage)
5. Report: Effect size with bootstrap CI across top-5 configurations

**Success Criteria (PoC)**:
- Primary: NFT_Spearman(gap) > DWS_Spearman(gap) by ≥ 0.01

**Failure Response**:
- IF NFT ≤ DWS on gap: Document as non-significant within equivariant class; main claim (H-M3) unaffected; scope NFT-specific claim out of conclusions

**Dependencies**: H-M3 (equivariant encoder differential advantage must be established first)

**Source**: Phase 2A predictions.P2, causal_mechanism.theoretical_grounding[2]

---

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  HYPOTHESIS INVENTORY COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generated: 5 hypotheses

| Type      | Count | IDs               |
|-----------|-------|-------------------|
| Existence | 1     | H-E1              |
| Mechanism | 4     | H-M1, H-M2, H-M3, H-M4 |
| Condition | 0     | N/A               |

Each specification: ~40-50 lines with verification protocol
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | ≥1 encoder Spearman(gap) > 0.5 | STOP: reassess entire hypothesis |
| H-M1 | MUST_WORK | ≥1 equivariant encoder Spearman(gap) > flat_MLP | EXPLORE then PIVOT if persists |
| H-M2 | MUST_WORK | Δ > 0.02 for ≥2 of 3 equivariant encoders (P1) | PIVOT: check budget/training |
| H-M3 | MUST_WORK | Δ confirmed target-specific; cross-zoo consistent | Narrow scope; document limitations |
| H-M4 | SHOULD_WORK | NFT Spearman(gap) > DWS by ≥ 0.01 | Scope NFT claim out; main claim holds |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Core Mechanisms | H-M1, H-M2, H-M3, H-M4 | 4 weeks (sequential) |
| **Total** | **5 hypotheses** | **6 weeks** |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1: Train_acc Ceiling Confound (from A1)**

**Source Assumption:** A1 — Gap has meaningful independent variance from test_acc (Spearman(gap, −test_acc) < 0.95)

**Description:** If all models in Unterthiner zoo have train_acc ≈ 1.0, then gap = 1 − test_acc and gap prediction becomes trivially identical to test_acc prediction. The differential Δ metric becomes uninformative because both targets are the same signal.

**Affected Hypotheses:** H-E1 (data audit gate), H-M2, H-M3 (Δ metric collapses)

**Severity:** Critical

**Mitigation Strategy:**
1. **Prevention:** Mandatory data audit before any training — run Spearman(gap, −test_acc) on full zoo
2. **Detection:** If Spearman ≥ 0.95, ceiling confirmed
3. **Response:**
   - PIVOT: Switch primary venue to Schürholt PDFD zoo (pre-specified fallback)
   - SCOPE: Retain Unterthiner as secondary venue with caveat

**Early Warning Indicators:**
- Mean train_acc > 0.98 across zoo
- Gap variance < 0.01 (very low spread)

---

**Risk R2: Encoder Budget Inequity (from A3)**

**Source Assumption:** A3 — 50-trial equal budget approximates best performance for each encoder

**Description:** NFT is architecturally more complex (cross-layer attention) and may require more hyperparameter trials to converge. Under a fixed 50-trial budget, NFT may appear worse than DWS not because of architectural inferiority but because of under-optimization.

**Affected Hypotheses:** H-M1, H-M2, H-M3, H-M4 (any performance comparison)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Pre-specify and lock 50-trial budget before any training; report top-5 sensitivity
2. **Detection:** Monitor NFT validation curves for convergence; compare trial efficiency plots
3. **Response:**
   - SCOPE: Report sensitivity analysis across top-1 vs. top-5 configurations per encoder
   - EXPLORE: If NFT clearly under-optimized, note as limitation; don't expand budget mid-experiment

**Early Warning Indicators:**
- NFT val curves still improving at trial 45-50 (not converged)
- NFT top-5 variance much larger than DWS top-5 variance

---

**Risk R3: Flat MLP Invariance via Sorting (from A2)**

**Source Assumption:** A2 — Weight tensor information accessible to all encoders in principle

**Description:** Flat MLPs applied to sorted/canonicalized weights are already permutation-invariant at inference. If sorting-based preprocessing is sufficient to capture gap signal, the architectural equivariance advantage disappears — both architectures become functionally equivalent.

**Affected Hypotheses:** H-M2, H-M3 (mechanism claim)

**Severity:** High

**Mitigation Strategy:**
1. **Prevention:** Use the theoretical distinction: sorting = preprocessing invariance (spurious features still learnable during training); equivariance = training-time invariance (spurious features architecturally blocked)
2. **Detection:** If flat MLP on sorted weights matches equivariant encoders on gap, mechanism claim is weakened
3. **Response:**
   - EXPLORE: Analyze flat MLP learned features; check for position-dependent patterns
   - SCOPE: Weaken claim from "equivariance necessary" to "equivariance sufficient and practically superior"

**Early Warning Indicators:**
- Flat MLP Spearman(gap) within 0.02 of best equivariant encoder
- Ablation: removing sorting preprocessing substantially degrades flat MLP on gap

---

**Risk R4: Zoo-Specific Result (from A4)**

**Source Assumption:** A4 — Unterthiner zoo provides a meaningful test of the hypothesis

**Description:** The result may be specific to the Unterthiner zoo's particular training regime (fixed CNN architecture, varying LR/WD/optimizer). The differential equivariance advantage may not generalize to other model families or training diversity levels.

**Affected Hypotheses:** H-M3 (generalizability claim), H-M4 (NFT advantage)

**Severity:** Medium

**Mitigation Strategy:**
1. **Prevention:** Dual-zoo design with Schürholt PDFD as secondary venue
2. **Detection:** Run H-M3 cross-zoo validation step (Verification Protocol Step 5)
3. **Response:**
   - SCOPE: Restrict claims to fixed-architecture convergence-regime settings
   - EXPLORE: If PDFD contradicts Unterthiner, analyze zoo-level moderators

**Early Warning Indicators:**
- PDFD Δ < 0 while Unterthiner Δ > 0.02
- Different encoder rank orderings between zoos

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity |
|------|--------|---------------------|----------|
| R1: Train_acc ceiling | A1 | H-E1, H-M2, H-M3 | Critical |
| R2: Encoder budget inequity | A3 | H-M1, H-M2, H-M3, H-M4 | High |
| R3: Flat MLP sorting invariance | A2 | H-M2, H-M3 | High |
| R4: Zoo-specific generalization | A4 | H-M3, H-M4 | Medium |

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RISK ANALYSIS COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Risks: 4 (1 Critical, 2 High, 1 Medium, 0 Low)
All risks mapped to hypotheses with mitigation strategies.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) — 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 — Root]
    H-E1 (EXISTENCE, MUST_WORK — no prerequisites)
         │
         ▼ [Gate 1: MUST_WORK — failure = STOP]
[Level 1 — Mechanism Core]
    H-M1 (MECHANISM, MUST_WORK ← H-E1)
         │
         ▼
[Level 2 — Differential Effect]
    H-M2 (MECHANISM, MUST_WORK ← H-M1)
         │
         ▼
[Level 3 — Target Specificity]
    H-M3 (MECHANISM, MUST_WORK ← H-M2)
         │
         ▼
[Level 4 — NFT Architectural Hierarchy]
    H-M4 (MECHANISM, SHOULD_WORK ← H-M3)
         │
         ▼ [Gate Final: Verification Complete]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
All sequential — no parallelization (incremental mode)
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy Table

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-E1 | None | MUST_WORK |
| 1 | H-M1 | H-E1 | MUST_WORK |
| 2 | H-M2 | H-M1 | MUST_WORK |
| 3 | H-M3 | H-M2 | MUST_WORK |
| 4 | H-M4 | H-M3 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE — 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2    │ W3-4    │ W5      │ W6      │ W7
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────
PHASE 1: Foundation
  H-E1           │ ████████│         │         │         │
  Data Audit     │ ◆       │         │         │         │
  [Gate 1]       │         │ ◆       │         │         │
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────
PHASE 2: Core Mechanisms
  H-M1           │         │ ████████│         │         │
  H-M2           │         │         │ ████    │         │
  H-M3           │         │         │         │ ████    │
  H-M4           │         │         │         │         │ ████
  [Gate 2]       │         │         │         │         │    ◆
─────────────────┼─────────┼─────────┼─────────┼─────────┼─────
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

**Note:** H-M1 through H-M4 largely share experimental infrastructure (same encoder training runs from H-E1). W3-4 = primary training; W5-W7 = analysis, cross-zoo validation, and NFT-DWS comparison.

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

Total Duration: 6 weeks
  Formula: 2 (H-E1) + 1 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (H-M4)

Slack Available: 0 weeks (all sequential)

Note: H-M1 through H-M4 share encoder training compute from H-E1.
Actual GPU time concentrated in Weeks 1-4; Weeks 5-7 are analysis.

Estimated GPU-days: 2-4 (per Prof_Pax feasibility assessment)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.5 Resource Summary

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  RESOURCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total Hypotheses: 5
- Existence: 1 (H-E1)
- Mechanism: 4 (H-M1 to H-M4)
- Condition: 0

Verification Phases: 2
1. Foundation (H-E1): 2 weeks
2. Mechanisms (H-M1–H-M4): 4 weeks

Total Duration: 6 weeks
Critical Path: 6 weeks
Execution Mode: Sequential chain

Compute: Single GPU, ~2-4 GPU-days for encoder training
Data: Unterthiner CIFAR-10 zoo (~10K models, public)
      Schürholt PDFD zoo (cross-zoo validation, public)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

**Step 1**: Execute H-E1 — Data audit + all-encoder training on gap target (Week 1-2)
**Step 2**: Evaluate Gate 1 → If Spearman(gap) > 0.5 for ≥1 encoder, proceed
**Step 3**: Execute H-M1 — Compare equivariant vs. flat_MLP Spearman(gap) (Week 3-4, uses H-E1 results)
**Step 4**: Execute H-M2 — Compute Δ metric and partial correlation (Week 5, uses H-E1 results)
**Step 5**: Execute H-M3 — Confirm target-specificity + cross-zoo validation (Week 6)
**Step 6**: Execute H-M4 — NFT vs. DWS Spearman(gap) comparison (Week 7)
**Step 7**: Evaluate Gate 2 → MUST_WORK (H-E1 to H-M3) + SHOULD_WORK (H-M4) assessment
**Final**: Verification complete → Phase 2C → Phase 3 → Phase 4 → (Phase 5 skipped per config) → Phase 6

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: Permutation-equivariant weight encoders have a
disproportionately larger advantage over flat MLP on generalization
gap prediction than on test accuracy prediction, because gap's
distributed weight-space signal structure matches equivariant
encoders' orbit-averaging inductive bias.

Supporting Evidence:
1. PAC-Bayes flatness/margin measures (closely related to gap)
   are permutation-invariant — equivariant encoders share this
   inductive bias by construction (theoretical grounding).
2. Flat MLP on sorted weights can still learn spurious position-
   indexed features during training; equivariant encoders cannot
   by architectural constraint (mechanism distinction).
3. Phase 2A consensus: 5/6 personas support with high confidence
   (mean confidence 0.838 across all personas).

Strengths:
- Clear falsifiable predictions with pre-specified thresholds (Δ > 0.02)
- Dual-zoo design (Unterthiner + PDFD) for generalization test
- Mandatory pre-conditions (data audit, locked budget) prevent confounds
- Existing codebases confirm technical feasibility (2-4 GPU-days)

Expected Outcomes:
- P1: ≥2 equivariant encoders with Δ > 0.02 Spearman
- P2: NFT Spearman(gap) > DWS by ≥ 0.01
- P3: Partial Spearman (equivariant, gap | test_acc) > 0, p < 0.05

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): No differential improvement (Δ ≤ 0.02).
Equivariant encoders are simply better weight encoders in general;
gap is mostly −test_acc and any advantage is target-independent.

Counter-Arguments:
1. Train_acc ceiling: If Unterthiner zoo has train_acc ≈ 1.0,
   gap ≈ 1 − test_acc and the differential claim is trivially false.
2. Budget inequity: NFT complexity may require more trials; fixed
   budget artificially disadvantages cross-layer attention encoders.
3. Sorting invariance: Flat MLP on sorted weights is permutation-
   invariant at inference — the architectural distinction may not
   translate to a measurable representational difference.

Potential Failure Points:
- R1 (Critical): A1 fails → experiment uninformative
- R2 (High): A3 fails → NFT appears worse due to under-optimization
- R3 (High): Flat MLP sorting invariance adequate → Δ ≈ 0

Conditions Under Which H0 Would Be Supported:
- Data audit: Spearman(gap, −test_acc) ≥ 0.95 (gap = −test_acc)
- Δ ≤ 0 for all equivariant encoders despite adequate budget
- Partial Spearman ≤ 0 (equivariant prediction = pure test_acc prediction)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:

The hypothesis H-GenGapEquiv-v1 presents a well-specified testable
claim connecting architectural inductive bias to target-dependent
prediction performance. The antithesis raises three valid threats,
all of which have been incorporated into the verification design:
R1 → mandatory data audit (mandatory pre-condition); R2 → locked
50-trial budget with sensitivity analysis; R3 → theoretical
distinction between architectural and preprocessing invariance.

Resolution Path:

The verification plan addresses this dialectic through:
1. H-E1 (Foundation): Validates gap is predictable before testing
   differential effects; data audit built into verification protocol.
2. Sequential mechanism testing (H-M1 → H-M4): Tests causal chain
   step-by-step, allowing early detection of H0 support at each gate.
3. Gate conditions: MUST_WORK for H-E1 through H-M3 → if any fails,
   experiment halts and H0 is recorded as supported for that step.
4. Dual-zoo cross-validation (H-M3): Distinguishes zoo-specific from
   general effects, directly addressing R4.

Conditions for Thesis Support:
- Data audit: Spearman(gap, −test_acc) < 0.95 (A1 holds)
- H-E1: ≥1 encoder Spearman(gap) > 0.5
- H-M2: Δ > 0.02 for ≥2 equivariant encoders (P1 confirmed)
- H-M2: Partial Spearman > 0, p < 0.05 (P3 confirmed)

Conditions for Antithesis Support:
- Data audit: Spearman(gap, −test_acc) ≥ 0.95 (A1 fails)
- H-E1 fails: No encoder achieves Spearman(gap) > 0.5
- H-M2 fails: Δ ≤ 0.02 for all equivariant encoders

Nuanced Outcome Possibilities:
1. Full Support: H-E1 through H-M4 pass → Thesis validated with NFT hierarchy
2. Partial Support: H-E1 to H-M3 pass, H-M4 fails → Core claim holds, NFT advantage absent
3. Core Claim Only: H-M1 passes, H-M2/H-M3 marginal → Weak differential, scope carefully
4. No Support: H-E1 or H-M1 fails → Antithesis supported, route to Phase 0

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                 ROBUSTNESS ASSESSMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Gap independence | Gap has own signal (A1) | Gap ≈ −test_acc | Data audit gate (H-E1) |
| Existence | Gap is predictable | No learnable signal | H-E1 Spearman > 0.5 test |
| Mechanism | Equivariant Δ > 0.02 | Δ ≤ 0 (sorting sufficient) | H-M2 partial correlation |
| Target-specificity | Advantage gap > test_acc | General encoder superiority | Δ metric isolates effect |
| NFT hierarchy | NFT > DWS on gap | Budget/optimization artifact | Top-5 sensitivity analysis |
| Generalizability | Dual-zoo consistent | Zoo-specific artifact | H-M3 PDFD cross-validation |

Overall Robustness Score: HIGH
- 4 mandatory pre-conditions locked before experiment
- Dual-zoo design for generalization
- Partial correlation for mechanism isolation
- Bootstrap sensitivity for statistical robustness

Confidence in Verification Plan: 0.83
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** Equivariant weight encoders (DWS, NFT, GNN) show disproportionately larger Spearman improvement over flat MLP on generalization gap prediction vs. test accuracy prediction — ID: H-GenGapEquiv-v1, Confidence: 0.83

**Verification Structure:**
- Mode: Incremental (Phase 2A data loaded)
- Sub-Hypotheses: 5 total (H-E1: 1, H-M1–H-M4: 4)
- Phases: 2 phases over 6 weeks; Critical Gates: 2 decision points (Gate 1 at H-E1, Gate 2 at H-M3)

**Risk Assessment:** Medium-High
- Primary concerns: R1 (train_acc ceiling — data audit mandated), R2 (encoder budget inequity — 50-trial lock)

**Immediate Action:** Begin Phase 1 with H-E1 data audit on Unterthiner zoo, then all-encoder training

### 7.2 Conclusions

**Key Achievements:**
- 5 sub-hypotheses spanning existence + 4-step mechanism causal chain
- H0 addressed: No differential improvement (Δ ≤ 0.02)
- Risk mitigations built into verification protocols (data audit, locked budget, dual-zoo, sensitivity)

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Validate gap predictability + data audit (A1 check)
- Gate 1: MUST PASS — failure → STOP, reassess

**Phase 2: Core Mechanisms** (4 weeks)
- H-M1: Equivariant vs. flat_MLP Spearman(gap) comparison
- H-M2: Δ metric + partial correlation (P1 and P3)
- H-M3: Target-specificity + cross-zoo validation
- H-M4: NFT architectural hierarchy vs. DWS (P2)
- Gate 2: H-E1 through H-M3 MUST_WORK; H-M4 SHOULD_WORK

**Critical Decision Points:**

1. **Gate 1 (Foundation):** H-E1 Spearman(gap) > 0.5 for ≥1 encoder
   - FAIL → STOP, assess gap distribution; switch to PDFD if A1 triggered
   - PASS → Proceed to Phase 2

2. **Gate 2 (Mechanisms):** Δ > 0.02 for ≥2 of 3 equivariant encoders
   - H-M1 FAIL → EXPLORE (budget check), then PIVOT if persists
   - H-M2/H-M3 FAIL → Scope main claim carefully; document as null finding
   - H-M4 FAIL → Scope out NFT hierarchy claim; main claim unaffected

**Open Questions:**
- Does the differential equivariance advantage scale with zoo diversity (single vs. multi-architecture)?
- Can the PAC-Bayes-equivariance connection be made rigorous (theoretical companion paper)?
- Would per-encoder budget scaling (proportional to parameter count) change NFT's relative performance?

**Recommendations:**

1. **Immediate Actions:**
   - Download and verify Unterthiner zoo data; run A1 data audit first
   - Confirm NFT code compatibility with small CNN architecture family before committing

2. **Resource Allocation:**
   - Allocate 6 calendar weeks; expect 2-4 GPU-days of actual compute
   - Reserve 1-week buffer for potential PDFD zoo fallback (A1 failure scenario)

3. **Failure Management:**
   - Document all gate results explicitly (for benchmark metrics: failure_recording_rate)
   - Execute pre-specified PIVOT strategies; do not improvise mid-experiment

### 7.3 Appendices

**A. Phase 2A Reference**
- Source: `docs/youra_research/03_refinement.yaml` (ID: H-GenGapEquiv-v1)
- Decision: PROCEED_TO_2B (6/6 persona consensus, 5 strong support + 2 conditional)
- Key pre-conditions from Phase 2A: data audit mandatory, 50-trial budget pre-specified, partial correlation mandatory

**B. MCP Tool Usage Summary**
- Total MCP calls: 0 (ABLATION MODE — MCP unavailable; LLM-level scientific reasoning used)
- Per ablation protocol: ClearThought scientificmethod, collaborativereasoning, structuredargumentation replaced by expert LLM analysis
- Impact: All outputs generated through LLM reasoning; quality maintained

---

*Phase 2B Verification Plan — Complete*
*Next: Phase 2C Experiment Design for H-E1 (first READY hypothesis)*
