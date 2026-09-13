---
hypothesis_title: "Backbone Spurious Encoding Reduction (BSER)"
hypothesis_id: "H-BSER-v1"
generated_at: "2026-08-05"
workflow: "phase2b-planning"
schema_version: "2.0"
research_mode: "incremental"
stepsCompleted:
  - "step-00-init-environment"
  - "step-01-init-parsing"
  - "step-02-input-hypothesis"
  - "step-03-hypothesis-generation"
  - "step-04-hypothesis-inventory"
  - "step-05-risk-analysis"
  - "step-06-dependency-graph"
  - "step-07-timeline-planning"
  - "step-08-dialectical-analysis"
  - "step-09-summary"
  - "step-10-finalize"
status: complete
completedAt: "2026-08-05"
---

# Verification Plan: Backbone Spurious Encoding Reduction (BSER)

**Date:** 2026-08-05
**Hypothesis ID:** H-BSER-v1
**Confidence:** 0.72
**Total Hypotheses:** 5 (H-P0, H-M1, H-M2, H-M3, H-P2)

---

## 0. Established Facts & Scope Reduction

**Scope Reduction: 33%** (6 BUILD_ON claims skipped, 3 PROVE_NEW claims targeted)

### Established Facts (BUILD_ON — DO NOT RE-VERIFY)

