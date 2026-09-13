# Phase 2C: Experiment Brief
## Sub-Hypothesis h-e1: Compression Ordering Effect Existence

**Generated:** 2026-08-25  
**Status:** READY for Phase 3  
**Gate Type:** MUST_WORK

---

## 1. Hypothesis Statement

Compression ordering (prune-first vs quantize-first) produces measurably different accuracy outcomes (>1% difference) on ResNet-18 at 50% parameter reduction + INT8 quantization on ImageNet-1K.

---

## 2. Experimental Design

### 2.1 Independent Variables

| Variable | Levels | Description |
|----------|--------|-------------|
| Compression Order | 2 | prune-first, quantize-first |
| Random Seed | 3 | 42, 123, 456 |

### 2.2 Dependent Variables

| Metric | Description | Collection Method |
|--------|-------------|-------------------|
| Top-1 Accuracy | Classification accuracy | `torchmetrics.Accuracy` |
| Top-5 Accuracy | Top-5 classification | `torchmetrics.Accuracy(top_k=5)` |
| Per-Layer Accuracy Delta | Accuracy difference per layer ordering | Custom logging |

### 2.3 Controlled Variables

| Variable | Fixed Value | Rationale |
|----------|-------------|-----------|
| Model | ResNet-18 (pretrained) | Standard benchmark, ~11M params |
| Dataset | ImageNet-1K (10% subset) | ~128K train, ~5K val images |
| Pruning Ratio | 50% global unstructured | Target compression level |
| Quantization | INT8 post-training | Standard deployment target |
| Calibration Samples | 1024 | Standard for PTQ |

---

## 3. Experimental Protocol

### 3.1 Prune-First Pipeline

```
1. Load pretrained ResNet-18 (torchvision)
2. Apply global unstructured pruning (torch.nn.utils.prune)
   - Method: L1Unstructured
   - Amount: 0.5 (50% of weights)
3. Fine-tune on ImageNet-10% subset (5 epochs)
4. Apply INT8 post-training quantization
   - Backend: fbgemm
   - Calibration: 1024 samples from train set
5. Evaluate on validation set
```

### 3.2 Quantize-First Pipeline

```
1. Load pretrained ResNet-18 (torchvision)
2. Apply INT8 post-training quantization
   - Backend: fbgemm
   - Calibration: 1024 samples from train set
3. Apply global unstructured pruning
   - Method: L1Unstructured on quantized weights
   - Amount: 0.5 (50% of weights)
4. Fine-tune on ImageNet-10% subset (5 epochs)
5. Evaluate on validation set
```

### 3.3 Evaluation Protocol

For each of 3 seeds × 2 orderings = 6 runs:
1. Record top-1/top-5 accuracy on full validation set (~5K images)
2. Log per-layer sparsity patterns
3. Record inference latency (optional)

---

## 4. Dataset Specification

### 4.1 Dataset Details

| Attribute | Value |
|-----------|-------|
| Name | ImageNet-1K (ILSVRC2012) |
| Type | standard |
| Subset | 10% stratified sample |
| Train Size | ~128,000 images |
| Val Size | ~5,000 images (full val set) |
| Classes | 1000 |
| Resolution | 224×224 (center crop) |

### 4.2 Data Preparation

```python
from torchvision import datasets, transforms
from torch.utils.data import Subset
import numpy as np

transform_val = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

# Full validation set for evaluation
val_dataset = datasets.ImageNet(root='./data', split='val', transform=transform_val)

# 10% stratified train subset
train_dataset = datasets.ImageNet(root='./data', split='train', transform=transform_train)
indices = stratified_subset(train_dataset, fraction=0.1, seed=42)
train_subset = Subset(train_dataset, indices)
```

### 4.3 Data Acquisition

ImageNet-1K requires:
1. Academic access via https://image-net.org/download-images
2. Or use `torchvision.datasets.ImageNet` with local path
3. Minimum 150GB disk space

---

## 5. Model Specification

### 5.1 Base Model

| Attribute | Value |
|-----------|-------|
| Architecture | ResNet-18 |
| Source | `torchvision.models.resnet18(weights='IMAGENET1K_V1')` |
| Parameters | 11.7M |
| Baseline Accuracy | 69.76% top-1, 89.08% top-5 |
| Layers to Analyze | 17 conv layers |

### 5.2 Pruning Configuration

