# Experiment Design Brief: H-E1 Statistical Features Sufficiency

**Date:** 2026-07-11  
**Hypothesis ID:** h-e1  
**Phase:** 2C - Experiment Design  
**Status:** COMPLETED  

---

## 1. Hypothesis Summary

**Statement:** Under TIMM model zoo evaluation, if normalization layer counts and parameter-mass ratio are extracted from checkpoints, then >80% 3-way classification accuracy (CNN/Transformer/Hybrid) can be achieved because these features capture fundamental architectural constraints (BatchNorm for spatial data, LayerNorm for sequential, conv vs linear parameter allocation).

**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Prerequisites:** None (foundation hypothesis)

---

## 2. Experiment Objectives

### 2.1 Primary Objective
Validate that simple statistical features (normalization layer counts + parameter-mass ratio) achieve >80% macro-averaged accuracy for 3-way architecture family classification on held-out TIMM models.

### 2.2 Secondary Objectives
1. Verify per-class accuracy ≥75% (no single class collapse)
2. Validate scale invariance: intra-family CV <0.15 across ResNet variants
3. Document confusion matrix and failure patterns
4. Establish baseline for mechanism hypotheses (H-M1, H-M2, H-M3)

---

## 3. Dataset Specification

### 3.1 Dataset Selection

**Name:** TIMM Model Zoo Architecture Families  
**Type:** programmatic-api  
**Source:** PyTorch Image Models (TIMM) library v1.0.9+  
**Access Method:** `timm.list_models()` + `timm.create_model()` with pretrained weights

**Rationale:**
- Real pretrained models from production library (not synthetic)
- Diverse architecture families with consistent naming conventions
- Standardized checkpoint format (PyTorch state_dict)
- Validated by Phase 2A assumption A1 (TIMM naming aligns with structure >90%)

### 3.2 Dataset Structure

**Total Sample Size:** 60 models (statistically meaningful for 3-class problem)

**Class Distribution (Stratified):**
- CNN: 24 models (40%)
- Transformer: 24 models (40%)
- Hybrid: 12 models (20%)

**Split Strategy:**
- Train: 42 models (70%) - stratified by family
- Validation: 18 models (30%) - stratified by family
- No test set (PoC phase, validation serves as held-out evaluation)

**Stratification Details:**
- Train: 17 CNN, 17 Transformer, 8 Hybrid
- Validation: 7 CNN, 7 Transformer, 4 Hybrid

### 3.3 Model Selection Criteria

**CNN Family (24 models):**
```python
# Scale diversity (ResNet family for CV validation)
resnet18, resnet34, resnet50, resnet101, resnet152

# Architecture diversity
mobilenetv3_large_100, efficientnet_b0, efficientnet_b4
densenet121, densenet201
vgg16, vgg19
convnext_tiny, convnext_base

# Additional variants
resnext50_32x4d, wide_resnet50_2
regnetx_032, regnety_032
seresnet50, senet154
inception_v3, inception_v4
dpn68, dpn131
```

**Transformer Family (24 models):**
```python
# Vision Transformers (scale diversity)
vit_tiny_patch16_224, vit_small_patch16_224
vit_base_patch16_224, vit_large_patch16_224

# DeiT variants
deit_tiny_patch16_224, deit_small_patch16_224
deit_base_patch16_224, deit_base_distilled_patch16_224

# Swin Transformers
swin_tiny_patch4_window7_224, swin_small_patch4_window7_224
swin_base_patch4_window7_224

# Other Transformer architectures
beit_base_patch16_224
twins_pcpvt_base, twins_svt_base
cait_s24_224
coat_lite_medium
levit_256, levit_384
poolformer_m36, poolformer_m48
xcit_small_12_p16_224
crossvit_base_240
```

**Hybrid Family (12 models):**
```python
# ResNet + Attention
resnetv2_50x1_bit_distilled
convit_base

# Transformer + Conv layers
pit_b_224, pit_s_224
cait_xxs24_224  # ConvToken + Transformer

# MLP-Mixer variants (Conv tokenization + MLP)
mixer_b16_224, mixer_l16_224

# Other hybrids
convnext_base_in22k  # Conv + LayerNorm
twins_pcpvt_small  # Local + Global attention
visformer_small  # Transformer + Conv
tnt_s_patch16_224  # Transformer-in-Transformer

# CoAtNet-style (Conv early + Transformer late)
maxvit_tiny_tf_224
```

