# Phase 2C Experiment Brief: H-M1 Normalization Layer Fingerprinting

**Hypothesis ID:** h-m1  
**Type:** MECHANISM  
**Gate Type:** MUST_WORK  
**Date:** 2026-07-11  
**Prerequisite:** h-e1 (VALIDATED - 88.89% accuracy)  

---

## 1. Hypothesis Statement

**Full Statement:**  
Under TIMM model checkpoint inspection, if normalization layer types are counted via state_dict key regex matching, then CNNs show predominantly BatchNorm (>80%), Transformers show predominantly LayerNorm (>80%), and Hybrids show mixed patterns because architectural paradigms impose normalization conventions (spatial vs token-wise statistics).

**Rationale:**  
This hypothesis tests the first step of the causal mechanism—that normalization layer choice is a reliable architectural signature. It validates Chun 2026's theoretical finding (LayerNorm reduces LLC by m/2 vs BatchNorm) manifests empirically as a discriminative feature.

**Prerequisite Results from H-E1:**
- ✅ 88.89% validation accuracy achieved (exceeded 80% threshold)
- ✅ Feature importance: `param_mass_ratio` (0.777) > `no_norm_flag` (0.456) > `bn_count` (0.353) > `ln_count` (0.171)
- ✅ Assumption A2 passed: CNN LayerNorm violation 0%, Transformer BatchNorm violation 13.33% (threshold ≤15%)
- ⚠️ Edge cases identified: VGG-16 (NormFree), PoolFormer (MetaFormer)

---

## 2. Research Questions

### Primary Question
**RQ1:** Do normalization layer counts (BN, LN, GN) reliably fingerprint architecture families (CNN/Transformer/Hybrid) with violation rates ≤15% per class?

### Secondary Questions
**RQ2:** What is the feature importance ranking of normalization counts (bn_count, ln_count, gn_count) in the logistic regression classifier?

**RQ3:** How do edge case architectures (NormFree, MetaFormer) affect normalization fingerprinting accuracy?

**RQ4:** Does adding fallback heuristics (`no_norm_flag`) mitigate edge case failures?

---

## 3. Experimental Design

### 3.1 Dataset Specification

**Source:** TIMM Model Zoo (reusing h-e1 dataset)

**Model Selection (50 models total):**
- **Training Set:** 32 models (70% split from h-e1)
  - CNN: 16 models (ResNet, MobileNet, EfficientNet, DenseNet, VGG, ConvNeXt, RegNet, SENet, Inception, DPN families)
  - Transformer: 15 models (ViT, DeiT, Swin, BEiT, Twins, CaiT, CoaT, LeViT, PoolFormer, XCiT, CrossViT families)
  - Hybrid: 5 models (ResNetV2-BiT, ConViT, PiT, CaiT-XXS, MLP-Mixer, Visformer, TnT, MaxViT families)

- **Validation Set:** 18 models (30% split from h-e1)
  - CNN: 7 models
  - Transformer: 4 models
  - Hybrid: 7 models

**Dataset Type:** `standard` (established TIMM model zoo, not synthetic)

**Dataset Characteristics:**
- **Scale:** Full TIMM pretrained checkpoints (standard validation set)
- **Diversity:** Multi-family coverage (ResNet, ViT, Swin, Hybrid architectures)
- **Ground Truth:** TIMM naming + structural validation (h-e1 confirmed 88.89% accuracy)

**Dataset Format:**
```python
# Each sample is a model checkpoint state_dict
{
    'model_name': 'resnet50',
    'family': 'CNN',
    'state_dict': OrderedDict(...),  # PyTorch checkpoint
    'features': {
        'bn_count': int,
        'ln_count': int,
        'gn_count': int,
        'no_norm_flag': int,
        'param_mass_ratio': float
    }
}
```

**Access Method:**
```python
import timm
model = timm.create_model(model_name, pretrained=True)
state_dict = model.state_dict()
```

### 3.2 Normalization Layer Counting Protocol

**Extraction Method:** Regex pattern matching on state_dict keys (reusing h-e1 implementation)

**Regex Patterns (from h-e1/code/config.py):**
```python
NORM_PATTERNS = {
    'bn': r'bn|batch_norm|batchnorm',
    'ln': r'ln|layer_norm|layernorm',
    'gn': r'gn|group_norm|groupnorm'
}
```

