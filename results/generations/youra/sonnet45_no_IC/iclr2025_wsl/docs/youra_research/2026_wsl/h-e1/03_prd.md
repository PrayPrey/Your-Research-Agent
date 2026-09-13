# Product Requirements Document: H-E1 Operation-Specific Weight Signal Existence

**Date:** 2026-07-13
**Author:** Anonymous
**Hypothesis ID:** H-E1
**Type:** EXISTENCE (FOUNDATION)
**Gate:** MUST_WORK (≥80% accuracy blocks H-M-Integrated)

---

## Executive Summary

**Purpose:** Validate that operation-specific weight signals exist and are distinguishable beyond tensor dimensions through binary classification of ResNet-50 vs ViT-Base models using operation-agnostic statistics.

**Success Criteria:** Binary classifier achieves ≥80% test accuracy distinguishing ResNet from ViT using layer norms and spectral norms, with statistical significance (p < 0.05) vs random baseline.

**Gate Impact:** 
- **PASS (≥80%):** Proceed to H-M-Integrated (full CAPE mechanism)
- **PARTIAL (70-80%):** Explore enhanced statistics (Fisher eigenspectrum, NTK trace)
- **FAIL (<70%):** ABANDON modular encoder approach, fall back to SNE set-encoding baseline

---

## Problem Statement

### Research Question
Can operation-specific weight signals (convolution vs attention) be detected from operation-agnostic statistics alone, without relying on tensor shape information?

### Hypothesis Statement
Under ImageNet-trained model zoos (ResNet-50 vs ViT-Base), if operation-specific weight signals exist beyond tensor dimensions, then a binary classifier trained on operation-agnostic statistics (layer norms, spectral norms) will achieve ≥80% accuracy distinguishing ResNet from ViT.

### Context
This is the foundational test (EXISTENCE hypothesis) for the CAPE (Cross-Architecture Parameterized Encoder) project. It validates Assumption A1: "Operation-specific weight signals exist and are distinguishable."

**Prerequisites:** None (foundation hypothesis)
**Blocks:** H-M-Integrated (full mechanism validation)

---

## Functional Requirements

### FR-1: Model Zoo Collection
**Priority:** P0 (CRITICAL)
**Description:** Download 100 ImageNet-1K pre-trained models from HuggingFace Hub (50 ResNet-50, 50 ViT-Base)

**Acceptance Criteria:**
- 50 ResNet-50 models collected with diverse accuracy levels
- 50 ViT-Base models collected with diverse accuracy levels
- All models trained on ImageNet-1K (exclude fine-tuned variants)
- Models balanced across performance quantiles (low/mid/high accuracy)
- Models stored with metadata (model_id, architecture, imagenet_accuracy)

**Implementation Notes:**
- Use `huggingface_hub.list_models()` with filters: `task:image-classification AND dataset:imagenet-1k`
- Stratify by ImageNet top-1 accuracy to ensure diversity
- Store model paths and metadata in `models_metadata.json`

**Data Output:** 
- File: `{hypothesis_folder}/data/models_metadata.json`
- Format: `[{"model_id": "...", "architecture": "resnet50|vit_base", "accuracy": 0.xx, "hf_path": "..."}]`

---

### FR-2: Weight Statistics Extraction
**Priority:** P0 (CRITICAL)
**Description:** Extract operation-agnostic statistics from each model's weights

**Statistics to Extract (per layer):**
1. L2 norm: `torch.norm(param)`
2. Top-5 spectral norms: `torch.linalg.svdvals(param.reshape(param.shape[0], -1))[:5]`
3. Mean: `param.mean()`
4. Standard deviation: `param.std()`

**Acceptance Criteria:**
- All trainable parameters processed (skip biases and frozen layers)
- 2D+ parameters include spectral norms; 1D parameters skip spectral computation
- Feature vector concatenated across all layers
- Feature dimensionality consistent across architectures

