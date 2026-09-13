# Product Requirements Document: H-M2 Architectural Constraints Mechanism Validation

**Hypothesis:** H-M2  
**Type:** Mechanism  
**Date:** 2026-04-21  
**Author:** Phase 3 Implementation Planning

---

## 1. Executive Summary

### Purpose
Validate that architectural constraints (residual connections, dense connections, bottleneck layers) create distinguishable weight patterns between shallow (≤34 layers) and deep (≥50 layers) pretrained CNNs. This mechanism hypothesis tests whether architectural differences contribute to the depth classification capability established in H-E1.

### Success Criteria
- **Primary:** Architectural constraint features achieve >50% test accuracy (SHOULD_WORK gate)
- **Secondary:** Within-family classification accuracy ≥65% (depth signal independent of architecture family)
- **Tertiary:** Compare pretrained vs random initialization to distinguish architectural vs training-induced patterns

### Scope
Build on H-E1 and H-M1 infrastructure, introducing 8 architectural constraint features that explicitly capture residual blocks, dense connections, and bottleneck layer patterns.

---

## 2. Problem Statement

H-E1 demonstrated 100% depth classification accuracy with weight statistics. H-M1 tested gradient accumulation and achieved 100% accuracy, but the random initialization test also achieved 100%, indicating features are architectural rather than training-induced.

**Hypothesis Statement:**  
Under pretrained CNN architectures, if residual connections (ResNet), dense connections (DenseNet), and bottleneck layers exist in deep models but not shallow models, then weight structures will exhibit depth-specific patterns, because architectural constraints shape weight organization.

**Research Gap:**  
H-M1 revealed that discriminative features are architectural, not gradient-induced. H-M2 directly tests whether explicit architectural constraints (skip connections, bottleneck ratios) explain the classification success.

---

## 3. Stakeholders

- **Research Team:** Validate architectural constraints as a causal mechanism
- **Future Work:** Inform H-M3 (normalization effects) based on architectural vs normalization contributions
- **Dependent Hypotheses:** H-M3 depends on understanding architectural vs normalization mechanisms

---

## 4. Data Specification

### 4.1 Primary Dataset

**Dataset:** PyTorch Torchvision Pretrained Models (Consistent with H-E1 and H-M1)

**Source:** torchvision.models API (programmatic, no manual download)

**Models (20 total):**
- **Shallow (≤34 layers, n=10):** resnet18, resnet34, vgg11, vgg13, vgg16, vgg19, alexnet, squeezenet1_0, mobilenet_v2, densenet121
- **Deep (≥50 layers, n=10):** resnet50, resnet101, resnet152, densenet161, densenet169, densenet201, wide_resnet50_2, wide_resnet101_2, resnext50_32x4d, resnext101_32x8d

**Architecture Families:**
- **ResNet:** Has residual connections (shortcut paths with downsample attribute)
- **VGG:** Sequential architecture WITHOUT skip connections (control group)
- **DenseNet:** Has dense connections (each layer connects to all subsequent layers)

**Split:** 80/20 stratified (16 train, 4 test, seed=42)

**Access Method:**
```python
import torchvision.models as models
model = models.resnet50(pretrained=True)
```

**Data Preparation Tasks:**
- ✅ No manual download required (auto-download via PyTorch)
- ✅ Model loading: Reuse H-E1 and H-M1 infrastructure

### 4.2 Baseline Comparison Data

**H-E1 Results (Global Statistics):**
- Test Accuracy: 100% (4/4 correct)
- Features: 4 global statistics (mean, std, min, max of Frobenius norms)

**H-M1 Results (Gradient Flow Features):**
- Test Accuracy: 100% (4/4 correct)
- Random Test Accuracy: 100% (4/4 correct) → Mechanism REJECTED
- Key Finding: Features are architectural, not training-induced

**Random Baseline:** 50% (binary classification guess)

**Within-Family Benchmark:** 60-75% accuracy (from Archon KB research)

### 4.3 Data Processing

**Feature Extraction (NEW for H-M2):**
Extract 8 architectural constraint features per model:

1. **Residual Block Count:** Count modules with `downsample` attribute (ResNet-specific)
2. **Dense Connection Count:** Count layers with "denselayer" in name (DenseNet-specific)
3. **Bottleneck Layer Ratio:** (1×1 conv count) / (total conv count)
4. **Layer Count:** Total number of Conv2d layers
5. **Skip Connection Presence:** Binary indicator (1 if residual/dense connections exist, 0 otherwise)
6. **Architecture Family:** Binary indicator (1 if ResNet or DenseNet, 0 if VGG/other)
7. **Residual Path Weight Norm:** Mean Frobenius norm of downsample layer weights
8. **Transition Layer Count:** Count DenseNet transition layers

**Normalization:** StandardScaler (mean=0, std=1) - consistent with H-E1 and H-M1

---

## 5. Functional Requirements

