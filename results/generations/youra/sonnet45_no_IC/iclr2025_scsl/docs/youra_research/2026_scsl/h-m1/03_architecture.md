# Architecture: Linear Separability Mechanism Analysis (H-M1)

**Version:** 1.0  
**Date:** 2026-07-13  
**Hypothesis:** H-M1 (MECHANISM)  
**Type:** Mechanism Analysis - Interpret H-E1 Results

**Applied:** Standard mechanism analysis pattern (coefficient interpretation + baseline comparison)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Extending H-E1 validated baseline  
**Analyzed Path:** `docs/youra_research/h-e1/code/`  
**Findings:** H-E1 implemented sklearn LogisticRegression with MaintenanceClassifier wrapper, StandardScaler normalization, 8-feature dataset. Module structure: src/trainer.py (model), src/evaluator.py (metrics), src/visualizer.py (plots). Import pattern: `from src.trainer import MaintenanceClassifier`. No saved model found - will retrain from same pipeline.

---

## Design Principles

**MECHANISM Scope:**
- Reuse H-E1 trained model (or retrain if not saved)
- Add mechanism analyzer for coefficient interpretation
- Add Gradient Boosting baseline for comparison
- PCA visualization for decision boundary
- Standard sklearn comparison patterns

**Success Criteria:**
- Coefficient signs correct (negative staleness, positive activity)
- LR vs GB gap ≤ 5%
- Feature importance alignment ≥ 2 top features

---

## Module Structure

### 1. Model Loading (`src/model_loader.py`)

**Dependencies:** sklearn.linear_model, pickle, pathlib

```python
class ModelLoader:
    def __init__(self, h_e1_path: str): ...
    def load_trained_lr(self) -> LogisticRegression: ...
    def retrain_fallback(self, X_train: np.ndarray, y_train: np.ndarray) -> LogisticRegression: ...
    def load_scaler(self) -> StandardScaler: ...
```

### 2. Mechanism Analyzer (`src/mechanism_analyzer.py`)

**Dependencies:** sklearn.decomposition, numpy, pandas

```python
class MechanismAnalyzer:
    def __init__(self, lr_model: LogisticRegression, feature_names: list): ...
    def extract_coefficients(self) -> dict: ...
    def verify_coefficient_signs(self, coefficients: dict) -> tuple[bool, dict]: ...
    def compute_feature_importance(self, use_abs: bool = True) -> dict: ...
    def pca_projection(self, X: np.ndarray, n_components: int = 2) -> tuple: ...
    def generate_decision_boundary_mesh(self, X_2d: np.ndarray, pca: PCA) -> tuple: ...
```

### 3. Gradient Boosting Baseline (`src/gb_baseline.py`)

**Dependencies:** sklearn.ensemble

```python
class GradientBoostingBaseline:
    def __init__(self, random_state: int = 42): ...
    def train(self, X_train: np.ndarray, y_train: np.ndarray): ...
    def predict(self, X: np.ndarray) -> np.ndarray: ...
    def get_feature_importance(self) -> np.ndarray: ...
```

### 4. Comparator (`src/comparator.py`)

**Dependencies:** sklearn.metrics

```python
class ModelComparator:
    def __init__(self, lr_model, gb_model): ...
    def compute_performance_gap(self, X_test: np.ndarray, y_test: np.ndarray) -> dict: ...
    def compare_feature_importance(self, lr_importance: dict, gb_importance: np.ndarray) -> dict: ...
    def check_linear_sufficiency(self, gap: float, threshold: float = 0.05) -> bool: ...
```

### 5. Mechanism Visualizer (`src/mechanism_visualizer.py`)

**Dependencies:** matplotlib, seaborn

```python
class MechanismVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_coefficients(self, coefficients: dict, expected_signs: dict): ...
    def plot_performance_comparison(self, lr_metrics: dict, gb_metrics: dict): ...
    def plot_decision_boundary_pca(self, X_2d: np.ndarray, y: np.ndarray, Z: np.ndarray, xx: np.ndarray, yy: np.ndarray): ...
    def plot_feature_importance_comparison(self, lr_importance: dict, gb_importance: dict, feature_names: list): ...
    def plot_confusion_matrices(self, y_test: np.ndarray, lr_pred: np.ndarray, gb_pred: np.ndarray): ...
```

### 6. Mechanism Evaluator (`src/mechanism_evaluator.py`)

**Dependencies:** None (pure logic)

