# Config: H-M2

**hypothesis_id:** h-m2
**hypothesis_type:** MECHANISM
**gate:** SHOULD_WORK
**generated_at:** 2026-03-16

Applied: Standard Python dataclass pattern (evaluation-continuation, no training config needed)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from base code via Read tool (Serena project not active — used direct file read)
**Config Files Found**: `h-m1/code/src/config.py`
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual h-m1 Code)

```python
# From: docs/youra_research/20260316_wsl/h-m1/code/src/config.py (ACTUAL CODE)
@dataclass
class DataConfig:
    dataset_url: str = "https://storage.googleapis.com/gresearch/dnn_predict_accuracy/small_mnist_networks.pkl"
    local_path: str = "data/unterthiner_mnist_zoo.pkl"
    min_samples: int = 500
    train_ratio: float = 0.8
    batch_size: int = 64
    seed: int = 42
    severity_levels: List[float] = field(default_factory=lambda: [0.0, 0.25, 0.5, 1.0])

@dataclass
class ExperimentConfig:
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456])
    encoder_names: List[str] = field(default_factory=lambda: list(ENCODER_NAMES))
    lr: float = 1e-3
    betas: tuple = (0.9, 0.999)
    weight_decay: float = 1e-4
    scheduler: str = "CosineAnnealingLR"
    T_max: int = 100
    eta_min: float = 1e-5
    batch_size: int = 64
    n_epochs: int = 100
    nan_recovery_lr: float = 1e-4
    n_bootstrap: int = 10000
    alpha: float = 0.05
    severity_levels: List[float] = field(default_factory=lambda: [0.0, 0.25, 0.5, 1.0])
    # ... additional run flags and paths

@dataclass
class GateConfig:
    nft_delta_rho_threshold: float = 0.02
    mediation_delta_r2_threshold: float = 0.10
    aug_partial_delta_rho_min: float = 0.05
    aug_partial_delta_rho_max: float = 0.10
    flat_mlp_delta_rho_threshold: float = 0.10
    gate_result_path: str = "results/gate_result.json"

@dataclass
class VizConfig:
    figures_dir: str = "figures/"
    dpi: int = 150
    fig_format: str = "png"
    # figsize tuples, style, palette, gate_line_* fields
    style: str = "seaborn-v0_8-whitegrid"
    palette: str = "tab10"
```

**Verified from**: `docs/youra_research/20260316_wsl/h-m1/code/src/config.py` (actual implementation)

**Key verified field names**:
- `train_ratio` (not `test_ratio`) in DataConfig
- `lr` (not `learning_rate`) in ExperimentConfig
- `n_bootstrap` in ExperimentConfig = 10000
- `severity_levels` shared in DataConfig and ExperimentConfig

---

## A-2: Checkpoint Verification [Complexity: 8, Budget: 1 subtask]

Applied: Standard dataclass pattern

### Configuration

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class CheckpointConfig:
    base_path: str = "docs/youra_research/20260316_wsl/h-m1/code/checkpoints"
    # NOTE: '+' in encoder names maps to 'plus' in checkpoint filenames
    encoder_names: List[str] = field(default_factory=lambda: [
        "flat-MLP",
        "flat-MLPplusaug",
        "flat-MLPpluscanon",
        "NFT-base",
    ])
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456])

    def get_checkpoint_path(self, encoder_name: str, seed: int) -> str:
        return f"{self.base_path}/{encoder_name}_seed{seed}.pt"

    def all_checkpoint_paths(self) -> List[str]:
        return [
            self.get_checkpoint_path(enc, seed)
            for enc in self.encoder_names
            for seed in self.seeds
        ]
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | CheckpointConfig | Dataclass for 12 checkpoint file paths with `plus` naming convention |

---

## A-3: Data & Split Setup [Complexity: 9, Budget: 2 subtasks]

Applied: Standard dataclass pattern

### Configuration

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class HM2DataConfig:
    cache_path: str = ".data_cache/datasets/unterthiner_mnist_zoo/zoo_enriched.pkl"
    split_seed: int = 42          # MUST match H-M1 for comparable Δρ values
    test_ratio: float = 0.2       # identical to H-M1 train_ratio=0.8
    encoders_to_eval: List[str] = field(default_factory=lambda: [
        "flat-MLP",
        "flat-MLP+aug",
        "flat-MLP+canon",
        "NFT-base",
    ])
    severity_levels: List[float] = field(default_factory=lambda: [0.0, 0.25, 0.5, 1.0])
    batch_size: int = 64
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | HM2DataConfig | Dataclass for data loading, split, and encoder selection |
| C-3-2 | severity_config | `severity_levels = [0.0, 0.25, 0.5, 1.0]` embedded in HM2DataConfig |

---

## A-7: Visualization Suite [Complexity: 13, Budget: 4 subtasks]

Applied: Standard dataclass pattern

### Configuration

