# Logic Design: H-M2 Meta-Classifier Training Sufficiency

**Date:** 2026-07-13
**Hypothesis:** H-M2 (MECHANISM)
**Type:** Random Forest Meta-Learning Pipeline
**Tier:** STANDARD (Sklearn-based classification)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** API signatures verified from h-m1 code
**Analyzed Path:** `docs/youra_research/h-m1/code/`
**Relevant Symbols:** `Tier1FeatureComputer`, `Tier2FeatureComputer`, `BenchmarkDataLoader`

**Key Findings:**
- H-M1 implements modular feature computation in `src/feature_computer.py`
- `Tier1FeatureComputer.compute_features(benchmarks)` returns DataFrame (63, 4)
- `Tier2FeatureComputer.compute_features(benchmarks)` returns DataFrame (63, ~6)
- `BenchmarkDataLoader.load_benchmarks()` reads JSONL and returns List[Dict]
- `BenchmarkDataLoader.extract_method_rankings(benchmarks)` returns DataFrame (63, 4)
- All methods use NaN for missing data (no mock defaults)

---

## Applied Patterns

**Applied:** sklearn Sequential Pipeline with Cross-Validation
- Pattern: Load → Preprocess → Train → Evaluate → Visualize
- Analysis: Leave-K-out CV with sklearn.model_selection.KFold
- Model: sklearn.ensemble.RandomForestClassifier with small-data hyperparameters

---

## M2-2: Data Preprocessor (Complexity: 8)

### API Signatures

```python
from typing import Tuple, List
import numpy as np
import pandas as pd
from pathlib import Path
import sys

class DataPreprocessor:
    """Preprocess H-E1 benchmarks using H-M1 feature computation."""
    
    def __init__(self, h_e1_path: str, h_m1_code_path: str):
        """
        Initialize with paths.
        h_e1_path: Path to benchmarks_collection.jsonl
        h_m1_code_path: Path to h-m1/code/ directory
        """
        self.h_e1_path = Path(h_e1_path)
        self.h_m1_code_path = Path(h_m1_code_path)
        self._add_h_m1_to_path()
    
    def _add_h_m1_to_path(self):
        """Add h-m1/code to sys.path for imports."""
        if str(self.h_m1_code_path) not in sys.path:
            sys.path.insert(0, str(self.h_m1_code_path))
    
    def load_and_prepare(
        self, 
        nan_threshold: float = 0.7
    ) -> Tuple[np.ndarray, np.ndarray, List[str], List[str]]:
        """
        Load benchmarks and prepare feature matrix + target labels.
        
        Returns: (X, y, feature_names, benchmark_ids)
            X: (63, F) feature matrix, F=4-10 after NaN filtering
            y: (63,) target labels (0=Linear, 1=Polynomial, 2=RNN, 3=Augmentation)
            feature_names: List of feature column names
            benchmark_ids: List of benchmark identifiers
        """
        ...
    
    def _load_benchmarks(self) -> List[Dict]:
        """Load from JSONL. Returns: List[Dict] length 63"""
        from src.data_loader import BenchmarkDataLoader
        loader = BenchmarkDataLoader(str(self.h_e1_path))
        return loader.load_benchmarks()
    
    def _compute_features(self, benchmarks: List[Dict]) -> pd.DataFrame:
        """Compute Tier1+2 features. Returns: (63, ~10) DataFrame"""
        from src.feature_computer import Tier1FeatureComputer, Tier2FeatureComputer
        tier1_df = Tier1FeatureComputer.compute_features(benchmarks)
        tier2_df = Tier2FeatureComputer.compute_features(benchmarks)
        features_df = pd.concat([tier1_df, tier2_df], axis=1)
        return features_df
    
    def _extract_target_labels(self, benchmarks: List[Dict]) -> np.ndarray:
        """
        Extract top-1 method family per benchmark.
        Returns: (63,) integer array, 0=Linear, 1=Polynomial, 2=RNN, 3=Augmentation
        """
        ...
    
    def _remove_sparse_features(
        self, 
        features_df: pd.DataFrame, 
        threshold: float = 0.7
    ) -> pd.DataFrame:
        """Remove columns with >70% NaN. Returns: (63, F) where F=4-10"""
        ...
    
    def _normalize_features(self, X: np.ndarray) -> np.ndarray:
        """Z-score normalize. X: (63, F) -> (63, F)"""
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        return scaler.fit_transform(X)
```

