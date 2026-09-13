# Configuration Document: H-M2 Meta-Classifier Training Sufficiency

**Date:** 2026-07-13
**Hypothesis:** H-M2 (MECHANISM)
**Type:** Random Forest Meta-Learning with Cross-Validation
**Tier:** STANDARD (Sklearn-based classification pipeline)

Applied: sklearn RandomForestClassifier small-data defaults, leave-k-out CV pattern

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis
**Status:** Config patterns verified from h-m1 code
**Config Files Found:** `h-m1/code/run_analysis.py` (hardcoded dict in main() function)
**Pattern Used:** Hardcoded dict (lines 191-197 in h-m1 run_analysis.py)

**Key Findings:**
- h-m1 uses hardcoded dict in main() function
- Pattern: Single CONFIG dict with all parameters
- Output: JSON files to ./output/, figures to ../figures/
- No dataclass pattern found in h-m1 codebase
- Module imports via sys.path manipulation

---

## Inherited Configuration (Base Hypothesis)

### H-M1 Config Pattern (From Actual Code)

```python
# From: h-m1/code/run_analysis.py (lines 191-197) - ACTUAL CODE
config = {
    'data_path': './data/h-e1/benchmarks_collection.jsonl',
    'output_dir': './output',
    'figures_dir': '../figures',
    'rho_threshold': 0.3,
    'alpha': 0.05
}
```

**Verified from**: `h-m1/code/run_analysis.py` (actual implementation)

### H-M1 Module Reuse

H-M2 reuses feature computation from h-m1:

```python
# From: h-m1/code/run_analysis.py (lines 13-18)
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data_loader import BenchmarkDataLoader
from feature_computer import Tier1FeatureComputer, Tier2FeatureComputer
```

**H-M2 adaptation:**
```python
# H-M2 imports h-m1 modules via relative path
sys.path.append('../h-m1/code')
from src.data_loader import BenchmarkDataLoader
from src.feature_computer import Tier1FeatureComputer
```

---

## Complete Configuration (Hardcoded Dict)

```python
# Main configuration for run_experiment.py
CONFIG = {
    # Data sources
    'h_e1_data_path': '../h-e1/code/output/benchmarks_collection.jsonl',
    'h_m1_code_path': '../h-m1/code',
    
    # Random Forest hyperparameters
    'n_estimators': 100,          # Ensemble size (sklearn default)
    'max_depth': 10,              # Constrained for small-data robustness
    'min_samples_split': 5,       # Prevent overfitting on 58 training samples
    'min_samples_leaf': 2,        # Minimum leaf size for generalization
    'criterion': 'gini',          # Standard for multi-class (sklearn default)
    'max_features': 'sqrt',       # Reduce tree correlation (sklearn default)
    'random_state': 42,           # Reproducibility
    
    # Cross-validation
    'n_folds': 13,                # 63 benchmarks ÷ 5 = 12.6 → 13 folds
    
    # Gate thresholds
    'accuracy_threshold': 0.35,   # PASS threshold from PRD
    'gap_threshold': 0.20,        # Max acceptable generalization gap
    'partial_accuracy_threshold': 0.30,
    'partial_gap_threshold': 0.25,
    
    # Data preprocessing
    'nan_threshold': 0.7,         # Remove features with >70% missing data
    'normalize_method': 'zscore', # Z-score normalization for features
    
    # Output paths (consistent with h-m1)
    'output_dir': './output',
    'figures_dir': '../figures',
    
    # Visualization
    'figure_dpi': 300,
    'figure_format': 'png'
}
```

---

## Configuration Rationale

### Random Forest Hyperparameters

**n_estimators=100**
- Standard ensemble size for stable predictions
- Balances computational cost vs accuracy
- Sufficient for 63-sample dataset

**max_depth=10**
- Prevents overfitting on small training sets (58 samples per fold)
- Deeper trees would memorize training data

**min_samples_split=5**
- Requires 5+ samples to create split
- Critical for 58-sample training sets
- Prevents leaf fragmentation

