# Verification Plan: Loss Trajectory Divergence Analysis for Spurious Correlation Detection

**Date:** 2026-04-14
**Hypothesis ID:** H-LossTraj-v1
**Confidence:** 0.75
**Total Hypotheses:** 4

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement
Under standard ERM training on spurious correlation benchmarks (Waterbirds), if we track per-sample loss trajectories across epochs, then minority group samples will exhibit statistically distinguishable trajectory patterns (AUROC > 0.75) with delayed curvature stabilization (≥3 epochs later than majority), because the model experiences prolonged optimization conflict when spurious background features contradict learned shortcuts.

### 1.2 Alternative Hypothesis (H0)
There is no significant difference in loss trajectory characteristics between minority and majority samples; trajectory-based features predict group membership at chance level (AUROC ≈ 0.5, p > 0.05).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Waterbirds (standard) | Standard spurious correlation benchmark with 95%/5% correlation; provides group labels for stratified analysis |
| **Model** | ResNet-50 | Standard architecture used in spurious correlation literature; enables comparison with prior work |

**Dataset Details:**
- Source: Sagawa et al. (2020) Group DRO paper
- Path: standard download via WILDS or deep_feature_reweighting repo

**Model Details:**
- Type: CNN pretrained
- Source: torchvision.models.resnet50(pretrained=True)

### 1.4 Baseline Methods (for H-CP* comparison)

| Method | Performance | Dataset |
|--------|-------------|---------|
| Gradient Norm Detection | AUC = 0.914 | Waterbirds |
| Attribution Divergence | IoU = 0.6477 (invalidated) | Waterbirds |
| GroupDRO | ~90% WGA | Waterbirds |
| Random Baseline | AUROC = 0.5 | Waterbirds |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Per-sample loss can be reliably tracked without stochastic noise dominating the signal | Use deterministic evaluation passes (no augmentation), 3-point smoothing | Trajectory features will be noisy; AUROC may collapse to chance |
| A2 | Curvature differences reflect optimization dynamics, not just loss scale | Normalized loss (Lₜ/L₁) removes magnitude effects | Curvature timing gap is artifact of scale; mechanism claim invalid |
| A3 | GroupDRO specifically attenuates spurious reliance, not just gradient variance | Variance-matched control condition tests this explicitly | Attenuation is generic smoothing effect; spurious-specific claim fails |
| A4 | Between-seed WGA variance is sufficient (≥3%) for predictive analysis | Pilot runs should verify σ_WGA > 3% | H-M3 underpowered; cross-seed prediction test may be inconclusive |
| A5 | Waterbirds benchmark is representative of spurious correlation phenomenon | Standard benchmark used in 100+ papers; CelebA provides secondary validation | Results may not generalize to other spurious correlation settings |

### 1.6 Research Gap & Novelty

**Gap:** While prior work tracks per-sample dynamics (Toneva: forgetting events) or extracts training features (Li: 142-D TD), no existing work examines loss trajectory divergence between spurious correlation groups, tests whether divergence precedes accuracy gaps, or validates that divergence attenuates under debiasing.

**Novelty:** First temporal characterization of spurious correlation formation dynamics during training - providing a "developmental signature" of bias formation.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-E1 | Existence | MUST_WORK | None | READY |
| H-M1 | Mechanism | SHOULD_WORK | H-E1 | BLOCKED |
| H-M2 | Mechanism | SHOULD_WORK | H-E1 | BLOCKED |
| H-M3 | Mechanism | SHOULD_WORK | H-E1, H-M1 | BLOCKED |

---

### 2.2 Hypothesis Specifications

---

#### H-E1: Trajectory Divergence Existence

**Statement:** Under standard ERM training on Waterbirds, if we extract per-sample loss trajectory features (L₁, slope, variance, time-to-convergence) from epochs 1-5, then these features will predict minority group membership with AUROC > 0.75, because minority samples experience prolonged optimization conflict creating distinctive trajectory patterns.

**Rationale:** This is the foundational existence test. If trajectory divergence is not measurable (AUROC ≤ 0.75), the entire mechanism hypothesis collapses. This test validates that temporal dynamics carry group-discriminative information beyond random chance.

