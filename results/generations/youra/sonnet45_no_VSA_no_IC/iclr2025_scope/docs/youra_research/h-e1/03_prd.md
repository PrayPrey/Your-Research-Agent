# Product Requirements Document (PRD)
## H-E1: Retrieval-Attention Correlation Experiment

**Version**: 1.0  
**Date**: 2026-08-20  
**Hypothesis ID**: h-e1  
**Gate**: MUST_WORK  
**Status**: PLANNING

---

## Executive Summary

Build experiment harness to validate whether retrieval relevance scores (BM25 + semantic) correlate moderately (Spearman ρ > 0.3) with LLM attention weights during RAG-based QA. If correlation fails, entire provenance-aware KV cache hypothesis invalidated → Phase 0 routing.

**Success Criterion**: Spearman ρ > 0.3 for both BM25 and Contriever retrievers across 600 LongBench multi-doc QA questions.

**Timeline**: 2.5 GPU-hours wall-clock, ~3 days implementation

**Compute**: 1x A100 40GB GPU

---

## Product Vision

### Problem Statement
Current KV cache eviction methods (H2O, StreamingLLM) ignore retrieval metadata. Main hypothesis assumes retrieval scores predict LLM attention patterns, but no direct measurement exists for long-context RAG settings.

### Target Users
- Research team validating provenance-aware KV cache hypothesis
- Downstream: H-M1 pilot experiment design (tiered eviction)

### Success Metrics
1. **Primary**: Spearman ρ > 0.3 for both BM25 and Contriever (averaged across 600 questions)
2. **Robustness**: No negative correlation in any stratification subgroup
3. **Statistical**: p < 0.05 (correlation significantly different from zero)

---

## Functional Requirements

### FR1: Data Pipeline
**Priority**: P0 (blocks all downstream work)

**Capabilities**:
1. Download LongBench dataset (`hotpotqa`, `2wikimqa`, `musique`) from HuggingFace
2. Parse 600 questions, segment passages on "\n\n" boundaries
3. Label query complexity (word count + entity density via spaCy)
4. Run dual retrieval (BM25 via rank_bm25, Contriever via HuggingFace)
5. Store retrieval scores (BM25, Contriever) per passage per question
6. Cache preprocessed dataset (pickle format, <100MB)

**Inputs**:
- LongBench dataset: `THUDM/LongBench` (HuggingFace)
- Retrieval top-k: 10 passages per question

**Outputs**:
- `preprocessed_longbench_h-e1.pkl`: 600 questions + passages + retrieval scores
- `query_complexity_labels.pkl`: Simple/Complex labels per question

**Validation**:
- Passage count per question: 10-30 range
- BM25 scores > 0, Contriever scores in [-1, 1]
- No missing data (100% coverage)

---

### FR2: Attention Extraction
**Priority**: P0 (core hypothesis test)

**Capabilities**:
1. Load Llama-2-7B-Chat model (HuggingFace `meta-llama/Llama-2-7b-chat-hf`)
2. Install PyTorch forward hooks on last decoder layer self-attention
3. Extract attention weights during answer generation (`output_attentions=True`)
4. Aggregate attention: average over heads, sum over generated tokens
5. Map token-level attention → passage-level attention (via passage boundaries)
6. Save attention outputs per question (NumPy format)

**Inputs**:
- Preprocessed dataset (600 questions + passages)
- Model: Llama-2-7B-Chat (7B params, FP16, ~14GB VRAM)

**Outputs**:
- `attentions/question_{id}.npy`: (num_passages,) attention weights per question
- `answers/question_{id}.txt`: Generated answer text

**Generation Config**:
```python
{
    "max_new_tokens": 128,
    "temperature": 0.7,
    "top_p": 0.9,
    "do_sample": False,  # Greedy decoding
    "output_attentions": True
}
```

**Validation**:
- Attention shape: (num_generated_tokens, num_heads, seq_len, seq_len)
- Non-zero attention weights (no all-zeros bug)
- Passage boundary alignment (token positions match passages)

