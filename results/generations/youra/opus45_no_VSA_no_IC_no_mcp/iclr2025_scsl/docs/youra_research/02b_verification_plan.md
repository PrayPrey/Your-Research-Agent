# Verification Plan: Temporal SGD Control of Spurious Feature Emergence

**Date:** 2026-08-28
**Hypothesis ID:** H-TemporalSGD-v1
**Confidence:** 0.80
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under standard supervised learning on datasets with spurious correlations (Waterbirds, CelebA), if we increase the learning rate or decrease the batch size, then peak spurious feature dominance will occur at later training epochs, because higher learning rates and smaller batches introduce optimization noise that disrupts the fast convergence to spurious feature reliance.

### 1.2 Alternative Hypothesis (H0)

There is no significant relationship between SGD hyperparameters (LR, batch size) and the epoch at which spurious feature reliance peaks. Variations in LR and batch size do not systematically affect worst-group accuracy beyond their general effects on training dynamics.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Waterbirds (standard) | Background-bird spurious correlation with ground-truth regions for attribution |
| **Model** | ResNet-50 | Standard architecture with well-understood gradient dynamics |

**Dataset Details:**
- Source: https://github.com/kohpangwei/group_DRO
- Path: data/waterbirds_v1.0

**Model Details:**
- Type: CNN
- Source: torchvision.models

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| ERM | ~75% worst-group accuracy | Waterbirds |
| JTT | ~86% worst-group accuracy | Waterbirds |
| Group DRO | ~91% worst-group accuracy | Waterbirds |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | GradCAM reliably separates spurious vs. core feature attribution | GradCAM established; Waterbirds/CelebA have ground-truth regions | Spurious dominance epoch measurement becomes unreliable |
| A2 | Spurious and core features compete for gradient signal | Simplicity bias implies features learned in order of gradient magnitude | Gradient competition mechanism invalid |
| A3 | Higher LR / smaller batch increases optimization noise | Well-established in SGD theory | Core mechanism of intervention fails |
| A4 | Delayed spurious dominance causally improves worst-group accuracy | Proposed - to be tested | Practical relevance diminishes |
| A5 | Effects transfer across datasets with similar spurious structure | Both Waterbirds and CelebA have background/foreground patterns | Method may be dataset-specific |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First temporal characterization of spurious feature emergence with optimization control

**Key Innovation:** Optimization-only, single-stage robustification via hyperparameter control (no group labels, no two-stage training)

**Differentiation:**
- Unlike Shah et al. (simplicity bias): We measure temporal dynamics across hyperparameters
- Unlike JTT: Single-stage vs. two-stage; hyperparameter control vs. example reweighting
- Unlike SAM: Focus on spurious features specifically, not general generalization

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | NOT_STARTED |
| H-M2 | MECHANISM | MUST_WORK | H-E1, H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | SHOULD_WORK | H-M2 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

#### H-E1: Spurious Feature Temporal Dominance Existence

**Type:** EXISTENCE
**Statement:** Under standard ERM training on Waterbirds dataset, if we measure GradCAM attribution over training epochs, then spurious features (background) will dominate core features (bird) before epoch 10, because spurious correlations provide stronger gradient signal early in training.

**Variables:**
- IV: Training epoch (1-50)
- DV: Spurious/Core attribution ratio (GradCAM)
- CV: Architecture (ResNet-50), Dataset (Waterbirds), LR (0.01), Batch (128)

**Success Criteria:**
- Spurious dominance epoch < 10 (mean across seeds)
- Attribution ratio > 1.0 at dominance epoch

**Gate:**
- Type: MUST_WORK
- If Fail: ABORT (foundational assumption invalid)

**Prerequisites:** None

**Verification Protocol:**
1. Train ResNet-50 on Waterbirds with default hyperparameters (5 seeds).
2. Compute GradCAM attribution on spurious/core regions every epoch.
3. Identify epoch where spurious attribution first exceeds core (ratio > 1).
4. Verify dominance epoch < 10 across all seeds.

---

#### H-M1: Gradient Signal Competition

**Type:** MECHANISM
**Statement:** Under ERM training on spurious correlation datasets, if we measure gradient norms for spurious vs. core features, then spurious features will show higher gradient norms in early epochs, because spurious correlations maximize training-set likelihood more directly.

**Variables:**
- IV: Feature type (spurious/core)
- DV: Gradient norm magnitude
- CV: Architecture, Dataset, Epoch range (1-10)