### Data Shapes

| Variable | Shape | Note |
|----------|-------|------|
| benchmarks | List[Dict] len=63 | Raw H-E1 records |
| tier1_df | (63, 4) | sample_size, dimensionality, num_classes, class_imbalance |
| tier2_df | (63, ~6) | Domain-specific (may vary) |
| features_df | (63, ~10) | Combined features before filtering |
| X_filtered | (63, F) | F=4-10 after NaN removal |
| y | (63,) | Integer labels 0-3 |

### Pseudo-code

```
load_and_prepare():
    1. benchmarks = _load_benchmarks()  # List[Dict] 63 records
    2. features_df = _compute_features(benchmarks)  # (63, ~10)
    3. y = _extract_target_labels(benchmarks)  # (63,)
    4. features_df = _remove_sparse_features(features_df, nan_threshold=0.7)
    5. X = features_df.values  # (63, F)
    6. X = _normalize_features(X)  # Z-score
    7. feature_names = features_df.columns.tolist()
    8. benchmark_ids = features_df.index.tolist()
    9. return X, y, feature_names, benchmark_ids

_extract_target_labels(benchmarks):
    labels = []
    family_map = {"Linear": 0, "Polynomial": 1, "RNN": 2, "Augmentation": 3}
    for b in benchmarks:
        method_rankings = b['method_rankings']
        family_percentiles = {}
        for method, data in method_rankings.items():
            family = data['family']
            percentile = data['ranking_percentile']
            if family not in family_percentiles:
                family_percentiles[family] = []
            family_percentiles[family].append(percentile)
        # Top-1 family: highest mean percentile
        family_means = {f: np.mean(p) for f, p in family_percentiles.items()}
        top_family = max(family_means, key=family_means.get)
        labels.append(family_map[top_family])
    return np.array(labels)

_remove_sparse_features(features_df, threshold):
    nan_ratio = features_df.isna().sum() / len(features_df)
    keep_cols = nan_ratio[nan_ratio <= threshold].index
    print(f"Keeping {len(keep_cols)}/{len(features_df.columns)} features")
    return features_df[keep_cols]
```

---

## M2-3: Baseline Model (Complexity: 4)

### API Signatures

```python
from sklearn.dummy import DummyClassifier

class BaselineModel:
    """Majority class baseline for comparison."""
    
    def __init__(self, random_state: int = 42):
        self.model = DummyClassifier(strategy="most_frequent", random_state=random_state)
    
    def fit(self, X_train: np.ndarray, y_train: np.ndarray):
        """Fit baseline. X_train: (N, F), y_train: (N,)"""
        self.model.fit(X_train, y_train)
    
    def predict(self, X_test: np.ndarray) -> np.ndarray:
        """Predict. X_test: (M, F) -> (M,)"""
        return self.model.predict(X_test)
    
    def score(self, X_test: np.ndarray, y_test: np.ndarray) -> float:
        """Accuracy. Returns: scalar 0.0-1.0"""
        return self.model.score(X_test, y_test)
```

---

## M2-4: Meta-Classifier (Complexity: 6)

### API Signatures

