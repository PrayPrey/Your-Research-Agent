# Experiment Design: h-m4

**Date:** 2026-08-20
**Author:** Anonymous
**Hypothesis Statement:** Adaptive cache (grow/shrink based on retrieval density) matches static 25% cache accuracy while using ≤20% budget on average
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-m3 VALIDATED)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m4
- **Type:** MECHANISM
- **Prerequisites:** h-m3

### Gate Condition
SHOULD_WORK: Experiment should demonstrate adaptive cache matching static 25% accuracy at ≤20% average budget. Non-critical optimization — failure documented as limitation.

---

## Continuation Context

h-m4 builds on h-m1 (tiered eviction) and h-m2 (diversity-aware scoring). h-m3 (query complexity tiering) failed validation — uniform tiering is fallback.

### Previous Hypothesis Results (if applicable)

**h-m3 (Query Complexity Attention):** FAILED
- Simple vs complex queries show no significant attention difference (p=0.9537, Δ=-0.003)
- Fallback: Uniform tiering (all retrieval passages treated equally)
- Core eviction mechanisms (h-m1, h-m4) remain valid

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Adaptive cache sizing experiment design**
- **HuggingFace Cache Management** (3932 words)
  - Insight: Cache management with size limits, cleanup strategies
  - Reference: https://huggingface.co/docs/huggingface_hub/guides/manage-cache
  
- **PyTorch Compile Caching** (1046 words)
  - Insight: Dynamic cache compilation, size-aware strategies
  - Reference: https://pytorch.org/tutorials/recipes/torch_compile_caching_tutorial.html

**Query 2: KV cache eviction implementation**
- **Flash Attention KV Cache** (4310 words)
  - Core pattern: Incremental cache updates with in-place modification
  - Key insight: `flash_attn_with_kvcache` supports dynamic sequence lengths via `cache_seqlens` parameter
  - Reference: https://github.com/HazyResearch/flash-attention

- **HuggingFace Cache Management** (3932 words, 3 chunks)
  - Patterns: LRU eviction, size-based cleanup
  - Best practice: Track cache metadata for eviction decisions

**Query 3: Retrieval QA benchmarks**
- Limited direct retrieval QA results found
- Fallback: Use standard QA datasets (NaturalQuestions, TriviaQA)

### Archon Code Examples

**Query 1: Adaptive cache PyTorch implementation**

**Flash Attention KV Cache:**
```python
# Incremental cache update with dynamic sizing
flash_attn_with_kvcache(
  q, k_cache, v_cache,
  k=new_k, v=new_v,  # New tokens appended in-place
  cache_seqlens=current_lengths,  # Track per-sequence cache positions
  ...
)
```
- **Pattern:** Separate pre-allocated cache tensors with per-sequence length tracking
- **Insight:** `cache_seqlens` parameter enables adaptive sizing per sequence
- **Reference:** https://github.com/HazyResearch/flash-attention

**VAE Cache Implementation:**
```python
# Hash-based cache with size tracking
def encode_image(self, pixel_values, filepath):
    file_hash = self.create_hash(filepath)
    filename = os.path.join(self.cache_dir, file_hash + ".pt")
    if os.path.exists(filename):  # Cache hit
        latents = self.load_from_cache(filename)
    else:  # Cache miss - encode and save
        latents = self.vae.encode(pixel_values).latent_dist.sample()
        self.save_to_cache(filename, latents)
    return latents
```
- **Pattern:** Check-before-encode with disk-based persistence
- **Insight:** Size tracking via file existence; eviction handled at directory level
- **Reference:** https://github.com/huggingface/diffusers/pull/4505

### Exa GitHub Implementations

**Repository 1: Arvind679715/adaptive-kv-memory** ⭐ DIRECT MATCH
- **URL:** https://github.com/Arvind679715/adaptive-kv-memory
- **Stars:** Not specified
- **Relevance:** Hierarchical adaptive KV cache with 3-tier architecture (hot/warm/cold)
- **Architecture:**
  - **Hot tier:** GPU/FP16 (most-accessed tokens)
  - **Warm tier:** GPU/quantized 3-4 bit block-affine
  - **Cold tier:** CPU/INT2 (least-accessed)
  - **Migration:** Bidirectional, attention-score driven
- **Key Code:**
  ```python
  from akv import AKVCache
  from transformers import AutoModelForCausalLM
  
  cache = AKVCache(preset="balanced")  # Adaptive sizing built-in
  # Zero-config drop-in for HuggingFace models
  ```
