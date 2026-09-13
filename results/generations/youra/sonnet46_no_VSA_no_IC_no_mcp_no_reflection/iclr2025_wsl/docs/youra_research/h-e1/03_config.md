---
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
tier: LIGHT
date: "2026-08-31"
author: "yoon303@ust.ac.kr"
---

# Config: H-E1 — CNN Weight-Space Encoder for Generalization Gap

## Summary

Single fixed config for EXISTENCE PoC. No grid, no ablations, no YAML parsing at runtime.
All values live in `config.py` as typed dataclasses and module-level constants.

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase. Serena skipped per protocol.
**Config Files Found**: None — new config design
**Pattern Used**: dataclass

---

## Applied Citations

Applied: Dataclass-Config — typed Python dataclasses for all config objects; no YAML parsing at runtime.
Applied: Per-Encoder-Config-Dict — one EncoderConfig per encoder type, keyed by name string in ENCODER_CONFIGS.
Applied: Audit-Threshold-Constant — SPEARMAN_AUDIT_THRESHOLD = 0.95 defined once, used in audit.py.
Applied: Train-Val-Test-Split-First — split computed once before any training; seed=42 fixed in AuditConfig.

---

## C-E1-1: ZooDataset and DataLoader Config [Complexity: 5, Budget: 1 subtask]

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E1-1-1 | DataLoader config | DataLoaderConfig dataclass + make_loader signature |

### Configuration

```python
# config.py (partial)
from dataclasses import dataclass, field

@dataclass
class DataLoaderConfig:
    batch_size: int = 64
    shuffle: bool = True
    num_workers: int = 4
    pin_memory: bool = True
```

`make_loader` signature (in `data/loader.py`):
```python
def make_loader(zoo: ZooData, split: str, config: DataLoaderConfig) -> DataLoader: ...
```

Split values: `"train"` | `"val"` | `"test"` — selects `zoo.idx_train / idx_val / idx_test`.

**Non-standard**: NFT overrides `batch_size=32` at call site (memory constraint from cross-layer attention).

---

## C-E1-2: Zoo Download and Path Config [Complexity: 5, Budget: 1 subtask]

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-E1-2-1 | ZooConfig + AuditConfig | Path, URL, audit threshold, split seed |

### Configuration

```python
@dataclass
class ZooConfig:
    zoo_path: str = "data/cifar10_zoo.npz"
    osf_url: str = "https://osf.io/hbm72/"
    fallback_url: str = "https://github.com/google-research/google-research/tree/master/cnns_weight_prediction"
    expected_n_models: int = 10_000

@dataclass
class AuditConfig:
    spearman_threshold: float = 0.95   # Non-standard: hard stop if gap ≈ -test_acc
    seed: int = 42
    split_ratios: list = field(default_factory=lambda: [0.8, 0.1, 0.1])
```

`spearman_threshold=0.95` from PRD FR-0.1 (gap must not be a near-linear transform of test_acc).

---

## Full EncoderConfig Schema

Values taken directly from PRD Table FR-3.1.

```python
@dataclass
class EncoderConfig:
    lr_candidates: list
    batch_size: int
    epochs: int
    lr_schedule: str    # "none" | "cosine"
    hidden_dim: int

ENCODER_CONFIGS: dict[str, EncoderConfig] = {
    "FlatMLP": EncoderConfig(
        lr_candidates=[1e-4, 5e-4, 1e-3],
        batch_size=64,
        epochs=100,
        lr_schedule="none",
        hidden_dim=256,
    ),
    "DWSNet": EncoderConfig(
        lr_candidates=[1e-4, 5e-4, 1e-3],
        batch_size=64,
        epochs=100,
        lr_schedule="none",
        hidden_dim=256,
    ),
    "NFT": EncoderConfig(
        lr_candidates=[1e-5, 1e-4, 5e-4],
        batch_size=32,      # Non-standard: reduced for cross-layer attention memory
        epochs=200,         # Non-standard: 2x epochs; transformer needs more warm-up
        lr_schedule="cosine",
        hidden_dim=256,
    ),
    "GNN": EncoderConfig(
        lr_candidates=[1e-4, 5e-4, 1e-3],
        batch_size=64,
        epochs=100,
        lr_schedule="cosine",
        hidden_dim=256,
    ),
}
```

---

## ExperimentConfig Top-Level Dataclass