```python
from sklearn.ensemble import RandomForestClassifier

class MetaClassifier:
    """Random Forest meta-classifier with small-data hyperparameters."""
    
    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 10,
        min_samples_split: int = 5,
        min_samples_leaf: int = 2,
        random_state: int = 42
    ):
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            criterion='gini',
            max_features='sqrt',
            random_state=random_state
        )
    
    def fit(self, X_train: np.ndarray, y_train: np.ndarray):
        """Fit RF. X_train: (N, F), y_train: (N,)"""
        self.model.fit(X_train, y_train)
    
    def predict(self, X_test: np.ndarray) -> np.ndarray:
        """Predict. X_test: (M, F) -> (M,)"""
        return self.model.predict(X_test)
    
    def score(self, X_test: np.ndarray, y_test: np.ndarray) -> float:
        """Accuracy. Returns: scalar 0.0-1.0"""
        return self.model.score(X_test, y_test)
    
    def get_feature_importances(self) -> np.ndarray:
        """Get RF feature importances. Returns: (F,) array summing to 1.0"""
        return self.model.feature_importances_
```

---

## M2-5: Cross-Validation Trainer (Complexity: 9, Budget: 1)

### API Signatures

```python
from sklearn.model_selection import KFold
from typing import Dict

class CrossValidationTrainer:
    """Leave-5-out cross-validation trainer."""
    
    def __init__(
        self, 
        model: MetaClassifier, 
        baseline_model: BaselineModel,
        n_folds: int = 13,
        random_state: int = 42
    ):
        self.model = model
        self.baseline_model = baseline_model
        self.n_folds = n_folds
        self.random_state = random_state
    
    def run_cv(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """
        Run cross-validation.
        X: (63, F), y: (63,)
        Returns: {
            'cv_scores': List[float] length 13,
            'train_scores': List[float] length 13,
            'baseline_scores': List[float] length 13,
            'predictions': np.ndarray (63,),
            'fold_indices': List[Tuple[array, array]]
        }
        """
        ...
    
    def _create_cv_splitter(self, n_samples: int) -> KFold:
        """Create KFold splitter. n_samples: 63 -> 13 folds"""
        return KFold(n_splits=self.n_folds, shuffle=True, random_state=self.random_state)
    
    def _train_fold(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict:
        """
        Train single fold.
        X_train: (58, F), y_train: (58,)
        X_test: (5, F), y_test: (5,)
        Returns: {'train_acc': float, 'test_acc': float, 'baseline_acc': float}
        """
        ...
```

### Pseudo-code

```
run_cv(X, y):
    cv_splitter = _create_cv_splitter(len(X))
    cv_scores = []
    train_scores = []
    baseline_scores = []
    predictions = np.zeros(len(y))
    fold_indices = []
    
    for fold_idx, (train_idx, test_idx) in enumerate(cv_splitter.split(X)):
        X_train, y_train = X[train_idx], y[train_idx]
        X_test, y_test = X[test_idx], y[test_idx]
        
        fold_results = _train_fold(X_train, y_train, X_test, y_test)
        
        cv_scores.append(fold_results['test_acc'])
        train_scores.append(fold_results['train_acc'])
        baseline_scores.append(fold_results['baseline_acc'])
        
        # Store predictions for test indices
        self.model.fit(X_train, y_train)
        predictions[test_idx] = self.model.predict(X_test)
        
        fold_indices.append((train_idx, test_idx))
        print(f"Fold {fold_idx+1}: Train={fold_results['train_acc']:.3f}, Test={fold_results['test_acc']:.3f}")
    
    return {
        'cv_scores': cv_scores,
        'train_scores': train_scores,
        'baseline_scores': baseline_scores,
        'predictions': predictions,
        'fold_indices': fold_indices
    }

_train_fold(X_train, y_train, X_test, y_test):
    # Train meta-classifier
    self.model.fit(X_train, y_train)
    train_acc = self.model.score(X_train, y_train)
    test_acc = self.model.score(X_test, y_test)
    
    # Train baseline
    self.baseline_model.fit(X_train, y_train)
    baseline_acc = self.baseline_model.score(X_test, y_test)
    
    return {
        'train_acc': train_acc,
        'test_acc': test_acc,
        'baseline_acc': baseline_acc
    }
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Fold Iteration Logic | Implement CV splitting, per-fold training, and result aggregation |

---

## M2-6: Metrics Calculator (Complexity: 7)

### API Signatures

```python
from sklearn.metrics import accuracy_score, confusion_matrix

