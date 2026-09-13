# Configuration Design: H-E1 — Sharpness Anisotropy in SSL Loss Landscapes

**Hypothesis:** H-E1 (EXISTENCE)
**Phase:** 3 — Implementation Planning
**Date:** 2026-08-21
**Author:** yoon303@etri.re.kr

---

**Applied:** Standard DL Config Dataclass Pattern (hierarchical dataclasses → YAML serialization → CLI override)

---

## Overview

All experiment hyperparameters are encoded as Python dataclasses with typed defaults. The master `ExperimentConfig` composes all sub-configs and serializes to YAML for reproducibility. CLI arguments map 1:1 to dataclass fields.

---

## Subtask C-2-1: SSL Method Config Dataclasses

**Parent Epic:** A-2 (SSL pre-training runners, complexity 14)

```python
from dataclasses import dataclass, field
from typing import List

@dataclass
class SimCLRConfig:
    # Loss
    temperature: float = 0.5
    projection_dim: int = 128
    # Optimizer
    lr: float = 0.03
    momentum: float = 0.9
    weight_decay: float = 1e-4
    # Training
    batch_size: int = 256
    epochs: int = 200
    checkpoint_epochs: List[int] = field(default_factory=lambda: [50, 100, 150, 200])
    # Augmentation
    crop_scale_min: float = 0.2
    crop_scale_max: float = 1.0
    color_jitter_strength: float = 0.4
    grayscale_prob: float = 0.2
    gaussian_blur_prob: float = 0.5

@dataclass
class MoCoV2Config:
    # Loss / queue
    temperature: float = 0.2
    queue_size: int = 65536       # K in paper
    momentum_encoder: float = 0.999  # m in paper
    projection_dim: int = 128
    # Optimizer (same as SimCLR)
    lr: float = 0.03
    momentum: float = 0.9
    weight_decay: float = 1e-4
    # Training
    batch_size: int = 256
    epochs: int = 200
    checkpoint_epochs: List[int] = field(default_factory=lambda: [50, 100, 150, 200])
    # Augmentation: same as SimCLR
    crop_scale_min: float = 0.2
    crop_scale_max: float = 1.0

@dataclass
class DINOConfig:
    # Teacher EMA schedule
    teacher_momentum_start: float = 0.996
    teacher_momentum_end: float = 1.0
    # Temperature (teacher/student)
    teacher_temp: float = 0.04
    student_temp: float = 0.1
    # Optimizer (AdamW for DINO)
    lr: float = 1e-4
    weight_decay: float = 0.04
    weight_decay_end: float = 0.4
    # Training
    batch_size: int = 256
    epochs: int = 200
    checkpoint_epochs: List[int] = field(default_factory=lambda: [50, 100, 150, 200])
    # Multi-crop
    global_crops_scale: tuple = (0.4, 1.0)
    local_crops_scale: tuple = (0.05, 0.4)
    local_crops_number: int = 8
```

---

## Subtask C-2-2: Dataset Config Dataclasses

**Parent Epic:** A-2 (complexity 14)

```python
@dataclass
class WaterbirdsConfig:
    name: str = "waterbirds"
    root_dir: str = "./data/waterbirds"
    # Download info for Phase 4
    download_url: str = "https://nlp.stanford.edu/data/dro/waterbird_complete95_forest2water2.tar.gz"
    archive_name: str = "waterbird_complete95_forest2water2.tar.gz"
    extracted_name: str = "waterbird_complete95_forest2water2"
    # Dataset stats
    n_groups: int = 4
    n_classes: int = 2
    img_size: int = 224
    resize_size: int = 256
    # ImageNet normalization
    mean: List[float] = field(default_factory=lambda: [0.485, 0.456, 0.406])
    std: List[float] = field(default_factory=lambda: [0.229, 0.224, 0.225])
    # Loader
    loader_type: str = "wilds"  # "wilds" | "groupdro"

@dataclass
class CelebAConfig:
    name: str = "celeba"
    root_dir: str = "./data/celeba"
    n_groups: int = 4
    n_classes: int = 2
    img_size: int = 224
    resize_size: int = 256
    mean: List[float] = field(default_factory=lambda: [0.485, 0.456, 0.406])
    std: List[float] = field(default_factory=lambda: [0.229, 0.224, 0.225])
    loader_type: str = "wilds"  # auto-download via WILDS

@dataclass
class CMNISTConfig:
    name: str = "cmnist"
    root_dir: str = "./data/cmnist"
    n_groups: int = 4
    n_classes: int = 2
    spurious_correlation_strength: float = 0.99
    img_size: int = 28   # MNIST native; no resize needed
    loader_type: str = "torchvision"  # auto-download
```

