# Phase 2A: Refinement Summary

## Metadata
- **Generated at**: 2026-07-12T06:08:42Z
- **Workflow**: phase2a-dialogue
- **Architecture**: Self-Play Loop (Claude-only, IC-ablation)
- **Gap ID**: gap-1-rag-curation
- **Gap Title**: RAG-Specific Data Curation
- **Execution Mode**: UNATTENDED
- **Discussion Exchanges**: 17

---

## Research Dialogue Context

**Participants**: Dr. Nova, Prof. Vera, Dr. Sage, Prof. Pax, Dr. Ally, Prof. Rex

**Total Exchanges**: 17

**Convergence Reason**: All 6 convergence criteria met after 17 exchanges with all personas participating. Hypothesis evolved from incremental "build better RAG filter" to conceptual "systematically map quality-coverage-diversity trade-off space for retrieval corpus curation."

### Key Insights

1. **Data quality is task-specific and multi-dimensional**: Not a monolithic concept. Pretraining optimizes for fluency/coherence; retrieval optimizes for factual density/entity coverage. These dimensions are orthogonal.

2. **Retrieval-optimal diverges from pretraining-optimal**: Documents that fail pretraining quality tests (high perplexity, low educational score) can succeed at retrieval (technical docs, API references, structured data tables).

3. **Factorized approach preserves diversity**: Single-dimension quality optimization risks homogenization. Multiple specialist classifiers (factoid, argumentative, technical) maintain corpus coverage across retrieval modes.

4. **Meta-contribution framework**: Analogous to DataComp-LM's benchmark role for pretraining, we provide systematic comparison framework for RAG filtering strategies along quality-coverage-diversity axes.

### Breakthrough Moments

- **Exchange 4**: Dr. Nova proposed factorized specialist classifier ensemble targeting different retrieval modes (factoid/argumentative/technical), addressing diversity concerns.

- **Exchange 7**: Dr. Ally introduced stratified training strategy (oversample low-educational, high-BEIR examples) to explicitly enforce retrieval-pretraining divergence.

- **Exchanges 12-13**: Prof. Vera and Dr. Ally developed difficulty-adjusted quality gain measurement (semantic vs lexical queries) to demonstrate quality beyond keyword matching.

- **Exchanges 16-17**: Dr. Nova and Dr. Sage reframed contribution from "better filter" to "quality-coverage trade-off characterization methodology" (meta-contribution).

---

## Final Hypothesis

### Title
RAG-Specific Corpus Curation via Retrieval-Quality Classifiers

### Hypothesis ID
H-RAGCuration-v1

### Core Claim
**Under-If-Then-Because Statement:**

Under RAG corpus construction from Common Crawl, **if** a factorized ensemble of specialist retrieval-quality classifiers (trained on stratified BEIR success examples) filters documents, **then** the resulting corpus achieves ≥3% higher Recall@10 on factoid QA tasks compared to perplexity-based filtering (matched corpus size), **because** retrieval utility optimizes for factual density, entity coverage, and retrieval-specific quality dimensions orthogonal to pretraining fluency.

### Mechanism

**4-Step Causal Chain:**

1. **Classifier Training**: Retrieval-quality classifier learns to identify documents with high factual density and entity coverage by training on positive examples (successful BEIR retrievals stratified by low educational score) vs negative examples (failed retrievals). This stratification forces the classifier to learn retrieval-specific signals independent of pretraining quality.

2. **Semantic Quality Improvement**: Documents with high factual density and entity coverage improve retrieval performance specifically on semantic queries (where BM25 lexical matching fails) because they contain information in multiple phrasings and higher informativeness per token.

3. **Diversity Preservation**: The factorized specialist classifier approach (multiple classifiers for factoid/argument/technical modes) preserves corpus diversity while ensuring quality, avoiding homogenization that single-quality-dimension filtering causes.

