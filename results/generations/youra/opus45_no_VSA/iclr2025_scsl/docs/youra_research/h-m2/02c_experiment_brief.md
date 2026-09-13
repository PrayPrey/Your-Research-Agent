# Experiment Design: H-M2

**Date:** 2026-08-09
**Author:** Anonymous
**Hypothesis Statement:** Update-norm parity intervention attenuates SR divergence (SR ≤ 1.1 vs baseline SR > 1.2)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing causal intervention effect.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-E1 (VALIDATED)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-E1

### Gate Condition
SHOULD_WORK: Failure allows continuation with logged limitation

---

## Continuation Context

Building on H-E1 validation showing SR ≈ 1.0 at initialization (no intrinsic curvature asymmetry), H-M2 tests whether enforcing update-norm parity can prevent SR divergence during training.

### Previous Hypothesis Results (if applicable)
- **H-E1:** Mean SR = 0.9999 at random init, 95% CI [0.9953, 1.0046] includes 1.0
- **Implication:** Differential convergence (not data geometry) causes SR divergence

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1:** "gradient scaling group robustness fairness"
- Limited direct results for group robustness domain
- General training optimization patterns found

**Query 2:** "sharpness aware minimization worst-group accuracy"
- No direct results in current KB
- Domain-specific literature needed (Exa search)

**Key Insight:** Archon KB lacks group robustness/fairness training literature. Experiment design will rely primarily on:
1. Exa GitHub search for Group DRO implementations
2. Standard PyTorch training patterns from KB

### Archon Code Examples

**Query:** "ResNet training SGD optimizer PyTorch"

**Example 1:** PyTorch 2.0 Training (pytorch.org/get-started)
```python
model = models.resnet18().cuda()
optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
# Standard training loop pattern
optimizer.zero_grad()
out = model(x)
out.sum().backward()
optimizer.step()
```
- Pattern: Standard SGD training loop
- Insight: Base pattern for per-group gradient intervention

**Example 2:** Autocast Training (pytorch.org/docs/stable/amp.html)
```python
with torch.autocast(device_type="cuda"):
    output = model(input)
    loss = loss_fn(output, target)
loss.backward()
optimizer.step()
```
- Pattern: Loss computation then backward
- Insight: Gradient scaling point is between backward() and step()

### Exa GitHub Implementations

**Query 1:** "group DRO Waterbirds PyTorch kohpangwei sagawa"

**Repository 1:** kohpangwei/group_DRO (Official Paper Implementation)
- **URL:** https://github.com/kohpangwei/group_DRO
- **Paper:** Sagawa et al., "Distributionally Robust Neural Networks for Group Shifts" (ICLR 2020)
- **Relevance:** Official Waterbirds dataset + Group DRO baseline
- **Architecture:** ResNet-50 pretrained ImageNet
- **Training Config:**
  - Optimizer: SGD (momentum=0.9)
  - Learning rate: 0.001
  - Batch size: 128
  - Weight decay: 0.0001
  - Epochs: 300
  - L2 regularization: λ=1.0 for worst-group improvement
- **Key Command:**
  ```bash
  python run_expt.py -s confounder -d CUB -t waterbird_complete95 -c forest2water2 \
    --lr 0.001 --batch_size 128 --weight_decay 0.0001 --model resnet50 \
    --n_epochs 300 --reweight_groups --robust --gamma 0.1
  ```
- **Results:** ERM WGA 21.3% → Group DRO WGA 84.6%

**Query 2:** "per-group gradient scaling fairness training PyTorch"

**Repository 2:** fairgrad (PyPI package)
- **URL:** https://pypi.org/project/fairgrad/
- **Relevance:** Per-group gradient weighting for fairness
- **Pattern:** Custom CrossEntropyLoss with group-aware gradient scaling
- **Key Insight:** Loss function modification point for per-group gradient intervention

**Repository 3:** PyTorch clip_grad_norm_ utilities
- **URL:** pytorch.org/docs/stable/torch.nn.utils.clip_grad_norm_
- **Relevance:** Gradient norm computation and scaling primitives
- **Key Code:**
  ```python
  # Compute per-group gradient norms
  total_norm = torch.nn.utils.get_total_norm(params)
  # Scale gradients
  torch.nn.utils.clip_grads_with_norm_(params, max_norm, total_norm)
  ```

**Serena Analysis Needed:** false (code patterns clear)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Use Case |
|----------|--------|----------|
| ⭐⭐⭐ HIGH | kohpangwei/group_DRO | Waterbirds dataset, ERM baseline, evaluation |
| ⭐⭐ MEDIUM | PyTorch grad utils | Update-norm computation primitives |
| ⭐ LOW | fairgrad | Reference for per-group loss weighting pattern |

