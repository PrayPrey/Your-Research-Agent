# Architecture: H-M1 — Differential Confidence Trajectory Verification

**Date:** 2026-08-04
**Type:** MECHANISM (PoC — Continuation)
**Applied:** group-wise evaluation loop (DFR pattern — PolinaKirichenko/deep_feature_reweighting)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-E3 extension)
**Status:** Patterns found from base code
**Analyzed Path:** `docs/youra_research/h-e3/code/`
**Findings:** H-E3 has `evaluate_seed()` iterating over checkpoints with Hessian trace; H-M1 replaces trace computation with softmax confidence extraction. `WaterbirdsDataset.__init__` builds `minority_mask` at line 24 using `(group==1)|(group==2)`. `get_eval_loader(root, split, batch_size)` returns a shuffle=False DataLoader. `config.py` has `ckpt_path(seed, epoch)` helper, `CHECKPOINT_EPOCHS`, `SEEDS`, `DEVICE` constants.

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| WaterbirdsDataset | `sys.path.insert(0, h_e3_code); from data import WaterbirdsDataset` | `docs/youra_research/h-e3/code/data.py:12` |
| get_eval_loader | `from data import get_eval_loader` | `docs/youra_research/h-e3/code/data.py:61` |
| config.ckpt_path | `from config import ckpt_path, CHECKPOINT_EPOCHS, SEEDS, DEVICE` | `docs/youra_research/h-e3/code/config.py` |

**Verified from:** `docs/youra_research/h-e3/code/` (actual implementation)

**Note:** H-E3 `minority_mask` in `WaterbirdsDataset` is computed as `(group==1)|(group==2)` (line 24 of data.py) — matches H-M1 definition. No adaptation needed.

**Note:** H-E3 `evaluate_seed()` loads checkpoints via `load_checkpoint(seed, epoch, device)` (evaluate_trajectory.py). H-M1 reuses same pattern but replaces `compute_traces_for_checkpoint()` with `extract_confidence_by_group()`.

---

## File Organization

- `docs/youra_research/h-m1/code/config.py` — H-M1 config (extends H-E3 constants)
- `docs/youra_research/h-m1/code/compute_confidence.py` — core confidence extraction + trajectory loop
- `docs/youra_research/h-m1/code/visualize.py` — 4 required figures
- `docs/youra_research/h-m1/code/run_experiment.py` — main orchestrator
- `docs/youra_research/h-m1/results/confidence_results.json` — output
- `docs/youra_research/h-m1/figures/` — fig_gate_metrics.png, fig_confidence_trajectory.png, fig_conf_distribution.png, fig_boundary_fraction.png

---

## Module Definitions

### Config (`docs/youra_research/h-m1/code/config.py`)

**Dependencies:** none (standalone constants)

```python
import sys, os

# Path injection for H-E3 reuse
H_E3_CODE = os.path.abspath("docs/youra_research/h-e3/code")

DATA_ROOT: str = "/home/PrayPrey/data/waterbirds_v1.0/"
CKPT_DIR: str = "docs/youra_research/h-e3/code/outputs/checkpoints"
RESULTS_PATH: str = "docs/youra_research/h-m1/results/confidence_results.json"
FIGURES_DIR: str = "docs/youra_research/h-m1/figures"

CHECKPOINT_EPOCHS: list = [0, 1, 5, 10, 20, 50]
SEEDS: list = [1, 2, 3, 4, 5]
TSTAR_PER_SEED: dict = {1: 20, 2: 50, 3: 50, 4: 20, 5: 5}  # from H-E3 04_validation.md

BATCH_SIZE: int = 256
DEVICE: str = "cuda"

# Gate thresholds
GATE_P_MIN_LOW: float = 0.3
GATE_P_MIN_HIGH: float = 0.7
GATE_P_MAJ: float = 0.80
GATE_N_SEEDS: int = 4

def ckpt_path(seed: int, epoch: int) -> str: ...
def ensure_dirs() -> None: ...
```

---

### ConfidenceExtractor (`docs/youra_research/h-m1/code/compute_confidence.py`)

**Dependencies:** config, H-E3 data.py (via sys.path), torchvision.models

