# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-04-14
**Main Hypothesis:** Loss Trajectory Divergence Analysis for Spurious Correlation Detection
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under standard ERM training on Waterbirds, if we extract per-sample loss trajectory features (L₁, slope, variance, time-to-convergence) from epochs 1-5, then these features will predict minority group membership with AUROC > 0.75, because minority samples experience prolonged optimization conflict creating distinctive trajectory patterns.

### Type
EXISTENCE

### Rationale
This is the foundational existence test. If trajectory divergence is not measurable (AUROC ≤ 0.75), the entire mechanism hypothesis collapses. This test validates that temporal dynamics carry group-discriminative information beyond random chance.

---

## Verification Protocol

### Conceptual Test
1. Train ERM model for 20 epochs with per-sample loss logging (deterministic eval passes).
2. Extract trajectory features: L₁, slope (L₅-L₁)/4, variance(L₁...L₅), time-to-95%-min.
3. Normalize losses per-sample (Lₜ/L₁) with 3-point moving average smoothing.
4. Train logistic regression on trajectory features; evaluate with 5-fold stratified CV.
5. Compute AUROC and significance vs random baseline (permutation test, p < 0.05).

### Success Criteria
- Primary: AUROC > 0.75 with p < 0.05 vs random baseline (0.5)
- Secondary: Feature importance shows multiple trajectory features contribute

### Variables (if applicable)
- **Independent Variable:** Group Membership (minority vs majority)
- **Dependent Variable:** Trajectory-Based AUROC
- **Controlled Variables:** ResNet-50, Waterbirds, ERM training, normalized loss

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Waterbirds
- **Type:** standard
- **Source:** Sagawa et al. (2020) Group DRO paper
- **Path:** standard download via WILDS or deep_feature_reweighting repo
- **Hypothesis Fit:** Standard spurious correlation benchmark with 95%/5% correlation; provides group labels for stratified analysis

### Selected Model
- **Name:** ResNet-50
- **Type:** CNN pretrained
- **Source:** torchvision.models.resnet50(pretrained=True)
- **Hypothesis Fit:** Standard architecture used in spurious correlation literature; enables comparison with prior work

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| Gradient Norm Detection | AUC = 0.914 | Waterbirds |
| Attribution Divergence | IoU = 0.6477 (invalidated) | Waterbirds |
| GroupDRO | ~90% WGA | Waterbirds |
| Random Baseline | AUROC = 0.5 | Waterbirds |

### Baseline Performance
- Random classifier: AUROC = 0.5 (chance level)
- Target: AUROC > 0.75 (significantly above chance)

### Gap Analysis
- 0.25 AUROC improvement over random baseline required for existence confirmation
- Gradient norm detection achieves 0.914, showing trajectory-based methods can work

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundation hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** ABANDON main hypothesis (trajectory divergence does not exist)

**Phase Assignment:** Phase 1 - Foundation

**Estimated Duration:** 4-6 hours

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the foundation hypothesis. All mechanism hypotheses (H-M1, H-M2, H-M3) depend on H-E1 passing.
- H-M1 (Curvature Timing) depends on H-E1
- H-M2 (GroupDRO Attenuation) depends on H-E1
- H-M3 (Cross-Seed Prediction) depends on H-E1 and H-M1

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design
5. **Baseline comparison targets (CRITICAL for H-CP* hypotheses)**

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use baseline metrics to set comparison targets
4. Design concrete experiment specification (Level 1.5)
5. Output: h-e1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
