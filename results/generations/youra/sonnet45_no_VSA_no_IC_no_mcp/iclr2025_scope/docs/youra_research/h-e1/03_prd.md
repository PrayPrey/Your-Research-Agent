# Product Requirements Document: h-e1

**Date:** 2026-08-25
**Author:** Phase 3 Implementation Planning
**Hypothesis:** h-e1 (EXISTENCE)
**Source:** 02c_experiment_brief.md

---

## Executive Summary

Build proof-of-concept experiment validating that benchmark design features can be extracted from papers and that citation contexts distinguish validation claims from baseline mentions with >85% precision.

**Success Criteria:**
- Citation classification precision >85% on test set (Primary Gate)
- Feature extraction inter-rater agreement kappa >0.80 (Secondary Gate)
- Gate Type: MUST_WORK (failure stops workflow)

**Timeline:** 2 weeks (from Phase 2B)
**Budget:** Tier 1 implementation (foundation hypothesis, small dataset, standard library usage)

---

## Background

### Hypothesis Context

**Statement:** Under the scope of DL benchmarks published 2015-2024 with ≥50 citations, if we extract design features (task type, metrics, modality, dataset size) from benchmark papers and classify citation contexts using NLP, then we can distinguish validation claims from baseline mentions with >85% precision, because benchmark construction choices create explicit constraints on what hypotheses can be validated.

**Type:** EXISTENCE (PoC validation)
**Prerequisites:** None (foundation hypothesis)
**Dependencies:** Runs parallel with H-M1; both must pass Gate 1 before H-M2

### Research Basis

- SciBERT (Beltagy et al., 2019): Pre-trained on 1.14M scientific papers, achieves 80-90% on scientific text classification
- BERT fine-tuning best practices: 2e-5 LR, linear warmup, 3-5 epochs
- Dataset sources: ArXiv API, Semantic Scholar API, Papers with Code API (all public)

---

## Product Goals

### Primary Objectives

1. **Data Collection Pipeline**
   - Fetch 50-100 benchmark papers from ArXiv (2015-2024, ≥50 citations)
   - Extract citation contexts from Semantic Scholar
   - Sample 100-200 citations for manual annotation

