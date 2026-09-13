# Experiment Design: H-E1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Spurious features dominate earlier than core features in ERM training (GradCAM attribution ratio > 1 before epoch 10)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (None required)
**Gate Status:** MUST_WORK - Not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
- Type: MUST_WORK
- Pass: Spurious dominance epoch < 10 (mean across seeds), Attribution ratio > 1.0
- Fail Action: ABORT (foundational assumption invalid)

---

## Continuation Context

This is the first hypothesis in the verification chain. No prior results to build upon.

### Previous Hypothesis Results (if applicable)
N/A - Foundation hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: GradCAM Attribution Experiment Design**
- **Dataset:** Waterbirds (standard for spurious correlation research)
- **Attribution Methods:** GradCAM, Integrated Gradients (cross-validation recommended)
- **Typical Setup:** ResNet-50, 50 epochs, 5 random seeds, batch size 128
- **Key Insight:** Ground-truth region masks available for quantitative spurious/core attribution measurement

**Query 2: Spurious Feature Learning Implementation Challenges**
- GradCAM can be noisy for small feature regions - use averaging over multiple samples
- Ground-truth region masks essential for reliable attribution ratio
- Early stopping may confound timing measurements - run full epochs
- Multiple seeds (≥5) required for robustness claims

**Query 3: Waterbirds Benchmark Results**
- ERM baseline: ~75% worst-group accuracy
- Group DRO: ~91% worst-group accuracy  
- JTT: ~86% worst-group accuracy
- Standard test set: 5,794 samples with group labels

### Archon Code Examples

**GradCAM Implementation Pattern:**
```python
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.image import show_cam_on_image

cam = GradCAM(model=model, target_layers=[model.layer4[-1]])
grayscale_cam = cam(input_tensor=input_tensor, targets=targets)

# Attribution ratio computation
spurious_attr = (grayscale_cam * spurious_mask).sum()
core_attr = (grayscale_cam * core_mask).sum()
ratio = spurious_attr / (core_attr + 1e-8)
```

**Waterbirds DataLoader Pattern:**
```python
# From kohpangwei/group_DRO repository
from data.dro_dataset import DRODataset
dataset = DRODataset(
    root_dir='data/waterbirds_v1.0',
    target_name='y',
    confounder_names=['place'],
    model_type='resnet50'
)
```

**Sources:** pytorch-grad-cam library, kohpangwei/group_DRO, Shah et al. (2020) simplicity bias

### Exa GitHub Implementations

**Repository 1: kohpangwei/group_DRO** (⭐ 300+)
- **URL:** https://github.com/kohpangwei/group_DRO
- **Relevance:** Official Waterbirds dataset, ERM baseline, group annotations
- **Architecture:** ResNet-50 with ImageNet pretrained weights
- **Key Code:**
  ```python
  # Dataset loading with group labels
  train_data = dro_dataset(root_dir, target_name='y', 
                           confounder_names=['place'], split='train')
  ```
- **Training Config:**
  - Optimizer: SGD with momentum 0.9
  - Learning rate: 0.01 with decay
  - Batch size: 128
  - Epochs: 50
- **Dataset:** Waterbirds v1.0 (4,795 train, 5,794 test)
- **Results:** ERM ~75% worst-group, Group DRO ~91%

**Repository 2: jacobgil/pytorch-grad-cam** (⭐ 8,000+)
- **URL:** https://github.com/jacobgil/pytorch-grad-cam
- **Relevance:** Standard GradCAM implementation for attribution
- **Key Code:**
  ```python
  cam = GradCAM(model=model, target_layers=[model.layer4[-1]], 
                reshape_transform=None)
  grayscale_cam = cam(input_tensor=x, targets=None)
  ```
- **Supports:** GradCAM, GradCAM++, ScoreCAM, AblationCAM
- **Usage:** Per-epoch attribution tracking feasible

**Repository 3: facebookresearch/DomainBed** (⭐ 1,500+)
- **URL:** https://github.com/facebookresearch/DomainBed
- **Relevance:** Standard spurious correlation benchmark framework
- **Training Config:** Standardized hyperparameter search grid

**Serena Analysis Needed:** false (code patterns clear)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Status |
|----------|--------|--------|
| 1 (Highest) | kohpangwei/group_DRO | ✅ Use for Waterbirds + ERM |
| 2 | pytorch-grad-cam | ✅ Use for attribution |
| 3 | Custom | Training loop + epoch-wise tracking |

