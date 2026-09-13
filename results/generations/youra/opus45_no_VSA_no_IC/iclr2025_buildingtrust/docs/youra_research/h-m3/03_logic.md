# Logic: H-M3

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no code to analyze (H-M2's `code/` does not exist on disk; `h-m2/model_scores.csv` is consumed as a plain data file, not an import)
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## M3-1: Data Loading + Merge [Complexity: 6, Budget: 6]

**Applied**: Standard pandas CSV load/merge (no strong KB match; reused H-M2 file-based pattern)

### API Signatures

```python
def load_base_scores(csv_path: str) -> pd.DataFrame:
    """Load H-M2 model_scores.csv (model_id, truthfulqa_mc2, halueval_agg)."""
    ...

def load_factscore(csv_path: str) -> pd.DataFrame:
    """Load FactScore CSV (model_id, factscore). Falls back to synth/proxy if missing."""
    ...

def merge_scores(base_df: pd.DataFrame, factscore_df: pd.DataFrame) -> pd.DataFrame:
    """Inner join on model_id. Logs N models retained."""
    ...

def validate_columns(df: pd.DataFrame, required: list[str]) -> None:
    """Raises ValueError listing missing columns."""
    ...
```

### Tensor/DataFrame Shapes

| Variable | Shape | Note |
|----------|-------|------|
| base_df | [N=50, 3] | model_id, truthfulqa_mc2, halueval_agg |
| factscore_df | [N=50, 2] | model_id, factscore |
| merged | [N<=50, 4] | inner join; warn if N < 10 |

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-M3-1-1 | data.py | Implement load_base_scores, load_factscore, merge_scores, validate_columns per signatures above; save merged to h-m3/model_scores.csv |

---

## M3-2: Correlation Core [Complexity: 6, Budget: 6]

**Applied**: scipy.stats.spearmanr pairwise correlation (H-M2 pattern)

```python
def compute_factscore_correlations(
    model_scores: pd.DataFrame,
    factscore_col: str = "factscore",
    truthfulqa_col: str = "truthfulqa_mc2",
    halueval_col: str = "halueval_agg",
) -> dict[str, tuple[float, float]]:
    """Returns {'fs_tqa': (r, p), 'fs_he': (r, p), 'tqa_he': (r, p)}."""
    ...
```

Pseudo-code:
```
for each pair (col_a, col_b) in [(FS,TQA), (FS,HE), (TQA,HE)]:
    if n < 3: result[pair] = (0.0, 1.0); continue
    r, p = scipy.stats.spearmanr(model_scores[col_a], model_scores[col_b])
    result[pair] = (r, p)
return result
```

---

## M3-3: Bootstrap CI [Complexity: 5, Budget: 5]

```python
def bootstrap_ci(
    x: np.ndarray, y: np.ndarray,
    n_bootstrap: int = 1000, ci: float = 0.95, seed: int = 42,
) -> tuple[float, float]:
    """Returns (lower, upper) percentile CI of spearman r. Degenerate (0.0, 1.0) if n < 3."""
    ...
```

Pseudo-code:
```
if len(x) < 3: return (0.0, 1.0)
rng = np.random.default_rng(seed)
boot_rs = []
for i in range(n_bootstrap):
    idx = rng.integers(0, len(x), len(x))  # resample with replacement
    r, _ = spearmanr(x[idx], y[idx])
    boot_rs.append(r)
lo, hi = np.percentile(boot_rs, [(1-ci)/2*100, (1+ci)/2*100])
return (lo, hi)
```

---

## M3-4: Gate Check [Complexity: 5, Budget: 5]

```python
def check_gate(results: dict[str, tuple[float, float]], threshold: float = 0.7) -> dict:
    """Returns {'verdict': 'PASS'|'PARTIAL'|'FAIL', 'r_fs_tqa': float, 'r_fs_he': float}."""
    ...
```

Pseudo-code:
```
r_fs_tqa, _ = results['fs_tqa']
r_fs_he, _ = results['fs_he']
cond_a = abs(r_fs_tqa) < threshold
cond_b = abs(r_fs_he) < threshold
if cond_a and cond_b: verdict = "PASS"
elif cond_a or cond_b: verdict = "PARTIAL"
else: verdict = "FAIL"
return {"verdict": verdict, "r_fs_tqa": r_fs_tqa, "r_fs_he": r_fs_he}
```

---

## M3-5: PCA Analysis [Complexity: 7, Budget: 7]

**Applied**: sklearn StandardScaler + PCA (standard pattern)

```python
def run_pca_analysis(
    model_scores: pd.DataFrame,
    benchmark_cols: list[str] = ["factscore", "truthfulqa_mc2", "halueval_agg"],
) -> dict:
    """Returns {'loadings': [C,F] array, 'explained_variance': [C], 'n_components_80pct': int}."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| X | [N, F=3] | standardized (z-score) benchmark scores |
| loadings | [C, F] | C = min(3, len(benchmark_cols)) |
| explained_variance | [C] | ratio per component |

Pseudo-code:
```
X = StandardScaler().fit_transform(model_scores[benchmark_cols])
n_components = min(3, len(benchmark_cols))
pca = PCA(n_components=n_components).fit(X)
cum_var = np.cumsum(pca.explained_variance_ratio_)
n_components_80pct = int(np.searchsorted(cum_var, 0.80) + 1)
return {
    "loadings": pca.components_,                  # [C, F]
    "explained_variance": pca.explained_variance_ratio_,  # [C]
    "n_components_80pct": n_components_80pct,
}
```

---

## M3-6: Visualization [Complexity: 9, Budget: 9]

**Applied**: matplotlib/seaborn standard plotting (bar, heatmap, biplot, pairplot, cumsum line)

```python
def plot_gate_metrics(r_fs_tqa: float, r_fs_he: float, threshold: float, out_path: str) -> None: ...
def plot_correlation_heatmap(model_scores: pd.DataFrame, cols: list[str], out_path: str) -> None: ...
def plot_pca_biplot(model_scores: pd.DataFrame, pca_result: dict, cols: list[str], out_path: str) -> None: ...
def plot_scatter_matrix(model_scores: pd.DataFrame, cols: list[str], out_path: str) -> None: ...
def plot_cumulative_variance(pca_result: dict, out_path: str) -> None: ...
```

No non-obvious shapes; each writes one PNG to `h-m3/figures/`.

---

## M3-7: Mechanism Verification + Report [Complexity: 6, Budget: 6]

```python
def verify_mechanism_activation(results: dict) -> dict:
    """Per PRD FR-6.2: returns dict of mechanism checks (e.g. corr signs, n used)."""
    ...

def write_validation_report(results: dict, gate: dict, pca_result: dict, out_path: str) -> None:
    """Writes h-m3/04_validation.md with findings, gate verdict, PCA summary."""
    ...
```

---

## M3-8: Entry Point + Wiring [Complexity: 6, Budget: 6]

```python
def main() -> None:
    """Orchestrates: load -> merge -> correlate -> bootstrap -> gate -> pca -> visualize -> report."""
    ...
```

Pseudo-code:
```
base_df = load_base_scores("h-m2/model_scores.csv")
fs_df = load_factscore(<factscore_csv_path>)
validate_columns(base_df, ["model_id", "truthfulqa_mc2", "halueval_agg"])
validate_columns(fs_df, ["model_id", "factscore"])
merged = merge_scores(base_df, fs_df)
merged.to_csv("h-m3/model_scores.csv", index=False)

corr_results = compute_factscore_correlations(merged)
for pair, cols in [("fs_tqa", ("factscore","truthfulqa_mc2")),
                    ("fs_he", ("factscore","halueval_agg")),
                    ("tqa_he", ("truthfulqa_mc2","halueval_agg"))]:
    ci = bootstrap_ci(merged[cols[0]].values, merged[cols[1]].values)
    corr_results[pair] += (ci,)  # append CI to tuple/dict

gate = check_gate(corr_results)
pca_result = run_pca_analysis(merged)

plot_gate_metrics(...); plot_correlation_heatmap(...); plot_pca_biplot(...)
plot_scatter_matrix(...); plot_cumulative_variance(...)

mech = verify_mechanism_activation(corr_results)
write_validation_report(corr_results, gate, pca_result, "h-m3/04_validation.md")
```

Error handling: `try/except ValueError` around load/validate steps → log + `sys.exit(1)`.
