# Logic Design: H-M3 Batch Normalization Mechanism Validation

**Hypothesis:** H-M3  
**Type:** Mechanism  
**Date:** 2026-04-21  
**Author:** Logic Agent (Phase 3)

**Applied:** PyTorch module iteration pattern, DL feature extraction pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from H-M2 actual code  
**Analyzed Path:** `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_wsl_3/docs/youra_research/20260421_wsl/h-m2/code/`  
**Relevant Symbols:** ModelLoader, DepthClassifier, Evaluator, Visualizer, WithinFamilyValidator, RandomInitTest (6 modules reused), ArchitecturalFeatureExtractor (replaced)

**Key Findings:**
- H-M2 uses identical class signatures as H-M1 for reused modules
- Feature extractor is the ONLY module requiring replacement (8 architectural features → 6 BN features)
- All parameter names verified from actual code (not specs)

---

## External Dependencies (Base Hypothesis)

### API Signatures (From H-M2 Actual Code)

The following APIs are called from H-M2. Signatures verified from actual implementation:

```python
# From: h-m2/code/src/model_loader.py (ACTUAL CODE)
class ModelLoader:
    def __init__(self, shallow_names: list = None, deep_names: list = None):
        """Initialize model loader with model name lists."""
        ...

    def load_all_models(self) -> tuple:
        """Load all 20 models. Returns: (shallow_dict, deep_dict)"""
        ...

    def load_random_model(self, model_name: str) -> nn.Module:
        """Load randomly initialized model (pretrained=False). Returns: random model"""
        ...


# From: h-m2/code/src/classifier.py (ACTUAL CODE)
class DepthClassifier:
    def __init__(self, random_state: int = 42):
        """Initialize classifier and scaler."""
        ...

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """Train classifier. X_train: [N, F], y_train: [N,]"""
        ...

    def predict(self, X_test: np.ndarray) -> np.ndarray:
        """Predict labels. X_test: [M, F] -> [M,]"""
        ...

    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Compute accuracy. Returns: float in [0, 1]"""
        ...

    def get_coefficients(self) -> np.ndarray:
        """Get logistic regression coefficients for feature importance."""
        ...


# From: h-m2/code/src/evaluator.py (ACTUAL CODE)
class Evaluator:
    def compute_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> dict:
        """Compute classification metrics. Returns: {confusion_matrix, classification_report, accuracy}"""
        ...

    def check_gate_condition(self, test_accuracy: float, threshold: float = 0.5) -> bool:
        """Check if gate condition is satisfied. Returns: True if passed"""
        ...

    def compare_with_baseline(self, h_m1_accuracy: float, h_e1_accuracy: float,
                              random_accuracy: float = None) -> dict:
        """Compare performance with baselines. Returns: comparison dict"""
        ...


# From: h-m2/code/src/visualizer.py (ACTUAL CODE)
class Visualizer:
    def __init__(self, output_dir: str = "./outputs/figures"):
        """Initialize visualizer with output directory."""
        ...

    def plot_accuracy_comparison(self, h_e1_accuracy: float, h_m1_accuracy: float,
                                 h_m2_accuracy: float = None,
                                 random_baseline: float = 0.5,
                                 random_test_accuracy: float = None) -> None:
        """Generate mandatory accuracy comparison bar chart. Saves to accuracy_comparison.png"""
        ...

    def plot_within_family_comparison(self, family_results: dict,
                                      all_families_accuracy: float) -> None:
        """Generate within-family vs all-families bar chart. Saves to within_family_comparison.png"""
        ...

    def plot_feature_importance(self, coefficients: np.ndarray,
                                feature_names: list) -> None:
        """Plot feature importance from logistic regression. Saves to feature_importance.png"""
        ...

    def plot_confusion_matrix(self, cm: np.ndarray, class_names: list) -> None:
        """Plot confusion matrix. Saves to confusion_matrix.png"""
        ...

    def plot_feature_distributions(self, X_shallow: np.ndarray, X_deep: np.ndarray,
                                   feature_names: list) -> None:
        """Plot feature distributions for shallow vs deep. Saves to feature_distributions.png"""
        ...

    def plot_train_test_comparison(self, train_accuracy: float, test_accuracy: float) -> None:
        """Plot train vs test accuracy. Saves to train_test_comparison.png"""
        ...

    def plot_gate_metrics(self, baseline: float, actual: float,
                         target: float, passed: bool) -> None:
        """Plot gate condition metrics. Saves to gate_metrics.png"""
        ...


# From: h-m2/code/src/within_family_validator.py (ACTUAL CODE)
class WithinFamilyValidator:
    def __init__(self, random_state: int = 42):
        """Initialize validator with random seed."""
        ...

    def classify_model_family(self, model_name: str) -> str:
        """Detect family from model name. Returns: 'resnet' | 'vgg' | 'densenet' | 'other'"""
        ...

    def validate_within_family(self, X: np.ndarray, y: np.ndarray,
                               model_names: list, test_size: float = 0.2) -> dict:
        """Train per-family classifiers. X: [N, F], y: [N,] -> results: dict"""
        ...


# From: h-m2/code/src/random_init_test.py (ACTUAL CODE)
class RandomInitTest:
    def __init__(self, shallow_names: list, deep_names: list, random_state: int = 42):
        """Initialize random initialization test."""
        ...

    def run_random_test(self, test_size: float = 0.2) -> dict:
        """Run full random initialization test. Returns: {test_accuracy, train_accuracy, ...}"""
        ...
```

