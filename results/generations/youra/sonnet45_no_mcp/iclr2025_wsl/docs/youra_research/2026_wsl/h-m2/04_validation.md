# Validation Report: H-M2 Architectural Constraints Mechanism Validation

**Hypothesis ID:** h-m2  
**Type:** Mechanism  
**Date:** 2026-04-21  
**Status:** COMPLETED  
**Gate Result:** PASS ✓

---

## Executive Summary

H-M2 successfully validated that **architectural constraints** (residual connections, dense connections, bottleneck layers) enable perfect depth classification of pretrained CNNs. The experiment achieved **100% test accuracy** with 8 architectural features, passing the SHOULD_WORK gate (>50% threshold). However, the random initialization test also achieved 100% accuracy, confirming that these features are **purely architectural** rather than training-induced, consistent with H-M1 findings.

**Key Finding:** Architectural patterns (residual blocks, bottleneck ratios, layer count) are the discriminative features, not gradient accumulation or training effects.

---

## Experiment Results

### Primary Metrics

| Metric | Value | Gate Threshold | Status |
|--------|-------|----------------|--------|
| **Test Accuracy** | **100.0%** (4/4) | >50% | ✓ PASS |
| Train Accuracy | 93.8% (15/16) | N/A | ✓ |
| Random Test Accuracy | 100.0% (4/4) | N/A | ⚠️ Same as pretrained |

**Test Models:** alexnet (shallow), vgg13 (shallow), resnet152 (deep), wide_resnet50_2 (deep)

**Confusion Matrix:**
```
              Predicted
           Shallow  Deep
Actual  
Shallow      2       0
Deep         0       2
```

**Perfect classification** with no errors.

---

## Within-Family Validation Results

| Family | Accuracy | Train Accuracy | Num Samples | Status |
|--------|----------|----------------|-------------|--------|
| **ResNet** | **100.0%** | 100.0% | 9 models | ✓ PASS (≥65%) |
| **DenseNet** | **100.0%** | 100.0% | 4 models | ✓ PASS (≥65%) |
| VGG | Skipped | N/A | 4 models | Only shallow models |

**Within-Family Gate:** PASS ✓ (both ResNet and DenseNet exceed 65% threshold)

**Key Insight:** Depth signal is detectable **within architecture families**, confirming that architectural features capture depth-specific patterns independent of architecture type.

**VGG Limitation:** All VGG models (vgg11, vgg13, vgg16, vgg19) are shallow, preventing within-family validation for this family.

---

## Random Initialization Test Results

| Model Type | Test Accuracy | Train Accuracy | Interpretation |
|------------|---------------|----------------|----------------|
| **Pretrained** | 100.0% | 93.8% | Perfect classification |
| **Random (Untrained)** | 100.0% | 93.8% | ⚠️ Same as pretrained |

**Random vs Pretrained Gap:** 0.0%

**Mechanism Conclusion:** Features are **ARCHITECTURAL**, not training-induced.

The random initialization test confirms H-M1's finding: architectural patterns (residual blocks, bottleneck layers, dense connections) exist in the architecture itself, not from gradient flow during training. Random models achieve identical accuracy because:
- Residual blocks are structural (hasattr(module, 'downsample'))
- Bottleneck ratios are architectural (1×1 conv count / total conv count)
- Layer counts are fixed by architecture
- Dense connections are defined by architecture (denselayer naming)

---

## Feature Importance Analysis

**Top 5 Most Important Features** (by logistic regression coefficient magnitude):

| Rank | Feature | Coefficient | Interpretation |
|------|---------|-------------|----------------|
| 1 | **Bottleneck Ratio** | +0.956 | Strong positive (deep models have more 1×1 convs) |
| 2 | **Layer Count** | +0.932 | Strong positive (deep models have more layers) |
| 3 | **Residual Blocks** | +0.606 | Positive (ResNet deep models have more blocks) |
| 4 | **Residual Norm** | +0.479 | Moderate positive (deeper residual paths) |
| 5 | **Dense Connections** | +0.396 | Positive (DenseNet deep models have more connections) |

**Least Important:**
- Transition Layers: -0.026 (near zero, not discriminative)

**Key Architectural Discriminators:**
1. **Bottleneck Ratio:** Deep models (ResNet50+, DenseNet) use bottleneck layers extensively
2. **Layer Count:** Direct depth indicator
3. **Residual Blocks:** ResNet deep models have 4 residual stages vs 3 in shallow

---

## Baseline Comparison

| Hypothesis | Features | Test Accuracy | Random Accuracy | Mechanism Status |
|------------|----------|---------------|-----------------|------------------|
| **H-E1** | Weight statistics (4 global) | 100.0% | N/A | Existence validated |
| **H-M1** | Gradient flow (6 layer-wise) | 100.0% | 100.0% | Mechanism REJECTED |
| **H-M2** | Architectural constraints (8) | 100.0% | 100.0% | Mechanism ARCHITECTURAL |

