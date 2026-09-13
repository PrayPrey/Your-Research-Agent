---
title: "Config: H-M1 - Base Calibration Verification"
hypothesis_id: h-m1
hypothesis_type: MECHANISM
phase: Phase 3
tier: FULL
date: 2026-03-15
---

Applied: custom pattern — no relevant KB results (diffusion-focused KB, similarity < 0.35)

# Config: H-M1 — Base Calibration Verification

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from base code (Read tool used on h-e1/code/ directly)
**Config Files Found**: `h-e1/code/calibration_analysis.py` — CALIBRATION_CONFIG, EVAL_CONFIG, GATE_CONFIG, REPORT_CONFIG, BASE_MODEL_IDS, MODEL_REGISTRY, MODELS (all module-level dicts, no separate config.py)
**Pattern Used**: hardcoded dict (consistent with h-e1)

---

## Inherited Configuration (Base Hypothesis)

### Config Constants (From Actual h-e1/code/calibration_analysis.py)

```python
# Verified field names and values from actual h-e1/code/calibration_analysis.py

CALIBRATION_CONFIG = {
    "n_bins": 15,                                    # verified
    "n_bootstrap": 1000,                             # verified
    "seed": 42,                                      # verified
    "results_dir": "./results",                      # verified
    "calibration_results_file": "calibration_results.json",  # verified
}

EVAL_CONFIG = {
    "batch_size": 8,                                 # verified
    "batch_size_fallback": 4,                        # verified
    "num_fewshot": 0,                                # verified
    "task": "mmlu",                                  # verified
    "dtype": "float16",                              # verified
    "output_base": "./results",                      # verified
}

# Base model IDs (verified from actual code — separate dict BASE_MODEL_IDS exists)
BASE_MODEL_IDS = {
    "1.4b": "EleutherAI/pythia-1.4b",
    "2.8b": "EleutherAI/pythia-2.8b",
    "6.9b": "EleutherAI/pythia-6.9b",
}

# Model key format verified from actual MODELS list: "pythia-{size}-{condition}"
MODELS = [
    "pythia-1.4b-base", "pythia-1.4b-sft", "pythia-1.4b-dpo", "pythia-1.4b-ppo",
    "pythia-2.8b-base", "pythia-2.8b-sft", "pythia-2.8b-dpo", "pythia-2.8b-ppo",
    "pythia-6.9b-base", "pythia-6.9b-sft", "pythia-6.9b-dpo", "pythia-6.9b-ppo",
]
```

**Import pattern (verified from actual code):**
```python
import sys
sys.path.append("../../h-e1/code/")
from calibration_analysis import (
    compute_ece,
    compute_brier_decomposition,
    load_lmeval_samples,
    CALIBRATION_CONFIG,
    EVAL_CONFIG,
    BASE_MODEL_IDS,
    MODELS,
)
```

**Verified from**: `h-e1/code/calibration_analysis.py` (actual implementation, lines 22-100)

---

## H-M1 Full Configuration (YAML Schema)

```yaml
hypothesis_id: h-m1
hypothesis_type: MECHANISM

gate:
  threshold: 0.15
  gate_type: MUST_WORK
  logic: ALL   # all 3 sizes must satisfy ECE_base < 0.15

base_sizes:
  - "1.4b"
  - "2.8b"
  - "6.9b"

base_model_hf_ids:
  "1.4b": "EleutherAI/pythia-1.4b"
  "2.8b": "EleutherAI/pythia-2.8b"
  "6.9b": "EleutherAI/pythia-6.9b"

calibration:
  n_bins: 15
  seed: 42

lmeval:
  num_fewshot: 0
  batch_size: 8
  dtype: "float16"
  device: "cuda:0"
  task: "mmlu"

paths:
  h_e1_validation: "../../h-e1/04_validation.md"
  h_e1_results_dir: "../../h-e1/results"
  h_m1_results_dir: "./results"
  h_m1_figures_dir: "./figures"
  h_m1_report: "../../04_validation.md"
  verification_state: "../../verification_state.yaml"

figures:
  figure_01: "figures/figure_01_ece_gate.png"
  figure_02: "figures/figure_02_base_vs_aligned_ece.png"
  figure_03: "figures/figure_03_calibration_curves.png"
  figure_04: "figures/figure_04_ece_by_subject.png"
  figure_05: "figures/figure_05_brier_decomposition.png"
```

---

## Python Config (h-m1/code/config.py — hardcoded dicts)

