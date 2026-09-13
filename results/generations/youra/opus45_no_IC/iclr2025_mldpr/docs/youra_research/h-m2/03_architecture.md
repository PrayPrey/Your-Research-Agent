# Architecture: H-M2 (MECHANISM Validation)

**Hypothesis:** Convergence creates implicit evaluation standards (prior-year HHI predicts standard-benchmark adoption)

Applied: no domain-specific KB pattern found (searched "logistic regression coefficient CI significance testing" — only unrelated diffusion-model results returned); using standard statsmodels Logit pattern.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1) + external (H-E1)
**Status**: `h-m1/code/` does not exist yet (glob returned no files) — H-M1 spec-only, no implementation to import. `h-e1/data/` also absent (no cached parquet). Falling back to specs per fallback rule.
**Analyzed Path**: `h-m1/code/` (empty/absent), `h-e1/data/` (empty/absent)
**Findings**: H-M1 architecture spec defines `data_loader.py::load_papers() -> DataFrame[paper_id, venue, year, task_categories]` and `build_venue_year_table() -> DataFrame[venue, year, hhi, task_counts]`, plus `compute_hhi(task_counts) -> float`. No built code to import; H-M2 reimplements a minimal loader locally (PWC papers + datasets_used, plus HHI table) rather than depending on unbuilt modules.

---

## File Structure (Minimal — statistical analysis, not a training pipeline)

```
h-m2/code/
├── data_loader.py   # PWC papers load + filter, HHI table load/recompute
├── labeling.py      # standard-dataset identification, paper labeling
├── analyze.py       # entrypoint: fit models, gate check
└── visualize.py     # required + additional figures
```

Single entrypoint (`analyze.py`), no config.py (few constants, used once).

---

## Modules

### data_loader.py

**Dependencies**: pandas, (datasets HF, fallback only)

```python
VENUES = ("NeurIPS", "ICML", "ICLR")
YEARS = range(2018, 2025)

def load_papers() -> pd.DataFrame:
    """Load PWC papers-with-abstracts.json, filter to VENUES/YEARS.
    Returns DataFrame[paper_id, venue, year, datasets_used(list[str])]."""
    ...

def load_hhi_table() -> pd.DataFrame:
    """Load H-E1 HHI results (h-e1/04_validation.md derived table or
    h-e1/data cache); recompute via H-M1's compute_hhi if absent.
    Returns DataFrame[venue, year, hhi_score]."""
    ...
```

### labeling.py

**Dependencies**: pandas

```python
def compute_standard_datasets(papers_df: pd.DataFrame, venue: str, year: int) -> set[str]:
    """Top-5 datasets by usage count in venue's prior year."""
    ...

def label_papers(papers_df: pd.DataFrame, hhi_df: pd.DataFrame) -> pd.DataFrame:
    """For each paper: uses_standard label + prior_hhi merge.
    Returns DataFrame[paper_id, venue, year, standard_benchmark(int), prior_hhi(float)]."""
    ...
```

### analyze.py (entrypoint)

**Dependencies**: data_loader, labeling, statsmodels, visualize

```python
def fit_model(df: pd.DataFrame, add_controls: bool = False) -> "statsmodels.Logit results":
    """P(standard) ~ prior_hhi [+ venue dummies]."""
    ...

def extract_metrics(model_results) -> dict:
    """beta_hhi, p_value, odds_ratio, ci_lower, ci_upper, n_papers,
    n_venue_years, pseudo_r2, llr_p."""
    ...

def gate_check(metrics: dict) -> bool:
    """beta_hhi > 0 AND p_value < 0.05."""
    ...

def verify_mechanism_activation(metrics: dict) -> tuple[bool, dict]:
    """coefficient_positive, statistically_significant, effect_meaningful(|beta|>0.1)."""
    ...

def main() -> None:
    """1. load_papers() + load_hhi_table() 2. label_papers()
    3. fit_model(baseline) 4. fit_model(controlled)
    5. extract_metrics + gate_check + verify_mechanism_activation
    6. visualize.generate_all() 7. save results dict to results/."""
    ...
```

### visualize.py

**Dependencies**: matplotlib/seaborn, analyze (metrics dict + labeled df)

```python
def plot_gate_metrics(metrics: dict, out_path: str) -> None: ...
def plot_hhi_vs_adoption_scatter(labeled_df: pd.DataFrame, out_path: str) -> None: ...
def plot_predicted_probability_curve(model_results, out_path: str) -> None: ...
def plot_model_comparison_table(baseline_metrics: dict, controlled_metrics: dict, out_path: str) -> None: ...
def generate_all(metrics: dict, controlled_metrics: dict, labeled_df: pd.DataFrame, model_results, out_dir: str = "figures/") -> None: ...
```

---

## External Dependencies (Base Hypothesis)

**Note**: Neither H-M1 nor H-E1 has built `code/`; nothing importable exists at analysis time. H-M2 reimplements a minimal PWC loader and HHI table load/recompute locally per specs, rather than importing unbuilt modules.

| Module | Import Path | File Location |
|--------|-------------|----------------|
| HHI results (spec ref, reimplemented) | N/A | `h-e1/04_validation.md` (values) / `h-m1/03_architecture.md` → `data_loader.py::compute_hhi` |
| PWC papers loader (spec ref, reimplemented) | N/A | `h-m1/03_architecture.md` → `data_loader.py::load_papers` |

**Verified from**: `h-m1/code/`, `h-e1/data/`, `h-e1/code/` (all absent — confirmed via glob), spec fallback used.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | PWC data loading | Load papers-with-abstracts.json, filter venues/years, extract datasets_used | 5 | 2+1+1+1 |
| A-2 | HHI table integration | Load/recompute H-E1 HHI per venue-year, validate range [0,1] | 5 | 1+2+1+1 |
| A-3 | Standard dataset identification | Top-5 by usage in prior year per venue | 4 | 1+1+2+0 |
| A-4 | Paper labeling | Merge prior_hhi, binary standard_benchmark label | 5 | 2+2+1+0 |
| A-5 | Baseline model | Logit(standard ~ 1) | 3 | 1+0+1+1 |
| A-6 | Proposed model | Logit(standard ~ prior_hhi), extract β/p/OR/CI | 6 | 1+1+3+1 |
| A-7 | Controlled model + diagnostics | Add venue dummies, pseudo-R², LLR test, Hosmer-Lemeshow | 7 | 2+2+2+1 |
| A-8 | Gate + mechanism verification | gate_check, verify_mechanism_activation | 3 | 1+0+1+1 |
| A-9 | Visualization | 4 figures (gate metrics, scatter, prob curve, comparison table) | 7 | 3+1+1+2 |
| A-10 | Pipeline integration | Wire main(), save results.json, run end-to-end | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [A-1, A-2, A-3, A-4, A-5, A-6, A-7, A-8, A-9, A-10]

---

## Dependencies (external)

- pandas, numpy
- statsmodels (Logit, LLR test)
- scipy.stats
- matplotlib, seaborn
- datasets (HuggingFace, fallback only)
