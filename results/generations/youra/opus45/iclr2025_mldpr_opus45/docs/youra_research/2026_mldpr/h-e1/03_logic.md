# Logic: h-e1 - DTW Time Series Clustering

**Hypothesis**: EXISTENCE - DTW clustering of HuggingFace dataset download trajectories
**Type**: PoC (EXISTENCE)
**Date**: 2026-03-27

Applied: modular-pipeline pattern (tslearn clustering)
Applied: Standard scikit-learn API conventions

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-3: Model Implementation [Complexity: 11, Budget: 2 subtasks]

### API Signatures

```python
# h-e1/code/model.py

import numpy as np
from typing import Tuple, Dict
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from tslearn.clustering import TimeSeriesKMeans
from code.config import ExperimentConfig


class BaselineModel:
    """KMeans clustering on summary features."""

    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config

    def fit(self, features: np.ndarray, k: int) -> np.ndarray:
        """Fit KMeans and return labels. features: [N, 3] -> labels: [N]"""
        # features: [N, 3]  (mean, std, trend_slope)
        # returns: [N]  cluster labels
        model = KMeans(
            n_clusters=k,
            random_state=self.config.random_state,
            n_init=self.config.n_init,
        )
        return model.fit_predict(features)

    def best_k_silhouette(
        self, features: np.ndarray
    ) -> Tuple[int, float, np.ndarray]:
        """Iterate k_range, return (best_k, best_score, best_labels).
        features: [N, 3]"""
        # features: [N, 3]
        best_k, best_score, best_labels = -1, -np.inf, None
        scores: Dict[int, float] = {}
        for k in range(self.config.k_range[0], self.config.k_range[1] + 1):
            labels = self.fit(features, k)
            score = silhouette_score(features, labels)
            scores[k] = score
            if score > best_score:
                best_k, best_score, best_labels = k, score, labels
        return best_k, best_score, best_labels  # (int, float, [N])


class DTWModel:
    """DTW TimeSeriesKMeans clustering on raw trajectories."""

    def __init__(self, config: ExperimentConfig) -> None:
        self.config = config

    def fit(self, X: np.ndarray, k: int) -> TimeSeriesKMeans:
        """Fit DTW model and return fitted model. X: [N, T, 1]"""
        # X: [N, T, 1]  tslearn 3D format
        model = TimeSeriesKMeans(
            n_clusters=k,
            metric="dtw",
            max_iter=self.config.max_iter,
            n_init=self.config.n_init,
            random_state=self.config.random_state,
        )
        model.fit(X)
        return model

    def best_k_silhouette(
        self, X: np.ndarray
    ) -> Tuple[int, float, TimeSeriesKMeans, Dict[int, float]]:
        """Iterate k_range, return (best_k, best_score, best_model, all_scores).
        X: [N, T, 1]"""
        # X: [N, T, 1]
        # X_flat for silhouette: [N, T]  (squeeze last dim)
        X_flat = X[:, :, 0]  # [N, T]
        best_k, best_score, best_model = -1, -np.inf, None
        all_scores: Dict[int, float] = {}
        for k in range(self.config.k_range[0], self.config.k_range[1] + 1):
            model = self.fit(X, k)
            labels = model.labels_  # [N]
            score = silhouette_score(X_flat, labels)
            all_scores[k] = score
            if score > best_score:
                best_k, best_score, best_model = k, score, model
        return best_k, best_score, best_model, all_scores
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| features | [N, 3] | mean, std, trend_slope per series |
| X | [N, T, 1] | tslearn 3D padded format |
| X_flat | [N, T] | squeezed for silhouette_score |
| labels | [N] | int cluster assignments |
| cluster_centers_ | [k, T, 1] | DTW cluster centroids |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | BaselineModel | KMeans on [N,3] features, k-range silhouette selection |
| L-3-2 | DTWModel | TimeSeriesKMeans on [N,T,1], k-range silhouette selection |

---

## A-4: Evaluation & Stability [Complexity: 12, Budget: 2 subtasks]

### API Signatures

```python
# h-e1/code/evaluate.py

import numpy as np
from typing import Tuple, Dict, List
from sklearn.metrics import silhouette_score
from tslearn.clustering import TimeSeriesKMeans
from code.config import ExperimentConfig


def compute_silhouette(X_flat: np.ndarray, labels: np.ndarray) -> float:
    """Compute silhouette score. X_flat: [N, T], labels: [N] -> float"""
    # X_flat: [N, T], labels: [N]
    return float(silhouette_score(X_flat, labels))


def compute_jaccard_stability(
    X: np.ndarray,
    model: TimeSeriesKMeans,
    config: ExperimentConfig,
) -> float:
    """Bootstrap Jaccard stability over n_bootstrap iterations.
    X: [N, T, 1] -> mean Jaccard float"""
    # X: [N, T, 1]
    ...


