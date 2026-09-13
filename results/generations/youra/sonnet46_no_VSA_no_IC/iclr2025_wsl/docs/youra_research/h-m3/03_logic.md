---
hypothesis_id: h-m3
phase: logic
generated_at: "2026-08-21"
---

# Logic: H-M3 — Permutation Augmentation (PermAug) for Flat-MLP

Applied: Standard PyTorch wrapper-dataset pattern (Archon KB: no relevant domain hits)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis + existing_codebase
**Status**: Serena project activation failed (no active project); API signatures verified via direct file reads
**Analyzed Path**: `docs/youra_research/h-e1/code/` and `docs/youra_research/h-m2/code/`
**Relevant Symbols**:
- `FlatMLP.__init__(input_dim, hidden_dim=256, num_layers=3)` — h-e1/encoders.py:14
- `FlatMLP.forward(x: Tensor) -> Tensor` — x: [B,D] → [B,] — h-e1/encoders.py:22
- `train_one(encoder, train_loader, val_loader, encoder_name, epochs, lr, weight_decay, seed, device) -> dict` — h-e1/train.py:8
- `get_predictions(encoder, loader, encoder_name, device) -> (np.ndarray, np.ndarray)` — h-e1/train.py:112
- `load_zoo(zoo_name: str) -> tuple[ZooDataset, ZooDataset, ZooDataset]` — h-e1/data.py:48
- `subsample(dataset, n, seed=42) -> ZooDataset` — h-e1/data.py:80
- `FlatCollator(scaler=None).__call__(batch) -> (Tensor[B,D], Tensor[B])` — h-e1/data.py:116
- `load_h_e1_results(path: str) -> Optional[dict]` — h-m2/results_loader.py:12
- `_setup_h_e1_imports()` inserts `cfg.H_E1_CODE_DIR, cfg.H_M1_CODE_DIR, cfg.MZDATASET_CODE_PATH` — h-m2/results_loader.py:67

---

## External Dependencies API

Signatures verified from actual code (NOT specs):

```python
# From: h-e1/code/train.py
def train_one(
    encoder: nn.Module,
    train_loader: DataLoader,
    val_loader: DataLoader,
    encoder_name: str,           # use "flat_mlp" (NOT "flat_mlp_perm_aug" — avoids H-E1 perm bug)
    epochs: int = 100,
    lr: float = 1e-3,
    weight_decay: float = 1e-4,
    seed: int = 42,
    device: str = "cuda",
) -> dict:                       # {"train_loss": [...], "val_loss": [...]}
    ...

def get_predictions(
    encoder: nn.Module,
    loader: DataLoader,
    encoder_name: str,           # "flat_mlp"
    device: str,
) -> tuple[np.ndarray, np.ndarray]:  # (y_true, y_pred)
    ...

# From: h-e1/code/data.py
def load_zoo(zoo_name: str) -> tuple:          # (train_ds, val_ds, test_ds)
    ...

def subsample(dataset, n, seed: int = 42):    # returns Subset with .targets attr
    ...

class FlatCollator:
    def __init__(self, scaler=None): ...       # scaler: (mean, std) or None
    def __call__(self, batch) -> tuple:        # (Tensor[B,D], Tensor[B])
        ...

# From: h-e1/code/encoders.py
class FlatMLP(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 256, num_layers: int = 3): ...
    def forward(self, x: Tensor) -> Tensor: ...  # [B,D] → [B,]

# From: h-m2/code/results_loader.py
def load_h_e1_results(path: str) -> Optional[dict]:
    ...  # returns {encoder: {zoo: {size_str: {mean_r2, ci_lo, ci_hi, seed_r2s}}}}
```

**Verified from**: actual files in `h-e1/code/` and `h-m2/code/` (not specs)

**Critical note**: H-E1's `_forward()` dispatches on `encoder_name`. Use `"flat_mlp"` (not `"flat_mlp_perm_aug"`) when calling `train_one` for PermAug training — H-M3 handles augmentation in the DataLoader, not in the model.

---

## A-2: PermAug Core [Complexity: 13, Budget: 2 subtasks]

Applied: Standard PyTorch wrapper-dataset pattern

### API Signatures

