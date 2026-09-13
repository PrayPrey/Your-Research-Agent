# Product Requirements Document: H-M3 Batch Normalization Mechanism Validation

**Hypothesis:** H-M3  
**Type:** Mechanism  
**Date:** 2026-04-21  
**Author:** Phase 3 Implementation Planning

---

## 1. Executive Summary

### Purpose
Validate that batch normalization layer weight distributions differ between shallow (≤34 layers) and deep (≥50 layers) pretrained CNNs due to cumulative normalization effects. This mechanism hypothesis tests whether batch normalization contributes to the depth classification capability established in H-E1.

### Success Criteria
- **Primary:** Batch normalization features achieve >50% test accuracy (SHOULD_WORK gate)
- **Secondary:** Within-family classification accuracy ≥65% (depth signal independent of architecture family)
- **Tertiary:** Compare pretrained vs random initialization to distinguish normalization-induced vs architectural patterns

### Scope
Build on H-E1, H-M1, and H-M2 infrastructure, introducing 6 batch normalization-specific features that capture BN layer statistics, count, and depth-weighted effects.

---

## 2. Problem Statement

H-E1 demonstrated 100% depth classification accuracy with weight statistics. H-M1 and H-M2 tested gradient and architectural mechanisms, both achieving 100% accuracy with random models, confirming features are architectural rather than training-induced.

**Hypothesis Statement:**  
Under pretrained CNN training with batch normalization, if normalization statistics accumulate across 50+ layers versus <34 layers, then batch norm layer weight distributions will differ, because cumulative normalization effects scale with depth.

**Research Gap:**  
H-M1 and H-M2 revealed that discriminative features are architectural. H-M3 tests whether batch normalization layers provide additional depth signal or if BN layer count is simply another architectural feature.

---

## 3. Stakeholders

- **Research Team:** Complete mechanism investigation (final mechanism hypothesis)
- **Future Work:** Comprehensive mechanism understanding (gradient vs architecture vs normalization)
- **Paper Contribution:** Attribute depth classification to specific causal mechanisms

---

## 4. Data Specification

### 4.1 Primary Dataset

**Dataset:** PyTorch Torchvision Pretrained Models (Consistent with H-E1, H-M1, H-M2)

**Source:** torchvision.models API (programmatic, no manual download)

**Models (20 total):**
- **Shallow (≤34 layers, n=10):** resnet18, resnet34, vgg11, vgg13, vgg16, vgg19, alexnet, squeezenet1_0, mobilenet_v2, densenet121
- **Deep (≥50 layers, n=10):** resnet50, resnet101, resnet152, densenet161, densenet169, densenet201, wide_resnet50_2, wide_resnet101_2, resnext50_32x4d, resnext101_32x8d

**Batch Normalization Coverage:**
- **ResNet:** Yes (all ResNet models have batch norm after each conv layer)
- **VGG:** No (VGG models have NO batch norm - control group)
- **DenseNet:** Yes (batch norm in each dense layer)
- **AlexNet:** No batch norm
- **MobileNet:** Yes (batch norm in inverted residual blocks)
- **SqueezeNet:** No batch norm

**Expected BN Layer Counts:**
- Shallow models with BN: 10-50 batch norm layers (ResNet18: ~20, DenseNet121: ~120)
- Deep models with BN: 50-200+ batch norm layers (ResNet152: ~150, DenseNet201: ~200)
- Models without BN: 0 layers (VGG, AlexNet, SqueezeNet serve as control group)

**Split:** 80/20 stratified (16 train, 4 test, seed=42)

**Access Method:**
```python
import torchvision.models as models
model = models.resnet50(pretrained=True)
```

**Data Preparation Tasks:**
- ✅ No manual download required (auto-download via PyTorch)
- ✅ Model loading: Reuse H-E1, H-M1, H-M2 infrastructure

### 4.2 Baseline Comparison Data

**H-E1 Results (Global Statistics):**
- Test Accuracy: 100% (4/4 correct)
- Features: 4 global statistics (mean, std, min, max of Frobenius norms)

**H-M1 Results (Gradient Flow Features):**
- Test Accuracy: 100% (4/4 correct)
- Random Test Accuracy: 100% (4/4 correct) → Mechanism REJECTED (architectural, not gradient-induced)

**H-M2 Results (Architectural Constraints):**
- Test Accuracy: 100% (4/4 correct)
- Random Test Accuracy: 100% (4/4 correct) → Mechanism is ARCHITECTURAL
- Within-Family: ResNet 100%, DenseNet 100%
- Key Finding: Features are purely architectural (skip connections, bottlenecks)

