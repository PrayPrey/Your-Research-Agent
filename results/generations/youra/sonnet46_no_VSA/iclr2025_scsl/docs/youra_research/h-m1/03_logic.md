# Logic: H-M1 — Differential Confidence Trajectory Verification

**Date:** 2026-08-04
**Budget:** 4 subtasks

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-E3 extension)
**Status:** API signatures verified from actual H-E3 code
**Analyzed Path:** `docs/youra_research/h-e3/code/`
**Relevant Symbols:**
- `load_checkpoint(seed: int, epoch: int, device: str) -> nn.Module` — `train_erm.py:25` (no model arg — builds internally)
- `get_eval_loader(root: str, split: int, batch_size: int) -> DataLoader` — `data.py:62`
- `WaterbirdsDataset.__init__(self, root: str, split: int, transform=None)` — `data.py:14`; `__getitem__` returns `(img, y, group)`
- `ckpt_path(seed: int, epoch: int) -> str` — `config.py:44`, pattern: `ckpt_seed{seed}_epoch{epoch}.pt`
- `CHECKPOINT_EPOCHS = [0,1,5,10,20,50]`, `SEEDS = [1,2,3,4,5]`
- `DATA_ROOT = "/home/PrayPrey/data/waterbirds_v1.0/waterbirds_v1.0/"` (double subdir — verified)
- `CKPT_DIR = "docs/youra_research/h-e3/results/checkpoints/"`
- `MINORITY_GROUPS = (1, 3)` in H-E3 config — H-M1 overrides to `(1, 2)` per PRD (group=2: waterbird/land)

**CRITICAL:** H-E3 `load_checkpoint(seed, epoch, device)` takes NO model argument — it builds the model internally. H-M1 `load_checkpoint` wrapper must match this exact signature.

Applied: Standard PyTorch softmax confidence extraction (no KB domain match)

---

## External Dependencies API (Base Hypothesis H-E3)

Signatures verified from actual code — NOT from specs:

```python
# From: docs/youra_research/h-e3/code/train_erm.py (ACTUAL CODE, line 25)
def load_checkpoint(seed: int, epoch: int, device: str) -> nn.Module:
    """Build ResNet-50, load state_dict, return model.eval() on device."""
    # path = config.ckpt_path(seed, epoch)  ->  CKPT_DIR/ckpt_seed{seed}_epoch{epoch}.pt

# From: docs/youra_research/h-e3/code/data.py (ACTUAL CODE)
class WaterbirdsDataset(Dataset):
    def __init__(self, root: str, split: int, transform=None): ...
    # .y: Tensor[N] int64, .group: Tensor[N] int64
    # .minority_mask: Tensor[N] bool  (built from config.MINORITY_GROUPS)
    # __getitem__ -> (img_tensor, y_scalar, group_scalar)

def get_eval_loader(root: str, split: int, batch_size: int) -> DataLoader:
    """shuffle=False, num_workers=4, eval_transform (Resize256/CenterCrop224/Normalize)."""
    # loader.dataset is WaterbirdsDataset instance

# From: docs/youra_research/h-e3/code/config.py (ACTUAL CODE)
DATA_ROOT: str = "/home/PrayPrey/data/waterbirds_v1.0/waterbirds_v1.0/"  # double subdir
CKPT_DIR:  str = "docs/youra_research/h-e3/results/checkpoints/"
CHECKPOINT_EPOCHS: list = [0, 1, 5, 10, 20, 50]
SEEDS: list = [1, 2, 3, 4, 5]
MINORITY_GROUPS: tuple = (1, 3)   # H-E3 definition; H-M1 uses (1, 2) — different!

def ckpt_path(seed: int, epoch: int) -> str:
    return os.path.join(CKPT_DIR, f"ckpt_seed{seed}_epoch{epoch}.pt")
```

**Verified from:** `docs/youra_research/h-e3/code/` (actual implementation, not specs)

---

## M1-3: Confidence Extraction [Complexity: 8, Budget: 1/4]

**Applied:** Standard PyTorch softmax indexing

### API Signatures

