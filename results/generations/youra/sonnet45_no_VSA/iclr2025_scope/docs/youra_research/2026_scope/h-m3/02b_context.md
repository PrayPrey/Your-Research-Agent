# Hypothesis Context: H-M3

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-11
**Main Hypothesis:** H-APIContracts-v1
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under ML reengineering workflows, if cross-library composition-level contracts validate binding assumptions (device placement, tensor layout consistency), then cross-library interaction defects are detected at environment-stage.

### Type
MECHANISM

### Rationale
Tests the third causal step. Many API defects arise from cross-library interactions (Torch + CUDA + Transformers version triads), requiring composition-level validation.

---

## Verification Protocol

### Conceptual Test
1. Implement composition-level contracts for common library triads (PyTorch + CUDA + Transformers)
2. Deploy to test repos with known cross-library interaction failures
3. Measure detection rate for composition-level defects
4. Validate execution time ≤10s for composition checks
5. Test robustness across version combinations

### Success Criteria
- **Primary:** Composition contracts detect ≥60% of cross-library interaction defects
- **Secondary:** Execution time ≤10s, applicable to ≥3 distinct repos

### Variables (if applicable)
- **Independent Variable:** Composition-level contract presence (enabled/disabled)
- **Dependent Variable:** Cross-library defect detection rate
- **Controlled Variables:** Library version combinations, device configurations

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Jiang et al. 348-Defect Corpus + Live GitHub Repos
- **Type:** standard + real-world
- **Source:** Published dataset (Jiang et al. 2023) + ≥1K stars CV repos from GitHub
- **Path:** Phase 1: Retrospective coding, Phase 2: Version-Transition Benchmark, Phase 3: Randomized trial on live repos
- **Hypothesis Fit:** Provides ecological validity (real reengineering defects); live trial tests marginal value in practice

### Selected Model
- **Name:** API contract validation framework
- **Type:** API contract validation framework
- **Source:** Pre-built library for PyTorch/HuggingFace/JAX + auto-generation pipeline
- **Hypothesis Fit:** Contracts are the 'model' — hypothesis tests their defect detection efficacy

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods

| Method | Performance | Dataset |
|--------|-------------|---------|
| No-CI (Control) | Version pinning only, no automated testing | Mirrors 75% of ML repos per Wolter et al. |
| CI-Only (Best-Practice Baseline) | pytest + integration tests + version pinning | Current best practice |
| Execution-Only (Adversarial Baseline) | Import + minimal forward pass | Catches obvious crashes, not subtle invariant violations |

### Baseline Performance
- **Best-Practice Baseline (CI-Only):** pytest + integration tests + version pinning
- **Current Practice:** 75% of ML repos lack automated testing, <50% specify dependencies (Wolter et al., 2025)
- **Gap:** 88% of environment defects are interface defects, 46% are API defects (Jiang et al., 2023)

### Gap Analysis
Many API defects arise from cross-library interactions (Torch + CUDA + Transformers version triads). Current CI-only baseline does not systematically validate composition-level invariants like device placement or tensor layout consistency across library boundaries.

---

## Dependencies and Gate Conditions

### Prerequisites
- **H-M1:** Structural Invariant Validation at Import Time (MUST_WORK gate)
- **H-M2:** Metamorphic Property Enforcement via Lightweight Probes (SHOULD_WORK gate)

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** If detection rate <40%, document as manual curation requirement

**Phase Assignment:** Phase 2 - Core Mechanisms

**Estimated Duration:** 1 week

---

## Dependency Context

### Relationship to Other Hypotheses
H-M3 is the third hypothesis in a sequential causal chain:
- **H-E1** (Foundation): Validates that ≥40% of environment-stage API defects are contractable
- **H-M1** (First mechanism): Validates structural contracts work at import time
- **H-M2** (Second mechanism): Validates metamorphic property enforcement
- **H-M3** (Third mechanism - THIS HYPOTHESIS): Validates composition-level cross-library contracts
- **H-M4** (Fourth mechanism): Validates lifecycle shift to environment-stage detection

H-M3 builds upon the proven mechanisms from H-M1 and H-M2, extending validation from single-library invariants (structural, metamorphic) to multi-library composition-level invariants (device placement, tensor layout).

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
5. Output: /workspace/TEST_scope/docs/youra_research/h-m3/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