| Claim | Evidence |
|-------|----------|
| DFR backbone weights ≡ ERM backbone (frozen in DFR protocol) | Kirichenko 2022; Izmailov repo; Exchanges 4, 12 |
| sklearn L-BFGS C=1e9 on frozen layer4 (D=2048) is established probing convention | Kirichenko 2022, Murotkar 2024, Izmailov dfr_evaluate_spurious.py |
| ERM backbone encodes strong spurious background (~85% s-DFR proxy accuracy) | Izmailov 2022 s-DFR analysis |
| 12 author-released ResNet-50 checkpoints exist (3 seeds × 4 methods) | izmailovpavel/spurious_feature_learning GitHub |
| Full-model gradient cosine similarity is not discriminative for spurious comparison (h-e1 FAIL: Cohen's d=-0.330) | Serena memory: h-e1 failure record |
| Head-only Hessian λ_max is not a valid curvature proxy (h-m2 LIMITATION) | Serena memory: h-m2 limitation record |

### New Claims (PROVE_NEW — Phase 2B targets)

| Claim | Target Hypothesis |
|-------|------------------|
| Per-method, per-seed spurious probe accuracy for 12 checkpoints not reported in existing work | H-P0 baseline measurement |
| GroupDRO training reduces backbone spurious encoding (probe acc < ERM) | H-M1→H-M2→H-M3 causal chain, H-P1 test |
| Spurious probe accuracy correlates negatively with WGA across distinct-backbone checkpoints | H-P2 (exploratory; full baseline comparison deferred to Phase 5) |

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under ResNet-50 checkpoints from izmailovpavel/spurious_feature_learning (3 seeds × 4 methods, fully trained on Waterbirds WILDS), if we compare GroupDRO-trained backbones to ERM-trained backbones using sklearn L-BFGS linear probe accuracy predicting background attribute (land/water, group_array) from frozen layer4 features (D=2048) on the full Waterbirds test set, then GroupDRO backbones exhibit significantly lower spurious probe accuracy (paired one-sided t-test, p<0.05, n=3 seeds), because GroupDRO's group-balanced worst-group loss forces gradient updates through all layers to reduce reliance on spurious background features, while DFR (head-only retraining) leaves backbone spurious encoding unchanged relative to ERM.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in spurious attribute linear probe accuracy between GroupDRO-trained and ERM-trained ResNet-50 layer4 features on Waterbirds WILDS (one-sided paired t-test: p >= 0.05 for GroupDRO < ERM direction).

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Waterbirds WILDS (standard) | Canonical spurious correlation benchmark; background (land/water) is spurious attribute; all 12 checkpoints trained/evaluated on this dataset |
| **Model** | ResNet-50 (12 checkpoints) | Layer4 is final backbone representation before classification head; standard probing point per Alain & Bengio 2016 |

**Dataset Details:**
- Source: WILDS benchmark (Koh et al. 2021)
- Path: `/home/PrayPrey/.wilds_cache/waterbirds_v1.0`
- Background extraction: `background_label = group_array % 2` (0=land, 1=water)

**Model Details:**
- Type: CNN feature extractor (backbone only — no head in feature extraction)
- Source: izmailovpavel/spurious_feature_learning GitHub (12 checkpoints)
- Feature extraction: `model.layer4 → AdaptiveAvgPool2d(output_size=(1,1)) → flatten → D=2048`

### 1.4 Baseline Methods

| Method | Performance | Dataset | Notes |
|--------|-------------|---------|-------|
| ERM (Empirical Risk Minimization) | WGA=0.72, spurious probe acc≈0.85 | Waterbirds WILDS | Positive control: high spurious encoding baseline |
| GroupDRO (Sagawa et al. 2019) | WGA=0.88 | Waterbirds WILDS | Primary comparison: backbone-changing method |
| SAM (Sharpness-Aware Minimization) | WGA=0.74 | Waterbirds WILDS | Exploratory: H-P1b, no pre-registered threshold |
| DFR (Kirichenko et al. 2022) | WGA=0.91 | Waterbirds WILDS | Backbone-preserving control: backbone ≡ ERM by design |
| Random baseline | acc≈0.50 | — | Binary background classification chance level |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | DFR backbone weights in released checkpoints are numerically identical to ERM at same seed (frozen backbone in DFR protocol) | Kirichenko 2022 DFR protocol; Izmailov repo; Exchanges 4, 12 | DFR cannot be excluded from backbone comparison; H-P1 must include DFR as 4th backbone condition |
| A2 | Background attribute (land/water) is linearly decodable from ERM layer4 features at above-chance accuracy (probe acc > 0.6) | Izmailov 2022 s-DFR proxy ~85%; if probe acc is near chance for all methods, metric lacks discriminative power | Probe methodology fails; must examine earlier layers or use non-linear probes |
| A3 | Within-method probe accuracy variance across 3 seeds is small enough for paired t-test to have meaningful power (expected CV < 0.05) | Linear probe accuracy bounded [0,1]; deterministic function of fixed features + stable sklearn probe; expected CV << 1 vs h-e1's CV=3.98 | Cohen's d threshold cannot be pre-set; all results reported as SUGGESTIVE; power analysis post-hoc |
| A4 | 12 released checkpoints represent genuinely different training methods (not identical due to bugs or shared random states) | WGA differences (ERM=0.72, GroupDRO=0.88, DFR=0.91) confirm differentiation; Izmailov 2022 validates | Checkpoint identity verification needed before any analysis |
| A5 | group_array in Waterbirds WILDS encodes background attribute (land/water) as binary label usable as probe target | Sagawa 2019: group_array(0=landbird-land, 1=landbird-water, 2=waterbird-land, 3=waterbird-water) → background = group_array % 2 | Label extraction code incorrect; probe predicts wrong attribute |

### 1.6 Research Gap & Novelty

**Gap:** Per-method, per-seed spurious attribute linear probe accuracy for 12 Waterbirds checkpoints is NOT reported in any existing publication. Izmailov 2022 reports aggregate s-DFR proxy (different task — background as head retraining target); Kirichenko 2022 uses WGA as indirect measure. No paper reports layer4 probe accuracy per-method per-seed with statistical testing.

**Key Innovation:** First systematic per-method, per-seed spurious attribute linear probe accuracy measurement with pre-registered statistical tests (paired t-test + Pearson correlation) and mechanistic prediction (backbone-changing vs backbone-preserving method distinction). Distinguishes backbone-level (GroupDRO, SAM) vs head-level (DFR) robustification mechanisms using quantitative spurious feature decodability.

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| H-P0 | EXISTENCE (Sanity Check) | MUST_WORK | None | READY |
| H-M1 | MECHANISM | MUST_WORK | H-P0 | NOT_STARTED |
| H-M2 | MECHANISM | SHOULD_WORK | H-M1 | NOT_STARTED |
| H-M3 | MECHANISM | MUST_WORK | H-M2 | NOT_STARTED |
| H-P2 | MECHANISM (Exploratory) | SHOULD_WORK | H-M3 | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-P0: DFR Backbone Identity Sanity Check**

**Type:** EXISTENCE (Sanity Check — gates all backbone comparisons)

**Statement:** Under ResNet-50 checkpoints from izmailovpavel/spurious_feature_learning, if we extract layer4 features (D=2048) from DFR and ERM checkpoints at matching seeds for 50 Waterbirds test images, then mean cosine similarity ≥ 0.9999 for all 3 seed pairs, because DFR protocol explicitly freezes backbone and retrains only the classification head.

**Rationale:** This is the architectural prerequisite for the entire hypothesis. DFR's mechanism is backbone-preservation; if H-P0 fails (similarity < 0.999), DFR must be treated as an independent backbone condition in H-P1/P2, fundamentally changing the experimental design. Prof. Pax (Exchange 4) identified this as the critical architectural insight.

**Variables:**
- Independent: Checkpoint pair type (DFR vs ERM at same seed)
- Dependent: Mean cosine similarity of layer4 features across 50 test images
- Controlled: Seed (matched pairs), test images (fixed 50), extraction protocol

**Verification Protocol:**
1. Download 12 checkpoints from izmailovpavel/spurious_feature_learning (HuggingFace Hub).
2. For each seed in {1,2,3}: load DFR and ERM checkpoints, set model.eval() + torch.no_grad().
3. Forward pass 50 fixed Waterbirds test images through model.layer4 → AdaptiveAvgPool2d(1,1) → flatten to [50, 2048].
4. Compute mean cosine_similarity(dfr_feat[i], erm_feat[i]) for i=1..50; report per-seed mean and variance.
5. Pass criterion: mean cosine similarity ≥ 0.9999 for ALL 3 seed pairs.

**Success Criteria:**
- PASS: Mean cosine similarity ≥ 0.9999 for all 3 seed pairs AND variance < 1e-6
- FAIL (branching): Cosine similarity < 0.999 → DFR includes backbone fine-tuning; must include DFR as 4th backbone condition in H-P1

**Gate:** MUST_WORK — fails interpretation of all downstream hypotheses

**Dependencies:** None (foundation)

**Source:** Phase 2A Section 1.6 Prediction P0; Exchange 12 (Prof. Rex)

---

**H-M1: GroupDRO Minority Group Upweighting Creates Group-Balanced Gradient Signal**

**Type:** MECHANISM (Step 1 of 3-step causal chain)

**Statement:** Under GroupDRO training on Waterbirds WILDS, the worst-group loss objective upweights minority groups (land-bird on land background, water-bird on water background — background-atypical examples), creating a group-balanced effective loss signal during backbone training that differs from ERM's uniform sample weighting.

**Rationale:** This is the initiating mechanism: GroupDRO's training distribution fundamentally differs from ERM by upweighting background-atypical examples. Without this differential signal, no backbone-level change would be expected. Supported by Sagawa 2019 GroupDRO paper and Exchange 3 (Dr. Sage), Exchange 6 (Prof. Vera).

**Variables:**
- Independent: Training objective (GroupDRO worst-group loss vs ERM cross-entropy)
- Dependent: Effective loss weighting on minority groups (land-bird-land, water-bird-water)
- Controlled: Architecture (ResNet-50), dataset (Waterbirds WILDS), checkpoint source (izmailovpavel)

**Verification Protocol:**
1. Confirm via Sagawa 2019 GroupDRO formulation: worst-group loss explicitly upweights worst-performing groups.
2. Identify minority groups in Waterbirds: group_array indices where bird species and background are non-correlated (land-bird on water, water-bird on land).
3. Verify from existing literature that GroupDRO's WGA improvement (0.88 vs ERM 0.72) implies successful minority group performance improvement — consistent with upweighting mechanism.
4. Treat as established theoretical mechanism with empirical consequence measured in H-M2/H-M3.

**Success Criteria:**
- Primary: Confirmed by Sagawa 2019 theoretical derivation (no new experiment needed — BUILD_ON theoretical foundation)
- Secondary: GroupDRO WGA improvement (0.88 vs ERM 0.72 from Izmailov 2022) consistent with mechanism

**Gate:** MUST_WORK — if GroupDRO mechanism doesn't create differential gradient signal, backbone change (H-M2) is unmotivated

**Dependencies:** H-P0 (establishes DFR ≡ ERM backbone, confirming backbone-changing vs preserving distinction)

**Source:** Phase 2A Section 1.3 Causal Step 1; Sagawa et al. 2019

---

**H-M2: Group-Balanced Gradient Propagates Through All Backbone Layers**

**Type:** MECHANISM (Step 2 of 3-step causal chain)

**Statement:** Under GroupDRO training on Waterbirds WILDS, the group-balanced gradient signal from the worst-group loss propagates through all ResNet-50 layers including layer4, modifying weight updates to reduce the predictive utility of spurious background features for classification loss minimization.

**Rationale:** This is the propagation mechanism linking training objective to backbone representation. GroupDRO modifies the effective training distribution seen by ALL layers (Prof. Pax, Exchange 8). Supported by representation learning theory: training objective shapes representation. The key question answered by H-M3: does this propagation actually reduce background decodability at layer4?

**Variables:**
- Independent: GroupDRO vs ERM training objective (manifests as different effective gradient signal at all layers)
- Dependent: Gradient signal modification at layer4 (proxied by resulting probe accuracy difference in H-M3)
- Controlled: Architecture, dataset, checkpoint source

**Verification Protocol:**
1. Establish theoretical basis: GroupDRO loss gradient ∂L/∂θ_L4 differs from ERM's uniform-weighted gradient by construction (group upweighting changes batch composition seen by all layers).
2. Verify empirically through H-M3 outcome: if layer4 spurious probe accuracy differs between GroupDRO and ERM, gradient propagation to layer4 is confirmed.
3. Falsification check: if spurious probe accuracy is unchanged despite different training objectives, gradient signal did not propagate effectively to backbone (or was counteracted by other forces).

**Success Criteria:**
- Primary: H-M3 CONFIRMED (proxy evidence of gradient propagation to layer4)
- Secondary: Cohen's d > 0.5 in H-M3 result (magnitude consistent with meaningful gradient modification)

**Gate:** SHOULD_WORK — failure narrows but does not invalidate (could be that only head benefits)

**Dependencies:** H-M1 (establishes that differential gradient signal is created at training time)

**Source:** Phase 2A Section 1.3 Causal Step 2; Exchange 8 (Prof. Pax)

---

**H-M3: Reduced Spurious Gradient Signal in Layer4 → Lower Background Linear Decodability**

**Type:** MECHANISM (Step 3 of 3-step causal chain; implements H-P1 primary test)

**Statement:** Under ResNet-50 checkpoints from izmailovpavel/spurious_feature_learning (3 seeds × GroupDRO and ERM), GroupDRO-trained layer4 features exhibit significantly lower background (land/water) linear decodability than ERM-trained layer4 features, measured as sklearn L-BFGS probe accuracy on the full Waterbirds WILDS test set, tested via one-sided paired t-test (p<0.05, n=3 seeds).

**Rationale:** This is the primary empirical test of the causal chain. If GroupDRO backbone-level gradient propagation (H-M2) reduces background decodability, it must manifest as measurably lower probe accuracy at layer4. This test uses the stable, bounded [0,1] probe metric (vs h-e1's unstable gradient cosine similarity). Park 2025 SCER demonstrates spurious representation directions can be regularized; H-M3 tests whether GroupDRO implicitly achieves this.

**Variables:**
- Independent: Training method (GroupDRO vs ERM, 3 pairs matched by seed)
- Dependent: Spurious attribute probe accuracy (sklearn L-BFGS predicting group_array%2 from layer4 features)
- Controlled: Probe architecture (L-BFGS C=1e9), feature layer (layer4 D=2048), test set (full Waterbirds WILDS), checkpoint source

**Verification Protocol:**
1. Prerequisite: H-P0 must PASS (confirms DFR ≡ ERM backbone; H-M3 then tests ERM/SAM/GroupDRO backbone comparison).
2. For each seed in {1,2,3}: load GroupDRO and ERM checkpoints; model.eval() + torch.no_grad().
3. Forward pass FULL Waterbirds WILDS test set through model.layer4 → AdaptiveAvgPool2d(1,1) → flatten → [N_test, 2048] feature matrix.
4. Extract background_label = group_array % 2 from WILDS metadata (0=land, 1=water).
5. Fit sklearn LogisticRegression(solver='lbfgs', C=1e9, max_iter=1000, random_state=42) on (features, background_labels); record probe_acc = probe.score(features, background_labels) per checkpoint.
6. Statistical test: scipy.stats.ttest_rel(erm_accs, groupdro_accs, alternative='greater'); compute Cohen's d = (ERM_mean - GroupDRO_mean) / pooled_std.
7. Exploratory H-P1b: repeat for SAM vs ERM; report direction and Cohen's d only (no pre-registered threshold).

**Success Criteria:**
- CONFIRMED: p < 0.05 one-sided AND Cohen's d > 0 (direction correct)
- SUGGESTIVE: p < 0.10 one-sided AND Cohen's d > 0.5
- REJECTED: GroupDRO mean ≥ ERM mean (wrong direction) OR p ≥ 0.10 with Cohen's d < 0.2
- Also verify: ERM mean probe acc > 0.6 (confirms metric discriminability — A2 validation)

**Gate:** MUST_WORK — core empirical test of the hypothesis

**Dependencies:** H-M1, H-M2 (theoretical chain motivating the measurement)

**Source:** Phase 2A Section 1.6 Prediction P1; Park 2025 SCER; Izmailov 2022 s-DFR

---

**H-P2: Spurious Probe Accuracy Correlates Negatively with WGA**

**Type:** MECHANISM (Exploratory correlation; partial Phase 5 preview)

**Statement:** Under 9 distinct-backbone ResNet-50 checkpoints (ERM×3 + SAM×3 + GroupDRO×3) from izmailovpavel/spurious_feature_learning, spurious attribute probe accuracy (layer4 background decodability) correlates negatively with WGA, measured as Pearson r < -0.5 with bootstrapped 95% CI upper bound < 0 (one-sided p < 0.05, n=9 checkpoints).

**Rationale:** If spurious probe accuracy predicts WGA, researchers could estimate WGA without group-labeled validation sets — a practical diagnostic tool. H-P2 establishes the correlation signal at PoC scale; Phase 5 will perform full baseline comparison. This was identified as a field-relevant finding regardless of H-P1 outcome (Dr. Sage, Exchange 14).

**Variables:**
- Independent: Spurious probe accuracy per checkpoint (from H-M3 measurement, 9 distinct-backbone checkpoints)
- Dependent: WGA per checkpoint (from Izmailov 2022 Table 1 or re-measured from checkpoints)
- Controlled: Checkpoint source (fixed 9 from ERM×3, SAM×3, GroupDRO×3; DFR excluded as backbone ≡ ERM)

**Verification Protocol:**
1. Prerequisite: H-M3 must complete (provides spurious probe accuracies for all 9 checkpoints).
2. Collect WGA values for 9 checkpoints from Izmailov 2022 Table 1 (ERM: 0.72/seed, GroupDRO: 0.88/seed, SAM: 0.74/seed — per-seed values).
3. Compute Pearson r = corr(spurious_probe_acc[9], wga[9]) using scipy.stats.pearsonr.
4. Bootstrap CI: resample 9 (probe_acc, WGA) pairs with replacement 1000×; compute r each time; report 95% CI.
5. One-sided p-value for H0: r ≥ 0.

**Success Criteria:**
- PRIMARY: Pearson r < -0.5 AND bootstrapped 95% CI upper bound < 0
- SECONDARY: r < -0.3 with CI including r < 0 (suggestive correlation)
- FAIL: r ≥ -0.3 or bootstrap CI includes r ≥ 0

**Gate:** SHOULD_WORK — exploratory; full baseline comparison deferred to Phase 5

**Dependencies:** H-M3 (provides probe accuracies for all 9 checkpoints)

**Source:** Phase 2A Section 1.6 Prediction P2; Exchange 14 (Dr. Sage)

---

## 3. Execution

### 3.1 Dependency Chain
```
H-P0 → H-M1 → H-M2 → H-M3 → H-P2
(sanity) (theory) (theory) (primary test) (correlation)
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| H-P0 | MUST_WORK | Cosine sim ≥ 0.9999 for all 3 seed pairs | STOP: DFR must be treated as 4th backbone; redesign H-M3 comparison |
| H-M1 | MUST_WORK | GroupDRO worst-group loss creates group-balanced gradient (theory + WGA evidence) | STOP: Mechanism unmotivated; reassess hypothesis |
| H-M2 | SHOULD_WORK | H-M3 confirms gradient propagation (proxy evidence) | DOCUMENT: Limitation — mechanism propagation not confirmed |
| H-M3 | MUST_WORK | GroupDRO probe acc < ERM; p<0.05 or SUGGESTIVE | PIVOT: If REJECTED, WGA improvement is head-only; document and route to Phase 5 |
| H-P2 | SHOULD_WORK | Pearson r < -0.5, bootstrap CI upper < 0 | DOCUMENT: Exploratory; full comparison deferred to Phase 5 |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 1: Foundation | H-P0 (sanity check) + H-M1 (theory confirmation) | 2 weeks |
| Phase 2: Core Mechanisms | H-M2 (propagation) + H-M3 (primary probe test) | 3 weeks |
| Phase 3: Exploratory | H-P2 (WGA correlation) | 1 week |

**Total Duration:** 5 weeks (sequential chain)

---

## 4. Risk Analysis

### 4.1 Assumption-to-Risk Mapping

**Risk R1 (CRITICAL): DFR Backbone Not Identical to ERM**
- Source Assumption: A1
- Affected Hypotheses: H-P0 (test), H-M3 (comparison design)
- Description: If H-P0 fails (cosine similarity < 0.999), DFR backbone was fine-tuned — the entire comparison framework changes. H-P1 must include DFR as 4th backbone method, and baseline probe accuracy reference must be recalculated.
- Severity: Critical
- Likelihood: Low (strong theoretical and empirical basis for frozen backbone in DFR)
- Mitigation:
  1. Prevention: Verify Izmailov repo source code confirms frozen backbone before any experiment
  2. Detection: H-P0 cosine similarity check before H-M3 execution
  3. Response PIVOT: If H-P0 fails, include DFR in H-M3 as 4th backbone condition (compare ERM/SAM/GroupDRO/DFR)

**Risk R2 (HIGH): Probe Metric Non-Discriminative (Near-Chance ERM Accuracy)**
- Source Assumption: A2
- Affected Hypotheses: H-M3, H-P2
- Description: If ERM layer4 probe accuracy is near 0.5 (binary background chance), the probe metric lacks discriminative power and cannot detect GroupDRO-ERM differences. This would invalidate H-M3 entirely.
- Severity: High
- Likelihood: Low (Izmailov 2022 s-DFR proxy shows ~85% background decodability from ERM features)
- Mitigation:
  1. Prevention: Compute ERM probe accuracy FIRST as baseline sanity check (embed in H-P0 step)
  2. Detection: If ERM probe acc < 0.6 on full test set, flag before GroupDRO comparison
  3. Response: EXPLORE earlier layers (layer3, layer2) or switch to non-linear probe if layer4 fails

**Risk R3 (MEDIUM): High Variance Across Seeds (Underpowered Test)**
- Source Assumption: A3
- Affected Hypotheses: H-M3
- Description: n=3 seeds may be insufficient for p<0.05 if Cohen's d is in 0.5-0.8 range. Expected from linear probe stability (bounded [0,1]) but not guaranteed.
- Severity: Medium
- Likelihood: Medium (n=3 underpowered at moderate effect sizes)
- Mitigation:
  1. Prevention: Pre-register tiered success criteria (CONFIRMED/SUGGESTIVE/REJECTED) upfront
  2. Detection: Compute CV across seeds before statistical test; if CV > 0.1, flag power warning
  3. Response: Report as SUGGESTIVE if p<0.10 and Cohen's d>0.5; document power limitation; both outcomes publishable

**Risk R4 (MEDIUM): Checkpoint Differentiation Failure**
- Source Assumption: A4
- Affected Hypotheses: H-P0, H-M3
- Description: If checkpoints are not genuinely differentiated (e.g., implementation bug causing shared weights), all probe accuracies will be similar regardless of training method.
- Severity: Medium
- Likelihood: Very Low (WGA differences of 0.16 between ERM and GroupDRO confirm differentiation)
- Mitigation:
  1. Prevention: Verify WGA values match published results before probe measurement
  2. Detection: If all probe accuracies are within 0.02 of each other, flag differentiation failure
  3. Response: ABORT — fundamental data quality issue; contact Izmailov repo maintainers

**Risk R5 (LOW): group_array Label Extraction Error**
- Source Assumption: A5
- Affected Hypotheses: H-M3, H-P2
- Description: If background_label = group_array % 2 extracts wrong attribute, probe predicts incorrect target and results are meaningless.
- Severity: Medium
- Likelihood: Very Low (Sagawa 2019 clearly defines group structure; group_array%2 is the correct extraction)
- Mitigation:
  1. Prevention: Verify against Sagawa 2019 Table 1: groups = {waterbird/landbird} × {water_bg/land_bg}
  2. Detection: Check class balance before training probe (should be ~50/50 for binary background)
  3. Response: Debug label extraction code; re-verify against WILDS API documentation

### 4.2 Risk-Hypothesis Mapping

| Risk | Source | Severity | Affected Hypotheses |
|------|--------|----------|---------------------|
| R1: DFR backbone mismatch | A1 | Critical | H-P0, H-M3 |
| R2: Probe non-discriminative | A2 | High | H-M3, H-P2 |
| R3: Underpowered test (n=3) | A3 | Medium | H-M3 |
| R4: Checkpoint differentiation failure | A4 | Medium | H-P0, H-M3 |
| R5: group_array label error | A5 | Low | H-M3, H-P2 |

### 4.3 Baseline Failure Patterns → Risks

| Baseline Limitation | Potential Risk | Mitigation |
|---------------------|----------------|------------|
| h-e1 FAIL: full-model gradient cosine similarity (D~25M, CV=3.98) | Metric instability — avoid gradient-based metrics | Linear probe is bounded [0,1]; stable by design |
| h-m2 LIMITATION: head-only Hessian λ_max invalid for full-model curvature | Wrong layer-of-analysis | Layer4 linear probe measures backbone features directly |

---

## 5. Dependency Graph & Timeline

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 5 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Foundation]
    H-P0 (EXISTENCE Sanity Check — no dependencies)
         │
         ▼
[Level 1 - Theory: Mechanism Initiation]
    H-M1 ← H-P0
         │
         ▼
[Level 2 - Theory: Gradient Propagation]
    H-M2 ← H-M1
         │
         ▼
[Level 3 - Empirical: Primary Test]
    H-M3 ← H-M2   (CORE EXPERIMENT — H-P1 test)
         │
         ▼
[Level 4 - Exploratory: Correlation]
    H-P2 ← H-M3

═══════════════════════════════════════════════════════════
Critical Path: H-P0 → H-M1 → H-M2 → H-M3 → H-P2
All sequential — no parallelization in incremental mode
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type |
|-------|-----------|---------------|-----------|
| 0 | H-P0 | None | MUST_WORK |
| 1 | H-M1 | H-P0 | MUST_WORK |
| 2 | H-M2 | H-M1 | SHOULD_WORK |
| 3 | H-M3 | H-M2 | MUST_WORK |
| 4 | H-P2 | H-M3 | SHOULD_WORK |

### 5.3 Gantt Timeline

```
═══════════════════════════════════════════════════════════════════
VERIFICATION TIMELINE - 5 Hypotheses
═══════════════════════════════════════════════════════════════════
Phase/Hypothesis    │ W1-2    │ W3-4    │ W5      │ W6      │ Note
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────
PHASE 1: Foundation
  H-P0 (sanity)    │ ████████│         │         │         │ 50 images
  H-M1 (theory)    │ ████████│         │         │         │ concurrent
  [Gate 1]         │         │◆        │         │         │ MUST PASS
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────
PHASE 2: Mechanisms
  H-M2 (propag.)   │         │ ████████│         │         │ theory
  H-M3 (probe)     │         │ ████████│ ████    │         │ full test set
  [Gate 2]         │         │         │◆        │         │ MUST PASS
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────
PHASE 3: Exploratory
  H-P2 (correl.)   │         │         │         │ ████    │ bootstrap
  [Gate 3]         │         │         │         │◆        │ SHOULD_WORK
────────────────────┼─────────┼─────────┼─────────┼─────────┼─────
═══════════════════════════════════════════════════════════════════
Legend: ████ = Active work | ◆ = Gate decision point
Total Duration: 5 weeks
═══════════════════════════════════════════════════════════════════
```

### 5.4 Critical Path Analysis

```
Critical Path: H-P0 → H-M1 → H-M2 → H-M3 → H-P2
Total Duration: 5 weeks
  Formula: 2 (H-P0 + H-M1 concurrent) + 2 (H-M2 + H-M3) + 1 (H-P2)
Slack Available: 0 weeks (fully sequential)
```

### 5.5 Resource Summary

```
Total Hypotheses: 5
- Existence/Sanity: 1 (H-P0)
- Mechanism: 3 (H-M1, H-M2, H-M3)
- Exploratory Correlation: 1 (H-P2)

Verification Phases: 3
1. Foundation (H-P0 + H-M1, concurrent)
2. Core Mechanisms (H-M2 + H-M3)
3. Exploratory (H-P2)

Total Duration: 5 weeks
Critical Path: 5 weeks
Execution: Sequential chain (no parallelization in PoC mode)
Dataset: Waterbirds WILDS full test set (~4795 images, 12 checkpoints)
Compute: Forward-pass feature extraction only (no training) + sklearn probe
```

### 5.6 Execution Order

**Step 1:** Execute H-P0 + H-M1 concurrently (Week 1-2)
- H-P0: Load 6 checkpoint pairs (DFR/ERM × 3 seeds), extract layer4 features for 50 test images, verify cosine similarity ≥ 0.9999
- H-M1: Confirm theoretical mechanism via Sagawa 2019 and WGA evidence
**Step 2:** Evaluate Gate 1 → If H-P0 PASS and H-M1 PASS, proceed; else STOP
**Step 3:** Execute H-M2 + H-M3 (Week 3-5, sequential)
- H-M2: Establish gradient propagation theoretical basis (concurrent with H-M3 setup)
- H-M3: Full feature extraction for 12 checkpoints on complete test set; sklearn probe training; paired t-test
**Step 4:** Evaluate Gate 2 → If H-M3 CONFIRMED or SUGGESTIVE, proceed; if REJECTED, document failure
**Step 5:** Execute H-P2 (Week 6) — only if H-M3 provides probe accuracies for 9 checkpoints
**Step 6:** Evaluate Gate 3 → H-P2 exploratory; result deferred to Phase 5 full analysis
**Final:** Verification complete; proceed to Phase 2C experiment design for H-P0 and H-M3

---

## 6. Dialectical Analysis

### 6.1 Thesis

**Core Claim:** GroupDRO training reduces linear decodability of spurious background attributes from ResNet-50 layer4 features compared to ERM training, as measured by sklearn L-BFGS probe accuracy on full Waterbirds WILDS test set (paired one-sided t-test, p<0.05, n=3 seeds).

**Supporting Evidence:**
1. GroupDRO worst-group loss upweights minority groups (background-atypical examples), creating differential gradient signal at all backbone layers (Sagawa 2019 — theoretical)
2. Representation learning theory: training objective shapes representation — gradient signal flowing through all layers during GroupDRO training should modify backbone encoding
3. ERM encodes strong background information (~85% s-DFR proxy accuracy, Izmailov 2022) — baseline exists for GroupDRO to reduce
4. Park 2025 SCER: spurious representation directions can be regularized in layer4 features — demonstrates the target mechanism is achievable

**Strengths:**
- Stable metric: linear probe accuracy bounded [0,1], expected CV < 0.05 (vs h-e1's CV=3.98)
- Pre-registered direction: one-sided test prevents post-hoc interpretation flip
- Tiered success criteria (CONFIRMED/SUGGESTIVE/REJECTED) handle n=3 power limitation honestly
- DFR backbone identity (H-P0) creates clean comparison: backbone-changing vs backbone-preserving

**Expected Outcomes:**
- P0: DFR cosine similarity ≥ 0.9999 (high confidence — 0.92)
- P1: GroupDRO probe acc < ERM probe acc (moderate confidence — 0.68)
- P2: Pearson r < -0.5 for probe acc vs WGA (lower confidence — n=9 correlation)

### 6.2 Antithesis

**Null Hypothesis (H0):** There is no significant difference in spurious attribute linear probe accuracy between GroupDRO-trained and ERM-trained ResNet-50 layer4 features on Waterbirds WILDS (one-sided paired t-test: p ≥ 0.05 for GroupDRO < ERM direction).

**Counter-Arguments:**
1. Kirichenko 2022 DFR achieves highest WGA (0.91) WITHOUT changing backbone — suggests head calibration alone may suffice for WGA improvement; backbone change may not be necessary
2. n=3 seeds provides insufficient power for Cohen's d < 0.8 effects — a real backbone difference could be missed statistically
3. GroupDRO gradient signal to backbone layers may be weak relative to class-discriminative features — spurious gradient propagation might be negligible in practice
4. "Dilution" vs "suppression": increased feature diversity may incidentally reduce background accuracy without targeted mechanism — if ERM and GroupDRO have similar directed spurious components, probe accuracy may not differ

**Conditions Under Which H0 Would Be Supported:**
- GroupDRO mean probe accuracy ≥ ERM mean probe accuracy (p ≥ 0.05, d < 0.2)
- WGA improvement in GroupDRO achieved entirely through head calibration (consistent with DFR matching GroupDRO WGA at 0.91 vs 0.88)
- If layer4 gradient signal from spurious features is negligible compared to class-discriminative features regardless of training objective

**Potential Failure Points:**
- R1: DFR backbone identity fails → redesign comparison
- R2: ERM probe accuracy near chance → metric fails
- R3: n=3 underpowered → p≥0.05 even with real effect

### 6.3 Synthesis

**Balanced Assessment:** The BSER hypothesis presents a testable, well-motivated claim that GroupDRO training creates a measurable backbone-level change in spurious feature encoding. The thesis is grounded in theoretical mechanism (Sagawa 2019 GroupDRO formulation) and supported by indirect evidence (Park 2025 SCER, Izmailov 2022 high ERM baseline). However, the null hypothesis raises valid concerns: DFR achieves higher WGA (0.91) than GroupDRO (0.88) without any backbone change, suggesting head calibration may dominate. The n=3 power limitation is real and honestly addressed through tiered criteria.

**Resolution Path:** The verification plan addresses this dialectic through:
1. **H-P0 (Foundation):** Empirically establishes DFR ≡ ERM backbone — eliminates confound and clarifies backbone-changing vs backbone-preserving distinction
2. **H-M1→H-M2 (Theory):** Documents theoretical mechanism chain before empirical test
3. **H-M3 (Primary Test):** Direct measurement with pre-registered direction, tiered criteria, and Cohen's d reporting
4. **H-P2 (Exploratory):** Tests predictive utility of probe accuracy — useful regardless of H-M3 outcome

**Nuanced Outcome Possibilities:**
1. **Full Support:** H-M3 CONFIRMED (p<0.05, d>0) → backbone-level spurious encoding reduction is real; GroupDRO modifies backbone representation
2. **Partial Support:** H-M3 SUGGESTIVE (p<0.10, d>0.5) → consistent with mechanism but underpowered; publishable as suggestive evidence
3. **H0 Supported:** H-M3 REJECTED → WGA improvement is head-only for all known methods; this is equally field-relevant (eliminates backbone mechanism hypothesis definitively)

**Both thesis and antithesis outcomes contribute to field understanding.** Dr. Sage (Exchange 14): "Either result reframes our understanding of robustification."

### 6.4 Robustness Assessment

| Aspect | Thesis Position | Antithesis Challenge | Resolution |
|--------|-----------------|----------------------|------------|
| Backbone identity | DFR ≡ ERM by protocol | May differ in released checkpoints | H-P0 empirical test |
| Mechanism | GroupDRO gradient modifies backbone encoding | Head calibration sufficient without backbone change | H-M3 direct probe measurement |
| Statistical power | Bounded metric, stable CV expected | n=3 underpowered at moderate effects | Tiered criteria + Cohen's d |
| Interpretation | GroupDRO suppresses spurious encoding | Dilution through feature diversity (not targeted suppression) | Both = the claimed mechanism (Dr. Ally, Exchange 11) |
| Field relevance | Confirms backbone-level mechanism | Eliminates backbone-level mechanism | Both outcomes publishable |

**Overall Robustness Score:** Medium-High

**Confidence in Verification Plan:** 0.72 (inherited from Phase 2A — reflects genuine uncertainty about H-M3 outcome, not methodological weakness)

---

## 7. Executive Summary & Conclusions

### 7.1 Executive Summary

**Main Hypothesis:** GroupDRO training reduces spurious attribute (background land/water) linear decodability from ResNet-50 layer4 features compared to ERM (sklearn L-BFGS probe, full Waterbirds WILDS test set)
- ID: H-BSER-v1 | Confidence: 0.72

**Verification Structure:**
- Mode: Incremental (Phase 2A Dialogue available)
- Sub-Hypotheses: 5 total (H-P0, H-M1, H-M2, H-M3, H-P2)
- Phases: 3 over 5 weeks
- Critical Gates: 3 decision points (Gate 1: MUST, Gate 2: MUST, Gate 3: SHOULD)

**Risk Assessment:** Medium
- Primary concerns: n=3 underpowered (R3), DFR backbone identity must be verified (R1)

**Immediate Action:** Execute H-P0 sanity check (DFR cosine similarity) before any backbone comparison

### 7.2 Verification Execution Order

**Phase 1: Foundation** (Weeks 1-2)
- H-P0: DFR backbone identity (cosine similarity ≥ 0.9999 for all 3 seed pairs) — MUST PASS
- H-M1: GroupDRO worst-group loss mechanism confirmation (theory + WGA evidence) — MUST PASS
- Gate 1: Both MUST PASS before Phase 2

**Phase 2: Core Mechanisms** (Weeks 3-5)
- H-M2: Gradient propagation to backbone (theoretical, proxied by H-M3)
- H-M3: Primary probe accuracy test — GroupDRO vs ERM spurious probe accuracy (paired t-test, full test set, n=3 seeds) — MUST_WORK

**Phase 3: Exploratory** (Week 6)
- H-P2: Pearson correlation spurious probe acc vs WGA across 9 distinct-backbone checkpoints (bootstrap CI)

### 7.3 Critical Decision Points

1. **Gate 1 (H-P0):** DFR backbone identity
   - PASS (≥0.9999) → Compare only backbone-changing methods (ERM/SAM/GroupDRO) in H-M3
   - FAIL (<0.999) → Include DFR as 4th backbone condition; redesign H-M3

2. **Gate 2 (H-M3):** Primary probe accuracy test
   - CONFIRMED (p<0.05, d>0) → Backbone-level mechanism validated; proceed to Phase 2C/3/4
   - SUGGESTIVE (p<0.10, d>0.5) → Consistent with mechanism; proceed with caveat
   - REJECTED (wrong direction or weak) → WGA improvement head-only; document as definitive negative result; route to Phase 5

3. **Gate 3 (H-P2):** WGA correlation
   - PASS (r<-0.5, CI<0) → Probe accuracy as WGA predictor validated
   - PARTIAL → Suggestive; defer to Phase 5 full baseline comparison

### 7.4 Open Questions

- Does SAM sharpness penalty incidentally reduce spurious encoding? (exploratory H-P1b, no pre-registered threshold)
- If H-P0 fails (DFR backbone ≠ ERM), what backbone change does DFR introduce?
- Is layer4 the right layer? (Phase 1 Gap 3: secondary gap on layer-wise profile — out of scope for this PoC)
- Does n=3 yield sufficient power given expected probe accuracy variance? (post-hoc power analysis needed if SUGGESTIVE)

### 7.5 Recommendations

1. **Immediate Actions:**
   - Start Phase 1 with H-P0 (cosine similarity sanity check) — 1-2 hours of compute
   - Verify ERM baseline probe accuracy first (A2 validation) before GroupDRO comparison
   - Set up WILDS data loading and checkpoint download pipeline

2. **Resource Allocation:**
   - Forward-pass feature extraction: ~4 hours GPU time (12 checkpoints × full test set)
   - sklearn probe fitting: fast (<1 min per checkpoint)
   - Statistical analysis: trivial (scipy.stats)
   - Reserve 1 week buffer for H-P0 failure (DFR re-design)

3. **Failure Management:**
   - H-P0 FAIL: PIVOT to 4-backbone design (include DFR in comparison)
   - H-M3 REJECTED: Document as definitive negative result (both outcomes publishable); route to Phase 5 for comparison analysis
   - SUGGESTIVE result: Publish with honest tiered reporting; do not over-interpret

---

## Appendices

### A. Phase 2A Reference
- **Source:** `docs/youra_research/03_refinement.yaml` (ID: H-BSER-v1)
- **Generated:** 2026-08-05 | Schema: 10.0.0

### B. MCP Tool Usage Summary
- **Total MCP calls:** 4 (2× scientificmethod for H-P0 + H-P1)
- **Mode:** Incremental (Phase 2A available)
- **Tools:** mcp__clearThought__scientificmethod (hypothesis + experiment stages)
