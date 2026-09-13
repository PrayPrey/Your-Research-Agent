# Hypothesis Context: h-m2

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-03-21
**Main Hypothesis:** CLT Stress-Test Framework - Empirical Validation
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
SGD with fixed hyperparameters produces finite-variance test accuracy distribution with Gaussian-like tails, validated through excess kurtosis 95% CI ∈ [−2, +2].

### Type
MECHANISM

### Rationale
This validates the second causal link. Even with deterministic training, different initializations must traverse different paths through the loss landscape. This explains how initial weight variance propagates through training to final model variance.

---

## Verification Protocol

### Conceptual Test
Under deterministic SGD with different initial weights (from H-M1), if training proceeds for 10 epochs, then optimization trajectories will diverge measurably, converging to different local minima, because non-convex loss landscapes have multiple minima and initialization determines which basin of attraction the optimizer enters.

### Success Criteria
- **Primary:** Final weight configurations differ significantly across seeds (mean pairwise distance > 0, p < 0.05)
- **Secondary:** Loss trajectories show measurable divergence (CV of final loss ≥ 1%)

### Variables
- **Independent Variable:** Initial Weight Configuration (from H-M1)
- **Dependent Variable:** Final Weight Configuration (after 10 epochs), Training Loss Trajectory
- **Controlled Variables:** Learning rate (0.01), Momentum (0.9), Batch size (64), Epochs (10)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** MNIST + Fashion-MNIST (Dual-Dataset Design)
- **Type:** standard
- **Source:** torchvision.datasets.MNIST / torchvision.datasets.FashionMNIST
- **Path:** Downloaded automatically via PyTorch
- **Hypothesis Fit:** MNIST provides clean pedagogical baseline (simple task, ~98% accuracy), Fashion-MNIST provides task difficulty sensitivity test (same dimensionality, harder task ~90% accuracy). Isomorphic datasets (28×28, 10 classes, 60K train) enable controlled comparison of variance vs task difficulty without confounding architecture changes.

### Selected Model
- **Name:** Simple MLPs (Dual-Architecture Design)
- **Type:** Feedforward Neural Network
- **Source:** Custom PyTorch implementation
- **Hypothesis Fit:** 1-layer MLP (784→128→10): Simplest non-trivial architecture, ~196K params, pedagogical baseline. 2-layer MLP (784→256→128→10): Slightly deeper (~400K params) to test architecture sensitivity. Both use ReLU activation, cross-entropy loss, fixed initialization (controlled by seed). Rationale: 1-layer alone may be too simple (variance too small), 2-layer provides robustness check while maintaining <25min runtime.

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| Picard 2021 - torch.manual_seed(3407) optimal seed search | Scanned 10^4 seeds on CIFAR-10 ResNet-18, found seed-dependent variance despite determinism | CIFAR-10 |
| Rajput 2023 - Decided sample size validation | Validated N≥30 criterion across 15 ML benchmarks (effect size ≥0.5, accuracy ≥80%) | 15 diverse datasets (medical imaging, tabular, etc.) |
| Ghasemzadeh 2023 - Generalizable ML Models via nested k-fold | Nested k-fold reduces required sample size by ~50% for stable model selection | Multiple benchmarks |

### Baseline Performance
No direct performance baseline - this is a mechanism validation hypothesis testing whether optimization trajectories diverge under different initializations.

### Gap Analysis
Previous work (Picard 2021, Rajput 2023) demonstrates seed-dependent variance exists, but does not validate the mechanism by which different initializations lead to different outcomes. H-M2 fills this gap by directly measuring optimization trajectory divergence and final weight configuration differences.

---

## Dependencies and Gate Conditions

### Prerequisites
- **h-m1** (PASSED): Seed Independence - confirms that different seeds create different initial weight configurations

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** EXPLORE - MNIST MLP may have dominant attractor despite different initializations

**Phase Assignment:** Phase 2C → 3 → 4

**Estimated Duration:** 0 seconds (analysis only - reuses h-m1 training data)

---

## Dependency Context

### Relationship to Other Hypotheses

h-m2 is the second link in the causal chain:
- **Depends on:** h-m1 (initial weights must differ)
- **Enables:** h-m3 (stable variance estimation requires different local minima to exist)

Without h-m2, we cannot explain HOW initial weight variance (h-m1) propagates through training to produce test accuracy variance. This validates the causal mechanism.

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** BLOCKED (prerequisite h-m1 now PASSED, ready to proceed)
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
5. Output: docs/youra_research/20260318_question/h-m2/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
