# Logic Specifications: H-M1 ProvenanceCache

**Date:** 2026-08-20  
**Hypothesis:** Provenance-Aware Tiered KV Cache Eviction  
**Target:** ≥5% F1 gain vs H2O at 25% cache budget

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation - no existing code to analyze  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - new implementation

---

## Core Algorithms

### A1: ProvenanceCache Eviction (Complexity: 3, Budget: 8)

**Applied:** Three-tier priority queue pattern (query > high-rel > low-rel)

#### API Signatures

```python
class ProvenanceCache:
    def __init__(self, cache_budget_ratio: float = 0.25):
        """Initialize cache with budget ratio."""
        self.cache_budget_ratio = cache_budget_ratio
        self.provenance_metadata: Dict[int, Tuple[str, float]] = {}
    
    def register_provenance(
        self,
        token_indices: List[int],
        token_types: List[str],
        relevance_scores: List[float]
    ) -> None:
        """Register provenance metadata. types: ['query', 'high_rel_passage', 'low_rel_passage']"""
        ...
    
    def evict_tokens(
        self,
        cache_keys: Tensor,  # [B, H, L, D]
        cache_values: Tensor,  # [B, H, L, D]
        max_seq_len: int
    ) -> Tuple[Tensor, Tensor]:
        """Evict tokens based on three-tier policy. Returns: ([B, H, L', D], [B, H, L', D])"""
        ...
```

#### Pseudo-code

```
INPUT: cache_keys [B, H, L, D], cache_values [B, H, L, D], max_seq_len
OUTPUT: evicted_keys [B, H, L', D], evicted_values [B, H, L', D]

1. cache_budget = int(max_seq_len * cache_budget_ratio)
2. keep_mask = zeros(L, dtype=bool)

3. Tier 0 (Query tokens - highest priority):
   query_indices = [i for i, (type, _) in metadata.items() if type == "query"]
   keep_mask[query_indices] = True

4. Tier 1 (High-relevance passages):
   high_rel = [(i, score) for i, (type, score) in metadata.items() if type == "high_rel_passage"]
   high_rel.sort(key=score, reverse=True)
   n_high = min(len(high_rel), cache_budget // 2)
   keep_mask[[i for i, _ in high_rel[:n_high]]] = True

5. Tier 2 (Low-relevance passages - diverse subset):
   low_rel = [(i, score) for i, (type, score) in metadata.items() if type == "low_rel_passage"]
   n_low = cache_budget - keep_mask.sum()
   keep_mask[[i for i, _ in low_rel[:n_low]]] = True

6. RETURN cache_keys[:, :, keep_mask, :], cache_values[:, :, keep_mask, :]
```

#### Correctness Invariants

- Total retained tokens ≤ cache_budget
- Query tokens always retained (tier precedence)
- High-rel tokens prioritized over low-rel (tier precedence)
- No duplicate token indices

#### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A1-1 | ProvenanceCache.__init__ | Initialize cache budget and metadata dict |
| L-A1-2 | register_provenance | Store token type and relevance score mappings |
| L-A1-3 | evict_tokens | Implement three-tier eviction logic |
| L-A1-4 | Tier 0 logic | Extract and retain query tokens |
| L-A1-5 | Tier 1 logic | Sort high-rel by score, retain top-K |
| L-A1-6 | Tier 2 logic | Fill remaining budget with low-rel |
| L-A1-7 | Build keep_mask | Boolean indexing for cache slicing |
| L-A1-8 | Return evicted cache | Slice keys/values by mask |

---

### A2: H2O Baseline Eviction (Complexity: 3, Budget: 8)

**Applied:** Heavy-hitter + recent token policy from NeurIPS 2023 paper

#### API Signatures

```python
class H2OCache:
    def __init__(self, heavy_ratio: float = 0.125, recent_ratio: float = 0.125, n_sink: int = 4):
        """Initialize H2O cache with heavy-hitter and recent token ratios."""
        self.heavy_ratio = heavy_ratio
        self.recent_ratio = recent_ratio
        self.n_sink = n_sink
        self.accumulated_attention: Dict[int, float] = {}
    
    def update_attention_scores(self, attention_weights: Tensor) -> None:
        """Accumulate attention scores. attention_weights: [B, H, Lq, Lkv]"""
        ...
    
    def evict_tokens(
        self,
        cache_keys: Tensor,  # [B, H, L, D]
        cache_values: Tensor,  # [B, H, L, D]
        cache_budget: int
    ) -> Tuple[Tensor, Tensor]:
        """Evict tokens using H2O policy. Returns: ([B, H, L', D], [B, H, L', D])"""
        ...
```

#### Pseudo-code

