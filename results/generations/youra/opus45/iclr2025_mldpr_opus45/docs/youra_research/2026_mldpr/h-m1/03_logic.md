# Logic: h-m1 PELT Changepoint Detection

**Applied**: Standard ruptures PELT pattern (Archon KB: no domain-specific results; sourced from experiment brief + h-e1 actual code)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Serena MCP unavailable (no active project); API signatures verified via direct file reads of h-e1/code/
**Analyzed Path**: `docs/youra_research/20260325_mldpr/h-e1/code/`
**Relevant Symbols**:
- `collect_datasets(config)` → `List[Dict]` with keys `{"id": str, "series": np.ndarray}`
- `preprocess(raw_series)` → `np.ndarray` shape `[N, T, 1]` (tslearn 3D format - NOT reusable directly)
- `validate_data_quality(datasets, max_missing_ratio)` → `Tuple[bool, Dict]`
- Cache file: `hf_dataset_cache.json` co-located with code files
- `BaselineModel.fit(features, k)`, `DTWModel.fit(X, k)` - NOT reused in h-m1

---

## External Dependencies API (Base Hypothesis)

### API Signatures (From Actual Code)

Verified from `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_mldpr_opus45/docs/youra_research/20260325_mldpr/h-e1/code/data.py`:

```python
# From: h-e1/code/data.py (ACTUAL CODE)

def collect_datasets(config: ExperimentConfig) -> List[Dict]:
    """Returns list of {"id": str, "series": np.ndarray} (1D raw flux values)."""
    # Cache file: os.path.join(os.path.dirname(__file__), "hf_dataset_cache.json")
    ...

def preprocess(raw_series: List[np.ndarray]) -> np.ndarray:
    """Returns [N, T, 1] tslearn 3D format - NOT compatible with ruptures."""
    # Uses tslearn TimeSeriesScalerMeanVariance + to_time_series_dataset
    ...

def validate_data_quality(
    datasets: List[Dict],
    max_missing_ratio: float = 0.1
) -> Tuple[bool, Dict]:
    """Returns (quality_passed: bool, report: Dict)."""
    ...
```

**Key Difference**: h-e1 `preprocess()` returns `[N, T, 1]` tslearn format. h-m1 must implement its own `preprocess_for_pelt()` returning `List[np.ndarray]` (1D per series) for ruptures compatibility.

**Cache reuse**: Load `hf_dataset_cache.json` from h-e1/code/ path, then apply h-m1's own preprocessing.

---

## A-1: Setup & Config [Complexity: 5, Budget: 1 subtask]

**Applied**: Standard dataclass config pattern

### API Signatures

```python
# h-m1/code/config.py
from dataclasses import dataclass, field

@dataclass
class ExperimentConfig:
    # Data
    min_series_length: int = 12
    target_n_series: int = 500
    random_state: int = 42

    # PELT parameters
    pelt_model: str = "l2"
    pelt_min_size: int = 3
    pelt_jump: int = 1

    # BIC penalty
    # pen = 2 * log(n) computed at runtime

    # CROPS grid search
    penalty_range: tuple = (1.0, 100.0)
    n_penalties: int = 20

    # Gate
    detection_rate_threshold: float = 0.50

    # Paths (set to absolute at runtime)
    figures_dir: str = "h-m1/figures"
    output_path: str = "h-m1/04_validation.md"
    cache_path: str = "../h-e1/code/hf_dataset_cache.json"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Config dataclass | ExperimentConfig with all fields above |

---

## A-2: Data Loading [Complexity: 9, Budget: 1 subtask]

**Applied**: Cache-first loading pattern from h-e1

### API Signatures

```python
# h-m1/code/data.py
import numpy as np
import json, os
from typing import List, Dict, Tuple
from config import ExperimentConfig

def load_series(config: ExperimentConfig) -> List[Dict]:
    """Load from h-e1 cache or re-collect via HuggingFace.
    Returns list of {"id": str, "series": np.ndarray} (1D raw values)."""
    ...

