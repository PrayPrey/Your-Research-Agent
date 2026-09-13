# Logic: H-M1 (MECHANISM)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1)
**Status**: API signatures verified from actual H-E1 code (`docs/youra_research/h-e1/code/`)
**Analyzed Path**: `docs/youra_research/h-e1/code/model.py`, `data.py`, `train.py`
**Relevant Symbols**:
- `build_resnet18(num_classes: int = 2, pretrained: bool = True) -> nn.Module` — `model.fc = nn.Linear(512, num_classes)`
- `get_dataloaders(root_dir: str, batch_size: int, num_workers: int, img_size: int, norm_mean: tuple, norm_std: tuple) -> dict[str, DataLoader]`
- `WaterbirdsDataset.__getitem__(idx) -> (img, y, place, idx)` — 4-tuple, `y`=bird_label (core), `place`=bg_label (spurious)
- `set_seed(seed: int) -> None` — random/np/torch/cudnn

**Applied**: Standard PyTorch (no Archon KB match for linear-probe-on-checkpoint pattern; PyTorch official docs only, not directly applicable)

---

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/model.py (ACTUAL CODE)
def build_resnet18(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """resnet18(weights=IMAGENET1K_V1 if pretrained), model.fc = nn.Linear(512, num_classes)."""
    ...

# From: h-e1/code/data.py (ACTUAL CODE)
def get_dataloaders(root_dir: str, batch_size: int, num_workers: int,
                     img_size: int, norm_mean: tuple, norm_std: tuple) -> dict[str, DataLoader]:
    """Returns {"train": DataLoader, "val": DataLoader, "test": DataLoader}."""
    ...
# WaterbirdsDataset.__getitem__(idx) -> (img: Tensor[3,H,W], y: int, place: int, idx: int)
#   y = bird_label (core, 0=landbird/1=waterbird), place = background_label (spurious, 0=land/1=water)

# From: h-e1/code/train.py (ACTUAL CODE)
def set_seed(seed: int) -> None: ...  # random, np, torch, cudnn determinism
```

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation, not spec).
**Note**: batches are 4-tuples `(img, y, place, idx)` — no `group_idx` in H-E1 final code, unlike an earlier spec revision.

---

## A-1/M-1: Data & Model Reuse [Complexity: 3, Budget: 3]

**Applied**: Direct import, no new code beyond a thin wrapper for defaults.

```python
from h_e1.code.model import build_resnet18
from h_e1.code.data import get_dataloaders
from h_e1.code.train import set_seed
```

No wrapper needed — call directly with `config.py` constants (IMG_SIZE=224, NORM_MEAN/STD from PRD).

### Subtasks [3/3]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | import verification | confirm module paths resolve (`h_e1.code.*`) |
| L-1-2 | contract check | batch = (img[B,3,224,224], y[B], place[B], idx[B]) |
| L-1-3 | config wiring | pass IMG_SIZE/NORM_MEAN/NORM_STD into get_dataloaders |

---

## A-2/M-2: Checkpointed Training (`train_checkpointed.py`) [Complexity: 7, Budget: 7]

**Applied**: Standard PyTorch SGD loop (same as H-E1 `train_erm`, minus per-sample tracking, plus checkpoint save)

```python
def train_with_checkpoints(
    model: nn.Module, loaders: dict, n_epochs: int,
    checkpoint_epochs: list[int], lr: float, momentum: float,
    weight_decay: float, device: str, ckpt_dir: str,
) -> dict[int, str]:
    """Standard ERM loop; torch.save(model.state_dict(), path) after epoch in checkpoint_epochs.
    Returns {epoch: checkpoint_path}."""
    ...
```

### Pseudo-code

```
optimizer = SGD(model.parameters(), lr, momentum, weight_decay)
criterion = CrossEntropyLoss()
ckpt_paths = {}

for epoch in 1..n_epochs:
    model.train()
    for imgs, y, place, idx in loaders["train"]:
        imgs, y = imgs.to(device), y.to(device)
        logits = model(imgs)              # [B, 2]
        loss = criterion(logits, y)
        loss.backward(); optimizer.step(); optimizer.zero_grad()

    if epoch in checkpoint_epochs:
        path = f"{ckpt_dir}/epoch_{epoch}.pt"
        torch.save(model.state_dict(), path)
        ckpt_paths[epoch] = path

return ckpt_paths
```

### Subtasks [4/4]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | optimizer/criterion setup | SGD + reduced CE (no per-sample tracker needed) |
| L-2-2 | train step | forward/backward/step, standard |
| L-2-3 | checkpoint save | `torch.save(state_dict())` at epochs 5, 20, 50 |
| L-2-4 | set_seed call | before training starts |

---

## A-3/M-3: LinearProbeAnalysis (`probe_model.py`) [Complexity: 5, Budget: 5]

**Applied**: Frozen-backbone feature extraction (DFR-style)

```python
class LinearProbeAnalysis(nn.Module):
    def __init__(self, backbone: nn.Module, feature_dim: int = 512):
        """backbone: resnet18 with fc replaced by nn.Identity()."""
        ...

    def extract_features(self, x: Tensor) -> Tensor:
        """x: [B,3,224,224] -> [B,512]. no_grad, avgpool + flatten."""
        ...

def load_frozen_backbone(checkpoint_path: str, num_classes: int = 2) -> nn.Module:
    """build_resnet18(num_classes) -> load_state_dict(checkpoint_path) ->
    model.fc = nn.Identity() -> model.eval() -> requires_grad_(False)."""
    ...
```

### Pseudo-code (extract_features)

```
with torch.no_grad():
    feats = backbone(x)             # backbone.fc = Identity -> [B, 512] directly
    # (if backbone retains conv layers only: F.adaptive_avg_pool2d(feats, 1).flatten(1))
return feats
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| x | [B, 3, 224, 224] | input batch |
| feats | [B, 512] | frozen backbone output |

### Subtasks [3/3]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | load_frozen_backbone | load ckpt, strip fc, eval(), freeze |
| L-3-2 | extract_features | no_grad forward, flatten to [B,512] |
| L-3-3 | device handling | .to(device) for backbone and batch |

---

## A-4/M-4: Probe Training/Eval (`probe_train.py`) [Complexity: 8, Budget: 8]

**Applied**: sklearn accuracy_score, SGD linear classifier on frozen features

```python
def train_probe(
    probe: nn.Linear, backbone: nn.Module, loader: DataLoader,
    label_idx: int, epochs: int, lr: float, device: str,
) -> nn.Linear:
    """label_idx: 1=y (core/bird), 2=place (spurious/bg) from (img,y,place,idx) batch.
    SGD(probe.parameters(), lr). Features via LinearProbeAnalysis.extract_features (no_grad)."""
    ...

def eval_probe(
    probe: nn.Linear, backbone: nn.Module, loader: DataLoader,
    label_idx: int, device: str,
) -> float:
    """Returns accuracy_score(y_true, y_pred) on loader (typically test split)."""
    ...

def run_probes_for_checkpoint(
    ckpt_path: str, loaders: dict, feature_dim: int,
    probe_epochs: float, lr: float, device: str,
) -> dict:
    """Loads backbone, trains+evals spurious probe (label_idx=2) and core probe (label_idx=1)
    on loaders["train"]/loaders["test"]. Returns {"spurious_acc": float, "core_acc": float}."""
    ...
```

### Pseudo-code (train_probe)

```
optimizer = SGD(probe.parameters(), lr=lr)
criterion = CrossEntropyLoss()
for epoch in range(epochs):
    for batch in loader:
        imgs, labels = batch[0].to(device), batch[label_idx].to(device)
        feats = extract_features(backbone, imgs)   # [B, 512], no_grad
        logits = probe(feats)                       # [B, 2]
        loss = criterion(logits, labels)
        loss.backward(); optimizer.step(); optimizer.zero_grad()
return probe
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| feats | [B, 512] | frozen, detached |
| probe logits | [B, 2] | binary classification |
| labels | [B] | y (idx=1) or place (idx=2) |

### Subtasks [4/4]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | train_probe | SGD loop over frozen features, label_idx selects target |
| L-4-2 | eval_probe | inference loop, sklearn accuracy_score |
| L-4-3 | run_probes_for_checkpoint | instantiate 2 probes, train+eval both |
| L-4-4 | probe init | fresh `nn.Linear(feature_dim, 2)` per checkpoint (no reuse across epochs) |

---

## A-5/M-5: Checkpoint Loop Orchestration [Complexity: 6, Budget: 6]

Handled inline in `run_experiment.py::main` — loop over `checkpoint_epochs`, call `run_probes_for_checkpoint` per path, collect into `results["epoch_{e}"]`.

### Subtasks [3/3]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | loop ckpt_paths | for epoch, path in ckpt_paths.items() |
| L-5-2 | collect results | `results[f"epoch_{epoch}"] = run_probes_for_checkpoint(...)` |
| L-5-3 | error isolation | skip/log if a checkpoint file missing |

---

## A-6/M-6: Mechanism Verification (`evaluate.py`) [Complexity: 4, Budget: 4]

```python
def verify_mechanism(results: dict) -> dict:
    """results keyed 'epoch_5'/'epoch_20'/'epoch_50', each {"spurious_acc","core_acc"}.
    Returns {"bias_exists": bool, "core_improves": bool}."""
    ...
```

### Pseudo-code

```
epoch5, epoch50 = results["epoch_5"], results["epoch_50"]
bias_exists = epoch5["spurious_acc"] > epoch5["core_acc"]      # gate condition
core_improves = epoch50["core_acc"] > epoch5["core_acc"]
return {"bias_exists": bias_exists, "core_improves": core_improves}
```

### Subtasks [2/2]

| ID | Subtask | Description |
|----|---------|--------------|
| L-6-1 | bias_exists check | spurious_acc(5) > core_acc(5) |
| L-6-2 | core_improves check | core_acc(50) > core_acc(5) |

---

## A-7/M-7: Visualization (`evaluate.py`) [Complexity: 4, Budget: 4]

```python
def plot_probe_accuracy_curve(results: dict, out_path: str) -> None:
    """Line plot: x=epochs [5,20,50], two lines (spurious_acc, core_acc). matplotlib, savefig(out_path)."""
    ...
```

### Subtasks [1/1]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | line plot | 2 series across 3 epochs, legend, save PNG |

---

## A-8/M-8: End-to-End Run (`run_experiment.py`) [Complexity: 5, Budget: 5]

```python
def run_evaluation(results: dict, figures_dir: str, metrics_path: str) -> dict:
    """Calls verify_mechanism + plot_probe_accuracy_curve, writes results+verification to metrics_path (JSON)."""
    ...

def main() -> None:
    """1. set_seed(SEED)
    2. get_dataloaders(DATA_ROOT, BATCH_SIZE, ...)
    3. train_with_checkpoints(model, loaders, N_EPOCHS, CHECKPOINT_EPOCHS, ...) -> ckpt_paths
    4. for epoch, path in ckpt_paths: results[f"epoch_{epoch}"] = run_probes_for_checkpoint(path, loaders, ...)
    5. run_evaluation(results, figures_dir, metrics_path)
    6. assert verify_mechanism(results)["bias_exists"]  # gate"""
    ...
```

### Subtasks [3/3]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | wire pipeline | train -> probes loop -> evaluation, in main() |
| L-8-2 | save metrics JSON | results + bias_exists/core_improves to metrics.json |
| L-8-3 | gate assertion | assert spurious_acc(5) > core_acc(5) |

---

## Data Flow

```
set_seed -> get_dataloaders (shared w/ H-E1)
  -> train_with_checkpoints(model, loaders) -> {5: path, 20: path, 50: path}
  -> for each ckpt: load_frozen_backbone(path) -> run_probes_for_checkpoint
       -> train_probe(spurious, label_idx=2) + train_probe(core, label_idx=1)
       -> eval_probe on test loader -> {spurious_acc, core_acc}
  -> results dict keyed epoch_5/epoch_20/epoch_50
  -> verify_mechanism(results) -> {bias_exists, core_improves}
  -> plot_probe_accuracy_curve + save metrics.json
  -> gate check: bias_exists must be True
```
