# Configuration: H-M-MITIGATE

**Hypothesis ID:** h-m-mitigate  
**Type:** MECHANISM (SHOULD_WORK gate)  
**Date:** 2026-08-20

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config classes verified from h-m-integrated code  
**Config Files Found:** h-m-integrated/code/config.py  
**Pattern Used:** Dataclass

---

## Applied Patterns

Applied: Standard PyTorch dataclass config pattern (from h-m-integrated)

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m-integrated/code/config.py (ACTUAL CODE)
@dataclass
class DataConfig:
    dataset_name: str = "waterbirds"
    batch_size: int = 128
    num_workers: int = 4
    data_root: str = "./data/waterbird_complete95_forest2water2"

@dataclass
class ModelConfig:
    architecture: str = "resnet50"
    pretrained: bool = True
    num_classes: int = 2
    freeze_early_layers: bool = False

@dataclass
class TrainingConfig:
    optimizer: str = "sgd"
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    num_epochs: int = 300
    scheduler: str = "cosine"
    T_max: int = 300
    eta_min: float = 0.0
    early_stopping_patience: int = 50
    early_stopping_metric: str = "worst_group_val_acc"
    seed: int = 42

@dataclass
class GAIAConfig:
    target_layer: str = "layer4"
    divergence_threshold: float = 0.2
    p_value_threshold: float = 0.01
    minority_groups: List[int] = field(default_factory=lambda: [1, 2])
    majority_groups: List[int] = field(default_factory=lambda: [0, 3])
    epsilon: float = 1e-6
```

---

## M-7: MNIST Experiments [Complexity: 8, Budget: 2 subtasks]

```python
@dataclass
class MNISTDataConfig:
    correlation: float = 0.9  # 90% spurious correlation
    batch_size: int = 128
    num_workers: int = 4
    data_root: str = "./data/mnist_color"

@dataclass
class MNISTModelConfig:
    architecture: str = "resnet18"
    pretrained: bool = False  # Train from scratch for MNIST
    num_classes: int = 10
    input_channels: int = 3

@dataclass
class MNISTTrainingConfig:
    optimizer: str = "sgd"
    lr: float = 0.01
    momentum: float = 0.9
    weight_decay: float = 1e-4
    epochs: int = 50
    scheduler: str = "plateau"
    patience: int = 5
    factor: float = 0.1
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])

@dataclass
class MNISTExperimentConfig:
    data: MNISTDataConfig = field(default_factory=MNISTDataConfig)
    model: MNISTModelConfig = field(default_factory=MNISTModelConfig)
    training: MNISTTrainingConfig = field(default_factory=MNISTTrainingConfig)
    checkpoint_dir: str = "./checkpoints/h-m-mitigate/mnist"
    results_dir: str = "./results/h-m-mitigate/mnist"
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-7-1 | MNIST orchestration | 4 conditions × 5 seeds script |
| M-7-2 | MNIST logging | WGA tracking per condition |

---

## M-2: GradCAM Integration [Complexity: 8, Budget: 2 subtasks]

```python
@dataclass
class GradCAMConfig:
    target_layer: str = "layer4"  # ResNet layer4 for both datasets
    percentile_threshold: int = 75
    update_frequency: int = 1  # Update mask every N batches
    max_samples_per_batch: int = 32  # Subsample for efficiency

@dataclass
class SpatialRegConfig:
    lambda_init: float = 0.01
    lambda_min: float = 0.001
    lambda_max: float = 1.0
    adaptive_scaling: float = 0.1  # exp(0.1 * WGA_gap)
    
@dataclass
class RegularizerConfig:
    gradcam: GradCAMConfig = field(default_factory=GradCAMConfig)
    spatial_reg: SpatialRegConfig = field(default_factory=SpatialRegConfig)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| M-2-1 | GradCAM wrapper | pytorch-grad-cam integration |
| M-2-2 | Difference map | Majority-minority CAM comparison |

---

## Extended Configuration (Current Hypothesis)

```python
from dataclasses import dataclass, field
from typing import List
import yaml


@dataclass
class WaterbirdsExperimentConfig:
    """Extends h-m-integrated config for spatial regularization."""
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    gaia: GAIAConfig = field(default_factory=GAIAConfig)
    regularizer: RegularizerConfig = field(default_factory=RegularizerConfig)
    checkpoint_dir: str = "./checkpoints/h-m-mitigate/waterbirds"
    results_dir: str = "./results/h-m-mitigate/waterbirds"

    @classmethod
    def from_yaml(cls, path: str):
        with open(path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        return cls(
            data=DataConfig(**config_dict.get('data', {})),
            model=ModelConfig(**config_dict.get('model', {})),
            training=TrainingConfig(**config_dict.get('training', {})),
            gaia=GAIAConfig(**config_dict.get('gaia', {})),
            regularizer=RegularizerConfig(**config_dict.get('regularizer', {})),
            checkpoint_dir=config_dict.get('checkpoint_dir', './checkpoints/h-m-mitigate/waterbirds'),
            results_dir=config_dict.get('results_dir', './results/h-m-mitigate/waterbirds')
        )
```

---

## Default YAML (MNIST)

```yaml
data:
  correlation: 0.9
  batch_size: 128
  num_workers: 4
  data_root: ./data/mnist_color

model:
  architecture: resnet18
  pretrained: false
  num_classes: 10
  input_channels: 3

training:
  optimizer: sgd
  lr: 0.01
  momentum: 0.9
  weight_decay: 0.0001
  epochs: 50
  scheduler: plateau
  patience: 5
  factor: 0.1
  seeds: [0, 1, 2, 3, 4]

checkpoint_dir: ./checkpoints/h-m-mitigate/mnist
results_dir: ./results/h-m-mitigate/mnist
```

---

## Default YAML (Waterbirds)

```yaml
data:
  dataset_name: waterbirds
  batch_size: 128
  num_workers: 4
  data_root: ./data/waterbird_complete95_forest2water2

model:
  architecture: resnet50
  pretrained: true
  num_classes: 2
  freeze_early_layers: false

training:
  optimizer: sgd
  lr: 0.001
  momentum: 0.9
  weight_decay: 0.0001
  num_epochs: 300
  scheduler: cosine
  T_max: 300
  eta_min: 0.0
  early_stopping_patience: 50
  early_stopping_metric: worst_group_val_acc
  seed: 42

gaia:
  target_layer: layer4
  divergence_threshold: 0.2
  p_value_threshold: 0.01
  minority_groups: [1, 2]
  majority_groups: [0, 3]
  epsilon: 1e-6

regularizer:
  gradcam:
    target_layer: layer4
    percentile_threshold: 75
    update_frequency: 1
    max_samples_per_batch: 32
  spatial_reg:
    lambda_init: 0.01
    lambda_min: 0.001
    lambda_max: 1.0
    adaptive_scaling: 0.1

checkpoint_dir: ./checkpoints/h-m-mitigate/waterbirds
results_dir: ./results/h-m-mitigate/waterbirds
```

---

## Validation

### Self-Validation Checklist

- [x] ONE format only (Dataclass)
- [x] No ASCII diagrams
- [x] KB search logged (1 line)
- [x] Codebase Analysis section included
- [x] Inherited Configuration section included
- [x] Field names match h-m-integrated actual code
- [x] Total length < 400 lines

### Base Hypothesis Checks

- [x] Read h-m-integrated config.py actual code
- [x] Field names verified (DataConfig, ModelConfig, TrainingConfig, GAIAConfig)
- [x] Default values match base implementation
- [x] Extended pattern maintains YAML serialization
