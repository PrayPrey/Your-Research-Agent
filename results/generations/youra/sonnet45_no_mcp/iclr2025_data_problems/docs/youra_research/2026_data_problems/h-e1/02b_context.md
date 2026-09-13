# Hypothesis Context: h-e1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-04-15
**Main Hypothesis:** Gradient-Geometric Data Scheduling for Foundation Models
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under foundation model pretraining with mixed-domain corpora, if training domains are ordered from high to low diversity (measured via corpus statistics), then final model performance on multi-domain benchmarks exceeds best static mixture baseline by ≥2.0% absolute at 1B scale and ≥0.5% absolute at 7B scale, because temporal ordering enables optimization trajectory advantages.

### Type
EXISTENCE

### Rationale
This hypothesis validates the existence of the core phenomenon: that temporal ordering matters for final performance. It establishes the foundation for mechanistic investigation by demonstrating measurable improvement before exploring why it occurs.

---

## Verification Protocol

### Conceptual Test
1. Train 4 conditions (static, diversity-ranked, reversed, shuffled) at 1B with n=5 seeds
2. Measure composite performance on MMLU + Big-Bench + domain benchmarks
3. Perform statistical significance testing with Bonferroni correction
4. Repeat at 7B scale with power analysis (n=5, ≥70% power)
5. Validate ≥2.0% improvement at 1B, ≥0.5% at 7B with p<0.05

### Success Criteria
- **Primary:** Diversity-ranked > static by ≥2.0% absolute at 1B (p<0.05, 95% CI excluding zero)
- **Secondary:** Diversity-ranked > static by ≥0.5% absolute at 7B (statistically significant, power ≥70%)

### Variables (if applicable)
- **Independent Variable:** Domain Ordering Schedule (static vs diversity-ranked vs reversed vs shuffled)
- **Dependent Variable:** Composite benchmark performance (MMLU + Big-Bench + domain-specific, 0-100%)
- **Controlled Variables:** Total tokens per domain, learning rate schedule, model architecture (1B/7B), optimizer hyperparameters

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Mixed-Domain Pretraining Corpus (standard)
- **Type:** standard
- **Source:** C4 (web), GitHub (code), arXiv (scientific), BookCorpus (books), legal corpus for continual learning injection
- **Path:** publicly_available_datasets
- **Hypothesis Fit:** Multi-domain corpus enables diversity-ranked scheduling experiments with established benchmark evaluation

### Selected Model
- **Name:** Transformer Decoder (GPT-style)
- **Type:** autoregressive_language_model
- **Source:** standard_architecture
- **Hypothesis Fit:** Transformer architecture with clear gradient-based representation formation, scales validated (1B, 7B)

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Best Static Mixture | To be measured (baseline) | C4, GitHub, arXiv, BookCorpus | Ad-hoc ratio selection, no temporal dynamics, no geometric mechanism understanding |
| Two-phase training | Common practice | General → domain-specific | Sharp transitions only, no systematic schedule optimization |
| DoReMi domain reweighting | State-of-art static mixing | Multi-domain pretraining | Static ratios throughout training, no temporal composition |

### Baseline Performance
To be measured as baseline comparison

### Gap Analysis
Existing work on data mixing optimizes static ratios (DoReMi) or uses ad-hoc two-phase training, but ignores temporal dynamics and lacks optimization-theoretic grounding for schedule design.

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundation hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** STOP and reassess entire hypothesis - if no performance improvement exists, mechanism investigation is premature

**Phase Assignment:** Phase 1 (Foundation)

**Estimated Duration:** 2-3 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
Foundation hypothesis - all subsequent mechanism hypotheses (H-M1, H-M2, H-M3, H-M4) depend on H-E1 validation

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
