# Logic Design Document: h-m2 Temporal Lead Time Validation

**Hypothesis ID:** h-m2  
**Type:** MECHANISM  
**Date:** 2026-08-28  
**Subtask Budget:** 2 tasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Extends h-m1 saturation detection with temporal validation  
**Analyzed Path:** docs/youra_research/h-m1/code/  
**Relevant Symbols:** run_convergence_experiment, ConvergenceDetector.detect_first_convergence

---

## Applied Patterns

Applied: **API Integration Pattern** (rate-limited external data fetch)  
Applied: **Temporal Alignment Analysis** (offset computation between event dates)

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

h-m2 reads h-m1 results directly from JSON (no function calls).

```python
# From: docs/youra_research/h-m1/results/convergence_results.json
# Schema verified from actual output:
{
  "results": {
    "imagenet": {
      "convergence_date": "2015-08",  # str, format: YYYY-MM
      "final_std": 0.010547,           # float
      "threshold": 0.012,              # float
      "validation": {
        "significant": true,           # bool
        "pvalue": 1.5e-08             # float
      }
    }
  },
  "converged_count": 3,
  "gate_pass": true
}
```

**Verified from:** docs/youra_research/h-m1/results/convergence_results.json (actual output)

---

## M2-1: Citation Data Fetching [Complexity: 8]

Applied: **API Integration Pattern**

### API Signatures

```python
from pathlib import Path
import requests
import time
import json
import pandas as pd
from typing import Dict

class CitationFetcher:
    def __init__(self, cache_dir: Path, rate_limit: tuple = (100, 300)):
        """rate_limit: (requests, seconds)"""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_requests, self.window_seconds = rate_limit
        self.request_times = []
    
    def fetch_citations(self, paper_id: str, force_refresh: bool = False) -> pd.DataFrame:
        """
        Fetch monthly citation counts from Semantic Scholar.
        Returns: df[date: str, citations: int]
        """
        pass
    
    def _api_call(self, paper_id: str) -> dict:
        """GET /paper/{paper_id}/citations. Returns: raw API response."""
        pass
    
    def _rate_limit_sleep(self) -> None:
        """Sleep if request rate exceeds limit."""
        pass
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | API client + caching | requests.get(), JSON cache read/write |
| L-1-2 | Rate limiter | Token bucket pattern, sleep injection |

---

## M2-2: Adoption Date Detection [Complexity: 7]

Applied: **Temporal Alignment Analysis**

### API Signatures

```python
import pandas as pd
import numpy as np
from typing import Optional

class AdoptionDetector:
    def __init__(self, threshold: int = 50, window: int = 3):
        """threshold: citations/month, window: sustained months"""
        self.threshold = threshold
        self.window = window
    
    def detect_adoption_date(self, citation_timeseries: pd.DataFrame) -> Optional[str]:
        """
        Find first month where citations >= threshold for window months.
        citation_timeseries: df[date: str, citations: int]
        Returns: adoption_date (YYYY-MM) or None
        """
        pass
    
    def smooth_citations(self, df: pd.DataFrame) -> pd.Series:
        """3-month rolling average. Returns: series[date -> citations]"""
        pass
```

### Pseudo-code

```
1. smooth = df['citations'].rolling(window=3).mean()
2. mask = smooth >= threshold
3. streak_start = None
4. for i, is_above in enumerate(mask):
       if is_above and streak_start is None:
           streak_start = i
       elif not is_above:
           streak_start = None
       if streak_start and (i - streak_start + 1) >= window:
           return df.iloc[streak_start]['date']
5. return None
```

### Subtasks [0/0 used]

(No subtask allocation - standalone task)

---

## Integration Points

### Data Flow

```
h-m1/results/convergence_results.json
    ↓
saturation_dates = {benchmark: convergence_date}
    ↓
Semantic Scholar API → CitationFetcher → data/citations/{paper_id}.json
    ↓
AdoptionDetector → shift_adoption_dates.json
    ↓
lead_times = [(benchmark, shift, adoption_date - saturation_date)]
    ↓
Gate: precede_fraction >= 0.6 AND mean_lead > 6
```

### Output Schema

```python
# data/shift_adoption_dates.json
{
  "gpt3": "2020-08",
  "vit": "2021-10",
  "llama": "2023-03"
}

# results/lead_times.json
{
  "pairs": [
    {
      "benchmark": "imagenet",
      "shift": "vit",
      "saturation_date": "2015-08",
      "adoption_date": "2021-10",
      "lead_time_months": 74
    }
  ],
  "precede_fraction": 0.67,
  "mean_lead_time": 48.3,
  "gate_pass": true
}
```

---

## Tensor Shapes (N/A)

No tensor operations - pure pandas/numpy time-series analysis.

---

## Configuration

```python
# Hardcoded constants (LIGHT tier)
PAPERS = {
    'gpt3': '2020.01109',
    'vit': '2010.11929',
    'llama': '2302.13971'
}

BENCHMARK_SHIFT_PAIRS = [
    ('imagenet', 'vit'),
    ('glue', 'gpt3'),
    ('squad', 'gpt3')
]

ADOPTION_THRESHOLD = 50  # citations/month
ADOPTION_WINDOW = 3      # sustained months
LEAD_TIME_THRESHOLD = 6  # months
RATE_LIMIT = (100, 300)  # 100 req/5min
```

---

## Next Steps

**Phase 4 Implementation Order:**
1. M2-1: Citation fetching (prerequisite)
2. M2-2: Adoption detection (core mechanism)
3. main_experiment.py: Load h-m1 JSON, compute lead times, gate evaluation

**Document Status:** READY FOR PHASE 4
