# Configuration Schema: h-c1

**Generated**: 2026-08-25  
**Hypothesis ID**: h-c1  
**Hypothesis Type**: CONDITION  
**Gate**: SHOULD_WORK  
**Prerequisites**: h-e1 (VALIDATED)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: h-e1 specs verified (no actual code yet - green-field for both)  
**Config Files Found**: None - extending h-e1 dataclass schema  
**Pattern Used**: Dataclass (consistent with h-e1)

**Applied**: Standard PyTorch training patterns from Archon KB

---

## Core Configuration

### Base Configuration (Inherited from h-e1)

```python
from dataclasses import dataclass, field
from typing import List, Literal


@dataclass
class BaseDataConfig:
    """Shared data configuration for both datasets."""
    batch_size: int = 64
    num_workers: int = 4
    image_size: int = 224
    normalize_mean: List[float] = field(default_factory=lambda: [0.485, 0.456, 0.406])
    normalize_std: List[float] = field(default_factory=lambda: [0.229, 0.224, 0.225])


@dataclass
class WaterbirdsDataConfig(BaseDataConfig):
    """Waterbirds dataset configuration (from h-e1)."""
    dataset_name: str = "waterbirds"
    data_dir: str = "./data/waterbirds/"


@dataclass
class CelebADataConfig(BaseDataConfig):
    """CelebA dataset configuration (new for h-c1)."""
    dataset_name: str = "celeba"
    data_dir: str = "./data/celeba/"
    center_crop_size: int = 178  # CelebA-specific preprocessing
    target_attribute: str = "Blond_Hair"
    spurious_attribute: str = "Male"


@dataclass
class ModelConfig:
    """Model architecture configuration."""
    architecture_names: List[str] = field(default_factory=lambda: ["ResNet-18-BN", "ResNet-18-LN"])
    num_classes: int = 2
    pretrained: bool = False
    init_mode: str = "kaiming_normal"


@dataclass
class TrainingConfig:
    """Training hyperparameters (from h-e1)."""
    optimizer: str = "SGD"
    learning_rate: float = 0.01
    momentum: float = 0.9
    weight_decay: float = 0.0001
    max_epochs: int = 100
    target_avg_accuracy: float = 0.90  # Early stop threshold
    seeds: List[int] = field(default_factory=lambda: list(range(10)))
    device: str = "cuda"


@dataclass
class RankingConfig:
    """Ranking and correlation analysis configuration."""
    correlation_method: Literal["spearman", "kendall"] = "spearman"
    success_threshold: float = 0.8  # ρ > 0.8 = PASSED
    failure_threshold: float = 0.6  # ρ < 0.6 = FAILED
    significance_level: float = 0.05


@dataclass
class OutputConfig:
    """Output paths and filenames."""
    results_dir: str = "results/h-c1/"
    waterbirds_metrics_file: str = "waterbirds_metrics.csv"
    celeba_metrics_file: str = "celeba_metrics.csv"
    ranking_file: str = "architecture_rankings.json"
    correlation_file: str = "correlation_stats.json"


@dataclass
class ExperimentConfig:
    """Full experiment configuration for h-c1."""
    waterbirds: WaterbirdsDataConfig = field(default_factory=WaterbirdsDataConfig)
    celeba: CelebADataConfig = field(default_factory=CelebADataConfig)
    model: ModelConfig = field(default_factory=ModelConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    ranking: RankingConfig = field(default_factory=RankingConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
```

---

## Configuration Rationale

### Reused from h-e1 (No Changes)
- `batch_size=64`: Validated in h-e1
- `learning_rate=0.01, momentum=0.9, weight_decay=1e-4`: Standard SGD for ResNet
- `max_epochs=100`: Sufficient for convergence on both datasets
- `seeds=0-9`: 10 seeds for statistical validity
- ImageNet normalization: Required for both datasets

### New for h-c1
- `center_crop_size=178`: CelebA standard preprocessing (before resize to 224×224)
- `target_avg_accuracy=0.90`: Early stop criterion (measure gap at accuracy-matched checkpoint)
- `correlation_method="spearman"`: Primary metric, Kendall as fallback
- `success_threshold=0.8`: Gate criterion from experiment brief

---

## Usage Example

```python
from config import ExperimentConfig

# Load config
config = ExperimentConfig()

# Access dataset-specific settings
print(f"Waterbirds: {config.waterbirds.data_dir}")
print(f"CelebA crop: {config.celeba.center_crop_size}")

# Access training settings
print(f"Training: LR={config.training.learning_rate}, Seeds={config.training.seeds}")

# Access ranking thresholds
print(f"Success: ρ > {config.ranking.success_threshold}")
```

---

## Validation Checklist

- [x] ONE format only (Dataclass)
- [x] No ASCII diagrams
- [x] Inherited h-e1 hyperparameters without modification
- [x] CelebA-specific preprocessing documented
- [x] Early stop threshold specified
- [x] Correlation thresholds match PRD (0.8 success, 0.6 failure)
- [x] Codebase Analysis section included
- [x] Total length < 400 lines
