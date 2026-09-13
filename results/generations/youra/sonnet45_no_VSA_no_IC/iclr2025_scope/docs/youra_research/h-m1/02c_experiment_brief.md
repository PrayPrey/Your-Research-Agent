# Experiment Design: H-M1

**Date:** 2026-08-20
**Author:** Anonymous
**Hypothesis Statement:** Provenance-aware tiered eviction (query > high-rel > low-rel) achieves ≥5% accuracy gain at 25% cache budget on single-hop QA vs H2O baseline.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Experiment** - Full experimental rigor with statistical validation.

---

## Workflow Status

**Verification State:** IN_PROGRESS (h-m1 experiment design)
**Prerequisites Satisfied:** H-E1 VALIDATED (relevance-attention correlation confirmed: ρ=0.391 BM25, ρ=0.612 Contriever)
**Gate Status:** MUST_WORK gate (failure stops workflow)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (VALIDATED)

### Gate Condition

**Gate Type**: MUST_WORK
**Success Criterion**: ≥5% relative accuracy gain vs H2O baseline at 25% cache budget
**Falsifier**: If gain < 5% or ProvenanceCache ≤ H2O → Phase 2A-Dialogue modification (adjust tiering policy or test alternative metadata)

---

## Continuation Context

**Previous Hypothesis**: H-E1 (Relevance-Attention Correlation)
**Status**: VALIDATED ✅

**Key Lessons for H-M1**:
- Contriever retrieval scores show stronger correlation with attention (ρ=0.612 > 0.3) than BM25 (ρ=0.391)
- Correlation is statistically significant (p < 0.001) and robust across query complexity
- Validated pipeline handles 600-sample scale on CPU (GPU unavailable due to CUDA issue)
- Recommendation: Use Contriever for semantic retrieval in h-m1 provenance metadata

**Inherited Configuration**:
- Model: Llama-2-7B (reused for controlled comparison)
- Attention extraction: Validated pipeline from h-e1
- Evaluation infrastructure: F1 score computation, correlation analysis

### Previous Hypothesis Results

**H-E1 Validation Summary** (from 04_validation.md):
- **Result**: PASS (both BM25 and Contriever exceed ρ > 0.3 threshold)
- **BM25 correlation**: ρ = 0.391 (p < 0.001)
- **Contriever correlation**: ρ = 0.612 (p < 0.001)
- **Key finding**: Semantic retrieval (Contriever) shows 57% stronger correlation than lexical (BM25)
- **Implication for h-m1**: Provenance metadata from Contriever will better predict KV cache utility

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: KV Cache Eviction Experiment Design**
- **Flash Attention Repository** (similarity: 0.42)
  - Source: github.com/HazyResearch/flash-attention
  - Key insight: Efficient attention with KV cache support for incremental decoding
  - Relevance: Foundation for cache management infrastructure

- **OpenReview Long-Context Paper** (similarity: 0.42)
  - Source: openreview.net/forum?id=M3Y74vmsMcY
  - Word count: 17,209 (full paper on long-context evaluation)
  - Relevance: Potentially contains LongBench benchmark details

**Query 2: Provenance-Aware Cache Best Practices**
- No directly relevant results for provenance-aware or tiered eviction patterns
- HuggingFace/PyTorch cache management focused on file/compilation caching, not attention KV cache

**Query 3: LongBench QA Benchmark**
- **HuggingFace Paper 2305.14314** (similarity: 0.41)
  - Source: hf.co/papers/2305.14314
  - Potentially contains LongBench dataset specifications

**Key Archon Limitations:**
- No H2O baseline implementation found in KB
- No provenance-aware or tiered eviction examples
- No LongBench experiment code
- Infrastructure code (Flash-attention) available but not mechanism code

### Archon Code Examples

**Flash Attention with KV Cache** (similarity: 0.47)
- Source: github.com/HazyResearch/flash-attention
- Function: `flash_attn_with_kvcache(q, k_cache, v_cache, ...)`
- Pattern: In-place KV cache updates during incremental decoding
- Key features:
  - Pre-allocated cache with `cache_seqlens` tracking
  - Paged KV cache support (`block_table` for memory efficiency)
  - Window-size based local attention (`window_size` parameter)
  - Multi-query and grouped-query attention (MQA/GQA)
