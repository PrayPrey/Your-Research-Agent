# Configuration Design: H-M1 Structural Contract Validation

**Hypothesis ID:** h-m1  
**Document Type:** Configuration Specification  
**Phase:** 3 - Implementation Planning  
**Status:** DRAFT  
**Generated:** 2026-07-11

---

## Codebase Analysis (Serena)

**Project Type**: Green-field  
**Status**: Green-field - designing new config schema  
**Config Files Found**: None - new contract validation system  
**Pattern Used**: Dataclass (following established project patterns from archived hypotheses)

**Note**: Applied patterns from PyTorch config.py and project convention of nested dataclass configurations.

---

## 1. Configuration Overview

**Applied**: PyTorch config.py pattern (nested dataclasses with validation methods)

This configuration system manages all parameters for the structural contract validation experiment. The design follows a nested dataclass architecture for type safety and clear organization.

**Key Design Principles:**
1. Single source of truth via dataclass defaults
2. Reproducibility via fixed random seeds
3. Validation methods prevent invalid configurations
4. Path management for cross-platform compatibility

---

## 2. Configuration Schema

### 2.1 Contract Library Configuration

```python
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional
import torch


@dataclass
class ContractConfig:
    """Contract library behavior settings."""
    
    # Probe execution
    probe_batch_size: int = 1
    enable_shape_validation: bool = True
    enable_dtype_validation: bool = True
    enable_device_validation: bool = True
    enable_null_check: bool = True
    
    # Caching
    enable_probe_cache: bool = True
    cache_dir: Path = Path.home() / ".cache" / "structural_contracts" / "probes"
    cache_ttl_seconds: int = 86400  # 24 hours
    
    # Error reporting
    error_verbosity: str = "detailed"  # "minimal", "detailed", "debug"
    include_fix_suggestions: bool = True
    
    # Symbolic dimensions
    symbolic_batch_dim: bool = True
    batch_dim_name: str = "B"
```

### 2.2 Defect Injection Configuration

```python
@dataclass
class DefectInjectionConfig:
    """Defect corpus and injection settings."""
    
    # Corpus configuration
    source_corpus_path: Path = Path("./data/jiang_corpus.json")
    catalog_output_path: Path = Path("./defects/catalog.json")
    total_defects: int = 200
    
    # Category distribution
    defect_categories: Dict[str, int] = field(default_factory=lambda: {
        "shape_mismatch": 50,
        "device_mismatch": 50,
        "dtype_mismatch": 50,
        "null_output": 50
    })
    
    # Injection modes
    injection_mode: str = "monkey_patch"  # "monkey_patch" or "source_modification"
    preserve_original: bool = True
    validate_injection: bool = True
    
    # Sampling
    random_seed: int = 42
    stratified_sampling: bool = True
```

### 2.3 Baseline Experiment Configuration

```python
@dataclass
class BaselineConfig:
    """Baseline experiment parameters."""
    
    # Model configuration
    model_name: str = "resnet18"
    pretrained: bool = True
    num_classes: int = 10
    
    # Dataset configuration
    dataset_name: str = "CIFAR10"
    data_root: Path = Path.home() / ".cache" / "torch" / "datasets"
    batch_size: int = 32
    num_workers: int = 4
    
    # Training configuration (sanity check only)
    epochs: int = 1
    learning_rate: float = 0.001
    optimizer: str = "adam"
    weight_decay: float = 0.0001
    
    # Expected accuracy threshold
    min_accuracy: float = 0.70
    
    # Timing measurements
    measure_latency: bool = True
    num_defect_samples: int = 50
```

### 2.4 Validation Experiment Configuration

```python
@dataclass
class ValidationConfig:
    """Contract validation experiment settings."""
    
    # Detection measurement
    total_defect_runs: int = 200
    detection_stage_tracking: bool = True  # import, forward, training
    
    # Execution time measurement
    measure_overhead: bool = True
    overhead_threshold_seconds: float = 10.0
    breakdown_timing: bool = True  # import, probe, validation
    
    # False positive measurement
    num_valid_batches: int = 1000
    false_positive_threshold: float = 0.05
    include_imagenet_samples: bool = True
    imagenet_sample_count: int = 100
    
    # Statistical analysis
    confidence_level: float = 0.95
    statistical_power: float = 0.80
    detection_rate_target: float = 0.80
    detection_rate_minimum: float = 0.60
```

### 2.5 Analysis Configuration