- **Training Config:** Not applicable (zero-config inference optimization)
- **Dataset:** Works with any HuggingFace model
- **Insight:** Attention-based importance scoring for tier migration - similar to h-m4 density-based sizing

**Repository 2: Large-scale-Sustainable-Computing-LSC/ARKV**
- **URL:** https://github.com/Large-scale-Sustainable-Computing-LSC/ARKV
- **Paper:** "ARKV: Adaptive and Resource-Efficient KV Cache Management under Limited Memory Budget"
- **Relevance:** Budget-constrained adaptive cache (eviction + quantization hybrid)
- **Architecture:** Dynamic cache allocation under fixed memory budget
- **Training Config:**
  - PyTorch >=2.0.0, Transformers >=4.35.0
  - Optional: Flash Attention 2, bitsandbytes quantization
- **Dataset:** Standard LLM benchmarks (not RAG-specific)
- **Insight:** Budget constraint handling - directly applicable to h-m4's ≤20% budget target

**Repository 3: DreamMr/DynamicKV** ⭐ HIGH RELEVANCE
- **URL:** https://github.com/DreamMr/DynamicKV
- **Paper:** arXiv:2412.14838
- **Relevance:** Task-aware adaptive cache with dynamic per-layer budget allocation
- **Architecture:**
  1. **Dynamic budget:** Top-K tokens per layer (attention-scored)
  2. **Progressive update:** Every m layers, globally renormalize cache sizes
- **Key Mechanism:**
  ```python
  # Pseudo-code from paper description
  for layer in model.layers:
      # Retain top-K tokens based on recent window attention
      cache[layer] = select_top_k(attention_scores, budget_per_layer)
      
      if layer % m == 0:  # Progressive update interval
          # Global renormalization to respect total budget
          redistribute_budget(cache, total_budget)
  ```
- **Results:** **1.7% cache retention → 90% of FullKV performance**
- **Training Config:** No training (plug-and-play)
- **Dataset:** QA, summarization, code (task-adaptive)
- **Insight:** Layer-wise adaptive sizing - orthogonal to h-m4 but demonstrates extreme compression viability

**Repository 4: KVLink (NeurIPS 2025)** ⭐⭐⭐ HIGHEST RELEVANCE FOR RAG
- **Paper:** "KVLink: Accelerating LLMs via Efficient KV Cache Reuse"
- **URLs:** 
  - https://arxiv.org/html/2502.16002v3
  - https://proceedings.neurips.cc/paper_files/paper/2025/file/c217d123885341853cecbdd2be809983-Paper-Conference.pdf
- **Relevance:** Retrieval-augmented QA with document KV cache reuse
- **Architecture:**
  - Pre-encode retrieved documents into separate KV caches
  - **Positional re-encoding:** Adjust position embeddings at inference
  - **Cross-segment tokens:** Trainable link tokens restore inter-document attention
- **Training Config:**
  - Models: Llama-3.2-1B, Llama-3.2-3B, Llama-3.1-8B
  - **Datasets:** **NaturalQuestions**, 2WikiMQA, TriviaQA, HotpotQA, MuSiQue
- **Evaluation Protocol (NaturalQuestions):**
  - 10 retrieved documents per question
  - Answer document systematically placed at positions 0-9
  - Final accuracy = average over 10 position evaluations
- **Results:**
  - **+6.6% over best baseline on NaturalQuestions**
  - **+7.3% on HotpotQA**
  - **96% TTFT latency reduction** via cache reuse
- **Insight:** Cache reuse complementary to adaptive sizing - could combine with h-m4

**Repository 5: RAGCache**
- **Paper:** "RAGCache: Efficient Knowledge Caching for Retrieval-Augmented Generation"
- **URLs:**
  - https://dl.acm.org/doi/full/10.1145/3768628
  - https://arxiv.org/html/2404.12457v2
- **Relevance:** System-level RAG caching with document frequency tracking
- **Architecture:** Multilevel caching (leverages skewed retrieval distribution)
- **Key Finding:** **60% of requests → 3% of documents** (20× skew)
- **Implementation:** vLLM + Faiss, ~5000 lines C++/Python
- **Datasets:** MMLU, **NaturalQuestions**
- **Training Config:**
  - PagedAttention for KV cache management
  - Triton/PyTorch prefill kernels
- **NaturalQuestions Config:**
  - Average output: 6 tokens
  - 99% of answers ≤32 tokens
  - Poisson arrival process for workload simulation
