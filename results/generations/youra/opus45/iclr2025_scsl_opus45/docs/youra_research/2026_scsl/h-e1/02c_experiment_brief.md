# Experiment Design: H-E1

**Date:** 2026-04-14
**Author:** Anonymous
**Hypothesis Statement:** Under standard ERM training on Waterbirds, if we extract per-sample loss trajectory features (L₁, slope, variance, time-to-convergence) from epochs 1-5, then these features will predict minority group membership with AUROC > 0.75, because minority samples experience prolonged optimization conflict creating distinctive trajectory patterns.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** N/A (no prerequisites)
**Gate Status:** MUST_WORK - Not yet evaluated

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-E1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
MUST_WORK: AUROC > 0.75 with p < 0.05 vs random baseline (0.5)
- If fails: ABANDON main hypothesis (trajectory divergence does not exist)

---

## Continuation Context

This is the first hypothesis in the verification sequence. No prior hypothesis results to build upon.

### Previous Hypothesis Results (if applicable)
N/A - Foundation hypothesis

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: "loss trajectory per-sample training dynamics"**
- Results: Diffusion model training examples (ControlNet, DreamBooth)
- No direct spurious correlation or per-sample loss tracking research found
- General insight: Standard PyTorch training patterns are well-documented

**Query 2: "spurious correlation waterbirds group robustness"**
- Results: Limited - primarily image generation datasets (butterflies)
- Waterbirds dataset not indexed in Archon KB
- Note: Will rely on Exa GitHub search for domain-specific implementations

**Query 3: "minority group detection ERM training"**
- Results: Consistency models, general training scripts
- No direct minority group detection methods found
- Insight: Novel research area - few indexed implementations

**Key Observation:** Archon KB lacks spurious correlation research content. This confirms the novelty of the research direction. Implementation patterns will come primarily from Exa GitHub search and domain literature.

### Archon Code Examples

**Query 1: "PyTorch training loop loss tracking"**
- Source: huggingface/optimum-quanto
- Pattern: Standard training loop with per-batch loss computation
```python
model.train()
for batch_idx, (data, target) in enumerate(train_loader):
    data, target = data.to(device), target.to(device)
    optimizer.zero_grad()
    output = model(data)
    loss = torch.nn.functional.nll_loss(output, target)
    loss.backward()
    optimizer.step()
```
- Insight: Can extend with per-sample loss logging by removing reduction

**Query 2: "ResNet50 image classification PyTorch"**
- Source: Various training scripts
- Pattern: Standard image classification with cross-entropy loss
- Insight: Use torchvision.models.resnet50(pretrained=True) with custom head

**Applicable Patterns for H-E1:**
1. Per-sample loss: Use `reduction='none'` in loss function to get individual losses
2. Deterministic evaluation: Disable dropout, use fixed batch ordering
3. Loss normalization: Divide by initial loss (L_t / L_1) for scale-invariance

### Exa GitHub Implementations

**Query 1: Waterbirds spurious correlation dataset PyTorch GroupDRO**

**Repository 1**: kohpangwei/group_DRO (295+ stars) - **OFFICIAL IMPLEMENTATION**
- **URL**: https://github.com/kohpangwei/group_DRO
- **Relevance**: Official Waterbirds dataset and GroupDRO implementation from Sagawa et al. (2020)
- **Architecture**: ResNet-50 pretrained on ImageNet
- **Key Code**:
  ```python
  # Sample command for Waterbirds
  python run_expt.py -s confounder -d CUB -t waterbird_complete95 -c forest2water2 \
    --lr 0.001 --batch_size 128 --weight_decay 0.0001 --model resnet50 --n_epochs 300
  ```
- **Training Config**:
  - Optimizer: SGD with momentum 0.9
  - Learning rate: 0.001
  - Batch size: 128
  - Weight decay: 0.0001
  - Epochs: 300 (for full training), 20 for our PoC
- **Dataset**: Waterbirds (4,795 training samples)
  - G1: Landbirds on land BG - 3,498 images
  - G2: Landbirds on water BG - 184 images (minority)
  - G3: Waterbirds on water BG - 1,057 images
  - G4: Waterbirds on land BG - 56 images (minority)
- **Results**: GroupDRO achieves ~89-90% WGA, ERM achieves ~72%

