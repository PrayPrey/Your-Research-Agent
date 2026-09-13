# Experiment Design: h-m3

**Date:** 2026-04-21
**Author:** Anonymous
**Hypothesis Statement:** Under pretrained CNN training with batch normalization, if normalization statistics accumulate across 50+ layers versus <34 layers, then batch norm layer weight distributions will differ, because cumulative normalization effects scale with depth.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Validates specific causal mechanism contribution.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** YES (h-m2 COMPLETED with 100% accuracy)
**Gate Status:** SHOULD_WORK (>50% threshold)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m3
- **Type:** Mechanism
- **Prerequisites:** h-m2 (Architectural Constraints)

### Gate Condition
**Gate Type:** SHOULD_WORK
**Threshold:** Test accuracy >50%
**Fail Action:** Document as limitation, gradient/architecture dominate

---

## Continuation Context

This is the third and final mechanism hypothesis in a sequential causal chain investigating why weight statistics enable depth classification:
- **H-E1** (Foundation): Validated that weight statistics achieve 100% depth classification
- **H-M1** (Gradient Flow): Tested gradient accumulation - REJECTED (features were architectural, not training-induced)
- **H-M2** (Architectural Constraints): Validated architectural features (residual blocks, bottlenecks) - CONFIRMED as mechanism
- **H-M3** (Normalization Effects): Tests whether batch normalization contributes additional signal

**Key Insight from H-M1 & H-M2:** Random initialization test revealed that features are purely architectural. Both H-M1 and H-M2 achieved 100% accuracy with random models, confirming the mechanism is structural (architecture definition) rather than training-induced.

### Previous Hypothesis Results (h-m2)

**H-M2 Validation Results:**
- **Test Accuracy:** 100% (4/4) - Perfect classification
- **Gate Status:** PASS (100% >> 50% threshold)
- **Mechanism Status:** ARCHITECTURAL (confirmed)
- **Random Test Accuracy:** 100% (same as pretrained)
- **Within-Family Validation:** PASS (ResNet: 100%, DenseNet: 100%)

**H-M2 Key Features (8 architectural features):**
1. Residual Block Count
2. Dense Connection Count
3. Bottleneck Ratio (most important: +0.956 coefficient)
4. Layer Count (second most important: +0.932 coefficient)
5. Skip Connection Presence
6. Residual Path Norm
7. Transition Layer Count
8. Architecture Family

**Optimal Configuration (reused from H-E1):**
- Classifier: LogisticRegression (C=1.0, solver='lbfgs', max_iter=1000, random_state=42)
- Feature Normalization: StandardScaler
- Train/Test Split: 80/20 stratified (16 train, 4 test, seed=42)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** Archon MCP unavailable in this session. Design based on validated patterns from H-E1, H-M1, H-M2.

**Batch Normalization in Depth Classification:**
- Batch normalization layers are standard in modern CNNs (ResNet, DenseNet, MobileNet)
- PyTorch provides `nn.BatchNorm2d` with accessible `weight` and `bias` parameters
- Batch norm statistics: `running_mean`, `running_var`, `weight` (gamma), `bias` (beta)
- Deep networks accumulate more batch norm layers (proportional to depth)

**Relevant Patterns from Previous Hypotheses:**
- H-M2 showed architectural features (layer counts, block structures) are discriminative
- Random initialization test is critical for mechanism validation
- Within-family validation tests depth signal robustness

### Archon Code Examples

**Note:** Archon MCP unavailable. Implementation based on PyTorch standard patterns.

**Batch Norm Parameter Extraction Pattern:**
```python
# Standard PyTorch pattern for extracting batch norm layers
bn_layers = [m for m in model.modules() if isinstance(m, nn.BatchNorm2d)]
bn_weights = [bn.weight.data.cpu().numpy() for bn in bn_layers]
bn_biases = [bn.bias.data.cpu().numpy() for bn in bn_layers]
```

### Exa GitHub Implementations

**Note:** Exa MCP unavailable. Design based on established batch normalization literature.

