# Experiment Design: H-E1 Gradient Abnormality Detection

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Status:** Design Complete  
**Date:** 2026-08-20  

---

## Executive Summary

**Objective:** Validate that minority group samples exhibit significantly higher GAIA-Z gradient abnormality scores than majority group samples on Waterbirds dataset.

**Approach:** Train ResNet-50 on Waterbirds with 90% spurious correlation, extract GradCAM gradients from all test samples, compute GAIA-Z scores, perform statistical comparison.

**Success Criteria:** GAIA-Z(minority) ≥ GAIA-Z(majority) + 0.2, p<0.01, Cohen's d≥0.8

**Timeline:** ~4 hours total (3hr training + 1hr analysis)

---

## 1. Hypothesis Statement

**Full Statement:**
> Under deep neural networks trained on Waterbirds dataset with 90% spurious correlation, if we compute GAIA-Z gradient abnormality metrics for test samples, then minority group samples (waterbird-land, landbird-water) will exhibit scores ≥0.2 higher than majority group samples because spurious reliance creates gradient scattering when shortcuts conflict with core features.

**Variables:**
- Independent: Test sample group membership (Majority vs Minority)
- Dependent: GAIA-Z score (zero-deflation ratio, range [0,1])
- Controlled: Model architecture (ResNet-50), training hyperparameters, image complexity

**Verification Protocol:**
1. Train ResNet-50 on Waterbirds 90% correlation, verify WGA <80%
2. Compute GAIA-Z for all 5794 test samples via GradCAM attribution gradients
3. Statistical test: two-sample t-test comparing minority vs majority mean GAIA-Z
4. Measure effect size via Cohen's d to quantify practical significance

---

## 2. Dataset

### 2.1 Specification

```yaml
dataset:
  name: Waterbirds
  type: standard
  source: WILDS benchmark
  version: v1.0
  access_method: wilds.get_dataset('waterbirds', download=True)
  cache_path: ~/.wilds/waterbirds_v1.0/
  license: Open (academic use)
  
splits:
  train: 4795 samples
  validation: 1199 samples
  test: 5794 samples  # PRIMARY EVALUATION
  
structure:
  classes: 2  # waterbird=0, landbird=1
  backgrounds: 2  # water=0, land=1
  groups: 4  # class × background
    - group_0: waterbird-water (MAJORITY, ~3498 train, 90%)
    - group_1: waterbird-land (MINORITY, ~184 train, 10%)
    - group_2: landbird-water (MINORITY, ~467 train, 10%)
    - group_3: landbird-land (MAJORITY, ~3626 train, 90%)
  
spurious_correlation:
  training: 90%  # background correlates with class
  test: 50%  # balanced across groups
  
image_properties:
  resolution: 224×224
  format: RGB
  normalization: ImageNet (mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
```

### 2.2 Data Loading

```python
from wilds import get_dataset

# Load dataset
dataset = get_dataset('waterbirds', download=True, root_dir='~/.wilds')

# Access splits
train_data = dataset.get_subset('train')
val_data = dataset.get_subset('val')
test_data = dataset.get_subset('test')

# Get metadata (class, background, group)
metadata_array = dataset.metadata_array
# metadata_array[:, 0] = class (y)
# metadata_array[:, 1] = background
# metadata_array[:, 2] = group_id (0-3)
```

### 2.3 Verification Checklist

- [ ] Dataset downloads successfully (11,788 images total)
- [ ] Test set contains 5794 samples
- [ ] Group labels accessible via metadata_array
- [ ] Training split has ~90% correlation (group 0,3 >> group 1,2)
- [ ] Test split balanced across 4 groups

---

## 3. Model

### 3.1 Architecture

```yaml
model:
  architecture: ResNet-50
  source: torchvision.models.resnet50
  pretrained: ImageNet
  modifications:
    - Replace fc layer: 1000 → 2 classes
  target_layer: layer4  # For GradCAM (final conv block)
```

### 3.2 Training Configuration

```yaml
training:
  optimizer:
    type: SGD
    lr: 1e-3
    momentum: 0.9
    weight_decay: 1e-4
  
  batch_size: 128
  epochs: 300
  early_stopping:
    metric: worst_group_accuracy
    patience: 50
  
  loss: CrossEntropyLoss
  
  scheduler:
    type: CosineAnnealingLR
    T_max: 300
  
  seed: 42
```