**Counting Algorithm:**
```python
def count_normalization_layers(state_dict: dict) -> dict:
    """Count normalization layers via regex matching on keys"""
    bn_count = sum(1 for k in state_dict.keys()
                  if re.search(r'bn|batch_norm|batchnorm', k, re.IGNORECASE))
    ln_count = sum(1 for k in state_dict.keys()
                  if re.search(r'ln|layer_norm|layernorm', k, re.IGNORECASE))
    gn_count = sum(1 for k in state_dict.keys()
                  if re.search(r'gn|group_norm|groupnorm', k, re.IGNORECASE))
    
    return {'bn_count': bn_count, 'ln_count': ln_count, 'gn_count': gn_count}
```

**Fallback Heuristic:**
```python
total_norm = bn_count + ln_count + gn_count
no_norm_flag = 1 if total_norm == 0 else 0
```

### 3.3 Violation Rate Analysis

**Definition of Violation:**
- **CNN Violation:** CNN model has `ln_count > bn_count` (LayerNorm dominates over BatchNorm)
- **Transformer Violation:** Transformer model has `bn_count > ln_count` (BatchNorm dominates over LayerNorm)
- **Hybrid:** No violation definition (expected to have mixed patterns)

**Violation Rate Calculation:**
```python
# Per-class violation rates
cnn_violation_rate = sum(ln_count > bn_count for CNN models) / len(CNN_models)
transformer_violation_rate = sum(bn_count > ln_count for Transformer models) / len(Transformer_models)
```

**Success Criteria:**
- `cnn_violation_rate ≤ 0.15` (≤15%)
- `transformer_violation_rate ≤ 0.15` (≤15%)

### 3.4 Feature Importance Analysis

**Method:** Logistic Regression Coefficients (from h-e1 classifier)

**Feature Ranking:**
```python
from sklearn.linear_model import LogisticRegression

clf = LogisticRegression(solver='lbfgs', max_iter=1000, random_state=42, class_weight='balanced')
clf.fit(X_train, y_train)

# Average absolute coefficient across 3 classes (CNN, Transformer, Hybrid)
feature_importance = np.mean(np.abs(clf.coef_), axis=0)
# Expected shape: [bn_count, ln_count, gn_count, no_norm_flag, param_mass_ratio]
```

**Expected Ranking (from h-e1 results):**
1. `param_mass_ratio`: 0.7770 (dominant feature)
2. `no_norm_flag`: 0.4561 (edge case detector)
3. `bn_count`: 0.3529 (CNN fingerprint)
4. `ln_count`: 0.1714 (Transformer fingerprint)
5. `gn_count`: 0.0000 (rare in TIMM)

**H-M1 Specific Analysis:**
- **Primary Goal:** Confirm `bn_count` and `ln_count` are top features **within normalization counts**
- **Expected:** `bn_count > ln_count > gn_count` (excluding param_mass_ratio and no_norm_flag)
- **Threshold:** `bn_count` and `ln_count` should both have non-zero coefficients (importance > 0.1)

### 3.5 Edge Case Robustness Testing

**Edge Case Models (from h-e1 failure analysis):**
1. **VGG-16 (NormFree CNN):**
   - Features: `bn_count=0, ln_count=0, gn_count=0, no_norm_flag=1, param_mass_ratio=1.0`
   - Expected: CNN (purely convolutional)
   - H-E1 Result: Misclassified as Hybrid (confused by `no_norm_flag=1`)
   - H-M1 Test: Verify `no_norm_flag` correctly identifies NormFree architectures

2. **PoolFormer-M36 (MetaFormer Transformer):**
   - Features: Non-standard LayerNorm placement
   - Expected: Transformer (attention-free transformer)
   - H-E1 Result: Misclassified as Hybrid (boundary case)
   - H-M1 Test: Analyze LayerNorm count distribution for MetaFormer architectures

**Edge Case Test Protocol:**
```python
# Identify edge cases in validation set
edge_cases = {
    'NormFree': [model for model in validation_set if model['features']['no_norm_flag'] == 1],
    'MetaFormer': [model for model in validation_set if 'poolformer' in model['model_name'].lower()]
}

# Measure accuracy degradation
baseline_accuracy = validation_accuracy_on_standard_models
edge_case_accuracy = validation_accuracy_on_edge_cases
degradation = baseline_accuracy - edge_case_accuracy
```

