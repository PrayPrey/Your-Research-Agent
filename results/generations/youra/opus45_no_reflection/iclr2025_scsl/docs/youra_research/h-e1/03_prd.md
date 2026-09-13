# Product Requirements Document: H-E1

**Date:** 2026-08-19
**Hypothesis:** CV of probe accuracy trajectories distinguishes spurious from core features with AUC >= 0.75
**Type:** EXISTENCE (PoC)
**Author:** Anonymous

---

## 1. Executive Summary

Validate that the coefficient of variation (CV) of linear probe accuracy trajectories can distinguish spurious features from core features in image classification. This proof-of-concept tests whether CV-based metrics provide a reliable signal for spurious correlation detection.

**Success Criteria:** AUC >= 0.75 for CV-based spurious vs core feature classification.

---

## 2. Problem Statement

Deep learning models learn spurious correlations (e.g., background features) that hurt worst-group accuracy. Existing detection methods require group labels. This experiment tests whether CV of probe accuracy trajectories—computed without group labels—can identify spurious features.

---

## 3. Functional Requirements

### FR-1: Dataset Loading
Load Waterbirds dataset with ground truth spurious/core labels.
- Download from Stanford NLP repository
- Parse metadata.csv for group assignments
- Support train/val/test splits (4795/1199/5794 samples)

### FR-2: Feature Extraction
Extract CLIP ViT-B/16 features for all images.
- Load pretrained CLIP model
- Extract 512-dim features
- L2-normalize features
- Cache features to disk

### FR-3: Linear Probe Training
Train logistic regression probes on random subsets.
- 5 random 20% subsets
- 10 regularization checkpoints (C: 0.001 to 100)
- Probe for both background (spurious) and bird_type (core)

### FR-4: CV Computation
Compute CV of accuracy improvement rates across subsets.
- Track accuracy trajectory per subset
- Calculate improvement rate (final - initial accuracy)
- Compute CV = std(rates) / mean(rates)

### FR-5: AUC Evaluation
Evaluate CV-based classifier performance.
- Compute ROC-AUC using CV values
- Lower CV = higher spurious probability
- Report AUC, precision, recall at various thresholds

### FR-6: Visualization
Generate analysis figures.
- CV distribution histogram by feature type
- ROC curve with AUC annotation
- Probe accuracy trajectories

---

## 4. Data Specification

### Primary Dataset: Waterbirds

| Attribute | Value |
|-----------|-------|
| Name | Waterbirds |
| Version | waterbird_complete95_forest2water2 |
| Source | https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz |
| Train | 4,795 samples |
| Val | 1,199 samples |
| Test | 5,794 samples |
| Groups | 4 (landbird-land, landbird-water, waterbird-land, waterbird-water) |
| Spurious Correlation | 95% (background correlates with bird type) |

**Download Required:** Yes (manual download, ~1.2GB)

---

## 5. Model Specification

### Feature Extractor: CLIP ViT-B/16

| Attribute | Value |
|-----------|-------|
| Architecture | Vision Transformer B/16 |
| Source | openai/clip |
| Output Dim | 512 |
| Pretrained | Yes (frozen) |
| Purpose | Feature extraction only |

### Classifier: Logistic Regression

| Attribute | Value |
|-----------|-------|
| Library | sklearn.linear_model |
| Solver | L-BFGS |
| Regularization | Sweep C in [0.001, 100] |
| Max Iterations | 1000 |

---

## 6. Evaluation Metrics

### Primary Metric
- **AUC**: ROC-AUC for CV-based spurious/core classification (target >= 0.75)

### Secondary Metrics
- **CV Separation**: Visual separation of CV distributions
- **Precision/Recall**: At optimal threshold
- **F1 Score**: At optimal threshold

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
clip @ git+https://github.com/openai/CLIP.git
scikit-learn>=1.0.0
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.5.0
pillow>=9.0.0
tqdm>=4.62.0
pyyaml>=6.0
```

### 7.2 Hardware Requirements
- GPU recommended for CLIP feature extraction
- ~8GB GPU memory for ViT-B/16
- ~10GB disk for dataset + cached features

---

## 8. Non-Functional Requirements

### NFR-1: Reproducibility
- Fixed random seeds (42)
- Deterministic feature extraction
- Cached intermediate results

### NFR-2: Performance
- Feature extraction: <10 min with GPU
- Probe training: <5 min total
- Full pipeline: <20 min

### NFR-3: Output Format
- Results in YAML format
- Figures in PNG (300 DPI)
- All outputs in hypothesis folder

---

## 9. Success Criteria

| Criterion | Threshold | Priority |
|-----------|-----------|----------|
| AUC >= 0.75 | Primary gate | MUST |
| CV(spurious) < CV(core) | Directional | SHOULD |
| Pipeline completes | Functional | MUST |
| Figures generated | Visualization | SHOULD |

---

## 10. Out of Scope

- Training neural networks (using pretrained CLIP)
- Group DRO or reweighting methods
- Multi-dataset evaluation
- Hyperparameter optimization beyond regularization sweep
