# Configuration: h-e1

**Hypothesis:** Pairwise failure correlations exceed random chance
**Type:** EXISTENCE (PoC)
**Date:** 2026-08-28

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass

---

## Configuration Schema

### Format: Python Dataclass

```python
from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path


@dataclass
class DataConfig:
    """Benchmark data collection parameters."""
    benchmarks: List[str] = None
    min_models: int = 15
    size_strata: Dict[str, str] = None
    data_dir: Path = Path("./data/h-e1")
    
    def __post_init__(self):
        if self.benchmarks is None:
            self.benchmarks = ["truthfulqa", "advbench", "bold"]
        if self.size_strata is None:
            self.size_strata = {
                "small": "<1B",
                "medium": "1-10B",
                "large": ">10B"
            }


@dataclass
class StatisticalConfig:
    """Statistical analysis parameters."""
    alpha: float = 0.01
    effect_size_threshold: float = 0.3
    correction_method: str = "bonferroni"
    # Bonferroni adjusted threshold for 3 comparisons
    alpha_corrected: float = 0.0033


@dataclass
class VisualizationConfig:
    """Visualization parameters."""
    figures_dir: Path = Path("./figures/h-e1")
    color_scheme: str = "RdBu_r"
    figure_dpi: int = 300
    annotation_style: Dict[str, any] = None
    
    def __post_init__(self):
        if self.annotation_style is None:
            self.annotation_style = {
                "fontsize": 10,
                "fmt": ".2f",
                "sig_marker": "*"
            }


@dataclass
class ExperimentConfig:
    """Master configuration for h-e1 statistical analysis."""
    data: DataConfig = None
    stats: StatisticalConfig = None
    viz: VisualizationConfig = None
    results_dir: Path = Path("./results/h-e1")
    
    def __post_init__(self):
        if self.data is None:
            self.data = DataConfig()
        if self.stats is None:
            self.stats = StatisticalConfig()
        if self.viz is None:
            self.viz = VisualizationConfig()
```

---

## Usage

```python
# Load default config
config = ExperimentConfig()

# Access parameters
print(config.data.benchmarks)  # ["truthfulqa", "advbench", "bold"]
print(config.stats.alpha)  # 0.01
print(config.viz.figure_dpi)  # 300

# Override specific values
custom_config = ExperimentConfig(
    data=DataConfig(min_models=20),
    stats=StatisticalConfig(alpha=0.05)
)
```

---

## Parameter Reference

### DataConfig

| Parameter | Default | Valid Range | Description |
|-----------|---------|-------------|-------------|
| benchmarks | ["truthfulqa", "advbench", "bold"] | Any benchmark list | Target benchmarks for correlation analysis |
| min_models | 15 | ≥10 | Minimum models required (5 per stratum) |
| size_strata | {small: <1B, medium: 1-10B, large: >10B} | Custom dict | Model size stratification |
| data_dir | ./data/h-e1 | Valid path | Input data directory |

### StatisticalConfig

| Parameter | Default | Valid Range | Description |
|-----------|---------|-------------|-------------|
| alpha | 0.01 | (0, 0.1] | Significance threshold before correction |
| effect_size_threshold | 0.3 | [0, 1] | Minimum Spearman r for medium effect |
| correction_method | "bonferroni" | bonferroni, holm, fdr | Multiple comparison correction |
| alpha_corrected | 0.0033 | Computed | α / n_comparisons (3 pairs) |

### VisualizationConfig

| Parameter | Default | Valid Range | Description |
|-----------|---------|-------------|-------------|
| figures_dir | ./figures/h-e1 | Valid path | Output directory for figures |
| color_scheme | "RdBu_r" | Matplotlib colormaps | Diverging colormap for heatmaps |
| figure_dpi | 300 | [72, 600] | Resolution for saved figures |
| annotation_style | {fontsize: 10, fmt: ".2f", sig_marker: "*"} | Dict | Heatmap annotation parameters |

### ExperimentConfig

| Parameter | Default | Valid Range | Description |
|-----------|---------|-------------|-------------|
| results_dir | ./results/h-e1 | Valid path | Output directory for JSON results |

---

## Rationale for Non-Standard Values

**alpha = 0.01** (not 0.05): Stricter threshold for MUST_WORK gate - minimizes false discovery risk.

**effect_size_threshold = 0.3**: Cohen's convention for "medium" effect size. Values <0.3 may lack practical significance.

**alpha_corrected = 0.0033**: Bonferroni correction for 3 pairwise comparisons (0.01 / 3 ≈ 0.0033).

---

## File Paths

```python
# Expected file structure
{config.data.data_dir}/benchmark_scores.csv          # Input: Raw benchmark data
{config.results_dir}/correlation_results.json        # Output: Numerical results
{config.viz.figures_dir}/correlation_matrix.png      # Output: Heatmap
{config.viz.figures_dir}/scatter_*.png               # Output: Scatter plots
{config.viz.figures_dir}/stratified_comparison.png   # Output: Stratum comparison
{config.viz.figures_dir}/gate_metrics.png            # Output: Gate chart
```

---

## Validation

```python
def validate_config(config: ExperimentConfig) -> None:
    """Validate configuration parameters."""
    assert len(config.data.benchmarks) == 3, "Must have exactly 3 benchmarks"
    assert config.data.min_models >= 10, "Need ≥10 models for statistical power"
    assert 0 < config.stats.alpha <= 0.1, "Alpha must be in (0, 0.1]"
    assert 0 <= config.stats.effect_size_threshold <= 1, "Effect size in [0, 1]"
    assert config.stats.correction_method in ["bonferroni", "holm", "fdr"]
    assert config.viz.figure_dpi >= 72, "DPI must be ≥72"
```

---

## Dependencies

```txt
scipy>=1.7.0
statsmodels>=0.13.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
numpy>=1.21.0
```

---

*Generated by Phase 3 Configuration Agent*
*Source: 02c_experiment_brief.md, 03_prd.md*