```python
import torch
import torch.nn.functional as F
from torch import Tensor

def build_model(device: str) -> torch.nn.Module:
    """ResNet-50 with fc replaced by Linear(2048, 2). Returns model skeleton (no weights)."""
    ...

def load_checkpoint(seed: int, epoch: int, model: torch.nn.Module, device: str) -> torch.nn.Module:
    """Load state_dict from H-E3 checkpoint; return model.eval()."""
    ...

def extract_confidence_by_group(
    model: torch.nn.Module,
    loader,
    minority_mask: Tensor,
    device: str,
) -> tuple[Tensor, float, float]:
    """
    Forward pass on full training set.
    Returns: (p_per_sample [N], p_minority scalar, p_majority scalar)
    p_i = softmax(logits)[y_i] (confidence in true class)
    """
    ...

def compute_trajectory(seed: int, model: torch.nn.Module, loader, minority_mask: Tensor, device: str) -> dict:
    """
    Iterates CHECKPOINT_EPOCHS for one seed.
    Returns: {epoch: {'p_min': float, 'p_maj': float, 'p_per_sample': Tensor}}
    """
    ...

def check_gate(p_min: float, p_maj: float) -> tuple[bool, bool]:
    """Returns (primary_pass, secondary_pass) per gate thresholds."""
    ...

def verify_mechanism_activated(results_per_seed: dict) -> tuple[bool, dict]:
    """
    Args: {seed: {t: {'p_min', 'p_maj'}, 'tstar': int}}
    Returns: (mechanism_active bool, per-seed indicators dict)
    """
    ...

def save_results(results_per_seed: dict, mechanism_active: bool, gate_pass_count: int) -> None:
    """Serialize to RESULTS_PATH JSON."""
    ...
```

---

### Visualizer (`docs/youra_research/h-m1/code/visualize.py`)

**Dependencies:** compute_confidence (results dict), matplotlib, config

```python
def plot_gate_metrics(results_per_seed: dict) -> None:
    """fig_gate_metrics.png — p_min(t*) and p_maj(t*) per seed with threshold lines."""
    ...

def plot_confidence_trajectory(results_per_seed: dict) -> None:
    """fig_confidence_trajectory.png — p_min(t) and p_maj(t) vs t per seed (5 lines each group)."""
    ...

def plot_conf_distribution(results_per_seed: dict) -> None:
    """fig_conf_distribution.png — box plot of p_per_sample at t* for minority vs majority."""
    ...

def plot_boundary_fraction(results_per_seed: dict) -> None:
    """fig_boundary_fraction.png — fraction of minority samples with p∈[0.3,0.7] at each t."""
    ...

def save_all_figures(results_per_seed: dict) -> None:
    """Calls all four plot functions; saves to FIGURES_DIR."""
    ...
```

---

### Runner (`docs/youra_research/h-m1/code/run_experiment.py`)

**Dependencies:** config, compute_confidence, visualize, H-E3 data.py

```python
def main() -> None:
    """
    1. ensure_dirs()
    2. Build model skeleton once; build loader once (split=0, train)
    3. For each seed: compute_trajectory() → store results
    4. verify_mechanism_activated() → log gate result
    5. save_results()
    6. save_all_figures()
    """
    ...

if __name__ == "__main__":
    main()
```

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M1-1 | Config & paths | config.py with H-E3 path injection, ckpt_path helper, gate constants | 5 | 1+1+1+2 |
| M1-2 | Model skeleton & checkpoint loader | build_model() + load_checkpoint() reusing H-E3 pattern | 7 | 2+2+1+2 |
| M1-3 | Confidence extraction | extract_confidence_by_group(): forward pass → softmax → group split | 8 | 2+2+2+2 |
| M1-4 | Trajectory loop | compute_trajectory() iterating 6 checkpoints per seed; store p_per_sample for viz | 9 | 2+2+2+3 |
| M1-5 | Gate + mechanism verification | check_gate(), verify_mechanism_activated(), assert shape invariants | 7 | 2+1+2+2 |
| M1-6 | Result persistence | save_results() → JSON with summary block; ensure_dirs() | 5 | 1+1+1+2 |
| M1-7 | Gate metrics figure | fig_gate_metrics.png with threshold overlays (MANDATORY) | 7 | 2+1+2+2 |
| M1-8 | Trajectory & distribution figures | fig_confidence_trajectory + fig_conf_distribution (requires p_per_sample) | 9 | 2+2+3+2 |
| M1-9 | Boundary fraction figure | fig_boundary_fraction: fraction of minority in [0.3,0.7] per checkpoint | 7 | 2+1+2+2 |
| M1-10 | Main runner & integration test | run_experiment.py orchestration; smoke test (single seed single checkpoint) | 10 | 2+2+3+3 |

**Distribution:** VeryHigh(18-20): [] | High(14-17): [] | Medium(9-13): [M1-4, M1-8, M1-10] | Low(4-8): [M1-1, M1-2, M1-3, M1-5, M1-6, M1-7, M1-9]

**Total complexity:** 74 | **Task count:** 10
