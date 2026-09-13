# Configuration: H-M1
# Graph Representation as Cross-Architecture Generalization Mechanism

Applied: standard-DL-config-dataclass (no weight-space patterns in Archon KB)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis (H-E1 incremental extension)
**Status**: Config verified from H-E1 actual code (`h-e1/code/config.py`)
**Config Files Found**: `docs/youra_research/h-e1/code/config.py` (flat constants module, not dataclasses)
**Pattern Used**: dataclass (H-M1 introduces structured dataclasses over H-E1's flat constants)

---

## Inherited Configuration (Base Hypothesis)

H-E1 uses a flat constants module (verified from actual code):

```python
# From: docs/youra_research/h-e1/code/config.py (ACTUAL CODE)
HIDDEN_DIM   = 256
LATENT_DIM   = 128
NUM_LAYERS   = 4
LR           = 1e-3
WEIGHT_DECAY = 1e-4
BETAS        = (0.9, 0.999)
BATCH_SIZE   = 64
EPOCHS       = 100
T_MAX        = 100
ETA_MIN      = 1e-5
TEMPERATURE  = 0.07
LAMBDA_SWEEP = [0.01, 0.1, 1.0, 10.0]
SEEDS        = [0, 1, 2, 3, 4]
VAL_FRACTION = 0.1
```

H-M1 fixes `lambda_rec = 0.1` (best from H-E1 sweep) and wraps all values in dataclasses.

**Verified from**: `docs/youra_research/h-e1/code/config.py` (actual implementation)

---

## Core Config (`code/config.py`)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class EquiSSLPermConfig:
    symmetry: str = "permutation"
    # Encoder dims — verified from H-E1: HIDDEN_DIM=256, LATENT_DIM=128, NUM_LAYERS=4
    hidden_dim: int = 256
    latent_dim: int = 128
    num_layers: int = 4
    # Training — verified from H-E1: LR=1e-3, WEIGHT_DECAY=1e-4, BATCH_SIZE=64, EPOCHS=100
    lr: float = 1e-3
    weight_decay: float = 1e-4
    betas: tuple = (0.9, 0.999)
    batch_size: int = 64
    epochs: int = 100
    # Scheduler — verified from H-E1: T_MAX=100, ETA_MIN=1e-5
    t_max: int = 100
    eta_min: float = 1e-5
    # SSL objective — verified from H-E1: TEMPERATURE=0.07; lambda fixed at best H-E1 value
    temperature: float = 0.07
    lambda_rec: float = 0.1
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])

@dataclass
class LinearProbeConfig:
    alphas: List[float] = field(default_factory=lambda: [0.1, 1.0, 10.0, 100.0])
    test_size: float = 0.2
    seeds: List[int] = field(default_factory=lambda: [0, 1, 2, 3, 4])

@dataclass
class PathConfig:
    he1_checkpoint_dir: str = "docs/youra_research/h-e1/checkpoints"
    checkpoint_dir: str = "docs/youra_research/h-m1/checkpoints"
    results_dir: str = "docs/youra_research/h-m1/results"
    figures_dir: str = "docs/youra_research/h-m1/figures"
    vit_zoo_root: str = "data/vitzoo"
    multizoo_root: str = "data/multizoo"

@dataclass
class ExperimentConfig:
    equi_perm: EquiSSLPermConfig = field(default_factory=EquiSSLPermConfig)
    probe: LinearProbeConfig = field(default_factory=LinearProbeConfig)
    paths: PathConfig = field(default_factory=PathConfig)
    device: str = "cuda"
```

---

## YAML Schema (`code/config.yaml`)

```yaml
device: cuda

equi_perm:
  symmetry: permutation
  hidden_dim: 256
  latent_dim: 128
  num_layers: 4
  lr: 1.0e-3
  weight_decay: 1.0e-4
  betas: [0.9, 0.999]
  batch_size: 64
  epochs: 100
  t_max: 100
  eta_min: 1.0e-5
  temperature: 0.07
  lambda_rec: 0.1
  seeds: [0, 1, 2, 3, 4]

probe:
  alphas: [0.1, 1.0, 10.0, 100.0]
  test_size: 0.2
  seeds: [0, 1, 2, 3, 4]

paths:
  he1_checkpoint_dir: docs/youra_research/h-e1/checkpoints
  checkpoint_dir: docs/youra_research/h-m1/checkpoints
  results_dir: docs/youra_research/h-m1/results
  figures_dir: docs/youra_research/h-m1/figures
  vit_zoo_root: data/vitzoo
  multizoo_root: data/multizoo