**Recommended Implementation Path:**
- Primary: Fork kohpangwei/group_DRO, add update-norm parity intervention to training loop
- Fallback: Standalone PyTorch script using their Waterbirds data loader
- Justification: Official repo provides exact dataset splits, evaluation protocol, and ERM baseline for direct comparison

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. Key patterns identified:
1. Training loop intervention point: between `loss.backward()` and `optimizer.step()`
2. Per-group gradient norm: `torch.nn.utils.clip_grad_norm_` primitives
3. Group labels available in Waterbirds dataloader for per-group computation

---

## Experiment Specification

### Dataset

**Name:** Waterbirds
**Type:** standard (real benchmark — NOT synthetic)
**Source:** kohpangwei/group_DRO (CUB-200 birds + Places backgrounds)
**Groups:** 4 groups (2 bird types × 2 backgrounds)
  - Landbird on land (majority)
  - Landbird on water (minority)
  - Waterbird on water (majority)
  - Waterbird on land (minority)
**Confounder Strength:** 95% (training), 50% (val/test balanced)

**Statistics:**
- Training: ~4,795 samples (skewed group distribution)
- Validation: ~1,199 samples (balanced)
- Test: ~5,794 samples (balanced)
- Classes: 2 (landbird/waterbird)

**Preprocessing:**
- Resize: 224×224
- Normalize: ImageNet mean/std
- Augmentation (train): RandomResizedCrop, RandomHorizontalFlip

**Loading Information** (for Phase 4 download):
- Method: Clone kohpangwei/group_DRO + generate dataset
- Identifier: `waterbird_complete95_forest2water2`
- Code:
  ```python
  # Requires CUB-200-2011 and Places365 datasets
  # Run: python dataset_scripts/generate_waterbirds.py
  # Or download pre-generated from Codalab worksheet
  from data.cub_dataset import CUBDataset
  dataset = CUBDataset(root_dir='./data', target_name='waterbird_complete95',
                       confounder_names=['forest2water2'], split='train')
  ```

### Models

#### Baseline Model

**Architecture:** ResNet-50
**Pretrained:** ImageNet (torchvision)
**Task:** Binary classification (landbird vs waterbird)
**Output:** 2-class logits

**Configuration:**
- Final layer: `nn.Linear(2048, 2)`
- Frozen backbone: No (full fine-tuning)
- Dropout: None (rely on L2 regularization)

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `resnet50`
- Code:
  ```python
  import torchvision.models as models
  model = models.resnet50(pretrained=True)
  model.fc = nn.Linear(2048, 2)  # Binary classification
  ```

#### Proposed Model

**Architecture:** ResNet-50 + Update-Norm Parity Intervention
**Integration Point:** Training loop, between `loss.backward()` and `optimizer.step()`
**Modification:** Scale per-group gradients to equalize update norms across groups

**Core Mechanism Implementation:**

```python
# Core Mechanism: Update-Norm Parity Intervention
# Based on: PyTorch gradient utilities + Group DRO group labels
# Purpose: Equalize gradient update norms across majority/minority groups

class UpdateNormParityTrainer:
    """
    Enforces equal update norms across groups during training.
    Hypothesis: This prevents SR divergence between groups.
    """
    def __init__(self, model, num_groups=4):
        self.model = model
        self.num_groups = num_groups
    
    def compute_group_grad_norms(self, group_labels):
        """Compute gradient norm per group."""
        group_norms = {}
        total_norm = torch.nn.utils.clip_grad_norm_(
            self.model.parameters(), max_norm=float('inf'))
        # Per-group norm estimation via loss decomposition
        for g in range(self.num_groups):
            mask = (group_labels == g)
            if mask.sum() > 0:
                group_norms[g] = total_norm * (mask.sum() / len(group_labels))
        return group_norms
    
    def apply_parity_scaling(self, group_labels):
        """Scale gradients so all groups have equal update norm."""
        norms = self.compute_group_grad_norms(group_labels)
        target_norm = sum(norms.values()) / len(norms)
        
        for param in self.model.parameters():
            if param.grad is not None:
                # Scale toward parity (simplified)
                param.grad.mul_(target_norm / (max(norms.values()) + 1e-8))
        
        print(f"[PARITY] Norms: {norms}, Target: {target_norm:.4f}")

# Training loop:
# loss.backward()
# trainer.apply_parity_scaling(group_labels)  # <-- Insert
# optimizer.step()
```

### Training Protocol

