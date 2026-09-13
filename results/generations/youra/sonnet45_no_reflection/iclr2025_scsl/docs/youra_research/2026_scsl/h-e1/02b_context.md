# Hypothesis Context: h-e1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-05-12
**Main Hypothesis:** Jacobian Stable Rank Unified Efficiency Framework
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under pretraining with explicit residual-corrected Jacobian stable rank (sr_ℓ^res) regularization, if models are trained to minimize sr_ℓ^res = ||J̃_ℓ||_F^2 / ||J̃_ℓ||_2^2 per layer, then mean stable rank reduces by ≥20% relative to baseline while maintaining iso-perplexity (≤1% deviation), because the regularization directly constrains the effective rank of layer-wise representation transformations.

### Type
EXISTENCE

### Rationale
This hypothesis validates that the proposed stable rank metric is (1) measurable with acceptable noise (CV < 15%), (2) controllable via gradient-based optimization, and (3) reducible without sacrificing model quality. It is the foundation for all downstream mechanistic claims.

---

## Verification Protocol

### Conceptual Test
1. Pretrain three 125M GPT-2 models on C4 (10B tokens): baseline, explicit sr_ℓ^res regularization, implicit control
2. Measure per-layer sr_ℓ^res every 1000 steps via Hutchinson trace (10 vectors) + randomized power iteration (5 iterations)
3. Tune regularization weight λ adaptively to maintain iso-perplexity (≤1% deviation across all variants)
4. Compute mean sr_ℓ^res reduction relative to baseline, layer-wise variance, and measurement CV
5. Validate upfront on 50M toy model that spectral norm estimation achieves CV < 15% before Phase 1 commitment

### Success Criteria
- **Primary**: Mean sr_ℓ^res reduction ≥20% in explicit regularization vs baseline, AND perplexity deviation ≤1%
- **Secondary**: Layer variance in rank reduction <2× mean (no compensatory redistribution), AND measurement CV <15%

### Variables
- **Independent Variable:** Regularization Type (baseline, explicit sr_ℓ^res penalty, implicit control via adaptive LR)
- **Dependent Variable:** Residual-Corrected Jacobian Stable Rank (sr_ℓ^res via Hutchinson trace + randomized power iteration)
- **Controlled Variables:** Perplexity (≤1% deviation), Model Width (125M, d=768), Training Corpus (C4, 10B tokens), Random Seeds (3 per variant)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** C4 (primary), The Stack (domain robustness)
- **Type:** standard
- **Source:** HuggingFace Datasets
- **Path:** allenai/c4 (10B token subset for Phase 1), bigcode/the-stack (code corpus for Phase 2 robustness)
- **Hypothesis Fit:** C4 provides standard natural language pretraining. The Stack tests domain robustness (high-entropy code). Both are existing, real datasets meeting feasibility constraints.

### Selected Model
- **Name:** Transformer (GPT-2 style decoder)
- **Type:** Autoregressive decoder-only transformer
- **Source:** HuggingFace Transformers library
- **Hypothesis Fit:** Standard architecture with clear layer-wise Jacobian structure (J_ℓ = I + J̃_ℓ due to residual connections). Enables residual-corrected stable rank computation. Pre-norm variant preferred for stable training dynamics.

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
Standard Transformer Pretraining with perplexity baseline on C4/The Stack (to be measured)

### Baseline Performance
Perplexity baseline on C4/The Stack (to be measured during experiment)

### Gap Analysis
Foundation hypothesis to validate controllability of stable rank metric before mechanistic claims.

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundation hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** The stable rank metric itself is not controllable → invalidates entire hypothesis chain → pivot to alternative structural metrics (e.g., effective rank via SVD, gradient flow analysis)

**Phase Assignment:** Phase 2C → 3 → 4 (first in sequence)

**Estimated Duration:** 3.5-5.5 months total pipeline (upfront 4 weeks measurement validation + 3 months Phase 1 + 2 months Phase 2 conditional)

---

## Dependency Context

### Relationship to Other Hypotheses
Foundation hypothesis for H-M-integrated (mechanistic propagation). H-M-integrated requires validated stable rank reduction from H-E1 to test correlation with efficiency metrics.

---

## Verification State Reference

**State File:** verification_state.yaml
**Current Status:** IN_PROGRESS (Phase 2C experiment design)
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
5. Output: /home/anonymous/YouRA_results_new_4_sonnet45_no_reflection/TEST_scsl_sonnet45_no_reflection/docs/youra_research/20260512_scsl/h-e1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
