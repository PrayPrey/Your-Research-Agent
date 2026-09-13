# Logic Specification: H-M1 Normalization Layer Fingerprinting

**Hypothesis ID:** h-m1  
**Type:** MECHANISM (MUST_WORK gate)  
**Date:** 2026-07-11  
**Status:** Ready for Phase 4 Implementation  

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** Reusing h-e1 validated components (88.89% validation accuracy)  
**Analyzed Path:** `docs/youra_research/h-e1/code/`  
**Relevant Symbols:** StatisticalFeatureExtractor, LogisticClassifierTrainer, NORM_PATTERNS  
**Code Reuse:** 80% from h-e1 (feature extraction, data loading, config)

---

## Knowledge Base Patterns Applied

**Applied:** sklearn LogisticRegression coefficient extraction, pandas groupby statistics

---

## A-1: ViolationRateAnalyzer [Complexity: 14, Budget: 14/14]

**Applied:** Classification violation detection pattern

### API Signatures

```python
class ViolationRateAnalyzer:
    def __init__(self, threshold: float = 0.15):
        """Initialize analyzer with violation threshold."""
        self.threshold = threshold
    
    def compute_violation_rates(self, features_df: pd.DataFrame) -> dict:
        """
        Compute per-family violation rates.
        
        Args:
            features_df: DataFrame with columns [model_name, family, bn_count, ln_count, ...]
        
        Returns:
            {
                'cnn_violation_rate': float,
                'transformer_violation_rate': float,
                'cnn_violations': list[str],
                'transformer_violations': list[str],
                'cnn_passed': bool,
                'transformer_passed': bool,
                'gate_decision': 'PASS' | 'FAIL'
            }
        """
        ...
    
    def _compute_family_violation_rate(
        self, family_df: pd.DataFrame, family: str
    ) -> tuple[float, list[str]]:
        """
        Compute violation rate for single family.
        
        Returns: (violation_rate, violator_model_names)
        """
        ...
    
    def save_violation_report(self, results: dict, output_path: str):
        """Save violation rates to CSV."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| features_df | (N, F) | N models × F features |
| family_df | (N_family, F) | Subset by family |
| violations | (V,) | Boolean mask |

### Pseudo-code

```
1. Split features_df by family (CNN, Transformer, Hybrid)

2. For CNN family:
   violations = (ln_count > bn_count)  # LayerNorm dominates
   cnn_violation_rate = violations.sum() / len(cnn_models)
   cnn_passed = (cnn_violation_rate <= 0.15)

3. For Transformer family:
   violations = (bn_count > ln_count)  # BatchNorm dominates
   transformer_violation_rate = violations.sum() / len(transformer_models)
   transformer_passed = (transformer_violation_rate <= 0.15)

4. Gate decision:
   IF cnn_passed AND transformer_passed:
       gate_decision = 'PASS'
   ELSE:
       gate_decision = 'FAIL'

5. Return results with violation lists
```

### Subtasks [14/14 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | Violation detection | Implement ln_count > bn_count for CNN |
| L-1-2 | Violation detection | Implement bn_count > ln_count for Transformer |
| L-1-3 | Rate calculation | Compute violations / total_models |
| L-1-4 | Gate logic | Implement P1 AND P2 threshold check |
| L-1-5 | Edge case handling | Skip Hybrid family (no violation definition) |
| L-1-6 | Output formatting | Generate violation CSV |

---

## A-2: NormalizationDistributionAnalyzer [Complexity: 12, Budget: 12/12]

**Applied:** Pandas groupby statistics pattern

### API Signatures

```python
class NormalizationDistributionAnalyzer:
    def compute_distributions(self, features_df: pd.DataFrame) -> dict:
        """
        Compute per-family normalization statistics.
        
        Args:
            features_df: DataFrame with [family, bn_count, ln_count, gn_count]
        
        Returns:
            {
                'CNN': {
                    'bn_count': {'mean': float, 'median': float, 'std': float},
                    'ln_count': {'mean': float, 'median': float, 'std': float},
                    'gn_count': {'mean': float, 'median': float, 'std': float},
                    'dominant_norm': 'BatchNorm' | 'LayerNorm' | 'GroupNorm' | 'Mixed'
                },
                'Transformer': {...},
                'Hybrid': {...}
            }
        """
        ...
    
    def _compute_family_stats(self, family_df: pd.DataFrame) -> dict:
        """Compute mean, median, std for single family."""
        ...
    
    def _determine_dominant_norm(self, family_df: pd.DataFrame) -> str:
        """Identify dominant normalization type (>50% models)."""
        ...
    
    def save_distributions(self, distributions: dict, output_path: str):
        """Save distributions to JSON."""
        ...
