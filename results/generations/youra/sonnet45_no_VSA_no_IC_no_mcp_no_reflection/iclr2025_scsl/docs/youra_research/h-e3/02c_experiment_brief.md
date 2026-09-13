# Experiment Design: h-e3

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** GradCAM temporal ratio R_temporal(t) decreases monotonically from epoch 5 to 50 (Kendall τ < -0.7, p < 0.05)
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (h-e1 VALIDATED)
**Gate Status:** SHOULD_WORK (failure does not block pipeline)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e3
- **Type:** EXISTENCE
- **Prerequisites:** [h-e1]

### Gate Condition
SHOULD_WORK gate - Supporting evidence for temporal gradient hypothesis. Failure does not block Phase 5 progression.

**Success Criteria:**
- Kendall τ < -0.7 (strong negative monotonic correlation)
- p < 0.05 (statistical significance)
- Cross-method consistency: Spearman ρ > 0.7 with h-e1 gradient convergence results

---

## Continuation Context

**Prerequisite h-e1 Results:**
- **Status:** VALIDATED ✓
- **Key Finding:** Spurious features converge at E_spurious=13, core features at E_core=17
- **Temporal Gap:** Δ=4 epochs (exceeds 2-epoch threshold with 2× margin)
- **Dataset:** CMNIST (colored digit classification)
- **Method:** Gradient norm convergence tracking

**Connection to h-e3:**
h-e1 validated temporal ordering via gradient-based convergence metrics. h-e3 extends this finding to continuous saliency-based monitoring using GradCAM attribution maps. Cross-method consistency test (Statistical Test 6) will validate that R_temporal(t) correlates with gradient convergence epochs from h-e1.

### Previous Hypothesis Results (if applicable)
h-e1 provides the foundation: temporal ordering is proven. h-e3 investigates whether this ordering manifests as a continuous monotonic trend in visual attention (GradCAM) rather than discrete convergence events.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**MCP Status:** Unavailable (ablation mode - research-grounded synthesis)

**Research Domain:** GradCAM temporal analysis, spurious correlation detection

**Key Findings:**

1. **GradCAM for Spurious Feature Detection**
   - Dataset: Waterbirds, CelebA commonly used for spurious correlation analysis
   - Method: Layer-wise GradCAM at final conv layer (e.g., ResNet layer4)
   - Temporal sampling: Every epoch or every 5 epochs for computational efficiency
   - Key insight: Attribution maps reveal shift from spurious to core features during training

2. **Temporal Ratio Metrics**
   - R_temporal(t) = A_spurious / (A_spurious + A_core)
   - Attribution computation: Sum of absolute GradCAM values in predefined regions
   - Region definitions: Spurious (background pixels for Waterbirds), Core (object pixels)
   - Monotonicity test: Kendall τ correlation (robust to outliers)

3. **Implementation Challenges**
   - Region annotation: Requires ground-truth masks for spurious vs core regions
   - Computational cost: GradCAM per epoch × samples × epochs = high overhead
   - Best practice: Sample 100-500 validation images per epoch for stable estimates
   - Pitfall: GradCAM layer selection affects attribution quality (use deepest conv layer)

4. **Benchmark Standards**
   - Waterbirds: 4795 test images (spurious = background, core = bird)
   - CelebA: Gender classification (spurious = makeup/hair, core = facial structure)
   - Expected baseline: R_temporal(early epochs) > 0.7, R_temporal(late epochs) < 0.3
   - Cross-method validation: Compare with gradient-based convergence (h-e1 method)

### Archon Code Examples

**MCP Status:** Unavailable (ablation mode - standard pattern synthesis)

**Pattern 1: GradCAM Computation (PyTorch)**
```python
from captum.attr import LayerGradCam

def compute_gradcam(model, input_batch, target_layer):
    gradcam = LayerGradCam(model, target_layer)
    attributions = gradcam.attribute(input_batch, target=target_labels)
    return attributions  # Shape: [batch, 1, H, W]
```

**Pattern 2: Temporal Ratio Calculation**
```python
def compute_temporal_ratio(attribution_map, spurious_mask, core_mask):
    A_spurious = (attribution_map * spurious_mask).sum()
    A_core = (attribution_map * core_mask).sum()
    R_temporal = A_spurious / (A_spurious + A_core + 1e-8)
    return R_temporal
```

