# Config: H-E1
# Equivariant Weight-Space Encoders — Sample Efficiency PoC

---
hypothesis_id: H-E1
hypothesis_type: EXISTENCE
tier: LIGHT
date: 2026-08-21
author: yoon303@etri.re.kr

---

## Overview

Single config for all experiment conditions: 4 encoders × 5 training sizes × 2 zoos.
PoC phase — one seed, fixed hyperparameters, no tuning.

Applied: No relevant KB pattern (Archon KB contains diffusion model content only; similarity ~0.48 to irrelevant content)

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design
**Config Files Found**: None - new config
**Pattern Used**: dataclass + YAML schema

---

## ExperimentConfig Dataclass (C-1-1)

```python
from dataclasses import dataclass, field


@dataclass
class ExperimentConfig:
    # Zoo settings
    zoo_names: list[str] = field(default_factory=lambda: ["mnist", "cifar10"])
    zoo_paths: dict[str, str] = field(default_factory=dict)  # MUST override: absolute paths to .pt files

    # Training
    seed: int = 42
    epochs: int = 200
    batch_size: int = 64
    lr: float = 1e-3
    weight_decay: float = 1e-4

    # Experiment conditions
    training_sizes: list = field(default_factory=lambda: [100, 250, 500, 1000, "full"])
    encoder_names: list[str] = field(default_factory=lambda: ["flat_mlp", "flat_mlp_perm_aug", "dwsnet", "gnn_nfn"])
    budget_tiers: dict[str, int] = field(default_factory=lambda: {"small": 50_000, "medium": 200_000, "large": 500_000})

    # Evaluation
    n_bootstrap: int = 1000
    ci_level: float = 0.95
    perm_aug_prob: float = 0.5

    # Output paths — MUST override for your environment
    figures_dir: str = "h-e1/figures"
    results_dir: str = "h-e1/results"
    checkpoint_dir: str = "h-e1/checkpoints"

    # Encoder-specific
    # Non-standard: hidden_dim values are derived targets for budget tiers, not directly a hidden dim.
    # Actual hidden_dim per encoder must be solved at init time to match param count.
    hidden_dim_small: int = 64    # target hidden_dim for ~50K params (encoder-dependent)
    hidden_dim_medium: int = 128  # target hidden_dim for ~200K params
    hidden_dim_large: int = 256   # target hidden_dim for ~500K params
    num_dws_layers: int = 3
    num_mlp_layers: int = 3
    gnn_hidden_dim: int = 64
```

---

## YAML Schema (C-1-2)

```yaml
# h-e1/config.yaml
# Values marked OVERRIDE must be set before running.

zoo:
  zoo_names:
    - mnist
    - cifar10
  zoo_paths:
    mnist: ""       # OVERRIDE: absolute path to mnist zoo .pt file
    cifar10: ""     # OVERRIDE: absolute path to cifar10 zoo .pt file

training:
  seed: 42
  epochs: 200
  batch_size: 64
  lr: 0.001
  weight_decay: 0.0001

encoders:
  encoder_names:
    - flat_mlp
    - flat_mlp_perm_aug
    - dwsnet
    - gnn_nfn
  training_sizes:
    - 100
    - 250
    - 500
    - 1000
    - full
  budget_tiers:
    small: 50000
    medium: 200000
    large: 500000
  hidden_dim_small: 64
  hidden_dim_medium: 128
  hidden_dim_large: 256
  num_dws_layers: 3
  num_mlp_layers: 3
  gnn_hidden_dim: 64
  perm_aug_prob: 0.5

evaluation:
  n_bootstrap: 1000
  ci_level: 0.95

paths:
  figures_dir: h-e1/figures   # OVERRIDE: use absolute path in production
  results_dir: h-e1/results   # OVERRIDE
  checkpoint_dir: h-e1/checkpoints  # OVERRIDE
```

---

## Configuration Guide

**Keep fixed (PoC):** seed, epochs, batch_size, lr, weight_decay, n_bootstrap, ci_level, num_dws_layers, num_mlp_layers, gnn_hidden_dim, perm_aug_prob

**Must override before running:**
- `zoo_paths.mnist` / `zoo_paths.cifar10` — absolute paths to downloaded zoo `.pt` files
- `figures_dir`, `results_dir`, `checkpoint_dir` — absolute paths for your machine

**Derived at runtime (not in config):** actual hidden_dim per encoder per budget tier — solver in `encoders.py` uses `hidden_dim_small/medium/large` as targets and finds nearest integer that matches the param budget.

---

## Subtask Summary

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | ExperimentConfig dataclass | Single dataclass in `code/config.py` covering all zoo, training, encoder, evaluation, and path settings |
| C-1-2 | YAML schema | `config.yaml` matching the dataclass; sections: zoo, training, encoders, evaluation, paths; OVERRIDE markers for environment-specific values |