```python
class MechanismEvaluator:
    def __init__(self, accuracy_gap_threshold: float = 0.05, feature_overlap_threshold: int = 2): ...
    def evaluate_mechanism(self, coefficient_signs: dict, performance_gap: float, feature_overlap: int) -> tuple[bool, dict]: ...
    def generate_mechanism_report(self, results: dict) -> str: ...
```

### 7. Experiment Runner (`run_h_m1_experiment.py`)

**Dependencies:** All above modules + H-E1 modules

```python
def main():
    """End-to-end mechanism analysis pipeline."""
    # 1. Load H-E1 data and model
    # 2. Extract coefficients and verify signs
    # 3. Train Gradient Boosting baseline
    # 4. Compare LR vs GB performance
    # 5. PCA decision boundary visualization
    # 6. Feature importance comparison
    # 7. Gate evaluation
    # 8. Generate validation report
    pass
```

### 8. Configuration (`config.py`)

**Dependencies:** dataclasses

```python
@dataclass
class MechanismConfig:
    h_e1_base_path: str
    h_e1_data_path: str
    h_e1_model_path: str
    h_e1_scaler_path: str
    output_figures_path: str
    gb_n_estimators: int = 50
    gb_max_depth: int = 6
    gb_learning_rate: float = 0.1
    pca_n_components: int = 2
    random_state: int = 42
    accuracy_gap_threshold: float = 0.05
    feature_overlap_threshold: int = 2
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| MaintenanceClassifier | `from src.trainer import MaintenanceClassifier` | `h-e1/code/src/trainer.py` |
| FeatureEngineer | `from src.feature_engineer import FeatureEngineer` | `h-e1/code/src/feature_engineer.py` |
| GateEvaluator | `from src.evaluator import GateEvaluator` | `h-e1/code/src/evaluator.py` |
| ExperimentConfig | `from config import ExperimentConfig` | `h-e1/code/config.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation)

**Usage Pattern:**
```python
# Load H-E1 configuration and data
sys.path.insert(0, '../h-e1/code')
from config import ExperimentConfig
from src.trainer import MaintenanceClassifier

# Retrain if model not saved
h_e1_config = ExperimentConfig()
classifier = MaintenanceClassifier(random_state=42)
# Use same preprocessing pipeline
```

---

## File Organization

```
h-m1/
├── code/
│   ├── src/
│   │   ├── model_loader.py              # Load H-E1 model or retrain
│   │   ├── mechanism_analyzer.py        # Coefficient extraction + PCA
│   │   ├── gb_baseline.py               # Gradient Boosting training
│   │   ├── comparator.py                # LR vs GB comparison
│   │   ├── mechanism_visualizer.py      # 5 required figures
│   │   └── mechanism_evaluator.py       # Gate checking
│   ├── config.py                        # Mechanism config + H-E1 paths
│   ├── run_h_m1_experiment.py           # Main pipeline
│   └── requirements.txt                 # Dependencies (reuse H-E1 + add PCA)
├── figures/                             # Generated visualizations
│   ├── coefficient_bar_chart.png
│   ├── performance_comparison.png
│   ├── decision_boundary_pca.png
│   ├── feature_importance_comparison.png
│   └── confusion_matrix_comparison.png
└── 04_validation.md                     # Mechanism validation report
```

---

## Data Flow

