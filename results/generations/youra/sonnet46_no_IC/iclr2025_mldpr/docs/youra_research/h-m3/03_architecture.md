# Architecture: H-M3 — Categorical Tag Count Dose-Response (NB-2)

**Date:** 2026-08-05
**Gate:** SHOULD_WORK
**Type:** MECHANISM (Dose-Response Categorical)

Applied: flat-4-script statistical pipeline (H-E1 pattern)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: H-E1 uses 4 flat scripts (01_preprocess.py, 02_fit_models.py, 03_generate_figures.py, 04_evaluate_gate.py) with module-level constants for paths/thresholds and a `main()` entry point per file. H-M3 mirrors this structure exactly. Optimizer: `method='bfgs', maxiter=100, disp=False`. Path convention: `BASE_DIR = "docs/youra_research/h-e1"`.

---

## File Organization

```
docs/youra_research/h-m3/
├── code/
│   ├── 01_preprocess.py       # Load H-E1 parquet, derive tag_count_cat bins, verify controls
│   ├── 02_fit_models.py       # CT LR test, baseline NB-2, categorical NB-2, RC-6, RC-7
│   ├── 03_generate_figures.py # 5 figures (IRR bar, dose-response, distribution, forest, attenuation)
│   └── 04_evaluate_gate.py    # Gate logic: monotonic AND ≥2/3 contrasts p < 0.0167
├── figures/                   (created at runtime)
└── results/
    └── primary_results.json   (created at runtime)
```

---

## Modules

### 01_preprocess (`code/01_preprocess.py`)

**Dependencies**: pandas, numpy, pyarrow (parquet)

```python
BASE_DIR: str = "docs/youra_research/h-m3"
H_E1_PARQUET: str = "docs/youra_research/h-e1/results/preprocessed.parquet"
H_E1_CSV_FALLBACK: str = "docs/youra_research/h-e1/code/data/h_e1/openml_dataset_corpus.csv"
PREPROCESSED_OUT: str = f"{BASE_DIR}/results/preprocessed.parquet"
EXPECTED_N: int = 5217
BIN_BREAKS: list = [-1, 0, 2, 5, float('inf')]
BIN_LABELS: list = ["0", "1-2", "3-5", "6+"]

def load_corpus() -> pd.DataFrame: ...
    # Primary: pd.read_parquet(H_E1_PARQUET)
    # Fallback: pd.read_csv(H_E1_CSV_FALLBACK) + re-derive controls

def derive_tag_count(df: pd.DataFrame) -> pd.DataFrame: ...
    # if 'tag_count' not in df: compute from 'tags' column
    # derive tag_count_cat via pd.cut(BIN_BREAKS, BIN_LABELS)

def verify_controls(df: pd.DataFrame) -> pd.DataFrame: ...
    # assert all controls present; dropna; assert len >= 5000

def validate(df: pd.DataFrame) -> None: ...
    # assert 4 non-empty bins; print bin distribution

def main() -> None: ...
```

### 02_fit_models (`code/02_fit_models.py`)

**Dependencies**: statsmodels, scipy, numpy, pandas, json

```python
BASE_DIR: str = "docs/youra_research/h-m3"
PREPROCESSED: str = f"{BASE_DIR}/results/preprocessed.parquet"
MODEL_RESULTS: str = f"{BASE_DIR}/results/model_results.json"
_CONTROLS: str = "log_n_instances + log_n_features + age_years + age_sq + C(decade)"
FORMULA_BASELINE: str = f"N_tasks ~ {_CONTROLS}"
FORMULA_BINARY: str = f"N_tasks ~ has_tags + {_CONTROLS}"
FORMULA_CAT: str = f"N_tasks ~ C(tag_count_cat) + {_CONTROLS}"
FORMULA_RC6: str = f"N_tasks ~ C(tag_count_cat)*C(decade) + log_n_instances + log_n_features + age_years + age_sq"
FORMULA_RC7: str = f"N_tasks ~ C(tag_count_cat) + log_n_instances + log_n_features + age_years + age_sq"
NB2_METHOD: str = "bfgs"
NB2_MAXITER: int = 200
NB2_DISP: bool = False
BONF_ALPHA: float = 0.0167

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any: ...

def ct_lr_test(df: pd.DataFrame) -> dict: ...
    # fit Poisson + NB-2 (controls-only); return lr_stat, p_value

def fit_nb2(formula: str, df: pd.DataFrame) -> Any: ...
    # smf.negativebinomial(formula, data=df, loglike_method='nb2').fit(...)

def extract_cat_irr(result: Any) -> dict: ...
    # extract IRR, CI, pvalue for each C(tag_count_cat) level

def check_monotonicity(irr_dict: dict) -> tuple[bool, tuple]: ...
    # verify IRR(1-2) < IRR(3-5) < IRR(6+) and all > 1.0

def test_adjacent_contrasts(result: Any) -> tuple[pd.DataFrame, int]: ...
    # result.t_test_pairwise('C(tag_count_cat)', method='bonferroni')
    # return result_frame, n_passing (count where adj contrast p < BONF_ALPHA)

def serialize_results(data: dict) -> None: ...

def main() -> None: ...
    # run ct_lr_test, fit_nb2 x4 (baseline, binary, cat, RC6, RC7)
    # check_monotonicity, test_adjacent_contrasts
    # serialize_results to MODEL_RESULTS
```

