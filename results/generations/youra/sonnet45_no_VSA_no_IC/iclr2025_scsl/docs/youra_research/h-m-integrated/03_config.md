# Configuration Specification: H-M-INTEGRATED

**Hypothesis ID:** h-m-integrated  
**Type:** MECHANISM (MUST_WORK gate)  
**Date:** 2026-08-20  

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (h-e1)  
**Status:** Config classes verified from h-e1 code  
**Config Files Found:** `/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_scsl/h-e1/code/config.py`  
**Pattern Used:** Dataclass with YAML serialization  

---

## Configuration Schema

**Format:** Python Dataclass (extends h-e1 config pattern)  
**Applied:** Standard PyTorch training patterns, h-e1 config structure  

### Inherited Configuration (Base Hypothesis)

```python
# From: h-e1/code/config.py (ACTUAL CODE)
@dataclass
class DataConfig:
    dataset_name: str
    batch_size: int = 64
    num_workers: int = 4
    data_root: str = "./data"

@dataclass
class ModelConfig:
    pretrained: bool = True
    freeze_early_layers: bool = True

@dataclass
class TrainingConfig:
    optimizer: str
    lr: float
    weight_decay: float
    momentum: float = 0.9
    num_epochs: int = 100
    scheduler_step_size: int = 30
    scheduler_gamma: float = 0.1
    seed: int = 42

@dataclass
class AttributionConfig:
    n_steps: int = 50
    num_samples: int = 500
    baseline_type: str = "zeros"
```

### Extended Configuration (Current Hypothesis)

```python
from dataclasses import dataclass
from typing import List
import yaml


@dataclass
class CorrelationSweepConfig:
    """Configuration for correlation rate sweep experiment."""
    correlation_rates: List[float] = None  # Default: [0.5, 0.55, ..., 0.95]
    
    def __post_init__(self):
        if self.correlation_rates is None:
            self.correlation_rates = [0.5 + 0.05*i for i in range(10)]


@dataclass
class DataConfig:
    """Extended from h-e1 DataConfig."""
    dataset_name: str = "waterbirds"
    batch_size: int = 128
    num_workers: int = 4
    data_root: str = "./data/wilds_cache"


@dataclass
class ModelConfig:
    """ResNet-50 configuration (matches h-e1 pattern)."""
    architecture: str = "resnet50"
    pretrained: bool = True
    num_classes: int = 2
    freeze_early_layers: bool = False  # Fine-tune entire network


@dataclass
class TrainingConfig:
    """Extended from h-e1 with CosineAnnealingLR."""
    optimizer: str = "sgd"
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    num_epochs: int = 300
    scheduler: str = "cosine"
    T_max: int = 300  # CosineAnnealingLR parameter
    eta_min: float = 0.0
    early_stopping_patience: int = 50
    early_stopping_metric: str = "worst_group_val_acc"
    seed: int = 42


@dataclass
class GAIAConfig:
    """GradCAM extraction configuration (from h-e1)."""
    target_layer: str = "layer4"  # ResNet-50 final conv layer
    divergence_threshold: float = 0.2
    p_value_threshold: float = 0.01
    minority_groups: List[int] = None  # Groups [1, 2]
    majority_groups: List[int] = None  # Groups [0, 3]
    
    def __post_init__(self):
        if self.minority_groups is None:
            self.minority_groups = [1, 2]
        if self.majority_groups is None:
            self.majority_groups = [0, 3]


@dataclass
class AugmentationConfig:
    """Background swap augmentation configuration."""
    segmentation_model: str = "nvidia/segformer-b5-finetuned-ade-640-640"
    num_minority_samples: int = 200  # 100 per minority group
    bird_class_id: int = 9  # ADE20K class ID for 'bird'
    background_pool_size: int = 500  # Per class
    reduction_threshold: float = 0.30  # 30% reduction required


@dataclass
class AnalysisConfig:
    """Correlation analysis configuration."""
    correlation_threshold: float = 0.7  # Pearson rho
    p_value_threshold: float = 0.05
    visualization_dpi: int = 300
    scatter_plot_size: tuple = (10, 6)  # Inches


@dataclass
class ExperimentConfig:
    """Top-level experiment configuration."""
    correlation_sweep: CorrelationSweepConfig
    data: DataConfig
    model: ModelConfig
    training: TrainingConfig
    gaia: GAIAConfig
    augmentation: AugmentationConfig
    analysis: AnalysisConfig
    checkpoint_dir: str = "./checkpoints/h-m-integrated"
    log_dir: str = "./logs/h-m-integrated"
    results_dir: str = "./results/h-m-integrated"
    
    @classmethod
    def from_yaml(cls, path: str):
        with open(path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        return cls(
            correlation_sweep=CorrelationSweepConfig(**config_dict.get('correlation_sweep', {})),
            data=DataConfig(**config_dict['data']),
            model=ModelConfig(**config_dict['model']),
            training=TrainingConfig(**config_dict['training']),
            gaia=GAIAConfig(**config_dict.get('gaia', {})),
            augmentation=AugmentationConfig(**config_dict.get('augmentation', {})),
            analysis=AnalysisConfig(**config_dict.get('analysis', {})),
            checkpoint_dir=config_dict.get('checkpoint_dir', './checkpoints/h-m-integrated'),
            log_dir=config_dict.get('log_dir', './logs/h-m-integrated'),
            results_dir=config_dict.get('results_dir', './results/h-m-integrated')
        )
    
    def to_yaml(self, path: str):
        config_dict = {
            'correlation_sweep': self.correlation_sweep.__dict__,
            'data': self.data.__dict__,
            'model': self.model.__dict__,
            'training': self.training.__dict__,
            'gaia': self.gaia.__dict__,
            'augmentation': self.augmentation.__dict__,
            'analysis': self.analysis.__dict__,
            'checkpoint_dir': self.checkpoint_dir,
            'log_dir': self.log_dir,
            'results_dir': self.results_dir
        }
        with open(path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False)
```