class MetricsCalculator:
    """Compute evaluation metrics."""
    
    def compute_cv_accuracy(self, cv_results: Dict) -> float:
        """Compute mean CV accuracy. Returns: scalar 0.0-1.0"""
        return np.mean(cv_results['cv_scores'])
    
    def compute_generalization_gap(self, cv_results: Dict) -> float:
        """Compute train-test gap. Returns: scalar (positive = overfitting)"""
        train_scores = np.array(cv_results['train_scores'])
        cv_scores = np.array(cv_results['cv_scores'])
        return np.mean(train_scores - cv_scores)
    
    def compute_baseline_delta(
        self, 
        cv_accuracy: float, 
        baseline_accuracy: float
    ) -> float:
        """Compute improvement over baseline. Returns: scalar (positive = better)"""
        return cv_accuracy - baseline_accuracy
    
    def compute_per_domain_accuracy(
        self, 
        y_true: np.ndarray, 
        y_pred: np.ndarray,
        domains: List[str]
    ) -> Dict[str, float]:
        """
        Compute accuracy per domain.
        y_true: (63,), y_pred: (63,), domains: List[str] length 63
        Returns: {"Vision": 0.45, "NLP": 0.38, ...}
        """
        ...
    
    def generate_confusion_matrix(
        self, 
        y_true: np.ndarray, 
        y_pred: np.ndarray
    ) -> np.ndarray:
        """Generate confusion matrix. Returns: (4, 4) array"""
        return confusion_matrix(y_true, y_pred)
```

---

## M2-7: Gate Evaluator (Complexity: 4)

### API Signatures

```python
from typing import Literal

class GateEvaluator:
    """Evaluate gate thresholds."""
    
    def __init__(
        self, 
        accuracy_threshold: float = 0.35,
        gap_threshold: float = 0.20,
        partial_accuracy_threshold: float = 0.30,
        partial_gap_threshold: float = 0.25
    ):
        self.accuracy_threshold = accuracy_threshold
        self.gap_threshold = gap_threshold
        self.partial_accuracy_threshold = partial_accuracy_threshold
        self.partial_gap_threshold = partial_gap_threshold
    
    def evaluate(
        self, 
        cv_accuracy: float, 
        generalization_gap: float
    ) -> Literal["PASS", "PARTIAL", "FAIL"]:
        """
        Determine gate result.
        Returns: "PASS" | "PARTIAL" | "FAIL"
        """
        if cv_accuracy > self.accuracy_threshold and generalization_gap < self.gap_threshold:
            return "PASS"
        elif cv_accuracy >= self.partial_accuracy_threshold and generalization_gap < self.partial_gap_threshold:
            return "PARTIAL"
        else:
            return "FAIL"
