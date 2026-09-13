# Verification Plan: Gradient Abnormality Detection and Spatial Regularization

**Date:** 2026-08-20
**Hypothesis ID:** H-GradAbn-v1
**Confidence:** 0.78
**Total Hypotheses:** 3

---

## 1. Main Hypothesis & Baselines

### 1.1 Core Statement

Under deep neural networks trained on datasets with spurious correlations (e.g., Waterbirds with 90% background-class correlation), if we compute gradient abnormality metrics (GAIA zero-deflation, channel-wise variance) for test samples, then minority group samples (waterbird-land, landbird-water) will exhibit significantly higher abnormality scores than majority group samples (waterbird-water, landbird-land), because spurious reliance creates gradient scattering when the spurious shortcut conflicts with core features in minority samples.

### 1.2 Alternative Hypothesis (H0)

There is no significant difference in gradient abnormality scores (GAIA-Z, GAIA-A) between majority and minority group samples.

### 1.3 Experimental Setup (from Phase 2A)

| Component | Selection | Justification |
|-----------|-----------|---------------|
| **Dataset** | Waterbirds (primary), MNIST+Color (toy), CelebA (generalization) (standard/synthetic) | Waterbirds: canonical spurious correlation benchmark (background-class), 4 groups with annotations. MNIST+Color: controlled spurious (color) for validation. CelebA: different spurious type (gender) for generalization. |
| **Model** | ResNet-50 (Waterbirds/CelebA), ResNet-18 (MNIST toy) | ResNet-50 standard for Waterbirds/CelebA evaluation (all baselines use it). Enables direct comparison to GroupDRO, JTT, SPROD results. |

**Dataset Details:**
- Source: Waterbirds via Wilds benchmark (pip install wilds), MNIST via torchvision, CelebA via Wilds
- Path: Waterbirds: wilds.get_dataset('waterbirds'), MNIST: torchvision.datasets.MNIST, CelebA: wilds.get_dataset('celebA')

**Model Details:**
- Type: Standard CNN backbone
- Source: torchvision.models.resnet50(pretrained=True) for Waterbirds/CelebA, torchvision.models.resnet18() for MNIST

### 1.4 Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| GroupDRO | 85-88% WGA | Waterbirds, CelebA, MultiNLI |
| JTT | ~88% WGA | Waterbirds, CelebA |
| SCER | ~90% WGA (estimated) | Waterbirds, CelebA |

### 1.5 Key Assumptions

| ID | Assumption | Evidence | If Violated |
|----|------------|----------|-------------|
| A1 | Minority groups correctly classified ≥60% for GradCAM difference | SPROD 2025 showed minority misclassified MORE but not exclusively | GradCAM highlights spurious (not core). Fallback: global regularization |
| A2 | Percentile normalization (75th) avoids majority bias | Prof. Rex identified mean-based would be majority-dominated | Penalty too weak on minority. Fallback: manual λ tuning |
| A3 | Gradient scattering caused by spurious conflict, not complexity | GAIA controlled for complexity in OOD. Waterbirds = controlled backgrounds | False positives. Must validate via augmentation test (P3) |
| A4 | Regularization reduces spurious reliance, not just smooths gradients | No direct prior work. Theoretical link via forcing alternative features | WGA unchanged. MNIST toy reveals. Fallback: detection-only |
| A5 | GroupDRO/JTT baselines sufficient without SCER | GroupDRO (294 stars), JTT (72 stars), both reproducible | Cannot claim Tier 1 SOTA. Accept Tier 2 ceiling |

### 1.6 Research Gap & Novelty

**Preserved Novelty:** First application of gradient abnormality (GAIA framework) to minority group detection within ID distribution. First gradient-based regularization for spurious mitigation. Automatic spurious localization via GradCAM difference maps without feature engineering.

**Key Innovation:** Extends GAIA from distribution shift (ID vs OOD) to subpopulation shift (majority vs minority). Spatial masking discovers spurious regions automatically by comparing majority/minority gradient patterns. Unified framework: same abnormality mechanism for both OOD and spurious detection.

**Differentiation:**
- vs. Adebayo 2022: Use gradient ABNORMALITY (process disruption), not gradient ATTRIBUTION (result interpretation)
- vs. GAIA 2023: Extend to subpopulation shift within ID distribution, add mitigation
- vs. SPROD 2025: Operate on gradient space (not prototype space), provide mitigation
- vs. SCER 2025: Operate on gradient space (not embedding space), complementary intervention points
- vs. GroupDRO/JTT: GroupDRO requires annotations, JTT two-stage. We provide diagnostic + mitigation