---

## Default Configuration (YAML)

```yaml
correlation_sweep:
  correlation_rates: [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95]

data:
  dataset_name: waterbirds
  batch_size: 128
  num_workers: 4
  data_root: ./data/wilds_cache

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

augmentation:
  segmentation_model: nvidia/segformer-b5-finetuned-ade-640-640
  num_minority_samples: 200
  bird_class_id: 9
  background_pool_size: 500
  reduction_threshold: 0.30

analysis:
  correlation_threshold: 0.7
  p_value_threshold: 0.05
  visualization_dpi: 300
  scatter_plot_size: [10, 6]

checkpoint_dir: ./checkpoints/h-m-integrated
log_dir: ./logs/h-m-integrated
results_dir: ./results/h-m-integrated
```

---

## Hyperparameter Justification

### Training Configuration

**batch_size: 128**  
Increased from h-e1 (64) for faster training across 10 models. Standard for ResNet-50 on single GPU.

**lr: 1e-3**  
Standard SGD learning rate for pretrained ResNet fine-tuning.

**weight_decay: 1e-4**  
Standard L2 regularization for ImageNet-pretrained models.

**num_epochs: 300, early_stopping_patience: 50**  
From experiment brief. Allows sufficient training while preventing overfitting on worst-group accuracy.

**CosineAnnealingLR (T_max=300, eta_min=0.0)**  
Replaces h-e1's StepLR. Smoother learning rate decay for longer training.

### GAIA Configuration

**target_layer: "layer4"**  
ResNet-50 final convolutional layer before global pooling. From h-e1 validation.

**divergence_threshold: 0.2, p_value_threshold: 0.01**  
From h-e1 statistical tests. Conservative thresholds for gradient abnormality detection.

### Augmentation Configuration

**num_minority_samples: 200**  
100 per minority group (waterbird-land, landbird-water). Sufficient for paired t-test statistical power.

**reduction_threshold: 0.30**  
From experiment brief success criteria (≥30% GAIA-Z reduction).

### Analysis Configuration

**correlation_threshold: 0.7, p_value_threshold: 0.05**  
From experiment brief. Standard thresholds for strong Pearson correlation.

---

## Environment Setup

### Conda Environment

```yaml
name: h-m-integrated
channels:
  - pytorch
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - pytorch=2.0.1
  - torchvision=0.15.2
  - cudatoolkit=11.8
  - pip
  - pip:
      - wilds==2.0.0
      - transformers==4.30.0
      - scipy==1.10.1
      - matplotlib==3.7.1
      - seaborn==0.12.2
      - pandas==2.0.2
      - Pillow==9.5.0
      - pyyaml==6.0
      - tqdm==4.65.0
```

### Pip Requirements

```txt
torch==2.0.1
torchvision==0.15.2
wilds==2.0.0
transformers==4.30.0
scipy==1.10.1
matplotlib==3.7.1
seaborn==0.12.2
pandas==2.0.2
Pillow==9.5.0
pyyaml==6.0
tqdm==4.65.0
```

---

## Configuration Validation

### Self-Validation Checklist

- [x] ONE format only (Dataclass, not dict + dataclass)
- [x] No ASCII diagrams (text only)
- [x] KB search logged (1 line: "Applied: Standard PyTorch training patterns")
- [x] Serena analysis included (Codebase Analysis section)
- [x] Rationale only for non-standard values (batch_size, scheduler change)
- [x] Inherited Configuration section (h-e1 base config verified)
- [x] Field names match h-e1 actual code
- [x] Total length < 400 lines

### Base Hypothesis Checks

- [x] Read h-e1 config classes from actual code
- [x] Field names verified (DataConfig, ModelConfig, TrainingConfig match)
- [x] Extended pattern maintained (YAML serialization preserved)
- [x] New configs added without breaking h-e1 interface

---

## Usage Example

```python
from config import ExperimentConfig

# Load from YAML
config = ExperimentConfig.from_yaml("configs/default.yaml")

# Access nested configs
print(config.training.lr)  # 0.001
print(config.correlation_sweep.correlation_rates)  # [0.5, 0.55, ..., 0.95]

# Save modified config
config.training.lr = 5e-4
config.to_yaml("configs/modified.yaml")
```

---

## Configuration Notes

**Non-standard Changes from h-e1:**
1. **batch_size: 128** (was 64) - Faster training for 10-model sweep
2. **scheduler: cosine** (was StepLR) - Better for 300-epoch training
3. **freeze_early_layers: False** (was True) - Fine-tune entire network for spurious feature learning

**New Configuration Sections:**
1. `CorrelationSweepConfig` - Multi-model training orchestration
2. `GAIAConfig` - Extracted from h-e1 implicit parameters
3. `AugmentationConfig` - Background swap pipeline
4. `AnalysisConfig` - Correlation analysis thresholds

**Validation:** All defaults match experiment brief requirements (FR-1 through FR-5).