4. **Measurable Divergence**: Retrieval-optimal and pretraining-optimal corpora diverge measurably because retrieval values factual density over narrative fluency, leading to systematic differences in document selection (high-perplexity technical docs selected by retrieval filter, rejected by pretraining filter).

---

## Testable Predictions

### P1 (Primary): Retrieval Performance Improvement
**Statement**: Corpus filtered by retrieval-quality classifier achieves ≥3% higher Recall@10 on BEIR Natural Questions than perplexity-filtered baseline (matched 1M document corpus size).

**Test Method**: Three-way controlled comparison (Perplexity vs Educational vs Retrieval filtering) on 100K Common Crawl sample. Index with DPR, measure Recall@10 on 10K Natural Questions test queries.

**Success Criterion**: Retrieval filter achieves Recall@10 ≥ Perplexity + 0.03 (absolute), p<0.05 (two-tailed t-test, 3-5 replications)

**Falsification**: If |ΔRecall@10| < 0.01 or p>0.05, retrieval-specific filtering provides no measurable advantage.

### P2: Corpus Divergence
**Statement**: Top-50K documents selected by retrieval filter show <60% overlap with educational filter, and divergent subset contributes ≥2% absolute Recall@10 gain.

**Test Method**: Compute set intersection between top-50K from each filter. Measure Recall@10 using (1) educational-filtered corpus alone, (2) educational + divergent subset.

**Success Criterion**: Overlap <60% AND ΔRecall ≥ 0.02

**Falsification**: If overlap >80% OR ΔRecall <0.01, divergence is not performance-relevant.

### P3: Semantic vs Lexical Quality Signal
**Statement**: Retrieval-quality corpus shows +4% Recall gain on semantic queries (BM25-failed) vs +1% on lexical queries (BM25-succeeded), demonstrating quality beyond keyword matching.

**Test Method**: Split Natural Questions into Lexical (answer in top-10 BM25) vs Semantic (answer not in top-10 BM25) subsets. Measure Recall@10 improvement separately.

**Success Criterion**: ΔRecall_semantic ≥ 0.04 AND ΔRecall_lexical ≤ 0.01

**Falsification**: If gains are uniform (within 0.01), improvement is just lexical coverage, not semantic quality.

---

## Novelty & Differentiation

### Key Innovation
Factorized specialist classifier ensemble that targets retrieval-specific quality dimensions (factual density, entity coverage) independent of pretraining quality, validated via stratified training on low-educational, high-BEIR examples.

### Differentiation from Prior Work

**vs. DataComp-LM** [Li et al., 2024]:
- DataComp-LM optimizes for pretraining quality (MMLU via next-token prediction)
- We optimize for retrieval utility (Recall@K) and demonstrate measurable divergence between these objectives
- Methodology transfer but different quality dimension

**vs. FineWeb-Edu** [Penedo et al., 2024]:
- FineWeb-Edu demonstrates domain-specific filtering (educational quality for knowledge tasks)
- We demonstrate task-specific filtering (retrieval utility for inference mode)
- Analogous methodology applied to different downstream use case

**vs. Perplexity-based filtering** (standard practice):
- Perplexity is pretraining-derived quality signal (fluency, coherence)
- Retrieval-quality classifier learns task-specific signals (factual density, entity coverage) via supervised training on retrieval success examples

### Meta-Contribution
Provides methodology for empirically characterizing filtering trade-offs along quality-coverage-diversity axes for RAG, analogous to DataComp-LM's benchmark contribution for pretraining. Enables principled RAG system design via systematic comparison framework.

---

## Experimental Design

### Dataset
**BEIR Natural Questions** (test set, ~3.5K queries)
- Factoid QA with extractive answers, ideal for controlled validation
- Derived from Wikipedia, likely well-covered in Common Crawl
- Sufficient size for statistical power (α=0.05, power=0.80)

### Model
**DPR (Dense Passage Retriever)**
- Standard dense retrieval architecture (bi-encoder)
- Pre-trained on Natural Questions (well-calibrated for task)
- Allows indexing filtered corpora without retraining

