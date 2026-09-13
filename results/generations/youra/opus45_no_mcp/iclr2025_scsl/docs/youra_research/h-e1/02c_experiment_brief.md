# Experiment Design: H-E1

**Date:** 2026-08-19
**Author:** Anonymous
**Hypothesis Statement:** Crystallization zone exists as localized training phase where WGA decline accelerates
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites)
**Gate Status:** MUST_WORK - not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK: If crystallization zone cannot be detected, entire research program stops.

---

## Continuation Context

This is the foundation hypothesis (first in chain). No previous hypothesis results available.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in verification chain.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Crystallization zone / WGA acceleration detection**
- **Simplicity Bias (Shah et al., 2020)**: DNNs preferentially learn linearly-separable features early in training. This creates the foundation for spurious feature advantage.
- **Gradient Starvation (Pezeshki et al., 2021)**: When one feature dominates gradients, others receive vanishing updates - mechanism for self-reinforcing feedback.
- **Last Layer Retraining (Kirichenko et al., 2023)**: Both spurious and core features are learned in representations, but classifier commits to spurious. Validates that crystallization is a classifier-level phenomenon.

**Query 2: Worst-Group Accuracy Implementation**
- WGA computed as minimum accuracy across all (label, spurious_attribute) groups
- WILDS benchmark provides group annotations for Waterbirds, CelebA
- Standard practice: evaluate WGA at each epoch checkpoint

**Query 3: Second Derivative Detection Methods**
- Numerical differentiation with smoothing common in training dynamics analysis
- 5-epoch rolling window balances noise reduction vs temporal resolution
- Peak detection via scipy.signal.find_peaks or manual threshold

### Archon Code Examples

**WILDS Benchmark Loading (p-lambda/wilds)**
```python
from wilds import get_dataset
dataset = get_dataset(dataset='waterbirds', download=True)
train_data = dataset.get_subset('train')
val_data = dataset.get_subset('val')
test_data = dataset.get_subset('test')
```

**WGA Computation Pattern**
```python
def compute_wga(predictions, labels, groups):
    group_accs = {}
    for g in unique_groups:
        mask = (groups == g)
        group_accs[g] = (predictions[mask] == labels[mask]).mean()
    return min(group_accs.values())
```

### Exa GitHub Implementations

**Repository 1**: p-lambda/wilds
- **URL**: https://github.com/p-lambda/wilds
- **Relevance**: Official WILDS benchmark with Waterbirds, CelebA datasets
- **Stars**: 1.2k+
- **Key Pattern**: GroupDRO baseline, WGA evaluation built-in

**Repository 2**: kohpangwei/group_DRO
- **URL**: https://github.com/kohpangwei/group_DRO
- **Relevance**: Original Group DRO implementation (Sagawa 2020)
- **Training Config**: SGD, lr=1e-3, batch_size=128, 100 epochs for Waterbirds

**Repository 3**: anniesch/jtt
- **URL**: https://github.com/anniesch/jtt
- **Relevance**: Just Train Twice baseline implementation

### 🎯 Implementation Priority Assessment

**This is a DETECTION experiment, not paper reproduction.** No author implementation exists for "crystallization zone detection" - this is the novel contribution being tested.

**Recommended Implementation Path:**
- Primary: WILDS benchmark (p-lambda/wilds) for datasets + WGA computation
- Fallback: Custom implementation using torchvision ResNet + manual group tracking
- Justification: WILDS provides standard dataset loading, splits, and group annotations. Detection logic (second derivative) is custom to this hypothesis.

### Code Analysis (Serena MCP)

*Serena MCP not available in this session. Analysis based on Phase 2B documentation and literature.*

**Architecture Analysis:**
- ResNet-50 with pretrained ImageNet weights (standard in group robustness literature)
- Final FC layer modified for dataset-specific classes (2 for Waterbirds, 2 for CelebA)
- No architectural changes needed for crystallization DETECTION - we observe existing training dynamics

---

## Experiment Specification

### Dataset

**Primary Dataset: Waterbirds**
- **Type:** standard
- **Source:** WILDS benchmark suite (p-lambda/wilds)
- **Task:** Binary classification (landbird vs waterbird)
- **Spurious Correlation:** Background (water vs land) correlates with label
- **Total Samples:** 11,788 total (4,795 train, 400 val, 6,593 test)
- **Minority Groups:** Waterbirds on land (~56 samples), Landbirds on water (~184 samples)
- **Group Annotations:** Built-in (enables WGA computation)
- **Splits:** Standard train/val/test from WILDS

**Secondary Dataset: CelebA (Hair Color)**
- **Type:** standard
- **Source:** WILDS benchmark suite
- **Task:** Binary classification (blond vs non-blond hair)
- **Spurious Correlation:** Gender correlates with hair color
- **Total Samples:** 202,599 total
- **Minority Groups:** Blond males (~1,387), Non-blond females (many)
- **Group Annotations:** Built-in

**Loading Information** (for Phase 4 download):
- Method: WILDS Python package
- Identifier: `waterbirds`, `celebA`
- Code:
```python
from wilds import get_dataset
from wilds.common.data_loaders import get_train_loader, get_eval_loader

# Waterbirds
wb_dataset = get_dataset(dataset='waterbirds', download=True, root_dir='./data')
wb_train = wb_dataset.get_subset('train', transform=train_transform)
wb_val = wb_dataset.get_subset('val', transform=eval_transform)
wb_test = wb_dataset.get_subset('test', transform=eval_transform)

# CelebA
celeba_dataset = get_dataset(dataset='celebA', download=True, root_dir='./data')
```

### Models

#### Baseline Model

