---
stepsCompleted: ["step-00-init-environment", "step-01-init-parsing", "step-02-input-hypothesis", "step-03-hypothesis-generation", "step-04-hypothesis-inventory", "step-05-risk-analysis", "step-06-dependency-graph", "step-07-timeline-planning", "step-08-dialectical-analysis", "step-09-summary", "step-10-finalize"]
status: complete
completedAt: "2026-08-21T00:00:00Z"
hypothesis_id: H-SAMSSL-v1
confidence_level: 0.72
total_hypothesis_count: 5
research_scope_mode: incremental
---

# Verification Plan: SAM-SSL Sharpness Anisotropy Hypothesis for Spurious Correlation Reduction

**Date:** 2026-08-21
**Hypothesis ID:** H-SAMSSL-v1
**Confidence:** 0.72
**Total Hypotheses:** 5

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under standard SSL pre-training (SimCLR/MoCo/DINO) on spurious correlation benchmarks
(Waterbirds/CelebA/CMNIST), if SAM is used as the optimizer instead of SGD/Adam
during contrastive pre-training, then worst-group accuracy improves by ≥2pp on at
least 2 of 3 benchmarks without group annotations, because SAM preferentially reduces
Hessian sharpness along spurious feature directions (identified via linear-probe loss
variance proxy following the LFR annotation-free protocol), and this sharpness
anisotropy reduction corresponds to reduced reliance on shortcut features in the
learned SSL representations.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in worst-group accuracy between SAM-trained and
SGD-trained SSL models (SimCLR/MoCo/DINO) on Waterbirds, CelebA, and CMNIST
(difference < 1pp on all datasets). Equivalently, loss landscape sharpness anisotropy
along spurious feature directions does not correlate with worst-group accuracy in SSL
models (|r| < 0.2, p > 0.05).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Waterbirds (primary), CelebA (secondary), CMNIST (secondary) (standard) | Canonical spurious correlation benchmarks with established worst-group evaluation protocols. Waterbirds has well-characterized spurious (background) vs. core (bird morphology) feature structure. CelebA and CMNIST provide diversity check. |
| **Model** | ResNet-50 | Standard SSL backbone; izmailovpavel/spurious_feature_learning uses ResNet-50 for SSL spurious analysis; enables direct comparison with existing SSL spurious work. |

**Dataset Details:**
- Source: kohpangwei/group_DRO repository; torchvision for CMNIST
- Path: Standard dataset loading via kohpangwei/group_DRO loaders

**Model Details:**
- Type: CNN backbone for SSL
- Source: torchvision pretrained weights (ImageNet init) or random init depending on SSL method standard protocol

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| SimCLR + SGD (standard) | ~75-80% worst-group (estimated from CLIP 80.7pp avg-worst gap) | Waterbirds |
| LFR (annotation-free, Ghaznavi 2023) | Beats DFR-Oracle on annotation-free setting | Waterbirds, CelebA |
| Group DRO (oracle upper bound) | ~91% worst-group with group labels | Waterbirds, CelebA |
| Cross-Variant SSL (Yadav 2026) | 92.5% worst-group (best SSL+spurious result) | Waterbirds |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | InfoNCE landscape qualitatively differs from supervised cross-entropy (no rank-1 simplicity bias transfer) | InfoNCE creates uniform distribution pressure (von Mises-Fisher) with no single rank-1 attractor | SAM would INCREASE spurious feature reliance → P3 fails, intervention is counterproductive |
| A2 | Linear probe loss variance is a valid annotation-free proxy for minority group membership and spurious direction identification | LFR (Ghaznavi 2023) validates proxy on Waterbirds/CelebA; EVaLS uses similar mechanism | Proxy precision/recall < 0.6 → P1 measurement invalid, cannot test |
| A3 | Hessian sharpness anisotropy (spurious vs. random direction ratio) is the relevant geometric property linking loss landscape to shortcut reliance | SCER (Park 2025) theoretically links embedding geometry to worst-group error | Anisotropy may exist but not predict worst-group accuracy |
| A4 | Standard SSL augmentation leaves spurious feature content consistent enough that SAM (not augmentation) is the primary mechanism | Cross-Variant SSL uses generative augmentation; our hypothesis relies on optimizer-level intervention | Standard augmentation already randomizes spurious features → baseline SSL already low-shortcut |
| A5 | SAM's 2x computational cost does not prevent convergence on ResNet-50 SSL training | davda54/sam widely used for 200-epoch ResNet-50 supervised training | Not a scientific barrier; resource/cost issue only (Prof. Pax) |

### 1.6 Research Gap & Novelty

**Confirmed Gap:** No paper has combined SAM-type optimization with SSL pre-training on spurious correlation benchmarks (confirmed absent: G2-SAM supervised-only, DGSAM domain-generalization-only, SubpopBench supervised-only).

**Key Innovation:** Decoupled two-part hypothesis: (1) sharpness anisotropy as annotation-free diagnostic of SSL shortcut reliance; (2) SAM as training-time intervention to reduce anisotropy. Both contributions are independent — diagnostic holds regardless of whether SAM intervention works.

