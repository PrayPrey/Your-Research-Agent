# Configuration Design: H-M2 Architectural Constraints Mechanism Validation

**Hypothesis:** H-M2  
**Type:** Mechanism  
**Date:** 2026-04-21  
**Author:** Configuration Agent (Phase 3)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Config classes verified from H-M1 code  
**Config Files Found**: `/home/anonymous/.../h-m1/code/config.py`  
**Pattern Used**: Hardcoded dict (H-M1 pattern)

---

## Applied Patterns

**Applied**: DL experiment configuration pattern (Archon KB)

---

## Configuration Format

**Format**: Hardcoded dict (consistent with H-M1)

**Rationale**: EXISTENCE hypothesis (PoC) - single fixed config sufficient. Matches H-M1 proven pattern.

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From H-M1 Actual Code)

The following configuration is inherited from H-M1:

```python
# From: h-m1/code/config.py (ACTUAL CODE - verified)
CONFIG = {
    # Experiment metadata
    "hypothesis_id": "h-m1",
    "experiment_name": "Gradient Flow Feature Validation",
    "base_hypothesis": "h-e1",
    
    # Dataset: Same 20 pretrained ImageNet CNNs
    "shallow_models": [
        "resnet18", "resnet34", "vgg11", "vgg13", "vgg16", "vgg19",
        "alexnet", "squeezenet1_0", "mobilenet_v2", "densenet121"
    ],
    "deep_models": [
        "resnet50", "resnet101", "resnet152", "densenet161", "densenet169",
        "densenet201", "wide_resnet50_2", "wide_resnet101_2",
        "resnext50_32x4d", "resnext101_32x8d"
    ],
    
    # Data splitting
    "test_size": 0.2,
    "stratify": True,
    "random_state": 42,
    
    # Feature normalization
    "scaler": {
        "with_mean": True,
        "with_std": True,
    },
    
    # Binary classifier (H-E1 optimal hyperparameters)
    "classifier": {
        "C": 1.0,
        "solver": "lbfgs",
        "max_iter": 1000,
        "random_state": 42,
    },
    
    # Validation
    "run_random_test": True,
    
    # Gate evaluation
    "gate_threshold": 0.50,
    "baseline_accuracy": 0.50,
    "h_e1_accuracy": 1.0,
    
    # Output paths
    "output_dir": ".",
    "results_dir": "./outputs",
    "figures_dir": "./outputs/figures",
    "figure_dpi": 150,
}
```

**Verified from**: `h-m1/code/config.py` lines 5-63

---

## H-M2 Configuration (Extended)

### Full Configuration

```python
# config.py - H-M2 Architectural Constraints Validation

CONFIG = {
    # Experiment metadata
    "hypothesis_id": "h-m2",
    "experiment_name": "Architectural Constraints Mechanism Validation",
    "base_hypothesis": "h-m1",
    
    # Dataset: Same 20 pretrained ImageNet CNNs as H-M1
    "shallow_models": [
        "resnet18", "resnet34", "vgg11", "vgg13", "vgg16", "vgg19",
        "alexnet", "squeezenet1_0", "mobilenet_v2", "densenet121"
    ],
    "deep_models": [
        "resnet50", "resnet101", "resnet152", "densenet161", "densenet169",
        "densenet201", "wide_resnet50_2", "wide_resnet101_2",
        "resnext50_32x4d", "resnext101_32x8d"
    ],
    
    # Data splitting (identical to H-M1)
    "test_size": 0.2,
    "stratify": True,
    "random_state": 42,
    
    # Feature extraction (NEW for H-M2)
    "feature_extractor": {
        "type": "ArchitecturalFeatureExtractor",
        "n_features": 8,
    },
    
    # Feature normalization (identical to H-M1)
    "scaler": {
        "with_mean": True,
        "with_std": True,
    },
    
    # Binary classifier (H-M1 optimal hyperparameters)
    "classifier": {
        "C": 1.0,
        "solver": "lbfgs",
        "max_iter": 1000,
        "random_state": 42,
    },
    
    # Within-family validation (NEW for H-M2)
    "within_family_threshold": 0.65,
    "architecture_families": {
        "resnet": ["resnet18", "resnet34", "resnet50", "resnet101", "resnet152",
                   "wide_resnet50_2", "wide_resnet101_2", "resnext50_32x4d", "resnext101_32x8d"],
        "vgg": ["vgg11", "vgg13", "vgg16", "vgg19"],
        "densenet": ["densenet121", "densenet161", "densenet169", "densenet201"],
    },
    
    # Validation
    "run_random_test": True,
    
    # Gate evaluation
    "gate_threshold": 0.50,
    "baseline_accuracy": 0.50,
    "h_e1_accuracy": 1.0,
    "h_m1_accuracy": 1.0,
    
    # Output paths
    "output_dir": ".",
    "results_dir": "./outputs",
    "figures_dir": "./outputs/figures",
    "figure_dpi": 150,
}
```

---

## Configuration Changes from H-M1

| Setting | H-M1 | H-M2 | Change Reason |
|---------|------|------|---------------|
| `hypothesis_id` | "h-m1" | "h-m2" | New hypothesis |
| `experiment_name` | "Gradient Flow..." | "Architectural Constraints..." | New mechanism |
| `base_hypothesis` | "h-e1" | "h-m1" | H-M2 extends H-M1 |
| `feature_extractor.type` | "GradientFlowFeatureExtractor" | "ArchitecturalFeatureExtractor" | New features |
| `feature_extractor.n_features` | 6 | 8 | Architectural features |
| `within_family_threshold` | N/A | 0.65 | NEW: Mechanism validation |
| `architecture_families` | N/A | {...} | NEW: Family grouping |
| `h_m1_accuracy` | N/A | 1.0 | NEW: Baseline comparison |