**Verified from:** `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_wsl_3/docs/youra_research/20260421_wsl/h-m2/code/` (actual implementation)

**Critical Note:** RandomInitTest imports ArchitecturalFeatureExtractor internally. For H-M3, we must create BatchNormFeatureExtractor and update RandomInitTest to use it.

---

## L-1: Batch Normalization Feature Extractor [Complexity: 16, Budget: 4]

**Applied:** PyTorch BatchNorm2d detection pattern

### API Signatures

```python
class BatchNormFeatureExtractor:
    """Extract 6 batch normalization features from pretrained CNNs."""
    
    def __init__(self):
        """Initialize extractor (stateless)."""
        ...
    
    def extract_features(self, model: nn.Module) -> np.ndarray:
        """Extract 6 BN features. model: nn.Module -> features: [6,]"""
        ...
    
    def collect_bn_layers(self, model: nn.Module) -> list:
        """Collect all BatchNorm2d layers. Returns: list of nn.BatchNorm2d"""
        ...
    
    def extract_gamma_stats(self, bn_layers: list) -> tuple:
        """Extract gamma (weight) statistics. Returns: (mean, std)"""
        ...
    
    def extract_beta_stats(self, bn_layers: list) -> tuple:
        """Extract beta (bias) statistics. Returns: (mean, std)"""
        ...
    
    def compute_depth_weighted_norm(self, bn_layers: list) -> float:
        """Compute depth-weighted BN norm. Returns: float"""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| bn_layers | list[nn.BatchNorm2d] | Variable length (0-200+) |
| gamma | [C,] | Per-layer BN weight (channel-wise) |
| beta | [C,] | Per-layer BN bias (channel-wise) |
| features | [6,] | Output: [count, γ_mean, γ_std, β_mean, β_std, weighted_norm] |

### Pseudo-code

```
extract_features(model):
    1. bn_layers = collect_bn_layers(model)  # Filter BatchNorm2d
    2. if len(bn_layers) == 0:
        return zeros(6)  # VGG, AlexNet, SqueezeNet
    
    3. gamma_mean, gamma_std = extract_gamma_stats(bn_layers)
    4. beta_mean, beta_std = extract_beta_stats(bn_layers)
    5. weighted_norm = compute_depth_weighted_norm(bn_layers)
    
    6. return [len(bn_layers), gamma_mean, gamma_std, beta_mean, beta_std, weighted_norm]

collect_bn_layers(model):
    1. layers = []
    2. for module in model.modules():
        if isinstance(module, nn.BatchNorm2d):
            layers.append(module)
    3. return layers

extract_gamma_stats(bn_layers):
    1. all_gamma = []
    2. for bn in bn_layers:
        all_gamma.extend(bn.weight.data.cpu().numpy())
    3. return (mean(all_gamma), std(all_gamma))

