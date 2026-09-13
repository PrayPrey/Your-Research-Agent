# Configuration Specification: h-e1 — Clusterability Diagnostic

**Date:** 2026-03-19
**Author:** Phase 3 Configuration Design
**Hypothesis:** h-e1 (EXISTENCE)
**Applied:** PyTorch dataclass config pattern, SSL hyperparameter defaults

---

## Configuration Schema

### DataConfig
```python
@dataclass
class DataConfig:
    data_dir: str = "./data/waterbird_complete95_forest2water2"
    batch_size: int = 256  # SimCLR: 256 (LARS optimizer compatible)
    num_workers: int = 4
    image_size: int = 224
    mean: Tuple[float, float, float] = (0.485, 0.456, 0.406)  # ImageNet
    std: Tuple[float, float, float] = (0.229, 0.224, 0.225)
```

### SimCLRConfig
```python
@dataclass
class SimCLRConfig:
    encoder: str = 'resnet50'
    projection_dim: int = 128
    pretrained: bool = False  # Train from scratch
    temperature: float = 0.5  # NT-Xent temperature
    epochs: int = 200
    lr: float = 0.3  # LARS: 0.3 × (batch_size/256)
    weight_decay: float = 1e-6
    momentum: float = 0.9
    checkpoint_epochs: List[int] = field(default_factory=lambda: [50, 100, 150, 200])
```

### LinearProbeConfig
```python
@dataclass
class LinearProbeConfig:
    input_dim: int = 2048
    num_classes: int = 2
    epochs: int = 20
    batch_size: int = 32
    # Grid search ranges
    lr_grid: List[float] = field(default_factory=lambda: [0.01, 0.001, 0.0001])
    wd_grid: List[float] = field(default_factory=lambda: [1e-4, 1e-5, 1e-6])
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])
```

### ClusteringConfig
```python
@dataclass
class ClusteringConfig:
    n_clusters: int = 4  # 4 subgroups in Waterbirds
    random_state: int = 42
    n_init: int = 10  # K-means restarts
    ami_threshold_high: float = 0.4  # High clusterability
    ami_threshold_low: float = 0.3   # Low clusterability
```

### ExperimentConfig
```python
@dataclass
class ExperimentConfig:
    data: DataConfig = field(default_factory=DataConfig)
    simclr: SimCLRConfig = field(default_factory=SimCLRConfig)
    linear_probe: LinearProbeConfig = field(default_factory=LinearProbeConfig)
    clustering: ClusteringConfig = field(default_factory=ClusteringConfig)
    
    # Paths
    output_dir: str = "./outputs"
    checkpoint_dir: str = "./outputs/checkpoints"
    results_dir: str = "./outputs/results"
    
    # Device
    device: str = "cuda"
    seed: int = 42
```

---

## YAML Example

```yaml
data:
  data_dir: "./data/waterbird_complete95_forest2water2"
  batch_size: 256
  num_workers: 4

simclr:
  epochs: 200
  lr: 0.3
  temperature: 0.5

linear_probe:
  lr_grid: [0.01, 0.001, 0.0001]
  wd_grid: [1e-4, 1e-5, 1e-6]
  seeds: [0, 1, 2, 3, 4]

clustering:
  n_clusters: 4
  ami_threshold_high: 0.4
  ami_threshold_low: 0.3

device: cuda
seed: 42
```

---

**Subtasks:** 4 (A-3: 2 subtasks, A-5: 2 subtasks)
**Status:** Complete