---

## 2. Hypotheses

### 2.1 Inventory

| ID | Type | Gate | Prerequisites | Status |
|----|------|------|---------------|--------|
| h-e1 | Existence | MUST_WORK | None | READY |
| h-m-integrated | Mechanism | MUST_WORK | h-e1 | NOT_STARTED |
| h-m-mitigate | Mechanism (Mitigation) | SHOULD_WORK | h-m-integrated | NOT_STARTED |

---

### 2.2 Hypothesis Specifications

---
**H-E1: Gradient Abnormality Detection on Minority Groups**

**Statement**: Under deep neural networks trained on Waterbirds dataset with 90% spurious correlation, if we compute GAIA-Z gradient abnormality metrics for test samples, then minority group samples (waterbird-land, landbird-water) will exhibit scores ≥0.2 higher than majority group samples because spurious reliance creates gradient scattering when shortcuts conflict with core features.

**Rationale**: Validates that gradient abnormality (GAIA framework) extends from OOD detection to subpopulation shift detection. If minority groups show higher abnormality scores, the detection mechanism works without prior knowledge of spurious features.

**Variables**:
- Independent: Test sample group membership (Majority vs Minority)
- Dependent: GAIA-Z score (zero-deflation ratio, range [0,1])
- Controlled: Model architecture (ResNet-50), training hyperparameters, image complexity

**Verification Protocol**:
1. Train ResNet-50 on Waterbirds 90% correlation, verify WGA <80%
2. Compute GAIA-Z for all 4795 test samples via GradCAM attribution gradients
3. Statistical test: two-sample t-test comparing minority vs majority mean GAIA-Z
4. Measure effect size via Cohen's d to quantify practical significance

**Success Criteria** (PoC: Direction-based):
- Primary: Mean GAIA-Z (minority) ≥ Mean GAIA-Z (majority) + 0.2 AND p < 0.01
- Secondary: Cohen's d ≥ 0.8 (large effect size)

**Gate**:
- Type: MUST_WORK
- If Fail: Abandon gradient abnormality approach

**Failure Response**: ABANDON (fundamental mechanism failure)

**Dependencies**: None (foundation hypothesis)

**Source**: Phase 2A Section 5 (SH1), Prediction P1

---
**H-M-INTEGRATED: 4-Step Causal Mechanism Validation**

**Statement**: The causal mechanism linking spurious training to gradient abnormality follows: (1) Model learns spurious shortcut → (2) Minority samples create conflict → (3) Conflict manifests as gradient scattering → (4) GAIA metrics quantify scattering.

**Rationale**: Validates the mechanistic chain connecting spurious reliance to observable gradient patterns. Tests whether GAIA divergence correlates with worst-group accuracy and whether augmentation causally affects abnormality.

**Variables**:
- Independent: Training correlation rate (50%, 60%, ..., 95%)
- Dependent: GAIA divergence (minority-majority gap), Worst-group accuracy
- Controlled: Model architecture (ResNet-50), hyperparameters

**Verification Protocol**:
1. Train 10 models with varying correlation rates, measure WGA and GAIA divergence
2. Compute Pearson correlation between GAIA divergence and WGA (expected ρ > 0.7)
3. Validate augmentation causality: swap backgrounds on 100 minority samples
4. Verify minority classification accuracy ≥60% (spatial masking validity)

**Success Criteria** (PoC: Direction-based):
- Primary: GAIA divergence correlates with WGA (ρ > 0.7, p < 0.05)
- Secondary: Background augmentation reduces GAIA-Z by ≥30%

**Gate**:
- Type: MUST_WORK
- If Fail: Identify failure point, pivot to detection-only

**Failure Response**: EXPLORE (identify which step fails: 1/2/3/4)

**Dependencies**: h-e1 (must pass first)

**Source**: Phase 2A Section 1.3 (Causal Mechanism), Predictions P2/P3

---
**H-M-MITIGATE: Spatial Gradient Regularization for Spurious Mitigation**

**Statement**: Under training with spatial gradient regularization (penalizing gradient divergence in GradCAM-identified spurious regions), if we apply adaptive penalty scaling, then worst-group accuracy improves by ≥5% over GroupDRO because regularization forces model reliance on core features.

**Rationale**: Tests whether gradient-based mitigation (not just detection) works. MNIST toy validates mechanism in controlled setting; Waterbirds validates real-world effectiveness vs baselines.

