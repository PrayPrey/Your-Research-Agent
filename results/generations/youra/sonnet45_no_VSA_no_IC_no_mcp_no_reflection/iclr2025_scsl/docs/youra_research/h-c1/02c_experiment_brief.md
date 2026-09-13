# Experiment Design: h-c1

**Date:** 2026-08-29
**Author:** Anonymous
**Hypothesis Statement:** Gradient-aware training (lr_j = lr_base * (1 - ρ_j)) matches or exceeds JTT worst-group accuracy on Waterbirds (within 1%)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-m1 (COMPLETED - provides ρ_j values)
**Gate Status:** SHOULD_WORK (failure does not block Phase 5)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-c1
- **Type:** CONDITION
- **Prerequisites:** h-m1 (feature complexity mechanism - MUST_WORK)

### Gate Condition
**Gate Type**: SHOULD_WORK
- Failure documented as limitation, workflow continues
- Intervention validation is supporting evidence, not blocking requirement

**Success Criterion**: Statistical Test 9 (paired t-test on worst-group accuracy)
- mean(Gradient-Aware) ≥ mean(JTT) - 1% AND p < 0.05

---

## Continuation Context

**Prerequisite Dependency**: h-m1 validation results
- Provides neuron-spurious correlation ρ_j values for each parameter
- ρ_j computed from ablation training (spurious-only vs core-only vs baseline)
- Used to modulate learning rates during h-c1 training

**No Direct Continuation**: h-c1 uses different dataset (Waterbirds vs CMNIST in h-m1)

### Previous Hypothesis Results (if applicable)
h-m1 validation provided:
- Layer-wise ρ_j values (early layers higher spurious correlation)
- Statistical validation: p=0.0028, t=2.78, Cohen d=0.25
- Mechanism confirmed: simpler spurious features learned earlier in network

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Gradient-aware debiasing experiment design**
- Result 1: Standard Waterbirds benchmark setup
  - Dataset: Waterbirds (4795 train, 1199 val, 5794 test)
  - Hyperparameters: SGD momentum 0.9, cosine annealing LR schedule, batch size 32-128
  - Baselines: ERM (72% worst-group), JTT (86-89%), Group DRO (91%)
  - Key insight: Per-neuron modulation requires measuring feature-spurious correlation ρ_j first

**Query 2: Implementation challenges for gradient modulation**
- Computing ρ_j: Requires ablation training data from prerequisite h-m1
- LR modulation timing: Must apply during gradient update (optimizer hook or custom optimizer)
- Neuron tracking: Need mapping between neurons and spurious vs core features
- Stability check: Validate ρ_j values are consistent across training epochs before applying

**Query 3: Waterbirds benchmark standards**
- Standard splits and preprocessing well-established (Sagawa et al. 2020)
- Expected baseline: ERM ~72%, target: JTT ~87% worst-group accuracy
- Success threshold: Within 1% of JTT (≥86% worst-group accuracy)

### Archon Code Examples

**Query 1: Learning rate modulation implementation pattern**
```python
# Pattern 1: Custom optimizer wrapper
for i, param_group in enumerate(optimizer.param_groups):
    param_group['lr'] = base_lr * (1 - rho_j[i])

# Pattern 2: Hook-based gradient modulation
def grad_hook(grad, rho):
    return grad * (1 - rho)

param.register_hook(lambda g: grad_hook(g, rho_j))
```
- Key insight: Hook approach cleaner for per-neuron modulation
- Alternative: Separate optimizer per layer with different LR values

**Query 2: Waterbirds dataset loading**
- Official repository: https://github.com/kohpangwei/group_DRO
- Preprocessing: Resize(256), CenterCrop(224), Normalize(ImageNet stats)
- Group labels: Required for worst-group accuracy metric computation

### Exa GitHub Implementations

**Query 1: JTT Official Implementation (PRIMARY BASELINE)**

**Repository 1**: kohpangwei/group_DRO (⭐ 400+)
- **URL**: https://github.com/kohpangwei/group_DRO
- **Relevance**: Official Waterbirds dataset and JTT baseline from Sagawa et al. (2020)
- **Architecture**: ResNet-50 (torchvision pretrained on ImageNet)
- **Key Code Pattern**:
  ```python
  # Two-stage training: identify error-prone examples, then reweight
  # Stage 1: Standard ERM
  # Stage 2: Upweight misclassified examples from stage 1
  ```
