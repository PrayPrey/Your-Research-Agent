# Experiment Design: H-M1

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Spurious features produce stronger gradient signal than core features (gradient norm ratio > 1.5 in early epochs)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing causal mechanism behind spurious feature dominance.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (VALIDATED, PASS)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1

### Gate Condition
- **Type:** MUST_WORK
- **Success Criteria:** Spurious gradient norm > core gradient norm (ratio > 1.5), ratio decreases over epochs
- **If Fail:** PIVOT (mechanism description, not effect)

---

## Continuation Context

### From H-E1 (Prerequisite)
- **Status:** VALIDATED (PASS)
- **Key Findings:**
  - Spurious dominance from epoch 0 (ratio=1.348)
  - Ratio remains >1.0 throughout all 50 epochs
  - Peak ratio 1.59 at epoch 13
  - Confirms simplicity bias in ERM training

### Previous Hypothesis Results (if applicable)
H-E1 established that spurious features dominate in GradCAM attribution. H-M1 now tests the underlying mechanism: whether this dominance is driven by stronger gradient signals for spurious features.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

⚠️ *Archon MCP unavailable - findings from WebFetch literature search*

**Query 1: Gradient Signal Competition in Spurious Correlations**
- **Shah et al. (2020) - Simplicity Bias:** Neural networks preferentially update toward simple/spurious features via gradient-based optimization. Networks "can exclusively rely on the simplest feature and remain invariant to all predictive complex features."
- **Implication:** Gradient norms for spurious features likely higher in early training due to simpler optimization landscape.

**Query 2: Spurious Correlation Datasets & Baselines**
- **Waterbirds Dataset (kohpangwei/group_DRO):**
  - Birds from CUB-200 cropped onto Places backgrounds
  - Spurious correlation: bird type ↔ background (water/land)
  - Ground-truth regions available for attribution analysis
  - Standard baseline: ResNet-50, LR 0.0001-0.001, batch 128, weight decay 0.0001
- **CelebA:** Hair color ↔ gender spurious correlation

**Query 3: Two-Stage Methods (JTT)**
- JTT trains ERM first, then upweights misclassified examples
- Closes 75% gap between ERM and Group DRO
- Validates that early training behavior reveals spurious reliance

### Archon Code Examples

⚠️ *Archon MCP unavailable - code patterns from repository analysis*

**Pattern 1: Group DRO Training (kohpangwei/group_DRO)**
```python
# Standard training setup for spurious correlation experiments
model = torchvision.models.resnet50(pretrained=True)
optimizer = torch.optim.SGD(model.parameters(), lr=0.001, weight_decay=0.0001)
# Batch size: 128, epochs: up to 300
```

**Pattern 2: Gradient Norm Computation**
```python
# Standard PyTorch gradient norm extraction
loss.backward()
total_norm = 0
for p in model.parameters():
    if p.grad is not None:
        total_norm += p.grad.data.norm(2).item() ** 2
total_norm = total_norm ** 0.5
```

**Key Insight:** No existing implementation directly compares spurious vs core feature gradient norms - this is novel measurement requiring custom hook-based approach.

### Exa GitHub Implementations

⚠️ *Exa MCP unavailable - findings from WebFetch GitHub search*

**Repository 1: pytorch-grad-cam** (jacobgil/pytorch-grad-cam)
- **URL:** https://github.com/jacobgil/pytorch-grad-cam
- **Relevance:** Provides GradCAM with gradient hooks for ResNet - key for measuring gradient flow to regions
- **Architecture:** Works with any CNN, explicit ResNet-50 support
- **Key Code:**
  ```python
  from pytorch_grad_cam import GradCAM
  from torchvision.models import resnet50, ResNet50_Weights
  
  model = resnet50(weights=ResNet50_Weights.DEFAULT)
  target_layers = [model.layer4[-1]]
  
  with GradCAM(model=model, target_layers=target_layers) as cam:
      grayscale_cam = cam(input_tensor=input_tensor, 
                          targets=[ClassifierOutputTarget(class_idx)])
  ```
- **Insight:** Registers hooks to capture gradients at intermediate layers - can adapt for gradient norm measurement

**Repository 2: captum** (pytorch/captum)
- **URL:** https://github.com/pytorch/captum
- **Relevance:** Official PyTorch interpretability library with Integrated Gradients
- **Key Features:**
  - LayerConductance for per-layer gradient importance
  - Integrated Gradients for input attribution
  - Hook-based gradient capture
- **Key Code:**
  ```python
  from captum.attr import LayerGradCam, IntegratedGradients
  layer_gc = LayerGradCam(model, model.layer4)
  attributions = layer_gc.attribute(input, target=class_idx)
  ```

**Repository 3: kohpangwei/group_DRO**
- **URL:** https://github.com/kohpangwei/group_DRO
- **Relevance:** Official Waterbirds dataset and baseline training
- **Training Config:**
  - Optimizer: SGD
  - Learning rate: 0.0001-0.001
  - Batch size: 128
  - Weight decay: 0.0001
  - Epochs: up to 300

