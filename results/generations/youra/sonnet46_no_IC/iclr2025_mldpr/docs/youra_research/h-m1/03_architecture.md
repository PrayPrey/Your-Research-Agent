# Architecture: H-M1 — Tag-Indexed Search Pathway Mechanism Verification

Applied: continuation-experiment minimal-script pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis extension
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**: H-E1 has 4 standalone scripts (01_preprocess, 02_fit_models, 03_generate_figures, 04_evaluate_gate). Key reuse: `fit_nb2()`, `NumpyEncoder`, path constants, BFGS optimizer config. H-M1 mirrors this 4-script structure exactly.

---

## Project Structure

```
docs/youra_research/h-m1/
├── code/
│   ├── 01_load_data.py         # FR-01, FR-02
│   ├── 02_fit_models.py        # FR-03, FR-04, FR-05
│   ├── 03_generate_figures.py  # FR-07
│   └── 04_evaluate_gate.py     # FR-06, FR-08
├── figures/                    # created by 03_generate_figures.py
└── results/
    └── primary_results.json    # created by 04_evaluate_gate.py
```

No shared library — each script is standalone, importing only stdlib + pandas/numpy/statsmodels/scipy/matplotlib.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Asset | Path | Notes |
|-------|------|-------|
| Preprocessed data | `docs/youra_research/h-e1/results/preprocessed.parquet` | N=5,217 |
| Model results | `docs/youra_research/h-e1/results/model_results.json` | has `proposed`, `rc7_age_only` keys |
| fit_nb2 pattern | `docs/youra_research/h-e1/code/02_fit_models.py:77-111` | copy inline, not imported |
| NumpyEncoder | `docs/youra_research/h-e1/code/02_fit_models.py:44` | copy inline |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

H-E1 scripts use `BASE_DIR = "docs/youra_research/h-e1"` with relative paths — H-M1 follows same convention with `BASE_DIR = "docs/youra_research/h-m1"`.

---

## Module Definitions

### DataLoader (`code/01_load_data.py`)

**Dependencies**: pandas, pyarrow, json, pathlib

```python
H_E1_BASE    = "docs/youra_research/h-e1"
PREPROCESSED = f"{H_E1_BASE}/results/preprocessed.parquet"
MODEL_RESULTS = f"{H_E1_BASE}/results/model_results.json"
EXPECTED_N   = 5217

def load_preprocessed() -> pd.DataFrame: ...
    # reads PREPROCESSED, asserts len==5217 and has_tags in {0,1}
    # fallback: re-runs H-E1 preprocessing from raw CSV if parquet missing

def load_h_e1_results() -> dict | None: ...
    # loads MODEL_RESULTS; returns None if file missing (triggers refit)

def main() -> None: ...
    # runs load_preprocessed + load_h_e1_results, prints summary stats
```

---

### ModelFitter (`code/02_fit_models.py`)

**Dependencies**: pandas, numpy, statsmodels, scipy.stats, json, pathlib

```python
H_E1_BASE     = "docs/youra_research/h-e1"
H_M1_BASE     = "docs/youra_research/h-m1"
PREPROCESSED  = f"{H_E1_BASE}/results/preprocessed.parquet"
H_E1_RESULTS  = f"{H_E1_BASE}/results/model_results.json"
MODEL_RESULTS = f"{H_M1_BASE}/results/model_results.json"

_CONTROLS       = "log_n_instances + log_n_features + age_years + age_sq"
FORMULA_WITH_FE = f"N_tasks ~ has_tags + {_CONTROLS} + C(decade)"
FORMULA_NO_FE   = f"N_tasks ~ has_tags + {_CONTROLS}"
NB2_METHOD      = "bfgs"
NB2_MAXITER     = 100

class NumpyEncoder(json.JSONEncoder): ...  # copied from H-E1

def fit_nb2(formula: str, df: pd.DataFrame, label: str) -> dict: ...
    # copied from H-E1 02_fit_models.py:77-111 verbatim
    # BFGS with Nelder-Mead fallback, returns params/pvalues/conf_int dict

def extract_irr(model_dict: dict, coef: str = "has_tags") -> tuple[float, float, float, float]: ...
    # returns (irr, ci_lower, ci_upper, pval)

def compute_cramers_v(df: pd.DataFrame) -> tuple[float, float]: ...
    # crosstab(decade, has_tags) → chi2_contingency → cramers_v, p_chi2

def compute_attenuation_ratio(irr_no_fe: float, irr_with_fe: float) -> float: ...
    # irr_no_fe / irr_with_fe

def load_or_fit_models(df: pd.DataFrame, h_e1_results: dict | None) -> dict: ...
    # if h_e1_results has 'proposed' and 'rc7_age_only': extract directly
    # else: fit FORMULA_WITH_FE and FORMULA_NO_FE via fit_nb2

def main() -> None: ...
    # load data → load_or_fit_models → compute_cramers_v → compute_attenuation_ratio
    # serialize all to MODEL_RESULTS
```