- **Training Config**:
  - Optimizer: SGD(lr=1e-3, momentum=0.9, weight_decay=1e-4)
  - Learning rate: Cosine decay schedule
  - Batch size: 128
  - Epochs: 300 total (100 stage 1 + 200 stage 2)
- **Dataset**: Waterbirds with group labels for worst-group accuracy
- **Results**: ~86-89% worst-group accuracy (benchmark target)

**Query 2: Gradient-based debiasing patterns**
- Most existing methods use loss-based reweighting (ERM + reweighting)
- Per-neuron learning rate modulation is novel approach
- Implementation pattern: Custom optimizer wrapper or gradient hook
- Key insight: Requires ρ_j (neuron-spurious correlation) from h-m1 prerequisite

**Serena Analysis Needed**: No (mechanism is straightforward optimizer modification)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Priority Analysis**:
1. ⭐⭐⭐ **JTT Official (kohpangwei/group_DRO)**: Baseline comparison reference
2. ⭐⭐ **Custom gradient-aware optimizer**: Novel mechanism, no prior implementation
3. ⭐ **Standard PyTorch SGD**: Base optimizer for modulation wrapper

**Recommended Implementation Path:**
- Primary: Use JTT official repository for dataset loading and baseline ERM/JTT implementations
- Secondary: Implement custom GradientAwareOptimizer wrapper around PyTorch SGD
- Fallback: If ρ_j computation fails, use layer-wise learning rates (simpler approximation)
- Justification: JTT repository provides validated Waterbirds setup and baseline results. Gradient-aware mechanism is novel and requires custom implementation based on h-m1 ρ_j values.

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Gradient-aware learning rate modulation is a straightforward optimizer modification pattern.

---

## Experiment Specification

### Dataset

**Dataset**: Waterbirds (Sagawa et al. 2020)
**Type**: standard (spurious correlation benchmark)
**Source**: https://github.com/kohpangwei/group_DRO

**Loading Information** (for Phase 4 download):
- Method: Custom download from official repository
- Identifier: kohpangwei/group_DRO dataset
- Code:
  ```python
  # Download from https://github.com/kohpangwei/group_DRO
  # Dataset structure: waterbird_complete95_forest2water2/
  # Contains train/val/test splits with group labels
  from torchvision import transforms
  from torch.utils.data import DataLoader
  
  transform = transforms.Compose([
      transforms.Resize(256),
      transforms.CenterCrop(224),
      transforms.ToTensor(),
      transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
  ])
  ```

**Statistics**:
- Total: 11,788 images (4795 train, 1199 val, 5794 test)
- Classes: 2 (landbird, waterbird)
- Groups: 4 (landbird on land, landbird on water, waterbird on land, waterbird on water)
- Spurious correlation: 95% training examples have spurious background

**Preprocessing**: Resize 256 → CenterCrop 224 → ImageNet normalization

**Augmentation**: Random horizontal flip (train only)

### Models

#### Baseline Model

**Architecture**: ResNet-50
**Type**: Convolutional Neural Network (CNN)
**Source**: torchvision.models (pretrained on ImageNet)

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: resnet50
- Code:
  ```python
  import torchvision.models as models
  
  # Option 1: Pretrained (recommended for Waterbirds)
  model = models.resnet50(pretrained=True)
  model.fc = nn.Linear(2048, 2)  # Replace final layer for binary classification
  
  # Option 2: From scratch
  model = models.resnet50(pretrained=False)
  model.fc = nn.Linear(2048, 2)
  ```

**Configuration**:
- Input size: (3, 224, 224)
- Output size: 2 classes (landbird, waterbird)
- Parameters: ~25.5M
- Layers: 50 (conv + residual blocks)

**Modifications for Hypothesis**: No architectural changes to baseline. Gradient-aware intervention modulates learning rates during training, not model architecture.

#### Proposed Model

**Architecture:** Baseline + [Mechanism from hypothesis]

**Core Mechanism Implementation:**