```python
@dataclass
class AnalysisConfig:
    """Statistical analysis and reporting settings."""
    
    # Hypothesis testing
    null_hypothesis_threshold: float = 0.60
    alternative_hypothesis_threshold: float = 0.80
    alpha: float = 0.05
    two_tailed: bool = True
    
    # Error message quality (exploratory)
    error_message_sample_size: int = 20
    enable_quality_rating: bool = True
    calculate_jaccard_similarity: bool = True
    
    # Output paths
    results_dir: Path = Path("./results")
    detection_rates_csv: Path = Path("./results/detection_rates.csv")
    execution_times_csv: Path = Path("./results/execution_times.csv")
    false_positives_csv: Path = Path("./results/false_positives.csv")
    analysis_json: Path = Path("./results/analysis.json")
```

### 2.6 Environment Configuration

```python
@dataclass
class EnvironmentConfig:
    """Environment and reproducibility settings."""
    
    # Python environment
    python_version: str = "3.9"
    pytorch_version: str = "2.0"
    torchvision_version: str = "0.15"
    
    # Random seeds (following PyTorch reproducibility docs)
    random_seed: int = 42
    torch_seed: int = 42
    numpy_seed: int = 42
    cuda_deterministic: bool = True
    cuda_benchmark: bool = False
    
    # Device configuration
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    gpu_id: int = 0
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = Path("./logs/h-m1.log")
    enable_wandb: bool = False
```

### 2.7 Root Configuration

```python
@dataclass
class H_M1_Config:
    """Root configuration for H-M1 structural contract validation."""
    
    hypothesis_id: str = "h-m1"
    experiment_name: str = "structural_contract_validation"
    
    # Nested configurations
    contract: ContractConfig = field(default_factory=ContractConfig)
    defect_injection: DefectInjectionConfig = field(default_factory=DefectInjectionConfig)
    baseline: BaselineConfig = field(default_factory=BaselineConfig)
    validation: ValidationConfig = field(default_factory=ValidationConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    environment: EnvironmentConfig = field(default_factory=EnvironmentConfig)
    
    def validate(self) -> bool:
        """Validate configuration constraints."""
        # Total defects must match category distribution
        total_category_defects = sum(self.defect_injection.defect_categories.values())
        assert total_category_defects == self.defect_injection.total_defects, \
            f"Category sum ({total_category_defects}) != total_defects ({self.defect_injection.total_defects})"
        
        # Confidence level must be valid
        assert 0 < self.analysis.confidence_level < 1, \
            "Confidence level must be between 0 and 1"
        
        # Detection thresholds must be ordered
        assert self.validation.detection_rate_minimum < self.validation.detection_rate_target, \
            "Minimum detection rate must be less than target"
        
        # Batch size must be positive
        assert self.baseline.batch_size > 0, "Batch size must be positive"
        
        # Overhead threshold must be positive
        assert self.validation.overhead_threshold_seconds > 0, \
            "Overhead threshold must be positive"
        
        return True
    
    def setup_directories(self) -> None:
        """Create required directories."""
        self.contract.cache_dir.mkdir(parents=True, exist_ok=True)
        self.baseline.data_root.mkdir(parents=True, exist_ok=True)
        self.analysis.results_dir.mkdir(parents=True, exist_ok=True)
        if self.environment.log_file:
            self.environment.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def setup_reproducibility(self) -> None:
        """Configure reproducibility settings."""
        import random
        import numpy as np
        import torch
        
        # Set seeds
        random.seed(self.environment.random_seed)
        np.random.seed(self.environment.numpy_seed)
        torch.manual_seed(self.environment.torch_seed)
        
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(self.environment.torch_seed)
            torch.backends.cudnn.deterministic = self.environment.cuda_deterministic
            torch.backends.cudnn.benchmark = self.environment.cuda_benchmark


def get_config() -> H_M1_Config:
    """Factory function to create and validate configuration."""
    config = H_M1_Config()
    config.validate()
    config.setup_directories()
    config.setup_reproducibility()
    return config
```

---

## 3. Default Values Rationale

### 3.1 Contract Library Defaults

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `probe_batch_size` | 1 | Minimal overhead for shape validation |
| `cache_ttl_seconds` | 86400 | Balance freshness vs. performance |
| `error_verbosity` | "detailed" | Research context requires full diagnostics |
| `symbolic_batch_dim` | True | Supports variable batch sizes in PyTorch 2.x |

### 3.2 Defect Injection Defaults

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `total_defects` | 200 | Statistical power >0.8 for 80% detection rate |
| Category distribution | 50 each | Balanced representation of defect types |
| `injection_mode` | "monkey_patch" | Preserves original library code, safer than source modification |

### 3.3 Baseline Experiment Defaults

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `epochs` | 1 | Sanity check only, not full training |
| `learning_rate` | 0.001 | Adam optimizer default |
| `min_accuracy` | 0.70 | Pretrained ResNet-18 baseline on CIFAR-10 |

