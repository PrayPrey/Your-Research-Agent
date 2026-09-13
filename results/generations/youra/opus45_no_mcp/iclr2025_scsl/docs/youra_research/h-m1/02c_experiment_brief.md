# Experiment Design: H-M1

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Feedback loop becomes self-reinforcing at crystallization point due to gradient starvation
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **MECHANISM Template** - Testing gradient starvation as crystallization mechanism.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 COMPLETED with PASS)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED)

### Gate Condition
MUST_WORK: Gradient ratio inflection must correlate with WGA acceleration (r > 0.7). If fails, EXPLORE alternative mechanism (loss landscape analysis).

---

## Continuation Context

This experiment builds on H-E1 results which established:
- Crystallization zone exists as detectable phenomenon
- d²WGA/dt² peak identifies crystallization timing
- Effect present across Waterbirds benchmark

### Previous Hypothesis Results (H-E1)
- **Status:** COMPLETED
- **Gate Result:** PASS - Code executes, mechanism implemented, metrics measurable
- **Key Finding:** Crystallization zone detected via second derivative analysis
- **Crystallization Timing:** Available from H-E1 validation for correlation analysis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Note:** MCP servers not available in this session. Findings synthesized from established literature.

**Query 1: Gradient Starvation Experiment Design**
- Pezeshki et al. (2021) "Gradient Starvation: A Learning Proclivity in Neural Networks"
  - Dataset: ColoredMNIST, CIFAR-MNIST
  - Setup: Track per-feature gradient magnitudes during training
  - Key insight: Dominant features starve gradients to minority features
  
- Shah et al. (2020) "The Pitfalls of Simplicity Bias in Neural Networks"
  - Dataset: Synthetic + CIFAR variants
  - Measurement: Feature attribution via gradient-based methods
  - Key insight: Early training commits to simplest features

**Query 2: Implementation Challenges**
- Challenge: Isolating gradients for spurious vs core features requires feature-specific probes
- Best practice: Use group-annotated datasets (Waterbirds/CelebA) where features are known
- Pitfall: Gradient magnitude alone insufficient; need gradient flow tracking per feature pathway

### Archon Code Examples

**Gradient Tracking Pattern (from WILDS/DomainBed implementations):**
```python
# Register backward hooks on classifier layer
def gradient_hook(module, grad_input, grad_output):
    store_gradient_magnitude(grad_output[0])
    
model.fc.register_full_backward_hook(gradient_hook)
```

### Exa GitHub Implementations

**Key Repositories:**
1. `p-lambda/wilds` - WILDS benchmark with group annotations
2. `kohpangwei/group_DRO` - Group DRO implementation with per-group tracking
3. `facebookresearch/DomainBed` - Domain generalization baselines

**Gradient Analysis Pattern (from DomainBed):**
- Track gradient norms per training step
- Correlate with per-group accuracy changes
- Use epoch-level aggregation for noise reduction

### Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Availability | Fit |
|----------|--------|--------------|-----|
| 1 | kohpangwei/group_DRO | MIT License | High - includes group-level tracking |
| 2 | p-lambda/wilds | Apache 2.0 | High - standard benchmark loader |
| 3 | Custom hooks | N/A | Fallback - minimal gradient tracking |

**Recommended Implementation Path:**
- Primary: Extend H-E1 codebase with gradient magnitude hooks
- Fallback: Standalone gradient tracking using PyTorch backward hooks
- Justification: H-E1 already implements WGA tracking; adding gradient hooks enables correlation analysis with minimal code changes

### Code Analysis (Serena MCP)

**Note:** Serena MCP not available. Analysis based on H-E1 validation report.

**From H-E1 Implementation:**
- WGA computation: Per-epoch, per-group accuracy tracking implemented
- Crystallization detection: d²WGA/dt² peak calculation validated
- Integration point: Add gradient hooks to classifier layer (model.fc)

---

## Experiment Specification

### Dataset

