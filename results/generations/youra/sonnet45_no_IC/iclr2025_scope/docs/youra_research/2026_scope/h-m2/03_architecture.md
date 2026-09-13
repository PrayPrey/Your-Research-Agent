# System Architecture: H-M2 Meta-Classifier Training Sufficiency

**Date:** 2026-07-13
**Hypothesis:** H-M2 (MECHANISM)
**Type:** Random Forest Meta-Learning with Cross-Validation
**Tier:** STANDARD (Sklearn-based classification pipeline)

Applied: sklearn RandomForestClassifier with small-data hyperparameters

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Patterns found from h-m1 code
**Analyzed Path:** `docs/youra_research/h-m1/code/`
**Findings:** h-m1 implements modular structure with src/ package. Feature computation in `src/feature_computer.py` (Tier1FeatureComputer class). Data loading in `src/data_loader.py` (BenchmarkDataLoader class). JSONL parsing from h-e1 output. Reuse feature_computer.py and data_loader.py directly via relative imports.

---

## System Overview

MECHANISM hypothesis testing if 50-60 training datasets suffice for Random Forest meta-classifier to learn generalizable feature-method relationships. Uses 63 benchmarks from h-e1 with leave-5-out cross-validation. Success gate: CV accuracy >35% AND generalization gap <20%.

**Core Pipeline:**
- Input: h-e1 benchmarks.json (63 datasets)
- Reuse: h-m1 feature_computer.py (Tier 1+2 features)
- Train: RandomForestClassifier (100 trees, max_depth=10)
- Evaluate: Leave-5-out CV (13 folds)
- Output: CV accuracy, generalization gap, gate result

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| BenchmarkDataLoader | `sys.path.append('../h-m1/code'); from src.data_loader import BenchmarkDataLoader` | `h-m1/code/src/data_loader.py` |
| Tier1FeatureComputer | `sys.path.append('../h-m1/code'); from src.feature_computer import Tier1FeatureComputer` | `h-m1/code/src/feature_computer.py` |

**Verified from:** `h-m1/code/src/` (actual implementation)

**Data Format (From h-e1 via h-m1):**
```python
# JSONL schema: h-e1/code/output/benchmarks_collection.jsonl
{
    "benchmark_id": str,
    "dataset_name": str,
    "domain": str,  # "vision", "nlp", "tabular", "graph", etc.
    "sample_size": int | None,
    "dimensionality": int | list | None,
    "num_classes": str | int | None,
    "method_rankings": {
        "MethodName": {
            "family": str,  # "Linear", "RNN", "Polynomial", "Augmentation"
            "ranking_percentile": float  # 0-100
        }
    }
}
```

---

## Module Structure

### 1. Data Loading Module (`code/src/data_loader.py`)

**Dependencies:** h-m1.src.data_loader, h-m1.src.feature_computer

```python
class DataPreprocessor:
    def __init__(self, h_e1_path: str): ...
    def load_and_prepare(self) -> Tuple[np.ndarray, np.ndarray, List[str]]: ...
    def _load_benchmarks(self) -> List[Dict]: ...
    def _compute_features(self, benchmarks: List[Dict]) -> pd.DataFrame: ...
    def _extract_target_labels(self, benchmarks: List[Dict]) -> np.ndarray: ...
    def _remove_sparse_features(self, features_df: pd.DataFrame, threshold: float = 0.7) -> pd.DataFrame: ...
    def _normalize_features(self, X: np.ndarray) -> np.ndarray: ...
```

---

### 2. Model Module (`code/src/model.py`)

**Dependencies:** sklearn.ensemble, sklearn.dummy

```python
class BaselineModel:
    def __init__(self, random_state: int = 42): ...
    def fit(self, X_train: np.ndarray, y_train: np.ndarray): ...
    def predict(self, X_test: np.ndarray) -> np.ndarray: ...
    def score(self, X_test: np.ndarray, y_test: np.ndarray) -> float: ...

class MetaClassifier:
    def __init__(self, n_estimators: int = 100, max_depth: int = 10, random_state: int = 42): ...
    def fit(self, X_train: np.ndarray, y_train: np.ndarray): ...
    def predict(self, X_test: np.ndarray) -> np.ndarray: ...
    def score(self, X_test: np.ndarray, y_test: np.ndarray) -> float: ...
    def get_feature_importances(self) -> np.ndarray: ...
```

---

