---
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
phase: Phase 3
generated_at: '2026-03-16'
---

# Logic: H-E1
## Normalized Gradient Norm as Minority Group Proxy (Existence PoC)

**Applied: No domain-specific matches in Archon KB (similarity 0.33–0.47, diffusion/distributed content only) — standard PyTorch register_forward_hook and ERM training patterns used from PyTorch docs**

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: No existing codebase — green-field project
**Analyzed Path**: N/A
**Relevant Symbols**: None — new implementation

---

## A-2: Model + Analyzer [Complexity: 12, Budget: 2 subtasks]

### API Signatures

```python
# src/model.py
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import Tensor
from torchvision import models

def get_model(device: torch.device) -> nn.Module:
    """ResNet-50 pretrained, fc replaced with Linear(2048, 2). BN in train mode."""
    model = models.resnet50(pretrained=True)
    model.fc = nn.Linear(2048, 2)
    return model.to(device)


class GradientNormAnalyzer:
    """Vectorized per-sample gradient norm via FC forward hook + outer-product decomp."""

    def __init__(self, model: nn.Module) -> None:
        """Register forward hook on model.fc; initialize features cache."""
        self.model = model
        self.features: dict[str, Tensor] = {}
        self._hook_handle = None
        self._register_hooks()

    def _register_hooks(self) -> None:
        # hook captures input[0] of model.fc -> self.features['fc_input']: (B, 2048) detached CPU
        def _hook(module, input, output):
            self.features['fc_input'] = input[0].detach().cpu()
        self._hook_handle = self.model.fc.register_forward_hook(_hook)

    def compute_batch_norms(
        self,
        images: Tensor,    # (B, 3, 224, 224) — on device
        labels: Tensor,    # (B,) — long, on device
    ) -> tuple[Tensor, Tensor, Tensor]:
        """
        Single forward pass, outer-product decomposition. No per-sample backward.
        Returns: g_raw (B,), g_tilde (B,), h_norm (B,) — all CPU float32.
        """
        with torch.no_grad():
            logits = self.model(images)                        # (B, 2)

        h = self.features['fc_input'].cpu()                    # (B, 2048)
        p = F.softmax(logits.cpu(), dim=1)                     # (B, 2)
        y_oh = F.one_hot(labels.cpu(), num_classes=2).float()  # (B, 2)
        residual = p - y_oh                                    # (B, 2)
        g_tilde = residual.norm(dim=1)                         # (B,)
        h_norm = h.norm(dim=1)                                 # (B,)
        g_raw = g_tilde * h_norm                               # (B,)
        return g_raw, g_tilde, h_norm

    def clear(self) -> None:
        """Clear self.features dict between batches."""
        self.features.clear()
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| images | (B, 3, 224, 224) | Input batch on device |
| labels | (B,) | Long int class labels |
| h = features['fc_input'] | (B, 2048) | FC input features from hook |
| logits | (B, 2) | FC output |
| p | (B, 2) | softmax(logits) |
| y_oh | (B, 2) | one_hot(labels, 2).float() |
| residual | (B, 2) | p - y_oh |
| g_tilde | (B,) | residual.norm(dim=1) — normalized grad norm |
| h_norm | (B,) | h.norm(dim=1) — feature L2 norm |
| g_raw | (B,) | g_tilde * h_norm — raw FC weight grad norm |

### Pseudo-code: compute_batch_norms()

```
1. with torch.no_grad():
       logits = model(images)               # (B, 2), hook fires -> features['fc_input']
2. h = features['fc_input']                 # (B, 2048) — already on CPU
3. p = softmax(logits, dim=1)               # (B, 2)
4. y_oh = one_hot(labels, 2).float()        # (B, 2)
5. residual = p - y_oh                      # (B, 2)
6. g_tilde = residual.norm(dim=1)           # (B,) <- g_tilde_i = ||p_i - y_i_oh||
7. h_norm  = h.norm(dim=1)                  # (B,) <- ||h(x_i)||
8. g_raw   = g_tilde * h_norm               # (B,) <- ||∇_W l_i||
9. return g_raw, g_tilde, h_norm
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| S-A-2-1 | GradientNormAnalyzer | _register_hooks() on model.fc + compute_batch_norms() outer-product decomp |
| S-A-2-2 | get_model + BN mode | ResNet-50 pretrained, fc replacement; BN train mode during ERM, eval mode during collection |

---

## A-3: Training Loop [Complexity: 11, Budget: 2 subtasks]

### API Signatures

