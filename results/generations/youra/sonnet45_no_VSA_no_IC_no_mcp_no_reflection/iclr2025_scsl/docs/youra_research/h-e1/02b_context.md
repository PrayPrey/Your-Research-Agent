# Hypothesis Context: h-e1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-28
**Main Hypothesis:** H-TemporalGradient-v1
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Spurious features converge at least 2 epochs earlier than core features across all 4 datasets (CMNIST, Waterbirds, CelebA, NICO++)

### Type
EXISTENCE

### Rationale
This hypothesis establishes the foundational temporal ordering pattern that is central to the main hypothesis. If spurious features do not converge earlier than core features, the entire temporal signature approach is falsified. Testing across 4 diverse datasets (low-level color, mid-level texture, attribute-based, semantic) ensures the finding is not dataset-specific.

---

## Verification Protocol

### Conceptual Test
Ablation training on spurious correlation benchmarks:
1. Train three variants: spurious-only features, core-only features, baseline (both)
2. Measure convergence epochs E_s and E_c using gradient norm convergence criterion (gradient norm < 10% of peak for 3 consecutive epochs)
3. Statistical validation across multiple random seeds

### Success Criteria
- **Statistical Test 1**: Paired t-test on (E_s, E_c) across 10 random seeds
- **Success Criterion**: p < 0.05 AND mean(E_c - E_s) ≥ 2 epochs
- **Multi-dataset requirement**: Pattern must hold across all 4 datasets

### Variables (if applicable)
- **Independent Variable:** Feature type (spurious vs core)
- **Dependent Variable:** Convergence epoch E (defined as gradient norm < 10% of peak for 3 consecutive epochs)
- **Controlled Variables:** Dataset, model architecture (ResNet-18 for CMNIST, ResNet-50 for others), optimizer (SGD momentum 0.9), learning rate schedule (dataset-specific), batch size, random seed

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** CMNIST (Colored MNIST), Waterbirds, CelebA, NICO++
- **Type:** standard
- **Source:** 
  - CMNIST: Torchvision + color corruption (standard benchmark)
  - Waterbirds: Wilds benchmark dataset
  - CelebA: Standard attribute-based bias dataset
  - NICO++: Object-context spurious correlation benchmark
- **Path:** To be specified in Phase 2C (standard dataset download paths)
- **Hypothesis Fit:** These 4 datasets span the spectrum of spurious feature types:
  - Low-level: CMNIST (color)
  - Mid-level: Waterbirds (background texture)
  - Attribute-based: CelebA (gender-attribute correlation)
  - Semantic: NICO++ (object-context associations)

### Selected Model
- **Name:** ResNet-18 (CMNIST), ResNet-50 (Waterbirds, CelebA, NICO++)
- **Type:** Convolutional Neural Network (CNN)
- **Source:** Torchvision pretrained models (ImageNet initialization standard for spurious correlation research)
- **Hypothesis Fit:** ResNet architecture is standard baseline for spurious correlation benchmarks, allowing direct comparison with prior work (Sagawa et al. 2020, Nam et al. 2020)

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
- **ERM (Empirical Risk Minimization)**: Standard training without debiasing
- **Prior Work Reference**: Convergence dynamics not directly measured in prior work, but:
  - Nam et al. (2020) observed early spurious feature learning qualitatively
  - Sagawa et al. (2020) showed worst-group accuracy degradation early in training
  - This hypothesis quantifies the temporal gap precisely

### Baseline Performance
Not applicable (H-E1 is EXISTENCE hypothesis, not performance comparison)

Expected convergence epochs based on standard training:
- CMNIST: Typically converges in 10-20 epochs
- Waterbirds: 50-100 epochs
- CelebA: 30-50 epochs
- NICO++: 50-100 epochs

### Gap Analysis
**Expected Effect Size**: ≥2 epoch gap between E_s and E_c
**Novelty**: First work to quantify temporal ordering with precise convergence criterion
**Risk**: If E_s ≥ E_c, entire temporal hypothesis framework is invalidated

---

## Dependencies and Gate Conditions

### Prerequisites
None (H-E1 is the foundation hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** 
- Blocks h-e2, h-e3, h-m1, h-m2 (all dependent hypotheses)
- Invalidates main hypothesis H-TemporalGradient-v1
- Requires return to Phase 0 (new research direction)

**Phase Assignment:** Phase 2C → 3 → 4

**Estimated Duration:** 2 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the ROOT node in the dependency graph:

```
h-e1 (MUST_WORK, READY)
  ├─→ h-e2 (SHOULD_WORK) - Multi-metric signature validation
  ├─→ h-e3 (SHOULD_WORK) - Continuous diagnostic (GradCAM ratio)
  ├─→ h-m1 (MUST_WORK) - Feature complexity mechanism
  │     └─→ h-c1 (SHOULD_WORK) - Gradient-aware intervention
  └─→ h-m2 (SHOULD_WORK) - Architectural modulation (CNN vs ViT)
```

**Critical Path:** h-e1 → h-m1 → h-c1 (5 weeks + 1 week + 3 weeks = 9 weeks)

If H-E1 passes:
- Unlocks all dependent hypotheses
- Validates temporal ordering foundation
- Enables mechanism and intervention studies

If H-E1 fails:
- All dependent hypotheses blocked
- Main hypothesis falsified
- Phase 5 comparison cannot proceed

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS (Phase 2C initiated)
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
5. Output: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_scsl/docs/youra_research/h-e1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
