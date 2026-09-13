# Configuration Schema: H-E1 Gradient Abnormality Detection

**Hypothesis:** h-e1  
**Type:** EXISTENCE  
**Version:** 1.0  
**Date:** 2026-08-20

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase  
**Status:** config pattern verified from h-e1/code/config.py  
**Config Files Found:** h-e1/code/config.py  
**Pattern Used:** dataclass with YAML serialization

---

## Configuration Format

**Format:** Python dataclasses with YAML serialization  
**Applied:** Existing h-e1 pattern (dataclass hierarchy with from_yaml/to_yaml methods)

---

## Configuration Classes

### 1. PathsConfig

```python
@dataclass
class PathsConfig:
    data_root: str = "./data"
    dataset_cache: str = "${data_root}/wilds_cache"
    checkpoints_dir: str = "./checkpoints"
    outputs_dir: str = "./outputs"
    plots_dir: str = "./plots"
```

### 2. ModelConfig

```python
@dataclass
class ModelConfig:
    architecture: str = "resnet50"
    pretrained: bool = True
    num_classes: int = 2
    target_layer: str = "layer4"  # GradCAM target
```

### 3. TrainingConfig

```python
@dataclass
class TrainingConfig:
    # Optimizer
    optimizer: str = "sgd"
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    
    # Scheduler
    scheduler: str = "cosine"
    T_max: int = 300
    eta_min: float = 0.0
    
    # Training loop
    batch_size: int = 128
    epochs: int = 300
    num_workers: int = 4
    
    # Early stopping
    early_stop_patience: int = 50
    early_stop_monitor: str = "worst_group_accuracy"
    
    # Checkpointing
    save_best: bool = True
    save_last: bool = True
    save_every_n_epochs: int = 50
```

### 4. EvaluationConfig

```python
@dataclass
class EvaluationConfig:
    # Training quality gates
    wga_threshold: float = 0.80  # Must be < this
    minority_acc_threshold: float = 0.60  # Must be >= this
    avg_acc_threshold: float = 0.95  # Must be > this
    
    # GAIA-Z computation
    gaia_z_epsilon: float = 1e-6  # Near-zero threshold
    
    # Statistical test thresholds
    divergence_threshold: float = 0.2  # Must be >= this
    p_value_threshold: float = 0.01  # Must be < this
    cohens_d_threshold: float = 0.8  # Must be >= this
```

### 5. ReproducibilityConfig

```python
@dataclass
class ReproducibilityConfig:
    seed: int = 42
    deterministic: bool = True
    cudnn_benchmark: bool = False
```

### 6. GradCAMConfig

```python
@dataclass
class GradCAMConfig:
    target_layer: str = "layer4"
    use_cuda: bool = True
    batch_size: int = 32  # Inference batch size
```

### 7. LoggingConfig

```python
@dataclass
class LoggingConfig:
    use_tensorboard: bool = False
    log_interval: int = 10  # Log every N batches
    save_training_log: bool = True
    training_log_path: str = "${outputs_dir}/training_log.csv"
```

### 8. ExperimentConfig (Root)

```python
@dataclass
class ExperimentConfig:
    experiment_name: str = "h_e1_gradient_detection"
    
    # Sub-configs
    paths: PathsConfig
    model: ModelConfig
    training: TrainingConfig
    evaluation: EvaluationConfig
    reproducibility: ReproducibilityConfig
    gradcam: GradCAMConfig
    logging: LoggingConfig
    
    @classmethod
    def from_yaml(cls, path: str):
        with open(path, 'r') as f:
            config_dict = yaml.safe_load(f)
        
        # Resolve environment variable placeholders
        config_dict = cls._resolve_placeholders(config_dict)
        
        return cls(
            experiment_name=config_dict.get('experiment_name', 'h_e1_gradient_detection'),
            paths=PathsConfig(**config_dict['paths']),
            model=ModelConfig(**config_dict['model']),
            training=TrainingConfig(**config_dict['training']),
            evaluation=EvaluationConfig(**config_dict['evaluation']),
            reproducibility=ReproducibilityConfig(**config_dict['reproducibility']),
            gradcam=GradCAMConfig(**config_dict['gradcam']),
            logging=LoggingConfig(**config_dict['logging'])
        )
    
    @staticmethod
    def _resolve_placeholders(config_dict):
        """Replace ${var} with values from paths or environment."""
        import os
        import re
        
        def resolve(value, context):
            if isinstance(value, str):
                pattern = r'\$\{([^}]+)\}'
                matches = re.findall(pattern, value)
                for match in matches:
                    replacement = context.get(match, os.environ.get(match, match))
                    value = value.replace(f'${{{match}}}', str(replacement))
            return value
        
        paths_context = config_dict.get('paths', {})
        for section in config_dict.values():
            if isinstance(section, dict):
                for key, val in section.items():
                    section[key] = resolve(val, paths_context)
        
        return config_dict
    
    def to_yaml(self, path: str):
        config_dict = {
            'experiment_name': self.experiment_name,
            'paths': self.paths.__dict__,
            'model': self.model.__dict__,
            'training': self.training.__dict__,
            'evaluation': self.evaluation.__dict__,
            'reproducibility': self.reproducibility.__dict__,
            'gradcam': self.gradcam.__dict__,
            'logging': self.logging.__dict__
        }
        with open(path, 'w') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
```

