# Architecture Design: h-e1

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-05-12  
**Applied Patterns:** DL experiment minimal PoC structure

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** Green-field project - no existing code to analyze  
**Analyzed Path:** N/A  
**Findings:** New implementation from scratch

---

## Architecture Overview

**Design Philosophy:** Minimal PoC to validate drift detection classification accuracy.

**Core Components:**
- Data loading for 15 dataset version pairs
- Feature extraction using frozen pre-trained models
- SVAD drift classifier (KS + MMD on PCA-reduced features)
- Classification evaluation against ground truth labels

---

## Module Definitions

### DataLoader (`src/data_loader.py`)

**Dependencies:** None

```python
class DatasetPairLoader:
    def __init__(self, data_root: str): ...
    def load_pair(self, dataset_name: str) -> tuple[torch.Tensor, torch.Tensor]: ...
    def get_all_pairs(self) -> list[tuple[str, torch.Tensor, torch.Tensor, str]]: ...

def load_ground_truth_labels() -> dict[str, str]: ...
```

### FeatureExtractor (`src/feature_extractor.py`)

**Dependencies:** DataLoader

```python
class FeatureExtractor:
    def __init__(self, model_type: str, device: str): ...
    def extract_features(self, data: torch.Tensor, batch_size: int = 256) -> torch.Tensor: ...
    def get_feature_dim(self) -> int: ...

def load_pretrained_model(model_type: str) -> torch.nn.Module: ...
```

### SVADClassifier (`src/svad_classifier.py`)

**Dependencies:** FeatureExtractor

```python
class SVADDriftClassifier:
    def __init__(self, n_pca_components: int = 2): ...
    def fit_reference(self, ref_features: torch.Tensor) -> None: ...
    def classify_version_change(self, new_features: torch.Tensor) -> tuple[str, dict[str, float]]: ...
    def _compute_ks_score(self, features: torch.Tensor) -> float: ...
    def _compute_mmd_score(self, features: torch.Tensor) -> float: ...
```

### Evaluator (`src/evaluator.py`)

**Dependencies:** SVADClassifier

```python
class ClassificationEvaluator:
    def __init__(self): ...
    def add_prediction(self, true_label: str, pred_label: str, scores: dict) -> None: ...
    def compute_metrics(self) -> dict[str, float]: ...
    def get_confusion_matrix(self) -> np.ndarray: ...
    def check_gate_condition(self) -> tuple[bool, dict]: ...
```

### Visualizer (`src/visualizer.py`)

**Dependencies:** Evaluator

```python
def plot_gate_metrics(metrics: dict, save_path: str) -> None: ...
def plot_confusion_matrix(cm: np.ndarray, save_path: str) -> None: ...
def plot_drift_scores(results: list, save_path: str) -> None: ...
def plot_per_dataset_performance(results: list, save_path: str) -> None: ...
```

### MainExperiment (`run_experiment.py`)

**Dependencies:** All modules

```python
def main():
    # Load dataset pairs and ground truth
    # Extract features for v_old and v_new
    # Fit and classify with SVAD
    # Evaluate and visualize results
    # Save results to JSON
    pass

if __name__ == "__main__":
    main()
```

### Configuration (`config.py`)

**Dependencies:** None

```python
@dataclass
class ExperimentConfig:
    data_root: str
    output_dir: str
    device: str
    batch_size: int
    n_pca_components: int
    thresholds: dict[str, float]
    seed: int

def get_default_config() -> ExperimentConfig: ...
```

---

## File Structure

