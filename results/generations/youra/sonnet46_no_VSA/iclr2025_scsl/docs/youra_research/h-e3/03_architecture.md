# Architecture: H-E3

**Applied: checkpoint-per-epoch measurement pattern (adapted from h-e1 pipeline)**

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (h-e1 archive)
**Status**: patterns found from base code
**Analyzed Path**: `docs/youra_research/_archive/20260803T064034_routing_recovery/h-e1/code/`
**Findings**: h-e1 uses `WaterbirdsDataset`, `config.py` constants, `run_experiment.py` seed loop, `metrics.py` with `compute_minority_auroc` and `compute_spearman_pd`. H-E3 reuses these patterns directly; no h-e2-k code found in the active tree (archive only), so interfaces are reconstructed from PRD pseudo-code.

---

## File Organization

```
docs/youra_research/h-e3/code/
├── config.py               # All constants (hyperparams, paths, checkpoint epochs)
├── data.py                 # WaterbirdsDataset + dataloaders
├── train_erm.py            # ERM training loop, checkpoint saves at t∈{0,1,5,10,20,50}
├── compute_traces.py       # K=50 Hutchinson trace via vmap+vjp (last-fc only)
├── evaluate_trajectory.py  # AUROC, R(t), Spearman ρ, gate check, figures
└── run_experiment.py       # Pilot gate → full 5-seed loop → save results
```

```
docs/youra_research/h-e3/
├── figures/                # All 5 figure outputs
└── results/
    └── h_e3_results.json   # Per-seed, per-checkpoint structured results
```

---

## Modules

### Config (`code/config.py`)

**Dependencies**: none

```python
DATA_ROOT: str = "/home/PrayPrey/data/waterbirds_v1.0/"
CKPT_DIR: str = "docs/youra_research/h-e3/results/checkpoints/"
RESULTS_PATH: str = "docs/youra_research/h-e3/results/h_e3_results.json"
FIGURES_DIR: str = "docs/youra_research/h-e3/figures/"

LR: float = 3e-3
MOMENTUM: float = 0.9
WEIGHT_DECAY: float = 1e-4
BATCH_SIZE: int = 32
N_EPOCHS: int = 50
CHECKPOINT_EPOCHS: list[int] = [0, 1, 5, 10, 20, 50]
SEEDS: list[int] = [1, 2, 3, 4, 5]
PILOT_SEED: int = 1
PILOT_EPOCHS: int = 5
K_HUTCHINSON: int = 50
DEVICE: str = "cuda"

MINORITY_GROUPS: tuple = (1, 3)
MAJORITY_GROUPS: tuple = (0, 2)
IMAGENET_MEAN: list = [0.485, 0.456, 0.406]
IMAGENET_STD: list = [0.229, 0.224, 0.225]

def set_seed(seed: int) -> None: ...
def ensure_dirs() -> None: ...
def ckpt_path(seed: int, epoch: int) -> str: ...
```

---

### Data (`code/data.py`)

**Dependencies**: config

```python
class WaterbirdsDataset(Dataset):
    def __init__(self, root: str, split: int, transform=None): ...
    # split: 0=train, 1=val, 2=test
    # Attributes: img_paths, y, group, minority_mask (bool tensor)
    def __len__(self) -> int: ...
    def __getitem__(self, idx: int) -> tuple[Tensor, int, int]: ...
    # returns (image, label, group)

def get_train_loader(root: str, batch_size: int) -> DataLoader: ...
def get_eval_loader(root: str, split: int, batch_size: int) -> DataLoader: ...
# eval_loader: no shuffle, deterministic order (required for trace alignment)
```

---

### ERM Training (`code/train_erm.py`)

**Dependencies**: config, data

```python
def build_model() -> nn.Module:
    # resnet50(IMAGENET1K_V1), replace fc with nn.Linear(2048, 2)
    ...

def save_checkpoint(model: nn.Module, seed: int, epoch: int) -> None: ...
def load_checkpoint(seed: int, epoch: int, device: str) -> nn.Module: ...

def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: Optimizer,
    scheduler,
    device: str,
) -> float:
    # Returns mean loss
    ...

def run_training(
    seed: int,
    n_epochs: int,
    checkpoint_epochs: list[int],
    device: str,
) -> None:
    # Saves checkpoint at epoch=0 BEFORE first gradient update
    # Saves at each epoch in checkpoint_epochs
    ...
```

---

### Hutchinson Trace (`code/compute_traces.py`)

**Dependencies**: config

```python
def extract_features(model: nn.Module, inputs: Tensor, device: str) -> Tensor:
    # Backbone forward with torch.no_grad(); returns (N, 2048)
    ...

def compute_per_sample_fc_trace(
    model: nn.Module,
    loader: DataLoader,
    K: int = 50,
    device: str = "cuda",
) -> Tensor:
    # Returns (N,) trace tensor for full dataset
    # Uses vmap+vjp Hutchinson on model.fc parameters only
    # Processes in batches; concatenates results
    ...

def compute_traces_for_checkpoint(
    seed: int,
    epoch: int,
    loader: DataLoader,
    K: int = 50,
    device: str = "cuda",
) -> Tensor:
    # Loads checkpoint, calls compute_per_sample_fc_trace, returns (N,)
    ...

def compute_hutchinson_cv(
    model: nn.Module,
    loader: DataLoader,
    n_resamples: int = 5,
    K: int = 50,
    device: str = "cuda",
) -> float:
    # std(resamples) / mean(resamples) — run at t* only
    ...

def verify_architecture(model: nn.Module) -> None:
    # assert isinstance(model.fc, nn.Linear)
    # assert model.fc.out_features == 2
    # assert model.fc.in_features == 2048
    ...
```

