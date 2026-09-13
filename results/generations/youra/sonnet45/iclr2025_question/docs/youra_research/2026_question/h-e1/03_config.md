# Configuration Specification: h-e1 Variance Measurement

**Date:** 2026-03-21
**Hypothesis ID:** h-e1 (EXISTENCE)
**Version:** 3.0
**Phase:** 3 (Implementation Planning)

Applied: PyTorch deterministic training pattern, modular dataclass config

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase
**Status:** Existing config classes verified from base code
**Config Files Found:** `/home/anonymous/YouRA_results_new_4_sonnet45/TEST_question/code/config.py`
**Pattern Used:** dataclass (nested config classes)

Verified actual field names and defaults from existing implementation. Current config uses nested dataclass pattern with EnvironmentConfig, DataConfig, ModelConfig, TrainingConfig, StatisticsConfig, EvaluationConfig, and VisualizationConfig.

---

## A-1: Configuration Setup [Complexity: 6, Budget: 3]

Applied: Nested dataclass pattern (from existing codebase)

### Configuration (Python Dataclass)

```python
"""Configuration for H-E1 Variance Measurement Experiment."""

from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any
import json
from pathlib import Path


@dataclass
class EnvironmentConfig:
    """Deterministic environment configuration."""
    cuda_visible_devices: str = "0"
    cublas_workspace_config: str = ":4096:8"
    cudnn_deterministic: bool = True
    cudnn_benchmark: bool = False


@dataclass
class DataConfig:
    """Dual-dataset configuration."""
    datasets: List[str] = field(default_factory=lambda: ["mnist", "fashion_mnist"])
    data_root: str = "./data"
    batch_size: int = 64
    test_batch_size: int = 64
    num_workers: int = 0
    download: bool = True

    # Dataset-specific normalization
    mnist_mean: float = 0.1307
    mnist_std: float = 0.3081
    fashion_mnist_mean: float = 0.5
    fashion_mnist_std: float = 0.5


@dataclass
class ModelConfig:
    """Dual-architecture configuration."""
    architectures: List[str] = field(default_factory=lambda: ["1layer", "2layer"])
    input_size: int = 784

    # 1-layer MLP
    hidden_size_1layer: int = 128

    # 2-layer MLP
    hidden1_2layer: int = 256
    hidden2_2layer: int = 128

    output_size: int = 10


@dataclass
class TrainingConfig:
    """Training protocol configuration."""
    seeds: List[int] = field(default_factory=lambda: list(range(30)))
    epochs: int = 10
    lr: float = 0.01
    momentum: float = 0.9
    device: str = "cuda"
    log_interval: int = 100


@dataclass
class StatisticsConfig:
    """Variance metrics configuration."""
    use_ddof: int = 1
    n_bootstrap_iterations: int = 1000
    ci_alpha: float = 0.95
    bootstrap_seed: int = 42


@dataclass
class EvaluationConfig:
    """Gate validation configuration."""
    variance_threshold: float = 0.3
    min_conditions_pass: int = 2
    results_dir: str = "./results"
    save_experiment_logs: bool = True
    save_variance_summary: bool = True
    save_gate_result: bool = True


@dataclass
class VisualizationConfig:
    """Visualization configuration."""
    figures_dir: str = "./figures"
    dpi: int = 300
    format: str = "png"
    figsize_gate: Tuple[int, int] = (10, 6)
    figsize_variance: Tuple[int, int] = (10, 6)
    figsize_distributions: Tuple[int, int] = (12, 10)
    figsize_cv: Tuple[int, int] = (10, 6)
    figsize_ranges: Tuple[int, int] = (10, 6)


@dataclass
class ExperimentConfig:
    """Top-level experiment configuration."""

    environment: EnvironmentConfig = field(default_factory=EnvironmentConfig)
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    statistics: StatisticsConfig = field(default_factory=StatisticsConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    visualization: VisualizationConfig = field(default_factory=VisualizationConfig)

    experiment_name: str = "h-e1-variance-measurement"
    hypothesis_id: str = "h-e1"
    verbose: bool = True

    def get_conditions(self) -> List[Tuple[str, str]]:
        """Return list of (dataset, architecture) conditions."""
        return [
            (dataset, arch)
            for dataset in self.data.datasets
            for arch in self.model.architectures
        ]

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for serialization."""
        return {
            'environment': self.environment.__dict__,
            'data': self.data.__dict__,
            'model': self.model.__dict__,
            'training': self.training.__dict__,
            'statistics': self.statistics.__dict__,
            'evaluation': self.evaluation.__dict__,
            'visualization': self.visualization.__dict__,
            'experiment_name': self.experiment_name,
            'hypothesis_id': self.hypothesis_id,
            'verbose': self.verbose
        }

    def save(self, path: str) -> None:
        """Save configuration to JSON file."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load(cls, path: str) -> 'ExperimentConfig':
        """Load configuration from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)

        config = cls()

        # Update sub-configs
        for key, value in data.get('environment', {}).items():
            setattr(config.environment, key, value)
        for key, value in data.get('data', {}).items():
            setattr(config.data, key, value)
        for key, value in data.get('model', {}).items():
            setattr(config.model, key, value)
        for key, value in data.get('training', {}).items():
            setattr(config.training, key, value)
        for key, value in data.get('statistics', {}).items():
            setattr(config.statistics, key, value)
        for key, value in data.get('evaluation', {}).items():
            setattr(config.evaluation, key, value)
        for key, value in data.get('visualization', {}).items():
            setattr(config.visualization, key, value)

        # Update top-level fields
        config.experiment_name = data.get('experiment_name', config.experiment_name)
        config.hypothesis_id = data.get('hypothesis_id', config.hypothesis_id)
        config.verbose = data.get('verbose', config.verbose)

        return config


def get_default_config() -> ExperimentConfig:
    """Return default experiment configuration."""
    return ExperimentConfig()
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Environment Config | CUDA determinism settings (cudnn, cublas workspace) |
| C-1-2 | Dataset/Model Config | Dual-dataset (MNIST, Fashion-MNIST), dual-architecture (1L, 2L) parameters |
| C-1-3 | Experiment Config | Training hyperparameters, seeds (0-29), gate threshold (0.3%) |

---

## Configuration Values Summary

### Datasets
- **MNIST:** torchvision.datasets.MNIST, normalization (0.1307, 0.3081)
- **Fashion-MNIST:** torchvision.datasets.FashionMNIST, normalization (0.5, 0.5)
- **Batch Size:** 64 (train and test)
- **Num Workers:** 0 (determinism requirement)

### Model Architectures
- **1-layer MLP:** 784 → 128 (ReLU) → 10 (~196K params)
- **2-layer MLP:** 784 → 256 (ReLU) → 128 (ReLU) → 10 (~400K params)

### Training Protocol
- **Seeds:** 0-29 (30 independent initializations)
- **Epochs:** 10
- **Optimizer:** SGD with lr=0.01, momentum=0.9
- **Device:** Single GPU (CUDA_VISIBLE_DEVICES=0)

### Determinism Settings
- **cudnn_deterministic:** True
- **cudnn_benchmark:** False
- **CUBLAS_WORKSPACE_CONFIG:** ":4096:8"
- **num_workers:** 0 (disable DataLoader multiprocessing)

### Gate Validation
- **Threshold:** σ² ≥ 0.3%
- **Pass Condition:** ≥2 out of 4 conditions meet threshold
- **Conditions:** (MNIST, 1L), (MNIST, 2L), (Fashion-MNIST, 1L), (Fashion-MNIST, 2L)

### Outputs
- **Results Directory:** ./results/
  - experiment_logs.csv
  - variance_summary.json
  - gate_result.json
- **Figures Directory:** ./figures/
  - gate_metrics_comparison.png (mandatory)
  - variance_by_condition.png
  - accuracy_distributions.png
  - cv_comparison.png
  - accuracy_ranges.png

---

## Usage Example

```python
from config import ExperimentConfig, get_default_config