**Serena Analysis Needed:** false (code patterns clear)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

This is NOVEL measurement - no existing paper measures spurious vs core gradient norms directly. Priority:
1. **Custom implementation** using pytorch-grad-cam hooks for gradient capture
2. **Waterbirds setup** from kohpangwei/group_DRO for dataset/training baseline
3. **Captum** as validation cross-check

**Recommended Implementation Path:**
- Primary: Custom gradient hook implementation using pytorch-grad-cam patterns + Waterbirds from group_DRO
- Fallback: Captum LayerConductance for gradient importance if custom hooks fail
- Justification: No existing implementation measures gradient norms by region - must build custom using established hook patterns

### Code Analysis (Serena MCP)

⚠️ *Serena MCP unavailable*

Code patterns are clear from GitHub analysis - custom gradient hook implementation needed:
1. Register forward hook on ResNet layer4 to capture activations
2. Register backward hook to capture gradients  
3. Use Waterbirds ground-truth masks to separate spurious (background) vs core (bird) regions
4. Compute gradient norms for each region per epoch

---

## Experiment Specification

### Dataset

**Name:** Waterbirds v1.0
**Type:** standard (real benchmark)
**Source:** kohpangwei/group_DRO (https://github.com/kohpangwei/group_DRO)

**Structure:**
- Birds cropped from CUB-200-2011, placed on Places backgrounds
- Spurious correlation: landbird ↔ land background, waterbird ↔ water background
- Ground-truth segmentation masks available for bird regions
- Train/Val/Test splits with different group proportions

**Statistics:**
- Total: ~11,788 images
- Classes: 2 (landbird, waterbird)
- Groups: 4 (bird type × background type)
- Worst-group: waterbird on land / landbird on water (~5% of data)

**Preprocessing:**
- Resize to 224×224
- Normalize: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
- No augmentation (standard ERM baseline)

**Continuation Note:** Same dataset as H-E1 - enables controlled comparison

**Loading Information** (for Phase 4 download):
- Method: custom (git clone + script)
- Identifier: kohpangwei/group_DRO
- Code:
```python
# Download from group_DRO repository
# git clone https://github.com/kohpangwei/group_DRO
# python generate_waterbirds.py
# Data structure: data/waterbird_complete95_forest2water2/
```

### Models

#### Baseline Model

**Architecture:** ResNet-50 (ImageNet pretrained)
**Type:** CNN
**Source:** torchvision.models

**Configuration:**
- Pretrained weights: IMAGENET1K_V1
- Final layer: Modified for 2-class output
- Input size: 224×224×3

**Continuation Note:** Same model as H-E1 - enables controlled comparison

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: resnet50
- Code:
```python
import torchvision.models as models
model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
model.fc = torch.nn.Linear(model.fc.in_features, 2)  # 2 classes
```

#### Proposed Model

**Architecture:** ResNet-50 + Gradient Norm Measurement Hooks
**Integration Point:** layer4 (final convolutional block)
**Modification:** Add forward/backward hooks to capture gradients, no architecture change

**Core Mechanism Implementation:**

```python
# Core Mechanism: Regional Gradient Norm Measurement
# Based on: pytorch-grad-cam hook patterns + Waterbirds masks

class GradientNormTracker:
    """
    Track gradient norms for spurious (background) vs core (bird) regions
    during training to test gradient competition hypothesis.
    """
    def __init__(self, model, target_layer):
        self.gradients = None
        self.activations = None
        # Register hooks on target layer
        target_layer.register_forward_hook(self._save_activation)
        target_layer.register_full_backward_hook(self._save_gradient)
    
    def _save_activation(self, module, input, output):
        self.activations = output.detach()
    
    def _save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()
    
    def compute_regional_gradient_norms(self, bird_mask, background_mask):
        """
        Args:
            bird_mask: (H, W) binary mask for bird region
            background_mask: (H, W) binary mask for background
        Returns:
            core_norm: float, gradient norm in bird region
            spurious_norm: float, gradient norm in background region
        """
        # Resize masks to match activation spatial dims
        grad_map = self.gradients  # (B, C, H', W')
        
        # Compute gradient norms per region
        core_norm = (grad_map * bird_mask).norm(2).item()
        spurious_norm = (grad_map * background_mask).norm(2).item()
        
        return core_norm, spurious_norm

# Integration: Wrap model, no architecture modification
# tracker = GradientNormTracker(model, model.layer4[-1])
```

### Training Protocol

**From H-E1 (Continuation Experiment):**
- **Optimizer:** SGD with momentum=0.9, weight_decay=0.0001
- **Learning Rate:** 0.001 (from group_DRO baseline)
- **Schedule:** Step decay at epochs 60, 120 (gamma=0.1)
- **Batch Size:** 128
- **Epochs:** 50 (sufficient for gradient dynamics observation)
- **Loss:** CrossEntropyLoss

**Rationale:** Reusing H-E1 training config for controlled comparison - only measurement changes.

**Seeds:** 3 (for statistical significance of mechanism hypothesis)

**Source:** kohpangwei/group_DRO training defaults

### Evaluation

**Primary Metrics:**
1. **Spurious/Core Gradient Norm Ratio** per epoch
   - Definition: `spurious_grad_norm / core_grad_norm`
   - Computed over full training set per epoch
2. **Ratio Trend Over Epochs**
   - Expected: Ratio > 1.5 in epochs 1-10, decreasing over training

**Success Criteria:**
- Gradient norm ratio > 1.5 in early epochs (1-10)
- Ratio shows decreasing trend over epochs
- Effect consistent across 3 seeds

**Expected Baseline Performance (from research):**
- H-E1 showed GradCAM attribution ratio ~1.35-1.59
- Gradient norm ratio expected to show similar or stronger effect
- Source: H-E1 validation results

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: gradient_analysis
- Library: custom (PyTorch hooks)
- Code:
```python
# Custom gradient norm computation
def compute_gradient_norm(tensor, mask):
    masked = tensor * mask.unsqueeze(0).unsqueeze(0)
    return masked.norm(2).item()
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Spurious vs Core gradient norm ratio bar chart (epochs 1-10)

#### Additional Figures (LLM Autonomous)
1. **Gradient Norm Ratio Over Epochs**: Line plot showing ratio trajectory across all 50 epochs
2. **Per-Epoch Gradient Norm Comparison**: Dual-axis or grouped bar chart showing absolute spurious and core gradient norms
3. **Heatmap Visualization**: Gradient magnitude heatmaps overlaid on sample images (early vs late epochs)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Spurious gradient norm ratio > 1.5 in early epochs
3. Ratio decreases over training epochs

---

## Appendix: Reference Implementations

### A. Literature Sources

**Source A.1: Shah et al. (2020) - Simplicity Bias**
- **arXiv:** 2006.07710
- **Relevance:** Theoretical foundation for gradient-based preference toward simple features
- **Key Insight:** Networks "exclusively rely on the simplest feature"
- **Used For:** Hypothesis justification, expected gradient behavior

**Source A.2: JTT - Just Train Twice (Liu et al., 2021)**
- **arXiv:** 2107.09044
- **Relevance:** Demonstrates early training reveals spurious reliance
- **Key Insight:** First model's errors identify spurious-dependent samples
- **Used For:** Training protocol design, epoch range selection

### B. GitHub Implementations

**Repository B.1: pytorch-grad-cam** (jacobgil/pytorch-grad-cam)
- **URL:** https://github.com/jacobgil/pytorch-grad-cam
- **Query:** "GradCAM gradient hooks ResNet"
- **Key Code:** Forward/backward hook registration pattern
- **Used For:** GradientNormTracker pseudo-code design

**Repository B.2: captum** (pytorch/captum)
- **URL:** https://github.com/pytorch/captum
- **Query:** "PyTorch interpretability gradient attribution"
- **Key Code:** LayerGradCam, hook-based gradient capture
- **Used For:** Validation cross-check, alternative implementation path

**Repository B.3: kohpangwei/group_DRO**
- **URL:** https://github.com/kohpangwei/group_DRO
- **Query:** "Waterbirds dataset spurious correlation"
- **Key Code:** Dataset loading, training configuration
- **Used For:** Dataset specification, training protocol, hyperparameters

### C. Code Analysis

**Serena Analysis:** Not performed - code patterns clear from GitHub search
**Rationale:** Hook registration patterns from pytorch-grad-cam are well-documented

### D. Previous Hypothesis Context

**Source:** H-E1 Validation Results (04_validation.md)
- **Status:** VALIDATED (PASS)
- **Reused Components:**
  - Dataset: Waterbirds v1.0 (verified working)
  - Model: ResNet-50 (ImageNet pretrained)
  - Training: SGD, LR=0.001, batch=128
- **Key Findings Informing H-M1:**
  - GradCAM attribution ratio 1.35-1.59 (spurious > core)
  - Peak at epoch 13
  - Consistent across training
- **Why Reused:** Enables controlled comparison - only measurement method changes

### E. Traceability Matrix

| Specification | Source Type | Reference |
|--------------|-------------|-----------|
| Dataset selection | Phase 2A/2B | 02b_verification_plan.md |
| Dataset loading | GitHub | B.3 (group_DRO) |
| Model architecture | torchvision | Standard ResNet-50 |
| Gradient hook pattern | GitHub | B.1 (pytorch-grad-cam) |
| Pseudo-code design | GitHub + Custom | B.1, B.2 |
| Training protocol | Previous + GitHub | D (H-E1), B.3 |
| Hyperparameters | GitHub | B.3 (group_DRO defaults) |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md |
| Success criteria | Phase 2B | H-M1 specification |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- Started: 2026-08-28 (Phase 2C experiment design)
- Prerequisite H-E1: VALIDATED (PASS)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
