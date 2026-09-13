# Configuration Specification: h-e1 Weight-Based Depth Classification

**Hypothesis:** h-e1 (EXISTENCE)  
**Date:** 2026-04-21  
**Author:** configuration-agent  
**Type:** PoC Validation  

**Applied:** Minimal PoC config pattern (hardcoded dict), sklearn LogisticRegression defaults

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: Foundation hypothesis - new config design from scratch  
**Config Files Found**: None - new config  
**Pattern Used**: Hardcoded dict (preferred for EXISTENCE PoC)

---

## System Overview

**Mission**: Provide minimal configuration for testing weight-based depth classification PoC.

**Configuration Strategy**: Single fixed configuration with standard defaults. No hyperparameter variations, no subtask decomposition - this is EXISTENCE validation only.

**Key Constraint**: MUST_WORK gate requires test accuracy ≥70%. Configuration uses proven defaults from sklearn documentation to maximize chance of success.

---

## Global Configuration

### Fixed Experiment Configuration (`config.py`)

```python
# h-e1/config.py - Single fixed configuration for EXISTENCE PoC

CONFIG = {
    # Dataset: 20 pretrained ImageNet CNNs
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
    "test_size": 0.2,  # 80/20 split: 16 train, 4 test
    "stratify": True,  # Maintain class balance
    "random_state": 42,  # Reproducibility
    
    # Feature normalization
    "scaler": {
        "with_mean": True,  # Center to mean=0
        "with_std": True,   # Scale to std=1
    },
    
    # Binary classifier (sklearn defaults)
    "classifier": {
        "C": 1.0,  # sklearn default regularization
        "solver": "lbfgs",  # sklearn default solver
        "max_iter": 1000,  # Sufficient for n=16 samples
        "random_state": 42,
    },
    
    # Gate evaluation
    "gate_threshold": 0.70,  # MUST_WORK threshold
    "baseline_accuracy": 0.50,  # Random guessing baseline
    
    # Output paths
    "output_dir": "h-e1",
    "results_dir": "h-e1/results",
    "figures_dir": "h-e1/figures",
    "figure_dpi": 300,  # Publication quality
}
```

**Rationale for Non-Standard Values:**
- `max_iter=1000`: sklearn default is 100, increased to avoid convergence warnings on small dataset
- `gate_threshold=0.70`: From hypothesis specification (70% accuracy target)
- `figure_dpi=300`: Publication quality requirement

---

## Module-Specific Configurations

### E1: Setup & Data Loading (Complexity: 8)

**Configuration:**

```python
# ModelLoader configuration (embedded in CONFIG)
MODEL_CONFIG = {
    "shallow_models": CONFIG["shallow_models"],  # 10 models ≤34 layers
    "deep_models": CONFIG["deep_models"],  # 10 models ≥50 layers
    "pretrained": True,  # Always use ImageNet pretrained weights
    "cache_dir": None,  # Use default ~/.cache/torch/hub/
}
```

**No subtasks needed** - Single module implementation (8 complexity < 10 threshold).

---

### E2: Feature Extraction (Complexity: 10)

**Configuration:**

```python
# FeatureExtractor configuration
FEATURE_CONFIG = {
    "norm_type": "fro",  # Frobenius norm
    "filter_params": {
        "trainable_only": True,  # requires_grad == True
        "weight_only": True,  # 'weight' in parameter name
    },
    "statistics": ["mean", "std", "min", "max"],  # 4 features per model
    "output_shape": (4,),  # Expected feature vector shape
}
```

**No subtasks needed** - Single module implementation (10 complexity ≤ 10 threshold).

---

### E3: Classification Pipeline (Complexity: 12)

**Configuration:**

```python
# Data splitting configuration
SPLIT_CONFIG = {
    "test_size": CONFIG["test_size"],  # 0.2
    "stratify": True,  # Maintain 50/50 class balance
    "random_state": CONFIG["random_state"],  # 42
    "shuffle": True,  # sklearn default
}

# Feature normalization configuration
SCALER_CONFIG = {
    "with_mean": CONFIG["scaler"]["with_mean"],  # True
    "with_std": CONFIG["scaler"]["with_std"],  # True
}

# Classifier configuration
CLASSIFIER_CONFIG = CONFIG["classifier"]  # LogisticRegression defaults
```

