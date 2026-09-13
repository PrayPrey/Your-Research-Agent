# Experiment Design: H-E1

**Date:** 2026-08-29
**Author:** Anonymous
**Hypothesis Statement:** Under standard supervised learning with spurious correlations, if we accumulate early training gradients into subspace S via incremental SVD, then S primarily captures spurious feature directions, because simplicity bias causes spurious features to dominate early learning.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK (if fail: STOP pipeline)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
- **Type:** MUST_WORK
- **Success Criteria:** S alignment with spurious features > 70% at early epochs
- **Secondary:** S alignment with core features < 30% at early epochs
- **If Fail:** STOP - core assumption invalid

---

## Continuation Context

**Previous Context:** None - this is the first hypothesis in the verification chain.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable in this session. Using established literature:*

**Source 1: Simplicity Bias Literature**
- Shah et al. (2020): "The Pitfalls of Simplicity Bias in Neural Networks"
- Key insight: Networks learn simpler (spurious) features before complex (core) features
- Relevance: Theoretical foundation for gradient subspace capturing spurious directions

**Source 2: Spurious Correlation Benchmarks**
- Sagawa et al. (2020): "Distributionally Robust Neural Networks"
- Dataset: Waterbirds with 95% spurious correlation
- Baseline ERM: ~60% worst-group accuracy

### Archon Code Examples

*MCP unavailable. Using known implementations:*

**Code Pattern: Gradient Logging**
```python
# Standard gradient accumulation pattern
for epoch in range(num_epochs):
    for batch in dataloader:
        loss = model(batch)
        loss.backward()
        if epoch < early_cutoff:
            accumulated_grads.append(get_gradients(model))
```

### Exa GitHub Implementations

*MCP unavailable. Using established repositories:*

**Repository 1**: kohpangwei/group_DRO (⭐ 500+)
- **URL**: https://github.com/kohpangwei/group_DRO
- **Relevance**: Official Waterbirds dataset + Group DRO baseline
- **Dataset**: Waterbirds preprocessing, transforms, splits
- **Training Config**: ResNet-50, SGD, lr=1e-3, batch=128

**Repository 2**: PolinaKirichenko/deep_feature_reweighting (⭐ 200+)
- **URL**: https://github.com/PolinaKirichenko/deep_feature_reweighting
- **Relevance**: DFR implementation, feature analysis methods
- **Key insight**: Last-layer features separate spurious/core after training

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

- Author implementations: kohpangwei/group_DRO for Waterbirds
- Standard ResNet-50 from torchvision

**Recommended Implementation Path:**
- Primary: torchvision ResNet-50 + Waterbirds from group_DRO repo
- Fallback: timm ResNet-50 if torchvision issues
- Justification: Most widely used and validated combination for spurious correlation research

### Code Analysis (Serena MCP)

*Serena unavailable. Code complexity is manageable without deep analysis.*

Key pattern identified from literature:
- Accumulate gradients during early epochs (1-10)
- Apply incremental SVD to gradient matrix
- Measure alignment with spurious (background) vs core (bird) feature directions

---

## Experiment Specification

### Dataset

**Dataset**: Waterbirds
**Type**: standard
**Source**: https://github.com/kohpangwei/group_DRO

**Statistics**:
- Train: 4,795 samples
- Validation: 1,199 samples  
- Test: 5,794 samples
- Classes: 2 (landbird, waterbird)
- Groups: 4 (bird × background combinations)
- Spurious correlation: 95% (waterbird with water, landbird with land)

**Preprocessing**:
- Resize to 224×224
- Normalize: ImageNet mean/std
- Train augmentation: RandomResizedCrop, RandomHorizontalFlip

**Loading Information** (for Phase 4 download):
- Method: Custom (from group_DRO repo)
- Identifier: `waterbird_complete95_forest2water2`
- Code:
```python
from wilds import get_dataset
dataset = get_dataset(dataset='waterbirds', download=True)
# Or manual download from group_DRO repo
```

### Models

#### Baseline Model

**Architecture**: ResNet-50
**Type**: CNN classifier
**Source**: torchvision pretrained (ImageNet)

**Configuration**:
- Input: (B, 3, 224, 224)
- Output: (B, 2) class logits
- Features: 2048-dim from avgpool
- Modification: Replace final FC with Linear(2048, 2)

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `resnet50`
- Code:
```python
import torchvision.models as models
model = models.resnet50(pretrained=True)
model.fc = nn.Linear(2048, 2)
```

#### Proposed Model

**Architecture:** Baseline + Gradient Subspace Accumulation

**Core Mechanism Implementation:**

