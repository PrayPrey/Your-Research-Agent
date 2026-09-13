# Architecture: H-E1 — Binary Tag Presence → Task Count (NB-2 Existence Test)

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-05

Applied: sequential-pipeline (4-script linear pipeline with parquet intermediate handoff)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: docs/youra_research/h-e1/code (does not exist yet)
**Findings**: New implementation from scratch; only existing artifact is corpus CSV at `docs/youra_research/h-e1/code/data/h_e1/openml_dataset_corpus.csv`

---

## File Organization

```
docs/youra_research/h-e1/
├── code/
│   ├── 01_preprocess.py
│   ├── 02_fit_models.py
│   ├── 03_generate_figures.py
│   ├── 04_evaluate_gate.py
│   ├── requirements.txt
│   └── data/
│       └── h_e1/
│           └── openml_dataset_corpus.csv  (existing cache)
├── results/
│   ├── preprocessed.parquet               (output of 01)
│   └── model_results.json                 (output of 02)
│       primary_results.json               (output of 04)
└── figures/
    ├── fig1_gate_metrics.png
    ├── fig2_forest_plot.png
    ├── fig3_decade_adoption.png
    ├── fig4_rc_comparison.png
    └── fig5_obs_vs_pred.png
```

---

## Module Structure

### Script 01 — Preprocess (`code/01_preprocess.py`)

**Dependencies**: pandas, numpy, scipy.stats

```python
CORPUS_PATH = "docs/youra_research/h-e1/code/data/h_e1/openml_dataset_corpus.csv"
OUT_PATH = "docs/youra_research/h-e1/results/preprocessed.parquet"

def load_corpus(path: str) -> pd.DataFrame: ...
    # pd.read_csv → filter N_tasks >= 1 → assert len == 5217

def derive_features(df: pd.DataFrame) -> pd.DataFrame: ...
    # has_tags, tag_count, log_n_instances, log_n_features,
    # upload_year, age_years, age_sq, decade

def validate(df: pd.DataFrame) -> None: ...
    # assert N=5217, no NaN in key cols, has_tags has both 0 and 1

def check_decade_correlation(df: pd.DataFrame) -> dict: ...
    # groupby decade → mean has_tags; chi2/cramers_v; return dict

def main() -> None: ...
    # load → derive → validate → check_decade_correlation (log) → save parquet
```

---

### Script 02 — Fit Models (`code/02_fit_models.py`)

**Dependencies**: pandas, numpy, scipy.stats, statsmodels.formula.api

```python
IN_PATH = "docs/youra_research/h-e1/results/preprocessed.parquet"
OUT_PATH = "docs/youra_research/h-e1/results/model_results.json"

FORMULA_CONTROLS = "N_tasks ~ log_n_instances + log_n_features + age_years + age_sq + C(decade)"
FORMULA_PROPOSED = "N_tasks ~ has_tags + " + FORMULA_CONTROLS.split("~")[1].strip()

def ct_lr_test(df: pd.DataFrame) -> dict: ...
    # fit Poisson + NB-2 with proposed formula
    # return {lr_stat, p_value, nb2_appropriate: bool}

def fit_nb2(formula: str, df: pd.DataFrame, label: str) -> dict: ...
    # smf.negativebinomial(formula, data=df, loglike_method='nb2').fit(method='bfgs', maxiter=100)
    # return {label, params, bse, pvalues, conf_int, llf, aic, bic}

def extract_has_tags_stats(model_dict: dict) -> dict: ...
    # irr, ci_lower, ci_upper, pval for has_tags coefficient

def rc4_winsorized(df: pd.DataFrame) -> dict: ...
    # clip N_tasks at 99th pct → fit_nb2 → extract_has_tags_stats

def rc5_tagged_only(df: pd.DataFrame) -> dict: ...
    # df[df.tag_count >= 1] → fit_nb2 → extract_has_tags_stats

def rc7_age_vs_decade(df: pd.DataFrame) -> dict: ...
    # fit age_years+age_sq only model (no C(decade)) → compare IRR

def main() -> None: ...
    # load parquet → ct_lr_test → fit baseline → fit proposed
    # → rc4, rc5, rc7 → serialize all to JSON
```

---

### Script 03 — Generate Figures (`code/03_generate_figures.py`)

**Dependencies**: pandas, numpy, matplotlib, json

```python
RESULTS_PATH = "docs/youra_research/h-e1/results/model_results.json"
DATA_PATH = "docs/youra_research/h-e1/results/preprocessed.parquet"
FIG_DIR = "docs/youra_research/h-e1/figures/"
THRESHOLD = 1.1

def fig1_gate_metrics(results: dict) -> None: ...
    # bar chart: IRR + CI error bars for has_tags; hline at THRESHOLD
    # save fig1_gate_metrics.png

def fig2_forest_plot(results: dict) -> None: ...
    # horizontal bar chart: all covariates IRR + CI from proposed model
    # save fig2_forest_plot.png

def fig3_decade_adoption(df: pd.DataFrame) -> None: ...
    # bar chart: mean has_tags rate per decade
    # save fig3_decade_adoption.png

def fig4_rc_comparison(results: dict) -> None: ...
    # bar chart: IRR for has_tags across primary/RC-4/RC-5/RC-7
    # hline at THRESHOLD; save fig4_rc_comparison.png

def fig5_obs_vs_pred(results: dict, df: pd.DataFrame) -> None: ...
    # scatter: log(N_tasks+1) observed vs predicted from proposed model
    # save fig5_obs_vs_pred.png

def main() -> None: ...
    # load results JSON + parquet → generate all 5 figures → save PNG 300 DPI
```

