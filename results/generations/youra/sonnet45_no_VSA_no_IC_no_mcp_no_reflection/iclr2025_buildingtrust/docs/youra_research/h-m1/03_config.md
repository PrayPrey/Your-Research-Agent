# Configuration: h-m1

**Hypothesis:** Hierarchical clustering (Ward linkage) applied to correlation matrices identifies 2-5 distinct failure mode clusters with silhouette score > 0.5 and ≥80% bootstrap consistency (1000 iterations)
**Type:** MECHANISM
**Date:** 2026-08-28

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** config classes verified from base code
**Config Files Found:** h-e1/code/config.py
**Pattern Used:** dataclass

Verified field names from actual h-e1 config code. Base config uses `benchmarks`, `data_dir`, `results_dir`, `figures_dir` (not `benchmark_names` or `output_path` as might be assumed from specs).

---

## Applied Patterns

**Archon KB:** Standard hierarchical clustering config pattern (scipy defaults)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from h-e1:

```python
# From: h-e1/code/config.py (ACTUAL CODE)
@dataclass
class DataConfig:
    benchmarks: List[str] = field(default_factory=lambda: ["truthfulqa", "advbench", "bold"])
    min_models: int = 15
    size_strata: Dict[str, str] = field(default_factory=lambda: {
        "small": "<1B",
        "medium": "1-10B",
        "large": ">10B"
    })
    data_dir: Path = Path("./data")

@dataclass
class VisualizationConfig:
    figures_dir: Path = Path("./figures")
    color_scheme: str = "RdBu_r"
    figure_dpi: int = 300
```

**Verified from:** h-e1/code/config.py (actual implementation)

---

## Configuration Schema

### Format: Python Dataclass

```python
from dataclasses import dataclass, field
from typing import List, Dict
from pathlib import Path


@dataclass
class DataConfig:
    """Reuses h-e1 data loading config."""
    benchmarks: List[str] = field(default_factory=lambda: ["truthfulqa", "advbench", "bold"])
    data_dir: Path = Path("./data")
    h_e1_results_path: Path = Path("../h-e1/results/correlation_results.json")
    h_e1_benchmark_scores: Path = Path("../h-e1/data/benchmark_scores.csv")
    cache_distance_matrix: bool = True
    distance_matrix_path: Path = Path("./data/correlation_distance_matrix.npy")


@dataclass
class ClusteringConfig:
    """Ward linkage clustering parameters."""
    linkage_method: str = "ward"
    k_range: List[int] = field(default_factory=lambda: [2, 3, 4, 5])
    distance_metric: str = "precomputed"
    random_seed: int = 42


@dataclass
class BootstrapConfig:
    """Bootstrap validation parameters."""
    n_iterations: int = 1000
    random_seed: int = 42
    sample_size: int = 20  # Number of models from h-e1


@dataclass
class MetricsConfig:
    """Gate thresholds."""
    silhouette_threshold: float = 0.5
    consistency_threshold: float = 80.0
    cophenetic_threshold: float = 0.7


@dataclass
class VisualizationConfig:
    """Visualization parameters (inherits from h-e1)."""
    figures_dir: Path = Path("./figures")
    color_scheme: str = "RdBu_r"
    figure_dpi: int = 300
    dendrogram_labels: List[str] = field(default_factory=lambda: ["TruthfulQA", "AdvBench", "BOLD"])


@dataclass
class ExperimentConfig:
    """Master configuration for h-m1 clustering analysis."""
    data: DataConfig = field(default_factory=DataConfig)
    clustering: ClusteringConfig = field(default_factory=ClusteringConfig)
    bootstrap: BootstrapConfig = field(default_factory=BootstrapConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)
    viz: VisualizationConfig = field(default_factory=VisualizationConfig)
    results_dir: Path = Path("./results")
```

---

## Task Configuration Breakdown

### M1: Data Loading [Complexity: 6, Budget: 4 subtasks]

**Applied:** h-e1 data schema reuse

