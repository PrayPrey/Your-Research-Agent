# Experiment Design: H-M2

**Date:** 2026-08-19
**Author:** PrayPrey
**Hypothesis Statement:** Post-crystallization, classifier commits to spurious features and does not revert
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** - Tests irreversibility of classifier commitment.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (H-M1 PASS - gradient starvation mechanism validated)
**Gate Status:** MUST_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M2
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (self-reinforcing feedback loop)

### Gate Condition
**MUST_WORK:** Spurious feature probe accuracy must not decrease post-crystallization. If spurious weights decrease or core feature recovery is observed, hypothesis fails and we EXPLORE late reversal possibility.

---

## Continuation Context

H-M1 validated that gradient starvation creates self-reinforcing feedback at crystallization point. H-M2 now tests whether this commitment is permanent: does the classifier remain locked to spurious features, or can it recover?

### Previous Hypothesis Results (if applicable)
- **H-E1:** PASS - Crystallization zone exists, detectable via d²WGA/dt² negative peak in first 50% of training
- **H-M1:** PASS - Gradient ratio inflection correlates with WGA acceleration, confirming self-reinforcing feedback mechanism

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP unavailable - using established literature:*

1. **Kirichenko et al. 2023 "Last Layer Retraining"**: Demonstrated that both spurious and core features are learned in representations, but classifier weights favor spurious features. Key insight: The representation contains sufficient information for both features, but the linear classifier commits to spurious.

2. **Linear Probing for Feature Analysis**: Standard technique from transfer learning literature (Alain & Bengio 2017). Freeze backbone, train linear classifier on top to measure feature quality.

3. **Sagawa et al. 2020 "Group DRO"**: Established WGA as metric for spurious feature reliance. Showed ERM models converge to spurious solutions without intervention.

### Archon Code Examples

*MCP unavailable - reference implementations:*

```python
# Linear probe pattern from pytorch-linear-probe
class LinearProbe(nn.Module):
    def __init__(self, input_dim, num_classes):
        super().__init__()
        self.fc = nn.Linear(input_dim, num_classes)
    
    def forward(self, x):
        return self.fc(x)

# Feature extraction from frozen model
def extract_features(model, dataloader, device):
    model.eval()
    features, labels = [], []
    with torch.no_grad():
        for x, y in dataloader:
            feat = model.features(x.to(device))  # Before final classifier
            features.append(feat.cpu())
            labels.append(y)
    return torch.cat(features), torch.cat(labels)
```

### Exa GitHub Implementations

*MCP unavailable - known repositories:*

1. **p-lambda/wilds** (github.com/p-lambda/wilds): WILDS benchmark suite with Waterbirds, CelebA datasets and evaluation infrastructure
2. **kohpangwei/group_DRO** (github.com/kohpangwei/group_DRO): Reference Group DRO implementation with linear probe utilities
3. **PolinaKirichenko/deep_feature_reweighting** (github.com/PolinaKirichenko/deep_feature_reweighting): Last-layer retraining code demonstrating probe-based feature analysis

### 🎯 Implementation Priority Assessment

**CRITICAL: Linear probing methodology is well-established**

**Primary Source:** PolinaKirichenko/deep_feature_reweighting
- Contains exact methodology: freeze backbone, train linear probes on group-balanced subset
- Proven to work on Waterbirds/CelebA

**Recommended Implementation Path:**
- Primary: Adapt linear probe code from deep_feature_reweighting
- Fallback: Custom implementation following Alain & Bengio 2017 methodology
- Justification: Author's implementation is reference standard for spurious feature analysis

### Code Analysis (Serena MCP)

*Serena MCP unavailable - using prior hypothesis code analysis:*

From H-E1/H-M1 validation, the following components exist:
- WGA tracking module (from H-E1)
- Gradient analysis module (from H-M1)
- Checkpoint loading infrastructure

