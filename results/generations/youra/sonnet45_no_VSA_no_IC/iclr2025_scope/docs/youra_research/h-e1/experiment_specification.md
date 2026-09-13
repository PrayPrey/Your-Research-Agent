# Experiment Specification: H-E1 Attention-Relevance Correlation

**Hypothesis ID**: h-e1  
**Generated**: 2026-08-20  
**Status**: Design Complete

---

## Hypothesis

**Statement**: Retrieval relevance scores correlate moderately (Spearman ρ > 0.3) with attention weights during answer generation

**Type**: EXISTENCE  
**Gate**: MUST_WORK  
**Success Criterion**: Spearman ρ > 0.3 for both BM25 and Contriever retrievers

---

## Experiment Overview

### Objective
Measure correlation between retrieval relevance scores and LLM attention patterns during RAG-based QA to validate foundational assumption of provenance-aware KV cache management.

### Dataset
- **Source**: LongBench multi-doc QA (`hotpotqa`, `2wikimqa`, `musique`)
- **Sample Size**: 600 questions
- **Context Length**: 8k-15k tokens per question
- **Type**: Real standard dataset (no synthetic data)

### Retrieval Setup
**Dual Retriever Configuration**:
1. **BM25** (lexical): rank_bm25 library, k1=1.5, b=0.75, top-k=10
2. **Contriever** (semantic): facebook/contriever-msmarco, max_len=512, top-k=10

### Model Configuration
- **Model**: Llama-2-7B-Chat (meta-llama/Llama-2-7b-chat-hf)
- **Context Window**: 8192 tokens
- **Generation**: Greedy decoding, max_new_tokens=128
- **Attention Extraction**: PyTorch forward hooks on layer -1

### Analysis Pipeline
1. Extract attention weights: generated tokens → all context tokens
2. Aggregate attention per passage (sum over tokens in passage boundary)
3. Compute Spearman rank correlation: retrieval_scores vs passage_attentions
4. Stratify by: retriever type, query complexity, answer correctness

---

## Metrics

### Primary
- **Spearman ρ**: Rank correlation between retrieval scores and attention weights
- **Target**: ρ > 0.3 (moderate correlation threshold)

### Secondary
- **Query-token attention concentration**: Ratio of attention on query tokens vs all context
- **Answer accuracy**: Exact match or F1 > 0.5 (for correctness stratification)

### Baselines
- **Random retrieval**: Shuffled scores → expect ρ ≈ 0
- **Uniform attention**: Flat weights → expect ρ ≈ 0

---

## Implementation Tasks

### Epic 1: Data Preparation (8 tasks)
1. Download LongBench (hotpotqa, 2wikimqa, musique)
2. Segment passages (parse "\n\n" boundaries)
3. Label query complexity (word count + entity density)
4. Implement BM25 retrieval
5. Implement Contriever retrieval
6. Store retrieval results (passage IDs + scores)
7. Validate data pipeline
8. Cache processed dataset

### Epic 2: Model Setup (6 tasks)
1. Load Llama-2-7B-Chat
2. Implement AttentionCollector hook class
3. Register hooks on model.layers[-1].self_attn
4. Implement attention aggregation (average heads, sum over tokens)
5. Implement passage-level attention mapping
6. Unit test attention extraction

### Epic 3: Experiment Execution (5 tasks)
1. Implement question batching
2. Run generation loop (600 questions)
3. Save attention outputs per question
4. Label answer correctness
5. Checkpoint every 100 questions

### Epic 4: Correlation Analysis (6 tasks)
1. Compute Spearman correlation per question
2. Aggregate results (mean ρ, 95% CI)
3. Stratified analysis (retriever/complexity/correctness)
4. Generate scatter plots
5. Generate correlation heatmaps
6. Write validation report

### Epic 5: Baselines (3 tasks)
1. Random retrieval baseline
2. Uniform attention baseline
3. Statistical significance testing

**Total**: 28 subtasks across 5 epics

---

## Compute Requirements

- **Hardware**: 1x A100 40GB GPU
- **Wall-Clock Time**: 2.5 hours
  - Data prep: 30 min
  - Attention extraction: 2 GPU-hours
  - Analysis: 10 min
- **Storage**: 3.1 GB
  - Preprocessed data: 100 MB
  - Attention weights: 3 GB
  - Results: 10 MB

---

## Expected Outputs

### During Execution
- `data/longbench_raw/`: HuggingFace downloaded datasets
- `data/preprocessed/`: Segmented passages + retrieval scores
- `outputs/attentions/`: NumPy arrays (600 files, ~5MB each)
- `outputs/checkpoints/`: Resume state every 100 questions

### Final Results
- `outputs/results/correlation_matrix.csv`: ρ values per stratification
- `outputs/results/summary_statistics.json`: Mean, CI, p-values
- `outputs/plots/scatter_bm25.png`: BM25 score vs attention
- `outputs/plots/scatter_contriever.png`: Contriever score vs attention
- `outputs/plots/heatmap_stratified.png`: ρ by retriever/complexity/correctness
- `validation_report.md`: Full analysis + pass/fail decision

---

## Success Criteria

### PASS Conditions
- Mean Spearman ρ > 0.3 for both BM25 AND Contriever
- p-value < 0.05 vs random baseline (statistically significant)
- Correlation robust across stratifications (no negative ρ in any subgroup)

### FAIL Conditions
- ρ ≤ 0.3 for either retriever
- Negative correlation in any major subgroup
- Correlation only holds for correct answers (confounded)

### Next Actions
- **PASS**: Proceed to H-M1 (Pilot 2: tiered eviction single-hop)
- **FAIL**: Route to Phase 0 (fundamental assumption broken)

---

## Risk Mitigation

### Technical Risks
1. **Attention extraction bugs**: Unit tests verify shape, non-zero values, uniform baseline
2. **Passage boundary errors**: Manual inspection + cross-check with LongBench source
3. **Compute overrun**: Checkpointing every 100 questions for resume capability

### Scientific Risks
1. **Low correlation**: Dual-retriever validation isolates retriever-specific failures
2. **Correctness confound**: Stratified analysis separates correct vs incorrect answers
3. **Query complexity effects**: Secondary metric validates adaptive tiering (H-M3 support)

---

## References

- **Experiment Brief**: `../02c_experiment_brief.md` (detailed specification)
- **Verification Plan**: `../02b_verification_plan.md` (sub-hypothesis context)
- **LongBench Paper**: https://arxiv.org/abs/2308.14508
- **Contriever Paper**: https://arxiv.org/abs/2112.09118
- **H2O Paper**: NeurIPS 2023 (baseline comparison)

---

**Status**: Ready for Phase 3 Implementation Planning  
**Archon Task**: 8e5db332-77b0-4e63-816f-99dac9f2fbeb  
**Next Phase**: Generate PRD + Architecture + Task Decomposition