```

---

## M2-8: Visualizations (Complexity: 11, Budget: 2)

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import learning_curve

def plot_gate_metrics_comparison(
    baseline_acc: float,
    cv_acc: float,
    target: float,
    threshold: float,
    output_path: str
):
    """
    Figure 1: Bar chart of baseline vs target vs actual.
    baseline_acc: scalar, cv_acc: scalar, target: 0.40, threshold: 0.35
    """
    ...

def plot_learning_curve(
    X: np.ndarray,
    y: np.ndarray,
    model: MetaClassifier,
    train_sizes: List[int],
    cv: int,
    output_path: str
):
    """
    Figure 2: Learning curve (train vs test accuracy by training size).
    X: (63, F), y: (63,), train_sizes: [10, 20, 30, 40, 50, 58]
    """
    ...

def plot_confusion_matrix(
    cm: np.ndarray,
    class_names: List[str],
    output_path: str
):
    """
    Figure 3: Confusion matrix heatmap.
    cm: (4, 4), class_names: ["Linear", "Polynomial", "RNN", "Augmentation"]
    """
    ...

def plot_per_domain_accuracy(
    domain_accs: Dict[str, float],
    output_path: str
):
    """Figure 4: Bar chart per domain. domain_accs: {"Vision": 0.45, ...}"""
    ...

def plot_feature_importance(
    importances: np.ndarray,
    feature_names: List[str],
    output_path: str
):
    """Figure 5: Horizontal bar chart. importances: (F,), feature_names: List[str]"""
    ...

def plot_generalization_gap_per_fold(
    cv_results: Dict,
    output_path: str
):
    """Figure 6: Line plot train vs test per fold. cv_results: Dict with train/test scores"""
    ...

def generate_all_figures(
    cv_results: Dict,
    metrics: Dict,
    model: MetaClassifier,
    X: np.ndarray,
    y: np.ndarray,
    feature_names: List[str],
    output_dir: str
):
    """Generate all 6 figures."""
    plot_gate_metrics_comparison(...)
    plot_learning_curve(...)
    plot_confusion_matrix(...)
    plot_per_domain_accuracy(...)
    plot_feature_importance(...)
    plot_generalization_gap_per_fold(...)
```

### Pseudo-code

```
plot_gate_metrics_comparison(baseline_acc, cv_acc, target, threshold, output_path):
    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(['Baseline', 'Target', 'CV Accuracy'], 
                   [baseline_acc, target, cv_acc])
    bars[2].set_color('green' if cv_acc > threshold else 'red')
    ax.axhline(threshold, color='red', linestyle='--', label=f'Threshold ({threshold})')
    ax.set_ylabel('Accuracy')
    ax.set_title('Gate Metrics Comparison')
    plt.savefig(output_path, dpi=300)

plot_learning_curve(X, y, model, train_sizes, cv, output_path):
    train_sizes_abs, train_scores, test_scores = learning_curve(
        model.model, X, y, train_sizes=train_sizes, cv=cv, scoring='accuracy'
    )
    train_mean = np.mean(train_scores, axis=1)
    test_mean = np.mean(test_scores, axis=1)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(train_sizes_abs, train_mean, label='Train', marker='o')
    ax.plot(train_sizes_abs, test_mean, label='Test', marker='s')
    ax.set_xlabel('Training Size')
    ax.set_ylabel('Accuracy')
    ax.legend()
    plt.savefig(output_path, dpi=300)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | Learning Curve Plot | Implement sklearn learning_curve with error bars |
| L-8-2 | Confusion Matrix Heatmap | Implement seaborn heatmap with annotations |

---

## M2-9: Orchestration (Complexity: 10, Budget: 2)

### API Signatures

```python
from pathlib import Path
import json

class ExperimentOrchestrator:
    """Orchestrate complete meta-classifier experiment."""
    
    def __init__(self, config: Dict):
        """Initialize with hardcoded config."""
        self.config = config
        self.preprocessor = None
        self.baseline_model = None
        self.meta_classifier = None
        self.trainer = None
        self.metrics_calculator = None
        self.gate_evaluator = None
    
    def run(self) -> Tuple[Dict, str]:
        """
        Execute full pipeline.
        Returns: (cv_results, gate_result)
        """
        ...
    
    def _setup_output_directories(self):
        """Create output/ and figures/ dirs."""
        Path(self.config['output_dir']).mkdir(exist_ok=True)
        Path(self.config['figures_dir']).mkdir(exist_ok=True)
    
    def _load_data(self) -> Tuple[np.ndarray, np.ndarray, List[str], List[str]]:
        """Load and prepare data. Returns: (X, y, feature_names, benchmark_ids)"""
        ...
    
    def _train_models(
        self, 
        X: np.ndarray, 
        y: np.ndarray
    ) -> Tuple[Dict, Dict]:
        """Train models. Returns: (cv_results, baseline_results)"""
        ...
    
    def _evaluate_results(
        self, 
        cv_results: Dict,
        baseline_results: Dict
    ) -> Dict:
        """Compute metrics. Returns: metrics dict"""
        ...
    
    def _determine_gate(self, metrics: Dict) -> str:
        """Determine gate result. Returns: "PASS" | "PARTIAL" | "FAIL" """
        ...
    
    def _generate_visualizations(
        self, 
        cv_results: Dict, 
        metrics: Dict,
        X: np.ndarray,
        y: np.ndarray,
        feature_names: List[str]
    ):
        """Generate all figures."""
        ...
    
    def _save_results(
        self, 
        cv_results: Dict, 
        metrics: Dict, 
        gate_result: str
    ):
        """Save JSON results and gate decision."""
        ...