New components needed:
- Linear probe trainer
- Feature extractor (hook on penultimate layer)
- Temporal probe accuracy tracker

---

## Experiment Specification

### Dataset

**Primary:** Waterbirds (from WILDS)
- **Type:** standard
- **Source:** WILDS benchmark (p-lambda/wilds)
- **Train:** 4,795 samples (majority: landbirds+land, minority: waterbirds+land)
- **Val:** 500 samples per group (balanced)
- **Test:** ~5,794 samples (standard test split, full evaluation)
- **Groups:** 4 groups based on (bird_type, background)
- **Preprocessing:** ImageNet normalization, 224x224 resize

**Loading Information** (for Phase 4 download):
- Method: Python package
- Identifier: wilds.get_dataset("waterbirds", download=True)
- Code:
```python
from wilds import get_dataset
from wilds.common.data_loaders import get_train_loader, get_eval_loader

dataset = get_dataset(dataset="waterbirds", download=True)
train_data = dataset.get_subset("train")
val_data = dataset.get_subset("val")
test_data = dataset.get_subset("test")

# DataLoaders
train_loader = get_train_loader("standard", train_data, batch_size=128)
val_loader = get_eval_loader("standard", val_data, batch_size=128)
test_loader = get_eval_loader("standard", test_data, batch_size=128)
```

### Models

#### Baseline Model

**Pre-crystallization Checkpoint** (from H-E1/H-M1):
- Architecture: ResNet-50 (pretrained ImageNet)
- Checkpoint: Epoch at crystallization point (detected by H-E1 d²WGA/dt² peak)
- Purpose: Reference state before commitment

**Loading Information** (for Phase 4 download):
- Method: PyTorch checkpoint from H-M1 outputs
- Identifier: `h-m1/code/checkpoints/epoch_{crystallization_epoch}.pt`
- Code:
```python
import torch
import torchvision.models as models

model = models.resnet50(pretrained=True)
model.fc = nn.Linear(model.fc.in_features, 2)  # Binary classification

# Load from H-M1 crystallization checkpoint
checkpoint = torch.load(f"h-m1/code/checkpoints/epoch_{crystallization_epoch}.pt")
model.load_state_dict(checkpoint['model_state_dict'])
```

#### Proposed Model

**Architecture:** ResNet-50 with Linear Probes for Feature Analysis

**Core Mechanism Implementation:**