### 3.4 Validation Experiment Defaults

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `total_defect_runs` | 200 | Matches defect corpus size for complete coverage |
| `overhead_threshold_seconds` | 10.0 | Per PRD requirement NFR-1 |
| `num_valid_batches` | 1000 | Sufficient for <5% false positive measurement |
| `false_positive_threshold` | 0.05 | Per PRD requirement FR-15 |

### 3.5 Random Seed Management

**Strategy**: Fixed seeds for complete reproducibility (following PyTorch docs on reproducibility)

| Seed | Value | Scope |
|------|-------|-------|
| `random_seed` | 42 | Python stdlib random |
| `torch_seed` | 42 | PyTorch RNG |
| `numpy_seed` | 42 | NumPy RNG |

**Deterministic Settings**:
- `cuda_deterministic`: True (slower but reproducible)
- `cuda_benchmark`: False (disables cudnn auto-tuner for determinism)

---

## 4. Configuration Loading and Usage

### 4.1 Basic Usage

```python
from config import get_config

# Load and validate configuration
config = get_config()

# Access nested configurations
print(f"Detection target: {config.validation.detection_rate_target * 100}%")
print(f"Overhead threshold: {config.validation.overhead_threshold_seconds}s")
print(f"Random seed: {config.environment.random_seed}")
```

### 4.2 Overriding Defaults

```python
from config import H_M1_Config, ContractConfig

# Custom contract configuration
custom_contract = ContractConfig(
    probe_batch_size=4,
    error_verbosity="debug",
    enable_probe_cache=False
)

# Create config with override
config = H_M1_Config(contract=custom_contract)
config.validate()
config.setup_directories()
config.setup_reproducibility()
```

### 4.3 Configuration in Experiment Scripts

```python
# baselines/sanity_check.py
from config import get_config

def run_sanity_check():
    config = get_config()
    
    # Load model
    model = torchvision.models.resnet18(pretrained=config.baseline.pretrained)
    model.fc = torch.nn.Linear(model.fc.in_features, config.baseline.num_classes)
    
    # Load dataset
    dataset = torchvision.datasets.CIFAR10(
        root=str(config.baseline.data_root),
        train=False,
        download=True
    )
    
    # Train for validation
    train_model(
        model=model,
        dataset=dataset,
        epochs=config.baseline.epochs,
        lr=config.baseline.learning_rate,
        device=config.environment.device
    )
```

---

## 5. Environment Variables (Optional Overrides)

While dataclass defaults are primary, these environment variables allow CI/CD overrides:

```bash
# Override device configuration
export H_M1_DEVICE="cpu"
export H_M1_GPU_ID="1"

# Override random seed for ablation studies
export H_M1_RANDOM_SEED="123"

# Override paths for cluster environments
export H_M1_DATA_ROOT="/scratch/datasets"
export H_M1_CACHE_DIR="/scratch/cache"
export H_M1_RESULTS_DIR="/scratch/results"

# Override detection thresholds for sensitivity analysis
export H_M1_DETECTION_TARGET="0.85"
export H_M1_DETECTION_MINIMUM="0.65"
```

**Loading environment overrides**:

```python
import os
from config import get_config

config = get_config()

# Apply environment overrides if present
if "H_M1_DEVICE" in os.environ:
    config.environment.device = os.environ["H_M1_DEVICE"]

if "H_M1_RANDOM_SEED" in os.environ:
    seed = int(os.environ["H_M1_RANDOM_SEED"])
    config.environment.random_seed = seed
    config.environment.torch_seed = seed
    config.environment.numpy_seed = seed
    config.setup_reproducibility()
```

---

## 6. File Paths and Caching

### 6.1 Default Directory Structure

```
experiments/h-m1/
├── config.py                           # Configuration module
├── data/
│   ├── jiang_corpus.json              # Source defect corpus
│   └── cifar10/                       # CIFAR-10 dataset (auto-downloaded)
├── defects/
│   └── catalog.json                   # Generated defect catalog (200 defects)
├── results/
│   ├── detection_rates.csv
│   ├── execution_times.csv
│   ├── false_positives.csv
│   └── analysis.json
├── logs/
│   └── h-m1.log
└── .cache/
    └── structural_contracts/
        └── probes/                    # Probe result cache
```

### 6.2 Cache Management

**Contract Probe Cache**:
- **Location**: `~/.cache/structural_contracts/probes/`
- **Format**: Pickle files keyed by (function_signature, contract_spec) hash
- **TTL**: 24 hours (configurable via `cache_ttl_seconds`)
- **Invalidation**: Automatic on library version change (hash includes library version)