---

## Complete config.yaml Template

```yaml
experiment_name: h_e1_gradient_detection

# Paths
paths:
  data_root: ./data
  dataset_cache: ${data_root}/wilds_cache
  checkpoints_dir: ./checkpoints
  outputs_dir: ./outputs
  plots_dir: ./plots

# Model architecture
model:
  architecture: resnet50
  pretrained: true
  num_classes: 2
  target_layer: layer4  # GradCAM extraction layer

# Training configuration
training:
  # Optimizer (from model_spec.yaml)
  optimizer: sgd
  lr: 0.001
  momentum: 0.9
  weight_decay: 0.0001
  
  # Scheduler (from model_spec.yaml)
  scheduler: cosine
  T_max: 300
  eta_min: 0.0
  
  # Training loop
  batch_size: 128
  epochs: 300
  num_workers: 4
  
  # Early stopping (from model_spec.yaml)
  early_stop_patience: 50
  early_stop_monitor: worst_group_accuracy
  
  # Checkpointing
  save_best: true
  save_last: true
  save_every_n_epochs: 50

# Evaluation thresholds (from metrics_spec.yaml)
evaluation:
  # Training quality gates
  wga_threshold: 0.80       # Worst-group accuracy MUST BE < 0.80
  minority_acc_threshold: 0.60  # Minority accuracy MUST BE >= 0.60
  avg_acc_threshold: 0.95   # Average accuracy MUST BE > 0.95
  
  # GAIA-Z computation (from metrics_spec.yaml)
  gaia_z_epsilon: 1.0e-6    # Near-zero threshold
  
  # Statistical test thresholds (from metrics_spec.yaml)
  divergence_threshold: 0.2     # GAIA-Z divergence MUST BE >= 0.2
  p_value_threshold: 0.01       # p-value MUST BE < 0.01
  cohens_d_threshold: 0.8       # Cohen's d MUST BE >= 0.8

# Reproducibility (from model_spec.yaml)
reproducibility:
  seed: 42
  deterministic: true
  cudnn_benchmark: false

# GradCAM configuration
gradcam:
  target_layer: layer4
  use_cuda: true
  batch_size: 32  # Inference batch size for gradient extraction

# Logging
logging:
  use_tensorboard: false
  log_interval: 10  # Log every N batches
  save_training_log: true
  training_log_path: ${outputs_dir}/training_log.csv
```

---

## Validation Rules

### Constraint Checks

```python
def validate_config(config: ExperimentConfig):
    """Validate configuration constraints."""
    errors = []
    
    # Training constraints
    if config.training.batch_size <= 0:
        errors.append("training.batch_size must be > 0")
    if config.training.lr <= 0:
        errors.append("training.lr must be > 0")
    if config.training.epochs <= 0:
        errors.append("training.epochs must be > 0")
    if config.training.weight_decay < 0:
        errors.append("training.weight_decay must be >= 0")
    if config.training.momentum < 0 or config.training.momentum >= 1:
        errors.append("training.momentum must be in [0, 1)")
    
    # Evaluation constraints
    if not (0 < config.evaluation.wga_threshold < 1):
        errors.append("evaluation.wga_threshold must be in (0, 1)")
    if not (0 < config.evaluation.minority_acc_threshold <= 1):
        errors.append("evaluation.minority_acc_threshold must be in (0, 1]")
    if not (0 < config.evaluation.avg_acc_threshold <= 1):
        errors.append("evaluation.avg_acc_threshold must be in (0, 1]")
    if config.evaluation.gaia_z_epsilon <= 0:
        errors.append("evaluation.gaia_z_epsilon must be > 0")
    if config.evaluation.divergence_threshold < 0:
        errors.append("evaluation.divergence_threshold must be >= 0")
    if not (0 < config.evaluation.p_value_threshold < 1):
        errors.append("evaluation.p_value_threshold must be in (0, 1)")
    
    # GradCAM constraints
    if config.gradcam.batch_size <= 0:
        errors.append("gradcam.batch_size must be > 0")
    
    if errors:
        raise ValueError("Config validation failed:\n" + "\n".join(f"  - {e}" for e in errors))
```

---

## Environment Variables

### Optional Overrides

