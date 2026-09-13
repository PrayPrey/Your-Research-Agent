# Config: H-M2 Training Regime vs Cross-Dataset Gap

**Applied**: Standard PyTorch dataclass config pattern (single flat `Config` dataclass, no KB match found for query)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - new config design (no existing `code/` or `src/` to reuse)
**Config Files Found**: None
**Pattern Used**: dataclass

---

## M-2: Multi-dataset assembly [Complexity: 9, Budget: 4]

**Applied**: WeightedRandomSampler inverse-frequency balancing (standard PyTorch pattern)

### Configuration (Python Dataclass)

```python
from dataclasses import dataclass, field

@dataclass
class MultiDatasetConfig:
    label_offset_mode: str = "sequential"   # unified label space: dataset_i offset = sum(prev num_classes)
    sampler_replacement: bool = True        # WeightedRandomSampler default
    # Non-standard: num_samples defaults to len(concat_dataset) unless overridden
    sampler_num_samples: int | None = None
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-2-1 | Label offset builder | Compute per-dataset class offsets, remap targets in ConcatDataset |
| C-2-2 | ConcatDataset wrapper | `build_multi_dataset(names, root)` -> offset-applied ConcatDataset |
| C-2-3 | Weighted sampler | `build_balanced_sampler`: weight_i = 1/len(dataset_i) per-sample |
| C-2-4 | Multi dataloader | `build_multi_dataloader` wiring sampler + ConcatDataset + batch_size |

---

## M-7: Gap + statistical analysis [Complexity: 10, Budget: 4]

**Applied**: scipy independent t-test + Cohen's d + bootstrap CI (standard stats pattern)

### Configuration (Python Dataclass)

```python
@dataclass
class StatsConfig:
    alpha: float = 0.05
    bootstrap_resamples: int = 1000
    bootstrap_ci: float = 0.95
    gap_threshold_pp: float = 5.0    # success criterion: mean gap diff > 5pp
    cohens_d_threshold: float = 0.5
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-7-1 | Gap computation | `compute_gap`/`compute_all_gaps`: in-dist acc minus mean OOD acc |
| C-7-2 | t-test + Cohen's d | `compare_groups`: scipy `ttest_ind`, pooled-std Cohen's d |
| C-7-3 | Bootstrap CI | `bootstrap_ci`: 1000 resamples, percentile 95% CI |
| C-7-4 | Plots | box plot (single vs multi gaps) + bar chart to `figures/` |

---

## M-8: Baselines [Complexity: 9, Budget: 4]

**Applied**: Standard baseline-control pattern (frozen/size-matched/shuffled)

### Configuration (Python Dataclass)

```python
@dataclass
class BaselineConfig:
    imagenet_frozen: bool = True         # Baseline 1: no fine-tuning
    size_control_target: str = "single"  # Baseline 2: subsample multi to match single dataset size
    random_mix_seed: int = 42            # Baseline 3: shuffle benchmark->sample assignment
    n_random_mix_trials: int = 3
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| C-8-1 | ImageNet-frozen baseline | `run_baseline_imagenet`: eval pretrained ResNet-50, no fine-tuning |
| C-8-2 | Size-control baseline | `run_baseline_size_control`: subsample multi-mix to single-benchmark size |
| C-8-3 | Random-mix baseline | `run_baseline_random_mix`: shuffle sample-to-benchmark labels before mixing |
| C-8-4 | Baseline reporting | Aggregate 3 baselines into results dict for comparison |

---

## Global Experiment Config (Shared)

```python
@dataclass
class Config:
    single_benchmarks: list[str] = field(default_factory=lambda: ["cub", "dogs", "cars", "aircraft", "flowers"])
    multi_configs: list[list[str]] = field(default_factory=lambda: [
        ["cub", "dogs", "cars"],
        ["cub", "dogs", "cars", "flowers"],
        ["cub", "dogs", "cars", "flowers", "aircraft"],
    ])
    seeds: list[int] = field(default_factory=lambda: [42, 123, 456])
    held_out_eval: str = "nabirds"
    epochs: int = 30
    lr: float = 0.01
    batch_size: int = 32
    weight_decay: float = 1e-4
    momentum: float = 0.9
    knn_k: int = 5
    knn_support_per_class: int = 5
    feature_dim: int = 2048
    data_root: str = "./data"
    ckpt_dir_single: str = "./models/single_benchmark"
    ckpt_dir_multi: str = "./models/multi_benchmark"
    feature_dir: str = "./features"
    results_path: str = "./results/h_m2_results.json"

    multi_dataset: MultiDatasetConfig = field(default_factory=MultiDatasetConfig)
    stats: StatsConfig = field(default_factory=StatsConfig)
    baseline: BaselineConfig = field(default_factory=BaselineConfig)
```

## YAML Configuration Schema

```yaml
single_benchmarks: [cub, dogs, cars, aircraft, flowers]
multi_configs:
  - [cub, dogs, cars]
  - [cub, dogs, cars, flowers]
  - [cub, dogs, cars, flowers, aircraft]
seeds: [42, 123, 456]
held_out_eval: nabirds
epochs: 30
lr: 0.01
batch_size: 32
weight_decay: 1.0e-4
momentum: 0.9
knn_k: 5
knn_support_per_class: 5
feature_dim: 2048
data_root: ./data
ckpt_dir_single: ./models/single_benchmark
ckpt_dir_multi: ./models/multi_benchmark
feature_dir: ./features
results_path: ./results/h_m2_results.json

multi_dataset:
  label_offset_mode: sequential
  sampler_replacement: true
  sampler_num_samples: null

stats:
  alpha: 0.05
  bootstrap_resamples: 1000
  bootstrap_ci: 0.95
  gap_threshold_pp: 5.0
  cohens_d_threshold: 0.5

baseline:
  imagenet_frozen: true
  size_control_target: single
  random_mix_seed: 42
  n_random_mix_trials: 3
```

## Hyperparameter Table

| Param | Default | Justification |
|-------|---------|----------------|
| lr | 0.01 | Standard SGD fine-tune rate for ResNet-50 (with cosine schedule per M-4/M-5) |
| epochs | 30 | Sufficient for convergence within 24 GPU-hr budget (NFR-1) |
| batch_size | 32 | Fits single-A100 memory for ResNet-50 at 224px |
| momentum | 0.9 | Standard SGD momentum |
| weight_decay | 1e-4 | Standard ResNet fine-tune regularization |
| knn_k | 5 | Fixed by FR-3.2 |
| knn_support_per_class | 5 | Fixed by FR-3.3 |
| bootstrap_resamples | 1000 | Fixed by FR-4.4 |
| gap_threshold_pp | 5.0 | Fixed by success criterion |
| cohens_d_threshold | 0.5 | Fixed by success criterion |

## CLI Argument Mappings

| CLI Flag | Config Field | Type |
|----------|--------------|------|
| `--lr` | `Config.lr` | float |
| `--epochs` | `Config.epochs` | int |
| `--batch-size` | `Config.batch_size` | int |
| `--seeds` | `Config.seeds` | list[int] (comma-separated) |
| `--data-root` | `Config.data_root` | str |
| `--knn-k` | `Config.knn_k` | int |
| `--bootstrap-resamples` | `Config.stats.bootstrap_resamples` | int |
| `--random-mix-seed` | `Config.baseline.random_mix_seed` | int |
| `--results-path` | `Config.results_path` | str |