---

### Script 04 — Evaluate Gate (`code/04_evaluate_gate.py`)

**Dependencies**: json

```python
RESULTS_PATH = "docs/youra_research/h-e1/results/model_results.json"
PRIMARY_OUT = "docs/youra_research/h-e1/results/primary_results.json"

def evaluate_gate(irr: float, ci_lower: float, ci_upper: float, pval: float) -> str: ...
    # returns "PASS" / "PARTIAL_PASS" / "FAIL"
    # PASS: irr >= 1.1 and ci_lower >= 1.1 and pval < 0.05
    # PARTIAL_PASS: 1.05 <= ci_lower < 1.1 and pval < 0.05
    # FAIL: otherwise

def main() -> None: ...
    # load model_results.json → extract has_tags stats from proposed model
    # → evaluate_gate → write primary_results.json
    # → print clear PASS/PARTIAL_PASS/FAIL verdict
```

---

## Epic Tasks

### Epic E1: Preprocessing Pipeline
**Complexity:** 7/20 (Low)
**Breakdown:** Module_Size(2) + Dependencies(1) + Algorithm(2) + Integration(2) = 7
**Description:** Implement 01_preprocess.py — load corpus, derive all features, validate N=5217, check decade-has_tags correlation, save parquet.
**Files:** `docs/youra_research/h-e1/code/01_preprocess.py`
**Acceptance Criteria:**
- Loads CSV, asserts N=5,217 after N_tasks>=1 filter
- All derived columns present: has_tags, tag_count, log_n_instances, log_n_features, age_years, age_sq, decade
- No NaN in key columns; has_tags has both 0 and 1 values
- Decade-has_tags correlation logged (mean has_tags by decade printed)
- Output saved to `results/preprocessed.parquet`

### Epic E2: Model Fitting Suite
**Complexity:** 12/20 (Medium)
**Breakdown:** Module_Size(3) + Dependencies(2) + Algorithm(4) + Integration(3) = 12
**Description:** Implement 02_fit_models.py — CT LR overdispersion test, baseline NB-2, proposed NB-2, RC-4/5/7 robustness checks, serialize all results to JSON.
**Files:** `docs/youra_research/h-e1/code/02_fit_models.py`
**Acceptance Criteria:**
- CT LR test runs and reports NB-2 appropriateness (expect LR >> 3.84)
- Baseline NB-2 (controls-only) converges with BFGS
- Proposed NB-2 (has_tags + controls) converges with BFGS maxiter=100
- IRR, CI_lower, CI_upper, pval extracted for has_tags from proposed model
- RC-4 (winsorized), RC-5 (tagged-only), RC-7 (age vs decade) all complete
- All results serialized to `results/model_results.json`

### Epic E3: Figure Generation
**Complexity:** 9/20 (Medium)
**Breakdown:** Module_Size(3) + Dependencies(1) + Algorithm(2) + Integration(3) = 9
**Description:** Implement 03_generate_figures.py — all 5 required figures saved as PNG 300 DPI.
**Files:** `docs/youra_research/h-e1/code/03_generate_figures.py`
**Acceptance Criteria:**
- Fig 1 (mandatory): IRR bar chart with CI error bars, threshold line at 1.1
- Fig 2: Forest plot for all covariates in proposed model
- Fig 3: has_tags adoption rate by decade bar chart
- Fig 4: RC suite IRR comparison bar chart with threshold line
- Fig 5: Observed vs predicted N_tasks scatter (log scale)
- All saved to `docs/youra_research/h-e1/figures/` at 300 DPI PNG

### Epic E4: Gate Evaluation
**Complexity:** 5/20 (Low)
**Breakdown:** Module_Size(1) + Dependencies(1) + Algorithm(1) + Integration(2) = 5
**Description:** Implement 04_evaluate_gate.py — apply gate logic, write primary_results.json, print verdict.
**Files:** `docs/youra_research/h-e1/code/04_evaluate_gate.py`, `docs/youra_research/h-e1/results/primary_results.json`
**Acceptance Criteria:**
- Loads model_results.json, extracts proposed model has_tags stats
- Gate logic: PASS (IRR>=1.1 AND CI_lower>=1.1 AND p<0.05), PARTIAL_PASS (CI_lower in [1.05,1.1) AND p<0.05), FAIL otherwise
- primary_results.json contains: gate_result, irr, ci_lower, ci_upper, pval
- Clear PASS/PARTIAL_PASS/FAIL verdict printed to stdout

**Distribution**: High(14-17): [], Medium(9-13): [E2, E3], Low(4-8): [E1, E4]

---

## Dependencies

```
statsmodels>=0.14
numpy>=1.24
pandas>=2.0
scipy>=1.10
matplotlib>=3.7
patsy>=0.5
openml>=0.14   # fallback only if CSV missing
```

No GPU, no PyTorch/TensorFlow. Pure statsmodels/pandas/numpy/scipy/matplotlib.

---

## Data Flow

```
openml_dataset_corpus.csv
  → 01_preprocess.py → results/preprocessed.parquet
  → 02_fit_models.py → results/model_results.json
  → 03_generate_figures.py → figures/*.png
  → 04_evaluate_gate.py → results/primary_results.json + stdout verdict
```