**Batch Normalization Feature Engineering:**
- Standard approach: Extract statistics from all batch norm layers
- Common features: mean/std of gamma (weight), mean/std of beta (bias)
- Layer-wise features: Count of batch norm layers, position distribution

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Implementation Strategy:** Custom feature extraction from pretrained models (no external reproduction needed)

**Recommended Implementation Path:**
- Primary: **PyTorch torchvision models + sklearn classifier** (same as H-E1, H-M1, H-M2)
- Fallback: Not applicable (self-contained implementation)
- Justification: Proven pipeline from H-E1/H-M1/H-M2, only feature extraction changes

### Code Analysis (Serena MCP)

**Note:** Serena MCP unavailable. Design based on PyTorch documentation and previous validation reports.

**Implementation Approach:**
1. Load 20 pretrained models (same as H-E1/H-M1/H-M2)
2. Extract batch normalization-specific features
3. Train binary classifier (shallow vs deep)
4. Evaluate with random initialization test (mechanism validation)

---

## Experiment Specification

### Dataset

**Dataset Name:** PyTorch Torchvision Pretrained Models  
**Type:** standard  
**Source:** torchvision.models (PyTorch official)

**Model Pool:**
- **Total Models:** 20 pretrained ImageNet CNNs
- **Shallow (10 models, ≤34 layers):** resnet18, resnet34, vgg11, vgg13, vgg16, vgg19, alexnet, squeezenet1_0, mobilenet_v2, densenet121
- **Deep (10 models, ≥50 layers):** resnet50, resnet101, resnet152, densenet161, densenet169, densenet201, wide_resnet50_2, wide_resnet101_2, resnext50_32x4d, resnext101_32x8d

**Architecture Families:**
- ResNet: 9 models (2 shallow, 7 deep)
- VGG: 4 models (4 shallow, 0 deep)
- DenseNet: 4 models (1 shallow, 3 deep)
- Other: 3 models (AlexNet, SqueezeNet, MobileNet)

**Loading Information** (for Phase 4 download):
- Method: torchvision.models
- Identifier: Model function names (e.g., `resnet50`, `vgg16`)
- Code: `torchvision.models.{model_name}(pretrained=True)`

**Split Strategy:**
- Train: 16 models (80%, stratified by depth)
- Test: 4 models (20%, stratified by depth)
- Random Seed: 42 (for reproducibility)

**Preprocessing:** None required (feature extraction only, no forward passes)

**Batch Normalization Coverage:**
- ResNet: Yes (all ResNet models have batch norm)
- VGG: No (VGG models have no batch norm)
- DenseNet: Yes (all DenseNet models have batch norm)
- AlexNet: No batch norm
- MobileNet: Yes (batch norm in inverted residual blocks)
- SqueezeNet: No batch norm

**Expected Batch Norm Layer Counts:**
- Shallow models with BN: 10-50 batch norm layers
- Deep models with BN: 50-200+ batch norm layers
- Models without BN: 0 layers (control group)

### Models

#### Baseline Model

**Architecture:** Logistic Regression (Binary Classifier)  
**Type:** Linear discriminative model  
**Source:** scikit-learn

**Configuration:**
- Input: Batch normalization features (dimension determined by feature extraction)
- Output: Binary prediction (0=shallow, 1=deep)
- Regularization: C=1.0 (L2 penalty, inverse regularization strength)
- Solver: lbfgs (quasi-Newton method)
- Max Iterations: 1000
- Random State: 42

**Loading Information** (for Phase 4 download):
- Method: scikit-learn
- Identifier: `LogisticRegression`
- Code: `from sklearn.linear_model import LogisticRegression; clf = LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000, random_state=42)`

**Feature Normalization:** StandardScaler (mean=0, std=1) applied before training

**Rationale:** Same classifier as H-E1, H-M1, H-M2 for controlled comparison. Linear model enables coefficient interpretation.

#### Proposed Model

**Architecture:** Baseline Classifier + Batch Normalization-Specific Features

**Feature Extraction (6 Batch Norm Features):**

