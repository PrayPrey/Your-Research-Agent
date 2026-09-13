# H-M1 Configuration

**Applied**: standard-dict-config (H-E1 hardcoded dict pattern, adapted for statistical pipeline)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extending H-E1)
**Status**: Config classes verified from H-E1 actual code
**Config Files Found**: `h-e1/code/run_experiment.py` (CONFIG dict), `h-e1/code/data_pipeline.py` (DOMAIN_MAP, CC18_TASK_IDS)
**Pattern Used**: Hardcoded dict (consistent with H-E1 style — no dataclass used in H-E1)

---

## Inherited Configuration (Base Hypothesis)

### Config Fields (From Actual H-E1 Code: `h-e1/code/run_experiment.py`)

```python
# Verified from h-e1/code/run_experiment.py — actual CONFIG dict
# Fields reused in H-M1 (identical values unless noted):
{
    "seed": 42,
    "min_submissions": 20,          # ← same filter criterion as H-E1 data_pipeline.py line 118
    "min_history_years": 2,         # ← same as H-E1 (730 days in data_pipeline.py line 124)
    "min_consecutive_quarters": 2,  # ← same as H-E1 saturation logic (data_pipeline.py line 266)
    "significance_level": 0.05,
    "output_dir": "h-e1/figures/",  # ← updated to h-m1/ for H-M1
    "results_json": "h-e1/results.json",  # ← updated for H-M1
    "results_csv": "h-e1/results.csv",    # ← updated for H-M1
    "figure_dpi": 150,
    "figure_size": (10, 6),
    "domain_colors": {
        "cv": "#2196F3",
        "nlp": "#FF5722",
        "tabular": "#4CAF50",
    },
    "domains": ["cv", "nlp", "tabular"],
}
# Fields NOT reused (H-E1 specific):
#   n_bootstrap, saturation_tau_threshold, healthy_tau_threshold,
#   cohens_d_threshold, auc_threshold, min_saturated_per_domain,
#   min_healthy_per_domain, min_benchmarks_per_domain,
#   temporal_lookbacks, threshold_line_styles
```

**Verified from**: `h-e1/code/run_experiment.py` (actual implementation, lines 10–42)

---

## H-M1 Configuration

### CONFIG Dict (Python — copy-paste ready)

```python
CONFIG = {
    # --- Reproducibility ---
    "seed": 42,

    # --- Data loading (inherited from H-E1, verified from data_pipeline.py) ---
    "min_submissions": 20,          # benchmarks with <20 total submissions excluded
    "min_history_years": 2,         # benchmarks with <2yr date range excluded (730 days)
    "min_quarters": 8,              # minimum quarterly time points for Granger test
    "date_start": "2018-01-01",
    "date_end": "2025-12-31",
    "domains": ["cv", "nlp", "tabular"],

    # --- Compression detection ---
    "compression_threshold": 1.5,   # score_var_top10 < 1.5 * sigma_measurement → compressed
    "min_consecutive": 2,           # consecutive compressed quarters to flag compression event
    "top_k_scores": 10,             # top-k model scores for variance computation

    # --- Granger causality ---
    "granger_max_lag": 4,           # max lag (quarters); primary test at lag=2
    "granger_primary_lag": 2,       # primary reporting lag (2-quarter causal delay)
    "adf_significance": 0.05,       # ADF p-threshold; apply first-difference if p >= this

    # --- Gate criteria ---
    "spearman_rho_target": 0.4,     # Spearman rho must exceed this for PASS
    "granger_p_target": 0.05,       # Granger F-test p-value must be below this for PASS
    "significance_level": 0.05,     # general alpha (inherited from H-E1)

    # --- Panel size requirements ---
    "min_panel_rows": 200,          # minimum (benchmark x quarter) observations
    "min_granger_benchmarks": 30,   # minimum benchmarks with valid Granger test

    # --- Output paths ---
    "output_dir": "h-m1/figures/",
    "results_json": "h-m1/results.json",
    "results_csv": "h-m1/results.csv",

    # --- Visualization (inherited from H-E1) ---
    "figure_dpi": 150,
    "figure_size": (10, 6),
    "domain_colors": {
        "cv": "#2196F3",
        "nlp": "#FF5722",
        "tabular": "#4CAF50",
    },
}
```

