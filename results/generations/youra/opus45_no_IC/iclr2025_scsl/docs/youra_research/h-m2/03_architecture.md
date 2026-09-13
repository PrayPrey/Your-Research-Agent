# Architecture: H-M2 (MECHANISM)

**Applied**: DFR-style frozen-backbone linear probe pattern, extended to full 100-epoch curve (from H-M1 architecture + experiment brief pseudo-code; Archon KB had no direct epoch-wise-probe / peak-detection matches — general consistency-model training scripts only, not relevant)

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (extends H-M1, which itself extends H-E1)
**Status**: `h-m1/code/` does not yet exist on disk (H-M1 is spec-only at this point) — falling back to H-M1's `03_architecture.md` spec and H-E1's verified module paths (same as H-M1 used).
**Analyzed Path**: `docs/youra_research/h-m1/code/` (not found, 0 files) → used `docs/youra_research/h-m1/03_architecture.md` instead
**Findings**:
- H-E1 provides `build_resnet18(num_classes=2, pretrained=True)` and `get_dataloaders(...)` returning `(img, y, place, idx)` batches — `y`=bird_label (core), `place`=bg_label (spurious). Same contract reused directly.
- H-M1's `train_checkpointed.py` saved only 3 checkpoints (5,20,50); H-M2 needs ALL 100 epochs, so this module must be rewritten, not reused, to checkpoint every epoch.
- H-M1's `probe_model.py`/`probe_train.py` pattern (frozen backbone + sklearn-style probe per checkpoint) is directly reusable in structure, swapped to sklearn LogisticRegression per PRD FR-4 (H-M1 used a torch nn.Linear probe; PRD explicitly requires sklearn here).

---

## File Structure

```
h-m2/code/
  train_full.py       # ERM training, save checkpoint every epoch (1-100)
  feature_cache.py     # Extract+cache 512-dim avgpool features per epoch
  probe_analysis.py    # sklearn LogisticRegression probes (spurious, core) per epoch
  peak_detection.py    # Smoothed peak finding + Wilcoxon test
  evaluate.py           # Mechanism verification + figures
  config.py             # Fixed hyperparameters
  run_experiment.py     # Orchestrates full pipeline
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code / Verified Spec)

| Module | Import Path | File Location |
|--------|-------------|----------------|
| build_resnet18 | `from h_e1.code.model import build_resnet18` | `h-e1/code/model.py` |
| get_dataloaders | `from h_e1.code.data import get_dataloaders, download_waterbirds` | `h-e1/code/data.py` |
| set_seed | `from h_e1.code.train import set_seed` | `h-e1/code/train.py` |

**Verified from**: H-M1's `03_architecture.md` (H-M1 verified these against actual `h-e1/code/` on disk). `get_dataloaders` batches: `(img, y, place, idx)` — `y`=bird_label (core), `place`=bg_label (spurious).

---

## Modules

### Full Training (`train_full.py`)

**Dependencies**: h-e1 build_resnet18/get_dataloaders/set_seed, config.py

```python
def train_with_full_checkpoints(model: nn.Module, loaders: dict, n_epochs: int,
                                 lr: float, momentum: float, weight_decay: float,
                                 device: str, ckpt_dir: str) -> dict[int, str]:
    ...  # standard SGD ERM loop; torch.save(model.state_dict()) after EVERY epoch
         # returns {epoch: checkpoint_path} for epochs 1..100
```

### Feature Caching (`feature_cache.py`)

**Dependencies**: torch, h-e1 build_resnet18

```python
def load_frozen_backbone(checkpoint_path: str, num_classes: int = 2) -> nn.Module: ...
    # build_resnet18, load_state_dict, strip fc, eval(), requires_grad_(False)