```
h-e1/
├── code/
│   ├── src/
│   │   ├── data_loader.py
│   │   ├── feature_extractor.py
│   │   ├── svad_classifier.py
│   │   ├── evaluator.py
│   │   └── visualizer.py
│   ├── config.py
│   ├── run_experiment.py
│   └── requirements.txt
├── data/
│   ├── ground_truth_labels.json
│   └── datasets/ (downloaded)
├── figures/
│   └── (generated plots)
├── 04_results.json
└── experiment.log
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup | Project structure, requirements, ground truth labels | 6 | 2+1+2+1 |
| A-2 | Data Loading | Implement DatasetPairLoader for 15 dataset pairs | 11 | 3+2+3+3 |
| A-3 | Feature Extraction | Implement FeatureExtractor with frozen models | 10 | 3+2+2+3 |
| A-4 | SVAD Classifier | Implement SVADDriftClassifier (PCA + KS + MMD) | 14 | 4+3+4+3 |
| A-5 | Evaluation | Implement ClassificationEvaluator and metrics | 9 | 2+2+3+2 |
| A-6 | Visualization | Generate gate metrics and additional figures | 8 | 2+2+2+2 |
| A-7 | Experiment Runner | Main experiment loop and results saving | 10 | 3+2+2+3 |

**Distribution:** VeryHigh(18-20): [], High(14-17): [A-4], Medium(9-13): [A-2, A-3, A-5, A-7], Low(4-8): [A-1, A-6]

**Total Complexity:** 68

---

## Task Breakdown Details

### A-1: Setup (Complexity: 6)
- Module_Size: 2 (config file + requirements + directory structure)
- Dependencies: 1 (no external module dependencies)
- Algorithm: 2 (ground truth label creation from literature)
- Integration: 1 (minimal integration)

**Subtasks:**
1. Create project directory structure
2. Write `requirements.txt` with dependencies
3. Create `ground_truth_labels.json` from PRD specifications
4. Setup basic logging configuration

### A-2: Data Loading (Complexity: 11)
- Module_Size: 3 (DataLoader class + utility functions)
- Dependencies: 2 (torchvision, HuggingFace datasets, external repos)
- Algorithm: 3 (dataset-specific preprocessing, special cases handling)
- Integration: 3 (multiple data sources, error handling)

**Subtasks:**
1. Implement `DatasetPairLoader.__init__` with data root
2. Implement `load_pair()` for vision datasets (CIFAR-10, MNIST, ImageNet)
3. Implement `load_pair()` for NLP datasets (GLUE, SQuAD)
4. Implement `get_all_pairs()` iterator for 15 dataset pairs
5. Add error handling for missing datasets
6. Load ground truth labels from JSON

### A-3: Feature Extraction (Complexity: 10)
- Module_Size: 3 (FeatureExtractor class + model loading)
- Dependencies: 2 (torchvision.models, transformers)
- Algorithm: 2 (forward pass only, no training)
- Integration: 3 (model-specific extraction, batch processing)

**Subtasks:**
1. Implement `load_pretrained_model()` for ResNet-50
2. Implement `load_pretrained_model()` for BERT-base
3. Implement `extract_features()` with batching
4. Remove classification heads from models
5. Add GPU memory management

### A-4: SVAD Classifier (Complexity: 14)
- Module_Size: 4 (SVADDriftClassifier + 3 statistical test methods)
- Dependencies: 3 (sklearn PCA, scipy KS test, torchdrift/custom MMD)
- Algorithm: 4 (PCA reduction, KS test, MMD test, threshold classification)
- Integration: 3 (PCA fitting, detector fitting, score aggregation)

**Subtasks:**
1. Implement `__init__` with PCA and detector initialization
2. Implement `fit_reference()` for v_old features
3. Implement `_compute_ks_score()` using scipy.stats.ks_2samp
4. Implement `_compute_mmd_score()` using torchdrift or custom
5. Implement `classify_version_change()` with threshold logic
6. Add Bonferroni correction for KS test
7. Add permutation testing for MMD p-values

### A-5: Evaluation (Complexity: 9)
- Module_Size: 2 (ClassificationEvaluator class)
- Dependencies: 2 (sklearn.metrics)
- Algorithm: 3 (precision, recall, F1, accuracy, confusion matrix)
- Integration: 2 (result aggregation, gate validation)

**Subtasks:**
1. Implement `add_prediction()` to store results
2. Implement `compute_metrics()` for precision/recall/F1/accuracy
3. Implement `get_confusion_matrix()` for 3×3 matrix
4. Implement `check_gate_condition()` for PoC pass validation

### A-6: Visualization (Complexity: 8)
- Module_Size: 2 (4 plot functions)
- Dependencies: 2 (matplotlib, seaborn)
- Algorithm: 2 (bar charts, heatmap, histograms)
- Integration: 2 (figure saving, layout management)

**Subtasks:**
1. Implement `plot_gate_metrics()` - bar chart with targets
2. Implement `plot_confusion_matrix()` - seaborn heatmap
3. Implement `plot_drift_scores()` - KS/MMD distributions
4. Implement `plot_per_dataset_performance()` - accuracy breakdown

### A-7: Experiment Runner (Complexity: 10)
- Module_Size: 3 (main loop + config + logging)
- Dependencies: 2 (all internal modules)
- Algorithm: 2 (loop over dataset pairs, aggregate results)
- Integration: 3 (module orchestration, error handling, results saving)

**Subtasks:**
1. Implement main experiment loop over 15 dataset pairs
2. Integrate data loading → feature extraction → classification
3. Aggregate metrics across all pairs
4. Save results to `04_results.json`
5. Generate all required visualizations
6. Add progress logging and error recovery

---

## Data Flow

```
Dataset Pairs (15) 
  → DataLoader.load_pair()
  → FeatureExtractor.extract_features() [v_old, v_new]
  → SVADClassifier.fit_reference(v_old)
  → SVADClassifier.classify_version_change(v_new) [label, scores]
  → Evaluator.add_prediction()
  → Evaluator.compute_metrics() [precision, recall, F1, accuracy]
  → Visualizer.plot_*() [gate_metrics.png, confusion_matrix.png, ...]
  → Save results to 04_results.json
```

---

## Key Design Decisions

**PCA Components:** Set to 2 (per TorchDrift best practices for KS test)  
**Thresholds:** Fixed cold-start values (7%/2%/0.5%) from hypothesis  
**Model Freezing:** All pre-trained models frozen (no training)  
**Error Handling:** Skip missing datasets with warning, continue execution  
**Reproducibility:** Fixed seed=42 for PCA and bootstrap sampling

---

## Validation Checkpoints

1. **After A-2:** Verify all 15 dataset pairs load correctly
2. **After A-3:** Check feature dimensions match expected (512-2048)
3. **After A-4:** Test drift scores computed without NaN/Inf
4. **After A-5:** Validate metrics match expected ranges
5. **After A-7:** Confirm gate condition check runs successfully

---

## Success Criteria

**PoC Pass Condition:**
- Code executes without errors on all 15 dataset pairs
- Precision ≥70% for MAJOR changes
- Recall ≥85% for MAJOR changes
- All required figures generated

**Gate Validation:**
- If precision ≥70% AND recall ≥85% → GATE SATISFIED
- Otherwise → GATE FAILED (requires threshold tuning or mechanism refinement)

---

**Document Status:** READY FOR PHASE 4 IMPLEMENTATION  
**Estimated Implementation Time:** 12-16 hours  
**Next Phase:** Phase 4 - Task-Driven Implementation
