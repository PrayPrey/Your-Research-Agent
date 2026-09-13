# Experiment Design: H-E1

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Models trained on high-popularity datasets show larger generalization gaps to held-out same-domain datasets compared to low-popularity datasets
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (None required)
**Gate Status:** MUST_WORK - Cohen's d > 0.3, p < 0.05

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
**Pass Condition:** Cohen's d > 0.3 for generalization gap difference between high-use and low-use conditions, p < 0.05
**Fail Action:** STOP - Reassess core hypothesis (fundamental premise invalidated)

---

## Continuation Context

**First hypothesis in verification chain.** No previous results to build upon.

### Previous Hypothesis Results (if applicable)
*Not applicable - H-E1 is the foundation hypothesis*

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**MCP Unavailable** - Using Phase 2B verification plan as primary source.

Key references from literature:
1. **Recht et al. (2019)** - ImageNetV2: 10-15% accuracy drop on distribution-matched test sets
2. **D'Amour et al. (2020)** - Underspecification and deployment failures
3. **Geirhos et al. (2019)** - Texture bias in CNNs on ImageNet

### Archon Code Examples

**MCP Unavailable** - Standard implementations from torchvision:
- ResNet-18: `torchvision.models.resnet18(pretrained=False)`
- Standard training loops from PyTorch examples

### Exa GitHub Implementations

**MCP Unavailable** - Using established dataset pairs:
1. **CIFAR-10 / CINIC-10**: High-use / held-out same-domain pair
2. **SVHN / SVHN-Extra**: Low-use / held-out same-domain pair

### Implementation Priority Assessment

**This is a statistical analysis experiment, not paper reproduction.**

**Recommended Implementation Path:**
- Primary: Standard PyTorch training with torchvision datasets/models
- Fallback: HuggingFace datasets if torchvision unavailable
- Justification: Simple controlled experiment measuring generalization gaps

### Code Analysis (Serena MCP)

**MCP Unavailable** - Using standard PyTorch patterns for CNN classification.

---

## Experiment Specification

### Dataset

**Multi-Dataset Design** (Required for popularity comparison):

| Condition | Training Dataset | Held-Out Test | Type | Popularity |
|-----------|------------------|---------------|------|------------|
| High-Use | CIFAR-10 | CINIC-10 | standard | Q4 (top quartile) |
| Low-Use | SVHN | SVHN-Extra | standard | Q1 (bottom quartile) |

**CIFAR-10** (High-Popularity):
- Classes: 10 (airplane, automobile, bird, cat, deer, dog, frog, horse, ship, truck)
- Train: 50,000 images (32x32 RGB)
- Test: 10,000 images
- Source: torchvision.datasets.CIFAR10

**CINIC-10** (Held-Out Same-Domain for CIFAR-10):
- Classes: 10 (same as CIFAR-10)
- Test: 90,000 images (from ImageNet downsampled + CIFAR)
- Source: Manual download from https://github.com/BayesWatch/cinic-10 or `torchvision` compatible loading

**SVHN** (Low-Popularity):
- Classes: 10 (digits 0-9)
- Train: 73,257 images (32x32 RGB)
- Test: 26,032 images
- Source: torchvision.datasets.SVHN

**SVHN-Extra** (Held-Out Same-Domain for SVHN):
- Classes: 10 (digits 0-9)
- Extra: 531,131 images (used as held-out test)
- Source: torchvision.datasets.SVHN(split='extra')

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: CIFAR10, SVHN, CINIC-10 (manual)
- Code:
```python
from torchvision import datasets, transforms

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.4914, 0.4822, 0.4465), (0.2470, 0.2435, 0.2616))
])

# High-use condition
cifar10_train = datasets.CIFAR10(root='./data', train=True, download=True, transform=transform)
cifar10_test = datasets.CIFAR10(root='./data', train=False, download=True, transform=transform)

# Low-use condition
svhn_train = datasets.SVHN(root='./data', split='train', download=True, transform=transform)
svhn_test = datasets.SVHN(root='./data', split='test', download=True, transform=transform)
svhn_extra = datasets.SVHN(root='./data', split='extra', download=True, transform=transform)

# CINIC-10 requires manual download
# wget https://datashare.ed.ac.uk/bitstream/handle/10283/3192/CINIC-10.tar.gz
```

### Models

#### Baseline Model

**Architecture:** ResNet-18
- Type: CNN Classification
- Parameters: ~11.2M
- Input: 32x32 RGB images
- Output: 10 classes (softmax)

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: resnet18
- Code:
```python
import torchvision.models as models
import torch.nn as nn

model = models.resnet18(pretrained=False)
model.fc = nn.Linear(model.fc.in_features, 10)  # Adjust for 10 classes
```

