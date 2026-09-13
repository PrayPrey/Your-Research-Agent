# Logic Design: H-E1 Statistical Features Sufficiency

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE (PoC)  
**Date:** 2026-07-11  
**Applied Pattern:** TIMM checkpoint loading + sklearn pipeline

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** New implementation from scratch (no existing code to analyze)  
**Analyzed Path:** N/A (verified docs/youra_research/h-e1 has no .py files)  
**Relevant Symbols:** None - new implementation

---

## Applied Knowledge Base Patterns

**Applied:** PyTorch state_dict loading pattern, sklearn StandardScaler + LogisticRegression pipeline pattern

---

## E1-2: Data Pipeline [Complexity: 12, Budget: 2 subtasks]

**Applied:** TIMM model loading + PyTorch state_dict parsing

### API Signatures

```python
from typing import List, Tuple, Dict, Optional
import torch
from torch import Tensor
import pandas as pd
import re

class TIMMDataLoader:
    def __init__(self, model_families: Dict[str, List[str]], random_seed: int = 42):
        """Initialize data loader with model family specifications."""
        self.model_families = model_families
        self.random_seed = random_seed
        
    def download_models(self) -> List[Tuple[str, str, Dict[str, Tensor]]]:
        """Download pretrained models.
        
        Returns:
            List of (model_name, family_label, state_dict). Length=60.
        """
        ...
    
    def create_splits(
        self, 
        data: List[Tuple[str, str, Dict]], 
        test_size: float = 0.3
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Create stratified train/val split.
        
        Args:
            data: Output from download_models()
            test_size: Validation split ratio
            
        Returns:
            (train_df, val_df) with columns [model_name, family, bn_count, ln_count, 
             gn_count, no_norm_flag, param_mass_ratio]
        """
        ...
    
    def save_features(
        self, 
        train_df: pd.DataFrame, 
        val_df: pd.DataFrame, 
        output_dir: str
    ) -> None:
        """Save feature DataFrames to CSV."""
        ...


class StatisticalFeatureExtractor:
    def __init__(self):
        """Initialize feature extractor with normalization patterns."""
        self.norm_patterns = {
            'bn': re.compile(r'bn|batch_norm|batchnorm', re.IGNORECASE),
            'ln': re.compile(r'ln|layer_norm|layernorm', re.IGNORECASE),
            'gn': re.compile(r'gn|group_norm|groupnorm', re.IGNORECASE)
        }
        self.head_keywords = ['head', 'fc', 'classifier']
    
    def extract_features(self, state_dict: Dict[str, Tensor]) -> Dict[str, float]:
        """Extract 5 statistical features from state_dict.
        
        Args:
            state_dict: PyTorch model checkpoint
            
        Returns:
            {bn_count: int, ln_count: int, gn_count: int, 
             no_norm_flag: int, param_mass_ratio: float}
        """
        ...
    
    def _count_normalization_layers(self, state_dict: Dict[str, Tensor]) -> Dict[str, int]:
        """Count normalization layers by regex matching keys.
        
        Returns:
            {bn_count: int, ln_count: int, gn_count: int}
        """
        ...
    
    def _compute_param_mass_ratio(self, state_dict: Dict[str, Tensor]) -> float:
        """Compute R = conv_params / (conv_params + linear_params_no_head).
        
        Returns:
            Ratio in [0.0, 1.0]. Returns 0.0 if denominator is zero.
        """
        ...
    
    def _is_conv_weight(self, tensor: Tensor) -> bool:
        """Check if tensor is 4D convolution weight."""
        return tensor.ndim == 4
    
    def _is_linear_weight(self, tensor: Tensor) -> bool:
        """Check if tensor is 2D linear weight."""
        return tensor.ndim == 2
    
    def _exclude_head_keys(self, key: str) -> bool:
        """Check if key contains head/fc/classifier."""
        return any(kw in key.lower() for kw in self.head_keywords)
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| state_dict values | [out_ch, in_ch, kH, kW] | Conv weights (4D) |
| state_dict values | [out_feat, in_feat] | Linear weights (2D) |
| feature_vector | [5] | [bn, ln, gn, no_norm, R] |
| train_df | [42, 7] | 42 models × 7 columns |
| val_df | [18, 7] | 18 models × 7 columns |

### Pseudo-code

```
# Download and feature extraction
1. models = []
2. for family in ['CNN', 'Transformer', 'Hybrid']:
3.     for model_name in model_families[family]:
4.         checkpoint = timm.create_model(model_name, pretrained=True).state_dict()
5.         features = extract_features(checkpoint)
6.         models.append((model_name, family, features))
7. train, val = stratified_split(models, test_size=0.3, stratify=family)

# Normalization counting (case-insensitive regex)
1. bn_count = sum(1 for k in state_dict.keys() if re.match(r'.*bn.*', k, re.I))
2. ln_count = sum(1 for k in state_dict.keys() if re.match(r'.*ln.*', k, re.I))
3. gn_count = sum(1 for k in state_dict.keys() if re.match(r'.*gn.*', k, re.I))
4. no_norm_flag = 1 if (bn_count + ln_count + gn_count == 0) else 0

# Parameter mass ratio
1. conv_params = sum(v.numel() for k, v in state_dict.items() 
                     if v.ndim == 4 and not _exclude_head_keys(k))
2. linear_params = sum(v.numel() for k, v in state_dict.items() 
                       if v.ndim == 2 and not _exclude_head_keys(k))
3. R = conv_params / (conv_params + linear_params) if (conv_params + linear_params) > 0 else 0.0
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | TIMM model download | Implement download_models() with retry logic |
| L-2-2 | Feature extraction | Implement extract_features() with regex patterns |

---

## E1-5: Evaluation [Complexity: 10, Budget: 2 subtasks]