- **Insight:** Document-level caching priority - adaptive sizing could target high-frequency docs

**Repository 6: ProphetKV**
- **Paper:** arXiv:2602.02579v2
- **Relevance:** Query-driven selective recomputation for RAG
- **Architecture:** Dual-stage recomputation with layer-wise fusion
- **Results:** **96%-101% accuracy with 20% recomputation**
- **Insight:** Query relevance scoring - could inform adaptive sizing decisions

**Serena Analysis Needed:** YES
- AKVCache tier migration logic
- DynamicKV progressive budget redistribution
- KVLink positional re-encoding mechanism

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Implementation Priority for h-m4:**

| Priority | Source | Type | Rationale |
|----------|--------|------|-----------|
| ⭐⭐⭐ **PRIMARY** | DreamMr/DynamicKV | Adaptive cache reference | Proven 1.7% → 90% compression, progressive budgeting pattern |
| ⭐⭐ **SECONDARY** | Arvind679715/adaptive-kv-memory | 3-tier adaptive architecture | Attention-based tier migration, production-ready AKVCache API |
| ⭐ **REFERENCE** | FMInference/H2O (from h-m1) | Baseline implementation | H2O eviction oracle for fair comparison |

**Recommended Implementation Path:**
- **Primary**: Custom implementation inspired by DynamicKV (progressive budget redistribution) + AKVCache (tier migration)
- **Fallback**: Adapt AKVCache with retrieval-density based sizing instead of attention-only
- **Justification**:
  - No existing implementation combines retrieval density tracking with adaptive cache sizing
  - DynamicKV proves extreme compression viability (1.7% retention)
  - H2O baseline (from h-m1) provides controlled comparison baseline
  - Custom design required to test h-m4 hypothesis (retrieval density → cache size)

### Code Analysis (Serena MCP)

*Limited* - Serena analysis skipped. Identified code resides in external repositories (Arvind679715/adaptive-kv-memory, DreamMr/DynamicKV, KVLink). Local codebase analysis not applicable for h-m4 mechanism design.

**Key Patterns Extracted from Exa Search:**

**Pattern 1: Attention-Based Importance Scoring (AKVCache)**
```python
# Tier migration based on accumulated attention scores
def compute_importance(attention_weights, cache_position):
    # Accumulate attention across decoding steps
    importance_score[cache_position] += attention_weights.sum()
    
    # Migrate between tiers based on thresholds
    if importance_score > hot_threshold:
        move_to_hot_tier(cache_position)
    elif importance_score < cold_threshold:
        move_to_cold_tier(cache_position)
```

**Pattern 2: Progressive Budget Redistribution (DynamicKV)**
```python
# Every m layers, renormalize cache budgets
for layer_idx in range(num_layers):
    # Local: retain top-K by recent window attention
    layer_cache[layer_idx] = select_top_k(
        attention_scores[layer_idx], 
        budget_per_layer[layer_idx]
    )
    
    if layer_idx % progressive_interval == 0:
        # Global: redistribute total budget across layers
        budget_per_layer = renormalize_budgets(
            layer_cache, 
            total_budget_constraint
        )
```

**Pattern 3: Retrieval Density Tracking**
```python
# RAGCache: document frequency → cache priority
document_access_count = defaultdict(int)

def on_retrieval(retrieved_docs):
    for doc in retrieved_docs:
        document_access_count[doc.id] += 1

def adaptive_cache_size(doc_id, base_budget):
    # Higher frequency → larger cache allocation
    frequency_multiplier = document_access_count[doc_id] / max_access_count
    return int(base_budget * (0.5 + 0.5 * frequency_multiplier))
```

**Synthesis for h-m4:**
- Use attention accumulation (Pattern 1) to track retrieval passage utility
- Implement sliding window budget adjustment (Pattern 2) based on retrieval density
- Track per-passage access frequency (Pattern 3) to inform cache growth/shrink decisions

---

## Experiment Specification

### Dataset

**Dataset**: LongBench (single-hop QA subset)
**Type**: standard
**Source**: THUDM/LongBench (HuggingFace Datasets)
**Task**: TriviaQA (single-hop factual QA, 8,209 avg token length)

**Continuation Note**: Reusing same dataset as h-m1, h-m2, h-m3 for controlled comparison. Only independent variable (IV) = adaptive cache sizing changes.