---

### FR3: Correlation Analysis
**Priority**: P0 (success criterion)

**Capabilities**:
1. Compute Spearman rank correlation (scipy.stats) per question
2. Stratify by retriever type (BM25, Contriever), query complexity, answer correctness
3. Bootstrap 95% confidence intervals (1000 resamples)
4. Run baselines: random retrieval, uniform attention, position bias
5. Generate scatter plots (retrieval score vs attention weight)
6. Statistical tests (observed vs random, BM25 vs Contriever)

**Inputs**:
- Retrieval scores: (600 questions, num_passages) for BM25 and Contriever
- Attention weights: (600 questions, num_passages)
- Ground truth answers (for correctness labeling)

**Outputs**:
- `per_question_correlations.csv`: ρ values per question
- `summary_statistics.json`: Mean ρ, 95% CI, stratified analysis
- `scatter_bm25.png`, `scatter_contriever.png`: Correlation visualizations
- `baseline_comparison.csv`: Observed vs random/uniform/position baselines

**Success Criterion**:
- `mean_rho_bm25 > 0.3` AND `mean_rho_contriever > 0.3`
- `p_bm25 < 0.05` AND `p_contriever < 0.05`

---

### FR4: Answer Correctness Labeling
**Priority**: P1 (stratification analysis)

**Capabilities**:
1. Exact match check (case-insensitive)
2. Token-level F1 score (nltk tokenization)
3. Label: Correct if (exact_match OR f1 > 0.5)

**Inputs**:
- Predicted answers (from generation)
- Ground truth answers (from LongBench)

**Outputs**:
- `answer_correctness_labels.pkl`: Correct/Incorrect per question

**Expected Distribution**:
- 40-60% correct (Llama-2-7B on LongBench multi-doc QA)

---

### FR5: Validation Reporting
**Priority**: P0 (gate decision)

**Capabilities**:
1. Generate validation report (`02d_validation_h-e1.md`)
2. Sections: Executive summary, correlation results, scatter plots, baseline comparisons, failure analysis, gate decision
3. PASS/FAIL determination based on ρ thresholds
4. Routing recommendation (H-M1 or Phase 0)

**Inputs**:
- All correlation results
- All baseline comparisons
- All visualizations

**Outputs**:
- `02d_validation_h-e1.md`: Validation report (target: <5 pages)

**Gate Decision Logic**:
- PASS: ρ_BM25 > 0.3 AND ρ_Contriever > 0.3 → Proceed to H-M1
- FAIL: ρ ≤ 0.3 for either retriever → Route to Phase 0

---

## Non-Functional Requirements

### NFR1: Performance
- Data preprocessing: <30 minutes wall-clock
- Attention extraction: <2 GPU-hours (600 questions × 12 sec/question)
- Correlation analysis: <10 minutes (CPU-bound)
- **Total wall-clock**: 2.5 hours

### NFR2: Reliability
- Checkpoint intermediate results every 100 questions
- Resume capability (if interrupted)
- Unit tests for passage segmentation, attention extraction, correlation computation

### NFR3: Reproducibility
- Fixed random seed: 42
- Deterministic generation (greedy decoding, `do_sample=False`)
- Cache all intermediate outputs (preprocessed data, attention weights)

### NFR4: Resource Constraints
- GPU: 1x A100 40GB (Llama-2-7B FP16 ~14GB, headroom for attention storage)
- Storage: ~3GB (attention weights) + ~100MB (preprocessed data)
- Memory: <64GB RAM for correlation analysis

---

## Technical Constraints

### TC1: Model Selection
- **Fixed**: Llama-2-7B-Chat (matches H2O baseline experiments)
- Rationale: Standard decoder-only architecture, fits single GPU, pre-trained for QA

### TC2: Dataset Selection
- **Fixed**: LongBench multi-doc QA (hotpotqa, 2wikimqa, musique)
- Rationale: Standard benchmark, multi-hop questions create relevance variation, 600 samples statistically powered

