# Configuration Specification: h-m1

**Date:** 2026-08-28  
**Author:** Phase 3 Configuration Agent  
**Hypothesis:** Transformer backbones capture global weight dependencies while Equivariant GNN backbones capture local permutation-symmetric patterns  
**Type:** MECHANISM

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Config classes verified from h-e1 base code  
**Config Files Found:** h-e1/src/config.py  
**Pattern Used:** dataclass (inherited from h-e1)

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From Actual Code)

The following configs are inherited from h-e1:

```python
# From: h-e1/src/config.py (ACTUAL CODE)
@dataclass
class DataConfig:
    source: str = "timm"
    families: List[str] = None  # defaults to ["resnet", "vit", "efficientnet", "convnext"]
    num_models: int = 100
    train_split: float = 0.7
    val_split: float = 0.15
    test_split: float = 0.15
    cache_path: str = "./data/model_zoo_cache/"
    max_layer_size: int = 4096

@dataclass
class TrainingConfig:
    optimizer: str = "AdamW"
    lr: float = 1e-4
    weight_decay: float = 1e-5
    batch_size: int = 32
    epochs: int = 50
    early_stopping_patience: int = 10
    gradient_clip_max_norm: float = 1.0
    scheduler_T_max: int = 50
    scheduler_eta_min: float = 1e-6
```

**Verified from:** h-e1/src/config.py (actual implementation)

---

## Extended Configuration (Current Hypothesis)

### GNN Model Configuration

```python
@dataclass
class GNNConfig:
    """E(n)-Equivariant GNN architecture configuration."""
    hidden_dim: int = 128
    num_gnn_layers: int = 2
    num_classes: int = 4
    # k_neighbors unused (fully connected graph)
```

### Transformer Model Configuration (Inherited)

```python
@dataclass
class TransformerConfig:
    """Transformer architecture configuration (from h-e1)."""
    type: str = "transformer"
    d_model: int = 256
    nhead: int = 8
    num_layers: int = 6
    dim_feedforward: int = 1024
    dropout: float = 0.1
    num_classes: int = 4
```

### Multi-Model Configuration

```python
@dataclass
class ModelConfig:
    """Combined model configuration for h-m1."""
    transformer: TransformerConfig
    gnn: GNNConfig
```

### Perturbation Configuration

```python
@dataclass
class PerturbationConfig:
    """Perturbation protocol configuration."""
    seed: int = 42
    perturbation_types: List[str] = None  # defaults to ['within', 'across']
    
    def __post_init__(self):
        if self.perturbation_types is None:
            self.perturbation_types = ['within', 'across']
```

### Gate Configuration

```python
@dataclass
class GateConfig:
    """MUST_WORK gate thresholds."""
    gnn_differential_min: float = 0.30
    transformer_differential_max: float = 0.10
```

### Experiment Configuration

```python
@dataclass
class ExperimentConfig:
    """Complete experiment configuration for h-m1."""
    data: DataConfig
    models: ModelConfig
    training: TrainingConfig
    perturbation: PerturbationConfig
    gate: GateConfig
    random_seed: int = 42
    device: str = "cuda"
    output_dir: str = "./h-m1/"


def get_default_config() -> ExperimentConfig:
    """Returns default configuration for h-m1 experiment."""
    return ExperimentConfig(
        data=DataConfig(),
        models=ModelConfig(
            transformer=TransformerConfig(),
            gnn=GNNConfig()
        ),
        training=TrainingConfig(),
        perturbation=PerturbationConfig(),
        gate=GateConfig()
    )
```

---

## Validation Logic

```python
def validate_config(config: ExperimentConfig) -> None:
    """Validate configuration parameters."""
    # Inherit h-e1 validation for data, training, general
    # (see h-e1/src/config.py validate_config for full list)
    
    # GNN-specific validation
    assert config.models.gnn.hidden_dim > 0, "gnn hidden_dim must be positive"
    assert config.models.gnn.num_gnn_layers > 0, "num_gnn_layers must be positive"
    assert config.models.gnn.num_classes > 1, "gnn num_classes must be > 1"
    
    # Perturbation validation
    assert config.perturbation.seed >= 0, "perturbation seed must be non-negative"
    assert len(config.perturbation.perturbation_types) > 0, "perturbation_types cannot be empty"
    valid_types = {'within', 'across'}
    for pt in config.perturbation.perturbation_types:
        assert pt in valid_types, f"perturbation_type {pt} not in {valid_types}"
    
    # Gate validation
    assert 0 < config.gate.gnn_differential_min < 1, "gnn_differential_min must be in (0, 1)"
    assert 0 < config.gate.transformer_differential_max < 1, "transformer_differential_max must be in (0, 1)"
```

---

## Environment Configuration (Inherited)

```python
# Reuse from h-e1/src/config.py
from h_e1.src.config import setup_environment

# Usage:
setup_environment(config)
```

---

## Usage Example

```python
# Load default config
config = get_default_config()

# Validate
validate_config(config)

# Setup environment (from h-e1)
from h_e1.src.config import setup_environment
setup_environment(config)

# Access parameters
print(f"GNN hidden dim: {config.models.gnn.hidden_dim}")
print(f"Transformer d_model: {config.models.transformer.d_model}")
print(f"Perturbation types: {config.perturbation.perturbation_types}")
print(f"Gate thresholds: GNN>{config.gate.gnn_differential_min}, Transformer<{config.gate.transformer_differential_max}")
```

---

## Configuration Notes

**Design Decisions:**
- **Inherited pattern**: dataclass from h-e1 for consistency
- **Multi-model support**: Separate configs for Transformer and GNN
- **Reuse h-e1 configs**: DataConfig, TrainingConfig unchanged
- **New configs**: GNNConfig, PerturbationConfig, GateConfig

**MECHANISM Simplifications:**
- Single fixed configuration (no sweeps)
- Fixed seed=42
- Gate thresholds from PRD

**Verified Field Names:**
- `lr` not `learning_rate` (from h-e1 actual code)
- `optimizer` = "AdamW" (from h-e1 actual code)
- `num_models` not `model_count` (from h-e1 actual code)

---

*Configuration Status: FINAL*  
*Next Phase: Phase 4 - Implementation*