**Subtasks (3/12 budget used):**

| ID | Subtask | Description | Complexity |
|----|---------|-------------|------------|
| E3-1 | Data splitting | Stratified train-test split (16/4) | 3 |
| E3-2 | Feature normalization | StandardScaler fit and transform | 3 |
| E3-3 | Binary classifier | LogisticRegression training | 6 |

**Rationale:** E3 requires sequential pipeline: split → normalize → classify. Each step has clear boundaries for implementation.

---

### E4: Evaluation & Visualization (Complexity: 11)

**Configuration:**

```python
# Evaluation configuration
EVAL_CONFIG = {
    "primary_metric": "accuracy",  # Test accuracy for gate
    "gate_threshold": CONFIG["gate_threshold"],  # 0.70
    "baseline": CONFIG["baseline_accuracy"],  # 0.50
    "target": CONFIG["gate_threshold"],  # 0.70
    "secondary_metrics": [
        "confusion_matrix",
        "classification_report",
        "train_accuracy",  # Overfitting check
    ],
}

# Visualization configuration
VIS_CONFIG = {
    "output_dir": CONFIG["figures_dir"],  # h-e1/figures/
    "dpi": CONFIG["figure_dpi"],  # 300
    "figures": {
        "gate_metrics": {
            "required": True,  # Mandatory
            "filename": "gate_metrics.png",
            "colors": {
                "pass": "green",
                "fail": "red",
            },
        },
        "confusion_matrix": {
            "filename": "confusion_matrix.png",
            "cmap": "Blues",
        },
        "feature_distributions": {
            "filename": "feature_distributions.png",
            "kind": "box",
        },
        "feature_importance": {
            "filename": "feature_importance.png",
            "orientation": "horizontal",
        },
        "train_test_comparison": {
            "filename": "train_test_comparison.png",
            "colors": ["steelblue", "coral"],
        },
    },
}
```

**Subtasks (3/11 budget used):**

| ID | Subtask | Description | Complexity |
|----|---------|-------------|------------|
| E4-1 | Metrics computation | Accuracy, confusion matrix, classification report | 3 |
| E4-2 | Gate verification | Check test_accuracy ≥ 0.70, mechanism indicators | 3 |
| E4-3 | Figure generation | Create 5 analysis figures (gate metrics mandatory) | 5 |

**Rationale:** E4 has two distinct outputs: metrics computation (E4-1, E4-2) and visualization (E4-3). Gate metrics figure is critical path.

---

## Mechanism Verification Configuration

```python
# Verification indicators
VERIFICATION_CONFIG = {
    "indicators": {
        "features_extracted": {
            "check": "num_models == 20 and feature_shape == (4,)",
            "expected": True,
        },
        "layer_norms_valid": {
            "check": "min_layer_count > 0 and max_layer_count > 0",
            "expected": True,
        },
        "classifier_trained": {
            "check": "train_accuracy > 0.0",
            "expected": True,
        },
        "effect_detected": {
            "check": "test_accuracy > 0.50",
            "expected": True,
        },
    },
    "success_criteria": {
        "mechanism_works": "all_indicators_true and test_accuracy > 0.50",
        "hypothesis_supported": "test_accuracy >= 0.70",
    },
}
```

---

## Control Experiments Configuration (P2/P3 Priority)

```python
# Control experiments (optional for EXISTENCE PoC)
CONTROL_CONFIG = {
    # P2: Within-family accuracy
    "within_family": {
        "enabled": False,  # Optional for EXISTENCE
        "families": ["resnet", "vgg", "densenet"],
        "target_accuracy": 0.65,
    },
    
    # P3: Random labels sanity check
    "random_labels": {
        "enabled": False,  # Optional for EXISTENCE
        "n_trials": 5,
        "expected_accuracy": 0.55,  # Near random baseline
    },
}
```

**Note:** Control experiments marked as P2/P3 priority in PRD. For EXISTENCE PoC, can be deferred to future hypotheses.

---

