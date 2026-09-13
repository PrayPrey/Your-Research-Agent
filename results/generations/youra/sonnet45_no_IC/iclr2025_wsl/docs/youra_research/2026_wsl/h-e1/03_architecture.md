# System Architecture: H-E1 Operation-Specific Weight Signal Existence

**Date:** 2026-07-13
**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Architecture Pattern Applied:** Minimal PoC Structure

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation from scratch
**Analyzed Path:** N/A
**Findings:** No existing codebase patterns to analyze. Fresh PoC implementation using standard PyTorch + sklearn pipeline.

---

## Architecture Overview

This is a **Proof of Concept (EXISTENCE)** hypothesis testing if operation-specific weight signals exist. The architecture follows minimal PoC principles:
- Single-file modules (no deep hierarchies)
- Standard library patterns (PyTorch, sklearn)
- Focus on binary classification pipeline over model zoo

**Pipeline Flow:**
1. Download model zoo (HuggingFace Hub)
2. Extract weight statistics (layer norms, spectral norms)
3. Train binary classifier (sklearn LogisticRegression)
4. Evaluate with ablation + statistical test

---

## Module Structure

### ModelZooCollector (`src/model_zoo.py`)

**Dependencies:** huggingface_hub, torch

```python
class ModelZooCollector:
    def __init__(self, output_dir: str, random_seed: int = 42): ...
    def collect_models(self, n_resnet: int = 50, n_vit: int = 50) -> dict: ...
    def download_model(self, model_id: str) -> dict: ...
    def save_metadata(self, metadata: list, filepath: str): ...
```

**Purpose:** Download 100 ImageNet-1K pre-trained models (50 ResNet-50, 50 ViT-Base) from HuggingFace Hub.

---

### FeatureExtractor (`src/feature_extractor.py`)

**Dependencies:** torch, numpy

```python
class FeatureExtractor:
    def __init__(self, include_spectral: bool = True): ...
    def extract_from_state_dict(self, state_dict: dict) -> np.ndarray: ...
    def extract_norms_only(self, state_dict: dict) -> np.ndarray: ...
    def extract_batch(self, model_list: list) -> tuple: ...
```

**Purpose:** Extract operation-agnostic statistics (L2 norms, spectral norms, mean, std) from model weights.

---

### BinaryClassifier (`src/classifier.py`)

**Dependencies:** sklearn, numpy

```python
class BinaryClassifier:
    def __init__(self, C: float = 1.0, max_iter: int = 1000, random_state: int = 42): ...
    def fit(self, X_train: np.ndarray, y_train: np.ndarray): ...
    def predict(self, X_test: np.ndarray) -> np.ndarray: ...
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict: ...
    def save_model(self, filepath: str): ...
```

**Purpose:** Train and evaluate logistic regression classifier for ResNet vs ViT binary classification.

---

### StatisticalTester (`src/statistical_test.py`)

**Dependencies:** sklearn, numpy

```python
class StatisticalTester:
    def __init__(self, n_permutations: int = 1000): ...
    def permutation_test(self, y_true: np.ndarray, y_pred: np.ndarray, actual_accuracy: float) -> dict: ...
    def compute_p_value(self, permuted_accuracies: list, actual_accuracy: float) -> float: ...
    def save_results(self, results: dict, filepath: str): ...
```

**Purpose:** Conduct permutation test to verify test accuracy significantly exceeds random baseline (50%).

---

### Visualizer (`src/visualizer.py`)

**Dependencies:** matplotlib, seaborn, numpy

```python
class Visualizer:
    def __init__(self, output_dir: str, dpi: int = 300): ...
    def plot_gate_comparison(self, target: float, baseline: float, proposed: float) -> str: ...
    def plot_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray, labels: list) -> str: ...
    def plot_feature_importance(self, coefficients: np.ndarray, feature_names: list, top_k: int = 10) -> str: ...
    def plot_permutation_distribution(self, permuted_acc: list, actual_acc: float) -> str: ...
```

**Purpose:** Generate required and recommended visualizations for experiment report.

---

### ExperimentRunner (`run_experiment.py`)

**Dependencies:** All above modules, json

```python
class ExperimentRunner:
    def __init__(self, config: dict): ...
    def setup_directories(self): ...
    def run_full_pipeline(self) -> dict: ...
    def train_test_split(self, metadata: list) -> tuple: ...
    def run_ablation_comparison(self) -> dict: ...
    def generate_report(self, results: dict): ...
```

**Purpose:** Orchestrate full experiment pipeline from data collection to final report.

---

## File Organization

```
docs/youra_research/h-e1/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── model_zoo.py           # FR-1: Model zoo collection
│   │   ├── feature_extractor.py   # FR-2: Weight statistics extraction
│   │   ├── classifier.py          # FR-4, FR-5: Binary classification
│   │   ├── statistical_test.py    # FR-6: Permutation test
│   │   └── visualizer.py          # FR-8: Figure generation
│   ├── run_experiment.py          # Main orchestration
│   ├── config.py                  # Configuration parameters
│   └── requirements.txt           # Dependencies
├── data/
│   ├── models_metadata.json       # Model zoo metadata
│   ├── weight_features.npz        # Extracted features
│   ├── train_indices.json         # Train split
│   └── test_indices.json          # Test split
├── models/
│   ├── classifier_norms_only.pkl  # Baseline classifier
│   └── classifier_full.pkl        # Full classifier
├── results/
│   ├── metrics.json               # Evaluation metrics
│   └── permutation_test.json      # Statistical test results
└── figures/
    ├── gate_comparison.png        # Required figure
    ├── confusion_matrix.png
    ├── feature_importance.png
    └── permutation_dist.png
```

