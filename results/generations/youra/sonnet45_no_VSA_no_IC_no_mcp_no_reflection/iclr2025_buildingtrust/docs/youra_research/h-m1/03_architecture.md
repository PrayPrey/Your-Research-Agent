# Architecture: h-m1

**Hypothesis:** Hierarchical clustering (Ward linkage) applied to correlation matrices identifies 2-5 distinct failure mode clusters with silhouette score > 0.5 and ≥80% bootstrap consistency (1000 iterations)

**Type:** MECHANISM
**Date:** 2026-08-28

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation from scratch
**Analyzed Path:** N/A
**Findings:** h-e1 code not yet implemented - statistical clustering pipeline will reuse h-e1 data schema

---

## Architecture Pattern

Applied: Statistical clustering pipeline (load h-e1 data → cluster → bootstrap validate → visualize)

---

## Module Structure

### DataLoader (`data_loader.py`)

**Dependencies:** pandas, numpy, json

```python
class H_E1_DataLoader:
    def load_correlation_matrix(self, h_e1_path: str) -> np.ndarray: ...
    def load_benchmark_scores(self, h_e1_path: str) -> pd.DataFrame: ...
    def compute_distance_matrix(self, corr_matrix: np.ndarray) -> np.ndarray: ...
    def stratify_models(self, df: pd.DataFrame) -> dict: ...
```

### ClusterAnalyzer (`clustering.py`)

**Dependencies:** scipy.cluster.hierarchy, numpy

```python
class WardClusterer:
    def __init__(self, distance_matrix: np.ndarray): ...
    def fit(self, method: str = 'ward') -> np.ndarray: ...
    def get_clusters(self, k: int) -> np.ndarray: ...
    def compute_cophenetic(self) -> float: ...
```

### ClusterMetrics (`metrics.py`)

**Dependencies:** sklearn.metrics, numpy

```python
def silhouette_score_for_k(distance_matrix: np.ndarray, labels: np.ndarray) -> float: ...
def find_optimal_k(distance_matrix: np.ndarray, linkage_matrix: np.ndarray, k_range: list) -> tuple: ...
```

### BootstrapValidator (`bootstrap.py`)

**Dependencies:** numpy, pandas, scipy

```python
class BootstrapClusterValidator:
    def __init__(self, benchmark_data: pd.DataFrame, optimal_k: int, n_iterations: int = 1000): ...
    def run_bootstrap(self) -> np.ndarray: ...
    def compute_consistency_matrix(self) -> dict: ...
```

### Visualizer (`visualizations.py`)

**Dependencies:** matplotlib, seaborn, scipy

```python
def plot_dendrogram(linkage_matrix: np.ndarray, labels: list, optimal_k: int, output_path: str): ...
def plot_silhouette_vs_k(silhouette_scores: dict, output_path: str): ...
def plot_consistency_matrix(consistency_matrix: np.ndarray, output_path: str): ...
```

### Main (`main.py`)

**Dependencies:** All above modules, argparse

```python
def run_clustering_analysis(h_e1_results_path: str, output_dir: str, n_bootstrap: int = 1000):
    # 1. Load h-e1 correlation matrix
    # 2. Apply Ward linkage
    # 3. Evaluate silhouette scores for k=2-5
    # 4. Run bootstrap validation
    # 5. Stratified clustering analysis
    # 6. Generate visualizations
    # 7. Save gate decision report
    ...
```

---

## File Organization

```
h-m1/
├── code/
│   ├── data_loader.py           # Load h-e1 correlation results
│   ├── clustering.py             # Ward linkage clustering
│   ├── metrics.py                # Silhouette, cophenetic correlation
│   ├── bootstrap.py              # Bootstrap consistency validation
│   ├── visualizations.py         # Dendrogram, silhouette plots
│   ├── main.py                   # Orchestration
│   └── requirements.txt          # scipy, sklearn, pandas, matplotlib, seaborn
├── data/
│   ├── correlation_distance_matrix.npy   # Cached distance matrix
│   └── stratified_correlations/          # Small/medium/large strata
├── results/
│   ├── clustering_results.json           # Cluster assignments, silhouette scores
│   ├── bootstrap_consistency.json        # Consistency matrix
│   └── gate_decision.json                # PASS/FAIL status
└── figures/
    ├── dendrogram.png
    ├── silhouette_vs_k.png
    └── consistency_matrix.png
```

---

## Data Flow