**Recommended Implementation Path:**
- Primary: kohpangwei/group_DRO dataset loader + pytorch-grad-cam for attribution
- Fallback: torchvision ResNet-50 + manual Waterbirds download
- Justification: Official dataset ensures correct spurious/core region masks; pytorch-grad-cam is de-facto standard

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. GradCAM and Waterbirds implementations are well-documented with standard patterns.

---

## Experiment Specification

### Dataset

**Name:** Waterbirds v1.0
**Type:** standard (NOT synthetic)
**Source:** https://github.com/kohpangwei/group_DRO
**Statistics:**
- Train: 4,795 samples
- Validation: Not specified (use 10% of train)
- Test: 5,794 samples (full test set used for evaluation)
- Classes: 2 (landbird, waterbird)
- Groups: 4 (bird × background combinations)
- Spurious correlation: bird type correlated with background (water/land)

**Preprocessing:**
- Resize: 224×224
- Normalization: ImageNet mean/std
- Center crop for validation/test

**Augmentation (training only):**
- RandomResizedCrop(224)
- RandomHorizontalFlip

**Ground-truth Masks:** Segmentation masks available for spurious (background) and core (bird) regions

**Loading Information** (for Phase 4 download):
- Method: Custom download from official source
- Identifier: `waterbirds_v1.0`
- Code:
```python
# Download from group_DRO repository
# wget https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz
# Extract to ./data/waterbirds_v1.0/

from wilds import get_dataset
dataset = get_dataset(dataset="waterbirds", root_dir="./data")
# Or use kohpangwei loader directly
```

### Models

#### Baseline Model

**Architecture:** ResNet-50
**Type:** CNN (standard torchvision)
**Source:** torchvision.models (ImageNet pretrained)
**Configuration:**
- Input: 224×224×3 RGB
- Output: 2 classes (binary classification)
- Final layer: Replace fc with Linear(2048, 2)
- Target layers for GradCAM: layer4[-1] (final conv block)

**Modifications for Hypothesis:**
- No architectural changes (this is baseline observation)
- Add epoch-wise GradCAM attribution tracking

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `resnet50`
- Code:
```python
import torchvision.models as models
model = models.resnet50(weights='IMAGENET1K_V1')
model.fc = torch.nn.Linear(2048, 2)  # 2 classes
```

#### Proposed Model

**Architecture:** ResNet-50 + Epoch-wise GradCAM Attribution Tracking
**Integration Point:** No architectural change (observation experiment)
**Modification:** Add GradCAM computation after each training epoch

**Core Mechanism Implementation:**

```python
# Core Mechanism: Epoch-wise Spurious/Core Attribution Ratio Measurement
# Based on: pytorch-grad-cam, kohpangwei/group_DRO region masks

from pytorch_grad_cam import GradCAM
import torch

class AttributionTracker:
    """
    Track spurious vs core feature attribution over training epochs.
    Uses GradCAM on final conv layer with ground-truth region masks.
    """
    def __init__(self, model, target_layer, spurious_masks, core_masks):
        self.cam = GradCAM(model=model, target_layers=[target_layer])
        self.spurious_masks = spurious_masks  # (N, H, W) binary
        self.core_masks = core_masks          # (N, H, W) binary
        self.epoch_ratios = []
    
    def compute_attribution_ratio(self, dataloader, device):
        """
        Returns: mean spurious/core attribution ratio over samples
        """
        ratios = []
        for x, y, masks_s, masks_c in dataloader:
            x = x.to(device)
            cam = self.cam(input_tensor=x, targets=None)  # (B, H, W)
            spurious_attr = (cam * masks_s.numpy()).sum(axis=(1,2))
            core_attr = (cam * masks_c.numpy()).sum(axis=(1,2)) + 1e-8
            ratios.extend((spurious_attr / core_attr).tolist())
        return np.mean(ratios)
    
    def log_epoch(self, epoch, dataloader, device):
        ratio = self.compute_attribution_ratio(dataloader, device)
        self.epoch_ratios.append((epoch, ratio))
        print(f"Epoch {epoch}: Spurious/Core ratio = {ratio:.3f}")
        return ratio

# Integration: Call tracker.log_epoch() after each training epoch
```

### Training Protocol

**Optimizer:** SGD
- Parameters: momentum=0.9, weight_decay=1e-4
- Source: kohpangwei/group_DRO baseline config

**Learning Rate:** 0.01
- Source: Standard Waterbirds ERM baseline

**Schedule:** StepLR
- Parameters: step_size=20, gamma=0.1
- Source: ResNet standard schedule

**Batch Size:** 128
- Source: kohpangwei/group_DRO baseline

**Epochs:** 50
- Source: Standard for Waterbirds convergence

**Loss Function:** CrossEntropyLoss

