# System Architecture: h-m1

**Hypothesis:** h-m1  
**Type:** MECHANISM  
**Gate:** MUST_WORK (accuracy ≥ 70%)  
**Date:** 2026-08-24  

Applied: Threshold classifier pattern, sklearn train/test split pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis  
**Status**: Analyzed h-e1 actual implementation  
**Analyzed Path**: `docs/youra_research/h-e1/code/`  
**Findings**: h-e1 outputs JSON results with per-sample entropies. Reuse data loading pattern, config structure, experiment runner pattern.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Data Source | File Location |
|--------|-------------|---------------|
| Entropy Data | `entropy_results.json` | `docs/youra_research/h-e1/code/results/entropy_results.json` |
| Sample Scores | `entropy_scores.csv` | `docs/youra_research/h-e1/code/results/entropy_scores.csv` |

**Verified from**: h-e1 actual implementation (not specs)

---

## Module Structure

### DataLoader (`src/data_loader.py`)

**Dependencies**: None (reads h-e1 outputs)

```python
class DataLoader:
    def load_h_e1_results(self, json_path: str) -> dict: ...
    def extract_arrays(self, results: dict) -> tuple[np.ndarray, np.ndarray]: ...
```

### ThresholdClassifier (`src/classifier.py`)

**Dependencies**: DataLoader

```python
class ThresholdClassifier:
    def __init__(self, threshold: float = 0.5): ...
    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> float: ...
    def predict(self, X: np.ndarray) -> np.ndarray: ...
```

### Evaluator (`src/evaluator.py`)

**Dependencies**: ThresholdClassifier

```python
class Evaluator:
    def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray) -> dict: ...
    def check_gate(self, accuracy: float, threshold: float = 0.70) -> bool: ...
```

### Visualizer (`src/visualizer.py`)

**Dependencies**: None

```python
def plot_threshold_curve(thresholds: list, accuracies: list, save_path: str): ...
def plot_confusion_matrix(cm: np.ndarray, save_path: str): ...
def plot_entropy_distribution(entity_vals: list, non_entity_vals: list, threshold: float, save_path: str): ...
```

### Config (`config.py`)

**Dependencies**: None

```python
CONFIG = {
    "data": {...},
    "classifier": {...},
    "evaluation": {...},
    "output": {...},
    "seed": 42
}
```

### ExperimentRunner (`src/run_experiment.py`)

**Dependencies**: DataLoader, ThresholdClassifier, Evaluator, Visualizer

```python
class ThresholdExperiment:
    def __init__(self): ...
    def load_data(self) -> tuple: ...
    def train_test_split(self, X, y) -> tuple: ...
    def grid_search_threshold(self, X_train, y_train) -> float: ...
    def run(self) -> dict: ...
```

---

## File Organization

```
h-m1/code/
├── config.py                 # Configuration
├── src/
│   ├── data_loader.py       # Load h-e1 results
│   ├── classifier.py        # Threshold classifier
│   ├── evaluator.py         # Metrics + gate check
│   ├── visualizer.py        # 3 plots
│   └── run_experiment.py    # Main runner
├── results/
│   └── classification_results.json
└── figures/
    ├── threshold_curve.png
    ├── confusion_matrix.png
    └── entropy_distribution.png
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M1-1 | Data Loading | Load h-e1 outputs, extract entropy arrays + labels | 6 | Module(2) + Deps(1) + Algo(1) + Integ(2) |
| M1-2 | Train/Test Split | Stratified 80/20 split with seed=42 | 4 | Module(1) + Deps(1) + Algo(1) + Integ(1) |
| M1-3 | Threshold Classifier | Grid search 101 thresholds, return best | 9 | Module(2) + Deps(1) + Algo(4) + Integ(2) |
| M1-4 | Test Evaluation | Apply threshold, compute accuracy/precision/recall/F1 | 7 | Module(2) + Deps(1) + Algo(2) + Integ(2) |
| M1-5 | Gate Check | Verify accuracy ≥ 0.70, return pass/fail | 4 | Module(1) + Deps(1) + Algo(1) + Integ(1) |
| M1-6 | Baseline Comparison | Random classifier, compare vs proposed | 5 | Module(1) + Deps(1) + Algo(2) + Integ(1) |
| M1-7 | Visualizations | 3 plots: threshold curve, confusion matrix, distributions | 10 | Module(3) + Deps(1) + Algo(3) + Integ(3) |
| M1-8 | Results Reporting | Save JSON results + gate status | 5 | Module(1) + Deps(1) + Algo(1) + Integ(2) |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M1-3, M1-7], Low(4-8): [M1-1, M1-2, M1-4, M1-5, M1-6, M1-8]

---

## Data Flow

1. Load h-e1 JSON → extract entity_entropies, non_entity_entropies arrays
2. Assign labels: 0=entity-error, 1=non-entity-error
3. Split 80/20 stratified (60 train, 13 test)
4. Grid search thresholds [0.00, 0.01, ..., 1.00] on train set
5. Select threshold with max train accuracy
6. Apply to test set → accuracy
7. Gate: accuracy ≥ 0.70 → PASS/FAIL
8. Save results + 3 figures

---

## Configuration Schema

```python
CONFIG = {
    "data": {
        "h_e1_results_path": "../h-e1/code/results/entropy_results.json",
        "train_ratio": 0.8,
        "stratify": True
    },
    "classifier": {
        "threshold_min": 0.0,
        "threshold_max": 1.0,
        "threshold_steps": 101
    },
    "evaluation": {
        "gate_threshold": 0.70,
        "metrics": ["accuracy", "precision", "recall", "f1"]
    },
    "output": {
        "results_file": "./results/classification_results.json",
        "figures_dir": "./figures/"
    },
    "seed": 42
}
```

---

## Key Interfaces

### DataLoader.extract_arrays
```python
def extract_arrays(self, results: dict) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns:
        X: (73,) entropy values
        y: (73,) labels (0=entity-error, 1=non-entity-error)
    """
```

### ThresholdClassifier.fit
```python
def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> float:
    """
    Grid search over thresholds.
    Returns: best_threshold
    """
```

### Evaluator.evaluate
```python
def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    """
    Returns: {
        "accuracy": float,
        "precision": float,
        "recall": float,
        "f1": float,
        "confusion_matrix": np.ndarray
    }
    """
```

---

## Integration Points

1. **h-e1 → h-m1**: Read `entropy_results.json` (73 samples: 50 entity + 23 non-entity)
2. **sklearn**: `train_test_split`, `accuracy_score`, `classification_report`, `confusion_matrix`
3. **matplotlib**: 3 visualization functions

---

## Success Criteria

1. Code runs without errors
2. Test accuracy ≥ 70% → GATE PASS
3. Proposed accuracy > random baseline (~50%)
4. 3 figures generated
5. JSON results saved

---

## Dependencies

**Python Libraries**:
- numpy
- scikit-learn
- matplotlib
- json (stdlib)

**External Data**:
- h-e1 validation outputs (VALIDATED prerequisite)

---

**Architecture Version:** 1.0  
**Status:** Ready for Phase 4 Implementation
