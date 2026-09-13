# Logic: H-C1 Prospective Structural Validity Test

**Applied**: Standard PyTorch/sklearn — pearsonr + bootstrap resampling (scipy.stats, numpy)

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (H-E1 sibling module, no shared classes to call)
**Status**: H-E1 saved no pickled `PCA` object — only `outputs/h_e1_results.json` (loadings_pc1 dict) and `outputs/residualized_matrix.csv`. No `pca.transform()` available; frozen PC1 is reconstructed as a fixed loading vector and applied via dot product on standardized residuals. This is mathematically equivalent to `pca.transform()` since PCA fits on already-standardized/residualized input (see H-E1 `analysis.py::fit_pca`, no `StandardScaler` — PCA operates directly on `Y_resid`).
**Analyzed Path**: `docs/youra_research/h-e1/code/`, `docs/youra_research/h-e1/outputs/`
**Relevant Symbols**: `analysis.residualize`, `analysis.fit_pca` (H-E1, reference only — not called directly)

---

## A-1: Holdout Structural Validity Test [Complexity: Tier 1, Budget: standard]

### API Signatures

```python
import numpy as np
import pandas as pd
from scipy.stats import pearsonr

def load_frozen_pc1(results_path: str = "../h-e1/outputs/h_e1_results.json") -> tuple[np.ndarray, list[str]]:
    """Load frozen PC1 loading vector. Returns (loadings [6], benchmark_names)."""
    ...

def compute_pc1_scores(residualized: pd.DataFrame, loadings: np.ndarray, benchmark_names: list[str]) -> np.ndarray:
    """Project residualized H-E1 benchmarks onto frozen PC1. residualized: [N,6] -> pc1_scores: [N]"""
    ...

def match_models(pc1_df: pd.DataFrame, trustllm_df: pd.DataFrame, key: str = "model_name") -> pd.DataFrame:
    """Inner-join on normalized model name. Returns merged df with pc1_score + holdout cols."""
    ...

def compute_holdout_loading(pc1_scores: np.ndarray, benchmark_scores: np.ndarray) -> tuple[float, float]:
    """Pearson correlation of PC1 scores vs one holdout benchmark. Returns (loading, p_value)."""
    ...

def bootstrap_ci(pc1_scores: np.ndarray, benchmark_scores: np.ndarray, n_boot: int = 1000, seed: int = 42) -> tuple[float, float]:
    """Bootstrap 95% CI for the loading. Returns (ci_low, ci_high)."""
    ...

def evaluate_gate(loadings: dict[str, float], threshold: float = 0.3, min_pass: int = 2) -> str:
    """Returns 'PASS' if >= min_pass holdout benchmarks have loading >= threshold, else 'FAIL'."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| loadings (frozen PC1) | [6] | From H-E1 `loadings_pc1` dict, ordered per `benchmark_names` |
| residualized | [N, 6] | H-E1 `residualized_matrix.csv`, N ≈ 4561 |
| pc1_scores | [N] | `residualized @ loadings` |
| trustllm_df | [M, K] | M = TrustLLM models, K = holdout dimension count |
| merged | [N_overlap, 1+K] | pc1_score + K holdout scores after model-name join |

### Pseudo-code (main workflow)

```
1. loadings, bench_names = load_frozen_pc1("h-e1/outputs/h_e1_results.json")
2. Y_resid = pd.read_csv("h-e1/outputs/residualized_matrix.csv")  # includes model_name col
3. pc1_scores = compute_pc1_scores(Y_resid[bench_names], loadings, bench_names)
4. pc1_df = DataFrame({model_name: Y_resid.model_name, pc1_score: pc1_scores})

5. trustllm_df = fetch_trustllm_scores()  # holdout dims e.g. truthfulness, safety, fairness, robustness, privacy, ethics
6. merged = match_models(pc1_df, trustllm_df)
   assert len(merged) >= 100, "Min 100 overlapping models required (PRD)"

7. results = {}
8. for dim in holdout_dims:
     x = merged.pc1_score.values
     y = merged[dim].values
     y_std = (y - y.mean()) / y.std()          # standardize holdout benchmark
     loading, p_value = compute_holdout_loading(x, y_std)
     ci_low, ci_high = bootstrap_ci(x, y_std, n_boot=1000)
     results[dim] = {loading, p_value, ci_low, ci_high}

9. n_passing = count(dim in results where loading >= 0.3)
10. verdict = "PASS" if n_passing >= 2 else "FAIL"
11. write h_c1_results.json, loading_comparison.png
```

### compute_holdout_loading / bootstrap_ci detail

```python
def compute_holdout_loading(pc1_scores, benchmark_scores):
    r, p = pearsonr(pc1_scores, benchmark_scores)
    return float(r), float(p)

def bootstrap_ci(pc1_scores, benchmark_scores, n_boot=1000, seed=42):
    rng = np.random.default_rng(seed)
    n = len(pc1_scores)
    boot_r = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.choice(n, n, replace=True)
        boot_r[i], _ = pearsonr(pc1_scores[idx], benchmark_scores[idx])
    return float(np.percentile(boot_r, 2.5)), float(np.percentile(boot_r, 97.5))
```

### Decision Logic

```python
def evaluate_gate(loadings: dict[str, float], threshold: float = 0.3, min_pass: int = 2) -> str:
    n_passing = sum(1 for v in loadings.values() if v >= threshold)
    return "PASS" if n_passing >= min_pass else "FAIL"
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-C1-1 | Load frozen PC1 | Parse `h_e1_results.json` loadings_pc1, load `residualized_matrix.csv` |
| L-C1-2 | TrustLLM fetch + match | Fetch holdout scores, normalize model names, inner-join, assert N>=100 |
| L-C1-3 | Loading + bootstrap CI | Per-holdout pearsonr + 1000-resample bootstrap CI |
| L-C1-4 | Gate + report | Apply `evaluate_gate`, write JSON + bar chart figure |

---

## Data Loading Note

No `find_symbol` API-signature verification was required beyond what's shown above: H-C1 does not call any H-E1 class/function at runtime — it only reads H-E1's persisted CSV/JSON outputs as plain data files. `analysis.py::fit_pca` and `residualize` were inspected only to confirm PCA runs directly on `Y_resid` (no separate scaler), which justifies reconstructing PC1 scores via `Y_resid @ loadings` instead of needing a pickled `sklearn.decomposition.PCA` object.
