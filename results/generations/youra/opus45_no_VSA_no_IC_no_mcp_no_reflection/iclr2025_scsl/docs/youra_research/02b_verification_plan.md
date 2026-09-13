# Verification Plan: Progressive Gradient Orthogonalization (PGO)

**Date:** 2026-08-29
**Hypothesis ID:** H-PGO-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under standard supervised classification with spurious correlations, if we progressively project training gradients orthogonal to the cumulative "easy gradient" subspace, then worst-group accuracy improves relative to ERM, because the model is forced to learn features that generalize beyond majority-group shortcuts.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in worst-group accuracy between Progressive Gradient Orthogonalization (PGO) and standard ERM training.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Waterbirds (standard) | Established benchmark with 95% background spurious correlation |
| **Model** | ResNet-50 | Standard architecture for spurious correlation research |

**Dataset Details:**
- Source: https://github.com/kohpangwei/group_DRO
- Path: datasets/waterbirds/

**Model Details:**
- Type: CNN classifier
- Source: torchvision pretrained

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| ERM | ~60% worst-group accuracy | Waterbirds |
| JTT | ~86% worst-group accuracy | Waterbirds |
| DFR | ~90% worst-group accuracy | Waterbirds |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Early gradient subspace is primarily spurious | Simplicity bias predicts spurious features learned first | Orthogonalization would harm core feature learning |
| A2 | Low-rank SVD captures spurious directions | Spurious features are 'simple' — low-dimensional subspace | Subspace S would miss spurious directions |
| A3 | Core and spurious gradients are separable | Distributed representations still have directional structure | Orthogonalization would be impossible |
| A4 | Progressive orthogonalization stable | Similar to gradient penalty methods that remain stable | Training would diverge |
| A5 | Benchmarks have sufficient spurious correlation | Established benchmarks with known spurious features | Would need different benchmarks |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** Progressive gradient orthogonalization as intervention mechanism

**Key Innovation:** First method to exploit training dynamics through continuous gradient subspace projection. Unlike JTT (sample identification) or DFR (post-training), PGO directly engineers the training trajectory in a single run.

**Differentiation:**
- vs JTT: PGO operates in gradient space, not sample space; single run vs two runs
- vs DFR: PGO intervenes during training, not post-training; no held-out groups needed
- vs Group DRO: PGO requires no group annotations during training

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | Mechanism | MUST_WORK | H-M1 | NOT_STARTED |
| H-M3 | Mechanism | MUST_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

#### H-E1: Gradient Subspace Captures Spurious Features

**Type:** EXISTENCE
**Statement:** Under standard supervised learning with spurious correlations, if we accumulate early training gradients into subspace S via incremental SVD, then S primarily captures spurious feature directions, because simplicity bias causes spurious features to dominate early learning.

**Variables:**
- IV: Training epoch (early vs late)
- DV: Spurious feature alignment of accumulated gradient subspace
- CV: ResNet-50, lr=0.001, batch=64, Waterbirds dataset

**Success Criteria:**
- Primary: S alignment with spurious features > 70% at early epochs
- Secondary: S alignment with core features < 30% at early epochs

**Gate:**
- Type: MUST_WORK
- If Fail: STOP - core assumption invalid

**Prerequisites:** None

**Verification Protocol:**
1. Train ERM baseline and log gradients at each epoch
2. Compute incremental SVD of accumulated gradients → subspace S
3. Measure alignment of S with spurious feature directions (background)
4. Compare alignment at epoch 5 vs epoch 45

---

#### H-M1: Early Training Follows Easy Gradients

**Type:** MECHANISM
**Statement:** Under standard ERM training, if spurious features are simpler than core features, then early epoch gradients point toward spurious feature directions, because simplicity bias drives network toward low-complexity solutions first.

**Variables:**
- IV: Training epoch
- DV: Gradient alignment with spurious vs core features
- CV: Model architecture, learning rate, dataset

**Success Criteria:**
- Primary: Early gradients (epoch 1-10) show higher spurious alignment than core
- Secondary: Alignment ratio flips or equalizes by late epochs

**Gate:**
- Type: MUST_WORK
- If Fail: PIVOT to alternative mechanism

**Prerequisites:** H-E1

**Verification Protocol:**
1. Train ResNet-50 on Waterbirds with ERM
2. Log gradient directions at epochs 1, 5, 10, 25, 50
3. Compute gradient alignment with spurious (background) vs core (bird) directions
4. Plot alignment ratio across training

---

#### H-M2: PGO Accumulates Spurious Directions into Subspace S

