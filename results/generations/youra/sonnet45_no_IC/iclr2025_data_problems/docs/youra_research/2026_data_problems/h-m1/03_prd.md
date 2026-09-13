# Product Requirements Document: h-m1

**Date:** 2026-07-12
**Author:** Anonymous
**Hypothesis:** h-m1 (MECHANISM - Step 1/4)
**Phase:** Phase 3 - Implementation Planning

---

## Executive Summary

This PRD specifies requirements for implementing h-m1, a mechanism hypothesis investigating how stratified training (oversampling low-educational, high-BEIR examples) enables a retrieval-quality classifier to learn document features (factual density, entity coverage) independent of educational quality signals.

**Success Criterion:** Classifier-selected documents show ≥15% higher named entity density compared to perplexity-matched controls (entity_density_retrieval / entity_density_perplexity ≥ 1.15).

**Scope:** Proof-of-Concept (PoC) validation focused on mechanism verification, not paper reproduction.

---

## Problem Statement

### Research Context

H-E1 (EXISTENCE, prerequisite) demonstrated that retrieval-quality filtering achieves +5% Recall@10 improvement over perplexity-based filtering on BEIR Natural Questions (baseline: 0.47 → proposed: 0.52). However, the mechanism by which the classifier learns to distinguish retrieval-quality documents from educational-quality documents remains unverified.

### Hypothesis Statement

Under stratified training (oversampling low-educational, high-BEIR examples), the retrieval-quality classifier learns to identify documents with high factual density and entity coverage, as evidenced by classifier-selected documents showing ≥15% higher named entity density than perplexity-matched controls.

### Why This Matters

If the classifier learns factual density as a retrieval-quality signal (independent of fluency/coherence), this validates that:
1. Retrieval-optimal and pretraining-optimal corpora diverge measurably
2. The divergence is driven by factual density, not narrative fluency
3. Stratified training can decouple these quality dimensions

---

## Functional Requirements

### FR-1: Common Crawl Document Sampling

**Priority:** HIGH
**Description:** Sample 100K documents from Common Crawl for experiment corpus.
**Acceptance Criteria:**
- Minimum 100K documents sampled from Common Crawl dumps
- Documents stored in plain text format
- Average document length: 200-1000 tokens
- Deduplication applied (URL-based)

**Implementation Notes:**
- Reuse H-E1 Common Crawl sample if available
- Alternative: Use pre-filtered subset from public datasets

### FR-2: BEIR Training Data Generation

**Priority:** HIGH
**Description:** Generate stratified training examples from BEIR Natural Questions benchmark.
**Acceptance Criteria:**
- ~10K training pairs (positive/negative examples)
- Positive class: Documents from successful BEIR retrievals (high Recall@10)
- Negative class: Documents from failed retrievals OR low-quality documents
- Each example labeled with educational quality score (perplexity via GPT-2)
- Each example labeled with BEIR quality score (retrieval success)

**Implementation Notes:**
- Use BEIR Natural Questions corpus as source
- Perplexity computed via GPT-2 base model
- BEIR quality derived from retrieval evaluation results

### FR-3: Stratified Sampling Strategy

**Priority:** HIGH
**Description:** Implement stratification logic to oversample divergent examples (low-educational, high-BEIR).
**Acceptance Criteria:**
- Identify divergent examples: educational_score > median AND beir_score > median
- Oversample divergent examples 3× in training set
- Verify oversampling ratio in final training data statistics
- Document stratification parameters (thresholds, multipliers)

**Implementation Notes:**
- Educational quality: Perplexity (high perplexity = low educational quality)
- BEIR quality: Retrieval success score
- 3× oversampling factor based on hypothesis design

### FR-4: FastText Classifier Training

**Priority:** HIGH
**Description:** Train FastText text classifier on stratified BEIR examples.
**Acceptance Criteria:**
- Model architecture: FastText (shallow neural network)
- Embedding dimension: 100
- N-grams: 2 (bigrams)
- Training epochs: 25
- Learning rate: 0.1 (AdaGrad optimizer)
- Training completes in <5 minutes on CPU
- Model saved to disk for evaluation

**Implementation Notes:**
- Use fastText library (Facebook Research) or PyTorch equivalent
- Input format: FastText supervised format (`__label__<class> <text>`)
- Output: Binary classifier (retrieval-quality: positive/negative)