**Implementation Notes:**
```python
def extract_weight_statistics(model_state_dict):
    features = []
    for name, param in model_state_dict.items():
        if not param.requires_grad or 'bias' in name:
            continue
        
        # L2 norm
        features.append(torch.norm(param).item())
        
        # Spectral norms (2D+ only)
        if len(param.shape) >= 2:
            param_2d = param.reshape(param.shape[0], -1)
            spectral_norms = torch.linalg.svdvals(param_2d)[:5]
            features.extend(spectral_norms.tolist())
        
        # Mean and std
        features.append(param.mean().item())
        features.append(param.std().item())
    
    return np.array(features)
```

**Data Output:**
- File: `{hypothesis_folder}/data/weight_features.npz`
- Format: `{"X": (100, num_features), "y": (100,), "model_ids": (100,)}`

---

### FR-3: Train/Test Split
**Priority:** P0 (CRITICAL)
**Description:** Create stratified train/test split ensuring balanced architecture distribution

**Acceptance Criteria:**
- 70 models for training (35 ResNet-50, 35 ViT-Base)
- 30 models for testing (15 ResNet-50, 15 ViT-Base)
- Stratification by accuracy quantiles within each architecture
- No data leakage between train/test

**Implementation Notes:**
- Use `sklearn.model_selection.train_test_split` with `stratify` parameter
- Random seed: 42 (reproducibility)

**Data Output:**
- Files: `train_indices.json`, `test_indices.json`

---

### FR-4: Binary Classifier Training (Norms-only Baseline)
**Priority:** P0 (CRITICAL)
**Description:** Train logistic regression classifier using L2 norms + mean + std only

**Acceptance Criteria:**
- Algorithm: Logistic Regression with L2 regularization
- Features: L2 norms, mean, std per layer (NO spectral norms)
- Preprocessing: StandardScaler (zero mean, unit variance)
- Hyperparameters: C=1.0, max_iter=1000, random_state=42
- Training accuracy computed on training set
- Test accuracy computed on held-out test set

**Implementation Notes:**
```python
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Extract norms-only features
X_train_norms = extract_norms_only(train_models)
y_train = np.array([0]*35 + [1]*35)  # 0=ResNet, 1=ViT

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train_norms)

clf_baseline = LogisticRegression(C=1.0, max_iter=1000, random_state=42)
clf_baseline.fit(X_train_scaled, y_train)

# Evaluate on test set
X_test_norms = extract_norms_only(test_models)
X_test_scaled = scaler.transform(X_test_norms)
baseline_accuracy = clf_baseline.score(X_test_scaled, y_test)
```

**Model Output:**
- File: `{hypothesis_folder}/models/classifier_norms_only.pkl`
- Metrics: Test accuracy, confusion matrix

---

### FR-5: Binary Classifier Training (Norms + Spectral)
**Priority:** P0 (CRITICAL)
**Description:** Train logistic regression classifier using full feature set (L2 norms + spectral norms + mean + std)

**Acceptance Criteria:**
- Same algorithm and hyperparameters as FR-4
- Features: L2 norms + top-5 spectral norms + mean + std per layer
- Same preprocessing (StandardScaler)
- Test accuracy ≥80% (hypothesis requirement)
- Improvement over norms-only ≥5% (ablation requirement)

**Implementation Notes:**
- Identical training procedure to FR-4, different feature set
- Compare: `accuracy_full - accuracy_baseline >= 0.05`

**Model Output:**
- File: `{hypothesis_folder}/models/classifier_full.pkl`
- Metrics: Test accuracy, confusion matrix, ablation delta

---

### FR-6: Statistical Significance Testing
**Priority:** P0 (CRITICAL)
**Description:** Permutation test to verify test accuracy significantly exceeds random baseline (50%)

