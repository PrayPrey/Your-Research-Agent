# Hypothesis Context: h-e1

**Generated from:** Phase 2B Verification Plan
**Date:** 2026-08-25
**Main Hypothesis:** H-BenchmarkCoveragePrediction-v1
**Phase 2B Source:** 02b_verification_plan.md

---

## Hypothesis Information

### Statement
Under the scope of DL benchmarks published 2015-2024 with ≥50 citations, if we extract design features (task type, metrics, modality, dataset size) from benchmark papers and classify citation contexts using NLP, then we can distinguish validation claims from baseline mentions with >85% precision, because benchmark construction choices create explicit constraints on what hypotheses can be validated.

### Type
EXISTENCE

### Rationale
This existence hypothesis validates that benchmark design features are extractable and that citation context reveals validation usage. Without >85% NLP precision, we cannot reliably identify which benchmarks are used for hypothesis validation versus simple baselines.

---

## Verification Protocol

### Conceptual Test
1. Manually annotate 100-200 random citations from benchmark papers (validation claim vs other mention).
2. Train SciBERT classifier on citation contexts using annotated data (80/20 train/test split).
3. Measure precision/recall on held-out test set for validation claim classification.
4. Extract design features from 20 diverse benchmarks using standardized protocol (PWC taxonomy + regex).
5. Calculate inter-rater agreement (Cohen's kappa) between two annotators on feature extraction.

### Success Criteria
- Primary: Citation classifier precision >85% on test set
- Secondary: Feature extraction kappa >0.80 between annotators

### Variables (if applicable)
- **Independent Variable:** benchmark_design_features (task type, metrics, modality, dataset characteristics)
- **Dependent Variable:** citation_classification_precision (NLP classifier accuracy, target >0.85)
- **Controlled Variables:** citation_database (Semantic Scholar API), benchmark_selection (≥50 citations)

---

## Experimental Setup (from Phase 2A via Phase 2B)

> **Note:** Dataset and model were selected in Phase 2A Dialogue based on hypothesis Variables.
> Phase 2C experiment design MUST use this selection.

### Selected Dataset
- **Name:** Benchmark Paper Corpus + Citation Data (custom)
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
| Method | Performance | Dataset | Why Insufficient |
|--------|-------------|---------|------------------|
| Random baseline | ~50% accuracy (random chance for binary suitability) | Any benchmark corpus | Provides no guidance on which benchmarks match hypothesis requirements. Pure chance is not useful for researchers. |
| Citation count ranking | Measures popularity, not suitability | Benchmark citation databases | Popularity ≠ coverage. ImageNet is highly cited but unsuitable for sequence generation hypotheses. |
| Manual benchmark review | High accuracy but requires weeks of expert time per hypothesis | N/A - human effort | Not scalable. Researchers spend weeks reviewing benchmarks manually. Our approach reduces this to minutes. |

### Baseline Performance
Best Baseline: Manual expert review (weeks of effort, high accuracy but not scalable)

### Gap Analysis
Manual review is accurate but unscalable. Automated approaches (citation count) fail to capture hypothesis-benchmark fit. Our approach targets >85% precision with automated NLP, bridging the scalability-accuracy gap.

---

## Dependencies and Gate Conditions

### Prerequisites
None (foundation hypothesis)

### Gate Information

**Gate Type:** MUST_WORK
- MUST_WORK: Failure stops entire workflow
- SHOULD_WORK: Failure documented as limitation, workflow continues
- DETERMINES_SUCCESS: Final validation gate

**Consequence if Fails:** If precision <80%: PIVOT - refine NLP classifier (try different models, more training data). If kappa <0.70: EXPLORE - improve feature extraction protocol clarity

**Phase Assignment:** Phase 1

**Estimated Duration:** 2 weeks

---

## Dependency Context

### Relationship to Other Hypotheses
Foundation hypothesis that runs parallel with H-M1. Both H-E1 AND H-M1 must pass Gate 1 before H-M2 can begin. H-E1 provides citation classifier for H-M3 prediction test.

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
5. Output: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet45/TEST_scope/docs/youra_research/h-e1/02c_experiment_brief.md

**Baseline Usage by Hypothesis Type:**
- **H-E* (Existence)**: Baseline context for expected effect sizes
- **H-M* (Mechanism)**: Baseline to understand improvement potential
- **H-C* (Condition)**: Baseline to identify scope boundaries
- **H-CP* (Comparison)**: **MANDATORY** - Direct comparison with baseline methods

---

*Optimized for single-hypothesis experiment design*