---

### FigureGenerator (`code/03_generate_figures.py`)

**Dependencies**: pandas, numpy, matplotlib, json, pathlib

```python
H_M1_BASE    = "docs/youra_research/h-m1"
MODEL_RESULTS = f"{H_M1_BASE}/results/model_results.json"
PREPROCESSED  = "docs/youra_research/h-e1/results/preprocessed.parquet"
FIGURES_DIR   = f"{H_M1_BASE}/figures"
FIGURE_DPI    = 300
FIGURE_FORMAT = "png"

def save_fig(fig: Figure, name: str) -> None: ...

def fig1_irr_comparison(results: dict) -> None: ...
    # bar chart: IRR with FE vs without FE + 95% CI error bars
    # threshold line at IRR=1.0
    # title: "H-M1 Mechanism Verification: has_tags Survives Decade FE"
    # saves: fig1_irr_comparison.png

def fig2_hastags_by_decade(df: pd.DataFrame) -> None: ...
    # bar chart: df.groupby('decade')['has_tags'].mean()
    # saves: fig2_hastags_by_decade.png

def fig3_coefficient_table(results: dict) -> None: ...
    # matplotlib table: has_tags coef, IRR, CI, p across model variants
    # saves: fig3_coefficient_table.png

def fig4_mechanism_flow(results: dict) -> None: ...
    # text-based flow diagram: Tags→Search Index→Discovery→Task Creation
    # saves: fig4_mechanism_flow.png (optional)

def main() -> None: ...
```

---

### GateEvaluator (`code/04_evaluate_gate.py`)

**Dependencies**: json, pathlib

```python
H_M1_BASE       = "docs/youra_research/h-m1"
MODEL_RESULTS   = f"{H_M1_BASE}/results/model_results.json"
PRIMARY_RESULTS = f"{H_M1_BASE}/results/primary_results.json"

GATE_IRR_MIN  = 1.1
GATE_PVAL_MAX = 0.05
H_E1_IRR_PREREQ = 1.2263
H_E1_GATE_PREREQ = "PASS"

def evaluate_mechanism(irr_with_fe: float, p_with_fe: float,
                        attenuation_ratio: float) -> str: ...
    # returns "STRONG" | "MODERATE"

def evaluate_gate(h_e1_gate: str, irr_with_fe: float,
                  p_with_fe: float) -> str: ...
    # returns "PASS" | "FAIL"

def build_results(model_results: dict) -> dict: ...
    # constructs primary_results.json payload per FR-08

def main() -> None: ...
    # load MODEL_RESULTS → build_results → evaluate_gate → write PRIMARY_RESULTS
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Project Setup | Create dirs (h-m1/code, figures, results), verify H-E1 parquet exists | 5 | 1+1+1+2 |
| A-2 | Data Loader | `01_load_data.py`: load parquet, assert N=5217, load H-E1 model_results.json | 6 | 2+1+1+2 |
| A-3 | Model Fitter (core) | `02_fit_models.py`: copy fit_nb2 from H-E1, implement load_or_fit_models with parquet/json fallback logic | 10 | 3+2+3+2 |
| A-4 | Attenuation & Cramér's V | In 02_fit_models.py: compute_cramers_v, compute_attenuation_ratio, serialize results | 7 | 2+2+2+1 |
| A-5 | Figure 1 (mandatory) | `03_generate_figures.py`: IRR comparison bar chart with CI error bars and threshold line | 8 | 2+2+2+2 |
| A-6 | Figures 2-4 | fig2_hastags_by_decade, fig3_coefficient_table, fig4_mechanism_flow | 8 | 2+2+2+2 |
| A-7 | Gate Evaluator | `04_evaluate_gate.py`: evaluate_gate, build_results, write primary_results.json | 7 | 2+1+2+2 |
| A-8 | End-to-end Integration | Run all 4 scripts in sequence, verify outputs match expected values (IRR≈1.2263, Cramér's V≈0.823) | 9 | 2+2+2+3 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-3, A-8], Low(4-8): [A-1, A-2, A-4, A-5, A-6, A-7]

---

## Execution Order

```
01_load_data.py       # verify inputs exist
02_fit_models.py      # fit or load models, compute attenuation + Cramér's V
03_generate_figures.py # produce 3-4 PNGs
04_evaluate_gate.py   # gate check, write primary_results.json
```

Each script is runnable standalone from project root:
```bash
python docs/youra_research/h-m1/code/01_load_data.py
python docs/youra_research/h-m1/code/02_fit_models.py
python docs/youra_research/h-m1/code/03_generate_figures.py
python docs/youra_research/h-m1/code/04_evaluate_gate.py
```