### 3. Training Module (`code/src/train.py`)

**Dependencies:** sklearn.model_selection, src.model

```python
class CrossValidationTrainer:
    def __init__(self, model, baseline_model, n_folds: int = 13, random_state: int = 42): ...
    def run_cv(self, X: np.ndarray, y: np.ndarray) -> Dict: ...
    def _create_cv_splitter(self, n_samples: int) -> KFold: ...
    def _train_fold(self, X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray, y_test: np.ndarray) -> Dict: ...
```

---

### 4. Evaluation Module (`code/src/evaluate.py`)

**Dependencies:** sklearn.metrics, numpy

```python
class MetricsCalculator:
    def compute_cv_accuracy(self, cv_results: Dict) -> float: ...
    def compute_generalization_gap(self, cv_results: Dict) -> float: ...
    def compute_baseline_delta(self, cv_accuracy: float, baseline_accuracy: float) -> float: ...
    def compute_per_domain_accuracy(self, y_true: np.ndarray, y_pred: np.ndarray, domains: List[str]) -> Dict[str, float]: ...
    def generate_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray: ...

class GateEvaluator:
    def __init__(self, accuracy_threshold: float = 0.35, gap_threshold: float = 0.20): ...
    def evaluate(self, cv_accuracy: float, generalization_gap: float) -> str: ...
```

---

### 5. Visualization Module (`code/src/visualizer.py`)

**Dependencies:** matplotlib, seaborn, numpy

```python
def plot_gate_metrics_comparison(baseline_acc: float, cv_acc: float, target: float, threshold: float, output_path: str): ...
def plot_learning_curve(X: np.ndarray, y: np.ndarray, model, train_sizes: List[int], output_path: str): ...
def plot_confusion_matrix(cm: np.ndarray, class_names: List[str], output_path: str): ...
def plot_per_domain_accuracy(domain_accs: Dict[str, float], output_path: str): ...
def plot_feature_importance(importances: np.ndarray, feature_names: List[str], output_path: str): ...
def plot_generalization_gap_per_fold(cv_results: Dict, output_path: str): ...

def generate_all_figures(cv_results: Dict, metrics: Dict, model, output_dir: str):
    plot_gate_metrics_comparison(...)
    plot_learning_curve(...)
    plot_confusion_matrix(...)
    plot_per_domain_accuracy(...)
    plot_feature_importance(...)
    plot_generalization_gap_per_fold(...)
```

---

### 6. Orchestration Module (`code/run_experiment.py`)

**Dependencies:** All above modules, argparse

```python
class ExperimentOrchestrator:
    def __init__(self, config: Dict): ...
    def run(self) -> Tuple[Dict, str]: ...
    def _setup_output_directories(self): ...
    def _load_data(self) -> Tuple[np.ndarray, np.ndarray, List[str], List[str]]: ...
    def _train_models(self, X: np.ndarray, y: np.ndarray) -> Tuple[Dict, Dict]: ...
    def _evaluate_results(self, cv_results: Dict, baseline_results: Dict) -> Dict: ...
    def _determine_gate(self, metrics: Dict) -> str: ...
    def _generate_visualizations(self, cv_results: Dict, metrics: Dict): ...
    def _save_results(self, cv_results: Dict, metrics: Dict, gate_result: str): ...

def main():
    config = {
        'h_e1_data_path': '../h-e1/code/output/benchmarks_collection.jsonl',
        'h_m1_code_path': '../h-m1/code',
        'n_estimators': 100,
        'max_depth': 10,
        'min_samples_split': 5,
        'min_samples_leaf': 2,
        'n_folds': 13,
        'random_state': 42,
        'accuracy_threshold': 0.35,
        'gap_threshold': 0.20,
        'output_dir': './output',
        'figures_dir': '../figures'
    }
    orchestrator = ExperimentOrchestrator(config)
    cv_results, gate_result = orchestrator.run()
    print(f"Gate Result: {gate_result}")
```

---

## File Organization

