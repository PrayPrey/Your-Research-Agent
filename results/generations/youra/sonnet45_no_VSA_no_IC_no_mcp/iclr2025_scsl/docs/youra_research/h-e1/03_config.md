# Configuration Schema: h-e1

**Generated**: 2026-08-24  
**Hypothesis ID**: h-e1  
**Hypothesis Type**: EXISTENCE  
**Complexity**: Tier 1 (Simple)

---

## Codebase Analysis

**Project Type**: Green-field  
**Status**: New config design (no existing code)  
**Config Files Found**: None  
**Pattern Used**: Dataclass + YAML

---

## config.yaml

```yaml
# Experiment Configuration for h-e1: BN-LN Worst-Group Gap Difference

data:
  dataset_name: "waterbirds"
  data_dir: "./data/waterbirds/"
  batch_size: 64
  num_workers: 4
  image_size: 224
  normalize_mean: [0.485, 0.456, 0.406]
  normalize_std: [0.229, 0.224, 0.225]

model:
  architecture_names: ["ResNet-18-BN", "ResNet-18-LN"]
  num_classes: 2
  pretrained: false
  init_mode: "kaiming_normal"

training:
  optimizer: "SGD"
  learning_rate: 0.01
  momentum: 0.9
  weight_decay: 0.0001
  epochs: 100
  seeds: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
  device: "cuda"

evaluation:
  target_accuracy: 0.90
  significance_level: 0.05
  min_effect_size: 0.8
  min_gap_difference: 5.0

output:
  results_dir: "results/h-e1/"
  metrics_file: "training_metrics.csv"
  stats_file: "statistical_test.txt"
  plot_file: "gap_comparison.png"
```

---

## Python Schema

```python
from dataclasses import dataclass, field
from typing import List


@dataclass
class DataConfig:
    dataset_name: str = "waterbirds"
    data_dir: str = "./data/waterbirds/"
    batch_size: int = 64
    num_workers: int = 4
    image_size: int = 224
    normalize_mean: List[float] = field(default_factory=lambda: [0.485, 0.456, 0.406])
    normalize_std: List[float] = field(default_factory=lambda: [0.229, 0.224, 0.225])


@dataclass
class ModelConfig:
    architecture_names: List[str] = field(default_factory=lambda: ["ResNet-18-BN", "ResNet-18-LN"])
    num_classes: int = 2
    pretrained: bool = False
    init_mode: str = "kaiming_normal"


@dataclass
class TrainingConfig:
    optimizer: str = "SGD"
    learning_rate: float = 0.01
    momentum: float = 0.9
    weight_decay: float = 0.0001
    epochs: int = 100
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
    device: str = "cuda"


@dataclass
class EvaluationConfig:
    target_accuracy: float = 0.90
    significance_level: float = 0.05
    min_effect_size: float = 0.8
    min_gap_difference: float = 5.0


@dataclass
class OutputConfig:
    results_dir: str = "results/h-e1/"
    metrics_file: str = "training_metrics.csv"
    stats_file: str = "statistical_test.txt"
    plot_file: str = "gap_comparison.png"


@dataclass
class ExperimentConfig:
    data: DataConfig = field(default_factory=DataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
```

---

## Hyperparameter Justification

### Data Configuration
- `batch_size=64`: Standard ResNet batch size from Torchvision examples
- `normalize_mean/std`: ImageNet pretrained statistics (Waterbirds uses ImageNet backgrounds)

### Training Configuration
- `learning_rate=0.01`: Constant LR per Phase 2B (isolates architectural effects, no confounding from LR schedule)
- `momentum=0.9, weight_decay=1e-4`: Standard SGD configuration for ResNet
- `epochs=100`: Sufficient for 90% accuracy convergence based on Sagawa et al. 2020 benchmarks
- `seeds=[0-9]`: 10 seeds provide 80% statistical power for 2pp effect at α=0.05

### Evaluation Configuration
- `target_accuracy=0.90`: Accuracy-matched comparison point (eliminates training speed confound)
- `min_gap_difference=5.0`: Clinical significance threshold (5 percentage points)
- `min_effect_size=0.8`: Large effect per Cohen's d standards

---

## Usage Example

```python
import yaml
from dataclasses import asdict

# Load from YAML
with open("config.yaml") as f:
    config_dict = yaml.safe_load(f)

config = ExperimentConfig(
    data=DataConfig(**config_dict["data"]),
    model=ModelConfig(**config_dict["model"]),
    training=TrainingConfig(**config_dict["training"]),
    evaluation=EvaluationConfig(**config_dict["evaluation"]),
    output=OutputConfig(**config_dict["output"])
)

# Access config
print(f"Training with LR={config.training.learning_rate} for {config.training.epochs} epochs")
print(f"Seeds: {config.training.seeds}")
```

---

## Validation

- Single format (dataclass): Copy-paste ready
- EXISTENCE hypothesis: Fixed config, no hyperparameter grid
- 10 seeds: Statistical power verified in Phase 2B
- No LR schedule: Controlled variable per experiment brief
