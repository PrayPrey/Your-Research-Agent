# Logic Design: H-E1 Operation-Specific Weight Signal Existence

**Date:** 2026-07-13
**Hypothesis ID:** H-E1
**Type:** EXISTENCE (PoC)
**Budget:** 4 subtasks allocated

---

## Codebase Analysis (Serena)

**Project Type:** green-field
**Status:** New implementation from scratch - designing new APIs
**Analyzed Path:** N/A
**Relevant Symbols:** None - new implementation

---

## A-1: Model Zoo Collection [Complexity: 8, Budget: 1]

**Applied:** Standard PyTorch + HuggingFace Hub

### API Signatures

```python
from typing import Dict, List
from pathlib import Path

class ModelZooCollector:
    def __init__(self, output_dir: str, random_seed: int = 42):
        """Initialize model zoo collector."""
        ...
    
    def collect_models(self, n_resnet: int = 50, n_vit: int = 50) -> Dict[str, List]:
        """
        Download models from HuggingFace Hub.
        Returns: {"models": [...metadata...], "success_count": int}
        """
        ...
    
    def download_model(self, model_id: str, retry: int = 3) -> Dict:
        """
        Download single model with retry logic.
        Returns: {"model_id": str, "architecture": str, "accuracy": float, "state_dict": OrderedDict}
        """
        ...
    
    def save_metadata(self, metadata: List[Dict], filepath: str) -> None:
        """Save collected metadata to JSON."""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | HuggingFace API integration | Query Hub with filters, download state_dict, extract metadata |

---

## A-2: Feature Extraction Pipeline [Complexity: 10, Budget: 1]

**Applied:** PyTorch SVD + NumPy array operations

### API Signatures

```python
import numpy as np
import torch
from typing import Tuple