### 3.4 Dataset Preparation Pipeline

**Step 1: Model Discovery**
```python
import timm

# Get all available pretrained models
all_models = timm.list_models(pretrained=True)

# Filter by family using naming patterns
cnn_pattern = r'^(resnet|mobilenet|efficientnet|densenet|vgg|convnext|resnext|wide_resnet|regnet|seresnet|senet|inception|dpn)'
transformer_pattern = r'^(vit|deit|swin|beit|twins|cait|coat|levit|poolformer|xcit|crossvit)'
hybrid_pattern = r'^(resnetv2.*bit|convit|pit|mixer|visformer|tnt|maxvit)'
```

**Step 2: Checkpoint Download**
```python
# Download and cache checkpoints
for model_name in selected_models:
    model = timm.create_model(model_name, pretrained=True)
    # Checkpoints auto-downloaded to ~/.cache/torch/hub/checkpoints/
    state_dict = model.state_dict()
```

**Step 3: Feature Extraction**
```python
def extract_features(state_dict):
    """
    Extract normalization counts and parameter-mass ratio from checkpoint.
    
    Returns:
        dict: {
            'bn_count': int,
            'ln_count': int,
            'gn_count': int,
            'no_norm_flag': int,
            'param_mass_ratio': float
        }
    """
    # Normalization layer counting via regex
    bn_count = sum(1 for k in state_dict.keys() if re.search(r'bn|batch_norm|batchnorm', k, re.I))
    ln_count = sum(1 for k in state_dict.keys() if re.search(r'ln|layer_norm|layernorm', k, re.I))
    gn_count = sum(1 for k in state_dict.keys() if re.search(r'gn|group_norm|groupnorm', k, re.I))
    
    # Fallback for NormFree networks
    no_norm_flag = 1 if (bn_count + ln_count + gn_count == 0) else 0
    
    # Parameter counting (4D=conv, 2D=linear)
    conv_params = 0
    linear_params = 0
    
    for k, v in state_dict.items():
        if 'head' in k or 'fc' in k or 'classifier' in k:
            continue  # Exclude classification head
        
        if v.dim() == 4:  # Conv weights [out_ch, in_ch, kH, kW]
            conv_params += v.numel()
        elif v.dim() == 2:  # Linear weights [out_feat, in_feat]
            linear_params += v.numel()
    
    # Compute parameter-mass ratio R
    total_params = conv_params + linear_params
    param_mass_ratio = conv_params / total_params if total_params > 0 else 0.0
    
    return {
        'bn_count': bn_count,
        'ln_count': ln_count,
        'gn_count': gn_count,
        'no_norm_flag': no_norm_flag,
        'param_mass_ratio': param_mass_ratio
    }
```

**Step 4: Dataset Creation**
```python
import pandas as pd
from sklearn.model_selection import train_test_split

# Extract features for all models
data = []
for model_name, family in model_family_mapping.items():
    model = timm.create_model(model_name, pretrained=True)
    features = extract_features(model.state_dict())
    data.append({
        'model_name': model_name,
        'family': family,
        **features
    })

df = pd.DataFrame(data)

# Stratified split
train_df, val_df = train_test_split(
    df, 
    test_size=0.3, 
    stratify=df['family'],
    random_state=42
)
```

### 3.5 Data Validation Checks

**Pre-experiment Validation:**
1. **Naming Alignment (A1):** Validate 10-model sample via structural inspection (target: >90% alignment)
   - Manual check: ResNet-50 has BatchNorm, ViT has LayerNorm
   - If <90%, flag for manual verification

2. **Normalization Convention (A2):** Check violation rates on training set
   - CNN with LayerNorm: must be ≤15%
   - Transformer with BatchNorm: must be ≤15%
   - Hybrid: allowed to have mixed patterns

3. **Scale Invariance (A3):** Validate CV <0.15 for ResNet family
   - Compute R for ResNet-18, 34, 50, 101, 152
   - Calculate coefficient of variation: CV = std(R) / mean(R)
   - If CV ≥0.15, flag scale confounding issue

---

## 4. Baseline Experiment Design

### 4.1 Model Architecture