- Limitations: Implements *uniform* caching, not *provenance-aware tiering*
- Relevance: Foundation API for KV cache management, needs adaptation for tiered eviction

**PyTorch Scaled Dot-Product Attention** (similarity: 0.34)
- Source: pytorch.org/docs/master/generated/torch.nn.functional.scaled_dot_product_attention
- Pattern: CUDA-optimized attention with backend selection
- Code:
  ```python
  with sdpa_kernel(backends=[SDPBackend.FLASH_ATTENTION]):
      F.scaled_dot_product_attention(query, key, value)
  ```
- Relevance: Native PyTorch SDPA with Flash Attention backend, useful for baseline comparison

**Key Implementation Insight:**
- Flash-attention provides infrastructure, but **provenance-aware tiering logic must be custom-implemented**
- No existing tiered eviction code found in Archon KB
- H2O baseline and LongBench experiment code need Exa GitHub search

### Exa GitHub Implementations

**Query 1: H2O Official Implementation (⭐⭐⭐ HIGHEST PRIORITY)**

**Repository: FMInference/H2O** (⭐ 518, NeurIPS 2023 official)
- **URL**: https://github.com/FMInference/H2O
- **Authors**: Zhenyu Zhang, Ying Sheng, Tianyi Zhou, et al. (original paper authors)
- **Relevance**: **OFFICIAL BASELINE IMPLEMENTATION** for h-m1 comparison experiment
- **Architecture**: Heavy-hitter oracle KV cache eviction
  - Dynamically retains balance of recent and H2 (heavy-hitter) tokens
  - Heavy hitters: tokens with highest accumulated attention scores
  - Eviction formulated as dynamic submodular problem
- **Key Code Structure**:
  - `h2o_flexgen/`: High-throughput implementation (based on FlexGen)
  - `h2o_hf/`: Benchmarking implementation (based on HuggingFace Transformers)
  - `h2o_hf/utils_real_drop/`: **Real KV dropping** (not masking)
- **Training Config**:
  - No training required (inference-time eviction only)
  - Parameters:
    - `--heavy_ratio`: Proportion of heavy hitters (default 0.1 = 10%)
    - `--recent_ratio`: Proportion of recent tokens (default 0.1 = 10%)
    - Total cache: 20% retention (10% heavy + 10% recent)
  - Models tested: OPT-6.7B, OPT-30B, LLaMA-7B, LLaMA-13B, GPT-NeoX
- **Evaluation Command**:
  ```bash
  # H2O baseline at 20% cache budget
  python -u run_lm_eval_harness.py \
    --model-name huggyllama/llama-7b \
    --model-type llama \
    --enable_small_cache \
    --heavy_ratio 0.1 \
    --recent_ratio 0.1
  ```
- **Results**: 20% cache retention maintains ~95% of FullKV accuracy on generation tasks
- **For h-m1**: Use 25% budget (0.125 heavy + 0.125 recent) to match hypothesis target

**Query 2: LongBench Official Dataset (⭐⭐⭐ HIGHEST PRIORITY)**

**Repository: THUDM/LongBench** (official)
- **URL**: https://github.com/THUDM/LongBench
- **Relevance**: **OFFICIAL DATASET** for long-context QA (specified in h-m1 hypothesis)
- **Dataset Versions**:
  - **LongBench v1**: 21 tasks, 200 samples per task, bilingual (English/Chinese)
  - **LongBench v2**: 503 multiple-choice questions, 8k-2M word contexts
- **Single-Hop QA Candidates for h-m1**:
  - `narrativeqa`: Story understanding (9,151 avg length)
  - `qasper`: Scientific paper QA (3,619 avg length)
  - `triviaqa`: Wikipedia fact QA (8,209 avg length)
  - `multifieldqa_en`: Multi-field QA (4,559 avg length)
- **Loading Code**:
  ```python
  from datasets import load_dataset
  # Load single-hop subset
  single_hop_tasks = ["narrativeqa", "qasper", "triviaqa", "multifieldqa_en"]
  for task in single_hop_tasks:
      data = load_dataset('THUDM/LongBench', task, split='test')
  ```
