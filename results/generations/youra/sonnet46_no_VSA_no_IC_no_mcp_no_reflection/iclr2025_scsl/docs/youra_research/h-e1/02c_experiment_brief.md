# Experiment Design: H-E1

**Date:** 2026-08-31
**Author:** Anonymous
**Hypothesis Statement:** Under standard ERM training on Waterbirds and CelebA with random mini-batch sampling, per-sample last-layer gradient alignment ROC-AUC for predicting spurious-minority group membership exceeds per-sample loss ROC-AUC at ≥1 epoch on BOTH datasets.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** — Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (no prerequisites)
**Gate Status:** MUST_WORK — not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK: If alignment ROC-AUC does not exceed loss ROC-AUC at ≥1 epoch on BOTH datasets, H-M1 through H-C1 are blocked and the core novelty claim of GAD collapses.

---

## Continuation Context

No previous hypothesis results — H-E1 is the first in the verification chain.

### Previous Hypothesis Results (if applicable)
None — first hypothesis.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*Archon MCP not available in this session (ablation mode). Limitation documented. All specifications derived from Exa/WebSearch and prior literature knowledge.*

**Key findings from web research:**

**Query 1: Gradient alignment / spurious correlation experiment design**
- Gradient-matching strategies prioritize samples whose per-sample gradients align with batch gradient direction, quantified using cosine similarity — established pattern in literature (Emergent Mind survey, 2025).
- Invariance Pair Guidance (arxiv 2502.18975) uses corrective gradients to identify spurious feature directions — confirms directional gradient signal encodes spurious membership.
- "Bias Leaves a Gradient Trail" (arxiv 2605.28780) — label-free bias identification via gradient probes — directly supports the hypothesis mechanism.

**Query 2: Implementation challenges**
- vmap(grad(f)) composes correctly for per-sample last-layer gradients (PyTorch docs, 2025).
- Last layer (2048×2 for ResNet-50) keeps gradient vector size manageable: 32 samples × 4096 floats = 131K floats — fits comfortably in GPU memory.
- Cosine similarity is magnitude-invariant — correct choice for directional signal across samples with varying gradient norms.

**Query 3: Waterbirds/CelebA benchmark setup**
- kohpangwei/group_DRO is canonical; provides `run_expt.py`, dataset generation scripts, and standard splits.
- Waterbirds: ResNet-50, lr=0.001, batch_size=128, n_epochs=300 (DRO setting); for ERM baseline use same backbone with standard SGD.
- CelebA: ResNet-50, lr=0.0001, batch_size=128, n_epochs=50 (DRO setting).
- JTT (Liu et al. 2021, ICML): Waterbirds worst-group 86.7%; ERM baseline 72.6% — confirmed reference targets.

### Archon Code Examples

*Archon MCP unavailable — no code examples from KB. Web research used instead.*

**PyTorch per-sample gradient pattern (from official PyTorch docs):**
```python
from torch.func import functional_call, vmap, grad

def compute_loss(params, buffers, sample, target):
    batch = sample.unsqueeze(0)
    targets = target.unsqueeze(0)
    preds = functional_call(model, (params, buffers), (batch,))
    return F.cross_entropy(preds, targets)

ft_compute_grad = grad(compute_loss)
ft_compute_sample_grad = vmap(ft_compute_grad, in_dims=(None, None, 0, 0))
ft_per_sample_grads = ft_compute_sample_grad(params, buffers, data, targets)
# ft_per_sample_grads[layer_name]: shape (batch_size, *param_shape)
```

### Exa GitHub Implementations

**Repository 1: kohpangwei/group_DRO** (canonical)
- **URL:** https://github.com/kohpangwei/group_DRO
- **Relevance:** Standard ERM/DRO training on Waterbirds + CelebA; provides dataset loading, group annotations, ResNet-50 fine-tuning.
- **Architecture:** ResNet-50 fine-tuned; linear last layer (2048 → n_classes)
- **Key Pattern:** `run_expt.py -s confounder -d CUB -t waterbird_complete95 -c forest2water2 --model resnet50 --n_epochs 300`
- **Dataset Loading:** Custom `ConfounderDataset` class; group labels loaded from metadata CSVs.
- **Results:** ERM baseline 72.6% worst-group accuracy on Waterbirds.

