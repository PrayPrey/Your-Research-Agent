# Config: H-M4 (Traditional Benchmark Persistence with Reduced Dominance)

**Applied**: Statistical experiment config (constants module, no ML hyperparameters) — Archon KB search returned no directly applicable DL config pattern; used standard PyTorch/scientific-computing config defaults.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (no base hypothesis code, no existing codebase to analyze)
**Config Files Found**: None
**Pattern Used**: Hardcoded dict (module-level constants in `config.py`)

---

## A-1: Config setup [Complexity: 4, Budget: 4]

**Applied**: Flat constants dict — statistical analysis, no model hyperparameters.

### Configuration (Hardcoded Dict / Module Constants)

```python
# config.py

TRADITIONAL_BENCHMARKS: list[str] = ["imagenet", "imagenet-1k", "cifar-10", "cifar-100"]

SPLIT_DATE: str = "2020-01"
DATE_RANGE: tuple[str, str] = ("2018-01", "2024-12")

# Gate thresholds
COUNT_RATIO_BOUNDS: tuple[float, float] = (0.8, 1.2)  # ±20% count stability
PER_BENCHMARK_STABILITY_BOUND: float = 0.30  # ±30%, P2 secondary metric

SIGNIFICANCE_ALPHA: float = 0.05

SEED: int = 42

HF_DATASETS = {
    "eval_tables": "pwc-archive/evaluation-tables",
    "datasets_meta": "pwc-archive/datasets",
}

OUTPUT_DIR: str = "figures/"
RESULTS_PATH: str = "code/results.yaml"
```

---

## A-8: Additional visualizations [Complexity: 10, Budget: 10]

**Applied**: Matplotlib fixed figure-size/color config — standard defaults, no tuning needed.

### Configuration (Hardcoded Dict)

```python
# visualize config (in config.py)

FIGURE_SIZE: tuple[int, int] = (10, 6)
DPI: int = 150

COLORS = {
    "traditional": "#d62728",   # red
    "emergent": "#1f77b4",      # blue
    "pre_2020": "#7f7f7f",      # gray
    "post_2020": "#2ca02c",     # green
    "split_line": "#000000",    # black dashed vertical marker
}

PER_BENCHMARK_COLORS = {
    "imagenet": "#1f77b4",
    "imagenet-1k": "#ff7f0e",
    "cifar-10": "#2ca02c",
    "cifar-100": "#d62728",
}

FIGURE_FILES = {
    "gate_metrics": "gate_metrics.png",
    "share_timeseries": "share_timeseries.png",
    "stacked_area": "stacked_area.png",
    "per_benchmark": "per_benchmark.png",
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| C-8-1 | Timeseries + stacked area | `plot_share_timeseries` (split marker) and `plot_stacked_area` (traditional vs emergent counts) |
| C-8-2 | Per-benchmark breakdown | `plot_per_benchmark` line chart using `PER_BENCHMARK_COLORS` |

---

## Output Schema: results.yaml

```yaml
hypothesis_id: H-M4
gate_pass: true            # bool, FR-4.3
share_decreased: true      # bool, FR-4.1
counts_stable: true        # bool, FR-4.2
count_ratio: 1.05          # float, post/pre count mean ratio
pre_2020_mean_share: 0.42
post_2020_mean_share: 0.18
pre_2020_mean_count: 1200.0
post_2020_mean_count: 1260.0
mann_whitney:
  statistic: 1234.5
  p_value: 0.001
  significant: true        # p < SIGNIFICANCE_ALPHA
per_benchmark_stability:
  imagenet: 0.05
  imagenet-1k: 0.12
  cifar-10: -0.08
  cifar-100: 0.02
figures:
  - figures/gate_metrics.png
  - figures/share_timeseries.png
  - figures/stacked_area.png
  - figures/per_benchmark.png
```
