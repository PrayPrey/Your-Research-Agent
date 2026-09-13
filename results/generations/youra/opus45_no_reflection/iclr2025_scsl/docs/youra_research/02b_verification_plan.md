# Verification Plan: Emergence Uniformity Regularization (EUR)

**Date:** 2026-08-18
**Hypothesis ID:** H-EUR-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under the Waterbirds/CelebA/ColoredMNIST benchmarks where spurious correlations cause poor worst-group performance, if we identify features by their emergence uniformity (low variance in probe learning rates across sample subsets, CV < 0.15) and apply gradient regularization proportional to uniformity, then worst-group accuracy improves by ≥5 percentage points over ERM, because uniform emergence indicates the feature is spuriously correlated with labels rather than discriminative.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in worst-group accuracy between EUR (Emergence Uniformity Regularization) and standard ERM training on spurious correlation benchmarks.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Waterbirds (standard) | Standard spurious correlation benchmark with known 95% background-label correlation |
| **Model** | ResNet-50 | Standard architecture used in all reference papers (JTT, Group DRO, LfF) |

**Dataset Details:**
- Source: https://github.com/kohpangwei/group_DRO
- Path: waterbird_complete95_forest2water2/

**Model Details:**
- Type: CNN
- Source: torchvision.models.resnet50(pretrained=True)

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| ERM | ~70% worst-group accuracy | Waterbirds |
| JTT | ~86% worst-group accuracy | Waterbirds |
| Group DRO (oracle) | ~91% worst-group accuracy | Waterbirds |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Spurious features emerge uniformly across training samples; core features emerge differentially across implicit groups | Implied by simplicity bias (spurious = simple = learned quickly by all samples) | CV cannot distinguish feature types; method fails |
| A2 | Linear probes on pretrained features capture relevant feature emergence patterns | Linear probes are standard for measuring representation quality | Nonlinear learning phases may be missed; alternative probing needed |
| A3 | CV threshold (0.15) can distinguish spurious from core features with reasonable accuracy | Proposed based on discussion; requires empirical validation | Threshold needs recalibration or adaptive selection |
| A4 | Gradient regularization in probe directions effectively suppresses feature learning | Spectral regularization literature; adversarial direction regularization | Alternative intervention mechanisms needed |
| A5 | CLIP features encode relevant visual concepts for Waterbirds/CelebA/ColoredMNIST | CLIP trained on diverse web images; benchmarks use common visual concepts | Need alternative feature extractors (DINOv2, ImageNet-pretrained) |

### 1.6 Research Gap & Novelty

This work introduces emergence uniformity as a novel signal for spuriousness detection. Unlike prior work that uses absolute timing (what emerges first), we use variance in emergence rates across sample subsets (what emerges uniformly). Key innovation: single-run dynamic gradient regularization based on CV of probe trajectories. No two-stage training required; intervention is continuous during training.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | EXISTENCE | MUST_WORK | None | Pending |
| H-M1 | MECHANISM | MUST_WORK | H-E1 | Pending |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | Pending |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | Pending |

---

### 2.2 Hypothesis Specifications

#### H-E1: CV Distinguishes Spurious from Core Features

**Type:** EXISTENCE
**Statement:** Under Waterbirds/CelebA/ColoredMNIST benchmarks, if we compute CV of probe accuracy trajectories across 5 random 20% sample subsets, then spurious features show CV < 0.15 and core features show CV > 0.2, because spurious features are learned uniformly due to simplicity bias while core features are learned differentially across implicit groups.

**Rationale:** This validates the foundational claim that emergence uniformity distinguishes feature types. Without this, the entire EUR mechanism lacks a reliable detection signal. The 0.15 threshold is proposed but requires empirical validation.

**Variables:**
- IV: CV threshold (0.1, 0.15, 0.2)
- DV: Feature classification AUC
- CV: Dataset, CLIP ViT-B/16, probe architecture

**Verification Protocol:**
1. Extract CLIP features for all Waterbirds training samples.
2. Train linear probes at 10 epoch checkpoints on multiple visual concepts.
3. Compute accuracy improvement rates on 5 random 20% subsets per feature.
4. Calculate CV for each feature and classify using threshold.
5. Compute AUC against ground truth (background=spurious, bird=core).