---

## Subtask C-3-1: Linear Probe Config

**Parent Epic:** A-3 (linear probe trainer, complexity 11)

```python
@dataclass
class ProbeConfig:
    # Optimizer
    lr: float = 0.01
    momentum: float = 0.9
    weight_decay: float = 0.0   # no regularization for probe
    # Training
    batch_size: int = 256
    epochs: int = 100
    # Architecture
    feature_dim: int = 2048     # ResNet-50 backbone output
    # Evaluation
    eval_batch_size: int = 512
    # Loss proxy for spurious direction
    spurious_quantile: float = 0.75   # top-25% high-loss = spurious proxy
```

---

## Subtask C-7-1: Experiment Orchestration Config

**Parent Epic:** A-7 (CLI orchestration, complexity 11)

```python
@dataclass
class AnisotropyMeasurementConfig:
    rho: float = 0.05             # SAM perturbation radius
    n_random: int = 100           # random direction baselines
    spurious_quantile: float = 0.75
    batch_size: int = 256

@dataclass
class ExperimentConfig:
    # Run matrix
    ssl_methods: List[str] = field(default_factory=lambda: ["simclr", "mocov2", "dino"])
    datasets: List[str] = field(default_factory=lambda: ["waterbirds", "celeba", "cmnist"])
    # Paths
    data_root: str = "./data"
    checkpoint_dir: str = "./checkpoints/h_e1"
    results_dir: str = "./docs/youra_research/h-e1"
    figures_dir: str = "./docs/youra_research/h-e1/figures"
    # Reproducibility
    seed: int = 1
    device: str = "cuda"
    # Execution control
    skip_training_if_exists: bool = True  # resume-safe
    skip_measurement_if_exists: bool = True
    # Sub-configs
    simclr: SimCLRConfig = field(default_factory=SimCLRConfig)
    mocov2: MoCoV2Config = field(default_factory=MoCoV2Config)
    dino: DINOConfig = field(default_factory=DINOConfig)
    waterbirds: WaterbirdsConfig = field(default_factory=WaterbirdsConfig)
    celeba: CelebAConfig = field(default_factory=CelebAConfig)
    cmnist: CMNISTConfig = field(default_factory=CMNISTConfig)
    probe: ProbeConfig = field(default_factory=ProbeConfig)
    anisotropy: AnisotropyMeasurementConfig = field(default_factory=AnisotropyMeasurementConfig)
    # Gate thresholds (from H-E1 hypothesis statement)
    gate_anisotropy_ratio_threshold: float = 1.2
    gate_pearson_r_threshold: float = 0.5
    gate_p_value_threshold: float = 0.05
    gate_min_passing_combinations: int = 7   # ≥7/9 must pass
```

---

## YAML Schema Example

Full experiment config serialized to YAML (excerpt):

```yaml
# config/experiment_h_e1.yaml
ssl_methods: [simclr, mocov2, dino]
datasets: [waterbirds, celeba, cmnist]
data_root: ./data
checkpoint_dir: ./checkpoints/h_e1
results_dir: ./docs/youra_research/h-e1
figures_dir: ./docs/youra_research/h-e1/figures
seed: 1
device: cuda
skip_training_if_exists: true

simclr:
  temperature: 0.5
  projection_dim: 128
  lr: 0.03
  momentum: 0.9
  weight_decay: 0.0001
  batch_size: 256
  epochs: 200
  checkpoint_epochs: [50, 100, 150, 200]

mocov2:
  temperature: 0.2
  queue_size: 65536
  momentum_encoder: 0.999
  projection_dim: 128
  lr: 0.03
  batch_size: 256
  epochs: 200

dino:
  teacher_momentum_start: 0.996
  teacher_momentum_end: 1.0
  lr: 0.0001
  weight_decay: 0.04
  batch_size: 256
  epochs: 200

probe:
  lr: 0.01
  epochs: 100
  spurious_quantile: 0.75

anisotropy:
  rho: 0.05
  n_random: 100
  spurious_quantile: 0.75

gate_anisotropy_ratio_threshold: 1.2
gate_pearson_r_threshold: 0.5
gate_p_value_threshold: 0.05
gate_min_passing_combinations: 7
```

