# Config: H-M2
## DPO vs PPO/SFT Logit Delta Variance in Low-Margin Regions

**Hypothesis ID:** H-M2
**Type:** MECHANISM (INCREMENTAL — extends H-M1)
**Date:** 2026-03-17

Applied: No applicable KB patterns (domain mismatch). Standard statistical analysis defaults used.

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from actual code via direct file read (Serena project activation failed — no active project error)
**Config Files Found**: `h-m1/code/config.py` (flat module, constants + dicts — no dataclass)
**Pattern Used**: hardcoded dict (matches H-M1 pattern)

---

## Inherited Configuration (Base Hypothesis)

### Config Constants (From Actual h-m1/code/config.py)

```python
# From: h-m1/code/config.py (ACTUAL CODE — field names verified)
SEED = 1                          # ← Verified from actual code
MODEL_PAIRS = [
    {"pair_id": "pair2", "base": "allenai/tulu-2-7b",
     "aligned": "allenai/tulu-2-dpo-7b", "method": "DPO"},
    {"pair_id": "pair4", "base": "EleutherAI/pythia-6.9b",
     "aligned": "dvruette/oasst-pythia-6.9b-4000-steps", "method": "SFT"},
    {"pair_id": "pair_new", "base": "EleutherAI/pythia-1.4b",
     "aligned": "pvduy/pythia-1.4b-rl-trlx-dolly15k", "method": "PPO"},
]
DATASETS = [
    {"name": "mmlu",       "hf_id": "cais/mmlu",      "config": "all",             "split": "test"},
    {"name": "truthfulqa", "hf_id": "truthful_qa",     "config": "multiple_choice", "split": "validation"},
    {"name": "arc",        "hf_id": "allenai/ai2_arc", "config": "ARC-Challenge",   "split": "test"},
]
VIZ_CONFIG = {
    "figsize": (10, 6),
    "dpi": 150,
    "n_quintiles": 5,
    "color_palette": "colorblind",
    "save_formats": ["pdf", "png"],
}
GATE_THRESHOLDS = {
    "anisotropy_ratio_min": 1.0,
    "pvalue_max": 0.05,
    "families_min": 2,
}
```

**Verified from**: `h-m1/code/config.py` (actual implementation — flat constants, no dataclass)

---

## A-9: Visualization Config [Complexity: 14, Budget: 4 subtasks]

**Applied**: Standard matplotlib/seaborn defaults

```python
# config.py — visualization section
VIZ_CONFIG = {
    "figsize": (10, 6),
    "dpi": 150,
    "save_formats": ["pdf", "png"],
    "color_palette": "colorblind",
    "n_quintiles": 5,
}

FIG1_CONFIG = {
    "figsize": (10, 6),
    "dpi": 150,
    "bar_colors": {"DPO": "steelblue", "SFT": "darkorange"},
    "save_name": "fig1_q1_variance_bar",
}

FIG2_CONFIG = {
    "figsize": (12, 5),
    "dpi": 150,
    "save_name": "fig2_quintile_trend",
}

FIG3_CONFIG = {
    "figsize": (9, 7),
    "dpi": 150,
    "cmap": "viridis",
    "alpha": 0.6,
    "save_name": "fig3_kl_scatter",
}

FIG4_CONFIG = {
    "figsize": (10, 6),
    "dpi": 150,
    "capsize": 4,
    "save_name": "fig4_benchmark_q1_grouped",
}

FIG5_CONFIG = {
    "figsize": (10, 5),
    "dpi": 150,
    "cmap": "RdBu_r",
    "save_name": "fig5_variance_ratio_heatmap",
}
```

### Subtasks [4/4 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | Fig1+Fig2 config | Bar chart and quintile trend figure configs |
| C-9-2 | Fig3+Fig4 config | KL scatter and grouped bar figure configs |
| C-9-3 | Fig5 config | Heatmap figure config |
| C-9-4 | save_figure defaults | formats, dpi, path pattern |

---

## A-10: Main Entry Point Config [Complexity: 10, Budget: 2 subtasks]

**Applied**: Standard logging + path resolution pattern (matches H-M1)