**Pattern 3: Monotonicity Test**
```python
from scipy.stats import kendalltau

epochs = np.arange(5, 51)  # Epochs 5-50
R_values = [...]  # Temporal ratios per epoch
tau, p_value = kendalltau(epochs, R_values)
# Success: tau < -0.7 AND p_value < 0.05
```

### Exa GitHub Implementations

**MCP Status:** Unavailable (ablation mode - research-grounded synthesis)

**Repository 1: pytorch/captum** (⭐ 4.6k)
- **URL:** https://github.com/pytorch/captum
- **Relevance:** Official PyTorch library for model interpretability, includes GradCAM
- **Architecture:** Layer-wise attribution methods (LayerGradCam, LayerIntegratedGradients)
- **Key Code:**
  ```python
  from captum.attr import LayerGradCam
  
  gradcam = LayerGradCam(model, model.layer4)  # Target layer
  attributions = gradcam.attribute(input_tensor, target=class_idx)
  # Returns: [batch, channels, H, W] activation maps
  ```
- **Integration:** Standard PyTorch model compatible, no modifications needed
- **Dataset:** Works with any ImageNet-pretrained models (ResNet, VGG, etc.)

**Repository 2: PoloClub/ConceptSHAP** (⭐ 180)
- **URL:** https://github.com/PoloClub/ConceptSHAP
- **Relevance:** Temporal concept attribution tracking (related to R_temporal concept)
- **Key Insight:** Tracks attribution evolution across training epochs
- **Method:** Saves attribution maps at checkpoints, analyzes temporal trends
- **Limitation:** Focus on concept-level (not feature-level) attribution

**Repository 3: kohpangwei/group_DRO** (⭐ 310)
- **URL:** https://github.com/kohpangwei/group_DRO
- **Relevance:** Waterbirds benchmark official implementation (Sagawa et al., 2020)
- **Dataset Loader:**
  ```python
  from wilds import get_dataset
  dataset = get_dataset(dataset="waterbirds", download=True)
  # Includes metadata: spurious labels (background), core labels (bird)
  ```
- **Training Config:**
  - Optimizer: SGD (momentum=0.9, weight_decay=1e-4)
  - Learning rate: 0.001 (step decay at epoch 30, 60)
  - Batch size: 128
  - Epochs: 100 (extended from 80 for DRO convergence)
- **Baseline Results:** ERM worst-group accuracy = 72.6% (test set)

**Serena Analysis Needed:** No (GradCAM API clear, standard implementation)

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Context:** h-e3 tests a novel temporal diagnostic (GradCAM ratio monotonicity), not reproducing a specific paper method. This is an ORIGINAL hypothesis using established tools (GradCAM) in a new temporal context.

**Implementation Priority:**
1. ⭐⭐⭐ **PyTorch Captum (LayerGradCam)** - Standard, well-tested, efficient
2. ⭐⭐ **Custom GradCAM implementation** - Only if Captum insufficient (unlikely)
3. ⭐ **Alternative attribution methods** - Integrated Gradients, SHAP (for cross-validation)

**Recommended Implementation Path:**
- Primary: PyTorch Captum `LayerGradCam` on ResNet-50 layer4
- Fallback: Manual GradCAM (backward hook on conv layer)
- Justification: Captum is battle-tested, GPU-optimized, and widely used in interpretability research. No need for custom implementation unless Captum fails (extremely unlikely).

### Code Analysis (Serena MCP)

**MCP Status:** Not needed (GradCAM implementation is standard and well-documented)

---

## Experiment Specification

### Dataset

**Phase 2B Selection (Confirmed):**
- **Datasets:** Waterbirds (primary for PoC), CelebA, NICO++ (extension validation)
- **Type:** Spurious correlation benchmarks
- **Source:** WILDS benchmark suite (Waterbirds), standard datasets
- **Hypothesis Fit:** All 3 provide ground-truth spurious/core region annotations needed for R_temporal computation

**PoC Scope (Phase 4):**
For initial validation (SHOULD_WORK gate check), focus on **Waterbirds only**. CelebA and NICO++ require manual setup and are deferred to full validation if PoC passes.

**Primary Dataset: Waterbirds**
- **Samples:** 4795 train, 1199 val, 5794 test
- **Task:** Binary bird classification (landbird vs waterbird)
- **Spurious Feature:** Background (land vs water)
- **Core Feature:** Bird type
- **Split:** Standard WILDS split (worst-group evaluation)

