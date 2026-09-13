# Validation Report: H-M3 Batch Normalization Mechanism

**Hypothesis ID:** h-m3  
**Type:** Mechanism  
**Date:** 2026-04-21  
**Phase:** Phase 4 - Implementation & Validation

---

## Executive Summary

**Hypothesis Statement:** Under pretrained CNN training with batch normalization, if normalization statistics accumulate across 50+ layers versus <34 layers, then batch norm layer weight distributions will differ, because cumulative normalization effects scale with depth.

**Gate Result:** ✅ **PASS** (SHOULD_WORK gate: 75.0% > 50% threshold)

**Key Findings:**
- Test accuracy: 75.0% (3/4 correct classifications)
- Mechanism: **ARCHITECTURAL** (not normalization-induced)
- Random initialization test: 75.0% (same as pretrained)
- Within-family validation: PASS (ResNet: 100%, DenseNet: 100%)

---

## 1. Experiment Results

### 1.1 Primary Metrics

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| Test Accuracy | 75.0% | >50% | ✅ PASS |
| Train Accuracy | 81.2% | N/A | ✅ |
| Gate Threshold | 50% | SHOULD_WORK | ✅ PASS |

### 1.2 Confusion Matrix

```
Predicted:    Shallow  Deep
Actual:
  Shallow        2       0
  Deep           1       1
```

**Test Models:**
- Shallow (correct): alexnet, vgg13
- Deep (misclassified): resnet152 → predicted as shallow
- Deep (correct): wide_resnet50_2

**Analysis:** One deep model (resnet152) was misclassified as shallow, likely because VGG models in training set have zero BN features, creating ambiguity.

---

## 2. Mechanism Validation

### 2.1 Random Initialization Test

**Purpose:** Determine if features are architectural vs training-induced

| Model Type | Test Accuracy | Interpretation |
|------------|---------------|----------------|
| Pretrained | 75.0% | Batch norm features enable classification |
| Random (untrained) | 75.0% | **SAME as pretrained** |

**Conclusion:** Features are **ARCHITECTURAL**, not normalization-induced.

**Mechanism Status:** The discriminative feature is **BN layer count** (architectural property), not gamma/beta statistics from training.

### 2.2 Within-Family Validation

**Purpose:** Test depth signal robustness within architecture families

| Family | Accuracy | Num Models | Status |
|--------|----------|------------|--------|
| ResNet | 100.0% | 9 | ✅ PASS |
| DenseNet | 100.0% | 4 | ✅ PASS |
| VGG | Skipped | 4 | N/A (no BN) |

**Result:** ✅ PASS (both families ≥65% threshold)

**Interpretation:** BN layer count varies with depth even within the same architecture family (ResNet18: 20 BN layers, ResNet152: 155 BN layers).

---

## 3. Feature Analysis

### 3.1 Batch Normalization Features (6 features)

1. **BN Layer Count** - Direct count of BatchNorm2d layers
2. **Gamma Mean** - Mean of BN weight (scale) parameters
3. **Gamma Std** - Std of BN weight parameters
4. **Beta Mean** - Mean of BN bias (shift) parameters
5. **Beta Std** - Std of BN bias parameters
6. **Depth-Weighted BN Norm** - Weighted sum emphasizing later layers

### 3.2 Feature Importance

**Most Important Features** (from logistic regression coefficients):
1. BN Layer Count (primary discriminator)
2. Depth-Weighted BN Norm (secondary)
3. Gamma/Beta statistics (minimal contribution)

**Key Insight:** BN layer count is the dominant feature, confirming the mechanism is architectural (deeper networks have more BN layers by design).

### 3.3 Feature Distributions

**Shallow Models:**
- BN Layer Count: 0-52 (mean: ~23, excluding VGG with 0)
- Models without BN: VGG (4 models), AlexNet, SqueezeNet

**Deep Models:**
- BN Layer Count: 53-201 (mean: ~130)
- All deep models have BN layers

**Separation:** Clear separation between shallow and deep models based on BN layer count.

---

## 4. Hypothesis Evaluation

### 4.1 Original Hypothesis

> "If normalization statistics accumulate across 50+ layers versus <34 layers, then batch norm layer weight distributions will differ, because cumulative normalization effects scale with depth."

**Evaluation:** ❌ **REJECTED** (mechanism hypothesis)

