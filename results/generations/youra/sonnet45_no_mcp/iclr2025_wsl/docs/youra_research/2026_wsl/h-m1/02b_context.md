# Hypothesis Context: H-M1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-04-21
**Main Hypothesis:** H-WeightDepthClassifier-v1
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under pretrained CNN training, if gradient transformations accumulate across 50+ layers (deep) versus <34 layers (shallow), then weight magnitude patterns will differ measurably, because backpropagation through more layers creates characteristic gradient flow signatures.

### Type
Mechanism

### Rationale
Tests whether gradient accumulation—the first proposed mechanism—contributes to classification success. Validates theoretical link between depth and weight update histories.

---

## Verification Protocol

### Conceptual Test
1. Analyze layer-wise weight norm progression from input to output layers
2. Compare gradient flow depth (shallow vs deep) using layer-wise statistics
3. Test if randomly initialized models (no training) show same patterns
4. Measure classification accuracy on gradient-related features only

### Success Criteria
- Primary: Gradient-based features contribute to classification (accuracy > baseline)
- Secondary: Randomly initialized models fail to classify (accuracy ≤ 55%)

### Variables
- **Independent Variable:** Layer count during training (depth proxy)
- **Dependent Variable:** Weight magnitude distribution patterns
- **Controlled Variables:** Architecture family, training dataset

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** PyTorch Torchvision Pretrained Models
- **Type:** standard
- **Source:** torchvision.models (PyTorch official)
- **Path:** torchvision.models API (no file downloads)
- **Hypothesis Fit:** Provides 20+ pretrained ImageNet CNNs with standardized training, covering shallow and deep architectures across multiple families

### Selected Model
- **Name:** sklearn LogisticRegression
- **Type:** Binary classifier
- **Source:** scikit-learn (built-in)
- **Hypothesis Fit:** Simple linear classifier appropriate for MECHANISM-tier validation, interpretable coefficients, no custom algorithms required

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| H-E1 (Foundation) | Test accuracy ≥ 70% (prerequisite) | 16 train, 4 test from 20 pretrained models |
| Random Classifier | 50% accuracy (random guessing) | N/A |

### Baseline Performance
H-E1 must pass with ≥70% test accuracy using all weight statistics (mean, std, min, max of Frobenius norms). H-M1 tests gradient-specific features.

### Gap Analysis
H-E1 establishes that weight statistics enable classification. H-M1 isolates gradient accumulation mechanism by testing gradient-related features only (layer-wise progression patterns).

---

## Dependencies and Gate Conditions

### Prerequisites
- H-E1 (Foundation) - MUST pass before H-M1 can begin

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** Investigate alternative mechanisms (architecture/normalization)

**Phase Assignment:** Phase 2 - Core Mechanisms

**Estimated Duration:** 1 week

---

## Dependency Context

### Relationship to Other Hypotheses
H-M1 is the first mechanism hypothesis in a sequential chain:
- Depends on H-E1 (Foundation) proving classification is possible
- Enables H-M2 (Architectural Constraints) to test structural mechanisms
- Together with H-M2 and H-M3, forms complete causal explanation

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
5. Baseline comparison targets (H-E1 results)

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Use H-E1 results as baseline for gradient feature contribution
4. Design concrete experiment specification (Level 1.5)
5. Output: h-m1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential (H-M1 tests gradient contribution beyond H-E1)
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: MANDATORY - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
