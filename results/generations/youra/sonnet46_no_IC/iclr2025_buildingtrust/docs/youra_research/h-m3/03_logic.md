# Logic: H-M3 — Ward Clustering + Robustness Checks

**Date:** 2026-08-04
**Tasks Covered:** A-4 (Ward Clustering, complexity=9), A-6 (Robustness Checks, complexity=10)
**Applied:** Standard scipy/sklearn pattern (Archon KB returned no relevant clustering results)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from base code (h-m2/code/analysis.py)
**Analyzed Path:** docs/youra_research/h-m2/code/analysis.py
**Relevant Symbols:**
- `run_analysis(he1_code_dir, he1_results_dir, he1_json) -> dict` — pipeline entry point pattern
- `load_he1_data(he1_code_dir, he1_results_dir, he1_json) -> tuple` — loads from HE1_JSON via `json.load`
- `compute_partial_spearman(annotated_df, dim_x, dim_y, covariates) -> tuple[float, float]`
- H-M2 does NOT use clustering; H-M3 designs new Ward/silhouette pipeline from scratch

**Key finding:** H-M2 `run_analysis` signature uses `(he1_code_dir, he1_results_dir, he1_json)`. H-M3 `run_analysis` uses `(he1_json_path: str)` only — simpler, no model loading needed (rho_partial already cached).

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual H-M2 Code)

```python
# From: docs/youra_research/h-m2/code/analysis.py (ACTUAL CODE)
# H-M3 reads rho_partial directly from JSON — does NOT call h-m2 functions.
# Pattern reused: json.load + np.array(he1_data["rho_partial"])

# h-m2 load pattern (reference only):
with open(he1_json) as f:
    he1_data = json.load(f)
rho_partial = np.array(he1_data["rho_partial"])  # shape (6,6)
```

**Verified from:** `docs/youra_research/h-m2/code/analysis.py` line 32-33

---

## A-4: Ward Clustering [Complexity: 9, Budget: 9 subtasks]

### API Signatures

```python
def load_rho_partial(he1_json_path: str) -> tuple[np.ndarray, list[str]]:
    """Load 6x6 rho_partial from h-e1 JSON. Returns (rho (6,6), dims)."""
    ...

def validate_rho_matrix(rho: np.ndarray) -> None:
    """Assert shape==(6,6), symmetric, diag==1, values in [-1,1]. Raises ValueError."""
    ...

def make_distance_matrix(rho: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """d=clip(1-rho, 0, 2), diag=0. Returns (dist_matrix (6,6), condensed (15,))."""
    ...

def run_ward_clustering(
    condensed: np.ndarray,       # (15,) condensed distance vector
    dist_matrix: np.ndarray,     # (6,6) for silhouette_score(precomputed)
    n_clusters: int = 2,
) -> dict:
    """scipy Ward linkage+fcluster+silhouette. Returns result dict."""
    ...

def compute_membership_alignment(labels: np.ndarray, dims: list[str]) -> int:
    """Best-of-two label assignment vs PREDICTED sets. Returns int in [0,4]."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| rho | (6, 6) | symmetric, diag=1 |
| dist_matrix | (6, 6) | d=clip(1-rho,0,2), diag=0 |
| condensed | (15,) | squareform(dist_matrix), upper triangle |
| Z | (5, 4) | linkage matrix from scipy |
| labels | (6,) | int, values in {0,1} |

### Pseudo-code: run_ward_clustering

```
Z = linkage(condensed, method='ward')          # scipy, deterministic
labels = fcluster(Z, t=n_clusters, criterion='maxclust') - 1  # 0-indexed
sil = silhouette_score(dist_matrix, labels, metric='precomputed')
cluster_membership = {dims[i]: int(labels[i]) for i in range(6)}
return {"Z": Z, "labels": labels, "silhouette_ward": sil,
        "cluster_membership": cluster_membership}
```

**FORBIDDEN:** `AgglomerativeClustering(linkage='ward', metric='precomputed')` — sklearn #27655

### Pseudo-code: compute_membership_alignment

```
SENSITIVE = {"safety", "machine_ethics"}      # from config
INSENSITIVE = {"robustness", "privacy"}       # from config
best = 0
for sensitive_label in [0, 1]:
    count = sum(
        1 for dim, lbl in cluster_membership.items()
        if (dim in SENSITIVE and lbl == sensitive_label)
        or (dim in INSENSITIVE and lbl != sensitive_label)
    )
    best = max(best, count)
return best  # range [0, 4]
```

### Subtasks [9/9 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | load_rho_partial | json.load + np.array; extract "rho_partial" key |
| L-4-2 | validate_rho_matrix | shape, symmetry, diag, range checks; raise ValueError |
| L-4-3 | make_distance_matrix | clip(1-rho,0,2), fill_diagonal(0), squareform |
| L-4-4 | linkage call | scipy linkage(condensed, method='ward') |
| L-4-5 | fcluster+0-index | fcluster(Z, t=n_clusters, criterion='maxclust') - 1 |
| L-4-6 | silhouette_score | silhouette_score(dist_matrix, labels, metric='precomputed') |
| L-4-7 | cluster_membership dict | {dim: int(label)} for all 6 dims |
| L-4-8 | compute_membership_alignment | best-of-two label assignment loop |
| L-4-9 | run_ward_clustering return dict | assemble all outputs into result dict |

---

## A-6: Robustness Checks [Complexity: 10, Budget: 10 subtasks]

### API Signatures

```python
def run_alternative_linkages(
    dist_matrix: np.ndarray,    # (6,6) precomputed
    dims: list[str],
) -> dict:
    """Average + complete linkage via sklearn (precomputed ok for non-Ward).
    Returns {"silhouette_average": float, "silhouette_complete": float}."""
    ...