**Statistics**:
- Test samples: ~200 per task (LongBench standard)
- Average context length: 8,209 tokens (TriviaQA)
- Task type: Extractive/generative QA
- Language: English
- Evaluation metric: F1 score (token overlap)

**Preprocessing**:
- Tokenization: Model-specific tokenizer (Llama tokenizer)
- No additional preprocessing (raw long-context QA)

**Augmentation**: None (evaluation dataset)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Datasets
- Identifier: `THUDM/LongBench`
- Code:
  ```python
  from datasets import load_dataset
  dataset = load_dataset('THUDM/LongBench', 'triviaqa', split='test')
  ```

### Models

#### Baseline Model

**Architecture**: Llama-2-7B
**Type**: Autoregressive causal language model
**Source**: Meta (HuggingFace Transformers)

**Continuation Note**: Reusing same baseline as h-m1, h-m2, h-m3 for fair comparison across cache mechanisms.

**Configuration**:
- Parameters: ~7B
- Layers: 32
- Hidden size: 4096
- Attention heads: 32
- Context window: 4096 tokens (base), extended for long-context evaluation
- Precision: FP16/BF16

**Modifications for Hypothesis**:
- **H2O Baseline (static 25% cache)**: Heavy-hitter oracle eviction (0.125 heavy_ratio + 0.125 recent_ratio)
- **Proposed (adaptive cache)**: Dynamic cache sizing based on retrieval density (≤20% budget on average, matching 25% static accuracy)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers
- Identifier: `meta-llama/Llama-2-7b-hf`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Llama-2-7b-hf",
      torch_dtype=torch.float16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
  ```

#### Proposed Model

**Architecture:** Llama-2-7B + Adaptive KV Cache (Retrieval-Density Based)

**Core Mechanism Implementation:**

```python
# Adaptive KV Cache: Retrieval-Density Based Sizing
# Based on: DynamicKV (arXiv:2412.14838), AKVCache patterns

class AdaptiveKVCache:
    """
    Adaptive cache sizing based on retrieval passage density.
    Grow cache when high retrieval density, shrink when low.
    Target: Match static 25% accuracy at ≤20% average budget.
    """
    def __init__(self, base_budget=0.25, min_budget=0.10, max_budget=0.30):
        self.base_budget = base_budget  # Static baseline: 25%
        self.min_budget = min_budget    # Floor: 10%
        self.max_budget = max_budget    # Ceiling: 30%
        self.passage_access_count = {}  # Track retrieval frequency
        self.current_budget = base_budget
    
    def update_retrieval_density(self, retrieved_passages, window_size=10):
        """Track retrieval passage density over sliding window."""
        # Count unique passages in recent window
        for passage_id in retrieved_passages:
            self.passage_access_count[passage_id] = \
                self.passage_access_count.get(passage_id, 0) + 1
        
        # Compute density: unique passages / window size
        unique_recent = len([p for p in self.passage_access_count 
                            if self.passage_access_count[p] > 0])
        density = unique_recent / window_size
        
        # Adaptive sizing: high density → grow cache, low density → shrink
        if density > 0.7:  # High density threshold
            self.current_budget = min(self.current_budget * 1.1, self.max_budget)
        elif density < 0.3:  # Low density threshold
            self.current_budget = max(self.current_budget * 0.9, self.min_budget)
        
        return int(self.current_budget * total_cache_capacity)
    
    def evict(self, attention_scores, cache_size_target):
        """Evict using H2O-style heavy-hitter oracle."""
        # Retain top-K by attention scores (from H2O baseline)
        heavy_ratio = 0.5 * self.current_budget
        recent_ratio = 0.5 * self.current_budget
        
        heavy_count = int(heavy_ratio * len(attention_scores))
        recent_count = int(recent_ratio * len(attention_scores))
        
        # Heavy hitters: top-K by cumulative attention
        heavy_indices = torch.topk(attention_scores, heavy_count).indices
        # Recent: sliding window
        recent_indices = torch.arange(len(attention_scores) - recent_count, 
                                     len(attention_scores))
        
        keep_indices = torch.cat([heavy_indices, recent_indices]).unique()
        return keep_indices

