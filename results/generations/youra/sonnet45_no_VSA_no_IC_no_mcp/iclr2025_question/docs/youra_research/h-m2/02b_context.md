# Hypothesis Context: H-M2

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-25
**Main Hypothesis:** H-PilotGates-v1
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under hypotheses that reach Gate 2 (100 samples), if we apply Bayesian updates combining Gate 1 prior P(O_full | O_10) with Gate 2 likelihood P(O_100 | O_full), then posterior prediction error will be >40% lower than Gate 1 prior error, because Bayesian inference reduces uncertainty by incorporating new evidence.

### Type
Mechanism

### Rationale
Tests incremental refinement claim. If Gate 2 data doesn't improve predictions, Bayesian updates add complexity without value.

---

## Verification Protocol

### Conceptual Test
1. For hypotheses with Gate 2 data (100 samples), compute Gate 1 prediction error.
2. Apply Bayesian update with O_100 as likelihood, compute Gate 2 posterior prediction.
3. Compute Gate 2 prediction error.
4. Measure error reduction: (Error_G1 - Error_G2) / Error_G1 × 100%.
5. Test if mean reduction >40% via paired t-test (p <0.05).

### Success Criteria
- Primary: Mean error reduction >40% (paired t-test p <0.05)
- Secondary: At least 10 hypotheses with Gate 2 data for statistical power

### Variables (if applicable)
- **Independent Variable:** Gate stage (Gate 1 prior vs Gate 2 posterior)
- **Dependent Variable:** Prediction error |O_pred - O_full| / O_full
- **Controlled Variables:** Bayesian model (Gaussian prior/likelihood), hypothesis type

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Retrospective ML Projects Corpus (custom)
- **Type:** custom
- **Source:** Papers with Code leaderboards + ML conference papers (NeurIPS, ICML, ICLR)
- **Path:** N/A (meta-dataset of published results)
- **Hypothesis Fit:** Framework validation requires past hypotheses with BOTH micro-pilot (10-sample), Gate 2 (100-sample), and full-scale overhead measurements. Target: subset with Gate 2 data (≥10 hypotheses).

### Selected Model
- **Name:** Bayesian Overhead Predictor
- **Type:** statistical model
- **Source:** Implemented using scipy.stats Gaussian priors/likelihoods
- **Hypothesis Fit:** Tests Bayesian inference for uncertainty reduction across gates.

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
Gate 1 Prior Prediction (from H-M1) - Linear extrapolation O_pred = k × O_10

### Baseline Performance
Gate 1 prediction error (from H-M1 validation results)

### Gap Analysis
If Bayesian updates do NOT reduce error >40%, framework adds complexity without value (falls back to Gate 1 only).

---

## Dependencies and Gate Conditions

### Prerequisites
- H-M1 (Micro-Pilot Overhead Correlates with Full-Scale Overhead)

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** Framework still works with Gate 1 only (nice-to-have refinement, not core claim)

**Phase Assignment:** Phase 2 - Mechanisms

**Estimated Duration:** Week 4

---

## Dependency Context

### Relationship to Other Hypotheses
Builds on H-M1 (valid extrapolation from O_10). Tests whether adding Gate 2 (O_100) improves predictions via Bayesian updates.

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
5. Output: h-m2/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