**Scope Reduction:** 62% of claims are BUILD_ON (pre-validated). Only 3 PROVE_NEW claims require new verification.

**PROVE_NEW Claims:**
1. No paper has combined SAM+SSL on spurious correlation benchmarks
2. Loss landscape sharpness anisotropy along spurious directions correlates with worst-group accuracy in SSL
3. SAM during SSL pre-training reduces spurious sharpness anisotropy and improves worst-group accuracy

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
**H-E1: SSL Loss Landscape Sharpness Anisotropy Existence**

**Type:** EXISTENCE
**Gate:** MUST_WORK — failure stops the entire hypothesis chain

**Statement:** Under standard SSL pre-training (SimCLR/MoCo-v2/DINO) with SGD on spurious correlation benchmarks (Waterbirds/CelebA/CMNIST), the loss landscape exhibits statistically significant sharpness anisotropy: the SAM perturbation loss increase along spurious feature directions (identified via linear probe loss variance proxy) is higher than along random directions (ratio > 1.2), and this anisotropy ratio correlates negatively with worst-group accuracy across model checkpoints (Pearson r < -0.5, p < 0.05).

**Rationale:** This is the foundation hypothesis. Before testing whether SAM can reduce spurious sharpness, we must first confirm that such anisotropy exists in SSL models trained on spurious benchmarks. If anisotropy is absent (ratio ≈ 1.0), the entire causal mechanism fails at step 1 and further experimentation is unwarranted. This directly verifies PROVE_NEW claim #2.

**Variables:**
- Independent: SSL pre-training method (SimCLR/MoCo-v2/DINO), benchmark dataset (Waterbirds/CelebA/CMNIST)
- Dependent: Sharpness anisotropy ratio (spurious/random SAM perturbation loss), Pearson r with worst-group accuracy
- Controlled: ResNet-50 backbone, identical augmentation pipeline, identical linear probe protocol (100 epochs, SGD, lr=0.01), 200 training epochs, SGD optimizer

**Verification Protocol:**
1. Train 9 SSL models (3 methods × 3 datasets) with SGD for 200 epochs; save checkpoints at epochs 50/100/150/200.
2. For each checkpoint: train linear probe on frozen representations (100 epochs, SGD, lr=0.01, no group labels).
3. Identify top-25% high-loss-variance samples from linear probe loss distribution as spurious direction proxy.
4. Measure SAM perturbation loss increase along spurious proxy directions vs. 100 random directions (rho=0.05); compute anisotropy ratio.
5. Evaluate worst-group accuracy via group_DRO protocol (group labels for evaluation only); compute Pearson r between anisotropy ratio and worst-group accuracy across checkpoints per model.

**Success Criteria (PoC):**
- Primary: Anisotropy ratio > 1.2 AND |r| > 0.5, p < 0.05 in at least 7/9 model-dataset combinations
- Secondary: Validate linear probe proxy quality — report precision/recall vs. ground-truth group labels ≥ 0.6

**Failure Response:**
- IF anisotropy ratio ≈ 1.0 across all models: ABANDON — mechanism does not exist in SSL InfoNCE setting; route to Phase 0
- IF ratio > 1.2 but |r| < 0.2: EXPLORE — anisotropy exists but does not predict worst-group accuracy; A3 violated

**Dependencies:** None (foundation)
**Source:** Phase 2A Section 1.3 (Causal Step 1), Section 1.6 (P1), Section 5 (SH1)

---

**H-M1: Spurious Direction Identification via Linear Probe Loss Variance**

**Type:** MECHANISM
**Gate:** MUST_WORK

**Statement:** Under SSL pre-training (SimCLR/MoCo-v2/DINO) with SGD on Waterbirds/CelebA/CMNIST, the linear probe trained on frozen SSL representations exhibits high loss variance specifically for minority group samples (e.g., waterbirds on land backgrounds), validly identifying the spurious feature directions in representation space without group annotations — with precision/recall ≥ 0.6 vs. held-out ground-truth group labels.

**Rationale:** This hypothesis validates the annotation-free measurement instrument (LFR proxy) in the SSL setting. The LFR proxy was validated on supervised ERM representations (Ghaznavi 2023); transfer to SSL InfoNCE representations is not guaranteed. If precision/recall < 0.6, the anisotropy measurement in H-E1 and the SAM intervention evaluation in H-M3/H-M4 lack a valid directional anchor. This is a mechanistic prerequisite step.

**Variables:**
- Independent: SSL pre-training method, benchmark dataset
- Dependent: Precision/recall of top-25% high-loss-variance samples vs. ground-truth minority group labels
- Controlled: ResNet-50, SGD pre-training, identical linear probe protocol

**Verification Protocol:**
1. Train linear probe on SGD-pretrained SSL representations (100 epochs, SGD, lr=0.01, no group labels used in training).
2. Compute linear probe loss for each sample in the training set.
3. Identify top-25% high-loss-variance samples as predicted spurious/minority group proxy.
4. Compare to ground-truth minority group labels (evaluation-only) to compute precision and recall.
5. Report precision/recall across 9 model-dataset combinations; threshold ≥ 0.6 for validity.

