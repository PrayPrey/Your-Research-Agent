# Experiment Design: H-M1

**Date:** 2026-08-12
**Author:** Anonymous
**Hypothesis Statement:** Under ERM training, if simplicity bias operates, then early representations (epoch 5) capture spurious features while later representations (epoch 50) capture core features, because neural networks prioritize simple patterns.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Testing causal mechanism of simplicity bias

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-E1 passed: Mann-Whitney p=7.36e-15, precision=0.329, recall=0.329)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M1
- **Type:** MECHANISM
- **Prerequisites:** H-E1 (COMPLETED, gate satisfied)

### Gate Condition
- **Type:** MUST_WORK
- **Pass Condition:** Spurious probe accuracy at epoch 5 > Core probe accuracy at epoch 5
- **Secondary:** CKA similarity shows representation change over training
- **Failure Response:** PIVOT to direct d_i measurement without mechanism explanation

---

## Continuation Context

### Previous Hypothesis Results (H-E1)
- **Status:** COMPLETED (gate satisfied)
- **Key Finding:** Onset delay d_i differs significantly between minority/majority groups
- **Metrics:** Precision=0.329, Recall=0.329, Mann-Whitney p=7.36e-15
- **Implication:** Foundation validated - simplicity bias mechanism testing now justified

### Reused Components from H-E1
- **Dataset:** Waterbirds (same)
- **Model:** ResNet-18 (same)
- **Training Protocol:** Same base configuration
- **Rationale:** Controlled comparison - only evaluation method changes (linear probes)

---

## Implementation Research Summary

### Archon Knowledge Base Findings

Limited direct findings on simplicity bias in Archon KB. Diffusion model documentation found but not directly applicable. Research pivoted to Exa web search for primary sources.

### Archon Code Examples

Linear probe / feature extraction code patterns found in PyTorch/diffusers ecosystem:
- Feature extraction via frozen backbone
- Preprocessing pipelines for image models
- Model loading patterns from pretrained weights

### Exa GitHub Implementations

**Key Papers Found:**

1. **SPARE (Yang et al., AISTATS 2024)** - "Identifying Spurious Biases Early in Training through the Lens of Simplicity Bias"
   - Core insight: Examples with spurious features are separable based on model output early in training
   - Shows simplicity bias causes spurious features to dominate early epochs
   - Up to 21.1% WGA improvement, 12x faster than alternatives

2. **DFR (Izmailov et al., NeurIPS 2022)** - "On Feature Learning in the Presence of Spurious Correlations"
   - ERM features highly competitive with specialized robustness methods
   - Last layer retraining on balanced set achieves 97% WGA on Waterbirds
   - Model architecture and pretraining matter more than training method

3. **Complexity Matters (Qiu et al., 2024)** - "Dynamics of Feature Learning in the Presence of Spurious Correlations"
   - Stronger spurious correlations slow core feature learning
   - Two distinct subnetworks form for core vs spurious features
   - Learning phases not always separable
   - Spurious features NOT forgotten even after core learning

### 🎯 Implementation Priority Assessment

**CRITICAL: For linear probe methodology, use established pattern from DFR/SPARE**

**Recommended Implementation Path:**
- Primary: Standard linear probe on frozen features (widely validated methodology)
- Fallback: N/A - linear probing is the standard approach
- Justification: DFR demonstrates linear probes effectively measure feature quality; SPARE shows early/late epoch comparison reveals simplicity bias

### Code Analysis (Serena MCP)

**Linear Probe Pattern (from Exa code search):**

```python
# Freeze backbone, train only linear head
model = resnet50(weights=ResNet50_Weights.IMAGENET1K_V2)
backbone = nn.Sequential(*list(model.children())[:-1])
backbone.eval()
for p in backbone.parameters():
    p.requires_grad = False

linear_head = nn.Linear(feature_dim, num_classes)
# Train linear_head on frozen features
```

**Key Implementation Notes:**
- Extract features at epoch 5, 20, 50 checkpoints
- Train separate probes for spurious (background) vs core (bird shape) features
- Use AdaptiveAvgPool2d to collapse spatial dimensions
- Block gradient flow: `torch.no_grad()` during feature extraction

