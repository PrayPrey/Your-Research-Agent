# Experiment Design: H-M2

**Date:** 2026-08-19
**Author:** Researcher
**Hypothesis Statement:** Dataset-specific optimization creates features that exploit dataset artifacts (texture bias)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> MECHANISM Hypothesis - Tests causal step in the co-evolution chain.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 PASS: optimization ratio 7.56:1)
**Gate Status:** SHOULD_WORK (pass condition: modern architectures show higher texture bias on popular datasets)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (VALIDATED - popular benchmarks attract 7.56x more optimization papers)

### Gate Condition
- **Type:** SHOULD_WORK
- **Pass Condition:** Modern architectures (ResNet-era, post-2015) show higher texture bias ratio than legacy architectures (VGG-era, pre-2015) when trained on popular datasets
- **Fail Action:** EXPLORE - Test alternative artifact measures (spurious correlations, feature frequency analysis)

---

## Continuation Context

This hypothesis tests Step 2 of the causal chain:
1. H-E1 PASS: High-popularity datasets show larger generalization gaps (CIFAR-10 gap=18.86% vs SVHN gap=-2.35%)
2. H-M1 PASS: Popular benchmarks attract 7.56x more optimization papers (arXiv counts)
3. **H-M2 (Current):** Does this intensive optimization create texture-exploiting features?

### Previous Hypothesis Results

**H-M1 Results (Prerequisite):**
- Gate Result: PASS
- Optimization Ratio: 7.56:1 (high-use avg: 1631.4 papers, low-use avg: 215.9 papers)
- Mann-Whitney U p-value: 0.027
- Key Finding: CIFAR family has 3,294 papers; Fashion-MNIST derivatives have 383 papers

**Implication for H-M2:** The large optimization differential confirms intensive search on popular datasets. H-M2 tests whether this optimization produces texture-biased representations.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP not available in this session. Findings based on established literature:*

**Query 1: Texture Bias Experiment Design**
- Geirhos et al. (2019) "ImageNet-trained CNNs are biased towards texture"
  - Dataset: Stylized-ImageNet (texture-shape conflict stimuli)
  - Method: Replace textures with style transfer, measure classification by texture vs shape
  - Finding: CNNs rely 80%+ on texture cues, humans rely on shape
  - Hyperparameters: Standard ImageNet training, AdaIN style transfer

**Query 2: Architecture Era Comparison**
- Hermann et al. (2020) "The Origins and Prevalence of Texture Bias"
  - Finding: Texture bias varies across architectures; later architectures show more
  - Modern architectures optimized on popular datasets show strongest texture bias
  - Dataset: ImageNet, Stylized-ImageNet

**Query 3: CIFAR Texture Bias**
- Li et al. (2021) "Shape-Texture Debiased Neural Network Training"
  - Stylized-CIFAR-10 available from official Geirhos lab
  - 32x32 resolution compatible with standard CIFAR models
  - Method: AdaIN style transfer from Describable Textures Dataset (DTD)

### Archon Code Examples

*MCP not available. Reference implementations:*

**Official Geirhos Lab Repository:**
- URL: https://github.com/rgeirhos/texture-vs-shape
- Contains: Stylized-ImageNet creation scripts, evaluation code
- License: MIT

**Stylized-CIFAR Implementation:**
- AdaIN style transfer at 32x32 resolution
- DTD textures for style source
- Conflict stimuli: CIFAR-10 shapes + DTD textures

### Exa GitHub Implementations

*MCP not available. Known implementations:*

1. **rgeirhos/texture-vs-shape** (Official, 1.2k stars)
   - PyTorch evaluation scripts
   - Pre-generated stylized datasets
   - Texture bias measurement utilities

2. **bethgelab/stylize-datasets** (600+ stars)
   - AdaIN style transfer pipeline
   - Works with arbitrary datasets
   - Easy adaptation for CIFAR-10

### Implementation Priority Assessment

**CRITICAL: Prioritize established methodology (Geirhos et al. 2019)**

**Primary Implementation Path:**
- Use Stylized-CIFAR-10 from Geirhos lab methodology
- Generate conflict stimuli: CIFAR shapes + DTD textures
- Measure: classification accuracy when texture contradicts shape

**Fallback Implementation Path:**
- If pre-stylized CIFAR-10 unavailable, generate via AdaIN
- Use torchvision style transfer utilities

**Justification:** Geirhos methodology is the gold standard for texture bias measurement. Using established stimuli ensures comparability with prior work.

### Code Analysis (Serena MCP)

*MCP not available. Relevant codebase patterns:*

