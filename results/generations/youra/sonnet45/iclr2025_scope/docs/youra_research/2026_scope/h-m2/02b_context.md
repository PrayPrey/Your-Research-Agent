# Hypothesis Context: h-m2

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-03-18
**Main Hypothesis:** Post-Hoc Hybrid SSM-Attention Conversion
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Selective SSM with input-conditioned parameters Δ(x) = Softplus(W_Δ[Q,K,V]) can compress low-rank attention operators via adapter-based distillation while preserving Jacobian geometry (Wasserstein-2 eigenvalue distance < 0.05).

### Type
MECHANISM

### Rationale
This validates that adapter-based distillation preserves operator-level equivalence (not just output matching), ensuring converted SSMs maintain the same dynamical behavior as original attention mechanisms.

---

## Verification Protocol

### Conceptual Test
1. Train adapter W_adapt to distill Q/K/V → A/B/C/Δ on single layer (Phase 0 pilot)
2. Measure output MSE and verify exponential decay in N
3. Compute Wasserstein-2 distance between attention and SSM Jacobian eigenvalues
4. Test cross-domain stability (The Pile vs LongBench error delta <3%)

### Success Criteria
- Primary: W2 Jacobian distance < 0.05 at N=512
- Secondary: Exponential MSE decay, cross-domain error <3%

### Variables
- **Independent Variable:** SSM state size N (64-1024), adapter architecture
- **Dependent Variable:** Distillation MSE, Wasserstein-2 Jacobian distance
- **Controlled Variables:** Base layer (LLaMA L28), calibration data

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** The Pile (calibration), LongBench (evaluation)
- **Type:** standard
- **Source:** EleutherAI (The Pile), THUDM (LongBench)
- **Path:** HuggingFace datasets: pile, THUDM/LongBench
- **Hypothesis Fit:** The Pile used for LLaMA pretraining (calibration continuity), LongBench tests long-context capabilities (8K-128K)

### Selected Model
- **Name:** LLaMA-7B / LLaMA-13B
- **Type:** decoder-only Transformer
- **Source:** Meta AI (official checkpoints)
- **Hypothesis Fit:** 32-layer architecture enables deep-layer subset conversion (L≥20), widely used baseline for efficiency research

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
- Vanilla LLaMA-7B (standard quadratic attention)
- Samba-3.8B (reference: 3.73× throughput at 128K, 71.9 MMLU, 87.6 GSM8K)
- LTI SSM control (non-selective SSM with fixed A,B,C)

### Baseline Performance
Samba-3.8B achieves 3.73× throughput at 128K context with maintained accuracy on LongBench, MMLU, GSM8K benchmarks.

### Gap Analysis
This hypothesis tests whether selective SSM mechanisms can preserve operator-level geometry during attention-to-SSM conversion, enabling post-hoc transformation of existing models rather than training from scratch (as in Samba).

---

## Dependencies and Gate Conditions

### Prerequisites
- h-m1: Low-Rank Compression Mechanism (validates bounded-state assumption)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** Operator families incompatible with SSM factorization, PIVOT to LTI control comparison

**Phase Assignment:** phase_2

**Estimated Duration:** Day 6-15 (within Mechanisms phase)

---

## Dependency Context

### Relationship to Other Hypotheses
h-m2 depends on h-m1 confirming low-rank structure existence. If h-m2 succeeds, it enables h-m3 (calibration efficiency) and h-m4 (end-to-end performance). Failure requires pivoting to LTI SSM baseline comparison to isolate selectivity necessity.

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
5. Output: docs/youra_research/20260318_scope/h-m2/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