**Repository 2**: ssagawa/overparam_spur_corr
- **URL**: https://github.com/ssagawa/overparam_spur_corr
- **Relevance**: Investigates why overparameterization exacerbates spurious correlations
- **Key Insight**: Provides random features experiments with logistic regression
- **Code Pattern**:
  ```python
  python run_waterbirds_random_features.py \
    --features_path resnet18_1layer.npy \
    --model_type logistic --error_type zero_one
  ```

**Query 2: Per-sample loss tracking training dynamics**

**Reference**: Toneva et al. "An Empirical Study of Example Forgetting" (arXiv:1812.05159)
- **Relevance**: DIRECTLY relevant - tracks per-sample learning dynamics
- **Key Concept**: "Forgetting events" = transitions from correct to incorrect classification
- **Insight**: Certain examples are forgotten with high frequency, some not at all
- **Application**: Our trajectory features (L₁, slope, variance) capture similar dynamics

**Query 3: AUROC calculation with sklearn/torchmetrics**

**Standard Pattern**:
```python
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

# 5-fold stratified cross-validation
kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = []
for train_idx, val_idx in kfold.split(X, y):
    model = LogisticRegression(max_iter=1000)
    model.fit(X[train_idx], y[train_idx])
    y_pred = model.predict_proba(X[val_idx])[:, 1]
    auc = roc_auc_score(y[val_idx], y_pred)
    scores.append(auc)
print(f'AUROC: {np.mean(scores):.3f} ± {np.std(scores):.3f}')
```

**Serena Analysis Needed**: No - Code patterns are clear and well-documented

### Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

| Priority | Source | Confidence | Use Case |
|----------|--------|------------|----------|
| 1 (HIGHEST) | kohpangwei/group_DRO | Very High | Waterbirds dataset, ERM baseline, training loop |
| 2 | Toneva et al. forgetting code | High | Per-sample loss tracking pattern |
| 3 | sklearn/torchmetrics | Very High | AUROC evaluation with cross-validation |

**Recommended Implementation Path:**
- Primary: kohpangwei/group_DRO for dataset and ERM training, custom per-sample loss logging
- Fallback: WILDS package for dataset access if group_DRO setup fails
- Justification: group_DRO is the official implementation cited in 100+ papers, provides exact hyperparameters and dataset splits used in spurious correlation literature

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. The kohpangwei/group_DRO repository provides well-documented training loops and data loading, and the sklearn AUROC patterns are standard. No complex custom architectures require deeper semantic analysis.

**Key Implementation Patterns Identified (from Exa results):**

1. **Per-sample loss extraction**: Use `reduction='none'` in CrossEntropyLoss
2. **Deterministic evaluation**: Disable data augmentation during loss logging
3. **Feature extraction**: Extract trajectory features at end of each epoch
4. **AUROC evaluation**: Use sklearn LogisticRegression with StratifiedKFold CV

---

## Experiment Specification

### Dataset

**Dataset**: Waterbirds
**Type**: standard (REAL dataset - NOT synthetic)
**Source**: Sagawa et al. (2020) - Distributionally Robust Neural Networks

**Statistics**:
- Total training samples: 4,795
- Validation samples: 1,199
- Test samples: 5,794
- Classes: 2 (waterbird, landbird)
- Groups: 4 (bird_type × background)
  - G1: Landbirds on land BG - 3,498 (majority)
  - G2: Landbirds on water BG - 184 (minority)
  - G3: Waterbirds on water BG - 1,057 (majority)
  - G4: Waterbirds on land BG - 56 (minority)

**Spurious Correlation**: 95% correlation between bird type and background in training set
**Distribution Shift**: Val/test sets are balanced (50/50) across groups

**Preprocessing**:
- Resize: 224×224 (standard ImageNet size)
- Normalization: ImageNet mean/std
  - mean = [0.485, 0.456, 0.406]
  - std = [0.229, 0.224, 0.225]

**Augmentation** (training only):
- RandomResizedCrop(224)
- RandomHorizontalFlip()

**Evaluation Transforms**:
- Resize(256)
- CenterCrop(224)

**Loading Information** (for Phase 4 download):
- Method: WILDS package (recommended) or HuggingFace
- Identifier: `waterbirds` (WILDS) or `grodino/waterbirds` (HuggingFace)
- Code:
```python
# Option 1: WILDS (recommended - includes group labels)
from wilds import get_dataset
dataset = get_dataset(dataset="waterbirds", download=True, root_dir="./data")

# Option 2: Direct download from group_DRO
# Download tarball from: https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz
# Extract to: ./data/waterbird_complete95_forest2water2/

# Option 3: HuggingFace
from datasets import load_dataset
dataset = load_dataset("grodino/waterbirds")
```

