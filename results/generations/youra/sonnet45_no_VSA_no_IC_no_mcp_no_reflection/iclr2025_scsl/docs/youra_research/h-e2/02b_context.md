# Hypothesis Context: h-e2

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-28
**Main Hypothesis:** H-TemporalGradient-v1
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Spurious features exhibit lower gradient variance (V_spurious < V_core, variance ratio < 0.7) and lower forgetting rate than core features

### Type
EXISTENCE

### Rationale
Building on h-e1's temporal ordering foundation, this hypothesis tests whether the early convergence of spurious features is accompanied by distinctive multi-metric signatures: lower gradient variance (indicating stable, consistent learning) and lower forgetting rate (indicating more robust feature retention). These additional metrics provide richer characterization of spurious feature learning dynamics.

---

## Verification Protocol

### Conceptual Test
Measure gradient variance and forgetting rate for spurious vs core features during training on spurious correlation benchmarks, using ablation-trained networks to isolate feature-specific signals.

### Success Criteria
- V_spurious / V_core < 0.7 (F-test, p < 0.05)
- Forgetting_spurious < Forgetting_core (paired t-test, p < 0.05)
- Partial correlation test confirms forgetting is independent of E_s (not merely derived from temporal ordering)

### Variables (if applicable)
- **Independent Variable:** Feature type (spurious vs core)
- **Dependent Variable:** Gradient variance, forgetting rate
- **Controlled Variables:** Architecture (ResNet-18), optimizer (SGD), learning rate schedule, dataset

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** CMNIST
- **Type:** standard (spurious correlation benchmark)
- **Source:** torchvision.datasets or custom implementation
- **Path:** ./data/mnist
- **Hypothesis Fit:** Canonical spurious correlation benchmark with clear spurious feature (color) and core feature (digit shape)

### Selected Model
- **Name:** ResNet-18
- **Type:** CNN
- **Source:** torchvision.models
- **Hypothesis Fit:** Standard architecture used in spurious correlation literature, sufficient capacity for feature separation

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
Standard ERM (Empirical Risk Minimization) training without debiasing interventions.

### Baseline Performance
Expected: High training accuracy (~95%+), low worst-group accuracy on CMNIST (~10-30%) due to spurious correlation reliance.

### Gap Analysis
h-e2 does not aim to improve performance metrics but to characterize learning dynamics. Baseline ERM provides the training trajectory to analyze.

---

## Dependencies and Gate Conditions

### Prerequisites
- h-e1 (Temporal Ordering Foundation) MUST be completed and PASS

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** Failure documented as limitation in final paper. Multi-metric characterization remains incomplete, but temporal ordering (h-e1) alone is sufficient for mechanism hypotheses (h-m1, h-m2) and intervention (h-c1).

**Phase Assignment:** Phase 2C → 3 → 4

**Estimated Duration:** 1 week

---

## Dependency Context

### Relationship to Other Hypotheses
- **Depends on:** h-e1 (requires convergence epoch measurements E_s, E_c from ablation training)
- **Independent from:** h-e3, h-m1, h-m2 (parallel characterization)
- **Supports:** Final paper evidence strength (more comprehensive characterization of spurious feature learning)

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS (experiment design phase)
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
5. Output: h-e2/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