### FR-5: Perplexity Baseline Filter

**Priority:** HIGH
**Description:** Implement perplexity-based document filtering as baseline.
**Acceptance Criteria:**
- GPT-2 base model for perplexity computation
- Perplexity computed for all 100K Common Crawl documents
- Top-50K documents selected by ascending perplexity (lowest = highest educational quality)
- Perplexity scores cached to avoid recomputation

**Implementation Notes:**
- Use HuggingFace Transformers GPT-2 implementation
- Perplexity = exp(average negative log-likelihood per token)
- Control set for comparison with classifier-selected documents

### FR-6: Classifier-Based Document Selection

**Priority:** HIGH
**Description:** Apply trained classifier to Common Crawl sample and select top-50K documents.
**Acceptance Criteria:**
- Classifier applied to all 100K Common Crawl documents
- Top-50K documents selected by classifier score
- Selection matches corpus size of perplexity baseline (50K)
- Classifier scores cached for analysis

**Implementation Notes:**
- Score = classifier confidence for positive class (retrieval-quality)
- Same corpus size as baseline ensures fair comparison

### FR-7: Named Entity Density Measurement

**Priority:** HIGH
**Description:** Compute named entity density for both classifier-selected and perplexity-selected document sets.
**Acceptance Criteria:**
- spaCy NER pipeline (`en_core_web_sm` model) applied to all documents
- Entity density = (num_entities / num_tokens) × 100
- Metrics computed for both sets: density_retrieval, density_perplexity
- Ratio computed: density_retrieval / density_perplexity
- Threshold check: ratio ≥ 1.15 (15% improvement)

**Implementation Notes:**
- Entity types: PERSON, ORG, GPE, DATE, MONEY, etc.
- Per-document densities computed, then averaged per set
- Secondary metrics: type-token ratio, entity type distribution

### FR-8: Visualization Generation

**Priority:** MEDIUM
**Description:** Generate visualizations for entity density comparison and distribution analysis.
**Acceptance Criteria:**
- **Mandatory Figure:** Bar chart comparing entity density (retrieval vs perplexity)
  - X-axis: Method (Perplexity Baseline, Retrieval Classifier)
  - Y-axis: Named Entity Density (entities per 100 tokens)
  - Threshold line at 1.15× baseline
- **Optional Figures:** Entity type distribution, document length distribution, type-token ratio comparison
- All figures saved to `{hypothesis_folder}/figures/` directory

**Implementation Notes:**
- Use matplotlib or seaborn for plotting
- Save as PNG with 300 DPI for paper inclusion

### FR-9: Experiment Orchestration Script

**Priority:** HIGH
**Description:** Provide end-to-end script to run complete experiment pipeline.
**Acceptance Criteria:**
- Single entry point: `run_experiment.py` or equivalent
- Executes all steps: sampling → stratification → training → evaluation → visualization
- Progress logging to console and log file
- Results summary printed at completion
- Exit code 0 on success, non-zero on failure

**Implementation Notes:**
- CLI arguments for configuration (corpus_size, stratification_factor, etc.)
- Checkpoint support (resume from intermediate steps)

---

## Non-Functional Requirements

### NFR-1: Computational Efficiency

**Description:** Experiment must complete within reasonable time on standard hardware.
**Acceptance Criteria:**
- FastText training: <5 minutes on CPU
- Perplexity computation: <30 minutes on GPU (or <2 hours on CPU)
- NER processing: <1 hour on CPU
- Total experiment runtime: <3 hours

### NFR-2: Reproducibility

**Description:** Experiment results must be reproducible across runs.
**Acceptance Criteria:**
- Random seed fixed (seed=42)
- All dependencies documented with versions
- Dataset sampling deterministic (seed-based)
- Model training deterministic (seed-based)

### NFR-3: Code Quality

**Description:** Code must be maintainable and understandable.
**Acceptance Criteria:**
- Type hints for function signatures
- Docstrings for public functions
- Logging instead of print statements
- Error handling for file I/O and model loading

---

## Data Specifications

### Input Data

| Dataset | Source | Size | Format | Purpose |
|---------|--------|------|--------|---------|
| BEIR Natural Questions | HuggingFace `beir/nq` | ~3.5K queries, ~2.7M docs | JSON | Training data source |
| Common Crawl Sample | Common Crawl dumps | 100K docs | Plain text | Evaluation corpus |

