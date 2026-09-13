# Logic Specification: h-e1 Weight-Based Depth Classification

**Hypothesis:** h-e1 (EXISTENCE)  
**Date:** 2026-04-21  
**Author:** logic-agent  
**Type:** PoC API Design  

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation - no existing code to analyze  
**Analyzed Path**: N/A  
**Relevant Symbols**: None - foundation hypothesis with clean slate implementation

---

## Applied Patterns

**From Archon KB:**
- Applied: PyTorch model introspection (`.named_parameters()` iteration)
- Applied: sklearn StandardScaler normalization pattern
- Applied: Binary classification pipeline (LogisticRegression)

---

## E1: Setup & Data Loading [Complexity: 8, Budget: 8]

**Applied**: Standard torchvision model loading pattern

### API Signatures

```python
from typing import Dict, Tuple, List
import torch.nn as nn

class ModelLoader:
    """Load pretrained ImageNet models from torchvision."""
    
    def __init__(self):
        """Initialize model loader."""
        self.shallow_names = [
            "resnet18", "resnet34", "vgg11", "vgg13", "vgg16", 
            "vgg19", "alexnet", "squeezenet1_0", "mobilenet_v2", "densenet121"
        ]
        self.deep_names = [
            "resnet50", "resnet101", "resnet152", "densenet161", "densenet169",
            "densenet201", "wide_resnet50_2", "wide_resnet101_2", 
            "resnext50_32x4d", "resnext101_32x8d"
        ]
    
    def load_shallow_models(self) -> Dict[str, nn.Module]:
        """Load shallow models (≤34 layers). Returns: {name: model}"""
        ...
    
    def load_deep_models(self) -> Dict[str, nn.Module]:
        """Load deep models (≥50 layers). Returns: {name: model}"""
        ...
    
    def load_all_models(self) -> Tuple[Dict[str, nn.Module], Dict[str, nn.Module]]:
        """Load all 20 models. Returns: (shallow_dict, deep_dict)"""
        ...
```

### Pseudo-code

```
1. Import torchvision.models
2. For each model name:
   - Call models.{name}(pretrained=True)
   - Auto-download weights to ~/.cache/torch/hub/
3. Return dicts: {name: model_instance}
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E1-1 | ModelLoader.__init__ | Define model name lists (10 shallow + 10 deep) |
| L-E1-2 | load_shallow_models | Iterate shallow_names, call torchvision API |
| L-E1-3 | load_deep_models | Iterate deep_names, call torchvision API |
| L-E1-4 | load_all_models | Wrapper calling both loaders |
| L-E1-5 | Error handling | Graceful model loading failures |
| L-E1-6 | Progress logging | Print loading progress (1/20, 2/20, ...) |
| L-E1-7 | Config integration | Import model lists from config.py |
| L-E1-8 | Return format | Structured dicts for downstream processing |

---

## E2: Feature Extraction [Complexity: 10, Budget: 10]

**Applied**: PyTorch Frobenius norm computation + numpy statistics

### API Signatures

```python
import torch
import numpy as np
from typing import List

