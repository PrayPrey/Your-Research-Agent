# Hypothesis Context: H-M1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-25
**Main Hypothesis:** Benchmark Coverage Prediction from Design Features
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
If we apply a standardized feature extraction protocol (Papers with Code taxonomy for task types, regex patterns for metrics, category tags for modality, table parsing for dataset size) to diverse benchmarks, then independent annotators will achieve >0.80 inter-rater agreement (Cohen's kappa), because the protocol provides objective decision rules for feature categorization.

### Type
MECHANISM

### Rationale
This mechanism hypothesis validates that feature extraction can be scaled reliably. Without high inter-rater agreement, the feature space is too subjective to support reproducible clustering and prediction.

---

## Verification Protocol

### Conceptual Test
1. Define standardized extraction protocol document (PWC taxonomy mapping + regex patterns for metrics).
2. Select 20 diverse benchmarks spanning task types, modalities, and dataset sizes.
3. Two annotators independently extract features following the protocol.
4. Calculate Cohen's kappa for categorical features (task, metrics, modality) and ICC for continuous (dataset size).
5. Refine protocol if kappa <0.80, then re-test on 10 new benchmarks.

### Success Criteria
- **Primary:** Cohen's kappa >0.80 for task type, metric types, modality
- **Secondary:** ICC >0.80 for dataset size

### Variables
- **Independent Variable:** feature_extraction_protocol (standardized rules using PWC taxonomy + regex)
- **Dependent Variable:** inter_rater_agreement (Cohen's kappa, target >0.80)
- **Controlled Variables:** annotator_expertise (both familiar with DL benchmarks), benchmark_diversity (20 benchmarks across vision/language/audio)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Benchmark Paper Corpus + Citation Data
- **Type:** custom
- **Source:** ArXiv API + Semantic Scholar API + Papers with Code API
- **Path:** To be collected
- **Hypothesis Fit:** Provides published design features (from papers) and usage patterns (from citations) needed to test coverage prediction hypothesis. No new data collection - all sources publicly accessible.

### Selected Model
- **Name:** Feature Extraction Pipeline (NLP + Clustering)
- **Type:** NLP + Clustering
- **Source:** SciBERT (citation classification) + SentenceBERT (feature embeddings) + k-means (clustering)
- **Hypothesis Fit:** SciBERT trained on scientific text handles citation context classification. SentenceBERT captures semantic similarity of task descriptions. K-means discovers coverage families without labeled data.

---

## Baseline & Comparison Targets

> **Note:** This section is PRIMARY for Comparison hypotheses (H-CP*).
> For other hypothesis types, baseline context helps understand expected improvements.

### Baseline Methods
Manual benchmark review - High accuracy but requires weeks of expert time per hypothesis.

### Baseline Performance
High accuracy but not scalable. Researchers spend weeks reviewing benchmarks manually.

### Gap Analysis
Without automated feature extraction achieving >0.80 inter-rater agreement, the approach cannot scale to 100 benchmarks. Manual review is not a viable baseline for automation.

---

## Dependencies and Gate Conditions

### Prerequisites
None (parallel with H-E1)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** 
- IF kappa <0.70: PIVOT - add decision tree flowcharts to protocol, re-test
- IF specific features low: EXPLORE - which features are ambiguous, refine definitions

**Phase Assignment:** Phase 1 (Week 1-2)

**Estimated Duration:** 2 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
H-M1 validates feature extraction objectivity. This is a prerequisite for H-M2 (clustering) and H-M3 (prediction). Runs in parallel with H-E1 (citation classifier). Both H-E1 and H-M1 must pass Gate 1 before proceeding to H-M2.

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
5. Output: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_scope/docs/youra_research/h-m1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