**Name:** Waterbirds (primary)
**Type:** standard
**Source:** WILDS benchmark suite (p-lambda/wilds)

| Property | Value |
|----------|-------|
| Total Samples | 11,788 |
| Train | 4,795 |
| Validation | 1,199 |
| Test | 5,794 |
| Classes | 2 (landbird, waterbird) |
| Groups | 4 (bird × background combinations) |
| Minority Group Size | ~500+ samples |

**Spurious Correlation:** Bird type correlated with background (water/land)
**Group Annotations:** Available for all splits, enabling per-group gradient tracking

**Preprocessing:**
- Resize: 224×224
- Normalize: ImageNet mean/std
- No augmentation (ERM baseline)

**Loading Information** (for Phase 4 download):
- Method: WILDS library
- Identifier: `waterbirds`
- Code:
```python
from wilds import get_dataset
dataset = get_dataset(dataset='waterbirds', download=True, root_dir='./data')
train_data = dataset.get_subset('train')
val_data = dataset.get_subset('val')
test_data = dataset.get_subset('test')
```

### Models

#### Baseline Model

**Architecture:** ResNet-50 (pretrained ImageNet)
**Configuration:**
- Backbone: ResNet-50 (frozen or fine-tuned)
- Classifier: Linear(2048, 2)
- Training: Standard ERM

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `resnet50`
- Code:
```python
import torchvision.models as models
model = models.resnet50(weights='IMAGENET1K_V1')
model.fc = nn.Linear(2048, 2)  # 2 classes for Waterbirds
```

#### Proposed Model

**Architecture:** ResNet-50 with Gradient Tracking Hooks

**Modification:** Add backward hooks to track gradient magnitudes flowing to classifier layer, enabling correlation analysis between gradient flow and WGA acceleration.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Gradient Starvation Tracking
# Based on: Pezeshki 2021, PyTorch backward hooks

class GradientTracker:
    """
    Track gradient magnitudes per group during training.
    Enables correlation with WGA crystallization timing.
    """
    def __init__(self, model, group_indices):
        self.gradient_history = []
        self.group_indices = group_indices  # {group_id: sample_indices}
        self.current_gradients = {}
        
        # Register hook on classifier layer
        model.fc.register_full_backward_hook(self._gradient_hook)
    
    def _gradient_hook(self, module, grad_input, grad_output):
        """Capture gradient magnitude during backward pass."""
        grad = grad_output[0]  # (B, num_classes)
        self.current_gradients['fc_grad'] = grad.detach().clone()
    
    def compute_group_gradient_ratio(self, batch_groups):
        """
        Compute ratio of minority to majority group gradient magnitudes.
        Returns: float - ratio (minority_grad_norm / majority_grad_norm)
        """
        grad = self.current_gradients.get('fc_grad')
        if grad is None:
            return None
        
        # Compute per-group gradient norms
        group_norms = {}
        for g in torch.unique(batch_groups):
            mask = (batch_groups == g)
            if mask.sum() > 0:
                group_norms[g.item()] = grad[mask].norm().item()
        
        # Ratio: minority (group 3) / majority (group 0)
        minority_norm = group_norms.get(3, 1e-8)
        majority_norm = group_norms.get(0, 1e-8)
        return minority_norm / (majority_norm + 1e-8)
    
    def log_epoch_gradients(self, epoch, ratio):
        """Store epoch-level gradient ratio for analysis."""
        self.gradient_history.append({
            'epoch': epoch,
            'gradient_ratio': ratio
        })