```
H-E1 Data + Model → model_loader.py → Trained LR model
                  ↓
mechanism_analyzer.py → Coefficients + PCA projections
                  ↓
gb_baseline.py → Trained GB model
                  ↓
comparator.py → Performance gap + Feature importance alignment
                  ↓
mechanism_visualizer.py → 5 figures
                  ↓
mechanism_evaluator.py → Gate decision (signs correct AND gap ≤5%)
                  ↓
04_validation.md
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Setup Project | Create directory structure, config with H-E1 paths, requirements | 4 | 1+1+1+1 |
| M-2 | Model Loading | Implement ModelLoader with H-E1 model loading and retrain fallback | 8 | 2+2+2+2 |
| M-3 | Mechanism Analyzer | Implement coefficient extraction, sign verification, PCA projection | 12 | 3+3+4+2 |
| M-4 | GB Baseline | Implement GradientBoostingBaseline training and prediction | 8 | 2+2+2+2 |
| M-5 | Comparison Logic | Implement ModelComparator for performance gap and feature importance | 10 | 3+2+3+2 |
| M-6 | Visualization | Generate 5 required figures (coefficients, comparison, PCA, importance, confusion) | 14 | 3+3+3+3+2 |
| M-7 | Mechanism Evaluation | Implement gate checking and report generation | 6 | 2+2+1+1 |
| M-8 | Integration | Wire all modules in run_h_m1_experiment.py, test end-to-end | 10 | 3+2+3+2 |

**Complexity Distribution:**
- High (14-17): [M-6] = 14 points
- Medium (9-13): [M-3, M-5, M-8] = 32 points
- Low (4-8): [M-1, M-2, M-4, M-7] = 26 points
- **Total:** 72 points across 8 tasks

**Complexity Breakdown:**
- Module_Size: LOC (1=<50, 2=50-100, 3=100-150, 4=>150, 5=>200)
- Dependencies: External integrations (1=none, 2=one, 3=H-E1+sklearn, 4=complex, 5=multi-framework)
- Algorithm: Logic complexity (1=trivial, 2=simple, 3=moderate PCA, 4=complex mesh grid, 5=novel)
- Integration: Cross-module dependencies (1=standalone, 2=one dep, 3=multiple, 4=central hub, 5=system-wide)

---

## Dependencies

### H-E1 Modules (Reused)
- `h-e1/code/src/trainer.py` - MaintenanceClassifier (retrain if needed)
- `h-e1/code/src/feature_engineer.py` - FeatureEngineer (data preprocessing)
- `h-e1/code/config.py` - ExperimentConfig (dataset parameters)
- `h-e1/data/raw_metadata.csv` - Dataset (if available)

### Python Libraries (New for H-M1)
```
scikit-learn>=1.0.0  # sklearn.decomposition.PCA, ensemble.GradientBoostingClassifier
matplotlib>=3.4.0
seaborn>=0.11.0
numpy>=1.20.0
pandas>=1.3.0
```

### Environment
- Python 3.8+
- Single CPU (GB training ~10 min)
- ~100 MB disk space

---

## Implementation Notes

### Model Loading Strategy

```python
# Priority 1: Load trained H-E1 model
try:
    lr_model = joblib.load(h_e1_model_path)
    scaler = joblib.load(h_e1_scaler_path)
except FileNotFoundError:
    # Priority 2: Retrain using H-E1 pipeline
    sys.path.insert(0, h_e1_base_path)
    from src.trainer import MaintenanceClassifier
    from src.feature_engineer import FeatureEngineer
    
    classifier = MaintenanceClassifier(random_state=42)
    # Load H-E1 data, preprocess, train
    classifier.train(X_train, y_train)
    lr_model = classifier.model
    scaler = classifier.scaler
```

### Coefficient Extraction Protocol

```python
# Extract coefficients
coef = lr_model.coef_[0]  # Shape: (8,)
feature_names = ['stars_log', 'forks_log', 'contributors_log', 
                 'commits_log', 'issues_log', 'days_since_last',
                 'commit_freq_weekly', 'issue_resolution_rate']
coefficients = dict(zip(feature_names, coef))

# Verify signs
expected_signs = {
    'days_since_last': 'negative',  # Staleness decreases maintenance
    'stars_log': 'positive',
    'forks_log': 'positive',
    'contributors_log': 'positive',
    'commits_log': 'positive',
    'issues_log': 'positive',
    'commit_freq_weekly': 'positive',
    'issue_resolution_rate': 'positive'
}

signs_correct = (
    coefficients['days_since_last'] < 0 and
    all(coefficients[k] > 0 for k in feature_names if k != 'days_since_last')
)
```

### Gradient Boosting Training Protocol

```python
from sklearn.ensemble import GradientBoostingClassifier

gb_model = GradientBoostingClassifier(
    n_estimators=50,
    max_depth=6,
    learning_rate=0.1,
    random_state=42
)
gb_model.fit(X_train_scaled, y_train)

# Compare performance
lr_acc = lr_model.score(X_test_scaled, y_test)
gb_acc = gb_model.score(X_test_scaled, y_test)
gap = abs(lr_acc - gb_acc)
linear_sufficient = gap <= 0.05
```

### PCA Decision Boundary Visualization

```python
from sklearn.decomposition import PCA

# Project to 2D
pca = PCA(n_components=2)
X_2d = pca.fit_transform(X_test_scaled)

