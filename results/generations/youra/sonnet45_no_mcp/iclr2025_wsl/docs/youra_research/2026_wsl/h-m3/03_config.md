# Configuration Design: H-M3 Batch Normalization Mechanism Validation

**Hypothesis:** H-M3  
**Type:** Mechanism  
**Date:** 2026-04-21  
**Author:** Configuration Agent (Phase 3)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Config classes verified from H-M2 code  
**Config Files Found**: `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_wsl_3/docs/youra_research/20260421_wsl/h-m2/code/config.py`  
**Pattern Used**: Hardcoded dict (H-M2 pattern)

---

## Applied Patterns

**Applied**: DL experiment configuration pattern (Archon KB)

---

## Configuration Format

**Format**: Hardcoded dict (consistent with H-M2)

**Rationale**: EXISTENCE hypothesis (PoC) - single fixed config sufficient. Matches H-M2 proven pattern.

---

## Inherited Configuration (Base Hypothesis)

### Config Classes (From H-M2 Actual Code)

The following configuration is inherited from H-M2:

```python
# From: h-m2/code/config.py (ACTUAL CODE - verified)
CONFIG = {
    # Experiment metadata
    "hypothesis_id": "h-m2",
    "experiment_name": "Architectural Constraints Mechanism Validation",
    "base_hypothesis": "h-m1",
    
    # Dataset: Same 20 pretrained ImageNet CNNs
    "shallow_models": [
        "resnet18", "resnet34",
        "vgg11", "vgg13", "vgg16", "vgg19",
        "alexnet", "squeezenet1_0",
        "mobilenet_v2", "densenet121"
    ],
    "deep_models": [
        "resnet50", "resnet101", "resnet152",
        "densenet161", "densenet169", "densenet201",
        "wide_resnet50_2", "wide_resnet101_2",
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
    
    # Binary classifier (H-M1 optimal hyperparameters)
    "classifier": {
        "C": 1.0,
        "solver": "lbfgs",
        "max_iter": 1000,
        "random_state": 42,
    },
    
    # Within-family validation
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

**Verified from**: `h-m2/code/config.py` lines 5-73

---

## H-M3 Configuration (Extended)

### Full Configuration

```python
# config.py - H-M3 Batch Normalization Mechanism Validation

CONFIG = {
    # Experiment metadata
    "hypothesis_id": "h-m3",
    "experiment_name": "Batch Normalization Mechanism Validation",
    "base_hypothesis": "h-m2",
    
    # Dataset: Same 20 pretrained ImageNet CNNs as H-M2
    "shallow_models": [
        "resnet18", "resnet34",
        "vgg11", "vgg13", "vgg16", "vgg19",
        "alexnet", "squeezenet1_0",
        "mobilenet_v2", "densenet121"
    ],
    "deep_models": [
        "resnet50", "resnet101", "resnet152",
        "densenet161", "densenet169", "densenet201",
        "wide_resnet50_2", "wide_resnet101_2",
        "resnext50_32x4d", "resnext101_32x8d"
    ],
    
    # Data splitting (identical to H-M2)
    "test_size": 0.2,
    "stratify": True,
    "random_state": 42,
    
    # Feature extraction (NEW for H-M3)
    "feature_extractor": {
        "type": "BatchNormFeatureExtractor",
        "n_features": 6,
    },
    
    # Feature normalization (identical to H-M2)
    "scaler": {
        "with_mean": True,
        "with_std": True,
    },
    
    # Binary classifier (H-M2 optimal hyperparameters)
    "classifier": {
        "C": 1.0,
        "solver": "lbfgs",
        "max_iter": 1000,
        "random_state": 42,
    },
    
    # Within-family validation (inherited from H-M2)
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
    "h_m2_accuracy": 1.0,
    
    # Output paths
    "output_dir": ".",
    "results_dir": "./outputs",
    "figures_dir": "./outputs/figures",
    "figure_dpi": 150,
}
```

---

## Configuration Changes from H-M2

| Setting | H-M2 | H-M3 | Change Reason |
|---------|------|------|---------------|
| `hypothesis_id` | "h-m2" | "h-m3" | New hypothesis |
| `experiment_name` | "Architectural Constraints..." | "Batch Normalization..." | New mechanism |
| `base_hypothesis` | "h-m1" | "h-m2" | H-M3 extends H-M2 |
| `feature_extractor.type` | "ArchitecturalFeatureExtractor" | "BatchNormFeatureExtractor" | New features |
| `feature_extractor.n_features` | 8 | 6 | Batch norm features |
| `h_m2_accuracy` | N/A | 1.0 | NEW: Baseline comparison |

**All other settings**: Inherited unchanged from H-M2 (proven optimal)

---

## Feature Extraction Configuration

### Batch Normalization Features (6 features)

```python
# Feature names and extraction logic
FEATURE_NAMES = [
    "bn_layer_count",           # Total BatchNorm2d layers
    "gamma_mean",               # Mean of BN weight params
    "gamma_std",                # Std of BN weight params
    "beta_mean",                # Mean of BN bias params
    "beta_std",                 # Std of BN bias params
    "depth_weighted_bn_norm",   # Weighted norm emphasizing later layers
]
```

**Extraction Parameters** (no tuning - detection-based):
- BN detection: `isinstance(module, nn.BatchNorm2d)`
- Parameter access: `bn.weight.data` (gamma), `bn.bias.data` (beta)
- Depth weighting: `sum((i+1) * bn.weight.abs().mean() for i, bn in enumerate(bn_layers))`
- Zero-BN handling: Models without BN → `np.zeros(6)`

---

## Within-Family Validation Configuration

### Family Grouping (Inherited from H-M2)

```python
# Minimum models per family for valid split
MIN_FAMILY_SIZE = 4

