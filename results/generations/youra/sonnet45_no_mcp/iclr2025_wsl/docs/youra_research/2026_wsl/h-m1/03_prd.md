# Product Requirements Document: H-M1 Gradient Flow Feature Validation

**Hypothesis:** H-M1  
**Type:** Mechanism  
**Date:** 2026-04-21  
**Author:** Phase 3 Implementation Planning

---

## 1. Executive Summary

### Purpose
Validate that gradient accumulation patterns during training create distinguishable weight magnitude features between shallow (≤34 layers) and deep (≥50 layers) pretrained CNNs. This mechanism hypothesis tests whether gradient flow through depth creates characteristic signatures in layer-wise weight norm progressions.

### Success Criteria
- **Primary:** Gradient-flow features achieve >50% test accuracy (better than random baseline)
- **Secondary:** Compare performance against H-E1 baseline (100% accuracy with global statistics)
- **Tertiary:** Random initialized models fail to classify (<55% accuracy), confirming training-induced patterns

### Scope
Build on H-E1's proven infrastructure, replacing global weight statistics with gradient-specific features that capture layer-wise progression patterns.

---

## 2. Problem Statement

H-E1 demonstrated that weight statistics enable 100% depth classification accuracy. However, it remains unclear which mechanism drives this discriminability. H-M1 tests the first proposed mechanism: **gradient accumulation through depth during training**.

**Hypothesis Statement:**  
Under pretrained CNN training, if gradient transformations accumulate across 50+ layers (deep) versus <34 layers (shallow), then weight magnitude patterns will differ measurably, because backpropagation through more layers creates characteristic gradient flow signatures.

**Research Gap:**  
Does the observed classification success (H-E1) stem from gradient flow patterns during training, or from other mechanisms (architectural constraints, normalization effects)?

---

## 3. Stakeholders

- **Research Team:** Validate gradient accumulation as a causal mechanism
- **Future Work:** Inform H-M2 (architectural mechanisms) and H-M3 (normalization effects)
- **Dependent Hypotheses:** H-M2, H-M3 depend on understanding relative mechanism contributions

---

## 4. Data Specification

### 4.1 Primary Dataset

**Dataset:** PyTorch Torchvision Pretrained Models (Reused from H-E1)

**Source:** torchvision.models API (programmatic, no manual download)

**Models (20 total):**
- **Shallow (≤34 layers, n=10):** resnet18, resnet34, vgg11, vgg13, vgg16, vgg19, alexnet, squeezenet1_0, mobilenet_v2, densenet121
- **Deep (≥50 layers, n=10):** resnet50, resnet101, resnet152, densenet161, densenet169, densenet201, wide_resnet50_2, wide_resnet101_2, resnext50_32x4d, resnext101_32x8d

**Split:** 80/20 stratified (16 train, 4 test, seed=42)

**Access Method:**
```python
import torchvision.models as models
model = models.resnet50(pretrained=True)
```

**Data Preparation Tasks:**
- ✅ No manual download required (auto-download via PyTorch)
- ✅ Model loading: Implemented in H-E1, reuse infrastructure

### 4.2 Baseline Comparison Data

**H-E1 Results:**
- Test Accuracy: 100% (4/4 correct)
- Train Accuracy: 93.8% (15/16 correct)
- Features: 4 global statistics (mean, std, min, max of layer-wise Frobenius norms)

**Random Baseline:** 50% (binary classification guess)

### 4.3 Data Processing

**Feature Extraction (NEW for H-M1):**
- Extract layer-wise Frobenius norms for all Conv2d/Linear weight tensors
- Track normalized layer position (0.0 = input layer, 1.0 = output layer)
- Compute 6 gradient-flow features per model:
  1. Norm progression slope (linear fit across layers)
  2. Norm variance (gradient stability)
  3. Input-layer norm (initial magnitude)
  4. Output-layer norm (final magnitude)
  5. Depth-weighted norm (position × magnitude)
  6. Layer count (explicit depth proxy)

**Normalization:** StandardScaler (mean=0, std=1) - same as H-E1

---

## 5. Functional Requirements