### Output Data

| Artifact | Path | Format | Purpose |
|----------|------|--------|---------|
| Stratified training data | `train_stratified.txt` | FastText format | Classifier training |
| Trained classifier | `classifier.bin` | FastText model | Document selection |
| Selected documents | `selected_retrieval.txt` | Plain text list | Evaluation set |
| Baseline documents | `selected_perplexity.txt` | Plain text list | Control set |
| Results | `results.json` | JSON | Metrics storage |
| Figures | `figures/*.png` | PNG | Visualization |

---

## Dependencies

### Software Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| `fasttext` | ≥0.9.2 | Text classification |
| `spacy` | ≥3.7 | Named entity recognition |
| `en_core_web_sm` | ≥3.7 | spaCy English NER model |
| `transformers` | ≥4.30 | GPT-2 perplexity computation |
| `datasets` | ≥2.0 | BEIR dataset loading |
| `torch` | ≥2.0 | GPU acceleration (optional) |
| `numpy` | ≥1.24 | Numerical operations |
| `matplotlib` | ≥3.7 | Visualization |

### Hardware Requirements

- **Minimum:** 16GB RAM, 4 CPU cores
- **Recommended:** 32GB RAM, 8 CPU cores, 1 GPU (for perplexity computation)

### Prerequisite Hypotheses

- **H-E1 (EXISTENCE):** COMPLETED, PASSED
  - Provides validation of retrieval-quality filtering approach
  - May provide reusable Common Crawl sample

---

## Success Criteria

### Primary Success Criterion (PoC Gate)

**Metric:** Entity density ratio ≥ 1.15
**Formula:** `density_retrieval / density_perplexity ≥ 1.15`
**Direction:** Higher is better (retrieval > perplexity)

**Pass Condition:**
- Code runs without error
- Ratio ≥ 1.0 (positive direction)
- **Bonus:** Ratio ≥ 1.15 (hypothesis validated)

### Secondary Metrics (Informational)

| Metric | Purpose | Target |
|--------|---------|--------|
| Type-token ratio | Vocabulary richness | Higher for retrieval-selected |
| Entity type distribution | Which entity types dominate | Report distribution |
| Document length | Control for length bias | Similar distributions |

### Statistical Validation (Optional)

- Paired t-test on per-document entity densities
- Report p-value if available
- **NOT REQUIRED** for PoC pass

---

## Risk Assessment

### Risk 1: Stratification Overfitting

**Probability:** MEDIUM
**Impact:** HIGH
**Mitigation:** Validate on held-out Common Crawl set (not seen during training)

### Risk 2: Entity Density Correlation with Length

**Probability:** MEDIUM
**Impact:** MEDIUM
**Mitigation:** Report document length distributions; normalize by token count

### Risk 3: Common Crawl Sample Bias

**Probability:** LOW
**Impact:** MEDIUM
**Mitigation:** Random sampling with seed; document domain diversity check

### Risk 4: Perplexity Baseline Instability

**Probability:** LOW
**Impact:** LOW
**Mitigation:** Use GPT-2 base model (stable, well-tested)

---

## Out of Scope

- Multi-class entity classification (binary positive/negative only)
- Cross-dataset generalization (focus on BEIR Natural Questions)
- Production deployment (PoC validation only)
- Hyperparameter tuning beyond defaults (fixed parameters from hypothesis)

---

## Appendix: Phase 2C Alignment

This PRD is derived from Phase 2C experiment brief (`02c_experiment_brief.md`) and includes:

✅ **Baseline Model:** Perplexity-based filtering (GPT-2) - FR-5
✅ **Proposed Model:** Stratified retrieval-quality classifier (FastText) - FR-4
✅ **Dataset:** BEIR Natural Questions + Common Crawl 100K - FR-1, FR-2
✅ **Primary Metric:** Named entity density ratio - FR-7
✅ **Secondary Metrics:** Type-token ratio, entity type distribution - FR-7
✅ **Visualization:** Entity density comparison bar chart - FR-8
✅ **Success Criterion:** Ratio ≥ 1.15 - Success Criteria section

**No missing Phase 2C items identified.**

---

**Document Status:** DRAFT
**Last Updated:** 2026-07-12
**Next Steps:** Proceed to Step 3 - Architecture Agent for module design and Epic task breakdown.
