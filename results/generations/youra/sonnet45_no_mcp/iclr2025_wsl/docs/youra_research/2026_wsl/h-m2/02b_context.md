# Hypothesis Context: H-M2

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-04-21
**Main Hypothesis:** H-WeightDepthClassifier-v1
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under pretrained CNN architectures, if residual connections (ResNet), dense connections (DenseNet), and bottleneck layers exist in deep models but not shallow models, then weight structures will exhibit depth-specific patterns, because architectural constraints shape weight organization.

### Type
Mechanism

### Rationale
Tests whether architectural differences (residual/dense connections) contribute to classification. Validates structural hypothesis independent of gradient flow.

---

## Verification Protocol

### Conceptual Test
1. Compare within-family accuracy (ResNet-only, VGG-only, DenseNet-only)
2. Test if VGG models (no residual connections) still classify correctly
3. Analyze weight norm patterns specific to residual/dense connections
4. Measure architecture-specific feature contributions

### Success Criteria
- Primary: Architecture features contribute to classification (within-family ≥ 65%)
- Secondary: VGG classification success validates depth signal over architecture type

### Variables (if applicable)
- **Independent Variable:** Architecture type (ResNet/DenseNet with residual/dense vs VGG without)
- **Dependent Variable:** Weight structure patterns
- **Controlled Variables:** Depth category, training dataset

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** PyTorch Torchvision Pretrained Models
- **Type:** standard
- **Source:** torchvision.models (PyTorch official)
- **Path:** torchvision.models API (no file downloads)
- **Hypothesis Fit:** Provides 20+ pretrained ImageNet CNNs with standardized training, covering shallow and deep architectures across multiple families (ResNet, VGG, DenseNet)

### Selected Model
- **Name:** sklearn LogisticRegression
- **Type:** Binary classifier
- **Source:** scikit-learn (built-in)
- **Hypothesis Fit:** Simple linear classifier appropriate for mechanism validation, interpretable coefficients, tests architectural feature contributions

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
- Run 3 Weight Norm Correlation: |ρ| = 0.859, p = 0.067 (failed significance), 5 ResNet models
- Random Classifier: 50% accuracy (random guessing baseline)

### Baseline Performance
Random classifier achieves 50% accuracy (theoretical random guessing baseline for binary classification)

### Gap Analysis
H-M2 tests whether architectural constraints (residual/dense connections) contribute to the depth classification established by H-E1. This mechanism hypothesis validates structural patterns independent of gradient flow (H-M1).

---

## Dependencies and Gate Conditions

### Prerequisites
- H-M1 (Gradient Accumulation Creates Depth-Specific Patterns)

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** Document as limitation, focus on H-M1/H-M3

**Phase Assignment:** Phase 2 - Core Mechanisms

**Estimated Duration:** 1 week (Week 4 in timeline)

---

## Dependency Context

### Relationship to Other Hypotheses
H-M2 is the second mechanism hypothesis in a sequential causal chain:
- Depends on H-M1 (gradient accumulation mechanism)
- Enables H-M3 (normalization effects)
- Tests architectural constraints as independent mechanism alongside gradient flow

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
5. Output: h-m2/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
