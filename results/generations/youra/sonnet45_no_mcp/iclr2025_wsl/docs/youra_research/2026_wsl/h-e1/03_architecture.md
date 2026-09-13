# Architecture Specification: h-e1 Weight-Based Depth Classification

**Hypothesis:** h-e1 (EXISTENCE)  
**Date:** 2026-04-21  
**Author:** architecture-agent  
**Type:** PoC Validation  

**Applied Patterns**: Standard PyTorch model introspection + sklearn binary classification

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation from scratch  
**Analyzed Path**: N/A  
**Findings**: Foundation hypothesis - no existing code to analyze

---

## System Overview

**Mission**: Validate if layer-wise weight norm statistics can classify pretrained CNN architectural depth (shallow ≤34 vs deep ≥50 layers) with ≥70% accuracy.

**Architecture Pattern**: Feature extraction pipeline + binary classifier (EXISTENCE tier - minimal structure)

**Key Constraint**: MUST_WORK gate - Test accuracy ≥70% or workflow stops

---

## Module Structure

### FeatureExtractor (`src/feature_extractor.py`)

**Dependencies**: torch, numpy

```python
class FeatureExtractor:
    def extract_layer_norms(self, model: torch.nn.Module) -> np.ndarray: ...
    def compute_statistics(self, layer_norms: np.ndarray) -> np.ndarray: ...
    def extract_features(self, model: torch.nn.Module) -> np.ndarray: ...
```

### ModelLoader (`src/model_loader.py`)

**Dependencies**: torchvision.models

```python
class ModelLoader:
    def load_shallow_models(self) -> dict: ...
    def load_deep_models(self) -> dict: ...
    def load_all_models(self) -> tuple: ...
```

### DepthClassifier (`src/classifier.py`)

**Dependencies**: sklearn.linear_model, sklearn.preprocessing, FeatureExtractor

```python
class DepthClassifier:
    def __init__(self, random_state: int = 42): ...
    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None: ...
    def predict(self, X_test: np.ndarray) -> np.ndarray: ...
    def score(self, X: np.ndarray, y: np.ndarray) -> float: ...
```

### Evaluator (`src/evaluator.py`)

**Dependencies**: sklearn.metrics, numpy

```python
class Evaluator:
    def compute_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> dict: ...
    def verify_mechanism(self, results: dict) -> tuple: ...
    def check_gate_condition(self, test_accuracy: float, threshold: float = 0.70) -> bool: ...
```

### Visualizer (`src/visualizer.py`)

**Dependencies**: matplotlib, seaborn, numpy

```python
class Visualizer:
    def __init__(self, output_dir: str): ...
    def plot_gate_metrics(self, baseline: float, actual: float, target: float, passed: bool) -> None: ...
    def plot_confusion_matrix(self, cm: np.ndarray, class_names: list) -> None: ...
    def plot_feature_distributions(self, features_shallow: np.ndarray, features_deep: np.ndarray) -> None: ...
    def plot_feature_importance(self, coefficients: np.ndarray, feature_names: list) -> None: ...
    def plot_train_test_comparison(self, train_acc: float, test_acc: float) -> None: ...
```

### Experiment (`src/experiment.py`)

**Dependencies**: All above modules

```python
class WeightDepthExperiment:
    def __init__(self, output_dir: str, random_state: int = 42): ...
    def run(self) -> dict: ...
    def _extract_all_features(self, shallow_models: dict, deep_models: dict) -> tuple: ...
    def _split_data(self, X: np.ndarray, y: np.ndarray) -> tuple: ...
    def _train_classifier(self, X_train: np.ndarray, y_train: np.ndarray) -> None: ...
    def _evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict: ...
    def _generate_visualizations(self, results: dict) -> None: ...
```

### Main Script (`main.py`)

**Dependencies**: Experiment

```python
def main():
    experiment = WeightDepthExperiment(output_dir="h-e1/results")
    results = experiment.run()
    # Print final metrics and gate status
```

---

## File Organization

```
h-e1/
├── src/
│   ├── __init__.py
│   ├── model_loader.py          # Load 20 pretrained models
│   ├── feature_extractor.py     # Extract Frobenius norm statistics
│   ├── classifier.py            # Binary depth classifier
│   ├── evaluator.py             # Metrics and verification
│   └── visualizer.py            # Generate 5 analysis figures
├── main.py                      # Experiment entry point
├── config.py                    # Fixed configuration
├── results/
│   ├── features.npy             # Extracted features (20, 4)
│   ├── labels.npy               # Binary labels (20,)
│   └── metrics.json             # Final evaluation metrics
└── figures/
    ├── gate_metrics.png         # MANDATORY - gate condition visualization
    ├── confusion_matrix.png
    ├── feature_distributions.png
    ├── feature_importance.png
    └── train_test_comparison.png
```