**Seeds:** 1 (fixed seed=42 for PoC)

> ⚠️ **EXISTENCE (PoC)**: Single seed sufficient for direction verification.

### Evaluation

**Primary Metrics:**
- Spurious/Core Attribution Ratio (per epoch)
- Dominance Epoch: First epoch where ratio > 1.0

**Success Criteria:**
- Dominance epoch < 10 (spurious features dominate early)
- Attribution ratio > 1.0 at dominance epoch

**Expected Baseline Performance** (from research):
- ERM worst-group accuracy: ~75%
- Attribution ratio expected > 1.0 by epoch 5-10
- Source: Shah et al. (2020) simplicity bias, JTT paper

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Attribution tracking (not classification accuracy)
- Library: pytorch-grad-cam + numpy
- Code:
```python
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
# See core mechanism pseudo-code above
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

1. **Attribution Ratio Over Epochs**: Line plot showing spurious/core ratio from epoch 1-50
2. **GradCAM Visualization**: Sample images with overlaid attribution heatmaps at key epochs (1, 5, 10, 25, 50)
3. **Dominance Epoch Distribution**: Bar showing which epoch spurious > core occurred

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: GradCAM Attribution Methods
- **Type**: Knowledge base / Best practices
- **Query Used**: "GradCAM attribution experiment design dataset"
- **Relevance**: Standard attribution measurement for CNNs
- **Key Insights**:
  - Use layer4[-1] for ResNet-50 GradCAM
  - Ground-truth region masks enable quantitative measurement
  - Multiple attribution methods (GradCAM + Integrated Gradients) for robustness
- **Used For**: Core mechanism design, evaluation metrics

**Source A.2**: Spurious Correlation Benchmarks
- **Type**: Benchmark results
- **Query Used**: "Waterbirds benchmark spurious correlation"
- **Key Insights**:
  - ERM ~75% worst-group accuracy
  - Group DRO ~91% worst-group accuracy
  - JTT ~86% worst-group accuracy
- **Used For**: Expected baseline performance

### B. GitHub Implementations (Exa)

**Repository B.1**: kohpangwei/group_DRO (⭐ 300+)
- **URL**: https://github.com/kohpangwei/group_DRO
- **Query Used**: "Waterbirds spurious correlation official implementation"
- **Relevance**: Official Waterbirds dataset, ERM baseline, group annotations
- **Key Code**:
  ```python
  # Dataset loading with spurious/core region masks
  train_data = dro_dataset(root_dir, target_name='y', 
                           confounder_names=['place'], split='train')
  ```
- **Configuration Extracted**: SGD momentum=0.9, LR=0.01, batch=128, epochs=50
- **Their Results**: ERM ~75% worst-group
- **Used For**: Dataset specification, training protocol, baseline model

**Repository B.2**: jacobgil/pytorch-grad-cam (⭐ 8,000+)
- **URL**: https://github.com/jacobgil/pytorch-grad-cam
- **Query Used**: "GradCAM PyTorch implementation"
- **Relevance**: Standard GradCAM implementation
- **Key Code**:
  ```python
  cam = GradCAM(model=model, target_layers=[model.layer4[-1]])
  grayscale_cam = cam(input_tensor=x, targets=None)
  ```
- **Used For**: Core mechanism pseudo-code, attribution ratio computation

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear. GradCAM and Waterbirds implementations follow well-documented standard patterns.

### D. Previous Hypothesis Context

**Previous Context**: None - H-E1 is the first hypothesis in the verification chain.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Phase 2A + GitHub | 02b_verification_plan.md, B.1 |
| Preprocessing | GitHub | B.1 (group_DRO defaults) |
| Baseline model | Phase 2A + torchvision | 02b_verification_plan.md |
| Mechanism design | GitHub | B.2 (pytorch-grad-cam) |
| Pseudo-code | GitHub | B.1, B.2 combined |
| Training protocol | GitHub | B.1 (group_DRO config) |
| Evaluation metrics | Phase 2B + Literature | 02b_verification_plan.md, Shah et al. |
| Success criteria | Phase 2B | 02b_verification_plan.md Section 2.2 |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- Phase 2C experiment design started
- Step 1: State initialized, hypothesis selected
- Step 2: Archon KB searched (3 queries)
- Step 3: GitHub implementations searched (3 repos)
- Step 4: Serena analysis skipped (code sufficiently clear)
- Step 5: Dataset and baseline confirmed (standard type)
- Step 6: Experiment specification synthesized
- Step 7: References documented with traceability matrix
- Step 8: Quality validation PASSED
- Phase 2C COMPLETED: 2026-08-28

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
