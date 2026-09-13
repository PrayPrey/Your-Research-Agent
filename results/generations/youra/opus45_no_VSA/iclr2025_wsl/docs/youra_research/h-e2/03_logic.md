# 03_logic.md — H-E2: CV_PR vs ImageNet Accuracy Correlation

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new API design (analysis script, no model code to reuse)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

Inputs are two CSV files (H-E1 output `results.csv` with columns
`model, model_cv_pr, time_sec, n_layers`, and timm `results-imagenet.csv` with
columns including `model, top1, top5`). No prior API to match.

---

## A-1: Merge + Correlation Analysis [Complexity: 2, Budget: 3]

**Applied**: Standard pandas/scipy (no KB pattern needed for tabular stats)

### API Signatures

```python
import pandas as pd
from scipy import stats
import numpy as np

def load_and_merge(
    cv_pr_path: str,
    imagenet_path: str,
    model_col: str = "model",
) -> pd.DataFrame:
    """Merge CV_PR scores with ImageNet top1 acc on model name. Returns df[model, model_cv_pr, top1]."""
    ...

def compute_correlations(
    df: pd.DataFrame,
    x_col: str = "model_cv_pr",
    y_col: str = "top1",
) -> dict:
    """Pearson + Spearman r, p-value. Returns {'pearson_r','pearson_p','spearman_r','spearman_p','n'}."""
    ...

def bootstrap_ci(
    x: np.ndarray,
    y: np.ndarray,
    method: str = "pearson",
    n_boot: int = 10000,
    ci: float = 0.95,
    seed: int = 42,
) -> tuple[float, float]:
    """Bootstrap CI for correlation coefficient. Returns (lo, hi)."""
    ...

def evaluate_success(corr: dict, ci: tuple[float, float]) -> bool:
    """Success: pearson_r < -0.3 and pearson_p < 0.05."""
    ...
```

### Merge Algorithm (pseudo-code)

Model name mismatches are the only non-trivial part (H-E1 uses timm
identifiers already, but suffixes/case may differ) — normalize before join.

```
1. df_cv = read_csv(cv_pr_path)          # [M, 4]
2. df_acc = read_csv(imagenet_path)      # [K, ...]
3. normalize(s) = s.strip().lower()
4. df_cv['key']  = df_cv['model'].map(normalize)
5. df_acc['key'] = df_acc['model'].map(normalize)
6. merged = df_cv.merge(df_acc[['key','top1']], on='key', how='inner')
7. assert len(merged) >= 30, "insufficient overlap for correlation test"
8. drop 'key' col; return merged[['model','model_cv_pr','top1']]
```

### Correlation Computation

```
pearson_r, pearson_p   = stats.pearsonr(merged.model_cv_pr, merged.top1)
spearman_r, spearman_p = stats.spearmanr(merged.model_cv_pr, merged.top1)
n = len(merged)
```

### Bootstrap CI Algorithm

```
1. rng = np.random.default_rng(seed)
2. boot_stats = empty[n_boot]
3. for i in range(n_boot):
4.     idx = rng.integers(0, n, size=n)          # resample with replacement
5.     xb, yb = x[idx], y[idx]
6.     if std(xb) == 0 or std(yb) == 0: boot_stats[i] = nan; continue
7.     boot_stats[i] = pearsonr(xb, yb)[0] if method=="pearson" else spearmanr(xb, yb)[0]
8. alpha = (1 - ci) / 2
9. lo, hi = nanpercentile(boot_stats, [100*alpha, 100*(1-alpha)])
10. return (lo, hi)
```

### Tensor / Array Shapes

| Variable | Shape | Note |
|----------|-------|------|
| merged | [N, 3] | N ≈ overlap count (rows) |
| x, y | [N] | model_cv_pr, top1 arrays |
| boot_stats | [n_boot] | resampled correlation coefficients |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-A1-1 | merge | Load both CSVs, normalize keys, inner join |
| L-A1-2 | correlate | Pearson + Spearman r/p via scipy.stats |
| L-A1-3 | bootstrap | 10k-resample CI for pearson_r, success gate check |
