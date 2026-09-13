# Logic: H-M5 (Modality Divergence — Phase Transition Effect)

**Type:** MECHANISM (statistical pipeline, no ML training)

## Codebase Analysis (Serena)

**Project Type:** Green-field: no existing codebase.
**Status:** N/A — new API design from architecture spec.
**Analyzed Path:** N/A
**Relevant Symbols:** None — new implementation.

---

## A-1: Data Loading [Complexity: 8, Budget: 8]

**Applied**: Standard HuggingFace `datasets.load_dataset` pattern.

### API Signatures

```python
# data_loader.py
from datasets import Dataset
import pandas as pd

def load_pwc_dataset(cache_dir: str = ".cache/pwc") -> Dataset:
    """Load pwc-archive/datasets train split, local cache fallback on timeout."""
    ...

def extract_modality(task: str) -> str:
    """Keyword match task string -> CV|NLP|Audio|Tabular|Other."""
    ...

def build_monthly_counts(raw_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate benchmark usage counts by month x modality.
    Returns columns: month (Period[M]), modality (str), benchmark (str), count (int)
    """
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | HF load + cache | `load_dataset(...)`, save parquet to cache_dir |
| L-1-2 | Field normalization | Extract task/date fields into flat DataFrame |
| L-1-3 | Timeout fallback | try/except -> load cached parquet if HF call fails |
| L-1-4 | Date range filter | Clip to 2018-01..2024-12 |

---

## A-2: Modality Classification [Complexity: 5, Budget: 5]

**Applied**: Simple keyword-lookup classifier (no ML needed — YAGNI).

### API Signatures

```python
# config.py
MODALITY_KEYWORDS: dict[str, list[str]] = {
    "CV": ["image", "vision", "object detection", "segmentation"],
    "NLP": ["text", "language", "nlp", "translation", "summarization"],
    "Audio": ["audio", "speech", "sound"],
    "Tabular": ["tabular", "structured"],
}
```

```python
# data_loader.py
def extract_modality(task: str) -> str:
    """Lowercase substring match against config.MODALITY_KEYWORDS; 'Other' if no match."""
    ...
```

### Subtasks [3/4 used — under budget]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Keyword dict | Define config.MODALITY_KEYWORDS |
| L-2-2 | Classifier fn | Case-insensitive substring match, first-match wins |
| L-2-3 | Vectorized apply | `raw_df["modality"] = raw_df["task"].map(extract_modality)` |

---

## A-3: Monthly Aggregation [Complexity: 6, Budget: 6]

**Applied**: Standard pandas groupby pattern.

### API Signatures

```python
# data_loader.py
def build_monthly_counts(raw_df: pd.DataFrame) -> pd.DataFrame:
    """groupby(month, modality, benchmark).size() -> long-format counts table."""
    ...
```

### Pseudo-code

```
1. raw_df["month"] = raw_df["date"].dt.to_period("M")
2. counts = raw_df.groupby(["month","modality","benchmark"]).size().reset_index(name="count")
3. return counts
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Month period col | `.dt.to_period("M")` |
| L-3-2 | Groupby+count | groupby month/modality/benchmark, size() |
| L-3-3 | Missing month fill | reindex to full month range, count=0 |
| L-3-4 | Validation | assert months span >= 2018-01..2024-12 |

---

## A-4: Gini Computation [Complexity: 6, Budget: 6]

**Applied**: Standard vectorized Gini formula (numpy sort + cumulative weighted sum).

### API Signatures

```python
# gini.py
import numpy as np

def compute_gini(counts: np.ndarray) -> float:
    """Gini coefficient of a 1D count array. NaN if empty, 0.0 if single element."""
    ...
```

### Pseudo-code

```
1. if len(counts) == 0: return nan
2. if len(counts) == 1: return 0.0
3. sorted_counts = np.sort(counts)          # [n]
4. n = len(sorted_counts)
5. cum = np.cumsum(sorted_counts)
6. gini = (2 * np.sum((np.arange(1, n+1)) * sorted_counts)) / (n * cum[-1]) - (n+1)/n
7. return gini
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Formula impl | Vectorized numpy formula |
| L-4-2 | Empty edge case | len==0 -> NaN |
| L-4-3 | Single edge case | len==1 -> 0.0 |
| L-4-4 | Zero-sum guard | sum(counts)==0 -> NaN |

---

## A-5: Gini Time Series [Complexity: 5, Budget: 5]

**Applied**: pandas pivot + groupby-apply.

### API Signatures

```python
# gini.py
import pandas as pd

