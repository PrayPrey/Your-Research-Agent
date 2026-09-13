# Configuration: H-M2 Analysis

**Applied**: Standard Python dataclass config pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code
**Config Files Found**: `h-e1/code/config.py`
**Pattern Used**: Hardcoded dict in H-E1; dataclasses for H-M2 analysis layer

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-e1/code/config.py (ACTUAL CODE - verified)
CONFIG = {
    "max_steps": 5000,
    "save_steps": 500,        # → checkpoint_interval in H-M2
    "curriculum_step": 2500,  # → early_phase_max_step in H-M2
    "log_dir": "h-e1/logs",
    "results_dir": "h-e1/results",
}
CONDITIONS = ["curriculum", "uniform", "easy_only", "hard_only"]
```

**Verified from**: `h-e1/code/config.py` (actual implementation)

---

## C-6: FigureGenerator Config [Complexity: 2, Budget: 2]

**Applied**: Standard Python dataclass config pattern

### Configuration

```python
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class FigureConfig:
    figure_dpi: int = 200
    figure_size: Tuple[int, int] = (10, 7)
    output_format: str = "png"
    colors: Dict[str, str] = field(default_factory=lambda: {
        "curriculum": "blue",
        "uniform":    "orange",
        "easy_only":  "green",
        "hard_only":  "red",
    })
    fig_reward_entropy:     str = "reward_entropy_comparison.png"
    fig_pass1_gain:         str = "pass1_gain_vs_density.png"
    fig_correlation_matrix: str = "correlation_matrix.png"
    fig_condition_summary:  str = "condition_summary.png"
    fig_checkpoint_series:  str = "checkpoint_series.png"


@dataclass
class AnalysisRunConfig:
    h_e1_log_dir:           str = "../h-e1/logs/"
    h_e1_results_dir:       str = "../h-e1/results/"
    output_dir:             str = "results/"
    figures_dir:            str = "figures/"
    conditions:             List[str] = field(default_factory=lambda: [
        "curriculum", "uniform", "easy_only", "hard_only"
    ])
    early_phase_max_step:   int = 2500  # from h-e1 curriculum_step
    checkpoint_interval:    int = 500   # from h-e1 save_steps
    n_checkpoints:          int = 10
    min_viable_checkpoints: int = 5
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | FigureConfig | Plot parameters, colors, output filenames |
| C-6-2 | AnalysisRunConfig | Paths, conditions, checkpoint window settings |

---

## C-8: pass@1 Fallback Config [Complexity: 2, Budget: 2]

**Applied**: Standard Python dataclass config pattern

### Configuration

```python
@dataclass
class DataDiscoveryConfig:
    csv_filename_template:  str = "pass1_checkpoint_{condition}.csv"
    json_fallback_template: str = "eval_results_{condition}.json"
    density_csv_template:   str = "reward_density_{condition}.csv"
    max_steps:              int = 5000  # from h-e1 max_steps
    window_size:            int = 500   # from h-e1 save_steps


@dataclass
class GateThresholdConfig:
    pearson_r_threshold:     float = 0.5
    p_value_threshold:       float = 0.05
    n_pooled_observations:   int   = 36
    entropy_direction_check: bool  = True
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | DataDiscoveryConfig | File templates, step/window params for data loading |
| C-8-2 | GateThresholdConfig | Pearson r, p-value, pooled-N gate thresholds |

---

## YAML Override (config.yaml)

```yaml
# h-m2/config.yaml — CLI override for AnalysisRunConfig
h_e1_log_dir: "../h-e1/logs/"
h_e1_results_dir: "../h-e1/results/"
output_dir: "results/"
figures_dir: "figures/"
early_phase_max_step: 2500
checkpoint_interval: 500
n_checkpoints: 10
min_viable_checkpoints: 5
pearson_r_threshold: 0.5
p_value_threshold: 0.05
n_pooled_observations: 36
entropy_direction_check: true
```
