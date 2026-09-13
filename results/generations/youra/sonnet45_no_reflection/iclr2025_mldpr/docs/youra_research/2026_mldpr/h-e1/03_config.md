# Configuration Design: h-e1

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-05-12  
**Budget:** 4 subtasks allocated

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** Green-field project - designing new config schema  
**Config Files Found:** None - new config  
**Pattern Used:** dataclass

---

## Knowledge Base Patterns

**Applied:** Python dataclass config pattern (PyTorch standard)

---

## Configuration Schema

### ExperimentConfig (config.py)

```python
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class ExperimentConfig:
    # Data settings
    data_root: str = "./data"
    output_dir: str = "./output"
    
    # Device settings
    device: str = "cuda"
    batch_size: int = 256
    
    # Drift detection settings
    n_pca_components: int = 2
    mmd_permutations: int = 1000
    
    # Cold-start thresholds (from hypothesis)
    thresholds: Dict[str, float] = field(default_factory=lambda: {
        'MAJOR': 0.07,
        'MINOR': 0.02,
        'PATCH': 0.005
    })
    
    # Reproducibility
    seed: int = 42
    
    # Feature extraction
    vision_model: str = "resnet50"
    nlp_model: str = "bert-base-uncased"
    max_seq_length: int = 512
    
    # Visualization
    figures_dir: str = "./figures"
    dpi: int = 300

def get_default_config() -> ExperimentConfig:
    return ExperimentConfig()
```

---

## Task Configurations

### A-1: Setup [Complexity: 6, Budget: 1/4]

**Config Type:** Project structure initialization

```python
# Directory structure config
PROJECT_STRUCTURE = {
    "code": ["src", "config.py", "run_experiment.py"],
    "data": ["ground_truth_labels.json", "datasets"],
    "figures": [],
    "output": []
}

# Requirements config
DEPENDENCIES = [
    "torch>=2.0.0",
    "torchvision>=0.15.0",
    "transformers>=4.30.0",
    "datasets>=2.12.0",
    "torchdrift>=0.3.0",
    "scikit-learn>=1.2.0",
    "scipy>=1.10.0",
    "numpy>=1.24.0",
    "pandas>=2.0.0",
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0",
    "pyyaml>=6.0",
    "tqdm>=4.65.0"
]

# Ground truth labels (from literature)
GROUND_TRUTH_LABELS = {
    "ImageNet_to_ImageNetV2": "MAJOR",
    "CIFAR10_to_CIFAR10.1": "MAJOR",
    "MNIST_v1_to_v2": "PATCH",
    "FashionMNIST_v1_to_v2": "PATCH",
    "GLUE_MRPC_v1_to_v2": "MINOR",
    "GLUE_RTE_v1_to_v2": "MINOR",
    "SQuAD_v1_to_v2": "MAJOR",
    "MSMARCO_v1_to_v2": "MINOR"
}
```

**Subtask:** C-1-1 (Directory + requirements + ground truth)

---

### A-2: Data Loading [Complexity: 11, Budget: 1/4]

**Config Type:** Dataset loading parameters

```python
@dataclass
class DataLoaderConfig:
    # Dataset paths
    torchvision_root: str = "./data/torchvision"
    huggingface_cache: str = "./data/hf_cache"
    cifar10_1_path: str = "./data/CIFAR-10.1"
    imagenet_path: str = "./data/imagenet"
    
    # Vision preprocessing
    image_size: int = 224
    imagenet_mean: tuple = (0.485, 0.456, 0.406)
    imagenet_std: tuple = (0.229, 0.224, 0.225)
    
    # NLP preprocessing
    max_length: int = 512
    tokenizer_name: str = "bert-base-uncased"
    
    # Dataset list
    vision_datasets: list = field(default_factory=lambda: [
        "CIFAR10", "MNIST", "FashionMNIST", "ImageNet"
    ])
    nlp_datasets: list = field(default_factory=lambda: [
        "glue/mrpc", "glue/rte", "squad", "ms_marco"
    ])
    
    # Error handling
    max_download_retries: int = 3
    skip_missing: bool = True
```

**Subtask:** C-2-1 (DataLoader class implementation)

---

### A-3: Feature Extraction [Complexity: 10, Budget: 1/4]