```

### Pseudo-code

```
1. For each family in ['CNN', 'Transformer', 'Hybrid']:
   family_df = features_df[features_df.family == family]
   
2. Compute statistics:
   stats = {
       'bn_count': {
           'mean': family_df.bn_count.mean(),
           'median': family_df.bn_count.median(),
           'std': family_df.bn_count.std()
       },
       'ln_count': {...},
       'gn_count': {...}
   }

3. Determine dominant norm:
   bn_dominant = (family_df.bn_count > family_df.ln_count).sum() / len(family_df)
   ln_dominant = (family_df.ln_count > family_df.bn_count).sum() / len(family_df)
   gn_dominant = (family_df.gn_count > max(family_df.bn_count, family_df.ln_count)).sum() / len(family_df)
   
   IF bn_dominant > 0.5:
       dominant_norm = 'BatchNorm'
   ELIF ln_dominant > 0.5:
       dominant_norm = 'LayerNorm'
   ELIF gn_dominant > 0.5:
       dominant_norm = 'GroupNorm'
   ELSE:
       dominant_norm = 'Mixed'

4. Return statistics dictionary
```

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Statistics | Implement mean/median/std for 3 norm types |
| L-2-2 | Dominant detection | Implement >50% threshold logic |
| L-2-3 | Family iteration | Loop over 3 families |
| L-2-4 | JSON export | Save distributions to file |

---

## A-3: EdgeCaseDetector [Complexity: 10, Budget: 10/10]

**Applied:** Regex pattern matching for model names

### API Signatures

```python
class EdgeCaseDetector:
    def detect_edge_cases(self, features_df: pd.DataFrame) -> dict:
        """
        Identify edge case models.
        
        Args:
            features_df: DataFrame with [model_name, family, bn_count, ln_count, no_norm_flag]
        
        Returns:
            {
                'NormFree': [
                    {'model': str, 'family': str, 'bn_count': int, 'ln_count': int, 'notes': str}
                ],
                'MetaFormer': [...],
                'ConvNeXt': [...],
                'total_edge_cases': int,
                'edge_case_rate': float
            }
        """
        ...
    
    def _detect_normfree(self, features_df: pd.DataFrame) -> list:
        """Detect models with no_norm_flag == 1."""
        ...
    
    def _detect_metaformer(self, features_df: pd.DataFrame) -> list:
        """Detect 'poolformer' in model_name."""
        ...
    
    def _detect_convnext(self, features_df: pd.DataFrame) -> list:
        """Detect 'convnext' in model_name."""
        ...
    
    def save_edge_cases(self, edge_cases: dict, output_path: str):
        """Save edge cases to JSON."""
        ...
```

### Pseudo-code

```
1. Detect NormFree:
   normfree_models = features_df[features_df.no_norm_flag == 1]
   normfree_list = [
       {
           'model': row.model_name,
           'family': row.family,
           'bn_count': row.bn_count,
           'ln_count': row.ln_count,
           'notes': 'No normalization layers'
       }
       for row in normfree_models
   ]

2. Detect MetaFormer:
   metaformer_models = features_df[features_df.model_name.str.contains('poolformer', case=False)]
   metaformer_list = [...]  # Same format

3. Detect ConvNeXt:
   convnext_models = features_df[features_df.model_name.str.contains('convnext', case=False)]
   convnext_list = [...]  # Same format

4. Compute edge case rate:
   total_edge_cases = len(normfree_list) + len(metaformer_list) + len(convnext_list)
   edge_case_rate = total_edge_cases / len(features_df)

5. Return categorized edge cases
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | NormFree detection | Check no_norm_flag == 1 |
| L-3-2 | MetaFormer detection | Regex 'poolformer' in model_name |
| L-3-3 | ConvNeXt detection | Regex 'convnext' in model_name |
| L-3-4 | Edge case formatting | Format output dictionaries |
| L-3-5 | JSON export | Save to file |

---

## A-4: FeatureImportanceExtractor [Complexity: 11, Budget: 11/11]

**Applied:** sklearn LogisticRegression coefficient extraction

### API Signatures

