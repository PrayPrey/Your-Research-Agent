# Logic Design: h-m1

**Hypothesis:** Hierarchical clustering (Ward linkage) applied to correlation matrices identifies 2-5 distinct failure mode clusters with silhouette score > 0.5 and ≥80% bootstrap consistency (1000 iterations)

**Type:** MECHANISM
**Date:** 2026-08-28
**Budget:** 4 subtasks allocated

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Base hypothesis (h-e1) code not yet implemented - will read h-e1 data files directly
**Analyzed Path**: /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP_no_Reflection/sonnet45/TEST_buildingtrust/docs/youra_research/h-e1/code
**Relevant Symbols**: None - h-e1 code directory does not exist yet. Will consume h-e1 data outputs (correlation_results.json, benchmark_scores.csv) when h-e1 is implemented.

**Note**: h-m1 depends on h-e1 data schema but not h-e1 code. Statistical clustering pipeline is standalone.

---

## A-M1: Data Loading and Distance Transform [Complexity: 6, Budget: 1]

**Applied**: Standard NumPy/Pandas data loading pattern

### API Signatures

```python
import numpy as np
import pandas as pd
from typing import Tuple, Dict
from pathlib import Path

class H_E1_DataLoader:
    """Load h-e1 correlation results and compute distance matrix for clustering."""
    
    def __init__(self, h_e1_results_path: str):
        """
        Args:
            h_e1_results_path: Path to h-e1/results/ directory
        """
        self.results_path = Path(h_e1_results_path)
    
    def load_correlation_matrix(self) -> Tuple[np.ndarray, list]:
        """
        Load 3x3 correlation matrix from h-e1 results.
        
        Returns:
            (corr_matrix, benchmark_names) where corr_matrix: [3, 3], benchmark_names: list of 3 strings
        """
        ...
    
    def compute_distance_matrix(self, corr_matrix: np.ndarray) -> np.ndarray:
        """
        Transform correlation to distance: d = 1 - abs(r).
        
        Args:
            corr_matrix: [3, 3] correlation matrix
        
        Returns:
            distance_matrix: [3, 3], symmetric, elements in [0, 2]
        """
        ...
    
    def load_benchmark_scores(self) -> pd.DataFrame:
        """
        Load raw model scores for bootstrap resampling.
        
        Returns:
            df: [N, 6] with columns [model_name, size_stratum, params_billions,
                truthfulqa_score, advbench_score, bold_score]
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| corr_matrix | [3, 3] | Symmetric, diagonal = 1.0 |
| distance_matrix | [3, 3] | Symmetric, d[i,i] = 0 |
| benchmark_scores | [N, 6] | N ≥ 15 models, 6 columns |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M1-1 | load_and_validate | Load JSON/CSV, validate schema, cache distance matrix to NPY |

---

## A-M2: Ward Linkage Clustering [Complexity: 8, Budget: 1]

**Applied**: scipy.cluster.hierarchy standard pattern

### API Signatures

```python
from scipy.cluster.hierarchy import linkage, fcluster, cophenet
from scipy.spatial.distance import squareform

class WardClusterer:
    """Hierarchical clustering with Ward linkage method."""
    
    def __init__(self, distance_matrix: np.ndarray):
        """
        Args:
            distance_matrix: [n, n] symmetric distance matrix
        """
        self.distance_matrix = distance_matrix
        self.linkage_matrix = None
    
    def fit(self, method: str = 'ward') -> np.ndarray:
        """
        Compute hierarchical linkage.
        
        Args:
            method: Linkage method (default: 'ward')
        
        Returns:
            linkage_matrix: [n-1, 4] scipy linkage format
        """
        ...
    
    def get_clusters(self, k: int) -> np.ndarray:
        """
        Extract k clusters from dendrogram.
        
        Args:
            k: Number of clusters (2-5 for h-m1)
        
        Returns:
            labels: [n,] cluster assignments (1 to k)
        """
        ...
    
    def compute_cophenetic(self) -> float:
        """
        Dendrogram quality metric.
        
        Returns:
            cophenetic_correlation: float in [-1, 1], target > 0.7
        """
        ...
