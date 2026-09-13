# Architecture: H-M2 — Tag Count Dose-Response (NB-2 Mechanism PoC)

**Applied**: N/A — Archon KB contains diffusion model domain content unrelated to NB-2 regression

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending H-E1 and H-M1)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`, `docs/youra_research/h-m1/code/`
**Findings**: H-E1 uses 4-script pipeline (01–04). All paths use `BASE_DIR = "docs/youra_research/h-e1"` prefix. H-E1 `derive_features()` already computes `tag_count` and `log_tag_count_p1`. H-M1 uses `PROJECT_ROOT = Path(__file__).resolve().parents[4]` for absolute path resolution. H-M2 must use the same `parents[4]` pattern for path safety.

---

## File Organization

```
docs/youra_research/h-m2/
├── code/
│   ├── 01_preprocess.py       # load H-E1 parquet, filter has_tags=1, derive IV, collinearity check
│   ├── 02_fit_models.py       # CT LR test, baseline NB-2, proposed NB-2, attenuation NB-2
│   ├── 03_generate_figures.py # 4 figures (gate bar, tag dist, partial regression, forest plot)
│   └── 04_evaluate_gate.py    # gate logic, primary_results.json
├── figures/
└── results/
    ├── model_results.json
    └── primary_results.json
```

---

## Module Definitions

### Preprocessor (`code/01_preprocess.py`)

**Dependencies**: pandas, numpy, scipy, pyarrow (H-E1 parquet)

```python
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[4]
H_E1_PARQUET = PROJECT_ROOT / "docs/youra_research/h-e1/results/preprocessed.parquet"
H_E1_CSV     = PROJECT_ROOT / "docs/youra_research/h-e1/code/data/h_e1/openml_dataset_corpus.csv"
OUT_PARQUET  = PROJECT_ROOT / "docs/youra_research/h-m2/results/tagged_subset.parquet"

EXPECTED_N_TAGGED = 2625  # ±100 acceptable

def load_h_e1_parquet() -> pd.DataFrame: ...
    # Primary: read_parquet(H_E1_PARQUET)
    # Fallback: read_csv(H_E1_CSV) + minimal feature derivation mirroring H-E1 derive_features()

def filter_tagged_subset(df: pd.DataFrame) -> pd.DataFrame: ...
    # df[df['has_tags'] == 1].copy()
    # Asserts len > 500

def derive_iv(df_tagged: pd.DataFrame) -> pd.DataFrame: ...
    # tag_count already in parquet from H-E1 derive_features()
    # log_tag_count_p1 = log(tag_count + 1) — also pre-derived in H-E1 parquet
    # Verify: tag_count >= 1 for all rows

def validate_subset(df_tagged: pd.DataFrame) -> None: ...
    # Check required columns: N_tasks, log_tag_count_p1, log_n_instances,
    #   log_n_features, age_years, age_sq, decade
    # Report tag_count.describe(), log_tag_count_p1.describe()
    # Assert no NaN in required columns

def check_collinearity(df_tagged: pd.DataFrame) -> dict: ...
    # Spearman rho(log_tag_count_p1, decade.astype(int))
    # Mean tag_count by decade
    # Returns {'rho': float, 'p_rho': float, 'decade_means': dict}

def main() -> None: ...
    # [1] load → [2] filter → [3] derive_iv → [4] validate → [5] collinearity → [6] save parquet
```

---

### ModelFitter (`code/02_fit_models.py`)

**Dependencies**: statsmodels, numpy, pandas, scipy, json

```python
from pathlib import Path

PROJECT_ROOT  = Path(__file__).resolve().parents[4]
TAGGED_PARQUET = PROJECT_ROOT / "docs/youra_research/h-m2/results/tagged_subset.parquet"
MODEL_RESULTS  = PROJECT_ROOT / "docs/youra_research/h-m2/results/model_results.json"

_CONTROLS         = "log_n_instances + log_n_features + age_years + age_sq + C(decade)"
FORMULA_BASELINE  = f"N_tasks ~ {_CONTROLS}"
FORMULA_PROPOSED  = f"N_tasks ~ log_tag_count_p1 + {_CONTROLS}"
FORMULA_NO_FE     = "N_tasks ~ log_tag_count_p1 + log_n_instances + log_n_features + age_years + age_sq"
NB2_METHOD        = "bfgs"
NB2_MAXITER       = 100

class NumpyEncoder(json.JSONEncoder): ...
    # handles np.integer, np.floating, np.ndarray

def ct_lr_test(df_tagged: pd.DataFrame) -> dict: ...
    # Fit Poisson(FORMULA_BASELINE) and NB2(FORMULA_BASELINE) on df_tagged
    # LR = 2*(llf_nb2 - llf_poisson)
    # Returns {'lr_stat': float, 'p_value': float, 'nb2_appropriate': bool}

def fit_nb2(formula: str, df: pd.DataFrame, label: str) -> tuple[Any, dict]: ...
    # smf.negativebinomial(formula, data=df, loglike_method='nb2').fit(method=NB2_METHOD, maxiter=NB2_MAXITER, disp=False)
    # Fallback: method='nm' (Nelder-Mead) if convergence fails
    # Returns (result_obj, stats_dict)

def extract_iv_stats(result: Any, iv_name: str) -> dict: ...
    # irr = np.exp(result.params[iv_name])
    # ci = result.conf_int(); ci_lower/upper = np.exp(ci.loc[iv_name, 0/1])
    # pval = result.pvalues[iv_name]
    # Returns {'irr': float, 'ci_lower': float, 'ci_upper': float, 'pval': float}

