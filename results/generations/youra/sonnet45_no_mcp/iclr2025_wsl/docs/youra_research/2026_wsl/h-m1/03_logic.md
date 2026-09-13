# Logic Design: H-M1 Gradient Flow Feature Validation

**Hypothesis:** H-M1  
**Type:** Mechanism  
**Date:** 2026-04-21  
**Author:** Logic Agent (Phase 3)

---

## 1. Overview

This document specifies API signatures, tensor shapes, and algorithmic pseudo-code for H-M1 gradient flow feature extraction. The core innovation is extracting layer-wise progression patterns that capture gradient accumulation effects during training.

---

## 2. Codebase Analysis (Serena)

**Base Hypothesis:** H-E1

### 2.1 H-E1 Feature Extractor (Reference)

**File:** `h-e1/code/feature_extractor.py`

**Actual Implementation (Verified):**
```python
class GlobalStatisticsExtractor:
    """Extract 4 global statistics from pretrained model weights"""
    
    def extract_features(self, model: torch.nn.Module) -> np.ndarray:
        """
        Args:
            model: PyTorch pretrained model
        Returns:
            features: (4,) array [mean_norm, std_norm, min_norm, max_norm]
        """
        layer_norms = []
        for param in model.parameters():
            if param.requires_grad and len(param.shape) >= 2:
                norm = torch.linalg.norm(param.data, ord='fro').item()
                layer_norms.append(norm)
        
        layer_norms = np.array(layer_norms)
        return np.array([
            np.mean(layer_norms),
            np.std(layer_norms),
            np.min(layer_norms),
            np.max(layer_norms)
        ])
```

**Key Findings:**
- Iterates `model.parameters()` (all trainable params)
- Filters: `param.requires_grad and len(param.shape) >= 2` (Conv/Linear only)
- Frobenius norm: `torch.linalg.norm(param.data, ord='fro')`
- Returns (4,) numpy array
- No position tracking (H-M1 addition)

**Applied:** Extend H-E1 pattern with layer position tracking for gradient-flow features

---

## 3. External Dependencies API (from H-E1)

### 3.1 Model Loading (H-E1 Reuse)

**File:** `h-e1/code/model_loader.py`

**Function Signature (Verified):**
```python
def load_pretrained_models() -> Dict[str, torch.nn.Module]:
    """
    Load all 20 pretrained models from torchvision.
    
    Returns:
        models: {"resnet18": model_obj, "resnet50": model_obj, ...}
    """
    pass
```

**Constants (Verified):**
```python
SHALLOW_MODELS = [
    "resnet18", "resnet34", "vgg11", "vgg13", "vgg16", 
    "vgg19", "alexnet", "squeezenet1_0", "mobilenet_v2", "densenet121"
]

DEEP_MODELS = [
    "resnet50", "resnet101", "resnet152", "densenet161", "densenet169",
    "densenet201", "wide_resnet50_2", "wide_resnet101_2", 
    "resnext50_32x4d", "resnext101_32x8d"
]
```

### 3.2 Classifier Training (H-E1 Reuse)

**File:** `h-e1/code/classifier.py`

**Function Signature (Verified):**
```python
def train_classifier(
    features: np.ndarray,  # Shape: (20, n_features)
    labels: np.ndarray,    # Shape: (20,) - 0=shallow, 1=deep
    config: dict
) -> Tuple[LogisticRegression, StandardScaler]:
    """
    Train LogisticRegression with StandardScaler normalization.
    
    Args:
        features: Feature matrix (n_samples, n_features)
        labels: Binary labels (0=shallow, 1=deep)
        config: {"C": 1.0, "solver": "lbfgs", "max_iter": 1000, "random_state": 42}
    
    Returns:
        classifier: Trained LogisticRegression
        scaler: Fitted StandardScaler
    """
    pass
```

**Applied:** Reuse H-E1 classifier with H-M1 gradient-flow features (6 features instead of 4)

---

## 4. Core Module: GradientFlowFeatureExtractor

### 4.1 Class Definition

```python
import torch
import numpy as np
from typing import Tuple

class GradientFlowFeatureExtractor:
    """
    Extract gradient-flow features from pretrained CNN weights.
    
    Captures layer-wise progression patterns that reflect gradient
    accumulation effects during training (shallow vs deep networks).
    """
    
    def __init__(self):
        """Initialize feature extractor (no state needed)"""
        pass
```

