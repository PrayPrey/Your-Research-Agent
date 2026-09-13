# Logic: H-M2 (MECHANISM)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-M1, which extends H-E1)
**Status**: `h-m1/code/` and `h-m2/code/` do not exist on disk yet (spec-only). Used H-M1's verified `03_architecture.md`/`03_logic.md` (which itself verified H-E1 actual code) as source of truth for external API signatures.
**Analyzed Path**: `docs/youra_research/h-m1/03_logic.md` (verified against `h-e1/code/model.py`, `data.py`, `train.py`)
**Relevant Symbols**: `build_resnet18`, `get_dataloaders`, `set_seed`, `WaterbirdsDataset.__getitem__` (see External Dependencies below)

**Applied**: Archon KB had no relevant matches for epoch-wise-probe/peak-detection (only diffusers pipeline docs, irrelevant) — using standard PyTorch + sklearn patterns per PRD FR-2/FR-4.

---

## External Dependencies (Base Hypothesis)

```python
# From: h-e1/code/model.py (ACTUAL CODE, via H-M1 verification)
def build_resnet18(num_classes: int = 2, pretrained: bool = True) -> nn.Module:
    """resnet18(weights=IMAGENET1K_V1 if pretrained), model.fc = nn.Linear(512, num_classes)."""
    ...

# From: h-e1/code/data.py (ACTUAL CODE)
def get_dataloaders(root_dir: str, batch_size: int, num_workers: int,
                     img_size: int, norm_mean: tuple, norm_std: tuple) -> dict[str, DataLoader]:
    """Returns {"train": DataLoader, "val": DataLoader, "test": DataLoader}."""
    ...
# WaterbirdsDataset.__getitem__(idx) -> (img: Tensor[3,H,W], y: int, place: int, idx: int)
#   y = bird_label (core), place = background_label (spurious)

# From: h-e1/code/train.py (ACTUAL CODE)
def set_seed(seed: int) -> None: ...
```

**Verified from**: `docs/youra_research/h-m1/03_logic.md` (which verified against actual `h-e1/code/`). Batches are 4-tuples `(img, y, place, idx)`.

---

## A-1/M2-2: Full Checkpointed Training (`train_full.py`) [Complexity: 8, Budget: 8]

**Applied**: Standard PyTorch SGD ERM loop (H-M1 pattern), extended to checkpoint every epoch instead of a fixed subset.

```python
def train_with_full_checkpoints(
    model: nn.Module, loaders: dict, n_epochs: int,
    lr: float, momentum: float, weight_decay: float,
    device: str, ckpt_dir: str,
) -> dict[int, str]:
    """Standard ERM loop; torch.save(model.state_dict(), path) after EVERY epoch (1..n_epochs).
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
        logits = model(imgs)                    # [B, 2]
        loss = criterion(logits, y)
        loss.backward(); optimizer.step(); optimizer.zero_grad()
    path = f"{ckpt_dir}/epoch_{epoch}.pt"
    torch.save(model.state_dict(), path)         # EVERY epoch, unlike H-M1's [5,20,50]
    ckpt_paths[epoch] = path
return ckpt_paths
```

### Subtasks [1/1 for this doc]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | full checkpoint loop | SGD train step + `torch.save` every epoch 1..100 |

---

## A-2/M2-3: Feature Caching (`feature_cache.py`) [Complexity: 7, Budget: 7]