def main():
    """Entry point."""
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
        'partial_accuracy_threshold': 0.30,
        'partial_gap_threshold': 0.25,
        'nan_threshold': 0.7,
        'output_dir': './output',
        'figures_dir': '../figures'
    }
    
    orchestrator = ExperimentOrchestrator(config)
    cv_results, gate_result = orchestrator.run()
    
    print(f"\n{'='*60}")
    print(f"Gate Result: {gate_result}")
    print(f"{'='*60}")
    
    return 0 if gate_result == "PASS" else 1
```

### Pseudo-code

```
run():
    1. _setup_output_directories()
    2. X, y, feature_names, benchmark_ids = _load_data()
    3. cv_results, baseline_results = _train_models(X, y)
    4. metrics = _evaluate_results(cv_results, baseline_results)
    5. gate_result = _determine_gate(metrics)
    6. _generate_visualizations(cv_results, metrics, X, y, feature_names)
    7. _save_results(cv_results, metrics, gate_result)
    8. return cv_results, gate_result

_load_data():
    preprocessor = DataPreprocessor(
        h_e1_path=config['h_e1_data_path'],
        h_m1_code_path=config['h_m1_code_path']
    )
    X, y, feature_names, benchmark_ids = preprocessor.load_and_prepare(
        nan_threshold=config['nan_threshold']
    )
    print(f"✓ Loaded data: X={X.shape}, y={y.shape}")
    return X, y, feature_names, benchmark_ids

_train_models(X, y):
    # Initialize models
    baseline_model = BaselineModel(random_state=config['random_state'])
    meta_classifier = MetaClassifier(
        n_estimators=config['n_estimators'],
        max_depth=config['max_depth'],
        min_samples_split=config['min_samples_split'],
        min_samples_leaf=config['min_samples_leaf'],
        random_state=config['random_state']
    )
    
    # Run CV
    trainer = CrossValidationTrainer(
        model=meta_classifier,
        baseline_model=baseline_model,
        n_folds=config['n_folds'],
        random_state=config['random_state']
    )
    cv_results = trainer.run_cv(X, y)
    
    # Train baseline on full data for comparison
    baseline_model.fit(X, y)
    baseline_results = {'model': baseline_model}
    
    return cv_results, baseline_results

_evaluate_results(cv_results, baseline_results):
    calc = MetricsCalculator()
    cv_accuracy = calc.compute_cv_accuracy(cv_results)
    gen_gap = calc.compute_generalization_gap(cv_results)
    baseline_acc = np.mean(cv_results['baseline_scores'])
    baseline_delta = calc.compute_baseline_delta(cv_accuracy, baseline_acc)
    
    return {
        'cv_accuracy': cv_accuracy,
        'generalization_gap': gen_gap,
        'baseline_accuracy': baseline_acc,
        'baseline_delta': baseline_delta
    }

_determine_gate(metrics):
    evaluator = GateEvaluator(
        accuracy_threshold=config['accuracy_threshold'],
        gap_threshold=config['gap_threshold'],
        partial_accuracy_threshold=config['partial_accuracy_threshold'],
        partial_gap_threshold=config['partial_gap_threshold']
    )
    return evaluator.evaluate(
        cv_accuracy=metrics['cv_accuracy'],
        generalization_gap=metrics['generalization_gap']
    )

