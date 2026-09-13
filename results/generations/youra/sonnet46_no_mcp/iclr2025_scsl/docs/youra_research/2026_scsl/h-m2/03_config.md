# Config: H-M2
# Feature Complexity Measurement — Spurious vs. Core Feature Analysis

Applied: dataclass composition pattern with YAML loading
Applied: frozen backbone inference-only config pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-M1 is base, but code not yet generated)
**Status**: H-M1 code not yet generated (Phase 4 pending) — designing new config schema consistent with H-M1 architecture spec
**Config Files Found**: `h-m1/03_config.md` (spec only, no actual code)
**Pattern Used**: dataclass

**Note**: H-M1 03_config.md shows `batch_size=64` for training; H-M2 uses `batch_size=256` for inference (no gradient, larger batch safe). Seeds pattern `[42, 123, 456]` is H-M2-specific (different from H-M1 `[1, 2, 3]`).

---

## Inherited Configuration (Base Hypothesis H-M1)

### What is inherited (from H-M1 03_architecture.md pattern):

- Dataset path pattern: `.data_cache/datasets/{dataset}` (consistent with H-M1 `data_root` convention)
- `num_workers: 4`
- `results_dir` / `figures_dir` top-level fields in ExperimentConfig
- `load_config(path) -> ExperimentConfig` signature with `yaml.safe_load`

### What differs from H-M1:

- No training loop — inference-only (no `TrainConfig`, `lr`, `momentum`, `weight_decay`, `epochs`)
- `batch_size=256` (H-M2 inference; H-M1 training used 64)
- Seeds `[42, 123, 456]` (H-M2 statistical replication; H-M1 used `[1, 2, 3]`)
- Adds `MetricConfig`, `ModelConfig`, `FigureConfig` (not in H-M1)
- Supports two datasets simultaneously (Waterbirds + CelebA)

**Verified from**: `h-m1/03_architecture.md` and `h-m1/03_config.md` (actual code not yet generated)

---

## A-10: Visualization [Complexity: 11, Budget: 2 subtasks]

Applied: dataclass with enum-validated string fields pattern

### Configuration

```python
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class FigureConfig:
    figures_dir: str = "./figures"
    dpi: int = 150
    format: str = "png"              # enum: "png" | "pdf" | "svg"
    n_fft_examples: int = 4
    pca_method: str = "pca"          # enum: "pca" | "tsne"
    colormap: str = "viridis"
    figsize: tuple = (10, 6)
```

### YAML Schema (configs/experiment.yaml — visualization section)

```yaml
visualization:
  figures_dir: ./figures
  dpi: 150
  format: png
  n_fft_examples: 4
  pca_method: pca
  colormap: viridis
  figsize: [10, 6]
```

### Validation Rules

- `dpi`: 72 <= dpi <= 600
- `format`: must be one of `["png", "pdf", "svg"]`
- `pca_method`: must be one of `["pca", "tsne"]`
- `n_fft_examples`: >= 1
- `figsize`: tuple/list of length 2, both positive

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-10-1 | FigureConfig dataclass | Define FigureConfig with figures_dir, dpi, format, n_fft_examples, pca_method, colormap, figsize |
| C-10-2 | Visualization validation | Implement validate_figure_config() checking dpi range, format enum, pca_method enum |

---

## A-5: ResNet-50 Feature Extractor [Complexity: 10, Budget: 2 subtasks]

Applied: frozen backbone inference config pattern

### Configuration

```python
from dataclasses import dataclass

@dataclass
class ModelConfig:
    backbone: str = "resnet50"
    pretrained: bool = True
    feature_layer: str = "layer4"    # Non-standard: layer4 = last conv block before avg-pool; outputs (N,2048,7,7) -> avg-pooled to (N,2048)
    feature_dim: int = 2048
    frozen: bool = True              # Non-standard: all params frozen, no gradient tracking (inference-only experiment)
    device: str = "cuda:0"
```

### YAML Schema (configs/experiment.yaml — model section)

```yaml
model:
  backbone: resnet50
  pretrained: true
  feature_layer: layer4
  feature_dim: 2048
  frozen: true
  device: cuda:0
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | ModelConfig dataclass | Define ModelConfig with backbone, pretrained, feature_layer, feature_dim, frozen, device |
| C-5-2 | Feature extraction rationale | batch_size=256 (no gradient, larger batch safe for inference); layer4 (2048-dim semantic features per Geirhos 2019); frozen=True (measuring existing representations, not fine-tuning) |

---

## A-11: Experiment Orchestrator [Complexity: 10, Budget: 2 subtasks]

Applied: dataclass composition with default_factory and YAML parsing

### Configuration

```python
from dataclasses import dataclass, field
from typing import List
import yaml
import os


@dataclass
class DataConfig:
    waterbirds_root: str = ".data_cache/datasets/waterbirds"
    celeba_root: str = ".data_cache/datasets/celeba"
    patch_size: int = 64
    batch_size: int = 256
    num_workers: int = 4
    celeba_samples_per_group: int = 5000
    use_segmentation_masks: bool = True


@dataclass
class MetricConfig:
    n_samples_list: List[int] = field(default_factory=lambda: [50, 100, 200, 500, 1000, 2000])
    seeds: List[int] = field(default_factory=lambda: [42, 123, 456])
    alpha: float = 0.05
    min_patches_per_class: int = 100
    logistic_c: float = 1.0
    logistic_max_iter: int = 1000
    bonferroni_n_tests: int = 6      # Non-standard: 3 metrics x 2 datasets = 6 simultaneous tests


