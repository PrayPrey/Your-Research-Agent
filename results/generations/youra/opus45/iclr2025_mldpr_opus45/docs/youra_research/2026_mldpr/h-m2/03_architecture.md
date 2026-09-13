# Architecture: h-m2 Shape Descriptor Differentiation

**Applied**: modular-experiment-pattern (data/model/evaluate/main separation)
**Applied**: variance-ratio-analysis-pattern (inter/intra cluster variance bootstrap)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/20260325_mldpr/h-m1/code/`
**Findings**: Flat module structure - config.py, data.py, model.py, evaluate.py, main.py; all imports relative; cache at `hf_dataset_cache.json` local to code dir; cluster data loaded from h-e1 via relative path `../../h-e1/code/hf_dataset_cache.json`.

---

## File Organization

- `h-m2/code/config.py` - ExperimentConfig dataclass
- `h-m2/code/data.py` - load centroids from h-e1, load series for bootstrap
- `h-m2/code/model.py` - ShapeDescriptorAnalyzer, BaselineDescriptor
- `h-m2/code/evaluate.py` - variance ratio analysis, gate metrics, figures, report
- `h-m2/code/main.py` - orchestration entry point
- `h-m2/figures/` - output PNG figures (300 DPI)
- `h-m2/04_validation.md` - gate pass/fail report

---

## Module Definitions

### ExperimentConfig (`code/config.py`)

**Dependencies**: stdlib only

```python
@dataclass
class ExperimentConfig:
    # Data
    n_clusters: int = 4
    n_series: int = 500
    random_state: int = 42

    # Shape descriptor parameters
    min_prominence: float = 0.1
    pelt_model: str = "l2"
    pelt_min_size: int = 3

    # Bootstrap parameters
    n_bootstrap: int = 100
    bootstrap_seed: int = 42

    # Gate threshold
    variance_ratio_threshold: float = 2.0
    min_descriptors_passing: int = 2

    # Output paths
    figures_dir: str = "h-m2/figures"
    output_path: str = "h-m2/04_validation.md"
    cache_path: str = "hf_dataset_cache.json"
    h_e1_cache_path: str = "../../h-e1/code/hf_dataset_cache.json"
    h_e1_model_path: str = "../../h-e1/code/kmeans_model.pkl"
```

---

### DataLoader (`code/data.py`)

**Dependencies**: ExperimentConfig, numpy, json, os, pickle (for h-e1 model)

```python
def load_series_and_clusters(config: ExperimentConfig) -> Tuple[List[np.ndarray], np.ndarray, np.ndarray]:
    """
    Load time series + cluster assignments + centroids from h-e1.

    Returns:
        (all_series, cluster_labels, centroids)
        all_series: List[np.ndarray] shape (T,) each, length=500
        cluster_labels: (N,) int array, cluster id per series
        centroids: (k, T) float array, one centroid per cluster
    """
    ...

def get_cluster_members(
    all_series: List[np.ndarray],
    cluster_labels: np.ndarray,
    cluster_id: int
) -> List[np.ndarray]:
    """
    Return all series assigned to given cluster_id.

    Returns:
        List[np.ndarray] of member series
    """
    ...

def validate_centroids(centroids: np.ndarray, config: ExperimentConfig) -> Tuple[bool, Dict]:
    """
    Validate centroid shape (k, T) and no NaN/Inf.

    Returns:
        (passed: bool, report: Dict)
    """
    ...
