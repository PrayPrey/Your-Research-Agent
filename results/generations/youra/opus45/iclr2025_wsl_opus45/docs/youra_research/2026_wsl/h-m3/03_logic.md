# Logic: H-M3 - FLAN Taxonomy Correlation with Grassmann Distances

Applied: spearman-bootstrap-ci pattern
Applied: correlation-analysis-reuse pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from filesystem read (Serena project activation unavailable for this project)
**Analyzed Path**: `docs/youra_research/20260413_wsl/h-e1/code/analyze.py`
**Relevant Symbols**:
- `extract_b_matrices(adapter_path: str) -> dict` - returns layer_name -> B_matrix
- `compute_orthonormal_basis(B: np.ndarray) -> np.ndarray` - QR decomp, returns Q [d_out, r]
- `grassmann_distance(B1: np.ndarray, B2: np.ndarray) -> float`
- `compute_pairwise_matrix(adapter_paths: list, aggregate: str = "mean") -> tuple[ndarray, list[dict]]`
- `split_within_between(distance_matrix: np.ndarray, adapter_meta: list) -> tuple[ndarray, ndarray]`
- `_bootstrap_ci(within: np.ndarray, between: np.ndarray, n_boot: int = 10000, alpha: float = 0.05) -> tuple[float, float]`

---

## External Dependencies API

### API Signatures (From Actual H-E1 Code)

```python
# From: h-e1/code/analyze.py (ACTUAL CODE)

def extract_b_matrices(adapter_path: str) -> dict:
    """Returns {layer_name: B_matrix (np.ndarray)}"""
    ...

def compute_orthonormal_basis(B: np.ndarray) -> np.ndarray:
    """B: [d_out, r] -> Q: [d_out, r]"""
    ...

def grassmann_distance(B1: np.ndarray, B2: np.ndarray) -> float:
    """B1, B2: [d_out, r] -> scalar distance"""
    ...

def compute_pairwise_matrix(
    adapter_paths: list,
    aggregate: str = "mean"          # "mean" or "sum"
) -> tuple:                          # (distance_matrix [N,N], adapter_meta list[dict])
    ...

def split_within_between(
    distance_matrix: np.ndarray,     # [N, N]
    adapter_meta: list               # list of {adapter_path, task, seed, category}
) -> tuple:                          # (within_distances [K], between_distances [M])
    ...

def _bootstrap_ci(
    within: np.ndarray,
    between: np.ndarray,
    n_boot: int = 10000,
    alpha: float = 0.05,
) -> tuple:                          # (lower: float, upper: float)
    # Note: bootstraps (between_mean - within_mean), sets seed=42 internally
    ...
```

**Verified from**: `docs/youra_research/20260413_wsl/h-e1/code/analyze.py` (actual implementation)

**Key Notes**:
- `_bootstrap_ci` bootstraps the difference (between - within), NOT correlation.
  H-M3 must implement its own bootstrap for Spearman rho.
- `adapter_meta` dict keys: `adapter_path`, `task`, `seed`, `category`
- `compute_pairwise_matrix` returns meta with `category` from `TASK_CATEGORIES`

---

## A-2: GrassmannLoader [Complexity: 9, Budget: 2 subtasks]

Applied: Standard NumPy load/validate pattern

### API Signatures

```python
# grassmann_loader.py

def load_or_compute_distances(
    h_e1_hypothesis_dir: str,
    force_recompute: bool = False,
) -> tuple[np.ndarray, list[dict]]:
    """Load pairwise_distances.npy + adapter_metadata.json from H-E1, or recompute.
    Returns (distance_matrix [40,40], adapter_meta list[dict])."""
    ...

def validate_distance_matrix(
    distance_matrix: np.ndarray,
    expected_n: int = 40,
) -> None:
    """Assert shape (N,N), symmetric (allclose), zero diagonal, all finite. Raises ValueError."""
    ...

def load_adapter_metadata(
    h_e1_results_dir: str,
) -> list[dict]:
    """Load adapter_metadata.json. Each dict: {adapter_path, task, seed, category}."""
    ...
```

### Pseudo-code