```python
class FeatureImportanceExtractor:
    def __init__(self, feature_names: list[str]):
        """Initialize with feature names from config."""
        self.feature_names = feature_names
    
    def extract_importance(self, classifier, feature_names: list[str]) -> pd.DataFrame:
        """
        Extract feature importance from LogisticRegression coefficients.
        
        Args:
            classifier: Trained sklearn LogisticRegression (one-vs-rest, 3 classes)
            feature_names: ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']
        
        Returns:
            DataFrame with columns [feature, coefficient, rank, interpretation]
            Sorted descending by absolute coefficient
        """
        ...
    
    def _compute_average_coefficient(self, classifier, feature_idx: int) -> float:
        """
        Compute average |coefficient| across 3 classes.
        
        Returns: mean(|coef[0, feature_idx]|, |coef[1, feature_idx]|, |coef[2, feature_idx]|)
        """
        ...
    
    def _interpret_coefficient(self, feature: str, coef: float) -> str:
        """Generate human-readable interpretation."""
        ...
    
    def check_normalization_feature_importance(self, importance_df: pd.DataFrame) -> dict:
        """
        Validate S1 criterion: bn_count, ln_count > 0.1.
        
        Returns:
            {
                'bn_count_coef': float,
                'ln_count_coef': float,
                'bn_passed': bool,
                'ln_passed': bool,
                's1_criterion_passed': bool
            }
        """
        ...
    
    def save_feature_importance(self, importance_df: pd.DataFrame, output_path: str):
        """Save feature importance to CSV."""
        ...
```

### Mathematical Formulation

**Feature Importance (Multi-class LogisticRegression):**

```
classifier.coef_ shape: (3, 5)  # 3 classes × 5 features

For feature i:
    avg_importance[i] = mean(|coef[0, i]|, |coef[1, i]|, |coef[2, i]|)

Ranking: sort features by avg_importance (descending)

S1 Criterion:
    bn_passed = (avg_importance[bn_count] > 0.1)
    ln_passed = (avg_importance[ln_count] > 0.1)
    s1_criterion_passed = bn_passed AND ln_passed
```

### Pseudo-code

```
1. Extract coefficients:
   coef_matrix = classifier.coef_  # shape: (3, 5)

2. For each feature:
   avg_coef = np.mean(np.abs(coef_matrix[:, feature_idx]))

3. Create importance DataFrame:
   importance_df = pd.DataFrame({
       'feature': feature_names,
       'coefficient': [avg_coef for each feature],
       'rank': [1, 2, 3, 4, 5],  # after sorting descending
       'interpretation': [interpret(feature, coef) for each feature]
   })

4. Check S1 criterion:
   bn_coef = importance_df[importance_df.feature == 'bn_count'].coefficient.iloc[0]
   ln_coef = importance_df[importance_df.feature == 'ln_count'].coefficient.iloc[0]
   s1_passed = (bn_coef > 0.1) AND (ln_coef > 0.1)

5. Return importance_df + S1 results
```

### Subtasks [11/11 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Coefficient extraction | Extract classifier.coef_ matrix |
| L-4-2 | Average computation | Mean of |coef| across classes |
| L-4-3 | Ranking | Sort by coefficient descending |
| L-4-4 | S1 validation | Check bn_count > 0.1, ln_count > 0.1 |
| L-4-5 | CSV export | Save to file |

---

## External Dependencies API (From h-e1)

### Verified from Actual Code

The following APIs are reused from h-e1 validated codebase. Signatures verified from actual implementation:

```python
# From: docs/youra_research/h-e1/code/src/feature_extractor.py (ACTUAL CODE)
class StatisticalFeatureExtractor:
    def extract_features(self, state_dict: dict) -> dict:
        """
        Extract normalization counts and parameter-mass ratio.
        
        Returns:
            {
                'bn_count': int,
                'ln_count': int,
                'gn_count': int,
                'no_norm_flag': int,  # 1 if total_norm == 0, else 0
                'param_mass_ratio': float  # conv_params / (conv_params + linear_params)
            }
        """
        ...
    
    def _count_normalization_layers(self, state_dict: dict) -> dict:
        """
        Count normalization layers via regex matching.
        
        Patterns (from config.NORM_PATTERNS):
            bn: r'bn|batch_norm|batchnorm'
            ln: r'ln|layer_norm|layernorm'
            gn: r'gn|group_norm|groupnorm'
        
        Returns: {'bn_count': int, 'ln_count': int, 'gn_count': int}
        """
        ...
    
    def _compute_param_mass_ratio(self, state_dict: dict) -> float:
        """
        Compute R = conv_params / (conv_params + linear_params).
        
        Logic:
            - 4D tensors → conv weights
            - 2D tensors → linear weights
            - Exclude classification head keys (HEAD_KEYWORDS)
        """
        ...


# From: docs/youra_research/h-e1/code/src/classifier_trainer.py (ACTUAL CODE)
class LogisticClassifierTrainer:
    def __init__(self, random_state: int = 42):
        """Initialize trainer."""
        ...
    
    def train(self, X_train: pd.DataFrame, y_train: pd.Series) -> tuple:
        """
        Train LogisticRegression with StandardScaler.
        
        Returns: (classifier, scaler)
        """
        ...
    
    def load_artifacts(self, model_dir: str) -> tuple:
        """
        Load classifier and scaler from disk.
        
        Returns: (classifier, scaler)
        """
        ...
    
    def save_artifacts(self, classifier, scaler, output_dir: str):
        """Save trained artifacts."""
        ...


# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
MODEL_FAMILIES = {
    'CNN': [
        'resnet18', 'resnet34', 'resnet50', 'resnet101', 'resnet152',
        'mobilenetv3_large_100', 'efficientnet_b0', 'efficientnet_b4',
        'densenet121', 'densenet201', 'vgg16', 'vgg19',
        'convnext_tiny', 'convnext_base',
        'resnext50_32x4d', 'wide_resnet50_2',
        'regnetx_032', 'regnety_032',
        'seresnet50', 'senet154',
        'inception_v3', 'inception_v4',
        'dpn68', 'dpn131'
    ],
    'Transformer': [
        'vit_tiny_patch16_224', 'vit_small_patch16_224',
        'vit_base_patch16_224', 'vit_large_patch16_224',
        'deit_tiny_patch16_224', 'deit_small_patch16_224',
        'deit_base_patch16_224', 'deit_base_distilled_patch16_224',
        'swin_tiny_patch4_window7_224', 'swin_small_patch4_window7_224',
        'swin_base_patch4_window7_224', 'beit_base_patch16_224',
        'twins_pcpvt_base', 'twins_svt_base', 'cait_s24_224',
        'coat_lite_medium', 'levit_256', 'levit_384',
        'poolformer_m36', 'poolformer_m48',
        'xcit_small_12_p16_224', 'crossvit_base_240'
    ],
    'Hybrid': [
        'resnetv2_50x1_bit_distilled', 'convit_base',
        'pit_b_224', 'pit_s_224', 'cait_xxs24_224',
        'mixer_b16_224', 'mixer_l16_224',
        'convnext_base_in22k', 'twins_pcpvt_small',
        'visformer_small', 'tnt_s_patch16_224', 'maxvit_tiny_tf_224'
    ]
}

FEATURE_NAMES = ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']

NORM_PATTERNS = {
    'bn': r'bn|batch_norm|batchnorm',
    'ln': r'ln|layer_norm|layernorm',
    'gn': r'gn|group_norm|groupnorm'
}

HEAD_KEYWORDS = ['head', 'fc', 'classifier']

CLASSIFIER_CONFIG = {
    'solver': 'lbfgs',
    'max_iter': 1000,
    'random_state': 42,
    'class_weight': 'balanced'
}
```

**Verified from:** `docs/youra_research/h-e1/code/` (actual implementation, NOT specs)

---

## Data Flow

### Input Schema (from h-e1)

**train_features.csv / val_features.csv:**
```
model_name,family,bn_count,ln_count,gn_count,no_norm_flag,param_mass_ratio
resnet18,CNN,20,0,0,0,0.997
vit_tiny_patch16_224,Transformer,0,24,0,0,0.015
mixer_b16_224,Hybrid,0,12,0,0,0.000
vgg16,CNN,0,0,0,1,0.995
```

**classifier.pkl:**
- Trained LogisticRegression (3 classes: CNN, Transformer, Hybrid)
- classifier.coef_ shape: (3, 5)
- classifier.classes_: ['CNN', 'Hybrid', 'Transformer']

### Output Schema

**h-m1_violation_rates.csv:**
```
family,total_models,violations,violation_rate,threshold,status
CNN,24,2,0.083,0.15,PASS
Transformer,15,1,0.067,0.15,PASS
```

**h-m1_feature_importance.csv:**
```
feature,coefficient,rank,interpretation
param_mass_ratio,2.456,1,Strong discriminator (conv vs linear mass)
bn_count,0.823,2,Moderate discriminator (CNN signature)
ln_count,0.567,3,Moderate discriminator (Transformer signature)
no_norm_flag,0.234,4,Weak discriminator (NormFree detection)
gn_count,0.012,5,Negligible (GroupNorm rare)
```

