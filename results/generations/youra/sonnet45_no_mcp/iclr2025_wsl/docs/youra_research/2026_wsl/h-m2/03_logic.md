# Logic Design: H-M2 Architectural Constraints Mechanism Validation

**Hypothesis:** H-M2  
**Type:** Mechanism  
**Date:** 2026-04-21  
**Author:** Logic Agent (Phase 3)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from H-M1 actual code  
**Analyzed Path:** `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_wsl_3/docs/youra_research/20260421_wsl/h-m1/code/`  
**Relevant Symbols:** ModelLoader, DepthClassifier, Evaluator, Visualizer, RandomInitTest

**Key Findings:**
- H-M1 uses modular src/ package structure with 6 core modules
- ModelLoader provides `load_all_models() -> (shallow_dict, deep_dict)` and `load_random_model(model_name: str)`
- DepthClassifier encapsulates StandardScaler + LogisticRegression with `train()`, `predict()`, `score()`, `get_coefficients()`
- Evaluator provides `compute_metrics()`, `check_gate_condition()`, `compare_with_baseline()`
- Visualizer generates 5 figure types, extensible for within-family plots
- RandomInitTest orchestrates random model extraction and classification

**Applied:** DL experiment modular architecture pattern (Archon KB)

---

## External Dependencies API (Base Hypothesis H-M1)

### API Signatures (From Actual Code)

The following APIs are reused from H-M1. Signatures verified from actual implementation:

```python
# From: h-m1/code/src/model_loader.py (ACTUAL CODE)
class ModelLoader:
    def __init__(self, shallow_names: list = None, deep_names: list = None):
        """Initialize with model name lists. Defaults to 10 shallow + 10 deep."""
        pass
    
    def load_all_models(self) -> tuple:
        """Load all 20 models. Returns: (shallow_dict, deep_dict)"""
        pass
    
    def load_random_model(self, model_name: str) -> nn.Module:
        """Load randomly initialized model (pretrained=False). Returns: model"""
        pass

# From: h-m1/code/src/classifier.py (ACTUAL CODE)
class DepthClassifier:
    def __init__(self, random_state: int = 42):
        """Initialize classifier with StandardScaler and LogisticRegression."""
        pass
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """Train classifier. X_train: [N, F], y_train: [N,]"""
        pass
    
    def predict(self, X_test: np.ndarray) -> np.ndarray:
        """Predict labels. X_test: [M, F] -> [M,]"""
        pass
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Compute accuracy. Returns: float in [0, 1]"""
        pass
    
    def get_coefficients(self) -> np.ndarray:
        """Get logistic regression coefficients for feature importance."""
        pass

# From: h-m1/code/src/evaluator.py (ACTUAL CODE)
class Evaluator:
    def compute_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> dict:
        """Compute classification metrics. Returns: {confusion_matrix, classification_report, accuracy}"""
        pass
    
    def check_gate_condition(self, test_accuracy: float, threshold: float = 0.5) -> bool:
        """Check if gate condition is satisfied."""
        pass
    
    def compare_with_baseline(self, h_m1_accuracy: float, h_e1_accuracy: float, 
                              random_accuracy: float = None) -> dict:
        """Compare performance with baselines. Returns: comparison dict"""
        pass

# From: h-m1/code/src/visualizer.py (ACTUAL CODE)
class Visualizer:
    def __init__(self, output_dir: str = "./outputs/figures"):
        """Initialize visualizer with output directory."""
        pass
    
    def plot_accuracy_comparison(self, h_e1_accuracy: float, h_m1_accuracy: float,
                                 random_baseline: float = 0.5,
                                 random_test_accuracy: float = None) -> None:
        """Generate accuracy comparison bar chart. Saves to output_dir."""
        pass
    
    def plot_feature_importance(self, coefficients: np.ndarray, 
                               feature_names: list) -> None:
        """Plot feature importance from logistic regression coefficients."""
        pass
    
    def plot_confusion_matrix(self, cm: np.ndarray, class_names: list) -> None:
        """Plot confusion matrix."""
        pass
    
    def plot_feature_distributions(self, X_shallow: np.ndarray, X_deep: np.ndarray,
                                   feature_names: list) -> None:
        """Plot feature distributions for shallow vs deep models."""
        pass

# From: h-m1/code/src/random_init_test.py (ACTUAL CODE)
class RandomInitTest:
    def __init__(self, shallow_names: list, deep_names: list, random_state: int = 42):
        """Initialize random initialization test."""
        pass
    
    def run_random_test(self, test_size: float = 0.2) -> dict:
        """Run full random initialization test. Returns: {test_accuracy, train_accuracy, ...}"""
        pass
```