**Success Criteria:**
- Edge case accuracy degradation ≤15% (e.g., if baseline 90%, edge cases ≥75%)

---

## 4. Baseline Comparison

### 4.1 Baseline: H-E1 Overall Classifier

**H-E1 Performance (prerequisite):**
- Validation Accuracy: 88.89% (16/18 correct)
- Feature Importance: `param_mass_ratio` (0.777) dominates
- Normalization counts contribute: `bn_count` (0.353), `ln_count` (0.171)

**H-M1 Focus:**
- Isolate normalization layer contributions from parameter-mass ratio
- Measure violation rates independently of overall accuracy
- Validate Assumption A2 mechanistically (not just empirically)

### 4.2 Baseline: Random Classifier

**Random Baseline:**
- 3-way classification (CNN, Transformer, Hybrid)
- Expected accuracy: 33.33% (chance level)

**H-M1 vs Random:**
- If normalization fingerprinting works, violation rates should be ≤15%
- If normalization is random/conventional, violation rates would be ~50%

### 4.3 Baseline: Manual Inspection (Ground Truth)

**Method:** Structural validation via state_dict inspection
- Load checkpoint with `torch.load(weights_only=True)`
- Manually count BatchNorm, LayerNorm, GroupNorm modules
- Compare regex-based counts with manual counts

**Validation Sample:** 10 models (same as h-e1 Assumption A1 test)

**Success Criteria:**
- Regex counting accuracy ≥95% (matches manual counts within 5% error)

---

## 5. Success Criteria & Gate Conditions

### 5.1 Primary Success Criteria (MUST_WORK Gate)

| Criterion | Metric | Threshold | Rationale |
|-----------|--------|-----------|-----------|
| **P1: CNN Violation Rate** | `cnn_violation_rate` | ≤15% | CNNs should predominantly use BatchNorm |
| **P2: Transformer Violation Rate** | `transformer_violation_rate` | ≤15% | Transformers should predominantly use LayerNorm |

**Gate Decision:**
- **PASS:** Both P1 AND P2 meet thresholds → Proceed to H-M2
- **FAIL:** Either P1 OR P2 exceeds threshold → PIVOT to alternative features

### 5.2 Secondary Success Criteria

| Criterion | Metric | Threshold | Rationale |
|-----------|--------|-----------|-----------|
| **S1: Feature Importance** | `bn_count` + `ln_count` coefficients | Both > 0.1 | Normalization counts contribute to classification |
| **S2: Regex Accuracy** | Manual validation match rate | ≥95% | Regex counting is reliable |
| **S3: Edge Case Handling** | `no_norm_flag` detection rate for NormFree | 100% | Fallback heuristic works |

### 5.3 Gate Failure Actions

**If P1 Fails (CNN violation >15%):**
- **Root Cause:** Modern CNNs adopting LayerNorm (e.g., ConvNeXt)
- **Pivot Action:** Add temporal feature (model release year) to distinguish legacy vs modern CNNs
- **Alternative:** Use GroupNorm patterns as secondary CNN fingerprint

**If P2 Fails (Transformer violation >15%):**
- **Root Cause:** Hybrid architectures mislabeled as pure Transformers
- **Pivot Action:** Refine family taxonomy (split "Hybrid" into "Conv-Transformer" vs "Pure Transformer")
- **Alternative:** Add attention mechanism detection (query/key/value weight counting)

---

## 6. Implementation Plan

### 6.1 Code Reuse from H-E1

**Reusable Components:**
1. **Feature Extractor (`h-e1/code/src/feature_extractor.py`):**
   - `StatisticalFeatureExtractor.extract_features()` → Already implements normalization counting
   - `_count_normalization_layers()` → Regex-based counting (ready to use)

2. **Data Loader (`h-e1/code/src/data_loader.py`):**
   - `TIMMModelLoader.load_models()` → Already loads 50 TIMM models
   - Train/validation split (70/30) → Same split as h-e1

3. **Classifier (`h-e1/code/src/classifier_trainer.py`):**
   - Logistic Regression training → Reuse for feature importance extraction

4. **Config (`h-e1/code/config.py`):**
   - `NORM_PATTERNS` → Regex patterns already defined
   - `MODEL_FAMILIES` → Same 50 models

### 6.2 New H-M1 Specific Components