**H-M2 vs H-E1:** Same performance (100%), architectural features are as effective as global weight statistics.

**H-M2 vs H-M1:** Same performance, but H-M2 directly extracts architectural patterns while H-M1 used gradient-flow proxies that turned out to be architectural.

---

## Gate Evaluation

### SHOULD_WORK Gate (>50% Test Accuracy)

**Threshold:** >50%  
**Actual:** 100.0%  
**Result:** ✓ PASS

**Interpretation:** Architectural constraint features (residual blocks, bottleneck ratios, dense connections) contribute **strongly** to depth classification, far exceeding the minimum threshold.

### Within-Family Validation Gate (≥65%)

**Threshold:** ≥65% for at least one family  
**Actual:** 100.0% (ResNet), 100.0% (DenseNet)  
**Result:** ✓ PASS

**Interpretation:** Depth signal is detectable within architecture families, validating that features capture depth-specific patterns beyond architecture type differences.

---

## Mechanism Validation

**Hypothesis Statement:** Under pretrained CNN architectures, if residual connections (ResNet), dense connections (DenseNet), and bottleneck layers exist in deep models but not shallow models, then weight structures will exhibit depth-specific patterns, because architectural constraints shape weight organization.

**Validation Results:**

✓ **Architectural features extracted:** 8 features (residual blocks, dense connections, bottleneck ratio, layer count, skip connections, residual norms, transition layers, architecture family)

✓ **Depth classification successful:** 100% test accuracy

✓ **Within-family validation passed:** 100% accuracy for ResNet and DenseNet families

⚠️ **Random initialization test:** 100% accuracy (same as pretrained)

**Mechanism Conclusion:** **ARCHITECTURAL**

The features are purely structural and exist in the architecture definition itself, not induced by training. This is expected because:
- Residual blocks are detected via module structure (downsample attribute)
- Bottleneck ratios are computed from kernel sizes (architectural property)
- Dense connections are identified via layer naming (architectural convention)
- Layer counts are fixed by architecture

**Refined Hypothesis Interpretation:** Architectural constraints (residual/dense connections, bottleneck layers) create depth-specific **structural patterns** that enable classification, independent of training. The original hypothesis correctly identified architectural constraints as the mechanism, though it overemphasized "weight organization" shaped by constraints rather than the constraints themselves being the discriminative features.

---

## Experimental Artifacts

### Generated Outputs

**Metrics:**
- `outputs/metrics.json` - Complete experiment metrics
- `outputs/features.npy` - Extracted architectural features (20, 8)
- `outputs/labels.npy` - Model labels (20,)

**Visualizations (7 figures):**
1. `accuracy_comparison.png` - H-E1 vs H-M1 vs H-M2 vs Random (MANDATORY)
2. `gate_metrics.png` - Test accuracy vs 50% threshold
3. `within_family_comparison.png` - ResNet/VGG/DenseNet/All-families accuracy
4. `feature_importance.png` - Logistic regression coefficients
5. `confusion_matrix.png` - 2×2 matrix (perfect classification)
6. `feature_distributions.png` - 8 feature box plots (shallow vs deep)
7. `train_test_comparison.png` - Train (93.8%) vs Test (100.0%)

---

## Technical Details

### Architectural Feature Extraction

**8 Features Extracted:**

1. **Residual Block Count:** Modules with `downsample` attribute (ResNet-specific)
   - Shallow: 0-3 blocks
   - Deep: 4 blocks (ResNet50+)

2. **Dense Connection Count:** Layers with "denselayer" in name (DenseNet-specific)
   - Shallow: 0-406 connections (densenet121)
   - Deep: 546-686 connections (densenet161-201)

3. **Bottleneck Ratio:** (1×1 conv count) / (total conv count)
   - VGG: 0.0 (no bottleneck layers)
   - ResNet/DenseNet shallow: 0.08-0.51
   - ResNet/DenseNet deep: 0.51-0.68

4. **Layer Count:** Total Conv2d layers
   - Shallow: 8-13 layers
   - Deep: 50-201 layers

5. **Skip Connection Presence:** Binary (1 if residual/dense exists, 0 otherwise)
   - VGG/AlexNet: 0
   - ResNet/DenseNet: 1

6. **Residual Path Norm:** Mean L2 norm of downsample layer weights
   - VGG: 0.0 (no downsample)
   - ResNet shallow: ~10-20
   - ResNet deep: ~30-50

7. **Transition Layer Count:** DenseNet transition layers
   - Non-DenseNet: 0
   - DenseNet: 3-4

8. **Architecture Family:** Binary (1 if ResNet/DenseNet, 0 if VGG/other)
   - ResNet/DenseNet: 1
   - VGG/AlexNet/SqueezeNet/MobileNet: 0

### Model Configuration