**Verified from:** H-M1 actual implementation (not specs)

---

## E-2: Architectural Feature Extractor [Complexity: 18, Budget: 5]

**Applied:** PyTorch module inspection pattern (Archon KB)

### API Signatures

```python
import torch
import torch.nn as nn
import numpy as np

class ArchitecturalFeatureExtractor:
    """Extract 8 architectural constraint features from pretrained CNNs."""
    
    def __init__(self):
        """Initialize extractor (no state needed)."""
        pass
    
    def extract_features(self, model: nn.Module) -> np.ndarray:
        """Extract 8 architectural features. model: nn.Module -> features: [8,]"""
        pass
    
    def count_residual_blocks(self, model: nn.Module) -> int:
        """Count modules with 'downsample' attribute. Returns: int"""
        pass
    
    def count_dense_connections(self, model: nn.Module) -> int:
        """Count 'denselayer' modules. Returns: int"""
        pass
    
    def compute_bottleneck_ratio(self, model: nn.Module) -> float:
        """Compute (1x1 convs) / (total convs). Returns: float in [0, 1]"""
        pass
    
    def extract_residual_path_norms(self, model: nn.Module) -> float:
        """Mean Frobenius norm of downsample layers. Returns: float"""
        pass
    
    def count_transition_layers(self, model: nn.Module) -> int:
        """Count DenseNet transition layers. Returns: int"""
        pass
    
    def detect_architecture_family(self, model: nn.Module) -> int:
        """Detect ResNet/DenseNet (1) vs VGG/other (0). Returns: int"""
        pass
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| model | nn.Module | Pretrained CNN |
| features | [8,] | Output feature vector |
| conv_layers | List[nn.Conv2d] | Variable length |
| residual_norms | List[float] | Variable length |

### Pseudo-code

```
extract_features(model):
    1. residual_blocks = count_residual_blocks(model)
    2. dense_connections = count_dense_connections(model)
    3. bottleneck_ratio = compute_bottleneck_ratio(model)
    4. layer_count = count_conv_layers(model)
    5. skip_present = 1 if (residual_blocks > 0 or dense_connections > 0) else 0
    6. residual_norm = extract_residual_path_norms(model)
    7. transition_count = count_transition_layers(model)
    8. arch_family = detect_architecture_family(model)
    return np.array([residual_blocks, dense_connections, bottleneck_ratio, 
                     layer_count, skip_present, residual_norm, transition_count, arch_family])

count_residual_blocks(model):
    count = 0
    for module in model.modules():
        if hasattr(module, 'downsample') and module.downsample is not None:
            count += 1
    return count

count_dense_connections(model):
    count = 0
    for name, module in model.named_modules():
        if 'denselayer' in name.lower():
            count += 1
    return count

compute_bottleneck_ratio(model):
    total_convs = 0
    bottleneck_convs = 0
    for module in model.modules():
        if isinstance(module, nn.Conv2d):
            total_convs += 1
            if module.kernel_size == (1, 1):
                bottleneck_convs += 1
    return bottleneck_convs / total_convs if total_convs > 0 else 0.0