```python
# Core Mechanism: Post-Crystallization Feature Commitment Tracking
# Tests whether spurious feature dominance is irreversible

class FeatureProbeAnalyzer:
    """Tracks linear probe accuracy on spurious vs core features
    across training epochs post-crystallization."""
    
    def __init__(self, model, crystallization_epoch, hidden_dim=2048):
        self.model = model
        self.crystallization_epoch = crystallization_epoch
        self.hidden_dim = hidden_dim
        
        # Probes for spurious feature (background) and core feature (bird)
        self.spurious_probe = nn.Linear(hidden_dim, 2)  # land/water
        self.core_probe = nn.Linear(hidden_dim, 2)  # landbird/waterbird
        
        # Track accuracy over epochs
        self.spurious_acc_history = []
        self.core_acc_history = []
    
    def extract_penultimate_features(self, dataloader):
        """Extract features from layer before final classifier."""
        features, spurious_labels, core_labels = [], [], []
        self.model.eval()
        
        # Hook on avgpool layer
        activation = {}
        def hook(module, input, output):
            activation['features'] = output.squeeze()
        
        handle = self.model.avgpool.register_forward_hook(hook)
        
        with torch.no_grad():
            for x, y, metadata in dataloader:
                _ = self.model(x.cuda())
                features.append(activation['features'].cpu())
                # metadata contains group info: (bird_type, background)
                core_labels.append(metadata[:, 0])  # Bird type
                spurious_labels.append(metadata[:, 1])  # Background
        
        handle.remove()
        return (torch.cat(features), 
                torch.cat(spurious_labels), 
                torch.cat(core_labels))
    
    def train_probes(self, features, spurious_labels, core_labels):
        """Train linear probes on extracted features."""
        # Train spurious feature probe
        self.spurious_probe.train()
        optimizer_s = torch.optim.SGD(self.spurious_probe.parameters(), lr=0.01)
        for _ in range(100):  # Quick probe training
            logits = self.spurious_probe(features.cuda())
            loss = F.cross_entropy(logits, spurious_labels.cuda())
            optimizer_s.zero_grad()
            loss.backward()
            optimizer_s.step()
        
        # Train core feature probe
        self.core_probe.train()
        optimizer_c = torch.optim.SGD(self.core_probe.parameters(), lr=0.01)
        for _ in range(100):
            logits = self.core_probe(features.cuda())
            loss = F.cross_entropy(logits, core_labels.cuda())
            optimizer_c.zero_grad()
            loss.backward()
            optimizer_c.step()
    
    def evaluate_probes(self, features, spurious_labels, core_labels):
        """Evaluate probe accuracy."""
        self.spurious_probe.eval()
        self.core_probe.eval()
        
        with torch.no_grad():
            spurious_pred = self.spurious_probe(features.cuda()).argmax(1)
            core_pred = self.core_probe(features.cuda()).argmax(1)
        
        spurious_acc = (spurious_pred == spurious_labels.cuda()).float().mean()
        core_acc = (core_pred == core_labels.cuda()).float().mean()
        
        return spurious_acc.item(), core_acc.item()
    
    def analyze_commitment(self, checkpoints_dir, epochs_post):
        """Main analysis: track probe accuracy across post-crystallization epochs."""
        for epoch in range(self.crystallization_epoch, 
                          self.crystallization_epoch + epochs_post):
            # Load checkpoint
            ckpt = torch.load(f"{checkpoints_dir}/epoch_{epoch}.pt")
            self.model.load_state_dict(ckpt['model_state_dict'])
            
            # Extract features and train probes
            feats, s_labels, c_labels = self.extract_penultimate_features(
                self.val_loader)
            self.train_probes(feats, s_labels, c_labels)
            
            # Evaluate
            s_acc, c_acc = self.evaluate_probes(feats, s_labels, c_labels)
            self.spurious_acc_history.append(s_acc)
            self.core_acc_history.append(c_acc)
        
        return self.spurious_acc_history, self.core_acc_history
    
    def check_commitment(self):
        """Check if classifier committed (spurious doesn't decrease)."""
        # Success: spurious probe accuracy monotonically non-decreasing
        # OR stable within noise margin (±2%)
        if len(self.spurious_acc_history) < 2:
            return None
        
        first_post = self.spurious_acc_history[0]
        final = self.spurious_acc_history[-1]
        
        # Commitment = spurious accuracy does not decrease significantly
        committed = (final >= first_post - 0.02)
        
        # Core suppression = core accuracy stays low
        core_suppressed = all(acc < 0.85 for acc in self.core_acc_history)
        
        return {"committed": committed, "core_suppressed": core_suppressed}
```

### Training Protocol

**Phase 1: Load checkpoints from H-M1**
- Use crystallization epoch identified by H-E1 (d²WGA/dt² peak)
- Load checkpoints: crystallization_epoch to final_epoch

**Phase 2: Feature Extraction**
- Hook penultimate layer (avgpool output, 2048-dim for ResNet-50)
- Extract features for all validation samples at each checkpoint

**Phase 3: Linear Probe Training**
- Train spurious feature probe (predict background: land/water)
- Train core feature probe (predict bird type: landbird/waterbird)
- Use SGD, lr=0.01, 100 iterations per probe

**Phase 4: Temporal Analysis**
- Track probe accuracy across epochs post-crystallization
- Measure: spurious_acc(t), core_acc(t) for t > crystallization_epoch

