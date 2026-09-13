# System Architecture: H-M2 Architectural Constraints Mechanism Validation

**Hypothesis:** H-M2  
**Type:** Mechanism  
**Date:** 2026-04-21  
**Author:** Architecture Agent (Phase 3)

Applied: DL experiment modular architecture pattern (Archon KB)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns analyzed from H-M1 implementation  
**Analyzed Path:** `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_wsl_3/docs/youra_research/20260421_wsl/h-m1/code/`  
**Findings:** H-M1 uses src/ package structure with 6 modules. Feature extractor follows extraction → computation pattern. Main pipeline orchestrates 9 steps. All imports verified functional.

---

## Architecture Overview

**System Purpose:** Validate architectural constraint mechanism (residual/dense connections, bottleneck layers) by extracting 8 architectural features from pretrained CNNs.

**Design Philosophy:**
- Reuse H-M1 proven infrastructure (model loader, classifier, evaluator, visualizer)
- Replace feature extractor only (gradient-flow → architectural constraints)
- Add within-family validation module for mechanism isolation

**High-Level Flow:**
```
Load Models → Extract Architectural Features → Train Classifier → 
Evaluate (All-families + Within-family) → Random Test → Visualize
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From H-M1 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ModelLoader | `from src.model_loader import ModelLoader` | `h-m1/code/src/model_loader.py` |
| DepthClassifier | `from src.classifier import DepthClassifier` | `h-m1/code/src/classifier.py` |
| Evaluator | `from src.evaluator import Evaluator` | `h-m1/code/src/evaluator.py` |
| Visualizer | `from src.visualizer import Visualizer` | `h-m1/code/src/visualizer.py` |

**Verified from:** H-M1 actual implementation (main.py lines 16-20)

**Note:** H-M2 reuses H-M1's src/ package structure. Feature extractor and within-family validator are NEW.

---

## Module Design

### ArchitecturalFeatureExtractor (`src/feature_extractor.py`)

**Dependencies:** torch, numpy

```python
class ArchitecturalFeatureExtractor:
    def extract_features(self, model: nn.Module) -> np.ndarray: ...
    def count_residual_blocks(self, model: nn.Module) -> int: ...
    def count_dense_connections(self, model: nn.Module) -> int: ...
    def compute_bottleneck_ratio(self, model: nn.Module) -> float: ...
    def extract_residual_path_norms(self, model: nn.Module) -> float: ...
    def count_transition_layers(self, model: nn.Module) -> int: ...
    def detect_architecture_family(self, model: nn.Module) -> int: ...
```

**Output:** (8,) numpy array per model

---

### WithinFamilyValidator (`src/within_family_validator.py`)

**Dependencies:** sklearn, numpy, DepthClassifier

```python
class WithinFamilyValidator:
    def __init__(self, random_state: int = 42): ...
    def classify_model_family(self, model_name: str) -> str: ...
    def validate_within_family(self, X: np.ndarray, y: np.ndarray, 
                               model_names: list, test_size: float) -> dict: ...
```

**Output:** Dict with per-family accuracy and overall within-family metrics

---

### ModelLoader (`src/model_loader.py`)

**Reused from H-M1** (verified path: `h-m1/code/src/model_loader.py`)

```python
class ModelLoader:
    def __init__(self, shallow_names: list, deep_names: list): ...
    def load_all_models(self) -> Tuple[dict, dict]: ...
```

---

### DepthClassifier (`src/classifier.py`)

**Reused from H-M1** (verified path: `h-m1/code/src/classifier.py`)

```python
class DepthClassifier:
    def __init__(self, random_state: int = 42): ...
    def train(self, X: np.ndarray, y: np.ndarray): ...
    def predict(self, X: np.ndarray) -> np.ndarray: ...
    def score(self, X: np.ndarray, y: np.ndarray) -> float: ...
    def get_coefficients(self) -> np.ndarray: ...
```

---

### Evaluator (`src/evaluator.py`)

**Reused from H-M1** (verified path: `h-m1/code/src/evaluator.py`)

```python
class Evaluator:
    def compute_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> dict: ...
    def check_gate_condition(self, accuracy: float, threshold: float) -> bool: ...
    def compare_with_baseline(self, h_m2_accuracy: float, h_e1_accuracy: float,
                              random_accuracy: float) -> dict: ...
