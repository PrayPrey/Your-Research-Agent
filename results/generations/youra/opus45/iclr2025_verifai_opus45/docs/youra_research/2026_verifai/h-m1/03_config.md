# Config: H-M1 — Granularity Effect on Repair Success

Applied: Standard Python dataclass pattern (KB search returned non-domain results)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from actual H-E1 code (read via file tool; Serena project activation unavailable)
**Config Files Found**: `h-e1/code/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

```python
# From: docs/youra_research/20260330_verifai/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    # Model
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    max_new_tokens: int = 512
    temperature: float = 0.0
    do_sample: bool = False

    # Dataset
    dataset_name: str = "mbpp"
    task_id_min: int = 11
    task_id_max: int = 510

    # Execution
    execution_timeout: int = 10

    # Reproducibility
    seed: int = 1

    # Paths
    results_dir: str = "results"
    figures_dir: str = "results/figures"
    output_json: str = "results/execution_results.json"
    output_metrics: str = "results/metrics.yaml"

    # Gate
    gate_threshold: float = 0.30
    ci_confidence: float = 0.95
    ci_method: str = "wilson"
```

**Verified from**: `docs/youra_research/20260330_verifai/h-e1/code/config.py` (actual implementation)

---

## A-2: Data Loading [Complexity: 9, Budget: 2 subtasks]

Applied: Standard Python dataclass pattern

### Configuration

```python
# In config.py
from dataclasses import dataclass

GRANULARITY_LEVELS = ["G0", "G1", "G2", "G3", "G4"]

@dataclass
class RepairConfig:
    # Model (inherited from H-E1 ExperimentConfig, field names verified)
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    max_new_tokens: int = 512
    temperature: float = 0.0
    do_sample: bool = False
    seed: int = 1

    # Data (mbpp field renamed from dataset_name for clarity)
    h_e1_results_path: str = "../h-e1/results/execution_results.json"
    mbpp_dataset_name: str = "mbpp"
    task_id_min: int = 11
    task_id_max: int = 510

    # Execution (inherited from H-E1)
    execution_timeout: int = 10

    # Paths
    results_dir: str = "results"
    figures_dir: str = "figures"
    output_json: str = "results/repair_results.json"
    output_metrics: str = "results/metrics.yaml"
    output_posthoc: str = "results/posthoc.yaml"
    checkpoint_path: str = "results/checkpoint.json"

    # Gate (ANOVA-specific, replaces H-E1 gate_threshold/ci fields)
    anova_alpha: float = 0.05
    eta_squared_threshold: float = 0.02
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | H-E1 Results Loader | Config fields: `h_e1_results_path`, `task_id_min`, `task_id_max` |
| C-2-2 | MBPP Index Loader | Config fields: `mbpp_dataset_name`, `task_id_min`, `task_id_max` |

---

## A-9: Visualization [Complexity: 12, Budget: 2 subtasks]

### Configuration

```python
# Visualization constants (used in evaluate.py, not in RepairConfig dataclass)
VIZ_CONFIG = {
    "figure_dpi": 150,
    "bar_color_palette": "Blues_d",
    "heatmap_cmap": "RdYlGn",
    "ci_confidence": 0.95,
    "figure_size": (8, 5),
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | Per-Granularity Plots | bar chart + line curve; uses `figures_dir`, `GRANULARITY_LEVELS` |
| C-9-2 | Analysis Plots | ANOVA summary, gate comparison, Tukey heatmap, error breakdown |

---

## A-10: Main Runner [Complexity: 9, Budget: 2 subtasks]

### Configuration

```python
# CLI defaults mirror RepairConfig fields
CLI_DEFAULTS = {
    "gpu": 0,
    "results_dir": "results",
    "h_e1_results": "../h-e1/results/execution_results.json",
}

# Gate verdict constants
GATE_EXIT_PASS = 0
GATE_EXIT_FAIL = 1
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-10-1 | Pipeline Orchestration | RepairConfig init, sys.path setup for H-E1 model, checkpoint resume |
| C-10-2 | Gate Verdict + CLI | argparse with CLI_DEFAULTS, exit code 0/1 based on `anova_alpha` |