```

---

### ShapeDescriptorAnalyzer (`code/model.py`)

**Dependencies**: ExperimentConfig, numpy, scipy.signal, ruptures

```python
class ShapeDescriptorAnalyzer:
    def __init__(self, config: ExperimentConfig) -> None: ...

    def compute_descriptors(self, centroid: np.ndarray) -> Dict[str, float]:
        """
        Compute 4 shape descriptors for a single centroid.

        Args:
            centroid: (T,) normalized time series
        Returns:
            dict with keys: growth_ratio, peak_timing,
                            changepoint_count, derivative_variance
        """
        ...

    def compute_descriptor_matrix(
        self, centroids: np.ndarray
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Apply compute_descriptors to all k centroids.

        Args:
            centroids: (k, T)
        Returns:
            (descriptor_matrix, descriptor_names)
            descriptor_matrix: (k, 4) float array
            descriptor_names: List[str] length 4
        """
        ...

    def normalize_descriptors(
        self, descriptor_matrix: np.ndarray
    ) -> np.ndarray:
        """
        Min-max normalize each descriptor column to [0, 1].

        Args:
            descriptor_matrix: (k, 4)
        Returns:
            normalized: (k, 4)
        """
        ...


class BaselineDescriptor:
    def __init__(self, config: ExperimentConfig) -> None: ...

    def compute_descriptors(self, centroid: np.ndarray) -> Dict[str, float]:
        """
        Baseline: simple summary statistics only (mean, std, trend).

        Args:
            centroid: (T,) time series
        Returns:
            dict with keys: mean, std, trend
        """
        ...

    def compute_descriptor_matrix(
        self, centroids: np.ndarray
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Args:
            centroids: (k, T)
        Returns:
            (descriptor_matrix, descriptor_names)
            descriptor_matrix: (k, 3)
        """
        ...
```

---

### VarianceAnalyzer (`code/evaluate.py`)

**Dependencies**: ExperimentConfig, numpy, sklearn.metrics, scipy.spatial.distance

```python
def compute_inter_cluster_variance(
    descriptor_matrix: np.ndarray,
    descriptor_names: List[str]
) -> Dict[str, float]:
    """
    Variance of each descriptor across k centroids.

    Args:
        descriptor_matrix: (k, 4)
    Returns:
        dict: descriptor_name -> variance scalar
    """
    ...

def compute_intra_cluster_variance(
    all_series: List[np.ndarray],
    cluster_labels: np.ndarray,
    analyzer: ShapeDescriptorAnalyzer,
    descriptor_names: List[str],
    config: ExperimentConfig
) -> Dict[str, float]:
    """
    Bootstrap intra-cluster descriptor variance, averaged across clusters.

    Args:
        all_series: List[np.ndarray] 500 series
        cluster_labels: (N,) int array
        analyzer: ShapeDescriptorAnalyzer instance
        descriptor_names: List[str]
        config: for n_bootstrap, bootstrap_seed
    Returns:
        dict: descriptor_name -> mean intra-cluster variance
    """
    ...

def compute_variance_ratios(
    inter_variance: Dict[str, float],
    intra_variance: Dict[str, float],
    epsilon: float = 1e-8
) -> Dict[str, float]:
    """
    Inter/intra ratio per descriptor.

    Returns:
        dict: descriptor_name -> ratio scalar
    """
    ...

def compute_gate_metrics(
    variance_ratios: Dict[str, float],
    descriptor_matrix: np.ndarray,
    config: ExperimentConfig
) -> Dict:
    """
    Evaluate gate: variance_ratio > 2.0 on >= 2 descriptors.

    Returns:
        dict with gate_pass, n_passing_descriptors, passing_descriptors,
             distinct_profiles, pairwise_distances
    """
    ...

def generate_figures(
    centroids: np.ndarray,
    descriptor_matrix: np.ndarray,
    descriptor_names: List[str],
    variance_ratios: Dict[str, float],
    baseline_ratios: Dict[str, float],
    config: ExperimentConfig
) -> List[str]:
    """
    Generate and save all figures.

    Figures:
    1. gate_metrics_bar.png - variance ratio per descriptor with 2.0 threshold
    2. centroid_overlay.png - all k centroids on same axes
    3. descriptor_radar.png - radar chart per cluster
    4. descriptor_scatter.png - 2D PCA of 4D descriptor space
    5. distance_heatmap.png - pairwise descriptor distances

    Returns:
        List of saved figure paths
    """
    ...

def write_validation_report(results: Dict, config: ExperimentConfig) -> str:
    """
    Write 04_validation.md with gate pass/fail.

    Returns:
        'PASS' or 'FAIL'
    """
    ...
```

---

### Main Runner (`code/main.py`)

**Dependencies**: all modules above

```python
def run_experiment(config: ExperimentConfig) -> Dict:
    """
    Orchestrate full h-m2 experiment pipeline.

    Steps:
    1. Load series + cluster assignments + centroids from h-e1
    2. Validate centroid shape (k=4, T=52)
    3. Compute shape descriptors for all centroids -> (k, 4) matrix
    4. Compute baseline descriptors for all centroids -> (k, 3) matrix
    5. Compute inter-cluster variance per descriptor
    6. Compute intra-cluster variance via bootstrap
    7. Compute variance ratios (shape vs baseline)
    8. Evaluate gate: ratio > 2.0 on >= 2 descriptors
    9. Generate figures
    10. Write validation report

    Returns:
        Dict with all metrics and gate_pass boolean
    """
    ...
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ExperimentConfig (h-m1) | `from config import ExperimentConfig` | `h-m1/code/config.py` |
| load_series | `from data import load_series` | `h-m1/code/data.py` |
| preprocess_for_pelt | `from data import preprocess_for_pelt` | `h-m1/code/data.py` |
| PELTDetector | `from model import PELTDetector` | `h-m1/code/model.py` |

### Data Artifacts Reused

| Artifact | Path | Used For |
|----------|------|----------|
| HF dataset cache | `h-m1/code/hf_dataset_cache.json` | Load 500 time series for bootstrap |
| h-e1 cache (fallback) | `../../h-e1/code/hf_dataset_cache.json` | Alternate source |
| h-e1 cluster model | `../../h-e1/code/` | Load k=4 centroids + labels |

**Note**: h-m2 does NOT import h-m1 modules directly. It replicates the PELT call inline inside `ShapeDescriptorAnalyzer.compute_descriptors()` for the changepoint_count descriptor (same ruptures parameters: model="l2", pen=2*log(n)).

**Verified from**: `docs/youra_research/20260325_mldpr/h-m1/code/` (actual implementation)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create h-m2/code/ structure, config.py, requirements.txt, figures dir | 5 | 1+1+1+2 |
| A-2 | Data Loading | Implement data.py: load h-e1 centroids + cluster labels + member series | 10 | 2+3+2+3 |
| A-3 | Shape Descriptor Analyzer | Implement ShapeDescriptorAnalyzer with 4 descriptors + normalization | 14 | 4+3+4+3 |
| A-4 | Baseline Descriptor | Implement BaselineDescriptor with mean/std/trend summary statistics | 7 | 2+2+2+1 |
| A-5 | Variance Analysis | Implement inter-cluster variance, bootstrap intra-cluster variance, ratio computation | 15 | 3+4+5+3 |
| A-6 | Gate Metrics | Implement gate evaluation: ratio > 2.0 on >= 2 descriptors, distinct profile check | 10 | 2+3+3+2 |
| A-7 | Visualization | Implement generate_figures: 5 figure types (bar, overlay, radar, scatter, heatmap) | 14 | 3+2+4+5 |
| A-8 | Validation Report | Implement write_validation_report with pass/fail verdict and all metrics | 8 | 2+2+2+2 |
| A-9 | Main Orchestration | Implement run_experiment: connect all steps, result compilation | 9 | 2+3+2+2 |
| A-10 | Integration Test | End-to-end run, verify gate metrics match expected, figures saved | 10 | 2+3+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3, A-5, A-7], Medium(9-13): [A-2, A-6, A-9, A-10], Low(4-8): [A-1, A-4, A-8]