### Baselines
1. Perplexity-based (GPT-2 threshold, yield 1M docs)
2. Educational quality (FineWeb-Edu style)
3. Unfiltered random sample (1M docs from Common Crawl)

### Variables

**Independent**: Filtering Strategy (categorical: Perplexity | Educational | Retrieval-Quality)

**Dependent (Primary)**: Recall@10 on BEIR Natural Questions (continuous)

**Controlled**: Corpus Size (1M docs), Common Crawl source (same 100K sample), Retrieval Model (DPR)

---

## Scope & Limitations

### Applies To
- Factoid question answering with extractive answers (Natural Questions-style)
- RAG corpus construction from web-crawled data (Common Crawl)
- Dense retrieval systems (DPR, Contriever)
- English-language corpora

### Does Not Apply To
- Abstractive QA requiring multi-hop synthesis (not validated)
- Non-English retrieval (FastText classifier language-dependent)
- Argumentative retrieval or document ranking (factoid-specific validation)
- Sparse retrieval only (BM25 without dense component)

### Known Limitations
1. Validation restricted to Natural Questions benchmark; generalization to other retrieval modes requires further work
2. Reader model confound: downstream performance depends on both document quality and reader architecture
3. Coverage vs quality trade-off not fully characterized (focuses on fixed-size quality improvement)
4. Stratified training requires sufficient low-educational, high-retrieval examples in BEIR

---

## Key Assumptions & Risks

**A1**: BEIR relevance annotations correlate with downstream task performance (QA accuracy)
- **Risk**: Annotation bias toward fluent documents
- **Mitigation**: Two-stage validation (train on annotations, validate on exact match QA accuracy)

**A2**: Factual density and entity coverage are orthogonal to pretraining quality
- **Risk**: High correlation reduces novelty claim
- **Validation**: Measure type-token ratio and NE density for classifier-selected docs vs perplexity-matched controls

**A3**: Common Crawl coverage is sufficient (coverage failures <50% of BM25-failed queries)
- **Risk**: Most failures are coverage gaps, not quality issues
- **Validation**: Answer string search to categorize failure modes

**A4**: Retrieval quality measurable independent of reader model
- **Risk**: Neural reader capabilities affect measured quality
- **Mitigation**: Use controlled reader (BM25 + exact match) for factoid QA

**A5**: Factorized approach preserves diversity
- **Risk**: Multi-dimensional optimization still homogenizes
- **Validation**: Average pairwise SBERT similarity <0.6

---

## Phase 2B Readiness

### Status: READY

**SH1 (Existence)**: All experimental components are established technologies (BEIR benchmark, DPR architecture, FastText classifiers, Common Crawl corpus).

**SH2 (Mechanism)**: Test whether factorized specialist classifiers learn retrieval-specific quality signals independent of pretraining quality, and whether this translates to measurable Recall@10 improvements.

**SH3 (Comparison)**: Compare against perplexity and educational baselines to demonstrate divergence. Deferred to Phase 5: comparison against state-of-the-art RAG corpus curation methods (Voyage AI, Anthropic RAG).

### Open Questions
1. Does stratified training produce sufficient signal given BEIR size/bias?
2. Can two-stage validation confirm BEIR relevance correlates with downstream utility?
3. Does factorized approach actually preserve diversity (SBERT similarity <0.6)?
4. How does quality-coverage trade-off manifest in Recall@K curves (steeper early gains vs tail coverage)?

---

## Decision

**Overall Status**: VALIDATED

**Convergence**: All 6 criteria met (SPECIFIC, MECHANISM, PREDICTIONS, NOVELTY, FEASIBILITY, OBJECTIONS)

**Clarity**: HIGH (hypothesis is specific, testable, and falsifiable)

**Remaining Objections**: None (all concerns addressed with mitigation strategies)

---

**Next Phase**: Phase 2B - Research Planning (Roadmap Creation)