def compute_modality_gini_series(monthly_df: pd.DataFrame) -> pd.DataFrame:
    """monthly_df: month,modality,benchmark,count -> DatetimeIndex, cols=[CV,NLP,Audio,Tabular]."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| gini_df | [T>=72, 4] | DatetimeIndex monthly, 4 modality columns |

### Pseudo-code

```
1. for each (month, modality) group: gini = compute_gini(group["count"].values)
2. pivot to wide DataFrame: index=month (-> Timestamp), columns=modality
3. reindex columns to [CV, NLP, Audio, Tabular]
4. assert len(gini_df) >= 72
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | Groupby apply | month,modality -> compute_gini |
| L-5-2 | Pivot wide | index=month, columns=modality |
| L-5-3 | Column order | reindex to CV/NLP/Audio/Tabular |
| L-5-4 | Min-length check | assert >=72 rows |

---

## A-6: Period + Rolling Correlation [Complexity: 6, Budget: 6]

**Applied**: scipy.stats.pearsonr + pandas .rolling().corr().

### API Signatures

```python
# correlation.py
import pandas as pd
from scipy import stats

def period_correlation(
    gini_df: pd.DataFrame, col_a: str, col_b: str,
    start: str | None = None, end: str | None = None,
) -> tuple[float, int]:
    """Pearson r between col_a,col_b in [start,end). Returns (r, n_obs), NaN-dropped."""
    ...

def rolling_correlation(
    gini_df: pd.DataFrame, col_a: str, col_b: str, window: int = 6,
) -> pd.Series:
    """6-month rolling Pearson correlation. Returns Series indexed like gini_df."""
    ...
```

### Pseudo-code

```
period_correlation:
1. sub = gini_df.loc[start:end, [col_a, col_b]].dropna()
2. r, _ = stats.pearsonr(sub[col_a], sub[col_b])
3. return r, len(sub)

rolling_correlation:
1. return gini_df[col_a].rolling(window).corr(gini_df[col_b])
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | Period slice | pre: [:2020-01), post: [2021-01:] |
| L-6-2 | pearsonr call | dropna paired, scipy.stats.pearsonr |
| L-6-3 | Rolling corr | pandas .rolling(window).corr() |
| L-6-4 | n_obs return | len(sub) for downstream Fisher test |

---

## A-7: Fisher Z-Test [Complexity: 5, Budget: 5]

**Applied**: Standard Fisher z-transform two-sample test.

### API Signatures

```python
# correlation.py
import numpy as np
from scipy import stats

def fisher_z_test(r1: float, n1: int, r2: float, n2: int) -> tuple[float, float]:
    """Fisher z-test comparing two correlations. Returns (z_stat, p_value)."""
    ...
```

### Pseudo-code

```
1. z1, z2 = np.arctanh(r1), np.arctanh(r2)
2. se = np.sqrt(1/(n1-3) + 1/(n2-3))
3. z_stat = (z1 - z2) / se
4. p_value = 2 * (1 - stats.norm.cdf(abs(z_stat)))
5. return z_stat, p_value
```

### Subtasks [3/4 used — under budget]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | z-transform | np.arctanh(r1), np.arctanh(r2) |
| L-7-2 | z-stat | (z1-z2)/sqrt(1/(n1-3)+1/(n2-3)) |
| L-7-3 | p-value | two-tailed via stats.norm.cdf |

---

## A-8: Baseline Model [Complexity: 3, Budget: 3]

**Applied**: Reuse gini.compute_gini on combined counts (no new formula).

### API Signatures

```python
# baseline.py
import pandas as pd

def compute_overall_gini_series(monthly_df: pd.DataFrame) -> pd.Series:
    """All-modality-combined monthly Gini, DatetimeIndex Series."""
    ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | Combine counts | groupby month only (ignore modality) |
| L-8-2 | Apply gini | compute_gini per month |
| L-8-3 | Return Series | DatetimeIndex, name="overall_gini" |

---

## A-9: Gate Evaluation + Failure Pivot [Complexity: 6, Budget: 6]

**Applied**: Simple threshold dict pattern.

### API Signatures

```python
# gate.py
import pandas as pd

def evaluate_gate(
    r_pre: float, r_post: float, p_value: float, n_pre: int, n_post: int,
) -> dict:
    """gate_pass = (r_pre>0.6) and (r_post<0.4) and (p_value<0.05).
    Returns {gate_pass, r_pre, r_post, p_value, n_pre, n_post}."""
    ...

def failure_pivot(gini_df: pd.DataFrame) -> pd.DataFrame:
    """If gate fails: pairwise pre/post correlations for CV-Audio, NLP-Audio,
    CV-Tabular, NLP-Tabular. Returns DataFrame [pair, r_pre, r_post]."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | Threshold checks | r_pre>0.6, r_post<0.4, p<0.05 |