**Variables:**
- Independent: Group Membership (minority vs majority)
- Dependent: Trajectory-Based AUROC
- Controlled: ResNet-50, Waterbirds, ERM training, normalized loss

**Verification Protocol:**
1. Train ERM model for 20 epochs with per-sample loss logging (deterministic eval passes).
2. Extract trajectory features: L₁, slope (L₅-L₁)/4, variance(L₁...L₅), time-to-95%-min.
3. Normalize losses per-sample (Lₜ/L₁) with 3-point moving average smoothing.
4. Train logistic regression on trajectory features; evaluate with 5-fold stratified CV.
5. Compute AUROC and significance vs random baseline (permutation test, p < 0.05).

**Success Criteria:**
- Primary: AUROC > 0.75 with p < 0.05 vs random baseline (0.5)
- Secondary: Feature importance shows multiple trajectory features contribute

**Failure Response:**
- IF fails: ABANDON main hypothesis (trajectory divergence does not exist)

**Dependencies:** None (foundation hypothesis)

**Source:** Phase 2A SH1, Prediction P1

---

#### H-M1: Curvature Timing Gap

**Statement:** Under ERM training, if we compute the second derivative of normalized loss curves, then minority samples will show delayed curvature stabilization (sign-flip epoch ≥3 epochs later than majority in ≥70% of seeds), because prolonged optimization conflict delays the transition from convex to stable loss landscape.

**Rationale:** Curvature timing provides mechanistic depth beyond classification accuracy. It tests whether the temporal signature has a specific structural form (delayed stabilization) consistent with optimization conflict theory.

**Variables:**
- Independent: Group Membership (minority vs majority)
- Dependent: Curvature Timing Gap (epochs)
- Controlled: Curvature threshold (κ > -0.002 for 2 consecutive epochs)

**Verification Protocol:**
1. Compute second derivative of normalized loss: κ = d²(L_norm)/dt².
2. Identify sign-flip epoch: first epoch where κ > -0.002 for 2 consecutive epochs.
3. Calculate median sign-flip epoch for minority vs majority groups.
4. Compute timing gap across 5+ random seeds.
5. Report % seeds showing gap ≥ 3 epochs.

**Success Criteria:**
- Primary: Timing gap ≥ 3 epochs in ≥ 70% of seeds
- Secondary: Gap direction consistent (minority always later)

**Failure Response:**
- IF fails: PIVOT to alternative temporal signatures (e.g., variance patterns)

**Dependencies:** H-E1 (existence must be established first)

**Source:** Phase 2A Causal Step 4, Prediction P2

---

#### H-M2: GroupDRO Attenuation Test

**Statement:** If trajectory divergence reflects spurious-feature conflict specifically, then AUROC will attenuate >0.10 under GroupDRO training but <0.05 under variance-matched random reweighting, because GroupDRO targets spurious reliance while random reweighting only smooths gradients generically.

**Rationale:** This is the key discriminator between spurious-specific and generic sample-hardness explanations. If both methods attenuate similarly, the divergence is not spurious-specific.

**Variables:**
- Independent: Training Regime (ERM vs GroupDRO vs Random Reweighting)
- Dependent: AUROC Attenuation (ΔAUROC)
- Controlled: Variance-matched random reweighting (same gradient variance as GroupDRO)

**Verification Protocol:**
1. Train under ERM, compute baseline AUROC_ERM.
2. Train under GroupDRO, compute AUROC_GroupDRO.
3. Design variance-matched random reweighting with same gradient variance as GroupDRO.
4. Train under random reweighting, compute AUROC_Random.
5. Compare: (AUROC_ERM - AUROC_GroupDRO) vs (AUROC_ERM - AUROC_Random).

**Success Criteria:**
- Primary: AUROC_ERM - AUROC_GroupDRO > 0.10
- Secondary: AUROC_ERM - AUROC_Random < 0.05

**Failure Response:**
- IF fails: EXPLORE alternative explanations (generic sample hardness)

**Dependencies:** H-E1 (baseline AUROC must exist)

**Source:** Phase 2A Causal Step 2-3, Prediction P3, Assumption A3

---

#### H-M3: Cross-Seed Predictive Power

**Statement:** If early trajectory divergence has causal relevance, then W1-distance at epoch 3 will predict final WGA at epoch 20 with R² > 0.5 across 10+ seeds, because early divergence signatures precede and cause downstream accuracy gaps.

