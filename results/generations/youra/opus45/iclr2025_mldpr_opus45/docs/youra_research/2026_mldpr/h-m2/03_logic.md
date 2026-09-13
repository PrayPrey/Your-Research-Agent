# Logic: h-m2 Shape Descriptor Differentiation

**Applied**: Standard scipy/numpy pattern (no relevant KB match for time series shape descriptors)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from base code
**Analyzed Path**: `docs/youra_research/20260325_mldpr/h-m1/code/`
**Relevant Symbols**:
- `load_series(config)` -> `List[Dict]` (keys: "id", "series")
- `preprocess_for_pelt(raw_series)` -> `List[np.ndarray]` (1D each)
- `PELTDetector.detect(series)` -> `Tuple[List[int], float]`
- `ExperimentConfig` dataclass (cache_path, pelt_model="l2", pelt_min_size=3, pelt_jump=1)

---

## External Dependencies API

### API Signatures (From Actual Code)

```python
# From: h-m1/code/data.py (ACTUAL CODE)
def load_series(config: ExperimentConfig) -> List[Dict]:
    """Returns list of {"id": str, "series": np.ndarray} (1D)."""
    ...

def preprocess_for_pelt(raw_series: List[np.ndarray]) -> List[np.ndarray]:
    """Log-transform + z-score per series. Returns List[np.ndarray] 1D."""
    ...

# From: h-m1/code/model.py (ACTUAL CODE)
class PELTDetector:
    def __init__(self, config: ExperimentConfig) -> None: ...
    def detect(self, series: np.ndarray) -> Tuple[List[int], float]:
        """Returns (changepoints_excl_endpoint, pen). pen = 2*log(n)."""
        ...

# From: h-m1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    pelt_model: str = "l2"
    pelt_min_size: int = 3
    pelt_jump: int = 1
    cache_path: str = "hf_dataset_cache.json"
    random_state: int = 42
```

**Note**: h-m2 does NOT import h-m1 modules. It replicates PELT inline with same params (model="l2", min_size=3, pen=2*log(n)).

**Verified from**: `h-m1/code/` actual implementation.

---

## A-1: Project Setup [Complexity: 5, Budget: 1]

**Applied**: Standard PyTorch modular layout (adapted for numpy-only)

### API Signatures

```python
# config.py
@dataclass
class ExperimentConfig:
    n_clusters: int = 4
    n_series: int = 500
    random_state: int = 42
    min_prominence: float = 0.1
    pelt_model: str = "l2"
    pelt_min_size: int = 3
    n_bootstrap: int = 100
    bootstrap_seed: int = 42
    variance_ratio_threshold: float = 2.0
    min_descriptors_passing: int = 2
    figures_dir: str = "h-m2/figures"
    output_path: str = "h-m2/04_validation.md"
    cache_path: str = "hf_dataset_cache.json"
    h_e1_cache_path: str = "../../h-e1/code/hf_dataset_cache.json"
    h_e1_model_path: str = "../../h-e1/code/kmeans_model.pkl"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Setup | Create dirs, config.py, requirements.txt |

---

## A-2: Data Loading [Complexity: 10, Budget: 2]

### API Signatures

```python
# data.py
def load_series_and_clusters(
    config: ExperimentConfig
) -> Tuple[List[np.ndarray], np.ndarray, np.ndarray]:
    """Load series + labels + centroids from h-e1.
    Returns: (all_series, cluster_labels, centroids)
      all_series: List[np.ndarray] (T,) each, len=500
      cluster_labels: (N,) int
      centroids: (k, T) float
    """
    ...

def get_cluster_members(
    all_series: List[np.ndarray],
    cluster_labels: np.ndarray,
    cluster_id: int
) -> List[np.ndarray]:
    """Return series assigned to cluster_id. Returns List[np.ndarray]."""
    ...

