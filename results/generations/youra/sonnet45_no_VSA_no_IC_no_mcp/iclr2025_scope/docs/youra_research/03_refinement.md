# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-08-25T12:30:00Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Contained Tikitaka Loop
- **Gap ID**: gap_1_systematic_benchmark_coverage
- **Gap Title**: Systematic Benchmark Coverage Analysis
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 7

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 7

**Convergence Reason**: All convergence criteria met at Exchange 7 - core claim stated, mechanism explained, predictions specified with success criteria, novelty articulated, feasibility established, all objections addressed with concrete mitigations

### Key Insights
- Historical validation (2022 features → 2023-2024 predictions) breaks circular reasoning trap identified by Prof. Rex
- Citation context filtering essential to separate validation claims from baseline mentions (Prof. Rex challenge addressed)
- Ground truth objectivity achieved via standardized taxonomies (Papers with Code) and regex patterns (Prof. Pax feasibility check)
- Contribution is predictive tool enabling hypothesis feasibility pre-checks, not just descriptive taxonomy (Dr. Sage significance requirement)

### Breakthrough Moments
- **Exchange 4**: Prof. Pax mechanism analysis clarified how design features create measurable constraints on hypothesis validation
- **Exchange 6**: Prof. Rex circular reasoning objection led to historical validation innovation (train/test split by publication year)
- **Exchange 7**: Dr. Nova historical split proposal unified all concerns into testable framework meeting all feasibility constraints

---

## Final Hypothesis

### Title
Benchmark Coverage Prediction from Design Features

### Core Claim
Under the scope of widely-used DL benchmarks (published 2015-2024), if we extract design features from benchmark papers (task formulation, evaluation metrics, data modality, dataset characteristics) and cluster them into coverage families using unsupervised learning, then coverage families from pre-2023 benchmarks will predict 2023-2024 benchmark adoption patterns for novel hypothesis validation with >70% accuracy, because benchmark construction choices create systematic constraints on hypothesis testability that persist over time.

### Mechanism
Benchmark construction choices create systematic constraints on hypothesis testability through four causal steps:

1. **Design Features → Measurement Constraints**: Task formulation defines measurable hypothesis space (classification ≠ generation ≠ retrieval), metrics define success criteria (accuracy vs BLEU vs recall@k), modality defines applicable domains (vision vs language vs multimodal)

2. **Constraints → Coverage Families**: Design features cluster through unsupervised learning on semantic embeddings, grouping benchmarks with similar validation capabilities

3. **Families → Hypothesis Suitability**: Coverage families predict which hypothesis types can be validated by matching hypothesis requirements to family constraints

4. **Historical Persistence**: Design constraints persist over time, enabling pre-2023 features to predict 2023-2024 adoption patterns (pure prediction, not circular description)

---

## Predictions

**P1 (Primary)**: Coverage families from pre-2023 benchmarks will predict 2023-2024 benchmark adoption patterns for hypothesis validation with >70% accuracy
- **Test Method**: Historical train/test split - extract features from 2015-2022 benchmarks, cluster into families, measure whether families predict which benchmarks are cited for hypothesis validation in 2023-2024 papers
- **Success Criterion**: Prediction accuracy >70% (significantly above 50% random baseline, p<0.05)
- **Falsification**: If accuracy ≤60%, coverage families do not meaningfully predict benchmark suitability

**P2**: Citation context NLP classifier will achieve >85% precision in distinguishing 'validation claims' from other citation types
- **Test Method**: Manual annotation of 100-200 random citations, train SciBERT classifier, measure precision on held-out test set
- **Success Criterion**: Precision >85% on test set
- **Falsification**: If precision <80%, citation evidence too noisy for reliable hypothesis type extraction