**Success Criteria (PoC):**
- Primary: Precision/recall ≥ 0.6 in at least 7/9 model-dataset combinations

**Failure Response:**
- IF precision/recall < 0.6 consistently: PIVOT — A2 violated; explore alternative proxy (e.g., gradient similarity, class activation maps) or use held-out group labels for direction identification

**Dependencies:** H-E1
**Source:** Phase 2A Section 1.3 (Causal Step 2), Section 1.4 (A2)

---

**H-M2: SAM Reduces Spurious Direction Sharpness During SSL Pre-Training**

**Type:** MECHANISM
**Gate:** MUST_WORK

**Statement:** SAM optimizer (rho=0.05) applied during SSL pre-training reduces Hessian sharpness preferentially along the spurious feature directions (identified via linear probe loss variance proxy): the spurious-to-random sharpness ratio is lower in SAM-trained models by ≥15% vs. SGD-trained models at convergence (SAM ratio ≤ 0.85 × SGD ratio), while majority-group linear probe accuracy is preserved within 2pp (ruling out fake flat minima — uniform flattening without selective anisotropy reduction).

**Rationale:** This is the central mechanistic test of the SAM intervention. The key tension (Gatmiry 2024 rank-1 simplicity bias) predicts SAM might INCREASE shortcut reliance in supervised settings; the InfoNCE landscape argument predicts the opposite. This hypothesis directly tests which prediction holds in the SSL setting. The majority accuracy preservation check distinguishes true shortcut reduction from fake flat minima (DGSAM failure mode). Verifies PROVE_NEW claim #3 mechanistically.

**Variables:**
- Independent: Optimizer (SAM rho=0.05, ASAM rho=0.5 vs. SGD baseline), SSL method
- Dependent: Spurious-to-random sharpness ratio reduction (SAM/SGD ratio), majority-group accuracy change
- Controlled: ResNet-50, identical augmentation, 200 epochs, identical linear probe evaluation

**Verification Protocol:**
1. Train SAM (rho=0.05) and ASAM (rho=0.5) variants for all 9 SSL method × dataset combinations (200 epochs).
2. Measure sharpness anisotropy ratio at final checkpoint (same measurement protocol as H-E1/H-M1).
3. Compute ratio-reduction: SAM_anisotropy / SGD_anisotropy (target: ≤ 0.85).
4. Measure majority-group linear probe accuracy for SAM and SGD models; compute difference.
5. Report both ratio-reduction and majority accuracy change across model-dataset combinations.

**Success Criteria (PoC):**
- Primary: SAM anisotropy ratio ≤ 0.85 × SGD anisotropy ratio in ≥ 2/3 datasets
- Secondary: Majority accuracy drop < 2pp (fake flat minima not occurring)

**Failure Response:**
- IF SAM ratio ≥ SGD ratio: ABANDON H-M2 → Gatmiry rank-1 bias transfers to InfoNCE; route to Phase 2A-Dialogue for hypothesis revision
- IF ratio reduces but majority accuracy drops > 5pp: EXPLORE — fake flat minima dominating; test with higher rho values or ASAM only

**Dependencies:** H-M1
**Source:** Phase 2A Section 1.3 (Causal Step 3), Section 1.4 (A1, A3)

---

**H-M3: Reduced Spurious Sharpness Improves Worst-Group Accuracy**

**Type:** MECHANISM
**Gate:** MUST_WORK

**Statement:** SAM-trained SSL models (rho=0.05), which exhibit reduced spurious direction sharpness vs. SGD-trained models, achieve ≥2pp higher worst-group accuracy on at least 2 of 3 benchmarks (Waterbirds/CelebA/CMNIST) without group annotations at training time, when evaluated using the standard worst-group accuracy protocol from kohpangwei/group_DRO.

**Rationale:** This is the outcome test that connects the mechanism (reduced anisotropy from H-M2) to the claimed benefit (improved worst-group accuracy). Even if H-M2 confirms anisotropy reduction, it is possible that reduced anisotropy is necessary but not sufficient for worst-group accuracy improvement (Step 4 falsifier in Phase 2A). This hypothesis determines whether the geometric intervention translates to practical robustness gains. Verifies PROVE_NEW claim #3 empirically.

**Variables:**
- Independent: Optimizer (SAM vs. SGD), SSL method, dataset
- Dependent: Worst-group accuracy (primary), average accuracy (secondary)
- Controlled: ResNet-50, identical augmentation, 200 epochs, identical linear probe protocol

**Verification Protocol:**
1. Compare worst-group accuracy of SAM-trained vs. SGD-trained SSL models after identical linear probe evaluation.
2. Compute worst-group accuracy improvement: SAM − SGD for each method × dataset combination.
3. Also compare vs. annotation-free baselines (LFR, EVaLS applied to SGD-trained SSL features) for context.
4. Report results across 9 model-dataset combinations; identify which SSL methods benefit most.
5. Statistical test: paired t-test (SAM vs. SGD across 3 datasets × 3 SSL methods, significance level 0.05).