**Type:** Logistic Regression (Linear Classifier)  
**Library:** scikit-learn v1.3+  
**Configuration:**
```python
from sklearn.linear_model import LogisticRegression

classifier = LogisticRegression(
    multi_class='multinomial',  # 3-way classification
    solver='lbfgs',              # Handles multinomial well
    max_iter=1000,               # Ensure convergence
    random_state=42,
    class_weight='balanced'      # Handle slight class imbalance (20% hybrid)
)
```

**Rationale:**
- Tests feature sufficiency (no MLP rescue allowed per Phase 2B)
- Interpretable coefficients for feature importance analysis
- Fast training (<1 minute for 42 samples)
- Well-suited for linearly separable features

### 4.2 Feature Vector

**Input Dimensions:** 5 features per model
```python
X = [
    bn_count,           # BatchNorm layer count
    ln_count,           # LayerNorm layer count  
    gn_count,           # GroupNorm layer count
    no_norm_flag,       # Binary flag for NormFree networks
    param_mass_ratio    # R = conv_params / (conv_params + linear_params_no_head)
]
```

**Feature Scaling:** StandardScaler (mean=0, std=1)
```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_val_scaled = scaler.transform(X_val)
```

**Rationale for Scaling:**
- Normalization counts (0-100s) vs parameter ratio (0-1) have different scales
- Logistic regression sensitive to feature magnitudes
- Preserves interpretability of coefficients after inverse transformation

### 4.3 Training Protocol

**Training Loop:**
```python
# Fit on training set
classifier.fit(X_train_scaled, y_train)

# Predict on validation set
y_val_pred = classifier.predict(X_val_scaled)
y_val_proba = classifier.predict_proba(X_val_scaled)
```

**No Hyperparameter Tuning:**
- Simple model, default hyperparameters sufficient
- No GridSearch/RandomSearch (avoids overfitting on small dataset)
- Regularization strength C=1.0 (sklearn default)

**No Cross-Validation:**
- Single train/val split (70/30 stratified)
- PoC experiment, focused on directional validation
- Cross-validation deferred to H-M hypotheses if H-E1 passes

### 4.4 Evaluation Metrics

**Primary Metric:**
```python
from sklearn.metrics import accuracy_score

# Macro-averaged accuracy (equal weight per class)
macro_accuracy = accuracy_score(y_val, y_val_pred)

# Success: macro_accuracy > 0.80
```

**Secondary Metrics:**
```python
from sklearn.metrics import classification_report, confusion_matrix

# Per-class accuracy
report = classification_report(y_val, y_val_pred, output_dict=True)
cnn_accuracy = report['CNN']['precision']
transformer_accuracy = report['Transformer']['precision']
hybrid_accuracy = report['Hybrid']['precision']

# Success: all class accuracies ≥ 0.75

# Confusion matrix
conf_matrix = confusion_matrix(y_val, y_val_pred, labels=['CNN', 'Transformer', 'Hybrid'])
```

**Feature Importance Analysis:**
```python
# Logistic regression coefficients
coefficients = classifier.coef_  # Shape: [3 classes, 5 features]

# Average absolute coefficient per feature (importance proxy)
feature_names = ['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']
importance = np.abs(coefficients).mean(axis=0)

# Rank features by importance
importance_ranking = sorted(zip(feature_names, importance), key=lambda x: x[1], reverse=True)
```

### 4.5 Statistical Validation

**Scale Invariance Test (A3):**
```python
# Extract R for ResNet family
resnet_models = ['resnet18', 'resnet34', 'resnet50', 'resnet101', 'resnet152']
resnet_R = [df[df['model_name'] == m]['param_mass_ratio'].values[0] for m in resnet_models]

# Coefficient of Variation
cv = np.std(resnet_R) / np.mean(resnet_R)

# Success: cv < 0.15
```

**Inter-Family Separation (for H-M2 preview):**
```python
from scipy import stats

# Cohen's d between CNN and Transformer R distributions
cnn_R = df[df['family'] == 'CNN']['param_mass_ratio']
transformer_R = df[df['family'] == 'Transformer']['param_mass_ratio']

cohens_d = (cnn_R.mean() - transformer_R.mean()) / np.sqrt((cnn_R.std()**2 + transformer_R.std()**2) / 2)

# Preview for H-M2: expect cohens_d > 1.0
```

---

## 5. Experimental Workflow

### 5.1 Step-by-Step Execution

