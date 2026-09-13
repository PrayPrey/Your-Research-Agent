# Configuration Schema: H-E2 SAT Profiler

**Hypothesis ID:** H-E2  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-07-10  
**Author:** Configuration Agent  
**Version:** 1.0  

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch  
**Config Files Found**: None - new config design based on H-M1 pattern  
**Pattern Used**: Dataclass (following established project pattern)

---

## Knowledge Base Application

Applied: PyTorch dataclass config pattern (type-safe, modular config with validation)

---

## Configuration Design

### CNNConfig

```python
@dataclass
class CNNConfig:
    """Configuration for CNN profiling experiments."""
    
    # Model specification
    model_name: str
    dataset: str
    optimizer: str
    
    # Training hyperparameters
    batch_size: int
    lr: float
    momentum: float = 0.9
    weight_decay: float = 0.0001
    
    # Profiling settings
    num_profiling_batches: int = 50
    device: str = "cuda"
```

### TransformerConfig

```python
@dataclass
class TransformerConfig:
    """Configuration for Transformer profiling experiments."""
    
    # Model specification
    model_name: str
    dataset: str
    optimizer: str
    
    # Training hyperparameters
    batch_size: int
    seq_length: int
    lr: float
    weight_decay: float = 0.01
    
    # Profiling settings
    num_profiling_batches: int = 50
    device: str = "cuda"
```

### ProfilingConfig

```python
@dataclass
class ProfilingConfig:
    """SAT profiling protocol configuration."""
    
    # Batch-level profiling
    num_batches: int = 50
    warmup_batches: int = 5
    
    # GPU monitoring
    gpu_util_sampling_interval: float = 0.1  # seconds
    use_torch_cuda_utilization: bool = True
    
    # Epoch timing validation
    measure_full_epoch: bool = True
    
    # Synchronization
    cuda_synchronize: bool = True
```

### JitterConfig

```python
@dataclass
class JitterConfig:
    """Synthetic jitter experiment configuration."""
    
    # Delay injection (milliseconds)
    delay_levels: List[int] = field(default_factory=lambda: [0, 50, 100, 200])
    
    # Causality validation
    num_batches_per_delay: int = 50
    warmup_batches: int = 5
    
    # Reference config for jitter experiments
    base_config_type: Literal["cnn", "transformer"] = "cnn"
```

### AnalysisConfig

```python
@dataclass
class AnalysisConfig:
    """Metrics and evaluation configuration."""
    
    # SAT threshold for degradation prediction
    sat_threshold: float = 1.5
    degradation_threshold: float = 0.15  # 15%
    
    # Metrics targets
    precision_target: float = 0.80
    recall_target: float = 0.70
    f1_target: float = 0.75
    
    # Causality validation
    gpu_util_low_threshold: float = 0.90  # Below 90% = data loading bottleneck
```

### OutputConfig

```python
@dataclass
class OutputConfig:
    """Output and logging configuration."""
    
    # Results directory
    hypothesis_folder: Path = Path("docs/youra_research/h-e2")
    
    # Output files
    profiling_results: str = "profiling_results.json"
    metrics_summary: str = "metrics_summary.json"
    
    # Figures
    figure_format: str = "png"
    dpi: int = 300
    figures_subdir: str = "figures"
    
    # Logging
    log_level: str = "INFO"
```

### ReproducibilityConfig

```python
@dataclass
class ReproducibilityConfig:
    """Reproducibility settings for profiling experiments."""
    
    random_seed: int = 42
    deterministic_cuda: bool = False  # Profiling experiments - prioritize realism over determinism
    
    # Environment
    cuda_visible_devices: str = "0"
    
    # Logging
    log_pytorch_version: bool = True
    log_cuda_version: bool = True
    log_gpu_model: bool = True
```

### ExperimentConfig