# Create mesh grid
x_min, x_max = X_2d[:, 0].min() - 1, X_2d[:, 0].max() + 1
y_min, y_max = X_2d[:, 1].min() - 1, X_2d[:, 1].max() + 1
xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100),
                     np.linspace(y_min, y_max, 100))

# Project back to original space and predict
mesh_original = pca.inverse_transform(np.c_[xx.ravel(), yy.ravel()])
Z = lr_model.predict(mesh_original).reshape(xx.shape)

# Plot
plt.contourf(xx, yy, Z, alpha=0.3)
plt.scatter(X_2d[:, 0], X_2d[:, 1], c=y_test, cmap='viridis')
plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.2%} var)')
plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.2%} var)')
```

### Feature Importance Comparison

```python
# LR feature importance (absolute coefficient magnitudes)
lr_importance = {k: abs(v) for k, v in coefficients.items()}

# GB feature importance (built-in)
gb_importance = dict(zip(feature_names, gb_model.feature_importances_))

# Top-3 overlap
lr_top3 = sorted(lr_importance, key=lr_importance.get, reverse=True)[:3]
gb_top3 = sorted(gb_importance, key=gb_importance.get, reverse=True)[:3]
overlap = len(set(lr_top3) & set(gb_top3))
alignment_pass = overlap >= 2
```

### Gate Evaluation

```python
mechanism_validated = (
    signs_correct and           # EM-1: Coefficient signs correct
    gap <= 0.05 and             # EM-2: Performance gap ≤ 5%
    overlap >= 2                # EM-3: Feature importance alignment
)
```

---

## Visualization Requirements

### Required Figures (Mandatory)

1. **Coefficient Bar Chart** (`coefficient_bar_chart.png`)
   - X-axis: 8 feature names
   - Y-axis: Coefficient values
   - Color: Red for negative (days_since_last), Green for positive
   - Expected: 1 red bar, 7 green bars

2. **Performance Comparison** (`performance_comparison.png`)
   - Side-by-side bar chart: LR vs GB
   - Metrics: Accuracy, F1
   - Include performance gap annotation

3. **Decision Boundary PCA** (`decision_boundary_pca.png`)
   - 2D scatter plot: PC1 vs PC2
   - Colors: Maintained (green) vs Abandoned (red)
   - Overlay: LR decision boundary contour
   - Include explained variance in axis labels

4. **Feature Importance Comparison** (`feature_importance_comparison.png`)
   - Side-by-side bar chart: LR importance vs GB importance
   - Sorted by LR importance descending
   - Highlight top-3 overlap

5. **Confusion Matrices** (`confusion_matrix_comparison.png`)
   - Two confusion matrices: LR (left), GB (right)
   - Heatmap format with counts

All figures: 300 DPI PNG, seaborn default style, clear labels.

---

## Risk Mitigation

### R-1: H-E1 Model Not Saved
**Mitigation:** Implement retrain fallback using H-E1 pipeline (MaintenanceClassifier)

### R-2: GB Training Time Exceeds Budget
**Mitigation:** Use n_estimators=50 (reduced from typical 100), max_depth=6 to limit complexity

### R-3: PCA Variance Loss
**Mitigation:** Report explained variance ratio, use visualization for interpretation only (not evaluation)

### R-4: Coefficient Signs Incorrect
**Mitigation:** Investigate feature engineering issues, report in validation document as mechanism failure

---

## Validation Criteria

**Primary Success (MUST_WORK):**
- Coefficient signs correct (negative staleness, positive activity)
- Performance gap ≤ 5% (linear sufficient)
- Feature overlap ≥ 2 (causal pathway validated)

**Secondary Success:**
- PCA visualization shows clear linear separation
- GB feature importance aligns with LR coefficients

**Failure Condition:**
- Signs incorrect → Feature engineering issues
- Gap > 10% → Non-linear mechanism, reject linear hypothesis
- Overlap < 2 → Causal pathway incorrect

**Expected Performance:**
- LR: Accuracy 1.0, F1 1.0 (from H-E1)
- GB: Expected similar (0.95-1.0) if linear sufficient
- Gap: Expected ≤ 5%

---

## Out of Scope

- Multi-seed analysis (inherited single seed from H-E1)
- Non-linear feature engineering
- Hyperparameter tuning for GB (using standard defaults)
- Temporal mechanism analysis (train on old data, test on new)
- 3D PCA visualization (2D sufficient for boundary interpretation)

---

**End of Architecture Document**
