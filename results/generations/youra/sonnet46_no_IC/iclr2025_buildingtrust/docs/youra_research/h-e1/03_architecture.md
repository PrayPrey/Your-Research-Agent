# Architecture: H-E1
## Partial Spearman Correlation Structure in LLM Trustworthiness Dimensions

**Hypothesis Type:** EXISTENCE (PoC)
**Date:** 2026-08-04
**Applied:** OLS-residualization-then-rank-correlation pattern (KB domain mismatch; diffusion model content only)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze
**Analyzed Path:** N/A
**Findings:** New implementation from scratch. No prior codebase. Serena skipped.

---

## File Organization

```
h-e1/code/
├── data_loader.py       # TrustLLM JSON parsing + model annotation
├── analysis.py          # Partial Spearman + baseline Spearman + sensitivity
├── clustering.py        # Average-linkage clustering + silhouette
├── visualization.py     # All figures → h-e1/figures/
├── main.py              # Orchestration + gate check + results JSON
└── requirements.txt
h-e1/figures/            # PNG outputs (300 DPI)
h-e1/experiment_results_phase3.json
h-e1/experiment.log
```

---

## Module Interfaces

### DataLoader (`h-e1/code/data_loader.py`)

**Dependencies:** numpy, pandas, statsmodels

```python
MODEL_ANNOTATIONS: dict[str, dict]  # {model_name: {log10_params, is_RLHF}}
DIMENSIONS: list[str]               # 6 dimension names

def load_trustllm_scores(results_dir: str) -> pd.DataFrame: ...
# Returns 16×6 DataFrame (rows=models, cols=dimensions), scores in [0,1]

def add_annotations(scores_df: pd.DataFrame) -> pd.DataFrame: ...
# Adds log10_params, is_RLHF columns; raises ValueError if model missing

def validate(df: pd.DataFrame) -> dict: ...
# Returns {missing_count, floor_ceiling_flags, vif_log10, vif_rlhf}
# Raises if missing >= 3 per dimension; warns VIF > 5
```

---

### Analysis (`h-e1/code/analysis.py`)

**Dependencies:** numpy, pandas, scipy, sklearn

```python
def raw_spearman_matrix(scores_df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]: ...
# Returns (rho_6x6, pval_6x6) — baseline uncontrolled Spearman

def ols_residualize(scores_df: pd.DataFrame, covariates_df: pd.DataFrame) -> pd.DataFrame: ...
# Returns 16×6 residuals DataFrame

def partial_spearman_matrix(
    scores_df: pd.DataFrame,
    covariates_df: pd.DataFrame,
    alpha_bonferroni: float = 0.0033
) -> tuple[np.ndarray, np.ndarray, list[tuple]]: ...
# Returns (rho_partial_6x6, pval_6x6, significant_pairs)
# significant_pairs: [(dim_i, dim_j, rho, pval), ...]
# t-stat df = n - 2 - k = 12

def partial_pearson_matrix(
    scores_df: pd.DataFrame,
    covariates_df: pd.DataFrame
) -> np.ndarray: ...
# Returns rho_pearson_partial_6x6 for sensitivity check

def check_sign_divergence(rho_spearman: np.ndarray, rho_pearson: np.ndarray) -> list[tuple]: ...
# Returns list of (i, j) pairs where Spearman and Pearson sign differ
```

---

### Clustering (`h-e1/code/clustering.py`)

**Dependencies:** numpy, scipy, sklearn, networkx

```python
def build_distance_matrix(rho_partial: np.ndarray) -> np.ndarray: ...
# D = 1 - |rho_partial|, diagonal = 0

def run_clustering(dist_matrix: np.ndarray, n_clusters: int = 2) -> tuple[np.ndarray, float]: ...
# average-linkage with precomputed distance
# Returns (labels_6, silhouette_score)
# ponytail: average linkage chosen; Ward needs euclidean, use Ward on feature matrix if linkage matters

def build_mst(rho_partial: np.ndarray, dim_names: list[str]) -> "nx.Graph": ...
# Returns networkx MST weighted by 1 - |rho_partial| (H-E2 prerequisite output)

def get_dendrogram_linkage(dist_matrix: np.ndarray) -> np.ndarray: ...
# scipy.cluster.hierarchy.linkage for dendrogram plotting
```

---

### Visualization (`h-e1/code/visualization.py`)

**Dependencies:** matplotlib, seaborn, scipy, numpy

```python
def plot_partial_corr_bar(
    rho_partial: np.ndarray,
    pvals: np.ndarray,
    dim_names: list[str],
    alpha: float,
    out_path: str
) -> None: ...
# Bar chart |rho_partial| for 15 pairs, threshold line at 0.5, color by significance

def plot_heatmap_comparison(
    rho_raw: np.ndarray,
    rho_partial: np.ndarray,
    dim_names: list[str],
    out_path: str
) -> None: ...
# Side-by-side 6×6 heatmaps, diverging colormap

def plot_dendrogram(linkage_matrix: np.ndarray, dim_names: list[str], out_path: str) -> None: ...
# scipy dendrogram with 2-cluster color threshold

def plot_scatter_confound(
    scores_df: pd.DataFrame,
    residuals_df: pd.DataFrame,
    dim_pair: tuple[str, str],
    out_path: str
) -> None: ...
# Before/after residualization scatter for top pair, colored by is_RLHF
```

---

### Main (`h-e1/code/main.py`)

**Dependencies:** all modules, json, logging

```python
def run_experiment(trustllm_results_dir: str, output_dir: str) -> dict: ...
# Orchestrates: load → validate → analyze → cluster → visualize → serialize
# Prints gate result to console and writes experiment.log
# Returns full results dict

def check_gate(significant_pairs: list) -> bool: ...
# Returns True if len(significant_pairs) >= 1

def serialize_results(results: dict, out_path: str) -> None: ...
# Writes experiment_results_phase3.json

if __name__ == "__main__":
    # argparse: --results-dir, --output-dir
    ...
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Data Loading | Clone TrustLLM, parse results/*.json, build 16×6 DataFrame, add annotations, validate (VIF, missing, floor/ceiling) | 9 | Size(2)+Dep(2)+Algo(2)+Int(3) |
| E-2 | Baseline Analysis | Raw Spearman 6×6 matrix, p-values, sensitivity Pearson comparison, sign-divergence check | 8 | Size(2)+Dep(2)+Algo(2)+Int(2) |
| E-3 | Partial Spearman | OLS residualization, t-stat with df=12, Bonferroni correction, significant pair extraction | 12 | Size(3)+Dep(2)+Algo(4)+Int(3) |
| E-4 | Clustering | Distance matrix, average-linkage k=2, silhouette score, MST for H-E2 output | 9 | Size(2)+Dep(3)+Algo(2)+Int(2) |
| E-5 | Visualization | 4 figures (bar chart, dual heatmap, dendrogram, scatter), 300 DPI PNG | 10 | Size(3)+Dep(2)+Algo(1)+Int(4) |
| E-6 | Orchestration & Gate | main.py integration, gate check, JSON serialization, experiment.log | 8 | Size(2)+Dep(3)+Algo(1)+Int(2) |

**Distribution**: High(10-13): [E-3, E-5], Medium(7-9): [E-1, E-2, E-4, E-6], Low(1-6): []

---

## Requirements (`h-e1/code/requirements.txt`)

```
numpy>=1.24
pandas>=1.5
scipy>=1.10
scikit-learn>=1.2
networkx>=3.0
statsmodels>=0.14
matplotlib>=3.7
seaborn>=0.12
pingouin>=0.5
```
