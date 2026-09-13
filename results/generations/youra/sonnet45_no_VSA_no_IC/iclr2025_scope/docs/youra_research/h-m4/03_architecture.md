# Architecture: h-m4 Adaptive KV Cache

**Date:** 2026-08-20  
**Hypothesis:** Adaptive cache (grow/shrink based on retrieval density) matches static 25% cache accuracy while using ≤20% budget on average  
**Applied Pattern:** DynamicKV progressive budgeting, H2O eviction oracle (from h-m1)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (extends h-m1)  
**Status:** Reusing H2O baseline + data loader from h-m1  
**Analyzed Path:** docs/youra_research/h-m1/code/  
**Findings:** H2OCache and LongBenchLoader verified in actual code, will be imported directly

---

## System Overview

Single-script comparison: H2O baseline (static 25%) vs AdaptiveKVCache (dynamic 10-30%) on LongBench TriviaQA.

**Data Flow:**
```
LongBench TriviaQA → Generate with cache policy → F1 eval → Budget tracking
```

**Core Components:**
1. AdaptiveKVCache (new, retrieval density-based sizing)
2. H2OCache baseline (from h-m1)
3. LongBench loader (from h-m1)
4. F1 evaluation
5. Budget visualization

---

## Module Specifications

### AdaptiveKVCache (`adaptive_cache.py`)

**Dependencies:** torch, h-m1 H2OCache

```python
class AdaptiveKVCache:
    def __init__(self, base_budget: float = 0.25, min_budget: float = 0.10, max_budget: float = 0.30, window_size: int = 10): ...
    def update_retrieval_density(self, passage_ids: list[str]) -> float: ...
    def evict(self, k: Tensor, v: Tensor, max_len: int) -> tuple[Tensor, Tensor]: ...
    def get_current_budget(self) -> float: ...
```

### Evaluation (`evaluate.py`)

**Dependencies:** scipy

```python
def compute_f1(prediction: str, ground_truth: str) -> float: ...
def run_comparison(h2o_results: list[dict], adaptive_results: list[dict]) -> dict: ...
```

### Visualization (`visualize.py`)

**Dependencies:** matplotlib

```python
def plot_f1_comparison(h2o_f1: float, adaptive_f1: float, save_path: str): ...
def plot_budget_over_time(budgets: list[float], save_path: str): ...
def plot_density_vs_budget(densities: list[float], budgets: list[float], save_path: str): ...
def plot_cumulative_avg_budget(budgets: list[float], save_path: str): ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| H2OCache | `from h_m1_code.cache_policy import H2OCache, H2OCacheConfig` | `docs/youra_research/h-m1/code/cache_policy.py` |
| LongBenchLoader | `from h_m1_code.data import LongBenchLoader` | `docs/youra_research/h-m1/code/data.py` |

**Verified from:** docs/youra_research/h-m1/code/ (actual implementation)

**Note:** Add h-m1/code to Python path in main.py:
```python
import sys
sys.path.insert(0, '/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_scope/docs/youra_research/h-m1/code')
from cache_policy import H2OCache, H2OCacheConfig
from data import LongBenchLoader
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup | Environment + model download | 6 | 1(deps)+2(llama)+2(verify-h2o)+1(path) |
| A-2 | AdaptiveCache | Implement density tracking + eviction | 12 | 3(density)+4(evict)+3(budget-adjust)+2(test) |
| A-3 | Data | LongBench TriviaQA loading | 5 | 2(import-loader)+2(load)+1(validate) |
| A-4 | Generation | Run both policies on ~200 samples | 10 | 3(h2o-run)+3(adaptive-run)+2(collect)+2(save) |
| A-5 | Evaluation | F1 + budget metrics + stats | 9 | 3(f1)+2(budget-calc)+2(stats)+2(test) |
| A-6 | Visualization | 4 required plots | 8 | 2(f1-bar)+2(budget-time)+2(density-scatter)+2(cumulative) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-2, A-4, A-5], Low(4-8): [A-1, A-3, A-6]

---

## Adaptive Cache Implementation

### Density Tracking

```python
class AdaptiveKVCache:
    def __init__(self, base_budget=0.25, min_budget=0.10, max_budget=0.30, window_size=10):
        self.base_budget = base_budget
        self.min_budget = min_budget
        self.max_budget = max_budget
        self.window_size = window_size
        self.current_budget = base_budget
        self.passage_history = []  # Sliding window of passage IDs
        self.h2o_evict = H2OCache(H2OCacheConfig(cache_budget_ratio=base_budget))
    
    def update_retrieval_density(self, passage_ids: list[str]) -> float:
        """Update density metric from retrieval event."""
        self.passage_history.extend(passage_ids)
        if len(self.passage_history) > self.window_size:
            self.passage_history = self.passage_history[-self.window_size:]
        
        unique_count = len(set(self.passage_history))
        density = unique_count / min(len(self.passage_history), self.window_size)
        
        # Adaptive budget adjustment
        if density > 0.7:
            self.current_budget = min(self.current_budget * 1.1, self.max_budget)
        elif density < 0.3:
            self.current_budget = max(self.current_budget * 0.9, self.min_budget)
        
        return density
    
    def evict(self, k: Tensor, v: Tensor, max_len: int) -> tuple[Tensor, Tensor]:
        """Use H2O eviction with adaptive budget."""
        self.h2o_evict.cache_budget_ratio = self.current_budget
        return self.h2o_evict.evict(k, v, max_len)
```

### Budget Adjustment Logic

**High density (>0.7):** Many unique passages → grow cache to retain more context  
**Low density (<0.3):** Few unique passages → shrink cache to save memory  
**Base budget:** 25% (matching H2O baseline)

---

## Integration Strategy

### H2O Baseline Reuse

**Source:** h-m1/code/cache_policy.py  
**Pattern:** Import H2OCache, use as eviction backend for adaptive cache

**Key difference:** Static H2O uses fixed 25% budget, Adaptive adjusts 10-30% based on density.

### Data Loading

**Source:** h-m1/code/data.py  
**Reuse:** LongBenchLoader class directly (no modifications needed)

---

## File Structure

```
h-m4/code/
├── adaptive_cache.py    # AdaptiveKVCache implementation
├── evaluate.py          # F1 scoring + budget metrics
├── visualize.py         # 4 plots (F1, budget-time, density-scatter, cumulative)
├── main.py              # Orchestration (import h-m1 modules)
└── requirements.txt
```

---

**Total Complexity:** 50 (low-moderate, reusing h-m1 baseline reduces overhead)  
**Critical Path:** A-2 (AdaptiveCache) → A-4 (generation) → A-5 (evaluation) → A-6 (viz)