**Component 1: Violation Rate Analyzer**
```python
class ViolationRateAnalyzer:
    """Analyze normalization layer violation rates per family"""
    
    def compute_violation_rates(self, features_df, family_labels):
        """
        Compute CNN and Transformer violation rates.
        
        Violation definitions:
        - CNN: ln_count > bn_count
        - Transformer: bn_count > ln_count
        """
        cnn_mask = (family_labels == 'CNN')
        transformer_mask = (family_labels == 'Transformer')
        
        cnn_violations = (features_df.loc[cnn_mask, 'ln_count'] > 
                         features_df.loc[cnn_mask, 'bn_count']).sum()
        cnn_total = cnn_mask.sum()
        
        transformer_violations = (features_df.loc[transformer_mask, 'bn_count'] > 
                                 features_df.loc[transformer_mask, 'ln_count']).sum()
        transformer_total = transformer_mask.sum()
        
        return {
            'cnn_violation_rate': cnn_violations / cnn_total if cnn_total > 0 else 0,
            'transformer_violation_rate': transformer_violations / transformer_total if transformer_total > 0 else 0,
            'cnn_violations': cnn_violations,
            'cnn_total': cnn_total,
            'transformer_violations': transformer_violations,
            'transformer_total': transformer_total
        }
```

**Component 2: Normalization Distribution Analyzer**
```python
class NormalizationDistributionAnalyzer:
    """Analyze per-family normalization layer distributions"""
    
    def compute_family_statistics(self, features_df, family_labels):
        """
        Compute normalization layer statistics per family.
        
        Returns:
        - Mean, median, std for bn_count, ln_count, gn_count per family
        - Dominant normalization type per family
        """
        stats = {}
        for family in ['CNN', 'Transformer', 'Hybrid']:
            family_mask = (family_labels == family)
            family_data = features_df[family_mask]
            
            stats[family] = {
                'bn_count': {
                    'mean': family_data['bn_count'].mean(),
                    'median': family_data['bn_count'].median(),
                    'std': family_data['bn_count'].std()
                },
                'ln_count': {
                    'mean': family_data['ln_count'].mean(),
                    'median': family_data['ln_count'].median(),
                    'std': family_data['ln_count'].std()
                },
                'gn_count': {
                    'mean': family_data['gn_count'].mean(),
                    'median': family_data['gn_count'].median(),
                    'std': family_data['gn_count'].std()
                },
                'dominant_norm': self._get_dominant_norm(family_data)
            }
        
        return stats
    
    def _get_dominant_norm(self, family_data):
        """Determine dominant normalization type for family"""
        mean_bn = family_data['bn_count'].mean()
        mean_ln = family_data['ln_count'].mean()
        mean_gn = family_data['gn_count'].mean()
        
        if mean_bn > mean_ln and mean_bn > mean_gn:
            return 'BatchNorm'
        elif mean_ln > mean_bn and mean_ln > mean_gn:
            return 'LayerNorm'
        elif mean_gn > mean_bn and mean_gn > mean_ln:
            return 'GroupNorm'
        else:
            return 'Mixed'
```

**Component 3: Edge Case Detector**
```python
class EdgeCaseDetector:
    """Detect and analyze edge cases (NormFree, MetaFormer)"""
    
    def detect_edge_cases(self, features_df, model_names):
        """
        Identify edge case models.
        
        Categories:
        - NormFree: no_norm_flag == 1
        - MetaFormer: 'poolformer' in model_name
        - ConvNeXt: 'convnext' in model_name (modern CNN with LayerNorm)
        """
        edge_cases = {
            'NormFree': [],
            'MetaFormer': [],
            'ConvNeXt': []
        }
        
        for idx, (model_name, features) in enumerate(zip(model_names, features_df.itertuples())):
            if features.no_norm_flag == 1:
                edge_cases['NormFree'].append({
                    'model_name': model_name,
                    'features': features._asdict()
                })
            
            if 'poolformer' in model_name.lower():
                edge_cases['MetaFormer'].append({
                    'model_name': model_name,
                    'features': features._asdict()
                })
            
            if 'convnext' in model_name.lower():
                edge_cases['ConvNeXt'].append({
                    'model_name': model_name,
                    'features': features._asdict()
                })
        
        return edge_cases
```

### 6.3 Experiment Execution Steps

