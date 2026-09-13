# Product Requirements Document: h-e1 - Retrieval-Quality Corpus Filtering

**Date:** 2026-07-12  
**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (Foundation)  
**Author:** Anonymous  

---

## Executive Summary

### Purpose
Validate that retrieval-specific quality signals can be learned and applied to corpus curation for RAG systems, achieving measurably better retrieval performance than general language quality metrics.

### Core Value Proposition
Demonstrate that a classifier trained on stratified BEIR success examples can filter Common Crawl documents to create a 1M-document corpus achieving ≥3% higher Recall@10 on Natural Questions compared to perplexity-based filtering.

### Success Criteria
- **Primary Gate:** Recall@10 ≥ baseline + 0.03, p<0.05 (MUST_WORK)
- **PoC Threshold:** Any positive improvement (direction-based validation)
- **Baseline:** Perplexity-filtered corpus using GPT-2

---

## Problem Statement

### Background
Current corpus curation methods for RAG systems primarily use language modeling objectives (perplexity, educational quality) which may not align with retrieval-specific requirements. Documents optimal for pretraining (low perplexity, narrative fluency) may differ from documents optimal for retrieval (high factual density, entity coverage).

### The Challenge
1. No established methodology for training retrieval-specific quality classifiers
2. Common Crawl scale requires efficient filtering mechanisms
3. Need to validate divergence between retrieval-optimal and LM-optimal corpora

### Hypothesis Under Test
**h-e1:** Under RAG corpus construction from Common Crawl, if a retrieval-quality classifier (trained on stratified BEIR success examples) filters documents, then the resulting 1M-document corpus achieves ≥3% higher Recall@10 on Natural Questions compared to perplexity-based filtering (matched corpus size), because the classifier learns to identify documents with high factual density and entity coverage.

---

## Functional Requirements

### FR-1: Dataset Acquisition and Preprocessing
**Priority:** P0 (Critical Path)  
**Description:** Acquire and preprocess evaluation and corpus datasets for the experiment

**Acceptance Criteria:**
- BEIR Natural Questions test split downloaded (~3,500 queries with relevance judgments)
- Common Crawl sample extracted (100K documents from CC-MAIN-2024-10)
- Text extraction from HTML with language filtering (English only)
- Deduplication applied to Common Crawl sample
- Length filtering (50-500 tokens per document)
- DPR tokenization applied to all documents

**Dependencies:** None

**Implementation Notes:**
- Use BEIR package for Natural Questions: `beir.util.download_and_unzip()`
- Common Crawl: Custom sampling script using warcio or equivalent
- Preprocessing pipeline: HTML→text→dedup→lang filter→length filter→tokenize

---

### FR-2: Baseline Model Loading
**Priority:** P0 (Critical Path)  
**Description:** Load pre-trained DPR (Dense Passage Retriever) bi-encoders for retrieval evaluation

**Acceptance Criteria:**
- DPR question encoder loaded: `facebook/dpr-question_encoder-single-nq-base`
- DPR context encoder loaded: `facebook/dpr-ctx_encoder-single-nq-base`
- Corresponding tokenizers loaded for both encoders
- Embeddings verified to be 768-dimensional
- FAISS index configured for cosine similarity search

**Dependencies:** FR-1 (requires tokenized documents)

**Implementation Notes:**
- Use HuggingFace Transformers library
- Pre-trained on Natural Questions (no fine-tuning required)
- Frozen encoders (testing corpus quality, not model training)

---

### FR-3: Perplexity-Based Baseline Corpus
**Priority:** P0 (Critical Path)  
**Description:** Create baseline filtered corpus using GPT-2 perplexity scoring

**Acceptance Criteria:**
- GPT-2 model loaded for perplexity computation
- Perplexity scores computed for all 100K Common Crawl documents
- Top 1M documents selected by lowest perplexity
- Corpus indexed with DPR context encoder
- FAISS index created for retrieval

**Dependencies:** FR-1, FR-2

**Implementation Notes:**
- Use `transformers.GPT2LMHeadModel` for perplexity
- Select documents with lowest perplexity (high language quality)
- Target corpus size: 1M documents

---

### FR-4: Stratified Training Data Generation
**Priority:** P0 (Critical Path)  
**Description:** Generate stratified training data for retrieval-quality classifier from BEIR corpus

**Acceptance Criteria:**
- Positive class: Documents with high BEIR relevance scores extracted
- Negative class: Documents with low BEIR relevance scores extracted
- Stratification applied: 2:1 ratio oversampling low-educational, high-BEIR examples
- Training set size: ~10K positive, ~10K negative examples
- FastText input format generated (one document per line with __label__ prefix)

**Dependencies:** FR-1