def compute_attenuation(irr_no_fe: float, irr_with_fe: float) -> float: ...
    # attenuation_ratio = irr_no_fe / irr_with_fe

def main() -> None: ...
    # [1] load tagged_subset.parquet
    # [2] ct_lr_test
    # [3] fit baseline NB-2
    # [4] fit proposed NB-2 (with C(decade))
    # [5] fit proposed NB-2 (no C(decade)) for attenuation
    # [6] compute_attenuation
    # [7] serialize all to model_results.json
```

---

### FigureGenerator (`code/03_generate_figures.py`)

**Dependencies**: matplotlib, numpy, pandas, json

```python
from pathlib import Path

PROJECT_ROOT   = Path(__file__).resolve().parents[4]
MODEL_RESULTS  = PROJECT_ROOT / "docs/youra_research/h-m2/results/model_results.json"
TAGGED_PARQUET = PROJECT_ROOT / "docs/youra_research/h-m2/results/tagged_subset.parquet"
FIGURES_DIR    = PROJECT_ROOT / "docs/youra_research/h-m2/figures"
GATE_THRESHOLD = 1.05

def fig1_gate_metrics(results: dict) -> None: ...
    # Bar chart: IRR_P2 with CI error bars; horizontal dashed line at 1.05
    # Annotate PASS / INFORMATIVE_NEGATIVE; save fig1_gate_metrics.png

def fig2_tag_count_distribution(df_tagged: pd.DataFrame) -> None: ...
    # Histogram of tag_count; log x-axis if max/median > 10
    # Save fig2_tag_count_distribution.png

def fig3_partial_regression(df_tagged: pd.DataFrame, results: dict) -> None: ...
    # Added variable plot: log_tag_count_p1 vs residual log(N_tasks)
    # Partial out controls via OLS residuals; scatter + regression line
    # Save fig3_partial_regression.png

def fig4_attenuation_forest(results: dict) -> None: ...
    # Forest plot: IRR with/without C(decade) FE for log_tag_count_p1
    # Error bars = 95% CI; vertical line at 1.0 and 1.05
    # Save fig4_attenuation_forest.png

def main() -> None: ...
    # load model_results.json + tagged_subset.parquet
    # call fig1–fig4; save all to FIGURES_DIR at 300 DPI
```

---

### GateEvaluator (`code/04_evaluate_gate.py`)

**Dependencies**: json

```python
from pathlib import Path

PROJECT_ROOT    = Path(__file__).resolve().parents[4]
MODEL_RESULTS   = PROJECT_ROOT / "docs/youra_research/h-m2/results/model_results.json"
PRIMARY_RESULTS = PROJECT_ROOT / "docs/youra_research/h-m2/results/primary_results.json"

GATE_CI_LOWER_MIN = 1.05
GATE_PVAL_MAX     = 0.05

def evaluate_gate(irr: float, ci_lower: float, pval: float, n_tagged: int,
                  attenuation_ratio: float) -> dict: ...
    # passed = (ci_lower >= 1.05) and (pval < 0.05)
    # result_label = 'PASS' if passed else 'INFORMATIVE_NEGATIVE'
    # Returns full results dict for primary_results.json

def main() -> None: ...
    # [1] load model_results.json
    # [2] extract proposed model IV stats
    # [3] evaluate_gate
    # [4] print verdict (PASS / INFORMATIVE_NEGATIVE)
    # [5] save primary_results.json
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| H-E1 preprocessed parquet | `PROJECT_ROOT / "docs/youra_research/h-e1/results/preprocessed.parquet"` | `h-e1/results/preprocessed.parquet` |
| H-E1 raw CSV (fallback) | `PROJECT_ROOT / "docs/youra_research/h-e1/code/data/h_e1/openml_dataset_corpus.csv"` | `h-e1/code/data/h_e1/openml_dataset_corpus.csv` |
| H-M1 results (context) | `PROJECT_ROOT / "docs/youra_research/h-m1/results/primary_results.json"` | `h-m1/results/primary_results.json` |

**Verified from**: `docs/youra_research/h-e1/code/` and `docs/youra_research/h-m1/code/` (actual implementation)

**Note**: H-E1 `derive_features()` already computes `tag_count` and `log_tag_count_p1` — these columns are present in `preprocessed.parquet`. Script `01_preprocess.py` only needs to filter and verify, not re-derive.

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & paths | Project dirs, verify H-E1 parquet accessible, path constants | 4 | 1+1+1+1 |
| A-2 | 01_preprocess.py | Load parquet, filter has_tags=1, verify tag_count/log_tag_count_p1, collinearity check, save tagged_subset.parquet | 8 | 2+2+2+2 |
| A-3 | 02_fit_models.py CT LR test | Poisson + NB-2 baseline on df_tagged, LR overdispersion test | 7 | 2+2+2+1 |
| A-4 | 02_fit_models.py model fits | Proposed NB-2 (with FE), proposed NB-2 (no FE), attenuation ratio, serialize model_results.json | 10 | 3+2+3+2 |
| A-5 | 03_generate_figures.py | 4 figures: gate bar, tag dist, partial regression, forest plot | 11 | 3+2+3+3 |
| A-6 | 04_evaluate_gate.py | Gate logic (SHOULD_WORK), primary_results.json, verdict print | 6 | 2+1+2+1 |
| A-7 | Integration test | Run full 4-script pipeline end-to-end, confirm N≈2625, gate verdict printed, all outputs saved | 9 | 2+2+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-5, A-7], Low(4-8): [A-1, A-2, A-3, A-6]
