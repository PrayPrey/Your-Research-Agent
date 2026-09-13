# Hypothesis Context: h-e1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-04-21
**Main Hypothesis:** H-WeightDepthClassifier-v1
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under the scope of pretrained ImageNet CNNs, if we extract layer-wise weight norm statistics (mean, std, min, max of Frobenius norms) and train a binary classifier on 16 models, then test accuracy on 4 held-out models will exceed 70%, because weight distributions encode architectural depth through training history.

### Type
Existence

### Rationale
This existence hypothesis validates that weight statistics alone contain sufficient discriminative information for binary depth classification. Success demonstrates that architectural depth leaves measurable fingerprints in weight space, establishing the foundation for all subsequent mechanism tests.

---

## Verification Protocol

### Conceptual Test
1. Load 20 pretrained models from PyTorch torchvision (10 shallow, 10 deep)
2. Extract layer-wise Frobenius norms and compute mean/std/min/max features
3. Split 80/20 (16 train, 4 test) and train sklearn LogisticRegression
4. Evaluate on held-out test set and measure accuracy
5. Compare against 50% random baseline and 70% success threshold

### Success Criteria
- **Primary**: Test accuracy ≥ 70%
- **Secondary**: P2 within-family accuracy ≥ 65%, P3 random labels ≤ 55%

### Variables
- **Independent Variable:** Network Depth Category (binary: shallow ≤34 vs deep ≥50 layers)
- **Dependent Variable:** Classification Accuracy (test set %, primary metric)
- **Controlled Variables:** Training Dataset (ImageNet 1K), Feature Extraction (Frobenius norms)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** PyTorch Torchvision Pretrained Models
- **Type:** standard
- **Source:** torchvision.models API (PyTorch official)
- **Path:** torchvision.models (no file downloads)
- **Hypothesis Fit:** Provides 20+ pretrained ImageNet CNNs with standardized training, covering shallow and deep architectures across multiple families

### Selected Model
- **Name:** sklearn LogisticRegression
- **Type:** Binary classifier
- **Source:** scikit-learn (built-in)
- **Hypothesis Fit:** Simple linear classifier appropriate for EXISTENCE-tier validation, interpretable coefficients, no custom algorithms required

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Run 3 Weight Norm Correlation | \|ρ\| = 0.859, p = 0.067 (failed significance) | 5 ResNet models | Small sample size (n=5), rigorous threshold (ρ ≥ 0.90), continuous correlation instead of classification |
| Random Classifier | 50% accuracy (random guessing) | N/A | Baseline for statistical significance |

### Baseline Performance
Best baseline: Random classifier 50% accuracy (theoretical baseline)

### Gap Analysis
The correlation approach (Run 3) showed promising signal (|ρ| = 0.859) but failed statistical significance due to small sample size (n=5) and rigorous threshold. Binary classification with larger sample (n=20) should amplify the signal through extreme group comparison and provide clearer validation.

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundation hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** STOP - Document negative result, publish or route to Phase 0

**Phase Assignment:** Phase 1 - Foundation

**Estimated Duration:** 2 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the foundation hypothesis. All mechanism hypotheses (H-M1, H-M2, H-M3) depend on H-E1 passing. If H-E1 fails, the entire verification plan stops.

**Dependents:**
- H-M1: Gradient Accumulation Creates Depth-Specific Patterns
- H-M2: Architectural Constraints Create Depth-Specific Structures  
- H-M3: Normalization Effects Accumulate Differently by Depth

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