**Variables**:
- Independent: Regularization condition (baseline, global, spatial spurious-region, spatial core-region)
- Dependent: Worst-group accuracy, Average accuracy
- Controlled: Dataset (MNIST+Color, Waterbirds), model architecture

**Verification Protocol**:
1. MNIST+Color toy: train 4 conditions, compare WGA
2. Validate color-only WGA ≥ baseline+10%, digit-only WGA ≤ baseline-5%
3. Waterbirds: train with spatial regularization (GradCAM masking + adaptive penalty)
4. Compare WGA to GroupDRO/JTT, track average accuracy drop (must be ≤2%)

**Success Criteria** (PoC: Direction-based):
- Primary (MNIST): Color-only WGA ≥ baseline+10%
- Primary (Waterbirds): WGA ≥ GroupDRO+5%, average accuracy drop ≤2%

**Gate**:
- Type: SHOULD_WORK
- If Fail: Reframe as detection-only contribution

**Failure Response**: PIVOT (to detection-only, Tier 3 positioning)

**Dependencies**: h-m-integrated (mechanism must hold)

**Source**: Phase 2A Predictions P4/P5, Assumptions A1/A2/A4

---

---

## 3. Execution

### 3.1 Dependency Chain
```
h-e1 → h-m-integrated → h-m-mitigate
```

### 3.2 Gate Summary

| Hypothesis | Gate Type | Pass Condition | Fail Action |
|------------|-----------|----------------|-------------|
| h-e1 | MUST_WORK | GAIA-Z (minority) ≥ (majority)+0.2, p<0.01 | ABANDON entire approach |
| h-m-integrated | MUST_WORK | ρ>0.7 (GAIA-WGA correlation) AND augmentation ≥30% reduction | EXPLORE failure point, pivot to detection-only |
| h-m-mitigate | SHOULD_WORK | MNIST WGA≥+10%, Waterbirds WGA≥GroupDRO+5% | PIVOT to detection-only (Tier 3) |

### 3.3 Timeline

| Phase | Hypotheses | Duration |
|-------|------------|----------|
| Phase 2C | Experiment Design (all 3) | 2-3 days |
| Phase 3 | Implementation Planning (all 3) | 3-4 days |
| Phase 4 | PoC Validation (sequential) | 10-14 days |
| Phase 5 | Baseline Comparison (SKIPPED) | N/A |

**Total Duration:** 15-21 days (excluding Phase 5)

---

## 4. Risk Analysis

### 4.1 Risk-Hypothesis Mapping

| Risk | Source | Affected Hypotheses | Severity | Mitigation |
|------|--------|---------------------|----------|------------|
| R1 | A1 | h-m-mitigate | High | Monitor minority accuracy, fall back to global regularization if <60% |
| R2 | A2 | h-m-mitigate | Medium | Use 75th percentile normalization, compare penalty magnitudes across groups |
| R3 | A3 | h-e1, h-m-integrated | High | Waterbirds only (controlled backgrounds), validate via augmentation test (P3) |
| R4 | A4 | h-m-mitigate | Medium | MNIST toy validates mechanism first, check feature attribution shift |
| R5 | A5 | All | Low | Accept Tier 2 ceiling, position as complementary method |

**Critical Risks:** 2 (R1: Minority accuracy, R3: Complexity confound)
**High Risks:** 2 (R1, R3)
**Medium Risks:** 2 (R2, R4)
**Low Risks:** 1 (R5)

### 4.2 Mitigation Strategies

**R1 (Minority Accuracy <60%):**
- Prevention: Empirical check during training
- Detection: Monitor minority classification accuracy continuously
- Response: Fall back to global gradient regularization if <60%

**R2 (Percentile Normalization Bias):**
- Prevention: Use 75th percentile (not mean)
- Detection: Compare penalty magnitudes across groups
- Response: Manual λ tuning if bias detected

**R3 (Complexity Confound):**
- Prevention: Use Waterbirds only (controlled backgrounds)
- Detection: Background augmentation test (P3) - expect ≥30% reduction
- Response: Abandon if augmentation effect <10%

**R4 (Regularization Mechanism Failure):**
- Prevention: MNIST toy validates mechanism first
- Detection: Check feature attribution shift, not just gradient smoothing
- Response: Pivot to detection-only if MNIST WGA <+5%

**R5 (SCER Comparison Unavailable):**
- Prevention: N/A (code unavailable)
- Detection: Check SCER repo for release
- Response: Accept Tier 2 ceiling, position as complementary

---

## 5. Visualization

### 5.1 Dependency Graph (DAG)

