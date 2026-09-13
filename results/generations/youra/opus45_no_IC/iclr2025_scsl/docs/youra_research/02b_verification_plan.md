# Verification Plan: Loss Trajectory Onset Delay for Spurious Detection (H-LT1)

**Date:** 2026-08-12
**Hypothesis ID:** H-LT1
**Confidence:** 0.75
**Total Hypotheses:** 6

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under standard ERM training of image classifiers on datasets with spurious correlations, if onset delay d_i (epochs until 10% loss reduction) exceeds the early detection threshold T_early (20% of total training), then the sample is enriched for minority-group membership, because simplicity bias causes majority-group samples to converge first on easily-learned spurious correlations, delaying meaningful learning on minority samples.

### 1.2 Alternative Hypothesis (H0)

Onset delay d_i is uniformly distributed across minority and majority groups. Threshold-based selection using d_i performs no better than random sampling for identifying minority-group samples.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Waterbirds (standard) | Canonical benchmark for spurious correlation with known group structure (waterbird/landbird × water/land background) |
| **Model** | ResNet-18 | Standard architecture for spurious correlation benchmarks, enables comparison with JTT, SPARE, DFR |

**Dataset Details:**
- Source: https://github.com/kohpangwei/group_DRO (Sagawa et al., 2019)
- Path: data/waterbirds/
- Size: 4795 train, 1199 val, 5794 test
- Spurious correlation: 95% (bird type ~ background)

**Model Details:**
- Type: CNN
- Source: torchvision.models.resnet18(pretrained=True)

### 1.4 Baseline Methods (for Phase 5 comparison)

| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| ERM | ~72% WGA | Waterbirds | Fails on minority groups due to spurious correlation reliance |
| JTT | ~86% WGA | Waterbirds | Requires two-stage training; binary signal may miss nuance |
| Group DRO | ~91% WGA | Waterbirds | Requires group labels during training (oracle) |

**Best Baseline:** JTT (~86% WGA without training group labels)

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Simplicity bias operates consistently across samples | SPARE demonstrates consistent early learning across Waterbirds, CelebA, MultiNLI | Onset delay would not systematically differ between groups |
| A2 | Onset delay observable by 20% of training epochs | SPARE identifies spurious correlations in first 20% | Detection phase too short for reliable measurement |
| A3 | Minority/majority differences manifest in trajectory shape | LA-SSL shows learning SPEED differs | Binary misclassification would contain same info as trajectory |
| A4 | Upweighting detected samples improves WGA | JTT demonstrates 75% gap closure | Detection signal useful for analysis but not intervention |
| A5 | Threshold transfers across datasets | JTT transfers across Waterbirds, CelebA, MultiNLI | Per-dataset threshold tuning required |

### 1.6 Research Gap & Novelty

**Key Innovation:** Adaptive Single-Run (ASR) paradigm - per-sample adaptive detection within single training run.

Unlike JTT (two-stage), SPARE (fixed epoch threshold), or LA-SSL (aggregate speed), we propose using continuous onset delay as a discriminative signal with per-sample adaptive detection. This enables intervention during training without a separate identification phase.

**Differentiation:**
- JTT: binary misclassification, two-stage → We use continuous onset delay, single run
- SPARE: fixed epoch threshold → We use per-sample adaptive onset detection
- LA-SSL: aggregate learning speed → We use multi-dimensional trajectory shape

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Statement | Prerequisites | Gate |
|----|------|-----------|---------------|------|
| H-E1 | EXISTENCE | Onset delay differs between minority/majority groups | None | MUST_WORK |
| H-M1 | MECHANISM | Simplicity bias causes early pattern learning | H-E1 | MUST_WORK |
| H-M2 | MECHANISM | Spurious features learned faster than core features | H-M1 | SHOULD_WORK |
| H-M3 | MECHANISM | Majority samples converge faster due to redundant cues | H-M2 | SHOULD_WORK |
| H-M4 | MECHANISM | Minority samples require core feature learning (delayed) | H-M3 | SHOULD_WORK |
| H-M5 | MECHANISM | Onset delay correlates with group membership (r > 0.4) | H-M4 | SHOULD_WORK |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Onset Delay Existence**

**Type:** EXISTENCE
**Statement:** Under ERM training on Waterbirds, if we compute onset delay d_i = min{t : L_i(t) < 0.9*L_i(0)} for each sample, then minority-group samples have significantly higher d_i than majority-group samples, because simplicity bias causes majority samples to converge first.

