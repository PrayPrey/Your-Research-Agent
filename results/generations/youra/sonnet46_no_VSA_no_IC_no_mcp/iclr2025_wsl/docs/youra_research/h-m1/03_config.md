---
title: "Config: H-M1 — NFT Orbit Invariance Probe"
hypothesis_id: H-M1
hypothesis_type: MECHANISM
tier: FULL
date: 2026-08-26
author: Anonymous
base_hypothesis: H-E1
budget: 5 subtasks (Config Agent allocation)
---

Applied: Dataclass-first config pattern (typed, default-complete, CLI-overridable)
Applied: Incremental config extension (inherit H-E1 dataset/training params; add probe-specific settings)

## Inherited Configuration

**From H-E1 Phase 3 config (verified from 03_architecture.md and 03_config.md):**
- Dataset: `schurholt/model_zoos_dataset`, config `mnist`, split `train+validation+test` (v2 corrected)
- Weight vector dim: D = 51,850
- Architecture: 784→64→10 MLP, ReLU
- NFT training (if fallback): Adam lr=1e-3, batch=64, epochs=100, MSE loss on normalized properties
- Seed: 42 (global)

**H-M1 inherits these unchanged.** Only probe-specific config is new.

---

## Configuration Schemas

### C-6-1: ProbeConfig (Primary experiment configuration)

**Parent Epic**: A-6

```python
from dataclasses import dataclass, field
from typing import Literal

@dataclass
class ProbeConfig:
    """Primary configuration for H-M1 orbit invariance probe."""

    # Probe settings
    n_orbit_pairs: int = 1000
    """Number of oracle orbit pairs to construct and probe per orbit type. ≥500 for statistical power."""

    orbit_types: list[str] = field(default_factory=lambda: ["scaling", "signflip"])
    """Orbit types to probe. Options: 'scaling', 'signflip'."""

    n_bootstrap: int = 1000
    """Bootstrap resamples for 95% CI on orbit_invariance_gap."""

    seed: int = 42
    """Global random seed for all stochastic operations."""

    device: str = "cpu"
    """Inference device. 'cpu' | 'cuda'. No training required for probe (fallback: 'cuda' if available)."""

    batch_size: int = 64
    """NFT inference batch size (models per forward pass)."""

    # Cross-orbit sampling
    n_accuracy_deciles: int = 10
    """Number of test_accuracy deciles for cross-orbit same-property pair sampling."""

    # Orbit construction bounds
    scale_min: float = 0.1
    scale_max: float = 10.0
    """Log-uniform scale range for scaling orbit construction: Uniform(scale_min, scale_max)."""

    flip_prob: float = 0.5
    """Probability of sign flip per hidden neuron for sign-flip orbit construction."""

    # Verification
    orbit_equiv_tol: float = 1e-4
    """Tolerance for functional equivalence verification of orbit pairs (max |Δ output|)."""

    activation_gap_min: float = 0.001
    """Minimum orbit_invariance_gap.abs().mean() to confirm probe is activated."""
```

---

### C-6-2: NFTConfig (NFT architecture and checkpoint settings)

**Parent Epic**: A-6

```python
@dataclass
class NFTConfig:
    """NFT Condition A encoder configuration (inherited from H-E1)."""

    # Architecture
    d_model: int = 256
    """NFT transformer hidden dimension."""

    n_heads: int = 8
    """NFT multi-head attention heads."""

    n_transformer_layers: int = 4
    """Number of NFT transformer encoder layers."""

    dropout: float = 0.0
    """Dropout rate (0.0 for inference-only use)."""

    # Checkpoint
    checkpoint_path: str = "../../h-e1/code/checkpoints/nft_condition_a.pt"
    """Path to H-E1 NFT Condition A checkpoint. Relative to h-m1/code/."""

    fallback_checkpoint_path: str = "checkpoints/nft_condition_a_hm1.pt"
    """Path to save retrained NFT if H-E1 checkpoint is missing."""

    # Tokenization (MNIST MLP zoo spec)
    arch_spec: dict = field(default_factory=lambda: {
        "d_in": 784, "h": 64, "d_out": 10, "n_hidden_layers": 1
    })
    """Architecture spec passed to NFT for weight tokenization setup."""
```

---

### C-6-3: FallbackTrainingConfig (NFT training, only if checkpoint missing)

**Parent Epic**: A-6

```python
@dataclass
class FallbackTrainingConfig:
    """
    NFT Condition A training config (FR-0.3 fallback).
    Activated only if H-E1 checkpoint is unavailable.
    Inherited from H-E1 training protocol (Zhou et al. 2023 NFT paper).
    """

    # Optimizer
    optimizer: str = "adam"
    lr: float = 1e-3
    betas: tuple = (0.9, 0.999)
    weight_decay: float = 1e-4

    # Scheduler
    scheduler: str = "cosine"
    T_max: int = 100
    """CosineAnnealingLR period (= n_epochs for one cycle)."""

    # Training loop
    n_epochs: int = 100
    batch_size: int = 64
    early_stop_patience: int = 10
    """Stop if validation loss doesn't improve for this many epochs."""

    # Loss
    loss: str = "mse"
    normalize_targets: bool = True
    """Mean-center + unit-variance normalize each property before MSE."""

    seed: int = 42
```

---

### C-9-1: VisualizationConfig (Figure output settings)