**Step 1: Data Preparation (Reuse h-e1 data)**
- Load TIMM models (same 50 models as h-e1)
- Extract features using `StatisticalFeatureExtractor`
- Split into train/validation (70/30, same split as h-e1)

**Step 2: Violation Rate Analysis**
```python
analyzer = ViolationRateAnalyzer()
violation_rates = analyzer.compute_violation_rates(validation_features, validation_labels)

# Check MUST_WORK gate
assert violation_rates['cnn_violation_rate'] <= 0.15, "P1 FAILED: CNN violation rate > 15%"
assert violation_rates['transformer_violation_rate'] <= 0.15, "P2 FAILED: Transformer violation rate > 15%"
```

**Step 3: Feature Importance Extraction**
```python
# Train logistic regression (reuse h-e1 classifier)
clf = LogisticRegression(solver='lbfgs', max_iter=1000, random_state=42, class_weight='balanced')
clf.fit(X_train, y_train)

# Extract coefficients
feature_importance = np.mean(np.abs(clf.coef_), axis=0)
feature_names = ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']

# Check secondary criterion S1
norm_importance = {
    'bn_count': feature_importance[0],
    'ln_count': feature_importance[1],
    'gn_count': feature_importance[2]
}
assert norm_importance['bn_count'] > 0.1 and norm_importance['ln_count'] > 0.1, "S1 FAILED: Normalization counts not important"
```

**Step 4: Normalization Distribution Analysis**
```python
dist_analyzer = NormalizationDistributionAnalyzer()
family_stats = dist_analyzer.compute_family_statistics(validation_features, validation_labels)

# Expected results:
# - CNN dominant_norm: 'BatchNorm'
# - Transformer dominant_norm: 'LayerNorm'
# - Hybrid dominant_norm: 'Mixed'
```

**Step 5: Edge Case Analysis**
```python
edge_detector = EdgeCaseDetector()
edge_cases = edge_detector.detect_edge_cases(validation_features, validation_model_names)

# Verify NormFree detection (S3)
normfree_detected = len(edge_cases['NormFree'])
expected_normfree = 1  # VGG-16 from h-e1
assert normfree_detected >= expected_normfree, "S3 FAILED: NormFree detection incomplete"
```

**Step 6: Manual Validation (S2)**
```python
# Sample 10 models for manual inspection
sample_models = random.sample(validation_set, 10)

for model in sample_models:
    # Manual count (ground truth)
    manual_counts = manually_count_normalization_layers(model['state_dict'])
    
    # Regex count (automated)
    regex_counts = feature_extractor._count_normalization_layers(model['state_dict'])
    
    # Compare
    match_rate = compute_match_rate(manual_counts, regex_counts)
    assert match_rate >= 0.95, f"S2 FAILED: Regex mismatch for {model['model_name']}"
```

### 6.4 Output Artifacts

**Artifact 1: Violation Rate Report (`h-m1_violation_rates.csv`)**
```csv
family,total_models,violations,violation_rate,threshold,status
CNN,7,0,0.00%,15%,PASSED
Transformer,4,0,0.00%,15%,PASSED
```

**Artifact 2: Feature Importance Report (`h-m1_feature_importance.csv`)**
```csv
feature,coefficient,rank,interpretation
param_mass_ratio,0.7770,1,Most discriminative (from h-e1)
no_norm_flag,0.4561,2,Edge case detector (from h-e1)
bn_count,0.3529,3,CNN fingerprint ← H-M1 PRIMARY FOCUS
ln_count,0.1714,4,Transformer fingerprint ← H-M1 PRIMARY FOCUS
gn_count,0.0000,5,Unused
```

**Artifact 3: Normalization Distribution Report (`h-m1_norm_distributions.json`)**
```json
{
  "CNN": {
    "bn_count": {"mean": 50.2, "median": 48, "std": 12.5},
    "ln_count": {"mean": 0.3, "median": 0, "std": 0.8},
    "gn_count": {"mean": 0.0, "median": 0, "std": 0.0},
    "dominant_norm": "BatchNorm"
  },
  "Transformer": {
    "bn_count": {"mean": 1.2, "median": 0, "std": 2.1},
    "ln_count": {"mean": 48.7, "median": 50, "std": 8.3},
    "gn_count": {"mean": 0.0, "median": 0, "std": 0.0},
    "dominant_norm": "LayerNorm"
  },
  "Hybrid": {
    "bn_count": {"mean": 24.5, "median": 22, "std": 15.2},
    "ln_count": {"mean": 26.3, "median": 25, "std": 14.8},
    "gn_count": {"mean": 0.1, "median": 0, "std": 0.3},
    "dominant_norm": "Mixed"
  }
}
```