**Applied:** sklearn metrics + matplotlib visualization

### API Signatures

```python
from typing import Dict, List, Tuple
import numpy as np
from numpy.typing import NDArray
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

class ValidationEvaluator:
    def __init__(self, classifier: LogisticRegression, scaler: StandardScaler):
        """Initialize evaluator with trained artifacts."""
        self.classifier = classifier
        self.scaler = scaler
    
    def evaluate(
        self, 
        X_val: pd.DataFrame, 
        y_val: pd.Series
    ) -> Dict[str, float]:
        """Compute validation metrics.
        
        Args:
            X_val: Feature matrix [18, 5]
            y_val: True labels [18]
            
        Returns:
            {macro_accuracy: float, cnn_accuracy: float, 
             transformer_accuracy: float, hybrid_accuracy: float,
             confusion_matrix: NDArray[shape=(3,3)]}
        """
        ...
    
    def generate_confusion_matrix(
        self, 
        y_true: NDArray, 
        y_pred: NDArray, 
        output_path: str
    ) -> None:
        """Generate and save confusion matrix heatmap.
        
        Args:
            y_true: [18] true labels
            y_pred: [18] predicted labels
            output_path: PNG file path
        """
        ...
    
    def generate_feature_importance(
        self, 
        feature_names: List[str], 
        output_path: str
    ) -> None:
        """Generate feature importance bar plot.
        
        Args:
            feature_names: ['bn_count', 'ln_count', 'gn_count', 
                            'no_norm_flag', 'param_mass_ratio']
            output_path: PNG file path
            
        Note:
            Importance = mean(|coef|) across 3 classes
        """
        ...
    
    def generate_r_distribution(
        self, 
        val_df: pd.DataFrame, 
        output_path: str
    ) -> None:
        """Generate parameter-mass ratio histogram per family.
        
        Args:
            val_df: Validation DataFrame [18, 7]
            output_path: PNG file path
        """
        ...
    
    def get_misclassified_models(
        self, 
        val_df: pd.DataFrame, 
        y_pred: NDArray
    ) -> pd.DataFrame:
        """Return DataFrame of misclassified models.
        
        Returns:
            Columns: [model_name, true_family, predicted_family]
        """
        ...
```

### Data Structures

| Variable | Shape | Note |
|----------|-------|------|
| X_val | [18, 5] | Validation features |
| y_val | [18] | True labels (0=CNN, 1=Transformer, 2=Hybrid) |
| y_pred | [18] | Predicted labels |
| confusion_matrix | [3, 3] | Rows=true, Cols=pred |
| coefficients | [3, 5] | 3 classes × 5 features |
| feature_importance | [5] | Mean absolute coefficient |

### Pseudo-code

```
# Macro-accuracy computation
1. X_scaled = scaler.transform(X_val)  # [18, 5]
2. y_pred = classifier.predict(X_scaled)  # [18]
3. macro_acc = accuracy_score(y_val, y_pred)  # average of 3 class accuracies

# Per-class accuracy
1. report = classification_report(y_val, y_pred, output_dict=True)
2. cnn_acc = report['CNN']['precision']
3. transformer_acc = report['Transformer']['precision']
4. hybrid_acc = report['Hybrid']['precision']

# Feature importance (coefficient analysis)
1. coefs = classifier.coef_  # [3, 5] for 3 classes
2. importance = np.mean(np.abs(coefs), axis=0)  # [5]
3. sorted_features = zip(feature_names, importance)
4. plot bar chart sorted by importance

# Confusion matrix visualization
1. cm = confusion_matrix(y_val, y_pred)  # [3, 3]
2. sns.heatmap(cm, annot=True, fmt='d', xticklabels=['CNN', 'Trans', 'Hybrid'], 
               yticklabels=['CNN', 'Trans', 'Hybrid'])
3. plt.ylabel('True Family')
4. plt.xlabel('Predicted Family')
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Metrics computation | Implement evaluate() with sklearn metrics |
| L-5-2 | Visualization | Implement 3 plot generation functions |

---

## Integration Notes

### Data Flow

1. `TIMMDataLoader.download_models()` → List[(name, family, state_dict)]
2. `StatisticalFeatureExtractor.extract_features()` → feature dict per model
3. `TIMMDataLoader.create_splits()` → (train_df, val_df) CSVs
4. `ClassifierTrainer.train()` reads train_df → (classifier, scaler)
5. `ValidationEvaluator.evaluate()` reads val_df → metrics dict
6. `ValidationEvaluator.generate_*()` → PNG plots

### Critical Implementation Requirements

**From Architecture Document:**
- `_count_normalization_layers()` MUST use `re.IGNORECASE` flag
- `_exclude_head_keys()` MUST check for 'head', 'fc', 'classifier' substrings
- `create_splits()` MUST use `stratify=df['family']` parameter

### Error Handling

**Data Pipeline:**
- Checkpoint download timeout (30 min) → retry once, skip model on second failure
- Empty state_dict → raise ValueError
- Zero total parameters → set param_mass_ratio = 0.0

**Evaluation:**
- Division by zero in metrics → handle with np.nan
- Plot generation failure → log error, continue pipeline

---

## Validation Checklist

- [ ] Feature extraction returns dict with exactly 5 keys
- [ ] Normalization counts are non-negative integers
- [ ] param_mass_ratio in [0.0, 1.0]
- [ ] train_df shape = (42, 7), val_df shape = (18, 7)
- [ ] Stratification maintains class ratios (CNN:Trans:Hybrid ≈ 2:2:1)
- [ ] Confusion matrix shape = (3, 3)
- [ ] Feature importance array shape = (5,)
- [ ] All plots saved as PNG files

---

**End of Logic Document**