```

---

### Visualizer (`src/visualizer.py`)

**Reused from H-M1** (verified path: `h-m1/code/src/visualizer.py`)

```python
class Visualizer:
    def __init__(self, output_dir: str): ...
    def plot_accuracy_comparison(self, h_e1_accuracy: float, h_m2_accuracy: float,
                                 random_baseline: float, random_test_accuracy: float): ...
    def plot_gate_metrics(self, baseline: float, actual: float, 
                         target: float, passed: bool): ...
    def plot_confusion_matrix(self, cm: np.ndarray, class_names: list): ...
    def plot_feature_distributions(self, X_shallow: np.ndarray, 
                                   X_deep: np.ndarray, feature_names: list): ...
    def plot_feature_importance(self, coefficients: np.ndarray, 
                               feature_names: list): ...
```

**Note:** Add `plot_within_family_comparison()` method for H-M2

---

### RandomInitTest (`src/random_init_test.py`)

**Reused from H-M1** (verified path: `h-m1/code/src/random_init_test.py`)

```python
class RandomInitTest:
    def __init__(self, shallow_names: list, deep_names: list, random_state: int): ...
    def run_random_test(self, test_size: float) -> dict: ...
```

---

### Main Pipeline (`main.py`)

**Dependencies:** All above modules, config

```python
def main() -> int:
    # [1/10] Load models
    # [2/10] Extract architectural features (8 features)
    # [3/10] Split data (80/20 stratified)
    # [4/10] Train all-families classifier
    # [5/10] Evaluate all-families accuracy
    # [6/10] Within-family validation (ResNet, VGG, DenseNet)
    # [7/10] Random initialization test
    # [8/10] Mechanism verification
    # [9/10] Gate check and baseline comparison
    # [10/10] Generate visualizations
    return exit_code
```

---

### Configuration (`config.py`)

**Structure:**

```python
CONFIG = {
    "hypothesis_id": "h-m2",
    "experiment_name": "Architectural Constraints Mechanism Validation",
    "base_hypothesis": "h-m1",
    "shallow_models": [...],  # 10 models (reused from H-M1)
    "deep_models": [...],     # 10 models (reused from H-M1)
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

## File Organization

```
h-m2/
├── code/
│   ├── main.py                          # Entry point (10-step pipeline)
│   ├── config.py                        # Configuration
│   ├── src/
│   │   ├── __init__.py
│   │   ├── feature_extractor.py         # NEW: ArchitecturalFeatureExtractor
│   │   ├── within_family_validator.py   # NEW: WithinFamilyValidator
│   │   ├── model_loader.py              # REUSED from H-M1
│   │   ├── classifier.py                # REUSED from H-M1
│   │   ├── evaluator.py                 # REUSED from H-M1
│   │   ├── visualizer.py                # REUSED + extended (within-family plot)
│   │   └── random_init_test.py          # REUSED from H-M1
│   └── outputs/
│       ├── metrics.json
│       ├── features.npy
│       ├── labels.npy
│       └── figures/
│           ├── accuracy_comparison.png           # MANDATORY
│           ├── gate_metrics.png
│           ├── confusion_matrix.png
│           ├── feature_distributions.png
│           ├── feature_importance.png
│           ├── within_family_comparison.png      # NEW
│           └── train_test_comparison.png
├── 03_prd.md
├── 03_architecture.md (this file)
├── 03_logic.md
├── 03_config.md
└── 03_tasks.yaml
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| E-1 | Environment Setup | Install dependencies, verify H-M1 code access | 4 | 1+1+0+2 |
| E-2 | Architectural Feature Extractor | Implement 8-feature extraction (residual/dense/bottleneck) | 18 | 5+3+8+2 |
| E-3 | Within-Family Validator | Implement family-specific classification | 14 | 4+2+5+3 |
| E-4 | Main Experiment Pipeline | Orchestrate 10-step pipeline (load → extract → train → evaluate) | 12 | 3+3+2+4 |
| E-5 | Random Initialization Test | Test random models (reuse H-M1 module) | 6 | 1+1+2+2 |
| E-6 | Visualization Extension | Add within-family comparison plot | 8 | 2+1+3+2 |
| E-7 | Integration Testing | Verify all modules work together | 6 | 2+1+1+2 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [E-2,E-3], Medium(9-13): [E-4], Low(4-8): [E-1,E-5,E-6,E-7]

**Total Complexity:** 68/140 (7 tasks × 20 max)

---

## Integration Points

### H-M1 Code Reuse

**Strategy:** Direct import from H-M1 src/ package

**Reused Modules (5):**
- `model_loader.py` - Load 20 torchvision models
- `classifier.py` - LogisticRegression wrapper
- `evaluator.py` - Metrics computation
- `visualizer.py` - Figure generation (extended for within-family)
- `random_init_test.py` - Random model validation

**New Modules (2):**
- `feature_extractor.py` - Architectural constraint extraction
- `within_family_validator.py` - Family-specific validation

### External Libraries

**PyTorch:**
- `torchvision.models.{model_name}(pretrained=True)` - Model loading
- `model.named_modules()` - Architecture inspection
- `hasattr(module, 'downsample')` - Residual block detection
- `isinstance(module, nn.Conv2d)` - Conv layer filtering

**Scikit-learn:**
- `LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000, random_state=42)`
- `StandardScaler()` - Feature normalization
- `train_test_split(test_size=0.2, stratify=y, random_state=42)`

---

## Technology Stack

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **DL Framework** | PyTorch | ≥2.0.0 | H-M1 compatibility |
| **Model Zoo** | torchvision | ≥0.15.0 | Pretrained CNNs |
| **Classifier** | scikit-learn | ≥1.3.0 | Binary classifier |
| **Numerics** | NumPy | ≥1.24.0 | Arrays |
| **Visualization** | Matplotlib | ≥3.7.0 | Figures |
| **Language** | Python | ≥3.9 | H-M1 compatibility |

---

## Data Flow

```
Step 1: Load 20 models (ModelLoader from H-M1)
  └─> {shallow: 10, deep: 10} model objects

