# Hypothesis Context: h-m1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-11
**Main Hypothesis:** h-s1 (Semantic Validity in Data Augmentation)
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Asymmetric digit degradation increases monotonically with flip probability (dose-response relationship)

**Full Statement:** The mechanism operates through four causal steps: (1) Horizontal flip creates non-canonical asymmetric digit images, (2) These invalid images retain original labels creating label noise, (3) Training on label noise degrades test accuracy on affected classes, (4) Degradation magnitude increases monotonically with flip probability.

### Type
MECHANISM

### Rationale
This hypothesis tests the complete causal chain from augmentation to outcome, including the critical dose-response relationship that strengthens the mechanistic claim.

---

## Verification Protocol

### Conceptual Test
1. Train models at multiple flip probabilities: p=0.0, p=0.3, p=0.5, p=0.9 with n=5 seeds each
2. Measure asymmetric digit accuracy at each flip probability level
3. Compute accuracy degradation: Baseline accuracy - Flip accuracy
4. Test dose-response: Spearman rank correlation (expect ρ<0, p<0.05)
5. Verify monotonic degradation: Higher flip probability → lower accuracy

### Success Criteria
- **Primary:** Spearman ρ significantly negative (p<0.05), indicating monotonic dose-response
- **Secondary:** Degradation visible at p=0.3, stronger at p=0.5, strongest at p=0.9
- **Mechanism Validation:** Each causal step observable

### Variables
- **Independent Variable:** Flip Probability (p ∈ {0.0, 0.3, 0.5, 0.9})
- **Dependent Variable:** Asymmetric Digit Accuracy, Accuracy Degradation
- **Controlled Variables:** Random Seed (n=5), Model Architecture, Training Protocol

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** MNIST
- **Type:** standard
- **Source:** torchvision.datasets (auto-download)
- **Path:** torchvision.datasets.MNIST
- **Details:** 60k train, 10k test, 10 classes, 28×28 grayscale
- **Hypothesis Fit:** Standard benchmark for testing digit-level augmentation effects

### Selected Model
- **Name:** Standard CNN
- **Type:** custom
- **Architecture:** 2 conv layers [32,64 filters], MaxPool, Dropout [0.25,0.5], 2 FC [128→10]
- **Hypothesis Fit:** Simple architecture suitable for MNIST, sufficient capacity for learning

---

## Baseline & Comparison Targets

### Baseline Methods
- **Baseline:** ToTensor + Normalize only (no augmentation)
- **Positive Control:** RandomRotation(±15°) + Normalize (semantically valid augmentation)

### Baseline Performance
- Standard CNN on MNIST without augmentation: ~99% test accuracy (literature baseline)

### Gap Analysis
No prior work explicitly tests semantic validity of standard augmentations on MNIST. This experiment fills that gap.

---

## Dependencies and Gate Conditions

### Prerequisites
- **H-E1 must pass:** Existence of asymmetric digit degradation effect must be confirmed before testing mechanism

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** EXPLORE (effect exists per H-E1 but mechanism unclear)

**Phase Assignment:** Phase 2-4 (Mechanism)

**Estimated Duration:** ~2 hours

---

## Dependency Context

### Relationship to Other Hypotheses
H-M depends on H-E1 (Existence hypothesis). H-E1 must demonstrate that asymmetric digits degrade under flip augmentation. H-M then explains WHY through the 4-step causal chain and demonstrates dose-response behavior.

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** Will be updated by Phase 2C
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Dependency information for controlled experiments
4. Success criteria for evaluation design
5. Baseline comparison targets

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use baseline metrics to set comparison targets
4. Design concrete experiment specification (Level 1.5)
5. Output: h-m1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-M* (Mechanism)**: Baseline to understand improvement potential and establish dose-response curve

---

*Optimized for single-hypothesis experiment design*
