# Hypothesis Context: H-E1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-03-18
**Main Hypothesis:** Lifecycle-Stage Functional Separability in Cross-Repository Metadata
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Cross-repository metadata fields exhibit measurable lifecycle-stage separability: inter-annotator agreement κ ≥ 0.60 across repositories AND linear probe accuracy ≥ 0.75 on scaffolded data, validating that lifecycle constructs are operationally stable and signals are linearly detectable.

### Type
EXISTENCE

### Rationale
H-E1 validates the foundation for all subsequent hypotheses by establishing that (1) lifecycle constructs are reliable measurement tools with operational stability, and (2) semantic embeddings contain detectable lifecycle signals that are linearly encoded. These are necessary conditions for testing unsupervised clustering recovery.

---

## Verification Protocol

### Conceptual Test
1. Three expert annotators independently label N=300 metadata fields with 2-tier lifecycle taxonomy (General Info vs RAI), blind to repository source
2. Compute Cohen's κ for each repository and overall κ_across to measure construct reliability
3. Train logistic regression probe on scaffolded HF embeddings (75 samples) to test linear separability
4. Test probe accuracy on held-out scaffolded data to validate signal detectability
5. Compare κ_within_repo vs κ_across to identify repository context effects

### Success Criteria
- **Primary:** κ_across ≥ 0.60 AND linear probe accuracy ≥ 0.75
- **Secondary:** κ_within ≥ 0.70 for structured repos (HF, OpenML)

### Variables
- **Independent Variable:** Repository Type (HuggingFace, OpenML, UCI)
- **Dependent Variable:** Inter-annotator Agreement (κ), Linear Probe Accuracy
- **Controlled Variables:** Sample Size (N=300 stratified), Text Length, Annotation Protocol

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Cross-Repository Metadata Sample
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
| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Manual cross-repository field mapping | N/A (expert annotation) | Same metadata sample | Not scalable, lacks automation |
| Lexical keyword matching | NMI ~0.45 (estimated) | Same metadata sample | Ignores distributional context and semantic nuance |
| Topic modeling (LDA) | NMI ~0.40-0.50 (estimated) | Same metadata sample | Bag-of-words approach misses sequential and normative structure |

### Baseline Performance
Best Baseline: Lexical heuristic NMI ~0.45

### Gap Analysis
H-E1 is a foundation hypothesis validating existence of lifecycle separability. Baselines provide context for expected effect sizes in downstream hypotheses (H-M-integrated).

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundation hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:**
- IF κ < 0.60: PIVOT to repository-scoped claims (lifecycle is context-dependent)
- IF probe < 0.75: PIVOT to normative geometry hypothesis (nonlinear encoding)

**Phase Assignment:** Week 3 (early falsification gate)

**Estimated Duration:** 1 week (data collection + annotation + probe training)

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the foundation hypothesis. H-M-integrated and H-C1 both depend on H-E1 passing. If H-E1 fails, the entire pipeline is STOPPED or pivoted based on failure mode.

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
