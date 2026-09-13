# Hypothesis Context: H-M-integrated

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-03-18
**Main Hypothesis:** Lifecycle-Stage Functional Separability in Cross-Repository Metadata
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Semantic embeddings encode lifecycle role via distributional signatures (lexical co-occurrence, normative modality, value-structural patterns), enabling unsupervised clustering to recover 2-tier lifecycle structure that exceeds baselines (permutation, LDA, lexical) by ≥0.15 NMI after controlling for stylistic artifacts through length/modality normalization and repository stratification.

### Type
MECHANISM

### Rationale
H-M-integrated tests the full causal mechanism through three validation tiers: (1) baseline comparisons establish semantic value, (2) stylistic controls distinguish signal from artifact, (3) repository stratification tests generalization. This addresses the key tension from Phase 2A: signal amplification vs interface-induced separability.

---

## Verification Protocol

### Conceptual Test
1. Compute NMI for 3 baselines (permutation, LDA 2-topic, lexical keyword matching) on unscaffolded sample to establish comparison points
2. Run unsupervised K-means clustering (k=2) on semantic embeddings (all-MiniLM-L6-v2), measure NMI against 2-tier labels
3. Apply length normalization and modality filtering (deontic language removal), recompute NMI to test signal persistence
4. Train repository-specific linear probes (HF/OpenML/UCI separate), measure accuracy variance to test generalization
5. Compare scaffolded vs unscaffolded NMI gap to quantify interface amplification effect

### Success Criteria
- **Primary:** NMI(unsupervised) > 0.6 AND improvement over max(baselines) ≥ 0.15
- **Secondary:** Normalized NMI ≥ 0.6 (signal persists after controls), Probe variance < 0.1 (generalization)

### Variables
- **Independent Variable:** Embedding Method (4 levels), Repository Scaffolding (scaffolded/unscaffolded), Repository Type
- **Dependent Variable:** NMI (Normalized Mutual Information), NMI Baseline Gap
- **Controlled Variables:** Text Length (normalized), Modality Density (filtered), Sample Size

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Cross-Repository Metadata Sample (custom)
- **Type:** custom
- **Source:** HuggingFace Hub API, OpenML API, UCI repository web scraping
- **Path:** N=300 stratified sample (150 HF [75 scaffolded Open Datasheets, 75 unscaffolded], 100 OpenML, 50 UCI)
- **Hypothesis Fit:** Heterogeneous metadata schemas across repositories test lifecycle separability under real-world schema variability

### Selected Model
- **Name:** Sentence Transformers (all-MiniLM-L6-v2)
- **Type:** Semantic embedding model
- **Source:** Hugging Face Transformers library
- **Hypothesis Fit:** Frozen embeddings enable linear separability probe and unsupervised clustering without fine-tuning artifacts

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
1. **Permutation baseline:** Random label assignment (expected NMI ≈ 0.0)
2. **Topic modeling (LDA):** 2-topic LDA on field text (estimated NMI ~0.40-0.50)
3. **Lexical keyword matching:** Keyword-based clustering (estimated NMI ~0.45)

### Baseline Performance
Best baseline: Lexical heuristic NMI ~0.45

### Gap Analysis
Target improvement: ≥0.15 NMI over best baseline (0.45) → Target NMI ≥ 0.60

---

## Dependencies and Gate Conditions

### Prerequisites
- **h-e1** (COMPLETED, PASS): Cross-repository lifecycle separability validated (κ ≥ 0.60, probe ≥ 0.75)

### Gate Information

**Gate Type:** SHOULD_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:**
- IF NMI < 0.6 OR baseline gap < 0.15: EXPLORE - embeddings insufficient, test alternative representations
- IF normalized NMI collapses: PIVOT - amplification is stylistic not semantic
- IF probe variance > 0.15: SCOPE - lifecycle is repository-specific

**Phase Assignment:** Phase 2C → 3 → 4

**Estimated Duration:** Week 4-5 (from 6-week timeline)

---

## Dependency Context

### Relationship to Other Hypotheses
H-M-integrated builds on H-E1 foundation (lifecycle constructs validated, linear signal detected) to test full mechanism chain. Success enables H-C1 boundary testing. This is the core mechanistic hypothesis that validates the distributional signature theory.

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
5. Output: h-m-integrated/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Generated by Phase 2C Workflow (JIT)*
*Optimized for single-hypothesis experiment design*