**Success Criteria (PoC):**
- Primary: Worst-group accuracy improvement ≥ 2pp on ≥ 2/3 datasets for at least one SSL method
- Secondary: Average accuracy preserved (< 1pp drop) to confirm representation quality maintained

**Failure Response:**
- IF < 1pp improvement on all 3 datasets for all SSL methods: H-M3 fails → reduced anisotropy is not sufficient for worst-group accuracy; document finding and route to Phase 2A-Dialogue
- IF improvement on 1/3 datasets only: SCOPE — document dataset-specific conditions; narrow scope claim

**Dependencies:** H-M2
**Source:** Phase 2A Section 1.3 (Causal Step 4), Section 1.6 (P3)

---

**H-M4: ASAM Variant Behaves Consistently with Standard SAM in SSL Setting**

**Type:** MECHANISM
**Gate:** SHOULD_WORK

**Statement:** ASAM (adaptive SAM, rho=0.5) exhibits similar or better spurious anisotropy reduction and worst-group accuracy improvement compared to standard SAM (rho=0.05) in the SSL pre-training setting, confirming that the SAM family of optimizers (not a specific rho value) drives the shortcut reduction mechanism.

**Rationale:** Prof. Rex (Phase 2A) noted that standard SAM's sensitivity to rho is a known concern (DGSAM), and ASAM's adaptive normalization may behave differently. This hypothesis verifies that findings generalize across the SAM family, strengthening the claim's scope. Failure narrows but does not invalidate — standard SAM findings remain valid; only the rho-sensitivity claim is affected.

**Variables:**
- Independent: SAM variant (standard SAM rho=0.05 vs. ASAM rho=0.5)
- Dependent: Spurious anisotropy ratio, worst-group accuracy
- Controlled: Same SSL method × dataset combinations, ResNet-50, identical evaluation

**Verification Protocol:**
1. Train ASAM (rho=0.5) for all 9 SSL method × dataset combinations (same protocol as SAM in H-M2/H-M3).
2. Measure sharpness anisotropy ratio and worst-group accuracy for ASAM models.
3. Compare ASAM vs. SAM vs. SGD on both metrics.
4. Report which variant achieves greater anisotropy reduction and worst-group accuracy.

**Success Criteria (PoC):**
- Primary: ASAM shows similar or better worst-group accuracy improvement as SAM (within 1pp)
- Secondary: ASAM anisotropy reduction ≥ SAM anisotropy reduction

**Failure Response:**
- IF ASAM shows worse accuracy than SGD: SCOPE — ASAM excluded from claims; standard SAM results still valid
- IF both SAM and ASAM perform differently from expected: document rho-sensitivity as limitation

**Dependencies:** H-M3
**Source:** Phase 2A Section 1.5 (known limitations: ASAM behavior), Section 5 (open questions)

---

## 3. Execution

### 3.1 Dependency Chain