**PyTorch Model Cache**:
- **Location**: `~/.cache/torch/hub/checkpoints/`
- **Managed by**: `torchvision.models` (automatic download and caching)

**Dataset Cache**:
- **Location**: `~/.cache/torch/datasets/cifar-10-batches-py/`
- **Managed by**: `torchvision.datasets.CIFAR10` (automatic download)

---

## 7. Reproducibility Checklist

Configuration ensures reproducibility through:

- [x] **Fixed random seeds** (Python, NumPy, PyTorch)
- [x] **CUDA deterministic mode** (slower but reproducible)
- [x] **Pinned library versions** (PyTorch 2.0, torchvision 0.15)
- [x] **Documented default values** (all parameters with rationale)
- [x] **Validation methods** (prevent invalid configurations)
- [x] **Defect corpus versioning** (sourced from Jiang et al. corpus, no synthetic)
- [x] **Cache invalidation** (automatic on library version change)
- [x] **Path management** (cross-platform compatible via `pathlib.Path`)

---

## 8. Configuration Validation

The `validate()` method enforces critical constraints:

```python
def validate(self) -> bool:
    """Validate configuration constraints."""
    
    # Defect corpus integrity
    assert sum(self.defect_injection.defect_categories.values()) == \
           self.defect_injection.total_defects
    
    # Statistical parameters
    assert 0 < self.analysis.confidence_level < 1
    assert self.validation.detection_rate_minimum < \
           self.validation.detection_rate_target
    
    # Experiment parameters
    assert self.baseline.batch_size > 0
    assert self.validation.overhead_threshold_seconds > 0
    
    return True
```

**Validation is mandatory** - `get_config()` always calls `validate()` before returning.

---

## 9. Integration with PRD Requirements

| PRD Requirement | Configuration Parameter | Default Value |
|-----------------|-------------------------|---------------|
| FR-2: Shape validation with symbolic batch dim | `contract.symbolic_batch_dim` | True |
| FR-6: 200 structural defects (50 per category) | `defect_injection.total_defects` | 200 |
| FR-9: ResNet-18 on CIFAR-10, ≥70% accuracy | `baseline.min_accuracy` | 0.70 |
| FR-13: 95% confidence interval | `analysis.confidence_level` | 0.95 |
| FR-14: Execution time ≤10s | `validation.overhead_threshold_seconds` | 10.0 |
| FR-15: False positive rate <5% | `validation.false_positive_threshold` | 0.05 |
| NFR-3: Determinism (fixed random seed) | `environment.random_seed` | 42 |
| NFR-7: PyTorch version ≥2.0 | `environment.pytorch_version` | "2.0" |

---

## 10. Configuration Testing

**Unit tests for configuration validation**:

```python
# tests/test_config.py
import pytest
from config import H_M1_Config, DefectInjectionConfig

def test_config_validation():
    """Test configuration validation logic."""
    config = H_M1_Config()
    assert config.validate() is True

def test_invalid_defect_distribution():
    """Test that mismatched defect counts raise error."""
    invalid_defect = DefectInjectionConfig(
        total_defects=200,
        defect_categories={
            "shape_mismatch": 60,  # Total = 210, should fail
            "device_mismatch": 50,
            "dtype_mismatch": 50,
            "null_output": 50
        }
    )
    config = H_M1_Config(defect_injection=invalid_defect)
    with pytest.raises(AssertionError):
        config.validate()

def test_reproducibility_setup():
    """Test that reproducibility setup configures seeds correctly."""
    import torch
    config = H_M1_Config()
    config.setup_reproducibility()
    
    # Verify seeds are set
    assert torch.initial_seed() == config.environment.torch_seed
```

---

## 11. Summary

**Configuration Format**: Python dataclasses (nested structure)

**Key Features**:
1. Type-safe defaults for all experiment parameters
2. Validation methods prevent invalid configurations
3. Reproducibility via fixed seeds and deterministic settings
4. Path management for cross-platform compatibility
5. Environment variable overrides for CI/CD flexibility

**Total Parameters**: 60+ configuration options organized into 7 nested dataclasses

**Reproducibility Guarantee**: Fixed seeds + deterministic CUDA + pinned versions

**Next Steps**:
- Implement configuration in `experiments/h-m1/config.py`
- Write unit tests for validation logic
- Integrate with experiment scripts (baselines, validation, analysis)

---

**Document Status:** READY FOR IMPLEMENTATION  
**Next Phase:** Phase 4 - Code Implementation  
**Configuration File Location:** `experiments/h-m1/config.py`
