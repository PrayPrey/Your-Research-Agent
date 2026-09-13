# Hypothesis Context: h-e1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-05-12
**Main Hypothesis:** H-HierarchicalAlign-v1
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under conditions of intermediate task heterogeneity (mean pairwise KL divergence 0.3-1.5 between independent routing distributions), if we apply performance-weighted alignment between adapter-specific routing biases and expert utilization patterns, then joint LoRA-MoE training achieves super-additive efficiency gains exceeding the additive baseline by ≥2% absolute accuracy.

### Type
EXISTENCE

### Rationale
This hypothesis validates the core existence claim—that coordination produces measurable super-additive benefits beyond what LoRA and MoE provide independently. Without demonstrating super-additivity in the predicted intermediate regime, the entire coordination principle lacks empirical foundation.

---

## Verification Protocol

### Conceptual Test
1. Select 5 task triplets with intermediate heterogeneity (mean pairwise KL 0.3-1.5)
2. Train 4 conditions per triplet: Baseline, LoRA-only, MoE-only, LoRA+MoE with alignment (5 seeds each)
3. Compute 2×2 factorial ANOVA with interaction term for each triplet
4. Test statistical significance (F_interaction > 4.0, p < 0.05) AND practical significance (coordinated - additive ≥ 2%)
5. Validate that ≥70% of mid-KL triplets satisfy both significance criteria

### Success Criteria
- Primary: Interaction F > 4.0, p < 0.05 AND coordinated outperforms additive baseline by ≥2% in ≥70% of mid-KL triplets
- Secondary: No super-additivity in low-KL (<0.3) or high-KL (>1.5) triplets (regime specificity)

### Variables
- **Independent Variable:** Alignment mechanism (enabled/disabled)
- **Dependent Variable:** Super-additive gain magnitude (interaction effect from 2×2 ANOVA, % accuracy)
- **Controlled Variables:** Total parameter count, optimization steps (12K all conditions), model architecture

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Multi-task NLP Suite (15 task triplets)
- **Type:** standard
- **Source:** GLUE, SuperGLUE, code tasks, cross-domain QA/summarization/translation
- **Path:** TBD by Phase 2C
- **Hypothesis Fit:** Requires task diversity to span low/mid/high KL heterogeneity regimes. 15 triplets × 3 tasks = 45 total tasks covering NLP, code, reasoning domains.

### Selected Model
- **Name:** Foundation model with MoE layers (e.g., Mixtral-8x7B or equivalent)
- **Type:** Mixture-of-Experts transformer
- **Source:** Pre-trained checkpoint
- **Hypothesis Fit:** Requires MoE architecture with 4+ experts for meaningful routing alignment. LoRA rank 8-16 for parameter efficiency.

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Independent LoRA + MoE | Additive gains (LoRA +5%, MoE +4% = +9%) | Various downstream tasks | No adapter alignment—misses coordination benefits |
| Shared adapter (no MoE) | Established baseline | Various | No expert routing coordination—misses token-level specialization |
| MoE-only (no adapters) | Established baseline | Large-scale LM | No adapter alignment—routing is task-agnostic at token level |
| MoE-based PEFT (2024) | Structural composition | Multi-task | Structural (not functional) coordination—doesn't test regime-dependent applicability |

### Baseline Performance
Independent LoRA + MoE achieves additive gains: LoRA +5%, MoE +4% = +9% total improvement

### Gap Analysis
Current methods achieve only additive gains. Coordination hypothesis predicts super-additive gains (≥11% total, i.e., ≥2% above additive baseline) through functional alignment mechanism.

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundational hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** ABANDON (coordination hypothesis fundamentally flawed—no super-additive effect exists)

**Phase Assignment:** Phase 1 (Foundation)

**Estimated Duration:** 2-3 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
Foundational hypothesis - required by H-M-integrated (mechanism) and H-C1 (condition). If H-E1 fails, entire hypothesis chain aborts.

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
5. Output: {hypothesis_folder}/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