**Hyperparameters:**
- Probe optimizer: SGD
- Probe learning rate: 0.01
- Probe training iterations: 100
- Epochs analyzed: crystallization_epoch to 100 (Waterbirds standard)

### Evaluation

**Primary Metrics:**
1. **Spurious Probe Accuracy Trend:** Does spurious feature probe accuracy decrease post-crystallization?
2. **Core Probe Accuracy Trend:** Does core feature probe accuracy increase (recovery) post-crystallization?

**Success Criteria (PoC):**
- **PRIMARY:** Spurious probe accuracy does NOT decrease by >2% post-crystallization
- **SECONDARY:** Core probe accuracy remains suppressed (< 85% at final epoch)

**Gate Condition:**
```
IF spurious_acc[final] >= spurious_acc[crystallization] - 0.02:
    PASS (Classifier committed to spurious features)
ELSE:
    FAIL → EXPLORE late reversal possibility
```

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification accuracy
- Library: PyTorch (manual accuracy computation)
- Code:
```python
def compute_accuracy(predictions, labels):
    return (predictions.argmax(1) == labels).float().mean().item()
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Spurious vs Core probe accuracy over epochs (post-crystallization timeline)

#### Additional Figures (LLM Autonomous)

1. **Temporal Probe Accuracy Plot:**
   - X-axis: Epoch (from crystallization to final)
   - Y-axis: Probe accuracy
   - Two lines: Spurious probe (expected flat/increasing), Core probe (expected flat/suppressed)
   - Vertical line at crystallization epoch

2. **Commitment Heatmap:**
   - Rows: Checkpoints (epochs)
   - Columns: Group (by bird_type × background)
   - Color: Probe accuracy

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. Spurious probe accuracy does NOT decrease post-crystallization (commitment confirmed)
3. Core probe accuracy remains suppressed (no late recovery)

---

## Appendix: Reference Implementations

### Key Papers

1. **Kirichenko, P., Izmailov, P., & Wilson, A. G. (2023).** Last Layer Re-Training is Sufficient for Robustness to Spurious Correlations. ICLR 2023.
   - URL: https://arxiv.org/abs/2204.02937
   - Relevance: Establishes linear probe methodology for spurious feature analysis

2. **Sagawa, S., Koh, P. W., Hashimoto, T. B., & Liang, P. (2020).** Distributionally Robust Neural Networks. ICLR 2020.
   - URL: https://arxiv.org/abs/1911.08731
   - Relevance: Waterbirds benchmark, WGA metric definition

3. **Alain, G., & Bengio, Y. (2017).** Understanding intermediate layers using linear classifier probes. ICLR Workshop.
   - URL: https://arxiv.org/abs/1610.01644
   - Relevance: Linear probing methodology foundation

### GitHub Repositories

1. **PolinaKirichenko/deep_feature_reweighting**
   - URL: https://github.com/PolinaKirichenko/deep_feature_reweighting
   - Files: `train_probe.py`, `utils/data_utils.py`
   - Usage: Linear probe training on frozen representations

2. **p-lambda/wilds**
   - URL: https://github.com/p-lambda/wilds
   - Files: `wilds/datasets/waterbirds_dataset.py`
   - Usage: Dataset loading, group metadata access

3. **kohpangwei/group_DRO**
   - URL: https://github.com/kohpangwei/group_DRO
   - Files: `data/waterbirds_dataset.py`, `models/resnet.py`
   - Usage: Reference implementation for Waterbirds training

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-19

### Workflow History for This Hypothesis
- 2026-08-19: H-M2 set to IN_PROGRESS (external loop)
- 2026-08-19: Phase 2C experiment design started
- Depends on: H-M1 (PASS - gradient starvation mechanism validated)

---

*MCP Tools Used: None available (batch mode without MCP)*
*All specifications grounded in established literature and prior hypothesis results*
*Next Phase: Phase 3 - Implementation Planning*