**Type:** MECHANISM
**Statement:** Under PGO training, if we apply incremental SVD to accumulated early gradients, then subspace S captures the spurious-dominant gradient directions, because the SVD captures the principal components of the gradient distribution.

**Variables:**
- IV: Subspace rank k (10, 25, 50)
- DV: Explained variance of spurious gradient directions
- CV: SVD algorithm, accumulation window

**Success Criteria:**
- Primary: Subspace S explains >60% variance of spurious gradient directions
- Secondary: Subspace condition number remains stable (< 1000)

**Gate:**
- Type: MUST_WORK
- If Fail: EXPLORE alternative accumulation methods

**Prerequisites:** H-M1

**Verification Protocol:**
1. Implement incremental SVD for gradient accumulation
2. Accumulate gradients during epochs 1-10
3. Compute SVD and extract top-k components → subspace S
4. Measure explained variance ratio for spurious vs core directions

---

#### H-M3: Orthogonalized Gradients Find Core Features

**Type:** MECHANISM
**Statement:** Under PGO training, if later gradients are projected orthogonal to subspace S, then the model learns core features that generalize to minority groups, because orthogonalization blocks spurious reinforcement and forces exploration of alternative directions.

**Variables:**
- IV: Orthogonalization schedule (none, linear, step)
- DV: Worst-group test accuracy
- CV: Model, dataset, learning rate, subspace rank

**Success Criteria:**
- Primary: PGO worst-group accuracy ≥ ERM + 5% (p < 0.05, 5 seeds)
- Secondary: Core feature probe accuracy improves over ERM

**Gate:**
- Type: MUST_WORK
- If Fail: EXPLORE alternative orthogonalization schedules

**Prerequisites:** H-M2

**Verification Protocol:**
1. Implement gradient projection: g' = g - proj_S(g)
2. Apply progressive orthogonalization (linear schedule, α: 0 → α_max)
3. Train ResNet-50 on Waterbirds with PGO
4. Evaluate worst-group accuracy on test set
5. Compare against ERM baseline

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3 → [Phase 5 Baseline Comparison]
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Spurious alignment > 70% | STOP |
| H-M1 | MUST_WORK | Early spurious > core alignment | STOP |
| H-M2 | MUST_WORK | Variance explained > 60% | STOP |
| H-M3 | MUST_WORK | WGA ≥ ERM + 5% | STOP |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Foundation | H-E1 | 2 weeks |
| Mechanisms | H-M1, H-M2, H-M3 | 4 weeks |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Risk Summary

| ID | Risk | Source | Severity | Affected | Mitigation |
|----|------|--------|----------|----------|------------|
| R1 | Core features in early subspace | A1 | Critical | H-E1, H-M1 | Delay orthogonalization start |
| R2 | SVD misses spurious | A2 | High | H-M2 | Ablate rank k |
| R3 | Gradients not separable | A3 | Critical | All H-M | Use strong-separation datasets |
| R4 | Training instability | A4 | High | H-M3 | Linear schedule + clip α |
| R5 | Weak spurious correlation | A5 | Medium | All | Use Waterbirds (95% correlation) |

### 4.2 Mitigation Strategies

**R1 (Critical): Early subspace contains core features**
- Detection: Compute core feature alignment of subspace S at epoch 10
- Prevention: Start orthogonalization later (epoch 15+)
- Response: PIVOT to selective orthogonalization using loss curvature

**R2 (High): SVD misses spurious directions**
- Detection: Track explained variance ratio during training
- Prevention: Ablate rank k (10, 25, 50)
- Response: EXPLORE incremental PCA or momentum-based accumulation

**R3 (Critical): Gradients not separable**
- Detection: Measure gradient overlap between core and spurious directions
- Prevention: Use datasets with known strong separation
- Response: ABORT mechanism hypothesis, PIVOT to alternative

**R4 (High): Training instability**
- Detection: Monitor loss oscillation and gradient norm spikes
- Prevention: Use linear schedule, clip orthogonalization strength
- Response: REDUCE α_max, ADD warmup period

**R5 (Medium): Insufficient spurious correlation**
- Detection: Measure ERM worst-group accuracy (should be low ~60%)
- Prevention: Use established benchmarks (Waterbirds, CelebA)
- Response: SELECT different benchmark

---

## 5. Dependency Graph & Timeline

### 5.1 DAG Visualization