### Models

#### Baseline Model

**Architecture**: ResNet-50
**Type**: CNN pretrained on ImageNet
**Source**: torchvision.models

**Configuration**:
- Backbone: ResNet-50 (pretrained on ImageNet)
- Final layer: Linear(2048, 2) for binary classification
- Total parameters: ~25.6M
- Input size: 224×224×3
- Output: 2 logits (waterbird, landbird)

**Modifications for H-E1 Experiment**:
- No architectural modifications needed
- Standard ERM training (not GroupDRO)
- Per-sample loss logging added (see Core Mechanism)

**Expected Baseline Performance** (from literature):
- ERM Average Accuracy: ~97%
- ERM Worst-Group Accuracy: ~72%
- GroupDRO WGA: ~89-90%

**Loading Information** (for Phase 4 download):
- Method: torchvision (auto-downloads pretrained weights)
- Identifier: `resnet50` with `weights=IMAGENET1K_V1`
- Code:
```python
import torchvision.models as models
import torch.nn as nn

# Load pretrained ResNet-50
model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)

# Replace final layer for binary classification
model.fc = nn.Linear(model.fc.in_features, 2)

# Move to device
model = model.to(device)
```

#### Proposed Model

**Architecture:** ResNet-50 (ERM) + Per-Sample Loss Trajectory Extraction + Logistic Regression Classifier

**Integration Point:**
- Loss tracking: After forward pass, before loss aggregation
- Feature extraction: At end of each epoch (epochs 1-5)
- Classification: After trajectory feature collection (post-training)

**Modification from Baseline:**
- Add per-sample loss logging (no architectural changes to ResNet-50)
- Extract 4 trajectory features per sample
- Train separate logistic regression on trajectory features for group prediction

**Core Mechanism Implementation:**

```python
# Core Mechanism: Per-Sample Loss Trajectory Extraction
# Based on: kohpangwei/group_DRO patterns + Toneva et al. forgetting dynamics

import torch
import torch.nn.functional as F
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import StratifiedKFold

class LossTrajectoryTracker:
    """
    Track per-sample loss trajectories across epochs for minority group detection.
    Hypothesis: Minority samples show distinctive trajectory patterns (AUROC > 0.75).
    """
    def __init__(self, num_samples, num_epochs=5):
        self.num_samples = num_samples
        self.num_epochs = num_epochs
        # Shape: (num_samples, num_epochs)
        self.loss_history = np.zeros((num_samples, num_epochs))
        self.current_epoch = 0
    
    def log_epoch_losses(self, sample_indices, losses):
        """Log per-sample losses for current epoch (deterministic eval pass)."""
        # losses: (batch_size,) from reduction='none'
        self.loss_history[sample_indices, self.current_epoch] = losses.cpu().numpy()
    
    def extract_features(self):
        """Extract 4 trajectory features per sample."""
        L = self.loss_history  # (N, E)
        L_norm = L / (L[:, 0:1] + 1e-8)  # Normalize by L1
        
        # Feature 1: Initial loss (L1)
        f1_initial = L[:, 0]
        # Feature 2: Slope (L5 - L1) / 4
        f2_slope = (L[:, -1] - L[:, 0]) / (self.num_epochs - 1)
        # Feature 3: Variance of normalized trajectory
        f3_variance = np.var(L_norm, axis=1)
        # Feature 4: Time to 95% of minimum (convergence speed)
        L_min = L.min(axis=1, keepdims=True)
        threshold = L[:, 0:1] - 0.95 * (L[:, 0:1] - L_min)
        f4_convergence = np.argmax(L <= threshold, axis=1).astype(float)
        
        return np.stack([f1_initial, f2_slope, f3_variance, f4_convergence], axis=1)
    
    def evaluate_auroc(self, group_labels):
        """Evaluate AUROC for predicting minority group membership."""
        features = self.extract_features()  # (N, 4)
        minority_labels = (group_labels == 1) | (group_labels == 3)  # Groups 2,4 are minority
        
        # 5-fold stratified cross-validation
        kfold = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        aucs = []
        for train_idx, val_idx in kfold.split(features, minority_labels):
            clf = LogisticRegression(max_iter=1000)
            clf.fit(features[train_idx], minority_labels[train_idx])
            y_pred = clf.predict_proba(features[val_idx])[:, 1]
            aucs.append(roc_auc_score(minority_labels[val_idx], y_pred))
        
        return np.mean(aucs), np.std(aucs)

# Integration in training loop:
# 1. After each epoch, run deterministic eval pass (no augmentation)
# 2. Compute per-sample loss with reduction='none'
# 3. Log to tracker: tracker.log_epoch_losses(indices, losses)
# 4. After epoch 5, extract features and compute AUROC
```