```python
@dataclass
class ExperimentConfig:
    zoo: ZooConfig = field(default_factory=ZooConfig)
    encoders: dict = field(default_factory=lambda: ENCODER_CONFIGS)
    loader: DataLoaderConfig = field(default_factory=DataLoaderConfig)
    audit: AuditConfig = field(default_factory=AuditConfig)
    n_trials: int = 50
    gate_threshold: float = 0.5
    figures_dir: str = "h-e1/figures"
    seed: int = 42
```

---

## YAML Schema (Human-Readable Reference)

```yaml
experiment:
  seed: 42
  n_trials: 50
  gate_threshold: 0.5
  figures_dir: "h-e1/figures"

  zoo:
    zoo_path: "data/cifar10_zoo.npz"
    osf_url: "https://osf.io/hbm72/"
    fallback_url: "https://github.com/google-research/google-research/tree/master/cnns_weight_prediction"
    expected_n_models: 10000

  audit:
    spearman_threshold: 0.95
    seed: 42
    split_ratios: [0.8, 0.1, 0.1]

  loader:
    batch_size: 64
    shuffle: true
    num_workers: 4
    pin_memory: true

  encoders:
    FlatMLP:
      lr_candidates: [1.0e-4, 5.0e-4, 1.0e-3]
      batch_size: 64
      epochs: 100
      lr_schedule: "none"
      hidden_dim: 256
    DWSNet:
      lr_candidates: [1.0e-4, 5.0e-4, 1.0e-3]
      batch_size: 64
      epochs: 100
      lr_schedule: "none"
      hidden_dim: 256
    NFT:
      lr_candidates: [1.0e-5, 1.0e-4, 5.0e-4]
      batch_size: 32
      epochs: 200
      lr_schedule: "cosine"
      hidden_dim: 256
    GNN:
      lr_candidates: [1.0e-4, 5.0e-4, 1.0e-3]
      batch_size: 64
      epochs: 100
      lr_schedule: "cosine"
      hidden_dim: 256
```

---

## Complete config.py (Copy-Paste Ready)

```python
# h-e1/config.py
from dataclasses import dataclass, field


@dataclass
class ZooConfig:
    zoo_path: str = "data/cifar10_zoo.npz"
    osf_url: str = "https://osf.io/hbm72/"
    fallback_url: str = "https://github.com/google-research/google-research/tree/master/cnns_weight_prediction"
    expected_n_models: int = 10_000


@dataclass
class AuditConfig:
    spearman_threshold: float = 0.95
    seed: int = 42
    split_ratios: list = field(default_factory=lambda: [0.8, 0.1, 0.1])


@dataclass
class DataLoaderConfig:
    batch_size: int = 64
    shuffle: bool = True
    num_workers: int = 4
    pin_memory: bool = True


@dataclass
class EncoderConfig:
    lr_candidates: list
    batch_size: int
    epochs: int
    lr_schedule: str
    hidden_dim: int


ENCODER_CONFIGS: dict[str, EncoderConfig] = {
    "FlatMLP": EncoderConfig(
        lr_candidates=[1e-4, 5e-4, 1e-3],
        batch_size=64,
        epochs=100,
        lr_schedule="none",
        hidden_dim=256,
    ),
    "DWSNet": EncoderConfig(
        lr_candidates=[1e-4, 5e-4, 1e-3],
        batch_size=64,
        epochs=100,
        lr_schedule="none",
        hidden_dim=256,
    ),
    "NFT": EncoderConfig(
        lr_candidates=[1e-5, 1e-4, 5e-4],
        batch_size=32,
        epochs=200,
        lr_schedule="cosine",
        hidden_dim=256,
    ),
    "GNN": EncoderConfig(
        lr_candidates=[1e-4, 5e-4, 1e-3],
        batch_size=64,
        epochs=100,
        lr_schedule="cosine",
        hidden_dim=256,
    ),
}

SPEARMAN_AUDIT_THRESHOLD: float = 0.95   # from AuditConfig; defined here for audit.py import


@dataclass
class ExperimentConfig:
    zoo: ZooConfig = field(default_factory=ZooConfig)
    encoders: dict = field(default_factory=lambda: ENCODER_CONFIGS)
    loader: DataLoaderConfig = field(default_factory=DataLoaderConfig)
    audit: AuditConfig = field(default_factory=AuditConfig)
    n_trials: int = 50
    gate_threshold: float = 0.5
    figures_dir: str = "h-e1/figures"
    seed: int = 42
```
