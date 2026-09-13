# Architecture: H-E1
# BCBHS: Domain-Specific Health Signal Discriminability (EXISTENCE PoC)

**Hypothesis ID:** H-E1
**Date:** 2026-05-19
**Phase:** 3 - Architecture Design
**Type:** EXISTENCE (PoC) — LIGHT tier

Applied: statistical-pipeline-module-pattern

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze
**Analyzed Path**: docs/youra_research/20260519_mldpr/h-e1 (documentation only)
**Findings**: New implementation from scratch — all modules designed fresh from PRD specifications

---

## File Structure

```
h-e1/code/
├── data_pipeline.py     # FR-1, FR-2, FR-3: data loading + saturation labeling
├── signal_compute.py    # FR-4, FR-5, FR-6: H_d signal computation per domain
├── baseline.py          # FR-7: naive logistic regression baseline
├── evaluate.py          # FR-8, FR-9: statistical testing + mechanism verification
├── visualize.py         # FR-10, FR-11: figure generation + temporal analysis
└── run_experiment.py    # Entry point / orchestration
```

---

## Module Interfaces

### DataPipeline (`h-e1/code/data_pipeline.py`)

**Dependencies**: datasets, openml, pandas, numpy, scipy.stats

```python
def load_pwc_panel() -> pd.DataFrame: ...
# Returns: DataFrame with columns [benchmark, domain, model, date, score, quarter]
# Source: pwc-archive/evaluation-tables (HuggingFace)
# Filter: >=20 submissions, >=2 years history, known domain (cv or nlp)

def load_openml_panel() -> pd.DataFrame: ...
# Returns: DataFrame with columns [task_id, model, date, score, quarter]
# Source: openml.study.get_suite("amlb-classification-all") + CC18
# Filter: >=20 evaluated runs, >=2 years of submissions

def label_saturation(panel: pd.DataFrame) -> pd.DataFrame: ...
# Returns: panel with added column [label: saturated|healthy|excluded]
# Saturated: Kendall tau(ranking_{t-1}, ranking_t) > 0.90 for >=2 consecutive quarters
# Healthy: tau < 0.70; Excluded: 0.70 <= tau <= 0.90

def get_domain_panels(
    panel: pd.DataFrame,
    domain: str,           # "cv" | "nlp" | "tabular"
    min_saturated: int = 15,
    min_healthy: int = 15
) -> tuple[pd.DataFrame, pd.DataFrame]: ...
# Returns: (saturated_df, healthy_df) filtered to domain, raises warning if < min
```

---

### SignalCompute (`h-e1/code/signal_compute.py`)

**Dependencies**: numpy, scipy.stats, constat, pandas

```python
def compute_hd_cv(
    benchmark_scores: np.ndarray,    # (N_models,) at t-24mo
    held_out_scores: np.ndarray      # (N_models,) on OOD/held-out variants
) -> float: ...
# Returns: scalar robustness_gap = mean(benchmark_scores - held_out_scores)
# Fallback: if held_out_scores unavailable, returns score variance as proxy

def compute_hd_nlp(
    benchmark_data: dict,
    reference_benchmark_data: dict
) -> float | None: ...
# Returns: s_index = -log(p_contamination + 1e-10) via ConStat
# Returns None if reference benchmark unavailable

def compute_hd_tabular(
    rankings_over_time: np.ndarray,  # (T_quarters, N_models)
    n_bootstrap: int = 1000,
    seed: int = 42
) -> float: ...
# Returns: mean block-bootstrapped Kendall tau (block_size = T//4)

def compute_domain_signals(
    panel: pd.DataFrame,
    domain: str,              # "cv" | "nlp" | "tabular"
    lookback_months: int = 24
) -> pd.DataFrame: ...
# Returns: DataFrame with columns [benchmark, label, hd_signal]
# Applies the appropriate compute_hd_* function per domain
```

---

### Baseline (`h-e1/code/baseline.py`)

**Dependencies**: numpy, pandas, sklearn

```python
def extract_naive_features(panel: pd.DataFrame) -> pd.DataFrame: ...
# Returns: DataFrame with columns:
#   score_variance_last_4q: variance of top-10 model scores over last 4 quarters
#   improvement_slope: linear trend of best score over time
#   benchmark_age_months: time since first submission

def fit_baseline(
    X_train: np.ndarray,
    y_train: np.ndarray
) -> LogisticRegression: ...
# Returns: fitted sklearn.linear_model.LogisticRegression on naive features

def predict_baseline(
    model: LogisticRegression,
    X: np.ndarray
) -> np.ndarray: ...
# Returns: predicted probabilities for saturation class
```

---

### Evaluate (`h-e1/code/evaluate.py`)

**Dependencies**: numpy, scipy.stats, sklearn.metrics, baseline, signal_compute