**h-m1_norm_distributions.json:**
```json
{
  "CNN": {
    "bn_count": {"mean": 18.5, "median": 20.0, "std": 4.2},
    "ln_count": {"mean": 0.3, "median": 0.0, "std": 1.1},
    "gn_count": {"mean": 0.0, "median": 0.0, "std": 0.0},
    "dominant_norm": "BatchNorm"
  },
  "Transformer": {
    "bn_count": {"mean": 0.8, "median": 0.0, "std": 2.1},
    "ln_count": {"mean": 22.3, "median": 24.0, "std": 5.6},
    "gn_count": {"mean": 0.0, "median": 0.0, "std": 0.0},
    "dominant_norm": "LayerNorm"
  },
  "Hybrid": {
    "bn_count": {"mean": 5.2, "median": 4.0, "std": 3.8},
    "ln_count": {"mean": 10.1, "median": 12.0, "std": 6.5},
    "gn_count": {"mean": 0.0, "median": 0.0, "std": 0.0},
    "dominant_norm": "Mixed"
  }
}
```

**h-m1_edge_cases.json:**
```json
{
  "NormFree": [
    {"model": "vgg16", "family": "CNN", "bn_count": 0, "ln_count": 0, "notes": "No normalization layers"}
  ],
  "MetaFormer": [
    {"model": "poolformer_m36", "family": "Transformer", "bn_count": 0, "ln_count": 12, "notes": "Token mixer architecture"}
  ],
  "ConvNeXt": [
    {"model": "convnext_tiny", "family": "CNN", "bn_count": 2, "ln_count": 9, "notes": "Modern CNN with LayerNorm"}
  ],
  "total_edge_cases": 5,
  "edge_case_rate": 0.10
}
```

---

## Gate Conditions (MUST_WORK Logic)

### Primary Criteria

**P1: CNN Violation Rate ≤15%**
```python
cnn_df = features_df[features_df.family == 'CNN']
cnn_violations = (cnn_df.ln_count > cnn_df.bn_count).sum()
cnn_violation_rate = cnn_violations / len(cnn_df)
P1_passed = (cnn_violation_rate <= 0.15)
```

**P2: Transformer Violation Rate ≤15%**
```python
transformer_df = features_df[features_df.family == 'Transformer']
transformer_violations = (transformer_df.bn_count > transformer_df.ln_count).sum()
transformer_violation_rate = transformer_violations / len(transformer_df)
P2_passed = (transformer_violation_rate <= 0.15)
```

### Gate Decision Tree

```
IF P1_passed AND P2_passed:
    gate_decision = 'PASS'
    recommendation = 'Proceed to H-M2'
ELSE:
    gate_decision = 'FAIL'
    IF NOT P1_passed:
        recommendation = 'PIVOT: Add temporal feature (model release year) or refine taxonomy (Legacy vs Modern CNN)'
    ELIF NOT P2_passed:
        recommendation = 'PIVOT: Add attention mechanism detection (Q/K/V weight counting)'
```

---

## Edge Case Handling

### NormFree Models (VGG-16)

**Detection:** `no_norm_flag == 1`

**Handling:**
```python
# NormFree models automatically violate CNN paradigm (no BatchNorm)
# Document as edge case, include in violation count
if no_norm_flag == 1:
    edge_cases['NormFree'].append({
        'model': model_name,
        'family': family,
        'bn_count': 0,
        'ln_count': 0,
        'notes': 'No normalization layers'
    })
```

**Impact:** May increase CNN violation rate if VGG-16 classified as CNN.

---

### MetaFormer Models (PoolFormer)

**Detection:** `'poolformer' in model_name.lower()`

**Handling:**
```python
# PoolFormer uses LayerNorm but is a token mixer, not pure Transformer
# May contribute to Transformer violation if has BatchNorm in stem
if 'poolformer' in model_name.lower():
    edge_cases['MetaFormer'].append({
        'model': model_name,
        'family': family,
        'bn_count': bn_count,
        'ln_count': ln_count,
        'notes': 'Token mixer architecture (non-standard LayerNorm)'
    })
```

**Impact:** Acceptable if Transformer violation rate ≤15%.

---

### ConvNeXt Models (Modern CNN with LayerNorm)

**Detection:** `'convnext' in model_name.lower()`

**Handling:**
```python
# ConvNeXt is modern CNN that uses LayerNorm instead of BatchNorm
# Expected to violate CNN paradigm (ln_count > bn_count)
if 'convnext' in model_name.lower():
    edge_cases['ConvNeXt'].append({
        'model': model_name,
        'family': family,
        'bn_count': bn_count,
        'ln_count': ln_count,
        'notes': 'Modern CNN with LayerNorm'
    })
```

**Impact:** Expected to violate CNN paradigm. Document for H-M2 refinement.

---

### DeiT Stem BatchNorm

**Detection:** `bn_count > 0` in Transformer family