class FeatureExtractor:
    """Extract layer-wise Frobenius norm statistics."""
    
    def extract_layer_norms(self, model: nn.Module) -> np.ndarray:
        """Extract Frobenius norm per layer. Returns: [L,] array"""
        ...
    
    def compute_statistics(self, layer_norms: np.ndarray) -> np.ndarray:
        """Compute [mean, std, min, max]. Returns: [4,] array"""
        ...
    
    def extract_features(self, model: nn.Module) -> np.ndarray:
        """End-to-end extraction. Returns: [4,] feature vector"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| layer_norms | [L,] | L = number of weight layers in model |
| statistics | [4,] | [mean, std, min, max] |

### Pseudo-code

```
extract_layer_norms(model):
    norms = []
    for name, param in model.named_parameters():
        if 'weight' in name and param.requires_grad:
            norm = torch.norm(param.data, p='fro').item()  # Frobenius norm
            norms.append(norm)
    return np.array(norms)

compute_statistics(layer_norms):
    mean = np.mean(layer_norms)
    std = np.std(layer_norms)
    min_val = np.min(layer_norms)
    max_val = np.max(layer_norms)
    return np.array([mean, std, min_val, max_val])

extract_features(model):
    norms = extract_layer_norms(model)
    return compute_statistics(norms)
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E2-1 | FeatureExtractor class | Initialize empty extractor |
| L-E2-2 | named_parameters iteration | Loop through model parameters |
| L-E2-3 | Weight filtering | Select only trainable weights (exclude biases) |
| L-E2-4 | Frobenius norm computation | torch.norm(param.data, p='fro') |
| L-E2-5 | Norm aggregation | Collect norms into list → numpy array |
| L-E2-6 | Statistics computation | np.mean, std, min, max |
| L-E2-7 | Shape validation | Ensure output is [4,] |
| L-E2-8 | Non-zero check | Verify all norms > 0 |
| L-E2-9 | extract_features wrapper | Combine extraction + statistics |
| L-E2-10 | Batch processing | Extract features for all 20 models |

---

## E3: Classification Pipeline [Complexity: 12, Budget: 12]

**Applied**: sklearn stratified split + StandardScaler + LogisticRegression

### API Signatures

```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

class DepthClassifier:
    """Binary depth classifier with feature normalization."""
    
    def __init__(self, random_state: int = 42):
        """Initialize classifier and scaler."""
        self.scaler = StandardScaler()
        self.classifier = LogisticRegression(
            C=1.0,
            solver='lbfgs',
            max_iter=1000,
            random_state=random_state
        )
        self.is_trained = False
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """Train classifier. X_train: [N, 4], y_train: [N,]"""
        ...
    
    def predict(self, X_test: np.ndarray) -> np.ndarray:
        """Predict labels. X_test: [M, 4] -> [M,]"""
        ...
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities. X: [N, 4] -> [N, 2]"""
        ...
    
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Compute accuracy. Returns: float in [0, 1]"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| X_train | [16, 4] | Training features (80% split) |
| y_train | [16,] | Training labels (0=shallow, 1=deep) |
| X_test | [4, 4] | Test features (20% split) |
| y_test | [4,] | Test labels |
| predictions | [4,] | Binary predictions |
| probabilities | [4, 2] | [P(shallow), P(deep)] |

### Pseudo-code

```
train(X_train, y_train):
    X_scaled = scaler.fit_transform(X_train)  # Fit scaler on train only
    classifier.fit(X_scaled, y_train)
    is_trained = True

predict(X_test):
    assert is_trained, "Must train first"
    X_scaled = scaler.transform(X_test)  # Use training scaler
    return classifier.predict(X_scaled)

score(X, y):
    predictions = predict(X)
    accuracy = (predictions == y).mean()
    return accuracy
```

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E3-1 | DepthClassifier.__init__ | Initialize scaler + classifier |
| L-E3-2 | Data split | train_test_split(stratify=y, test_size=0.2, random_state=42) |
| L-E3-3 | Scaler fitting | scaler.fit(X_train) - training data only |
| L-E3-4 | Train normalization | scaler.transform(X_train) |
| L-E3-5 | Test normalization | scaler.transform(X_test) - no refitting |
| L-E3-6 | Classifier training | classifier.fit(X_scaled, y_train) |
| L-E3-7 | Prediction | classifier.predict(X_test_scaled) |
| L-E3-8 | Probability estimates | classifier.predict_proba(X_scaled) |
| L-E3-9 | Training accuracy | score(X_train, y_train) |
| L-E3-10 | Test accuracy | score(X_test, y_test) |
| L-E3-11 | Convergence check | Verify no sklearn warnings |
| L-E3-12 | State validation | is_trained flag prevents predict before train |

---

## E4: Evaluation & Visualization [Complexity: 11, Budget: 11]

**Applied**: sklearn.metrics + matplotlib visualization patterns

### API Signatures

