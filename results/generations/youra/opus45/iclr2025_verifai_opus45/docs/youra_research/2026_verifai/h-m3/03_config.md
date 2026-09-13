# Config: H-M3 Non-Monotonicity Confirmation (G3 >= G4)

**Date:** 2026-03-30
**Hypothesis:** G4 (full trace) does not significantly outperform G3 (G4 <= G3 + 2%)
**Type:** MECHANISM (Statistical Reanalysis)

Applied: Standard Python dataclass pattern (Archon KB search returned no domain-specific pattern)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from actual H-M1 code (direct file read)
**Config Files Found**: `h-m1/code/config.py` — `RepairConfig`, `ExperimentConfig` dataclasses
**Pattern Used**: dataclass (consistent with H-M1 convention)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual H-M1 Code)

```python
# From: h-m1/code/config.py (ACTUAL CODE - verified field names and defaults)
@dataclass
class RepairConfig:
    model_id: str = "codellama/CodeLlama-7b-Instruct-hf"
    max_new_tokens: int = 512
    temperature: float = 0.0
    do_sample: bool = False
    seed: int = 1
    h_e1_results_path: str = "data/h_e1_results.json"
    mbpp_dataset_name: str = "google-research-datasets/mbpp"
    task_id_min: int = 11
    task_id_max: int = 510
    execution_timeout: int = 10
    results_dir: str = "results"
    figures_dir: str = "figures"
    output_json: str = "results/repair_results.json"     # <- H-M3 reads this file
    output_metrics: str = "results/metrics.yaml"
    output_posthoc: str = "results/posthoc.yaml"
    checkpoint_path: str = "results/checkpoint.json"
    anova_alpha: float = 0.05
    eta_squared_threshold: float = 0.02
```

H-M3 reads `RepairConfig.output_json` ("results/repair_results.json") as its data source.
H-M3 does NOT inherit `RepairConfig` — it defines its own `AnalysisConfig`.
Key data fields confirmed in H-M1 output: `task_id` (int), `granularity` (str: "G0"-"G4"), `success` (bool).

**Verified from**: `/h-m1/code/config.py` (actual implementation)

---

## A-1: Project Setup [Complexity: 5]

No config subtasks allocated. Config defined below covers all setup needs.

---

## A-8: Visualizations [Complexity: 9, Budget: 2 subtasks]

Applied: Standard matplotlib/seaborn figure defaults

### Configuration (Python Dataclass)

```python
# h-m3/code/config.py
from dataclasses import dataclass

H_M1_RESULTS_PATH: str = "../h-m1/code/results/repair_results.json"


@dataclass
class AnalysisConfig:
    # Data source (path relative to h-m3/code/)
    h_m1_results_path: str = H_M1_RESULTS_PATH

    # Statistical thresholds
    equivalence_margin: float = 0.02  # Non-standard: matches hypothesis "G4 <= G3 + 2%"
    alpha: float = 0.05
    confidence: float = 0.95

    # Output paths
    results_dir: str = "results"
    figures_dir: str = "figures"
    output_contingency: str = "results/contingency_table.json"
    output_stats: str = "results/statistical_tests.yaml"
    output_metrics: str = "results/metrics.yaml"

    # Visualization settings
    fig_width: int = 8
    fig_height: int = 6
    dpi: int = 150  # Non-standard: publication quality without excessive file size
    color_g3: str = "#2ecc71"
    color_g4: str = "#3498db"
    color_threshold: str = "red"
    output_gate_comparison: str = "figures/gate_comparison.png"
    output_contingency_heatmap: str = "figures/contingency_heatmap.png"
    output_confidence_interval: str = "figures/confidence_interval.png"
    output_granularity_curve: str = "figures/granularity_curve.png"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Core Figures | `plot_gate_comparison`, `plot_contingency_heatmap`, `plot_confidence_interval` using fig_width/height/dpi/color fields |
| C-8-2 | Granularity Curve + Wrapper | `plot_granularity_curve` for G0-G4 non-monotonic pattern + `generate_all_figures` orchestrator |

---

## YAML Output Schemas

```yaml
# results/statistical_tests.yaml
mcnemar:
  statistic: float
  pvalue: float
  significant: bool
  interpretation: str
tost:
  g3_rate: float
  g4_rate: float
  difference: float
  margin: float          # = equivalence_margin (0.02)
  p_lower: float
  p_upper: float
  tost_pvalue: float
  equivalent: bool
  interpretation: str
confidence_interval:
  point_estimate: float
  ci_lower: float
  ci_upper: float
  confidence: float      # = 0.95
  interpretation: str

# results/metrics.yaml
gate:
  g3_rate: float
  g4_rate: float
  difference: float
  margin: float
  within_margin: bool
  mcnemar_pvalue: float
  gate_passed: bool
  reason: str
```