```
h-e1/results/correlation_results.json → DataLoader → WardClusterer → ClusterMetrics → BootstrapValidator
                                                           ↓                ↓              ↓
                                                  linkage_matrix   silhouette_scores  consistency_matrix
                                                           ↓                ↓              ↓
                                                       Visualizer → figures/
                                                           ↓
                                                  gate_decision.json
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M1 | Data Loading | Load h-e1 correlation matrix, compute distance matrix, stratify models | 6 | load_json(1) + distance_transform(2) + stratify(2) + cache(1) |
| M2 | Ward Linkage Clustering | Implement hierarchical clustering for k=2-5, compute cophenetic correlation | 8 | linkage(3) + fcluster(2) + cophenetic(2) + validation(1) |
| M3 | Silhouette Evaluation | Compute silhouette scores for k=2-5, identify optimal k | 7 | compute_silhouette(3) + find_optimal_k(2) + store_results(2) |
| M4 | Bootstrap Validation | 1000-iteration bootstrap resampling, cluster consistency tracking | 14 | resample_loop(5) + correlation_recompute(4) + consistency_matrix(3) + mean_threshold(2) |
| M5 | Stratified Clustering | Apply Ward linkage to small/medium/large strata for h-m4 prep | 9 | stratify_data(2) + cluster_per_stratum(4) + compare_structures(3) |
| M6 | Visualizations | Generate dendrogram, silhouette vs k, consistency matrix plots | 9 | dendrogram(4) + silhouette_plot(2) + consistency_heatmap(3) |
| M7 | Gate Decision Logic | Evaluate gate criteria, generate validation report, update verification state | 6 | check_criteria(2) + generate_report(3) + update_state(1) |

**Distribution:** VeryHigh(18-20): [], High(14-17): [M4], Medium(9-13): [M5, M6], Low(4-8): [M1, M2, M3, M7]

**Total Complexity:** 59

---

## Interface Contracts

### DataLoader → WardClusterer

```python
# Input: distance_matrix (n_benchmarks × n_benchmarks, positive semi-definite)
# Output: linkage_matrix (n-1 × 4), cluster_labels (n_benchmarks,)
```

### WardClusterer → ClusterMetrics

```python
# Input: distance_matrix, cluster_labels for each k
# Output: dict {k: silhouette_score}, optimal_k: int
```

### BootstrapValidator Input

```python
# Input: benchmark_data (20 models × 3 benchmarks), optimal_k
# Output: consistency_matrix (n_benchmarks × n_benchmarks), mean_consistency: float
```

---

## Dependencies

**External:**
- scipy >= 1.7.0 (cluster.hierarchy: linkage, dendrogram, fcluster, cophenet)
- scikit-learn >= 1.0.0 (metrics.silhouette_score)
- numpy >= 1.21.0 (array operations, random seeding)
- pandas >= 1.3.0 (data loading, stratification)
- matplotlib >= 3.4.0 (dendrogram visualization)
- seaborn >= 0.11.0 (heatmaps)

**Internal:** None (h-e1 code not implemented yet - will read h-e1 data files directly)

---

## External Dependencies (h-e1 Data Files)

### Data Paths (Expected from h-e1)

| Asset | Path | Format | Description |
|-------|------|--------|-------------|
| Correlation matrix | `h-e1/results/correlation_results.json` | JSON | 3×3 Spearman correlations |
| Benchmark scores | `h-e1/data/benchmark_scores.csv` | CSV | 20 models × 3 benchmarks + size_stratum |

**Note:** h-e1 code not yet implemented, but data schema defined in h-e1/03_architecture.md

---

## Gate Decision Logic

### Primary Metrics (MUST_WORK Gate)

```python
def evaluate_gate(silhouette_scores: dict, mean_consistency: float, optimal_k: int) -> str:
    if max(silhouette_scores.values()) > 0.5 and mean_consistency >= 80.0 and 2 <= optimal_k <= 5:
        return "PASS"
    else:
        return "FAIL"
```

### Success Criteria

1. Silhouette score > 0.5 for at least one k in [2,5]
2. Bootstrap consistency ≥80% across all benchmark pairs
3. 2-5 distinct clusters identified
4. Cophenetic correlation > 0.7 (dendrogram quality)

---

## Validation Checkpoints

1. **Data Loading:** Distance matrix symmetric, positive semi-definite, in [0, 2] range
2. **Clustering:** Linkage matrix produces valid dendrogram, no degenerate clusters
3. **Silhouette:** At least one k achieves >0.5 score
4. **Bootstrap:** Mean consistency ≥80%, runtime ≤15 minutes
5. **Stratified:** Cluster structures qualitatively similar across strata
6. **Gate Decision:** Automated PASS/FAIL based on metrics

---

## Configuration Parameters

```python
# config.py
K_RANGE = [2, 3, 4, 5]  # Cluster counts to evaluate
LINKAGE_METHOD = 'ward'  # Hierarchical clustering method
N_BOOTSTRAP = 1000       # Bootstrap iterations
RANDOM_SEED = 42         # Reproducibility
SILHOUETTE_THRESHOLD = 0.5
CONSISTENCY_THRESHOLD = 80.0
COPHENETIC_THRESHOLD = 0.7
```

---

## Performance Requirements

**Runtime Targets:**
- Data loading + distance computation: <1 minute
- Ward linkage clustering: <1 second
- Silhouette score evaluation (k=2-5): <1 second
- Bootstrap validation (1000 iterations): 5-10 minutes
- Stratified clustering: <5 seconds
- Visualization generation: <30 seconds

**Total:** ~10-15 minutes on standard CPU

**Memory:** <200 MB (small correlation matrices, 20 models)

---

## Reproducibility

**Fixed random seed:** `np.random.seed(42)` for bootstrap resampling

**Cached artifacts:**
- `correlation_distance_matrix.npy` (avoid recomputation)
- `clustering_results.json` (intermediate results)

**Version control:** Document scipy/sklearn versions in requirements.txt

---

## Notes

- No model training - pure statistical analysis
- Reuses h-e1 validated correlation data (r > 0.99 confirmed)
- Stratified clustering prepares for h-m4 Mantel test
- Bootstrap validation is critical path (10 minutes runtime)
- Single-file modules (no subpackages for standard clustering)
- Dendrogram visualization must be publication-ready
