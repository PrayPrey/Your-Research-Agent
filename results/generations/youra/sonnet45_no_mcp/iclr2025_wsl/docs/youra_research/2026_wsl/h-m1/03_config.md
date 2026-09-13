# Configuration Design: H-M1 Gradient Flow Feature Validation

**Hypothesis:** H-M1  
**Type:** Mechanism  
**Date:** 2026-04-21  
**Author:** Configuration Agent (Phase 3)

---

## 1. Overview

This document specifies configuration schemas, hyperparameters, and settings for H-M1 gradient flow feature validation experiment. As a MECHANISM-tier hypothesis with FULL infrastructure level, we use hardcoded configuration with optional YAML override (lightweight approach).

---

## 2. Configuration Architecture

### 2.1 Configuration Hierarchy

```
main.py (hardcoded defaults)
    ↓
[Optional] config.yaml override
    ↓
Command-line arguments (--random-seed, --run-random-test)
```

**Rationale:** 
- FULL tier supports YAML config, but H-M1 is simple enough for hardcoded defaults
- YAML override allows easy experimentation without code changes
- Command-line args for quick toggles (random test, seed)

---

## 3. Configuration Schema

### 3.1 Main Configuration (Hardcoded in main.py)

```python
# main.py - Default configuration

CONFIG = {
    # Experiment metadata
    "hypothesis_id": "h-m1",
    "experiment_name": "Gradient Flow Feature Validation",
    "base_hypothesis": "h-e1",
    
    # Reproducibility
    "random_seed": 42,
    
    # Data split
    "train_test_split": 0.8,  # 80% train (16 models), 20% test (4 models)
    
    # Feature extraction
    "feature_extractor": {
        "type": "GradientFlowFeatureExtractor",
        "n_features": 6,
        "filter_params": {
            "requires_grad": True,
            "min_dims": 2  # Conv2d/Linear only
        }
    },
    
    # Classifier configuration (reuse H-E1 optimal hyperparameters)
    "classifier": {
        "type": "LogisticRegression",
        "C": 1.0,               # Regularization strength (H-E1 optimal)
        "solver": "lbfgs",      # Optimizer (H-E1 optimal)
        "max_iter": 1000,       # Max iterations (H-E1 optimal)
        "random_state": 42
    },
    
    # Feature scaling
    "feature_scaler": {
        "type": "StandardScaler",
        "with_mean": True,
        "with_std": True
    },
    
    # Validation
    "run_random_test": True,  # Enable random initialization test
    
    # Output paths
    "output_dir": "outputs",
    "figures_dir": "outputs/figures",
    "metrics_file": "outputs/metrics.json",
    
    # Logging
    "log_level": "INFO",
    "log_progress": True  # Print per-model progress
}
```

### 3.2 Optional YAML Configuration

**File:** `config.yaml` (optional override)

```yaml
# config.yaml - Optional configuration override

hypothesis_id: h-m1
experiment_name: "Gradient Flow Feature Validation"
base_hypothesis: h-e1

# Reproducibility
random_seed: 42

# Data split
train_test_split: 0.8

# Feature extraction
feature_extractor:
  type: GradientFlowFeatureExtractor
  n_features: 6
  filter_params:
    requires_grad: true
    min_dims: 2

# Classifier (H-E1 optimal hyperparameters)
classifier:
  type: LogisticRegression
  C: 1.0
  solver: lbfgs
  max_iter: 1000
  random_state: 42

# Feature scaling
feature_scaler:
  type: StandardScaler
  with_mean: true
  with_std: true

# Validation
run_random_test: true

# Output
output_dir: outputs
figures_dir: outputs/figures
metrics_file: outputs/metrics.json

# Logging
log_level: INFO
log_progress: true
```

### 3.3 Configuration Loading (Python)

```python
import yaml
from typing import Dict, Any

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration with priority: YAML > Hardcoded defaults
    
    Args:
        config_path: Path to optional config.yaml
    
    Returns:
        config: Merged configuration dictionary
    """
    # Start with hardcoded defaults
    config = CONFIG.copy()
    
    # Override with YAML if provided
    if config_path and os.path.exists(config_path):
        with open(config_path, 'r') as f:
            yaml_config = yaml.safe_load(f)
        config.update(yaml_config)
    
    return config
```

