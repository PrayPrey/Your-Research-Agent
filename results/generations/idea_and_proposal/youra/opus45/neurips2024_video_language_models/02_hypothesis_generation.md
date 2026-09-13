# Phase 2A Extended: Hypothesis Clarification (Summary)

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md (PhysTac - Round 1)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-PhysTac-001
**Confidence Level:** 0.78

**Main Hypothesis:**
Physics-informed disentangled representation learning for vision-based tactile sensors achieves superior cross-sensor transfer in low-data regimes compared to purely data-driven approaches. Specifically, by separating sensor-agnostic contact geometry features (learned via FEM-supervised physics branch) from sensor-specific appearance features (learned via reconstruction branch), the resulting representations enable: (1) >10% improvement in zero-shot transfer to unseen sensors, and (2) equivalent performance with <10× fewer labeled samples from new sensors compared to state-of-the-art data-driven methods (T3, AnyTouch).

**Alternative Hypothesis (H0):**
Data-driven alignment (as in T3/AnyTouch/Sparsh) is sufficient for cross-sensor transfer, and physics-informed supervision provides no statistically significant improvement over pure data-driven approaches in either zero-shot or few-shot regimes.

### 1.2 Variables

| Variable Type | Variable | Operationalization | Measurement |
|---------------|----------|-------------------|-------------|
| **IV1** | Architecture Type | (a) PhysTac (physics-disentangled), (b) T3 (shared trunk), (c) AnyTouch (unified static-dynamic), (d) Single-sensor | Categorical |
| **IV2** | Physics Supervision Level | (a) Full deformation field, (b) Contact mask + normal force, (c) None | Ordinal |
| **IV3** | Target Sensor Data Amount | n ∈ {0, 10, 50, 100, 500, 1000} samples | Continuous |
| **DV1** | Zero-Shot Transfer Accuracy | TacBench accuracy on held-out sensor (%) | Continuous [0-100] |
| **DV2** | Few-Shot Efficiency | Samples needed to match T3-1000 baseline | Count |
| **DV3** | Force Estimation Performance | Mean Absolute Error (N) on force prediction | Continuous |
| **CV1** | Base Encoder | ViT-B/16 (frozen architecture) | Fixed |
| **CV2** | Pre-training Data Size | 3M+ samples (FoTa dataset) | Fixed |
| **CV3** | Evaluation Benchmark | TacBench (6 tasks, standardized) | Fixed |

### 1.3 Causal Mechanism

```
[Physics Supervision via FEM Labels]
         ↓
[Physics Branch Learns Contact Geometry Features]
         ↓
[Disentanglement Regularization (GRL + MI Minimization)]
         ↓
[Separation: Physics-Invariant vs Sensor-Specific Features]
         ↓
[Physics-Informed Contrastive Alignment (Same-Physics → Positive Pairs)]
         ↓
[Superior Cross-Sensor Transfer in Low-Data Regimes]
```

**Evidence for Causal Links:**
1. **FEM → Contact Geometry:** TensorTouch (2025) demonstrates FEM+DL extracts stress tensors and deformation fields at pixel-level resolution with 90% manipulation success
2. **Disentanglement → Separation:** VAMP (2025) shows feature diversion prevents knowledge dilution in multimodal learning; Cross-Sensor DA (2025) achieves 89.8% with style-content separation
3. **Physics-Invariant → Transfer:** DigiTac (2022) demonstrates physics IS transferable across sensors (similar pose prediction across DIGIT and TacTip)

**Key Tension:**
The hypothesis depends on FEM simulation accuracy being sufficient for supervision. While TensorTouch validates this, a potential failure mode exists if simulation-to-real domain gap undermines physics label quality. Domain randomization is included to mitigate this risk.

### 1.4 Key Assumptions

| # | Assumption | Validation Status | Evidence |
|---|------------|-------------------|----------|
| A1 | FEM simulation provides accurate enough deformation labels for supervision | **Validated** | TensorTouch (2025): 90% manipulation success with FEM+DL |
| A2 | Contact mechanics is sensor-agnostic; only optical encoding differs | **Validated** | DigiTac (2022): Similar pose prediction across sensors |
| A3 | Disentanglement regularization effectively separates physics from appearance | **Partially Validated** | VAMP (2025): Works for multimodal; untested for tactile |
| A4 | Physics-grounded representations generalize better than appearance-grounded | **Theoretical** | Grounded in contact mechanics invariance; requires empirical validation |

### 1.5 Scope & Boundaries

**Applies To:**
- Vision-based optical tactile sensors (GelSight variants, DIGIT, TacTip, 9DTact)
- Elastomer-based deformation sensing modality
- Manipulation tasks involving contact geometry (grasping, insertion, texture recognition)

**Does NOT Apply To:**
- Non-optical tactile sensors (resistive pressure arrays, capacitive sensors, piezoelectric)
- BioTac-style barometric/impedance sensors
- Tasks not involving deformation (e.g., pure temperature sensing)

**Boundary Conditions:**
- Minimum 50k pre-training samples per sensor type for physics branch training
- Target sensor must have compatible elastomer physics (gel-based)
- Force prediction limited to normal and shear components (not full 6-DOF)