```python
# ── Paths ─────────────────────────────────────────────────────────────────────
H_E1_VALIDATION_PATH = "../../h-e1/04_validation.md"
H_E1_RESULTS_DIR     = "../../h-e1/results"
H_M1_RESULTS_DIR     = "./results"
H_M1_FIGURES_DIR     = "./figures"
H_M1_REPORT_PATH     = "../../04_validation.md"
VERIFICATION_STATE   = "../../verification_state.yaml"

# ── Gate ──────────────────────────────────────────────────────────────────────
GATE_THRESHOLD = 0.15
BASE_SIZES = ["1.4b", "2.8b", "6.9b"]

# ── Calibration (inherited values from h-e1/code/calibration_analysis.py) ────
N_BINS = 15
SEED   = 42

# ── Base model HF IDs ────────────────────────────────────────────────────────
BASE_MODEL_HF_IDS = {
    "1.4b": "EleutherAI/pythia-1.4b",
    "2.8b": "EleutherAI/pythia-2.8b",
    "6.9b": "EleutherAI/pythia-6.9b",
}

# ── lm-eval settings (Path B fallback only) ───────────────────────────────────
LMEVAL_CONFIG = {
    "num_fewshot": 0,
    "batch_size": 8,
    "dtype": "float16",
    "device": "cuda:0",
    "task": "mmlu",
}

# ── Figure settings ───────────────────────────────────────────────────────────
FIGURE_CONFIG = {
    "dpi": 150,
    "figsize_single": (7, 5),
    "figsize_triple": (15, 5),
    "figsize_bar_wide": (10, 6),
    "color_pass": "green",     # ECE_base < 0.15
    "color_fail": "red",       # ECE_base >= 0.15
    "gate_line_style": "--",
    "gate_line_color": "black",
    "gate_line_alpha": 0.7,
    "n_mmlu_subjects": 57,
    # Alignment condition colors (consistent with h-e1)
    "colors": {
        "base": "#9E9E9E",
        "sft":  "#2196F3",
        "dpo":  "#FF9800",
        "ppo":  "#F44336",
    },
}

# ── Validation report config ──────────────────────────────────────────────────
REPORT_CONFIG = {
    "output_path": "../../04_validation.md",
    "gate_result_path": "./results/gate_result.json",
    "sections": [
        "metadata",
        "gate_result",
        "ece_table",
        "calibration_ordering",
        "figure_paths",
        "key_findings",
        "execution_path",
    ],
    "min_key_findings": 3,
}

# ── verification_state.yaml write config ──────────────────────────────────────
VERIFICATION_STATE_CONFIG = {
    "state_file": "../../verification_state.yaml",
    "hypothesis_id": "h-m1",
    "gate_key": "gate_result",     # "PASS" | "FAIL"
    "ece_key": "ece_base_values",  # dict: {"1.4b": float, "2.8b": float, "6.9b": float}
    "gate_type": "MUST_WORK",
}
```

---

## M1-5: Figure Generation [Complexity: 13, Budget: 2 subtasks]

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Figure 1 (Gate Bar — Mandatory) | `plot_ece_gate_bar()`: bar chart ECE_base × 3 sizes (1.4B/2.8B/6.9B), dashed line at 0.15, green bar if ECE < 0.15 else red, saves `figure_01_ece_gate.png` |
| C-5-2 | Figures 2-5 (Recommended) | `plot_base_vs_aligned_ece()` (3 sizes × 4 conditions grouped bar), `plot_calibration_reliability_diagrams()` (3-panel per size), `plot_ece_by_subject()` (box plot 57 subjects × 3 models), `plot_brier_decomposition_base()` (stacked bar REL/RES/UNC for 3 base models) |

---

## M1-6: Validation Report [Complexity: 9, Budget: 2 subtasks]

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | generate_validation_report() | Write `h-m1/04_validation.md` using REPORT_CONFIG sections: metadata (h-m1, MECHANISM, date), gate result (PASS/FAIL), ECE table (3 sizes), calibration ordering (ECE_base < ECE_SFT check), figure paths, key findings (>=3), execution path (A/A-extended/B) |
| C-6-2 | update_verification_state() | Read `verification_state.yaml`, write gate_result and ece_base_values for h-m1 key using pyyaml read-modify-write; preserve all other hypothesis entries |

---

*Generated: Phase 3 Config Agent*
*Hypothesis: H-M1 (MECHANISM, FULL tier) | Base: H-E1*