**P3**: Feature extraction protocol will achieve >0.80 inter-rater agreement (Cohen's kappa) across diverse benchmarks
- **Test Method**: Two independent annotators extract features from 20 benchmarks using standardized protocol, calculate Cohen's kappa
- **Success Criterion**: Kappa >0.80 for categorical features (task type, modality), ICC >0.80 for continuous features (dataset size)
- **Falsification**: If kappa <0.70, feature extraction too subjective to scale reliably

---

## Novelty

**Key Innovation**: First systematic attempt to predict future benchmark suitability from design features using historical train/test validation. Shifts benchmark coverage analysis from descriptive taxonomy to predictive tool.

**What Makes This New**:
- **vs Benchmark Taxonomies** (e.g., Papers with Code): Those organize benchmarks descriptively. We PREDICT future suitability from design features, enabling hypothesis feasibility pre-checks.
- **vs Citation Count Studies**: Those measure popularity. We extract WHY benchmarks are suitable (design constraints) and predict novel hypothesis validation.
- **vs Recommendation Systems**: Those rely on user behavior similarity. We use inherent design features, enabling prediction for novel hypothesis types without prior usage data.

**Impact**: Enables researchers to pre-check hypothesis testability in minutes (vs weeks of manual benchmark review), discovers coverage gaps revealing where new benchmarks are needed, unlocks novel research directions previously blocked by "no suitable benchmark" problem.

---

## Experimental Design

**Dataset**: Benchmark Paper Corpus (ArXiv 2015-2024) + Semantic Scholar citation data + Papers with Code taxonomy
- No new data collection - all sources publicly accessible
- Provides published design features (from papers) and usage patterns (from citations)

**Models**:
- SciBERT: Citation context classification (validation claims vs baseline mentions)
- SentenceBERT: Feature embeddings for semantic clustering
- k-means: Unsupervised discovery of coverage families

**Baselines**:
- Random baseline (50% accuracy expected)
- Name-based matching (keyword overlap between benchmark name and hypothesis)
- Citation count ranking (popularity only, ignoring design features)
- Gold standard: Manual expert review (high accuracy but weeks of effort, not scalable)

**Validation Protocol**:
1. Extract features from 2015-2022 papers using objective protocol (task type from PWC taxonomy, metrics via regex, modality from categories, size from tables)
2. Cluster features into coverage families using k-means on SentenceBERT embeddings
3. Classify 2023-2024 citation contexts using SciBERT (validation claims vs other mentions)
4. Measure prediction accuracy: do 2022 families predict 2023-2024 validation citations?
5. Validate classifier precision (100-200 manual annotations) and feature extraction agreement (20 benchmarks, 2 annotators, Cohen's kappa)

---

## Limitations

**Scope Boundaries**:
- Applies to widely-used benchmarks (≥50 citations) with published papers
- Covers 2015-2024 DL era (modern benchmarks only)
- Limited to domains with Papers with Code taxonomy coverage
- Does not apply to informal datasets (GitHub-only, no paper), newly-created benchmarks (<50 citations), or private/proprietary benchmarks

**Temporal Limitations**:
- Historical validation limited to 2-3 year window (2022→2023-2024)
- Coverage families may not generalize to future paradigm shifts (e.g., if transformers → entirely new architecture class)
- Multiple historical splits (2020/2021-2022, 2021/2022-2023) verify temporal stability but cannot guarantee indefinite persistence

**Data Dependencies**:
- Citation analysis depends on Semantic Scholar API coverage (not all papers indexed)
- Feature extraction requires manual ground truth validation (20 benchmarks) before scaling
- Terminology normalization relies on SentenceBERT semantic similarity (embedding quality affects clustering)

---

## Decision

| Item | Status |
|------|--------|
| **Overall Status** | VALIDATED |
| **Discussion Convergence** | All convergence criteria met at Exchange 7 |
| **Clarity Verified** | Yes |
| **Remaining Objections** | None (all addressed with concrete mitigations) |

**Remaining Risks** (Prof. Rex):
1. Citation precision <85% → contaminated validation evidence
2. Feature agreement <0.80 → subjective extraction breaks scalability
3. Prediction accuracy <60% → mechanism claim breaks (near random baseline)

**Mitigation Strategy**:
- Validate citation classifier on 100-200 manual annotations BEFORE full-scale analysis
- Pilot feature extraction on 20 benchmarks, refine codebook until kappa >0.80
- Use multiple historical splits to verify temporal stability
- **Fail fast**: If any threshold fails on validation set, revise protocol before scaling

---

**Phase 2A Complete - Ready for Phase 2B Planning**
