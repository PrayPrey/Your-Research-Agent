# System Architecture: H-M3 Batch Normalization Mechanism Validation

**Hypothesis:** H-M3  
**Type:** Mechanism  
**Date:** 2026-04-21  
**Author:** Architecture Agent (Phase 3)

Applied: DL experiment modular architecture pattern (Archon KB)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Patterns analyzed from H-M2 implementation  
**Analyzed Path:** `/home/anonymous/YouRA_results_new_4_sonnet45_no_mcp/TEST_wsl_3/docs/youra_research/20260421_wsl/h-m2/code/`  
**Findings:** H-M2 uses src/ package structure with 7 modules (6 reused from H-M1 + 2 new). Feature extractor follows extraction → computation pattern. Main pipeline orchestrates 10 steps. Within-family validation module added for mechanism isolation.

---

## Architecture Overview

**System Purpose:** Validate batch normalization mechanism by extracting 6 BN-specific features from pretrained CNNs to test if normalization statistics contribute to depth classification.

**Design Philosophy:**
- Reuse H-M2 proven infrastructure (all modules except feature extractor)
- Replace feature extractor only (architectural constraints → batch normalization statistics)
- Reuse within-family validation for mechanism isolation

**High-Level Flow:**
```
Load Models → Extract BN Features → Train Classifier → 
Evaluate (All-families + Within-family) → Random Test → Visualize
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From H-M2 Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| ModelLoader | `from src.model_loader import ModelLoader` | `h-m2/code/src/model_loader.py` |
| DepthClassifier | `from src.classifier import DepthClassifier` | `h-m2/code/src/classifier.py` |
| Evaluator | `from src.evaluator import Evaluator` | `h-m2/code/src/evaluator.py` |
| Visualizer | `from src.visualizer import Visualizer` | `h-m2/code/src/visualizer.py` |
| RandomInitTest | `from src.random_init_test import RandomInitTest` | `h-m2/code/src/random_init_test.py` |
| WithinFamilyValidator | `from src.within_family_validator import WithinFamilyValidator` | `h-m2/code/src/within_family_validator.py` |

**Verified from:** H-M2 actual implementation (main.py lines 27-33, config.py)

**Note:** H-M3 reuses H-M2's complete src/ package structure. Feature extractor is the ONLY new module.

---

## Module Design

### BatchNormFeatureExtractor (`src/feature_extractor.py`)

**Dependencies:** torch, torch.nn, numpy

```python
class BatchNormFeatureExtractor:
    def extract_features(self, model: nn.Module) -> np.ndarray: ...
    def collect_bn_layers(self, model: nn.Module) -> list: ...
    def extract_gamma_stats(self, bn_layers: list) -> tuple: ...
    def extract_beta_stats(self, bn_layers: list) -> tuple: ...
    def compute_depth_weighted_norm(self, bn_layers: list) -> float: ...
```

**Output:** (6,) numpy array per model
- Features: [bn_count, gamma_mean, gamma_std, beta_mean, beta_std, depth_weighted_norm]
- Models without BN (VGG, AlexNet, SqueezeNet) return zeros(6)

---

### ModelLoader (`src/model_loader.py`)

**Reused from H-M2** (verified path: `h-m2/code/src/model_loader.py`)

```python
class ModelLoader:
    def __init__(self, shallow_names: list, deep_names: list): ...
    def load_all_models(self) -> Tuple[dict, dict]: ...
```

---

### DepthClassifier (`src/classifier.py`)

**Reused from H-M2** (verified path: `h-m2/code/src/classifier.py`)

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

**Reused from H-M2** (verified path: `h-m2/code/src/evaluator.py`)

```python
class Evaluator:
    def compute_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> dict: ...
    def check_gate_condition(self, accuracy: float, threshold: float) -> bool: ...
    def compare_with_baseline(self, h_m3_accuracy: float, h_e1_accuracy: float,
                              random_accuracy: float) -> dict: ...