### 1.6 Testable Predictions

**Primary Prediction (P1):**
PhysTac with physics supervision (IV2=b or a) achieves >10% higher zero-shot transfer accuracy (DV1) on held-out sensors compared to T3 baseline, measured on TacBench aggregate score.

*Quantitative Threshold:* T3 baseline ~65% → PhysTac target ≥71.5%

**Secondary Predictions:**

**(P2) Few-Shot Efficiency:**
PhysTac requires ≤100 samples from new sensor to match T3 performance with 1000 samples (10× sample efficiency improvement).

**(P3) Force Estimation:**
Physics branch representations achieve ≥15% lower MAE on force estimation compared to appearance-only representations (Sparsh baseline).

**Falsification Criteria:**
- If PhysTac zero-shot accuracy is ≤T3 baseline (within 2% margin): H0 not rejected
- If PhysTac requires >300 samples to match T3-1000: Few-shot claim falsified
- If physics branch force estimation MAE ≥ Sparsh: Physics supervision claim falsified

### 1.7 Statistical Verification Design

**Design Type:** Mixed factorial design with repeated measures
**Primary Analysis:** Two-way ANOVA (Architecture × Physics Level) with post-hoc Tukey HSD
**Sample Size Justification:** Based on TacBench variance (σ ≈ 5%), α=0.05, β=0.20, detecting 10% improvement requires n≥25 evaluation samples per condition

**Statistical Tests:**
| Prediction | Test | α | Power Target |
|------------|------|---|--------------|
| P1 (Zero-shot) | Independent t-test (PhysTac vs T3) | 0.05 | 0.80 |
| P2 (Few-shot) | Learning curve analysis (samples-to-threshold) | N/A | Descriptive |
| P3 (Force) | Paired t-test (physics vs appearance branch) | 0.05 | 0.80 |

**Multiple Comparison Correction:** Bonferroni correction for 3 primary predictions (α_adj = 0.017)

---

## 2. Contribution Summary

| Contribution Type | Description | Novelty Claim |
|-------------------|-------------|---------------|
| **Theoretical** | Physics-informed disentanglement framework for tactile cross-sensor transfer | First to ground cross-sensor alignment in contact mechanics rather than appearance statistics |
| **Methodological** | Dual-branch architecture combining FEM supervision with disentanglement regularization (GRL + MI) | Novel training paradigm integrating physics simulation with representation learning |
| **Practical** | Few-shot adaptation capability for novel/custom sensors | Enables rapid deployment on new sensor hardware with <100 samples |

---

## 3. Key Related Work

| Paper | Year | Relation | Key Difference |
|-------|------|----------|----------------|
| T3 (Zhao et al.) | 2024 | Primary Baseline | Uses shared trunk with sensor-specific encoders; data-driven alignment |
| AnyTouch | 2025 | Recent Baseline | Unified static-dynamic representations; no physics supervision |
| Sparsh (Meta AI) | 2024 | SSL Baseline | DINO/IJEPA pre-training; appearance-based features |
| TensorTouch (Do et al.) | 2025 | Foundation | Validates FEM+DL for tactile; provides physics supervision methodology |
| VAMP (Li et al.) | 2025 | Methodology Source | Feature diversion for multimodal; adapted for sensor-specific disentanglement |
| Cross-Sensor DA (Jing & Qian) | 2025 | Foundation | Style-content separation achieves 89.8%; validates disentanglement approach |

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Physics-supervised encoder learns representations that capture contact geometry features, as evidenced by superior performance on physics-related downstream tasks (force estimation, contact mask prediction) compared to appearance-only encoders."

**SH2 (Mechanism):**
"Disentanglement regularization (GRL + MI minimization) effectively separates physics-invariant features from sensor-specific features, as measured by probing task accuracy (sensor classification from physics branch should be at chance level)."

**SH3 (Comparison):**
"PhysTac achieves superior cross-sensor transfer compared to T3/AnyTouch baselines, with statistically significant improvements in both zero-shot (>10%) and few-shot (<10× samples) regimes."

### Readiness Checklist

| Item | Status | Notes |
|------|--------|-------|
| Variables operationalized | ✅ Complete | All IVs, DVs, CVs defined |
| Predictions quantified | ✅ Complete | Numerical thresholds specified |
| Falsification criteria defined | ✅ Complete | Clear rejection conditions |
| Statistical design specified | ✅ Complete | ANOVA + t-tests with correction |
| Baselines identified | ✅ Complete | T3, AnyTouch, Sparsh |
| Datasets confirmed | ✅ Complete | FoTa (3M+), TacBench |
| Scope boundaries set | ✅ Complete | Vision-based optical sensors only |

### Open Questions

1. **FEM Methodology Selection:** TacEx (Isaac Sim) vs GelSight-Sim vs custom FEM - which provides best label quality?
2. **Disentanglement Hyperparameters:** Optimal β for MI regularization and GRL gradient reversal strength
3. **Domain Randomization Strategy:** Physical parameter ranges for simulation augmentation

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-13*