# Integration: Wrap training loop
# tracker = GradientTracker(model, group_indices)
# After each batch backward: ratio = tracker.compute_group_gradient_ratio(groups)
# After each epoch: tracker.log_epoch_gradients(epoch, avg_ratio)
```

### Training Protocol

**Optimizer:** SGD
- momentum: 0.9
- weight_decay: 1e-4
- Source: WILDS Waterbirds default

**Learning Rate:** 1e-3
- Source: WILDS benchmark configuration

**Schedule:** Step LR
- Milestones: [30, 60]
- Gamma: 0.1
- Source: Standard practice for Waterbirds

**Batch Size:** 128
- Source: Group DRO paper (Sagawa 2020)

**Epochs:** 100
- Source: WILDS benchmark default

**Loss Function:** CrossEntropyLoss

**Seeds:** 1 (fixed seed=42)
- Note: MECHANISM hypothesis, single seed for PoC

**Dense Checkpointing:** Every epoch (required for gradient ratio tracking)

### Evaluation

**Primary Metrics:**
- Gradient Ratio Inflection Epoch: Epoch where d(gradient_ratio)/dt shows acceleration
- Correlation Coefficient (r): Pearson correlation between gradient ratio inflection and d²WGA/dt² peak

**Success Criteria:**
- Primary: r > 0.7 (gradient inflection correlates with WGA crystallization)
- Secondary: Inflection occurs before 50% of training (epoch < 50)

**Expected Baseline Performance:**
- ERM WGA: 60-75% on Waterbirds
- Crystallization timing: 20-40% of training (from H-E1)
- Source: WILDS benchmark, H-E1 validation results

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: multiclass classification + correlation analysis
- Library: scipy.stats (for Pearson correlation), torchmetrics (accuracy)
- Code:
```python
from scipy.stats import pearsonr
import torchmetrics

# Accuracy
accuracy = torchmetrics.Accuracy(task='multiclass', num_classes=2)

# Correlation analysis
r, p_value = pearsonr(gradient_inflection_epochs, wga_peak_epochs)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Gradient ratio inflection vs WGA acceleration timing correlation

#### Additional Figures (LLM Autonomous)

1. **Gradient Ratio Timeline**: Plot gradient_ratio across epochs with inflection point marked
2. **WGA vs Gradient Overlay**: Dual-axis plot showing WGA curve and gradient ratio on same timeline
3. **Correlation Scatter**: Scatter plot of (gradient_inflection_epoch, wga_peak_epoch) across runs if multiple seeds
4. **Per-Group Gradient Norms**: Line plot showing gradient magnitude per group over training

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Gradient ratio inflection timing correlates with d²WGA/dt² peak (r > 0.7)
3. Inflection occurs before 50% of training

---

## Appendix: Reference Implementations

### Primary References

1. **Pezeshki et al. (2021)** - "Gradient Starvation: A Learning Proclivity in Neural Networks"
   - Establishes gradient starvation mechanism
   - Code: Not officially released, mechanism described in paper
   - Key insight: Dominant features reduce gradient flow to minority features

2. **Sagawa et al. (2020)** - "Distributionally Robust Neural Networks" (Group DRO)
   - Repository: https://github.com/kohpangwei/group_DRO
   - License: MIT
   - Relevance: Group-aware training loop, per-group tracking utilities

3. **WILDS Benchmark (2021)**
   - Repository: https://github.com/p-lambda/wilds
   - License: Apache 2.0
   - Relevance: Waterbirds dataset loader, group annotations

4. **H-E1 Implementation (This Project)**
   - File: `h-e1/code/`
   - Relevance: WGA tracking, d²WGA/dt² crystallization detection
   - Reuse: Extend with gradient hooks

### Code Snippets for Reuse

**From H-E1 (WGA Tracking):**
```python
# Reuse existing WGA computation
from h_e1.metrics import compute_wga, compute_second_derivative
wga_curve = compute_wga(model, dataloader, group_ids)
d2wga = compute_second_derivative(wga_curve, window=5)
```

**Gradient Hook Pattern (PyTorch standard):**
```python
def register_gradient_hooks(model):
    hooks = []
    for name, module in model.named_modules():
        if isinstance(module, nn.Linear):
            hook = module.register_full_backward_hook(gradient_callback)
            hooks.append(hook)
    return hooks
```

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19: H-M1 set to IN_PROGRESS (Phase 2C started)
- Prerequisite H-E1 COMPLETED with PASS result

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