### 3.3 Expected Performance

```yaml
performance_targets:
  average_accuracy: ">95%"
  worst_group_accuracy: "<80%"  # Confirms spurious learning
  minority_accuracy: "≥60%"     # Required for GradCAM validity (A1)
  
group_breakdown:
  group_0_acc: "~97%"  # waterbird-water (majority, aligned)
  group_1_acc: "~65%"  # waterbird-land (minority, conflict)
  group_2_acc: "~65%"  # landbird-water (minority, conflict)
  group_3_acc: "~97%"  # landbird-land (majority, aligned)
```

### 3.4 Training Code Skeleton

```python
import torch
import torch.nn as nn
from torchvision import models
from wilds import get_dataset
from wilds.common.data_loaders import get_train_loader, get_eval_loader

# Load data
dataset = get_dataset('waterbirds', download=True)
train_data = dataset.get_subset('train')

# Initialize model
model = models.resnet50(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, 2)  # 2 classes
model = model.cuda()

# Training loop
optimizer = torch.optim.SGD(model.parameters(), lr=1e-3, momentum=0.9, weight_decay=1e-4)
criterion = nn.CrossEntropyLoss()

for epoch in range(300):
    # Standard training
    # Track WGA and minority accuracy
    pass
```

---

## 4. Gradient Collection & GAIA-Z Computation

### 4.1 GradCAM Setup

```python
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

# Initialize GradCAM
target_layers = [model.layer4]
cam = GradCAM(model=model, target_layers=target_layers)

# For each test sample
for img, label, metadata in test_loader:
    # Forward pass
    output = model(img)
    pred_class = output.argmax(dim=1)
    
    # Get GradCAM gradients
    targets = [ClassifierOutputTarget(pred_class.item())]
    grayscale_cam = cam(input_tensor=img, targets=targets)
    
    # Extract raw gradients (from cam internals)
    gradients = cam.activations_and_grads.gradients[0]
    # Shape: (batch, 2048, 7, 7) for ResNet-50 layer4
    
    # Store for GAIA-Z computation
    store_gradient(gradients, metadata['group'])
```

### 4.2 GAIA-Z Metric

```python
import numpy as np

def compute_gaia_z(gradient_tensor, epsilon=1e-6):
    """
    Compute GAIA-Z: zero-deflation ratio
    
    Args:
        gradient_tensor: numpy array (C, H, W) or flattened
        epsilon: near-zero threshold
    
    Returns:
        gaia_z: float in [0, 1]
    """
    flat_grad = gradient_tensor.flatten()
    near_zero_count = np.sum(np.abs(flat_grad) < epsilon)
    total_elements = flat_grad.size
    
    gaia_z = near_zero_count / total_elements
    return gaia_z

# Apply to all test samples
gaia_z_scores = []
for grad, group_id in gradient_data:
    score = compute_gaia_z(grad)
    gaia_z_scores.append({
        'gaia_z': score,
        'group': group_id,
        'is_minority': group_id in [1, 2]
    })
```

### 4.3 Data Storage

```python
# Save gradients (optional, for debugging)
np.savez_compressed(
    'gradients.npz',
    gradients=all_gradients,
    group_ids=all_group_ids,
    predictions=all_predictions
)

# Save GAIA-Z scores (required)
import pandas as pd
df = pd.DataFrame(gaia_z_scores)
df.to_csv('gaia_z_scores.csv', index=False)
```

---

## 5. Statistical Analysis

### 5.1 Primary Test

```python
from scipy.stats import ttest_ind
import numpy as np

# Separate by group type
minority_scores = df[df['is_minority'] == True]['gaia_z'].values
majority_scores = df[df['is_minority'] == False]['gaia_z'].values

# Two-sample t-test (Welch's, unequal variance)
t_stat, p_value = ttest_ind(minority_scores, majority_scores, equal_var=False)

# Compute means
mean_minority = np.mean(minority_scores)
mean_majority = np.mean(majority_scores)
divergence = mean_minority - mean_majority

# Cohen's d effect size
pooled_std = np.sqrt((np.var(minority_scores) + np.var(majority_scores)) / 2)
cohens_d = divergence / pooled_std

print(f"Minority Mean: {mean_minority:.4f}")
print(f"Majority Mean: {mean_majority:.4f}")
print(f"Divergence: {divergence:.4f}")
print(f"p-value: {p_value:.4e}")
print(f"Cohen's d: {cohens_d:.4f}")
```

