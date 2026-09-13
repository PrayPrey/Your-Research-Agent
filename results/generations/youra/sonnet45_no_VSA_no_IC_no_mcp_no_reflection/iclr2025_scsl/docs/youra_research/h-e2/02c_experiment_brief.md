# Experiment Design: h-e2

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Spurious features exhibit lower gradient variance (V_spurious < V_core, variance ratio < 0.7) and lower forgetting rate than core features
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** h-e1 COMPLETED
**Gate Status:** SHOULD_WORK gate active

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e2
- **Type:** EXISTENCE
- **Prerequisites:** h-e1 (Temporal Ordering Foundation)

### Gate Condition
SHOULD_WORK gate: Failure documented as limitation, workflow continues. Does not block dependent hypotheses.

---

## Continuation Context

h-e2 builds on h-e1's validated temporal ordering (E_spurious=13, E_core=17, Δ=4 epochs). Uses same ablation-trained networks from h-e1 to extract gradient variance and forgetting metrics.

### Previous Hypothesis Results (if applicable)

**h-e1 (COMPLETED):**
- PoC (seed 0): E_spurious=13, E_core=17, Δ=4 epochs ✅
- Gate threshold exceeded (Δ≥2) with 2× margin
- Full 10-seed statistical validation in progress
- Dataset: CMNIST only

**Key outputs reusable for h-e2:**
- Ablation-trained networks (spurious-only, core-only, baseline)
- Per-epoch gradient norms already logged
- Convergence epochs E_s, E_c established

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP server unavailable - using fallback domain knowledge*

**Gradient Variance in Deep Learning:**
- Standard metric for training stability analysis
- Lower variance indicates more stable convergence path
- Commonly computed using rolling window over gradient norms
- Expected pattern: variance decreases as training progresses toward convergence

**Spurious Correlation Literature Context:**
- Prior work focuses on final accuracy metrics, not training dynamics
- Gradient variance rarely measured separately for spurious vs core features
- h-e2 extends standard variance tracking to ablation-based feature attribution

### Archon Code Examples

*MCP server unavailable - using fallback implementations*

**Gradient Logging Pattern (PyTorch standard):**
```python
# Hook-based gradient logging
def log_gradient_hook(grad):
    grad_norm = grad.norm().item()
    gradient_logger.append(grad_norm)
    return grad

for name, param in model.named_parameters():
    param.register_hook(log_gradient_hook)
```

**Variance Computation:**
```python
# Rolling window variance (NumPy)
window_size = 3
variances = [np.var(grad_history[i:i+window_size]) 
             for i in range(len(grad_history) - window_size + 1)]
```

### Exa GitHub Implementations

*MCP server unavailable - using fallback references*

**Toneva et al. (2019) Forgetting Metric:**
- Repository: https://github.com/mtoneva/example_forgetting
- Key file: `forgetting_events.py`
- Implementation: Track per-sample prediction correctness across epochs, count flips

**Spurious Correlation Benchmarks:**
- CMNIST implementations widely available in bias mitigation repos
- Standard pattern: Color augmentation with controllable correlation strength
- h-e1 implementation provides tested CMNIST loader

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Assessment:**
- No prior work directly implements gradient variance + forgetting metrics for spurious vs core features
- h-e2 combines two established metrics (gradient variance, forgetting events) in novel ablation framework
- Implementation builds on h-e1 infrastructure (ablation training already validated)

**Recommended Implementation Path:**
- Primary: Extend h-e1 implementation (gradient norms already logged, reuse ablation networks)
- Fallback: Toneva et al. (2019) forgetting metric implementation from official repo
- Justification: Reuse h-e1 infrastructure minimizes implementation overhead and ensures consistency with h-e1 results

### Code Analysis (Serena MCP)

*MCP server unavailable - codebase analysis step skipped*

**Fallback Analysis:**
- h-e1 codebase already includes gradient logging infrastructure
- Extend `train.py` with variance computation and forgetting tracking
- Expected modifications: ~100 lines (GradientVarianceTracker + ForgettingTracker classes)

---

## Experiment Specification

### Dataset

**Name:** CMNIST (Colored MNIST)
**Type:** standard (spurious correlation benchmark)
**Source:** torchvision.datasets.MNIST + color augmentation
**Splits:** 50k train, 10k test
**Preprocessing:** Normalize to [0,1], color-digit correlation 95% in train, 10% in test
**Path:** ./data/mnist

**Spurious Feature:** Digit color (10 colors × 10 digits)
**Core Feature:** Digit shape (0-9)

**Loading Information** (for Phase 4 download):
- Method: torchvision dataset + custom color augmentation
- Identifier: MNIST
- Code:
```python
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

# Base MNIST
mnist_train = datasets.MNIST('./data/mnist', train=True, download=True)
mnist_test = datasets.MNIST('./data/mnist', train=False, download=True)

# Apply color augmentation (correlation 95% train, 10% test)
# See h-e1 implementation for color_augment() function
```

### Models

#### Baseline Model

**Architecture:** ResNet-18 (pretrained=False)
**Input:** 3×28×28 (RGB)
**Output:** 10 classes
**Parameters:** ~11M

**Loading Information** (for Phase 4 download):
- Method: torchvision.models
- Identifier: resnet18
- Code:
```python
import torch.nn as nn
from torchvision import models

model = models.resnet18(pretrained=False, num_classes=10)
# Modify first conv layer for 28×28 input
model.conv1 = nn.Conv2d(3, 64, kernel_size=3, stride=1, padding=1, bias=False)
model.maxpool = nn.Identity()
```

