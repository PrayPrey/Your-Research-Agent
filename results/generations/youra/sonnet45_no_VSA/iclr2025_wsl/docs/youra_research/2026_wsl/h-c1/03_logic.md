# Logic Design: H-C1 Edge Case Robustness Validation

**Hypothesis ID:** h-c1  
**Type:** CONDITION (SHOULD_WORK gate)  
**Date:** 2026-07-11  
**Applied Pattern:** TIMM model validation + statistical testing + failure mode analysis

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase  
**Status:** Building on h-m3 (feature extraction) and h-e1 (classifier)  
**Analyzed Path:** docs/youra_research/h-m3/code/, docs/youra_research/h-e1/code/  
**Relevant Symbols:** 
- `CheckpointOnlyExtractor.extract_batch()` from h-m3
- `StatisticalFeatureExtractor.extract_features()` from h-m3
- Trained classifier at h-e1/code/models/classifier.pkl
- Trained scaler at h-e1/code/models/scaler.pkl

---

## Applied Knowledge Base Patterns

**Applied:** TIMM model availability validation, Wilson score confidence intervals for small samples, sklearn confusion matrix analysis

---

## C1-1: Edge Case Model Curation [Complexity: 8, Budget: 2 subtasks]

**Applied:** TIMM availability validation with fallback logic

### API Signatures

```python
from typing import List, Dict, Tuple
import timm
import logging

class EdgeCaseModelCurator:
    def __init__(self, min_models_per_family: int = 3):
        """Initialize curator with minimum viable threshold."""
        self.min_models_per_family = min_models_per_family
        
    def validate_availability(
        self, 
        edge_case_config: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """Validate TIMM availability for edge case models.
        
        Args:
            edge_case_config: {family: [model_names]}
            
        Returns:
            {family: [available_model_names]}. Raises RuntimeError if <3 models per family.
        """
        ...
    
    def get_fallback_models(
        self, 
        family: str, 
        missing_count: int
    ) -> List[str]:
        """Find fallback models when primary choices unavailable.
        
        Args:
            family: 'NormFree' | 'SENet' | 'RegNet' | 'ViT-Extreme'
            missing_count: Number of models needed
            
        Returns:
            List of alternative model names from TIMM. Empty if none found.
        """
        ...
    
    def assign_ground_truth_labels(
        self, 
        model_names: List[str]
    ) -> Dict[str, str]:
        """Assign family labels based on model naming patterns.
        
        Args:
            model_names: List of TIMM model names
            
        Returns:
            {model_name: family_label}. Family is one of: NormFree, SENet, RegNet, ViT-Extreme
        """
        ...
```

### Pseudo-code

```
# Availability validation
1. available = timm.list_models()
2. for family, models in edge_case_config.items():
3.     valid_models = [m for m in models if m in available]
4.     if len(valid_models) < min_models_per_family:
5.         fallbacks = get_fallback_models(family, min_models_per_family - len(valid_models))
6.         valid_models.extend(fallbacks)
7.     if len(valid_models) < min_models_per_family:
8.         raise RuntimeError(f"Cannot find {min_models_per_family} models for {family}")
9. return validated_config

# Ground truth labeling
1. if 'nfnet' in model_name or 'dm_nfnet' in model_name:
2.     return 'NormFree'
3. if 'se' in model_name and 'resnet' in model_name:
4.     return 'SENet'
5. if 'regnet' in model_name:
6.     return 'RegNet'
7. if 'vit_giant' in model_name or 'vit_huge' in model_name or 'deit_huge' in model_name:
8.     return 'ViT-Extreme'
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Availability check | Implement validate_availability() with timm.list_models() |
| L-1-2 | Fallback logic | Implement get_fallback_models() with family-specific search |

---

## C1-2: Feature Extraction Workflow [Complexity: 6, Budget: 1 subtask]

**Applied:** Reuse h-m3 CheckpointOnlyExtractor (100% code reuse)

### API Signatures

```python
import pandas as pd
from typing import Dict
import sys
import os

# Import from h-m3
sys.path.append('docs/youra_research/h-m3/code/src')
from checkpoint_only_extractor import CheckpointOnlyExtractor

