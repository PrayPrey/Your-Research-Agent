# Hypothesis Context: h-e1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-11
**Main Hypothesis:** h-s1 - Semantic Validity in Data Augmentation
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
When horizontal flip augmentation is applied to MNIST training data, asymmetric digits {2,3,5,6,7,9} will show reduced test accuracy compared to baseline, while symmetric digits {0,1,8} remain unaffected.

### Type
EXISTENCE

### Rationale
This hypothesis validates the core phenomenon that semantic invalidity degrades model performance. If confirmed, it establishes that "standard" augmentations can harm accuracy when they violate domain-specific semantic constraints.

---

## Verification Protocol

### Conceptual Test
1. Train models on Baseline, Flip (p=0.5), and Rotation (±15°) conditions with n=5 seeds
2. Measure per-class test accuracy for all 10 digit classes
3. Group accuracy by symmetry: Symmetric {0,1,8} vs Asymmetric {2,3,5,6,7,9}
4. Statistical test: Wilcoxon signed-rank on asymmetric accuracy (Flip vs Baseline), require p<0.05 AND Cohen's d≥0.5
5. Verify positive control: Rotation should NOT differentially harm asymmetric digits

### Success Criteria
- **Primary:** Asymmetric digit accuracy significantly lower under Flip vs Baseline (p<0.05, d≥0.5)
- **Secondary:** Symmetric digit accuracy stable across conditions
- **Positive Control:** Rotation does NOT create differential effect

### Variables (if applicable)
- **Independent Variable:** Augmentation Type (Baseline/HorizontalFlip/Rotation±15°), Digit Symmetry Group
- **Dependent Variable:** Per-Class Test Accuracy (0-100% for each of 10 classes)
- **Controlled Variables:** Model Architecture, Training Hyperparameters

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** MNIST
- **Type:** standard
- **Source:** torchvision.datasets (auto-download)
- **Path:** Auto-downloaded via torchvision
- **Hypothesis Fit:** Perfect match - Contains symmetric {0,1,8} and asymmetric {2,3,5,6,7,9} digits for differential effect testing

### Selected Model
- **Name:** Standard CNN
- **Type:** custom
- **Source:** Custom implementation
- **Hypothesis Fit:** Standard baseline architecture for MNIST, sufficient capacity to learn digit features

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
Standard CNN on MNIST without augmentation

### Baseline Performance
~99% test accuracy (literature baseline)

### Gap Analysis
No prior work explicitly tests semantic validity of horizontal flip augmentation on MNIST. This is an exploratory experiment to establish the phenomenon.

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundational hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** ABANDON (core phenomenon does not exist)

**Phase Assignment:** Phase 4 PoC Validation

**Estimated Duration:** ~2 hours

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the foundational hypothesis. H-M (Mechanism) depends on H-E1 success. If H-E1 fails, the entire hypothesis verification stops.

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
5. Output: h-e1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