```python
@dataclass
class ExperimentConfig:
    """Master configuration for H-E2 SAT profiling experiment."""
    
    profiling: ProfilingConfig = field(default_factory=ProfilingConfig)
    jitter: JitterConfig = field(default_factory=JitterConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    reproducibility: ReproducibilityConfig = field(default_factory=ReproducibilityConfig)
    
    def __post_init__(self):
        """Validate configuration and create directories."""
        # Validate SAT threshold
        assert self.analysis.sat_threshold > 1.0, \
            "SAT threshold must be > 1.0 (ratio of P95/Median)"
        
        # Validate degradation threshold
        assert 0.0 < self.analysis.degradation_threshold < 1.0, \
            "Degradation threshold must be between 0 and 1"
        
        # Validate profiling batches
        assert self.profiling.num_batches >= 50, \
            "Minimum 50 batches required for reliable P95 estimation"
        
        # Create output directories
        self.output.hypothesis_folder.mkdir(parents=True, exist_ok=True)
        (self.output.hypothesis_folder / "results").mkdir(parents=True, exist_ok=True)
        (self.output.hypothesis_folder / self.output.figures_subdir).mkdir(
            parents=True, exist_ok=True
        )
```

---

## Natural Workload Configurations

### CNN Configurations (24 total)

```python
def get_cnn_configs() -> List[CNNConfig]:
    """Generate 24 CNN profiling configurations."""
    
    configs = []
    
    # Models (8): ResNet-18, ResNet-50, VGG-16, EfficientNet-B0, 
    #             DenseNet-121, MobileNetV2, ShuffleNetV2, SqueezeNet
    cnn_models = [
        "resnet18", "resnet50", "vgg16", "efficientnet_b0",
        "densenet121", "mobilenet_v2", "shufflenet_v2_x1_0", "squeezenet1_0"
    ]
    
    # Datasets (2): CIFAR-10, ImageNet
    datasets = ["cifar10", "imagenet"]
    
    # Optimizers (3): SGD, Adam, AdamW
    optimizers = ["sgd", "adam", "adamw"]
    
    # Standard batch sizes per model type
    batch_sizes = {
        "resnet18": 128, "resnet50": 64, "vgg16": 64, "efficientnet_b0": 64,
        "densenet121": 64, "mobilenet_v2": 128, "shufflenet_v2_x1_0": 128, "squeezenet1_0": 128
    }
    
    # Learning rates per optimizer
    lrs = {"sgd": 0.01, "adam": 0.001, "adamw": 0.001}
    
    # Sample selection (24 from 48 possible combinations)
    for model in cnn_models:
        # Each model gets 3 configs (vary optimizer/dataset)
        configs.append(CNNConfig(
            model_name=model,
            dataset="cifar10",
            optimizer="sgd",
            batch_size=batch_sizes[model],
            lr=lrs["sgd"]
        ))
        
        configs.append(CNNConfig(
            model_name=model,
            dataset="imagenet" if model in ["resnet50", "vgg16", "densenet121", "efficientnet_b0"] else "cifar10",
            optimizer="adam",
            batch_size=batch_sizes[model] // 2 if model in ["resnet50", "vgg16"] else batch_sizes[model],
            lr=lrs["adam"]
        ))
        
        configs.append(CNNConfig(
            model_name=model,
            dataset="cifar10",
            optimizer="adamw",
            batch_size=batch_sizes[model],
            lr=lrs["adamw"]
        ))
    
    return configs[:24]  # Ensure exactly 24 configs
```

### Transformer Configurations (24 total)

