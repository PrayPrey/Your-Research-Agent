# Hypothesis Context: h-m1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-03-21
**Main Hypothesis:** CLT Stress-Test Framework - Empirical Validation
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under full determinism (PyTorch seed control), if different random seeds are used for initialization, then initial weight configurations will differ measurably across the 30 training runs, because torch.manual_seed(seed) is the ONLY source of variance under deterministic training.

### Type
MECHANISM

### Rationale
This validates the first link in the causal chain. If initial weights don't differ, there's no mechanism to produce test accuracy variance. Confirms that PyTorch determinism is working correctly and seed initialization is the controlled randomness source.

---

## Verification Protocol

### Conceptual Test
1. Initialize the same MLP architecture with all 30 seeds (0-29)
2. Extract initial weight tensors immediately after model initialization (before any training)
3. Compute pairwise Euclidean distances between all weight configurations (30 choose 2 = 435 pairs)
4. Test if mean pairwise distance > 0 with statistical significance (t-test vs null hypothesis of zero distance)

### Success Criteria
- **Primary:** Mean pairwise distance > 0 with p < 0.05 (weights differ across seeds)
- **Secondary:** Distance distribution shows no clustering (confirms independence)

### Variables (if applicable)
- **Independent Variable:** Random Seed (30 levels: 0-29)
- **Dependent Variable:** Initial Weight Configuration (weight tensor Euclidean distances between seed pairs)
- **Controlled Variables:** Model architecture, initialization method (PyTorch defaults)

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
- Picard 2021 - torch.manual_seed(3407) optimal seed search: Scanned 10^4 seeds on CIFAR-10 ResNet-18, found seed-dependent variance despite determinism (CIFAR-10)
- Rajput 2023 - Decided sample size validation: Validated N≥30 criterion across 15 ML benchmarks (effect size ≥0.5, accuracy ≥80%) (15 diverse datasets)
- Ghasemzadeh 2023 - Generalizable ML Models via nested k-fold: Nested k-fold reduces required sample size by ~50% for stable model selection (Multiple benchmarks)

### Baseline Performance
Not applicable - this is a mechanism verification hypothesis testing seed independence, not a performance comparison.

### Gap Analysis
This hypothesis fills the gap in validating the fundamental assumption that random seed initialization creates truly independent training runs under PyTorch determinism.

---

## Dependencies and Gate Conditions

### Prerequisites
- **h-e1** (FAILED): Baseline Variance Measurability - Must establish that measurable variance exists before validating the mechanism that produces it.

**Note:** Prerequisite h-e1 has FAILED with gate MUST_WORK. This hypothesis (h-m1) is currently BLOCKED.

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** PIVOT - investigate PyTorch determinism failures, check seed control implementation

**Phase Assignment:** Phase 2C → 3 → 4

**Estimated Duration:** 20 seconds

---

## Dependency Context

### Relationship to Other Hypotheses
H-M1 is the first mechanism hypothesis in the causal chain. It validates that seed initialization creates independent weight configurations, which is prerequisite for:
- **h-m2** (Different Initializations Lead to Different Optimization Trajectories): Depends on h-m1 proving initial weight variance exists
- **h-m3** (CLT-Predicted Slope): Requires both h-m1 and h-m2 to validate the full causal chain

H-M1 builds on:
- **h-e1** (Baseline Variance Measurability): Must establish variance exists before validating its mechanism

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** BLOCKED (prerequisite h-e1 FAILED)
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
5. Output: /home/anonymous/YouRA_results_new_4_sonnet45/TEST_question/docs/youra_research/20260318_question/h-m1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
