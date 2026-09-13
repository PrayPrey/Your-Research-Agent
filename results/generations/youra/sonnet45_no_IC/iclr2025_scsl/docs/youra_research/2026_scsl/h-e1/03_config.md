# Configuration: Repository Maintenance Classification (H-E1)

**Version:** 1.0  
**Date:** 2026-07-13  
**Hypothesis:** H-E1 (EXISTENCE)  
**Type:** Proof of Concept - Baseline Validation

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation - designing new config schema  
**Config Files Found:** None - new config  
**Pattern Used:** dataclass (Python 3.7+)

**Applied:** Standard sklearn defaults pattern

---

## A-4: Model Training [Complexity: 8, Budget: 8]

**Applied:** Standard sklearn LogisticRegression defaults with balanced class weights

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass
from typing import Tuple

@dataclass
class ModelConfig:
    """Logistic Regression training configuration."""
    
    # Train/test split
    test_size: float = 0.20
    random_state: int = 42
    stratify: bool = True
    
    # Logistic Regression hyperparameters
    max_iter: int = 1000
    solver: str = 'lbfgs'
    class_weight: str = 'balanced'
    
    # Feature normalization
    normalize_features: bool = True
    
    # Model persistence
    model_save_path: str = 'models/lr_classifier.pkl'
    scaler_save_path: str = 'models/feature_scaler.pkl'
```

**Rationale for non-standard values:**
- `class_weight='balanced'`: Handles potential class imbalance in maintained vs abandoned repos
- `max_iter=1000`: Increased from sklearn default (100) to ensure convergence

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Train/test split | Implement stratified 80/20 split with random_state=42 |
| C-4-2 | Feature normalization | Apply StandardScaler (fit on train, transform on test) |
| C-4-3 | Model initialization | Create LogisticRegression with balanced weights |
| C-4-4 | Model training | Fit model on scaled training data, validate convergence |

---

## A-5: Evaluation Pipeline [Complexity: 6, Budget: 6]

**Applied:** Standard sklearn metrics pattern for binary classification

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class EvaluationConfig:
    """Evaluation metrics and gate thresholds."""
    
    # Gate thresholds (MUST_WORK criteria)
    accuracy_threshold: float = 0.75
    f1_threshold: float = 0.73
    
    # Metrics to compute
    compute_metrics: Tuple[str, ...] = (
        'accuracy',
        'precision',
        'recall',
        'f1',
        'roc_auc'
    )
    
    # Classification report
    output_dict: bool = True
    zero_division: int = 0
    
    # Report save path
    report_path: str = 'results/metrics.json'
```

**Rationale for non-standard values:**
- `accuracy_threshold=0.75`, `f1_threshold=0.73`: Defined by hypothesis success criteria

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Metrics computation | Calculate accuracy, precision, recall, F1, ROC-AUC |
| C-5-2 | Gate checking | Compare metrics against thresholds, determine PASS/FAIL |
| C-5-3 | Classification report | Generate sklearn classification_report with per-class metrics |
| C-5-4 | Results persistence | Save metrics dict to JSON for validation report |

---

## A-7: Integration [Complexity: 8, Budget: 8]

**Applied:** Pipeline orchestration pattern for end-to-end experiment

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    """End-to-end experiment pipeline configuration."""
    
    # GitHub API
    github_api_token: str = ''  # Set via environment variable
    
    # Data collection
    dataset_size: int = 2000
    year_range: Tuple[int, int] = (2020, 2024)
    min_stars: int = 32
    data_output_path: str = 'data/raw_metadata.csv'
    
    # Feature engineering
    label_threshold_days: int = 180
    
    # Visualization
    figures_output_path: str = 'figures/'
    figure_dpi: int = 300
    figure_format: str = 'png'
    
    # Integration
    model_config: ModelConfig = None
    eval_config: EvaluationConfig = None
    
    def __post_init__(self):
        """Initialize nested configs with defaults."""
        if self.model_config is None:
            self.model_config = ModelConfig()
        if self.eval_config is None:
            self.eval_config = EvaluationConfig()
```

**Rationale for non-standard values:**
- `dataset_size=2000`: Specified in PRD for computational feasibility
- `year_range=(2020, 2024)`: Recent repositories for relevance
- `min_stars=32`: Filter low-activity repos as per PRD
- `label_threshold_days=180`: 6-month activity window for maintenance classification
- `figure_dpi=300`: Publication-quality visualizations

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Data collection | Instantiate GitHubDataCollector, fetch 2000 repos |
| C-7-2 | Feature engineering | Apply log1p transforms, generate labels |
| C-7-3 | Model training | Call MaintenanceClassifier with ModelConfig |
| C-7-4 | Evaluation | Run GateEvaluator with EvaluationConfig |
| C-7-5 | Visualization | Generate 5 required figures |
| C-7-6 | Pipeline orchestration | Wire modules with error handling |
| C-7-7 | Results output | Write gate decision to 04_validation.md |
| C-7-8 | End-to-end test | Validate full pipeline execution |

---

## Complete Configuration File

**File:** `code/config.py`

```python
from dataclasses import dataclass
from typing import Tuple

@dataclass
class ModelConfig:
    """Logistic Regression training configuration."""
    test_size: float = 0.20
    random_state: int = 42
    stratify: bool = True
    max_iter: int = 1000
    solver: str = 'lbfgs'
    class_weight: str = 'balanced'
    normalize_features: bool = True
    model_save_path: str = 'models/lr_classifier.pkl'
    scaler_save_path: str = 'models/feature_scaler.pkl'

@dataclass
class EvaluationConfig:
    """Evaluation metrics and gate thresholds."""
    accuracy_threshold: float = 0.75
    f1_threshold: float = 0.73
    compute_metrics: Tuple[str, ...] = (
        'accuracy', 'precision', 'recall', 'f1', 'roc_auc'
    )
    output_dict: bool = True
    zero_division: int = 0
    report_path: str = 'results/metrics.json'

@dataclass
class ExperimentConfig:
    """End-to-end experiment pipeline configuration."""
    github_api_token: str = ''
    dataset_size: int = 2000
    year_range: Tuple[int, int] = (2020, 2024)
    min_stars: int = 32
    data_output_path: str = 'data/raw_metadata.csv'
    label_threshold_days: int = 180
    figures_output_path: str = 'figures/'
    figure_dpi: int = 300
    figure_format: str = 'png'
    model_config: ModelConfig = None
    eval_config: EvaluationConfig = None
    
    def __post_init__(self):
        if self.model_config is None:
            self.model_config = ModelConfig()
        if self.eval_config is None:
            self.eval_config = EvaluationConfig()
```

---

## Usage Example

```python
from config import ExperimentConfig

# Initialize with defaults
config = ExperimentConfig(
    github_api_token="ghp_xxx"  # Set from environment
)

# Access nested configs
print(config.model_config.max_iter)  # 1000
print(config.eval_config.accuracy_threshold)  # 0.75

# Override specific values
config.dataset_size = 1000
config.model_config.random_state = 123
```

---

## Self-Validation Checklist

- [x] ONE format only (Dataclass)
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Rationale only for non-standard values
- [x] Subtask count within budget (8/8, 6/6, 8/8)
- [x] Total length < 400 lines
- [x] Codebase Analysis (Serena) section included
- [x] Green-field project - Serena skip acceptable

---

**End of Configuration Document**
