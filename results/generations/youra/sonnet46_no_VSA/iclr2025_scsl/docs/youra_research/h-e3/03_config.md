# Config: H-E3

**Applied: PyTorch flat-constants + dataclass pattern (adapted from pytorch/inductor config.py)**

---

## Codebase Analysis (Serena)

**Project Type**: existing_codebase (h-e1 archive)
**Status**: Architecture doc captures h-e1 patterns; h-e3 follows same flat-constants style, extended with dataclasses per task spec
**Config Files Found**: h-e1 `config.py` (flat constants); h-e3 `code/config.py` to be created
**Pattern Used**: dataclass

---

## C-2-1: Training Hyperparameter Schema [Complexity: 2, Budget: A-2]

**Applied: Standard PyTorch SGD + CosineAnnealingLR defaults**

### Configuration

```python
from dataclasses import dataclass, field
import torch
import torch.nn as nn
import torchvision.models as models
from torchvision.models import ResNet50_Weights


@dataclass
class TrainConfig:
    lr: float = 3e-3                  # izmailovpavel reference
    momentum: float = 0.9
    weight_decay: float = 1e-4
    batch_size: int = 32
    n_epochs: int = 50
    seeds: list = field(default_factory=lambda: [1, 2, 3, 4, 5])
    checkpoint_epochs: list = field(default_factory=lambda: [0, 1, 5, 10, 20, 50])
    pilot_seed: int = 1
    pilot_epochs: int = 5
    scheduler: str = "cosine_annealing"  # CosineAnnealingLR(optimizer, T_max=n_epochs, eta_min=0)
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


def build_optimizer(model: nn.Module, cfg: TrainConfig) -> torch.optim.SGD:
    return torch.optim.SGD(
        model.parameters(),
        lr=cfg.lr,
        momentum=cfg.momentum,
        weight_decay=cfg.weight_decay,
    )


def build_scheduler(optimizer: torch.optim.SGD, cfg: TrainConfig):
    return torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=cfg.n_epochs, eta_min=0
    )


def build_model() -> nn.Module:
    model = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(2048, 2)
    return model
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Training Hyperparameter Schema | TrainConfig dataclass + optimizer/scheduler/model builders |

---

## C-4-1: Metric Schema and Gate Thresholds [Complexity: 4, Budget: A-4]

**Applied: Standard binary classification gate pattern**

### Configuration

```python
@dataclass
class MetricConfig:
    auroc_gate_tstar: float = 0.85    # MUST_WORK threshold at t*
    auroc_gate_t0: float = 0.70       # pretrained artifact guard: AUROC(t=0) must be < this
    spearman_gate: float = 0.80       # rising segment Spearman ρ threshold
    hutchinson_cv_warn: float = 0.10  # CV warning threshold at t* (not a hard gate)
    n_seeds_required: int = 4         # ≥4/5 seeds must pass all 3 gates
    cv_n_resamples: int = 5           # Hutchinson trace resamples for CV estimate


@dataclass
class ResultSchema:
    """Per-seed, per-checkpoint record — mirrors h_e3_results.json leaf structure."""
    seed: int
    checkpoint_epoch: int
    auroc: float
    R: float                          # mean_min / mean_maj
    mean_min: float
    mean_maj: float
    traces_std_min: float
    t_star: int                       # per-seed argmax R(t)
    spearman_rho: float               # over rising segment [0, t_star]
    spearman_p: float
    hutchinson_cv: float              # at t* only
    gate_auroc_tstar: bool            # auroc >= 0.85
    gate_auroc_t0: bool               # auroc_t0 < 0.70
    gate_spearman: bool               # rho >= 0.80
    seed_passes: bool                 # all 3 gates pass
```

### Subtasks [1/2 used — C-4-2 below is second]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-1 | Metric Schema and Gate Thresholds | MetricConfig + ResultSchema dataclasses |

---

## C-4-2: Results I/O Schema [Complexity: 4, Budget: A-4]

**Applied: Structured JSON schema pattern**

### Configuration

```python
# h_e3_results.json top-level structure (write via json.dump)
H_E3_RESULTS_SCHEMA = {
    "hypothesis_id": "H-E3",
    "run_date": "",           # YYYY-MM-DD, filled at runtime
    "config": {},             # TrainConfig + MetricConfig fields as dict
    "pilot": {
        "seed": 1,
        "auroc_t0": 0.0,
        "passed": False,
    },
    "seeds": {
        # key: str(seed), e.g. "1"
        # "<seed>": {
        #     "checkpoints": {
        #         "<epoch>": {
        #             "auroc": float,
        #             "R": float,
        #             "mean_min": float,
        #             "mean_maj": float,
        #             "traces_std_min": float,
        #         },
        #         ...
        #     },
        #     "t_star": int,
        #     "spearman_rho": float,
        #     "spearman_p": float,
        #     "hutchinson_cv": float,
        #     "gate_auroc_tstar": bool,
        #     "gate_auroc_t0": bool,
        #     "gate_spearman": bool,
        #     "seed_passes": bool,
        # }
    },
    "gate": {
        "n_seeds_passing": 0,
        "satisfied": False,
        "per_seed_pass": {},  # {"1": bool, "2": bool, ...}
    },
}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-4-2 | Results I/O Schema | JSON skeleton constant for h_e3_results.json |

---

## C-5-1: Abort Logic and Logging Config [Complexity: 5, Budget: A-5]

**Applied: Standard Python logging.basicConfig pattern**

### Configuration

```python
import logging
import os


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
logger = logging.getLogger(__name__)


PILOT_ABORT_MSG = (
    "ABORT: AUROC(t=0) = {auroc:.4f} >= 0.70 threshold. "
    "Pretrained artifact detected (h-e2 failure mode). "
    "Halting experiment. Route to Phase 0 for signal redesign."
)

LOG_CHECKPOINT_MSG = (
    "Trace computed for N={n_samples} samples at checkpoint t={epoch}, "
    "mean_min={mean_min:.4f}, mean_maj={mean_maj:.4f}, "
    "AUROC={auroc:.4f}, R={R:.4f}"
)


@dataclass
class PathConfig:
    data_root: str = "/home/PrayPrey/data/waterbirds_v1.0/"
    ckpt_dir: str = "docs/youra_research/h-e3/results/checkpoints/"
    results_path: str = "docs/youra_research/h-e3/results/h_e3_results.json"
    figures_dir: str = "docs/youra_research/h-e3/figures/"

    def ckpt_path(self, seed: int, epoch: int) -> str:
        return f"{self.ckpt_dir}ckpt_seed{seed}_epoch{epoch}.pt"

    def makedirs(self) -> None:
        os.makedirs(self.ckpt_dir, exist_ok=True)
        os.makedirs(self.figures_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.results_path), exist_ok=True)
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Abort Logic and Logging Config | PILOT_ABORT_MSG, LOG_CHECKPOINT_MSG, PathConfig with makedirs |