---

## CLI Argument Mapping

| CLI Flag | Config Field | Default |
|----------|-------------|---------|
| `--ssl-methods` | `ExperimentConfig.ssl_methods` | `simclr mocov2 dino` |
| `--datasets` | `ExperimentConfig.datasets` | `waterbirds celeba cmnist` |
| `--data-root` | `ExperimentConfig.data_root` | `./data` |
| `--checkpoint-dir` | `ExperimentConfig.checkpoint_dir` | `./checkpoints/h_e1` |
| `--seed` | `ExperimentConfig.seed` | `1` |
| `--device` | `ExperimentConfig.device` | `cuda` |
| `--rho` | `ExperimentConfig.anisotropy.rho` | `0.05` |
| `--n-random` | `ExperimentConfig.anisotropy.n_random` | `100` |
| `--skip-training` | `ExperimentConfig.skip_training_if_exists` | `true` |
| `--config` | load from YAML file | — |

---

## Results YAML Schema (Phase 4 Output Target)

```yaml
# results/h_e1_results.yaml — written by Phase 4 experiment code
hypothesis: H-E1
date: "2026-08-21"
seed: 1

combinations:
  simclr_waterbirds:
    checkpoints:
      50:  {anisotropy_ratio: 1.31, spurious_increase: 0.042, mean_random_increase: 0.032, wga: 0.38}
      100: {anisotropy_ratio: 1.45, spurious_increase: 0.058, mean_random_increase: 0.040, wga: 0.41}
      150: {anisotropy_ratio: 1.52, spurious_increase: 0.063, mean_random_increase: 0.041, wga: 0.43}
      200: {anisotropy_ratio: 1.61, spurious_increase: 0.071, mean_random_increase: 0.044, wga: 0.44}
    pearson_r: -0.97
    p_value: 0.03
    gate_passed: true   # ratio > 1.2 in all 4, |r| > 0.5, p < 0.05

gate_summary:
  combinations_passing_ratio: 8   # of 9
  combinations_passing_pearson: 7  # of 9
  gate_satisfied: true
  verdict: PASS
```

---

## Hyperparameter Registry

| Parameter | Value | Source | Module |
|-----------|-------|--------|--------|
| SimCLR temperature τ | 0.5 | izmailovpavel/spurious_feature_learning | SimCLRConfig |
| SimCLR projection dim | 128 | Standard SimCLR | SimCLRConfig |
| MoCo-v2 temperature τ | 0.2 | facebookresearch/moco | MoCoV2Config |
| MoCo-v2 queue size K | 65536 | facebookresearch/moco | MoCoV2Config |
| MoCo-v2 momentum m | 0.999 | facebookresearch/moco | MoCoV2Config |
| DINO teacher momentum start | 0.996 | facebookresearch/dino | DINOConfig |
| SSL lr | 0.03 | izmailovpavel/spurious_feature_learning | *Config |
| SSL weight_decay | 1e-4 | Standard | *Config |
| SSL batch_size | 256 | Standard | *Config |
| SSL epochs | 200 | Standard for PoC | *Config |
| Probe lr | 0.01 | izmailovpavel/spurious_feature_learning | ProbeConfig |
| Probe epochs | 100 | Standard linear eval | ProbeConfig |
| SAM rho | 0.05 | davda54/sam default | AnisotropyMeasurementConfig |
| Spurious quantile | 0.75 | Ghaznavi 2023 LFR top-25% | ProbeConfig |
| n_random baselines | 100 | Statistical robustness (PoC) | AnisotropyMeasurementConfig |
| Seed | 1 | PoC single-seed | ExperimentConfig |