```python
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from typing import Dict, Tuple
import matplotlib.pyplot as plt

class Evaluator:
    """Compute metrics and verify gate condition."""
    
    def compute_metrics(
        self, 
        y_true: np.ndarray, 
        y_pred: np.ndarray
    ) -> Dict[str, any]:
        """Compute accuracy, confusion matrix, classification report."""
        ...
    
    def verify_mechanism(self, results: Dict) -> Tuple[bool, bool, bool, bool]:
        """Check 4 activation indicators. Returns: (feat_ext, norms_valid, trained, effect)"""
        ...
    
    def check_gate_condition(
        self, 
        test_accuracy: float, 
        threshold: float = 0.70
    ) -> bool:
        """Gate check: test_accuracy >= threshold. Returns: PASS/FAIL"""
        ...


class Visualizer:
    """Generate 5 analysis figures."""
    
    def __init__(self, output_dir: str):
        """Initialize with output directory."""
        self.output_dir = output_dir
    
    def plot_gate_metrics(
        self, 
        baseline: float, 
        actual: float, 
        target: float, 
        passed: bool
    ) -> None:
        """MANDATORY: Gate condition visualization. Saves to figures/gate_metrics.png"""
        ...
    
    def plot_confusion_matrix(
        self, 
        cm: np.ndarray, 
        class_names: List[str]
    ) -> None:
        """Confusion matrix heatmap. Saves to figures/confusion_matrix.png"""
        ...
    
    def plot_feature_distributions(
        self, 
        features_shallow: np.ndarray, 
        features_deep: np.ndarray
    ) -> None:
        """Box plots for 4 features. Saves to figures/feature_distributions.png"""
        ...
    
    def plot_feature_importance(
        self, 
        coefficients: np.ndarray, 
        feature_names: List[str]
    ) -> None:
        """Logistic regression coefficients. Saves to figures/feature_importance.png"""
        ...
    
    def plot_train_test_comparison(
        self, 
        train_acc: float, 
        test_acc: float
    ) -> None:
        """Train vs test accuracy bars. Saves to figures/train_test_comparison.png"""
        ...
```

### Pseudo-code

```
compute_metrics(y_true, y_pred):
    accuracy = accuracy_score(y_true, y_pred)
    cm = confusion_matrix(y_true, y_pred)
    report = classification_report(y_true, y_pred, output_dict=True)
    return {'accuracy': accuracy, 'cm': cm, 'report': report}

verify_mechanism(results):
    feat_ext = results['num_models'] == 20 and results['feature_shape'] == (4,)
    norms_valid = results['min_layer_count'] > 0 and results['max_layer_count'] > 0
    trained = results['train_accuracy'] > 0
    effect = results['test_accuracy'] > 0.50
    return (feat_ext, norms_valid, trained, effect)

check_gate_condition(test_accuracy, threshold=0.70):
    gate_passed = test_accuracy >= threshold
    print(f"Gate Status: {'PASS' if gate_passed else 'FAIL'}")
    return gate_passed

plot_gate_metrics(baseline, actual, target, passed):
    fig, ax = plt.subplots(figsize=(8, 6))
    x = ['Baseline', 'Actual', 'Target']
    y = [baseline, actual, target]
    colors = ['gray', 'green' if passed else 'red', 'blue']
    ax.bar(x, y, color=colors)
    ax.axhline(y=target, color='black', linestyle='--', label='Threshold')
    ax.set_ylabel('Accuracy')
    ax.set_title(f'Gate Condition: {"PASS" if passed else "FAIL"}')
    plt.savefig(f'{output_dir}/figures/gate_metrics.png', dpi=300)
```

### Subtasks [11/11 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-E4-1 | Evaluator.__init__ | Initialize evaluator |
| L-E4-2 | Accuracy computation | sklearn.metrics.accuracy_score |
| L-E4-3 | Confusion matrix | sklearn.metrics.confusion_matrix (2×2) |
| L-E4-4 | Classification report | Per-class precision/recall/f1 |
| L-E4-5 | Mechanism verification | Check 4 boolean indicators |
| L-E4-6 | Gate condition check | test_accuracy >= 0.70 → PASS/FAIL |
| L-E4-7 | Visualizer.__init__ | Create output_dir/figures/ directory |
| L-E4-8 | Gate metrics plot | MANDATORY bar chart with threshold line |
| L-E4-9 | Confusion matrix heatmap | Seaborn annotated heatmap |
| L-E4-10 | Feature distributions | 4 box plots (shallow vs deep) |
| L-E4-11 | Feature importance | Classifier coefficients bar chart |