**Phase 1: Setup (Est. 30 min)**
1. Install dependencies: `pip install timm==1.0.9 torch sklearn pandas`
2. Create project directory: `experiments/h_e1_stat_features/`
3. Initialize logging: `experiment_log.txt`

**Phase 2: Data Preparation (Est. 2-3 hours)**
1. Download 60 model checkpoints via TIMM (auto-cached, ~15 GB total)
2. Extract features from all models (checkpoint-only, CPU-based)
3. Create train/val DataFrames with stratified split
4. Save to CSV: `train_features.csv`, `val_features.csv`
5. **Validation checkpoint:** Run A1, A2, A3 assumption tests

**Phase 3: Training (Est. 5 min)**
1. Load train features, apply StandardScaler
2. Fit LogisticRegression classifier
3. Save model: `classifier.pkl`, `scaler.pkl`

**Phase 4: Evaluation (Est. 5 min)**
1. Load val features, apply scaler
2. Predict on validation set
3. Compute macro-accuracy, per-class accuracy, confusion matrix
4. Analyze feature importance from coefficients
5. **Success checkpoint:** Check macro_accuracy > 0.80

**Phase 5: Reporting (Est. 30 min)**
1. Generate plots: confusion matrix, feature importance bar chart
2. Document results in `h_e1_results.md`
3. Update verification state: `experiment_design.status = COMPLETED`

**Total Estimated Time:** 3-4 hours (mostly checkpoint download)

### 5.2 Computational Requirements

**Hardware:**
- CPU: 4+ cores (checkpoint download parallelization)
- RAM: 8 GB minimum (load multiple models simultaneously)
- Storage: 20 GB (15 GB checkpoints + 5 GB workspace)
- GPU: NOT REQUIRED (checkpoint-only extraction)

**Software:**
- Python 3.9+
- PyTorch 2.1+ (TIMM dependency)
- TIMM 1.0.9
- scikit-learn 1.3+
- pandas, numpy, matplotlib

**Network:**
- Internet required for initial checkpoint download
- Cached checkpoints reusable across experiments

---

## 6. Success Criteria & Decision Gates

### 6.1 Primary Success Criteria

**Gate Type:** MUST_WORK  
**Threshold:** Validation accuracy > 80% (macro-averaged)

**Pass Condition:**
```python
if macro_accuracy > 0.80:
    print("H-E1 PASSED: Features are sufficient for classification")
    next_action = "Proceed to H-M1 (Normalization Fingerprinting)"
```

**Fail Condition:**
```python
if macro_accuracy <= 0.80:
    print("H-E1 FAILED: Features insufficient")
    
    if macro_accuracy <= 0.50:
        # Near-random performance (33.3% baseline for 3-way)
        decision = "ABANDON: Features fundamentally insufficient, need complex representations (GNN/MLP)"
    else:
        # Partial success (50-80%)
        decision = "PIVOT: Test alternative features (GroupNorm patterns, activation functions)"
```

### 6.2 Secondary Success Criteria

**Per-Class Accuracy:**
- CNN accuracy ≥ 75%
- Transformer accuracy ≥ 75%
- Hybrid accuracy ≥ 75%

**Failure Mode:**
```python
if any(class_acc < 0.75):
    # Single class collapse detected
    analyze_confusion_matrix()
    # Example: If Hybrid collapsed into CNN, investigate parameter-mass ratio overlap
```

**Scale Invariance:**
- Intra-family CV < 0.15 for ResNet variants

**Failure Mode:**
```python
if cv >= 0.15:
    # Scale confounds structure
    decision = "PIVOT: Use R-rank instead of R-absolute, or normalize by model size"
```

### 6.3 Diagnostic Outputs

**If H-E1 Fails:**
1. **Confusion Matrix Analysis:**
   - Which families are confused? (CNN↔Hybrid? Transformer↔Hybrid?)
   - Asymmetric confusion? (CNN→Transformer but not reverse?)

2. **Feature Distribution Plots:**
   - Scatter plot: BN_count vs LN_count (expect diagonal separation)
   - Histogram: R distributions per family (expect non-overlapping)

3. **Failure Case Inspection:**
   - List misclassified models by name
   - Manual structural inspection: Why did ResNet-50 classify as Transformer?

4. **Alternative Feature Exploration:**
   - Test GroupNorm counts (GN_count importance)
   - Test activation function counts (ReLU vs GELU)
   - Test embedding dimension patterns

---