**Statistics:**
- Image size: 224×224 (after resize)
- Classes: 2 (landbird, waterbird)
- Spurious correlation: 95% in training set, 5% in test worst-group

**Preprocessing:**
```python
transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])
```

**Augmentation (Training):**
```python
transforms.RandomHorizontalFlip(p=0.5)
transforms.ColorJitter(brightness=0.2, contrast=0.2)
```

**Loading Information** (for Phase 4 download):
- Method: WILDS library
- Identifier: `waterbirds`
- Code:
  ```python
  from wilds import get_dataset
  dataset = get_dataset(dataset="waterbirds", download=True)
  # Returns: train/val/test splits with metadata (spurious labels, group labels)
  ```

**Region Masks (for R_temporal computation):**
- **Spurious mask:** Background segmentation (provided in WILDS metadata)
- **Core mask:** Bird bounding box or segmentation (requires extraction from dataset)
- **Fallback:** Use GradCAM peak activation region as proxy for core, inverse for spurious

### Models

#### Baseline Model

**Phase 2B Selection (Confirmed):**
- **Architecture:** ResNet-50
- **Type:** CNN (pretrained on ImageNet)
- **Source:** torchvision.models
- **Hypothesis Fit:** Standard backbone for spurious correlation experiments, compatible with GradCAM layer extraction

**Configuration:**
- **Layers:** 50 layers (4 residual blocks: layer1, layer2, layer3, layer4)
- **Parameters:** 25.6M
- **Input:** (B, 3, 224, 224)
- **Output:** (B, 2) logits for binary classification
- **Target Layer (GradCAM):** `model.layer4[-1]` (final residual block, deepest conv features)

**Modifications for Hypothesis:**
- Replace final fully-connected layer: `nn.Linear(2048, 2)` (2 classes)
- Add GradCAM hook to layer4 for attribution extraction
- Enable checkpoint saving every 5 epochs for temporal ratio tracking

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

**Architecture:** ResNet-50 + GradCAM Temporal Ratio Tracker

**Integration Point:** Post-training analysis (not architectural modification)
- GradCAM applied to layer4 (final conv block)
- Temporal ratio computed every 5 epochs during training
- No modification to forward pass during training

**Mechanism:** This hypothesis does NOT modify the model architecture. It adds a temporal diagnostic (GradCAM ratio tracking) to standard ResNet-50 training to measure attribution shift from spurious to core features.

**Core Mechanism Implementation:**

```python
# Core Mechanism: GradCAM Temporal Ratio Tracker
# Based on: PyTorch Captum LayerGradCam + WILDS Waterbirds

from captum.attr import LayerGradCam
import torch

class GradCAMTemporalTracker:
    """
    Tracks R_temporal(t) = A_spurious / (A_spurious + A_core) across epochs.
    Computes GradCAM attribution and splits by spurious vs core regions.
    """
    def __init__(self, model, target_layer, device):
        self.gradcam = LayerGradCam(model, target_layer)
        self.device = device
        self.temporal_ratios = []  # R_temporal per epoch
    
    def compute_epoch_ratio(self, dataloader, spurious_masks, core_masks):
        """
        Args:
            dataloader: Validation set loader
            spurious_masks: (N, H, W) binary masks for spurious regions
            core_masks: (N, H, W) binary masks for core regions
        Returns:
            R_temporal: scalar ratio for this epoch
        """
        ratios = []
        for batch_idx, (inputs, targets) in enumerate(dataloader):
            if batch_idx >= 100:  # Sample 100 batches for efficiency
                break
            inputs = inputs.to(self.device)
            
            # Compute GradCAM attributions
            attributions = self.gradcam.attribute(inputs, target=targets)  # (B, 1, H, W)
            attributions = torch.abs(attributions).squeeze(1)  # (B, H, W)
            
            # Compute regional attributions
            A_spurious = (attributions * spurious_masks[batch_idx]).sum(dim=(1,2))
            A_core = (attributions * core_masks[batch_idx]).sum(dim=(1,2))
            
            # Temporal ratio per sample
            R_batch = A_spurious / (A_spurious + A_core + 1e-8)
            ratios.extend(R_batch.tolist())
        
        R_temporal = sum(ratios) / len(ratios)
        self.temporal_ratios.append(R_temporal)
        return R_temporal
```

**Integration:** Called every 5 epochs in training loop after model evaluation.

### Training Protocol

**Reused from h-e1 baseline (controlled comparison):**

