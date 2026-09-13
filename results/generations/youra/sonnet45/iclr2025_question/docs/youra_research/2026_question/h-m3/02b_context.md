# Hypothesis Context: H-M3

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-03-21
**Main Hypothesis:** Classical Variance Baseline for Neural Network Training Stochasticity
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under bootstrap resampling (B=1000) of the 30 test accuracy values from different local minima (H-M2), if we estimate confidence intervals on variance σ², then CI width will be ≤ 50% of the point estimate for all 4 conditions, because N=30 provides sufficient sample size for stable variance estimation per Rajput 2023's criterion.

### Type
MECHANISM

### Rationale
This validates the third causal link and measurement stability. Measurable variance (H-E1) arising from distinct minima (H-M2) must be reliably estimable. This proves the methodology can be used as a baseline for UQ method comparison.

---

## Verification Protocol

### Conceptual Test
1. For each of the 4 conditions, take the 30 test accuracy values from H-E1
2. Perform bootstrap resampling with B=1000 resamples to estimate variance σ²
3. Compute 95% confidence interval as [percentile(2.5), percentile(97.5)]
4. Calculate CI width = (CI_upper - CI_lower) / σ² × 100% for each condition
5. Verify CI width ≤ 50% for all 4 conditions

### Success Criteria
- **Primary:** CI width ≤ 50% for all 4 conditions (stable variance estimation)
- **Secondary:** Statistical triangulation agreement (bootstrap, permutation, Bayesian methods agree within 10%)

### Variables
- **Independent Variable:** Test Accuracy Sample (30 values per condition from H-E1)
- **Dependent Variable:** Bootstrap CI Width = (CI_upper - CI_lower) / σ² × 100%
- **Controlled Variables:** Bootstrap resamples (B=1000), Confidence level (95%)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** MNIST + Fashion-MNIST (Dual-Dataset Design)
- **Type:** standard
- **Source:** torchvision.datasets.MNIST / torchvision.datasets.FashionMNIST
- **Path:** Downloaded automatically via PyTorch (from h-e1 artifacts)
- **Hypothesis Fit:** Isomorphic datasets (28×28, 10 classes, 60K train) enable controlled comparison of variance vs task difficulty

### Selected Model
- **Name:** Simple MLPs (Dual-Architecture Design)
- **Type:** Feedforward Neural Network
- **Source:** Custom PyTorch implementation (from h-e1 artifacts)
- **Hypothesis Fit:** 1-layer MLP (784→128→10): ~196K params, pedagogical baseline. 2-layer MLP (784→256→128→10): ~400K params to test architecture sensitivity

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
- **Picard 2021** - torch.manual_seed(3407) optimal seed search: Scanned 10^4 seeds on CIFAR-10 ResNet-18, found seed-dependent variance despite determinism
- **Rajput 2023** - Decided sample size validation: Validated N≥30 criterion across 15 ML benchmarks (effect size ≥0.5, accuracy ≥80%)
- **Ghasemzadeh 2023** - Generalizable ML Models via nested k-fold: Nested k-fold reduces required sample size by ~50% for stable model selection

### Baseline Performance
Rajput 2023 empirically validated N≥30 across 15 ML benchmark datasets with effect size ≥0.5. Power analysis: For one-sample variance test with N=30, α=0.05, σ_true=0.1%, power ≈ 0.85 (chi-squared distribution).

### Gap Analysis
No direct variance estimation stability baseline exists for neural networks. This hypothesis establishes the methodology that future UQ methods should be compared against.

---

## Dependencies and Gate Conditions

### Prerequisites
- **h-m2** (COMPLETED): Different local minima must exist to produce variance to estimate

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** EXPLORE - N=30 may be insufficient for stable estimation despite Rajput 2023, add N sensitivity analysis

**Phase Assignment:** Phase 4

**Estimated Duration:** 0 seconds (analysis only - reuses h-e1 test accuracy data)

---

## Dependency Context

### Relationship to Other Hypotheses
H-M3 is the final mechanism hypothesis in the causal chain:
- H-E1 establishes variance exists
- H-M1 validates seed initialization creates different weights
- H-M2 validates different weights lead to different local minima
- **H-M3 validates variance estimates from different minima are stable**

This completes the measurement infrastructure validation, proving that classical variance estimation is reliable for neural network training stochasticity.

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
5. Output: /home/anonymous/YouRA_results_new_4_sonnet45/TEST_question/docs/youra_research/20260318_question/h-m3/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