**Rationale:** This transforms correlation into near-causal evidence. If early divergence predicts final outcomes across independent training runs, it suggests the divergence is causally upstream of accuracy gaps.

**Variables:**
- Independent: W1-distance at epoch 3 (between-group trajectory distribution distance)
- Dependent: WGA at epoch 20 (Worst-Group Accuracy)
- Controlled: Same architecture, dataset, hyperparameters across seeds

**Verification Protocol:**
1. Run 10+ training seeds with per-sample loss tracking.
2. Compute W1-distance (Wasserstein-1) between minority/majority trajectory distributions at epoch 3.
3. Record final WGA at epoch 20 for each seed.
4. Regress WGA_epoch20 on W1-distance_epoch3 using nested cross-validation.
5. Report R², effect size (β × σ_W1 / σ_WGA), and held-out RMSE vs mean baseline.

**Success Criteria:**
- Primary: R² > 0.5 with effect size ≥ 3% WGA per SD of W1-distance
- Secondary: Held-out RMSE beats mean baseline by ≥ 30%

**Failure Response:**
- IF fails: Document as correlation only (no predictive power)

**Dependencies:** H-E1 (existence), H-M1 (curvature establishes temporal structure)

**Source:** Phase 2A Causal Step 4, Prediction P4, Assumption A4

---

## 3. Risk Analysis

### 3.1 Risk-Hypothesis Mapping

| Risk | Source | Description | Severity | Affected Hypotheses |
|------|--------|-------------|----------|---------------------|
| R1 | A1 | Noise Domination | HIGH | H-E1, H-M1, H-M2, H-M3 |
| R2 | A2 | Scale Artifacts | MEDIUM | H-M1 |
| R3 | A3 | Generic Attenuation | HIGH | H-M2 |
| R4 | A4 | Insufficient WGA Variance | MEDIUM | H-M3 |
| R5 | A5 | Benchmark Specificity | LOW | All |

### 3.2 Risk Details & Mitigation

**R1: Noise Domination (HIGH)**
- **Source:** A1 - Per-sample loss tracking may be dominated by stochastic noise
- **Impact:** If trajectory features are noise-dominated, AUROC collapses to chance; H-E1 fails, cascading to all mechanism hypotheses
- **Mitigation:**
  - Prevention: Use deterministic evaluation passes (no augmentation, fixed batch order)
  - Prevention: Apply 3-point moving average smoothing to loss curves
  - Detection: Pilot run to verify signal-to-noise ratio before full experiment
  - Response: If pilot fails, explore alternative smoothing (5-point, exponential)
- **Early Warning:** AUROC < 0.60 in pilot run

**R2: Scale Artifacts (MEDIUM)**
- **Source:** A2 - Curvature differences may reflect loss magnitude, not dynamics
- **Impact:** H-M1 curvature timing gap is artifact of scale, not optimization conflict
- **Mitigation:**
  - Prevention: Normalize losses per-sample (Lₜ/L₁) before curvature computation
  - Detection: Verify curvature patterns persist after scale normalization
  - Response: If normalization removes signal, pivot to alternative temporal signatures
- **Early Warning:** Curvature gap disappears after normalization

**R3: Generic Attenuation (HIGH)**
- **Source:** A3 - GroupDRO attenuation may be generic gradient smoothing, not spurious-specific
- **Impact:** H-M2 mechanism claim fails; divergence is not spurious-specific
- **Mitigation:**
  - Prevention: Mandatory variance-matched random reweighting control
  - Detection: Compare attenuation magnitudes between GroupDRO and random control
  - Response: If both attenuate similarly, document as "generic sample hardness" finding
- **Early Warning:** Random reweighting attenuates AUROC by > 0.05

**R4: Insufficient WGA Variance (MEDIUM)**
- **Source:** A4 - Between-seed WGA variance < 3% makes H-M3 underpowered
- **Impact:** Cross-seed prediction test inconclusive (but H-E1/H-M1/H-M2 unaffected)
- **Mitigation:**
  - Prevention: Pilot run with 5 seeds to verify σ_WGA > 3%
  - Detection: Check variance before committing to 10+ seed experiment
  - Response: If variance insufficient, document as limitation; skip H-M3
