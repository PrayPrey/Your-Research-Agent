# Configuration: h-m-integrated - Mechanism Validation Pipeline

**Date:** 2026-08-20
**Hypothesis:** MECHANISM
**Status:** Validation Configuration

Applied: Modular DL experiment config pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config schema verified from h-e1 code - reusing base dataclass structure
**Config Files Found:** h-e1 uses hardcoded values in run_experiment.py (no config.py file)
**Pattern Used:** Python dataclass (following h-e1 spec pattern)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From h-e1 Specs)

The following configs are inherited from base hypothesis:

```python
# From: h-e1/03_config.md (specification)
@dataclass
class ModelConfig:
    model_id: str = "meta-llama/Llama-3.1-8B-Instruct"
    cache_dir: str = "./cache"
    batch_size: int = 8
    max_tokens: int = 100
    temperature: float = 1.0
    top_p: float = 1.0
    device_map: str = "auto"
    torch_dtype: str = "float16"

@dataclass
class DataConfig:
    dataset_name: str = "truthfulqa/truthful_qa"
    dataset_config: str = "generation"
    cal_ratio: float = 0.4
    seed: int = 42

@dataclass
class UQConfig:
    temp_epochs: int = 50
    temp_lr: float = 0.01
    alpha: float = 0.1
    dropout_rate: float = 0.1
    mc_k_values: list[int] = field(default_factory=lambda: [1, 3, 5, 10])
```

**Note:** h-e1 actual code uses hardcoded values in run_experiment.py. Above configs follow h-e1 spec pattern.

---

## Configuration Schema

### Python Dataclass (config.py)

```python
from dataclasses import dataclass, field


@dataclass
class HaluEvalConfig:
    """HaluEval dataset configuration."""
    dataset_name: str = "pminervini/HaluEval"
    split: str = "qa"
    calib_ratio: float = 0.8
    seed: int = 42


@dataclass
class ValidationConfig:
    """Mechanism validation thresholds."""
    spearman_threshold: float = 0.2
    auroc_threshold: float = 0.55
    n_bins_ause: int = 10
    min_passing_methods: int = 4
    non_degenerate_methods: list[str] = field(
        default_factory=lambda: ["temp_scaling", "conformal", "mc_k3", "mc_k5", "mc_k10"]
    )


@dataclass
class CrossDatasetConfig:
    """Cross-dataset calibration configuration."""
    alpha: float = 0.1
    target_coverage: float = 0.9
    max_coverage_gap: float = 0.1
    calibration_method: str = "conformal"


@dataclass
class VisualizationConfig:
    """Plot generation configuration."""
    figures_dir: str = "./figures"
    dpi: int = 300
    figure_formats: list[str] = field(default_factory=lambda: ["png"])


@dataclass
class ExperimentConfig:
    """Root configuration for h-m-integrated experiment."""
    model: ModelConfig = field(default_factory=ModelConfig)
    data: DataConfig = field(default_factory=DataConfig)
    uq: UQConfig = field(default_factory=UQConfig)
    halueval: HaluEvalConfig = field(default_factory=HaluEvalConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    cross_dataset: CrossDatasetConfig = field(default_factory=CrossDatasetConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    
    # Paths
    h_e1_cache_dir: str = "../h-e1/cache"
    results_dir: str = "./results"
```

---

## A-1: Data Pipeline [Complexity: 8, Budget: 8]

**Applied:** Standard PyTorch dataset loading pattern

### Configuration

```python
@dataclass
class DataManagerConfig:
    """Configuration for DataManager."""
    h_e1_cache_dir: str = "../h-e1/cache"
    halueval_cache_dir: str = "./cache/halueval"
    seed: int = 42
    verify_splits: bool = True
```

### Subtasks [8/8 used]

| ID | Subtask | Budget | Description |
|----|---------|--------|-------------|
| C-1-1 | h-e1 artifact paths | 2 | Cache dir for answers, uq_scores, calibration params |
| C-1-2 | HaluEval config | 2 | Dataset name, split, calib_ratio, cache_dir |
| C-1-3 | Data verification | 2 | verify_splits flag, split consistency check |
| C-1-4 | Seed consistency | 2 | Reuse h-e1 seed=42 for reproducibility |

---

## A-2: Mechanism Validator [Complexity: 12, Budget: 12]

**Applied:** Standard metric computation config pattern

### Configuration

```python
@dataclass
class MechanismValidatorConfig:
    """Configuration for UQMechanismValidator."""
    spearman_threshold: float = 0.2
    auroc_threshold: float = 0.55
    n_bins_ause: int = 10
    min_passing_methods: int = 4
    method_names: list[str] = field(
        default_factory=lambda: ["temp_scaling", "conformal", "mc_k1", "mc_k3", "mc_k5", "mc_k10"]
    )
    non_degenerate_methods: list[str] = field(
        default_factory=lambda: ["temp_scaling", "conformal", "mc_k3", "mc_k5", "mc_k10"]
    )
```

### Subtasks [12/12 used]