def validate_centroids(
    centroids: np.ndarray,
    config: ExperimentConfig
) -> Tuple[bool, Dict]:
    """Validate shape (k, T), no NaN/Inf. Returns (passed, report)."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Load | Parse h-e1 cache JSON + pickle model for centroids/labels |
| L-2-2 | Validate | Shape/NaN checks, get_cluster_members helper |

---

## A-3: Shape Descriptor Analyzer [Complexity: 14, Budget: 2]

### API Signatures

```python
# model.py
class ShapeDescriptorAnalyzer:
    def __init__(self, config: ExperimentConfig) -> None: ...

    def compute_descriptors(self, centroid: np.ndarray) -> Dict[str, float]:
        """4 descriptors for centroid (T,).
        Returns: {"growth_ratio", "peak_timing", "changepoint_count", "derivative_variance"}
        """
        ...

    def compute_descriptor_matrix(
        self, centroids: np.ndarray
    ) -> Tuple[np.ndarray, List[str]]:
        """centroids: (k, T) -> (descriptor_matrix: (k, 4), descriptor_names: List[str])"""
        ...

    def normalize_descriptors(self, descriptor_matrix: np.ndarray) -> np.ndarray:
        """Min-max normalize columns. (k, 4) -> (k, 4)"""
        ...
```

### Pseudo-code (compute_descriptors)

```
gradient = np.gradient(centroid)                        # (T,)
growth_ratio = mean(gradient > 0)                       # scalar [0,1]
peaks, _ = find_peaks(centroid, prominence=min_prominence)
peak_timing = peaks[0]/T if peaks else 0.5              # scalar [0,1]
algo = rpt.Pelt(model="l2", min_size=3).fit(centroid)
n_cps = len(algo.predict(pen=2*log(T))) - 1             # int
derivative_variance = var(gradient)                     # scalar
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Descriptors | compute_descriptors + edge cases (flat series, no peaks) |
| L-3-2 | Matrix | compute_descriptor_matrix + normalize_descriptors |

---

## A-4: Baseline Descriptor [Complexity: 7, Budget: 1]

### API Signatures

```python
class BaselineDescriptor:
    def __init__(self, config: ExperimentConfig) -> None: ...

    def compute_descriptors(self, centroid: np.ndarray) -> Dict[str, float]:
        """mean, std, trend. centroid: (T,) -> dict[str, float]"""
        ...

    def compute_descriptor_matrix(
        self, centroids: np.ndarray
    ) -> Tuple[np.ndarray, List[str]]:
        """centroids: (k, T) -> ((k, 3), ["mean","std","trend"])"""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Baseline | mean/std/polyfit(1) per centroid |

---

## A-5: Variance Analysis [Complexity: 15, Budget: 2]

### API Signatures

```python
# evaluate.py
def compute_inter_cluster_variance(
    descriptor_matrix: np.ndarray,   # (k, D)
    descriptor_names: List[str]
) -> Dict[str, float]:
    """var of each column across k centroids. -> {name: scalar}"""
    ...

def compute_intra_cluster_variance(
    all_series: List[np.ndarray],
    cluster_labels: np.ndarray,
    analyzer: ShapeDescriptorAnalyzer,
    descriptor_names: List[str],
    config: ExperimentConfig
) -> Dict[str, float]:
    """Bootstrap intra-cluster variance, averaged across clusters.
    n_bootstrap=100 samples per cluster. -> {name: scalar}
    """
    ...

def compute_variance_ratios(
    inter_variance: Dict[str, float],
    intra_variance: Dict[str, float],
    epsilon: float = 1e-8
) -> Dict[str, float]:
    """inter/intra per descriptor. -> {name: ratio}"""
    ...
```

### Pseudo-code (bootstrap intra)

```
rng = RandomState(config.bootstrap_seed)
for each cluster c in range(k):
    members = get_cluster_members(all_series, labels, c)
    per_bootstrap = []
    for _ in range(n_bootstrap):
        sample = rng.choice(members, size=len(members), replace=True)
        descs = [analyzer.compute_descriptors(s) for s in sample]
        per_bootstrap.append(var([d[name] for d in descs]) per name)
    intra_per_cluster[c] = mean(per_bootstrap)
intra = mean over clusters
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Inter/ratio | compute_inter_cluster_variance + compute_variance_ratios |
| L-5-2 | Bootstrap | compute_intra_cluster_variance with seed-controlled bootstrap |

---

## A-6: Gate Metrics [Complexity: 10, Budget: 1]

### API Signatures

```python
def compute_gate_metrics(
    variance_ratios: Dict[str, float],
    descriptor_matrix: np.ndarray,   # (k, D) normalized
    config: ExperimentConfig
) -> Dict:
    """Gate: ratio > 2.0 on >= 2 descriptors.
    Returns: {gate_pass, n_passing, passing_descriptors,
              distinct_profiles, pairwise_distances}
    """
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Gate | Ratio threshold check + pairwise distance (sklearn) |

---

## A-7: Visualization [Complexity: 14, Budget: 1]

### API Signatures

```python
def generate_figures(
    centroids: np.ndarray,           # (k, T)
    descriptor_matrix: np.ndarray,   # (k, 4)
    descriptor_names: List[str],
    variance_ratios: Dict[str, float],
    baseline_ratios: Dict[str, float],
    config: ExperimentConfig
) -> List[str]:
    """Save 5 PNG figures to figures_dir. Returns list of paths."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Figures | bar, overlay, radar, scatter(PCA), heatmap at 300 DPI |

---

## A-8: Validation Report [Complexity: 8, Budget: 1]

### API Signatures

```python
def write_validation_report(results: Dict, config: ExperimentConfig) -> str:
    """Write 04_validation.md. Returns 'PASS' or 'FAIL'."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Report | Markdown with all metrics, gate verdict, timestamp |

---

## A-9: Main Orchestration [Complexity: 9, Budget: 1]

### API Signatures

```python
# main.py
def run_experiment(config: ExperimentConfig) -> Dict:
    """Full pipeline. Returns dict with all metrics + gate_pass."""
    ...

if __name__ == "__main__":
    config = ExperimentConfig()
    results = run_experiment(config)
    print(f"Gate: {'PASS' if results['gate_pass'] else 'FAIL'}")
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | Main | Wire all steps, compile results dict |

---

## A-10: Integration Test [Complexity: 10, Budget: 1]

No new API. End-to-end `run_experiment()` invocation + assertions on gate metrics and figure file existence.

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-10-1 | E2E test | Run pipeline, assert gate_pass in results, assert 5 figures saved |

---

## Subtask Budget Summary

| Task | Budget | Used |
|------|--------|------|
| A-1 | 1 | 1 |
| A-2 | 2 | 2 |
| A-3 | 2 | 2 |
| A-4 | 1 | 1 |
| A-5 | 2 | 2 |
| A-6 | 1 | 1 |
| A-7 | 1 | 1 |
| A-8 | 1 | 1 |
| A-9 | 1 | 1 |
| A-10 | 1 | 1 |
| **Total** | **13** | **13** |
