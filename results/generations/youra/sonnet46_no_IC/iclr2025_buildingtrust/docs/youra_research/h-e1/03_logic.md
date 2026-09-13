# Logic: H-E1
## Partial Spearman Correlation Structure in LLM Trustworthiness Dimensions

**Hypothesis Type:** EXISTENCE (PoC)
**Date:** 2026-08-04
**Budget:** 6 subtasks (E-3: 3, E-5: 3)

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** green-field — no existing code to analyze
**Analyzed Path:** N/A
**Relevant Symbols:** None — new implementation

---

## Applied Patterns

Applied: Standard scipy/sklearn OLS residualization pattern (KB domain mismatch — diffusion model content only; no statistical analysis patterns found)
Applied: scipy.stats.spearmanr + LinearRegression residualization (stdlib pattern)

---

## E-3: Partial Spearman [Complexity: 12, Budget: 3]

### API Signatures

```python
# analysis.py

from sklearn.linear_model import LinearRegression
from scipy.stats import spearmanr, t as t_dist
import numpy as np
import pandas as pd


def ols_residualize(
    scores_df: pd.DataFrame,       # [16, 6] model scores
    covariates_df: pd.DataFrame    # [16, 2] log10_params, is_RLHF
) -> pd.DataFrame:
    """OLS-residualize each dimension on covariates. Returns [16, 6] residuals."""
    ...


def _partial_spearman_tstat(
    rho: float,
    n: int,
    k: int
) -> tuple[float, float]:
    """Compute t-stat and two-sided p-value for partial Spearman rho.
    df = n - 2 - k; floor guard 1e-10 on denominator."""
    ...


def partial_spearman_matrix(
    scores_df: pd.DataFrame,       # [16, 6]
    covariates_df: pd.DataFrame,   # [16, 2]
    alpha_bonferroni: float = 0.0033
) -> tuple[np.ndarray, np.ndarray, list[tuple]]:
    """Returns (rho_partial [6,6], pval [6,6], significant_pairs).
    significant_pairs: [(dim_i, dim_j, rho, pval), ...] where |rho|>0.5 AND p<alpha."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| scores_df | [16, 6] | raw scores per model per dimension |
| covariates_df | [16, 2] | log10_params, is_RLHF |
| residuals | [16, 6] | scores after OLS removal of covariates |
| rho_partial | [6, 6] | symmetric, diagonal=1.0 |
| pval | [6, 6] | symmetric, diagonal=0.0 |

---

## L-3-1: OLS Residualization [Subtask 1/3]

### Pseudo-code

```
def ols_residualize(scores_df, covariates_df):
    X = covariates_df.values          # [16, 2]
    residuals = {}
    for col in scores_df.columns:
        y = scores_df[col].values     # [16]
        reg = LinearRegression().fit(X, y)
        residuals[col] = y - reg.predict(X)   # [16]
    return pd.DataFrame(residuals, index=scores_df.index)
```

Note: LinearRegression includes intercept by default (`fit_intercept=True`). This is correct — residuals are mean-zero by construction.

---

## L-3-2: t-statistic for Partial Spearman [Subtask 2/3]

### Pseudo-code

```
def _partial_spearman_tstat(rho, n, k):
    df = n - 2 - k                         # 16 - 2 - 2 = 12
    denom = max(1 - rho**2, 1e-10)         # floor guard avoids div-by-zero at |rho|=1
    t = rho * np.sqrt(df / denom)
    pval = t_dist.sf(abs(t), df=df) * 2   # two-sided
    return t, pval