```python
@dataclass
class DataConfig:
    benchmarks: List[str] = field(default_factory=lambda: ["truthfulqa", "advbench", "bold"])
    data_dir: Path = Path("./data")
    h_e1_results_path: Path = Path("../h-e1/results/correlation_results.json")
    h_e1_benchmark_scores: Path = Path("../h-e1/data/benchmark_scores.csv")
    cache_distance_matrix: bool = True
    distance_matrix_path: Path = Path("./data/correlation_distance_matrix.npy")
```

#### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M1-1 | Load h-e1 correlation matrix | Read JSON, validate shape (3×3) |
| M1-2 | Compute distance matrix | Transform `d = 1 - abs(r)` |
| M1-3 | Load model stratification | Parse size_stratum column from CSV |
| M1-4 | Cache distance matrix | Save to `.npy` for reuse |

---

### M2: Ward Linkage Clustering [Complexity: 8]

**Applied:** scipy.cluster.hierarchy defaults

```python
@dataclass
class ClusteringConfig:
    linkage_method: str = "ward"
    k_range: List[int] = field(default_factory=lambda: [2, 3, 4, 5])
    distance_metric: str = "precomputed"
    random_seed: int = 42  # For reproducibility in tie-breaking
```

---

### M3: Silhouette Evaluation [Complexity: 7]

**Applied:** sklearn.metrics defaults

```python
@dataclass
class MetricsConfig:
    silhouette_threshold: float = 0.5
    consistency_threshold: float = 80.0
    cophenetic_threshold: float = 0.7  # Dendrogram quality
```

---

### M4: Bootstrap Validation [Complexity: 14]

**Applied:** Standard bootstrap resampling

```python
@dataclass
class BootstrapConfig:
    n_iterations: int = 1000
    random_seed: int = 42
    sample_size: int = 20  # Number of models from h-e1
```

---

## Usage

```python
# Load default config
config = ExperimentConfig()

# Access parameters
config.clustering.k_range  # [2, 3, 4, 5]
config.bootstrap.n_iterations  # 1000
config.metrics.silhouette_threshold  # 0.5

# Override for testing
test_config = ExperimentConfig(
    bootstrap=BootstrapConfig(n_iterations=100),
    clustering=ClusteringConfig(k_range=[2, 3])
)
```

---

## Rationale for Non-Standard Values

**n_iterations = 1000** (not 500): PRD specifies 1000 for ≥80% consistency threshold.

**cophenetic_threshold = 0.7** (not 0.8): Literature standard for "good" dendrogram quality.

---

## File Paths

```python
# Input (from h-e1)
../h-e1/results/correlation_results.json        # 3×3 correlation matrix
../h-e1/data/benchmark_scores.csv               # 20 models × 3 benchmarks

# Cache
./data/correlation_distance_matrix.npy          # Cached distance matrix
./data/stratified_correlations/*.npy            # Per-stratum matrices

# Output
./results/clustering_results.json               # Cluster assignments, silhouette scores
./results/bootstrap_consistency.json            # Consistency matrix
./results/gate_decision.json                    # PASS/FAIL status
./figures/dendrogram.png                        # Hierarchical clustering tree
./figures/silhouette_vs_k.png                   # Silhouette score plot
./figures/consistency_matrix.png                # Bootstrap heatmap
```

---

## Validation

```python
def validate_config(config: ExperimentConfig) -> None:
    assert len(config.data.benchmarks) == 3
    assert config.clustering.linkage_method == "ward"
    assert 2 in config.clustering.k_range and 5 in config.clustering.k_range
    assert config.bootstrap.n_iterations >= 500
    assert 0 < config.metrics.silhouette_threshold <= 1
    assert config.metrics.consistency_threshold >= 50.0
```

---

## Dependencies

```txt
scipy>=1.7.0
scikit-learn>=1.0.0
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
```

---

*Generated by Phase 3 Configuration Agent*
*Source: 03_architecture.md, 03_prd.md, h-e1/code/config.py*
