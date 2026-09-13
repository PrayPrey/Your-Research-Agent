# Configuration Design: h-e1

**Version:** 1.0
**Date:** 2026-08-29
**Hypothesis:** h-e1 (EXISTENCE)

---

Applied: Dataclass Configuration Pattern (Archon KB)
Applied: YAML-First Configuration Pattern

---

## Configuration Schema

### experiment_config.yaml

```yaml
# h-e1 Experiment Configuration
experiment:
  name: "h-e1-duality-existence"
  hypothesis_id: "h-e1"
  type: "EXISTENCE"
  seed: 42

# Model Configuration
model:
  source:
    name: "bert-base-uncased"
    source: "huggingface"
    cache_dir: "~/.cache/huggingface"
  
  ssm:
    d_state: 64
    target_layer: 0  # Convert layer 0 attention only for PoC

# Data Configuration
data:
  dataset:
    name: "wikitext"
    config: "wikitext-103-raw-v1"
    split: "validation"
    cache_dir: "~/.cache/huggingface/datasets"
  
  preprocessing:
    min_length: 512
    max_length: 2048
    num_samples: 100
    batch_size: 8

# Validation Thresholds
validation:
  nan_inf_threshold: 0.0  # Must be exactly 0%
  magnitude_ratio_threshold: 10.0  # Must be < 10x
  
# Output Configuration
output:
  results_dir: "results/"
  figures_dir: "figures/"
  save_intermediate: false

# Hardware
hardware:
  device: "cuda"  # or "cpu"
  dtype: "float32"  # Use fp32 for stability validation
```

---

## Python Dataclasses

### config.py

```python
from dataclasses import dataclass, field
from typing import Optional, List
from pathlib import Path

@dataclass
class SourceModelConfig:
    """BERT source model configuration."""
    name: str = "bert-base-uncased"
    source: str = "huggingface"
    cache_dir: str = "~/.cache/huggingface"

@dataclass
class SSMConfig:
    """SSM conversion parameters."""
    d_state: int = 64
    target_layer: int = 0

@dataclass
class ModelConfig:
    """Combined model configuration."""
    source: SourceModelConfig = field(default_factory=SourceModelConfig)
    ssm: SSMConfig = field(default_factory=SSMConfig)

@dataclass
class DatasetConfig:
    """Dataset loading configuration."""
    name: str = "wikitext"
    config: str = "wikitext-103-raw-v1"
    split: str = "validation"
    cache_dir: str = "~/.cache/huggingface/datasets"

@dataclass
class PreprocessingConfig:
    """Data preprocessing parameters."""
    min_length: int = 512
    max_length: int = 2048
    num_samples: int = 100
    batch_size: int = 8

@dataclass
class DataConfig:
    """Combined data configuration."""
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    preprocessing: PreprocessingConfig = field(default_factory=PreprocessingConfig)

@dataclass
class ValidationConfig:
    """Validation thresholds for gate condition."""
    nan_inf_threshold: float = 0.0
    magnitude_ratio_threshold: float = 10.0

@dataclass
class OutputConfig:
    """Output paths configuration."""
    results_dir: str = "results/"
    figures_dir: str = "figures/"
    save_intermediate: bool = False

@dataclass
class HardwareConfig:
    """Hardware settings."""
    device: str = "cuda"
    dtype: str = "float32"

@dataclass
class ExperimentConfig:
    """Top-level experiment configuration."""
    name: str = "h-e1-duality-existence"
    hypothesis_id: str = "h-e1"
    type: str = "EXISTENCE"
    seed: int = 42
    
    model: ModelConfig = field(default_factory=ModelConfig)
    data: DataConfig = field(default_factory=DataConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    hardware: HardwareConfig = field(default_factory=HardwareConfig)

def load_config(path: str = "configs/experiment_config.yaml") -> ExperimentConfig:
    """Load configuration from YAML file."""
    import yaml
    from dacite import from_dict
    
    with open(path) as f:
        data = yaml.safe_load(f)
    
    return from_dict(data_class=ExperimentConfig, data=data)
```

---

## Default Values Justification

| Parameter | Default | Justification |
|-----------|---------|---------------|
| `d_state` | 64 | Standard Mamba state dimension, balances expressivity vs memory |
| `target_layer` | 0 | PoC validates single layer; multi-layer in h-m1 |
| `num_samples` | 100 | Sufficient for existence check; not for statistical significance |
| `min_length` | 512 | Ensures enough context for SSM dynamics |
| `max_length` | 2048 | Memory-efficient for batch_size=8 |
| `batch_size` | 8 | Fits 16GB GPU with 2048-token sequences |
| `magnitude_ratio_threshold` | 10.0 | Order of magnitude tolerance for initialization |
| `seed` | 42 | Reproducibility |

---

## Environment Variables

```bash
# Optional overrides
export HF_HOME="~/.cache/huggingface"
export CUDA_VISIBLE_DEVICES="0"
export PYTORCH_CUDA_ALLOC_CONF="max_split_size_mb:512"
```

---

## Subtasks (from E-2: Data Pipeline - Low Complexity)

| Subtask | Description |
|---------|-------------|
| E-2.1 | Create experiment_config.yaml with defaults |
| E-2.2 | Implement config.py dataclasses |

---

*Configuration design for EXISTENCE hypothesis*
*Next: Complexity Assessment (Step 6)*