**Handling:**
```python
# DeiT uses BatchNorm in stem, LayerNorm in blocks
# Acceptable if ln_count > bn_count (LayerNorm still dominates)
if family == 'Transformer' and bn_count > 0 and ln_count > bn_count:
    # Not a violation (LayerNorm dominates)
    pass
elif family == 'Transformer' and bn_count > ln_count:
    # Violation (BatchNorm dominates)
    violations.append(model_name)
```

**Impact:** h-e1 showed 13.33% Transformer models with BatchNorm (acceptable if ≤15%).

---

## Validation Logic (Manual Validation)

### S2 Criterion: Regex Accuracy ≥95%

**Procedure:**
```
1. Sample 10 models randomly from 50 models:
   sample_models = random.sample(all_models, 10)

2. For each model:
   a. Load state_dict
   b. Print state_dict.keys()
   c. Manually count BN/LN/GN keys
   d. Compare with StatisticalFeatureExtractor output
   e. Record match (1) or mismatch (0)

3. Compute accuracy:
   manual_accuracy = matches / 10
   S2_passed = (manual_accuracy >= 0.95)

4. Expected result: 9/10 or 10/10 matches (≥95%)
```

**Sample Models (Suggested):**
- resnet18 (CNN, high bn_count)
- vit_tiny_patch16_224 (Transformer, high ln_count)
- mixer_b16_224 (Hybrid, mixed)
- vgg16 (NormFree, no_norm_flag=1)
- poolformer_m36 (MetaFormer)
- convnext_tiny (ConvNeXt)
- deit_tiny_patch16_224 (DeiT, potential stem BN)
- efficientnet_b0 (CNN, high bn_count)
- swin_tiny_patch4_window7_224 (Transformer, high ln_count)
- pit_b_224 (Hybrid, mixed)

---

## Error Handling

### ZeroDivisionError

```python
# In ViolationRateAnalyzer
if len(family_df) == 0:
    raise ValueError(f"No models found for family: {family}")

# In NormalizationDistributionAnalyzer
if family_df.empty:
    return {'mean': 0.0, 'median': 0.0, 'std': 0.0}
```

### KeyError

```python
# In FeatureImportanceExtractor
if feature not in feature_names:
    raise KeyError(f"Feature '{feature}' not found in feature_names")

# In ViolationRateAnalyzer
required_columns = ['model_name', 'family', 'bn_count', 'ln_count']
missing = [col for col in required_columns if col not in features_df.columns]
if missing:
    raise KeyError(f"Missing required columns: {missing}")
```

### ValueError

```python
# In EdgeCaseDetector
if not isinstance(features_df, pd.DataFrame):
    raise ValueError("features_df must be a pandas DataFrame")

# In NormalizationDistributionAnalyzer
if family not in ['CNN', 'Transformer', 'Hybrid']:
    raise ValueError(f"Invalid family: {family}")
```

---

## Integration Logic

### H_M1_Runner Orchestration

```python
class H_M1_Runner:
    def run_mechanism_validation(self) -> dict:
        """
        Main orchestration function.
        
        Returns:
            {
                'violation_results': dict,
                'distribution_results': dict,
                'edge_case_results': dict,
                'feature_importance_results': dict,
                'gate_decision': 'PASS' | 'FAIL',
                'runtime_seconds': float
            }
        """
        start_time = time.time()
        
        # Step 1: Load h-e1 artifacts
        features_df = pd.read_csv(f"{self.base_hypothesis_dir}/outputs/train_features.csv")
        val_features_df = pd.read_csv(f"{self.base_hypothesis_dir}/outputs/val_features.csv")
        classifier = joblib.load(f"{self.base_hypothesis_dir}/outputs/classifier.pkl")
        
        # Step 2: Run ViolationRateAnalyzer
        violation_analyzer = ViolationRateAnalyzer(threshold=0.15)
        violation_results = violation_analyzer.compute_violation_rates(features_df)
        
        # Step 3: Run NormalizationDistributionAnalyzer
        distribution_analyzer = NormalizationDistributionAnalyzer()
        distribution_results = distribution_analyzer.compute_distributions(features_df)
        
        # Step 4: Run EdgeCaseDetector
        edge_case_detector = EdgeCaseDetector()
        edge_case_results = edge_case_detector.detect_edge_cases(features_df)
        
        # Step 5: Run FeatureImportanceExtractor
        feature_importance_extractor = FeatureImportanceExtractor(FEATURE_NAMES)
        importance_df = feature_importance_extractor.extract_importance(classifier, FEATURE_NAMES)
        importance_results = feature_importance_extractor.check_normalization_feature_importance(importance_df)
        
        # Step 6: Generate 04_validation.md
        self._generate_validation_report(
            violation_results,
            distribution_results,
            edge_case_results,
            importance_results
        )
        
        # Step 7: Save all outputs
        self._save_all_outputs(
            violation_results,
            distribution_results,
            edge_case_results,
            importance_df
        )
        
        end_time = time.time()
        runtime_seconds = end_time - start_time
        
        return {
            'violation_results': violation_results,
            'distribution_results': distribution_results,
            'edge_case_results': edge_case_results,
            'feature_importance_results': importance_results,
            'gate_decision': violation_results['gate_decision'],
            'runtime_seconds': runtime_seconds
        }
```