# Family classifications (from CONFIG)
FAMILIES = {
    "resnet": 9 models,    # All have BN
    "vgg": 4 models,       # No BN - control group
    "densenet": 4 models,  # All have BN
}

# Within-family split (same seed as main experiment)
WITHIN_FAMILY_CONFIG = {
    "test_size": 0.2,
    "random_state": 42,
    "stratify": True,
    "min_train_samples": 3,
}
```

**Validation Logic**:
- Train separate classifier per family
- VGG family expected to fail (no BN layers → zeros features)
- ResNet/DenseNet families expected to pass (BN layer count varies by depth)

---

## Random Initialization Test Configuration

```python
# Random test settings (inherited from H-M2)
RANDOM_TEST_CONFIG = {
    "enabled": True,
    "use_same_split": True,
    "random_state": 42,
}
```

**Expected Outcome**: Random accuracy ≈ Pretrained accuracy (BN layer count is architectural)

---

## Visualization Configuration

```python
# Figure generation settings
VISUALIZATION_CONFIG = {
    "mandatory_figures": [
        "accuracy_comparison",          # H-E1 vs H-M1 vs H-M2 vs H-M3 vs Random (5-way)
        "gate_metrics",                 # Test accuracy vs threshold
    ],
    "optional_figures": [
        "confusion_matrix",
        "feature_distributions",
        "feature_importance",
        "within_family_comparison",
        "train_test_comparison",
    ],
    "figure_format": "png",
    "dpi": 150,
    "figsize": (8, 6),
}
```

---

## Hyperparameter Reference

### Classifier (Inherited from H-M2, no tuning)

| Parameter | Value | Source |
|-----------|-------|--------|
| `C` | 1.0 | H-M2/H-M1/H-E1 optimal |
| `solver` | "lbfgs" | H-M2/H-M1/H-E1 optimal |
| `max_iter` | 1000 | H-M2/H-M1/H-E1 optimal |
| `random_state` | 42 | Reproducibility |

### Data Split (Inherited from H-M2, no tuning)

| Parameter | Value | Source |
|-----------|-------|--------|
| `test_size` | 0.2 | H-M2/H-M1/H-E1 optimal |
| `stratify` | True | Required for small dataset |
| `random_state` | 42 | Reproducibility |

### Feature Scaling (Inherited from H-M2)

| Parameter | Value | Source |
|-----------|-------|--------|
| `with_mean` | True | StandardScaler default |
| `with_std` | True | StandardScaler default |

---

## Configuration Validation

```python
def validate_config(config: dict) -> None:
    """Validate H-M3 configuration before execution."""
    # Check required fields
    assert config["hypothesis_id"] == "h-m3"
    assert config["feature_extractor"]["n_features"] == 6
    assert config["within_family_threshold"] == 0.65
    
    # Check family definitions
    assert len(config["architecture_families"]["resnet"]) >= 4
    assert len(config["architecture_families"]["vgg"]) >= 4
    assert len(config["architecture_families"]["densenet"]) >= 4
    
    # Check inherited settings
    assert config["random_state"] == 42
    assert config["test_size"] == 0.2
    assert config["classifier"]["C"] == 1.0
    
    # Check baseline accuracies
    assert config["h_m2_accuracy"] == 1.0
    
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
    
    feature_extractor = BatchNormFeatureExtractor()
    
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

**Format**: Hardcoded dict (H-M2 pattern)  
**Inheritance**: 95% from H-M2 (models, classifier, split, scaler, within-family config)  
**New Elements**: 6 batch norm features, H-M2 baseline accuracy  
**Hyperparameters**: No tuning (EXISTENCE PoC with proven H-M2 defaults)  
**Subtasks**: 0/2 used (single fixed config, no decomposition)

---

*Configuration Document v1.0 | Generated by Phase 3 Configuration Agent | Hypothesis: H-M3*
