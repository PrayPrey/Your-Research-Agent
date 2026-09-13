# Logic Specifications: h-m4 Adaptive KV Cache

**Date:** 2026-08-20  
**Hypothesis:** Adaptive cache matches static 25% F1 while using ≤20% budget on average  
**Budget:** 3 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (extends h-m1)  
**Status:** Reusing H2OCache + LongBenchLoader from h-m1  
**Analyzed Path:** docs/youra_research/h-m1/code/  
**Relevant Symbols:** H2OCache, H2OCacheConfig, LongBenchLoader (verified from actual code)

**Critical Finding:** H2O parameter is `cache_budget_ratio` (not `budget_ratio` as in spec).

---

## A-2: AdaptiveKVCache (Complexity: 12, Budget: 3)

**Applied:** Sliding window density tracking + H2O backend

### API Signatures

```python
class AdaptiveKVCache:
    def __init__(
        self,
        base_budget: float = 0.25,
        min_budget: float = 0.10,
        max_budget: float = 0.30,
        window_size: int = 10
    ):
        """Initialize adaptive cache. base_budget: matching H2O baseline."""
        self.base_budget = base_budget
        self.min_budget = min_budget
        self.max_budget = max_budget
        self.window_size = window_size
        self.current_budget = base_budget
        self.passage_history: List[str] = []
        
        # H2O backend (verified API from h-m1 actual code)
        from cache_policy import H2OCache, H2OCacheConfig
        self.h2o_backend = H2OCache(H2OCacheConfig(
            cache_budget_ratio=base_budget  # Note: cache_budget_ratio (not budget_ratio)
        ))
    
    def update_density(self, passage_ids: List[str]) -> float:
        """Update retrieval density. Returns: density in [0,1]"""
        # passage_ids: [P1, P2, ...] from latest retrieval event
        ...
    
    def evict(self, k: Tensor, v: Tensor, max_len: int) -> Tuple[Tensor, Tensor]:
        """Evict using H2O with adaptive budget. k, v: [B, H, L, D] -> [B, H, L', D]"""
        ...
    
    def get_budget(self) -> float:
        """Return current budget for tracking."""
        return self.current_budget
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| k, v | [B, H, L, D] | Batch × Heads × Seq × Dim |
| passage_history | [W] | Sliding window of passage IDs |
| density | scalar | unique / window_size |

### Pseudo-code

```
UPDATE_DENSITY:
INPUT: passage_ids [P1, P2, ...]
OUTPUT: density (float)

1. passage_history.extend(passage_ids)
2. IF len(passage_history) > window_size:
     passage_history = passage_history[-window_size:]
3. unique_count = len(set(passage_history))
4. density = unique_count / len(passage_history)

5. Adjust budget:
   IF density > 0.7:
     current_budget = min(current_budget * 1.1, max_budget)
   ELIF density < 0.3:
     current_budget = max(current_budget * 0.9, min_budget)

6. RETURN density

EVICT:
INPUT: k [B, H, L, D], v [B, H, L, D], max_len
OUTPUT: k' [B, H, L', D], v' [B, H, L', D]

1. h2o_backend.cache_budget_ratio = current_budget
2. RETURN h2o_backend.evict(k, v, max_len)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Density tracking | Sliding window + unique count |
| L-2-2 | Budget adjustment | Growth/shrink thresholds |
| L-2-3 | H2O delegation | Update ratio + call evict |

---

## A-5: Evaluation (Complexity: 9, Budget: 0)

**Applied:** Token-level F1 from LongBench standard

### API Signatures

```python
def compute_f1(prediction: str, ground_truth: str) -> float:
    """F1: token overlap. Returns: [0,1]"""
    ...

def run_comparison(
    h2o_results: List[Dict],
    adaptive_results: List[Dict]
) -> Dict:
    """Statistical test. Returns: {'h2o_f1', 'adaptive_f1', 'avg_budget', 'p_value'}"""
    ...
```

### Pseudo-code

```
COMPUTE_F1:
1. pred_tokens = prediction.split()
2. gt_tokens = ground_truth.split()
3. common = Counter(pred_tokens) & Counter(gt_tokens)
4. IF sum(common) == 0: RETURN 0.0
5. precision = sum(common) / len(pred_tokens)
6. recall = sum(common) / len(gt_tokens)
7. RETURN 2 * precision * recall / (precision + recall)

RUN_COMPARISON:
1. h2o_scores = [compute_f1(r['pred'], r['gt']) for r in h2o_results]
2. adaptive_scores = [compute_f1(r['pred'], r['gt']) for r in adaptive_results]
3. avg_budget = mean([r['budget'] for r in adaptive_results])
4. p_value = ttest_rel(adaptive_scores, h2o_scores).pvalue
5. RETURN {'h2o_f1': mean(h2o_scores), 'adaptive_f1': mean(adaptive_scores), 
           'avg_budget': avg_budget, 'p_value': p_value}
```

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

**Verified from:** /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_scope/docs/youra_research/h-m1/code/

```python
# From: h-m1/code/cache_policy.py (ACTUAL CODE)
@dataclass
class H2OCacheConfig:
    heavy_ratio: float = 0.125
    recent_ratio: float = 0.125
    n_sink: int = 4
    cache_budget_ratio: float = 0.25  # ← Actual parameter name!

class H2OCache:
    def __init__(self, config: H2OCacheConfig):
        """Initialize with config."""
        self.cache_budget_ratio = config.cache_budget_ratio  # ← Mutable!
        ...
    
    def update_attention_scores(self, attention_weights: Tensor) -> None:
        """attention_weights: [B, H, Lq, Lkv]"""
        ...
    
    def evict(self, k: Tensor, v: Tensor, max_len: int) -> Tuple[Tensor, Tensor]:
        """k, v: [B, H, L, D] -> [B, H, L', D]"""
        ...

# From: h-m1/code/data.py (ACTUAL CODE)
class LongBenchLoader:
    def __init__(
        self,
        tasks: List[str],
        tokenizer_name: str,
        max_context_length: int = 4096
    ):
        """Load LongBench dataset."""
        ...
    
    def load(self) -> List[Dict]:
        """Returns: [{'input', 'context', 'answers', 'task'}]"""
        ...
    
    def preprocess_sample(self, sample: Dict) -> Dict:
        """Truncate context to max_context_length."""
        ...
```

**Import Pattern:**

```python
import sys
sys.path.insert(0, '/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_scope/docs/youra_research/h-m1/code')
from cache_policy import H2OCache, H2OCacheConfig
from data import LongBenchLoader
```

---

## Budget Summary

| Task | Allocated | Used | Remaining |
|------|-----------|------|-----------|
| A-2 (AdaptiveCache) | 12 | 3 | 9 |
| A-5 (Evaluation) | 9 | 0 | 9 |
| **Total** | **21** | **3** | **18** |

---

**Applied:** Sliding window tracking, H2O eviction backend, token-level F1  
**Green-field for AdaptiveKVCache, reuses h-m1 H2O + LongBench**
