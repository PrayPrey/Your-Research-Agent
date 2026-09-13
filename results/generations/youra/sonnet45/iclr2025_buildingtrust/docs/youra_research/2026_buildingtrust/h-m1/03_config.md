# Configuration: H-M1 — Logit Delta Anisotropy Analysis

**Hypothesis ID:** H-M1
**Type:** MECHANISM (INCREMENTAL — extends H-E1)
**Date:** 2026-03-17

Applied: hardcoded-dict pattern (consistent with H-E1 config.py style)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from h-e1/code/config.py (actual implementation read)
**Config Files Found**: `h-e1/code/config.py`
**Pattern Used**: hardcoded dict (matching H-E1 style — no dataclass in base)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

Verified from `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_buildingtrust/docs/youra_research/20260317_buildingtrust/h-e1/code/config.py`:

```python
# H-E1 actual field names and defaults (verified)
SEED        = 42           # H-M1 changes to 1 (controlled comparison)
TORCH_DTYPE = "float16"    # inherited unchanged
DEVICE_MAP  = "auto"       # inherited unchanged
BATCH_SIZE  = 1            # inherited unchanged

DATASETS = [
    {"name": "mmlu",       "hf_id": "cais/mmlu",       "config": "all",             "split": "test"},
    {"name": "truthfulqa", "hf_id": "truthful_qa",      "config": "multiple_choice", "split": "validation"},
    {"name": "arc",        "hf_id": "allenai/ai2_arc",  "config": "ARC-Challenge",   "split": "test"},
]

VIZ_CONFIG = {
    "figsize":       (10, 6),
    "dpi":           150,
    "n_quintiles":   5,
    "color_palette": "colorblind",
    "save_formats":  ["pdf", "png"],
}
```

**Key delta from H-E1:**
- `SEED`: 42 → 1 (documented controlled change)
- `MODEL_PAIRS`: replaced with 3 new pairs (pair2 DPO, pair4 SFT, pair_new PPO)
- `GATE_THRESHOLDS`: entirely new keys for anisotropy gate
- `RESULTS_DIR` / `OUTPUTS_DIR`: not carried forward (H-M1 uses `experiment_results.json` directly)

---

## H-M1 Complete Configuration

### YAML Schema

```yaml
# H-M1 config schema
seed: 1
torch_dtype: "float16"
device_map: "auto"
batch_size: 1

model_pairs:
  - pair_id: "pair2"
    base: "allenai/tulu-2-7b"
    aligned: "allenai/tulu-2-dpo-7b"
    method: "DPO"
  - pair_id: "pair4"
    base: "EleutherAI/pythia-6.9b"
    aligned: "dvruette/oasst-pythia-6.9b-4000-steps"
    method: "SFT"
  - pair_id: "pair_new"
    base: "EleutherAI/pythia-1.4b"
    aligned: "pvduy/pythia-1.4b-rl-trlx-dolly15k"
    method: "PPO"

datasets:
  - name: "mmlu"
    hf_id: "cais/mmlu"
    config: "all"
    split: "test"
    n_items: 14042
  - name: "truthfulqa"
    hf_id: "truthful_qa"
    config: "multiple_choice"
    split: "validation"
    n_items: 817
  - name: "arc"
    hf_id: "allenai/ai2_arc"
    config: "ARC-Challenge"
    split: "test"
    n_items: 1172

gate_thresholds:
  anisotropy_ratio_min: 1.0
  pvalue_max: 0.05
  families_min: 2

viz_config:
  figsize: [10, 6]
  dpi: 150
  n_quintiles: 5
  color_palette: "colorblind"
  save_formats: ["pdf", "png"]

paths:
  cache_dir: "h-m1/cache"
  figures_dir: "h-m1/figures"
  results_file: "h-m1/experiment_results.json"
```

---

## Python Configuration (h-m1/code/config.py)