def verify_mechanism(
    model: TimeSeriesKMeans,
    silhouette: float,
    baseline_silhouette: float,
) -> Tuple[bool, Dict]:
    """Check mechanism indicators. Returns (passed, indicators_dict)."""
    ...


def generate_figures(
    X: np.ndarray,                      # [N, T, 1]
    labels: np.ndarray,                 # [N]
    silhouette_scores: Dict[int, float],
    model: TimeSeriesKMeans,
    config: ExperimentConfig,
) -> None:
    """Generate and save 5 required PNG figures to config.figures_dir."""
    ...


def write_validation_report(results: Dict, config: ExperimentConfig) -> None:
    """Write pass/fail + all metrics to config.output_path."""
    ...
```

### Pseudo-code: Bootstrap Jaccard Stability

```
def compute_jaccard_stability(X, model, config):
    # X: [N, T, 1],  original labels = model.labels_ [N]
    original_labels = model.labels_          # [N]
    jaccard_scores = []

    for _ in range(config.n_bootstrap):     # 100 iterations
        # 1. Sample 80% indices (with replacement allowed)
        n = len(X)
        n_sample = int(n * config.bootstrap_ratio)   # ~0.8 * N
        idx = np.random.choice(n, size=n_sample, replace=False)

        # 2. Refit DTW model on subsample
        X_sub = X[idx]                       # [n_sample, T, 1]
        boot_model = TimeSeriesKMeans(
            n_clusters=model.n_clusters,
            metric="dtw",
            max_iter=config.max_iter,
            n_init=config.n_init,
            random_state=None,               # vary per bootstrap
        )
        boot_model.fit(X_sub)
        boot_labels = boot_model.labels_     # [n_sample]

        # 3. Align cluster labels via majority vote (Hungarian matching)
        orig_sub = original_labels[idx]      # [n_sample]
        aligned = align_labels(boot_labels, orig_sub, model.n_clusters)

        # 4. Compute per-cluster Jaccard, take mean
        jaccards = []
        for c in range(model.n_clusters):
            A = set(np.where(orig_sub == c)[0])
            B = set(np.where(aligned == c)[0])
            if len(A | B) == 0:
                continue
            jaccards.append(len(A & B) / len(A | B))
        jaccard_scores.append(np.mean(jaccards))

    return float(np.mean(jaccard_scores))


def align_labels(boot_labels, orig_labels, k):
    # Build k x k cost matrix (overlap counts)
    # Apply Hungarian algorithm (scipy.optimize.linear_sum_assignment)
    # Return relabeled boot_labels array
    ...
```

### Pseudo-code: verify_mechanism

```
def verify_mechanism(model, silhouette, baseline_silhouette):
    indicators = {
        "has_cluster_centers":  hasattr(model, "cluster_centers_"),
        "n_clusters_valid":     model.n_clusters >= 3,
        "silhouette_positive":  silhouette > 0,
        "silhouette_vs_base":   silhouette >= baseline_silhouette * 0.9,
        "gate_silhouette":      silhouette > 0.25,
        "gate_k_valid":         3 <= model.n_clusters <= 8,
    }
    passed = all(indicators.values())
    return passed, indicators
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Bootstrap Jaccard | 100x bootstrap resample + label alignment + per-cluster Jaccard |
| L-4-2 | Gate Verification | verify_mechanism + generate_figures + write_validation_report |

---

## Supporting Modules (Low Complexity - No Subtask Budget)

### data.py API

```python
# h-e1/code/data.py

def collect_datasets(config: ExperimentConfig) -> List[Dict]:
    """Query HfApi, filter, return list of {id, series}.
    series per item: np.ndarray [T] monthly downloads"""
    ...

def preprocess(raw_series: List[np.ndarray]) -> np.ndarray:
    """log1p -> to_time_series_dataset -> z-score normalize.
    Returns X: [N, T, 1]"""
    ...

def extract_features(series_list: List[np.ndarray]) -> np.ndarray:
    """Extract [mean, std, trend_slope] per series.
    Returns features: [N, 3]"""
    ...
```

### main.py API

```python
# h-e1/code/main.py

def run_experiment(config: ExperimentConfig) -> Dict:
    """Full pipeline. Returns: {
        silhouette: float,
        optimal_k: int,
        jaccard_stability: float,
        baseline_silhouette: float,
        gate_pass: bool,
        silhouette_scores: Dict[int, float],
    }"""
    ...
```

---

## Gate Pass/Fail Thresholds

| Metric | Threshold | Source |
|--------|-----------|--------|
| silhouette | > 0.25 | FR-5.1 |
| optimal_k | in [3, 8] | FR-5.1 |
| jaccard_stability | > 0.65 | FR-5.2 |
