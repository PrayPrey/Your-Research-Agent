# Logic Specification: h-m1

**Hypothesis:** h-m1  
**Type:** MECHANISM  
**Gate:** MUST_WORK (accuracy ≥ 70%)  
**Date:** 2026-08-24  
**Budget:** 1 subtask  

---

## Codebase Analysis (Serena)

**Project Type**: green-field  
**Status**: New implementation - consumes h-e1 validated outputs  
**Analyzed Path**: N/A (new module)  
**Relevant Symbols**: None - baseline classifier implementation  

**Note**: h-m1 is a standalone classifier. h-e1 outputs already generated and validated (73 samples confirmed in `entropy_results.json`).

---

## External Dependencies (h-e1)

### Data Source (Verified from Actual Code)

```python
# From: docs/youra_research/h-e1/code/src/run_experiment.py
# Output format (lines 148-157):
results_out = {
    "p_value": float,
    "mean_entity": float,
    "mean_non_entity": float,
    "cohens_d": float,
    "pass": bool,
    "entity_entropies": list[float],      # 50 samples
    "non_entity_entropies": list[float],  # 23 samples (some skipped)
    "n_entity": int,
    "n_non_entity": int,
    "n_skipped": int
}
```

**File Location**: `../h-e1/code/results/entropy_results.json`  
**Verified**: 73 total samples (50 entity + 23 non-entity)

---

## M1-3: Threshold Classifier [Complexity: 9, Budget: 1]

**Applied**: sklearn classification pattern, numpy threshold search

### API Signatures

```python
# src/classifier.py
import numpy as np
from typing import Tuple

class ThresholdClassifier:
    """Binary classifier using single threshold on entropy values."""
    
    def __init__(self, threshold: float = 0.5):
        """Initialize with default threshold."""
        self.threshold = threshold
        self.best_threshold: float = 0.5
        self.train_accuracy: float = 0.0
    
    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> float:
        """
        Grid search optimal threshold.
        X_train: (N,) entropy values
        y_train: (N,) labels (0=entity-error, 1=non-entity-error)
        Returns: best_threshold
        """
        ...
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        Apply threshold. X: (N,) -> (N,) binary predictions.
        Rule: entropy < threshold -> 0 (entity-error)
        """
        ...
    
    def get_threshold(self) -> float:
        """Return fitted threshold."""
        return self.best_threshold


# src/data_loader.py
import json
import numpy as np
from typing import Tuple

class DataLoader:
    """Load h-e1 entropy results."""
    
    def load_h_e1_results(self, json_path: str) -> dict:
        """Load JSON from h-e1. Returns raw dict."""
        ...
    
    def extract_arrays(self, results: dict) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract (X, y) arrays.
        Returns:
            X: (73,) entropy values
            y: (73,) labels (0=entity, 1=non-entity)
        """
        ...


# src/evaluator.py
import numpy as np
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from typing import Dict

class Evaluator:
    """Compute metrics and gate check."""
    
    def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Compute classification metrics.
        Returns: {
            "accuracy": float,
            "precision": float,
            "recall": float,
            "f1": float,
            "confusion_matrix": [[int, int], [int, int]]
        }
        """
        ...
    
    def check_gate(self, accuracy: float, threshold: float = 0.70) -> bool:
        """Return True if accuracy >= threshold."""
        ...


# src/visualizer.py
import numpy as np
import matplotlib.pyplot as plt
from typing import List

def plot_threshold_curve(thresholds: List[float], accuracies: List[float], 
                        best_threshold: float, save_path: str) -> None:
    """Plot 101-point accuracy vs threshold with best marker."""
    ...

def plot_confusion_matrix(cm: np.ndarray, save_path: str) -> None:
    """2x2 heatmap with counts."""
    ...

def plot_entropy_distribution(entity_vals: List[float], non_entity_vals: List[float],
                              threshold: float, save_path: str) -> None:
    """Overlaid histograms + vertical threshold line."""
    ...


# src/run_experiment.py
from sklearn.model_selection import train_test_split
import numpy as np
from typing import Dict

class ThresholdExperiment:
    """Main experiment runner."""
    
    def __init__(self, config: dict):
        self.config = config
        self.loader = DataLoader()
        self.classifier = ThresholdClassifier()
        self.evaluator = Evaluator()
    
    def load_data(self) -> Tuple[np.ndarray, np.ndarray]:
        """Load h-e1 results. Returns (X, y) of shape (73,)."""
        ...
    
    def train_test_split(self, X: np.ndarray, y: np.ndarray) -> Tuple:
        """
        80/20 stratified split.
        Returns: X_train (60,), X_test (13,), y_train, y_test
        """
        ...
    
    def grid_search_threshold(self, X_train: np.ndarray, y_train: np.ndarray) -> Tuple:
        """
        Search 101 thresholds [0.00, 0.01, ..., 1.00].
        Returns: (best_threshold, threshold_list, accuracy_list)
        """
        ...
    
    def run(self) -> Dict:
        """
        Execute full pipeline.
        Returns: {
            "best_threshold": float,
            "train_accuracy": float,
            "test_accuracy": float,
            "test_metrics": dict,
            "gate_pass": bool
        }
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| entity_entropies | (50,) | From h-e1 JSON |
| non_entity_entropies | (23,) | From h-e1 JSON |
| X | (73,) | Concatenated entropy values |
| y | (73,) | Binary labels (0/1) |
| X_train | (60,) | 80% split |
| X_test | (13,) | 20% split |
| thresholds | (101,) | [0.00, 0.01, ..., 1.00] |
| y_pred | (13,) | Test predictions |
| confusion_matrix | (2, 2) | [[TN, FP], [FN, TP]] |

### Pseudo-code

```
# Data Loading
1. Load entropy_results.json
2. X = entity_entropies + non_entity_entropies  # (73,)
3. y = [0]*50 + [1]*23  # Labels

