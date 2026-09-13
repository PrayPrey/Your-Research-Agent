# Config: h-m1

Applied: dataclass pattern (inherited from h-e1/code/config.py)

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: Config classes verified from actual h-e1/code/config.py
**Config Files Found**: `h-e1/code/config.py` — ZooConfig (zoo_path, osf_url, expected_n_models), AuditConfig (spearman_threshold, seed=42, split_ratios=[0.8,0.1,0.1]), DataLoaderConfig, EncoderConfig, ExperimentConfig
**Pattern Used**: dataclass

---

## Inherited Configuration (Base Hypothesis)

```python
# From: h-e1/code/config.py (ACTUAL CODE — verified field names)
@dataclass
class ZooConfig:
    zoo_path: str = "data/cifar10_zoo.npz"
    osf_url: str = "https://osf.io/hbm72/"
    expected_n_models: int = 10_000

@dataclass
class AuditConfig:
    spearman_threshold: float = 0.95
    seed: int = 42
    split_ratios: list = field(default_factory=lambda: [0.8, 0.1, 0.1])
```

H-M1 inherits: `seed=42`, `split_ratios=[0.8, 0.1, 0.1]` from AuditConfig.

---

## A-6: Visualizations [Complexity: 11, Budget: 1 subtask]

Applied: Standard matplotlib defaults

### Configuration

```python
from dataclasses import dataclass, field

@dataclass
class FigureConfig:
    out_dir: str = "figures"
    dpi: int = 150
    fmt: str = "png"
    # figsize per figure type
    bar_figsize: tuple = (7, 4)       # fig1_bar
    scatter_figsize: tuple = (8, 8)   # fig2_scatter (2x2 grid)
    ranking_figsize: tuple = (8, 4)   # fig3_ranking (side-by-side bars)
    delta_figsize: tuple = (6, 4)     # fig4_delta (arrow plot)
    dist_figsize: tuple = (6, 4)      # fig5_dist (histogram)
    baseline_r: float = 0.5567        # FlatMLP Spearman r from H-E1
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | FigureConfig dataclass | Fields: out_dir, dpi, fmt, per-figure figsize, baseline_r |

---

## A-7: Results & Entry Point [Complexity: 7, Budget: 1 subtask]

Applied: Standard JSON schema pattern

### Configuration

```python
from dataclasses import dataclass, field

@dataclass
class AnalysisConfig:
    # Paths (relative to h-m1/ directory)
    h_e1_code_path: str = "../h-e1/code"
    checkpoint_dir: str = "../h-e1/checkpoints"
    zoo_path: str = "../../data/cifar10_zoo.npz"
    results_path: str = "04_results.json"
    figures_dir: str = "figures"
    # Inherited from h-e1 AuditConfig
    seed: int = 42
    # Analysis constants
    flat_mlp_baseline_r: float = 0.5567
    bootstrap_n: int = 1000
    encoder_names: list = field(default_factory=lambda: ["flat_mlp", "dws_net", "nft", "gnn"])
    checkpoint_files: dict = field(default_factory=lambda: {
        "flat_mlp": "flat_mlp.pt",
        "dws_net": "dws_net.pt",
        "nft": "nft.pt",
        "gnn": "gnn.pt",
    })
    device: str = "cpu"   # set to "cuda" at runtime if torch.cuda.is_available()
    batch_size: int = 256


@dataclass
class RetrainConfig:
    """Fallback: re-train missing checkpoints using H-E1 protocol."""
    lr: float = 1e-3
    batch_size: int = 64
    epochs: int = 100
    optimizer: str = "adamw"
    loss: str = "mse"
    early_stop_patience: int = 10
```

### Results JSON Schema (`04_results.json`)

```json
{
  "encoder_name": {
    "r": 0.0,
    "ci_low": 0.0,
    "ci_high": 0.0
  },
  "delta_gap": 0.0,
  "gate_passed": false,
  "timestamp": "2026-08-31T00:00:00"
}
```

**Field definitions:**
- `encoder_name` (object, repeated for each of `flat_mlp`, `dws_net`, `nft`, `gnn`): Spearman r with 95% bootstrap CI
- `delta_gap` (float): `mean(equivariant encoders r) - flat_mlp_baseline_r`
- `gate_passed` (bool): `True` if any equivariant encoder `r > 0.5567`
- `timestamp` (str): ISO-8601 UTC timestamp of run

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | ResultsSchema | JSON schema for 04_results.json with encoder results, delta_gap, gate_passed, timestamp |