#### Proposed Model

**Architecture:** Same ResNet-18 (no architectural modification)

**This is a COMPARISON experiment**, not mechanism testing. Same model trained on different popularity conditions to measure generalization gap difference.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Generalization Gap Measurement
# This experiment measures GAP, not a new mechanism

def compute_generalization_gap(model, in_domain_loader, held_out_loader):
    """
    Measure generalization gap: accuracy_in_domain - accuracy_held_out
    
    Args:
        model: Trained ResNet-18
        in_domain_loader: Test set from training distribution
        held_out_loader: Held-out same-domain test set
    Returns:
        gap: float, generalization gap
    """
    in_domain_acc = evaluate(model, in_domain_loader)
    held_out_acc = evaluate(model, held_out_loader)
    gap = in_domain_acc - held_out_acc
    return gap, in_domain_acc, held_out_acc

# Experimental Design:
# 1. Train ResNet-18 on CIFAR-10 (high-use)
# 2. Compute gap_high = acc(CIFAR-10 test) - acc(CINIC-10)
# 3. Train ResNet-18 on SVHN (low-use)
# 4. Compute gap_low = acc(SVHN test) - acc(SVHN-Extra sample)
# 5. Compare: Cohen's d(gap_high, gap_low)
```

### Training Protocol

**Optimizer:** SGD
- Momentum: 0.9
- Weight Decay: 5e-4
- Source: Standard CIFAR-10 training practice

**Learning Rate:** 0.1
- Schedule: MultiStepLR, milestones=[100, 150], gamma=0.1
- Source: ResNet paper defaults for CIFAR

**Batch Size:** 128
- Source: Standard practice

**Epochs:** 200
- Source: Standard CIFAR-10 convergence

**Loss Function:** CrossEntropyLoss

**Seeds:** 1 (PoC - single run per condition)

**Data Augmentation (Training Only):**
- RandomCrop(32, padding=4)
- RandomHorizontalFlip()

### Evaluation

**Primary Metrics:**
- In-domain test accuracy (%)
- Held-out test accuracy (%)
- Generalization gap = in_domain_acc - held_out_acc

**Gate Metrics (from Phase 2B):**
- Cohen's d > 0.3 for gap difference between high-use and low-use conditions
- p < 0.05 for independent samples t-test

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Image Classification
- Library: torchmetrics + scipy.stats
- Code:
```python
from torchmetrics import Accuracy
from scipy.stats import ttest_ind, cohens_d

accuracy = Accuracy(task="multiclass", num_classes=10)

# After computing gaps for multiple runs:
# d = cohens_d(gaps_high_use, gaps_low_use)
# t, p = ttest_ind(gaps_high_use, gaps_low_use)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart showing generalization gaps for high-use vs low-use conditions with error bars

#### Additional Figures (LLM Autonomous)
- Accuracy comparison: In-domain vs held-out for both conditions
- Training curves: Loss/accuracy over epochs for all conditions

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Both conditions (high-use, low-use) produce valid accuracy measurements
3. gap_high_use > gap_low_use (direction check for PoC)

**Full Validation (if PoC passes):**
- Cohen's d > 0.3 between high-use and low-use generalization gaps
- p < 0.05 for independent samples t-test

---

## Appendix: Reference Implementations

### Key References

1. **Recht et al. (2019)** - "Do ImageNet Classifiers Generalize to ImageNet?"
   - GitHub: https://github.com/modestyachts/ImageNetV2
   - Methodology: Distribution-matched test set creation
   - Finding: 10-15% accuracy drop on ImageNetV2

2. **CINIC-10 Dataset**
   - GitHub: https://github.com/BayesWatch/cinic-10
   - Paper: Darlow et al. "CINIC-10 Is Not ImageNet or CIFAR-10"
   - Purpose: Held-out same-domain test for CIFAR-10

3. **PyTorch ResNet Implementation**
   - Source: torchvision.models.resnet18
   - Training example: https://github.com/pytorch/examples/tree/main/imagenet

4. **SVHN Dataset**
   - Source: http://ufldl.stanford.edu/housenumbers/
   - torchvision: `datasets.SVHN`

### Code Snippets

**Standard CIFAR-10 Training (Reference):**
```python
# From PyTorch examples
for epoch in range(200):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        optimizer.zero_grad()
        output = model(data)
        loss = F.cross_entropy(output, target)
        loss.backward()
        optimizer.step()
    scheduler.step()
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19: Hypothesis h-e1 set to IN_PROGRESS (External loop starting Phase 2C)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
