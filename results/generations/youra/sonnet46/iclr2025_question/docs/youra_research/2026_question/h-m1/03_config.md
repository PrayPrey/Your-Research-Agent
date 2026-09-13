# Config: H-M1

**Hypothesis:** H-M1 (MECHANISM PoC)
**Type:** Statistical Analysis — no GPU, no training
**Applied:** Standard dataclass + YAML config pattern (FULL tier)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: Config classes verified from actual base code (`h-e1/code/config.py`)
**Config Files Found**: `h-e1/code/config.py` (read directly)
**Pattern Used**: dataclass + YAML (`load_config()` reading `config.yaml` → `ExperimentConfig`)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: h-e1/code/config.py (ACTUAL CODE — verified)
@dataclass
class ExperimentConfig:
    # Model (NOT inherited — H-M1 does no inference)
    model_name: str = "cross-encoder/nli-deberta-v3-large"

    # Inference (NOT inherited — H-M1 does no inference)
    batch_size: int = 32
    batch_size_fallback: int = 16
    max_length: int = 512
    truncation: bool = True

    # Reproducibility (INHERITED)
    seed: int = 42

    # Dataset (INHERITED — same field names)
    halueval_hf_id: str = "pminervini/HaluEval"
    tasks: Tuple[str, ...] = ("dialogue", "qa", "summarization")
    hf_config_names: Dict[str, str] = {"dialogue": "dialogue", "qa": "qa", "summarization": "summarization"}
    premise_fields: Dict[str, str] = {"dialogue": "knowledge", "qa": "knowledge", "summarization": "document"}
    hypothesis_right_fields: Dict[str, str] = {"dialogue": "right_response", "qa": "right_answer", "summarization": "right_summary"}
    hypothesis_hall_fields: Dict[str, str] = {"dialogue": "hallucinated_response", "qa": "hallucinated_answer", "summarization": "hallucinated_summary"}

    # Output (NOT directly inherited — H-M1 uses different filenames/dirs)
    results_dir: str = "results"
    figures_dir: str = "figures"
    scores_filename: str = "h-e1_results.json"
    summary_filename: str = "h-e1_summary.json"
```

**Verified from**: `h-e1/code/config.py` (actual implementation)

**Inherited fields**: `seed`, `halueval_hf_id`, `tasks`, `hf_config_names`, `premise_fields`, `hypothesis_right_fields`, `hypothesis_hall_fields`

**Dropped fields** (H-M1 does no inference): `model_name`, `batch_size`, `batch_size_fallback`, `max_length`, `truncation`, `auroc_threshold`, `delong_alpha`, `cohen_d_threshold`, `tasks_required_to_pass`, `label_audit_n`, `save_scores`

---

## A-6: Visualization - Gate Metrics [Complexity: 9, Budget: 2]

**Applied**: Standard dataclass config pattern

### Configuration (Python Dataclass — fields in ExperimentConfig)

```python
# Visualization parameters for plot_gate_metrics_comparison()
# Added to ExperimentConfig in config.py

# Figure settings (gate metrics comparison — 2-subplot)
fig_gate_figsize: Tuple[float, float] = (10.0, 8.0)
fig_dpi: int = 150
fig_bar_color_pass: str = "#2196F3"    # blue — KL/Wilcoxon bars
fig_bar_color_fail: str = "#F44336"    # red — below threshold
fig_threshold_color: str = "#FF9800"   # orange — threshold lines
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Gate figure config | figsize, DPI, color constants for KL bar + Wilcoxon p-value subplots |
| C-6-2 | Threshold config | kl_threshold and wilcoxon_alpha reused from statistical thresholds section |

---

## A-7: Visualization - Distributions [Complexity: 10, Budget: 2]

**Applied**: Standard dataclass config pattern

### Configuration (Python Dataclass — fields in ExperimentConfig)

```python
# Visualization parameters for violin + KL summary figures

# Violin plot (score_distributions_violin)
fig_violin_figsize: Tuple[float, float] = (14.0, 10.0)
fig_violin_color_hall: str = "#E91E63"     # pink/red — hallucinated
fig_violin_color_corr: str = "#4CAF50"     # green — correct
fig_uniform_ref_color: str = "#9E9E9E"     # grey — uniform 1/3 reference

# KL divergence summary (kl_divergence_summary — 3x3 bar chart)
fig_kl_summary_figsize: Tuple[float, float] = (12.0, 6.0)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Violin config | figsize, per-class colors (hall vs corr), uniform reference line color |
| C-7-2 | KL summary config | figsize for 3x3 bar chart; threshold line reused from kl_threshold |

---

## A-8: Visualization - Separation [Complexity: 9, Budget: 2]

**Applied**: Standard dataclass config pattern

### Configuration (Python Dataclass — fields in ExperimentConfig)

```python
# Visualization parameters for boxplot + near-uniform figures

# Score separation boxplot (score_separation_boxplot)
fig_box_figsize: Tuple[float, float] = (12.0, 6.0)
fig_box_color_hall: str = "#FF9800"    # orange — hallucinated (as per PRD FR-5.4)
fig_box_color_corr: str = "#2196F3"    # blue — correct (as per PRD FR-5.4)