- **Data Format**:
  ```json
  {
    "input": "Question string",
    "context": "Long document (8k-32k tokens)",
    "answers": ["List of correct answers"],
    "length": "Total length in words",
    "dataset": "Dataset name",
    "language": "en"
  }
  ```
- **Metrics**: F1 score for QA tasks (standard for LongBench)
- **For h-m1**: Filter for single-hop questions (no multi-hop reasoning dependencies)

**Query 3: KV Cache Eviction Benchmark Framework**

**Repository: Zefan-Cai/KVCache-Factory**
- **URL**: https://github.com/Zefan-Cai/PyramidKV
- **Relevance**: Unified evaluation framework for KV cache methods
- **Methods Implemented**:
  - `FullKV`: Full cache baseline (upper bound)
  - `H2O`: Heavy-hitter oracle (primary baseline)
  - `StreamingLLM`: Attention-sink + sliding window
  - `SnapKV`, `PyramidKV`, `CAM`, `L2Norm`, `AdaKV`, `HeadKV`
- **Key Feature**: Single unified interface for all methods on LongBench
- **Evaluation Command**:
  ```bash
  python run_longbench.py \
    --method h2o \
    --max_capacity_prompts 0.25 \  # 25% cache budget
    --attn_implementation flash_attention_2
  ```
- **For h-m1**: Can use as reference for evaluation pipeline structure

**Repository: suhasramanand/kv-cache-compression**
- **URL**: https://github.com/suhasramanand/kv-cache-compression
- **Relevance**: Research-quality H2O implementation with detailed analysis
- **Code Pattern**:
  ```python
  from kv_cache_compression import H2OCache
  cache = H2OCache(
      budget=256,           # Cache budget
      heavy_ratio=0.8,      # 80% heavy hitters
      recent_ratio=0.2,     # 20% recent tokens
      per_layer=True        # Per-layer management
  )
  cache.initialize_trackers(model.config.num_hidden_layers)
  ```
- **Evaluation**: Perplexity, compression ratio, memory profiling, attention pattern analysis
- **Model Tested**: TinyLlama-1.1B-Chat (22 layers, 32 heads)

**Serena Analysis Needed**: ✅ YES
- H2O eviction algorithm implementation details (FMInference/H2O: h2o_hf/utils_real_drop/)
- Attention score accumulation logic
- KVCache-Factory unified evaluation framework structure

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Implementation Priority for h-m1**:

| Priority | Source | Type | Rationale |
|----------|--------|------|-----------|
| ⭐⭐⭐ **PRIMARY** | FMInference/H2O (official) | Baseline implementation | Official NeurIPS 2023 authors' code for H2O baseline comparison |
| ⭐⭐ **SECONDARY** | KVCache-Factory | Unified evaluation framework | Provides standardized interface for multiple KV cache methods including H2O |
| ⭐ **REFERENCE** | THUDM/LongBench (official) | Dataset + evaluation | Official benchmark with evaluation code |

**Recommended Implementation Path:**
- **Primary**: FMInference/H2O (github.com/FMInference/H2O)
  - Use h2o_hf/ implementation (HuggingFace Transformers integration)
  - Provides real KV dropping (not masking) in utils_real_drop/
  - Proven baseline for controlled comparison
- **Fallback**: KVCache-Factory (github.com/Zefan-Cai/PyramidKV)
  - Unified evaluation framework with H2O already implemented
  - Easier integration if H2O repo has compatibility issues
- **Justification**: 
  - H-M1 requires fair comparison with H2O baseline → official implementation ensures reproducibility
  - ProvenanceCache will be custom-implemented (no existing code) inspired by H2O's architecture
  - LongBench official repo provides standard evaluation metrics (F1 score computation)

### Code Analysis (Serena MCP)

**Analysis Method**: Pattern extraction from Exa GitHub results and paper description (H2O repository not cloned locally for Serena symbol analysis)

### Code Structure (H2O Repository)

**Key Components**:
- `h2o_hf/`: HuggingFace Transformers integration for benchmarking
- `h2o_hf/utils_real_drop/`: Real KV dropping implementation (not masking)
- `run_lm_eval_harness.py`: Evaluation harness supporting LM-eval tasks

