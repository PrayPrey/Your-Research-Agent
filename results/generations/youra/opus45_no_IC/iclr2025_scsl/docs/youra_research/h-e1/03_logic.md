# Logic: H-E1 (EXISTENCE PoC)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field, no existing code
**Analyzed Path**: N/A
**Relevant Symbols**: None - new implementation

**Applied**: Standard PyTorch (no direct KB match for per-sample loss tracking; JTT-style methodology per architecture doc)

---

## A-1: Data Pipeline [Complexity: 8, Budget: 8]

**Applied**: Standard PyTorch Dataset/DataLoader

### API Signatures

```python
class WaterbirdsDataset(Dataset):
    def __init__(self, root_dir: str, split: str):
        """split in {"train","val","test"}, reads metadata.csv."""
        ...
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> tuple[Tensor, int, int, int]:
        """Returns (img [3,224,224], y, place, group_idx)."""
        ...

def download_waterbirds(root_dir: str) -> None: ...  # no-op if already extracted
def get_dataloaders(root_dir: str, batch_size: int) -> dict[str, DataLoader]: ...
def is_minority(y: np.ndarray, place: np.ndarray) -> np.ndarray:
    """bool [N], True where y != place."""
    ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| img | [3, 224, 224] | normalized, ImageNet stats |
| y, place, group_idx | scalar int | per sample |
| batch img | [B, 3, 224, 224] | B=64 |

### Subtasks [4/4]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | download_waterbirds | wget + tar -xzf, skip if exists |
| L-1-2 | WaterbirdsDataset | metadata.csv parse + transforms |
| L-1-3 | get_dataloaders | shuffle train, no shuffle val/test |
| L-1-4 | is_minority | vectorized comparison |

---

## A-2: Model Setup [Complexity: 3, Budget: 3]

**Applied**: torchvision pretrained model, standard fc replacement

```python
def build_resnet18(num_classes: int = 2) -> nn.Module:
    """resnet18(pretrained=True); model.fc = nn.Linear(512, num_classes)."""
    ...