---

## 4. Hyperparameter Reference

### 4.1 Model Selection (Fixed - No Tuning)

**Dataset:** 20 PyTorch torchvision pretrained models

| Parameter | Value | Source |
|-----------|-------|--------|
| Shallow models | 10 (resnet18, resnet34, ...) | H-E1 |
| Deep models | 10 (resnet50, resnet101, ...) | H-E1 |
| Pretrained weights | ImageNet | torchvision |
| Model selection | Fixed (same as H-E1) | Controlled experiment |

**Rationale:** Use identical models as H-E1 for controlled comparison.

### 4.2 Feature Extraction (No Tuning)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Number of features | 6 | Gradient-flow specific (designed) |
| Layer filter | `requires_grad=True, dims>=2` | Conv2d/Linear only (H-E1 pattern) |
| Norm type | Frobenius | Standard choice (H-E1) |
| Position normalization | [0, 1] | Comparable across architectures |

**Feature List:**
1. Norm progression slope
2. Norm variance
3. Input-layer norm
4. Output-layer norm
5. Depth-weighted norm
6. Layer count

**Rationale:** Features designed to capture gradient accumulation patterns (not tuned).

### 4.3 Classifier Hyperparameters (Reuse H-E1)

| Hyperparameter | Value | Source | Tuning |
|----------------|-------|--------|--------|
| `C` (regularization) | 1.0 | H-E1 optimal | ❌ No tuning |
| `solver` | lbfgs | H-E1 optimal | ❌ No tuning |
| `max_iter` | 1000 | H-E1 optimal | ❌ No tuning |
| `penalty` | l2 (default) | sklearn default | ❌ No tuning |

**Rationale:** H-E1 found optimal hyperparameters (100% accuracy). Reuse for controlled experiment.

### 4.4 Feature Scaling (Reuse H-E1)

| Parameter | Value | Source |
|-----------|-------|--------|
| Scaler type | StandardScaler | H-E1 |
| `with_mean` | True | Center to zero |
| `with_std` | True | Scale to unit variance |

**Rationale:** Gradient-flow features have different scales (norms vs counts) → normalization required.

### 4.5 Data Split (Reuse H-E1)

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Train size | 0.8 (16 models) | H-E1 optimal split |
| Test size | 0.2 (4 models) | H-E1 optimal split |
| Stratification | Yes (preserve class balance) | Required for small dataset |
| Random seed | 42 | Reproducibility (H-E1) |

---

## 5. Experimental Settings

### 5.1 Random Initialization Test

```python
# Random test configuration
RANDOM_TEST_CONFIG = {
    "enabled": True,  # Toggle random test
    "use_same_split": True,  # Same train-test split as pretrained
    "random_seed": 42,  # Same seed for reproducibility
    "expected_accuracy_max": 0.55  # Threshold for "fail to classify"
}
```

**Rationale:** 
- Verify training-induced patterns (random models should fail to classify)
- Use same seed for comparable splits
- Expected: <55% accuracy (close to random 50%)

### 5.2 Visualization Settings

```python
# Visualization configuration
VIZ_CONFIG = {
    "mandatory_plots": [
        "accuracy_comparison"  # H-E1 vs H-M1 vs Random
    ],
    "optional_plots": [
        "feature_importance",
        "confusion_matrix",
        "layer_progression",
        "feature_distributions"
    ],
    "figure_format": "png",
    "dpi": 150,
    "figsize": (8, 6),
    "color_scheme": {
        "h_e1": "green",
        "h_m1": "blue",
        "random": "gray"
    }
}
```

### 5.3 Output Settings

```python
# Output configuration
OUTPUT_CONFIG = {
    "save_metrics": True,
    "metrics_format": "json",
    "metrics_fields": [
        "test_accuracy",
        "train_accuracy",
        "confusion_matrix",
        "feature_importance",
        "random_test_accuracy"
    ],
    "save_figures": True,
    "figures_format": "png",
    "log_to_console": True
}
```