```
UPDATE ATTENTION SCORES:
INPUT: attention_weights [B, H, Lq, Lkv]
1. token_importance = attention_weights.sum(dim=(1, 2))  # [B, Lkv]
2. FOR each token_idx in range(Lkv):
     accumulated_attention[token_idx] += token_importance[0, token_idx]

EVICT TOKENS:
INPUT: cache_keys [B, H, L, D], cache_values [B, H, L, D], cache_budget
OUTPUT: evicted_keys [B, H, L', D], evicted_values [B, H, L', D]

1. keep_mask = zeros(L, dtype=bool)

2. Tier 0 (Attention sinks - first tokens):
   keep_mask[:n_sink] = True

3. Tier 1 (Heavy hitters - top by accumulated attention):
   n_heavy = int(cache_budget * heavy_ratio)
   attention_scores = tensor([accumulated_attention.get(i, 0) for i in range(L)])
   attention_scores[:n_sink] = -inf  # Exclude sinks from selection
   heavy_indices = topk(attention_scores, k=min(n_heavy, L)).indices
   keep_mask[heavy_indices] = True

4. Tier 2 (Recent tokens - sliding window):
   n_recent = int(cache_budget * recent_ratio)
   keep_mask[-n_recent:] = True

5. Update accumulated_attention tracker (re-index retained tokens)
6. RETURN cache_keys[:, :, keep_mask, :], cache_values[:, :, keep_mask, :]
```

#### Correctness Invariants

- Sink tokens always retained (attention sink preservation)
- Heavy-hitter count ≤ n_heavy (budget constraint)
- Recent count = n_recent (sliding window guarantee)
- Accumulated attention re-indexed after eviction

#### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A2-1 | H2OCache.__init__ | Initialize ratios and attention tracker |
| L-A2-2 | update_attention_scores | Sum attention across heads/queries |
| L-A2-3 | evict_tokens | Implement sink + heavy + recent logic |
| L-A2-4 | Tier 0 logic | Retain first n_sink tokens |
| L-A2-5 | Tier 1 logic | Top-K by accumulated attention |
| L-A2-6 | Tier 2 logic | Sliding window of recent tokens |
| L-A2-7 | Re-index tracker | Update accumulated_attention after eviction |
| L-A2-8 | Return evicted cache | Slice keys/values by mask |

---

### A3: Contriever Retrieval Pipeline (Complexity: 2, Budget: 6)

**Applied:** Dense passage retrieval with chunking and top-K selection

#### API Signatures

```python
class ContrieverRetriever:
    def __init__(self, model_name: str = "facebook/contriever-msmarco"):
        """Load Contriever model and tokenizer."""
        ...
    
    def chunk_document(
        self,
        document: str,
        chunk_size: int = 512,
        overlap: int = 128
    ) -> List[str]:
        """Split document into overlapping passages. Returns: list of passage strings"""
        ...
    
    def retrieve(
        self,
        query: str,
        passages: List[str],
        top_k: int = 5
    ) -> Tuple[List[str], List[float]]:
        """Retrieve top-K passages. Returns: (passages, normalized_scores)"""
        ...
```

#### Pseudo-code

```
CHUNK DOCUMENT:
INPUT: document (str), chunk_size, overlap
OUTPUT: passages (List[str])

1. tokens = tokenize(document)
2. passages = []
3. FOR start in range(0, len(tokens), chunk_size - overlap):
     end = start + chunk_size
     passages.append(detokenize(tokens[start:end]))
4. RETURN passages

RETRIEVE:
INPUT: query (str), passages (List[str]), top_k
OUTPUT: top_passages (List[str]), normalized_scores (List[float])

1. query_emb = encode(query)  # [D]
2. passage_embs = encode(passages)  # [N, D]
3. scores = cosine_similarity(query_emb, passage_embs)  # [N]
4. normalized_scores = (scores - min(scores)) / (max(scores) - min(scores))  # Min-max to [0,1]
5. top_indices = argsort(scores, descending=True)[:top_k]
6. RETURN [passages[i] for i in top_indices], [normalized_scores[i] for i in top_indices]
```

#### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A3-1 | ContrieverRetriever.__init__ | Load model from HuggingFace |
| L-A3-2 | chunk_document | Sliding window tokenization |
| L-A3-3 | retrieve | Encode query and passages |
| L-A3-4 | Compute similarity | Cosine similarity between embeddings |
| L-A3-5 | Normalize scores | Min-max scaling to [0,1] |
| L-A3-6 | Select top-K | Argsort and slice results |

---

### A4: F1 Score Computation (Complexity: 1, Budget: 4)

**Applied:** Token-level overlap with normalization (LongBench standard)

#### API Signatures

```python
def compute_f1(prediction: str, ground_truths: List[str]) -> float:
    """Compute max F1 across ground truth answers. Returns: F1 score in [0,1]"""
    ...

def normalize_answer(s: str) -> str:
    """Remove articles, punctuation, extra whitespace. Returns: normalized string"""
    ...
```

#### Pseudo-code

