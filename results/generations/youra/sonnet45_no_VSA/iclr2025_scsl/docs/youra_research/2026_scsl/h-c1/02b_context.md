# Hypothesis Context: h-c1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-11
**Main Hypothesis:** Semantic Validity in Data Augmentation
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Rotation ±15° augmentation does NOT cause differential degradation on asymmetric digits (positive control isolating semantic effect)

### Type
CONDITION

### Rationale
This hypothesis serves as a positive control for H-E1. It validates that rotation augmentation, which preserves semantic validity (rotated digits remain recognizable as their original class), does NOT selectively harm asymmetric digits. This isolates the semantic invalidity mechanism: if rotation shows no differential effect while horizontal flip does (H-E1), it confirms that semantic invalidity, not general augmentation or asymmetry itself, causes degradation.

---

## Verification Protocol

### Conceptual Test
Train models on MNIST with rotation ±15° augmentation, measure per-class test accuracy, and compare asymmetric digit performance to baseline. Statistical test should show NO significant differential degradation on asymmetric digits {2,3,5,6,7,9} compared to symmetric digits {0,1,8}.

### Success Criteria
- **Primary:** NO significant difference in asymmetric digit accuracy degradation between rotation and baseline conditions (Wilcoxon p ≥ 0.05 OR Cohen's d < 0.5)
- **Secondary:** Symmetric digit accuracy stable across conditions
- **Control Validation:** Overall accuracy similar or improved vs baseline (rotation is a valid augmentation)

### Variables (if applicable)
- **Independent Variable:** Augmentation Type (Baseline vs Rotation ±15°), Digit Symmetry Group (Symmetric vs Asymmetric)
- **Dependent Variable:** Per-Class Test Accuracy (0-100% for each of 10 classes)
- **Controlled Variables:** Model Architecture (Standard CNN), Training Hyperparameters (Adam, lr=0.001, batch=64, epochs=30), Random Seeds (n=5)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** MNIST
- **Type:** standard
- **Source:** torchvision.datasets (auto-download)
- **Path:** Auto-downloaded to cache
- **Hypothesis Fit:** Contains symmetric {0,1,8} and asymmetric {2,3,5,6,7,9} digits for differential effect testing

### Selected Model
- **Name:** Standard CNN
- **Type:** custom
- **Source:** PyTorch implementation
- **Hypothesis Fit:** 2 conv layers [32,64 filters], MaxPool, Dropout [0.25,0.5], 2 FC [128→10] — sufficient capacity for MNIST without overfitting

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
- **Baseline Condition:** ToTensor + Normalize only (no augmentation)
- **Alternative Control (Optional):** Translation/Brightness augmentation (if rotation control fails)

### Baseline Performance
- **Expected Baseline Accuracy:** ~99% test accuracy on MNIST (standard CNN without augmentation)
- **Per-Class Baseline:** All digit classes ~98-99% accuracy

### Gap Analysis
**Rotation should maintain or improve overall accuracy** (~99% or better) while showing NO differential effect on asymmetric vs symmetric digits. Any degradation should be uniform across all digit classes.

---

## Dependencies and Gate Conditions

### Prerequisites
None (this is a positive control for H-E1, but can be validated independently)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** CRITICAL - If rotation DOES cause differential degradation on asymmetric digits, the semantic invalidity mechanism is NOT isolated. This invalidates H-E1's interpretation. Response: Use alternative control (translation, brightness) or ABORT hypothesis.

**Phase Assignment:** Phase 4 (Coding & PoC Validation)

**Estimated Duration:** ~2 hours

---

## Dependency Context

### Relationship to Other Hypotheses
**Positive Control for H-E1:** h-c1 validates that rotation (semantically valid augmentation) does NOT harm asymmetric digits, while H-E1 tests that horizontal flip (semantically invalid augmentation) DOES harm asymmetric digits. This comparison isolates the semantic invalidity mechanism.

**Risk Mitigation:** R5 in Phase 2B Risk Analysis — "Rotation Control Invalidity". If this hypothesis fails, H-E1's interpretation becomes ambiguous.

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS (experiment_design phase)
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
5. Output: /workspace/TEST_scsl/docs/youra_research/h-c1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
