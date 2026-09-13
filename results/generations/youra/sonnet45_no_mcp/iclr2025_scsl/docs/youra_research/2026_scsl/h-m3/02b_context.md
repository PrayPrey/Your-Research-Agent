# Hypothesis Context: h-m3

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-04-24
**Main Hypothesis:** Loss Landscape Geometry and Spurious Correlation Robustness
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
During training, if sharp curvature exists in specific directions (H-M2), then SGD dynamics will preferentially follow locally flat directions to minimize curvature-induced gradient variance, because well-documented SGD implicit bias toward flat minima creates directional flow.

### Type
MECHANISM (Step 3 of 4)

### Rationale
Third causal link: explains optimization dynamics—WHY high A(w) solutions emerge from SGD (flatness bias) rather than being artifacts of final solutions.

---

## Verification Protocol

### Conceptual Test
1. Track SGD trajectories during training via gradient direction logging
2. Measure directional bias: correlation between gradient steps and eigenvector directions
3. Calculate curvature-induced gradient variance along different directions
4. Verify that SGD steps preferentially align with low-curvature (flat) directions
5. Test early-epoch A(w) prediction of final trajectory (forecasting power)

### Success Criteria
- **Primary:** SGD steps align more with flat directions than sharp directions (measured bias)
- **Secondary:** Early A(w) (10% training) predicts final robustness (incremental R²>10% beyond λ_max)

### Variables
- **Independent Variable:** Local curvature landscape (flat vs sharp directions)
- **Dependent Variable:** SGD trajectory direction (measured via gradient alignment over time)
- **Controlled Variables:** Learning rate, momentum, batch size

---

## Experimental Setup (from Phase 2A via Phase 2B)

### Selected Dataset
- **Name:** Waterbirds
- **Type:** standard
- **Source:** group_DRO repository (https://github.com/kohpangwei/group_DRO)
- **Path:** Downloaded via group_DRO scripts
- **Hypothesis Fit:** Ground-truth spurious labels enable behavioral phenotyping (spurious vs core solutions). Background spurious correlation provides testbed for SGD trajectory analysis.

### Selected Model
- **Name:** ResNet-50
- **Type:** Standard CNN with skip connections
- **Source:** torchvision.models
- **Hypothesis Fit:** Li et al. show ResNets produce analyzable loss landscapes with skip connections creating flat minima. Sufficient over-parameterization for Marchenko-Pastur assumptions.

---

## Baseline & Comparison Targets

### Baseline Methods
- Standard ERM: 85-90% average, 60-75% worst-group (Waterbirds)
- Group-DRO: 75-80% worst-group (requires group labels)
- Fast Geometric Ensembling (FGE): Cyclical learning rate sampling

### Gap Analysis
H-M3 tests optimization dynamics (SGD trajectory preferences), not final performance. No direct baseline comparison needed—measures directional bias during training.

---

## Dependencies and Gate Conditions

### Prerequisites
- **h-m2** (COMPLETED): Sharp directions align with minority gradients established

### Gate Information

**Gate Type:** SHOULD_WORK
- Failure documented as limitation, workflow continues

**Consequence if Fails:** 
EXPLORE alternative optimization dynamics or reconsider SGD implicit bias assumption

**Estimated Duration:** 1 week

---

## Dependency Context

### Relationship to Other Hypotheses

**Builds on h-m2:** Uses the validated finding that sharp curvature directions align with minority gradients. H-M3 explains WHY this alignment emerges via SGD dynamics, testing the causal mechanism (flatness bias) rather than just documenting correlation.

**Enables h-m4:** If h-m3 validates that SGD flows along flat directions, then h-m4 can test whether this geometric flow predicts final robustness outcomes (geometry-phenotype coupling).

### Key Context from h-m2 (Previous Validation)

**From h-m2 validation report:**
- Gate Result: FAIL (SHOULD_WORK - documented as limitation)
- **Key Limitation:** Used random orthonormal basis instead of real Hessian eigenvectors
- Minority/majority alignments both near-zero (~1e-06) with random basis
- Mock data issues fully resolved (real Waterbirds, actual gradients)
- Remaining challenge: Requires actual Hessian eigendecomposition for meaningful results

**Critical Lesson for h-m3:**
To test SGD trajectory alignment with flat vs. sharp directions, h-m3 MUST:
1. Compute actual Hessian eigenvectors (not random basis)
2. Track gradient steps during training (not just final state)
3. Measure directional bias relative to real outlier vs. bulk eigenvectors
4. Use full training protocol (100 epochs, not lightweight 5-epoch PoC)

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS (experiment_design: NOT_STARTED)
**Workflow Status:** ACTIVE

---

## Phase 2C Usage Notes

**This context file provides:**
1. Complete hypothesis specification for experiment design
2. Gate conditions for prerequisite validation
3. Critical lessons from h-m2 (avoid random basis limitation)
4. Success criteria for evaluation design

**Phase 2C will:**
1. Design trajectory logging mechanism for SGD steps
2. Specify Hessian eigenvector computation protocol (real, not random)
3. Define directional bias metrics (alignment to flat vs. sharp directions)
4. Create early-prediction experiment (10% epoch A(w) → final robustness)
5. Output: h-m3/02c_experiment_brief.md

**Critical Requirements:**
- Must use real Hessian eigenvectors (learn from h-m2 limitation)
- Must track training dynamics (not just final checkpoints)
- Must distinguish flat (bulk) vs. sharp (outlier) eigenvector directions
- Must test forecasting power (early A(w) prediction)

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