```

---

### Visualizer (`src/visualizer.py`)

**Reused from H-M2** (verified path: `h-m2/code/src/visualizer.py`)

```python
class Visualizer:
    def __init__(self, output_dir: str): ...
    def plot_accuracy_comparison(self, h_e1_accuracy: float, h_m1_accuracy: float,
                                 h_m2_accuracy: float, h_m3_accuracy: float,
                                 random_baseline: float, random_test_accuracy: float): ...
    def plot_gate_metrics(self, baseline: float, actual: float, 
                         target: float, passed: bool): ...
    def plot_confusion_matrix(self, cm: np.ndarray, class_names: list): ...
    def plot_feature_distributions(self, X_shallow: np.ndarray, 
                                   X_deep: np.ndarray, feature_names: list): ...
    def plot_feature_importance(self, coefficients: np.ndarray, 
                               feature_names: list): ...
    def plot_within_family_comparison(self, family_results: dict, 
                                     all_families_accuracy: float): ...
    def plot_train_test_comparison(self, train_acc: float, test_acc: float): ...
```

**Note:** Extend `plot_accuracy_comparison()` to include H-M3 result (5-way comparison)

---

### WithinFamilyValidator (`src/within_family_validator.py`)

**Reused from H-M2** (verified path: `h-m2/code/src/within_family_validator.py`)

```python
class WithinFamilyValidator:
    def __init__(self, random_state: int = 42): ...
    def classify_model_family(self, model_name: str) -> str: ...
    def validate_within_family(self, X: np.ndarray, y: np.ndarray, 
                               model_names: list, test_size: float) -> dict: ...
```

**Note:** VGG family excluded from within-family validation (no batch norm)

---

### RandomInitTest (`src/random_init_test.py`)

**Reused from H-M2** (verified path: `h-m2/code/src/random_init_test.py`)

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
    # [2/10] Extract batch normalization features (6 features)
    # [3/10] Split data (80/20 stratified)
    # [4/10] Train all-families classifier
    # [5/10] Evaluate all-families accuracy
    # [6/10] Within-family validation (ResNet, DenseNet - exclude VGG)
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
    "hypothesis_id": "h-m3",
    "experiment_name": "Batch Normalization Mechanism Validation",
    "base_hypothesis": "h-m2",
    "shallow_models": [...],  # 10 models (reused from H-M2)
    "deep_models": [...],     # 10 models (reused from H-M2)
    "test_size": 0.2,
    "random_state": 42,
    "feature_extractor": {"type": "BatchNormFeatureExtractor", "n_features": 6},
    "classifier": {"C": 1.0, "solver": "lbfgs", "max_iter": 1000},
    "within_family_threshold": 0.65,
    "run_random_test": True,
    "gate_threshold": 0.50,
    "h_e1_accuracy": 1.0,
    "h_m1_accuracy": 1.0,
    "h_m2_accuracy": 1.0,
    "baseline_accuracy": 0.50,
    "results_dir": "./outputs",
    "figures_dir": "./outputs/figures",
}
```

---

## File Organization