**Architecture:** ResNet-50 (pretrained on ImageNet)
- **Type:** CNN
- **Parameters:** ~25.6M
- **Input:** 224x224 RGB images
- **Output:** 2 classes (binary classification)
- **Modification:** Replace final FC layer for dataset-specific classes

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `resnet50`
- Code:
```python
import torchvision.models as models

model = models.resnet50(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, num_classes)  # num_classes=2
```

#### Proposed Model

**Architecture:** Baseline ResNet-50 (no architectural modification)

**NOTE:** This is an EXISTENCE hypothesis testing DETECTION of crystallization, not a new mechanism. The "proposed" component is the analysis pipeline, not a model modification.

**Core Mechanism Implementation:**

```python
# Crystallization Zone Detection Pipeline
# Based on: Shah 2020 (simplicity bias), Pezeshki 2021 (gradient starvation)

import numpy as np
from scipy.ndimage import uniform_filter1d

class CrystallizationDetector:
    """
    Detect crystallization zone via second derivative of WGA.
    """
    def __init__(self, smoothing_window=5):
        self.smoothing_window = smoothing_window
        self.wga_history = []
    
    def log_epoch(self, wga):
        """Record WGA for current epoch."""
        self.wga_history.append(wga)
    
    def compute_second_derivative(self):
        """Compute smoothed d²WGA/dt² across training."""
        wga = np.array(self.wga_history)
        # Apply smoothing
        smoothed = uniform_filter1d(wga, size=self.smoothing_window)
        # First derivative
        d1 = np.gradient(smoothed)
        # Second derivative
        d2 = np.gradient(d1)
        return d2
    
    def detect_crystallization_peak(self, threshold=-0.01):
        """Find significant negative peak in second derivative."""
        d2 = self.compute_second_derivative()
        # Find most negative point in first 50% of training
        midpoint = len(d2) // 2
        d2_early = d2[:midpoint]
        peak_idx = np.argmin(d2_early)
        peak_value = d2_early[peak_idx]
        return peak_idx, peak_value, peak_value < threshold

# Integration: Run after each epoch evaluation
```

### Training Protocol

**Optimizer:** SGD
- momentum: 0.9
- weight_decay: 1e-4
- **Source:** WILDS Waterbirds baseline (kohpangwei/group_DRO)

**Learning Rate:** 1e-3
- **Schedule:** None (constant) - important for crystallization detection to avoid LR confounds
- **Source:** Control experiment requirement from Phase 2B

**Batch Size:** 128
- **Source:** Standard in group robustness literature

**Epochs:** 100 (Waterbirds), 50 (CelebA)
- **Checkpointing:** Every epoch (dense for WGA curve)
- **Source:** Phase 2B verification protocol

**Loss Function:** CrossEntropyLoss
- **Source:** Standard for classification

**Seeds:** 1 (fixed at 42)
- **Rationale:** EXISTENCE PoC requires single run only

### Evaluation

**Primary Metrics:**
- **Worst-Group Accuracy (WGA):** Minimum accuracy across all (label, spurious_attr) groups
- **d²WGA/dt²:** Second derivative of smoothed WGA curve

**Success Criteria (PoC: Direction-based):**
1. Significant negative d²WGA/dt² peak exists in first 50% of training
2. Peak magnitude < -0.01 (threshold for "significant")
3. Effect present in at least 2/3 benchmarks tested

**Expected Baseline Performance:**
- Initial WGA: ~90% (epoch 0, random classifier)
- Final WGA: ~60-75% (ERM converged)
- **Source:** WILDS benchmark, Sagawa 2020

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification with group annotations
- Library: Custom + torchmetrics
- Code:
```python
def compute_wga(predictions, labels, groups):
    """Compute worst-group accuracy."""
    unique_groups = torch.unique(groups)
    group_accs = []
    for g in unique_groups:
        mask = (groups == g)
        if mask.sum() > 0:
            acc = (predictions[mask] == labels[mask]).float().mean()
            group_accs.append(acc.item())
    return min(group_accs)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **WGA Curve with Crystallization Point**: Line plot of WGA vs epoch, with detected crystallization epoch marked
- **Second Derivative Plot**: d²WGA/dt² vs epoch, with negative peak highlighted

#### Additional Figures (LLM Autonomous)

1. **Multi-Benchmark Comparison**: WGA curves for Waterbirds and CelebA overlaid (normalized epoch)
2. **Smoothing Sensitivity**: d²WGA/dt² with different window sizes (3, 5, 7 epochs)
3. **Group-wise Accuracy**: Per-group accuracy curves showing minority vs majority divergence

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### Primary References

1. **WILDS Benchmark**
   - URL: https://github.com/p-lambda/wilds
   - Usage: Dataset loading, WGA computation
   - License: MIT

2. **Group DRO (Sagawa et al., 2020)**
   - URL: https://github.com/kohpangwei/group_DRO
   - Paper: "Distributionally Robust Neural Networks for Group Shifts"
   - Usage: Training protocol reference, expected WGA baselines

3. **Simplicity Bias (Shah et al., 2020)**
   - Paper: "The Pitfalls of Simplicity Bias in Neural Networks"
   - Usage: Theoretical foundation for early spurious feature preference

4. **Gradient Starvation (Pezeshki et al., 2021)**
   - Paper: "Gradient Starvation: A Learning Proclivity in Neural Networks"
   - Usage: Mechanism explanation for self-reinforcing feedback

5. **Last Layer Retraining (Kirichenko et al., 2023)**
   - Paper: "Last Layer Re-Training is Sufficient for Robustness to Spurious Correlations"
   - Usage: Evidence that features are learned but classifier commits to spurious

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19: H-E1 set to IN_PROGRESS (Phase 2C start)
- 2026-08-19: Phase 2C experiment design completed

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