### 4.2 Main API: extract_features

**Signature:**
```python
def extract_features(self, model: torch.nn.Module) -> np.ndarray:
    """
    Extract 6 gradient-flow features from a pretrained model.
    
    Args:
        model: PyTorch pretrained model (e.g., resnet50, vgg16)
    
    Returns:
        features: (6,) numpy array with gradient-flow features:
            [0] norm_slope: Linear trend of norms across layers
            [1] norm_variance: Variance of layer norms (stability)
            [2] input_norm: First layer norm magnitude
            [3] output_norm: Last layer norm magnitude
            [4] depth_weighted_norm: Sum of (position × norm)
            [5] layer_count: Number of trainable layers
    
    Tensor Shapes:
        model.parameters(): Iterator[torch.Tensor] - variable shapes
        param.data: torch.Tensor - shape depends on layer type
            - Conv2d: (out_channels, in_channels, kH, kW)
            - Linear: (out_features, in_features)
        layer_norms: np.ndarray - shape (n_layers,)
        layer_positions: np.ndarray - shape (n_layers,)
        features: np.ndarray - shape (6,)
    
    Algorithm:
        1. Iterate through model.parameters()
        2. For each trainable 2D+ param (Conv/Linear):
            a. Compute Frobenius norm
            b. Track normalized position [0, 1]
        3. Compute 6 features from (norms, positions) arrays
    """
```

**Pseudo-code:**
```python
def extract_features(self, model):
    # Step 1: Initialize collectors
    layer_norms = []
    layer_positions = []
    
    # Step 2: Extract layer-wise norms with position tracking
    total_layers = sum(1 for p in model.parameters() if p.requires_grad and len(p.shape) >= 2)
    
    for idx, param in enumerate(model.parameters()):
        # Filter: Only trainable Conv2d/Linear layers
        if param.requires_grad and len(param.shape) >= 2:
            # Compute Frobenius norm
            norm = torch.linalg.norm(param.data, ord='fro').item()
            
            # Normalized position: 0.0 (input) to 1.0 (output)
            position = idx / total_layers if total_layers > 0 else 0.0
            
            layer_norms.append(norm)
            layer_positions.append(position)
    
    # Convert to numpy
    layer_norms = np.array(layer_norms)
    layer_positions = np.array(layer_positions)
    
    # Step 3: Compute gradient-flow features
    # Feature 1: Norm progression slope (captures gradient accumulation trend)
    # Uses linear regression: slope, intercept = polyfit(x, y, deg=1)
    if len(layer_norms) > 1:
        norm_slope = np.polyfit(layer_positions, layer_norms, deg=1)[0]
    else:
        norm_slope = 0.0
    
    # Feature 2: Norm variance (gradient stability across depth)
    norm_variance = np.var(layer_norms) if len(layer_norms) > 0 else 0.0
    
    # Feature 3: Input-layer norm (initial gradient magnitude)
    input_norm = layer_norms[0] if len(layer_norms) > 0 else 0.0
    
    # Feature 4: Output-layer norm (final gradient magnitude)
    output_norm = layer_norms[-1] if len(layer_norms) > 0 else 0.0
    
    # Feature 5: Gradient depth proxy (weighted by position)
    # Deep networks accumulate more gradient transformations → higher weighted sum
    depth_weighted_norm = np.sum(layer_norms * layer_positions) if len(layer_norms) > 0 else 0.0
    
    # Feature 6: Layer count (explicit depth signal)
    layer_count = len(layer_norms)
    
    # Return as (6,) array
    return np.array([
        norm_slope,
        norm_variance,
        input_norm,
        output_norm,
        depth_weighted_norm,
        layer_count
    ])
```

**Complexity:** O(L) where L = number of layers (typically 20-200)

---

## 5. Main Pipeline

### 5.1 Experiment Orchestration

**File:** `main.py`