Step 2: Extract architectural features (NEW ArchitecturalFeatureExtractor)
  └─> (20, 8) feature array
      [residual_blocks, dense_connections, bottleneck_ratio, layer_count,
       skip_connection_present, residual_path_norm, transition_layers, 
       architecture_family]

Step 3: Normalize features (StandardScaler from H-M1 classifier)
  └─> (20, 8) normalized array

Step 4: Split data (80/20 stratified, seed=42)
  └─> Train: (16, 8), Test: (4, 8)

Step 5: Train all-families classifier (DepthClassifier from H-M1)
  └─> Trained LogisticRegression

Step 6: Evaluate all-families (Evaluator from H-M1)
  └─> Test accuracy, confusion matrix

Step 7: Within-family validation (NEW WithinFamilyValidator)
  └─> {ResNet: acc, VGG: acc, DenseNet: acc}

Step 8: Random initialization test (RandomInitTest from H-M1)
  └─> Random model accuracy

Step 9: Visualize (Visualizer from H-M1 + NEW within-family plot)
  └─> 7 PNG figures

Step 10: Save metrics
  └─> metrics.json
```

---

## Risk Analysis

| Risk | Mitigation |
|------|------------|
| VGG models deep but no skip connections | Expected: VGG classified by layer_count, validates depth vs architecture separation |
| Within-family insufficient samples | Report only families with ≥4 models (ResNet: 5, VGG: 4, DenseNet: 4) |
| Random test shows 100% like H-M1 | Expected: Architectural features are structural, confirms H-M1 finding |
| Bottleneck ratio confounded with depth | Use within-family validation to isolate depth signal |

---

## Architecture Validation

**Checklist:**
- ✅ Reuses 5/7 modules from H-M1 (proven infrastructure)
- ✅ 7 Epic tasks (within 6-12 FULL tier range)
- ✅ Isolates H-M2-specific logic (architectural features, within-family validation)
- ✅ Controlled experiment (identical pipeline except feature extractor)
- ✅ Clear integration with H-M1 codebase
- ✅ Modular design (easy feature extractor swap)
- ✅ External dependencies verified from H-M1 implementation

---

*Architecture Document v1.0 | Generated by Phase 3 Architecture Agent | Hypothesis: H-M2*