- **Early Warning:** σ_WGA < 2% in pilot seeds

**R5: Benchmark Specificity (LOW)**
- **Source:** A5 - Waterbirds may not be representative of spurious correlation generally
- **Impact:** Results may not generalize to other settings
- **Mitigation:**
  - Prevention: Accept benchmark-specific results for PoC phase
  - Detection: Note any Waterbirds-specific artifacts
  - Response: CelebA secondary validation in Phase 5
- **Early Warning:** Results depend on Waterbirds-specific properties

### 3.3 Risk Summary

| Severity | Count | IDs |
|----------|-------|-----|
| Critical | 0 | - |
| High | 2 | R1, R3 |
| Medium | 2 | R2, R4 |
| Low | 1 | R5 |

**Recommendation:** Execute pilot run first to verify A1 (signal-to-noise) and A4 (WGA variance). Proceed with fail-fast order: H-E1 → H-M2 → H-M1 → H-M3.

---

## 4. Dependency Graph (DAG)

### 4.1 DAG Visualization

```
═══════════════════════════════════════════════════════════════════════════
                    DEPENDENCY GRAPH - 4 Hypotheses
═══════════════════════════════════════════════════════════════════════════

[Level 0 - Foundation]
                    ┌─────────────────────────────┐
                    │  H-E1: Trajectory Existence │
                    │  Gate: MUST_WORK            │
                    │  AUROC > 0.75               │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                             │
                    ▼                             ▼
[Level 1 - Mechanism Tests]
    ┌─────────────────────────────┐   ┌─────────────────────────────┐
    │  H-M1: Curvature Timing     │   │  H-M2: GroupDRO Attenuation │
    │  Gate: SHOULD_WORK          │   │  Gate: SHOULD_WORK          │
    │  Gap ≥ 3 epochs             │   │  Δ > 0.10 (GroupDRO)        │
    └──────────────┬──────────────┘   └─────────────────────────────┘
                   │
                   ▼
[Level 2 - Causal Evidence]
    ┌─────────────────────────────┐
    │  H-M3: Cross-Seed Predict   │
    │  Gate: SHOULD_WORK          │
    │  R² > 0.5                   │
    └─────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M3
Parallelizable: H-M1 ∥ H-M2 (both depend only on H-E1)
═══════════════════════════════════════════════════════════════════════════
```

### 4.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Parallel Group |
|-------|------------|---------------|-----------|----------------|
| 0 | H-E1 | None | MUST_WORK | - |
| 1 | H-M1 | H-E1 | SHOULD_WORK | A |
| 1 | H-M2 | H-E1 | SHOULD_WORK | A |
| 2 | H-M3 | H-E1, H-M1 | SHOULD_WORK | B |

### 4.3 Verification Phases

**Phase 0 - Pilot Run**
- Verify A1: Signal-to-noise ratio (deterministic eval + smoothing)
- Verify A4: Between-seed WGA variance ≥ 3%
- Duration: 2-3 hours
- Gate: If pilot fails → investigate noise sources before proceeding

**Phase 1 - Foundation (H-E1)**
- Test: Trajectory features predict minority membership
- Success: AUROC > 0.75, p < 0.05
- Gate: MUST_WORK - if fails, ABANDON main hypothesis

**Phase 2 - Mechanism (H-M1, H-M2 - parallelizable)**
- H-M1: Curvature timing gap ≥ 3 epochs in ≥ 70% seeds
- H-M2: GroupDRO attenuates > 0.10, Random < 0.05
- Gate: SHOULD_WORK - failures narrow scope but don't invalidate

**Phase 3 - Causal Evidence (H-M3)**
- Test: Early divergence predicts final WGA
- Success: R² > 0.5, effect size ≥ 3%/SD
- Gate: SHOULD_WORK - failure documents as correlation only

---

## 5. Execution

### 5.1 Recommended Execution Order
```
H-E1 (Existence) ──┬──→ H-M1 (Curvature) ──→ H-M3 (Cross-Seed)
                   │
                   └──→ H-M2 (Attenuation)
```