**Function Signature:**
```python
def run_experiment(config: dict) -> dict:
    """
    Run full H-M1 experiment pipeline.
    
    Args:
        config: Experiment configuration
            {
                "random_seed": 42,
                "train_test_split": 0.8,
                "classifier": {"C": 1.0, "solver": "lbfgs", "max_iter": 1000},
                "run_random_test": True
            }
    
    Returns:
        results: Experiment results
            {
                "test_accuracy": float,
                "train_accuracy": float,
                "confusion_matrix": np.ndarray (2, 2),
                "feature_importance": np.ndarray (6,),
                "random_test_accuracy": float (if run_random_test=True),
                "comparison": {"h_e1": 1.0, "h_m1": float, "random": 0.5}
            }
    
    Tensor Shapes:
        features: (20, 6) - 20 models × 6 gradient-flow features
        labels: (20,) - binary labels (0=shallow, 1=deep)
        X_train: (16, 6), y_train: (16,)
        X_test: (4, 6), y_test: (4,)
    """
```

**Pseudo-code:**
```python
def run_experiment(config):
    # Step 1: Load pretrained models (H-E1 reuse)
    from h_e1.code.model_loader import load_pretrained_models, SHALLOW_MODELS, DEEP_MODELS
    models = load_pretrained_models()  # 20 models
    
    # Step 2: Extract gradient-flow features (H-M1 new)
    from feature_extractor import GradientFlowFeatureExtractor
    extractor = GradientFlowFeatureExtractor()
    
    features = []
    labels = []
    for name, model in models.items():
        feat = extractor.extract_features(model)  # (6,)
        features.append(feat)
        labels.append(0 if name in SHALLOW_MODELS else 1)
    
    features = np.array(features)  # (20, 6)
    labels = np.array(labels)      # (20,)
    
    # Step 3: Train-test split (H-E1 reuse)
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(
        features, labels,
        test_size=0.2,
        random_state=config["random_seed"],
        stratify=labels
    )
    
    # Step 4: Train classifier (H-E1 reuse)
    from h_e1.code.classifier import train_classifier
    classifier, scaler = train_classifier(X_train, y_train, config["classifier"])
    
    # Step 5: Evaluate (H-E1 reuse)
    from h_e1.code.evaluate import compute_metrics
    y_pred_train = classifier.predict(scaler.transform(X_train))
    y_pred_test = classifier.predict(scaler.transform(X_test))
    
    train_accuracy = accuracy_score(y_train, y_pred_train)
    test_accuracy = accuracy_score(y_test, y_pred_test)
    confusion = confusion_matrix(y_test, y_pred_test)
    feature_importance = classifier.coef_[0]  # (6,) - logistic regression coefficients
    
    # Step 6: Random initialization test (H-M1 new)
    random_accuracy = None
    if config.get("run_random_test", False):
        from random_init_test import test_random_models
        random_accuracy = test_random_models(extractor, config)
    
    # Step 7: Compile results
    return {
        "test_accuracy": test_accuracy,
        "train_accuracy": train_accuracy,
        "confusion_matrix": confusion,
        "feature_importance": feature_importance,
        "random_test_accuracy": random_accuracy,
        "comparison": {
            "h_e1": 1.0,  # From H-E1 validation report
            "h_m1": test_accuracy,
            "random": 0.5  # Theoretical random baseline
        }
    }
```

---

## 6. Random Initialization Test

### 6.1 Random Model Generator

**File:** `random_init_test.py`

**Function Signature:**
```python
def create_random_model(architecture_name: str) -> torch.nn.Module:
    """
    Create randomly initialized model with same architecture as pretrained.
    
    Args:
        architecture_name: Model name (e.g., "resnet50", "vgg16")
    
    Returns:
        model: Randomly initialized model (pretrained=False)
    
    Example:
        model = create_random_model("resnet50")
        # Same architecture as torchvision.models.resnet50(pretrained=True)
        # but with random weights (no training)
    """
```

**Pseudo-code:**
```python
def create_random_model(architecture_name):
    import torchvision.models as models
    
    # Get model class (e.g., models.resnet50)
    model_class = getattr(models, architecture_name)
    
    # Initialize with random weights (pretrained=False)
    model = model_class(pretrained=False)
    
    return model
```

### 6.2 Random Model Test

**Function Signature:**
```python
def test_random_models(
    extractor: GradientFlowFeatureExtractor,
    config: dict
) -> float:
    """
    Test gradient-flow features on randomly initialized models.
    
    Args:
        extractor: Feature extractor instance
        config: Experiment configuration
    
    Returns:
        random_test_accuracy: Test accuracy on random models
    
    Expected: <0.55 (fail to classify)
    Rationale: If random models classify well, features are architectural
               (not gradient-induced from training)
    """
```