```
═══════════════════════════════════════════════════════════
DEPENDENCY GRAPH (DAG) - 3 Hypotheses
═══════════════════════════════════════════════════════════

[Level 0 - Root]
    h-e1 (Existence: Gradient Abnormality Detection)
         │
         │  Gate: MUST_WORK
         │  → If fails: Abandon gradient abnormality approach
         ▼
[Level 1 - Mechanism Validation]
    h-m-integrated (4-Step Causal Mechanism)
         │
         │  Gate: MUST_WORK
         │  → If fails: Identify failure point, pivot to detection-only
         ▼
[Level 2 - Mitigation]
    h-m-mitigate (Spatial Gradient Regularization)
         │
         │  Gate: SHOULD_WORK
         │  → If fails: Reframe as detection-only contribution
         ▼
[Terminal]

═══════════════════════════════════════════════════════════
Critical Path: h-e1 → h-m-integrated → h-m-mitigate
Total Depth: 3 levels
═══════════════════════════════════════════════════════════
```

### 5.2 Dependency Hierarchy

| Level | Hypothesis | Prerequisites | Gate Type | Consequence if Fail |
|-------|-----------|---------------|-----------|---------------------|
| 0 | h-e1 | None | MUST_WORK | Abandon entire approach |
| 1 | h-m-integrated | h-e1 | MUST_WORK | Pivot to detection-only |
| 2 | h-m-mitigate | h-m-integrated | SHOULD_WORK | Tier 3 (detection-only) |

---

## 6. Summary

### 6.1 Executive Summary

This verification plan decomposes the main hypothesis (H-GradAbn-v1) into 3 sub-hypotheses spanning existence validation, mechanism validation, and mitigation testing. The plan leverages Phase 2A Dialogue outputs to achieve 60% scope reduction by building on established facts (GAIA metrics, spurious correlation theory) and focusing on novel claims (minority group detection, spatial regularization).

**Key Decision Gates:**
1. **h-e1 (Foundation)**: Must prove minority groups exhibit gradient abnormality. Failure = abandon approach.
2. **h-m-integrated (Mechanism)**: Must validate 4-step causal chain. Failure = pivot to detection-only.
3. **h-m-mitigate (Mitigation)**: Should improve WGA over GroupDRO. Failure = reframe as detection-only (Tier 3).

**Risk Profile:** 2 high-risk assumptions (minority accuracy, complexity confound) with clear mitigation strategies. MNIST toy experiment provides early validation of regularization mechanism.

**Estimated Duration:** 15-21 days (Phase 2C→4, excluding Phase 5 baseline comparison per module.yaml skip_baseline_comparison=true).

### 6.2 Next Steps

1. **Phase 2C (Experiment Design)**: Generate detailed experiment specifications for each hypothesis
2. **Phase 3 (Implementation Planning)**: Create PRD, architecture, and task breakdowns
3. **Phase 4 (PoC Validation)**: Execute experiments, validate via MUST_WORK/SHOULD_WORK gates
4. **Phase 6 (Paper Writing)**: Synthesize results, position as Tier 2-3 contribution

---

## Appendices

### A. Scope Reduction Summary

**BUILD_ON Claims (Do NOT re-verify):**
- Gradient attribution methods fail for unknown spurious (Adebayo 2022)
- GAIA detects OOD via gradient abnormality (Chen et al. 2023)
- Models trained on spurious achieve lower WGA (established literature)

**PROVE_NEW Claims (Focus verification):**
- Gradient abnormality detects minority groups (h-e1)
- Spatial regularization improves WGA (h-m-mitigate)

**Scope Reduction:** 60% (3 BUILD_ON claims, 2 PROVE_NEW claims)

### B. Archon Task Mapping

**Pipeline Project ID:** ef7140fe-2bf9-4e5e-95dc-bf2484dc0083
**Pipeline Title:** Anonymous Pipeline: Gradient-Based Spurious Feature Detection

**Hypothesis Task IDs:**
- h-e1: 28693385-e2a4-42df-ba9a-8f8e903c76bb
- h-m-integrated: 2c7459e2-2180-4032-896c-deb038ba950c
- h-m-mitigate: 3ba4c5c9-74e4-4e2d-b3c7-6d09a730af6d

**Phase Task IDs:**
- Phase 2B: 4bb1f293-6c4f-421c-8eb5-1fa41dec1a87 (done)
- Phase 2C: e5e29855-a636-4d17-b973-516946a29a29 (doing)

---

**Document Status:** Complete
**Generated:** 2026-08-20T02:17:45Z
**Next Action:** Begin Phase 2C with h-e1 experiment design
