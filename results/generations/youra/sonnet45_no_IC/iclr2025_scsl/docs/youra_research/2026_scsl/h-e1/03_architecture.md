# Architecture: Repository Maintenance Classification (H-E1)

**Version:** 1.0  
**Date:** 2026-07-13  
**Hypothesis:** H-E1 (EXISTENCE)  
**Type:** Proof of Concept - Baseline Validation

**Applied:** Minimal PoC pattern for EXISTENCE hypothesis

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch  
**Analyzed Path:** N/A  
**Findings:** No existing codebase. Standard sklearn + GitHub API implementation.

---

## Design Principles

**EXISTENCE Scope:**
- Single-file modules for simplicity
- Baseline model only (Logistic Regression)
- No ablation studies
- Minimal infrastructure

**Success Criteria:**
- Accuracy ≥75% AND F1 ≥0.73
- MUST_WORK gate validation

---

## Module Structure

### 1. Data Collection (`src/data_collector.py`)

**Dependencies:** requests, pandas

```python
class GitHubDataCollector:
    def __init__(self, api_token: str): ...
    def collect_pwc_repos(self, year_range: tuple, min_stars: int, max_repos: int) -> pd.DataFrame: ...
    def fetch_repo_metadata(self, repo_full_name: str) -> dict: ...
    def save_raw_data(self, data: pd.DataFrame, output_path: str): ...
```

### 2. Feature Engineering (`src/feature_engineer.py`)

**Dependencies:** numpy, pandas

```python
class FeatureEngineer:
    def __init__(self): ...
    def transform_features(self, raw_data: pd.DataFrame) -> pd.DataFrame: ...
    def create_labels(self, raw_data: pd.DataFrame, threshold_days: int = 180) -> np.ndarray: ...
    def validate_distributions(self, features: pd.DataFrame) -> dict: ...
```

### 3. Model Training (`src/trainer.py`)

**Dependencies:** sklearn.linear_model, sklearn.preprocessing, sklearn.model_selection

```python
class MaintenanceClassifier:
    def __init__(self, random_state: int = 42): ...
    def prepare_data(self, X: pd.DataFrame, y: np.ndarray, test_size: float = 0.20) -> tuple: ...
    def train(self, X_train: np.ndarray, y_train: np.ndarray): ...
    def predict(self, X: np.ndarray) -> np.ndarray: ...
    def save_model(self, path: str): ...
```

### 4. Evaluation (`src/evaluator.py`)

**Dependencies:** sklearn.metrics

```python
class GateEvaluator:
    def __init__(self, accuracy_threshold: float = 0.75, f1_threshold: float = 0.73): ...
    def compute_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> dict: ...
    def check_gate_status(self, metrics: dict) -> tuple[bool, str]: ...
    def generate_classification_report(self, y_true: np.ndarray, y_pred: np.ndarray) -> str: ...
```

### 5. Visualization (`src/visualizer.py`)

**Dependencies:** matplotlib, seaborn, sklearn.metrics

```python
class ResultVisualizer:
    def __init__(self, output_dir: str): ...
    def plot_gate_metrics(self, metrics: dict, targets: dict): ...
    def plot_confusion_matrix(self, y_true: np.ndarray, y_pred: np.ndarray): ...
    def plot_feature_importance(self, coefficients: np.ndarray, feature_names: list): ...
    def plot_roc_curve(self, y_true: np.ndarray, y_proba: np.ndarray): ...
    def plot_class_distribution(self, y_train: np.ndarray, y_test: np.ndarray): ...
```

### 6. Experiment Runner (`run_experiment.py`)

**Dependencies:** All above modules

```python
def main():
    """End-to-end experiment pipeline."""
    # 1. Collect data
    # 2. Engineer features
    # 3. Train model
    # 4. Evaluate on test set
    # 5. Generate visualizations
    # 6. Output gate decision
    pass
```

### 7. Configuration (`config.py`)

**Dependencies:** None

```python
@dataclass
class ExperimentConfig:
    github_api_token: str
    data_output_path: str
    figures_output_path: str
    dataset_size: int = 2000
    year_range: tuple = (2020, 2024)
    min_stars: int = 32
    test_size: float = 0.20
    random_state: int = 42
    label_threshold_days: int = 180
    accuracy_threshold: float = 0.75
    f1_threshold: float = 0.73
```

---

## File Organization

```
h-e1/
├── code/
│   ├── src/
│   │   ├── data_collector.py       # GitHub API integration
│   │   ├── feature_engineer.py     # Log1p transforms + labeling
│   │   ├── trainer.py              # LogisticRegression wrapper
│   │   ├── evaluator.py            # Metrics + gate checking
│   │   └── visualizer.py           # 5 required figures
│   ├── config.py                   # Experiment parameters
│   ├── run_experiment.py           # Main pipeline
│   └── requirements.txt            # Dependencies
├── data/
│   └── raw_metadata.csv            # Collected GitHub data
├── figures/                        # Generated visualizations
└── 04_validation.md                # Results report (auto-generated)
```

---

## Data Flow