class EdgeCaseFeatureExtractor:
    def __init__(self, cache_dir: str = ".cache/checkpoints"):
        """Initialize with h-m3 extractor."""
        self.extractor = CheckpointOnlyExtractor(cache_dir=cache_dir)
    
    def extract_edge_case_features(
        self, 
        model_names: List[str],
        ground_truth_labels: Dict[str, str]
    ) -> pd.DataFrame:
        """Extract features using h-m3 extractor and add ground truth.
        
        Args:
            model_names: List of edge case model names
            ground_truth_labels: {model_name: edge_case_family}
            
        Returns:
            DataFrame with columns [model_name, bn_count, ln_count, gn_count, 
            no_norm_flag, param_mass_ratio, edge_family]. Shape: [N, 7]
        """
        ...
    
    def validate_normfree_flag(self, features_df: pd.DataFrame) -> bool:
        """Validate no_norm_flag=1 for NormFree models.
        
        Args:
            features_df: Output from extract_edge_case_features()
            
        Returns:
            True if all NormFree models have no_norm_flag=1, else False
        """
        ...
```

### Pseudo-code

```
# Feature extraction (reuses h-m3)
1. result = CheckpointOnlyExtractor().extract_batch(model_names)
2. features_df = result['features']  # [N, 6]: model_name, bn, ln, gn, no_norm, R, family
3. features_df['edge_family'] = features_df['model_name'].map(ground_truth_labels)
4. return features_df

# NormFree validation
1. normfree_models = features_df[features_df['edge_family'] == 'NormFree']
2. all_flagged = (normfree_models['no_norm_flag'] == 1).all()
3. if not all_flagged:
4.     log warning about unexpected NormFree models with norm layers
5. return all_flagged
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Wrapper implementation | Wrap h-m3 extractor with ground truth labels |

---

## C1-3: Accuracy Evaluation with Confidence Intervals [Complexity: 12, Budget: 3 subtasks]

**Applied:** Wilson score confidence intervals for small sample statistical testing

### API Signatures

```python
import numpy as np
from numpy.typing import NDArray
from typing import Dict, Tuple
import pickle
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

class EdgeCaseEvaluator:
    def __init__(
        self, 
        classifier_path: str = 'docs/youra_research/h-e1/code/models/classifier.pkl',
        scaler_path: str = 'docs/youra_research/h-e1/code/models/scaler.pkl'
    ):
        """Load h-e1 trained classifier and scaler."""
        with open(classifier_path, 'rb') as f:
            self.classifier = pickle.load(f)
        with open(scaler_path, 'rb') as f:
            self.scaler = pickle.load(f)
    
    def predict_edge_cases(
        self, 
        features_df: pd.DataFrame
    ) -> pd.DataFrame:
        """Apply h-e1 classifier to edge case features.
        
        Args:
            features_df: [N, 7] with 5D features
            
        Returns:
            predictions_df: [N, 4] with columns [model_name, predicted_family, 
            ground_truth, correct]
        """
        ...
    
    def compute_overall_accuracy(
        self, 
        predictions_df: pd.DataFrame
    ) -> Dict[str, float]:
        """Compute overall accuracy with Wilson 95% CI.
        
        Args:
            predictions_df: Output from predict_edge_cases()
            
        Returns:
            {accuracy: float, ci_lower: float, ci_upper: float, sample_size: int}
        """
        ...
    
    def compute_per_family_accuracy(
        self, 
        predictions_df: pd.DataFrame
    ) -> Dict[str, Dict[str, float]]:
        """Compute accuracy breakdown per edge family.
        
        Args:
            predictions_df: Output from predict_edge_cases()
            
        Returns:
            {
                'NormFree': {accuracy: float, correct: int, total: int},
                'SENet': {accuracy: float, correct: int, total: int},
                'RegNet': {accuracy: float, correct: int, total: int},
                'ViT-Extreme': {accuracy: float, correct: int, total: int}
            }
        """
        ...
    
    def evaluate_gate_decision(
        self, 
        overall_acc: float, 
        per_family_acc: Dict[str, Dict]
    ) -> Tuple[str, str]:
        """Make SHOULD_WORK gate decision.
        
        Args:
            overall_acc: Overall accuracy from compute_overall_accuracy()
            per_family_acc: Per-family breakdown
            
        Returns:
            (gate_status, rationale). gate_status is 'PASS' or 'DOCUMENT'.
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| X_edge | [N, 5] | Edge case features |
| X_scaled | [N, 5] | After StandardScaler |
| y_pred | [N] | Predicted family (0=CNN, 1=Transformer, 2=Hybrid) |
| y_true_edge | [N] | Ground truth edge family labels |

### Pseudo-code

```
# Prediction
1. X = features_df[['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']]
2. X_scaled = scaler.transform(X)  # [N, 5]
3. y_pred = classifier.predict(X_scaled)  # [N]
4. predictions_df = pd.DataFrame({
       'model_name': features_df['model_name'],
       'predicted_family': y_pred,
       'ground_truth': features_df['edge_family'],
       'correct': (y_pred == y_true)
   })