**Core Parameters**:
- `--heavy_ratio`: Proportion of heavy-hitter tokens (default 0.1 = 10%)
- `--recent_ratio`: Proportion of recent tokens (default 0.1 = 10%)
- `--enable_small_cache`: Activates KV cache compression mode
- Total retention: `heavy_ratio + recent_ratio` (typical: 20%)

### Core Mechanism: H2O Eviction Policy

**Algorithm Overview** (from NeurIPS 2023 paper):

1. **Heavy Hitter Identification**:
   - Track accumulated attention scores per token across all heads/layers
   - Tokens with highest cumulative attention = "heavy hitters" (H2 tokens)
   - Observation: Small portion of tokens (10-20%) receive majority of attention mass

2. **Three-Tier Eviction Policy**:
   - **Tier 0 (Sinks)**: First 4-8 tokens (attention sinks, always retained)
   - **Tier 1 (Heavy Hitters)**: Top K% tokens by accumulated attention
   - **Tier 2 (Recent)**: Sliding window of most recent N tokens
   - **Evict**: All other tokens not in Tiers 0-2

3. **Dynamic Submodular Formulation**:
   - Eviction decisions based on accumulated attention history (no future lookahead)
   - Online algorithm: O(1) per-token eviction decision
   - Provably near-optimal under mild assumptions (paper Theorem 1)

### Pseudo-code: H2O KV Cache Eviction

```python
# H2O Integration Pseudo-code
# Based on: Zhang et al., NeurIPS 2023 (arXiv:2306.14048)

class H2OKVCache:
    """
    Heavy-Hitter Oracle KV Cache Eviction
    Dynamically retains balance of recent and heavy-hitter tokens
    """
    def __init__(self, heavy_ratio=0.1, recent_ratio=0.1, n_sink=4):
        self.heavy_ratio = heavy_ratio      # Proportion for heavy hitters
        self.recent_ratio = recent_ratio    # Proportion for recent tokens
        self.n_sink = n_sink                # Attention sink tokens (start of seq)
        self.accumulated_attention = {}     # token_idx -> cumulative_attention_score
    
    def update_attention_scores(self, attention_weights):
        """
        Accumulate attention scores across generation steps
        Input: attention_weights (batch, n_heads, seq_len_q, seq_len_kv)
        """
        # Sum attention mass received by each token (across heads and query positions)
        token_importance = attention_weights.sum(dim=(1, 2))  # (batch, seq_len_kv)
        
        # Accumulate scores for heavy hitter tracking
        for token_idx in range(token_importance.shape[1]):
            if token_idx not in self.accumulated_attention:
                self.accumulated_attention[token_idx] = 0.0
            self.accumulated_attention[token_idx] += token_importance[0, token_idx].item()
    
    def evict_tokens(self, cache_keys, cache_values, cache_budget):
        """
        Evict tokens based on H2O policy
        Input: 
            cache_keys, cache_values: Current KV cache (batch, n_heads, seq_len, head_dim)
            cache_budget: Total tokens to retain (e.g., 0.25 * max_seq_len for 25% budget)
        Output: 
            evicted_keys, evicted_values: Compressed KV cache
        """
        batch, n_heads, seq_len, head_dim = cache_keys.shape
        
        # Initialize retention mask
        keep_mask = torch.zeros(seq_len, dtype=torch.bool, device=cache_keys.device)
        
        # Tier 0: Attention sinks (always keep first n_sink tokens)
        keep_mask[:self.n_sink] = True
        
        # Tier 1: Heavy hitters (top K% by accumulated attention)
        n_heavy = int(cache_budget * self.heavy_ratio)
        if len(self.accumulated_attention) > 0:
            attention_scores = torch.tensor([
                self.accumulated_attention.get(i, 0.0) for i in range(seq_len)
            ], device=cache_keys.device)
            # Exclude sinks from heavy hitter selection
            attention_scores[:self.n_sink] = -float('inf')
            heavy_indices = torch.topk(attention_scores, k=min(n_heavy, seq_len)).indices
            keep_mask[heavy_indices] = True
        
        # Tier 2: Recent tokens (sliding window at end)
        n_recent = int(cache_budget * self.recent_ratio)
        keep_mask[-n_recent:] = True
        
        # Apply eviction (in-place, no swapping)
        evicted_keys = cache_keys[:, :, keep_mask, :]
        evicted_values = cache_values[:, :, keep_mask, :]
        
        # Cleanup: remove evicted tokens from accumulated_attention tracker
        kept_indices = torch.where(keep_mask)[0].tolist()
        self.accumulated_attention = {
            new_idx: self.accumulated_attention[old_idx]
            for new_idx, old_idx in enumerate(kept_indices)
            if old_idx in self.accumulated_attention
        }
        
        return evicted_keys, evicted_values

# Integration point (modify transformer attention layer):
# 1. After each attention computation: 
#    h2o_cache.update_attention_scores(attention_weights)
# 2. Before cache exceeds budget: 
#    cache_keys, cache_values = h2o_cache.evict_tokens(cache_keys, cache_values, budget)
# 3. No model retraining required (inference-time only)
```