def preprocess_for_pelt(raw_series: List[np.ndarray]) -> List[np.ndarray]:
    """Log-transform + z-score per series.
    Input: List of 1D np.ndarray (raw). Output: List of 1D np.ndarray (preprocessed)."""
    # per series: shift to positive, log1p, z-score with epsilon guard
    ...

def validate_series(datasets: List[Dict]) -> Tuple[bool, Dict]:
    """Check length >= min_series_length, no NaN/Inf, sufficient count.
    Returns (passed: bool, report: Dict)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| raw_series list item | `(T,)` | 1D numpy, variable T |
| preprocessed list item | `(T,)` | log1p + z-score, same T |

### Pseudo-code for `preprocess_for_pelt`

```
for ts in raw_series:
    min_val = min(ts)
    if min_val <= 0: ts = ts - min_val + 1
    ts = log1p(ts)
    mu, sigma = mean(ts), std(ts)
    if sigma < 1e-10: sigma = 1.0  # constant series guard
    ts = (ts - mu) / sigma
    result.append(ts)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Data loading + preprocessing | load_series (cache-first), preprocess_for_pelt, validate_series |

---

## A-3: Baseline Models [Complexity: 7, Budget: 0 subtasks]

**Applied**: Null baseline pattern

### API Signatures

```python
# h-m1/code/model.py (BaselineDetector)
import numpy as np
from typing import List, Dict
from config import ExperimentConfig

class BaselineDetector:
    """Null baselines: random, none, fixed-interval."""

    def __init__(self, config: ExperimentConfig) -> None: ...

    def detect_random(self, series: np.ndarray) -> List[int]:
        """Place 0-4 changepoints uniformly at random. series: (T,) -> List[int]."""
        ...

    def detect_none(self, series: np.ndarray) -> List[int]:
        """Return [] (null model). series: (T,) -> []."""
        ...

    def detect_fixed_interval(
        self, series: np.ndarray, interval: int = 6
    ) -> List[int]:
        """Place changepoints at fixed intervals. series: (T,) -> List[int]."""
        ...

    def compute_detection_rate(
        self, all_series: List[np.ndarray], method: str = "random"
    ) -> float:
        """Proportion with >=1 changepoint across all_series. Returns float in [0,1]."""
        ...
```

---

## A-4: PELT Detector [Complexity: 12, Budget: 1 subtask]

**Applied**: ruptures.Pelt with BIC penalty + CROPS-style grid search

### API Signatures

```python
# h-m1/code/model.py (PELTDetector)
import ruptures as rpt
import numpy as np
from typing import List, Tuple
from config import ExperimentConfig

class PELTDetector:
    """PELT changepoint detection with BIC penalty."""

    def __init__(self, config: ExperimentConfig) -> None:
        # self.algo_params = {model, min_size, jump} from config
        ...

    def detect(self, series: np.ndarray) -> Tuple[List[int], float]:
        """Run PELT with BIC penalty on single series.
        series: (T,) -> (changepoints: List[int], optimal_penalty: float).
        changepoints excludes endpoint (result[:-1])."""
        ...

    def detect_all(
        self, all_series: List[np.ndarray]
    ) -> Tuple[List[List[int]], float]:
        """Apply PELT to all series.
        Returns (all_changepoints: List[List[int]], detection_rate: float)."""
        ...

    def penalty_sensitivity(
        self, series: np.ndarray
    ) -> List[Tuple[float, int, List[int]]]:
        """CROPS-style grid over penalty_range with n_penalties log-spaced values.
        Returns [(penalty, n_changepoints, changepoints)] sorted by penalty."""
        ...
```

### Pseudo-code for `detect`

```
algo = rpt.Pelt(model=config.pelt_model, min_size=config.pelt_min_size, jump=config.pelt_jump)
algo.fit(series)  # series: (T,)
n = len(series)
pen = 2 * log(n)  # BIC penalty
result = algo.predict(pen=pen)
changepoints = result[:-1]  # exclude endpoint T
return changepoints, pen
```

### Pseudo-code for `penalty_sensitivity`

```
algo = rpt.Pelt(...).fit(series)
penalties = logspace(log10(range[0]), log10(range[1]), n_penalties)
for pen in penalties:
    bkps = algo.predict(pen=pen)
    n_cps = len(bkps) - 1  # exclude endpoint
    results.append((pen, n_cps, bkps[:-1]))
return results
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | PELTDetector | detect, detect_all, penalty_sensitivity |

---

## A-5: Evaluation & Figures [Complexity: 10, Budget: 0 subtasks]

**Applied**: Standard gate metrics + matplotlib figures

### API Signatures

```python
# h-m1/code/evaluate.py
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict
from config import ExperimentConfig

def compute_gate_metrics(
    all_changepoints: List[List[int]],
    config: ExperimentConfig,
) -> Dict:
    """Returns {"detection_rate": float, "mean_cps": float, "gate_pass": bool}."""
    ...

def generate_figures(
    all_series: List[np.ndarray],
    all_changepoints: List[List[int]],
    baseline_rates: Dict[str, float],
    pelt_rate: float,
    config: ExperimentConfig,
) -> List[str]:
    """Generate 4 figures to figures_dir. Returns list of saved paths."""
    # 1. gate_metrics_bar.png - detection rate vs 50% threshold
    # 2. changepoint_distribution.png - histogram of cp counts
    # 3. example_series.png - 3-5 series with detected changepoints
    # 4. penalty_sensitivity.png - detection rate vs penalty (CROPS elbow)
    ...

def write_validation_report(results: Dict, config: ExperimentConfig) -> str:
    """Write 04_validation.md. Returns 'PASS' or 'FAIL'."""
    ...
```

---

## A-6: Integration & Run [Complexity: 8, Budget: 0 subtasks]

### API Signatures

```python
# h-m1/code/main.py
import sys
from config import ExperimentConfig
from data import load_series, preprocess_for_pelt, validate_series
from model import BaselineDetector, PELTDetector
from evaluate import compute_gate_metrics, generate_figures, write_validation_report

def run_experiment(config: ExperimentConfig) -> Dict:
    """Run full pipeline. Returns results dict with gate_pass key."""
    ...

if __name__ == "__main__":
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    config = ExperimentConfig(
        figures_dir=os.path.join(base, "..", "figures"),
        output_path=os.path.join(base, "..", "04_validation.md"),
        cache_path=os.path.join(base, "..", "..", "h-e1", "code", "hf_dataset_cache.json"),
    )
    results = run_experiment(config)
    sys.exit(0 if results["gate_pass"] else 1)
```

### Pseudo-code for `run_experiment`

```
1. datasets = load_series(config)
2. _, quality = validate_series(datasets)
3. raw = [d["series"] for d in datasets]
4. preprocessed = preprocess_for_pelt(raw)

5. baseline = BaselineDetector(config)
6. baseline_rates = {
     "random": baseline.compute_detection_rate(preprocessed, "random"),
     "none": 0.0,
     "fixed": baseline.compute_detection_rate(preprocessed, "fixed_interval"),
   }

7. pelt = PELTDetector(config)
8. all_changepoints, pelt_rate = pelt.detect_all(preprocessed)

9. metrics = compute_gate_metrics(all_changepoints, config)
10. figure_paths = generate_figures(preprocessed, all_changepoints,
                                    baseline_rates, pelt_rate, config)
11. gate_result = write_validation_report({**metrics, **baseline_rates,
                                           "figure_paths": figure_paths}, config)
12. return {**metrics, "gate_pass": metrics["gate_pass"]}
```

---

## Subtask Summary [3/3 budget used]

| ID | Task | Subtask | Description |
|----|------|---------|-------------|
| L-1-1 | A-1 | Config dataclass | ExperimentConfig |
| L-2-1 | A-2 | Data loading + preprocessing | load_series, preprocess_for_pelt, validate_series |
| L-4-1 | A-4 | PELTDetector | detect, detect_all, penalty_sensitivity |