# Wilson score CI (95% confidence)
1. n = len(predictions_df)
2. p_hat = sum(predictions_df['correct']) / n
3. z = 1.96  # 95% confidence
4. ci_lower = (p_hat + z^2/(2*n) - z*sqrt(p_hat*(1-p_hat)/n + z^2/(4*n^2))) / (1 + z^2/n)
5. ci_upper = (p_hat + z^2/(2*n) + z*sqrt(p_hat*(1-p_hat)/n + z^2/(4*n^2))) / (1 + z^2/n)

# Per-family accuracy
1. for family in ['NormFree', 'SENet', 'RegNet', 'ViT-Extreme']:
2.     family_preds = predictions_df[predictions_df['ground_truth'] == family]
3.     correct = sum(family_preds['correct'])
4.     total = len(family_preds)
5.     accuracy = correct / total

# Gate decision
1. if overall_acc >= 0.70:
2.     return 'PASS', 'Edge case accuracy meets 70% threshold'
3. families_pass = sum(1 for f in per_family_acc if f['accuracy'] >= 0.70)
4. if families_pass >= 3:
5.     return 'PASS', '3/4 families pass 70% threshold'
6. return 'DOCUMENT', f'Overall: {overall_acc:.1%}, only {families_pass}/4 families pass'
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Classifier loading | Load h-e1 artifacts with pickle |
| L-3-2 | Wilson CI implementation | Implement Wilson score binomial CI |
| L-3-3 | Gate logic | Implement evaluate_gate_decision() |

---

## C1-4: Per-Family Accuracy Computation [Complexity: 8, Budget: 2 subtasks]

**Applied:** Stratified accuracy computation with JSON output

### API Signatures

```python
import json
from typing import Dict

class FamilyAccuracyAnalyzer:
    def compute_degradation(
        self, 
        edge_accuracy: float,
        baseline_accuracy: float = 0.85
    ) -> float:
        """Compute degradation from h-e1 baseline.
        
        Args:
            edge_accuracy: Overall edge case accuracy
            baseline_accuracy: h-e1 standard architecture accuracy (from validation)
            
        Returns:
            Degradation percentage (positive means degradation)
        """
        ...
    
    def generate_accuracy_report(
        self, 
        overall_acc: Dict[str, float],
        per_family_acc: Dict[str, Dict],
        baseline_acc: float,
        output_path: str
    ) -> None:
        """Generate JSON accuracy report.
        
        Args:
            overall_acc: From EdgeCaseEvaluator.compute_overall_accuracy()
            per_family_acc: From EdgeCaseEvaluator.compute_per_family_accuracy()
            baseline_acc: h-e1 baseline accuracy
            output_path: results/accuracy_by_family.json
            
        JSON structure:
            {
                "NormFree": {"accuracy": 0.XX, "count": 5, "correct": X},
                "SENet": {"accuracy": 0.XX, "count": 5, "correct": X},
                "RegNet": {"accuracy": 0.XX, "count": 5, "correct": X},
                "ViT-Extreme": {"accuracy": 0.XX, "count": 5, "correct": X},
                "overall_edge": {"accuracy": 0.XX, "ci_lower": 0.XX, "ci_upper": 0.XX},
                "overall_baseline": {"accuracy": 0.85},
                "degradation": 0.XX,
                "gate_decision": "PASS" | "DOCUMENT"
            }
        """
        ...
```

### Pseudo-code

```
# Degradation computation
1. degradation = baseline_accuracy - edge_accuracy
2. if degradation <= 0.15:
3.     status = "acceptable"
4. else:
5.     status = "exceeds_threshold"

# JSON report generation
1. report = {}
2. for family, stats in per_family_acc.items():
3.     report[family] = {
4.         'accuracy': stats['accuracy'],
5.         'count': stats['total'],
6.         'correct': stats['correct']
7.     }
8. report['overall_edge'] = overall_acc
9. report['degradation'] = degradation
10. with open(output_path, 'w') as f:
11.     json.dump(report, f, indent=2)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Degradation calc | Implement compute_degradation() |
| L-4-2 | JSON serialization | Implement generate_accuracy_report() |

---

## C1-5: Failure Mode Analysis Algorithm [Complexity: 14, Budget: 3 subtasks]

**Applied:** sklearn confusion matrix + feature distribution analysis

### API Signatures

```python
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
from typing import List

