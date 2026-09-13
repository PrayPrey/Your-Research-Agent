# Product Requirements Document: H-E1
## Compression Ordering Effect Existence

**Version:** 1.0  
**Date:** 2026-08-25  
**Hypothesis ID:** h-e1  
**Gate Type:** MUST_WORK

---

## 1. Executive Summary

This experiment validates whether compression ordering (prune-first vs quantize-first) produces measurably different accuracy outcomes (>1% difference) on ResNet-18 at 50% parameter reduction + INT8 quantization on ImageNet-1K.

**Success Criteria:** Demonstrate statistically significant accuracy difference (p < 0.05) between orderings with effect size > 0.5%.

---

## 2. Problem Statement

Neural network compression typically applies pruning and quantization, but the optimal ordering is unclear. This experiment establishes whether ordering matters at all before investigating predictive mechanisms.

---

## 3. Functional Requirements

### FR-1: Prune-First Pipeline
- Load pretrained ResNet-18 from torchvision
- Apply 50% global unstructured L1 pruning to Conv2d layers
- Fine-tune on ImageNet-1K 10% subset (5 epochs)
- Apply INT8 post-training quantization (fbgemm backend)
- Evaluate on full validation set (~50K images)

### FR-2: Quantize-First Pipeline
- Load pretrained ResNet-18 from torchvision
- Apply INT8 post-training quantization (fbgemm backend, 1024 calibration samples)
- Apply 50% global unstructured L1 pruning to quantized weights
- Fine-tune on ImageNet-1K 10% subset (5 epochs)
- Evaluate on full validation set (~50K images)

### FR-3: Multi-Seed Evaluation
- Run each ordering with 3 random seeds (42, 123, 456)
- Total: 6 experiment runs (2 orderings × 3 seeds)

### FR-4: Metrics Collection
- Top-1 accuracy on validation set
- Top-5 accuracy on validation set
- Per-layer sparsity patterns (for downstream h-m1)

### FR-5: Statistical Analysis
- Paired t-test between orderings across seeds
- Effect size calculation (mean difference)
- p-value < 0.05 for significance

---

## 4. Data Specification

### 4.1 Primary Dataset: ImageNet-1K (ILSVRC2012)

| Attribute | Value |
|-----------|-------|
| Name | ImageNet-1K |
| Type | standard |
| Download | Manual (requires academic access) |
| Train Subset | 10% stratified (~128K images) |
| Validation | Full set (~50K images) |
| Classes | 1000 |
| Resolution | 224×224 (center crop from 256) |
| Storage | ~150GB |

### 4.2 Preprocessing

```python
transform_train = transforms.Compose([
    transforms.RandomResizedCrop(224),
    transforms.RandomHorizontalFlip(),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

transform_val = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])
```

---

## 5. Model Specification

### 5.1 Base Model

| Attribute | Value |
|-----------|-------|
| Architecture | ResNet-18 |
| Source | torchvision.models.resnet18(weights='IMAGENET1K_V1') |
| Parameters | 11.7M |
| Baseline Accuracy | 69.76% top-1 |

### 5.2 Compression Configuration

**Pruning:**
- Method: Global Unstructured L1 (torch.nn.utils.prune)
- Target: Conv2d layers only
- Amount: 50%

**Quantization:**
- Type: Post-Training Quantization (PTQ)
- Backend: fbgemm (x86)
- Calibration: 1024 samples from training set

---

## 6. Success Criteria

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Effect Size | > 0.5% | abs(mean_prune_first - mean_quant_first) |
| Statistical Significance | p < 0.05 | Paired t-test |
| Consistency | Same winner across seeds | Visual inspection |

**Gate Decision:**
- PASS: Effect > 0.5% AND p < 0.05
- FAIL: Effect ≤ 0.5% OR p ≥ 0.05

---

## 7. Dependencies

### 7.1 Python Packages

```
torch>=2.0.0
torchvision>=0.15.0
torchmetrics>=1.0.0
numpy>=1.24.0
scipy>=1.10.0
pyyaml>=6.0
tqdm>=4.65.0
```

### 7.2 Hardware Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| GPU | 1× RTX 3080 (10GB) | 1× A100 (40GB) |
| RAM | 32GB | 64GB |
| Storage | 200GB | 500GB |
| GPU Hours | 2-4 | 4-6 |

---

## 8. Non-Functional Requirements

### NFR-1: Reproducibility
- All random seeds must be set (torch, numpy, CUDA)
- Deterministic mode enabled where possible

### NFR-2: Logging
- Log accuracy per epoch during fine-tuning
- Save per-layer statistics for h-m1 downstream use

### NFR-3: Checkpointing
- Save model after pruning (before fine-tune)
- Save model after fine-tuning (before/after quantization)

---

## 9. Deliverables

1. **Results Table:** 6 runs with top-1/top-5 accuracy
2. **Statistical Report:** t-test results, effect size, CI
3. **Per-Layer Data:** CSV with sparsity patterns (for h-m1)
4. **Gate Decision:** PASS/FAIL with justification