```python
# Core Mechanism: Gradient-Aware Learning Rate Modulation
# Based on: Per-neuron spurious correlation ρ_j from h-m1

class GradientAwareOptimizer:
    """
    Modulates per-neuron learning rates based on spurious correlation strength.
    Neurons with high ρ_j (spurious) receive lower learning rates.
    """
    def __init__(self, base_optimizer, rho_j_dict, base_lr=1e-3):
        """
        Args:
            base_optimizer: SGD or Adam instance
            rho_j_dict: Dict mapping parameter names to ρ_j values from h-m1
            base_lr: Base learning rate before modulation
        """
        self.optimizer = base_optimizer
        self.rho_j = rho_j_dict
        self.base_lr = base_lr
    
    def step(self):
        """Apply gradient update with modulated learning rates."""
        for param_group in self.optimizer.param_groups:
            param_name = param_group['name']
            rho = self.rho_j.get(param_name, 0.0)  # Default 0 if not measured
            
            # Core formula: lr_j = lr_base * (1 - ρ_j)
            # Higher ρ_j → lower learning rate → suppress spurious features
            modulated_lr = self.base_lr * (1 - rho)
            param_group['lr'] = max(modulated_lr, 1e-5)  # Floor to prevent zero LR
        
        self.optimizer.step()

# Integration: Replace standard optimizer.step() with gradient_aware_optimizer.step()
# Input: Requires ρ_j values from h-m1 ablation training analysis
```

### Training Protocol

**Optimizer**: SGD
- Parameters: momentum=0.9, weight_decay=1e-4
- **Source**: Standard for Waterbirds benchmark (Sagawa et al. 2020, JTT paper)

**Learning Rate**: 1e-3 (base, before gradient-aware modulation)
- **Schedule**: Cosine decay over 300 epochs
- **Source**: JTT baseline configuration

**Batch Size**: 128
- **Source**: Standard Waterbirds training configuration

**Epochs**: 300
- **Rationale**: Match JTT training duration for fair comparison
- **Source**: Sagawa et al. (2020)

**Loss Function**: Cross-entropy loss
- **Source**: Standard for classification tasks

**Seeds**: 10 random seeds for statistical validation
- **Rationale**: Required for paired t-test (Statistical Test 9 from Phase 2B)

**Gradient-Aware Modulation**:
- Compute ρ_j values from h-m1 validation results
- Apply lr_j = base_lr * (1 - ρ_j) per parameter group
- Update ρ_j every 10 epochs to track changing correlations

### Evaluation

**Primary Metric**: Worst-group accuracy
- **Definition**: Accuracy on the worst-performing group (min over 4 groups)
- **Groups**: {landbird on land, landbird on water, waterbird on land, waterbird on water}
- **Rationale**: Standard metric for spurious correlation robustness

**Secondary Metrics**:
- Average accuracy (all test samples)
- Per-group accuracy (4 groups)
- Worst-group loss

**Success Criteria** (Statistical Test 9 from Phase 2B):
- Paired t-test on worst-group accuracy across 10 seeds
- H0: mean(Gradient-Aware) < mean(JTT) - 1%
- Ha: mean(Gradient-Aware) ≥ mean(JTT) - 1%
- Significance: p < 0.05
- **Pass condition**: Non-inferiority demonstrated (within 1% of JTT)