### FR-1: Gradient Flow Feature Extractor
**Priority:** P0 (Critical Path)  
**Description:** Implement `GradientFlowFeatureExtractor` class to extract 6 gradient-related features from pretrained models.

**Acceptance Criteria:**
- Extract layer-wise Frobenius norms with position tracking
- Compute norm progression slope via linear regression
- Calculate norm variance, input/output norms, depth-weighted norm, layer count
- Output: numpy array of shape (6,) per model
- Processing time: <5 seconds for 20 models

### FR-2: Model Loader (Reuse H-E1)
**Priority:** P0 (Critical Path)  
**Description:** Load 20 pretrained models from torchvision.models with automatic download.

**Acceptance Criteria:**
- Load all 20 models successfully
- Handle auto-download for first run
- Return model objects with accessible parameters
- **Reuse H-E1 implementation** (proven stable)

### FR-3: Binary Classifier (Reuse H-E1)
**Priority:** P0 (Critical Path)  
**Description:** Train LogisticRegression classifier on gradient-flow features.

**Acceptance Criteria:**
- Classifier: LogisticRegression(C=1.0, solver='lbfgs', max_iter=1000)
- Feature scaling: StandardScaler
- Train on 16 models, test on 4 models
- **Reuse H-E1 classifier configuration** (optimal hyperparameters)

### FR-4: Evaluation Pipeline
**Priority:** P0 (Critical Path)  
**Description:** Compute test accuracy and compare against H-E1 baseline and random guess.

**Acceptance Criteria:**
- Calculate test accuracy on 4 held-out models
- Generate confusion matrix
- Compare H-M1 accuracy vs H-E1 (100%) vs Random (50%)
- Report feature importance (logistic regression coefficients)

### FR-5: Random Initialization Test
**Priority:** P1 (Gate Validation)  
**Description:** Extract gradient-flow features from randomly initialized (untrained) models to verify training-induced patterns.

**Acceptance Criteria:**
- Initialize same 20 model architectures with random weights
- Extract gradient-flow features (same 6 features)
- Train classifier on random models
- Expected: <55% accuracy (fail to classify), confirming gradient flow signature requires training

### FR-6: Visualization Generation
**Priority:** P2 (Analysis)  
**Description:** Generate figures for mechanism validation and comparison with H-E1.

**Acceptance Criteria:**
- **Mandatory:** Test accuracy bar chart (H-E1 vs H-M1 vs Random baseline)
- **Optional:** Layer-wise norm progression plot (shallow vs deep)
- **Optional:** Feature importance comparison (H-E1's 4 features vs H-M1's 6 features)
- **Optional:** Confusion matrix, feature distribution box plots
- Save all figures to `h-m1/figures/`

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- Total experiment runtime: <60 seconds (feature extraction + training + evaluation)
- Feature extraction: <5 seconds for 20 models
- Training time: <1 second (linear model, 16 samples)

### NFR-2: Reproducibility
- Fixed random seed: 42 (consistent with H-E1)
- Deterministic train-test split (stratified, same seed)
- Same model versions as H-E1 (torchvision pretrained weights)

### NFR-3: Code Reusability
- Reuse H-E1 model loader (minimal changes)
- Reuse H-E1 classifier configuration
- Modular feature extractor for easy comparison

### NFR-4: Logging
- Print-based logging (LIGHT tier)
- Save metrics to CSV: `h-m1/code/outputs/metrics.json`
- Log feature extraction progress per model

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

### 7.2 External Code References

**H-E1 Codebase (Base Hypothesis):**
- Model loader: `h-e1/code/model_loader.py` (reuse)
- Classifier pipeline: `h-e1/code/classifier.py` (reuse configuration)
- Evaluation: `h-e1/code/evaluate.py` (reuse metrics)

**Modifications for H-M1:**
- Replace feature extractor: `GlobalStatisticsExtractor` → `GradientFlowFeatureExtractor`
- Add random initialization test
- Update visualization to compare feature sets

### 7.3 Hardware Requirements

