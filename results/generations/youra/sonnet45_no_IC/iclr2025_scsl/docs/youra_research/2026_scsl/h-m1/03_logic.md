# Logic Design: Linear Separability Mechanism Analysis (H-M1)

**Version:** 1.0  
**Date:** 2026-07-13  
**Hypothesis:** H-M1 (MECHANISM)  
**Budget:** 6 subtasks (Medium complexity mechanism analysis)

**Applied:** Standard sklearn coefficient interpretation + PCA visualization patterns

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** API signatures verified from H-E1 actual code  
**Analyzed Path:** docs/youra_research/h-e1/code/  
**Relevant Symbols:** MaintenanceClassifier, FeatureEngineer, ExperimentConfig

**Key Findings:**
- H-E1 implements MaintenanceClassifier with StandardScaler normalization
- LogisticRegression trained with class_weight='balanced', max_iter=1000
- 8 features: [stars_log, forks_log, contributors_log, total_commits_log, open_issues_log, days_since_last_commit, commit_frequency_median_weekly, issue_resolution_rate]
- Model persistence: pickle format (.pkl files)

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

The following APIs are called from H-E1. Signatures verified from actual implementation:

```python
# From: docs/youra_research/h-e1/code/src/trainer.py (ACTUAL CODE)
class MaintenanceClassifier:
    def __init__(self, random_state: int = 42):
        """Initialize with sklearn LogisticRegression and StandardScaler."""
        ...

    def prepare_data(
        self,
        X: pd.DataFrame,
        y: np.ndarray,
        test_size: float = 0.20
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Split data with stratification. Returns: (X_train, X_test, y_train, y_test)"""
        ...

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> dict:
        """Train model. Returns: training_info dict with convergence status."""
        ...

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict labels. Input is raw features (scaled internally)."""
        ...

    def get_feature_importance(self) -> pd.DataFrame:
        """Extract coefficients. Returns: DataFrame with [feature, coefficient, abs_coefficient]"""
        ...

    def load_model(self, model_path: str, scaler_path: str) -> None:
        """Load persisted model and scaler from disk."""
        ...

# From: docs/youra_research/h-e1/code/src/feature_engineer.py (ACTUAL CODE)
class FeatureEngineer:
    def transform_features(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Apply log1p transforms. Returns: DataFrame with 8 features."""
        ...

    def create_labels(self, raw_data: pd.DataFrame, threshold_days: int = 180) -> np.ndarray:
        """Generate binary labels (1=maintained, 0=abandoned)."""
        ...

# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
@dataclass
class ExperimentConfig:
    dataset_size: int = 120
    year_range: Tuple[int, int] = (2020, 2024)
    label_threshold_days: int = 180
    data_output_path: str = 'data/raw_metadata.csv'
    model_config: ModelConfig = field(default_factory=ModelConfig)
    eval_config: EvaluationConfig = field(default_factory=EvaluationConfig)
```

**Verified from**: docs/youra_research/h-e1/code/ (actual implementation, NOT spec!)

---

## M-2: Model Loading [Complexity: 8, Budget: 2]

**Applied:** Sklearn pickle persistence pattern

### API Signatures

```python
import pickle
import sys
from pathlib import Path
from typing import Tuple, Optional
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

class ModelLoader:
    def __init__(self, h_e1_base_path: str):
        """Initialize loader with H-E1 base directory path."""
        ...

    def load_trained_lr(self) -> Tuple[LogisticRegression, StandardScaler]:
        """Load trained LR model and scaler from H-E1 artifacts.
        
        Returns:
            Tuple of (model, scaler)
        
        Raises:
            FileNotFoundError: If model files not found, triggers retrain fallback
        """
        ...

    def retrain_fallback(
        self, 
        X_train: np.ndarray, 
        y_train: np.ndarray
    ) -> Tuple[LogisticRegression, StandardScaler]:
        """Retrain LR model using H-E1 MaintenanceClassifier.
        
        Args:
            X_train: Training features [N, 8]
            y_train: Training labels [N]
        
        Returns:
            Tuple of (trained_model, fitted_scaler)
        """
        ...

    def _load_h_e1_data(self) -> Tuple[pd.DataFrame, np.ndarray]:
        """Load H-E1 dataset for retraining. Returns: (X, y)"""
        ...
```