```python
# docs/youra_research/h-m1/code/compute_confidence.py

import torch
import torch.nn.functional as F
from torch import Tensor
from typing import Tuple

def extract_confidence_by_group(
    model: torch.nn.Module,
    loader,                      # DataLoader yielding (x, y, g); shuffle=False
    minority_mask: Tensor,       # [N] bool, precomputed externally (NOT from loader.dataset)
    device: str,
) -> Tuple[Tensor, float, float]:
    """Forward pass; softmax; index by true class.
    Returns: (p_per_sample [N], p_minority scalar, p_majority scalar)
    """
    model.eval()
    all_conf: list[Tensor] = []
    with torch.no_grad():
        for x, y, _g in loader:
            x, y = x.to(device), y.to(device)
            logits = model(x)                          # [B, 2]
            probs  = F.softmax(logits, dim=1)          # [B, 2]
            conf   = probs[torch.arange(len(y)), y]    # [B]
            all_conf.append(conf.cpu())
    p_per_sample = torch.cat(all_conf)                 # [N=4795]
    p_min = p_per_sample[minority_mask].mean().item()
    p_maj = p_per_sample[~minority_mask].mean().item()
    return p_per_sample, p_min, p_maj
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x | [B, 3, 224, 224] | eval_transform applied by loader |
| y | [B] | int64 |
| logits | [B, 2] | ResNet-50 fc output |
| probs | [B, 2] | softmax, rows sum to 1 |
| conf | [B] | probs[i, y[i]] |
| p_per_sample | [4795] | full train set, CPU |
| minority_mask | [4795] | bool, sum=240 |

### Subtasks [1/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | confidence_loop | extract_confidence_by_group() implementation |

---

## M1-4: Trajectory Loop [Complexity: 9, Budget: 2/4]

**Applied:** Standard checkpoint iteration, CPU tensor accumulation

### API Signatures

```python
def compute_trajectory(
    seed: int,
    loader,                  # single DataLoader instance, reused across all checkpoints
    minority_mask: Tensor,   # [N=4795] bool
    device: str,
) -> dict:
    """Load each checkpoint epoch; extract confidence; free GPU between loads.
    Returns: {epoch: {'p_min': float, 'p_maj': float, 'p_per_sample': Tensor[N]}}
    """
```

### Pseudo-code: compute_trajectory()

```
from train_erm import load_checkpoint   # H-E3 API: (seed, epoch, device) -> model

results = {}
for epoch in CHECKPOINT_EPOCHS:                   # [0, 1, 5, 10, 20, 50]
    model = load_checkpoint(seed, epoch, device)  # loads from CKPT_DIR
    p_per_sample, p_min, p_maj = extract_confidence_by_group(model, loader, minority_mask, device)
    results[epoch] = {
        'p_min': p_min,
        'p_maj': p_maj,
        'p_per_sample': p_per_sample,             # [4795] on CPU
    }
    del model
    torch.cuda.empty_cache()
return results
```

**Memory note (L-4-2):** 6 epochs × 4795 × 4 bytes = ~115 KB per seed. No OOM risk.
Store p_per_sample on CPU (`.cpu()` in extract loop). Convert to `.tolist()` only in save_results JSON serialization.

### Subtasks [2/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | trajectory_loop | compute_trajectory() with epoch iteration and del model |
| L-4-2 | memory_mgmt | CPU accumulation, cuda.empty_cache, tolist() at JSON save time |

---

## M1-5 (partial): Gate Logic [no extra budget]

### API Signatures

```python
def check_gate(p_min: float, p_maj: float) -> Tuple[bool, bool]:
    """primary: 0.3<=p_min<=0.7; secondary: p_maj>0.80"""
    return (GATE_P_MIN_LOW <= p_min <= GATE_P_MIN_HIGH), (p_maj > GATE_P_MAJ)

def verify_mechanism_activated(
    results_per_seed: dict,
    # {seed: {epoch: {'p_min': float, 'p_maj': float, 'p_per_sample': Tensor}, 'tstar': int}}
) -> Tuple[bool, dict]:
    """Returns (mechanism_active, per_seed_indicators). mechanism_active if >=4 seeds pass primary."""
```

### Gate Pseudo-code

```
indicators = {}
for seed, traj in results_per_seed.items():
    tstar = traj['tstar']
    p_min = traj[tstar]['p_min']
    p_maj = traj[tstar]['p_maj']
    primary, secondary = check_gate(p_min, p_maj)
    indicators[seed] = {
        'minority_boundary': primary,
        'majority_saturated': secondary,
        'gap': p_maj - p_min,
        'both_pass': primary and secondary,
    }