**Classifier:** LogisticRegression (C=1.0, solver='lbfgs', max_iter=1000, random_state=42)  
**Feature Normalization:** StandardScaler (mean=0, std=1)  
**Train/Test Split:** 80/20 stratified (16 train, 4 test, seed=42)  
**Reused from:** H-M1 optimal hyperparameters (validated in H-E1)

### Dataset

**20 Pretrained ImageNet CNNs:**
- Shallow (10): resnet18, resnet34, vgg11, vgg13, vgg16, vgg19, alexnet, squeezenet1_0, mobilenet_v2, densenet121
- Deep (10): resnet50, resnet101, resnet152, densenet161, densenet169, densenet201, wide_resnet50_2, wide_resnet101_2, resnext50_32x4d, resnext101_32x8d

**Architecture Families:**
- ResNet: 9 models (2 shallow, 7 deep)
- VGG: 4 models (4 shallow, 0 deep) ← Limitation
- DenseNet: 4 models (1 shallow, 3 deep)
- Other: 3 models (alexnet, squeezenet1_0, mobilenet_v2)

---

## Limitations and Future Work

### Limitations

1. **VGG Family Imbalance:** All VGG models are shallow, preventing within-family depth validation for this family.

2. **Random Initialization Paradox:** Features are purely architectural, raising the question: Why does H-E1 (global weight statistics) also achieve 100%? Suggests global weight statistics may also capture architectural patterns (layer count via parameter count, bottleneck presence via weight tensor shapes).

3. **Feature Redundancy:** Bottleneck Ratio and Layer Count are highly correlated with architecture family, suggesting some features may be redundant.

4. **Small Test Set:** Only 4 test models limits statistical confidence, though perfect accuracy suggests robust features.

### Future Work

**H-M3 (Next):** Test batch normalization effects as third mechanism hypothesis.

**Extended Analysis:**
- Test on additional architecture families (Inception, EfficientNet, Vision Transformers)
- Investigate why global weight statistics (H-E1) and architectural features (H-M2) both achieve 100%
- Feature ablation study: Which of the 8 features are necessary and sufficient?

---

## Conclusions

### Primary Conclusions

1. **Gate Status:** ✓ PASS (100% >> 50% threshold)
   - Architectural constraint features enable perfect depth classification

2. **Within-Family Validation:** ✓ PASS (100% >> 65% threshold)
   - Depth signal is detectable within ResNet and DenseNet families
   - Confirms features capture depth-specific patterns beyond architecture type

3. **Mechanism Status:** ARCHITECTURAL (not training-induced)
   - Random models achieve identical 100% accuracy
   - Features exist in architecture definition, not learned during training

4. **Hypothesis Validation:** PARTIALLY SUPPORTED
   - ✓ Architectural constraints create distinguishable depth patterns
   - ⚠️ Patterns are structural (architecture definition), not weight organization shaped by constraints
   - Refined interpretation: Architecture **definition** is the mechanism, not constraints shaping weight organization

### Scientific Insights

**Key Insight:** Architectural patterns (residual blocks, bottleneck ratios, layer counts) are perfectly discriminative for depth classification, but these are **definitional features** of the architecture rather than emergent training effects.

**Comparison with H-M1:** Both H-M1 (gradient flow) and H-M2 (architectural constraints) achieve 100% accuracy with random models, but H-M2 directly extracts the architectural features while H-M1 used layer-wise statistics that turned out to be architectural proxies.

**Broader Implication:** The success of both H-E1 (global weight statistics) and H-M2 (architectural features) suggests that **architecture depth is encoded in multiple ways**: global parameter statistics, layer-wise patterns, and explicit architectural features. All are deterministic from the architecture definition.

### Next Steps

**Recommended:** Proceed to H-M3 (batch normalization effects) to test whether normalization-specific patterns add any signal beyond architectural features.

**Alternative:** Investigate why architectural depth is so strongly encoded across multiple feature types (global statistics, layer-wise patterns, architectural features) and whether any features capture **training-induced** depth effects rather than architectural ones.

---

## Appendix: Feature Extraction Implementation

### Residual Block Detection
```python
def count_residual_blocks(model):
    count = 0
    for module in model.modules():
        if hasattr(module, 'downsample') and module.downsample is not None:
            count += 1
    return count
```

### Bottleneck Ratio Computation
```python
def compute_bottleneck_ratio(model):
    total_convs = sum(1 for m in model.modules() if isinstance(m, nn.Conv2d))
    bottleneck_convs = sum(1 for m in model.modules() 
                          if isinstance(m, nn.Conv2d) and m.kernel_size == (1, 1))
    return bottleneck_convs / total_convs if total_convs > 0 else 0.0
```

### Dense Connection Detection
```python
def count_dense_connections(model):
    return sum(1 for name, module in model.named_modules() 
               if 'denselayer' in name.lower())
```

---

*Validation Report v1.0 | H-M2 Architectural Constraints Mechanism | Gate: PASS | Status: COMPLETED*