```

Input `[B, 3, 224, 224]` -> logits `[B, 2]`.

### Subtasks [3/3]

| ID | Subtask | Description |
|----|---------|--------------|
| L-2-1 | load pretrained | torchvision.models.resnet18(weights=...) |
| L-2-2 | replace fc | nn.Linear(512, num_classes) |
| L-2-3 | device transfer | .to(device) |

---

## A-3: OnsetDelayTracker [Complexity: 6, Budget: 6]

**Applied**: Standard PyTorch (custom per-sample state, JTT methodology)

### API Signatures

```python
class OnsetDelayTracker:
    def __init__(self, n_samples: int, threshold: float = 0.9):
        """loss_history: [n_samples, 0] growing list; threshold applied to L_i(0)."""
        ...

    def update(self, epoch: int, sample_indices: np.ndarray, losses: np.ndarray) -> None:
        """sample_indices [B], losses [B] (unreduced CE per-sample this epoch)."""
        ...

    def predict_minority(self, T_early: int = 20) -> np.ndarray:
        """bool [n_samples], True where onset_delay > T_early."""
        ...

    def get_onset_delays(self) -> np.ndarray:
        """int [n_samples], d_i per sample (inf/-1 if never crossed threshold)."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| loss_matrix | [n_samples, n_epochs] | filled incrementally per epoch |
| initial_loss L_i(0) | [n_samples] | captured at epoch 0 |
| d_i | [n_samples] | int, -1 sentinel if no onset observed |

### Pseudo-code

```
init: loss_matrix = full((n_samples, n_epochs), nan)

update(epoch, sample_indices, losses):
    loss_matrix[sample_indices, epoch] = losses

get_onset_delays():
    L0 = loss_matrix[:, 0]                       # [N]
    target = threshold * L0                      # [N]
    below = loss_matrix < target[:, None]         # [N, n_epochs]
    d_i = argmax(below, axis=1) where any(below, axis=1) else -1
    return d_i

predict_minority(T_early):
    d_i = get_onset_delays()
    return d_i > T_early   # -1 (never onset) counts as minority (delay effectively infinite)
```

### Subtasks [3/3]

| ID | Subtask | Description |
|----|---------|--------------|
| L-3-1 | __init__/update | preallocate loss_matrix, in-place fill |
| L-3-2 | get_onset_delays | vectorized threshold crossing (argmax on bool mask) |
| L-3-3 | predict_minority | threshold d_i > T_early |

---

## A-4: ERM Training Loop [Complexity: 9, Budget: 9]

**Applied**: Standard PyTorch SGD training loop with unreduced loss

### API Signatures

```python
def train_erm(
    model: nn.Module, loaders: dict, tracker: OnsetDelayTracker,
    n_epochs: int, lr: float, momentum: float, weight_decay: float,
    device: str,
) -> OnsetDelayTracker:
    """CrossEntropyLoss(reduction='none') per batch; tracker.update() each epoch."""
    ...

def set_seed(seed: int) -> None: ...  # torch, np, random
```

### Pseudo-code

```
optimizer = SGD(model.parameters(), lr, momentum, weight_decay)
criterion = CrossEntropyLoss(reduction='none')

for epoch in range(n_epochs):
    model.train()
    for imgs, y, place, group_idx, sample_idx in loaders["train"]:
        imgs, y = imgs.to(device), y.to(device)
        logits = model(imgs)                # [B, 2]
        per_sample_loss = criterion(logits, y)  # [B]
        loss = per_sample_loss.mean()
        loss.backward(); optimizer.step(); optimizer.zero_grad()
        tracker.update(epoch, sample_idx.numpy(), per_sample_loss.detach().cpu().numpy())
return tracker
```

**Note**: `WaterbirdsDataset.__getitem__` must also return `sample_idx` (=idx) so DataLoader batches carry global indices for tracker updates. Update A-1 signature: `__getitem__` returns `(img, y, place, group_idx, idx)` — 5-tuple (revise from A-1's 4-tuple; A-4 depends on it).

### Subtasks [4/4]

| ID | Subtask | Description |
|----|---------|--------------|
| L-4-1 | optimizer/criterion setup | SGD + unreduced CE |
| L-4-2 | train step | forward, per-sample loss, backward |
| L-4-3 | tracker.update call | per batch, per epoch |
| L-4-4 | set_seed | torch/np/random determinism |

---

## A-5/A-6: Detection Metrics + Statistical Test [Complexity: 7, Budget: 7]

**Applied**: sklearn precision_recall, scipy.stats.mannwhitneyu

```python
def compute_gate_metrics(d_i: np.ndarray, minority_mask: np.ndarray, T_early: int) -> dict:
    """{'precision': float, 'recall': float}; pred = d_i > T_early vs minority_mask."""
    ...

def mann_whitney_test(d_i: np.ndarray, minority_mask: np.ndarray) -> tuple[float, float]:
    """one-sided (minority > majority): mannwhitneyu(d_i[minority], d_i[~minority], alternative='greater')."""
    ...
```

### Subtasks [3/3]

| ID | Subtask | Description |
|----|---------|--------------|
| L-5-1 | compute_gate_metrics | sklearn precision_score/recall_score |
| L-5-2 | mann_whitney_test | scipy mannwhitneyu, alternative='greater' |
| L-5-3 | edge case handling | -1 sentinel treated as max delay before test |

---

## A-7: Figures [Complexity: 7, Budget: 7]

**Applied**: matplotlib standard plotting

```python
def plot_gate_metrics_bar(results: dict, out_path: str) -> None: ...
def plot_onset_delay_histogram(d_i: np.ndarray, minority_mask: np.ndarray, out_path: str) -> None: ...
def plot_loss_trajectories(loss_history: np.ndarray, minority_mask: np.ndarray, out_path: str) -> None:
    """loss_history [N, n_epochs]; samples 20 (10 minority, 10 majority) for line plot."""
    ...
def plot_precision_recall_curve(d_i: np.ndarray, minority_mask: np.ndarray, out_path: str) -> None:
    """sweep T_early in range(1, 51), plot precision/recall vs T_early."""
    ...
```

### Subtasks [4/4]

| ID | Subtask | Description |
|----|---------|--------------|
| L-7-1 | gate_metrics_bar | precision/recall bars |
| L-7-2 | onset_delay_histogram | grouped by minority_mask |
| L-7-3 | loss_trajectories | sample 20, plot lines |
| L-7-4 | precision_recall_curve | T_early sweep 1-50 |

---

## A-8: End-to-End Run [Complexity: 5, Budget: 5]

```python
def run_evaluation(tracker: OnsetDelayTracker, minority_mask: np.ndarray, figures_dir: str) -> dict:
    """Orchestrates A-5/A-6/A-7, returns metrics dict, checks gate condition."""
    ...
```

### Subtasks [3/3]

| ID | Subtask | Description |
|----|---------|--------------|
| L-8-1 | wire train+evaluate | main script calling train_erm then run_evaluation |
| L-8-2 | save metrics JSON | precision, recall, p-value to results.json |
| L-8-3 | verify gate condition | assert precision>0.5 and recall>0.3 and p<0.05 |

---

## Data Flow

```
download_waterbirds -> WaterbirdsDataset -> get_dataloaders
  -> train_erm(model, loaders, tracker) [per-epoch: forward -> per-sample CE -> tracker.update]
  -> tracker.get_onset_delays() -> d_i [N]
  -> is_minority(y, place) -> minority_mask [N]
  -> run_evaluation(tracker, minority_mask) -> {precision, recall, p_value} + figures
  -> gate check (precision>0.5, recall>0.3, p<0.05)
```
