# Hypothesis Context: H-M2

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-07-11
**Main Hypothesis:** API Contracts for ML Reproducibility
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under ML reengineering workflows, if contracts enforce metamorphic mathematical properties (softmax sums, dropout identity) via lightweight probes, then mathematical invariant violations are detected at environment-stage before training begins.

### Type
MECHANISM

### Rationale
Tests the second causal step. Metamorphic properties are version-stable mathematical guarantees that don't require full inference, enabling fast validation.

---

## Verification Protocol

### Conceptual Test
1. Implement metamorphic contracts (softmax sums to 1, dropout identity on eval mode, etc.)
2. Deploy to test repos with known mathematical invariant violations
3. Measure detection rate and execution time
4. Test version stability across library updates
5. Validate false positive rate on valid library usage

### Success Criteria
- Primary: Metamorphic contracts detect ≥70% of mathematical invariant violations
- Secondary: Execution time ≤10s, version stability across ±2 releases

### Variables (if applicable)
- **Independent Variable:** Metamorphic contract presence (enabled/disabled)
- **Dependent Variable:** Metamorphic property violation detection rate
- **Controlled Variables:** Library versions, probe complexity (≤10s constraint)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Jiang et al. 348-Defect Corpus + Live GitHub Repos
- **Type:** standard + real-world
- **Source:** Published dataset (Jiang et al. 2023) + ≥1K stars CV repos from GitHub
- **Path:** Phase 1: Retrospective coding, Phase 2: Version-Transition Benchmark, Phase 3: Randomized trial on live repos
- **Hypothesis Fit:** Provides real-world metamorphic property violations for detection validation

### Selected Model
- **Name:** API contract validation framework
- **Type:** Metamorphic property enforcement via lightweight probes
- **Source:** Pre-built library for PyTorch/HuggingFace/JAX + auto-generation pipeline
- **Hypothesis Fit:** Contracts are the 'model' — hypothesis tests their defect detection efficacy for mathematical invariants

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
| H-M1 (Structural Contracts) | Structural invariant validation at import time | Detection rate ≥80% for structural API defects |

### Baseline Performance
H-M1 (prerequisite) achieves ≥80% detection for structural violations. H-M2 targets complementary category: mathematical invariants (softmax sums, dropout behavior).

### Gap Analysis
H-M1 detects structural violations (shapes, types, nulls). H-M2 extends to mathematical properties that structural checks cannot validate.

---

## Dependencies and Gate Conditions

### Prerequisites
- H-M1 (Structural Invariant Validation at Import Time) - MUST PASS

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** If detection rate <50%, document limitation — structural contracts still viable

**Phase Assignment:** Phase 2 (Mechanisms)

**Estimated Duration:** 1 week

---

## Dependency Context

### Relationship to Other Hypotheses
- Builds on H-M1 (structural validation foundation)
- Prerequisite for H-M3 (cross-library composition validation)
- Part of 4-step causal chain: H-E1 → H-M1 → H-M2 → H-M3 → H-M4

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
5. Output: docs/youra_research/h-m2/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
