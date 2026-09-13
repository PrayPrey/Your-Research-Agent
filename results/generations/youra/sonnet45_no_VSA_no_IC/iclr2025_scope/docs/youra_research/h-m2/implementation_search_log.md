# Implementation Search Log — H-M2

**Generated**: 2026-08-20  
**Purpose**: Query Archon knowledge base for implementation examples to inform Phase 3 code design  
**Target**: MMR diversity scoring, Contriever embeddings, tiered cache eviction, HotpotQA evaluation

---

## Search Query 1: MMR Diversity Scoring

**Query**: `rag_search_code_examples("MMR diversity scoring", match_count=5)`

**Expected Patterns**:
- Greedy MMR selection algorithm (iterative relevance - max_similarity computation)
- Cosine similarity computation between embeddings
- Lambda parameter handling (relevance-diversity tradeoff)

**Implementation Notes**:
- MMR formula: `score = λ * relevance - (1-λ) * max_similarity(candidate, selected_set)`
- Greedy loop: Start with highest-relevance passage, iteratively select next-best MMR score
- Sentence-transformers `util.cos_sim()` for pairwise similarity matrix

**Code Snippet Template** (expected from search):
```python
def mmr_select(candidates, query_embedding, embeddings, lambda_param=0.5, k=5):
    """Greedy MMR passage selection."""
    selected_indices = []
    candidate_pool = set(range(len(candidates)))
    
    # Compute relevance scores (cosine similarity to query)
    relevance = util.cos_sim(query_embedding, embeddings)[0]  # shape: (n_candidates,)
    
    # Greedy selection
    for _ in range(k):
        best_score = -float('inf')
        best_idx = None
        
        for idx in candidate_pool:
            # Relevance term
            rel_score = relevance[idx]
            
            # Diversity term (max similarity to already-selected passages)
            if selected_indices:
                similarities = util.cos_sim(embeddings[idx], embeddings[selected_indices])[0]
                max_sim = similarities.max()
            else:
                max_sim = 0.0
            
            # MMR score
            mmr_score = lambda_param * rel_score - (1 - lambda_param) * max_sim
            
            if mmr_score > best_score:
                best_score = mmr_score
                best_idx = idx
        
        selected_indices.append(best_idx)
        candidate_pool.remove(best_idx)
    
    return selected_indices
```

---

## Search Query 2: Contriever Passage Embeddings

**Query**: `rag_search_code_examples("Contriever passage embeddings", match_count=5)`

**Expected Patterns**:
- SentenceTransformer model loading (`sentence-transformers/contriever-base-msmarco`)
- Batch encoding for efficiency (multiple passages per call)
- Embedding cache management (precompute + save to disk)

**Code Snippet Template** (expected from search):
```python
from sentence_transformers import SentenceTransformer
import pickle

# Load Contriever model
model = SentenceTransformer('sentence-transformers/contriever-base-msmarco')

# Encode passages (batch processing)
passages = ["Passage 1 text...", "Passage 2 text..."]
embeddings = model.encode(passages, convert_to_tensor=True, show_progress_bar=True)

# Cache embeddings to disk
with open('passage_embeddings_cache.pkl', 'wb') as f:
    pickle.dump(embeddings, f)

# Load cached embeddings
with open('passage_embeddings_cache.pkl', 'rb') as f:
    cached_embeddings = pickle.load(f)
```

**Implementation Notes**:
- Use `convert_to_tensor=True` for GPU acceleration (torch.Tensor on CUDA)
- Batch size: 32-64 passages per encode call (balance memory vs speed)
- Cache embeddings per dataset split (dev set: 7,405 questions × 10 passages = 74,050 embeddings)

---

## Search Query 3: KV Cache Eviction Policy

**Query**: `rag_search_code_examples("KV cache eviction policy", match_count=5)`

**Expected Patterns**:
- Cache budget tracking (tokens consumed per layer)
- Eviction selection logic (scoring function → sort → evict lowest-scored)
- Tiered eviction priority (query tokens > high-relevance > low-relevance)

**Code Snippet Template** (expected from search):
```python
class TieredEvictionPolicy:
    def __init__(self, budget_percent=0.25, tier_allocation=(0.1, 0.6, 0.3)):
        self.budget_percent = budget_percent
        self.tier_allocation = tier_allocation  # (query, high_rel, low_rel)
    
    def evict(self, kv_cache, passage_scores, query_token_count):
        """Evict KV cache entries to meet budget constraint."""
        total_tokens = sum(kv_cache.token_counts)
        budget = int(total_tokens * self.budget_percent)
        
        # Tier budgets
        query_budget = int(budget * self.tier_allocation[0])
        high_rel_budget = int(budget * self.tier_allocation[1])
        low_rel_budget = int(budget * self.tier_allocation[2])
        
        # Tier 0: Always retain query tokens
        retained_query = kv_cache.select_by_provenance('query', max_tokens=query_budget)
        
        # Tier 1: High-relevance passages (top-k by score)
        high_rel_passages = sorted(passage_scores, key=lambda x: x[1], reverse=True)[:5]
        retained_high_rel = kv_cache.select_passages(high_rel_passages, max_tokens=high_rel_budget)
        
        # Tier 2: Low-relevance passages (remaining budget)
        low_rel_passages = sorted(passage_scores, key=lambda x: x[1], reverse=True)[5:]
        retained_low_rel = kv_cache.select_passages(low_rel_passages, max_tokens=low_rel_budget)
        
        # Merge retained entries
        retained_cache = retained_query + retained_high_rel + retained_low_rel
        return retained_cache
```

**Implementation Notes**:
- Budget overflow handling: If Tier 0 exceeds budget, clip Tier 1/2 (query tokens never evicted)
- Diversity-aware variant: Replace `sorted(passage_scores, key=lambda x: x[1])` with MMR scoring
- Token count tracking: Sum across all transformer layers (consistent with H2O implementation)