```python
# Core Mechanism: Gradient Subspace Accumulation via Incremental SVD
# Purpose: Capture early gradient directions into subspace S

class GradientSubspaceAccumulator:
    """
    Accumulates gradients during early training epochs and computes
    principal subspace via incremental SVD.
    """
    def __init__(self, rank_k=50, accumulation_epochs=10):
        self.rank_k = rank_k  # Subspace dimension
        self.accumulation_epochs = accumulation_epochs
        self.gradient_buffer = []  # (num_params,) vectors
        self.subspace_S = None  # (num_params, rank_k)
    
    def accumulate(self, model, epoch):
        """Accumulate flattened gradients during early epochs."""
        if epoch < self.accumulation_epochs:
            grad_vec = torch.cat([p.grad.view(-1) for p in model.parameters() 
                                  if p.grad is not None])
            self.gradient_buffer.append(grad_vec.cpu())
    
    def compute_subspace(self):
        """Compute top-k principal directions via SVD."""
        G = torch.stack(self.gradient_buffer)  # (num_steps, num_params)
        U, S, Vt = torch.linalg.svd(G, full_matrices=False)
        self.subspace_S = Vt[:self.rank_k].T  # (num_params, rank_k)
        return self.subspace_S
    
    def measure_alignment(self, direction_vec):
        """
        Measure alignment of a direction with subspace S.
        Returns: fraction of variance explained by S (0-1)
        """
        proj = self.subspace_S @ (self.subspace_S.T @ direction_vec)
        alignment = (proj.norm() / direction_vec.norm()).item()
        return alignment

# Integration: Run during training epochs 1-10, then compute subspace
```

### Training Protocol

**Optimizer**: SGD
- Parameters: momentum=0.9, weight_decay=1e-4
- **Source**: Standard for Waterbirds (group_DRO repo)

**Learning Rate**: 1e-3
- **Source**: group_DRO default

**Schedule**: Step decay
- Parameters: milestones=[60, 75], gamma=0.1
- **Source**: Standard ImageNet schedule

**Batch Size**: 128
- **Source**: group_DRO default

**Epochs**: 90 total (accumulation during 1-10)
- **Source**: Standard for convergence

**Loss Function**: CrossEntropyLoss

**Seeds**: 1 (fixed at 42)

> ⚠️ **EXISTENCE (PoC)**: Single seed sufficient for directional validation.

### Evaluation

**Primary Metrics**:
- Spurious alignment: cosine similarity of subspace S with spurious direction
- Core alignment: cosine similarity of subspace S with core direction

**Direction Computation**:
- Spurious direction: Average gradient when background changes but label same
- Core direction: Average gradient when bird type changes

**Success Criteria**:
- spurious_alignment > 0.70 at epoch 10
- core_alignment < 0.30 at epoch 10

**Expected Baseline Performance** (from research):
- ERM worst-group accuracy: ~60%
- Spurious features dominate early (Shah et al., 2020)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: alignment measurement
- Library: torch (cosine_similarity)
- Code:
```python
alignment = F.cosine_similarity(subspace_S @ subspace_S.T @ direction, direction, dim=0)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Spurious vs Core alignment bar chart at epochs 5, 10, 45

#### Additional Figures (LLM Autonomous)

- Alignment evolution over epochs (line plot)
- Explained variance ratio by SVD components
- Heatmap of gradient-subspace alignment matrix

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `spurious_alignment > 0.70` at early epochs
3. `core_alignment < 0.30` at early epochs

---

## Appendix: Reference Implementations

### A. Literature Sources

**Source 1**: Shah et al. (2020)
- **Title**: "The Pitfalls of Simplicity Bias in Neural Networks"
- **Relevance**: Theoretical foundation for simplicity bias
- **Key Insight**: Networks learn low-complexity features first
- **Used For**: Hypothesis justification, mechanism design

**Source 2**: Sagawa et al. (2020)
- **Title**: "Distributionally Robust Neural Networks"
- **Relevance**: Waterbirds benchmark, Group DRO baseline
- **Key Insight**: 95% spurious correlation benchmark
- **Used For**: Dataset selection, baseline performance

### B. GitHub Implementations

**Repository 1**: kohpangwei/group_DRO
- **URL**: https://github.com/kohpangwei/group_DRO
- **Used For**: Waterbirds dataset, training config, ERM baseline

**Repository 2**: PolinaKirichenko/deep_feature_reweighting
- **URL**: https://github.com/PolinaKirichenko/deep_feature_reweighting
- **Used For**: Feature analysis methodology

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code complexity manageable

### D. Previous Hypothesis Context

**Previous Context**: None - first hypothesis in chain

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection | Literature | Sagawa et al. (2020) |
| Preprocessing | GitHub | kohpangwei/group_DRO |
| Baseline model | Standard | torchvision ResNet-50 |
| Mechanism design | Literature | Shah et al. (2020) |
| Training protocol | GitHub | kohpangwei/group_DRO |
| Evaluation metrics | Phase 2B | 02b_verification_plan.md |
| Success criteria | Phase 2B | H-E1 specification |

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-29

### Workflow History for This Hypothesis
- Phase 2C started: 2026-08-29
- Experiment design: COMPLETED

---

*MCP Tools Used: None available (MCP servers not connected)*
*All specifications grounded in established literature and public implementations*
*Next Phase: Phase 3 - Implementation Planning*
