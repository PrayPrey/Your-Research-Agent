# H-M4 Logic: Layer-wise Grassmann Distance Analysis

Applied: analysis-pipeline pattern (layer-wise decomposition), bootstrap-CI pattern, Cohen's d effect size

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M3)
**Status**: API signatures verified from actual H-M3 code via direct file read (Serena MCP had no active project)
**Analyzed Path**: `docs/youra_research/20260413_wsl/h-m3/code/`
**Relevant Symbols**:
- `load_adapter_metadata(h_e1_results_dir)` -> `list[dict]` with keys: `task`, `seed`, `category`, `adapter_path`
- `validate_distance_matrix(distance_matrix, expected_n=40)` -> None
- `_flatten_upper_triangle(matrix)` -> `np.ndarray` (1D, k=1)
- `_extract_within_cluster_distances(grassmann_matrix, adapter_meta)` -> pairs where same category, different task
- `compute_p3_control` uses `adapter_meta[i]['category']` and `adapter_meta[i]['task']` keys

**Note**: H-M3 metadata dict keys are `task`, `seed`, `category`, `adapter_path`. H-M4 `AdapterRecord` must align with these keys when reading from H-E1 results.

---

## External Dependencies (Base Hypothesis H-M3)

```python
# From: h-m3/code/grassmann_loader.py (ACTUAL CODE)
def load_adapter_metadata(h_e1_results_dir: str) -> list[dict]:
    # Returns list of dicts: {adapter_path, task, seed, category}
    # Reads h-e1/results/adapter_metadata.json
    # Validates N_ADAPTERS == 40, required keys present
    ...

def validate_distance_matrix(
    distance_matrix: np.ndarray,
    expected_n: int = 40,
) -> None:
    # Checks shape, symmetry, zero diagonal, finite values
    ...

# From: h-m3/code/correlation.py (ACTUAL CODE)
def _flatten_upper_triangle(matrix: np.ndarray) -> np.ndarray:
    # np.triu_indices(n, k=1) -> 1D array length N*(N-1)/2
    ...

def _extract_within_cluster_distances(
    grassmann_matrix: np.ndarray,
    adapter_meta: list[dict],  # keys: task, seed, category
) -> np.ndarray:
    # Pairs: same category, different task
    ...
```

**Verified from**: `h-m3/code/grassmann_loader.py`, `h-m3/code/correlation.py`

---

## A-3: Grassmann Distance [Complexity: 14, Budget: 4 subtasks]

Applied: QR+SVD Grassmann geodesic distance pattern

### API Signatures

```python
# layer_distances.py

import numpy as np
from typing import Optional

def grassmann_distance(A: np.ndarray, B: np.ndarray) -> float:
    """Grassmann geodesic distance between column spaces of A and B."""
    # A: [dim, r], B: [dim, r] -> scalar

def compute_layer_type_distance_matrix(
    all_b_matrices: np.ndarray,
    layer_idx_list: Optional[list[int]] = None,
) -> np.ndarray:
    """Pairwise distance matrix averaged over transformer layers.
    all_b_matrices: [40, 22, dim, r] -> [40, 40]
    """

def compute_all_layer_type_distances(
    records: list,          # list[AdapterRecord]
    layer_types: list[str],
    h_e1_adapter_dir: str,
) -> dict[str, np.ndarray]:
    """Returns {layer_type: (40, 40)} for all 7 layer types."""

def save_layer_distances(distances: dict[str, np.ndarray], output_path: str) -> None:
    """Save as .npz with layer_type keys."""

def load_layer_distances(path: str) -> dict[str, np.ndarray]:
    """Load .npz, return {layer_type: (40, 40)}."""
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| A, B | [dim, r] | Single layer B matrix; dim varies by layer type |
| Q_A, Q_B | [dim, r] | After QR decomposition |
| M | [r, r] | Q_A.T @ Q_B |
| S | [r] | Singular values of M, clamped to [-1, 1] |
| all_b_matrices | [40, 22, dim, r] | Per layer type; r=32 |
| dist_matrix | [40, 40] | Symmetric, zero diagonal |

### Pseudo-code: grassmann_distance

```
1. Q_A, _ = np.linalg.qr(A)              # [dim, r]
2. Q_B, _ = np.linalg.qr(B)              # [dim, r]
3. M = Q_A.T @ Q_B                        # [r, r]
4. _, S, _ = np.linalg.svd(M, full_matrices=False)  # [r]
5. S = np.clip(S, -1.0, 1.0)             # numerical stability
6. angles = np.arccos(S)                  # principal angles [r]
7. return float(np.linalg.norm(angles))   # Frobenius norm
```

### Pseudo-code: compute_layer_type_distance_matrix

```
1. n = all_b_matrices.shape[0]           # 40
2. dist = zeros(n, n)
3. for i in range(n):
4.   for j in range(i+1, n):
5.     layer_dists = []
6.     for l in range(22):
7.       d = grassmann_distance(all_b_matrices[i, l], all_b_matrices[j, l])
8.       layer_dists.append(d)
9.     dist[i,j] = dist[j,i] = mean(layer_dists)
10. return dist   # [40, 40]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | QR decomposition | `grassmann_distance`: QR + SVD + arccos norm |
| L-3-2 | load_all_b_matrices | Load safetensors, filter by layer_type key, return [40, 22, dim, r] |
| L-3-3 | compute_layer_type_distance_matrix | Pairwise [40,40] averaging over 22 layers |
| L-3-4 | compute_all_layer_type_distances + save/load | Loop over 7 types, save/load .npz |

