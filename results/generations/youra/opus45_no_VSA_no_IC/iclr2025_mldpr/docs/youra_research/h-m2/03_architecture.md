# Architecture: H-M2 Training Regime vs Cross-Dataset Gap

**Type:** MECHANISM | **Epic Tasks:** 8

Applied: standard feature-extraction + k-NN eval pattern (frozen backbone, sklearn KNN, ConcatDataset+WeightedRandomSampler)

## Codebase Analysis (Serena)

**Project Type**: green-field
**Status**: green-field - no existing code to analyze (no `src/` in repo; h-e1 architecture reviewed as reference only, no `code/` folder provided for reuse)
**Analyzed Path**: N/A
**Findings**: New implementation from scratch. Reuses h-e1's `FeatureResNet50` pattern conceptually but no importable code exists to link against.

## File Structure

```
src/
├── data/
│   ├── datasets.py          # 6 dataset loaders + transforms
│   └── multi_dataset.py     # ConcatDataset + WeightedRandomSampler + label offset
├── models/
│   └── feature_extractor.py # ResNet-50 wrapper w/ feature hook
├── training/
│   ├── finetune_single.py   # single-benchmark training loop
│   └── finetune_multi.py    # multi-benchmark training loop
├── evaluation/
│   ├── knn_eval.py          # k-NN cross-dataset accuracy
│   └── gap_analysis.py      # gap computation, t-test, Cohen's d, bootstrap CI
├── experiments/
│   └── h_m2_training_regime.py  # orchestrator: run all + baselines + report
└── config.py                 # experiment config
```

## Modules

### config.py

```python
@dataclass
class Config:
    single_benchmarks: list[str] = ("cub", "dogs", "cars", "aircraft", "flowers")
    multi_configs: list[list[str]] = (
        ["cub", "dogs", "cars"],
        ["cub", "dogs", "cars", "flowers"],
        ["cub", "dogs", "cars", "flowers", "aircraft"],
    )
    seeds: list[int] = (42, 123, 456)
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
```

### data/datasets.py

**Dependencies**: config.py

```python
def get_transforms(train: bool) -> transforms.Compose: ...
def build_dataset(name: str, root: str, train: bool) -> Dataset: ...
    # name in {cub, dogs, flowers, cars, aircraft, nabirds}
def build_dataloader(name: str, root: str, train: bool, batch_size: int) -> DataLoader: ...
```

### data/multi_dataset.py (`src/data/multi_dataset.py`)

**Dependencies**: data/datasets.py

```python
def build_multi_dataset(names: list[str], root: str) -> ConcatDataset: ...
    # applies per-dataset label offset -> unified label space
def build_balanced_sampler(datasets: list[Dataset]) -> WeightedRandomSampler: ...
    # weight_i = 1/len(dataset_i), inverse-frequency balancing
def build_multi_dataloader(names: list[str], root: str, batch_size: int) -> DataLoader: ...
```

### models/feature_extractor.py

**Dependencies**: torchvision

```python
class FeatureResNet50(nn.Module):
    def __init__(self, num_classes: int, pretrained: bool = True): ...
    def forward(self, x: Tensor) -> Tensor: ...          # classification logits
    def extract_features(self, x: Tensor) -> Tensor: ... # 2048-d avgpool output
```

### training/finetune_single.py

**Dependencies**: data/datasets.py, models/feature_extractor.py, config.py

```python
def finetune_single(benchmark: str, seed: int, cfg: Config) -> str: ...  # returns ckpt path
def run_all_single(cfg: Config) -> list[str]: ...  # 15 models (5 benchmarks x 3 seeds)
```

### training/finetune_multi.py

**Dependencies**: data/multi_dataset.py, models/feature_extractor.py, config.py

```python
def finetune_multi(benchmark_names: list[str], seed: int, cfg: Config) -> str: ...  # returns ckpt path
def run_all_multi(cfg: Config) -> list[str]: ...  # 9 models (3 mixes x 3 seeds)
```

### evaluation/knn_eval.py

**Dependencies**: models/feature_extractor.py, sklearn

```python
def extract_features(model: FeatureResNet50, loader: DataLoader) -> tuple[np.ndarray, np.ndarray]: ...
def knn_accuracy(model: FeatureResNet50, support_loader: DataLoader, query_loader: DataLoader, k: int = 5) -> float: ...
def evaluate_in_distribution(model, benchmark: str, cfg: Config) -> float: ...
def evaluate_ood(model, target_benchmark: str, cfg: Config) -> float: ...
def evaluate_all_targets(model, train_domains: list[str], eval_domains: list[str], cfg: Config) -> dict[str, float]: ...
```

### evaluation/gap_analysis.py

**Dependencies**: evaluation/knn_eval.py, scipy, numpy

```python
def compute_gap(in_dist_acc: float, out_dist_accs: list[float]) -> float: ...
def compute_all_gaps(ckpt_paths: list[str], train_domains_map: dict[str, list[str]], cfg: Config) -> list[float]: ...
def compare_groups(single_gaps: list[float], multi_gaps: list[float]) -> dict: ...
    # returns {t_stat, p_value, cohens_d, mean_diff_pp}
def bootstrap_ci(values: list[float], n_resamples: int = 1000) -> tuple[float, float]: ...
```

### experiments/h_m2_training_regime.py

**Dependencies**: all above

```python
def run_baseline_imagenet(cfg: Config) -> list[float]: ...       # Baseline 1: frozen pretrained
def run_baseline_size_control(cfg: Config) -> list[float]: ...   # Baseline 2: subsampled multi
def run_baseline_random_mix(cfg: Config) -> list[float]: ...     # Baseline 3: shuffled benchmark assignment
def plot_results(single_gaps: list[float], multi_gaps: list[float], cfg: Config) -> None: ...
    # box plot + bar chart to figures/
def main(cfg: Config) -> None: ...
    # orchestrates: train all -> extract/eval -> gaps -> stats -> baselines -> write results_path
```

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| M-1 | Data pipeline | Loaders+transforms for 6 datasets | 8 | 3+1+2+2 |
| M-2 | Multi-dataset assembly | ConcatDataset, label offset, WeightedRandomSampler | 9 | 2+3+3+1 |
| M-3 | Model wrapper | ResNet-50 w/ classifier head + feature-extraction hook | 6 | 2+1+2+1 |
| M-4 | Single-benchmark training | Train 15 models (5 benchmarks x 3 seeds), SGD+cosine | 11 | 3+2+3+3 |
| M-5 | Multi-benchmark training | Train 9 models (3 mixes x 3 seeds) w/ balanced sampler | 12 | 3+3+3+3 |
| M-6 | k-NN cross-dataset eval | Feature extraction + k-NN (k=5, cosine) across 24 models x held-out/OOD domains | 13 | 3+3+3+4 |
| M-7 | Gap + statistical analysis | Gap computation, t-test, Cohen's d, bootstrap CI, plots | 10 | 2+2+4+2 |
| M-8 | Baselines | ImageNet-frozen, size-control subsample, random-mix shuffle | 9 | 2+2+3+2 |

**Distribution**: VeryHigh(18-20): [], High(14-17): [M-6], Medium(9-13): [M-1, M-2, M-4, M-5, M-7, M-8], Low(4-8): [M-3]
