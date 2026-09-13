# Logic Design Document — H-M2

**Hypothesis ID**: h-m2  
**Type**: MECHANISM  
**Gate**: SHOULD_WORK  
**Generated**: 2026-08-20

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: API signatures verified from h-m1 code  
**Analyzed Path**: docs/youra_research/h-m1/code/  
**Relevant Symbols**: ProvenanceCache.evict, compute_f1, compute_exact_match, compute_significance

---

## L-1: MMR Diversity Scorer [Complexity: 3, Budget: 8]

**Applied**: PyTorch batch cosine similarity

### API Signatures

```python
class MMRDiversityScorer:
    def __init__(self, lambda_param: float = 0.5):
        """Initialize MMR scorer.
        
        Args:
            lambda_param: Relevance weight (0=pure diversity, 1=pure relevance)
        """
        self.lambda_param = lambda_param
    
    def select_diverse_passages(
        self,
        query_embedding: Tensor,  # [768]
        passage_embeddings: Tensor,  # [N, 768]
        passage_scores: Tensor,  # [N]
        budget_tokens: int
    ) -> Tuple[List[int], List[float]]:
        """Greedily select diverse passages. Returns (selected_indices, mmr_scores)."""
        ...
    
    def compute_mmr_score(
        self,
        candidate_idx: int,
        query_embedding: Tensor,  # [768]
        passage_embeddings: Tensor,  # [N, 768]
        passage_scores: Tensor,  # [N]
        selected_indices: List[int]
    ) -> float:
        """Compute MMR = λ * relevance - (1-λ) * max_similarity."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| query_embedding | [768] | Contriever query vector |
| passage_embeddings | [N, 768] | N=10 passages |
| passage_scores | [N] | Contriever relevance |
| selected_indices | [k] | k ≤ N passages retained |
| mmr_scores | [k] | MMR score per selection |

### Pseudo-code

```
1. selected = []
2. candidates = set(0..N-1)