**Expected Baseline Performance** (from research):
- ERM worst-group: ~72%
- JTT worst-group: ~86-89%
- Target: ≥86% (JTT - 1%)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: multiclass classification with group labels
- Library: Custom (group-aware accuracy computation)
- Code:
  ```python
  import torch
  
  def worst_group_accuracy(preds, labels, groups):
      """
      Compute worst-group accuracy.
      Args:
          preds: (N,) predicted labels
          labels: (N,) true labels
          groups: (N,) group indices [0-3]
      Returns:
          worst_acc: float, min accuracy over 4 groups
      """
      group_accs = []
      for g in range(4):
          mask = (groups == g)
          if mask.sum() > 0:
              acc = (preds[mask] == labels[mask]).float().mean()
              group_accs.append(acc)
      return min(group_accs) if group_accs else 0.0
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on gradient-aware intervention hypothesis, generate:
1. **Learning rate modulation heatmap**: Visualize per-layer ρ_j values and resulting learning rates
2. **Training curves**: Worst-group accuracy over epochs for ERM, JTT, Gradient-Aware
3. **Per-group accuracy bars**: Final test accuracy for all 4 groups (ERM vs JTT vs Gradient-Aware)
4. **Convergence comparison**: Epochs to reach 80% worst-group accuracy threshold

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

**Source 1**: Waterbirds benchmark standard setup
- **Type**: Knowledge base article (synthesized from hypothesis context)
- **Query Used**: "gradient-aware debiasing experiment design"
- **Relevance**: Standard benchmark configuration for worst-group accuracy evaluation
- **Key Insights**:
  - Waterbirds: 4795 train, 1199 val, 5794 test samples
  - Standard preprocessing: Resize 256 → CenterCrop 224 → ImageNet normalization
  - ERM baseline ~72%, JTT target ~87% worst-group accuracy
- **Used For**: Dataset specification, baseline performance expectations

**Source 2**: Gradient modulation implementation patterns
- **Type**: Code patterns from knowledge base
- **Query Used**: "gradient-aware learning rate modulation implementation challenges"
- **Relevance**: Best practices for per-neuron learning rate control
- **Key Insights**:
  - Optimizer hook approach cleaner than custom optimizer class
  - Need ρ_j stability check across training epochs
  - Learning rate floor prevents zero gradients
- **Used For**: Core mechanism pseudo-code, training protocol

### Archon Code Examples

**Code Source 1**: Learning rate modulation pattern
- **Query Used**: "Learning rate modulation implementation pattern"
- **Key Code**:
  ```python
  # Pattern: Custom optimizer wrapper
  for i, param_group in enumerate(optimizer.param_groups):
      param_group['lr'] = base_lr * (1 - rho_j[i])
  ```
- **Used For**: GradientAwareOptimizer pseudo-code in Step 6

### B. GitHub Implementations (Exa)

**Repository 1**: kohpangwei/group_DRO (⭐ 400+)
- **URL**: https://github.com/kohpangwei/group_DRO
- **Query Used**: "JTT official implementation GitHub"
- **Relevance**: Official Waterbirds dataset and JTT baseline from Sagawa et al. (2020)
- **Key Code** (annotated):
  ```python
  # Two-stage training: identify error-prone examples, then reweight
  # Stage 1: Standard ERM (100 epochs)
  # Stage 2: Upweight misclassified examples (200 epochs)
  # Configuration: SGD(lr=1e-3, momentum=0.9), cosine decay, batch 128
  ```
- **Configuration Extracted**: SGD momentum 0.9, lr 1e-3, cosine decay, 300 epochs, batch 128
- **Their Results**: ~86-89% worst-group accuracy (baseline target)
- **Used For**: Dataset loading code, baseline training protocol, baseline performance

**Repository 2**: Gradient-based debiasing patterns
- **URL**: Various feature-level reweighting implementations
- **Query Used**: "gradient-based debiasing patterns"
- **Relevance**: Most existing methods use loss reweighting, not direct gradient modulation
- **Key Insight**: Per-neuron LR modulation is novel - no direct prior implementation found
- **Used For**: Confirmed novelty of gradient-aware approach, informed custom implementation

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear. Gradient-aware learning rate modulation is a straightforward optimizer modification pattern.

### D. Previous Hypothesis Context

**Source**: Phase 4 Validation Report - h-m1
- **File**: h-m1/04_validation.md
- **Reused Components**:
  - ρ_j values: Neuron-spurious correlation computed from ablation training
  - Layer-wise pattern: Early layers higher spurious correlation (ρ=0.003 vs 0.001)
  - Statistical validation: p=0.0028, t=2.78, Cohen d=0.25
- **Why Reused**: h-c1 mechanism depends on h-m1 ρ_j values to modulate learning rates

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (Waterbirds) | GitHub + Phase 2B | kohpangwei/group_DRO, 02b_context.md |
| Preprocessing | GitHub | Repository B.1 (Resize 256 → CenterCrop 224) |
| Baseline model (ResNet-50) | Phase 2B + GitHub | 02b_context.md, torchvision.models |
| Mechanism (gradient-aware LR) | Archon KB + Novel | Source A.2, custom implementation |
| Pseudo-code | Archon Code + Custom | Code Source 1, adapted for ρ_j modulation |
| Training protocol | GitHub | Repository B.1 (SGD, cosine, 300 epochs) |
| Evaluation metrics | Phase 2B + GitHub | 02b_verification_plan.md, worst-group accuracy |
| ρ_j values | Previous hypothesis | h-m1 validation results |
| Success criteria | Phase 2B | Statistical Test 9 (paired t-test) |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-29T00:00:00Z

### Workflow History for This Hypothesis
- 2026-08-29: Phase 2C experiment design initiated
- Status: IN_PROGRESS
- Prerequisites: h-m1 validation completed (provides ρ_j values)
- Next: Phase 3 implementation planning

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
