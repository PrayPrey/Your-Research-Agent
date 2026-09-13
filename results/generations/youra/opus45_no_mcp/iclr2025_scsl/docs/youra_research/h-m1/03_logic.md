# Logic: H-M1 Gradient Starvation Mechanism (MECHANISM/FULL)

Applied: PyTorch `register_full_backward_hook` pattern for classifier-layer gradient capture
Applied: Rolling-window second-derivative peak detection (reused from h-e1, extended to gradient ratio)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (h-e1)
**Status**: API signatures verified from actual h-e1 code (not spec)
**Analyzed Path**: `docs/youra_research/h-e1/code/{data,model,evaluate,detector,train,config}.py`
**Relevant Symbols**:
- `data.get_loaders(name, batch_size) -> dict[str, DataLoader]`
- `model.build_resnet50(num_classes, pretrained) -> nn.Module`
- `evaluate.evaluate_epoch(model, loader, device) -> tuple[float, dict]`
- `evaluate.compute_wga(predictions, labels, groups) -> float`
- `detector.CrystallizationDetector(smoothing_window).log_epoch/compute_second_derivative/detect_crystallization_peak`
- `config.Config` dataclass, `CONFIG` instance

**Discrepancy vs spec**: PRD/brief pseudo-code shows `compute_wga(model, dataloader, group_ids)` and `compute_second_derivative(wga_curve, window=5)` as free functions — actual code differs: `compute_wga(predictions, labels, groups)` is prediction-based, and second-derivative logic lives inside `CrystallizationDetector` class, not a standalone function. Use actual class-based API below.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/data.py (ACTUAL CODE)
def get_loaders(name: str, batch_size: int = 128) -> dict[str, DataLoader]:
    """Returns {'train','val','test'}. Batch: (x [B,3,224,224], y [B], metadata [B,K])."""
    ...