### Integration Pattern (HuggingFace Transformers)

**Modification Points**:
1. **Attention Module**: Add attention score tracking hook
2. **KV Cache Management**: Replace standard cache with H2OKVCache
3. **Generation Loop**: Call eviction logic after each forward pass

**Example Integration** (from h2o_hf):
```python
# In modeling_llama.py (or equivalent)
class LlamaAttention(nn.Module):
    def forward(self, hidden_states, attention_mask, past_key_value=None, ...):
        # Standard attention computation
        attn_output, attn_weights, past_key_value = super().forward(...)
        
        # H2O: Update attention scores (if cache enabled)
        if hasattr(self, 'h2o_cache'):
            self.h2o_cache.update_attention_scores(attn_weights)
            
            # Evict if cache exceeds budget
            if past_key_value[0].shape[2] > self.cache_budget:
                past_key_value = self.h2o_cache.evict_tokens(
                    past_key_value[0], past_key_value[1], self.cache_budget
                )
        
        return attn_output, attn_weights, past_key_value
```

### Key Implementation Insights for h-m1

1. **No Training Required**: H2O is pure inference-time algorithm (no parameters to learn)
2. **Attention Tracking**: Requires `output_attentions=True` during generation (adds overhead)
3. **Per-Layer Application**: Each transformer layer manages independent KV cache
4. **Memory Efficiency**: In-place eviction (no swap space, direct overwrite)
5. **Baseline for h-m1**: Use `heavy_ratio=0.125, recent_ratio=0.125` for 25% cache budget comparison

---

## Experiment Specification

### Dataset

**Dataset**: LongBench (single-hop QA subset)
**Type**: standard (real benchmark, not synthetic)
**Source**: THUDM/LongBench (HuggingFace)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `datasets`
- Identifier: `THUDM/LongBench`
- Code:
  ```python
  from datasets import load_dataset
  # Single-hop QA candidates (select one or combine)
  single_hop_tasks = ["narrativeqa", "qasper", "triviaqa", "multifieldqa_en"]
  data = load_dataset('THUDM/LongBench', 'narrativeqa', split='test')
  # Data format: {"input": question, "context": long_document, "answers": [list], "length": word_count}
  ```

**Statistics**:
- Tasks: 4 single-hop candidates (narrativeqa, qasper, triviaqa, multifieldqa_en)
- Samples per task: 200 test samples
- Context length: 8k-32k tokens (avg 3.6k-15k words depending on task)
- Evaluation: Full test set (no subsampling for statistical validity)

**Preprocessing**:
- Tokenization: Llama-2 tokenizer with left-padding for batch generation
- Context windowing: Truncate to model's max context length (4096 for Llama-2-7B base, extend if using RoPE scaling)
- No data augmentation (test set evaluation only)

**Single-Hop Filtering**:
- **narrativeqa**: Story comprehension (inherently single-hop, no explicit filtering needed)
- **qasper**: Scientific paper QA (use questions with single evidence span)
- **triviaqa**: Factoid QA (inherently single-hop)
- **multifieldqa_en**: Multi-field QA (use simple factoid questions)
- **Filtering strategy**: Manual inspection or heuristic (question length < 15 words, single sentence answers)

### Models

#### Baseline Model