**Applied**: DFR-style frozen-backbone extraction (same as H-M1's `LinearProbeAnalysis`), plus disk cache since 100 epochs would otherwise recompute features repeatedly.

```python
def load_frozen_backbone(checkpoint_path: str, num_classes: int = 2) -> nn.Module:
    """build_resnet18 -> load_state_dict(checkpoint_path) -> model.fc = nn.Identity()
    -> model.eval() -> requires_grad_(False)."""
    ...

def extract_epoch_features(
    backbone: nn.Module, loader: DataLoader, device: str, cache_path: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """no_grad avgpool forward -> 512-dim; returns (features, bird_labels, bg_labels).
    Loads from np.load(cache_path) if exists, else computes + np.savez(cache_path, ...)."""
    ...
```

### Pseudo-code (extract_epoch_features)

```
if os.path.exists(cache_path):
    data = np.load(cache_path)
    return data["features"], data["bird_labels"], data["bg_labels"]

feats_list, y_list, place_list = [], [], []
with torch.no_grad():
    for imgs, y, place, idx in loader:
        f = backbone(imgs.to(device))           # fc=Identity -> [B, 512]
        feats_list.append(f.cpu().numpy())
        y_list.append(y.numpy()); place_list.append(place.numpy())
features = np.concatenate(feats_list)            # [N, 512]
bird_labels = np.concatenate(y_list)             # [N]
bg_labels = np.concatenate(place_list)           # [N]
np.savez(cache_path, features=features, bird_labels=bird_labels, bg_labels=bg_labels)
return features, bird_labels, bg_labels
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| imgs | [B, 3, 224, 224] | input batch |
| features | [N, 512] | avgpool output, all samples for the loader |
| bird_labels | [N] | core (y) |
| bg_labels | [N] | spurious (place) |

### Subtasks [1/1 for this doc]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | extract + cache | no_grad avgpool -> [N,512], npz cache load/save |

---

## A-3/M2-4: Epoch-wise Probe Training (`probe_analysis.py`) [Complexity: 9, Budget: 9]

**Applied**: sklearn LogisticRegression per PRD FR-4 (differs from H-M1's torch nn.Linear probe — PRD explicitly requires sklearn here).

```python
def train_epoch_probes(
    features: np.ndarray, bird_labels: np.ndarray, bg_labels: np.ndarray,
) -> dict[str, float]:
    """LogisticRegression(C=1.0, max_iter=1000, solver="lbfgs"), fit+score separately
    for spurious (bg) and core (bird). Returns {"spurious_acc": float, "core_acc": float}."""
    ...

def run_all_epochs(
    ckpt_paths: dict[int, str], loaders: dict, feature_dim: int,
    device: str, cache_dir: str,
) -> dict[int, dict]:
    """For each of 100 epochs: load_frozen_backbone, extract_epoch_features (train split
    for fit, test split for score), train_epoch_probes.
    Returns {epoch: {"spurious_acc":.., "core_acc":..}}."""
    ...
```

### Pseudo-code (train_epoch_probes)

```
X_train, y_bird_train, y_bg_train = ... (loaders["train"] features)
X_test, y_bird_test, y_bg_test = ... (loaders["test"] features)

clf_spurious = LogisticRegression(C=1.0, max_iter=1000, solver="lbfgs")
clf_spurious.fit(X_train, y_bg_train)
spurious_acc = clf_spurious.score(X_test, y_bg_test)

clf_core = LogisticRegression(C=1.0, max_iter=1000, solver="lbfgs")
clf_core.fit(X_train, y_bird_train)
core_acc = clf_core.score(X_test, y_bird_test)

return {"spurious_acc": spurious_acc, "core_acc": core_acc}
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| X_train / X_test | [N, 512] | cached features |
| y_bird / y_bg | [N] | binary labels (0/1) |

### Subtasks [1/1 for this doc]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | 100-epoch probe loop | load backbone -> extract features -> fit 2x LogisticRegression -> collect dict |

---

## A-4/M2-6,M2-7: Peak Detection & Significance (`peak_detection.py`) [Complexity: 10, Budget: 10]

**Applied**: Moving-average smoothing + argmax (standard signal processing); scipy Wilcoxon signed-rank test.

```python
def find_peak_epoch(accuracies: list[float], window: int = 5) -> int:
    """Smooth via np.convolve(acc, ones(window)/window, mode="valid");
    peak = argmax(smoothed) + window // 2 (re-align to original epoch index, 1-based)."""
    ...

def compute_auc(accuracies: list[float], start: int = 1, end: int = 20) -> float:
    """Trapezoidal AUC (np.trapz) over accuracies[start-1:end]."""
    ...

def wilcoxon_test(spurious_acc: list[float], core_acc: list[float]) -> dict:
    """scipy.stats.wilcoxon(spurious_acc, core_acc).
    Returns {"statistic": float, "p_value": float}."""
    ...
```

### Pseudo-code (find_peak_epoch)

```
kernel = np.ones(window) / window
smoothed = np.convolve(accuracies, kernel, mode="valid")   # len = len(acc) - window + 1
peak_idx = np.argmax(smoothed)
peak_epoch = peak_idx + window // 2 + 1                     # +1 for 1-based epoch numbering
return peak_epoch
```

### Subtasks [2/2 for this doc]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | smoothed peak + AUC | convolve->argmax; trapezoidal AUC(1-20) |
| L-4-2 | wilcoxon_test | scipy.stats.wilcoxon on full 100-epoch curves |

---

## A-5/M2-8,M2-9,M2-10: Verification, Viz, Orchestration (`evaluate.py`, `run_experiment.py`) [Complexity: 15, Budget: 15]

**Applied**: Same verify/plot/orchestrate pattern as H-M1 A-6/A-7/A-8, extended for 100-epoch curves + peak markers.

```python
def verify_mechanism(results: dict[int, dict], spurious_peak: int, core_peak: int) -> dict:
    """Primary: spurious_peak < core_peak. Secondary: AUC(1-20) comparison.
    Returns {"passed": bool, "peak_diff": int, "auc_spurious": float, "auc_core": float}."""
    ...

def plot_learning_curves(
    results: dict[int, dict], spurious_peak: int, core_peak: int, out_path: str,
) -> None:
    """Dual-line plot (spurious_acc vs core_acc over epochs 1..100) + vertical axvline
    at spurious_peak and core_peak. matplotlib, savefig(out_path)."""
    ...

def run_evaluation(results: dict[int, dict], figures_dir: str, metrics_path: str) -> dict:
    """Orchestrates find_peak_epoch x2 (window=5), wilcoxon_test, verify_mechanism,
    plot_learning_curves, saves results+verification to metrics_path (JSON)."""
    ...

def main() -> None:
    """1. set_seed(SEED)
    2. get_dataloaders(DATA_ROOT, BATCH_SIZE, ...)
    3. train_with_full_checkpoints(model, loaders, N_EPOCHS=100, ...) -> ckpt_paths
    4. run_all_epochs(ckpt_paths, loaders, FEATURE_DIM, device, CACHE_DIR) -> results
    5. run_evaluation(results, figures_dir, metrics_path)
    6. assert verify_mechanism(...)["passed"]  # gate: spurious_peak < core_peak"""
    ...
```

### Pseudo-code (verify_mechanism)

```
spurious_series = [results[e]["spurious_acc"] for e in 1..100]
core_series = [results[e]["core_acc"] for e in 1..100]
auc_spurious = compute_auc(spurious_series, 1, 20)
auc_core = compute_auc(core_series, 1, 20)
passed = spurious_peak < core_peak                 # PRIMARY gate
peak_diff = core_peak - spurious_peak
return {"passed": passed, "peak_diff": peak_diff, "auc_spurious": auc_spurious, "auc_core": auc_core}
```

### Subtasks [1/1 for this doc]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | verify+plot+orchestrate | mechanism check, dual-line plot w/ peak markers, wire main(), save metrics.json, gate assertion |

---

## Config (`config.py`)

```python
SEED = 42
DATA_ROOT = "../h-e1/code/data/waterbirds"
BATCH_SIZE = 128
LR = 1e-3
MOMENTUM = 0.9
WEIGHT_DECAY = 1e-4
N_EPOCHS = 100
FEATURE_DIM = 512
PEAK_WINDOW = 5
AUC_RANGE = (1, 20)
CKPT_DIR = "./checkpoints"
CACHE_DIR = "./feature_cache"
```

---

## Data Flow

```
set_seed -> get_dataloaders (shared w/ H-E1)
  -> train_with_full_checkpoints(model, loaders, 100) -> {1..100: path}
  -> run_all_epochs: for each ckpt -> load_frozen_backbone -> extract_epoch_features (cached)
       -> train_epoch_probes -> {epoch: {spurious_acc, core_acc}}
  -> find_peak_epoch(spurious_series) / find_peak_epoch(core_series)  (window=5)
  -> wilcoxon_test(spurious_series, core_series)
  -> verify_mechanism -> {passed, peak_diff, auc_spurious, auc_core}
  -> plot_learning_curves (100 epochs, peak markers) + save metrics.json
  -> gate check: spurious_peak < core_peak must be True
```