```
h-m2/
├── code/
│   ├── src/
│   │   ├── __init__.py
│   │   ├── data_loader.py           (Preprocessing + feature reuse)
│   │   ├── model.py                 (Baseline + Random Forest)
│   │   ├── train.py                 (CV trainer)
│   │   ├── evaluate.py              (Metrics + gate evaluation)
│   │   └── visualizer.py            (6 figures)
│   ├── run_experiment.py            (Main orchestrator)
│   └── requirements.txt             (sklearn, pandas, matplotlib, seaborn)
├── output/
│   ├── cv_results.json              (Fold-wise results)
│   ├── metrics.json                 (Aggregated metrics)
│   ├── gate_result.txt              (PASS/PARTIAL/FAIL)
│   └── feature_importances.csv      (RF importances)
└── figures/
    ├── gate_metrics.png             (MANDATORY)
    ├── learning_curve.png
    ├── confusion_matrix.png
    ├── per_domain_accuracy.png
    ├── feature_importance.png
    └── generalization_gap.png
```

---

## Data Flow

1. **Setup Phase:**
   - Add h-m1/code to sys.path
   - Import BenchmarkDataLoader, Tier1FeatureComputer

2. **Load Phase:**
   - Read h-e1 JSONL: `../h-e1/code/output/benchmarks_collection.jsonl`
   - Parse 63 benchmark records
   - Extract method_rankings nested dict

3. **Feature Phase:**
   - Compute Tier 1 features via h-m1 code
   - Remove features with >70% NaN
   - Z-score normalize remaining features
   - Output: X (63 × F), F = 4-10 features

4. **Target Phase:**
   - Extract top-1 method family per benchmark
   - Encode as categorical: Linear/Polynomial/RNN/Augmentation
   - Output: y (63,)

5. **Training Phase:**
   - Initialize 13-fold leave-5-out CV
   - For each fold:
     - Train baseline (DummyClassifier) on 58 samples
     - Train Random Forest on 58 samples
     - Predict on 5 held-out samples
     - Record train/test accuracy

6. **Evaluation Phase:**
   - Aggregate CV results: mean accuracy, std
   - Compute generalization gap: mean(train_acc - test_acc)
   - Compare to baseline
   - Check gate: CV_acc > 0.35 AND gap < 0.20

7. **Visualization Phase:**
   - Generate 6 figures
   - Save to `../figures/`

8. **Reporting Phase:**
   - Save results to output/
   - Write gate decision

---

## Configuration (STANDARD Tier)

**Hardcoded in `run_experiment.py`:**

```python
CONFIG = {
    # Data sources
    'h_e1_data_path': '../h-e1/code/output/benchmarks_collection.jsonl',
    'h_m1_code_path': '../h-m1/code',
    
    # Random Forest hyperparameters
    'n_estimators': 100,
    'max_depth': 10,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'criterion': 'gini',
    'max_features': 'sqrt',
    
    # Cross-validation
    'n_folds': 13,                    # 63 ÷ 5 = 12.6 → 13 folds
    'random_state': 42,
    
    # Gate thresholds
    'accuracy_threshold': 0.35,
    'gap_threshold': 0.20,
    'partial_accuracy_threshold': 0.30,
    'partial_gap_threshold': 0.25,
    
    # Feature processing
    'nan_threshold': 0.7,             # Remove features with >70% NaN
    'normalize_method': 'zscore',
    
    # Output paths
    'output_dir': './output',
    'figures_dir': '../figures',
    
    # Visualization
    'figure_dpi': 300,
    'figure_format': 'png'
}
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M2-1 | Setup Project Structure | Create folders, requirements.txt, validate h-m1/h-e1 paths, sys.path configuration | 5 | Size(1) + Deps(2) + Algo(0) + Integ(2) |
| M2-2 | Implement Data Preprocessor | DataPreprocessor with h-m1 feature reuse, NaN filtering, normalization | 8 | Size(2) + Deps(2) + Algo(2) + Integ(2) |
| M2-3 | Implement Baseline Model | DummyClassifier wrapper with consistent interface | 4 | Size(1) + Deps(1) + Algo(0) + Integ(2) |
| M2-4 | Implement Meta-Classifier | RandomForestClassifier with small-data hyperparameters | 6 | Size(2) + Deps(1) + Algo(1) + Integ(2) |
| M2-5 | Implement CV Trainer | CrossValidationTrainer with leave-5-out, fold-wise train/test recording | 9 | Size(2) + Deps(2) + Algo(3) + Integ(2) |
| M2-6 | Implement Metrics Calculator | CV accuracy, generalization gap, per-domain accuracy, confusion matrix | 7 | Size(2) + Deps(1) + Algo(2) + Integ(2) |
| M2-7 | Implement Gate Evaluator | Threshold-based gate logic (PASS/PARTIAL/FAIL) | 4 | Size(1) + Deps(0) + Algo(1) + Integ(2) |
| M2-8 | Implement Visualizations | 6 figures: gate metrics, learning curve, confusion matrix, domain accuracy, feature importance, gap per fold | 11 | Size(3) + Deps(2) + Algo(3) + Integ(3) |
| M2-9 | Orchestration and Integration | ExperimentOrchestrator connecting all modules, result saving, validation reporting | 10 | Size(2) + Deps(3) + Algo(2) + Integ(3) |

**Total Complexity:** 64
**Distribution:** VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M2-5, M2-8, M2-9], Low(4-8): [M2-1, M2-2, M2-3, M2-4, M2-6, M2-7]

---

## Dependencies

**External Libraries:**
```
scikit-learn>=1.0.0
pandas>=1.5.0
numpy>=1.21.0
matplotlib>=3.6.0
seaborn>=0.12.0
scipy>=1.7.0
```

**Code Dependencies:**
- h-m1 Feature Computer: `../h-m1/code/src/feature_computer.py` (MUST exist)
- h-m1 Data Loader: `../h-m1/code/src/data_loader.py` (MUST exist)

**Data Sources:**
- h-e1 Benchmarks: `../h-e1/code/output/benchmarks_collection.jsonl` (MUST exist)

**Internal Dependencies:**
- Verification State: Check h-m1 status = COMPLETED before running

---

## Success Criteria

**Quantitative Metrics:**
1. CV Accuracy > 0.35 (PASS threshold)
2. Generalization Gap < 0.20 (overfitting control)
3. Baseline Delta > 0.05 (learning beyond chance)

**Gate Logic:**
```python
if cv_accuracy > 0.35 and generalization_gap < 0.20:
    gate_result = "PASS"