---

## Data Flow

```
Models (torchvision)
    ↓
ModelLoader: Load 20 models (10 shallow + 10 deep)
    ↓
FeatureExtractor: Extract layer-wise Frobenius norms → [mean, std, min, max]
    ↓
Data Split: 80/20 stratified (16 train, 4 test)
    ↓
StandardScaler: Normalize features (mean=0, std=1)
    ↓
DepthClassifier: LogisticRegression binary classification
    ↓
Evaluator: Test accuracy ≥ 70%? → GATE PASS/FAIL
    ↓
Visualizer: Generate 5 analysis figures
```

---

## Configuration

**Fixed Configuration** (`config.py`):

```python
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

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E1 | Setup & Data Loading | Project structure + load 20 pretrained models | 8 | Module(2) + Deps(2) + Algo(2) + Integration(2) |
| E2 | Feature Extraction | Extract Frobenius norm statistics from model weights | 10 | Module(3) + Deps(2) + Algo(3) + Integration(2) |
| E3 | Classification Pipeline | Train-test split + normalization + binary classifier | 12 | Module(3) + Deps(3) + Algo(3) + Integration(3) |
| E4 | Evaluation & Visualization | Compute metrics + gate check + generate 5 figures | 11 | Module(3) + Deps(2) + Algo(3) + Integration(3) |

**Distribution**: High(9-13): [E2, E3, E4], Low(4-8): [E1]

**Total Complexity**: 41 (Light EXISTENCE tier - 4 epic tasks)

---

## Complexity Breakdown

### E1: Setup & Data Loading (8)
- **Module Size (2)**: ModelLoader class + config
- **Dependencies (2)**: torchvision.models API
- **Algorithm (2)**: Sequential model loading with auto-download
- **Integration (2)**: Standalone data loading component

### E2: Feature Extraction (10)
- **Module Size (3)**: FeatureExtractor class with 3 methods
- **Dependencies (2)**: PyTorch tensor operations + numpy
- **Algorithm (3)**: Frobenius norm computation + statistics aggregation
- **Integration (2)**: Pure feature extraction (no model modification)

### E3: Classification Pipeline (12)
- **Module Size (3)**: DepthClassifier + data splitting logic
- **Dependencies (3)**: sklearn (LogisticRegression, StandardScaler, train_test_split)
- **Algorithm (3)**: Stratified split + feature normalization + logistic regression
- **Integration (3)**: Connects feature extraction → training → prediction

### E4: Evaluation & Visualization (11)
- **Module Size (3)**: Evaluator + Visualizer classes
- **Dependencies (2)**: sklearn.metrics + matplotlib/seaborn
- **Algorithm (3)**: Metrics computation + mechanism verification + 5 figures
- **Integration (3)**: Final results pipeline + gate condition checking

---

## Interface Contracts

### FeatureExtractor Interface

**Input**: PyTorch model object  
**Output**: NumPy array shape (4,) - [mean, std, min, max]

**Contract**:
- Must extract only trainable weight parameters (exclude biases, batch norm)
- Must compute Frobenius norm per layer
- Must return 4 statistics: mean, std, min, max

### DepthClassifier Interface

**Input**: Feature array (N, 4), labels (N,)  
**Output**: Test accuracy (float)

**Contract**:
- Must apply StandardScaler to features before training
- Must use same scaler for test data transformation
- Must return predictions and probability estimates

### Evaluator Interface

**Input**: True labels, predicted labels  
**Output**: Metrics dict with accuracy, confusion matrix, classification report

**Contract**:
- Primary metric: test_accuracy (float)
- Gate check: test_accuracy >= 0.70 → PASS, else FAIL
- Mechanism verification: 4 boolean indicators (features_extracted, layer_norms_valid, classifier_trained, effect_detected)

### Visualizer Interface

**Input**: Metrics dict, features, labels  
**Output**: 5 PNG figures saved to h-e1/figures/

**Contract**:
- MANDATORY: gate_metrics.png showing baseline/actual/target with pass/fail color
- 4 additional figures: confusion matrix, feature distributions, feature importance, train-test comparison
- All figures 300 DPI publication quality

---

## Mechanism Verification

**Pre-conditions**:
1. All 20 models loadable via torchvision API
2. All models expose `.named_parameters()` method
3. Weight tensors accessible and non-zero

**Activation Indicators**:

| Indicator | Check | Expected |
|-----------|-------|----------|
| features_extracted | num_models_processed == 20 AND feature_shape == (4,) | TRUE |
| layer_norms_valid | min_layer_count > 0 AND max_layer_count > 0 | TRUE |
| classifier_trained | training_accuracy > 0 | TRUE |
| effect_detected | test_accuracy > 0.50 | TRUE |

**Success Criteria**:
- **Mechanism Works**: All 4 indicators TRUE + test_accuracy > 50%
- **Hypothesis Supported**: test_accuracy >= 70% (GATE PASS)

**Failure Modes**:
- feature_shape != (4,) → Feature extraction broken
- All norms == 0 → Frobenius norm computation failed
- test_accuracy <= 50% → No depth signal in weight statistics
- Convergence warnings → Feature normalization missing

---

## Testing Strategy

**Unit Tests** (Optional for EXISTENCE PoC):
- FeatureExtractor: Verify output shape (4,) for test model
- ModelLoader: Verify 20 models loaded
- DepthClassifier: Verify training completes without warnings

**Integration Test** (Main experiment):
- Full pipeline: Load models → Extract features → Train → Evaluate → Visualize
- Expected runtime: <10 minutes total
- Expected output: 5 figures + metrics.json + gate status

**Gate Validation**:
- Primary: test_accuracy >= 0.70 (MUST_WORK condition)
- Secondary: training_accuracy reported (overfitting check)
- Tertiary: All 4 mechanism indicators TRUE

---

## Dependencies

**External Libraries**:
- PyTorch >= 1.10 (model loading, tensor operations)
- torchvision >= 0.11 (pretrained models)
- scikit-learn >= 0.24 (classification, preprocessing, metrics)
- numpy >= 1.20 (array operations)
- matplotlib >= 3.3 (visualization)
- seaborn >= 0.11 (enhanced visualizations)

**System Requirements**:
- Python 3.8+
- Disk: ~5GB (model cache in ~/.cache/torch/hub/)
- RAM: 8GB minimum
- GPU: Optional (CPU sufficient for this experiment)

---

## Risk Analysis

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Model download fails | Low | High | Auto-retry on first run, cache for subsequent runs |
| Feature normalization skipped | Medium | Critical | Explicit StandardScaler in pipeline, validation check |
| Small sample overfitting | High | Medium | Report train/test accuracy gap, expect some overfitting (n=16) |
| Gate threshold too high | Medium | High | 70% threshold based on correlation analysis (ρ=0.859), but n=20 is small |
| Architecture variations | Low | Low | Frobenius norm works uniformly across ResNet/VGG/DenseNet |

---

## Success Metrics

**Primary (MUST_WORK Gate)**:
- Test accuracy >= 70% on 4 held-out models

**Secondary (Mechanism Verification)**:
- All 4 activation indicators TRUE
- Test accuracy > 50% (better than random)
- Training completes without convergence warnings

**Deliverables**:
- ✅ Working experiment code
- ✅ 5 analysis figures (gate metrics mandatory)
- ✅ Metrics JSON with gate status
- ✅ Mechanism verification report

---

## Notes for Phase 4

**Critical Implementation Details**:

1. **Feature Normalization is MANDATORY**
   - Weight magnitudes vary 10³-10⁴ across architectures
   - StandardScaler MUST be fit on training data only
   - Test data transformed using training scaler

2. **Model Loading Pattern**
   ```python
   import torchvision.models as models
   model = models.resnet18(pretrained=True)  # Auto-downloads on first use
   ```

3. **Frobenius Norm Extraction**
   ```python
   for name, param in model.named_parameters():
       if 'weight' in name and param.requires_grad:
           norm = torch.norm(param.data, p='fro').item()
   ```

4. **Gate Condition Check**
   ```python
   gate_passed = test_accuracy >= 0.70
   print(f"Gate Status: {'PASS' if gate_passed else 'FAIL'}")
   ```

5. **Mandatory Figure**
   - gate_metrics.png MUST show: baseline (50%), actual, target (70%)
   - Color: Red if FAIL (<70%), Green if PASS (>=70%)
   - Horizontal line at 70% threshold

---

**Document Version**: 1.0  
**Total Epic Tasks**: 4 (EXISTENCE tier - minimal PoC)  
**Next Phase**: Phase 4 - Implementation