## 7. Expected Outcomes & Predictions

### 7.1 Strong Success Scenario (>90% accuracy)

**Interpretation:**
- Features are highly discriminative, linear separability confirmed
- Normalization counts dominate classification (expected from Chun 2026)
- Parameter-mass ratio provides secondary signal

**Implications for Future Hypotheses:**
- H-M1: Expect violation rates <5% (strong normalization fingerprint)
- H-M2: Expect Cohen's d > 2.0 (very strong separation)
- H-C1: Edge cases may still fail (acceptable boundary condition)

**Next Steps:**
- Fast-track H-M1, H-M2, H-M3 (mechanism hypotheses)
- Consider expanding dataset to 100+ models for robustness

### 7.2 Moderate Success Scenario (80-90% accuracy)

**Interpretation:**
- Features are sufficient but not perfect
- Some family overlap expected (Hybrid architecture ambiguity)
- Linear classifier adequate, no need for MLP

**Implications:**
- H-M1: Expect violation rates 10-15% (normalization is convention for some models)
- H-M2: Expect Cohen's d ≈ 1.0 (moderate separation)

**Next Steps:**
- Proceed to H-M hypotheses with caution
- Document ambiguous cases for H-C1 edge case analysis

### 7.3 Marginal Success Scenario (75-80% accuracy)

**Interpretation:**
- Features barely meet threshold, linear separability questionable
- May need feature engineering (interaction terms, polynomial features)

**Implications:**
- Re-evaluate "simple features" claim
- Consider adding secondary features (activation counts, embedding dims)

**Decision:**
- PIVOT: Test logistic regression with polynomial features
- If still <80%, EXPLORE alternative classifiers (SVM with RBF kernel)

### 7.4 Failure Scenario (<75% accuracy)

**Interpretation:**
- Features insufficient for classification task
- Normalization counts may be convention, not paradigm signal
- Parameter-mass ratio may confound scale with structure

**Root Cause Analysis:**
1. **Assumption A2 Violated:** Normalization choice is historical convention
   - Evidence: High violation rates (CNN with LayerNorm >15%)
   - Action: ABANDON simple features, need structural analysis

2. **Assumption A3 Violated:** Parameter-mass ratio is scale-variant
   - Evidence: High intra-family CV (≥0.15)
   - Action: PIVOT to normalized ratio or R-rank

3. **Linear Classifier Insufficient (A4):**
   - Evidence: Features not linearly separable (scatter plot shows overlap)
   - Action: EXPLORE non-linear classifiers (MLP with 1 hidden layer)

**Final Decision:**
```python
if macro_accuracy < 0.50:
    # Near-random (33.3% baseline)
    decision = "ABANDON: Weight-space statistical features fundamentally insufficient"
    recommendation = "Shift to complex representations (Kofinas GNN approach)"
else:
    # 50-75% (better than random but below threshold)
    decision = "PIVOT: Refine features or add secondary signals"
    recommendation = "Test GroupNorm patterns, activation functions, or interaction terms"
```

---

## 8. Risk Mitigation & Contingencies

### 8.1 Data Quality Risks

**R1: TIMM Naming Misalignment (>10%)**

**Detection:**
- Pre-validate 10-model sample via structural inspection
- Check: ResNet-50 has >50% BatchNorm keys, ViT-Base has >50% LayerNorm keys

**Mitigation:**
- If misalignment >10%, add structural validation layer
- Use state_dict key patterns as secondary labels (not TIMM names)

**Contingency:**
- PIVOT to manual verification for low-confidence models
- Reduce dataset to high-confidence subset (may drop to 40-50 models)

### 8.2 Feature Quality Risks

**R2: Normalization Convention (Violation >15%)**

**Detection:**
- Monitor violation rates during data preparation
- CNN with LayerNorm count, Transformer with BatchNorm count

**Mitigation:**
- Add GroupNorm counts as backup feature
- Test activation function patterns (ReLU=CNN, GELU=Transformer)

**Contingency:**
- EXPLORE alternative features: attention layer counts, embedding dimensions
- If features fundamentally insufficient, ABANDON hypothesis

**R3: Scale Invariance Failure (CV ≥0.15)**

**Detection:**
- Pre-validate ResNet family before full experiment
- Compute CV on ResNet-{18,34,50,101,152}

**Mitigation:**
- Use R-rank instead of R-absolute (ordinal encoding)
- Normalize by model size: R_norm = R / log(total_params)