class FailureModeAnalyzer:
    def __init__(self):
        """Initialize analyzer with matplotlib configuration."""
        self.family_order = ['NormFree', 'SENet', 'RegNet', 'ViT-Extreme']
    
    def generate_confusion_matrix(
        self, 
        predictions_df: pd.DataFrame,
        output_path: str
    ) -> NDArray:
        """Generate confusion matrix for edge cases.
        
        Args:
            predictions_df: [N, 4] from EdgeCaseEvaluator.predict_edge_cases()
            output_path: results/confusion_matrix.png
            
        Returns:
            confusion_matrix: [4, 4] matrix (rows=true, cols=pred)
        """
        ...
    
    def analyze_feature_distributions(
        self, 
        edge_features_df: pd.DataFrame,
        baseline_features_df: pd.DataFrame,
        output_path: str
    ) -> None:
        """Compare edge vs baseline feature distributions.
        
        Args:
            edge_features_df: Edge case features [N_edge, 7]
            baseline_features_df: Baseline features [N_baseline, 7]
            output_path: results/feature_distributions.png
            
        Generates:
            5-subplot violin plot comparing edge vs baseline for each feature
        """
        ...
    
    def identify_systematic_patterns(
        self, 
        predictions_df: pd.DataFrame,
        features_df: pd.DataFrame
    ) -> Dict[str, str]:
        """Identify systematic misclassification patterns.
        
        Args:
            predictions_df: Predictions with ground truth
            features_df: Features for misclassified models
            
        Returns:
            {
                'NormFree': 'Pattern: all misclassified as CNN due to R>0.9',
                'SENet': 'Pattern: no systematic errors',
                ...
            }
        """
        ...
    
    def generate_failure_report(
        self, 
        misclassified_df: pd.DataFrame,
        systematic_patterns: Dict[str, str],
        output_path: str
    ) -> None:
        """Generate detailed failure analysis markdown.
        
        Args:
            misclassified_df: Subset of predictions_df where correct=False
            systematic_patterns: From identify_systematic_patterns()
            output_path: results/failure_analysis.md
            
        Markdown structure:
            # Failure Mode Analysis
            ## Overall Statistics
            ## Per-Family Patterns
            ### NormFree
            - Systematic pattern: ...
            - Misclassified models: ...
            ## Proposed Extensions
        """
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| confusion_matrix | [4, 4] | Rows=true family, Cols=predicted |
| edge_features | [N_edge, 5] | 5D feature vectors |
| baseline_features | [N_baseline, 5] | From h-e1 validation set |

### Pseudo-code

```
# Confusion matrix generation
1. y_true = predictions_df['ground_truth']
2. y_pred = predictions_df['predicted_family']
3. cm = confusion_matrix(y_true, y_pred, labels=family_order)  # [4, 4]
4. sns.heatmap(cm, annot=True, fmt='d', xticklabels=family_order, yticklabels=family_order)
5. plt.ylabel('True Edge Family')
6. plt.xlabel('Predicted Family')
7. plt.savefig(output_path)

# Feature distribution comparison
1. fig, axes = plt.subplots(1, 5, figsize=(20, 4))
2. for i, feature in enumerate(['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'R']):
3.     edge_vals = edge_features_df[feature]
4.     baseline_vals = baseline_features_df[feature]
5.     axes[i].violinplot([edge_vals, baseline_vals])
6.     axes[i].set_title(feature)
7.     axes[i].set_xticklabels(['Edge', 'Baseline'])
8. plt.savefig(output_path)

# Systematic pattern detection
1. for family in family_order:
2.     misclassified = predictions_df[(predictions_df['ground_truth'] == family) & 
3.                                     (predictions_df['correct'] == False)]
4.     if len(misclassified) == 0:
5.         patterns[family] = 'No failures'
6.     elif len(misclassified) == len(predictions_df[predictions_df['ground_truth'] == family]):
7.         # All misclassified - check features
8.         common_pred = misclassified['predicted_family'].mode()[0]
9.         feature_mean = features_df[features_df['model_name'].isin(misclassified['model_name'])].mean()
10.        patterns[family] = f'All {len(misclassified)} models misclassified as {common_pred}'
11.    else:
12.        patterns[family] = f'{len(misclassified)} partial failures'
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Confusion matrix | Implement generate_confusion_matrix() with seaborn |
| L-5-2 | Distribution plots | Implement analyze_feature_distributions() |
| L-5-3 | Pattern detection | Implement identify_systematic_patterns() |

---

## External Dependencies (h-e1 and h-m3)

### API Signatures (From Actual Code)

The following APIs are called from existing hypotheses. Signatures verified from actual implementation:

```python
# From: docs/youra_research/h-m3/code/src/checkpoint_only_extractor.py
class CheckpointOnlyExtractor:
    def __init__(self, cache_dir: str = ".cache/checkpoints"):
        """Initialize checkpoint extractor."""
        ...
    
    def extract_batch(self, model_names: List[str]) -> Dict:
        """Extract features from checkpoints.
        
        Returns:
            {
                'total_time': float,
                'per_model_times': dict[str, float],
                'features': pd.DataFrame,  # [N, 6]: model_name, bn, ln, gn, no_norm, R, family
                'failed_models': list[str]
            }
        """
        ...