class FeatureExtractor:
    def __init__(self, include_spectral: bool = True):
        """Initialize feature extractor."""
        ...
    
    def extract_from_state_dict(self, state_dict: Dict) -> np.ndarray:
        """
        Extract full feature vector from model state_dict.
        Returns: [F] where F = num_layers × (1 L2 + 5 spectral + 1 mean + 1 std)
        """
        ...
    
    def extract_norms_only(self, state_dict: Dict) -> np.ndarray:
        """
        Extract norms-only baseline features.
        Returns: [F_baseline] where F_baseline = num_layers × (1 L2 + 1 mean + 1 std)
        """
        ...
    
    def extract_batch(self, model_list: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Batch process multiple models.
        Returns: (X: [N, F], y: [N]) where N=100, y=0 for ResNet, y=1 for ViT
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| state_dict[key] | [varies] | Raw weight tensor (2D, 3D, 4D) |
| param_2d | [D, prod(rest)] | Reshaped for SVD |
| spectral_norms | [5] | Top-5 singular values |
| features | [F] | Concatenated statistics |
| X_batch | [N, F] | N models × F features |
| y_batch | [N] | Binary labels |

### Pseudo-code

```
1. For each parameter in state_dict:
   a. Compute L2 norm: torch.norm(param)
   b. If param is 2D+:
      - Reshape to [D, -1]
      - Compute SVD: torch.linalg.svdvals()
      - Take top-5 singular values
   c. Compute mean and std
   d. Append to features list
2. Return np.array(features)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | SVD-based spectral extraction | Reshape tensors, compute singular values, handle 1D parameters |

---

## A-3: Binary Classification Training [Complexity: 9, Budget: 1]

**Applied:** sklearn LogisticRegression standard pipeline

### API Signatures

```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

class BinaryClassifier:
    def __init__(self, C: float = 1.0, max_iter: int = 1000, random_state: int = 42):
        """Initialize binary classifier with scaler."""
        ...
    
    def fit(self, X_train: np.ndarray, y_train: np.ndarray) -> None:
        """
        Train logistic regression classifier.
        X_train: [N_train, F], y_train: [N_train]
        """
        ...
    
    def predict(self, X_test: np.ndarray) -> np.ndarray:
        """
        Predict labels for test set.
        X_test: [N_test, F] -> [N_test]
        """
        ...
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """
        Compute test accuracy and confusion matrix.
        Returns: {"accuracy": float, "confusion_matrix": [[TN, FP], [FN, TP]]}
        """
        ...
    
    def save_model(self, filepath: str) -> None:
        """Pickle classifier and scaler."""
        ...
```

### Pseudo-code

```
1. Initialize StandardScaler
2. Fit scaler on X_train, transform X_train
3. Train LogisticRegression(C=1.0, max_iter=1000)
4. For evaluation:
   a. Transform X_test with fitted scaler
   b. Predict labels
   c. Compute accuracy = (TP + TN) / N
   d. Compute confusion matrix
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Train/test split + ablation | Stratified split, train 2 classifiers, compute delta |

---

## A-4: Statistical Testing & Evaluation [Complexity: 11, Budget: 1]

**Applied:** sklearn permutation_test_score + matplotlib visualization

### API Signatures

```python
class StatisticalTester:
    def __init__(self, n_permutations: int = 1000):
        """Initialize statistical tester."""
        ...
    
    def permutation_test(
        self, 
        y_true: np.ndarray, 
        y_pred: np.ndarray, 
        actual_accuracy: float
    ) -> Dict[str, float]:
        """
        Permutation test vs random baseline.
        Returns: {"p_value": float, "permuted_mean": float, "permuted_std": float}
        """
        ...
    
    def compute_p_value(self, permuted_accuracies: List[float], actual_accuracy: float) -> float:
        """
        Compute p-value: fraction of permuted >= actual.
        Returns: p_value (0-1)
        """
        ...
    
    def save_results(self, results: Dict, filepath: str) -> None:
        """Save to JSON."""
        ...


class Visualizer:
    def __init__(self, output_dir: str, dpi: int = 300):
        """Initialize visualizer with output settings."""
        ...
    
    def plot_gate_comparison(
        self, 
        target: float, 
        baseline: float, 
        proposed: float
    ) -> str:
        """
        REQUIRED: Bar chart showing target vs baseline vs proposed accuracy.
        Returns: filepath to saved PNG
        """
        ...
    
    def plot_confusion_matrix(
        self, 
        y_true: np.ndarray, 
        y_pred: np.ndarray, 
        labels: List[str]
    ) -> str:
        """
        Confusion matrix heatmap.
        Returns: filepath
        """
        ...
    
    def plot_feature_importance(
        self, 
        coefficients: np.ndarray, 
        feature_names: List[str], 
        top_k: int = 10
    ) -> str:
        """
        Bar chart of top-K feature coefficients.
        Returns: filepath
        """
        ...
    
    def plot_permutation_distribution(
        self, 
        permuted_acc: List[float], 
        actual_acc: float
    ) -> str:
        """
        Histogram with actual accuracy marked.
        Returns: filepath
        """
        ...


class ExperimentRunner:
    def __init__(self, config: Dict):
        """Initialize experiment orchestrator."""
        ...
    
    def setup_directories(self) -> None:
        """Create data/, models/, results/, figures/ directories."""
        ...
    
    def run_full_pipeline(self) -> Dict:
        """
        Execute full pipeline.
        Returns: {"gate_status": str, "metrics": dict, "filepaths": dict}
        """
        ...
    
    def train_test_split(
        self, 
        metadata: List[Dict]
    ) -> Tuple[List[int], List[int]]:
        """
        Stratified split by architecture and accuracy quantile.
        Returns: (train_indices: [70], test_indices: [30])
        """
        ...
    
    def run_ablation_comparison(self) -> Dict[str, float]:
        """
        Compare norms-only vs norms+spectral.
        Returns: {"baseline_acc": float, "full_acc": float, "delta": float}
        """
        ...
    
    def generate_report(self, results: Dict) -> None:
        """Generate final validation report with gate decision."""
        ...
```

### Pseudo-code

```
Permutation Test:
1. actual_acc = accuracy_score(y_test, y_pred)
2. For i in 1..1000:
   a. Shuffle y_test with seed=i
   b. Compute perm_acc = accuracy_score(y_test_shuffled, y_pred)
   c. Append to permuted_accuracies
3. p_value = mean(permuted_accuracies >= actual_acc)

Gate Comparison Plot:
1. Create bar chart with 3 bars: [Target=0.80, Baseline, Proposed]
2. Color: green if >= target, yellow if >= 0.70, red otherwise
3. Add horizontal line at target threshold
4. Save as gate_comparison.png (300 DPI)

Full Pipeline:
1. ModelZooCollector.collect_models() → metadata
2. FeatureExtractor.extract_batch() → X, y
3. train_test_split() → train/test indices
4. BinaryClassifier(norms_only).fit().evaluate() → baseline_acc
5. BinaryClassifier(norms+spectral).fit().evaluate() → full_acc
6. StatisticalTester.permutation_test() → p_value
7. Visualizer.plot_gate_comparison() → gate figure
8. Determine gate: PASS if >= 0.80, PARTIAL if >= 0.70, else FAIL
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Pipeline orchestration | Integrate all modules, generate report with gate decision |

---

## Configuration Schema

```python
CONFIG = {
    "random_seed": 42,
    "model_zoo": {
        "n_resnet": 50,
        "n_vit": 50,
        "architectures": ["resnet50", "vit_base_patch16_224"],
        "dataset_filter": "imagenet-1k",
        "retry_attempts": 3
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

## Data Flow Summary

```
1. HuggingFace Hub → ModelZooCollector → models_metadata.json
2. state_dict × 100 → FeatureExtractor → weight_features.npz
3. weight_features.npz → train_test_split → train/test_indices.json
4. Train set → BinaryClassifier (2 variants) → classifier_*.pkl
5. Test set → evaluate() → metrics.json
6. Test predictions → StatisticalTester → permutation_test.json
7. All results → Visualizer → figures/*.png
8. All outputs → ExperimentRunner → validation report
```

---

## Self-Validation

- [x] No ASCII diagrams
- [x] KB pattern applied: Standard PyTorch + sklearn
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in comments
- [x] Subtask count: 4/4 used (within budget)
- [x] Total length: ~400 lines (within 600 limit)
- [x] Codebase Analysis section included
- [x] Green-field project confirmed
- [x] EXISTENCE-specific: Minimal pseudo-code, single forward path

---

**Status:** COMPLETE
**Next Phase:** Phase 4 - Implementation
**File Locations:**
- Architecture: `/workspace/TEST_wsl/docs/youra_research/h-e1/03_architecture.md`
- PRD: `/workspace/TEST_wsl/docs/youra_research/h-e1/03_prd.md`
- Logic: `/workspace/TEST_wsl/docs/youra_research/h-e1/03_logic.md`
