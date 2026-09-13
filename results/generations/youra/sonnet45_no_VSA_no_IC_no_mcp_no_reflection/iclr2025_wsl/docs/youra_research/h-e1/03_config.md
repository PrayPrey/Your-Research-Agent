# Configuration Specification: h-e1

**Date:** 2026-08-28  
**Author:** Phase 3 Configuration Agent  
**Hypothesis:** Layer-wise weight tokenization for architecture family classification  
**Type:** EXISTENCE (PoC)

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New configuration schema - no existing code  
**Config Files Found:** None - new config  
**Pattern Used:** dataclass

---

## Configuration Schema (Python Dataclass)

```python
from dataclasses import dataclass
from typing import List


@dataclass
class DataConfig:
    """Data loading and preprocessing configuration."""
    source: str = "timm"
    families: List[str] = None
    num_models: int = 100
    train_split: float = 0.7
    val_split: float = 0.15
    test_split: float = 0.15
    cache_path: str = "./data/model_zoo_cache/"
    max_layer_size: int = 4096
    
    def __post_init__(self):
        if self.families is None:
            self.families = ["resnet", "vit", "efficientnet", "convnext"]


@dataclass
class ModelConfig:
    """Transformer architecture configuration."""
    type: str = "transformer"
    d_model: int = 256
    nhead: int = 8
    num_layers: int = 6
    dim_feedforward: int = 1024
    dropout: float = 0.1
    num_classes: int = 4


@dataclass
class TrainingConfig:
    """Training loop configuration."""
    optimizer: str = "AdamW"
    lr: float = 1e-4
    weight_decay: float = 1e-5
    batch_size: int = 32
    epochs: int = 50
    early_stopping_patience: int = 10
    gradient_clip_max_norm: float = 1.0
    scheduler_T_max: int = 50
    scheduler_eta_min: float = 1e-6


@dataclass
class EvaluationConfig:
    """Evaluation thresholds and baselines."""
    gate_threshold: float = 0.6
    random_baseline: float = 0.25
    stats_baseline: float = 0.35


@dataclass
class ExperimentConfig:
    """Complete experiment configuration."""
    data: DataConfig
    model: ModelConfig
    training: TrainingConfig
    evaluation: EvaluationConfig
    random_seed: int = 42
    device: str = "cuda"
    output_dir: str = "./h-e1/"


def get_default_config() -> ExperimentConfig:
    """Returns default configuration for h-e1 experiment."""
    return ExperimentConfig(
        data=DataConfig(),
        model=ModelConfig(),
        training=TrainingConfig(),
        evaluation=EvaluationConfig()
    )
```

---

## Validation Logic

```python
def validate_config(config: ExperimentConfig) -> None:
    """Validate configuration parameters."""
    # Data validation
    assert 0 < config.data.train_split < 1, "train_split must be in (0, 1)"
    assert 0 < config.data.val_split < 1, "val_split must be in (0, 1)"
    assert 0 < config.data.test_split < 1, "test_split must be in (0, 1)"
    assert abs(config.data.train_split + config.data.val_split + 
               config.data.test_split - 1.0) < 1e-6, "splits must sum to 1.0"
    assert config.data.num_models > 0, "num_models must be positive"
    assert config.data.max_layer_size > 0, "max_layer_size must be positive"
    
    # Model validation
    assert config.model.d_model > 0, "d_model must be positive"
    assert config.model.nhead > 0, "nhead must be positive"
    assert config.model.d_model % config.model.nhead == 0, "d_model must be divisible by nhead"
    assert config.model.num_layers > 0, "num_layers must be positive"
    assert config.model.dim_feedforward > 0, "dim_feedforward must be positive"
    assert 0 <= config.model.dropout < 1, "dropout must be in [0, 1)"
    assert config.model.num_classes > 1, "num_classes must be > 1"
    
    # Training validation
    assert 0 < config.training.lr < 1, "lr must be in (0, 1)"
    assert config.training.weight_decay >= 0, "weight_decay must be non-negative"
    assert config.training.batch_size > 0, "batch_size must be positive"
    assert config.training.epochs > 0, "epochs must be positive"
    assert config.training.early_stopping_patience > 0, "patience must be positive"
    assert config.training.gradient_clip_max_norm > 0, "gradient_clip_max_norm must be positive"
    assert config.training.scheduler_T_max > 0, "scheduler_T_max must be positive"
    assert 0 < config.training.scheduler_eta_min < config.training.lr, "eta_min must be in (0, lr)"
    
    # Evaluation validation
    assert 0 < config.evaluation.gate_threshold < 1, "gate_threshold must be in (0, 1)"
    
    # General validation
    assert config.random_seed >= 0, "random_seed must be non-negative"
    assert config.device in ["cuda", "cpu"], "device must be 'cuda' or 'cpu'"
```

---

## Environment Configuration

```python
import os

# Environment variables for reproducibility and resource management
ENV_CONFIG = {
    "PYTHONHASHSEED": str(42),
    "CUBLAS_WORKSPACE_CONFIG": ":4096:8",
    "OMP_NUM_THREADS": str(4),
    "MKL_NUM_THREADS": str(4),
}

def setup_environment(config: ExperimentConfig):
    """Configure environment for reproducible training."""
    # Set environment variables
    for key, value in ENV_CONFIG.items():
        os.environ[key] = value
    
    # Set random seeds
    import random
    import numpy as np
    import torch
    
    random.seed(config.random_seed)
    np.random.seed(config.random_seed)
    torch.manual_seed(config.random_seed)
    torch.cuda.manual_seed_all(config.random_seed)
    
    # Enable deterministic operations
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True)
    
    # Create output directory
    os.makedirs(config.output_dir, exist_ok=True)
    os.makedirs(os.path.join(config.output_dir, "figures"), exist_ok=True)
    os.makedirs(config.data.cache_path, exist_ok=True)
```

---

## Usage Example

```python
# Load default config
config = get_default_config()

# Validate
validate_config(config)

# Setup environment
setup_environment(config)

# Access parameters
print(f"Learning rate: {config.training.lr}")
print(f"Model dimension: {config.model.d_model}")
print(f"Gate threshold: {config.evaluation.gate_threshold}")
```

---

## Configuration Notes

**Design Decisions:**
- **dataclass over dict**: Type safety and IDE autocomplete
- **Nested configs**: Logical grouping (data/model/training/evaluation)
- **Defaults from PRD**: All values match PRD specifications exactly
- **Minimal validation**: Only critical constraints (no hyperparameter tuning logic for EXISTENCE)

**EXISTENCE Simplifications:**
- Single fixed configuration (no sweeps)
- No ablation variants
- No dynamic config loading (YAML omitted for PoC)

**Add Later (if hypothesis passes MUST_WORK gate):**
- YAML serialization/deserialization
- Hyperparameter sweep configs
- Ablation study variants
- Multi-seed experiment configs

---

*Configuration Status: FINAL*  
*Next Phase: Phase 4 - Implementation*