**All other settings**: Inherited unchanged from H-M1 (proven optimal)

---

## Feature Extraction Configuration

### Architectural Features (8 features)

```python
# Feature names and extraction logic
FEATURE_NAMES = [
    "residual_block_count",        # ResNet downsample modules
    "dense_connection_count",      # DenseNet denselayer count
    "bottleneck_ratio",            # 1x1 conv / total conv
    "layer_count",                 # Total Conv2d layers
    "skip_connection_present",     # Binary: 1 if residual/dense exists
    "residual_path_norm",          # Mean Frobenius norm of downsample weights
    "transition_layer_count",      # DenseNet transition layers
    "architecture_family",         # Binary: 1 if ResNet/DenseNet, 0 if VGG
]
```

**Extraction Parameters** (no tuning - detection-based):
- Residual detection: `hasattr(module, 'downsample')`
- Dense detection: `'denselayer' in name.lower()`
- Bottleneck detection: `kernel_size == (1, 1)`
- Transition detection: `'transition' in name.lower()`

---

## Within-Family Validation Configuration

### Family Grouping

```python
# Minimum models per family for valid split
MIN_FAMILY_SIZE = 4

# Family classifications (from CONFIG)
FAMILIES = {
    "resnet": 9 models,    # Sufficient for train-test split
    "vgg": 4 models,       # Minimal but sufficient
    "densenet": 4 models,  # Minimal but sufficient
}

# Within-family split (same seed as main experiment)
WITHIN_FAMILY_CONFIG = {
    "test_size": 0.2,
    "random_state": 42,
    "stratify": True,
    "min_train_samples": 3,  # Require at least 3 training samples
}
```

**Validation Logic**:
- Train separate classifier per family
- Use same hyperparameters as main classifier
- Report accuracy only if family has ≥4 models

---

## Random Initialization Test Configuration

```python
# Random test settings (inherited from H-M1)
RANDOM_TEST_CONFIG = {
    "enabled": True,
    "use_same_split": True,
    "random_state": 42,
}
```

**Expected Outcome**: Random accuracy ≈ Pretrained accuracy (features are architectural, like H-M1)

---

## Visualization Configuration

```python
# Figure generation settings
VISUALIZATION_CONFIG = {
    "mandatory_figures": [
        "accuracy_comparison",          # H-E1 vs H-M1 vs H-M2 vs Random
        "gate_metrics",                 # Test accuracy vs threshold
    ],
    "optional_figures": [
        "confusion_matrix",
        "feature_distributions",
        "feature_importance",
        "within_family_comparison",     # NEW: Per-family accuracy
        "train_test_comparison",
    ],
    "figure_format": "png",
    "dpi": 150,
    "figsize": (8, 6),
}
```

---

## Hyperparameter Reference

### Classifier (Inherited from H-M1, no tuning)

| Parameter | Value | Source |
|-----------|-------|--------|
| `C` | 1.0 | H-M1/H-E1 optimal |
| `solver` | "lbfgs" | H-M1/H-E1 optimal |
| `max_iter` | 1000 | H-M1/H-E1 optimal |
| `random_state` | 42 | Reproducibility |

### Data Split (Inherited from H-M1, no tuning)

| Parameter | Value | Source |
|-----------|-------|--------|
| `test_size` | 0.2 | H-M1/H-E1 optimal |
| `stratify` | True | Required for small dataset |
| `random_state` | 42 | Reproducibility |

### Feature Scaling (Inherited from H-M1)

| Parameter | Value | Source |
|-----------|-------|--------|
| `with_mean` | True | StandardScaler default |
| `with_std` | True | StandardScaler default |

---

## Configuration Validation

```python
def validate_config(config: dict) -> None:
    """Validate H-M2 configuration before execution."""
    # Check required fields
    assert config["hypothesis_id"] == "h-m2"
    assert config["feature_extractor"]["n_features"] == 8
    assert config["within_family_threshold"] == 0.65
    
    # Check family definitions
    assert len(config["architecture_families"]["resnet"]) >= 4
    assert len(config["architecture_families"]["vgg"]) >= 4
    assert len(config["architecture_families"]["densenet"]) >= 4
    
    # Check inherited settings
    assert config["random_state"] == 42
    assert config["test_size"] == 0.2
    assert config["classifier"]["C"] == 1.0
    
    print("✓ Configuration validation passed")
```

---

## Usage Example

```python
# main.py - Load and use configuration

from config import CONFIG

def main():
    # Access configuration
    model_loader = ModelLoader(
        shallow_names=CONFIG["shallow_models"],
        deep_names=CONFIG["deep_models"]
    )
    
    feature_extractor = ArchitecturalFeatureExtractor()
    
    classifier = DepthClassifier(
        random_state=CONFIG["classifier"]["random_state"]
    )
    
    # Within-family validation
    for family_name, model_list in CONFIG["architecture_families"].items():
        if len(model_list) >= 4:
            validate_within_family(family_name, model_list)
    
    # Gate check
    if test_accuracy > CONFIG["gate_threshold"]:
        print("✓ SHOULD_WORK gate PASSED")
    
    return 0

if __name__ == "__main__":
    exit(main())
```

---

## Configuration Summary

**Format**: Hardcoded dict (H-M1 pattern)  
**Inheritance**: 90% from H-M1 (models, classifier, split, scaler)  
**New Elements**: 8 architectural features, within-family validation, architecture family grouping  
**Hyperparameters**: No tuning (EXISTENCE PoC with proven H-M1 defaults)  
**Subtasks**: 0/2 used (single fixed config, no decomposition)

---

*Configuration Document v1.0 | Generated by Phase 3 Configuration Agent | Hypothesis: H-M2*