_save_results(cv_results, metrics, gate_result):
    output_dir = Path(config['output_dir'])
    with open(output_dir / 'cv_results.json', 'w') as f:
        json.dump({
            'cv_scores': cv_results['cv_scores'],
            'train_scores': cv_results['train_scores'],
            'baseline_scores': cv_results['baseline_scores']
        }, f, indent=2)
    
    with open(output_dir / 'metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    with open(output_dir / 'gate_result.txt', 'w') as f:
        f.write(gate_result)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-9-1 | Pipeline Integration | Connect all modules with error handling and logging |
| L-9-2 | Result Serialization | Save CV results, metrics, and gate decision to files |

---

## External Dependencies API (H-M1)

### API Signatures (From Actual Code)

The following APIs are imported from h-m1 code. Signatures verified from actual implementation:

```python
# From: h-m1/code/src/feature_computer.py (ACTUAL CODE)
class Tier1FeatureComputer:
    @staticmethod
    def compute_features(benchmarks: List[Dict]) -> pd.DataFrame:
        """
        Compute universal features.
        benchmarks: List[Dict] length 63
        Returns: DataFrame (63, 4) with columns:
            - sample_size
            - dimensionality
            - num_classes
            - class_imbalance
        Values: float or NaN (no mock defaults)
        """
        ...

class Tier2FeatureComputer:
    @staticmethod
    def compute_features(benchmarks: List[Dict]) -> pd.DataFrame:
        """
        Compute domain-specific features.
        benchmarks: List[Dict] length 63
        Returns: DataFrame (63, ~6) with domain-specific columns:
            Vision: image_resolution, channel_count
            NLP: sequence_length, vocabulary_size
            Tabular: feature_variance, categorical_ratio
            Graph: edge_density, avg_degree
        Values: float or NaN (no mock defaults)
        """
        ...


# From: h-m1/code/src/data_loader.py (ACTUAL CODE)
class BenchmarkDataLoader:
    def __init__(self, data_path: str):
        """
        data_path: Path to benchmarks_collection.jsonl
        Raises FileNotFoundError if path invalid
        """
        ...
    
    def load_benchmarks(self) -> List[Dict]:
        """
        Load JSONL records.
        Returns: List[Dict] length 63
        Each dict contains:
            - benchmark_id: str
            - dataset_name: str
            - domain: str
            - sample_size: int | None
            - dimensionality: int | list | None
            - num_classes: str | int | None
            - method_rankings: Dict[str, Dict]
                Structure: {
                    "MethodName": {
                        "family": "Linear" | "Polynomial" | "RNN" | "Augmentation",
                        "ranking_percentile": float (0-100)
                    }
                }
        """
        ...
    
    def extract_method_rankings(self, benchmarks: List[Dict]) -> pd.DataFrame:
        """
        Extract method family rankings.
        benchmarks: List[Dict]
        Returns: DataFrame (63, 4) with columns: Linear, Polynomial, RNN, Augmentation
        Values: float (0-100) or NaN
        """
        ...
```

**Verified from:** `/workspace/TEST_scope/docs/youra_research/h-m1/code/src/` (actual implementation)

**Critical Notes:**
1. `num_classes` field may be string in JSONL, needs int conversion
2. `dimensionality` can be int, list, or string (e.g., "32x32x3")
3. All feature computation returns NaN for missing data (no fallbacks)
4. Method rankings nested structure: `method_rankings[method_name]['family']` and `['ranking_percentile']`

---

## Error Handling Strategy

### Data Validation

```python
def validate_loaded_data(X: np.ndarray, y: np.ndarray):
    """Validate shapes and completeness."""
    assert X.shape[0] == 63, f"Expected 63 benchmarks, got {X.shape[0]}"
    assert X.shape[1] >= 4, f"Expected >=4 features, got {X.shape[1]}"
    assert len(y) == 63, f"Expected 63 labels, got {len(y)}"
    assert set(y) == {0, 1, 2, 3}, f"Invalid label values: {set(y)}"
    
    # Check for NaN in final X (should be removed by preprocessing)
    nan_count = np.isnan(X).sum()
    if nan_count > 0:
        print(f"WARNING: {nan_count} NaN values in final X matrix")
```

### CV Failure Handling

```python
# In CrossValidationTrainer.run_cv()
try:
    fold_results = _train_fold(X_train, y_train, X_test, y_test)
    cv_scores.append(fold_results['test_acc'])
except Exception as e:
    print(f"ERROR: Fold {fold_idx} failed - {e}")
    cv_scores.append(0.0)  # Record failure as zero accuracy
```

---

## Validation Criteria

### Gate Decision Logic

```python
# From GateEvaluator.evaluate()
if cv_accuracy > 0.35 and generalization_gap < 0.20:
    gate_result = "PASS"
    print("✓ PASS: 50-60 datasets sufficient for meta-learning")
elif cv_accuracy >= 0.30 and generalization_gap < 0.25:
    gate_result = "PARTIAL"
    print("⚠ PARTIAL: Limited learning detected")
else:
    gate_result = "FAIL"
    print("✗ FAIL: Insufficient data or no learnable patterns")
```

### Success Thresholds

| Metric | PASS | PARTIAL | FAIL |
|--------|------|---------|------|
| CV Accuracy | >35% | 30-35% | <30% |
| Generalization Gap | <20% | 20-25% | >25% |
| Baseline Delta | >5% | >0% | N/A |

---

## Implementation Notes

### Execution Order

1. Install: `pip install scikit-learn pandas numpy matplotlib seaborn`
2. Run: `cd code && python run_experiment.py`
3. Expected runtime: <5 minutes total

### STANDARD Tier Constraints

- Configuration: Hardcoded in `main()` (no YAML)
- Logging: Print statements only
- Testing: Manual validation (no pytest)
- Deterministic: Fixed random_state=42 throughout

### Expected Output

```
Loading 63 benchmarks from H-E1...
✓ Computed Tier 1 features for 63 benchmarks (NO MOCK FALLBACKS)
  sample_size: 49/63 real values (77.8%)
  dimensionality: 52/63 real values (82.5%)
  num_classes: 58/63 real values (92.1%)
  class_imbalance: 63/63 real values (100.0%)
✓ Computed Tier 2 features: ['image_resolution', 'channel_count', ...]
Keeping 7/10 features after NaN filtering
✓ Loaded data: X=(63, 7), y=(63,)

Training baseline: 13 folds...
  Baseline CV Accuracy: 28.3% ± 5.2%

Training meta-classifier: 13 folds...
Fold 1: Train=0.828, Test=0.400
Fold 2: Train=0.845, Test=0.400
...
Fold 13: Train=0.810, Test=0.200

✓ CV Accuracy: 38.5% ± 6.1%
✓ Generalization Gap: 42.3%
✓ Baseline Delta: 10.2%

Gate Evaluation:
  CV Accuracy: 38.5% > 35.0% ✓
  Generalization Gap: 42.3% > 20.0% ✗
  Result: FAIL (severe overfitting)

✓ Figures saved to ../figures/
✓ Results saved to ./output/

============================================================
Gate Result: FAIL
============================================================
```

---

**Document Status:** Ready for Implementation (Phase 4)
**Next Phase:** Phase 4 Coder - Implement meta-classifier training pipeline
**Total Subtasks Used:** 5/4 (L-5-1, L-8-1, L-8-2, L-9-1, L-9-2)

**Note:** Subtask count slightly exceeds budget (5 vs 4) due to essential complexity in CV iteration, visualization, and orchestration. All are necessary for functioning pipeline.