**Artifact 4: Edge Case Analysis Report (`h-m1_edge_cases.json`)**
```json
{
  "NormFree": [
    {
      "model_name": "vgg16",
      "features": {"bn_count": 0, "ln_count": 0, "gn_count": 0, "no_norm_flag": 1, "param_mass_ratio": 1.0},
      "true_family": "CNN",
      "predicted_family": "Hybrid",
      "correctly_detected": true
    }
  ],
  "MetaFormer": [
    {
      "model_name": "poolformer_m36",
      "features": {"bn_count": 0, "ln_count": 24, "gn_count": 0, "no_norm_flag": 0, "param_mass_ratio": 0.15},
      "true_family": "Transformer",
      "predicted_family": "Hybrid",
      "correctly_detected": true
    }
  ],
  "ConvNeXt": [
    {
      "model_name": "convnext_tiny",
      "features": {"bn_count": 0, "ln_count": 12, "gn_count": 0, "no_norm_flag": 0, "param_mass_ratio": 0.85},
      "true_family": "CNN",
      "predicted_family": "CNN",
      "note": "Modern CNN using LayerNorm instead of BatchNorm"
    }
  ]
}
```

**Artifact 5: Validation Report (`h-m1/04_validation.md`)**
- Gate decision (PASS/FAIL)
- Violation rate results (P1, P2)
- Feature importance analysis (S1)
- Regex validation results (S2)
- Edge case handling (S3)
- Recommendations for H-M2

---

## 7. Computational Requirements

### 7.1 Resource Estimates

| Resource | Requirement | Justification |
|----------|-------------|---------------|
| **GPU** | Not required | Checkpoint-only analysis (no forward passes) |
| **RAM** | 8 GB | TIMM model loading + state_dict processing |
| **Storage** | 10 GB | TIMM checkpoint cache (~200 MB per model × 50 models) |
| **Runtime** | 15 minutes | Model loading (10 min) + feature extraction (2 min) + analysis (3 min) |

### 7.2 Environment Setup

**Dependencies (from h-e1):**
```txt
torch>=2.1.0
timm==1.0.9
scikit-learn>=1.3.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

**Environment Activation:**
```bash
cd docs/youra_research/h-m1/code
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 7.3 Expected Runtime Breakdown

1. **Model Loading:** 10 minutes (50 models × 12 seconds avg)
2. **Feature Extraction:** 2 minutes (regex matching on state_dict keys)
3. **Violation Rate Analysis:** 1 minute (simple counting operations)
4. **Feature Importance Extraction:** 1 minute (logistic regression already trained in h-e1)
5. **Normalization Distribution Analysis:** 1 minute (pandas groupby operations)
6. **Edge Case Detection:** 30 seconds (string matching on model names)
7. **Manual Validation:** 5 minutes (10 models × 30 seconds manual inspection)
8. **Report Generation:** 2 minutes (CSV/JSON writing)

**Total Runtime:** ~15-20 minutes

---

## 8. Risk Mitigation

### 8.1 Identified Risks

**R1: ConvNeXt False Positives**
- **Risk:** ConvNeXt is a modern CNN that uses LayerNorm instead of BatchNorm
- **Impact:** CNN violation rate may exceed 15% threshold
- **Likelihood:** Medium (2 ConvNeXt models in dataset)
- **Mitigation:** 
  - Document ConvNeXt as "modern CNN" edge case
  - Add temporal feature (release year) to distinguish legacy vs modern CNNs
  - Alternative: Treat ConvNeXt as "Hybrid" in taxonomy

**R2: DeiT Stem BatchNorm**
- **Risk:** DeiT variants include BatchNorm in patch embedding stem
- **Impact:** Transformer violation rate may increase (h-e1 showed 13.33%)
- **Likelihood:** Low (already near 15% threshold)
- **Mitigation:**
  - Acceptable if violation stays ≤15%
  - Document as "trace BatchNorm" (non-core architecture)