**min_samples_leaf=2**
- Forces leaves to represent 2+ samples
- Reduces overfitting risk
- Ensures predictions based on multiple examples

**criterion='gini', max_features='sqrt'**
- Standard sklearn defaults for multi-class classification

### Cross-Validation Strategy

**n_folds=13 (leave-5-out)**
- 63 total benchmarks ÷ 5 test per fold = 12.6 → 13 folds
- Test fold size: 5 benchmarks
- Training fold size: 58 benchmarks
- Mimics deployment scenario: predict on 5 new datasets

### Gate Thresholds

**accuracy_threshold=0.35**
- PASS threshold from PRD (FR4)
- Above 4-class random baseline (~25%)
- Indicates learning beyond majority class

**gap_threshold=0.20**
- Max acceptable train-test gap
- Gap >20% indicates severe overfitting

**partial thresholds (0.30, 0.25)**
- Partial success criteria from PRD
- Indicates limited but detectable learning

### Preprocessing

**nan_threshold=0.7**
- Remove features with >70% missing data
- Ensures features based on sufficient samples
- Expected: 4-10 features remain after filtering

**normalize_method='zscore'**
- Standardizes features to zero mean, unit variance
- Required for fair feature importance comparison
- Prevents dominance by large-scale features

---

## Usage Example (Phase 4 Implementation)

```python
# code/run_experiment.py
import sys
from pathlib import Path

# Add h-m1 code to path for feature reuse
sys.path.append('../h-m1/code')

from src.data_loader import BenchmarkDataLoader
from src.feature_computer import Tier1FeatureComputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import KFold
from sklearn.dummy import DummyClassifier
import numpy as np
import pandas as pd


def main():
    """Main experiment orchestrator."""
    # Configuration
    config = CONFIG  # Use dict defined above
    
    # Step 1: Load data
    print("Loading benchmarks from h-e1...")
    sys.path.append(config['h_m1_code_path'])
    loader = BenchmarkDataLoader(config['h_e1_data_path'])
    benchmarks = loader.load_benchmarks()
    print(f"Loaded {len(benchmarks)} benchmarks")
    
    # Step 2: Compute features
    print("Computing Tier 1 features...")
    features_df = Tier1FeatureComputer.compute_features(benchmarks)
    
    # Remove sparse features
    coverage = features_df.notna().mean()
    keep_features = coverage[coverage > (1 - config['nan_threshold'])].index
    features_df = features_df[keep_features]
    print(f"Retained {len(keep_features)} features after NaN filtering")
    
    # Normalize features
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X = scaler.fit_transform(features_df.values)
    
    # Step 3: Extract target labels
    rankings_df = loader.extract_method_rankings(benchmarks)
    y = rankings_df.idxmax(axis=1).values  # Top-1 method family
    print(f"Target classes: {np.unique(y)}")
    
    # Step 4: Train models with cross-validation
    print(f"\nTraining with {config['n_folds']}-fold CV...")
    
    # Initialize models
    rf_model = RandomForestClassifier(
        n_estimators=config['n_estimators'],
        max_depth=config['max_depth'],
        min_samples_split=config['min_samples_split'],
        min_samples_leaf=config['min_samples_leaf'],
        criterion=config['criterion'],
        max_features=config['max_features'],
        random_state=config['random_state']
    )
    
    baseline_model = DummyClassifier(
        strategy='most_frequent',
        random_state=config['random_state']
    )
    
    # Cross-validation
    kfold = KFold(n_splits=config['n_folds'], shuffle=True, random_state=config['random_state'])
    
    cv_results = {
        'rf_train_scores': [],
        'rf_test_scores': [],
        'baseline_test_scores': []
    }
    
    for fold_idx, (train_idx, test_idx) in enumerate(kfold.split(X), 1):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Train and evaluate Random Forest
        rf_model.fit(X_train, y_train)
        train_acc = rf_model.score(X_train, y_train)
        test_acc = rf_model.score(X_test, y_test)
        
        # Train and evaluate Baseline
        baseline_model.fit(X_train, y_train)
        baseline_acc = baseline_model.score(X_test, y_test)
        
        cv_results['rf_train_scores'].append(train_acc)
        cv_results['rf_test_scores'].append(test_acc)
        cv_results['baseline_test_scores'].append(baseline_acc)
        
        print(f"Fold {fold_idx:2d}: Train={train_acc:.3f}, Test={test_acc:.3f}, Gap={train_acc - test_acc:.3f}")
    
    # Step 5: Compute metrics
    cv_accuracy = np.mean(cv_results['rf_test_scores'])
    generalization_gap = np.mean(np.array(cv_results['rf_train_scores']) - np.array(cv_results['rf_test_scores']))
    baseline_accuracy = np.mean(cv_results['baseline_test_scores'])
    
    print(f"\n{'=' * 70}")
    print(f"RESULTS")
    print(f"{'=' * 70}")
    print(f"Baseline CV Accuracy: {baseline_accuracy:.3f}")
    print(f"RF CV Accuracy:      {cv_accuracy:.3f}")
    print(f"Generalization Gap:  {generalization_gap:.3f}")
    print()
    
    # Step 6: Gate evaluation
    if cv_accuracy > config['accuracy_threshold'] and generalization_gap < config['gap_threshold']:
        gate_result = "PASS"
    elif cv_accuracy >= config['partial_accuracy_threshold'] and generalization_gap < config['partial_gap_threshold']:
        gate_result = "PARTIAL"
    else:
        gate_result = "FAIL"
    
    print(f"{'=' * 70}")
    print(f"GATE RESULT: {gate_result}")
    print(f"{'=' * 70}")
    
    # Step 7: Save results
    output_dir = Path(config['output_dir'])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    import json
    with open(output_dir / 'metrics.json', 'w') as f:
        json.dump({
            'cv_accuracy': float(cv_accuracy),
            'generalization_gap': float(generalization_gap),
            'baseline_accuracy': float(baseline_accuracy),
            'gate_result': gate_result
        }, f, indent=2)
    
    print(f"\nResults saved to {output_dir}")
    
    return 0 if gate_result != "FAIL" else 1


if __name__ == '__main__':
    sys.exit(main())
```