```python
def test_discriminability(
    saturated_signals: np.ndarray,
    healthy_signals: np.ndarray
) -> dict: ...
# Returns: {"p_value": float, "auc": float, "cohens_d": float}
# Mann-Whitney U, AUC = U/(n_sat * n_healthy), Cohen's d pooled std

def evaluate_domain(
    domain_signals: pd.DataFrame,     # [benchmark, label, hd_signal]
    baseline_probs: np.ndarray,
    domain: str
) -> dict: ...
# Returns: {domain: {p_value, cohens_d, auc_hd, auc_baseline,
#                     n_benchmarks, n_saturated, n_healthy}}

def verify_mechanism_activated(domain_results: dict) -> tuple[bool, dict]: ...
# Returns: (all_activated: bool, per_domain_indicators: dict)
# Checks: signals_computed (>=15), groups_defined (>=10 each),
#         effect_measurable (|d|>0.0), better_than_baseline (auc_hd > auc_baseline)

def check_gate_condition(domain_results: dict) -> tuple[bool, dict]: ...
# Returns: (passed: bool, summary: dict)
# PASS if p<0.05 AND Cohen's d>0.5 in >=2 of 3 domains

def run_temporal_test(
    panel: pd.DataFrame,
    domain: str,
    lookbacks: list[int] = [6, 12, 18, 24]
) -> dict: ...
# Returns: {lookback_months: cohens_d} for temporal separation analysis (FR-11)

def save_results(results: dict, output_path: str) -> None: ...
# Saves all domain_results + gate status to CSV
```

---

### Visualize (`h-e1/code/visualize.py`)

**Dependencies**: matplotlib, seaborn, numpy, pandas

```python
def plot_gate_metrics(
    domain_results: dict,
    output_dir: str
) -> None: ...
# Saves: figures/gate_metrics.png
# Bar chart: p-value, Cohen's d, AUC per domain (target vs actual)

def plot_signal_boxplots(
    domain_signals: dict,   # {domain: DataFrame[benchmark, label, hd_signal]}
    output_dir: str
) -> None: ...
# Saves: figures/boxplots_domain.png

def plot_roc_curves(
    domain_results: dict,
    output_dir: str
) -> None: ...
# Saves: figures/roc_curves.png

def plot_temporal_separation(
    temporal_results: dict,   # {domain: {lookback_months: cohens_d}}
    output_dir: str
) -> None: ...
# Saves: figures/temporal_separation.png

def plot_scatter_saturation(
    domain_signals: dict,
    output_dir: str
) -> None: ...
# Saves: figures/scatter_saturation.png

def generate_all_figures(
    domain_results: dict,
    domain_signals: dict,
    temporal_results: dict,
    output_dir: str = "h-e1/figures/"
) -> None: ...
# Calls all plot_* functions; creates output_dir if not exists
```

---

### RunExperiment (`h-e1/code/run_experiment.py`)

**Dependencies**: data_pipeline, signal_compute, baseline, evaluate, visualize

```python
# Hardcoded config (argparse override supported)
CONFIG = {
    "seed": 42,
    "n_bootstrap": 1000,
    "lookback_months": 24,
    "min_submissions": 20,
    "significance_level": 0.05,
    "cohens_d_threshold": 0.5,
    "auc_threshold": 0.70,
    "min_saturated_per_domain": 15,
    "min_healthy_per_domain": 15,
    "output_dir": "h-e1/figures/",
    "results_csv": "h-e1/results.csv",
}

def main(args=None) -> None: ...
# Orchestrates: load data → label → compute signals → baseline →
#               evaluate → verify → check gate → visualize → save
# Prints gate pass/fail to stdout
```

---

## Data Flow

- `data_pipeline` loads PWC + OpenML panels and applies saturation labels
- `signal_compute` receives labeled panel per domain, returns `[benchmark, label, hd_signal]`
- `baseline` receives same panel, extracts naive features, fits + predicts
- `evaluate` receives domain_signals + baseline predictions → statistical results
- `visualize` receives all results → writes 5 figures to `h-e1/figures/`
- `run_experiment` orchestrates all steps, saves `results.csv`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data Pipeline | Load PWC (HuggingFace) + OpenML panels; apply saturation labeling (Kendall tau); filter by domain | 13 | 3+3+4+3 |
| A-2 | Signal Computation | Implement compute_hd_cv (robustness gap), compute_hd_nlp (ConStat S_index), compute_hd_tabular (block-bootstrapped Kendall tau) | 15 | 4+3+5+3 |
| A-3 | Baseline Model | Extract naive features (variance, slope, age); fit LogisticRegression; produce baseline predictions | 8 | 2+2+2+2 |
| A-4 | Evaluation + Gate Check | Mann-Whitney U, Cohen's d, AUC per domain; mechanism activation verification; gate condition check; temporal ordering test | 14 | 3+3+4+4 |
| A-5 | Visualization | Generate 5 figures (gate metrics, boxplots, ROC curves, temporal separation, scatter); save to h-e1/figures/ | 9 | 2+2+3+2 |
| A-6 | Orchestration + Integration | run_experiment.py entry point; argparse config; CSV logging; smoke test end-to-end | 8 | 2+2+2+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-2, A-4], Medium(9-13): [A-1, A-5], Low(4-8): [A-3, A-6]

---

## External Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| datasets | >=2.0.0 | HuggingFace PWC archive loading |
| openml | >=0.14.0 | OpenML benchmark panel |
| scipy | >=1.9.0 | mannwhitneyu, kendalltau |
| scikit-learn | >=1.0.0 | LogisticRegression, roc_auc_score |
| numpy | >=1.21.0 | Array operations, bootstrap |
| pandas | >=1.3.0 | Panel dataframes |
| matplotlib | >=3.4.0 | Figures |
| seaborn | >=0.11.0 | Figures |
| constat | GitHub | eth-sri/ConStat NLP S_index |

**ConStat install:** `pip install -e . && pip install -r requirements.txt` (from cloned eth-sri/ConStat repo)

---

*Generated by Phase 3 Architecture Agent*
*Hypothesis: H-E1 EXISTENCE PoC | Tier: LIGHT | Domains: CV + NLP + Tabular*