**Random Baseline:** 50% (binary classification guess)

**Within-Family Benchmark:** 60-75% accuracy (from previous hypotheses)

### 4.3 Data Processing

**Feature Extraction (NEW for H-M3):**
Extract 6 batch normalization-specific features per model:

1. **BN Layer Count:** Total number of BatchNorm2d layers (direct depth proxy)
2. **Gamma Mean:** Mean of BN weight (scale) parameters across all layers
3. **Gamma Std:** Standard deviation of BN weight parameters (distribution shape)
4. **Beta Mean:** Mean of BN bias (shift) parameters across all layers
5. **Beta Std:** Standard deviation of BN bias parameters (distribution shape)
6. **Depth-Weighted BN Norm:** Weighted sum emphasizing later layers (tests accumulation hypothesis)

**Normalization:** StandardScaler (mean=0, std=1) - consistent with H-E1, H-M1, H-M2

---

## 5. Functional Requirements

### FR-1: Batch Normalization Feature Extractor
**Priority:** P0 (Critical Path)  
**Description:** Implement `BatchNormFeatureExtractor` class to extract 6 BN-specific features from pretrained models.

**Acceptance Criteria:**
- Detect BatchNorm2d layers via `isinstance(module, nn.BatchNorm2d)`
- Extract gamma (weight) and beta (bias) parameters from all BN layers
- Compute mean and std of gamma and beta across all layers
- Calculate depth-weighted norm: `sum((i+1) * bn.weight.abs().mean() for i, bn in enumerate(bn_layers))`
- Handle models without BN (VGG, AlexNet, SqueezeNet) → return zeros
- Output: numpy array of shape (6,) per model
- Processing time: <10 seconds for 20 models

**Implementation Reference:**
- PyTorch BN layer access: `model.modules()`, filter by `nn.BatchNorm2d`
- Parameter access: `bn_layer.weight.data`, `bn_layer.bias.data`

### FR-2: Model Loader (Reuse H-E1/H-M1/H-M2)
**Priority:** P0 (Critical Path)  
**Description:** Load 20 pretrained models from torchvision.models with automatic download.

**Acceptance Criteria:**
- Load all 20 models successfully
- Handle auto-download for first run
- Return model objects with accessible parameters and modules
- **Reuse H-E1/H-M1/H-M2 implementation** (proven stable)

### FR-3: Binary Classifier (Reuse H-E1/H-M1/H-M2)
**Priority:** P0 (Critical Path)  
**Description:** Train LogisticRegression classifier on batch normalization features.

**Acceptance Criteria:**
- Classifier: LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000, random_state=42)
- Feature scaling: StandardScaler
- Train on 16 models, test on 4 models
- **Reuse H-E1/H-M1/H-M2 classifier configuration** (optimal hyperparameters)

### FR-4: Within-Family Validation
**Priority:** P1 (Mechanism Validation)  
**Description:** Train separate classifiers for ResNet-only and DenseNet-only subsets (exclude VGG/other families without BN).

**Acceptance Criteria:**
- Filter models by architecture family AND batch norm presence
- Train 2 classifiers: ResNet-only (has BN), DenseNet-only (has BN)
- Require ≥4 models per family for valid split
- Target: ≥65% within-family accuracy (depth signal independent of family)
- Report accuracy per family
- VGG excluded from within-family test (no BN layers)

**Rationale:** Isolates depth signal from architecture type, focusing on BN-enabled families

### FR-5: Random Initialization Test
**Priority:** P1 (Gate Validation)  
**Description:** Extract BN features from randomly initialized (untrained) models to verify normalization-induced vs architectural patterns.

**Acceptance Criteria:**
- Initialize same 20 model architectures with random weights (pretrained=False)
- Extract BN features (same 6 features)
- Train classifier on random models
- Expected behavior:
  - If random accuracy ≈ pretrained accuracy → Features are purely architectural (BN layer count)
  - If random accuracy << pretrained accuracy → Normalization statistics matter
- Report random test accuracy

**Rationale:** Following H-M1/H-M2 protocol to distinguish architectural vs training effects

### FR-6: Evaluation Pipeline
**Priority:** P0 (Critical Path)  
**Description:** Compute test accuracy, within-family accuracy, and compare against baselines.

