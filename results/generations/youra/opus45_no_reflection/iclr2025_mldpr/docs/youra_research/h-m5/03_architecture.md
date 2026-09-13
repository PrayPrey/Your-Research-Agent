# Architecture: H-M5 (Modality Divergence — Phase Transition Effect)

**Type:** MECHANISM (statistical analysis, no ML training)
**Applied:** Standard pandas/scipy statistical pipeline pattern (no directly relevant KB entries found; using domain-standard rolling-correlation + Fisher z-test approach per experiment brief).

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** Green-field — no existing codebase to analyze
**Analyzed Path:** N/A
**Findings:** Fresh implementation from specification; no base hypothesis code to reuse.

---

## File Organization

```
h-m5/code/
  data_loader.py       # FR-1: load PWC, classify modality, aggregate monthly
  gini.py               # FR-2: Gini coefficient + time series construction
  correlation.py        # FR-3: period corr, rolling corr, Fisher z-test
  baseline.py            # FR-4: unified concentration null model
  gate.py                 # FR-5: gate evaluation + failure pivot
  visualize.py            # FR-6: 4 required figures
  run_experiment.py       # orchestrator: end-to-end pipeline
config.py                  # constants (date ranges, thresholds, keywords)
```

---

## Module Interfaces

### data_loader (`code/data_loader.py`)

**Dependencies**: datasets (HuggingFace), pandas

```python
def load_pwc_dataset() -> "datasets.Dataset": ...
def extract_modality(task: str) -> str: ...  # returns CV|NLP|Audio|Tabular|Other
def build_monthly_counts(raw_df: pd.DataFrame) -> pd.DataFrame: ...
    # columns: month (Period[M]), modality, benchmark, count
```

### gini (`code/gini.py`)

**Dependencies**: numpy, pandas

```python
def compute_gini(counts: np.ndarray) -> float: ...  # NaN if empty, 0 if single
def compute_modality_gini_series(monthly_df: pd.DataFrame) -> pd.DataFrame: ...
    # DatetimeIndex, columns: CV, NLP, Audio, Tabular
```

### correlation (`code/correlation.py`)

**Dependencies**: gini, numpy, scipy.stats

```python
def period_correlation(gini_df: pd.DataFrame, col_a: str, col_b: str,
                        start: str = None, end: str = None) -> tuple[float, int]: ...
    # returns (r, n)
def rolling_correlation(gini_df: pd.DataFrame, col_a: str, col_b: str,
                         window: int = 6) -> pd.Series: ...
def fisher_z_test(r1: float, n1: int, r2: float, n2: int) -> tuple[float, float]: ...
    # returns (z_stat, p_value)
def modality_pair_correlations(gini_df: pd.DataFrame, period: str) -> pd.DataFrame: ...
    # correlation matrix for failure-pivot (FR-5.2)
```

### baseline (`code/baseline.py`)

**Dependencies**: gini

```python
def compute_overall_gini_series(monthly_df: pd.DataFrame) -> pd.Series: ...
    # all modalities combined, reference for null hypothesis (FR-4.1)
```

### gate (`code/gate.py`)

**Dependencies**: correlation

```python
def evaluate_gate(r_pre: float, r_post: float, p_value: float,
                   n_pre: int, n_post: int) -> dict: ...
    # {gate_pass: bool, r_pre, r_post, p_value, n_pre, n_post}
def failure_pivot(gini_df: pd.DataFrame) -> pd.DataFrame: ...
    # domain-pair specific analysis if gate fails (FR-5.2)
```

### visualize (`code/visualize.py`)

**Dependencies**: matplotlib, correlation, gini

```python
def plot_gate_metrics(result: dict, out_path: str) -> None: ...        # FR-6.1 (required)
def plot_rolling_correlation(rolling: pd.Series, out_path: str) -> None: ...  # FR-6.2
def plot_gini_trajectories(gini_df: pd.DataFrame, out_path: str) -> None: ...  # FR-6.3
def plot_correlation_heatmap(pre_matrix: pd.DataFrame, post_matrix: pd.DataFrame,
                              out_path: str) -> None: ...  # FR-6.4
```

### run_experiment (`code/run_experiment.py`)

**Dependencies**: all modules above

```python
def main() -> dict: ...  # orchestrates full pipeline, writes 04_validation.md inputs
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data loading | Load PWC dataset via HF datasets, cache locally | 8 | 2+3+1+2 |
| A-2 | Modality classification | Keyword-based task→modality mapping | 5 | 2+1+1+1 |
| A-3 | Monthly aggregation | Groupby month/modality, build counts table | 6 | 2+2+1+1 |
| A-4 | Gini computation | Implement + vectorize Gini formula, edge cases | 6 | 2+1+2+1 |
| A-5 | Gini time series | Build DataFrame of monthly Gini per modality, validate ≥72 points | 5 | 2+2+1+0 |
| A-6 | Period + rolling correlation | Pearson r pre/post, 6-month rolling window | 6 | 2+2+1+1 |
| A-7 | Fisher z-test | Implement z-transform, z-stat, p-value | 5 | 1+2+2+0 |
| A-8 | Baseline model | Overall Gini series (unified null hypothesis) | 3 | 1+1+1+0 |
| A-9 | Gate evaluation + failure pivot | Gate logic, domain-pair correlation fallback | 6 | 2+2+1+1 |
| A-10 | Visualization suite | 4 figures (gate metrics, rolling corr, trajectories, heatmap) | 8 | 3+2+1+2 |
| A-11 | End-to-end orchestration | Wire pipeline, write validation report inputs | 7 | 2+3+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1,A-2,A-3,A-4,A-5,A-6,A-7,A-8,A-9,A-10,A-11]

---

## Data Flow

1. `data_loader.load_pwc_dataset()` → raw HF dataset
2. `data_loader.extract_modality()` + `build_monthly_counts()` → monthly counts table
3. `gini.compute_modality_gini_series()` → Gini DataFrame (CV, NLP, Audio, Tabular)
4. `baseline.compute_overall_gini_series()` → null-hypothesis reference series
5. `correlation.period_correlation()` (pre/post) + `rolling_correlation()` + `fisher_z_test()`
6. `gate.evaluate_gate()` → pass/fail; if fail, `gate.failure_pivot()`
7. `visualize.*` → 4 PNGs to `figures/`
8. `run_experiment.main()` → aggregates all results for `04_validation.md`