---

## 6. Inherited Configuration (from H-E1)

### 6.1 H-E1 Configuration Review

**H-E1 Config File:** `h-e1/code/config.py` (if exists) or hardcoded in `h-e1/code/main.py`

**Verified Settings from H-E1:**
- Random seed: 42 ✓
- Train-test split: 0.8/0.2 ✓
- Classifier: LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000) ✓
- Scaler: StandardScaler() ✓
- Stratified split: Yes ✓

**H-M1 Inheritance:**
- ✅ Reuse all H-E1 hyperparameters (proven optimal)
- ✅ Same random seed (reproducibility)
- ✅ Same train-test split (controlled comparison)
- ❌ Replace feature extractor (4 global stats → 6 gradient-flow features)

### 6.2 Configuration Comparison

| Setting | H-E1 | H-M1 | Change |
|---------|------|------|--------|
| Random seed | 42 | 42 | ✅ Same |
| Train-test split | 0.8/0.2 | 0.8/0.2 | ✅ Same |
| Classifier C | 1.0 | 1.0 | ✅ Same |
| Solver | lbfgs | lbfgs | ✅ Same |
| Max iterations | 1000 | 1000 | ✅ Same |
| Feature scaler | StandardScaler | StandardScaler | ✅ Same |
| Feature count | 4 | 6 | ❌ Changed (mechanism test) |
| Random test | No | Yes | ❌ Added (validation) |

---

## 7. Configuration Dataclass (Python 3.9+)

```python
from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class FeatureExtractorConfig:
    """Feature extraction configuration"""
    type: str = "GradientFlowFeatureExtractor"
    n_features: int = 6
    requires_grad: bool = True
    min_dims: int = 2

@dataclass
class ClassifierConfig:
    """Classifier hyperparameters"""
    type: str = "LogisticRegression"
    C: float = 1.0
    solver: str = "lbfgs"
    max_iter: int = 1000
    random_state: int = 42

@dataclass
class FeatureScalerConfig:
    """Feature scaling configuration"""
    type: str = "StandardScaler"
    with_mean: bool = True
    with_std: bool = True

@dataclass
class ExperimentConfig:
    """Main experiment configuration"""
    hypothesis_id: str = "h-m1"
    experiment_name: str = "Gradient Flow Feature Validation"
    base_hypothesis: str = "h-e1"
    
    # Reproducibility
    random_seed: int = 42
    
    # Data
    train_test_split: float = 0.8
    
    # Components
    feature_extractor: FeatureExtractorConfig = field(default_factory=FeatureExtractorConfig)
    classifier: ClassifierConfig = field(default_factory=ClassifierConfig)
    feature_scaler: FeatureScalerConfig = field(default_factory=FeatureScalerConfig)
    
    # Validation
    run_random_test: bool = True
    
    # Output
    output_dir: str = "outputs"
    figures_dir: str = "outputs/figures"
    metrics_file: str = "outputs/metrics.json"
    
    # Logging
    log_level: str = "INFO"
    log_progress: bool = True
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> "ExperimentConfig":
        """Load configuration from YAML file"""
        with open(yaml_path, 'r') as f:
            config_dict = yaml.safe_load(f)
        return cls(**config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "hypothesis_id": self.hypothesis_id,
            "experiment_name": self.experiment_name,
            "base_hypothesis": self.base_hypothesis,
            "random_seed": self.random_seed,
            "train_test_split": self.train_test_split,
            "classifier": {
                "C": self.classifier.C,
                "solver": self.classifier.solver,
                "max_iter": self.classifier.max_iter
            },
            "feature_extractor": {
                "type": self.feature_extractor.type,
                "n_features": self.feature_extractor.n_features
            }
        }
```

**Usage:**
```python
# Option 1: Use defaults
config = ExperimentConfig()

# Option 2: Load from YAML
config = ExperimentConfig.from_yaml("config.yaml")

# Option 3: Override specific fields
config = ExperimentConfig(
    random_seed=123,
    run_random_test=False
)

# Access nested config
classifier_params = {
    "C": config.classifier.C,
    "solver": config.classifier.solver,
    "max_iter": config.classifier.max_iter,
    "random_state": config.classifier.random_state
}
```