### 5.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | AUROC > 0.75, p < 0.05 | ABANDON (main hypothesis invalid) |
| H-M1 | SHOULD_WORK | Gap ≥ 3 epochs in ≥ 70% seeds | PIVOT to alternative temporal signatures |
| H-M2 | SHOULD_WORK | GroupDRO Δ > 0.10, Random Δ < 0.05 | EXPLORE generic hardness explanation |
| H-M3 | SHOULD_WORK | R² > 0.5, effect ≥ 3%/SD | Document as correlation only |

### 5.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Pilot | Signal/variance check | 2-3 hours |
| Phase 1 | H-E1 (Existence) | 4-6 hours |
| Phase 2a | H-M2 (Attenuation) | 6-8 hours |
| Phase 2b | H-M1 (Curvature) | 3-4 hours |
| Phase 3 | H-M3 (Cross-Seed) | 8-12 hours |

**Total Duration:** ~24-33 hours (excluding Phase 5 baseline comparison)

### 5.4 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════════════════════
                    VERIFICATION TIMELINE - 4 Hypotheses
═══════════════════════════════════════════════════════════════════════════════════
Phase/Hypothesis     │ Hour 0-4  │ Hour 4-8  │ Hour 8-12 │ Hour 12-20│ Hour 20-33│
─────────────────────┼───────────┼───────────┼───────────┼───────────┼───────────┤
PILOT: Validation    │           │           │           │           │           │
  Signal/Variance    │ ██        │           │           │           │           │
  [Pilot Gate]       │    ◆      │           │           │           │           │
─────────────────────┼───────────┼───────────┼───────────┼───────────┼───────────┤
PHASE 1: Foundation  │           │           │           │           │           │
  H-E1 Existence     │    ███████│███        │           │           │           │
  [Gate 1: MUST]     │           │   ◆       │           │           │           │
─────────────────────┼───────────┼───────────┼───────────┼───────────┼───────────┤
PHASE 2: Mechanisms  │           │           │           │           │           │
  H-M1 Curvature     │           │    ███████│           │           │           │
  H-M2 Attenuation   │           │    ███████│███████████│           │           │
  [Gate 2: SHOULD]   │           │           │           │◆          │           │
─────────────────────┼───────────┼───────────┼───────────┼───────────┼───────────┤
PHASE 3: Causal      │           │           │           │           │           │
  H-M3 Cross-Seed    │           │           │           │ ██████████│███████████│
  [Gate 3: SHOULD]   │           │           │           │           │          ◆│