```

### Pseudo-code

```
1. condensed_dist = squareform(distance_matrix)  # Upper triangular
2. linkage_matrix = linkage(condensed_dist, method='ward')
3. For k in [2, 3, 4, 5]:
     labels_k = fcluster(linkage_matrix, k, criterion='maxclust')
4. cophenetic_corr = cophenet(linkage_matrix, condensed_dist)[0]
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M2-1 | ward_clustering | Fit linkage, extract k=2-5 cluster labels, compute cophenetic |

---

## A-M3: Silhouette Evaluation [Complexity: 7, Budget: 1]

**Applied**: sklearn.metrics standard pattern

### API Signatures

```python
from sklearn.metrics import silhouette_score
from typing import Dict

def silhouette_score_for_k(
    distance_matrix: np.ndarray, 
    labels: np.ndarray
) -> float:
    """
    Compute silhouette score for given cluster assignments.
    
    Args:
        distance_matrix: [n, n] precomputed distances
        labels: [n,] cluster assignments
    
    Returns:
        silhouette: float in [-1, 1], >0.5 indicates good separation
    """
    return silhouette_score(distance_matrix, labels, metric='precomputed')

def find_optimal_k(
    distance_matrix: np.ndarray,
    linkage_matrix: np.ndarray,
    k_range: list = [2, 3, 4, 5]
) -> Tuple[int, Dict[int, float]]:
    """
    Evaluate silhouette scores and select optimal k.
    
    Args:
        distance_matrix: [n, n] distances
        linkage_matrix: [n-1, 4] from WardClusterer.fit()
        k_range: Cluster counts to evaluate
    
    Returns:
        (optimal_k, silhouette_scores) where silhouette_scores: {k: score}
    """
    ...
```

### Pseudo-code

```
1. For each k in [2, 3, 4, 5]:
     labels = fcluster(linkage_matrix, k, criterion='maxclust')
     scores[k] = silhouette_score(distance_matrix, labels, metric='precomputed')
2. optimal_k = argmax(scores)
3. Validate max(scores) > 0.5 (gate criterion)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M3-1 | silhouette_eval | Compute scores for k=2-5, select optimal k, validate threshold |

---

## A-M4: Bootstrap Validation [Complexity: 14, Budget: 1]

**Applied**: NumPy random resampling pattern

### API Signatures

```python
class BootstrapClusterValidator:
    """Bootstrap resampling for cluster stability validation."""
    
    def __init__(
        self, 
        benchmark_data: pd.DataFrame,
        optimal_k: int,
        n_iterations: int = 1000,
        random_seed: int = 42
    ):
        """
        Args:
            benchmark_data: [N, 6] from H_E1_DataLoader.load_benchmark_scores()
            optimal_k: Number of clusters from silhouette evaluation
            n_iterations: Bootstrap iterations (default: 1000)
            random_seed: Reproducibility seed
        """
        self.data = benchmark_data
        self.k = optimal_k
        self.n_iter = n_iterations
        self.seed = random_seed
    
    def run_bootstrap(self) -> np.ndarray:
        """
        Execute bootstrap resampling loop.
        
        Returns:
            consistency_matrix: [3, 3] co-occurrence percentages
        """
        ...
    
    def compute_consistency_matrix(
        self, 
        co_occurrence_counts: np.ndarray
    ) -> Tuple[np.ndarray, float]:
        """
        Convert counts to percentages and compute mean.
        
        Args:
            co_occurrence_counts: [3, 3] raw counts from bootstrap
        
        Returns:
            (consistency_matrix, mean_consistency) where mean_consistency >= 80.0 for gate pass
        """
        ...