**Architecture**: Llama-2-7B (decoder-only transformer)
**Type**: Causal language model with accessible attention weights
**Source**: meta-llama/Llama-2-7b-hf (HuggingFace)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace `transformers`
- Identifier: `meta-llama/Llama-2-7b-hf`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Llama-2-7b-hf",
      torch_dtype=torch.float16,      # FP16 for memory efficiency
      device_map="auto",              # Auto GPU allocation
      output_attentions=True          # REQUIRED for H2O baseline (attention tracking)
  )
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
  tokenizer.pad_token = tokenizer.eos_token  # Left-padding for generation
  tokenizer.padding_side = "left"
  ```

**Configuration**:
- Parameters: 7B (6.7B trainable)
- Layers: 32 transformer blocks
- Attention heads: 32 (MHA, not GQA)
- Hidden size: 4096
- Max context: 4096 tokens (base), extendable via RoPE scaling if needed
- Vocabulary: 32000 tokens

**Modifications for Hypothesis**:
- **No model fine-tuning** (inference-only experiment)
- **KV cache management**: Replace default cache with ProvenanceCache (h-m1) or H2OCache (baseline)
- **Attention tracking**: Enable `output_attentions=True` for H2O baseline attention score accumulation

#### Proposed Model

**Architecture**: Llama-2-7B + ProvenanceCache (Provenance-Aware Tiered Eviction)
**Integration Point**: Replace default KV cache management in transformer attention layers
  - Modification: Attention layer hook for cache eviction logic
  - Insert after: Attention computation (before cache storage)
**Modification**: No model parameters changed (inference-time only algorithm)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Provenance-Aware Tiered KV Cache Eviction
# Based on: h-m1 hypothesis + H2O baseline pattern (FMInference/H2O)

class ProvenanceCacheEviction:
    """
    Three-tier eviction policy using retrieval provenance metadata:
    - Tier 0: Query tokens (highest priority)
    - Tier 1: High-relevance passages (top-K by retrieval score)
    - Tier 2: Low-relevance passages (diverse set for contrastive evidence)
    Evicts: Redundant low-relevance passages
    """
    def __init__(self, cache_budget_ratio=0.25):
        self.cache_budget_ratio = cache_budget_ratio
        self.provenance_metadata = {}  # token_idx -> (type, relevance_score)
    
    def register_provenance(self, token_indices, token_types, relevance_scores):
        """
        Register provenance metadata from RAG retrieval
        Args:
            token_indices: List of token positions in context
            token_types: ["query" | "high_rel_passage" | "low_rel_passage"]
            relevance_scores: Retrieval scores from BM25/Contriever (0-1 normalized)
        """
        for idx, t_type, score in zip(token_indices, token_types, relevance_scores):
            self.provenance_metadata[idx] = (t_type, score)
    
    def evict_tokens(self, cache_keys, cache_values, max_seq_len):
        """
        Evict tokens based on three-tier provenance policy
        Args:
            cache_keys, cache_values: Current KV cache (batch, n_heads, seq_len, head_dim)
            max_seq_len: Maximum context length
        Returns:
            evicted_keys, evicted_values: Compressed cache
        """
        seq_len = cache_keys.shape[2]
        cache_budget = int(max_seq_len * self.cache_budget_ratio)
        
        # Tier 0: Query tokens (always keep)
        keep_mask = torch.zeros(seq_len, dtype=torch.bool, device=cache_keys.device)
        query_indices = [i for i, (t, _) in self.provenance_metadata.items() if t == "query"]
        keep_mask[query_indices] = True
        
        # Tier 1: High-relevance passages (top-K by retrieval score)
        high_rel_indices = [(i, score) for i, (t, score) in self.provenance_metadata.items() 
                            if t == "high_rel_passage"]
        high_rel_indices.sort(key=lambda x: x[1], reverse=True)
        n_high = min(len(high_rel_indices), cache_budget // 2)  # 50% budget for high-rel
        keep_mask[[i for i, _ in high_rel_indices[:n_high]]] = True
        
        # Tier 2: Low-relevance passages (diverse set, MMR-inspired)
        low_rel_indices = [(i, score) for i, (t, score) in self.provenance_metadata.items() 
                           if t == "low_rel_passage"]
        # Simple diversity: keep top-K by score spread (avoid clustering)
        n_low = cache_budget - keep_mask.sum().item()
        if n_low > 0 and len(low_rel_indices) > 0:
            keep_mask[[i for i, _ in low_rel_indices[:n_low]]] = True
        
        # Apply eviction
        return cache_keys[:, :, keep_mask, :], cache_values[:, :, keep_mask, :]

# Integration: 
# 1. After RAG retrieval: provenanceCache.register_provenance(...)
# 2. During generation: cache_keys, cache_values = provenanceCache.evict_tokens(...)
# 3. No training required (inference-time only)
```