---

## Configuration (`config.py`)

```python
CONFIG = {
    "random_seed": 42,
    "model_zoo": {
        "n_resnet": 50,
        "n_vit": 50,
        "architectures": ["resnet50", "vit_base_patch16_224"],
        "dataset_filter": "imagenet-1k"
    },
    "train_test_split": {
        "test_size": 0.3,
        "stratify": True
    },
    "classifier": {
        "C": 1.0,
        "max_iter": 1000,
        "solver": "lbfgs"
    },
    "statistical_test": {
        "n_permutations": 1000,
        "alpha": 0.05
    },
    "features": {
        "include_spectral": True,
        "top_k_spectral": 5
    },
    "visualization": {
        "dpi": 300,
        "style": "seaborn"
    },
    "success_criteria": {
        "target_accuracy": 0.80,
        "partial_threshold": 0.70,
        "ablation_improvement": 0.05
    }
}
```

---

## Data Flow

1. **Collection Phase**:
   - `ModelZooCollector` → downloads models → `models_metadata.json`

2. **Feature Extraction Phase**:
   - Load model state_dict → `FeatureExtractor` → `weight_features.npz`

3. **Training Phase**:
   - Stratified split → `BinaryClassifier` → `classifier_*.pkl`

4. **Evaluation Phase**:
   - Test set prediction → `StatisticalTester` → `metrics.json`, `permutation_test.json`

5. **Visualization Phase**:
   - Results → `Visualizer` → `figures/*.png`

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Model Zoo Collection | Download 100 models from HuggingFace Hub, save metadata | 8 | 2+2+2+2 |
| A-2 | Feature Extraction Pipeline | Extract L2 norms, spectral norms, mean, std from all models | 10 | 3+2+3+2 |
| A-3 | Binary Classification Training | Train norms-only and norms+spectral classifiers with ablation | 9 | 2+2+3+2 |
| A-4 | Statistical Testing & Evaluation | Permutation test, compute metrics, generate visualizations | 11 | 3+2+4+2 |

**Complexity Breakdown:** Module_Size + Dependencies + Algorithm + Integration (each 1-5)

**Distribution:**
- VeryHigh(18-20): []
- High(14-17): []
- Medium(9-13): [A-2, A-3, A-4]
- Low(4-8): [A-1]

**Total Complexity:** 38 points (4 tasks)

---

## Task Details

### A-1: Model Zoo Collection (Complexity: 8)
**Modules:** `model_zoo.py`
**Deliverables:**
- Implement HuggingFace Hub query with filters
- Download 50 ResNet-50, 50 ViT-Base models
- Extract ImageNet accuracy metadata
- Save to `models_metadata.json`

**Acceptance:**
- 100 models successfully downloaded
- Metadata includes model_id, architecture, accuracy
- Stratification by accuracy quantiles verified

---

### A-2: Feature Extraction Pipeline (Complexity: 10)
**Modules:** `feature_extractor.py`
**Deliverables:**
- Implement L2 norm computation per layer
- Implement top-5 spectral norm extraction (SVD)
- Implement mean/std statistics
- Batch processing for 100 models
- Save to `weight_features.npz`

**Acceptance:**
- All 100 models processed without error
- Feature dimensionality consistent across architectures
- Two feature sets: norms-only, norms+spectral

---

### A-3: Binary Classification Training (Complexity: 9)
**Modules:** `classifier.py`
**Deliverables:**
- Implement stratified train/test split (70/30)
- Train logistic regression (norms-only baseline)
- Train logistic regression (norms+spectral)
- Compute ablation improvement
- Save models to `models/`

**Acceptance:**
- Both classifiers trained successfully
- Test accuracy computed on held-out 30 models
- Ablation delta ≥ 5% (validation requirement)

---

### A-4: Statistical Testing & Evaluation (Complexity: 11)
**Modules:** `statistical_test.py`, `visualizer.py`, `run_experiment.py`
**Deliverables:**
- Implement permutation test (1000 iterations)
- Compute p-value vs random baseline (50%)
- Generate gate comparison figure (REQUIRED)
- Generate confusion matrix, feature importance, distribution plots
- Save all results to `results/` and `figures/`

**Acceptance:**
- p-value < 0.05 (statistical significance)
- All 5 figures generated and saved
- Final metrics match success criteria (≥80% accuracy)

---

## Dependencies

**External Libraries:**
- `torch>=2.0` - Model loading, tensor operations, SVD
- `numpy>=1.21` - Array operations
- `scikit-learn>=1.0` - Classification, metrics, preprocessing
- `huggingface_hub>=0.16` - Model discovery and download
- `matplotlib>=3.5` - Visualization
- `seaborn>=0.11` - Styled plots

**Data Dependencies:**
- HuggingFace Model Hub (internet connection required)
- ImageNet-1K pre-trained models

---

## Success Validation

**Primary Gate (MUST_WORK):**
- Test accuracy ≥ 80% → PASS (proceed to H-M-Integrated)
- 70% ≤ accuracy < 80% → PARTIAL (explore enhanced statistics)
- accuracy < 70% → FAIL (abandon modular encoders)

**Secondary Validations:**
- Ablation improvement ≥ 5%
- p-value < 0.05 (statistical significance)
- All 100 models processed successfully

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Model download failures | Medium | Retry logic (3 attempts), require ≥90 models |
| Feature dimensionality mismatch | High | Architecture-specific handling, padding if needed |
| Insufficient signal (<80%) | Critical | Partial success path explores enhanced statistics |

---

**Architecture Status:** COMPLETE
**Next Phase:** Phase 4 - Implementation (Epic task execution)
**Estimated Timeline:** 6-8 hours (PoC execution)