**Config Type:** Model and feature extraction settings

```python
@dataclass
class FeatureExtractorConfig:
    # Vision models
    vision_model_name: str = "resnet50"
    vision_weights: str = "IMAGENET1K_V2"
    vision_feature_dim: int = 2048
    
    # NLP models
    nlp_model_name: str = "bert-base-uncased"
    nlp_feature_dim: int = 768
    use_cls_token: bool = True
    
    # Batch processing
    batch_size: int = 256
    num_workers: int = 4
    
    # Memory management
    enable_grad: bool = False
    use_amp: bool = False
```

**Subtask:** C-3-1 (FeatureExtractor class)

---

### A-4: SVAD Classifier [Complexity: 14, Budget: 1/4]

**Config Type:** Drift detection algorithm parameters

```python
@dataclass
class SVADClassifierConfig:
    # PCA reduction
    n_pca_components: int = 2
    pca_whiten: bool = False
    
    # KS test settings
    ks_bonferroni_correction: bool = True
    ks_alpha: float = 0.05
    
    # MMD settings
    mmd_kernel: str = "gaussian_rbf"
    mmd_bandwidth: str = "median_heuristic"
    mmd_permutations: int = 1000
    mmd_alpha: float = 0.05
    
    # Classification thresholds (cold-start, from hypothesis)
    threshold_major: float = 0.07
    threshold_minor: float = 0.02
    threshold_patch: float = 0.005
    
    # Reproducibility
    random_state: int = 42
```

**Subtask:** C-4-1 (SVADDriftClassifier implementation)

---

## Subtask Allocation

| Task ID | Subtask ID | Description | Config Included |
|---------|------------|-------------|-----------------|
| A-1 | C-1-1 | Project setup + requirements + ground truth | ✓ |
| A-2 | C-2-1 | DataLoader implementation | ✓ |
| A-3 | C-3-1 | FeatureExtractor implementation | ✓ |
| A-4 | C-4-1 | SVAD classifier implementation | ✓ |

**Total Subtasks Used:** 4/4

---

## Integration Configuration

### Main Experiment Runner (run_experiment.py)

```python
@dataclass
class ExperimentRunnerConfig:
    # Experiment metadata
    hypothesis_id: str = "h-e1"
    experiment_name: str = "svad_drift_classification"
    
    # Input/output
    config_path: str = "./config.py"
    results_path: str = "./04_results.json"
    log_path: str = "./experiment.log"
    
    # Execution
    verbose: bool = True
    save_features: bool = False
    
    # Evaluation
    target_precision: float = 0.70
    target_recall: float = 0.85
    target_accuracy: float = 0.85
    
    # Visualization
    generate_figures: bool = True
    figure_format: str = "png"
    figure_dpi: int = 300
```

---

## Environment Configuration

### GPU Settings

```python
# Set before running experiment
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Single GPU

# PyTorch settings
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = False
```

### Logging Configuration

```python
import logging

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'filename': 'experiment.log',
            'mode': 'w'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
}
```

---

## Validation Checks

- [x] Single config format (dataclass only)
- [x] All configs use defaults from research (TorchDrift, hypothesis specs)
- [x] Subtask count within budget (4/4 used)
- [x] No hyperparameter grid (EXISTENCE PoC - single fixed config)
- [x] Seed fixed for reproducibility
- [x] Threshold values from hypothesis specification
- [x] No ASCII diagrams
- [x] Total length < 400 lines

---

## Configuration Usage

### Loading Configuration

```python
from config import ExperimentConfig, get_default_config

# Use default config
config = get_default_config()

# Or customize
config = ExperimentConfig(
    data_root="/custom/path",
    device="cuda:1",
    seed=123
)
```

### Passing to Modules

```python
# Initialize modules with config
data_loader = DatasetPairLoader(config.data_root)
feature_extractor = FeatureExtractor(config.vision_model, config.device)
svad_classifier = SVADDriftClassifier(
    n_pca_components=config.n_pca_components,
    thresholds=config.thresholds
)
```

---

**Document Status:** READY FOR PHASE 4 IMPLEMENTATION  
**Config Pattern:** Python dataclass (PyTorch standard)  
**Total Subtasks:** 4/4 allocated  
**Next Phase:** Phase 4 - Task-Driven Implementation