```

### Subtasks [5/5 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Residual detection | Implement `count_residual_blocks()` via `hasattr(module, 'downsample')` |
| L-2-2 | Dense detection | Implement `count_dense_connections()` via name pattern matching |
| L-2-3 | Bottleneck ratio | Compute 1x1 conv ratio via kernel_size inspection |
| L-2-4 | Residual norms | Extract Frobenius norms from downsample layers |
| L-2-5 | Feature assembly | Combine 8 features into numpy array |

---

## E-3: Within-Family Validator [Complexity: 14, Budget: 4]

**Applied:** Stratified validation pattern (Archon KB)

### API Signatures

```python
class WithinFamilyValidator:
    """Validate depth signal within architecture families."""
    
    def __init__(self, random_state: int = 42):
        """Initialize validator with random seed."""
        self.random_state = random_state
    
    def classify_model_family(self, model_name: str) -> str:
        """Detect family from model name. Returns: 'resnet' | 'vgg' | 'densenet' | 'other'"""
        pass
    
    def validate_within_family(self, X: np.ndarray, y: np.ndarray, 
                               model_names: list, test_size: float = 0.2) -> dict:
        """Train per-family classifiers. X: [N, 8], y: [N,], names: [N] -> results: dict"""
        pass
    
    def train_family_classifier(self, X_family: np.ndarray, y_family: np.ndarray, 
                               family_name: str) -> dict:
        """Train classifier on single family. Returns: {accuracy, num_samples}"""
        pass
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| X | [N, 8] | All features |
| y | [N,] | All labels |
| X_family | [M, 8] | Family subset (M < N) |
| y_family | [M,] | Family labels |
| results | dict | Per-family accuracies |

### Pseudo-code

```
validate_within_family(X, y, model_names, test_size):
    1. families = {'resnet': [], 'vgg': [], 'densenet': []}
    2. For i, name in enumerate(model_names):
        family = classify_model_family(name)
        families[family].append(i)
    
    3. results = {}
    4. For family, indices in families.items():
        if len(indices) < 4:  # Skip insufficient samples
            continue
        X_fam = X[indices]
        y_fam = y[indices]
        results[family] = train_family_classifier(X_fam, y_fam, family)
    
    5. return results

classify_model_family(model_name):
    if 'resnet' in model_name.lower():
        return 'resnet'
    elif 'vgg' in model_name.lower():
        return 'vgg'
    elif 'densenet' in model_name.lower():
        return 'densenet'
    else:
        return 'other'

train_family_classifier(X_family, y_family, family_name):
    classifier = DepthClassifier(random_state=self.random_state)
    X_train, X_test, y_train, y_test = train_test_split(
        X_family, y_family, test_size=0.2, stratify=y_family, random_state=self.random_state)
    classifier.train(X_train, y_train)
    accuracy = classifier.score(X_test, y_test)
    return {'accuracy': accuracy, 'num_samples': len(X_family)}
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Family classifier | Implement `classify_model_family()` via string pattern matching |
| L-3-2 | Data filtering | Group features by family into separate datasets |
| L-3-3 | Per-family training | Train DepthClassifier on each family subset |
| L-3-4 | Results aggregation | Collect and return per-family accuracies |

---

## Visualization Extension (Part of E-6)

**Applied:** Matplotlib comparison visualization pattern (Archon KB)

### API Signatures

```python
# Extension to H-M1 Visualizer class
class Visualizer:
    # ... (H-M1 methods reused) ...
    
    def plot_within_family_comparison(self, family_results: dict, 
                                      all_families_accuracy: float) -> None:
        """Generate within-family vs all-families bar chart. 
        family_results: {'resnet': {accuracy, ...}, 'vgg': {...}, 'densenet': {...}}
        Saves to: output_dir/within_family_comparison.png"""
        pass