# Train/Test Split
4. X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

# Grid Search (on train set)
5. For threshold in [0.00, 0.01, ..., 1.00]:
       y_pred = (X_train < threshold).astype(int)  # Flip: entropy < t -> label=0
       acc = accuracy(y_train, 1 - y_pred)  # Invert prediction for correct classification
6. best_threshold = argmax(accuracies)

# Test Evaluation
7. y_pred_test = (X_test >= best_threshold).astype(int)  # Apply optimal threshold
8. test_acc = accuracy(y_test, y_pred_test)
9. gate_pass = (test_acc >= 0.70)

# Visualization
10. Plot threshold curve (101 points)
11. Plot confusion matrix (2x2)
12. Plot entropy distributions + threshold line
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Threshold Search | Grid search 101 thresholds, select max train accuracy |

---

## Configuration API

```python
# config.py
CONFIG = {
    "data": {
        "h_e1_results_path": "../h-e1/code/results/entropy_results.json",
        "train_ratio": 0.8,
        "test_size": 0.2,
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

## Output Schema

```python
# results/classification_results.json
{
    "best_threshold": float,
    "train_accuracy": float,
    "test_accuracy": float,
    "test_metrics": {
        "accuracy": float,
        "precision": float,
        "recall": float,
        "f1": float
    },
    "confusion_matrix": [[int, int], [int, int]],
    "baseline_accuracy": float,  # Random ~0.5
    "gate_pass": bool,
    "n_train": 60,
    "n_test": 13
}
```

---

## Validation Checklist

- [x] No ASCII diagrams
- [x] No KB search logs (Applied: sklearn patterns)
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in comments
- [x] Subtask count = 1 (within budget)
- [x] Total length < 600 lines
- [x] Codebase Analysis section included
- [x] Green-field project noted
- [x] External Dependencies from h-e1 verified

---

**Logic Version:** 1.0  
**Status:** Ready for Phase 4 Implementation