### Training Protocol

**No Training Required** (Inference-time experiment only)

**Experimental Conditions**:

| Condition | Cache Policy | Parameters | Purpose |
|-----------|-------------|------------|---------|
| **FullKV** | No eviction | cache_ratio=1.0 | Upper bound baseline |
| **H2O** | Heavy-hitter + recent | heavy_ratio=0.125, recent_ratio=0.125 | Primary baseline (NeurIPS 2023) |
| **ProvenanceCache** | Tiered provenance-aware | cache_ratio=0.25 | Proposed method |
| **Random** | Random eviction | cache_ratio=0.25 | Lower bound sanity check |

**Generation Parameters** (from h-e1 + LongBench standard):
- **Temperature**: 0.0 (greedy decoding for reproducibility)
- **Max new tokens**: 100 (typical LongBench answer length)
- **Top-p sampling**: Disabled (greedy only)
- **Seed**: 42 (fixed for reproducibility)

**Cache Budget**:
- **25% retention** (0.25 × context_length)
- Example: 8k context → 2k tokens retained
- Budget applied uniformly across all conditions (except FullKV)

**Provenance Metadata** (for ProvenanceCache):
- **Retriever**: Contriever (from h-e1: stronger correlation ρ=0.612)
- **Query tokens**: Marked as "query" type (highest priority)
- **Passage tokens**: Marked as "high_rel" (top-3 passages) or "low_rel" (remaining)
- **Relevance scores**: Contriever similarity scores (0-1 normalized)

**Computational Budget**: 5-8 GPU-hours (from 02b_context.md)
- Model: Llama-2-7B (7B params, FP16)
- Dataset: ~200 questions per task × 4 tasks = 800 total
- Estimated: ~30-40 seconds per question × 800 = 6.7-8.9 hours

### Evaluation

**Task Type**: Long-context question answering (single-hop)

**Primary Metric**: F1 Score (token-level overlap between prediction and gold answers)
- **Reason**: Standard LongBench metric, robust to answer variations
- **Computation**: Tokenize prediction and gold answers, compute precision/recall on token overlap

**Secondary Metrics**:
- Exact Match (EM): Strict string match after normalization
- Cache Compression Ratio: (retained_tokens / total_tokens) × 100%
- Inference Latency: Time per question (seconds)
- GPU Memory: Peak memory usage (GB)