2. **Manual Annotation Interface**
   - Binary labeling tool (validation claim vs other mention)
   - Feature extraction protocol (task type, metrics, modality, size)
   - Inter-rater agreement measurement (Cohen's kappa)

3. **Citation Classifier Training**
   - Fine-tune SciBERT on annotated citation contexts
   - 80/20 train/validation split
   - Target: >85% precision on test set

4. **Feature Extraction Validation**
   - Two annotators label 20 benchmarks independently
   - Measure Cohen's kappa (target >0.80)
   - Identify ambiguous feature categories

### Secondary Objectives

- Generate visualizations (confusion matrix, PR curve, training metrics)
- Save trained model for downstream hypotheses (H-M3 uses citation classifier)
- Document data collection protocol for reproducibility

### Non-Goals (Out of Scope)

- Full-scale deployment (PoC only, single run with seed=42)
- Multi-class citation intent classification (binary only: validation vs other)
- Cross-domain benchmark coverage (DL only: ML/CV/NLP)
- Real-time inference API (offline batch processing sufficient)

---

## User Stories

### US-1: Data Collection
**As a** researcher  
**I want to** fetch benchmark papers and citation contexts from public APIs  
**So that** I can build an annotated dataset for citation classification

**Acceptance Criteria:**
- Fetch 50-100 benchmark papers from ArXiv (2015-2024, mentions "benchmark" or "dataset")
- Filter by citation count ≥50 using Semantic Scholar
- Extract 100-200 random citation contexts (3-sentence windows)
- Save raw data to JSON/CSV for annotation

### US-2: Manual Annotation
**As an** annotator  
**I want to** label citation contexts and extract design features from benchmark papers  
**So that** I can provide ground truth for classifier training

**Acceptance Criteria:**
- Simple CLI/notebook interface for binary labeling (validation claim: yes/no)
- Feature extraction form (task type, metrics, modality, dataset size)
- Two annotators independently label same 20 benchmarks
- Cohen's kappa calculated automatically (target >0.80)

### US-3: Classifier Training
**As a** machine learning engineer  
**I want to** fine-tune SciBERT on annotated citation contexts  
**So that** I can achieve >85% precision on validation claim detection

**Acceptance Criteria:**
- Load "allenai/scibert_scivocab_uncased" from Hugging Face
- Tokenize citation contexts (max 512 tokens)
- Train with hyperparameters: LR=2e-5, batch=16, epochs=3-5, early stopping
- Evaluate on held-out 20% test set
- Precision >85% (primary gate), Recall >70%, F1 >75%

### US-4: Visualization & Reporting
**As a** researcher  
**I want to** see training metrics and classification performance  
**So that** I can validate hypothesis and diagnose failure modes

**Acceptance Criteria:**
- Confusion matrix (2x2 predicted vs actual)
- Precision-Recall curve
- Training loss/metrics over time
- Feature extraction agreement heatmap
- Citation context length distribution
- All figures saved to `h-e1/figures/`

---

## Functional Requirements

### FR-1: Data Collection Module
**Priority:** P0 (Must Have)

**Requirements:**
- FR-1.1: Implement ArXiv API search (query: "benchmark OR dataset evaluation", max_results=200)
- FR-1.2: Filter papers by citation count ≥50 via Semantic Scholar API
- FR-1.3: Extract citation contexts (3-sentence windows: before, containing, after)
- FR-1.4: Sample 100-200 citations randomly (reproducible seed)
- FR-1.5: Save to structured format (JSON/CSV with fields: paper_id, citing_paper, context_text)

**Technical Notes:**
- Use `arxiv` Python library (pip install arxiv)
- Use `semanticscholar` Python library or REST API
- Handle API rate limits (sleep between requests)
- Cache intermediate results (avoid re-fetching)

### FR-2: Annotation Interface
**Priority:** P0 (Must Have)

**Requirements:**
- FR-2.1: CLI/notebook tool for binary labeling (display context, record label)
- FR-2.2: Feature extraction form (dropdown for task type via PWC taxonomy, regex for metrics, text for modality/size)
- FR-2.3: Save annotations to separate files per annotator (annotator1.json, annotator2.json)
- FR-2.4: Calculate Cohen's kappa on 20 overlapping benchmarks
- FR-2.5: Report kappa score (must be >0.80 for gate pass)

**Technical Notes:**
- Simple Python script or Jupyter notebook sufficient (no web UI needed)
- Task type taxonomy from Papers with Code API (standard categorization)
- Metrics extraction: regex patterns for common DL metrics (accuracy, F1, BLEU, etc.)

### FR-3: Citation Classifier
**Priority:** P0 (Must Have)

**Requirements:**
- FR-3.1: Load SciBERT model ("allenai/scibert_scivocab_uncased")
- FR-3.2: Add classification head (num_labels=2)
- FR-3.3: Tokenize inputs (max_length=512, truncation=True, padding=True)
- FR-3.4: Split data 80/20 (train/validation)
- FR-3.5: Train with Hugging Face Trainer (AdamW, LR=2e-5, batch=16, epochs=3-5)
- FR-3.6: Early stopping on validation loss (patience=2 epochs)
- FR-3.7: Evaluate on test set (precision, recall, F1)
- FR-3.8: Save trained model to `h-e1/models/scibert_citation_classifier/`

**Technical Notes:**
- Use `transformers` library (Hugging Face)
- Fixed seed=42 for reproducibility (single run, PoC)
- Monitor GPU memory (SciBERT base = 110M params, small batch size)

### FR-4: Evaluation Metrics
**Priority:** P0 (Must Have)

**Requirements:**
- FR-4.1: Calculate precision (pos_label=1, "validation claim")
- FR-4.2: Calculate recall (pos_label=1)
- FR-4.3: Calculate F1 score
- FR-4.4: Generate classification report (sklearn)
- FR-4.5: Report Cohen's kappa for feature extraction agreement
- FR-4.6: Log all metrics to JSON (results.json)

**Technical Notes:**
- Use `sklearn.metrics` (precision_score, recall_score, f1_score, classification_report, cohen_kappa_score)
- Precision is PRIMARY gate metric (>85%)
- Kappa is SECONDARY gate metric (>0.80)

### FR-5: Visualization
**Priority:** P1 (Should Have)

**Requirements:**
- FR-5.1: Confusion matrix (2x2, predicted vs actual)
- FR-5.2: Precision-Recall curve
- FR-5.3: Training metrics over epochs (loss, precision, recall)
- FR-5.4: Feature extraction agreement heatmap (kappa per feature type)
- FR-5.5: Citation context length distribution (histogram)
- FR-5.6: Save all figures to `h-e1/figures/` (PNG format)

**Technical Notes:**
- Use `matplotlib` or `seaborn` for plotting
- All figures must be reproducible (fixed seed, deterministic)

---

## Non-Functional Requirements

### NFR-1: Performance
- Data collection: <30 minutes for 50-100 papers (API-limited)
- Annotation: ~1 hour per annotator for 100 citations (manual)
- Training: <1 hour on single GPU (small dataset, 3-5 epochs)
- Total experiment runtime: <2 hours (excluding manual annotation)

### NFR-2: Reproducibility
- Fixed random seed (42) for all stochastic operations
- Version-pinned dependencies (transformers, torch, sklearn)
- All hyperparameters documented in config file
- Dataset collection protocol documented (API queries, filters)

### NFR-3: Maintainability
- Modular code structure (data collection, annotation, training, evaluation as separate scripts)
- Clear docstrings for all functions
- No external dependencies beyond standard DL libraries (torch, transformers, sklearn, arxiv, semanticscholar)

### NFR-4: Scalability (Not Critical for PoC)
- Current scope: 100-200 annotated samples (sufficient for PoC)
- Future scaling: Could extend to 1000+ samples with minimal code changes

---

## Technical Constraints

### TC-1: Library Dependencies
- Python ≥3.8
- PyTorch ≥1.10 (for transformers)
- Hugging Face transformers ≥4.20
- scikit-learn ≥1.0
- arxiv, semanticscholar libraries (pip installable)

### TC-2: Compute Resources
- GPU recommended but not required (CPU training feasible for small dataset)
- RAM: 8GB minimum (SciBERT base model)
- Disk: ~500MB for model + data

### TC-3: API Limitations
- ArXiv API: No rate limit but recommend <10 requests/sec
- Semantic Scholar API: 100 requests/5 minutes (free tier)
- Papers with Code API: Rate limit varies (cache taxonomy locally)

### TC-4: Data Constraints
- Manual annotation effort: ~2 hours total (2 annotators × 1 hour each)
- Annotation quality depends on clear protocol (PWC taxonomy for tasks, regex for metrics)
- Small dataset (100-200 samples) may limit generalization but sufficient for PoC

---

## Success Metrics

### Gate Metrics (Primary)

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Citation Precision | >85% | TBD | PENDING |
| Feature Kappa | >0.80 | TBD | PENDING |

**Gate Type:** MUST_WORK (both metrics must pass)

**Failure Response:**
- Precision <80%: PIVOT - Refine classifier (try RoBERTa, more training data, different features)
- Kappa <0.70: EXPLORE - Improve annotation protocol (clearer instructions, examples)

### Secondary Metrics

- Citation Recall: >70%
- Citation F1: >75%
- Training convergence: Validation loss decreases monotonically
- No overfitting: Train-val loss gap <10%

---

## Implementation Phases

### Phase 0: Environment Setup (0.5 days)
- Install dependencies (transformers, torch, sklearn, arxiv, semanticscholar)
- Test API access (ArXiv, Semantic Scholar, Papers with Code)
- Create project structure (`data/`, `models/`, `figures/`, `scripts/`)

### Phase 1: Data Collection (2 days)
- Implement ArXiv search and Semantic Scholar filtering (FR-1)
- Extract citation contexts from 50-100 benchmarks
- Sample 100-200 citations randomly
- Save to `data/raw_citations.json`

### Phase 2: Manual Annotation (2 days)
- Build annotation interface (CLI/notebook, FR-2)
- Two annotators label citation contexts independently
- Extract features from 20 overlapping benchmarks
- Calculate Cohen's kappa

### Phase 3: Classifier Training (3 days)
- Implement SciBERT fine-tuning (FR-3)
- Train with 80/20 split, early stopping
- Evaluate on test set (FR-4)
- Save trained model

### Phase 4: Visualization & Reporting (1 day)
- Generate all required figures (FR-5)
- Log metrics to JSON
- Validate gate criteria (precision >85%, kappa >0.80)

### Phase 5: Documentation (0.5 days)
- Write experiment README
- Document data collection protocol
- Save validation report to `h-e1/04_validation.md`

**Total Duration:** ~9 days (within 2-week estimate from Phase 2B)

---

## Risk Assessment

### Risk 1: Low Citation Context Quality
**Probability:** Medium  
**Impact:** High (affects classifier performance)  
**Mitigation:** Use 3-sentence windows (before, containing, after) to provide sufficient context. Validate sample quality manually before annotation.

### Risk 2: Low Inter-Rater Agreement (Kappa <0.80)
**Probability:** Medium  
**Impact:** High (fails secondary gate)  
**Mitigation:** Provide clear annotation protocol with examples. Pilot with 5 benchmarks, refine protocol, then proceed.

### Risk 3: Insufficient Training Data (100-200 samples)
**Probability:** Medium  
**Impact:** Medium (precision <85%)  
**Mitigation:** Use transfer learning (SciBERT pre-trained on scientific text). If needed, increase annotation to 300 samples (within 2-week budget).

### Risk 4: API Rate Limits
**Probability:** Low  
**Impact:** Low (delays data collection)  
**Mitigation:** Cache intermediate results. Sleep between requests. Use free tier limits conservatively.

### Risk 5: Overfitting on Small Dataset
**Probability:** Medium  
**Impact:** Medium (test precision inflated)  
**Mitigation:** Use early stopping. Monitor train-val loss gap. Report both validation and test metrics separately.

---

## Open Questions

1. **Annotation Protocol Clarity:** Should we provide examples for edge cases (e.g., benchmark mentioned in related work vs methods)?
   - **Resolution:** Pilot with 5 benchmarks, document edge cases, refine protocol.

2. **Citation Context Window Size:** Is 3 sentences sufficient or should we use 5?
   - **Resolution:** Start with 3 sentences (standard). Analyze truncation rate. If >20% contexts truncated, expand to 5.

3. **Task Taxonomy Source:** Use Papers with Code taxonomy or custom?
   - **Resolution:** Use PWC taxonomy (standardized, widely adopted in DL community).

4. **Model Selection:** SciBERT vs RoBERTa-scientific?
   - **Resolution:** Start with SciBERT (trained on scientific papers, well-established). RoBERTa as fallback if precision <80%.

---

## Acceptance Criteria (Definition of Done)

- [ ] Data collection pipeline implemented and tested (50-100 benchmarks fetched)
- [ ] 100-200 citation contexts annotated by two independent annotators
- [ ] Cohen's kappa >0.80 on feature extraction (20 overlapping benchmarks)
- [ ] SciBERT classifier trained (80/20 split, early stopping, seed=42)
- [ ] Citation precision >85% on test set (PRIMARY GATE)
- [ ] All visualizations generated and saved to `h-e1/figures/`
- [ ] Trained model saved to `h-e1/models/scibert_citation_classifier/`
- [ ] Metrics logged to `h-e1/results.json`
- [ ] Validation report written to `h-e1/04_validation.md`
- [ ] Code runs end-to-end without errors (reproducible with seed=42)

---

## Appendix: References

### Phase 2C Experiment Brief
- **File:** 02c_experiment_brief.md
- **Sections Used:** Dataset, Models, Training Protocol, Evaluation, Visualization

### Phase 2B Verification Plan
- **File:** 02b_verification_plan.md
- **Sections Used:** Success criteria (>85% precision, >0.80 kappa), Gate type (MUST_WORK)

### Original Papers
- Beltagy, I., Lo, K., & Cohan, A. (2019). SciBERT: A Pretrained Language Model for Scientific Text. EMNLP 2019.
- Devlin, J., et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.

### API Documentation
- ArXiv API: https://arxiv.org/help/api
- Semantic Scholar API: https://api.semanticscholar.org
- Papers with Code API: https://paperswithcode.com/api/v1/docs

---

**Document Status:** FINAL
**Next Phase:** Phase 3 - Architecture Design
**Validation:** All requirements traced to 02c_experiment_brief.md