```

### Pseudo-code

```
plot_within_family_comparison(family_results, all_families_accuracy):
    families = list(family_results.keys()) + ['All Families']
    accuracies = [family_results[f]['accuracy'] for f in family_results.keys()] + [all_families_accuracy]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(families, accuracies, color=['steelblue', 'coral', 'lightgreen', 'gray'])
    
    for bar, acc in zip(bars, accuracies):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{acc:.1%}", ha='center', fontsize=12, fontweight='bold')
    
    ax.set_ylabel("Test Accuracy", fontsize=12)
    ax.set_title("H-M2: Within-Family Depth Classification", fontsize=14, fontweight='bold')
    ax.axhline(y=0.65, color='orange', linestyle='--', label='Within-Family Target (65%)')
    ax.axhline(y=0.5, color='red', linestyle=':', label='Random Baseline (50%)')
    ax.legend()
    plt.tight_layout()
    plt.savefig(f"{self.output_dir}/within_family_comparison.png", dpi=150)
    plt.close()
```

---

## Main Pipeline (Part of E-4)

**Applied:** Research experiment pipeline pattern (Archon KB)

### API Signatures

```python
def main() -> int:
    """Run H-M2 10-step pipeline. Returns: 0 (success) or 1 (failure)"""
    pass
```

### Pseudo-code

```
main():
    # [1/10] Load models
    loader = ModelLoader()
    shallow_models, deep_models = loader.load_all_models()
    
    # [2/10] Extract architectural features (8 features)
    extractor = ArchitecturalFeatureExtractor()
    features = []
    labels = []
    model_names = []
    
    for name, model in shallow_models.items():
        feat = extractor.extract_features(model)  # [8,]
        features.append(feat)
        labels.append(0)
        model_names.append(name)
    
    for name, model in deep_models.items():
        feat = extractor.extract_features(model)
        features.append(feat)
        labels.append(1)
        model_names.append(name)
    
    X = np.array(features)  # [20, 8]
    y = np.array(labels)    # [20,]
    
    # [3/10] Split data (80/20 stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42)
    
    # [4/10] Train all-families classifier
    classifier = DepthClassifier(random_state=42)
    classifier.train(X_train, y_train)
    
    # [5/10] Evaluate all-families accuracy
    y_pred = classifier.predict(X_test)
    test_accuracy = classifier.score(X_test, y_test)
    
    evaluator = Evaluator()
    metrics = evaluator.compute_metrics(y_test, y_pred)
    
    # [6/10] Within-family validation
    validator = WithinFamilyValidator(random_state=42)
    family_results = validator.validate_within_family(X, y, model_names, test_size=0.2)
    
    # [7/10] Random initialization test
    random_tester = RandomInitTest(
        shallow_names=list(shallow_models.keys()),
        deep_names=list(deep_models.keys()),
        random_state=42
    )
    # Replace extractor in RandomInitTest with ArchitecturalFeatureExtractor
    random_tester.extractor = extractor
    random_results = random_tester.run_random_test(test_size=0.2)
    
    # [8/10] Mechanism verification
    gate_passed = evaluator.check_gate_condition(test_accuracy, threshold=0.5)
    
    # [9/10] Gate check and baseline comparison
    comparison = evaluator.compare_with_baseline(
        h_m1_accuracy=test_accuracy,
        h_e1_accuracy=1.0,  # From H-E1 validation
        random_accuracy=random_results['test_accuracy']
    )
    
    # [10/10] Generate visualizations
    visualizer = Visualizer(output_dir="./outputs/figures")
    visualizer.plot_accuracy_comparison(
        h_e1_accuracy=1.0,
        h_m1_accuracy=test_accuracy,
        random_baseline=0.5,
        random_test_accuracy=random_results['test_accuracy']
    )
    visualizer.plot_feature_importance(
        coefficients=classifier.get_coefficients(),
        feature_names=[
            "Residual Blocks", "Dense Connections", "Bottleneck Ratio",
            "Layer Count", "Skip Connections", "Residual Norm",
            "Transition Layers", "Arch Family"
        ]
    )
    visualizer.plot_confusion_matrix(metrics['confusion_matrix'], ['shallow', 'deep'])
    visualizer.plot_within_family_comparison(family_results, test_accuracy)
    
    # Save metrics
    save_metrics({
        'test_accuracy': test_accuracy,
        'gate_passed': gate_passed,
        'family_results': family_results,
        'random_accuracy': random_results['test_accuracy'],
        'comparison': comparison
    }, "outputs/metrics.json")
    
    return 0 if gate_passed else 1