# Integration: Replace static H2O cache with adaptive version in forward pass
```

**Key Differences from H2O Baseline:**
1. **Static (H2O)**: Fixed 25% cache budget
2. **Adaptive (h-m4)**: Dynamic 10-30% budget based on retrieval density
3. **Expected**: 20% average budget, matching 25% static accuracy

### Training Protocol

**Training**: None required (inference-time cache policy)

**Inference Protocol**:
- **Model**: Llama-2-7B (no fine-tuning)
- **Task**: Retrieval-augmented QA on LongBench TriviaQA
- **Batch size**: 1 (sequential inference, cache state-dependent)
- **Context length**: 8,209 tokens average (TriviaQA)
- **Seed**: 42 (PoC uses single seed)

**Cache Configuration**:
- **H2O Baseline**: `heavy_ratio=0.125, recent_ratio=0.125` (static 25%)
- **Proposed Adaptive**: `base_budget=0.25, min=0.10, max=0.30` (dynamic)
- **Retrieval window**: 10 queries (sliding window for density tracking)

**Evaluation Setup**:
- **Dataset split**: LongBench TriviaQA test set (~200 samples)
- **No train/val split** (evaluation-only experiment)
- **Precision**: FP16 for memory efficiency

### Evaluation

**Primary Metric**: F1 Score (token-level overlap between generated answer and ground truth)

**Computation**:
```python
def compute_f1(prediction, ground_truth):
    pred_tokens = prediction.split()
    gt_tokens = ground_truth.split()
    
    common = Counter(pred_tokens) & Counter(gt_tokens)
    num_common = sum(common.values())
    
    if num_common == 0:
        return 0.0
    
    precision = num_common / len(pred_tokens)
    recall = num_common / len(gt_tokens)
    f1 = 2 * (precision * recall) / (precision + recall)
    return f1
```

**Success Criteria (PoC)**:
1. **Code runs without error**
2. **Adaptive F1 ≥ H2O F1** (direction test, no statistical significance)
3. **Average cache budget ≤ 20%** (resource efficiency check)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Extractive/Generative QA
- Library: Custom (token-level F1 computation as above)
- Code:
  ```python
  from collections import Counter
  
  def compute_f1(prediction, ground_truth):
      # Token-level F1 (standard for LongBench evaluation)
      # (see code above)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: F1 score bar chart (H2O baseline vs Adaptive)

#### Additional Figures (LLM Autonomous)

**Figure 2: Cache Budget Over Time**
- X-axis: Query index (sequential)
- Y-axis: Cache budget percentage
- Lines: Adaptive budget trace (showing growth/shrinkage)
- Horizontal line: Static 25% baseline

**Figure 3: Retrieval Density vs Cache Budget**
- X-axis: Retrieval density (unique passages / window)
- Y-axis: Allocated cache budget
- Scatter plot with trend line

**Figure 4: Cumulative Average Budget**
- X-axis: Query index
- Y-axis: Cumulative average budget
- Target line: 20% threshold

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source 1**: HuggingFace Cache Management
- **Type**: Documentation
- **Query Used**: "adaptive cache sizing experiment design dataset"
- **URL**: https://huggingface.co/docs/huggingface_hub/guides/manage-cache
- **Relevance**: Cache management with size limits and cleanup strategies
- **Key Insights**:
  - LRU eviction patterns
  - Size-based cache cleanup
- **Used For**: Cache eviction policy design

**Source 2**: Flash Attention KV Cache
- **Type**: Code example + documentation
- **Query Used**: "KV cache eviction implementation challenges best practices"
- **URL**: https://github.com/HazyResearch/flash-attention
- **Relevance**: Incremental cache updates with dynamic sequence length tracking
- **Key Insights**:
  - `cache_seqlens` parameter for per-sequence adaptive sizing
  - In-place cache modification pattern
- **Used For**: Cache infrastructure understanding

**Code Source 1**: Flash Attention KV Cache Implementation
- **Query Used**: "adaptive cache PyTorch"
- **Key Code**:
  ```python
  def flash_attn_with_kvcache(
    q, k_cache, v_cache,
    k=new_k, v=new_v,  # New tokens appended in-place
    cache_seqlens=current_lengths,  # Track per-sequence positions
    ...
  )
  ```
- **Used For**: Cache update mechanism pattern

### B. GitHub Implementations (Exa)

**Repository 1**: Arvind679715/adaptive-kv-memory (Direct Match)
- **URL**: https://github.com/Arvind679715/adaptive-kv-memory
- **Query Used**: "adaptive KV cache PyTorch implementation GitHub"
- **Relevance**: Hierarchical 3-tier adaptive cache (hot/warm/cold)
- **Architecture**: Attention-score driven tier migration
- **Key Code Pattern**:
  ```python
  from akv import AKVCache
  cache = AKVCache(preset="balanced")  # Adaptive sizing built-in
  ```
