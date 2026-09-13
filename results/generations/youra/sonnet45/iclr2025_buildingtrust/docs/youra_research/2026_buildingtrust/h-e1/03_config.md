# Configuration: H-E1 — Confidence Margin Predicts Argmax Flip (EXISTENCE PoC)

**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Date:** 2026-03-17

Applied: Standard PyTorch/HuggingFace inference defaults (Archon KB domain mismatch — similarity < 0.44)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (Serena skipped, no existing codebase)
**Config Files Found**: None - new config
**Pattern Used**: hardcoded dict (EXISTENCE PoC preference)

---

## Full Pipeline Config (`h-e1/code/config.py`)

```python
MODEL_PAIRS: list[dict] = [
    {"pair_id": "pair1", "base": "allenai/tulu-2-7b",      "aligned": "allenai/tulu-2-ppo-7b",  "method": "PPO"},
    {"pair_id": "pair2", "base": "allenai/tulu-2-7b",      "aligned": "allenai/tulu-2-dpo-7b",  "method": "DPO"},
    {"pair_id": "pair3", "base": "EleutherAI/pythia-1.4b", "aligned": "allenai/pythia-1.4b-ppo", "method": "PPO"},
    {"pair_id": "pair4", "base": "EleutherAI/pythia-6.9b", "aligned": "allenai/pythia-6.9b-ppo", "method": "PPO"},
]

DATASETS: list[dict] = [
    {"name": "mmlu",       "hf_id": "cais/mmlu",        "config": "all",             "split": "test"},
    {"name": "truthfulqa", "hf_id": "truthful_qa",       "config": "multiple_choice", "split": "validation"},
    {"name": "arc",        "hf_id": "allenai/ai2_arc",   "config": "ARC-Challenge",   "split": "test"},
]

CACHE_DIR: str   = "h-e1/cache"
FIGURES_DIR: str = "h-e1/figures"
RESULTS_DIR: str = "h-e1/results"
SEED: int        = 42

TORCH_DTYPE: str = "float16"
DEVICE_MAP: str  = "auto"
BATCH_SIZE: int  = 1

GATE_THRESHOLDS: dict = {
    "beta1_max":         0.0,
    "pvalue_max":        0.005,
    "auroc_min":         0.75,
    "partial_eta2_min":  0.06,
}

VIZ_CONFIG: dict = {
    "figsize":       (10, 6),
    "dpi":           150,
    "n_quintiles":   5,
    "color_palette": "colorblind",
    "save_formats":  ["pdf", "png"],
}
```

---

## A-4: Visualization [Complexity: 9, Budget: 2]

**Applied**: Standard PyTorch/HuggingFace inference defaults

### Configuration

```python
VIZ_CONFIG: dict = {
    "figsize":       (10, 6),
    "dpi":           150,          # Non-standard: 150 for print-quality PDF without excessive file size
    "n_quintiles":   5,
    "color_palette": "colorblind",  # Non-standard: accessibility-safe palette for publication figures
    "save_formats":  ["pdf", "png"],
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Plot functions | Implement plot_gate_metrics, plot_quintile_flip_rates, plot_roc_curves, plot_margin_distribution using VIZ_CONFIG |
| C-4-2 | Save all figures | Implement save_all_figures: iterate plots, call savefig for each format in save_formats |

---

## Self-Validation

- [x] ONE format only (hardcoded dict)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values (dpi, color_palette)
- [x] Subtask count within budget (2/2)
- [x] Total length < 400 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] Green-field: Serena skip noted in Codebase Analysis
