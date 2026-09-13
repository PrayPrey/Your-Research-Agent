# Configuration Document: H-M4

**Date:** 2026-08-26
**Author:** yoon303@ust.ac.kr
**Hypothesis:** H-M4 — Cross-dataset OLS Replication (Gao et al. 2023)
**Phase:** 3 — Implementation Planning

---

## 1. Configuration Overview

H-M4 has minimal configuration — it is a statistical pipeline with fixed methodology. All hyperparameters mirror H-M3 exactly (required for methodological consistency in cross-dataset comparison). Only path configurations change.

---

## 2. `config.py` — Full Contents

```python
# config.py — H-M4 Configuration
# All paths relative to repo root (docs/youra_research/h-m4/)
from pathlib import Path

# --- Directory structure ---
BASE = Path("docs/youra_research/h-m4")
DATA_DIR = BASE / "data"
CODE_DIR = BASE / "code"
FIGURES_DIR = BASE / "figures"
RESULTS_DIR = BASE / "results"

# --- File paths ---
DATA_RAW = DATA_DIR / "gao_2023_raw.csv"       # WebPlotDigitizer output
DATA_GAP = DATA_DIR / "gao_2023_gap.csv"       # After normalization
RESULTS_JSON = RESULTS_DIR / "h_m4_results.json"
RESULTS_CSV = RESULTS_DIR / "gao_2023_gap_final.csv"

# H-M3 data path (for cross-dataset overlay figure)
DATA_COSTE = Path("docs/youra_research/h-m2/results/h_m2_normalized_gap.csv")

# --- Statistical parameters (MUST match H-M3 for methodological consistency) ---
N_BOOT = 10_000          # Bootstrap resamples
SEED = 42                # Random seed (bootstrap)
ALPHA = 0.05             # Significance level

# --- Gate thresholds (SHOULD_WORK) ---
GATE_BETA_MIN = 0.0      # β must be > this
GATE_P_MAX = 0.05        # p must be < this

# --- H-M3 reference values (for cross-dataset comparison) ---
BETA_COSTE = 0.1433      # H-M3 validated slope
P_COSTE = 8.89e-7        # H-M3 p-value
R2_COSTE = 0.9577        # H-M3 R²
N_COSTE = 10             # H-M3 sample size

# --- Data constraints ---
MIN_N = 6                # Minimum KL checkpoints for valid regression
GAP_STD_MIN = 0.01       # Minimum gap std to detect normalization failure
DIGITIZATION_PRECISION = 0.03   # Target ±3% per point

# --- Gao et al. source ---
GAO_PAPER = "Gao et al. 2023, arXiv 2210.10760 Figure 1"
GAO_RM_SIZE_PRIMARY = "6B"
GAO_RM_SIZE_FALLBACK = "mean of 302M-3B"
GAO_KL_RANGE = (0.0, 8.0)      # Approximate x-axis range in Figure 1

# --- Figure settings ---
FIGURE_DPI = 150
FIGURE_FORMAT = "png"
FIGURES = {
    "fig1": "fig1_gate_metrics.png",
    "fig2": "fig2_regression_gao.png",
    "fig3": "fig3_cross_dataset_slopes.png",
    "fig4": "fig4_dual_overlay.png",
    "fig5": "fig5_bootstrap_histogram.png",
}
```

---

## 3. Parameter Rationale

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| N_BOOT | 10,000 | Matches H-M3 exactly — required for methodological consistency |
| SEED | 42 | Matches H-M3 exactly — reproducibility |
| ALPHA | 0.05 | Standard significance level; matches H-M3 |
| GATE_BETA_MIN | 0.0 | Gate condition: β > 0 |
| GATE_P_MAX | 0.05 | Gate condition: p < 0.05 |
| BETA_COSTE | 0.1433 | H-M3 validated result; used in compare_with_coste() |
| MIN_N | 6 | Minimum valid OLS with 2 parameters (slope + intercept) requires df ≥ 4; 6 is conservative floor |
| GAP_STD_MIN | 0.01 | Detects degenerate normalization (proxy = gold throughout) |
| DIGITIZATION_PRECISION | 0.03 | WebPlotDigitizer achievable precision for clean Gao et al. figure |
| FIGURE_DPI | 150 | Sufficient for paper-quality PNG figures |

---

## 4. Environment Configuration

### Conda Environment

Reuse `youra-h-m3` environment directly, or clone:

```bash
# Option A: reuse existing
conda activate youra-h-m3

# Option B: clone
conda create --name youra-h-m4 --clone youra-h-m3
conda activate youra-h-m4

# Option C: create fresh (if h-m3 env unavailable)
conda create -n youra-h-m4 python=3.10 -y
conda activate youra-h-m4
pip install scipy>=1.10 statsmodels>=0.14 numpy>=1.24 matplotlib>=3.7 pandas>=2.0
```

### Working Directory

Run all code from repo root:
```bash
cd /home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_bi_align
python docs/youra_research/h-m4/code/main.py
```

---

## 5. Pre-run Checklist

```
[ ] WebPlotDigitizer digitization complete → gao_2023_raw.csv exists
[ ] conda env active (youra-h-m3 or youra-h-m4)
[ ] Working directory = repo root
[ ] docs/youra_research/h-m4/data/ directory exists
[ ] docs/youra_research/h-m4/figures/ directory exists
[ ] docs/youra_research/h-m4/results/ directory exists
[ ] H-M3 data accessible at docs/youra_research/h-m2/results/h_m2_normalized_gap.csv (for dual overlay fig4)
```

---

## 6. Output Configuration

| Output | Path | Format |
|--------|------|--------|
| Processed gap data | data/gao_2023_gap.csv | CSV (4 columns) |
| Results | results/h_m4_results.json | JSON |
| Results copy | results/gao_2023_gap_final.csv | CSV |
| Gate metrics figure | figures/fig1_gate_metrics.png | PNG 150 DPI |
| Regression figure | figures/fig2_regression_gao.png | PNG 150 DPI |
| Cross-dataset comparison | figures/fig3_cross_dataset_slopes.png | PNG 150 DPI |
| Dual overlay | figures/fig4_dual_overlay.png | PNG 150 DPI |
| Bootstrap histogram | figures/fig5_bootstrap_histogram.png | PNG 150 DPI |
| Validation report | 04_validation.md | Markdown |

---

## 7. Results JSON Schema

```json
{
  "hypothesis": "H-M4",
  "dataset": "Gao et al. 2023 arXiv 2210.10760 Figure 1",
  "rm_size": "6B (or fallback: mean 302M-3B)",
  "regression": {
    "slope": 0.0,
    "intercept": 0.0,
    "r_squared": 0.0,
    "p_value": 0.0,
    "std_err": 0.0,
    "t_stat": 0.0,
    "ci_parametric": [0.0, 0.0],
    "ci_bootstrap": [0.0, 0.0],
    "n": 0
  },
  "gate": {
    "gate_pass": false,
    "gate_type": "SHOULD_WORK",
    "reason": ""
  },
  "cross_dataset": {
    "beta_gao": 0.0,
    "beta_coste": 0.1433,
    "ratio": 0.0,
    "within_order_of_magnitude": false
  },
  "mechanism_verified": true,
  "figures_generated": ["fig1_gate_metrics.png", "fig2_regression_gao.png",
                         "fig3_cross_dataset_slopes.png", "fig4_dual_overlay.png",
                         "fig5_bootstrap_histogram.png"],
  "timestamp": "2026-08-26T00:00:00Z"
}
```