```
load_or_compute_distances(h_e1_hypothesis_dir, force_recompute):
    results_dir = h_e1_hypothesis_dir / "results"
    npy_path = results_dir / "pairwise_distances.npy"
    meta_path = results_dir / "adapter_metadata.json"

    if not force_recompute and npy_path.exists() and meta_path.exists():
        dist = np.load(npy_path)
        meta = json.load(meta_path)
        validate_distance_matrix(dist)
        return dist, meta

    # Fallback: recompute via H-E1 bridge
    adapter_dir = h_e1_hypothesis_dir / "adapters"
    adapter_paths = sorted([p for p in adapter_dir.iterdir() if "_seed" in p.name])
    dist, meta = compute_pairwise_matrix(adapter_paths)   # H-E1 bridge
    validate_distance_matrix(dist)
    np.save(npy_path, dist)
    json.dump(meta, meta_path)
    return dist, meta
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | load_or_compute | Load from H-E1 results with fallback recompute |
| L-2-2 | validate | Shape, symmetry, diagonal, finite checks |

---

## A-5: Spearman Correlation [Complexity: 12, Budget: 3 subtasks]

Applied: spearman-bootstrap-ci pattern

### API Signatures

```python
# correlation.py

class CorrelationResult(NamedTuple):
    spearman_rho: float
    p_value: float
    ci_low: float
    ci_high: float
    n_pairs: int
    gate_passed: bool   # rho > 0.3 AND p < 0.05

def compute_spearman_correlation(
    grassmann_matrix: np.ndarray,   # [N, N]
    taxonomy_matrix: np.ndarray,    # [N, N]
    n_bootstrap: int = 1000,
    random_seed: int = 42,
) -> CorrelationResult:
    """Flatten upper triangles (k=1), scipy spearmanr, bootstrap 95% CI on rho."""
    ...

def _flatten_upper_triangle(matrix: np.ndarray) -> np.ndarray:
    """np.triu_indices(n, k=1) -> 1D array [N*(N-1)/2]"""
    ...

def _bootstrap_spearman_ci(
    x: np.ndarray,          # [K] flattened grassmann
    y: np.ndarray,          # [K] flattened taxonomy
    n_bootstrap: int = 1000,
    random_seed: int = 42,
    alpha: float = 0.05,
) -> tuple[float, float]:   # (ci_low, ci_high)
    """Bootstrap CI for Spearman rho by resampling paired (x,y) rows."""
    ...
```

### Pseudo-code

```
compute_spearman_correlation(grassmann_matrix, taxonomy_matrix, n_bootstrap, random_seed):
    g_flat = _flatten_upper_triangle(grassmann_matrix)   # [780]
    t_flat = _flatten_upper_triangle(taxonomy_matrix)    # [780]
    rho, p_value = spearmanr(g_flat, t_flat)
    ci_low, ci_high = _bootstrap_spearman_ci(g_flat, t_flat, n_bootstrap, random_seed)
    gate_passed = (rho > 0.3) and (p_value < 0.05)
    return CorrelationResult(rho, p_value, ci_low, ci_high, len(g_flat), gate_passed)

_bootstrap_spearman_ci(x, y, n_bootstrap, random_seed, alpha):
    rng = np.random.default_rng(random_seed)
    rhos = []
    for _ in range(n_bootstrap):
        idx = rng.integers(0, len(x), size=len(x))
        rho_b, _ = spearmanr(x[idx], y[idx])
        rhos.append(rho_b)
    return percentile(rhos, 2.5), percentile(rhos, 97.5)
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|-------|
| grassmann_matrix | [40, 40] | symmetric, zero diag |
| taxonomy_matrix | [40, 40] | binary 0/1 |
| g_flat / t_flat | [780] | 40*39/2 upper triangle pairs |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | flatten + spearmanr | _flatten_upper_triangle + scipy.stats.spearmanr call |
| L-5-2 | bootstrap_ci | _bootstrap_spearman_ci with paired resampling |
| L-5-3 | gate_eval | CorrelationResult assembly + gate_passed logic |

---

## A-6: P3 Control Analysis [Complexity: 11, Budget: 3 subtasks]

Applied: within-between split pattern (extended from H-E1 split_within_between)

### API Signatures