```python
# src/train.py
import torch
import torch.nn as nn
import numpy as np
from torch import Tensor
from torch.utils.data import DataLoader
from torch.optim import Optimizer
from src.model import GradientNormAnalyzer

def set_seed(seed: int = 1) -> None:
    """Fix torch, numpy, random seeds + cudnn deterministic."""
    ...

def train_epoch(
    model: nn.Module,
    loader: DataLoader,       # train_shuffle (shuffle=True)
    optimizer: Optimizer,
    device: torch.device,
) -> dict[str, float]:
    """
    Standard ERM forward+backward+step. BN stays in train mode.
    Returns: {'loss': float, 'acc': float}
    """
    ...

def collect_gradnorms(
    model: nn.Module,
    analyzer: GradientNormAnalyzer,
    loader: DataLoader,       # train_ordered (shuffle=False), 4795 samples
    device: torch.device,
    epoch: int,
    output_dir: str,          # e.g. 'outputs/h-e1/'
) -> dict[str, np.ndarray]:
    """
    model.eval() pass over full train set. Saves gradnorm_epoch_{epoch}.npz.
    Returns keys: g_raw, g_tilde, h_norm, sample_indices, group_labels, class_labels.
    All arrays shape (4795,).
    """
    ...
```

### Tensor Shapes (collect_gradnorms output)

| Key | Shape | dtype |
|-----|-------|-------|
| g_raw | (4795,) | float32 |
| g_tilde | (4795,) | float32 |
| h_norm | (4795,) | float32 |
| sample_indices | (4795,) | int64 |
| group_labels | (4795,) | int64, {0,1,2,3} |
| class_labels | (4795,) | int64, {0,1} |

### Pseudo-code: collect_gradnorms()

```
1. model.eval()
2. all_g_raw, all_g_tilde, all_h_norm = [], [], []
   all_idx, all_group, all_class = [], [], []
3. for batch_idx, (images, y, place) in enumerate(loader):
       images, y = images.to(device), y.to(device)
       group = y * 2 + place                           # (B,) in {0,1,2,3}
       g_raw_b, g_tilde_b, h_norm_b = analyzer.compute_batch_norms(images, y)
       analyzer.clear()
       start = batch_idx * loader.batch_size
       idx_b = torch.arange(start, start + len(y))
       [append all to lists]
4. arrays = {
       'g_raw':          cat(all_g_raw).numpy(),       # (4795,)
       'g_tilde':        cat(all_g_tilde).numpy(),     # (4795,)
       'h_norm':         cat(all_h_norm).numpy(),      # (4795,)
       'sample_indices': cat(all_idx).numpy(),         # (4795,)
       'group_labels':   cat(all_group).numpy(),       # (4795,)
       'class_labels':   cat(all_class).numpy(),       # (4795,)
   }
5. np.savez(f"{output_dir}/gradnorm_epoch_{epoch}.npz", **arrays)
6. model.train()   # restore train mode
7. return arrays
```

### CSV Schema (train_log.csv)

Columns: `epoch, loss, acc, ratio, auc, balance_deviation`

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| S-A-3-1 | train_epoch() | ERM forward+backward+step + per-epoch CSV row append |
| S-A-3-2 | collect_gradnorms() | eval-mode full-set pass, batch concat, .npz save, model.train() restore |

---

## A-4: Evaluation + Gate [Complexity: 9, Budget: 2 subtasks]

### API Signatures

```python
# src/evaluate.py
import numpy as np
from sklearn.metrics import roc_auc_score
import json
import datetime

def compute_metrics(
    g_tilde: np.ndarray,       # (N,) float32
    g_raw: np.ndarray,         # (N,) float32
    h_norm: np.ndarray,        # (N,) float32
    group_labels: np.ndarray,  # (N,) int64 — {0,1,2,3}
    class_labels: np.ndarray,  # (N,) int64 — {0,1}
) -> dict[str, float]:
    """
    Computes ratio, auc, balance_deviation + secondary per-group means.
    minority = G1 (group==1) | G2 (group==2).
    """
    ...

def gate_check(
    metrics: dict[str, float]
) -> tuple[bool, dict[str, bool]]:
    """Check ratio>=3.0, auc>0.70, balance_deviation<=0.10."""
    ...

def verify_mechanism_activated(
    epoch_results: dict[str, float],  # metrics dict from compute_metrics
) -> tuple[bool, dict[str, bool]]:
    """
    Check: hook_fired (features_count>0), ratio_above_chance>1.5,
    auc_above_random>0.55, feature_norms_equalized (h_norm_std_ratio<0.5).
    """
    ...

def save_results(
    per_epoch_metrics: dict[int, dict],   # {epoch: metrics_dict}
    gate_results: dict,                   # from gate_check at epoch 5
    secondary_metrics: dict,
    output_path: str,                     # 'outputs/h-e1/results.json'
) -> None:
    """Write results.json per FR-7.1 schema."""
    ...
```

