# Logic Design: H-M1

**Hypothesis:** r(TruthfulQA, MMLU) < r(MMLU subtasks internal mean), with divergent profile models.
**Type:** MECHANISM (meta-analysis, no model training)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - designing new APIs (meta-analysis over published scores, no existing model code)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Data Loading [Complexity: 2, Budget: 2]

**Applied**: Standard pandas parquet/CSV ingestion

### API Signatures

```python
def load_scores(
    leaderboard_path: str,
    model_list: list[str],
) -> pd.DataFrame:
    """Load truthfulqa, mmlu, mmlu_* subject cols for N=50 models. Returns [N, 60] df."""
    ...

def validate_scores(df: pd.DataFrame, min_models: int = 30) -> pd.DataFrame:
    """Drop rows with missing truthfulqa/mmlu; assert len(df) >= min_models."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| raw_df | [M, K] | M >= 50 leaderboard rows, K = all columns |
| scores_df | [N, 59] | N <= 50 filtered models; cols = [model, truthfulqa, mmlu, mmlu_subject_1..57] |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | load_scores | Read parquet, select model + truthfulqa + mmlu + mmlu_* cols |
| L-1-2 | validate_scores | Dropna, assert min N, raise if mmlu_subjects < 2 |

---

## A-2: Correlation Analysis [Complexity: 4, Budget: 5]

**Applied**: scipy.stats.spearmanr pairwise correlation

### API Signatures

```python
def compute_tqa_mmlu_correlation(scores_df: pd.DataFrame) -> tuple[float, float]:
    """Spearman r(truthfulqa, mmlu). Returns (r, p)."""
    ...

def compute_mmlu_internal_correlation(scores_df: pd.DataFrame) -> tuple[float, np.ndarray]:
    """Pairwise Spearman r across all mmlu_* subject cols.
    Returns (mean_r, all_rs [P]) where P = C(57, 2) pairs (up to 1596)."""
    ...

def compute_r2_gap(r_tqa_mmlu: float, r_mmlu_internal_mean: float) -> float:
    """r_mmlu_internal_mean**2 - r_tqa_mmlu**2, variance-share difference."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| scores_df['truthfulqa'] | [N] | |
| scores_df['mmlu'] | [N] | |
| mmlu_subject_cols | [S] | S = number of mmlu_* cols found (<=57) |
| pairwise_rs | [C(S,2)] | flat array of all subject-pair correlations |

### Pseudo-code

```
FUNCTION compute_mmlu_internal_correlation(scores_df):
    subjects = [c for c in scores_df.columns if c.startswith('mmlu_')]
    assert len(subjects) >= 2, "need >=2 MMLU subjects for internal correlation"
    rs = []
    FOR i in range(len(subjects)):
        FOR j in range(i+1, len(subjects)):
            r, p = spearmanr(scores_df[subjects[i]], scores_df[subjects[j]])
            IF not isnan(r): rs.append(r)
    RETURN mean(rs), array(rs)
```

### Subtasks [3/5 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | compute_tqa_mmlu_correlation | Single spearmanr call |
| L-2-2 | compute_mmlu_internal_correlation | Nested loop over subject pairs, mean of valid r's |
| L-2-3 | compute_r2_gap | Scalar arithmetic for secondary metric |

---

## A-3: Divergent Profile Detection [Complexity: 3, Budget: 3]

**Applied**: Standard PyTorch/pandas z-score thresholding

### API Signatures

```python
def detect_divergent_models(
    scores_df: pd.DataFrame,
    mmlu_z_thresh: float = 1.0,
    tqa_z_thresh: float = 0.0,
) -> pd.DataFrame:
    """Flag models with mmlu_z > mmlu_z_thresh AND tqa_z < tqa_z_thresh.
    Returns subset df [D, 59+2] with added mmlu_z, tqa_z cols, D = divergent count."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| mmlu_z, tqa_z | [N] | per-model z-scores |
| divergent_mask | [N] bool | |
| divergent_df | [D, 61] | D = sum(divergent_mask), D >= 0 |

### Pseudo-code