```
h-m3/
├── code/
│   ├── main.py                          # Entry point (10-step pipeline)
│   ├── config.py                        # Configuration
│   ├── src/
│   │   ├── __init__.py
│   │   ├── feature_extractor.py         # NEW: BatchNormFeatureExtractor
│   │   ├── model_loader.py              # REUSED from H-M2
│   │   ├── classifier.py                # REUSED from H-M2
│   │   ├── evaluator.py                 # REUSED from H-M2
│   │   ├── visualizer.py                # REUSED + extended (add H-M3 to comparison)
│   │   ├── within_family_validator.py   # REUSED from H-M2
│   │   └── random_init_test.py          # REUSED from H-M2
│   └── outputs/
│       ├── metrics.json
│       ├── features.npy
│       ├── labels.npy
│       └── figures/
│           ├── accuracy_comparison.png           # MANDATORY (5-way: H-E1/M1/M2/M3/Random)
│           ├── gate_metrics.png
│           ├── confusion_matrix.png
│           ├── feature_distributions.png
│           ├── feature_importance.png
│           ├── within_family_comparison.png
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
| E-1 | Environment Setup | Install dependencies, verify H-M2 code access | 4 | 1+1+0+2 |
| E-2 | Batch Norm Feature Extractor | Implement 6-feature extraction (BN layer detection, gamma/beta stats) | 16 | 4+3+7+2 |
| E-3 | Main Experiment Pipeline | Orchestrate 10-step pipeline (load → extract → train → evaluate) | 10 | 3+2+2+3 |
| E-4 | Within-Family Validation | Validate ResNet/DenseNet families (exclude VGG) | 6 | 2+1+1+2 |
| E-5 | Random Initialization Test | Test random models (reuse H-M2 module) | 5 | 1+1+1+2 |
| E-6 | Visualization Extension | Add H-M3 to accuracy comparison plot (5-way) | 7 | 2+1+2+2 |
| E-7 | Integration Testing | Verify all modules work together | 6 | 2+1+1+2 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [E-2], Medium(9-13): [E-3], Low(4-8): [E-1,E-4,E-5,E-6,E-7]

**Total Complexity:** 54/140 (7 tasks × 20 max)

---

## Integration Points

### H-M2 Code Reuse

**Strategy:** Direct reuse of H-M2 src/ package (6 modules identical)

**Reused Modules (6):**
- `model_loader.py` - Load 20 torchvision models
- `classifier.py` - LogisticRegression wrapper
- `evaluator.py` - Metrics computation
- `visualizer.py` - Figure generation (extended for 5-way comparison)
- `within_family_validator.py` - Family-specific validation
- `random_init_test.py` - Random model validation

**New Modules (1):**
- `feature_extractor.py` - Batch normalization statistics extraction

### External Libraries

**PyTorch:**
- `torchvision.models.{model_name}(pretrained=True)` - Model loading
- `model.modules()` - Module iteration
- `isinstance(module, nn.BatchNorm2d)` - BN layer detection
- `bn_layer.weight.data` - Gamma parameter access
- `bn_layer.bias.data` - Beta parameter access

**Scikit-learn:**
- `LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000, random_state=42)`
- `StandardScaler()` - Feature normalization
- `train_test_split(test_size=0.2, stratify=y, random_state=42)`

---

## Technology Stack

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **DL Framework** | PyTorch | ≥2.0.0 | H-M2 compatibility |
| **Model Zoo** | torchvision | ≥0.15.0 | Pretrained CNNs |
| **Classifier** | scikit-learn | ≥1.3.0 | Binary classifier |
| **Numerics** | NumPy | ≥1.24.0 | Arrays |
| **Visualization** | Matplotlib | ≥3.7.0 | Figures |
| **Language** | Python | ≥3.9 | H-M2 compatibility |

---

## Data Flow

```
Step 1: Load 20 models (ModelLoader from H-M2)
  └─> {shallow: 10, deep: 10} model objects

Step 2: Extract batch norm features (NEW BatchNormFeatureExtractor)
  └─> (20, 6) feature array
      [bn_layer_count, gamma_mean, gamma_std, beta_mean, beta_std, 
       depth_weighted_bn_norm]
  └─> VGG/AlexNet/SqueezeNet → zeros(6) (no BN layers)

Step 3: Normalize features (StandardScaler from H-M2 classifier)
  └─> (20, 6) normalized array

Step 4: Split data (80/20 stratified, seed=42)
  └─> Train: (16, 6), Test: (4, 6)

Step 5: Train all-families classifier (DepthClassifier from H-M2)
  └─> Trained LogisticRegression

Step 6: Evaluate all-families (Evaluator from H-M2)
  └─> Test accuracy, confusion matrix

Step 7: Within-family validation (WithinFamilyValidator from H-M2)
  └─> {ResNet: acc, DenseNet: acc} (VGG excluded: no BN)

Step 8: Random initialization test (RandomInitTest from H-M2)
  └─> Random model accuracy

Step 9: Visualize (Visualizer from H-M2 + extended comparison)
  └─> 7 PNG figures (5-way comparison: H-E1/M1/M2/M3/Random)

Step 10: Save metrics
  └─> metrics.json
```

---

## Risk Analysis

| Risk | Mitigation |
|------|------------|
| VGG models deep but no BN layers | Return zeros(6), BN layer count becomes discriminative feature |
| Within-family validation excludes VGG | Focus on BN-enabled families (ResNet, DenseNet) |
| Random test likely shows 100% like H-M1/H-M2 | Expected: BN layer count is architectural, not training-induced |
| BN layer count confounded with depth | Expected: Primary discriminative feature (architectural signal) |

---

## Architecture Validation

**Checklist:**
- ✅ Reuses 6/7 modules from H-M2 (proven infrastructure)
- ✅ 7 Epic tasks (within 6-12 FULL tier range)
- ✅ Isolates H-M3-specific logic (batch norm feature extraction)
- ✅ Controlled experiment (identical pipeline except feature extractor)
- ✅ Clear integration with H-M2 codebase
- ✅ Modular design (easy feature extractor swap)
- ✅ External dependencies verified from H-M2 implementation

---

*Architecture Document v1.0 | Generated by Phase 3 Architecture Agent | Hypothesis: H-M3*