---

## Main Experiment Orchestrator

**Applied**: Standard experiment pipeline pattern

### API Signatures

```python
class WeightDepthExperiment:
    """Main experiment orchestrator."""
    
    def __init__(self, output_dir: str = "h-e1", random_state: int = 42):
        """Initialize experiment with output directory."""
        self.output_dir = output_dir
        self.random_state = random_state
        self.loader = ModelLoader()
        self.extractor = FeatureExtractor()
        self.classifier = DepthClassifier(random_state=random_state)
        self.evaluator = Evaluator()
        self.visualizer = Visualizer(output_dir=output_dir)
        self.results = {}
    
    def run(self) -> Dict[str, any]:
        """Execute full pipeline. Returns: results dict with metrics + gate status"""
        ...
    
    def _extract_all_features(
        self, 
        shallow_models: Dict[str, nn.Module], 
        deep_models: Dict[str, nn.Module]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Extract features from all models. Returns: (X, y) with X: [20, 4], y: [20,]"""
        ...
    
    def _split_data(
        self, 
        X: np.ndarray, 
        y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Stratified split. Returns: (X_train, X_test, y_train, y_test)"""
        ...
    
    def _train_classifier(
        self, 
        X_train: np.ndarray, 
        y_train: np.ndarray
    ) -> None:
        """Train depth classifier."""
        ...
    
    def _evaluate(
        self, 
        X_test: np.ndarray, 
        y_test: np.ndarray
    ) -> Dict[str, any]:
        """Compute test metrics. Returns: metrics dict"""
        ...
    
    def _generate_visualizations(self, results: Dict) -> None:
        """Generate all 5 figures."""
        ...
```

### Pseudo-code

```
run():
    # 1. Load models
    shallow_models, deep_models = loader.load_all_models()
    
    # 2. Extract features
    X, y = _extract_all_features(shallow_models, deep_models)
    
    # 3. Split data
    X_train, X_test, y_train, y_test = _split_data(X, y)
    
    # 4. Train classifier
    _train_classifier(X_train, y_train)
    
    # 5. Evaluate
    results = _evaluate(X_test, y_test)
    
    # 6. Gate check
    gate_passed = evaluator.check_gate_condition(results['test_accuracy'])
    results['gate_passed'] = gate_passed
    
    # 7. Visualize
    _generate_visualizations(results)
    
    # 8. Save results
    save_results(results)
    
    return results

_extract_all_features(shallow_models, deep_models):
    features = []
    labels = []
    
    # Shallow models (label=0)
    for name, model in shallow_models.items():
        feat = extractor.extract_features(model)
        features.append(feat)
        labels.append(0)
    
    # Deep models (label=1)
    for name, model in deep_models.items():
        feat = extractor.extract_features(model)
        features.append(feat)
        labels.append(1)
    
    X = np.array(features)  # [20, 4]
    y = np.array(labels)    # [20,]
    return X, y

_split_data(X, y):
    from sklearn.model_selection import train_test_split
    return train_test_split(
        X, y, 
        test_size=0.2, 
        stratify=y, 
        random_state=self.random_state
    )
```

---

## Main Script Entry Point

### API Signatures

```python
def main():
    """Execute h-e1 experiment."""
    import os
    
    # Setup
    output_dir = "h-e1"
    os.makedirs(f"{output_dir}/figures", exist_ok=True)
    
    # Run experiment
    experiment = WeightDepthExperiment(output_dir=output_dir, random_state=42)
    results = experiment.run()
    
    # Display results
    print("\n" + "="*60)
    print("H-E1 WEIGHT-BASED DEPTH CLASSIFICATION RESULTS")
    print("="*60)
    print(f"Train Accuracy: {results['train_accuracy']:.2%}")
    print(f"Test Accuracy:  {results['test_accuracy']:.2%}")
    print(f"Baseline:       {results['baseline_accuracy']:.2%}")
    print(f"Target:         {results['target_accuracy']:.2%}")
    print(f"\nGate Status:    {'✓ PASS' if results['gate_passed'] else '✗ FAIL'}")
    print("="*60)
    
    # Mechanism verification
    indicators = results['mechanism_indicators']
    print("\nMechanism Verification:")
    print(f"  Features Extracted:   {'✓' if indicators[0] else '✗'}")
    print(f"  Layer Norms Valid:    {'✓' if indicators[1] else '✗'}")
    print(f"  Classifier Trained:   {'✓' if indicators[2] else '✗'}")
    print(f"  Effect Detected:      {'✓' if indicators[3] else '✗'}")
    print("\nFigures saved to: h-e1/figures/")
    print("Results saved to: h-e1/metrics.json")
    
    return 0 if results['gate_passed'] else 1


if __name__ == "__main__":
    exit(main())
```