elif cv_accuracy >= 0.30 and generalization_gap < 0.25:
    gate_result = "PARTIAL"
else:
    gate_result = "FAIL"
```

**Output:**
- `cv_results.json` - Fold-wise train/test accuracies
- `metrics.json` - Aggregated metrics
- `gate_result.txt` - Final decision
- 6 figure files in `../figures/`

**Gate Decision:**
- PASS: 50-60 datasets sufficient → proceed to h-m3
- PARTIAL: Limited learning → investigate feature quality
- FAIL: Insufficient data → hypothesis rejected

---

## Implementation Notes

**Recommended Development Order:**
1. M2-1: Setup (folders, requirements.txt, path validation)
2. M2-2: Data preprocessor (test h-m1 integration first)
3. M2-3: Baseline model (simple, test CV integration)
4. M2-4: Meta-classifier (test training on full dataset)
5. M2-5: CV trainer (core mechanism test)
6. M2-6: Metrics calculator (verify gate logic)
7. M2-7: Gate evaluator (threshold testing)
8. M2-8: Visualizations (after all data available)
9. M2-9: Final orchestration (integration test)

**Key Design Constraints:**
- STANDARD tier: Hardcoded config in run_experiment.py
- Runtime: <5 minutes total (sklearn is fast on 63 samples)
- Deterministic: Fixed random_state=42 for reproducibility
- Reuse h-m1 code: No duplication of feature computation

**Phase 4 Execution:**
```bash
cd h-m2/code
pip install -r requirements.txt
python run_experiment.py
```

**Expected Output:**
```
✓ Loaded 63 benchmarks from h-e1
✓ Computed Tier 1 features: 63 benchmarks, 7 features after NaN filtering
✓ Extracted target labels: 4 classes (Linear, Polynomial, RNN, Augmentation)
✓ Training baseline: 13 folds...
  Baseline CV Accuracy: 28.3% ± 5.2%
✓ Training meta-classifier: 13 folds...
  Fold 1: Train=82.8%, Test=40.0%
  Fold 2: Train=84.5%, Test=40.0%
  ...
  CV Accuracy: 38.5% ± 6.1%
  Generalization Gap: 42.3%
✓ Gate Evaluation:
  CV Accuracy: 38.5% > 35.0% ✓
  Generalization Gap: 42.3% > 20.0% ✗
  Result: FAIL (severe overfitting)
✓ Figures saved to ../figures/
```

---

**Document Status:** Ready for Implementation (Phase 4)
**Next Step:** Phase 4 Coder Agent - Implement meta-classifier training pipeline