```
GitHub API → data_collector.py → raw_metadata.csv
           ↓
feature_engineer.py → (X, y) features + labels
           ↓
trainer.py → trained LogisticRegression model
           ↓
evaluator.py → metrics (accuracy, F1, precision, recall)
           ↓
visualizer.py → 5 figures (gate metrics, confusion matrix, etc.)
           ↓
Gate Decision → 04_validation.md
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup Project | Create directory structure, requirements.txt, config.py | 4 | 1+1+1+1 |
| A-2 | Data Collection | Implement GitHubDataCollector with Papers with Code API integration | 12 | 3+3+4+2 |
| A-3 | Feature Engineering | Implement log1p transforms, derived features, label generation | 10 | 3+2+3+2 |
| A-4 | Model Training | Implement MaintenanceClassifier with train/test split, normalization, LR training | 8 | 2+2+2+2 |
| A-5 | Evaluation Pipeline | Implement metrics computation, gate checking, classification report | 6 | 2+2+1+1 |
| A-6 | Visualization | Generate 5 required figures (gate metrics, confusion matrix, ROC, etc.) | 10 | 2+2+2+2+2 |
| A-7 | Integration | Wire all modules in run_experiment.py, test end-to-end pipeline | 8 | 2+2+2+2 |

**Complexity Distribution:**
- Medium (9-13): [A-2, A-3, A-6] = 32 points
- Low (4-8): [A-1, A-4, A-5, A-7] = 26 points
- **Total:** 58 points across 7 tasks

**Complexity Breakdown:**
- Module_Size: Implementation lines of code (1=<50, 2=50-100, 3=100-200, 4=>200)
- Dependencies: External API/library integration (1=none, 2=one, 3=multiple, 4=complex)
- Algorithm: Logic complexity (1=trivial, 2=simple, 3=moderate, 4=complex)
- Integration: Cross-module dependencies (1=standalone, 2=one dep, 3=multiple, 4=central hub)

---

## Dependencies

### External APIs
- GitHub REST API v3 (authentication required)
- Papers with Code API (public, no auth)

### Python Libraries
```
scikit-learn>=1.0.0
pandas>=1.3.0
numpy>=1.20.0
matplotlib>=3.4.0
seaborn>=0.11.0
requests>=2.26.0
python-dotenv>=0.19.0
```

### Environment
- Python 3.8+
- Single CPU (no GPU required)
- ~500 MB disk space

---

## Implementation Notes

### Data Collection Strategy
1. Query Papers with Code API for benchmark repositories (2020-2024)
2. Filter: min_stars=32, non-fork, active during period
3. For each repository, extract via GitHub API:
   - stars, forks, contributors, total_commits, open_issues
   - last_commit_date (for days_since_last_commit)
   - commit history (for commit_frequency_median_weekly)
   - issue history (for issue_resolution_rate)
4. Handle rate limiting: 5000 req/hr with authentication
5. Cache responses locally to enable re-runs

### Feature Engineering Protocol
```python
# Log1p transforms (handle zeros gracefully)
features['stars_log'] = np.log1p(raw['stars'])
features['forks_log'] = np.log1p(raw['forks'])
features['contributors_log'] = np.log1p(raw['contributors'])
features['total_commits_log'] = np.log1p(raw['total_commits'])
features['open_issues_log'] = np.log1p(raw['open_issues'])

# Derived features (keep raw scale)
features['days_since_last_commit'] = (datetime.now() - raw['last_commit_date']).days
features['commit_frequency_median_weekly'] = raw['commit_frequency_median_weekly']
features['issue_resolution_rate'] = raw['closed_issues'] / (raw['total_issues'] + 1e-6)

# Binary labels
labels = (features['days_since_last_commit'] < 180).astype(int)  # 1=maintained, 0=abandoned
```

### Model Training Protocol
```python
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

# Stratified split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, stratify=y, random_state=42
)

# Normalization
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Model
model = LogisticRegression(
    max_iter=1000,
    class_weight='balanced',
    solver='lbfgs',
    random_state=42
)
model.fit(X_train_scaled, y_train)
```

### Evaluation Metrics
```python
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

y_pred = model.predict(X_test_scaled)

metrics = {
    'accuracy': accuracy_score(y_test, y_pred),
    'f1': f1_score(y_test, y_pred),
    'precision': precision_score(y_test, y_pred),
    'recall': recall_score(y_test, y_pred)
}

# Gate decision
gate_pass = (metrics['accuracy'] >= 0.75) and (metrics['f1'] >= 0.73)
```

### Visualization Requirements
1. **Gate Metrics Comparison** (mandatory): Bar chart comparing target vs actual
2. **Confusion Matrix**: Heatmap with TP/FP/TN/FN counts
3. **Feature Importance**: Bar chart of LR coefficient magnitudes
4. **ROC Curve**: ROC with AUC score
5. **Class Distribution**: Train/test split validation

All figures saved to `figures/` with 300 DPI PNG format.

---

## Risk Mitigation

### R-1: GitHub API Rate Limiting
**Mitigation:** Use authentication token (5000 req/hr), implement exponential backoff retry logic

### R-2: Class Imbalance
**Mitigation:** Use class_weight='balanced', validate with F1 score (imbalance-robust metric)

### R-3: Labeling Noise
**Mitigation:** Report class distribution statistics, validate on high-confidence subset if needed

### R-4: Feature Distribution Issues
**Mitigation:** Validate log-transformed features are approximately normal, use StandardScaler

---

## Validation Criteria

**Primary Success (MUST_WORK):**
- Accuracy ≥ 0.75 AND F1 ≥ 0.73

**Secondary Success:**
- Performance exceeds majority baseline by ≥10%
- No convergence warnings from LogisticRegression

**Failure Condition:**
- Accuracy < 0.70 → Linear separability hypothesis rejected

**Expected Baselines:**
- Majority baseline: ~60% (class distribution dependent)
- Target: ≥75% accuracy
- Context: CSI (F1 0.80), GB (C-Index 0.810)

---

## Out of Scope

- Graph-based features (HITS, PageRank)
- Ensemble methods (Gradient Boosting, Random Forest)
- Hyperparameter tuning (using sklearn defaults)
- Temporal validation (train on older data, test on newer)
- Production deployment infrastructure

---

**End of Architecture Document**
