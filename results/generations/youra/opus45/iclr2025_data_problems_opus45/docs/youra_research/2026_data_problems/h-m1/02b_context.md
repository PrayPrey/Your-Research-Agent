# Hypothesis Context: h-m1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-03-26
**Main Hypothesis:** Multi-Objective Pareto Trade-offs in Finite-Compute Data Attribution
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
In convex settings (logistic regression), cross-metric partial correlations corr(rho_r, rho_m | budget) >= 0.95 at all compute levels, establishing baseline coupling.

### Type
MECHANISM

### Rationale
This establishes the baseline expectation. Convex coupling proves that metrics CAN be correlated when geometry is simple, making deep network decoupling meaningful by contrast.

---

## Verification Protocol

### Conceptual Test
1. Extract features from pre-trained ResNet-18 and train logistic regression on CIFAR-10.
2. Compute exact LOO influence (closed-form solution available for convex models).
3. Run attribution approximations at varying compute budgets.
4. Compute cross-metric partial correlations at each budget level.
5. Verify correlation >= 0.95 across all budget levels.

### Success Criteria
- Primary: corr(rho_r, rho_m | budget) >= 0.95 at all 5 compute levels
- Secondary: R^2 from single-error-axis regression >= 0.95

### Variables (if applicable)
- **Independent Variable:** Compute budget (10-100 gradient-equivalents), Attribution approximation method
- **Dependent Variable:** Cross-metric partial correlation corr(rho_r, rho_m | budget)
- **Controlled Variables:** Logistic regression on CIFAR-10 features, Fixed regularization

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** CIFAR-10
- **Type:** standard
- **Source:** torchvision
- **Path:** Loaded via standard APIs
- **Hypothesis Fit:** Standard benchmark with manageable size for LOO ground truth estimation

### Selected Model
- **Name:** Logistic Regression (on ResNet-18 extracted features)
- **Type:** Linear classifier (convex)
- **Source:** scikit-learn or PyTorch
- **Hypothesis Fit:** Convex model with closed-form LOO influence for establishing baseline coupling

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
Attribution methods: TRAK, TracIn, IF, FastIF (same as H-E1)

### Baseline Performance
From H-E1: IF vs FastIF shows crossings at all 5 compute levels in non-convex (ResNet-18) setting

### Gap Analysis
H-M1 establishes that in convex settings, these methods should NOT show crossings (high correlation expected)

---

## Dependencies and Gate Conditions

### Prerequisites
- h-e1: VALIDATED (PASS) - Demonstrated Pareto trade-offs exist in non-convex setting

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** PIVOT: Redefine metrics (if correlation < 0.90 in convex, metrics are definitionally inconsistent)

**Phase Assignment:** Phase 2 (Mechanism)

**Estimated Duration:** 2 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
- **Prerequisite for:** H-M2 (Deep Network Decoupling)
- **Builds on:** H-E1 (Pareto Trade-offs Exist) - Uses established experimental framework
- **Purpose:** Establishes convex baseline to contrast with H-M2's deep network decoupling test

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS (experiment_design)
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
5. Output: h-m1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

## Previous Hypothesis Results (h-e1)

From h-e1 validation (PASS):
- IF vs FastIF shows crossings at 5 budget levels (10, 25, 50, 75, 100)
- IF achieves higher rank preservation (rho_r), FastIF achieves higher magnitude fidelity (rho_m)
- Demonstrates clear Pareto trade-off in non-convex ResNet-18 setting
- Key insight: Crossings exist when geometry is non-convex; H-M1 tests if they disappear in convex

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