**Implementation Notes:**
- Extract from BEIR Natural Questions corpus annotations
- Compute perplexity for each BEIR document
- Oversample: low-perplexity AND high-BEIR-relevance (forces retrieval-specific learning)
- Format: `__label__positive <document_text>` or `__label__negative <document_text>`

---

### FR-5: Retrieval-Quality Classifier Training
**Priority:** P0 (Critical Path)  
**Description:** Train FastText binary classifier to identify retrieval-optimal documents

**Acceptance Criteria:**
- FastText model trained on stratified BEIR examples
- Hyperparameters: `dim=100, lr=0.1, epoch=25, wordNgrams=2`
- Model achieves >0.7 validation accuracy on held-out BEIR examples
- Quality score prediction function implemented
- Threshold calibration performed to target 1M corpus size

**Dependencies:** FR-4

**Implementation Notes:**
- Use `fasttext.train_supervised()` with specified parameters
- Based on DataComp-LM classifier methodology
- Lightweight architecture suitable for corpus-scale filtering

---

### FR-6: Retrieval-Quality Filtered Corpus
**Priority:** P0 (Critical Path)  
**Description:** Apply trained classifier to filter Common Crawl into retrieval-optimal corpus

**Acceptance Criteria:**
- Classifier applied to all 100K Common Crawl documents
- Quality scores computed for each document
- Threshold determined to select 1M documents
- Filtered corpus indexed with DPR context encoder
- FAISS index created for retrieval

**Dependencies:** FR-1, FR-2, FR-5

**Implementation Notes:**
- Predict quality scores using `model.predict(doc)`
- Sort by score and select top 1M
- Index with same DPR encoder as baseline (fair comparison)

---

### FR-7: Recall@10 Evaluation
**Priority:** P0 (Critical Path)  
**Description:** Evaluate retrieval performance for both baseline and proposed corpora

**Acceptance Criteria:**
- Recall@10 computed for perplexity-filtered corpus
- Recall@10 computed for retrieval-quality filtered corpus
- Evaluation uses BEIR Natural Questions test queries (~3,500 queries)
- Results reported with absolute delta and relative improvement
- PoC pass condition checked: `proposed > baseline`
- Gate condition checked: `proposed ≥ baseline + 0.03` (for full validation)

**Dependencies:** FR-3, FR-6

**Implementation Notes:**
- Use BEIR `EvaluateRetrieval` class
- Metric: Fraction of queries where correct answer in top-10 retrieved documents
- Formula: `Recall@10 = (queries with answer in top-10) / (total queries)`

---

### FR-8: Visualization and Reporting
**Priority:** P1 (High)  
**Description:** Generate required visualizations and analysis for hypothesis validation

**Acceptance Criteria:**
- **Figure 1 (Mandatory):** Recall@10 comparison bar chart (Perplexity vs Retrieval-Quality)
  - Horizontal line showing gate threshold (baseline + 0.03)
- **Figure 2:** Quality score distribution histogram
  - Show FastText scores for Common Crawl sample
  - Mark threshold used for 1M selection
- **Figure 3:** Document statistics comparison table/heatmap
  - Entity density (entities per 100 tokens)
  - Type-token ratio
  - Average document length
  - Perplexity distribution
- **Figure 4:** Query-level performance scatter plot
  - X-axis: Perplexity-filtered Recall, Y-axis: Retrieval-filtered Recall
  - Diagonal line (y=x) for improvement direction
  - Highlight queries with largest gains/losses
- All figures saved to `docs/youra_research/h-e1/figures/`

**Dependencies:** FR-7

**Implementation Notes:**
- Use matplotlib or seaborn for visualizations
- Export as PNG and PDF (300 DPI for paper quality)
- Include figure generation logic in experiment code

---

## Non-Functional Requirements

### NFR-1: Performance and Efficiency
- FastText classifier training: <10 minutes on CPU
- Common Crawl filtering: <1 hour for 100K documents
- DPR encoding: Batch processing with GPU acceleration if available
- FAISS indexing: <5 minutes for 1M documents

### NFR-2: Reproducibility
- Fixed random seed: `random_state=42` for all stochastic operations
- Single seed sufficient for PoC (EXISTENCE hypothesis)
- All hyperparameters explicitly documented
- Dataset versions pinned (BEIR release, CC snapshot)

### NFR-3: Code Quality
- Modular pipeline: separate scripts for each FR
- Logging: INFO level for progress, DEBUG for detailed metrics
- Checkpointing: Save intermediate outputs (training data, filtered corpora)
- Error handling: Graceful failures with informative messages

### NFR-4: Storage Requirements
- Common Crawl sample: ~500MB compressed
- BEIR Natural Questions: ~100MB
- FAISS indices: ~2GB (2 corpora × 1M docs × 768-dim)
- Figures and logs: <50MB

---

## Data Specifications

### Input Data