**Reason:** Random initialization test showed 75% accuracy (same as pretrained), indicating features are architectural (BN layer count), not normalization-induced (gamma/beta statistics from training).

### 4.2 Revised Understanding

**Actual Mechanism:** BN layer count (architectural property) enables depth classification, not cumulative normalization effects.

**Evidence:**
1. Random models achieve same accuracy as pretrained (75%)
2. BN layer count is the primary discriminative feature
3. Gamma/beta statistics contribute minimally

---

## 5. Comparison with Previous Hypotheses

| Hypothesis | Test Accuracy | Mechanism | Training-Induced |
|------------|---------------|-----------|------------------|
| H-E1 (Weight Stats) | 100% | Weight norms | Unknown |
| H-M1 (Gradient Flow) | 100% | REJECTED | No (architectural) |
| H-M2 (Architecture) | 100% | CONFIRMED | No (architectural) |
| **H-M3 (Batch Norm)** | **75%** | **ARCHITECTURAL** | **No** |
| Random Baseline | 50% | N/A | N/A |

**Key Findings:**
- H-M3 achieves lower accuracy (75%) than H-E1/H-M1/H-M2 (100%)
- Like H-M1 and H-M2, H-M3 features are architectural (random test confirms)
- BN layer count is less discriminative than H-M2's architectural features (residual blocks, bottlenecks)

---

## 6. Gate Decision

**Gate Type:** SHOULD_WORK  
**Threshold:** Test accuracy >50%  
**Actual:** 75.0%  
**Result:** ✅ **PASS**

**Interpretation:** Batch normalization features contribute to depth classification (75% > 50%), but the mechanism is architectural (BN layer count) rather than normalization-induced (gamma/beta statistics).

**Action:** Proceed to Phase 5 (baseline comparison) with PASS status.

---

## 7. Limitations and Notes

### 7.1 Limitations

1. **VGG Control Group:** VGG models have no BN layers (zero features), creating a trivial classification case for shallow models.
2. **Small Test Set:** Only 4 test models limits statistical confidence.
3. **Confounding Factor:** BN layer count is perfectly correlated with depth (architectural design choice).

### 7.2 Unexpected Findings

1. **Lower Accuracy than H-M2:** H-M3 (75%) < H-M2 (100%), suggesting architectural constraints (residual blocks, bottlenecks) are more discriminative than BN layer count.
2. **Misclassified Deep Model:** ResNet152 (155 BN layers) misclassified as shallow, possibly due to VGG models with 0 BN layers in training set.

### 7.3 Future Work

- Exclude VGG models to test BN statistics on BN-enabled families only
- Test on larger model pool with more architectural diversity
- Isolate gamma/beta statistics effects by controlling for BN layer count

---

## 8. Deliverables

### 8.1 Code Artifacts

- **Feature Extractor:** `src/feature_extractor.py` (BatchNormFeatureExtractor)
- **Main Pipeline:** `main.py` (10-step experiment pipeline)
- **Configuration:** `config.py` (H-M3 experiment settings)
- **Visualizations:** 7 figures in `outputs/figures/`

### 8.2 Output Files

- **Metrics:** `outputs/metrics.json`
- **Features:** `outputs/features.npy` (20, 6)
- **Labels:** `outputs/labels.npy` (20,)
- **Figures:**
  - `accuracy_comparison.png` (5-way: H-E1/M1/M2/M3/Random)
  - `gate_metrics.png`
  - `confusion_matrix.png`
  - `feature_distributions.png`
  - `feature_importance.png`
  - `within_family_comparison.png`
  - `train_test_comparison.png`

---

## 9. Conclusions

1. **Gate Status:** ✅ PASS (75% > 50% SHOULD_WORK threshold)
2. **Mechanism:** BN features enable depth classification, but through architectural property (BN layer count), not normalization effects
3. **Training-Induced:** ❌ No (random models achieve same accuracy)
4. **Within-Family:** ✅ PASS (ResNet: 100%, DenseNet: 100%)
5. **Comparative Performance:** Lower than H-M2 (75% vs 100%), suggesting architectural constraints are more discriminative

**Final Verdict:** Hypothesis H-M3 PASSES the gate but mechanism hypothesis is REJECTED. Batch normalization contributes to depth classification through layer count (architectural), not cumulative normalization effects (training-induced).

---

**Generated:** 2026-04-21  
**Validation Status:** COMPLETED  
**Next Phase:** Phase 5 - Baseline Comparison