**Parent Epic**: A-9

```python
@dataclass
class VisualizationConfig:
    """Configuration for H-M1 figure generation."""

    figures_dir: str = "docs/youra_research/h-m1/figures"
    """Output directory for all figures."""

    dpi: int = 150
    """Figure resolution."""

    format: str = "png"
    """Output format. 'png' | 'pdf'."""

    # Heatmap / PCA settings
    n_models_heatmap: int = 50
    """Number of models shown in similarity heatmap (split 25 base + 25 orbit)."""

    n_models_pca: int = 100
    """Number of models shown in PCA scatter (split 50 base + 50 orbit)."""

    # Histogram settings
    n_bins_histogram: int = 50
    """Number of bins for cosine similarity distribution histograms."""

    # Color settings
    color_base:  str = "#1f77b4"  # matplotlib blue
    color_orbit: str = "#ff7f0e"  # matplotlib orange
    color_cross: str = "#2ca02c"  # matplotlib green
```

---

### C-8-1: DataConfig (Dataset and paths)

**Parent Epic**: A-8

```python
@dataclass
class DataConfig:
    """Dataset configuration — inherited from H-E1, extended for full zoo access."""

    hf_identifier: str = "schurholt/model_zoos_dataset"
    """HuggingFace dataset identifier. v2 corrected from ModelZoos/ModelZooDataset."""

    hf_config: str = "mnist"
    """Dataset configuration name. v2 corrected from mnist-mlp."""

    hf_split: str = "train+validation+test"
    """Dataset split(s) to load. Full zoo for maximum diversity in cross-orbit sampling."""

    local_fallback_path: str = "./data/mnist_zoo"
    """Local path for fallback if HuggingFace download fails."""

    expected_weight_dim: int = 51_850
    """Expected flat weight vector dimension per model. Fail fast if mismatch."""

    # Paths
    results_path: str = "docs/youra_research/h-m1/results.json"
    """Output path for JSON results file."""

    code_dir: str = "docs/youra_research/h-m1/code"
    """Root code directory for H-M1."""

    h_e1_code_dir: str = "docs/youra_research/h-e1/code"
    """Path to H-E1 code directory (added to sys.path for module reuse)."""
```

---

## YAML Config File

```yaml
# h-m1/config.yaml — full experiment configuration

probe:
  n_orbit_pairs: 1000
  orbit_types: ["scaling", "signflip"]
  n_bootstrap: 1000
  seed: 42
  device: "cpu"
  batch_size: 64
  n_accuracy_deciles: 10
  scale_min: 0.1
  scale_max: 10.0
  flip_prob: 0.5
  orbit_equiv_tol: 1.0e-4
  activation_gap_min: 0.001

nft:
  d_model: 256
  n_heads: 8
  n_transformer_layers: 4
  dropout: 0.0
  checkpoint_path: "../../h-e1/code/checkpoints/nft_condition_a.pt"
  fallback_checkpoint_path: "checkpoints/nft_condition_a_hm1.pt"
  arch_spec:
    d_in: 784
    h: 64
    d_out: 10
    n_hidden_layers: 1

training_fallback:  # Only used if H-E1 checkpoint missing
  optimizer: "adam"
  lr: 1.0e-3
  betas: [0.9, 0.999]
  weight_decay: 1.0e-4
  scheduler: "cosine"
  T_max: 100
  n_epochs: 100
  batch_size: 64
  early_stop_patience: 10
  loss: "mse"
  normalize_targets: true
  seed: 42

visualization:
  figures_dir: "docs/youra_research/h-m1/figures"
  dpi: 150
  format: "png"
  n_models_heatmap: 50
  n_models_pca: 100
  n_bins_histogram: 50
  color_base: "#1f77b4"
  color_orbit: "#ff7f0e"
  color_cross: "#2ca02c"

data:
  hf_identifier: "schurholt/model_zoos_dataset"
  hf_config: "mnist"
  hf_split: "train+validation+test"
  local_fallback_path: "./data/mnist_zoo"
  expected_weight_dim: 51850
  results_path: "docs/youra_research/h-m1/results.json"
  h_e1_code_dir: "docs/youra_research/h-e1/code"
```

---

## Hyperparameter Justification

| Parameter | Value | Source |
|-----------|-------|--------|
| `n_orbit_pairs=1000` | 1000 | Phase 2B protocol (≥500 for power); doubled for robustness |
| `n_bootstrap=1000` | 1000 | Efron & Tibshirani (1993) standard for CI estimation |
| `seed=42` | 42 | H-E1 consistency; reproducibility |
| `scale_min/max=0.1/10.0` | [0.1, 10.0] | H-E1 verified range; avoids near-zero scales |
| `flip_prob=0.5` | 0.5 | Uniform Bernoulli per neuron; maximal entropy sign flip |
| `d_model=256, n_heads=8, n_layers=4` | paper defaults | Zhou et al. 2023 NFT on Schürholt zoo |
| `lr=1e-3` | 1e-3 | Zhou et al. 2023 training config |
| `batch_size=64` | 64 | NFT paper; memory feasible for 51850-dim weights |
| `n_accuracy_deciles=10` | 10 | Standard decile binning; balanced bucket sizes |
| `orbit_equiv_tol=1e-4` | 1e-4 | Sufficient for float32 accumulated error |