**Success Criteria:**
- Primary: Feature classification AUC ≥ 0.75
- Secondary: CV distributions for spurious vs core features are separable

**Failure Response:** IF fails: PIVOT to alternative detection metrics (loss trajectory variance, gradient magnitude)

**Dependencies:** None (foundation hypothesis)
**Source:** Phase 2A SH1, Prediction P1

---

#### H-M1: Probe-Based Detection Captures Emergence Dynamics

**Type:** MECHANISM
**Statement:** Under standard training with probe checkpoints every 5 epochs, if we train linear probes on CLIP features at each checkpoint, then probe accuracy trajectories reflect feature learning order and stability, because probes measure representation quality at each training stage.

**Rationale:** This validates the detection mechanism. Probes must reliably track feature emergence for CV computation to be meaningful. If probe trajectories are noisy or non-monotonic, the measurement method is invalid.

**Variables:**
- IV: Probe checkpoint interval (5 epochs)
- DV: Probe accuracy trajectory monotonicity
- CV: CLIP ViT-B/16, linear probe architecture

**Verification Protocol:**
1. Train ResNet-50 on Waterbirds for 50 epochs with checkpoints every 5 epochs.
2. At each checkpoint, train linear probes on CLIP features for known visual concepts.
3. Plot probe accuracy trajectories for spurious (background) and core (bird) features.
4. Verify trajectories are monotonically increasing with >0.8 Spearman correlation.

**Success Criteria:**
- Primary: Probe accuracies increase monotonically (ρ > 0.8)
- Secondary: Spurious feature probes reach high accuracy earlier than core feature probes

**Failure Response:** IF fails: EXPLORE alternative probe intervals or nonlinear probes

**Dependencies:** H-E1
**Source:** Phase 2A Causal Step 1

---

#### H-M2: CV Threshold Classifies Features Reliably

**Type:** MECHANISM
**Statement:** Under computed CV values from H-M1 probe trajectories, if we apply threshold CV < 0.15 for spurious classification, then at least 70% of known spurious features are correctly identified with <30% false positive rate, because uniform emergence is a distinguishing characteristic of simplicity-biased features.

**Rationale:** This validates the classification step. The threshold must generalize across features within a dataset. If CV distributions overlap completely, alternative thresholds or adaptive selection are needed.

**Variables:**
- IV: CV threshold value (0.1, 0.15, 0.2)
- DV: Spurious feature recall and precision
- CV: Dataset, probe trajectories from H-M1

**Verification Protocol:**
1. Collect CV values for all measured features from H-M1.
2. Apply CV < 0.15 threshold to classify features as spurious.
3. Compare against ground truth labels (known spurious/core features).
4. Compute precision, recall, and F1 for spurious feature classification.

**Success Criteria:**
- Primary: Spurious feature recall ≥ 0.70, precision ≥ 0.70
- Secondary: F1 score ≥ 0.70 across all three datasets

**Failure Response:** IF fails: PIVOT to adaptive threshold selection or per-dataset calibration

**Dependencies:** H-M1
**Source:** Phase 2A Causal Step 2

---

#### H-M3: Gradient Regularization Improves Worst-Group Accuracy

**Type:** MECHANISM
**Statement:** Under classification from H-M2 identifying low-CV features as spurious, if we apply gradient penalty λ*(grad·probe_direction)² to low-CV feature directions during training, then worst-group accuracy improves by ≥5 pp over ERM on Waterbirds because the network is forced to rely on high-CV discriminative features.

**Rationale:** This validates the intervention mechanism. The gradient regularization must effectively suppress spurious feature learning without destroying overall performance. This is the core test of EUR's effectiveness.

**Variables:**
- IV: Regularization strength λ (0, 0.01, 0.1, 1.0)
- DV: Worst-group accuracy, average accuracy
- CV: ResNet-50, SGD optimizer, standard train/val/test splits

**Verification Protocol:**
1. Train ResNet-50 with EUR: probe detection + CV classification + gradient regularization.
2. Sweep λ ∈ {0.01, 0.1, 1.0} with CV threshold = 0.15.
3. Evaluate worst-group accuracy on Waterbirds test set (full 5794 samples).
4. Compare against ERM baseline trained with identical settings.
5. Run 5 seeds and report mean ± std.