**Success Criteria:**
- Spurious gradient norm > core gradient norm (ratio > 1.5)
- Ratio decreases over epochs

**Gate:**
- Type: MUST_WORK
- If Fail: PIVOT (mechanism description, not effect)

**Prerequisites:** H-E1

**Verification Protocol:**
1. Train model, capture gradients for spurious/core feature channels.
2. Compute gradient norm for each feature type per epoch.
3. Compare spurious vs. core gradient norm ratio.
4. Verify ratio > 1.5 in epochs 1-10.

---

#### H-M2: Optimization Noise Disruption

**Type:** MECHANISM
**Statement:** Under varied SGD hyperparameters on Waterbirds, if we increase learning rate 10x or decrease batch size 4x, then peak spurious dominance epoch will shift later by ≥5 epochs, because optimization noise disrupts spurious gradient advantage.

**Variables:**
- IV: LR (0.001, 0.01, 0.1), Batch size (32, 128, 512)
- DV: Peak spurious dominance epoch
- CV: Architecture, Dataset, Total epochs (50)

**Success Criteria:**
- High-LR dominance epoch ≥ low-LR + 5 epochs
- Smaller batch → later dominance

**Gate:**
- Type: MUST_WORK
- If Fail: ABORT (intervention ineffective)

**Prerequisites:** H-E1, H-M1

**Verification Protocol:**
1. Run 9 configurations (3 LR × 3 batch) × 5 seeds = 45 runs.
2. Identify peak dominance epoch for each run.
3. Compare high-LR vs. low-LR dominance epochs.
4. Verify shift ≥5 epochs with p < 0.05 (paired t-test).

---

#### H-M3: Timing-Accuracy Correlation

**Type:** MECHANISM
**Statement:** Under varied hyperparameter configurations, if peak spurious dominance occurs later, then final worst-group accuracy will be higher, because delayed dominance allows more core feature learning time.

**Variables:**
- IV: Peak spurious dominance epoch
- DV: Final worst-group accuracy
- CV: Architecture, Dataset

**Success Criteria:**
- Spearman r < -0.5 (negative correlation)
- Effect visible on both Waterbirds and CelebA

**Gate:**
- Type: SHOULD_WORK
- If Fail: PIVOT (timing control works but practical impact unclear)

**Prerequisites:** H-M2

**Verification Protocol:**
1. Use 45 runs from H-M2 experiment.
2. Compute Spearman correlation between dominance epoch and worst-group accuracy.
3. Verify r < -0.5 with p < 0.05.

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Dominance < epoch 10 | ABORT all |
| H-M1 | MUST_WORK | Gradient ratio > 1.5 | ABORT (mechanism invalid) |
| H-M2 | MUST_WORK | Epoch shift ≥ 5 | ABORT (intervention fails) |
| H-M3 | SHOULD_WORK | r < -0.5 | Document limitation |

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
| R1 | GradCAM attribution unreliable | A1 | HIGH | H-E1, H-M1 | Dual methods: GradCAM + Integrated Gradients |
| R2 | Gradient competition not detectable | A2 | MEDIUM | H-M1 | Direct measurement, fallback to empirical only |
| R3 | LR/batch noise effect absent | A3 | HIGH | H-M2 | Test extreme ranges (0.001 vs 0.1) |
| R4 | Timing-accuracy correlation weak | A4 | MEDIUM | H-M3 | Document as limitation if r > -0.3 |
| R5 | Effects don't transfer | A5 | MEDIUM | All | Replication on CelebA required |

### 4.2 Mitigation Strategies

**R1 (HIGH):** Use ground-truth region masks; cross-validate with Integrated Gradients
**R2 (MEDIUM):** Sample gradients at fine intervals; accept empirical timing without mechanism
**R3 (HIGH):** Use 10x LR range; if same dominance epoch (±2), ABORT
**R4 (MEDIUM):** Ensure 45 runs for statistical power; report timing control without accuracy claims if weak
**R5 (MEDIUM):** Verify CelebA has similar spurious structure; limit claims if transfer fails

---

## 5. Dependency Graph & Timeline

### 5.1 DAG Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    ┌─────────────────────────────────────┐
    │  H-E1: Spurious Dominance Exists    │
    │  Gate: MUST_WORK                    │
    │  Prerequisites: None                │
    └─────────────────────────────────────┘
                      │
                      ▼