def extract_epoch_features(backbone: nn.Module, loader: DataLoader, device: str,
                            cache_path: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    ...  # no_grad avgpool -> 512-dim; returns (features, bird_labels, bg_labels)
         # np.savez(cache_path, ...) to avoid recompute; loads from cache if exists
```

### Probe Analysis (`probe_analysis.py`)

**Dependencies**: sklearn.linear_model.LogisticRegression, feature_cache.py

```python
def train_epoch_probes(features: np.ndarray, bird_labels: np.ndarray,
                        bg_labels: np.ndarray) -> dict[str, float]:
    ...  # LogisticRegression(C=1.0, max_iter=1000, solver="lbfgs")
         # fits + scores separately for spurious (bg) and core (bird)
         # returns {"spurious_acc": float, "core_acc": float}

def run_all_epochs(ckpt_paths: dict[int, str], loaders: dict, feature_dim: int,
                    device: str, cache_dir: str) -> dict[int, dict]:
    ...  # for each of 100 epochs: load_frozen_backbone, extract_epoch_features,
         # train_epoch_probes -> {epoch: {"spurious_acc":.., "core_acc":..}}
```

### Peak Detection (`peak_detection.py`)

**Dependencies**: numpy, scipy.stats.wilcoxon

```python
def find_peak_epoch(accuracies: list[float], window: int = 5) -> int: ...
    # smoothed via np.convolve(ones(window)/window, mode="valid"); argmax + window//2

def compute_auc(accuracies: list[float], start: int = 1, end: int = 20) -> float: ...
    # trapezoidal AUC over epochs[start:end]

def wilcoxon_test(spurious_acc: list[float], core_acc: list[float]) -> dict:
    ...  # scipy.stats.wilcoxon(spurious_acc, core_acc) -> {"statistic":.., "p_value":..}
```

### Evaluation (`evaluate.py`)

**Dependencies**: matplotlib, peak_detection.py

```python
def verify_mechanism(results: dict[int, dict], spurious_peak: int, core_peak: int) -> dict:
    ...  # primary: spurious_peak < core_peak; secondary: AUC(1-20) comparison
         # returns {"passed": bool, "peak_diff": int, "auc_spurious":.., "auc_core":..}

def plot_learning_curves(results: dict[int, dict], spurious_peak: int, core_peak: int,
                          out_path: str) -> None:
    ...  # dual-line plot (spurious vs core acc over 100 epochs) + vertical peak markers

def run_evaluation(results: dict[int, dict], figures_dir: str, metrics_path: str) -> dict:
    ...  # orchestrates find_peak_epoch x2, wilcoxon_test, verify_mechanism,
         # plot_learning_curves, save JSON
```

### Config (`config.py`)

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

### Orchestration (`run_experiment.py`)

**Dependencies**: all modules above

```python
def main() -> None: ...
    # 1. get_dataloaders (shared w/ H-E1)
    # 2. train_with_full_checkpoints -> {1..100: path}
    # 3. run_all_epochs -> {epoch: {"spurious_acc":.., "core_acc":..}}
    # 4. find_peak_epoch x2, run_evaluation(results, figures_dir, metrics_path)
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M2-1 | Reuse data/model wiring | Import H-E1 get_dataloaders/build_resnet18, verify (img,y,place,idx) contract | 3 | 1+2+0+0 |
| M2-2 | Full checkpointed training | ERM loop with model.state_dict() save at every epoch (1-100) | 8 | 3+2+2+1 |
| M2-3 | Feature caching pipeline | Frozen backbone avgpool extraction + disk cache per epoch (100x) | 7 | 2+2+2+1 |
| M2-4 | Epoch-wise probe training | sklearn LogisticRegression spurious+core probes per epoch, 100 iterations | 9 | 2+2+3+2 |
| M2-5 | Full pipeline orchestration | Loop 100 checkpoints -> extract -> probe -> collect results dict | 6 | 1+3+1+1 |
| M2-6 | Peak detection algorithm | Smoothed peak finding (window=5), AUC(1-20) computation | 6 | 2+1+3+0 |
| M2-7 | Statistical significance | Wilcoxon signed-rank test on learning curves | 4 | 1+1+2+0 |
| M2-8 | Mechanism verification | spurious_peak < core_peak check, peak difference report | 4 | 1+1+2+0 |
| M2-9 | Visualization | Dual-line plot (100 epochs) + peak marker vertical lines | 5 | 2+1+1+1 |
| M2-10 | End-to-end run | Wire run_experiment.py, save metrics.json, verify gate | 5 | 1+2+1+1 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [], Medium(9-13): [M2-4], Low(4-8): [M2-1, M2-2, M2-3, M2-5, M2-6, M2-7, M2-8, M2-9, M2-10]