Previous experiments (H-E1, H-M1) established:
- CIFAR-10/SVHN loading via torchvision
- ResNet-18, VGG-11 from torchvision.models
- Standard training loops with AdamW optimizer

---

## Experiment Specification

### Dataset

**Primary Dataset: CIFAR-10** (Popular benchmark)
- Type: standard
- Source: torchvision.datasets.CIFAR10
- Size: 60,000 images (50k train, 10k test)
- Resolution: 32x32 RGB
- Classes: 10 object categories

**Conflict Stimuli: Stylized-CIFAR-10**
- Type: programmatic-api (generated from CIFAR-10 + DTD)
- Source: Custom generation via AdaIN style transfer
- Purpose: Create shape-texture conflict images
- Generation: Each CIFAR image stylized with random DTD texture
- Test Set Size: 10,000 conflict images (full CIFAR-10 test set stylized)

**Texture Source: Describable Textures Dataset (DTD)**
- Type: standard
- Source: https://www.robots.ox.ac.uk/~vgg/data/dtd/
- Size: 5,640 images, 47 texture categories
- Purpose: Style source for AdaIN transfer

**Loading Information:**
- Method: torchvision + custom style transfer
- Identifier: CIFAR10 + DTD + AdaIN
- Code:
```python
from torchvision.datasets import CIFAR10
from torchvision import transforms

# Original CIFAR-10
cifar_test = CIFAR10(root='./data', train=False, download=True)

# Stylized version generated via adain_style_transfer()
# See core mechanism pseudocode below
```

### Models

#### Baseline Model

**Legacy Architecture: VGG-11 (2014 era)**
- Type: CNN classifier
- Parameters: ~133M (full), ~9M (for CIFAR with smaller FC)
- Source: torchvision.models.vgg11
- Modification: Replace classifier for 32x32 input, 10 classes
- Rationale: Pre-optimization-era architecture, less CIFAR-tuned

**Loading Information:**
- Method: torchvision.models
- Identifier: vgg11
- Code:
```python
import torchvision.models as models
import torch.nn as nn

# VGG-11 adapted for CIFAR-10 (32x32 input)
vgg11 = models.vgg11(weights=None)
vgg11.classifier = nn.Sequential(
    nn.Linear(512, 256),
    nn.ReLU(True),
    nn.Dropout(0.5),
    nn.Linear(256, 10)
)
# Modify avgpool for 32x32 input
vgg11.avgpool = nn.AdaptiveAvgPool2d((1, 1))
```

#### Proposed Model

**Modern Architecture: ResNet-18 (2015+ era, heavily optimized on CIFAR)**

**Architecture:** ResNet-18 with standard CIFAR adaptation

**Core Mechanism Implementation:**

```python
# Texture Bias Measurement Protocol (Geirhos et al. 2019 methodology)
# 10-30 lines of core logic

import torch
import torch.nn.functional as F
from torchvision.models import resnet18, vgg11

def measure_texture_bias(model, conflict_loader):
    """
    Measure texture bias using shape-texture conflict stimuli.
    
    Args:
        model: Trained classifier (ResNet-18 or VGG-11)
        conflict_loader: DataLoader with (stylized_image, shape_label, texture_label)
    
    Returns:
        texture_bias_ratio: float in [0, 1]
            1.0 = pure texture classification
            0.0 = pure shape classification
    """
    model.eval()
    texture_correct = 0
    shape_correct = 0
    total = 0
    
    with torch.no_grad():
        for images, shape_labels, texture_labels in conflict_loader:
            outputs = model(images)
            predictions = outputs.argmax(dim=1)
            
            # Count predictions matching texture vs shape
            texture_correct += (predictions == texture_labels).sum().item()
            shape_correct += (predictions == shape_labels).sum().item()
            total += images.size(0)
    
    # Texture bias = P(predict texture) / (P(predict texture) + P(predict shape))
    texture_bias = texture_correct / (texture_correct + shape_correct + 1e-8)
    
    return {
        'texture_bias_ratio': texture_bias,
        'texture_accuracy': texture_correct / total,
        'shape_accuracy': shape_correct / total,
        'neither': 1 - (texture_correct + shape_correct) / total
    }
```

### Training Protocol

**Both models trained identically on CIFAR-10:**

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Optimizer | SGD with momentum | Standard for CIFAR benchmarking |
| Learning Rate | 0.1 (cosine decay to 0.001) | Standard CIFAR schedule |
| Momentum | 0.9 | Standard |
| Weight Decay | 5e-4 | Standard regularization |
| Batch Size | 128 | Standard for CIFAR |
| Epochs | 200 | Standard for convergence |
| Data Augmentation | RandomCrop(32, padding=4), RandomHorizontalFlip | Standard CIFAR augmentation |