**Acceptance Criteria:**
- Null hypothesis: Test accuracy = 50% (random guess)
- Procedure: 1000 random label permutations, compute accuracy distribution
- Significance level: p < 0.05 (test accuracy in top 5% of permuted distribution)
- Report: p-value and permutation distribution visualization

**Implementation Notes:**
```python
from sklearn.utils import shuffle

# Permutation test
permuted_accuracies = []
for i in range(1000):
    y_test_perm = shuffle(y_test, random_state=i)
    perm_acc = accuracy_score(y_test, clf.predict(X_test_scaled))
    permuted_accuracies.append(perm_acc)

# P-value: fraction of permuted >= actual
p_value = np.mean(permuted_accuracies >= actual_accuracy)
```

**Test Output:**
- File: `{hypothesis_folder}/results/permutation_test.json`
- Format: `{"p_value": 0.xx, "actual_accuracy": 0.xx, "permuted_mean": 0.xx}`

---

### FR-7: Evaluation Metrics Computation
**Priority:** P0 (CRITICAL)
**Description:** Compute comprehensive evaluation metrics for both classifiers

**Metrics:**
1. **Primary:** Test accuracy (percentage correctly classified)
2. **Secondary:** Ablation improvement (Norms+Spectral - Norms-only)
3. **Statistical:** p-value from permutation test
4. **Diagnostic:** Confusion matrix, per-class precision/recall

**Acceptance Criteria:**
- All metrics computed for both classifiers
- Results saved in structured format
- Comparison table generated

**Metrics Output:**
- File: `{hypothesis_folder}/results/metrics.json`
- Format:
```json
{
  "norms_only": {"test_accuracy": 0.xx, "confusion_matrix": [[...]]},
  "norms_spectral": {"test_accuracy": 0.xx, "confusion_matrix": [[...]]},
  "ablation_delta": 0.xx,
  "p_value": 0.xx
}
```

---

### FR-8: Visualization Generation
**Priority:** P1 (HIGH)
**Description:** Generate required and recommended visualizations

**Required Figure:**
- Gate Metrics Comparison: Bar chart showing Target (80%) vs Norms-only vs Norms+Spectral accuracy

**Recommended Figures:**
1. Confusion Matrix: 2x2 heatmap (ResNet/ViT classification)
2. Feature Importance: Coefficient magnitudes from logistic regression (top 10)
3. Permutation Test Distribution: Histogram with actual result marked
4. Accuracy by Model Performance: Scatter plot (classifier accuracy vs ImageNet accuracy)

**Acceptance Criteria:**
- All figures saved as PNG with 300 DPI
- Figures follow consistent style (matplotlib seaborn theme)
- All figures include titles, axis labels, and legends

**Visualization Output:**
- Directory: `{hypothesis_folder}/figures/`
- Files: `gate_comparison.png`, `confusion_matrix.png`, `feature_importance.png`, `permutation_dist.png`, `accuracy_vs_performance.png`

---

## Non-Functional Requirements

### NFR-1: Reproducibility
**Priority:** P0
- All random operations use fixed seeds (random_state=42)
- Model download order deterministic (alphabetical sort)
- Feature extraction order deterministic (state_dict iteration order)
- Results identical across re-runs

### NFR-2: Performance
**Priority:** P1
- Model download: < 5 minutes per model (parallelizable)
- Feature extraction: < 30 seconds per model
- Classifier training: < 10 seconds
- Total runtime: < 2 hours for full pipeline

### NFR-3: Storage
**Priority:** P1
- Model weights: ~200MB per model × 100 = 20GB (downloaded on-demand, not persisted)
- Feature data: < 100MB (weight_features.npz)
- Models: < 10MB (classifier_*.pkl)
- Figures: < 5MB total

### NFR-4: Error Handling
**Priority:** P1
- Graceful handling of model download failures (retry 3 times)
- Skip corrupted models with warning
- Validate feature dimensionality consistency
- Raise error if <90 models successfully processed

---

## Data Specifications