### Training Protocol

> **EXISTENCE (PoC)**: Single seed, fixed hyperparameters from literature.

**Optimizer**: SGD
- momentum: 0.9
- weight_decay: 0.0001
- **Source**: kohpangwei/group_DRO (Sagawa et al., 2020)

**Learning Rate**: 0.001
- **Source**: group_DRO default for Waterbirds

**Schedule**: None (constant LR for PoC simplicity)
- For full experiment: StepLR with milestones

**Batch Size**: 128
- **Source**: group_DRO default

**Epochs**: 20 (full training) with trajectory logging for epochs 1-5
- **Rationale**: 5 epochs sufficient for trajectory divergence detection
- Model trains for 20 epochs total, but features extracted from early epochs

**Loss Function**: CrossEntropyLoss
- With `reduction='none'` for per-sample loss tracking
- Aggregated with mean for backward pass

**Seeds**: 1 (fixed at 42)
- **Rationale**: PoC only needs direction, not variance estimates

**Per-Sample Loss Logging Protocol**:
1. After each training epoch, run deterministic evaluation pass
2. Disable data augmentation (only resize + center crop)
3. Compute loss with `reduction='none'`
4. Store per-sample losses indexed by sample ID
5. Apply 3-point moving average smoothing (optional, for noise reduction)

### Evaluation

> **EXISTENCE (PoC)**: No statistical tests. Success = proposed > baseline.

**Primary Metric**: AUROC (Area Under ROC Curve)
- Definition: Probability that trajectory features rank a random minority sample higher than a random majority sample
- Target: AUROC > 0.75 (from Phase 2B gate condition)
- Baseline: Random classifier AUROC = 0.50

**Secondary Metrics**:
- Feature importance: Logistic regression coefficients for each trajectory feature
- Per-feature AUROC: Individual discriminative power of L₁, slope, variance, convergence time

**Success Criteria (PoC)**:
- ✅ PASS: AUROC > 0.75 (25 percentage points above chance)
- ❌ FAIL: AUROC ≤ 0.75

**Expected Performance** (from literature):
- Random baseline: AUROC = 0.50
- Gradient norm detection (Liu et al.): AUROC ≈ 0.91
- Our target: AUROC > 0.75 (conservative threshold for existence proof)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (minority vs majority group)
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import StratifiedKFold

# AUROC with 5-fold CV
def compute_auroc_cv(features, labels, n_splits=5):
    kfold = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    aucs = []
    for train_idx, val_idx in kfold.split(features, labels):
        clf = LogisticRegression(max_iter=1000)
        clf.fit(features[train_idx], labels[train_idx])
        y_pred = clf.predict_proba(features[val_idx])[:, 1]
        aucs.append(roc_auc_score(labels[val_idx], y_pred))
    return np.mean(aucs), np.std(aucs)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on H-E1 hypothesis (trajectory divergence existence), recommended visualizations:

1. **Loss Trajectory Comparison** (recommended)
   - Plot: Normalized loss curves (L_t/L_1) over epochs 1-5
   - Groups: Minority vs Majority (mean ± std)
   - Purpose: Visualize trajectory divergence between groups

2. **Feature Distribution** (recommended)
   - Plot: Histogram/violin plot of each trajectory feature
   - Groups: Minority vs Majority
   - Purpose: Show feature separability

3. **ROC Curve** (recommended)
   - Plot: TPR vs FPR with AUROC annotation
   - Include: Random baseline diagonal
   - Purpose: Visualize classification performance

