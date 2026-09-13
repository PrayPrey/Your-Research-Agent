# Architecture: H-M1 (MECHANISM)

**Applied**: DFR-style frozen-backbone linear probe pattern (from experiment brief; Archon KB had no direct simplicity-bias matches, general PyTorch docs only)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-E1)
**Status**: H-E1 actual code inspected (not just spec) - `build_resnet18`, `get_dataloaders`, `train_erm`, `Config` verified in `h-e1/code/`
**Analyzed Path**: `docs/youra_research/h-e1/code/`
**Findings**:
- `model.py::build_resnet18(num_classes=2, pretrained=True) -> nn.Module` — matches spec exactly.
- `data.py::get_dataloaders(root_dir, batch_size, num_workers, img_size, norm_mean, norm_std) -> dict[str, DataLoader]` — `WaterbirdsDataset.__getitem__` returns `(img, y, place, idx)`, i.e. y=bird label, place=background label. Directly usable as (bird_label, bg_label) for probes.
- `train.py::train_erm(model, loaders, tracker, n_epochs, lr, momentum, weight_decay, device)` — trains ERM, has `OnsetDelayTracker` coupling; H-M1 needs checkpoint saving at specific epochs, so a new `train_checkpointed.py` variant is required (can't reuse train_erm as-is, no checkpoint saving hook).
- `config.py::Config` is a dataclass — H-M1 will use its own `Config` with checkpoint epochs added, importing shared constants where useful.

---

## File Structure

```
h-m1/code/
  probe_model.py    # LinearProbeAnalysis: feature extraction + spurious/core probes
  train_checkpointed.py  # ERM training with checkpoint save at epochs 5,20,50
  probe_train.py    # Train+eval linear probes per checkpoint
  evaluate.py        # Mechanism verification, figures
  config.py          # Fixed hyperparameters (extends H-E1 config values)
  run_experiment.py  # Orchestrates: train base model -> probes per ckpt -> verify -> figures
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| build_resnet18 | `from h_e1.code.model import build_resnet18` | `h-e1/code/model.py` |
| WaterbirdsDataset / get_dataloaders | `from h_e1.code.data import get_dataloaders, download_waterbirds` | `h-e1/code/data.py` |
| set_seed | `from h_e1.code.train import set_seed` | `h-e1/code/train.py` |

**Verified from**: `docs/youra_research/h-e1/code/` (actual implementation). Note: `get_dataloaders` batch yields `(img, y, place, idx)` — `y`=bird_label (core), `place`=bg_label (spurious).

---

## Modules

### LinearProbeAnalysis (`probe_model.py`)

**Dependencies**: torch, torch.nn.functional, h-e1 build_resnet18

```python
class LinearProbeAnalysis(nn.Module):
    def __init__(self, backbone: nn.Module, feature_dim: int = 512): ...
    def extract_features(self, x: Tensor) -> Tensor: ...  # no_grad, avgpool -> (B, 512)

def load_frozen_backbone(checkpoint_path: str, num_classes: int = 2) -> nn.Module: ...  # build_resnet18, load_state_dict, strip fc, eval(), requires_grad_(False)
```

### Checkpointed Training (`train_checkpointed.py`)

**Dependencies**: h-e1 build_resnet18/get_dataloaders/set_seed, config.py

```python
def train_with_checkpoints(model: nn.Module, loaders: dict, n_epochs: int,
                            checkpoint_epochs: list[int], lr: float, momentum: float,
                            weight_decay: float, device: str, ckpt_dir: str) -> dict[int, str]:
    ...  # returns {epoch: checkpoint_path}; standard ERM loop, torch.save(model.state_dict()) at checkpoint_epochs
```

### Probe Training (`probe_train.py`)

**Dependencies**: probe_model.py, sklearn.metrics

```python
def train_probe(probe: nn.Linear, backbone: nn.Module, loader: DataLoader,
                label_idx: int, epochs: int, lr: float, device: str) -> nn.Linear: ...
    # label_idx: 1=y(bird/core), 2=place(bg/spurious) from (img,y,place,idx) batch

def eval_probe(probe: nn.Linear, backbone: nn.Module, loader: DataLoader,
               label_idx: int, device: str) -> float: ...  # accuracy_score

def run_probes_for_checkpoint(ckpt_path: str, loaders: dict, feature_dim: int,
                               probe_epochs: float, lr: float, device: str) -> dict: ...
    # returns {"spurious_acc": float, "core_acc": float}
```

### Evaluation (`evaluate.py`)

**Dependencies**: matplotlib

```python
def verify_mechanism(results: dict) -> dict: ...  # bias_exists, core_improves bools; results keyed "epoch_5"/"epoch_20"/"epoch_50"
def plot_probe_accuracy_curve(results: dict, out_path: str) -> None: ...  # spurious vs core line plot across epochs
def run_evaluation(results: dict, figures_dir: str, metrics_path: str) -> dict: ...  # orchestrates verify + plot + save JSON
```

### Config (`config.py`)

```python
SEED = 42
DATA_ROOT = "../h-e1/code/data/waterbirds"  # reuse downloaded data
BATCH_SIZE = 64
LR = 1e-3
MOMENTUM = 0.9
WEIGHT_DECAY = 1e-4
N_EPOCHS = 50
CHECKPOINT_EPOCHS = [5, 20, 50]
PROBE_LR = 0.01
PROBE_EPOCHS = 10
FEATURE_DIM = 512
CKPT_DIR = "./checkpoints"
```

### Orchestration (`run_experiment.py`)

**Dependencies**: all modules above

```python
def main() -> None: ...
    # 1. get_dataloaders (shared w/ H-E1)
    # 2. train_with_checkpoints -> {5: path, 20: path, 50: path}
    # 3. for each ckpt: load_frozen_backbone, run_probes_for_checkpoint
    # 4. run_evaluation(results, figures_dir, metrics_path)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Reuse data/model wiring | Import H-E1 get_dataloaders/build_resnet18, verify (img,y,place,idx) contract | 3 | 1+2+0+0 |
| M-2 | Checkpointed training | ERM loop with model.state_dict() save at epochs 5,20,50 | 7 | 2+2+2+1 |
| M-3 | LinearProbeAnalysis module | Frozen backbone feature extraction (avgpool, no_grad, 512-dim) | 5 | 2+1+2+0 |
| M-4 | Probe train/eval | SGD linear probes (spurious, core), 10 epochs each, per checkpoint | 8 | 2+2+3+1 |
| M-5 | Checkpoint loop orchestration | Load each of 3 checkpoints, run both probes, collect results dict | 6 | 1+3+1+1 |
| M-6 | Mechanism verification | spurious_acc(5)>core_acc(5) check, core improvement check | 4 | 1+1+2+0 |
| M-7 | Visualization | Line plot spurious vs core accuracy across epochs 5/20/50 | 4 | 1+1+1+1 |
| M-8 | End-to-end run | Wire run_experiment.py, save metrics.json, verify gate | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [], Low(4-8): [M-1, M-2, M-3, M-4, M-5, M-6, M-7, M-8]