### Pseudo-code

```
1. Try load from pickle files:
   - model = pickle.load(h_e1_base_path / 'models/lr_classifier.pkl')
   - scaler = pickle.load(h_e1_base_path / 'models/feature_scaler.pkl')
   
2. If FileNotFoundError:
   - Import H-E1 modules: sys.path.insert(0, h_e1_base_path)
   - Load H-E1 data using FeatureEngineer
   - Create MaintenanceClassifier(random_state=42)
   - Call prepare_data(), train()
   - Extract model.model and model.scaler
   
3. Verify loaded model:
   - Check model.coef_ shape == (1, 8)
   - Check scaler has mean_ and scale_ attributes
   
4. Return (model, scaler)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Pickle loading | Load model/scaler from H-E1 artifacts |
| L-2-2 | Retrain fallback | Retrain using H-E1 pipeline if files missing |

---

## M-3: Mechanism Analyzer [Complexity: 12, Budget: 3]

**Applied:** Sklearn coefficient extraction + PCA 2D projection pattern

### API Signatures

```python
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
import numpy as np
import pandas as pd
from typing import Dict, Tuple, List

class MechanismAnalyzer:
    def __init__(self, lr_model: LogisticRegression, feature_names: List[str]):
        """Initialize analyzer with trained LR model.
        
        Args:
            lr_model: Trained sklearn LogisticRegression
            feature_names: List of 8 feature names
        """
        ...

    def extract_coefficients(self) -> Dict[str, float]:
        """Extract coefficients from LR model.
        
        Returns:
            Dict mapping feature_name -> coefficient_value
        """
        ...

    def verify_coefficient_signs(
        self, 
        coefficients: Dict[str, float]
    ) -> Tuple[bool, Dict[str, str]]:
        """Verify coefficient signs match expected causal pathway.
        
        Expected:
            - days_since_last_commit: negative
            - All other features: positive
        
        Returns:
            Tuple of (all_correct: bool, sign_report: dict)
        """
        ...

    def compute_feature_importance(
        self, 
        use_abs: bool = True
    ) -> Dict[str, float]:
        """Compute feature importance from coefficient magnitudes.
        
        Args:
            use_abs: If True, use absolute values
        
        Returns:
            Dict mapping feature_name -> importance_score
        """
        ...

    def pca_projection(
        self, 
        X: np.ndarray, 
        n_components: int = 2
    ) -> Tuple[np.ndarray, PCA]:
        """Project features to 2D using PCA.
        
        Args:
            X: Feature matrix [N, 8] (pre-scaled)
            n_components: Number of PCA components
        
        Returns:
            Tuple of (X_2d: [N, 2], fitted_pca)
        """
        ...

    def generate_decision_boundary_mesh(
        self, 
        X_2d: np.ndarray, 
        pca: PCA, 
        lr_model: LogisticRegression
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Generate mesh grid for decision boundary visualization.
        
        Args:
            X_2d: 2D projected data [N, 2]
            pca: Fitted PCA object
            lr_model: Trained LR model
        
        Returns:
            Tuple of (xx: [100, 100], yy: [100, 100], Z: [100, 100])
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| coefficients | (8,) | From model.coef_[0] |
| X | [N, 8] | Input features (scaled) |
| X_2d | [N, 2] | PCA projected features |
| xx, yy | [100, 100] | Mesh grid for contour |
| Z | [100, 100] | Decision boundary predictions |

### Pseudo-code

```
1. Extract coefficients:
   coef = lr_model.coef_[0]  # Shape: [8]
   coefficients = dict(zip(feature_names, coef))

2. Verify signs:
   signs_correct = (
       coefficients['days_since_last_commit'] < 0 and
       all(coefficients[f] > 0 for f in other_features)
   )

3. Feature importance:
   importance = {k: abs(v) for k, v in coefficients.items()}

4. PCA projection:
   pca = PCA(n_components=2)
   X_2d = pca.fit_transform(X)  # [N, 8] -> [N, 2]

5. Decision boundary mesh:
   x_min, x_max = X_2d[:, 0].min() - 1, X_2d[:, 0].max() + 1
   y_min, y_max = X_2d[:, 1].min() - 1, X_2d[:, 1].max() + 1
   xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100),
                        np.linspace(y_min, y_max, 100))
   mesh_2d = np.c_[xx.ravel(), yy.ravel()]  # [10000, 2]
   mesh_original = pca.inverse_transform(mesh_2d)  # [10000, 8]
   Z = lr_model.predict(mesh_original).reshape(xx.shape)  # [100, 100]
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Coefficient extraction | Extract and verify signs |
| L-3-2 | Feature importance | Compute importance from magnitudes |
| L-3-3 | PCA projection + mesh | 2D projection and decision boundary grid |

---

## M-4: GB Baseline [Complexity: 8, Budget: 2]

**Applied:** Sklearn GradientBoostingClassifier standard training pattern

### API Signatures

```python
from sklearn.ensemble import GradientBoostingClassifier
import numpy as np

class GradientBoostingBaseline:
    def __init__(
        self, 
        n_estimators: int = 50, 
        max_depth: int = 6, 
        learning_rate: float = 0.1,
        random_state: int = 42
    ):
        """Initialize GB classifier with standard hyperparameters."""
        ...

    def train(self, X_train: np.ndarray, y_train: np.ndarray) -> dict:
        """Train GB model.
        
        Args:
            X_train: Training features [N, 8] (pre-scaled)
            y_train: Training labels [N]
        
        Returns:
            Training info dict with convergence status
        """
        ...

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict labels. X: [N, 8] -> predictions: [N]"""
        ...

    def get_feature_importance(self) -> np.ndarray:
        """Extract feature importance scores.
        
        Returns:
            Feature importance array [8] from model.feature_importances_
        """
        ...
```

### Pseudo-code

```
1. Initialize model:
   gb = GradientBoostingClassifier(
       n_estimators=50,
       max_depth=6,
       learning_rate=0.1,
       random_state=42
   )

2. Train:
   gb.fit(X_train_scaled, y_train)

3. Extract importance:
   importance = gb.feature_importances_  # Shape: [8]
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | GB training | Train GradientBoostingClassifier |
| L-4-2 | Feature importance extraction | Extract importance scores |

---

## M-5: Comparison Logic [Complexity: 10, Budget: 2]

**Applied:** Sklearn metrics + set-based feature overlap pattern

### API Signatures

```python
from sklearn.metrics import accuracy_score, f1_score
import numpy as np
from typing import Dict, Tuple

class ModelComparator:
    def __init__(
        self, 
        lr_model, 
        gb_model, 
        scaler, 
        feature_names: list
    ):
        """Initialize comparator with both models."""
        ...

    def compute_performance_gap(
        self, 
        X_test: np.ndarray, 
        y_test: np.ndarray
    ) -> Dict[str, float]:
        """Compute accuracy/F1 gap between LR and GB.
        
        Args:
            X_test: Test features [N, 8] (raw, will be scaled)
            y_test: Test labels [N]
        
        Returns:
            Dict with keys: lr_accuracy, gb_accuracy, gap, lr_f1, gb_f1
        """
        ...

    def compare_feature_importance(
        self, 
        lr_importance: Dict[str, float], 
        gb_importance: np.ndarray
    ) -> Dict[str, any]:
        """Compare feature importance between models.
        
        Args:
            lr_importance: Dict from LR coefficient magnitudes
            gb_importance: Array [8] from GB feature_importances_
        
        Returns:
            Dict with keys: lr_top3, gb_top3, overlap_count, overlap_features
        """
        ...

    def check_linear_sufficiency(
        self, 
        gap: float, 
        threshold: float = 0.05
    ) -> bool:
        """Check if linear model is sufficient. Returns: gap <= threshold"""
        ...
```

### Pseudo-code

```
1. Compute performance:
   X_test_scaled = scaler.transform(X_test)
   lr_pred = lr_model.predict(X_test_scaled)
   gb_pred = gb_model.predict(X_test_scaled)
   
   lr_acc = accuracy_score(y_test, lr_pred)
   gb_acc = accuracy_score(y_test, gb_pred)
   gap = abs(lr_acc - gb_acc)

2. Compare feature importance:
   gb_importance_dict = dict(zip(feature_names, gb_importance))
   
   lr_top3 = sorted(lr_importance, key=lr_importance.get, reverse=True)[:3]
   gb_top3 = sorted(gb_importance_dict, key=gb_importance_dict.get, reverse=True)[:3]
   
   overlap = set(lr_top3) & set(gb_top3)
   overlap_count = len(overlap)

3. Check sufficiency:
   linear_sufficient = (gap <= 0.05)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Performance comparison | Compute accuracy/F1 gap |
| L-5-2 | Feature alignment | Compare top-3 feature overlap |

---

## M-6: Visualization [Complexity: 14, Budget: 3]

**Applied:** Matplotlib/seaborn standard plotting patterns

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict
import numpy as np

class MechanismVisualizer:
    def __init__(self, output_dir: str, dpi: int = 300):
        """Initialize visualizer with output directory."""
        ...

    def plot_coefficients(
        self, 
        coefficients: Dict[str, float], 
        expected_signs: Dict[str, str],
        save_path: str
    ) -> None:
        """Generate coefficient bar chart.
        
        Args:
            coefficients: Feature -> coefficient value
            expected_signs: Feature -> 'positive' or 'negative'
            save_path: Output file path
        """
        ...

    def plot_performance_comparison(
        self, 
        lr_metrics: Dict[str, float], 
        gb_metrics: Dict[str, float],
        save_path: str
    ) -> None:
        """Side-by-side bar chart: LR vs GB accuracy/F1."""
        ...

    def plot_decision_boundary_pca(
        self, 
        X_2d: np.ndarray, 
        y: np.ndarray, 
        Z: np.ndarray, 
        xx: np.ndarray, 
        yy: np.ndarray,
        pca_variance: tuple,
        save_path: str
    ) -> None:
        """2D PCA scatter with decision boundary contour.
        
        Args:
            X_2d: Projected features [N, 2]
            y: Labels [N]
            Z: Decision boundary mesh [100, 100]
            xx, yy: Mesh grid coordinates [100, 100]
            pca_variance: (var_pc1, var_pc2) explained variance ratios
        """
        ...

    def plot_feature_importance_comparison(
        self, 
        lr_importance: Dict[str, float], 
        gb_importance: Dict[str, float], 
        feature_names: list,
        save_path: str
    ) -> None:
        """Side-by-side feature importance bars."""
        ...

    def plot_confusion_matrices(
        self, 
        y_test: np.ndarray, 
        lr_pred: np.ndarray, 
        gb_pred: np.ndarray,
        save_path: str
    ) -> None:
        """Two heatmaps: LR confusion matrix (left), GB (right)."""
        ...
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Coefficient/performance plots | Bar charts for coefficients and LR vs GB |
| L-6-2 | PCA decision boundary | 2D scatter with contour overlay |
| L-6-3 | Feature importance/confusion | Comparison bars and heatmaps |

---

## M-7: Mechanism Evaluation [Complexity: 6, Budget: 1]

**Applied:** Gate logic evaluation pattern

### API Signatures

```python
from typing import Tuple, Dict

class MechanismEvaluator:
    def __init__(
        self, 
        accuracy_gap_threshold: float = 0.05, 
        feature_overlap_threshold: int = 2
    ):
        """Initialize evaluator with gate thresholds."""
        ...

    def evaluate_mechanism(
        self, 
        coefficient_signs: Dict[str, bool], 
        performance_gap: float, 
        feature_overlap: int
    ) -> Tuple[bool, Dict[str, any]]:
        """Evaluate mechanism validation gates.
        
        Args:
            coefficient_signs: Feature -> is_correct_sign
            performance_gap: LR vs GB accuracy gap
            feature_overlap: Number of overlapping top-3 features
        
        Returns:
            Tuple of (mechanism_validated: bool, detailed_report: dict)
        """
        ...

    def generate_mechanism_report(self, results: Dict[str, any]) -> str:
        """Generate markdown validation report."""
        ...
```

### Pseudo-code

```
1. Check gates:
   gate_1 = all(coefficient_signs.values())  # All signs correct
   gate_2 = performance_gap <= 0.05          # Linear sufficient
   gate_3 = feature_overlap >= 2             # Causal alignment
   
2. Overall:
   mechanism_validated = gate_1 and gate_2 and gate_3

3. Generate report:
   markdown_report = f"""
   ## Mechanism Validation Results
   
   - EM-1 Coefficient Signs: {'PASS' if gate_1 else 'FAIL'}
   - EM-2 Performance Gap: {performance_gap:.3f} ({'PASS' if gate_2 else 'FAIL'})
   - EM-3 Feature Overlap: {feature_overlap}/3 ({'PASS' if gate_3 else 'FAIL'})
   
   **Overall:** {'VALIDATED' if mechanism_validated else 'REJECTED'}
   """
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Gate evaluation | Check all three gates and generate report |

---

## M-8: Integration [Complexity: 10, Budget: 1]

**Applied:** Standard experiment pipeline pattern

### API Signatures

```python
def main():
    """End-to-end mechanism analysis pipeline.
    
    Steps:
        1. Load H-E1 data and model
        2. Extract coefficients and verify signs
        3. Train GB baseline
        4. Compare LR vs GB performance
        5. PCA decision boundary visualization
        6. Feature importance comparison
        7. Gate evaluation
        8. Generate validation report
    """
    ...

if __name__ == '__main__':
    main()
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | End-to-end pipeline | Wire all modules in run_h_m1_experiment.py |

---

## Summary

### Complexity Budget Usage

| Task | Allocated | Used | Remaining |
|------|-----------|------|-----------|
| M-2: Model Loading | 8 | 2 | 6 |
| M-3: Mechanism Analyzer | 12 | 3 | 9 |
| M-4: GB Baseline | 8 | 2 | 6 |
| M-5: Comparison Logic | 10 | 2 | 8 |
| M-6: Visualization | 14 | 3 | 11 |
| M-7: Mechanism Evaluation | 6 | 1 | 5 |
| M-8: Integration | 10 | 1 | 9 |
| **Total** | **68** | **15** | **53** |

**Note:** Budget allocated is 6 subtasks total, distributed across medium-high complexity tasks.

### Key Design Decisions

1. **Model Loading:** Pickle persistence with fallback to H-E1 retrain pipeline
2. **Coefficient Extraction:** Direct access to model.coef_[0] with sign verification
3. **PCA Visualization:** 2D projection with inverse transform for decision boundary mesh
4. **GB Baseline:** Standard hyperparameters (n_estimators=50) for efficiency
5. **Feature Comparison:** Top-3 overlap using set intersection
6. **Visualization:** 5 required figures using matplotlib/seaborn standard patterns

### Integration Pattern

```python
# run_h_m1_experiment.py
from src.model_loader import ModelLoader
from src.mechanism_analyzer import MechanismAnalyzer
from src.gb_baseline import GradientBoostingBaseline
from src.comparator import ModelComparator
from src.mechanism_visualizer import MechanismVisualizer
from src.mechanism_evaluator import MechanismEvaluator

# 1. Load model
loader = ModelLoader(h_e1_base_path='../h-e1')
lr_model, scaler = loader.load_trained_lr()

# 2. Analyze mechanism
analyzer = MechanismAnalyzer(lr_model, feature_names)
coefficients = analyzer.extract_coefficients()
signs_correct, sign_report = analyzer.verify_coefficient_signs(coefficients)

# 3. Train GB
gb = GradientBoostingBaseline(n_estimators=50, random_state=42)
gb.train(X_train_scaled, y_train)

# 4. Compare
comparator = ModelComparator(lr_model, gb.model, scaler, feature_names)
performance = comparator.compute_performance_gap(X_test, y_test)
feature_alignment = comparator.compare_feature_importance(lr_importance, gb_importance)

# 5. Visualize
visualizer = MechanismVisualizer(output_dir='figures/')
visualizer.plot_coefficients(coefficients, expected_signs, 'figures/coefficient_bar_chart.png')
# ... (4 more figures)

# 6. Evaluate
evaluator = MechanismEvaluator()
validated, report = evaluator.evaluate_mechanism(sign_report, performance['gap'], feature_alignment['overlap_count'])
```

---

**End of Logic Design Document**