### FR-1: Architectural Feature Extractor
**Priority:** P0 (Critical Path)  
**Description:** Implement `ArchitecturalFeatureExtractor` class to extract 8 architectural constraint features from pretrained models.

**Acceptance Criteria:**
- Detect residual blocks via `hasattr(module, 'downsample')` pattern
- Count dense connections via `'denselayer' in name.lower()` pattern
- Compute bottleneck ratio via kernel size inspection (1×1 convs)
- Extract residual path norms from downsample layers
- Count transition layers for DenseNet models
- Output: numpy array of shape (8,) per model
- Processing time: <10 seconds for 20 models

**Implementation Reference:**
- Based on `idiap/residual-networks-analysis` repository pattern (from Phase 2C)
- PyTorch module inspection: `model.named_modules()`, `model.named_parameters()`

### FR-2: Model Loader (Reuse H-E1/H-M1)
**Priority:** P0 (Critical Path)  
**Description:** Load 20 pretrained models from torchvision.models with automatic download.

**Acceptance Criteria:**
- Load all 20 models successfully
- Handle auto-download for first run
- Return model objects with accessible parameters and modules
- **Reuse H-E1/H-M1 implementation** (proven stable)

### FR-3: Binary Classifier (Reuse H-E1/H-M1)
**Priority:** P0 (Critical Path)  
**Description:** Train LogisticRegression classifier on architectural features.

**Acceptance Criteria:**
- Classifier: LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000, random_state=42)
- Feature scaling: StandardScaler
- Train on 16 models, test on 4 models
- **Reuse H-E1/H-M1 classifier configuration** (optimal hyperparameters)

### FR-4: Within-Family Validation
**Priority:** P1 (Mechanism Validation)  
**Description:** Train separate classifiers for ResNet-only, VGG-only, and DenseNet-only subsets to test depth signal within architecture families.

**Acceptance Criteria:**
- Filter models by architecture family (detect via model class name)
- Train 3 separate classifiers (one per family)
- Require ≥4 models per family for valid split
- Target: ≥65% within-family accuracy (depth signal independent of family)
- Report accuracy per family

**Rationale:** Isolates depth signal from architecture type confounds (critical for mechanism validation)

### FR-5: Random Initialization Test
**Priority:** P1 (Gate Validation)  
**Description:** Extract architectural features from randomly initialized (untrained) models to verify architectural vs training-induced patterns.

**Acceptance Criteria:**
- Initialize same 20 model architectures with random weights (pretrained=False)
- Extract architectural features (same 8 features)
- Train classifier on random models
- Expected behavior:
  - If random accuracy ≈ pretrained accuracy → Features are purely architectural (like H-M1)
  - If random accuracy << pretrained accuracy → Features are training-induced
- Report random test accuracy

**Rationale:** Following H-M1 protocol to distinguish architectural vs training effects

### FR-6: Evaluation Pipeline
**Priority:** P0 (Critical Path)  
**Description:** Compute test accuracy, within-family accuracy, and compare against baselines.

**Acceptance Criteria:**
- Calculate test accuracy on 4 held-out models (SHOULD_WORK gate: >50%)
- Generate confusion matrix
- Compare H-M2 vs H-E1 (100%) vs H-M1 (100%) vs Random (50%)
- Report feature importance (logistic regression coefficients)
- Identify which architectural features contribute most

### FR-7: Visualization Generation
**Priority:** P2 (Analysis)  
**Description:** Generate figures for mechanism validation and comparison with H-E1 and H-M1.

**Acceptance Criteria:**
- **Mandatory:** Gate metrics comparison bar chart (Test accuracy vs 50% threshold)
- **Feature Importance:** Bar chart of logistic regression coefficients for 8 features
- **Within-Family Accuracy:** Bar chart comparing ResNet, VGG, DenseNet, and All-families accuracy
- **Architectural Feature Distributions:** Box plots of 8 features split by shallow vs deep
- **Random vs Pretrained Comparison:** Side-by-side bar chart
- **H-E1 vs H-M1 vs H-M2 Comparison:** Three-way accuracy comparison
- **Confusion Matrix:** 2×2 heatmap with counts
- Save all figures to `h-m2/figures/`

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- Total experiment runtime: <90 seconds (feature extraction + training + evaluation + within-family tests)
- Feature extraction: <10 seconds for 20 models
- Training time: <1 second per classifier (linear model, 16 samples)
- Within-family training: <3 seconds total (3 classifiers)

### NFR-2: Reproducibility
- Fixed random seed: 42 (consistent with H-E1 and H-M1)
- Deterministic train-test split (stratified, same seed)
- Same model versions as H-E1 and H-M1 (torchvision pretrained weights)

### NFR-3: Code Reusability
- Reuse H-E1/H-M1 model loader (minimal changes)
- Reuse H-E1/H-M1 classifier configuration
- Modular feature extractor for easy comparison with H-E1 and H-M1