```python
# config.py — core constants
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
HYPOTHESIS_DIR = os.path.dirname(BASE_DIR)           # h-m2/
HM1_CODE_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "..", "h-m1", "code")
)
HE1_CACHE_DIR = os.path.abspath(
    os.path.join(BASE_DIR, "..", "..", "h-e1", "cache")
)

FIGURES_DIR  = os.path.join(HYPOTHESIS_DIR, "figures")
CACHE_OUT_DIR = os.path.join(HYPOTHESIS_DIR, "cache")
RESULTS_PATH  = os.path.join(HYPOTHESIS_DIR, "experiment_results.json")

SEED         = 1
N_QUINTILES  = 5
MIN_QUINTILE_N = 100       # skip quintile if item count < this
N_BOOTSTRAP  = 5000        # bootstrap iterations for 95% CI

GATE_THRESHOLDS = {
    "pvalue_max":         0.05,
    "variance_ratio_min": 1.0,
    "benchmarks_min":     2,   # must pass on >= 2/3 datasets
}

# H-M2 uses only pair2 (DPO) and pair4 (SFT) — pair_new excluded
MODEL_PAIRS = [
    {"pair_id": "pair2", "method": "DPO",
     "base": "allenai/tulu-2-7b",
     "aligned": "allenai/tulu-2-dpo-7b"},
    {"pair_id": "pair4", "method": "SFT",
     "base": "EleutherAI/pythia-6.9b",
     "aligned": "dvruette/oasst-pythia-6.9b-4000-steps"},
]

DATASETS = [
    {"name": "mmlu",       "n": 14042},
    {"name": "truthfulqa", "n": 817},
    {"name": "arc",        "n": 1172},
]

LOG_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    "log_file": os.path.join(HYPOTHESIS_DIR, "run.log"),
}
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-10-1 | Path + seed constants | BASE_DIR, HYPOTHESIS_DIR, HM1_CODE_DIR, HE1_CACHE_DIR, FIGURES_DIR, CACHE_OUT_DIR, RESULTS_PATH, SEED, N_QUINTILES, MIN_QUINTILE_N, N_BOOTSTRAP |
| C-10-2 | Gate + model/dataset dicts | GATE_THRESHOLDS, MODEL_PAIRS, DATASETS, LOG_CONFIG |

---

## A-11: Test Config [Complexity: 11, Budget: 2 subtasks]

**Applied**: Standard pytest fixture defaults

```python
# tests/test_config.py — test-time constants
import numpy as np

TEST_SEED       = 1
TEST_N_ITEMS    = 500      # synthetic cache size for fast unit tests
TEST_N_QUINTILES = 5
TEST_N_BOOTSTRAP = 100     # reduced for test speed (non-standard: 5000 → 100)
TEST_N_OPTIONS  = 4        # logprob vector width (MMLU-style)

# Synthetic data factory defaults
SYNTHETIC_CACHE = {
    "n":         TEST_N_ITEMS,
    "n_options": TEST_N_OPTIONS,
    "margin_std": 1.0,
    "kl_scale":  0.5,
    "seed":      TEST_SEED,
}

# Tolerance for floating-point assertions
ATOL = 1e-6
```

### Subtasks [2/2 used]
| ID | Subtask | Description |
|----|---------|-------------|
| C-11-1 | Test constants | TEST_SEED, TEST_N_ITEMS, TEST_N_QUINTILES, TEST_N_BOOTSTRAP, TEST_N_OPTIONS, ATOL |
| C-11-2 | Synthetic data config | SYNTHETIC_CACHE factory dict for fixture reuse |

---

## Summary

| Task | Format | Key Constants |
|------|--------|---------------|
| A-9 | Hardcoded dict | VIZ_CONFIG + FIG1..FIG5 configs |
| A-10 | Hardcoded dict | Paths, SEED=1, N_BOOTSTRAP=5000, GATE_THRESHOLDS, MODEL_PAIRS |
| A-11 | Hardcoded dict | TEST_N_BOOTSTRAP=100 (fast), TEST_N_ITEMS=500 |

**Total subtasks used**: 8/8

*Generated by Phase 3 Configuration Agent — H-M2 MECHANISM INCREMENTAL*
*Base config field names verified from h-m1/code/config.py (actual implementation)*