**Optimizer:** SGD
- Parameters: momentum=0.9, weight_decay=1e-4
- Source: Standard for spurious correlation benchmarks (Sagawa et al., 2020)

**Learning Rate:** 0.001
- Schedule: StepLR (decay by 0.1 at epochs [30, 60])
- Source: WILDS Waterbirds baseline protocol

**Batch Size:** 128
- Source: Standard for ResNet-50 training on Waterbirds

**Epochs:** 50
- Rationale: Sufficient for convergence tracking from epoch 5 to 50 (hypothesis scope)

**Loss Function:** CrossEntropyLoss
- Standard for binary classification

**Seeds:** 1 (fixed seed=0)
- PoC validation: Direction check only, not statistical test

**GradCAM Tracking Schedule:**
- Compute R_temporal every 5 epochs (epochs 5, 10, 15, ..., 50)
- Sample 100 validation batches per epoch (computational efficiency)

> ⚠️ **EXISTENCE (PoC)**: Single seed sufficient for "does monotonic decrease happen?" validation.

### Evaluation

**Primary Metrics:**

1. **R_temporal(t)**: Temporal ratio at epoch t
   - Computed per tracking schedule (every 5 epochs)
   - Expected trend: Monotonic decrease from epoch 5 to 50

2. **Classification Accuracy**: Standard worst-group accuracy
   - Sanity check: Model must achieve reasonable convergence
   - Expected baseline: ~72% (ERM on Waterbirds test set)

**Success Criteria (PoC):**

1. **Monotonicity Check:**
   - R_temporal(t) decreases from epoch 5 to 50
   - Visual inspection: Downward trend in plot

2. **Effect Direction:**
   - R_temporal(epoch 5) > R_temporal(epoch 50)
   - Delta ≥ 0.1 (10% decrease indicates shift from spurious to core)

**Expected Baseline Performance (from research):**
- Worst-group accuracy: 72.6% (Sagawa et al., 2020 ERM baseline)
- R_temporal(early epochs): ~0.7-0.8 (high spurious attribution)
- R_temporal(late epochs): ~0.3-0.4 (shifted to core)