extract_beta_stats(bn_layers):
    1. all_beta = []
    2. for bn in bn_layers:
        all_beta.extend(bn.bias.data.cpu().numpy())
    3. return (mean(all_beta), std(all_beta))

compute_depth_weighted_norm(bn_layers):
    1. weighted_sum = 0
    2. for i, bn in enumerate(bn_layers):
        layer_norm = bn.weight.abs().mean().item()
        weighted_sum += (i + 1) * layer_norm
    3. return weighted_sum
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | BN Layer Detection | Iterate modules, filter BatchNorm2d, handle zero-BN models |
| L-1-2 | Gamma/Beta Extraction | Extract .weight and .bias from all BN layers, compute mean/std |
| L-1-3 | Depth-Weighted Norm | Weighted sum emphasizing later layers (tests accumulation hypothesis) |
| L-1-4 | Feature Assembly | Combine 6 features into (6,) numpy array, validate shape |

---

## L-2: Main Experiment Pipeline [Complexity: 10, Budget: 0]

**Note:** Reused from H-M2 with minor modifications (change feature extractor import). No budget allocated - simple orchestration.

### API Signatures

```python
def main() -> int:
    """Main experiment pipeline. Returns: exit_code (0=success)"""
    # [1/10] Load models
    # [2/10] Extract batch normalization features (6 features)
    # [3/10] Split data (80/20 stratified)
    # [4/10] Train all-families classifier
    # [5/10] Evaluate all-families accuracy
    # [6/10] Within-family validation (ResNet, DenseNet - exclude VGG)
    # [7/10] Random initialization test
    # [8/10] Mechanism verification
    # [9/10] Gate check and baseline comparison
    # [10/10] Generate visualizations
    ...
```

### Pseudo-code

```
main():
    1. loader = ModelLoader(shallow_names, deep_names)
    2. shallow_models, deep_models = loader.load_all_models()
    
    3. extractor = BatchNormFeatureExtractor()  # NEW (was ArchitecturalFeatureExtractor)
    4. X, y, names = extract_all_features(shallow_models, deep_models, extractor)
    
    5. X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)
    
    6. classifier = DepthClassifier(random_state=42)
    7. classifier.train(X_train, y_train)
    8. test_accuracy = classifier.score(X_test, y_test)
    
    9. validator = WithinFamilyValidator(random_state=42)
    10. family_results = validator.validate_within_family(X, y, names, test_size=0.2)
    
    11. random_tester = RandomInitTest(shallow_names, deep_names, random_state=42)
    12. random_results = random_tester.run_random_test(test_size=0.2)
    
    13. evaluator = Evaluator()
    14. gate_passed = evaluator.check_gate_condition(test_accuracy, threshold=0.5)
    
    15. visualizer = Visualizer(output_dir="./outputs/figures")
    16. visualizer.plot_accuracy_comparison(h_e1_accuracy=1.0, h_m1_accuracy=1.0, 
                                            h_m2_accuracy=1.0, h_m3_accuracy=test_accuracy,
                                            random_baseline=0.5, random_test_accuracy=random_results['test_accuracy'])
    17. visualizer.plot_within_family_comparison(family_results, test_accuracy)
    18. visualizer.plot_feature_importance(classifier.get_coefficients(), feature_names)
    19. visualizer.plot_confusion_matrix(cm, ['shallow', 'deep'])
    20. visualizer.plot_feature_distributions(X_shallow, X_deep, feature_names)
    21. visualizer.plot_train_test_comparison(train_accuracy, test_accuracy)
    22. visualizer.plot_gate_metrics(baseline=0.5, actual=test_accuracy, target=0.5, passed=gate_passed)
    
    23. save_metrics(metrics_dict, "./outputs/metrics.json")
    24. return 0 if gate_passed else 1
```

---

## L-3: Visualizer Extension for 5-Way Comparison [Complexity: 7, Budget: 0]

**Note:** Extend H-M2 Visualizer.plot_accuracy_comparison() to accept h_m3_accuracy parameter. Minimal modification.

### API Signatures

