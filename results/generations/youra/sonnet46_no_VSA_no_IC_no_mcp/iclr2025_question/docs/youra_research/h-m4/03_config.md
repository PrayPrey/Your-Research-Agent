---
hypothesis_id: h-m4
phase: config
generated_at: "2026-08-25"
author: yoon303@ust.ac.kr
---

# Config: H-M4 — Verbalized Confidence (VC) Calibration

Applied: single-script-dataclass pattern

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends h-m3)
**Status**: Config classes verified from h-m3/code/config.py actual code
**Config Files Found**: `docs/youra_research/h-m3/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

From `docs/youra_research/h-m3/code/config.py` (actual code):

```python
# H-M3 actual fields (verified)
@dataclass
class Config:
    K: int = 10
    seed: int = 42
    n_bootstrap: int = 1000
    n_questions: int = 98
    delta_auroc_gate: float = 0.03
    he1_code_dir: str = "../../h-e1/code"
    hm2_code_dir: str = "../../h-m2/code"
    he1_results_dir: str = "../../h-e1/results"
    figures_dir: str = "../figures"
    results_path: str = "../results.json"
    rescale_with_baseline: bool = True
```

H-M4 inherits: `seed`, `n_bootstrap`, `n_questions`, `hm2_code_dir`, `he1_code_dir`, `figures_dir`, `results_path`

Dropped: `K`, `delta_auroc_gate`, `he1_results_dir`, `rescale_with_baseline` (not needed for VC)

New in H-M4: `model_id`, `max_new_tokens`, `parse_rate_gate`, `auroc_te_baseline`, `auroc_se_baseline`, `hm3_results_path`, figure settings, `n_bins_ece`, `dataset_id`, `dataset_config`

---

## A-7: Visualization Config [Complexity: 1, Budget: 2]

Applied: Standard matplotlib defaults

### C-7-1: Figure Configuration

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    # --- Model ---
    model_id: str = "meta-llama/Llama-2-7b-chat-hf"
    max_new_tokens: int = 80
    do_sample: bool = False          # greedy; sampling excluded per PRD
    temperature: float = 1.0

    # --- Inference ---
    batch_size: int = 1
    seed: int = 42
    precision: str = "float16"

    # --- Evaluation ---
    n_bootstrap: int = 1000
    n_bins_ece: int = 10
    parse_rate_gate: float = 0.80
    auroc_te_baseline: float = 0.4381   # inherited from h-m3 results
    auroc_se_baseline: float = 0.286    # inherited from h-m3 results

    # --- Data ---
    n_questions: int = 98
    dataset_id: str = "mandarjoshi/trivia_qa"
    dataset_config: str = "rc"

    # --- Paths ---
    hm2_code_dir: str = "../../h-m2/code"
    hm3_results_path: str = "../../h-m3/results.json"
    he1_code_dir: str = "../../h-e1/code"
    figures_dir: str = "../figures"
    results_path: str = "../results.json"

    # --- Figure settings (C-7-1) ---
    figure_dpi: int = 150
    fig_size_bar: tuple = (7, 5)         # auroc_comparison.png
    fig_size_hist: tuple = (7, 4)        # confidence_histogram.png
    fig_size_roc: tuple = (6, 6)         # roc_curves.png
    fig_size_cal: tuple = (6, 6)         # reliability_diagram.png
    fig_size_scatter: tuple = (6, 5)     # scatter_vc_em.png

    # Color palette: VC / TE / SE bars
    color_vc: str = "#4C72B0"
    color_te: str = "#DD8452"
    color_se: str = "#55A868"

    # Output filenames
    fname_bar: str = "auroc_comparison.png"
    fname_hist: str = "confidence_histogram.png"
    fname_roc: str = "roc_curves.png"
    fname_cal: str = "reliability_diagram.png"
    fname_scatter: str = "scatter_vc_em.png"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Figure config | figure_dpi, fig_size_*, color_*, fname_* fields in Config |
| C-7-2 | Full YAML schema | see below |

---

## C-7-2: Full Experiment YAML Schema

```yaml
# h-m4 experiment config — all tunable parameters
# Usage: loaded by run.py, overrides Config defaults

model:
  model_id: "meta-llama/Llama-2-7b-chat-hf"
  max_new_tokens: 80
  do_sample: false
  temperature: 1.0

inference:
  batch_size: 1
  seed: 42
  precision: "float16"   # "float16" | "bfloat16" | "float32"

evaluation:
  n_bootstrap: 1000
  n_bins_ece: 10

data:
  n_questions: 98
  dataset_id: "mandarjoshi/trivia_qa"
  dataset_config: "rc"

paths:
  hm2_code_dir: "../../h-m2/code"
  hm3_results_path: "../../h-m3/results.json"
  he1_code_dir: "../../h-e1/code"
  figures_dir: "../figures"
  results_path: "../results.json"

thresholds:
  parse_rate_gate: 0.80      # fail if VC parse rate < this
  auroc_te_baseline: 0.4381  # inherited from h-m3; gate: VC AUROC < this
  auroc_se_baseline: 0.286   # inherited from h-m3; gate: VC AUROC < this

figures:
  dpi: 150
  colors:
    vc: "#4C72B0"
    te: "#DD8452"
    se: "#55A868"
  sizes:
    bar: [7, 5]
    hist: [7, 4]
    roc: [6, 6]
    cal: [6, 6]
    scatter: [6, 5]
  filenames:
    bar: "auroc_comparison.png"
    hist: "confidence_histogram.png"
    roc: "roc_curves.png"
    cal: "reliability_diagram.png"
    scatter: "scatter_vc_em.png"
```

**Validation notes:**
- `parse_rate_gate`: experiment aborts early if parse rate falls below 0.80 (degenerate VC signal)
- `auroc_te_baseline` / `auroc_se_baseline`: hardcoded from h-m3 `results.json`; update only if h-m3 re-run
- `precision`: only `float16` tested; `bfloat16` is safe on Ampere+
- `do_sample: false` enforces greedy; `temperature` has no effect but kept for completeness
