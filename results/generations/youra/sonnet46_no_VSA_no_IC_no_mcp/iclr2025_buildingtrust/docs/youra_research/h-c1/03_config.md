---
title: "Config: h-c1 — RLHF Calibration Moderation Experiment"
hypothesis_id: h-c1
hypothesis_type: CONDITION
date: 2026-08-25
author: yoon303@ust.ac.kr
---

Applied: H-E1 dataclass extension pattern
Applied: Standard matplotlib figure config pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code at `h-e1/code/config.py`
**Config Files Found**: `docs/youra_research/h-e1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    seed: int = 1
    batch_size: int = 8
    n_bins_primary: int = 15
    n_bins_secondary: int = 10
    min_examples_per_cell: int = 50
    subsample_clean: int = 200
    subsample_adv: int = 200
    prevalidation_n: int = 10
    models: List[str] = field(default_factory=lambda: ["meta-llama/Llama-2-7b-hf"])
    use_4bit_threshold_gb: float = 40.0
    max_confidence_degenerate: float = 0.999
    non_degenerate_fraction: float = 0.90
    min_confidence_uniform: float = 0.30
    prob_sum_tolerance: float = 1e-3
    ece_plausible_min: float = 0.0
    ece_plausible_max: float = 0.5
    clean_ece_min: float = 0.05
    clean_ece_max: float = 0.15
    min_models_sanity: int = 1
    gate_min_cells: int = 1
    task_split_map: Dict[str, Tuple[str, str]] = field(default_factory=lambda: {
        "qqp":  ("glue_qqp",  "advglue_qqp"),
        "sst2": ("glue_sst2", "advglue_sst2"),
        "nli":  ("mnli",      "advglue_mnli"),
    })
    anli_splits: List[str] = field(default_factory=lambda: ["anli_r1", "anli_r2", "anli_r3"])
    results_dir: str = "docs/youra_research/h-e1/results"
    figures_dir: str = "docs/youra_research/h-e1/figures"
    errors_log: str = "docs/youra_research/h-e1/results/errors.log"
```

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation)

---

## A-6: Gate Evaluation & Consistency [Complexity: 2, Budget: 2 subtasks]

```python
from dataclasses import dataclass, field
from typing import List, Dict, Tuple


@dataclass
class HC1Config(ExperimentConfig):
    # --- Models (extends base) ---
    models: List[str] = field(default_factory=lambda: [
        "meta-llama/Llama-2-7b-hf",
        "meta-llama/Llama-2-7b-chat-hf",
    ])

    # --- Paths ---
    results_dir: str = "docs/youra_research/h-c1/results"
    figures_dir: str = "docs/youra_research/h-c1/figures"
    errors_log: str = "docs/youra_research/h-c1/results/errors.log"
    results_file: str = "docs/youra_research/h-c1/results/hc1_results.json"
    validation_report: str = "docs/youra_research/h-c1/04_validation.md"

    # A-6-1: Gate thresholds
    moderation_rate_threshold: float = 0.60   # fraction of cells where ΔECE_chat < ΔECE_base
    ddece_nli_threshold: float = 0.01         # min ΔΔECE on NLI cell to count as CONFIRMED

    # A-6-2: Consistency baselines (from H-E1 actual results)
    he1_base_ece_clean_nli: float = 0.279
    he1_base_delta_ece_nli: float = 0.071
    consistency_tolerance: float = 0.005      # warn if recomputed base deviates beyond this
    consistency_failure_mode: str = "warn"    # "warn" | "fail" — never fail, just log
```

### hc1_results.json schema

```python
# Per-cell record (one entry per (model, task, split) triple)
CELL_SCHEMA = {
    "model": str,           # "base" | "chat"
    "task": str,            # "nli" | "qqp" | "sst2" | "anli_r1" | "anli_r2" | "anli_r3"
    "split": str,           # "clean" | "adversarial"
    "ece": float,
    "n_examples": int,
    "label_preservation_rate": float,
}

# Top-level output
HC1_RESULTS_SCHEMA = {
    "hypothesis_id": "h-c1",
    "timestamp": str,       # ISO 8601
    "cells": List[CELL_SCHEMA],
    "summary": {
        "moderation_rate": float,
        "ddece_nli": float,
        "gate_result": str,     # "CONFIRMED" | "FAILED"
        "consistency_ok": bool,
    },
}
```

### 04_validation.md template structure

```markdown
# Validation Report: h-c1
date: {timestamp}
gate_result: {CONFIRMED|FAILED}

## Gate Metrics
- moderation_rate: {value} (threshold: 0.60)
- ddece_nli: {value} (threshold: 0.01)

## Consistency Check (vs H-E1)
- he1_base_ece_clean_nli expected: 0.279 ± 0.005, observed: {value}
- he1_base_delta_ece_nli expected: 0.071 ± 0.005, observed: {value}
- consistency_ok: {True|False}

## Per-Cell Results
| model | task | split | ECE | ΔECE | ΔΔECE |
|-------|------|-------|-----|------|-------|
...

## Mechanism Indicators
...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Gate config | `moderation_rate_threshold`, `ddece_nli_threshold`, results schema, validation template |
| C-6-2 | Consistency config | H-E1 baseline values, tolerance, warn-not-fail mode |

---

## A-7: Figure Configuration [Complexity: 2, Budget: 2 subtasks]

```python
@dataclass
class FigureConfig:
    dpi: int = 300
    base_color: str = "#2196F3"    # blue — base model
    chat_color: str = "#FF5722"    # deep orange — chat model; distinct from base

    # Fig 1: Paired bar chart (ΔECE_base vs ΔECE_chat across cells)
    fig1_size: Tuple[float, float] = (10, 5)
    fig1_xlabel: str = "(task, split) cell"
    fig1_ylabel: str = "ΔECE (ECE_adv − ECE_clean)"
    fig1_title: str = "RLHF Moderation of Adversarial Calibration Degradation (H-C1)"

    # Fig 2: Reliability diagrams (2×2 grid)
    fig2_size: Tuple[float, float] = (10, 8)
    fig2_n_bins: int = 15          # inherited from H-E1 n_bins_primary
    fig2_bin_edges: List[float] = field(
        default_factory=lambda: [i / 15 for i in range(16)]  # 15 equal-width bins [0,1]
    )
    fig2_title: str = "ECE Reliability Diagrams — NLI Task (H-C1)"

    # Fig 3: ΔΔECE scatter plot
    fig3_size: Tuple[float, float] = (6, 6)
    fig3_xlabel: str = "ΔECE_base"
    fig3_ylabel: str = "ΔECE_chat"
    fig3_title: str = "ΔΔECE Scatter: Base vs Chat (H-C1)"
    fig3_identity_color: str = "#9E9E9E"   # grey identity line
    fig3_identity_linestyle: str = "--"
    fig3_identity_linewidth: float = 1.0

    # Fig 4: ANLI gradient (ΔECE by R1→R2→R3)
    fig4_size: Tuple[float, float] = (7, 5)
    fig4_xlabel: str = "ANLI Split"
    fig4_ylabel: str = "ΔECE"
    fig4_title: str = "ANLI Calibration Gradient — Base vs Chat (H-C1)"
    fig4_x_order: List[str] = field(default_factory=lambda: ["R1", "R2", "R3"])  # enforced ordering

    figures_dir: str = "docs/youra_research/h-c1/figures"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Figure base config | DPI, colors, sizes, axis labels, titles for all 4 figures |
| C-7-2 | Plot-specific settings | Fig2 bin edges (15), fig3 identity line, fig4 x-axis order R1→R2→R3 |
