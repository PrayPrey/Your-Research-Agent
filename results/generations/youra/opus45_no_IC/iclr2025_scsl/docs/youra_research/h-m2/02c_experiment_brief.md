# Experiment Design: H-M2

**Date:** 2026-08-12
**Author:** Anonymous
**Hypothesis Statement:** Spurious features are easier to learn than core features
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Template** - Testing causal step in hypothesis chain.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 PASSED)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (Simplicity bias causes early pattern learning) - PASSED

### Gate Condition
**Type:** SHOULD_WORK
**Pass Condition:** Spurious probe accuracy peaks before core probe accuracy peaks
**Failure Response:** Document as limitation, proceed with empirical d_i correlation

---

## Continuation Context

### Previous Hypothesis Results (H-M1)
- **Status:** PASSED
- **Key Findings:**
  - Spurious probe accuracy at epoch 5: 91.2%
  - Core probe accuracy at epoch 5: 80.5%
  - Bias confirmed: spurious features learned faster early
  - Core improvement confirmed over training

H-M2 builds on H-M1 by measuring WHEN each feature type peaks, not just early-epoch comparison.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct results for "spurious correlation feature learning speed". Related findings:
- Training dynamics research shows early layer representations stabilize quickly
- Deep network representations evolve differently across layers during training

### Archon Code Examples

No directly relevant linear probe implementations found in KB. General feature extraction patterns available.

### Exa GitHub Implementations

**Key Findings:**

1. **PyTorch Feature Extraction (Official)**
   - `torchvision.models.feature_extraction.create_feature_extractor()`
   - Enables intermediate layer access via symbolic tracing
   - Node naming: `"layer4.2.relu"` format for ResNet

2. **Linear Probe Pattern (The Neural Base)**
   ```python
   linear_head = nn.Linear(feature_dim, num_classes)
   with torch.no_grad():
       features = backbone(images)
   logits = linear_head(features)
   ```
   - Freeze backbone, train only linear head
   - Use `torch.no_grad()` for feature extraction

3. **Training Dynamics Research (simranketha/Dynamics_during_training_DNN)**
   - Tracks latent generalization across training epochs
   - Uses linear probes on layer-wise outputs
   - Demonstrates peak-finding methodology across epochs

4. **Tunnel Effect Paper**
   - Linear probing accuracy reaches 95-98% of final performance in early layers
   - ResNet-34 transition at layer 19
   - Numerical rank reduces to ~number of classes

### 🎯 Implementation Priority Assessment

**CRITICAL: For this experiment, we implement from scratch using standard patterns**

**Recommended Implementation Path:**
- Primary: PyTorch feature extraction + custom linear probe training loop
- Fallback: Manual hook-based feature extraction
- Justification: Standard pattern, well-documented, enables epoch-by-epoch probe training

### Code Analysis (Serena MCP)

Not applicable - no existing codebase to analyze for this hypothesis.

---

## Experiment Specification

### Dataset

**Name:** Waterbirds
**Version:** Standard (Sagawa et al., 2019)
**Source:** https://github.com/kohpangwei/group_DRO
**Type:** standard

| Split | Size | Purpose |
|-------|------|---------|
| Train | 4795 | Model training + probe training |
| Val | 1199 | Hyperparameter tuning |
| Test | 5794 | Final evaluation |

**Spurious Correlation:** 95% (bird type ↔ background)

**Group Structure:**
- Majority: waterbird+water, landbird+land (95%)
- Minority: waterbird+land, landbird+water (5%)

**Preprocessing:**
- Resize to 224×224
- Normalize: ImageNet mean/std
- Standard augmentation (random crop, horizontal flip)

**Loading Information** (for Phase 4 download):
- Method: Custom download script
- Identifier: group_DRO/waterbirds
- Code:
```python
# Download from group_DRO repository
# Extract to data/waterbirds/
# Load using custom WaterbirdsDataset class
from wilds import get_dataset
dataset = get_dataset(dataset='waterbirds', download=True)
```

### Models

#### Baseline Model

**Architecture:** ResNet-18 (pretrained on ImageNet)
**Source:** torchvision.models.resnet18(pretrained=True)
**Final Layer:** Replace fc with nn.Linear(512, 2)

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: ResNet18_Weights.IMAGENET1K_V1
- Code:
```python
import torchvision.models as models
model = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
model.fc = nn.Linear(512, 2)
```

#### Proposed Model

**Architecture:** Same ResNet-18 with epoch-wise probe extraction

**Core Mechanism Implementation:**