**Rationale:** This is the foundation hypothesis. If onset delay does not differ between groups, the entire mechanism is invalid. SPARE and LA-SSL provide indirect support but no direct measurement of onset delay as discriminative signal.

**Variables:**
- IV: Group membership (minority vs majority)
- DV: Onset delay d_i (epochs)
- CV: Architecture (ResNet-18), optimizer (SGD), dataset (Waterbirds)

**Verification Protocol:**
1. Train ResNet-18 on Waterbirds for 100 epochs, logging per-sample losses every epoch.
2. Compute d_i for all 4795 training samples.
3. At T_early=20, threshold samples by d_i > T_early.
4. Compute precision/recall vs ground-truth minority labels.
5. Perform Mann-Whitney U test on d_i distributions.

**Success Criteria (PoC):**
- Primary: Precision > 0.5 AND Recall > 0.3 for minority detection
- Secondary: Mann-Whitney p < 0.05

**Failure Response:**
- IF fails: ABANDON entire hypothesis (foundation failure)

**Dependencies:** None (foundation)

**Source:** Phase 2A SH1, Prediction P1

---
**H-M1: Simplicity Bias Early Learning**

**Type:** MECHANISM
**Statement:** Under ERM training, if simplicity bias operates, then early representations (epoch 5) capture spurious features while later representations (epoch 50) capture core features, because neural networks prioritize simple patterns.

**Rationale:** First causal step. SPARE demonstrates this indirectly; we need to show it holds for our specific setting and measurement approach.

**Variables:**
- IV: Training epoch (early vs late)
- DV: Feature representation content (spurious vs core)
- CV: Same model, same dataset

**Verification Protocol:**
1. Extract representations at epoch 5, 20, 50.
2. Train linear probe classifiers on spurious feature (background).
3. Train linear probe classifiers on core feature (bird shape).
4. Compare probe accuracy progression over epochs.

**Success Criteria (PoC):**
- Primary: Spurious probe accuracy at epoch 5 > Core probe accuracy at epoch 5
- Secondary: CKA similarity shows representation change over training

**Failure Response:**
- IF fails: PIVOT to direct d_i measurement without mechanism explanation

**Dependencies:** H-E1

**Source:** Phase 2A Causal Step 1

---
**H-M2: Spurious Features Easier**

**Type:** MECHANISM
**Statement:** Under ERM training, if spurious features (background) are easier to learn than core features (bird shape), then spurious probe accuracy peaks before core probe accuracy peaks, because spurious correlations provide strong, consistent signal with less variation.

**Rationale:** Second causal step. Explains WHY simplicity bias favors spurious features specifically.

**Variables:**
- IV: Feature type (spurious vs core)
- DV: Learning rate (epochs to peak accuracy)
- CV: Same probing methodology

**Verification Protocol:**
1. Track probe accuracy for both feature types across all epochs.
2. Identify epoch of peak accuracy for each feature type.
3. Compare learning curves statistically.

**Success Criteria (PoC):**
- Primary: Spurious peak epoch < Core peak epoch

**Failure Response:**
- IF fails: Document as limitation, proceed with empirical d_i correlation

**Dependencies:** H-M1

**Source:** Phase 2A Causal Step 2

---
**H-M3: Majority Convergence Advantage**

**Type:** MECHANISM
**Statement:** Under ERM training, if majority samples have redundant cues (both spurious and core predict label), then majority samples show faster loss reduction in epochs 1-20, because either feature suffices for correct prediction.

**Rationale:** Third causal step. Connects feature learning to sample-level dynamics.

**Variables:**
- IV: Sample group (majority vs minority)
- DV: Loss reduction rate in epochs 1-20
- CV: Same training run

**Verification Protocol:**
1. Compute per-sample loss reduction: (L_i(0) - L_i(20)) / L_i(0).
2. Compare distributions between majority and minority groups.
3. Perform statistical test.

**Success Criteria (PoC):**
- Primary: Mean loss reduction (majority) > Mean loss reduction (minority)

**Failure Response:**
- IF fails: Document, proceed to H-M5 correlation test

**Dependencies:** H-M2

**Source:** Phase 2A Causal Step 3

---
**H-M4: Minority Delayed Learning**

**Type:** MECHANISM
**Statement:** Under ERM training, if minority samples lack spurious cues, then they require core feature learning and show delayed onset of loss reduction, because the model must learn harder features without shortcut.