n_pass = sum(v['both_pass'] for v in indicators.values())
return (n_pass >= GATE_N_SEEDS), indicators   # GATE_N_SEEDS=4
```

---

## M1-10: Main Runner & Integration Test [Complexity: 10, Budget: 3-4/4]

### API Signatures

```python
# docs/youra_research/h-m1/code/run_experiment.py

def main() -> None:
    """Full experiment: 5 seeds x 6 checkpoints; gate verify; save; figures."""

def smoke_test(seed: int = 1, epoch: int = 1) -> None:
    """Single checkpoint pipeline check. Runs in <30s."""

if __name__ == "__main__":
    import sys
    if "--smoke" in sys.argv:
        smoke_test()
    else:
        main()
```

### Pseudo-code: main() [L-10-1]

```
1. sys.path.insert(0, H_E3_CODE)           # enable H-E3 imports
2. ensure_dirs()
3. loader = get_eval_loader(DATA_ROOT, split=0, batch_size=BATCH_SIZE)
4. dataset = loader.dataset                 # WaterbirdsDataset
5. minority_mask = (dataset.group == 1) | (dataset.group == 2)   # [4795] bool; NOT dataset.minority_mask
6. assert minority_mask.sum() == 240, f"Expected 240, got {minority_mask.sum()}"

7. results_per_seed = {}
8. for seed in SEEDS:
9.     torch.manual_seed(seed)
10.    traj = compute_trajectory(seed, loader, minority_mask, device=DEVICE)
11.    traj['tstar'] = TSTAR_PER_SEED[seed]
12.    results_per_seed[seed] = traj
13.    tstar = TSTAR_PER_SEED[seed]
14.    print(f"seed={seed} t*={tstar} p_min={traj[tstar]['p_min']:.3f} p_maj={traj[tstar]['p_maj']:.3f}")

15. mechanism_active, indicators = verify_mechanism_activated(results_per_seed)
16. n_pass = sum(v['both_pass'] for v in indicators.values())
17. print(f"Gate: {n_pass}/5 pass | mechanism_active={mechanism_active}")

18. save_results(results_per_seed, mechanism_active, n_pass)
19. save_all_figures(results_per_seed)
```

**Note line 5:** Use `(dataset.group == 1) | (dataset.group == 2)` explicitly.
Do NOT use `dataset.minority_mask` — that is built from H-E3's `MINORITY_GROUPS=(1,3)`.

### Pseudo-code: smoke_test() [L-10-2]

```
sys.path.insert(0, H_E3_CODE)
loader = get_eval_loader(DATA_ROOT, split=0, batch_size=256)
dataset = loader.dataset
minority_mask = (dataset.group == 1) | (dataset.group == 2)
model = load_checkpoint(seed=1, epoch=1, device=DEVICE)    # H-E3 API
p_per_sample, p_min, p_maj = extract_confidence_by_group(model, loader, minority_mask, DEVICE)
assert p_per_sample.shape == (4795,), f"shape={p_per_sample.shape}"
assert 0.0 < p_min < 1.0, f"p_min out of range: {p_min}"
assert 0.0 < p_maj < 1.0, f"p_maj out of range: {p_maj}"
print(f"SMOKE OK: p_min={p_min:.3f} p_maj={p_maj:.3f}")
```

### Subtasks [3-4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-10-1 | main_orchestration | minority_mask override, seed loop, gate verify, save, figures |
| L-10-2 | smoke_test | single seed/epoch, shape + range assertions |

---

## Budget Summary

| ID | Task | Description |
|----|------|-------------|
| L-3-1 | M1-3 | extract_confidence_by_group() |
| L-4-1 | M1-4 | compute_trajectory() checkpoint loop |
| L-4-2 | M1-4 | memory management (CPU storage, JSON serialization) |
| L-10-1 | M1-10 | main() orchestration |
| L-10-2 | M1-10 | smoke_test() |

**Total: 4 subtasks used / 4 budget** (L-4-1 and L-4-2 counted as one M1-4 slot; L-10-1 and L-10-2 as one M1-10 slot)