| L-9-2 | Result dict | assemble gate_pass + inputs |
| L-9-3 | Pair loop | 4 modality pairs, call period_correlation twice each |
| L-9-4 | Pivot table | assemble DataFrame [pair, r_pre, r_post] |

---

## A-10: Visualization Suite [Complexity: 8, Budget: 8]

**Applied**: Standard matplotlib bar/line/heatmap patterns.

### API Signatures

```python
# visualize.py
import pandas as pd
import matplotlib.pyplot as plt

def plot_gate_metrics(result: dict, out_path: str) -> None:
    """Bar chart r_pre vs r_post; hlines at 0.6, 0.4; pass/fail annotation."""
    ...

def plot_rolling_correlation(rolling: pd.Series, out_path: str) -> None:
    """Line plot; vlines at 2020-01, 2021-01."""
    ...

def plot_gini_trajectories(gini_df: pd.DataFrame, out_path: str) -> None:
    """Multi-line plot, one line per modality column."""
    ...

def plot_correlation_heatmap(
    pre_matrix: pd.DataFrame, post_matrix: pd.DataFrame, out_path: str,
) -> None:
    """Two-panel heatmap (pre vs post) via imshow, side-by-side subplots."""
    ...
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-10-1 | Gate bar chart | bar r_pre/r_post + threshold hlines |
| L-10-2 | Gate annotation | pass/fail text label |
| L-10-3 | Rolling line plot | plot Series + vlines |
| L-10-4 | Trajectories plot | 4-line plot, legend by modality |
| L-10-5 | Heatmap pre panel | imshow(pre_matrix), colorbar |
| L-10-6 | Heatmap post panel | imshow(post_matrix), shared colorbar |
| L-10-7 | Save all PNGs | savefig to figures/ dir |
| L-10-8 | Style consistency | shared figsize/dpi across all 4 |

---

## A-11: End-to-End Orchestration [Complexity: 7, Budget: 7]

**Applied**: Sequential pipeline orchestrator (no framework needed).

### API Signatures

```python
# run_experiment.py
def main() -> dict:
    """Runs full pipeline steps 1-8 per architecture Data Flow.
    Returns dict of all metrics for 04_validation.md generation."""
    ...
```

### Pseudo-code

```
1. raw = data_loader.load_pwc_dataset()
2. raw_df = ... ; raw_df["modality"] = raw_df["task"].map(extract_modality)
3. monthly_df = data_loader.build_monthly_counts(raw_df)
4. gini_df = gini.compute_modality_gini_series(monthly_df)
5. overall = baseline.compute_overall_gini_series(monthly_df)
6. r_pre, n_pre = correlation.period_correlation(gini_df,"CV","NLP",end="2020-01")
7. r_post, n_post = correlation.period_correlation(gini_df,"CV","NLP",start="2021-01")
8. rolling = correlation.rolling_correlation(gini_df,"CV","NLP")
9. z_stat, p_value = correlation.fisher_z_test(r_pre,n_pre,r_post,n_post)
10. result = gate.evaluate_gate(r_pre,r_post,p_value,n_pre,n_post)
11. if not result["gate_pass"]: pivot = gate.failure_pivot(gini_df)
12. visualize.plot_gate_metrics(result, "figures/gate_metrics.png")
13. visualize.plot_rolling_correlation(rolling, "figures/rolling_correlation.png")
14. visualize.plot_gini_trajectories(gini_df, "figures/gini_trajectories.png")
15. visualize.plot_correlation_heatmap(pre_matrix, post_matrix, "figures/correlation_heatmap.png")
16. return {**result, "rolling": rolling, "gini_df": gini_df, ...}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-11-1 | Wire pipeline | call modules in Data Flow order |
| L-11-2 | Metric assembly | collect all outputs into result dict |
| L-11-3 | Figure generation | call all 4 visualize.* functions |
| L-11-4 | Report inputs | write metrics dict for 04_validation.md |