```
FUNCTION detect_divergent_models(scores_df, mmlu_z_thresh=1.0, tqa_z_thresh=0.0):
    mmlu_z = (scores_df.mmlu - scores_df.mmlu.mean()) / scores_df.mmlu.std()
    tqa_z  = (scores_df.truthfulqa - scores_df.truthfulqa.mean()) / scores_df.truthfulqa.std()
    mask = (mmlu_z > mmlu_z_thresh) & (tqa_z < tqa_z_thresh)
    out = scores_df[mask].copy()
    out['mmlu_z'] = mmlu_z[mask]
    out['tqa_z'] = tqa_z[mask]
    RETURN out.sort_values('mmlu_z', ascending=False)
```

### Subtasks [1/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | detect_divergent_models | z-score compute + boolean mask + sorted subset |

---

## A-4: Gate Evaluation [Complexity: 1, Budget: 2]

### API Signatures

```python
def evaluate_gate(
    r_tqa_mmlu: float,
    r_mmlu_internal_mean: float,
    divergent_df: pd.DataFrame,
) -> dict:
    """Combine conditions 1 & 2 into gate_pass bool + full results dict."""
    ...
```

### Pseudo-code

```
FUNCTION evaluate_gate(r_tqa_mmlu, r_mmlu_internal_mean, divergent_df):
    cond1 = r_tqa_mmlu < r_mmlu_internal_mean
    cond2 = len(divergent_df) >= 1
    gate_pass = cond1 AND cond2
    RETURN {
        'r_truthfulqa_mmlu': r_tqa_mmlu,
        'r_mmlu_internal_mean': r_mmlu_internal_mean,
        'condition_1_pass': cond1,
        'condition_2_pass': cond2,
        'divergent_count': len(divergent_df),
        'divergent_models': divergent_df['model'].tolist(),
        'gate_pass': gate_pass,
    }
```

### Subtasks [1/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | evaluate_gate | Boolean AND of two conditions, assemble results dict |

---

## A-5: Visualization [Complexity: 3, Budget: 4]

**Applied**: matplotlib standard bar/scatter/heatmap/box

### API Signatures

```python
def plot_gate_comparison(r_tqa_mmlu: float, r_mmlu_internal_mean: float, out_path: str) -> None:
    """REQUIRED. Bar chart: 2 bars [r_tqa_mmlu, r_mmlu_internal_mean]."""
    ...

def plot_scatter_divergent(scores_df: pd.DataFrame, divergent_df: pd.DataFrame, out_path: str) -> None:
    """Scatter mmlu (x) vs truthfulqa (y), divergent points highlighted red."""
    ...

def plot_correlation_heatmap(scores_df: pd.DataFrame, out_path: str) -> None:
    """Heatmap of corr matrix over [truthfulqa, mmlu, mmlu_subject_1..S]. [S+2, S+2]."""
    ...

def plot_divergent_boxplot(scores_df: pd.DataFrame, divergent_df: pd.DataFrame, out_path: str) -> None:
    """Box plot of mmlu & truthfulqa distributions: divergent vs non-divergent groups."""
    ...
```

### Visualization Specifications

| Figure | File | Type | Required |
|--------|------|------|----------|
| Gate comparison | `figures/gate_comparison.png` | 2-bar chart, labels ["r(TQA,MMLU)", "r(MMLU internal)"], y-axis "Spearman r", annotate gate_pass in title | Yes (mandatory) |
| Scatter | `figures/scatter_divergent.png` | x=mmlu, y=truthfulqa, gray dots, divergent models red + labeled | No |
| Heatmap | `figures/correlation_heatmap.png` | seaborn/matplotlib imshow, corr matrix [S+2, S+2], colorbar -1..1 | No |
| Boxplot | `figures/divergent_boxplot.png` | 2 groups x 2 metrics (mmlu, truthfulqa), divergent vs rest | No |

### Subtasks [1/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | plot_gate_comparison | Only mandatory figure; others best-effort if time permits |

---

## Gate Pass Logic (Summary)

```
gate_pass = (r_truthfulqa_mmlu < r_mmlu_internal_mean) AND (divergent_count >= 1)
```

Both conditions computed independently in A-2/A-3, combined in A-4. Result dict written to `results/h_m1_results.json`.