**Acceptance Criteria:**
- Calculate test accuracy on 4 held-out models (SHOULD_WORK gate: >50%)
- Generate confusion matrix
- Compare H-M3 vs H-E1 (100%) vs H-M1 (100%) vs H-M2 (100%) vs Random (50%)
- Report feature importance (logistic regression coefficients)
- Identify which BN features contribute most (likely BN layer count)

### FR-7: Visualization Generation
**Priority:** P2 (Analysis)  
**Description:** Generate figures for mechanism validation and comparison with H-E1, H-M1, H-M2.

**Acceptance Criteria:**
- **Mandatory:** Gate metrics comparison bar chart (Test accuracy vs 50% threshold)
- **Accuracy Comparison:** H-E1 vs H-M1 vs H-M2 vs H-M3 vs Random baseline (5-way comparison)
- **Feature Importance:** Bar chart of logistic regression coefficients for 6 BN features
- **Within-Family Accuracy:** Bar chart comparing ResNet, DenseNet, VGG (no BN), All-families
- **Feature Distributions:** Box plots of 6 features split by shallow vs deep
- **Random vs Pretrained Comparison:** Side-by-side bar chart (mechanism validation)
- **Confusion Matrix:** 2×2 heatmap with counts
- Save all figures to `h-m3/figures/`

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- Total experiment runtime: <90 seconds (feature extraction + training + evaluation + within-family tests)
- Feature extraction: <10 seconds for 20 models
- Training time: <1 second per classifier (linear model, 16 samples)
- Within-family training: <2 seconds total (2 classifiers)

### NFR-2: Reproducibility
- Fixed random seed: 42 (consistent with H-E1, H-M1, H-M2)
- Deterministic train-test split (stratified, same seed)
- Same model versions as H-E1, H-M1, H-M2 (torchvision pretrained weights)

### NFR-3: Code Reusability
- Reuse H-E1/H-M1/H-M2 model loader (minimal changes)
- Reuse H-E1/H-M1/H-M2 classifier configuration
- Modular feature extractor for easy comparison with previous hypotheses

### NFR-4: Logging
- Print-based logging (FULL tier: standard infrastructure)
- Save metrics to JSON: `h-m3/code/outputs/metrics.json`
- Log feature extraction progress per model
- Log BN layer counts per model (important for understanding results)

---

## 7. Dependencies

### 7.1 Python Packages

**Core Dependencies:**
- `torch>=2.0.0` (PyTorch)
- `torchvision>=0.15.0` (pretrained models)
- `scikit-learn>=1.3.0` (LogisticRegression, StandardScaler, metrics)
- `numpy>=1.24.0` (numerical operations)
- `matplotlib>=3.7.0` (visualizations)

**Installation:**
```bash
pip install torch torchvision scikit-learn numpy matplotlib
```

### 7.2 Hardware Requirements
- CPU-only execution (no GPU required for inference on pretrained models)
- RAM: 4GB minimum (model loading + feature extraction)
- Storage: 2GB for torchvision model cache

### 7.3 Prerequisite Hypotheses
- **H-E1:** Provides proven model loading infrastructure and optimal classifier configuration
- **H-M1:** Provides random initialization test protocol
- **H-M2:** Provides within-family validation framework and mechanism validation pattern

### 7.4 External Resources
- PyTorch torchvision pretrained models (auto-download from PyTorch Hub)
- No manual dataset downloads required
- No external baseline repositories required

---

## 8. Success Metrics

### 8.1 Gate Condition (SHOULD_WORK)
- **Primary Metric:** Test Accuracy > 50%
- **Consequence if Fails:** Document as limitation, gradient/architecture dominate (BN contribution minimal)
- **Pass Criteria:** At least 3/4 test models classified correctly

### 8.2 Mechanism Validation Metrics
- **Within-Family Accuracy:** ≥65% for ResNet or DenseNet families
  - Validates depth signal exists independent of architecture type (for BN-enabled models)
- **Random vs Pretrained Comparison:**
  - Expected: Random accuracy ≈ Pretrained accuracy (features are architectural - BN layer count)
  - Alternative: Random << Pretrained (normalization statistics from training matter)

### 8.3 Comparative Metrics
- Compare H-M3 accuracy against:
  - H-E1: 100% (global statistics baseline)
  - H-M1: 100% (gradient flow features, mechanism rejected)
  - H-M2: 100% (architectural constraints, mechanism confirmed)
  - Random: 50% (theoretical baseline)

