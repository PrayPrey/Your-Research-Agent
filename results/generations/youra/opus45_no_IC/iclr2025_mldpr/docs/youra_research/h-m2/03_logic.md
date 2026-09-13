# Logic: H-M2 (MECHANISM Validation)

**Hypothesis:** Prior-year HHI predicts current-year standard-benchmark adoption

Applied: standard statsmodels Logit pattern (KB search "logistic regression API statsmodels" returned only unrelated diffusion-model repos — no relevant results; using standard statsmodels.api.Logit API from public docs).

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1) — code absent
**Status**: `h-m1/code/` confirmed absent via glob (no files). `h-e1/code/` and `h-e1/data/` also absent. No implementation exists to verify signatures against — spec fallback used (per architecture doc's prior analysis). Serena symbol search skipped since there is no code to query.
**Analyzed Path**: N/A (no code)
**Relevant Symbols**: None — H-M2 reimplements a minimal PWC loader and HHI table load/recompute locally per `h-m1/03_architecture.md` spec.

Subtask budget: 10 (per allocation; architecture shows all tasks Low complexity 3-7, breakdowns already listed).

---

## Module: data_loader.py

```python
VENUES = ("NeurIPS", "ICML", "ICLR")
YEARS = range(2018, 2025)
CACHE_PATH = "h-m2/data/pwc_papers_labeled.parquet"

def load_papers() -> pd.DataFrame:
    """Load PWC papers-with-abstracts.json; filter to VENUES/YEARS.
    Returns DataFrame[paper_id, venue, year, datasets_used(list[str])]."""
    ...

def load_hhi_table() -> pd.DataFrame:
    """Load H-E1 HHI values from h-e1/04_validation.md table; if absent,
    recompute via compute_hhi(task_counts) per h-m1/03_architecture.md formula.
    Returns DataFrame[venue, year, hhi_score]."""
    ...

def compute_hhi(task_counts: pd.Series) -> float:
    """HHI = sum((count_i/total)^2). Reimplemented from h-m1 spec (no code to import)."""
    shares = task_counts / task_counts.sum()
    return float((shares ** 2).sum())
```

---

## Module: labeling.py

```python
def compute_standard_datasets(papers_df: pd.DataFrame, venue: str, year: int) -> set[str]:
    """Top-5 datasets by usage count for venue in year (year-1) papers."""
    ...

def label_papers(papers_df: pd.DataFrame, hhi_df: pd.DataFrame) -> pd.DataFrame:
    """Adds standard_benchmark(0/1) via compute_standard_datasets(prior year),
    merges prior_hhi from hhi_df (venue, year-1) -> (venue, year).
    Returns DataFrame[paper_id, venue, year, standard_benchmark(int), prior_hhi(float)]."""
    ...
```

### Pseudo-code: label_papers

```
1. hhi_df['year'] = hhi_df['year'] + 1   # shift so hhi_df now represents "prior_hhi for this year"
2. papers_df = papers_df.merge(hhi_df.rename(columns={'hhi_score': 'prior_hhi'}),
                                on=['venue', 'year'], how='inner')  # drops first year per venue (no prior)
3. for (venue, year), group in papers_df.groupby(['venue', 'year']):
     standard = compute_standard_datasets(papers_df, venue, year - 1)
     mask = group['datasets_used'].apply(lambda ds: bool(set(ds) & standard))
     papers_df.loc[group.index, 'standard_benchmark'] = mask.astype(int)
4. return papers_df[['paper_id', 'venue', 'year', 'standard_benchmark', 'prior_hhi']]
```

### Tensor / DataFrame shapes

| Variable | Shape/Type | Note |
|----------|-----------|------|
| papers_df | DataFrame, ~80k rows | one row per paper |
| labeled_df | DataFrame, ~65-75k rows | after dropping first-year-per-venue (no prior HHI) |
| standard | set[str] | top-5 dataset names |

---

## Module: analyze.py (entrypoint)

```python
import statsmodels.api as sm
import statsmodels.formula.api as smf

def fit_model(df: pd.DataFrame, add_controls: bool = False) -> "sm.discrete.discrete_model.BinaryResultsWrapper":
    """P(standard) ~ prior_hhi [+ C(venue)]. Uses smf.logit(formula, data=df).fit()."""
    formula = "standard_benchmark ~ prior_hhi"
    if add_controls:
        formula += " + C(venue)"
    return smf.logit(formula, data=df).fit(disp=0)

def fit_baseline(df: pd.DataFrame) -> "sm.discrete.discrete_model.BinaryResultsWrapper":
    """P(standard) ~ 1 (intercept only)."""
    return smf.logit("standard_benchmark ~ 1", data=df).fit(disp=0)

def extract_metrics(model_results, hhi_param: str = "prior_hhi") -> dict:
    """beta_hhi, p_value, odds_ratio, ci_lower, ci_upper, n_papers,
    n_venue_years, pseudo_r2, llr_p. See schema below."""
    ...

def hosmer_lemeshow(model_results, df: pd.DataFrame, groups: int = 10) -> tuple[float, float]:
    """Bin predicted probs into deciles, chi2 goodness-of-fit test.
    Returns (chi2_stat, p_value)."""
    ...

def gate_check(metrics: dict) -> bool:
    """beta_hhi > 0 AND p_value < 0.05."""
    return metrics["beta_hhi"] > 0 and metrics["p_value"] < 0.05

def verify_mechanism_activation(metrics: dict) -> tuple[bool, dict]:
    """Returns (passed, {coefficient_positive, statistically_significant,
    effect_meaningful}); effect_meaningful = abs(beta_hhi) > 0.1."""
    ...

def main() -> None:
    """1. load_papers() + load_hhi_table()
    2. label_papers()
    3. fit_model(baseline=intercept-only) 4. fit_model(df, add_controls=False) [proposed]
    5. fit_model(df, add_controls=True) [controlled]
    6. extract_metrics for proposed + controlled; hosmer_lemeshow(proposed)
    7. gate_check(proposed_metrics) + verify_mechanism_activation(proposed_metrics)
    8. visualize.generate_all(...) 9. save results dict -> results/results.json."""
    ...
```

### extract_metrics dict schema

| Key | Type | Note |
|-----|------|------|
| beta_hhi | float | `model_results.params[hhi_param]` |
| p_value | float | `model_results.pvalues[hhi_param]` |
| odds_ratio | float | `exp(beta_hhi)` |
| ci_lower, ci_upper | float | `exp(model_results.conf_int().loc[hhi_param])` |
| n_papers | int | `model_results.nobs` |
| n_venue_years | int | `df[['venue','year']].drop_duplicates().shape[0]` |
| pseudo_r2 | float | `model_results.prsquared` (McFadden) |
| llr_p | float | `model_results.llr_pvalue` |

### gate_check / verify_mechanism_activation logic

```
gate_check: beta_hhi > 0 and p_value < 0.05

verify_mechanism_activation:
  coefficient_positive = metrics['beta_hhi'] > 0
  statistically_significant = metrics['p_value'] < 0.05
  effect_meaningful = abs(metrics['beta_hhi']) > 0.1
  passed = coefficient_positive and statistically_significant
  return passed, {coefficient_positive, statistically_significant, effect_meaningful}
```

---

## Module: visualize.py

```python
def plot_gate_metrics(metrics: dict, out_path: str) -> None: ...
def plot_hhi_vs_adoption_scatter(labeled_df: pd.DataFrame, out_path: str) -> None: ...
def plot_predicted_probability_curve(model_results, out_path: str) -> None: ...
def plot_model_comparison_table(baseline_metrics: dict, controlled_metrics: dict, out_path: str) -> None: ...
def generate_all(metrics: dict, controlled_metrics: dict, labeled_df: pd.DataFrame,
                  model_results, out_dir: str = "h-m2/figures/") -> None:
    """Calls all 4 plot functions above, writes PNGs to out_dir."""
    ...
```

No tensors — pandas/statsmodels scalars and DataFrames only.

---

## External Dependencies (Base Hypothesis)

Neither H-M1 nor H-E1 has built `code/` (confirmed absent via glob). H-M2 reimplements `compute_hhi` and a minimal PWC loader locally per spec, rather than importing unbuilt modules.

| Module | Import Path | File Location |
|--------|-------------|----------------|
| HHI results (spec ref, reimplemented) | N/A | `h-e1/04_validation.md` (values) / `h-m1/03_architecture.md::data_loader.py::compute_hhi` |
| PWC papers loader (spec ref, reimplemented) | N/A | `h-m1/03_architecture.md::data_loader.py::load_papers` |

**Verified from**: `h-m1/code/`, `h-e1/code/`, `h-e1/data/` — all absent, confirmed via glob. Spec fallback used.

---

## Subtasks [used within Low-complexity guidance; matches architecture breakdown]

| ID | Task | Subtask | Description |
|----|------|---------|--------------|
| L-A1-1 | A-1 | Load PWC JSON | Parse papers-with-abstracts.json |
| L-A1-2 | A-1 | Filter venue/year | Restrict to VENUES/YEARS |
| L-A2-1 | A-2 | Load H-E1 HHI | Parse `04_validation.md` table or cache |
| L-A2-2 | A-2 | Recompute fallback | `compute_hhi` if H-E1 data absent |
| L-A3-1 | A-3 | Top-5 per venue-year | `compute_standard_datasets` |
| L-A4-1 | A-4 | Merge prior_hhi | Shift year, inner join |
| L-A4-2 | A-4 | Binary label | `standard_benchmark` via set intersection |
| L-A6-1 | A-6 | Fit proposed Logit | `smf.logit(formula).fit()` |
| L-A7-1 | A-7 | Hosmer-Lemeshow | Decile chi2 test |
| L-A9-1 | A-9 | 4 figures | `visualize.generate_all` |

10/10 subtasks used (matches budget cap; architecture breakdown sums confirm same total granularity).
