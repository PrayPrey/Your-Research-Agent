# Configuration: H-E1 — Permutation Orbit Non-Triviality Analysis

**Applied**: dataclass-config pattern (single ExperimentConfig, YAML-mapped, green-field)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## ExperimentConfig (`h-e1/code/config.py`)

```python
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExperimentConfig:
    # Paths
    data_dir: Path = Path("data/model_zoo")
    results_dir: Path = Path("results")
    figures_dir: Path = Path("figures")

    # Zoo settings
    zoo_name: str = "mnist_cnn"

    # Reproducibility
    seed: int = 42

    # Sampling
    n_per_decile: int = 50
    n_deciles: int = 10

    # Gate thresholds
    acc_threshold: float = 0.01
    cosine_dist_threshold: float = 0.1
    orbit_proportion_gate: float = 0.05

    # Verification
    bn_verify_sample_size: int = 5

    def __post_init__(self):
        self.data_dir = Path(self.data_dir)
        self.results_dir = Path(self.results_dir)
        self.figures_dir = Path(self.figures_dir)

    @property
    def n_pairs(self) -> int:
        return self.n_per_decile * self.n_deciles
```

---

## YAML Configuration Schema (`config.yaml`)

```yaml
# H-E1 Experiment Configuration
data_dir: "data/model_zoo"
results_dir: "results"
figures_dir: "figures"

zoo_name: "mnist_cnn"

seed: 42

n_per_decile: 50
n_deciles: 10

acc_threshold: 0.01
cosine_dist_threshold: 0.1
orbit_proportion_gate: 0.05

bn_verify_sample_size: 5
```

---

## A-6: Visualization Configuration [Complexity: 9, Budget: 2 subtasks]

**Applied**: matplotlib-figure-config pattern

```python
@dataclass
class VisualizationConfig:
    dpi: int = 150
    output_format: str = "png"
    colormap: str = "viridis"

    # gate_metrics.png — bar chart of gate pass/fail metrics
    gate_metrics_figsize: tuple = (8, 5)
    gate_metrics_bar_color_pass: str = "#2ecc71"
    gate_metrics_bar_color_fail: str = "#e74c3c"

    # cosine_dist_histogram.png — distribution of cosine distances
    cosine_hist_figsize: tuple = (8, 5)
    cosine_hist_bins: int = 50
    cosine_hist_color: str = "#3498db"
    cosine_hist_threshold_linecolor: str = "#e74c3c"

    # acc_vs_distance.png — scatter of accuracy diff vs cosine distance
    scatter_figsize: tuple = (8, 6)
    scatter_alpha: float = 0.4
    scatter_point_size: int = 10
    scatter_color: str = "#8e44ad"

    # per_decile_proportion.png — orbit proportion per accuracy decile
    decile_figsize: tuple = (10, 5)
    decile_bar_color: str = "#1abc9c"
    decile_gate_linecolor: str = "#e74c3c"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Figure Layout Config | Implement VisualizationConfig dataclass with per-figure size, DPI, color settings for all 4 figures |
| C-6-2 | Figure Save Utility | Implement save_figure(fig, name, cfg) that saves PNG at cfg.dpi to cfg.figures_dir |

---

## Results Output Schema (`h_e1_results.yaml`)

```yaml
hypothesis_id: "H-E1"
date: "2026-05-05"
seed: 42
zoo_name: "mnist_cnn"
n_pairs: 500

gate:
  passed: true           # bool: both bn_free AND orbit_proportion pass
  bn_free: true          # bool: no BatchNorm layers found in sampled models
  orbit_proportion: 0.12 # float: fraction of pairs meeting both thresholds
  threshold: 0.05        # float: orbit_proportion_gate value used

statistics:
  mean_cosine_dist: 0.35
  std_cosine_dist: 0.18
  per_decile_proportions:
    - decile: 0
      proportion: 0.10
    - decile: 1
      proportion: 0.12
    # ... (10 entries total, one per decile)

metadata:
  acc_threshold: 0.01
  cosine_dist_threshold: 0.1
  n_per_decile: 50
  n_deciles: 10
  bn_verify_sample_size: 5
```