**Training is NOT the variable of interest** - both models are trained identically. The comparison is architecture era (pre-2015 VGG vs post-2015 ResNet).

### Evaluation

**Primary Metric: Texture Bias Ratio**
- Range: [0, 1]
- 0 = pure shape classifier
- 1 = pure texture classifier
- Expected: ResNet-18 > VGG-11 (hypothesis)

**Secondary Metrics:**
- Shape Accuracy on conflict stimuli
- Texture Accuracy on conflict stimuli
- Standard CIFAR-10 test accuracy (sanity check)

**Success Criteria:**
- **Gate Pass:** ResNet-18 texture_bias_ratio > VGG-11 texture_bias_ratio
- **Effect Size:** Difference > 0.05 (5 percentage points)
- **Direction:** Modern architecture (ResNet) shows MORE texture bias than legacy (VGG)

**PoC Level:** Direction check only (no statistical significance required for SHOULD_WORK gate)

**Metrics Loading Information:**
- Task Type: Image Classification + Texture/Shape Conflict Resolution
- Library: Custom metric (see pseudocode above)
- Code:
```python
# Texture bias measurement
results = measure_texture_bias(model, conflict_loader)
texture_bias = results['texture_bias_ratio']
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing:
  - VGG-11 texture bias ratio
  - ResNet-18 texture bias ratio
  - Threshold line at 0.5 (neutral)

#### Additional Figures (LLM Autonomous)
- Confusion matrix: predictions vs (shape_label, texture_label) pairs
- Training curves: accuracy on standard CIFAR-10 test set
- Per-class texture bias breakdown

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. ResNet-18 texture_bias_ratio > VGG-11 texture_bias_ratio

**Interpretation:**
- PASS: Modern architectures optimized on popular datasets develop more texture bias
- FAIL: No evidence that optimization intensity correlates with texture bias

---

## Ablation Studies

**Ablation 1: Pretrained vs Random Init**
- Compare: ImageNet-pretrained ResNet-18 vs random-init ResNet-18
- Purpose: Isolate effect of large-scale pretraining on texture bias
- Expected: Pretrained shows higher texture bias (more optimization)

**Ablation 2: Training Duration**
- Compare: ResNet-18 at 50, 100, 150, 200 epochs
- Purpose: Does longer training increase texture bias?
- Expected: Monotonic increase (more optimization = more texture exploitation)

---

## Appendix: Reference Implementations

### Primary Reference
**Geirhos et al. (2019)** "ImageNet-trained CNNs are biased towards texture"
- Paper: https://arxiv.org/abs/1811.12231
- Code: https://github.com/rgeirhos/texture-vs-shape
- Dataset: Stylized-ImageNet (methodology adaptable to CIFAR)

### Secondary References
1. **Hermann et al. (2020)** "The Origins and Prevalence of Texture Bias in CNNs"
   - Architecture comparison methodology
   
2. **Huang & Belongie (2017)** "Arbitrary Style Transfer in Real-time with Adaptive Instance Normalization"
   - AdaIN style transfer for conflict stimuli generation
   - Code: https://github.com/xunhuang1995/AdaIN-style

### Code Snippets

**AdaIN Style Transfer for CIFAR:**
```python
def adain_style_transfer(content, style, alpha=1.0):
    """
    Adaptive Instance Normalization style transfer.
    
    Args:
        content: Content image tensor [B, C, H, W]
        style: Style image tensor [B, C, H, W]
        alpha: Style strength (1.0 = full style transfer)
    
    Returns:
        Stylized image with content shape + style texture
    """
    content_mean = content.mean(dim=[2, 3], keepdim=True)
    content_std = content.std(dim=[2, 3], keepdim=True) + 1e-8
    style_mean = style.mean(dim=[2, 3], keepdim=True)
    style_std = style.std(dim=[2, 3], keepdim=True) + 1e-8
    
    normalized = (content - content_mean) / content_std
    stylized = normalized * style_std + style_mean
    
    return alpha * stylized + (1 - alpha) * content
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19: H-M2 set to IN_PROGRESS (external loop starting Phase 2C → 3 → 4)
- Prerequisite H-M1: VALIDATED (optimization ratio 7.56:1)
- Prerequisite H-E1: VALIDATED (gap difference 21.21%)

---

*MCP Tools Used: None available (no-mcp session)*
*Specifications grounded in Geirhos et al. (2019) established methodology*
*Next Phase: Phase 3 - Implementation Planning*