═══════════════════════════════════════════════════════════════════════════════════
Legend: ██ = Active work | ◆ = Gate decision point
Total Duration: 24-33 hours | Critical Path: Pilot → H-E1 → H-M1 → H-M3
═══════════════════════════════════════════════════════════════════════════════════
```

### 5.5 Critical Path Analysis

**Critical Path:** Pilot → H-E1 → H-M1 → H-M3
**Path Duration:** 2-3h + 4-6h + 3-4h + 8-12h = **17-25 hours minimum**

**Parallelization Opportunity:**
- H-M1 and H-M2 can run in parallel after H-E1 passes
- If parallelized: saves 3-4 hours on critical path
- Recommended: Run H-M2 (longer) first, H-M1 can overlap

**Slack Analysis:**
| Hypothesis | Duration | Float | On Critical Path |
|------------|----------|-------|------------------|
| Pilot | 2-3h | 0 | Yes |
| H-E1 | 4-6h | 0 | Yes |
| H-M1 | 3-4h | 0 | Yes |
| H-M2 | 6-8h | 3-4h | No (parallel) |
| H-M3 | 8-12h | 0 | Yes |

### 5.6 Resource Requirements

| Phase | GPU Hours | Seeds | Key Resources |
|-------|-----------|-------|---------------|
| Pilot | 2-3h | 5 | 1 GPU, basic logging |
| H-E1 | 4-6h | 3-5 | 1 GPU, loss tracking |
| H-M1 | 3-4h | 5+ | Same runs as H-E1 |
| H-M2 | 6-8h | 3-5 | 3 training regimes |
| H-M3 | 8-12h | 10+ | Multi-seed runs |

**Total GPU Time:** ~24-33 hours (sequential) or ~20-28 hours (with parallelization)

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** Loss trajectory divergence exists between minority and majority samples and reflects spurious-feature conflict dynamics during ERM training.

**Supporting Evidence:**
1. Per-sample training dynamics are trackable and informative (Toneva et al., 933 citations)
2. Gradient norm detection achieves AUC=0.914 for minority detection, proving gradients carry group information
3. Encoder representations diverge between groups (CKA=0.115), indicating differential feature learning
4. Spectral bias theory predicts faster convergence for pattern-aligned samples
5. Attribution patterns are similar (IoU=0.6477), ruling out WHERE-based explanations and pointing to HOW/WHEN

**Strengths:**
- Builds on established findings from 7+ previous runs
- Clear quantitative thresholds enable falsification
- Temporal analysis is genuinely novel - no prior work on trajectory divergence for spurious correlations
- Multiple converging lines of evidence support the mechanism

**Weaknesses:**
- Cannot mathematically prove spurious-feature causality vs structured hardness
- Relies on assumption that noise can be sufficiently controlled
- Limited to Waterbirds benchmark initially

**Expected Outcome:** Trajectory features (L₁, slope, variance, convergence time) will predict minority membership with AUROC > 0.75, and this divergence will attenuate specifically under GroupDRO (not random reweighting).

**Confidence:** 0.75

### 6.2 Antithesis (H0)

**Null Hypothesis:** There is no significant difference in loss trajectory characteristics between minority and majority samples; any observed divergence reflects generic sample hardness, not spurious-feature conflict.

**Counter-Arguments:**
1. Detection success (AUC=0.914) did not translate to intervention success in 7+ attempts - detection may be measuring the wrong thing
2. Trajectory differences could reflect inherent sample difficulty unrelated to spurious features
3. Stochastic noise in per-sample loss tracking may dominate any true signal
4. GroupDRO attenuation could be generic gradient smoothing, not spurious-specific
5. Curvature timing differences may be scale artifacts rather than optimization dynamics

**Strengths:**
- Consistent with repeated intervention failures despite detection success
- Parsimony - generic sample hardness is simpler than spurious-specific mechanism
- Addresses the attribution similarity finding (groups look at same regions)

**Weaknesses:**
- Does not explain why gradient norms achieve high detection AUC
- Does not account for differential convergence rates predicted by spectral bias
- Temporal analysis has not been attempted before - cannot rule out a priori

**Conditions for H0 Support:**
- AUROC ≤ 0.75 or not significantly different from chance (p > 0.05)
- GroupDRO and random reweighting attenuate AUROC equally (both > 0.05 or both < 0.05)
- Curvature timing gap < 2 epochs in ≥ 70% of seeds

**Confidence:** 0.25

### 6.3 Synthesis

**Balanced Assessment:**

The hypothesis H-LossTraj-v1 presents a testable claim that temporal dynamics of loss curves carry discriminative information about spurious correlation group membership. However, the null hypothesis raises valid concerns that any observed divergence may reflect generic sample difficulty rather than spurious-specific optimization conflict.

**Resolution Path:**

The verification plan addresses this dialectic through:

1. **Foundation verification (H-E1):** Establishes existence before investigating mechanism - if AUROC ≤ 0.75, antithesis supported
2. **Variance-matched control (H-M2):** The key discriminator - if GroupDRO and random reweighting attenuate equally, the signal is not spurious-specific
3. **Sequential mechanism testing (H-M1, H-M3):** Provides mechanistic depth and near-causal evidence
4. **Fail-fast execution order:** Minimizes wasted effort if antithesis is correct

**Outcome Possibilities:**

| Outcome | Conditions | Interpretation |
|---------|------------|----------------|
| **Full Thesis Support** | H-E1, H-M1, H-M2, H-M3 all pass | Trajectory divergence exists, is spurious-specific, and has predictive power |
| **Partial Support** | H-E1 passes, H-M2 fails | Divergence exists but is not spurious-specific (generic hardness) |
| **Partial Support** | H-E1, H-M2 pass, H-M3 fails | Spurious-specific divergence exists but lacks predictive power |
| **Antithesis Support** | H-E1 fails | No measurable trajectory divergence - hypothesis invalid |

**Confidence in Verification Plan:** 0.85

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution Test |
|--------|-----------------|----------------------|-----------------|
| Existence | Divergence is measurable | May be noise/artifact | H-E1: AUROC > 0.75 |
| Mechanism | Spurious-feature conflict | Generic sample hardness | H-M2: Variance-matched control |
| Temporal Structure | Curvature timing gap | Scale artifacts | H-M1: Normalized curvature |
| Causal Relevance | Predicts future WGA | Correlation only | H-M3: Cross-seed R² > 0.5 |

**Overall Robustness Score:** HIGH

- Explicit quantitative thresholds enable unambiguous adjudication
- Variance-matched control addresses the core uncertainty
- Fail-fast design treats thesis and antithesis fairly
- Either outcome advances scientific understanding

---

## 7. Executive Summary

### 7.1 Hypothesis Overview

**Main Hypothesis (H-LossTraj-v1):** Under standard ERM training on spurious correlation benchmarks, per-sample loss trajectories exhibit statistically distinguishable patterns between minority and majority groups, with AUROC > 0.75 and delayed curvature stabilization (≥3 epochs), because minority samples experience prolonged optimization conflict.

**Novelty:** First temporal characterization of spurious correlation formation dynamics during training.

**Scope Reduction:** 40% - building on 5 established facts from prior work.

### 7.2 Sub-Hypotheses Summary

| ID | Type | Test | Success Criterion | Gate |
|----|------|------|-------------------|------|
| H-E1 | Existence | Trajectory-based minority prediction | AUROC > 0.75 | MUST_WORK |
| H-M1 | Mechanism | Curvature timing gap | Gap ≥ 3 epochs, 70% seeds | SHOULD_WORK |
| H-M2 | Mechanism | GroupDRO attenuation test | Δ > 0.10 GroupDRO, < 0.05 Random | SHOULD_WORK |
| H-M3 | Mechanism | Cross-seed predictive power | R² > 0.5, effect ≥ 3%/SD | SHOULD_WORK |

### 7.3 Key Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| R1: Noise Domination | HIGH | Deterministic eval, 3-point smoothing, pilot run |
| R3: Generic Attenuation | HIGH | Variance-matched random reweighting control |
| R2: Scale Artifacts | MEDIUM | Normalized loss (Lₜ/L₁) |
| R4: WGA Variance | MEDIUM | Pilot run to verify σ_WGA > 3% |

### 7.4 Execution Plan

**Recommended Order:** Pilot → H-E1 → H-M2 → H-M1 → H-M3
**Total Duration:** 24-33 hours (20-28 with parallelization)
**Critical Path:** Pilot → H-E1 → H-M1 → H-M3

### 7.5 Decision Points

1. **Pilot Gate:** If signal-to-noise insufficient → investigate noise sources
2. **Gate 1 (H-E1):** If AUROC ≤ 0.75 → ABANDON (antithesis supported)
3. **Gate 2 (H-M2):** If attenuation is generic → EXPLORE alternative explanations
4. **Gate 3 (H-M1):** If curvature gap < 2 epochs → PIVOT to alternative temporal signatures
5. **Gate 4 (H-M3):** If R² < 0.3 → Document as correlation only

---

## 8. Appendices

### A. Phase 2A Reference
- **Source:** `03_refinement.yaml` (H-LossTraj-v1)
- **Schema Version:** 10.0.0
- **Gap ID:** gap-1 (No Existing Loss Trajectory Divergence Analysis for Spurious Correlation)

### B. MCP Tool Usage Summary
- **Total MCP calls:** 6
- **Tools used:**
  - `mcp__clearThought__scientificmethod`: 4 calls (hypothesis + experiment stages)
  - `mcp__clearThought__collaborativereasoning`: 1 call (risk analysis)
  - `mcp__clearThought__structuredargumentation`: 3 calls (thesis/antithesis/synthesis)

### C. Open Questions for Phase 2C
1. What is the exact epoch of first significant divergence?
2. Does the signal generalize to CelebA?
3. Can trajectory features enable successful intervention (beyond detection)?

### D. Related Files
- `00_brainstorm_session.md` - Phase 0 output
- `01_targeted_research.md` - Phase 1 output
- `03_refinement.yaml` - Phase 2A output (primary input)
- `02_synthesis.yaml` - Phase 2A synthesis (supplementary)
- `verification_state.yaml` - Generated by Phase 2B Step 10

---

*Generated by YouRA Phase 2B v6.0 | 2026-04-14*