```python
# correlation.py (continued)

class P3ControlResult(NamedTuple):
    within_task_mean: float
    within_cluster_mean: float
    ratio: float                # within_task_mean / within_cluster_mean
    control_passed: bool        # ratio < 0.5

def compute_p3_control(
    grassmann_matrix: np.ndarray,   # [N, N]
    adapter_meta: list[dict],       # [{task, seed, category, ...}]
    ratio_threshold: float = 0.5,
) -> P3ControlResult:
    """Within-task (same task, diff seed) vs within-cluster (same category, diff task)."""
    ...

def _extract_within_task_distances(
    grassmann_matrix: np.ndarray,
    adapter_meta: list[dict],
) -> np.ndarray:
    """Pairs where meta[i]['task'] == meta[j]['task'] and i < j."""
    ...

def _extract_within_cluster_distances(
    grassmann_matrix: np.ndarray,
    adapter_meta: list[dict],
) -> np.ndarray:
    """Pairs where same category but different tasks and i < j."""
    ...
```

### Pseudo-code

```
_extract_within_task_distances(grassmann_matrix, adapter_meta):
    distances = []
    for i < j:
        if meta[i]['task'] == meta[j]['task']:
            distances.append(grassmann_matrix[i,j])
    return np.array(distances)   # [N_within_task] = 8 tasks * C(5,2) = 80

_extract_within_cluster_distances(grassmann_matrix, adapter_meta):
    distances = []
    for i < j:
        if meta[i]['category'] == meta[j]['category']
           AND meta[i]['task'] != meta[j]['task']:
            distances.append(grassmann_matrix[i,j])
    return np.array(distances)   # [N_within_cluster] = 2 clusters * C(20,2) - within_task

compute_p3_control(grassmann_matrix, adapter_meta, ratio_threshold):
    wt = _extract_within_task_distances(...)
    wc = _extract_within_cluster_distances(...)
    ratio = wt.mean() / wc.mean()
    return P3ControlResult(wt.mean(), wc.mean(), ratio, ratio < ratio_threshold)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | within_task_extract | Same task, diff seed pair extraction |
| L-6-2 | within_cluster_extract | Same category, diff task pair extraction |
| L-6-3 | ratio_gate | Mean ratio computation + control_passed gate |

---

## A-12: Orchestration [Complexity: 10, Budget: 2 subtasks]

Applied: Standard PyTorch

### API Signatures

```python
# run_experiment.py

def run(force_recompute: bool = False) -> dict:
    """Wire all modules. Returns combined results dict.
    Steps: load distances -> build taxonomy -> correlate + P3 -> save -> figures -> print."""
    ...

def print_gate_summary(corr: CorrelationResult, p3: P3ControlResult) -> None:
    """Structured PASS/FAIL print: rho, p-value, CI, P3 ratio."""
    ...

def parse_args() -> argparse.Namespace:
    """--force-recompute flag."""
    ...
```

### Pseudo-code

```
run(force_recompute):
    # 1. Load Grassmann distances
    dist_matrix, adapter_meta = load_or_compute_distances(H_E1_HYPOTHESIS_DIR, force_recompute)

    # 2. Build taxonomy matrix
    task_labels = extract_task_labels_from_meta(adapter_meta)
    taxonomy_matrix = build_taxonomy_distance_matrix(task_labels, FLAN_CATEGORIES)

    # 3. Correlation + P3
    corr = compute_spearman_correlation(dist_matrix, taxonomy_matrix,
                                        n_bootstrap=ANALYSIS_CONFIG['n_bootstrap'],
                                        random_seed=ANALYSIS_CONFIG['random_seed'])
    p3 = compute_p3_control(dist_matrix, adapter_meta,
                             ratio_threshold=ANALYSIS_CONFIG['p3_ratio_threshold'])

    # 4. Save results
    save_correlation_results(corr, p3, RESULTS_DIR)
    save_taxonomy_matrix(taxonomy_matrix, RESULTS_DIR)

    # 5. Figures
    generate_all_figures(HYPOTHESIS_FOLDER, dist_matrix, taxonomy_matrix, adapter_meta, corr, p3)

    # 6. Summary
    print_gate_summary(corr, p3)

    return {**corr._asdict(), **p3._asdict()}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-12-1 | run_wiring | Sequential module calls with error handling |
| L-12-2 | gate_summary | print_gate_summary + return dict formatting |
