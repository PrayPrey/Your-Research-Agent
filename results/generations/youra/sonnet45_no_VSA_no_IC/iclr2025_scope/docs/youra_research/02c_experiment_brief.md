# Phase 2C: Experiment Brief

**Generated**: 2026-08-20  
**Hypothesis ID**: h-e1  
**Hypothesis Type**: EXISTENCE  
**Gate**: MUST_WORK  
**Pipeline Project**: dd500899-44fd-44d5-b7ea-7d7ec8f5c571  
**Archon Task ID**: 8e5db332-77b0-4e63-816f-99dac9f2fbeb

---

## Hypothesis Statement

**H-E1: Retrieval relevance scores correlate moderately (Spearman ρ > 0.3) with attention weights during answer generation**

This is a foundational existence hypothesis that validates whether retrieval metadata (BM25 and semantic retrieval scores) aligns with LLM attention patterns during RAG-based QA. If this hypothesis fails (ρ ≤ 0.3), the entire provenance-aware KV cache approach is invalidated.

---

## Research Context

### Background
RAG-based long-context QA systems retrieve passages from large document collections and concatenate them into context windows (8k-32k tokens). Current KV cache eviction methods (H2O, StreamingLLM) treat all tokens uniformly, ignoring retrieval provenance metadata. The core assumption of the main hypothesis is that retrieval relevance scores predict which passages the LLM actually attends to during answer generation.

### Prior Work
- **H2O** (Zhang et al., NeurIPS 2023): Evicts tokens with low accumulated attention weights, achieving 20% cache retention with minimal accuracy degradation
- **Lost in the Middle** (Liu et al., 2023): Shows LLMs attend primarily to beginning/end of context, ignoring middle passages even when relevant
- **Contriever** (Izacard et al., 2022): Unsupervised dense retriever competitive with BM25 on BEIR benchmark
- **DPR** (Karpukhin et al., 2020): Dense passage retrieval trained on NaturalQuestions, establishes query-passage encoding framework

### Knowledge Gaps
1. No direct measurement of retrieval score vs attention weight correlation in long-context RAG settings
2. Unclear whether lexical (BM25) vs semantic (DPR/Contriever) retrieval scores better predict attention patterns
3. Unknown whether correlation holds for both correct and incorrect answers (potential confound if attention only aligns when answer is correct)

---

## Experiment Design

### Primary Objective
Measure Spearman rank correlation (ρ) between retrieval relevance scores and attention weights from generated answer tokens to passage tokens, stratified by:
1. **Retriever type**: BM25 (lexical) vs Contriever (semantic)
2. **Query complexity**: Simple (word count < 10, entity density < 0.3) vs Complex (word count ≥ 10, entity density ≥ 0.3)
3. **Answer correctness**: Correct vs Incorrect generations

### Success Criterion
**Primary**: Spearman ρ > 0.3 for both BM25 and Contriever retrievers (averaged across all questions)

**Secondary** (for H-M3 support): Simple queries show significantly higher query-token attention concentration than complex queries (two-sample t-test, p < 0.05)

### Falsification Criterion
If ρ ≤ 0.3 or negative correlation for either retriever type → Phase 0 routing (fundamental assumption broken)

---

## Dataset Specification