### 8.4 Feature Analysis Metrics
- Feature importance ranking (which of 6 BN features contribute most)
- Expected: BN layer count dominates (architectural signal)
- Alternative: Gamma/beta statistics matter (normalization effects)
- VGG vs ResNet/DenseNet: Does BN presence predict depth?

---

## 9. Constraints and Assumptions

### 9.1 Constraints
- **Model Availability:** Limited to torchvision pretrained models (20 models)
- **Sample Size:** 20 models total, 4 test samples (small test set)
- **BN Coverage:** Only ~13 models have batch norm (ResNet, DenseNet, MobileNet)
- **Architecture Coverage:** VGG, AlexNet, SqueezeNet lack BN (serve as control group)

### 9.2 Assumptions
- Torchvision pretrained models are trained with standard ImageNet protocol
- Batch normalization layers are identifiable via `nn.BatchNorm2d` type
- BN parameters (gamma, beta) are accessible via `.weight` and `.bias` attributes
- Models without BN can be handled gracefully (zero features)

### 9.3 Risks
- **Risk 1:** VGG models are deep but have NO batch norm
  - Mitigation: VGG serves as control group; BN presence feature should differentiate
  - Impact: BN layer count becomes primary discriminative feature
- **Risk 2:** Within-family validation limited to ResNet and DenseNet (VGG excluded)
  - Mitigation: Focus on BN-enabled families only
- **Risk 3:** Random initialization test likely shows same result as H-M1/H-M2 (100% accuracy)
  - Impact: Confirms features are purely architectural (BN layer count, not normalization statistics)
  - Expected: BN layer count is architectural, gamma/beta distributions may require training

---

## 10. Out of Scope

### Explicitly Excluded
- Training new models from scratch
- Fine-tuning pretrained models
- Testing on non-ImageNet pretrained models
- Running statistics analysis (`running_mean`, `running_var`) - focus on learnable parameters only
- Gradient flow analysis (covered by H-M1)
- Architectural constraints beyond BN (covered by H-M2)

### Future Work (Post-H-M3)
- Extended architecture families (Inception, EfficientNet with BN variants)
- Quantitative mechanism attribution (gradient vs architecture vs normalization contributions)
- Cross-hypothesis mechanism comparison (which mechanism contributes most?)

---

## 11. Acceptance Criteria Summary

**Phase 4 Implementation Complete When:**
1. ✅ 6 batch normalization features extracted from all 20 models
2. ✅ Classifier trained on 16 models, tested on 4 models
3. ✅ Test accuracy > 50% (SHOULD_WORK gate satisfied)
4. ✅ Within-family validation completed for ResNet and DenseNet
5. ✅ Random initialization test completed
6. ✅ All 7 figures generated and saved
7. ✅ Metrics saved to `metrics.json`
8. ✅ Validation report (`04_validation.md`) documents gate status and mechanism findings

---

## 12. Implementation Notes

### 12.1 Key Differences from H-M2
- **Feature Design:** Batch normalization statistics (6 features) vs architectural constraints (8 features)
- **Mechanism Focus:** Normalization layer effects vs skip connections and bottlenecks
- **Expected Outcome:** Likely 100% accuracy driven by BN layer count (architectural signal)

### 12.2 Critical Implementation Details
- **BN Layer Detection:** Use `isinstance(module, nn.BatchNorm2d)` from PyTorch
- **Parameter Extraction:** Access via `bn.weight.data` (gamma) and `bn.bias.data` (beta)
- **Zero-BN Handling:** Models without BN (VGG, AlexNet, SqueezeNet) → return `np.zeros(6)`
- **Depth-Weighted Norm:** `sum((i+1) * bn.weight.abs().mean() for i, bn in enumerate(bn_layers))`

### 12.3 Validation Protocol
- Follow H-M1/H-M2 validation framework (gate check + mechanism validation + random test)
- If gate fails (<50%): Document that BN contribution is minimal (architectural features dominate)
- If random test also passes: Confirms BN layer count is architectural (not normalization statistics)
- Within-family results: Key mechanism insight (depth signal within BN-enabled architectures)

### 12.4 Expected Insights
- **If Random ≈ Pretrained:** BN layer count (architectural) is the discriminative feature
- **If Random << Pretrained:** Gamma/beta statistics from training contribute to depth signal
- **Feature Importance:** Likely dominated by BN layer count (feature #1)
- **Mechanism Conclusion:** BN provides depth signal through layer count (architectural), not normalization effects

---

*This PRD defines requirements for H-M3 implementation (Phase 4 Coding). All functional requirements must be satisfied before proceeding to Phase 4 validation.*