---

## YAML Schema / Example Config

```yaml
# h-m1/config.yaml — override any CONFIG defaults at runtime
seed: 42

# Data loading
min_submissions: 20
min_history_years: 2
min_quarters: 8
date_start: "2018-01-01"
date_end: "2025-12-31"
domains:
  - cv
  - nlp
  - tabular

# Compression detection
compression_threshold: 1.5
min_consecutive: 2
top_k_scores: 10

# Granger causality
granger_max_lag: 4
granger_primary_lag: 2
adf_significance: 0.05

# Gate criteria
spearman_rho_target: 0.4
granger_p_target: 0.05
significance_level: 0.05

# Panel requirements
min_panel_rows: 200
min_granger_benchmarks: 30

# Output
output_dir: "h-m1/figures/"
results_json: "h-m1/results.json"
results_csv: "h-m1/results.csv"
figure_dpi: 150
figure_size: [10, 6]
```

---

## Argparse Integration

```python
# run_experiment.py — H-M1 entry point (mirrors H-E1 parse_args pattern)
import argparse

CONFIG = { ... }  # dict above

def parse_args(config: dict, args=None) -> dict:
    parser = argparse.ArgumentParser(
        description="H-M1: BCBHS Causal Mechanism — Submission Count → Score Compression"
    )
    parser.add_argument("--seed", type=int, default=config["seed"])
    parser.add_argument("--min-submissions", type=int, default=config["min_submissions"],
                        dest="min_submissions")
    parser.add_argument("--min-quarters", type=int, default=config["min_quarters"],
                        dest="min_quarters")
    parser.add_argument("--compression-threshold", type=float,
                        default=config["compression_threshold"],
                        dest="compression_threshold")
    parser.add_argument("--granger-max-lag", type=int, default=config["granger_max_lag"],
                        dest="granger_max_lag")
    parser.add_argument("--output-dir", type=str, default=config["output_dir"],
                        dest="output_dir")
    parser.add_argument("--results-csv", type=str, default=config["results_csv"],
                        dest="results_csv")
    parsed = parser.parse_args(args)
    config.update(vars(parsed))
    return config


def main(args=None):
    config = dict(CONFIG)
    config = parse_args(config, args)
    import numpy as np
    np.random.seed(config["seed"])
    # ... rest of experiment
```

---

## Hyperparameter Sensitivity

| Parameter | Value | Sensitivity | Rationale |
|-----------|-------|-------------|-----------|
| `compression_threshold` | 1.5 | HIGH | Directly controls how many compression events are flagged; shifts Spearman rho |
| `granger_primary_lag` | 2 | HIGH | Gate criterion measured at this lag; wrong lag → missed causality |
| `min_consecutive` | 2 | MEDIUM | Filters noise; too high reduces compression event count below power threshold |
| `min_quarters` | 8 | MEDIUM | Determines benchmark eligibility; lower → more benchmarks but noisier Granger |
| `granger_max_lag` | 4 | LOW | Controls search range; primary test at lag=2 is unaffected |
| `min_submissions` | 20 | LOW | Inherited from H-E1; already validated as appropriate filter |
| `adf_significance` | 0.05 | LOW | Standard threshold; affects only pre-processing differencing step |
| `seed` | 42 | NONE | Pure statistical pipeline; no stochastic training |

---

## Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-M1-1 | Data config | `min_submissions`, `min_quarters`, `date_start/end` for panel construction |
| C-M1-2 | Compression config | `compression_threshold`, `min_consecutive`, `top_k_scores` for compression detection |
| C-M1-3 | Granger config | `granger_max_lag`, `granger_primary_lag`, `adf_significance` for causality tests |
| C-M1-4 | Gate config | `spearman_rho_target`, `granger_p_target`, `min_panel_rows`, `min_granger_benchmarks` |
| C-M1-5 | Output + argparse | `output_dir`, `results_json`, `results_csv`, argparse integration |