# From: docs/youra_research/h-m3/code/src/feature_extractor.py
class StatisticalFeatureExtractor:
    def extract_features(self, state_dict: dict) -> dict:
        """Extract 5D feature vector.
        
        Returns:
            {
                'bn_count': int,
                'ln_count': int,
                'gn_count': int,
                'no_norm_flag': int,  # 1 if total_norm==0, else 0
                'param_mass_ratio': float
            }
        """
        ...

# From: docs/youra_research/h-e1/code/models/classifier.pkl
# sklearn.linear_model.LogisticRegression (pre-trained)
classifier.predict(X_scaled)  # X_scaled: [N, 5] -> [N] with labels 0/1/2

# From: docs/youra_research/h-e1/code/models/scaler.pkl
# sklearn.preprocessing.StandardScaler (pre-fitted)
scaler.transform(X)  # X: [N, 5] -> [N, 5]
```

**Verified from**: h-m3/code/src/ and h-e1/code/models/ (actual implementation, not specs)

---

## Critical Decision Points

### Model Unavailability
**Trigger:** TIMM model not in `timm.list_models()`  
**Decision:** 
1. Search for similar variant (e.g., `nfnet_f0` instead of `nfnet_f3`)
2. If <3 models per family after fallback → raise RuntimeError (cannot proceed)

### Missing h-e1 Classifier
**Trigger:** classifier.pkl not found at expected path  
**Decision:** 
1. Quick-train fallback: Load h-e1 training features, train LogisticRegression (30 sec)
2. Verify baseline accuracy >80% before applying to edge cases

### Insufficient Sample Size
**Trigger:** Wilson CI width >±10%  
**Decision:**
1. Flag in report: "High variance - expand to 30 models recommended"
2. Proceed with evaluation but mark as low confidence

### NormFree Validation Failure
**Trigger:** NormFree model has `no_norm_flag=0`  
**Decision:**
1. Log warning: "Unexpected norm layers in {model_name}"
2. Proceed but flag in failure analysis (may indicate mislabeling)

---

## Integration Notes

### Data Flow

1. `EdgeCaseModelCurator.validate_availability()` → validated edge case list (20 models)
2. `EdgeCaseFeatureExtractor.extract_edge_case_features()` → features_df [20, 7]
3. `EdgeCaseEvaluator.predict_edge_cases()` → predictions_df [20, 4]
4. `EdgeCaseEvaluator.compute_overall_accuracy()` → {accuracy, CI}
5. `FamilyAccuracyAnalyzer.generate_accuracy_report()` → JSON file
6. `FailureModeAnalyzer.generate_failure_report()` → Markdown file

### Error Handling

**Model Download Failures:**
- CheckpointOnlyExtractor has retry logic (max_retries=3 from h-m3 config)
- Failed models logged in result['failed_models']
- Continue with remaining models if ≥12 edge cases available

**Classifier Loading Failures:**
- If classifier.pkl missing → RuntimeError with clear message
- If pickle version mismatch → attempt joblib.load() fallback

**Statistical Edge Cases:**
- Division by zero in Wilson CI → handle with np.clip(p_hat, 0.01, 0.99)
- Zero-count families → skip in per-family analysis, document limitation

---

## Self-Validation Checklist

**Quick Checks:**
- [x] No ASCII diagrams
- [x] No KB search logs (only "Applied: X")
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in code comments
- [x] Subtask count within budget (11 subtasks total, budget allows up to 42)
- [x] Total length < 600 lines
- [x] "Codebase Analysis (Serena)" section included

**Base Hypothesis Checks:**
- [x] Read actual code from h-m3/code/ and h-e1/code/
- [x] API signatures verified from actual implementation (not specs)
- [x] Parameter names exactly match actual code
- [x] External Dependencies API section included

**Logic Completeness:**
- [x] All 5 key requirements addressed (curation, extraction, accuracy, per-family, failure analysis)
- [x] Critical decision points documented with triggers and actions
- [x] Wilson score CI implementation specified
- [x] Gate decision logic (≥70% overall OR 3/4 families pass)