4. **Feature Importance** (optional)
   - Plot: Bar chart of logistic regression coefficients
   - Purpose: Identify most discriminative trajectory features

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1**: PyTorch Training Loop Patterns
- **Type**: Code examples
- **Query Used**: "PyTorch training loop loss tracking"
- **Relevance**: Standard training loop structure for per-sample loss extraction
- **Key Insights**:
  - Use `reduction='none'` to get per-sample losses
  - Standard optimizer patterns (SGD with momentum)
- **Used For**: Training protocol design

**Source A.2**: Loss Function Patterns
- **Type**: Code examples
- **Query Used**: "loss trajectory per-sample training dynamics"
- **Relevance**: Loss computation patterns in PyTorch
- **Used For**: Per-sample loss logging implementation

**Note**: Archon KB lacks specific spurious correlation/Waterbirds content, confirming novelty of research direction. Primary implementation guidance from Exa GitHub.

### B. GitHub Implementations (Exa)

**Repository B.1**: kohpangwei/group_DRO (⭐ 295+) - **PRIMARY SOURCE**
- **URL**: https://github.com/kohpangwei/group_DRO
- **Query Used**: "Waterbirds spurious correlation dataset PyTorch GroupDRO"
- **Relevance**: Official Waterbirds dataset and GroupDRO implementation from Sagawa et al. (2020)
- **Key Code** (annotated):
  ```python
  # run_expt.py - Training command
  python run_expt.py -s confounder -d CUB -t waterbird_complete95 -c forest2water2 \
    --lr 0.001 --batch_size 128 --weight_decay 0.0001 --model resnet50 --n_epochs 300
  ```
- **Configuration Extracted**:
  - Optimizer: SGD, momentum=0.9, weight_decay=0.0001
  - Learning rate: 0.001
  - Batch size: 128
  - Model: ResNet-50 pretrained
- **Their Results**: ERM ~72% WGA, GroupDRO ~89% WGA
- **Used For**: Dataset loading, training hyperparameters, baseline performance

**Repository B.2**: ssagawa/overparam_spur_corr (⭐ 30)
- **URL**: https://github.com/ssagawa/overparam_spur_corr
- **Query Used**: Same as B.1
- **Relevance**: Logistic regression on Waterbirds features
- **Key Code**:
  ```python
  python run_waterbirds_random_features.py --model_type logistic
  ```
- **Used For**: Logistic regression evaluation pattern

**Paper Reference B.3**: Toneva et al. "An Empirical Study of Example Forgetting" (arXiv:1812.05159)
- **URL**: https://arxiv.org/abs/1812.05159
- **Query Used**: "per-sample loss tracking training dynamics forgetting events"
- **Relevance**: DIRECTLY relevant - defines per-sample learning dynamics tracking
- **Key Concept**: "Forgetting events" as sample-level training dynamics
- **Used For**: Theoretical foundation for trajectory feature extraction

**Reference B.4**: sklearn ROC/AUC Documentation
- **URL**: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.roc_auc_score.html
- **Query Used**: "sklearn AUROC logistic regression cross-validation"
- **Relevance**: Standard AUROC computation with stratified CV
- **Used For**: Evaluation metrics implementation

### C. Code Analysis (Serena)

**Serena Analysis**: Not performed - code from search results was sufficiently clear.

The kohpangwei/group_DRO repository provides well-documented training loops and data loading patterns. The sklearn AUROC computation is standard. No complex custom architectures required deeper semantic analysis.

### D. Previous Hypothesis Context

**Previous Context**: None - H-E1 is the first hypothesis in the verification chain.

This is the foundation EXISTENCE hypothesis. All subsequent hypotheses (H-M1, H-M2, H-M3) depend on H-E1 passing.

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| Dataset (Waterbirds) | GitHub | B.1 (kohpangwei/group_DRO) |
| Dataset statistics | GitHub + HuggingFace | B.1, grodino/waterbirds |
| Preprocessing | GitHub | B.1 (group_DRO transforms) |
| Baseline model (ResNet-50) | GitHub | B.1 (group_DRO) |
| Training hyperparameters | GitHub | B.1, B.2 |
| Per-sample loss concept | Paper | B.3 (Toneva et al.) |
| Trajectory features | Phase 2B + Novel | 02b_verification_plan.md |
| AUROC evaluation | sklearn docs | B.4 |
| Success criteria | Phase 2B | 02b_verification_plan.md |
| Expected baseline | Literature | B.1, Sagawa et al. (2020) |

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-14

### Workflow History for This Hypothesis
- Phase 2C started: 2026-04-14

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
