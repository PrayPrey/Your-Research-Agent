# Configuration Specification: h-m1

**Hypothesis**: Asymmetric digit degradation increases monotonically with flip probability (dose-response relationship)  
**Type**: MECHANISM  
**Date**: 2026-07-11

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase  
**Status**: Patterns found from h-e1 experiment  
**Config Files Found**: `experiments/h-e1/config.py`  
**Pattern Used**: Dataclass (hierarchical composition)

**Applied**: h-e1 dataclass pattern with hierarchical config composition

---

## A-6: Visualization (Complexity: 9, Budget: 1 subtask)

**Applied**: Standard matplotlib configuration defaults

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import Tuple

@dataclass
class VisualizationConfig:
    """Visualization configuration for dose-response analysis"""
    
    # Figure settings
    figure_dpi: int = 300
    figure_format: str = "png"
    figure_size_single: Tuple[float, float] = (8.0, 6.0)
    figure_size_wide: Tuple[float, float] = (12.0, 5.0)
    
    # Style
    style: str = "seaborn-v0_8-darkgrid"
    font_size: int = 12
    title_size: int = 14
    label_size: int = 12
    
    # Colors
    line_color: str = "#2E86AB"
    error_color: str = "#A23B72"
    bar_colors: Tuple[str, str, str] = ("#3A86FF", "#8338EC", "#FF006E")
    heatmap_cmap: str = "coolwarm"
    
    # Markers and lines
    marker_style: str = "o"
    marker_size: int = 8
    line_width: float = 2.0
    error_capsize: float = 5.0
    
    # Gate metrics visualization
    gate_pass_color: str = "#06D6A0"
    gate_fail_color: str = "#EF476F"
    
    # Heatmap settings
    heatmap_annot: bool = True
    heatmap_fmt: str = ".2f"
    heatmap_cbar_label: str = "Accuracy"
    
    # Output paths (relative to experiment root)
    output_subdir: str = "figures"
    dose_response_filename: str = "dose_response_curve.png"
    heatmap_filename: str = "per_digit_heatmap.png"
    degradation_filename: str = "degradation_bars.png"
    gate_metrics_filename: str = "gate_metrics.png"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Implement 4 plotting functions | dose_response_curve, per_digit_heatmap, degradation_bars, gate_metrics |

---

## Master Configuration Schema

**Applied**: h-e1 hierarchical dataclass pattern (DataConfig, ModelConfig, TrainingConfig, ExperimentConfig composition)

### Complete Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Optional

@dataclass
class DataConfig:
    """Data pipeline configuration"""
    dataset_name: str = "mnist"
    data_root: str = "data/mnist"
    batch_size: int = 64
    num_workers: int = 4
    pin_memory: bool = True
    
    # Dose-response experimental conditions
    flip_probabilities: List[float] = field(default_factory=lambda: [0.0, 0.3, 0.5, 0.9])
    
    # MNIST normalization (standard)
    mean: Tuple[float] = (0.1307,)
    std: Tuple[float] = (0.3081,)


@dataclass
class ModelConfig:
    """Model architecture configuration"""
    architecture: str = "standard_cnn"
    in_channels: int = 1
    num_classes: int = 10
    
    # Regularization (PyTorch MNIST official example)
    dropout_conv: float = 0.25
    dropout_fc: float = 0.5


@dataclass
class TrainingConfig:
    """Training protocol configuration"""
    # Optimizer
    optimizer: str = "adam"
    lr: float = 0.001
    weight_decay: float = 0.0
    
    # Schedule (PyTorch official example)
    lr_schedule: str = "step"
    scheduler_step: int = 1
    scheduler_gamma: float = 0.7
    
    # Training duration
    max_epochs: int = 30
    patience: int = 5
    
    # Gradient management
    gradient_clip_norm: float = 1.0
    gradient_clip_enabled: bool = True
    detect_nan_gradients: bool = True
    
    # Multi-seed execution
    seeds: List[int] = field(default_factory=lambda: [42, 43, 44, 45, 46])
    
    # Compute
    device: str = "cuda"
    mixed_precision: bool = False


@dataclass
class EvaluationConfig:
    """Evaluation metrics configuration"""
    # Primary metric (hypothesis-specific)
    asymmetric_digits: List[int] = field(default_factory=lambda: [2, 3, 5, 6, 7, 9])
    symmetric_digits: List[int] = field(default_factory=lambda: [0, 1, 8])
    
    # Statistical test
    correlation_method: str = "spearman"
    alpha: float = 0.05
    
    # Gate criteria
    gate_type: str = "SHOULD_WORK"
    gate_rho_threshold: float = 0.0  # Must be < 0 (negative correlation)
    gate_p_threshold: float = 0.05