```python
# code/perm_aug.py
import torch
from torch import Tensor
from torch.utils.data import Dataset


def apply_random_permutation(weight_vector: Tensor, layer_sizes: list[int]) -> Tensor:
    """Permute hidden neurons of a flat weight vector. weight_vector: [D,] -> [D,]"""
    ...


class PermAugDataset(Dataset):
    def __init__(
        self,
        base_dataset: Dataset,
        layer_sizes: list[int],
        num_permutations: int = 10,
    ):
        """Wraps base_dataset; __len__ = len(base) * (num_permutations + 1)."""
        self.base = base_dataset
        self.layer_sizes = layer_sizes
        self.num_permutations = num_permutations

    def __len__(self) -> int:
        return len(self.base) * (self.num_permutations + 1)

    def __getitem__(self, idx: int) -> tuple[Tensor, Tensor]:
        # x: [D,], y: scalar
        ...


def get_layer_sizes(first_flat_sample: Tensor, layer_spec: list[int]) -> list[int]:
    """Return [input_dim, h1, h2, ..., output_dim] from known architecture spec."""
    # For CIFAR-10 CNN zoo: layer_spec is passed from config (architecture known)
    return layer_spec
```

### Subtask L-1: apply_random_permutation — pseudo-code

```
Input:  weight_vector: Tensor shape (D,)
        layer_sizes:   [s0, s1, s2, ..., sL]  # e.g. [input, 256, 128, 1] for FlatMLP

Step 1: Compute per-layer offsets for (W_l, b_l) in the flat vector.
        Each layer l has:
          W_l: rows=layer_sizes[l+1], cols=layer_sizes[l]  → numel = layer_sizes[l+1]*layer_sizes[l]
          b_l: size = layer_sizes[l+1]
        offsets[l] = cumsum of all prior (W + b) sizes.

Step 2: Clone weight_vector → out: Tensor [D,]

Step 3: For l in range(0, len(layer_sizes)-2):   # hidden layers only (exclude output layer)
          h = layer_sizes[l+1]                    # hidden size to permute
          perm = torch.randperm(h)                # random permutation of h neurons

          # Slice W_l from flat vector: shape (h, layer_sizes[l])
          W_l_start = offset[l]
          W_l_end   = W_l_start + h * layer_sizes[l]
          W_l = out[W_l_start:W_l_end].view(h, layer_sizes[l])

          # Slice b_l: shape (h,)
          b_l_start = W_l_end
          b_l_end   = b_l_start + h
          b_l = out[b_l_start:b_l_end]

          # Slice W_{l+1}: shape (layer_sizes[l+2], h)
          W_next_start = b_l_end
          W_next_end   = W_next_start + layer_sizes[l+2] * h
          W_next = out[W_next_start:W_next_end].view(layer_sizes[l+2], h)

          # Apply permutation
          out[W_l_start:W_l_end]     = W_l[perm, :].reshape(-1)
          out[b_l_start:b_l_end]     = b_l[perm]
          out[W_next_start:W_next_end] = W_next[:, perm].reshape(-1)

Step 4: Return out  # shape (D,), same norm as input (permutation is norm-preserving)

Verify: assert (out.norm() - weight_vector.norm()).abs() < 1e-4
```

### Subtask L-2: PermAugDataset.__getitem__ — tensor shape trace

```
Input:  idx: int in [0, len(base) * 11)

base_idx = idx // 11       # which base sample
aug_idx  = idx % 11        # 0=original, 1-10=augmented

x, y = self.base[base_idx]
# x: Tensor [D,]   (already flattened and normalized by FlatCollator upstream)
# y: Tensor []     (scalar float32)

if aug_idx == 0:
    return x, y            # original, no permutation
else:
    return apply_random_permutation(x, self.layer_sizes), y
    # output x_aug: [D,] same dtype/device as x

Note: PermAugDataset returns RAW (x, y) pairs — DataLoader uses FlatCollator for batching.
      But since base_dataset items are already flat Tensors (post-collation), PermAugDataset
      needs its own collate:
        collate_fn = lambda batch: (torch.stack([b[0] for b in batch]),
                                    torch.stack([b[1] for b in batch]))
      OR: base_dataset is the ZooDataset (state_dicts), and x is extracted via FlatCollator
          inside __getitem__. Use the simpler approach: store pre-flattened tensors.

Recommended: pre-flatten all base samples at __init__ time to avoid repeated collation.
```