### TC3: Retrieval Methods
- **Fixed**: BM25 (lexical) + Contriever (semantic)
- Rationale: Test correlation robustness across retrieval paradigms (lexical vs dense)

### TC4: Attention Extraction Layer
- **Fixed**: Last decoder layer (`model.layers[-1].self_attn`)
- Rationale: Research shows last layer attention most predictive of generation decisions

---

## Dependencies

### External Libraries
- `transformers` (HuggingFace): Model loading, tokenization, generation
- `torch` (PyTorch): Attention hooks, GPU inference
- `rank_bm25`: Lexical retrieval
- `scipy`: Spearman correlation, statistical tests
- `spacy`: Named entity recognition (entity density)
- `nltk`: Tokenization (BM25, F1 score)
- `numpy`, `matplotlib`: Data processing, visualization

### Dataset Dependencies
- LongBench dataset: `THUDM/LongBench` (HuggingFace)
- Contriever model: `facebook/contriever-msmarco` (HuggingFace)
- Llama-2-7B-Chat: `meta-llama/Llama-2-7b-chat-hf` (HuggingFace, requires access token)

### Compute Dependencies
- 1x A100 40GB GPU (or equivalent V100 32GB with model quantization)
- Linux environment (CUDA 11.8+)

---

## Risk Mitigation

### Risk 1: Correlation Below Threshold
- **Mitigation**: Dual-retriever validation (BM25 + Contriever)
- **Fallback**: If only one retriever succeeds, pivot to semantic-only metadata

### Risk 2: Attention Extraction Bugs
- **Mitigation**: Unit tests (attention shape verification), uniform attention baseline (should yield ρ ≈ 0)
- **Fallback**: Use `output_attentions=True` direct output (slower but more stable)

### Risk 3: LongBench Passage Parsing Errors
- **Mitigation**: Manual inspection (10 sample questions), cross-check with LongBench source code
- **Fallback**: Character-based passage boundaries (500-char windows)

---

## Success Criteria Summary

### Primary Success
- Spearman ρ > 0.3 for both BM25 and Contriever
- p < 0.05 (statistically significant)
- No negative correlation in any subgroup

### Secondary Success (for H-M3 support)
- Simple queries show higher query-token attention concentration than complex queries (t-test p < 0.05)

### Failure Triggers
- ρ ≤ 0.3 for either retriever → Phase 0 routing
- ρ_position > ρ_retrieval → Position bias dominates (Phase 0)

---

## Deliverables

1. **Code Repository**: `h-e1-attention-correlation/` (data prep, attention extraction, correlation analysis)
2. **Preprocessed Dataset**: `preprocessed_longbench_h-e1.pkl` (600 questions + retrieval scores)
3. **Attention Outputs**: `attentions/*.npy` (600 files, ~3GB total)
4. **Correlation Results**: `per_question_correlations.csv`, `summary_statistics.json`
5. **Visualizations**: Scatter plots, heatmaps, boxplots
6. **Validation Report**: `02d_validation_h-e1.md` (gate decision + routing recommendation)

---

## Open Questions

1. **Llama-2 Access**: HuggingFace access token required for `meta-llama/Llama-2-7b-chat-hf` — confirm credentials
2. **GPU Availability**: A100 40GB reserved? Fallback to V100 32GB requires FP16 quantization check
3. **Checkpoint Strategy**: Resume from checkpoint on interruption — store question IDs processed?

---

## Appendix: Epic Task Breakdown (Preview for Phase 3)

**Epic 1**: Data Preparation (~8 subtasks)  
**Epic 2**: Model Setup & Attention Extraction (~6 subtasks)  
**Epic 3**: Experiment Execution (~5 subtasks)  
**Epic 4**: Correlation Analysis & Reporting (~6 subtasks)  
**Epic 5**: Failsafe & Baseline Validation (~3 subtasks)  

**Total**: 5 epics, 28 subtasks (detailed breakdown in Architecture document)