@dataclass
class LoggingConfig:
    """Logging configuration"""
    # Logging frequency
    log_every_n_steps: int = 10
    log_epoch_summary: bool = True
    
    # Console output
    verbose: bool = True
    progress_bar: bool = True
    
    # File logging
    use_file_logging: bool = True
    log_file: str = "experiment.log"
    metrics_file: str = "metrics.json"
    results_file: str = "results.csv"


@dataclass
class ExperimentConfig:
    """Master configuration container"""
    
    # Experiment metadata
    experiment_name: str = "h-m1-dose-response"
    hypothesis_id: str = "h-m1"
    seed: int = 42
    
    # Component configs
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Paths (absolute)
    project_root: Path = Path("/workspace/TEST_scsl")
    output_root: Path = field(init=False)
    checkpoint_dir: Path = field(init=False)
    results_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
    figures_dir: Path = field(init=False)
    
    def __post_init__(self):
        # Resolve paths
        self.output_root = self.project_root / f"experiments/{self.hypothesis_id}/results"
        self.checkpoint_dir = self.output_root / "checkpoints"
        self.results_dir = self.output_root / "results"
        self.logs_dir = self.output_root / "logs"
        self.figures_dir = self.output_root / "figures"
        
        # Create directories
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.figures_dir.mkdir(parents=True, exist_ok=True)


def get_config(seed: int = 42, **overrides) -> ExperimentConfig:
    """
    Factory function to create experiment config.
    
    Args:
        seed: Random seed
        **overrides: Override any config field (e.g., data__batch_size=64)
    
    Returns:
        ExperimentConfig with all defaults
    """
    config = ExperimentConfig(seed=seed)
    
    # Apply overrides (nested fields with __)
    for key, value in overrides.items():
        parts = key.split("__")
        obj = config
        for part in parts[:-1]:
            obj = getattr(obj, part)
        setattr(obj, parts[-1], value)
    
    return config
```

---

## Configuration Rationale

### Non-Standard Values

**DataConfig.flip_probabilities = [0.0, 0.3, 0.5, 0.9]**  
Dose-response experimental design: baseline (0.0) + three increasing dosages to test monotonic relationship.

**TrainingConfig.scheduler_gamma = 0.7**  
From PyTorch official MNIST example - aggressive decay ensures convergence within 30 epochs.

**TrainingConfig.max_epochs = 30**  
Short training (vs h-e1's 200 epochs) - MNIST baseline converges quickly, dose-response effect observable early.

**EvaluationConfig.asymmetric_digits = [2,3,5,6,7,9]**  
Hypothesis-specific: only these digits become invalid under horizontal flip.

**VisualizationConfig.bar_colors = ("#3A86FF", "#8338EC", "#FF006E")**  
High-contrast color scheme for degradation bars (3 non-baseline conditions).

---

## Usage Examples

### Basic Usage

```python
from config import get_config

# Default configuration
config = get_config(seed=42)

# Access nested configs
print(config.data.flip_probabilities)  # [0.0, 0.3, 0.5, 0.9]
print(config.training.lr)              # 0.001
print(config.evaluation.asymmetric_digits)  # [2, 3, 5, 6, 7, 9]
```

### Override Parameters

```python
# Override nested fields
config = get_config(
    seed=43,
    data__batch_size=128,
    training__max_epochs=50,
    training__lr=0.0005
)
```

### Multi-Condition Execution

```python
# Run all flip probability conditions
for flip_prob in config.data.flip_probabilities:
    for seed in config.training.seeds:
        # Create transform with specific flip_prob
        transform = create_transform(flip_prob, config.data.mean, config.data.std)
        # Train model
        model, history = train_model(config, flip_prob, seed)
```

---

## File Structure

```
experiments/h-m1/
├── config.py                    # This configuration (dataclasses)
├── data/
│   ├── __init__.py
│   └── datasets.py              # Uses DataConfig
├── models/
│   ├── __init__.py
│   └── baseline.py              # Uses ModelConfig
├── train.py                     # Uses TrainingConfig
├── evaluate.py                  # Uses EvaluationConfig
├── visualize.py                 # Uses VisualizationConfig (C-6-1)
├── run_experiment.py            # Uses ExperimentConfig
└── results/                     # Created by __post_init__
    ├── checkpoints/
    ├── results/
    ├── logs/
    └── figures/                 # Visualization outputs
```

---

## Validation Checklist

- [x] ONE format only (Dataclass)
- [x] Rationale only for non-standard values
- [x] Subtask count within budget (1/1)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Applied pattern from h-e1 actual code
- [x] Field names consistent with existing patterns
- [x] No ASCII diagrams
- [x] No full config example duplicates

---

**Next Phase**: Phase 4 - Implementation  
**Primary Task**: C-6-1 (Implement 4 plotting functions)  
**Config Usage**: Phase 4 will import `from config import get_config`