---

## A-5: Training Loop [Complexity: 12, Budget: 2 subtasks]

Applied: Standard PyTorch training loop with DataLoader injection

### API Signatures

```python
# code/train.py
import sys
import torch
import numpy as np
from torch import Tensor
from torch.utils.data import DataLoader
from sklearn.metrics import r2_score


def train_perm_aug(
    n_train: int,
    zoo_name: str = "cifar10",
    device: str = "cuda",
) -> tuple[float, list[float], list[float]]:
    """Train FlatMLP + PermAug for one (zoo, n_train) cell.
    Returns (r2_test, train_loss_curve, val_loss_curve)."""
    ...


def train_all_sizes(
    sizes: list[int],
    zoo_name: str = "cifar10",
    device: str = "cuda",
) -> dict:
    """Train PermAug for all N in sizes.
    Returns {str(N): {"r2": float, "train_losses": list, "val_losses": list}}."""
    ...


def verify_perm_aug_mechanism(
    perm_dataset: "PermAugDataset",
    plain_dataset,
    layer_sizes: list[int],
) -> dict:
    """Mechanism check: must pass before any training.
    Returns indicators dict. Raises RuntimeError if any check fails."""
    ...
```

### Subtask L-3: train_perm_aug — pseudo-code

```
def train_perm_aug(n_train, zoo_name="cifar10", device="cuda"):

  # 1. Inject base code paths (match H-M2 pattern from results_loader._setup_h_e1_imports)
  import config as cfg
  for p in [cfg.H_E1_CODE_DIR, cfg.H_M1_CODE_DIR, cfg.MZDATASET_CODE_PATH]:
      if p not in sys.path:
          sys.path.insert(0, p)

  from data import load_zoo, subsample, FlatCollator, compute_flat_scaler
  from train import train_one, get_predictions
  from encoders import FlatMLP
  from perm_aug import PermAugDataset, get_layer_sizes
  from verify import verify_perm_aug_mechanism

  # 2. Load data
  train_ds, val_ds, test_ds = load_zoo(zoo_name)
  sub_train = subsample(train_ds, n_train, seed=cfg.SEED)

  # 3. Compute scaler from sub-train for normalization
  scaler = compute_flat_scaler(sub_train)   # (mean [D,], std [D,])

  # 4. Get flat input_dim from first sample
  collator = FlatCollator(scaler)
  probe_loader = DataLoader(sub_train, batch_size=2, shuffle=False, collate_fn=collator)
  first_batch = next(iter(probe_loader))
  input_dim = first_batch[0].shape[1]       # D

  # 5. Pre-flatten sub_train for PermAugDataset
  #    Build a TensorDataset of (flat_x, y) for fast __getitem__
  all_x, all_y = [], []
  for x_batch, y_batch in DataLoader(sub_train, batch_size=64, collate_fn=collator):
      all_x.append(x_batch)
      all_y.append(y_batch)
  flat_x = torch.cat(all_x)   # [N, D]
  flat_y = torch.cat(all_y)   # [N]
  plain_tensor_ds = torch.utils.data.TensorDataset(flat_x, flat_y)

  # 6. layer_sizes for CIFAR-10 CNN zoo (from config)
  layer_sizes = cfg.CIFAR10_LAYER_SIZES  # e.g. [input_dim] + hidden + [1] for FlatMLP

  # 7. Build PermAugDataset
  perm_ds = PermAugDataset(plain_tensor_ds, layer_sizes, num_permutations=cfg.NUM_PERMUTATIONS)

  # 8. Verify mechanism BEFORE training (raises RuntimeError on failure)
  verify_perm_aug_mechanism(perm_ds, plain_tensor_ds, layer_sizes)

  # 9. Build DataLoaders
  batch_size = cfg.BATCH_SIZE_SMALL if n_train <= cfg.SMALL_SIZE_THRESHOLD else cfg.BATCH_SIZE
  # perm_ds already has flat Tensors — use simple collate
  def flat_collate(batch):
      xs, ys = zip(*batch)
      return torch.stack(xs), torch.stack(ys)

  train_loader = DataLoader(perm_ds, batch_size=batch_size, shuffle=True,
                            collate_fn=flat_collate, num_workers=0)
  val_loader   = DataLoader(
      torch.utils.data.TensorDataset(
          *[t for t in zip(*[collator([item]) for item in val_ds])]
      ), ...
  )
  # Simpler val_loader: re-use FlatCollator on val_ds
  val_loader  = DataLoader(val_ds, batch_size=64, shuffle=False, collate_fn=collator)
  test_loader = DataLoader(test_ds, batch_size=64, shuffle=False, collate_fn=collator)

  # 10. Build FlatMLP
  encoder = FlatMLP(input_dim=input_dim, hidden_dim=256, num_layers=3)

  # 11. Train — use encoder_name="flat_mlp" (H-E1 _forward dispatches to plain x forward)
  torch.manual_seed(cfg.SEED)
  history = train_one(
      encoder, train_loader, val_loader,
      encoder_name="flat_mlp",    # NOT "flat_mlp_perm_aug" — augmentation is in DataLoader
      epochs=cfg.EPOCHS,
      lr=cfg.LR,
      weight_decay=cfg.WEIGHT_DECAY,
      seed=cfg.SEED,
      device=device,
  )
  # history: {"train_loss": [...×100], "val_loss": [...×10]}

  # 12. Test eval on PLAIN (non-augmented) weights
  y_true, y_pred = get_predictions(encoder, test_loader, "flat_mlp", device)
  r2 = float(r2_score(y_true, y_pred))

  print(f"[H-M3] n_train={n_train} R²={r2:.4f}")
  return r2, history["train_loss"], history["val_loss"]
```