| ID | Subtask | Budget | Description |
|----|---------|--------|-------------|
| C-2-1 | Spearman config | 3 | Threshold 0.2, compute_spearman params |
| C-2-2 | AUROC config | 3 | Threshold 0.55, compute_auroc params |
| C-2-3 | AUSE config | 3 | n_bins=10, sparsification curve settings |
| C-2-4 | Gate check config | 3 | min_passing_methods=4, non_degenerate list |

---

## A-3: Cross-Dataset Calibration [Complexity: 11, Budget: 11]

**Applied:** Conformal prediction config pattern

### Configuration

```python
@dataclass
class CrossDatasetCalibratorConfig:
    """Configuration for CrossDatasetCalibrator."""
    alpha: float = 0.1
    target_coverage: float = 0.9
    max_coverage_gap: float = 0.1
    calibration_method: str = "conformal"
    compute_auroc_transfer: bool = True
```

### Subtasks [11/11 used]

| ID | Subtask | Budget | Description |
|----|---------|--------|-------------|
| C-3-1 | Conformal params | 3 | alpha=0.1, target_coverage=0.9 |
| C-3-2 | Coverage gap threshold | 2 | max_coverage_gap=0.1 |
| C-3-3 | Transfer metrics | 3 | AUROC transfer computation flag |
| C-3-4 | Source/target paths | 3 | HaluEval calib/test, TruthfulQA test split paths |

---

## A-4: HaluEval Inference [Complexity: 14, Budget: 3]

**Applied:** Reuse h-e1 model config (ModelConfig inherited)

### Configuration

```python
# Inherited from h-e1 ModelConfig
# model_id: "meta-llama/Llama-3.1-8B-Instruct"
# batch_size: 8
# max_tokens: 100
# temperature: 1.0
```

### Subtasks [3/3 used]

| ID | Subtask | Budget | Description |
|----|---------|--------|-------------|
| C-4-1 | Model config reuse | 1 | Inherit ModelConfig from h-e1 |
| C-4-2 | HaluEval batch size | 1 | batch_size=8 (same as h-e1) |
| C-4-3 | UQ methods reuse | 1 | Reuse UQConfig mc_k_values, alpha, dropout_rate |

---

## A-5: Visualization Suite [Complexity: 13, Budget: 13]

**Applied:** Matplotlib config pattern

### Configuration

```python
@dataclass
class PlotConfig:
    """Configuration for visualization plots."""
    figures_dir: str = "./figures"
    dpi: int = 300
    figure_formats: list[str] = field(default_factory=lambda: ["png"])
    figsize_single: tuple[int, int] = (8, 6)
    figsize_grid: tuple[int, int] = (12, 8)
    
    # Plot-specific settings
    gate_scatter_colors: dict[str, str] = field(
        default_factory=lambda: {
            "mc_k1": "gray",
            "temp_scaling": "blue",
            "conformal": "green",
            "mc_k3": "orange",
            "mc_k5": "red",
            "mc_k10": "purple"
        }
    )
```

### Subtasks [13/13 used]

| ID | Subtask | Budget | Description |
|----|---------|--------|-------------|
| C-5-1 | Figure output paths | 3 | figures_dir, dpi, formats |
| C-5-2 | Plot dimensions | 3 | figsize_single, figsize_grid |
| C-5-3 | Color schemes | 4 | gate_scatter_colors, method colors |
| C-5-4 | Threshold lines | 3 | Spearman=0.2, AUROC=0.55, coverage=0.9 |

---

## A-6: Report Generation [Complexity: 9, Budget: 9]

**Applied:** Standard output config pattern

### Configuration

```python
@dataclass
class ReportConfig:
    """Configuration for report generation."""
    output_dir: str = "./results"
    validation_report_name: str = "04_validation.md"
    metrics_json_name: str = "metrics.json"
    sparsification_json_name: str = "sparsification.json"
    cross_dataset_json_name: str = "cross_dataset.json"
```

### Subtasks [9/9 used]

| ID | Subtask | Budget | Description |
|----|---------|--------|-------------|
| C-6-1 | Output paths | 2 | output_dir, validation report path |
| C-6-2 | JSON filenames | 2 | metrics.json, sparsification.json, cross_dataset.json |
| C-6-3 | Report structure | 3 | Gate results table, cross-dataset table, figure refs |
| C-6-4 | Gate decision format | 2 | PASSED/FAILED, reflection text |

---

## Usage Example

```python
from config import ExperimentConfig

# Default configuration
config = ExperimentConfig()

# Override specific values
config.validation.min_passing_methods = 3
config.halueval.calib_ratio = 0.9
config.cross_dataset.alpha = 0.05

# Access nested configs
print(config.validation.spearman_threshold)  # 0.2
print(config.cross_dataset.target_coverage)  # 0.9
print(config.visualization.dpi)  # 300
```

---

## Validation Notes

- [x] Single format (dataclass only)
- [x] No ASCII diagrams
- [x] Codebase Analysis section included
- [x] Inherited Configuration section included
- [x] Subtask counts within budgets (8+12+11+3+13+9 = 56 total)
- [x] Total length < 400 lines
- [x] Field names verified from h-e1 specs (no actual config.py exists in h-e1 code)