---

## 8. Command-Line Interface

### 8.1 Argument Parser

```python
import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="H-M1: Gradient Flow Feature Validation"
    )
    
    # Configuration file
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to YAML configuration file (optional)"
    )
    
    # Override common settings
    parser.add_argument(
        "--random-seed",
        type=int,
        default=42,
        help="Random seed for reproducibility (default: 42)"
    )
    
    parser.add_argument(
        "--run-random-test",
        action="store_true",
        default=True,
        help="Run random initialization test (default: True)"
    )
    
    parser.add_argument(
        "--no-random-test",
        action="store_false",
        dest="run_random_test",
        help="Skip random initialization test"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs",
        help="Output directory for results (default: outputs)"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    return parser.parse_args()
```

**Usage Examples:**
```bash
# Use all defaults
python main.py

# Custom random seed
python main.py --random-seed 123

# Skip random test
python main.py --no-random-test

# Load custom config
python main.py --config custom_config.yaml

# Override config with CLI args
python main.py --config config.yaml --random-seed 999

# Verbose logging
python main.py --log-level DEBUG
```

---

## 9. Environment Variables

```bash
# Optional environment variables

# PyTorch settings
export TORCH_HOME=/path/to/torch/models  # Model cache directory
export OMP_NUM_THREADS=4                 # CPU threads

# CUDA (not needed - CPU-only experiment)
# export CUDA_VISIBLE_DEVICES=-1         # Force CPU

# Logging
export H_M1_LOG_LEVEL=INFO               # Default log level
export H_M1_OUTPUT_DIR=./outputs         # Output directory
```

---

## 10. Configuration Validation

```python
def validate_config(config: ExperimentConfig) -> None:
    """
    Validate configuration before experiment execution.
    
    Args:
        config: Experiment configuration
    
    Raises:
        ValueError: If configuration is invalid
    """
    # Validate random seed
    if config.random_seed < 0:
        raise ValueError(f"random_seed must be non-negative, got {config.random_seed}")
    
    # Validate train-test split
    if not 0.0 < config.train_test_split < 1.0:
        raise ValueError(f"train_test_split must be in (0, 1), got {config.train_test_split}")
    
    # Validate classifier hyperparameters
    if config.classifier.C <= 0:
        raise ValueError(f"classifier.C must be positive, got {config.classifier.C}")
    
    if config.classifier.max_iter <= 0:
        raise ValueError(f"classifier.max_iter must be positive, got {config.classifier.max_iter}")
    
    # Validate output directory
    if not config.output_dir:
        raise ValueError("output_dir cannot be empty")
    
    print("✓ Configuration validation passed")
```

---

## 11. Applied Patterns (Archon KB)

**Applied:** Configuration management best practices
- **Pattern 1:** Hierarchical configuration (defaults → YAML → CLI args)
- **Pattern 2:** Dataclass-based config (type safety, IDE support)
- **Pattern 3:** Inherited hyperparameters from base hypothesis (H-E1)
- **Pattern 4:** Validation before execution (fail fast)
- **Pattern 5:** YAML + dataclass for FULL tier (flexibility + type safety)

**Source:** Archon Knowledge Base - ML Experiment Configuration Patterns

---

## 12. Configuration Checklist

**Before Phase 4 Implementation:**
- ✅ Hardcoded defaults match H-E1 optimal hyperparameters
- ✅ Random seed fixed (42) for reproducibility
- ✅ Train-test split identical to H-E1 (0.8/0.2)
- ✅ Classifier configuration verified from H-E1 (C=1.0, solver='lbfgs')
- ✅ Feature scaler matches H-E1 (StandardScaler)
- ✅ Random initialization test enabled (validation)
- ✅ Output paths configured (outputs/, outputs/figures/)
- ✅ YAML override available (optional flexibility)
- ✅ Command-line interface designed
- ✅ Configuration validation implemented

---

*Configuration Document v1.0 | Generated by Phase 3 Configuration Agent | Hypothesis: H-M1*
