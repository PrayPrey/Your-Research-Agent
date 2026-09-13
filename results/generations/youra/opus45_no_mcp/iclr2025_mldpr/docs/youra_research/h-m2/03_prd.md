# Product Requirements Document: H-M2

**Hypothesis:** Dataset-specific optimization creates features that exploit dataset artifacts (texture bias)
**Type:** MECHANISM
**Date:** 2026-08-19
**Author:** Phase 3 Implementation Planning

---

## 1. Executive Summary

This PRD defines requirements for testing whether modern architectures (post-2015, heavily optimized on popular benchmarks) exhibit higher texture bias than legacy architectures (pre-2015). The experiment uses Geirhos et al. (2019) methodology with Stylized-CIFAR-10 conflict stimuli.

**Key Deliverable:** Texture bias comparison between ResNet-18 (modern) and VGG-11 (legacy) trained on CIFAR-10.

---

## 2. Problem Statement

H-M1 established that popular benchmarks attract 24.68x more optimization papers. H-M2 tests whether this intensive optimization produces texture-exploiting features rather than generalizable shape-based representations.

**Research Question:** Does architecture era (optimized vs. legacy) correlate with texture bias when trained on popular datasets?

---

## 3. Goals and Objectives

### Primary Goal
Measure and compare texture bias ratios between modern (ResNet-18) and legacy (VGG-11) architectures.

### Success Criteria
- **Gate Pass:** ResNet-18 texture_bias_ratio > VGG-11 texture_bias_ratio
- **Effect Size:** Difference > 0.05 (5 percentage points)
- **Direction:** Modern architecture shows MORE texture bias

### Out of Scope
- Shape-texture debiasing interventions
- Alternative texture bias measurements beyond Geirhos methodology
- Architectures beyond ResNet-18/VGG-11 comparison

---

## 4. Data Specification

### 4.1 Primary Dataset: CIFAR-10

| Attribute | Value |
|-----------|-------|
| Source | torchvision.datasets.CIFAR10 |
| Download | Automatic (PyTorch) |
| Size | 60,000 images (50k train, 10k test) |
| Resolution | 32x32 RGB |
| Classes | 10 object categories |

### 4.2 Texture Source: Describable Textures Dataset (DTD)

| Attribute | Value |
|-----------|-------|
| Source | https://www.robots.ox.ac.uk/~vgg/data/dtd/ |
| Download | **Manual download required** |
| Size | 5,640 images, 47 texture categories |
| Purpose | Style source for AdaIN transfer |
| Local Path | data/dtd/ |

### 4.3 Conflict Stimuli: Stylized-CIFAR-10

| Attribute | Value |
|-----------|-------|
| Source | Generated programmatically |
| Method | AdaIN style transfer (CIFAR shape + DTD texture) |
| Test Size | 10,000 conflict images (full CIFAR-10 test set) |
| Purpose | Shape-texture conflict for bias measurement |

---

## 5. Functional Requirements

### FR-1: Data Pipeline
- FR-1.1: Download CIFAR-10 via torchvision (automatic)
- FR-1.2: Load DTD textures from local path
- FR-1.3: Generate Stylized-CIFAR-10 conflict stimuli using AdaIN
- FR-1.4: Create DataLoader with (image, shape_label, texture_label) triplets

### FR-2: Model Implementation
- FR-2.1: Implement VGG-11 baseline adapted for CIFAR-10 (32x32 input)
- FR-2.2: Implement ResNet-18 adapted for CIFAR-10
- FR-2.3: Both models use identical training configuration

### FR-3: Training Pipeline
- FR-3.1: Train both models on CIFAR-10 for 200 epochs
- FR-3.2: Use SGD with cosine learning rate decay (0.1 → 0.001)
- FR-3.3: Standard augmentation: RandomCrop(32, padding=4), RandomHorizontalFlip
- FR-3.4: Save checkpoints for texture bias evaluation

### FR-4: Evaluation Pipeline
- FR-4.1: Implement texture bias measurement (Geirhos methodology)
- FR-4.2: Calculate texture_bias_ratio = P(predict texture) / (P(predict texture) + P(predict shape))
- FR-4.3: Report shape accuracy, texture accuracy, and neither count
- FR-4.4: Compare ResNet-18 vs VGG-11 texture bias

### FR-5: Visualization
- FR-5.1: Generate gate metrics comparison bar chart
- FR-5.2: Save figures to h-m2/figures/

### FR-6: Ablation Studies (Optional)
- FR-6.1: Pretrained vs Random Init comparison
- FR-6.2: Training duration effect (50, 100, 150, 200 epochs)

---

## 6. Non-Functional Requirements

### NFR-1: Performance
- Training: Complete within 4 hours on single GPU
- Inference: Process 10k conflict images in <30 minutes

### NFR-2: Reproducibility
- Fixed random seeds for training
- Deterministic AdaIN style transfer

### NFR-3: Scale
- Full CIFAR-10 test set (10,000 samples) for evaluation
- Full DTD dataset for texture variety

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
torchvision>=0.15.0
numpy>=1.24.0
matplotlib>=3.7.0
pyyaml>=6.0
tqdm>=4.65.0
```

### 7.2 External Datasets
- DTD: Manual download from https://www.robots.ox.ac.uk/~vgg/data/dtd/

### 7.3 Reference Implementations
- Geirhos et al. texture-vs-shape: https://github.com/rgeirhos/texture-vs-shape
- AdaIN style transfer: Huang & Belongie (2017)

---

## 8. Success Criteria Summary

| Metric | Pass Condition |
|--------|----------------|
| Code Execution | Runs without error |
| Direction Check | ResNet-18 texture_bias > VGG-11 texture_bias |
| Effect Size | Difference > 0.05 |
| Sample Size | Full 10k test set evaluated |

---

## 9. Appendix: Texture Bias Measurement

```python
def measure_texture_bias(model, conflict_loader):
    """
    Returns texture_bias_ratio in [0, 1]
    1.0 = pure texture classifier
    0.0 = pure shape classifier
    """
    texture_correct = 0
    shape_correct = 0
    total = 0
    
    for images, shape_labels, texture_labels in conflict_loader:
        predictions = model(images).argmax(dim=1)
        texture_correct += (predictions == texture_labels).sum()
        shape_correct += (predictions == shape_labels).sum()
        total += images.size(0)
    
    return texture_correct / (texture_correct + shape_correct + 1e-8)
```