---

## Performance Requirements

### Runtime Budget

**Target:** ≤20 minutes (CPU-only)

**Breakdown:**
- Load h-e1 features: <1 min (CSV read)
- ViolationRateAnalyzer: <1 min (pandas filter + boolean operations)
- NormalizationDistributionAnalyzer: <1 min (pandas groupby + statistics)
- EdgeCaseDetector: <1 min (string matching)
- FeatureImportanceExtractor: <1 min (sklearn coefficient extraction)
- Report generation: <1 min (markdown writing)
- **Total: ~5 minutes** (well below 20 min threshold)

**Note:** h-m1 reuses h-e1 features (no model download), reducing runtime from 20 min to 5 min.

---

### Memory Budget

**Target:** ≤8 GB peak RAM

**Profile:**
- h-e1 features: 50 models × 5 features × 8 bytes = 2 KB
- h-e1 classifier: ~10 KB (sklearn LogisticRegression)
- Analysis results: ~50 KB (violation rates, distributions, edge cases)
- **Peak RAM: <100 MB** (well below 8 GB threshold)

---

## Success Metrics

### Primary Success Criteria (MUST_WORK Gate)

| ID | Criterion | Metric | Threshold | Measurement |
|----|-----------|--------|-----------|-------------|
| P1 | CNN Violation Rate | `cnn_violation_rate` | ≤15% | violations / total_cnn_models |
| P2 | Transformer Violation Rate | `transformer_violation_rate` | ≤15% | violations / total_transformer_models |

**Gate Decision:**
- **PASS:** P1 AND P2 meet thresholds → Proceed to H-M2
- **FAIL:** P1 OR P2 exceeds threshold → PIVOT

---

### Secondary Success Criteria

| ID | Criterion | Metric | Threshold | Measurement |
|----|-----------|--------|-----------|-------------|
| S1 | Feature Importance | bn_count + ln_count coefficients | Both > 0.1 | avg(\|coef\|) across classes |
| S2 | Regex Accuracy | Manual validation match rate | ≥95% | manual_matches / 10 |
| S3 | Edge Case Handling | no_norm_flag detection for NormFree | 100% | detected / known_edge_cases |

---

## Reproducibility Guarantees

### Determinism

- Reuse h-e1 features (same 70/30 split, random_state=42)
- No randomness in h-m1 modules (deterministic regex, statistics)
- Fixed TIMM version: 1.0.9 (same as h-e1)
- Fixed sklearn version: 1.3.0 (same as h-e1)

### Verification

```python
# Run h-m1 twice, compare outputs byte-by-byte
run_1_results = H_M1_Runner().run_mechanism_validation()
run_2_results = H_M1_Runner().run_mechanism_validation()

assert run_1_results == run_2_results  # Expect identical results
```

---

## Type Annotations

### Core Types

```python
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression

# Feature extraction
Features = Dict[str, Union[int, float]]  # {bn_count: int, ln_count: int, ...}

# Violation analysis
ViolationResults = Dict[str, Union[float, List[str], bool, str]]
# {
#     'cnn_violation_rate': float,
#     'transformer_violation_rate': float,
#     'cnn_violations': List[str],
#     'transformer_violations': List[str],
#     'cnn_passed': bool,
#     'transformer_passed': bool,
#     'gate_decision': str
# }

# Distribution analysis
FamilyStats = Dict[str, Dict[str, float]]
# {
#     'bn_count': {'mean': float, 'median': float, 'std': float},
#     'ln_count': {...},
#     'gn_count': {...},
#     'dominant_norm': str
# }

DistributionResults = Dict[str, FamilyStats]
# {'CNN': FamilyStats, 'Transformer': FamilyStats, 'Hybrid': FamilyStats}

# Edge case detection
EdgeCaseModel = Dict[str, Union[str, int]]
# {'model': str, 'family': str, 'bn_count': int, 'ln_count': int, 'notes': str}

EdgeCaseResults = Dict[str, Union[List[EdgeCaseModel], int, float]]
# {
#     'NormFree': List[EdgeCaseModel],
#     'MetaFormer': List[EdgeCaseModel],
#     'ConvNeXt': List[EdgeCaseModel],
#     'total_edge_cases': int,
#     'edge_case_rate': float
# }

# Feature importance
ImportanceResults = Dict[str, Union[float, bool]]
# {
#     'bn_count_coef': float,
#     'ln_count_coef': float,
#     'bn_passed': bool,
#     'ln_passed': bool,
#     's1_criterion_passed': bool
# }
```