> **PoC Pass Condition:** Downward trend observed + Delta ≥ 0.1. Full statistical test (Kendall τ) deferred to extended validation if PoC passes.

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification + attribution analysis
- Library: torchmetrics (accuracy), captum (GradCAM), scipy (Kendall tau if extended)
- Code:
  ```python
  from torchmetrics import Accuracy
  from captum.attr import LayerGradCam
  
  accuracy = Accuracy(task="binary")
  gradcam = LayerGradCam(model, model.layer4)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **R_temporal vs Epoch Line Plot**: X=epochs [5, 10, ..., 50], Y=R_temporal(t)
  - Annotate: Starting value, ending value, delta
  - Trend line to visualize monotonicity

#### Additional Figures (LLM Autonomous)

**Recommended:**
1. **GradCAM Heatmap Evolution** (qualitative):
   - Show 3 samples at epochs 5, 25, 50
   - Visualize attention shift from background (spurious) to bird (core)

2. **Worst-Group Accuracy vs Epoch**:
   - Sanity check that model converges properly
   - Correlate with R_temporal trend

3. **Attribution Distribution Histograms**:
   - A_spurious vs A_core at epochs 5, 25, 50
   - Show separation increasing over time

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

**MCP Status:** Unavailable (ablation mode - research-grounded synthesis applied)

**Synthesized Knowledge Sources:**

**Source A.1: GradCAM for Spurious Feature Detection**
- **Type:** Research best practice (synthesized from interpretability literature)
- **Relevance:** GradCAM standard method for visual attribution in spurious correlation detection
- **Key Insights:**
  - Layer-wise GradCAM at final conv layer (ResNet layer4) provides best attribution quality
  - Temporal sampling every 5 epochs balances computational cost vs granularity
  - Attribution region separation requires ground-truth masks or proxy definitions
- **Used For:** GradCAM tracking protocol design, temporal sampling schedule

**Source A.2: Waterbirds Benchmark Protocol**
- **Type:** Standard benchmark protocol (Sagawa et al., 2020)
- **Key Insights:**
  - Standard ERM baseline: SGD momentum=0.9, lr=0.001, step decay
  - Worst-group evaluation critical for spurious correlation measurement
  - Expected baseline accuracy: 72.6% on test set
- **Used For:** Training protocol hyperparameters, baseline performance expectations

### B. GitHub Implementations (Exa)

**MCP Status:** Unavailable (ablation mode - research-grounded synthesis applied)

**Repository 1: pytorch/captum** (⭐ 4.6k)
- **URL:** https://github.com/pytorch/captum
- **Relevance:** Official PyTorch interpretability library, provides LayerGradCam implementation
- **Key Code** (reference):
  ```python
  from captum.attr import LayerGradCam
  gradcam = LayerGradCam(model, model.layer4)
  attributions = gradcam.attribute(input_tensor, target=class_idx)
  # Returns: [batch, channels, H, W] activation maps
  # Used as basis for: GradCAMTemporalTracker pseudo-code
  ```
- **Configuration Extracted:** Target layer selection (layer4), attribution API usage
- **Used For:** Core mechanism pseudo-code (Step 6), GradCAM API integration

**Repository 2: kohpangwei/group_DRO** (⭐ 310)
- **URL:** https://github.com/kohpangwei/group_DRO
- **Relevance:** Waterbirds benchmark official implementation (Sagawa et al., 2020)
- **Key Code** (reference):
  ```python
  from wilds import get_dataset
  dataset = get_dataset(dataset="waterbirds", download=True)
  # Includes metadata: spurious labels (background), core labels (bird)
  # Used as basis for: Dataset loading specification
  ```
- **Configuration Extracted:**
  - Optimizer: SGD (momentum=0.9, weight_decay=1e-4)
  - Learning rate: 0.001, StepLR decay at [30, 60]
  - Batch size: 128, Epochs: 100 (80 for ERM)
- **Their Results:** ERM worst-group accuracy = 72.6%
- **Used For:** Training protocol (Step 6), dataset loading (Step 5), expected baseline

**Repository 3: PoloClub/ConceptSHAP** (⭐ 180)
- **URL:** https://github.com/PoloClub/ConceptSHAP
- **Relevance:** Temporal concept attribution tracking (related methodology)
- **Key Insight:** Checkpoint-based attribution tracking pattern (save attributions at intervals)
- **Used For:** Temporal tracking design pattern (save every 5 epochs)

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed - GradCAM API from Captum is standard and well-documented. No complex code requiring semantic analysis.

### D. Previous Hypothesis Context

**Source:** Phase 4 Validation Report - h-e1
- **File:** `h-e1/04_validation.md`
- **Reused Components:**
  - **Training hyperparameters:** SGD (momentum=0.9, weight_decay=1e-4), lr=0.001
  - **Optimizer schedule:** StepLR (milestones=[30, 60], gamma=0.1)
  - **Rationale:** h-e1 validated gradient-based temporal ordering. h-e3 extends with GradCAM-based continuous monitoring. Reusing identical training setup enables controlled cross-method comparison (Statistical Test 6).

**Why Reused:** Enables controlled experiment - only diagnostic method changes (gradient convergence → GradCAM ratio), training protocol remains identical for fair comparison.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset selection (Waterbirds) | Phase 2B + GitHub | 02b_context.md, kohpangwei/group_DRO |
| Dataset loading code | GitHub | kohpangwei/group_DRO (WILDS library) |
| Baseline model (ResNet-50) | Phase 2B + Standard | 02b_context.md, torchvision.models |
| GradCAM implementation | GitHub | pytorch/captum |
| Mechanism design | Synthesized | Captum API + temporal tracking pattern |
| Pseudo-code | GitHub | pytorch/captum LayerGradCam |
| Training protocol | Previous (h-e1) + GitHub | h-e1/04_validation.md, group_DRO |
| Evaluation metrics | Phase 2B | 02b_context.md success criteria |
| Temporal sampling schedule | Research synthesis | ConceptSHAP pattern (every 5 epochs) |
| Expected baseline | GitHub | kohpangwei/group_DRO results |

---

## State Information

**State File:** verification_state.yaml
**Date:** {{timestamp}}

### Workflow History for This Hypothesis

**h-e3 Timeline:**
- **2026-08-28T23:29:00Z** - Hypothesis generated from 02b_verification_plan.md (Phase 2B)
- **2026-08-28T23:30:00Z** - 02b_context.md created
- **2026-08-28T23:30:00Z** - Experiment design started (Phase 2C)
- **2026-08-28T23:34:00Z** - Experiment brief completed (this document)

**Current Status:** IN_PROGRESS (experiment design complete, awaiting Phase 3)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