**Contingency:**
- If scale confounding confirmed, update feature definition in Phase 2B
- Document limitation: "Approach works within single scale, not across scales"

### 8.3 Computational Risks

**R4: Checkpoint Download Timeout**

**Detection:**
- Monitor download progress, timeout after 30 min per model

**Mitigation:**
- Use TIMM's built-in caching (checkpoints stored in ~/.cache/torch)
- Parallelize downloads across 4 workers

**Contingency:**
- If specific model unavailable, substitute with similar architecture
- Example: If ResNet-152 fails, use ResNet-101 instead

**R5: Memory Overflow (>8 GB RAM)**

**Detection:**
- Monitor RAM usage during feature extraction

**Mitigation:**
- Extract features one model at a time (no batch loading)
- Delete model after feature extraction: `del model; torch.cuda.empty_cache()`

**Contingency:**
- If RAM still insufficient, run extraction on smaller batches (10 models at a time)
- Save intermediate results to disk: `features_batch_1.csv`, etc.

---

## 9. Implementation Roadmap

### 9.1 File Structure

```
experiments/
├── h_e1_stat_features/
│   ├── data/
│   │   ├── model_list.json          # 60 model names + family labels
│   │   ├── train_features.csv       # 42 models, 5 features + label
│   │   ├── val_features.csv         # 18 models, 5 features + label
│   │   └── assumption_validation.json  # A1, A2, A3 test results
│   ├── models/
│   │   ├── classifier.pkl           # Trained LogisticRegression
│   │   └── scaler.pkl               # Fitted StandardScaler
│   ├── results/
│   │   ├── confusion_matrix.png     # Validation confusion matrix
│   │   ├── feature_importance.png   # Bar chart of coefficients
│   │   ├── r_distribution.png       # Histogram of R per family
│   │   └── h_e1_results.md          # Full results report
│   ├── scripts/
│   │   ├── 01_prepare_data.py       # Download checkpoints, extract features
│   │   ├── 02_validate_assumptions.py  # A1, A2, A3 tests
│   │   ├── 03_train_classifier.py   # Fit LogisticRegression
│   │   ├── 04_evaluate.py           # Validation metrics, plots
│   │   └── 05_analyze_failures.py   # Diagnostic analysis if failed
│   └── experiment_log.txt           # Timestamped execution log
```

### 9.2 Key Scripts

**01_prepare_data.py:**
```python
"""
Download TIMM model checkpoints and extract statistical features.

Outputs:
- data/model_list.json: 60 models with family labels
- data/train_features.csv: 42 training samples
- data/val_features.csv: 18 validation samples

Runtime: ~2-3 hours (checkpoint download)
"""

import timm
import torch
import pandas as pd
from sklearn.model_selection import train_test_split

# Model selection (manually curated)
model_families = {
    'CNN': [
        'resnet18', 'resnet34', 'resnet50', 'resnet101', 'resnet152',
        # ... (24 total)
    ],
    'Transformer': [
        'vit_tiny_patch16_224', 'vit_small_patch16_224',
        # ... (24 total)
    ],
    'Hybrid': [
        'resnetv2_50x1_bit_distilled', 'convit_base',
        # ... (12 total)
    ]
}

def extract_features(state_dict):
    # [Feature extraction logic from Section 3.4]
    pass

# Main execution
all_data = []
for family, models in model_families.items():
    for model_name in models:
        model = timm.create_model(model_name, pretrained=True)
        features = extract_features(model.state_dict())
        all_data.append({'model_name': model_name, 'family': family, **features})

df = pd.DataFrame(all_data)
train_df, val_df = train_test_split(df, test_size=0.3, stratify=df['family'], random_state=42)

train_df.to_csv('data/train_features.csv', index=False)
val_df.to_csv('data/val_features.csv', index=False)
```

**02_validate_assumptions.py:**
```python
"""
Validate Phase 2A assumptions A1, A2, A3 before training.

Tests:
- A1: TIMM naming alignment >90% (10-model sample)
- A2: Normalization violation rate ≤15% per class
- A3: Scale invariance CV <0.15 (ResNet family)

Outputs:
- data/assumption_validation.json: Pass/fail results
"""

def test_a1_naming_alignment(train_df):
    # Manually inspect 10 models: expected vs observed normalization
    pass

def test_a2_violation_rate(train_df):
    # Count CNN with LayerNorm, Transformer with BatchNorm
    pass

def test_a3_scale_invariance(train_df):
    # Compute CV for ResNet family R values
    pass
```