```python
# MODIFIED signature (add h_m3_accuracy parameter)
def plot_accuracy_comparison(self, h_e1_accuracy: float, h_m1_accuracy: float,
                             h_m2_accuracy: float = None, h_m3_accuracy: float = None,
                             random_baseline: float = 0.5,
                             random_test_accuracy: float = None) -> None:
    """Generate mandatory 5-way accuracy comparison bar chart. Saves to accuracy_comparison.png"""
    ...
```

### Pseudo-code

```
plot_accuracy_comparison(..., h_m3_accuracy):
    1. if h_m3_accuracy is not None and random_test_accuracy is not None:
        methods = ["H-E1\n(Weight Stats)", "H-M1\n(Gradient Flow)",
                  "H-M2\n(Architecture)", "H-M3\n(Batch Norm)", 
                  "Random\nBaseline", "Random Models\n(Untrained)"]
        accuracies = [h_e1_accuracy, h_m1_accuracy, h_m2_accuracy, h_m3_accuracy, 
                     random_baseline, random_test_accuracy]
        colors = ["green", "blue", "purple", "orange", "gray", "lightcoral"]
    
    2. elif h_m3_accuracy is not None:
        methods = ["H-E1\n(Weight Stats)", "H-M1\n(Gradient Flow)",
                  "H-M2\n(Architecture)", "H-M3\n(Batch Norm)", "Random\nBaseline"]
        accuracies = [h_e1_accuracy, h_m1_accuracy, h_m2_accuracy, h_m3_accuracy, random_baseline]
        colors = ["green", "blue", "purple", "orange", "gray"]
    
    3. bars = ax.bar(methods, accuracies, color=colors, alpha=0.7, edgecolor='black')
    4. Add accuracy labels on bars
    5. Set title: "H-M3: Batch Normalization Mechanism Validation"
    6. Add gate threshold line at 0.5
    7. Save to accuracy_comparison.png
```

---

## L-4: Random Initialization Test Update [Complexity: 5, Budget: 0]

**Note:** Update RandomInitTest to use BatchNormFeatureExtractor instead of ArchitecturalFeatureExtractor. Line 9 change only.

### API Signatures

```python
class RandomInitTest:
    """Test batch norm features on randomly initialized models."""
    
    def __init__(self, shallow_names: list, deep_names: list, random_state: int = 42):
        """Initialize random initialization test."""
        self.shallow_names = shallow_names
        self.deep_names = deep_names
        self.random_state = random_state
        self.loader = ModelLoader(shallow_names, deep_names)
        self.extractor = BatchNormFeatureExtractor()  # CHANGED from ArchitecturalFeatureExtractor
    
    # All other methods identical to H-M2 (extract_random_features, run_random_test)
```

### Pseudo-code

```
# Only change is line 9 in __init__:
__init__(...):
    ...
    self.extractor = BatchNormFeatureExtractor()  # NEW (was ArchitecturalFeatureExtractor)

# run_random_test() logic unchanged:
run_random_test(test_size):
    1. X, y = self.extract_random_features()  # Uses BatchNormFeatureExtractor
    2. Split, train, evaluate (same as H-M2)
    3. Interpretation: if test_accuracy < 0.55 → training-induced
                      else → architectural (BN layer count)
    4. return {test_accuracy, train_accuracy, interpretation, training_required}
```

---

## Configuration Design

**Applied:** Python dict configuration pattern

### config.py

```python
CONFIG = {
    "hypothesis_id": "h-m3",
    "experiment_name": "Batch Normalization Mechanism Validation",
    "base_hypothesis": "h-m2",
    
    "shallow_models": [
        "resnet18", "resnet34", "vgg11", "vgg13", "vgg16",
        "vgg19", "alexnet", "squeezenet1_0", "mobilenet_v2", "densenet121"
    ],
    
    "deep_models": [
        "resnet50", "resnet101", "resnet152", "densenet161", "densenet169",
        "densenet201", "wide_resnet50_2", "wide_resnet101_2",
        "resnext50_32x4d", "resnext101_32x8d"
    ],
    
    "test_size": 0.2,
    "random_state": 42,
    
    "feature_extractor": {
        "type": "BatchNormFeatureExtractor",
        "n_features": 6,
        "feature_names": [
            "bn_layer_count",
            "gamma_mean",
            "gamma_std",
            "beta_mean",
            "beta_std",
            "depth_weighted_bn_norm"
        ]
    },
    
    "classifier": {
        "C": 1.0,
        "solver": "lbfgs",
        "max_iter": 1000
    },
    
    "within_family_threshold": 0.65,
    "run_random_test": True,
    "gate_threshold": 0.50,
    
    "baseline_accuracies": {
        "h_e1_accuracy": 1.0,
        "h_m1_accuracy": 1.0,
        "h_m2_accuracy": 1.0,
        "baseline_accuracy": 0.50
    },
    
    "results_dir": "./outputs",
    "figures_dir": "./outputs/figures"
}
```