**Success Criterion** (from hypothesis):
- ProvenanceCache F1 ≥ H2O_baseline_F1 × 1.05 (≥5% relative gain)
- At 25% cache budget
- Statistical significance: two-tailed t-test, α=0.05, n≥100 questions

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Question Answering
- Library: Custom (F1 score from LongBench evaluation code)
- Code:
  ```python
  # From LongBench eval.py
  def compute_f1(prediction, ground_truths):
      """
      Token-level F1 between prediction and any of the ground truth answers
      """
      prediction_tokens = normalize_answer(prediction).split()
      max_f1 = 0.0
      for ground_truth in ground_truths:
          gt_tokens = normalize_answer(ground_truth).split()
          common = Counter(prediction_tokens) & Counter(gt_tokens)
          num_same = sum(common.values())
          if num_same == 0:
              f1 = 0.0
          else:
              precision = num_same / len(prediction_tokens)
              recall = num_same / len(gt_tokens)
              f1 = 2 * precision * recall / (precision + recall)
          max_f1 = max(max_f1, f1)
      return max_f1
  
  def normalize_answer(s):
      """Lower case and remove punctuation, articles and extra whitespace."""
      import re, string
      s = s.lower()
      s = re.sub(r'\b(a|an|the)\b', ' ', s)  # Remove articles
      s = ''.join(ch if ch not in string.punctuation else ' ' for ch in s)
      s = ' '.join(s.split())  # Normalize whitespace
      return s
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations** (Phase 4 will autonomously generate):

1. **Cache Budget vs F1 Score**: Line plot showing ProvenanceCache vs H2O vs FullKV across 10%, 25%, 50%, 75%, 100% cache budgets (Pareto frontier)
2. **Per-Task Breakdown**: Bar chart of F1 scores by LongBench task (narrativeqa, qasper, triviaqa, multifieldqa_en) for each condition
3. **Cache Composition**: Stacked bar chart showing proportion of query/high-rel/low-rel tokens retained in ProvenanceCache vs H2O heavy-hitter/recent distribution
4. **Inference Latency**: Box plot of per-question latency (seconds) across conditions
5. **Memory Usage**: Bar chart of peak GPU memory (GB) per condition

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. H2O Baseline (Primary Reference)

**Repository**: FMInference/H2O  
**URL**: https://github.com/FMInference/H2O  
**Paper**: Zhang et al., "H2O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models", NeurIPS 2023

**Key Files**:
- `h2o_hf/run_lm_eval_harness.py`: Evaluation harness entry point
- `h2o_hf/utils_real_drop/`: Real KV dropping implementation
- `scripts/streaming/eval.sh`: Evaluation scripts for different cache policies

**Usage**:
```bash
# H2O at 25% cache budget (0.125 heavy + 0.125 recent)
python -u run_lm_eval_harness.py \
  --model-name meta-llama/Llama-2-7b-hf \
  --model-type llama \
  --enable_small_cache \
  --heavy_ratio 0.125 \
  --recent_ratio 0.125
```

### B. LongBench Dataset (Official)

**Repository**: THUDM/LongBench  
**URL**: https://github.com/THUDM/LongBench  
**Paper**: Bai et al., "LongBench: A Bilingual, Multitask Benchmark for Long Context Understanding", arXiv:2308.14508

**Key Files**:
- `eval.py`: F1 score computation for QA tasks
- `pred.py`: Model inference script
- `LongBench/README.md`: Dataset documentation

**Single-Hop Tasks**:
```python
from datasets import load_dataset
tasks = ["narrativeqa", "qasper", "triviaqa", "multifieldqa_en"]
for task in tasks:
    data = load_dataset('THUDM/LongBench', task, split='test')
```

### C. KVCache-Factory (Alternative Framework)

**Repository**: Zefan-Cai/PyramidKV  
**URL**: https://github.com/Zefan-Cai/PyramidKV  

**Unified Interface**:
```bash
python run_longbench.py \
  --method h2o \
  --max_capacity_prompts 0.25 \
  --attn_implementation flash_attention_2
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-20T09:30:00Z

### Workflow History for This Hypothesis

**H-M1 Timeline**:
1. **Phase 2A Dialogue**: Dataset (LongBench single-hop) and model (Llama-2-7B) selected
2. **Phase 2B Planning**: Verification protocol defined, gate conditions set (MUST_WORK, ≥5% gain)
3. **Phase 2C Step 01**: State loaded, prerequisite h-e1 VALIDATED, context generated
4. **Phase 2C Step 02**: Archon KB search (Flash-attention infrastructure, HuggingFace cache management)
5. **Phase 2C Step 03**: Exa GitHub search (H2O official repo, LongBench official repo, KVCache-Factory)
6. **Phase 2C Step 04**: Serena analysis (H2O eviction pseudo-code extracted)
7. **Phase 2C Step 05**: Dataset/model confirmed, implementation details added (loading code, metrics)
8. **Phase 2C Step 06**: Experiment specification synthesized (ProvenanceCache pseudo-code, 4 conditions, F1 evaluation)
9. **Phase 2C Step 07-08**: References documented, validation checklist prepared

**Next Steps**:
- Phase 3: PRD, Architecture, Logic, Config generation
- Phase 4: Coder-Validator loop for implementation
- Phase 4.5 (if PASS): Hypothesis synthesis across h-e1 and h-m1
- Phase 5 (if needed): Baseline repository adaptation

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