```

---

## A-7: Figure Generation [Complexity: 12, Budget: 3 subtasks]

Applied: standard-DL-config-dataclass (no weight-space patterns in Archon KB)

### C-7-1: Bar Chart + Ablation Ladder Config [subtask 1/3]

```python
@dataclass
class BarChartConfig:
    output_path: str = "docs/youra_research/h-m1/figures/r2_bar_chart.png"
    ablation_output_path: str = "docs/youra_research/h-m1/figures/ablation_ladder.png"
    dpi: int = 150
    style: str = "seaborn-v0_8"
    figsize: tuple = (8, 5)
    # Color per model — consistent across all figures
    colors: dict = field(default_factory=lambda: {
        "SANE": "#4C72B0",
        "EquiSSL-perm": "#DD8452",
        "EquiSSL": "#55A868",
    })
    capsize: int = 5          # error bar cap width
    threshold_linestyle: str = "dashed"
    threshold_color: str = "gray"
```

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Bar + Ablation Config | `BarChartConfig` for R² bar chart with error bars and ablation grouped bars |

### C-7-2: t-SNE 4-Panel Config [subtask 2/3]

```python
@dataclass
class TSNEConfig:
    output_path: str = "docs/youra_research/h-m1/figures/tsne_comparison.png"
    dpi: int = 150
    style: str = "seaborn-v0_8"
    figsize: tuple = (16, 4)
    # sklearn TSNE params — use max_iter (not n_iter) per H-E1 bug fix NFR-4
    perplexity: int = 30
    max_iter: int = 1000      # Non-standard name: sklearn renamed n_iter -> max_iter (sklearn>=1.2)
    random_state: int = 0
    # 4 panels: SANE, EquiSSL-perm, EquiSSL, + placeholder slot
    panels: List[str] = field(default_factory=lambda: ["SANE", "EquiSSL-perm", "EquiSSL", "EquiSSL-perm (seed0)"])
    cmap: str = "tab10"       # colored by architecture family
    alpha: float = 0.7
    point_size: int = 20
```

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-2 | t-SNE Config | `TSNEConfig` for 4-panel t-SNE with perplexity, max_iter (H-E1 bug fix applied), colormap |

### C-7-3: Paired Scatter + Histogram Config [subtask 3/3]

```python
@dataclass
class ScatterHistConfig:
    scatter_output_path: str = "docs/youra_research/h-m1/figures/paired_seed_scatter.png"
    hist_output_path: str = "docs/youra_research/h-m1/figures/vit_accuracy_hist.png"
    dpi: int = 150
    style: str = "seaborn-v0_8"
    scatter_figsize: tuple = (6, 6)
    hist_figsize: tuple = (7, 4)
    scatter_alpha: float = 0.8
    scatter_point_size: int = 60
    diagonal_color: str = "gray"   # dots above diagonal = improvement
    hist_bins: int = 20
    hist_color: str = "#4C72B0"
```

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-3 | Scatter + Histogram Config | `ScatterHistConfig` for paired seed R² scatter and ViT accuracy histogram |

---

## A-8: Report & Orchestration [Complexity: 9, Budget: 1 subtask]

Applied: standard-DL-config-dataclass (no weight-space patterns in Archon KB)

### C-8-1: Orchestration Config [subtask 1/1]

Argparse flags for `run_experiment.py`:

```python
# run_experiment.py argparse schema
def get_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="H-M1 experiment pipeline")
    p.add_argument("--config", default="code/config.yaml", help="YAML config path")
    p.add_argument("--device", default=None, help="Override device (cuda/cpu)")
    p.add_argument("--skip-train", action="store_true", help="Skip EquiSSL-perm training (use existing checkpoints)")
    p.add_argument("--skip-figures", action="store_true", help="Skip figure generation")
    p.add_argument("--wandb", action="store_true", help="Enable WandB logging (optional)")
    p.add_argument("--wandb-project", default="h-m1-equissl-perm")
    p.add_argument("--log-csv", default="docs/youra_research/h-m1/results/run_log.csv")
    return p
```

CSV logging schema (always-on fallback):

```python
# CSV columns written per seed per model
CSV_COLUMNS = [
    "model",        # SANE | EquiSSL | EquiSSL-perm
    "seed",         # 0-4
    "r2_test",      # float
    "alpha_best",   # float (best RidgeCV alpha)
    "epoch",        # final epoch (training only)
    "loss_final",   # float (training only, NaN for frozen reuse)
]
```

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | Orchestration Config | argparse schema + CSV logging columns for `run_experiment.py` |

---

## Subtask Summary

| ID | Task | Subtask | Description |
|----|------|---------|-------------|
| C-7-1 | A-7 | Bar + Ablation Config | `BarChartConfig` for R² bar + ablation grouped bars |
| C-7-2 | A-7 | t-SNE Config | `TSNEConfig` 4-panel, max_iter bug fix applied |
| C-7-3 | A-7 | Scatter + Histogram Config | `ScatterHistConfig` paired scatter + ViT accuracy histogram |
| C-8-1 | A-8 | Orchestration Config | argparse + CSV logging schema |

Total: 4 subtasks (within budget).
