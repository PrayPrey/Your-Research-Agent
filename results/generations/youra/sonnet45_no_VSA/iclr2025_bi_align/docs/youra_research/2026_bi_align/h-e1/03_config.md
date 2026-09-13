# Configuration Specification
## H-E1: Segment-level Memory Stress Index Profiler

**Hypothesis**: h-e1  
**Type**: EXISTENCE (PoC)  
**Version**: 1.0  
**Date**: 2026-07-10

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch  
**Config Files Found**: None - new config design  
**Pattern Used**: Python dataclass (consistent with archive pattern)

---

## Applied Patterns

**Applied**: Python dataclass configuration (from Archon KB standard PyTorch patterns)

---

## E1-5: Evaluation Harness [Complexity: 13, Budget: 2/8]

**Applied**: Standard PyTorch evaluation defaults

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class ErrorThresholds:
    """Error acceptance thresholds for EXISTENCE gate."""
    cnn_median: float = 0.10
    transformer_median: float = 0.15
    p95_all: float = 0.25


@dataclass
class StatisticalTest:
    """Wilcoxon test configuration."""
    method: str = "wilcoxon"
    alpha: float = 0.05
    alternative: str = "less"
    zero_method: str = "wilcox"


@dataclass
class ErrorMetrics:
    """Error computation results."""
    median_error: float
    p95_error: float
    ground_truth_mb: float
    predicted_mb: float


@dataclass
class EvaluationConfig:
    """ErrorAnalyzer and Visualizer configuration."""
    error_thresholds: ErrorThresholds = ErrorThresholds()
    statistical_test: StatisticalTest = StatisticalTest()
    
    results_dir: str = "./results"
    figures_dir: str = "./figures"
    
    export_csv: bool = True
    generate_plots: bool = True
```

### Subtasks [2/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Error threshold validation | Implement threshold checks for CNN/transformer median and P95 errors |
| C-5-2 | Statistical test execution | Implement Wilcoxon signed-rank test for 3-iter vs 2-iter comparison |

---

## E1-3: Model Registry [Complexity: 11, Budget: 2/8]

**Applied**: Standard PyTorch model defaults

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class ModelConfig:
    """Model initialization parameters."""
    name: str
    num_classes: int
    dataset_type: str  # "image" or "text"


@dataclass
class ModelRegistry:
    """16 models for memory profiling (8 CNNs + 8 transformers)."""
    
    cnn_models: list[str] = field(default_factory=lambda: [
        "resnet18",
        "resnet34",
        "resnet50",
        "vgg16",
        "densenet121",
        "mobilenet_v2",
        "efficientnet_b0",
        "shufflenet_v2_x1_0"
    ])
    
    transformer_models: list[str] = field(default_factory=lambda: [
        "bert-base-uncased",
        "roberta-base",
        "gpt2",
        "t5-small",
        "distilbert-base-uncased",
        "albert-base-v2",
        "microsoft/deberta-base",
        "google/vit-base-patch16-224"
    ])
    
    default_num_classes: int = 10
```

### Subtasks [2/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-3-1 | CNN model loading | Implement torchvision model loader for 8 CNN architectures |
| C-3-2 | Transformer model loading | Implement HuggingFace model loader for 8 transformer architectures |

---

## E1-8: Statistical Validation [Complexity: 10, Budget: 2/8]

**Applied**: Standard scipy.stats defaults

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class AblationConfig:
    """2-iteration vs 3-iteration protocol comparison."""
    baseline_iters: int = 2
    proposed_iters: int = 3
    use_stratified: bool = True  # Only for 3-iter protocol


@dataclass
class WilcoxonParams:
    """Wilcoxon signed-rank test parameters."""
    alternative: str = "less"  # 3-iter errors < 2-iter errors
    zero_method: str = "wilcox"
    correction: bool = False
    mode: str = "auto"


@dataclass
class StatisticalValidationConfig:
    """Ablation study and statistical testing."""
    ablation: AblationConfig = AblationConfig()
    wilcoxon: WilcoxonParams = WilcoxonParams()
    
    significance_level: float = 0.05
    export_ablation_results: bool = True
    ablation_csv: str = "ablation_2iter_results.csv"