### Primary Dataset: LongBench Multi-Doc QA Subset
**Source**: HuggingFace `THUDM/LongBench` (https://huggingface.co/datasets/THUDM/LongBench)

**Task Selection**: 
- `hotpotqa` (multi-hop QA, 200 questions)
- `2wikimqa` (multi-hop QA, 200 questions)
- `musique` (multi-hop QA, 200 questions)

**Rationale**: Multi-hop questions require reasoning over multiple passages, creating variation in passage relevance (high-relevance passages contain answer evidence, low-relevance passages contain distractors or contrastive evidence)

**Total Sample Size**: 600 questions (statistically powered for correlation analysis with 95% confidence)

**Data Format** (from LongBench):
```json
{
    "input": "Question text",
    "context": "Long context (multiple concatenated passages)",
    "answers": ["Answer 1", "Answer 2"],
    "length": 15234,
    "dataset": "hotpotqa",
    "_id": "hotpotqa_123"
}
```

### Data Preprocessing
1. **Passage Segmentation**: Parse LongBench `context` field to recover individual passage boundaries (passages are separated by "\n\n" in LongBench format)
2. **Query Complexity Labeling**: 
   - Word count: `len(question.split())`
   - Entity density: Named entity count / total tokens (using spaCy NER)
   - Simple: word count < 10 AND entity density < 0.3
   - Complex: word count ≥ 10 OR entity density ≥ 0.3
3. **Answer Correctness Labeling**: Exact match or F1 > 0.5 against ground truth answers

**No Synthetic Data**: Using real LongBench standard dataset ensures meaningful results and aligns with baseline comparison requirements (H2O paper reports results on similar QA tasks)

---

## Retrieval Configuration

### Dual-Retriever Setup
Run retrieval with **both** BM25 (lexical) and Contriever (semantic) to test correlation robustness across retrieval paradigms.

#### BM25 Configuration
**Implementation**: `rank_bm25` Python library
```python
from rank_bm25 import BM25Okapi
import nltk

# Tokenize passages
tokenized_passages = [nltk.word_tokenize(p.lower()) for p in passages]
bm25 = BM25Okapi(tokenized_passages)

# Retrieve top-k passages per question
tokenized_query = nltk.word_tokenize(question.lower())
bm25_scores = bm25.get_scores(tokenized_query)  # Shape: (num_passages,)
top_k_indices = np.argsort(bm25_scores)[::-1][:k]
```

**Hyperparameters**:
- `k1=1.5`, `b=0.75` (BM25 standard parameters)
- Top-k retrieval: k=10 passages per question

#### Contriever Configuration
**Model**: `facebook/contriever-msmarco` (pretrained on MSMARCO, from HuggingFace)

```python
from transformers import AutoTokenizer, AutoModel
import torch

tokenizer = AutoTokenizer.from_pretrained("facebook/contriever-msmarco")
model = AutoModel.from_pretrained("facebook/contriever-msmarco").cuda()
model.eval()

# Encode query and passages
with torch.no_grad():
    query_inputs = tokenizer(question, return_tensors='pt', padding=True, truncation=True, max_length=512).to('cuda')
    query_emb = model(**query_inputs).last_hidden_state[:, 0, :]  # CLS token embedding
    
    passage_inputs = tokenizer(passages, return_tensors='pt', padding=True, truncation=True, max_length=512).to('cuda')
    passage_embs = model(**passage_inputs).last_hidden_state[:, 0, :]  # (num_passages, hidden_dim)

# Compute cosine similarity scores
contriever_scores = torch.matmul(query_emb, passage_embs.T).squeeze().cpu().numpy()  # (num_passages,)
top_k_indices = np.argsort(contriever_scores)[::-1][:k]
```

**Hyperparameters**:
- Max sequence length: 512 tokens (Contriever paper standard)
- Top-k retrieval: k=10 passages per question
- Batch size: 64 passages per forward pass (memory-efficient)

### Retrieval Corpus Construction
For each LongBench question:
1. Split `context` field into passages (boundaries marked by "\n\n")
2. Index all passages (typically 10-30 passages per question context)
3. Retrieve top-10 passages using both BM25 and Contriever
4. Store retrieval scores for correlation analysis

---

## Model Configuration

### Base Model: Llama-2-7B-Chat
**Rationale**: 
- Standard decoder-only architecture (matches H2O baseline experiments)
- 7B size fits single GPU for attention extraction (A100 40GB)
- Pre-trained chat model handles QA task without finetuning
- HuggingFace checkpoint: `meta-llama/Llama-2-7b-chat-hf`

**Context Window**: 8192 tokens (standard Llama-2 limit)

**Generation Hyperparameters**:
```python
generation_config = {
    "max_new_tokens": 128,  # Short answer generation (QA tasks produce <50 token answers)
    "temperature": 0.7,
    "top_p": 0.9,
    "do_sample": False,  # Greedy decoding for reproducibility
    "output_attentions": True  # CRITICAL: Enable attention weight return
}
```

### Attention Extraction Setup
**Hook Installation** (PyTorch forward hooks):
```python
import torch
from torch import nn

class AttentionCollector:
    def __init__(self):
        self.attentions = []  # Store attention weights per layer
        
    def hook_fn(self, module, input, output):
        # output[1] contains attention weights when output_attentions=True
        # Shape: (batch_size, num_heads, seq_len, seq_len)
        attn_weights = output[1].detach().cpu()
        self.attentions.append(attn_weights)
        
    def clear(self):
        self.attentions = []

# Install hook on last decoder layer (layer -1)
# Research shows last layer attention most predictive of generation decisions
attention_collector = AttentionCollector()
model.model.layers[-1].self_attn.register_forward_hook(attention_collector.hook_fn)

# Generate answer
with torch.no_grad():
    outputs = model.generate(input_ids, attention_mask=attention_mask, **generation_config)

# Extract attention weights
# Shape: (num_generated_tokens, num_heads, total_seq_len, total_seq_len)
last_layer_attentions = attention_collector.attentions
```

**Attention Weight Processing**:
1. Extract attention from generated answer tokens → all context tokens
2. Average over attention heads: `attn_avg = attn_weights.mean(dim=1)`  # (num_generated_tokens, total_seq_len)
3. Aggregate over generated tokens: `attn_per_context_token = attn_avg.sum(dim=0)`  # (total_seq_len,)
4. Map context token positions → passage IDs (track passage boundaries during tokenization)
5. Sum attention weights per passage: `passage_attention[passage_id] = attn_per_context_token[passage_start:passage_end].sum()`

---

## Baseline Experiments

### Baseline 1: Random Retrieval Scores (Null Model)
**Purpose**: Establish floor correlation (should be ~0 if attention is non-random)

**Method**: Shuffle retrieval scores randomly, compute Spearman ρ with attention weights

**Expected**: ρ ≈ 0 (random baseline)

### Baseline 2: Uniform Attention (Sanity Check)
**Purpose**: Verify attention extraction correctness

**Method**: Generate answers with uniform attention mask (all context tokens equal weight), compute correlation

**Expected**: ρ ≈ 0 (no structure in attention)

---

## Evaluation Metrics

### Primary Metric: Spearman Rank Correlation (ρ)
**Formula**: 
```
ρ = 1 - (6 Σ d_i^2) / (n(n^2 - 1))
```
where `d_i` is rank difference between retrieval score and attention weight for passage `i`

**Computation** (per question):
```python
from scipy.stats import spearmanr

# Inputs:
# retrieval_scores: (num_passages,) - BM25 or Contriever scores
# passage_attentions: (num_passages,) - Summed attention weights per passage

rho, p_value = spearmanr(retrieval_scores, passage_attentions)
```

**Aggregation**: 
- Report mean ρ across all questions
- Report 95% confidence interval (bootstrapped over questions)
- Report per-stratum ρ (by retriever type, query complexity, answer correctness)

### Secondary Metrics

**Query-Token Attention Concentration** (for H-M3 support):
```python
# Query tokens: first `len(query_tokens)` positions in context
# Total context tokens: sum of query + passage tokens

query_attn_ratio = passage_attention[0:len(query_tokens)].sum() / passage_attention.sum()
```

**Expected**: Simple queries → higher `query_attn_ratio` (LLM anchors to query keywords)

**Answer Accuracy** (for correctness stratification):
```python
from nltk.metrics import f1_score

# Exact match
exact_match = (predicted_answer.strip().lower() in [a.strip().lower() for a in ground_truth_answers])

# Token-level F1
f1 = f1_score(set(ground_truth_answer.split()), set(predicted_answer.split()))

# Label: Correct if exact_match OR f1 > 0.5
```

---

## Implementation Plan

### Epic Task Breakdown (for Phase 3)

**Epic 1: Data Preparation** (~8 subtasks)
1. Download LongBench dataset (`hotpotqa`, `2wikimqa`, `musique`)
2. Implement passage segmentation (parse `context` field on "\n\n")
3. Implement query complexity labeling (word count + spaCy NER entity density)
4. Implement BM25 retrieval (rank_bm25 integration)
5. Implement Contriever retrieval (HuggingFace model loading + embedding)
6. Store retrieval results (passage IDs, BM25 scores, Contriever scores per question)
7. Validate data pipeline (unit tests: passage count, score ranges, no duplicates)
8. Cache processed dataset (pickle format for fast loading)

**Epic 2: Model Setup & Attention Extraction** (~6 subtasks)
1. Load Llama-2-7B-Chat model (HuggingFace Transformers)
2. Implement AttentionCollector hook class
3. Register hooks on model.layers[-1].self_attn
4. Implement attention weight aggregation (average heads, sum over generated tokens)
5. Implement passage-level attention mapping (token positions → passage IDs)
6. Unit test: verify attention shape, non-zero values, passage boundary correctness

**Epic 3: Experiment Execution** (~5 subtasks)
1. Implement question batching (batch size 1 for attention extraction stability)
2. Run generation loop (600 questions, ~2 GPU-hours estimated)
3. Save attention outputs per question (NumPy format)
4. Implement answer correctness labeling (exact match + F1 > 0.5)
5. Checkpoint intermediate results every 100 questions (resume capability)

**Epic 4: Correlation Analysis & Reporting** (~6 subtasks)
1. Implement Spearman correlation computation (scipy.stats.spearmanr)
2. Compute per-question ρ (BM25 vs attention, Contriever vs attention)
3. Stratified analysis (by retriever type, query complexity, answer correctness)
4. Bootstrap confidence intervals (1000 resamples)
5. Generate correlation scatter plots (retrieval score vs attention weight)
6. Write validation report (02d_validation_h-e1.md)

**Epic 5: Failsafe & Baseline Validation** (~3 subtasks)
1. Implement random retrieval baseline (shuffle scores, compute ρ)
2. Implement uniform attention baseline (flat attention weights, compute ρ)
3. Statistical significance test (t-test: observed ρ vs random baseline)

**Total Tasks**: 5 epics, 28 subtasks

---

## Compute Budget

### GPU Requirements
- **Hardware**: 1x A100 40GB GPU
- **Model Memory**: Llama-2-7B in FP16 (~14GB VRAM)
- **Attention Storage**: ~500MB per 100 questions (attention weights + metadata)

### Time Estimates
- **Data Preparation**: 30 minutes (retrieval indexing + scoring)
- **Attention Extraction**: 2 GPU-hours (600 questions × 12 seconds/question average)
- **Correlation Analysis**: 10 minutes (CPU-bound Spearman computation)

**Total Wall-Clock Time**: ~2.5 hours (matches 2 GPU-hour budget from Phase 2B)

### Storage
- Preprocessed dataset: ~100MB (600 questions + passages + retrieval scores)
- Attention weights: ~3GB (600 questions × 5MB/question average)
- Final results: ~10MB (correlation matrices + plots)

---

## Risk Analysis

### High-Risk Scenarios

**Risk 1: Correlation Below Threshold (ρ ≤ 0.3)**
- **Likelihood**: Medium (BM25 lexical scores might misalign with semantic reasoning)
- **Impact**: Critical (invalidates provenance hypothesis → Phase 0 routing)
- **Mitigation**: Dual-retriever validation (if Contriever shows ρ > 0.3 but BM25 fails, pivot to semantic-only metadata)
- **Fallback**: If both retrievers fail → Phase 0 (fundamental assumption broken)

**Risk 2: Attention Extraction Bugs**
- **Likelihood**: Low (well-documented PyTorch hook API + Flash Attention examples)
- **Impact**: High (garbage correlation results)
- **Mitigation**: 
  - Unit test: verify attention shape matches (num_generated_tokens, num_heads, seq_len, seq_len)
  - Sanity check: uniform attention baseline should yield ρ ≈ 0
  - Visual inspection: plot attention heatmaps for 5 sample questions
- **Fallback**: If hook API changes in PyTorch version → use `output_attentions=True` direct output (slower but more stable)

**Risk 3: LongBench Context Parsing Errors**
- **Likelihood**: Medium (passage boundaries not explicitly marked in LongBench format)
- **Impact**: Medium (incorrect passage-level attention aggregation → biased correlation)
- **Mitigation**: 
  - Manual inspection: verify passage count matches expected for 10 sample questions
  - Cross-check: compare parsed passages against LongBench source code (https://github.com/THUDM/LongBench)
- **Fallback**: Use character-based passage boundaries if "\n\n" split fails (count characters, split at 500-character windows)

### Medium-Risk Scenarios

**Risk 4: Answer Correctness Confound**
- **Likelihood**: Medium (attention might only align with retrieval scores when answer is correct)
- **Impact**: Medium (limits generalizability of correlation, but doesn't invalidate hypothesis)
- **Mitigation**: Stratified analysis by answer correctness (report ρ for correct vs incorrect subsets)
- **Interpretation**: If ρ > 0.3 only for correct answers → attention alignment is conditional on reasoning success (still validates provenance metadata utility)

**Risk 5: Compute Budget Overrun**
- **Likelihood**: Low (600 questions × 12 seconds/question = 2 hours, well below 3-hour buffer)
- **Impact**: Low (delayed results, no scientific impact)
- **Mitigation**: Checkpoint intermediate results every 100 questions (resume from checkpoint if interrupted)

---

## Expected Outcomes

### Success Case (ρ > 0.3)
**Interpretation**: Retrieval relevance scores moderately predict attention patterns during answer generation. This validates the foundational assumption of provenance-aware KV cache eviction.

**Next Steps**: 
- Proceed to H-M1 (Pilot 2: tiered eviction single-hop validation)
- Use correlation stratification results (simple vs complex queries) to inform adaptive tiering in H-M3
- If Contriever outperforms BM25 (higher ρ), prioritize semantic retrieval scores in Phase 3 implementation

### Failure Case (ρ ≤ 0.3)
**Interpretation**: Retrieval scores do not align with LLM attention patterns. Provenance metadata is unreliable for predicting cache utility.

**Routing Decision**: Phase 0 (fundamental assumption broken)

**Salvage Analysis**: 
- Compute correlation separately for high-relevance passages (top-3 retrieved) vs low-relevance passages (bottom-7 retrieved) → might reveal non-linear relationship
- Qualitative failure analysis: manually inspect 10 questions where ρ is negative → identify systematic misalignment patterns (e.g., LLM ignores retrieved passages and uses memorized knowledge)

### Partial Success (ρ > 0.3 for one retriever only)
**Interpretation**: Correlation is retriever-dependent. Semantic retrieval (Contriever) might align better with semantic reasoning than lexical retrieval (BM25).

**Adaptation**: Pivot provenance hypothesis to use only semantic retrieval scores (still novel, since H2O uses no retrieval metadata)

**Phase 2A-Dialogue Modification**: Revise main hypothesis to explicitly state "semantic retrieval scores" instead of "retrieval scores (BM25 + semantic)"

---

## Validation Report Template

After experiment execution, populate:

**File**: `02d_validation_h-e1.md`

**Sections**:
1. **Executive Summary**: ρ values (BM25, Contriever), pass/fail decision
2. **Correlation Results Table**: Mean ρ, 95% CI, stratified by retriever/query complexity/correctness
3. **Scatter Plots**: Retrieval score vs attention weight (per-passage, 6 representative questions)
4. **Baseline Comparisons**: Observed ρ vs random baseline ρ (statistical significance)
5. **Failure Analysis** (if applicable): Questions with ρ < 0.1, qualitative inspection
6. **Routing Decision**: PASS to H-M1 or FAIL to Phase 0
7. **Archon Task Update**: Mark task 8e5db332-77b0-4e63-816f-99dac9f2fbeb as "completed"

---

## Code Repository Structure (Preview for Phase 3)

```
h-e1-attention-correlation/
├── data/
│   ├── longbench_raw/          # Downloaded from HuggingFace
│   ├── preprocessed/            # Passage-segmented + retrieval scores
│   └── cache/                   # Pickle cached datasets
├── src/
│   ├── data_prep.py             # Epic 1: LongBench preprocessing + retrieval
│   ├── attention_extractor.py   # Epic 2: AttentionCollector + hook setup
│   ├── experiment_runner.py     # Epic 3: Generation loop + checkpointing
│   ├── correlation_analysis.py  # Epic 4: Spearman computation + plots
│   └── baselines.py             # Epic 5: Random + uniform baselines
├── configs/
│   ├── llama2_7b.yaml           # Model config (HF checkpoint, device)
│   ├── retrieval.yaml           # BM25/Contriever hyperparameters
│   └── experiment.yaml          # Sample size, batch size, checkpoint frequency
├── outputs/
│   ├── attentions/              # NumPy attention weights per question
│   ├── results/                 # Correlation matrices + stratified tables
│   └── plots/                   # Scatter plots + heatmaps
├── tests/
│   ├── test_passage_segmentation.py
│   ├── test_attention_shape.py
│   └── test_correlation.py
├── requirements.txt             # transformers, torch, rank_bm25, scipy, spacy, nltk
└── README.md                    # Experiment overview + usage
```

---

## Archon Integration

**Project ID**: dd500899-44fd-44d5-b7ea-7d7ec8f5c571  
**Task ID**: 8e5db332-77b0-4e63-816f-99dac9f2fbeb  
**Status**: DESIGN_COMPLETED (Phase 2C output)

**Next Phase Actions**:
1. Phase 3 (Implementation Planning): 
   - Generate PRD for h-e1 attention correlation experiment
   - Architecture document: data pipeline, attention extraction, correlation analysis
   - Decompose 5 epics into Archon subtasks (28 tasks total)
2. Phase 4 (PoC Validation):
   - Implement 28 subtasks sequentially
   - Execute experiment (2.5 GPU-hours)
   - Generate validation report (02d_validation_h-e1.md)
   - Update checkpoint with gate decision (PASS/FAIL)

---

## References

### Key Papers
1. **H2O** (Zhang et al., NeurIPS 2023): Heavy-Hitter Oracle attention-based KV cache eviction
2. **LongBench** (Bai et al., 2023): Multi-task long-context evaluation benchmark (https://arxiv.org/abs/2308.14508)
3. **Contriever** (Izacard et al., 2022): Unsupervised dense retrieval with contrastive learning (https://arxiv.org/abs/2112.09118)
4. **DPR** (Karpukhin et al., 2020): Dense Passage Retrieval for Open-Domain QA (https://arxiv.org/abs/2004.04906)
5. **Lost in the Middle** (Liu et al., 2023): LLM attention concentration at beginning/end of context (https://arxiv.org/abs/2307.03172)

### Code Resources
1. LongBench dataset: https://huggingface.co/datasets/THUDM/LongBench
2. Contriever model: https://huggingface.co/facebook/contriever-msmarco
3. Llama-2-7B-Chat: https://huggingface.co/meta-llama/Llama-2-7b-chat-hf
4. PyTorch attention extraction gist: https://gist.github.com/airalcorn2/50ec06517ce96ecc143503e21fa6cb91
5. rank_bm25 library: https://pypi.org/project/rank-bm25/

### Archon Knowledge Base Searches
- Attention weight extraction: PyTorch scaled_dot_product_attention, Flash Attention KV cache
- Spearman correlation: scipy.stats evaluation metrics
- LongBench evaluation: Multi-doc QA dataset structure, eval scripts

---

**Document Status**: COMPLETED  
**Ready for Phase 3**: YES  
**Estimated Implementation Complexity**: Tier 2 (28 subtasks, 2.5 GPU-hours, well-scoped)