```python
def get_transformer_configs() -> List[TransformerConfig]:
    """Generate 24 Transformer profiling configurations."""
    
    configs = []
    
    # Models (8): GPT-2-small, BERT-base, T5-small, DistilBERT,
    #             RoBERTa-base, ALBERT-base, ELECTRA-small, DeBERTa-base
    transformer_models = [
        "gpt2", "bert-base-uncased", "t5-small", "distilbert-base-uncased",
        "roberta-base", "albert-base-v2", "google/electra-small-discriminator", "microsoft/deberta-base"
    ]
    
    # Datasets (2): WildChat, PersonaChat
    datasets = ["wildchat", "personachat"]
    
    # Optimizers (3): Adam, AdamW, Adafactor
    optimizers = ["adam", "adamw", "adafactor"]
    
    # Sequence lengths and batch sizes (vary by model size)
    model_configs = {
        "gpt2": {"seq_length": 512, "batch_size": 16},
        "bert-base-uncased": {"seq_length": 512, "batch_size": 16},
        "t5-small": {"seq_length": 256, "batch_size": 32},
        "distilbert-base-uncased": {"seq_length": 512, "batch_size": 32},
        "roberta-base": {"seq_length": 512, "batch_size": 16},
        "albert-base-v2": {"seq_length": 512, "batch_size": 32},
        "google/electra-small-discriminator": {"seq_length": 512, "batch_size": 32},
        "microsoft/deberta-base": {"seq_length": 512, "batch_size": 16}
    }
    
    # Learning rate
    lr = 2e-5
    
    # Sample selection (24 from 48 possible combinations)
    for model in transformer_models:
        # Each model gets 3 configs (vary optimizer/dataset)
        configs.append(TransformerConfig(
            model_name=model,
            dataset="wildchat",
            optimizer="adam",
            batch_size=model_configs[model]["batch_size"],
            seq_length=model_configs[model]["seq_length"],
            lr=lr
        ))
        
        configs.append(TransformerConfig(
            model_name=model,
            dataset="personachat",
            optimizer="adamw",
            batch_size=model_configs[model]["batch_size"],
            seq_length=model_configs[model]["seq_length"],
            lr=lr
        ))
        
        configs.append(TransformerConfig(
            model_name=model,
            dataset="wildchat",
            optimizer="adafactor",
            batch_size=model_configs[model]["batch_size"] // 2,  # Smaller batch for diversity
            seq_length=model_configs[model]["seq_length"],
            lr=lr
        ))
    
    return configs[:24]  # Ensure exactly 24 configs
```

---

## Helper Functions

### Reproducibility Setup

```python
def set_reproducibility(config: ReproducibilityConfig):
    """Configure environment for reproducible profiling."""
    import os
    import random
    import numpy as np
    import torch
    
    # Set seeds
    random.seed(config.random_seed)
    np.random.seed(config.random_seed)
    torch.manual_seed(config.random_seed)
    
    if torch.cuda.is_available():
        torch.cuda.manual_seed(config.random_seed)
        torch.cuda.manual_seed_all(config.random_seed)
        
        if config.deterministic_cuda:
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    
    # Set environment variables
    os.environ["CUDA_VISIBLE_DEVICES"] = config.cuda_visible_devices
```

### Environment Logging

```python
def log_environment(config: ReproducibilityConfig):
    """Log environment information for reproducibility."""
    import torch
    import logging
    
    logger = logging.getLogger(__name__)
    
    if config.log_pytorch_version:
        logger.info(f"PyTorch version: {torch.__version__}")
    
    if config.log_cuda_version and torch.cuda.is_available():
        logger.info(f"CUDA version: {torch.version.cuda}")
    
    if config.log_gpu_model and torch.cuda.is_available():
        logger.info(f"GPU model: {torch.cuda.get_device_name(0)}")
        logger.info(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
```

---

## Configuration Notes

### EXISTENCE (PoC) Constraints

This is a validation experiment, not production deployment:

1. **Fixed Values**: No hyperparameter search - using standard research defaults
2. **Single Seed**: 42 (sufficient for profiling validation)
3. **Minimal Epochs**: 50 batches for SAT + 1 full epoch for validation
4. **No Tuning**: Batch sizes and learning rates based on model capacity, not optimized

### Non-Standard Choices

1. **deterministic_cuda=False**: Profiling experiments prioritize realistic system behavior over exact reproducibility
2. **num_batches=50**: Minimum required for reliable P95 estimation (literature recommends 50+)
3. **gpu_util_sampling_interval=0.1s**: Balance between measurement overhead and temporal resolution

### Configuration Validation

Built-in validation in `__post_init__`:
- SAT threshold > 1.0 (P95 must exceed median)
- Degradation threshold in (0, 1)
- Minimum 50 profiling batches
- Directory creation

---

## Usage Example

```python
from config import ExperimentConfig, get_cnn_configs, get_transformer_configs, set_reproducibility

# Initialize experiment
config = ExperimentConfig()

# Setup reproducibility
set_reproducibility(config.reproducibility)

# Get configurations
cnn_configs = get_cnn_configs()
transformer_configs = get_transformer_configs()

# Total: 48 configs (24 CNN + 24 Transformer)
print(f"Total configs: {len(cnn_configs) + len(transformer_configs)}")
```

---

**Document Status**: Complete  
**Next Phase**: Task Allocation (03_tasks.yaml)