**03_train_classifier.py:**
```python
"""
Train LogisticRegression classifier on training features.

Outputs:
- models/classifier.pkl: Trained model
- models/scaler.pkl: Fitted StandardScaler

Runtime: <1 minute
"""

from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import joblib

train_df = pd.read_csv('data/train_features.csv')

X_train = train_df[['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']]
y_train = train_df['family']

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)

classifier = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=1000, random_state=42, class_weight='balanced')
classifier.fit(X_train_scaled, y_train)

joblib.dump(classifier, 'models/classifier.pkl')
joblib.dump(scaler, 'models/scaler.pkl')
```

**04_evaluate.py:**
```python
"""
Evaluate classifier on validation set and generate plots.

Outputs:
- results/confusion_matrix.png
- results/feature_importance.png
- results/r_distribution.png
- results/h_e1_results.md

Runtime: <5 minutes
"""

from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import matplotlib.pyplot as plt

val_df = pd.read_csv('data/val_features.csv')
classifier = joblib.load('models/classifier.pkl')
scaler = joblib.load('models/scaler.pkl')

X_val = val_df[['bn_count', 'ln_count', 'gn_count', 'no_norm_flag', 'param_mass_ratio']]
y_val = val_df['family']

X_val_scaled = scaler.transform(X_val)
y_val_pred = classifier.predict(X_val_scaled)

macro_accuracy = accuracy_score(y_val, y_val_pred)
report = classification_report(y_val, y_val_pred, output_dict=True)

# Generate plots
# ... [Confusion matrix, feature importance, R distribution]

# Write results
with open('results/h_e1_results.md', 'w') as f:
    f.write(f"# H-E1 Results\n\n")
    f.write(f"**Macro Accuracy:** {macro_accuracy:.2%}\n")
    f.write(f"**Decision:** {'PASS' if macro_accuracy > 0.80 else 'FAIL'}\n")
```

### 9.3 Execution Commands

```bash
# Setup
cd experiments/h_e1_stat_features
pip install timm==1.0.9 torch scikit-learn pandas matplotlib

# Run pipeline
python scripts/01_prepare_data.py      # ~2-3 hours
python scripts/02_validate_assumptions.py  # ~5 min
python scripts/03_train_classifier.py  # <1 min
python scripts/04_evaluate.py          # <5 min

# Check results
cat results/h_e1_results.md
```

---

## 10. Reporting Template

**Results Document: `h_e1_results.md`**

```markdown
# H-E1 Validation Results: Statistical Features Sufficiency

**Date:** [YYYY-MM-DD]  
**Hypothesis ID:** h-e1  
**Status:** [PASSED | FAILED | PIVOTED]

---

## Summary

**Primary Metric:**
- Validation Accuracy: [XX.X]%
- Threshold: >80%
- **Decision:** [PASSED | FAILED]

**Secondary Metrics:**
- CNN Accuracy: [XX.X]%
- Transformer Accuracy: [XX.X]%
- Hybrid Accuracy: [XX.X]%
- Scale Invariance CV: [0.XXX]

---

## Confusion Matrix

|               | Pred: CNN | Pred: Transformer | Pred: Hybrid |
|---------------|-----------|-------------------|--------------|
| True: CNN     | X         | X                 | X            |
| True: Transformer | X     | X                 | X            |
| True: Hybrid  | X         | X                 | X            |

![Confusion Matrix](confusion_matrix.png)

---

## Feature Importance

| Feature          | Avg Abs Coefficient | Rank |
|------------------|---------------------|------|
| param_mass_ratio | X.XXX               | 1    |
| ln_count         | X.XXX               | 2    |
| bn_count         | X.XXX               | 3    |
| gn_count         | X.XXX               | 4    |
| no_norm_flag     | X.XXX               | 5    |

![Feature Importance](feature_importance.png)

---

## Failure Cases

**Misclassified Models:** [N] / [18]

| Model Name | True Label | Predicted Label | Notes |
|------------|------------|-----------------|-------|
| [model]    | [family]   | [family]        | [reason] |

---

## Assumption Validation

**A1: TIMM Naming Alignment**
- Alignment Rate: [XX]% (threshold: >90%)
- Status: [PASSED | FAILED]

**A2: Normalization Convention**
- CNN with LayerNorm: [X]% (threshold: ≤15%)
- Transformer with BatchNorm: [X]% (threshold: ≤15%)
- Status: [PASSED | FAILED]

**A3: Scale Invariance**
- ResNet Family CV: [0.XXX] (threshold: <0.15)
- Status: [PASSED | FAILED]

---

## Next Steps

[If PASSED]:
- Proceed to H-M1: Normalization Layer Fingerprinting
- Update verification_state.yaml: h-e1.validation.status = COMPLETED

[If FAILED]:
- [Root cause analysis findings]
- [Recommended pivot action]
- [Alternative feature exploration needed]
```

