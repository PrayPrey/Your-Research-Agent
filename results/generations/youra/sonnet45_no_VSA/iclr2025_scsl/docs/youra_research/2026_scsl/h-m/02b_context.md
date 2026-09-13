# Hypothesis Context: H-M

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-11
**Main Hypothesis:** Semantic validity predicts augmentation effectiveness
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
The mechanism operates through four causal steps: (1) Horizontal flip creates non-canonical asymmetric digit images, (2) These invalid images retain original labels creating label noise, (3) Training on label noise degrades test accuracy on affected classes, (4) Degradation magnitude increases monotonically with flip probability.

### Type
Mechanism

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
- Primary: Spearman ρ significantly negative (p<0.05), indicating monotonic dose-response
- Secondary: Degradation visible at p=0.3, stronger at p=0.5, strongest at p=0.9
- Mechanism Validation: Each causal step observable in training/test dynamics

### Variables (if applicable)
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
- **Path:** Auto-download via torchvision
- **Hypothesis Fit:** Standard benchmark dataset with known digit semantics (asymmetric vs symmetric digits), 60k train, 10k test, 10 classes, 28×28 grayscale

### Selected Model
- **Name:** Standard CNN
- **Type:** custom
- **Source:** Implemented from scratch
- **Hypothesis Fit:** Simple architecture with 2 conv layers [32,64 filters], MaxPool, Dropout [0.25,0.5], 2 FC [128→10] - sufficient capacity to learn MNIST without overfitting to augmentation noise

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
Standard CNN on MNIST without augmentation (ToTensor + Normalize only)

### Baseline Performance
~99% test accuracy (literature baseline)

### Gap Analysis
No prior work explicitly tests semantic validity of standard augmentations on MNIST. This hypothesis fills that gap by establishing dose-response relationship between flip probability and accuracy degradation.

---

## Dependencies and Gate Conditions

### Prerequisites
H-E1 (Asymmetric Digit Degradation Effect) - MUST pass before H-M can proceed

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** EXPLORE (effect exists per H-E1 but mechanism unclear)

**Phase Assignment:** Phase 2 (Sequential execution after H-E1)

**Estimated Duration:** ~2 hours

---

## Dependency Context

### Relationship to Other Hypotheses
H-M is a mechanism hypothesis that depends on H-E1 (existence hypothesis). H-E1 validates that the asymmetric digit degradation effect exists. H-M tests the complete causal chain explaining WHY that effect exists and validates the dose-response relationship. If H-E1 passes but H-M fails, the effect is real but the mechanistic explanation needs refinement.

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
5. **Baseline comparison targets (CRITICAL for H-CP* hypotheses)**

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use baseline metrics to set comparison targets
4. Design concrete experiment specification (Level 1.5)
5. Output: docs/youra_research/h-m/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