# From: h-e1/code/model.py (ACTUAL CODE)
def build_resnet50(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """ResNet-50, model.fc = Linear(2048, num_classes)."""
    ...

# From: h-e1/code/evaluate.py (ACTUAL CODE)
def evaluate_epoch(model, loader, device) -> tuple:
    """Returns (wga: float, group_acc: dict[int, float])."""
    ...

# From: h-e1/code/detector.py (ACTUAL CODE)
class CrystallizationDetector:
    def __init__(self, smoothing_window: int = 5): ...
    def log_epoch(self, wga: float) -> None: ...
    def compute_second_derivative(self) -> np.ndarray: ...
    def detect_crystallization_peak(self, threshold: float = -0.01) -> tuple:
        """Returns (peak_epoch: int, peak_value: float, is_significant: bool)."""
        ...

# From: h-e1/code/config.py (ACTUAL CODE)
from dataclasses import dataclass
@dataclass
class Config:
    lr: float = 1e-3
    momentum: float = 0.9
    weight_decay: float = 1e-4
    batch_size: int = 128
    epochs_waterbirds: int = 100
    smoothing_window: int = 5
    detection_threshold: float = -0.01
    # ... (see h-e1/code/config.py for full fields)
```

**Verified from**: `h-e1/code/*.py` (actual implementation).

---

## A-1: GradientTracker Mechanism [Complexity: 12, Budget: 12]

**Applied**: PyTorch backward-hook gradient capture pattern

### API Signatures

```python
# gradient_tracker.py
import torch
from torch import nn, Tensor

class GradientTracker:
    """Tracks per-group gradient norms on model.fc via backward hook."""

    def __init__(self, model: nn.Module, group_indices: dict[int, list[int]] | None = None):
        """group_indices optional pre-computed {group_id: [sample_idx,...]}; not required for batch-level use."""
        self.gradient_history: list[dict] = []
        self.current_gradients: Tensor | None = None  # [B, num_classes], set each backward
        self._hook_handle = model.fc.register_full_backward_hook(self._gradient_hook)

    def _gradient_hook(self, module: nn.Module, grad_input: tuple, grad_output: tuple) -> None:
        """grad_output[0]: [B, C] gradient w.r.t. fc output logits."""
        self.current_gradients = grad_output[0].detach().clone()

    def compute_group_gradient_ratio(self, batch_groups: Tensor) -> float | None:
        """batch_groups: [B] long tensor of group ids (0..3).
        Returns minority(group 3) / majority(group 0) gradient-norm ratio, or None if no grad captured."""
        ...

    def log_epoch_gradients(self, epoch: int, ratio: float) -> None:
        """Append {'epoch': epoch, 'gradient_ratio': ratio} to gradient_history."""
        ...

    def remove(self) -> None:
        """Detach hook (call at end of training)."""
        self._hook_handle.remove()
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| grad_output[0] | [B, 2] | fc-layer output gradient (Waterbirds: 2 classes) |
| batch_groups | [B] | long, values 0-3 |
| current_gradients | [B, 2] | cached per backward call |

### Pseudo-code

```
compute_group_gradient_ratio(batch_groups):
    if self.current_gradients is None: return None
    grad = self.current_gradients                      # [B, 2]
    group_norms = {}
    for g in unique(batch_groups):
        mask = (batch_groups == g)                      # [B]
        if mask.sum() > 0:
            group_norms[g] = grad[mask].norm().item()   # scalar L2 norm over masked rows
    minority = group_norms.get(3, 1e-8)
    majority = group_norms.get(0, 1e-8)
    return minority / (majority + 1e-8)
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Hook registration | `__init__`: register `_gradient_hook` on `model.fc`, matches h-e1 `build_resnet50` output layer |
| L-1-2 | Group ratio calc | `compute_group_gradient_ratio`: mask by group id, L2 norm, minority/majority ratio (per PRD FR-3) |
| L-1-3 | Epoch logging | `log_epoch_gradients` + `remove`: history storage and hook cleanup |

---

## A-2: Training Loop Integration [Complexity: 10, Budget: 10]

**Applied**: Extend h-e1 `train_one_epoch`/`train` loop with per-batch gradient tracking

### API Signatures

```python
# train.py (h-m1)
import torch
from torch import nn
from torch.utils.data import DataLoader
from gradient_tracker import GradientTracker

# Reused from h-e1:
from h_e1.data import get_loaders
from h_e1.model import build_resnet50
from h_e1.evaluate import evaluate_epoch
from h_e1.detector import CrystallizationDetector

def train_one_epoch_tracked(
    model: nn.Module, loader: DataLoader, optimizer: torch.optim.Optimizer,
    criterion: nn.Module, device: str, tracker: GradientTracker
) -> tuple[float, float]:
    """One epoch ERM training + gradient ratio capture.
    Returns (avg_train_loss, avg_epoch_gradient_ratio)."""
    ...

def train_with_gradient_tracking(dataset_name: str, cfg: "Config") -> dict:
    """Full run: WGA history (h-e1 detector) + gradient ratio history (GradientTracker).
    Returns {'wga_history': list[float], 'gradient_ratio_history': list[float],
             'group_acc_history': list[dict]}."""
    ...
```

### Pseudo-code

```
1. model = build_resnet50(); model.to(device)
2. optimizer = SGD(model.parameters(), lr=cfg.lr, momentum=cfg.momentum, weight_decay=cfg.weight_decay)
3. scheduler = MultiStepLR(optimizer, milestones=[30,60], gamma=0.1)
4. criterion = CrossEntropyLoss()
5. loaders = get_loaders(dataset_name, cfg.batch_size)
6. tracker = GradientTracker(model)
7. detector = CrystallizationDetector(smoothing_window=cfg.smoothing_window)
8. for epoch in range(cfg.epochs_waterbirds):
     model.train()
     epoch_ratios = []
     for x, y, metadata in loaders['train']:
         x, y, groups = x.to(device), y.to(device), metadata[:,0].to(device)
         optimizer.zero_grad()
         logits = model(x)                          # [B, 2]
         loss = criterion(logits, y)
         loss.backward()                             # triggers _gradient_hook -> current_gradients
         ratio = tracker.compute_group_gradient_ratio(groups)
         if ratio is not None: epoch_ratios.append(ratio)
         optimizer.step()
     scheduler.step()
     avg_ratio = mean(epoch_ratios) if epoch_ratios else 0.0
     tracker.log_epoch_gradients(epoch, avg_ratio)
     wga, group_acc = evaluate_epoch(model, loaders['val'], device)
     detector.log_epoch(wga)
     torch.save(model.state_dict(), f"ckpt_epoch{epoch}.pt")
9. tracker.remove()
10. return {'wga_history': detector.wga_history,
            'gradient_ratio_history': [h['gradient_ratio'] for h in tracker.gradient_history],
            'group_acc_history': group_acc_history}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | Tracked epoch loop | `train_one_epoch_tracked`: forward/backward/step + per-batch ratio capture |
| L-2-2 | Full run orchestration | `train_with_gradient_tracking`: wires GradientTracker + CrystallizationDetector + checkpointing |
| L-2-3 | Scheduler | MultiStepLR(milestones=[30,60], gamma=0.1) per PRD FR-2 |

---

## A-3: Correlation Analysis [Complexity: 9, Budget: 9]

**Applied**: Standard PyTorch/scipy pattern — inflection via 2nd-derivative acceleration, Pearson r

### API Signatures

```python
# analysis.py
import numpy as np
from scipy.stats import pearsonr
from scipy.ndimage import uniform_filter1d

def detect_gradient_inflection(gradient_history: list[float], smoothing_window: int = 5) -> int:
    """Epoch index where d(ratio)/dt shows max negative acceleration (mirrors CrystallizationDetector logic)."""
    ...

def compute_correlation(inflection_epochs: list[int], wga_peak_epochs: list[int]) -> tuple[float, float]:
    """Pearson (r, p_value) between gradient inflection epoch(s) and WGA crystallization peak epoch(s)."""
    ...
```

### Pseudo-code

```
detect_gradient_inflection(ratio_history, smoothing_window):
    ratio = array(ratio_history)
    if len(ratio) < smoothing_window: return 0
    smoothed = uniform_filter1d(ratio, size=smoothing_window)
    d1 = gradient(smoothed)
    d2 = gradient(d1)
    midpoint = max(1, len(d2)//2)          # search first half (PRD: inflection < 50% training)
    return int(argmin(d2[:midpoint]))       # most negative acceleration = starvation onset

compute_correlation(inflection_epochs, wga_peak_epochs):
    r, p = pearsonr(inflection_epochs, wga_peak_epochs)
    return r, p
```

**Note**: single-seed run (PRD Section 9) — `inflection_epochs`/`wga_peak_epochs` are single-element lists unless multi-seed ablation added; `pearsonr` requires len>=2, so correlation is computed across available checkpoints/epochs pairs (e.g., per-dataset if both waterbirds runs available) per experiment brief's temporal-precedence check.

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Inflection detection | `detect_gradient_inflection`: reuse h-e1 smoothing/2nd-derivative pattern on gradient ratio |
| L-3-2 | Correlation calc | `compute_correlation`: `scipy.stats.pearsonr` wrapper, returns (r, p) |
| L-3-3 | Gate check | Combine `detect_gradient_inflection` + `CrystallizationDetector.detect_crystallization_peak` outputs, assert r>0.7 and inflection_epoch < 0.5*n_epochs (PRD FR-5/Section 6) |

---

## A-4: Visualization [Complexity: 6, Budget: 6]

**Applied**: matplotlib dual-axis + scatter patterns

### API Signatures

```python
# visualize.py
import matplotlib.pyplot as plt

def plot_gate_comparison(inflection_epoch: int, wga_peak_epoch: int, r: float, p: float, save_path: str) -> None:
    """Required gate figure: bar/marker comparison of inflection vs WGA peak timing."""
    ...

def plot_gradient_timeline(gradient_ratio_history: list[float], inflection_epoch: int, save_path: str) -> None:
    ...

def plot_wga_gradient_overlay(wga_history: list[float], gradient_ratio_history: list[float], save_path: str) -> None:
    """Dual-axis: WGA (left y) vs gradient ratio (right y) over epochs."""
    ...

def plot_per_group_gradient_norms(group_norm_history: list[dict[int, float]], save_path: str) -> None:
    """One line per group id (0-3)."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | Required gate figure | `plot_gate_comparison` -> `figures/gate_comparison.png` |
| L-4-2 | Secondary figures | timeline, overlay, per-group norms -> `figures/*.png` |

---

## Total Subtasks: 11/30 budget used (FULL tier)