## Output Specifications

### File Outputs

```python
OUTPUT_FILES = {
    "features": "h-e1/results/features.npy",  # (20, 4) feature array
    "labels": "h-e1/results/labels.npy",  # (20,) binary labels
    "metrics": "h-e1/results/metrics.json",  # Evaluation metrics dict
    "scaler": "h-e1/results/scaler.pkl",  # Fitted StandardScaler (optional)
    "classifier": "h-e1/results/classifier.pkl",  # Trained model (optional)
}
```

### Required Figures

```python
REQUIRED_FIGURES = [
    "h-e1/figures/gate_metrics.png",  # MANDATORY - gate status visualization
    "h-e1/figures/confusion_matrix.png",
    "h-e1/figures/feature_distributions.png",
    "h-e1/figures/feature_importance.png",
    "h-e1/figures/train_test_comparison.png",
]
```

---

## Environment Configuration

```python
# System requirements
ENV_CONFIG = {
    "python_version": ">=3.8",
    "dependencies": {
        "torch": ">=1.10",
        "torchvision": ">=0.11",
        "scikit-learn": ">=0.24",
        "numpy": ">=1.20",
        "matplotlib": ">=3.3",
        "seaborn": ">=0.11",
    },
    "resources": {
        "disk_space_gb": 5,  # Model cache
        "ram_gb": 8,  # Minimum
        "gpu": False,  # CPU sufficient for this PoC
    },
}
```

---

## Usage Example

```python
# main.py - Minimal PoC experiment

from config import CONFIG
from src.experiment import WeightDepthExperiment

def main():
    # Initialize experiment with fixed config
    experiment = WeightDepthExperiment(
        output_dir=CONFIG["output_dir"],
        random_state=CONFIG["random_state"]
    )
    
    # Run full pipeline
    results = experiment.run()
    
    # Check gate condition
    gate_passed = results["test_accuracy"] >= CONFIG["gate_threshold"]
    
    print(f"\n{'='*60}")
    print(f"h-e1 Weight-Based Depth Classification - EXISTENCE PoC")
    print(f"{'='*60}")
    print(f"Test Accuracy: {results['test_accuracy']:.1%}")
    print(f"Gate Threshold: {CONFIG['gate_threshold']:.1%}")
    print(f"Gate Status: {'PASS ✓' if gate_passed else 'FAIL ✗'}")
    print(f"{'='*60}\n")
    
    return results

if __name__ == "__main__":
    main()
```

---

## Validation Checklist

### Configuration Completeness
- [x] Single fixed config (no variations)
- [x] Hardcoded dict format (copy-paste ready)
- [x] All hyperparameters with defaults
- [x] Subtasks only for E3 (12 complexity) and E4 (11 complexity)
- [x] Total subtasks: 6 (within budget for EXISTENCE)

### EXISTENCE PoC Rules
- [x] No hyperparameter grid
- [x] No multiple config options
- [x] Single seed (42)
- [x] Minimal epochs: N/A (no neural network training)
- [x] Default values from sklearn documentation

### Documentation Standards
- [x] No ASCII diagrams
- [x] One-line Archon KB note
- [x] Codebase Analysis section included
- [x] Rationale only for non-standard values
- [x] Total length < 400 lines

---

## Summary

**Total Tasks with Subtasks:** 2/4 epics decomposed (E3, E4)  
**Total Subtasks:** 6 (3 for E3, 3 for E4)  
**Configuration Format:** Hardcoded dict (copy-paste ready for Phase 4)  
**Config Complexity:** Minimal (EXISTENCE PoC tier)  

**Critical Success Factors:**
1. StandardScaler normalization MUST be applied (weight magnitudes vary 10³-10⁴)
2. Stratified split MUST maintain class balance (8/8 train, 2/2 test)
3. Gate metrics figure MUST be generated (mandatory deliverable)
4. Random seed MUST be 42 throughout (reproducibility)

**Next Phase:** Phase 4 Implementation - Copy configurations directly into code modules.

---

**Document Version:** 1.0  
**Configuration Pattern:** Minimal PoC (sklearn defaults)  
**Total Lines:** ~340
