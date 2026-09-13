# H-E1: Retrieval-Attention Correlation Experiment

**Hypothesis**: Retrieval relevance scores correlate moderately (Spearman ρ > 0.3) with attention weights during answer generation

**Type**: EXISTENCE (foundational validation)  
**Gate**: MUST_WORK  
**Status**: Design Complete  
**Phase**: 2C (Experiment Design)

---

## Quick Links

- **Main Experiment Brief**: [`../02c_experiment_brief.md`](../02c_experiment_brief.md)
- **Verification Plan**: [`../02b_verification_plan.md`](../02b_verification_plan.md)
- **Archon Task**: `8e5db332-77b0-4e63-816f-99dac9f2fbeb`

---

## Hypothesis Overview

### Research Question
Do retrieval relevance scores (BM25 lexical + Contriever semantic) predict which passages LLMs attend to during RAG-based QA?

### Why This Matters
The main hypothesis (provenance-aware KV cache) assumes retrieval metadata predicts attention utility. If retrieval scores don't correlate with attention weights, provenance-based eviction is fundamentally invalid.

### Success Criterion
Spearman ρ > 0.3 for **both** BM25 and Contriever retrievers (moderate correlation threshold)

### Failure Consequence
Route to Phase 0 (entire provenance hypothesis invalidated)

---

## Experiment Design Summary

### Dataset
- **Source**: LongBench multi-doc QA (`hotpotqa`, `2wikimqa`, `musique`)
- **Size**: 600 questions
- **Type**: Real standard dataset (no synthetic data)
- **Context Length**: 8k-15k tokens per question

### Retrieval Setup
**Dual Configuration**:
1. **BM25** (lexical): rank_bm25, top-k=10
2. **Contriever** (semantic): facebook/contriever-msmarco, top-k=10

### Model
- **Base Model**: Llama-2-7B-Chat
- **Attention Extraction**: PyTorch forward hooks on layer -1
- **Generation**: Greedy decoding, max_tokens=128

### Analysis
1. Extract attention: generated tokens → context tokens
2. Aggregate per passage: sum attention over passage boundaries
3. Compute Spearman ρ: retrieval_scores vs passage_attentions
4. Stratify by: retriever type, query complexity, answer correctness

---

## File Structure

```
h-e1/
├── README.md                          # This file (experiment overview)
├── experiment_specification.md        # Detailed experiment design
├── dataset_specification.yaml         # Dataset config (LongBench tasks, preprocessing)
├── baseline_experiments.yaml          # Baseline definitions (random, uniform, position)
├── evaluation_metrics.yaml            # Metrics (Spearman ρ, stratification, plots)
└── [Future: validation_report.md]    # Phase 4 output (after execution)
```

---

## Implementation Tasks (28 Subtasks)

### Epic 1: Data Preparation (8 tasks)
Download LongBench → segment passages → label complexity → BM25 retrieval → Contriever retrieval → validate → cache

### Epic 2: Model Setup (6 tasks)
Load Llama-2 → implement hooks → register attention extraction → aggregate attention → map passages → unit test

### Epic 3: Experiment Execution (5 tasks)
Batch questions → generation loop (600 questions) → save attentions → label correctness → checkpoint

### Epic 4: Correlation Analysis (6 tasks)
Compute Spearman ρ → aggregate results → stratified analysis → scatter plots → heatmaps → validation report

### Epic 5: Baselines (3 tasks)
Random retrieval baseline → uniform attention baseline → statistical tests

---

## Compute Budget

- **Hardware**: 1x A100 40GB GPU
- **Time**: 2.5 hours
  - Data prep: 30 min
  - Attention extraction: 2 GPU-hours
  - Analysis: 10 min
- **Storage**: 3.1 GB

---

## Expected Outputs

### During Execution
- `data/longbench_raw/`: Downloaded datasets
- `data/preprocessed/`: Segmented passages + retrieval scores
- `outputs/attentions/`: NumPy arrays (600 files)
- `outputs/checkpoints/`: Resume state every 100 questions

### Final Results
- `outputs/results/correlation_matrix.csv`: ρ values per stratification
- `outputs/results/summary_statistics.json`: Mean, CI, p-values
- `outputs/plots/scatter_bm25.png`: BM25 score vs attention
- `outputs/plots/scatter_contriever.png`: Contriever score vs attention
- `outputs/plots/heatmap_stratified.png`: Stratified ρ heatmap
- `validation_report.md`: Full analysis + gate decision

---

## Success/Failure Criteria

### PASS (→ H-M1)
- Mean ρ > 0.3 for both BM25 AND Contriever
- p < 0.05 (statistically significant vs random baseline)
- Robust across stratifications (no negative ρ subgroups)

### FAIL (→ Phase 0)
- ρ ≤ 0.3 for either retriever
- Negative correlation in any major subgroup
- Correlation only holds for correct answers (confounded)

---

## Key References

### Papers
- **H2O**: Zhang et al., NeurIPS 2023 (baseline KV cache eviction)
- **LongBench**: Bai et al., 2023 (https://arxiv.org/abs/2308.14508)
- **Contriever**: Izacard et al., 2022 (https://arxiv.org/abs/2112.09118)
- **DPR**: Karpukhin et al., 2020 (https://arxiv.org/abs/2004.04906)
- **Lost in the Middle**: Liu et al., 2023 (https://arxiv.org/abs/2307.03172)

### Code Resources
- LongBench: https://huggingface.co/datasets/THUDM/LongBench
- Contriever: https://huggingface.co/facebook/contriever-msmarco
- Llama-2: https://huggingface.co/meta-llama/Llama-2-7b-chat-hf
- Attention extraction: https://gist.github.com/airalcorn2/50ec06517ce96ecc143503e21fa6cb91
- rank_bm25: https://pypi.org/project/rank-bm25/

---

## Next Steps

1. **Phase 3** (Implementation Planning):
   - Generate PRD (Product Requirements Document)
   - Architecture document (data pipeline, model setup, analysis)
   - Decompose 28 tasks into Archon subtasks

2. **Phase 4** (PoC Validation):
   - Implement 28 subtasks sequentially
   - Execute experiment (2.5 GPU-hours)
   - Generate validation report
   - Update gate status (PASS/FAIL)

3. **Gate Decision**:
   - PASS → H-M1 (Pilot 2: tiered eviction single-hop)
   - FAIL → Phase 0 routing (fundamental assumption broken)

---

## Archon Integration

- **Pipeline Project**: dd500899-44fd-44d5-b7ea-7d7ec8f5c571
- **Hypothesis Task**: 8e5db332-77b0-4e63-816f-99dac9f2fbeb
- **Current Status**: DESIGN_COMPLETED (Phase 2C)
- **Next Phase**: IMPLEMENTATION_PLANNING (Phase 3)

---

**Last Updated**: 2026-08-20  
**Document Version**: 1.0  
**Ready for Phase 3**: ✅ YES