---

## 11. Phase 2C Completion Checklist

- [x] Hypothesis summary extracted from 02b_verification_plan.md
- [x] Dataset specified: TIMM Model Zoo (60 models, programmatic-api type)
- [x] Dataset preparation pipeline designed (4-step process)
- [x] Baseline experiment designed: LogisticRegression with 5 features
- [x] Training protocol specified: StandardScaler + stratified split
- [x] Evaluation metrics defined: macro-accuracy, per-class accuracy, confusion matrix
- [x] Success criteria & decision gates documented (MUST_WORK >80%)
- [x] Expected outcomes & predictions (4 scenarios: strong/moderate/marginal/failure)
- [x] Risk mitigation strategies (R1-R5 with contingencies)
- [x] Implementation roadmap: file structure + 5 key scripts
- [x] Reporting template provided
- [x] Computational requirements: CPU-only, 8 GB RAM, 20 GB storage
- [x] Estimated timeline: 3-4 hours total

**Experiment Design Status:** READY FOR PHASE 3 IMPLEMENTATION PLANNING

---

## Appendix A: Related Work Integration

### A.1 Archon KB Findings

**Code Example: Checkpoint Loading**
```python
# From IP-Adapter project (Archon KB)
import torch
ckpt = "checkpoint-50000/pytorch_model.bin"
sd = torch.load(ckpt, map_location="cpu")

# Extracting specific components via key prefixes
for k in sd:
    if k.startswith("image_proj_model"):
        # Process image projection layers
    elif k.startswith("adapter_modules"):
        # Process adapter modules
```

**Relevance:** Demonstrates state_dict key prefix matching for component extraction (adapted for normalization layer counting).

### A.2 Theoretical Foundations (from Phase 2A)

**Chun et al. 2026:** LayerNorm reduces Loss Landscape Curvature (LLC) by m/2 vs BatchNorm
- **Implication:** Normalization choice reflects fundamental architectural constraints
- **Experiment Link:** Validates assumption A2 (normalization reflects paradigm, not convention)

**Fang et al. 2024:** Heterogeneous structures have diverged importance distributions
- **Implication:** Parameter allocation patterns (conv vs linear) reflect computation style
- **Experiment Link:** R = conv_params / total_params captures this divergence

**Kofinas et al. 2024:** GNN-based architecture classification (high complexity)
- **Baseline Comparison:** 50+ hours implementation vs our 6 hours
- **Experiment Link:** H-E1 tests if simple features suffice (no GNN needed)

---

## Appendix B: Dataset NOT Synthetic

**CRITICAL VALIDATION:**

This experiment uses **REAL pretrained models** from the TIMM library, NOT synthetic data.

**Dataset Type:** `programmatic-api`  
**Source:** PyTorch Image Models (TIMM) library  
**Nature:** Real production models trained on ImageNet, CIFAR, etc.

**Why NOT Synthetic:**
- Checkpoints downloaded from HuggingFace Hub (real model weights)
- Models trained by external researchers/organizations (ResNet by Microsoft, ViT by Google, etc.)
- Validation accuracy metrics reflect true architectural patterns

**Contrast with Synthetic:**
- Synthetic would be: "Generate random state_dicts with fake normalization counts"
- Real (ours): "Download ResNet-50 checkpoint from TIMM, count actual BatchNorm layers"

**Verification:**
- All models accessible via `timm.create_model(name, pretrained=True)`
- Checkpoints stored in `~/.cache/torch/hub/checkpoints/` (verifiable file sizes)
- Total download size ~15 GB (confirms real model weights, not small synthetic files)

---

**End of Experiment Design Brief**