### Dataset: HuggingFace Model Hub - ImageNet Vision Models

**Source:** HuggingFace Hub (https://huggingface.co/models)
**Selection Criteria:**
- Task: image-classification
- Dataset: imagenet-1k (training dataset)
- Architectures: resnet-50, vit-base-patch16-224
- Type: Pre-trained weights (exclude fine-tuned)

**Collection Strategy:**
```python
from huggingface_hub import list_models

resnet_models = list(list_models(
    filter="resnet-50,imagenet-1k", 
    sort="downloads", 
    direction=-1,
    limit=50
))

vit_models = list(list_models(
    filter="vit-base-patch16,imagenet-1k",
    sort="downloads",
    direction=-1,
    limit=50
))
```

**Stratification:**
- Divide each architecture into 3 quantiles by ImageNet top-1 accuracy
- Sample evenly from each quantile for train/test split
- Ensures diverse performance levels in both sets

**Data Schema:**
```json
{
  "model_id": "string (unique identifier)",
  "architecture": "resnet50 | vit_base",
  "hf_path": "string (HuggingFace model path)",
  "imagenet_accuracy": "float (top-1 accuracy)",
  "download_url": "string",
  "split": "train | test"
}
```

---

## Success Criteria

### Primary Success Criterion (Gate)
**Test Accuracy ≥ 80%**
- Norms+Spectral classifier achieves ≥80% accuracy on held-out 30-model test set
- This is the MUST_WORK gate blocking H-M-Integrated

### Secondary Success Criterion (Ablation)
**Ablation Improvement ≥ 5%**
- Norms+Spectral accuracy exceeds Norms-only by at least 5 percentage points
- Validates that spectral norms add discriminative power

### Statistical Success Criterion
**p < 0.05 vs Random Baseline**
- Permutation test confirms test accuracy significantly exceeds 50% chance level
- Validates signal existence with statistical rigor

### Partial Success (70-80% accuracy)
- Signal exists but weaker than expected
- Action: Explore enhanced statistics (Fisher eigenspectrum, NTK trace)
- Still allows cautious progress to H-M-Integrated with modifications

### Failure Criteria (<70% accuracy)
- Insufficient signal distinguishing ResNet vs ViT
- Action: ABANDON modular encoder approach
- Fallback: SNE set-encoding baseline (ρ=0.54 known performance)

---

## Dependencies

### Technical Dependencies
| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | ≥3.8 | Runtime |
| PyTorch | ≥2.0 | Weight loading, tensor ops, SVD |
| NumPy | ≥1.21 | Array operations |
| scikit-learn | ≥1.0 | Logistic regression, metrics |
| huggingface_hub | ≥0.16 | Model discovery and download |
| matplotlib | ≥3.5 | Visualization |
| seaborn | ≥0.11 | Styled plots |

### Input Dependencies
| Input | Source | Requirement |
|-------|--------|-------------|
| Experiment Brief | Phase 2C | 02c_experiment_brief.md must exist |
| Model Zoo | HuggingFace Hub | Internet connection required |
| ImageNet Accuracy | Model cards | Metadata from HuggingFace |

### Hypothesis Dependencies
- **Prerequisites:** None (foundation hypothesis)
- **Blocks:** H-M-Integrated (full CAPE mechanism)
- **Gate Type:** MUST_WORK (hard blocker if failed)

---

## Risk Assessment

### Technical Risks

**Risk 1: Insufficient Model Diversity**
- **Impact:** High - Could bias classifier
- **Probability:** Low - HuggingFace has >50 models per architecture
- **Mitigation:** Stratify by accuracy, verify diversity metrics

**Risk 2: Feature Dimensionality Mismatch**
- **Impact:** Medium - Different architectures have different layer counts
- **Probability:** Medium - ResNet and ViT have very different structures
- **Mitigation:** Padding or truncation strategy, or architecture-specific handling

**Risk 3: Model Download Failures**
- **Impact:** Low - Can use fewer models if needed
- **Probability:** Medium - Network issues, deprecated models
- **Mitigation:** Retry logic, skip failed models, require ≥90 successful downloads

### Hypothesis Risks

**Risk 4: Signal Insufficient (<80% accuracy)**
- **Impact:** High - Blocks H-M-Integrated, requires fallback to SNE
- **Probability:** Medium - Untested assumption
- **Mitigation:** Partial success path (70-80%) explores enhanced statistics

**Risk 5: Spectral Norms Don't Add Value (<5% improvement)**
- **Impact:** Medium - Questions operation-specific encoding approach
- **Probability:** Low - Spectral analysis widely used in weight-space research
- **Mitigation:** Explore alternative statistics (Fisher, NTK)

---

## Timeline Estimate

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Data Collection** | 2-4 hours | Model zoo download, metadata extraction |
| **Feature Extraction** | 1-2 hours | Weight statistics computation |
| **Classifier Training** | < 30 min | Train both classifiers, compute metrics |
| **Statistical Testing** | < 30 min | Permutation test, significance analysis |
| **Visualization** | 1 hour | Generate all required figures |
| **Validation** | 1 hour | Verify results, write validation report |
| **Total** | 6-8 hours | Full pipeline execution |

**Note:** This is a PoC (Proof of Concept) experiment - no extensive hyperparameter tuning or model training required.

---

## Appendix A: Related Work

### SANE (Set-based Tokenization)
- Zhou et al. 2022
- Same-family transfer: +2.2% (ResNet-18→50)
- Approach: Tokenize weights into sets

### SNE (Set-Encoding Baseline)
- Karpathy et al. 2021
- Cross-architecture: ρ=0.54 (ResNet→ViT)
- Current best for cross-architecture prediction

### UNF (Universal Neural Functionals)
- Navon et al. 2023
- Theorem 3.2: Permutation-equivariance for weight-space encoders
- Basis for operation-agnostic statistics

---

## Appendix B: Gate Decision Logic

```python
def evaluate_gate(test_accuracy, p_value, ablation_delta):
    """
    Determine gate status for H-E1.
    
    Returns: ("PASS" | "PARTIAL" | "FAIL", action_string)
    """
    if test_accuracy >= 0.80 and p_value < 0.05 and ablation_delta >= 0.05:
        return "PASS", "Proceed to H-M-Integrated"
    elif 0.70 <= test_accuracy < 0.80 and p_value < 0.05:
        return "PARTIAL", "Explore enhanced statistics before H-M-Integrated"
    else:
        return "FAIL", "ABANDON modular encoders, fall back to SNE baseline"
```

---

## Appendix C: File Structure

```
docs/youra_research/h-e1/
├── 02c_experiment_brief.md           # Input (Phase 2C)
├── 03_prd.md                          # This document
├── 03_architecture.md                 # Next step (Phase 3)
├── 03_logic.md                        # Phase 3
├── 03_config.md                       # Phase 3
├── 03_tasks.yaml                      # Phase 3
├── data/
│   ├── models_metadata.json           # Model zoo metadata
│   ├── weight_features.npz            # Extracted features
│   ├── train_indices.json             # Train split
│   └── test_indices.json              # Test split
├── models/
│   ├── classifier_norms_only.pkl      # Baseline classifier
│   └── classifier_full.pkl            # Full classifier
├── results/
│   ├── metrics.json                   # All evaluation metrics
│   └── permutation_test.json          # Statistical test results
└── figures/
    ├── gate_comparison.png            # REQUIRED
    ├── confusion_matrix.png
    ├── feature_importance.png
    ├── permutation_dist.png
    └── accuracy_vs_performance.png
```

---

**Document Status:** COMPLETE
**Next Phase:** Step 3 - Architecture Agent (Epic-level task breakdown)
**Validation:** Ready for implementation planning
