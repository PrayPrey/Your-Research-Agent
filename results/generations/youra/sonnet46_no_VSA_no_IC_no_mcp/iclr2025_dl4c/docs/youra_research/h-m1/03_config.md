---
title: "Config: H-M1 — SFT Signal Void at Hard Difficulty"
hypothesis_id: H-M1
hypothesis_type: MECHANISM
date: "2026-08-26"
author: yoon303@ust.ac.kr
---

Applied: Flat-script analysis pattern (dataclass per script, no shared config hierarchy)
Applied: Results-file decoupling pattern (each config section maps to one output JSON)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 extends H-E1)
**Status**: H-E1 code not yet materialized — architecture spec used as source of truth
**Config Files Found**: None in `h-e1/code/` (Phase 4 not yet run); field names taken from H-E1 03_prd.md Section 2.3 and 3.2
**Pattern Used**: Python dataclass

---

## Inherited Configuration (Base Hypothesis)

H-E1 SFT training hyperparameters (from H-E1 PRD §3.2, §2.3). H-M1 reuses the checkpoint only; no re-training.

```python
# From: docs/youra_research/h-e1/03_prd.md (verified field names)
# H-E1 SFT training config (reference only — checkpoint already produced)
HE1_SFT_REFERENCE = {
    "model": "deepseek-ai/deepseek-coder-7b-base",
    "checkpoint_out": "checkpoints/sft_baseline/",
    "dtype": "bfloat16",
    "lr": 1e-5,
    "optimizer": "AdamW",
    "effective_batch_size": 32,
    "grad_accum_steps": 8,
    "per_device_batch": 4,
    "epochs": 3,
    "warmup_steps": 100,
    "lr_schedule": "cosine",
    "max_grad_norm": 1.0,
    "seed": 42,
    "max_length": 1024,
    "dataset": "codeparrot/apps",
    "split": "train",
}
```

H-M1 seed is 1 (matching H-M1 NFR-1); H-E1 seed was 42 (training only, not reused here).

---

## H-M1 Runtime Config

```python
from dataclasses import dataclass, field

@dataclass
class HM1Config:
    # --- Checkpoint ---
    sft_checkpoint: str = "checkpoints/sft_baseline/"
    harness_dir: str = "bigcode-evaluation-harness"

    # --- Fallback model (FR-1.2) ---
    fallback_model: str = "deepseek-ai/deepseek-coder-7b-base"

    # --- H-E1 results cache (FR-2.1: check before re-running harness) ---
    he1_results_json: str = "results/h-e1/sft_baseline_livecodebench.json"

    # --- Data ---
    apps_dataset: str = "codeparrot/apps"
    apps_split: str = "train"
    max_examples_per_bucket: int = 500
    max_length: int = 2048

    # --- Evaluation (Task A) ---
    temperature: float = 0.0   # greedy, deterministic
    n_samples: int = 1

    # --- Analysis thresholds ---
    gate_threshold: float = 0.60        # primary gate: pass@1 < 0.60
    coverage_threshold: float = 0.30    # secondary: coverage < 0.30
    coverage_timeout: float = 5.0       # subprocess execution timeout (seconds)

    # --- Output paths ---
    results_dir: str = "results/h-m1"
    figures_dir: str = "docs/youra_research/h-m1/figures"

    # --- Reproducibility ---
    seed: int = 1
    device: str = "cuda"
```

---

## A-M1-6: Figure Generation [Complexity: 9, Budget: 1 subtask]

Applied: Seaborn defaults pattern (theme set once at module level)

```python
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class FigureConfig:
    # Layout
    figsize: tuple = (8, 5)
    figsize_wide: tuple = (10, 5)   # difficulty_gradient uses wider aspect
    dpi: int = 150

    # Style
    style: str = "seaborn-v0_8-whitegrid"
    context: str = "paper"
    font_scale: float = 1.2

    # Color palette — difficulty buckets
    bucket_colors: Dict[str, str] = field(default_factory=lambda: {
        "introductory": "#4C9BE8",   # blue
        "interview":    "#F5A623",   # amber
        "competition":  "#E84C4C",   # red (signal void emphasis)
    })

    # Gate threshold line (60%)
    gate_threshold: float = 0.60
    gate_line_color: str = "#333333"
    gate_line_style: str = "--"
    gate_line_width: float = 1.5
    gate_line_label: str = "Gate (60%)"

    # Output paths (relative to figures_dir)
    gate_metrics_fname: str = "gate_metrics.png"
    difficulty_gradient_fname: str = "difficulty_gradient.png"
    apps_difficulty_loss_fname: str = "apps_difficulty_loss.png"
    apps_coverage_fname: str = "apps_coverage.png"

    # Coverage stacked bar colors
    coverage_colors: Dict[str, str] = field(default_factory=lambda: {
        "solvable":   "#4C9BE8",
        "unsolvable": "#E84C4C",
    })
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-M1-6-1 | Figure config | FigureConfig dataclass + seaborn init snippet for make_figures.py |

---

## Usage Snippet (copy-paste for make_figures.py)

```python
import matplotlib.pyplot as plt
import seaborn as sns
from config import FigureConfig

cfg = FigureConfig()
plt.style.use(cfg.style)
sns.set_context(cfg.context, font_scale=cfg.font_scale)
```

---

## Result File Schema (reference for aggregate_results.py)

```python
# results/h-m1/signal_void_analysis.json
SIGNAL_VOID_SCHEMA = {
    "sft_lcb_hard_pass1": float,          # Task A primary metric
    "signal_void_primary": bool,           # pass1 < gate_threshold
    "apps_difficulty_loss": {
        "introductory": float,
        "interview": float,
        "competition": float,
        "counts": {"introductory": int, "interview": int, "competition": int},
    },
    "loss_gradient_secondary": bool,       # competition_loss > introductory_loss
    "apps_competition_coverage": float,    # Task C fraction
    "coverage_void_secondary": bool,       # coverage < coverage_threshold
    "gate_satisfied": bool,                # == signal_void_primary (primary gate only)
}
```
