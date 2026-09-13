# Logic: h-m2 (Pareto-Optimal ECE Analysis)

**Type**: MECHANISM | **Gate**: SHOULD_WORK

**Applied**: statistical-hypothesis-test-pipeline (Welch t-test + Cohen's d + baseline controls)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1 data) + reused module (h-m1 ece.py)
**Status**: API signatures verified from actual code (Serena MCP unavailable in this env; Read tool used on h-e1/code/config.py, h-m1/code/config.py, h-m1/code/ece.py per architecture doc precedent)
**Analyzed Path**: `h-e1/code/config.py`, `h-m1/code/config.py`, `h-m1/code/ece.py`
**Relevant Symbols**: `compute_ece`, `generate_synthetic_ece`, `compute_all_ece` (h-m1/code/ece.py); `MODEL_PARAMS` dict (h-m1/code/config.py, NOT h-e1's `MODELS` list-of-dicts format)

## External Dependencies (Base Hypothesis)

```python
# From: h-m1/code/ece.py (ACTUAL CODE, copied verbatim into h-m2/code/ece.py)
def compute_ece(confidences: np.ndarray, predictions: np.ndarray, labels: np.ndarray, n_bins: int = 15) -> float: ...
def generate_synthetic_ece(model_id: str, seed: int = 42) -> float: ...
    # internally: `from config import MODEL_PARAMS`  <- requires local config.py in same dir
def compute_all_ece(models: list, seed: int = 42) -> dict: ...
    # returns {model_id: ece_float}

# From: h-m1/code/config.py (ACTUAL CODE) — MODEL_PARAMS format to copy
MODEL_PARAMS: dict[str, int]  # e.g. {"EleutherAI/pythia-70m": 70_000_000, ...} — 14 entries
```

**Verified from**: `h-m1/code/ece.py`, `h-m1/code/config.py` (actual implementation). `ece.py`'s `generate_synthetic_ece` does a same-directory `from config import MODEL_PARAMS` — h-m2 MUST provide local `config.py` with this exact dict name, copied from h-m1 (h-e1's config.py uses a different `MODELS` list-of-dicts format, not usable directly).

Also verified `h-e1/code/results/scores.csv` columns (via `pd.read_csv`): `model, family, params, log_params, truthfulqa_mc1, advglue_avg` (14 rows).

---

## A-1: config.py [Complexity: 5, Budget: 5]

**Applied**: Standard PyTorch/data-science config module (constants only)

### API Signatures

```python
# h-m2/code/config.py
from pathlib import Path

SEED: int = 42
N_BINS: int = 15
P_THRESHOLD: float = 0.05
D_THRESHOLD: float = 0.5  # Cohen's d medium effect

H_E1_SCORES: Path   # = Path(__file__).parent / "../../h-e1/code/results/scores.csv"
OUTPUT_PATH: Path   # = Path(__file__).parent / "results"
FIGURES_PATH: Path  # = Path(__file__).parent / "../figures"

MODEL_PARAMS: dict[str, int]  # copied verbatim from h-m1/code/config.py (14 entries)
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Paths | H_E1_SCORES, OUTPUT_PATH, FIGURES_PATH |
| L-1-2 | Constants | SEED, N_BINS |
| L-1-3 | Thresholds | P_THRESHOLD, D_THRESHOLD |
| L-1-4 | MODEL_PARAMS | Copy dict verbatim from h-m1/code/config.py |

---

## A-2: pareto.py [Complexity: 8, Budget: 8]

**Applied**: O(n²) Pareto dominance scan (standard, no KB pattern needed)

### API Signatures

```python
# h-m2/code/pareto.py
import pandas as pd

def identify_pareto_optimal(
    df: pd.DataFrame,
    x_col: str = "truthfulqa_mc1",
    y_col: str = "advglue_avg",
) -> list[str]:
    """Returns list of model ids not dominated on both x_col and y_col."""
    ...

def label_pareto(df: pd.DataFrame, pareto_models: list[str]) -> pd.DataFrame:
    """Returns df copy with added bool column 'is_pareto'."""
    ...
```

### Pseudo-code

```
identify_pareto_optimal(df, x_col, y_col):
  pareto = []
  for i, row_i in df.iterrows():
    dominated = False
    for j, row_j in df.iterrows():
      if i == j: continue
      if row_j[x_col] >= row_i[x_col] and row_j[y_col] >= row_i[y_col] \
         and (row_j[x_col] > row_i[x_col] or row_j[y_col] > row_i[y_col]):
        dominated = True; break
    if not dominated:
      pareto.append(row_i["model"])
  return pareto
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| df | [14, 6] | model, family, params, log_params, truthfulqa_mc1, advglue_avg |
| pareto_models | list[str] | expected len 4-6 |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Dominance check | Pairwise O(n²) comparison loop |
| L-2-2 | Frontier extraction | Collect non-dominated model ids |
| L-2-3 | label_pareto | Add is_pareto bool column via `.isin()` |
| L-2-4 | Edge case | If len(pareto) < 3, no special handling here (analysis.py reports it) |

---

## A-3: ece.py [Complexity: 4, Budget: 4]

**Applied**: Direct copy, no new pattern

### API Signatures

```python
# h-m2/code/ece.py — copied verbatim from h-m1/code/ece.py, unmodified
def compute_ece(confidences: np.ndarray, predictions: np.ndarray, labels: np.ndarray, n_bins: int = 15) -> float: ...
def generate_synthetic_ece(model_id: str, seed: int = 42) -> float: ...  # uses local `from config import MODEL_PARAMS`
def compute_all_ece(models: list, seed: int = 42) -> dict: ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Copy file | Byte-copy h-m1/code/ece.py to h-m2/code/ece.py |
| L-3-2 | Verify import | Confirm `from config import MODEL_PARAMS` resolves against h-m2/code/config.py |
| L-3-3 | Smoke test | Call `compute_all_ece(list(MODEL_PARAMS.keys()))`, check 14 floats in [0,1] |
| L-3-4 | No modification | Leave logic untouched (reuse, not reimplementation) |

---

## A-4: analysis.py — welch_ttest + cohens_d [Complexity: 7, Budget: 7]

**Applied**: scipy.stats.ttest_ind(equal_var=False) for Welch's t-test

### API Signatures

```python
# h-m2/code/analysis.py
import numpy as np
from scipy import stats

def welch_ttest(pareto_ece: np.ndarray, non_pareto_ece: np.ndarray) -> dict:
    """Returns {'t': float, 'p': float, 'mean_pareto': float, 'mean_non_pareto': float}."""
    ...

def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    """Pooled-std effect size between two 1D arrays."""
    ...
```

### Pseudo-code

```
welch_ttest(a, b):
  t, p = scipy.stats.ttest_ind(a, b, equal_var=False)
  return {t, p, mean(a), mean(b)}

cohens_d(a, b):
  pooled_std = sqrt(((len(a)-1)*var(a,ddof=1) + (len(b)-1)*var(b,ddof=1)) / (len(a)+len(b)-2))
  return (mean(a) - mean(b)) / pooled_std
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | welch_ttest | scipy.stats.ttest_ind(equal_var=False) wrapper |
| L-4-2 | cohens_d | Pooled std-dev effect size formula |
| L-4-3 | Return dict shape | Match architecture-specified keys exactly |
| L-4-4 | Edge case | N<2 per group -> return NaN, do not raise |

---

## A-5: analysis.py — baselines [Complexity: 9, Budget: 9]

**Applied**: Standard PyTorch/pandas group-split baseline pattern

### API Signatures

```python
def random_split_baseline(df: pd.DataFrame, seed: int = 42) -> dict:
    """Randomly split df in half (size matching Pareto/non-Pareto counts), run welch_ttest+cohens_d on ECE."""
    ...

def size_matched_baseline(df: pd.DataFrame) -> dict:
    """Split by median log_params instead of Pareto status; controls for model size confound."""
    ...
```

### Pseudo-code

```
random_split_baseline(df, seed):
  rng = np.random.default_rng(seed)
  shuffled = df.sample(frac=1, random_state=seed)
  n_pareto = count(df.is_pareto)  # match real group sizes
  group_a, group_b = shuffled[:n_pareto], shuffled[n_pareto:]
  ece_a, ece_b = compute_all_ece(group_a.model), compute_all_ece(group_b.model)
  return {**welch_ttest(ece_a, ece_b), 'cohens_d': cohens_d(ece_a, ece_b)}

size_matched_baseline(df):
  median_lp = df.log_params.median()
  small, large = df[df.log_params <= median_lp], df[df.log_params > median_lp]
  ece_s, ece_l = compute_all_ece(small.model), compute_all_ece(large.model)
  return {**welch_ttest(ece_s, ece_l), 'cohens_d': cohens_d(ece_s, ece_l)}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | random_split_baseline | Seeded shuffle, group-size matched to real Pareto/non-Pareto split |
| L-5-2 | size_matched_baseline | Median log_params split |
| L-5-3 | ECE reuse | Call ece.compute_all_ece per baseline group |
| L-5-4 | Result dict | Include t, p, means, cohens_d for both baselines |

---

## A-6: analysis.py — run_analysis orchestrator [Complexity: 8, Budget: 8]

**Applied**: gate-verdict aggregation pattern (from h-e1/h-m1 03_logic.md precedent)

### API Signatures

```python
def run_analysis(df: pd.DataFrame) -> dict:
    """
    Full pipeline: label pareto -> compute ECE per model -> welch_ttest -> cohens_d
    -> baselines -> gate_passed verdict.
    Returns dict with keys: pareto_models, n_pareto, n_non_pareto, ece_stats,
    ttest, cohens_d, random_baseline, size_matched_baseline, gate_passed.
    """
    ...
```

### Pseudo-code

```
run_analysis(df):
  pareto_models = identify_pareto_optimal(df)
  df = label_pareto(df, pareto_models)
  ece_map = compute_all_ece(df.model.tolist())
  df['ece'] = df.model.map(ece_map)
  pareto_ece = df[df.is_pareto].ece.values
  non_pareto_ece = df[~df.is_pareto].ece.values

  ttest = welch_ttest(pareto_ece, non_pareto_ece)
  d = cohens_d(pareto_ece, non_pareto_ece)
  rand_base = random_split_baseline(df)
  size_base = size_matched_baseline(df)

  gate_passed = (
    ttest['p'] < P_THRESHOLD
    and ttest['mean_pareto'] < ttest['mean_non_pareto']
    and len(pareto_ece) >= 3
    and len(non_pareto_ece) >= 5
    and d > D_THRESHOLD
  )
  return {pareto_models, len(pareto_ece), len(non_pareto_ece), ttest, d,
          rand_base, size_base, gate_passed}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | Group split | pareto vs non-pareto ECE arrays via is_pareto mask |
| L-6-2 | Stats aggregation | welch_ttest + cohens_d + both baselines |
| L-6-3 | Gate verdict | Boolean AND of 5 success criteria from PRD Sec.5 |
| L-6-4 | Return dict | Single flat dict, all PRD Sec.5 metrics present |

---

## A-7: visualize.py [Complexity: 7, Budget: 7]

**Applied**: matplotlib scatter + boxplot (reused from h-e1/h-m1 visualize.py pattern)

### API Signatures

```python
# h-m2/code/visualize.py
import pandas as pd
from pathlib import Path

def plot_pareto_frontier(df: pd.DataFrame, pareto_models: list[str], out_path: Path) -> None:
    """Scatter truthfulqa_mc1 (x) vs advglue_avg (y), pareto points highlighted."""
    ...

def plot_ece_comparison(df: pd.DataFrame, out_path: Path) -> None:
    """Boxplot of 'ece' column grouped by 'is_pareto'; df must have both columns."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | Scatter plot | truthfulqa_mc1 vs advglue_avg, color by is_pareto |
| L-7-2 | Frontier line | Sort pareto points, connect with step line |
| L-7-3 | Boxplot | ece by is_pareto group (2 boxes) |
| L-7-4 | Save both | savefig to FIGURES_PATH, dpi=150 |

---

## A-8: run.py [Complexity: 8, Budget: 8]

**Applied**: load -> compute -> analyze -> plot -> save JSON (standard-hypothesis-test-pipeline)

### API Signatures

```python
# h-m2/code/run.py
def main() -> dict:
    """Load scores.csv -> run_analysis -> plots -> save results.json. Returns run_analysis() dict."""
    ...

if __name__ == "__main__":
    main()
```

### Pseudo-code

```
main():
  df = pd.read_csv(H_E1_SCORES)
  results = run_analysis(df)
  df_labeled = label_pareto(df, results['pareto_models'])
  plot_pareto_frontier(df_labeled, results['pareto_models'], FIGURES_PATH / "pareto_frontier.png")
  df_labeled['ece'] = df_labeled.model.map(compute_all_ece(df_labeled.model.tolist()))
  plot_ece_comparison(df_labeled, FIGURES_PATH / "ece_comparison.png")
  json.dump(results, open(OUTPUT_PATH / "results.json", "w"), indent=2, default=float)
  return results
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | Load data | pd.read_csv(H_E1_SCORES) |
| L-8-2 | Run pipeline | Call run_analysis, then both plot functions |
| L-8-3 | Save JSON | OUTPUT_PATH/results.json, numpy types cast to float |
| L-8-4 | Ensure dirs | OUTPUT_PATH.mkdir, FIGURES_PATH.mkdir (parents=True, exist_ok=True) |

---

## A-9: Integration test [Complexity: 6, Budget: 6]

**Applied**: assert-based smoke test (no framework)

### API Signatures

```python
# h-m2/code/test_integration.py (or inline __main__ assert block)
def test_pipeline() -> None:
    """Run main(), assert N>=3/N>=5, runtime<30s, gate_passed is bool."""
    ...
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-9-1 | Timed run | time.time() wrap around main() |
| L-9-2 | Assert sample sizes | n_pareto>=3, n_non_pareto>=5 (relax note if frontier <3) |
| L-9-3 | Assert runtime | elapsed < 30 |
| L-9-4 | Assert outputs exist | results.json + 2 PNGs written to disk |