**Pseudo-code:**
```python
def test_random_models(extractor, config):
    from h_e1.code.model_loader import SHALLOW_MODELS, DEEP_MODELS
    
    # Step 1: Create random models (same architectures, random weights)
    random_features = []
    random_labels = []
    
    for name in SHALLOW_MODELS:
        model = create_random_model(name)
        feat = extractor.extract_features(model)
        random_features.append(feat)
        random_labels.append(0)
    
    for name in DEEP_MODELS:
        model = create_random_model(name)
        feat = extractor.extract_features(model)
        random_features.append(feat)
        random_labels.append(1)
    
    random_features = np.array(random_features)  # (20, 6)
    random_labels = np.array(random_labels)      # (20,)
    
    # Step 2: Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        random_features, random_labels,
        test_size=0.2,
        random_state=config["random_seed"],
        stratify=random_labels
    )
    
    # Step 3: Train classifier on random models
    from h_e1.code.classifier import train_classifier
    classifier, scaler = train_classifier(X_train, y_train, config["classifier"])
    
    # Step 4: Evaluate
    y_pred = classifier.predict(scaler.transform(X_test))
    random_accuracy = accuracy_score(y_test, y_pred)
    
    return random_accuracy
```

---

## 7. Visualization Module

### 7.1 Comparison Bar Chart (Mandatory)

**File:** `visualize_comparison.py`

**Function Signature:**
```python
def plot_accuracy_comparison(
    h_e1_accuracy: float,
    h_m1_accuracy: float,
    random_baseline: float,
    output_path: str
) -> None:
    """
    Generate bar chart comparing H-E1 vs H-M1 vs Random baseline.
    
    Args:
        h_e1_accuracy: H-E1 test accuracy (1.0)
        h_m1_accuracy: H-M1 test accuracy (computed)
        random_baseline: Random guess (0.5)
        output_path: Save path (e.g., "outputs/figures/accuracy_comparison.png")
    
    Saves:
        PNG figure with 3 bars (H-E1, H-M1, Random)
    """
```

**Pseudo-code:**
```python
def plot_accuracy_comparison(h_e1_acc, h_m1_acc, random_acc, output_path):
    import matplotlib.pyplot as plt
    
    methods = ["H-E1\n(All Weight Stats)", "H-M1\n(Gradient Flow)", "Random\nBaseline"]
    accuracies = [h_e1_acc, h_m1_acc, random_acc]
    colors = ["green", "blue", "gray"]
    
    plt.figure(figsize=(8, 6))
    bars = plt.bar(methods, accuracies, color=colors, alpha=0.7)
    
    # Add accuracy labels on bars
    for bar, acc in zip(bars, accuracies):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                 f"{acc:.1%}", ha='center', va='bottom', fontsize=12)
    
    plt.ylabel("Test Accuracy", fontsize=12)
    plt.title("H-M1: Gradient Flow Mechanism Validation", fontsize=14, fontweight='bold')
    plt.ylim(0, 1.1)
    plt.axhline(y=0.5, color='red', linestyle='--', label='Random Baseline (50%)')
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
```

### 7.2 Feature Importance Comparison (Optional)

**Function Signature:**
```python
def plot_feature_importance_comparison(
    h_e1_coefficients: np.ndarray,  # (4,)
    h_m1_coefficients: np.ndarray,  # (6,)
    output_path: str
) -> None:
    """
    Compare feature importance between H-E1 (4 features) and H-M1 (6 features).
    
    Args:
        h_e1_coefficients: Logistic regression coefficients from H-E1
        h_m1_coefficients: Logistic regression coefficients from H-M1
        output_path: Save path
    
    Saves:
        Side-by-side bar chart showing coefficient magnitudes
    """
```

---

## 8. Tensor Shape Reference

### 8.1 Data Tensors

| Tensor | Shape | Description |
|--------|-------|-------------|
| `model.parameters()` | Iterator[Variable] | All model parameters |
| `param.data` | (out, in, h, w) or (out, in) | Conv2d or Linear weights |
| `layer_norms` | (L,) | L = number of layers |
| `layer_positions` | (L,) | Normalized positions [0, 1] |
| `features` | (6,) | Gradient-flow features per model |
| `all_features` | (20, 6) | All models × 6 features |
| `labels` | (20,) | Binary labels (0=shallow, 1=deep) |