### 5.2 Success Criteria Evaluation

```python
# Primary criteria
primary_pass = (divergence >= 0.2) and (p_value < 0.01)

# Secondary criteria
secondary_pass = (cohens_d >= 0.8)

# Overall gate
gate_pass = primary_pass and secondary_pass

if gate_pass:
    print("✓ H-E1 PASSED: Gradient abnormality exists in minority groups")
else:
    print("✗ H-E1 FAILED: ABANDON gradient abnormality approach")
    if divergence < 0.2:
        print(f"  - Divergence insufficient: {divergence:.4f} < 0.2")
    if p_value >= 0.01:
        print(f"  - Not statistically significant: p={p_value:.4f}")
    if cohens_d < 0.8:
        print(f"  - Effect size too small: d={cohens_d:.4f} < 0.8")
```

### 5.3 Visualization

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Box plot
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# By group type (minority vs majority)
sns.boxplot(data=df, x='is_minority', y='gaia_z', ax=axes[0])
axes[0].set_title('GAIA-Z by Group Type')
axes[0].set_xlabel('Minority Group')
axes[0].set_ylabel('GAIA-Z Score')

# By individual group (4 groups)
sns.boxplot(data=df, x='group', y='gaia_z', ax=axes[1])
axes[1].set_title('GAIA-Z by Group ID')
axes[1].set_xlabel('Group ID')
axes[1].axhline(mean_minority, color='red', linestyle='--', label='Minority Avg')
axes[1].axhline(mean_majority, color='blue', linestyle='--', label='Majority Avg')
axes[1].legend()

plt.tight_layout()
plt.savefig('gaia_z_comparison.png', dpi=300)
```

---

## 6. Implementation Timeline

### 6.1 Execution Plan

| Step | Task | Duration | Deliverable |
|------|------|----------|-------------|
| 1 | Setup environment + download data | 30 min | Dataset cached, dependencies installed |
| 2 | Train ResNet-50 | 3 hours | trained_model.pth, training_log.csv |
| 3 | Verify WGA <80% | 5 min | Performance report |
| 4 | Extract GradCAM gradients | 15 min | gradients.npz (5794 samples) |
| 5 | Compute GAIA-Z scores | 5 min | gaia_z_scores.csv |
| 6 | Statistical analysis | 10 min | statistical_results.json |
| 7 | Generate visualizations | 5 min | plots/ |
| **Total** | | **~4 hours** | Complete h-e1 validation |

### 6.2 Directory Structure

```
experiments/h_e1_detection/
├── configs/
│   └── config.yaml                 # Hyperparameters
├── data/                           # Auto-generated by WILDS
│   └── waterbirds_v1.0/
├── checkpoints/
│   └── trained_model.pth
├── outputs/
│   ├── gradients.npz               # Optional (debugging)
│   ├── gaia_z_scores.csv           # Required
│   ├── statistical_results.json    # Required
│   └── training_log.csv
├── plots/
│   ├── gaia_z_comparison.png
│   ├── gaia_z_histogram.png
│   └── training_curves.png
├── train_model.py
├── collect_gradients.py
├── compute_gaia_z.py
├── statistical_test.py
└── utils/
    ├── gradcam.py
    ├── gaia_metrics.py
    └── visualization.py