**BEIR Natural Questions (Evaluation)**
- Source: BEIR benchmark (Thakur et al., 2021)
- Identifier: `beir/nq`
- Format: JSON (queries, corpus, qrels)
- Size: ~3,500 test queries, Wikipedia-derived corpus
- Preprocessing: DPR tokenization (WordPiece, max_length=512)

**Common Crawl Sample (Filtering Target)**
- Source: CC-MAIN-2024-10 snapshot
- Sampling: Random 100K documents
- Format: WARC → extracted text
- Preprocessing: HTML→text, dedup, English filter, length filter (50-500 tokens)

### Output Data

**03_prd.md** (This document)  
**03_architecture.md** (Next step)  
**03_logic.md** (Next step)  
**03_config.md** (Next step)  
**03_tasks.yaml** (Step 9)  

**Experimental Artifacts:**
- `filtered_corpora/perplexity_1M.jsonl`
- `filtered_corpora/retrieval_quality_1M.jsonl`
- `models/retrieval_quality_classifier.bin`
- `results/recall_at_10_comparison.json`
- `figures/*.png` (4 figures)

---

## Dependencies and Integration

### External Dependencies
1. **HuggingFace Transformers** (v4.30+)
   - DPR encoders and tokenizers
   - GPT-2 for perplexity

2. **BEIR** (v1.0+)
   - Dataset loading
   - Evaluation framework

3. **FastText** (v0.9.2+)
   - Classifier training

4. **FAISS** (v1.7+)
   - Dense retrieval indexing

5. **warcio** or equivalent
   - Common Crawl WARC parsing

### Internal Dependencies
- Phase 2C experiment brief: `docs/youra_research/h-e1/02c_experiment_brief.md`
- verification_state.yaml (hypothesis metadata)

---

## Success Criteria

### Primary Metrics
- **Recall@10 (Proposed):** Fraction of queries with answer in top-10 (retrieval-quality corpus)
- **Recall@10 (Baseline):** Fraction of queries with answer in top-10 (perplexity corpus)

### Gate Conditions
- **MUST_WORK Gate:** `Recall@10_proposed ≥ Recall@10_baseline + 0.03` AND `p < 0.05`
- **PoC Pass (h-e1):** `Recall@10_proposed > Recall@10_baseline` (direction-based, no statistical test required)

### Expected Performance
- Baseline (perplexity-filtered): 0.45-0.50 Recall@10 (estimated)
- Target (retrieval-quality): 0.48-0.53 Recall@10 (≥0.03 improvement)
- Reference (DPR on full Wikipedia): 0.79 Recall@10 (Karpukhin et al., 2020)

---

## Risk Assessment

### Technical Risks
1. **Risk:** Common Crawl sample quality too low for meaningful comparison
   - **Mitigation:** Pre-filter for minimum text quality before sampling
   - **Contingency:** Use curated web corpus (C4, OSCAR) if needed

2. **Risk:** FastText classifier overfits to BEIR corpus characteristics
   - **Mitigation:** Stratified sampling to force retrieval-specific signal learning
   - **Contingency:** Try alternative lightweight classifiers (Logistic Regression)

3. **Risk:** 1M corpus size insufficient for fair DPR evaluation
   - **Mitigation:** Scale to 5M if initial results inconclusive
   - **Contingency:** Use Wikipedia subset as corpus (known to work with DPR)

### Schedule Risks
1. **Risk:** Common Crawl download/processing exceeds time budget
   - **Mitigation:** Pre-sample smaller subset (50K) for pilot
   - **Contingency:** Use pre-extracted CC samples from research datasets

---

## Appendix: Traceability

All specifications are grounded in Phase 2C research findings:

| Specification | Source |
|---------------|--------|
| BEIR Natural Questions dataset | Phase 2C: Repository B.2 (beir-cellar/beir) |
| DPR pre-trained models | Phase 2C: Repository B.1 (facebook/DPR) |
| FastText classifier | Phase 2C: Repository B.3 (facebookresearch/fastText) |
| Stratified training methodology | Phase 2C: DataComp-LM classifier approach |
| Recall@10 metric | Phase 2C: BEIR evaluation framework |
| Success criteria (≥3% gain) | Phase 2B: 02b_verification_plan.md Section 2.2 |
| Gate condition (p<0.05) | Phase 2B: 02b_verification_plan.md Section 3.2 |

---

## Document Metadata

**Workflow:** Phase 3 - Implementation Planning  
**Step:** 2 of 10 (PRD Generation)  
**Next Steps:**
1. Architecture design (03_architecture.md) via architecture-agent
2. Logic specification (03_logic.md) via logic-agent
3. Configuration design (03_config.md) via configuration-agent
4. Task generation (03_tasks.yaml)

**Version:** 1.0  
**Status:** Complete  
**Generated:** 2026-07-12  