### Pseudo-code: compute_metrics()

```
1. minority_mask = (group_labels == 1) | (group_labels == 2)   # (N,) bool
2. ratio = g_tilde[minority_mask].mean() / g_tilde[~minority_mask].mean()
3. auc = roc_auc_score(minority_mask.astype(int), g_tilde)

4. top_k = int(0.25 * N)                                       # 1199
   top_k_idx = np.argsort(g_tilde)[-top_k:]
   selected_y = class_labels[top_k_idx]
   selected_g = group_labels[top_k_idx]
   deviations = []
   for y_val in [0, 1]:
       y_mask = (selected_y == y_val)
       if y_mask.sum() > 0:
           place_bits = selected_g[y_mask] % 2                 # place=0 or 1
           counts = np.bincount(place_bits, minlength=2)
           p_place = counts / counts.sum()
           deviations.append(np.max(np.abs(p_place - 0.5)))
   balance_deviation = max(deviations)

5. per_group_g_tilde = {g: g_tilde[group_labels==g].mean() for g in range(4)}
   per_group_h_norm  = {g: h_norm[group_labels==g].mean() for g in range(4)}
   per_group_g_raw   = {g: g_raw[group_labels==g].mean() for g in range(4)}

6. return {
       'ratio': ratio, 'auc': auc, 'balance_deviation': balance_deviation,
       **{f'g_tilde_mean_G{g}': v for g,v in per_group_g_tilde.items()},
       **{f'h_norm_mean_G{g}':  v for g,v in per_group_h_norm.items()},
       **{f'g_raw_mean_G{g}':   v for g,v in per_group_g_raw.items()},
   }
```

### Pseudo-code: gate_check()

```
criteria = {
    'ratio':             metrics['ratio'] >= 3.0,
    'auc':               metrics['auc'] > 0.70,
    'balance_deviation': metrics['balance_deviation'] <= 0.10,
}
all_pass = all(criteria.values())
return all_pass, criteria
```

### Pseudo-code: verify_mechanism_activated()

```
indicators = {
    'hook_fired':             epoch_results.get('features_count', 0) > 0,
    'ratio_above_chance':     epoch_results['ratio'] > 1.5,
    'auc_above_random':       epoch_results['auc'] > 0.55,
    'feature_norms_equalized': epoch_results.get('h_norm_std_ratio', 1.0) < 0.5,
}
all_activated = all(indicators.values())
return all_activated, indicators
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| S-A-4-1 | compute_metrics() | ratio, AUC via sklearn, balance_deviation top-25% within-class; accepts g_tilde, g_raw, h_norm, group_labels, class_labels |
| S-A-4-2 | gate_check() + verify_mechanism_activated() + save_results() | threshold checks, indicator checks, results.json write per FR-7.1 |

---

## Summary: All 6 Subtasks

| ID | Task | Subtask | Description |
|----|------|---------|-------------|
| S-A-2-1 | A-2 | GradientNormAnalyzer | FC hook + outer-product decomp |
| S-A-2-2 | A-2 | get_model + BN mode | ResNet-50 setup, BN mode management |
| S-A-3-1 | A-3 | train_epoch | ERM loop + CSV row logging |
| S-A-3-2 | A-3 | collect_gradnorms | eval-mode full pass + .npz save |
| S-A-4-1 | A-4 | compute_metrics | ratio, AUC, balance_deviation + secondary |
| S-A-4-2 | A-4 | gate_check + save | threshold checks + verify_mechanism + results.json |

---

## Constants Reference

```python
COLLECTION_EPOCHS = {1, 3, 5, 10}
PRIMARY_EPOCH     = 5
LR                = 0.001
MOMENTUM          = 0.9
WEIGHT_DECAY      = 1e-4
BATCH_SIZE        = 128
TOTAL_EPOCHS      = 10
SEED              = 1
TOP_K_FRACTION    = 0.25
GATE_RATIO        = 3.0
GATE_AUC          = 0.70
GATE_BALANCE      = 0.10
FC_INPUT_DIM      = 2048
EPSILON           = 1e-8
```

---

*Logic for H-E1 | EXISTENCE PoC | Green-field | 6 subtasks (A-2: 2, A-3: 2, A-4: 2)*