```

### Subtasks [2/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | 2-iteration baseline profiling | Implement 2-iteration protocol without post-optimizer sampling |
| C-8-2 | Wilcoxon test comparison | Implement statistical test for 3-iter vs 2-iter error distributions |

---

## E1-1/E1-2/E1-4/E1-6/E1-7: Shared Experiment Configs [Complexity: 62, Budget: 2/8]

**Applied**: Standard PyTorch training defaults

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class DatasetConfig:
    """Dataset loading parameters."""
    root: str = "./data"
    batch_size: int = 128  # CIFAR-10 default
    max_length: int = 128  # WMT-14 token limit
    
    # Dataset-specific overrides
    imagenet_batch_size: int = 64
    wmt14_batch_size: int = 32


@dataclass
class StratifiedSamplingConfig:
    """Length-based stratification for transformers."""
    quantiles: list[float] = field(default_factory=lambda: [0.5, 0.75, 0.95, 0.99])
    min_samples_per_bin: int = 100
    enabled: bool = True  # Only for variable-length datasets


@dataclass
class OptimizerConfig:
    """Optimizer hyperparameters (Adam/AdamW/SGD)."""
    name: str  # "adam", "adamw", or "sgd"
    
    # Adam/AdamW defaults
    adam_lr: float = 0.0001
    adam_betas: tuple[float, float] = (0.9, 0.999)
    adamw_weight_decay: float = 0.01
    
    # SGD defaults
    sgd_lr: float = 0.1
    sgd_momentum: float = 0.9


@dataclass
class ProfilingConfig:
    """Memory profiling protocol settings."""
    device: str = "cuda:0"
    
    # Ground truth protocol
    num_ground_truth_iters: int = 10
    
    # Lightweight protocol
    num_lightweight_iters: int = 3  # iter1 + post-optim + stratified
    
    # Memory tracking
    reset_between_experiments: bool = True
    track_segment_level: bool = True  # Use torch.cuda.memory_stats()


@dataclass
class ExperimentConfig:
    """Master configuration for H-E1 experiment."""
    seed: int = 42
    device: str = "cuda:0"
    
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    stratified_sampling: StratifiedSamplingConfig = field(default_factory=StratifiedSamplingConfig)
    optimizer: OptimizerConfig = None  # Set per experiment
    profiling: ProfilingConfig = field(default_factory=ProfilingConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    statistical: StatisticalValidationConfig = field(default_factory=StatisticalValidationConfig)
    
    verbose: bool = True
    log_level: str = "INFO"
```

### Subtasks [2/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Dataset config instantiation | Create DatasetConfig instances for CIFAR-10, ImageNet, WMT-14 |
| C-1-2 | Optimizer config factory | Create OptimizerConfig instances for Adam, AdamW, SGD |

---

## Complete Configuration Example

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

# === Core Configs ===

@dataclass
class ErrorThresholds:
    cnn_median: float = 0.10
    transformer_median: float = 0.15
    p95_all: float = 0.25


@dataclass
class StatisticalTest:
    method: str = "wilcoxon"
    alpha: float = 0.05
    alternative: str = "less"
    zero_method: str = "wilcox"


@dataclass
class ErrorMetrics:
    median_error: float
    p95_error: float
    ground_truth_mb: float
    predicted_mb: float


@dataclass
class EvaluationConfig:
    error_thresholds: ErrorThresholds = field(default_factory=ErrorThresholds)
    statistical_test: StatisticalTest = field(default_factory=StatisticalTest)
    results_dir: str = "./results"
    figures_dir: str = "./figures"
    export_csv: bool = True
    generate_plots: bool = True


@dataclass
class ModelConfig:
    name: str
    num_classes: int
    dataset_type: str


@dataclass
class ModelRegistry:
    cnn_models: list[str] = field(default_factory=lambda: [
        "resnet18", "resnet34", "resnet50", "vgg16",
        "densenet121", "mobilenet_v2", "efficientnet_b0", "shufflenet_v2_x1_0"
    ])
    transformer_models: list[str] = field(default_factory=lambda: [
        "bert-base-uncased", "roberta-base", "gpt2", "t5-small",
        "distilbert-base-uncased", "albert-base-v2",
        "microsoft/deberta-base", "google/vit-base-patch16-224"
    ])
    default_num_classes: int = 10


@dataclass
class AblationConfig:
    baseline_iters: int = 2
    proposed_iters: int = 3
    use_stratified: bool = True