```python
"""Configuration for H-M1: Logit Delta Anisotropy Analysis."""

import os

BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
HYPOTHESIS_DIR = os.path.dirname(BASE_DIR)  # h-m1/

MODEL_PAIRS = [
    {
        "pair_id": "pair2",
        "base":    "allenai/tulu-2-7b",
        "aligned": "allenai/tulu-2-dpo-7b",
        "method":  "DPO",
    },
    {
        "pair_id": "pair4",
        "base":    "EleutherAI/pythia-6.9b",
        "aligned": "dvruette/oasst-pythia-6.9b-4000-steps",
        "method":  "SFT",
    },
    {
        "pair_id": "pair_new",
        "base":    "EleutherAI/pythia-1.4b",
        "aligned": "pvduy/pythia-1.4b-rl-trlx-dolly15k",
        "method":  "PPO",
    },
]

DATASETS = [
    {"name": "mmlu",       "hf_id": "cais/mmlu",       "config": "all",             "split": "test"},
    {"name": "truthfulqa", "hf_id": "truthful_qa",      "config": "multiple_choice", "split": "validation"},
    {"name": "arc",        "hf_id": "allenai/ai2_arc",  "config": "ARC-Challenge",   "split": "test"},
]

CACHE_DIR   = os.path.join(HYPOTHESIS_DIR, "cache")
FIGURES_DIR = os.path.join(HYPOTHESIS_DIR, "figures")
SEED        = 1          # Non-standard: changed from H-E1's 42 for controlled comparison

TORCH_DTYPE = "float16"
DEVICE_MAP  = "auto"
BATCH_SIZE  = 1

GATE_THRESHOLDS = {
    "anisotropy_ratio_min": 1.0,   # r = λ₁ / mean(λ₂,λ₃,λ₄) must exceed this
    "pvalue_max":           0.05,  # paired t-test significance threshold
    "families_min":         2,     # minimum families passing both criteria
}

VIZ_CONFIG = {
    "figsize":       (10, 6),
    "dpi":           150,
    "n_quintiles":   5,
    "color_palette": "colorblind",
    "save_formats":  ["pdf", "png"],
}
```

---

## A-9: Visualizations Figs 1-3 [Complexity: 11, Budget: 2]

**Applied**: Standard matplotlib pattern (H-E1 VIZ_CONFIG inherited)

### Configuration

```python
# A-9 viz parameters — drawn from VIZ_CONFIG
FIG1_CONFIG = {
    "figsize":          (10, 6),
    "dpi":              150,
    "threshold_line":   1.0,       # GATE_THRESHOLDS["anisotropy_ratio_min"]
    "bar_color":        "steelblue",
    "threshold_color":  "red",
    "save_name":        "fig1_anisotropy_gate_metrics",
}

FIG2_CONFIG = {
    "figsize":   (12, 5),          # Non-standard: wider to show 4 eigenvalues × 3 pairs
    "dpi":       150,
    "save_name": "fig2_eigenvalue_spectrum",
}

FIG3_CONFIG = {
    "figsize":      (8, 7),        # Non-standard: square for 2D PCA scatter
    "dpi":          150,
    "n_quintiles":  5,             # VIZ_CONFIG["n_quintiles"]
    "cmap":         "viridis",
    "save_name":    "fig3_delta_pca",
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | Fig1 Gate Bar Chart | `plot_anisotropy_gate_metrics`: bar chart per pair, red threshold line at r=1.0 |
| C-9-2 | Fig2+3 Spectrum+PCA | `plot_eigenvalue_spectrum` (4 eigenvalues per pair) + `plot_delta_pca` (2D PCA colored by quintile) |

---

## A-10: Visualizations Figs 4-5 [Complexity: 9, Budget: 2]

**Applied**: Standard matplotlib/seaborn pattern

### Configuration

```python
# A-10 viz parameters
FIG4_CONFIG = {
    "figsize":      (8, 5),
    "dpi":          150,
    "n_quintiles":  5,             # VIZ_CONFIG["n_quintiles"]
    "marker":       "o",
    "save_name":    "fig4_anisotropy_by_quintile",
}

FIG5_CONFIG = {
    "figsize":   (10, 6),
    "dpi":       150,
    "methods":   ["DPO", "SFT", "PPO"],
    "axes":      ["decision", "orthogonal_1", "orthogonal_2", "orthogonal_3"],
    "save_name": "fig5_method_comparison",
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-10-1 | Fig4 Quintile Line Chart | `plot_anisotropy_by_quintile`: r vs margin quintile per pair, bridge to H-M2 |
| C-10-2 | Fig5 Method Box Plots | `plot_method_comparison`: box plots Δ variance decision vs orthogonal axes, DPO/SFT/PPO |

---

## Hyperparameter Defaults Summary

| Parameter | Value | Source |
|-----------|-------|--------|
| SEED | 1 | Changed from H-E1 (42) — controlled comparison |
| TORCH_DTYPE | "float16" | Inherited H-E1 |
| DEVICE_MAP | "auto" | Inherited H-E1 |
| BATCH_SIZE | 1 | Sequential model loading constraint |
| anisotropy_ratio_min | 1.0 | Gate: isotropic null = r≈1.0 |
| pvalue_max | 0.05 | Standard significance threshold |
| families_min | 2 | Gate: ≥2/3 families must pass |
| n_quintiles | 5 | Inherited H-E1 VIZ_CONFIG |
| dpi | 150 | Inherited H-E1 VIZ_CONFIG |
| figsize | (10, 6) | Inherited H-E1 VIZ_CONFIG |

---

*Generated by Phase 3 Config Agent — H-M1 MECHANISM hypothesis*