**Repository 2: izmailovpavel/spurious_feature_learning**
- **URL:** https://github.com/izmailovpavel/spurious_feature_learning
- **Relevance:** Feature learning analysis on Waterbirds/CelebA with ResNet-50; competitive results; useful for understanding ERM training dynamics.
- **Architecture:** ResNet-50; analysis of feature representations during training.
- **Used For:** Reference for ERM training dynamics and feature evolution across epochs.

**Repository 3: PyTorch per-sample-gradients tutorial**
- **URL:** https://docs.pytorch.org/tutorials/intermediate/per_sample_grads.html
- **Relevance:** Official reference for vmap(grad()) pattern — the core computational primitive for H-E1.
- **Key Code:** See Archon Code Examples above.

**Serena Analysis Needed:** false (code primitives are clear from official docs)

### 🎯 Implementation Priority Assessment

**For H-E1, there is no prior published implementation** — this is a PROVE_NEW claim testing a novel signal. Priority hierarchy:

1. **kohpangwei/group_DRO** for ERM training harness and dataset loading (ground truth baseline infrastructure)
2. **PyTorch torch.func** for per-sample gradient computation (official primitive)
3. **sklearn.metrics.roc_auc_score** for ROC-AUC evaluation

**Recommended Implementation Path:**
- Primary: Build on kohpangwei/group_DRO training loop; inject per-sample gradient hooks at checkpoint epochs using torch.func.vmap
- Fallback: Implement standalone ERM trainer (simpler but loses dataset loading convenience)
- Justification: group_DRO provides verified group-annotation loading, standard splits, and baseline ERM results — eliminates dataset preprocessing as confound.

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. torch.func.vmap + grad is a well-documented PyTorch primitive; no complex custom layers requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Dataset 1: Waterbirds**
- **Name:** Waterbirds (CUB + Places background composite)
- **Type:** standard (via kohpangwei/group_DRO download script)
- **Source:** Sagawa et al. 2020; kohpangwei/group_DRO `dataset_scripts/generate_waterbirds.py`
- **Splits:** Train: 4,795 / Val: 1,199 / Test: 5,794 (standard splits)
- **Groups:** 4 groups — (landbird/waterbird) × (land/water background)
  - Spurious-minority: waterbird on land (56 train), landbird on water (184 train) — ~5% combined