[Level 1 - Mechanism Step 1]
    ┌─────────────────────────────────────┐
    │  H-M1: Gradient Signal Competition  │
    │  Gate: MUST_WORK                    │
    │  Prerequisites: H-E1                │
    └─────────────────────────────────────┘
                      │
                      ▼
[Level 2 - Mechanism Step 2]
    ┌─────────────────────────────────────┐
    │  H-M2: Optimization Noise Disrupts  │
    │  Gate: MUST_WORK                    │
    │  Prerequisites: H-E1, H-M1          │
    └─────────────────────────────────────┘
                      │
                      ▼
[Level 3 - Mechanism Step 3]
    ┌─────────────────────────────────────┐
    │  H-M3: Timing-Accuracy Correlation  │
    │  Gate: SHOULD_WORK                  │
    │  Prerequisites: H-M2                │
    └─────────────────────────────────────┘

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Total Depth: 4 levels
═══════════════════════════════════════════════════════════
```

### 5.2 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis      │ W1-2     │ W3-4     │ W5       │ W6       │
──────────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 1: Foundation
  H-E1                │ ████████ │          │          │          │
  [Gate 1]            │        ◆ │          │          │          │
──────────────────────┼──────────┼──────────┼──────────┼──────────┤
PHASE 2: Mechanisms
  H-M1                │          │ ████████ │          │          │
  H-M2                │          │          │ ████████ │          │
  H-M3                │          │          │          │ ████████ │
  [Gate 2]            │          │          │          │        ◆ │
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Under standard supervised learning on datasets with spurious correlations, if we increase the learning rate or decrease the batch size, then peak spurious feature dominance will occur at later training epochs.

**Supporting Evidence:**
1. Simplicity bias literature establishes spurious features learn faster (Shah et al., 2020)
2. SGD noise theory supports LR/batch effects on optimization dynamics
3. Three testable predictions with quantitative thresholds

**Strengths:**
- Builds on established simplicity bias theory
- Clear 3-step causal mechanism with falsifiers
- Practical intervention requiring no group labels

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant relationship between SGD hyperparameters (LR, batch size) and the epoch at which spurious feature reliance peaks.

**Counter-Arguments:**
1. LR/batch effects may be confounded with convergence speed
2. GradCAM attribution may be too noisy to detect timing shifts
3. Gradient competition may be approximation, not actual mechanism

**Conditions Under Which H0 Would Be Supported:**
- High-LR configs show ≤2 epoch shift (P1 falsification)
- Timing-accuracy correlation r ≥ -0.3 (P2 falsification)

### 6.3 Synthesis

The verification plan addresses the thesis-antithesis dialectic through:

1. **Foundation verification (H-E1):** Establishes existence before testing mechanism
2. **Sequential mechanism testing (H-M1-3):** Tests causal chain step-by-step with falsifiers
3. **Gate conditions:** Allow early termination if H0 is supported

| Outcome | Gate Result | Interpretation |
|---------|-------------|----------------|
| Full Support | All pass | Temporal SGD control validated |
| Partial Support | H-M3 fails | Timing control works, practical impact unclear |
| No Support | H-E1 or H-M1 fails | Mechanism invalid, H0 supported |

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | Spurious dominance measurable | GradCAM noise | Dual attribution methods |
| Mechanism | Gradient competition | Alternative explanations | Step-by-step H-M tests |
| Intervention | LR/batch controls timing | Confounded with speed | Matched control design |
| Impact | Improves worst-group accuracy | Marginal effect | Effect size criteria |

**Overall Robustness:** HIGH
**Confidence in Verification Plan:** 0.80

---

## 7. Executive Summary

**Main Hypothesis:** Temporal SGD Control of Spurious Feature Emergence
- ID: H-TemporalSGD-v1, Confidence: 0.80

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 4 total (H-E: 1, H-M: 3)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points

**Risk Assessment:** Medium
- Primary concerns: GradCAM reliability (R1), LR noise effect absence (R3)

**Immediate Action:** Begin Phase 2C with H-E1 (spurious dominance existence)

---

## Appendices

**A. Phase 2A Reference:** 03_refinement.yaml (H-TemporalSGD-v1)
**B. Total Experimental Runs:** 45 (9 configs × 5 seeds)
**C. Established Facts (BUILD_ON):** Simplicity bias (Shah et al., 2020), SAM flat minima (Foret et al., 2021)