@dataclass
class ModelConfig:
    backbone: str = "resnet50"
    pretrained: bool = True
    feature_layer: str = "layer4"
    feature_dim: int = 2048
    frozen: bool = True
    device: str = "cuda:0"


@dataclass
class FigureConfig:
    figures_dir: str = "./figures"
    dpi: int = 150
    format: str = "png"
    n_fft_examples: int = 4
    pca_method: str = "pca"
    colormap: str = "viridis"
    figsize: tuple = (10, 6)


@dataclass
class ExperimentConfig:
    data: DataConfig = field(default_factory=DataConfig)
    metric: MetricConfig = field(default_factory=MetricConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    visualization: FigureConfig = field(default_factory=FigureConfig)
    results_dir: str = "./results"
    hypothesis_id: str = "H-M2"
    gate_min_metrics: int = 2        # Non-standard: gate requires >= 2/3 metrics to pass
    gate_n_total_metrics: int = 3


def validate_config(cfg: ExperimentConfig) -> None:
    """Raises ValueError on invalid config."""
    # Path existence (data)
    for path_attr, label in [
        (cfg.data.waterbirds_root, "waterbirds_root"),
        (cfg.data.celeba_root, "celeba_root"),
    ]:
        if not os.path.exists(path_attr):
            raise ValueError(f"{label} not found: {path_attr}")
    # Device availability
    if cfg.model.device.startswith("cuda"):
        import torch
        if not torch.cuda.is_available():
            raise ValueError(f"CUDA device requested but not available: {cfg.model.device}")
    # n_samples_list must be sorted ascending
    if cfg.metric.n_samples_list != sorted(cfg.metric.n_samples_list):
        raise ValueError("metric.n_samples_list must be sorted ascending")
    # seeds must be unique
    if len(cfg.metric.seeds) != len(set(cfg.metric.seeds)):
        raise ValueError("metric.seeds must be unique")
    # visualization enums
    if cfg.visualization.format not in ("png", "pdf", "svg"):
        raise ValueError(f"visualization.format must be png|pdf|svg, got: {cfg.visualization.format}")
    if cfg.visualization.pca_method not in ("pca", "tsne"):
        raise ValueError(f"visualization.pca_method must be pca|tsne, got: {cfg.visualization.pca_method}")
    if not (72 <= cfg.visualization.dpi <= 600):
        raise ValueError(f"visualization.dpi must be 72-600, got: {cfg.visualization.dpi}")


def load_config(config_path: str) -> ExperimentConfig:
    with open(config_path, "r") as f:
        raw = yaml.safe_load(f)

    data_cfg = DataConfig(**raw.get("data", {}))
    metric_cfg = MetricConfig(**raw.get("metric", {}))
    model_cfg = ModelConfig(**raw.get("model", {}))
    viz_cfg_raw = raw.get("visualization", {})
    if "figsize" in viz_cfg_raw:
        viz_cfg_raw["figsize"] = tuple(viz_cfg_raw["figsize"])
    viz_cfg = FigureConfig(**viz_cfg_raw)

    # Environment variable overrides
    device = os.environ.get("CUDA_VISIBLE_DEVICES")
    if device is not None:
        model_cfg.device = f"cuda:{device}" if device.isdigit() else model_cfg.device

    cfg = ExperimentConfig(
        data=data_cfg,
        metric=metric_cfg,
        model=model_cfg,
        visualization=viz_cfg,
        results_dir=raw.get("results_dir", "./results"),
        hypothesis_id=raw.get("hypothesis_id", "H-M2"),
        gate_min_metrics=raw.get("gate_min_metrics", 2),
        gate_n_total_metrics=raw.get("gate_n_total_metrics", 3),
    )
    return cfg
```

### Full configs/experiment.yaml

```yaml
data:
  waterbirds_root: .data_cache/datasets/waterbirds
  celeba_root: .data_cache/datasets/celeba
  patch_size: 64
  batch_size: 256
  num_workers: 4
  celeba_samples_per_group: 5000
  use_segmentation_masks: true

metric:
  n_samples_list: [50, 100, 200, 500, 1000, 2000]
  seeds: [42, 123, 456]
  alpha: 0.05
  min_patches_per_class: 100
  logistic_c: 1.0
  logistic_max_iter: 1000
  bonferroni_n_tests: 6

model:
  backbone: resnet50
  pretrained: true
  feature_layer: layer4
  feature_dim: 2048
  frozen: true
  device: cuda:0

visualization:
  figures_dir: ./figures
  dpi: 150
  format: png
  n_fft_examples: 4
  pca_method: pca
  colormap: viridis
  figsize: [10, 6]

results_dir: ./results
hypothesis_id: H-M2
gate_min_metrics: 2
gate_n_total_metrics: 3
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-11-1 | ExperimentConfig composition | Define ExperimentConfig composing DataConfig, MetricConfig, ModelConfig, FigureConfig with default_factory; implement load_config() with YAML parsing and CUDA_VISIBLE_DEVICES env override |
| C-11-2 | Config validation | Implement validate_config() checking path existence, device availability, n_samples_list ordering, seeds uniqueness, visualization enum fields |
