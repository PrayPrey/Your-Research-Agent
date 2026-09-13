# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-05-12
**Main Hypothesis:** AI-Idiomatic Feature Selection (AIFS) Adaptation Detection in RLHF Preference Corpora
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under RLHF preference annotation with multi-condition collection (deployed vs. naive annotators), if AIFS features are measured via automated regex extraction and preference pairs are matched by semantic cluster, then deployed-condition annotators show significantly higher conditional selection preference for AI-idiomatic features (β₄ > 0, OR ≥ 1.10, p < 0.01) compared to naive-condition annotators, because prior exposure to RLHF-optimized outputs shifts annotator preference weighting toward AI-native discourse norms.

### Type
EXISTENCE (H-E1)

### Rationale
This is the foundational existence test — without demonstrating the β₄ signal, subsequent mechanism steps are ungrounded. It tests whether the human-to-AI adaptation effect exists at all as a latent signal in HH-RLHF, using the documented online/base split as a natural experimental condition.

---

## Verification Protocol

### Conceptual Test
1. Extract AIFS features (structured lists, safety-prefaces, CoT markers) via regex from all candidate responses in HH-RLHF helpful-base and helpful-online splits (full dataset, 160K+ pairs).
2. Cluster prompts using frozen all-MiniLM-L6-v2 at cosine ≥ 0.85 threshold; compute ΔAIFS per matched preference pair.
3. Fit conditional logit model: P(chosen=1) ~ β₁·ΔAIFS + β₂·Δlength + β₃·Δperplexity + β₄·(ΔAIFS×split) + cluster_FE on the full matched dataset.
4. Test H₀: β₄ = 0; extract OR, 95% CI, p-value; verify effect persists after controlling for marginal AIFS supply distribution.
5. Report β₄, OR, CI, p-value, and McFadden R² for the full model.

### Success Criteria
- Primary: β₄ > 0, OR ≥ 1.10, 95% CI excludes 1.0, p < 0.01
- Secondary: Effect persists after marginal AIFS supply control

### Variables
- **Independent Variable:** Annotator condition (helpful-base vs. helpful-online split)
- **Dependent Variable:** β₄ logit interaction coefficient (ΔAIFS × split)
- **Controlled Variables:** Marginal AIFS supply, prompt semantic complexity, semantic cluster FE, response length, perplexity

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** HH-RLHF (helpful-base + helpful-online splits)
- **Type:** standard
- **Source:** HuggingFace: anthropic/hh-rlhf
- **Path:** https://github.com/anthropics/hh-rlhf
- **Hypothesis Fit:** Provides documented multi-condition collection (deployed vs. naive annotators) in a single preference corpus; 160K+ pairs; separate splits enable the core β₄ interaction test

### Selected Model
- **Name:** Conditional logistic regression + sentence-transformers (all-MiniLM-L6-v2 frozen)
- **Type:** statistical
- **Source:** scikit-learn (logistic regression); sentence-transformers (all-MiniLM-L6-v2 frozen)
- **Hypothesis Fit:** Logistic regression operationalizes the β₄ interaction test; frozen sentence-transformers provide stable semantic clustering without model-dependent drift

---

## Baseline & Comparison Targets

### Baseline Methods
| Method | Performance | Dataset |
|--------|-------------|---------|
| HH-RLHF preference modeling (AI-to-human direction only) | Standard RLHF reward modeling; no measurement of human adaptation direction | HH-RLHF (160K+ pairs) |
| Vishwarupe et al. (2026) benchmark audit | 16/16 benchmarks lack user-facing verification — qualitative finding | 16 alignment benchmarks |
| STEER-BENCH / HumanAgencyBench (2025) | Best LLMs 15+ points below human experts; 6-dimensional agency measurement | 30 community pairs / new prompts |

### Baseline Performance
No existing methodology measures β₄ interaction coefficient. Null baseline: β₄ = 0 (OR = 1.0).

### Gap Analysis
Gap = demonstrating β₄ > 0 with OR ≥ 1.10. This is novel — no prior work has measured the human-to-AI adaptation direction in preference corpora.

---

## Dependencies and Gate Conditions

### Prerequisites
None (H-E1 is the foundation hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow

**Consequence if Fails:** PIVOT — reframe as population heterogeneity study (A1 violation check); investigate whether AIFS construct validity is the issue (triggers A2 validation priority). Stops H-M1 through H-M4.

**Phase Assignment:** Phase 2C → 3 → 4 (First)

**Estimated Duration:** Week 1-2

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the prerequisite for all other hypotheses (H-M1 through H-M4). It is the foundational existence test. If H-E1 fails, the entire pipeline is stopped or pivoted.

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

**Phase 2C will:**
1. Load this file instead of full Phase 2B roadmap (91% smaller)
2. Search for implementation patterns (Archon, Exa MCP)
3. Design concrete experiment specification (Level 1.5)
4. Output: h-e1/02c_experiment_brief.md

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