---

### Evaluation + Figures (`code/evaluate_trajectory.py`)

**Dependencies**: config, compute_traces

```python
def compute_auroc(traces: Tensor, minority_mask: Tensor) -> float:
    # roc_auc_score(minority_mask.cpu(), traces.cpu())
    ...

def compute_R(traces: Tensor, minority_mask: Tensor) -> float:
    # mean(traces[minority]) / mean(traces[majority])
    ...

def compute_spearman(
    t_values: list[int],
    auroc_values: list[float],
) -> tuple[float, float]:
    # spearmanr over rising segment; returns (rho, p_value)
    ...

def evaluate_seed(
    seed: int,
    loader: DataLoader,
    minority_mask: Tensor,
    checkpoint_epochs: list[int],
    device: str,
) -> dict:
    # Returns per-checkpoint {epoch: {auroc, R, mean_min, mean_maj, traces_std_min}}
    # Computes t*, Spearman ρ, Hutchinson CV at t*
    ...

def check_gate(all_seed_results: dict) -> tuple[bool, dict]:
    # Counts seeds passing all 3 primary criteria
    # Returns (gate_satisfied, per_seed_pass)
    ...

def verify_mechanism_activated(checkpoint_results: dict, t_star: int) -> tuple[bool, dict]: ...

# --- Figures ---
def plot_gate_metrics(all_seed_results: dict, out_dir: str) -> None:
    # fig1_gate_metrics.png — bar chart AUROC(t=0) vs AUROC(t*)
    ...

def plot_R_trajectory(all_seed_results: dict, out_dir: str) -> None:
    # fig2_R_trajectory.png — R(t) mean±std, t* annotated
    ...

def plot_auroc_trajectory(all_seed_results: dict, out_dir: str) -> None:
    # fig3_auroc_trajectory.png — per-seed + mean AUROC(t)
    ...

def plot_trace_distribution(all_seed_results: dict, minority_mask: Tensor, out_dir: str) -> None:
    # fig4_trace_distribution.png — violin at t*, minority vs majority
    ...

def plot_spearman_rising(all_seed_results: dict, out_dir: str) -> None:
    # fig5_spearman_rising.png — scatter AUROC vs epoch over rising segment
    ...
```

---

### Orchestration (`code/run_experiment.py`)

**Dependencies**: config, data, train_erm, compute_traces, evaluate_trajectory

```python
def run_pilot(device: str) -> bool:
    # seed=1, 5 epochs, compute trace at t=0, check AUROC(t=0) < 0.70
    # Returns True if safe to continue, False if abort
    ...

def main() -> None:
    # 1. run_pilot() — abort if AUROC(t=0) >= 0.70
    # 2. for seed in SEEDS: run_training(seed, N_EPOCHS, CHECKPOINT_EPOCHS, device)
    # 3. for seed in SEEDS: evaluate_seed(...) → collect all_seed_results
    # 4. check_gate(all_seed_results) → log verdict
    # 5. save all_seed_results to RESULTS_PATH
    # 6. generate all 5 figures
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| A-1 | Setup & Data | config.py + data.py; WaterbirdsDataset loading and split verification | 7 | 2+1+1+3 |
| A-2 | ERM Training | train_erm.py; ResNet-50 build, SGD+cosine, checkpoint saves at t∈{0,1,5,10,20,50} with t=0 pre-training save | 10 | 2+2+3+3 |
| A-3 | Hutchinson Trace | compute_traces.py; vmap+vjp per-sample fc-trace, Rademacher probes, batch processing, architecture verify | 14 | 3+3+5+3 |
| A-4 | Metrics & Gate | evaluate_trajectory.py metrics (AUROC, R(t), Spearman ρ, CV); gate logic across 5 seeds | 9 | 2+2+3+2 |
| A-5 | Pilot Gate + Orchestration | run_experiment.py; pilot abort logic, full seed loop, JSON results save | 8 | 2+3+2+1 |
| A-6 | Figures | 5 required plots (gate metrics, R(t), AUROC trajectory, trace distribution, Spearman scatter) | 9 | 2+1+2+4 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [A-3], Medium(9-13): [A-2, A-4, A-5, A-6], Low(4-8): [A-1]

---

## Dependency Graph

```
config.py
    └─ data.py
    └─ train_erm.py
    └─ compute_traces.py ─── evaluate_trajectory.py
                                    └─ run_experiment.py (top-level)
```

---

## Key Interface Notes for Phase 4

- `WaterbirdsDataset.__getitem__` returns `(image, label, group)` — group needed for minority mask
- `minority_mask` is a boolean tensor of shape `(N_train,)` built once from metadata: `group ∈ {1, 3}`
- `compute_per_sample_fc_trace` processes in batches but returns a single concatenated `(N,)` tensor — caller must ensure eval loader is **non-shuffled** so indices align with minority mask
- `t=0` checkpoint is saved BEFORE calling `optimizer.step()` for the first Waterbirds batch — this is the pretrained-artifact control
- `evaluate_seed` stores raw traces at t* for `plot_trace_distribution` (needed for per-sample violin)
- Pilot run reuses `run_training(seed=1, n_epochs=5, checkpoint_epochs=[0], ...)` then calls `compute_traces_for_checkpoint(seed=1, epoch=0, ...)` — full 5-epoch pilot not needed for gate, only t=0 trace
