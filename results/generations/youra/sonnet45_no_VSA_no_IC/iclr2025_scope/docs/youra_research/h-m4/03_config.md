# Configuration for H-M4 Adaptive KV Cache

**Hypothesis**: h-m4  
**Type**: MECHANISM  
**Date**: 2026-08-20

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m1)  
**Status**: Reuses H2O baseline + LongBench loader from h-m1  
**Config Files Found**: h-m1/code/cache_policy.py (verified dataclasses)  
**Pattern Used**: Python dataclass (minimal hardcoded dict for adaptive params)

**Applied**: PyTorch defaults, h-m1 H2OCacheConfig inheritance

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from base hypothesis h-m1:

```python
# From: docs/youra_research/h-m1/code/cache_policy.py (ACTUAL CODE)
@dataclass
class H2OCacheConfig:
    heavy_ratio: float = 0.125
    recent_ratio: float = 0.125
    n_sink: int = 4
    cache_budget_ratio: float = 0.25
```

**Verified from**: docs/youra_research/h-m1/code/cache_policy.py (actual implementation)

---

## Configuration (Python Dataclass)

### AdaptiveCacheConfig

```python
from dataclasses import dataclass
from h_m1_code.cache_policy import H2OCacheConfig

@dataclass
class AdaptiveCacheConfig:
    """Adaptive cache sizing based on retrieval density"""
    base_budget: float = 0.25
    min_budget: float = 0.10
    max_budget: float = 0.30
    window_size: int = 10
    density_threshold_high: float = 0.7
    density_threshold_low: float = 0.3
    growth_factor: float = 1.1
    shrink_factor: float = 0.9
    h2o_config: H2OCacheConfig = None
    
    def __post_init__(self):
        if self.h2o_config is None:
            self.h2o_config = H2OCacheConfig(cache_budget_ratio=self.base_budget)
```

---

## Experiment Configuration (Hardcoded Dict)

```python
EXPERIMENT_CONFIG = {
    "seed": 42,
    "dataset": "THUDM/LongBench",
    "task": "triviaqa",
    "split": "test",
    "num_samples": 200,
    "model": "meta-llama/Llama-2-7b-hf",
    "dtype": "float16",
    "device": "auto",
    "generation": {
        "max_new_tokens": 100,
        "temperature": 0.0,
        "do_sample": False
    },
    "output_dir": "docs/youra_research/h-m4/figures"
}
```

---

## Evaluation Configuration (Hardcoded Dict)

```python
EVAL_CONFIG = {
    "metrics": ["f1", "avg_cache_budget"],
    "statistical_test": {
        "method": "ttest_ind",
        "alternative": "greater",
        "alpha": 0.05
    },
    "success_criteria": {
        "f1": "adaptive_f1 >= h2o_f1",
        "avg_budget": "<= 0.20"
    },
    "figures": [
        "f1_comparison",
        "budget_over_time",
        "density_vs_budget",
        "cumulative_avg_budget"
    ]
}
```

---

## Visualization Configuration (Hardcoded Dict)

```python
VIZ_CONFIG = {
    "format": "png",
    "dpi": 300,
    "figsize": (10, 6),
    "style": "seaborn-v0_8-whitegrid",
    "colors": {
        "h2o": "#1f77b4",
        "adaptive": "#ff7f0e",
        "threshold": "#d62728"
    }
}
```

---

## Hyperparameter Rationale

**Non-standard values only:**

- **window_size: 10**: Sliding window for density tracking (balances responsiveness vs stability)
- **density_threshold_high: 0.7**: Trigger cache growth when 70%+ unique passages (high diversity)
- **density_threshold_low: 0.3**: Trigger cache shrink when <30% unique passages (low diversity)
- **growth_factor: 1.1**: Conservative 10% growth per step (prevents overshooting)
- **shrink_factor: 0.9**: Conservative 10% shrink per step (prevents undershooting)

---

## Usage Example

```python
import sys
sys.path.insert(0, '/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_scope/docs/youra_research/h-m1/code')

from cache_policy import H2OCache, H2OCacheConfig
from dataclasses import dataclass

@dataclass
class AdaptiveCacheConfig:
    base_budget: float = 0.25
    min_budget: float = 0.10
    max_budget: float = 0.30
    window_size: int = 10
    density_threshold_high: float = 0.7
    density_threshold_low: float = 0.3
    growth_factor: float = 1.1
    shrink_factor: float = 0.9
    h2o_config: H2OCacheConfig = None
    
    def __post_init__(self):
        if self.h2o_config is None:
            self.h2o_config = H2OCacheConfig(cache_budget_ratio=self.base_budget)

# Create configs
adaptive_cfg = AdaptiveCacheConfig()
h2o_baseline_cfg = H2OCacheConfig(cache_budget_ratio=0.25)

# Use in experiment
from adaptive_cache import AdaptiveKVCache
cache = AdaptiveKVCache(
    base_budget=adaptive_cfg.base_budget,
    min_budget=adaptive_cfg.min_budget,
    max_budget=adaptive_cfg.max_budget,
    window_size=adaptive_cfg.window_size
)
```

---

## File Locations

```
h-m4/code/
├── adaptive_cache.py    # AdaptiveKVCache implementation
├── evaluate.py          # F1 + budget metrics
├── visualize.py         # 4 plots
├── main.py              # Orchestration (imports h-m1 modules)
└── requirements.txt
```

---

**Config Status**: COMPLETE  
**Ready for Phase 4**: YES  
**Format**: Python dataclass (AdaptiveCacheConfig) + hardcoded dicts (experiment/eval/viz)  
**Base Hypothesis**: h-m1 (verified) - reuses H2OCacheConfig