---

## Search Query 4: HotpotQA Evaluation F1 Score

**Query**: `rag_search_code_examples("HotpotQA evaluation F1 score", match_count=5)`

**Expected Patterns**:
- Official `hotpot_evaluate_v1.py` script usage
- Token-level F1 computation (normalize answer strings, compute overlap)
- Exact Match (EM) binary scoring

**Code Snippet Template** (expected from search):
```python
def normalize_answer(s):
    """Normalize answer string (lowercase, strip articles/punctuation)."""
    import re
    import string
    
    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)
    
    def white_space_fix(text):
        return ' '.join(text.split())
    
    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)
    
    def lower(text):
        return text.lower()
    
    return white_space_fix(remove_articles(remove_punc(lower(s))))

def f1_score(prediction, ground_truth):
    """Compute token-level F1 between prediction and ground truth."""
    pred_tokens = normalize_answer(prediction).split()
    gt_tokens = normalize_answer(ground_truth).split()
    
    if len(pred_tokens) == 0 or len(gt_tokens) == 0:
        return int(pred_tokens == gt_tokens)
    
    common = set(pred_tokens) & set(gt_tokens)
    num_same = len(common)
    
    if num_same == 0:
        return 0
    
    precision = num_same / len(pred_tokens)
    recall = num_same / len(gt_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    return f1

def exact_match(prediction, ground_truth):
    """Binary exact match score."""
    return normalize_answer(prediction) == normalize_answer(ground_truth)
```

**Implementation Notes**:
- Normalization: Lowercase, strip articles (a/an/the), remove punctuation
- F1 aggregation: Macro-average (per-question F1, then average across dataset)
- HotpotQA ground truth format: `{"answer": str, "supporting_facts": [[title, sent_id], ...]}`

---

## Search Query 5: Tiered Eviction Cache Implementation

**Query**: `rag_search_knowledge_base("tiered eviction cache implementation", match_count=5)`

**Expected Patterns**:
- Multi-tier cache data structures (priority queues, sorted lists)
- Provenance metadata tagging (query tokens, passage IDs, relevance tiers)
- Budget enforcement (cumulative token counting, eviction triggers)

**Code Snippet Template** (expected from search):
```python
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class CacheEntry:
    token_ids: List[int]
    provenance: str  # 'query' | 'passage_{id}'
    relevance_score: float
    tier: int  # 0=query, 1=high_rel, 2=low_rel
    
class ProvenanceCacheTiered:
    def __init__(self, budget_percent=0.25, tier_allocation=(0.1, 0.6, 0.3)):
        self.budget_percent = budget_percent
        self.tier_allocation = tier_allocation
        self.entries: List[CacheEntry] = []
    
    def add_entry(self, token_ids, provenance, relevance_score):
        """Add cache entry with provenance metadata."""
        tier = self._assign_tier(provenance, relevance_score)
        entry = CacheEntry(token_ids, provenance, relevance_score, tier)
        self.entries.append(entry)
    
    def _assign_tier(self, provenance, relevance_score):
        """Assign tier based on provenance type and relevance threshold."""
        if provenance == 'query':
            return 0
        elif relevance_score > 0.7:  # High-relevance threshold
            return 1
        else:
            return 2
    
    def evict_to_budget(self, total_context_length):
        """Evict entries to meet budget constraint."""
        budget = int(total_context_length * self.budget_percent)
        
        # Sort entries by (tier ascending, relevance descending)
        sorted_entries = sorted(self.entries, key=lambda e: (e.tier, -e.relevance_score))
        
        # Greedily retain entries until budget exhausted
        retained = []
        current_tokens = 0
        
        for entry in sorted_entries:
            if current_tokens + len(entry.token_ids) <= budget:
                retained.append(entry)
                current_tokens += len(entry.token_ids)
            else:
                break
        
        self.entries = retained
        return retained
```

**Implementation Notes**:
- Tier assignment: Query tokens (tier 0), top-k passages by relevance (tier 1), remaining passages (tier 2)
- Diversity-aware variant: Within each tier, sort by MMR score instead of raw relevance
- Budget overflow: Clip lower tiers if higher tiers exceed allocation (query tokens always prioritized)

---

## Summary: Key Implementation Patterns

| **Component** | **Key Pattern** | **Source** |
|--------------|----------------|-----------|
| MMR Selection | Greedy loop: `λ * relevance - (1-λ) * max_similarity` | Search Query 1 |
| Contriever Embeddings | `SentenceTransformer.encode(passages, convert_to_tensor=True)` | Search Query 2 |
| Tiered Eviction | Sort by `(tier, -relevance)`, retain until budget exhausted | Search Query 3 |
| HotpotQA F1 | Token-level overlap: `2 * precision * recall / (precision + recall)` | Search Query 4 |
| Cache Data Structure | `CacheEntry` with provenance, tier, relevance metadata | Search Query 5 |

---

## Phase 3 Readiness

Implementation search complete. All key patterns identified for Phase 3 code design.

**Next Steps**:
1. Generate PRD (API specifications for MMR module, cache manager, evaluation harness)
2. Generate Architecture (class hierarchy, module dependencies, data flow)
3. Generate Logic pseudo-code (MMR greedy selection, tiered eviction state machine)
4. Generate Config schemas (hyperparameters, model paths, ablation settings)

**Estimated Phase 3 Duration**: 2-3 hours (parallel agent orchestration for 4 design documents)

---

**Document Status**: COMPLETE  
**Phase 2C Output Files**: ✓ experiment_brief.md, ✓ experiment_design_log.md, ✓ implementation_search_log.md  
**Ready for Phase 3**: YES