**R3: Regex False Negatives**
- **Risk:** Non-standard normalization layer naming (e.g., `norm1`, `norm2`)
- **Impact:** Undercounting normalization layers
- **Likelihood:** Low (TIMM uses standard naming)
- **Mitigation:**
  - Manual validation (S2 criterion) catches false negatives
  - Expand regex patterns if needed: `r'norm|bn|ln|gn|batch_norm|layer_norm|group_norm'`

**R4: GroupNorm Irrelevance**
- **Risk:** GroupNorm coefficient remains 0.0 (from h-e1)
- **Impact:** gn_count feature is unused
- **Likelihood:** High (confirmed in h-e1)
- **Mitigation:**
  - Acceptable (GroupNorm is rare in pretrained TIMM models)
  - Remove gn_count from future experiments (dimensionality reduction)

### 8.2 Contingency Plans

**If P1 Fails (CNN violation >15%):**
1. **Diagnosis:** Identify which CNN models violate (expect ConvNeXt)
2. **Pivot Option 1:** Refine taxonomy (split CNN into "Legacy CNN" vs "Modern CNN")
3. **Pivot Option 2:** Add temporal feature (model release year)
4. **Pivot Option 3:** Use parameter-mass ratio as primary CNN fingerprint (already validated in h-e1)

**If P2 Fails (Transformer violation >15%):**
1. **Diagnosis:** Identify which Transformer models violate (expect Hybrid mislabels)
2. **Pivot Option 1:** Refine ground truth labels (manual structural validation)
3. **Pivot Option 2:** Add attention mechanism detection (query/key/value weight counting)
4. **Pivot Option 3:** Treat high-violation models as Hybrid (taxonomic correction)

**If Both P1 and P2 Fail:**
- **Action:** PIVOT to H-M2 (parameter allocation pattern) as primary mechanism
- **Rationale:** param_mass_ratio is already validated as dominant feature (0.777 from h-e1)
- **Impact:** Normalization fingerprinting becomes secondary feature, not primary mechanism

---

## 9. Expected Results

### 9.1 Hypothesis Confirmation Scenario

**Expected Outcomes (PASS):**
- CNN violation rate: 0-10% (most CNNs use BatchNorm exclusively)
- Transformer violation rate: 10-15% (DeiT stem BatchNorm acceptable)
- Feature importance: `bn_count` (0.35) > `ln_count` (0.17) (from h-e1, both > 0.1 threshold)
- Regex accuracy: 95-100% (manual validation)
- Edge case detection: 100% for NormFree (VGG-16 detected)

**Interpretation:**
- Normalization layer choice is a reliable architectural signature
- BatchNorm → CNN, LayerNorm → Transformer paradigm confirmed
- Chun 2026 theory validated empirically

**Next Steps:**
- Proceed to H-M2 (parameter allocation pattern)
- Combine normalization fingerprint with parameter-mass ratio for robust classifier

### 9.2 Hypothesis Rejection Scenario

**Unexpected Outcomes (FAIL):**
- CNN violation rate: >20% (modern CNNs widely adopt LayerNorm)
- Transformer violation rate: >20% (hybrid architectures mislabeled)
- Feature importance: `bn_count` and `ln_count` coefficients < 0.1 (negligible contribution)

**Interpretation:**
- Normalization layer choice is conventional, not architectural necessity
- Modern CNNs (ConvNeXt, NFNet) break BatchNorm assumption
- Transformer taxonomy is too broad (includes MetaFormer, MLP-Mixer)

**Next Steps:**
- **PIVOT Action:** Refine taxonomy (split "Transformer" into "Attention-based" vs "Token-Mixer")
- **Alternative Feature:** Add activation function counts (`ReLU` vs `GELU` vs `SiLU`)
- **Fallback:** Rely on parameter-mass ratio as primary mechanism (H-M2)

### 9.3 Edge Case Insights

**Expected Edge Cases:**
1. **VGG-16 (NormFree):** Correctly detected via `no_norm_flag=1`
2. **PoolFormer (MetaFormer):** Non-standard LayerNorm placement (acceptable boundary case)
3. **ConvNeXt (Modern CNN):** Uses LayerNorm instead of BatchNorm (taxonomic ambiguity)

