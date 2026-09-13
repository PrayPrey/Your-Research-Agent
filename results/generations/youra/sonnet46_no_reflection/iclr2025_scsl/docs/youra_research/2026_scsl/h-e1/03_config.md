# Configuration: H-E1 — Spurious Direction Recovery via K-Means

**Hypothesis**: H-E1 (EXISTENCE / PoC)
**Tier**: LIGHT

---

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field — no existing codebase to analyze
**Config Files Found**: None — new config design
**Pattern Used**: dataclass + YAML

---

## A-1: Data Pipeline [Complexity: 2, Budget: C-1-1]

Applied: Standard DL Config Dataclass

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DatasetConfig:
    name: str = "waterbirds"          # "waterbirds" or "celeba"
    root: str = "./data/waterbirds"
    split: str = "train"
    num_classes: int = 2
    num_groups: int = 4
    img_size: int = 224
    augment: bool = True
    num_workers: int = 4


@dataclass
class TrainingConfig:
    seed: int = 1
    epochs: int = 100
    early_stop_epoch: int = 5         # Checkpoint saved at this epoch; pipeline stops
    batch_size: int = 32
    optimizer: str = "sgd"
    lr: float = 1e-3                  # Source: DFR repo train_classifier.py
    momentum: float = 0.9             # Source: DFR repo train_classifier.py
    weight_decay: float = 1e-3        # Waterbirds: 1e-3, CelebA: 1e-4
    scheduler: Optional[str] = None
    pretrained: bool = True


@dataclass
class ClusteringConfig:
    k: int = 2
    n_init: int = 10
    seed: int = 42


@dataclass
class GateConfig:
    ami_threshold: float = 0.5
    purity_threshold: float = 0.75


@dataclass
class OutputConfig:
    checkpoint_dir: str = "./checkpoints/h-e1/waterbirds"
    embeddings_path: str = "./embeddings/h-e1/waterbirds_epoch5.npy"
    results_path: str = "./results/h-e1/waterbirds_results.yaml"
    figures_dir: str = "./h-e1/figures"


@dataclass
class ExperimentConfig:
    dataset: DatasetConfig = field(default_factory=DatasetConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    clustering: ClusteringConfig = field(default_factory=ClusteringConfig)
    gate: GateConfig = field(default_factory=GateConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
```

### YAML Configs

**configs/waterbirds.yaml**
```yaml
dataset:
  name: waterbirds
  root: ./data/waterbirds
  split: train
  num_classes: 2
  num_groups: 4
  img_size: 224
  augment: true

training:
  seed: 1
  epochs: 100
  early_stop_epoch: 5
  batch_size: 32
  optimizer: sgd
  lr: 0.001
  momentum: 0.9
  weight_decay: 0.001
  scheduler: null

clustering:
  k: 2
  n_init: 10
  seed: 42

gate:
  ami_threshold: 0.5
  purity_threshold: 0.75

output:
  checkpoint_dir: ./checkpoints/h-e1/waterbirds
  embeddings_path: ./embeddings/h-e1/waterbirds_epoch5.npy
  results_path: ./results/h-e1/waterbirds_results.yaml
  figures_dir: ./h-e1/figures
```

**configs/celeba.yaml**
```yaml
dataset:
  name: celeba
  root: ./data/celeba
  split: train
  num_classes: 2
  num_groups: 4
  img_size: 224
  augment: true

training:
  seed: 1
  epochs: 50
  early_stop_epoch: 5
  batch_size: 128
  optimizer: sgd
  lr: 0.001
  momentum: 0.9
  weight_decay: 0.0001      # Non-standard: CelebA uses 1e-4 vs Waterbirds 1e-3 (DFR repo)
  scheduler: null

clustering:
  k: 2
  n_init: 10
  seed: 42

gate:
  ami_threshold: 0.5
  purity_threshold: 0.75

output:
  checkpoint_dir: ./checkpoints/h-e1/celeba
  embeddings_path: ./embeddings/h-e1/celeba_epoch5.npy
  results_path: ./results/h-e1/celeba_results.yaml
  figures_dir: ./h-e1/figures
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-1-1 | Dataset config YAML schema | waterbirds.yaml and celeba.yaml with paths, splits, transforms |

---

## A-5: Visualization [Complexity: 1, Budget: C-5-1]

Applied: Standard DL Config Dataclass

### Configuration (Python Dataclass)

```python
@dataclass
class VisualizationConfig:
    # Figure sizes
    bar_chart_figsize: tuple = (10, 6)
    tsne_figsize: tuple = (12, 8)
    ami_curve_figsize: tuple = (10, 6)
    composition_figsize: tuple = (10, 6)

    # Output format
    output_format: str = "png"
    dpi: int = 150

    # Color palette — 4 distinct colors for 4 groups
    group_colors: list = field(default_factory=lambda: [
        "#1f77b4",   # group 0
        "#ff7f0e",   # group 1
        "#2ca02c",   # group 2
        "#d62728",   # group 3
    ])

    # Threshold lines for bar chart
    ami_threshold_line: float = 0.5
    purity_threshold_line: float = 0.75

    # Save paths (relative to figures_dir from OutputConfig)
    bar_chart_fname: str = "metrics_bar.png"
    tsne_class_fname: str = "tsne_class.png"
    tsne_group_fname: str = "tsne_group.png"
    tsne_cluster_fname: str = "tsne_cluster.png"
    ami_curve_fname: str = "ami_vs_epoch.png"
    composition_fname: str = "cluster_composition.png"
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-5-1 | Visualization config | Figure sizes, DPI, colors, output paths |

---

## A-6: Gate Evaluation [Complexity: 1, Budget: C-6-1]

Applied: Standard DL Config Dataclass

### Gate Config (Python Dataclass — already defined above in GateConfig)

```python
@dataclass
class GateConfig:
    ami_threshold: float = 0.5        # MUST_WORK gate: AMI >= 0.5 on both datasets
    purity_threshold: float = 0.75    # MUST_WORK gate: worst-cluster purity >= 0.75
    ami_chance_margin: float = 0.1    # ami_actual > ami_random + 0.1 (FR-7 check)
    min_cluster_size: int = 10        # Both clusters must contain > 10 samples (FR-7)
```

### Results Schema (YAML written by evaluate.py)

```yaml
# results/h-e1/{dataset}_results.yaml
hypothesis: h-e1
dataset: waterbirds   # or celeba
epoch: 5

metrics:
  ami: 0.0            # Actual AMI value
  purity: 0.0         # Worst-cluster purity value
  ami_random: 0.0     # Random baseline AMI (shuffled labels)
  purity_random: 0.0  # Random baseline purity

gate:
  ami_threshold: 0.5
  purity_threshold: 0.75
  ami_pass: false     # ami >= ami_threshold
  purity_pass: false  # purity >= purity_threshold
  dataset_pass: false # ami_pass AND purity_pass

verification:
  embedding_shape_ok: false   # shape[1] == 2048
  non_degenerate: false       # both clusters > 10 samples
  above_chance: false         # ami > ami_random + 0.1
```

```yaml
# results/h-e1/overall_results.yaml
hypothesis: h-e1
epoch: 5

datasets:
  waterbirds:
    ami: 0.0
    purity: 0.0
    pass: false
  celeba:
    ami: 0.0
    purity: 0.0
    pass: false

gate:
  overall_pass: false   # true only if BOTH datasets pass
  gate_type: MUST_WORK
  blocks_pipeline: true
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-6-1 | Gate threshold config and results schema | GateConfig dataclass, YAML results schema |
