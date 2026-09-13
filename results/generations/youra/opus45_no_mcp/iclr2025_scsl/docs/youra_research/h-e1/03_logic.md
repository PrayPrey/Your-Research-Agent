# Logic: H-E1 Crystallization Zone Detection (EXISTENCE/PoC)

Applied: WILDS-loader pattern (group-annotated `get_dataset`/`get_subset`)
Applied: Rolling-window numerical differentiation (np.convolve + np.gradient) for peak detection

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project - no existing code to analyze, new API design
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

---

## A-1: Data Pipeline [Complexity: 10, Budget: 10]

**Applied**: WILDS-loader pattern

### API Signatures

```python
# data.py
from wilds import get_dataset
from wilds.common.data_loaders import get_train_loader, get_eval_loader
from torchvision.transforms import Compose
from torch.utils.data import DataLoader

def get_transforms(eval_mode: bool) -> Compose:
    """224x224 resize + normalize (ImageNet stats). eval_mode disables augmentation."""
    ...

def load_dataset(name: str, root_dir: str = "./data"):
    """name in {'waterbirds','celebA'}. Downloads via WILDS if missing."""
    ...

def get_loaders(name: str, batch_size: int = 128) -> dict[str, DataLoader]:
    """Returns {'train','val','test'}. Each batch: (x, y, metadata)
    x: [B,3,224,224], y: [B], metadata: [B, K] (col 0 = group id)."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x | [B, 3, 224, 224] | Image batch |
| y | [B] | Binary label (long) |
| metadata | [B, K] | metadata[:,0] = group id (0..3) |

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | Transforms | `get_transforms`: Resize(224), ToTensor, Normalize |
| L-1-2 | Dataset load | `load_dataset` wraps `wilds.get_dataset(dataset=name, download=True, root_dir=root_dir)` |
| L-1-3 | Split loaders | `get_loaders`: `dataset.get_subset(split, transform=...)` -> `get_train_loader`/`get_eval_loader` for train/val/test |
| L-1-4 | Group id extraction | Confirm `metadata[:,0]` maps to WILDS `eval_grouper` group id (4 groups per dataset) |

---

## A-3: Training Loop [Complexity: 11, Budget: 11]

**Applied**: Standard PyTorch ERM training loop

### API Signatures

```python
# train.py
import torch
from torch import nn, Tensor
from torch.utils.data import DataLoader

def train_one_epoch(
    model: nn.Module, loader: DataLoader, optimizer: torch.optim.Optimizer,
    criterion: nn.Module, device: str
) -> float:
    """One epoch of ERM training. Returns avg train loss (scalar)."""
    ...

def train(dataset_name: str, cfg: "Config") -> dict:
    """Full training run with per-epoch WGA eval + checkpointing.
    Returns {'wga_history': list[float], 'group_acc_history': list[dict[int,float]]}."""
    ...
```

### Pseudo-code

```
1. model = build_resnet50(); model.to(device)
2. optimizer = SGD(model.params, lr=cfg.lr, momentum=cfg.momentum, weight_decay=cfg.weight_decay)
3. criterion = CrossEntropyLoss()
4. loaders = get_loaders(dataset_name, cfg.batch_size)
5. n_epochs = cfg.epochs_waterbirds if dataset_name=="waterbirds" else cfg.epochs_celeba
6. for epoch in range(n_epochs):
     train_one_epoch(model, loaders['train'], optimizer, criterion, device)
     wga, group_acc = evaluate_epoch(model, loaders['val'], device)   # [B,2048]->[B,2] logits inside model
     wga_history.append(wga); group_acc_history.append(group_acc)
     torch.save(model.state_dict(), f"ckpt_epoch{epoch}.pt")          # checkpoint every epoch (NFR-1)
7. return {'wga_history': wga_history, 'group_acc_history': group_acc_history}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | Optimizer/loop setup | `train_one_epoch`: forward, CE loss, backward, step |
| L-3-2 | Per-epoch WGA hook | Call `evaluate_epoch(model, val_loader, device)` after each epoch, append to histories |
| L-3-3 | Checkpointing | Save `model.state_dict()` every epoch to `ckpt_epoch{N}.pt` (NFR-1) |

---

## Codebase Note

`evaluate.py` (A-4) and `detector.py` (A-5) are allocated to other agents/low-complexity
handling per task allocation; only A-1 and A-3 detailed here per budget. Their signatures
are already fixed in `03_architecture.md` and reused as-is by A-3's `evaluate_epoch` call.