**Core Mechanism Implementation:**

```python
# Core Mechanism: Batch Normalization Statistics Extraction
# Purpose: Extract discriminative features from batch norm layers only

import torch
import torch.nn as nn
import numpy as np

def extract_batchnorm_features(model):
    """
    Extract 6 batch normalization-specific features from pretrained CNN.
    
    Args:
        model: PyTorch pretrained model (e.g., resnet50)
    
    Returns:
        features: numpy array of shape (6,)
            [bn_count, gamma_mean, gamma_std, beta_mean, beta_std, bn_depth_weighted]
    """
    # Step 1: Collect all batch norm layers
    bn_layers = [m for m in model.modules() if isinstance(m, nn.BatchNorm2d)]
    
    if len(bn_layers) == 0:
        # No batch norm (VGG, AlexNet) - return zeros
        return np.zeros(6)
    
    # Step 2: Extract gamma (weight) and beta (bias) parameters
    gammas = torch.cat([bn.weight.data.flatten() for bn in bn_layers])
    betas = torch.cat([bn.bias.data.flatten() for bn in bn_layers])
    
    # Step 3: Compute features
    features = np.array([
        len(bn_layers),                    # Feature 1: Batch norm layer count
        gammas.mean().item(),              # Feature 2: Mean gamma (scaling factor)
        gammas.std().item(),               # Feature 3: Std gamma (variability)
        betas.mean().item(),               # Feature 4: Mean beta (shift factor)
        betas.std().item(),                # Feature 5: Std beta (variability)
        sum((i+1) * bn.weight.data.abs().mean().item() 
            for i, bn in enumerate(bn_layers))  # Feature 6: Depth-weighted BN norm
    ])
    
    return features

# Integration: Apply to all 20 models, train classifier on features
```

**Feature Descriptions:**
1. **BN Layer Count:** Direct depth proxy (more layers → more BN)
2. **Gamma Mean:** Average scaling factor across all batch norm layers
3. **Gamma Std:** Variability of scaling factors (distribution shape)
4. **Beta Mean:** Average shift parameter across all batch norm layers
5. **Beta Std:** Variability of shift parameters (distribution shape)
6. **Depth-Weighted BN Norm:** Weighted sum emphasizing later layers (tests accumulation hypothesis)

### Training Protocol

**From Previous Hypothesis (H-M2):** Reusing optimal configuration for controlled comparison

**Classifier Training:**
- **Optimizer:** Not applicable (LogisticRegression uses lbfgs solver internally)
- **Regularization:** C=1.0 (L2 penalty)
- **Solver:** lbfgs (quasi-Newton method)
- **Max Iterations:** 1000
- **Feature Normalization:** StandardScaler (mean=0, std=1)
- **Random State:** 42

**Data Split:**
- Train: 16 models (80%)
- Test: 4 models (20%)
- Stratification: Balanced shallow/deep in both splits
- Seed: 42

**Training Time:** <5 seconds (expected, based on H-E1/H-M1/H-M2)

**Seeds:** 1 (fixed seed 42)

**Rationale:** Identical configuration to H-E1, H-M1, H-M2 ensures controlled experiment. Only feature extraction method changes to isolate batch normalization mechanism contribution.

### Evaluation

**Primary Metrics:**
- **Test Accuracy:** Percentage of correct depth predictions on 4 held-out models
- **Train Accuracy:** Training set performance (overfitting check)
- **Confusion Matrix:** 2×2 matrix (shallow/deep predictions)

**Success Criteria:**
- **Gate Condition:** Test accuracy >50% (SHOULD_WORK threshold)
- **PoC Success:** `test_accuracy > 50%` (batch norm features contribute to classification)

**Secondary Metrics:**
- **Random Initialization Test Accuracy:** Evaluate on randomly initialized models (mechanism validation)
- **Within-Family Accuracy:** Test depth classification within ResNet and DenseNet families separately
- **Feature Importance:** Logistic regression coefficients (which BN features matter most)