```

Numerical precision note: `1e-10` floor on `(1 - rho^2)` prevents overflow when rho=±1.0 exactly. With n=16, k=2, df=12 is fixed — no dynamic df computation needed.

---

## L-3-3: Bonferroni Filter [Subtask 3/3]

### Pseudo-code

```
def partial_spearman_matrix(scores_df, covariates_df, alpha_bonferroni=0.0033):
    residuals = ols_residualize(scores_df, covariates_df)
    dims = list(scores_df.columns)   # 6 dimension names
    n = len(dims)
    rho_mat = np.eye(n)
    pval_mat = np.zeros((n, n))
    significant_pairs = []

    for i in range(n):
        for j in range(i+1, n):
            rho, _ = spearmanr(residuals.iloc[:, i], residuals.iloc[:, j])
            _, pval = _partial_spearman_tstat(rho, n=16, k=2)
            rho_mat[i, j] = rho_mat[j, i] = rho
            pval_mat[i, j] = pval_mat[j, i] = pval
            if abs(rho) > 0.5 and pval < alpha_bonferroni:
                significant_pairs.append((dims[i], dims[j], rho, pval))

    return rho_mat, pval_mat, significant_pairs
```

Note: We recompute p-value via `_partial_spearman_tstat` (not from `spearmanr` directly) because `spearmanr` uses df=n-2, not df=n-2-k=12. This is the critical difference between raw and partial Spearman significance.

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | OLS Residualization | LinearRegression per dimension on [log10_params, is_RLHF]; return residual DataFrame |
| L-3-2 | t-stat + p-value | df=n-2-k=12, floor guard 1e-10, two-sided from scipy.stats.t.sf |
| L-3-3 | Bonferroni Filter | Iterate 15 pairs, flag |rho|>0.5 AND p<0.0033, return significant_pairs list |

---

## E-5: Visualization [Complexity: 10, Budget: 3]

### API Signatures

```python
# visualization.py

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy.cluster.hierarchy import dendrogram


def plot_partial_corr_bar(
    rho_partial: np.ndarray,   # [6, 6] symmetric
    pvals: np.ndarray,         # [6, 6] symmetric
    dim_names: list[str],      # length 6
    alpha: float,              # 0.0033
    out_path: str              # e.g. "h-e1/figures/bar_partial_corr.png"
) -> None:
    """Bar chart of |rho_partial| for all 15 pairs with Bonferroni line at 0.5."""
    ...


def plot_heatmap_comparison(
    rho_raw: np.ndarray,       # [6, 6]
    rho_partial: np.ndarray,   # [6, 6]
    dim_names: list[str],
    out_path: str
) -> None:
    """Side-by-side 6x6 heatmaps (raw vs partial), diverging colormap vmin=-1, vmax=1."""
    ...


def plot_dendrogram(
    linkage_matrix: np.ndarray,   # [5, 4] scipy linkage output
    dim_names: list[str],
    out_path: str
) -> None:
    """Dendrogram with color_threshold at 2-cluster cut."""
    ...


def plot_scatter_confound(
    scores_df: "pd.DataFrame",    # [16, 6] raw scores
    residuals_df: "pd.DataFrame", # [16, 6] residuals
    dim_pair: tuple[str, str],    # e.g. ("truthfulness", "safety")
    out_path: str
) -> None:
    """Before/after residualization scatter for top pair, colored by is_RLHF."""
    ...
```

---

## L-5-1: Bar Chart [Subtask 1/3]

### Pseudo-code

```
def plot_partial_corr_bar(rho_partial, pvals, dim_names, alpha, out_path):
    # Extract upper triangle (15 pairs)
    pairs, rhos, sigs = [], [], []
    for i in range(6):
        for j in range(i+1, 6):
            label = f"{dim_names[i][:4]}-{dim_names[j][:4]}"
            pairs.append(label)
            rhos.append(abs(rho_partial[i, j]))
            sigs.append(pvals[i, j] < alpha and abs(rho_partial[i, j]) > 0.5)

    # Sort by |rho| descending for readability
    order = np.argsort(rhos)[::-1]
    colors = ["#d62728" if sigs[k] else "#1f77b4" for k in order]

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(range(15), [rhos[k] for k in order], color=colors)
    ax.axhline(0.5, color="red", linestyle="--", label=f"Bonferroni threshold (α={alpha})")
    ax.set_xticks(range(15))
    ax.set_xticklabels([pairs[k] for k in order], rotation=45, ha="right")
    ax.set_ylabel("|ρ_partial|")
    ax.set_ylim(0, 1)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