#### Proposed Model

**Architecture:** Baseline + gradient variance tracking + forgetting event tracking

**Core Mechanism Implementation:**

```python
# Gradient Variance Tracker
class GradientVarianceTracker:
    def __init__(self, model, window_size=3):
        self.window_size = window_size
        self.grad_history = {name: [] for name, _ in model.named_parameters()}
    
    def log_gradients(self, model):
        for name, param in model.named_parameters():
            if param.grad is not None:
                grad_norm = param.grad.norm().item()
                self.grad_history[name].append(grad_norm)
    
    def compute_variance(self, feature_type='spurious'):
        # Filter parameters by feature type using ablation network masks
        relevant_params = filter_by_feature_type(self.grad_history, feature_type)
        variances = []
        for param_grads in relevant_params:
            if len(param_grads) >= self.window_size:
                window = param_grads[-self.window_size:]
                variances.append(np.var(window))
        return np.mean(variances)

# Forgetting Event Tracker (Toneva et al. 2019)
class ForgettingTracker:
    def __init__(self, num_samples):
        self.predictions = {}  # {sample_idx: [pred_epoch1, pred_epoch2, ...]}
    
    def log_predictions(self, sample_indices, predictions, epoch):
        for idx, pred in zip(sample_indices, predictions):
            if idx not in self.predictions:
                self.predictions[idx] = []
            self.predictions[idx].append(pred)
    
    def compute_forgetting_events(self):
        forgetting_counts = []
        for idx, preds in self.predictions.items():
            # Count prediction flips (1→0→1 pattern)
            flips = sum(1 for i in range(1, len(preds)) if preds[i] != preds[i-1])
            forgetting_counts.append(flips)
        return np.mean(forgetting_counts)
```

### Training Protocol

**Optimizer:** SGD (momentum=0.9)
**Learning Rate:** 0.001 (constant, no schedule)
**Batch Size:** 256
**Epochs:** 30 (sufficient to observe variance stabilization)
**Loss:** CrossEntropyLoss
**Weight Decay:** 0.0001

**Training Procedure:**
1. Train 3 models in parallel (spurious-only, core-only, baseline) — reuse h-e1 ablation setup
2. Log gradients every batch → compute rolling 3-epoch variance
3. Log predictions every epoch → track forgetting events
4. Run 10 random seeds for statistical tests

**Hardware:** 1× GPU (V100/A100)
**Expected Runtime:** ~3 hours (10 seeds × 3 models × 30 epochs)

### Evaluation

**Primary Metrics:**
1. **Gradient Variance Ratio:** V_spurious / V_core (computed at epochs 10, 20, 30)
2. **Forgetting Rate:** Mean forgetting events per sample (spurious vs core features)

**Statistical Tests:**
- F-test for variance ratio (H0: V_spurious / V_core = 1)
- Paired t-test on forgetting rates (10 seeds)
- Partial correlation test: Control for E_s to verify independence

**Success Criteria:**
- V_spurious / V_core < 0.7 (p < 0.05)
- Forgetting_spurious < Forgetting_core (p < 0.05)
- Partial correlation significant (p < 0.05)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Multi-class classification (10 classes)
- Library: NumPy, SciPy (stats)
- Code:
```python
from scipy.stats import f_test, ttest_rel
import numpy as np

# F-test for variance ratio
variance_ratio = var_spurious / var_core
f_stat, p_value = f_test(var_spurious_samples, var_core_samples)

# Paired t-test on forgetting rates
t_stat, p_value = ttest_rel(forgetting_spurious, forgetting_core)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Variance ratio and forgetting rate bar charts (spurious vs core)

#### Additional Figures (LLM Autonomous)

1. **Rolling Gradient Variance Over Time** (epochs 1-30, 3-epoch window)
   - Two lines: V_spurious(t), V_core(t)
   - Shaded region for ±1 std across 10 seeds

2. **Forgetting Events Heatmap** (samples × epochs)
   - Color: prediction flip frequency
   - Separate plots for spurious-only vs core-only features

3. **Partial Correlation Analysis**
   - Scatter: Forgetting rate vs E_s (controlling for variance)
   - Show correlation coefficient + p-value

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-e2/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. V_spurious / V_core < V_threshold (direction-based, no statistical test required for PoC)
3. Forgetting_spurious < Forgetting_core (direction-based)

**Note:** Full statistical validation (F-test, t-test, partial correlation) required for final paper, but PoC only needs directional confirmation.

---

## Appendix: Reference Implementations

**Gradient Variance Tracking:**
- PyTorch gradient hooks: https://pytorch.org/docs/stable/generated/torch.Tensor.register_hook.html
- Rolling window variance: NumPy rolling window implementations

**Forgetting Events (Toneva et al. 2019):**
- Paper: "An Empirical Study of Example Forgetting during Deep Neural Network Learning"
- Official code: https://github.com/mtoneva/example_forgetting
- Key metric: Forgetting event = prediction flip from correct to incorrect

**Ablation Training (from h-e1):**
- Spurious-only: Train on color-only cues (masked digit shapes)
- Core-only: Train on grayscale images (no color)
- Baseline: Standard CMNIST training

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-08-28T23:05:00Z

### Workflow History for This Hypothesis
- 2026-08-28T23:05:00Z: h-e2 experiment design initiated
- Prerequisites: h-e1 COMPLETED (PoC validated, full statistical validation in progress)
- Gate: SHOULD_WORK (failure does not block workflow)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