**Insights for H-C1 (Edge Case Robustness):**
- NormFree detection via `no_norm_flag` is effective
- MetaFormer architectures need special handling (separate taxonomy category?)
- Modern CNNs challenge the "BatchNorm = CNN" assumption (temporal evolution of conventions)

---

## 10. References

### 10.1 Theoretical Foundations

**Chun et al. 2026:**
- Finding: LayerNorm reduces LLC (Last Layer Collapse) by m/2 vs BatchNorm
- Implication: Normalization choice affects optimization geometry
- H-M1 Test: Does this theoretical difference manifest as an empirical discriminative feature?

**Fang et al. 2024:**
- Finding: Heterogeneous structures have diverged importance distributions
- Implication: Parameter allocation patterns reflect architectural computation style
- H-M1 Context: Normalization layer choice is part of architectural "heterogeneity"

### 10.2 Prerequisite Results (H-E1)

**H-E1 Validation Report:**
- Path: `docs/youra_research/h-e1/04_validation.md`
- Key Results:
  - ✅ 88.89% validation accuracy (exceeded 80% threshold)
  - ✅ Assumption A2 passed (CNN LayerNorm 0%, Transformer BatchNorm 13.33%)
  - ⚠️ Edge cases: VGG-16 (NormFree), PoolFormer (MetaFormer)
  - Feature importance: `param_mass_ratio` > `no_norm_flag` > `bn_count` > `ln_count`

**H-E1 Code Assets:**
- Feature Extractor: `h-e1/code/src/feature_extractor.py`
- Regex Patterns: `h-e1/code/config.py` → `NORM_PATTERNS`
- Dataset: Same 50 TIMM models (70/30 split)

### 10.3 TIMM Model Zoo Documentation

**TIMM Library:**
- Version: 1.0.9
- Repository: https://github.com/huggingface/pytorch-image-models
- Checkpoint Access: `timm.create_model(model_name, pretrained=True)`

**Normalization Layer Conventions:**
- ResNet family: BatchNorm2d
- ViT family: LayerNorm
- ConvNeXt family: LayerNorm (modern CNN)
- DeiT family: LayerNorm + trace BatchNorm in stem

---

## 11. Appendix

### 11.1 Regex Pattern Design Rationale

**Why Case-Insensitive Matching?**
- TIMM uses mixed case: `BatchNorm2d`, `LayerNorm`, `batchnorm`, `layernorm`
- Regex flag: `re.IGNORECASE` ensures all variants are captured

**Why Alternation (`|`) Instead of Character Classes?**
- `bn|batch_norm|batchnorm` captures abbreviations and full names
- Character class `[bn]` would match individual characters (incorrect)

**Why No Word Boundaries (`\b`)?**
- State_dict keys use dots: `layer1.0.bn1.weight`
- Word boundaries would miss `bn1` (expects whitespace delimiters)

**Example Matches:**
- `bn`: Matches `bn1`, `bn2`, `bn3` in ResNet
- `batch_norm`: Matches `batch_norm.weight` in older checkpoints
- `batchnorm`: Matches `batchnorm2d` in non-standard naming

### 11.2 Violation Rate Threshold Justification

**Why 15% Threshold?**
- Allows for trace violations (e.g., DeiT stem BatchNorm)
- Stricter than random (50% violation expected for random choice)
- Aligned with h-e1 Assumption A2 test (13.33% observed)

**Statistical Interpretation:**
- p-value < 0.05 for difference from random (binomial test)
- 15% threshold corresponds to ~85% adherence to paradigm convention
- Acceptable for proof-of-concept (production systems may require stricter threshold)

### 11.3 Feature Importance Interpretation

**Logistic Regression Coefficients:**
- Multi-class (one-vs-rest): 3 coefficient vectors (CNN, Transformer, Hybrid)
- Averaging: `np.mean(np.abs(coef_), axis=0)` averages across classes
- Interpretation: Higher absolute coefficient → stronger discriminative power

**Expected Coefficient Signs:**
- `bn_count`: Positive for CNN class, negative for Transformer class
- `ln_count`: Negative for CNN class, positive for Transformer class
- `no_norm_flag`: Positive for Hybrid class (catches VGG-16)

**Caveats:**
- Coefficients are not causal (correlation only)
- Feature scaling affects magnitude (sklearn `LogisticRegression` does not auto-scale)
- Coefficients from h-e1 used features scaled to [0, 1] range

---

**End of Experiment Brief**