### NFR-4: Logging
- Print-based logging (FULL tier: standard infrastructure)
- Save metrics to JSON: `h-m2/code/outputs/metrics.json`
- Log feature extraction progress per model
- Log within-family validation results

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
- **H-M1:** Provides random initialization test protocol and mechanism validation framework

### 7.4 External Resources
- PyTorch torchvision pretrained models (auto-download from PyTorch Hub)
- No manual dataset downloads required
- No external baseline repositories required

---

## 8. Success Metrics

### 8.1 Gate Condition (SHOULD_WORK)
- **Primary Metric:** Test Accuracy > 50%
- **Consequence if Fails:** Document as limitation, proceed to H-M3 (normalization effects)
- **Pass Criteria:** At least 3/4 test models classified correctly

### 8.2 Mechanism Validation Metrics
- **Within-Family Accuracy:** ≥65% for at least one architecture family
  - Validates depth signal exists independent of architecture type
- **Random vs Pretrained Comparison:**
  - Expected: Random accuracy ≈ Pretrained accuracy (features are architectural)
  - Alternative: Random << Pretrained (features require training)

### 8.3 Comparative Metrics
- Compare H-M2 accuracy against:
  - H-E1: 100% (global statistics baseline)
  - H-M1: 100% (gradient flow features, but mechanism rejected)
  - Random: 50% (theoretical baseline)

### 8.4 Feature Analysis Metrics
- Feature importance ranking (which of 8 features contribute most)
- Residual blocks vs bottleneck ratio: Which matters more?
- ResNet/DenseNet vs VGG: Does skip connection presence predict depth?

---

## 9. Constraints and Assumptions

### 9.1 Constraints
- **Model Availability:** Limited to torchvision pretrained models (20 models)
- **Sample Size:** 20 models total, 4 test samples (small test set)
- **Architecture Coverage:** Only ResNet, VGG, DenseNet families (no Inception, EfficientNet)

### 9.2 Assumptions
- Torchvision pretrained models are trained with standard ImageNet protocol
- Model architectures are correctly identified via class name inspection
- Residual blocks are identifiable via `downsample` attribute (PyTorch convention)
- Dense connections are identifiable via "denselayer" naming (PyTorch convention)

### 9.3 Risks
- **Risk 1:** VGG models are deep (VGG19=19 layers) but have NO skip connections
  - Mitigation: VGG serves as control group; skip connection feature should differentiate
- **Risk 2:** Within-family validation may have insufficient samples per family
  - Mitigation: Report results only for families with ≥4 models
- **Risk 3:** Random initialization test may show same result as H-M1 (100% accuracy)
  - Impact: Confirms features are purely architectural (expected based on H-M1 findings)

---

## 10. Out of Scope

### Explicitly Excluded
- Training new models from scratch
- Fine-tuning pretrained models
- Testing on non-ImageNet pretrained models
- Cross-architecture transfer learning experiments
- Gradient flow analysis (covered by H-M1)
- Normalization layer analysis (reserved for H-M3)

### Future Work (Post-H-M2)
- H-M3: Batch normalization effects on depth classification
- Extended architecture families (Inception, EfficientNet, Vision Transformers)
- Quantitative mechanism attribution (how much do architectural constraints vs other factors contribute?)

---

## 11. Acceptance Criteria Summary

**Phase 4 Implementation Complete When:**
1. ✅ 8 architectural features extracted from all 20 models
2. ✅ Classifier trained on 16 models, tested on 4 models
3. ✅ Test accuracy > 50% (SHOULD_WORK gate satisfied)
4. ✅ Within-family validation completed for all eligible families
5. ✅ Random initialization test completed
6. ✅ All 7 figures generated and saved
7. ✅ Metrics saved to `metrics.json`
8. ✅ Validation report (`04_validation.md`) documents gate status and mechanism findings

---

## 12. Implementation Notes

### 12.1 Key Differences from H-M1
- **Feature Design:** Architectural constraints (8 features) vs gradient flow (6 features)
- **Mechanism Focus:** Skip connections and bottleneck layers vs layer-wise norm progression
- **Expected Outcome:** Likely 100% accuracy (H-M1 showed features are architectural)

### 12.2 Critical Implementation Details
- **Residual Block Detection:** Use `hasattr(module, 'downsample')` from `idiap/residual-networks-analysis`
- **Bottleneck Detection:** Inspect Conv2d kernel_size == (1, 1)
- **DenseNet Detection:** Use `'denselayer' in name.lower()` pattern
- **VGG Handling:** VGG has NO residual blocks, serves as negative control

### 12.3 Validation Protocol
- Follow H-M1 validation framework (gate check + mechanism validation + random test)
- If gate fails (<50%): Document limitation, note architectural constraints insufficient
- If random test also passes: Confirms features are purely architectural (not training-induced)
- Within-family results: Key mechanism insight (depth signal vs architecture type confound)

---

*This PRD defines requirements for H-M2 implementation (Phase 4 Coding). All functional requirements must be satisfied before proceeding to Phase 4 validation.*
