# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-03-27
**Main Hypothesis:** Memory Horizon Separation in SSM Adaptation
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under pretrained Mamba-1.4B, if we compute the local Jacobian eigenvalues across random input sequences, then the spectral memory horizon H_spec = -1/log|λ_max| is stable with CV < 0.3, because the A matrix in Mamba is input-independent diagonal.

### Type
EXISTENCE

### Rationale
This hypothesis validates that H_spec is a measurable model property, not a sequence-dependent artifact. Without stable H_spec, the entire MHSH/EUH framework collapses. This is the foundation for all subsequent mechanism hypotheses.

---

## Verification Protocol

### Conceptual Test
Load pretrained Mamba-1.4B and compute Jacobian eigenvalues at multiple token positions using autograd hooks. Calculate H_spec = -1/log|λ_max| for each of 1000 random sequences. Compute CV = std(H_spec)/mean(H_spec) and verify CV < 0.3. Cross-validate on Mamba-370M for scale consistency.

### Success Criteria
- Primary: CV(H_spec) < 0.3 across 1000 sequences
- Secondary: H_spec scales monotonically with model size

### Variables (if applicable)
- **Independent Variable:** Input sequences (1000 random samples)
- **Dependent Variable:** H_spec stability (CV metric)
- **Controlled Variables:** Model checkpoint (Mamba-1.4B), sequence length, computation method

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Multi-Query Associative Recall (MQAR)
- **Type:** synthetic (programmatic generation)
- **Source:** Custom generation following MQAR protocol
- **Path:** generated at runtime
- **Hypothesis Fit:** Controllable dependency length L, prevents low-dimensional compression with N > state_dim

### Selected Model
- **Name:** Mamba-1.4B
- **Type:** SSM
- **Source:** state-spaces/mamba
- **Hypothesis Fit:** Primary Mamba architecture with accessible eigenanalysis

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| Projection-only LoRA | Competitive on short-context NLU (~95% of full fine-tuning) | Standard NLU benchmarks |
| SDT (Sparse Dimension Tuning) | Outperforms LoRA on SSM modules | Mixed benchmarks |
| State-offset Tuning | Empirically effective | Mixed benchmarks |
| Full Fine-tuning | Upper bound reference | All benchmarks |

### Baseline Performance
No direct baseline for H_spec stability measurement - this is a novel metric.

### Gap Analysis
First work to measure and report H_spec stability across sequences for Mamba models.

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundation hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** Entire MHSH/EUH framework invalidated; workflow stops

**Phase Assignment:** Phase 2C → 3 → 4

**Estimated Duration:** 1-2 hours (eigenvalue computation)

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the foundation hypothesis. All subsequent hypotheses (H-M1 through H-M4) depend on H-E1 establishing that H_spec is a stable, measurable property.

- H-M1 (SSM State Dynamics): Requires H_spec exists
- H-M2 (LoRA Preserves Eigenvalues): Requires baseline H_spec measurement
- H-M3 (Energy Redistribution): Requires stable reference point
- H-M4 (MHSH vs EUH): Requires all above

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