---

## A-4: Statistical Analysis [Complexity: 15, Budget: 4 subtasks]

Applied: Cohen's d pooled-std pattern, pingouin bootstrap CI pattern

### API Signatures

```python
# statistics.py

import numpy as np
from typing import TypedDict
import pingouin

class CohensDResult(TypedDict):
    layer_type: str
    cohens_d: float
    ci_low: float
    ci_high: float
    p_value: float
    n_within: int
    n_between: int

def split_within_between(
    distance_matrix: np.ndarray,   # [40, 40]
    records: list,                  # list[AdapterRecord] or list[dict] with .category
) -> tuple[np.ndarray, np.ndarray]:
    """Split upper-triangle pairs by category match.
    Returns (within, between): 1D distance arrays, diagonal excluded.
    """

def compute_cohens_d_with_ci(
    within: np.ndarray,             # 1D distances, same category
    between: np.ndarray,            # 1D distances, different category
    n_bootstrap: int = 2000,
    random_seed: int = 42,
    ci_level: float = 0.95,
) -> tuple[float, float, float]:
    """Returns (cohens_d, ci_low, ci_high)."""

def analyze_all_layer_types(
    distances: dict[str, np.ndarray],  # {layer_type: [40,40]}
    records: list,
    n_bootstrap: int = 2000,
    random_seed: int = 42,
) -> list[CohensDResult]:
    """Returns list sorted by cohens_d descending."""

def compute_group_statistics(
    results: list[CohensDResult],
    attention_types: list[str],
    mlp_types: list[str],
) -> dict:
    """Returns {attention_mean, attention_std, mlp_mean, mlp_std, p_value, group_difference}."""

def evaluate_gate(
    results: list[CohensDResult],
    threshold: float = 0.8,
) -> dict:
    """Returns {passed, best_layer, max_d, layers_above_threshold}."""
```

### Pseudo-code: split_within_between

```
1. n = 40
2. within, between = [], []
3. for i in range(n):
4.   for j in range(i+1, n):
5.     cat_i = records[i].category  # "reasoning" | "nlu"
6.     cat_j = records[j].category
7.     d = distance_matrix[i, j]
8.     if cat_i == cat_j:
9.       within.append(d)
10.    else:
11.      between.append(d)
12. return np.array(within), np.array(between)
```

### Pseudo-code: compute_cohens_d_with_ci

```
1. mean_w = mean(within)
2. mean_b = mean(between)
3. n_w, n_b = len(within), len(between)
4. pooled_std = sqrt(((n_w-1)*var(within) + (n_b-1)*var(between)) / (n_w+n_b-2))
5. d = (mean_b - mean_w) / pooled_std   # positive = between > within (clustering signal)
6. # Bootstrap CI via pingouin
7. combined = concatenate([within, between])
8. labels = [0]*n_w + [1]*n_b
9. ci = pingouin.compute_bootci(
       x=combined, func=lambda x: cohens_d_func(x[:n_w], x[n_w:]),
       n_boot=n_bootstrap, seed=random_seed, confidence=ci_level
   )
   # Alternative: manual bootstrap if pingouin API mismatch
10. return (d, ci[0], ci[1])
```

### Pseudo-code: compute_group_statistics

```
1. attn_d = [r['cohens_d'] for r in results if r['layer_type'] in attention_types]
2. mlp_d  = [r['cohens_d'] for r in results if r['layer_type'] in mlp_types]
3. from scipy.stats import mannwhitneyu
4. stat, p = mannwhitneyu(attn_d, mlp_d, alternative='two-sided')
5. return {
     attention_mean: mean(attn_d), attention_std: std(attn_d),
     mlp_mean: mean(mlp_d), mlp_std: std(mlp_d),
     p_value: p,
     group_difference: mean(attn_d) - mean(mlp_d)
   }
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | split_within_between | Upper-triangle pair split by category membership |
| L-4-2 | compute_cohens_d_with_ci | Pooled-std Cohen's d + pingouin bootstrap CI |
| L-4-3 | analyze_all_layer_types + compute_group_statistics | Loop over 7 types, Mann-Whitney group test |
| L-4-4 | evaluate_gate | Threshold check, best_layer identification, JSON output |