# Option 1: Use defaults
config = get_default_config()

# Option 2: Customize
config = ExperimentConfig()
config.environment.cuda_visible_devices = "1"  # Use GPU 1
config.training.seeds = list(range(20))  # Only 20 seeds for testing
config.evaluation.variance_threshold = 0.2  # Lower threshold

# Get experiment conditions
conditions = config.get_conditions()
# Returns: [("mnist", "1layer"), ("mnist", "2layer"),
#           ("fashion_mnist", "1layer"), ("fashion_mnist", "2layer")]

# Save/load
config.save("./results/config.json")
loaded_config = ExperimentConfig.load("./results/config.json")
```

---

## Validation Checklist

- [x] ONE format only (dataclass - matches existing codebase)
- [x] Field names verified from actual base config
- [x] Default values from research (MNIST tutorials: lr=0.01, momentum=0.9, epochs=10)
- [x] Determinism settings complete (cudnn, cublas, num_workers=0)
- [x] Dual-dataset/dual-architecture support (4 conditions)
- [x] Gate threshold configuration (0.3%, ≥2 conditions)
- [x] 30 seeds for stable variance estimation
- [x] Subtask count within budget (3/3)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included

---

## Notes

**EXISTENCE PoC Configuration:**
- Single fixed config (no hyperparameter grid)
- Minimal epochs (10 - sufficient for MNIST/Fashion-MNIST convergence)
- Standard defaults from PyTorch MNIST tutorials
- 30 seeds per condition (Rajput 2023 recommendation)

**Non-Standard Values:**
- `num_workers=0`: Required for deterministic DataLoader shuffling
- `cublas_workspace_config=":4096:8"`: CUDA determinism requirement (PyTorch 1.10+)
- `momentum=0.9`: Standard SGD momentum (vs 0.5 in pilot experiment)

**Inherited from Base Config:**
- Nested dataclass pattern
- save/load methods for JSON serialization
- to_dict conversion for logging
