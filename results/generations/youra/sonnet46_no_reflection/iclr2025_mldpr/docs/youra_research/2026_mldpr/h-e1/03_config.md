# Configuration Design: H-E1
# BCBHS: Domain-Specific Health Signal Discriminability

**Date:** 2026-05-19
**Hypothesis:** H-E1 (EXISTENCE, LIGHT tier, MUST_WORK gate)
**Phase:** 3 — Configuration Design

Applied: hardcoded-dict-config pattern with argparse CLI overrides (KB search returned diffusion model results only; standard statistical pipeline pattern applied)

---

## Configuration Philosophy

H-E1 is a LIGHT-tier EXISTENCE hypothesis running a pure statistical pipeline (no GPU, no neural networks, no WandB). Per PRD NFR 5.3, no YAML config system is needed. A single hardcoded CONFIG dict in run_experiment.py provides all defaults; argparse overrides allow targeted CLI changes without editing source.

---

## Main Configuration (run_experiment.py)

### CONFIG Dict

```python
CONFIG = {
    # Reproducibility
    "seed": 42,

    # Bootstrap parameters
    "n_bootstrap": 1000,

    # Data filtering
    "min_submissions": 20,
    "min_history_years": 2,

    # Signal computation window
    "lookback_months": 24,

    # Saturation labeling thresholds
    "saturation_tau_threshold": 0.90,   # tau > 0.90 for >= min_consecutive_quarters
    "healthy_tau_threshold": 0.70,      # tau < 0.70 = healthy
    "min_consecutive_quarters": 2,

    # Statistical testing thresholds
    "significance_level": 0.05,
    "cohens_d_threshold": 0.5,
    "auc_threshold": 0.70,

    # Sample size requirements
    "min_saturated_per_domain": 15,
    "min_healthy_per_domain": 15,
    "min_benchmarks_per_domain": 10,    # for mechanism activation check

    # Output paths
    "output_dir": "h-e1/figures/",
    "results_csv": "h-e1/results.csv",

    # Visualization (C-A5-1)
    "figure_dpi": 150,
    "figure_size": (10, 6),
    "domain_colors": {
        "cv":      "#2196F3",   # blue
        "nlp":     "#FF5722",   # orange-red
        "tabular": "#4CAF50",   # green
    },
    "threshold_line_styles": {
        "significance": {"color": "#F44336", "linestyle": "--", "label": "p=0.05"},
        "cohens_d":     {"color": "#FF9800", "linestyle": "--", "label": "d=0.5"},
        "auc":          {"color": "#4CAF50", "linestyle": "--", "label": "AUC=0.70"},
    },
}
```

### argparse Definitions

```python
import argparse

def parse_args(config: dict) -> dict:
    parser = argparse.ArgumentParser(description="H-E1: Domain Health Signal Discriminability")
    parser.add_argument("--seed",            type=int,   default=config["seed"])
    parser.add_argument("--n-bootstrap",     type=int,   default=config["n_bootstrap"])
    parser.add_argument("--lookback-months", type=int,   default=config["lookback_months"])
    parser.add_argument("--output-dir",      type=str,   default=config["output_dir"])
    parser.add_argument("--results-csv",     type=str,   default=config["results_csv"])
    args = parser.parse_args()

    config["seed"]            = args.seed
    config["n_bootstrap"]     = args.n_bootstrap
    config["lookback_months"] = args.lookback_months
    config["output_dir"]      = args.output_dir
    config["results_csv"]     = args.results_csv
    return config
```

---

## Environment Setup

### requirements.txt

```
datasets>=2.0.0
openml>=0.14.0
scipy>=1.9.0
scikit-learn>=1.0.0
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
```

### ConStat Installation

```bash
git clone https://github.com/eth-sri/ConStat.git
cd ConStat
pip install -e .
pip install -r requirements.txt
cd ..
```

Run after installing the requirements above. ConStat is used for contamination-adjusted S_index computation in the NLP domain signal.

---

## Output Path Configuration

```
h-e1/
  figures/
    gate_metrics.png
    boxplots.png
    roc_curves.png
    temporal_separation.png
    scatter.png
  results.csv
```

Create directories before writing:

```python
import os
os.makedirs(config["output_dir"], exist_ok=True)
os.makedirs(os.path.dirname(config["results_csv"]), exist_ok=True)
```

---

## Subtask: C-A5-1 — Visualization Configuration

**Parent Epic**: A-5 (Visualization, complexity 9)

### Figure Sizes per Plot

| Plot file            | figure_size  | DPI | Notes                            |
|----------------------|--------------|-----|----------------------------------|
| gate_metrics.png     | (12, 5)      | 150 | 3 subplots side-by-side (p, d, AUC) |
| boxplots.png         | (10, 6)      | 150 | 3 domains x 2 groups             |
| roc_curves.png       | (8, 6)       | 150 | 1 curve per domain               |
| temporal_separation.png | (12, 5)   | 150 | time-series, 3 domain panels     |
| scatter.png          | (8, 7)       | 150 | signal vs. saturation label      |

### Color Scheme

```python
DOMAIN_COLORS = {
    "cv":      "#2196F3",   # Material Blue
    "nlp":     "#FF5722",   # Material Deep Orange
    "tabular": "#4CAF50",   # Material Green
}
```

### Threshold Lines (gate_metrics figure)

```python
THRESHOLD_LINES = {
    "p_value":  {"y": 0.05, "color": "#F44336", "linestyle": "--", "label": "p=0.05"},
    "cohens_d": {"y": 0.50, "color": "#FF9800", "linestyle": "--", "label": "d=0.5"},
    "auc":      {"y": 0.70, "color": "#4CAF50", "linestyle": "--", "label": "AUC=0.70"},
}
```

### Output Filenames

```python
FIGURE_PATHS = {
    "gate_metrics":       "h-e1/figures/gate_metrics.png",
    "boxplots":           "h-e1/figures/boxplots.png",
    "roc_curves":         "h-e1/figures/roc_curves.png",
    "temporal_separation":"h-e1/figures/temporal_separation.png",
    "scatter":            "h-e1/figures/scatter.png",
}
```

---

## Subtask Summary

| ID     | Title                      | Parent Epic | Complexity |
|--------|----------------------------|-------------|------------|
| C-A5-1 | Visualization Configuration | A-5 (9)    | Medium     |