### 8.2 Training Tensors

| Tensor | Shape | Description |
|--------|-------|-------------|
| `X_train` | (16, 6) | Training features |
| `y_train` | (16,) | Training labels |
| `X_test` | (4, 6) | Test features |
| `y_test` | (4,) | Test labels |
| `y_pred` | (4,) | Predicted labels |
| `confusion_matrix` | (2, 2) | [[TN, FP], [FN, TP]] |
| `classifier.coef_` | (1, 6) | Logistic regression coefficients |

---

## 9. Algorithm Complexity

| Module | Time Complexity | Space Complexity |
|--------|-----------------|------------------|
| `extract_features` | O(L) | O(L) |
| `load_pretrained_models` | O(M × W) | O(M × W) |
| `train_classifier` | O(N × F) | O(F) |
| `run_experiment` | O(M × L + N × F) | O(M × F) |

Where:
- L = layers per model (~20-200)
- M = number of models (20)
- W = weights per model (~millions, auto-download once)
- N = training samples (16)
- F = number of features (6)

**Expected Runtime:** <60 seconds (dominated by model loading ~30s)

---

## 10. Error Handling

### 10.1 Model Loading Failures

```python
def load_pretrained_models():
    try:
        models = {}
        for name in SHALLOW_MODELS + DEEP_MODELS:
            model_class = getattr(torchvision.models, name)
            models[name] = model_class(pretrained=True)
        return models
    except Exception as e:
        raise RuntimeError(f"Model loading failed: {e}. Check internet connection for auto-download.")
```

### 10.2 Feature Extraction Edge Cases

```python
def extract_features(self, model):
    layer_norms = []
    layer_positions = []
    
    total_layers = sum(1 for p in model.parameters() if p.requires_grad and len(p.shape) >= 2)
    
    if total_layers == 0:
        # No trainable layers (edge case)
        return np.zeros(6)
    
    # ... extraction logic ...
    
    # Handle single-layer models
    if len(layer_norms) == 1:
        norm_slope = 0.0  # Undefined slope
    else:
        norm_slope = np.polyfit(layer_positions, layer_norms, deg=1)[0]
    
    # ... rest of features ...
```

---

## 11. Testing Strategy

### 11.1 Unit Tests

```python
# test_feature_extractor.py

def test_extract_features_shape():
    """Verify output shape is (6,)"""
    extractor = GradientFlowFeatureExtractor()
    model = torchvision.models.resnet18(pretrained=True)
    features = extractor.extract_features(model)
    assert features.shape == (6,), f"Expected (6,), got {features.shape}"

def test_extract_features_range():
    """Verify features are reasonable values"""
    extractor = GradientFlowFeatureExtractor()
    model = torchvision.models.resnet50(pretrained=True)
    features = extractor.extract_features(model)
    
    # Norms should be positive
    assert features[2] > 0, "Input norm should be positive"
    assert features[3] > 0, "Output norm should be positive"
    
    # Layer count should match architecture
    assert features[5] > 50, "ResNet50 should have >50 layers"

def test_shallow_vs_deep_features():
    """Verify shallow and deep models have different features"""
    extractor = GradientFlowFeatureExtractor()
    shallow = torchvision.models.resnet18(pretrained=True)
    deep = torchvision.models.resnet50(pretrained=True)
    
    feat_shallow = extractor.extract_features(shallow)
    feat_deep = extractor.extract_features(deep)
    
    # Layer count should differ
    assert feat_shallow[5] < feat_deep[5], "Deep model should have more layers"
```

---

## 12. Applied Patterns (Archon KB)

**Applied:** Research experiment best practices
- **Pattern 1:** Controlled baseline comparison (H-E1 vs H-M1 vs Random)
- **Pattern 2:** Feature extraction from pretrained weights (no re-training)
- **Pattern 3:** Linear model for interpretability (coefficient = feature importance)
- **Pattern 4:** Stratified train-test split (preserve class balance)
- **Pattern 5:** Random initialization control (verify training-induced patterns)

**Source:** Archon Knowledge Base - Deep Learning Experiment Design Patterns

---

*Logic Document v1.0 | Generated by Phase 3 Logic Agent | Hypothesis: H-M1*