```

### Pseudo-code

```
1. Initialize co_occurrence_matrix = zeros([3, 3])
2. For iteration in range(1000):
     a. resample_indices = np.random.choice(N, size=N, replace=True)
     b. bootstrap_df = data.iloc[resample_indices]
     c. corr_matrix_i = compute_pairwise_correlations(bootstrap_df)
     d. dist_matrix_i = 1 - abs(corr_matrix_i)
     e. linkage_i = ward_linkage(dist_matrix_i)
     f. labels_i = fcluster(linkage_i, k=optimal_k)
     g. For each pair (bench_a, bench_b):
          if labels_i[a] == labels_i[b]:
              co_occurrence_matrix[a, b] += 1
3. consistency_matrix = (co_occurrence_matrix / 1000) * 100  # Percentages
4. mean_consistency = mean(consistency_matrix[upper_triangular])
5. Validate mean_consistency >= 80.0 (gate criterion)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-M4-1 | bootstrap_loop | Resample, recompute correlations, track co-clustering, validate ≥80% |

---

## External Dependencies (h-e1 Data)

### Data File Schemas

h-m1 consumes data outputs from h-e1 (not code APIs). Expected file formats:

```python
# h-e1/results/correlation_results.json
{
    "correlation_matrix": [[1.0, 0.996, 0.993], 
                           [0.996, 1.0, 0.997], 
                           [0.993, 0.997, 1.0]],  # [3, 3]
    "benchmarks": ["TruthfulQA", "AdvBench", "BOLD"],
    "p_values": [[0.0, 1.2e-18, 3.4e-17], ...],
    "sample_size": 20
}

# h-e1/data/benchmark_scores.csv
# Columns: model_name, size_stratum, params_billions, truthfulqa_score, advbench_score, bold_score
# Shape: [N, 6] where N >= 15
```

**No code imports from h-e1** - pure data-driven pipeline. If h-e1 changes its data schema, h-m1 loader (L-M1-1) must be updated to match new JSON/CSV format.

---

## Configuration Parameters

```python
# config.py
K_RANGE = [2, 3, 4, 5]  # Cluster counts to evaluate
LINKAGE_METHOD = 'ward'
N_BOOTSTRAP = 1000
RANDOM_SEED = 42
SILHOUETTE_THRESHOLD = 0.5
CONSISTENCY_THRESHOLD = 80.0
COPHENETIC_THRESHOLD = 0.7
```

---

## Gate Decision Logic

```python
def evaluate_gate(
    silhouette_scores: Dict[int, float],
    mean_consistency: float,
    optimal_k: int
) -> str:
    """
    Automated gate decision.
    
    Returns:
        'PASS' if all criteria met, else 'FAIL'
    """
    max_silhouette = max(silhouette_scores.values())
    
    if (max_silhouette > 0.5 
        and mean_consistency >= 80.0 
        and 2 <= optimal_k <= 5):
        return "PASS"
    else:
        return "FAIL"
```

---

## Visualization APIs (Optional - Not in 4-subtask budget)

**Note**: Visualization tasks (M6) were not allocated in the 4-subtask budget. If implemented later, use these signatures:

```python
def plot_dendrogram(
    linkage_matrix: np.ndarray,
    labels: list,
    optimal_k: int,
    output_path: str
):
    """Generate dendrogram with optimal k cutline marked."""
    ...

def plot_silhouette_vs_k(
    silhouette_scores: Dict[int, float],
    output_path: str
):
    """Line plot: k vs silhouette score."""
    ...

def plot_consistency_matrix(
    consistency_matrix: np.ndarray,
    output_path: str
):
    """Heatmap: 3x3 co-occurrence percentages."""
    ...
```

---

## Self-Validation

- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in code comments
- [x] Subtask count within budget (4/4 used)
- [x] Total length < 600 lines
- [x] Codebase Analysis (Serena) section included
- [x] External Dependencies section for h-e1 data schema
- [x] No imports from h-e1 code (data files only)

---

*Generated for Phase 4 Implementation*
*Allocated Subtasks: 4 (M1, M2, M3, M4)*
*Excluded: Stratified clustering (M5), Visualizations (M6), Gate reporting (M7) - implement if budget increases*