```

---

## Configuration

**Applied:** Centralized config pattern (Archon KB)

### API Signatures

```python
# config.py
CONFIG = {
    "hypothesis_id": "h-m2",
    "experiment_name": "Architectural Constraints Mechanism Validation",
    "base_hypothesis": "h-m1",
    "shallow_models": [...],  # 10 models
    "deep_models": [...],     # 10 models
    "test_size": 0.2,
    "random_state": 42,
    "feature_extractor": {"type": "ArchitecturalFeatureExtractor", "n_features": 8},
    "classifier": {"C": 1.0, "solver": "lbfgs", "max_iter": 1000},
    "within_family_threshold": 0.65,
    "run_random_test": True,
    "gate_threshold": 0.50,
    "h_e1_accuracy": 1.0,
    "h_m1_accuracy": 1.0,
    "results_dir": "./outputs",
    "figures_dir": "./outputs/figures",
}
```

---

## Algorithm Complexity

| Module | Time Complexity | Space Complexity |
|--------|-----------------|------------------|
| `extract_features` | O(M) | O(M) |
| `count_residual_blocks` | O(M) | O(1) |
| `count_dense_connections` | O(M) | O(1) |
| `validate_within_family` | O(F × N × D) | O(N × D) |
| `main` | O(K × M + F × N × D) | O(K × D) |

Where:
- M = modules per model (~100-500)
- K = number of models (20)
- F = number of families (3)
- N = samples per family (~4-7)
- D = feature dimension (8)

**Expected Runtime:** <90 seconds (dominated by model loading ~30s + feature extraction ~10s)

---

## Tensor Shape Reference

### Data Tensors

| Tensor | Shape | Description |
|--------|-------|-------------|
| `model.modules()` | Iterator[nn.Module] | All modules |
| `features` | [8,] | Per-model features |
| `X` | [20, 8] | All models × 8 features |
| `y` | [20,] | Binary labels (0=shallow, 1=deep) |
| `X_train` | [16, 8] | Training features |
| `X_test` | [4, 8] | Test features |
| `X_family` | [M, 8] | Family subset (M ≥ 4) |
| `confusion_matrix` | [2, 2] | [[TN, FP], [FN, TP]] |
| `coefficients` | [8,] | Feature importance weights |

---

## Error Handling

### Edge Cases

```python
# Handle models without skip connections (e.g., VGG)
def count_residual_blocks(self, model):
    count = 0
    for module in model.modules():
        if hasattr(module, 'downsample') and module.downsample is not None:
            count += 1
    return count  # Returns 0 for VGG (expected behavior)

# Handle families with insufficient samples
def validate_within_family(self, X, y, model_names, test_size):
    results = {}
    for family, indices in families.items():
        if len(indices) < 4:  # Need at least 4 for 80/20 split
            print(f"Warning: Skipping {family} (only {len(indices)} models)")
            continue
        # ... train classifier ...
    return results

# Handle zero convolutions (edge case)
def compute_bottleneck_ratio(self, model):
    total_convs = 0
    bottleneck_convs = 0
    for module in model.modules():
        if isinstance(module, nn.Conv2d):
            total_convs += 1
            if module.kernel_size == (1, 1):
                bottleneck_convs += 1
    return bottleneck_convs / total_convs if total_convs > 0 else 0.0
```

---

## Self-Validation

### Quick Checks
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in code comments
- [x] Total length < 600 lines
- [x] "Codebase Analysis (Serena)" section included
- [x] External Dependencies API section included
- [x] API signatures verified from actual H-M1 code

### Base Hypothesis Checks
- [x] Read actual code from H-M1 implementation
- [x] API signatures verified from actual code (not specs)
- [x] Parameter names exactly match actual code
- [x] External Dependencies API section included

---

*Logic Document v1.0 | Generated by Phase 3 Logic Agent | Hypothesis: H-M2 | Budget: 9 subtasks used*
