# Hypothesis Context: h-c1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-29
**Main Hypothesis:** H-TemporalGradient-v1
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Gradient-aware training (lr_j = lr_base * (1 - ρ_j)) matches or exceeds JTT worst-group accuracy on Waterbirds (within 1%)

### Type
CONDITION

### Rationale
This hypothesis tests whether the gradient-level temporal signature discovered in H-M1 (feature complexity mechanism) can be leveraged for a practical intervention. By modulating per-neuron learning rates based on spurious correlation strength ρ_j, gradient-aware training should suppress spurious feature learning and match or exceed the performance of existing debiasing methods like JTT (Just Train Twice).

---

## Verification Protocol

### Conceptual Test
Implement feature-selective learning rate modulation where each neuron j receives learning rate lr_j = lr_base * (1 - ρ_j), where ρ_j is the neuron-spurious correlation computed from H-M1 ablation data. Train on Waterbirds dataset and compare worst-group accuracy against three baselines: ERM (standard training), JTT, and Layer-wise Regularization.

### Success Criteria
Statistical Test 9: Paired t-test on worst-group accuracy across 10 random seeds. Success: mean(Gradient-Aware) ≥ mean(JTT) - 1% AND p < 0.05 (demonstrating non-inferiority with statistical significance).

### Variables (if applicable)
- **Independent Variable:** Training method (ERM vs JTT vs Layer-wise Regularization vs Gradient-Aware)
- **Dependent Variable:** Worst-group accuracy on Waterbirds test set
- **Controlled Variables:** Model architecture (ResNet-50), optimizer (SGD momentum 0.9), base learning rate (dataset-specific with cosine annealing), batch size, number of epochs, random seed

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Waterbirds
- **Type:** standard (spurious correlation benchmark)
- **Source:** https://github.com/kohpangwei/group_DRO (Sagawa et al. 2020)
- **Path:** To be specified in Phase 2C
- **Hypothesis Fit:** Waterbirds is the standard benchmark for worst-group accuracy evaluation in spurious correlation research. It contains bird images with spurious background correlation (landbirds on land, waterbirds on water), making it ideal for testing debiasing interventions.

### Selected Model
- **Name:** ResNet-50
- **Type:** Convolutional Neural Network (CNN)
- **Source:** torchvision.models (pretrained ImageNet weights optional)
- **Hypothesis Fit:** ResNet-50 is the standard architecture used in Waterbirds benchmarks (Sagawa et al. 2020, Liu et al. 2021). Using the same architecture ensures fair comparison with published JTT baseline results.

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
1. **ERM (Empirical Risk Minimization):** Standard training without debiasing
2. **JTT (Just Train Twice):** Two-stage training (identify error-prone examples in stage 1, upweight them in stage 2)
3. **Layer-wise Regularization:** Penalize early-layer representations to reduce spurious feature reliance

### Baseline Performance
From Sagawa et al. (2020) and Liu et al. (2021) on Waterbirds:
- ERM worst-group accuracy: ~72%
- JTT worst-group accuracy: ~86-89%
- Layer-wise Regularization: ~80-84%

### Gap Analysis
Gradient-Aware training targets JTT-level performance (~87%) with a more principled mechanism (direct gradient modulation based on spurious correlation). Success criterion allows 1% gap (≥86%) to account for implementation differences while still demonstrating competitive performance.

---

## Dependencies and Gate Conditions

### Prerequisites
- **h-m1** (MUST_WORK): Feature complexity mechanism hypothesis must pass to provide neuron-spurious correlation ρ_j values for gradient modulation.

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** SHOULD_WORK gate allows progression to Phase 5 even if gradient-aware training does not match JTT performance. Intervention validation is supporting evidence for the temporal gradient hypothesis, not a blocking requirement.

**Phase Assignment:** Phase 2C → 3 → 4 (Weeks 9-11 in verification plan)

**Estimated Duration:** 3 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
h-c1 depends on h-m1 (feature complexity mechanism) to provide ρ_j values. It is the final hypothesis in the critical path (h-e1 → h-m1 → h-c1) but runs in parallel with h-e2, h-e3, h-m2 (which depend only on h-e1).

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
5. Output: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_scsl/docs/youra_research/h-c1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