- **Group annotations:** Available in metadata CSV (used for evaluation only, not training)
- **Preprocessing:** Resize 256×256 → CenterCrop 224×224; ImageNet normalization (mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
- **Augmentation (train):** RandomHorizontalFlip
- **Path type:** custom (download via group_DRO script to `./data/waterbirds/`)

**Dataset 2: CelebA**
- **Name:** CelebA (Large-scale Face Attributes Dataset)
- **Type:** standard (via kohpangwei/group_DRO)
- **Source:** Liu et al. 2015; kohpangwei/group_DRO integration
- **Splits:** Train: 162,770 / Val: 19,867 / Test: 19,962 (standard splits)
- **Task:** Blond hair prediction; spurious feature: gender
- **Groups:** 4 groups — (blond/non-blond) × (male/female)
  - Spurious-minority: blond male (~0.8% of train) — ~1,387 samples
- **Group annotations:** Available via CelebA attribute metadata
- **Preprocessing:** Resize 256×256 → CenterCrop 224×224; ImageNet normalization
- **Augmentation (train):** RandomHorizontalFlip
- **Path type:** custom (download via group_DRO script to `./data/celeba/`)

**Loading Information** (for Phase 4 download):
- Method: custom (kohpangwei/group_DRO ConfounderDataset class)
- Identifier: `CUB` (Waterbirds), `CelebA` (CelebA) — as in `run_expt.py -d` flag
- Code:
```python
# Via group_DRO:
# python dataset_scripts/generate_waterbirds.py
# Then: ConfounderDataset(root_dir='./data', target_name='waterbird_complete95', confounder_names=['forest2water2'])
```

### Models

#### Baseline Model

**Architecture:** ResNet-50 (pretrained on ImageNet)
- **Last layer:** Linear(2048, n_classes) — n_classes=2 for both datasets
- **Last-layer gradient size:** 2048×2 + 2 bias = 4,098 parameters per sample
- **Feasibility:** 32 samples × 4,098 floats × 4 bytes = ~512 KB — fits in GPU memory

**Configuration:**
- Waterbirds: SGD, lr=0.001, momentum=0.9, weight_decay=1e-4, batch_size=32 (ERM baseline)
- CelebA: SGD, lr=0.0001, momentum=0.9, weight_decay=1e-4, batch_size=32 (ERM baseline)
- Note: batch_size=32 (not 128 as in DRO paper) — required for per-sample gradient memory budget

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `resnet50`
- Code: `torchvision.models.resnet50(weights=torchvision.models.ResNet50_Weights.IMAGENET1K_V1)`

#### Proposed Model

**Architecture:** Baseline ResNet-50 (ERM training only — no architectural change for H-E1)

H-E1 is a measurement hypothesis: it asks whether the gradient alignment signal (computed during standard ERM) predicts spurious-minority membership better than loss. No model modification is needed — the "proposed model" is the same ERM model with diagnostic probes injected at checkpoint epochs.

**Core Mechanism Implementation:**

```python
# Core Mechanism: Per-Sample Last-Layer Gradient Alignment Signal
# Based on: torch.func.vmap + grad (PyTorch official tutorial)
# Source: docs.pytorch.org/tutorials/intermediate/per_sample_grads.html

from torch.func import functional_call, vmap, grad
import torch.nn.functional as F

def compute_last_layer_grad_alignment(model, data_loader, device):
    """
    Compute per-sample last-layer gradient cosine similarity with batch mean.
    Returns: alignment_scores (N,), loss_scores (N,)
    """
    model.eval()
    params = {k: v for k, v in model.named_parameters() if 'fc' in k}
    buffers = dict(model.named_buffers())

    def loss_fn(params, buffers, x, y):
        # Forward pass through full model, but only last-layer params tracked
        out = functional_call(model, ({**dict(model.named_parameters()), **params}, buffers), (x.unsqueeze(0),))
        return F.cross_entropy(out, y.unsqueeze(0))

    ft_grad = grad(loss_fn)
    ft_per_sample_grad = vmap(ft_grad, in_dims=(None, None, 0, 0))

    all_alignments, all_losses = [], []
    for x_batch, y_batch, _ in data_loader:  # _ = group labels (unused in training)
        x_batch, y_batch = x_batch.to(device), y_batch.to(device)

        # Per-sample last-layer gradients: shape (B, 2048, 2) for weight + (B, 2) for bias
        per_sample_grads = ft_per_sample_grad(params, buffers, x_batch, y_batch)
        # Flatten to (B, D) where D = 4098
        g_flat = torch.cat([v.flatten(1) for v in per_sample_grads.values()], dim=1)

        # Batch mean gradient (spurious signal direction)
        g_mean = g_flat.mean(dim=0, keepdim=True)  # (1, D)

        # Cosine similarity with batch mean
        cos_sim = F.cosine_similarity(g_flat, g_mean.expand_as(g_flat), dim=1)  # (B,)
        all_alignments.append(cos_sim.detach().cpu())

        # Per-sample loss
        with torch.no_grad():
            logits = model(x_batch)
            loss_per_sample = F.cross_entropy(logits, y_batch, reduction='none')  # (B,)
        all_losses.append(loss_per_sample.cpu())

    return torch.cat(all_alignments), torch.cat(all_losses)
```

### Training Protocol

**Optimizer:** SGD
- momentum=0.9, weight_decay=1e-4
- Source: kohpangwei/group_DRO ERM baseline standard settings

**Learning Rate:**
- Waterbirds: 0.001 (Source: group_DRO README)
- CelebA: 0.0001 (Source: group_DRO README)
- Schedule: None (constant) for ERM baseline

**Batch Size:** 32
- Reason: Per-sample gradient memory budget (32 × 4098 floats fits comfortably); smaller than DRO paper's 128 but standard for gradient analysis work.

**Epochs:**
- Waterbirds: 300 (standard ERM epochs per group_DRO)
- CelebA: 50 (standard ERM epochs per group_DRO)
- Checkpoint epochs for probe: {1, 5, 10, 25, 50} on both datasets (H-E1 verification protocol)

**Loss Function:** Cross-entropy (standard ERM, no reweighting)

**Seeds:** 1 (fixed seed=42)

> ⚠️ **EXISTENCE (PoC):** Single run. No multiple seeds. No hyperparameter search.

### Evaluation

**Primary Metrics:**
- Alignment ROC-AUC: ROC-AUC of alignment score (negated cosine similarity — lower alignment = more likely spurious-minority) for predicting spurious-minority membership (binary label from group annotations)
- Loss ROC-AUC: ROC-AUC of per-sample loss for predicting spurious-minority membership

Note: alignment_score used as predictor is the **negative** cosine similarity (spurious-minority → conflicting gradient → lower cosine similarity → higher predictor score after negation).

**Evaluation per epoch:** Compute both ROC-AUC values at each of {1, 5, 10, 25, 50} epochs on FULL training set.

**Success Criteria:**
- alignment_roc_auc > loss_roc_auc at ≥1 checkpoint epoch on BOTH Waterbirds AND CelebA
- Secondary: max alignment_roc_auc > 0.6 on both datasets (meaningful predictive power)

**Expected Baseline Performance (from literature):**
- Loss ROC-AUC for spurious-minority prediction: ~0.6–0.75 (loss identifies hard samples generally, not spurious-minority specifically; JTT relies on this signal)
- Alignment ROC-AUC (hypothesis): expected > 0.70 at early epochs when spurious correlation most active
- Source: Inference from JTT (Liu et al. 2021) and LfF (Nam et al. 2020) which use loss as proxy; no prior paper reports alignment ROC-AUC directly (PROVE_NEW claim).

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: binary classification (spurious-minority vs not)
- Library: sklearn.metrics
- Code: `from sklearn.metrics import roc_auc_score; auc = roc_auc_score(group_labels, scores)`

### Visualization Requirements

#### Required Figure (Mandatory)
- **ROC-AUC vs Epoch:** Line plot comparing alignment_roc_auc and loss_roc_auc across epochs {1,5,10,25,50} for both Waterbirds and CelebA (2×1 subplot).

#### Additional Figures (LLM Autonomous)
- Cosine similarity score distributions (violin/box plot) at epoch 5: spurious-minority vs spurious-majority groups, for both datasets.
- ROC curves (FPR vs TPR) at the epoch where alignment_roc_auc is maximized, for both datasets.

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures saved to `h-e1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error on both Waterbirds and CelebA
2. alignment_roc_auc > loss_roc_auc at ≥1 checkpoint epoch on BOTH datasets

---

## Appendix: Reference Implementations

### A. Web Research Sources (Archon MCP unavailable)

**Source 1:** kohpangwei/group_DRO
- **URL:** https://github.com/kohpangwei/group_DRO
- **Query Used:** "kohpangwei group_DRO Waterbirds CelebA dataset loading training setup ResNet50"
- **Key Insights:** Standard dataset loading (ConfounderDataset), group annotation CSVs, ERM/DRO training scripts, standard hyperparameters.
- **Used For:** Training harness, dataset loading, ERM baseline hyperparameters, reference worst-group accuracy values.

**Source 2:** PyTorch per-sample-gradients tutorial
- **URL:** https://docs.pytorch.org/tutorials/intermediate/per_sample_grads.html
- **Query Used:** "torch.func vmap per-sample gradients last layer"
- **Key Insights:** `vmap(grad(loss_fn))` pattern for efficient per-sample gradient computation without for-loop overhead.
- **Used For:** Core mechanism pseudocode; confirms approach feasibility.

**Source 3:** izmailovpavel/spurious_feature_learning
- **URL:** https://github.com/izmailovpavel/spurious_feature_learning
- **Query Used:** "per-sample gradient cosine similarity spurious correlation Waterbirds CelebA"
- **Key Insights:** ResNet-50 feature analysis on Waterbirds/CelebA; ERM training dynamics; useful as secondary reference for feature evolution across epochs.
- **Used For:** Understanding ERM feature learning timeline for checkpoint epoch selection.

**Source 4:** Liu et al. 2021 — Just Train Twice (JTT)
- **URL:** https://arxiv.org/abs/2107.09044
- **Query Used:** "JTT just train twice Liu 2021 Waterbirds worst group accuracy"
- **Key Insights:** JTT achieves 86.7% worst-group on Waterbirds; ERM baseline 72.6%; uses misclassification (loss-based proxy) for upweighting.
- **Used For:** Baseline comparison targets; confirms loss ROC-AUC is the competing signal to beat.

**Source 5:** "Bias Leaves a Gradient Trail" (arxiv 2605.28780)
- **URL:** https://arxiv.org/pdf/2605.28780
- **Query Used:** "per-sample gradient cosine similarity spurious correlation"
- **Key Insights:** Label-free bias identification via gradient probes; gradient direction encodes spurious feature membership — directly supports H-E1 mechanism claim.
- **Used For:** Theoretical grounding; confirms that gradient direction is a bias-relevant signal.

**Source 6:** "Gradient-Weight Alignment as Train-Time Proxy" (arxiv 2510.25480)
- **URL:** https://arxiv.org/html/2510.25480v1
- **Query Used:** "gradient alignment debiasing per-sample cosine similarity batch mean gradient ERM"
- **Key Insights:** Gradient-weight alignment used as proxy for generalization; cosine similarity between per-sample and batch gradients quantifies alignment.
- **Used For:** Confirms cosine similarity formulation is standard; supports using batch-mean gradient as reference direction.

### B. Serena Analysis

*Skipped* — Code primitives (torch.func.vmap, grad, F.cosine_similarity, sklearn.roc_auc_score) are clear from official documentation. No complex custom layers requiring semantic analysis.

### C. Previous Hypothesis Context

None — H-E1 is the first hypothesis in the chain.

### D. Traceability Matrix

| Specification | Source Type | Source Reference |
|---|---|---|
| Waterbirds dataset splits/groups | GitHub | kohpangwei/group_DRO README |
| CelebA dataset splits/groups | GitHub | kohpangwei/group_DRO README |
| ERM training hyperparameters (Waterbirds) | GitHub | group_DRO `run_expt.py` defaults |
| ERM training hyperparameters (CelebA) | GitHub | group_DRO `run_expt.py` defaults |
| Per-sample gradient computation | PyTorch docs | per_sample_grads tutorial |
| Cosine similarity formulation | Web research | arxiv 2510.25480 |
| Gradient as bias proxy | Web research | arxiv 2605.28780 |
| Baseline worst-group accuracy | Paper | Liu et al. 2021 (JTT) |
| ROC-AUC evaluation | sklearn docs | sklearn.metrics.roc_auc_score |
| Checkpoint epochs {1,5,10,25,50} | Phase 2B | H-E1 verification protocol |

---

## State Information

**State File:** verification_state.yaml (ABLATION OVERRIDE active)
**Date:** 2026-08-31

### Workflow History for This Hypothesis
- 2026-08-31: H-E1 set to IN_PROGRESS (external loop, Phase 2C start)
- 2026-08-31: experiment_design.status = IN_PROGRESS (Step 1)
- 2026-08-31: 02b_context.md generated JIT from 02b_verification_plan.md
- 2026-08-31: Research gathered via WebSearch (Archon/Serena MCP unavailable in session)
- 2026-08-31: experiment_design.status = COMPLETED (Step 8)

---

*MCP Tools Used: WebSearch (Archon/Exa MCP unavailable in this session — documented limitation)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
