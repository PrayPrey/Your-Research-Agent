# Config: H-M3 (Researcher Attention Shift)

**Applied**: Standard PyTorch/dataclass config defaults (no specific KB pattern matched — general dataclass config used)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass (Python)

---

## config.py

```python
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class BenchmarkConfig:
    emergent: list[str] = field(default_factory=lambda: [
        "MMLU", "BIG-Bench", "HumanEval", "GSM8K", "MATH",
        "ARC", "HellaSwag", "WinoGrande", "TruthfulQA", "LAMBADA",
    ])
    traditional: list[str] = field(default_factory=lambda: [
        "ImageNet", "CIFAR-10", "CIFAR-100", "MNIST",
        "SQuAD", "GLUE", "CoNLL", "Penn Treebank",
    ])
    time_range: tuple[str, str] = ("2018-01", "2024-12")
    split_date: str = "2021-01"
    ablation_splits: list[str] = field(default_factory=lambda: ["2020-01", "2021-01", "2022-01"])

    def __post_init__(self):
        overlap = set(self.emergent) & set(self.traditional)
        if overlap:
            raise ValueError(f"Benchmark(s) in both categories: {overlap}")


@dataclass
class DataConfig:
    retries: int = 3
    backoff_base_seconds: float = 2.0
    pwc_api_base_url: str = "https://paperswithcode.com/api/v1/"
    hf_fallback_dataset: str = "pwc-archive/datasets"
    seed: int = 42


@dataclass
class AnalysisConfig:
    chi_square_alpha: float = 0.05
    period_labels: tuple[str, str] = ("pre_2021", "post_2021")


@dataclass
class VisualizationConfig:
    figsize_default: tuple[int, int] = (10, 6)
    figsize_heatmap: tuple[int, int] = (14, 8)
    dpi: int = 150
    style: str = "seaborn-v0_8-whitegrid"
    palette_emergent: str = "#d62728"    # red
    palette_traditional: str = "#1f77b4"  # blue
    heatmap_top_n: int = 20
    output_dir: str = "figures/"
    file_format: Literal["png", "pdf", "svg"] = "png"


@dataclass
class ExperimentConfig:
    benchmarks: BenchmarkConfig = field(default_factory=BenchmarkConfig)
    data: DataConfig = field(default_factory=DataConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    viz: VisualizationConfig = field(default_factory=VisualizationConfig)
    results_path: str = "results.json"
```

**Non-standard**: `palette_emergent`/`palette_traditional` fixed hex colors (not seaborn default) to ensure consistent red/blue coding across all 5 figures.

---

## YAML Schema (external override, optional)

```yaml
benchmarks:
  emergent: [MMLU, BIG-Bench, HumanEval, GSM8K, MATH, ARC, HellaSwag, WinoGrande, TruthfulQA, LAMBADA]
  traditional: [ImageNet, CIFAR-10, CIFAR-100, MNIST, SQuAD, GLUE, CoNLL, Penn Treebank]
  time_range: ["2018-01", "2024-12"]
  split_date: "2021-01"
  ablation_splits: ["2020-01", "2021-01", "2022-01"]

data:
  retries: 3
  backoff_base_seconds: 2.0

analysis:
  chi_square_alpha: 0.05

viz:
  figsize_default: [10, 6]
  dpi: 150
  heatmap_top_n: 20
  output_dir: "figures/"
```

Loaded via `yaml.safe_load` + `ExperimentConfig(**dict)` merge (FR-2.3 extensible categorization).

---

## A-8: Visualization Pipeline [Complexity: 10, Budget: 10]

**Applied**: Standard matplotlib/seaborn config defaults

Uses `VisualizationConfig` above. All 5 plot functions take `out_path` built as `f"{viz.output_dir}/{name}.{viz.file_format}"`.

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-8-1 | Style setup + gate/timeline plots | Apply `viz.style`, implement `plot_gate_metrics` (bar) and `plot_share_timeline` (line), use emergent/traditional palette |
| C-8-2 | Area + heatmap plots | `plot_absolute_counts` (stacked area, figsize_default) and `plot_benchmark_heatmap` (figsize_heatmap, top `heatmap_top_n` by year) |
| C-8-3 | Residuals plot + save utility | `plot_chi_square_residuals`, shared `save_fig(fig, out_path, dpi)` helper writing to `viz.output_dir` |
