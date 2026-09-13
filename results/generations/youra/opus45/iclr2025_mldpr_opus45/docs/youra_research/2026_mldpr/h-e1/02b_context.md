# Hypothesis Context: h-e1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-03-27
**Main Hypothesis:** Hierarchical Lifecycle Taxonomy of HuggingFace Dataset Adoption Patterns
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under the HuggingFace dataset ecosystem (datasets with >=12 months history), if we apply DTW-based TimeSeriesKMeans clustering to normalized download trajectories, then datasets will partition into 3-8 distinct clusters with silhouette score >0.25 and bootstrap Jaccard stability >0.65, because download dynamics reflect recurring adoption mechanisms.

### Type
EXISTENCE

### Rationale
This is the foundational existence test. If no meaningful clustering structure exists, the entire taxonomy approach fails. The silhouette and stability thresholds are derived from clustering literature standards for interpretable groupings.

---

## Verification Protocol

### Conceptual Test
1. Query HuggingFace API for datasets meeting inclusion criteria (target >=500 datasets).
2. Preprocess trajectories: validate monotonicity, log-transform, z-score normalize.
3. Apply TimeSeriesKMeans with DTW metric for k in [2,10].
4. Select optimal k via silhouette score maximization.
5. Bootstrap 100x, compute Jaccard similarity for stability.

### Success Criteria
- Primary: Optimal k in [3,8] with silhouette >0.25
- Secondary: Bootstrap Jaccard stability >0.65

### Variables (if applicable)
- **Independent Variable:** Dataset trajectory shape (DTW distance in normalized trajectory space)
- **Dependent Variable:** Cluster membership (k in [3,8]), Silhouette score (>0.25)
- **Controlled Variables:** Dataset age (>=12 months), Data quality (<10% missing), Normalization (log + z-score)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** HuggingFace Dataset Download Statistics
- **Type:** custom (API-based collection)
- **Source:** HuggingFace Hub API (huggingface_hub library)
- **Path:** API query - no static path
- **Hypothesis Fit:** Direct measurement of the adoption dynamics we aim to characterize

### Selected Model
- **Name:** TimeSeriesKMeans with DTW metric
- **Type:** Unsupervised clustering
- **Source:** tslearn library
- **Hypothesis Fit:** DTW handles variable-length series and temporal warping; validated in similar domains

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
| Method | Description |
|--------|-------------|
| Single-level DTW clustering | TimeSeriesKMeans without phase normalization |
| Random assignment | Random cluster labels as null baseline |
| K-means on summary statistics | Cluster on (mean, std, trend) rather than full trajectories |

### Baseline Performance
- General DTW clustering: Established methodology, silhouette typically 0.2-0.4 for time series
- npm package trajectory analysis (Mujahid et al., 2021): Identified patterns but single-level

### Gap Analysis
- Novelty: First hierarchical lifecycle analysis of ML dataset ecosystems
- Key Innovation: Two-level structure separates age-confounded phase states from trajectory archetypes

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundation hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** STOP - reassess entire hypothesis

**Phase Assignment:** Phase 1 - Foundation

**Estimated Duration:** 2 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
H-E1 is the foundation for all subsequent hypotheses:
- H-M1 (PELT Phase Detection) depends on H-E1
- H-M2 (Shape Differentiation) depends on H-M1
- H-M3 (Archetype Recovery) depends on H-M2

If H-E1 fails, the entire verification chain stops.

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