**Expected Baseline Performance:**
- H-E1 baseline: 100% test accuracy (global weight statistics)
- H-M1 baseline: 100% test accuracy (gradient flow features)
- H-M2 baseline: 100% test accuracy (architectural features)
- Random classifier: 50% (chance level)

**Mechanism Validation:**
- **Expected:** Batch norm features achieve >50% if normalization contributes
- **Null Hypothesis:** Random initialization test matches pretrained (features are architectural, not normalization-induced)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification
- Library: scikit-learn
- Code: 
  ```python
  from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
  test_accuracy = accuracy_score(y_test, y_pred)
  confusion = confusion_matrix(y_test, y_pred)
  report = classification_report(y_test, y_pred, target_names=['shallow', 'deep'])
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Test accuracy vs 50% threshold (bar chart with pass/fail indicator)

#### Additional Figures (LLM Autonomous)

Based on mechanism hypothesis validation requirements, generate:

1. **Accuracy Comparison** (Multi-hypothesis): H-E1 vs H-M1 vs H-M2 vs H-M3 vs Random baseline
2. **Confusion Matrix**: 2×2 heatmap showing shallow/deep classification results
3. **Feature Importance**: Bar chart of logistic regression coefficients for 6 BN features
4. **Feature Distributions**: Box plots comparing shallow vs deep for each of 6 features
5. **Within-Family Validation**: Accuracy comparison for ResNet-only, DenseNet-only, VGG-only, All-families
6. **Random vs Pretrained**: Side-by-side bar chart comparing mechanism validation results
7. **Train vs Test Accuracy**: Overfitting check visualization

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 Mechanism Success Check

**Mechanism Pass Conditions:**
1. **Gate Condition:** Test accuracy >50% (batch norm features contribute)
2. **Mechanism Validation:** Random initialization test accuracy <50% (training-induced patterns)
3. **Within-Family Check:** At least one family achieves ≥65% accuracy (depth signal beyond architecture type)

**Expected Outcome:**
- **If Random = Pretrained:** Features are architectural (BN layer count), not normalization-induced
- **If Random < Pretrained:** Normalization statistics from training contribute to depth signal

---

## Appendix: Reference Implementations

### Batch Normalization Literature

**Key Papers:**
1. Ioffe & Szegedy (2015). "Batch Normalization: Accelerating Deep Network Training by Reducing Internal Covariate Shift"
   - Original batch normalization paper
   - Defines gamma (scale) and beta (shift) parameters

2. Santurkar et al. (2018). "How Does Batch Normalization Help Optimization?"
   - Shows batch norm smooths loss landscape
   - Not directly about depth fingerprinting

**Implementation References:**
- PyTorch Documentation: `torch.nn.BatchNorm2d`
- Attribute access: `bn_layer.weight` (gamma), `bn_layer.bias` (beta)
- Running statistics: `bn_layer.running_mean`, `bn_layer.running_var`

### Previous Hypothesis Implementations

**H-E1 Code:** `h-e1/code/` - Global weight statistics feature extraction
**H-M1 Code:** `h-m1/code/` - Gradient flow features (layer-wise progression)
**H-M2 Code:** `h-m2/code/` - Architectural features (residual blocks, bottlenecks)

**Reusable Components:**
- Model loader: Load 20 pretrained models from torchvision
- Classifier: LogisticRegression training and evaluation
- Evaluator: Metrics computation, gate checking
- Visualizer: Figure generation (7 figures)
- Random initialization test: Mechanism validation

**H-M3 Novel Component:**
- Batch norm feature extractor: Extract 6 features from BN layers only

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-21T07:04:07.184731+00:00

### Workflow History for This Hypothesis

**Events:**
1. H-M3 set to IN_PROGRESS (2026-04-21T07:04:07)
2. Experiment design started (2026-04-21T07:04:07)
3. Prerequisites validated: H-M2 COMPLETED with PASS status

**Dependency Chain:**
- H-E1 → H-M1 → H-M2 → **H-M3** (current)
- All prerequisites PASSED with 100% test accuracy
- Critical insight: Random initialization tests revealed features are architectural

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