---

## Data Flow Summary

```
Step 1: Load 20 models
  └─> {shallow: 10, deep: 10} model objects

Step 2: Extract batch norm features (NEW)
  └─> (20, 6) feature array
      Feature 0: BN layer count (0 for VGG/AlexNet/SqueezeNet, 20-200 for others)
      Feature 1: Gamma mean (scale parameter mean)
      Feature 2: Gamma std (scale parameter distribution)
      Feature 3: Beta mean (shift parameter mean)
      Feature 4: Beta std (shift parameter distribution)
      Feature 5: Depth-weighted norm (cumulative effect test)

Step 3: Normalize features
  └─> StandardScaler (mean=0, std=1)

Step 4: Split data
  └─> Train: (16, 6), Test: (4, 6)

Step 5: Train classifier
  └─> LogisticRegression on 6 BN features

Step 6: Evaluate
  └─> Test accuracy, compare to 50% gate

Step 7: Within-family validation
  └─> ResNet, DenseNet (exclude VGG - no BN)

Step 8: Random initialization test
  └─> Extract BN features from random models
  └─> Expected: ~100% accuracy (BN layer count is architectural)

Step 9: Visualize
  └─> 7 PNG figures (5-way comparison: H-E1/M1/M2/M3/Random)

Step 10: Save metrics
  └─> metrics.json
```

---

## Feature Extraction Details

### Feature 1: BN Layer Count
- Direct count of `nn.BatchNorm2d` layers
- Range: 0 (VGG/AlexNet/SqueezeNet) to 200+ (DenseNet201)
- Expected to be primary discriminative feature (architectural signal)

### Features 2-5: Gamma/Beta Statistics
- Aggregate all BN layer weights and biases
- Compute mean and std across all layers
- Tests whether normalization statistics from training contribute to depth signal

### Feature 6: Depth-Weighted Norm
- `sum((i+1) * bn.weight.abs().mean() for i, bn in enumerate(bn_layers))`
- Emphasizes later BN layers (tests cumulative normalization hypothesis)
- Later layers weighted more heavily (1×, 2×, 3×, ...)

---

## Expected Results

### Baseline Hypothesis
- **Primary discriminator:** BN layer count (feature 1)
- **Test accuracy:** ~100% (if BN count correlates with depth)
- **Random test accuracy:** ~100% (BN count is architectural, not training-induced)
- **Within-family:** Lower accuracy (VGG excluded, ResNet/DenseNet depth range varies)

### Alternative Hypothesis
- **If gamma/beta statistics matter:** Random test accuracy < pretrained accuracy
- **If depth-weighted norm matters:** Feature importance shows feature 6 contributes

### Mechanism Conclusion
- **If random ≈ pretrained:** BN provides depth signal through layer count (architectural), not normalization effects
- **If random << pretrained:** Gamma/beta statistics from training contribute to depth signal

---

## Validation Checklist

- [ ] 6 BN features extracted from all 20 models
- [ ] VGG/AlexNet/SqueezeNet return zeros(6)
- [ ] Test accuracy > 50% (SHOULD_WORK gate)
- [ ] Within-family validation completed (ResNet, DenseNet only)
- [ ] Random initialization test completed
- [ ] 7 figures generated (5-way comparison mandatory)
- [ ] metrics.json saved
- [ ] Feature importance analysis identifies dominant features

---

*Logic Document v1.0 | Generated by Phase 3 Logic Agent | Hypothesis: H-M3 | Budget: 4/4 subtasks used*
