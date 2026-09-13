# Architecture: h-e1 - DTW Time Series Clustering

**Hypothesis**: EXISTENCE - DTW clustering of HuggingFace dataset download trajectories
**Type**: PoC (minimal structure)
**Date**: 2026-03-27

Applied: modular-pipeline pattern (tslearn clustering)
Applied: flat-file EXISTENCE PoC structure

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Findings**: New implementation from scratch; no base hypothesis code exists

---

## File Structure

- `h-e1/code/config.py` - Single fixed config dataclass
- `h-e1/code/data.py` - HuggingFace API collection + preprocessing
- `h-e1/code/model.py` - Baseline KMeans + DTW TimeSeriesKMeans
- `h-e1/code/evaluate.py` - Silhouette, Jaccard bootstrap, visualization
- `h-e1/code/main.py` - Orchestration entry point

---

## Module Definitions

### Config (`h-e1/code/config.py`)

**Dependencies**: none

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    k_range: tuple = (3, 8)
    max_iter: int = 10
    n_init: int = 2
    random_state: int = 42
    n_bootstrap: int = 100
    bootstrap_ratio: float = 0.8
    min_downloads: int = 100
    min_months: int = 12
    target_n_datasets: int = 500
    figures_dir: str = "h-e1/figures"
    output_path: str = "h-e1/04_validation.md"
```

---

### DataModule (`h-e1/code/data.py`)

**Dependencies**: Config

```python
import numpy as np
from typing import List, Tuple
from h_e1.code.config import ExperimentConfig

def collect_datasets(config: ExperimentConfig) -> List[dict]: ...
    # HfApi().list_datasets(full=True), filter by date/downloads/months
    # Checkpoint raw results; handle rate limits
    # Returns list of {"id": str, "series": np.ndarray}

def preprocess(raw_series: List[np.ndarray]) -> np.ndarray: ...
    # np.log1p -> to_time_series_dataset -> TimeSeriesScalerMeanVariance
    # Returns 3D array (n_samples, max_len, 1)

def extract_features(series_list: List[np.ndarray]) -> np.ndarray: ...
    # Per-series: [mean, std, trend_slope via np.polyfit]
    # Returns 2D array (n_samples, 3)
```

---

### Models (`h-e1/code/model.py`)

**Dependencies**: Config

```python
import numpy as np
from typing import Tuple
from sklearn.cluster import KMeans
from tslearn.clustering import TimeSeriesKMeans
from h_e1.code.config import ExperimentConfig

class BaselineModel:
    def __init__(self, config: ExperimentConfig): ...
    def fit(self, features: np.ndarray, k: int) -> np.ndarray: ...
        # KMeans(n_clusters=k, random_state=config.random_state).fit_predict
    def best_k_silhouette(
        self, features: np.ndarray
    ) -> Tuple[int, float, np.ndarray]: ...
        # Iterate k in config.k_range, return (best_k, best_score, best_labels)

class DTWModel:
    def __init__(self, config: ExperimentConfig): ...
    def fit(self, X: np.ndarray, k: int) -> TimeSeriesKMeans: ...
        # TimeSeriesKMeans(n_clusters=k, metric="dtw",
        #   max_iter=config.max_iter, n_init=config.n_init,
        #   random_state=config.random_state)
    def best_k_silhouette(
        self, X: np.ndarray
    ) -> Tuple[int, float, TimeSeriesKMeans]: ...
        # Iterate k in config.k_range; return (best_k, best_score, fitted_model)
```

---

### Evaluate (`h-e1/code/evaluate.py`)

**Dependencies**: Config, DTWModel

```python
import numpy as np
from typing import Tuple, Dict
from tslearn.clustering import TimeSeriesKMeans
from h_e1.code.config import ExperimentConfig

def compute_silhouette(X_flat: np.ndarray, labels: np.ndarray) -> float: ...
    # sklearn.metrics.silhouette_score(X_flat, labels)

def compute_jaccard_stability(
    X: np.ndarray,
    model: TimeSeriesKMeans,
    config: ExperimentConfig
) -> float: ...
    # n_bootstrap iterations: resample 80%, refit DTW model,
    # compute Jaccard similarity vs original labels on overlap
    # Returns mean Jaccard score

def verify_mechanism(
    model: TimeSeriesKMeans,
    silhouette: float,
    baseline_silhouette: float
) -> Tuple[bool, Dict]: ...
    # Checks: cluster_centers_ exists, n_clusters>=3,
    #   silhouette>0, silhouette>=baseline*0.9

def generate_figures(
    X: np.ndarray,
    labels: np.ndarray,
    silhouette_scores: Dict[int, float],
    model: TimeSeriesKMeans,
    config: ExperimentConfig
) -> None: ...
    # Generates and saves to config.figures_dir (PNG, 300 DPI):
    #   gate_metrics_bar.png, silhouette_vs_k.png, cluster_centroids.png,
    #   cluster_distribution.png, tsne_projection.png

def write_validation_report(results: Dict, config: ExperimentConfig) -> None: ...
    # Write pass/fail determination + all metric values to config.output_path
```

---

### Main (`h-e1/code/main.py`)

**Dependencies**: Config, DataModule, Models, Evaluate

```python
from typing import Dict
from h_e1.code.config import ExperimentConfig

def run_experiment(config: ExperimentConfig) -> Dict: ...
    # 1. collect_datasets(config) -> validate data quality
    # 2. preprocess(raw_series) -> X (3D), extract_features -> features (2D)
    # 3. BaselineModel.best_k_silhouette(features) -> baseline_k, baseline_score
    # 4. DTWModel.best_k_silhouette(X) -> best_k, best_score, dtw_model
    # 5. compute_jaccard_stability(X, dtw_model, config)
    # 6. verify_mechanism(dtw_model, best_score, baseline_score)
    # 7. generate_figures(X, labels, silhouette_scores, dtw_model, config)
    # 8. write_validation_report(results, config)
    # Returns: {silhouette, optimal_k, jaccard_stability, baseline_silhouette, gate_pass}

if __name__ == "__main__":
    config = ExperimentConfig()
    results = run_experiment(config)
```

---

## Dependencies

```
config.py
  data.py       (imports config)
  model.py      (imports config)
  evaluate.py   (imports config, model)
    main.py     (imports all above)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Data Collection | HfApi integration, date/downloads filtering, quality validation (<10% missing), rate-limit checkpointing | 10 | 3+2+3+2 |
| A-2 | Preprocessing Pipeline | log1p transform, tslearn 3D format conversion, z-score normalization, summary feature extraction | 7 | 2+2+2+1 |
| A-3 | Model Implementation | BaselineKMeans on features + DTWTimeSeriesKMeans on trajectories, k-range iteration, silhouette selection | 11 | 3+2+4+2 |
| A-4 | Evaluation & Stability | Bootstrap Jaccard 100x, mechanism verification indicators, gate pass/fail logic | 12 | 3+2+4+3 |
| A-5 | Visualization & Report | 5 required figures (bar/silhouette-k/centroids/distribution/t-SNE), 04_validation.md report | 9 | 2+1+3+3 |

**Distribution**: High(10-13): [A-3, A-4], Medium(7-9): [A-1, A-2, A-5]

---

## Output Artifacts

- `h-e1/figures/gate_metrics_bar.png` - mandatory gate validation figure
- `h-e1/figures/silhouette_vs_k.png`
- `h-e1/figures/cluster_centroids.png`
- `h-e1/figures/cluster_distribution.png`
- `h-e1/figures/tsne_projection.png`
- `h-e1/04_validation.md` - gate pass/fail report with all metrics and timestamps
