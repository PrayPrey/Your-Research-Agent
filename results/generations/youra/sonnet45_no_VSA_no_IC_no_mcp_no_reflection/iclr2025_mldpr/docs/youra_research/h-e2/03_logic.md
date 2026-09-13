# Logic Specification: h-e2

**Date:** 2026-08-28
**Hypothesis:** Velocity Decay Detection via Linear Regression
**Type:** EXISTENCE (Proof-of-Concept)
**Budget:** 5 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation from scratch
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation following h-e1 pattern (PWC API → validation → report)

---

## A-1: Data Loading [Complexity: 8, Budget: 1]

**Applied:** Standard pandas/PWC API pattern

### API Signatures

```python
from pathlib import Path
from typing import Optional
import pandas as pd

def load_pwc_benchmark(benchmark_id: str, cache_dir: Optional[Path] = None) -> pd.DataFrame:
    """Fetch PWC benchmark data. Returns: DataFrame with columns ['date', 'score', 'model', 'paper']"""
    ...

def preprocess_leaderboard(df: pd.DataFrame) -> pd.DataFrame:
    """Clean data. df: [N rows x 4 cols] -> [M rows x 2 cols where M<=N]. Keeps date, score only."""
    ...
```

### Data Schema

| Column | Type | Note |
|--------|------|------|
| date | datetime64 | Submission timestamp |
| score | float64 | Benchmark metric |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | PWC fetch + pandas clean | API call, type conversion, dedup, sort |

---

## A-2: Core Detector [Complexity: 12, Budget: 2]

**Applied:** scipy.stats linregress + rolling window pattern

### API Signatures

```python
from typing import Tuple, List, Optional
import pandas as pd

class VelocityDecayDetector:
    def __init__(self, window_days: int = 180, threshold: float = 0.1):
        """Initialize detector. window_days: rolling window size, threshold: velocity limit (improvement/month)"""
        ...

    def detect(
        self, df: pd.DataFrame
    ) -> Tuple[Optional[pd.Timestamp], List[Tuple[pd.Timestamp, float, float]]]:
        """Detect decay. df: [N, 2] -> (first_decay_date, velocities). velocities: [(date, velocity, p_value)]"""
        ...

    def _compute_velocity(self, window: pd.DataFrame) -> Tuple[float, float]:
        """Compute slope. window: [K, 2] -> (monthly_velocity, p_value). K >= 10."""
        ...
```

### Pseudo-code

```
detect(df):
    velocities = []
    for each row i in df:
        window = df[(df.date >= i.date - 180d) & (df.date <= i.date)]
        if len(window) < 10: skip
        
        velocity, p = _compute_velocity(window)
        velocities.append((i.date, velocity, p))
        
        if velocity < threshold AND p < 0.05:
            return i.date, velocities
    
    return None, velocities

_compute_velocity(window):
    x = (window.date - window.date.min()).dt.days  # [K] days since start
    y = window.score  # [K] scores
    slope, _, _, p_value, _ = scipy.stats.linregress(x, y)
    return slope * 30, p_value  # daily -> monthly
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | VelocityDecayDetector class | __init__, detect, _compute_velocity |
| L-2-2 | Rolling window loop | Iterate rows, filter 180d windows, detect first decay |

---

## A-3: Baseline [Complexity: 5, Budget: 1]

**Applied:** Simple heuristic

### API Signatures

```python
def manual_inspection_baseline(df: pd.DataFrame) -> Optional[pd.Timestamp]:
    """Naive baseline. df: [N, 2] -> first_decay_date. Rule: 6mo with <1% total improvement."""
    ...
```

### Pseudo-code

```
for i in range(len(df) - 180):
    window = df[i : i+180]
    total_change = window.score[-1] - window.score[0]
    if total_change < 0.01 * window.score[0]:
        return window.date[0]
return None
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Baseline heuristic | Single-function 6mo window check |

---

## A-4: Metrics [Complexity: 6, Budget: 0]

**Applied:** Standard numpy stats

**Note:** SKIPPED - exceeds budget. Inline in main.py validation step.

---

## A-5: Visualization [Complexity: 9, Budget: 0]

**Applied:** matplotlib.pyplot

**Note:** SKIPPED - exceeds budget. Defer to Phase 4 if needed for validation.

---

## A-6: Pipeline [Complexity: 7, Budget: 1]

**Applied:** h-e1 orchestration pattern

### API Signatures

```python
from pathlib import Path
from typing import Dict

def run_experiment(benchmark_id: str, output_dir: Path) -> Dict:
    """Run full pipeline. Returns: {'detection_success': bool, 'first_decay_date': Optional[pd.Timestamp], 'stability_cv': float}"""
    ...

def main():
    """CLI entry point."""
    ...
```

### Pseudo-code

```
run_experiment(benchmark_id, output_dir):
    df = load_pwc_benchmark(benchmark_id)
    df = preprocess_leaderboard(df)
    
    detector = VelocityDecayDetector(window_days=180, threshold=0.1)
    first_decay, velocities = detector.detect(df)
    
    baseline_date = manual_inspection_baseline(df)
    
    # Inline metrics
    detection_success = first_decay is not None
    velocity_vals = [v[1] for v in velocities]
    stability_cv = np.std(velocity_vals) / abs(np.mean(velocity_vals)) if velocity_vals else float('inf')
    p_vals = [v[2] for v in velocities]
    significance_ratio = sum(1 for p in p_vals if p < 0.05) / len(p_vals) if p_vals else 0.0
    
    return {
        'detection_success': detection_success,
        'first_decay_date': first_decay,
        'baseline_date': baseline_date,
        'stability_cv': stability_cv,
        'significance_ratio': significance_ratio
    }
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Pipeline orchestration | run_experiment + main, inline metrics computation |

---

## Budget Summary

| Task | Allocated | Used | Remaining |
|------|-----------|------|-----------|
| A-1 | 1 | 1 | 0 |
| A-2 | 2 | 2 | 0 |
| A-3 | 1 | 1 | 0 |
| A-4 | 0 | 0 | 0 |
| A-5 | 0 | 0 | 0 |
| A-6 | 1 | 1 | 0 |
| **Total** | **5** | **5** | **0** |

---

## Self-Validation

- [x] No ASCII diagrams
- [x] KB patterns noted (1 line each)
- [x] "Codebase Analysis (Serena)" section included
- [x] Docstrings <= 2 lines
- [x] Tensor shapes in code comments
- [x] Subtask count within budget (5/5)
- [x] Total length < 600 lines
- [x] Green-field project confirmed