```python
from dataclasses import dataclass, field
from typing import List, Tuple, Dict

# Color mapping per encoder (verified encoder names from h-m1 ENCODER_NAMES)
ENCODER_COLORS: Dict[str, str] = {
    "flat-MLP":        "red",
    "flat-MLP+aug":    "orange",
    "flat-MLP+canon":  "green",
    "NFT-base":        "blue",
}

# Threshold lines for gate_metrics_comparison figure
THRESHOLD_LINES: List[float] = [0.02, 0.03, 0.05]

@dataclass
class FigureConfig:
    figsize: Tuple[int, int] = (10, 6)
    dpi: int = 150
    colors: Dict[str, str] = field(default_factory=lambda: dict(ENCODER_COLORS))
    threshold_lines: List[float] = field(default_factory=lambda: list(THRESHOLD_LINES))
    output_dir: str = "docs/youra_research/20260316_wsl/h-m2/figures"
    style: str = "seaborn-v0_8-whitegrid"
    fig_format: str = "png"

    # Per-figure output filenames
    gate_metrics_comparison: str = "gate_metrics_comparison.png"
    delta_rho_heatmap: str = "delta_rho_heatmap.png"
    rho_degradation_curves: str = "rho_degradation_curves.png"
    threeway_ranking_scatter: str = "threeway_ranking_scatter.png"
    bootstrap_distributions: str = "bootstrap_distributions.png"

    # Heatmap-specific: blue=robust (low Δρ), red=degraded (high Δρ)
    heatmap_cmap: str = "RdBu_r"
    heatmap_figsize: Tuple[int, int] = (10, 5)
    bootstrap_figsize: Tuple[int, int] = (10, 5)
```

### YAML Schema for Visualization Config

```yaml
# h-m2/figures_config.yaml
figure_config:
  figsize: [10, 6]
  dpi: 150
  output_dir: "docs/youra_research/20260316_wsl/h-m2/figures"
  style: "seaborn-v0_8-whitegrid"
  fig_format: "png"

  colors:
    flat-MLP: "red"
    flat-MLP+aug: "orange"
    flat-MLP+canon: "green"
    NFT-base: "blue"

  threshold_lines: [0.02, 0.03, 0.05]

  figures:
    gate_metrics_comparison: "gate_metrics_comparison.png"
    delta_rho_heatmap: "delta_rho_heatmap.png"
    rho_degradation_curves: "rho_degradation_curves.png"
    threeway_ranking_scatter: "threeway_ranking_scatter.png"
    bootstrap_distributions: "bootstrap_distributions.png"

  heatmap_cmap: "RdBu_r"
  heatmap_figsize: [10, 5]
  bootstrap_figsize: [10, 5]
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | FigureConfig | Dataclass with figsize, dpi, output_dir, per-figure filenames |
| C-7-2 | fig_yamls | YAML schema for all 5 figure configs |
| C-7-3 | color_scheme | ENCODER_COLORS dict: flat-MLP=red, +aug=orange, +canon=green, NFT=blue |
| C-7-4 | threshold_config | THRESHOLD_LINES=[0.02, 0.03, 0.05] for gate_metrics_comparison |

---

## A-8: Results Reporting [Complexity: 7, Budget: 1 subtask]

Applied: Standard dataclass pattern

### Configuration

```python
from dataclasses import dataclass

@dataclass
class ResultsConfig:
    output_dir: str = "docs/youra_research/20260316_wsl/h-m2/results"
    json_file: str = "hm2_results.json"
    csv_file: str = "hm2_eval_df.csv"

    def json_path(self) -> str:
        return f"{self.output_dir}/{self.json_file}"

    def csv_path(self) -> str:
        return f"{self.output_dir}/{self.csv_file}"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | ResultsConfig | Dataclass for output paths: hm2_results.json and hm2_eval_df.csv |

---

## A-9: Integration Test [Complexity: 9, Budget: 2 subtasks]

Applied: Standard dataclass pattern

### Configuration

```python
from dataclasses import dataclass, field
from typing import Dict

# Expected values from H-M1 (PASS, verified) for consistency check
HM1_EXPECTED: Dict[str, float] = {
    "nft_delta_rho_approx": 4.71e-07,
    "aug_delta_rho_approx": 0.2239,
}

@dataclass
class TestConfig:
    tolerance: float = 0.01       # ±0.01 from H-M1 reported values
    fast_mode: bool = True         # reduces bootstrap n for CI smoke test
    n_bootstrap_fast: int = 100    # fast_mode bootstrap count (vs 10,000 full)
    seed: int = 42
    expected_nft_delta_rho: float = 4.71e-07
    expected_aug_delta_rho: float = 0.2239
    # Consistency thresholds (from FR-3.4)
    nft_consistency_max: float = 0.03    # NFT-base Δρ <= H-M1 value + tolerance
    aug_consistency_min: float = 0.21    # aug Δρ >= H-M1 value - tolerance
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-9-1 | TestConfig | Dataclass with tolerance=0.01, fast_mode=True, n_bootstrap_fast=100 |
| C-9-2 | expected_values | HM1_EXPECTED dict: nft=4.71e-07, aug=0.2239 embedded in TestConfig |

---

## Summary

| Task | Config Class | Subtasks | Budget Used |
|------|-------------|----------|-------------|
| A-2 | CheckpointConfig | C-2-1 | 1/1 |
| A-3 | HM2DataConfig | C-3-1, C-3-2 | 2/2 |
| A-7 | FigureConfig + ENCODER_COLORS + THRESHOLD_LINES | C-7-1 to C-7-4 | 4/4 |
| A-8 | ResultsConfig | C-8-1 | 1/1 |
| A-9 | TestConfig + HM1_EXPECTED | C-9-1, C-9-2 | 2/2 |
| **Total** | | | **10/10** |