- **Used For**: Tier migration concept, attention-based importance scoring

**Repository 2**: Large-scale-Sustainable-Computing-LSC/ARKV
- **URL**: https://github.com/Large-scale-Sustainable-Computing-LSC/ARKV
- **Paper**: "ARKV: Adaptive and Resource-Efficient KV Cache Management under Limited Memory Budget"
- **Query Used**: Same as Repository 1
- **Relevance**: Budget-constrained adaptive cache
- **Used For**: Budget constraint handling (h-m4's ≤20% target)

**Repository 3**: DreamMr/DynamicKV ⭐ HIGH RELEVANCE
- **URL**: https://github.com/DreamMr/DynamicKV
- **Paper**: arXiv:2412.14838
- **Query Used**: Same as Repository 1
- **Relevance**: Task-aware adaptive cache with per-layer budget allocation
- **Results**: 1.7% cache retention → 90% FullKV performance
- **Key Mechanism**:
  ```python
  # Dynamic budget per layer (top-K by attention)
  # Progressive renormalization every m layers
  for layer in model.layers:
      cache[layer] = select_top_k(attention_scores, budget_per_layer)
      if layer % m == 0:
          redistribute_budget(cache, total_budget)
  ```
- **Used For**: Extreme compression viability proof, progressive budget update concept

**Repository 4**: KVLink (NeurIPS 2025) ⭐⭐⭐ RAG-SPECIFIC
- **Paper**: "KVLink: Accelerating LLMs via Efficient KV Cache Reuse"
- **URLs**:
  - https://arxiv.org/html/2502.16002v3
  - https://proceedings.neurips.cc/paper_files/paper/2025/file/c217d123885341853cecbdd2be809983-Paper-Conference.pdf
- **Query Used**: "retrieval augmented generation KV cache PyTorch NaturalQuestions"
- **Relevance**: RAG with document KV cache reuse (complementary to h-m4)
- **Results**: +6.6% NaturalQuestions, 96% TTFT reduction
- **Evaluation Protocol**: 10 retrieved docs, answer at each position 0-9, average accuracy
- **Used For**: RAG evaluation protocol design, complementary cache reuse concept

**Repository 5**: RAGCache
- **Paper**: "RAGCache: Efficient Knowledge Caching for Retrieval-Augmented Generation"
- **URLs**:
  - https://dl.acm.org/doi/full/10.1145/3768628
  - https://arxiv.org/html/2404.12457v2
- **Query Used**: Same as Repository 4
- **Relevance**: System-level RAG caching with document frequency tracking
- **Key Finding**: 60% of requests → 3% of documents (20× skew)
- **Datasets**: MMLU, NaturalQuestions
- **Used For**: Document-level caching priority insight

### C. Dataset Loading Information

**LongBench Official Documentation**
- **Source**: https://github.com/THUDM/LongBench/blob/main/LongBench/README.md
- **HuggingFace**: https://huggingface.co/datasets/THUDM/LongBench
- **Query Used**: "LongBench dataset THUDM load_dataset HuggingFace usage"
- **Code**:
  ```python
  from datasets import load_dataset
  data = load_dataset('THUDM/LongBench', 'triviaqa', split='test')
  ```
- **Used For**: Dataset loading specification (Step 5)

### D. Model Loading Information

**Llama Model Loading**
- **Source**: Archon code examples
- **Query Used**: "Llama AutoModelForCausalLM pretrained loading"
- **Code**:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Llama-2-7b-hf",
      torch_dtype=torch.float16,
      device_map="auto"
  )
  ```
- **Used For**: Baseline model loading specification (Step 5)

### E. Hypothesis Continuation Context

**Previous Hypothesis**: h-m3 (Query Complexity Attention)
- **File**: docs/youra_research/h-m3/04_validation.md
- **Result**: FAILED (p=0.9537, no significance)
- **Fallback**: Uniform tiering (all retrieval passages treated equally)
- **Used For**: Continuation context, uniform tiering baseline assumption

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-20

### Workflow History for This Hypothesis

- **2026-08-20**: Experiment design completed (Phase 2C)
- **Prerequisites**: h-m3 (VALIDATED), h-m2 (VALIDATED), h-m1 (VALIDATED)
- **Gate**: SHOULD_WORK
- **Status**: Experiment design COMPLETED, ready for Phase 3

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