```
═══════════════════════════════════════════════════════════════
  DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════════

[Level 0 - Foundation]
         ┌─────────────────────────────────────┐
         │  H-E1: Subspace captures spurious   │
         │  Gate: MUST_WORK                    │
         └─────────────────────────────────────┘
                          │
                          ▼
[Level 1 - Mechanism Step 1]
         ┌─────────────────────────────────────┐
         │  H-M1: Early gradients → spurious   │
         │  Gate: MUST_WORK                    │
         └─────────────────────────────────────┘
                          │
                          ▼
[Level 2 - Mechanism Step 2]
         ┌─────────────────────────────────────┐
         │  H-M2: PGO accumulates into S       │
         │  Gate: MUST_WORK                    │
         └─────────────────────────────────────┘
                          │
                          ▼
[Level 3 - Mechanism Step 3]
         ┌─────────────────────────────────────┐
         │  H-M3: Orthogonalization → core     │
         │  Gate: MUST_WORK                    │
         └─────────────────────────────────────┘
                          │
                          ▼
                    [COMPLETE]
                          │
                          ▼
               ┌──────────────────┐
               │   Phase 5        │
               │ Baseline Compare │
               └──────────────────┘

═══════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 (all sequential)
═══════════════════════════════════════════════════════════════
```

### 5.2 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════════
  VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis      │ W1-2     │ W3-4     │ W5       │ W6       │
──────────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 1: Foundation   │          │          │          │          │
  H-E1 (Existence)    │ ████████ │          │          │          │
  [Gate 1]            │        ◆ │          │          │          │
──────────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 2: Mechanisms   │          │          │          │          │
  H-M1 (Early grads)  │          │ ████████ │          │          │
  H-M2 (Accumulate)   │          │          │ ████     │          │
  H-M3 (Orthogonalize)│          │          │          │ ████     │
  [Gate 2]            │          │          │          │        ◆ │
═══════════════════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════════════════
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Progressive gradient orthogonalization improves worst-group accuracy by forcing networks to learn core features.

**Supporting Evidence:**
1. Simplicity bias causes spurious features to dominate early learning (Shah et al., 2020)
2. Early gradient subspace should capture these spurious directions (A1-A3)
3. Orthogonalization mathematically blocks reinforcement of accumulated directions

**Strengths:**
- Builds on established simplicity bias theory
- Clear 3-step causal mechanism with testable links
- Single-run method requiring no group annotations

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in worst-group accuracy between PGO and ERM.

**Counter-Arguments:**
1. Early gradient subspace may contain essential core feature directions (Risk R1)
2. Low-rank SVD may miss critical spurious directions (Risk R2)
3. Core and spurious gradients may be entangled (Risk R3)

**Potential Failure Points:**
- Orthogonalization harms core feature learning if A1 violated
- Training becomes unstable with progressive projection (Risk R4)
- Effect size may be negligible despite statistical significance

### 6.3 Synthesis

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Confirms subspace captures spurious before intervening
2. **Sequential mechanism testing (H-M1-M3):** Tests each causal link independently
3. **Gate conditions:** Early failure detection prevents wasted effort on invalid premises

**Nuanced Outcome Possibilities:**
1. **Full Support:** All pass → PGO validated as novel robustification method
2. **Partial Support:** Some H-M fail → Mechanism refinement needed
3. **No Support:** Foundation fails → Hypothesis rejected, alternative approach needed

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Subspace S captures spurious | May capture core too | H-E1: measure alignment |
| Mechanism | Orthogonalization finds core | May harm learning | H-M1-M3: sequential test |
| Stability | Progressive schedule stable | May diverge | Linear schedule + clip α |
| Performance | Outperforms ERM | Marginal/null effect | Phase 5 comparison |

**Overall Robustness Score:** Medium-High
**Confidence in Verification Plan:** 0.75

---

## 7. Executive Summary

**Main Hypothesis:** Progressive gradient orthogonalization improves worst-group accuracy
- ID: H-PGO-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 4 total (H-E: 1, H-M: 3)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points (all MUST_WORK)

**Risk Assessment:** Medium
- Primary concerns: R1 (core features in early subspace), R3 (gradient separability)

**Immediate Action:** Begin Phase 2C experiment design for H-E1

---

## Appendices

### A. Phase 2A Reference
- Source: 03_refinement.yaml (ID: H-PGO-v1)
- Schema: v10.0.0

### B. Established Facts (BUILD_ON - Not Re-verified)
1. Simplicity bias causes spurious features to be learned before core features
2. Last-layer retraining can recover core features (DFR)
3. Two-stage training improves worst-group accuracy (JTT)

### C. Open Questions
- Optimal rank k for different datasets
- Interaction between orthogonalization strength and learning rate
- Generalization to other architectures (ViT, etc.)