### 03_generate_figures (`code/03_generate_figures.py`)

**Dependencies**: matplotlib, numpy, pandas, json

```python
BASE_DIR: str = "docs/youra_research/h-m3"
MODEL_RESULTS: str = f"{BASE_DIR}/results/model_results.json"
FIGURES_DIR: str = f"{BASE_DIR}/figures"
FIGURE_DPI: int = 300
FIGURE_FORMAT: str = "png"

def save_fig(fig: Any, name: str) -> None: ...

def fig1_irr_bar_chart(results: dict) -> None: ...
    # IRR per category (0,1-2,3-5,6+) with 95% CI error bars
    # horizontal reference lines at IRR=1.0 and IRR=1.1

def fig2_dose_response(results: dict) -> None: ...
    # IRR by category colored by adjacent contrast significance

def fig3_bin_distribution(results: dict) -> None: ...
    # bar chart of N per tag_count_cat bin

def fig4_contrast_forest(results: dict) -> None: ...
    # forest plot of 3 adjacent contrasts with Bonferroni CIs

def fig5_attenuation(results: dict) -> None: ...
    # IRR with vs without C(decade) FE (primary vs RC-7)

def main() -> None: ...
```

### 04_evaluate_gate (`code/04_evaluate_gate.py`)

**Dependencies**: json

```python
BASE_DIR: str = "docs/youra_research/h-m3"
MODEL_RESULTS: str = f"{BASE_DIR}/results/model_results.json"
PRIMARY_RESULTS: str = f"{BASE_DIR}/results/primary_results.json"
BONF_ALPHA: float = 0.0167
MIN_CONTRASTS_PASS: int = 2

def evaluate_gate(model_data: dict) -> dict: ...
    # extract is_monotonic, n_adj_passing from model_data
    # gate_pass = is_monotonic and n_adj_passing >= MIN_CONTRASTS_PASS
    # return full gate result dict

def main() -> None: ...
    # load MODEL_RESULTS, evaluate_gate, save PRIMARY_RESULTS
```

---

## External Dependencies (Base Hypothesis)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| Preprocessed corpus | `pd.read_parquet("docs/youra_research/h-e1/results/preprocessed.parquet")` | `h-e1/results/preprocessed.parquet` |
| CSV fallback | `pd.read_csv("docs/youra_research/h-e1/code/data/h_e1/openml_dataset_corpus.csv")` | `h-e1/code/data/h_e1/openml_dataset_corpus.csv` |

**Verified from**: `docs/youra_research/h-e1/code/02_fit_models.py` (actual implementation: `BASE_DIR = "docs/youra_research/h-e1"`, `PREPROCESSED = f"{BASE_DIR}/results/preprocessed.parquet"`)

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Paths | Create h-m3/code/ dir structure, results/, figures/ dirs; verify H-E1 parquet accessible | 5 | 1+1+1+2 |
| A-2 | Implement 01_preprocess.py | Load H-E1 parquet, derive tag_count/tag_count_cat bins, verify controls, validate bin counts | 8 | 2+2+2+2 |
| A-3 | Implement CT LR test + baseline NB-2 | ct_lr_test(), fit_nb2() for Poisson and controls-only NB-2 in 02_fit_models.py | 7 | 2+2+2+1 |
| A-4 | Implement categorical NB-2 (primary model) | fit_nb2(FORMULA_CAT), extract_cat_irr(), serialize IRR/CI/pvalues | 9 | 2+2+3+2 |
| A-5 | Implement monotonicity check | check_monotonicity() verifying IRR(1-2) < IRR(3-5) < IRR(6+), all > 1.0 | 6 | 1+1+3+1 |
| A-6 | Implement adjacent contrast testing | test_adjacent_contrasts() via t_test_pairwise(method='bonferroni'), count passing at p<0.0167 | 9 | 2+2+3+2 |
| A-7 | Implement RC-6 and RC-7 | fit decade-interaction and no-decade-FE models; compute attenuation ratios | 8 | 2+2+2+2 |
| A-8 | Implement 04_evaluate_gate.py | evaluate_gate(): monotonic AND ≥2/3 contrasts → PASS/PARTIAL/INFORMATIVE_NEGATIVE; save primary_results.json | 7 | 2+1+2+2 |
| A-9 | Implement 5 figures | fig1 (mandatory IRR bar), fig2 (dose-response colored), fig3 (distribution), fig4 (forest), fig5 (attenuation) | 10 | 2+2+2+4 |
| A-10 | Integration test & end-to-end run | Run scripts 01→04 sequentially; verify N=5217, 4 non-empty bins, convergence, primary_results.json written | 9 | 2+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-4, A-6, A-9, A-10], Low(4-8): [A-1, A-2, A-3, A-5, A-7, A-8]