@dataclass
class WilcoxonParams:
    alternative: str = "less"
    zero_method: str = "wilcox"
    correction: bool = False
    mode: str = "auto"


@dataclass
class StatisticalValidationConfig:
    ablation: AblationConfig = field(default_factory=AblationConfig)
    wilcoxon: WilcoxonParams = field(default_factory=WilcoxonParams)
    significance_level: float = 0.05
    export_ablation_results: bool = True
    ablation_csv: str = "ablation_2iter_results.csv"


@dataclass
class DatasetConfig:
    root: str = "./data"
    batch_size: int = 128
    max_length: int = 128
    imagenet_batch_size: int = 64
    wmt14_batch_size: int = 32


@dataclass
class StratifiedSamplingConfig:
    quantiles: list[float] = field(default_factory=lambda: [0.5, 0.75, 0.95, 0.99])
    min_samples_per_bin: int = 100
    enabled: bool = True


@dataclass
class OptimizerConfig:
    name: Literal["adam", "adamw", "sgd"]
    adam_lr: float = 0.0001
    adam_betas: tuple[float, float] = (0.9, 0.999)
    adamw_weight_decay: float = 0.01
    sgd_lr: float = 0.1
    sgd_momentum: float = 0.9


@dataclass
class ProfilingConfig:
    device: str = "cuda:0"
    num_ground_truth_iters: int = 10
    num_lightweight_iters: int = 3
    reset_between_experiments: bool = True
    track_segment_level: bool = True


@dataclass
class ExperimentConfig:
    seed: int = 42
    device: str = "cuda:0"
    
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    stratified_sampling: StratifiedSamplingConfig = field(default_factory=StratifiedSamplingConfig)
    optimizer: OptimizerConfig = None
    profiling: ProfilingConfig = field(default_factory=ProfilingConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    statistical: StatisticalValidationConfig = field(default_factory=StatisticalValidationConfig)
    
    verbose: bool = True
    log_level: str = "INFO"


# === Helper Functions ===

def create_optimizer_config(name: Literal["adam", "adamw", "sgd"]) -> OptimizerConfig:
    """Factory function for optimizer configs."""
    return OptimizerConfig(name=name)


def set_global_seed(seed: int):
    """Ensure full reproducibility across libraries."""
    import random
    import numpy as np
    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
```

---

## Usage Examples

### Initialize Master Config

```python
config = ExperimentConfig()
set_global_seed(config.seed)
```

### Create Model Configs

```python
registry = ModelRegistry()

# CNN model config
cnn_config = ModelConfig(
    name="resnet18",
    num_classes=10,
    dataset_type="image"
)

# Transformer model config
transformer_config = ModelConfig(
    name="bert-base-uncased",
    num_classes=2,
    dataset_type="text"
)
```

### Create Optimizer Configs

```python
adam_config = create_optimizer_config("adam")
adamw_config = create_optimizer_config("adamw")
sgd_config = create_optimizer_config("sgd")
```

### Run Evaluation

```python
from src.eval.error_analysis import ErrorAnalyzer

analyzer = ErrorAnalyzer()
results = analyzer.aggregate_errors([0.05, 0.08, 0.12, 0.09])

# Check thresholds
thresholds = config.evaluation.error_thresholds
passed = results['median'] <= thresholds.cnn_median
```

---

## Configuration File Locations

```
experiments/
└── configs/
    └── default_config.py      # ExperimentConfig class definitions
```

---

## Validation Checklist

- [ ] All dataclass fields have default values
- [ ] Seed propagation to all random operations
- [ ] Error thresholds match PRD requirements (10/15/25%)
- [ ] Wilcoxon test parameters match scipy.stats signature
- [ ] Model registry contains exactly 8 CNNs + 8 transformers
- [ ] Optimizer configs cover Adam, AdamW, SGD
- [ ] Profiling iteration counts match protocol (2/3/10 iters)
- [ ] Dataset batch sizes match PRD (128/64/32)

---

## Document Status

**Configuration Status**: COMPLETE  
**Subtasks Used**: 8/8  
**Format**: Python dataclass (single format)  
**Ready for Phase 4**: YES  
**Next Step**: Phase 4 Logic Agent (algorithm design)

---

## Output Files

**Configuration Document**: `/workspace/TEST_bi_align/docs/youra_research/h-e1/03_config.md`