```python
# Pseudo-code: Track probe accuracy for spurious vs core features

def train_with_probes(model, train_loader, epochs=100):
    """Train model and track linear probe accuracy per epoch."""
    
    # Storage for probe accuracies
    spurious_probe_acc = []  # Background classification
    core_probe_acc = []      # Bird shape classification
    
    # Feature extractor (freeze after each epoch for probing)
    feature_extractor = create_feature_extractor(
        model, return_nodes={'avgpool': 'features'}
    )
    
    for epoch in range(epochs):
        # 1. Train model for one epoch (standard ERM)
        train_one_epoch(model, train_loader)
        
        # 2. Extract features with frozen backbone
        features, spurious_labels, core_labels = extract_all_features(
            feature_extractor, train_loader
        )
        
        # 3. Train spurious probe (background: water=0, land=1)
        spurious_probe = LogisticRegression(max_iter=1000)
        spurious_probe.fit(features, spurious_labels)
        spurious_acc = spurious_probe.score(features, spurious_labels)
        spurious_probe_acc.append(spurious_acc)
        
        # 4. Train core probe (bird: waterbird=0, landbird=1)
        core_probe = LogisticRegression(max_iter=1000)
        core_probe.fit(features, core_labels)
        core_acc = core_probe.score(features, core_labels)
        core_probe_acc.append(core_acc)
        
        print(f"Epoch {epoch}: Spurious={spurious_acc:.3f}, Core={core_acc:.3f}")
    
    return spurious_probe_acc, core_probe_acc

def find_peak_epoch(accuracies, window=5):
    """Find epoch where accuracy peaks (smoothed)."""
    smoothed = np.convolve(accuracies, np.ones(window)/window, mode='valid')
    peak_epoch = np.argmax(smoothed) + window // 2
    return peak_epoch

# Main analysis
spurious_acc, core_acc = train_with_probes(model, train_loader)
spurious_peak = find_peak_epoch(spurious_acc)
core_peak = find_peak_epoch(core_acc)

# H-M2 success: spurious peaks before core
success = spurious_peak < core_peak
```

### Training Protocol

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Optimizer | SGD | Standard for Waterbirds |
| Learning Rate | 0.001 | From group_DRO baseline |
| Momentum | 0.9 | Standard |
| Weight Decay | 1e-4 | Standard regularization |
| Batch Size | 128 | Memory-efficient |
| Epochs | 100 | Full training curve |
| LR Schedule | None | Simpler analysis |

**Probe Training:**
- Method: sklearn LogisticRegression
- Regularization: L2 (C=1.0)
- Max iterations: 1000
- Solver: lbfgs

### Evaluation

**Primary Metric:** Peak epoch comparison
- spurious_peak_epoch: First epoch where spurious probe accuracy stabilizes
- core_peak_epoch: First epoch where core probe accuracy stabilizes

**Success Criteria (PoC):**
- **Primary:** spurious_peak_epoch < core_peak_epoch
- **Secondary:** Statistically significant difference in learning curves

**Statistical Test:**
- Compare area under curve (AUC) for epochs 1-20
- Wilcoxon signed-rank test on per-epoch differences

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Classification (binary probes)
- Library: sklearn.linear_model.LogisticRegression
- Code:
```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Learning Curves:** Spurious vs Core probe accuracy over epochs (dual y-axis or overlay)
- **Peak Markers:** Vertical lines indicating peak epochs for each feature type

#### Additional Figures (LLM Autonomous)
- Accuracy difference curve (spurious - core) over epochs
- First derivative of accuracy curves (learning speed)
- Confusion matrices at peak epochs

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `spurious_peak_epoch < core_peak_epoch`

**Expected Outcome:**
- Spurious probe should peak early (epochs 5-15) as model quickly captures background correlation
- Core probe should peak later (epochs 30-60) as model gradually learns bird shape features
- Difference of at least 10 epochs expected based on H-M1 results

---

## Appendix: Reference Implementations

### 1. PyTorch Feature Extraction
**Source:** https://docs.pytorch.org/vision/main/feature_extraction.html
```python
from torchvision.models.feature_extraction import create_feature_extractor
return_nodes = {'avgpool': 'features'}
feature_extractor = create_feature_extractor(model, return_nodes=return_nodes)
```

### 2. Linear Probe Pattern
**Source:** The Neural Base (theneuralbase.com)
```python
# Freeze backbone
for param in backbone.parameters():
    param.requires_grad = False

# Extract features
with torch.no_grad():
    features = backbone(images)
    features = features.view(features.size(0), -1)

# Train probe
linear_head = nn.Linear(feature_dim, num_classes)
```

### 3. Training Dynamics Analysis
**Source:** simranketha/Dynamics_during_training_DNN
- Checkpoint saving every epoch
- Layer-wise probe evaluation
- Peak detection methodology

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-12T14:55:00Z

### Workflow History for This Hypothesis
- H-M2 set to IN_PROGRESS (2026-08-12T14:53:40Z)
- Phase 2C experiment design started (2026-08-12T14:55:00Z)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