**Rationale:** Fourth causal step. Direct precursor to the main d_i difference.

**Variables:**
- IV: Sample group (minority)
- DV: Onset delay d_i
- CV: Same definition of d_i

**Verification Protocol:**
1. Isolate minority samples (n~227 for Waterbirds).
2. Compute d_i distribution.
3. Compare to majority d_i distribution.
4. Analyze variance and outliers.

**Success Criteria (PoC):**
- Primary: Median d_i (minority) > Median d_i (majority)

**Failure Response:**
- IF fails: Document, check if d_i correlates with other factors (difficulty, noise)

**Dependencies:** H-M3

**Source:** Phase 2A Causal Step 4

---
**H-M5: Onset Delay Group Correlation**

**Type:** MECHANISM
**Statement:** Under ERM training, if the mechanism is correct, then onset delay d_i correlates more strongly with group membership than with sample difficulty/confidence, because the signal is specifically about spurious vs core features, not general difficulty.

**Rationale:** Final mechanism step. Distinguishes our claim from alternative explanations.

**Variables:**
- IV: Predictor (group indicator vs ERM confidence)
- DV: Correlation with d_i
- CV: Same samples, same d_i computation

**Verification Protocol:**
1. Compute Spearman r(d_i, group_indicator).
2. Compute Spearman r(d_i, ERM_confidence).
3. Compare correlation magnitudes.
4. Test significance of difference.

**Success Criteria (PoC):**
- Primary: r(d_i, group) > 0.4 AND r(d_i, confidence) < r(d_i, group)

**Failure Response:**
- IF fails: Report that d_i may be difficulty proxy, not group-specific

**Dependencies:** H-M4

**Source:** Phase 2A Causal Step 5, Prediction P4

---

## 3. Risk Analysis

### 3.1 Assumption-to-Risk Mapping

| Risk | Source | Description | Severity | Affected Hypotheses |
|------|--------|-------------|----------|---------------------|
| R1 | A1 | Simplicity bias inconsistent across samples | High | H-E1, H-M1 |
| R2 | A2 | Onset delay not observable by epoch 20 | Medium | H-E1 |
| R3 | A3 | Trajectory shape contains no more info than binary | High | All H-M |
| R4 | A4 | Upweighting doesn't improve WGA | Medium | (Phase 5) |
| R5 | A5 | Threshold doesn't transfer | Low | (Phase 5) |

### 3.2 Mitigation Strategies

**R1: Simplicity Bias Inconsistency**
- Prevention: Use established dataset (Waterbirds) where SPARE demonstrated consistency
- Detection: Monitor variance in d_i within each group
- Response: If variance too high, report as limitation; consider per-class analysis

**R2: Detection Phase Too Short**
- Prevention: Use T_early=20 (20% of 100 epochs) as per SPARE findings
- Detection: Check if d_i distribution has stabilized by epoch 20
- Response: If not stabilized, extend detection phase to T_early=30

**R3: Trajectory vs Binary Equivalence**
- Prevention: P4 explicitly tests group vs difficulty correlation
- Detection: Compare d_i-based selection with JTT-style binary selection
- Response: If equivalent, report efficiency/simplicity comparison only

### 3.3 Risk Summary

| Severity | Count | Notes |
|----------|-------|-------|
| Critical | 0 | - |
| High | 2 | R1, R3 - core to hypothesis validity |
| Medium | 2 | R2, R4 - affect scope not validity |
| Low | 1 | R5 - Phase 5 concern |

---

## 4. Execution Plan

### 4.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH - 6 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    H-E1 (Existence - MUST_WORK)
         │
         ▼