---

## Experiment Specification

### Dataset

**Dataset:** Waterbirds
**Type:** standard (benchmark dataset)
**Source:** https://github.com/kohpangwei/group_DRO (Sagawa et al., 2019)

**Statistics:**
- Train: 4795 samples
- Val: 1199 samples  
- Test: 5794 samples
- Groups: 4 (waterbird/landbird × water/land background)
- Spurious correlation: 95%

**Loading Information** (for Phase 4 download):
- Method: Custom download + torch DataLoader
- Identifier: `waterbird_complete95_forest2water2`
- Code:
```python
# Download from group_DRO repository
# wget https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz
from wilds import get_dataset
dataset = get_dataset('waterbirds', download=True)
```

**Preprocessing:**
- Resize to 224x224
- Normalize: mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]
- Training augmentation: RandomResizedCrop(224), RandomHorizontalFlip

### Models

#### Baseline Model

**Architecture:** ResNet-18 (pretrained ImageNet)
**Type:** CNN
**Source:** `torchvision.models.resnet18(pretrained=True)`

**Loading Information** (for Phase 4 download):
- Method: torchvision
- Identifier: `resnet18`
- Code:
```python
import torchvision.models as models
model = models.resnet18(weights='IMAGENET1K_V1')
model.fc = nn.Linear(512, 2)  # Binary: waterbird vs landbird
```

#### Proposed Model

**Architecture:** ResNet-18 + Linear Probe Analysis (no architecture change)

**Core Mechanism:** Linear probe comparison across epochs to measure feature content

This hypothesis does NOT modify the model architecture. Instead, it measures what the baseline learns at different epochs via linear probing.

**Core Mechanism Implementation:**

```python
class LinearProbeAnalysis:
    """
    Measure simplicity bias via linear probes on frozen features.
    Compares spurious (background) vs core (bird shape) feature learning.
    """
    def __init__(self, backbone, feature_dim=512):
        self.backbone = backbone
        self.spurious_probe = nn.Linear(feature_dim, 2)  # water/land
        self.core_probe = nn.Linear(feature_dim, 2)      # waterbird/landbird
        
    def extract_features(self, x):
        """Extract features from frozen backbone."""
        with torch.no_grad():
            features = self.backbone(x)
            features = F.adaptive_avg_pool2d(features, 1)
            features = features.view(features.size(0), -1)
        return features
    
    def train_probes(self, train_loader, epochs=10):
        """Train separate probes for spurious and core features."""
        for epoch in range(epochs):
            for images, (bird_labels, bg_labels) in train_loader:
                features = self.extract_features(images)
                # Train spurious probe (predict background)
                spurious_loss = F.cross_entropy(
                    self.spurious_probe(features), bg_labels)
                # Train core probe (predict bird type)
                core_loss = F.cross_entropy(
                    self.core_probe(features), bird_labels)
        
    def evaluate(self, test_loader):
        """Return probe accuracies."""
        spurious_acc = compute_accuracy(self.spurious_probe, test_loader)
        core_acc = compute_accuracy(self.core_probe, test_loader)
        return spurious_acc, core_acc

# Experiment: Compare probe accuracies at epoch 5, 20, 50
# Hypothesis: spurious_acc(epoch5) > core_acc(epoch5)
```

### Training Protocol

**Training (Base Model):**
- Optimizer: SGD
- Parameters: momentum=0.9, weight_decay=1e-4
- Learning Rate: 0.001
- Schedule: StepLR, step_size=30, gamma=0.1
- Batch Size: 64
- Epochs: 100 (save checkpoints at 5, 20, 50)
- Loss: CrossEntropyLoss
- Seeds: 1 (fixed: 42)
- **Source:** Standard Waterbirds training (JTT, DFR papers)

**Linear Probe Training (per checkpoint):**
- Optimizer: SGD
- Learning Rate: 0.01
- Epochs: 10 (probe converges quickly on frozen features)
- **Source:** DFR paper methodology

### Evaluation

**Primary Metrics:**
- Spurious probe accuracy at epoch 5, 20, 50
- Core probe accuracy at epoch 5, 20, 50