**Success Criteria:**
- Primary: Worst-group accuracy ≥ ERM + 5 pp on Waterbirds
- Secondary: Average accuracy drop ≤ 2 pp

**Failure Response:** IF fails: EXPLORE λ calibration strategies or alternative regularization forms

**Dependencies:** H-M2
**Source:** Phase 2A Causal Step 3, Prediction P1

<!--
Each hypothesis follows this format:

#### {H-ID}: {Title}

**Type:** {EXISTENCE|MECHANISM|CONDITION|COMPARISON}
**Statement:** {Full Under-If-Then-Because statement}

**Variables:**
- IV: {independent variable}
- DV: {dependent variable}
- CV: {controlled variables}

**Success Criteria:**
- {quantitative threshold 1}
- {quantitative threshold 2}

**Gate:**
- Type: {MUST_WORK|SHOULD_WORK|DETERMINES_SUCCESS}
- If Fail: {consequence}

**Prerequisites:** {list or "None"}

**Verification Protocol:** (100-150 words)
{step-by-step protocol}

---
-->

---

## 3. Execution

### 3.1 Dependency Chain
```
H-E1 → H-M1 → H-M2 → H-M3
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | AUC ≥ 0.75 | STOP: Reassess CV metric |
| H-M1 | MUST_WORK | Trajectory ρ > 0.8 | STOP: Detection invalid |
| H-M2 | SHOULD_WORK | F1 ≥ 0.70 | PIVOT: Adaptive threshold |
| H-M3 | MUST_WORK | WGA ≥ ERM + 5pp | PIVOT: Alt regularization |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Foundation | H-E1 | 2 weeks |
| Mechanisms | H-M1, H-M2, H-M3 | 4 weeks |

**Total Duration:** 6 weeks

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

| ID | Risk | Source Assumption | Severity | Likelihood |
|----|------|-------------------|----------|------------|
| R1 | CV cannot distinguish spurious from core features | A1: Spurious features emerge uniformly | Critical | Medium |
| R2 | Linear probes miss nonlinear learning dynamics | A2: Linear probes capture emergence patterns | High | Low |
| R3 | CV threshold (0.15) fails to generalize | A3: CV threshold separates feature types | High | Medium |
| R4 | Gradient regularization ineffective | A4: Regularization suppresses feature learning | High | Low |
| R5 | CLIP encodes dataset biases | A5: CLIP features encode relevant concepts | Medium | Medium |

### 4.2 Risk-Hypothesis Mapping

| Risk | Affected Hypotheses | Impact |
|------|---------------------|--------|
| R1 | H-E1, H-M1, H-M2 | Foundation failure - invalidates detection mechanism |
| R2 | H-M1 | Detection mechanism incomplete |
| R3 | H-M2 | Classification unreliable across datasets |
| R4 | H-M3 | Intervention mechanism fails |
| R5 | All (H-E1, H-M1-3) | Feature extraction corrupted |

### 4.3 Mitigation Strategies

**R1: CV Distribution Overlap (Critical)**
- Prevention: Validate on dataset with known ground truth labels
- Detection: Compute CV distribution separation metrics (KL divergence)
- Response:
  - PIVOT: Use alternative metrics (loss trajectory variance, gradient magnitude patterns)
  - SCOPE: Focus on features with extreme CV values only
  - ABORT: If CV distributions identical after multiple threshold adjustments

**R2: Linear Probe Limitation (High)**
- Prevention: Compare linear vs MLP probe trajectories on subset
- Detection: Check for non-monotonic accuracy trajectories
- Response:
  - PIVOT: Use 2-layer MLP probes instead of linear
  - SCOPE: Focus on late-training dynamics where linear approximation holds

**R3: Threshold Generalization (High)**
- Prevention: Ablate CV threshold {0.1, 0.15, 0.2} on all three datasets
- Detection: Track per-dataset optimal threshold variance
- Response:
  - PIVOT: Adaptive threshold selection per dataset
  - SCOPE: Use relative ranking instead of absolute threshold

**R4: Regularization Ineffective (High)**
- Prevention: Validate gradient penalty reduces low-CV feature activations
- Detection: Monitor feature activation patterns during training
- Response:
  - PIVOT: Alternative regularization forms (spectral, adversarial)
  - SCOPE: Increase λ range exploration

**R5: CLIP Bias (Medium)**
- Prevention: Test with alternative extractors (DINOv2, ImageNet-pretrained)
- Detection: Compare feature quality across extractors
- Response:
  - PIVOT: Use DINOv2 or ensemble of extractors
  - SCOPE: Document as limitation if EUR works despite CLIP bias

### 4.4 Risk Summary

| ID | Risk | Severity | Mitigation | Status |
|----|------|----------|------------|--------|
| R1 | CV overlap | Critical | Validate separation, pivot metrics | Monitor |
| R2 | Linear probe limits | High | Test MLP alternative | Low priority |
| R3 | Threshold generalization | High | Per-dataset ablation | Planned |
| R4 | Regularization ineffective | High | Validate gradient impact | Monitor |
| R5 | CLIP bias | Medium | Test DINOv2 fallback | Backup |

**Summary:** Critical: 1, High: 3, Medium: 1, Low: 0

---

## 5. Dependency Graph & Timeline

### 5.1 DAG Visualization

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 4 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    ┌─────────────────────────────────────────┐
    │  H-E1: CV Distinguishes Feature Types   │
    │  Gate: MUST_WORK                        │
    └─────────────────────────────────────────┘
                        │
                        ▼
[Level 1 - Detection Mechanism]
    ┌─────────────────────────────────────────┐
    │  H-M1: Probe-Based Detection            │
    │  Gate: MUST_WORK                        │
    └─────────────────────────────────────────┘
                        │
                        ▼
[Level 2 - Classification Mechanism]
    ┌─────────────────────────────────────────┐
    │  H-M2: CV Threshold Classification      │
    │  Gate: SHOULD_WORK                      │
    └─────────────────────────────────────────┘
                        │
                        ▼
[Level 3 - Intervention Mechanism]
    ┌─────────────────────────────────────────┐
    │  H-M3: Gradient Regularization          │
    │  Gate: MUST_WORK                        │
    └─────────────────────────────────────────┘
                        │
                        ▼
                   [COMPLETE]

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3
Path Length: 4 hypotheses (sequential)
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | If Fail |
|-------|------------|---------------|-----------|---------|
| 0 | H-E1 | None | MUST_WORK | STOP: Reassess entire hypothesis |
| 1 | H-M1 | H-E1 | MUST_WORK | STOP: Detection mechanism invalid |
| 2 | H-M2 | H-M1 | SHOULD_WORK | PIVOT: Adaptive threshold selection |
| 3 | H-M3 | H-M2 | MUST_WORK | PIVOT: Alternative regularization |

**Verification Phases:**

| Phase | Hypotheses | Gate Condition | Duration |
|-------|------------|----------------|----------|
| 1. Foundation | H-E1 | Must demonstrate CV separates spurious/core | 1 week |
| 2. Mechanism | H-M1, H-M2, H-M3 | Must show full pipeline works | 2 weeks |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis      │ W1-2     │ W3-4     │ W5       │ W6
──────────────────────┼──────────┼──────────┼──────────┼──────────
PHASE 1: Foundation   │          │          │          │
  H-E1 (Existence)    │ ████████ │          │          │
  [Gate 1]            │        ◆ │          │          │
──────────────────────┼──────────┼──────────┼──────────┼──────────
PHASE 2: Mechanisms   │          │          │          │
  H-M1 (Detection)    │          │ ████████ │          │
  H-M2 (Classification│          │          │ ████     │
  H-M3 (Intervention) │          │          │          │ ████
  [Gate 2]            │          │          │          │    ◆
══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 6 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path

**Critical Path:** H-E1 → H-M1 → H-M2 → H-M3

| Segment | Duration | Cumulative | Gate |
|---------|----------|------------|------|
| H-E1 | 2 weeks | Week 2 | Gate 1: MUST_WORK |
| H-M1 | 2 weeks | Week 4 | - |
| H-M2 | 1 week | Week 5 | - |
| H-M3 | 1 week | Week 6 | Gate 2: MUST_WORK |

**Slack:** 0 weeks (all sequential, no parallelization)

### 5.5 Resource Summary

| Resource | Requirement |
|----------|-------------|
| GPU Compute | 1x A100 (40GB) for ResNet-50 + CLIP feature extraction |
| Storage | ~50GB for Waterbirds + checkpoints + probe cache |
| Runtime per hypothesis | ~4-8 hours (5 seeds × training) |
| Total compute time | ~24-48 GPU-hours |

### 5.6 Execution Order

1. **Week 1-2:** Execute H-E1 - Validate CV distinguishes features
2. **Gate 1:** If AUC < 0.75 → STOP and reassess
3. **Week 3-4:** Execute H-M1 - Validate probe detection mechanism
4. **Week 5:** Execute H-M2 - Validate CV threshold classification
5. **Week 6:** Execute H-M3 - Validate gradient regularization improves worst-group
6. **Gate 2:** If worst-group improvement < 5pp → PIVOT to alternative regularization
7. **Complete:** Proceed to Phase 5 baseline comparison if all gates pass

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** EUR improves worst-group accuracy on spurious correlation benchmarks by detecting and suppressing spurious features based on CV of probe trajectories.

**Supporting Evidence:**
1. Simplicity bias causes spurious features to emerge uniformly (Shah et al. 2020)
2. Core features emerge differentially across implicit groups due to group-specific discriminative power
3. Gradient regularization is established for suppressing specific feature directions

**Strengths:**
- Builds on established simplicity bias and gradient starvation literature
- Clear 3-step causal mechanism (detect, classify, intervene)
- Single-run approach eliminates two-stage training overhead

**Expected Outcomes:**
- Primary: ≥5 pp worst-group improvement on Waterbirds
- Secondary: ≥3 pp improvement on CelebA and ColoredMNIST
- Tertiary: ≤2 pp average accuracy drop

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in worst-group accuracy between EUR and standard ERM training on spurious correlation benchmarks.

**Counter-Arguments:**
1. CV distributions for spurious and core features may overlap significantly
2. Linear probes may miss nonlinear learning dynamics
3. CLIP features may encode spurious correlations from web pretraining
4. Gradient regularization may suppress useful features alongside spurious ones

**Potential Failure Points:**
- R1: CV cannot distinguish feature types (Critical)
- R3: CV threshold fails to generalize across datasets (High)
- R4: Gradient regularization ineffective at suppressing features (High)

**Conditions Under Which H0 Would Be Supported:**
- Feature classification AUC < 0.6 (CV overlap too large)
- Worst-group improvement < 3 pp despite mechanism appearing to work
- Average accuracy drop > 5 pp (over-regularization)

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis H-EUR-v1 presents a testable claim that emergence uniformity serves as a novel signal for spuriousness detection. However, the null hypothesis raises valid concerns regarding CV threshold sensitivity and feature extractor bias.

**Resolution Path:**

The verification plan addresses this dialectic through:
1. **H-E1 directly tests** whether CV distinguishes feature types (addresses core antithesis concern)
2. **Sequential H-M testing** validates each mechanism step with clear fallback strategies
3. **Gate conditions** (MUST_WORK) ensure invalid approaches are caught early (Week 2, Week 6)
4. **Risk mitigation strategies** provide PIVOT options for each identified failure mode

**Conditions for Thesis Support:**
- H-E1 passes with AUC ≥ 0.75
- All MUST_WORK gates pass
- Worst-group improvement ≥ 5 pp confirmed

**Conditions for Antithesis Support:**
- H-E1 fails (CV cannot separate features)
- H-M1 fails (detection mechanism invalid)
- Worst-group improvement < 3 pp after all interventions

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | CV distinguishes features | May be artifact of CLIP | H-E1 + DINOv2 fallback |
| Detection | Probes track emergence | Miss nonlinear dynamics | MLP probe alternative |
| Classification | CV < 0.15 works | Threshold too rigid | Per-dataset ablation |
| Intervention | Gradient penalty effective | May suppress core features | λ sweep + activation monitoring |

**Overall Robustness Score:** Medium-High

**Confidence in Verification Plan:** 0.75

The plan is robust because it tests each component sequentially with clear gates. Failure at any MUST_WORK gate triggers immediate reassessment rather than wasted effort. The synthesis position (confidence 0.8) is that either outcome—thesis support or antithesis support—advances scientific understanding.

---

## 7. Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** EUR detects spurious features via emergence uniformity (CV < 0.15) and applies gradient regularization to improve worst-group accuracy
- ID: H-EUR-v1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 4 total (H-E1, H-M1, H-M2, H-M3)
- Phases: 2 phases over 6 weeks
- Critical Gates: 2 decision points (Gate 1 @ Week 2, Gate 2 @ Week 6)

**Risk Assessment:** Medium
- Primary concerns: R1 (CV overlap), R3 (threshold generalization)

**Immediate Action:** Begin Phase 1 with H-E1 on Waterbirds dataset

### 7.2 Final Summary

**Verification Execution Order:**

| Phase | Hypotheses | Duration | Gate |
|-------|------------|----------|------|
| 1. Foundation | H-E1 | 2 weeks | MUST_WORK |
| 2. Mechanisms | H-M1, H-M2, H-M3 | 4 weeks | MUST_WORK (H-M1, H-M3) |

**Critical Decision Points:**
1. **Gate 1 (Week 2):** H-E1 must demonstrate AUC ≥ 0.75
   - FAIL → STOP, reassess CV metric
   - PASS → Proceed to Phase 2
2. **Gate 2 (Week 6):** H-M3 must show ≥5 pp improvement
   - FAIL → PIVOT to alternative regularization
   - PASS → Proceed to Phase 5 baseline comparison

### 7.3 Conclusions

**Key Achievements:**
- 4 hypotheses defined with clear verification protocols
- 5 risks identified with mitigation strategies
- Sequential DAG ensures foundation before mechanism testing
- Dialectical analysis confirms plan robustness

**Open Questions:**
- Optimal CV threshold value (0.15 proposed, needs validation)
- λ calibration strategy across datasets
- Alternative feature extractors beyond CLIP

**Recommendations:**
1. Start H-E1 immediately on Waterbirds
2. Prepare DINOv2 fallback if CLIP bias detected
3. Reserve 2-week buffer for unexpected pivots

### 7.4 Appendices

**A. Phase 2A Reference:**
- Source: 03_refinement.yaml (H-EUR-v1)
- Scope reduction: 50% (3 BUILD_ON claims excluded)

**B. MCP Tool Usage:**
- scientificmethod: 2 calls (H-E1, H-M integrated)
- structuredargumentation: 3 calls (thesis, antithesis, synthesis)

**C. Dataset Specifications:**
- Waterbirds: 4795 train, 1199 val, 5794 test (95% spurious correlation)
- CelebA: 162770 train, 19867 val, 19962 test (blond hair / gender)
- ColoredMNIST: 50000 train, 10000 test (color / digit correlation)

---

## 8. State & Tasks

### 8.1 Verification State

**File:** `verification_state.yaml`
**Status:** Created with 4 sub-hypotheses

| Hypothesis | Status | Gate |
|------------|--------|------|
| H-E1 | READY | MUST_WORK |
| H-M1 | NOT_STARTED | MUST_WORK |
| H-M2 | NOT_STARTED | SHOULD_WORK |
| H-M3 | NOT_STARTED | MUST_WORK |

### 8.2 Pipeline Tasks

| Task | Status | ID |
|------|--------|-----|
| Phase 2A-Dialogue | done | d4a6fd1b-cf44-4689-88a7-492024aaf934 |
| Phase 2B-Planning | done | 9cc2f88b-94e4-42ed-91c6-e67e7ea026e6 |
| Phase 2C-Experiment | doing | f9446724-a1b5-45a2-be4a-67f23cb916ea |

### 8.3 Hypothesis Tasks

| Hypothesis | Archon Task ID |
|------------|----------------|
| H-E1 | 96d2e1a4-83db-4c1c-bcfc-e347d1b00ffa |
| H-M1 | 70645b46-3d4d-4131-bb2b-addbb3909b21 |
| H-M2 | bcce6eae-b4b4-4411-8c19-f1b93ab7ff0e |
| H-M3 | 97b421ec-b487-48ca-ba49-45a95154b9ef |

---

*Generated by Phase 2B Planning Workflow*