---

## Testing Strategy

### Unit Tests

**test_violation_analyzer.py:**
```python
def test_cnn_violation_detection():
    # Test: ln_count > bn_count triggers CNN violation
    features = pd.DataFrame({
        'model_name': ['convnext_tiny'],
        'family': ['CNN'],
        'bn_count': [2],
        'ln_count': [9]
    })
    analyzer = ViolationRateAnalyzer()
    result = analyzer._compute_family_violation_rate(features, 'CNN')
    assert result[0] == 1.0  # 100% violation rate
    assert 'convnext_tiny' in result[1]

def test_gate_decision_pass():
    # Test: Both ≤15% → PASS
    features = pd.DataFrame({
        'family': ['CNN', 'CNN', 'CNN', 'CNN', 'CNN', 'CNN', 'CNN',
                   'Transformer', 'Transformer', 'Transformer', 'Transformer', 'Transformer', 'Transformer', 'Transformer'],
        'bn_count': [20, 18, 22, 19, 21, 17, 5,  # 6/7 CNNs have bn > ln
                     0, 2, 0, 0, 0, 0, 0],       # 1/7 Transformers has bn > ln
        'ln_count': [0, 0, 0, 0, 0, 0, 9,        # 1/7 CNNs has ln > bn (14.3%)
                     24, 12, 20, 18, 22, 16, 14] # 6/7 Transformers have ln > bn
    })
    analyzer = ViolationRateAnalyzer(threshold=0.15)
    result = analyzer.compute_violation_rates(features)
    assert result['cnn_violation_rate'] <= 0.15
    assert result['transformer_violation_rate'] <= 0.15
    assert result['gate_decision'] == 'PASS'
```

**test_distribution_analyzer.py:**
```python
def test_dominant_norm_batchnorm():
    # Test: CNN → 'BatchNorm' when >50% models have bn_count > ln_count
    features = pd.DataFrame({
        'family': ['CNN', 'CNN', 'CNN', 'CNN'],
        'bn_count': [20, 18, 22, 0],
        'ln_count': [0, 0, 0, 9]
    })
    analyzer = NormalizationDistributionAnalyzer()
    result = analyzer._determine_dominant_norm(features)
    assert result == 'BatchNorm'  # 3/4 models have bn > ln
```

**test_edge_case_detector.py:**
```python
def test_detect_normfree():
    # Test: no_norm_flag == 1 detected as NormFree
    features = pd.DataFrame({
        'model_name': ['vgg16'],
        'family': ['CNN'],
        'bn_count': [0],
        'ln_count': [0],
        'no_norm_flag': [1]
    })
    detector = EdgeCaseDetector()
    result = detector._detect_normfree(features)
    assert len(result) == 1
    assert result[0]['model'] == 'vgg16'
    assert result[0]['notes'] == 'No normalization layers'
```

**test_feature_importance.py:**
```python
def test_extract_importance():
    # Test: average |coef| across classes
    classifier = LogisticRegression()
    classifier.coef_ = np.array([
        [1.0, -0.5, 0.3, -0.2, 2.0],  # Class 0
        [-0.8, 0.6, -0.4, 0.1, 1.5],  # Class 1
        [0.9, -0.7, 0.2, -0.3, 2.5]   # Class 2
    ])
    extractor = FeatureImportanceExtractor(['f0', 'f1', 'f2', 'f3', 'f4'])
    result = extractor.extract_importance(classifier, ['f0', 'f1', 'f2', 'f3', 'f4'])
    
    # Check f0: mean(|1.0|, |-0.8|, |0.9|) = 0.9
    assert abs(result[result.feature == 'f0'].coefficient.iloc[0] - 0.9) < 0.01
    
    # Check f4 has highest importance
    assert result.iloc[0].feature == 'f4'
```

---

## Document Metadata

**Version:** 1.0  
**Last Updated:** 2026-07-11  
**Status:** APPROVED for Phase 4 Implementation  
**Estimated Implementation Time:** 5 hours  
**Estimated Runtime:** 5 minutes  
**Code Reuse:** 80% from h-e1  
**New Code:** 4 modules, ~300 LOC  
**Total Complexity:** 47 (14 + 12 + 10 + 11)