```
H-E1 → H-M1 → H-M2 → H-M3 → H-M4
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-E1 | MUST_WORK | Anisotropy ratio > 1.2 AND \|r\| > 0.5 in ≥7/9 | STOP — route to Phase 0 |
| H-M1 | MUST_WORK | Proxy precision/recall ≥ 0.6 in ≥7/9 | PIVOT — find alternative proxy |
| H-M2 | MUST_WORK | SAM ratio ≤ 0.85 × SGD AND majority drop < 2pp | Route to Phase 2A-Dialogue |
| H-M3 | MUST_WORK | ≥2pp improvement on ≥2/3 datasets for ≥1 SSL method | Route to Phase 2A-Dialogue |
| H-M4 | SHOULD_WORK | ASAM comparable to SAM (within 1pp) | SCOPE — narrow claim, continue |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-E1 | 2 weeks |
| Phase 2: Mechanisms | H-M1, H-M2, H-M3, H-M4 | 5 weeks (H-M1: W3-4, H-M2: W5, H-M3: W6, H-M4: W7) |

**Total Duration:** 7 weeks

---

## 4. Risk Analysis

### 4.1 Assumptions & Risk Mapping

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | InfoNCE landscape differs from supervised cross-entropy | von Mises-Fisher uniform distribution pressure | SAM increases shortcut reliance |
| A2 | Linear probe loss variance is valid spurious direction proxy | LFR (Ghaznavi 2023) validates on supervised ERM | P1 measurement invalid |
| A3 | Sharpness anisotropy links to shortcut reliance | SCER (Park 2025) theoretical link | Anisotropy exists but does not predict accuracy |
| A4 | Standard augmentation doesn't remove spurious content | Cross-Variant SSL requires generative augmentation | Baseline SSL already low-shortcut |
| A5 | SAM 2x cost feasible on ResNet-50 | davda54/sam widely deployed for supervised training | Resource constraint only, not scientific |

**Risk R1 — InfoNCE Landscape Assumption Failure (A1)**
- Severity: Critical
- Likelihood: Medium
- Affected: H-M2, H-M3 (SAM may increase shortcut reliance)
- Mitigation:
  1. Prevention: Design H-E1 to detect anisotropy direction before committing to SAM intervention
  2. Detection: H-M2 fake flat minima check (majority accuracy + anisotropy direction)
  3. Response: IF SAM increases anisotropy → PIVOT to negative result paper ("SAM promotes shortcuts in SSL") — still publishable

**Risk R2 — Linear Probe Proxy Invalid (A2)**
- Severity: High
- Likelihood: Low-Medium
- Affected: H-E1, H-M1, H-M2, H-M3 (all depend on proxy validity)
- Mitigation:
  1. Prevention: Validate proxy precision/recall in H-M1 before using it for intervention measurement
  2. Detection: Report precision/recall explicitly as secondary metric in H-M1
  3. Response: IF precision/recall < 0.6 → PIVOT to alternative proxy (gradient similarity, class activation maps); or use held-out group labels in evaluation-only mode

**Risk R3 — Anisotropy Does Not Predict Accuracy (A3)**
- Severity: High
- Likelihood: Low-Medium
- Affected: H-M3, H-M4 (mechanism exists but outcome fails)
- Mitigation:
  1. Prevention: Measure correlation (r, p-value) in H-E1 before proceeding
  2. Detection: H-E1 secondary criterion: |r| > 0.5
  3. Response: IF |r| < 0.2 → EXPLORE alternative landscape property (gradient alignment, loss curvature sign); document as limitation

**Risk R4 — Standard Augmentation Already Removes Spurious Content (A4)**
- Severity: Medium
- Likelihood: Low
- Affected: H-M2, H-M3 (SAM has nothing to target if baseline already low-shortcut)
- Mitigation:
  1. Prevention: Report baseline SSL worst-group accuracy; if already high (>85%), A4 may be violated
  2. Detection: Compare baseline SSL worst-group to expected ~75-80%; if higher, investigate augmentation effect
  3. Response: IF baseline already >85% → SCOPE — report as null finding; design augmentation-controlled experiment

**Risk R5 — ASAM Sensitivity (related to A5)**
- Severity: Low
- Likelihood: Medium
- Affected: H-M4 only (SHOULD_WORK gate — does not block)
- Mitigation:
  1. Prevention: Include multiple rho values for standard SAM (0.05, 0.1, 0.2)
  2. Detection: H-M4 ASAM vs. SAM comparison built into protocol
  3. Response: IF ASAM behaves differently → SCOPE — report rho-sensitivity as limitation; standard SAM results stand

### 4.2 Risk Summary

| ID | Risk | Source | Severity | Affected | Strategy |
|----|------|--------|----------|----------|----------|
| R1 | InfoNCE landscape assumption fails — SAM increases shortcuts | A1 | Critical | H-M2, H-M3 | Design H-E1 to detect direction; pivot to negative-result paper |
| R2 | Linear probe proxy invalid (precision/recall < 0.6) | A2 | High | All H-* | Validate in H-M1; pivot to alternative proxy |
| R3 | Anisotropy does not predict worst-group accuracy (\|r\| < 0.2) | A3 | High | H-M3, H-M4 | H-E1 correlation check gates progression |
| R4 | Baseline SSL already low-shortcut (augmentation removes spurious) | A4 | Medium | H-M2, H-M3 | Verify baseline performance before SAM comparison |
| R5 | ASAM behaves differently from standard SAM | A5 | Low | H-M4 | SHOULD_WORK gate — failure narrows scope, does not block |

**Critical: 1 | High: 2 | Medium: 1 | Low: 1**

### 4.3 Baseline Failure Patterns → Additional Risks

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| Group DRO requires group labels | Annotation-free constraint may be undermined if proxy fails | H-M1 proxy validation gates all downstream measurement |
| Cross-Variant SSL uses generative augmentation | Different mechanism — augmentation confound | Standard augmentation controlled; generative augmentation explicitly excluded |
| LFR/EVaLS operate on fixed representations | Post-hoc comparison may show larger gains than optimizer-level | Include LFR/EVaLS as baselines in H-M3 for direct comparison |

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root: Foundation]
    H-E1  (EXISTENCE — no dependencies, MUST_WORK)
         │
         ▼ Gate 1: MUST PASS → continue; FAIL → STOP
[Level 1 - Mechanism: Proxy Validity]
    H-M1  (MECHANISM — depends on H-E1, MUST_WORK)
         │
         ▼ Gate 2a: MUST PASS → continue; FAIL → PIVOT proxy
[Level 2 - Mechanism: SAM Intervention]
    H-M2  (MECHANISM — depends on H-M1, MUST_WORK)
         │
         ▼ Gate 2b: MUST PASS → continue; FAIL → Phase 2A-Dialogue
[Level 3 - Mechanism: Accuracy Outcome]
    H-M3  (MECHANISM — depends on H-M2, MUST_WORK)
         │
         ▼ Gate 2c: MUST PASS → continue; FAIL → Phase 2A-Dialogue
[Level 4 - Mechanism: SAM Variant]
    H-M4  (MECHANISM — depends on H-M3, SHOULD_WORK)
         │
         ▼ Gate 3: SHOULD PASS → stronger claim; FAIL → SCOPE (narrow)

═══════════════════════════════════════════════════════════
Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4
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

### 5.3 Verification Timeline (Gantt)

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis     │ W1-2   │ W3-4   │ W5     │ W6     │ W7
─────────────────────┼────────┼────────┼────────┼────────┼────────
PHASE 1: Foundation
  H-E1               │ ██████ │        │        │        │
  [Gate 1]           │      ◆ │        │        │        │
─────────────────────┼────────┼────────┼────────┼────────┼────────
PHASE 2: Mechanisms
  H-M1               │        │ ██████ │        │        │
  H-M2               │        │      ◆ │ ████   │        │
  H-M3               │        │        │      ◆ │ ████   │
  H-M4               │        │        │        │      ◆ │ ████
  [Gate 2 final]     │        │        │        │        │     ◆
─────────────────────┼────────┼────────┼────────┼────────┼────────
═══════════════════════════════════════════════════════════════════
Legend: ██ = Active work | ◆ = Gate decision point
Total Duration: 7 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  CRITICAL PATH ANALYSIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Critical Path: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

Total Duration: 7 weeks
  Formula: 2 (H-E1) + 2 (H-M1) + 1 (H-M2) + 1 (H-M3) + 1 (H-M4)

Slack Available: 0 weeks (all sequential — strict causal chain)

Note: H-M1 runs alongside H-E1 measurement (W3-4) since same
training runs are reused — proxy validation is a secondary analysis
on existing SGD models, not additional training.
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
- Condition: 0 (skipped — no testable boundary conditions)

Verification Phases: 2
1. Foundation (H-E1): 2 weeks
2. Mechanisms (H-M1 to H-M4): 5 weeks

Compute: 9 SGD SSL training runs (Phase 1) + 9 SAM + 9 ASAM training runs (Phase 2) = 27 training runs total
Each run: ResNet-50, 200 epochs, GPU hours ~6-12h per run (estimated)
Total GPU budget: ~160-320 GPU hours

Total Duration: 7 weeks
Critical Path Length: 7 weeks
Execution Mode: Sequential chain (MUST_WORK gates enforce order)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5.6 Execution Order

**Step 1:** Execute H-E1 — Train 9 SGD SSL models, measure sharpness anisotropy (Week 1-2)
**Step 2:** Evaluate Gate 1 → If anisotropy ratio > 1.2 AND |r| > 0.5: PASS; else STOP
**Step 3:** Execute H-M1 — Validate linear probe proxy precision/recall on same 9 models (Week 3-4, concurrent analysis)
**Step 4:** Evaluate Gate 2a → If precision/recall ≥ 0.6: PASS; else PIVOT
**Step 5:** Execute H-M2 — Train 9 SAM + 9 ASAM models, measure anisotropy reduction (Week 5)
**Step 6:** Evaluate Gate 2b → If SAM ratio ≤ 0.85 × SGD AND majority drop < 2pp: PASS; else Phase 2A-Dialogue
**Step 7:** Execute H-M3 — Evaluate worst-group accuracy improvement (Week 6, same SAM runs)
**Step 8:** Evaluate Gate 2c → If ≥2pp improvement on ≥2/3 datasets: PASS; else Phase 2A-Dialogue
**Step 9:** Execute H-M4 — Compare ASAM vs. SAM (Week 7, same ASAM runs from H-M2)
**Step 10:** Evaluate Gate 3 → SHOULD_WORK; failure narrows scope only

---

## 6. Dialectical Analysis

### 6.1 Thesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  THESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Core Claim: SAM during SSL pre-training reduces spurious sharpness
anisotropy and improves worst-group accuracy ≥2pp on ≥2/3 benchmarks
without group annotations.

Supporting Evidence:
1. Theoretical (Gatmiry 2024): SAM promotes sharpness minimization →
   spurious features (lower-rank, simpler) correspond to sharper loss
   directions → SAM preferentially flattens them.
2. Empirical precedent (G2-SAM, Ji 2025): Group-wise SAM improves
   worst-group accuracy in supervised setting via group sharpness reduction.
3. InfoNCE landscape argument: Unlike supervised cross-entropy (single rank-1
   attractor), InfoNCE creates uniform distribution pressure — no mechanism
   for rank-1 simplicity bias to dominate (Dr. Nova, Exchange 7).
4. Annotation-free proxy validity: LFR (Ghaznavi 2023) validates loss
   variance proxy for spurious direction identification on Waterbirds/CelebA.

Strengths:
- Two independent contributions (diagnostic P1 + intervention P3): scientifically
  valuable regardless of which succeeds
- All experimental components exist (pyssl + davda54/sam + group_DRO)
- Distinguishable failure modes (fake flat minima detectable via majority accuracy)
- Three distinct falsifiable predictions with quantitative thresholds

Expected Outcomes:
- P1: Anisotropy ratio > 1.2, |r| > 0.5 in ≥7/9 model-dataset pairs
- P2: SAM ratio ≤ 0.85 × SGD, majority drop < 2pp in ≥2/3 datasets
- P3: ≥2pp worst-group accuracy improvement on ≥2/3 datasets for ≥1 SSL method
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Antithesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ANTITHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Null Hypothesis (H0): No significant difference in worst-group accuracy
between SAM-trained and SGD-trained SSL models (<1pp on all datasets).
Sharpness anisotropy does not correlate with worst-group accuracy (|r| < 0.2).

Counter-Arguments:
1. Gatmiry (2024) proves SAM promotes rank-1/simplicity bias in supervised
   cross-entropy. Spurious features are simpler (lower-rank) than core features.
   If this transfers to InfoNCE, SAM INCREASES shortcut reliance — opposite of thesis.
2. Linear probe loss variance proxy may have high false positive rate: hard samples
   (non-minority group with high loss due to difficult instances) confound the proxy.
   If precision/recall < 0.6, all anisotropy measurements are directionally invalid.
3. DGSAM (Song 2025) shows fake flat minima: SAM may flatten all directions equally,
   producing uniform sharpness reduction without selective spurious direction targeting.
4. Standard augmentation (crop, color jitter) may already randomize enough spurious
   content that baseline SSL shortcut reliance is lower than assumed.

Potential Failure Points:
- R1 (Critical): InfoNCE landscape → SAM promotes rank-1 → MORE shortcuts
- R2 (High): Proxy invalid → anisotropy measurement is directionally wrong
- R3 (High): Anisotropy exists but does not predict worst-group accuracy

Conditions Under Which H0 Would Be Supported:
- Anisotropy ratio ≈ 1.0 across all 9 SSL model-dataset combinations (H-E1 fails)
- SAM anisotropy ratio ≥ SGD ratio at convergence (H-M2 fails — opposite direction)
- <1pp worst-group accuracy improvement on all 3 datasets for all SSL methods (H-M3 fails)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.3 Synthesis

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SYNTHESIS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Balanced Assessment:

H-SAMSSL-v1 presents a well-structured, testable claim grounded in
convergent theoretical motivation. The InfoNCE landscape argument
(Exchange 7, Dr. Nova) provides a plausible mechanism distinct from
Gatmiry's supervised result. However, the antithesis is equally
well-grounded: the Gatmiry rank-1 simplicity bias is a proven theorem,
and whether InfoNCE's uniform distribution pressure is sufficient to
prevent it from applying to SSL is empirically unresolved.

Resolution Path:
1. H-E1 (Foundation): Establishes whether anisotropy exists at all
   — distinguishes between "mechanism doesn't exist" and "exists but
   SAM can't exploit it"
2. H-M1 (Proxy validity): Gates all intervention measurements on
   measurement instrument quality — prevents false positives
3. H-M2 (Direction test): Directly tests thesis vs. antithesis on
   SAM's effect direction — resolves the Gatmiry conflict empirically
4. H-M3 (Outcome test): Connects mechanism to practical benefit
5. H-M4 (Robustness): Strengthens generalizability claim

Conditions for Thesis Support:
- H-E1: Anisotropy ratio > 1.2, |r| > 0.5
- H-M2: SAM ratio ≤ 0.85 × SGD, majority accuracy preserved
- H-M3: ≥2pp improvement on ≥2/3 datasets

Conditions for Antithesis Support:
- H-E1 fails (no anisotropy) — mechanism does not apply to SSL InfoNCE
- H-M2 fails (SAM increases anisotropy) — Gatmiry bias transfers
- Both publishable: negative result identifies why SSL shortcut
  reduction via optimizer intervention fails

Nuanced Outcome Possibilities:
1. Full Support: All MUST_WORK gates pass → SAM-SSL as shortcut
   reduction method confirmed; both diagnostic and intervention valid
2. Partial Support (Diagnostic only): H-E1/H-M1 pass, H-M3 fails →
   anisotropy measurement valid but SAM intervention insufficient;
   paper: "SSL loss landscape geometry as shortcut diagnostic"
3. No Support: H-E1 fails → anisotropy mechanism does not exist in
   InfoNCE SSL; paper: "Null result: SSL loss landscape is not
   anisotropically structured along spurious directions"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Existence | SSL anisotropy exists along spurious directions | May be artifact / uniform curvature | H-E1 test with quantitative threshold |
| Proxy Validity | LFR proxy transfers from supervised to SSL | False positive rate may be high in SSL | H-M1 precision/recall validation |
| Mechanism Direction | SAM preferentially flattens spurious directions in InfoNCE | Gatmiry rank-1 bias makes SAM increase shortcuts | H-M2 direction test (definitive empirical answer) |
| Outcome Translation | Reduced anisotropy → better worst-group accuracy | Anisotropy necessary but not sufficient | H-M3 direct accuracy comparison |
| Generalizability | SAM family (incl. ASAM) shows consistent results | rho-sensitivity may limit replication | H-M4 ASAM variant (SHOULD_WORK) |

**Overall Robustness Score:** High — all failure modes are distinguishable; scientific value preserved under any outcome.

**Confidence in Verification Plan:** 0.72 (matches Phase 2A confidence level)

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** H-SAMSSL-v1 — SAM during SSL pre-training reduces spurious sharpness anisotropy → improves worst-group accuracy ≥2pp on ≥2/3 benchmarks (annotation-free)
- ID: H-SAMSSL-v1, Confidence: 0.72

**Verification Structure:**
- Mode: Incremental (62% scope reduction from Phase 2A Established Facts)
- Sub-Hypotheses: 5 total (H-E: 1, H-M: 4, H-C: 0)
- Phases: 2 phases over 7 weeks
- Critical Gates: 4 MUST_WORK + 1 SHOULD_WORK

**Risk Assessment:** High (1 Critical, 2 High risks identified)
- Primary concerns: InfoNCE landscape assumption (A1), linear probe proxy validity (A2)

**Immediate Action:** Begin Phase 1 with H-E1 — train 9 SGD SSL models and measure sharpness anisotropy

### 7.2 Conclusions

**Key Achievements:**
- 5 sub-hypotheses across 2 phases, fully decomposing the 4-step causal chain
- H0 addressed: SAM no-effect on worst-group accuracy; sharpness anisotropy no-correlation
- Two-part structure ensures scientific value in all outcomes (diagnostic + intervention)

**Verification Execution Order:**

**Phase 1: Foundation** (2 weeks)
- H-E1: Confirm sharpness anisotropy exists in SGD-trained SSL models; validate correlation with worst-group accuracy
- Gate 1: MUST PASS — failure stops chain and routes to Phase 0

**Phase 2: Core Mechanisms** (5 weeks)
- H-M1: Validate linear probe loss variance proxy precision/recall ≥ 0.6 (Week 3-4, concurrent with H-E1 models)
- H-M2: Confirm SAM reduces spurious anisotropy by ≥15% without fake flat minima (Week 5)
- H-M3: Confirm ≥2pp worst-group accuracy improvement on ≥2/3 datasets (Week 6)
- H-M4: Confirm ASAM variant behaves consistently with standard SAM (Week 7)
- Gate 2: H-M1/H-M2/H-M3 must pass; H-M4 failure narrows scope only

**Critical Decision Points:**

1. **Gate 1 (H-E1):** MUST PASS
   - FAIL → STOP entire chain; route to Phase 0 for new hypothesis direction
   - PASS → Proceed to Phase 2

2. **Gate 2a (H-M1 Proxy):** MUST PASS
   - FAIL → PIVOT to alternative spurious direction identification method

3. **Gate 2b (H-M2 Direction):** MUST PASS — resolves Gatmiry conflict empirically
   - FAIL (SAM increases anisotropy) → Route to Phase 2A-Dialogue for hypothesis revision

4. **Gate 2c (H-M3 Outcome):** MUST PASS
   - FAIL (< 1pp improvement) → Route to Phase 2A-Dialogue; document diagnostic contribution separately

**Open Questions:**
- Does Gatmiry's rank-1 simplicity bias apply to InfoNCE objectives? (P1/P2 answers empirically)
- Does linear probe loss variance precision/recall hold in SSL representations (not just supervised ERM)?
- Does ASAM (adaptive SAM) perform differently from standard SAM in SSL setting?
- Does UrbanCars (multi-attribute) behave differently? (Extended analysis if primary results positive)

**Recommendations:**

1. **Immediate Actions:**
   - Set up measurement infrastructure: pyssl + davda54/sam + kohpangwei/group_DRO + izmailovpavel/spurious_feature_learning
   - Begin H-E1 SGD training runs (9 models) to establish baseline
   - Implement anisotropy measurement: SAM perturbation loss ratio along top-25% high-loss-variance directions vs. 100 random directions

2. **Resource Allocation:**
   - Allocate 7 weeks for critical path
   - Reserve GPU buffer (~320 GPU hours) for 27 training runs (9 SGD + 9 SAM + 9 ASAM)
   - Checkpoint every 50 epochs for anisotropy tracking

3. **Failure Management:**
   - Document all gate failures with quantitative evidence
   - Execute PIVOT/SCOPE strategies as specified per hypothesis
   - Preserve partial results — diagnostic (P1) is independent of intervention (P3)

### 7.3 Appendices

**Appendix A: Phase 2A Reference**
- Source: docs/youra_research/03_refinement.yaml (ID: H-SAMSSL-v1)
- Convergence: 10 exchanges, self-play Tikitaka loop; all 6 criteria met at Exchange 10

**Appendix B: MCP Tool Usage Summary**
- Total MCP calls: 3 (mcp__clearThought__scientificmethod: H-E1 hypothesis+experiment, H-M1-2 integrated, H-M3-4 integrated)
- Mode: Incremental (Phase 2A data pre-seeded)
- No Exa search required (Phase 2A had sufficient literature context)

**Appendix C: Scope Reduction**
- Total claims: 8 | BUILD_ON: 5 | PROVE_NEW: 3
- Scope reduction: 62% — only 3 claims require new experimental verification