```

---

## L-5-2: Side-by-Side Heatmap [Subtask 2/3]

### Pseudo-code

```
def plot_heatmap_comparison(rho_raw, rho_partial, dim_names, out_path):
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    kw = dict(vmin=-1, vmax=1, cmap="RdBu_r", annot=True, fmt=".2f",
              xticklabels=dim_names, yticklabels=dim_names, square=True)
    sns.heatmap(rho_raw, ax=axes[0], **kw)
    axes[0].set_title("Raw Spearman ρ")
    sns.heatmap(rho_partial, ax=axes[1], **kw)
    axes[1].set_title("Partial Spearman ρ (controlled)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
```

Note: `cmap="RdBu_r"` is standard diverging colormap centered at 0. `annot=True` with `fmt=".2f"` keeps annotations readable at 6×6 scale.

---

## L-5-3: Dendrogram + Scatter [Subtask 3/3]

### Pseudo-code

```
def plot_dendrogram(linkage_matrix, dim_names, out_path):
    fig, ax = plt.subplots(figsize=(8, 5))
    # color_threshold at midpoint of last merge for 2-cluster coloring
    color_thresh = 0.5 * (linkage_matrix[-1, 2] + linkage_matrix[-2, 2])
    dendrogram(linkage_matrix, labels=dim_names, color_threshold=color_thresh, ax=ax)
    ax.set_ylabel("Distance (1 - |ρ_partial|)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def plot_scatter_confound(scores_df, residuals_df, dim_pair, out_path):
    d0, d1 = dim_pair
    is_rlhf = scores_df["is_RLHF"].values   # [16] binary
    colors = ["#d62728" if r else "#1f77b4" for r in is_rlhf]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Before residualization
    axes[0].scatter(scores_df[d0], scores_df[d1], c=colors)
    axes[0].set_xlabel(d0); axes[0].set_ylabel(d1)
    axes[0].set_title("Raw scores")

    # After residualization
    axes[1].scatter(residuals_df[d0], residuals_df[d1], c=colors)
    axes[1].set_xlabel(f"{d0} residual"); axes[1].set_ylabel(f"{d1} residual")
    axes[1].set_title("After OLS residualization")

    # Legend
    from matplotlib.patches import Patch
    axes[1].legend(handles=[
        Patch(color="#d62728", label="RLHF"),
        Patch(color="#1f77b4", label="Base")
    ])
    fig.tight_layout()
    fig.savefig(out_path, dpi=300)
    plt.close(fig)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Bar Chart | |rho_partial| for 15 pairs sorted descending, red=significant, threshold line at 0.5 |
| L-5-2 | Dual Heatmap | Side-by-side 6×6 raw vs partial, RdBu_r diverging, annot=True |
| L-5-3 | Dendrogram + Scatter | scipy dendrogram 2-cluster coloring; before/after scatter colored by is_RLHF |

---

## Full Module Signatures Reference

For completeness — non-allocated modules (E-1, E-2, E-4, E-6) use signatures from 03_architecture.md verbatim.

### Numerical Precision Notes

| Location | Guard | Reason |
|----------|-------|--------|
| `_partial_spearman_tstat` | `max(1 - rho**2, 1e-10)` | Prevents div-by-zero at rho=±1.0 |
| `build_distance_matrix` | diagonal explicitly set to 0 | Avoids floating-point `1 - 1.0 != 0` edge case |
| `spearmanr` | use `spearmanr(a, b)` not matrix form | Matrix form returns scalar for 2-column input in older scipy |

### Fixed Constants (not parameterized)

```python
N_MODELS = 16        # fixed by TrustLLM dataset
N_DIMS = 6           # fixed by TrustLLM dimensions
K_COVARIATES = 2     # log10_params, is_RLHF
DF = N_MODELS - 2 - K_COVARIATES  # = 12
N_PAIRS = 15         # C(6,2)
ALPHA_BONFERRONI = 0.05 / N_PAIRS  # = 0.0033...
RHO_THRESHOLD = 0.5  # gate condition
```