---

## Configuration Module

### API Signatures

```python
# config.py
CONFIG = {
    # Dataset
    "shallow_models": [
        "resnet18", "resnet34", "vgg11", "vgg13", "vgg16", 
        "vgg19", "alexnet", "squeezenet1_0", "mobilenet_v2", "densenet121"
    ],
    "deep_models": [
        "resnet50", "resnet101", "resnet152", "densenet161", "densenet169",
        "densenet201", "wide_resnet50_2", "wide_resnet101_2", 
        "resnext50_32x4d", "resnext101_32x8d"
    ],
    
    # Data split
    "test_size": 0.2,
    "stratify": True,
    "random_state": 42,
    
    # Classifier
    "classifier": {
        "C": 1.0,
        "solver": "lbfgs",
        "max_iter": 1000,
        "random_state": 42
    },
    
    # Evaluation
    "gate_threshold": 0.70,
    "baseline_accuracy": 0.50,
    
    # Output
    "output_dir": "h-e1",
    "figure_dpi": 300
}
```

---

## Implementation Notes

### Critical Requirements

1. **Feature Normalization (MANDATORY)**
   - StandardScaler MUST be fit on training data only
   - Test data transformed using training scaler (no refitting)
   - Prevents data leakage

2. **Gate Condition Check**
   - Primary metric: test_accuracy >= 0.70
   - Must be clearly displayed in console output and gate_metrics.png
   - Exit code: 0 if PASS, 1 if FAIL

3. **Model Loading Pattern**
   ```python
   import torchvision.models as models
   model = models.resnet18(pretrained=True)  # Auto-downloads weights
   ```

4. **Frobenius Norm Extraction**
   ```python
   for name, param in model.named_parameters():
       if 'weight' in name and param.requires_grad:
           norm = torch.norm(param.data, p='fro').item()
   ```

5. **Mandatory Figure**
   - gate_metrics.png MUST show: baseline (50%), actual test accuracy, target (70%)
   - Color coding: Green if PASS (>=70%), Red if FAIL (<70%)
   - Horizontal line at 70% threshold

### Error Handling

- Graceful model loading failures (retry or skip)
- Validate feature shapes before training
- Check scaler fitted before transforming test data
- Ensure output directories exist

### Logging

- Print model loading progress (1/20, 2/20, ...)
- Log feature extraction for each model
- Display training start/completion
- Clear final metrics display

---

## Validation Checklist

**EXISTENCE PoC Compliance:**
- [x] Single forward() signatures only
- [x] Minimal pseudo-code (only for complex algorithms)
- [x] No ablation logic
- [x] No complex variants
- [x] Total length: 475 lines (within 300-500 target)

**Required Sections:**
- [x] Codebase Analysis (Serena) - green-field noted
- [x] Applied Patterns - Archon KB patterns listed
- [x] API signatures with type hints
- [x] Tensor shapes in comments
- [x] Subtasks within budget

**API Completeness:**
- [x] ModelLoader: load_all_models() → (shallow_dict, deep_dict)
- [x] FeatureExtractor: extract_features() → [4,] array
- [x] DepthClassifier: train(), predict(), score()
- [x] Evaluator: compute_metrics(), verify_mechanism(), check_gate_condition()
- [x] Visualizer: 5 plot methods (gate_metrics mandatory)
- [x] WeightDepthExperiment: run() → results dict

---

**Document Version:** 1.0  
**Total Tasks:** 4 (E1-E4)  
**Total Budget:** 41 subtasks allocated  
**Next Phase:** Phase 4 - Implementation
