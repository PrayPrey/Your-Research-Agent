# Config: H-M1
# SSD Frobenius Error Scaling Gate Experiment

**Hypothesis:** H-M1 | **Type:** MECHANISM (Day 0 Gate) | **Date:** 2026-08-03

Applied: HuggingFace TrainingArguments dataclass pattern (field grouping by concern)
Applied: Standard PyTorch Adam defaults (betas, weight_decay)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing code to analyze
**Config Files Found**: None — new config design
**Pattern Used**: dataclass

---

## Main Config (`code/config.py`)

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    # --- Data ---
    teacher_model_id: str = "meta-llama/Llama-3-8B"
    dataset_id: str = "allenai/c4"
    dataset_subset: str = "en"
    dataset_split: str = "validation"
    n_samples: int = 500
    target_lengths: List[int] = field(default_factory=lambda: [512, 1024, 2048, 4096, 8192])
    seed: int = 42

    # --- Model dimensions (match LLaMA-3-8B) ---
    n_layers: int = 32
    d_model: int = 4096
    d_state: int = 64
    n_heads: int = 32
    headdim: int = 128       # d_model // n_heads

    # --- SSD Fitter ---
    n_opt_steps: int = 10000
    lr: float = 1e-3
    adam_betas: tuple = (0.9, 0.999)
    adam_weight_decay: float = 0.0
    teacher_dtype: str = "bfloat16"
    fitter_dtype: str = "float32"  # Non-standard: fp32 for SSM numerical stability

    # --- Gate thresholds ---
    gate_slope_threshold: float = 0.5
    gate_pct90_threshold: float = 0.3

    # --- Paths ---
    results_dir: str = "results"
    figures_dir: str = "figures"
    checkpoint_every_n_samples: int = 50
```

---

## YAML Schema (CLI Override)

```yaml
# h-m1/config.yaml — override any field via: python run.py --config config.yaml

teacher_model_id: "meta-llama/Llama-3-8B"
dataset_id: "allenai/c4"
dataset_subset: "en"
dataset_split: "validation"
n_samples: 500
target_lengths: [512, 1024, 2048, 4096, 8192]
seed: 42

n_layers: 32
d_model: 4096
d_state: 64
n_heads: 32
headdim: 128

n_opt_steps: 10000
lr: 0.001
adam_betas: [0.9, 0.999]
adam_weight_decay: 0.0
teacher_dtype: "bfloat16"
fitter_dtype: "float32"

gate_slope_threshold: 0.5
gate_pct90_threshold: 0.3

results_dir: "results"
figures_dir: "figures"
checkpoint_every_n_samples: 50
```

---

## A-10: Visualization [Complexity: 12, Budget: 2 subtasks]

Applied: Standard PyTorch defaults

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-10-1 | Figure Layout Config | Figure sizes, DPI, color palette, axis styling |
| C-10-2 | Plot Dataclasses | Per-figure config dataclass for each of the 4 figures |

---

### C-10-1: Figure Layout Configuration

```python
# code/config.py (append to module)

FIGURE_DPI: int = 150
COLOR_SSD: str = "#2196F3"
COLOR_TOEPLITZ: str = "#FF5722"
COLOR_THRESHOLD: str = "#F44336"
COLOR_PALETTE_VIOLIN: str = "Blues"

FIGURE_SIZE_BAR_LOGLOG: tuple = (12, 5)   # Fig 1: two-panel
FIGURE_SIZE_SCALING: tuple = (8, 6)        # Fig 2
FIGURE_SIZE_VIOLIN: tuple = (14, 6)        # Fig 3
FIGURE_SIZE_HEATMAP: tuple = (10, 4)       # Fig 4
```

---

### C-10-2: Plot-Level Config Dataclasses

```python
# code/config.py (append to module)
from dataclasses import dataclass


@dataclass
class GatePlotConfig:
    """Fig 1: Bar chart (pct90 per N) + log-log error curve."""
    figsize: tuple = (12, 5)
    dpi: int = 150
    bar_color: str = "#2196F3"
    threshold_color: str = "#F44336"
    threshold_value: float = 0.3
    xlabel_bar: str = "Sequence Length N"
    ylabel_bar: str = "90th Pct Frobenius Error"
    xlabel_loglog: str = "log N"
    ylabel_loglog: str = "log Mean Frobenius Error"
    out_filename: str = "fig1_gate_bar_loglog.png"


@dataclass
class ScalingPlotConfig:
    """Fig 2: Log-log SSD vs Toeplitz scaling with regression line."""
    figsize: tuple = (8, 6)
    dpi: int = 150
    color_ssd: str = "#2196F3"
    color_toeplitz: str = "#FF5722"
    xlabel: str = "Sequence Length N (log scale)"
    ylabel: str = "Mean Frobenius Error (log scale)"
    out_filename: str = "fig2_scaling_ssd_vs_toeplitz.png"


@dataclass
class ViolinPlotConfig:
    """Fig 3: Violin distribution per N with 90th pct threshold line."""
    figsize: tuple = (14, 6)
    dpi: int = 150
    palette: str = "Blues"
    threshold_color: str = "#F44336"
    threshold_value: float = 0.3
    xlabel: str = "Sequence Length N"
    ylabel: str = "Frobenius Error"
    out_filename: str = "fig3_violin_distribution.png"


@dataclass
class HeatmapPlotConfig:
    """Fig 4: Per-layer mean Frobenius error at N=8k."""
    figsize: tuple = (10, 4)
    dpi: int = 150
    cmap: str = "viridis"
    xlabel: str = "Layer Index"
    ylabel: str = "Mean Frobenius Error"
    title: str = "Per-Layer Frobenius Error at N=8192"
    out_filename: str = "fig4_layer_heatmap.png"
```

---

## Results Output Schema (`results/gate_metrics.json`)

```json
{
  "hypothesis_id": "H-M1",
  "gate_pass": true,
  "beta": 0.31,
  "pct90_at_8k": 0.21,
  "mean_errors_by_N": {
    "512": 0.097,
    "1024": 0.112,
    "2048": 0.134,
    "4096": 0.158,
    "8192": 0.183
  },
  "gate_threshold_slope": 0.5,
  "gate_threshold_pct90": 0.3,
  "decision": "PASS",
  "timestamp": "2026-08-03T00:00:00Z"
}
```

**Field types:**
- `hypothesis_id`: string, fixed `"H-M1"`
- `gate_pass`: bool, `beta <= threshold AND pct90 <= threshold`
- `beta`: float, log-log regression slope from `np.polyfit`
- `pct90_at_8k`: float, `np.percentile(errors_by_N[8192], 90)`
- `mean_errors_by_N`: dict, keys are string N values, values are floats
- `gate_threshold_slope`: float, copied from `Config.gate_slope_threshold`
- `gate_threshold_pct90`: float, copied from `Config.gate_pct90_threshold`
- `decision`: string literal `"PASS"` or `"STOP"`
- `timestamp`: ISO8601 string, set at experiment completion