```

---

## 7. Validation & Quality Checks

### 7.1 Training Validation

```python
# After training completes
def validate_training(model, test_loader, metadata):
    # Compute group accuracies
    group_correct = {0: 0, 1: 0, 2: 0, 3: 0}
    group_total = {0: 0, 1: 0, 2: 0, 3: 0}
    
    for img, label, meta in test_loader:
        pred = model(img).argmax(dim=1)
        group_id = meta['group'].item()
        
        group_total[group_id] += 1
        if pred == label:
            group_correct[group_id] += 1
    
    # Compute metrics
    group_accs = {g: group_correct[g]/group_total[g] for g in range(4)}
    wga = min(group_accs.values())
    minority_acc = (group_accs[1] + group_accs[2]) / 2
    avg_acc = sum(group_correct.values()) / sum(group_total.values())
    
    # Validation checks
    assert wga < 0.80, f"WGA too high: {wga:.2%} (expected <80%)"
    assert minority_acc >= 0.60, f"Minority acc too low: {minority_acc:.2%} (A1 violation)"
    assert avg_acc > 0.95, f"Avg acc too low: {avg_acc:.2%}"
    
    print("✓ Training validation passed")
    return group_accs, wga, minority_acc, avg_acc
```

### 7.2 GAIA-Z Validation

```python
# Check GAIA-Z scores are meaningful
def validate_gaia_z_scores(df):
    # Not all identical
    assert df['gaia_z'].std() > 0.01, "GAIA-Z scores degenerate (no variance)"
    
    # Within valid range
    assert df['gaia_z'].min() >= 0.0, "GAIA-Z < 0 (invalid)"
    assert df['gaia_z'].max() <= 1.0, "GAIA-Z > 1 (invalid)"
    
    # Reasonable distribution
    median_score = df['gaia_z'].median()
    assert 0.1 < median_score < 0.9, f"GAIA-Z median suspect: {median_score:.4f}"
    
    print("✓ GAIA-Z validation passed")
```

---

## 8. Risk Mitigation

### 8.1 Critical Assumptions

**A1: Minority group samples correctly classified ≥60%**
- Monitor: Check minority_acc during training
- Fallback: If <60%, flag assumption violation → use global regularization (not spatial)

**A3: Gradient scattering caused by spurious conflict, not complexity**
- Validation: Waterbirds has controlled backgrounds (low complexity variance)
- Post-hoc test (optional): Swap backgrounds on 100 minority samples → expect GAIA-Z drop ≥30%

### 8.2 Failure Modes

| Failure | Detection | Response |
|---------|-----------|----------|
| WGA ≥80% | After training | Retrain with different seed/hyperparameters |
| Minority acc <60% | After training | Flag A1 violation, pivot to global regularization |
| GAIA-Z divergence <0.2 | Statistical test | FAIL gate, abandon approach |
| p-value ≥0.01 | Statistical test | FAIL gate, check sample size/variance |
| Cohen's d <0.8 | Effect size | FAIL gate (weak effect) |

---

## 9. Success Criteria (Gate: MUST_WORK)

### 9.1 Primary

✓ **Divergence:** GAIA-Z(minority) - GAIA-Z(majority) ≥ 0.2  
✓ **Significance:** p-value < 0.01 (two-sample t-test)

### 9.2 Secondary

✓ **Effect Size:** Cohen's d ≥ 0.8 (large effect)

### 9.3 Quality Gates

✓ **Training:** WGA <80%, minority_acc ≥60%  
✓ **Data:** 5794 test samples with GAIA-Z scores  
✓ **Reproducibility:** Seed=42, deterministic results

### 9.4 Gate Decision

```
IF (divergence ≥ 0.2) AND (p < 0.01) AND (d ≥ 0.8):
    → h-e1 PASSES
    → Proceed to h-m-integrated (mechanism validation)
ELSE:
    → h-e1 FAILS
    → ABANDON gradient abnormality approach
    → Block h-m-integrated, h-m-mitigate
```

---

## 10. Next Steps

**If h-e1 Passes:**
1. Proceed to h-m-integrated experiment design
2. Design correlation sweep (50%-95% spurious rates)
3. Plan augmentation causality test

**If h-e1 Fails:**
1. Analyze failure mode (divergence vs significance vs effect size)
2. Investigate: visualization of GAIA-Z distributions, sample-level inspection
3. Decision: ABANDON or reformulate hypothesis

---

**Document Status:** Complete  
**Dependencies:** None (foundation hypothesis)  
**Blocks:** h-m-integrated, h-m-mitigate (both require h-e1 pass)  
**Archon Task:** 28693385-e2a4-42df-ba9a-8f8e903c76bb  
**Phase Task:** e5e29855-a636-4d17-b973-516946a29a29