def run_k3_check(
    condensed: np.ndarray,      # (15,) condensed distances
    dist_matrix: np.ndarray,    # (6,6) for silhouette
) -> float:
    """Ward at k=3 via scipy. Returns silhouette_k3."""
    ...

def run_alt_distance(
    rho: np.ndarray,            # (6,6) raw correlation
    dims: list[str],
) -> dict:
    """d=sqrt(1-rho^2); re-run Ward. Returns {"silhouette_alt_distance": float}."""
    ...

def run_mds_projection(
    dist_matrix: np.ndarray,    # (6,6)
    seed: int = 1,
) -> np.ndarray:
    """2D MDS. Returns coords (6,2)."""
    ...
```

### Pseudo-code: run_alternative_linkages

```
# Average and complete linkage support metric='precomputed' in sklearn
for method in ['average', 'complete']:
    model = AgglomerativeClustering(n_clusters=2, metric='precomputed', linkage=method)
    labels = model.fit_predict(dist_matrix)
    sil = silhouette_score(dist_matrix, labels, metric='precomputed')
    results[f"silhouette_{method}"] = sil
return results
```

### Pseudo-code: run_k3_check

```
Z = linkage(condensed, method='ward')
labels_k3 = fcluster(Z, t=3, criterion='maxclust') - 1
return silhouette_score(dist_matrix, labels_k3, metric='precomputed')
```

### Pseudo-code: run_alt_distance

```
dist_alt = np.sqrt(np.clip(1 - rho**2, 0, 1))   # (6,6), clip for numerical safety
np.fill_diagonal(dist_alt, 0)
condensed_alt = squareform(dist_alt)
Z_alt = linkage(condensed_alt, method='ward')
labels_alt = fcluster(Z_alt, t=2, criterion='maxclust') - 1
sil_alt = silhouette_score(dist_alt, labels_alt, metric='precomputed')
return {"silhouette_alt_distance": sil_alt, "labels_alt": labels_alt}
```

### Pseudo-code: run_mds_projection

```
mds = MDS(n_components=2, dissimilarity='precomputed', random_state=seed, normalized_stress='auto')
return mds.fit_transform(dist_matrix)   # (6,2)
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | run_alternative_linkages average | sklearn AgglomerativeClustering(linkage='average', metric='precomputed') |
| L-6-2 | run_alternative_linkages complete | sklearn AgglomerativeClustering(linkage='complete', metric='precomputed') |
| L-6-3 | silhouette for average | silhouette_score(dist_matrix, labels, metric='precomputed') |
| L-6-4 | silhouette for complete | same as L-6-3 but complete labels |
| L-6-5 | run_k3_check linkage | scipy linkage(condensed, method='ward') |
| L-6-6 | run_k3_check fcluster k=3 | fcluster(Z, t=3, criterion='maxclust') - 1 |
| L-6-7 | run_k3_check silhouette | silhouette_score(dist_matrix, labels_k3, metric='precomputed') |
| L-6-8 | run_alt_distance dist construction | sqrt(clip(1-rho^2, 0,1)), fill_diagonal(0), squareform |
| L-6-9 | run_alt_distance Ward + silhouette | linkage+fcluster+silhouette on condensed_alt |
| L-6-10 | run_mds_projection | MDS(dissimilarity='precomputed', random_state=seed).fit_transform |

---

## Full Pipeline: run_analysis

```python
def run_analysis(he1_json_path: str) -> dict:
    """Full pipeline. Returns serializable results dict."""
    rho, dims = load_rho_partial(he1_json_path)
    validate_rho_matrix(rho)
    dist_matrix, condensed = make_distance_matrix(rho)

    ward = run_ward_clustering(condensed, dist_matrix, n_clusters=2)
    alignment = compute_membership_alignment(ward["labels"], dims)

    alt_linkages = run_alternative_linkages(dist_matrix, dims)
    sil_k3 = run_k3_check(condensed, dist_matrix)
    alt_dist = run_alt_distance(rho, dims)
    coords = run_mds_projection(dist_matrix, seed=1)

    return {
        "rho": rho,
        "dims": dims,
        "dist_matrix": dist_matrix,
        "condensed": condensed,
        "Z": ward["Z"],
        "labels": ward["labels"],
        "silhouette_ward": ward["silhouette_ward"],
        "cluster_membership": ward["cluster_membership"],
        "membership_alignment": alignment,
        "primary_gate_pass": ward["silhouette_ward"] > 0.3,
        "secondary_gate_pass": alignment >= 4,
        "silhouette_average": alt_linkages["silhouette_average"],
        "silhouette_complete": alt_linkages["silhouette_complete"],
        "silhouette_k3": sil_k3,
        "silhouette_alt_distance": alt_dist["silhouette_alt_distance"],
        "mds_coords": coords,
    }
```