### Subtask L-4: verify_perm_aug_mechanism — pseudo-code

```
def verify_perm_aug_mechanism(perm_dataset, plain_dataset, layer_sizes):

  indicators = {}

  # Check 1: permutation actually changes tensor
  x_plain, y = plain_dataset[0]          # [D,], scalar
  x_aug, _   = perm_dataset[1]           # aug_idx=1 → apply_random_permutation
  aug_diff = (x_aug - x_plain).abs().max().item()
  indicators["aug_diff"] = aug_diff
  print(f"[H-M3] Check 1: aug_diff = {aug_diff:.6f} (must be > 1e-6)")
  if aug_diff <= 1e-6:
      raise RuntimeError(f"[H-M3] FAIL: PermAug did not change tensor! aug_diff={aug_diff}")

  # Check 2: dataset size is 11× base
  expected_len = len(plain_dataset) * 11
  actual_len   = len(perm_dataset)
  indicators["len_check"] = {"expected": expected_len, "actual": actual_len}
  print(f"[H-M3] Check 2: len(perm_ds)={actual_len}, expected={expected_len}")
  if actual_len != expected_len:
      raise RuntimeError(
          f"[H-M3] FAIL: len(perm_ds)={actual_len} != {expected_len}"
      )

  print(f"[H-M3] MECHANISM CHECK PASSED: aug_diff={aug_diff:.6f} > 1e-6, "
        f"len={actual_len} = {len(plain_dataset)} × 11")
  return indicators
```

---

## Config Additions (A-2 / A-5 dependencies)

The following constants must be added to `code/config.py` for L-3 and L-4:

```python
# CIFAR-10 CNN zoo layer sizes for PermAug
# FlatMLP operates on the flattened CNN weight vector; PermAug permutes the FlatMLP's
# OWN hidden layers (not the zoo CNN layers).
# FlatMLP architecture: input_dim → 256 → 128 → 1
# layer_sizes for PermAug on FlatMLP: [input_dim, 256, 128, 1]
# input_dim is determined at runtime from first batch.
FLATMLP_HIDDEN: list = [256, 128]          # hidden dims of FlatMLP predictor
# layer_sizes = [input_dim] + FLATMLP_HIDDEN + [1]  (constructed at runtime)
```

---

## Subtask Summary [4/4 used]

| ID | Subtask | Task | Description |
|----|---------|------|-------------|
| L-1 | apply_random_permutation pseudo-code | A-2 | Index arithmetic + permutation loop |
| L-2 | PermAugDataset.__getitem__ shape trace | A-2 | Tensor flow + collation strategy |
| L-3 | train_perm_aug pseudo-code | A-5 | Full training loop with sys.path injection |
| L-4 | verify_perm_aug_mechanism pseudo-code | A-5 | Two checks + RuntimeError on fail |