- **GPU:** Not required (feature extraction from pretrained weights, no training)
- **CPU:** Any modern CPU (feature extraction is lightweight)
- **RAM:** ~4GB (load 20 pretrained models sequentially)
- **Storage:** ~500MB (pretrained model weights auto-downloaded)

---

## 8. Success Criteria

### 8.1 Primary Gate (MUST_WORK)
- **Gradient-flow features contribute to classification:** Test accuracy > 50% (random baseline)
- **Rationale:** If gradient accumulation is a mechanism, features derived from gradient flow patterns should enable better-than-random classification.

### 8.2 Secondary Validation
- **Training-induced patterns:** Random initialized models achieve <55% accuracy (fail to classify)
- **Rationale:** If random models classify well, features are architectural (not gradient-induced).

### 8.3 Mechanism Contribution Analysis
| H-M1 Accuracy | Interpretation | Next Steps |
|---------------|----------------|------------|
| ≥ 100% | Gradient flow is sufficient mechanism | H-M2/H-M3 may be redundant |
| 70-99% | Gradient flow is strong contributor | Test H-M2/H-M3 for residual signal |
| 50-69% | Gradient flow is partial contributor | H-M2/H-M3 likely necessary |
| <50% | Gradient flow not a mechanism (FAIL) | Investigate alternative mechanisms |

### 8.4 Comparison with H-E1
- **H-E1 (all weight statistics):** 100% test accuracy
- **H-M1 (gradient-flow features only):** Expected 70-100% if gradient is key mechanism
- **Performance gap:** (H-E1 - H-M1) indicates contribution from other mechanisms (architecture/normalization)

---

## 9. Out of Scope

- **Neural network training:** This is feature extraction + linear classification, not DL training
- **New datasets:** Use same 20 models as H-E1 (controlled experiment)
- **Hyperparameter tuning:** Use H-E1's optimal LogisticRegression configuration
- **Deep learning frameworks beyond PyTorch:** Focus on torchvision models
- **Production deployment:** Research experiment only

---

## 10. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Gradient-flow features fail (accuracy <50%) | MUST_WORK gate fails | Document as negative result, proceed to H-M2/H-M3 |
| Random models also classify well | Invalidates gradient mechanism | Report architectural mechanism dominance |
| Performance gap from H-E1 too large | Partial mechanism only | Quantify contribution, test H-M2/H-M3 |
| Code reuse breaks H-E1 compatibility | Regression in baseline | Maintain separate feature extractors |

---

## 11. Acceptance Criteria Summary

**Ready for Phase 4 when:**
- ✅ All 6 FRs implemented (FR-1 to FR-6)
- ✅ All NFRs met (performance, reproducibility, reusability, logging)
- ✅ Dependencies installed
- ✅ H-E1 codebase reviewed for reuse components
- ✅ Test accuracy computed on 4 held-out models
- ✅ Random initialization test completed
- ✅ Mandatory visualization (accuracy bar chart) generated
- ✅ Metrics saved to `h-m1/code/outputs/metrics.json`

**Gate Criteria (for Phase 4.5):**
- Test accuracy > 50% (primary gate)
- Random models < 55% accuracy (validation)

---

## Appendix A: H-E1 Reuse Checklist

**Components to Reuse:**
- ✅ Model loader (torchvision.models, same 20 models)
- ✅ Train-test split logic (stratified, seed=42)
- ✅ Classifier configuration (LogisticRegression, StandardScaler)
- ✅ Evaluation metrics (accuracy_score, confusion_matrix)
- ✅ Output structure (metrics.json, figures/)

**Components to Replace:**
- ❌ Feature extractor: `GlobalStatisticsExtractor` → `GradientFlowFeatureExtractor`
- ❌ Feature count: 4 global features → 6 gradient-flow features
- ❌ Visualization: Add feature importance comparison plot

**Integration Strategy:**
- Import H-E1 model loader, classifier, evaluation modules
- Implement new `GradientFlowFeatureExtractor` as drop-in replacement
- Run experiment with identical pipeline (only feature extraction differs)

---

*PRD v1.0 | Generated by Phase 3 Implementation Planning | Hypothesis: H-M1*