**Success Criteria (PoC):**
- **Primary:** `spurious_acc(epoch5) > core_acc(epoch5)`
- **Secondary:** `core_acc(epoch50) > core_acc(epoch5)` (core features learned later)

**Expected Baseline Performance** (from research):
- Spurious probe (background) at epoch 5: ~85-95% (easy to learn)
- Core probe (bird type) at epoch 5: ~60-70% (harder)
- **Source:** SPARE demonstrates early spurious dominance

**Metrics Loading Information:**
- Task Type: multiclass classification (2 classes)
- Library: sklearn.metrics
- Code:
```python
from sklearn.metrics import accuracy_score
accuracy = accuracy_score(y_true, y_pred)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Probe Accuracy Comparison**: Line plot showing spurious vs core probe accuracy across epochs (5, 20, 50)

#### Additional Figures (LLM Autonomous)
- Feature representation t-SNE at epoch 5 vs 50 (optional)
- Per-group probe accuracy breakdown (optional)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- `mechanism_exists`: Yes - linear probing is well-established methodology
- `mechanism_isolatable`: Yes - separate probes for spurious vs core features
- `baseline_measurable`: Yes - probe accuracies are directly comparable

### Architecture Compatibility
- ResNet-18 outputs 512-dim features from avgpool layer
- Linear probes operate on these frozen features
- No architecture modification required (analysis-only hypothesis)

### Activation Indicators
- `mechanism_log_message`: "Epoch {epoch}: Spurious probe acc = {s_acc:.3f}, Core probe acc = {c_acc:.3f}"
- `tensor_shape_change`: Features (B, 512) → Probe logits (B, 2)
- `metric_delta_expected`: spurious_acc - core_acc > 0.1 at epoch 5

### Mechanism Verification Code
```python
def verify_mechanism(results):
    """Verify simplicity bias mechanism."""
    epoch5 = results['epoch_5']
    epoch50 = results['epoch_50']
    
    # Primary check: spurious > core at epoch 5
    bias_exists = epoch5['spurious_acc'] > epoch5['core_acc']
    
    # Secondary check: core improves over training
    core_improves = epoch50['core_acc'] > epoch5['core_acc']
    
    print(f"Simplicity bias detected: {bias_exists}")
    print(f"Core feature learning: {core_improves}")
    
    return bias_exists  # Gate condition
```

### Success Criteria
- `hypothesis_support_threshold`: spurious_acc(epoch5) > core_acc(epoch5)
- `hypothesis_support_metric`: accuracy difference (spurious - core)

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `spurious_probe_acc(epoch5) > core_probe_acc(epoch5)`

---

## Appendix: Reference Implementations

### Primary References

1. **SPARE (Yang et al., AISTATS 2024)**
   - URL: https://proceedings.mlr.press/v238/yang24c.html
   - Key insight: Simplicity bias enables early spurious detection
   - Relevance: Direct theoretical foundation for H-M1

2. **DFR (Izmailov et al., NeurIPS 2022)**
   - URL: https://proceedings.neurips.cc/paper_files/paper/2022/file/fb64a552feda3d981dbe43527a80a07e-Paper-Conference.pdf
   - Key insight: Linear probes effectively measure feature quality
   - Relevance: Methodology for feature evaluation

3. **Complexity Matters (Qiu et al., 2024)**
   - URL: https://arxiv.org/html/2403.03375v2
   - Key insight: Spurious feature complexity affects learning dynamics
   - Relevance: Theoretical understanding of mechanism

### Code References

1. **Linear Probe Pattern** (PyTorch standard)
   - Freeze backbone with `requires_grad = False`
   - Extract features with `torch.no_grad()`
   - Train simple linear classifier on frozen features

2. **Understanding Intermediate Layers (Alain & Bengio, 2016)**
   - URL: https://arxiv.org/pdf/1610.01644
   - Linear separability increases monotonically with depth
   - Foundational work on probing methodology

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-12T14:30:00Z

### Workflow History for This Hypothesis
- H-E1 completed with PARTIAL_PASS (precision/recall limited by 5% base rate, not signal absence)
- H-M1 set to IN_PROGRESS for mechanism testing
- Phase 2C experiment design generated

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub + Web)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