3. for step in range(budget_tokens // avg_passage_len):
4.     best_score = -inf
5.     best_idx = None
6.     
7.     for idx in candidates:
8.         # Relevance term
9.         rel = passage_scores[idx]
10.         
11.         # Diversity term
12.         if selected:
13.             # Batch cosine: [1, 768] @ [k, 768].T -> [1, k]
14.             sims = F.cosine_similarity(
15.                 passage_embeddings[idx].unsqueeze(0),
16.                 passage_embeddings[selected]
17.             )
18.             max_sim = sims.max()
19.         else:
20.             max_sim = 0.0  # First passage edge case
21.         
22.         # MMR score
23.         mmr = lambda_param * rel - (1 - lambda_param) * max_sim
24.         
25.         if mmr > best_score:
26.             best_score = mmr
27.             best_idx = idx
28.     
29.     selected.append(best_idx)
30.     candidates.remove(best_idx)
31. 
32. return selected, [mmr_scores[i] for i in selected]
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Init | Store lambda parameter |
| L-1-2 | Greedy loop | Iterate until budget exhausted |
| L-1-3 | Batch cosine | GPU-accelerated similarity [1, 768] @ [k, 768].T |
| L-1-4 | Max similarity | Reduce over selected passages |
| L-1-5 | MMR score | λ * rel - (1-λ) * max_sim |
| L-1-6 | First passage | max_sim = 0.0 edge case |
| L-1-7 | Lambda edge | λ=1.0 → pure relevance, λ=0.0 → pure diversity |
| L-1-8 | Return | (selected_indices, mmr_scores) |

---

## L-2: Tiered Eviction State Machine [Complexity: 4, Budget: 10]

**Applied**: h-m1 ProvenanceCache pattern (extended with diversity)

### API Signatures

```python
class ProvenanceCacheDiversity(ProvenanceCache):
    """Extends h-m1 ProvenanceCache with MMR diversity scoring."""
    
    def __init__(
        self,
        config: ProvenanceCacheConfig,
        diversity_scorer: Optional[MMRDiversityScorer] = None
    ):
        """Initialize cache with optional diversity scorer.
        
        Args:
            config: Cache budget + tier allocation
            diversity_scorer: If None, use relevance-only (ablation baseline)
        """
        super().__init__(config)
        self.diversity_scorer = diversity_scorer
    
    def evict(
        self,
        k: Tensor,  # [B, H, L, D]
        v: Tensor,  # [B, H, L, D]
        max_len: int,
        passage_embeddings: Optional[Dict[str, Tensor]] = None,
        query_embedding: Optional[Tensor] = None
    ) -> Tuple[Tensor, Tensor]:
        """Evict KV cache to budget with diversity-aware tier selection."""
        ...
    
    def _select_tier_passages(
        self,
        tier: int,
        passage_ids: List[str],
        scores: Dict[str, float],
        budget_tokens: int,
        passage_embeddings: Optional[Dict[str, Tensor]] = None,
        query_embedding: Optional[Tensor] = None
    ) -> List[str]:
        """Select passages within tier budget (diversity-aware or relevance-only)."""
        ...
```

### State Machine

```
State 0: Init (k, v, provenance_metadata, budget)
  ↓
State 1: Assign tiers (query=0, high_rel=1, low_rel=2)
  ↓
State 2: Tier 0 eviction (query tokens always kept, clip if overflow)
  ↓
State 3: Tier 1 eviction (diversity_scorer? MMR : relevance_sort)
  ↓
State 4: Tier 2 eviction (diversity_scorer? MMR : relevance_sort)
  ↓
State 5: Merge retained tokens, return (k', v')
```

### Pseudo-code

```
1. seq_len = k.shape[2]
2. budget = int(max_len * cache_budget_ratio)
3. 
4. # Tier assignment (from h-m1)
5. query_mask = [provenance[i][0] == 'query' for i in range(seq_len)]
6. high_rel_mask = [provenance[i][0] == 'high_rel_passage' for i in range(seq_len)]
7. low_rel_mask = [provenance[i][0] == 'low_rel_passage' for i in range(seq_len)]
8. 
9. # Tier 0: Query tokens (always retained)
10. query_budget = int(budget * 0.1)
11. query_indices = torch.where(query_mask)[0][:query_budget]
12. 
13. # Tier 1: High-relevance passages
14. high_rel_budget = int(budget * 0.6)
15. high_rel_ids = [provenance[i][1] for i in range(seq_len) if high_rel_mask[i]]
16. 
17. if diversity_scorer:
18.     # Diversity-aware selection
19.     selected = diversity_scorer.select_diverse_passages(
20.         query_embedding,
21.         passage_embeddings[high_rel_ids],  # [N_high, 768]
22.         relevance_scores[high_rel_ids],    # [N_high]
23.         high_rel_budget
24.     )
25. else:
26.     # Relevance-only (ablation baseline)
27.     selected = sorted(high_rel_ids, key=lambda x: relevance_scores[x], reverse=True)
28.     selected = selected[:high_rel_budget // avg_passage_len]
29. 
30. high_rel_indices = [i for i in range(seq_len) if provenance[i][1] in selected]
31. 
32. # Tier 2: Low-relevance passages (same logic)
33. low_rel_budget = int(budget * 0.3)
34. low_rel_indices = _select_tier_passages(2, low_rel_ids, low_rel_budget)
35. 
36. # Merge and slice KV cache
37. keep_mask = torch.zeros(seq_len, dtype=bool)
38. keep_mask[query_indices] = True
39. keep_mask[high_rel_indices] = True
40. keep_mask[low_rel_indices] = True
41. 
42. return k[:, :, keep_mask, :], v[:, :, keep_mask, :]
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Extend base | Inherit from h-m1 ProvenanceCache |
| L-2-2 | Diversity flag | Check if diversity_scorer is None |
| L-2-3 | Tier 0 budget | Query tokens, clip if overflow |
| L-2-4 | Tier 1 selection | MMR if diversity_scorer else relevance_sort |
| L-2-5 | Tier 2 selection | Same logic as Tier 1 |
| L-2-6 | Budget overflow | Tier 0 exceeds → reduce Tier 1/2 |
| L-2-7 | Passage→token map | Map passage IDs to token indices |
| L-2-8 | Keep mask | Boolean mask for KV cache slicing |
| L-2-9 | KV slice | k[:, :, keep_mask, :], v[:, :, keep_mask, :] |
| L-2-10 | Return | (k_retained, v_retained) |

---

## L-3: Passage Embedding Cache [Complexity: 2, Budget: 5]

**Applied**: torch.load memory-mapped storage

### API Signatures

```python
class EmbeddingCache:
    def __init__(self, cache_path: str):
        """Load embedding cache from disk (memory-mapped)."""
        self.cache = torch.load(cache_path, map_location='cpu', mmap=True)
    
    def get_embeddings(
        self,
        question_id: str,
        passage_ids: List[str]
    ) -> Tensor:
        """Fetch embeddings for passages. Returns [N, 768]."""
        ...
    
    def get_query_embedding(self, question_id: str) -> Tensor:
        """Fetch query embedding. Returns [768]."""
        ...
```

### Pseudo-code

```
1. cache = torch.load(cache_path, mmap=True)  # Lazy loading
2. 
3. def get_embeddings(question_id, passage_ids):
4.     embs = [cache[question_id][pid] for pid in passage_ids]
5.     return torch.stack(embs)  # [N, 768]
6. 
7. def get_query_embedding(question_id):
8.     return cache[question_id]['query']  # [768]
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Load cache | torch.load with mmap=True |
| L-3-2 | Get passages | Stack embeddings [N, 768] |
| L-3-3 | Get query | Single vector [768] |
| L-3-4 | Missing key | Raise KeyError if question_id not in cache |
| L-3-5 | Device transfer | .to(device) when needed |

---

## L-4: HotpotQA Evaluation [Complexity: 2, Budget: 6]

**Applied**: h-m1 normalize_answer, compute_f1 (reuse exact API)

### API Signatures (Verified from h-m1/code/evaluate.py)

```python
def normalize_answer(s: str) -> str:
    """Remove articles, punctuation, extra whitespace. Returns normalized string."""
    ...

def compute_f1(prediction: str, ground_truths: List[str]) -> float:
    """Token-level F1 (max over multiple ground truths). Returns F1 ∈ [0, 1]."""
    ...

def compute_exact_match(prediction: str, ground_truths: List[str]) -> float:
    """Binary exact match after normalization. Returns 0.0 or 1.0."""
    ...

def compute_significance(
    diversity_scores: List[float],
    relevance_scores: List[float],
    alpha: float = 0.05
) -> Dict[str, float]:
    """Two-tailed paired t-test. Returns {t_stat, p_value, significant}."""
    ...
```

### Pseudo-code (F1 computation)

```
1. pred_tokens = normalize_answer(prediction).split()
2. max_f1 = 0.0
3. 
4. for gt in ground_truths:
5.     gt_tokens = normalize_answer(gt).split()
6.     common = Counter(pred_tokens) & Counter(gt_tokens)
7.     num_same = sum(common.values())
8.     
9.     if num_same == 0:
10.         f1 = 0.0
11.     else:
12.         precision = num_same / len(pred_tokens)
13.         recall = num_same / len(gt_tokens)
14.         f1 = 2 * precision * recall / (precision + recall)
15.     
16.     max_f1 = max(max_f1, f1)
17. 
18. return max_f1
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Normalize | Lowercase, strip articles (a/an/the), remove punctuation |
| L-4-2 | Tokenize | Split on whitespace |
| L-4-3 | Precision | num_same / len(pred_tokens) |
| L-4-4 | Recall | num_same / len(gt_tokens) |
| L-4-5 | F1 | 2 * P * R / (P + R) |
| L-4-6 | Max F1 | Take max over multiple ground truths |

---

## External Dependencies (Base Hypothesis)

### API Signatures (From h-m1/code/)

The following APIs are reused from h-m1 (verified from actual code):

```python
# From: h-m1/code/cache_policy.py
class ProvenanceCache:
    def __init__(self, config: ProvenanceCacheConfig):
        self.cache_budget_ratio = config.cache_budget_ratio
        self.high_rel_count = config.high_rel_count
        self.tier_allocation_high = config.tier_allocation_high
        self.tier_allocation_low = config.tier_allocation_low
        self.provenance_metadata: Dict[int, Tuple[str, float]] = {}
    
    def register_provenance(
        self,
        token_indices: List[int],
        token_types: List[str],
        relevance_scores: List[float]
    ) -> None:
        """Register provenance metadata for tokens."""
        ...
    
    def evict(
        self,
        k: Tensor,  # [B, H, L, D]
        v: Tensor,  # [B, H, L, D]
        max_len: int
    ) -> Tuple[Tensor, Tensor]:
        """Base eviction logic (relevance-only)."""
        ...

# From: h-m1/code/evaluate.py
def normalize_answer(s: str) -> str:
    """Normalize answer string for HotpotQA evaluation."""
    ...

def compute_f1(prediction: str, ground_truths: List[str]) -> float:
    """Token-level F1 score."""
    ...

def compute_exact_match(prediction: str, ground_truths: List[str]) -> float:
    """Binary exact match score."""
    ...

def compute_significance(
    provenance_scores: List[float],
    h2o_scores: List[float],
    alpha: float = 0.05
) -> Dict[str, float]:
    """Paired t-test for statistical validation."""
    ...
```

**Verified from**: h-m1/code/cache_policy.py, h-m1/code/evaluate.py

---

## Edge Case Handling

### MMR Edge Cases
1. **First passage**: max_similarity = 0.0 (no selected passages yet)
2. **Lambda=1.0**: Collapses to pure relevance ranking (diversity term zeroed)
3. **Lambda=0.0**: Pure diversity (relevance term zeroed, unlikely to select high-relevance passages)

### Budget Overflow
1. **Query tokens exceed Tier 0 budget**: Clip query tokens to budget, log warning
2. **Tier allocation sum ≠ 1.0**: Raise ValueError during initialization
3. **No high-relevance passages**: Roll Tier 1 budget to Tier 2

### Embedding Cache
1. **Missing question_id**: Raise KeyError with clear error message
2. **Missing passage_id**: Raise KeyError (indicates data preprocessing bug)
3. **Dimension mismatch**: Validate embedding.shape == [768] during load

---

## Performance Constraints

| Component | Constraint | Strategy |
|-----------|-----------|----------|
| MMR selection | <100ms for 10 passages | Batch cosine similarity on GPU |
| Embedding cache | <10ms per lookup | Memory-mapped torch.load |
| Eviction decision | <500ms per step | Reuse h-m1 tier assignment logic |
| F1 computation | <1ms per sample | Reuse h-m1 normalize_answer |

---

**Document Status**: READY FOR PHASE 4 IMPLEMENTATION  
**Total Subtasks**: 29 (within budget)  
**Base Hypothesis Integration**: h-m1 ProvenanceCache, evaluate.py APIs verified