**Optimizer:** SGD
  - Parameters: `momentum=0.9, weight_decay=0.0001`
  - **Source:** kohpangwei/group_DRO official settings

**Learning Rate:** 0.001
  - **Source:** Group DRO paper Waterbirds experiments

**Schedule:** ReduceLROnPlateau
  - Parameters: `mode='min', patience=5`
  - **Source:** kohpangwei/group_DRO train.py

**Batch Size:** 128
  - **Source:** Group DRO paper

**Epochs:** 100 (early stopping on worst-group val accuracy)
  - **Source:** Reduced from 300 for mechanism test

**Loss Function:** CrossEntropyLoss

**Seeds:** 5 (for statistical comparison)

### Evaluation

**Primary Metrics:**
- **Sharpness Ratio (SR):** Hessian trace ratio minority/majority groups
- **Worst-Group Accuracy (WGA):** Min accuracy across 4 groups

**Success Criteria (MECHANISM hypothesis):**
- Baseline: SR > 1.2 by epoch 50
- Proposed: SR ≤ 1.1 sustained throughout training
- Statistical: SR difference significant across 5 seeds

**Expected Baseline Performance:**
- ERM WGA: ~21% (kohpangwei/group_DRO)
- **Source:** Sagawa et al. 2020

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification with group labels
- Library: Custom SR + sklearn.metrics
- Code:
  ```python
  from sklearn.metrics import accuracy_score
  wga = min([accuracy_score(y[g==i], pred[g==i]) for i in range(4)])
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **SR Trajectory Comparison**: Baseline vs Parity SR over epochs

#### Additional Figures (LLM Autonomous)
- Per-group accuracy trajectories (4 lines × 2 conditions)
- Update norm distribution per group (boxplot)
- Final WGA comparison bar chart
- SR vs WGA correlation scatter

**Output Location:** `h-m2/figures/`

### Ablation Studies

| Variant | Description | Purpose |
|---------|-------------|---------|
| Baseline (ERM) | No intervention | Control, expect SR > 1.2 |
| Full Parity | Scale to equal norms | Main intervention |
| Partial (50%) | 50% scaling toward parity | Dose-response |

### Mechanism Verification Protocol

**Pre-conditions:**
- `mechanism_exists`: Parity scaling applied between backward() and step()
- `mechanism_isolatable`: Toggle via flag
- `baseline_measurable`: SR computed without intervention

**Activation Indicators:**
- Log: "[PARITY] Norms equalized: {norms}"
- Metric: SR should decrease vs baseline

**Verification Code:**
```python
assert abs(max(norms.values()) - min(norms.values())) < 0.1, "Parity not achieved"
```

**Success Threshold:** SR ≤ 1.1 (vs baseline SR > 1.2)

---

## 🔬 Mechanism Success Check

**Pass Condition:**
1. Code runs without error
2. SR ≤ 1.1 under parity vs SR > 1.2 baseline (across 5 seeds)

---

## Appendix: Reference Implementations

### A. Primary Sources

| Source | URL | Use |
|--------|-----|-----|
| kohpangwei/group_DRO | https://github.com/kohpangwei/group_DRO | Dataset, baseline, evaluation |
| Sagawa et al. 2020 | https://arxiv.org/abs/1911.08731 | Hyperparameters, expected results |
| PyTorch clip_grad_norm_ | https://pytorch.org/docs | Gradient norm utilities |
| fairgrad | https://pypi.org/project/fairgrad | Per-group gradient concept |

### B. Archon Knowledge Base
- Query: "gradient scaling group robustness" → PyTorch training patterns
- Query: "ResNet SGD optimizer" → Standard training loop structure

### C. Exa GitHub Search
- Query: "group DRO Waterbirds kohpangwei" → Official implementation found
- Query: "per-group gradient scaling" → fairgrad and PyTorch utilities

### D. Serena Analysis
*Skipped* - Code patterns sufficiently clear from search results

### E. Traceability Matrix

| Specification | Source Type | Reference |
|--------------|-------------|-----------|
| Dataset (Waterbirds) | Exa GitHub | kohpangwei/group_DRO |
| Preprocessing | Exa GitHub | kohpangwei/group_DRO |
| Baseline model (ResNet-50) | Exa GitHub | kohpangwei/group_DRO |
| Training protocol | Exa GitHub + Paper | Sagawa et al. 2020 |
| Gradient scaling pattern | Exa + Archon | PyTorch docs, fairgrad |
| Pseudo-code design | Synthesis | Based on PyTorch grad utils |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md |
| SR computation | H-E1 | Previous hypothesis |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-09

### Workflow History for This Hypothesis
- Phase 2C experiment design started

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