[Level 1 - Mechanism Chain]
    H-M1 ← H-E1 (MUST_WORK)
         │
         ▼
    H-M2 ← H-M1
         │
         ▼
    H-M3 ← H-M2
         │
         ▼
    H-M4 ← H-M3
         │
         ▼
    H-M5 ← H-M4

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4 → H-M5
═══════════════════════════════════════════════════════════
```

### 4.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Precision > 0.5, Recall > 0.3 | ABANDON |
| H-M1 | MUST_WORK | Spurious probe > Core probe (epoch 5) | PIVOT |
| H-M2 | SHOULD_WORK | Spurious peak < Core peak | Document limitation |
| H-M3 | SHOULD_WORK | Majority reduction > Minority reduction | Document limitation |
| H-M4 | SHOULD_WORK | Minority d_i > Majority d_i | Document limitation |
| H-M5 | SHOULD_WORK | r(d_i, group) > 0.4 | Report as difficulty proxy |

### 4.3 Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 6 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis │ W1-2 │ W3-4 │ W5 │ W6 │ W7 │
─────────────────┼──────┼──────┼────┼────┼────┤
PHASE 1: Foundation
  H-E1           │██████│      │    │    │    │
  [Gate 1]       │      │ ◆    │    │    │    │
─────────────────┼──────┼──────┼────┼────┼────┤
PHASE 2: Mechanisms
  H-M1           │      │██████│    │    │    │
  H-M2           │      │      │████│    │    │
  H-M3           │      │      │    │████│    │
  H-M4           │      │      │    │    │████│
  H-M5           │      │      │    │    │████│
  [Gate 2]       │      │      │    │    │   ◆│
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

### 4.4 Resource Summary

- Total Hypotheses: 6
  - Existence: 1 (H-E1)
  - Mechanism: 5 (H-M1 to H-M5)
- Verification Phases: 2
- Total Duration: 7 weeks
- Critical Path: 7 weeks (all sequential)

---

## 5. Dialectical Analysis

### 5.1 Thesis

**Core Claim:** Onset delay d_i discriminates minority from majority samples during ERM training.

**Supporting Evidence:**
1. SPARE demonstrates simplicity bias causes early spurious learning
2. LA-SSL shows minority samples learn slower overall
3. DFR shows ERM learns good features, classifier fails on minorities

**Strengths:**
- Grounded in established phenomena (simplicity bias)
- Clear causal mechanism with 5 testable steps
- Quantitative predictions with specific thresholds

### 5.2 Antithesis

**Null Hypothesis (H0):** Onset delay d_i is uniformly distributed across groups; threshold selection performs no better than random.

**Counter-Arguments:**
1. Onset delay may correlate with general sample difficulty, not group membership
2. Binary misclassification (JTT) may already capture all relevant information
3. Effect size may be too small to be practically useful

**Conditions for H0 Support:**
- H-E1 fails: Precision ≤ 0.5 OR Recall ≤ 0.3
- H-M5 fails: r(d_i, confidence) ≥ r(d_i, group)

### 5.3 Synthesis

The verification plan addresses this dialectic through:
1. **Foundation verification (H-E1):** Establishes existence before mechanism
2. **Sequential mechanism testing (H-M1-5):** Tests causal chain step-by-step
3. **Explicit difficulty test (H-M5):** P4 distinguishes group from difficulty correlation

**Outcome Possibilities:**
1. **Full Support:** All gates pass → Thesis validated, proceed to Phase 5 baseline comparison
2. **Partial Support:** H-E1, H-M1 pass, later H-M fail → Refined thesis with documented limitations
3. **No Support:** H-E1 fails → Antithesis supported, hypothesis abandoned

### 5.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | d_i differs by group | May be artifact | H-E1 statistical test |
| Mechanism | 5-step causal chain | Alternative explanations | H-M1-5 sequential testing |
| Specificity | Group-specific signal | Difficulty proxy | H-M5 correlation comparison |
| Utility | Enables upweighting | Marginal improvement | Phase 5 comparison |

**Overall Robustness:** Medium-High
**Confidence in Verification Plan:** 0.75

---

## 6. Executive Summary

**Main Hypothesis:** H-LT1 - Onset delay discriminates minority/majority samples
- ID: H-LT1, Confidence: 0.75

**Verification Structure:**
- Mode: Incremental (Phase 2A available)
- Sub-Hypotheses: 6 total (H-E: 1, H-M: 5)
- Phases: 2 phases over 7 weeks
- Critical Gates: 2 decision points (H-E1, H-M1 MUST_WORK)

**Risk Assessment:** Medium
- Primary concerns: R1 (simplicity bias inconsistency), R3 (trajectory vs binary equivalence)

**Immediate Action:** Begin Phase 1 with H-E1 (onset delay existence verification)

---

## 7. Appendices

### A. Phase 2A Reference
- Source: 03_refinement.yaml (H-LT1)
- Scope Reduction: 80% (4 BUILD_ON claims, 1 PROVE_NEW)

### B. MCP Tool Usage
- Total MCP calls: 4
- Tools: scientificmethod (hypothesis + experiment stages)

### C. Open Questions
- What is optimal threshold for T_early? (20% is initial guess from SPARE)
- Does method work on MultiNLI (NLP) or vision-specific?
- What is effect size ceiling compared to two-stage methods?