---

## Output File Specifications

```python
OUTPUT_SCHEMA = {
    'output/cv_results.json': {
        'fold_results': [
            {
                'fold': int,
                'train_accuracy': float,
                'test_accuracy': float,
                'baseline_accuracy': float
            }
        ]
    },
    
    'output/metrics.json': {
        'cv_accuracy': float,
        'generalization_gap': float,
        'baseline_accuracy': float,
        'baseline_delta': float,
        'gate_result': str  # "PASS" | "PARTIAL" | "FAIL"
    },
    
    'output/feature_importances.csv': {
        'columns': ['feature', 'importance'],
        'sorted_by': 'importance descending'
    },
    
    'figures/gate_metrics.png': {
        'type': 'bar chart',
        'x_axis': ['Baseline', 'Target (35%)', 'CV Accuracy'],
        'mandatory': True
    }
}
```

---

## Self-Validation Checklist

- [x] ONE format only (hardcoded dict, consistent with h-m1)
- [x] No ASCII diagrams
- [x] KB search results noted ("Applied: sklearn RandomForestClassifier small-data defaults")
- [x] Rationale only for non-standard values (max_depth, min_samples_split, min_samples_leaf)
- [x] No subtask decomposition (budget = 0 per mission)
- [x] Total length < 400 lines
- [x] Codebase Analysis section included
- [x] Inherited Configuration section with verified h-m1 patterns
- [x] Field names verified from actual h-m1 code (run_analysis.py lines 191-197)
- [x] Ready-to-use Python code (copy-paste ready for Phase 4)

---

**Document Status:** Ready for Implementation (Phase 4)
**Next Step:** Phase 4 Coder Agent - Implement meta-classifier training pipeline with this configuration