```python
import torch.nn.utils.prune as prune

def apply_global_pruning(model, amount=0.5):
    parameters_to_prune = [
        (module, 'weight') for module in model.modules()
        if isinstance(module, torch.nn.Conv2d)
    ]
    prune.global_unstructured(
        parameters_to_prune,
        pruning_method=prune.L1Unstructured,
        amount=amount
    )
    return model
```

### 5.3 Quantization Configuration

```python
import torch.quantization as quant

def apply_int8_quantization(model, calibration_loader):
    model.eval()
    model.qconfig = quant.get_default_qconfig('fbgemm')
    quant.prepare(model, inplace=True)
    
    # Calibration
    with torch.no_grad():
        for images, _ in calibration_loader:
            model(images)
            if calibration_loader.batch_idx >= 1024 // batch_size:
                break
    
    quant.convert(model, inplace=True)
    return model
```

---

## 6. Success Criteria

### 6.1 Primary Criterion (MUST_WORK Gate)

| Criterion | Threshold | Measurement |
|-----------|-----------|-------------|
| Mean accuracy difference | > 0.5% | |prune_first_acc - quant_first_acc| |
| Statistical significance | p < 0.05 | Paired t-test across 3 seeds |

### 6.2 Early Stop Conditions

| Condition | Action |
|-----------|--------|
| Effect size < 0.5% in both directions | FAIL gate, stop pipeline |
| All seeds show same ordering preference | Strong signal, proceed |

### 6.3 Expected Outcomes

Based on literature (Han et al., Deep Compression):
- Prune-first typically preserves accuracy better when weights have high kurtosis
- Quantize-first may work better for already-sparse layers
- Expected difference: 1-3% accuracy gap at 50% compression

---

## 7. Implementation Requirements

### 7.1 Dependencies

```
torch>=2.0.0
torchvision>=0.15.0
torchmetrics>=1.0.0
numpy>=1.24.0
scipy>=1.10.0  # for statistical tests
```

### 7.2 Hardware Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| GPU | 1× RTX 3080 (10GB) | 1× A100 (40GB) |
| RAM | 32GB | 64GB |
| Storage | 200GB (ImageNet) | 500GB |
| GPU Hours | 2-4 | 4-6 |

### 7.3 Code Structure

```
experiments/
├── h_e1_ordering_effect/
│   ├── config.yaml
│   ├── prune_first.py
│   ├── quantize_first.py
│   ├── evaluate.py
│   ├── analyze_results.py
│   └── requirements.txt
```

---

## 8. Analysis Plan

### 8.1 Statistical Analysis

```python
from scipy import stats

# Paired t-test for ordering effect
prune_first_accs = [acc1, acc2, acc3]  # 3 seeds
quant_first_accs = [acc1, acc2, acc3]  # 3 seeds

t_stat, p_value = stats.ttest_rel(prune_first_accs, quant_first_accs)
effect_size = np.mean(prune_first_accs) - np.mean(quant_first_accs)

gate_passed = (abs(effect_size) > 0.5) and (p_value < 0.05)
```

### 8.2 Per-Layer Analysis

For downstream h-m1 (mechanism hypothesis):
- Record which ordering wins per layer
- Compute pre-compression weight statistics (sparsity, kurtosis)
- Save as structured data for correlation analysis

---

## 9. Risk Mitigation

| Risk | Mitigation |
|------|------------|
| ImageNet access issues | Fall back to CIFAR-100 with note |
| Effect too small | Increase seeds to 5, tighten statistical power |
| Quantization incompatibility | Use dynamic quantization as fallback |
| Memory overflow | Reduce batch size, use gradient checkpointing |

---

## 10. Deliverables

1. **Accuracy table**: 6 runs (3 seeds × 2 orderings) with top-1/top-5
2. **Statistical test results**: t-test p-value, effect size, CI
3. **Per-layer ordering preference**: CSV for h-m1 input
4. **Gate decision**: PASS/FAIL with justification

---

## References

1. Han et al. "Deep Compression" ICLR 2016
2. PyTorch Quantization: https://pytorch.org/docs/stable/quantization.html
3. PyTorch Pruning: https://pytorch.org/tutorials/intermediate/pruning_tutorial.html
4. torchvision QuantizableResNet: https://github.com/pytorch/vision/blob/main/torchvision/models/quantization/resnet.py