```
NORMALIZE ANSWER:
INPUT: s (str)
OUTPUT: normalized (str)

1. s = s.lower()
2. s = remove_regex(s, r'\b(a|an|the)\b')  # Remove articles
3. s = remove_punctuation(s)
4. s = normalize_whitespace(s)
5. RETURN s

COMPUTE F1:
INPUT: prediction (str), ground_truths (List[str])
OUTPUT: max_f1 (float)

1. pred_tokens = normalize_answer(prediction).split()
2. max_f1 = 0.0
3. FOR gt in ground_truths:
     gt_tokens = normalize_answer(gt).split()
     common = Counter(pred_tokens) & Counter(gt_tokens)
     num_same = sum(common.values())
     IF num_same == 0:
       f1 = 0.0
     ELSE:
       precision = num_same / len(pred_tokens)
       recall = num_same / len(gt_tokens)
       f1 = 2 * precision * recall / (precision + recall)
     max_f1 = max(max_f1, f1)
4. RETURN max_f1
```

#### Edge Cases

- Empty prediction: F1 = 0
- Empty ground truth: F1 = 0
- Exact match after normalization: F1 = 1.0
- No common tokens: F1 = 0

#### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A4-1 | normalize_answer | Remove articles, punctuation, whitespace |
| L-A4-2 | Tokenize | Split normalized strings |
| L-A4-3 | Compute overlap | Counter intersection for common tokens |
| L-A4-4 | Max F1 | Iterate over ground truths, return max |

---

### A5: Statistical Testing (Complexity: 1, Budget: 3)

**Applied:** Two-tailed paired t-test for F1 comparison

#### API Signatures

```python
def compute_significance(
    provenance_scores: List[float],
    h2o_scores: List[float],
    alpha: float = 0.05
) -> Dict[str, float]:
    """Paired t-test for F1 scores. Returns: {'t_stat': ..., 'p_value': ..., 'significant': bool}"""
    ...
```

#### Pseudo-code

```
INPUT: provenance_scores (List[float]), h2o_scores (List[float]), alpha
OUTPUT: result (Dict)

1. ASSERT len(provenance_scores) == len(h2o_scores)
2. differences = [p - h for p, h in zip(provenance_scores, h2o_scores)]
3. t_stat, p_value = scipy.stats.ttest_rel(provenance_scores, h2o_scores)
4. significant = (p_value < alpha)
5. RETURN {'t_stat': t_stat, 'p_value': p_value, 'significant': significant}
```

#### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-A5-1 | Compute differences | Element-wise subtraction |
| L-A5-2 | Paired t-test | scipy.stats.ttest_rel |
| L-A5-3 | Significance check | p_value < alpha |

---

## Provenance Registration Logic

### Token-to-Provenance Mapping

```python
def register_query_and_passages(
    query_tokens: List[int],
    passage_tokens_list: List[List[int]],
    passage_scores: List[float],
    cache: ProvenanceCache,
    high_rel_threshold: int = 3
) -> None:
    """Map tokens to provenance types and scores.
    
    query_tokens: [Q] token indices for query
    passage_tokens_list: [[P1], [P2], ...] token indices per passage
    passage_scores: [S1, S2, ...] normalized retrieval scores
    high_rel_threshold: top-K passages marked as high-relevance
    """
    # Register query tokens (highest priority)
    cache.register_provenance(
        query_tokens,
        ["query"] * len(query_tokens),
        [1.0] * len(query_tokens)  # Max score for query tokens
    )
    
    # Register passage tokens (high-rel vs low-rel)
    for i, (passage_tokens, score) in enumerate(zip(passage_tokens_list, passage_scores)):
        token_type = "high_rel_passage" if i < high_rel_threshold else "low_rel_passage"
        cache.register_provenance(
            passage_tokens,
            [token_type] * len(passage_tokens),
            [score] * len(passage_tokens)
        )
```

---

## Integration Workflow

### End-to-End Pipeline

```
1. Load LongBench question-document pair
2. Chunk document → passages (ContrieverRetriever.chunk_document)
3. Retrieve top-K passages (ContrieverRetriever.retrieve)
4. Tokenize query + retrieved passages
5. Register provenance metadata (register_query_and_passages)
6. Run generation with ProvenanceCache eviction
7. Compute F1 score (compute_f1)
8. Repeat for all samples and conditions
9. Statistical testing (compute_significance)
```

### Complexity Analysis

| Algorithm | Time Complexity | Space Complexity |
|-----------|-----------------|------------------|
| ProvenanceCache.evict_tokens | O(L log L) | O(L) |
| H2OCache.evict_tokens | O(L log L) | O(L) |
| ContrieverRetriever.retrieve | O(N × D) | O(N × D) |
| compute_f1 | O(T × G × W) | O(W) |

Legend: L = sequence length, N = num passages, D = embedding dim, T = num ground truths, G = avg ground truth length, W = avg word count

---

## Budget Summary

| Task | Allocated | Used | Remaining |
|------|-----------|------|-----------|
| A1 (ProvenanceCache) | 8 | 8 | 0 |
| A2 (H2OCache) | 8 | 8 | 0 |
| A3 (Contriever) | 6 | 6 | 0 |
| A4 (F1 Score) | 4 | 4 | 0 |
| A5 (Statistical Test) | 3 | 3 | 0 |
| **Total** | **29** | **29** | **0** |

---

*Applied KB patterns: Three-tier priority queue, token-level F1 normalization, paired t-test*  
*Green-field project - new API design*