# Near-uniform proportion (near_uniform_proportion — stacked bar)
fig_near_uniform_figsize: Tuple[float, float] = (8.0, 6.0)
fig_near_uniform_target_color: str = "#F44336"    # red — target line at 5%
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Boxplot config | figsize, orange/blue colors per PRD; p-value annotation enabled via wilcoxon_alpha |
| C-8-2 | Near-uniform config | figsize, target line color; threshold reused from near_uniform_threshold |

---

## Full ExperimentConfig (h-m1/code/config.py)

```python
from dataclasses import dataclass, field
from typing import Tuple, Dict
import yaml


@dataclass
class ExperimentConfig:
    # --- Data paths ---
    h_e1_results_path: str = "../../h-e1/results/h-e1_results.json"
    halueval_hf_id: str = "pminervini/HaluEval"

    # --- Dataset (inherited from h-e1, same field names) ---
    tasks: Tuple[str, ...] = ("dialogue", "qa", "summarization")
    hf_config_names: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "dialogue", "qa": "qa", "summarization": "summarization"
    })
    premise_fields: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "knowledge", "qa": "knowledge", "summarization": "document"
    })
    hypothesis_right_fields: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "right_response", "qa": "right_answer", "summarization": "right_summary"
    })
    hypothesis_hall_fields: Dict[str, str] = field(default_factory=lambda: {
        "dialogue": "hallucinated_response", "qa": "hallucinated_answer",
        "summarization": "hallucinated_summary"
    })

    # --- Statistical thresholds ---
    kl_threshold: float = 0.05
    wilcoxon_alpha: float = 0.05
    near_uniform_threshold: float = 0.05       # within 5% of 1/3 per-dimension
    near_uniform_warn_threshold: float = 0.50  # warn if > 50% examples near-uniform
    wilcoxon_tasks_required: int = 2           # ≥2/3 tasks must pass Wilcoxon

    # --- Reproducibility ---
    seed: int = 42

    # --- Output ---
    results_dir: str = "../results"
    figures_dir: str = "../figures"
    results_filename: str = "h_m1_results.json"
    summary_filename: str = "h_m1_summary.json"

    # --- Visualization: shared ---
    fig_dpi: int = 150

    # --- Visualization: gate metrics comparison (A-6) ---
    fig_gate_figsize: Tuple[float, float] = (10.0, 8.0)
    fig_bar_color_pass: str = "#2196F3"
    fig_bar_color_fail: str = "#F44336"
    fig_threshold_color: str = "#FF9800"

    # --- Visualization: violin distributions (A-7) ---
    fig_violin_figsize: Tuple[float, float] = (14.0, 10.0)
    fig_violin_color_hall: str = "#E91E63"
    fig_violin_color_corr: str = "#4CAF50"
    fig_uniform_ref_color: str = "#9E9E9E"

    # --- Visualization: KL divergence summary (A-7) ---
    fig_kl_summary_figsize: Tuple[float, float] = (12.0, 6.0)

    # --- Visualization: score separation boxplot (A-8) ---
    fig_box_figsize: Tuple[float, float] = (12.0, 6.0)
    fig_box_color_hall: str = "#FF9800"
    fig_box_color_corr: str = "#2196F3"

    # --- Visualization: near-uniform proportion (A-8) ---
    fig_near_uniform_figsize: Tuple[float, float] = (8.0, 6.0)
    fig_near_uniform_target_color: str = "#F44336"


def load_config(path: str = "config.yaml") -> ExperimentConfig:
    """Load ExperimentConfig from YAML, falling back to defaults for missing keys."""
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f) or {}
        # Convert list → tuple for tuple fields
        for key in ("tasks",):
            if key in data and isinstance(data[key], list):
                data[key] = tuple(data[key])
        # Convert list → tuple for figsize fields
        for key in data:
            if key.endswith("_figsize") and isinstance(data[key], list):
                data[key] = tuple(data[key])
        return ExperimentConfig(**{k: v for k, v in data.items()
                                   if k in ExperimentConfig.__dataclass_fields__})
    except FileNotFoundError:
        return ExperimentConfig()
```

---

## config.yaml (h-m1/code/config.yaml)

```yaml
# H-M1 Statistical Analysis Configuration

# Data paths
h_e1_results_path: "../../h-e1/results/h-e1_results.json"
halueval_hf_id: "pminervini/HaluEval"
tasks: ["dialogue", "qa", "summarization"]

# Statistical thresholds
kl_threshold: 0.05
wilcoxon_alpha: 0.05
near_uniform_threshold: 0.05
near_uniform_warn_threshold: 0.50
wilcoxon_tasks_required: 2

# Reproducibility
seed: 42

# Output
results_dir: "../results"
figures_dir: "../figures"
results_filename: "h_m1_results.json"
summary_filename: "h_m1_summary.json"

# Visualization
fig_dpi: 150
fig_gate_figsize: [10.0, 8.0]
fig_bar_color_pass: "#2196F3"
fig_bar_color_fail: "#F44336"
fig_threshold_color: "#FF9800"
fig_violin_figsize: [14.0, 10.0]
fig_violin_color_hall: "#E91E63"
fig_violin_color_corr: "#4CAF50"
fig_uniform_ref_color: "#9E9E9E"
fig_kl_summary_figsize: [12.0, 6.0]
fig_box_figsize: [12.0, 6.0]
fig_box_color_hall: "#FF9800"
fig_box_color_corr: "#2196F3"
fig_near_uniform_figsize: [8.0, 6.0]
fig_near_uniform_target_color: "#F44336"
```
