# Architecture: H-E1 (EXISTENCE PoC)

**Applied**: group_DRO-style Waterbirds Dataset handling + JTT-style per-sample loss tracking (from experiment brief; Archon KB had no direct matches)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: Green-field project, no existing code
**Analyzed Path**: N/A
**Findings**: New implementation from scratch

---

## File Structure

```
h-e1/code/
  data.py        # Waterbirds download + Dataset/DataLoader
  model.py        # ResNet-18 baseline + OnsetDelayTracker
  train.py        # ERM training loop with per-sample loss logging
  evaluate.py      # Minority detection metrics, Mann-Whitney U, figures
  config.py        # Fixed hyperparameters
```

---

## Modules

### WaterbirdsDataset (`data.py`)

**Dependencies**: torchvision.transforms, pandas, PIL

```python
class WaterbirdsDataset(Dataset):
    def __init__(self, root_dir: str, split: str): ...  # split in {"train","val","test"}
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> tuple[Tensor, int, int, int]: ...  # img, y, place, group_idx

def download_waterbirds(root_dir: str) -> None: ...  # wget + tar -xzf if not present
def get_dataloaders(root_dir: str, batch_size: int) -> dict[str, DataLoader]: ...  # {"train","val","test"}
def is_minority(y: np.ndarray, place: np.ndarray) -> np.ndarray: ...  # bool array, y != place
```

### Model + Tracker (`model.py`)

**Dependencies**: torchvision.models, numpy

```python
def build_resnet18(num_classes: int = 2) -> nn.Module: ...  # pretrained, fc replaced

class OnsetDelayTracker:
    def __init__(self, n_samples: int, threshold: float = 0.9): ...
    def update(self, epoch: int, sample_indices: np.ndarray, losses: np.ndarray) -> None: ...
    def predict_minority(self, T_early: int = 20) -> np.ndarray: ...  # bool array
    def get_onset_delays(self) -> np.ndarray: ...  # d_i per sample
```

### Training (`train.py`)

**Dependencies**: model.py, data.py, config.py

```python
def train_erm(model: nn.Module, loaders: dict, tracker: OnsetDelayTracker,
              n_epochs: int, lr: float, momentum: float, weight_decay: float,
              device: str) -> OnsetDelayTracker: ...  # logs per-sample loss each epoch

def set_seed(seed: int) -> None: ...
```

### Evaluation (`evaluate.py`)

**Dependencies**: sklearn.metrics, scipy.stats, matplotlib

```python
def compute_gate_metrics(d_i: np.ndarray, minority_mask: np.ndarray, T_early: int) -> dict: ...  # precision, recall
def mann_whitney_test(d_i: np.ndarray, minority_mask: np.ndarray) -> tuple[float, float]: ...  # stat, pvalue
def plot_gate_metrics_bar(results: dict, out_path: str) -> None: ...
def plot_onset_delay_histogram(d_i: np.ndarray, minority_mask: np.ndarray, out_path: str) -> None: ...
def plot_loss_trajectories(loss_history: np.ndarray, minority_mask: np.ndarray, out_path: str) -> None: ...
def plot_precision_recall_curve(d_i: np.ndarray, minority_mask: np.ndarray, out_path: str) -> None: ...  # T_early sweep 1-50
def run_evaluation(tracker: OnsetDelayTracker, minority_mask: np.ndarray, figures_dir: str) -> dict: ...  # orchestrates all above
```

### Config (`config.py`)

```python
SEED = 42
DATA_URL = "https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz"
BATCH_SIZE = 64
LR = 1e-3
MOMENTUM = 0.9
WEIGHT_DECAY = 1e-4
N_EPOCHS = 100
T_EARLY = 20
ONSET_THRESHOLD = 0.9
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Data pipeline | Download Waterbirds, parse metadata.csv, build Dataset/DataLoader with group labels | 8 | 3+2+2+1 |
| A-2 | Model setup | ResNet-18 pretrained, replace fc layer for 2-class output | 3 | 1+1+1+0 |
| A-3 | OnsetDelayTracker | Implement per-sample loss tracker, d_i computation, minority prediction | 6 | 2+1+3+0 |
| A-4 | ERM training loop | Per-sample unreduced CE loss, tracker update each epoch, SGD optimizer, 100 epochs | 9 | 3+3+2+1 |
| A-5 | Detection metrics | Precision/recall at T_early=20 vs ground-truth minority groups | 4 | 1+2+1+0 |
| A-6 | Statistical test | Mann-Whitney U test, minority vs majority d_i | 3 | 1+1+1+0 |
| A-7 | Figures | Gate metrics bar chart, onset delay histogram, loss trajectories, PR curve vs T_early | 7 | 2+2+2+1 |
| A-8 | End-to-end run | Wire train.py + evaluate.py, save metrics JSON, verify gate condition | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [A-1, A-4], Low(4-8): [A-2, A-3, A-5, A-6, A-7, A-8]
