# Configuration: h-m2 (MECHANISM)

**Type**: MECHANISM — extends h-m1 `Config` with data-fraction subsampling fields, dataclass format

Applied: sample-efficiency-curve-pattern (subsample train set at fixed fractions, retrain from scratch, fixed test set)
Applied: distributional-comparison-pattern (mean±std across seeds, gap-closure metric — reused from h-m1)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: config classes verified from actual h-m1 code (`h-m1/code/config.py` read directly — Serena unavailable, manual fallback per h-m1/h-e1 precedent)
**Config Files Found**: `docs/youra_research/h-m1/code/config.py` (single `@dataclass Config`)
**Pattern Used**: dataclass (inheritance)

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-m1/code/config.py (ACTUAL CODE)
@dataclass
class Config:
    data_dir: str = ".../h-e1/code/data/mnist_inrs"
    batch_size: int = 64
    num_workers: int = 2
    train_split: float = 0.8

    d_model: int = 128
    nhead: int = 4
    num_layers: int = 2
    dws_hidden: int = 128
    mlp_hidden: List[int] = field(default_factory=lambda: [512, 256, 128])
    dropout: float = 0.1
    num_classes: int = 10

    lr: float = 1e-4
    weight_decay: float = 1e-2
    epochs: int = 30
    cosine_t_max: int = 30
    device: str = "cuda"
    seed: int = 42

    seeds: List[int] = field(default_factory=lambda: [42, 123, 7])
    track_every: int = 1
    snapshot_every: int = 10

    wasserstein_threshold: float = 0.1
    early_signature_epoch: int = 20

    results_path: str = ".../h-m1/code/outputs/results.json"
    fig_dir: str = ".../h-m1/figures"
```

**Verified from**: `docs/youra_research/h-m1/code/config.py` (actual implementation)

**Note on PRD deviation**: PRD's `seeds=[42,123,456]` and `Config.seeds=[42,123,7]` (base code) differ — h-m2 keeps base code's `[42, 123, 7]` for consistency with h-m1 results; PRD's TrojAI/binary AUC setup is replaced with the actual 10-class MNIST-INR pipeline per architecture.md (macro-AUC ovr).

---

## S-1/S-2: Extended Config + Subsampling [Complexity: 11, Budget: 2]

**Applied**: sample-efficiency-curve-pattern

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import List
from h_m1.config import Config as BaseConfig  # copy into h-m2/code/config.py, edit in place

@dataclass
class Config(BaseConfig):
    epochs: int = 100                    # unchanged from h-m1 base
    fractions: List[float] = field(default_factory=lambda: [0.25, 0.50, 1.0])  # NEW: sample-efficiency axis

    # Non-standard: results/fig paths repointed to h-m2 output dirs
    results_path: str = ".../h-m2/code/outputs/results.json"
    fig_dir: str = ".../h-m2/figures"
```

`track_every`/`snapshot_every`/`wasserstein_threshold`/`early_signature_epoch` inherited but unused (tracker output discarded in `run_single`, per architecture.md).

No YAML/CLI — hardcode `Config()` in `main.py`, same as h-m1.

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Config + subsample_train | Copy/extend `Config` with `fractions`; implement `subsample_train(train_ds, fraction, seed) -> Subset` (deterministic `torch.Generator(seed)` random subset) |
| C-1-2 | get_fraction_loader + metrics/success-criteria wiring | `get_fraction_loader(train_ds, fraction, seed, cfg) -> DataLoader`; `macro_auc_ovr`, `gap_closure`, `aggregate_stats`, `check_success_criteria` consume `cfg.fractions`/`cfg.seeds` directly, no new config fields |

---

## Remaining Tasks (S-3..S-8)

No config-level parameters beyond `Config` above. `run_sweep.py`/`main.py` iterate `cfg.fractions x cfg.seeds x ["mlp","dws","nft"]`; `train_model_tracked` reused verbatim with existing AdamW/cosine/CE hyperparameters (`lr`, `weight_decay`, `cosine_t_max`, `epochs`); visualization reuses `cfg.fig_dir`, matplotlib `dpi=150` convention from h-e1/h-m1.
