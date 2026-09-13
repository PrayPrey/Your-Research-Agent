# Phase 3 Architecture: H-E2 Correlation Analysis

**Type**: EXISTENCE | **Applied**: single-script pandas/scipy analysis pipeline (no KB match found; standard pattern used)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze (h-e2/code/ does not exist yet)
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. H-E1 output consumed only as a data file (`h-e1/h-e1/results/results.csv`), not as code dependency.

---

## 1. Components

- **DataLoader**: reads CV_PR csv (local) + timm accuracy csv (remote GitHub raw URL, with local cache)
- **Merger**: normalizes model names, joins two dataframes, reports match rate
- **Correlator**: Pearson + Spearman correlation, bootstrap CI, outlier detection
- **Visualizer**: scatter plot with regression line + annotated stats

## 2. Data Flow

1. `DataLoader.load_cvpr()` -> DataFrame[model, model_cv_pr, time_sec, n_layers]
2. `DataLoader.load_accuracy()` -> DataFrame[model, top1, top5, param_count, ...] (downloaded + cached)
3. `Merger.merge(cvpr_df, acc_df)` -> merged DataFrame + match_rate report
4. `Correlator.analyze(merged)` -> dict{r_pearson, p_pearson, r_spearman, p_spearman, ci_low, ci_high, n, outliers}
5. `Visualizer.plot(merged, stats)` -> saves PNG
6. `main()` -> writes `correlation_results.json`, prints PASS/FAIL verdict

## 3. File Structure

```
h-e2/
  code/
    correlate.py      # DataLoader, Merger, Correlator, Visualizer, main()
  results/
    correlation_results.json
    accuracy_cache.csv   # cached download of results-imagenet.csv
  figures/
    scatter_cv_pr_vs_accuracy.png
  04_validation.md
```

Single-file module (EXISTENCE scope) — all four components are classes/functions in `correlate.py`.

## 4. Module Interfaces (`h-e2/code/correlate.py`)

```python
CVPR_PATH = "h-e1/h-e1/results/results.csv"
ACCURACY_URL = "https://raw.githubusercontent.com/huggingface/pytorch-image-models/main/results/results-imagenet.csv"
CACHE_PATH = "h-e2/results/accuracy_cache.csv"
THRESHOLD_R = -0.3
THRESHOLD_P = 0.05

class DataLoader:
    @staticmethod
    def load_cvpr(path: str = CVPR_PATH) -> pd.DataFrame: ...
    @staticmethod
    def load_accuracy(url: str = ACCURACY_URL, cache_path: str = CACHE_PATH) -> pd.DataFrame: ...

class Merger:
    @staticmethod
    def normalize_name(name: str) -> str: ...  # strip .in1k etc, lowercase
    @staticmethod
    def merge(cvpr_df: pd.DataFrame, acc_df: pd.DataFrame) -> tuple[pd.DataFrame, float]: ...  # (merged, match_rate)

class Correlator:
    @staticmethod
    def analyze(merged: pd.DataFrame, n_bootstrap: int = 2000) -> dict: ...
    @staticmethod
    def bootstrap_ci(x: np.ndarray, y: np.ndarray, n_bootstrap: int = 2000) -> tuple[float, float]: ...
    @staticmethod
    def find_outliers(merged: pd.DataFrame, stats: dict, z_thresh: float = 2.0) -> pd.DataFrame: ...

class Visualizer:
    @staticmethod
    def plot(merged: pd.DataFrame, stats: dict, out_path: str) -> None: ...

def main() -> dict: ...  # orchestrates pipeline, writes JSON, prints verdict
```

**Dependencies**: Merger depends on DataLoader outputs; Correlator depends on Merger output; Visualizer depends on Merger + Correlator outputs; `main()` orchestrates all.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | DataLoader | Load CV_PR CSV + download/cache timm accuracy CSV | 6 | 2+1+2+1 |
| A-2 | Merger | Name normalization + join + match-rate report | 6 | 2+1+2+1 |
| A-3 | Correlator core | Pearson/Spearman r, p + JSON output | 5 | 2+1+1+1 |
| A-4 | Correlator robustness | Bootstrap CI + outlier detection | 6 | 2+1+2+1 |
| A-5 | Visualizer | Scatter + regression line + annotations | 4 | 2+1+1+0 |
| A-6 | Integration run | `main()` orchestration, verdict, end-to-end test | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6]