```bash
# GPU device selection
export CUDA_VISIBLE_DEVICES=0

# Data root override
export DATA_ROOT=/path/to/data

# Checkpoint directory override
export CHECKPOINT_DIR=/path/to/checkpoints

# Random seed override
export EXPERIMENT_SEED=42
```

### Usage in Code

```python
import os

# Override from environment if set
config.paths.data_root = os.environ.get('DATA_ROOT', config.paths.data_root)
config.paths.checkpoints_dir = os.environ.get('CHECKPOINT_DIR', config.paths.checkpoints_dir)
config.reproducibility.seed = int(os.environ.get('EXPERIMENT_SEED', config.reproducibility.seed))
```

---

## Reproducibility Settings

### Seed Initialization

```python
import torch
import numpy as np
import random

def set_seed(config: ReproducibilityConfig):
    """Set random seeds for reproducibility."""
    seed = config.seed
    
    # Python random
    random.seed(seed)
    
    # Numpy
    np.random.seed(seed)
    
    # PyTorch
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    
    # CuDNN
    if config.deterministic:
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False
    else:
        torch.backends.cudnn.benchmark = config.cudnn_benchmark
```

---

## Hardware Profiles

### Minimum Configuration (8GB GPU)

```yaml
training:
  batch_size: 64  # Reduced from 128
  num_workers: 2

gradcam:
  batch_size: 16  # Reduced from 32
```

**Expected runtime:** ~4-5 hours training

### Recommended Configuration (RTX 3080, 16GB GPU)

```yaml
training:
  batch_size: 128
  num_workers: 4

gradcam:
  batch_size: 32
```

**Expected runtime:** ~3 hours training

### High-End Configuration (A100, 40GB GPU)

```yaml
training:
  batch_size: 256
  num_workers: 8

gradcam:
  batch_size: 64
```

**Expected runtime:** ~1.5 hours training

---

## Usage Examples

### Loading Configuration

```python
# From YAML file
config = ExperimentConfig.from_yaml('config.yaml')

# Validate
validate_config(config)

# Set seeds
set_seed(config.reproducibility)

# Use in training
optimizer = torch.optim.SGD(
    model.parameters(),
    lr=config.training.lr,
    momentum=config.training.momentum,
    weight_decay=config.training.weight_decay
)
```

### Creating Default Configuration

```python
# Programmatic defaults
config = ExperimentConfig(
    experiment_name="h_e1_gradient_detection",
    paths=PathsConfig(),
    model=ModelConfig(),
    training=TrainingConfig(),
    evaluation=EvaluationConfig(),
    reproducibility=ReproducibilityConfig(),
    gradcam=GradCAMConfig(),
    logging=LoggingConfig()
)

# Save to file
config.to_yaml('config.yaml')
```

### Runtime Configuration Adjustment

```python
# Adjust for available GPU memory
if torch.cuda.get_device_properties(0).total_memory < 10 * 1024**3:  # < 10GB
    config.training.batch_size = 64
    config.gradcam.batch_size = 16
    print("Adjusted batch sizes for limited GPU memory")
```

---

## Output Files Generated

### Training Outputs

| File | Path | Description |
|------|------|-------------|
| Training log | `outputs/training_log.csv` | Per-epoch metrics (loss, acc, WGA) |
| Best checkpoint | `checkpoints/best_model.pth` | Highest WGA checkpoint |
| Final checkpoint | `checkpoints/final_model.pth` | Last epoch checkpoint |

### Evaluation Outputs

| File | Path | Description |
|------|------|-------------|
| GAIA-Z scores | `outputs/gaia_z_scores.csv` | Per-sample scores (5794 rows) |
| Statistical results | `outputs/statistical_results.json` | Hypothesis test results |
| Summary table | `outputs/statistical_summary.csv` | Group-level statistics |

### Visualizations

| File | Path | Description |
|------|------|-------------|
| Box plot (type) | `plots/gaia_z_boxplot_by_type.png` | Minority vs majority |
| Box plot (group) | `plots/gaia_z_boxplot_by_group.png` | Per-group (0-3) |
| Histogram | `plots/gaia_z_histogram.png` | Distribution overlay |

---

## Configuration File Location

**Recommended path:** `/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_scsl/h-e1/config.yaml`

**Python class location:** `/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_scsl/h-e1/code/config.py` (extend existing classes)

---

## Summary

- **Format:** Dataclass hierarchy matching existing h-e1/code/config.py pattern
- **Defaults:** All values from model_spec.yaml and metrics_spec.yaml
- **Validation:** Runtime constraint checking prevents invalid configurations
- **Reproducibility:** Deterministic training with seed=42, cudnn settings
- **Hardware profiles:** Three presets (8GB/16GB/40GB GPU)
- **Extensibility:** YAML serialization, environment variable support, placeholder resolution
